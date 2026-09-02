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


def load_corpus(name: str) -> list[Verse]:
    return load_mbh() if name == "mbh" else load()


def load(path: Path = CORPUS) -> list[Verse]:
    if not path.exists():
        sys.exit(f"corpus not found at {path}; see docs/corpus-audit.md")
    raw = path.read_text(encoding="utf-8")
    out: list[Verse] = []
    for k, sg, sl, body in VERSE_RE.findall(raw):
        lines = [re.sub(r"\s+", " ", t).strip() for t in LINE_RE.findall(body)]
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
        hay = strip_diacritics(v.text) if fold else v.text
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
    ap.add_argument("--kanda", help="restrict to kandas, e.g. 2-6 or 1,7")
    ap.add_argument("--fold", action="store_true",
                    help="strip diacritics before matching (looser, noisier)")
    ap.add_argument("--count", action="store_true", help="report counts only")
    ap.add_argument("--corpus", choices=("ram", "mbh"), default="ram")
    ap.add_argument("--archetypal-only", action="store_true",
                    help="MBh only: exclude star passages, which the BORI editors judged "
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

    unit = "parvan" if args.corpus == "mbh" else "kanda"
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
