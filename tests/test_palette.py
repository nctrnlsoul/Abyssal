"""Contrast is COMPUTED here, not eyeballed, and not trusted from a note.

Ported discipline from HIGHWATER, where the design skill's own verdict colors
turned out to be tuned for a dark field and landed near 1.9:1 on white. The
test computes the ratio so nobody can paste a failing pair back in.

It also asserts the correct tokens are PRESENT, not merely that banned ones are
absent. An absent-only test passes on an empty file.
"""
import re, pathlib
import pytest

from core.palette import (
    BANNED, CONTRAST_REQUIREMENTS, SEMANTIC, contrast, css_variables,
)

HTML = pathlib.Path(__file__).resolve().parents[1] / "web" / "index.html"


@pytest.mark.parametrize("fg,bg,minimum", CONTRAST_REQUIREMENTS)
def test_contrast_meets_wcag_aa(fg, bg, minimum):
    ratio = contrast(SEMANTIC[fg], SEMANTIC[bg])
    assert ratio >= minimum, (
        f"{fg} on {bg} is {ratio:.2f}:1, needs {minimum}:1. "
        f"Retune the value, do not lower the threshold."
    )


def test_product_accent_is_not_the_maker_accent():
    """Product accent is not maker accent. Do not bleed NorthSchema blue in."""
    assert SEMANTIC["accent"].lower() != "#0055fd"


def test_no_banned_color_appears_in_the_shipped_page():
    if not HTML.exists():
        pytest.skip("console not built yet")
    text = HTML.read_text(encoding="utf-8").lower()
    for hexval, why in BANNED.items():
        assert hexval not in text, f"{hexval} present in the page: {why}"


def test_required_tokens_are_actually_present_in_the_page():
    """The absent-only version of this test passes on an empty file."""
    if not HTML.exists():
        pytest.skip("console not built yet")
    text = HTML.read_text(encoding="utf-8")
    for name in ("--field", "--accent", "--state-ok", "--heading"):
        assert name in text, f"semantic token {name} missing from the page"
    assert SEMANTIC["accent"].lower() in text.lower(), "accent value not in page"


def test_page_has_no_em_dash():
    """HIGHWATER shipped two to a judged surface and now fails its build on one."""
    if not HTML.exists():
        pytest.skip("console not built yet")
    text = HTML.read_text(encoding="utf-8")
    assert "\u2014" not in text, "em dash in the console"


def test_page_uses_american_english():
    if not HTML.exists():
        pytest.skip("console not built yet")
    text = HTML.read_text(encoding="utf-8").lower()
    for brit in ("colour", "grey", "behaviour", "analyse", "centre"):
        assert brit not in text, f"British spelling {brit!r} in the console"


def test_css_variables_block_covers_every_semantic_token():
    block = css_variables()
    for name in SEMANTIC:
        assert f"--{name}:" in block
