"""Figures for Lesson 5G (kept apart from figs.py, which the scaffold task owns; same pattern as figs_5f.py).

Run: python3 workspace/build/int1/figs_5g.py   (writes svg/c5g_*.svg, svg/a5g_*.svg and svg/q5g_*.svg)

Curves are drawn in ink and regions shaded blue, as in the textbook (Ext 1 Y12, PDF 263-269).
Every label is checked against the SVG frame when the file is written (estimated text extents), so
that no label is clipped; the script stops with an error if one would be.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, OUT, ACC, INK  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from svg_overlap import check_string  # noqa: E402

SUP = {"2": "2", "3": "3", "4": "4", "6": "6"}


def zero(_):
    return 0.0


# ---------------------------------------------------------------- labels with superscripts and fractions
def _esc(s):
    return s.replace("-", "−")


def rich(x, y, s, anchor="start", size=10.5, italic=True, color=INK):
    """Text with ^d superscripts (one digit) drawn as raised tspans. x, y: anchor point, y = text centre."""
    parts = re.split(r"\^(\d)", s)
    out, raised = [], False
    for i, p in enumerate(parts):
        if i % 2 == 0:
            if p:
                out.append(f'<tspan dy="{size * 0.38:.1f}">{_esc(p)}</tspan>' if raised else _esc(p))
                raised = False
        else:
            out.append(f'<tspan dy="{-size * 0.38:.1f}" font-size="{size * 0.72:.1f}">{p}</tspan>')
            raised = True
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y + size * 0.35:.1f}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{color}"{st}>{"".join(out)}</text>')


def lab(g, x, y, s, dx=0, dy=0, anchor="start", size=10.5, italic=True):
    g.items.append(rich(g.X(x) + dx, g.Y(y) + dy, s, anchor, size, italic))
    return g


def num(g, x, y, s, dx=0, dy=0, anchor="middle", size=10.5):
    """Upright number or point label, e.g. '(1, 1)' or '-4'."""
    return lab(g, x, y, s, dx, dy, anchor, size, italic=False)


def fracpoint(g, x, y, a, b, c, d, dx=0, dy=0, size=10.5):
    """Point label (a/b, c/d) with stacked fractions; (dx, dy) moves its left edge from the point."""
    X0, Y0 = g.X(x) + dx, g.Y(y) + dy
    fs = size * 0.85
    it = []
    cur = X0

    def put(t, w):
        nonlocal cur
        it.append(f'<text x="{cur + w / 2:.1f}" y="{Y0 + size * 0.35:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}" data-f="1">{t}</text>')
        cur += w

    def frac(n_, m_):
        nonlocal cur
        w = max(len(n_), len(m_)) * fs * 0.6 + 3
        cx = cur + w / 2
        it.append(f'<text x="{cx:.1f}" y="{Y0 - 2.5:.1f}" text-anchor="middle" font-size="{fs:.1f}" fill="{INK}" data-f="1">{n_}</text>')
        it.append(f'<line x1="{cur + 0.5:.1f}" y1="{Y0:.1f}" x2="{cur + w - 0.5:.1f}" y2="{Y0:.1f}" stroke="{INK}" stroke-width="0.9" data-f="1"/>')
        it.append(f'<text x="{cx:.1f}" y="{Y0 + fs + 0.5:.1f}" text-anchor="middle" font-size="{fs:.1f}" fill="{INK}" data-f="1">{m_}</text>')
        cur += w

    put("(", size * 0.5)
    cur += 3
    frac(a, b)
    cur += 3
    put(",", size * 0.4)
    cur += 3
    frac(c, d)
    cur += 3
    put(")", size * 0.5)
    g.items.extend(it)
    g._fracboxes = getattr(g, "_fracboxes", []) + [(X0, Y0 - fs - 2, cur, Y0 + fs + 3)]
    return g


DIRS = {"e": (1, 0), "ne": (0.75, -0.75), "n": (0, -1), "nw": (-0.75, -0.75), "w": (-1, 0),
        "sw": (-0.75, 0.75), "s": (0, 1), "se": (0.75, 0.75)}


def _box_of(t):
    return _text_boxes(t)[0][:4]


def _problems(g):
    return set(check_string(g.svg()))


def place(g, x, y, s, prefer="e ne se n s w nw sw", size=10, italic=True, rmin=5, rmax=46):
    """Put label s near the data point (x, y): the first offset (rings of growing radius, directions in
    the order given) at which workspace/tools/svg_overlap.py finds no new problem (frame, strokes, dots,
    other labels, with its 2 px clearance)."""
    px, py = g.X(x), g.Y(y)
    base = _problems(g)
    order = prefer.split() + [d for d in DIRS if d not in prefer.split()]
    r = rmin
    while r <= rmax:
        for d in (prefer.split() if r < rmin + 12 else order):
            ux, uy = DIRS[d]
            anchor = "start" if ux > 0 else ("end" if ux < 0 else "middle")
            tx, ty = px + ux * r, py + uy * r
            if uy and not ux:
                ty += uy * size * 0.25
            g.items.append(rich(tx, ty, s, anchor, size, italic))
            if _problems(g) <= base:
                return g
            g.items.pop()
        r += 3
    print(f"  no free place for {s!r}")
    g.items.append(rich(px, py, s, "start", size, italic))
    return g


def pt(g, x, y, s=None, prefer="e ne se n s w nw sw", size=10, rmax=70):
    """Dot at (x, y) with its coordinates placed nearby (upright)."""
    g.dot(x, y, r=2.2)
    if s is None:
        s = f"({x:g}, {y:g})"
    return place(g, x, y, s, prefer, size, italic=False, rmin=4, rmax=rmax)


def seg(g, x0, y0, x1, y1, color="ink", width=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{d}/>')
    return g


def leader(g, x0, y0, x1, y1, width=0.9, head=5.5):
    """Arrow leader from a label at (x0, y0) to a curve at (x1, y1), data coordinates (as the textbook's)."""
    from math import atan2, cos, sin
    X0, Y0, X1, Y1 = g.X(x0), g.Y(y0), g.X(x1), g.Y(y1)
    g.items.append(f'<line x1="{X0:.1f}" y1="{Y0:.1f}" x2="{X1:.1f}" y2="{Y1:.1f}" stroke="{INK}" stroke-width="{width}"/>')
    a = atan2(Y1 - Y0, X1 - X0)
    p1 = (X1 - head * cos(a - 0.4), Y1 - head * sin(a - 0.4))
    p2 = (X1 - head * cos(a + 0.4), Y1 - head * sin(a + 0.4))
    g.items.append(f'<path d="M{X1:.1f},{Y1:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} z" fill="{INK}"/>')
    return g


def ycurve(g, fx, y0, y1, color="ink", width=1.3, n=300):
    """Draw x = fx(y) for y0 <= y <= y1."""
    pts = [f"{g.X(fx(y0 + (y1 - y0) * i / n)):.1f},{g.Y(y0 + (y1 - y0) * i / n):.1f}" for i in range(n + 1)]
    g.items.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ACC[color]}" '
                   f'stroke-width="{width}" stroke-linejoin="round"/>')
    return g


def guide(g, x, y, xs=True, ys=True):
    """Dashed guides from a point to the axes."""
    if xs:
        g.vline(x, 0, y, color="faint", dash="3 3", width=1.0)
    if ys:
        g.hline(y, color="faint", dash="3 3", x0=0, x1=x, width=1.0)
    return g


# ---------------------------------------------------------------- frame check and save
def _text_boxes(svg):
    boxes = []
    for m in re.finditer(r'<text x="([-\d.]+)" y="([-\d.]+)" text-anchor="(\w+)" font-size="([\d.]+)"([^>]*)>(.*?)</text>', svg):
        if "data-f" in m.group(5):
            continue
        body = m.group(6)
        x, y, anc, size, body = float(m.group(1)), float(m.group(2)), m.group(3), float(m.group(4)), body
        sups = re.findall(r'font-size="[\d.]+">([^<]*)</tspan>', body)
        plain = re.sub(r"<[^>]+>", "", body).replace(" ", "")
        n_sup = sum(len(s.replace(" ", "")) for s in sups)
        w = 0.0
        for ch in plain:
            w += size * (0.3 if ch in " ,.()|" else 0.6)
        w -= n_sup * size * 0.6 * 0.3          # superscripts are smaller
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anc]
        top = y - size * (1.05 if sups else 0.78)
        boxes.append((x0, top, x0 + w, y + size * 0.25, plain))
    return boxes


def _segments(svg):
    segs = []
    for m in re.finditer(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"(?![^>]*data-f)', svg):
        segs.append(tuple(float(v) for v in m.groups()))
    for m in re.finditer(r'<polyline points="([^"]+)"', svg):
        pts = [tuple(float(v) for v in p.split(",")) for p in m.group(1).split()]
        segs += [(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:])]
    return segs


def _hits(box, seg):
    """Does the segment pass through the box (shrunk by 1 px)?"""
    x0, y0, x1, y1 = box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1
    ax, ay, bx, by = seg
    n = max(2, int(max(abs(bx - ax), abs(by - ay)) / 1.5))
    for i in range(n + 1):
        px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
        if x0 < px < x1 and y0 < py < y1:
            return True
    return False


def save(name, g):
    svg = g.svg()
    msgs = check_string(svg)
    for msg in msgs:
        print(f"{name}: {msg}")
    if msgs and not os.environ.get("FIGS_WARN"):
        sys.exit("figure labels need fixing (workspace/tools/svg_overlap.py)")
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    SAVED.append(name)


SAVED = []


def graph(xr, yr, w, h, pad=(14, 30, 22, 18)):
    return Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=pad)


def ink(g, f, a, b, width=1.4):
    return g.curve(f, color="ink", width=width, x0=a, x1=b)


# ---------------------------------------------------------------- lesson figures
def lesson():
    # Example 28: y = x^2 and y = (x - 2)^2, region under both from 0 to 2
    f1, f2 = (lambda x: x * x), (lambda x: (x - 2) ** 2)
    g = graph((-1.6, 3.6), (-0.3, 3.0), 175, 140)
    g.fill(lambda x: min(f1(x), f2(x)), zero, 0, 2)
    g.axes()
    ink(g, f1, -1.48, 1.48), ink(g, f2, 0.52, 3.48)
    guide(g, 1, 1)
    g.dot(1, 1, r=2.4)
    num(g, 1, 0, "1", dy=11), num(g, 2, 0, "2", dy=11), num(g, 0, 1, "1", dx=-7, anchor="end")
    lab(g, -1.6, 2.68, "y = x^2", anchor="start", size=10)
    lab(g, 3.6, 2.68, "y = (x - 2)^2", anchor="end", size=10)
    save("c5g_e28", g)

    # Example 29: y = (x - 2)^2 and the line y = x, between x = 1 and x = 4
    f, l_ = (lambda x: (x - 2) ** 2), (lambda x: x)
    g = graph((-0.8, 5.0), (-0.8, 5.6), 170, 160)
    g.fill(l_, f, 1, 4)
    g.axes()
    ink(g, f, -0.25, 4.33), ink(g, l_, -0.7, 5.0)
    guide(g, 4, 4), guide(g, 1, 1)
    g.dot(1, 1, r=2.4).dot(4, 4, r=2.4)
    num(g, 1, 0, "1", dy=11, dx=-1), num(g, 2, 0, "2", dy=11), num(g, 4, 0, "4", dy=11)
    num(g, 0, 4, "4", dx=-6, anchor="end"), num(g, 0, 1, "1", dx=-6, anchor="end")
    place(g, 4.25, 5.06, "y = (x - 2)^2", prefer="w nw sw")
    lab(g, 4.3, 3.0, "y = x", anchor="start", size=10)
    save("c5g_e29", g)

    # Example 30: y = x^2 - 4x + 2 and y = x - 2, between x = 1 and x = 4
    f, l_ = (lambda x: x * x - 4 * x + 2), (lambda x: x - 2)
    g = graph((-0.8, 6.0), (-2.6, 3.6), 185, 150)
    g.fill(l_, f, 1, 4)
    g.axes()
    ink(g, f, -0.25, 4.3), ink(g, l_, -0.5, 5.4)
    g.vline(4, 0, 2, color="faint", dash="3 3", width=1.0).hline(2, color="faint", dash="3 3", x0=0, x1=4, width=1.0)
    g.vline(1, -1, 0, color="faint", dash="3 3", width=1.0).hline(-1, color="faint", dash="3 3", x0=0, x1=1, width=1.0)
    g.dot(1, -1, r=2.4).dot(4, 2, r=2.4)
    num(g, 1, 0, "1", dy=-9, dx=-4), num(g, 4, 0, "4", dy=11, dx=5)
    num(g, 0, 2, "2", dx=-6, anchor="end"), num(g, 0, -1, "-1", dx=-6, anchor="end")
    place(g, 2, 0, "2", prefer="nw n ne", italic=False, size=10.5, rmin=3)
    lab(g, 4.3, 3.45, "y = x^2 - 4x + 2", anchor="end", dx=-8, size=10)
    lab(g, 4.5, 0.9, "y = x - 2", anchor="start", size=10)
    save("c5g_e30", g)

    # Example 31: y = -x^2 + 4x - 4 and y = x^2 - 8x + 12, meeting at (2, 0) and (4, -4); region from x = 0 to 4
    p, q = (lambda x: -x * x + 4 * x - 4), (lambda x: x * x - 8 * x + 12)
    g = graph((-0.6, 7.6), (-5.4, 13.0), 205, 175)
    g.fill(lambda x: max(p(x), q(x)), lambda x: min(p(x), q(x)), 0, 4)
    g.axes()
    ink(g, p, -0.05, 4.6), ink(g, q, -0.05, 7.0)
    g.vline(4, -4, 0, color="faint", dash="3 3", width=1.0).hline(-4, color="faint", dash="3 3", x0=0, x1=4, width=1.0)
    g.dot(2, 0, r=2.4).dot(4, -4, r=2.4)
    num(g, 4, 0, "4", dy=-9, dx=5), num(g, 6, 0, "6", dy=11, dx=6)
    place(g, 2, 0, "2", prefer="ne n nw", italic=False, size=10.5, rmin=6)
    num(g, 0, 12, "12", dx=-6, anchor="end"), num(g, 0, -4, "-4", dx=-6, anchor="end")
    lab(g, 7.0, 11.2, "y = x^2 - 8x + 12", anchor="end", dx=-6, size=10)
    lab(g, 4.6, -4.9, "y = -x^2 + 4x - 4", anchor="start", dx=3, size=10)
    save("c5g_e31", g)

    # Box 17 tip: area under g minus area under f = area between (both above the x-axis)
    G, F = (lambda x: 3.4 - 0.3 * (x - 2) ** 2), (lambda x: 0.4 + 0.2 * x)
    for name, top, bot in (("c5g_sub1", G, zero), ("c5g_sub2", F, zero), ("c5g_sub3", G, F)):
        g = graph((-0.4, 4.4), (-0.3, 3.9), 128, 104, pad=(12, 26, 20, 18))
        g.fill(top, bot, 0.6, 3.6)
        g.axes()
        ink(g, G, 0.1, 4.2, 1.3), ink(g, F, 0.1, 4.2, 1.3)
        seg(g, 0.6, 0, 0.6, G(0.6) if top is G else F(0.6), width=0.9)
        seg(g, 3.6, 0, 3.6, G(3.6) if top is G else F(3.6), width=0.9)
        num(g, 0.6, 0, "a", dy=11), num(g, 3.6, 0, "b", dy=11)
        lab(g, 2.0, G(2.0), "g", anchor="middle", dy=-9, size=10.5)
        place(g, 4.2, F(4.2), "f", prefer="n nw ne", size=10.5, rmin=3)
        save(name, g)

    # Concept 4 demo and your turn: y = -(x - 1)^2 with a second parabola, region from the y-axis
    for name, q, c, Y, ytop, ybot in (("c5g_d4", lambda x: x * x - 8 * x + 7, 4, -9, 8.4, -10.6),
                                      ("c5g_y4", lambda x: x * x - 6 * x + 5, 3, -4, 6.2, -5.4)):
        p = lambda x: -(x - 1) ** 2  # noqa: E731
        g = graph((-0.6, c + 4.6), (ybot, ytop), 215, 170)
        g.fill(lambda x: max(p(x), q(x)), lambda x: min(p(x), q(x)), 0, c)
        g.axes()
        ink(g, p, -0.05, c + 0.55), ink(g, q, -0.05, c + 2.6)
        g.vline(c, Y, 0, color="faint", dash="3 3", width=1.0).hline(Y, color="faint", dash="3 3", x0=0, x1=c, width=1.0)
        g.dot(1, 0, r=2.4).dot(c, Y, r=2.4)
        num(g, c, 0, str(c), dy=-9, dx=5)
        place(g, 1, 0, "1", prefer="ne n", italic=False, size=10.5, rmin=6)
        num(g, 0, q(0), str(int(q(0))), dx=-6, anchor="end"), num(g, 0, Y, str(Y), dx=-6, anchor="end")
        lab(g, c + 4.6, ytop - 1.4, "y = x^2 - " + ("8x + 7" if c == 4 else "6x + 5"), anchor="end", dx=-4, size=10)
        place(g, c + 0.5, p(c + 0.5), "y = -x^2 + 2x - 1", prefer="e se s sw")
        save(name, g)


# ---------------------------------------------------------------- answer sketches for C1-C3
def answers():
    # C1: y = x^2 and y = (x - k)^2, region under both from 0 to k
    for name, k in (("a5g_c1d", 4), ("a5g_c1y", 6)):
        m = k / 2
        top = 1.2 * m * m
        f1, f2 = (lambda x: x * x), (lambda x, k=k: (x - k) ** 2)
        g = graph((-0.75 * k, 1.75 * k), (-0.08 * top, 1.45 * top), 175, 135)
        g.fill(lambda x: min(f1(x), f2(x)), zero, 0, k)
        g.axes()
        e = (top) ** 0.5
        ink(g, f1, -e, e), ink(g, f2, k - e, k + e)
        guide(g, m, m * m)
        num(g, k, 0, str(k), dy=11)
        pt(g, m, m * m, prefer="n ne nw e w")
        place(g, -e, top, "y = x^2", prefer="nw w n ne")
        place(g, k + e, top, f"y = (x - {k})^2", prefer="ne e n nw")
        save(name, g)

    # C2 and C3: line above a parabola
    specs = (("a5g_c2d", lambda x: (x - 3) ** 2, lambda x: x + 3, 1, 6, "y = (x - 3)^2", "y = x + 3", (-3.6, 11.5), (-2.6, 11.5), 3),
             ("a5g_c2y", lambda x: (x - 1) ** 2, lambda x: x + 1, 0, 3, "y = (x - 1)^2", "y = x + 1", (-3.0, 6.6), (-1.6, 6.0), 1),
             ("a5g_c3d", lambda x: x * x - 6 * x + 3, lambda x: x - 3, 1, 6, "y = x^2 - 6x + 3", "y = x - 3", (-3.6, 11.5), (-8.6, 5.5), 3),
             ("a5g_c3y", lambda x: x * x - 2 * x - 2, lambda x: x - 2, 0, 3, "y = x^2 - 2x - 2", "y = x - 2", (-3.0, 6.6), (-4.8, 2.8), 1))
    for name, f, l_, a, b, fl, ll, xr, yr, v in specs:
        g = graph(xr, yr, 215, 150)
        g.fill(l_, f, a, b)
        g.axes()
        cap = yr[1] - 0.12 * (yr[1] - yr[0])
        e = (cap - f(v)) ** 0.5
        ink(g, f, v - e, v + e), ink(g, l_, -1.0, b + 0.7)
        if a > 0:      # the left point is just right of the y-axis: label it left of the axis, with a leader
            g.dot(a, l_(a), r=2.2)
            num(g, -0.45, l_(a), f"({a}, {l_(a):g})", anchor="end", size=10)
            seg(g, -0.18, l_(a), a - 0.18, l_(a), width=0.8)
        else:
            pt(g, a, l_(a), prefer="w nw sw")
        pt(g, b, l_(b), prefer="w nw se e")
        place(g, v, f(v), fl, prefer="s se sw", rmin=6)
        place(g, b + 0.7, l_(b + 0.7), ll, prefer="se e s")
        save(name, g)


# ---------------------------------------------------------------- exercise figures
QW, QH = 150, 128


def finish(g, labels, pts):
    for (px, py, s, pref) in pts:
        pt(g, px, py, s, prefer=pref)
    for (px, py, s, pref) in labels:
        place(g, px, py, s, prefer=pref)


def q1():
    def two(name, xr, yr, top, bot, a, b, curves, labels, pts, w=QW, extra=()):
        g = graph(xr, yr, w, QH, pad=(10, 28, 20, 16))
        g.fill(top, bot, a, b)
        g.axes()
        for fn, x0, x1 in curves:
            ink(g, fn, x0, x1, 1.3)
        for (lx, ly, s_, anc, lead) in extra:
            lab(g, lx, ly, s_, anchor=anc, size=9.5 if lead or "+ 1" in s_ else 10)
            if lead:
                seg(g, *lead, width=0.8)
        finish(g, labels, pts)
        save(name, g)

    I = lambda x: x  # noqa: E731
    for nm, n_, xl in (("a", 2, 1.33), ("b", 3, 1.21), ("c", 4, 1.15)):
        two(f"q5g_1{nm}", (-0.9, 1.5), (-0.7, 1.9), I, lambda x, n_=n_: x ** n_, 0, 1,
            [(I, -0.7, 1.5), (lambda x, n_=n_: x ** n_, -0.92 if n_ % 2 == 0 else -0.85, xl)],
            [(0.45, 0.45, "y = x", "nw w n"), (0.75, 0.75 ** n_, f"y = x^{n_}", "se e s")], [(1, 1, "(1, 1)", "e se ne")])
    two("q5g_1d", (-0.9, 1.5), (-0.7, 1.9), lambda x: x * x, lambda x: x ** 3, 0, 1,
        [(lambda x: x * x, -0.92, 1.33), (lambda x: x ** 3, -0.85, 1.21)],
        [(1.1, 1.21, "y = x^2", "w nw sw"), (0.8, 0.512, "y = x^3", "se e s")], [(1, 1, "(1, 1)", "e se ne")])
    two("q5g_1e", (-1.3, 1.6), (-0.3, 2.0), lambda x: x ** 4, lambda x: x ** 6, 0, 1,
        [(lambda x: x ** 4, -1.17, 1.17), (lambda x: x ** 6, -1.11, 1.11)],
        [], [(1, 1, "(1, 1)", "nw w n")], extra=[(1.3, 1.5, "y = x^4", "start", None), (1.03, 0.3, "y = x^6", "start", None)])
    two("q5g_1f", (-4.4, 5.0), (-2.0, 19.0), lambda x: 3 * x + 4, lambda x: x * x, -1, 4,
        [(lambda x: x * x, -4.3, 4.3), (lambda x: 3 * x + 4, -1.7, 4.6)],
        [(3.2, 10.24, "y = x^2", "se e s")], [(-1, 1, "(-1, 1)", "w sw nw"), (4, 16, "(4, 16)", "w nw sw")], w=180,
        extra=[(-0.4, 17.3, "y = 3x + 4", "end", (-0.15, 15.2, 2.2, 10.7))])
    two("q5g_1g", (-6.4, 3.8), (-2.0, 21.0), lambda x: 9 - 2 * x, lambda x: x * x + 1, -4, 2,
        [(lambda x: x * x + 1, -4.4, 3.8), (lambda x: 9 - 2 * x, -4.6, 2.8)],
        [], [(-4, 17, "(-4, 17)", "ne e n"), (2, 5, "(2, 5)", "e se ne")], w=190, extra=[
            (0.25, 19.0, "y = 9 - 2x", "start", (1.2, 16.4, -0.4, 10.0)), (-5.9, 2.4, "y = x^2 + 1", "start", None)])
    two("q5g_1h", (-6.6, 3.6), (-2.5, 12.0), lambda x: 10 - x * x, lambda x: x + 4, -3, 2,
        [(lambda x: 10 - x * x, -3.6, 3.6), (lambda x: x + 4, -5.0, 3.6)],
        [(-2.2, 5.16, "y = 10 - x^2", "w nw sw"), (3.0, 7.0, "y = x + 4", "se e s n")], [(-3, 1, "(-3, 1)", "nw w n"), (2, 6, "(2, 6)", "e ne se")], w=180)


def q2():
    def yreg(name, xr, yr, right, left, c, d, curves, labels, pts, w=QW, extra=()):
        g = graph(xr, yr, w, QH, pad=(10, 28, 20, 16))
        g.fill_y(right, left, c, d)
        g.axes()
        for fx, y0, y1 in curves:
            ycurve(g, fx, y0, y1, width=1.3)
        for (lx, ly, s_, anc, lead) in extra:
            lab(g, lx, ly, s_, anchor=anc, size=10)
        finish(g, labels, pts)
        save(name, g)

    yreg("q5g_2a", (-0.8, 6.0), (-2.6, 3.2), lambda y: 2 * y, lambda y: y * y, 0, 2,
         [(lambda y: y * y, -2.4, 2.4), (lambda y: 2 * y, -0.35, 2.95)],
         [(5.4, 2.7, "x = 2y", "n nw ne w"), (4.4, -2.1, "x = y^2", "s sw w se")], [(4, 2, "(4, 2)", "s se sw e")])
    yreg("q5g_2b", (-0.8, 5.6), (-0.8, 2.6), lambda y: 3 * y - 2, lambda y: y * y, 1, 2,
         [(lambda y: y * y, -0.5, 2.3), (lambda y: 3 * y - 2, 0.2, 2.45)],
         [], [(1, 1, "(1, 1)", "se e s"), (4, 2, "(4, 2)", "nw n w")], extra=[(2.6, 2.15, "x = y^2", "end", None), (2.6, 1.15, "x = 3y - 2", "start", None)])
    yreg("q5g_2c", (-2.6, 3.8), (-0.6, 5.2), lambda y: 5 * y - y * y - 4, lambda y: 4 - y, 2, 4,
         [(lambda y: 5 * y - y * y - 4, 0.3, 4.7), (lambda y: 4 - y, -0.4, 5.0)],
         [(0, 3.1, "x = 4 - y", "w sw nw"), (-1.3, 0.7, "x = 5y - y^2 - 4", "s se sw")],
         [(2, 2, "(2, 2)", "e se ne"), (0, 4, "4", "w nw sw"), (0, 1, "1", "nw w n")], w=160)
    yreg("q5g_2d", (-0.8, 8.0), (-2.2, 3.0), lambda y: y + 4, lambda y: y * y + 2, -1, 2,
         [(lambda y: y * y + 2, -2.15, 2.4), (lambda y: y + 4, -2.1, 2.9)],
         [(6.9, 2.9, "y = x - 4", "n nw w"), (6.5, -2.1, "x = y^2 + 2", "s sw w")], [(3, -1, "(3, -1)", "w sw nw"), (6, 2, "(6, 2)", "w nw sw")])


def q3q4():
    # 3a: y = (x - 2)^2 and y = (x + 2)^2, region under both from -2 to 2
    f1, f2 = (lambda x: (x - 2) ** 2), (lambda x: (x + 2) ** 2)
    g = graph((-3.8, 3.8), (-0.4, 6.6), 200, 132, pad=(10, 28, 20, 18))
    g.fill(lambda x: min(f1(x), f2(x)), zero, -2, 2)
    g.axes()
    ink(g, f2, -3.8, 0.45, 1.3), ink(g, f1, -0.45, 3.8, 1.3)
    num(g, -2, 0, "-2", dy=11), num(g, 2, 0, "2", dy=11)
    place(g, 0.45, 6.0, "y = (x - 2)^2", prefer="e ne se")
    place(g, 0.95, 2.6, "y = (x + 2)^2", prefer="ne e n")
    save("q5g_3a", g)

    # 3b: y = x^2 and y = (x - 3)^2, meeting at (3/2, 9/4); point label and curve labels with leaders, as in the textbook
    f1, f2 = (lambda x: x * x), (lambda x: (x - 3) ** 2)
    g = graph((-1.9, 6.6), (-0.4, 6.6), 245, 132, pad=(10, 28, 20, 18))
    g.fill(lambda x: min(f1(x), f2(x)), zero, 0, 3)
    g.axes()
    ink(g, f1, -1.9, 2.35, 1.3), ink(g, f2, 0.65, 5.35, 1.3)
    g.dot(1.5, 2.25, r=2.2)
    num(g, 3, 0, "3", dy=11)
    fracpoint(g, -1.85, 5.9, "3", "2", "9", "4", size=10)
    seg(g, 0.15, 5.3, 1.42, 2.4, width=0.9)
    g.items.append(rich(g.X(2.62), g.Y(5.95), "y = x^2", "start", 10))
    leader(g, 2.66, 5.3, 2.08, 4.33)
    g.items.append(rich(g.X(4.6), g.Y(1.2), "y = (x - 3)^2", "start", 10))
    leader(g, 4.35, 1.32, 3.85, f2(3.85))
    save("q5g_3b", g)

    # 4a: rectangle 0 <= x <= 6, 0 <= y <= 3, less the region under y = 6x - x^2 - 8 from 2 to 4
    h = lambda x: 6 * x - x * x - 8  # noqa: E731
    g = graph((-0.6, 7.0), (-0.6, 4.8), 200, 132, pad=(14, 28, 20, 18))
    g.fill(lambda x: 3.0, lambda x: max(0.0, h(x)) if 2 <= x <= 4 else 0.0, 0, 6, n=400)
    g.axes()
    seg(g, 0, 3, 6, 3, width=1.3), seg(g, 6, 0, 6, 3, width=1.3)
    ink(g, h, 2, 4, 1.3)
    num(g, 2, 0, "2", dy=11), num(g, 4, 0, "4", dy=11), num(g, 6, 0, "6", dy=11)
    num(g, 0, 3, "3", dx=-6, anchor="end")
    lab(g, 3.1, 4.25, "y = 6x - x^2 - 8", anchor="start", dx=-10, size=10)
    seg(g, 3.3, 3.7, 3.05, 1.15, width=0.9)
    save("q5g_4a", g)

    # 4b: region between y = 4 - x^2 and y = 1 - x^2 above the x-axis
    t_, b_ = (lambda x: 4 - x * x), (lambda x: 1 - x * x)
    g = graph((-3.0, 3.0), (-3.4, 4.8), 200, 132, pad=(10, 28, 20, 18))
    g.fill(t_, lambda x: max(0.0, b_(x)), -2, 2)
    g.axes()
    ink(g, t_, -2.75, 2.75, 1.3), ink(g, b_, -2.05, 2.05, 1.3)
    num(g, -2, 0, "-2", dy=-9, dx=-8), num(g, 2, 0, "2", dy=-9, dx=7)
    num(g, -1, 0, "-1", dy=11, dx=9), num(g, 1, 0, "1", dy=11, dx=-7)
    place(g, 1.1, 2.79, "y = 4 - x^2", prefer="ne e n")
    place(g, 0.05, -2.9, "y = 1 - x^2", prefer="e", size=9.5, rmin=2)
    save("q5g_4b", g)


if __name__ == "__main__":
    lesson()
    answers()
    q1()
    q2()
    q3q4()
    print("wrote", len(SAVED), "figures; no label outside its frame or across a curve")
