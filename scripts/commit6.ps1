$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Console: design gate run, brief written first, palette computed

BRIEF.md answers all five gate questions BEFORE any markup, per the rule the
previous project learned the hard way.

  single job in five seconds  convince them it is real, so the first element
                              is a VERIFIED citation with its page number,
                              not a hero headline
  signature element           the band ruler, built first, and the ONLY place
                              the accent color is spent
  tension                     a confident instrument reaching a humble
                              conclusion. nothing on the page shouts CRITICAL

THE BAND RULER. Five published FWC categories on a log axis with Florida's
5,000 cells/L trigger drawn at its COMPUTED position, 33.9794 percent, which
lands inside 'very low'. Geometry lives in core.synthesis and is asserted by
tests, including one that fails if a future rescale moves the trigger out of
that band. A linear reading would have drawn it at 28.9 percent and the
graphic would have quietly lied.

PALETTE. core/palette.py is three-tier; components reference semantic tokens.
Every contrast ratio is COMPUTED in tests/test_palette.py, never eyeballed.
Lowest pair is state-bad on field at 6.61:1 against a 4.5 requirement.
Tests also assert required tokens are PRESENT, not merely that banned ones
are absent, because an absent-only test passes on an empty file. Banned set
includes the stale NorthSchema blue, the maker blue (product accent is not
maker accent), Anthropic terracotta and cream, and Custos brass.

ZERO EXTERNAL REQUESTS. No webfont, no CDN, no icon library. Every external
asset in the draft this replaces resolved to a wrong URL and the page
rendered unstyled with blank gaps. System font stack removes that entire
failure class from a judged surface, and sidesteps the open Inter conflict
rather than resolving it silently. Mono is used for machine data only.

SECURITY. HIGHWATER's hardening ported: derived-sha256 CSP with no inline
script allowance, full header set, dual-layer rate limiter carrying the v3
fix (look up without inserting; client check before charging the global
window), generic errors on 400/404/405/500, _client inside the middleware try.
The console is KEYLESS AND SPENDLESS: it serves a recorded real run, labelled
recorded on its face. A run costs about \$0.42 and reads 532 pages, so an
unauthenticated endpoint that spends per click is denial-of-wallet, which is
exactly what the draft this replaces shipped.

FOUND BY LOOKING AT IT IN A BROWSER, not by any test:
  - grid tracks are min-width:auto, so one long mono trace line pushed the
    column past the viewport and the panel ran off the right edge
  - the trigger line overshot into the paragraph and its dot collided with
    its own label
  - at a simulated 375px the five bands compress to 68px and the wrapped
    labels clipped against a fixed 46px height

VERIFIED IN-BROWSER: 16/16 trace rows replay, all five nodes reach COMPLETE,
verdict renders, zero console errors, zero horizontal overflow at 1203px and
at a simulated 375px, no interactive target under 24px. True 375px could not
be tested by window resize because Chrome on Windows enforces a minimum
window width; the constrained-container simulation is what was measured and
that limitation is stated rather than glossed.

47 tests plus 16 route assertions pass." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
git push 2>&1 | Select-Object -Last 2
