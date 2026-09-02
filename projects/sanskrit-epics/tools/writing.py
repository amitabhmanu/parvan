"""The writing horizon: what a text does when it has no writing.

    uv run python tools/writing.py

An absence claim is only as good as its control, and this one has an unusually strong one:
the Ramayana core does not merely lack writing, it visibly does something ELSE in the slot a
literate culture fills with a document.

The argument has three parts, and the tool prints all three so each can be checked:

1. VOCABULARY. No lipi, no pustaka, no written or sealed message anywhere in Ram.2-6.
2. SEMANTICS. The root LIKH is present eleven times and never means 'write'. Ten of the
   eleven are one formula - peaks and palaces scraping the sky - and the eleventh is beasts
   scoring each other with fangs. The Mahabharata archetype has reached the next sense along,
   'draw' (citre likhaty asvan, pratimas calikhanty anye); the Ramayana core has not.
3. CONTROL. The core has 25 duta episodes and 18 uses of abhijnana, 'recognition token'. Its
   central authentication problem - proving a messenger genuine to a captive behind enemy
   lines - is solved with a signet ring marked with Rama's name, answered with a crest jewel.
   Objects carrying a personal name exist; writing does not.

The comparison row matters as much as the Ramayana row. Later layers of the SAME tradition
acquire the vocabulary - pustaka appears in the Mahabharata apparatus and nowhere else - so
the silence is not something the genre imposes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import concordance as C  # noqa: E402

# samudra, 'ocean', contains mudra and swamps a search for seals if it is not excluded.
PATTERNS = [
    ("writing", [("lipi (script)", "lipi"), ("pustaka (book)", "pustak"),
                 ("lekhya (document / painting)", "lekhya"),
                 ("mudra (seal), not samudra", r"(?<!sa)(?<!sā)mudrā")]),
    ("the occasion for it", [("duta (messenger)", "dūta"),
                             ("abhijnana (recognition token)", "abhijñān"),
                             ("anguliya (signet ring)", "aṅgulīya"),
                             ("cudamani (crest jewel)", "cūḍāmaṇi")]),
    ("coinage, for comparison", [("karsapana (punch-marked)", "kārṣāpaṇ"),
                                 ("dinara (Roman)", "dīnār")]),
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ram, mbh = C.load(), C.load_mbh()
    sets = {
        "Ram core 2-6": [v for v in ram if 2 <= v.kanda <= 6],
        "Ram 1+7": [v for v in ram if v.kanda in (1, 7)],
        "MBh arch": [v for v in mbh if v.archetypal],
        "MBh appar": [v for v in mbh if not v.archetypal],
        "Raghuvamsa": [v for v in C.load_ragh() if v.archetypal],
    }
    print(f"{'':32s}" + "".join(f"{k:>13s}" for k in sets))
    for heading, group in PATTERNS:
        print(f"\n{heading.upper()}")
        for label, pat in group:
            print(f"  {label:30s}" + "".join(f"{len(C.search(v, pat)):>13}" for v in sets.values()))

    core = sets["Ram core 2-6"]
    print("\n\nEVERY occurrence of the root LIKH in the Ramayana core, for reading:")
    for v in C.search(core, "likh"):
        print(f"  {v.locus}  {v.text[:98]}")
    print("\nThe same root in the Mahabharata archetype, where it has reached 'draw':")
    for v in C.search(sets["MBh arch"], r"likhaty|cālikhanty"):
        print(f"  {v.locus}  {v.text[:98]}")
    print("\nWhat is carried instead of a letter:")
    for pat in ("aṅgulīya", "cūḍāmaṇi"):
        for v in C.search(core, pat)[:2]:
            print(f"  {v.locus}  {v.text[:98]}")


if __name__ == "__main__":
    main()
