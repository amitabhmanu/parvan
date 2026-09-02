# sanskrit-epics

The Rāmāyaṇa and Mahābhārata project: the tradition Parvan was built on, and until the
engine/project split the whole of the repository.

A *project* supplies everything the engine does not know: a corpus, adapters that read it, a
store of nodes and edges, instruments that measure it, and a preregistration frozen before
any of it ran. The engine supplies the schema, the gates, the solver and the falsifiers, and
knows nothing about Sanskrit.

```
store/    nodes, edges, methods.yaml   the constraint network
corpus/   third-party texts            fetched, never redistributed - see docs/corpus-audit.md
tools/    adapters and instruments     concordance, apparatus, aspect, subjunctive, ...
docs/     source synthesis + findings  including the frozen preregistration
runs/     solver run records           G-6 reproducibility
```

## Running it

From the repository root:

```bash
uv run parvan validate projects/sanskrit-epics/store
```

```bash
uv run parvan solve projects/sanskrit-epics/store
```

Run records land in `projects/sanskrit-epics/runs/`, alongside the store that produced them.

Instruments are run from inside this directory, because they resolve their corpus relative to
themselves:

```bash
cd projects/sanskrit-epics && uv run python tools/writing.py
```

## The corpus is not in the repository

`corpus/` is gitignored. The files are GRETIL and PTS transcriptions held under their own
terms; `docs/corpus-audit.md` records what each one is, where it came from, and what it can
and cannot support. Every loader asserts its own completeness before returning a line, because
an absence search over a corpus that silently drops 13% of its text is worthless — and that
happened three times before the check existed.
