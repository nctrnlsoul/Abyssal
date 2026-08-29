$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Stage 1 acoustic agent proven against real SanctSound audio

First real Gemini call. gemini-3.5-flash over a 60s window of NOAA/Navy
SanctSound FK04 (Florida Keys National Marine Sanctuary), structured
output validated against core/schemas.py AcousticFinding.

Result: snapping shrimp crackle dominant, DENSE biological density,
vessel engine detected. Both are correct for that site.

DIFFERENTIAL CONTROL RUN (scripts/differential_acoustic.py):
two different 60s windows from the same deployment.
  window A (t=02:00): vessel engine present
  window B (t=20:00): anthropogenic list EMPTY
  biological content identical in both (correct, same reef)
  dominant_character similarity 0.55
The constant stayed constant and the variable varied, which is the
signature of a model reading the waveform rather than the prompt.
A single-sample run could not have shown this.

Schema deliberately has NO absolute-decibel field. A SanctSound FLAC
carries no calibration constant, so SPL is not recoverable from the
waveform. The earlier Gemini-authored draft hardcoded -45.2/-78.9 dB
and a 33.7 dB drop. Those were never measurable. The schema is now
shaped so that claim cannot be expressed.

Cost: 6,736 tokens across three calls, about one cent." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
Write-Output '=== push ==='
git push 2>&1 | Select-Object -Last 3
