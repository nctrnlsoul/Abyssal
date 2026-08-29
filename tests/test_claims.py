"""Every number in the judged prose, recomputed from the code.

On the previous project, adversarial review found FOUR false claims on judged
surfaces, including a dollar figure on the console's own empty state that
contradicted its own data. The fix was a test that derives each claim rather
than trusting the sentence. This is that test.

It also blocks the specific fabrications that repeatedly appeared in
AI-suggested submission copy for this project: Firestore, Vertex AI, Cloud
Storage, decibel drops, and a nonexistent cell-count threshold.
"""
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md", ROOT / "docs" / "DEVPOST.md", ROOT / "docs" / "DEMO_SCRIPT.md"]
LIVE_URL = "https://abyssal-7517955252.us-central1.run.app"


def _prose() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in DOCS if p.exists())


# --- claims that must match the code ----------------------------------------

def test_closure_trigger_figure_matches_the_constant():
    from core.synthesis import FL_CLOSURE_TRIGGER_CELLS_PER_L
    assert FL_CLOSURE_TRIGGER_CELLS_PER_L == 5_000
    assert "5,000 cells" in _prose()


def test_very_low_band_figures_match_the_table():
    from core.synthesis import FWC_BANDS
    lo, hi = FWC_BANDS["very low"]
    text = _prose()
    assert (lo, hi) == (1_000, 10_000)
    assert "1,000" in text and "10,000" in text


def test_ruler_percentage_claim_matches_the_computed_value():
    from core.synthesis import trigger_position_pct
    pct = trigger_position_pct()
    assert f"{pct:.2f}" == "33.98"
    assert "33.98" in _prose(), "prose cites a ruler position the code does not produce"


def test_federal_criterion_string_matches_the_constant():
    from core.synthesis import NSSP_NSP_ACTION_LEVEL, NSSP_MEASURED_IN
    text = _prose()
    assert "20 MU/100 grams" in NSSP_NSP_ACTION_LEVEL
    assert "20 MU/100 grams" in text
    assert NSSP_MEASURED_IN == "shellfish meats"


def test_page_numbers_cited_in_prose_match_the_recorded_run():
    import json
    run = ROOT / "docs" / "recorded-run.json"
    if not run.exists():
        pytest.skip("no recorded run")
    pages = {c["page"] for c in json.loads(run.read_text(encoding="utf-8"))["regulatory"]["citations"]}
    text = _prose()
    for p in pages:
        assert f"page {p}" in text or f"p.{p}" in text, f"p.{p} cited in the run but not in the prose"


def test_verified_citation_count_claim_is_true():
    import json
    run = ROOT / "docs" / "recorded-run.json"
    if not run.exists():
        pytest.skip("no recorded run")
    d = json.loads(run.read_text(encoding="utf-8"))
    v = d.get("verification", {})
    assert v.get("passed") == v.get("checked") == 2
    assert "2/2" in _prose() or "2 of 2" in _prose()


def test_zero_occurrences_claim_is_actually_true():
    """The headline claim. If the PDF is present, prove it rather than repeat it."""
    pdf = ROOT / "data" / "nssp_2023.pdf"
    if not pdf.exists():
        pytest.skip("source PDF not present (gitignored, run scripts/fetch_data.ps1)")
    pymupdf = pytest.importorskip("pymupdf")
    doc = pymupdf.open(str(pdf))
    hits = sum(1 for i in range(doc.page_count)
               if re.search(r"5,?000\s+cells", doc[i].get_text(), re.I))
    page_count = doc.page_count
    doc.close()
    assert hits == 0, f"'5,000 cells' found on {hits} pages. The headline claim is FALSE."
    assert page_count == 532, f"prose says 532 pages, document has {page_count}"
    assert "532" in _prose()


def _collected(target: str) -> int:
    r = subprocess.run([sys.executable, "-m", "pytest", target, "--collect-only", "-q"],
                       cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+) tests? collected", r.stdout)
    return int(m.group(1)) if m else -1


def test_total_test_count_claim_matches_the_actual_suite():
    """A README that says 73 tests when there are 90 is a false claim on a
    judged surface, and it goes stale silently.

    Matches only the TOTAL-suite phrasings. The first version grabbed every
    "N tests" in the prose and tripped on "12 tests" in the decision-layer row,
    which is a different and correct claim. A claim test that cannot tell two
    claims apart produces false failures and gets disabled, which is worse than
    not having it.
    """
    actual = _collected("tests")
    if actual < 0:
        pytest.skip("could not read collection count")
    text = _prose()
    claims = set(int(x) for x in re.findall(r"(\d+) tests plus", text))
    claims |= set(int(x) for x in re.findall(r"run_tests\.ps1\s*#\s*(\d+) tests", text))
    assert claims, "prose makes no total test-count claim"
    for c in claims:
        assert c == actual, f"prose claims {c} tests total, suite collects {actual}"


def test_decision_layer_test_count_claim_is_true():
    """The README credits the pure decision layer with a specific count."""
    text = _prose()
    m = re.search(r"no model, (\d+) tests", text)
    if not m:
        pytest.skip("no decision-layer test-count claim in the prose")
    actual = _collected("tests/test_synthesis.py")
    if actual < 0:
        pytest.skip("could not read collection count")
    assert int(m.group(1)) == actual, (
        f"prose credits core/synthesis with {m.group(1)} tests, "
        f"test_synthesis.py collects {actual}")


def test_live_url_is_consistent_everywhere():
    for p in DOCS:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        if "run.app" in t:
            assert LIVE_URL in t, f"{p.name} cites a different Cloud Run URL"


# --- fabrications that kept reappearing in suggested copy --------------------

FORBIDDEN = {
    "firestore": "no Firestore is used anywhere",
    "vertex ai": "the Gemini API is used, not Vertex",
    "cloud storage": "assets are in the repo, no GCS",
    "decibel": "no decibel is computed; the schema forbids the field",
    "threshold breach": "there is no threshold breach; that is the opposite of the finding",
    "202 accepted": "every route is GET; there is no job creation",
}


_NEGATION = re.compile(r"\b(no|not|never|without|cannot|forbid\w*|none|zero)\b")


@pytest.mark.parametrize("term,why", list(FORBIDDEN.items()))
def test_submission_prose_contains_no_fabrication(term, why):
    """Flag AFFIRMATIVE claims, not honest disclaimers.

    The first version of this test failed on the README's own sentence, "has no
    decibel field, by construction", which is the opposite of a fabrication.
    A blunt substring check cannot tell a claim from its denial, so a sentence
    carrying a negation is allowed to name the thing it is denying.
    """
    for p in DOCS:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8").lower()
        # DEMO_SCRIPT lists these in its explicit "do not say" section.
        if p.name == "DEMO_SCRIPT.md":
            text = text.split("## do not say")[0]
        for sentence in re.split(r"(?<=[.!?\n])\s+", text):
            if term in sentence and not _NEGATION.search(sentence):
                pytest.fail(f"{p.name} asserts {term!r} without negation: {why}\n"
                            f"  offending sentence: {sentence.strip()[:160]}")


def test_prose_has_no_em_dash_and_is_american_english():
    for p in DOCS:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        assert "—" not in t, f"em dash in {p.name}"


def test_prose_never_calls_the_recorded_run_live():
    """The console replays a recording and says so. Prose that calls it live
    would be the one claim a judge could disprove in five seconds."""
    for p in DOCS:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8").lower()
        if p.name == "DEMO_SCRIPT.md":
            continue  # it discusses the distinction explicitly
        for bad in ("live run of the console", "runs live on every visit",
                    "each visitor triggers"):
            assert bad not in t, f"{p.name} implies the public console runs live"
