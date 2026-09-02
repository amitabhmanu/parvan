"""Concordance over the GRETIL Ramayana TEI, for promoting edges from asserted to attested.

Every hit is a citable locus in the form the store uses (R-1), so an edge's provenance can
name a verse a stranger can check. A search that returns nothing is also a result: a measured
silence is what turns an argument from absence into evidence anyone can re-run.

    uv run python tools/concordance.py yavana
    uv run python tools/concordance.py 'p[aā][tṭ]aliputra' --kanda 2-6 --count

Sanskrit compounds mean a stem can sit anywhere inside a word, so matches are substring by
default and must be read in context before being cited. The tool finds candidates; it does
not judge them.

SEARCH THE CONSONANTAL STEM, NOT THE CITATION FORM. This is the trap that produced the worst
error in this project so far. A stem-final vowel changes under case-ending sandhi, so the
citation form often does not occur anywhere in the text:

    cola   + accusative plural -> colan      'cola' does not match
    yavana + accusative plural -> yavanan    'yavana' does not match
    andhra + accusative plural -> andhras    'andhra' does not match

Searching 'yavana' over Kiskindhakanda returned zero and was published as a finding. The
correct search, 'yavan', returns Ram.4.042.011 - kambojan yavanams caiva sakan - and the
finding was wrong. Truncate before the stem-final vowel, always, and treat a zero result
from an untruncated stem as meaningless.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "corpus"
CORPUS = ROOT / "sa_rAmAyaNa.xml"
MBH_DIR = ROOT / "mbh"
AV_FILE = ROOT / "av" / "avs_acu.htm"
RAGH_FILE = ROOT / "kavya" / "kragh_pu.htm"

VERSE_RE = re.compile(r'<lg xml:id="R_(\d+)\.(\d+)\.(\d+)">(.*?)</lg>', re.S)
LINE_RE = re.compile(r'<l xml:id="[^"]*">(.*?)</l>', re.S)

# Mahabharata lines: "06,001.001a<TAB>text<BR>", and star passages "06,001.000*0001_01".
# A star passage is one the BORI editors relegated to the apparatus as non-archetypal -
# evidence that a reading is an interpolation rather than part of the constituted text.
# The Ramayana TEI carries no apparatus at all, so this check exists only for the MBh.
#   06,001.001a<TAB>text<BR>            plain verse, pada letter
#   06,001.001d*0003_01<TAB>text<BR>    star passage - the marker follows the pada letter
#   10,000.000*0001_01<>text<BR>        parvan 10 uses "<>" where the rest use a tab
#
# Both variants cost real data before they were noticed: an earlier pattern put the star
# marker before the pada letter and required a tab, which silently dropped 1,710 of 13,189
# lines in parvan 6 and the whole of parvan 10. An absence search over a corpus that loads
# 87% of its lines is worthless, so load_mbh asserts completeness rather than trusting this.
#   01,001.001A<TAB>text<BR>            prose runs use an UPPERCASE pada letter
#   01,001.053b@002_0001<TAB>text<BR>   "@" marks an APPENDIX passage, "*" a star passage
#
# Both apparatus markers mean the same thing for dating: the BORI editors judged the passage
# non-archetypal. They differ only in length, so `archetypal` covers both.
MBH_LINE = re.compile(r"^\d+,\d+\.")
TOLERANCE = 0.0005  # 0.05% - source defects only, never a pattern bug
# The marker itself has many shapes - @001A_0001, *0128a_01, *0128_01(127ab) - so it is
# matched as "anything after * or @ up to the separator" rather than enumerated. Enumerating
# cost three rounds of silent data loss; the completeness check below is what caught each.
MBH_RE = re.compile(
    r"^(\d+),(\d+)\.(\d+)[a-zA-Z]*([*@][^\t<]*)?(?:\t|<>)(.*?)(?:<BR>)?\s*$"
)


# Atharvaveda-Samhita, Saunaka recension, ACCENTED text (GRETIL avs_acu.htm; Orlandi 1991
# collated with Roth/Whitney 1856, rev. Griffiths 2009). The one Vedic text GRETIL ships with
# accent intact - its stated default, confirmed in the Rgveda header, is that "accents have
# been dropped in order to facilitate word search".
#
#   (AVS_1,1.1a) ye trisaptah pariyanti visva rupani bibhratah |<BR>
#   (AVS_19,7.1[2.3]a) ...        books 11-20 carry a second numbering in brackets
#
# Two encoding differences from the epic files, and both silently break a cross-corpus
# search if not normalised:
#   1. Accent is a combining acute (udatta) or grave (svarita) on the vowel. A pattern
#      typed without accents matches nothing at all unless the text is folded first.
#   2. Vocalic r is r + COMBINING RING BELOW, not the precomposed 'r' the epic files use.
#      So 'krta' finds 5,142 vocalic r's in the epics and zero here.
# av_fold() handles both. Vocalic l (9 occurrences) is left alone: folding it to 'l' would
# collide with the intervocalic retroflex d the same file writes 'l'.
AV_LINE = re.compile(
    r"^\(AVŚ_(\d+),(\d+)(?:\[\d+\])?\.(?:\[-\])?(\d+)(?:\[[^\]]*\])?"
    r"[a-zA-Zḍ]?\)\s*(.*?)(?:<BR>)?\s*$"
)

ACCENTS = ("\N{COMBINING ACUTE ACCENT}", "\N{COMBINING GRAVE ACCENT}")
"""Udatta and svarita. Named escapes because these marks are invisible in source."""

def av_fold(s: str) -> str:
    """Drop Vedic accent and write vocalic r the way the epic corpora write it.

    Length, retroflexion, nasalisation and palatalisation all survive - only the two accent
    marks are removed, so this is not strip_diacritics(). The result is directly comparable
    with a Ramayana or Mahabharata line.
    """
    d = unicodedata.normalize("NFD", s)
    for a in ACCENTS:
        d = d.replace(a, "")
    # r + COMBINING RING BELOW -> the precomposed vocalic r the epic files use.
    d = d.replace(
        "r\N{COMBINING RING BELOW}\N{COMBINING MACRON}",
        "\N{LATIN SMALL LETTER R WITH DOT BELOW AND MACRON}",
    )
    d = d.replace("r\N{COMBINING RING BELOW}", "\N{LATIN SMALL LETTER R WITH DOT BELOW}")
    return unicodedata.normalize("NFC", d)


# Kalidasa, Raghuvamsa (GRETIL kragh_pu.htm; ed. Scharpe, Kalidasa Lexicon I, Bruges 1964).
# Held as a GENRE CONTROL, not as a dating source. It is court epic in the same genre as the
# Ramayana, narrating the same dynasty, and securely dated c. 400 CE - so a doctrine it
# discusses freely cannot be one the Ramayana's genre forbade it to discuss.
#
#   ... vande parvatiparamesvarau  // Ragh_1.1 //<BR>       constituted text
#   ... vaikhanasair adrsyagni...  // Ragh_1.49* //<BR>     ksepaka: interpolated
#
# The star means what it means in the Mahabharata files - the editor judged the verse an
# interpolation - so `archetypal` carries it and --archetypal-only filters it. A control
# resting on an interpolated verse is not a control.
RAGH_MARK = re.compile(r"//\s*Ragh_(\d+)\.(\d+)(\*?)\s*//")

@dataclass(frozen=True)
class Verse:
    kanda: int
    sarga: int
    sloka: int
    text: str
    work: str = "Ram"
    archetypal: bool = True

    @property
    def locus(self) -> str:
        star = "" if self.archetypal else "*"
        return f"{self.work}.{self.kanda}.{self.sarga:03d}.{self.sloka:03d}{star}"


def strip_diacritics(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)
    )


def load_mbh(directory: Path = MBH_DIR) -> list[Verse]:
    """The BORI Mahabharata, one file per parvan, with apparatus status preserved."""
    if not directory.exists():
        sys.exit(f"Mahabharata corpus not found at {directory}; see docs/corpus-audit.md")
    out: list[Verse] = []
    seen = dropped = 0
    for f in sorted(directory.glob("mbh_*_u.htm")):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if not MBH_LINE.match(line):
                continue
            seen += 1
            m = MBH_RE.match(line)
            if not m:
                dropped += 1
                continue
            parvan, adhyaya, sloka, star, text = m.groups()
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                out.append(Verse(int(parvan), int(adhyaya), int(sloka), text,
                                 work="MBh", archetypal=star is None))
    # A handful of GRETIL lines are malformed at source - a space where the separator should
    # be, a missing sigil, one line with no text at all. Those are transcription defects, not
    # parse failures, and the tolerance is deliberately tiny: anything above it means the
    # pattern is wrong again, and an absence search over a corpus that silently drops lines
    # is worthless. Three rounds of exactly that happened before this check existed.
    if dropped > seen * TOLERANCE:
        raise SystemExit(
            f"MBh parse incomplete: {dropped} of {seen} verse lines did not match "
            f"({100 * dropped / seen:.2f}%). Every absence search over this corpus would be "
            "unsound. Fix MBH_RE before using it."
        )
    if dropped:
        print(f"note: {dropped}/{seen} MBh lines unparsed ({100 * dropped / seen:.3f}%), "
              "malformed at source", file=sys.stderr)
    return out


def load_av(path: Path = AV_FILE) -> list[Verse]:
    """The accented Saunaka Atharvaveda, padas merged into whole verses.

    Accent is preserved in `text` - it is the reason to hold this file rather than the
    unaccented sibling - and folded at search time, so a pattern written for the epics works
    here unchanged.
    """
    if not path.exists():
        sys.exit(f"Atharvaveda not found at {path}; see docs/corpus-audit.md")
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [ln for ln in lines if ln.startswith("(AV")]
    merged: dict[tuple[int, int, int], list[str]] = {}
    order: list[tuple[int, int, int]] = []
    dropped = 0
    for ln in body:
        m = AV_LINE.match(ln)
        if not m:
            dropped += 1
            continue
        book, hymn, verse, text = m.groups()
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        key = (int(book), int(hymn), int(verse))
        if key not in merged:
            merged[key] = []
            order.append(key)
        if text:
            merged[key].append(text)
    # Same discipline as load_mbh, and for the same reason: the Atharvaveda's value here is
    # as a *baseline* for absence claims, and a baseline that quietly drops lines makes every
    # differential computed against it wrong in the direction that flatters the hypothesis.
    if dropped > len(body) * TOLERANCE:
        raise SystemExit(
            f"AV parse incomplete: {dropped} of {len(body)} verse lines did not match "
            f"({100 * dropped / len(body):.2f}%). Fix AV_LINE before using it."
        )
    return [
        Verse(b, h, v, " / ".join(merged[(b, h, v)]), work="AVS")
        for (b, h, v) in order
        if merged[(b, h, v)]
    ]


def load_ragh(path: Path = RAGH_FILE) -> list[Verse]:
    """Kalidasa's Raghuvamsa, verses reassembled across their line breaks."""
    if not path.exists():
        sys.exit(f"Raghuvamsa not found at {path}; see docs/corpus-audit.md")
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if "Ragh_1.1 //" in ln)
    except StopIteration:
        sys.exit("Raghuvamsa: no verse markers found; the file layout has changed")
    out: list[Verse] = []
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
        buf.append(RAGH_MARK.sub("", t).strip())
        text = " ".join(x for x in buf if x)
        buf = []
        if text:
            out.append(Verse(int(m.group(1)), int(m.group(2)), 0, text,
                             work="Ragh", archetypal=not m.group(3)))
    # Same discipline as the other two loaders. A control corpus that silently drops verses
    # would understate the very presence it exists to demonstrate, which is the direction
    # that flatters the hypothesis - so leftover text is refused rather than ignored.
    if buf:
        raise SystemExit(
            f"Raghuvamsa parse incomplete: {len(buf)} line(s) after the last verse marker "
            "were never attached to a verse. Fix RAGH_MARK before using it."
        )
    return out


def load_corpus(name: str) -> list[Verse]:
    if name == "mbh":
        return load_mbh()
    if name == "av":
        return load_av()
    if name == "ragh":
        return load_ragh()
    return load()


def load(path: Path = CORPUS) -> list[Verse]:
    if not path.exists():
        sys.exit(f"corpus not found at {path}; see docs/corpus-audit.md")
    raw = path.read_text(encoding="utf-8")
    out: list[Verse] = []
    for k, sg, sl, body in VERSE_RE.findall(raw):
        lines = []
        for t in LINE_RE.findall(body):
            # Many <l> elements wrap their padas in <seg type="pada" n="a">. Leaving that
            # markup in the text glued attribute text onto the first word of every seg -
            # 16,154 corrupted tokens, so `n="a">sa` was in the corpus where `sa` should be.
            # Word-final searches survived it; a whole-word or anchored search did not, and
            # the literal string "pada" inside type="pada" was matchable as if it were text.
            # The Mahabharata loader has always stripped tags here; this one did not.
            t = re.sub(r"<[^>]+>", " ", t)
            lines.append(re.sub(r"\s+", " ", t).strip())
        out.append(Verse(int(k), int(sg), int(sl), " / ".join(lines)))
    return out


def search(
    verses: list[Verse], pattern: str, *, kandas: set[int] | None = None, fold: bool = False
) -> list[Verse]:
    rx = re.compile(pattern, re.I)
    hits = []
    for v in verses:
        if kandas and v.kanda not in kandas:
            continue
        hay = av_fold(v.text) if v.work == "AVS" else v.text
        if fold:
            hay = strip_diacritics(hay)
        if rx.search(hay):
            hits.append(v)
    return hits


def parse_kandas(spec: str | None) -> set[int] | None:
    if not spec:
        return None
    out: set[int] = set()
    for part in spec.split(","):
        if "-" in part:
            lo, hi = part.split("-")
            out |= set(range(int(lo), int(hi) + 1))
        else:
            out.add(int(part))
    return out


def main() -> None:
    # Windows consoles default to cp1252, which cannot encode IAST. Without this every
    # diacritic search dies on a UnicodeEncodeError instead of printing its result.
    # Reported by the extraction agent on its first run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pattern", help="regex, matched against IAST verse text")
    ap.add_argument("--kanda", help="restrict to kandas/parvans/books, e.g. 2-6 or 1,7")
    ap.add_argument("--fold", action="store_true",
                    help="strip diacritics before matching (looser, noisier)")
    ap.add_argument("--count", action="store_true", help="report counts only")
    ap.add_argument("--corpus", choices=("ram", "mbh", "av", "ragh"), default="ram")
    ap.add_argument("--archetypal-only", action="store_true",
                    help="MBh and Raghuvamsa: exclude star passages, which the BORI editors judged "
                         "non-archetypal. A floor resting on a star passage is a floor on "
                         "an interpolation.")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    verses = load_corpus(args.corpus)
    if args.archetypal_only:
        verses = [v for v in verses if v.archetypal]
    kandas = parse_kandas(args.kanda)
    scope = [v for v in verses if not kandas or v.kanda in kandas]
    hits = search(verses, args.pattern, kandas=kandas, fold=args.fold)

    unit = {"mbh": "parvan", "av": "book", "ragh": "sarga"}.get(args.corpus, "kanda")
    where = f"{unit} {args.kanda}" if args.kanda else "whole text"
    print(f"pattern {args.pattern!r} over {where}: {len(hits)} hit(s) in {len(scope)} verses")

    if args.count or not hits:
        if not hits:
            print("  MEASURED SILENCE - re-runnable by anyone with the same corpus file")
        return

    print()
    for v in hits[: args.limit]:
        print(f"  {v.locus}  {v.text}")
    if len(hits) > args.limit:
        print(f"  ... {len(hits) - args.limit} more")


if __name__ == "__main__":
    main()
