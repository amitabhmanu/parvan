# Preregistration

**Frozen: 2026-08-31, Phase 1.** No solver existed when this was written. No solve run had
been executed. That is the point.

The source synthesis diagnoses astronomical dating as follows: *"every researcher discards a
subset, chosen after the target date is in view."* Parvan is structurally capable of the same
failure. This document is the countermeasure, and it is worthless if written later.

## Amendment rule

This file may be **added to**, never weakened. Specifically:

- A threshold may not be loosened after a run that failed it.
- A holdout may not be moved to the sacred list after it failed to be recovered.
- An ε value may not be selected because it produced a better result.
- Every amendment is a separate commit whose message states what changed and why, and it
  applies only to runs **after** that commit.

A result reported against a threshold that was loosened to accommodate it is not a result.

---

## 1. Holdout policy (G-5, V-2)

### Holdout-eligible anchors

Declared now, before any of them is encoded. When these enter the store at Phase 4 they carry
`holdout_eligible: true`.

| Anchor | Interval | Method class |
|---|---|---|
| Agathocles coins, Ai-Khanoum | c. 190–180 BCE | material (numismatic) |
| Heliodorus pillar, Besnagar | c. 115–105 BCE | documentary (epigraphic) |
| Spitzer manuscript, Kizil | c. 200–300 CE | material (palaeography) |
| *Liudu jijing*, Kang Senghui | 251 CE | foreign-documentary |
| Khoh plates of Sarvanātha | c. 500–520 CE | documentary (epigraphic) |
| Veal Kantel, Cambodia | c. 590–610 CE | documentary (epigraphic) |
| Cham inscription (Vālmīki temple) | 7th c. CE | documentary (epigraphic) |
| Aihole inscription of Pulakeśin II | 634 CE | documentary (epigraphic) |

### Sacred anchors — never held out

Removing these would let the whole system float, so a run that held them out would be testing
nothing.

- **Aśokan edicts** (c. 265–238 BCE) — the load-bearing early anchor for the entire
  concept-referent layer.
- **The earliest and the latest anchor in the store at run time**, whatever they turn out to
  be. These bound the system; without them every interval shifts together.

### Structural rule

**Every holdout run must leave at least one anchor standing in each `independence_class`
present in the store.** Holding out an entire class tests whether that class exists, not
whether the network works.

Holdouts are one-at-a-time. Leave-two-out only as a stated secondary analysis.

---

## 2. Retrodiction thresholds (V-2)

For a held-out anchor with true interval `[a, b]`, midpoint `m`, and recovered interval
`[f, c]` with midpoint `m'`:

| Outcome | Condition |
|---|---|
| **PASS** | `[f, c]` contains `m`, and `abs(m' - m) <= 150` years |
| **WEAK** | `[f, c]` overlaps `[a, b]`, and `150 < abs(m' - m) <= 300` years |
| **FAIL** | no overlap, or `abs(m' - m) > 300` years |

150 years is chosen because consensus brackets in this field run roughly 300 years wide;
recovering an anchor to within half a bracket is informative, and to within a full bracket
is not.

**Aggregate criterion for V-2:** across all single-holdout runs, **≥ 70% PASS or WEAK, with
≥ 40% PASS.** Below that, retrodiction has failed and no interval from the network is
reportable as a finding.

### Vacuity check

A run also fails if the recovered interval for a held-out anchor is **unbounded in either
direction**, or wider than 800 years. Containing the truth inside an interval that wide is
not recovery, and would otherwise let the aggregate criterion be met trivially.

---

## 3. Falsifiers (V-4)

Named outcomes that would embarrass the project. Each is a stopping condition, not a tuning
opportunity.

**F-1 · Metrical evidence carries nothing.**
If ablating every `metrical-statistics` edge does not degrade anchor recovery, then metrical
arguments carry no usable information, and the source document's claim that language and
metre form "the tightest single bracket" is wrong. Report it as such.

**F-2 · Method reliabilities do not identify.**
If the Phase 5 posteriors on method reliability are no narrower than their priors, the
calibration corpus is too thin. The hierarchical layer collapses to hand-assigned scores and
Parvan is a spreadsheet with extra steps. Say so rather than shipping the priors as results.

**F-3 · Referent posteriors conflict with archaeology.**
If referent intervals derived from the textual subgraph systematically disagree with the
material record, either the textual subgraph is contaminated or an anchor is wrong. Both
require stopping and diagnosing. Neither permits adjusting the referent priors until the
conflict goes away.

**F-4 · Seed partitions do not converge.**
If running from different published stratifications yields materially different intervals,
results are an artefact of whichever cut was loaded first. Report the divergence; report no
intervals.

**F-5 · §12 does not follow from §12.**
If V-1 fails *and* review shows the schema is not lossy, then the source document's stated
Rāmāyaṇa result does not follow from its own table. Write that up. It is a finding about the
source, not a bug in Parvan.

**F-6 · The network reports opinion, not evidence.**
Re-run with every `asserted`-tier edge removed, keeping only `attested`. **If conclusions
change materially, the network is propagating scholarly opinion rather than evidence**, and
its outputs are a summary of the literature wearing a solver's clothes. This is the
consensus-laundering failure detected from the other end, and it is the single most important
check in this document.

---

## 4. Transmission lag policy (O-1, R-5)

ε is a claim about how fast texts could cite each other, and it is not known.

- **Results are reported at ε ∈ {25, 50, 100} years, always all three.**
- Sensitivity to ε is reported as a first-class result, never suppressed.
- **No single ε may be selected because it produced a preferred outcome.** If conclusions
  depend on the choice, that dependence *is* the finding.
- ε = 0 is invalid for `cites` and `frames` edges and is refused at load (R-5), because at
  zero a chain transmits nothing and directed cycles stop reporting infeasible.

---

## 5. What counts as a trivial success

Declared so it cannot be claimed later:

- If every node's posterior equals its prior, propagation did nothing, regardless of whether
  the intervals look plausible.
- If the network reproduces the consensus using only `asserted` edges sourced from the
  scholars who formed that consensus, it has confirmed nothing (see **F-6**).
- Recovering an anchor inside an interval wider than 800 years is not recovery (§2).

---

## 6. Run record requirements (G-6)

Every reported result must be regenerable from four values, recorded automatically:

1. Store commit hash
2. Solver version
3. RNG seed
4. ε in force

A result that cannot be regenerated from those is not a result and may not be cited in any
write-up.
