"""Figures for Lesson 5B (kept apart from figs.py, which the scaffold task owns; same pattern as figs_4j.py).

Run: python3 workspace/build/int1/figs_5b.py   (writes svg/c5b_*.svg, svg/q5b_*.svg and svg/p5b_*.svg)
"""
import os
import sys
from math import cos, pi, sin, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Fig, Graph, save, ACC, INK, FAINT  # noqa: E402,F401


def zero(x):
    return 0.0


def lesson():
    # Worked example 2a: y = 2x, region from 0 to 2 (a triangle)
    g = Graph(-1.0, 3.0, -2.0, 5.6, w=150, h=150, pad=(16, 30, 16, 14))
    g.fill(lambda x: 2 * x, zero, 0, 2, opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: 2 * x, color="ink", width=1.5, x0=-0.8, x1=2.75)
    g.vline(2, 0, 4, color="ink", dash="", width=1.1).hline(4, color="faint", x0=0, x1=2)
    g.xticks([(2, "2")]).yticks([(4, "4")])
    g.label(2.75, 5.5, "y = 2x", dx=-4, anchor="end", size=11, italic=True)
    save("c5b_e2a", g)

    # Worked example 2b: y = 2x - 3, region from 2 to 4 (a trapezium)
    g = Graph(-0.8, 5.0, -3.6, 6.2, w=150, h=160, pad=(16, 30, 16, 14))
    g.fill(lambda x: 2 * x - 3, zero, 2, 4, opacity=0.25)
    g.axes("x", "y")
    g.curve(lambda x: 2 * x - 3, color="ink", width=1.5, x0=0.5, x1=4.55)
    g.vline(2, 0, 1, color="ink", dash="", width=1.1).vline(4, 0, 5, color="ink", dash="", width=1.1)
    g.hline(1, color="faint", x0=0, x1=2).hline(5, color="faint", x0=0, x1=4)
    g.xticks([(2, "2"), (4, "4")]).yticks([(1, "1"), (5, "5")])
    g.label(4.4, 6.0, "y = 2x - 3", dx=-6, anchor="end", size=11, italic=True)
    save("c5b_e2b", g)

    # Warning: y = x^-4 has an asymptote at x = 0; the 'region' from -1 to 1 is unbounded
    g = Graph(-2.4, 2.4, -0.3, 6.0, w=190, h=160, pad=(14, 30, 16, 16))
    f = lambda x: x ** -4  # noqa: E731
    g.fill(lambda x: min(f(x), 6.0), zero, -1, -0.64, color="ink", opacity=0.3)
    g.fill(lambda x: min(f(x), 6.0), zero, 0.64, 1, color="ink", opacity=0.3)
    g.items.insert(0, f'<rect x="{g.X(-0.64):.1f}" y="{g.Y(6.0):.1f}" width="{g.X(0.64) - g.X(-0.64):.1f}" '
                      f'height="{g.Y(0) - g.Y(6.0):.1f}" fill="{INK}" fill-opacity="0.3"/>')
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.5, x0=-2.35, x1=-0.64)
    g.curve(f, color="ink", width=1.5, x0=0.64, x1=2.35)
    g.vline(-1, 0, 1, color="ink", dash="", width=1.1).vline(1, 0, 1, color="ink", dash="", width=1.1)
    g.xticks([(-1, "-1"), (1, "1")])
    # one text element, so that the index stays with its base when labels are nudged
    g.items.append(f'<text x="{g.X(1.5):.1f}" y="{g.Y(2.8) + 3.85:.1f}" font-size="11" fill="{INK}" font-weight="500" '
                   f'font-style="italic">y = x<tspan dy="-4.5" font-size="8.5" font-style="normal">−4</tspan></text>')
    save("c5b_asym", g)

    # The area of a circle: the circle cut into 16 sectors, and the sectors rearranged into a 'rectangle'
    BLUE, YEL = "#bfe3fa", "#fff066"
    m = 16
    f = Fig(470, 170)
    cx, cy, r = 86, 82, 66
    for i in range(m):
        a0, a1 = 2 * pi * i / m, 2 * pi * (i + 1) / m
        col = YEL if cos((a0 + a1) / 2) > 0 else BLUE
        p0 = (cx + r * sin(a0), cy - r * cos(a0))
        p1 = (cx + r * sin(a1), cy - r * cos(a1))
        f.raw(f'<path d="M{cx},{cy} L{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 0 1 {p1[0]:.1f},{p1[1]:.1f} Z" '
              f'fill="{col}" stroke="{INK}" stroke-width="0.8"/>')
    f.line(cx, cy, cx, cy + r, width=1.4)
    f.text(cx + 8, cy + 36, "r", italic=True)
    # rearranged: m/2 sectors pointing up (blue) interleaved with m/2 pointing down (yellow)
    x0, ytop, ybot = 230, 40, 40 + 64
    half = m // 2
    wsec = 26.0              # chord width of each sector at its arc
    for i in range(half):
        xl = x0 + i * wsec
        f.raw(f'<path d="M{xl:.1f},{ybot} Q{xl + wsec / 2:.1f},{ybot + 5} {xl + wsec:.1f},{ybot} L{xl + wsec / 2:.1f},{ytop} Z" '
              f'fill="{BLUE}" stroke="{INK}" stroke-width="0.8"/>')
    for i in range(half):
        xl = x0 + wsec / 2 + i * wsec
        f.raw(f'<path d="M{xl:.1f},{ytop} Q{xl + wsec / 2:.1f},{ytop - 5} {xl + wsec:.1f},{ytop} L{xl + wsec / 2:.1f},{ybot} Z" '
              f'fill="{YEL}" stroke="{INK}" stroke-width="0.8"/>')
    xr = x0 + half * wsec + wsec / 2
    f.dim(x0, ybot + 18, xr, ybot + 18)
    f.dim(x0 + wsec / 2, ytop - 16, xr, ytop - 16)
    f.text((x0 + xr) / 2, ybot + 36, "πr", italic=True)
    f.text((x0 + xr) / 2 + wsec / 4, ytop - 24, "πr", italic=True)
    f.dim(x0 - 12, ytop, x0 - 12, ybot)
    f.text(x0 - 22, (ytop + ybot) / 2 + 4, "r", italic=True)
    f.arrow(160, 82, 205, 82, color="faint", width=1.4)
    save("c5b_circle", f)


def exercise():
    # Exercise 5B Q12: a = quadrant, two lines (a V) and a quadrant; b = concave quadrant, flat line, line, quadrant
    def q12(name, segs):
        g = Graph(-0.2, 4.4, -0.25, 1.45, w=300, h=132, pad=(26, 26, 14, 20))
        g.axes("x", "y")
        g.hline(1, color="faint", x0=0, x1=4 if name.endswith("b") else 3)
        for v in (1, 2, 3, 4):
            g.vline(v, 0, 1, color="faint")
        for fn, a, b in segs:
            g.curve(fn, color="ink", width=1.5, x0=a, x1=b, n=300)
        g.xticks([(1, "1"), (2, "2"), (3, "3"), (4, "4")]).yticks([(1, "1"), (0.5, "")])
        save(name, g)

    q12("q5b_12a", [(lambda x: sqrt(max(0.0, 1 - (x - 1) ** 2)), 0, 1),
                    (lambda x: 2 - x, 1, 2), (lambda x: x - 2, 2, 3),
                    (lambda x: sqrt(max(0.0, 1 - (x - 3) ** 2)), 3, 4)])
    q12("q5b_12b", [(lambda x: 1 - sqrt(max(0.0, 1 - x * x)), 0, 1),
                    (lambda x: 1.0, 1, 2), (lambda x: 3 - x, 2, 3),
                    (lambda x: sqrt(max(0.0, 1 - (x - 4) ** 2)), 3, 4)])


def pastpaper():
    # NSB 2022 Q10: the graph of y = f(x): 0 for |x| >= 1, a peak (0, 1), straight lines to (-1, 0) and (1, 0)
    g = Graph(-2.1, 2.1, -0.2, 1.25, w=260, h=116, pad=(18, 30, 16, 20))
    g.axes("x", "y")
    g.curve(lambda x: max(0.0, 1 - abs(x)), color="ink", width=2.6, x0=-2, x1=2, n=400)
    g.xticks([(-2, "-2"), (-1, "-1"), (0, ""), (1, "1"), (2, "2")])
    g.label(0, 0, "0", dx=-1, dy=14, size=11)
    g.label(0, 1, "1", dx=-6, dy=-2, anchor="end", size=9)
    save("p5b_nsb", g)


if __name__ == "__main__":
    lesson()
    exercise()
    pastpaper()
