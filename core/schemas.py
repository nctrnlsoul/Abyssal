"""Structured output contracts between pipeline stages.

Every field here is something the model can actually ground in the input.
There is deliberately NO absolute-decibel field: a SanctSound FLAC carries no
calibration constant, so sound pressure level cannot be recovered from the
waveform alone. An earlier draft of this project reported "-45.2 dB baseline,
-78.9 dB current, 33.7 dB drop" as hardcoded values. Those numbers were not
measurable from the input and were not measured. The schema is shaped so that
class of claim cannot be expressed.
"""
from __future__ import annotations
from pydantic import BaseModel, Field


class AcousticFinding(BaseModel):
    """What is audibly present in a hydrophone recording."""
    biological_sounds: list[str] = Field(
        description="Biological sound types actually audible, e.g. snapping shrimp "
                    "crackle, fish chorus, cetacean vocalisation. Empty if none heard."
    )
    anthropogenic_sounds: list[str] = Field(
        description="Human-origin sounds actually audible, e.g. vessel engine, "
                    "sonar ping, mooring noise. Empty if none heard."
    )
    dominant_character: str = Field(
        description="One sentence on what dominates the recording overall."
    )
    relative_biological_density: str = Field(
        description="Qualitative only: SPARSE, MODERATE, or DENSE biological activity "
                    "relative to a typical reef soundscape."
    )
    calibration_caveat: str = Field(
        description="State plainly that absolute sound pressure level cannot be "
                    "derived without the deployment calibration constant, which is "
                    "not present in this file."
    )
    confidence: str = Field(description="LOW, MEDIUM, or HIGH, in this assessment.")


class RegulatoryCitation(BaseModel):
    """One located provision, shaped so it can be mechanically verified."""
    page: int = Field(
        description="1-indexed PDF page the provision appears on."
    )
    verbatim_quote: str = Field(
        description="An EXACT substring copied from that page, 20 to 400 characters. "
                    "Do not paraphrase, reformat, fix typos, or join across pages. "
                    "This string is checked against the PDF text; a quote that "
                    "cannot be found is treated as a failure."
    )
    provision_reference: str = Field(
        description="The section, chapter and paragraph label as written in the "
                    "document, e.g. 'Section II Model Ordinance Chapter IV @ .04'."
    )


class RegulatoryFinding(BaseModel):
    """What the ordinance actually says about closing shellfish areas for NSP."""
    nsp_action_level: str = Field(
        description="The stated action level for Neurotoxic Shellfish Poisoning, "
                    "with its units exactly as the document expresses them."
    )
    measured_in: str = Field(
        description="What matrix the action level is measured in: shellfish meat, "
                    "growing water, or something else. Quote the document's own wording."
    )
    cell_count_threshold_present: bool = Field(
        description="True only if the document states a numeric Karenia brevis "
                    "cell-count threshold. Search before answering. If no numeric "
                    "cell-count threshold appears anywhere, this is False."
    )
    cell_count_explanation: str = Field(
        description="Explain what the document does and does not say about using "
                    "organism counts in growing waters, quoting its wording."
    )
    all_biotoxin_criteria: list[str] = Field(
        description="Every enumerated biotoxin closure criterion, verbatim."
    )
    citations: list[RegulatoryCitation] = Field(
        description="At least one, supporting the action level. Quotes must be exact."
    )
    caveats: str = Field(
        description="Anything you could not determine from the document. Say so "
                    "plainly rather than filling the gap."
    )
