$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Real waveform, timeline spine, dual-pane evidence, global status

THE WAVEFORM IS REAL DATA. core/waveform.py computes the peak envelope of the
same 60s SanctSound clip the acoustic agent read, stdlib wave and array, no new
dependency. 320 buckets, normalized to the clip's own peak so a quiet but valid
recording does not render as a flat line. A test asserts 60s at 16 kHz and that
the envelope is not suspiciously flat. A decorative CSS sine wave would have
been easier and would have been the exact species of lie this project exists
to avoid.

A playhead sweeps it during the acoustic stage for the REAL recorded duration
between dispatch and completion, scaled by replay speed.

THE BUG THAT MATTERED, found in-browser: requestAnimationFrame is throttled to
zero in a backgrounded or non-painting tab. Measured: the sweep started, the
playhead class went on, step() never ran once, style.transform stayed empty,
and not a single bar lit. A judge who tabs away, or a screen recorder that
backgrounds the window, would have seen the waveform freeze half-drawn.

  Fix: the ANIMATION is rAF-driven, the STATE is timer-driven, plus a
  visibilitychange catch-up. Verified under the same non-painting condition
  that broke it: 0 lit bars before, 320 after.

  General rule, now a test: no visual OUTCOME may depend on a frame ever
  being painted.

ADOPTED FROM A SUGGESTION THAT WAS RIGHT ABOUT THE METAPHOR:
  - agent timeline spine that fills to the last completed node, instead of
    five unrelated boxes. Agents hand work down a pipeline, so it should read
    as one path with progress on it
  - dual pane: the exact NOAA frame the imagery agent read, beside the diagram
    it produced, so a viewer can check the reading against the source instead
    of trusting the structured output. Same principle as the citation verifier
  - a global status line, idle to executing to complete

The NOAA image is now committed (534 KB, US Government public domain). It is
date-stamped by NOAA and rotates daily, so the committed copy IS the artifact,
and a deployed instance that cannot show its own evidence is not showing
evidence.

Also: ambient depth drift, boot sequence, trace rows entering, the trigger line
drawing down into the ruler, the verdict landing, sonar ping rings on ONLY the
sites actually above the trigger. Pinging a 'not present' site would be
decoration asserting something the data does not say.

Everything degrades to a correct static end state under prefers-reduced-motion,
and a test now fails if any animation targets a class nothing carries.

A TEST OF MINE PRODUCED A FALSE POSITIVE and I fixed the test, not the code:
it flagged .trigger-label as dead because its match patterns did not cover
className = 'trigger-label draw'. The class was live; the assertion was narrow.
Bending code to satisfy a bad test is the costlier mistake.

62 tests plus 22 route assertions pass." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
git push 2>&1 | Select-Object -Last 2
