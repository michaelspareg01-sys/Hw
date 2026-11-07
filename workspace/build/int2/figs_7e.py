"""Figures for Lesson 7E and the review section (kept apart from figs.py, which the scaffold task owns;
same pattern as figs_6e.py and figs_7d.py).

Run: python3 workspace/build/int2/figs_7e.py
(writes svg/c7e_*.svg, svg/q7e_*.svg, svg/p7e_*.svg, svg/r7e_*.svg and svg/a7e_*.svg)

Every label is placed by a small search: each label has a list of candidate offsets, and the figure is
checked with workspace/tools/svg_overlap.py after each round. A label that is crossed by a stroke, overlaps
another label or a dot, or is clipped moves to its next candidate. Labels are drawn after all strokes. If a
label runs out of candidates it gets a small white background. The script prints any problem that is left.
"""
import os
import sys
import re
from math import sin, cos, tan, atan, acos, exp, pi, sqrt, e

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from figs import Graph, ACC, INK  # noqa: E402
import svg_overlap as SO  # noqa: E402

OUT = os.path.join(HERE, "svg")
LINE = "#cdd4dd"
MINUS = chr(0x2212)


def zero(x):
    return 0


def mn(s):
    return s.replace("-", MINUS)


# ---------------------------------------------------------------- graph with placed labels
SHIFTS = [(0, 0), (0, -8), (0, 8), (10, 0), (-10, 0), (10, -8), (-10, -8), (10, 8), (-10, 8), (0, -16), (0, 16),
          (20, 0), (-20, 0), (20, -10), (-20, -10), (20, 10), (-20, 10), (0, -24), (0, 24)]


class LG(Graph):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.labels = []

    def L(self, x, y, s, cands, kind="txt", anchor="middle", size=10.5, italic=False, power="", tail="",
          mask=False):
        """A label at graph point (x, y); cands is a list of (dx, dy) offsets (or (dx, dy, anchor))."""
        if kind == "frac":
            num, den = s.split("/")
            name = mn(num) + "/" + mn(den)
        elif kind == "sup":
            name = mn(s) + mn(power) + mn(tail)
        else:
            name = mn(s)
        self.labels.append(dict(X=self.X(x), Y=self.Y(y), s=s, cands=list(cands), i=0, kind=kind, anchor=anchor,
                                size=size, italic=italic, power=power, tail=tail, mask=mask, name=name))
        return self

    def near(self, x, y, s, dx, dy, anchor="middle", **k):
        """A curve or point label near (x, y) + (dx, dy), with the standard ring of nearby shifts."""
        return self.L(x, y, s, [(dx + a, dy + b) for a, b in SHIFTS], anchor=anchor, **k)

    def tick(self, v, s, below=True, size=10.5, mark=True):
        X = self.X(v)
        if mark:
            self.items.append(f'<line x1="{X:.1f}" y1="{self._y0 - 3:.1f}" x2="{X:.1f}" y2="{self._y0 + 3:.1f}" stroke="{INK}" stroke-width="1.1"/>')
        if not s:
            return self
        fr = "/" in s
        lo, hi = (13, -21) if fr else (12, -11)
        order = [lo, hi] if below else [hi, lo]
        c = []
        for dx in (0, 6, -6, 11, -11, 16, -16):
            for dy in order:
                c.append((dx, dy))
        return self.L(v, 0, s, c, kind="frac" if fr else "txt", size=size)

    def ytick(self, v, s, left=True, size=10.5, mark=True):
        Y = self.Y(v)
        if mark:
            self.items.append(f'<line x1="{self._x0 - 3:.1f}" y1="{Y:.1f}" x2="{self._x0 + 3:.1f}" y2="{Y:.1f}" stroke="{INK}" stroke-width="1.1"/>')
        if not s:
            return self
        fr = "/" in s
        w = (max(len(p) for p in s.split("/")) * size * 0.55 + 4) if fr else 0
        sides = [-1, 1] if left else [1, -1]
        c = []
        for dy in (0, -7, 7, -12, 12):
            for sd in sides:
                if fr:
                    c.append((sd * (w / 2 + 6), dy))
                else:
                    c.append((sd * 6, dy, "end" if sd < 0 else "start"))
        return self.L(0, v, s, c, kind="frac" if fr else "txt", size=size)

    def _render(self, lab):
        c = lab["cands"][min(lab["i"], len(lab["cands"]) - 1)]
        dx, dy = c[0], c[1]
        anc = c[2] if len(c) > 2 else lab["anchor"]
        X, Y, size = lab["X"] + dx, lab["Y"] + dy, lab["size"]
        out = []
        if lab["kind"] == "frac":
            num, den = (mn(p) for p in lab["s"].split("/"))
            w = max(len(num), len(den)) * size * 0.55 + 2
            if lab["mask"]:
                bw = max(SO.text_width(num, size), SO.text_width(den, size), w) + 4
                out.append(f'<rect x="{X - bw / 2:.1f}" y="{Y - 2 - 0.8 * size:.1f}" width="{bw:.1f}" height="{2.0 * size + 3:.1f}" fill="#fff"/>')
            out.append(f'<text x="{X:.1f}" y="{Y - 2:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}">{num}</text>')
            out.append(f'<line x1="{X - w / 2:.1f}" y1="{Y + 0.5:.1f}" x2="{X + w / 2:.1f}" y2="{Y + 0.5:.1f}" stroke="{INK}" stroke-width="0.8"/>')
            out.append(f'<text x="{X:.1f}" y="{Y + size + 0.5:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}">{den}</text>')
            return "".join(out)
        Yb = Y + size * 0.35
        st = ' font-style="italic"' if lab["italic"] else ''
        if lab["mask"]:
            wd = SO.text_width(lab["name"], size) + 4
            x0 = {"start": X - 2, "middle": X - wd / 2, "end": X - wd + 2}[anc]
            up, down = SO.text_extent(lab["name"], size)
            out.append(f'<rect x="{x0:.1f}" y="{Yb - up - 2:.1f}" width="{wd:.1f}" height="{up + down + 4:.1f}" fill="#fff"/>')
        if lab["kind"] == "sup":
            body = (mn(lab["s"]) + f'<tspan dy="{-size * 0.42:.1f}" font-size="{size * 0.72:.1f}">{mn(lab["power"])}</tspan>'
                    + (f'<tspan dy="{size * 0.42:.1f}">{mn(lab["tail"])}</tspan>' if lab["tail"] else ""))
        else:
            body = mn(lab["s"])
        out.append(f'<text x="{X:.1f}" y="{Yb:.1f}" text-anchor="{anc}" font-size="{size}" fill="{INK}" font-weight="500"{st}>{body}</text>')
        return "".join(out)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="Inter, Arial, sans-serif">' + "".join(self.items)
                + "".join(self._render(lab) for lab in self.labels) + "</svg>")


LEFT = []


def save(name, g, width_mm=None, rounds=80):
    """Place the labels, then write svg/<name>.svg."""
    for _ in range(rounds):
        probs = SO.check_string(g.svg())
        if not probs:
            break
        hit = set()
        for p in probs:
            hit.update(re.findall(r"'([^']*)'", p))
        moved = False
        for lab in getattr(g, "labels", []):
            if lab["name"] in hit:
                if lab["i"] + 1 < len(lab["cands"]):
                    lab["i"] += 1
                    moved = True
                elif not lab["mask"]:
                    lab["mask"] = True
                    lab["i"] = 0
                    moved = True
        if not moved:
            break
    s = g.svg()
    for p in SO.check_string(s):
        LEFT.append(f"{name}: {p}")
    if width_mm:
        s = s.replace("<svg ", f'<svg style="width:{width_mm}mm;max-width:100%" ', 1)
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(s)


# ---------------------------------------------------------------- shared shapes
def shade(g, f1, f2, a, b, opacity=0.3, color="blue"):
    g.fill(lambda t: max(f1(t), f2(t)), lambda t: min(f1(t), f2(t)), a, b, color=color, opacity=opacity)


def wave(name, f, xr, yr, a, b, ticks, label, lab_at, w=300, h=150, width_mm=None, pad=(18, 30, 18, 14),
         yt=((1, "1"), (-1, "-1")), curve_from=None):
    """One curve y = f(x) with the region between it and the x-axis shaded from a to b."""
    g = LG(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=pad)
    shade(g, f, zero, a, b)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=xr[0] + 0.05 if curve_from is None else curve_from, x1=xr[1] - 0.05)
    for v, s, below in ticks:
        g.tick(v, s, below)
    for v, s in yt:
        g.ytick(v, s)
    g.near(lab_at[0], lab_at[1], label, lab_at[2], lab_at[3], anchor=lab_at[4])
    save(name, g, width_mm)


def two(name, f1, f2, xr, yr, a, b, ticks, labels, w=300, h=160, width_mm=None, pad=(18, 30, 18, 14),
        yt=((1, "1"), (-1, "-1")), dots=(), vlines=(), hlines=(), x0=None, x1=None):
    """Two curves with the region between them shaded from a to b."""
    g = LG(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=pad)
    shade(g, f1, f2, a, b)
    g.axes("x", "y")
    for xv, y0, y1 in vlines:
        g.vline(xv, y0, y1)
    for yv, xa, xb in hlines:
        g.hline(yv, x0=xa, x1=xb)
    lo = xr[0] + 0.05 if x0 is None else x0
    hi = xr[1] - 0.05 if x1 is None else x1
    g.curve(f1, color="ink", width=1.6, x0=lo, x1=hi)
    g.curve(f2, color="ink", width=1.3, x0=lo, x1=hi)
    for xv, yv in dots:
        g.dot(xv, yv, r=2.4)
    for v, s, below in ticks:
        g.tick(v, s, below)
    for v, s in yt:
        g.ytick(v, s)
    for lx, ly, s, dx, dy, anc in labels:
        g.near(lx, ly, s, dx, dy, anchor=anc)
    save(name, g, width_mm)


# ---------------------------------------------------------------- lesson
def lesson():
    # Worked example 24: y = cos x/2 on [0, 4 pi], all three pieces shaded
    wave("c7e_ex24", lambda t: cos(t / 2), (-0.9, 4 * pi + 0.9), (-1.35, 1.45), 0, 4 * pi,
         [(pi, "π", False), (2 * pi, "2π", False), (3 * pi, "3π", True), (4 * pi, "4π", True)],
         "y = cos ½x", (4 * pi + 0.6, cos((4 * pi + 0.6) / 2), -2, -13, "end"), w=290, h=140, curve_from=-0.6)
    # Worked example 25: y = sin x and y = sin 2x on [0, pi], region on [0, pi/3]
    two("c7e_ex25", sin, lambda t: sin(2 * t), (-0.45, pi + 0.55), (-1.3, 1.45), 0, pi / 3,
        [(pi / 4, "π/4", True), (pi / 3, "π/3", True), (pi / 2, "π/2", True), (3 * pi / 4, "3π/4", False),
         (pi, "π", False)],
        [(pi / 2, 1, "y = sin x", 4, -10, "start"), (3 * pi / 4, -1, "y = sin 2x", 8, 8, "start")],
        w=290, h=170, vlines=((pi / 3, 0, sin(pi / 3)),), hlines=((1, 0, pi / 2),), x0=-0.35, x1=pi + 0.4)


# ---------------------------------------------------------------- textbook exercise 7E
def small_wave(name, f, xr, yr, a, b, ticks, label, lab_at, yt=((1, "1"), (-1, "-1")), w=210, h=135, edges=()):
    g = LG(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=(18, 26, 18, 12))
    shade(g, f, zero, a, b)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=xr[0] + 0.15, x1=xr[1] - 0.1)
    for xv in edges:
        g.vline(xv, 0, f(xv), color="ink", dash="")
    for v, s, below in ticks:
        g.tick(v, s, below)
    for v, s in yt:
        g.ytick(v, s)
    g.near(lab_at[0], lab_at[1], label, lab_at[2], lab_at[3], anchor=lab_at[4])
    save(name, g)


def exercise():
    # Q4a: y = sin x, shaded from pi/6 to pi/2
    small_wave("q7e_q4a", sin, (-0.6, pi + 0.5), (-1.3, 1.4), pi / 6, pi / 2,
               [(pi / 6, "π/6", True), (pi / 2, "π/2", True), (pi, "π", True)], "y = sin x",
               (pi / 2, 1, 6, -10, "start"), edges=(pi / 6, pi / 2))
    # Q4b: y = cos x, shaded from 2pi/3 to pi (below the axis)
    small_wave("q7e_q4b", cos, (-0.6, pi + 0.6), (-1.3, 1.4), 2 * pi / 3, pi,
               [(pi / 2, "π/2", True), (2 * pi / 3, "2π/3", False), (pi, "π", False)], "y = cos x",
               (0.3, 1, 8, -8, "start"), edges=(2 * pi / 3, pi))
    # Q6a: sin x and cos x, shaded between them from pi/4 to pi/2
    two("q7e_q6a", sin, cos, (-0.7, pi + 0.55), (-1.3, 1.45), pi / 4, pi / 2,
        [(pi / 4, "π/4", True), (pi / 2, "π/2", True), (pi, "π", True)],
        [(pi / 2, 1, "y = sin x", 6, -9, "start"), (pi * 0.8, cos(pi * 0.8), "y = cos x", 0, 13, "middle")],
        w=220, h=145, vlines=((pi / 2, 0, 1),))
    # Q6b: sin x and sin 2x, shaded from 0 to pi/3, dot at (pi, 0)
    two("q7e_q6b", sin, lambda t: sin(2 * t), (-0.45, pi + 0.55), (-1.3, 1.45), 0, pi / 3,
        [(pi / 3, "π/3", True), (pi / 2, "π/2", True), (pi, "π", True)],
        [(pi / 2, 1, "y = sin x", 8, -10, "start"), (3 * pi / 4, -1, "y = sin 2x", 4, 9, "start")],
        w=220, h=145, dots=((pi, 0),), vlines=((pi / 3, 0, sin(pi / 3)),))
    # Q6c: y = x and y = sin x, shaded from 0 to pi/2
    g = LG(-0.75, pi + 0.5, -1.3, 2.3, w=220, h=155, pad=(26, 26, 18, 12))
    g.fill(lambda t: t, sin, 0, pi / 2, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(lambda t: t, color="ink", width=1.3, x0=-0.75, x1=2.2)
    g.curve(sin, color="ink", width=1.6, x0=-0.7, x1=pi + 0.45)
    g.vline(pi / 2, 0, pi / 2, color="ink", dash="").hline(pi / 2, x0=0, x1=pi / 2)
    g.tick(pi / 2, "π/2").tick(pi, "π")
    g.ytick(1, "1").ytick(pi / 2, "π/2").ytick(-1, "-1")
    g.near(2.0, 2.0, "y = x", 6, 4, anchor="start")
    g.near(2.2, sin(2.2), "y = sin x", 4, -12, anchor="start")
    save("q7e_q6c", g)
    # Q6d: y = 1 and y = cos x from -pi/2 to pi/2
    two("q7e_q6d", lambda t: 1, cos, (-2.2, 2.2), (-0.75, 1.5), -pi / 2, pi / 2,
        [(-pi / 2, "-π/2", True), (pi / 2, "π/2", True)],
        [(-pi / 2, 1, "y = 1", -2, -9, "end"), (-2.0, cos(-2.0), "y = cos x", 6, 13, "start")],
        w=220, h=135, yt=((1, "1"),), vlines=((-pi / 2, 0, 1), (pi / 2, 0, 1)))
    # Q7a: below both y = sin x and y = cos x, from 0 to pi/2
    g = LG(-0.7, pi + 0.55, -1.3, 1.45, w=220, h=145, pad=(18, 26, 18, 12))
    g.fill(lambda t: min(sin(t), cos(t)), zero, 0, pi / 2, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(sin, color="ink", width=1.6, x0=-0.65, x1=pi + 0.5)
    g.curve(cos, color="ink", width=1.3, x0=-0.65, x1=pi + 0.5)
    g.tick(pi / 4, "").tick(pi / 2, "π/2").tick(pi, "π")
    g.ytick(1, "1").ytick(-1, "-1")
    g.near(pi / 2, 1, "y = sin x", 8, -9, anchor="start")
    g.near(pi * 0.8, cos(pi * 0.8), "y = cos x", 0, 13)
    save("q7e_q7a", g)
    # Q7b: y = x + 1 and y = cos x, region above the x-axis from -1 to pi/2
    g = LG(-2.2, 2.2, -1.5, 1.9, w=220, h=155, pad=(18, 26, 18, 12))
    g.fill(lambda t: t + 1 if t < 0 else cos(t), zero, -1, pi / 2, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(lambda t: t + 1, color="ink", width=1.3, x0=-2.2, x1=0.85)
    g.curve(cos, color="ink", width=1.6, x0=-2.2, x1=2.2)
    g.tick(-pi / 2, "-π/2", below=False).tick(-1, "-1").tick(pi / 2, "π/2")
    g.ytick(1, "1")
    g.near(0.8, 1.8, "y = x + 1", 6, 2, anchor="start")
    g.near(0.8, cos(0.8), "y = cos x", 10, -2, anchor="start")
    save("q7e_q7b", g)
    # Q11: arch window y = 3 cos(pi x / 2), -1 <= x <= 1
    g = LG(-1.5, 1.5, -0.4, 3.5, w=180, h=150, pad=(16, 32, 18, 14))
    g.axes("x", "y")
    g.curve(lambda t: 3 * cos(pi * t / 2), color="ink", width=1.6, x0=-1, x1=1)
    g.dot(-1, 0, r=2.6).dot(1, 0, r=2.6)
    g.tick(-1, "-1", mark=False).tick(1, "1", mark=False)
    g.near(0, 3, "3", -5, -9, anchor="end")
    save("q7e_q11", g)


# ---------------------------------------------------------------- past papers
def grid(g, xs, ys, color=LINE, width=0.6):
    for xv in xs:
        g.items.insert(0, f'<line x1="{g.X(xv):.1f}" y1="{g.Y(g.ymin):.1f}" x2="{g.X(xv):.1f}" y2="{g.Y(g.ymax):.1f}" stroke="{color}" stroke-width="{width}"/>')
    for yv in ys:
        g.items.insert(0, f'<line x1="{g.X(g.xmin):.1f}" y1="{g.Y(yv):.1f}" x2="{g.X(g.xmax):.1f}" y2="{g.Y(yv):.1f}" stroke="{color}" stroke-width="{width}"/>')


def pp():
    # Fort Street 2020 Q10: y = sin x and y = cos x, region between A and B shaded
    g = LG(-0.25, 2 * pi + 0.5, -2.4, 2.4, w=270, h=175, pad=(22, 26, 18, 12))
    g.fill(sin, cos, pi / 4, 5 * pi / 4, color="rose", opacity=0.14)
    g.axes("x", "y")
    g.curve(sin, color="rose", width=1.8, x0=0, x1=2 * pi)
    g.curve(cos, color="amber", width=1.3, x0=0, x1=2 * pi)
    g.dot(pi / 4, sqrt(0.5), r=2.4).dot(5 * pi / 4, -sqrt(0.5), r=2.4)
    for v, s in ((pi / 2, "π / 2"), (pi, "π"), (3 * pi / 2, "3π / 2"), (2 * pi, "2π")):
        g.tick(v, s, size=10)
    for v in (2, 1, -1, -2):
        g.ytick(v, str(v), size=10)
    g.L(0, 0, "0", [(-6, 8, "end"), (-6, 11, "end"), (-9, 8, "end")], size=10)
    g.near(pi / 4, sqrt(0.5), "A", -3, -12, size=11)
    g.near(5 * pi / 4, -sqrt(0.5), "B", 1, 12, size=11)
    g.near(1.35, 1.0, "y = sin x", 0, -12, anchor="start", italic=True)
    g.near(4.9, 1.0, "y = cos x", 0, -12, anchor="start", italic=True)
    save("p7e_fs", g)

    # Caringbah 2021 Q12(c): f(x) = 2 cos^-1 (x/3) on graph paper, no numbers on the axes
    g = LG(-4, 4.4, -4.5, 8, w=260, h=200, pad=(10, 14, 10, 8))
    grid(g, [k for k in range(-4, 5)], [k for k in range(-4, 9)])
    y0, x0 = g.Y(0), g.X(0)
    g.items.append(f'<line x1="{g.X(g.xmin):.1f}" y1="{y0:.1f}" x2="{g.X(g.xmax) + 4:.1f}" y2="{y0:.1f}" stroke="{INK}" stroke-width="1.3"/>')
    g.items.append(f'<path d="M{g.X(g.xmax) + 6:.1f},{y0:.1f} l-6,-3 v6 z" fill="{INK}"/>')
    g.items.append(f'<line x1="{x0:.1f}" y1="{g.Y(g.ymin):.1f}" x2="{x0:.1f}" y2="{g.Y(g.ymax):.1f}" stroke="{INK}" stroke-width="1.3"/>')
    g.curve(lambda t: 2 * acos(t / 3) if abs(t) <= 3 else None, color="ink", width=1.9, x0=-3, x1=3, n=800)
    g.L(4.4, 0, "x axis", [(-2, 9, "end"), (-2, -9, "end")], size=7.5, mask=True)
    g.L(0, 8, "y axis", [(4, 6, "start"), (-4, 6, "end")], size=7.5, mask=True)
    save("p7e_car", g)

    # Hornsby Girls 2023 Q14(b): y = 2 cos^-1 (x + 1/2), region in the first quadrant shaded
    g = LG(-1.4, 1.4, -0.85, 4.95, w=250, h=190, pad=(10, 16, 10, 10))
    grid(g, [k / 8 for k in range(-11, 12)], [k * pi / 8 for k in range(-2, 13)], color="#e3e8ee", width=0.5)
    grid(g, [-1, -0.5, 0.5, 1], [pi / 2, pi, 3 * pi / 2], color="#b8c1cc", width=0.7)
    f = lambda t: 2 * acos(t + 0.5)  # noqa: E731
    g.fill(f, zero, 0, 0.5, color="blue", opacity=0.35)
    y0, x0 = g.Y(0), g.X(0)
    g.items.append(f'<line x1="{g.X(-1.4):.1f}" y1="{y0:.1f}" x2="{g.X(1.4):.1f}" y2="{y0:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    g.items.append(f'<line x1="{x0:.1f}" y1="{g.Y(-0.85):.1f}" x2="{x0:.1f}" y2="{g.Y(4.95):.1f}" stroke="{INK}" stroke-width="1.2"/>')
    g.curve(f, color="blue", width=1.8, x0=-1.2071, x1=0.5, n=800)
    for v, s in ((-1, "-1"), (-0.5, "-0.5"), (0, "0"), (0.5, "0.5"), (1, "1")):
        g.L(v, 0, s, [((-5 if v == 0 else 0), 8)], size=7.5, mask=True)
    for v, s in ((pi / 2, "π/2"), (pi, "π"), (3 * pi / 2, "3π/2")):
        g.L(0, v, s.replace("/", "∕"), [(-2, 0, "end")], size=7.5, mask=True)
    save("p7e_hgs", g, 56)


# ---------------------------------------------------------------- review figures (Chapter 6 and Chapter 7)
def review():
    # Ch 6 review Q22a: y = e^{2x}, shaded from 0 to 1
    g = LG(-1.6, 1.6, -0.6, 8.2, w=200, h=155, pad=(18, 50, 18, 12))
    g.fill(lambda t: exp(2 * t), zero, 0, 1, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(lambda t: exp(2 * t), color="ink", width=1.6, x0=-1.6, x1=1.04)
    g.vline(1, 0, exp(2), color="ink", dash="")
    g.tick(1, "1")
    g.near(0, 1, "1", -5, -7, anchor="end")
    g.near(1.04, 7.4, "y = e", 8, 0, anchor="start", kind="sup", power="2x")
    save("r7e_6q22a", g)
    # Ch 6 review Q22b: y = 1 - e^{-x}, shaded from 0 to 1, asymptote y = 1
    g = LG(-1.4, 2.2, -1.6, 1.5, w=195, h=155, pad=(18, 26, 18, 12))
    f = lambda t: 1 - exp(-t)  # noqa: E731
    g.fill(f, zero, 0, 1, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.hline(1)
    g.curve(f, color="ink", width=1.6, x0=-0.93, x1=2.2)
    g.vline(1, 0, f(1), color="ink", dash="")
    g.tick(1, "1")
    g.near(0, 1, "1", -5, -7, anchor="end")
    g.near(0.2, -1.1, "y = 1 - e", 4, 0, anchor="start", kind="sup", power="-x")
    save("r7e_6q22b", g)
    # Ch 6 review Q23a: y = e^{2x} - 1, shaded from -1 to 0 (below the axis), asymptote y = -1
    g = LG(-1.9, 1.3, -1.6, 2.2, w=195, h=155, pad=(18, 26, 18, 12))
    f = lambda t: exp(2 * t) - 1  # noqa: E731
    g.fill(zero, f, -1, 0, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.hline(-1)
    g.curve(f, color="ink", width=1.6, x0=-1.9, x1=0.57)
    g.vline(-1, 0, f(-1), color="ink", dash="")
    g.tick(-1, "-1", below=False)
    g.near(0, -1, "-1", -5, 8, anchor="end")
    g.near(0.5, 1.6, "y = e", -10, 0, anchor="end", kind="sup", power="2x", tail=" - 1")
    save("r7e_6q23a", g)
    # Ch 6 review Q23b: y = e^x - 1 and y = (e - 1)x, shaded from 0 to 1
    g = LG(-1.9, 1.55, -1.75, 2.4, w=235, h=185, pad=(70, 26, 18, 12))
    f = lambda t: exp(t) - 1  # noqa: E731
    gl = lambda t: (e - 1) * t  # noqa: E731
    g.fill(gl, f, 0, 1, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.hline(-1)
    g.vline(1, 0, e - 1).hline(e - 1, x0=0, x1=1)
    g.curve(f, color="ink", width=1.6, x0=-1.7, x1=1.2)
    g.curve(gl, color="ink", width=1.3, x0=-0.8, x1=1.35)
    g.tick(1, "1")
    g.near(0, e - 1, "e - 1", -5, 0, anchor="end")
    g.near(-1.25, exp(-1.25) - 1, "y = e", 0, -12, kind="sup", power="x", tail=" - 1")
    g.near(-0.8, -(e - 1) * 0.8, "y = (e - 1)x", -4, 2, anchor="end")
    save("r7e_6q23b", g)
    # Ch 7 review Q10a: y = cos x and y = cos 2x from 0 to pi/2, region above the x-axis between them
    g = LG(-0.35, 2.15, -0.45, 1.3, w=210, h=145, pad=(18, 26, 18, 12))
    g.fill(cos, lambda t: max(cos(2 * t), 0), 0, pi / 2, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.curve(cos, color="ink", width=1.6, x0=0, x1=2.05)
    g.curve(lambda t: cos(2 * t), color="ink", width=1.3, x0=0, x1=pi / 4 + 0.12)
    g.tick(pi / 4, "π/4").tick(pi / 2, "π/2")
    g.ytick(1, "1")
    g.near(0.95, cos(0.95), "y = cos x", 6, -8, anchor="start")
    g.near(0.92, -0.3, "y = cos 2x", 0, 0, anchor="start")
    save("r7e_7q10a", g)
    # Ch 7 review Q10b: y = cos x and y = cos 2x from 0 to 2pi/3
    two("r7e_7q10b", cos, lambda t: cos(2 * t), (-0.35, pi + 0.45), (-1.35, 1.45), 0, 2 * pi / 3,
        [(pi / 4, "π/4", False), (pi / 2, "π/2", True), (2 * pi / 3, "2π/3", True), (3 * pi / 4, "3π/4", False),
         (pi, "π", True)],
        [(2.4, cos(2.4), "y = cos x", 6, 12, "start"), (2.75, cos(5.5), "y = cos 2x", 2, -12, "end")],
        w=260, h=165, hlines=((-1, 0, pi / 2),), vlines=((2 * pi / 3, 0, -0.5),), x0=0)
    # Ch 7 review Q11: y = tan x, shaded from 0 to pi/4, asymptote x = pi/2
    g = LG(-0.3, 1.85, -0.3, 2.4, w=180, h=160, pad=(18, 26, 18, 22))
    g.fill(tan, zero, 0, pi / 4, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.vline(pi / 2, -0.3, 2.4)
    g.hline(1, x0=0, x1=pi / 4)
    g.curve(tan, color="ink", width=1.6, x0=0, x1=atan(2.35))
    g.vline(pi / 4, 0, 1, color="ink", dash="")
    g.tick(pi / 4, "π/4").tick(pi / 2, "π/2")
    g.near(0, 1, "1", -5, 0, anchor="end")
    g.near(atan(2.35), 2.35, "y = tan x", -6, -2, anchor="end")
    save("r7e_7q11", g)


# ---------------------------------------------------------------- answers
def answers():
    # C1 tutor demo: y = cos x/3 on [0, 6 pi]; your turn: y = cos 2x on [0, pi]
    wave("a7e_c1d", lambda t: cos(t / 3), (-1.2, 6 * pi + 1.2), (-1.35, 1.45), 0, 6 * pi,
         [(3 * pi / 2, "3π/2", False), (3 * pi, "3π", False), (9 * pi / 2, "9π/2", True), (6 * pi, "6π", True)],
         "y = cos ⅓x", (6 * pi + 0.9, cos((6 * pi + 0.9) / 3), -2, -13, "end"), w=300, h=145, width_mm=72,
         curve_from=-0.9)
    wave("a7e_c1y", lambda t: cos(2 * t), (-0.3, pi + 0.35), (-1.35, 1.45), 0, pi,
         [(pi / 4, "π/4", False), (pi / 2, "π/2", True), (3 * pi / 4, "3π/4", False), (pi, "π", True)],
         "y = cos 2x", (pi, 1, 4, -8, "end"), w=260, h=145, width_mm=62, curve_from=-0.2)
    # C2 tutor demo: sin x and sin 2x, region on [pi/3, pi]; your turn: cos x and sin 2x, region on [0, pi/6]
    two("a7e_c2d", sin, lambda t: sin(2 * t), (-0.45, pi + 0.55), (-1.3, 1.45), pi / 3, pi,
        [(pi / 3, "π/3", True), (pi / 2, "π/2", True), (3 * pi / 4, "3π/4", False), (pi, "π", False)],
        [(pi / 2, 1, "y = sin x", 4, -10, "start"), (3 * pi / 4, -1, "y = sin 2x", 8, 8, "start")],
        w=270, h=175, width_mm=62, vlines=((pi / 3, 0, sin(pi / 3)),), x0=-0.35, x1=pi + 0.4)
    two("a7e_c2y", cos, lambda t: sin(2 * t), (-0.3, pi / 2 + 0.45), (-0.3, 1.4), 0, pi / 6,
        [(pi / 6, "π/6", True), (pi / 4, "π/4", True), (pi / 2, "π/2", True)],
        [(0.05, 1.0, "y = cos x", 6, -8, "start"), (pi / 4, 1, "y = sin 2x", 10, -6, "start")],
        w=240, h=160, width_mm=56, yt=((1, "1"),), vlines=((pi / 6, 0, cos(pi / 6)),), x0=-0.2, x1=pi / 2 + 0.3)
    # C3 tutor demo: sin x and -cos x on [0, 2pi]; your turn: sin x and cos x on [-pi, pi]
    two("a7e_c3d", sin, lambda t: -cos(t), (-0.4, 2 * pi + 0.6), (-1.35, 1.5), 3 * pi / 4, 7 * pi / 4,
        [(pi / 2, "π/2", True), (3 * pi / 4, "3π/4", False), (pi, "π", True), (3 * pi / 2, "3π/2", False),
         (7 * pi / 4, "7π/4", True), (2 * pi, "2π", True)],
        [(pi / 2, 1, "y = sin x", -6, -9, "end"), (0.3, -cos(0.3), "y = -cos x", 4, 12, "start")],
        w=300, h=175, width_mm=72, dots=((3 * pi / 4, sqrt(0.5)), (7 * pi / 4, -sqrt(0.5))),
        x0=-0.3, x1=2 * pi + 0.4)
    two("a7e_c3y", sin, cos, (-pi - 0.45, pi + 0.6), (-1.35, 1.5), -3 * pi / 4, pi / 4,
        [(-pi, "-π", True), (-3 * pi / 4, "-3π/4", False), (-pi / 2, "-π/2", True), (pi / 4, "π/4", True),
         (pi / 2, "π/2", True), (pi, "π", True)],
        [(pi / 2, 1, "y = sin x", 6, -9, "start"), (-0.2, 1, "y = cos x", -6, -9, "end")],
        w=300, h=175, width_mm=72, dots=((-3 * pi / 4, -sqrt(0.5)), (pi / 4, sqrt(0.5))),
        x0=-pi - 0.35, x1=pi + 0.4)
    # Ch 7 review Q9a: y = 2 sin 2x on [0, pi], shaded from pi/4 to 3pi/4
    g = LG(-0.3, pi + 0.45, -2.5, 2.6, w=250, h=165, pad=(18, 46, 18, 12))
    f = lambda t: 2 * sin(2 * t)  # noqa: E731
    shade(g, f, zero, pi / 4, 3 * pi / 4)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6, x0=0, x1=pi)
    g.vline(pi / 4, 0, 2, color="ink", dash="").vline(3 * pi / 4, 0, -2, color="ink", dash="")
    g.tick(pi / 4, "π/4").tick(pi / 2, "π/2").tick(3 * pi / 4, "3π/4", below=False).tick(pi, "π", below=False)
    g.ytick(2, "2").ytick(-2, "-2")
    g.near(2.6, f(2.6), "y = 2 sin 2x", 10, 4, anchor="start")
    save("a7e_r9a", g, 56)
    # PLC 2024 Q13(d)(i): y = -tan^-1 x, asymptotes y = +-pi/2, the point (1, -pi/4), the region shaded
    g = LG(-4.2, 4.2, -2.0, 2.0, w=280, h=175, pad=(18, 30, 18, 14))
    f = lambda t: -atan(t)  # noqa: E731
    g.fill(zero, f, 0, 1, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.hline(pi / 2).hline(-pi / 2)
    g.curve(f, color="ink", width=1.7)
    g.vline(1, 0, f(1), color="ink", dash="")
    g.dot(1, f(1), r=2.6)
    g.tick(1, "1", below=False)
    g.ytick(pi / 2, "π/2", left=False)
    g.ytick(-pi / 2, "-π/2", left=False)
    g.near(1, f(1), "(1, -π/4)", 8, 10, anchor="start")
    g.near(-4.1, 1.15, "y = -tan", 0, 0, anchor="start", kind="sup", power="-1", tail=" x")
    save("a7e_plc", g, 66)
    # Manly 2020 Q11(c): y = tan^-1 x with the lines y = +-pi/4, both regions next to the y-axis shaded
    g = LG(-2.6, 2.6, -1.9, 1.9, w=250, h=175, pad=(18, 30, 18, 14))
    g.fill_y(lambda y: tan(y), zero, 0, pi / 4, color="blue", opacity=0.3)
    g.fill_y(zero, lambda y: tan(y), -pi / 4, 0, color="blue", opacity=0.3)
    g.axes("x", "y")
    g.hline(pi / 2).hline(-pi / 2)
    g.hline(pi / 4, x0=-2.6, x1=2.6, color="ink", dash="").hline(-pi / 4, x0=-2.6, x1=2.6, color="ink", dash="")
    g.curve(atan, color="ink", width=1.7)
    g.dot(1, pi / 4, r=2.4).dot(-1, -pi / 4, r=2.4)
    g.tick(1, "1").tick(-1, "-1", below=False)
    g.ytick(pi / 4, "π/4", left=True)
    g.ytick(-pi / 4, "-π/4", left=False)
    g.ytick(pi / 2, "π/2", left=False)
    g.near(1.35, atan(1.35), "y = tan", 4, 14, anchor="start", kind="sup", power="-1", tail=" x")
    save("a7e_manly", g, 60)


if __name__ == "__main__":
    lesson()
    exercise()
    pp()
    review()
    answers()
    print("\n".join(LEFT) if LEFT else "svg_overlap: no problems in any 7E figure")
