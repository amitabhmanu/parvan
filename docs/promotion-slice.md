# The promotion slice — asserted to attested

**Goal.** Take a handful of §12's realia edges to the critical edition, cite verses, and see
whether F-6 gets an answer. Manual, no agent: the point was to learn what an extraction
contract needs before writing one.

**Result.** Four edges promoted. F-6 now returns a real bracket instead of nothing. Along the
way the text contradicted two of §12's rows — one of them scored 5.

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
| `ram.core absent-from ref.pataliputra-imperial` | 0/18,761 verses | measured silence, re-runnable |

Note the discipline on iron: most `āyasa` hits in the core are metaphorical — *āyasaṃ hṛdayaṃ*,
"a heart of iron". The cited loci are material iron, a weapon and a sacrificial ladle. Finding
the string is not the same as verifying the claim, and this is the first thing the extraction
contract has to enforce.

---

## 2. Two of §12's rows do not survive contact with the critical edition

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

### Yavanas and Śakas — misattributed to the wrong stratum

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

### The likely common cause

Both rows look like **vulgate-based claims inside an inventory that otherwise presupposes the
critical edition**. The vulgate's Kiṣkindhākāṇḍa carries sargas the Baroda editors excised, and
*dīnāra* is exactly the kind of late lexical item such passages contain.

This is inference, not verification — confirming it needs a vulgate text, which we have not
fetched. But it is testable, and if right it means §12 violates §13's own step 0: *"Establish
the archetype … otherwise you assign dates to variants that entered in the twelfth century."*

---

## 3. F-6 now returns an answer

```
edges: 54 total | 50 asserted | 4 attested

after stripping every asserted edge:
  ram.core = [1300 BCE, 300 BCE]
  ram.bala = [330 BCE, unbounded]
```

The sentence F-6 exists to produce is finally writable:

> **The checkable evidence alone puts the Rāmāyaṇa core between 1300 BCE and 300 BCE, and
> Bālakāṇḍa after 330 BCE. Scholarly interpretation tightens the core's floor from 1300 BCE
> to 700 BCE.**

Four edges carry that: iron floors the core, the Pāṭaliputra silence ceilings it, and the
Yavana attestation floors Bāla. Everything else in the store is still testimony.

Note what this exposes. The core's **useful** floor — 700 BCE, from a fortified Ayodhyā — rests
on an `asserted` edge. The attested floor is 1300 BCE, which excludes almost nothing. So the
evidence that actually does the work on the floor side has not been checked yet.

---

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

- Promote `ref.fortified-ayodhya` — the constraint doing the real floor work. Harder than a
  word search: it needs judging descriptions of the city, not finding a term.
- Fetch a vulgate text to test the §2 hypothesis directly.
- Carry the *dīnāra* and Yavana corrections into any restatement of §12.
