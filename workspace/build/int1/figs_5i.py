"""Figures for Lesson 5I and the Chapter 5 review (kept apart from figs.py, which the scaffold task owns;
same pattern as figs_5f.py and figs_5g.py, with the helpers copied so that this file stands alone).

Run: python3 workspace/build/int1/figs_5i.py   (writes svg/q5i_*.svg and svg/a5i_*.svg)

Curves are drawn in ink and regions shaded blue, as in the textbook (Ext 1 Y12, PDF 288).
Every label is checked against the SVG frame when the file is written (estimated text extents), and
against the lines and curves and the other labels; the script stops with an error if a label would be
clipped or would overlap something.
"""
import os
import re
import sys
from math import sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, OUT, ACC, INK  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import svg_overlap  # noqa: E402


def zero(_):
    return 0.0


# ---------------------------------------------------------------- labels with superscripts
def _esc(s):
    return s.replace("-", "−")


def rich(x, y, s, anchor="start", size=10.5, italic=True, color=INK):
    """Text with ^d superscripts (one digit) drawn as raised tspans. x, y: anchor point, y = text centre."""
    parts = re.split(r"\^(\d)", s)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            if p:
                out.append(_esc(p))
        else:
            out.append(f'<tspan dy="{-size * 0.38:.1f}" font-size="{size * 0.72:.1f}">{p}</tspan>'
                       f'<tspan dy="{size * 0.38:.1f}"> </tspan>')
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y + size * 0.35:.1f}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{color}"{st}>{"".join(out)}</text>')


def lab(g, x, y, s, dx=0, dy=0, anchor="start", size=10.5, italic=True):
    g.items.append(rich(g.X(x) + dx, g.Y(y) + dy, s, anchor, size, italic))
    return g


def num(g, x, y, s, dx=0, dy=0, anchor="middle", size=10.5):
    """Upright number or point label, e.g. '(1, 1)' or '-4'."""
    return lab(g, x, y, s, dx, dy, anchor, size, italic=False)


def seg(g, x0, y0, x1, y1, color="ink", width=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{d}/>')
    return g


def guide(g, x, y, xs=True, ys=True):
    """Dashed guides from a point to the axes."""
    if xs:
        g.vline(x, 0, y, color="faint", dash="3 3", width=1.0)
    if ys:
        g.hline(y, color="faint", dash="3 3", x0=0, x1=x, width=1.0)
    return g


def tick_x(g, x, h=3):
    g.items.append(f'<line x1="{g.X(x):.1f}" y1="{g.Y(0) - h:.1f}" x2="{g.X(x):.1f}" y2="{g.Y(0) + h:.1f}" stroke="{INK}" stroke-width="1.0" data-f="1"/>')
    return g


def tick_y(g, y, w=3):
    g.items.append(f'<line x1="{g.X(0) - w:.1f}" y1="{g.Y(y):.1f}" x2="{g.X(0) + w:.1f}" y2="{g.Y(y):.1f}" stroke="{INK}" stroke-width="1.0" data-f="1"/>')
    return g


# ---------------------------------------------------------------- frame check and save
def _text_boxes(svg):
    boxes = []
    for m in re.finditer(r'<text x="([-\d.]+)" y="([-\d.]+)" text-anchor="(\w+)" font-size="([\d.]+)"([^>]*)>(.*?)</text>', svg):
        body = m.group(6)
        x, y, anc, size = float(m.group(1)), float(m.group(2)), m.group(3), float(m.group(4))
        sups = re.findall(r'font-size="[\d.]+">([^<]*)</tspan>', body)
        plain = re.sub(r"<[^>]+>", "", body)
        n_sup = sum(len(s.replace(" ", "")) for s in sups)
        w = 0.0
        for ch in plain:
            w += size * (0.3 if ch in " ,.()|" else 0.6)
        w -= n_sup * size * 0.6 * 0.3          # superscripts are smaller
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anc]
        top = y - size * (1.05 if sups else 0.78)
        boxes.append((x0, top, x0 + w, y + size * 0.25, plain.replace(" ", "")))
    return boxes


def _segments(svg):
    segs = []
    for m in re.finditer(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"(?![^>]*data-f)', svg):
        segs.append(tuple(float(v) for v in m.groups()))
    for m in re.finditer(r'<polyline points="([^"]+)"', svg):
        pts = [tuple(float(v) for v in p.split(",")) for p in m.group(1).split()]
        segs += [(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:])]
    return segs


def _hits(box, sg):
    """Does the segment pass through the box (shrunk by 1 px)?"""
    x0, y0, x1, y1 = box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1
    ax, ay, bx, by = sg
    n = max(2, int(max(abs(bx - ax), abs(by - ay)) / 1.5))
    for i in range(n + 1):
        px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
        if x0 < px < x1 and y0 < py < y1:
            return True
    return False


SAVED = []


def save(name, g):
    svg = g.svg()
    boxes = _text_boxes(svg)
    msgs = []
    for x0, y0, x1, y1, s in boxes:
        if x0 < 0.5 or y0 < 0.5 or x1 > g.w - 0.5 or y1 > g.h - 0.5:
            msgs.append(f"CLIPPED label {s!r} in {name}: box ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f}) frame {g.w}x{g.h}")
    segs = _segments(svg)
    inner = [b for b in boxes if not re.fullmatch(r"[xy]", b[4])]   # the axis names sit at the arrow tips
    for b in inner:
        if any(_hits(b, sg) for sg in segs):
            msgs.append(f"OVERLAP label {b[4]!r} in {name} crosses a line or curve")
    for i, b in enumerate(boxes):
        for c in boxes[i + 1:]:
            if b[0] < c[2] - 1 and c[0] < b[2] - 1 and b[1] < c[3] - 1 and c[1] < b[3] - 1:
                msgs.append(f"OVERLAP labels {b[4]!r} and {c[4]!r} in {name}")
    msgs += [f"svg_overlap {name}: {p}" for p in svg_overlap.check_string(svg)]
    for msg in msgs:
        print(msg)
    if msgs and not os.environ.get("FIGS_WARN"):
        sys.exit("figure labels need fixing")
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    SAVED.append(name)


def graph(xr, yr, w, h, pad=(14, 30, 22, 18)):
    return Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=pad)


def ink(g, f, a, b, width=1.3):
    return g.curve(f, color="ink", width=width, x0=a, x1=b)


# ---------------------------------------------------------------- Chapter 5 review, Question 6
def review6():
    # a: the segment from (0, 0) to (2, 4), then y = 4 for 2 <= x <= 3, with the drop at x = 3
    g = graph((-1.0, 4.6), (-1.0, 5.0), 200, 150)
    g.axes()
    seg(g, 0, 0, 2, 4, width=1.3)
    seg(g, 2, 4, 3, 4, width=1.3)
    seg(g, 3, 4, 3, 0, width=1.3)
    g.vline(2, 0, 4, color="faint", dash="3 3", width=1.0).hline(4, color="faint", dash="3 3", x0=0, x1=2, width=1.0)
    num(g, 2, 0, "2", dy=11), num(g, 3, 0, "3", dy=11), num(g, 0, 4, "4", dx=-6, anchor="end")
    save("q5i_r6a", g)

    # b: the segment from (0, 2) to (3, -1), with the vertical line at x = 3
    g = graph((-1.0, 4.4), (-1.8, 2.8), 200, 150)
    g.axes()
    seg(g, 0, 2, 3, -1, width=1.3)
    seg(g, 3, -1, 3, 0, width=1.3)
    g.hline(-1, color="faint", dash="3 3", x0=0, x1=3, width=1.0)
    tick_x(g, 2), tick_x(g, 3), tick_y(g, 2), tick_y(g, -1)
    num(g, 2, 0, "2", dy=11, dx=-5), num(g, 3, 0, "3", dy=-10, dx=5), num(g, 0, 2, "2", dx=-6, anchor="end")
    num(g, 0, -1, "-1", dx=-6, anchor="end")
    save("q5i_r6b", g)


# ---------------------------------------------------------------- Chapter 5 review, Question 9
def review9():
    W, H = 160, 140
    # a: y = x^2, shaded from x = -3 to x = 1
    f = lambda x: x * x  # noqa: E731
    g = graph((-3.8, 2.6), (-0.9, 10.5), W, H)
    g.fill(f, zero, -3, 1)
    g.axes()
    ink(g, f, -3.2, 2.4)
    seg(g, -3, 0, -3, 9, width=1.0)
    seg(g, 1, 0, 1, 1, width=1.0)
    num(g, -3, 0, "-3", dy=11), num(g, 1, 0, "1", dy=11, dx=3)
    lab(g, 2.6, 7.2, "y = x^2", anchor="end", dx=0, size=10)
    save("q5i_r9a", g)

    # b: y = x^3 - 4x, shaded between the curve and the x-axis from x = -2 to x = 0
    f = lambda x: x ** 3 - 4 * x  # noqa: E731
    g = graph((-3.0, 3.0), (-5.5, 6.2), W, H)
    g.fill(f, zero, -2, 0)
    g.axes()
    ink(g, f, -2.62, 2.62)
    num(g, -2, 0, "-2", dy=-10, dx=-14), num(g, 2, 0, "2", dy=11, dx=5)
    lab(g, -0.3, 5.2, "y = x^3 - 4x", anchor="end", size=10)
    save("q5i_r9b", g)

    # c: y = x^2 - 4x + 3, shaded between the curve and the x-axis from x = 1 to x = 3
    f = lambda x: x * x - 4 * x + 3  # noqa: E731
    g = graph((-0.9, 5.0), (-1.6, 5.5), W, H)
    g.fill(zero, f, 1, 3)
    g.axes()
    ink(g, f, -0.45, 4.45)
    num(g, 1, 0, "1", dy=11, dx=-5), num(g, 3, 0, "3", dy=11, dx=5)
    lab(g, 0.25, 5.35, "y = x^2 - 4x + 3", anchor="start", size=9.5)
    save("q5i_r9c", g)

    # d: the line x = 2y - 6, shaded between the line, the y-axis and y = 4 (3 <= y <= 4)
    g = graph((-7.5, 3.6), (-1.0, 5.6), W, H)
    g.fill_y(lambda y: 2 * y - 6, zero, 3, 4)
    g.axes()
    ink(g, lambda x: (x + 6) / 2, -7.4, 3.4)
    seg(g, 0, 4, 2, 4, width=1.0)
    num(g, 0, 4, "4", dx=-6, anchor="end", dy=-3), num(g, 0, 3, "3", dx=5, dy=7, anchor="start")
    lab(g, 0.5, 5.25, "x = 2y - 6", anchor="start", size=10)
    save("q5i_r9d", g)

    # e: y = x^2 and y = x, shaded between them from x = 0 to x = 1
    f, l_ = (lambda x: x * x), (lambda x: x)
    g = graph((-1.7, 2.0), (-1.0, 2.9), W, H)
    g.fill(l_, f, 0, 1)
    g.axes()
    ink(g, f, -1.65, 1.68), ink(g, l_, -1.0, 1.95)
    tick_x(g, 1), tick_y(g, 1)
    g.dot(1, 1, r=2.2)
    num(g, 1, 1, "(1, 1)", dx=9, dy=4, anchor="start")
    lab(g, -0.3, 2.65, "y = x^2", anchor="end", size=10)
    lab(g, -0.95, -0.55, "y = x", anchor="end", dx=-6, size=10)
    save("q5i_r9e", g)

    # f: y = x^4 and y = x^2, shaded between them from x = -1 to x = 1
    f4, f2 = (lambda x: x ** 4), (lambda x: x * x)
    g = graph((-1.7, 1.9), (-0.35, 2.95), W, H)
    g.fill(f2, f4, -1, 1)
    g.axes()
    ink(g, f4, -1.25, 1.25), ink(g, f2, -1.5, 1.5)
    g.hline(1, color="faint", dash="3 3", x0=-1, x1=1, width=1.0)
    num(g, -1, 0, "-1", dy=11), num(g, 1, 0, "1", dy=11), num(g, 0, 1, "1", dx=-5, dy=-7, anchor="end")
    lab(g, 0.06, 2.8, "y = x^4", anchor="start", dx=4, size=9.5)
    lab(g, 1.5, 1.85, "y = x^2", anchor="start", dx=3, size=10)
    save("q5i_r9f", g)

    # g: y = x^2 and the line y = 3x - 2 through (1, 1) and (2, 4), shaded between them from x = 1 to x = 2
    f, l_ = (lambda x: x * x), (lambda x: 3 * x - 2)
    g = graph((-1.9, 3.0), (-2.6, 5.6), W, H)
    g.fill(l_, f, 1, 2)
    g.axes()
    ink(g, f, -1.85, 2.3), ink(g, l_, 0.05, 2.45)
    g.dot(1, 1, r=2.2).dot(2, 4, r=2.2)
    num(g, 1, 1, "(1, 1)", dx=9, dy=3, anchor="start")
    num(g, 2, 4, "(2, 4)", dx=-7, dy=-2, anchor="end")
    lab(g, -1.75, 4.6, "y = x^2", anchor="start", size=10)
    lab(g, 0.95, -2.0, "y = 3x - 2", anchor="start", dx=4, size=10)
    save("q5i_r9g", g)

    # h: y = x - 1 and y = 1 - x^2, meeting at (-2, -3) and (1, 0), shaded between them
    p, l_ = (lambda x: 1 - x * x), (lambda x: x - 1)
    g = graph((-2.8, 2.2), (-4.6, 2.8), W, H)
    g.fill(p, l_, -2, 1)
    g.axes()
    ink(g, p, -2.4, 2.02), ink(g, l_, -2.7, 2.2)
    g.vline(-2, -3, 0, color="faint", dash="3 3", width=1.0).hline(-3, color="faint", dash="3 3", x0=-2, x1=0, width=1.0)
    num(g, -2, 0, "-2", dy=-10, dx=-3), num(g, 1, 0, "1", dy=15, dx=-3), num(g, 0, -3, "-3", dx=5, dy=0, anchor="start")
    lab(g, 0.25, 2.45, "y = x - 1", anchor="start", size=10)
    lab(g, 2.6, -4.05, "y = 1 - x^2", anchor="end", size=10)
    save("q5i_r9h", g)


# ---------------------------------------------------------------- answer sketches
def answers():
    # Exercise 5I Q17(c): y = x sqrt(x^2 - 1), domain |x| >= 1, odd
    f = lambda x: x * sqrt(x * x - 1) if abs(x) >= 1 else None  # noqa: E731
    g = graph((-3.4, 3.4), (-9.5, 9.5), 220, 170, pad=(14, 34, 22, 16))
    g.axes()
    ink(g, f, -3.25, -1.0, width=1.6), ink(g, f, 1.0, 3.25, width=1.6)
    g.dot(-1, 0, r=2.4).dot(1, 0, r=2.4)
    num(g, -1, 0, "-1", dy=-12, dx=-10), num(g, 1, 0, "1", dy=11, dx=-3)
    g.vline(3, 0, 3 * sqrt(8), color="faint", dash="3 3", width=1.0)
    num(g, 3, 0, "3", dy=-10, dx=6)
    lab(g, -0.3, 8.0, "y = x√(x^2 - 1)", anchor="end", size=10)
    save("a5i_17c", g)

    # Exercise 5I Q18(a): y = x(7 - x^2)^3
    f = lambda x: x * (7 - x * x) ** 3  # noqa: E731
    r7 = sqrt(7)
    g = graph((-3.5, 3.5), (-260, 260), 230, 180, pad=(16, 34, 22, 18))
    g.axes()
    ink(g, f, -2.95, 2.95, width=1.6)
    for xs, ys in ((1, 216), (-1, -216), (r7, 0), (-r7, 0), (0, 0)):
        g.dot(xs, ys, r=2.4)
    g.hline(216, color="faint", dash="3 3", x0=0, x1=1, width=1.0).vline(1, 0, 216, color="faint", dash="3 3", width=1.0)
    g.hline(-216, color="faint", dash="3 3", x0=-1, x1=0, width=1.0).vline(-1, -216, 0, color="faint", dash="3 3", width=1.0)
    num(g, 1, 216, "(1, 216)", dy=-13)
    num(g, -1, -216, "(-1, -216)", dx=20, dy=13, anchor="end")
    num(g, r7, 0, "√7", dy=-11, dx=9), num(g, -r7, 0, "-√7", dy=-11, dx=-9)
    save("a5i_18a", g)

    # Chapter 5 review Q10(b): y = x^2 - 3x + 5 and y = x + 2, region between x = 1 and x = 3
    p, l_ = (lambda x: x * x - 3 * x + 5), (lambda x: x + 2)
    g = graph((-1.0, 4.3), (-0.8, 7.6), 200, 160)
    g.fill(l_, p, 1, 3)
    g.axes()
    ink(g, p, -0.55, 4.0, width=1.4), ink(g, l_, -0.9, 4.2, width=1.4)
    g.dot(1, 3, r=2.4).dot(3, 5, r=2.4)
    g.vline(1, 0, 3, color="faint", dash="3 3", width=1.0).vline(3, 0, 5, color="faint", dash="3 3", width=1.0)
    num(g, 1, 3, "(1, 3)", dx=6, dy=14, anchor="start"), num(g, 3, 5, "(3, 5)", dx=-7, dy=-8, anchor="end")
    num(g, 1, 0, "1", dy=11), num(g, 3, 0, "3", dy=11), num(g, 0, 5, "5", dx=5, dy=-8, anchor="start"), num(g, 0, 2, "2", dx=5, dy=9, anchor="start")
    lab(g, 0.15, 7.35, "y = x^2 - 3x + 5", anchor="start", size=10)
    lab(g, 3.15, 3.0, "y = x + 2", anchor="start", size=10)
    save("a5i_r10b", g)


if __name__ == "__main__":
    review6()
    review9()
    answers()
    print("wrote", len(SAVED), "figures:", " ".join(SAVED))
