---
description: Promote a Parvan edge from asserted to attested by checking it against the critical edition
---

Promote an edge from `asserted` to `attested`.

Arguments: `/attest <edge-id> [project]`. `$1` is the edge id; `$2` is a project directory
name under `projects/`, defaulting to `sanskrit-epics`.

1. Confirm the instrument before trusting it:
   `uv run parvan profile projects/<project> --check`. If a control fails, stop and report —
   the corpus, loader or orthography has moved and no silence measured today is sound.
2. Read `projects/<project>/store/edges/$1.yaml` for the claim, and the stratum file it points
   at for the declared `extent` and `excludes`.
3. Launch the `extractor` subagent with the project name, the edge id, the claim, and the
   extent. It reads the project's `profile.yaml` for everything language-specific.
4. Relay its verdict. On PROMOTE, show the proposed provenance block and **stop** — the human
   commits it (G-3). On CONTRADICTS, report it prominently; that is the more valuable result.
5. If a record is committed, re-run `uv run parvan validate projects/<project>/store` and the
   F-6 check, and say whether the attested-only bracket moved.

Never edit the store yourself on the agent's say-so.
