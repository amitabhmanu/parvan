"""Stage-1 solver: the Simple Temporal Problem (Dechter, Meiri & Pearl 1991).

Every constraint reduces to a difference inequality ``X_dst - X_src <= w``, which is an edge
``src -> dst`` of weight ``w`` in a distance graph. Shortest-path closure over that graph
yields the tightest bounds the constraints support, and the system is consistent **iff the
distance graph has no negative cycle**. That is the whole method; the rest is bookkeeping.

Two facts about this formulation are worth stating because the design document gets them
subtly wrong:

* Order-independence does not need acyclicity. Shortest-path closure is a monotone operator
  on a finite structure, so the fixpoint is unique regardless of update order. Acyclicity
  buys single-pass convergence, not uniqueness.
* A **directed** cycle of strict edges is unsatisfiable and signals an error. An
  **undirected** cycle - two independent routes from different anchors meeting at one node -
  is the desired case, and is what the convergence argument actually means. Only the first
  produces a negative cycle here.

Referents carry two variables, ``#emergence`` and ``#attestation``, because first attestation
caps emergence from above and never bounds it below (R-4).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .loader import Store

SOLVER_VERSION = "stp/0.1.0"

# The reference point. Every absolute bound is expressed against it, and it sits at year 0
# in astronomical numbering (D-6).
ORIGIN = "__origin__"

INF = math.inf


@dataclass(frozen=True)
class Constraint:
    """``X_dst - X_src <= weight``, i.e. a distance-graph edge ``src -> dst``."""

    src: str
    dst: str
    weight: float
    origin: str  # edge or node id this came from
    why: str


@dataclass
class Bounds:
    floor: float
    ceiling: float

    @property
    def width(self) -> float:
        return self.ceiling - self.floor

    @property
    def unbounded(self) -> bool:
        return self.floor == -INF or self.ceiling == INF


@dataclass
class Solution:
    consistent: bool
    bounds: dict[str, Bounds] = field(default_factory=dict)
    negative_cycle: list[Constraint] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def witness(self) -> str:
        """Human-readable negative cycle. R-8 requires this to name every edge involved."""
        if not self.negative_cycle:
            return ""
        lines = ["Negative cycle - these constraints cannot all hold:"]
        total = 0.0
        for c in self.negative_cycle:
            total += c.weight
            lines.append(f"    {c.src}  ->  {c.dst}   w={c.weight:+g}   [{c.origin}] {c.why}")
        lines.append(f"    cycle weight = {total:+g}  (must be >= 0 for consistency)")
        return "\n".join(lines)


def emergence_var(node_id: str) -> str:
    return f"{node_id}#emergence"


def attestation_var(node_id: str) -> str:
    return f"{node_id}#attestation"


def date_var(store: Store, node_id: str) -> str:
    """The variable standing for a node's date. Referents resolve to their emergence."""
    node = store.nodes.get(node_id)
    if node is not None and node.kind == "referent":
        return emergence_var(node_id)
    return node_id


def build(
    store: Store, *, epsilon: int = 25, contains_threshold: float = 0.5
) -> tuple[list[Constraint], list[str], list[str]]:
    """Translate a store into difference constraints.

    ``epsilon`` is the default minimum transmission lag for ordering edges that do not
    declare their own (R-5, O-1). It is never chosen post hoc: the preregistration requires
    reporting at several values.
    """
    cons: list[Constraint] = []
    variables: set[str] = {ORIGIN}
    skipped: list[str] = []

    # --- absolute bounds from node intervals ---------------------------------------
    for node in store.nodes.values():
        if node.kind == "referent":
            e, a = emergence_var(node.id), attestation_var(node.id)
            variables |= {e, a}
            _absolute(cons, e, node.emergence.floor, node.emergence.ceiling, node.id, "emergence")
            _absolute(
                cons, a, node.attestation.floor, node.attestation.ceiling, node.id, "attestation"
            )
            # R-4: emergence precedes attestation. Attestation caps it; nothing floors it.
            cons.append(
                Constraint(a, e, 0.0, node.id, "emergence precedes attestation (R-4)")
            )
        else:
            variables.add(node.id)
            _absolute(cons, node.id, node.interval.floor, node.interval.ceiling, node.id, "interval")

    # --- ordering from edges --------------------------------------------------------
    for edge in store.edges.values():
        src_node = store.nodes[edge.src]
        dst_node = store.nodes[edge.dst]
        # `is None` rather than falsiness: an explicit zero is a real declaration on an
        # absence edge, not an absent one.
        lag = epsilon if edge.lag_min_years is None else edge.lag_min_years

        if edge.type == "presupposes":
            # The stratum postdates the referent's emergence.
            s, r = date_var(store, edge.src), emergence_var(edge.dst)
            cons.append(Constraint(s, r, 0.0, edge.id, f"{edge.src} presupposes {edge.dst}"))

        elif edge.type == "attests":
            # The referent had emerged by the attester's date.
            x, r = date_var(store, edge.src), emergence_var(edge.dst)
            cons.append(Constraint(x, r, 0.0, edge.id, f"{edge.src} attests {edge.dst}"))
            # The attestation point is no later than its attester.
            cons.append(
                Constraint(
                    x,
                    attestation_var(edge.dst),
                    0.0,
                    edge.id,
                    f"{edge.dst} attested by {edge.src}",
                )
            )

        elif edge.type == "grounds":
            # The referent did not exist before the horizon: X_ref^e >= X_horizon.
            # This is the only edge that floors an emergence from material evidence, and
            # it is what makes an anchor load-bearing rather than ornamental.
            h, r = date_var(store, edge.src), emergence_var(edge.dst)
            cons.append(
                Constraint(r, h, 0.0, edge.id, f"{edge.dst} not before {edge.src}")
            )

        elif edge.type == "absent-from":
            # The only method that ever floors a concept referent: a source that should
            # mention it and does not.
            a, r = date_var(store, edge.src), emergence_var(edge.dst)
            cons.append(
                Constraint(r, a, float(lag), edge.id, f"{edge.dst} absent from {edge.src}")
            )

        elif edge.type in ("cites", "frames"):
            # A postdates B by at least the transmission lag.
            a, b = date_var(store, edge.src), date_var(store, edge.dst)
            cons.append(
                Constraint(a, b, -float(lag), edge.id, f"{edge.src} {edge.type} {edge.dst} (e={lag})")
            )

        elif edge.type == "contains":
            # Stage 1 cannot express probabilistic membership, so apply it as hard only
            # above the threshold and record what was dropped.
            if edge.confidence < contains_threshold:
                skipped.append(
                    f"{edge.id}: contains p={edge.confidence} below threshold "
                    f"{contains_threshold}; deferred to the Bayesian layer"
                )
                continue
            w, s = date_var(store, edge.src), date_var(store, edge.dst)
            cons.append(
                Constraint(w, s, 0.0, edge.id, f"{edge.src} contains {edge.dst}")
            )

        del src_node, dst_node

    return cons, sorted(variables), skipped


def _absolute(
    cons: list[Constraint],
    var: str,
    floor: int | None,
    ceiling: int | None,
    origin: str,
    label: str,
) -> None:
    if ceiling is not None:
        cons.append(Constraint(ORIGIN, var, float(ceiling), origin, f"{label} ceiling {ceiling}"))
    if floor is not None:
        cons.append(Constraint(var, ORIGIN, -float(floor), origin, f"{label} floor {floor}"))


def solve(store: Store, *, epsilon: int = 25, contains_threshold: float = 0.5) -> Solution:
    cons, variables, skipped = build(
        store, epsilon=epsilon, contains_threshold=contains_threshold
    )
    sol = Solution(
        consistent=True, constraints=cons, variables=variables, skipped=skipped
    )

    cycle = _negative_cycle(cons, variables)
    if cycle:
        sol.consistent = False
        sol.negative_cycle = cycle
        return sol

    sol.bounds = _minimal_network(cons, variables)
    return sol


def _negative_cycle(cons: list[Constraint], variables: list[str]) -> list[Constraint]:
    """Bellman-Ford from a virtual source reaching every variable at weight 0.

    The virtual source makes every variable reachable, so any negative cycle anywhere in the
    graph is found - not only those reachable from an arbitrary start.
    """
    dist: dict[str, float] = {v: 0.0 for v in variables}
    pred: dict[str, Constraint | None] = {v: None for v in variables}

    updated_var: str | None = None
    for i in range(len(variables)):
        updated_var = None
        for c in cons:
            if dist[c.src] + c.weight < dist[c.dst] - 1e-9:
                dist[c.dst] = dist[c.src] + c.weight
                pred[c.dst] = c
                updated_var = c.dst
        if updated_var is None:
            return []

    if updated_var is None:
        return []

    # Walk back |V| steps to land inside the cycle, then walk the cycle itself.
    node = updated_var
    for _ in range(len(variables)):
        edge = pred[node]
        if edge is None:
            return []
        node = edge.src

    cycle: list[Constraint] = []
    cursor = node
    while True:
        edge = pred[cursor]
        if edge is None:
            break
        cycle.append(edge)
        cursor = edge.src
        if cursor == node:
            break
    cycle.reverse()
    return cycle


def _minimal_network(cons: list[Constraint], variables: list[str]) -> dict[str, Bounds]:
    """Floyd-Warshall closure, then read bounds off the distances to and from the origin.

    With ``X_origin`` pinned at 0: ``X_i <= d(origin, i)`` and ``X_i >= -d(i, origin)``.
    """
    idx = {v: i for i, v in enumerate(variables)}
    n = len(variables)
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0.0
    for c in cons:
        i, j = idx[c.src], idx[c.dst]
        if c.weight < d[i][j]:
            d[i][j] = c.weight

    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue
            di = d[i]
            for j in range(n):
                if dk[j] == INF:
                    continue
                alt = dik + dk[j]
                if alt < di[j]:
                    di[j] = alt

    o = idx[ORIGIN]
    out: dict[str, Bounds] = {}
    for v in variables:
        if v == ORIGIN:
            continue
        i = idx[v]
        ceiling = d[o][i]
        floor = -d[i][o] if d[i][o] != INF else -INF
        out[v] = Bounds(floor=floor, ceiling=ceiling)
    return out


def fmt_year(y: float) -> str:
    """Astronomical numbering to a readable era label."""
    if y == INF:
        return "unbounded"
    if y == -INF:
        return "unbounded"
    y = int(round(y))
    return f"{abs(y)} {'BCE' if y < 0 else 'CE'}" if y != 0 else "1 BCE"


def fmt_bounds(b: Bounds) -> str:
    lo = "unbounded" if b.floor == -INF else fmt_year(b.floor)
    hi = "unbounded" if b.ceiling == INF else fmt_year(b.ceiling)
    return f"[{lo}, {hi}]"


# ---------------------------------------------------------------------------------------
# Bound support: how redundantly is a bound held up?
# ---------------------------------------------------------------------------------------
# Leave-one-out cannot answer this. Remove either edge of a two-route bound and nothing
# moves, so both report as slack - the better-supported a bound is, the less important its
# supports appear. That is backwards.
#
# By Menger's theorem the minimum number of constraints whose joint removal moves a bound
# equals the maximum number of edge-disjoint paths realising it. So we count routes: find a
# shortest path that realises the bound, delete it, and see whether the bound survives.


def _shortest_path(
    cons: list[Constraint], variables: list[str], src: str, dst: str
) -> tuple[float, list[Constraint]]:
    """Bellman-Ford with predecessors. Returns (distance, the path's constraints)."""
    dist: dict[str, float] = {v: INF for v in variables}
    pred: dict[str, Constraint | None] = {v: None for v in variables}
    dist[src] = 0.0

    for _ in range(len(variables) - 1):
        changed = False
        for c in cons:
            if dist[c.src] != INF and dist[c.src] + c.weight < dist[c.dst] - 1e-9:
                dist[c.dst] = dist[c.src] + c.weight
                pred[c.dst] = c
                changed = True
        if not changed:
            break

    if dist[dst] == INF:
        return INF, []

    path: list[Constraint] = []
    seen: set[str] = set()
    cursor = dst
    while cursor != src:
        edge = pred[cursor]
        if edge is None or cursor in seen:
            break
        seen.add(cursor)
        path.append(edge)
        cursor = edge.src
    path.reverse()
    return dist[dst], path


def bound_support(
    store: Store,
    target: str,
    side: str = "ceiling",
    *,
    epsilon: int = 25,
    contains_threshold: float = 0.5,
    max_routes: int = 12,
) -> list[list[Constraint]]:
    """Edge-disjoint routes holding up one bound of ``target``.

    ``len(result)`` is the minimum cut: how many constraints must fail together before the
    bound moves. 1 means a single point of failure; 0 means the bound is unbounded already.
    """
    cons, variables, _ = build(store, epsilon=epsilon, contains_threshold=contains_threshold)
    var = date_var(store, target)
    if var not in variables:
        return []

    # X_i <= d(origin, i) is the ceiling; X_i >= -d(i, origin) is the floor.
    src, dst = (ORIGIN, var) if side == "ceiling" else (var, ORIGIN)

    baseline, _ = _shortest_path(cons, variables, src, dst)
    if baseline == INF:
        return []

    routes: list[list[Constraint]] = []
    live = list(cons)
    for _ in range(max_routes):
        dist, path = _shortest_path(live, variables, src, dst)
        if dist != baseline or not path:
            break
        routes.append(path)
        drop = set(map(id, path))
        live = [c for c in live if id(c) not in drop]
    return routes
