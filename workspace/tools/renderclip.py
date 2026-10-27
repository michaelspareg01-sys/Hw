import sys, pymupdf as fitz
# usage: renderclip.py pdf page out.png zoom x0 y0 x1 y1 (fractions)
pdf, pg, out, z = sys.argv[1], int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
fx0, fy0, fx1, fy1 = map(float, sys.argv[5:9])
p = fitz.open(pdf)[pg-1]; r = p.rect
clip = fitz.Rect(r.x0+r.width*fx0, r.y0+r.height*fy0, r.x0+r.width*fx1, r.y0+r.height*fy1)
p.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip).save(out)
