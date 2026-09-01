"""Solver tests on hand-built fixtures with known answers.

These build Store objects directly rather than going through the loader, so solver semantics
can be tested independently of the gates - including at epsilon = 0, which the loader refuses
(R-5) but which the solver must still handle correctly so the refusal has something to
protect against.
"""

from __future__ import annotations

from parvan.loader import Store
from parvan.model import Edge, Interval, Node, Provenance
from parvan.stp import emergence_var, solve

PROV = Provenance(tier="attested", locus="test")


def anchor(node_id: str, floor: int, ceiling: int) -> Node:
    return Node(
        id=node_id,
        kind="anchor",
        interval=Interval(floor=floor, ceiling=ceiling),
        provenance=PROV,
    )


def stratum(node_id: str) -> Node:
    return Node(id=node_id, kind="stratum")


def referent(node_id: str, **kw) -> Node:
    return Node(id=node_id, kind="referent", provenance=PROV, **kw)


def edge(edge_id: str, etype: str, src: str, dst: str, **kw) -> Edge:
    return Edge(id=edge_id, type=etype, src=src, dst=dst, method="realia-floor",
                provenance=PROV, **kw)


def mkstore(nodes: list[Node], edges: list[Edge]) -> Store:
    store = Store()
    for n in nodes:
        store.nodes[n.id] = n
    for e in edges:
        store.edges[e.id] = e
    return store


# --- directed cycles are errors ---------------------------------------------------


def test_directed_cycle_of_citations_is_infeasible() -> None:
    """A cites B cites C cites A cannot all hold. This is the Manu circularity in its
    purest form, and detecting it is the diagnostic doing real work."""
    store = mkstore(
        [stratum("a"), stratum("b"), stratum("c")],
        [
            edge("e1", "cites", "a", "b", lag_min_years=25),
            edge("e2", "cites", "b", "c", lag_min_years=25),
            edge("e3", "cites", "c", "a", lag_min_years=25),
        ],
    )
    sol = solve(store)
    assert not sol.consistent
    assert sol.negative_cycle


def test_witness_path_names_every_edge_involved() -> None:
    """R-8: an inconsistency has to be actionable, which means naming the constraints."""
    store = mkstore(
        [stratum("a"), stratum("b")],
        [
            edge("e.forward", "cites", "a", "b", lag_min_years=50),
            edge("e.backward", "cites", "b", "a", lag_min_years=50),
        ],
    )
    sol = solve(store)
    assert not sol.consistent
    witness = sol.witness()
    assert "e.forward" in witness and "e.backward" in witness
    assert "cycle weight" in witness
    ids = {c.origin for c in sol.negative_cycle}
    assert ids == {"e.forward", "e.backward"}


def test_impossible_absolute_bounds_are_infeasible() -> None:
    store = mkstore(
        [anchor("early", -300, -290), anchor("late", 400, 410)],
        [edge("e1", "cites", "early", "late", lag_min_years=25)],
    )
    # 'early' cites 'late', so early must postdate 410 + 25 -- contradicting its own ceiling.
    sol = solve(store)
    assert not sol.consistent


# --- undirected cycles are the desired case ---------------------------------------


def test_two_anchors_meeting_at_one_node_is_consistent() -> None:
    """The convergence argument: two independent routes arriving at the same node form an
    UNDIRECTED cycle. It must not be reported as inconsistency - the opposite outcome from
    a directed cycle, and the design document conflates the two."""
    store = mkstore(
        [anchor("anc.early", -200, -190), anchor("anc.late", -100, -90), referent("ref.x")],
        [
            edge("e1", "attests", "anc.early", "ref.x"),
            edge("e2", "attests", "anc.late", "ref.x"),
        ],
    )
    sol = solve(store)
    assert sol.consistent
    assert sol.bounds[emergence_var("ref.x")].ceiling == -190


def test_only_the_earliest_attester_moves_the_bound() -> None:
    """Interval tightening is an order-statistic problem: a referent's emergence ceiling is
    set by its EARLIEST attester, so adding later ones changes nothing. This is why
    tightening scales as log T in corpus size and testability scales linearly."""
    base = [anchor("anc.early", -200, -190), referent("ref.x")]
    one = solve(mkstore(base, [edge("e1", "attests", "anc.early", "ref.x")]))

    many = solve(
        mkstore(
            base + [anchor(f"anc.{i}", -100 + i, -90 + i) for i in range(5)],
            [edge("e1", "attests", "anc.early", "ref.x")]
            + [edge(f"e{i + 2}", "attests", f"anc.{i}", "ref.x") for i in range(5)],
        )
    )
    assert many.consistent
    assert (
        many.bounds[emergence_var("ref.x")].ceiling
        == one.bounds[emergence_var("ref.x")].ceiling
    )


# --- transmission lag is what makes chain depth pay -------------------------------


def _chain() -> tuple[list[Node], list[Edge]]:
    nodes = [anchor("anc", -300, -300), stratum("c"), stratum("b"), stratum("a")]
    edges = [
        edge("e.c", "cites", "c", "anc"),
        edge("e.b", "cites", "b", "c"),
        edge("e.a", "cites", "a", "b"),
    ]
    return nodes, edges


def test_chain_transmits_nothing_at_zero_lag() -> None:
    nodes, edges = _chain()
    sol = solve(mkstore(nodes, edges), epsilon=0)
    assert sol.consistent
    assert sol.bounds["c"].floor == -300
    assert sol.bounds["b"].floor == -300
    assert sol.bounds["a"].floor == -300


def test_chain_floors_step_with_lag() -> None:
    """Figure 4 of the design: the same chain at epsilon = 25 converts corpus depth into
    precision. Without lag, long chains are decorative."""
    nodes, edges = _chain()
    sol = solve(mkstore(nodes, edges), epsilon=25)
    assert sol.consistent
    assert sol.bounds["c"].floor == -275
    assert sol.bounds["b"].floor == -250
    assert sol.bounds["a"].floor == -225


# --- referent semantics -----------------------------------------------------------


def test_emergence_is_unbounded_below_without_an_absence_edge() -> None:
    """Attestation caps emergence from above and never floors it. Absence edges are the only
    thing that ever supplies a floor - which is why corpus density matters (R-4)."""
    store = mkstore(
        [anchor("anc", -200, -190), referent("ref.x")],
        [edge("e1", "attests", "anc", "ref.x")],
    )
    sol = solve(store)
    assert sol.consistent
    assert sol.bounds[emergence_var("ref.x")].floor == float("-inf")


def test_absence_edge_supplies_the_missing_floor() -> None:
    store = mkstore(
        [anchor("anc", -200, -190), anchor("silent", -500, -500), referent("ref.x")],
        [
            edge("e1", "attests", "anc", "ref.x"),
            edge("e2", "absent-from", "silent", "ref.x", lag_min_years=0),
        ],
    )
    sol = solve(store)
    assert sol.consistent
    bounds = sol.bounds[emergence_var("ref.x")]
    assert bounds.floor == -500
    assert bounds.ceiling == -190


def test_presupposition_floors_the_stratum_from_the_referent() -> None:
    store = mkstore(
        [
            anchor("anc", -200, -190),
            anchor("silent", -500, -500),
            referent("ref.x"),
            stratum("str.y"),
        ],
        [
            edge("e1", "attests", "anc", "ref.x"),
            edge("e2", "absent-from", "silent", "ref.x", lag_min_years=0),
            edge("e3", "presupposes", "str.y", "ref.x"),
        ],
    )
    sol = solve(store)
    assert sol.consistent
    # The stratum inherits the referent's floor: it cannot predate what it presupposes.
    assert sol.bounds["str.y"].floor == -500


# --- probabilistic containment is deferred, not silently applied ------------------


def test_low_confidence_containment_is_skipped_and_reported() -> None:
    store = mkstore(
        [anchor("ws", 200, 300), stratum("str.y")],
        [edge("e1", "contains", "ws", "str.y", confidence=0.35)],
    )
    sol = solve(store, contains_threshold=0.5)
    assert sol.consistent
    assert any("e1" in s for s in sol.skipped)
    assert sol.bounds["str.y"].ceiling == float("inf")


# --- the document's score-1 verdict, as a computation ------------------------------


def test_astronomical_date_for_rama_is_infeasible_against_the_iron_floor() -> None:
    """Section 12 scores astronomical dating of Rama's birth at 1, on the grounds that it
    "contradicts horse, iron, urbanism constraints". That verdict is a negative cycle: a
    narrative saturated with iron weaponry cannot depict 5114 BCE, because iron metallurgy
    does not reach South Asia until roughly 1300-1200 BCE.

    Rejecting it needs no argument about ephemeris software - only two constraints that were
    already in the store for other reasons.
    """
    store = mkstore(
        [
            Node(id="ram.core", kind="stratum", interval=Interval(floor=-5114, ceiling=-5114)),
            referent("ref.iron", emergence=Interval(floor=-1300, ceiling=-1200)),
            Node(
                id="hor.iron",
                kind="horizon",
                interval=Interval(floor=-1300, ceiling=-1200),
                provenance=PROV,
            ),
        ],
        [
            edge("e.iron", "presupposes", "ram.core", "ref.iron"),
            edge("e.hor", "attests", "hor.iron", "ref.iron"),
        ],
    )
    sol = solve(store)
    assert not sol.consistent
    assert "e.iron" in {c.origin for c in sol.negative_cycle} | {
        c.origin for c in sol.constraints
    }
    assert "cycle weight" in sol.witness()


# --- grounding: the missing half of attestation -----------------------------------


def test_grounds_floors_an_emergence_where_attests_cannot() -> None:
    """Attestation caps from above and never floors. Without `grounds`, a material referent
    contributes no floor to anything that presupposes it - which is how thirteen horizon
    nodes came to be inert while their floors sat hardcoded in the encoder."""
    nodes = [
        Node(id="hor.iron", kind="horizon", interval=Interval(floor=-1300, ceiling=-1200),
             provenance=PROV),
        referent("ref.iron"),
        stratum("str.epic"),
    ]
    attest_only = mkstore(nodes, [
        edge("e1", "attests", "hor.iron", "ref.iron"),
        edge("e2", "presupposes", "str.epic", "ref.iron"),
    ])
    sol = solve(attest_only)
    assert sol.consistent
    assert sol.bounds["str.epic"].floor == float("-inf")

    grounded = mkstore(nodes, [
        edge("e1", "attests", "hor.iron", "ref.iron"),
        edge("e3", "grounds", "hor.iron", "ref.iron"),
        edge("e2", "presupposes", "str.epic", "ref.iron"),
    ])
    sol = solve(grounded)
    assert sol.consistent
    assert sol.bounds["str.epic"].floor == -1300


def test_grounding_makes_the_anchor_load_bearing() -> None:
    """The point of the change: deleting a horizon must now move what it supports."""
    nodes = [
        Node(id="hor.iron", kind="horizon", interval=Interval(floor=-1300, ceiling=-1200),
             provenance=PROV),
        referent("ref.iron"),
        stratum("str.epic"),
    ]
    edges = [
        edge("e1", "attests", "hor.iron", "ref.iron"),
        edge("e3", "grounds", "hor.iron", "ref.iron"),
        edge("e2", "presupposes", "str.epic", "ref.iron"),
    ]
    with_anchor = solve(mkstore(nodes, edges))
    without = solve(mkstore(nodes[1:], [e for e in edges if e.src != "hor.iron"]))
    assert with_anchor.bounds["str.epic"].floor == -1300
    assert without.bounds["str.epic"].floor == float("-inf")
