"""Every real corpus a project declares must satisfy the completeness contract.

Deferred from the corpus-protocol commit because corpus/ is gitignored, so these files are
absent in a clean checkout and an unconditional test would fail for everyone. The profile is
what made this possible without the engine importing project code by name: it names the
adapter module and the object in it, so this test walks profiles rather than knowing anything
about any tradition.

Skipped, not failed, when the texts are not on disk. What is NOT skipped is the case where the
texts are present and a loader has started losing them.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from parvan.corpus import Corpus
from parvan.profile import Profile, ProfileError

PROJECTS = Path(__file__).resolve().parents[1] / "projects"


def _profiles() -> list[Path]:
    if not PROJECTS.is_dir():
        return []
    return sorted(p for p in PROJECTS.glob("*/profile.yaml"))


PROFILES = _profiles()
IDS = [p.parent.name for p in PROFILES]


@pytest.mark.skipif(not PROFILES, reason="no project profiles on disk")
@pytest.mark.parametrize("path", PROFILES, ids=IDS)
def test_profile_validates(path: Path) -> None:
    try:
        Profile.load(path)
    except ProfileError as exc:
        pytest.fail(f"{path} refused:\n{exc.report()}")


def _loaded(path: Path):
    """The project's corpora, or a skip if its texts are not fetched."""
    prof = Profile.load(path)
    try:
        adapters = prof.adapters()
    except ProfileError as exc:
        pytest.fail(f"{path}: {exc.report()}")
    if not adapters:
        pytest.skip("profile declares no adapter module")
    out = {}
    for key, corpus in adapters.items():
        assert isinstance(corpus, Corpus), f"{key} is not a Corpus"
        try:
            out[key] = corpus.load()
        except SystemExit:
            # Every adapter exits with a fetch instruction when its source file is missing.
            pytest.skip(f"{key}: corpus files not fetched (see the project's corpus audit)")
    return prof, adapters, out


@pytest.mark.skipif(not PROFILES, reason="no project profiles on disk")
@pytest.mark.parametrize("path", PROFILES, ids=IDS)
def test_declared_corpora_satisfy_the_completeness_contract(path: Path) -> None:
    _, adapters, loaded = _loaded(path)
    for key, passages in loaded.items():
        assert passages, f"{key} loaded zero passages"
        # load() would have raised on a bad ratio or on residue; this pins the tolerance so a
        # loosened one shows up as a test change rather than as a quieter build.
        c = adapters[key]
        assert c.unparsed <= c.candidates * c.tolerance


@pytest.mark.skipif(not PROFILES, reason="no project profiles on disk")
@pytest.mark.parametrize("path", PROFILES, ids=IDS)
def test_every_locus_round_trips(path: Path) -> None:
    """A locus that does not parse back is a citation nobody can resolve against the text."""
    _, adapters, loaded = _loaded(path)
    for key, passages in loaded.items():
        c = adapters[key]
        sample = passages[:: max(1, len(passages) // 50)]
        for p in sample:
            assert c.parse_locus(c.locus(p)) == p.ref, f"{key}: {c.locus(p)} does not round-trip"


@pytest.mark.skipif(not PROFILES, reason="no project profiles on disk")
@pytest.mark.parametrize("path", PROFILES, ids=IDS)
def test_declared_controls_still_hold(path: Path) -> None:
    """The regression test the whole profile exists to make possible.

    These counts are the project's own published findings - a Roman coin name absent from the
    constituted text, a word for 'book' surviving only in the apparatus. If one moves, either
    a finding was wrong or the instrument broke, and both need saying out loud.
    """
    prof, _, _ = _loaded(path)
    bad = [r for r in prof.calibrate() if not r["ok"]]
    assert not bad, "controls no longer hold: " + "; ".join(
        f"{r['corpus']}/{r['pattern']} expected {r['expect']}, got {r['got']}" for r in bad
    )
