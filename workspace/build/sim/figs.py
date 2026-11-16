"""Figures for the Year 9/10 Simultaneous Equations pack: helpers (Plane, Sketch) and the revision figures.

Graphs are drawn to scale: one unit on the x-axis is the same length as one unit on the y-axis, and
`unit=CM` makes one unit exactly 1 cm on the printed page (96 px per inch). Lines are drawn from their
equation ax + by = c (class "ln", data-eq gives the equation), points of intersection are circles of
class "ix", tick labels are texts of class "tx" / "ty". The checks (workspace/checks/sim_*.py) read the
lines, dots and tick labels back from the SVG and work in coordinates.
Labels sit on a white mask, so grid lines behind them do not cross them (tools/svg_overlap.py).
Lesson figures live in figs_l1.py (and later figs_l2.py, figs_l3.py); they import the helpers below.
Run: python3 figs.py && python3 figs_l1.py   (writes svg/*.svg)
"""
import os
import re
import sys
from math import hypot, cos, sin, radians

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from svg_overlap import text_width, text_extent, check_string, seg_hits_box, boxes_meet  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")
os.makedirs(OUT, exist_ok=True)

CM = 96 / 2.54          # px per cm on the printed page
INK, FAINT, GRID = "#1f2a37", "#8a96a3", "#cdd4dd"
COL = {"blue": "#2563eb", "rose": "#e11d48", "teal": "#0d9488", "amber": "#c2790a", "violet": "#6d44d9",
       "green": "#15a34a", "ink": INK, "faint": FAINT}
ITAL = re.compile(r"(?<![A-Za-z])([a-zA-Z])(?![A-Za-z])")


def _f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def label_markup(s, italic_letters=True):
    """'y = 2x - 1' -> markup with a true minus sign and the single letters in italics."""
    s = s.replace("-", "−")
    if not italic_letters:
        return s
    return ITAL.sub(lambda m: f'<tspan font-style="italic">{m.group(1)}</tspan>', s)


def text(x, y, s, anchor="middle", size=12.0, color=INK, cls=None, mask=True, italic_letters=True, weight=500,
         italic=False):
    """A label whose vertical centre is near y (baseline y + 0.35 size), on a white mask."""
    plain = s.replace("-", "−")
    base = y + 0.35 * size
    w = text_width(plain, size)
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    up, down = text_extent(plain, size)
    out = []
    if mask:
        out.append(f'<rect x="{_f(x0 - 2.5)}" y="{_f(base - up - 2.5)}" width="{_f(w + 5)}" '
                   f'height="{_f(up + down + 5)}" fill="#fff"/>')
    c = f' class="{cls}"' if cls else ""
    it = ' font-style="italic"' if italic else ""
    out.append(f'<text{c} x="{_f(x)}" y="{_f(base)}" text-anchor="{anchor}" font-size="{size}" '
               f'fill="{color}" font-weight="{weight}"{it}>{label_markup(s, italic_letters and not italic)}</text>')
    return "".join(out)


def arrowhead(x1, y1, x2, y2, color, size=7.0):
    """Filled arrowhead with its tip at (x2, y2), pointing from (x1, y1)."""
    d = hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    bx, by = x2 - size * ux, y2 - size * uy
    px, py = -uy * size * 0.42, ux * size * 0.42
    return (f'<path d="M{_f(x2)},{_f(y2)} L{_f(bx + px)},{_f(by + py)} L{_f(bx - px)},{_f(by - py)} z" '
            f'fill="{color}" stroke="none"/>')


class Plane:
    """A number plane drawn to scale. unit = px per unit on both axes.

    Layers, in drawing order: grid, axes, labels (each on a white mask), dashed guides, plotted lines,
    dots. A tick label that would touch a plotted line, a dot or another label is left out, so every
    label that is drawn is clear (tools/svg_overlap.py checks the result)."""

    def __init__(self, xmin, xmax, ymin, ymax, unit=CM, pad=(22, 22, 20, 20), grid=True, ticks=True,
                 xticks=None, yticks=None, tick_size=11.0, origin_label=True, axis_extra=0.45):
        self.xmin, self.xmax, self.ymin, self.ymax, self.u = xmin, xmax, ymin, ymax, unit
        self.pl, self.pr, self.pt, self.pb = pad
        self.ext = axis_extra                       # axes run this many units past the grid
        self.w = self.pl + (xmax - xmin + 2 * axis_extra) * unit + self.pr
        self.h = self.pt + (ymax - ymin + 2 * axis_extra) * unit + self.pb
        self.grid, self.axes, self.labels, self.guide_items, self.lines, self.dots = [], [], [], [], [], []
        self.segs, self.dot_boxes = [], []
        if grid:
            for i in range(int(round(xmin)), int(round(xmax)) + 1):
                self.grid.append(f'<line x1="{_f(self.X(i))}" y1="{_f(self.Y(ymin))}" x2="{_f(self.X(i))}" '
                                 f'y2="{_f(self.Y(ymax))}" stroke="{GRID}" stroke-width="0.7"/>')
            for j in range(int(round(ymin)), int(round(ymax)) + 1):
                self.grid.append(f'<line x1="{_f(self.X(xmin))}" y1="{_f(self.Y(j))}" x2="{_f(self.X(xmax))}" '
                                 f'y2="{_f(self.Y(j))}" stroke="{GRID}" stroke-width="0.7"/>')
        self._axes(ticks, xticks, yticks, tick_size, origin_label)

    def X(self, x):
        return self.pl + (x - self.xmin + self.ext) * self.u

    def Y(self, y):
        return self.pt + (self.ymax - y + self.ext) * self.u

    def _lab(self, x, y, s, anchor, size, color=INK, cls=None, italic=False, tick=False, cands=None, optional=False,
             at=None):
        """A label at (x, y) px; with cands = [(x, y, anchor), ...] the first clear position is used."""
        self.labels.append(dict(x=x, y=y, s=s, anchor=anchor, size=size, color=color, cls=cls, italic=italic,
                                tick=tick, cands=cands, optional=optional, at=at))

    def _axes(self, ticks, xticks, yticks, size, origin_label):
        x0, y0 = self.X(0), self.Y(0)
        xa, xb = self.X(self.xmin - self.ext), self.X(self.xmax + self.ext)
        ya, yb = self.Y(self.ymin - self.ext), self.Y(self.ymax + self.ext)
        a = self.axes
        a.append(f'<line x1="{_f(xa)}" y1="{_f(y0)}" x2="{_f(xb - 4)}" y2="{_f(y0)}" stroke="{INK}" stroke-width="1.3"/>')
        a.append(arrowhead(xa, y0, xb, y0, INK, 7))
        a.append(f'<line x1="{_f(x0)}" y1="{_f(ya)}" x2="{_f(x0)}" y2="{_f(yb + 4)}" stroke="{INK}" stroke-width="1.3"/>')
        a.append(arrowhead(x0, ya, x0, yb, INK, 7))
        self.axis_segs = [((xa, y0), (xb, y0), 1.3 + 1), ((x0, ya), (x0, yb), 1.3 + 1)]
        self._lab(xb + 5, y0 + 1, "x", "start", 12.5, cands=[(xb + 5, y0 + 1, "start"), (xb - 2, y0 - 11, "middle"),
                                                             (xb - 2, y0 + 12, "middle")])
        self._lab(x0 + 7, yb + 3, "y", "start", 12.5, cands=[(x0 + 7, yb + 3, "start"), (x0 - 7, yb + 3, "end"),
                                                             (x0 + 9, yb + 10, "start"), (x0 - 9, yb + 10, "end"),
                                                             (x0 + 7, yb - 3, "start"), (x0 - 7, yb - 3, "end"),
                                                             (x0 + 14, yb + 16, "start"), (x0 - 14, yb + 16, "end")])
        if not ticks:
            return
        xt = xticks if xticks is not None else [i for i in range(int(round(self.xmin)), int(round(self.xmax)) + 1) if i]
        yt = yticks if yticks is not None else [j for j in range(int(round(self.ymin)), int(round(self.ymax)) + 1) if j]
        for v in xt:
            x = self.X(v)
            a.append(f'<line x1="{_f(x)}" y1="{_f(y0 - 3)}" x2="{_f(x)}" y2="{_f(y0 + 3)}" stroke="{INK}" stroke-width="1.1"/>')
            self._lab(x, y0 + 10.5, _num(v), "middle", size, cls="tx", tick=True, at=(v, 0),
                      cands=[(x, y0 + 10.5, "middle"), (x + 7, y0 + 10.5, "start"), (x - 7, y0 + 10.5, "end"),
                             (x + 7, y0 - 10, "start"), (x - 7, y0 - 10, "end")])
        for v in yt:
            y = self.Y(v)
            a.append(f'<line x1="{_f(x0 - 3)}" y1="{_f(y)}" x2="{_f(x0 + 3)}" y2="{_f(y)}" stroke="{INK}" stroke-width="1.1"/>')
            self._lab(x0 - 6, y, _num(v), "end", size, cls="ty", tick=True, at=(0, v),
                      cands=[(x0 - 6, y, "end"), (x0 - 6, y - 10, "end"), (x0 - 6, y + 10, "end"),
                             (x0 + 6, y - 10, "start"), (x0 + 6, y + 10, "start")])
        if origin_label:
            self._lab(x0 - 5, y0 + 10.5, "O", "end", size, italic=True, optional=True,
                      cands=[(x0 - 5, y0 + 10.5, "end"), (x0 + 5, y0 + 10.5, "start"), (x0 - 5, y0 - 10, "end"),
                             (x0 + 5, y0 - 10, "start")])

    def clip(self, a, b, c, lo=None, hi=None, extend=0.0):
        """End points of the part of ax + by = c inside the grid box grown by `extend` units
        (optionally only lo <= x <= hi)."""
        xa, xb = self.xmin - extend, self.xmax + extend
        ya, yb = self.ymin - extend, self.ymax + extend
        if lo is not None:
            xa = max(xa, lo)
        if hi is not None:
            xb = min(xb, hi)
        pts = []
        if b != 0:
            for x in (xa, xb):
                y = (c - a * x) / b
                if ya - 1e-9 <= y <= yb + 1e-9:
                    pts.append((x, y))
        if a != 0:
            for y in (ya, yb):
                x = (c - b * y) / a
                if xa - 1e-9 <= x <= xb + 1e-9:
                    pts.append((x, y))
        uniq = []
        for p in pts:
            if all(hypot(p[0] - q[0], p[1] - q[1]) > 1e-6 for q in uniq):
                uniq.append(p)
        uniq.sort(key=lambda p: (p[0], p[1]))
        return uniq[0], uniq[-1]

    def line(self, a, b, c, color="blue", eq=None, width=2.0, lo=None, hi=None, arrows=True, extend=None):
        if extend is None:
            extend = 0.75 * self.ext
        (x1, y1), (x2, y2) = self.clip(a, b, c, lo, hi, extend)
        X1, Y1, X2, Y2 = self.X(x1), self.Y(y1), self.X(x2), self.Y(y2)
        col = COL[color]
        d = f' data-eq="{eq}"' if eq else ""
        self.segs.append(((X1, Y1), (X2, Y2), width + 4))
        self.eqs = getattr(self, "eqs", []) + [(a, b, c)]
        if arrows:
            L = hypot(X2 - X1, Y2 - Y1)
            ux, uy = (X2 - X1) / L, (Y2 - Y1) / L
            self.lines.append(f'<line class="ln"{d} x1="{_f(X1 + 3 * ux)}" y1="{_f(Y1 + 3 * uy)}" '
                              f'x2="{_f(X2 - 3 * ux)}" y2="{_f(Y2 - 3 * uy)}" stroke="{col}" stroke-width="{width}"/>')
            self.lines.append(arrowhead(X2 - ux, Y2 - uy, X2, Y2, col, 8))
            self.lines.append(arrowhead(X1 + ux, Y1 + uy, X1, Y1, col, 8))
        else:
            self.lines.append(f'<line class="ln"{d} x1="{_f(X1)}" y1="{_f(Y1)}" x2="{_f(X2)}" y2="{_f(Y2)}" '
                              f'stroke="{col}" stroke-width="{width}"/>')
        return self

    def label(self, x, y, s, anchor="middle", color="ink", size=11.5, dx=0, dy=0, cls=None):
        self._lab(self.X(x) + dx, self.Y(y) + dy, s, anchor, size, COL[color], cls=cls)
        return self

    def plabel(self, x, y, s, color="ink", size=11.5):
        """Label for the point (x, y): the first clear spot around it."""
        X, Y = self.X(x), self.Y(y)
        c = [(X + 8, Y - 10, "start"), (X - 8, Y - 10, "end"), (X + 8, Y + 10, "start"), (X - 8, Y + 10, "end")]
        for r in (13, 18, 24, 31, 39):
            for k in range(24):
                t = radians(15 * k + 7.5)
                cx, cy = cos(t), sin(t)
                anc = "start" if cx > 0.3 else "end" if cx < -0.3 else "middle"
                c.append((X + r * cx, Y - r * cy + (3 if anc == "middle" and cy < 0 else 0), anc))
        self._lab(X, Y, s, "start", size, COL[color], cands=c)
        return self

    def llabel(self, a, b, c, s, color="ink", size=11.5, ts=(0.86, 0.14, 0.72, 0.28, 0.6, 0.4, 0.5)):
        """Label for the line ax + by = c: beside the drawn line, at the first clear spot along it."""
        (x1, y1), (x2, y2) = self.clip(a, b, c)
        X1, Y1, X2, Y2 = self.X(x1), self.Y(y1), self.X(x2), self.Y(y2)
        L = hypot(X2 - X1, Y2 - Y1)
        nx, ny = -(Y2 - Y1) / L, (X2 - X1) / L
        cand = []
        for t in ts:
            px, py = X1 + t * (X2 - X1), Y1 + t * (Y2 - Y1)
            for side in (1, -1):
                for d in (11, 17, 24, 32):
                    qx, qy = px + side * d * nx, py + side * d * ny
                    hx = side * nx
                    anc = "start" if hx > 0.35 else "end" if hx < -0.35 else "middle"
                    qy += side * ny * 3 if anc == "middle" else 0
                    cand.append((qx, qy, anc))
        self._lab(X1, Y1, s, "start", size, COL[color], cands=cand)
        self.labels[-1]["kind"] = "line"
        return self

    def guides(self, x, y, color="faint"):
        """Dashed lines from (x, y) to both axes."""
        X, Y, X0, Y0 = self.X(x), self.Y(y), self.X(0), self.Y(0)
        sx = 1 if Y0 > Y else -1               # stop 3 px short of each axis
        sy = 1 if X0 > X else -1
        for p, q in (((X, Y), (X, Y0 - 3 * sx)), ((X, Y), (X0 - 3 * sy, Y))):
            self.guide_items.append(f'<line x1="{_f(p[0])}" y1="{_f(p[1])}" x2="{_f(q[0])}" y2="{_f(q[1])}" '
                                    f'stroke="{COL[color]}" stroke-width="1.2" stroke-dasharray="4 3"/>')
            self.segs.append((p, q, 1.2 + 4))
        return self

    def dot(self, x, y, cls="ix", color="ink", r=3.4):
        c = f' class="{cls}"' if cls else ""
        X, Y = self.X(x), self.Y(y)
        self.dots.append(f'<circle{c} cx="{_f(X)}" cy="{_f(Y)}" r="{r}" fill="{COL[color]}"/>')
        self.dot_boxes.append((X - r - 2, Y - r - 2, X + r + 2, Y + r + 2))
        return self

    @staticmethod
    def _box(L):
        plain = L["s"].replace("-", "−")
        w = text_width(plain, L["size"])
        base = L["y"] + 0.35 * L["size"]
        x0 = {"start": L["x"], "middle": L["x"] - w / 2, "end": L["x"] - w}[L["anchor"]]
        up, down = text_extent(plain, L["size"])
        return (x0 - 2.5, base - up - 2.5, x0 + w + 2.5, base + down + 2.5)

    def svg(self):
        kept, boxes = [], []
        fixed = [L for L in self.labels if not L["tick"] and not L["cands"]]
        auto = [L for L in self.labels if L["cands"] and not L["tick"]]
        ticks = [L for L in self.labels if L["tick"]]
        axes_thin = getattr(self, "axis_segs", [])
        axes_wide = [(p, q, 26) for p, q, w in axes_thin]

        def clear(b, segs):
            if b[0] < 0 or b[1] < 0 or b[2] > self.w or b[3] > self.h:
                return False
            if any(boxes_meet(b, o) for o in boxes) or any(boxes_meet(b, o) for o in self.dot_boxes):
                return False
            return not any(seg_hits_box(p, q, (b[0] - w / 2, b[1] - w / 2, b[2] + w / 2, b[3] + w / 2))
                           for p, q, w in segs)

        for L in fixed:
            kept.append(L)
            boxes.append(self._box(L))
        for L in auto:
            segs = self.segs + (axes_wide if L.get("kind") == "line" else axes_thin)
            for (x, y, anc) in L["cands"]:
                M = dict(L, x=x, y=y, anchor=anc)
                b = self._box(M)
                if clear(b, segs):
                    kept.append(M)
                    boxes.append(b)
                    break
            else:
                if not L["optional"]:
                    raise SystemExit(f"no clear place for label {L['s']!r} (figure {self.w:.0f} x {self.h:.0f})")
        for L in ticks:
            # the usual place; the other places only when a plotted line crosses the usual one
            first = self._box(dict(L, x=L["cands"][0][0], y=L["cands"][0][1], anchor=L["cands"][0][2]))
            u, v = L["at"]
            intercept = any(abs(a * u + b * v - c) < 0.05 * hypot(a, b) for a, b, c in getattr(self, "eqs", []))
            crossed = intercept and not clear(first, self.segs) and clear(first, [])
            for (x, y, anc) in (L["cands"] if crossed else L["cands"][:1]):
                M = dict(L, x=x, y=y, anchor=anc)
                b = self._box(M)
                if clear(b, self.segs):
                    kept.append(M)
                    boxes.append(b)
                    break
        labs = [text(L["x"], L["y"], L["s"], L["anchor"], L["size"], L["color"], cls=L["cls"], italic=L["italic"])
                for L in kept]
        body = "".join(self.grid + self.axes + labs + self.guide_items + self.lines + self.dots)
        st = f' style="width:{_f(self.w)}px"' if getattr(self, "natural", False) else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_f(self.w)} {_f(self.h)}" '
                f'width="{_f(self.w)}" height="{_f(self.h)}"{st} font-family="Inter, Arial, sans-serif">{body}</svg>')


def _num(v):
    s = _f(v)
    return s.replace("-", "−")


class Sketch:
    """A free sketch in pixel coordinates (y down), for figures that are not to scale."""

    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def line(self, x1, y1, x2, y2, color=INK, width=1.4, cls=None, dash=None):
        c = f' class="{cls}"' if cls else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<line{c} x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{color}" '
                          f'stroke-width="{width}"{ds}/>')
        return self

    def arrow(self, x1, y1, x2, y2, color=INK, width=1.4, head=7.0, cls=None):
        d = hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        self.line(x1, y1, x2 - 3 * ux, y2 - 3 * uy, color, width, cls)
        self.items.append(arrowhead(x1, y1, x2, y2, color, head))
        return self

    def text(self, x, y, s, anchor="middle", size=12.0, mask=True, cls=None, italic=False):
        self.items.append(text(x, y, s, anchor, size, cls=cls, mask=mask, italic=italic))
        return self

    def dot(self, x, y, r=2.8, cls=None):
        c = f' class="{cls}"' if cls else ""
        self.items.append(f'<circle{c} cx="{_f(x)}" cy="{_f(y)}" r="{r}" fill="{INK}"/>')
        return self

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_f(self.w)} {_f(self.h)}" '
                f'width="{_f(self.w)}" height="{_f(self.h)}" font-family="Inter, Arial, sans-serif">'
                + "".join(self.items) + "</svg>")


def save(name, fig):
    s = fig.svg()
    probs = check_string(s)
    if probs:
        print(f"  {name}: " + "; ".join(probs))
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(s)


# ======================= revision figures =======================

def rev_7b():
    """Year 8 Example 2 (7B): y = 2x - 1 plotted from its table, x from -3 to 3."""
    p = Plane(-3, 3, -7, 5, unit=18, pad=(48, 46, 14, 14), tick_size=11, axis_extra=0.7, origin_label=False)
    p.line(2, -1, 1, "blue", eq="y=2x-1")
    pts = [(-3, -7), (-2, -5), (-1, -3), (0, -1), (1, 1), (2, 3), (3, 5)]
    for x, y in pts:
        p.dot(x, y, cls="pt", color="blue", r=2.8)
    off = {(-3, -7): (-9, -4, "end"), (-2, -5): (-9, -4, "end"), (-1, -3): (-9, -4, "end"),
           (0, -1): (9, 4, "start"), (1, 1): (9, 4, "start"), (2, 3): (9, 4, "start"), (3, 5): (9, 4, "start")}
    for (x, y), (dx, dy, anc) in off.items():
        p.label(x, y, f"({x}, {y})", anc, size=11, dx=dx, dy=dy)
    save("rev_7b", p)


def rev_7e():
    """Year 8 7E Key ideas: y = 2x - 1 through (0, -1) and (1, 1)."""
    p = Plane(-2, 2, -2, 2, unit=22, pad=(24, 22, 14, 14), tick_size=11, axis_extra=0.6)
    p.line(2, -1, 1, "blue", eq="y=2x-1")
    p.dot(0, -1, cls="pt", color="blue", r=2.8).dot(1, 1, cls="pt", color="blue", r=2.8)
    p.label(1, 1, "(1, 1)", "start", size=11, dx=8, dy=0)
    p.label(0, -1, "(0, −1)", "start", size=11, dx=8, dy=4)
    save("rev_7e", p)


def rev_w4_grid():
    """Blank 1 cm grid for warm-up Q4 (Year 8 7B Q6c)."""
    p = Plane(-3, 3, -1, 7, unit=CM * 0.55, pad=(26, 22, 14, 14), tick_size=11)
    save("rev_w4", p)


def rev_w4_ans():
    """Answer graph for warm-up Q4: y = 3 - x plotted from its table."""
    p = Plane(-3, 3, -1, 7, unit=24, pad=(26, 22, 14, 14), tick_size=11)
    p.line(1, 1, 3, "blue", eq="y=3-x")
    for x in range(-3, 4):
        p.dot(x, 3 - x, cls="pt", color="blue", r=2.8)
    p.label(1.3, 3.3, "y = 3 − x", "start", size=11.5)
    save("rev_w4a", p)


if __name__ == "__main__":
    rev_7b()
    rev_7e()
    rev_w4_grid()
    rev_w4_ans()
    print("revision figures written")
