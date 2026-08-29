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


def test_page_declares_reduced_motion_handling():
    if not HTML.exists():
        pytest.skip("console not built yet")
    t = HTML.read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in t
    assert "REDUCED" in t, "no scripted reduced-motion branch for the streaming trace"


def test_page_sanitizes_before_injecting_generated_svg():
    """A render boundary that trusts its input is the defect the previous
    project shipped. Assert the scrubber exists and that innerHTML is never
    handed model-adjacent markup."""
    if not HTML.exists():
        pytest.skip("console not built yet")
    t = HTML.read_text(encoding="utf-8")
    assert "safeSvg" in t
    assert "DOMParser" in t
    assert "importNode" in t
    assert 'innerHTML = markup' not in t
    assert '.innerHTML = map.svg' not in t


# --- the waveform is real data, so it gets asserted like data ----------------

def test_waveform_envelope_comes_from_the_real_clip():
    import pathlib
    from core.waveform import envelope
    clip = pathlib.Path(__file__).resolve().parents[1] / "data" / "reef_window_a.wav"
    if not clip.exists():
        pytest.skip("clip not present")
    env = envelope(str(clip), buckets=64)
    assert env["rate"] == 16000, "clip should be the 16 kHz mono cut"
    assert 59 <= env["seconds"] <= 61, f"expected a 60s window, got {env['seconds']}"
    assert len(env["peaks"]) == 64
    assert all(0.0 <= p <= 1.0 for p in env["peaks"])
    assert max(env["peaks"]) == 1.0, "envelope must be normalized to its own peak"
    # A reef soundscape is not silence and is not a constant tone.
    assert min(env["peaks"]) < 0.9, "envelope is suspiciously flat for a real recording"


def test_sweep_has_a_terminal_state_not_driven_by_animation_frames():
    """requestAnimationFrame is throttled to zero in a backgrounded tab.
    Measured in-browser: the sweep started, the playhead class was applied, and
    step() never ran, so no bar ever lit and the waveform sat frozen. A demo
    surface cannot have its OUTCOME depend on the tab being painted, so the
    visual is rAF-driven and the state is timer-driven."""
    if not HTML.exists():
        pytest.skip("console not built yet")
    t = HTML.read_text(encoding="utf-8")
    assert "finishSweep" in t, "no terminal state for the sweep"
    assert "setTimeout(finishSweep" in t, "terminal state is not timer-driven"
    assert "visibilitychange" in t, "no catch-up when the tab comes back"


def test_every_animation_selector_matches_a_real_element_or_class():
    """The design skill's rule: never leave dead animation code, and verify by
    search rather than by reading."""
    if not HTML.exists():
        pytest.skip("console not built yet")
    import re
    t = HTML.read_text(encoding="utf-8")
    animated = set(re.findall(r"\.([a-z-]+)(?:\.[a-z-]+)?\s*\{[^}]*animation:", t))

    # Look for the class OUTSIDE the stylesheet. The first version of this test
    # matched a handful of literal quoting patterns and produced a FALSE
    # POSITIVE on .trigger-label, which is applied as className = "trigger-label
    # draw". The class was live; the assertion was too narrow. Stripping the
    # style block and searching the remaining markup plus script is both simpler
    # and actually correct.
    body = re.sub(r"<style>.*?</style>", "", t, flags=re.S)
    for cls in animated:
        assert re.search(r"\b" + re.escape(cls) + r"\b", body), \
            f"animation targets .{cls} but nothing outside the stylesheet ever carries it"
