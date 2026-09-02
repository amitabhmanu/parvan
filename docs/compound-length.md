# Compound length tracks register, not stratum

§5 of the source synthesis treats compound length as a chronological arrow: *"Epic compounds
run to a few members; mature classical kāvya (Bāṇa, Daṇḍin, 6th–7th c.) piles up ten or
fifteen. The epics never do this."* That is a statistic, and the critical edition is machine
readable, so it can be measured rather than cited.

```bash
uv run python tools/compounds.py --threshold 20
```

Token length in IAST characters, as a proxy for compound size. A proxy, not a member count —
so the tail matters more than the mean, since a 30-character token is a multi-member compound
whatever else it is.

## The measurement

| kāṇḍa | tokens | mean | p99 | max | ≥20 chars | per 1,000 |
|---|---|---|---|---|---|---|
| 1 · Bāla | 21,711 | 7.20 | 19 | 43 | 202 | 9.30 |
| 2 · Ayodhyā | 37,442 | 6.91 | 19 | 42 | 296 | 7.91 |
| 3 · Araṇya | 23,647 | 7.14 | 20 | 40 | 240 | 10.15 |
| 4 · Kiṣkindhā | 22,453 | 7.19 | 20 | 38 | 248 | 11.05 |
| 5 · Sundara | 28,029 | 7.35 | 20 | 43 | 457 | **16.30** |
| 6 · Yuddha | 49,422 | 7.40 | 20 | 38 | 639 | 12.93 |
| 7 · Uttara | 31,111 | 6.97 | 19 | 40 | 254 | 8.16 |

| | mean | p99 | long per 1,000 |
|---|---|---|---|
| **Core** (2–6) | 7.21 | 20 | **11.68** |
| **Frame** (1, 7) | 7.06 | 19 | **8.63** |

## The result runs the wrong way

If compound length tracked date, the later books would be the more *kāvya*-like ones. §12
classes Bāla and Uttara as the late strata — and they have the **fewest** long compounds. The
core, supposedly earlier, has ~35% more.

The variation is not core-versus-frame at all. It is dominated by **Sundarakāṇḍa at 16.30 per
1,000**, nearly double Ayodhyākāṇḍa's 7.91 — and Sundara is the book of Hanumān's journey and
the long descriptive set-pieces on Laṅkā. Yuddha, the other descriptive and martial book, is
second. Ayodhyā and Uttara, the two most narrative-and-dialogue books, are lowest.

**So the metric separates descriptive register from narrative register, not early from late.**
Within a single text at kāṇḍa granularity it is not a chronological signal.

That is a caution for Phase 6. Compound length is one of the measurable features intended to
seed a stratification, and on this evidence it would seed one that tracks genre. It should
either be used residualised against register, or not used alone.

## What this does and does not settle for e.040

`ram.core --absent-from--> ref.classical-kavya-style` stays **`asserted`**, and the reason is
worth stating rather than glossing.

- **Measured:** the Rāmāyaṇa's own distribution. Its longest token in 214,000 is 43 characters,
  and p99 sits at 20 — roughly four to six members.
- **Not measured:** the other half. §5's claim is *comparative*, and the comparison needs Bāṇa
  and Daṇḍin, who are not in this corpus.

An absence edge whose referent has never been measured cannot honestly be tiered `attested`.
Fetching a *kāvya* sample would settle it, and would cost one afternoon — the same move that
turned the Pāṭaliputra silence from an assertion into a measurement.

## Incidental

The four longest compounds in the critical edition, none of them near classical *kāvya* scale:

```
43  Rām.1.015.010  snigdhaharyakṣatanujaśmaśrupravaramūrdhajam
43  Rām.5.055.003  bhujaṃgayakṣagandharvaprabuddhakamalotpalam
42  Rām.2.088.024  kuṣṭhapuṃnāgatagarabhūrjapatrottaracchadān
40  Rām.5.007.041  vyāvṛttagurupīnasrakprakīrṇavarabhūṣaṇāḥ
```
