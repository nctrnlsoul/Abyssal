"""Construct every agent. Actually construct them.

The previous build had eight wiring tests that checked tool names, tiers,
docstrings, signatures and instruction text, and NOT ONE of them ever built an
agent. A hyphen in a worker name made ADK reject construction and every live
run died, while the suite stayed green. The rule that came out of it:

    If a factory function exists, a test must call it.
    Testing its inputs is not testing it.

LlmAgent validates its own fields before any model is called, so all of this
runs with no API key and costs nothing.
"""
import pytest

from agents.definitions import (
    ALL_FACTORIES, MAX_LLM_CALLS, MAX_OUTPUT_TOKENS,
    build_report_agent,
)
from agents.tools import REPORT_TOOLS, render_incident_map, write_advisory


def test_every_factory_actually_constructs():
    for expected_name, factory in ALL_FACTORIES.items():
        agent = factory()
        assert agent is not None
        assert agent.name == expected_name


def test_report_agent_constructs_with_its_tools():
    agent = build_report_agent(REPORT_TOOLS)
    assert agent.name == "remediation_reporter"


def test_every_agent_name_is_a_valid_python_identifier():
    """ADK rejects a non-identifier name at construction. A hyphen here cost
    the previous build every live run it attempted."""
    names = list(ALL_FACTORIES) + ["remediation_reporter"]
    for n in names:
        assert n.isidentifier(), f"{n!r} is not a valid Python identifier"


def test_every_agent_bounds_its_own_output():
    """A model-spending product with no cap on its own spend is denial-of-wallet."""
    for factory in ALL_FACTORIES.values():
        cfg = factory().generate_content_config
        assert cfg is not None
        assert cfg.max_output_tokens and cfg.max_output_tokens > 0
        assert cfg.temperature == 0.0


def test_llm_call_cap_is_set_and_sane():
    assert 1 <= MAX_LLM_CALLS <= 50
    assert MAX_OUTPUT_TOKENS >= 512


def test_structured_agents_declare_an_output_schema():
    for name, factory in ALL_FACTORIES.items():
        assert factory().output_schema is not None, name


# --- the tools are real functions, so they get tested as real functions ------

def test_render_incident_map_emits_wellformed_svg():
    r = render_incident_map("The public map reads 'low'.")
    assert r["svg"].startswith("<svg") and r["svg"].endswith("</svg>")
    assert r["sites_rendered"] == 4


def test_render_incident_map_escapes_its_input():
    """The headline reaches an SVG text node. It is model-adjacent text on a
    surface a judge loads in a browser, so it gets escaped, not trusted.
    The previous build shipped an innerHTML render boundary and had to fix it."""
    r = render_incident_map('<script>alert(1)</script>')
    assert "<script>" not in r["svg"]
    assert "&lt;script&gt;" in r["svg"]


def test_render_incident_map_labels_itself_schematic():
    """Calling a site diagram a map is the small overclaim that becomes a big one."""
    assert "SCHEMATIC" in render_incident_map("x")["svg"]


def test_write_advisory_states_it_is_not_an_official_determination():
    r = write_advisory("headline", "20 MU/100 grams", "cell counts trigger testing")
    assert "not an official determination" in r["advisory"]
    assert "Division of Aquaculture" in r["advisory"]
    assert r["chars"] == len(r["advisory"])


def test_tools_have_docstrings_because_adk_sends_them_to_the_model():
    for fn in REPORT_TOOLS:
        assert fn.__doc__ and len(fn.__doc__.strip()) > 20, fn.__name__


# --- the measured Gemini 3.x thinking-budget trap ----------------------------

def test_output_cap_leaves_room_above_the_thinking_budget():
    """MEASURED 2026-08-28: thinking tokens count against max_output_tokens on
    gemini-3.x. A 4096 cap produced 3,928 thinking tokens and 152 output
    tokens, truncating the JSON mid-string. The cap must exceed the thinking
    budget by a real margin or every structured stage is one long answer away
    from a misleading 'Invalid JSON' error."""
    from agents.definitions import THINKING_BUDGET, MAX_OUTPUT_TOKENS
    assert MAX_OUTPUT_TOKENS > THINKING_BUDGET, "no room left for actual output"
    assert MAX_OUTPUT_TOKENS - THINKING_BUDGET >= 2048, "headroom too thin"


def test_every_agent_declares_a_thinking_budget():
    from agents.definitions import ALL_FACTORIES, THINKING_BUDGET
    for name, factory in ALL_FACTORIES.items():
        cfg = factory().generate_content_config
        assert cfg.thinking_config is not None, f"{name} has no thinking budget"
        assert cfg.thinking_config.thinking_budget == THINKING_BUDGET, name
        assert cfg.max_output_tokens > THINKING_BUDGET, name


def test_truncation_error_type_exists_and_is_distinct():
    """A budget failure must not arrive disguised as a parse failure."""
    from agents.definitions import TruncatedOutputError
    assert issubclass(TruncatedOutputError, RuntimeError)
    assert not issubclass(TruncatedOutputError, ValueError)


# --- the generated SVG is a render boundary, so it gets boundary tests --------

def test_generated_svg_carries_no_script_or_event_handlers():
    """The console injects this into the DOM. The tool escapes its inputs, but
    'our own code made it' is the assumption that stops being true one refactor
    later, so assert it here AND scrub it in the page."""
    import re
    svg = render_incident_map("verdict line")["svg"]
    low = svg.lower()
    assert "<script" not in low
    assert "foreignobject" not in low
    assert "javascript:" not in low
    assert not re.search(r"\son[a-z]+\s*=", low), "event handler attribute in generated SVG"


def test_generated_svg_escapes_a_hostile_headline_end_to_end():
    bad = '"><script>fetch("//evil")</script><text x="0'
    svg = render_incident_map(bad)["svg"]
    assert "<script" not in svg.lower()
    assert "&lt;script&gt;" in svg


def test_advisory_never_contains_an_em_dash():
    """Judged surface. The previous build failed its own build on one."""
    r = write_advisory("h", "20 MU/100 grams", "cell counts trigger testing")
    assert "—" not in r["advisory"]


def test_generated_svg_declares_the_svg_namespace():
    """Without xmlns the markup is still 'valid' and still renders inline in
    HTML, because the HTML parser infers the namespace. It then parses into the
    NULL namespace through DOMParser and the browser lays the whole diagram out
    as flowing text. A silent visual failure that no string assertion about the
    SVG's content would have caught."""
    svg = render_incident_map("x")["svg"]
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg


def test_generated_svg_is_parseable_as_xml():
    """If it does not parse as XML it will not survive DOMParser either."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(render_incident_map("verdict")["svg"])
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
    assert len(circles) == 4, "one marker per monitoring site"


# --- clipping is invisible, so it gets an invariant ---------------------------

def _text_elements(svg: str):
    """(x, anchor, font_size, content) for every <text> in the markup."""
    import xml.etree.ElementTree as ET
    NS = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(svg)
    out = []
    for t in root.findall(f".//{NS}text"):
        out.append((
            float(t.get("x")),
            t.get("text-anchor", "start"),
            float(t.get("font-size")),
            "".join(t.itertext()),
        ))
    return out


def test_no_text_overruns_the_viewbox():
    """The first version clipped 'Jacksonville / St Augustine [low]' and the
    headline, silently: no error, no warning, just a truncated word that only a
    careful reader notices. Monospace advances at about 0.6 em, so the extent is
    computable and the invariant is assertable."""
    from agents.tools import VIEW_W, MONO_ADVANCE
    svg = render_incident_map(
        "The public map reads 'low', every value of which is at or above "
        "Florida's 5,000 cells/L closure trigger.")["svg"]
    for x, anchor, size, content in _text_elements(svg):
        extent = len(content) * size * MONO_ADVANCE
        left = x - extent if anchor == "end" else x
        right = x if anchor == "end" else x + extent
        assert left >= -0.5, f"text starts off-canvas at {left:.1f}: {content[:40]!r}"
        assert right <= VIEW_W + 0.5, (
            f"text overruns viewBox width {VIEW_W} to {right:.1f}: {content[:40]!r}")


def test_label_flips_only_when_it_would_otherwise_clip():
    """Tests the BRANCH, not the data. The first version of this test asserted
    that the current four sites trigger the flip; they do not on the widened
    canvas, so it failed and correctly exposed the flip as dead code for this
    input. A test that needs the data to reach a branch stops testing the branch
    the day the data moves."""
    from agents.tools import label_anchor, VIEW_W
    anchor, x = label_anchor(10.0, "Site A [low]")
    assert anchor == "start" and x == 15.0
    anchor, x = label_anchor(VIEW_W - 4, "A very long site label [not present]")
    assert anchor == "end" and x == VIEW_W - 9
    # exactly-fits stays on the right
    from agents.tools import LABEL_PT, MONO_ADVANCE
    label = "abc"
    just_fits = VIEW_W - 5 - len(label) * LABEL_PT * MONO_ADVANCE
    assert label_anchor(just_fits, label)[0] == "start"


def test_every_real_site_label_stays_on_canvas():
    """The invariant that actually matters, over the real site table."""
    from agents.tools import VIEW_W, MONO_ADVANCE
    svg = render_incident_map("x")["svg"]
    for x, anchor, size, content in _text_elements(svg):
        if "[" not in content:
            continue
        extent = len(content) * size * MONO_ADVANCE
        right = x if anchor == "end" else x + extent
        assert right <= VIEW_W + 0.5, content


def test_a_very_long_headline_is_ellipsised_not_overflowed():
    long = "word " * 200
    svg = render_incident_map(long)["svg"]
    from agents.tools import VIEW_W, MONO_ADVANCE
    for x, anchor, size, content in _text_elements(svg):
        assert x + len(content) * size * MONO_ADVANCE <= VIEW_W + 0.5
    assert "..." in svg


def test_wrap_never_returns_more_than_max_lines():
    from agents.tools import _wrap
    assert len(_wrap("a " * 500, 40, 2)) <= 2
    assert _wrap("short", 40, 2) == ["short"]
    assert _wrap("", 40, 2) == []


def test_map_grid_is_self_contained_geometry_not_an_external_asset():
    """This markup is committed into the recorded run and re-rendered through a
    sanitizer, so a CSS background-image or an external reference would be
    stripped or would silently fail to load."""
    svg = render_incident_map("x")["svg"]
    assert "<line" in svg, "no grid geometry"
    assert "url(http" not in svg and "background-image" not in svg
    assert "xlink:href" not in svg


def test_map_defs_filter_survives_the_page_sanitizer():
    """The page strips script, foreignObject, use, image and anchor tags. The
    glow uses filter + feGaussianBlur, none of which are on that list, so it
    must still be present after a round trip."""
    import xml.etree.ElementTree as ET
    NS = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(render_incident_map("x")["svg"])
    assert root.find(f".//{NS}filter") is not None
    for stripped in ("use", "image", "foreignObject", "script", "a"):
        assert root.find(f".//{NS}{stripped}") is None, f"{stripped} would be stripped"


def test_crosshairs_only_on_sites_above_the_trigger():
    """Decoration must not assert something the data does not say. A crosshair
    on a 'not present' site would claim attention the reading does not support."""
    from agents.tools import SITES
    svg = render_incident_map("x")["svg"]
    above = [s for s in SITES if s[3] not in ("not present", "very low")]
    assert svg.count("<path d=\"M ") >= len(above)
    assert len(above) == 2, "expected the two 'low' sites"
