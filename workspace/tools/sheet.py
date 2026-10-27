"""Render PDF pages into 2-up contact sheets: sheet.py file.pdf outprefix [zoom] [first last]"""
import sys, pymupdf as fitz
pdf, pre = sys.argv[1], sys.argv[2]
z = float(sys.argv[3]) if len(sys.argv) > 3 else 0.85
d = fitz.open(pdf)
a = int(sys.argv[4]) if len(sys.argv) > 4 else 1
b = int(sys.argv[5]) if len(sys.argv) > 5 else d.page_count
pages = list(range(a - 1, b))
for k in range(0, len(pages), 2):
    pair = pages[k:k + 2]
    pm = [d[i].get_pixmap(matrix=fitz.Matrix(z, z)) for i in pair]
    w = sum(p.width for p in pm) + 10 * (len(pm) - 1); h = max(p.height for p in pm)
    out = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, w, h), False); out.clear_with(200)
    x = 0
    for p in pm:
        p2 = fitz.Pixmap(fitz.csRGB, p) if p.n != 3 else p
        p2.set_origin(x, 0); out.copy(p2, p2.irect); x += p.width + 10
    out.save(f"{pre}{pair[0]+1:02d}.png")
