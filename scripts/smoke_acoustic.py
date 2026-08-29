"""Prove Gemini can actually analyse the real hydrophone recording.

Raw google-genai on purpose. This isolates one question, 'does the model do
anything real with this audio', from 'is the ADK wiring correct'. Building
scaffolding on an unproven premise is how the previous version of this project
ended up with four agents and no engine.
"""
import os, sys, json
from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import AcousticFinding

CLIP = r"C:\Users\brian\Projects\abyssal\data\reef_window_a.wav"
MODEL = "gemini-3.5-flash"

PROMPT = """You are analysing a real underwater hydrophone recording from NOAA
SanctSound monitoring site FK04, in the Florida Keys National Marine Sanctuary.
It is a 60 second window, 16 kHz mono.

Report only what you can actually hear. Do not infer ecosystem health, do not
estimate decibel levels, and do not invent a historical baseline to compare
against. If you hear nothing biological, say so.

Absolute sound pressure level cannot be computed from this file because it
carries no calibration constant. State that in the calibration_caveat field."""

def main() -> int:
    client = genai.Client()
    print(f"uploading {os.path.basename(CLIP)} ...")
    f = client.files.upload(file=CLIP)
    print(f"uploaded: {f.name}")

    resp = client.models.generate_content(
        model=MODEL,
        contents=[PROMPT, f],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AcousticFinding,
        ),
    )
    print("\n--- RAW MODEL OUTPUT ---")
    print(resp.text)

    parsed = AcousticFinding.model_validate_json(resp.text)
    print("\n--- PARSED AND SCHEMA-VALID ---")
    print(json.dumps(parsed.model_dump(), indent=2))

    u = resp.usage_metadata
    print(f"\ntokens: prompt={u.prompt_token_count} output={u.candidates_token_count} total={u.total_token_count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
