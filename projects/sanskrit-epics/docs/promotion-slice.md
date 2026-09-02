# The promotion slice — asserted to attested

**Goal.** Take a handful of §12's realia edges to the critical edition, cite verses, and see
whether F-6 gets an answer. Manual, no agent: the point was to learn what an extraction
contract needs before writing one.

**Result.** Six edges promoted. F-6 now returns a real bracket instead of nothing. Along the
way the text contradicted **three** of §12's rows — one scored 5, two scored 4 — including the
one that was setting the core's floor.

Every search below is reproducible:

```bash
uv run python tools/concordance.py 'd[iī]n+[aā]ra' --count
```

---

## 0. Two audit questions closed

**O-2 resolved: this is the Baroda critical edition.** 18,761 verses across 7 kāṇḍas, against
the CE's ~18,600 and the vulgate's ~24,000, with sarga counts well below vulgate values
throughout. Phase 6 is unblocked.

Addressing is `R_1.001.001ab` — kāṇḍa.sarga.śloka plus pāda-pair, finer than R-1 requires.

**The star-passage check is not available for the Rāmāyaṇa.** The TEI carries zero `<app>`,
`<rdg>`, `<lem>` or `<note>` elements: it is a constituted text with **no critical apparatus**.
The Mahābhārata file preserves the BORI star passages; this one does not. So `archetypal:
true|star` can be populated for the Mahābhārata at Phase 4 and not here — which matters,
because it removes the cheapest way to tell an archetypal reading from an excised one.

---

## 1. Promoted

| Edge | Locus | Basis |
|---|---|---|
| `ram.core presupposes ref.horse-chariot` | Rām.2.090.008 | *rathāśvagajasaṃbādhāṃ yattair yuktāṃ padātibhiḥ* — an army thronged with chariots, horses and elephants |
| `ram.core presupposes ref.iron-weaponry` | Rām.6.086.006 | *āyasaṃ parighaṃ gṛhya* — an iron bludgeon wielded in battle. Cf. 6.060.022, 6.067.006 *sruvaṃ kārṣṇāyasaṃ* |
| `ram.bala presupposes ref.yavana-saka` | Rām.1.053.020–021, 1.054.003 | *pahlavān … śakān yavanamiśritān* |
| `ram.bala presupposes ref.fortified-ayodhya` | Rām.1.005.010–013 | *śataghnīśatasaṃkulām … durgagambhīraparikhāṃ* |
| `ram.core absent-from ref.pataliputra-imperial` | 0/18,761 verses | measured silence, re-runnable |

Note the discipline on iron: most `āyasa` hits in the core are metaphorical — *āyasaṃ hṛdayaṃ*,
"a heart of iron". The cited loci are material iron, a weapon and a sacrificial ladle. Finding
the string is not the same as verifying the claim, and this is the first thing the extraction
contract has to enforce.

---

## 2. Three of §12's rows do not survive contact with the critical edition

### *Dīnāra* — scored 5, and the word is not in the text

```
d[iī]n+[aā]ra   main text (Baroda CE)        0 hits / 18,761 verses
                southern recension file      0 hits
                Hellwig revision, kāṇḍas 2-3 0 hits
```

Zero under every spelling, diacritic-folded included, across all three files. §12 lists

> | *Dīnāra*, the Roman denarius | Floor c. 100 CE on those passages | **5** |

as one of only four score-5 floors in the entire Rāmāyaṇa inventory.

**Removed from the store** — along with `ref.dinara`, `hor.roman-denarius`, and the
`ram.dinara` stratum, which turned out to have no extent. A constraint that bears on no verse
of the critically constituted text does not belong in a store that models it.

### Yavanas and Śakas — RETRACTED. The error was mine.

> **This section originally reported that §12 had misattributed the Yavana/Śaka passages to
> Kiṣkindhākāṇḍa when they were really in Bālakāṇḍa. That finding is withdrawn. §12 was
> right.**

The searches behind it were run on citation-form stems, which **case-ending sandhi hides**:

```
searched        text actually has     result
yavana          yavanāṃś              no match
cola            colān                 no match
āndhra          āndhrāṃś              no match
```

The truncated stem `yavan` returns **Rām.4.042.011** — *kāmbojān yavanāṃś caiva śakān
āraṭṭakān api* — in Sugrīva's western-direction speech, inside Kiṣkindhākāṇḍa exactly where
§12 places it. Kāṇḍa 4 also has *mleccha* and *pulinda* (4.042.010), *cīna* (4.042.012), and
*āndhra, colān pāṇḍyān sakeralān* (4.040.013). The claim that "book 4 contains no foreign
ethnonym at all" was false.

Caught by an extraction agent checking a different edge, which noticed that `pāṇḍya` returning
zero was implausible and found the sandhi cause. The store is corrected, the tool now warns,
and the extractor contract has a rule for it.

**What this cost.** The retracted finding had been committed, pushed, and published in the
design document, where it was presented as evidence of a systematic bias in §12. One of the
three rows in that pattern was not a row at all.

### What the original section got right, restated



§12 places them in "the Kiṣkindhā geography", i.e. book 4, which sits inside the core.
Book 4 of the Baroda CE contains **no foreign ethnonym at all**:

```
kāṇḍa 4, 1,987 verses:
  yavana 0   śaka 0*  pahlava 0   kāmboja 0   mleccha 0   kirāta 0
  pulinda 0  āndhra 0  cola 0     pāṇḍya 0    kerala 0    cīna 0
                                    (* the one śaka hit is śakalīkurvan, "shattering")
```

The genuine attestations are three, all in **Bālakāṇḍa** 1.53–1.54 — Vasiṣṭha's cow generating
armies of Pahlavas, Śakas and Yavanas. (Eight raw `yavana` hits reduce to three: the five in
book 7 are all *cyavana*, the sage, matching as a substring.)

This changes what the constraint does. §12 credits it as a floor on **the core**; it is
actually a floor on **Bāla**, which §12 itself classes as a later stratum whose lateness is not
in dispute. Corrected in the store, with a visible effect: `ram.bala` tightens from
[675 BCE, 609 CE] to **[330 BCE, 609 CE]**, a 345-year gain, while the core is untouched.

### Ayodhyā as a great fortified metropolis — the same error, on the load-bearing edge

This was the constraint actually setting the core's floor, so it got checked next. It fails
the same way.

The canonical description is **Rām.1.005.010–013**, in **Bālakāṇḍa**:

> *kapāṭatoraṇavatīṃ … sarvayantrāyudhavatīm … uccāṭṭāladhvajavatīṃ **śataghnī**śatasaṃkulām …
> **durga**gambhīra**parikhāṃ** durgām anyair durāsadām*
>
> gates and archways · furnished with every engine and weapon · high watchtowers and banners ·
> thronged with hundreds of *śataghnī* · a deep impassable moat · a fortress unassailable by others

Book 2 — Ayodhyā's own book, and part of the core — contains:

| Term | kāṇḍa 1 | kāṇḍa 2 |
|---|---|---|
| *śataghnī* | 1 | **0** |
| *gopura* | 0 | **0** |
| *prākāra* | 0 | 1 — but see below |
| *parikhā* | 1 | 2 — one is **Rājagṛha** (2.064.001) |
| *aṭṭālaka* | 0 | 1 |

Book 2's one moat-and-rampart passage, 2.074.017–018, describes ***niveśa*** — the army's road
camps on Bharata's march, "ringed with moats, enclosed with stuccoed ramparts." Not the city.

So the core's entire fortification datum is the single word *aṭṭālakeṣu* in a list of city
features at 2.006.011. That does not support "a great fortified metropolis."

**Effect:** the edge moves to `ram.bala`, and `ram.core` loosens from [700 BCE, 300 BCE] to
**[750 BCE, 300 BCE]**. Fifty years is not the point. The point is that the core's floor now
rests entirely on `ref.kosala-power` — a single `asserted` edge nobody has checked.

### The pattern, and the likely common cause

**Two** rows fail, not three:

| Row | Score | Failure | Status |
|---|---|---|---|
| *Dīnāra* | **5** | Not in the critical edition at all | holds |
| Fortified Ayodhyā | 4 | In Bālakāṇḍa, credited to the core | holds |
| ~~Yavanas and Śakas~~ | 4 | ~~In Bālakāṇḍa~~ | **retracted — §12 was right** |

With the Yavana row withdrawn there is no longer a *pattern* of Bālakāṇḍa evidence credited to
the core. There is one instance of it, and one row resting on passages outside the critical
edition. Two separate errors, not a systematic bias — and the claim that it was systematic was
itself the product of a search bug.

*Dīnāra* is a different failure and looks like a **vulgate-based claim inside an inventory that
otherwise presupposes the critical edition**. The vulgate's Kiṣkindhākāṇḍa carries sargas the Baroda editors excised, and
*dīnāra* is exactly the kind of late lexical item such passages contain.

This is inference, not verification — confirming it needs a vulgate text, which we have not
fetched. But it is testable, and if right it means §12 violates §13's own step 0: *"Establish
the archetype … otherwise you assign dates to variants that entered in the twelfth century."*

---

## 3. F-6, after agent-driven promotion

```
edges: 109 total | 56 asserted | 53 attested

attested only:
  ram.core           [750 BCE, 300 BCE]      <- identical to the full network
  ram.bala           [330 BCE, unbounded]
  ram.kiskindha-geog [330 BCE, unbounded]
  ws.mbh.core        [unbounded, 299 CE]
```

**The Rāmāyaṇa core's bracket is now carried entirely by checkable evidence.** Stripping every
`asserted` edge leaves it unchanged at [750 BCE, 300 BCE]. Scholarly interpretation contributes
nothing to that bracket — which is the sentence F-6 was written to make possible, and which
was unwriteable two days ago when stripping the asserted tier left nothing at all.

Two things made the difference. Agents promoted realia and absence edges to verse loci. And
material edges — those sourced from a horizon or an anchor — now inherit their node's locus
rather than being tiered `asserted`, because G-1 defines `attested` as pointing at a resolvable
locus and explicitly includes an excavation report page.

**The honest caveat.** Archaeological loci in this store are category references —
"Ayodhyā excavation levels", "Mahājanapada settlement record" — not volume-and-page citations.
They are weaker than the verse IDs, and a reader cannot currently check them the way they can
re-run a concordance search. Bringing them to the same standard is real work and is not done.

## 4. What this taught the extraction contract

Ahead of Phase 3, the refusal conditions need to be sharper than the design's three:

1. **A string match is a candidate, not a citation.** *āyasa* is usually metaphorical; *yavana*
   matches *cyavana*; *śaka* matches *śakalī-*, *maśaka*, *nāśakat*. The agent must read the
   verse and say why it supports the claim, or refuse.
2. **Check the stratum, not just the text.** The Yavana error was not a bad locus — it was a
   locus in the wrong book. Every promotion must confirm the verse falls inside the stratum's
   declared extent.
3. **A zero result is a deliverable.** Absence searches produce `attested` edges of their own,
   provided the pattern and corpus are recorded so anyone can re-run them.
4. **Report contradictions rather than resolving them.** *Dīnāra* returning zero is a finding
   about the source. An agent that quietly picked a different locus, or fell back to
   `asserted`, would have buried the most interesting result of this slice.

---

## 5. Next

- ~~Promote `ref.fortified-ayodhya`.~~ **Done — it failed.** The description is Bālakāṇḍa's.
- ~~Check `ref.kosala-power`.~~ **Done — it holds.** Rām.4.039.021, Kosala in a mahājanapada
  roster. The first floor constraint on the core to survive contact with the text.
- Fetch a vulgate text to test the §2 hypothesis directly.
- Carry the *dīnāra* and Yavana corrections into any restatement of §12.
