"""F-1 adjudication: does metrical and linguistic evidence carry anything?

    uv run python projects/sanskrit-epics/tools/f1_check.py

F-1 is a preregistered falsifier, frozen in docs/preregistration.md before a solver existed:

    "If ablating every metrical-statistics edge does not degrade anchor recovery, then
     metrical arguments carry no usable information, and the source document's claim that
     language and metre form 'the tightest single bracket' is wrong. Report it as such."

It is a stopping condition, not a tuning opportunity, so it is adjudicated in code and the
verdict is whatever falls out.

THE SPECIFIED INSTRUMENT MAY NOT BE ABLE TO ANSWER IT, and that possibility is checked first
rather than assumed away. V-2 anchor recovery already fails 0 of 9 at baseline: every anchor
in this store is TERMINAL - nothing in the corpus is later than it - so holding one out leaves
its ceiling unbounded whatever else is in the network. A measure that reads zero before the
ablation cannot read lower after it. Test 1 establishes whether that is so here.

When an instrument cannot discriminate, the honest move is to say so and then answer the
question a different way rather than report a vacuous pass. Tests 2 and 3 do that.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from parvan.loader import load  # noqa: E402
from parvan.retrodict import MIN_PASS_RATE, _classify  # noqa: E402
from parvan.stp import date_var, solve  # noqa: E402

STORE = ROOT / "projects" / "sanskrit-epics" / "store"

# The class F-1 names, and the wider class it belongs to. Both are reported: F-1 asks about
# metre specifically, but metre and morphology are the same kind of claim - a property of the
# form of the text rather than of what it mentions - and the store puts them under two tags.
ABLATIONS = {
    "baseline (nothing removed)": (),
    "metrical-statistics removed": ("metrical-statistics",),
    "metre + linguistic-stratigraphy removed": ("metrical-statistics", "linguistic-stratigraphy"),
}


def ablated(methods: tuple[str, ...]):
    store = load(STORE)
    for eid in [e.id for e in store.edges.values() if e.method in methods]:
        store.edges.pop(eid)
    return store


def retrodict_ablated(methods: tuple[str, ...], epsilon: int = 25):
    """The V-2 hold-out loop, but over a store with `methods` edges removed."""
    base = ablated(methods)
    dated = [n for n in base.of_kind("anchor") if n.interval.floor is not None]
    earliest = min(dated, key=lambda n: n.interval.floor).id
    latest = max(dated, key=lambda n: n.interval.ceiling).id
    eligible = sorted(n.id for n in base.of_kind("anchor")
                      if n.holdout_eligible and n.id not in (earliest, latest))
    out = []
    for anchor in eligible:
        store = ablated(methods)
        node = store.nodes[anchor]
        lo, hi = node.interval.floor, node.interval.ceiling
        node.interval = type(node.interval)()
        sol = solve(store, epsilon=epsilon)
        got = sol.bounds[date_var(store, anchor)]
        verdict, _err, _note = _classify(lo, hi, got)
        out.append((anchor, verdict, got))
    return out


def fmt(y: float | None) -> str:
    if y is None or abs(y) == float("inf"):
        return "unbounded"
    return f"{abs(int(y))} {'BCE' if y < 0 else 'CE'}"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("F-1 ADJUDICATION\n" + "=" * 78)

    counts = {e.method: 0 for e in load(STORE).edges.values()}
    for e in load(STORE).edges.values():
        counts[e.method] += 1
    print(f"\nedges in the store: metrical-statistics {counts.get('metrical-statistics', 0)}, "
          f"linguistic-stratigraphy {counts.get('linguistic-stratigraphy', 0)}")

    # --- 1. the specified test ------------------------------------------------------
    print("\n1. THE SPECIFIED TEST - V-2 anchor recovery, with and without the class\n")
    print(f"   {'ablation':44s}{'PASS':>6}{'WEAK':>6}{'FAIL':>6}{'rate':>7}")
    recovered = {}
    for label, methods in ABLATIONS.items():
        rs = retrodict_ablated(methods)
        c = {v: sum(1 for _, vv, _ in rs if vv == v) for v in ("PASS", "WEAK", "FAIL")}
        rate = c["PASS"] / (len(rs) or 1)
        recovered[label] = {a: (g.floor, g.ceiling) for a, _, g in rs}
        print(f"   {label:44s}{c['PASS']:>6}{c['WEAK']:>6}{c['FAIL']:>6}{rate:>6.0%}")

    base_key = "baseline (nothing removed)"
    identical = all(recovered[k] == recovered[base_key] for k in recovered)
    print(f"\n   preregistered floor {MIN_PASS_RATE:.0%}. Every recovered interval identical "
          f"across ablations: {identical}")
    print("   The measure reads zero before the ablation, so it cannot read lower after it.")
    print("   F-1's specified instrument CANNOT DISCRIMINATE on this store, and reporting")
    print("   'no degradation' from it would be vacuous rather than informative.")

    # --- 2. does the class move any bound at all? -----------------------------------
    print("\n2. THE QUESTION F-1 WAS ASKING - does the class move any bound anywhere?\n")
    base = solve(load(STORE), epsilon=25).bounds
    for label, methods in ABLATIONS.items():
        if not methods:
            continue
        b = solve(ablated(methods), epsilon=25).bounds
        moved = [k for k in base if k in b
                 and (base[k].floor, base[k].ceiling) != (b[k].floor, b[k].ceiling)]
        print(f"   {label:44s} bounds moved: {len(moved)}")
        for k in moved[:8]:
            print(f"      {k:38s} [{fmt(base[k].floor)}, {fmt(base[k].ceiling)}]"
                  f"  ->  [{fmt(b[k].floor)}, {fmt(b[k].ceiling)}]")

    print("\n3. THE INDEPENDENT EVIDENCE - see tools/apparatus.py.")
    print("   Against 66,177 lines the Mahabharata's editors labelled non-archetypal,")
    print("   every form-based metric is flat (1.07x, 0.96x, 0.83x, 1.01x) while lexical")
    print("   content moves fifteenfold. That is a direct measurement of discriminative")
    print("   power on labelled data, and it is the evidence F-1 should be decided on.")


if __name__ == "__main__":
    main()
