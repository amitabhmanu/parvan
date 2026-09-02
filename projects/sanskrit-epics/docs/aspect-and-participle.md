# The last two reachable components — and a withheld constraint refuted

**Date:** 2026-09-02 · **Phase:** 4 · **Status:** two encoded, one metric refuted, one
constraint permanently retired

Three measurements were run. Two survived their controls and are encoded; one did not and is
recorded as unusable. Separately, the control corpus fetched for this work settled a question
that had been left open since Phase 4: the Rāmāyaṇa's silence about liberation.

The score-5 grammar row now stands at **five of six components attested**.

---

## 0. Why these were thought unreachable, and why that was wrong

Aspectual collapse and past-participle-as-predicate were both written off as "claims about how
forms *function* across a whole text, which no locus settles." That reasoning was wrong in
exactly the way the subjunctive was wrong.

**A function claim becomes measurable the moment it is expressed as a ratio against its own
alternative**, because the ratio cancels the confounds a raw frequency cannot. The subjunctive
needed `bhavati` counted against `bhavāti`. These need the same move.

## 1. Aspectual collapse — encoded

The claim: Vedic keeps imperfect, aorist and perfect functionally distinct; epic Sanskrit
collapses them into interchangeable narrative preterites.

**Perfect against imperfect of a single root** (√vac/√brū "said", the highest-frequency
narrative verb):

```
corpus            words  perfect  imperf   ratio
Atharvaveda      85,489        1      12    0.08
Rām core        160,993      250     419    0.60
MBh arch        891,852      811     923    0.88
Raghuvaṃśa       18,418       11       2    5.50
```

The perfect is essentially unavailable for narration in the Vedic text and carries a third to
a half of it in the epics — an order of magnitude, and Kālidāsa continues in the **same**
direction, so the metric is monotone across all three dates.

**An edition artifact that had to be removed first.** The BORI Mahābhārata sets speech
attribution as a verse of its own — 5,863 verses that are nothing but `NAME uvāca` — and the
Baroda Rāmāyaṇa does not. Counting them puts the Mahābhārata at 7.23 against the Rāmāyaṇa's
0.60, a twelvefold "difference between the epics" that is entirely two editorial conventions.
Excluded, the two epics sit at 0.60 and 0.88.

## 2. Past participle as predicate — encoded

Instrumental agent plus a participle carrying the whole predicate — *tvayā daśaratho guṇair
**ārādhitaḥ***, "by you Daśaratha was propitiated with virtues" — the construction ancestral
to the Middle Indo-Aryan ergative.

```
corpus            hits   per 10k
Atharvaveda         53      6.20
Rām core           356     22.11
MBh arch         1,329     14.90
Raghuvaṃśa          26     14.12
```

**What it can and cannot do.** All three post-Vedic texts sit in a band of 14–22 while the
Vedic text sits at 6.2. It separates Vedic from post-Vedic cleanly and orders nothing within
post-Vedic — which is what a floor claim needs and all it supports. Stated in the edge so
nobody later reads more into it.

## 3. Aorist frequency — measured, and refuted as a clock

```
corpus          tokens   types   per 10k
Atharvaveda         37      16      4.33
Rām core             3       2      0.19
MBh arch           100      46      1.12
Raghuvaṃśa           9       5      4.89
```

Read the first three rows and the aorist looks like a clean clock: 4.33 in the Vedic text,
collapsing to 0.19 and 1.12 in the epics. **Then read the fourth.** A poet of c. 400 CE runs
at the Vedic rate, 25 times the Rāmāyaṇa's.

A metric on which a fifth-century author resembles the Atharvaveda is measuring **how learned
the register is, not how old the text is** — the same confound that sank the compound-length
measurement. Not encoded, and recorded here so it is not proposed again.

*(A prior trap on the same metric: word-final `-īt` is 90% `āsīt`, which is the* imperfect *of
√as, not an aorist at all, and `abravīt` is likewise an imperfect. Unfiltered, the "aorist"
count is dominated by two forms that are not aorists.)*

## 4. The *mokṣa* silence — refuted, and the constraint permanently retired

The Rāmāyaṇa core's silence about liberation was measured in Phase 4, deliberately **withheld**
for want of a positive control, and would have moved the core's ceiling from 300 BCE to
500 BCE — the largest single move available anywhere in the store.

Kālidāsa's Raghuvaṃśa was fetched to be that control. It turned out to be unnecessary, because
a far better control was already on disk: **the Rāmāyaṇa's own late books.**

```
corpus              verses    words   hits   per 10k
Rām 2-6 (core)      14,130  160,993      0      0.00
Rām 1 (Bāla)         1,941   21,711      0      0.00
Rām 7 (Uttara)       2,690   31,111      0      0.00
Mahābhārata        158,502  903,578     88      0.97
Raghuvaṃśa           1,568   18,418      3      1.63
Atharvaveda          5,839   85,489      0      0.00
```

*(punarjanman, punarbhava, apunarbhava, saṃsāra, mumukṣu, mokṣadharma, apavarga, kaivalya,
jñānayoga, brahmanirvāṇa. `mokṣ` and `nirvāṇ` alone are excluded: in the core all 53 and 2
occurrences mean releasing a necklace, shedding tears, or an un-pacified elephant.)*

**Books 1 and 7 are zero too.** They are later than the core by this store's own attested
constraints — `ram.bala` floors at 330 BCE against the core's 750 BCE — and they demonstrably
absorbed avatāra theology the core does not carry. If the silence tracked date, the late books
would have broken it. They did not.

The external controls confirm the genre permits the vocabulary: the Mahābhārata at 0.97 per
10,000 words and a court epic on the same dynasty at 1.63. The whole Rāmāyaṇa runs 0.00 at
every stratum, early and late alike.

**The silence is a property of the Rāmāyaṇa tradition, not of its date.** Withholding it was
right; the answer is now that it should never be encoded, and the reason is recorded on
`ref.moksa-as-goal` itself so it is not proposed again.

This is a better outcome than promotion would have been. A 200-year tightening bought on a
silence that turns out to be traditional would have been the single largest error the store
could contain, and it would have looked like the project's best result.

## 5. State of the row

| Component | Status |
|---|---|
| Absolutive chaining | attested |
| `-tum` as sole infinitive | attested |
| Lost subjunctive | attested — `subjunctive-baseline.md` |
| **Aspectual collapse** | **attested — §1** |
| **Past participle as predicate** | **attested — §2** |
| Absent pitch accent | unreachable: no epic manuscript carries the notation |

Store: 79 nodes, 117 edges, **73 attested to a locus**. Solve consistent, and both headline
brackets unchanged at `ram.core [750 BCE, 300 BCE]` and `ws.mbh.core [500 BCE, 300 BCE]` —
the Atharvaveda floor these components inherit is slack by 450 and 700 years, exactly as with
the subjunctive.

## 6. Reproduction

```bash
uv run python tools/aspect.py           # sections 1, 2 and 3
uv run python tools/subjunctive.py      # the third component
```

Requires `corpus/av/avs_acu.htm` and `corpus/kavya/kragh_pu.htm` (GRETIL, not redistributed).
