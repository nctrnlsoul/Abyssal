"""Dump the real Karenia brevis / brevetoxin / NSP passages. Ground truth."""
import re
import pymupdf

PDF = r"C:\Users\brian\Projects\abyssal\data\nssp_2023.pdf"
PAGES = [19, 70, 189, 195, 277, 284, 364, 368]
PATTERNS = r"(Karenia|brevetoxin|NSP\b|neurotoxic|mouse unit|MU/|mg/kg|action level)"

doc = pymupdf.open(PDF)
for p in PAGES:
    text = doc[p - 1].get_text()
    print(f"\n{'#'*74}\n# PAGE {p}\n{'#'*74}")
    lines = text.splitlines()
    keep, buf = [], []
    for i, ln in enumerate(lines):
        if re.search(PATTERNS, ln, re.I):
            lo, hi = max(0, i - 4), min(len(lines), i + 5)
            buf.append((lo, hi))
    # merge overlapping windows
    merged = []
    for lo, hi in buf:
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    for lo, hi in merged[:8]:
        chunk = "\n".join(l for l in lines[lo:hi] if l.strip())
        print(chunk)
        print("   " + "-" * 60)
doc.close()
