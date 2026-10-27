import sys, pymupdf as fitz
# usage: render.py pdf page(1-based) out.png [zoom] [y0frac y1frac]
pdf, pg, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
z = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
d = fitz.open(pdf); p = d[pg-1]; r = p.rect
if len(sys.argv) > 6:
    r = fitz.Rect(r.x0, r.y0 + r.height*float(sys.argv[5]), r.x1, r.y0 + r.height*float(sys.argv[6]))
p.get_pixmap(matrix=fitz.Matrix(z, z), clip=r).save(out)
