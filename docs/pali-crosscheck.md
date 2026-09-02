# The Pali cross-check, and a corpus file that turned out not to be what the audit thought

**Date:** 2026-09-02 · **Phase:** 4 · **Status:** one encoded, one audit entry retracted

Two additions were attempted, in the order recommended: the free one first, then the expensive
one. The free one failed. The expensive one delivered more than it was asked for, and one
thing it delivered was not a date at all.

---

## 1. Retraction: the southern recension is not a second recension

`corpus-audit.md` recorded the GRETIL southern Rāmāyaṇa file as "a direct win", on the
grounds that §12's *southern vs northern recension divergence* constraint would stop being a
citation to someone else's collation and become computable from two files on disk. **It does
not, and the audit entry is withdrawn.**

`sa_vAlmIki-rAmAyaNa-southern-2.xml` covers the Ayodhyākāṇḍa only: 3,158 verses in 111
sargas, against the critical edition's 3,160 in 111. It carries its own `*` marker on 84
verses — which looked promising, since that is exactly the apparatus structure that made the
Mahābhārata's 66,177 excised lines so useful.

It is not that. Aligning every southern verse against its best-matching critical-edition verse:

```
                 n     median best-match Jaccard    orphans (<0.34)
plain         3,074              1.00                 2  (0.1%)
starred          84              1.00                 0  (0.0%)
```

**Every southern verse has a near-identical counterpart in the critical edition**, starred
ones included. The differences are word-division and orthography — `śeṣvān antarhitāyāṃ`
against `śeṣvānantarhitāyāṃ` — not content. This file is the constituted text with southern
readings, not an independent recension with its own additions, so it yields no labelled
lateness set and cannot promote the divergence constraint.

*(A parse check earned its keep on the way in: a first pattern that did not allow the `*`
silently dropped all 84 starred verses and reported a plausible-looking 2.7% deficit against
the critical edition. The completeness check caught it before any conclusion rested on it.)*

**Consequence.** The Rāmāyaṇa still has **no** apparatus of any kind, and the asymmetry the
audit noted stands: `archetypal: true|star` is populable for the Mahābhārata and not for the
Rāmāyaṇa. Given that the apparatus turned out to be the most useful single structure in the
corpus (`new-instruments.md`), that is a sharper loss than it looked.

---

## 2. The Dīgha-Nikāya

Fetched: the three PTS volumes in GRETIL's **annotated** form — `dighn{1,2,3}ou.htm`, 903
PTS pages. The plain-text versions were fetched first and discarded: they state that "all
annotations have been removed", which strips the page references, and a text with no citable
locus cannot satisfy G-1.

This is the only body of text the project can reach that is transmitted independently of
Sanskrit epic tradition, dated by an unrelated apparatus, and still full of the same
referents. Independence of dating chain is the design's own criterion for what an addition is
worth, and nothing else available scores as high.

### A parse rule that had to exist before any search was trusted

Searching raw pages for `potthaka`, "book", returns three hits. All three are the PTS editors
writing *Sīhaḷapotthake*, "in the Sinhalese manuscript". **Counting them would have produced
the exact claim the search was meant to test — that this tradition knows books — out of
nothing but apparatus.** Everything below a page's rule line is editorial and `tools/pali.py`
holds it separately; footnotes are searched only on request.

```
                       text   footnotes
potthaka (book)           0           3
```

### It replicates the writing horizon from an independent tradition

```
Dīgha-Nikāya, 903 PTS pages, text only
  lipi / lekhā as script      0
  potthaka (book)             0
  kahāpaṇa (coin)             0
  √likh                       2
```

Both √likh occurrences are one stock phrase — DN i.63 and DN i.250, *saṅkha-**likhitaṃ**
brahmacariyaṃ*, the holy life "polished like a conch-shell". **That is the same
scratch-and-polish sense the Rāmāyaṇa core uses eleven times and never leaves.** Two
traditions with no transmission in common, sharing a semantic stage.

**And the control here is of a better kind than the Rāmāyaṇa's.** The Brahmajāla and
Sāmaññaphala suttas enumerate the low arts a recluse abstains from — dozens of items — and at
DN i.11 and i.69 the list runs:

> *muddā, gaṇanā, saṃkhānaṃ, kāveyyaṃ, lokāyataṃ*
> finger-reckoning, counting, computation, poetry, Lokāyata

It enumerates the skills that sit next to writing and **stops short of writing itself.** A
narrative may omit anything; a list that aims at completeness over its domain and omits an
item is the enumerative control this project has been short of since the *mokṣa* row failed
for want of one.

### It corroborates the Pāṭaliputra argument from inside the transition

The single point of failure in the whole network is `e.044`, the attestation of
`ref.pataliputra-imperial`, which carries the pre-Common-Era ceiling for **both** epics off one
row the source scores 2 of 5. The epic argument is a silence: the epics name Girivraja and
never Pāṭaliputra.

The Dīgha-Nikāya shows the same distribution and dates the transition from within it:
**Rājagaha is the operative capital on 22 pages; Pāṭaliputta appears on 2, and only as a city
not yet built.** Within two PTS pages the same place is a village and then a future city:

> DN ii.86 — *Sunīdha-Vassakārā **Magadha-mahāmattā Pāṭaligāme nagaraṃ māpenti** Vajjīnaṃ
> paṭibāhāya* · Magadha's chief ministers building a fort at the **village** of Pāṭaligāma
>
> DN ii.88 — ***Pāṭaliputtassa** kho Ānanda tayo antarāyā bhavissanti* · the three dangers
> foretold for **Pāṭaliputta**

**Deliberately not encoded as an edge.** Everything the Dīgha-Nikāya can attest about that
referent is slacker than the Mauryan horizon already supplies, so an edge would add a node and
move nothing — the same law that made the Mahābhārata and the Atharvaveda slack. It is
recorded as a note on `ref.pataliputra-imperial`, because what it changes is confidence in the
warrant, not the arithmetic.

### What it did move — and the direction is the surprise

`ws.dighanikaya` was entered at **[400 BCE, 100 BCE]**, deliberately late at the ceiling so
that its absence claim would be as weak as possible. The solve returns:

```
ws.dighanikaya        [400 BCE, 230 BCE]     ceiling tightened by 130 years
ref.writing-practice  [400 BCE, 230 BCE]     floor raised from 750 BCE
```

The Pali text's own ceiling was tightened by its ignorance of writing, propagating through the
Aśokan attestation. **This is the first time a corpus addition in this project has tightened
anything at all** — and what it tightened was not an epic but the new text itself. A network
built to date Sanskrit epics dated a Pali collection as a side effect.

The epic brackets are unchanged and every minimum cut is still 1. Corroboration is not
redundancy: a second argument for the same conclusion, running through the same terminus,
does not raise a cut.

---

## 4. The Vinaya-Piṭaka: the scribe appears

The Dīgha-Nikāya established that the Pali tradition shares the Rāmāyaṇa's pre-literate
profile. The obvious next question is when *that* tradition acquires writing, and the answer
sits inside the same canon.

The Vinaya was fetched for its **genre**, not its content. A monastic legal code enumerates
trades, possessions and offences exhaustively, and enumerative lists are the scarce commodity
here: an absence argument is only as good as a source that aimed at completeness and omitted
the item anyway.

```
                              Dīgha-Nikāya      Vinaya
  lipi (script)                          0           0
  lekhaka (scribe)                       0         yes
  kahāpaṇa / māsaka / rūpiya       0 / 0 / 0   7 / 18 / 16
  √likh                                  2          20
```

**The decisive passage is enumerative, which is why it was worth going for.** Vin iv.8, a rule
against insulting speech, lists the trades — *naḷakāraṃ kumbhakāraṃ pesakāraṃ cammakāraṃ
nahāpitaṃ* as low, and ***muddikaṃ gaṇakaṃ lekhakaṃ*** — reckoner, calculator, **scribe** —
as high.

That is the *same slot* the Dīgha-Nikāya fills with *muddā, gaṇanā, saṃkhānaṃ* and no scribe.
One tradition, one language, one transmission, one list-type: in one collection the scribe is
absent, in the other he is a respectable profession. Cf. Vin i.77, Upāli's parents weighing
*lekhā* as a trade for their son, and Vin iii.76, where inciting a death **by writing** is an
offence.

**Two readings withdrawn on inspection**, both of which would have overstated the case.
*potthaka* at Vin i.306 and i.311 is a coarse cloth in a list of forbidden robes, not a book;
*avalekhanakaṭṭha* at Vin ii.141 and ii.222 is a latrine scraping-stick, not a stylus — the
scratch sense of √likh persisting beside the literate one, in the same volume. Neither is
counted.

**What it changes.** Encoded as `ws.vinaya` attesting `ref.writing-practice`, it is slack
against the Aśokan attestation, as every addition to this store has been. What it changes is
the warrant: the genre excuse for the Rāmāyaṇa's silence is now excluded **from inside a
single tradition** rather than across two.

**And the network entails an ordering it was never built to produce.** The Dīgha-Nikāya must
precede writing's emergence; the Vinaya attests it. So `DN ≤ writing ≤ Vinaya`. A network
assembled to date Sanskrit epics has issued a falsifiable claim about the relative order of two
Pali collections — the kind of output the project exists to generate, and the kind a Pali
scholar can shoot down.

## 5. Reproduction

```bash
uv run python tools/pali.py rājagah
uv run python tools/pali.py 'lipi|lekhā|potthak'          # measured silence
uv run python tools/pali.py 'muddā, gaṇanā'               # the enumerative control
uv run python tools/pali.py potthak --notes               # and why footnotes are held apart
uv run python tools/pali.py "lekhak|kahāpaṇ" --corpus vin  # the Vinaya contrast
```

Store: 85 nodes, 124 edges, 76 attested. Consistent.
Corpora on disk: six works, 31 MB, all gitignored. The Pali files are PTS/Dhammakāya
Foundation material under CC BY-SA 4.0, provided for scholarly use and not redistributed.
