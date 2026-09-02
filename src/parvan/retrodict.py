"""V-2 retrodiction: hold out an anchor, rebuild, and see whether the network recovers it.

The protocol is fixed by `docs/preregistration.md`, frozen in Phase 1 before a solver existed.
Nothing here may be tuned to improve the outcome - that is the whole point of having written
it down first, and the document the project derives from diagnoses exactly this failure in
astronomical dating: "every researcher discards a subset, chosen after the target date is in
view."

Holding out an anchor means erasing its declared interval while leaving the node and all its
edges in place, then asking what the rest of the network can say about its date.
"""

from __future__ import annotations

from dataclasses import dataclass

from .loader import Store, load
from .model import Interval
from .stp import INF, Bounds, date_var, solve

# --- thresholds, from the preregistration. Do not edit to accommodate a result. -------
PASS_YEARS = 150
WEAK_YEARS = 300
MAX_WIDTH = 800          # wider than this is not recovery, however well it contains the truth
MIN_PASS_RATE = 0.40
MIN_PASS_OR_WEAK = 0.70


@dataclass
class Retrodiction:
    anchor: str
    true_floor: int
    true_ceiling: int
    recovered: Bounds
    verdict: str
    error: float | None
    note: str = ""

    @property
    def true_mid(self) -> float:
        return (self.true_floor + self.true_ceiling) / 2


def _classify(true_lo: int, true_hi: int, got: Bounds) -> tuple[str, float | None, str]:
    if got.floor == -INF or got.ceiling == INF:
        return "FAIL", None, "unbounded - the preregistered vacuity check"
    width = got.ceiling - got.floor
    if width > MAX_WIDTH:
        return "FAIL", None, f"interval {width:.0f}y exceeds the {MAX_WIDTH}y vacuity cap"

    true_mid = (true_lo + true_hi) / 2
    got_mid = (got.floor + got.ceiling) / 2
    err = abs(got_mid - true_mid)
    contains = got.floor <= true_mid <= got.ceiling
    overlaps = got.floor <= true_hi and got.ceiling >= true_lo

    if contains and err <= PASS_YEARS:
        return "PASS", err, ""
    if overlaps and err <= WEAK_YEARS:
        return "WEAK", err, ""
    return "FAIL", err, "no overlap" if not overlaps else f"midpoint error {err:.0f}y"


def run_one(store_path: str, anchor_id: str, *, epsilon: int = 25) -> Retrodiction:
    store: Store = load(store_path)
    node = store.nodes[anchor_id]
    true_lo, true_hi = node.interval.floor, node.interval.ceiling
    node.interval = Interval()  # erase the declared date, keep every edge
    sol = solve(store, epsilon=epsilon)

    if not sol.consistent:
        return Retrodiction(anchor_id, true_lo, true_hi, Bounds(-INF, INF),
                            "FAIL", None, "store became inconsistent")

    got = sol.bounds[date_var(store, anchor_id)]
    verdict, err, note = _classify(true_lo, true_hi, got)
    return Retrodiction(anchor_id, true_lo, true_hi, got, verdict, err, note)


def run_all(store_path: str, *, epsilon: int = 25) -> tuple[list[Retrodiction], dict]:
    store = load(store_path)
    eligible = sorted(
        n.id for n in store.of_kind("anchor") if n.holdout_eligible
    )

    # Preregistration §1: the earliest and the latest anchor in the store are sacred,
    # whatever they turn out to be, because removing them lets the whole system float.
    dated = [n for n in store.of_kind("anchor") if n.interval.floor is not None]
    if dated:
        earliest = min(dated, key=lambda n: n.interval.floor).id
        latest = max(dated, key=lambda n: n.interval.ceiling).id
        eligible = [a for a in eligible if a not in (earliest, latest)]
    else:
        earliest = latest = None

    results = [run_one(store_path, a, epsilon=epsilon) for a in eligible]
    counts = {v: sum(1 for r in results if r.verdict == v) for v in ("PASS", "WEAK", "FAIL")}
    n = len(results) or 1
    summary = {
        "n": len(results),
        "counts": counts,
        "pass_rate": counts["PASS"] / n,
        "pass_or_weak_rate": (counts["PASS"] + counts["WEAK"]) / n,
        "sacred_excluded": [x for x in (earliest, latest) if x],
        "meets_v2": (counts["PASS"] / n >= MIN_PASS_RATE
                     and (counts["PASS"] + counts["WEAK"]) / n >= MIN_PASS_OR_WEAK),
    }
    return results, summary


def fmt_v2(results: list[Retrodiction], summary: dict) -> str:
    from .stp import fmt_bounds

    lines = ["V-2 retrodiction  (thresholds from docs/preregistration.md, frozen Phase 1)", ""]
    if summary["sacred_excluded"]:
        lines.append("  sacred, not held out: " + ", ".join(summary["sacred_excluded"]))
        lines.append("")
    lines.append(f"  {'anchor':<26}{'true':<24}{'recovered':<28}{'err':>7}  verdict")
    for r in results:
        true = f"[{r.true_floor}, {r.true_ceiling}]"
        err = f"{r.error:.0f}" if r.error is not None else "-"
        lines.append(f"  {r.anchor:<26}{true:<24}{fmt_bounds(r.recovered):<28}{err:>7}  "
                     f"{r.verdict}"
                     + (f"  ({r.note})" if r.note else ""))

    c = summary["counts"]
    lines += [
        "",
        f"  PASS {c['PASS']}   WEAK {c['WEAK']}   FAIL {c['FAIL']}   of {summary['n']}",
        f"  pass rate         {summary['pass_rate']:.0%}  (preregistered floor 40%)",
        f"  pass-or-weak rate {summary['pass_or_weak_rate']:.0%}  (preregistered floor 70%)",
        "",
        ("  V-2 PASSES" if summary["meets_v2"] else "  V-2 FAILS"),
    ]
    return "\n".join(lines)
