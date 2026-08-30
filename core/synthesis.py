"""The decision layer. Pure, deterministic, no model, no IO.

The agents OBSERVE. This module DECIDES. That split is the whole reason the
conclusion can be trusted: the headline claim is computed from published
numeric bands by code you can read, not asserted by a language model inside a
prompt. Swapping the model cannot change the verdict.

Everything here is sourced. See docs/GROUND_TRUTH.md.
"""
from __future__ import annotations
from dataclasses import dataclass


# FWC published bloom-concentration bands, in CELLS PER LITRE.
# Source: https://myfwc.com/research/redtide/statewide/
# (low, high). None on the upper bound means unbounded.
FWC_BANDS: dict[str, tuple[int, int | None]] = {
    "not present": (0, 1_000),
    "very low":    (1_000, 10_000),
    "low":         (10_000, 100_000),
    "medium":      (100_000, 1_000_000),
    "high":        (1_000_000, None),
}

# Florida operational trigger for shellfish harvesting closure, cells per liter.
# FWC: closures "when cell abundance equals or exceeds 5,000 cells/L".
# This is a STATE trigger. It is not in the federal NSSP Guide: "5,000 cells"
# appears zero times across all 532 pages. Proven in docs/GROUND_TRUTH.md.
FL_CLOSURE_TRIGGER_CELLS_PER_L = 5_000

# The federal criterion, from NSSP 2023 Guide p.70, verified verbatim.
NSSP_NSP_ACTION_LEVEL = "20 MU/100 grams (0.8 mg brevetoxin-2 equivalents/kg)"
NSSP_MEASURED_IN = "shellfish meats"


@dataclass(frozen=True)
class BandVerdict:
    category: str
    band_low: int
    band_high: int | None
    relation: str   # BELOW | STRADDLES | ABOVE | UNKNOWN
    explanation: str


def assess_band(category: str) -> BandVerdict:
    """Where does a published map category sit relative to the closure trigger?

    Three outcomes, and the middle one is the point of the whole project:
      BELOW     the entire band is under the trigger
      STRADDLES the trigger falls INSIDE the band, so the category cannot tell
                you whether the area is closed
      ABOVE     the entire band is at or over the trigger
    """
    key = (category or "").strip().lower()
    if key not in FWC_BANDS:
        return BandVerdict(category, -1, None, "UNKNOWN",
                           f"'{category}' is not an FWC published band.")

    lo, hi = FWC_BANDS[key]
    t = FL_CLOSURE_TRIGGER_CELLS_PER_L

    if hi is not None and hi <= t:
        rel = "BELOW"
        why = (f"The whole '{key}' band (up to {hi:,} cells/L) is under the "
               f"{t:,} cells/L closure trigger.")
    elif lo >= t:
        rel = "ABOVE"
        why = (f"The whole '{key}' band starts at {lo:,} cells/L, at or above the "
               f"{t:,} cells/L closure trigger. Every sample in this category is "
               f"over the trigger.")
    else:
        rel = "STRADDLES"
        why = (f"The {t:,} cells/L closure trigger falls INSIDE the '{key}' band "
               f"({lo:,} to {hi:,} cells/L). A sample shown as '{key}' on the "
               f"public map may be either side of the trigger. The category alone "
               f"cannot tell you whether the area is closed.")
    return BandVerdict(category, lo, hi, rel, why)


def straddling_categories() -> list[str]:
    """Which published categories are ambiguous with respect to closure."""
    return [c for c in FWC_BANDS if assess_band(c).relation == "STRADDLES"]


@dataclass(frozen=True)
class Assessment:
    headline: str
    map_category: str
    band_relation: str
    band_explanation: str
    federal_criterion: str
    federal_matrix: str
    cell_threshold_in_federal_doc: bool
    reconciliation: str
    caveats: list[str]


def synthesise(*, map_category: str, cell_threshold_in_federal_doc: bool,
               federal_criterion: str = NSSP_NSP_ACTION_LEVEL,
               federal_matrix: str = NSSP_MEASURED_IN,
               extra_caveats: list[str] | None = None) -> Assessment:
    v = assess_band(map_category)

    if v.relation == "STRADDLES":
        headline = (f"The public map reads '{v.category}', which cannot establish "
                    f"whether this area is closed to harvest.")
    elif v.relation == "ABOVE":
        headline = (f"The public map reads '{v.category}'. Every value in that "
                    f"band is at or above Florida's {FL_CLOSURE_TRIGGER_CELLS_PER_L:,} "
                    f"cells/L closure trigger.")
    elif v.relation == "BELOW":
        headline = (f"The public map reads '{v.category}', entirely below Florida's "
                    f"{FL_CLOSURE_TRIGGER_CELLS_PER_L:,} cells/L closure trigger.")
    else:
        headline = f"Unrecognized map category '{v.category}'. No verdict."

    reconciliation = (
        "In the federal rulebook, cell counts trigger TESTING and toxin in "
        "the meat triggers CLOSURE. "
        f"Florida's {FL_CLOSURE_TRIGGER_CELLS_PER_L:,} cells/L closure line is "
        "the state's own rule, not a federal action level: it appears nowhere in "
        f"the NSSP Guide. The federal criterion is {federal_criterion}, measured "
        f"in {federal_matrix}."
    )

    caveats = list(extra_caveats or [])
    caveats.append(
        "A category on a public map is not a measurement. No cells-per-liter "
        "figure is derived from map color anywhere in this system."
    )
    if cell_threshold_in_federal_doc:
        caveats.append(
            "WARNING: the regulatory stage reported a cell-count threshold present "
            "in the federal document. That contradicts the verified source reading. "
            "Re-run scripts/find_biotoxin.py before relying on this result."
        )

    return Assessment(
        headline=headline,
        map_category=v.category,
        band_relation=v.relation,
        band_explanation=v.explanation,
        federal_criterion=federal_criterion,
        federal_matrix=federal_matrix,
        cell_threshold_in_federal_doc=cell_threshold_in_federal_doc,
        reconciliation=reconciliation,
        caveats=caveats,
    )


# --- the band ruler geometry -------------------------------------------------
# The signature element. Its position is COMPUTED, not eyeballed, so the graphic
# cannot drift away from the numbers it claims to represent.
#
# The bands are decades (1k, 10k, 100k, 1M), so the axis is logarithmic and each
# band is one equal segment. The trigger line's position inside its own band is
# the log-interpolated fraction, which is what makes "it lands inside very low"
# a measured statement rather than a drawing decision.
import math

RULER_ORDER = ["not present", "very low", "low", "medium", "high"]


def ruler_segments() -> list[dict]:
    n = len(RULER_ORDER)
    out = []
    for i, cat in enumerate(RULER_ORDER):
        lo, hi = FWC_BANDS[cat]
        out.append({
            "category": cat,
            "low": lo,
            "high": hi,
            "start_pct": round(i * 100 / n, 4),
            "width_pct": round(100 / n, 4),
            "relation": assess_band(cat).relation,
        })
    return out


def trigger_position_pct() -> float:
    """Where the 5,000 cells/L line falls across the whole ruler, in percent."""
    n = len(RULER_ORDER)
    for i, cat in enumerate(RULER_ORDER):
        lo, hi = FWC_BANDS[cat]
        if hi is not None and lo <= FL_CLOSURE_TRIGGER_CELLS_PER_L <= hi:
            span_lo = math.log10(max(lo, 1))
            span_hi = math.log10(hi)
            frac = ((math.log10(FL_CLOSURE_TRIGGER_CELLS_PER_L) - span_lo)
                    / (span_hi - span_lo))
            return round((i + frac) * 100 / n, 4)
    raise ValueError("trigger falls in no published band")
