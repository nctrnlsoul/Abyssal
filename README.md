# Project Abyssal

A multi-agent marine biosecurity control plane that reads the actual regulation.

**Live: https://abyssal-7517955252.us-central1.run.app**

Built for the Google All Things Agentic Hackathon. Four agents run over **real
public data**, not a simulation.

## What is real and what is not

This section exists because the honest version of it is the whole point.

| Component | Status |
|---|---|
| Hydrophone acoustic analysis | **Real.** NOAA/Navy SanctSound site FK04, Florida Keys National Marine Sanctuary. Real Gemini audio input |
| Bloom imagery analysis | **Real.** NOAA NCCOS HAB Operational Forecast and NASA MODIS. Real Gemini vision |
| Regulatory analysis | **Real.** The FDA NSSP Guide for the Control of Molluscan Shellfish, 2023 Revision, ~520 pages, 297,921 tokens. Real Gemini long context |
| Report and map generation | **Real.** Gemini function calling |
| The incident scenario | A selected case study over real archived data, not a live sensor feed. Stated plainly rather than implied otherwise |

## The finding

Florida closes shellfish harvesting areas when *Karenia brevis* reaches or exceeds
**5,000 cells per litre**. FWC's own public bloom scale puts "very low" at
1,000 to 10,000 cells/L.

The closure threshold sits *inside the very low band*. An area can be legally closed
while the public red tide map still reads "very low."

There is a second layer, and it is the one almost every secondary source gets wrong:
FDA removed cell counts from the Model Ordinance threshold criteria. 5,000 cells/L now
triggers **mandatory shellfish toxicity testing**, with the closure action level
expressed as brevetoxin in shellfish meat, not as a cell count.

Reading that correctly requires the actual 520-page ordinance. That is the job.

## Data attribution

All source data is US Government public domain.

- NOAA Office of National Marine Sanctuaries and U.S. Navy. 2020. SanctSound Raw
  Passive Acoustic Data. NOAA National Centers for Environmental Information.
  https://doi.org/10.25921/saca-sp25
- NOAA NCCOS Harmful Algal Bloom Operational Forecast System
- NASA MODIS/Terra. Image courtesy Jacques Descloitres, MODIS Land Rapid Response
  Team at NASA GSFC
- FDA/ISSC National Shellfish Sanitation Program Guide, 2023 Revision
- Florida Fish and Wildlife Conservation Commission (FWC-FWRI) red tide status data

## Spin-up

Windows, PowerShell. Every step is a script in `scripts/`.

```powershell
# 1. dependencies
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. fetch the source data (about 91 MB, from NOAA, NASA and FDA)
.\scripts\fetch_data.ps1
.\scripts\prep_audio.ps1     # cuts the 60s 16 kHz windows with ffmpeg

# 3. the console. KEYLESS: this process reads no API key.
.\scripts\serve.ps1 -Port 8080

# 4. the tests
.\scripts\run_tests.ps1      # 117 tests
.\scripts\smoke_web.ps1      # 22 route assertions
```

To run the **live** agent pipeline, which does make real Gemini calls and costs
about $0.42 for a full pass:

```powershell
# GOOGLE_API_KEY must be an OS environment variable. Never put it in a file.
.\scripts\run_pipeline.ps1   # four ADK agents, real Gemini, real files
.\scripts\record_run.ps1     # the same, saved to docs/recorded-run.json
```

`scripts/fetch_data.ps1` reproduces every source asset from its original public
URL, so the repo carries no large binaries. The two derived 60-second clips and
the NOAA forecast frame are committed, so a fresh clone can serve the console
without downloading anything.

## Deploy

```powershell
.\deploy.ps1
```

Builds from the `Dockerfile` and deploys to Cloud Run with a dedicated service
account holding **no IAM roles**, `--max-instances 3` as the spend cap, and
**no API key on the service**. The deployed image installs
`requirements-web.txt` only; `scripts/import_graph.py` proves in a fresh
interpreter that the console reaches no `google-adk`, `pymupdf` or `numpy`.

## The finding

Florida closes shellfish harvesting when *Karenia brevis* reaches or exceeds
**5,000 cells per litre**. FWC's published bloom scale puts "very low" at 1,000
to 10,000 cells/L, so **the closure trigger lands inside a published category**
and the map alone cannot tell you whether an area is closed.

And the number everyone cites is not federal. **"5,000 cells" appears zero
times in the 532-page FDA ordinance.** The actual criterion, page 70, is
`NSP - 20 MU/100 grams (0.8 mg brevetoxin-2 equivalents/kg)`, measured in
shellfish meats. Page 359 reconciles it: cell counts trigger *testing*, toxin
in meat triggers *closure*.

Full working in `docs/GROUND_TRUTH.md`, which was written by reading the PDF
**before** the agent existed, so the agent could be graded rather than trusted.

## How each stage was verified

| Stage | Result |
|---|---|
| Regulatory | 5/5 graded checks, **2/2 citations verified as exact substrings of the cited page** |
| Imagery | 7/7 graded checks, plus a differential against a second image |
| Acoustic | Differential control: two windows, same reef in both, vessel engine in one only |
| Decision | Pure Python, no model, 17 tests including the band boundaries |

## Notes for reviewers

- The console **replays a recorded real run**, labelled as recorded on the page
  and in the payload. A live run costs about $0.42 and reads 532 pages; an
  unauthenticated endpoint that spends that per click is denial-of-wallet.
- `core/schemas.py` has **no decibel field, by construction**. A SanctSound
  FLAC carries no calibration constant, so sound pressure level cannot be
  recovered from the waveform.
- The waveform on the console is a real 320-bucket peak envelope of the same
  clip the acoustic agent read, computed with stdlib `wave`.
- Zero external requests: no CDN, no webfont, no icon library.

## Licence

MIT. See LICENSE.
