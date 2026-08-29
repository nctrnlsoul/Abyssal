"""Design tokens, three tier. Components reference SEMANTIC names, never raw hex.

Every ratio in tests/test_palette.py is COMPUTED from these values, not copied
from a note. The previous build shipped a stale brand blue for eight months
because a color was treated as a durable fact. It is a perishable one.
"""
from __future__ import annotations

# --- tier 1, primitives ------------------------------------------------------
ABYSS_900 = "#070B10"   # page field
ABYSS_800 = "#0E141B"   # cards
ABYSS_700 = "#1A2430"   # hairlines, rules
SLATE_300 = "#CBD5E1"   # body text
SLATE_400 = "#94A3B8"   # muted text
SLATE_100 = "#E8EEF5"   # headings

# Product accent. Deliberately NOT the NorthSchema maker blue (#0055FD):
# product accent is not maker accent. Chosen on-subject for hydrophone and
# sonar readouts, and spent in exactly ONE place, the band ruler.
SONAR_400 = "#38D6E0"
SONAR_600 = "#0E7C88"   # accent on a LIGHT chip, where the bright one fails

# Approved dark-field verdict triple. Valid on ABYSS_900 only.
# Never paste these onto a light field: measured 1.88, 2.98 and 1.75 on white.
OK_400 = "#3ED598"
BAD_400 = "#FF5E64"
WARN_400 = "#F2BB4F"

# --- tier 2, semantic --------------------------------------------------------
SEMANTIC = {
    "field": ABYSS_900,
    "surface": ABYSS_800,
    "rule": ABYSS_700,
    "text": SLATE_300,
    "text-muted": SLATE_400,
    "heading": SLATE_100,
    "accent": SONAR_400,
    "accent-ink": SONAR_600,
    "state-ok": OK_400,
    "state-bad": BAD_400,
    "state-warn": WARN_400,
}

# Which pairs must clear which AA threshold. Asserted in tests.
# 4.5:1 for body text, 3.0:1 for large text and UI components.
CONTRAST_REQUIREMENTS = [
    ("text",        "field",   4.5),
    ("text",        "surface", 4.5),
    ("heading",     "field",   4.5),
    ("heading",     "surface", 4.5),
    ("text-muted",  "field",   4.5),
    ("text-muted",  "surface", 4.5),
    ("accent",      "field",   3.0),
    ("accent",      "surface", 3.0),
    ("state-ok",    "field",   4.5),
    ("state-bad",   "field",   4.5),
    ("state-warn",  "field",   4.5),
]

# Colors that must NEVER appear. Enforced by a test against the shipped HTML.
BANNED = {
    "#4392e6": "stale NorthSchema blue, superseded 2026-08-10, fails 4.5:1",
    "#0055fd": "NorthSchema MAKER accent. Product accent is not maker accent.",
    "#d97757": "Anthropic terracotta. A documented AI tell on anyone else's brief.",
    "#faf9f5": "Anthropic cream. Same reason.",
    "#c9a24b": "Custos brass. Different product, do not bleed.",
}


def _srgb(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def contrast(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    lo, hi = sorted((a, b))
    return (hi + 0.05) / (lo + 0.05)


def css_variables() -> str:
    """The single source the stylesheet consumes. Swapping this reskins."""
    return "\n".join(f"      --{k}: {v};" for k, v in SEMANTIC.items())
