"""Data model for the Parvan constraint store.

Gate and requirement references (G-*, R-*, D-*) point at the requirements index in the
design document. The invariants enforced here are the store's validity conditions, not
conveniences: see G-1, G-2, G-4, R-4, D-2.

Time is a signed integer year in astronomical numbering - year 0 is 1 BCE - so arithmetic
never crosses a discontinuity (D-6). ``None`` means unbounded in that direction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

NodeKind = Literal[
    "anchor", "horizon", "referent", "stratum", "work-state", "reception", "feature-band"
]
EdgeType = Literal["presupposes", "attests", "cites", "contains", "frames", "absent-from"]
Tier = Literal["attested", "asserted", "model-inferred"]

NODE_KINDS: frozenset[str] = frozenset(
    ("anchor", "horizon", "referent", "stratum", "work-state", "reception", "feature-band")
)
EDGE_TYPES: frozenset[str] = frozenset(
    ("presupposes", "attests", "cites", "contains", "frames", "absent-from")
)
TIERS: frozenset[str] = frozenset(("attested", "asserted", "model-inferred"))

# Structural nodes are inferred groupings, not evidential claims, so they carry no
# provenance. Everything else asserts something about the world and must cite a source.
REQUIRES_PROVENANCE: frozenset[str] = frozenset(("anchor", "horizon", "referent", "reception"))

# Edges that order two nodes in time, and so must carry a minimum transmission lag (R-5).
# Without strict lag a chain collapses to a single constraint and directed cycles never
# report infeasible.
LAGGED_EDGES: frozenset[str] = frozenset(("cites", "frames"))


@dataclass(frozen=True)
class Violation:
    """A refused record. ``gate`` names the invariant so failures trace back to the design."""

    gate: str
    record: str
    message: str

    def __str__(self) -> str:
        return f"[{self.gate}] {self.record}: {self.message}"


@dataclass
class Interval:
    """A closed year interval.

    ``hedge`` preserves the scholarly wording verbatim (D-6) so the Bayesian layer can
    reinterpret it as a distribution without re-reading sources.
    """

    floor: int | None = None
    ceiling: int | None = None
    hedge: str | None = None

    @property
    def unbounded_below(self) -> bool:
        return self.floor is None

    @property
    def is_empty(self) -> bool:
        return self.floor is not None and self.ceiling is not None and self.floor > self.ceiling

    def validate(self, record: str, label: str) -> list[Violation]:
        if self.is_empty:
            return [
                Violation(
                    "R-4",
                    record,
                    f"{label} interval is empty: floor {self.floor} "
                    f"is later than ceiling {self.ceiling}",
                )
            ]
        return []

    @classmethod
    def parse(cls, raw: dict | None) -> Interval:
        if raw is None:
            return cls()
        return cls(floor=raw.get("floor"), ceiling=raw.get("ceiling"), hedge=raw.get("hedge"))


@dataclass
class Provenance:
    """Where a claim comes from. The validity condition, not metadata (G-1).

    ``attested`` needs a resolvable locus - a verse ID, inscription number, coin catalogue
    entry, excavation report page. ``asserted`` needs a publication and page, and is carried
    as that scholar's claim rather than as fact. ``model-inferred`` is quarantined (G-2).
    """

    tier: Tier
    locus: str | None = None
    source: str | None = None
    note: str | None = None

    def validate(self, record: str, *, in_quarantine: bool) -> list[Violation]:
        out: list[Violation] = []

        if self.tier not in TIERS:
            return [Violation("G-1", record, f"unknown provenance tier {self.tier!r}")]

        if self.tier == "model-inferred":
            if not in_quarantine:
                out.append(
                    Violation(
                        "G-2",
                        record,
                        "model-inferred records may not enter the main store; they belong "
                        "in store/quarantine/ and are never loaded into a solve",
                    )
                )
            return out

        if in_quarantine:
            out.append(
                Violation(
                    "G-2",
                    record,
                    f"tier {self.tier!r} found in quarantine; promote it into the store "
                    "with a human commit rather than leaving it here",
                )
            )

        if self.tier == "attested" and not (self.locus and self.locus.strip()):
            out.append(Violation("G-1", record, "tier 'attested' requires a resolvable locus"))
        if self.tier == "asserted" and not (self.source and self.source.strip()):
            out.append(
                Violation(
                    "G-1", record, "tier 'asserted' requires a source (publication and page)"
                )
            )
        return out

    @classmethod
    def parse(cls, raw: dict | None) -> Provenance | None:
        if raw is None:
            return None
        return cls(
            tier=raw.get("tier"),
            locus=raw.get("locus"),
            source=raw.get("source"),
            note=raw.get("note"),
        )


@dataclass
class Node:
    id: str
    kind: NodeKind
    label: str = ""
    provenance: Provenance | None = None

    # anchor / horizon / reception
    interval: Interval = field(default_factory=Interval)
    dating_method: str | None = None
    independent_of: list[str] = field(default_factory=list)
    holdout_eligible: bool = False

    # referent
    emergence: Interval = field(default_factory=Interval)
    attestation: Interval = field(default_factory=Interval)
    text_derived: bool = False
    node_class: str | None = None

    # stratum / work-state
    work: str | None = None
    extent: list[str] = field(default_factory=list)
    archetypal: str = "true"  # 'true' | 'star' - BORI apparatus status, see corpus audit

    source_file: str = ""
    in_quarantine: bool = False

    def validate(self) -> list[Violation]:
        rec = self.source_file or self.id
        out: list[Violation] = []

        if self.kind not in NODE_KINDS:
            return [Violation("R-2", rec, f"unknown node kind {self.kind!r}")]

        if self.kind in REQUIRES_PROVENANCE and self.provenance is None:
            out.append(
                Violation("G-1", rec, f"node kind {self.kind!r} requires a provenance record")
            )
        elif self.provenance is not None:
            out += self.provenance.validate(rec, in_quarantine=self.in_quarantine)

        out += self.interval.validate(rec, "interval")
        out += self.emergence.validate(rec, "emergence")
        out += self.attestation.validate(rec, "attestation")

        if self.kind == "referent":
            # R-4: first attestation caps emergence from above and never bounds it below.
            ec, af = self.emergence.ceiling, self.attestation.floor
            if ec is not None and af is not None and ec > af:
                out.append(
                    Violation(
                        "R-4",
                        rec,
                        f"emergence.ceiling ({ec}) is later than attestation.floor ({af}); "
                        "attestation caps emergence from above, never bounds it below",
                    )
                )

        if self.archetypal not in ("true", "star"):
            out.append(
                Violation(
                    "R-1", rec, f"archetypal must be 'true' or 'star', got {self.archetypal!r}"
                )
            )
        return out


@dataclass
class Edge:
    id: str
    type: EdgeType
    src: str
    dst: str
    method: str = ""
    # None means "inherit the run's epsilon", which is distinct from an explicit 0.
    # Conflating the two silently swallows a legitimate zero-lag absence edge (R-5, O-1).
    lag_min_years: int | None = None
    direction_uncertain: bool = False
    confidence: float = 1.0
    provenance: Provenance | None = None

    source_file: str = ""
    in_quarantine: bool = False

    def validate(self, methods: frozenset[str]) -> list[Violation]:
        rec = self.source_file or self.id
        out: list[Violation] = []

        if self.type not in EDGE_TYPES:
            return [Violation("R-3", rec, f"unknown edge type {self.type!r}")]

        # G-1: every edge is a constraint, so every edge needs provenance.
        if self.provenance is None:
            out.append(Violation("G-1", rec, "edge requires a provenance record"))
        else:
            out += self.provenance.validate(rec, in_quarantine=self.in_quarantine)

        # R-6: closed method vocabulary. Methods are the units of the reliability model,
        # so an unknown tag would silently create an unpooled category.
        if not self.method:
            out.append(Violation("R-6", rec, "edge requires a method tag"))
        elif self.method not in methods:
            out.append(
                Violation(
                    "R-6",
                    rec,
                    f"method {self.method!r} is not in the closed vocabulary "
                    "(store/methods.yaml); adding one is a schema change",
                )
            )

        if self.lag_min_years is not None and self.lag_min_years < 0:
            out.append(Violation("R-5", rec, "lag_min_years may not be negative"))

        if not 0.0 <= self.confidence <= 1.0:
            out.append(Violation("R-3", rec, f"confidence {self.confidence} outside [0, 1]"))

        return out
