"""The corpus completeness contract, proved by rejection.

Same discipline as the gate tests: a corpus loader that accepts good input is near-worthless
evidence that the contract works. What has to be demonstrated is that a loader which quietly
loses text cannot return that text as if it were whole, because that failure - not a crash,
not an exception, just a smaller number - is the one that turns a measured silence into a
false finding.
"""

from __future__ import annotations

import pytest

from parvan.corpus import Corpus, CorpusError, Passage, Tally, strip_diacritics


def build(parse, **attrs) -> Corpus:
    """A throwaway corpus whose _parse is supplied by the test."""
    ns = {
        "name": "Test",
        "sigil": "T",
        "ref_levels": ("book", "line"),
        "ref_pad": (0, 3),
        "_parse": lambda self, tally: parse(tally),
    }
    ns.update(attrs)
    return type("TestCorpus", (Corpus,), ns)()


def verses(tally: Tally, n: int = 4, *, work: str = "T") -> list[Passage]:
    out = []
    for i in range(n):
        tally.saw()
        out.append(Passage(ref=(1, i + 1), text=f"line {i + 1}", work=work))
    return out


# -- the completeness contract -----------------------------------------------------------


def test_loader_that_never_counts_is_refused():
    """The failure mode that motivates the whole contract: a denominator nobody supplied."""
    c = build(lambda t: [Passage(ref=(1, 1), text="x", work="T")])
    with pytest.raises(CorpusError, match="without counting a single candidate"):
        c.load()


def test_dropping_above_tolerance_is_refused():
    def parse(t):
        t.saw(10_000)
        for _ in range(6):
            t.drop("no match")
        return verses(t, 0)

    c = build(parse)
    with pytest.raises(CorpusError, match="parse incomplete"):
        c.load()


def test_dropping_at_tolerance_is_allowed_and_recorded():
    """Source-level transcription defects are real; they are reported, not hidden."""

    def parse(t):
        t.saw(10_000)
        for _ in range(5):
            t.drop("malformed at source")
        return verses(t, 1)

    c = build(parse)
    c.load()
    assert c.unparsed == 5
    assert "unparsed" in c.describe()


def test_residue_is_refused_even_though_every_line_parsed():
    """The Raghuvamsa failure: a ratio cannot see text attached to no locus."""

    def parse(t):
        out = verses(t)
        t.leftover("a trailing half-verse belonging to no marker")
        return out

    c = build(parse)
    with pytest.raises(CorpusError, match="never attached to a passage"):
        c.load()


def test_exemption_allows_no_denominator_but_not_residue():
    def parse(t):
        t.exempt("continuous prose, no line sigla to count")
        return [Passage(ref=(1, 1), text="x", work="T")]

    c = build(parse)
    assert len(c.load()) == 1
    assert "exempt" in c.describe()

    def parse_residue(t):
        t.exempt("continuous prose")
        t.leftover("orphan text")
        return []

    with pytest.raises(CorpusError, match="never attached"):
        build(parse_residue).load()


def test_load_is_cached_so_the_contract_runs_once():
    calls = []

    def parse(t):
        calls.append(1)
        return verses(t)

    c = build(parse)
    c.load()
    c.load()
    assert len(calls) == 1


# -- apparatus ----------------------------------------------------------------------------


def test_archetypal_only_is_refused_when_the_edition_has_no_apparatus():
    """Filtering nothing while implying a filter ran is the quiet version of a false claim."""
    c = build(verses)
    with pytest.raises(CorpusError, match="no apparatus"):
        c.search("line", archetypal_only=True)


def test_archetypal_only_filters_when_the_edition_does_have_one():
    def parse(t):
        t.saw(2)
        return [
            Passage(ref=(1, 1), text="constituted", work="T"),
            Passage(ref=(1, 2), text="constituted too", work="T", archetypal=False),
        ]

    c = build(parse, has_apparatus=True)
    assert len(c.search("constituted")) == 2
    assert len(c.search("constituted", archetypal_only=True)) == 1
    assert "1 archetypal, 1 apparatus" in c.describe()


def test_apparatus_status_shows_in_the_locus():
    def parse(t):
        t.saw()
        return [Passage(ref=(6, 1), text="x", work="T", archetypal=False)]

    c = build(parse, has_apparatus=True)
    assert c.locus(c.load()[0]) == "T.6.001*"


# -- editorial matter ----------------------------------------------------------------------


def test_notes_are_excluded_from_search_by_default():
    """The potthaka case: three hits, all of them the editors' own words."""

    def parse(t):
        t.saw()
        return [Passage(ref=(1, 1), text="the text itself", work="T",
                        notes="in the Sinhalese manuscript, potthaka")]

    c = build(parse)
    assert c.search("potthaka") == []
    assert len(c.search("potthaka", include_notes=True)) == 1


# -- loci, folding, divisions ---------------------------------------------------------------


def test_locus_round_trips():
    c = build(verses)
    for p in c.load():
        assert c.parse_locus(c.locus(p)) == p.ref


def test_parse_locus_rejects_a_foreign_sigil():
    c = build(verses)
    with pytest.raises(ValueError, match="not a T locus"):
        c.parse_locus("MBh.6.001.001")


def test_fold_is_applied_at_search_time():
    """An edition whose orthography differs from the tradition's normal search form."""

    def parse(t):
        t.saw()
        return [Passage(ref=(1, 1), text="agní", work="T")]

    plain = build(parse)
    assert plain.search("agni") == []

    folding = build(parse, fold=lambda self, s: strip_diacritics(s))
    assert len(folding.search("agni")) == 1


def test_divisions_filter_on_the_coarsest_level():
    def parse(t):
        t.saw(3)
        return [Passage(ref=(k, 1), text="x", work="T") for k in (1, 2, 7)]

    c = build(parse)
    assert len(c.search("x", divisions=[2, 7])) == 2
