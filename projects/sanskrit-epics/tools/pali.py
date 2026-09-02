"""Concordance over the Pali canon (PTS text via GRETIL), for cross-tradition checks.

    uv run python tools/pali.py rajagah
    uv run python tools/pali.py 'lekh|likh' --notes

The Pali canon is the only body of text this project can reach that is transmitted
independently of Sanskrit epic tradition, dated by an independent scholarly apparatus, and
still full of the same referents - Magadha, Kosala, Rajagaha, Pataliputta. Independence of
dating chain is the design's stated criterion for what a corpus addition is worth, and
nothing else available scores as high on it.

LOCI are PTS volume and page - "DN ii.86" - which is how the Pali is cited everywhere, so an
edge's provenance names something a stranger can look up in print.

FOOTNOTES ARE NOT TEXT, and this is not a pedantic distinction. Searching the raw page for
'potthaka', book, returns three hits, and all three are the PTS editors writing
"Sihalapotthake", 'in the Sinhalese manuscript'. Counting those would have produced the exact
claim the search was meant to test - that this tradition knows books - out of nothing but
apparatus. Everything below a page's rule line is editorial and is held separately, in
Passage.notes, which the engine's search ignores unless asked. --notes asks.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpora import PALI, PALI_COLLECTIONS  # noqa: E402

COLLECTIONS = PALI_COLLECTIONS


def load(collection: str = "dn"):
    """PTS pages of one collection. Kept as a function for the instruments that call it."""
    if collection not in PALI:
        sys.exit(f"unknown collection {collection!r}; choose from {sorted(PALI)}")
    return list(PALI[collection].load())


def search(pages, pattern: str, *, notes: bool = False) -> list[tuple[object, str]]:
    """Return each matching page with the window of text around the first hit.

    Kept here rather than delegating to Corpus.search because what this tool prints is the
    CONTEXT - a Pali page is far too long to read whole, and a hit without its surroundings
    cannot be judged.
    """
    rx = re.compile(pattern, re.I)
    hits = []
    for p in pages:
        hay = p.text + (" " + p.notes if notes else "")
        m = rx.search(hay)
        if m:
            lo, hi = max(0, m.start() - 110), m.end() + 170
            hits.append((p, hay[lo:hi]))
    return hits


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pattern")
    ap.add_argument("--corpus", choices=sorted(COLLECTIONS), default="dn")
    ap.add_argument("--notes", action="store_true",
                    help="search the PTS footnotes too; off by default, because they are the "
                         "editors' words and counting them as text manufactures evidence")
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    corpus = PALI[args.corpus]
    pages = load(args.corpus)
    hits = search(pages, args.pattern, notes=args.notes)
    print(f"pattern {args.pattern!r} over {len(pages)} PTS pages of "
          f"{COLLECTIONS[args.corpus][0]}"
          f"{' including footnotes' if args.notes else ''}: {len(hits)} page(s)\n")
    if not hits:
        print("  MEASURED SILENCE - re-runnable by anyone with the same PTS files")
        return
    for p, ctx in hits[:args.limit]:
        print(f"  {corpus.locus(p)}: ...{ctx}...\n")
    if len(hits) > args.limit:
        print(f"  ... {len(hits) - args.limit} more")


if __name__ == "__main__":
    main()
