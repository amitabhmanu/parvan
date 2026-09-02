# V-2 — retrodiction

**Result: FAILS, 0 PASS / 0 WEAK / 8 FAIL.** Every held-out anchor trips the preregistered
vacuity check.

```bash
uv run parvan retrodict store
```

```
sacred, not held out: anc.agathocles, anc.cham-valmiki

anchor                  true          recovered              verdict
anc.deogarh             [400, 550]    [749 BCE, unbounded]   FAIL
anc.heliodorus          [-115, -105]  [190 BCE, unbounded]   FAIL
anc.imprecatory-grants  [450, 600]    [151 CE,  unbounded]   FAIL
anc.khoh-plates         [500, 520]    [151 CE,  unbounded]   FAIL
anc.liudu-jijing        [251, 251]    [749 BCE, unbounded]   FAIL
anc.nagarjunakonda      [200, 400]    [749 BCE, unbounded]   FAIL
anc.spitzer             [200, 300]    [499 BCE, unbounded]   FAIL
anc.veal-kantel         [590, 610]    [151 CE,  unbounded]   FAIL

pass rate 0% (floor 40%)   pass-or-weak 0% (floor 70%)
```

The failure was predictable — with every minimum cut at 1, removing a constraint leaves what
depended on it unbounded. It was run anyway, because skipping a preregistered validation
because you expect it to fail is the precise error the preregistration exists to prevent.

## The diagnosis: the anchors are terminal

Look at the shape rather than the counts. **Every recovery has a floor and no ceiling.** Not
one is bounded above.

That is structural. Anchors in this store sit at the *late* end of every chain they belong to
— `anc.spitzer cites ws.mbh.core`, `anc.veal-kantel cites ws.ram.600ce`. The network can
therefore say "this inscription postdates the text it cites" and nothing more, because
**nothing in the store is later than the anchors**, so nothing can ceiling them.

Which is a true description of the evidence. The Veal Kantel inscription really is among the
latest things available; there is no later witness to bound it. The network is reporting the
shape of the archive correctly.

**So V-2 as written cannot pass for a terminal node**, whatever the network's quality. The
protocol tacitly assumed anchors are interior, with constraints on both sides. They are not.

## One thing that did work

**No recovered floor contradicts the truth.** All eight are earlier than the held-out value,
as a valid floor must be — the network is never *wrong* about an anchor, only silent in one
direction. Two are within 100 years of it: Heliodorus recovers ≥190 BCE against a true
115–105 BCE, and Spitzer recovers ≥499 BCE against 200–300 CE.

That is a weaker claim than V-2 asked for and worth recording as its own result: the
directional constraint is sound, the two-sided one is unavailable.

## What must not happen next

The preregistration's amendment rule: *"A threshold may not be loosened after a run that failed
it."* This result stands as a failure. Specifically:

- The vacuity check is **not** relaxed to accept one-sided recoveries.
- The 800-year width cap is **not** raised.
- The eight holdouts are **not** re-scoped to the two that came closest.

A revised protocol — for instance, floor-only retrodiction on terminal anchors, scored against
whether the recovered floor is valid and how tight it is — would be a legitimate **addition**,
declared before the run it applies to and committed as a separate amendment. It would not
change this outcome, and any future report must carry both.

## What would actually make V-2 passable

Not a threshold change. Structure:

1. **A later witness for each anchor.** An anchor cited by something later becomes interior
   and acquires a ceiling. The Cambodian and Cham material could bound each other; the Gupta
   grants could be bounded by post-Gupta ones.
2. **Redundancy.** Minimum cut is 1 on every bound in the store. Until some bound has two
   genuinely edge-disjoint routes, removing anything leaves a hole.

Both are corpus problems, not solver problems. V-2 should be re-run when the store has grown,
and its failure today is a measurement of how thin the network still is rather than a verdict
on the method.
