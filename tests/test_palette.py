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


# --- the container is a judged surface too -----------------------------------

def _root():
    import pathlib
    return pathlib.Path(__file__).resolve().parents[1]


def _effective(path) -> str:
    """File content with '#' comment lines removed.

    All three of these tests failed on their first run against their OWN
    documentation: the Dockerfile comment explaining why `app.main:app` is wrong
    contains the string `app.main:app`, and so on. A grep over a whole file
    tests the prose as well as the code. Assert the effective content.
    """
    lines = (_root() / path).read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in lines if not l.lstrip().startswith("#"))


def test_dockerfile_entrypoint_matches_the_real_module_path():
    """A suggested Dockerfile shipped `CMD uvicorn app.main:app` against a
    project whose module is `web.app:app`. That container starts, fails, and
    restarts forever while the deploy reports success. Assert the path exists."""
    import importlib.util
    df = _effective("Dockerfile")
    assert "web.app:app" in df, "Dockerfile CMD does not reference web.app:app"
    assert "app.main:app" not in df
    assert importlib.util.find_spec("web.app") is not None


def test_dockerfile_has_a_build_time_import_check():
    df = _effective("Dockerfile")
    assert "from web.app import app" in df, "no build-time import smoke test"


def test_dockerfile_runs_as_non_root():
    df = _effective("Dockerfile")
    assert "USER " in df and "root" not in df.split("USER ")[1].split("\n")[0]


def test_dockerignore_excludes_the_heavy_sources_and_the_venv():
    di = _effective(".dockerignore")
    for pattern in (".venv", ".git", "data/*.flac", "data/*.pdf", "agents"):
        assert pattern in di, f"{pattern} not excluded from the image"


def test_web_requirements_do_not_include_the_agent_framework():
    """The console never imports ADK; scripts/import_graph.py proves it in a
    fresh interpreter. Installing it anyway would put the whole tree on a public
    unauthenticated surface."""
    rw = _effective("requirements-web.txt").lower()
    for banned in ("google-adk", "google-genai", "pymupdf", "numpy"):
        assert banned not in rw, f"{banned} in the deployed image's requirements"
    assert "fastapi==" in rw and "starlette==" in rw, "pins must be exact"


def test_deploy_sets_a_service_account_and_an_instance_cap():
    """Adversarial review on the previous project: Cloud Run with no
    --service-account runs as project Editor, reachable keylessly from the
    metadata server. And --max-instances IS the spend cap."""
    dp = _effective("deploy.ps1")
    assert "--service-account" in dp
    assert "--max-instances" in dp
    assert "LASTEXITCODE" in dp, "a failed native command would be reported as success"


def test_deploy_never_sets_an_api_key_on_the_service():
    dp = _effective("deploy.ps1")
    assert "GOOGLE_API_KEY" not in dp, "the public console must stay keyless"


def test_deploy_anchors_its_own_working_directory():
    """The first run of deploy.ps1 had no Set-Location, so PowerShell's default
    cwd applied, `--source .` resolved to C:\\Windows\\System32, and gcloud spent
    two minutes uploading the Windows system directory before crashing. A
    relative --source in a script that does not pin its location does not fail
    with 'file not found'; it uploads your operating system."""
    dp = _effective("deploy.ps1")
    assert "Set-Location" in dp, "deploy script does not anchor its cwd"
    assert "PSScriptRoot" in dp, "cwd is anchored to something other than the script"


def test_deploy_preflights_the_files_the_image_needs():
    dp = _effective("deploy.ps1")
    assert "Test-Path" in dp, "no preflight, so a wrong cwd falls back to Buildpacks"
    for required in ("Dockerfile", "web/app.py", "recorded-run.json"):
        assert required in dp, f"preflight does not check {required}"


def test_gcloudignore_exists_and_excludes_the_venv():
    """Without .gcloudignore, gcloud uses .gitignore semantics, which are not
    the same set and do not exclude what a build upload should exclude."""
    gi = _effective(".gcloudignore")
    for pattern in (".venv", ".git", "data/*.flac"):
        assert pattern in gi, f"{pattern} would be uploaded to Cloud Build"


def test_health_endpoint_avoids_the_path_cloud_run_intercepts():
    """MEASURED on the deployed service: the Google Front End intercepts
    /healthz on Cloud Run and serves its own 404. The request never reaches the
    container, so a liveness check on that path reports a healthy service as
    down. /health, /api/healthz and every other path reach the app normally.

    This also corrects a wrong diagnosis on the previous project, where the
    same 404 was attributed to a stale revision.
    """
    src = _effective("web/app.py")
    assert '@app.get("/health")' in src
    assert '@app.get("/healthz")' not in src, "GFE swallows /healthz on Cloud Run"


def test_low_band_is_returned_at_both_scales_with_the_ratio():
    """Two scalings on purpose. `low_band` keeps the honest relative energy and
    renders nearly flat, because shrimp dominate this recording by more than an
    order of magnitude. `low_band_self` shows the shape in its own lane. The
    ratio is returned so the page can print it rather than let a reader compare
    bar heights across lanes."""
    import pathlib
    from core.waveform import envelope
    clip = pathlib.Path(__file__).resolve().parents[1] / "data" / "reef_window_a.wav"
    if not clip.exists():
        pytest.skip("clip not present")
    e = envelope(str(clip), buckets=64)
    assert len(e["low_band"]) == len(e["low_band_self"]) == len(e["peaks"]) == 64
    assert max(e["low_band_self"]) == 1.0, "self-scaled band must reach 1.0"
    assert max(e["low_band"]) < 0.5, "shared-scale low band should be small on this clip"
    assert 0 < e["low_band_share_of_peak"] < 0.5
    assert e["low_band_corner_hz"] == 500


def test_waveform_reports_where_the_peaks_actually_are():
    import pathlib
    from core.waveform import envelope
    clip = pathlib.Path(__file__).resolve().parents[1] / "data" / "reef_window_a.wav"
    if not clip.exists():
        pytest.skip("clip not present")
    e = envelope(str(clip), buckets=64)
    assert 0 <= e["peak_at_seconds"] <= e["seconds"]
    assert 0 <= e["low_peak_at_seconds"] <= e["seconds"]
    assert e["peaks"][e["peak_bucket"]] == 1.0
