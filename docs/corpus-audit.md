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
`corpus/` directory (6.1 MB, not redistributed). Nothing else has been downloaded.
