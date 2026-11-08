"""Figures for Lesson 6I (kept apart from figs.py, which the scaffold task owns; same pattern as figs_6e.py).

Run: python3 workspace/build/int2/figs_6i.py   (writes svg/c6i_*.svg)
"""
import os
import sys
from math import e

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from relabel import relabel  # noqa: E402
from figs import RELOG, Graph, ACC, INK  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")


def save(name, g, width_mm=None):
    s = g.svg()
    if width_mm:
        s = s.replace("<svg ", f'<svg style="width:{width_mm}mm;max-width:100%" ', 1)
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(relabel(s, RELOG, name))      # Int2 assembly: clear labels of strokes


def zero(x):
    return 0


def recip(x):
    return 1 / x if x != 0 else None


def ylab(g, x, y, dx=8, dy=0, anchor="start", size=13):
    """The label 'y = 1/x' with a small stacked fraction."""
    X, Y = g.X(x) + dx, g.Y(y) + dy
    g.items.append(f'<text x="{X:.1f}" y="{Y + 4:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{INK}" '
                   f'font-style="italic">y =</text>')
    fx = X + (size * 2.15 if anchor == "start" else 6)
    g.items.append(f'<text x="{fx:.1f}" y="{Y - 2:.1f}" text-anchor="middle" font-size="{size * 0.85:.1f}" fill="{INK}">1</text>')
    g.items.append(f'<line x1="{fx - 4:.1f}" y1="{Y + 1:.1f}" x2="{fx + 4:.1f}" y2="{Y + 1:.1f}" stroke="{INK}" stroke-width="0.9"/>')
    g.items.append(f'<text x="{fx:.1f}" y="{Y + size * 0.85:.1f}" text-anchor="middle" font-size="{size * 0.85:.1f}" fill="{INK}" '
                   f'font-style="italic">x</text>')


def rectangles():
    """Example 33: the integral of 1/x from 1 to 2 lies between the areas of two rectangles."""
    g = Graph(-0.35, 3.3, -0.25, 2.6, w=230, h=190, pad=(24, 30, 18, 14))
    hatch = (f'<defs><pattern id="h6i" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             f'<line x1="0" y1="0" x2="0" y2="6" stroke="{INK}" stroke-width="0.9"/></pattern></defs>')
    x1, x2 = g.X(1), g.X(2)
    g.items.append(f'<rect x="{x1:.1f}" y="{g.Y(1):.1f}" width="{x2 - x1:.1f}" height="{g.Y(0) - g.Y(1):.1f}" '
                   f'fill="url(#h6i)" stroke="{INK}" stroke-width="1"/>')
    g.items.append(f'<rect x="{x1:.1f}" y="{g.Y(0.5):.1f}" width="{x2 - x1:.1f}" height="{g.Y(0) - g.Y(0.5):.1f}" '
                   f'fill="#f7c9d4" fill-opacity="1" stroke="{INK}" stroke-width="1"/>')
    g.items.insert(0, hatch)
    g.axes("x", "y")
    g.curve(recip, color="ink", width=1.8, x0=1 / 2.6, x1=3.3)
    g.hline(1, x0=0, x1=1).hline(0.5, x0=0, x1=1)
    g.xticks([(1, "1"), (2, "2")])
    g.yticks([(1, "1"), (0.5, "1/2")])
    ylab(g, 0.62, 1.95, dx=8)
    save("c6i_rect", g)


def char_e():
    """A characterisation of e: the area under y = 1/x from 1 to e is 1."""
    g = Graph(-0.35, 3.6, -0.25, 2.6, w=230, h=170, pad=(24, 30, 18, 14))
    g.fill(recip, zero, 1, e)
    g.axes("x", "y")
    g.curve(recip, color="ink", width=1.8, x0=1 / 2.6, x1=3.6)
    g.hline(1, x0=0, x1=1).vline(1, 0, 1).vline(e, 0, 1 / e)
    g.xticks([(1, "1")])
    g.label(e, 0, "e", dy=14, size=11, italic=True)
    g.yticks([(1, "1")])
    ylab(g, 0.62, 1.95, dx=8)
    save("c6i_e", g)


def both_sides():
    """The two branches of y = 1/x; the definite integral from -4 to -1 lies on the left branch."""
    g = Graph(-4.8, 3.2, -2.9, 2.9, w=240, h=200, pad=(18, 30, 18, 14))
    g.fill(zero, recip, -4, -1)
    g.axes("x", "y")
    g.curve(recip, color="ink", width=1.8, x0=-4.8, x1=-1 / 2.9)
    g.curve(recip, color="ink", width=1.8, x0=1 / 2.9, x1=3.2)
    g.vline(-1, -1, 0).vline(-4, -0.25, 0)
    g.label(-4, 0, "-4", dy=-11, size=11).label(-1, 0, "-1", dy=-11, size=11)
    save("c6i_both", g)


if __name__ == "__main__":
    rectangles()
    char_e()
    both_sides()
