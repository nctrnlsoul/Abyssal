"""Stage 2: real Gemini vision, graded against what I confirmed is in the images.

Runs BOTH images. Same differential logic as the acoustic stage: a categorical
monitoring map and a true-colour satellite capture are different objects, so
near-identical output would mean the model is answering the prompt.
"""
import os, sys, json, difflib
from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import ImageryFinding

D = r"C:\Users\brian\Projects\abyssal\data"
MODEL = "gemini-3.5-flash"

PROMPT = """Analyse this image, which relates to Karenia brevis (Florida red tide)
monitoring.

Report only what is actually visible. Specifically:
- Read the legend if there is one, and list its categories in order.
- List only the categories you can actually see plotted as samples.
- A coloured category marker is NOT a numeric value. Set numeric_values_present
  to true only if real numbers are legible in the image.
- Do not estimate a cells-per-litre figure from a colour. If the image does not
  state a number, it does not have one.
- In determinability_caveat, say plainly whether a shellfish harvesting closure
  decision could be made from this image alone."""


def analyse(client, path):
    f = client.files.upload(file=path)
    r = client.models.generate_content(
        model=MODEL,
        contents=[PROMPT, f],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ImageryFinding,
        ),
    )
    return ImageryFinding.model_validate_json(r.text), r.usage_metadata.total_token_count


def main() -> int:
    client = genai.Client()
    results, total = {}, 0
    for label, name in (("NOAA map", "hab_forecast_cellcounts.png"),
                        ("NASA MODIS", "nasa_modis_redtide_2001.jpg")):
        print(f"analysing {label} ...")
        res, tok = analyse(client, os.path.join(D, name))
        results[label] = res
        total += tok

    for label, res in results.items():
        print(f"\n=== {label} ===")
        print(json.dumps(res.model_dump(), indent=2))

    noaa = results["NOAA map"]
    nasa = results["NASA MODIS"]

    print("\n=== GRADED AGAINST THE IMAGE I INSPECTED ===")
    legend = " | ".join(noaa.legend_categories).lower()
    checks = {
        "legend has 5 categories":        len(noaa.legend_categories) == 5,
        "legend includes 'not present'":  "not present" in legend,
        "legend includes 'very low'":     "very low" in legend,
        "legend includes 'high'":         "high" in legend,
        "no numeric values on the map":   noaa.numeric_values_present is False,
        "highest observed is not medium/high":
            noaa.highest_observed_category.lower() not in ("medium", "high"),
        "caveat says closure NOT determinable":
            any(w in noaa.determinability_caveat.lower()
                for w in ("cannot", "not possible", "insufficient", "no ", "not determin")),
    }
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")

    print("\n=== DIFFERENTIAL (map vs satellite) ===")
    ratio = difflib.SequenceMatcher(None, noaa.spatial_summary, nasa.spatial_summary).ratio()
    print(f"image_kind:  NOAA={noaa.image_kind!r}")
    print(f"             NASA={nasa.image_kind!r}")
    print(f"legend sizes: NOAA={len(noaa.legend_categories)} NASA={len(nasa.legend_categories)}")
    print(f"spatial_summary similarity: {ratio:.2f}")
    differential_ok = ratio < 0.90 and noaa.image_kind.lower() != nasa.image_kind.lower()
    print(f"  [{'PASS' if differential_ok else 'FAIL'}] outputs track the input, not the prompt")

    print(f"\ntokens across both: {total}")
    print(f"\nOVERALL: {sum(checks.values())}/{len(checks)} graded checks, "
          f"differential {'PASS' if differential_ok else 'FAIL'}")
    return 0 if all(checks.values()) and differential_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
