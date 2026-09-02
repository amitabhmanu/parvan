# Splitting the load-bearing horizons, and what was really carrying the ceiling

**Date:** 2026-09-02 · **Phase:** 4 · **Status:** done; the cut did not move, and the reason is structural

Every bound in this network terminates in a **material horizon that nothing inside the network
dates**. Each carried its bound alone, and the interval itself is the binding constraint — so
no text could ever raise a minimum cut, which three corpus additions had by then demonstrated
three times over.

```
hor.kosala-power       [-750, -650]   incoming edges: 0
hor.massed-elephants   [-500, -350]   incoming edges: 0
hor.mauryan-capital    [-350, -300]   incoming edges: 0
```

## What the split found

Two of the three were bundling **two dating chains in one node and one interval**.

`hor.mauryan-capital` read *"Pāṭaliputra excavation; Nanda accession through early Mauryan
consolidation"* — site stratigraphy and dynastic chronology, in a single interval, under
`dating_method: archaeological-horizon`. Separated:

| node | chain | interval |
|---|---|---|
| `hor.mauryan-capital` | historical — Strabo XV.1.36, Megasthenes at Palibothra, anchored in Seleucid chronology | [-350, -300] |
| `hor.pataliputra-site` | archaeological — Altekar & Mishra, *Kumrahar 1951–1955*, Patna 1959 | [-600, -150] |

**Ablation says which one was doing the work:**

```
as built                          Rām core ceiling   300 BCE
archaeological chain removed                         300 BCE   (no change)
historical chain removed                             230 BCE
```

Archaeology alone supports nothing tighter than 150 BCE. **The bundled node had been
presenting historical-chronological precision under an archaeological label** — the "category
reference" weakness this store already records against its whole material tier, made concrete
and measurable.

Independence is recorded as **partial**, deliberately: the Kumrahar timber palisade is
conventionally identified as the wall Megasthenes describes, so the site's phasing leans on the
very account it is supposed to be independent of. The archaeological node's interval is wide
enough that nothing rests on the entanglement.

`hor.massed-elephants` was split the same way, the Greek eyewitness accounts moving to
`anc.greek-elephant-accounts` — Arrian *Anabasis* V.15 on Poros' elephant line, Strabo XV.2.9
on the five hundred elephants Seleucus received under the settlement of c. 303 BCE.

**`hor.kosala-power` was deliberately NOT split.** It rests on one chain, and splitting a
single excavation into two labels would manufacture precisely the false redundancy this
exercise exists to expose. Its locus is now resolved: K. K. Sinha, *Excavations at Śrāvastī —
1959*, reporting Painted Grey Ware in the lowest **pre-fortification** levels passing into
NBPW beneath a rampart circuit of about five kilometres.

## Why the minimum cut did not move, and why that is not a failure

It is still 1 everywhere, and the reason is structural rather than sloppy:

> **A minimum cut counts routes that *realise* a bound.** Two independent chains raise it only
> when their precisions match. Real evidence almost never comes in matched pairs.

Two genuinely independent chains reaching the same conclusion with different tightness produce
one binding route and one slack one — cut 1, permanently. **The measure is telling the truth
about the evidence, not about the store.** Adding evidence of lower precision, however
independent, cannot raise it. That is worth knowing before anyone spends effort trying.

What such evidence *does* buy is **backstop distance**, which is the quantity worth reporting:
how far a bound falls if its binding route is removed. For the Rāmāyaṇa's ceiling that is now
70 years — to the writing horizon at 230 BCE — against the 550-year collapse it faced before.

## Epigraphic loci: one resolved, one downgraded

- `anc.khoh-plates` **resolved and corrected.** Fleet, *CII* III: the Khoh copper plate of
  Mahārāja Sarvanātha, Gupta year 214 = **533/534 CE**, granting Vyāghrapallikā and
  Kacārapallikā for the worship of Piṣṭapurikādevī, and referring to the Mahābhārata as the
  *śata-sāhasrī saṃhitā*. The store had [500, 520] — wrong by some fifteen years, and naming no
  plate, though Sarvanātha issued several and only this one carries the phrase. It moves no
  bound; the anchor is slack either way. Record accuracy, not a result.
- `anc.imprecatory-grants` **downgraded to asserted.** Its locus named hundreds of grants and
  no grant. An anchor whose locus cannot be looked up is an assertion with a date attached, and
  that difference is this project's entire argument. Promoting it back needs one plate, one
  volume, one page — a smaller claim, not a larger one.

After both changes the headline still holds: dropping all 48 asserted-tier constraints leaves
76 attested ones, the store stays consistent, and both epic brackets are identical to the year.
