"""G-9, proved by rejection: an attested absence must be re-runnable and controlled.

An argument from silence is the strongest thing this framework produces and the easiest to
fake, because a search that finds nothing looks exactly like a search that cannot find
anything. `yavana` over Kiskindhakanda returned zero, was published as a finding, and had to
be retracted when the truncated stem returned the verse. No prose record could have caught
that. A declared positive control would have, which is the entire content of this gate.
"""

from __future__ import annotations

import pytest

from parvan.loader import StoreError, load
from parvan.model import Control, Silence

from conftest import write

GOOD = {
    "corpus": "t",
    "scope": "the whole test corpus",
    "divisions": [1],
    "passages": 100,
    "patterns": ["absent-thing"],
    "hits": 0,
    "instrument": "tools/search.py",
    "controls": [{"pattern": "present-thing", "expect": 7}],
}


def absence(store_root, **silence_changes):
    """An attested absent-from edge whose silence block is GOOD plus the given changes."""
    sil = {**GOOD, **silence_changes}
    for k, v in list(sil.items()):
        if v is None:
            del sil[k]
    body = {
        "id": "e.absence",
        "type": "absent-from",
        "from": "str.test",
        "to": "ref.test",
        "method": "realia-floor",
        "provenance": {"tier": "attested", "locus": "measured silence, see silence block"},
    }
    if silence_changes.get("__drop__") is not True:
        body["silence"] = sil
    write(store_root, "edges/e.absence.yaml", body)
    return store_root


def refusal(store_root) -> str:
    with pytest.raises(StoreError) as e:
        load(store_root)
    assert {"G-9"} <= {v.gate for v in e.value.violations}
    return e.value.report()


# -- the gate ------------------------------------------------------------------------------


def test_a_well_formed_silence_loads(store):
    load(absence(store))


def test_attested_absence_without_a_silence_block_is_refused(store):
    assert "Prose in the locus is not re-runnable" in refusal(absence(store, __drop__=True))


def test_silence_without_a_control_is_refused(store):
    """The gate. Everything else in this file is scaffolding around this test."""
    assert "declares no positive control" in refusal(absence(store, controls=[]))


def test_control_pattern_without_an_expected_count_is_refused(store):
    r = refusal(absence(store, controls=[{"pattern": "present-thing"}]))
    assert "no expected count" in r


def test_control_must_be_exactly_one_kind(store):
    both = [{"pattern": "p", "locus": "T.1.001", "expect": 1}]
    assert "exactly one of" in refusal(absence(store, controls=both))
    neither = [{"note": "trust me"}]
    assert "exactly one of" in refusal(absence(store, controls=neither))


def test_measurement_control_needs_an_instrument(store):
    bad = [{"measurement": "200 indicatives of the same stems", "expect": 200}]
    assert "no instrument" in refusal(absence(store, controls=bad))


# -- the denominator -------------------------------------------------------------------------


def test_silence_over_zero_passages_is_refused(store):
    """A zero denominator is exactly what a corpus that failed to load looks like."""
    assert "absence over nothing is vacuous" in refusal(absence(store, passages=0))


def test_silence_without_a_passage_count_is_refused(store):
    assert "how many passages" in refusal(absence(store, passages=None))


def test_silence_without_an_instrument_is_refused(store):
    assert "not re-runnable" in refusal(absence(store, instrument=""))


def test_silence_with_neither_patterns_nor_a_measurement_is_refused(store):
    r = refusal(absence(store, patterns=[], hits=None))
    assert "nothing for anyone to re-run" in r


def test_patterns_without_a_hit_count_are_refused(store):
    assert "records no hit count" in refusal(absence(store, hits=None))


# -- unexplained hits ------------------------------------------------------------------------


def test_nonzero_hits_with_no_account_are_refused(store):
    """The dhrtarastri case: two hits, both a bird-ancestress, neither the Kuru king.

    A silence may legitimately return hits - a string match is a candidate, not a citation -
    but a record that reports a count and says nothing about it is indistinguishable from one
    whose author never looked.
    """
    assert "accounts for none of them" in refusal(absence(store, hits=2))


def test_nonzero_hits_are_allowed_once_rejected(store):
    load(absence(store, hits=2, rejected=["T.1.001 - the bird, not the king",
                                          "T.1.002 - likewise"]))


def test_nonzero_hits_are_allowed_once_the_reading_is_described(store):
    load(absence(store, hits=29, measurement="every hit read; none is an identity claim"))


# -- tier discipline ---------------------------------------------------------------------------


def test_a_silence_block_on_an_asserted_edge_is_refused(store):
    """An asserted absence is a scholar's claim, and stands on their argument, not our search."""
    write(store, "edges/e.absence.yaml", {
        "id": "e.absence", "type": "absent-from", "from": "str.test", "to": "ref.test",
        "method": "realia-floor",
        "provenance": {"tier": "asserted", "source": "Someone 2019, p. 40"},
        "silence": GOOD,
    })
    assert "the tier does not support" in refusal(store)


def test_an_asserted_absence_needs_no_silence_block(store):
    write(store, "edges/e.absence.yaml", {
        "id": "e.absence", "type": "absent-from", "from": "str.test", "to": "ref.test",
        "method": "realia-floor",
        "provenance": {"tier": "asserted", "source": "Someone 2019, p. 40"},
    })
    load(store)


def test_a_non_absence_edge_needs_no_silence_block(store):
    """G-9 is about arguments from silence, not about every attested edge."""
    load(store)


# -- the parsed record ---------------------------------------------------------------------------


def test_control_kinds_are_distinguished():
    assert Control(pattern="p", expect=1).kind == "pattern"
    assert Control(locus="T.1.001").kind == "locus"
    assert Control(measurement="a ratio", instrument="t.py").kind == "measurement"


def test_silence_parses_its_scope_and_options():
    sil = Silence.parse({
        "corpus": "ram", "scope": "books 2-6", "divisions": [2, 3],
        "excludes": ["Ram.6.105"], "passages": 10, "patterns": ["x"], "hits": 0,
        "instrument": "t.py",
        "controls": [{"pattern": "y", "expect": 3, "corpus": "mbh", "include_notes": True}],
    })
    assert sil.divisions == [2, 3]
    assert sil.excludes == ["Ram.6.105"]
    assert sil.controls[0].corpus == "mbh"
    assert sil.controls[0].include_notes is True
