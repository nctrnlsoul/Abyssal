# Project Abyssal

**Live:** https://abyssal-7517955252.us-central1.run.app
**Repo:** https://github.com/nctrnlsoul/Abyssal

## What it does

Four agents read three kinds of real public data and report where Florida's
public red tide map and the federal shellfish regulation disagree.

Not a chatbot, and not a simulation. Every stage runs on Gemini 3.5 through the
Google Agent Development Kit against files you can download yourself.

## The finding

Florida closes shellfish harvesting areas when *Karenia brevis* reaches or
exceeds **5,000 cells per liter**. FWC's own published bloom scale puts
"very low" at 1,000 to 10,000 cells/L.

**The closure trigger lands inside a published category.** A sample shown as
"very low" on the public map may sit either side of it. The category alone
cannot tell you whether an area is closed. That is the signature graphic on the
console: five bands, one line, drawn at its computed log position of 33.98%.

There is a second layer, and it is the one most secondary sources get wrong.
The regulatory agent read all 532 pages of the FDA National Shellfish
Sanitation Program Guide, 2023 Revision, and reported that **no numeric
cell-count threshold exists in it.** Verified independently: the string
"5,000 cells" appears **zero times** in the document. The actual federal
criterion, on page 70, is:

> NSP - 20 MU/100 grams (0.8 mg brevetoxin-2 equivalents/kg)

measured in shellfish **meats**, not in water. The agent also surfaced page 359
unprompted, which reconciles the two:

> Cell counts, as measured per liter of water, are often used to trigger
> additional testing of shellfish in biotoxin monitoring programs.

**Cell counts trigger testing. Toxin in meat triggers closure.** The widely
cited "NSSP action level of 5,000 cells/L" is a Florida state operational
trigger, not a federal action level.

## How it was verified, which is the point

An agent that cannot be graded is a demo. So every stage was graded against
ground truth established **before** the agent existed.

**Regulatory, 5 of 5 graded checks, 2 of 2 citations verified.**
`docs/GROUND_TRUTH.md` was written first by reading the PDF with PyMuPDF.
Then `scripts/verify_citation.py` looks up every quote the model produced as an
exact substring of the page it cited. A paraphrase fails. Both quotes matched
exactly, on p.70 and p.359. That result is on the console before you scroll.

**Acoustic, verified by differential control.** A single sample cannot
distinguish a model reading a waveform from a model answering the prompt, so
two different 60-second windows from the same NOAA deployment were run:

| | Window A (t=02:00) | Window B (t=20:00) |
|---|---|---|
| biological | snapping shrimp crackle | snapping shrimp crackle |
| anthropogenic | **vessel engine** | **empty** |

The constant stayed constant and the variable varied. Same reef in both, the
passing vessel in one.

**Imagery, 7 of 7 graded checks plus a differential.** The agent read all five
legend categories in order, reported `numeric_values_present: false`, and stated
that a closure decision cannot be made from the image alone. The NOAA map and a
NASA satellite capture produced different `image_kind` and legend sizes.

## Architecture

**The agents observe. Code decides.**

`core/synthesis.py` is pure: no model, no network, no IO. It computes the
verdict from published numeric bands, so **swapping the model cannot change the
conclusion.** The agents supply observations; the decision is readable Python
with 12 tests on it, including one that fails loudly if a future FWC rescale
moves the trigger out of the "very low" band.

Four ADK `LlmAgent`s driven by `InMemoryRunner`:

- `acoustic_auditor` reads a NOAA/Navy SanctSound recording from site FK04 in
  the Florida Keys National Marine Sanctuary
- `imagery_inspector` reads the NOAA NCCOS harmful algal bloom forecast
- `regulatory_ombudsman` reads the full 532-page FDA ordinance, 297,921 tokens
- `remediation_reporter` renders the output through real function calling

**The schema forbids the lie.** `AcousticFinding` has no decibel field, by
construction: a SanctSound FLAC carries no calibration constant, so sound
pressure level is not recoverable from the waveform. An earlier draft of this
project hardcoded a "-33.7 dB drop". That number was never measurable from any
input. The schema is shaped so the claim cannot be expressed.

## Security, on a public URL

The console is **keyless and spendless**. It reads no API key, none is baked
into the image, and none is set on the service. Every route is GET and there is
no job creation, so there is no job store to exhaust.

That is deliberate. A live run reads a 532-page document and costs about $0.42.
An unauthenticated endpoint that spends that per click is denial-of-wallet. So
the public console replays a **real recorded run**, labelled recorded on its
face, with its real timings and real outputs. The live path is
`agents/pipeline.py`, in the repo, and it is what produced the transcript.

Also shipped: a dedicated Cloud Run service account holding **no IAM roles**
(without one, a revision runs as project Editor, mintable from the metadata
server), `--max-instances` as the spend cap, a CSP with no inline-script
allowance whose hash is derived from the shipped file at startup, a dual-layer
rate limiter, and generic errors on every status. `scripts/import_graph.py`
proves in a fresh interpreter that the public console reaches no `google-adk`,
no `pymupdf` and no `numpy`, so the deployed image installs none of them.

## Two platform findings worth passing on

**`requestAnimationFrame` is throttled to zero in a backgrounded tab.**
Measured here: the waveform sweep started, the playhead class applied, and
`step()` never ran once, so not one bar lit. Fixed by splitting responsibility.
The animation is frame-driven; the state is timer-driven, with a
`visibilitychange` catch-up. **No visual outcome depends on a frame being
painted**, and there is a test enforcing it.

**The Google Front End intercepts `/healthz` on Cloud Run.** It serves its own
404 and the request never reaches the container. Proved by comparing bodies on
the live URL: `/healthz` returns Google's HTML, while `/nope`, `/health` and
`/api/healthz` all return the application's JSON. Any liveness probe on that
path reports a healthy service as down.

## Data

All US Government public domain, and reproducible with `scripts/fetch_data.ps1`.

- NOAA Office of National Marine Sanctuaries and U.S. Navy. 2020. SanctSound
  Raw Passive Acoustic Data. NOAA NCEI. https://doi.org/10.25921/saca-sp25
- NOAA NCCOS Harmful Algal Bloom Operational Forecast System
- NASA MODIS/Terra, image courtesy Jacques Descloitres, MODIS Land Rapid
  Response Team at NASA GSFC
- FDA and ISSC, NSSP Guide for the Control of Molluscan Shellfish, 2023 Revision
- Florida Fish and Wildlife Conservation Commission (FWC-FWRI)

## Built with

Gemini 3.5 Flash, Google Agent Development Kit, Google Cloud Run, FastAPI,
Pydantic, PyMuPDF.

**103 tests plus 22 route assertions.** Zero external requests on the console:
no CDN, no webfont, no icon library.

## Honest limits, stated rather than discovered

- The console replays a recorded run. It says so on its face and in the payload.
- The site diagram is schematic, not georeferenced, and implies no cell counts.
- The advisory is not an official determination. Harvesting area status is set
  by the Florida Department of Agriculture and Consumer Services, Division of
  Aquaculture.
- The rate limiter is in-process, so it is per-instance. `--max-instances`
  bounds the real total.
- The NOAA forecast image is date-stamped and rotates daily, so the committed
  copy is the artifact.
