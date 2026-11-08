"""Figures for Lesson 4J (kept apart from figs.py, which the scaffold task owns; same pattern as ch17/figs_17a.py).

Run: python3 workspace/build/int1/figs_4j.py   (writes svg/c4j_*.svg and svg/a4j_*.svg)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, save, ACC, INK, FAINT  # noqa: E402
from figfit import masked  # noqa: E402


def styled(g, width_mm):
    """Graph svg with an inline width (the answers stylesheet forces 88 mm on bare svgs)."""
    s = g.svg()
    return s.replace("<svg ", f'<svg style="width:{width_mm}mm;max-width:100%" ', 1)


def save_raw(name, text):
    from figfit import fit, flatten, untangle, separate  # panels in true coordinates; flagged labels nudged; frame grown if clipped
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg", name + ".svg")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(fit(untangle(separate(flatten(text)))))


def family():
    """Lesson: the family y = x^2 + C for C = 3, 0, -3, -6, with the member through (2, 7)."""
    g = Graph(-2.9, 2.9, -7, 9.2, w=230, h=230, pad=(30, 26, 16, 12))
    g.axes("x", "y")
    for c in (3, 0, -3, -6):
        col = "blue" if c == 3 else "ink"
        wid = 2.2 if c == 3 else 1.5
        g.curve(lambda x, c=c: x * x + c, color=col, width=wid, x0=-2.75, x1=2.75)
    g.hline(7, x0=0, x1=2).vline(2, 0, 7)
    g.dot(2, 7, color="blue")
    g.label(0, 7, "7", dx=-6, anchor="end", size=11)
    g.label(0, 3, "3", dx=-7, dy=-12, anchor="end", size=11)
    g.label(0, -3, "-3", dx=-7, dy=-12, anchor="end", size=11)
    g.label(0, -6, "-6", dx=-7, dy=-12, anchor="end", size=11)
    g.label(2, 0, "2", dy=12, dx=-8, size=11)
    save("c4j_family", g)


def q8_panel(f, members, special, xr, yr, title, clab, adx, ady, w=200, h=175):
    """One panel of Exercise 4J Q8: members y = f(x) + c for c in members, the member through A(1, 2) in blue."""
    g = Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=(24, 24, 22, 28))
    g.axes("x", "y")
    for c in members:
        col, wid = ("blue", 2.2) if c == special else ("ink", 1.3)
        if f.__name__ == "recip":
            g.curve(lambda x, c=c: f(x) + c, color=col, width=wid, x0=xr[0], x1=-0.02)
            g.curve(lambda x, c=c: f(x) + c, color=col, width=wid, x0=0.02, x1=xr[1])
        else:
            g.curve(lambda x, c=c: f(x) + c, color=col, width=wid)
    g.hline(2, x0=0, x1=1).vline(1, 0, 2)
    g.dot(1, 2, color="blue")
    g.label(1, 2, "A(1, 2)", dx=adx, dy=ady, anchor="start" if adx > 0 else "end", size=10, color="blue")
    g.items[-1] = masked(g.items[-1])        # the label sits over the family of curves
    if clab:
        g.label(clab[0], clab[1], clab[2], anchor="start", size=10, color="blue")
    g.items.append(f'<text x="{w / 2}" y="{h - 6}" text-anchor="middle" font-size="11.5" fill="{INK}">{title}</text>')
    return g


def q8():
    def neg4(x):
        return -2 * x * x

    def three(x):
        return 3 * x

    def cube(x):
        return x ** 3

    def recip(x):
        return 1 / x

    panels = [
        (neg4, (4, 0, -2), 4, (-2.4, 2.4), (-5, 5.6), "(a)  y = −2x² + C,  blue: C = 4", None, 7, -9),
        (three, (-1, 2, -4), -1, (-2.4, 2.4), (-5, 5.6), "(b)  y = 3x + C,  blue: C = −1", None, 8, 11),
        (cube, (1, 0, -2), 1, (-2, 2), (-5, 5.6), "(c)  y = x³ + C,  blue: C = 1", None, -7, -10),
        (recip, (1, 0, -1), 1, (-3, 3), (-5, 5.6), "(d)  y = x⁻¹ + C,  blue: C = 1", None, 8, 13),
    ]
    # titles with a fraction would be stacked by the label helper: keep plain text
    parts = []
    for i, (f, mem, sp, xr, yr, title, clab, adx, ady) in enumerate(panels):
        g = q8_panel(f, mem, sp, xr, yr, title, clab, adx, ady)
        inner = g.svg()
        body = inner[inner.index(">") + 1: inner.rindex("</svg>")]
        dx, dy = (i % 2) * 225, (i // 2) * 180
        parts.append(f'<g transform="translate({dx},{dy})">{body}</g>')
    W, H = 225 + 215, 180 + 175
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" style="width:130mm;max-width:100%" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" font-family="Inter, Arial, sans-serif">' + "".join(parts) + "</svg>")
    save_raw("a4j_q8", svg)


def q18():
    """Exercise 4J Q18: f(x) = 1/x + 1 for x > 0 and f(x) = 1/x + 3 for x < 0."""
    g = Graph(-4, 4, -3.2, 7, w=260, h=230, pad=(26, 26, 16, 10))
    g.axes("x", "y")
    g.hline(1, x0=0, x1=4).hline(3, x0=-4, x1=0)
    g.curve(lambda x: 1 / x + 3, color="blue", width=2.2, x0=-4, x1=-0.05)
    g.curve(lambda x: 1 / x + 1, color="blue", width=2.2, x0=0.05, x1=4)
    g.dot(1, 2).dot(-1, 2).dot(-1 / 3, 0)
    g.label(1, 2, "(1, 2)", dx=7, dy=-9, anchor="start", size=10)
    g.label(-1, 2, "(-1, 2)", dx=-8, dy=8, anchor="end", size=10)
    g.label(-1 / 3, 0, "-1/3", dx=-14, dy=18, size=10)
    g.label(0, 1, "1", dx=6, dy=9, anchor="start", size=10.5)
    g.label(0, 3, "3", dx=-6, dy=-8, anchor="end", size=10.5)
    g.label(3.9, 1, "y = 1", dy=10, anchor="end", size=9.5, color="faint")
    g.label(-3.9, 3, "y = 3", dy=-9, anchor="start", size=9.5, color="faint")
    save_raw("a4j_q18", styled(g, 66))


if __name__ == "__main__":
    family()
    q8()
    q18()
