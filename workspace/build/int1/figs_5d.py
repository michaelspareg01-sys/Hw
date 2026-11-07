"""Figures for Lesson 5D (kept apart from figs.py, as figs_5a.py).

Run: python3 workspace/build/int1/figs_5d.py   (writes svg/c5d_*.svg, svg/q5d_*.svg and svg/a5d_*.svg)
"""
import os
import sys
from math import sqrt, exp, log, atan, cos, sin, pi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save, OUT, ACC, INK, FAINT, _txt  # noqa: E402

GREY = "#9aa3ad"


def zero(t):
    return 0.0


def seg(g, x0, y0, x1, y1, color="ink", width=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{d}/>')


def rect(g, x0, x1, y0, y1, fill, op=0.45):
    X0, X1, Y0, Y1 = g.X(x0), g.X(x1), g.Y(y0), g.Y(y1)
    g.items.append(f'<rect x="{min(X0, X1):.1f}" y="{min(Y0, Y1):.1f}" width="{abs(X1 - X0):.1f}" '
                   f'height="{abs(Y1 - Y0):.1f}" fill="{fill}" fill-opacity="{op}" stroke="{INK}" stroke-width="1"/>')


def pointer(g, x0, y0, x1, y1, bend=0.0):
    """Thin curved arrow from (x0, y0) to (x1, y1), in graph units, for area labels."""
    X0, Y0, X1, Y1 = g.X(x0), g.Y(y0), g.X(x1), g.Y(y1)
    cx, cy = (X0 + X1) / 2 + bend, min(Y0, Y1) - 6
    g.items.append(f'<path d="M{X0:.1f},{Y0:.1f} Q{cx:.1f},{cy:.1f} {X1:.1f},{Y1:.1f}" fill="none" '
                   f'stroke="{INK}" stroke-width="0.9"/>')
    g.items.append(f'<circle cx="{X1:.1f}" cy="{Y1:.1f}" r="1.8" fill="{INK}"/>')


def size(name, mm):
    """Fix the printed width of an answer figure (the answers CSS otherwise stretches every figure to 88 mm)."""
    p = os.path.join(OUT, name + ".svg")
    with open(p, encoding="utf-8") as fh:
        s = fh.read()
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(s.replace("<svg ", f'<svg style="width:{mm}mm;height:auto" ', 1))


def combine(name, graphs, gap=10, mm=None):
    """Place several Graph objects side by side in one svg."""
    w = sum(gr.w for gr in graphs) + gap * (len(graphs) - 1)
    h = max(gr.h for gr in graphs)
    out, xo = [], 0
    for gr in graphs:
        out.append(f'<svg x="{xo}" y="0" width="{gr.w}" height="{gr.h}" viewBox="0 0 {gr.w} {gr.h}">'
                   + "".join(gr.items) + '</svg>')
        xo += gr.w + gap
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        st = f' style="width:{mm}mm;height:auto"' if mm else ''
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg"{st} viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                 f'font-family="Inter, Arial, sans-serif">' + "".join(out) + '</svg>')


def step_line(c, m):
    """f(t) = c for t < 0 and c - m t for t >= 0 (Example 13 shape)."""
    return lambda t: c if t < 0 else c - m * t


def step_area(c, m):
    """A(x) = integral from 0 to x of step_line(c, m)."""
    return lambda x: c * x if x < 0 else c * x - m * x * x / 2


# ---------------------------------------------------------------- lesson figures
def lesson():
    # the definite integral as a function of its upper limit, and A(x)
    a0 = 0.7

    def f(t):
        return 0.9 + 0.45 * (t - a0) ** 2

    g = Graph(-1.4, 3.3, -0.3, 4.0, w=170, h=128, pad=(12, 30, 18, 18))
    g.fill(f, zero, a0, 2.6, opacity=0.25)
    g.axes("t", "y")
    g.curve(f, color="ink", width=1.5, x0=-1.3, x1=3.2)
    g.vline(a0, 0, f(a0), color="ink", dash="", width=1.1).vline(2.6, 0, f(2.6), color="ink", dash="", width=1.1)
    g.label(a0, 0, "a", dy=13, italic=True).label(2.6, 0, "x", dy=13, italic=True)
    save("c5d_fa", g)

    def A(x):
        return 0.9 * (x - a0) + 0.15 * (x - a0) ** 3

    g = Graph(-1.4, 3.3, -2.6, 3.0, w=170, h=128, pad=(12, 30, 18, 12))
    g.axes("x", "A(x)")
    g.curve(A, color="blue", width=2, x0=-1.3, x1=3.0)
    g.dot(a0, 0, r=2.4).label(a0, 0, "a", dy=13, italic=True)
    save("c5d_Aa", g)

    # parabola with axis t = b, zeros a and c, and d chosen so that the area from c to d is also B
    b0 = 2.2
    aa, cc, dd = b0 - 1, b0 + 1, b0 + sqrt(3)

    def p(t):
        return (t - b0) ** 2 - 1

    def Ap(x):
        u = x - b0
        return u ** 3 / 3 - u - 2 / 3

    g = Graph(-0.5, 4.5, -1.4, 2.6, w=200, h=150, pad=(12, 30, 18, 16))
    g.fill(zero, p, aa, cc, opacity=0.25)
    g.fill(p, zero, cc, dd, opacity=0.25)
    g.axes("t", "f(t)")
    g.curve(p, color="ink", width=1.5, x0=-0.4, x1=4.3)
    g.vline(dd, 0, p(dd), color="ink", dash="", width=1.1)
    for v in (aa, b0, cc, dd):
        g.vline(v, -1.4, 0, color="faint", width=1)
    g.label(aa, 0, "a", dx=-10, dy=-9, italic=True).label(b0, 0, "b", dy=-9, italic=True)
    g.label(cc, 0, "c", dx=-7, dy=-9, italic=True).label(dd, 0, "d", dx=7, dy=-9, italic=True)
    g.label(b0 - 0.5, 1.85, "B", italic=True, size=12).label(b0 + 1.05, 1.85, "B", italic=True, size=12)
    pointer(g, b0 - 0.55, 1.6, b0 - 0.45, -0.45, bend=-14)
    pointer(g, b0 - 0.45, 1.6, b0 + 0.45, -0.45, bend=14)
    pointer(g, b0 + 1.1, 1.6, cc + 0.5, 0.25, bend=10)
    save("c5d_fp", g)

    g = Graph(-0.5, 4.5, -2.0, 1.2, w=200, h=156, pad=(12, 30, 24, 18))
    g.axes("x", "A(x)")
    for v in (aa, b0, cc, dd):
        g.vline(v, -2.0, 1.2, color="faint", width=1)
    g.hline(-2 / 3, x0=0, x1=dd).hline(-4 / 3, x0=0, x1=cc)
    g.curve(Ap, color="blue", width=2, x0=-0.4, x1=4.4)
    g.label(aa, 0, "a", dy=12, italic=True).label(b0, 0, "b", dy=-9, italic=True)
    g.label(cc, 0, "c", dy=12, italic=True).label(dd, 0, "d", dy=-9, italic=True)
    g.label(0, -2 / 3, "-B", dx=-5, anchor="end", italic=True).label(0, -4 / 3, "-2B", dx=-5, anchor="end", italic=True)
    save("c5d_Ap", g)

    # Example 13: the graph of f and the graph of A
    g = Graph(-3.4, 3.4, -3.2, 2.6, w=170, h=150, pad=(12, 30, 18, 12))
    g.axes("x", "y")
    g.curve(step_line(2, 2), color="ink", width=1.5, x0=-3.3, x1=2.6)
    g.xticks([(1, "1"), (2, "2"), (3, "3")]).yticks([(-2, "-2")])
    g.label(0, 2, "2", dx=5, dy=-7, anchor="start")
    save("c5d_e13f", g)

    g = Graph(-1.8, 3.4, -4.6, 1.6, w=170, h=150, pad=(12, 30, 18, 12))
    g.axes("x", "y")
    g.vline(-1, -2, 0).hline(-2, x0=-1, x1=0).vline(3, -3, 0).hline(-3, x0=0, x1=3)
    g.curve(step_area(2, 2), color="blue", width=2, x0=-1.7, x1=3.25)
    g.xticks([(1, "1"), (2, "2")]).yticks([(1, "1"), (-2, "-2"), (-3, "-3")])
    g.label(-1, 0, "-1", dy=-10, size=11).label(3, 0, "3", dy=-10, size=11)
    save("c5d_e13A", g)

    # Tutor demo: f(t) = 4 for t < 0, 4 - 2t for t >= 0;  Your turn: f(t) = 1 for t < 0, 1 - t for t >= 0
    g = Graph(-2.4, 4.4, -4.6, 4.8, w=170, h=150, pad=(12, 30, 18, 12))
    g.axes("t", "y")
    g.curve(step_line(4, 2), color="ink", width=1.5, x0=-2.3, x1=4.3)
    g.xticks([(-2, "-2"), (-1, "-1"), (1, "1"), (2, "2"), (3, "3"), (4, "4")]).yticks([(-4, "-4")])
    g.label(0, 4, "4", dx=5, dy=-7, anchor="start")
    save("c5d_d1f", g)

    g = Graph(-3.4, 3.4, -2.6, 1.8, w=170, h=150, pad=(12, 30, 18, 12))
    g.axes("t", "y")
    g.curve(step_line(1, 1), color="ink", width=1.5, x0=-3.3, x1=3.3)
    g.xticks([(-3, "-3"), (-2, "-2"), (-1, "-1"), (1, "1"), (2, "2"), (3, "3")]).yticks([(-2, "-2")])
    g.label(0, 1, "1", dx=5, dy=-7, anchor="start")
    save("c5d_y1f", g)

    # proof of the differential form: lower rectangle (blue) and the extra part of the upper rectangle (amber)
    def q(t):
        return 0.55 + 0.05 * (t + 1.2) ** 2

    xx, hh = 4.0, 1.0
    g = Graph(-0.6, 6.4, -0.3, 2.9, w=300, h=140, pad=(12, 30, 18, 18))
    rect(g, xx, xx + hh, 0, q(xx), ACC["blue"], 0.22)
    rect(g, xx, xx + hh, q(xx), q(xx + hh), ACC["amber"], 0.4)
    g.axes("t", "y")
    g.curve(q, color="ink", width=1.5, x0=-0.5, x1=5.9)
    g.vline(1.0, 0, q(1.0), color="ink", dash="", width=1)
    g.label(1.0, 0, "a", dy=13, italic=True).label(xx, 0, "x", dy=13, italic=True)
    g.label(xx + hh, 0, "x + h", dy=13, italic=True)
    g.label(xx - 0.12, q(xx) / 2, "f(x)", anchor="end", size=10.5, italic=True)
    g.label(xx + hh + 0.12, q(xx + hh) - 0.25, "f(x + h)", anchor="start", size=10.5, italic=True)
    save("c5d_ftc", g)

    # the reciprocal function
    g = Graph(-3, 3, -3, 3, w=130, h=120, pad=(12, 26, 16, 12))
    g.axes("x", "y")
    g.curve(lambda t: 1 / t, color="ink", width=1.5, x0=0.33, x1=2.95)
    g.curve(lambda t: 1 / t, color="ink", width=1.5, x0=-2.95, x1=-0.33)
    save("c5d_recip", g)


# ---------------------------------------------------------------- exercise figures
def exercise():
    # Q1: y = 3t for 0 <= t <= 3
    g = Graph(-0.5, 3.4, -1.0, 10.2, w=130, h=120, pad=(14, 24, 14, 14))
    g.fill(lambda t: 3 * t, zero, 0, 2.1, opacity=0.25)
    g.axes("t", "y")
    g.curve(lambda t: 3 * t, color="ink", width=1.5, x0=-0.3, x1=3.25)
    g.vline(2.1, 0, 6.3, color="ink", dash="", width=1)
    g.vline(3, 0, 9).hline(9, x0=0, x1=3)
    g.label(2.1, 0, "x", dy=13, italic=True).xticks([(3, "3")]).yticks([(9, "9")])
    save("q5d_1", g)

    # Q2 a-d
    def q2(name, f, ymax, yt, xmax=4.6, extra=None):
        g = Graph(-0.6, xmax, -0.8, ymax, w=150, h=118, pad=(14, 26, 14, 14))
        g.fill(f, zero, 0, 2.8, opacity=0.25)
        g.axes("t", "y")
        g.curve(f, color="ink", width=1.5, x0=-0.5 if name != "q5d_2d" else -0.3, x1=xmax - 0.1)
        g.vline(2.8, 0, f(2.8), color="ink", dash="", width=1)
        g.vline(4, 0, f(4))
        if name != "q5d_2a":
            g.hline(f(4), x0=0, x1=4)
        g.label(2.8, 0, "x", dy=13, italic=True).xticks([(4, "4")] + (extra or []))
        g.yticks(yt)
        save(name, g)

    q2("q5d_2a", lambda t: 3, 4.2, [(3, "3")])
    q2("q5d_2b", lambda t: 2 * t, 9.5, [(8, "8")])
    q2("q5d_2c", lambda t: 2 + t, 7.2, [(2, "2"), (6, "6")])
    q2("q5d_2d", lambda t: 5 - t, 6.2, [(1, "1"), (5, "5")], xmax=5.6, extra=[(5, "5")])

    # Q3 a and b
    g = Graph(-0.6, 4.6, -0.5, 3.4, w=170, h=110, pad=(14, 26, 14, 14))
    g.axes("t", "y")
    g.curve(lambda t: 1 + 0.25 * (t - 2) ** 2, color="ink", width=1.5, x0=0, x1=4.5)
    g.dot(0, 2, r=2.6).xticks([(2, "2")])
    save("q5d_3a", g)
    g = Graph(-0.6, 5.6, -0.3, 1.5, w=170, h=110, pad=(14, 26, 14, 14))
    g.axes("x", "y")
    g.curve(lambda t: 1 / (1 + (t - 2) ** 2), color="ink", width=1.5, x0=0, x1=5.5)
    g.dot(0, 0.2, r=2.6).xticks([(2, "2")])
    save("q5d_3b", g)

    # Q8: y = cos x on [0, 2 pi], region P shaded
    g = Graph(-0.4, 6.9, -1.4, 1.5, w=170, h=112, pad=(14, 24, 14, 12))
    g.fill(cos, zero, 0, pi / 2, opacity=0.3)
    g.axes("x", "y")
    g.curve(cos, color="ink", width=1.5, x0=0, x1=2 * pi)
    g.dot(0, 1, r=2.6).dot(2 * pi, 1, r=2.6).vline(2 * pi, 0, 1)
    g.xticks([(pi, "π"), (2 * pi, "2π")], below=False).yticks([(1, "1"), (-1, "-1")])
    g.label(0.75, 0.55, "P", italic=True, size=12)
    save("q5d_8", g)

    # Q9: f has point symmetry in (c, 0): positive for t < c, maximum at b, minimum at d
    g = Graph(-0.6, 6.2, -1.1, 1.0, w=220, h=130, pad=(14, 26, 16, 12))
    g.axes("t", "y")
    g.curve(f9, color="ink", width=1.5, x0=-0.5, x1=6.0)
    g.xticks([(1, ""), (2, ""), (3, ""), (4, ""), (5, "")])
    for v, s in ((1, "a"), (2, "b"), (3, "c")):
        g.label(v, 0, s, dy=13, italic=True)
    for v, s in ((4, "d"), (5, "e")):
        g.label(v, 0, s, dy=-11, italic=True)
    save("q5d_9", g)


def f9(t):
    u = t - 3
    return -u / (1 + u * u / 3) ** 2


def A9(x):
    # integral from 1 to x of f9: an antiderivative of -u/(1+u^2/3)^2 is (3/2)/(1+u^2/3)
    def P(t):
        u = t - 3
        return 1.5 / (1 + u * u / 3)
    return P(x) - P(1)


# ---------------------------------------------------------------- answer figures
def answers():
    # C1 sketches of A(x)
    g = Graph(-2.4, 4.4, -9.0, 5.4, w=180, h=150, pad=(14, 30, 14, 12))
    g.axes("x", "y")
    g.vline(-2, -8, 0).hline(-8, x0=-2, x1=0).vline(-1, -4, 0).hline(-4, x0=-1, x1=0)
    g.vline(1, 0, 3).vline(3, 0, 3).hline(3, x0=0, x1=3).hline(4, x0=0, x1=2).vline(2, 0, 4)
    g.curve(step_area(4, 2), color="blue", width=2, x0=-2.25, x1=4.25)
    g.xticks([(-2, "-2"), (-1, "-1"), (1, "1"), (2, "2"), (3, "3"), (4, "4")])
    g.yticks([(4, "4"), (-4, "-4"), (-8, "-8")])
    g.dot(2, 4, r=2.4)
    g.label(3.6, 3.6, "y = A(x)", anchor="start", color="blue", size=10.5)
    save("a5d_d1A", g)
    size("a5d_d1A", 62)

    g = Graph(-3.4, 3.4, -3.4, 1.4, w=180, h=150, pad=(14, 30, 14, 12))
    g.axes("x", "y")
    g.vline(-3, -3, 0).hline(-3, x0=-3, x1=0).vline(3, -1.5, 0).hline(-1.5, x0=0, x1=3)
    g.vline(1, 0, 0.5).hline(0.5, x0=0, x1=1)
    g.curve(step_area(1, 1), color="blue", width=2, x0=-3.25, x1=3.3)
    g.xticks([(-3, "-3"), (-2, "-2"), (-1, "-1"), (1, "1"), (2, "2")]).yticks([(-3, "-3"), (-1.5, "-3/2")])
    g.label(0, 0.5, "1/2", dx=-8, dy=-4, anchor="end", size=10)
    g.label(3, 0, "3", dy=-11, size=11)
    g.dot(1, 0.5, r=2.4)
    save("a5d_y1A", g)
    size("a5d_y1A", 62)

    # Q3 sketches of A(x)
    def A3a(x):
        return x + (x - 2) ** 3 / 12 + 8 / 12

    g = Graph(-0.6, 4.6, -0.6, 6.0, w=170, h=128, pad=(34, 24, 24, 12))
    g.axes("x", "A(x)")
    g.curve(A3a, color="blue", width=2, x0=0, x1=4.4)
    g.dot(0, 0, r=2.4).dot(2, A3a(2), r=2.4).xticks([(2, "2")])
    g.vline(2, 0, A3a(2))
    combine_a = g

    def A3b(x):
        return atan(x - 2) + atan(2)

    g = Graph(-0.6, 8.6, -0.4, 3.2, w=170, h=128, pad=(34, 24, 24, 12))
    g.axes("x", "A(x)")
    g.curve(A3b, color="blue", width=2, x0=0, x1=8.4)
    g.dot(0, 0, r=2.4).dot(2, A3b(2), r=2.4).xticks([(2, "2")])
    g.vline(2, 0, A3b(2))
    combine("a5d_q3", [combine_a, g], gap=24, mm=110)

    # Q7: each graph shows y = f(t) (grey, dashed) and y = A(x) (blue)
    def q7(f, A, lo, hi, ylo, yhi, x0f, x0A):
        g = Graph(lo, hi, ylo, yhi, w=150, h=136, pad=(14, 28, 22, 12))
        g.axes("x", "y")
        g.curve(f, color="faint", width=1.5, dash="5 3", x0=x0f, x1=hi - 0.05)
        g.curve(A, color="blue", width=2, x0=x0A, x1=hi - 0.05)
        return g

    ga = q7(exp, lambda x: exp(x) - 1, -3, 1.6, -1.6, 4.0, -2.95, -2.95)
    ga.hline(-1, x0=-3, x1=1.5).yticks([(1, "1"), (-1, "-1")])
    gb = q7(log, lambda x: x * log(x) - x + 1, -0.4, 3.4, -2.4, 2.4, 0.08, 0.002)
    gb.xticks([(1, "1")]).yticks([(1, "1")])
    gc = q7(lambda t: 1 / t, log, -0.4, 3.4, -2.4, 3.0, 0.34, 0.09)
    gc.xticks([(1, "1")])
    combine("a5d_q7", [ga, gb, gc], gap=14, mm=140)

    # Q8: y = A(x) = sin x and y = A(x) = 1 - cos x
    g = Graph(-0.4, 6.9, -1.4, 1.5, w=180, h=122, pad=(34, 26, 24, 14))
    g.axes("x", "A(x)")
    g.curve(sin, color="blue", width=2, x0=0, x1=2 * pi)
    g.xticks([(pi / 2, "π/2"), (pi, "π")], below=False).xticks([(3 * pi / 2, "3π/2"), (2 * pi, "2π")], below=False)
    g.yticks([(1, "1"), (-1, "-1")])
    g2 = Graph(-0.4, 6.9, -0.4, 2.4, w=180, h=122, pad=(34, 26, 24, 14))
    g2.axes("x", "A(x)")
    g2.curve(lambda x: 1 - cos(x), color="blue", width=2, x0=0, x1=2 * pi)
    g2.xticks([(pi / 2, "π/2"), (pi, "π"), (3 * pi / 2, "3π/2"), (2 * pi, "2π")]).yticks([(1, "1"), (2, "2")])
    combine("a5d_q8", [g, g2], gap=24, mm=120)

    # Q9 f: sketch of A(x)
    g = Graph(-0.6, 6.4, -1.0, 1.6, w=210, h=126, pad=(30, 24, 22, 12))
    g.axes("x", "A(x)")
    g.curve(A9, color="blue", width=2, x0=-0.5, x1=6.3)
    for v, s in ((1, "a"), (2, "b"), (3, "c"), (4, "d"), (5, "e")):
        g.xticks([(v, "")]).label(v, 0, s, dy=13, italic=True)
    g.dot(3, A9(3), r=2.4).vline(3, 0, A9(3))
    save("a5d_q9", g)
    size("a5d_q9", 80)


if __name__ == "__main__":
    lesson()
    exercise()
    answers()
