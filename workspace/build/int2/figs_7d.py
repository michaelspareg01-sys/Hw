"""Figures for Lesson 7D (kept apart from figs.py, which the scaffold task owns; same pattern as figs_6e.py).

Run: python3 workspace/build/int2/figs_7d.py   (writes svg/c7d_*.svg and svg/q7d_*.svg)
"""
import os
import sys
from math import sin, cos, pi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from relabel import relabel  # noqa: E402
from figs import RELOG, Graph, ACC, INK  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")


def save_raw(name, text):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(relabel(text, RELOG, name))      # Int2 assembly: clear labels of strokes


def save(name, g, width_mm=None):
    s = g.svg()
    if width_mm:
        s = s.replace("<svg ", f'<svg style="width:{width_mm}mm;max-width:100%" ', 1)
    save_raw(name, s)


def zero(x):
    return 0


def back(g, X, Y, w, h):
    """White backing rectangle (centre X, Y in pixels) so that a label stays clear of the curve."""
    g.items.append(f'<rect x="{X - w / 2:.1f}" y="{Y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#fff"/>')


def frac(g, x, y, num, den, dx=0, dy=0, size=10.5):
    """A small stacked fraction label such as pi over 2, centred at graph point (x, y) + (dx, dy)."""
    X, Y = g.X(x) + dx, g.Y(y) + dy
    w = max(len(num), len(den)) * size * 0.55 + 2
    back(g, X, Y + 1, w + 3, 2 * size + 3)
    g.items.append(f'<text x="{X:.1f}" y="{Y - 2:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}">{num}</text>')
    g.items.append(f'<line x1="{X - w / 2:.1f}" y1="{Y + 0.5:.1f}" x2="{X + w / 2:.1f}" y2="{Y + 0.5:.1f}" stroke="{INK}" stroke-width="0.8"/>')
    g.items.append(f'<text x="{X:.1f}" y="{Y + size + 0.5:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}">{den}</text>')
    return g


def tag(g, x, y, s, dx=0, dy=0, size=11, w=None):
    X, Y = g.X(x) + dx, g.Y(y) + dy
    back(g, X, Y, w or (len(s) * size * 0.6 + 4), size + 3)
    g.items.append(f'<text x="{X:.1f}" y="{Y + size * 0.36:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}">{s}</text>')


def arch(name, f, a, b, ticks, label, lab_x, xr=(-0.55, 2 * pi + 0.75)):
    """y = f(x) over about one period, with the region from x = a to x = b under the curve shaded."""
    g = Graph(xr[0], xr[1], -1.35, 1.45, w=270, h=150, pad=(18, 30, 18, 14))
    g.fill(f, zero, a, b, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=xr[0] + 0.05 if f is sin else 0.0, x1=xr[1] - 0.05)
    if ticks[0][2]:
        g.hline(1, x0=0, x1=ticks[0][0])
    tag(g, 0, 1, "1", dx=-9)
    for xv, txt, dashed, ddx in ticks:
        if dashed:
            g.vline(xv, 0, 1)
        if "/" in txt:
            num, den = txt.split("/")
            frac(g, xv, 0, num, den, dx=ddx, dy=15)
        else:
            tag(g, xv, 0, txt, dx=ddx, dy=12)
    tag(g, lab_x, 0.72, label, size=11)
    save(name, g, 62)


def lesson():
    # each tick: (x, label, dashed line up to the curve, label shift so that it stays clear of the curve)
    sin_ticks = [(pi / 2, "π/2", True, 0), (pi, "π", False, -9), (2 * pi, "2π", False, 10)]
    # Worked example 16: the first arch of y = sin x, shaded from 0 to pi
    arch("c7d_ex16", sin, 0, pi, sin_ticks, "y = sin x", 3 * pi / 2)
    # Tutor demo: y = cos x, shaded from 0 to pi/2
    arch("c7d_demo", cos, 0, pi / 2, [(pi / 2, "π/2", False, -10), (pi, "π", False, 0), (3 * pi / 2, "3π/2", False, 13),
                                      (2 * pi, "2π", False, 0)], "y = cos x", pi)
    # Your turn: y = sin x, shaded from 0 to pi/2
    arch("c7d_turn", sin, 0, pi / 2, sin_ticks, "y = sin x", 3 * pi / 2)


def q4_grid():
    """Exercise 7D Q4: y = sin x on graph paper, 10 small divisions to 1 unit (100 little squares = 1 square unit)."""
    x0, x1, y0, y1 = -0.3, 6.6, -1.3, 1.3
    u = 64  # pixels per unit
    pl, pr, pt, pb = 14, 30, 18, 10
    W, H = pl + pr + (x1 - x0) * u, pt + pb + (y1 - y0) * u

    def X(x):
        return pl + (x - x0) * u

    def Y(y):
        return pt + (y1 - y) * u

    it = []
    for i in range(int(round((x1 - x0) * 10)) + 1):
        xv = x0 + i / 10
        k = int(round(xv * 10))
        w_, col = (1.1, INK) if k % 5 == 0 else (0.35, "#aab4bf")
        it.append(f'<line x1="{X(xv):.1f}" y1="{Y(y0):.1f}" x2="{X(xv):.1f}" y2="{Y(y1):.1f}" stroke="{col}" stroke-width="{w_}"/>')
    for j in range(int(round((y1 - y0) * 10)) + 1):
        yv = y0 + j / 10
        k = int(round(yv * 10))
        w_, col = (1.1, INK) if k % 5 == 0 else (0.35, "#aab4bf")
        it.append(f'<line x1="{X(x0):.1f}" y1="{Y(yv):.1f}" x2="{X(x1):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="{w_}"/>')
    # axes
    it.append(f'<line x1="{X(x0):.1f}" y1="{Y(0):.1f}" x2="{X(x1) + 14:.1f}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.5"/>')
    it.append(f'<path d="M{X(x1) + 14:.1f},{Y(0):.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    it.append(f'<line x1="{X(0):.1f}" y1="{Y(y0):.1f}" x2="{X(0):.1f}" y2="{Y(y1) - 12:.1f}" stroke="{INK}" stroke-width="1.5"/>')
    it.append(f'<path d="M{X(0):.1f},{Y(y1) - 12:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    it.append(f'<text x="{X(x1) + 20.4:.1f}" y="{Y(0) + 4:.1f}" font-size="12" font-style="italic" fill="{INK}">x</text>')
    it.append(f'<text x="{X(0) - 6:.1f}" y="{Y(y1) - 8:.1f}" text-anchor="end" font-size="12" font-style="italic" fill="{INK}">y</text>')

    def tag(xp, yp, s, w=14):
        it.append(f'<rect x="{xp - w / 2:.1f}" y="{yp - 9:.1f}" width="{w}" height="13" fill="#fff"/>')
        it.append(f'<text x="{xp:.1f}" y="{yp + 1.5:.1f}" text-anchor="middle" font-size="11" fill="{INK}">{s}</text>')

    def ftag(xp, yp, num, den):
        it.append(f'<rect x="{xp - 9:.1f}" y="{yp - 10:.1f}" width="18" height="24" fill="#fff"/>')
        it.append(f'<text x="{xp:.1f}" y="{yp - 0.5:.1f}" text-anchor="middle" font-size="10.5" fill="{INK}">{num}</text>')
        it.append(f'<line x1="{xp - 7:.1f}" y1="{yp + 1.5:.1f}" x2="{xp + 7:.1f}" y2="{yp + 1.5:.1f}" stroke="{INK}" stroke-width="0.8"/>')
        it.append(f'<text x="{xp:.1f}" y="{yp + 12:.1f}" text-anchor="middle" font-size="10.5" fill="{INK}">{den}</text>')

    for v in (1, 2, 4, 5):
        tag(X(v) + 7, Y(0) + 12, str(v), 10)
    tag(X(6) + 7, Y(0) - 10, "6", 10)
    tag(X(3) - 7, Y(0) + 12, "3", 10)
    tag(X(pi) + 8, Y(0) - 10, "π", 10)
    tag(X(2 * pi) + 9, Y(0) + 12, "2π", 16)
    ftag(X(pi / 2), Y(0) + 11, "π", "2")
    ftag(X(3 * pi / 2), Y(0) + 11, "3π", "2")
    tag(X(0) - 9, Y(1) + 1, "1", 10)
    tag(X(0) - 11, Y(-1) + 1, "−1", 16)
    # dashed line from the maximum down to x = pi/2
    it.append(f'<line x1="{X(pi / 2):.1f}" y1="{Y(1):.1f}" x2="{X(pi / 2):.1f}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="0.9" stroke-dasharray="3 2"/>')
    # the curve y = sin x
    xa, xb = -0.22, 6.5
    pts = " ".join(f"{X(xa + (xb - xa) * i / 500):.1f},{Y(sin(xa + (xb - xa) * i / 500)):.1f}" for i in range(501))
    it.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" style="width:150mm;max-width:100%" viewBox="0 0 {W:.0f} {H:.0f}" '
           f'width="{W:.0f}" height="{H:.0f}" font-family="Inter, Arial, sans-serif">' + "".join(it) + "</svg>")
    save_raw("q7d_q4", svg)


if __name__ == "__main__":
    lesson()
    q4_grid()
