# Ground truth, established by reading the document before building the agent

Every claim below was extracted from `data/nssp_2023.pdf` with PyMuPDF by
`scripts/find_biotoxin.py` and `scripts/read_biotoxin_pages.py`, before the
long-context agent existed. It exists so the agent can be GRADED rather than
trusted. An agent that cannot be graded is a demo, not a system.

Document: FDA/ISSC National Shellfish Sanitation Program Guide for the Control
of Molluscan Shellfish, 2023 Revision. **532 pages**, 297,921 Gemini tokens.

## 1. The actual closure criterion, page 70

Verbatim:

> shellstock when the Authority determines that the number of toxin-forming
> organisms in the growing waters and/or the level of biotoxin present in
> shellfish meats is sufficient to cause a health risk. The closed status shall
> be established based on the following criteria:
> (a) PSP - 80 ug saxitoxin equivalents/100 grams
> (b) NSP - 20 MU/100 grams (0.8 mg brevetoxin-2 equivalents/kg)
> (c) AZP - 0.16 mg azaspiracid-1 (AZA-1) equivalents/kg (0.16 ppm)
> (d) DSP - 0.16 mg okadaic acid (OA) equivalents/kg (0.16 ppm)
> (e) ASP - 2 mg domoic acid/100 grams (20 ppm)

**NSP is the Karenia brevis one.** The criterion is **20 MU/100 g, equal to
0.8 mg brevetoxin-2 equivalents/kg, measured in shellfish MEAT.**

## 2. The number everyone cites is not in the document

`"5,000 cells"` and `"5000 cells"` appear **ZERO times across all 532 pages.**
Searched case-insensitively with and without the comma.

`Karenia brevis` appears on exactly **4 pages: 19, 189, 195, 368.**
`brevetoxin` appears on **7 pages: 70, 189, 195, 277, 284, 364, 368.**

This confirms the FDA position that cell counts were removed from the Model
Ordinance threshold criteria. **The widely repeated "NSSP action level of
5,000 cells/L" is not a current NSSP action level.**

## 3. What 5,000 cells/L actually is

A **Florida state operational trigger**, published by FWC: shellfish harvesting
closures when *Karenia brevis* "equals or exceeds 5,000 cells/L"
(https://myfwc.com/research/redtide/statewide/). It is a state monitoring and
management threshold, executed by FDACS Division of Aquaculture. It is not the
federal action level, and the federal document does not contain it.

## 4. The nuance that makes both true at once

Page 70 says closure rests on "the number of toxin-forming organisms in the
growing waters **and/or** the level of biotoxin present in shellfish meats."
So cell density can inform the Authority's determination. But every enumerated
criterion (a) through (e) is a **toxin concentration in meat**. Cell count
informs; toxin in meat is the stated criterion.

## 5. The FWC bloom scale, for the map-versus-law gap

Units are cells per LITRE. Source: https://myfwc.com/research/redtide/statewide/

| Category | Range (cells/L) |
|---|---|
| Background / not present | <= 1,000 |
| Very low | > 1,000 to 10,000 |
| Low | > 10,000 to 100,000 |
| Medium | > 100,000 to 1,000,000 |
| High | > 1,000,000 |

**Florida's 5,000 cells/L trigger sits inside the "very low" band.** An area can
be closed to harvest while the public map reads very low.

## 6. What the agent must reproduce to pass

1. Name the NSP criterion as **20 MU/100 g (0.8 mg brevetoxin-2 equivalents/kg)**.
2. State it is measured in **shellfish meat**.
3. Report that a **cell-count threshold is absent** from the document.
4. Cite a page, and supply a **verbatim quote that is verified to exist on that
   page** by `scripts/verify_citation.py`. An unverifiable quote is a failure
   even if the substance is right.

---

## Addendum, 2026-08-28: the agent found a page this document missed

Recorded honestly, because it cuts both ways.

The first full-document run surfaced **page 359**, which I had not read when
writing sections 1 to 6 above. Verified by `scripts/verify_citation.py` as an
exact match:

> Cell counts, as measured per liter of water, are often used to trigger
> additional testing of shellfish in biotoxin monitoring programs.

That is the guidance layer that reconciles everything: cell counts trigger
**testing**, toxin in meat triggers **closure**. It is the missing hinge between
Florida's 5,000 cells/L operational trigger and the federal action level, and it
is stated in the document itself.

It also surfaced the rest of the page 70 provision, clause (2), covering
biotoxins with no established criteria:

> either cell counts of the toxin producing organism in the water column or
> biotoxin meat concentrations may be used by the Authority as the criteria for
> not allowing the harvest of shellstock

**Two lessons, and the second one matters more.**

1. The long-context stage is doing real retrieval work over 532 pages, not
   pattern-matching my prompt back at me. It returned a page I never mentioned.
2. **My ground truth was incomplete, so grading against it could have produced a
   false FAIL on a correct answer.** A hand-built answer key is itself a claim.
   When a model's citation verifies exactly against the source but contradicts
   the key, re-read the source before trusting the key. The mechanical check
   against the PDF is the authority here; this file is a convenience.
