"""Profile validation, proved by rejection.

P-1 is the gate that carries this file. A search trap with no worked example is the shape of
every rule that got written down and then not applied: "truncate before the stem-final vowel"
reads as pedantry until you see that the untruncated search returned zero and the zero was
published. Refusing the profile is cheaper than discovering which kind of rule you wrote after
the retraction.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from parvan.profile import Profile, ProfileError

MINIMAL = {
    "project": "test",
    "corpora": {
        "t": {
            "role": "primary",
            "object": "T",
            "positive_controls": [{"pattern": "x", "expect": 3}],
        }
    },
    "search_traps": [
        {
            "id": "a-trap",
            "rule": "the naive search misses the inflected form",
            "examples": [{"search": "foo", "text_has": "foos", "result": "no match"}],
        }
    ],
}


def write(tmp_path: Path, data: dict) -> Path:
    (tmp_path / "profile.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return tmp_path


def mutate(**changes) -> dict:
    import copy

    d = copy.deepcopy(MINIMAL)
    d.update(changes)
    return d


def gates(exc: ProfileError) -> set[str]:
    return {v.gate for v in exc.violations}


def test_minimal_profile_loads(tmp_path):
    prof = Profile.load(write(tmp_path, MINIMAL))
    assert prof.project == "test"
    assert len(prof.traps) == 1
    assert prof.corpora["t"].role == "primary"


def test_a_directory_without_a_profile_is_refused(tmp_path):
    # ProfileError's str() is the violation count; the detail is in report().
    with pytest.raises(ProfileError) as e:
        Profile.load(tmp_path)
    assert "no profile.yaml" in e.value.report()


# -- P-1: a rule without a worked example is advice, not a check ---------------------------


def test_trap_without_an_example_is_refused(tmp_path):
    d = mutate(search_traps=[{"id": "bare", "rule": "be careful out there"}])
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-1" in gates(e.value)
    assert "no worked example" in e.value.report()


def test_trap_without_a_rule_is_refused(tmp_path):
    d = mutate(search_traps=[{"id": "bare", "examples": [{"search": "a", "result": "b"}]}])
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-1" in gates(e.value)


def test_example_without_a_result_is_refused(tmp_path):
    d = mutate(search_traps=[{"id": "half", "rule": "r", "examples": [{"search": "a"}]}])
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-1" in gates(e.value)


def test_a_profile_with_no_traps_at_all_is_refused(tmp_path):
    """Every writing system has at least one. Claiming otherwise must be done explicitly."""
    d = mutate(search_traps=[])
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-1" in gates(e.value)


# -- P-2 / P-3: roles and adapters ----------------------------------------------------------


def test_unknown_role_is_refused(tmp_path):
    d = mutate(corpora={"t": {"role": "vibes", "object": "T",
                              "positive_controls": [{"pattern": "x", "expect": 1}]}})
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-2" in gates(e.value)


def test_corpus_without_an_adapter_object_is_refused(tmp_path):
    d = mutate(corpora={"t": {"role": "primary",
                              "positive_controls": [{"pattern": "x", "expect": 1}]}})
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-3" in gates(e.value)


def test_missing_adapter_object_is_refused_at_resolution(tmp_path):
    (tmp_path / "adapters.py").write_text("PRESENT = 1\n", encoding="utf-8")
    d = mutate(adapter_module="adapters.py")
    prof = Profile.load(write(tmp_path, d))
    with pytest.raises(ProfileError) as e:
        prof.adapters()
    assert "P-3" in gates(e.value)
    assert "defines no 'T'" in e.value.report()


# -- P-4: a silence measured with an unproven search is not a measured silence ---------------


def test_primary_corpus_without_a_positive_control_is_refused(tmp_path):
    d = mutate(corpora={"t": {"role": "primary", "object": "T"}})
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-4" in gates(e.value)
    assert "unmeasured silence" in e.value.report()


def test_a_control_corpus_needs_no_positive_control(tmp_path):
    """A genre control is never the thing an absence is measured over."""
    d = mutate(corpora={"t": {"role": "primary", "object": "T",
                              "positive_controls": [{"pattern": "x", "expect": 1}]},
                        "g": {"role": "genre-control", "object": "G"}})
    prof = Profile.load(write(tmp_path, d))
    assert prof.corpora["g"].role == "genre-control"


def test_control_without_an_expected_count_is_refused(tmp_path):
    d = mutate(corpora={"t": {"role": "primary", "object": "T",
                              "positive_controls": [{"pattern": "x"}]}})
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert "P-4" in gates(e.value)


def test_every_violation_is_reported_not_just_the_first(tmp_path):
    d = mutate(
        project="",
        # Two corpora, because an unknown role deliberately does NOT reach the
        # calibration gate - P-4 asks whether a *primary* proved its searches work.
        corpora={"t": {"role": "nonsense"}, "u": {"role": "primary", "object": "U"}},
        search_traps=[{"id": "bare"}],
    )
    with pytest.raises(ProfileError) as e:
        Profile.load(write(tmp_path, d))
    assert len(e.value.violations) >= 4
    assert {"P-1", "P-2", "P-3", "P-4"} <= gates(e.value)


# -- calibration --------------------------------------------------------------------------


def test_calibrate_reports_a_control_that_has_stopped_holding(tmp_path):
    (tmp_path / "adapters.py").write_text(
        "class _C:\n"
        "    def search(self, pattern, **kw):\n"
        "        return [1, 2] if pattern == 'here' else []\n"
        "T = _C()\n",
        encoding="utf-8",
    )
    d = mutate(
        adapter_module="adapters.py",
        corpora={"t": {"role": "primary", "object": "T",
                       "positive_controls": [{"pattern": "here", "expect": 2},
                                             {"pattern": "moved", "expect": 5}],
                       "known_silences": [{"pattern": "gone", "expect": 0}]}},
    )
    results = Profile.load(write(tmp_path, d)).calibrate()
    by_pattern = {r["pattern"]: r for r in results}
    assert by_pattern["here"]["ok"] is True
    assert by_pattern["gone"]["ok"] is True
    assert by_pattern["moved"]["ok"] is False
    assert by_pattern["moved"]["got"] == 0


# -- verify_silences ------------------------------------------------------------------------


def _verifiable(tmp_path: Path):
    """A tiny two-corpus project plus a store holding one attested absence."""
    (tmp_path / "adapters.py").write_text(
        "from parvan.corpus import Corpus, Passage\n"
        "class _C(Corpus):\n"
        "    ref_levels = ('book', 'line')\n"
        "    def __init__(self, sigil, rows):\n"
        "        super().__init__(); self.sigil = sigil; self.name = sigil; self.rows = rows\n"
        "    def _parse(self, t):\n"
        "        for ref, text in self.rows:\n"
        "            t.saw(); yield Passage(ref=ref, text=text, work=self.sigil)\n"
        "A = _C('A', [((1, 1), 'present-thing'), ((1, 2), 'filler'), ((2, 1), 'other book')])\n"
        "B = _C('B', [((1, 1), 'absent-thing lives here')])\n",
        encoding="utf-8",
    )
    (tmp_path / "profile.yaml").write_text(
        yaml.safe_dump({
            "project": "v", "adapter_module": "adapters.py",
            "corpora": {
                "a": {"role": "primary", "object": "A",
                      "positive_controls": [{"pattern": "present-thing", "expect": 1}]},
                "b": {"role": "baseline", "object": "B",
                      "positive_controls": [{"pattern": "absent-thing", "expect": 1}]},
            },
            "search_traps": MINIMAL["search_traps"],
        }, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return tmp_path


class _Store:
    def __init__(self, edges):
        self.edges = edges


def _edge(silence):
    from parvan.model import Edge, Provenance, Silence
    return Edge(id="e.1", type="absent-from", src="s", dst="d", method="m",
                provenance=Provenance(tier="attested", locus="x"),
                silence=Silence.parse(silence))


def test_verify_reconstructs_scope_and_confirms_a_silence(tmp_path):
    from parvan.profile import verify_silences
    prof = Profile.load(_verifiable(tmp_path))
    store = _Store({"e.1": _edge({
        "corpus": "a", "scope": "book 1", "divisions": [1], "passages": 2,
        "patterns": ["absent-thing"], "hits": 0, "instrument": "t.py",
        "controls": [{"pattern": "present-thing", "expect": 1}],
    })})
    by = {r["check"]: r for r in verify_silences(prof, store)}
    assert by["passages"]["ok"] and by["passages"]["got"] == 2
    assert by["hits"]["ok"]
    assert by["control[0]"]["ok"]


def test_verify_catches_a_scope_that_has_changed_size(tmp_path):
    from parvan.profile import verify_silences
    prof = Profile.load(_verifiable(tmp_path))
    store = _Store({"e.1": _edge({
        "corpus": "a", "scope": "book 1", "divisions": [1], "passages": 99,
        "patterns": ["absent-thing"], "hits": 0, "instrument": "t.py",
        "controls": [{"pattern": "present-thing", "expect": 1}],
    })})
    by = {r["check"]: r for r in verify_silences(prof, store)}
    assert by["passages"]["ok"] is False
    assert "different text" in by["passages"]["message"] or "no longer holds" in by["passages"]["message"]


def test_verify_catches_a_control_that_has_stopped_holding(tmp_path):
    from parvan.profile import verify_silences
    prof = Profile.load(_verifiable(tmp_path))
    store = _Store({"e.1": _edge({
        "corpus": "a", "scope": "book 1", "divisions": [1], "passages": 2,
        "patterns": ["absent-thing"], "hits": 0, "instrument": "t.py",
        "controls": [{"pattern": "present-thing", "expect": 44}],
    })})
    by = {r["check"]: r for r in verify_silences(prof, store)}
    assert by["control[0]"]["ok"] is False
    assert "currently sound" in by["control[0]"]["message"]


def test_a_cross_corpus_control_runs_against_its_own_corpus(tmp_path):
    """The strongest control available: the same string, proven well-formed elsewhere."""
    from parvan.profile import verify_silences
    prof = Profile.load(_verifiable(tmp_path))
    store = _Store({"e.1": _edge({
        "corpus": "a", "scope": "book 1", "divisions": [1], "passages": 2,
        "patterns": ["absent-thing"], "hits": 0, "instrument": "t.py",
        "controls": [{"pattern": "absent-thing", "corpus": "b", "expect": 1}],
    })})
    by = {r["check"]: r for r in verify_silences(prof, store)}
    assert by["control[0]"]["ok"], "the pattern is absent in A but present in B, which is the point"
    assert by["control[0]"]["detail"] == "b/absent-thing"


def test_excludes_drop_a_whole_prefix(tmp_path):
    from parvan.profile import scope_of
    prof = Profile.load(_verifiable(tmp_path))
    from parvan.model import Silence
    a = prof.adapters()["a"]
    assert len(scope_of(a, Silence.parse({"divisions": [1, 2]}))) == 3
    assert len(scope_of(a, Silence.parse({"divisions": [1, 2], "excludes": ["A.2"]}))) == 2


def test_a_measurement_control_is_reported_unchecked_not_passed(tmp_path):
    from parvan.profile import verify_silences
    prof = Profile.load(_verifiable(tmp_path))
    store = _Store({"e.1": _edge({
        "corpus": "a", "scope": "book 1", "divisions": [1], "passages": 2,
        "measurement": "a ratio no regex can re-derive", "instrument": "t.py",
        "controls": [{"measurement": "200 indicatives", "instrument": "t.py", "expect": 200}],
    })})
    by = {r["check"]: r for r in verify_silences(prof, store)}
    assert by["control[0]"].get("unchecked") is True
    assert "re-run t.py" in by["control[0]"]["message"]
