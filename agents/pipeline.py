"""The orchestration. Real ADK Runners, real Gemini, real files.

This is the file that makes the Google agent-framework requirement true rather
than claimed. Every stage below goes through google.adk InMemoryRunner. Nothing
here is simulated and nothing is hardcoded: if the model is unreachable the
stage FAILS, it does not fall back to a canned answer.

The pipeline is deliberately shaped so the last word belongs to code:
stages 1 to 3 OBSERVE, core.synthesis DECIDES, stage 4 RENDERS what it was
handed. A model cannot revise the verdict.
"""
from __future__ import annotations
import asyncio, json, os, time
from dataclasses import dataclass, field
from typing import Callable

from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google import genai
from google.genai import types

from agents.definitions import (
    MAX_LLM_CALLS, TruncatedOutputError, build_acoustic_agent,
    build_imagery_agent, build_regulatory_agent, build_report_agent,
)
from agents.tools import REPORT_TOOLS
from core.schemas import AcousticFinding, ImageryFinding, RegulatoryFinding
from core.synthesis import Assessment, synthesise

APP = "abyssal"
DATA = os.environ.get("ABYSSAL_DATA", r"C:\Users\brian\Projects\abyssal\data")


@dataclass
class Trace:
    """Every line the console streams. Also the audit record."""
    rows: list[tuple[str, str, str]] = field(default_factory=list)

    def add(self, stage: str, level: str, msg: str) -> None:
        self.rows.append((time.strftime("%H:%M:%S"), f"{stage}:{level}", msg))

    def dump(self) -> None:
        for ts, tag, msg in self.rows:
            print(f"[{ts}] {tag:<24} {msg}")


class _Uploader:
    """Uploads once per path, per process. The 532-page PDF is 6.6 MB and
    297,921 tokens; re-uploading it per stage would be careless with both."""

    def __init__(self, client: genai.Client):
        self._client = client
        self._cache: dict[str, object] = {}

    def part(self, filename: str) -> types.Part:
        path = os.path.join(DATA, filename)
        if path not in self._cache:
            f = self._client.files.upload(file=path)
            while getattr(f.state, "name", "") == "PROCESSING":
                time.sleep(2)
                f = self._client.files.get(name=f.name)
            if getattr(f.state, "name", "") == "FAILED":
                raise RuntimeError(f"file upload failed for {filename}")
            self._cache[path] = f
        f = self._cache[path]
        return types.Part.from_uri(file_uri=f.uri, mime_type=f.mime_type)


async def _run_stage(agent, prompt: str, parts: list[types.Part],
                     session_id: str) -> str:
    """One ADK Runner, one session, one stage. Returns the final text.

    Bounded by ADK's OWN max_llm_calls rather than by breaking out of its async
    generator: abandoning that generator is what printed GeneratorExit
    tracebacks into the middle of the previous build's results table.
    """
    runner = InMemoryRunner(agent=agent, app_name=APP)
    await runner.session_service.create_session(
        app_name=APP, user_id="ops", session_id=session_id)

    msg = types.Content(role="user", parts=[types.Part(text=prompt), *parts])

    final = ""
    async for event in runner.run_async(
            user_id="ops", session_id=session_id, new_message=msg,
            run_config=RunConfig(max_llm_calls=MAX_LLM_CALLS)):
        # Detect the ceiling BEFORE the text reaches a parser. Left alone, a
        # truncated response arrives as a pydantic "Invalid JSON" three frames
        # deep, which names the schema instead of the budget. Measured trap:
        # see agents/definitions.py THINKING_BUDGET.
        for cand in (getattr(event, "candidates", None) or []):
            if str(getattr(cand, "finish_reason", "")).endswith("MAX_TOKENS"):
                raise TruncatedOutputError(
                    f"{agent.name} hit the token ceiling. Thinking tokens count "
                    f"against max_output_tokens on this model, so raise "
                    f"ABYSSAL_OUTPUT_HEADROOM or lower ABYSSAL_THINKING_BUDGET. "
                    f"This is a budget failure, not a schema failure."
                )
        if getattr(event, "content", None) and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    final = p.text
    if not final.strip():
        raise RuntimeError(f"{agent.name} produced no text")
    return final.strip()


def _parse(model_cls, text: str):
    """Structured output arrives as JSON text. Fenced output is tolerated,
    a non-conforming payload is NOT: it raises rather than degrading to a
    partial object that later reads as a real finding."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    return model_cls.model_validate_json(t)


async def run_pipeline(trace: Trace | None = None,
                       on_update: Callable[[], None] | None = None) -> dict:
    trace = trace or Trace()
    client = genai.Client()
    up = _Uploader(client)

    def step(stage, level, msg):
        trace.add(stage, level, msg)
        if on_update:
            on_update()

    # ---- stage 1, acoustic -------------------------------------------------
    step("sonar", "RUNNING", "Uploading NOAA SanctSound FK04 clip, Florida Keys NMS...")
    audio = up.part("reef_window_a.wav")
    step("sonar", "RUNNING", "ADK Runner dispatched to acoustic_auditor...")
    acoustic = _parse(AcousticFinding, await _run_stage(
        build_acoustic_agent(),
        "Analyse this 60 second, 16 kHz mono hydrophone window from NOAA "
        "SanctSound site FK04 in the Florida Keys National Marine Sanctuary.",
        [audio], "s-acoustic"))
    step("sonar", "COMPLETE",
         f"Biological: {', '.join(acoustic.biological_sounds) or 'none'}. "
         f"Anthropogenic: {', '.join(acoustic.anthropogenic_sounds) or 'none'}. "
         f"Density {acoustic.relative_biological_density}.")

    # ---- stage 2, imagery --------------------------------------------------
    step("vision", "RUNNING", "Uploading NOAA NCCOS HAB operational forecast...")
    img = up.part("hab_forecast_cellcounts.png")
    step("vision", "RUNNING", "ADK Runner dispatched to imagery_inspector...")
    imagery = _parse(ImageryFinding, await _run_stage(
        build_imagery_agent(),
        "Analyse this Karenia brevis monitoring image.",
        [img], "s-imagery"))
    step("vision", "COMPLETE",
         f"Legend: {len(imagery.legend_categories)} categories. Observed: "
         f"{', '.join(imagery.observed_categories) or 'none'}. Highest: "
         f"{imagery.highest_observed_category}. Numeric values present: "
         f"{imagery.numeric_values_present}.")

    # ---- stage 3, regulatory ----------------------------------------------
    step("regulatory", "RUNNING",
         "Uploading FDA NSSP 2023 Guide, 532 pages, 297,921 tokens...")
    pdf = up.part("nssp_2023.pdf")
    step("regulatory", "RUNNING",
         "ADK Runner dispatched to regulatory_ombudsman. Long context read...")
    regulatory = _parse(RegulatoryFinding, await _run_stage(
        build_regulatory_agent(),
        "A Florida shellfish growing area is affected by a Karenia brevis "
        "bloom. Determine what THIS DOCUMENT requires in order to close a "
        "growing area for Neurotoxic Shellfish Poisoning.",
        [pdf], "s-regulatory"))
    step("regulatory", "COMPLETE",
         f"NSP action level: {regulatory.nsp_action_level}, measured in "
         f"{regulatory.measured_in}.")
    step("regulatory", "COMPLETE",
         f"Numeric cell-count threshold present in the ordinance: "
         f"{regulatory.cell_count_threshold_present}.")

    # ---- the decision, in code, not in a model -----------------------------
    step("decide", "RUNNING", "Deterministic decision layer. No model in this step.")
    assessment: Assessment = synthesise(
        map_category=imagery.highest_observed_category,
        cell_threshold_in_federal_doc=regulatory.cell_count_threshold_present,
        federal_criterion=regulatory.nsp_action_level,
        federal_matrix=regulatory.measured_in,
    )
    step("decide", "COMPLETE", assessment.headline)

    # ---- stage 4, tool calling --------------------------------------------
    step("mapper", "RUNNING", "ADK Runner dispatched to remediation_reporter...")
    calls: list[str] = []
    results: dict[str, dict] = {}

    def _wrap(fn):
        def inner(*a, **kw):
            calls.append(fn.__name__)
            out = fn(*a, **kw)
            results[fn.__name__] = out
            step("mapper", "RUNNING", f"tool call: {fn.__name__}()")
            return out
        inner.__name__ = fn.__name__
        inner.__doc__ = fn.__doc__
        inner.__signature__ = __import__("inspect").signature(fn)
        return inner

    await _run_stage(
        build_report_agent([_wrap(f) for f in REPORT_TOOLS]),
        "Compile the advisory for this incident.\n"
        f"VERDICT (computed by code, do not revise): {assessment.headline}\n"
        f"FEDERAL CRITERION: {assessment.federal_criterion}\n"
        f"RECONCILIATION: {assessment.reconciliation}\n"
        "Call render_incident_map, then write_advisory.",
        [], "s-report")
    step("mapper", "COMPLETE", f"{len(calls)} tool calls: {', '.join(calls) or 'none'}")

    return {
        "acoustic": acoustic.model_dump(),
        "imagery": imagery.model_dump(),
        "regulatory": regulatory.model_dump(),
        "assessment": assessment.__dict__,
        "tool_calls": calls,
        "artifacts": results,
        "trace": trace.rows,
    }


if __name__ == "__main__":
    t = Trace()
    out = asyncio.run(run_pipeline(t))
    t.dump()
    print("\n=== VERDICT ===")
    print(out["assessment"]["headline"])
    print("\n=== TOOL CALLS (stage 4 function calling) ===")
    print(out["tool_calls"])
    print("\n=== ADVISORY ===")
    print(out["artifacts"].get("write_advisory", {}).get("advisory", "(none)"))
