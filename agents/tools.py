"""Stage 4 tools. Real function calling, and the functions really do something.

These are the only place the pipeline produces a rendered artifact. They are
plain Python, unit-testable without a model, because a tool whose behaviour is
only ever observed through an LLM is not a tested tool.
"""
from __future__ import annotations
import html


# Verified sample locations read off the NOAA public map. Categories only,
# because that map carries no numeric values. See docs/GROUND_TRUTH.md.
SITES = [
    ("Jacksonville / St Augustine", 0.74, 0.18, "low"),
    ("Big Bend",                    0.46, 0.30, "not present"),
    ("Tampa Bay / Clearwater",      0.52, 0.52, "low"),
    ("Port St Lucie",               0.80, 0.62, "not present"),
]

_FILL = {
    "not present": "#6b7280",
    "very low":    "#f8fafc",
    "low":         "#eab308",
    "medium":      "#f97316",
    "high":        "#ef4444",
}


def render_incident_map(headline: str) -> dict:
    """Draw the monitoring sites and their reported map categories as an SVG.

    Args:
        headline: the verdict line to print under the map.

    Returns:
        A dict with the SVG markup and the site count.
    """
    parts = [
        '<svg viewBox="0 0 200 130" role="img" '
        'aria-label="Florida Karenia brevis monitoring sites">',
        '<rect width="200" height="130" fill="#0b1220"/>',
        # deliberately schematic. This is a site diagram, not a georeferenced
        # map, and labelling it otherwise would be the overclaim this project
        # exists to avoid.
        '<path d="M 60,18 C 96,14 118,30 122,52 C 126,76 112,100 92,110" '
        'fill="none" stroke="#334155" stroke-width="1.5"/>',
    ]
    for name, x, y, cat in SITES:
        cx, cy = 20 + x * 150, 10 + y * 100
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" '
            f'fill="{_FILL.get(cat, "#94a3b8")}" stroke="#0b1220" stroke-width="0.8"/>'
        )
        parts.append(
            f'<text x="{cx + 5:.1f}" y="{cy + 2:.1f}" font-size="4" '
            f'fill="#94a3b8" font-family="monospace">{html.escape(name)} '
            f'[{html.escape(cat)}]</text>'
        )
    parts.append(
        f'<text x="10" y="124" font-size="4.6" fill="#e2e8f0" '
        f'font-family="monospace">{html.escape(headline[:88])}</text>'
    )
    parts.append(
        '<text x="10" y="10" font-size="4" fill="#64748b" '
        'font-family="monospace">SCHEMATIC. Site categories only, not a '
        'georeferenced map, no cell counts implied.</text>'
    )
    parts.append("</svg>")
    return {"svg": "".join(parts), "sites_rendered": len(SITES)}


def write_advisory(headline: str, federal_criterion: str, reconciliation: str) -> dict:
    """Emit the advisory text for the incident.

    Args:
        headline: the verdict computed by the decision layer.
        federal_criterion: the action level as the ordinance states it.
        reconciliation: how the state trigger and the federal criterion relate.

    Returns:
        A dict with the advisory body and its character count.
    """
    body = (
        f"ADVISORY\n\n{headline}\n\n"
        f"Federal criterion: {federal_criterion}\n\n"
        f"{reconciliation}\n\n"
        "This advisory is generated from archived public data for demonstration. "
        "It is not an official determination. Harvesting area status is set by "
        "the Florida Department of Agriculture and Consumer Services, Division "
        "of Aquaculture."
    )
    return {"advisory": body, "chars": len(body)}


REPORT_TOOLS = [render_incident_map, write_advisory]
