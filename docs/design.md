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

### Deferred

| Question | Decided at |
|---|---|
| Audience: personal exploration vs. tool offered to scholars (**O-4**) | Phase 2 gate |
| Harness investment: agent definitions, commands, hooks | After the solver works (Phase 3) |
| Defensible default ε, and whether it differs by edge type (**O-1**) | Phase 2, reported as a sensitivity |
