"""Gate tests. Each feeds the loader a deliberately malformed record and asserts refusal.

Naming maps 1:1 onto the requirements index, so a failure here names the design invariant
that broke rather than a symptom.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from parvan.loader import StoreError, load

from conftest import write


def refuse(root: Path) -> set[str]:
    """Load, expect refusal, return the set of gates that fired."""
    with pytest.raises(StoreError) as exc:
        load(root)
    return {v.gate for v in exc.value.violations}


# --- control ---------------------------------------------------------------------
# Without this the gate tests could all be passing for the wrong reason.


def test_baseline_store_loads_clean(store: Path) -> None:
    loaded = load(store)
    assert len(loaded.nodes) == 3
    assert len(loaded.edges) == 2
    assert loaded.quarantine == []
    assert "realia-floor" in loaded.methods


# --- G-1: provenance is the validity condition -----------------------------------


def test_g1_attested_without_locus_is_refused(store: Path) -> None:
    write(
        store,
        "edges/e.presup.yaml",
        {
            "id": "e.presup",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "attested"},  # no locus
        },
    )
    assert "G-1" in refuse(store)


def test_g1_asserted_without_source_is_refused(store: Path) -> None:
    write(
        store,
        "edges/e.presup.yaml",
        {
            "id": "e.presup",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "asserted", "note": "everyone knows this"},
        },
    )
    assert "G-1" in refuse(store)


def test_g1_edge_without_provenance_at_all_is_refused(store: Path) -> None:
    write(
        store,
        "edges/e.presup.yaml",
        {
            "id": "e.presup",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
        },
    )
    assert "G-1" in refuse(store)


# --- G-2: quarantine is one-way ---------------------------------------------------


def test_g2_model_inferred_in_main_store_is_refused(store: Path) -> None:
    """The failure mode the whole project exists to prevent: a model's recollection
    entering the store as if it were evidence."""
    write(
        store,
        "edges/e.recalled.yaml",
        {
            "id": "e.recalled",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "model-inferred", "note": "recalled, not read"},
        },
    )
    assert "G-2" in refuse(store)


def test_g2_valid_record_left_in_quarantine_is_refused(store: Path) -> None:
    write(
        store,
        "quarantine/e.stranded.yaml",
        {
            "id": "e.stranded",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "attested", "locus": "Test.1.5.1"},
        },
    )
    assert "G-2" in refuse(store)


def test_g2_quarantined_records_never_reach_the_graph(store: Path) -> None:
    write(
        store,
        "quarantine/e.recalled.yaml",
        {
            "id": "e.recalled",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "model-inferred", "note": "recalled, not read"},
        },
    )
    loaded = load(store)
    assert len(loaded.quarantine) == 1
    assert "e.recalled" not in loaded.edges
    assert len(loaded.edges) == 2


# --- G-4: no node may both date a referent and be dated by it ---------------------


def test_g4_circular_attest_and_presuppose_is_refused(store: Path) -> None:
    """The Manu circularity: texts dated against Manu, Manu dated against the texts.
    Reification does not create it - it makes it detectable."""
    write(
        store,
        "edges/e.circular.yaml",
        {
            "id": "e.circular",
            "type": "attests",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "attested", "locus": "Test.1.4.2"},
        },
    )
    assert "G-4" in refuse(store)


def test_g4_text_only_referent_must_be_flagged(store: Path) -> None:
    store_only_textual(store)
    gates = refuse(store)
    assert "G-4" in gates


def test_g4_text_derived_flag_with_external_attestation_is_refused(store: Path) -> None:
    ref = {
        "id": "ref.test",
        "kind": "referent",
        "label": "Test referent",
        "class": "institution",
        "attestation": {"floor": -190, "ceiling": -180},
        "text_derived": True,  # contradicts the surviving anchor edge
        "provenance": {"tier": "attested", "locus": "test locus"},
    }
    write(store, "nodes/referents/ref.test.yaml", ref)
    assert "G-4" in refuse(store)


def store_only_textual(store: Path) -> None:
    """Drop the anchor edge so the referent is attested by texts alone."""
    (store / "edges" / "e.attest.yaml").unlink()
    write(
        store,
        "edges/e.presup2.yaml",
        {
            "id": "e.presup2",
            "type": "presupposes",
            "from": "anc.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "attested", "locus": "Test.2.1.1"},
        },
    )


# --- R-4: attestation caps emergence from above, never bounds it below ------------


def test_r4_emergence_ceiling_after_attestation_floor_is_refused(store: Path) -> None:
    write(
        store,
        "nodes/referents/ref.test.yaml",
        {
            "id": "ref.test",
            "kind": "referent",
            "label": "Test referent",
            "class": "institution",
            "emergence": {"floor": -400, "ceiling": -100},  # later than attestation.floor
            "attestation": {"floor": -190, "ceiling": -180},
            "provenance": {"tier": "attested", "locus": "test locus"},
        },
    )
    assert "R-4" in refuse(store)


def test_r4_empty_interval_is_refused(store: Path) -> None:
    write(
        store,
        "nodes/anchors/anc.test.yaml",
        {
            "id": "anc.test",
            "kind": "anchor",
            "label": "Test anchor",
            "interval": {"floor": -100, "ceiling": -300},  # floor later than ceiling
            "provenance": {"tier": "attested", "locus": "test coin catalogue no. 1"},
        },
    )
    assert "R-4" in refuse(store)


# --- R-5: ordering edges need a strict lag ---------------------------------------


def test_r5_citation_edge_without_lag_is_refused(store: Path) -> None:
    """At lag zero a chain transmits nothing beyond its base floor, and a directed cycle
    stops reporting infeasible - the diagnostic silently switches off."""
    write(
        store,
        "edges/e.cite.yaml",
        {
            "id": "e.cite",
            "type": "cites",
            "from": "str.test",
            "to": "anc.test",
            "method": "literary-citation",
            "lag_min_years": 0,
            "provenance": {"tier": "attested", "locus": "Test.1.1.1"},
        },
    )
    assert "R-5" in refuse(store)


# --- R-6: closed method vocabulary ------------------------------------------------


def test_r6_unknown_method_is_refused(store: Path) -> None:
    """An unknown tag would silently create an unpooled category in the Phase 5 model
    and overstate independence."""
    write(
        store,
        "edges/e.presup.yaml",
        {
            "id": "e.presup",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "vibes",
            "provenance": {"tier": "attested", "locus": "Test.1.4.2"},
        },
    )
    assert "R-6" in refuse(store)


def test_r6_missing_method_is_refused(store: Path) -> None:
    write(
        store,
        "edges/e.presup.yaml",
        {
            "id": "e.presup",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "provenance": {"tier": "attested", "locus": "Test.1.4.2"},
        },
    )
    assert "R-6" in refuse(store)


# --- D-2: referent inclusion rule -------------------------------------------------


def test_d2_singly_attested_referent_is_refused(store: Path) -> None:
    """A referent with one textual source cannot propagate, so it adds a node and buys
    nothing. Keeping the rule enforced is what holds the graph near 250-350 nodes."""
    (store / "edges" / "e.attest.yaml").unlink()
    (store / "nodes" / "anchors" / "anc.test.yaml").unlink()
    assert "D-2" in refuse(store)


# --- referential integrity and identity -------------------------------------------


def test_dangling_edge_reference_is_refused(store: Path) -> None:
    write(
        store,
        "edges/e.dangling.yaml",
        {
            "id": "e.dangling",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.does-not-exist",
            "method": "realia-floor",
            "provenance": {"tier": "attested", "locus": "Test.1.4.2"},
        },
    )
    assert "R-3" in refuse(store)


def test_duplicate_id_is_refused(store: Path) -> None:
    write(
        store,
        "nodes/strata/str.duplicate.yaml",
        {"id": "str.test", "kind": "stratum", "label": "Collides with the baseline stratum"},
    )
    assert "R-2" in refuse(store)


def test_unknown_node_kind_is_refused(store: Path) -> None:
    write(
        store,
        "nodes/strata/str.odd.yaml",
        {"id": "str.odd", "kind": "vibe-layer", "label": "Not a declared kind"},
    )
    assert "R-2" in refuse(store)


# --- the report names gates, so failures are actionable ---------------------------


def test_report_groups_violations_by_gate(store: Path) -> None:
    write(
        store,
        "edges/e.bad.yaml",
        {
            "id": "e.bad",
            "type": "presupposes",
            "from": "str.test",
            "to": "ref.test",
            "method": "vibes",
            "provenance": {"tier": "attested"},
        },
    )
    with pytest.raises(StoreError) as exc:
        load(store)
    report = exc.value.report()
    assert "G-1" in report and "R-6" in report
    assert "e.bad" in report


# --- G-7: only material evidence may floor an emergence ---------------------------


def test_g7_a_text_may_not_ground_an_emergence(store: Path) -> None:
    """A floor on when something began to exist is a material claim. Letting a text make it
    reintroduces exactly the circularity G-4 prevents: the text would date the referent that
    then dates the text."""
    write(
        store,
        "edges/e.textgrounds.yaml",
        {
            "id": "e.textgrounds",
            "type": "grounds",
            "from": "str.test",
            "to": "ref.test",
            "method": "realia-floor",
            "provenance": {"tier": "attested", "locus": "Test.1.4.2"},
        },
    )
    assert "G-7" in refuse(store)


def test_g7_a_horizon_may_ground(store: Path) -> None:
    """The control: an anchor grounding a referent is exactly what the edge is for."""
    write(
        store,
        "edges/e.anchorgrounds.yaml",
        {
            "id": "e.anchorgrounds",
            "type": "grounds",
            "from": "anc.test",
            "to": "ref.test",
            "method": "numismatic",
            "provenance": {"tier": "attested", "locus": "test coin catalogue no. 1"},
        },
    )
    loaded = load(store)
    assert "e.anchorgrounds" in loaded.edges


# --- G-8: a carve-out must be claimed by some other stratum -----------------------


def test_g8_dangling_carve_out_is_refused(store: Path) -> None:
    """A seam inside a book can only be expressed by carving it out of the containing
    stratum. If nothing claims the carved range, those passages fall out of the network
    silently - which is worse than the overlap the carve-out was meant to fix."""
    write(
        store,
        "nodes/strata/str.test.yaml",
        {
            "id": "str.test",
            "kind": "stratum",
            "label": "Test stratum",
            "work": "test",
            "extent": ["Test.1"],
            "excludes": ["Test.1.099"],
        },
    )
    assert "G-8" in refuse(store)


def test_g8_carve_out_claimed_by_another_stratum_loads(store: Path) -> None:
    """The control: once a stratum owns the carved range, the store is coherent."""
    write(
        store,
        "nodes/strata/str.test.yaml",
        {
            "id": "str.test", "kind": "stratum", "label": "Test stratum",
            "work": "test", "extent": ["Test.1"], "excludes": ["Test.1.099"],
        },
    )
    write(
        store,
        "nodes/strata/str.seam.yaml",
        {
            "id": "str.seam", "kind": "stratum", "label": "The carved-out seam",
            "work": "test", "extent": ["Test.1.099"],
        },
    )
    loaded = load(store)
    assert loaded.nodes["str.test"].excludes == ["Test.1.099"]
    assert "str.seam" in loaded.nodes
