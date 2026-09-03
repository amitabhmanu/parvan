# F-1 · Verdict: fires

**Date:** 2026-09-03 · **Status:** adjudicated · **Reproduce:** `uv run python projects/sanskrit-epics/tools/f1_check.py`

The prediction, frozen in `preregistration.md` before a solver existed:

> **F-1 · Metrical evidence carries nothing.** If ablating every `metrical-statistics` edge
> does not degrade anchor recovery, then metrical arguments carry no usable information, and
> the source document's claim that language and metre form "the tightest single bracket" is
> wrong. Report it as such.

**It fires** — but the specified test is not what decides it, and saying why matters more than
the verdict.

---

## 1. The specified instrument cannot answer the question

```
ablation                                   PASS  WEAK  FAIL   rate
baseline (nothing removed)                    0     0     9     0%
metrical-statistics removed                   0     0     9     0%
metre + linguistic-stratigraphy removed       0     0     9     0%
```

Every recovered interval is **byte-identical** across all three runs.

That is not a pass. V-2 anchor recovery already fails 0 of 9 at baseline, because every anchor
in this store is **terminal** — nothing in the corpus is later than it, so holding one out
leaves its ceiling unbounded whatever else the network contains. *A measure that reads zero
before an ablation cannot read lower after it.*

So F-1's literal condition — "ablating does not degrade anchor recovery" — is satisfied
**vacuously**. Reporting that as the finding would be worse than reporting nothing, because it
would look like evidence and be an artefact of a floored instrument. The preregistration could
not have known this: V-2's terminality was discovered afterwards (`v2-retrodiction.md`).

When an instrument cannot discriminate, the honest move is to say so and answer the question
another way.

## 2. What the class actually does: it bounds only itself

Ablating the classes and asking what moves anywhere in the network:

```
metrical-statistics removed                      2 bounds moved
  ref.classical-kavya-style#attestation   [500 BCE, 460 CE]   -> [500 BCE, unbounded]
  ref.classical-kavya-style#emergence     [500 BCE, 460 CE]   -> [500 BCE, unbounded]

metre + linguistic-stratigraphy removed          6 bounds moved
  ref.aspectual-collapse#emergence        [1200 BCE, 300 BCE] -> [1200 BCE, unbounded]
  ref.classical-kavya-style#attestation   [500 BCE, 460 CE]   -> [500 BCE, unbounded]
  ref.classical-kavya-style#emergence     [500 BCE, 460 CE]   -> [500 BCE, unbounded]
  ref.post-vedic-grammar#emergence        [unbounded, 300 BCE]-> [unbounded, unbounded]
  ref.ppp-predicate#emergence             [1200 BCE, 300 BCE] -> [1200 BCE, unbounded]
  ref.subjunctive-loss#emergence          [1200 BCE, 300 BCE] -> [1200 BCE, unbounded]
```

**Every bound that moves is a referent that exists only to carry this class of argument.** Not
one text stratum moves — `ram.core` and `ws.mbh.core` are unchanged to the year, and so is
every other work-state and stratum in the store.

That is a sharper statement than the preregistration anticipated, and a more useful one:

> The metrical and linguistic edges form a **closed pocket** in the graph. They bound the
> concept referents they themselves introduce — *post-Vedic grammar*, *aspectual collapse*,
> *the lost subjunctive*, *classical kāvya style* — and transmit nothing to any text. Remove
> them and the only thing that loses its date is the argument itself.

They are not weak evidence for dating the epics. They are **not evidence for dating the epics
at all**: they are a self-contained description of the language, correctly recorded, wired to
nothing.

## 3. The independent measurement agrees

`new-instruments.md` measured the same class a different way, against 66,177 lines the
Mahābhārata's editors labelled non-archetypal — a per-passage label of relative date holding
work, genre, language and transmission constant:

```
metric                    archetypal   apparatus   shift
perfect/imperfect ratio         0.88        0.94   1.07×
PPP-predicate per 10k          14.90       14.26   0.96×
aorist per 10k                  1.12        0.93   0.83×
mean word length                7.01        7.07   1.01×
```

Flat, while lexical content across the same boundary moves fifteenfold and more. Three
independent routes now agree: ablation moves no text bound, the labelled-data test shows no
discriminative power, and the specified instrument cannot see anything either way.

## 4. Consequences, stated as the preregistration requires

**The source's claim is wrong.** "Language and metre form the tightest single bracket" is the
highest-rated evidence class in both inventories. It supplies no bracket on either epic. The
row survives only as what `aspect-and-participle.md` and `subjunctive-baseline.md` showed it to
be — a **floor**, post-Vedic, resting on a comparison with the Atharvaveda that is slack by
450 and 700 years.

**Phase 6 as designed is retired.** It proposed to seed latent stratification from *vipulā*
ratios, compound length, and morphological frequencies in sliding windows — precisely this
class. Running it would spend weeks inferring strata from features now measured three ways to
carry nothing. This is the "stopping condition, not a tuning opportunity" the preregistration
demands, and the stop is recorded here rather than absorbed quietly.

**The 14 edges stay in the store.** They are accurate records of an argument the field makes,
and deleting them would hide the finding rather than state it. What changes is that the finding
is now attached to them.

**What replaces Phase 6.** The same measurement that retires the form-based version endorses a
content-based one: lexical markers move 15× across the labelled boundary. The Mahābhārata has
66,177 labelled lines to train on and the Rāmāyaṇa has **no apparatus at all**, so a lateness
model fitted on the first and applied to the second would produce a per-passage stratification
for a text that has none — testable against the one thing independently known, that books 1
and 7 are late. That prediction must be preregistered before the model is run, and the
theological vocabulary must be held out, or it will detect devotion rather than date.

## 5. What this does not say

It does not say the epic language is not post-Vedic; it is, and that is attested. It does not
say metre and morphology are uninformative about language history — they are the primary
evidence for it. It says something narrower and harder: **in this network, on this corpus,
that class of evidence does not reach any text whose date is in question.**
