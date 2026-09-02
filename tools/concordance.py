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

CORPUS = Path(__file__).resolve().parents[1] / "corpus" / "sa_rAmAyaNa.xml"

VERSE_RE = re.compile(r'<lg xml:id="R_(\d+)\.(\d+)\.(\d+)">(.*?)</lg>', re.S)
LINE_RE = re.compile(r'<l xml:id="[^"]*">(.*?)</l>', re.S)


@dataclass(frozen=True)
class Verse:
    kanda: int
    sarga: int
    sloka: int
    text: str

    @property
    def locus(self) -> str:
        return f"Ram.{self.kanda}.{self.sarga:03d}.{self.sloka:03d}"


def strip_diacritics(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)
    )


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
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    verses = load()
    kandas = parse_kandas(args.kanda)
    scope = [v for v in verses if not kandas or v.kanda in kandas]
    hits = search(verses, args.pattern, kandas=kandas, fold=args.fold)

    where = f"kanda {args.kanda}" if args.kanda else "whole text"
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
