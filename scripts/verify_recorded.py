"""Verify the recorded run's citations against the PDF and store the result.

This is what the console shows first. The brief's single job is 'convince them
it is real in five seconds', and the only thing that does that is a citation,
its page, and a verdict that came from looking it up rather than from a model
claiming it.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.verify_citation import verify

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "docs", "recorded-run.json")

d = json.load(open(P, encoding="utf-8"))
out = []
for c in d["regulatory"]["citations"]:
    r = verify(c["page"], c["verbatim_quote"])
    out.append({**c, "verified": r["ok"], "verify_reason": r["reason"]})
    print(f"[{'PASS' if r['ok'] else 'FAIL'}] p.{c['page']}  {r['reason']}")

d["regulatory"]["citations"] = out
d["verification"] = {
    "checked": len(out),
    "passed": sum(1 for c in out if c["verified"]),
    "source_document": "FDA NSSP Guide for the Control of Molluscan Shellfish, 2023 Revision",
    "source_pages": 532,
    "method": "each quote looked up as an exact substring of the cited PDF page",
}
json.dump(d, open(P, "w", encoding="utf-8"), indent=2)
print(f"\n{d['verification']['passed']}/{d['verification']['checked']} verified. wrote {P}")
