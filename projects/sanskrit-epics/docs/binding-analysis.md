# What actually dates the Rāmāyaṇa core

**Two verse-checkable facts. Everything else in §12 is slack.**

```bash
uv run parvan influence store -t ram.core
```

```
leave-one-out over 54 edges, watching 1 node(s)

BINDING  2
  e.009  [attested/realia-floor]
      ram.core [750 BCE, 300 BCE] -> [1300 BCE, 300 BCE]
  e.043  [attested/absence]
      ram.core [750 BCE, 300 BCE] -> [750 BCE, 250 CE]

SLACK    52 edges move nothing
```

The two:

| | Constraint | Locus | §12 score |
|---|---|---|---|
| **Floor 750 BCE** | Kosala in a mahājanapada roster | Rām.4.039.021 | 4 |
| **Ceiling 300 BCE** | Pāṭaliputra occurs nowhere | 0 / 18,761 verses | **2** |

Remove the first and the floor falls to 1300 BCE. Remove the second and the ceiling jumps to
250 CE. Remove any of the other fifty-two and nothing happens at all.

---

## 1. F-6 now passes, and the reason is the finding

```
attested edges: 6 / 54

full solve      ram.core = [750 BCE, 300 BCE]
attested only   ram.core = [750 BCE, 300 BCE]      identical
```

The preregistration's central falsifier asks whether conclusions survive stripping every
`asserted` edge. For the core they do not merely survive — **they do not change**. All fifty
interpretive edges are non-binding.

Two turns ago F-6 fired maximally and the network said nothing without its testimony. What
closed the gap was not adding constraints but **checking four of them against the text**. Three
failed and moved to Bāla; the fourth held, and it turned out to be the one carrying the floor.

## 2. Every score-5 floor in §12 contributes nothing to the core

This is the sharpest result, and it is not a criticism of the scores — it is a criticism of
scoring alone as an instrument.

| §12 score-5 floor | Fate |
|---|---|
| Horses and spoked chariots | Floor 2100 BCE — dominated by Kosala. **Slack** |
| Iron weaponry | Floor 1300 BCE — dominated by Kosala. **Slack** |
| Post-Vedic grammar | Emergence unbounded below; supplies no floor. **Slack** |
| *Dīnāra* | Does not occur in the critical edition. **Absent** |

All four of the inventory's highest-confidence floors are inert. Meanwhile the core's ceiling —
the entire pre-CE half of its bracket — rests on a row scored **2**, the weakest in the table.

**A score measures how sure you are of a constraint. It says nothing about whether the
constraint does any work.** A certain floor at 2100 BCE excludes nothing that a merely-probable
floor at 750 BCE has not already excluded. The design flagged this axis-conflation on the first
read of the document; this is it, measured.

## 3. The fragility that follows

The core's bracket has no redundancy whatsoever. Each bound hangs on exactly one edge, and
there is no second path to either:

- **The floor** is Kosala's appearance in one verse. It survives because it is a
  mahājanapada roster rather than a description that could belong to a later book — but a
  single verse is a single verse.
- **The ceiling** is an argument from silence, scored 2, and it carries a **550-year** swing.
  Reject it and the core's ceiling moves to 250 CE.

So the honest statement of the Rāmāyaṇa core's date, from this evidence, is:

> **750–300 BCE, where the floor rests on one verse and the ceiling on one silence — and
> rejecting the silence widens the bracket to 750 BCE – 250 CE.**

That is a much less comfortable sentence than "c. 500–200 BCE", and it is what the evidence
supports.

## 4. An incidental cross-check that supports the document

Book 4's geography knows Indian mahājanapadas — Videha, Kāśi, Kosala, Magadha, Puṇḍra, Vaṅga
at Rām.4.039.021 — and **no** Greeks, Scythians, Pahlavas, Kāmbojas or Cīnas anywhere. Those
appear only in Bālakāṇḍa.

That is the profile of a genuinely pre-Hellenistic core geography, and it is an argument §12
does not make explicitly. It emerged from a search run to check something else.

## 5. What this changes about the method

The design proposed **influence ranking** (R-12) as a Phase 7 report. It arrived at Phase 3
because the store is small and the pass is a loop over `solve`. It should run continuously
rather than at the end, for a plain reason:

**Encoding effort should go to binding constraints, and most constraints do not bind.** Fifty-two
of fifty-four edges here could be deleted without changing a single reported bound. Promoting
any of them from `asserted` to `attested` would be careful work with no effect on the answer.

The two-column agenda the design wanted — *what to resolve* and *what to double-check* — is
therefore available now, and for this store it is very short:

1. **Double-check the Pāṭaliputra silence.** It is 550 years of the bracket, scored 2, and it
   is the single most consequential claim in the inventory.
2. **Find a second route to the core's floor.** One verse is not redundancy.
3. **Ignore the other fifty-two edges** until something makes one of them binding.
