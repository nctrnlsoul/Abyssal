# Project Abyssal

A multi-agent marine biosecurity control plane that reads the actual regulation.

Built for the Google All Things Agentic Hackathon. Four agents run as long-running
background work over **real public data**, not a simulation.

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

Documented before the deadline. `scripts/fetch_data.ps1` reproduces every source
asset from its original public URL, so the repo carries no large binaries.

## Licence

MIT. See LICENSE.
