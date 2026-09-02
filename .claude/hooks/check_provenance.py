#!/usr/bin/env python
"""G-1's second enforcement point: refuse a commit that adds an ungated store record.

The loader is the first. Two, because one will eventually be bypassed - a record written by
hand, an editor plugin, a merge that resurrects a deleted file.

Exit 2 blocks the commit.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

VALID = {"attested", "asserted"}


def staged() -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=False,
    ).stdout.split()
    # Any path with a `store/` segment, not just a top-level one: stores live under
    # projects/<name>/store/ since the engine/project split, and a prefix test would have
    # silently stopped gating every record in the repo.
    return [
        Path(p) for p in out
        if p.endswith(".yaml") and "store" in Path(p).parts
    ]


def main() -> int:
    problems: list[str] = []
    for path in staged():
        if path.name == "methods.yaml" or not path.exists():
            continue
        try:
            rec = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            problems.append(f"[parse] {path}: {exc}")
            continue

        quarantined = "quarantine" in path.parts
        prov = rec.get("provenance")
        structural = rec.get("kind") in ("stratum", "work-state", "feature-band")

        if prov is None:
            if not structural:
                problems.append(f"[G-1] {path}: no provenance record")
            continue

        tier = prov.get("tier")
        if tier == "model-inferred" and not quarantined:
            problems.append(f"[G-2] {path}: model-inferred outside store/quarantine/")
        elif tier in VALID and quarantined:
            problems.append(f"[G-2] {path}: tier {tier!r} stranded in quarantine")
        elif tier == "attested" and not (prov.get("locus") or "").strip():
            problems.append(f"[G-1] {path}: attested without a resolvable locus")
        elif tier == "asserted" and not (prov.get("source") or "").strip():
            problems.append(f"[G-1] {path}: asserted without a source")
        elif tier not in VALID | {"model-inferred"}:
            problems.append(f"[G-1] {path}: unknown tier {tier!r}")

    if problems:
        print("COMMIT REFUSED - provenance is the validity condition, not metadata\n")
        for p in problems:
            print(f"  {p}")
        print("\nFix the record, or move it to store/quarantine/ if it is model-inferred.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
