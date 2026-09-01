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
from .stp import SOLVER_VERSION, Solution, fmt_bounds, solve as run_solve


@click.group()
@click.version_option(__version__, prog_name="parvan")
def main() -> None:
    """A constraint network over Sanskrit textual strata."""


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
def solve(store_path: Path, epsilon: int, contains_threshold: float, seed: int,
          no_record: bool) -> None:
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
    outdir = Path("runs") / f"{stamp}-{commit[:8]}"
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
