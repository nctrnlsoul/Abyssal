$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
git commit -m "Render the generated artifact, add scanlines, glow, streaming and pulse

THE REAL GAP, not a style preference: stage 4 called render_incident_map and
produced a real SVG that the console then threw away. The pipeline generated
an artifact and the UI discarded it. Now rendered, with the advisory beside it.

Visual additions, all pure CSS or DOM, zero external requests:
  scanlines            fixed overlay, pointer-events none, kept faint so it
                       does not fight the contrast the palette tests enforce
  accent glow          on the trigger line, its label, h1 and the straddling
                       band. Accent still spent in ONE place
  streaming trace      characters reveal with a caret, like a terminal
  running pulse        amber node pulse. cause and effect, not decoration

prefers-reduced-motion is honored as REDUCE, not kill: the pulse stops and the
trace appears instantly, while scanlines, glow, color, layout and the replay
itself all remain. Killing motion outright would leave a viewer with the
setting on staring at a dead page.

TWO BUGS FOUND BY LOOKING AT THE PAGE, both invisible to a string assertion:

1. The generated SVG had NO xmlns. HTML's parser infers the SVG namespace for
   a bare <svg>, so the markup was valid and rendered fine inline, then parsed
   into the NULL namespace through DOMParser and the browser laid the entire
   diagram out as FLOWING TEXT. No error, no warning. Fixed at the source and
   the page now rejects any root outside the SVG namespace so the failure
   surfaces as 'did not parse' rather than as garbled text.

2. Labels and the headline overran the viewBox and were silently clipped:
   'Jacksonville / St Augustine [' just stopped. Canvas widened, headline
   wrapped on a character budget with ellipsis, and the overrun invariant is
   now asserted from monospace advance width instead of eyeballed.

A THIRD THING THE TESTS CAUGHT ON THEMSELVES: the first flip test asserted
that the current four sites trigger the label flip. On the widened canvas they
do not, so it failed and correctly exposed the flip as dead code for this
input. Rewrote it to test the BRANCH via label_anchor() directly. A test that
needs the data to reach a branch stops testing the branch the day data moves.

Injection is parsed and scrubbed, never innerHTML: DOMParser, namespace check,
strip script/foreignObject/use/image/a and every on* handler, href and style,
then importNode. 'Our own code generated it' is the assumption that stops
being true one refactor later.

59 tests pass." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
git push 2>&1 | Select-Object -Last 2
