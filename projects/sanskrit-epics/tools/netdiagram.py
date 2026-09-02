"""Render the whole constraint network as a layered SVG.

    uv run python tools/netdiagram.py > network.svg

The layout is not decorative - it is the argument. Every node sits in the column its KIND
puts it in, and evidence flows left to right:

    external evidence  ->  referents  ->  texts
    (dated by excavation,   (institutions,   (the strata whose
     coin, inscription)      concepts)        dates are the question)

So kind is encoded by position, not by colour, which leaves colour free to carry the thing
this project actually exists to separate: whether a constraint is attested to a resolvable
locus or merely asserted by a scholar.

Colours come from the host page's CSS custom properties, so the figure follows the reader's
light or dark theme instead of carrying its own.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT.parents[1] / "src"))

from parvan.loader import load  # noqa: E402
from parvan.stp import bound_support  # noqa: E402

HEADLINES = ("ram.core", "ws.mbh.core")

# Ordering edges between texts, as opposed to evidential edges into referents. Drawn dashed:
# they say "A is later than B" rather than "this evidence bounds that concept".
ORDERING = frozenset(("cites", "frames", "contains"))

COL_OF = {
    "anchor": 0, "horizon": 0,
    "referent": 1,
    "stratum": 2, "work-state": 2,
}

W, PAD_T, PAD_B = 1132, 96, 34
PITCH, BOXH = 26, 19
COL_X = (235, 560, 838)           # right edge / centre / left edge of each column
CHAR_W, FONT = 5.9, 11


def short(node) -> str:
    """Drop the id prefix; it is redundant once the column says what kind it is."""
    i = node.id
    for p in ("ref.", "hor.", "anc.", "ws.", "ram."):
        if i.startswith(p):
            return i[len(p):] if p != "ram." else "Rām " + i[len(p):]
    return i


def order_columns(nodes, edges):
    """Barycentre sweeps: put each node near the mean height of its neighbours."""
    cols = [[n for n in nodes if COL_OF[n.kind] == c] for c in range(3)]
    for c in cols:
        c.sort(key=lambda n: (n.kind, n.id))
    pos = {n.id: i for c in cols for i, n in enumerate(c)}
    nbr: dict[str, list[str]] = {n.id: [] for n in nodes}
    for e in edges:
        nbr[e.src].append(e.dst)
        nbr[e.dst].append(e.src)

    for sweep in range(24):
        order = (1, 0, 2) if sweep % 2 else (1, 2, 0)
        for ci in order:
            col = cols[ci]
            keyed = []
            for n in col:
                out = [pos[m] for m in nbr[n.id] if COL_OF[nodes_by[m].kind] != ci]
                keyed.append((sum(out) / len(out) if out else pos[n.id], n))
            keyed.sort(key=lambda kv: kv[0])
            cols[ci] = [n for _, n in keyed]
            for i, n in enumerate(cols[ci]):
                pos[n.id] = i
    return cols


def main() -> None:
    store = load(PROJECT / "store")
    global nodes_by
    nodes_by = store.nodes
    nodes = list(store.nodes.values())
    edges = list(store.edges.values())

    critical: set[str] = set()
    for target in HEADLINES:
        for side in ("floor", "ceiling"):
            for route in bound_support(store, target, side):
                critical |= {c.origin for c in route}

    cols = order_columns(nodes, edges)
    tallest = max(len(c) for c in cols)
    height = PAD_T + tallest * PITCH + PAD_B

    xy: dict[str, tuple[float, float, float]] = {}   # id -> (left, right, cy)
    for ci, col in enumerate(cols):
        top = PAD_T + (tallest - len(col)) * PITCH / 2
        for i, n in enumerate(col):
            cy = top + i * PITCH + BOXH / 2
            w = max(46, len(short(n)) * CHAR_W + 15)
            if ci == 0:
                left, right = COL_X[0] - w, COL_X[0]
            elif ci == 1:
                left, right = COL_X[1] - w / 2, COL_X[1] + w / 2
            else:
                left, right = COL_X[2], COL_X[2] + w
            xy[n.id] = (left, right, cy)

    out: list[str] = [
        f'<svg viewBox="0 0 {W} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="IBM Plex Sans, system-ui, sans-serif" role="img" '
        f'aria-label="The complete Parvan constraint network: {len(nodes)} nodes and '
        f'{len(edges)} edges in three tiers.">'
    ]

    # --- column headings -------------------------------------------------------
    heads = (
        (COL_X[0], "end", "EXTERNAL EVIDENCE", "coins · inscriptions · excavation"),
        (COL_X[1], "middle", "REFERENTS", "institutions, concepts, events"),
        (COL_X[2], "start", "TEXTS", "strata whose dates are the question"),
    )
    for x, anchor, title, sub in heads:
        out.append(f'<text x="{x}" y="34" text-anchor="{anchor}" font-size="11.5" '
                   f'font-weight="600" letter-spacing="1.4" fill="currentColor">{title}</text>')
        out.append(f'<text x="{x}" y="52" text-anchor="{anchor}" font-size="10.5" '
                   f'fill="currentColor" opacity=".5">{sub}</text>')
    for x in (398, 700):
        out.append(f'<line x1="{x}" y1="66" x2="{x}" y2="{height - 20}" '
                   f'stroke="currentColor" stroke-width="1" opacity=".1"/>')

    # --- edges, slack first so the load-bearing ones land on top ----------------
    def path(e) -> str:
        sl, sr, sy = xy[e.src]
        dl, dr, dy = xy[e.dst]
        same = COL_OF[store.nodes[e.src].kind] == COL_OF[store.nodes[e.dst].kind]
        if same:
            # Text-to-text ordering inside one column. Bow out to the right of the column
            # rather than running back through the nodes themselves, which is what made the
            # first render look tangled where it was merely dense.
            bow = 30 + min(96.0, abs(dy - sy) * 0.36)
            return (f"M{sr:.1f},{sy:.1f}C{sr + bow:.1f},{sy:.1f} "
                    f"{dr + bow:.1f},{dy:.1f} {dr:.1f},{dy:.1f}")
        x1, x2 = (sr, dl) if sr <= dl else (sl, dr)
        dx = max(34.0, abs(x2 - x1) * 0.42)
        sgn = 1 if x2 >= x1 else -1
        return f"M{x1:.1f},{sy:.1f}C{x1 + sgn * dx:.1f},{sy:.1f} {x2 - sgn * dx:.1f},{dy:.1f} {x2:.1f},{dy:.1f}"

    for e in sorted(edges, key=lambda e: e.id in critical):
        hot = e.id in critical
        attested = e.provenance is not None and e.provenance.tier == "attested"
        stroke = "var(--fails)" if hot else ("var(--holds)" if attested else "currentColor")
        op = 1.0 if hot else (0.34 if attested else 0.17)
        wdt = 2.1 if hot else 0.85
        dash = ' stroke-dasharray="3.5 3"' if e.type in ORDERING else ""
        out.append(f'<path d="{path(e)}" fill="none" stroke="{stroke}" stroke-width="{wdt}" '
                   f'opacity="{op}"{dash}/>')

    # --- nodes -------------------------------------------------------------------
    # Colour carries ONE thing in this figure - evidential status - so node kind is on shape
    # instead. A pill is a span (a material horizon, a whole work-state); a square-cornered
    # box is a single dated object or one stratum. Shape survives greyscale and colour
    # blindness, and the column has already said which kind of thing this is.
    RX = {"anchor": 2, "horizon": 9.5, "referent": 3, "stratum": 2, "work-state": 9.5}
    for n in nodes:
        left, right, cy = xy[n.id]
        head = n.id in HEADLINES
        hot = head or n.id in critical
        colour = "var(--fails)" if hot else "currentColor"
        y = cy - BOXH / 2
        out.append(
            f'<rect x="{left:.1f}" y="{y:.1f}" width="{right - left:.1f}" height="{BOXH}" '
            f'rx="{RX[n.kind]}" fill="{colour}" opacity="{0.14 if hot else 0.06}" '
            f'stroke="{colour}" stroke-width="{1.6 if hot else 0.7}" '
            f'stroke-opacity="{0.95 if hot else 0.28}"/>')
        out.append(
            f'<text x="{(left + right) / 2:.1f}" y="{cy + 3.6:.1f}" text-anchor="middle" '
            f'font-size="{FONT}" fill="currentColor" opacity="{1 if hot else .72}" '
            f'{"font-weight=\'600\'" if head else ""}>{short(n)}</text>')

    out.append("</svg>")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))
    print(f"<!-- {len(nodes)} nodes, {len(edges)} edges, {len(critical)} load-bearing -->",
          file=sys.stderr)


if __name__ == "__main__":
    main()
