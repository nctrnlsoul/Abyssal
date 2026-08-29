$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Four-stage ADK pipeline runs end to end. Mandatory requirement met.

Every stage goes through google.adk InMemoryRunner with real Gemini calls
over real files. Nothing simulated, nothing hardcoded. Full run, 3m26s:

  sonar       acoustic_auditor        snapping shrimp, vessel engine, DENSE
  vision      imagery_inspector       5 legend categories, highest 'low',
                                      numeric_values_present False
  regulatory  regulatory_ombudsman    20 MU/100 g (0.8 mg brevetoxin-2
                                      equivalents/kg); cell threshold False
  decide      core.synthesis          NO MODEL. deterministic verdict
  mapper      remediation_reporter    2 real tool calls: render_incident_map,
                                      write_advisory

Mandatory checklist: Gemini 3.5 YES, Google agent framework (ADK) YES,
Google Cloud service (Cloud Run) pending deploy.

MEASURED TRAP, and it cost real time, so it is written into the code:

  On gemini-3.x, THINKING TOKENS COUNT AGAINST max_output_tokens.
  Reproduced by scripts/diagnose_truncation.py on the 532-page ordinance:

    cap 4096, thinking on   -> MAX_TOKENS, thoughts 3928, output 152, parse FAILS
    cap 4096, thinking off  -> STOP,       output 388,                parse OK

  A cap that looks generous was 96 percent eaten by reasoning and the JSON
  was cut mid-string. It then arrives as pydantic 'Invalid JSON' three
  frames deep, which names the SCHEMA when the fault is the BUDGET.

  The fix is NOT disabling thinking: thinking is what found p.359 unprompted
  in 532 pages. The fix is an explicit thinking_budget plus an output cap
  comfortably above it, so both are bounded and neither starves the other.
  Plus TruncatedOutputError, raised on finish_reason MAX_TOKENS before any
  parser sees the text, so the failure names itself.

26 tests pass, including one asserting the cap exceeds the thinking budget
by real headroom, and one asserting every agent declares a thinking budget." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
git push 2>&1 | Select-Object -Last 2
