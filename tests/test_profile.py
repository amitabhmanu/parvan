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
