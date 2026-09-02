# V-1 — the expressivity test

**Phase 2 gate.** Encode §12 of `dating-sanskrit-epics.md` — the Rāmāyaṇa inventory — and
check whether stage-1 propagation reproduces its stated result of a core at **c. 500–200 BCE**.

**Verdict: gate outcome 3.** The schema carries the argument. The stated result does not
follow from the stated table.

```
network   ram.core = [700 BCE, 300 BCE]
document  ram.core = [500 BCE, 200 BCE]
```

The intervals overlap on 500–300 BCE, but neither contains the other, and the divergence has
a different cause at each end.

Store: 51 nodes, 57 edges, 68 variables, 151 constraints. Consistent. Reproduce with

```bash
uv run python tools/encode_s12.py && uv run parvan solve store --epsilon 25
```

---

## 1. The floor: 700 BCE against 500 BCE

The network's floor on the core comes from one constraint — the core presupposes a fortified
Ayodhyā, whose emergence the archaeology places in the 7th century BCE.

Two separate things account for the 200-year gap.

**100 years is a century-boundary convention.** §3 states that "Ayodhyā yields no substantial
occupation before c. 7th c. BCE." The 7th century BCE runs 700–601 BCE, so emergence lies
somewhere in that window and the hard floor the constraint licenses is **700 BCE**. §12's
floors column rounds this to "c. 600 BCE" — the *late* end of the same window. Both are
defensible readings of the archaeology; only one is what the constraint formally supports.
This is a mundane finding, and exactly the sort formalization is for.

**The other 100 years has no source in §12 at all.** Nothing in the floors table yields
500 BCE. The nearest thing in the document is §4, which quotes Brockington's scheme — "core
c. 5th c. BCE" — from a different section and a different method. The stated floor is
imported, not derived.

## 2. The ceiling: 300 BCE against 200 BCE

This end is sharper. **§12's ceilings table contains exactly one pre-CE entry:**

> | Pāṭaliputra absent as imperial capital | Soft ceiling c. 300 BCE on the geographic frame | 2 |

Every other ceiling in the table is CE-dated. So the core's ceiling rests entirely on a single
argument from silence, scored 2 out of 5, about "the geographic frame" rather than the core.

The consequence is a cliff:

| Pāṭaliputra argument | Binding ceiling on `ram.core` |
|---|---|
| Accepted | **300 BCE** (the absence edge) |
| Rejected | **250 CE** (*Liudu jijing*, the next binding constraint) |

A 550-year swing turning on one score-2 row. **Nothing in the table produces 200 BCE**, and
no combination of table rows lands between 300 BCE and 250 CE.

That is the finding. Not that the document's answer is wrong — the consensus it reports may
well be right — but that **§12's result is not reconstructible from §12's evidence**, and the
one row holding the pre-CE ceiling up is the weakest kind of argument the document itself
warns against.

---

## 3. Was the schema lossy?

Gate outcome 2 would be "the schema could not carry the argument." It carried 33 of 37 rows.
The four it did not:

| Row | Score | Why not encoded | Would it move `ram.core`? |
|---|---|---|---|
| Southern vs northern recension divergence | 3 | Needs both recensions as work-states with differential containment. **Genuine expressivity gap.** | No — a relative marker |
| Verse comparing "the Buddha" to a thief | 2 | Constrains one verse, not the core; §12 does not localise it | No — per-passage |
| No Vedic attestation of Rāma Dāśarathi | 2 | Establishes only that the story is not Vedic; yields no interval | No |
| Astronomical dating of Rāma's birth | 1 | Encoded instead as a **test**, see §5 | No |

Only the first is a real gap in the schema, and it is a *relative* constraint that cannot move
an absolute bound. **The schema is not lossy in any way that explains the divergence.**

---

## 4. Two results that were not the point of the test

### F-6 fires maximally: the store contains no attested edge at all

```
edges: 57 total | 57 asserted | 0 attested
after stripping asserted: 0 edges remain
ram.core = [unbounded, unbounded]
```

The preregistration's most important falsifier asks: strip every `asserted`-tier edge and see
whether conclusions survive. Here **nothing** survives, because every edge is `asserted`.

This is not an encoding shortcut. §12 states its claims at the level of "Yavanas and Śakas in
the Kiṣkindhā geography" without giving a sarga or śloka, so no edge could honestly be tiered
`attested` from the document alone. The anchors and horizons are attested as *nodes* — the
inscriptions and excavations are real and dated — but every inference **connecting an artefact
to a text stratum is scholarly assertion**.

That makes the network, as it currently stands, a formalization of the literature rather than
of the evidence. Which is precisely what F-6 was written to detect.

**It also converts into a concrete Phase 4 task.** Phase 0 confirmed the critical editions are
machine-readable with pāda-level addressing. Every `realia-floor` edge in this store can be
promoted from `asserted` to `attested` by going to the text and citing the verse. That is the
single highest-value encoding work available, and it is now prioritized by evidence rather
than by intuition.

### ε does not matter here, and that is informative

```
eps=25   ram.core [700 BCE, 300 BCE]
eps=50   ram.core [700 BCE, 300 BCE]
eps=100  ram.core [700 BCE, 300 BCE]
```

Identical across the whole preregistered sweep. The reason: the constraints binding `ram.core`
are `presupposes` and `absent-from` edges, which carry no lag. No citation chain reaches it.

So this graph is **anchor-adjacent and shallow** — every conclusion is one or two hops from a
horizon or an inscription, and none is chain-mediated. That matches the sparsity prediction:
with one text, referents are hubs of degree one or two and propagation does little work.
ε only starts to matter once the corpus is deep enough to build chains, which is Phase 4.

---

## 5. What the solver caught along the way

**D-2 refused four referents on the first pass.** `karma-rebirth-moksa`, `lokayata-school`,
`caste-hardening` and `bharata-war-narrative` each had degree 1 in a Rāmāyaṇa-only store — one
text touching each, so nothing to propagate. The rule was right and the encoding was thin: the
document names the other sources (the Upaniṣads, Manu, the Mahābhārata's Cārvāka cameo), and
adding them satisfied D-2 honestly rather than by weakening it.

**A real bug in lag handling.** `edge.lag_min_years or epsilon` silently treated an explicit
`0` as unset, so zero-lag absence edges were being given ε = 25. Caught by a solver test whose
expected answer was known by hand. `None` now means "inherit ε" and is distinct from a
declared zero.

**Astronomical dating is a negative cycle.** §12 scores it 1 because it "contradicts horse,
iron, urbanism constraints." That verdict is now a test: pin the core to 5114 BCE, keep the
iron floor already in the store for other reasons, and the network reports infeasible with a
witness path. Rejecting it requires no argument about ephemeris software.

---

## 6. Gate decision

**Proceed.** The schema expresses real scholarly argument, the solver is correct on
hand-checkable fixtures, and the one divergence is a property of the source rather than of the
encoding.

Carried forward:

1. **Promote `realia-floor` edges from `asserted` to `attested`** using verse loci from the
   critical edition. F-6 says this is where the value is.
2. **Model recensions as work-states** so the southern/northern divergence becomes expressible.
3. **Report the Pāṭaliputra sensitivity** wherever a Rāmāyaṇa ceiling is quoted. A 550-year
   swing on one score-2 row is the kind of dependency that should never be invisible.
4. **Resolve the Ayodhyā century convention** — decide whether a "7th c. BCE" horizon floors at
   700 or 600, apply it consistently, and record the choice.
