# Design brief. All five answered before any markup.

Per the Design Gate. The previous project skipped this and the vault records
what it cost.

## 1. Subject
A live operations console for a four-agent pipeline that reads real NOAA
hydrophone audio, real NOAA and NASA bloom imagery, and the real 532-page FDA
shellfish ordinance, then reports where the public red tide map and the closure
regulation disagree.

## 2. Audience
Hackathon judges, four minutes each, who have already seen fifty agent demos
today. **What they already believe: this one is also simulated.** Nearly every
multi-agent demo they have watched was a timer printing a script. That belief is
the obstacle, and it is correct often enough that they are right to hold it.

## 3. The single job, first five seconds
**Convince them it is real.** So the first thing on screen is not a hero
headline, it is verifiable evidence: a citation, its page number, and the word
VERIFIED next to it, next to the source document it was checked against. Every
other element defers to that.

## 4. One personality tension
**A confident instrument reaching a humble conclusion.** It has the posture of a
threat-detection console, and what it actually reports is "the public map cannot
tell you this." The interface is certain; the finding is about the limits of
certainty. Nothing on this page shouts CRITICAL, because the honest answer is
narrower and more interesting than an alarm.

## 5. The signature element
**The band ruler.** One horizontal scale of the five published FWC categories
with Florida's 5,000 cells/L closure trigger drawn as a hard vertical line that
lands *inside* the "very low" band. That single graphic is the entire thesis:
the category and the law do not line up.

It is built first, not last, and it is the only place the accent color is spent.

## Reference discipline
Not anchored to any dashboard or terminal template. The mechanic is the ruler
and the trace, so the mechanic is the layout. No sidebar-plus-grid.

## Decisions taken, and the conflicts behind them, surfaced not buried

**Type: system font stack, no webfont at all.**
The skill flags an open conflict on Inter (brand token vs two sources banning it
as an AI tell, Geist named instead). I am not resolving that conflict silently
and I am not adding a font request. **A separate and stronger reason: every
single external asset in the Gemini-authored draft failed to load.** Tailwind,
Font Awesome and the Google Fonts import were all wrong URLs, so the page
rendered unstyled with blank gaps. Zero external requests removes that whole
class of failure from a judged surface. Mono is used for machine data only:
trace lines, token counts, citations, page numbers. Never for labels or headings.

**Accent: this product does not use the NorthSchema maker blue.**
Per the rule that product accent is not maker accent. Abyssal gets its own,
chosen on-subject (hydrophone and sonar), and spent in exactly one place: the
band ruler.

**Field: dark.** On-subject, and the approved dark-field verdict triple is
available. Every value is computed in tests/test_palette.py, not eyeballed.

## Non-negotiables carried in
- WCAG 2.2 AA, computed in-test, not by eye.
- Meaning never carried by color alone. Every state has an icon or a word.
- prefers-reduced-motion means reduce, not kill.
- Terminal branch for empty and error states, not only the happy path.
- **Every rendered value resolves or is labelled.** A recorded run says so.
- No em dashes anywhere. American English.
