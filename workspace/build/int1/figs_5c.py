"""Figures for Lesson 5C (kept apart from figs.py, which the scaffold task owns; same pattern as figs_5a.py).

Run: python3 workspace/build/int1/figs_5c.py   (writes svg/c5c_*.svg, svg/q5c_*.svg and svg/p5c_*.svg)
"""
import os
import sys
from math import acos, pi, sin, cos

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save, ACC, INK  # noqa: E402


def zero(x):
    return 0.0


def seg(g, x0, y0, x1, y1, color="ink", width=1.3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{d}/>')


def arc(g, cx, cy, r, t0, t1, n=120, width=1.3):
    """Circular arc centre (cx, cy), radius r, from angle t0 to t1 (radians), in graph units (equal scales)."""
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        pts.append(f"{g.X(cx + r * cos(t)):.1f},{g.Y(cy + r * sin(t)):.1f}")
    g.items.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="{width}"/>')


# ---------------------------------------------------------------- lesson figures
def lesson():
    # Box 5: signed areas A (above), B (below), C (above), with a < h < k < b
    def f(x):
        return 0.18 * (x - 2) * (x - 4) * (x + 0.3)

    g = Graph(-0.8, 5.6, -1.0, 3.2, w=320, h=190, pad=(14, 32, 16, 16))
    g.fill(f, zero, 0.6, 2, opacity=0.25)
    g.fill(f, zero, 2, 4, color="rose", opacity=0.22)
    g.fill(f, zero, 4, 5, opacity=0.25)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.5, x0=-0.55, x1=5.35)
    g.vline(0.6, 0, f(0.6), color="ink", dash="", width=1.0).vline(5, 0, f(5), color="ink", dash="", width=1.0)
    for v, lab in ((0.6, "a"), (2, "h"), (4, "k"), (5, "b")):
        g.label(v, 0, lab, dx=(-6 if lab in "hk" else 0), dy=(-9 if lab == "k" else 13), size=11.5, italic=True)
    g.label(1.2, 0.3, "A", size=12, italic=True)
    g.label(3.0, -0.3, "B", size=12, italic=True)
    g.label(4.7, 0.6, "C", size=12, italic=True)
    save("c5c_signed", g)

    # Example 7: y = x - 4, triangles OAB (below) and BMC (above)
    g = Graph(-1.2, 7.2, -4.8, 2.9, w=215, h=190, pad=(14, 32, 16, 14))
    g.fill(lambda x: x - 4, zero, 0, 4, opacity=0.25)
    g.fill(lambda x: x - 4, zero, 4, 6, opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: x - 4, color="ink", width=1.5, x0=-0.3, x1=6.8)
    g.vline(6, 0, 2, color="ink", dash="", width=1.1)
    g.hline(2, color="faint", x0=0, x1=6)
    g.yticks([(2, "2"), (-4, "-4")])
    g.label(4, 0, "4", dx=2, dy=13, size=11).label(6, 0, "6", dx=-6, dy=13, size=11)
    g.label(0, 0, "O", dx=-8, dy=11, size=11, italic=True)
    g.label(0, -4, "A", dx=9, dy=6, size=11, italic=True)
    g.label(4, 0, "B", dx=-4, dy=-9, size=11, italic=True)
    g.label(6, 2, "C", dx=8, dy=7, size=11, italic=True)
    g.label(6, 0, "M", dx=8, dy=-8, size=11, italic=True)
    save("c5c_e7", g)

    # Example 8a: odd function y = x^3 - 4x on [-2, 2]
    def odd(x):
        return x ** 3 - 4 * x

    g = Graph(-2.6, 2.6, -4.2, 4.2, w=200, h=160, pad=(14, 32, 16, 14))
    g.fill(odd, zero, -2, 2, opacity=0.25)
    g.axes("x", "y")
    g.curve(odd, color="ink", width=1.5, x0=-2.45, x1=2.45)
    g.label(-2, 0, "-2", dx=-10, dy=-10, size=11).label(2, 0, "2", dx=9, dy=12, size=11)
    save("c5c_odd", g)

    # Example 8b: even function y = x^2 + 1 on [-2, 2]
    def ev(x):
        return x * x + 1

    g = Graph(-2.6, 2.6, -0.5, 6.4, w=200, h=165, pad=(14, 32, 16, 18))
    g.fill(ev, zero, -2, 2, opacity=0.25)
    g.axes("x", "y")
    g.curve(ev, color="ink", width=1.5, x0=-2.35, x1=2.35)
    g.vline(-2, 0, 5, color="ink", dash="", width=1.0).vline(2, 0, 5, color="ink", dash="", width=1.0)
    g.hline(5, color="faint", x0=-2, x1=2)
    g.xticks([(-2, "-2"), (2, "2")])
    g.label(0, 5, "5", dx=-5, dy=-8, anchor="end", size=11)
    g.label(0, 1, "1", dx=-5, dy=-6, anchor="end", size=11)
    save("c5c_even", g)

    # Box 7: dissection of the interval at c
    def inc(x):
        return 0.8 + 0.08 * (x + 0.5) ** 2

    g = Graph(-0.6, 5.4, -0.3, 3.4, w=190, h=120, pad=(14, 32, 16, 18))
    g.fill(inc, zero, 1.0, 2.2, color="amber", opacity=0.35)
    g.fill(inc, zero, 2.2, 4.6, opacity=0.25)
    g.axes("x", "y")
    g.curve(inc, color="ink", width=1.5, x0=-0.5, x1=5.1)
    for v in (1.0, 2.2, 4.6):
        g.vline(v, 0, inc(v), color="ink", dash="", width=1.0)
    for v, lab in ((1.0, "a"), (2.2, "c"), (4.6, "b")):
        g.label(v, 0, lab, dy=13, size=11.5, italic=True)
    save("c5c_dissect", g)

    # Box 8: an interval of zero width at x = a
    g = Graph(-0.6, 5.4, -0.3, 3.4, w=190, h=120, pad=(14, 32, 16, 18))
    g.axes("x", "y")
    g.curve(inc, color="ink", width=1.5, x0=-0.5, x1=5.1)
    g.vline(2.6, 0, inc(2.6), color="faint", dash="4 3", width=1.1)
    g.label(2.6, 0, "a", dy=13, size=11.5, italic=True)
    save("c5c_zero", g)

    # Example 9: y = x - 1 from 2 to 4
    g = Graph(-1.4, 5.4, -1.7, 4.4, w=200, h=175, pad=(14, 32, 16, 16))
    g.fill(lambda x: x - 1, zero, 2, 4, opacity=0.28)
    g.axes("x", "y")
    g.curve(lambda x: x - 1, color="ink", width=1.5, x0=-0.6, x1=5.1)
    g.vline(2, 0, 1, color="ink", dash="", width=1.0).vline(4, 0, 3, color="ink", dash="", width=1.0)
    g.hline(1, color="faint", x0=0, x1=2).hline(3, color="faint", x0=0, x1=4)
    g.xticks([(2, "2"), (4, "4")]).yticks([(1, "1"), (3, "3"), (-1, "-1")])
    save("c5c_e9", g)

    # Example 12: y = 4 - x^2 inside the square of side 4
    g = Graph(-2.9, 2.9, -0.6, 5.0, w=205, h=180, pad=(14, 32, 16, 18))
    g.fill(lambda x: 4 - x * x, zero, -2, 2, opacity=0.28)
    g.axes("x", "y")
    g.curve(lambda x: 4 - x * x, color="ink", width=1.5, x0=-2.25, x1=2.25)
    g.hline(4, color="ink", dash="", x0=-2.8, x1=2.8, width=1.1)
    g.vline(-2, 0, 4, color="faint").vline(2, 0, 4, color="faint")
    g.label(-2, 0, "-2", dx=9, dy=13, size=11).label(2, 0, "2", dx=-7, dy=13, size=11)
    g.label(0, 4, "4", dx=-5, dy=-8, anchor="end", size=11)
    g.label(1.6, 4, "y = 4", dy=-9, size=10.5, italic=True)
    save("c5c_e12", g)


# ---------------------------------------------------------------- exercise figures
def exercise():
    # Q4: the line y = x - 1
    g = Graph(-2.6, 3.0, -2.6, 2.6, w=185, h=165, pad=(14, 32, 16, 14))
    g.axes("x", "y")
    g.curve(lambda x: x - 1, color="ink", width=1.4, x0=-1.5, x1=2.95)
    g.xticks([(-2, "-2"), (-1, "-1"), (1, "1"), (2, "2")])
    save("q5c_4", g)

    # Q5: the parabola y = 1 - x^2
    g = Graph(-2.1, 3.6, -3.4, 1.6, w=200, h=170, pad=(14, 32, 16, 14))
    g.axes("x", "y")
    g.curve(lambda x: 1 - x * x, color="ink", width=1.4, x0=-2.05, x1=2.05)
    g.xticks([(0.5, ""), (3, "3")])
    g.label(-1, 0, "-1", dx=-12, dy=-9, size=11).label(1, 0, "1", dx=10, dy=-9, size=11)
    g.label(0.5, 0, "1/2", dy=18, size=10.5)
    g.label(0, 1, "1", dx=-5, dy=-7, anchor="end", size=11)
    save("q5c_5", g)

    # Q12a, Q12b: lines and quadrants (equal scales)
    for name in ("q5c_12a", "q5c_12b"):
        g = Graph(-0.4, 4.6, -1.35, 1.35, w=250, h=135, pad=(14, 32, 14, 12))
        g.axes("x", "y")
        if name == "q5c_12a":
            arc(g, 0, 0, 1, pi / 2, 0)             # quadrant from (0, 1) to (1, 0), centre O
            seg(g, 1, 0, 2, -1)
            seg(g, 2, -1, 3, 1)
            arc(g, 3, 0, 1, pi / 2, 0)             # quadrant from (3, 1) to (4, 0), centre (3, 0)
            seg(g, 0, 1, 3, 1, color="faint", width=1.0, dash="4 3")
            seg(g, 0, -1, 2, -1, color="faint", width=1.0, dash="4 3")
            seg(g, 2, -1, 2, 0, color="faint", width=1.0, dash="4 3")
            seg(g, 3, 0, 3, 1, color="faint", width=1.0, dash="4 3")
            g.label(1, 0, "1", dy=13, size=11).label(2, 0, "2", dy=-9, size=11)
            g.label(3, 0, "3", dy=13, size=11).label(4, 0, "4", dy=13, size=11)
        else:
            arc(g, 0, 1, 1, -pi / 2, 0)            # quadrant from (0, 0) to (1, 1), centre (0, 1)
            seg(g, 1, 1, 3, -1)
            arc(g, 3, 0, 1, -pi / 2, 0)            # quadrant from (3, -1) to (4, 0), centre (3, 0)
            seg(g, 0, 1, 1, 1, color="faint", width=1.0, dash="4 3")
            seg(g, 1, 0, 1, 1, color="faint", width=1.0, dash="4 3")
            seg(g, 0, -1, 3, -1, color="faint", width=1.0, dash="4 3")
            seg(g, 3, 0, 3, -1, color="faint", width=1.0, dash="4 3")
            g.label(1, 0, "1", dy=13, size=11).label(2, 0, "2", dy=13, size=11)
            g.label(3, 0, "3", dy=-9, size=11).label(4, 0, "4", dy=-9, size=11)
        for v in (0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4):
            g.items.append(f'<line x1="{g.X(v)}" y1="{g.Y(0) - 3}" x2="{g.X(v)}" y2="{g.Y(0) + 3}" stroke="{INK}" stroke-width="1.2"/>')
        g.yticks([(1, "1"), (0.5, ""), (-0.5, ""), (-1, "-1")])
        save(name, g)


# ---------------------------------------------------------------- past-paper figures
def stf(x):
    """Sydney Tech 2021 Q6: a function drawn to scale on [0, 8] (zeros at 2, 6, 8)."""
    if x <= 1:
        return 3.1 - 0.9 * (x - 1) ** 2
    if x <= 2:                                   # cubic Hermite 3.1 -> 0, slopes 0 -> -pi/4
        t = x - 1
        m1 = -pi / 4
        return 3.1 * (2 * t ** 3 - 3 * t ** 2 + 1) + m1 * (t ** 3 - t ** 2)
    if x <= 6:
        return -sin(pi * (x - 2) / 4)
    return 0.5 * sin(pi * (x - 6) / 2)


def pastpapers():
    g = Graph(-0.3, 8.6, -1.4, 3.5, w=320, h=180, pad=(18, 30, 16, 12))
    g.axes("x", "y")
    g.curve(stf, color="ink", width=1.5, x0=0, x1=8, n=800)
    g.xticks([(v, str(v)) for v in range(1, 9)])
    g.label(0, 0, "O", dx=-8, dy=11, size=11, italic=True)
    g.label(1.6, 2.3, "y = f(x)", anchor="start", size=10.5, italic=True)
    save("p5c_st", g)

    # Epping 2024 Q12(c)(i): the graph of f(x) = 2 cos^-1(x - 1) (supplied for part (ii))
    def ep(x):
        return 2 * acos(max(-1.0, min(1.0, x - 1)))

    g = Graph(-0.5, 2.6, -0.5, 6.9, w=160, h=170, pad=(22, 32, 16, 14))
    g.axes("x", "y")
    g.curve(ep, color="ink", width=1.5, x0=0, x1=2, n=800)
    g.dot(0, 2 * pi, r=2.6).dot(2, 0, r=2.6).dot(1, pi, r=2.6)
    g.hline(pi, color="faint", x0=0, x1=1).vline(1, 0, pi, color="faint")
    g.yticks([(pi, "π"), (2 * pi, "2π")])
    g.xticks([(1, "1"), (2, "2")])
    g.label(1.15, 4.6, "y = f(x)", anchor="start", size=10.5, italic=True)
    save("p5c_ep", g)

    # solutions: y = cos^-1 x on [-1, 1] inside the rectangle 2 by pi
    g = Graph(-1.6, 1.7, -0.5, 3.6, w=170, h=150, pad=(22, 32, 16, 14))
    g.fill(lambda x: acos(max(-1.0, min(1.0, x))), zero, -1, 1, opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: acos(max(-1.0, min(1.0, x))), color="ink", width=1.5, x0=-1, x1=1, n=800)
    g.hline(pi, color="faint", x0=-1, x1=1).vline(-1, 0, pi, color="faint")
    g.hline(pi / 2, color="faint", x0=-1, x1=0)
    g.dot(0, pi / 2, r=2.6)
    g.yticks([(pi, ""), (pi / 2, "")])
    g.label(-1, pi, "π", dx=-8, anchor="end", size=11)       # beside the ends of the dashed guides,
    g.label(-1, pi / 2, "π/2", dx=-8, anchor="end", size=11)  # clear of the curve
    g.xticks([(-1, "-1"), (1, "1")])
    g.label(-0.5, 0.6, "S", size=12, italic=True).label(0.45, 2.5, "T", size=12, italic=True)
    save("p5c_abs", g)

    # solutions: y = 2 cos^-1(x - 1) - pi, two congruent regions
    def h(x):
        return 2 * acos(max(-1.0, min(1.0, x - 1))) - pi

    g = Graph(-0.5, 2.6, -3.6, 3.6, w=160, h=170, pad=(22, 32, 16, 14))
    g.fill(h, zero, 0, 1, opacity=0.25)
    g.fill(h, zero, 1, 2, color="rose", opacity=0.22)
    g.axes("x", "y")
    g.curve(h, color="ink", width=1.5, x0=0, x1=2, n=800)
    g.dot(0, pi, r=2.6).dot(2, -pi, r=2.6).dot(1, 0, r=2.6)
    g.yticks([(pi, "π"), (-pi, "-π")])
    g.xticks([(2, "")])
    g.label(2, 0, "2", dx=4, dy=-10, size=11)
    g.label(1, 0, "1", dx=-7, dy=12, size=11)
    g.hline(-pi, color="faint", x0=0, x1=2)
    g.label(0.4, 1.0, "P", size=12, italic=True).label(1.5, -1.3, "Q", size=12, italic=True)
    save("p5c_eps", g)


if __name__ == "__main__":
    lesson()
    exercise()
    pastpapers()
