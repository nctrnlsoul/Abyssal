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
