"""Parvan command line."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from . import __version__
from .loader import StoreError, load
from .retrodict import fmt_v2, run_all
from .stp import (SOLVER_VERSION, Solution, bound_support, fmt_bounds,
                  solve as run_solve)


@click.group()
@click.version_option(__version__, prog_name="parvan")
def main() -> None:
    """A constraint network over textual strata."""


@main.command()
@click.argument(
    "store_path",
    default="store",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def validate(store_path: Path) -> None:
    """Load STORE_PATH and refuse it if any invariant fails."""
    try:
        store = load(store_path)
    except StoreError as exc:
        click.secho(f"REFUSED - {len(exc.violations)} violation(s)\n", fg="red", bold=True)
        click.echo(exc.report())
        sys.exit(1)

    click.secho("OK", fg="green", bold=True)
    click.echo(f"  schema      {store.schema_version}")
    click.echo(f"  nodes       {len(store.nodes)}")
    for kind in sorted({n.kind for n in store.nodes.values()}):
        click.echo(f"    {kind:<14}{len(store.of_kind(kind))}")
    click.echo(f"  edges       {len(store.edges)}")
    click.echo(f"  methods     {len(store.methods)}")
    click.echo(f"  quarantined {len(store.quarantine)}  (G-2: never enters a solve)")


@main.command()
@click.argument(
    "store_path",
    default="store",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option("--target", "-t", multiple=True, help="Node ids to watch. Repeatable.")
@click.option("--epsilon", default=25, show_default=True)
def influence(store_path: Path, target: tuple[str, ...], epsilon: int) -> None:
    """Leave-one-out: which edges actually move a bound, and which are slack (R-12).

    Scoring an argument for confidence says nothing about whether it *binds*. A score-5
    constraint dominated by a weaker one contributes exactly nothing to the answer, and only
    this pass can tell you which is which.
    """
    try:
        store = load(store_path)
    except StoreError as exc:
        click.secho(f"REFUSED - {len(exc.violations)} violation(s)\n", fg="red", bold=True)
        click.echo(exc.report())
        sys.exit(1)

    targets = list(target) or [n.id for n in store.of_kind("stratum")]
    ref = run_solve(store, epsilon=epsilon)
    if not ref.consistent:
        click.secho("store is inconsistent; resolve that first", fg="red")
        click.echo(ref.witness())
        sys.exit(1)

    base = {t: (ref.bounds[t].floor, ref.bounds[t].ceiling) for t in targets if t in ref.bounds}
    binding: list[tuple[str, str, str, list[str]]] = []

    for eid in sorted(store.edges):
        probe = load(store_path)
        del probe.edges[eid]
        sol = run_solve(probe, epsilon=epsilon)
        if not sol.consistent:
            continue
        diffs = [
            f"{t} {fmt_bounds(ref.bounds[t])} -> {fmt_bounds(sol.bounds[t])}"
            for t in base
            if (sol.bounds[t].floor, sol.bounds[t].ceiling) != base[t]
        ]
        if diffs:
            e = store.edges[eid]
            binding.append((eid, e.provenance.tier, e.method, diffs))

    click.echo(f"leave-one-out over {len(store.edges)} edges, watching {len(base)} node(s)\n")
    click.secho(f"BINDING  {len(binding)}", fg="green", bold=True)
    for eid, tier, method, diffs in binding:
        colour = "cyan" if tier == "attested" else "yellow"
        click.echo("  ", nl=False)
        click.secho(f"{eid}", fg=colour, nl=False)
        click.echo(f"  [{tier}/{method}]")
        for d in diffs:
            click.echo(f"      {d}")
    click.secho(f"\nSLACK    {len(store.edges) - len(binding)} edges move nothing", fg="yellow")


@main.command()
@click.argument("store_path", default="store",
                type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--target", "-t", multiple=True, required=True, help="Node ids. Repeatable.")
@click.option("--epsilon", default=25, show_default=True)
def support(store_path: Path, target: tuple[str, ...], epsilon: int) -> None:
    """How redundantly is each bound held up? Reports the minimum cut (R-12).

    Leave-one-out cannot answer this: remove either edge of a two-route bound and nothing
    moves, so both look slack, and the better-supported a bound is the less important its
    supports appear. By Menger's theorem the minimum number of constraints whose joint
    removal moves a bound equals the number of edge-disjoint routes realising it, so this
    counts routes instead.

    A cut of 1 is a single point of failure. That is the number to worry about.
    """
    try:
        store = load(store_path)
    except StoreError as exc:
        click.secho(f"REFUSED - {len(exc.violations)} violation(s)\n", fg="red", bold=True)
        click.echo(exc.report())
        sys.exit(1)

    sol = run_solve(store, epsilon=epsilon)
    if not sol.consistent:
        click.secho("store is inconsistent; resolve that first", fg="red")
        click.echo(sol.witness())
        sys.exit(1)

    for node_id in target:
        var = node_id if node_id in sol.bounds else f"{node_id}#emergence"
        if var not in sol.bounds:
            click.secho(f"{node_id}: not in the store", fg="red")
            continue
        click.secho(f"\n{node_id}  {fmt_bounds(sol.bounds[var])}", bold=True)
        for side in ("floor", "ceiling"):
            routes = bound_support(store, node_id, side, epsilon=epsilon)
            n = len(routes)
            if n == 0:
                click.echo(f"  {side:<9} unbounded - nothing to support")
                continue
            colour = "red" if n == 1 else "green"
            click.echo(f"  {side:<9} ", nl=False)
            click.secho(f"cut {n}", fg=colour, nl=False)
            click.echo("  (single point of failure)" if n == 1 else "  edge-disjoint routes")
            for c in routes[0]:
                click.echo(f"      {c.origin:<28} {c.why}")


@main.command()
@click.argument("store_path", default="store",
                type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--epsilon", default=25, show_default=True)
def retrodict(store_path: Path, epsilon: int) -> None:
    """V-2: hold out each eligible anchor and measure whether the network recovers it.

    Thresholds come from docs/preregistration.md, frozen before a solver existed. They are
    not adjustable from here, deliberately.
    """
    try:
        load(store_path)
    except StoreError as exc:
        click.secho(f"REFUSED - {len(exc.violations)} violation(s)\n", fg="red", bold=True)
        click.echo(exc.report())
        sys.exit(1)

    results, summary = run_all(str(store_path), epsilon=epsilon)
    click.echo(fmt_v2(results, summary))
    sys.exit(0 if summary["meets_v2"] else 1)


def _commit_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")
    except Exception:
        return "unknown"


def _render(sol: Solution, store, epsilon: int) -> str:
    lines: list[str] = []
    if not sol.consistent:
        lines.append("INCONSISTENT\n")
        lines.append(sol.witness())
        return "\n".join(lines)

    lines.append(f"CONSISTENT   epsilon={epsilon}  variables={len(sol.variables)}  "
                 f"constraints={len(sol.constraints)}\n")
    by_kind: dict[str, list[tuple[str, str, str]]] = {}
    for var, bounds in sorted(sol.bounds.items()):
        base = var.split("#")[0]
        node = store.nodes.get(base)
        kind = node.kind if node else "?"
        label = (node.label if node else "")[:52]
        by_kind.setdefault(kind, []).append((var, fmt_bounds(bounds), label))

    for kind in sorted(by_kind):
        lines.append(f"  {kind}")
        for var, bounds, label in by_kind[kind]:
            lines.append(f"    {var:<38} {bounds:<34} {label}")
        lines.append("")

    if sol.skipped:
        lines.append("  deferred to the Bayesian layer")
        for s in sol.skipped:
            lines.append(f"    {s}")
    return "\n".join(lines)


@main.command()
@click.argument(
    "store_path",
    default="store",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option("--epsilon", default=25, show_default=True,
              help="Default minimum transmission lag, in years (R-5, O-1).")
@click.option("--contains-threshold", default=0.5, show_default=True,
              help="Below this confidence, containment defers to the Bayesian layer.")
@click.option("--seed", default=0, show_default=True, help="Recorded for reproducibility (G-6).")
@click.option("--no-record", is_flag=True, help="Skip writing a run record.")
@click.option("--runs-dir", type=click.Path(file_okay=False, path_type=Path), default=None,
              help="Where to write the run record. Defaults to the store's sibling runs/.")
def solve(store_path: Path, epsilon: int, contains_threshold: float, seed: int,
          no_record: bool, runs_dir: Path | None) -> None:
    """Propagate STORE_PATH to its tightest consistent bounds."""
    try:
        store = load(store_path)
    except StoreError as exc:
        click.secho(f"REFUSED - {len(exc.violations)} violation(s)\n", fg="red", bold=True)
        click.echo(exc.report())
        sys.exit(1)

    sol = run_solve(store, epsilon=epsilon, contains_threshold=contains_threshold)
    text = _render(sol, store, epsilon)
    click.echo(text)

    if no_record:
        return

    # G-6: a result that cannot be regenerated from these four values is not a result.
    commit = _commit_hash()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # Run records belong to the project that owns the store, not to whatever directory the
    # command happened to be invoked from. Once stores live under projects/<name>/store, a
    # cwd-relative "runs/" silently scatters one project's history across the tree.
    base = runs_dir or (store_path.resolve().parent / "runs")
    outdir = base / f"{stamp}-{commit[:8]}"
    outdir.mkdir(parents=True, exist_ok=True)

    record = {
        "store_commit": commit,
        "solver_version": SOLVER_VERSION,
        "seed": seed,
        "epsilon": epsilon,
        "contains_threshold": contains_threshold,
        "store_path": str(store_path),
        "consistent": sol.consistent,
        "nodes": len(store.nodes),
        "edges": len(store.edges),
        "bounds": {
            v: {
                "floor": None if b.floor == float("-inf") else b.floor,
                "ceiling": None if b.ceiling == float("inf") else b.ceiling,
            }
            for v, b in sol.bounds.items()
        },
        "skipped": sol.skipped,
        "negative_cycle": [c.origin for c in sol.negative_cycle],
    }
    (outdir / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    (outdir / "bounds.txt").write_text(text, encoding="utf-8")
    click.secho(f"\nrun record: {outdir}", fg="cyan")
    if commit.endswith("-dirty"):
        click.secho("  working tree is dirty; this run is not reproducible from the "
                    "commit alone (G-6)", fg="yellow")


if __name__ == "__main__":
    main()
