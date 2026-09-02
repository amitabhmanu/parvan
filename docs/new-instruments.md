# Two new instruments, one of which refutes a method the store was using

**Date:** 2026-09-02 · **Phase:** 4 · **Status:** one encoded, one methodological

Everything in the store so far has been an argument somebody had already made, checked against
the text. This is the first work that goes the other way: read the corpora, find signals
nobody in the source inventory proposed, and test them.

Two came out of it. The second is a genuine result about **method** rather than about dates,
and it constrains what the rest of the project can hope for.

---

## 1. The critical apparatus is a labelled lateness set

The BORI editors marked, passage by passage and on manuscript evidence, which lines they
judged non-archetypal. That is **66,177 lines — 28% of the transmitted Mahābhārata** — each
carrying a label of *relative* lateness.

Nothing else this project can reach controls so tightly. Every external comparison it makes —
Vedic against epic, epic against Kālidāsa — varies genre, register, subject matter and
centuries simultaneously. This one varies date and almost nothing else: same work, same
genre, same language, same transmission, same scribes.

**Its limit, stated first.** The archetype is not the original; it is the reconstructed common
ancestor of the surviving manuscripts, itself already a late redaction. So this measures
accretion *after* the archetype, not the whole history. A term can be late in absolute time
and still sit in the constituted text, because the constituted text is late.

### It calibrates

Before trusting it to discover anything, test it on referents with independent external dates:

```
referent                          arch/10k   app/10k    enrichment
dīnāra  (Roman aureus, 1c CE+)       0.000     0.085   only in apparatus
pustaka (book)                       0.000     0.113   only in apparatus
temple  (devālaya / mandira)         0.033     0.507        15.3×
mokṣa vocabulary                     0.797     2.676         3.4×
Yavana                               2.368     1.324         0.6×
horse-chariot                        0.089     0.056         0.6×
```

*dīnāra* — a Roman coin, and the source inventory's clearest late marker — occurs **zero times
in the constituted text and only in the apparatus.** So does *pustaka*, "book". Temples run
15× enriched. Early material culture is flat or depleted. The instrument works.

*(One trap on the way, and it is the same trap as always: `hūṇ` matches **`sthūṇa`**, "pillar" —
`sthūṇāsahasraiḥ`, "with a thousand pillars". An uncorrected search reported a Hūṇa rate five
times the true one.)*

### It discovers

Ranking all vocabulary by log-odds enrichment rather than testing a list produces a coherent
and entirely unprompted signature of what the tradition added:

| enriched in the apparatus | enriched in the constituted text |
|---|---|
| `devi` `umā` `devīṃ` `priye` `śobhane` | `vaiśaṃpāyana` `saṃjaya` `bhīṣma` |
| `maheśvaraḥ` `mahādeva` `devadeveśa` | `rājan` `mahārāja` `viśāṃ pate` |
| `namaḥ` `namo` | `bhāratā` `bharatarṣabha` |
| `puṇyaphalaṃ` `dānaṃ` `karmavipākena` | `raṇe` `tato` `tataḥ` `iva` |
| `śṛṇu` `kathitaṃ` `mārkaṇḍeyaḥ` `nārada` | |

Śaiva and goddess devotion, merit-and-gift ritual, and didactic framing accrete onto a
constituted text that is narrative, martial and courtly. That is what the scholarship says
qualitatively; here it is measured, and it was found rather than assumed.

### And it refutes something

Run the store's own linguistic dating metrics against the same label:

```
metric                    archetypal   apparatus   shift
perfect/imperfect ratio         0.88        0.94   1.07×
PPP-predicate per 10k          14.90       14.26   0.96×
aorist per 10k                  1.12        0.93   0.83×
thematic subjunctives              0           0       —
mean word length                7.01        7.07   1.01×
```

**Every one is flat.** Lexical content moves by 15× and more across the same boundary;
grammar does not move at all.

The explanation is not mysterious: an interpolator adding verses to the Mahābhārata writes
epic Sanskrit *on purpose*. The register is a target, not a symptom. So linguistic
stratigraphy separates Vedic from epic — a real gap of centuries and a change of genre, which
`subjunctive-baseline.md` and `aspect-and-participle.md` measure properly — and **cannot
separate epic from epic-plus-centuries.**

Two consequences, and they are not small:

- The score-5 grammar row survives as what it always claimed to be, a **floor**: the language
  is post-Vedic. It gives no support whatever to *fine-grained* stratification.
- **Phase 6 as planned is in trouble.** It proposed to infer strata from metrical and
  morphological features in sliding windows. On the one labelled dataset available, features
  of that class have no discriminative power at all. Referential content does. Phase 6 should
  be re-scoped around what the text *mentions* before any effort goes into how it says it.

This is also the third independent arrival at one confound — register imitated rather than
inherited — after compound length and the aorist.

---

## 2. The writing horizon, and the network's first real backstop

The Rāmāyaṇa core does not merely lack writing. It visibly does **something else** in the slot
a literate culture fills with a document, and that turns an argument from silence into an
argument from substitution.

### Vocabulary

Zero `lipi` (script), zero `pustaka` (book), zero seals — `mudrā` returns nothing once
`samudra`, "ocean", is excluded — and no written or sealed message anywhere in 14,130 verses.

### Semantics: the root is present and pre-literate

√likh occurs **eleven times in the core and never means "write."** Ten are one formula:

> Rām 4.040.028 — *śṛṅgair **ambaraṃ vilikhann** iva* · peaks as if scraping the sky
> Rām 6.030.023 — *kailāsaśikharākāro dṛśyate **kham ivollikhan*** · a palace scoring the sky

The eleventh is beasts scoring each other with fangs (6.046.038). The word for "write" is
sitting right there in its original sense of scratching, doing no literate work at all.

**The Mahābhārata archetype has moved one step along that path and no further** — √likh has
reached *draw*: MBh.3.278.013 *citre 'pi ca **likhaty** aśvān*, "he draws horses in a picture";
MBh.6.003.009 *pratimāś **cālikhanty** anye*, "others draw images". Still never "write". So the
corpus preserves a three-stage sequence in one root: **scratch (Rām core) → draw (MBh
archetype) → books (MBh apparatus, where `pustaka` appears and nowhere else).**

### The control, which is the plot itself

The core has **25 `dūta` episodes** and **18 uses of `abhijñāna`, "recognition token"** — nine
times the rate of the Mahābhārata archetype. Its central authentication problem is the one a
letter exists to solve: prove a messenger genuine to a captive behind enemy lines.

It is solved with a **signet ring**:

> Rām 4.043.011 — *dadau … **svanāmāṅkopaśobhitam aṅgulīyam abhijñānam*** · he gave the ring
> adorned with his own name, as a token
> Rām 5.034.002 — *dūto rāmasya … **rāmanāmāṅkitaṃ** cedaṃ paśya devy aṅgulīyakam* · "I am
> Rāma's messenger; look at this ring marked with Rāma's name"

Sītā answers not with a reply but with the *cūḍāmaṇi*, her crest jewel (5.036.052).

So the text **has objects marked with a personal name** — the signet is right there — and no
writing. That is a far stronger position than absence: the technology's precursor is attested,
the occasion for its use is attested twenty-five times, and the culture reaches for a token
every time.

**And the genre excuse does not apply**, because later layers of the same tradition acquire the
vocabulary: `pustaka` appears in the Mahābhārata apparatus and nowhere else in the corpus.

### What it buys: a backstop where the network needed one most

Encoded conservatively — `anc.asokan-brahmi` takes the *late* end of the Brāhmī debate
(260–230 BCE), so the bound is as weak as the evidence allows.

The store's worst structural weakness has been that the pre-Common-Era ceiling for **both**
epics rests on a single row the source itself scores 2 of 5, with a minimum cut of 1. Ablation:

```
scenario                                        Rām core ceiling
as built                                            300 BCE      (via Pāṭaliputra)
Pāṭaliputra attestation removed, writing kept       230 BCE      (via Aśokan Brāhmī)
both removed                                        250 CE
```

The writing constraint is **slack by 70 years** and does not tighten anything. What it does is
convert the failure mode: if the Pāṭaliputra argument falls, the ceiling now slips **70 years
instead of 480.** For a network in which every bound had a minimum cut of 1, that is the first
genuine insurance policy in it.

*(A correction while measuring this: the ceiling does not rest on the Pāṭaliputra argument
from silence as such. There are two such silences, one via the Rāmāyaṇa and one via the
Mahābhārata, and removing either leaves the other. The single point of failure is `e.044`, the
attestation of the referent both silences point at — which is what the redundancy analysis
meant by "both routes pass through the same terminus," now confirmed by ablation.)*

---

## 3. Reproduction

```bash
uv run python tools/apparatus.py             # calibration and the metric test
uv run python tools/apparatus.py --discover  # the enrichment ranking
uv run python tools/writing.py               # all three parts of the writing argument
```

Store after this work: 81 nodes, 119 edges, 74 attested. Solve consistent, both headline
brackets unchanged at `ram.core [750 BCE, 300 BCE]` and `ws.mbh.core [500 BCE, 300 BCE]`.

## 4. What this opens that is not yet done

- **The southern recension of the Rāmāyaṇa is on disk and unused.** It gives a second labelled
  divergence set of the same kind as the BORI apparatus, for the epic that currently has no
  apparatus at all.
- **Frame depth.** The 5,863 bare `NAME uvāca` attribution lines encode who speaks to whom
  throughout the Mahābhārata; that is a computable map of narrative nesting, and nesting depth
  is a candidate stratum signal that costs nothing to extract.
- **Simile vehicles date the poet, not the hero.** A simile draws on the composer's world, not
  the story's. `iva` occurs 3,090 times in the constituted text alone, and the semantic fields
  its vehicles come from have never been inventoried here.
