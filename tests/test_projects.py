"""Every real store in projects/ must load clean under the engine's gates.

This is where the loud break lives. The gate tests run against a synthetic fixture so that
the engine stays ignorant of any tradition; this file runs the engine against the traditions
themselves, so a method rename, an orphaned edge reference, or a record that loses its
provenance still fails the suite.

Parameterised over whatever is on disk, so adding a project adds coverage with no edit here.
A project with no store yet is skipped rather than failed - scaffolding one is a legitimate
intermediate state.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from parvan.loader import StoreError, load
from parvan.stp import solve

PROJECTS = Path(__file__).resolve().parents[1] / "projects"


def _stores() -> list[Path]:
    if not PROJECTS.is_dir():
        return []
    return sorted(p / "store" for p in PROJECTS.iterdir() if (p / "store" / "methods.yaml").is_file())


STORES = _stores()
IDS = [p.parent.name for p in STORES]


@pytest.mark.skipif(not STORES, reason="no project stores on disk")
@pytest.mark.parametrize("store_path", STORES, ids=IDS)
def test_project_store_loads(store_path: Path) -> None:
    try:
        store = load(store_path)
    except StoreError as exc:
        pytest.fail(f"{store_path} refused:\n{exc.report()}")
    assert store.nodes, "a store that loads but holds no nodes is a path bug, not a store"
    assert store.edges


@pytest.mark.skipif(not STORES, reason="no project stores on disk")
@pytest.mark.parametrize("store_path", STORES, ids=IDS)
def test_project_store_is_consistent(store_path: Path) -> None:
    """An inconsistent store is a real finding, but never a silent one."""
    sol = solve(load(store_path))
    assert sol.consistent, f"{store_path} has a negative cycle:\n{sol.witness()}"
