"""Compound-length distribution over the GRETIL Ramayana, per kanda.

Section 5 of the source synthesis makes a measurable claim: "Epic compounds run to a few
members; mature classical kavya (Bana, Dandin, 6th-7th c.) piles up ten or fifteen. The epics
never do this." That is a statistic, not an opinion, and the critical edition is machine
readable, so it can be checked rather than cited.

In IAST a Sanskrit compound is written as one orthographic word, so token length in characters
is a serviceable proxy for compound size. It is a proxy and not a count of members - a long
word could be one long stem - so the tail matters more than the mean: a 30-character token is
a multi-member compound whatever else it is.

    uv run python tools/compounds.py
    uv run python tools/compounds.py --threshold 25 --examples 5

What this can and cannot establish is set out at the bottom of the output.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "corpus" / "sa_rAmAyaNa.xml"
VERSE_RE = re.compile(r'<lg xml:id="R_(\d+)\.(\d+)\.(\d+)">(.*?)</lg>', re.S)
LINE_RE = re.compile(r'<l xml:id="[^"]*">(.*?)</l>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def tokens_by_kanda(path: Path = CORPUS) -> dict[int, list[tuple[str, str]]]:
    if not path.exists():
        sys.exit(f"corpus not found at {path}; see docs/corpus-audit.md")
    raw = path.read_text(encoding="utf-8")
    out: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for k, sg, sl, body in VERSE_RE.findall(raw):
        locus = f"Ram.{int(k)}.{int(sg):03d}.{int(sl):03d}"
        for line in LINE_RE.findall(body):
            text = TAG_RE.sub(" ", line)
            for tok in text.split():
                tok = tok.strip("/|.,;'\"()[]-")
                if tok and not tok.isdigit():
                    out[int(k)].append((unicodedata.normalize("NFC", tok), locus))
    return out


def pct(sorted_lens: list[int], p: float) -> int:
    if not sorted_lens:
        return 0
    return sorted_lens[min(len(sorted_lens) - 1, int(len(sorted_lens) * p))]


def main() -> None:
    # Windows consoles default to cp1252, which cannot encode IAST. Without this every
    # diacritic search dies on a UnicodeEncodeError instead of printing its result.
    # Reported by the extraction agent on its first run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=int, default=20,
                    help="token length counted as a long compound")
    ap.add_argument("--examples", type=int, default=3)
    args = ap.parse_args()

    data = tokens_by_kanda()
    core = {2, 3, 4, 5, 6}

    print(f"compound-length proxy: token length in IAST characters, threshold {args.threshold}\n")
    print(f"{'kanda':<8}{'tokens':>9}{'mean':>7}{'p95':>6}{'p99':>6}{'max':>6}"
          f"{'>=' + str(args.threshold):>8}{'per 1k':>9}")

    totals: dict[str, list[int]] = {"core": [], "frame": []}
    for k in sorted(data):
        lens = sorted(len(t) for t, _ in data[k])
        long_n = sum(1 for x in lens if x >= args.threshold)
        rate = 1000 * long_n / len(lens)
        print(f"  {k:<6}{len(lens):>9}{sum(lens) / len(lens):>7.2f}"
              f"{pct(lens, 0.95):>6}{pct(lens, 0.99):>6}{max(lens):>6}"
              f"{long_n:>8}{rate:>9.2f}")
        totals["core" if k in core else "frame"].extend(lens)

    print()
    for label, lens in totals.items():
        lens = sorted(lens)
        long_n = sum(1 for x in lens if x >= args.threshold)
        which = "books 2-6" if label == "core" else "books 1 and 7"
        print(f"  {label:<6} ({which:<14}) mean {sum(lens) / len(lens):.2f}  "
              f"p99 {pct(lens, 0.99)}  max {max(lens)}  "
              f"long/1k {1000 * long_n / len(lens):.2f}")

    print(f"\nlongest tokens in the corpus (>= {args.threshold} chars):")
    every = [(len(t), t, loc) for k in data for t, loc in data[k]]
    every.sort(reverse=True)
    for n, tok, loc in every[: args.examples]:
        print(f"  {n:>3}  {loc}  {tok}")

    print("""
WHAT THIS ESTABLISHES
  The Ramayana's own compound-length distribution, per kanda, reproducibly.
  It is therefore a measured internal statistic, usable as a stratification signal
  (Phase 6) and comparable across books without any external corpus.

WHAT IT DOES NOT ESTABLISH
  Section 5's claim is COMPARATIVE - that mature classical kavya piles up ten or
  fifteen members and the epics never do. The kavya half of that comparison needs
  Bana and Dandin, which are not in this corpus. Until they are, an edge asserting
  "no mature kavya style" can be attested for the epic side only, and the comparison
  itself remains `asserted`.""")


if __name__ == "__main__":
    main()
