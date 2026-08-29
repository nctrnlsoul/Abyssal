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

# Canvas. Monospace advances at roughly 0.6 em, which is what lets
# tests/test_agent_wiring.py assert nothing overruns the viewBox.
VIEW_W = 240
VIEW_H = 118
LABEL_PT = 4.6
HEADLINE_PT = 5.0
MONO_ADVANCE = 0.6
# Widest line that fits from x=8 to the right margin at HEADLINE_PT.
HEADLINE_CHARS = int((VIEW_W - 16) / (HEADLINE_PT * MONO_ADVANCE))


def _grid(w: float, h: float, step: float = 20.0) -> str:
    """A coordinate grid, as real SVG lines.

    Deliberately not a CSS background-image or an external asset: this markup
    is also committed into the recorded run and re-rendered by the console
    through a sanitizer, so it has to be self-contained geometry.
    """
    lines = []
    x = step
    while x < w:
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}"/>')
        x += step
    y = step
    while y < h:
        lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}"/>')
        y += step
    return ('<g stroke="#38D6E0" stroke-width="0.25" opacity="0.14">'
            + "".join(lines) + '</g>')


def label_anchor(cx: float, label: str, view_w: float = None) -> tuple[str, float]:
    """Decide which side of a marker its label sits on.

    Returns (text-anchor, x). Flips to the left once the label would run past
    the right edge. Extracted so the flip can be unit tested directly: asserting
    that the current four sites happen to trigger it would stop testing the
    branch the day a site moves.
    """
    w = VIEW_W if view_w is None else view_w
    extent = len(label) * LABEL_PT * MONO_ADVANCE
    if cx + 5 + extent > w:
        return "end", cx - 5
    return "start", cx + 5


def _wrap(s: str, width: int, max_lines: int) -> list[str]:
    """Word wrap on a character budget, ellipsising rather than overflowing."""
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and len(" ".join(lines)) < len(s):
        lines[-1] = lines[-1][:max(0, width - 3)].rstrip() + "..."
    return lines


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

    Geometry note. The first version used a 200x130 viewBox and placed every
    label to the RIGHT of its marker at a fixed offset. Labels for right-hand
    sites, and the headline, ran past the viewBox and were silently clipped by
    the browser: no error, no warning, just a truncated word. So the canvas is
    wider now, labels flip to the left of the marker once a site sits in the
    right third, and the headline wraps on a character budget. The invariant is
    asserted in tests rather than eyeballed, because clipping is invisible until
    someone reads the picture carefully.
    """
    w, h = VIEW_W, VIEW_H
    parts = [
        # xmlns is REQUIRED, not decorative. The HTML parser infers the SVG
        # namespace for a bare <svg>, so omitting it looks fine inline and then
        # breaks in any XML-namespace-aware consumer: DOMParser parsed this into
        # the null namespace and the browser rendered the whole diagram as
        # flowing text. Caught by looking at the page, not by any unit test,
        # because the string itself was perfectly valid.
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="Florida Karenia brevis monitoring sites">',
        f'<rect width="{w}" height="{h}" fill="#070B10"/>',
        # Coordinate grid. Drawn as real geometry rather than a background
        # image so it scales with the viewBox and needs no external asset.
        # Defs first: a soft glow the markers reuse, so the accent is applied
        # in one place instead of per element.
        '<defs>'
        '<filter id="ab-glow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="1.6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
        '</defs>',
        _grid(w, h),
        # Schematic on purpose. Calling a site diagram a map is the small
        # overclaim that becomes a big one.
        '<path d="M 74,26 C 112,22 136,40 140,64 C 144,90 129,116 108,126" '
        'fill="none" stroke="#1f6f78" stroke-width="3" opacity="0.25"/>',
        '<path d="M 74,26 C 112,22 136,40 140,64 C 144,90 129,116 108,126" '
        'fill="none" stroke="#5b7d8c" stroke-width="1.4"/>',
        f'<text x="8" y="12" font-size="4.4" fill="#64748b" '
        f'font-family="monospace">SCHEMATIC. Site categories only, not a '
        f'georeferenced map, no cell counts implied.</text>',
    ]

    for name, x, y, cat in SITES:
        cx, cy = 18 + x * 120, 26 + y * 74
        label = f"{name} [{cat}]"
        anchor, tx = label_anchor(cx, label, w)
        fill = _FILL.get(cat, "#94a3b8")
        # Crosshair ticks on the sites that matter, so the eye lands on them
        # without needing color alone to carry it.
        if cat not in ("not present", "very low"):
            parts.append(
                f'<path d="M {cx-6.5:.1f},{cy:.1f} h 3 M {cx+3.5:.1f},{cy:.1f} h 3 '
                f'M {cx:.1f},{cy-6.5:.1f} v 3 M {cx:.1f},{cy+3.5:.1f} v 3" '
                f'stroke="{fill}" stroke-width="0.6" opacity="0.9"/>'
            )
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.0" '
            f'fill="{fill}" stroke="#070B10" stroke-width="0.8" '
            f'filter="url(#ab-glow)"/>'
        )
        parts.append(
            f'<text x="{tx:.1f}" y="{cy + 1.6:.1f}" font-size="{LABEL_PT}" '
            f'text-anchor="{anchor}" fill="#94a3b8" font-family="monospace">'
            f'{html.escape(label)}</text>'
        )

    for i, line in enumerate(_wrap(headline, HEADLINE_CHARS, 2)):
        parts.append(
            f'<text x="8" y="{h - 14 + i * 7:.1f}" font-size="{HEADLINE_PT}" '
            f'fill="#e2e8f0" font-family="monospace">{html.escape(line)}</text>'
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
