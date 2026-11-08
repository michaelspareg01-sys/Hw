"""Figures for Lesson 12A (Inverse trigonometric functions: differentiating).

Kept in its own file so that parallel lesson builds do not edit the shared figs.py.
Run: python3 workspace/build/int3/figs_12a.py   (writes svg/c12a_*.svg and svg/a12a_*.svg)
"""
import os
import sys
from math import acos, asin, atan, cos, pi, sin, sqrt, tan

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import ACC, Fig, H, diag, new, save, tip  # noqa: E402
from plots import Graph  # noqa: E402
from plots import INK, LINE  # noqa: E402

R3 = sqrt(3)


def clamp(v):
    return max(-1.0, min(1.0, v))


def tangent(g, x0, y0, m, half):
    """Short tangent segment of gradient m through (x0, y0), half-length 'half' in x units."""
    g.items.append(f'<line x1="{g.X(x0 - half):.1f}" y1="{g.Y(y0 - m * half):.1f}" x2="{g.X(x0 + half):.1f}" '
                   f'y2="{g.Y(y0 + m * half):.1f}" stroke="{ACC["ink"]}" stroke-width="1.1"/>')
    return g


# ---------------- Exercise 12A Q1: y = sin^-1 x on a fine grid (equal scales) ----------------
def fig_q1():
    u = 100                      # pixels per unit on both axes
    x0, x1, y0, y1 = -1.2, 1.2, -1.9, 1.9
    pl, pt = 14, 14
    W, Hh = int((x1 - x0) * u) + 2 * pl + 8, int((y1 - y0) * u) + 2 * pt
    X = lambda x: pl + (x - x0) * u
    Y = lambda y: pt + (y1 - y) * u
    f = Fig(W, Hh)
    for k in range(int(round((x1 - x0) * 10)) + 1):
        xv = x0 + k / 10
        major = abs(round(xv * 2) - xv * 2) < 1e-9
        f.raw(f'<line x1="{X(xv):.1f}" y1="{Y(y1):.1f}" x2="{X(xv):.1f}" y2="{Y(y0):.1f}" stroke="{INK if major else LINE}" '
              f'stroke-width="{0.9 if major else 0.6}" stroke-opacity="{0.55 if major else 1}"/>')
    for k in range(int(round((y1 - y0) * 10)) + 1):
        yv = y0 + k / 10
        major = abs(round(yv * 2) - yv * 2) < 1e-9
        f.raw(f'<line x1="{X(x0):.1f}" y1="{Y(yv):.1f}" x2="{X(x1):.1f}" y2="{Y(yv):.1f}" stroke="{INK if major else LINE}" '
              f'stroke-width="{0.9 if major else 0.6}" stroke-opacity="{0.55 if major else 1}"/>')
    f.arrow(X(x0), Y(0), X(x1) + 8, Y(0), width=1.4, head=7)
    f.arrow(X(0), Y(y0), X(0), Y(y1) - 6, width=1.4, head=7)
    f.text(X(x1) + 12, Y(0) + 4, "x", anchor="start", italic=True)
    f.text(X(0) - 6, pt - 2, "y", anchor="end", italic=True)
    pts = " ".join(f"{X(sin(t)):.1f},{Y(t):.1f}" for t in [-H + k * pi / 600 for k in range(601)])
    f.raw(f'<polyline points="{pts}" fill="none" stroke="{ACC["blue"]}" stroke-width="1.8"/>')
    f.dot(X(-1), Y(-H), 3).dot(X(1), Y(H), 3)
    f.line(X(0), Y(H), X(1), Y(H), color="faint", width=1.0, dash="4 3")
    f.line(X(-1), Y(-H), X(0), Y(-H), color="faint", width=1.0, dash="4 3")
    for v, s in ((-1, "−1"), (1, "1")):
        f.raw(f'<rect x="{X(v) - 8:.1f}" y="{Y(0) + 4:.1f}" width="16" height="14" fill="#fff"/>')
        f.text(X(v), Y(0) + 15, s, size=11)
    for v, s in ((-1, "−1"), (1, "1")):
        f.raw(f'<rect x="{X(0) - 20:.1f}" y="{Y(v) - 7:.1f}" width="17" height="14" fill="#fff"/>')
        f.text(X(0) - 5, Y(v) + 4, s, anchor="end", size=11)
    f.raw(f'<rect x="{X(0) + 4:.1f}" y="{Y(H) - 22:.1f}" width="16" height="26" fill="#fff"/>')
    f.raw(f'<rect x="{X(0) - 26:.1f}" y="{Y(-H) - 10:.1f}" width="24" height="26" fill="#fff"/>')
    f.items.append(__import__("plots")._txt(X(0) + 12, Y(H) - 9, "π/2", size=10.5))
    f.items.append(__import__("plots")._txt(X(0) - 12, Y(-H) + 3, "−π/2", size=10.5))
    save("c12a_q1grid", f)


# ---------------- Example 2: y = cos^-1(x - 1), tangents of gradient -2 ----------------
def ex2_like(name, F, a, b, top, pts, m, labels, xt, yt, w=210, h=180):
    g = new(min(a, 0) - 0.5, max(b, 0) + 0.6, min(-0.4, F(a) - 0.4, F(b) - 0.4), max(top + 0.45, 0.5), w, h)
    g.curve(F, color="blue", width=2.1, x0=a, x1=b, n=900)
    g.dot(a, F(a)).dot(b, F(b))
    for (px, py), lab in zip(pts, labels):
        tangent(g, px, py, m, 0.28)
        g.dot(px, py, r=2.6)
        g.label(px, py, lab[0], dx=lab[1], dy=lab[2], italic=True, size=11.5)
    for px, py in pts:
        g.hline(py, x0=0, x1=px, dash="3 3")
    g.xticks(xt).yticks(yt)
    save(name, g)
    return g


def fig_ex2():
    F = lambda x: acos(clamp(x - 1))
    pA, pB = (1 + R3 / 2, pi / 6), (1 - R3 / 2, 5 * pi / 6)
    ex2_like("c12a_ex2", F, 0, 2, pi, [pA, pB], -2, [("A", 9, -2), ("B", 10, -4)],
             [(1, "1"), (2, "2")], [(pi, "π"), (5 * pi / 6, "5π/6"), (H, "π/2"), (pi / 6, "π/6")])


def fig_c2():
    F = lambda x: asin(clamp(x + 1))
    pA, pB = (-1 + R3 / 2, pi / 3), (-1 - R3 / 2, -pi / 3)
    g = new(-2.6, 0.7, -1.95, 1.95, 220, 190)
    g.curve(F, color="blue", width=2.1, x0=-2, x1=0, n=900)
    g.dot(-2, -H).dot(0, H)
    for (px, py), lab in zip((pA, pB), (("A", -10, -4), ("B", -11, -5))):
        tangent(g, px, py, 2, 0.22)
        g.dot(px, py, r=2.6)
        g.label(px, py, lab[0], dx=lab[1], dy=lab[2], italic=True, size=11.5)
        g.hline(py, x0=min(0, px), x1=max(0, px), dash="3 3")
    g.hline(-H, x0=-2, x1=0, dash="3 3")
    g.xticks([(-2, "-2"), (-1, "")]).yticks([(H, "π/2"), (pi / 3, ""), (-pi / 3, ""), (-H, "")])
    g.label(-1, 0, "-1", dx=11, dy=14, size=11)
    g.label(0, pi / 3, "π/3", dx=7, anchor="start", size=10.5)
    g.label(0, -pi / 3, "-π/3", dx=15, dy=-3, anchor="start", size=10.5)
    g.label(0, -H, "-π/2", dx=15, dy=3, anchor="start", size=10.5)
    save("a12a_c2d", g)
    F = lambda x: acos(clamp(x - 2))
    pA, pB = (2 + R3 / 2, pi / 6), (2 - R3 / 2, 5 * pi / 6)
    ex2_like("a12a_c2y", F, 1, 3, pi, [pA, pB], -2, [("A", 9, -2), ("B", 10, -4)],
             [(1, "1"), (2, "2"), (3, "3")], [(pi, "π"), (5 * pi / 6, "5π/6"), (H, "π/2"), (pi / 6, "π/6")], w=230)


# ---------------- Example 4 and the Concept 4 answers: zigzags ----------------
def zgraph(xmin, xmax, ymin, ymax, w, h):
    g = Graph(xmin, xmax, ymin, ymax, w=w, h=h, pad=(16, 30, 18, 24))
    g.axes("x", "y")
    return g


def xlab(g, ticks):
    """Ticks on the x-axis; each label is placed (dx, dy) from the tick, clear of the curve."""
    g.xticks([(v, "") for v, *_ in ticks])
    for v, lab, dx, dy in ticks:
        g.label(v, 0, lab, dx=dx, dy=dy, size=10.5)
    return g


def fig_ex4():
    f = lambda t: acos(clamp(cos(t)))
    g = new(-2.5 * pi * 1.08, 2.5 * pi * 1.08, -0.5, 3.8, 300, 120)
    g.hline(pi, dash="3 3", x0=-2.5 * pi, x1=2.5 * pi)
    g.curve(f, color="blue", width=2.0, x0=-2.5 * pi, x1=2.5 * pi, n=1600)
    tip(g, f, 2.5 * pi, 1)
    tip(g, f, -2.5 * pi, -1)
    g.xticks([(-2 * pi, "-2π"), (-pi, "-π"), (pi, "π"), (2 * pi, "2π")]).yticks([(pi, "π")])
    save("c12a_ex4", g)
    # Your turn: y = cos^-1(cos 2x), between 0 and pi; it touches the x-axis at k pi
    f2 = lambda t: acos(clamp(cos(2 * t)))
    g = zgraph(-1.3 * pi, 1.3 * pi, -0.5, 3.8, 320, 140)
    g.hline(pi, dash="3 3", x0=-1.25 * pi, x1=1.25 * pi)
    g.curve(f2, color="blue", width=2.0, x0=-1.25 * pi, x1=1.25 * pi, n=1600)
    tip(g, f2, 1.25 * pi, 1)
    tip(g, f2, -1.25 * pi, -1)
    xlab(g, [(-pi, "-π", 0, 14), (-H, "-π/2", 0, 18), (H, "π/2", 0, 18), (pi, "π", 0, 14)])
    g.yticks([(pi, "")])
    g.label(0, pi, "π", dx=-7, dy=-9, anchor="end", size=11)
    save("a12a_c4y", g)
    # Exercise 21e: y = sin^-1(sin x), a zigzag between -pi/2 and pi/2 through (k pi, 0)
    f3 = lambda t: asin(clamp(sin(t)))
    g = zgraph(-2.35 * pi, 2.35 * pi, -2.1, 2.1, 340, 150)
    g.hline(H, dash="3 3", x0=-2.3 * pi, x1=2.3 * pi).hline(-H, dash="3 3", x0=-2.3 * pi, x1=2.3 * pi)
    g.curve(f3, color="blue", width=2.0, x0=-2.3 * pi, x1=2.3 * pi, n=1600)
    tip(g, f3, 2.3 * pi, 1)
    tip(g, f3, -2.3 * pi, -1)
    # at even multiples of pi the curve rises to the right, at odd multiples it falls to the right
    xlab(g, [(-2 * pi, "-2π", 11, 12), (-pi, "-π", -10, 12), (pi, "π", -9, 12), (2 * pi, "2π", 11, 12)])
    g.yticks([(H, ""), (-H, "")])
    g.label(0, H, "π/2", dx=-14, dy=-2, size=10.5)
    g.label(0, -H, "-π/2", dx=16, dy=0, size=10.5)
    save("a12a_q21e", g)


def fig_c4d():
    # y = tan^-1(tan x): segments of gradient 1, open circles where tan x is undefined
    g = zgraph(-2.35 * pi, 2.35 * pi, -2.1, 2.1, 340, 150)
    g.hline(H, dash="3 3").hline(-H, dash="3 3")
    lo_x, hi_x = -2.25 * pi, 2.25 * pi
    for k in range(-2, 3):
        a, b = k * pi - H, k * pi + H
        lo, hi = max(a, lo_x), min(b, hi_x)
        g.curve(lambda t, k=k: t - k * pi, color="blue", width=2.0, x0=lo, x1=hi, n=4)
        if a >= lo_x:
            g.dot(a, -H, color="blue", r=2.8, hollow=True)
        if b <= hi_x:
            g.dot(b, H, color="blue", r=2.8, hollow=True)
    tip(g, lambda t: t - 2 * pi, hi_x, 1)
    tip(g, lambda t: t + 2 * pi, lo_x, -1)
    # each segment crosses the axis at k pi rising to the right, so labels go below and to the right
    xlab(g, [(-2 * pi, "-2π", 11, 12), (-pi, "-π", 10, 12), (pi, "π", 9, 12), (2 * pi, "2π", 11, 12)])
    g.yticks([(H, ""), (-H, "")])
    g.label(0, H, "π/2", dx=-14, dy=-2, size=10.5)
    g.label(0, -H, "-π/2", dx=-17, dy=16, size=10.5)
    save("a12a_c4d", g)


# ---------------- Answers: Exercise 13f and 17g ----------------
def fig_q13f():
    f = lambda x: acos(clamp(x * x))
    g = new(-1.6, 1.6, -0.35, 2.0, 190, 150)
    g.curve(f, color="blue", width=2.1, x0=-1, x1=1, n=900)
    g.dot(-1, 0).dot(1, 0)
    g.xticks([(-1, "-1"), (1, "1")]).yticks([(H, "")])
    g.label(0, H, "π/2", dx=-13, dy=-13, size=10.5)
    save("a12a_q13f", g)


def fig_q17g():
    f = lambda x: acos(clamp(1 / x))
    g = new(-4.2, 4.2, -0.5, 3.75, 230, 160)
    g.hline(H, dash="4 3")
    g.curve(f, color="blue", width=2.1, x0=1, x1=4.0, n=900)
    g.curve(f, color="blue", width=2.1, x0=-4.0, x1=-1, n=900)
    tip(g, f, 4.0, 1)
    tip(g, f, -4.0, -1)
    g.dot(1, 0).dot(-1, pi)
    g.xticks([(-1, "-1"), (1, "1")]).yticks([(pi, "π"), (H, "π/2")])
    save("a12a_q17g", g)


# ---------------- Exercise Q14 and Q15 diagrams ----------------
def fig_q14():
    f = Fig(230, 190)
    E, P = (40, 165), (180, 165)
    B, T = (180, 75), (180, 30)
    f.line(*E, *P).line(*P, *T, width=1.6)
    f.line(*E, *B, color="blue", width=1.4).line(*E, *T, color="blue", width=1.4)
    f.right(P[0], P[1], -1, -1, 8)
    f.text(E[0] - 4, E[1] + 16, "E", italic=True).text(P[0] + 4, P[1] + 16, "P", italic=True)
    f.text(B[0] + 7, B[1] + 4, "B", anchor="start", italic=True).text(T[0] + 7, T[1] + 2, "T", anchor="start", italic=True)
    f.text((E[0] + P[0]) / 2, E[1] + 16, "x", italic=True)
    f.text(T[0] + 8, (B[1] + T[1]) / 2 + 4, "1 m", anchor="start", size=11)
    f.text(B[0] + 8, (B[1] + P[1]) / 2 + 4, "3 m", anchor="start", size=11)
    f.arc(E[0], E[1], 52, 32.7, 48.2)
    f.text(E[0] + 36, E[1] - 58, "θ", size=12, italic=True)
    save("c12a_q14", f)


def fig_q15():
    f = Fig(275, 130)
    A, O, P = (40, 25), (40, 105), (170, 25)
    f.line(*A, *O).line(*A, *P)
    f.arrow(P[0], P[1], P[0] + 45, P[1], dash="4 3", width=1.3)
    f.line(*O, *P, color="blue", width=1.4)
    f.line(O[0], O[1], O[0] + 95, O[1], color="faint", width=1.1, dash="3 3")
    f.right(A[0], A[1], 1, 1, 8)
    f.dot(*P, r=2.6)
    f.text(A[0] - 6, A[1] + 2, "A", anchor="end", italic=True).text(O[0] - 6, O[1] + 6, "O", anchor="end", italic=True)
    f.text(P[0], P[1] - 8, "P", italic=True)
    f.text((A[0] + P[0]) / 2, A[1] - 8, "x", italic=True)
    f.text(A[0] + 6, (A[1] + O[1]) / 2 + 4, "6 km", anchor="start", size=11)
    f.raw(f'<text x="{P[0] + 8}" y="{P[1] + 22}" text-anchor="start" font-size="11" fill="{ACC["ink"]}" font-weight="500">600 km/h</text>')
    f.arc(O[0], O[1], 30, 0, 31.6)
    f.text(O[0] + 37, O[1] - 7, "θ", size=12, italic=True)
    save("c12a_q15", f)


if __name__ == "__main__":
    fig_q1()
    fig_ex2()
    fig_c2()
    fig_ex4()
    fig_c4d()
    fig_q13f()
    fig_q17g()
    fig_q14()
    fig_q15()
