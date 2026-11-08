"""Figures for Lesson 5A (kept apart from figs.py, which the scaffold task owns; same pattern as ch17/figs_17a.py).

Run: python3 workspace/build/int1/figs_5a.py   (writes svg/c5a_*.svg and svg/q5a_*.svg)
"""
import os
import sys
from math import sqrt, log

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save, ACC, INK, FAINT, _txt  # noqa: E402
from figfit import masked  # noqa: E402

GREY = "#9aa3ad"


def hatch_defs(g, pid):
    g.items.insert(0, f'<defs><pattern id="{pid}" patternUnits="userSpaceOnUse" width="5" height="5" '
                      f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" stroke="{INK}" '
                      f'stroke-width="0.8"/></pattern></defs>')


def rect(g, x0, x1, y0, y1, kind="plain", pid=None, width=1.1):
    """Rectangle [x0, x1] x [y0, y1] in graph units. kind: plain | grey | hatch | blue."""
    X0, X1, Y0, Y1 = g.X(x0), g.X(x1), g.Y(y0), g.Y(y1)
    fill = {"plain": "none", "grey": GREY, "hatch": f"url(#{pid})", "blue": ACC["blue"]}[kind]
    op = {"plain": 1, "grey": 0.55, "hatch": 1, "blue": 0.16}[kind]
    g.items.append(f'<rect x="{min(X0, X1):.1f}" y="{min(Y0, Y1):.1f}" width="{abs(X1 - X0):.1f}" '
                   f'height="{abs(Y1 - Y0):.1f}" fill="{fill}" fill-opacity="{op}" stroke="{INK}" stroke-width="{width}"/>')


def seg(g, x0, y0, x1, y1, color="ink", width=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{d}/>')


def zero(x):
    return 0.0


# ---------------------------------------------------------------- lesson figures
def lesson():
    # three diagrams: the region, the region cut into strips, one strip
    def f(x):
        return 1 + 0.11 * (x - 0.8) ** 2

    for name in ("c5a_reg", "c5a_strips", "c5a_strip"):
        g = Graph(-1, 6.2, 0, 3.4, w=196, h=128, pad=(14, 32, 18, 22))
        if name == "c5a_reg":
            g.fill(f, zero, 1, 5, opacity=0.2)
            g.vline(1, 0, f(1), color="ink", dash="", width=1.1).vline(5, 0, f(5), color="ink", dash="", width=1.1)
        elif name == "c5a_strips":
            g.fill(f, zero, 1, 5, opacity=0.2)
            for k in range(11):
                xx = 1 + 0.4 * k
                g.vline(xx, 0, f(xx), color="ink", dash="", width=0.9)
        else:
            g.fill(f, zero, 3.6, 3.95, opacity=0.35)
            g.vline(3.6, 0, f(3.6), color="ink", dash="", width=1).vline(3.95, 0, f(3.95), color="ink", dash="", width=1)
            g.vline(1, 0, f(1), color="faint").vline(5, 0, f(5), color="faint")
            g.hline(f(3.6), color="faint", x0=0, x1=3.6)
            g.label(0, f(3.6), "f(x)", dx=-3, dy=-9, anchor="end", size=11, italic=True)
            g.label(4.2, 2.95, "x + δx", size=11, italic=True)
            g.items.append(f'<path d="M{g.X(4.25):.1f},{g.Y(2.75):.1f} C{g.X(4.6):.1f},{g.Y(2.1):.1f} '
                           f'{g.X(3.7):.1f},{g.Y(1.2):.1f} {g.X(3.95):.1f},{g.Y(0.35):.1f}" fill="none" '
                           f'stroke="{INK}" stroke-width="1"/>')
        g.axes("x", "y")
        g.curve(f, color="ink", width=1.5, x0=-0.7, x1=6.0)
        ticks = [(1, "a"), (5, "b")] if name != "c5a_strip" else [(1, "a"), (3.6, "x"), (5, "b")]
        for v, lab in ticks:
            g.label(v, 0, lab, dy=13, size=11.5, italic=True)
        save(name, g)

    # Worked example 1 a-d
    def lin(a, b, name, yt):
        g = Graph(-1.6, 5, -1.6, 4.2, w=150, h=118, pad=(14, 32, 16, 14))
        g.fill(lambda x: x - 1, zero, a, b, opacity=0.25)
        g.axes("x", "y")
        g.curve(lambda x: x - 1, color="ink", width=1.5, x0=-0.5, x1=4.9)
        g.vline(b, 0, b - 1, color="ink", dash="", width=1.1)
        if a > 1:
            g.vline(a, 0, a - 1, color="ink", dash="", width=1.1)
        for v in yt:
            g.hline(v, color="faint", x0=0, x1=v + 1)
        g.xticks([(t, str(t)) for t in sorted({1, a, b}) if t])
        g.yticks([(v, str(v)) for v in yt] + [(-1, "-1")])
        save(name, g)
    lin(1, 4, "c5a_e1a", [1, 3])
    lin(2, 4, "c5a_e1b", [1, 3])

    g = Graph(-3, 3, -0.4, 3.2, w=150, h=108, pad=(14, 32, 16, 14))
    g.fill(abs, zero, -2, 2, opacity=0.25)
    g.axes("x", "y")
    g.curve(abs, color="ink", width=1.5, x0=-2.9, x1=2.9)
    g.vline(-2, 0, 2, color="ink", dash="", width=1.1).vline(2, 0, 2, color="ink", dash="", width=1.1)
    g.hline(2, color="faint", x0=-2, x1=2)
    g.xticks([(-2, "-2"), (2, "2")]).yticks([(2, "")])
    g.label(0, 2, "2", dx=-5, dy=-8, anchor="end", size=11)
    save("c5a_e1c", g)

    g = Graph(-6.5, 6.5, -0.6, 6.2, w=150, h=92, pad=(14, 32, 16, 14))
    g.fill(lambda x: sqrt(max(0, 25 - x * x)), zero, -5, 5, opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: sqrt(max(0, 25 - x * x)), color="ink", width=1.5, x0=-5, x1=5)
    g.dot(-5, 0, r=2.4).dot(5, 0, r=2.4)
    g.xticks([(-5, "-5"), (5, "5")])
    g.label(0, 5, "5", dx=-5, dy=-8, anchor="end", size=11)
    save("c5a_e1d", g)

    # Concept 3: the region under y = x^2 inside the unit square
    g = Graph(-0.3, 1.3, -0.15, 1.3, w=150, h=128, pad=(14, 32, 16, 18))
    g.fill(lambda x: x * x, zero, 0, 1, opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: x * x, color="ink", width=1.5, x0=0, x1=1.12)
    g.vline(1, 0, 1, color="ink", dash="", width=1.1).hline(1, color="faint", x0=0, x1=1)
    g.xticks([(1, "1")]).yticks([(1, "1")])
    save("c5a_sq", g)

    # the four trapping pictures: n = 2, 3, 4, 5 strips (upper hatched, lower grey)
    for n in (2, 3, 4, 5):
        name = f"c5a_tr{n}"
        g = Graph(-0.25, 1.35, -0.15, 1.3, w=158, h=132, pad=(14, 32, 16, 22))
        pid = "h" + name
        hatch_defs(g, pid)
        g.axes("x", "y")
        for k in range(1, n + 1):
            rect(g, (k - 1) / n, k / n, 0, (k / n) ** 2, "hatch", pid)
        for k in range(1, n + 1):
            if k > 1:
                rect(g, (k - 1) / n, k / n, 0, ((k - 1) / n) ** 2, "grey")
        g.curve(lambda x: x * x, color="ink", width=1.4, x0=0, x1=1.12)
        g.hline(1, color="faint", x0=0, x1=1)
        g.yticks([(1, "1")])
        ticks = [(1, "1")]
        if n <= 3:
            ticks += [(k / n, f"{k}/{n}") for k in range(1, n)]
        g.xticks(ticks)
        save(name, g)

    # the general picture with n strips (drawn with 10 strips; the middle ones are left out)
    g = Graph(-0.06, 1.12, -0.08, 1.08, w=430, h=200, pad=(26, 26, 16, 34))
    pid = "hc5a_trn"
    hatch_defs(g, pid)
    g.axes("x", "y")
    n = 10
    for k in list(range(1, 6)) + [10]:
        rect(g, (k - 1) / n, k / n, 0, (k / n) ** 2, "hatch", pid)
        if k > 1:
            rect(g, (k - 1) / n, k / n, 0, ((k - 1) / n) ** 2, "grey")
    g.curve(lambda x: x * x, color="ink", width=1.4, x0=0, x1=1.06)
    g.hline(1, color="faint", x0=0, x1=0.9)
    g.yticks([(1, "1")])
    labs = [(k / n, f"{k}/n") for k in range(1, 6)] + [(0.9, "n-1/n"), (1.0, "n/n")]
    g.xticks(labs)
    g.label(1.0, 0, "= 1", dx=12, dy=18, anchor="start", size=11)
    g.label(0.72, 0, "· · ·", dy=18, size=12)
    g.label(0.68, 0.35, "· · ·", size=12)
    save("c5a_trn", g)


# ---------------------------------------------------------------- exercise figures
def parab(g, x0=-0.55, x1=1.12):
    g.curve(lambda x: x * x, color="ink", width=1.4, x0=x0, x1=x1)
    g.label(0.62, 1.42, "y = x²", anchor="end", size=11, italic=True)


def exercise():
    # Q1, Q2, Q3: chords under y = x^2
    for q in (1, 2, 3):
        g = Graph(-0.6, 1.25, -0.25, 1.5, w=160, h=104, pad=(14, 32, 18, 22))
        g.axes("x", "y")
        parab(g)
        g.yticks([(1, "1")])
        if q == 1:
            seg(g, 0, 0, 1, 1)
            seg(g, 1, 0, 1, 1)
            g.xticks([(1, "1")])
            g.label(1, 1, "B", dx=-9, dy=-7, size=11.5, italic=True)
            g.label(1, 0, "A", dx=8, dy=-8, size=11.5, italic=True)
        elif q == 2:
            seg(g, 0, 0, 0.5, 0.25)
            seg(g, 0.5, 0.25, 1, 1)
            seg(g, 0.5, 0, 0.5, 0.25)
            seg(g, 1, 0, 1, 1)
            g.xticks([(0.5, "1/2"), (1, "1")])
            g.label(1, 1, "B", dx=-9, dy=-7, size=11.5, italic=True)
            g.label(1, 0, "A", dx=8, dy=-8, size=11.5, italic=True)
            g.label(0.5, 0.25, "D", dx=-9, dy=-7, size=11.5, italic=True)
            g.label(0.5, 0, "C", dx=8, dy=-8, size=11.5, italic=True)
        else:
            pts = [(k / 4, (k / 4) ** 2) for k in range(5)]
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                seg(g, xa, ya, xb, yb)
            for xx, yy in pts[1:]:
                seg(g, xx, 0, xx, yy)
            g.xticks([(0.25, "1/4"), (0.5, "1/2"), (0.75, "3/4"), (1, "1")])
        g.label(0, 0, "O", dx=-8, dy=11, size=11.5, italic=True) if q < 3 else None
        save(f"q5a_{q}", g)

    # Q4 a-h, Q5 a-h: sketches of the definite integrals
    def sk(name, f, a, b, xr, yr, xt, yt, pts=(), curve=True, xlab=None):
        g = Graph(xr[0], xr[1], yr[0], yr[1], w=150, h=92, pad=(14, 32, 12, 16))
        g.fill(f, zero, a, b, opacity=0.25)
        g.axes("x", "y")
        g.curve(f, color="ink", width=1.4, x0=xr[0] + 0.03 * (xr[1] - xr[0]), x1=xr[1] - 0.02 * (xr[1] - xr[0]))
        for v in (a, b):
            if abs(f(v)) > 1e-9:
                g.vline(v, 0, f(v), color="ink", dash="", width=1.0)
        for v in yt:
            g.hline(v[0], color="faint", x0=0 if xr[0] < 0 else xr[0], x1=v[1]) if isinstance(v[1], (int, float)) else None
        g.xticks([(t, s) for t, s in xt])
        for v in yt:
            if v[2]:
                g.label(0, v[0], v[2], dx=-5, dy=(-7 if v[0] > 0 else 9) if v[1] != "below" else 8, anchor="end", size=11)
        for (px, py, s, dx, dy, anc) in pts:
            g.label(px, py, s, dx=dx, dy=dy, anchor=anc, size=10.5)
        save(name, g)

    c = lambda k: (lambda x: k)  # noqa: E731
    sk("q5a_4a", c(3), 0, 2, (-0.6, 3), (-0.6, 4), [(2, "2")], [(3, None, "3")])
    sk("q5a_4b", c(4), 0, 3, (-0.6, 4.2), (-0.6, 5.2), [(3, "3")], [(4, None, "4")])
    sk("q5a_4c", lambda x: x, 0, 4, (-1.4, 5.2), (-1.4, 5.4), [(4, "4")], [(4, 4, "4")])
    sk("q5a_4d", lambda x: 2 * x, 0, 3, (-0.6, 4), (-1.2, 7.6), [(3, "3")], [(6, 3, "6")])
    sk("q5a_4e", lambda x: 2 - x, 0, 2, (-1.2, 3.2), (-1.0, 3.0), [(2, "")], [(2, "below", "2")],
       pts=[(2, 0, "2", -4, 13, "middle")])
    sk("q5a_4f", lambda x: 5 - x, 0, 5, (-1.0, 6.6), (-1.0, 6.4), [(5, "")], [(5, "below", "5")],
       pts=[(5, 0, "5", -4, 13, "middle")])
    sk("q5a_4g", lambda x: x + 2, 0, 2, (-2.6, 3.2), (-0.8, 5.4), [(2, "2")], [(4, 2, "4"), (2, None, "2")],
       pts=[(0, 0, "0", -5, 12, "end")])
    sk("q5a_4h", lambda x: x + 3, 0, 4, (-3.2, 5.4), (-0.8, 9.0), [(4, "4")], [(7, 4, "7"), (3, None, "3")],
       pts=[(0, 0, "0", -5, 12, "end")])

    sk("q5a_5a", c(2), -1, 3, (-2.2, 4.2), (-1.4, 3.6), [(-1, "-1"), (3, "3")], [(2, None, "2")])
    sk("q5a_5b", c(5), -3, 2, (-4.2, 3.4), (-0.8, 6.4), [(-3, "-3"), (2, "2")], [(5, None, "5")])
    sk("q5a_5c", lambda x: 2 * x + 4, -2, 1, (-3, 2.2), (-0.8, 7.4), [(-2, "-2"), (1, "1")], [(4, None, "4")],
       pts=[(1, 6, "(1, 6)", 4, -2, "start")])
    sk("q5a_5d", lambda x: 3 * x + 3, -1, 3, (-2, 4.4), (-1.6, 16.5), [(-1, ""), (3, "3")], [(12, 3, "12"), (3, None, "3")],
       pts=[(-1, 0, "-1", -2, -9, "end")])
    sk("q5a_5e", lambda x: x + 4, -1, 5, (-3.6, 6.8), (-0.8, 11), [(-1, "-1"), (5, "5")], [(4, None, "4")],
       pts=[(5, 9, "(5, 9)", -4, -10, "end"), (-1, 3, "(-1, 3)", -4, -8, "end")])
    sk("q5a_5f", lambda x: x + 6, -2, 2, (-5.2, 4.4), (-0.8, 10.4), [], [(6, None, "6")],
       pts=[(2, 8, "(2, 8)", 4, 6, "start"), (-2, 4, "(-2, 4)", -4, -8, "end")])
    sk("q5a_5g", abs, -3, 3, (-4.2, 4.4), (-0.8, 4.2), [(-3, "-3"), (3, "3")], [(3, 3, "3")])
    sk("q5a_5h", lambda x: abs(2 * x), -2, 2, (-3.2, 3.4), (-0.8, 5.6), [(-2, "-2"), (2, "2")], [(4, 2, "4")])

    # Q8: lower and upper rectangles of width 1/4
    g = Graph(-0.6, 1.25, -0.2, 1.5, w=180, h=155, pad=(14, 32, 18, 24))
    g.axes("x", "y")
    for k in range(1, 5):
        rect(g, (k - 1) / 4, k / 4, 0, (k / 4) ** 2, "plain", width=0.9)
        rect(g, (k - 1) / 4, k / 4, 0, ((k - 1) / 4) ** 2, "plain", width=0.9)
    parab(g)
    g.yticks([(1, "1")])
    g.xticks([(0.25, "1/4"), (0.5, "1/2"), (0.75, "3/4"), (1, "1")])
    for px, py, s, dx in ((0.75, 0, "P", -8), (1, 0, "Q", 9), (1, 9 / 16, "R", 9), (1, 1, "S", 9),
                          (0.75, 1, "T", -8), (0.75, 9 / 16, "U", -8)):
        g.label(px, py, s, dx=dx, dy=-8 if py == 0 else (-7 if s == "U" else 0), size=11.5, italic=True)
    save("q5a_8", g)

    # Q9: y = 2^x, region from 0 to 1 shaded
    g = Graph(-1.8, 1.6, -0.3, 3.3, w=160, h=130, pad=(14, 32, 16, 14))
    g.fill(lambda x: 2 ** x, zero, 0, 1, color="ink", opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: 2 ** x, color="ink", width=1.4, x0=-1.75, x1=1.55)
    g.vline(1, 0, 2, color="ink", dash="", width=1.0)
    g.xticks([(1, "1")]).yticks([(1, "1"), (2, "2")])
    save("q5a_9", g)

    # Q10: y = ln x, region from 2 to 4 shaded
    g = Graph(-0.8, 5.6, -2.2, 2.2, w=170, h=130, pad=(14, 32, 16, 12))
    g.fill(log, zero, 2, 4, color="ink", opacity=0.25)
    g.axes("x", "y")
    g.curve(log, color="ink", width=1.4, x0=0.12, x1=5.5)
    g.vline(4, 0, log(4), color="ink", dash="", width=1.0)
    g.xticks([(1, "1"), (2, "2"), (4, "4")])
    save("q5a_10", g)

    # Q11: y = 1/(x + 1), one strip and two strips
    for name, n in (("q5a_11a", 1), ("q5a_11b", 2)):
        g = Graph(-1.4, 2.4, -0.45, 2.3, w=160, h=112, pad=(14, 32, 16, 18))
        g.axes("x", "y")
        g.vline(-1, -0.45, 2.3, color="ink", dash="4 3", width=1.0)
        for k in range(1, n + 1):
            rect(g, (k - 1) / n, k / n, 0, 1 / (1 + (k - 1) / n), "plain", width=0.9)
            rect(g, (k - 1) / n, k / n, 0, 1 / (1 + k / n), "plain", width=0.9)
        g.curve(lambda x: 1 / (x + 1), color="ink", width=1.4, x0=-0.58, x1=2.3)
        ticks = [(-1, "-1"), (1, "1")] + ([(0.5, "1/2")] if n == 2 else [])
        g.xticks(ticks)
        g.label(0, 1, "1", dx=-5, dy=-7, anchor="end", size=11)
        save(name, g)

    # Q13, Q14: graph paper, 20 little divisions to 1 unit
    for name, fn, x1 in (("q5a_13", lambda x: x * x, 1.06), ("q5a_14", lambda x: sqrt(max(0.0, 1 - x * x)), 1.0)):
        lo, hi = -0.1, 1.1
        g = Graph(lo, hi, lo, hi, w=290, h=290, pad=(14, 32, 18, 16))
        for k in range(-2, 23):
            v = k / 20
            wd = 1.3 if k % 10 == 0 else (0.75 if k % 5 == 0 else 0.35)
            col = INK if k % 5 == 0 else FAINT
            g.items.append(f'<line x1="{g.X(v):.1f}" y1="{g.Y(lo):.1f}" x2="{g.X(v):.1f}" y2="{g.Y(hi):.1f}" stroke="{col}" stroke-width="{wd}"/>')
            g.items.append(f'<line x1="{g.X(lo):.1f}" y1="{g.Y(v):.1f}" x2="{g.X(hi):.1f}" y2="{g.Y(v):.1f}" stroke="{col}" stroke-width="{wd}"/>')
        g.axes("x", "y")
        g.curve(fn, color="ink", width=1.2, x0=0, x1=x1, n=600)
        g.label(1, 0, "1", dx=-6, dy=9, size=11, anchor="end")
        g.items[-1] = masked(g.items[-1])    # on graph paper, the unit labels sit on white
        g.label(0, 1, "1", dx=6, dy=-8, size=11, anchor="start")
        g.items[-1] = masked(g.items[-1])
        save(name, g)


if __name__ == "__main__":
    lesson()
    exercise()
