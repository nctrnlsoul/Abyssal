"""The four monitoring sites, positioned on the actual NOAA frame.

Fractions are of the committed image data/hab_forecast_cellcounts.png
(1156 x 875), placed BY EYE on the visible sample clusters: the yellow "low"
dots by St Augustine, the gray cluster on the Big Bend coast, the mixed
cluster at Tampa Bay / Clearwater, and the single gray point by Port St Lucie.

That makes these APPROXIMATE positions, and every surface that draws them says
so. Eyeballed-and-labelled beats a precise-looking schematic that corresponds
to nothing: the overlay puts the agent's reading on the evidence it read.

Categories are the imagery agent's verified reading of the same frame.
tests/test_agent_wiring.py asserts this table and the schematic renderer's
table agree on names and categories, so the two can never drift apart.
"""

SITES_ON_IMAGE = [
    {"name": "Jacksonville / St Augustine", "category": "low",         "x": 0.632, "y": 0.217},
    {"name": "Big Bend",                    "category": "not present", "x": 0.502, "y": 0.343},
    {"name": "Tampa Bay / Clearwater",      "category": "low",         "x": 0.510, "y": 0.486},
    {"name": "Port St Lucie",               "category": "not present", "x": 0.718, "y": 0.563},
]

POSITIONING_NOTE = ("approximate positions, placed by eye on the visible "
                    "sample clusters of the NOAA frame")
