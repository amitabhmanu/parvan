"""Fail-closed loader for the Parvan constraint store.

Record-level invariants live on the dataclasses in :mod:`parvan.model`. This module adds the
graph-level ones that cannot be checked on a record in isolation - G-4 and D-2 - plus
referential integrity, and refuses the whole store if anything fails.

Refusing loudly is the point. A store that half-loads is a store that quietly drops the
constraint that would have caught the error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .model import Edge, Interval, Node, Provenance, Violation

# Referents may legitimately be attested by these kinds without circularity: they are dated
# by non-textual means. A referent attested only by texts is text-derived (G-4).
EXTERNAL_KINDS: frozenset[str] = frozenset(("anchor", "horizon", "reception"))


class StoreError(Exception):
    """Raised when a store fails validation. Carries every violation, not just the first."""

    def __init__(self, violations: list[Violation]) -> None:
        self.violations = violations
        super().__init__(f"{len(violations)} violation(s)")

    def report(self) -> str:
        by_gate: dict[str, list[Violation]] = {}
        for v in self.violations:
            by_gate.setdefault(v.gate, []).append(v)
        lines: list[str] = []
        for gate in sorted(by_gate):
            lines.append(f"{gate} - {len(by_gate[gate])} violation(s)")
            for v in by_gate[gate]:
                lines.append(f"    {v.record}: {v.message}")
        return "\n".join(lines)


@dataclass
class Store:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)
    quarantine: list[Node | Edge] = field(default_factory=list)
    methods: frozenset[str] = frozenset()
    method_classes: dict[str, str] = field(default_factory=dict)
    schema_version: str = ""

    def edges_into(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges.values() if e.dst == node_id]

    def edges_out_of(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges.values() if e.src == node_id]

    def of_kind(self, kind: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.kind == kind]

    @property
    def anchors(self) -> list[Node]:
        """Nodes that fix absolute time. Text-derived referents are excluded by G-4."""
        return [n for n in self.nodes.values() if n.kind in EXTERNAL_KINDS]


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data or {}


def _node_from(raw: dict, path: str, in_quarantine: bool) -> Node:
    return Node(
        id=raw.get("id", ""),
        kind=raw.get("kind", ""),
        label=raw.get("label", ""),
        provenance=Provenance.parse(raw.get("provenance")),
        interval=Interval.parse(raw.get("interval")),
        dating_method=raw.get("dating_method"),
        independent_of=raw.get("independent_of") or [],
        holdout_eligible=bool(raw.get("holdout_eligible", False)),
        emergence=Interval.parse(raw.get("emergence")),
        attestation=Interval.parse(raw.get("attestation")),
        text_derived=bool(raw.get("text_derived", False)),
        node_class=raw.get("class"),
        work=raw.get("work"),
        extent=raw.get("extent") or [],
        archetypal=str(raw.get("archetypal", "true")),
        source_file=path,
        in_quarantine=in_quarantine,
    )


def _edge_from(raw: dict, path: str, in_quarantine: bool) -> Edge:
    return Edge(
        id=raw.get("id", ""),
        type=raw.get("type", ""),
        src=raw.get("from", ""),
        dst=raw.get("to", ""),
        method=raw.get("method", ""),
        lag_min_years=int(raw.get("lag_min_years", 0) or 0),
        direction_uncertain=bool(raw.get("direction_uncertain", False)),
        confidence=float(raw.get("confidence", 1.0)),
        provenance=Provenance.parse(raw.get("provenance")),
        source_file=path,
        in_quarantine=in_quarantine,
    )


def load_methods(root: Path) -> tuple[frozenset[str], dict[str, str], str]:
    path = root / "methods.yaml"
    if not path.exists():
        raise StoreError(
            [Violation("R-6", str(path), "methods.yaml is missing; the vocabulary is required")]
        )
    raw = _read_yaml(path)
    methods = raw.get("methods") or {}
    classes = {name: (body or {}).get("class", "") for name, body in methods.items()}
    return frozenset(methods), classes, raw.get("schema_version", "")


def load(root: str | Path, *, strict: bool = True) -> Store:
    """Load and validate a store. Raises :class:`StoreError` unless ``strict`` is False.

    ``strict=False`` is for tooling that needs to inspect a broken store in order to report
    on it. Never use it in the solver path - a solve over an unvalidated store is exactly
    the confidently-wrong fixpoint the design warns about.
    """
    root = Path(root)
    violations: list[Violation] = []

    methods, method_classes, schema_version = load_methods(root)
    store = Store(methods=methods, method_classes=method_classes, schema_version=schema_version)

    seen_ids: dict[str, str] = {}

    def _register(rec_id: str, path: str, kind: str) -> bool:
        if not rec_id:
            violations.append(Violation("R-2", path, f"{kind} record has no id"))
            return False
        if rec_id in seen_ids:
            violations.append(
                Violation("R-2", path, f"duplicate id {rec_id!r}, first seen in {seen_ids[rec_id]}")
            )
            return False
        seen_ids[rec_id] = path
        return True

    # --- nodes -----------------------------------------------------------------
    for path in sorted((root / "nodes").rglob("*.yaml")):
        raw = _read_yaml(path)
        if not raw:
            continue
        rel = str(path.relative_to(root))
        node = _node_from(raw, rel, in_quarantine=False)
        if not _register(node.id, rel, "node"):
            continue
        violations += node.validate()
        store.nodes[node.id] = node

    # --- edges -----------------------------------------------------------------
    for path in sorted((root / "edges").rglob("*.yaml")):
        raw = _read_yaml(path)
        if not raw:
            continue
        rel = str(path.relative_to(root))
        edge = _edge_from(raw, rel, in_quarantine=False)
        if not _register(edge.id, rel, "edge"):
            continue
        violations += edge.validate(methods)
        store.edges[edge.id] = edge

    # --- quarantine (G-2) ------------------------------------------------------
    # Parsed and validated, never added to nodes/edges, never reaching a solve.
    for path in sorted((root / "quarantine").rglob("*.yaml")):
        raw = _read_yaml(path)
        if not raw:
            continue
        rel = str(path.relative_to(root))
        if raw.get("kind"):
            rec = _node_from(raw, rel, in_quarantine=True)
            violations += rec.validate()
        else:
            rec = _edge_from(raw, rel, in_quarantine=True)
            violations += rec.validate(methods)
        store.quarantine.append(rec)

    violations += _check_graph(store)

    if violations and strict:
        raise StoreError(violations)
    return store


def _check_graph(store: Store) -> list[Violation]:
    """Invariants that need the whole graph: referential integrity, G-4, D-2, R-5."""
    out: list[Violation] = []

    # --- referential integrity -------------------------------------------------
    for edge in store.edges.values():
        for role, target in (("from", edge.src), ("to", edge.dst)):
            if target not in store.nodes:
                out.append(
                    Violation(
                        "R-3",
                        edge.source_file or edge.id,
                        f"{role} references unknown node {target!r}",
                    )
                )

    # --- R-5: ordering edges need a strict lag ---------------------------------
    # Without it a chain collapses to one constraint and a directed cycle of these edges
    # never reports infeasible - the diagnostic quietly stops working.
    for edge in store.edges.values():
        if edge.type in ("cites", "frames") and edge.lag_min_years <= 0:
            out.append(
                Violation(
                    "R-5",
                    edge.source_file or edge.id,
                    f"{edge.type!r} edge needs lag_min_years > 0; at zero the chain "
                    "transmits nothing and directed cycles stop reporting infeasible",
                )
            )

    for referent in store.of_kind("referent"):
        rec = referent.source_file or referent.id
        incoming = store.edges_into(referent.id)

        # --- G-4: no node may both date a referent and be dated by it ----------
        attesters = {e.src for e in incoming if e.type == "attests"}
        presupposers = {e.src for e in incoming if e.type == "presupposes"}
        for circular in sorted(attesters & presupposers):
            out.append(
                Violation(
                    "G-4",
                    rec,
                    f"node {circular!r} both attests and presupposes this referent; "
                    "its interval would derive from a text it then constrains",
                )
            )

        # --- G-4: text-derived referents may not anchor ------------------------
        externally_attested = any(
            store.nodes[e.src].kind in EXTERNAL_KINDS
            for e in incoming
            if e.type == "attests" and e.src in store.nodes
        )
        if referent.text_derived and externally_attested:
            out.append(
                Violation(
                    "G-4",
                    rec,
                    "marked text_derived but carries an external attestation; "
                    "clear the flag or remove the external edge - it cannot be both",
                )
            )
        if not referent.text_derived and not externally_attested and incoming:
            out.append(
                Violation(
                    "G-4",
                    rec,
                    "attested only by texts but not marked text_derived: true; "
                    "an unflagged referent of this kind can anchor the very strata "
                    "that date it",
                )
            )

        # --- D-2: inclusion rule ------------------------------------------------
        # Reify only anchors, or referents shared by two or more sources. A singly
        # attested referent cannot propagate, so it adds a node and buys nothing.
        sources = {e.src for e in incoming}
        if len(sources) < 2 and not externally_attested:
            out.append(
                Violation(
                    "D-2",
                    rec,
                    f"degree {len(sources)} and no external attestation; reify a referent "
                    "only if it is an anchor or is shared by two or more sources",
                )
            )

    return out
