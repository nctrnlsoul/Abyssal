"""Differential control: run TWO different 60s windows from the same recording.

A model that returns near-identical output for acoustically different windows
is answering the prompt, not the audio. That failure is invisible in a
single-sample run, and a single-sample run is what the previous version of
this project called proof. So this is the check that makes the result mean
something.

Window A is at 02:00, window B at 20:00 of the same 35-minute deployment.
"""
import os, sys, json, difflib
from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import AcousticFinding

D = r"C:\Users\brian\Projects\abyssal\data"
MODEL = "gemini-3.5-flash"

PROMPT = """You are analysing a real underwater hydrophone recording from NOAA
SanctSound monitoring site FK04, in the Florida Keys National Marine Sanctuary.
It is a 60 second window, 16 kHz mono.

Report only what you can actually hear. Do not infer ecosystem health, do not
estimate decibel levels, and do not invent a historical baseline to compare
against. If you hear nothing biological, say so.

Absolute sound pressure level cannot be computed from this file because it
carries no calibration constant. State that in the calibration_caveat field."""


def analyse(client, path):
    f = client.files.upload(file=path)
    r = client.models.generate_content(
        model=MODEL,
        contents=[PROMPT, f],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AcousticFinding,
        ),
    )
    return AcousticFinding.model_validate_json(r.text), r.usage_metadata.total_token_count


def main() -> int:
    client = genai.Client()
    results = {}
    total = 0
    for label, name in (("A (t=02:00)", "reef_window_a.wav"), ("B (t=20:00)", "reef_window_b.wav")):
        print(f"analysing window {label} ...")
        res, tok = analyse(client, os.path.join(D, name))
        results[label] = res
        total += tok

    for label, res in results.items():
        print(f"\n=== WINDOW {label} ===")
        print(json.dumps(res.model_dump(), indent=2))

    a, b = list(results.values())
    print("\n=== DIFFERENTIAL VERDICT ===")
    same_bio = set(a.biological_sounds) == set(b.biological_sounds)
    same_anthro = set(a.anthropogenic_sounds) == set(b.anthropogenic_sounds)
    ratio = difflib.SequenceMatcher(None, a.dominant_character, b.dominant_character).ratio()

    print(f"biological lists identical:    {same_bio}")
    print(f"anthropogenic lists identical: {same_anthro}")
    print(f"dominant_character similarity: {ratio:.2f}")
    print(f"density A={a.relative_biological_density}  B={b.relative_biological_density}")

    if ratio > 0.95 and same_bio and same_anthro:
        print("\nWARNING: outputs are near-identical. The model may be answering the")
        print("prompt rather than the audio. Do NOT claim real analysis on this basis.")
    else:
        print("\nPASS: the two windows produced materially different descriptions,")
        print("which is what you would expect if the model is reading the waveform.")
    print(f"\ntotal tokens across both runs: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
