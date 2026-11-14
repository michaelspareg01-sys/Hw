"""Figures for the Year 7 revision practice pack.

Run: python3 workspace/build/y7rev/figs.py   (writes svg/*.svg)

Every diagram recreates a textbook diagram (ICE-EM Mathematics 7 3rd ed) or draws the data of a
Pack question. Number planes use plots.Graph with a unit grid; every label sits on a small white
background so that it never collides with a grid line.
"""
import os, sys
from math import sqrt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt  # noqa: F401  (house header)

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)
BLUE = "#2b4aa0"          # textbook-style line colour
GRID = "#cdd4dd"
RED = "#d6283c"           # plotted points, as in the book
POINTS = {}               # name -> list of plotted (x, y); read by the check script


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(g if isinstance(g, str) else g.svg())


def tw(s, size):
    """Rough width of a label in pixels."""
    w = 0
    for ch in s:
        w += 0.36 if ch in "1()−-.,iljt " else 0.62
    return w * size


class Plane(Graph):
    """Number plane with a unit grid. unit = pixels per unit."""

    def __init__(self, xmin, xmax, ymin, ymax, unit=22, pad=(26, 30, 24, 24)):
        w = pad[0] + pad[1] + (xmax - xmin) * unit
        h = pad[2] + pad[3] + (ymax - ymin) * unit
        super().__init__(xmin, xmax, ymin, ymax, w, h, pad)

    def grid(self):
        for x in range(self.xmin, self.xmax + 1):
            self.items.append(f'<line x1="{self.X(x):.1f}" y1="{self.Y(self.ymin):.1f}" x2="{self.X(x):.1f}" '
                              f'y2="{self.Y(self.ymax):.1f}" stroke="{GRID}" stroke-width="0.8"/>')
        for y in range(self.ymin, self.ymax + 1):
            self.items.append(f'<line x1="{self.X(self.xmin):.1f}" y1="{self.Y(y):.1f}" x2="{self.X(self.xmax):.1f}" '
                              f'y2="{self.Y(y):.1f}" stroke="{GRID}" stroke-width="0.8"/>')
        return self

    def wlabel(self, px, py, s, anchor="middle", size=10.5, italic=False, color=INK, weight=500):
        """Label centred vertically on py, on a white background rectangle."""
        w = tw(s.replace("-", "−"), size) + 3
        x0 = {"middle": px - w / 2, "start": px - 1.5, "end": px - w + 1.5}[anchor]
        self.items.append(f'<rect x="{x0:.1f}" y="{py - size * 0.62:.1f}" width="{w:.1f}" height="{size * 1.24:.1f}" fill="#fff"/>')
        self.items.append(_txt(px, py, s, anchor, size=size, color=color, weight=weight, italic=italic))
        return self

    def frame(self, xlabel="x", ylabel="y", xstep=1, ystep=1, labels=True):
        """Grid, axes with arrows, ticks; tick labels every xstep / ystep (0 shown once)."""
        self.grid()
        self.axes(xlabel, ylabel)
        del self.items[-2:]               # put the axis names where no tick label can meet them
        x0, y0 = self._x0, self._y0
        self.items.append(_txt(self.X(self.xmax) + 18, y0 + 1, xlabel, "start", italic=True))
        self.items.append(_txt(x0 + 9, self.Y(self.ymax) - 13, ylabel, "start", italic=True))
        self._ticklabels = []
        quad = self.xmin < 0 < self.xmax and self.ymin < 0 < self.ymax
        for x in range(self.xmin, self.xmax + 1):
            if x and x % xstep == 0:
                self.items.append(f'<line x1="{self.X(x):.1f}" y1="{y0 - 3}" x2="{self.X(x):.1f}" y2="{y0 + 3}" stroke="{INK}" stroke-width="1.1"/>')
                dx = -3 if (quad and x == -xstep) else 0      # nudged clear of the origin 0 and the y labels
                self._ticklabels.append((self.X(x) + dx, y0 + 11, str(x), "middle"))
        for y in range(self.ymin, self.ymax + 1):
            if y and y % ystep == 0:
                self.items.append(f'<line x1="{x0 - 3}" y1="{self.Y(y):.1f}" x2="{x0 + 3}" y2="{self.Y(y):.1f}" stroke="{INK}" stroke-width="1.1"/>')
                dy = 3 if (quad and y == -ystep) else 0       # nudged down, clear of the origin 0
                self._ticklabels.append((x0 - 4, self.Y(y) + dy, str(y), "end"))
        if quad or (self.xmin == 0 and self.ymin == 0):
            self._ticklabels.append((x0 - 3, y0 + 8, "0", "end"))
        self._labels_on = labels
        return self

    def ticklabels(self, avoid=(), r=2.8):
        """Tick labels on white boxes. A label whose box would cover a data point in `avoid` is left out,
        so that no plotted point is ever hidden (the points are drawn after the labels)."""
        size = 9
        if self._labels_on:
            for px, py, s, a in self._ticklabels:
                w = tw(s.replace("-", "−"), size) + 3
                bx = {"middle": px - w / 2, "start": px - 1.5, "end": px - w + 1.5}[a]
                by, bh = py - size * 0.62, size * 1.24
                m = r + 2.5
                if any(bx - m < self.X(x) < bx + w + m and by - m < self.Y(y) < by + bh + m for x, y in avoid):
                    self.skipped = getattr(self, "skipped", []) + [s]
                    continue
                self.wlabel(px, py, s, a, size=size)
        return self

    def pts(self, name, pts, labels=None, r=2.8):
        POINTS[name] = list(pts)
        for (x, y) in pts:
            self.items.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{RED}"/>')
        return self


# ------------------------------------------------------------------ E Ch 7 Challenge Q7: rectangle ABCD
def e_rect():
    W, H, p = 150, 86, 22
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 2 * p} {H + 2 * p}" width="{W + 2 * p}" height="{H + 2 * p}" font-family="Inter, Arial, sans-serif">']
    s.append(f'<rect x="{p}" y="{p}" width="{W}" height="{H}" fill="none" stroke="{BLUE}" stroke-width="1.4"/>')
    for lab, x, y in (("B", p - 8, p - 8), ("C", p + W + 8, p - 8), ("A", p - 8, p + H + 9), ("D", p + W + 8, p + H + 9)):
        s.append(_txt(x, y, lab, size=13, italic=True))
    s.append("</svg>")
    save("e_rect", "".join(s))


# ------------------------------------------------------------------ G Ch 12 Review Q3: points A to G
G_COORDS = {"A": (4, 4), "B": (-4, 3), "C": (-3, -2), "D": (3, -3), "E": (1, 1), "F": (0, -4), "G": (-2, 0)}


def g_coords():
    g = Plane(-5, 5, -5, 5, unit=21)
    g.frame()
    g.ticklabels(avoid=G_COORDS.values())
    g.pts("g_coords", G_COORDS.values())
    off = {"G": (-9, -10)}
    for lab, (x, y) in G_COORDS.items():
        dx, dy = off.get(lab, (9, 9))
        g.wlabel(g.X(x) + dx, g.Y(y) + dy, lab, "middle", size=12, italic=True)
    save("g_coords", g)


# ------------------------------------------------------------------ G blank planes for plotting
def g_blank(name, xmin, xmax, ymin, ymax, unit, xlabel="x", ylabel="y", xstep=1, ystep=1):
    g = Plane(xmin, xmax, ymin, ymax, unit=unit)
    g.frame(xlabel, ylabel, xstep, ystep)
    g.ticklabels()
    save(name, g)


def g_ans_12c():
    """Answer: the points of y = -x + 1/2 for x = -3..3."""
    g = Plane(-4, 4, -3, 4, unit=20)
    g.frame()
    pts = [(x, -x + 0.5) for x in range(-3, 4)]
    line = [(-3.5 + k / 20, 4 - k / 20) for k in range(141)]       # samples of the drawn line y = -x + 1/2
    g.ticklabels(avoid=pts + line)
    g.items.append(f'<line x1="{g.X(-3.5):.1f}" y1="{g.Y(4):.1f}" x2="{g.X(3.5):.1f}" y2="{g.Y(-3):.1f}" stroke="{ACC["blue"]}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    g.pts("g_ans12c", pts)
    save("g_ans12c", g)


# ------------------------------------------------------------------ G Ex 12D Q2: matchstick triangles
def g_triangles():
    side, gap, p = 34, 30, 10
    hgt = side * sqrt(3) / 2
    widths = [side * (n + 1) / 2 for n in range(1, 5)]
    W = sum(widths) + gap * 3 + 2 * p
    H = hgt + 2 * p + 22
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.1f}" height="{H:.1f}" font-family="Inter, Arial, sans-serif">']
    x0 = p
    for n in range(1, 5):
        base_y, top_y = p + hgt, p
        segs = []
        # n triangles alternately pointing up and down along a strip
        for k in range(n):
            xl = x0 + k * side / 2
            if k % 2 == 0:      # up triangle: base (xl, base) to (xl+side, base), apex (xl+side/2, top)
                segs += [((xl, base_y), (xl + side, base_y)), ((xl, base_y), (xl + side / 2, top_y)),
                         ((xl + side / 2, top_y), (xl + side, base_y))]
            else:               # down triangle: top edge (xl, top) to (xl+side, top), apex (xl+side/2, base)
                segs += [((xl, top_y), (xl + side, top_y)), ((xl, top_y), (xl + side / 2, base_y)),
                         ((xl + side / 2, base_y), (xl + side, top_y))]
        uniq = []
        for a, b in segs:
            key = tuple(sorted((tuple(round(v, 2) for v in a), tuple(round(v, 2) for v in b))))
            if key not in uniq:
                uniq.append(key)
        POINTS[f"g_tri{n}"] = len(uniq)          # matches drawn in diagram n
        for (ax, ay), (bx, by) in uniq:
            s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{BLUE}" stroke-width="1.6" stroke-linecap="round"/>')
        s.append(_txt(x0 + widths[n - 1] / 2, p + hgt + 16, f"Diagram {n}", size=11, weight=600))
        x0 += widths[n - 1] + gap
    s.append("</svg>")
    save("g_tri", "".join(s))


# ------------------------------------------------------------------ G Ex 12D Q8: match the graphs
G8 = {"a": (lambda x: x + 3, range(-7, 7)), "c": (lambda x: -2 * x + 1, range(-4, 5)), "f": (lambda x: -2 * x - 1, range(-5, 4))}


def g_match():
    for k, (f, xs) in G8.items():
        g = Plane(-7, 7, -9, 10, unit=9.5, pad=(22, 32, 17, 14))
        g.frame(xstep=2, ystep=2)
        pts = [(x, f(x)) for x in xs if -9 <= f(x) <= 10]
        g.ticklabels(avoid=pts, r=2.4)
        g.pts("g8" + k, pts, r=2.4)
        save("g8" + k, g)


# ------------------------------------------------------------------ G Pack question: which sets of points are linear?
G_LIN = {"P": [(1, 1), (2, 3), (3, 5), (4, 7)],              # y = 2x - 1
         "Q": [(0, 1), (1, 2), (2, 4), (3, 8)],              # doubles each step: not a line
         "R": [(0, 7), (1, 6), (2, 5), (3, 4), (4, 3)]}      # y = 7 - x


def g_linear():
    for k, pts in G_LIN.items():
        g = Plane(0, 5, 0, 9, unit=13, pad=(24, 28, 22, 22))
        g.frame(ystep=2)
        g.ticklabels(avoid=pts)
        g.pts("g_lin" + k, pts)
        save("g_lin" + k, g)


# ------------------------------------------------------------------ H Pack question: Venn diagram
H_VENN = {"T only": 14, "both": 9, "S only": 22, "neither": 15}
POINTS["h_venn"] = H_VENN


def h_venn():
    W, H = 300, 170
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, Arial, sans-serif">']
    s.append(f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    r, cy = 58, 94
    c1, c2 = 118, 190
    for c in (c1, c2):                # circles drawn as two arcs
        s.append(f'<path d="M{c - r},{cy} A{r},{r} 0 1 0 {c + r},{cy} A{r},{r} 0 1 0 {c - r},{cy} Z" fill="none" stroke="{BLUE}" stroke-width="1.5"/>')
    s.append(_txt(c1 - 22, 24, "Tennis", size=12, weight=600))
    s.append(_txt(c2 + 22, 24, "Swimming", size=12, weight=600))
    s.append(_txt(c1 - 28, cy, str(H_VENN["T only"]), size=13))
    s.append(_txt((c1 + c2) / 2, cy, str(H_VENN["both"]), size=13))
    s.append(_txt(c2 + 28, cy, str(H_VENN["S only"]), size=13))
    s.append(_txt(W - 26, H - 22, str(H_VENN["neither"]), size=13))
    s.append("</svg>")
    save("h_venn", "".join(s))


if __name__ == "__main__":
    e_rect()
    g_coords()
    g_blank("g_plane12c", -4, 4, -3, 4, 20)
    g_ans_12c()
    g_triangles()
    g_blank("g_plane12d", 0, 7, 0, 14, 13, xlabel="t", ylabel="m", xstep=1, ystep=2)
    g_match()
    g_linear()
    h_venn()
    print("figures:", sorted(f for f in os.listdir(OUT)))
    import json
    with open(os.path.join(OUT, "figdata.json"), "w", encoding="utf-8") as f:
        json.dump(POINTS, f, indent=1)
    print("points:", {k: v for k, v in POINTS.items()})
