"""Aspectual collapse and past-participle-as-predicate: the last two reachable components
of the score-5 "post-Vedic, non-Paninian grammar" row.

Both were written off as unreachable on the grounds that they are claims about how forms
FUNCTION across a whole text, which no single locus settles. That was wrong in the same way
the subjunctive was wrong. A function claim becomes measurable the moment it is expressed as
a RATIO against its own alternative, because the ratio cancels the confounds a raw frequency
cannot.

    uv run python tools/aspect.py

Three measurements, and one of the three does not survive its own control.

WHAT THE CONTROLS ARE FOR. Every count here is run over Kalidasa's Raghuvamsa as well as the
two epics. Kalidasa is court epic in the same genre, narrating the same dynasty as the
Ramayana, and securely dated c. 400 CE - so a metric on which Kalidasa resembles the VEDIC
text rather than the epics is not measuring date. One of the three does exactly that.

Speech-attribution lines are excluded throughout. The Mahabharata's critical edition sets
"NAME uvaca" as a verse of its own and the Ramayana's does not; counting them made the
Mahabharata look twelve times more perfect-heavy than the Ramayana, which is a fact about two
editorial conventions and nothing whatever about Sanskrit.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import concordance as C  # noqa: E402

SPEECH_TAG = re.compile(r"\S+\s+uvāca")
WORD_SPLIT = re.compile(r"[|/\d\[\]()*@_,.-]")

# Instrumental agents. The construction diagnostic of the drift toward Middle Indo-Aryan is
# an instrumental agent with a past participle as the whole predicate - tvaya daSaratho
# gunair aradhitah, "by you Dasaratha was propitiated with virtues" - which is the ancestor
# of the modern ergative.
AGENTS = frozenset(
    ("mayā", "tvayā", "tena", "tayā", "yena", "asmābhiḥ", "yuṣmābhiḥ", "bhavatā", "taiḥ", "kena")
)
# Nominative and accusative only. An oblique participle agrees with something else in the
# clause and cannot be the predicate, so -tena and -tasya must not count.
PPP = re.compile(r"t(aḥ|ā|am|āḥ|āni|au|e|a)$")


def corpora() -> dict[str, list]:
    return {
        "Atharvaveda": C.load_av(),
        "Rām core": [v for v in C.load() if 2 <= v.kanda <= 6],
        "MBh arch": [v for v in C.load_mbh() if v.archetypal],
        "Raghuvaṃśa": [v for v in C.load_ragh() if v.archetypal],
    }


def words(verses) -> list[str]:
    out: list[str] = []
    for v in verses:
        if SPEECH_TAG.fullmatch(v.text.strip()):
            continue
        text = C.av_fold(v.text) if v.work == "AVS" else v.text
        out += [w for w in WORD_SPLIT.sub(" ", text).split() if w]
    return out


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    corp = {k: words(v) for k, v in corpora().items()}

    print("A. PERFECT vs IMPERFECT of one root (√vac / √brū 'said')")
    print("   The perfect taking over plain narrative past is the collapse itself.\n")
    print(f"   {'corpus':13s}{'words':>10}{'perfect':>9}{'imperf':>8}{'ratio':>8}")
    for name, ws in corp.items():
        c = collections.Counter(ws)
        perf, impf = c["uvāca"] + c["ūcuḥ"], c["abravīt"] + c["abruvan"]
        ratio = perf / impf if impf else float("inf")
        print(f"   {name:13s}{len(ws):>10,}{perf:>9}{impf:>8}{ratio:>8.2f}")
    print("\n   Vedic 0.08 against 0.60 and 0.88 in the epics: an order of magnitude, and")
    print("   Kalidasa continues in the SAME direction. Monotone, so it survives the control.")

    print("\nB. AORIST FREQUENCY - and why it must NOT be used")
    print("   Word-final -it, excluding √as (asit is an imperfect) and √bru (abravit).\n")
    print(f"   {'corpus':13s}{'tokens':>8}{'types':>7}{'per 10k':>9}")
    for name, ws in corp.items():
        c = collections.Counter(
            w for w in ws
            if w.endswith("īt") and not w.endswith("āsīt") and not w.endswith("bravīt")
        )
        n = sum(c.values())
        print(f"   {name:13s}{n:>8}{len(c):>7}{10000 * n / len(ws):>9.2f}")
    print("\n   REFUTED AS A CLOCK. Kalidasa's rate matches the Vedic one and is 25 times the")
    print("   Ramayana's. A metric on which a 5th-century CE poet resembles the Atharvaveda")
    print("   is measuring how learned the register is, not how old the text is - the same")
    print("   confound that sank the compound-length measurement.")

    print("\nC. PAST PARTICIPLE AS PREDICATE (instrumental agent + participle)\n")
    print(f"   {'corpus':13s}{'hits':>7}{'per 10k':>9}")
    for name, ws in corp.items():
        n = sum(
            1 for i, w in enumerate(ws[:-3])
            if w in AGENTS and any(PPP.search(x) for x in ws[i + 1:i + 4])
        )
        print(f"   {name:13s}{n:>7}{10000 * n / len(ws):>9.2f}")
    print("\n   Vedic 6.2 against 14-22 across all three post-Vedic texts. It separates Vedic")
    print("   from post-Vedic cleanly and does not order anything within post-Vedic - which is")
    print("   exactly what a FLOOR claim needs and all it can support.")


if __name__ == "__main__":
    main()
