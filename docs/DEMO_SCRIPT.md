# Demo script, 4 minutes

Target 3:45 so a slow load does not push you over. Record at 1440x900 or wider.

**Before recording**
- Open https://abyssal-7517955252.us-central1.run.app and hard refresh once so
  the 534 KB source image is warm. A cold Cloud Run start plus that image is
  the only thing that can make the opening look slow.
- Leave Speed at 8x. The replay is then about 15 seconds.
- Do not narrate the URL bar. Judges can see it.

**The one rule:** never say "live run". It is a recorded run and the page says
so. Getting caught softening that would cost more than the sentence buys.

---

## 0:00 to 0:35  The problem, not the product

> "Florida closes shellfish harvesting when red tide reaches five thousand
> cells per liter. But the public map does not show you a number. It shows you
> a category."

**SHOT: the band ruler, full width. Do not scroll past it. This is the whole
project in one graphic.**

> "Here are the five published categories, and here is the closure line. It
> lands *inside* very low. So a beach shown as very low on the public map might
> be open, or it might be legally closed, and the map cannot tell you which."

Pause on the ruler for a full two seconds. It is the thing they will remember.

---

## 0:35 to 1:15  What it reads

**SHOT: scroll slowly to the agent pipeline, then the trace panel.**

> "Abyssal reads three real sources to settle that. A NOAA hydrophone recording
> from the Florida Keys National Marine Sanctuary. The NOAA harmful algal bloom
> forecast. And all five hundred and thirty two pages of the FDA shellfish
> ordinance."

**SHOT: press Replay run. Let the trace stream.**

> "Four agents on the Google Agent Development Kit. This is a recorded run
> replaying at eight times speed, and those are the real elapsed seconds from
> when it executed."

---

## 1:15 to 2:00  The waveform, because it proves the point

**SHOT: the hydrophone panel while the playhead sweeps.**

> "That is not a decorative animation. It is a three hundred and twenty bucket
> peak envelope computed from the actual sixty second clip the acoustic agent
> analyzed, with Python's standard wave library."

> "And we did not trust one sample. We ran two different windows from the same
> deployment. Both heard snapping shrimp, because it is the same reef. Only one
> heard a vessel engine. The constant stayed constant and the variable varied,
> which is what tells you the model is reading the waveform and not the prompt."

---

## 2:00 to 3:00  The finding. This is the money.

**SHOT: scroll up to the two green VERIFIED p.70 badges.**

> "The regulatory agent read the full ordinance and reported that no numeric
> cell count threshold exists in it. We checked. The string five thousand cells
> appears zero times across all five hundred and thirty two pages."

> "The real federal criterion is on page seventy: twenty mouse units per hundred
> grams of brevetoxin, measured in shellfish meat, not in water."

**SHOT: point at the VERIFIED badges.**

> "And we do not take that on trust. Every quote is looked up as an exact
> substring of the page it cites. A paraphrase fails. Two of two verified."

> "The agent also found page three fifty nine on its own, which reconciles the
> whole thing. Cell counts trigger testing. Toxin in meat triggers closure. The
> five thousand figure everyone cites is a Florida state trigger, not a federal
> action level."

---

## 3:00 to 3:30  Why the conclusion is trustworthy

**SHOT: the dual pane, source NOAA frame beside the generated diagram.**

> "On the left is the exact frame the imagery agent read. On the right is what
> it produced. You can check the reading against the source."

> "And the verdict itself is not written by a model. The agents observe; a pure
> deterministic layer decides, from published numeric bands. Swapping the model
> cannot change the conclusion."

---

## 3:30 to 3:45  Close

> "It is deployed on Cloud Run with a service account that holds no roles, a
> hard instance cap, and no API key on the service at all, so the public console
> cannot spend money. Ninety tests. Every source file is public domain
> and reproducible from the repo."

> "Abyssal does not tell you there is a crisis. It tells you the map and the law
> disagree, and it shows you the page."

---

## Cut order if you run long

Cut in this order. Never cut the first two.

1. **Never cut:** the band ruler at 0:00, or the VERIFIED badges at 2:00. Those
   two are the entire submission.
2. Cut the dual pane paragraph at 3:00 first.
3. Then the differential control detail at 1:40, keeping "computed from the
   actual clip".
4. Then the security sentence at 3:30, keeping "ninety one tests".

## Do not say

- "live run" or "real time". It is a recorded run.
- "crisis", "critical", "emergency". The finding is that the map is ambiguous,
  not that anything is on fire. Overclaiming here contradicts the product.
- "decibel", "cell density", "threshold breach". None of those are computed and
  the schema forbids the first one.
- "Firestore", "Vertex AI", "Cloud Storage". None are used.
