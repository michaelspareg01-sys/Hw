"""Figures for Lesson 6K (kept apart from figs.py, which the scaffold task owns; same pattern as figs_6i.py).

Run: python3 workspace/build/int2/figs_6k.py   (writes svg/c6k_*.svg and svg/a6k_*.svg)
"""
import os
import sys
from math import e, log

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, ACC, INK  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(g.svg())


def zero(x):
    return 0


def rich(g, x, y, parts, dx=0, dy=0, anchor="start", size=12, color="ink"):
    """A label with italic letters, subscripts and superscripts.
    parts: list of (text, kind), kind 'r' roman, 'i' italic, 'sub' subscript (italic), 'sup' superscript (italic)."""
    X, Y = g.X(x) + dx, g.Y(y) + dy + size * 0.35
    out = [f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{ACC[color]}">']
    shift = 0
    for s, kind in parts:
        s = s.replace("-", "−")
        if kind in ("sub", "sup"):
            want = size * 0.32 if kind == "sub" else -size * 0.42
            out.append(f'<tspan dy="{want - shift:.1f}" font-size="{size * 0.72:.1f}" font-style="italic">{s}</tspan>')
            shift = want
        else:
            st = ' font-style="italic"' if kind == "i" else ""
            out.append(f'<tspan dy="{-shift:.1f}"{st}>{s}</tspan>')
            shift = 0
    out.append("</text>")
    g.items.append("".join(out))
    return g


def ylog(base):
    return [("y", "i"), (" = log", "r"), (base, "sub"), (" x", "i")]


def ypow(base, exp_="x"):
    return [("y", "i"), (f" = {base}", "r"), (exp_, "sup")]


def ex42():
    """Example 42: y = log_e x and its tangent y = x - 1 at the x-intercept (1, 0)."""
    g = Graph(-0.6, 3.4, -2.2, 1.7, w=230, h=190, pad=(26, 26, 16, 12))
    g.axes("x", "y")
    g.curve(log, color="ink", width=1.8, x0=0.11, x1=3.4)
    g.curve(lambda t: t - 1, color="ink", width=1.1, x0=-0.6, x1=2.6)
    g.hline(1, x0=0, x1=e).vline(e, 0, 1)
    g.xticks([(1, "1"), (2, "2")])
    g.label(e, 0, "e", dy=14, size=11, italic=True)
    g.yticks([(1, "1"), (-1, "-1")])
    rich(g, 1.25, -1.35, ylog("e"), size=12)
    save("c6k_ex42", g)


def area_fig(name, base, m, xmin=-1.4, xmax=1.5, curve_lab_at=(-1.35, 0.95)):
    """y = base^x and the line y = m x + 1, meeting at x = 0 and x = 1, with the region between them shaded."""
    ymax = base + 1
    g = Graph(xmin, xmax, -1.05, ymax, w=240, h=210, pad=(22, 26, 16, 10))
    g.fill(lambda t: m * t + 1, lambda t: base ** t, 0, 1)
    g.axes("x", "y")
    g.curve(lambda t: base ** t, color="ink", width=1.8)
    g.curve(lambda t: m * t + 1, color="ink", width=1.1)
    g.hline(base, x0=0, x1=1).vline(1, 0, base)
    if m == 1:
        g.xticks([(-1, "-1"), (1, "1")])
    else:
        g.xticks([(1, "1"), (-1 / m, "")])
        g.label(-1 / m, 0, f"-1/{m}", dx=11, dy=17, size=10)
    g.yticks([(base, str(base))])
    g.label(0, 1, "1", dx=-7, dy=-7, size=11)
    lx, ly = curve_lab_at
    rich(g, lx, ly, ypow(str(base)), size=12)
    rich(g, 0.06, -0.78, [("y", "i"), (" = ", "r"), ("x" if m == 1 else f"{m}x", "i"), (" + 1", "r")], size=12)
    save(name, g)


def q8():
    """Exercise 6K Q8(b): y = log_2 x, y = log_e x and y = log_4 x."""
    g = Graph(-0.3, 5.0, -2.3, 2.6, w=270, h=200, pad=(22, 62, 16, 12))
    g.axes("x", "y")
    for b in (2, e, 4):
        g.curve(lambda t, b=b: log(t) / log(b), color="ink", width=1.6, x0=0.2, x1=5.0)
    g.hline(1, x0=0, x1=4).vline(2, 0, 1).vline(e, 0, 1).vline(4, 0, 1)
    g.xticks([(1, "1"), (2, "2"), (4, "4")])
    g.label(e, 0, "e", dy=14, size=11, italic=True)
    g.yticks([(1, "1"), (-1, "-1"), (2, "2")])
    for b, t in ((2, "2"), (e, "e"), (4, "4")):
        rich(g, 5.0, log(5) / log(b), [("y", "i"), (" = log", "r"), (t, "sub"), (" x", "i")], dx=4, size=10.5)
    save("a6k_q8", g)


def q13():
    """Exercise 6K Q13: y = 2^x and y = 1 + 2x - x^2, meeting at A(0, 1) and B(1, 2)."""
    g = Graph(-1.4, 2.6, -1.4, 2.9, w=230, h=200, pad=(22, 26, 16, 12))
    g.fill(lambda t: 1 + 2 * t - t * t, lambda t: 2 ** t, 0, 1)
    g.axes("x", "y")
    g.curve(lambda t: 2 ** t, color="ink", width=1.8, x0=-1.4, x1=1.5)
    g.curve(lambda t: 1 + 2 * t - t * t, color="ink", width=1.1, x0=-0.5, x1=2.5)
    g.hline(2, x0=0, x1=1).vline(1, 0, 2)
    g.xticks([(1, "1"), (2, "2")])
    g.yticks([(2, "2")])
    g.label(0, 1, "1", dx=-7, dy=-8, size=11)
    g.label(0, 1, "A", dx=9, dy=8, size=11, italic=True)
    g.label(1, 2, "B", dx=-2, dy=-11, size=11, italic=True)
    rich(g, -1.35, 0.82, ypow("2"), size=11)
    rich(g, 1.5, 2.15, [("y", "i"), (" = 1 + 2", "r"), ("x", "i"), (" − ", "r"), ("x", "i"), ("2", "sup")], size=11)
    save("a6k_q13", g)


def q15():
    """Exercise 6K Q15(a): y = 3 - 3^x, intercepts (0, 2) and (1, 0), asymptote y = 3."""
    g = Graph(-2.6, 1.6, -1.3, 3.7, w=230, h=200, pad=(22, 26, 16, 12))
    g.fill(lambda t: 3 - 3 ** t, zero, 0, 1)
    g.axes("x", "y")
    g.curve(lambda t: 3 - 3 ** t, color="ink", width=1.8, x0=-2.6, x1=1.3)
    g.hline(3, x0=-2.6, x1=1.6)
    g.xticks([(1, "")])
    g.label(1, 0, "1", dx=-8, dy=13, size=11)
    g.yticks([(2, "2"), (3, "")])
    g.label(0, 3, "3", dx=-7, dy=-8, size=11)
    rich(g, -2.5, 3.3, [("y", "i"), (" = 3", "r")], size=11)
    rich(g, 0.75, 1.75, [("y", "i"), (" = 3 \u2212 3", "r"), ("x", "sup")], size=11)
    save("a6k_q15", g)


if __name__ == "__main__":
    ex42()
    area_fig("c6k_ex45", 2, 1, curve_lab_at=(-1.35, 1.05))
    area_fig("a6k_c6d", 3, 2)
    area_fig("a6k_c6y", 4, 3, xmax=1.4)
    q8()
    q13()
    q15()
