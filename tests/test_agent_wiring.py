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
