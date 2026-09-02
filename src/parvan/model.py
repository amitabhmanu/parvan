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
EdgeType = Literal[
    "presupposes", "attests", "grounds", "cites", "contains", "frames", "absent-from"
]
Tier = Literal["attested", "asserted", "model-inferred"]

NODE_KINDS: frozenset[str] = frozenset(
    ("anchor", "horizon", "referent", "stratum", "work-state", "reception", "feature-band")
)
EDGE_TYPES: frozenset[str] = frozenset(
    ("presupposes", "attests", "grounds", "cites", "contains", "frames", "absent-from")
)

# `grounds` is the missing half of `attests`. Attestation caps an emergence from above and
# never floors it (R-4), so a referent whose emergence is only attested contributes no floor
# to anything - which is how thirteen horizon nodes came to be inert while the floors they
# were supposed to supply sat hardcoded in the encoder instead.
#
# A material horizon makes a genuinely two-sided claim: iron metallurgy did not exist in
# South Asia before c. 1300 BCE. That is a floor, and only material evidence can make it,
# so only material node kinds may ground.
GROUNDING_KINDS: frozenset[str] = frozenset(("horizon", "anchor"))
TIERS: frozenset[str] = frozenset(("attested", "asserted", "model-inferred"))

# Structural nodes are inferred groupings, not evidential claims, so they carry no
# provenance. Everything else asserts something about the world and must cite a source.
REQUIRES_PROVENANCE: frozenset[str] = frozenset(("anchor", "horizon", "referent", "reception"))

# Edges that order two nodes in time, and so must carry a minimum transmission lag (R-5).
# Without strict lag a chain collapses to a single constraint and directed cycles never
# report infeasible.
LAGGED_EDGES: frozenset[str] = frozenset(("cites", "frames"))

# Edge types whose attested form is an argument from silence, and so must carry a
# re-runnable Silence record naming a positive control (G-9).
SILENCE_EDGES: frozenset[str] = frozenset(("absent-from",))


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
class Control:
    """Evidence that the instrument which measured a silence can find anything at all.

    Either a pattern with the count it returns, or a locus the search does hit. Both are
    accepted because the two strongest controls in the store are of different kinds: a
    signet ring the Ramayana core describes eleven times where a letter would be, and the
    Digha-Nikaya's list of low arts that enumerates finger-reckoning and computation and
    stops short of writing.
    """

    pattern: str | None = None
    locus: str | None = None
    #: A number a bespoke instrument produces - a paired ratio's denominator, a rate per
    #: 10,000 words - which no regex can re-derive. Requires `instrument`.
    measurement: str | None = None
    instrument: str = ""
    expect: int | None = None
    #: Which corpus this control was measured over. None means the silence's own. A control
    #: run against a DIFFERENT corpus is often the strongest one available: the same pattern
    #: string returning thousands of hits elsewhere proves the string is well-formed, which
    #: is precisely what a mistruncated stem is not.
    corpus: str | None = None
    #: Search options the count was measured under. Silently dropping either of these makes
    #: a sound control look broken - and, worse, could make a broken one look sound.
    include_notes: bool = False
    archetypal_only: bool = False
    note: str = ""

    def validate(self, record: str, edge: str, i: int) -> list[Violation]:
        kinds = [bool(self.pattern), bool(self.locus), bool(self.measurement)]
        if sum(kinds) != 1:
            return [
                Violation(
                    "G-9", record,
                    f"{edge}: control {i} must be exactly one of a pattern (re-runnable as a "
                    "search), a locus (resolvable in the corpus), or a measurement (a number "
                    "some named instrument produces)",
                )
            ]
        if self.pattern and self.expect is None:
            return [
                Violation("G-9", record,
                          f"{edge}: control {i} gives pattern {self.pattern!r} with no expected "
                          "count, so nobody can tell whether it still holds")
            ]
        if self.measurement and not self.instrument.strip():
            return [
                Violation("G-9", record,
                          f"{edge}: control {i} describes a measurement with no instrument, so "
                          "nobody can reproduce it")
            ]
        return []

    @property
    def kind(self) -> str:
        if self.pattern:
            return "pattern"
        return "locus" if self.locus else "measurement"

    @classmethod
    def parse(cls, raw) -> Control:
        if isinstance(raw, str):
            # "ram/yavan" - a reference to a control the project's profile already declares.
            corpus, _, pattern = raw.partition("/")
            return cls(pattern=pattern or None, note=f"profile control {raw}", expect=-1)
        raw = raw or {}
        return cls(
            pattern=raw.get("pattern"),
            locus=raw.get("locus"),
            measurement=raw.get("measurement"),
            instrument=raw.get("instrument", ""),
            expect=raw.get("expect"),
            corpus=raw.get("corpus"),
            include_notes=bool(raw.get("include_notes", False)),
            archetypal_only=bool(raw.get("archetypal_only", False)),
            note=raw.get("note", ""),
        )


@dataclass
class Silence:
    """A measured absence, in the form that lets someone else re-run it (G-9).

    An argument from silence is the strongest thing this project produces and the easiest to
    fake, because a search that finds nothing looks exactly like a search that cannot find
    anything. `yavana` over Kiskindhakanda returned zero, was published as a finding, and had
    to be retracted when the truncated stem returned the verse. The prose record could not
    have caught that; a declared control would have.

    So an attested absence must say what corpus it searched, over what scope, with how many
    passages under it, with which patterns, what it got, how to re-run it, and - the part
    that is the whole gate - what proves the instrument was working.
    """

    corpus: str = ""
    scope: str = ""
    #: The scope again, machine-readable, so the claim can actually be re-run rather than
    #: merely described. `divisions` are values of the corpus's coarsest ref level; each
    #: `excludes` entry is a locus PREFIX (Ram.6.105 drops that whole sarga).
    divisions: list[int | str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    passages: int | None = None
    patterns: list[str] = field(default_factory=list)
    hits: int | None = None
    measurement: str = ""
    instrument: str = ""
    controls: list[Control] = field(default_factory=list)
    #: Hits the search returned that were read and thrown out, with the reason. A string
    #: match is a candidate, not a citation, so a silence can legitimately have non-zero
    #: hits - but then it owes an account of every one of them.
    rejected: list[str] = field(default_factory=list)

    def validate(self, record: str, edge: str) -> list[Violation]:
        out: list[Violation] = []

        if not self.corpus.strip():
            out.append(Violation("G-9", record, f"{edge}: silence names no corpus"))
        if not self.scope.strip():
            out.append(Violation("G-9", record, f"{edge}: silence names no scope"))
        if not self.instrument.strip():
            out.append(
                Violation("G-9", record,
                          f"{edge}: silence names no instrument, so it is not re-runnable")
            )

        # A silence over nothing is vacuous, and a zero denominator is the exact shape of a
        # corpus that failed to load - which is how 87% of the Mahabharata went missing once.
        if self.passages is None or self.passages <= 0:
            out.append(
                Violation("G-9", record,
                          f"{edge}: silence must state how many passages it searched, and the "
                          "number must be positive - an absence over nothing is vacuous, and a "
                          "zero denominator is what a corpus that failed to load looks like")
            )

        if not self.patterns and not self.measurement.strip():
            out.append(
                Violation("G-9", record,
                          f"{edge}: silence lists no patterns and describes no measurement, so "
                          "there is nothing for anyone to re-run")
            )
        if self.patterns and self.hits is None:
            out.append(
                Violation("G-9", record,
                          f"{edge}: silence searched {len(self.patterns)} pattern(s) but records "
                          "no hit count")
            )

        # A silence whose search returned hits is not thereby wrong - a string match is a
        # candidate, not a citation, and the two dhrtarastri hits in the Ramayana are a
        # bird-ancestress in a genealogy of geese, not the Mahabharata's king. But a record
        # that reports a non-zero count and says nothing about it is indistinguishable from
        # one whose author never looked.
        if self.hits and not (self.rejected or self.measurement.strip()):
            out.append(
                Violation(
                    "G-9",
                    record,
                    f"{edge}: silence records {self.hits} hit(s) and accounts for none of "
                    "them. Read every one and either list it under `rejected` with the reason "
                    "it is not the claim, or describe the reading in `measurement`",
                )
            )

        # The gate.
        if not self.controls:
            out.append(
                Violation(
                    "G-9",
                    record,
                    f"{edge}: silence declares no positive control. A search never shown to "
                    "find anything cannot be trusted to report that something is missing - "
                    "this is the gate that exists because an untruncated stem returned zero "
                    "and the zero was published as a finding",
                )
            )
        for i, c in enumerate(self.controls):
            out += c.validate(record, edge, i)
        return out

    @classmethod
    def parse(cls, raw: dict | None) -> Silence | None:
        if raw is None:
            return None
        return cls(
            corpus=str(raw.get("corpus", "")),
            scope=str(raw.get("scope", "")),
            divisions=list(raw.get("divisions") or []),
            excludes=[str(x) for x in (raw.get("excludes") or [])],
            passages=raw.get("passages"),
            patterns=[str(p) for p in (raw.get("patterns") or [])],
            hits=raw.get("hits"),
            measurement=str(raw.get("measurement", "")),
            instrument=str(raw.get("instrument", "")),
            controls=[Control.parse(c) for c in (raw.get("controls") or [])],
            rejected=[str(r) for r in (raw.get("rejected") or [])],
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
    # Ranges carved out of `extent` and claimed by a more specific stratum. Without this a
    # seam inside a book can only be expressed by two strata both claiming the book, which
    # leaves the overlap unresolved and forces every check to subtract it by hand - exactly
    # the sort of convention that holds until someone forgets (G-8).
    excludes: list[str] = field(default_factory=list)
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
    silence: Silence | None = None

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

        # G-9. Only the attested tier: an asserted absence is carried as a scholar's claim
        # and stands or falls on their published argument, not on a search this project ran.
        attested = self.provenance is not None and self.provenance.tier == "attested"
        if self.type in SILENCE_EDGES and attested:
            if self.silence is None:
                out.append(
                    Violation(
                        "G-9",
                        rec,
                        "an attested absence needs a `silence:` record - corpus, scope, "
                        "passages searched, patterns, hits, instrument, and at least one "
                        "positive control. Prose in the locus is not re-runnable",
                    )
                )
            else:
                out += self.silence.validate(rec, self.id)
        elif self.silence is not None and not attested:
            out.append(
                Violation("G-9", rec,
                          "a `silence:` record on a non-attested edge claims a measurement "
                          "the tier does not support; promote it or drop the block")
            )

        return out
