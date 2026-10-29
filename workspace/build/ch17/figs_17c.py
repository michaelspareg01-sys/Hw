"""Figures for Lesson 17C (kept apart from figs.py, which Task 1 owns; same pattern as figs_17a.py and figs_17b.py).

Run: python3 workspace/build/ch17/figs_17c.py   (writes svg/c17c_*.svg and svg/a17c_*.svg)
"""
import os
import sys
from fractions import Fraction as Fr
from math import comb, exp, pi, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Fig, save, ACC, INK  # noqa: E402

LINE = "#cdd4dd"


def pmf(n, p):
    p = Fr(p)
    return [float(comb(n, x) * p ** x * (1 - p) ** (n - x)) for x in range(n + 1)]


def npdf(x, mu, var):
    return exp(-(x - mu) ** 2 / (2 * var)) / sqrt(2 * pi * var)


def _frame(n, ymax, yt, w, h, l=44, r=24, t=14, b=24, xstep=1, fs=9.5, x0=0, ylab=None):
    """Axes for x = x0..n in pixel space; the y-axis sits half a unit left of x0."""
    f = Fig(w, h)
    ux = (w - l - r) / (n - x0 + 1.0)

    def X(x):
        return l + (x - x0 + 0.5) * ux

    def Y(y):
        return t + (ymax - y) / ymax * (h - t - b)
    y0 = Y(0)
    f.line(l - 4, y0, w - r + 10, y0, width=1.2)
    f.raw(f'<path d="M{w - r + 10:.1f},{y0:.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    f.line(l, y0 + 4, l, t - 8, width=1.2)
    f.raw(f'<path d="M{l:.1f},{t - 8:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    f.text(w - r + 14, y0 + 4, "x", anchor="start", italic=True, size=fs + 1)
    if ylab:
        f.raw(f'<text x="{l + 6:.1f}" y="{t - 2:.1f}" font-size="{fs}" fill="{INK}" font-style="italic">{ylab}</text>')
    for v in yt:
        f.line(l - 3, Y(v), l + 3, Y(v), width=1.0)
        f.raw(f'<text x="{l - 6:.1f}" y="{Y(v) + 3.4:.1f}" text-anchor="end" font-size="{fs}" fill="{INK}">{v:.2f}</text>')
    for x in range(x0, n + 1, xstep):
        f.line(X(x), y0, X(x), y0 + 3, width=0.9)
        f.raw(f'<text x="{X(x):.1f}" y="{y0 + 13:.1f}" text-anchor="middle" font-size="{fs}" fill="{INK}">{x}</text>')
    return f, X, Y, ux


def approx(name, n, p, ymax, yt, shade=None, w=300, h=130, xstep=1, fs=9.5):
    """Frequency polygon of B(n, p) (dots joined) with the normal curve N(np, npq); optional shading [a, b] under the curve."""
    mu, var = n * float(p), n * float(p) * (1 - float(p))
    f, X, Y, ux = _frame(n, ymax, yt, w, h, xstep=xstep, fs=fs)
    xa, xb = -0.5, n + 0.5
    if shade:
        a, b = shade
        steps = 80
        pts = [(X(a), Y(0))] + [(X(a + (b - a) * i / steps), Y(npdf(a + (b - a) * i / steps, mu, var))) for i in range(steps + 1)] + [(X(b), Y(0))]
        f.poly(pts, color="blue", opacity=0.28, stroke="ink", width=0.9)
    steps = 300
    d = "M" + " L".join(f"{X(xa + (xb - xa) * i / steps):.1f},{Y(min(npdf(xa + (xb - xa) * i / steps, mu, var), ymax * 1.02)):.1f}" for i in range(steps + 1))
    f.path(d, color="blue", width=1.4)
    vals = pmf(n, p)
    f.poly([(X(x), Y(v)) for x, v in enumerate(vals)], color=None, stroke="ink", width=1.1, closed=False)
    for x, v in enumerate(vals):
        f.dot(X(x), Y(v), r=1.9)
    save(name, f)


def q3_histogram(name, n=20, p=0.6, w=250, h=170):
    """Exercise 17C Q3f: histogram of B(20, 0.6) on a light grid with the normal curve N(12, 4.8) overlaid."""
    l, r, t, b = 40, 10, 10, 34
    ymax = 0.22
    mu, var = n * p, n * p * (1 - p)
    f = Fig(w, h)

    def X(x):
        return l + (x + 0.5) / (n + 1.5) * (w - l - r)

    def Y(y):
        return t + (ymax - y) / ymax * (h - t - b)
    for gx in range(0, n + 2):
        f.raw(f'<line x1="{X(gx - 0.5):.1f}" y1="{Y(0):.1f}" x2="{X(gx - 0.5):.1f}" y2="{Y(ymax):.1f}" stroke="{LINE}" stroke-width="0.6"/>')
    for k in range(0, 23):
        gy = k / 100
        f.raw(f'<line x1="{X(-0.5):.1f}" y1="{Y(gy):.1f}" x2="{X(n + 0.5):.1f}" y2="{Y(gy):.1f}" stroke="{LINE}" stroke-width="0.4"/>')
    vals = pmf(n, p)
    for x, v in enumerate(vals):
        if v > 0.0015:
            f.raw(f'<rect x="{X(x - 0.5):.1f}" y="{Y(v):.1f}" width="{X(x + 0.5) - X(x - 0.5):.1f}" height="{Y(0) - Y(v):.1f}" '
                  f'fill="{ACC["amber"]}" fill-opacity="0.55" stroke="{INK}" stroke-width="0.6"/>')
    steps = 300
    d = "M" + " L".join(f"{X(-0.5 + (n + 1) * i / steps):.1f},{Y(npdf(-0.5 + (n + 1) * i / steps, mu, var)):.1f}" for i in range(steps + 1))
    f.path(d, color="ink", width=1.1)
    for x, v in enumerate(vals):
        cx, cy = X(x), Y(v)
        f.raw(f'<path d="M{cx - 2.4:.1f},{cy - 2.4:.1f} L{cx + 2.4:.1f},{cy + 2.4:.1f} M{cx - 2.4:.1f},{cy + 2.4:.1f} L{cx + 2.4:.1f},{cy - 2.4:.1f}" stroke="{ACC["blue"]}" stroke-width="1"/>')
    f.line(X(-0.5), Y(0), X(n + 0.5) + 4, Y(0), width=1.2)
    f.line(X(-0.5), Y(0) + 3, X(-0.5), Y(ymax), width=1.0)
    for v, lab in ((0.05, "0.05"), (0.1, "0.1"), (0.15, "0.15"), (0.2, "0.2")):
        f.raw(f'<text x="{X(-0.5) - 5:.1f}" y="{Y(v) + 3.4:.1f}" text-anchor="end" font-size="9.5" fill="{ACC["rose"]}">{lab}</text>')
    for x in range(2, n + 1, 2):
        f.raw(f'<text x="{X(x):.1f}" y="{Y(0) + 13:.1f}" text-anchor="middle" font-size="9.5" fill="{ACC["rose"]}">{x}</text>')
    f.raw(f'<text x="{X(n) :.1f}" y="{Y(0) + 26:.1f}" text-anchor="middle" font-size="9.5" fill="{ACC["rose"]}" font-style="italic">pink</text>')
    save(name, f)


def oc_curves(name, curves, w=230, h=150):
    """Operating characteristic curves: P(reject) against p, for p = 0, 0.05, 0.1, ..., 0.4 (Exercise 17C Q12 answers)."""
    l, r, t, b = 40, 26, 18, 26
    f = Fig(w, h)

    def X(p):
        return l + p / 0.5 * (w - l - r)

    def Y(y):
        return t + (1.1 - y) / 1.1 * (h - t - b)
    for k in range(1, 6):
        f.raw(f'<line x1="{X(k / 10):.1f}" y1="{Y(0):.1f}" x2="{X(k / 10):.1f}" y2="{Y(1.1):.1f}" stroke="{LINE}" stroke-width="0.6"/>')
    for k in range(1, 6):
        f.raw(f'<line x1="{X(0):.1f}" y1="{Y(k / 5):.1f}" x2="{X(0.5):.1f}" y2="{Y(k / 5):.1f}" stroke="{LINE}" stroke-width="0.6"/>')
    f.line(X(0) - 4, Y(0), X(0.5) + 14, Y(0), width=1.2)
    f.raw(f'<path d="M{X(0.5) + 14:.1f},{Y(0):.1f} l-7,-3.5 v7 z" fill="{INK}"/>')
    f.line(X(0), Y(0) + 4, X(0), Y(1.1) - 6, width=1.2)
    f.raw(f'<path d="M{X(0):.1f},{Y(1.1) - 6:.1f} l-3.5,7 h7 z" fill="{INK}"/>')
    f.text(X(0.5) + 18, Y(0) + 4, "p", anchor="start", italic=True, size=10.5)
    f.raw(f'<text x="{X(0) + 6:.1f}" y="{Y(1.1) - 2:.1f}" font-size="10" fill="{INK}" font-style="italic">P(reject)</text>')
    for k in range(1, 6):
        f.raw(f'<text x="{X(0) - 5:.1f}" y="{Y(k / 5) + 3.4:.1f}" text-anchor="end" font-size="9.5" fill="{INK}">{k / 5:.1f}</text>')
        f.raw(f'<text x="{X(k / 10):.1f}" y="{Y(0) + 13:.1f}" text-anchor="middle" font-size="9.5" fill="{INK}">{k / 10:.1f}</text>')
    for pts, col, lab in curves:
        f.poly([(X(p), Y(v)) for p, v in pts], color=None, stroke=col, width=1.4, closed=False)
        for p, v in pts:
            f.dot(X(p), Y(v), r=2.3, color=col)
        p, v = pts[-1]
        f.raw(f'<text x="{X(p) + 6:.1f}" y="{Y(v) + (11 if lab == "b" else -5):.1f}" font-size="10" fill="{ACC[col]}" font-weight="600">{lab}</text>')
    save(name, f)


def oc_points(k, m):
    """P(reject) for samples of k punnets, rejecting when at least m are bad."""
    out = []
    for p in (Fr(0), Fr(5, 100), Fr(1, 10), Fr(2, 10), Fr(3, 10), Fr(4, 10)):
        acc = sum(comb(k, x) * p ** x * (1 - p) ** (k - x) for x in range(m))
        out.append((float(p), float(1 - acc)))
    return out


if __name__ == "__main__":
    yt20 = (0.05, 0.10, 0.15, 0.20)
    # Concept 1: an example of approximations (20 coins), and Worked examples 11 and 12 (shaded areas)
    approx("c17c_coin20", 20, Fr(1, 2), 0.21, yt20, w=380, h=135, fs=8.8)
    approx("c17c_ex11", 20, Fr(1, 2), 0.21, yt20, shade=(12.5, 20.5), w=380, h=135, fs=8.8)
    approx("c17c_ex12", 20, Fr(1, 2), 0.21, yt20, shade=(7.5, 12.5), w=380, h=135, fs=8.8)
    # Concept 5: how good is the approximation? p = 1/2 (n = 5, 10) and p = 1/6 (n = 5, 10, 20)
    yt35 = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35)
    approx("c17c_h5", 5, Fr(1, 2), 0.37, yt35, w=200, h=140)
    approx("c17c_h10", 10, Fr(1, 2), 0.37, yt35, w=200, h=140)
    approx("c17c_s5", 5, Fr(1, 6), 0.52, (0.10, 0.20, 0.30, 0.40, 0.50), w=200, h=150)
    approx("c17c_s10", 10, Fr(1, 6), 0.37, yt35, w=200, h=140)
    approx("c17c_s20", 20, Fr(1, 6), 0.26, (0.05, 0.10, 0.15, 0.20, 0.25), w=380, h=125, fs=8.8)
    # Exercise 17C Q3f
    q3_histogram("c17c_q3")
    # Exercise 17C Q12 answers: operating characteristic curves
    oc_curves("a17c_q12a", [(oc_points(10, 1), "ink", "a")])
    oc_curves("a17c_q12b", [(oc_points(10, 1), "ink", "a"), (oc_points(15, 2), "blue", "b")])
