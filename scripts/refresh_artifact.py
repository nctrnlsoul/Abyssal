"""Regenerate the recorded run's SVG after fixing the xmlns bug.

Legitimate because render_incident_map is DETERMINISTIC: it takes the headline
and the site table and emits markup with no model in the loop. Re-running the
whole pipeline to pick up a code fix in a pure function would cost $0.42 and
change nothing else. The model outputs in the transcript are untouched.

If the tool ever stops being deterministic, delete this script and re-record.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.tools import render_incident_map, write_advisory

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "docs", "recorded-run.json")
d = json.load(open(P, encoding="utf-8"))
head = d["assessment"]["headline"]

before = len(d["artifacts"].get("render_incident_map", {}).get("svg", ""))
d["artifacts"]["render_incident_map"] = render_incident_map(head)
d["artifacts"]["write_advisory"] = write_advisory(
    head, d["assessment"]["federal_criterion"], d["assessment"]["reconciliation"])
after = len(d["artifacts"]["render_incident_map"]["svg"])

json.dump(d, open(P, "w", encoding="utf-8"), indent=2)
print(f"svg regenerated: {before} -> {after} chars")
print("xmlns present:", 'xmlns="http://www.w3.org/2000/svg"' in d["artifacts"]["render_incident_map"]["svg"])
