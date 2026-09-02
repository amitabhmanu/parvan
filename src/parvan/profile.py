"""The project profile: what an extraction agent must be told before it can search a corpus.

The extractor agent was the least portable thing in the Sanskrit project and the most
valuable. Its seven rules are universal - a string match is a candidate not a citation, check
the stratum and not just the text, a zero result is a deliverable, report contradictions and
never resolve them - but the tables underneath them are pure Sanskrit: sandhi truncation,
stems buried inside compounds, `cyavana` masquerading as `yavana`. Every tradition has an
analogue and none of them can be derived a priori. Greek has the augment, crasis and movable
nu; unpointed Hebrew has prefixed prepositions and ketiv/qere; Akkadian has logographic
against syllabic spellings; Chinese has loan graphs and no word boundaries.

So the profile carries the tables and the agent carries the rules.

THE ONE GATE THAT MATTERS HERE IS P-1: a search trap must come with a worked example. The
Sanskrit rule "truncate before the stem-final vowel" reads like pedantry until you see that
`yavana` returns zero over Kiskindhakanda and `yavan` returns the verse, and that the zero was
published as a finding before anyone noticed. A rule without a worked example is advice; a
rule with one is a check somebody can run. Refusing the profile is cheaper than discovering
which kind you wrote after the retraction.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .model import Violation

#: What a corpus is FOR. Roles are closed because the extractor reasons about them: it may
#: cite a primary corpus, must not date anything from a control, and has to say which
#: baseline an absence was measured against.
ROLES: frozenset[str] = frozenset((
    "primary",              # the text being dated; loci from here enter the store
    "baseline",             # an earlier text the primary is measured against
    "genre-control",        # same genre, secure date: rules out "the genre forbade it"
    "date-control",         # secure date, used to check a metric tracks date at all
    "independent-tradition",  # same referents, independent transmission and dating chain
    "reception",            # cites or reworks the primary; yields ceilings
))

#: Corpora an absence claim may be made over must prove their searches can find things.
NEEDS_CALIBRATION: frozenset[str] = frozenset(("primary", "baseline"))


@dataclass
class Example:
    """A worked example. The thing that makes a trap checkable rather than merely stated."""

    search: str = ""
    text_has: str = ""
    result: str = ""
    note: str = ""

    @classmethod
    def parse(cls, raw: dict) -> Example:
        return cls(
            search=str(raw.get("search", "")),
            text_has=str(raw.get("text_has", "")),
            result=str(raw.get("result", "")),
            note=str(raw.get("note", "")),
        )


@dataclass
class Trap:
    """A way a naive search over this language returns the wrong answer.

    ``cost`` records what it actually broke. It is optional, and worth filling in: an agent
    that has read what a rule cost last time applies it more carefully than one that has read
    the rule.
    """

    id: str
    rule: str
    examples: list[Example] = field(default_factory=list)
    severity: str = "high"
    cost: str = ""

    def validate(self, rec: str) -> list[Violation]:
        out: list[Violation] = []
        if not self.rule.strip():
            out.append(Violation("P-1", rec, f"trap {self.id!r} states no rule"))
        if not self.examples:
            out.append(
                Violation(
                    "P-1",
                    rec,
                    f"trap {self.id!r} has no worked example. A rule nobody can run is advice, "
                    "not a check: give a search, what the text actually has, and the result",
                )
            )
        for i, ex in enumerate(self.examples):
            if not (ex.search and ex.result):
                out.append(
                    Violation("P-1", rec,
                              f"trap {self.id!r} example {i} needs at least a search and a result")
                )
        return out


@dataclass
class CorpusEntry:
    """One corpus, joined to the adapter that reads it."""

    key: str
    role: str
    object: str = ""
    note: str = ""
    command: str = ""
    #: Patterns known to be PRESENT, with the count the corpus returns. A search tool that
    #: cannot find these cannot be trusted to report a silence.
    positive_controls: list[dict] = field(default_factory=list)
    #: Patterns known to be ABSENT. A measured silence already established, re-runnable.
    known_silences: list[dict] = field(default_factory=list)

    def validate(self, rec: str) -> list[Violation]:
        out: list[Violation] = []
        if self.role not in ROLES:
            out.append(
                Violation("P-2", rec,
                          f"corpus {self.key!r} has role {self.role!r}, not in {sorted(ROLES)}")
            )
        if not self.object:
            out.append(Violation("P-3", rec, f"corpus {self.key!r} names no adapter object"))
        if self.role in NEEDS_CALIBRATION and not self.positive_controls:
            out.append(
                Violation(
                    "P-4",
                    rec,
                    f"corpus {self.key!r} has role {self.role!r} but declares no positive "
                    "control. An absence claim over a corpus whose searches were never shown "
                    "to find anything is unmeasured silence, not measured silence",
                )
            )
        for c in self.positive_controls + self.known_silences:
            if "pattern" not in c or "expect" not in c:
                out.append(
                    Violation("P-4", rec,
                              f"corpus {self.key!r}: each control needs a pattern and an expect")
                )
        return out


@dataclass
class Profile:
    project: str = ""
    tradition: str = ""
    languages: list[str] = field(default_factory=list)
    script: str = ""
    adapter_module: str = ""
    corpora: dict[str, CorpusEntry] = field(default_factory=dict)
    traps: list[Trap] = field(default_factory=list)
    conventions: dict = field(default_factory=dict)
    source: Path | None = None

    # -- loading --------------------------------------------------------------------------

    @classmethod
    def load(cls, path: str | Path) -> Profile:
        """Read and validate a profile. Refuses the whole file if anything fails."""
        p = Path(path)
        if p.is_dir():
            p = p / "profile.yaml"
        if not p.is_file():
            raise ProfileError([Violation("P-0", str(p), "no profile.yaml here")])
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

        prof = cls(
            project=raw.get("project", ""),
            tradition=raw.get("tradition", ""),
            languages=list(raw.get("languages", []) or []),
            script=raw.get("script", ""),
            adapter_module=raw.get("adapter_module", ""),
            conventions=raw.get("conventions", {}) or {},
            source=p,
        )
        for key, body in (raw.get("corpora") or {}).items():
            body = body or {}
            prof.corpora[key] = CorpusEntry(
                key=key,
                role=body.get("role", ""),
                object=body.get("object", ""),
                note=body.get("note", ""),
                command=body.get("command", ""),
                positive_controls=list(body.get("positive_controls", []) or []),
                known_silences=list(body.get("known_silences", []) or []),
            )
        for t in raw.get("search_traps") or []:
            prof.traps.append(
                Trap(
                    id=t.get("id", "?"),
                    rule=t.get("rule", ""),
                    severity=t.get("severity", "high"),
                    cost=t.get("cost", ""),
                    examples=[Example.parse(e) for e in (t.get("examples") or [])],
                )
            )

        violations = prof.validate()
        if violations:
            raise ProfileError(violations)
        return prof

    def validate(self) -> list[Violation]:
        rec = str(self.source or self.project or "profile")
        out: list[Violation] = []
        if not self.project:
            out.append(Violation("P-2", rec, "profile names no project"))
        if not self.corpora:
            out.append(Violation("P-2", rec, "profile declares no corpora"))
        if not self.traps:
            out.append(
                Violation(
                    "P-1",
                    rec,
                    "profile declares no search traps. Every writing system has at least one "
                    "way a naive search returns the wrong answer; if you genuinely believe "
                    "this one does not, say so as a trap with that as its rule",
                )
            )
        for c in self.corpora.values():
            out += c.validate(rec)
        for t in self.traps:
            out += t.validate(rec)
        return out

    # -- joining to the adapters ------------------------------------------------------------

    def adapters(self) -> dict[str, object]:
        """Import the project's adapter module and resolve each corpus object.

        Loaded by path rather than by import name so the engine never needs a project's
        directory on sys.path - the projects are data to it, not dependencies.
        """
        if not self.adapter_module or self.source is None:
            return {}
        mod_path = (self.source.parent / self.adapter_module).resolve()
        if not mod_path.is_file():
            raise ProfileError(
                [Violation("P-3", str(self.source), f"adapter_module {mod_path} does not exist")]
            )
        spec = importlib.util.spec_from_file_location(f"_parvan_adapters_{self.project}", mod_path)
        if spec is None or spec.loader is None:
            raise ProfileError(
                [Violation("P-3", str(self.source), f"cannot import {mod_path}")]
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        out: dict[str, object] = {}
        missing: list[Violation] = []
        for key, entry in self.corpora.items():
            obj = getattr(module, entry.object, None)
            if obj is None:
                missing.append(
                    Violation("P-3", str(self.source),
                              f"corpus {key!r}: {self.adapter_module} defines no {entry.object!r}")
                )
                continue
            out[key] = obj
        if missing:
            raise ProfileError(missing)
        return out

    def calibrate(self) -> list[dict]:
        """Run every declared control and report whether the corpus still answers as claimed.

        This is what stops the profile being decorative. A positive control that stops
        matching means the loader, the corpus file or the orthography moved under you, and
        every silence measured since is unsound.
        """
        results: list[dict] = []
        adapters = self.adapters()
        for key, entry in self.corpora.items():
            corpus = adapters.get(key)
            if corpus is None:
                continue
            checks = (
                [("positive", c) for c in entry.positive_controls]
                + [("silence", c) for c in entry.known_silences]
            )
            for kind, c in checks:
                pattern, expect = c["pattern"], c["expect"]
                kwargs = {}
                if c.get("archetypal_only"):
                    kwargs["archetypal_only"] = True
                if c.get("include_notes"):
                    kwargs["include_notes"] = True
                got = len(corpus.search(pattern, **kwargs))
                results.append({
                    "corpus": key,
                    "kind": kind,
                    "pattern": pattern,
                    "expect": expect,
                    "got": got,
                    "ok": got == expect,
                    "note": c.get("note", ""),
                })
        return results


class ProfileError(Exception):
    """Raised when a profile fails validation. Carries every violation, not just the first."""

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
