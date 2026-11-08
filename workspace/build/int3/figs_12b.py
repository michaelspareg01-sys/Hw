"""Figures for Lesson 12B (kept apart from figs.py, which the scaffold task owns).

Run: python3 workspace/build/int3/figs_12b.py   (writes svg/c12b_*.svg, svg/pp12b_*.svg, svg/a12b_*.svg)
"""
import os
import sys
from math import asin, atan, pi, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save, tip, ACC, INK, _txt  # noqa: E402

H = pi / 2
GRID = "#c9d1db"
GRID_MID = "#8a96a3"


def new(xmin, xmax, ymin, ymax, w, h, pad=(14, 30, 18, 14)):
    g = Graph(xmin, xmax, ymin, ymax, w=w, h=h, pad=pad)
    g.axes("x", "y")
    return g


def fig_ex10():
    # Example 10: area under y = sin^-1 x from x = 0 to x = 1
    g = new(-1.5, 1.6, -1.9, 1.95, 190, 170)
    g.fill(lambda t: asin(min(1.0, t)), lambda t: 0.0, 0, 1, color="blue")
    g.curve(asin, color="blue", width=2.2, x0=-1, x1=1, n=800)
    g.dot(-1, -H).dot(1, H)
    g.vline(1, 0, H, color="blue", dash="", width=1.4)
    g.xticks([(-1, "-1"), (1, "1")]).yticks([(H, "π/2"), (-H, "-π/2")])
    save("c12b_ex10", g)


def fig_q1():
    # Exercise 12B Q1: y = 1/(1 + x^2) on graph paper, little squares 0.1 by 0.1
    x0, x1, y0, y1 = -3.0, 3.0, -0.3, 1.2
    W, Hh = 600, 175
    pl, pr, pt, pb = 14, 30, 18, 12
    g = Graph(x0, x1, y0, y1, w=W, h=Hh, pad=(pl, pr, pt, pb))
    lines = []
    for i in range(int(round((x1 - x0) * 10)) + 1):
        v = round(x0 + i / 10, 2)
        major = abs(v - round(v)) < 1e-9
        half = abs(v * 2 - round(v * 2)) < 1e-9
        col, wd = (INK, 1.1) if major else ((GRID_MID, 0.8) if half else (GRID, 0.5))
        lines.append(f'<line x1="{g.X(v):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(v):.1f}" y2="{g.Y(y1):.1f}" stroke="{col}" stroke-width="{wd}"/>')
    for j in range(int(round((y1 - y0) * 10)) + 1):
        v = round(y0 + j / 10, 2)
        major = abs(v - round(v)) < 1e-9
        half = abs(v * 2 - round(v * 2)) < 1e-9
        col, wd = (INK, 1.1) if major else ((GRID_MID, 0.8) if half else (GRID, 0.5))
        lines.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(v):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(v):.1f}" stroke="{col}" stroke-width="{wd}"/>')
    g.items += lines
    g.axes("x", "y")
    g.curve(lambda t: 1 / (1 + t * t), color="blue", width=1.8, x0=-3, x1=3)
    for v in (-2, -1, 1, 2):
        g.items.append(f'<rect x="{g.X(v) - 9:.1f}" y="{g.Y(0) + 4:.1f}" width="18" height="13" fill="#fff"/>')
        g.label(v, 0, str(v), dy=11, size=11)
    g.items.append(f'<rect x="{g.X(0) - 15:.1f}" y="{g.Y(0) + 4:.1f}" width="12" height="13" fill="#fff"/>')
    g.label(0, 0, "0", dx=-9, dy=11, size=11)
    g.items.append(f'<rect x="{g.X(0) - 15:.1f}" y="{g.Y(1) - 18:.1f}" width="12" height="13" fill="#fff"/>')
    g.label(0, 1, "1", dx=-9, dy=-11, size=11)
    g.items.append(f'<rect x="{g.X(1.12):.1f}" y="{g.Y(0.93):.1f}" width="92" height="40" fill="#fff"/>')
    g.label(1.17, 0.72, "1/1 + x²", dx=62, size=14)
    g.items.append(f'<rect x="{g.X(1.12):.1f}" y="{g.Y(0.93):.1f}" width="{g.X(1.17) - g.X(1.12) + 27:.1f}" height="40" fill="#fff"/>')
    g.label(1.17, 0.72, "y =", anchor="start", size=13, italic=True)
    save("c12b_q1", g)


def fig_q17():
    # Exercise 12B Q17: y = sin^-1 x, the y-axis and the tangent at (sqrt3/2, pi/3)
    a = sqrt(3) / 2
    tan_ = lambda t: 2 * t + pi / 3 - sqrt(3)
    g = new(-1.35, 1.45, -1.85, 1.95, 175, 235)
    g.fill(lambda t: asin(t), tan_, 0, a, color="blue")
    g.curve(asin, color="blue", width=2.0, x0=-1, x1=1, n=800)
    g.curve(tan_, color="ink", width=1.3, x0=-0.12, x1=1.28)
    tip(g, tan_, 1.28, 1, color="ink")
    tip(g, tan_, -0.12, -1, color="ink")
    g.dot(-1, -H).dot(1, H).dot(a, pi / 3, r=2.6)
    g.vline(a, 0, pi / 3, dash="3 3")
    g.hline(pi / 3, x0=0, x1=a, dash="3 3")
    g.xticks([(-1, "-1")]).xticks([(1, "1")], below=False).yticks([(H, "π/2"), (pi / 3, "π/3"), (-H, "-π/2")])
    g.xticks([(a, "")])
    g.label(a, 0, "√3/2", dx=-4, dy=19, size=10)
    save("c12b_q17", g)


def fig_q23():
    # Exercise 12B Q23: n rectangles between y = tan^-1 x and y = tan^-1 (x - 1) on [1, n + 1]
    W, Hh = 520, 175
    g = Graph(-0.25, 7.3, -0.12, 1.85, w=W, h=Hh, pad=(26, 30, 18, 20))
    g.axes("x", "y")
    g.hline(H, dash="4 3", x0=0, x1=7.3)
    for k in (1, 2, 3, 5, 6):
        top = atan(k if k < 4 else k)
        g.items.append(f'<rect x="{g.X(k):.1f}" y="{g.Y(top):.1f}" width="{g.X(k + 1) - g.X(k):.1f}" '
                       f'height="{g.Y(0) - g.Y(top):.1f}" fill="none" stroke="{INK}" stroke-width="1"/>')
    g.curve(atan, color="blue", width=2.0, x0=0, x1=7.25)
    g.curve(lambda t: atan(t - 1), color="blue", width=2.0, x0=1, x1=7.25)
    g.xticks([(1, "1"), (2, "2"), (3, "3"), (5, "n"), (6, "n + 1")])
    g.label(4, 0, "· · ·", dy=13, size=11)
    g.label(4.05, 0.62, "· · ·", size=12)
    g.yticks([(H, "π/2")])
    g.label(0.55, 1.45, "y = tan⁻¹x", anchor="start", size=10.5, italic=True)
    g.items.append(f'<line x1="{g.X(1.05):.1f}" y1="{g.Y(1.36):.1f}" x2="{g.X(1.3):.1f}" y2="{g.Y(atan(1.3)) - 3:.1f}" stroke="{INK}" stroke-width="0.9"/>')
    g.label(4.45, 1.76, "y = tan⁻¹(x − 1)", anchor="start", size=10.5, italic=True)
    g.items.append(f'<line x1="{g.X(5.1):.1f}" y1="{g.Y(1.68):.1f}" x2="{g.X(5.0):.1f}" y2="{g.Y(atan(4.0)) + 2:.1f}" stroke="{INK}" stroke-width="0.9"/>')
    save("c12b_q23", g)


def fig_pp_sths23():
    # STHS 2023 Q14(b): region enclosed by y = 4 - 8/sqrt(8 - x^2) and the semicircle y = -sqrt(4 - x^2)
    f = lambda t: 4 - 8 / sqrt(8 - t * t)
    s = lambda t: -sqrt(max(0.0, 4 - t * t))
    g = Graph(-3.3, 3.3, -3.6, 2.6, w=280, h=258, pad=(14, 26, 18, 10))
    g.axes("x", "y")
    g.fill(f, s, -2, 2, color="green", opacity=0.45)
    g.curve(f, color="ink", width=1.8, x0=-2.62, x1=2.62, n=600)
    g.curve(s, color="ink", width=1.8, x0=-2, x1=2, n=600)
    tip(g, f, 2.62, 1, color="ink")
    tip(g, f, -2.62, -1, color="ink")
    g.dot(-2, 0, r=2.6).dot(2, 0, r=2.6).dot(0, 4 - sqrt(8), r=2.6).dot(0, -2, r=2.6)
    g.xticks([(-3, "-3"), (-1, "-1"), (1, "1")])
    g.label(-2, 0, "-2", dx=-7, dy=-11, size=10)
    g.label(2, 0, "2", dx=8, dy=-11, size=10)
    g.yticks([(2, "2"), (1, ""), (-1, "-1"), (-3, "-3")])
    g.label(0, 1, "1", dx=8, dy=-2, size=10)
    g.label(0, -2, "-2", dx=12, dy=8, size=10)
    g.items.append(f'<rect x="{g.X(0) - 44:.1f}" y="{g.Y(4 - sqrt(8)) - 24:.1f}" width="40" height="14" fill="#fff" fill-opacity="0.85"/>')
    g.label(0, 4 - sqrt(8), "4 − √8", dx=-6, dy=-17, anchor="end", size=10.5)
    save("pp12b_sths23", g)


def fig_a15():
    # Answers Q15: y = sqrt(4 - x^2) (dashed) and y = 1/sqrt(4 - x^2)
    g = new(-2.9, 2.9, -0.3, 3.3, 220, 165)
    g.vline(2, -0.3, 3.3, dash="3 3").vline(-2, -0.3, 3.3, dash="3 3")
    g.curve(lambda t: sqrt(max(0.0, 4 - t * t)), color="faint", width=1.4, dash="4 3", x0=-2, x1=2, n=600)
    f = lambda t: 1 / sqrt(4 - t * t)
    g.curve(f, color="blue", width=2.0, x0=-1.958, x1=1.958, n=600)
    tip(g, f, 1.958, 1)
    tip(g, f, -1.958, -1)
    g.dot(0, 0.5, r=2.6)
    g.xticks([(-2, "-2"), (2, "2")]).yticks([(2, "2"), (0.5, "")])
    g.label(0, 0.5, "1/2", dx=-14, dy=-14, size=10)
    save("a12b_q15", g)


def fig_a16():
    # Answers Q16: y = 4/(x^2 + 4) and y = (x^2 + 4)/4 (dashed)
    g = new(-4.2, 4.2, -0.3, 3.0, 230, 150)
    g.curve(lambda t: (t * t + 4) / 4, color="faint", width=1.4, dash="4 3", x0=-2.9, x1=2.9)
    f = lambda t: 4 / (t * t + 4)
    g.curve(f, color="blue", width=2.0, x0=-4.1, x1=4.1)
    tip(g, f, 4.1, 1)
    tip(g, f, -4.1, -1)
    g.dot(0, 1, r=2.6)
    g.xticks([(-2, "-2"), (2, "2")]).yticks([(1, "1"), (2, "2")])
    g.label(2.15, 1.72, "y = ¼(x² + 4)", anchor="start", size=10, italic=True)
    g.label(1.5, 0.82, "y = f(x)", anchor="start", size=10, italic=True)
    save("a12b_q16", g)


if __name__ == "__main__":
    fig_ex10()
    fig_q1()
    fig_q17()
    fig_q23()
    fig_pp_sths23()
    fig_a15()
    fig_a16()
