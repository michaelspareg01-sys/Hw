"""Figures for Lesson 3 (problem solving) and the chapter review. Run after figs.py: python3 figs_l3.py

l3_bp  Sydney Grammar 2025 Q6(e): parallel box plots redrawn from the paper (five-number summaries read
       from the scan at zoom 3: French 50, 60, 70, 80, 95; Geography 55, 70, 80, 90, 100), to scale.
       Each box plot is a group of class "bp" with data-five="min q1 med q3 max"; the scale is read from
       the tick labels (class "tx").
r_sb22 Sydney Boys 2022 Q18: the lines l (x + 2y - 5 = 0) and CB (2x - y - 4 = 0) with A(-1, 3), B(1, -2),
       C on CB and T where they meet, drawn to scale on axes without a grid (the paper's figure is a sketch).
"""
from figs import Plane, Sketch, save, text, INK


def boxplot():
    W, H = 330, 112
    x0, x1, v0, v1 = 96, 316, 47, 103          # px for 47 and 103 marks
    X = lambda v: x0 + (v - v0) / (v1 - v0) * (x1 - x0)  # noqa: E731
    s = Sketch(W, H)
    for (name, five, y) in (("French:", (50, 60, 70, 80, 95), 22), ("Geography:", (55, 70, 80, 90, 100), 56)):
        mn, q1, md, q3, mx = five
        g = [f'<g class="bp" data-five="{mn} {q1} {md} {q3} {mx}">']
        g.append(f'<line x1="{X(mn):.1f}" y1="{y}" x2="{X(q1):.1f}" y2="{y}" stroke="{INK}" stroke-width="1.6"/>')
        g.append(f'<line x1="{X(q3):.1f}" y1="{y}" x2="{X(mx):.1f}" y2="{y}" stroke="{INK}" stroke-width="1.6"/>')
        g.append(f'<rect x="{X(q1):.1f}" y="{y - 10}" width="{X(q3) - X(q1):.1f}" height="20" fill="#e5e7eb" stroke="{INK}" stroke-width="1.6"/>')
        for v, h in ((mn, 10), (md, 10), (mx, 10)):
            g.append(f'<line x1="{X(v):.1f}" y1="{y - h}" x2="{X(v):.1f}" y2="{y + h}" stroke="{INK}" stroke-width="1.6"/>')
        g.append("</g>")
        s.items.append("".join(g))
        s.text(x0 - 8, y, name, "end", size=11.5, mask=False)
    ya = 90
    s.arrow(X(47), ya, X(103) + 8, ya, head=6)
    for v in range(50, 101, 5):
        s.line(X(v), ya - 3, X(v), ya + 3, width=1.0)
    for v in range(50, 101, 10):
        s.items.append(text(X(v), ya + 13, str(v), "middle", 11, cls="tx", mask=False))
    save("l3_bp", s)


def sb22():
    p = Plane(-3, 6, -5, 6, unit=18, grid=False, ticks=False, pad=(18, 18, 14, 14))
    p.line(1, 2, 5, "ink", eq="x+2y-5=0", width=1.6)
    p.line(2, -1, 4, "ink", eq="2x-y-4=0", width=1.6)
    for (x, y, nm) in ((-1, 3, "A"), (1, -2, "B"), (4.5, 5, "C"), (13 / 5, 6 / 5, "T")):
        p.dot(x, y, cls="pt", r=2.8)
        p.plabel(x, y, nm)
    p.llabel(1, 2, 5, "l", "ink", size=12, ts=(0.95, 0.9, 0.85))
    save("r_sb22", p)


if __name__ == "__main__":
    boxplot()
    sb22()
    print("lesson 3 figures written")
