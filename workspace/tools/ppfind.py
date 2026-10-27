"""Find and render past-paper pages.
usage: ppfind.py outdir tag "relative/paper.pdf" "search text" [more tag/paper/text triples...]
Renders the first page whose text contains the search text (case-insensitive) to outdir/tag.png.
"""
import sys, os, re, subprocess, pymupdf
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())

ROOT = os.path.join(os.path.dirname(__file__), "..", "pp", "Ext 1")
out = sys.argv[1]
args = sys.argv[2:]
for i in range(0, len(args), 3):
    tag, rel, needle = args[i:i + 3]
    d = pymupdf.open(os.path.join(ROOT, rel))
    hit = None
    n = norm(needle)
    for p in d:
        txt = subprocess.run(["pdftotext", "-f", str(p.number + 1), "-l", str(p.number + 1), "-layout",
                              os.path.join(ROOT, rel), "-"], capture_output=True, text=True, errors="ignore").stdout
        if n in norm(txt) or n in norm(p.get_text()):
            hit = p
            break
    if hit is None:
        print(tag, "NOT FOUND")
        continue
    hit.get_pixmap(matrix=pymupdf.Matrix(0.95, 0.95)).save(os.path.join(out, tag + ".png"))
    print(tag, "page", hit.number + 1)
