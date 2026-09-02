# The lost subjunctive — one component of the score-5 grammar row, made checkable

**Date:** 2026-09-02 · **Phase:** 4 · **Status:** encoded, and slack

The "post-Vedic, non-Pāṇinian grammar" row is rated **5 of 5** in both inventories and called
"the tightest single bracket" available. It bundles six typologically distinct changes, and
until now a concordance reached two of them. This is the third.

It needed no accented text. The accented Atharvaveda was fetched for a different reason (see
`corpus-audit.md` §6) and turned out to be unnecessary for this: the subjunctive carries no
accent dependency. What was missing was simply a **Vedic baseline**, and the corpus had none.

---

## 1. Why a suffix search is worthless here

The obvious instrument — count word-final `-āti`, the thematic subjunctive 3sg — produces a
clean-looking differential that is **entirely noise**:

```
                        per 10,000 words
  AVŚ         24.68
  Rām core     7.03      apparent 3.5× enrichment in the Vedic text
  MBh arch     8.16
```

Reading the actual word types kills it. Every `-āti` in both epics is a root-class present
(`yāti`, `bhāti`, `vāti`, `pāti`, `ākhyāti`, `jahāti`, `dadāti`), a class-9 present
(`jānāti`, `aśnāti`, `gṛhṇāti`, `badhnāti`, `punāti`, `prīṇāti`, `mathnāti`), or a sandhi
artifact (`nāti` = *na*+*ati*, `cāti` = *ca*+*ati*, `babhūvāti` = *babhūva*+*ati*). The
Atharvaveda contains all the same noise. Not one epic token is a subjunctive.

**The measurement had to be paired within stem.** The subjunctive of a thematic present is
formed by lengthening the stem's own `-a`:

```
  bhava + ti            ->  bhavati    indicative
  bhava + ti, ā long    ->  bhavāti    subjunctive
```

Counting indicative and subjunctive **for the same stem** eliminates every root-class and
class-9 form by construction. 28 thematic stems (classes 1/4/6/10), three person slots.
3pl is excluded: its subjunctive ending `-ān` collides with the accusative plural and, for
the commonest stem here, with `bhavān` "your honour".

---

## 2. The result

```
corpus          words  indicative  subjunctive  subj share
AVŚ            85,489         200           46      18.70%
Rām core      160,993         247            0       0.00%
MBh arch      903,578       1,778            0       0.00%
```

The Atharvaveda's 46 subjunctives are 19 distinct forms across 15 distinct stems — not one
lexical accident:

```
bhavāti ×8   vadāsi ×5   jīvāti ×4   patāti ×3   nayāti ×3   kalpayāti ×3
randhayāsi ×3   vadāti ×2   vahātha ×2   tiṣṭhāti ×2   jayāti ×2   sṛjāti ×2
bhavāsi   nayāsi   vahāti   tapāti   tiṣṭhāsi   pibātha   vardhayātha
```

> AVŚ 2.36.3 — *súvānā putrā́n máhiṣī **bhavāti*** · "she shall become chief queen"

At the Atharvaveda's rate the expected counts in the epics are **57** and **409**. Observed:
zero and zero.

## 3. The positive control

An absence is not evidence until something rules out the instrument being blind — the lesson
the Pāṭaliputra row taught this project, and the one the *mokṣa* silence failed.

The subjunctive did not vanish entirely. Its **1st person** survived by being reassigned to
the imperative paradigm, and that is exactly what the same search finds:

```
  Rām core   karavāṇi ×2
  MBh arch   karavāṇi ×39   dadāni ×32   karavāma ×3   karavāva ×1
```

So the category is visible to the instrument in the epics; it is the 2nd and 3rd persons that
are gone. **The zero is a property of the text, not of the search.** And unlike the *mokṣa*
silence, this is a morphological category rather than a topic — a narrative has as much use
for "he shall become" as a hymn does, so the genre confound that blocked *mokṣa* does not
apply. It is encoded rather than withheld for exactly that reason.

## 4. What it is worth in the network — nothing, and that was the prediction

Encoded as an R-10 split off `ref.post-vedic-grammar`:

| Record | |
|---|---|
| `ws.atharvaveda` | work-state, [1200 BCE, 900 BCE], asserted |
| `ref.subjunctive-loss` | referent, text-derived |
| `e.154` | `absent-from` — the loss is absent from the Atharvaveda · **attested** |
| `e.155` | `ram.core` presupposes the loss · **attested** |
| `e.156` | `ws.mbh.core` presupposes the loss · **attested** |

Solve: **consistent**, 104 variables, 245 constraints.

```
  ram.core      [750 BCE, 300 BCE]     unchanged
  ws.mbh.core   [500 BCE, 300 BCE]     unchanged
```

The floor this supplies is 1200 BCE. The floors already standing are 750 and 500 BCE, so the
new constraint is **slack by 450 and 700 years**, and the min-cut support for every bound is
unchanged.

**That is the predicted outcome, and predicting it correctly is the point.** The published
result from Phase 4 was that a referent's bound is set by its *earliest* attester, so a new
source moves a bound only by supplying a new extreme — and therefore precision scales
logarithmically in corpus size while independent checks scale linearly. The Atharvaveda is an
extreme by construction: it is by far the earliest text in the store. It was the strongest
available test of that law, and the law held. Corpus growth bought checking, not resolution,
in the one case most likely to have bought resolution.

What it did buy is real: a 5-of-5 row that rested on an unfalsifiable bundle now has three of
its six components attested to a re-runnable measurement with a positive control.

## 5. A defect found and closed

The Rāmāyaṇa loader had never stripped TEI markup inside `<l>` elements, so `<seg type="pāda"
n="a">` was being glued onto the first word of every pāda — **16,154 corrupted tokens**, e.g.
`n="a">sa` where the text has `sa`.

Every published count was re-run against both loaders. **None changed**: `tvā` 1,714,
`viṣṇu` 27, `mokṣ` 53, and all four soteriological zeros are identical either way, because
the corruption only ever prefixed a token and every published search was a substring or
word-final match. The one pattern it did affect is `pāda`, which matched the literal string
inside `type="pāda"` in every segment — 962 spurious verses against 162 real ones. That was
never a published search. A latent hazard rather than a live error, and now closed.

**One published figure is imprecise for a different reason.** "1,714 `-tvā` hits" counts
verses containing the substring `tvā`, which includes `tvām`/`tvāṃ` "you" (accusative). The
figure for verses containing a word-final absolutive is **1,298**. The claim it supports —
that absolutive chaining is pervasive — is unaffected.

## 6. Reproduction

```bash
uv run python tools/subjunctive.py            # the table above
uv run python tools/subjunctive.py --types    # every -āti type, for hand-checking the zero
```

Requires `corpus/av/avs_acu.htm` (GRETIL, not redistributed — see `corpus-audit.md` §6).
