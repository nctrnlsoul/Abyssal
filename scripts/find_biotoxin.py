"""Locate the real marine biotoxin language in the NSSP 2023 Guide.

This runs BEFORE the long-context agent exists, on purpose. If I cannot state
what the document actually says at a given page, I have no way to grade what
the model claims it says. The previous version of this project skipped this
step and shipped an invented statute.
"""
import re, sys, json
import fitz  # PyMuPDF

PDF = r"C:\Users\brian\Projects\abyssal\data\nssp_2023.pdf"

TERMS = [
    r"Karenia\s+brevis",
    r"5,?000\s+cells",
    r"brevetoxin",
    r"Marine\s+Biotoxin",
    r"NSP\b",
]

def main():
    doc = fitz.open(PDF)
    print(f"pages: {doc.page_count}")
    hits = {t: [] for t in TERMS}
    for i in range(doc.page_count):
        text = doc[i].get_text()
        for t in TERMS:
            if re.search(t, text, re.I):
                hits[t].append(i + 1)  # 1-indexed

    for t, pages in hits.items():
        shown = pages[:25]
        more = "" if len(pages) <= 25 else f" ... (+{len(pages)-25} more)"
        print(f"\n{t!r}: {len(pages)} pages -> {shown}{more}")

    # The intersection is where the actual action level should live.
    core = set(hits[r"Karenia\s+brevis"]) & set(hits[r"5,?000\s+cells"])
    print(f"\n=== PAGES CONTAINING BOTH 'Karenia brevis' AND '5,000 cells': {sorted(core)} ===")

    for p in sorted(core)[:6]:
        text = doc[p - 1].get_text()
        print(f"\n{'='*70}\nPAGE {p}\n{'='*70}")
        # print only the neighbourhood of the number, not the whole page
        for m in re.finditer(r"5,?000\s+cells", text, re.I):
            s = max(0, m.start() - 700)
            e = min(len(text), m.end() + 700)
            print(text[s:e].strip())
            print("-" * 40)

    doc.close()

if __name__ == "__main__":
    main()
