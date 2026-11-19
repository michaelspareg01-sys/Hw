"""Figures for the auxiliary angle homework (answers booklet only).

Run: python3 workspace/build/auxangle/figs.py   (writes svg/*.svg)
"""
import os, sys
from math import sin, cos, pi, sqrt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, svg):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def wl(g, x, y, s, dx=0, dy=0, anchor="middle", size=11, color="ink"):
    """Label on a white background, drawn after everything else."""
    from plots import _txt, ACC
    px, py = g.X(x) + dx, g.Y(y) + dy
    frac = "/" in s
    n = len(s.replace("/", "")) if not frac else max(len(p) for p in s.split("/")) + (1 if s.startswith(("-", "−")) else 0)
    w = n * size * 0.6 + 6
    h = size * (2.3 if frac else 1.3)
    x0 = {"middle": px - w / 2, "start": px - 3, "end": px - w + 3}[anchor]
    g.late.append(f'<rect x="{x0:.1f}" y="{py - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#fff"/>')
    g.late.append(_txt(px, py, s, anchor, size=size, color=ACC[color]))
    return g


def done(g):
    g.items += g.late
    return g.svg()


# D1 (Ex 11B Q5 f): y = sqrt3 cos x - sin x = 2 cos(x + pi/6), with y = 1
g = Graph(0, 2 * pi, -2.3, 2.4, 470, 240, pad=(38, 44, 22, 40))
g.late = []
g.axes()
g.xticks([(t, "") for t in (pi / 6, pi / 3, 5 * pi / 6, 4 * pi / 3, 3 * pi / 2, 11 * pi / 6, 2 * pi)])
g.yticks([(2, ""), (sqrt(3), ""), (1, ""), (-2, "")])
g.hline(1, color="amber", dash="5 3", width=1.6)
g.curve(lambda x: 2 * cos(x + pi / 6), "blue")
for x in (pi / 6, 3 * pi / 2):
    g.vline(x, 0, 1, color="faint")
    g.dot(x, 1, "rose")
g.dot(5 * pi / 6, -2).dot(11 * pi / 6, 2)
wl(g, pi / 6, 0, "π/6", dy=-20)
wl(g, pi / 3, 0, "π/3", dx=10, dy=20)
wl(g, 5 * pi / 6, 0, "5π/6", dy=-20)
wl(g, 4 * pi / 3, 0, "4π/3", dx=-12, dy=20)
wl(g, 3 * pi / 2, 0, "3π/2", dy=-20)
wl(g, 11 * pi / 6, 0, "11π/6", dy=20)
wl(g, 2 * pi, 0, "2π", dx=6, dy=20)
wl(g, 0, sqrt(3), "√3", dx=-9, dy=2, anchor="end")
wl(g, 0, 1, "1", dx=-9, dy=2, anchor="end")
wl(g, 0, -2, "−2", dx=-9, anchor="end")
wl(g, 2 * pi, 1, "y = 1", dx=10, dy=-12, anchor="end", color="amber", size=10.5)
wl(g, 5 * pi / 6, -2, "(5π∕6, −2)", dx=12, dy=4, anchor="start", size=10.5)
wl(g, 11 * pi / 6, 2, "(11π∕6, 2)", dx=-12, dy=-2, anchor="end", size=10.5)
save("q5f", done(g))

# D2 (Ex 11B Q19 a ii, iii): y = sin x - cos x = sqrt2 sin(x - pi/4), with y = 1
g = Graph(0, 2 * pi, -1.7, 1.75, 470, 230, pad=(38, 44, 22, 40))
g.late = []
g.axes()
g.xticks([(t, "") for t in (pi / 4, pi / 2, 3 * pi / 4, pi, 5 * pi / 4, 3 * pi / 2, 7 * pi / 4, 2 * pi)])
g.yticks([(sqrt(2), ""), (1, ""), (-1, ""), (-sqrt(2), "")])
g.shade_x(pi / 2, pi, "rose")
g.hline(1, color="amber", dash="5 3", width=1.6)
g.curve(lambda x: sin(x) - cos(x), "blue")
g.vline(pi / 2, 0, 1).vline(pi, 0, 1)
g.dot(pi / 2, 1, "rose", hollow=True).dot(pi, 1, "rose", hollow=True)
g.dot(3 * pi / 4, sqrt(2)).dot(7 * pi / 4, -sqrt(2))
wl(g, pi / 4, 0, "π/4", dx=-6, dy=20)
wl(g, pi / 2, 0, "π/2", dy=-20)
wl(g, 3 * pi / 4, 0, "3π/4", dy=-20)
wl(g, pi, 0, "π", dy=-14)
wl(g, 5 * pi / 4, 0, "5π/4", dx=-4, dy=-20)
wl(g, 3 * pi / 2, 0, "3π/2", dy=20)
wl(g, 7 * pi / 4, 0, "7π/4", dy=20)
wl(g, 2 * pi, 0, "2π", dx=6, dy=-14)
wl(g, 0, sqrt(2), "√2", dx=-9, anchor="end")
wl(g, 0, 1, "1", dx=-9, anchor="end")
wl(g, 0, -1, "−1", dx=-9, anchor="end")
wl(g, 0, -sqrt(2), "−√2", dx=-9, dy=2, anchor="end")
wl(g, 2 * pi, 1, "y = 1", dx=10, dy=-12, anchor="end", color="amber", size=10.5)
save("q19a", done(g))

# D4 (Normanhurst Boys 2021 Q12(d)): y = 1/(4 cos(x + pi/6)) on [-pi/6, 11pi/6]
a, b = -pi / 6, 11 * pi / 6
g = Graph(a, b, -1.6, 1.6, 490, 260, pad=(44, 60, 22, 30))
g.late = []
g.axes()
g.xticks([(t, "") for t in (a, pi / 3, 5 * pi / 6, 4 * pi / 3, b)])
g.vline(pi / 3, color="amber", dash="5 3").vline(4 * pi / 3, color="amber", dash="5 3")
f = lambda x: 1 / (4 * cos(x + pi / 6))
g.curve(f, "blue", x0=a, x1=pi / 3 - 0.02)
g.curve(f, "blue", x0=pi / 3 + 0.02, x1=4 * pi / 3 - 0.02)
g.curve(f, "blue", x0=4 * pi / 3 + 0.02, x1=b)
g.dot(a, 0.25).dot(b, 0.25).dot(5 * pi / 6, -0.25).dot(0, 1 / (2 * sqrt(3)), r=2.6)
wl(g, a, 0, "−π∕6", dx=-4, dy=16)
wl(g, pi / 3, 0, "π/3", dx=14, dy=-22)
wl(g, 5 * pi / 6, 0, "5π/6", dy=-22)
wl(g, 4 * pi / 3, 0, "4π/3", dx=-18, dy=-22)
wl(g, b, 0, "11π/6", dx=-4, dy=22)
wl(g, a, 0.25, "(−π∕6, 1∕4)", dx=-30, dy=-18, anchor="start", size=10.5)
wl(g, b, 0.25, "(11π∕6, 1∕4)", dx=34, dy=-18, anchor="end", size=10.5)
wl(g, 5 * pi / 6, -0.25, "(5π∕6, −1∕4)", dy=18, size=10.5)
wl(g, 0, 1 / (2 * sqrt(3)), "√3/6", dx=8, dy=-14, anchor="start", size=10.5)
wl(g, pi / 3, 1.45, "x = π∕3", dx=-8, anchor="end", color="amber", size=10.5)
wl(g, 4 * pi / 3, 1.45, "x = 4π∕3", dx=8, anchor="start", color="amber", size=10.5)
save("nbhs21", done(g))
print("figures written")
