"""Show the decision layer's verdict for every published map category.

No model, no network, no cost. This is the part a judge can reason about
without trusting anything.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.synthesis import FWC_BANDS, synthesise, assess_band

print(f"{'MAP CATEGORY':<14} {'BAND (cells/L)':<26} {'VS 5,000 TRIGGER'}")
print("-" * 70)
for cat in FWC_BANDS:
    v = assess_band(cat)
    hi = "unbounded" if v.band_high is None else f"{v.band_high:,}"
    print(f"{cat:<14} {v.band_low:>10,} to {hi:<12} {v.relation}")

print("\n" + "=" * 70)
print("VERDICT FOR THE CATEGORY THE VISION AGENT ACTUALLY OBSERVED ('low')")
print("=" * 70)
a = synthesise(map_category="low", cell_threshold_in_federal_doc=False)
print(f"\nHEADLINE\n  {a.headline}")
print(f"\nWHY\n  {a.band_explanation}")
print(f"\nRECONCILIATION\n  {a.reconciliation}")
print("\nCAVEATS")
for c in a.caveats:
    print(f"  - {c}")

print("\n" + "=" * 70)
print("AND THE AMBIGUOUS ONE, WHICH IS THE POINT OF THE PROJECT")
print("=" * 70)
b = synthesise(map_category="very low", cell_threshold_in_federal_doc=False)
print(f"\nHEADLINE\n  {b.headline}")
print(f"\nWHY\n  {b.band_explanation}")
