"""The corpus protocol: how a project hands the engine a text it can cite.

The engine needs four things from a corpus and refuses to guess any of them: where a passage
lives (a locus a stranger can look up), what its text is, whether the edition judged it part
of the constituted text or of the apparatus, and - the part that has to be enforced rather
than trusted - whether the loader actually read all of it.

WHY THE COMPLETENESS CONTRACT IS IN THE BASE CLASS. It was written three times in the
Sanskrit project, and each time it was written because a loader had already silently dropped
text: a Mahabharata pattern that lost 1,710 lines of parvan 6 and the whole of parvan 10,
leaving 87% of the corpus loaded and every absence search over it worthless. An absence claim
is the strongest thing this framework produces - a measured silence is evidence anyone can
re-run - and it is exactly the claim a lossy loader turns into a lie, in the direction that
flatters the hypothesis. So Corpus.load will not return passages a subclass has not
accounted for. A loader may opt out, but only by saying so in code, once, with a reason.

The three other lessons that are structural here rather than remembered:

- Editorial matter is not text. Searching raw PTS pages for 'potthaka' (book) returns three
  hits, all of them the editors writing "in the Sinhalese manuscript" - which would have
  manufactured, out of nothing but apparatus, the exact claim the search existed to test. So
  Passage.notes holds editorial matter apart from Passage.text, and Corpus.search ignores it
  unless asked.
- Apparatus status is a dating fact, not a formatting detail. An edition that marks which
  passages it judged non-archetypal is handing over a per-passage label of relative lateness.
  A floor resting on such a passage is a floor on an interpolation, so `archetypal` travels
  with every passage and is filterable.
- Normalisation belongs to the corpus. Accent, vocalic-r notation, pointing, sigla and
  orthographic variation differ per edition, so folding is declared by the corpus that needs
  it rather than applied globally to everything.
"""

from __future__ import annotations

import re
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Sequence


class CorpusError(Exception):
    """A corpus that cannot be trusted to be complete. Never a warning."""


@dataclass(frozen=True)
class Passage:
    """One citable unit of text: a verse, a line, a printed page, a tablet column.

    `ref` is the address within the work, coarsest level first, and its meaning is declared
    by the corpus (`ref_levels`). Keeping it an opaque tuple is what lets a two-level
    tradition (Homer: book, line) and a three-level one (book, chapter, verse) share a store.

    `notes` is editorial matter that belongs to the page but is not the text - PTS footnotes,
    an apparatus band, a translator's gloss. It is carried so it can be inspected and
    excluded, never merged into `text`.
    """

    ref: tuple[int | str, ...]
    text: str
    work: str
    archetypal: bool = True
    notes: str = ""


@dataclass
class Tally:
    """A loader's account of what it read and what it could not.

    Passed into `_parse` and checked by `load`. The point is that the denominator is reported
    by the code that did the reading, so "0 unparsed" cannot be produced by a pattern that
    matched nothing in the first place.
    """

    seen: int = 0
    dropped: int = 0
    reasons: list[str] = field(default_factory=list)
    residue: list[str] = field(default_factory=list)
    exemption: str | None = None

    def saw(self, n: int = 1) -> None:
        """Count a candidate unit the loader was offered."""
        self.seen += n

    def drop(self, why: str) -> None:
        """Count a candidate the loader could not parse. Keeps the first few reasons."""
        self.dropped += 1
        if len(self.reasons) < 5:
            self.reasons.append(why)

    def leftover(self, what: str) -> None:
        """Structural residue: text read but never attached to any passage.

        A ratio cannot see this. Raghuvamsa verses span line breaks, so a broken verse marker
        leaves a buffer of real text belonging to no verse while every line still parses.
        """
        self.residue.append(what)

    def exempt(self, reason: str) -> None:
        """Opt out of the ratio check, on the record.

        For a format with no countable candidate unit - a continuous prose file with no line
        sigla, say. Structural residue is still refused. If you are reaching for this to make
        a red build go away, the loader is wrong, not the contract.
        """
        self.exemption = reason


class Corpus(ABC):
    """A text the store can cite. Subclasses supply `_parse` and the identifying metadata.

    Subclass contract:

    - `sigil` prefixes every locus and must match what the store's provenance already uses.
    - `ref_levels` names the address levels; `ref_pad` zero-pads them for sorting.
    - `_parse` yields Passage objects and reports to the Tally.
    - `fold` may be overridden when the edition's orthography differs from the tradition's
      normal search form.
    """

    name: str = ""
    sigil: str = ""
    ref_levels: tuple[str, ...] = ()
    #: What one passage is called in prose. Defaults to the finest ref level.
    unit: str = ""
    ref_pad: tuple[int, ...] = ()
    #: Does the edition mark passages it judged non-archetypal? Only then does
    #: archetypal_only mean anything, so search refuses the flag rather than silently
    #: returning everything and implying the filter was applied.
    has_apparatus: bool = False
    #: 0.05%. Source-level transcription defects only. Anything above it means the pattern
    #: is wrong, and it is set this tight deliberately.
    tolerance: float = 0.0005

    def __init__(self) -> None:
        self._cache: list[Passage] | None = None
        self.unparsed = 0
        self.candidates = 0
        self.exemption: str | None = None

    # -- subclass hooks ------------------------------------------------------------------

    @abstractmethod
    def _parse(self, tally: Tally) -> Iterator[Passage]:
        """Read the source files and yield passages, reporting to `tally`."""

    def fold(self, text: str) -> str:
        """Normalise text for searching. Identity unless the edition needs otherwise."""
        return text

    # -- the contract --------------------------------------------------------------------

    def load(self) -> list[Passage]:
        """Read the corpus, refusing it if the loader cannot account for what it skipped."""
        if self._cache is not None:
            return self._cache

        tally = Tally()
        passages = list(self._parse(tally))

        if tally.residue:
            raise CorpusError(
                f"{self.name}: {len(tally.residue)} fragment(s) of text were read but never "
                f"attached to a passage, e.g. {tally.residue[0][:90]!r}. Fix the loader: text "
                "that belongs to no locus is text no search will ever find."
            )

        if tally.exemption is None:
            if tally.seen == 0:
                raise CorpusError(
                    f"{self.name}: the loader produced {len(passages)} passage(s) without "
                    "counting a single candidate, so its completeness cannot be checked. "
                    "Call tally.saw() per candidate unit, or tally.exempt(reason) to opt out "
                    "on the record."
                )
            if tally.dropped > tally.seen * self.tolerance:
                pct = 100 * tally.dropped / tally.seen
                raise CorpusError(
                    f"{self.name}: parse incomplete - {tally.dropped} of {tally.seen} "
                    f"candidate unit(s) did not match ({pct:.2f}%, tolerance "
                    f"{100 * self.tolerance:.2f}%). Every absence search over this corpus "
                    f"would be unsound. Examples: {tally.reasons}"
                )

        self.unparsed = tally.dropped
        self.candidates = tally.seen
        self.exemption = tally.exemption
        self._cache = passages
        return passages

    # -- loci ----------------------------------------------------------------------------

    def locus(self, p: Passage) -> str:
        """The citation form. Apparatus passages carry a trailing '*', as in print."""
        parts = []
        for i, level in enumerate(p.ref):
            pad = self.ref_pad[i] if i < len(self.ref_pad) else 0
            parts.append(f"{level:0{pad}d}" if isinstance(level, int) and pad else str(level))
        star = "" if p.archetypal else "*"
        return f"{self.sigil}.{'.'.join(parts)}{star}"

    def parse_locus(self, locus: str) -> tuple[int | str, ...]:
        """Inverse of `locus`, so an extent in the store can be matched against text."""
        body = locus.rstrip("*")
        if not body.startswith(f"{self.sigil}."):
            raise ValueError(f"{locus!r} is not a {self.sigil} locus")
        out: list[int | str] = []
        for part in body[len(self.sigil) + 1:].split("."):
            out.append(int(part) if part.isdigit() else part)
        return tuple(out)

    # -- searching -----------------------------------------------------------------------

    def search(
        self,
        pattern: str,
        *,
        passages: Sequence[Passage] | None = None,
        divisions: Iterable[int | str] | None = None,
        fold_diacritics: bool = False,
        archetypal_only: bool = False,
        include_notes: bool = False,
    ) -> list[Passage]:
        """Substring/regex search over passage text.

        A hit is a CANDIDATE, not a citation: in a compounding language a stem sits inside
        unrelated words, and literal terms are routinely metaphorical. Read every hit.

        `include_notes` is off by default and should usually stay off - editorial matter is
        the editors' words, and counting it as text manufactures evidence.
        """
        if archetypal_only and not self.has_apparatus:
            raise CorpusError(
                f"{self.name} has no apparatus, so archetypal_only would filter nothing while "
                "implying it had. Drop the flag, or say in the finding that this edition "
                "makes no archetypal/interpolated distinction at all."
            )
        pool = self.load() if passages is None else passages
        if archetypal_only:
            pool = [p for p in pool if p.archetypal]
        if divisions is not None:
            keep = set(divisions)
            pool = [p for p in pool if p.ref and p.ref[0] in keep]

        rx = re.compile(pattern, re.I)
        hits = []
        for p in pool:
            hay = self.fold(p.text + (" " + p.notes if include_notes else ""))
            if fold_diacritics:
                hay = strip_diacritics(hay)
            if rx.search(hay):
                hits.append(p)
        return hits

    def describe(self) -> str:
        loaded = self.load()
        unit = self.unit or (self.ref_levels[-1] if self.ref_levels else "passage")
        bits = [f"{self.name}: {len(loaded)} {unit}s"]
        if self.has_apparatus:
            arch = sum(1 for p in loaded if p.archetypal)
            bits.append(f"{arch} archetypal, {len(loaded) - arch} apparatus")
        if self.unparsed:
            bits.append(f"{self.unparsed}/{self.candidates} unparsed, malformed at source")
        if self.exemption:
            bits.append(f"completeness ratio exempt: {self.exemption}")
        return "; ".join(bits)


def strip_diacritics(s: str) -> str:
    """Drop every combining mark. Lossy and noisy - a last resort, not a normaliser."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)
    )
