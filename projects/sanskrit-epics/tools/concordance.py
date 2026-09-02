"""Concordance over the project's Sanskrit corpora, for promoting edges asserted -> attested.

Every hit is a citable locus in the form the store uses (R-1), so an edge's provenance can
name a verse a stranger can check. A search that returns nothing is also a result: a measured
silence is what turns an argument from absence into evidence anyone can re-run.

    uv run python tools/concordance.py yavan
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
finding was wrong. Truncate before the stem-final vowel, always, and treat a zero result from
an untruncated stem as meaningless.

The loaders themselves now live in corpora.py, behind the engine's Corpus protocol, which is
what enforces that a corpus is completely read before anything is searched over it. This file
is the command line and the epic-facing shims the instruments import.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpora import (AV, MBH, RAGH, RAM, SANSKRIT, Verse, av_fold,  # noqa: E402,F401
                     strip_diacritics)


# ---------------------------------------------------------------------------------------
# Shims. The instruments (aspect, subjunctive, writing, apparatus) import these by name.
# ---------------------------------------------------------------------------------------

def load() -> list[Verse]:
    """The Ramayana."""
    return list(RAM.load())


def load_mbh() -> list[Verse]:
    """The Mahabharata, with apparatus status preserved.

    A handful of GRETIL lines are malformed at source - a space where the separator should be,
    a missing sigil, one line with no text at all. Those are transcription defects, not parse
    failures, and the note is printed so the number is visible every time rather than sitting
    in a log. Anything above the corpus tolerance is refused outright by Corpus.load.
    """
    out = list(MBH.load())
    if MBH.unparsed:
        print(f"note: {MBH.unparsed}/{MBH.candidates} MBh lines unparsed "
              f"({100 * MBH.unparsed / MBH.candidates:.3f}%), malformed at source",
              file=sys.stderr)
    return out


def load_av() -> list[Verse]:
    """The accented Saunaka Atharvaveda."""
    return list(AV.load())


def load_ragh() -> list[Verse]:
    """Kalidasa's Raghuvamsa, the genre control."""
    return list(RAGH.load())


def load_corpus(name: str) -> list[Verse]:
    return {"mbh": load_mbh, "av": load_av, "ragh": load_ragh}.get(name, load)()


def search(
    verses: list[Verse], pattern: str, *, kandas: set[int] | None = None, fold: bool = False
) -> list[Verse]:
    """Search a list of verses, folding Vedic accent when the verses are Atharvavedic.

    Dispatch is on the verse rather than on a corpus handle because the instruments pass in
    lists they have already filtered and mixed - a corpus object would have to be threaded
    through every call site to say something each verse already knows.
    """
    import re

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
                    help="MBh and Raghuvamsa: exclude star passages, which the editors judged "
                         "non-archetypal. A floor resting on a star passage is a floor on "
                         "an interpolation.")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    # Refused rather than ignored: the Baroda Ramayana and the Atharvaveda mark no
    # interpolations at all, so accepting the flag here would filter nothing while implying
    # to the reader of the finding that an apparatus check had been run.
    if args.archetypal_only and not SANSKRIT[args.corpus].has_apparatus:
        sys.exit(f"--archetypal-only: {SANSKRIT[args.corpus].name} has no apparatus, so the "
                 "flag would filter nothing while implying it had. Drop it, and say in the "
                 "finding that this edition makes no archetypal/interpolated distinction.")

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
