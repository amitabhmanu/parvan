"""Concordance over the Digha-Nikaya (PTS text via GRETIL), for cross-tradition checks.

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
apparatus. Everything below a page's rule line is editorial and is held separately.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "corpus" / "pali"
# PTS volume order. The Vinaya's is Oldenberg's: Mahavagga, Cullavagga, the two halves of
# the Suttavibhanga, Parivara - so "Vin iii.21" is a Suttavibhanga page, not a Mahavagga one.
COLLECTIONS = {
    "dn": ("Digha-Nikaya", "DN",
           [("dighn1ou", "i"), ("dighn2ou", "ii"), ("dighn3ou", "iii")]),
    "vin": ("Vinaya-Pitaka", "Vin",
            [("vin1maou", "i"), ("vin2cuou", "ii"), ("vin3s1ou", "iii"),
             ("vin4s2ou", "iv"), ("vin5paou", "v")]),
}
PAGE = re.compile(r"\[page (\d+)\]")
# A run of hyphens separates the text of a PTS page from its footnotes.
RULE = re.compile(r"-{20,}")


@dataclass(frozen=True)
class Page:
    vol: str
    page: int
    text: str
    notes: str
    sigil: str = "DN"

    @property
    def locus(self) -> str:
        return f"{self.sigil} {self.vol}.{self.page}"


def load(collection: str = "dn", directory: Path = ROOT) -> list[Page]:
    if collection not in COLLECTIONS:
        sys.exit(f"unknown collection {collection!r}; choose from {sorted(COLLECTIONS)}")
    heading, sigil, files = COLLECTIONS[collection]
    if not directory.exists():
        sys.exit(f"Pali corpus not found at {directory}; see docs/corpus-audit.md")
    out: list[Page] = []
    for stem, vol in files:
        path = directory / f"{stem}.htm"
        if not path.exists():
            sys.exit(f"missing {path}: fetch the ANNOTATED (ou) files, not the plain ones - "
                     "the plain version strips the page references that make a locus citable")
        raw = path.read_text(encoding="utf-8", errors="replace")
        start = raw.find(heading)
        if start < 0:
            sys.exit(f"{path}: heading {heading!r} not found; the file layout has changed")
        body = re.sub(r"<[^>]+>", " ", raw[start:])
        parts = PAGE.split(body)
        if len(parts) < 3:
            sys.exit(f"{path}: no [page N] markers found; loci would be uncitable")
        for i in range(1, len(parts), 2):
            chunk = re.sub(r"\s+", " ", parts[i + 1])
            split = RULE.split(chunk, maxsplit=1)
            out.append(Page(vol, int(parts[i]), split[0],
                            split[1] if len(split) > 1 else "", sigil))
    return out


def search(pages: list[Page], pattern: str, *, notes: bool = False) -> list[tuple[Page, str]]:
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

    pages = load(args.corpus)
    hits = search(pages, args.pattern, notes=args.notes)
    print(f"pattern {args.pattern!r} over {len(pages)} PTS pages of "
          f"{COLLECTIONS[args.corpus][0]}"
          f"{' including footnotes' if args.notes else ''}: {len(hits)} page(s)\n")
    if not hits:
        print("  MEASURED SILENCE - re-runnable by anyone with the same PTS files")
        return
    for p, ctx in hits[:args.limit]:
        print(f"  {p.locus}: ...{ctx}...\n")
    if len(hits) > args.limit:
        print(f"  ... {len(hits) - args.limit} more")


if __name__ == "__main__":
    main()
