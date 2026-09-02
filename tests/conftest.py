"""Fixtures building throwaway stores on disk.

The baseline store is deliberately minimal and valid. Each gate test mutates one thing and
asserts the loader refuses the whole store. Tests that prove acceptance are near-worthless
here - the gates exist to reject, so rejection is what has to be demonstrated.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_METHODS = Path(__file__).resolve().parent / "fixtures" / "methods.yaml"


def write(root: Path, relpath: str, data: dict) -> Path:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
    return path


@pytest.fixture
def store(tmp_path: Path) -> Path:
    """A minimal store that loads clean: one anchor, one referent, one stratum, two edges."""
    root = tmp_path / "store"
    for sub in ("nodes/anchors", "nodes/referents", "nodes/strata", "edges", "quarantine"):
        (root / sub).mkdir(parents=True, exist_ok=True)

    # An engine-owned vocabulary, not a project's. See the header of fixtures/methods.yaml:
    # real stores are kept honest by test_projects.py instead.
    shutil.copy(FIXTURE_METHODS, root / "methods.yaml")

    write(
        root,
        "nodes/anchors/anc.test.yaml",
        {
            "id": "anc.test",
            "kind": "anchor",
            "label": "Test anchor",
            "interval": {"floor": -190, "ceiling": -180},
            "dating_method": "numismatic-typology",
            "independent_of": ["internal-linguistic", "internal-doctrinal"],
            "holdout_eligible": True,
            "provenance": {"tier": "attested", "locus": "test coin catalogue no. 1"},
        },
    )
    write(
        root,
        "nodes/referents/ref.test.yaml",
        {
            "id": "ref.test",
            "kind": "referent",
            "label": "Test referent",
            "class": "institution",
            "emergence": {"floor": None, "ceiling": None},
            "attestation": {"floor": -190, "ceiling": -180},
            "text_derived": False,
            "provenance": {"tier": "attested", "locus": "test locus"},
        },
    )
    write(
        root,
        "nodes/strata/str.test.yaml",
        {
            "id": "str.test",
            "kind": "stratum",
            "label": "Test stratum",
            "work": "test",
            "extent": ["Test.1.1.1", "Test.1.9.9"],
        },
    )
    write(
        root,
        "edges/e.attest.yaml",
        {
            "id": "e.attest",
            "type": "attests",
            "from": "anc.test",
            "to": "ref.test",
            "method": "numismatic",
            "confidence": 0.95,
            "provenance": {"tier": "attested", "locus": "test coin catalogue no. 1"},
        },
    )
    write(
        root,
        "edges/e.presup.yaml",
        {
            "id": "e.presup",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "confidence": 0.9,
            "provenance": {"tier": "attested", "locus": "Test.1.4.2"},
        },
    )
    return root
