"""Figures for Lesson 6J (kept apart from figs.py, which the scaffold task owns; same pattern as figs_6e.py).

Run: python3 workspace/build/int2/figs_6j.py   (writes svg/c6j_*.svg, svg/q6j_*.svg and svg/a6j_*.svg)
"""
import os
import sys
from math import exp, log, sqrt, e

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, ACC, INK  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")


def save_raw(name, text):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(text)


def styled(g, width_mm):
    """Graph svg with an inline width (the answers stylesheet forces 88 mm on bare svgs)."""
    return g.svg().replace("<svg ", f'<svg style="width:{width_mm}mm;max-width:100%" ', 1)


def save(name, g, width_mm=None):
    save_raw(name, styled(g, width_mm) if width_mm else g.svg())


def zero(x):
    return 0


def lab(g, x, y, base, sup=None, dx=0, dy=0, anchor="middle", size=11, color="ink"):
    """Label 'base^sup' at graph point (x, y), with a real superscript; '-' is printed as a minus sign."""
    X, Y = g.X(x) + dx, g.Y(y) + dy + size * 0.35
    s = f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{ACC[color]}" font-weight="500">'
    s += base.replace("-", "−")
    if sup:
        s += f'<tspan dy="{-size * 0.42:.1f}" font-size="{size * 0.72:.1f}">{sup.replace("-", chr(0x2212))}</tspan>'
    s += "</text>"
    g.items.append(s)
    return g


def frac(g, x, y, num, den, dx=0, dy=0, size=10, pre="", anchor="middle"):
    """A small stacked fraction label (for 1/2, 3/2 and the like), with optional text before it."""
    X, Y = g.X(x) + dx, g.Y(y) + dy
    s = size * 0.78
    w = max(len(num), len(den)) * s * 0.62 + 2
    if pre:
        pw = len(pre) * size * 0.55
        g.items.append(f'<text x="{X - w / 2 - 2:.1f}" y="{Y + size * 0.35:.1f}" text-anchor="end" font-size="{size}" fill="{INK}" font-weight="500">{pre}</text>')
    g.items.append(f'<text x="{X:.1f}" y="{Y - 2:.1f}" text-anchor="middle" font-size="{s:.1f}" fill="{INK}">{num}</text>')
    g.items.append(f'<line x1="{X - w / 2:.1f}" y1="{Y:.1f}" x2="{X + w / 2:.1f}" y2="{Y:.1f}" stroke="{INK}" stroke-width="0.8"/>')
    g.items.append(f'<text x="{X:.1f}" y="{Y + s + 1:.1f}" text-anchor="middle" font-size="{s:.1f}" fill="{INK}">{den}</text>')
    return g


def eqlab(g, x, y, num, den, pre="y =", post="", size=10.5):
    """'y = num/den post' with a stacked fraction, starting at graph point (x, y)."""
    X, Y = g.X(x), g.Y(y)
    fs = size * 0.85
    g.items.append(f'<text x="{X:.1f}" y="{Y + size * 0.35:.1f}" font-size="{size}" font-style="italic" fill="{INK}">{pre}</text>')
    cx = X + len(pre) * size * 0.5 + 6
    w = max(len(num), len(den)) * fs * 0.6 + 3
    g.items.append(f'<text x="{cx:.1f}" y="{Y - 2:.1f}" text-anchor="middle" font-size="{fs:.1f}" fill="{INK}">{num}</text>')
    g.items.append(f'<line x1="{cx - w / 2:.1f}" y1="{Y + 1:.1f}" x2="{cx + w / 2:.1f}" y2="{Y + 1:.1f}" stroke="{INK}" stroke-width="0.8"/>')
    g.items.append(f'<text x="{cx:.1f}" y="{Y + fs + 2:.1f}" text-anchor="middle" font-size="{fs:.1f}" font-style="italic" fill="{INK}">{den}</text>')
    if post:
        g.items.append(f'<text x="{cx + w / 2 + 3:.1f}" y="{Y + size * 0.35:.1f}" font-size="{size}" fill="{INK}">{post.replace("-", chr(0x2212))}</text>')
    return g


def small(xr, yr, w=190, h=150):
    return Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=(22, 30, 18, 12))


# ---------------------------------------------------------------- lesson: hyperbola and line (Example 38 and its variants)
def hyp_line(name, k, s, width=None, labels=True):
    """xy = k and x + y = s (k = s - 1, meeting at x = 1 and x = k), the region between them shaded."""
    top = s + 0.6
    g = Graph(-0.35, top, -0.35, top, w=200, h=200, pad=(18, 30, 18, 14))
    g.fill(lambda x: s - x, lambda x: k / x, 1, k, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(lambda x: k / x if x > 0 else None, color="ink", width=1.7, x0=k / top, x1=top)
    g.curve(lambda x: s - x, color="ink", width=1.4, x0=-0.25, x1=s + 0.25)
    g.vline(1, 0, k).vline(k, 0, 1).hline(k, x0=0, x1=1).hline(1, x0=0, x1=k)
    g.xticks([(1, "1"), (k, str(k)), (s, str(s))])
    g.yticks([(1, "1"), (k, str(k)), (s, str(s))])
    if labels:
        g.label(k / (top - 0.15), top - 0.15, f"xy = {k}", dx=6, anchor="start", size=10.5, italic=True)
        g.label(s - 0.35, 0.35, f"x + y = {s}", dx=8, dy=-6, anchor="start", size=10.5, italic=True)
    save(name, g, width)


# ---------------------------------------------------------------- Exercise 6J Q1: the grid
def q1_grid():
    x0, x1, y0, y1 = -0.5, 3.0, -0.5, 2.1
    u = 110  # pixels per unit
    pl, pr, pt, pb = 14, 22, 18, 10
    W, H = pl + pr + (x1 - x0) * u, pt + pb + (y1 - y0) * u

    def X(x):
        return pl + (x - x0) * u

    def Y(y):
        return pt + (y1 - y) * u

    it = []
    for i in range(int(round((x1 - x0) * 10)) + 1):
        xv = x0 + i / 10
        k = int(round(xv * 10))
        w_, col = (1.15, INK) if k % 10 == 0 else ((0.7, "#8a96a3") if k % 5 == 0 else (0.35, "#aab4bf"))
        it.append(f'<line x1="{X(xv):.1f}" y1="{Y(y0):.1f}" x2="{X(xv):.1f}" y2="{Y(y1):.1f}" stroke="{col}" stroke-width="{w_}"/>')
    for j in range(int(round((y1 - y0) * 10)) + 1):
        yv = y0 + j / 10
        k = int(round(yv * 10))
        w_, col = (1.15, INK) if k % 10 == 0 else ((0.7, "#8a96a3") if k % 5 == 0 else (0.35, "#aab4bf"))
        it.append(f'<line x1="{X(x0):.1f}" y1="{Y(yv):.1f}" x2="{X(x1):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="{w_}"/>')
    it.append(f'<line x1="{X(x0) - 4:.1f}" y1="{Y(0):.1f}" x2="{X(x1) + 14:.1f}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.5"/>')
    it.append(f'<path d="M{X(x1) + 14:.1f},{Y(0):.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    it.append(f'<line x1="{X(0):.1f}" y1="{Y(y0):.1f}" x2="{X(0):.1f}" y2="{Y(y1) - 12:.1f}" stroke="{INK}" stroke-width="1.5"/>')
    it.append(f'<path d="M{X(0):.1f},{Y(y1) - 12:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    it.append(f'<text x="{X(x1) + 17:.1f}" y="{Y(0) + 4:.1f}" font-size="12" font-style="italic" fill="{INK}">x</text>')
    it.append(f'<text x="{X(0) - 6:.1f}" y="{Y(y1) - 8:.1f}" text-anchor="end" font-size="12" font-style="italic" fill="{INK}">y</text>')

    def tag(xp, yp, s):
        it.append(f'<rect x="{xp - 7:.1f}" y="{yp - 9:.1f}" width="14" height="13" fill="#fff"/>')
        it.append(f'<text x="{xp:.1f}" y="{yp + 1.5:.1f}" text-anchor="middle" font-size="11" fill="{INK}">{s}</text>')

    for v in (1, 2, 3):
        tag(X(v) - 8, Y(0) + 12, str(v))
    tag(X(0) - 9, Y(0) + 12, "0")
    for v in (1, 2):
        tag(X(0) - 9, Y(v) + 1, str(v))
    # the curve y = 1/x, from the top of the grid to x = 3, with arrows at both ends
    xs = 1 / y1
    pts = " ".join(f"{X(xs + (x1 - xs) * i / 400):.1f},{Y(1 / (xs + (x1 - xs) * i / 400)):.1f}" for i in range(401))
    it.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    it.append(f'<path d="M{X(xs):.1f},{Y(y1):.1f} l-2.6,7.6 l5.4,0.6 z" fill="{INK}"/>')
    it.append(f'<path d="M{X(x1):.1f},{Y(1 / x1):.1f} l-7.6,-2.6 l-0.4,5.4 z" fill="{INK}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" style="width:104mm;max-width:100%" viewBox="0 0 {W:.0f} {H:.0f}" '
           f'width="{W:.0f}" height="{H:.0f}" font-family="Inter, Arial, sans-serif">' + "".join(it) + "</svg>")
    save_raw("q6j_q1", svg)


# ---------------------------------------------------------------- Exercise 6J Q3, Q5-Q9, Q23
def q3():
    g = small((-0.6, 3.7), (-0.3, 3.2))
    f = lambda x: 1 / x  # noqa: E731
    g.fill(f, zero, 2, 3)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=1 / 3.2, x1=3.7)
    g.vline(2, 0, f(2), color="ink", dash="").vline(3, 0, f(3), color="ink", dash="")
    g.xticks([(2, "2"), (3, "3")])
    eqlab(g, 0.75, 2.2, "1", "x")
    save("q6j_q3a", g)
    g = small((-0.6, 3.7), (-0.3, 3.2))
    g.fill(f, zero, 0.5, 2)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=1 / 3.2, x1=3.7)
    g.vline(0.5, 0, 2, color="ink", dash="").vline(2, 0, 0.5, color="ink", dash="")
    g.xticks([(0.5, ""), (2, "2")])
    frac(g, 0.5, 0, "1", "2", dy=13)
    eqlab(g, 1.0, 1.9, "1", "x")
    save("q6j_q3b", g)


def q5():
    g = small((-0.6, 3.8), (-0.9, 3.5))
    f = lambda x: 3 - 3 / x  # noqa: E731
    g.fill(f, zero, 1, 3)
    g.axes("x", "y")
    g.hline(3, x0=-0.6, x1=3.8).hline(2, x0=0, x1=3)
    g.curve(f, color="ink", width=1.6, x0=3 / 3.85, x1=3.8)
    g.vline(3, 0, 2, color="ink", dash="")
    g.xticks([(1, "1"), (3, "3")])
    g.label(0, 3, "3", dx=-6, dy=-6, anchor="end", size=11).label(0, 2, "2", dx=-6, anchor="end", size=11)
    save("q6j_q5a", g)
    g = small((-0.6, 3.8), (-0.9, 2.6))
    f = lambda x: 2 - 1 / x  # noqa: E731
    g.fill(f, zero, 1, 3)
    g.axes("x", "y")
    g.hline(2, x0=-0.6, x1=3.8)
    g.curve(f, color="ink", width=1.6, x0=1 / 2.9, x1=3.8)
    g.vline(1, 0, 1, color="ink", dash="").vline(3, 0, f(3), color="ink", dash="")
    g.xticks([(1, "1"), (3, "3")])
    g.label(0, 2, "2", dx=-6, dy=-6, anchor="end", size=11)
    save("q6j_q5b", g)


def q6():
    g = small((-0.6, 4.8), (-0.9, 2.3), w=200)
    f = lambda x: 2 - 2 / x  # noqa: E731
    ln_ = lambda x: (x - 1) / 2  # noqa: E731
    g.fill(f, ln_, 1, 4)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=2 / 2.9, x1=4.8)
    g.curve(ln_, color="ink", width=1.3, x0=0.0, x1=4.8)
    g.vline(4, 0, 1.5).hline(1.5, x0=0, x1=4)
    g.xticks([(1, "1"), (4, "4")])
    frac(g, 0, 1.5, "3", "2", dx=-9)
    save("q6j_q6a", g)
    g = small((-0.6, 4.8), (-0.3, 2.9), w=200)
    f = lambda x: 2 / x  # noqa: E731
    ln_ = lambda x: (5 - x) / 2  # noqa: E731
    g.fill(ln_, f, 1, 4)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=2 / 2.9, x1=4.8)
    g.curve(ln_, color="ink", width=1.3, x0=0.4, x1=4.8)
    g.vline(1, 0, 2).vline(4, 0, 0.5)
    g.xticks([(1, "1"), (4, "4")])
    save("q6j_q6b", g)


def q7():
    g = small((-0.6, 3.6), (-1.2, 2.6))
    f = lambda x: 2 - 2 / x  # noqa: E731
    g.fill(lambda x: 2, f, 1, 2)
    g.axes("x", "y")
    g.hline(2, color="ink", dash="", width=1.3)
    g.curve(f, color="ink", width=1.6, x0=2 / 3.25, x1=3.6)
    g.vline(1, 0, 2, color="ink", dash="").vline(2, f(2), 2, color="ink", dash="").vline(2, 0, f(2))
    g.xticks([(1, "1"), (2, "2")])
    g.label(0, 2, "2", dx=-6, dy=-7, anchor="end", size=11)
    save("q6j_q7a", g)
    g = small((-2.7, 1.5), (-0.4, 2.4))
    f = lambda x: 1 / (x + 2)  # noqa: E731
    g.fill(lambda x: 1, f, -1, 0)
    g.axes("x", "y")
    g.vline(-2, -0.4, 2.4)
    g.curve(f, color="ink", width=1.6, x0=-2 + 1 / 2.4, x1=1.5)
    g.items.append(f'<line x1="{g.X(-1):.1f}" y1="{g.Y(1):.1f}" x2="{g.X(0):.1f}" y2="{g.Y(1):.1f}" stroke="{INK}" stroke-width="1.3"/>')
    g.xticks([(-2, "-2"), (-1, "-1")])
    g.label(0, 1, "1", dx=7, anchor="start", size=11)
    save("q6j_q7b", g)


def q8():
    g = small((-0.6, 4.8), (-3.3, 0.6), w=200)
    f = lambda x: -1 / x  # noqa: E731
    g.fill(zero, f, 1, 4)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=1 / 3.3, x1=4.8)
    g.vline(1, f(1), 0, color="ink", dash="").vline(4, f(4), 0, color="ink", dash="")
    g.xticks([(1, "1"), (4, "4")], below=False)
    save("q6j_q8a", g)
    g = small((-0.6, 3.8), (-3.6, 0.9), w=190, h=165)
    f = lambda x: 3 / x - 3  # noqa: E731
    g.fill(zero, f, 1, 3)
    g.axes("x", "y")
    g.hline(-3, x0=-0.6, x1=3.8).hline(-2, x0=0, x1=3)
    g.curve(f, color="ink", width=1.6, x0=3 / 3.9, x1=3.8)
    g.vline(3, f(3), 0, color="ink", dash="")
    g.xticks([(1, "1"), (3, "3")], below=False)
    g.label(0, -2, "-2", dx=-6, dy=6, anchor="end", size=11).label(0, -3, "-3", dx=-6, dy=6, anchor="end", size=11)
    save("q6j_q8b", g)


def q9():
    g = small((-0.6, 3.0), (-1.6, 2.6))
    f = lambda x: 1 / x - 1  # noqa: E731
    g.fill(f, zero, 0.5, 1).fill(zero, f, 1, 2)
    g.axes("x", "y")
    g.hline(-1, x0=-0.6, x1=3.0).hline(1, x0=0, x1=0.5)
    g.curve(f, color="ink", width=1.6, x0=1 / 3.6, x1=3.0)
    g.vline(0.5, 0, 1, color="ink", dash="").vline(2, f(2), 0, color="ink", dash="")
    g.xticks([(0.5, ""), (1, ""), (2, "2")], below=False)
    g.label(1, 0, "1", dx=4, dy=-12, size=11)
    frac(g, 0.5, 0, "1", "2", dy=10)
    g.label(0, 1, "1", dx=-6, anchor="end", size=11).label(0, -1, "-1", dx=-6, dy=7, anchor="end", size=11)
    save("q6j_q9a", g)
    g = small((-0.6, 3.8), (-1.6, 1.5))
    f = lambda x: 1 - 2 / x  # noqa: E731
    g.fill(zero, f, 1, 2).fill(f, zero, 2, 3)
    g.axes("x", "y")
    g.hline(1, x0=-0.6, x1=3.8)
    g.curve(f, color="ink", width=1.6, x0=2 / 2.6, x1=3.8)
    g.vline(1, f(1), 0, color="ink", dash="").vline(3, 0, f(3), color="ink", dash="")
    g.xticks([(1, ""), (2, "2"), (3, "3")])
    g.label(1, 0, "1", dy=-10, size=11)
    g.label(0, 1, "1", dx=-6, dy=-6, anchor="end", size=11)
    save("q6j_q9b", g)


def q23():
    r = 2.4  # where sqrt(x) is drawn
    g = Graph(-0.6, 3.4, -0.6, 2.6, w=210, h=150, pad=(24, 30, 18, 12))
    f = lambda t: 1 / t  # noqa: E731
    g.fill(f, zero, 1, r)
    g.axes("t", "y")
    g.curve(f, color="ink", width=1.6, x0=1 / 2.6, x1=3.4)
    g.hline(1, x0=0, x1=r).vline(r, 0, 1)
    g.vline(1, 0, 1, color="ink", dash="")
    g.xticks([(1, "1"), (r, "√x")])
    g.label(0, 1, "1", dx=-6, anchor="end", size=11)
    g.label(0, 0, "O", dx=-8, dy=12, size=11, italic=True)
    g.label(0, 1, "C", dx=8, dy=-9, size=11, italic=True)
    g.label(r, 1, "B", dx=4, dy=-9, size=11, italic=True)
    g.label(r, 0, "A", dx=9, dy=-7, anchor="start", size=11, italic=True)
    eqlab(g, 1.25, 2.1, "1", "t")
    save("q6j_q23", g)


# ---------------------------------------------------------------- answers: sketches
def demo1(name, k, b, xr, yr):
    """y = k/x - 1 shaded from x = k/2 ... (from x = b0 to x = b), split at the x-intercept x = k."""
    a = k / 2
    g = Graph(xr[0], xr[1], yr[0], yr[1], w=200, h=170, pad=(22, 30, 18, 12))
    f = lambda x: k / x - 1  # noqa: E731
    g.fill(f, zero, a, k).fill(zero, f, k, b)
    g.axes("x", "y")
    g.hline(-1, x0=xr[0], x1=xr[1])
    g.curve(f, color="ink", width=1.6, x0=k / (yr[1] + 1), x1=xr[1])
    g.vline(a, 0, f(a), color="ink", dash="").vline(b, f(b), 0, color="ink", dash="")
    g.xticks([(a, str(int(a))), (k, ""), (b, str(int(b)))])
    g.label(k, 0, str(k), dy=-10, size=11)
    lab(g, 0, -1, "-1", dx=-6, dy=7, anchor="end", size=10.5)
    lab(g, xr[1], -1, "y = -1", dy=9, anchor="end", size=10, color="faint")
    eqlab(g, k / 2.8 + 0.1, 1.8, str(k), "x", post="- 1", size=10)
    save(name, g, 50)


def answers():
    demo1("a6j_c1d", 2, 4, (-0.6, 4.7), (-1.6, 2.6))
    demo1("a6j_c1y", 4, 8, (-1.0, 9.2), (-1.6, 2.6))
    hyp_line("a6j_c2d", 3, 4, width=48)
    hyp_line("a6j_c2y", 4, 5, width=48)
    # Q10: y = 1, x = 8 and y = 4/x
    g = small((-0.8, 9.6), (-0.3, 2.3), w=200)
    f = lambda x: 4 / x  # noqa: E731
    g.fill(lambda x: 1, f, 4, 8)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=4 / 2.3, x1=9.6)
    g.items.append(f'<line x1="{g.X(4):.1f}" y1="{g.Y(1):.1f}" x2="{g.X(8):.1f}" y2="{g.Y(1):.1f}" stroke="{INK}" stroke-width="1.3"/>')
    g.vline(8, f(8), 1, color="ink", dash="").hline(1, x0=0, x1=4).vline(4, 0, 1).vline(8, 0, f(8))
    g.xticks([(4, "4"), (8, "8")])
    g.label(0, 1, "1", dx=-6, anchor="end", size=11)
    save("a6j_q10", g, 46)
    # Q13: the x-axis, y = x, y = 1/x and x = e
    g = small((-0.6, 3.4), (-0.6, 2.8), w=190, h=160)
    g.fill(lambda x: min(x, 1 / x), zero, 0.002, e)
    g.axes("x", "y")
    g.curve(lambda x: x, color="ink", width=1.3, x0=-0.5, x1=2.75)
    g.curve(lambda x: 1 / x, color="ink", width=1.6, x0=1 / 2.8, x1=3.4)
    g.vline(e, 0, 1 / e, color="ink", dash="").vline(1, 0, 1)
    g.xticks([(1, "1"), (e, "e")])
    g.label(0, 1, "1", dx=-6, anchor="end", size=11)
    save("a6j_q13", g, 44)
    # Q16: y = 6/x and y = x^2 - 6x + 11, meeting at x = 1, 2, 3
    g = small((-0.5, 4.2), (-0.5, 7.4), w=190, h=190)
    q = lambda x: x * x - 6 * x + 11  # noqa: E731
    h = lambda x: 6 / x  # noqa: E731
    g.fill(q, h, 1, 2).fill(h, q, 2, 3)
    g.axes("x", "y")
    g.curve(h, color="ink", width=1.6, x0=6 / 7.3, x1=4.2)
    g.curve(q, color="ink", width=1.3, x0=0.75, x1=4.0)
    for xv, yv in ((1, 6), (2, 3), (3, 2)):
        g.vline(xv, 0, yv).hline(yv, x0=0, x1=xv)
        g.label(0, yv, str(yv), dx=-6, anchor="end", size=11)
    g.xticks([(1, "1"), (2, "2"), (3, "3")])
    save("a6j_q16", g, 44)
    # Q18: y = 6e^{-x} and y = e^x - 1, the region between them and the y-axis
    g = small((-1.6, 2.2), (-1.4, 7.2), w=190, h=190)
    g.fill(lambda x: 6 * exp(-x), lambda x: exp(x) - 1, 0, log(3))
    g.axes("x", "y")
    g.hline(-1, x0=-1.6, x1=2.2)
    g.curve(lambda x: 6 * exp(-x), color="ink", width=1.6, x0=-log(7.2 / 6), x1=2.2)
    g.curve(lambda x: exp(x) - 1, color="ink", width=1.4, x0=-1.6, x1=log(8.2))
    g.vline(log(3), 0, 2).hline(2, x0=0, x1=log(3))
    g.xticks([(log(3), "ln 3")])
    g.label(0, 6, "6", dx=-6, anchor="end", size=11).label(0, 2, "2", dx=-6, anchor="end", size=11)
    lab(g, 0, -1, "-1", dx=-6, dy=7, anchor="end", size=10.5)
    save("a6j_q18", g, 44)


if __name__ == "__main__":
    hyp_line("c6j_ex38", 2, 3)
    q1_grid()
    q3()
    q5()
    q6()
    q7()
    q8()
    q9()
    q23()
    answers()
