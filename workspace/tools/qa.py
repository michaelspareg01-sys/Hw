"""Flag raw LaTeX / unexpanded macros left in a PDF's text layer: qa.py file.pdf"""
import sys, re, pymupdf
BS = chr(92)
pat = re.compile(re.escape(BS) + r"[a-zA-Z]+|" + re.escape(BS + "(") + "|" + re.escape(BS + "[") + r"|\{\{|\}\}|\$")
d = pymupdf.open(sys.argv[1]); bad = 0
for i, p in enumerate(d):
    t = p.get_text()
    for m in pat.finditer(t):
        bad += 1; print(i + 1, repr(t[max(0, m.start() - 40):m.end() + 40]))
print(sys.argv[1], d.page_count, "pages,", bad, "problems")
