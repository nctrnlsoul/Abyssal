"""Reproduce and diagnose the stage 3 failure. Do not guess at it.

Hypothesis: gemini-3.x THINKING tokens count against max_output_tokens, so a
4096 cap that looks generous is consumed by reasoning and the visible JSON gets
cut mid-string. The smoke test passed because it set no cap at all.

If that is right, finish_reason will be MAX_TOKENS and thoughts_token_count
will be large. If it is wrong, this prints something else and I stop guessing.
"""
import os, sys, json
from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import RegulatoryFinding

PDF = r"C:\Users\brian\Projects\abyssal\data\nssp_2023.pdf"
MODEL = "gemini-3.5-flash"
PROMPT = ("A Florida shellfish growing area is affected by a Karenia brevis bloom. "
          "Determine what THIS DOCUMENT requires in order to close a growing area "
          "for Neurotoxic Shellfish Poisoning. Report only what is in the document.")

client = genai.Client()
f = client.files.upload(file=PDF)
import time
while getattr(f.state, "name", "") == "PROCESSING":
    time.sleep(2); f = client.files.get(name=f.name)

for label, cfg in [
    ("A: cap 4096, temp 0.0 (reproduces the pipeline)",
     types.GenerateContentConfig(max_output_tokens=4096, temperature=0.0,
                                 response_mime_type="application/json",
                                 response_schema=RegulatoryFinding)),
    ("B: cap 4096, temp 0.0, thinking budget 0",
     types.GenerateContentConfig(max_output_tokens=4096, temperature=0.0,
                                 response_mime_type="application/json",
                                 response_schema=RegulatoryFinding,
                                 thinking_config=types.ThinkingConfig(thinking_budget=0))),
]:
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    try:
        r = client.models.generate_content(model=MODEL, contents=[PROMPT, f], config=cfg)
        u = r.usage_metadata
        fr = r.candidates[0].finish_reason if r.candidates else None
        print(f"finish_reason      : {fr}")
        print(f"prompt tokens      : {u.prompt_token_count}")
        print(f"candidates tokens  : {u.candidates_token_count}")
        print(f"thoughts tokens    : {getattr(u, 'thoughts_token_count', None)}")
        print(f"total tokens       : {u.total_token_count}")
        text = r.text or ""
        print(f"text length        : {len(text)}")
        try:
            RegulatoryFinding.model_validate_json(text)
            print("PARSE              : OK")
        except Exception as e:
            print(f"PARSE              : FAILED {type(e).__name__}")
            print(f"tail of output     : ...{text[-120:]!r}")
    except Exception as e:
        print(f"CALL FAILED: {type(e).__name__}: {str(e)[:300]}")
