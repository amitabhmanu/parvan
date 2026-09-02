---
description: Promote a Parvan edge from asserted to attested by checking it against the critical edition
---

Promote edge `$1` from `asserted` to `attested`, in the `sanskrit-epics` project.

Paths are project-relative to `projects/sanskrit-epics/`. When a second project exists this
command takes the project as its first argument; until then it is hardcoded, because guessing
which store an edge id belongs to is exactly the kind of convention that fails silently.

1. Read `projects/sanskrit-epics/store/edges/$1.yaml` for the claim, and the stratum file it
   points at for the declared `extent`.
2. Launch the `extractor` subagent with the edge id, the claim, and the extent.
3. Relay its verdict. On PROMOTE, show the proposed provenance block and **stop** — the human
   commits it (G-3). On CONTRADICTS, report it prominently; that is the more valuable result.
4. If a record is committed, re-run `uv run parvan validate projects/sanskrit-epics/store`
   and the F-6 check, and say whether the attested-only bracket moved.

Never edit the store yourself on the agent's say-so.
