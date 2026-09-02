"""Measure the thematic subjunctive across the Atharvaveda and the two epics.

One component of the score-5 "post-Vedic, non-Paninian grammar" row, made checkable. The row
bundles six typologically distinct changes; this is the third to become attestable at locus
level, and it needed no accented text - only a Vedic baseline.

    uv run python tools/subjunctive.py
    uv run python tools/subjunctive.py --types      # every -ati type, for hand-checking

WHY A PAIRED WITHIN-STEM COUNT, AND NOT A SUFFIX SEARCH. A raw count of word-final -ati is
worthless: in the epics it is dominated by root-class presents (yati, bhati, vati, pati,
akhyati, jahati, dadati) and class-9 presents (janati, asnati, grhnati, badhnati, punati),
none of which is a subjunctive. Counting them produced an apparent 7-8 per 10,000 words in
both epics against 24.7 in the Atharvaveda, which looks like a real differential and is
entirely noise.

The subjunctive of a THEMATIC present is formed by lengthening the stem's own -a:

    bhava + ti  -> bhavati   indicative
    bhava + ti  -> bhavati with the thematic vowel long -> bhavAti   subjunctive

So counting indicative and subjunctive for the SAME stem removes every root-class and
class-9 form by construction, and the ratio is directly comparable across corpora.

3pl is excluded. Its thematic subjunctive ending -An collides with the accusative plural,
and for the commonest stem here with bhavAn, "your honour" - one of the most frequent words
in either epic.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import concordance as C  # noqa: E402

# Thematic present stems, classes 1/4/6/10. Every one ends in -a.
STEMS = (
    "bhava", "gaccha", "vada", "cara", "jīva", "pata", "naya", "vaha", "bhara", "tapa",
    "paśya", "tiṣṭha", "piba", "jaya", "viśa", "sṛja", "spṛśa", "iccha", "krīḍa", "śoca",
    "kalpaya", "randhaya", "dhāraya", "kāraya", "nāśaya", "vardhaya", "bodhaya", "yaja",
)
SLOTS = (("ti", "3sg"), ("si", "2sg"), ("tha", "2pl"))

# The 1sg the subjunctive kept by being reassigned to the imperative paradigm. Its presence
# in the epics is the positive control: it shows the search can see the category, so a zero
# in the other persons is a property of the text rather than of the instrument. Without a
# control an absence is not evidence - the lesson the Pataliputra row taught this project.
CONTROL = ("karavāṇi", "dadāni", "bravāṇi", "karavāva", "karavāma")

WORD_SPLIT = re.compile(r"[|/\d\[\]()*@_,.-]")


def words(verses) -> list[str]:
    out: list[str] = []
    for v in verses:
        text = C.av_fold(v.text) if v.work == "AVS" else v.text
        out += [w for w in WORD_SPLIT.sub(" ", text).split() if w]
    return out


def corpora() -> dict[str, list[str]]:
    return {
        "AVS": words(C.load_av()),
        "Ram core": words([v for v in C.load() if 2 <= v.kanda <= 6]),
        "MBh arch": words([v for v in C.load_mbh() if v.archetypal]),
    }


def measure(ws: list[str]) -> tuple[int, collections.Counter]:
    cnt = collections.Counter(ws)
    indicative = 0
    subjunctive: collections.Counter = collections.Counter()
    for stem in STEMS:
        for ending, _person in SLOTS:
            indicative += cnt[stem + ending]
            subj = stem[:-1] + "ā" + ending
            if cnt[subj]:
                subjunctive[subj] += cnt[subj]
    return indicative, subjunctive


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--types", action="store_true",
                    help="list every word-final -ati type per corpus, for hand-checking the zero")
    args = ap.parse_args()

    corp = corpora()

    print(f"{'corpus':10s} {'words':>10s} {'indicative':>11s} {'subjunctive':>12s} {'subj share':>11s}")
    results = {}
    for name, ws in corp.items():
        ind, sub = measure(ws)
        results[name] = (ind, sub)
        total = ind + sum(sub.values())
        share = 100 * sum(sub.values()) / total if total else 0.0
        print(f"{name:10s} {len(ws):>10,} {ind:>11,} {sum(sub.values()):>12,} {share:>10.2f}%")

    print("\nsubjunctive forms:")
    for name, (_ind, sub) in results.items():
        forms = ", ".join(f"{w}×{n}" for w, n in sub.most_common())
        print(f"  {name:10s} {forms or '- none -'}")

    print("\npositive control - the 1sg the subjunctive kept, reassigned to the imperative:")
    for name, ws in corp.items():
        cnt = collections.Counter(ws)
        hits = {w: cnt[w] for w in CONTROL if cnt[w]}
        print(f"  {name:10s} {hits or '- none -'}")

    # What a zero costs, stated as an expectation rather than a shrug.
    av_ind, av_sub = results["AVS"]
    rate = sum(av_sub.values()) / (av_ind + sum(av_sub.values()))
    print("\nexpected subjunctives in each epic at the Atharvaveda's rate:")
    for name in ("Ram core", "MBh arch"):
        ind, sub = results[name]
        print(f"  {name:10s} {rate * ind / (1 - rate):>8.0f} expected, {sum(sub.values())} observed")

    if args.types:
        for name, ws in corp.items():
            types = sorted({w for w in ws if w.endswith("āti")})
            print(f"\nword-final -ati types in {name} ({len(types)}):")
            print("  " + ", ".join(types))


if __name__ == "__main__":
    main()
