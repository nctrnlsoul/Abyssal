"""The four ADK agents. This file is what satisfies the Google agent-framework
requirement, and it is the part the previous draft of this project faked.

Two hard lessons from the previous build are encoded here rather than
remembered:

1. ADK rejects an agent name that is not a valid Python identifier, at
   LlmAgent construction. A hyphen killed every live run there while eight
   structural tests stayed green, because not one of them ever CONSTRUCTED an
   agent. tests/test_agent_wiring.py calls every factory in this file.

2. A model-spending product with no cap on its own spend is denial-of-wallet.
   Every agent carries max_output_tokens, and the pipeline carries ADK's own
   max_llm_calls. The 520-page document makes this the expensive project it
   would be careless not to bound.
"""
from __future__ import annotations
import os

from google.adk.agents import LlmAgent
from google.genai import types

from core.schemas import AcousticFinding, ImageryFinding, RegulatoryFinding

MODEL = os.environ.get("ABYSSAL_MODEL", "gemini-3.5-flash")
MAX_LLM_CALLS = int(os.environ.get("ABYSSAL_MAX_LLM_CALLS", "12"))

# THE TRAP, measured on 2026-08-28, not guessed at.
#
# On gemini-3.x, THINKING TOKENS COUNT AGAINST max_output_tokens. Reproduced
# with scripts/diagnose_truncation.py against the 532-page ordinance:
#
#   max_output_tokens=4096, thinking on   -> finish_reason MAX_TOKENS
#                                            thoughts 3,928, output 152, parse FAILS
#   max_output_tokens=4096, thinking off  -> finish_reason STOP
#                                            output 388, parse OK
#
# A cap that looks generous was 96% eaten by reasoning, and the JSON was cut
# mid-string. It then surfaces as pydantic "Invalid JSON", which sends you
# looking at the schema instead of the budget. That is the whole danger: the
# error names the wrong thing.
#
# The fix is NOT to disable thinking. Thinking is what let this model find
# page 359 unprompted in a 532-page document, which is the best result in the
# project. The fix is to budget thinking EXPLICITLY and set the output cap
# comfortably above it, so both are bounded and neither starves the other.
THINKING_BUDGET = int(os.environ.get("ABYSSAL_THINKING_BUDGET", "4096"))
OUTPUT_HEADROOM = int(os.environ.get("ABYSSAL_OUTPUT_HEADROOM", "4096"))
MAX_OUTPUT_TOKENS = THINKING_BUDGET + OUTPUT_HEADROOM


class TruncatedOutputError(RuntimeError):
    """Raised when a stage hit the token ceiling.

    Exists so this failure NAMES ITSELF. Left alone it arrives as a JSON parse
    error three frames deep inside pydantic, and the previous forty minutes of
    this build were spent because the message pointed at the wrong subsystem.
    """


# temperature 0.0 throughout: a regulatory finding that changes between runs is
# not a finding. It also makes the citation verifier's PASS meaningful.
def _cfg(headroom: int | None = None) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        max_output_tokens=THINKING_BUDGET + (headroom or OUTPUT_HEADROOM),
        temperature=0.0,
        thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
    )


ACOUSTIC_INSTRUCTION = """You analyse underwater hydrophone recordings from NOAA
SanctSound monitoring stations.

Report only what is audibly present. Do not infer ecosystem health from a single
window. Do not estimate decibel levels and do not invent a historical baseline
to compare against: you have not been given one.

Absolute sound pressure level cannot be computed from these files because they
carry no calibration constant. Say so in calibration_caveat every time."""


IMAGERY_INSTRUCTION = """You analyse Karenia brevis monitoring imagery: public
categorical bloom maps and satellite captures.

Read the legend if one exists and list its categories in order. List only the
categories you can actually see plotted.

A coloured category marker is NOT a numeric value. Set numeric_values_present to
true only if real numbers are legible in the image. Never estimate a
cells-per-litre figure from a colour: if the image does not state a number, it
does not have one.

In determinability_caveat, say plainly whether a shellfish harvesting closure
decision could be made from this image alone."""


REGULATORY_INSTRUCTION = """You read the FDA National Shellfish Sanitation
Program Guide for the Control of Molluscan Shellfish in full and report what it
actually requires.

Report only what is in the document. Do not supply outside knowledge.

Many secondary sources state an NSSP action level of 5,000 Karenia brevis cells
per litre. Search the document and report whether a numeric cell-count threshold
is actually present. Do not assume it is there.

Every verbatim_quote must be an EXACT substring of the page you cite. Quotes are
checked against the PDF programmatically and a paraphrase fails. If something is
not determinable from the document, put it in caveats rather than filling the
gap."""


REPORT_INSTRUCTION = """You compile the final incident advisory from findings
that have already been established by other agents and by a deterministic
decision layer.

You have tools. Use them:
1. render_incident_map to draw the affected area
2. write_advisory to emit the advisory text

Do NOT restate a cells-per-litre number that was not given to you, and do not
soften or strengthen the verdict you were handed. The verdict was computed by
code, not by a model, and it is not yours to revise. Your job is to render it."""


def build_acoustic_agent() -> LlmAgent:
    return LlmAgent(
        name="acoustic_auditor",
        model=MODEL,
        instruction=ACOUSTIC_INSTRUCTION,
        output_schema=AcousticFinding,
        output_key="acoustic",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        generate_content_config=_cfg(),
    )


def build_imagery_agent() -> LlmAgent:
    return LlmAgent(
        name="imagery_inspector",
        model=MODEL,
        instruction=IMAGERY_INSTRUCTION,
        output_schema=ImageryFinding,
        output_key="imagery",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        generate_content_config=_cfg(),
    )


def build_regulatory_agent() -> LlmAgent:
    return LlmAgent(
        name="regulatory_ombudsman",
        model=MODEL,
        instruction=REGULATORY_INSTRUCTION,
        output_schema=RegulatoryFinding,
        output_key="regulatory",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        generate_content_config=_cfg(8192),
    )


def build_report_agent(tools: list) -> LlmAgent:
    return LlmAgent(
        name="remediation_reporter",
        model=MODEL,
        instruction=REPORT_INSTRUCTION,
        tools=tools,
        generate_content_config=_cfg(),
    )


#: Every factory in this module, so a test cannot forget one.
ALL_FACTORIES = {
    "acoustic_auditor": build_acoustic_agent,
    "imagery_inspector": build_imagery_agent,
    "regulatory_ombudsman": build_regulatory_agent,
}
