"""Figures for Lesson 6E (kept apart from figs.py, which the scaffold task owns; same pattern as int1/figs_4j.py).

Run: python3 workspace/build/int2/figs_6e.py   (writes svg/c6e_*.svg, svg/q6e_*.svg, svg/p6e_*.svg and svg/a6e_*.svg)
"""
import os
import sys
from math import exp, log, sqrt, e

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, ACC, INK, FAINT  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")


def save_raw(name, text):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(text)


def styled(g, width_mm):
    """Graph svg with an inline width (the answers stylesheet forces 88 mm on bare svgs)."""
    return g.svg().replace("<svg ", f'<svg style="width:{width_mm}mm;max-width:100%" ', 1)


def zero(x):
    return 0


def lab(g, x, y, base, sup=None, dx=0, dy=0, anchor="middle", size=11, color="ink", pre=""):
    """Label 'pre base^sup' at graph point (x, y), with a real superscript (no fraction stacking)."""
    X, Y = g.X(x) + dx, g.Y(y) + dy + size * 0.35
    s = f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{ACC[color]}" font-weight="500">'
    s += pre.replace("-", "−") + base.replace("-", "−")
    if sup:
        s += f'<tspan dy="{-size * 0.42:.1f}" font-size="{size * 0.72:.1f}">{sup.replace("-", chr(0x2212))}</tspan>'
    s += "</text>"
    g.items.append(s)
    return g


def save(name, g, width_mm=None):
    save_raw(name, styled(g, width_mm) if width_mm else g.svg())


# ---------------------------------------------------------------- lesson: worked examples
def ex17(name="c6e_ex17", k=1.0, kl="e", xr=(-3.2, 1.9), yr=(-3.3, 1.5), width=None):
    """y = e^x - e^k: the region between the curve, the x-axis and the y-axis (below the axis)."""
    c = exp(k)
    g = Graph(xr[0], xr[1], yr[0], yr[1], w=226, h=200, pad=(24, 28, 18, 12))
    g.fill(zero, lambda x: exp(x) - c, 0, k, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.hline(-c, x0=xr[0], x1=xr[1])
    g.curve(lambda x: exp(x) - c, color="ink", width=1.8, x0=xr[0], x1=log(c + yr[1] * 0.95))
    g.dot(k, 0, r=2.4).dot(0, 1 - c, r=2.4)
    g.label(k, 0, str(int(k)) if k != 1 else "1", dx=7, dy=12, size=11)
    if kl == "e":
        lab(g, 0, 1 - c, "1 - e", dx=-6, dy=-9, anchor="end")
        lab(g, 0, -c, "-e", dx=-6, dy=9, anchor="end")
    else:
        lab(g, 0, 1 - c, "1 - e", kl, dx=-6, dy=-9, anchor="end")
        lab(g, 0, -c, "-e", kl, dx=-6, dy=9, anchor="end")
    lab(g, xr[1], -c, "y = -e" if kl == "e" else "y = -e", None if kl == "e" else kl, dy=-9, anchor="end", size=10, color="faint")
    save(name, g, width)


def ex18(name="c6e_ex18", a=2, xr=(-2.6, 2.8), ymax=None, width=None, ylabels=None):
    """y = e^x and y = x^2 on [-a, a], the region between them shaded from x = 0 to x = a."""
    ymax = ymax or exp(a) * 1.08
    g = Graph(xr[0], xr[1], -0.06 * ymax, ymax, w=210, h=230, pad=(30, 40, 22, 22))
    g.fill(exp, lambda x: x * x, 0, a, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.curve(exp, color="ink", width=1.8, x0=xr[0], x1=log(ymax * 1.02))
    g.curve(lambda x: x * x, color="ink", width=1.4, x0=-sqrt(ymax * 1.02), x1=sqrt(ymax * 1.02))
    g.vline(a, 0, exp(a)).vline(-a, 0, a * a)
    g.hline(exp(a), x0=0, x1=a).hline(a * a, x0=-a, x1=a)
    g.xticks([(-a, str(-a)), (a, str(a))] + ([(1, "1")] if a == 2 else []))
    for yv, base, sup in (ylabels or []):
        g.hline(yv, x0=0, x1=log(yv)) if base == "e" and sup is None else None
        lab(g, 0, yv, base, sup, dx=-6, anchor="end", size=10.5)
    lab(g, log(ymax) - 0.05, ymax, "y = e", "x", dx=-8, dy=-2, anchor="end", size=10.5)
    lab(g, sqrt(ymax * 0.78), ymax * 0.78, "y = x", "2", dx=6, anchor="start", size=10.5)
    save(name, g, width)


def tip_y():
    """Pack tip: the region between y = log_e x, the y-axis and the lines y = 0 and y = 1 (x = e^y)."""
    g = Graph(-0.5, 3.6, -1.6, 1.6, w=218, h=150, pad=(18, 30, 16, 10))
    g.fill_y(exp, zero, 0, 1, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.curve(lambda x: log(x) if x > 0 else None, color="ink", width=1.8, x0=exp(-1.6), x1=3.6)
    g.hline(1, x0=0, x1=e)
    g.dot(e, 1, r=2.4).dot(1, 0, r=2.4)
    g.label(0, 1, "1", dx=-6, anchor="end", size=11)
    g.label(1, 0, "1", dx=6, dy=11, size=11)
    lab(g, e, 1, "(e, 1)", dx=-4, dy=-10, anchor="end", size=10.5)
    lab(g, 3.3, log(3.3), "y = log", None, dx=-2, dy=26, anchor="end", size=10.5)
    g.items.append(f'<text x="{g.X(3.3) - 2:.1f}" y="{g.Y(log(3.3)) + 26 + 3.7:.1f}" text-anchor="start" font-size="10.5" fill="{INK}">'
                   f'<tspan dy="3" font-size="7.6">e</tspan><tspan dy="-3"> x</tspan></text>')
    save("c6e_tipy", g)


# ---------------------------------------------------------------- Exercise 6E Q1: the grid
def q1_grid():
    x0, x1, y0, y1 = -5.0, 2.0, -0.3, 3.3
    u = 70  # pixels per unit
    pl, pr, pt, pb = 14, 22, 18, 10
    W, H = pl + pr + (x1 - x0) * u, pt + pb + (y1 - y0) * u

    def X(x):
        return pl + (x - x0) * u

    def Y(y):
        return pt + (y1 - y) * u

    it = []
    for i in range(int(round((x1 - x0) * 10)) + 1):
        xv = x0 + i / 10
        w_, col = (1.15, INK) if i % 10 == 0 else ((0.7, "#8a96a3") if i % 5 == 0 else (0.35, "#aab4bf"))
        it.append(f'<line x1="{X(xv):.1f}" y1="{Y(y0):.1f}" x2="{X(xv):.1f}" y2="{Y(y1):.1f}" stroke="{col}" stroke-width="{w_}"/>')
    for j in range(int(round((y1 - y0) * 10)) + 1):
        yv = y0 + j / 10
        k = int(round(yv * 10))
        w_, col = (1.15, INK) if k % 10 == 0 else ((0.7, "#8a96a3") if k % 5 == 0 else (0.35, "#aab4bf"))
        it.append(f'<line x1="{X(x0):.1f}" y1="{Y(yv):.1f}" x2="{X(x1):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="{w_}"/>')
    # axes
    it.append(f'<line x1="{X(x0) - 4:.1f}" y1="{Y(0):.1f}" x2="{X(x1) + 14:.1f}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.5"/>')
    it.append(f'<path d="M{X(x1) + 14:.1f},{Y(0):.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    it.append(f'<line x1="{X(0):.1f}" y1="{Y(y0):.1f}" x2="{X(0):.1f}" y2="{Y(y1) - 12:.1f}" stroke="{INK}" stroke-width="1.5"/>')
    it.append(f'<path d="M{X(0):.1f},{Y(y1) - 12:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    it.append(f'<text x="{X(x1) + 17:.1f}" y="{Y(0) + 4:.1f}" font-size="12" font-style="italic" fill="{INK}">x</text>')
    it.append(f'<text x="{X(0) - 6:.1f}" y="{Y(y1) - 8:.1f}" text-anchor="end" font-size="12" font-style="italic" fill="{INK}">y</text>')

    def tag(xp, yp, s, anchor="middle"):
        it.append(f'<rect x="{xp - 9:.1f}" y="{yp - 9:.1f}" width="18" height="13" fill="#fff"/>')
        it.append(f'<text x="{xp:.1f}" y="{yp + 1.5:.1f}" text-anchor="{anchor}" font-size="11" fill="{INK}">{s}</text>')

    for v in (-4, -3, -2, -1, 1):
        tag(X(v), Y(0) + 12, str(v).replace("-", "−"))
    tag(X(0) - 11, Y(0) + 12, "0")
    for v in (1, 2, 3):
        tag(X(0) - 12, Y(v) + 1, str(v))
    # the curve y = e^x, from x = -5 to the top of the grid, with an arrow
    xe = log(y1)
    pts = " ".join(f"{X(x0 + (xe - x0) * i / 400):.1f},{Y(exp(x0 + (xe - x0) * i / 400)):.1f}" for i in range(401))
    it.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    it.append(f'<path d="M{X(xe):.1f},{Y(y1):.1f} l-1.2,8 l-5,-2.6 z" fill="{INK}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" style="width:138mm;max-width:100%" viewBox="0 0 {W:.0f} {H:.0f}" '
           f'width="{W:.0f}" height="{H:.0f}" font-family="Inter, Arial, sans-serif">' + "".join(it) + "</svg>")
    save_raw("q6e_q1", svg)


# ---------------------------------------------------------------- Exercise 6E Q4, Q6, Q8-Q10
def small(xr, yr, w=190, h=150):
    g = Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=(22, 30, 18, 12))
    return g


def q4():
    g = small((-1.6, 2.6), (-0.25, 3.2))
    f = lambda x: exp(x / 2)  # noqa: E731
    g.fill(f, zero, -1, 2)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=-1.6, x1=2.25)
    g.vline(-1, 0, f(-1), color="ink", dash="").vline(2, 0, e, color="ink", dash="")
    g.hline(e, x0=0, x1=2).hline(f(-1), x0=-1, x1=0)
    g.xticks([(-1, "-1"), (2, "2")])
    g.label(0, e, "e", dx=-6, anchor="end", size=11, italic=True)
    g.label(0, 1, "1", dx=-6, dy=-7, anchor="end", size=11)
    lab(g, 0, f(-1), "e", "-1/2", dx=4, dy=8, anchor="start", size=10.5)
    save("q6e_q4a", g)
    g = small((-1.3, 2.0), (-0.25, 2.3))
    f = lambda x: exp(-x)  # noqa: E731
    g.fill(f, zero, 0, 1)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=-0.8, x1=2.0)
    g.vline(1, 0, f(1), color="ink", dash="").hline(f(1), x0=0, x1=1)
    g.xticks([(1, "1")])
    g.label(0, 1, "1", dx=6, dy=-7, anchor="start", size=11)
    lab(g, 0, f(1), "e", "-1", dx=-5, anchor="end", size=10.5)
    save("q6e_q4b", g)


def q6():
    # a: y = e^{-x}, x = 2, y = 1
    g = small((-1.3, 2.7), (-0.35, 2.4))
    f = lambda x: exp(-x)  # noqa: E731
    g.fill(lambda x: 1, f, 0, 2)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=-0.85, x1=2.7)
    g.hline(1, color="ink", dash="").vline(2, color="ink", dash="")
    g.xticks([(2, "2")])
    g.label(0, 1, "1", dx=-6, dy=-8, anchor="end", size=11)
    save("q6e_q6a", g)
    # b: y = e - e^x in the first quadrant
    g = small((-1.6, 1.6), (-0.9, 3.1))
    f = lambda x: e - exp(x)  # noqa: E731
    g.fill(f, zero, 0, 1)
    g.axes("x", "y")
    g.hline(e, x0=-1.6, x1=1.6)
    g.curve(f, color="ink", width=1.6, x0=-1.6, x1=1.25)
    g.xticks([(1, "1")])
    g.label(0, e, "e", dx=-6, dy=-7, anchor="end", size=11, italic=True)
    lab(g, 0, e - 1, "e - 1", dx=-5, dy=-2, anchor="end", size=10.5)
    save("q6e_q6b", g)
    # c: y = e^x - 1, x = -1
    g = small((-1.7, 1.4), (-1.3, 2.2))
    f = lambda x: exp(x) - 1  # noqa: E731
    g.fill(zero, f, -1, 0)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=-1.7, x1=1.15)
    g.vline(-1, color="ink", dash="")
    g.label(-1, 0, "-1", dx=-1, dy=-9, size=11)
    save("q6e_q6c", g)
    # d: y = e^{-x} - 2, x = 2, the axes
    g = small((-1.0, 2.7), (-2.5, 1.6))
    f = lambda x: exp(-x) - 2  # noqa: E731
    g.fill(zero, f, 0, 2)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=-0.9, x1=2.7)
    g.vline(2, color="ink", dash="")
    g.label(2, 0, "2", dx=-7, dy=-9, size=11)
    g.label(0, -1, "-1", dx=-6, dy=6, anchor="end", size=11)
    save("q6e_q6d", g)
    # e: y = e^{-x} - e and the coordinate axes
    g = small((-1.6, 1.8), (-3.2, 0.9))
    f = lambda x: exp(-x) - e  # noqa: E731
    g.fill(zero, f, -1, 0)
    g.axes("x", "y")
    g.hline(-e, x0=-1.6, x1=1.8)
    g.curve(f, color="ink", width=1.6, x0=-1.27, x1=1.8)
    g.label(-1, 0, "-1", dx=-7, dy=9, size=11)
    lab(g, 0, 1 - e, "-e + 1", dx=-5, anchor="end", size=10.5)
    lab(g, 0, -e, "-e", dx=-5, dy=7, anchor="end", size=10.5)
    save("q6e_q6e", g)
    # f: y = 3 - e^{-x}, x-axis, x = -1 and x = 2
    g = small((-1.5, 2.6), (-0.4, 3.5))
    f = lambda x: 3 - exp(-x)  # noqa: E731
    g.fill(f, zero, -1, 2)
    g.axes("x", "y")
    g.hline(3)
    g.curve(f, color="ink", width=1.6, x0=-1.25, x1=2.6)
    g.vline(-1, 0, f(-1), color="ink", dash="").vline(2, 0, f(2), color="ink", dash="")
    g.xticks([(-1, "-1"), (2, "2")])
    g.label(0, 3, "3", dx=-6, dy=-7, anchor="end", size=11)
    g.label(0, 2, "2", dx=-6, dy=-7, anchor="end", size=11)
    save("q6e_q6f", g)


def q8_10():
    # Q8: below both y = e^x and y = e^{-x}, -1 <= x <= 1
    g = small((-1.6, 1.6), (-0.25, 3.3), w=180, h=165)
    g.fill(lambda x: min(exp(x), exp(-x)), zero, -1, 1)
    g.axes("x", "y")
    g.curve(exp, color="ink", width=1.5, x0=-1.6, x1=log(3.3))
    g.curve(lambda x: exp(-x), color="ink", width=1.5, x0=-log(3.3), x1=1.6)
    g.vline(-1, 0, e).vline(1, 0, e).hline(e, x0=-1, x1=1)
    g.xticks([(-1, "-1"), (1, "1")])
    g.label(0, e, "e", dx=-6, dy=-7, anchor="end", size=11, italic=True)
    g.label(0, 1, "1", dx=-6, dy=-7, anchor="end", size=11)
    save("q6e_q8", g)
    # Q9: below both y = e - e^{-x} and y = e - e^x
    g = small((-1.6, 1.6), (-1.0, 3.3), w=180, h=165)
    g.fill(lambda x: min(e - exp(x), e - exp(-x)), zero, -1, 1)
    g.axes("x", "y")
    g.hline(e, x0=-1.6, x1=1.6)
    g.curve(lambda x: e - exp(x), color="ink", width=1.5, x0=-1.6, x1=1.2)
    g.curve(lambda x: e - exp(-x), color="ink", width=1.5, x0=-1.2, x1=1.6)
    g.xticks([(-1, "-1"), (1, "1")])
    g.label(0, e, "e", dx=-6, dy=-7, anchor="end", size=11, italic=True)
    lab(g, 0, e - 1, "e - 1", dx=-6, dy=-4, anchor="end", size=10.5)
    save("q6e_q9", g)
    # Q10: y = e^x - e^{-x}, x = -3 and x = 3 (not to scale, as in the textbook)
    g = small((-3.8, 3.8), (-22, 22), w=180, h=165)
    f = lambda x: exp(x) - exp(-x)  # noqa: E731
    g.fill(f, zero, 0, 3).fill(zero, f, -3, 0)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.5, x0=-3.12, x1=3.12)
    g.vline(-3, f(-3), 0, color="ink", dash="").vline(3, 0, f(3), color="ink", dash="")
    g.label(-3, 0, "-3", dy=-10, size=11).label(3, 0, "3", dy=12, size=11)
    save("q6e_q10", g)


# ---------------------------------------------------------------- past papers
def pp():
    # PLC 2023 Q13(d): y = log_e(x - 1), the x-axis and the line x = e + 1 (no scale marks, as printed)
    g = Graph(-1.2, 4.6, -2.6, 1.6, w=300, h=170, pad=(24, 104, 18, 12))
    f = lambda x: log(x - 1)  # noqa: E731
    g.fill(f, zero, 2, e + 1)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.7, x0=1 + exp(-2.6), x1=4.6)
    g.vline(e + 1, 0, 1, color="ink", dash="3 2")
    lab(g, 4.6, f(4.6), "y = log", None, dx=6, anchor="start", size=10.5)
    g.items.append(f'<text x="{g.X(4.6) + 6 + 40:.1f}" y="{g.Y(f(4.6)) + 3.7 + 3:.1f}" font-size="7.6" fill="{INK}">e</text>')
    g.items.append(f'<text x="{g.X(4.6) + 6 + 46:.1f}" y="{g.Y(f(4.6)) + 3.7:.1f}" font-size="10.5" fill="{INK}">(x − 1)</text>')
    save("p6e_plc", g)
    # Fort Street 2020 Q11(c): f(x) = e^{x/2} + 1 and the normal at x = 0 (no scale marks, as printed)
    g = Graph(-2.8, 3.2, -3.0, 5.0, w=230, h=210, pad=(18, 50, 18, 12))
    f = lambda x: exp(x / 2) + 1  # noqa: E731
    g.fill(f, lambda x: 2 - 2 * x, 0, 1, color="ink", opacity=0.3)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=-2.8, x1=2 * log(4))
    g.curve(lambda x: 2 - 2 * x, color="ink", width=1.4, x0=-1.4, x1=2.5)
    g.vline(1, 0, f(1), color="ink", dash="")
    g.label(0, 0, "O", dx=-8, dy=12, size=11, italic=True)
    lab(g, 2 * log(4), 4, "y = f(x)", dx=5, dy=8, anchor="start", size=10.5)
    save("p6e_fs", g)
    # Caringbah 2020 Q14(c): y = 1 + ln x on (0, 1] and its inverse y = e^{x - 1}
    g = Graph(-2.3, 1.35, -2.3, 1.35, w=226, h=220, pad=(16, 30, 18, 12))
    g.fill(lambda x: exp(x - 1), lambda x: max(0, 1 + log(x)) if x > 0 else 0, 0, 1, color="teal", opacity=0.3)
    g.axes("x", "y")
    g.curve(lambda x: exp(x - 1), color="ink", width=1.8, x0=-2.3, x1=1)
    g.curve(lambda x: 1 + log(x) if x > 0 else None, color="ink", width=1.8, x0=exp(-3.3), x1=1)
    g.xticks([(-2, "-2"), (-1, "-1"), (1, "1")])
    g.yticks([(-2, "-2"), (-1, "-1"), (1, "1")])
    save("p6e_car", g)
    # Saint Ignatius 2024 Q13(d): y = ln(2x/3) and the normal at x = 3e^2/2 (to scale)
    a = 1.5 * e * e
    xi = a + 4 / (3 * e * e)
    g = Graph(-0.8, 14.5, -2.2, 3.4, w=300, h=180, pad=(18, 40, 18, 12))
    g.fill_y(lambda y: a + (2 - y) * 2 / (3 * e * e), lambda y: 1.5 * exp(y), 0, 2, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.curve(lambda x: log(2 * x / 3) if x > 0 else None, color="ink", width=1.8, x0=1.5 * exp(-2.2), x1=14.5)
    m = -1.5 * e * e
    g.curve(lambda x: m * (x - a) + 2, color="ink", width=1.5, x0=a - 1.4 / -m * 1, x1=a + 4.2 / -m)
    g.label(0, 2, "2", dx=-6, anchor="end", size=11)
    g.hline(2, x0=0, x1=a)
    lab(g, 14.4, log(2 * 14.4 / 3), "y = f(x)", dx=-2, dy=-11, anchor="end", size=10.5)
    save("p6e_si", g)


# ---------------------------------------------------------------- answers: sketches
def answers():
    # C1 tutor demo and your turn: y = e^x - e^2 and y = e^x - e^3
    ex17("a6e_c1d", k=2.0, kl="2", xr=(-3.2, 2.9), yr=(-8.6, 3.5), width=52)
    ex17("a6e_c1y", k=3.0, kl="3", xr=(-3.2, 3.8), yr=(-22.5, 9.0), width=52)
    # C2 tutor demo: y = e^x and y = x^2 on [-3, 3]; your turn on [-1, 1]
    ex18("a6e_c2d", a=3, xr=(-3.6, 3.9), ymax=22.5, width=50,
         ylabels=[(exp(3), "e", "3"), (9, "9", None)])
    g = Graph(-1.5, 1.7, -0.15, 3.1, w=210, h=230, pad=(30, 40, 22, 22))
    g.fill(exp, lambda x: x * x, 0, 1, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.curve(exp, color="ink", width=1.8, x0=-1.5, x1=log(3.05))
    g.curve(lambda x: x * x, color="ink", width=1.4, x0=-1.5, x1=1.5)
    g.vline(1, 0, e).vline(-1, 0, 1).hline(e, x0=0, x1=1).hline(1, x0=-1, x1=1)
    g.xticks([(-1, "-1"), (1, "1")])
    lab(g, 0, e, "e", dx=-6, anchor="end", size=10.5)
    lab(g, 0, 1, "1", dx=-6, dy=-7, anchor="end", size=10.5)
    lab(g, log(3.05) - 0.03, 3.05, "y = e", "x", dx=-8, dy=-2, anchor="end", size=10.5)
    lab(g, 1.5, 2.25, "y = x", "2", dx=4, anchor="start", size=10.5)
    save("a6e_c2y", g, 50)
    # Q7a: e^x and x + 1; Q7b: e^x and 1 - x, from 0 to 1
    for name, h, hl in (("a6e_q7a", lambda x: x + 1, "y = x + 1"), ("a6e_q7b", lambda x: 1 - x, "y = 1 - x")):
        g = Graph(-1.3, 1.6, -0.6, 3.4, w=190, h=190, pad=(22, 46, 18, 12))
        g.fill(exp, h, 0, 1, color="blue", opacity=0.28)
        g.axes("x", "y")
        g.curve(exp, color="ink", width=1.7, x0=-1.3, x1=log(3.4))
        g.curve(h, color="ink", width=1.3)
        g.vline(1, 0, e).hline(e, x0=0, x1=1)
        g.xticks([(1, "1")])
        lab(g, 0, e, "e", dx=-6, anchor="end", size=10.5)
        lab(g, 0, 1, "1", dx=-6, dy=-7 if name.endswith("a") else 8, anchor="end", size=10.5)
        lab(g, log(3.3), 3.3, "y = e", "x", dx=-6, anchor="end", size=10)
        g.label(1.55, h(1.55), hl, dx=-2, dy=12, anchor="end", size=10)
        save(name, g, 44)
    # Q11b: y = x^2 and y = e^{x+1}, second quadrant
    g = Graph(-2.3, 1.5, -0.4, 3.3, w=190, h=190, pad=(22, 40, 18, 12))
    g.fill(lambda x: exp(x + 1), lambda x: x * x, -1, 0, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.curve(lambda x: exp(x + 1), color="ink", width=1.7, x0=-2.3, x1=log(3.3) - 1)
    g.curve(lambda x: x * x, color="ink", width=1.3, x0=-1.8, x1=1.8)
    g.vline(-1, 0, 1).hline(1, x0=-1, x1=0)
    g.xticks([(-1, "-1")])
    lab(g, 0, e, "e", dx=6, anchor="start", size=10.5)
    lab(g, 0, 1, "1", dx=6, dy=6, anchor="start", size=10.5)
    lab(g, log(3.3) - 1, 3.3, "y = e", "x+1", dx=-6, anchor="end", size=10)
    lab(g, 1.75, 3.06, "y = x", "2", dx=-3, dy=12, anchor="end", size=10)
    save("a6e_q11", g, 44)
    # Q12: y = e^x and y = x, from the y-axis to x = 2
    g = Graph(-1.4, 2.6, -1.2, 8.2, w=190, h=210, pad=(24, 40, 18, 12))
    g.fill(exp, lambda x: x, 0, 2, color="blue", opacity=0.28)
    g.axes("x", "y")
    g.curve(exp, color="ink", width=1.7, x0=-1.4, x1=log(8.2))
    g.curve(lambda x: x, color="ink", width=1.3, x0=-1.2, x1=2.6)
    g.vline(2, 0, exp(2)).hline(exp(2), x0=0, x1=2)
    g.xticks([(2, "2")])
    lab(g, 0, exp(2), "e", "2", dx=-6, anchor="end", size=10.5)
    lab(g, 0, 1, "1", dx=-6, dy=-6, anchor="end", size=10.5)
    lab(g, log(8.0), 8.0, "y = e", "x", dx=-6, anchor="end", size=10)
    g.label(2.55, 2.55, "y = x", dx=-2, dy=12, anchor="end", size=10)
    save("a6e_q12", g, 44)


if __name__ == "__main__":
    ex17()
    ex18(ylabels=[(exp(2), "e", "2"), (4, "4", None), (e, "e", None), (1, "1", None)])
    tip_y()
    q1_grid()
    q4()
    q6()
    q8_10()
    pp()
    answers()
