$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Stage 2 vision (7/7 + differential) and the pure decision layer (12 tests)

STAGE 2, real gemini-3.5-flash vision, graded against the images after I
inspected them myself:
  legend read correctly, all 5 categories in order
  observed categories 'not present' and 'low' only
  numeric_values_present FALSE (the map shows colour bands, not numbers)
  closure correctly reported as NOT determinable from the image alone
  7/7 graded checks

DIFFERENTIAL: the NOAA categorical map and the NASA true-colour capture
produced different image_kind, different legend sizes (5 vs 0), and
spatial_summary similarity 0.39. Output tracks the input, not the prompt.

DECISION LAYER, core/synthesis.py: pure, deterministic, no model, no IO.
The agents observe; this decides. The headline claim is computed from
published numeric bands by readable code, so swapping the model cannot
change the verdict.

    not present     0 to 1,000          BELOW
    very low    1,000 to 10,000         STRADDLES
    low        10,000 to 100,000        ABOVE
    medium    100,000 to 1,000,000      ABOVE
    high    1,000,000 to unbounded      ABOVE

Exactly one published category is ambiguous, and a test asserts that, so a
future FWC rescale fails loudly instead of letting the headline keep
claiming a clean gap.

12 tests pass. One failed first and the TEST was wrong, not the code: it
asserted 'trigger CLOSURE' against text reading 'triggers CLOSURE'. Fixed
the assertion rather than bending the code, and left the note in the test." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
git push 2>&1 | Select-Object -Last 2
