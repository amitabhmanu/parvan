"""Parvan command line."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__
from .loader import StoreError, load


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


if __name__ == "__main__":
    main()
