"""Check a model's quotes against the actual PDF.

The point of the whole regulatory stage is that a judge can check it. So the
quote is not trusted, it is looked up. Normalisation is deliberately mild:
whitespace and the PDF's mangled dashes/quotes are collapsed, nothing else.
A model that paraphrases fails, which is the intent.
"""
import re
import pymupdf

PDF = r"C:\Users\brian\Projects\abyssal\data\nssp_2023.pdf"


def _norm(s: str) -> str:
    s = s.replace("\u2264", "<=").replace("\u2265", ">=")
    s = re.sub(r"[\u2010-\u2015\u2212-]", "-", s)
    s = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", s)
    s = re.sub(r"[^\x20-\x7e]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def verify(page: int, quote: str, pdf_path: str = PDF) -> dict:
    doc = pymupdf.open(pdf_path)
    if not (1 <= page <= doc.page_count):
        doc.close()
        return {"ok": False, "reason": f"page {page} out of range 1..{doc.page_count}"}
    target = _norm(quote)
    on_page = _norm(doc[page - 1].get_text())
    if target and target in on_page:
        doc.close()
        return {"ok": True, "reason": f"exact match on page {page}"}
    # Where does it actually live, if anywhere?
    for i in range(doc.page_count):
        if target and target in _norm(doc[i].get_text()):
            doc.close()
            return {"ok": False, "reason": f"quote is real but on page {i+1}, not {page}"}
    doc.close()
    return {"ok": False, "reason": "quote not found anywhere in the document"}
