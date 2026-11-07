"""Figures for Lesson 12F (kept apart from figs.py, which the scaffold task owns).

Run: python3 workspace/build/int3/figs_12f.py   (writes svg/c12f_*.svg, svg/q12f_*.svg, svg/pp12f_*.svg, svg/a12f_*.svg)
"""
import os
import sys
from math import cos, exp, log, pi, sin, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Fig, Graph, save, tip, ACC, INK, _txt  # noqa: E402

H = pi / 2
BLUE = ACC["blue"]


def new(xmin, xmax, ymin, ymax, w, h, pad=(14, 30, 18, 14)):
    g = Graph(xmin, xmax, ymin, ymax, w=w, h=h, pad=pad)
    g.axes("x", "y")
    return g


def edge(g, top, bottom, a, b, n=120):
    """Thin blue outline of a shaded region (top and bottom functions of x)."""
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    pts = [f"{g.X(t):.1f},{g.Y(top(t)):.1f}" for t in xs] + [f"{g.X(t):.1f},{g.Y(bottom(t)):.1f}" for t in reversed(xs)]
    g.items.insert(1, f'<polygon points="{" ".join(pts)}" fill="none" stroke="{BLUE}" stroke-width="1" stroke-opacity=".7"/>')
    return g


def edge_y(g, right, left, c, d, n=120):
    ys = [c + (d - c) * i / n for i in range(n + 1)]
    pts = [f"{g.X(right(t)):.1f},{g.Y(t):.1f}" for t in ys] + [f"{g.X(left(t)):.1f},{g.Y(t):.1f}" for t in reversed(ys)]
    g.items.insert(1, f'<polygon points="{" ".join(pts)}" fill="none" stroke="{BLUE}" stroke-width="1" stroke-opacity=".7"/>')
    return g


def row(name, panels, gap=6, lw=14):
    """Put several Graph panels side by side, each with a bold part letter in a gutter at its top left."""
    W = sum(p.w + lw for _, p in panels) + gap * (len(panels) - 1)
    Hh = max(p.h for _, p in panels)
    out, x0 = [], 0
    for letter, p in panels:
        out.append(f'<text x="{x0 + 1}" y="13" font-size="13" font-weight="700" fill="{ACC["teal"]}">{letter}</text>')
        inner = p.svg().replace('<svg xmlns="http://www.w3.org/2000/svg"', f'<svg x="{x0 + lw}" y="0"', 1)
        out.append(inner)
        x0 += p.w + lw + gap
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" '
           f'font-family="Inter, Arial, sans-serif">' + "".join(out) + "</svg>")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg", name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)


def curve_y(g, xf, y0, y1, color="blue", width=2.0, n=300, dash=None):
    """Curve given as x = xf(y)."""
    pts = [f"{g.X(xf(y0 + (y1 - y0) * i / n)):.1f},{g.Y(y0 + (y1 - y0) * i / n):.1f}" for i in range(n + 1)]
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"{d} stroke-linejoin="round"/>')
    return g


def arrow_y(g, xf, y, toward, color="blue", head=7):
    """Arrowhead at the end of a curve x = xf(y), pointing in the direction of increasing y (toward=1) or decreasing."""
    import math
    h = 1e-3 * (g.ymax - g.ymin)
    xa, ya = g.X(xf(y)), g.Y(y)
    xb, yb = g.X(xf(y - toward * h)), g.Y(y - toward * h)
    a = math.atan2(ya - yb, xa - xb)
    p1 = (xa - head * cos(a - 0.4), ya - head * sin(a - 0.4))
    p2 = (xa - head * cos(a + 0.4), ya - head * sin(a + 0.4))
    g.items.append(f'<path d="M{xa:.1f},{ya:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} z" fill="{ACC[color]}"/>')
    return g


# ---------------------------------------------------------------- Concept 1: slicing the solid
def fig_slice():
    f = lambda t: 0.55 + 0.05 * t + 0.045 * t * t
    a, b, xm, dxw = 1.6, 4.0, 2.9, 0.22
    # left panel: the region under y = f(x) from a to b, with one strip
    g = new(-0.6, 5.2, -0.5, 2.0, 250, 122)
    g.fill(f, lambda t: 0.0, a, b, color="blue")
    g.fill(f, lambda t: 0.0, xm, xm + dxw, color="blue", opacity=0.45)
    g.curve(f, color="blue", width=2.0, x0=0.2, x1=4.9)
    tip(g, f, 4.9, 1).vline(a, 0, f(a), color="blue", dash="", width=1.2).vline(b, 0, f(b), color="blue", dash="", width=1.2)
    g.vline(xm, 0, f(xm), color="ink", dash="", width=1).vline(xm + dxw, 0, f(xm + dxw), color="ink", dash="", width=1)
    g.xticks([(a, "a"), (b, "b")])
    g.label(xm + dxw / 2, 0, "dx", dy=26, size=11, italic=True)
    yy = g.Y(0) + 13
    g.items.append(f'<line x1="{g.X(xm) - 14:.1f}" y1="{yy:.1f}" x2="{g.X(xm):.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="1"/>')
    g.items.append(f'<path d="M{g.X(xm):.1f},{yy:.1f} l-6,-3 v6 z" fill="{INK}"/>')
    g.items.append(f'<line x1="{g.X(xm + dxw) + 14:.1f}" y1="{yy:.1f}" x2="{g.X(xm + dxw):.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="1"/>')
    g.items.append(f'<path d="M{g.X(xm + dxw):.1f},{yy:.1f} l6,-3 v6 z" fill="{INK}"/>')
    g.label(xm + dxw / 2, f(xm), "y = f(x)", dx=-30, dy=-30, size=11, italic=True)
    left = g.svg()
    # right panel: the solid, with the slice of width dx
    w, hgt = 290, 128
    X0, Y0, sx, sy = 30, 62, 52, 22
    X = lambda t: X0 + (t - 0.0) * sx
    Yp = lambda v: Y0 - v * sy
    rx = lambda r: 0.28 * r * sy
    it = []
    up = [f"{X(a + (b - a) * i / 80):.1f},{Yp(f(a + (b - a) * i / 80)):.1f}" for i in range(81)]
    dn = [f"{X(a + (b - a) * i / 80):.1f},{Yp(-f(a + (b - a) * i / 80)):.1f}" for i in range(80, -1, -1)]
    it.append(f'<polygon points="{" ".join(up + dn)}" fill="{BLUE}" fill-opacity=".14" stroke="none"/>')
    it.append(f'<polyline points="{" ".join(up)}" fill="none" stroke="{BLUE}" stroke-width="1.6"/>')
    it.append(f'<polyline points="{" ".join(dn)}" fill="none" stroke="{BLUE}" stroke-width="1.6"/>')
    for t, op in ((a, ".25"), (b, ".25")):
        it.append(f'<ellipse cx="{X(t):.1f}" cy="{Y0}" rx="{rx(f(t)):.1f}" ry="{f(t) * sy:.1f}" fill="{BLUE}" fill-opacity="{op}" stroke="{BLUE}" stroke-width="1.4"/>')
    # the slice: two ellipses joined
    for t in (xm, xm + dxw):
        it.append(f'<ellipse cx="{X(t):.1f}" cy="{Y0}" rx="{rx(f(t)):.1f}" ry="{f(t) * sy:.1f}" fill="{ACC["amber"]}" fill-opacity=".35" stroke="{ACC["amber"]}" stroke-width="1.4"/>')
    it.append(f'<line x1="{X(xm):.1f}" y1="{Yp(f(xm)):.1f}" x2="{X(xm + dxw):.1f}" y2="{Yp(f(xm + dxw)):.1f}" stroke="{ACC["amber"]}" stroke-width="1.4"/>')
    it.append(f'<line x1="{X(xm):.1f}" y1="{Yp(-f(xm)):.1f}" x2="{X(xm + dxw):.1f}" y2="{Yp(-f(xm + dxw)):.1f}" stroke="{ACC["amber"]}" stroke-width="1.4"/>')
    # radius of the slice
    it.append(f'<line x1="{X(xm + dxw):.1f}" y1="{Y0}" x2="{X(xm + dxw):.1f}" y2="{Yp(f(xm + dxw)):.1f}" stroke="{INK}" stroke-width="1.2"/>')
    it.append(_txt(X(xm + dxw) + 5, Yp(f(xm + dxw)) - 9, "y", "start", size=12, italic=True))
    # axes
    it.append(f'<line x1="10" y1="{Y0}" x2="{w - 16}" y2="{Y0}" stroke="{INK}" stroke-width="1.4"/>')
    it.append(f'<path d="M{w - 16},{Y0} l-7,-3.5 v7 z" fill="{INK}"/>')
    it.append(_txt(w - 12, Y0 + 12, "x", "start", italic=True))
    it.append(f'<line x1="{X(0):.1f}" y1="{hgt - 8}" x2="{X(0):.1f}" y2="10" stroke="{INK}" stroke-width="1.4"/>')
    it.append(f'<path d="M{X(0):.1f},10 l-3.5,7 h7 z" fill="{INK}"/>')
    it.append(_txt(X(0) - 6, 12, "y", "end", italic=True))
    it.append(_txt(X(a), Yp(-f(a)) + 11, "a", size=11, italic=True))
    it.append(_txt(X(b), Yp(-f(b)) + 11, "b", size=11, italic=True))
    it.append(_txt(X(xm + dxw / 2), Yp(-f(xm + dxw)) + 13, "dx", size=11, italic=True))
    right = (f'<svg x="262" y="0" viewBox="0 0 {w} {hgt}" width="{w}" height="{hgt}">' + "".join(it) + "</svg>")
    W = 262 + w
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {hgt}" width="{W}" height="{hgt}" font-family="Inter, Arial, sans-serif">'
           + left.replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg x="0" y="4"', 1) + right + "</svg>")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg", "c12f_slice.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)


# ---------------------------------------------------------------- worked examples
def fig_ex22():
    s = lambda t: sqrt(max(0.0, 16 - t * t))
    g = new(-5.0, 5.6, -1.4, 5.0, 180, 125)
    g.fill(s, lambda t: 0.0, 2, 4, color="blue")
    edge(g, s, lambda t: 0.0, 2, 4)
    g.curve(s, color="blue", width=2.0, x0=-4, x1=4, n=800)
    g.dot(-4, 0).dot(4, 0)
    g.vline(2, -1.3, 4.9, color="ink", dash="", width=1.3)
    g.items.append(f'<path d="M{g.X(2)},{g.Y(4.9) - 6} l-3.5,7 h7 z" fill="{INK}"/>')
    g.items.append(f'<path d="M{g.X(2)},{g.Y(-1.3) + 6} l-3.5,-7 h7 z" fill="{INK}"/>')
    g.xticks([(-4, "-4"), (2, ""), (4, "")]).yticks([(4, "4")])
    g.label(2, 0, "2", dx=-7, dy=13, size=11).label(4, 0, "4", dx=6, dy=13, size=11)
    save("c12f_ex22", g)


def fig_ex23():
    g = new(-2.6, 2.6, -0.5, 5.2, 190, 160)
    g.fill(lambda t: 4.0, lambda t: t * t, -2, 2, color="blue")
    edge(g, lambda t: 4.0, lambda t: t * t, -2, 2)
    g.curve(lambda t: t * t, color="blue", width=2.0, x0=-2.25, x1=2.25)
    tip(g, lambda t: t * t, 2.25, 1)
    tip(g, lambda t: t * t, -2.25, -1)
    g.hline(4, color="ink", dash="", x0=-2.5, x1=2.5, width=1.3)
    g.items.append(f'<path d="M{g.X(2.5) + 6},{g.Y(4)} l-7,-3.5 v7 z" fill="{INK}"/>')
    g.items.append(f'<path d="M{g.X(-2.5) - 6},{g.Y(4)} l7,-3.5 v7 z" fill="{INK}"/>')
    g.yticks([(4, "")]).label(0, 4, "4", dx=-8, dy=-10, size=11)
    g.label(1.6, 2.6, "y = x²", dx=12, anchor="start", size=11, italic=True)
    save("c12f_ex23", g)


def fig_ex24():
    p = lambda t: 4 - t * t
    g = new(-2.7, 2.9, -0.9, 4.8, 190, 160)
    g.fill(p, lambda t: 4 - 2 * t, 0, 2, color="blue")
    edge(g, p, lambda t: 4 - 2 * t, 0, 2)
    g.curve(p, color="blue", width=2.0, x0=-2.3, x1=2.3)
    tip(g, p, 2.3, 1)
    tip(g, p, -2.3, -1)
    g.items.append(f'<line x1="{g.X(0)}" y1="{g.Y(4)}" x2="{g.X(2)}" y2="{g.Y(0)}" stroke="{INK}" stroke-width="1.4"/>')
    g.dot(0, 4).dot(2, 0).dot(-2, 0)
    g.label(0, 4, "A", dx=9, dy=-6, size=11.5).label(2, 0, "B", dx=8, dy=-10, size=11.5).label(-2, 0, "C", dx=-9, dy=-10, size=11.5)
    g.label(2, 0, "2", dx=-7, dy=13, size=11).label(-2, 0, "-2", dx=-4, dy=13, size=11)
    g.label(0, 4, "4", dx=-8, dy=-2, size=11)
    save("c12f_ex24", g)


# ---------------------------------------------------------------- Exercise 12F Q3 (about the x-axis)
PW, PH = 146, 118


def p(xmin, xmax, ymin, ymax, w=PW):
    return new(xmin, xmax, ymin, ymax, w, PH, pad=(12, 26, 18, 12))


def harrow(g, y, x0, x1, color="blue"):
    g.items.append(f'<line x1="{g.X(x0)}" y1="{g.Y(y)}" x2="{g.X(x1)}" y2="{g.Y(y)}" stroke="{ACC[color]}" stroke-width="2"/>')
    g.items.append(f'<path d="M{g.X(x1) + 6},{g.Y(y)} l-7,-3.5 v7 z" fill="{ACC[color]}"/>')
    g.items.append(f'<path d="M{g.X(x0) - 6},{g.Y(y)} l7,-3.5 v7 z" fill="{ACC[color]}"/>')


def fig_q3():
    pan = []
    g = p(-3, 3, -0.8, 3.2)          # a: y = 2 from -2 to 2
    g.fill(lambda t: 2.0, lambda t: 0.0, -2, 2)
    edge(g, lambda t: 2.0, lambda t: 0.0, -2, 2)
    harrow(g, 2, -2.8, 2.8)
    g.xticks([(-2, "-2"), (2, "2")]).label(0, 2, "2", dx=-7, dy=-8, size=11).label(1.2, 2, "y = 2", dy=-10, size=11, italic=True)
    pan.append(("a", g))
    g = p(-1, 3.8, -1, 4)            # b: y = x from 0 to 3
    g.fill(lambda t: t, lambda t: 0.0, 0, 3)
    edge(g, lambda t: t, lambda t: 0.0, 0, 3)
    g.curve(lambda t: t, x0=-0.9, x1=3.6, width=2)
    tip(g, lambda t: t, 3.6, 1)
    tip(g, lambda t: t, -0.9, -1)
    g.vline(3, 0, 3, color="blue", dash="", width=1.2)
    g.xticks([(3, "3")]).label(1.6, 2.3, "y = x", dx=-6, anchor="end", size=11, italic=True)
    pan.append(("b", g))
    g = p(-2.3, 2.6, -0.6, 4.6)      # c: y = x^2 from 0 to 2
    g.fill(lambda t: t * t, lambda t: 0.0, 0, 2)
    edge(g, lambda t: t * t, lambda t: 0.0, 0, 2)
    g.curve(lambda t: t * t, x0=-2.1, x1=2.12, width=2)
    tip(g, lambda t: t * t, 2.12, 1)
    tip(g, lambda t: t * t, -2.1, -1)
    g.xticks([(2, "2")]).label(0.25, 3.9, "y = x²", anchor="start", size=10, italic=True)
    pan.append(("c", g))
    g = p(-0.6, 5, -0.6, 2.6)        # d: y = sqrt x from 2 to 4
    g.fill(lambda t: sqrt(t), lambda t: 0.0, 2, 4)
    edge(g, lambda t: sqrt(t), lambda t: 0.0, 2, 4)
    g.curve(lambda t: sqrt(max(t, 0)), x0=0, x1=4.8, width=2, n=600)
    tip(g, sqrt, 4.8, 1)
    g.dot(0, 0, r=2.6).xticks([(2, "2"), (4, "4")]).label(2.6, 2.05, "y = √x", anchor="end", size=11, italic=True)
    pan.append(("d", g))
    row("q12f_q3a", pan)
    pan = []
    s = lambda t: sqrt(max(0.0, 4 - t * t))
    g = p(-2.8, 3, -0.7, 3)          # e: quarter circle
    g.fill(s, lambda t: 0.0, 0, 2)
    edge(g, s, lambda t: 0.0, 0, 2)
    g.curve(s, x0=-2, x1=2, width=2, n=800)
    g.xticks([(-2, "-2"), (2, "2")]).label(0, 2, "2", dx=-7, dy=-8, size=11).label(0.55, 2.4, "y = √(4 − x²)", anchor="start", size=9.5, italic=True)
    pan.append(("e", g))
    c = lambda t: t ** 3
    g = p(-1.6, 1.6, -2.2, 2.2)      # f: y = x^3 from -1 to 0
    g.fill(lambda t: 0.0, c, -1, 0)
    edge(g, lambda t: 0.0, c, -1, 0)
    g.curve(c, x0=-1.28, x1=1.28, width=2)
    tip(g, c, 1.28, 1)
    tip(g, c, -1.28, -1)
    g.vline(-1, -1, 0, color="blue", dash="", width=1.2)
    g.label(-1, 0, "-1", dy=-10, size=11).label(-0.15, 1.5, "y = x³", anchor="end", size=10.5, italic=True)
    pan.append(("f", g))
    ln = lambda t: t + 2
    g = p(-6, 1.4, -3.8, 2.4)        # g: y = x + 2 from -5 to -2
    g.fill(lambda t: 0.0, ln, -5, -2)
    edge(g, lambda t: 0.0, ln, -5, -2)
    g.curve(ln, x0=-5.7, x1=0.3, width=2)
    tip(g, ln, 0.3, 1)
    tip(g, ln, -5.7, -1)
    g.vline(-5, -3, 0, color="blue", dash="", width=1.2)
    g.label(-5, 0, "-5", dy=-10, size=11).label(-2, 0, "-2", dx=-9, dy=-10, size=11).label(-4.7, -3.45, "y = x + 2", anchor="start", size=10, italic=True)
    pan.append(("g", g))
    e = lambda t: sqrt(max(0.0, 4 - 4 * t * t / 9))
    g = p(-3.8, 3.8, -2.0, 2.8)      # h: half ellipse
    g.fill(e, lambda t: 0.0, -3, 3)
    edge(g, e, lambda t: 0.0, -3, 3)
    g.curve(e, x0=-3, x1=3, width=2, n=800)
    g.xticks([(-3, "-3"), (3, "3")]).label(0, 2, "2", dx=-7, dy=-9, size=11)
    g.label(-3.3, -1.5, "y² = 4 − ⁴⁄₉x²", anchor="start", size=10.5, italic=True)
    pan.append(("h", g))
    row("q12f_q3b", pan)


# ---------------------------------------------------------------- Exercise 12F Q4 (about the y-axis)
def fig_q4():
    pan = []
    g = p(-1.6, 2.2, -0.6, 3.8)      # a: x = 1, 0 <= y <= 3
    g.fill_y(lambda y: 1.0, lambda y: 0.0, 0, 3)
    edge_y(g, lambda y: 1.0, lambda y: 0.0, 0, 3)
    g.vline(1, -0.5, 3.6, color="blue", dash="", width=2)
    g.hline(3, color="blue", dash="", x0=0, x1=1, width=1.2)
    g.label(0, 3, "3", dx=-7, size=11).xticks([(1, "1")]).label(1, 1.6, "x = 1", dx=6, anchor="start", size=11, italic=True)
    pan.append(("a", g))
    g = p(-1.5, 9.5, -1.5, 5)        # b: x = 2y, 0 <= y <= 4
    g.fill_y(lambda y: 2 * y, lambda y: 0.0, 0, 4)
    edge_y(g, lambda y: 2 * y, lambda y: 0.0, 0, 4)
    curve_y(g, lambda y: 2 * y, -1.3, 4.6)
    arrow_y(g, lambda y: 2 * y, 4.6, 1)
    arrow_y(g, lambda y: 2 * y, -1.3, -1)
    g.hline(4, color="blue", dash="", x0=0, x1=8, width=1.2)
    g.label(0, 4, "4", dx=-7, size=11).label(6.5, 2.0, "x = 2y", anchor="start", size=11, italic=True)
    pan.append(("b", g))
    g = p(-1.5, 27, -2.5, 6.2)       # c: x = y^2, 2 <= y <= 5
    g.fill_y(lambda y: y * y, lambda y: 0.0, 2, 5)
    edge_y(g, lambda y: y * y, lambda y: 0.0, 2, 5)
    curve_y(g, lambda y: y * y, -2.3, 5.1)
    arrow_y(g, lambda y: y * y, 5.1, 1)
    arrow_y(g, lambda y: y * y, -2.3, -1)
    g.hline(5, color="blue", dash="", x0=0, x1=25, width=1.2).hline(2, color="blue", dash="", x0=0, x1=4, width=1.2)
    g.label(0, 5, "5", dx=-7, size=11).label(0, 2, "2", dx=-7, size=11).label(16, 2.6, "x = y²", anchor="start", size=11, italic=True)
    pan.append(("c", g))
    g = p(-1.2, 2.8, -0.4, 3.4)      # d: x = sqrt y, 0 <= y <= 1
    g.fill_y(lambda y: sqrt(y), lambda y: 0.0, 0, 1)
    edge_y(g, lambda y: sqrt(y), lambda y: 0.0, 0, 1)
    g.curve(lambda t: t * t, x0=0, x1=1.8, width=2)
    tip(g, lambda t: t * t, 1.8, 1)
    g.hline(1, color="blue", dash="", x0=0, x1=1, width=1.2)
    g.dot(0, 0, r=2.6).label(0, 1, "1", dx=-7, size=11).label(1.5, 1.05, "x = √y", anchor="start", size=11, italic=True)
    pan.append(("d", g))
    row("q12f_q4a", pan)
    pan = []
    s = lambda y: sqrt(max(0.0, 16 - y * y))
    g = p(-6.5, 6, -5, 5, w=190)     # e: x = sqrt(16 - y^2)
    g.fill_y(s, lambda y: 0.0, -4, 4)
    edge_y(g, s, lambda y: 0.0, -4, 4)
    curve_y(g, s, -4, 4, n=800)
    g.label(0, 4, "4", dx=-7, size=11).label(0, -4, "-4", dx=-9, size=11).label(4, 0, "4", dx=7, dy=-9, size=11)
    g.label(-0.5, 2.6, "x =", anchor="end", size=10.5, italic=True).label(-0.5, 1.5, "√(16 − y²)", anchor="end", size=10.5, italic=True)
    pan.append(("e", g))
    q = lambda y: -y * y
    g = p(-12, 1.2, -4, 4, w=130)           # f: x = -y^2, -3 <= y <= 0
    g.fill_y(lambda y: 0.0, q, -3, 0)
    edge_y(g, lambda y: 0.0, q, -3, 0)
    curve_y(g, q, -3.3, 3.3)
    arrow_y(g, q, 3.3, 1)
    arrow_y(g, q, -3.3, -1)
    g.hline(-3, color="blue", dash="", x0=-9, x1=0, width=1.2)
    g.label(0, -3, "-3", dx=8, anchor="start", size=11).label(-6, 1.8, "x = −y²", anchor="end", size=11, italic=True)
    pan.append(("f", g))
    r = lambda y: 2 * y - y * y
    g = p(-3.2, 1.8, -1.6, 3.6, w=130)      # g: x = 2y - y^2, 0 <= y <= 2
    g.fill_y(r, lambda y: 0.0, 0, 2)
    edge_y(g, r, lambda y: 0.0, 0, 2)
    curve_y(g, r, -1.3, 3.3)
    arrow_y(g, r, 3.3, 1)
    arrow_y(g, r, -1.3, -1)
    g.label(0, 2, "2", dx=7, dy=-6, anchor="start", size=11).label(-0.4, 1.0, "x = 2y − y²", anchor="end", size=10.5, italic=True)
    pan.append(("g", g))
    e = lambda y: sqrt(max(0.0, 4 - 4 * y * y))
    g = p(-1.2, 2.8, -1.5, 1.6, w=130)      # h: x = sqrt(4 - 4y^2)
    g.fill_y(e, lambda y: 0.0, -1, 1)
    edge_y(g, e, lambda y: 0.0, -1, 1)
    curve_y(g, e, -1, 1, n=800)
    g.label(0, 1, "1", dx=-7, size=11).label(0, -1, "-1", dx=-9, size=11).label(2, 0, "2", dx=7, dy=-9, size=11)
    g.label(0.3, 1.32, "x = √(4 − 4y²)", anchor="start", size=10.5, italic=True)
    pan.append(("h", g))
    row("q12f_q4b", pan)


# ---------------------------------------------------------------- Exercise 12F Q16
def fig_q16():
    pan = []
    g = p(-2.3, 2.6, -0.6, 4.6)      # a
    g.fill(lambda t: t * t, lambda t: 0.0, 0, 2)
    edge(g, lambda t: t * t, lambda t: 0.0, 0, 2)
    g.curve(lambda t: t * t, x0=-2.1, x1=2.12, width=2)
    tip(g, lambda t: t * t, 2.12, 1)
    tip(g, lambda t: t * t, -2.1, -1)
    g.vline(2, 0, 4, color="blue", dash="", width=1.2)
    g.xticks([(2, "2")]).label(0.25, 3.9, "y = x²", anchor="start", size=10, italic=True)
    pan.append(("a", g))
    g = p(-0.9, 2.2, -1.5, 6.2)      # b
    g.fill(lambda t: 5.0, lambda t: 5 * t, 0, 1)
    edge(g, lambda t: 5.0, lambda t: 5 * t, 0, 1)
    g.curve(lambda t: 5 * t, x0=-0.25, x1=1.18, width=2)
    tip(g, lambda t: 5 * t, 1.18, 1)
    tip(g, lambda t: 5 * t, -0.25, -1)
    g.hline(5, color="blue", dash="", x0=0, x1=1, width=1.2)
    g.label(0, 5, "5", dx=-7, size=11).label(0.85, 2.6, "y = 5x", anchor="start", size=11, italic=True)
    pan.append(("b", g))
    g = p(-0.8, 5.4, -2.0, 3)        # c
    g.fill(lambda t: sqrt(t), lambda t: 0.0, 0, 4, n=400)
    edge(g, lambda t: sqrt(t), lambda t: 0.0, 0, 4)
    curve_y(g, lambda y: y * y, -1.7, 2.25)
    arrow_y(g, lambda y: y * y, 2.25, 1)
    arrow_y(g, lambda y: y * y, -1.7, -1)
    g.vline(4, 0, 2, color="blue", dash="", width=1.2)
    g.xticks([(4, "4")]).label(1.9, 2.55, "x = y²", anchor="start", size=10.5, italic=True)
    pan.append(("c", g))
    g = p(-1.8, 1.8, -0.5, 5.4)      # d
    g.fill(lambda t: 4.0, lambda t: t * t + 3, 0, 1)
    edge(g, lambda t: 4.0, lambda t: t * t + 3, 0, 1)
    g.curve(lambda t: t * t + 3, x0=-1.45, x1=1.45, width=2)
    tip(g, lambda t: t * t + 3, 1.45, 1)
    tip(g, lambda t: t * t + 3, -1.45, -1)
    g.hline(4, color="blue", dash="", x0=0, x1=1, width=1.2)
    g.label(0, 4, "4", dx=-7, size=11).label(0, 3, "3", dx=-8, dy=11, size=11).label(0.45, 1.7, "y = x² + 3", anchor="start", size=10, italic=True)
    pan.append(("d", g))
    row("q12f_q16", pan)


# ---------------------------------------------------------------- past papers
def fig_pp_nsb20():
    a = 1.74688174230853
    pq = lambda t: (t - 1) ** 2
    g = new(-0.4, 5.4, -1.2, 3.4, 300, 200, pad=(16, 30, 18, 14))
    for v in range(1, 6):
        g.vline(v, -1.2, 3.4, color="faint", dash="", width=0.5)
    for v in (-1, 1, 2, 3):
        g.hline(v, color="faint", dash="", width=0.5)
    g.fill(lambda t: log(t), pq, 1, a, color="blue", opacity=0.4)
    edge(g, lambda t: log(t), pq, 1, a)
    g.curve(pq, color="ink", width=1.8, x0=-0.4, x1=2.95)
    g.curve(lambda t: log(t), color="blue", width=1.8, x0=0.3, x1=5.4)
    g.dot(1, 0).dot(a, log(a))
    g.label(1, 0, "B", dx=-2, dy=-11, size=11).label(a, log(a), "A", dx=-3, dy=-12, size=11)
    g.xticks([(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]).yticks([(-1, "-1"), (1, "1"), (2, "2"), (3, "3")])
    g.label(2.25, 3.05, "y = (x − 1)²", anchor="end", size=11, italic=True).label(3.4, 1.75, "y = logₑx", anchor="start", size=11, italic=True)
    save("pp12f_nsb20", g)


def fig_pp_bb20():
    f = lambda t: sqrt(max(0.0, cos(t))) * exp(sin(t))
    g = new(-2.1, 2.2, -1.2, 2.4, 230, 150)
    g.fill(f, lambda t: 0.0, 0, H, color="blue", opacity=0.35)
    edge(g, f, lambda t: 0.0, 0, H)
    g.curve(f, color="ink", width=1.8, x0=-H, x1=H, n=800)
    g.xticks([(-H, "-π/2"), (H, "π/2")]).yticks([(1, "1"), (2, "2"), (-1, "-1")])
    g.label(0, 0, "0", dx=-7, dy=12, size=11)
    save("pp12f_bb20", g)


def fig_pp_st21():
    g = new(-4.5, 4.6, -2.4, 7.1, 250, 230)
    g.fill(lambda t: 5 - 4 * t * t, lambda t: t * t, 0, 1, color="blue", opacity=0.3)
    edge(g, lambda t: 5 - 4 * t * t, lambda t: t * t, 0, 1)
    g.curve(lambda t: t * t, color="ink", width=1.6, x0=-2.5, x1=2.5)
    tip(g, lambda t: t * t, 2.5, 1, color="ink")
    tip(g, lambda t: t * t, -2.5, -1, color="ink")
    q = lambda t: 5 - 4 * t * t
    g.curve(q, color="ink", width=1.6, x0=-1.45, x1=1.45)
    tip(g, q, 1.45, 1, color="ink")
    tip(g, q, -1.45, -1, color="ink")
    g.dot(1, 1)
    g.label(1, 1, "(1, 1)", dx=8, dy=-2, anchor="start", size=11)
    g.xticks([(v, str(v)) for v in (-4, -3, -2, 2, 3, 4)] + [(-1, ""), (1, "")]).yticks([(-1, ""), (1, ""), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6")])
    g.label(1, 0, "1", dx=6, dy=13, size=11).label(0, 1, "1", dx=-7, dy=-6, size=11).label(0, 0, "O", dx=-8, dy=12, size=11, italic=True)
    g.label(2.75, 6.6, "y = x²", anchor="start", size=11, italic=True).label(1.5, -1.9, "y = 5 − 4x²", anchor="start", size=11, italic=True)
    # rotation arrow around the y-axis near the top
    cx, cy = g.X(0), g.Y(6.55)
    g.items.append(f'<path d="M{cx - 2:.1f},{cy - 5:.1f} A12,5 0 1 0 {cx + 9:.1f},{cy - 4:.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    g.items.append(f'<path d="M{cx + 9:.1f},{cy - 4:.1f} l-6,-3 l1,6 z" fill="{INK}"/>')
    save("pp12f_st21", g)


def fig_a_jr20():
    pq = lambda t: 3 + t * t / 8
    g = new(-6.5, 6.8, -0.8, 7.5, 230, 160)
    g.fill(lambda t: 5.0, pq, -4, 4, color="blue", opacity=0.3)
    edge(g, lambda t: 5.0, pq, -4, 4)
    g.curve(pq, color="ink", width=1.8, x0=-6.2, x1=6.2)
    tip(g, pq, 6.2, 1, color="ink")
    tip(g, pq, -6.2, -1, color="ink")
    g.hline(5, color="blue", dash="", x0=-6.3, x1=6.6, width=1.4)
    g.dot(0, 3).dot(-4, 5).dot(4, 5)
    g.label(0, 3, "(0, 3)", dx=6, dy=10, anchor="start", size=10.5).label(4, 5, "(4, 5)", dx=5, dy=-10, anchor="start", size=10.5)
    g.label(-4, 5, "(−4, 5)", dx=-5, dy=-10, anchor="end", size=10.5).label(6.5, 5, "y = 5", dy=12, anchor="end", size=10.5, italic=True)
    save("a12f_jr20", g)


if __name__ == "__main__":
    fig_slice()
    fig_ex22()
    fig_ex23()
    fig_ex24()
    fig_q3()
    fig_q4()
    fig_q16()
    fig_pp_nsb20()
    fig_pp_bb20()
    fig_pp_st21()
    fig_a_jr20()
    print("figs_12f done")
