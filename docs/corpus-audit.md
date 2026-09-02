# M0 — Corpus reachability audit

**Date:** 2026-08-31 · **Phase:** 0 · **Status:** complete

**Verdict: green.** Both critical editions are machine-readable with verse addressing intact,
and structured epigraphy exists for the anchor class that matters most. Nothing in Phases 1–6
is blocked on digitization. Two items need verification before Phase 6.

Verification levels below: **fetched** = page retrieved and inspected directly;
**search** = from search-result summaries only, re-verify before relying on it.

---

## 1. Critical editions

### Mahābhārata — BORI / Poona critical edition · fetched

- **Source:** GRETIL, `1_sanskr/2_epic/mbh/mbh_NN_u.htm`, one file per *parvan*.
- **Basis:** Bhandarkar Oriental Research Institute, Pune. Entered by Muneo Tokunaga et al.,
  revised by John Smith (Cambridge) et al.
- **Encoding:** UTF-8, IAST with diacritics (`ā ṃ ḥ ṛ`), header carries the full mapping table.
- **Addressing — confirmed by inspection:**

  ```
  06,001.001a     parvan 06, adhyāya 001, śloka 001, pāda a
  06,001.000*0001_01   star passage (CE-excluded), numbered separately
  ```

**This is finer than R-1 requires.** The plan specifies `MBh.parvan.adhyāya.śloka`; the source
gives pāda-level granularity for free. Adopt pāda addressing in the schema — metrical work in
Phase 6 operates on pādas, and coarsening later is trivial where refining is not.

**Unanticipated find — the star-passage apparatus.** Lines marked `*NNNN` are passages the BORI
editors relegated to the apparatus as non-archetypal. This is free stratification signal the
design document did not account for: the critical editors have already marked what they judged
late, per passage, with manuscript support. Two uses —

- Seed evidence for Phase 6's change-point detection, independent of metre.
- A ready source of `absent-from` edge candidates (**R-3**), which §4 of the design identifies
  as the only thing that ever bounds a concept referent from below.

Worth a schema field: `archetypal: true|star` on stratum passages.

### Rāmāyaṇa — GRETIL · fetched

- **Primary:** `sa_rAmAyaNa.xml`, TEI-conformant XML. Tokunaga, revised by John Smith;
  second revision of Kāṇḍas 2–3 by Oliver Hellwig (`sa_vAlmIki-rAmAyaNa-rev-2-3.xml`).
- **Southern Recension:** `sa_vAlmIki-rAmAyaNa-southern-2.xml`, entered by Oliver Hellwig.
- **Formats offered:** TEI XML, analytic HTML, plain text.

**The southern recension file is a direct win.** §12's "southern vs northern recension
divergence" constraint (scored 3, relative ordering) stops being a citation to someone else's
collation and becomes computable from two files.

> **RESOLVED 2026-09-01 — this is the Baroda critical edition.** 18,761 verses across 7
> kāṇḍas, against the CE's ~18,600 and the vulgate's ~24,000, with sarga counts well below
> vulgate values throughout. Addressing is `R_1.001.001ab` — kāṇḍa.sarga.śloka plus pāda-pair.
> Phase 6 is unblocked. See `promotion-slice.md`.
>
> **But: no critical apparatus.** The TEI carries zero `<app>`, `<rdg>`, `<lem>` or `<note>`
> elements. Unlike the Mahābhārata file, it preserves no star passages, so `archetypal:
> true|star` can be populated for the Mahābhārata and **not** for the Rāmāyaṇa. That removes
> the cheapest way to distinguish an archetypal reading from an excised one.

---

## 2. Epigraphy

### Siddham — The Asia Inscriptions Database · fetched

- **URL:** https://siddham.network/ — live, active (uploads through January 2026).
- **Format:** EpiDoc (TEI for epigraphy), XML. Relational tables over XML snippets.
- **Bulk access:** Zenodo dataset releases, "Siddham Epigraphic Archive — Texts in EpiDoc"
  (search-level; confirm the current DOI at Phase 4).
- **Licence:** Creative Commons, open access. Specific variant not stated on the about page —
  check Terms & Conditions before redistributing anything derived.
- **Coverage:** Sanskrit, Prakrit, Tamil, Telugu, Kannada, Khmer and others; early centuries BCE
  to 19th century; South, Central and Southeast Asia. Development began with **Gupta epigraphy**.

**This is the best single find of the audit.** The Gupta focus lands precisely on Parvan's
highest-value anchor class — the copper-plate grants of §7, including the imprecatory verses
quoted in hundreds of grants from the 5th century, which carry two of the design's four
score-5 Mahābhārata ceilings. Structured, addressable, and independently dated.

### Corpus Inscriptionum Indicarum, Epigraphia Indica · search

- Internet Archive holds CII (Hultzsch vol. I *Inscriptions of Asoka*; Lüders vol. II.2;
  Mirashi vol. VI) and the full run of *Epigraphia Indica*.
- **Format: PDF and DjVu with OCR of variable quality.** Not bulk-ingestible.

**Treat as hand-encoding sources, not pipelines.** These supply a citable locus per anchor
(volume, inscription number, page), which is all **G-1** requires. Anchors number roughly 40
in the target store — hand-encoding is the right cost.

---

## 3. Secondary scholarship — O-3

| Source | Status | Use |
|---|---|---|
| Hopkins, *The Great Epic of India* (1901) | Public domain | Metrical groundwork; the original *vipulā* statistics |
| Sukthankar, *Prolegomena* (1933) | On Internet Archive; likely PD | Stratification argument, Bhārgava thesis, contamination |
| Brockington (modern) | **In copyright** | Best seed prior for Phase 6, and not redistributable |

**Consequence for R-15.** The plan wants several published stratifications as competing seeds.
Brockington's cannot be shipped in the store. Two lawful routes: cite it as an `asserted`-tier
edge set with page loci and no reproduced text; or **re-derive** a *vipulā*-based partition
from the GRETIL text using Hopkins' published method. Re-derivation is preferable anyway — a
partition Parvan computes is one it can also recompute under ablation.

---

## 4. Blocking status by phase

| Phase | Blocked? | Note |
|---|---|---|
| 1 · Schema, store, gates | No | No external data needed |
| 2 · STP solver, V-1 gate | No | §12 hand-encoded from the markdown in this repo |
| 3 · Harness | No | — |
| 4 · Corpus & calibration | No | Siddham for Gupta anchors; CII/EI hand-encoded |
| 5 · Bayesian layer | No | Depends on Phase 4 calibration texts, not on new sources |
| 6 · Latent stratification | **Verify first** | Confirm the Rāmāyaṇa edition basis; adopt pāda addressing |
| 7 · Reports | No | — |

---

## 5. Actions arising

1. **Adopt pāda-level addressing** in the Phase 1 schema, not śloka-level. Amends **R-1**.
2. **Add `archetypal: true|star`** to stratum passage records to carry the BORI apparatus.
3. ~~Verify the GRETIL Rāmāyaṇa edition basis before Phase 6.~~ **Done** — Baroda CE
   confirmed; no apparatus.
4. **Confirm the Siddham licence variant and current Zenodo DOI** at Phase 4.
5. **Plan to re-derive** rather than ship a Brockington seed partition (**R-15**).

**Update 2026-09-01.** The three GRETIL Rāmāyaṇa files have been fetched into a gitignored
`corpus/` directory (6.1 MB, not redistributed).

**Update 2026-09-02 — the Mahābhārata, and the apparatus check.** All 18 parvans fetched
(16 MB, gitignored). No TEI exists for the MBh; the older HTM files are the ones that
preserve the BORI apparatus, which is why they are the right source.

```
224,679 lines parsed, all 18 parvans
158,502 archetypal          (~79k slokas, matching the critical edition)
 66,177 apparatus           star (*) and appendix (@) passages
     62 unparsed (0.028%)   malformed at source, reported not swallowed
```

**`--archetypal-only` is a capability the Rāmāyaṇa cannot offer.** A floor resting on a star
passage is a floor on an interpolation, and until now there was no way to tell.

Getting the parse right took four attempts, each one silently losing data until a completeness
assertion was added. The format has five variants — a tab separator except in parvan 10 which
uses `<>`, the apparatus marker after rather than before the pāda letter, uppercase pāda
letters in prose runs, `@` appendix markers alongside `*` star markers, and marker suffixes
like `*0128_01(127ab)`. The first pattern loaded 87% of the corpus and reported nothing wrong.
`load_mbh` now refuses above a 0.05% tolerance, because an absence search over a corpus that
drops lines is worthless.

---

## 6. Accented Vedic text — correction and availability · fetched 2026-09-02

An earlier reading of the grammar row held that GRETIL strips accent from every text it
hosts, making "absent pitch accent" unfalsifiable for want of data. **That is GRETIL's
stated default but not its practice**, and the correction matters because the conclusion it
supported was published.

- **Default, confirmed in the file header of `rv_hn01u.htm`:** "Unless indicated otherwise,
  accents have been dropped in order to facilitate word search." Inspection agrees — the
  van Nooten–Holland Ṛgveda reads `RV_1,001.01a agnim īḷe purohitaṃ yajñasya devam ṛtvijam`,
  vowel-length and anusvāra diacritics only, no udātta or svarita.
- **The exception is shipped.** `1_veda/1_sam/avs_acu.htm` — Atharvaveda-Saṃhitā, Śaunaka
  recension, **accented**, alongside `avs___u.htm` unaccented. Verified by inspection:

  ```
  (AVŚ_1,1.1a)  yé triṣaptā́ḥ pariyánti víśvā rūpā́ṇi bíbhrataḥ
  (AVŚ_1,1.1c)  vācás pátir bálā téṣāṃ tanvò adyá dadhātu me
  ```

  UTF-8 with combining marks (`á` udātta, `à` svarita, `ā́` long udātta), header carries the
  mapping. Addressing is `AVŚ_book,hymn.verse.pāda` — the same pāda granularity as the
  Mahābhārata files, so it needs no new addressing scheme (**R-1**).
  Basis: Vishva Bandhu, Hoshiarpur 1960–64.

### What this does and does not unblock

| Grammar-row component | Before | After | Why |
|---|---|---|---|
| Absent pitch accent | unreachable | **still unreachable** | See below — the obstacle is not the corpus |
| Lost subjunctive | unreachable | **reachable** | Needs a Vedic baseline, not accent |
| Absolutive chaining | reachable | reachable | — |
| `-tum` as sole infinitive | reachable | reachable | — |
| Aspectual collapse | unreachable | unreachable | A claim about function across a whole text |
| Past participle as predicate | unreachable | unreachable | Same |

**Accent stays unreachable for a better reason than the one first given.** Accent notation is
a Vedic scribal apparatus. No epic manuscript in any recension carries it, so the epic side of
the comparison cannot be measured from any edition, however good — the mark was never written.
The epic's unaccented state records how the text was transmitted, not how it was spoken.

This is the **third instance of one confound** already in the store: an absence that may record
genre rather than date, alongside the Rāmāyaṇa's silence about *mokṣa* (`v2-retrodiction.md`)
and the compound-length register effect (`compound-length.md`). Worth naming as a standing
check — an absence needs a positive control before it earns an edge.

**The subjunctive is the actionable one.** Subjunctive morphology (`-āt`, `-ān`, `-āsi`,
`-āni`) carries no accent dependency; establishing that the forms were productive in the
earlier stage needs only an accented-or-not Vedic Saṃhitā. This takes the score-5 grammar row
from two of six components attestable to three, and turns a binary absence claim into a
measured frequency differential, which is stronger evidence than the row currently carries.

### Second use — the Atharvaveda as a network node

Separate from the grammar row, an early Saṃhitā is the first corpus addition with a structural
reason to move a bound. A referent's emergence ceiling is set by its **earliest** attester, and
every text in the store so far is late; adding the Mahābhārata to a Rāmāyaṇa-only network moved
one referent and bound nothing precisely because neither is an extreme. An Atharvaveda is an
extreme by construction. **This is a real test of the "corpus growth buys checking, not
resolution" result rather than a second confirmation of it** — and either outcome is
informative.

Its `absent-from` potential is the larger prize and the larger trap: referents the epics treat
as ordinary that are missing from the Atharvaveda would floor those referents' emergence, which
is the only mechanism that floors a text presupposing them. Every such edge needs the
Pāṭaliputra treatment — a positive control — before it may leave quarantine.

**Fetched 2026-09-02** into `corpus/av/avs_acu.htm` (1.1 MB, gitignored). Parse is complete:
all 11,395 verse-ID lines matched, zero dropped, 731 hymns and 5,839 verses across all 20
books. Two encoding differences from the epic files, both silently fatal to a cross-corpus
search if unhandled — accent as a combining acute or grave, and vocalic *r* written as
`r` + COMBINING RING BELOW rather than the precomposed `ṛ` the epic files use. `av_fold()`
in `tools/concordance.py` normalises both, so a pattern written for the epics works here
unchanged. Available as `--corpus av`.

**Outcome: the subjunctive component is now attested, and the bound it supplies is slack.**
See `subjunctive-baseline.md`. The Atharvaveda is the earliest text in the store and so was
the strongest available test of the Phase 4 result that corpus growth buys checking rather
than resolution. The law held: both headline brackets are unchanged to the year.


---

## 7. Kālidāsa, Raghuvaṃśa — a genre control · fetched 2026-09-02

`corpus/kavya/kragh_pu.htm` (GRETIL, ed. Scharpé, *Kālidāsa Lexicon* I, Bruges 1964), 284 KB,
gitignored. Parse complete: 1,627 verses across 19 sargas, of which **59 carry a `*` marker**
— *kṣepaka*, verses the editor judged interpolated. That is the same apparatus signal the BORI
Mahābhārata files carry and the Baroda Rāmāyaṇa lacks, so `archetypal: true|star` and
`--archetypal-only` work here too. A control resting on an interpolated verse is not a control.

**Held as a control, not as a dating source.** Court epic in the same genre as the Rāmāyaṇa,
narrating the same dynasty, securely dated c. 400 CE (`ws.kalidasa`, already in the store). Its
value is that it answers "could a text of this kind have said this?" for any absence claim
about the Rāmāyaṇa.

It earned its place immediately, and twice:

1. It **refuted the aorist** as a dating metric. Kālidāsa's aorist rate matches the
   Atharvaveda's and is 25× the Rāmāyaṇa's — a register effect, not a chronological one.
2. It **confirmed the genre permits soteriological vocabulary** (1.63 per 10,000 words), which
   with the Rāmāyaṇa's own late books retired the withheld *mokṣa* constraint for good.

See `aspect-and-participle.md`. Available as `--corpus ragh`.
