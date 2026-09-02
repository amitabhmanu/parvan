"""The Sanskrit and Pali corpora, behind the engine's Corpus protocol.

Every parsing lesson this project paid for is preserved here verbatim; what has changed is
where the *enforcement* lives. The completeness check that each loader used to carry as its
own copy-pasted tail is now inherited from parvan.corpus.Corpus, so a fifth corpus added next
week cannot forget it - which is the whole reason the check exists, since it was forgotten
three times running while it was a convention.

    from corpora import RAM, MBH, AV, RAGH, DN, VIN

Each is a singleton; load() is cached, so passing them around is free.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterator

from parvan.corpus import Corpus, CorpusError, Passage, Tally, strip_diacritics  # noqa: F401

ROOT = Path(__file__).resolve().parents[1] / "corpus"


class Verse(Passage):
    """A Passage that still answers to the epic vocabulary.

    The instruments (aspect, subjunctive, writing, apparatus, compounds) address verses as
    .kanda/.sarga/.sloka and format their own loci. Those names are the project's, not the
    engine's, so they live on this side of the boundary rather than being pushed into
    Passage, where a Homerist would have to explain what a kanda is.
    """

    __slots__ = ()

    @property
    def kanda(self) -> int:
        return self.ref[0]

    @property
    def sarga(self) -> int:
        return self.ref[1]

    @property
    def sloka(self) -> int:
        return self.ref[2]

    @property
    def locus(self) -> str:
        star = "" if self.archetypal else "*"
        return f"{self.work}.{self.kanda}.{self.sarga:03d}.{self.sloka:03d}{star}"


def verse(k: int, s: int, sl: int, text: str, work: str = "Ram", archetypal: bool = True) -> Verse:
    return Verse(ref=(k, s, sl), text=text, work=work, archetypal=archetypal)


# =========================================================================================
# Ramayana - GRETIL TEI of the Baroda critical edition
# =========================================================================================

VERSE_RE = re.compile(r'<lg xml:id="R_(\d+)\.(\d+)\.(\d+)">(.*?)</lg>', re.S)
LINE_RE = re.compile(r'<l xml:id="[^"]*">(.*?)</l>', re.S)


class Ramayana(Corpus):
    """The Baroda Ramayana. No apparatus: this edition marks no interpolations at all,
    which is why the Mahabharata's star passages are the only lateness label the project has.
    """

    name = "Ramayana (Baroda, GRETIL TEI)"
    sigil = "Ram"
    ref_levels = ("kanda", "sarga", "sloka")
    ref_pad = (0, 3, 3)
    has_apparatus = False

    path = ROOT / "sa_rAmAyaNa.xml"

    def _parse(self, tally: Tally) -> Iterator[Verse]:
        if not self.path.exists():
            sys.exit(f"corpus not found at {self.path}; see docs/corpus-audit.md")
        raw = self.path.read_text(encoding="utf-8")
        for k, sg, sl, body in VERSE_RE.findall(raw):
            tally.saw()
            lines = []
            for t in LINE_RE.findall(body):
                # Many <l> elements wrap their padas in <seg type="pada" n="a">. Leaving that
                # markup in glued attribute text onto the first word of every seg - 16,154
                # corrupted tokens, so `n="a">sa` sat in the corpus where `sa` should be.
                # Word-final searches survived it; anchored ones did not, and the literal
                # string "pada" inside type="pada" was matchable as if it were text.
                t = re.sub(r"<[^>]+>", " ", t)
                lines.append(re.sub(r"\s+", " ", t).strip())
            yield verse(int(k), int(sg), int(sl), " / ".join(lines))


# =========================================================================================
# Mahabharata - BORI critical edition, apparatus preserved
# =========================================================================================

# Lines look like "06,001.001a<TAB>text<BR>", and star passages "06,001.000*0001_01".
# A star passage is one the BORI editors relegated to the apparatus as non-archetypal -
# evidence that a reading is an interpolation rather than part of the constituted text.
#   06,001.001a<TAB>text<BR>            plain verse, pada letter
#   06,001.001d*0003_01<TAB>text<BR>    star passage - the marker follows the pada letter
#   10,000.000*0001_01<>text<BR>        parvan 10 uses "<>" where the rest use a tab
#   01,001.001A<TAB>text<BR>            prose runs use an UPPERCASE pada letter
#   01,001.053b@002_0001<TAB>text<BR>   "@" marks an APPENDIX passage, "*" a star passage
#
# Both variants cost real data before they were noticed: an earlier pattern put the star
# marker before the pada letter and required a tab, which silently dropped 1,710 of 13,189
# lines in parvan 6 and the whole of parvan 10. Both apparatus markers mean the same thing
# for dating - the editors judged the passage non-archetypal - so `archetypal` covers both.
MBH_LINE = re.compile(r"^\d+,\d+\.")
# The marker itself has many shapes - @001A_0001, *0128a_01, *0128_01(127ab) - so it is
# matched as "anything after * or @ up to the separator" rather than enumerated. Enumerating
# cost three rounds of silent data loss; the completeness contract is what caught each.
MBH_RE = re.compile(r"^(\d+),(\d+)\.(\d+)[a-zA-Z]*([*@][^\t<]*)?(?:\t|<>)(.*?)(?:<BR>)?\s*$")


class Mahabharata(Corpus):
    name = "Mahabharata (BORI, GRETIL)"
    sigil = "MBh"
    ref_levels = ("parvan", "adhyaya", "sloka")
    ref_pad = (0, 3, 3)
    has_apparatus = True

    directory = ROOT / "mbh"

    def _parse(self, tally: Tally) -> Iterator[Verse]:
        if not self.directory.exists():
            sys.exit(f"Mahabharata corpus not found at {self.directory}; see docs/corpus-audit.md")
        for f in sorted(self.directory.glob("mbh_*_u.htm")):
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if not MBH_LINE.match(line):
                    continue
                tally.saw()
                m = MBH_RE.match(line)
                if not m:
                    tally.drop(line[:60])
                    continue
                parvan, adhyaya, sloka, star, text = m.groups()
                text = re.sub(r"<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    yield verse(int(parvan), int(adhyaya), int(sloka), text,
                                work="MBh", archetypal=star is None)


# =========================================================================================
# Atharvaveda-Samhita, Saunaka recension, ACCENTED
# =========================================================================================

# GRETIL avs_acu.htm; Orlandi 1991 collated with Roth/Whitney 1856, rev. Griffiths 2009. The
# one Vedic text GRETIL ships with accent intact - its stated default, confirmed in the
# Rgveda header, is that accents are dropped to facilitate word search.
#
#   (AVS_1,1.1a) ye trisaptah pariyanti visva rupani bibhratah |<BR>
#   (AVS_19,7.1[2.3]a) ...        books 11-20 carry a second numbering in brackets
AV_LINE = re.compile(
    r"^\(AVŚ_(\d+),(\d+)(?:\[\d+\])?\.(?:\[-\])?(\d+)(?:\[[^\]]*\])?"
    r"[a-zA-Zḍ]?\)\s*(.*?)(?:<BR>)?\s*$"
)

ACCENTS = ("\N{COMBINING ACUTE ACCENT}", "\N{COMBINING GRAVE ACCENT}")
"""Udatta and svarita. Named escapes because these marks are invisible in source."""


def av_fold(s: str) -> str:
    """Drop Vedic accent and write vocalic r the way the epic corpora write it.

    Two encoding differences from the epic files, and both silently break a cross-corpus
    search if not normalised:
      1. Accent is a combining acute (udatta) or grave (svarita) on the vowel. A pattern
         typed without accents matches nothing at all unless the text is folded first.
      2. Vocalic r is r + COMBINING RING BELOW, not the precomposed form the epic files use.
         So 'krta' finds 5,142 vocalic r's in the epics and zero here.

    Length, retroflexion, nasalisation and palatalisation all survive - only the two accent
    marks are removed, so this is not strip_diacritics(). Vocalic l (9 occurrences) is left
    alone: folding it to 'l' would collide with the intervocalic retroflex d the same file
    writes 'l'.
    """
    d = unicodedata.normalize("NFD", s)
    for a in ACCENTS:
        d = d.replace(a, "")
    d = d.replace(
        "r\N{COMBINING RING BELOW}\N{COMBINING MACRON}",
        "\N{LATIN SMALL LETTER R WITH DOT BELOW AND MACRON}",
    )
    d = d.replace("r\N{COMBINING RING BELOW}", "\N{LATIN SMALL LETTER R WITH DOT BELOW}")
    return unicodedata.normalize("NFC", d)


class Atharvaveda(Corpus):
    """The accented Saunaka Atharvaveda, padas merged into whole verses.

    Accent is preserved in the text - it is the reason to hold this file rather than the
    unaccented sibling - and folded at search time, so a pattern written for the epics works
    here unchanged. Its value is as a BASELINE for absence claims, and a baseline that quietly
    drops lines makes every differential computed against it wrong in the flattering
    direction.
    """

    name = "Atharvaveda-Samhita, Saunaka (accented)"
    sigil = "AVS"
    ref_levels = ("book", "hymn", "verse")
    ref_pad = (0, 3, 3)

    path = ROOT / "av" / "avs_acu.htm"

    def fold(self, text: str) -> str:
        return av_fold(text)

    def _parse(self, tally: Tally) -> Iterator[Verse]:
        if not self.path.exists():
            sys.exit(f"Atharvaveda not found at {self.path}; see docs/corpus-audit.md")
        body = [ln for ln in self.path.read_text(encoding="utf-8").splitlines()
                if ln.startswith("(AV")]
        merged: dict[tuple[int, int, int], list[str]] = {}
        order: list[tuple[int, int, int]] = []
        for ln in body:
            tally.saw()
            m = AV_LINE.match(ln)
            if not m:
                tally.drop(ln[:60])
                continue
            book, hymn, v, text = m.groups()
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            key = (int(book), int(hymn), int(v))
            if key not in merged:
                merged[key] = []
                order.append(key)
            if text:
                merged[key].append(text)
        for k in order:
            if merged[k]:
                yield verse(k[0], k[1], k[2], " / ".join(merged[k]), work="AVS")


# =========================================================================================
# Kalidasa, Raghuvamsa - the GENRE CONTROL
# =========================================================================================

# GRETIL kragh_pu.htm; ed. Scharpe, Kalidasa Lexicon I, Bruges 1964. Held as a genre control,
# not as a dating source: court epic in the same genre as the Ramayana, narrating the same
# dynasty, securely dated c. 400 CE - so a doctrine it discusses freely cannot be one the
# Ramayana's genre forbade it to discuss.
#
#   ... vande parvatiparamesvarau  // Ragh_1.1 //<BR>       constituted text
#   ... vaikhanasair adrsyagni...  // Ragh_1.49* //<BR>     ksepaka: interpolated
#
# The star means what it means in the Mahabharata files, so archetypal carries it. A control
# resting on an interpolated verse is not a control.
RAGH_MARK = re.compile(r"//\s*Ragh_(\d+)\.(\d+)(\*?)\s*//")


class Raghuvamsa(Corpus):
    name = "Raghuvamsa (Kalidasa, ed. Scharpe)"
    sigil = "Ragh"
    ref_levels = ("sarga", "verse", "_")
    unit = "verse"
    ref_pad = (0, 3, 3)
    has_apparatus = True

    path = ROOT / "kavya" / "kragh_pu.htm"

    def _parse(self, tally: Tally) -> Iterator[Verse]:
        if not self.path.exists():
            sys.exit(f"Raghuvamsa not found at {self.path}; see docs/corpus-audit.md")
        lines = self.path.read_text(encoding="utf-8").splitlines()
        try:
            start = next(i for i, ln in enumerate(lines) if "Ragh_1.1 //" in ln)
        except StopIteration:
            sys.exit("Raghuvamsa: no verse markers found; the file layout has changed")
        buf: list[str] = []
        for ln in lines[start - 1:]:
            t = re.sub(r"<[^>]+>", " ", ln)
            t = re.sub(r"\s+", " ", t).strip()
            if not t:
                continue
            m = RAGH_MARK.search(t)
            if not m:
                buf.append(t)
                continue
            tally.saw()
            buf.append(RAGH_MARK.sub("", t).strip())
            text = " ".join(x for x in buf if x)
            buf = []
            if text:
                yield verse(int(m.group(1)), int(m.group(2)), 0, text,
                            work="Ragh", archetypal=not m.group(3))
        # Verses span line breaks here, so a broken marker leaves real text attached to no
        # verse while every line still parses. The ratio cannot see that; residue can.
        if buf:
            tally.leftover(" ".join(buf))


# =========================================================================================
# Pali - PTS texts, addressed by printed page
# =========================================================================================

PAGE = re.compile(r"\[page (\d+)\]")
RULE = re.compile(r"-{20,}")  # separates a PTS page's text from its footnotes

PALI_COLLECTIONS = {
    "dn": ("Digha-Nikaya", "DN", [("dighn1ou", "i"), ("dighn2ou", "ii"), ("dighn3ou", "iii")]),
    # The Vinaya's PTS volume order is Oldenberg's: Mahavagga, Cullavagga, the two halves of
    # the Suttavibhanga, Parivara - so "Vin iii.21" is a Suttavibhanga page, not a Mahavagga one.
    "vin": ("Vinaya-Pitaka", "Vin", [("vin1maou", "i"), ("vin2cuou", "ii"), ("vin3s1ou", "iii"),
                                     ("vin4s2ou", "iv"), ("vin5paou", "v")]),
}


class PaliCollection(Corpus):
    """A PTS edition addressed by volume and printed page.

    The only body of text this project can reach that is transmitted independently of Sanskrit
    epic tradition, dated by an independent apparatus, and still full of the same referents.

    FOOTNOTES ARE NOT TEXT, and this is not pedantry. Searching the raw page for 'potthaka',
    book, returns three hits, and all three are the PTS editors writing "Sihalapotthake", in
    the Sinhalese manuscript. Counting those would have produced the exact claim the search
    was meant to test - that this tradition knows books - out of nothing but apparatus. So
    everything below a page's rule line goes to `notes`, which search ignores by default.
    """

    ref_levels = ("volume", "page")
    unit = "page"
    directory = ROOT / "pali"

    def __init__(self, key: str) -> None:
        super().__init__()
        if key not in PALI_COLLECTIONS:
            sys.exit(f"unknown collection {key!r}; choose from {sorted(PALI_COLLECTIONS)}")
        self.key = key
        self.heading, self.sigil, self.files = PALI_COLLECTIONS[key]
        self.name = f"{self.heading} (PTS)"

    def locus(self, p: Passage) -> str:
        """PTS citation form - "DN ii.86" - which is how the Pali is cited everywhere."""
        return f"{self.sigil} {p.ref[0]}.{p.ref[1]}"

    def parse_locus(self, locus: str) -> tuple[int | str, ...]:
        m = re.match(rf"^{re.escape(self.sigil)}\s+([ivx]+)\.(\d+)$", locus.strip())
        if not m:
            raise ValueError(f"{locus!r} is not a {self.sigil} locus")
        return (m.group(1), int(m.group(2)))

    def _parse(self, tally: Tally) -> Iterator[Passage]:
        if not self.directory.exists():
            sys.exit(f"Pali corpus not found at {self.directory}; see docs/corpus-audit.md")
        for stem, vol in self.files:
            path = self.directory / f"{stem}.htm"
            if not path.exists():
                sys.exit(f"missing {path}: fetch the ANNOTATED (ou) files, not the plain ones - "
                         "the plain version strips the page references that make a locus citable")
            raw = path.read_text(encoding="utf-8", errors="replace")
            start = raw.find(self.heading)
            if start < 0:
                sys.exit(f"{path}: heading {self.heading!r} not found; the file layout has changed")
            body = re.sub(r"<[^>]+>", " ", raw[start:])
            parts = PAGE.split(body)
            if len(parts) < 3:
                sys.exit(f"{path}: no [page N] markers found; loci would be uncitable")
            for i in range(1, len(parts), 2):
                tally.saw()
                chunk = re.sub(r"\s+", " ", parts[i + 1])
                split = RULE.split(chunk, maxsplit=1)
                yield Passage(ref=(vol, int(parts[i])), text=split[0], work=self.sigil,
                              notes=split[1] if len(split) > 1 else "")


RAM = Ramayana()
MBH = Mahabharata()
AV = Atharvaveda()
RAGH = Raghuvamsa()
DN = PaliCollection("dn")
VIN = PaliCollection("vin")

SANSKRIT = {"ram": RAM, "mbh": MBH, "av": AV, "ragh": RAGH}
PALI = {"dn": DN, "vin": VIN}
