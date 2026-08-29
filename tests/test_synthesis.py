"""The decision layer is where the product claim lives, so it gets real tests.

Deliberately includes the boundary cases. The previous build's lesson was that
a guard placed downstream of a coercion is not a guard; the sibling lesson is
that a band comparison with no boundary test is not a comparison.
"""
import pytest
from core.synthesis import (
    FWC_BANDS, FL_CLOSURE_TRIGGER_CELLS_PER_L, assess_band,
    straddling_categories, synthesise,
)


def test_trigger_is_the_published_state_figure():
    assert FL_CLOSURE_TRIGGER_CELLS_PER_L == 5_000


def test_not_present_is_entirely_below_trigger():
    v = assess_band("not present")
    assert v.relation == "BELOW"


def test_very_low_straddles_and_this_is_the_whole_point():
    """1,000 to 10,000 contains 5,000. The category cannot decide closure."""
    v = assess_band("very low")
    assert v.relation == "STRADDLES"
    assert "cannot tell you" in v.explanation


def test_low_and_above_are_entirely_over_the_trigger():
    for cat in ("low", "medium", "high"):
        assert assess_band(cat).relation == "ABOVE", cat


def test_exactly_one_published_category_is_ambiguous():
    """If a future FWC rescale makes two bands ambiguous, this must fail loudly
    rather than let the headline keep claiming a single clean gap."""
    assert straddling_categories() == ["very low"]


def test_unknown_category_does_not_silently_pass():
    v = assess_band("catastrophic")
    assert v.relation == "UNKNOWN"
    assert synthesise(map_category="catastrophic",
                      cell_threshold_in_federal_doc=False).band_relation == "UNKNOWN"


def test_case_and_whitespace_are_tolerated_not_guessed():
    assert assess_band("  VERY LOW  ").relation == "STRADDLES"
    assert assess_band("").relation == "UNKNOWN"


def test_bands_are_contiguous_and_ordered():
    """A gap or overlap between bands would make a verdict meaningless."""
    ordered = ["not present", "very low", "low", "medium", "high"]
    prev_hi = 0
    for cat in ordered:
        lo, hi = FWC_BANDS[cat]
        assert lo == prev_hi, f"{cat} does not start where the previous band ended"
        if hi is not None:
            assert hi > lo
            prev_hi = hi
    assert FWC_BANDS["high"][1] is None, "top band must be unbounded"


def test_synthesis_contradiction_raises_a_visible_caveat():
    """If the regulatory stage ever claims a cell threshold IS in the federal
    document, that contradicts the verified reading and must be surfaced, not
    quietly folded into a confident headline."""
    a = synthesise(map_category="very low", cell_threshold_in_federal_doc=True)
    assert any("WARNING" in c for c in a.caveats)
    assert any("find_biotoxin" in c for c in a.caveats)


def test_synthesis_always_states_that_colour_is_not_a_measurement():
    a = synthesise(map_category="low", cell_threshold_in_federal_doc=False)
    assert any("not a measurement" in c for c in a.caveats)


def test_reconciliation_states_the_testing_versus_closure_distinction():
    a = synthesise(map_category="very low", cell_threshold_in_federal_doc=False)
    # Assert the distinction, not my guess at the exact verb form. The first
    # version of this test asserted "trigger CLOSURE" against text that reads
    # "triggers CLOSURE" and failed. The code was right and the test was wrong,
    # which is its own small lesson: a brittle string assertion tests the
    # assertion, not the behaviour.
    assert "TESTING" in a.reconciliation
    assert "CLOSURE" in a.reconciliation
    assert a.reconciliation.index("TESTING") < a.reconciliation.index("CLOSURE")
    assert "20 MU/100 grams" in a.reconciliation


def test_headline_matches_the_relation_it_reports():
    """A headline that contradicts its own verdict field is the failure shape
    that put four false claims on the previous build's judged surfaces."""
    for cat in FWC_BANDS:
        a = synthesise(map_category=cat, cell_threshold_in_federal_doc=False)
        if a.band_relation == "STRADDLES":
            assert "cannot establish" in a.headline
        elif a.band_relation == "ABOVE":
            assert "at or above" in a.headline
        elif a.band_relation == "BELOW":
            assert "entirely below" in a.headline


# --- the signature element's geometry ---------------------------------------

def test_ruler_has_one_segment_per_published_band():
    from core.synthesis import ruler_segments, FWC_BANDS
    segs = ruler_segments()
    assert len(segs) == len(FWC_BANDS)
    assert sum(s["width_pct"] for s in segs) == pytest.approx(100.0)


def test_ruler_segments_are_contiguous():
    from core.synthesis import ruler_segments
    segs = ruler_segments()
    for a, b in zip(segs, segs[1:]):
        assert a["start_pct"] + a["width_pct"] == pytest.approx(b["start_pct"])


def test_trigger_line_lands_inside_the_very_low_segment():
    """The whole thesis, asserted numerically. If a future rescale moves the
    trigger out of 'very low', this fails rather than letting the graphic keep
    telling a story the numbers no longer support."""
    from core.synthesis import ruler_segments, trigger_position_pct
    pos = trigger_position_pct()
    very_low = next(s for s in ruler_segments() if s["category"] == "very low")
    assert very_low["start_pct"] < pos < very_low["start_pct"] + very_low["width_pct"]


def test_trigger_position_is_the_log_interpolated_value():
    """5,000 sits at log10 69.9% through the 1,000 to 10,000 decade, so at
    33.98% across a five-segment ruler. A linear reading would put it at 28.9%
    and the line would sit visibly in the wrong place."""
    from core.synthesis import trigger_position_pct
    assert trigger_position_pct() == pytest.approx(33.98, abs=0.02)
