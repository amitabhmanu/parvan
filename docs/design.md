# Parvan — design reference

The full requirements and design document (v0.1, 35 numbered requirements, six diagrams)
is published as an artifact:

**https://claude.ai/code/artifact/3233d750-370d-4fbb-be0f-9fddfa34d2a6**

Source synthesis this project derives from: [dating-sanskrit-epics.md](dating-sanskrit-epics.md),
especially §§11–12 (scored inventories), §13 (generalized procedure), §14 (network formalization).

Prior art ported rather than reinvented:

- **Dechter, Meiri & Pearl 1991** — the Simple Temporal Problem. Time points with difference
  constraints, solved by shortest-path closure; consistent iff no negative cycle.
- **Allen 1983** — interval algebra. `frames` is Allen's *contains*; `cites` is *before*.
- **OxCal** — anchored Bayesian chronological modelling. Phase 5 is essentially this applied
  to textual strata rather than radiocarbon samples.

---

## Decisions log

Decisions that could have gone otherwise. Revisit if the reasoning changes.

| ID | Decision | Rationale |
|---|---|---|
| D-1 | Nodes are passages; strata are a latent partition | Stratification is an output, not a prerequisite. Only the critical edition must precede the graph. |
| D-2 | Reify a referent only if it is an anchor or has degree ≥ 2 | Singly-attested referents cannot propagate. Holds the graph near 250–350 nodes. |
| D-3 | Correlation is modelled, never pruned | Deleting edges to simulate independence destroys the cycles that provide consistency checks. |
| D-4 | Git is the disagreement mechanism | The deliverable is contestable structure. A pull request is the unit of scholarly dispute. |
| D-5 | Interval stage precedes Bayesian stage | Deterministic propagation debugs the encoding before probability hides the bugs. |
| D-6 | Signed integer years, astronomical numbering | Year 0 = 1 BCE, so arithmetic never crosses a discontinuity. Hedges stored verbatim alongside. |
| D-7 | A seventh edge type, `grounds`, and a seventh gate, G-7 | `attests` caps an emergence from above and never floors it, so material referents were carrying hardcoded emergence intervals while their horizons sat inert. `grounds` supplies the missing floor; G-7 restricts it to `horizon` and `anchor`, because a claim about when something *began to exist* is material, and letting a text make it reintroduces the circularity G-4 prevents. |
| D-8 | Horizon intervals express **onset**, not duration | Grounding pins a referent's emergence to its horizon's interval, so a horizon must say when the thing began, not how long it lasted. Encoding `hor.mauryan-capital` as the imperial *phase* [-320, -180] made the Pāṭaliputra absence argument yield "predates 180 BCE" — the date Pāṭaliputra stopped being unremarkable to omit, which is not the claim. |

### Deferred

| Question | Decided at |
|---|---|
| Audience: personal exploration vs. tool offered to scholars (**O-4**) | Phase 2 gate |
| Harness investment: agent definitions, commands, hooks | After the solver works (Phase 3) |
| Defensible default ε, and whether it differs by edge type (**O-1**) | Phase 2, reported as a sensitivity |
