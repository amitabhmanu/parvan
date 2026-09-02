"""The BORI apparatus as a labelled lateness set.

    uv run python tools/apparatus.py            # calibration and the metric test
    uv run python tools/apparatus.py --discover # what the apparatus is enriched in

The critical editors of the Mahabharata marked, passage by passage and on manuscript
evidence, which lines they judged non-archetypal. That is 66,177 lines - 28% of the
transmitted text - carrying a per-passage label of RELATIVE LATENESS, in the same work, the
same genre, the same language and the same transmission as the constituted text.

Nothing else available to this project controls that tightly. Every external comparison the
store makes - Vedic against epic, epic against Kalidasa - varies genre, register, subject and
centuries all at once. This one varies date and almost nothing else.

Its limit, and it is a real one: the archetype is not the original. It is the reconstructed
common ancestor of the surviving manuscripts, itself already a late redaction. So this
measures accretion AFTER the archetype, not the whole history of the text. A term can be late
in absolute time and still sit in the constituted text, because the constituted text is late.
"""

from __future__ import annotations

import argparse
import collections
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import concordance as C  # noqa: E402

WORD = re.compile(r"[|/\d\[\]()*@_,.-]")

# Referents with independent external dates, used to check whether apparatus enrichment
# tracks lateness at all before it is trusted to discover anything.
CALIBRATION = [
    ("dinara (Roman aureus, 1c CE+)", "dīnār"),
    ("pustaka (book)", "pustak"),
    ("temple (devalaya / mandira)", "devālay|mandir"),
    ("moksa vocabulary", "punarjanman|saṃsāra|apunarbhava|mumukṣu|mokṣadharma|apavarg|kaivalya"),
    ("avatara", "avatār"),
    # sthUNa, 'pillar', contains hUN and floods this search if it is not excluded. The same
    # compounding trap the concordance docstring warns about, in a new place.
    ("Huna (excluding sthUNa)", r"(?<!st)hūṇ"),
    ("Yavana", "yavan"),
    ("horse-chariot (ratha + haya)", "hayair yukt"),
]


def words(verses) -> list[str]:
    out: list[str] = []
    for v in verses:
        out += [w for w in WORD.sub(" ", v.text).split() if w]
    return out


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--discover", action="store_true",
                    help="rank vocabulary by log-odds enrichment instead of testing known terms")
    ap.add_argument("--min-count", type=int, default=40)
    args = ap.parse_args()

    mbh = C.load_mbh()
    arch = [v for v in mbh if v.archetypal]
    app = [v for v in mbh if not v.archetypal]
    wa, wp = words(arch), words(app)
    print(f"archetypal {len(arch):>7,} lines  {len(wa):>9,} words")
    print(f"apparatus  {len(app):>7,} lines  {len(wp):>9,} words  "
          f"({100 * len(wp) / (len(wa) + len(wp)):.1f}% of the transmitted text)\n")

    if not args.discover:
        print("CALIBRATION - does apparatus enrichment track known lateness?\n")
        print(f"  {'referent':34s}{'arch/10k':>10}{'app/10k':>10}{'enrichment':>12}")
        for label, pat in CALIBRATION:
            a = 1e4 * len(C.search(arch, pat)) / len(wa)
            p = 1e4 * len(C.search(app, pat)) / len(wp)
            ratio = f"{p / a:.1f}x" if a else ("only in apparatus" if p else "absent")
            print(f"  {label:34s}{a:>10.3f}{p:>10.3f}{ratio:>12}")
        print("\nTHE METRIC TEST - do the linguistic dating metrics track the same label?\n")
        import aspect as ASP  # noqa: PLC0415
        import subjunctive as SUB  # noqa: PLC0415
        TAG = re.compile(r"\S+\s+uvāca")
        rows = {}
        for name, vs in (("archetypal", arch), ("apparatus", app)):
            ws = [w for v in vs if not TAG.fullmatch(v.text.strip())
                  for w in WORD.sub(" ", v.text).split() if w]
            c = collections.Counter(ws)
            perf, impf = c["uvāca"] + c["ūcuḥ"], c["abravīt"] + c["abruvan"]
            ppp = sum(1 for i, w in enumerate(ws[:-3])
                      if w in ASP.AGENTS and any(ASP.PPP.search(x) for x in ws[i + 1:i + 4]))
            aor = sum(1 for w in ws if w.endswith("īt")
                      and not w.endswith("āsīt") and not w.endswith("bravīt"))
            _ind, sub = SUB.measure(ws)
            rows[name] = (perf / impf if impf else 0, 1e4 * ppp / len(ws),
                          1e4 * aor / len(ws), sum(sub.values()),
                          sum(len(w) for w in ws) / len(ws))
        labels = ("perfect/imperfect ratio", "PPP-predicate /10k", "aorist /10k",
                  "thematic subjunctives", "mean word length")
        print(f"  {'metric':28s}{'archetypal':>12}{'apparatus':>12}{'shift':>9}")
        for i, lab in enumerate(labels):
            a, p = rows["archetypal"][i], rows["apparatus"][i]
            sh = f"{p / a:.2f}x" if a else "-"
            print(f"  {lab:28s}{a:>12.2f}{p:>12.2f}{sh:>9}")
        print("\n  Lexical markers move by 15x and more. Every linguistic metric is flat.")
        print("  Interpolators wrote epic Sanskrit on purpose, so grammar does not separate")
        print("  epic from epic-plus-centuries even where content plainly does.")
        return

    # --- discovery: log-odds with an uninformative Dirichlet prior (Monroe et al.) --------
    A, P = collections.Counter(w for w in wa if len(w) > 2), collections.Counter(
        w for w in wp if len(w) > 2)
    na, np_ = sum(A.values()), sum(P.values())
    a0, V = 0.5, len(set(A) | set(P))
    rows_d = []
    for w in set(A) | set(P):
        ca, cp = A[w], P[w]
        if ca + cp < args.min_count:
            continue
        la = math.log((ca + a0) / (na + a0 * V - ca - a0))
        lp = math.log((cp + a0) / (np_ + a0 * V - cp - a0))
        rows_d.append(((lp - la) / math.sqrt(1 / (ca + a0) + 1 / (cp + a0)), w, ca, cp))
    rows_d.sort(reverse=True)
    print("MOST ENRICHED IN THE APPARATUS")
    for z, w, ca, cp in rows_d[:25]:
        print(f"  {z:6.1f}  {w:22s}{ca:>7}{cp:>6}")
    print("\nMOST ENRICHED IN THE CONSTITUTED TEXT")
    for z, w, ca, cp in rows_d[-15:][::-1]:
        print(f"  {z:6.1f}  {w:22s}{ca:>7}{cp:>6}")


if __name__ == "__main__":
    main()
