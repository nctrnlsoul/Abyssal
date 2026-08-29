"""Stage 3: real Gemini long context over the real 532-page ordinance.

Then every citation it produces is CHECKED against the PDF. The model is not
trusted, it is graded, against docs/GROUND_TRUTH.md which was written first.
"""
import os, sys, json, time
from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import RegulatoryFinding
from scripts.verify_citation import verify

PDF = r"C:\Users\brian\Projects\abyssal\data\nssp_2023.pdf"
MODEL = "gemini-3.5-flash"

PROMPT = """You are reading the FDA National Shellfish Sanitation Program (NSSP)
Guide for the Control of Molluscan Shellfish, 2023 Revision, in full.

A Florida shellfish growing area is affected by a Karenia brevis bloom. Determine
what THIS DOCUMENT actually requires in order to close a growing area for
Neurotoxic Shellfish Poisoning.

Critical instructions:
- Report only what is in this document. Do not supply outside knowledge.
- Many secondary sources state an NSSP action level of 5,000 Karenia brevis
  cells per litre. Search this document and report whether a numeric cell-count
  threshold is actually present. Do not assume it is there.
- Every verbatim_quote must be an EXACT substring of the page you cite. It will
  be checked against the PDF programmatically. Paraphrase fails.
- If something is not determinable from the document, put it in caveats."""


def main() -> int:
    client = genai.Client()
    print(f"uploading {os.path.basename(PDF)} (532 pages) ...")
    f = client.files.upload(file=PDF)
    while f.state.name == "PROCESSING":
        time.sleep(2)
        f = client.files.get(name=f.name)
    print(f"file state: {f.state.name}")

    t0 = time.time()
    resp = client.models.generate_content(
        model=MODEL,
        contents=[PROMPT, f],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RegulatoryFinding,
        ),
    )
    elapsed = time.time() - t0

    parsed = RegulatoryFinding.model_validate_json(resp.text)
    print("\n=== MODEL FINDING ===")
    print(json.dumps(parsed.model_dump(), indent=2))

    print("\n=== CITATION VERIFICATION (checked against the PDF) ===")
    passed = 0
    for c in parsed.citations:
        r = verify(c.page, c.verbatim_quote)
        mark = "PASS" if r["ok"] else "FAIL"
        passed += r["ok"]
        print(f"[{mark}] p.{c.page}  {r['reason']}")
        print(f"       {c.verbatim_quote[:150]!r}")

    print("\n=== GRADED AGAINST docs/GROUND_TRUTH.md ===")
    blob = json.dumps(parsed.model_dump()).lower()
    checks = {
        "names 20 MU/100 g":            "20 mu/100" in blob.replace(" mu /", " mu/"),
        "names 0.8 mg brevetoxin":      "0.8 mg" in blob,
        "measured in shellfish meat":   "meat" in parsed.measured_in.lower(),
        "cell-count threshold ABSENT":  parsed.cell_count_threshold_present is False,
        "at least one verified quote":  passed > 0,
    }
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")

    u = resp.usage_metadata
    print(f"\nlatency {elapsed:.1f}s | prompt={u.prompt_token_count} "
          f"output={u.candidates_token_count} total={u.total_token_count}")
    print(f"approx cost this run: ${u.prompt_token_count * 1.50 / 1_000_000:.3f}")
    print(f"\nOVERALL: {sum(checks.values())}/{len(checks)} checks passed, "
          f"{passed}/{len(parsed.citations)} citations verified")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
