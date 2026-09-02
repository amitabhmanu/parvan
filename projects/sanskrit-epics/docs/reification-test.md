# Does reification pay? The two-text test

The design's central bet is that making referents into nodes lets evidence cross between texts.
Adding the Mahābhārata to a Rāmāyaṇa-only store is the direct test.

**Result: it pays in connection, not in robustness.** Both texts' ceilings now run through one
shared referent — but through the *same* declared value, so the minimum cut is still 1.

§2 below originally claimed redundancy. It was measured with leave-one-out, the instrument §3
identifies as broken, and §2a corrects it. The corrected finding is weaker and more useful.

Store: 76 nodes, 94 edges, both inventories.

---

## 1. Tightening: none, as predicted

| | Rāmāyaṇa only | Both texts |
|---|---|---|
| `ram.core` | [750 BCE, 300 BCE] | **[750 BCE, 300 BCE]** |

Of eight shared referents, exactly one moved — `ref.classical-kavya-style`, whose floor went
from 750 BCE to 500 BCE, and which binds nothing.

This is the order-statistics argument holding: a referent's bound is set by its **extreme**
attester, so a second text changes it only by supplying a new extreme. The Mahābhārata supplied
none for the referents the Rāmāyaṇa depends on. Tightening scales as `log T`, and this is what
`log T` looks like at T = 2.

## 2. Redundancy: real, and I was wrong

`ram.core`'s ceiling had exactly one route before. It now has two.

```
drop e.043 (Rām lacks Pāṭaliputra)   ram.core = [750 BCE, 300 BCE]   unchanged
drop e.107 (MBh lacks Pāṭaliputra)   ram.core = [750 BCE, 300 BCE]   unchanged
drop BOTH                            ram.core = [750 BCE, 250 CE]    550-year swing
```

Either alone suffices. The second route is a three-hop chain through two shared referents,
crossing between the epics twice:

```
  MBh heroic narrative names no Pāṭaliputra
        └─ e.107 ─→  MBh heroic ≤ 300 BCE
              └─ e.035 ─→  the Bhārata war narrative existed by then
                    └─ e.042 ─→  Rāmāyaṇa core names no Pāṇḍavas, so ≤ 300 BCE
```

The Rāmāyaṇa's ceiling is now underwritten by the Mahābhārata's silence about a city.

**A slack edge became binding.** §12 scores "Rāmāyaṇa never mentions the Pāṇḍavas" a 3 and
flags it as an argument from silence. In the single-text store it moved nothing. With a second
text present it is load-bearing — one of three edges on the alternate path.

That is the reification thesis demonstrated rather than argued: **the value of a constraint is
not a property of the constraint. It is a property of the graph it sits in.** No scoring scheme
applied to §12 in isolation could have predicted that this row would matter.

It is also §14's convergence argument made concrete — multiple disjoint paths, from different
anchors, arriving at the same bound.

## 2a. CORRECTION — measured again with the right instrument, §2 is wrong

§2 was written with leave-one-out, the instrument §3 goes on to identify as broken. That was
careless, and the corrected measurement inverts the conclusion.

`parvan support` counts edge-disjoint routes, so the number it reports is the minimum cut —
how many constraints must fail *together* before a bound moves.

```
ram.core   [750 BCE, 300 BCE]
  floor    cut 1   e.009  ram.core presupposes ref.kosala-power
                   ref.kosala-power           emergence floor -750
  ceiling  cut 1   ref.pataliputra-imperial   emergence ceiling -300
                   e.043  ref.pataliputra-imperial absent from ram.core

ws.mbh.core  [500 BCE, 300 BCE]
  ceiling  cut 1   ref.pataliputra-imperial   emergence ceiling -300
                   e.107  ref.pataliputra-imperial absent from ws.mbh.core
```

**Every bound in the store has a minimum cut of 1.** Not one is redundantly supported.

The two Pāṭaliputra routes are real — either absence edge suffices, as §2 shows — but they
**share their terminus**. Both end at one declared number, `ref.pataliputra-imperial`'s
emergence ceiling of −300 BCE. Remove that and both routes die together. So the redundancy is
at the level of *edges*, not of *evidence*: the Rāmāyaṇa and the Mahābhārata now hang their
ceilings on the same single value.

That is a weaker and more useful result than the one §2 claimed. Reification did connect the
two texts; it did not make either bound robust.

### The defect underneath: the anchors are decorative

```
drop hor.mauryan-capital (the anchor)   ram.core = [750 BCE, 300 BCE]   unchanged
```

Deleting the archaeological horizon changes nothing, because the referent's emergence was
**declared** in the encoder rather than derived from the horizon that attests it. The same is
true of every material referent: `hor.iron-india`, `hor.horse-chariot`, `hor.ayodhya-urban`,
`hor.kosala-power` and the rest are all inert. Thirteen horizon nodes, contributing nothing.

This is the Vāsudeva error again in a form that does not announce itself. There it produced a
negative cycle and got caught in one reading. Here it produces a *consistent* network whose
anchors are ornamental, and only a cut analysis reveals it.

It also falsifies, for this store, §14's claim that "anchors carry the whole system". They
carry nothing. What carries the system is about six numbers typed into
`tools/encode_inventory.py`, each with `attested` provenance pointing at an excavation report
nobody has opened.

**Fixed.** A seventh edge type, `grounds`, supplies the floor that `attests` cannot, and G-7
restricts it to material node kinds. Every material referent now derives its emergence from a
horizon instead of declaring one, and the anchors bind:

```
drop hor.mauryan-capital   ram.core    [750 BCE, 300 BCE] -> [750 BCE, 250 CE]
                           ws.mbh.core [500 BCE, 300 BCE] -> [500 BCE, 299 CE]
drop hor.kosala-power      ram.core    [750 BCE, 300 BCE] -> [1300 BCE, 300 BCE]
drop hor.massed-elephants  ws.mbh.core [500 BCE, 300 BCE] -> [750 BCE, 300 BCE]
```

The brackets are unchanged, which is the point: the same numbers, now derived from cited
horizons rather than typed into the encoder. Cuts remain 1, but the single point of failure is
now a named archaeological horizon rather than an invisible constant.

The change also exposed a second error. Grounding pins emergence to the horizon's interval, so
a horizon must express an **onset window**, not a duration. `hor.mauryan-capital` had been
encoded as the imperial phase [-320, -180], which made the absence argument yield "predates
180 BCE" — the date Pāṭaliputra stopped being unremarkable to omit, which is not the claim.
Corrected to the accession window. Every other horizon was already an onset window; this was
the only one, and only deriving rather than declaring made it visible.

## 3. A limitation this exposed in `parvan influence`

Leave-one-out reported `BINDING 1` for `ram.core` after the Mahābhārata was added — *fewer*
than the 2 it reported before, even though the evidence had strictly grown.

That is not a bug in the network, it is a blind spot in the measurement. **Leave-one-out cannot
see a redundant pair:** remove either edge of a two-route bound and nothing moves, so both
report as slack. The effect is perverse — the better-supported a bound is, the less important
its supports appear.

The honest instrument is a **minimum cut**: the smallest set of edges whose joint removal moves
the bound. That is what "how well supported is this?" actually asks. Leave-one-out answers it
only when support is a single point of failure, which is the case it is least needed for.

Recorded as a defect. `influence` should report cut size, not per-edge deltas.

## 4. What the Mahābhārata's own brackets came out at

Encoded from §11 and not tuned:

| Stratum | Bracket | Set by |
|---|---|---|
| Heroic narrative | **[500 BCE, 300 BCE]** | massed elephant corps · Pāṭaliputra silence |
| Anthology layer | [475 BCE, unbounded] | frames the heroic narrative |
| Theological layer | [475 BCE, unbounded] | frames the heroic narrative |
| Didactic mass | **[150 CE, 450 CE]** | Greek astrological loans · unsystematized Sāṃkhya |
| Late peoples lists | [450 CE, unbounded] | the Hūṇa floor |

The didactic bracket is the interesting one: floored by Greek-derived astrological vocabulary
and ceilinged by the absence of classical Sāṃkhya, it reproduces §11's reasoning without being
told the answer. The Hūṇa floor at 450 CE is the document's "latest binding floor", and it
lands where the document says.

## 5. The error the network caught — R-10's first real firing

The first combined solve was **inconsistent**, with this witness:

```
ref.vasudeva-arjuna-cult#emergence -> __origin__   w=+190   emergence floor -190
__origin__ -> ws.panini                            w=-330   Pāṇini ceiling -330
ws.panini -> ref.vasudeva-arjuna-cult#emergence    w=+0     [e.128] Pāṇini attests the cult
cycle weight = -140
```

I had pinned the cult's emergence to the Agathocles coins at [190, 180] BCE. Pāṇini attests the
same cult 150 years earlier. Two faults, one on top of the other:

1. **R-4 violated by my own hand** — I let an attestation *floor* an emergence when it can only
   cap it from above. Exactly the invariant the loader enforces on referent records, evaded by
   declaring the interval directly.
2. **Conflation**, which was the deeper fault. §11 already keeps these apart: Pāṇini bounds
   "the cult pairing", the coins bound "the divine pair **with epic attributes**". One node,
   two dates.

The fix is R-10's split operator, applied for the first time on a real contradiction rather
than a fixture. `ref.vasudeva-arjuna-cult` and `ref.vasudeva-epic-attributes` are now separate,
and the store is consistent.

Worth noting what this cost to find: nothing. The witness named all three constraints, and the
diagnosis took one reading.

---

## 6. Verdict

| Prediction | Outcome |
|---|---|
| Tightening scales as log T; a second text moves little | **Confirmed** — one non-binding referent moved |
| Redundancy is where corpus growth pays | **Not shown.** Two routes, one shared terminus, minimum cut still 1 |
| Inconsistency detection does real work | **Confirmed** — caught a conflation I introduced |

What a second text bought was a *connection* between the epics, not a robust bound. Every
bound in the store remains a single point of failure, and the anchors that were supposed to
fix absolute time turn out to be inert.

The honest summary is that Phase 4 found two defects in the model and one in the measurement,
and that this is worth more than the confirmation it was looking for.
