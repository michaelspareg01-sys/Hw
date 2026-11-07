"""Figures for Lesson 12D (answers): Exercise 12D Q6.

Kept in its own file so that parallel lesson tasks do not edit int3/figs.py at the same time.
Run: python3 workspace/build/int3/figs_12d.py  (writes int3/svg/a12d_q6.svg)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save  # noqa: E402


def fig_q6():
    # Region under y = x^2/(1 + x^6) from x = 0 to x = 1 (area pi/12)
    f = lambda x: x * x / (1 + x ** 6)
    g = Graph(-0.25, 2.25, -0.12, 0.82, w=260, h=140, pad=(14, 34, 18, 22))
    g.axes("x", "y")
    g.fill(f, lambda t: 0.0, 0, 1, color="blue")
    g.curve(f, color="blue", width=2.2, x0=0, x1=2.2)
    g.vline(1, 0, f(1), color="blue", dash="", width=1.4)
    g.dot(1, 0.5, r=2.6)
    g.xticks([(1, "1"), (2, "2")])
    g.yticks([(0.5, "1/2")])
    g.label(1.45, f(1.45), "y = x²/(1 + x⁶)", dx=6, dy=-10, anchor="start", size=10, color="blue")
    save("a12d_q6", g)


if __name__ == "__main__":
    fig_q6()
