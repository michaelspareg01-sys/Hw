"""Figures for Lesson 17D and the Chapter 17 review (kept apart from figs.py, which Task 1 owns; same pattern as
figs_17a.py, figs_17b.py and figs_17c.py).

Run: python3 workspace/build/ch17/figs_17d.py   (writes svg/c17d_*.svg and svg/a17d_*.svg)
"""
import os
import sys
from fractions import Fraction as Fr
from math import comb, erf, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Fig, save, ACC, INK  # noqa: E402

LINE = "#cdd4dd"


def pmf(n, p):
    p = Fr(p)
    return [comb(n, x) * p ** x * (1 - p) ** (n - x) for x in range(n + 1)]


def cum(vals):
    out, s = [], 0
    for v in vals:
        s += v
        out.append(s)
    return out


def Phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def _axes(f, l, r, t, b, w, h, xlab, ylab, fs):
    y0 = h - b
    f.line(l - 4, y0, w - r + 10, y0, width=1.2)
    f.raw(f'<path d="M{w - r + 10:.1f},{y0:.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    f.line(l, y0 + 4, l, t - 8, width=1.2)
    f.raw(f'<path d="M{l:.1f},{t - 8:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    f.text(w - r + 14, y0 + 4, xlab, anchor="start", italic=True, size=fs + 1)
    f.raw(f'<text x="{l + 6:.1f}" y="{t - 2:.1f}" font-size="{fs}" fill="{INK}" font-style="italic">{ylab}</text>')


def polygon(name, n, p, ymax, yt, phat=False, w=230, h=150, fs=9.5, labs=None):
    """Frequency polygon of B(n, p) (phat=False) or of the sample proportion p-hat = X/n (phat=True).
    The p-hat graph is the same polygon with the x-axis labelled 0, 1/n, ..., n/n."""
    l, r, t, b = 42, 26, 16, 34 if phat else 22
    f = Fig(w, h)
    ux = (w - l - r) / (n + 0.6)

    def X(x):
        return l + x * ux

    def Y(y):
        return t + (ymax - y) / ymax * (h - t - b)
    _axes(f, l, r, t, b, w, h, "p̂" if phat else "x", "P(p̂)" if phat else "P(X = x)", fs)
    for v in yt:
        f.line(l - 3, Y(v), l + 3, Y(v), width=1.0)
        f.raw(f'<text x="{l - 6:.1f}" y="{Y(v) + 3.4:.1f}" text-anchor="end" font-size="{fs}" fill="{INK}">{v:.2f}</text>')
    for x in range(1, n + 1):
        f.line(X(x), Y(0), X(x), Y(0) + 3, width=0.9)
        lab = (labs[x] if labs else f"{x}/{n}") if phat else str(x)
        f.text(X(x), Y(0) + (15 if phat and "/" in lab else 13), lab, size=fs)
    vals = [float(v) for v in pmf(n, p)]
    f.poly([(X(x), Y(v)) for x, v in enumerate(vals)], color=None, stroke="ink", width=1.1, closed=False)
    for x, v in enumerate(vals):
        f.dot(X(x), Y(v), r=2.1)
    save(name, f)


def _marker(f, kind, x, y, col):
    c = ACC[col]
    if kind == "x":
        f.raw(f'<path d="M{x - 3:.1f},{y - 3:.1f} L{x + 3:.1f},{y + 3:.1f} M{x - 3:.1f},{y + 3:.1f} L{x + 3:.1f},{y - 3:.1f}" stroke="{c}" stroke-width="1.3"/>')
    elif kind == "o":
        f.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="white" stroke="{c}" stroke-width="1.2"/>')
    else:
        f.raw(f'<path d="M{x:.1f},{y - 3.6:.1f} L{x + 3.3:.1f},{y + 2.4:.1f} L{x - 3.3:.1f},{y + 2.4:.1f} z" fill="{c}"/>')


def cumulative(name, n, series, labels, w=330, h=190, fs=9.5, legend_xy=None):
    """Cumulative graphs against p-hat = 0, 1/n, ..., 1: each series is (values, marker, colour), joined by lines.
    labels are the x-axis labels at k/n."""
    l, r, t, b = 42, 26, 16, 26
    f = Fig(w, h)

    def X(v):
        return l + v * (w - l - r) / 1.06

    def Y(y):
        return t + (1.08 - y) / 1.08 * (h - t - b)
    for k in range(1, 11):
        f.raw(f'<line x1="{X(0):.1f}" y1="{Y(k / 10):.1f}" x2="{X(1.02):.1f}" y2="{Y(k / 10):.1f}" stroke="{LINE}" stroke-width="0.5"/>')
    _axes(f, l, r, t, b, w, h, "p̂", "", fs)
    for k in range(1, 11):
        f.line(l - 3, Y(k / 10), l + 3, Y(k / 10), width=1.0)
        f.raw(f'<text x="{l - 6:.1f}" y="{Y(k / 10) + 3.4:.1f}" text-anchor="end" font-size="{fs}" fill="{INK}">{k / 10:.2f}</text>')
    for k, lab in enumerate(labels):
        if k == 0:
            continue
        f.line(X(k / n), Y(0), X(k / n), Y(0) + 3, width=0.9)
        f.text(X(k / n), Y(0) + 13, lab, size=fs)
    for vals, kind, col in series:
        f.poly([(X(k / n), Y(v)) for k, v in enumerate(vals)], color=None, stroke=col, width=1.0, closed=False)
        for k, v in enumerate(vals):
            _marker(f, kind, X(k / n), Y(v), col)
    lx, ly = legend_xy or (X(0.66), Y(0.52))
    for i, (txt, kind, col) in enumerate((("experiment", "x", "rose"), ("binomial", "o", "blue"), ("normal", "t", "ink"))):
        _marker(f, kind, lx, ly + 13 * i - 3, col)
        f.text(lx + 8, ly + 13 * i + 0.5, txt, anchor="start", size=fs)
    save(name, f)


def q11_figure(name, w=470, h=170):
    """Exercise 17D Q11: cumulative histogram of p-hat = X/20, X ~ B(20, 0.6), with the normal CDF N(0.6, 0.012),
    a circle round the left tail near 0.4, and an enlarged view of that region."""
    n, p = 20, Fr(3, 5)
    cdf = [float(v) for v in cum(pmf(n, p))]
    sd = sqrt(0.6 * 0.4 / 20)
    f = Fig(w, h)
    # left panel
    l, t, pw, ph = 34, 14, 200, 120

    def X(v):
        return l + v * pw / 1.05

    def Y(y):
        return t + (1.08 - y) / 1.08 * ph
    for k in range(1, 6):
        f.raw(f'<line x1="{X(0):.1f}" y1="{Y(k / 5):.1f}" x2="{X(1.03):.1f}" y2="{Y(k / 5):.1f}" stroke="{LINE}" stroke-width="0.6"/>')
    for k in range(1, 11):
        f.raw(f'<line x1="{X(k / 10):.1f}" y1="{Y(0):.1f}" x2="{X(k / 10):.1f}" y2="{Y(1.0):.1f}" stroke="{LINE}" stroke-width="0.5"/>')
    for k, v in enumerate(cdf):
        if v < 0.0005:
            continue
        x0, x1 = X(k / 20 - 0.025), X(k / 20 + 0.025)
        f.raw(f'<rect x="{x0:.1f}" y="{Y(v):.1f}" width="{x1 - x0:.1f}" height="{Y(0) - Y(v):.1f}" fill="{ACC["teal"]}" fill-opacity="0.55" stroke="{INK}" stroke-width="0.5"/>')
    steps = 240
    d = "M" + " L".join(f"{X(1.02 * i / steps):.1f},{Y(Phi((1.02 * i / steps - 0.6) / sd)):.1f}" for i in range(steps + 1))
    f.path(d, color="rose", width=1.5)
    f.line(X(0) - 4, Y(0), X(1.03) + 6, Y(0), width=1.2)
    f.line(X(0), Y(0) + 3, X(0), Y(1.08), width=1.2)
    for k in range(1, 6):
        f.raw(f'<text x="{X(0) - 5:.1f}" y="{Y(k / 5) + 3.4:.1f}" text-anchor="end" font-size="9.5" fill="{INK}">{k / 5:g}</text>')
    for k in (2, 4, 6, 8):
        f.raw(f'<text x="{X(k / 10):.1f}" y="{Y(0) + 13:.1f}" text-anchor="middle" font-size="9.5" fill="{INK}">{k / 10:g}</text>')
    f.text(X(1.03) + 10, Y(0) + 4, "p̂", anchor="start", italic=True, size=10.5)
    cx, cy = X(0.355), Y(0.03)
    f.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="none" stroke="{INK}" stroke-width="0.9"/>')
    # right panel: enlarged view of 0.28 <= p-hat <= 0.47, 0 <= y <= 0.17
    L, T, W, H = 280, 22, 175, 112
    a0, a1, ytop = 0.28, 0.465, 0.17

    def XX(v):
        return L + (v - a0) / (a1 - a0) * W

    def YY(y):
        return T + (ytop - y) / ytop * H
    f.raw(f'<line x1="{XX(0.4):.1f}" y1="{YY(0):.1f}" x2="{XX(0.4):.1f}" y2="{YY(ytop):.1f}" stroke="{LINE}" stroke-width="0.8"/>')
    f.raw(f'<line x1="{XX(a0):.1f}" y1="{YY(0.1):.1f}" x2="{XX(a1):.1f}" y2="{YY(0.1):.1f}" stroke="{LINE}" stroke-width="0.8"/>')
    for k, v in enumerate(cdf):
        lo, hi = k / 20 - 0.025, k / 20 + 0.025
        if hi <= a0 or lo >= a1 or v < 0.0005:
            continue
        lo, hi = max(lo, a0), min(hi, a1)
        top = min(v, ytop)
        f.raw(f'<rect x="{XX(lo):.1f}" y="{YY(top):.1f}" width="{XX(hi) - XX(lo):.1f}" height="{YY(0) - YY(top):.1f}" fill="{ACC["teal"]}" fill-opacity="0.55" stroke="{INK}" stroke-width="0.6"/>')
    pts = [(XX(k / 20 + 0.025), YY(v)) for k, v in enumerate(cdf) if a0 <= k / 20 + 0.025 <= a1 and v <= ytop]
    f.poly(pts, color=None, stroke="blue", width=1.1, closed=False)
    steps = 120
    vals = [(a0 + (a1 - a0) * i / steps, Phi((a0 + (a1 - a0) * i / steps - 0.6) / sd)) for i in range(steps + 1)]
    f.path("M" + " L".join(f"{XX(x):.1f},{YY(y):.1f}" for x, y in vals if y <= ytop), color="rose", width=1.5)
    f.line(XX(a0), YY(0), XX(a1), YY(0), width=1.1)
    f.raw(f'<text x="{XX(0.4):.1f}" y="{YY(0) + 13:.1f}" text-anchor="middle" font-size="9.5" fill="{INK}">0.4</text>')
    f.raw(f'<path d="M{cx + 12:.1f},{cy + 19:.1f} C{cx + 60:.1f},{cy + 50:.1f} {L - 60:.1f},{cy + 40:.1f} {L - 6:.1f},{YY(0) + 8:.1f}" fill="none" stroke="{INK}" stroke-width="0.9"/>')
    f.raw(f'<path d="M{L - 4:.1f},{YY(0) + 7:.1f} l-8,-1 l4,6 z" fill="{INK}"/>')
    save(name, f)


def dotplot(name, counts, w=260, h=96):
    """Dot plot of p-hat = 0, 0.2, ..., 1 with the given frequencies (Exercise 17D Q6d answer)."""
    l, r = 24, 20
    f = Fig(w, h)
    y0 = h - 24

    def X(v):
        return l + v * (w - l - r)
    f.line(X(0) - 6, y0, X(1) + 8, y0, width=1.2)
    for k in range(6):
        v = k / 5
        f.line(X(v), y0, X(v), y0 + 4, width=1.0)
        f.text(X(v), y0 + 15, f"{v:g}", size=9.5)
        for j in range(counts[k]):
            f.raw(f'<circle cx="{X(v):.1f}" cy="{y0 - 8 - 10 * j:.1f}" r="4" fill="white" stroke="{INK}" stroke-width="1.1"/>')
    f.text(X(1) + 12, y0 + 4, "p̂", anchor="start", italic=True, size=10.5)
    save(name, f)


def sim_series(n, freqs, p, half):
    """Cumulative relative frequencies of simulated data, cumulative binomial probabilities, and the normal CDF with
    the continuity correction half = 1/(2n), all at p-hat = k/n."""
    runs = sum(freqs)
    cf = [Fr(v, runs) for v in cum(freqs)]
    cb = cum(pmf(n, p))
    sd = sqrt(float(p) * (1 - float(p)) / n)
    cn = [Phi((k / n + half - float(p)) / sd) for k in range(n + 1)]
    return [float(v) for v in cf], [float(v) for v in cb], cn


if __name__ == "__main__":
    # Worked example 15 (a coin tossed six times)
    yt = (0.10, 0.20, 0.30, 0.40)
    polygon("c17d_ex15a", 6, Fr(1, 2), 0.42, yt)
    polygon("c17d_ex15b", 6, Fr(1, 2), 0.42, yt, phat=True)
    # Worked example 19 (10 coins, the 100 simulations of Worked example 9 in Lesson 17B)
    freq19 = [0, 2, 6, 15, 20, 23, 17, 13, 1, 3, 0]
    a, bb, _ = sim_series(10, freq19, Fr(1, 2), 0.05)
    zs = [-2.85, -2.21, -1.581, -0.949, -0.316, 0.316, 0.949, 1.581, 2.21, 2.85, 3.48]   # the printed z-scores
    cumulative("c17d_ex19", 10, [(a, "x", "rose"), (bb, "o", "blue"), ([Phi(z) for z in zs], "t", "ink")],
               [f"{k / 10:g}" for k in range(11)])
    # Exercise 17D Q11
    q11_figure("c17d_q11")
    # Answers: C1 tutor demo (spinner, n = 3, p = 1/3) and your turn (coin, n = 4)
    polygon("a17d_c1x", 3, Fr(1, 3), 0.50, (0.10, 0.20, 0.30, 0.40, 0.50), w=170, h=120)
    polygon("a17d_c1p", 3, Fr(1, 3), 0.50, (0.10, 0.20, 0.30, 0.40, 0.50), phat=True, w=170, h=130)
    polygon("a17d_y1x", 4, Fr(1, 2), 0.42, yt, w=170, h=120)
    polygon("a17d_y1p", 4, Fr(1, 2), 0.42, yt, phat=True, w=170, h=130)
    # Answers: C4 tutor demo (8 coins, 17B demo data) and your turn (8 dice, 5 or 6, 17B your-turn data)
    eighths = ["0", "1/8", "2/8", "3/8", "4/8", "5/8", "6/8", "7/8", "1"]
    a, bb, c = sim_series(8, [0, 4, 10, 22, 28, 20, 11, 4, 1], Fr(1, 2), 1 / 16)
    cumulative("a17d_c4", 8, [(a, "x", "rose"), (bb, "o", "blue"), (c, "t", "ink")], eighths, w=300, h=180)
    a, bb, c = sim_series(8, [5, 15, 29, 26, 16, 7, 2, 0, 0], Fr(1, 3), 1 / 16)
    cumulative("a17d_y4", 8, [(a, "x", "rose"), (bb, "o", "blue"), (c, "t", "ink")], eighths, w=300, h=180)
    # Answers: Exercise 17D Q6d
    dotplot("a17d_q6d", [1, 2, 3, 4, 0, 0])
