$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Stage 3 regulatory agent: 5/5 graded checks, 2/2 citations verified

Real gemini-3.5-flash long context over the full 532-page FDA NSSP 2023
Guide. 276,840 prompt tokens, 78.3s, \$0.415 per full run.

Ground truth (docs/GROUND_TRUTH.md) was established FIRST by reading the
PDF with PyMuPDF, so the agent could be graded rather than trusted.

Model output, all five checks passed:
  NSP action level  20 MU/100 grams (0.8 mg brevetoxin-2 equivalents/kg)
  measured in       shellfish meats
  cell-count threshold present  FALSE
  all five biotoxin criteria    reproduced verbatim

Citations are machine-checked, not trusted. scripts/verify_citation.py
looks every quote up in the PDF and fails a paraphrase:
  p.70  PASS  exact match
  p.359 PASS  exact match

The headline finding is now proven from the primary source: '5,000 cells'
appears ZERO times in 532 pages. The widely repeated 'NSSP action level of
5,000 cells/L' is not an NSSP action level. It is a Florida state trigger.

The agent also surfaced p.359, which I had not read: 'Cell counts, as
measured per liter of water, are often used to trigger additional testing
of shellfish in biotoxin monitoring programs.' That is the hinge between
the state trigger and the federal criterion. Cell counts trigger TESTING;
toxin in meat triggers CLOSURE.

Logged in GROUND_TRUTH.md that a hand-built answer key is itself a claim,
and the mechanical check against the PDF outranks it." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
git push 2>&1 | Select-Object -Last 2
