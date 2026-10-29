"""Figures for Lesson 17B (kept apart from figs.py, which Task 1 owns; same pattern as figs_17a.py).

Run: python3 workspace/build/ch17/figs_17b.py   (writes svg/c17b_*.svg and svg/a17b_*.svg)
"""
import os
import sys
from fractions import Fraction as Fr
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Fig, save, _txt, ACC, INK  # noqa: E402

LINE = "#cdd4dd"


def pmf(n, p):
    p = Fr(p)
    return [float(comb(n, x) * p ** x * (1 - p) ** (n - x)) for x in range(n + 1)]


def _frame(n, ymax, yt, w, h, ylab, l=46, r=26, t=22, b=26, xstep=1, fs=10.5):
    """Axes in pixel space for x = 0..n (the y-axis sits half a unit left of x = 0)."""
    f = Fig(w, h)
    ux = (w - l - r) / (n + 1.0)

    def X(x):
        return l + (x + 0.5) * ux

    def Y(y):
        return t + (ymax - y) / ymax * (h - t - b)
    y0 = Y(0)
    f.line(l - 4, y0, w - r + 12, y0, width=1.3)
    f.raw(f'<path d="M{w - r + 12:.1f},{y0:.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    f.line(l, y0 + 4, l, t - 10, width=1.3)
    f.raw(f'<path d="M{l:.1f},{t - 10:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    f.text(w - r + 16, y0 + 4, "x", anchor="start", italic=True, size=fs + 1)
    f.raw(f'<text x="{l + 6:.1f}" y="{t - 6:.1f}" font-size="{fs}" fill="{INK}" font-style="italic">{ylab}</text>')
    for v in yt:
        f.line(l - 3, Y(v), l + 3, Y(v), width=1.1)
        f.raw(f'<text x="{l - 6:.1f}" y="{Y(v) + 3.6:.1f}" text-anchor="end" font-size="{fs}" fill="{INK}">{v:.2f}</text>')
    for x in range(0, n + 1, xstep):
        f.line(X(x), y0, X(x), y0 + 3, width=1.0)
        f.raw(f'<text x="{X(x):.1f}" y="{y0 + 14:.1f}" text-anchor="middle" font-size="{fs}" fill="{INK}">{x}</text>')
    return f, X, Y, ux


def dots(name, n, p, ymax, yt, w=330, h=128):
    """Dot graph of P(X = x) for B(n, p), as in the textbook's skewness graphs."""
    f, X, Y, _ = _frame(n, ymax, yt, w, h, "P(X = x)", fs=9.5)
    for x, v in enumerate(pmf(n, p)):
        f.dot(X(x), Y(v), r=2.4)
    save(name, f)


def histo(name, vals, ymax, yt, ylab, w=230, h=140, cap=None):
    """Histogram (columns 1 unit wide, centred on x) with the frequency polygon through the column tops."""
    n = len(vals) - 1
    f, X, Y, ux = _frame(n, ymax, yt, w, h, ylab, l=40, r=22, b=34 if cap else 24, fs=9.5)
    for x, v in enumerate(vals):
        if v > 0:
            f.raw(f'<rect x="{X(x) - ux / 2:.1f}" y="{Y(v):.1f}" width="{ux:.1f}" height="{Y(0) - Y(v):.1f}" '
                  f'fill="{ACC["blue"]}" fill-opacity="0.22" stroke="{INK}" stroke-width="0.9"/>')
    pts = [(X(-0.5), Y(0))] + [(X(x), Y(v)) for x, v in enumerate(vals)] + [(X(n + 0.5), Y(0))]
    f.poly(pts, color=None, stroke="ink", width=1.2, closed=False)
    if cap:
        f.text(w / 2, h - 6, cap, size=10, color="faint")
    save(name, f)


def polygon_grid(name, n, p, w=250, h=150):
    """Relative frequency polygon of B(n, p) on a light grid (Exercise 17B Q6)."""
    l, r, t, b = 44, 14, 12, 24
    ymax = 0.16
    f = Fig(w, h)

    def X(x):
        return l + x / n * (w - l - r)

    def Y(y):
        return t + (ymax - y) / ymax * (h - t - b)
    for gx in range(0, n + 1, 3):
        f.raw(f'<line x1="{X(gx):.1f}" y1="{Y(0):.1f}" x2="{X(gx):.1f}" y2="{Y(ymax):.1f}" stroke="{LINE}" stroke-width="0.6"/>')
    for k in range(0, 17):
        gy = k / 100
        f.raw(f'<line x1="{X(0):.1f}" y1="{Y(gy):.1f}" x2="{X(n):.1f}" y2="{Y(gy):.1f}" stroke="{LINE}" stroke-width="0.6"/>')
    f.line(X(0), Y(0), X(n) + 4, Y(0), width=1.3)
    f.line(X(0), Y(0) + 4, X(0), Y(ymax) - 4, width=1.3)
    for v, lab in ((0.05, "0.05"), (0.1, "0.1"), (0.15, "0.15")):
        f.line(X(0) - 3, Y(v), X(0), Y(v), width=1.1)
        f.raw(f'<text x="{X(0) - 6:.1f}" y="{Y(v) + 3.6:.1f}" text-anchor="end" font-size="10" fill="{INK}">{lab}</text>')
    for x in range(6, n + 1, 6):
        f.line(X(x), Y(0), X(x), Y(0) + 3, width=1.0)
        f.raw(f'<text x="{X(x):.1f}" y="{Y(0) + 14:.1f}" text-anchor="middle" font-size="10" fill="{INK}">{x}</text>')
    pts = [(X(x), Y(v)) for x, v in enumerate(pmf(n, p))]
    f.poly(pts, color=None, stroke="ink", width=1.5, closed=False)
    save(name, f)


def var_parabola(name, w=210, h=140):
    """sigma^2 = np(1 - p) against p, for 0 <= p <= 1 (Exercise 17B Q11 answer)."""
    l, r, t, b = 34, 30, 22, 32
    f = Fig(w, h)

    def X(p):
        return l + p * (w - l - r)

    def Y(s):
        return t + (0.3 - s) / 0.3 * (h - t - b)
    f.line(X(0) - 6, Y(0), X(1) + 18, Y(0), width=1.3)
    f.raw(f'<path d="M{X(1) + 18:.1f},{Y(0):.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    f.line(X(0), Y(0) + 6, X(0), Y(0.3) - 8, width=1.3)
    f.raw(f'<path d="M{X(0):.1f},{Y(0.3) - 8:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    f.text(X(1) + 22, Y(0) + 4, "p", anchor="start", italic=True)
    f.raw(f'<text x="{X(0) + 6:.1f}" y="{Y(0.3) - 4:.1f}" font-size="11" fill="{INK}" font-style="italic">σ²</text>')
    d = "M" + " L".join(f"{X(i / 100):.1f},{Y(i / 100 * (1 - i / 100)):.1f}" for i in range(101))
    f.path(d, color="blue", width=2)
    f.line(X(0.5), Y(0), X(0.5), Y(0.25), color="faint", width=1.1, dash="3 3")
    f.line(X(0), Y(0.25), X(0.5), Y(0.25), color="faint", width=1.1, dash="3 3")
    f.dot(X(0.5), Y(0.25), r=2.6)
    f.raw(_txt(X(0) - 9, Y(0.25), "n/4", anchor="end", size=10.5))
    f.raw(_txt(X(0.5), Y(0) + 16, "1/2", size=10.5))
    f.text(X(1), Y(0) + 13, "1", size=10.5)
    f.text(X(0) - 7, Y(0) + 11, "O", size=10.5, italic=True)
    save(name, f)


if __name__ == "__main__":
    # Concept 4: the three graphs in the text (20 coins; 20 dice with success 'six' and 'not six')
    dots("c17b_coin20", 20, Fr(1, 2), 0.20, (0.05, 0.10, 0.15, 0.20))
    dots("c17b_die20", 20, Fr(1, 6), 0.25, (0.05, 0.10, 0.15, 0.20, 0.25))
    dots("c17b_die20r", 20, Fr(5, 6), 0.25, (0.05, 0.10, 0.15, 0.20, 0.25))
    # Worked examples 9 and 10: theoretical distribution and the simulation (data from the text)
    yt = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
    histo("c17b_ex9a", pmf(10, Fr(1, 2)), 0.32, yt, "P(X = x)", cap="The theoretical distribution")
    histo("c17b_ex9b", [f / 100 for f in (0, 2, 6, 15, 20, 23, 17, 13, 1, 3, 0)], 0.32, yt, "fᵣ", cap="The simulation")
    histo("c17b_ex10a", pmf(10, Fr(1, 6)), 0.34, yt, "P(X = x)", cap="The theoretical distribution")
    histo("c17b_ex10b", [f / 100 for f in (11, 28, 31, 21, 9, 0, 0, 0, 0, 0, 0)], 0.34, yt, "fᵣ", cap="The simulation")
    # Concept 5 answers (C5): tutor demo 8 coins, your turn 8 dice with success 'five or six'
    yt2 = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
    histo("a17b_d_th", pmf(8, Fr(1, 2)), 0.32, yt2, "P(X = x)", w=200, h=132, cap="Theoretical")
    histo("a17b_d_sim", [f / 100 for f in (0, 4, 10, 22, 28, 20, 11, 4, 1)], 0.32, yt2, "fᵣ", w=200, h=132, cap="Simulation")
    histo("a17b_y_th", pmf(8, Fr(1, 3)), 0.32, yt2, "P(X = x)", w=200, h=132, cap="Theoretical")
    histo("a17b_y_sim", [f / 100 for f in (5, 15, 29, 26, 16, 7, 2, 0, 0)], 0.32, yt2, "fᵣ", w=200, h=132, cap="Simulation")
    # Exercise 17B Q6 (question) and Q6e (answer: p = 0.75), Q11a (answer)
    polygon_grid("c17b_q6", 48, Fr(1, 4))
    polygon_grid("a17b_q6e", 48, Fr(3, 4))
    var_parabola("a17b_q11")
