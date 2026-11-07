"""Figures for Lesson 12C (answers): Exercise 12C Q7 and Q13(e).

Kept in its own file so that parallel lesson tasks do not edit int3/figs.py at the same time.
Run: python3 workspace/build/int3/figs_12c.py  (writes int3/svg/a12c_*.svg)
"""
import os
import sys
from math import cos, pi, sin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save  # noqa: E402

H = pi / 2


def new(xmin, xmax, ymin, ymax, w, h):
    g = Graph(xmin, xmax, ymin, ymax, w=w, h=h, pad=(14, 34, 18, 22))
    g.axes("x", "y")
    return g


def fig_q7():
    # y = cos 2x (dashed), y = 1/2(1 + cos 2x) (blue) and y = 1/2(1 - cos 2x) (rose), 0 <= x <= 2 pi
    g = new(-0.35, 6.9, -1.3, 1.45, 330, 150)
    g.hline(1, dash="3 3", x0=0, x1=2 * pi)
    g.curve(lambda x: cos(2 * x), color="faint", width=1.4, dash="5 3", x0=0, x1=2 * pi)
    g.curve(lambda x: (1 + cos(2 * x)) / 2, color="blue", width=2.0, x0=0, x1=2 * pi)
    g.curve(lambda x: (1 - cos(2 * x)) / 2, color="rose", width=2.0, x0=0, x1=2 * pi)
    g.xticks([(H, "π/2"), (pi, "π"), (3 * H, "3π/2"), (2 * pi, "2π")])
    g.yticks([(1, "1"), (-1, "-1"), (0.5, "")])
    g.label(0, 0.5, "1/2", dx=-14, size=10)
    save("a12c_q7", g)


def fig_q13():
    # y = F(x) = x/2 - (1/4) sin 2x and y = F'(x) = sin^2 x on 0 <= x <= 2 pi
    F = lambda x: x / 2 - sin(2 * x) / 4
    g = new(-0.35, 6.9, -0.35, 3.55, 330, 175)
    g.hline(pi, dash="3 3", x0=0, x1=2 * pi).hline(H, dash="3 3", x0=0, x1=pi)
    g.curve(lambda x: sin(x) ** 2, color="rose", width=2.0, x0=0, x1=2 * pi)
    g.curve(F, color="blue", width=2.2, x0=0, x1=2 * pi)
    for xv in (H, pi, 3 * H, 2 * pi):
        g.dot(xv, F(xv), r=2.6)
    g.dot(0, 0, r=2.6)
    g.xticks([(H, "π/2"), (pi, "π"), (3 * H, "3π/2"), (2 * pi, "2π")])
    g.yticks([(pi, "π"), (H, "π/2"), (1, "1")])
    g.label(5.0, F(5.0), "y = F(x)", dx=-8, dy=-12, anchor="end", size=10, color="blue")
    g.label(3 * H, 1, "y = F′(x)", dx=0, dy=-9, size=10, color="rose")
    save("a12c_q13", g)


if __name__ == "__main__":
    fig_q7()
    fig_q13()
