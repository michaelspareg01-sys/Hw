"""Figures for Lesson 5F (kept apart from figs.py, which the scaffold task owns; same pattern as figs_5a.py).

Run: python3 workspace/build/int1/figs_5f.py   (writes svg/c5f_*.svg and svg/q5f_*.svg)

Curves are drawn in ink and regions shaded blue, as in the textbook (Ext 1 Y12, PDF 254-262).
Where the textbook draws a schematic curve (Ex 5F Q1k, Q3d), the figure is schematic too.
"""
import os
import sys
from math import sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save, ACC  # noqa: E402
from plots import _txt  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from svg_overlap import check_string, text_extent, text_width  # noqa: E402

W, H, PAD = 136, 112, (12, 27, 16, 16)       # small exercise figure


def zero(_):
    return 0.0


def cbrt(v):
    return v ** (1 / 3) if v >= 0 else -((-v) ** (1 / 3))


def ycurve(g, fx, y0, y1, color="ink", width=1.4, n=300):
    """Draw x = fx(y) for y0 <= y <= y1."""
    pts = []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        pts.append(f"{g.X(fx(y)):.1f},{g.Y(y):.1f}")
    g.items.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ACC[color]}" '
                   f'stroke-width="{width}" stroke-linejoin="round"/>')


def seg(g, x0, y0, x1, y1, color="ink", width=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{d}/>')


def put(g, x, y, s, dx=0, dy=0, anchor="middle", size=11.5, italic=False, color="ink", radius=30):
    """Add a label at (x, y) + (dx, dy) px, moved to the nearest spot (within radius px) where
    workspace/tools/svg_overlap.py finds no new problem: no stroke through it, no other label on it and
    no clipping at the frame. If there is no such spot, the label is drawn at the preferred spot on a
    small white background."""
    base = set(check_string(g.svg()))
    offs = sorted(((ox, oy) for ox in range(-radius, radius + 1, 2) for oy in range(-radius, radius + 1, 2)
                   if ox * ox + oy * oy <= radius * radius), key=lambda o: (o[0] ** 2 + o[1] ** 2, abs(o[1])))
    n = len(g.items)
    for ox, oy in offs:
        g.label(x, y, s, dx=dx + ox, dy=dy + oy, anchor=anchor, size=size, italic=italic, color=color)
        if set(check_string(g.svg())) <= base:
            return
        del g.items[n:]
    # white-backed label at the preferred spot
    w = text_width(s.replace("-", "−"), size)
    up, down = text_extent(s.replace("-", "−"), size)
    sx, sy = g.X(x) + dx, g.Y(y) + dy + size * 0.35
    x0 = {"start": sx, "middle": sx - w / 2, "end": sx - w}[anchor]
    g.items.append(f'<rect x="{x0 - 1.5:.1f}" y="{sy - up - 1.5:.1f}" width="{w + 3:.1f}" '
                   f'height="{up + down + 3:.1f}" fill="#fff" rx="1.5"/>')
    g.label(x, y, s, dx=dx, dy=dy, anchor=anchor, size=size, italic=italic, color=color)


def xlab(g, v, s, below=True, dx=0):
    """Number on the x-axis (no tick), moved clear of the curves if needed."""
    put(g, v, 0, s, dx=dx, dy=12 if below else -10, size=10.5, radius=10)


def ylab(g, v, s, left=True, dy=0):
    """Number on the y-axis (no tick), moved clear of the curves if needed."""
    put(g, 0, v, s, dx=-6 if left else 6, dy=dy, anchor="end" if left else "start", size=10.5, radius=10)


# ---------------------------------------------------------------- lesson figures
def lesson():
    # Example 22: y = 4 - x^2
    f = lambda x: 4 - x * x  # noqa: E731
    g = Graph(-2.7, 2.7, -2.2, 4.9, w=170, h=150, pad=(12, 26, 16, 14))
    g.fill(f, zero, -2, 2, opacity=0.28)
    g.axes()
    g.curve(f, color="ink", width=1.4, x0=-2.55, x1=2.55)
    xlab(g, -2, "-2", dx=-7), xlab(g, 2, "2", dx=6)
    ylab(g, 4, "4", dy=-7)
    put(g, 0.35, 4.3, "y = 4 - x²", anchor="start", size=10.5, italic=True)
    save("c5f_e22", g)

    # Example 23: y = x^2 - 1
    f = lambda x: x * x - 1  # noqa: E731
    g = Graph(-2.0, 3.0, -1.6, 2.8, w=170, h=140, pad=(12, 26, 16, 14))
    g.fill(zero, f, -1, 1, opacity=0.28)
    g.axes()
    g.curve(f, color="ink", width=1.4, x0=-1.9, x1=1.9)
    xlab(g, -1, "-1", below=False, dx=-8), xlab(g, 1, "1", below=False, dx=7)
    ylab(g, -1, "-1", dy=8)
    put(g, 1.6, 1.0, "y = x² - 1", anchor="start", size=10.5, italic=True)
    save("c5f_e23", g)

    # Example 24: y = x(x + 1)(x - 2)
    f = lambda x: x * (x + 1) * (x - 2)  # noqa: E731
    g = Graph(-1.6, 2.7, -2.7, 3.6, w=170, h=150, pad=(12, 26, 16, 14))
    g.fill(f, zero, -1, 0, opacity=0.28)
    g.fill(zero, f, 0, 2, opacity=0.28)
    g.axes()
    g.curve(f, color="ink", width=1.4, x0=-1.38, x1=2.48)
    xlab(g, -1, "-1", below=False, dx=-9), xlab(g, 2, "2", below=False, dx=8)
    save("c5f_e24", g)

    # Example 25: y = x^3 - x
    f = lambda x: x ** 3 - x  # noqa: E731
    g = Graph(-1.6, 1.6, -1.4, 1.6, w=170, h=140, pad=(12, 26, 16, 14))
    g.fill(f, zero, -1, 0, opacity=0.28)
    g.fill(zero, f, 0, 1, opacity=0.28)
    g.axes()
    g.curve(f, color="ink", width=1.4, x0=-1.4, x1=1.4)
    xlab(g, -1, "-1", below=False, dx=-9), xlab(g, 1, "1", dx=6)
    save("c5f_e25", g)

    # Example 26: y = x + 1 and y = 5, region to the right of the y-axis
    g = Graph(-1.3, 6.0, -1.0, 6.6, w=170, h=150, pad=(12, 26, 16, 14))
    g.fill_y(lambda y: y - 1, zero, 1, 5, opacity=0.28)
    g.axes()
    g.curve(lambda x: x + 1, color="ink", width=1.4, x0=-1.2, x1=5.4)
    seg(g, -1.2, 5, 5.9, 5, width=1.4)
    ylab(g, 5, "5", dy=-7), ylab(g, 1, "1", dy=-6)
    put(g, 5.4, 6.4, "y = x + 1", anchor="end", size=10.5, italic=True, dx=-6)
    put(g, 5.9, 5, "y = 5", anchor="end", size=10.5, italic=True, dy=10)
    save("c5f_e26", g)

    # Example 27: y = x^3, regions to the right (0 <= y <= 8) and left (-1 <= y <= 0) of the y-axis
    g = Graph(-1.6, 2.6, -2.4, 9.0, w=170, h=165, pad=(12, 26, 16, 14))
    g.fill_y(cbrt, zero, 0, 8, opacity=0.28)
    g.fill_y(zero, cbrt, -1, 0, opacity=0.28)
    g.axes()
    g.curve(lambda x: x ** 3, color="ink", width=1.4, x0=-1.32, x1=2.07)
    seg(g, 0, 8, 2, 8), seg(g, -1, -1, 0, -1)
    ylab(g, 8, "8", dy=-6), ylab(g, -1, "-1", left=False, dy=4)
    put(g, 1.0, 6.4, "y = x³", anchor="end", size=10.5, italic=True)
    save("c5f_e27", g)


# ---------------------------------------------------------------- exercise figures
def small(xr, yr, h=H, w=W):
    return Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=PAD)


def q1():
    # a  y = 2x on [0, 2]
    f = lambda x: 2 * x  # noqa: E731
    g = small((-1.2, 3.4), (-2.3, 6.4))
    g.fill(f, zero, 0, 2)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-1.1, x1=3.1)
    seg(g, 2, 0, 2, 4)
    xlab(g, 2, "2")
    put(g, 2.25, 4.3, "y = 2x", anchor="start", size=10, italic=True)
    save("q5f_1a", g)

    # b  y = 3x^2 on [1, 3]
    f = lambda x: 3 * x * x  # noqa: E731
    g = small((-2.6, 4.4), (-4, 40))
    g.fill(f, zero, 1, 3)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-2.4, x1=3.6)
    seg(g, 3, 0, 3, 27)
    xlab(g, 1, "1"), xlab(g, 3, "3")
    put(g, 3.4, 33, "y = 3x²", anchor="end", size=10, italic=True, dx=-6)
    save("q5f_1b", g)

    # c  y = 4x^3 on [0, 3]
    f = lambda x: 4 * x ** 3  # noqa: E731
    g = small((-3.6, 4.4), (-140, 140))
    g.fill(f, zero, 0, 3)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-3.25, x1=3.25)
    seg(g, 3, 0, 3, 108)
    xlab(g, 3, "3", dx=4)
    put(g, 0.3, -80, "y = 4x³", anchor="start", size=10, italic=True)
    save("q5f_1c", g)

    # d  y = 3x^2 + 1 on [-1, 2]
    f = lambda x: 3 * x * x + 1  # noqa: E731
    g = small((-2.6, 2.6), (-1.5, 15.5))
    g.fill(f, zero, -1, 2)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-1.85, x1=2.2)
    seg(g, -1, 0, -1, 4), seg(g, 2, 0, 2, 13)
    xlab(g, -1, "-1"), xlab(g, 2, "2")
    ylab(g, 1, "1", dy=-6)
    put(g, -0.3, 14.2, "y = 3x² + 1", anchor="end", size=9.5, italic=True)
    save("q5f_1d", g)

    # e  y = x^2 on [0, 3]
    f = lambda x: x * x  # noqa: E731
    g = small((-3.4, 4.0), (-1.4, 12))
    g.fill(f, zero, 0, 3)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-3.3, x1=3.3)
    seg(g, 3, 0, 3, 9)
    xlab(g, 3, "3")
    put(g, 0.25, 10.4, "y = x²", anchor="start", size=10, italic=True)
    save("q5f_1e", g)

    # f  y = x^2 - 2x on [2, 4]
    f = lambda x: x * x - 2 * x  # noqa: E731
    g = small((-1.6, 5.2), (-2.2, 10))
    g.fill(f, zero, 2, 4)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-1.5, x1=4.3)
    seg(g, 4, 0, 4, 8)
    xlab(g, 2, "2"), xlab(g, 4, "4")
    put(g, 0.2, 9.2, "y = x² - 2x", anchor="start", size=9.5, italic=True)
    save("q5f_1f", g)

    # g  y = sqrt(x) on [0, 16]
    g = small((-2, 21), (-1.3, 6))
    g.fill(sqrt, zero, 0, 16)
    g.axes()
    g.curve(sqrt, color="ink", width=1.3, x0=0, x1=20)
    seg(g, 16, 0, 16, 4)
    g.dot(0, 0, r=2.4)
    xlab(g, 16, "16")
    put(g, 11.5, 5.4, "y = √x", anchor="middle", size=10, italic=True)
    save("q5f_1g", g)

    # h  y = 5 - x on [1, 3]
    f = lambda x: 5 - x  # noqa: E731
    g = small((-1.0, 6.4), (-1.4, 6.6))
    g.fill(f, zero, 1, 3)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-0.6, x1=6.0)
    seg(g, 1, 0, 1, 4), seg(g, 3, 0, 3, 2)
    xlab(g, 1, "1"), xlab(g, 3, "3"), xlab(g, 5, "5", dx=-3)
    ylab(g, 5, "5", dy=-5)
    put(g, 1.9, 4.6, "y = 5 - x", anchor="start", size=10, italic=True)
    save("q5f_1h", g)

    # i  y = x^3 - x, shaded on [-1, 0]
    f = lambda x: x ** 3 - x  # noqa: E731
    g = small((-1.7, 1.8), (-1.6, 1.6))
    g.fill(f, zero, -1, 0)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-1.45, x1=1.45)
    xlab(g, -1, "-1", below=False, dx=-8)
    put(g, 0.15, -0.95, "y = x³ - x", anchor="start", size=10, italic=True)
    save("q5f_1i", g)

    # j  y = 12 - x - x^2 on [-4, 3]
    f = lambda x: 12 - x - x * x  # noqa: E731
    g = small((-5.2, 4.4), (-4.5, 16))
    g.fill(f, zero, -4, 3)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-4.6, x1=3.6)
    xlab(g, -4, "-4", dx=6), xlab(g, 3, "3", dx=-6)
    put(g, -4.9, 14.6, "y = 12 - x - x²", anchor="start", size=10, italic=True)
    save("q5f_1j", g)

    # k  y = 5x^4 + 1 on [-1, 2]  (schematic, as in the book)
    d = lambda x: 1 + 0.9 * x * x  # noqa: E731
    g = small((-2.6, 3.0), (-0.6, 5.8))
    g.fill(d, zero, -1, 2)
    g.axes()
    g.curve(d, color="ink", width=1.3, x0=-2.0, x1=2.3)
    seg(g, -1, 0, -1, d(-1)), seg(g, 2, 0, 2, d(2))
    xlab(g, -1, "-1"), xlab(g, 2, "2")
    ylab(g, 1, "1", dy=-7)
    put(g, -0.2, 5.4, "y = 5x⁴ + 1", anchor="end", size=9.5, italic=True)
    save("q5f_1k", g)

    # l  y = cube root of x on [1, 27]
    g = small((-8, 32), (-3.6, 4.2))
    g.fill(cbrt, zero, 1, 27)
    g.axes()
    g.curve(cbrt, color="ink", width=1.3, x0=-30, x1=31)
    seg(g, 1, 0, 1, 1), seg(g, 27, 0, 27, 3)
    xlab(g, 1, "1"), xlab(g, 27, "27")
    put(g, 6, 3.9, "y = ∛x", anchor="start", size=10, italic=True)
    save("q5f_1l", g)


def q2():
    # a  x = 2y, 0 <= y <= 5
    g = small((-3, 13), (-1.6, 7))
    g.fill_y(lambda y: 2 * y, zero, 0, 5)
    g.axes()
    ycurve(g, lambda y: 2 * y, -1.3, 6.3, width=1.3)
    seg(g, 0, 5, 10, 5)
    ylab(g, 5, "5")
    put(g, 10, 3.4, "x = 2y", anchor="middle", size=10, italic=True)
    save("q5f_2a", g)

    # b  x = 3y^2, -2 <= y <= 0
    g = small((-2.5, 16), (-2.8, 2.8))
    g.fill_y(lambda y: 3 * y * y, zero, -2, 0)
    g.axes()
    ycurve(g, lambda y: 3 * y * y, -2.25, 2.25, width=1.3)
    seg(g, 0, -2, 12, -2)
    ylab(g, -2, "-2")
    put(g, 8.6, 2.3, "x = 3y²", anchor="middle", size=10, italic=True)
    save("q5f_2b", g)

    # c  x = 2y - 4, 2 <= y <= 4
    g = small((-3, 8), (-1.0, 6.4))
    g.fill_y(lambda y: 2 * y - 4, zero, 2, 4)
    g.axes()
    ycurve(g, lambda y: 2 * y - 4, 0.6, 5.6, width=1.3)
    seg(g, 0, 4, 4, 4)
    ylab(g, 4, "4"), ylab(g, 2, "2", dy=-7)
    put(g, 5.6, 2.6, "x = 2y - 4", anchor="middle", size=10, italic=True)
    save("q5f_2c", g)

    # d  x = 27 - 3y^2, -3 <= y <= 3
    g = small((-8, 36), (-5.4, 4.4))
    g.fill_y(lambda y: 27 - 3 * y * y, zero, -3, 3)
    g.axes()
    ycurve(g, lambda y: 27 - 3 * y * y, -3.7, 3.7, width=1.3)
    ylab(g, 3, "3", left=False, dy=-7), ylab(g, -3, "-3", dy=7)
    xlab(g, 27, "27", below=False, dx=6)
    put(g, 20, -4.6, "x = 27 - 3y²", anchor="middle", size=10, italic=True)
    save("q5f_2d", g)

    # e  x = y, 0 <= y <= 3
    g = small((-1.6, 4.4), (-1.6, 4.2))
    g.fill_y(lambda y: y, zero, 0, 3)
    g.axes()
    ycurve(g, lambda y: y, -1.4, 4.0, width=1.3)
    seg(g, 0, 3, 3, 3)
    ylab(g, 3, "3")
    put(g, 2.5, 1.2, "x = y", anchor="start", size=10, italic=True)
    save("q5f_2e", g)

    # f  x = y^2 + 1, 3 <= y <= 5
    g = small((-3, 30), (-6.4, 6.4))
    g.fill_y(lambda y: y * y + 1, zero, 3, 5)
    g.axes()
    ycurve(g, lambda y: y * y + 1, -5.0, 5.0, width=1.3)
    seg(g, 0, 3, 10, 3), seg(g, 0, 5, 26, 5)
    ylab(g, 5, "5", dy=-3), ylab(g, 3, "3", dy=3)
    put(g, 1.0, -6.0, "x = y² + 1", anchor="start", size=10, italic=True)
    save("q5f_2f", g)

    # g  x = sqrt(y), 0 <= y <= 9
    g = small((-1.0, 4.6), (-1.6, 11.5))
    g.fill_y(sqrt, zero, 0, 9)
    g.axes()
    ycurve(g, sqrt, 0, 11.0, width=1.3)
    seg(g, 0, 9, 3, 9)
    g.dot(0, 0, r=2.4)
    ylab(g, 9, "9")
    put(g, 3.1, 4.0, "x = √y", anchor="start", size=10, italic=True)
    save("q5f_2g", g)

    # h  x = 1/sqrt(y), 1 <= y <= 4
    fx = lambda y: 1 / sqrt(y)  # noqa: E731
    g = small((-0.5, 4.2), (-1.0, 5.0))
    g.fill_y(fx, zero, 1, 4)
    g.axes()
    ycurve(g, fx, 0.06, 4.8, width=1.3)
    seg(g, 0, 1, 1, 1)
    ylab(g, 4, "4"), ylab(g, 1, "1")
    put(g, 1.55, 2.6, "x =", anchor="start", size=10, italic=True)
    put(g, 2.95, 2.6, "1/√y", anchor="middle", size=10, italic=True)
    save("q5f_2h", g)


def q3():
    # a  y = x^2 - 4x + 3, region below the x-axis on [1, 3]
    f = lambda x: x * x - 4 * x + 3  # noqa: E731
    g = small((-0.6, 4.4), (-1.6, 4.6))
    g.fill(zero, f, 1, 3)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-0.3, x1=3.7)
    xlab(g, 1, "1", dx=-6), xlab(g, 3, "3", dx=6)
    ylab(g, 3, "3")
    put(g, 0.35, 3.9, "y = x² - 4x + 3", anchor="start", size=10, italic=True)
    save("q5f_3a", g)

    # b  y = 3x, region below the x-axis on [-3, 0]
    f = lambda x: 3 * x  # noqa: E731
    g = small((-4.2, 4.2), (-11, 11))
    g.fill(zero, f, -3, 0)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-3.6, x1=3.6)
    seg(g, -3, 0, -3, -9)
    xlab(g, -3, "-3", below=False)
    put(g, 1.8, 2.6, "y = 3x", anchor="start", size=10, italic=True)
    save("q5f_3b", g)

    # c  y = x^3, region below the x-axis on [-3, 0]
    f = lambda x: x ** 3  # noqa: E731
    g = small((-4.0, 4.0), (-30, 30))
    g.fill(zero, f, -3, 0)
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-3.15, x1=3.15)
    xlab(g, -3, "-3", below=False)
    put(g, 2.5, 24, "y = x³", anchor="end", size=10, italic=True)
    save("q5f_3c", g)

    # d  y = 1 - x^4, region below the x-axis on [1, 3]  (schematic, as in the book)
    d = lambda x: 1 - x * x  # noqa: E731
    g = small((-2.6, 4.0), (-9.2, 2.6), h=124)
    g.fill(zero, d, 1, 3)
    g.axes()
    g.curve(d, color="ink", width=1.3, x0=-3.2, x1=3.15)
    seg(g, 3, 0, 3, -8)
    xlab(g, 1, "1", below=False, dx=7), xlab(g, 3, "3", below=False)
    ylab(g, 1, "1", dy=-8)
    put(g, -2.4, -8.6, "y = 1 - x⁴", anchor="start", size=10, italic=True)
    save("q5f_3d", g)


def q4():
    # a  x = 1 - y, 1 <= y <= 4
    g = small((-4.6, 2.4), (-1.6, 5.4))
    g.fill_y(zero, lambda y: 1 - y, 1, 4)
    g.axes()
    ycurve(g, lambda y: 1 - y, -1.2, 5.2, width=1.3)
    seg(g, -3, 4, 0, 4)
    ylab(g, 4, "4", left=False), ylab(g, 1, "1", left=False, dy=-7)
    put(g, -2.0, 2.0, "x = 1 - y", anchor="end", size=10, italic=True)
    save("q5f_4a", g)

    # b  x = y^2 - 6y + 8, 2 <= y <= 4 (left of the y-axis)
    fx = lambda y: y * y - 6 * y + 8  # noqa: E731
    g = small((-2.2, 10), (-1.0, 5.4))
    g.fill_y(zero, fx, 2, 4)
    g.axes()
    ycurve(g, fx, -0.3, 5.0, width=1.3)
    ylab(g, 4, "4", dy=-7), ylab(g, 2, "2", dy=7)
    xlab(g, 8, "8")
    put(g, 0.8, 3.0, "x = y² - 6y + 8", anchor="start", size=10, italic=True)
    save("q5f_4b", g)

    # c  x = cube root of y, -8 <= y <= -1 (left of the y-axis)
    g = small((-2.8, 2.6), (-10.5, 9.5))
    g.fill_y(zero, cbrt, -8, -1)
    g.axes()
    ycurve(g, cbrt, -10, 9.4, width=1.3)
    seg(g, -2, -8, 0, -8), seg(g, -1, -1, 0, -1)
    ylab(g, -1, "-1", left=False, dy=5), ylab(g, -8, "-8", left=False)
    put(g, -0.3, 6.0, "x = ∛y", anchor="end", size=10, italic=True)
    save("q5f_4c", g)

    # d  x = -y^2, 0 <= y <= 3 (left of the y-axis)
    fx = lambda y: -y * y  # noqa: E731
    g = small((-12.5, 2.6), (-4.2, 4.4))
    g.fill_y(zero, fx, 0, 3)
    g.axes()
    ycurve(g, fx, -3.4, 3.4, width=1.3)
    seg(g, -9, 3, 0, 3)
    ylab(g, 3, "3", left=False)
    put(g, -7.0, -1.3, "x = -y²", anchor="middle", size=10, italic=True)
    save("q5f_4d", g)


def q567():
    # Q5: y = x + 1 with dashed lines at x = -3 and x = 2
    f = lambda x: x + 1  # noqa: E731
    g = Graph(-4.0, 3.2, -3.4, 4.4, w=170, h=150, pad=(12, 26, 16, 14))
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-4.0, x1=3.1)
    g.vline(-3, -2, 0, color="faint", dash="4 3").vline(2, 0, 3, color="faint", dash="4 3")
    xlab(g, -3, "-3", below=False), xlab(g, -1, "-1", below=False, dx=-4), xlab(g, 2, "2")
    save("q5f_5", g)

    # Q6: y = (x - 1)(x + 3) with a dashed line at x = 2
    f = lambda x: (x - 1) * (x + 3)  # noqa: E731
    g = Graph(-4.4, 2.8, -4.8, 8.0, w=170, h=150, pad=(12, 26, 16, 14))
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-4.3, x1=2.45)
    g.vline(2, 0, 5, color="faint", dash="4 3")
    xlab(g, -3, "-3", dx=-7), xlab(g, 1, "1", dx=-5), xlab(g, 2, "2", dx=4)
    save("q5f_6", g)

    # Q7: y = x(x + 1)(x - 2)
    f = lambda x: x * (x + 1) * (x - 2)  # noqa: E731
    g = Graph(-1.6, 2.7, -2.7, 3.6, w=170, h=150, pad=(12, 26, 16, 14))
    g.axes()
    g.curve(f, color="ink", width=1.3, x0=-1.38, x1=2.48)
    xlab(g, -1, "-1", below=False, dx=-9), xlab(g, 2, "2", below=False, dx=8)
    save("q5f_7", g)

    # Q12: y^2 = 16(2 - x), shaded in the first quadrant
    fx = lambda y: 2 - y * y / 16  # noqa: E731
    g = Graph(-1.0, 3.0, -7.4, 7.4, w=160, h=150, pad=(12, 26, 16, 14))
    g.fill_y(fx, zero, 0, sqrt(32))
    g.axes()
    ycurve(g, fx, -7.0, 7.0, width=1.3)
    save("q5f_12", g)


if __name__ == "__main__":
    lesson()
    q1()
    q2()
    q3()
    q4()
    q567()
