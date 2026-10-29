import os, sys
from math import sin, cos, tan, atan, atan2, pi, sqrt, radians, degrees
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(g.svg())


class Fig:
    """Plain geometry diagram in pixel coordinates (y downwards)."""

    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def line(self, x1, y1, x2, y2, color="ink", width=1.6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ACC[color]}" stroke-width="{width}"{d} stroke-linecap="round"/>')
        return self

    def arrow(self, x1, y1, x2, y2, color="ink", width=1.6, head=7, dash=None):
        self.line(x1, y1, x2, y2, color, width, dash)
        a = atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head * cos(a - 0.4), y2 - head * sin(a - 0.4))
        p2 = (x2 - head * cos(a + 0.4), y2 - head * sin(a + 0.4))
        self.items.append(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} z" fill="{ACC[color]}"/>')
        return self

    def dim(self, x1, y1, x2, y2, color="faint"):
        """Double-headed dimension arrow."""
        self.arrow(x1, y1, x2, y2, color, 1.1, 6)
        return self.arrow(x2, y2, x1, y1, color, 1.1, 6)

    def poly(self, pts, color="blue", opacity=0.18, stroke="ink", width=1.6, closed=True):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        fill = ACC[color] if color else "none"
        self.items.append(f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" stroke="{ACC[stroke]}" stroke-width="{width}" stroke-linejoin="round"/>')
        return self

    def path(self, d, color="blue", width=2.2, dash=None, fill="none", opacity=1):
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        f = ACC[fill] if fill != "none" else "none"
        self.items.append(f'<path d="{d}" fill="{f}" fill-opacity="{opacity}" stroke="{ACC[color]}" stroke-width="{width}"{ds} stroke-linejoin="round"/>')
        return self

    def arc(self, cx, cy, r, a0, a1, color="faint", width=1.3):
        """Arc from angle a0 to a1 (degrees, anticlockwise from +x on screen, i.e. upwards)."""
        x0, y0 = cx + r * cos(radians(a0)), cy - r * sin(radians(a0))
        x1, y1 = cx + r * cos(radians(a1)), cy - r * sin(radians(a1))
        large = 1 if abs(a1 - a0) > 180 else 0
        sweep = 0 if a1 > a0 else 1
        self.items.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"/>')
        return self

    def right(self, x, y, dx, dy, s=8):
        """Right-angle mark at (x, y) with legs towards (dx, dy) signs."""
        self.items.append(f'<path d="M{x + dx*s:.1f},{y:.1f} L{x + dx*s:.1f},{y + dy*s:.1f} L{x:.1f},{y + dy*s:.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
        return self

    def text(self, x, y, s, anchor="middle", size=12, color="ink", italic=False, weight=500):
        self.items.append(_txt(x, y, s, anchor, size=size, color=ACC[color], italic=italic, weight=weight))
        return self

    def dot(self, x, y, r=3, color="ink"):
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{ACC[color]}"/>')
        return self

    def raw(self, s):
        self.items.append(s)
        return self

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="Inter, Arial, sans-serif">' + "".join(self.items) + "</svg>")


# ---------------------------------------------------------------- 14A: filling places one at a time
def boxes(name, contents, captions, bw=64, bh=40, gap=8, fixed=()):
    """A row of places. contents: big text in each box; captions: small text below.
    Indices in `fixed` are drawn shaded (a letter that is placed first)."""
    n = len(contents)
    w = n * bw + (n - 1) * gap + 8
    f = Fig(w, bh + 30)
    for i, (c, cap) in enumerate(zip(contents, captions)):
        x = 4 + i * (bw + gap)
        fill = ACC["amber"] if i in fixed else ACC["blue"]
        f.raw(f'<rect x="{x}" y="4" width="{bw}" height="{bh}" rx="5" fill="{fill}" fill-opacity="0.10" '
              f'stroke="{ACC["ink"]}" stroke-width="1.4"/>')
        f.text(x + bw / 2, 4 + bh / 2, str(c), size=17, weight=600)
        f.text(x + bw / 2, bh + 20, cap, size=10.5, color="faint")
    save(name, f)


def fig_14a():
    places = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]
    # textbook: a queue of five people at a bus stop
    boxes("queue5", [5, 4, 3, 2, 1], [p + " place" for p in places[:5]], bw=78)
    # PP: a PIN using four of the digits 0 to 9, no repeats
    boxes("pin4", [10, 9, 8, 7], [p + " digit" for p in places[:4]], bw=78)
    # PP: EPSILON beginning with P and ending with S
    boxes("epsilon", ["P", 5, 4, 3, 2, 1, "S"], places, bw=50, fixed=(0, 6))


def fig_14c():
    # Example 9: the five groups of the queue (couple, three girls, three single boys)
    boxes("groups9", ["G B", "G G G", "B", "B", "B"],
          ["couple: 2! orders", "3 girls: 3! orders", "boy", "boy", "boy"], bw=104, fixed=(0, 1))


# ---------------------------------------------------------------- 14D: paths on a grid
def grid(name, rects, points, path=None, cell=30, pad=24):
    """Grids of unit squares drawn in grid units with y upwards.
    rects: (x0, y0, cols, rows) blocks of squares; points: {label: (gx, gy, dx, dy)} with a
    dot at (gx, gy) and the label offset by (dx, dy) pixels; path: grid points joined in colour."""
    X1 = max(x + c for x, y, c, r in rects)
    Y1 = max(y + r for x, y, c, r in rects)
    f = Fig(X1 * cell + 2 * pad, Y1 * cell + 2 * pad)
    P = lambda gx, gy: (pad + gx * cell, pad + (Y1 - gy) * cell)
    for x0, y0, c, r in rects:
        for i in range(c + 1):
            f.line(*P(x0 + i, y0), *P(x0 + i, y0 + r), color="faint", width=1.2)
        for j in range(r + 1):
            f.line(*P(x0, y0 + j), *P(x0 + c, y0 + j), color="faint", width=1.2)
    if path:
        d = "M" + " L".join("{:.1f},{:.1f}".format(*P(*q)) for q in path)
        f.path(d, color="blue", width=3)
    for lab, (gx, gy, dx, dy) in points.items():
        x, y = P(gx, gy)
        f.dot(x, y, 4)
        f.text(x + dx, y + dy, lab, size=13, italic=True, weight=600)
    save(name, f)


def fig_14d():
    # Concept 2: a 3 by 2 grid, right or down from A (top left) to B (bottom right), path R D R R D
    grid("grid32", [(0, 0, 3, 2)], {"A": (0, 2, -12, -8), "B": (3, 0, 12, 12)},
         path=[(0, 2), (1, 2), (1, 1), (2, 1), (3, 1), (3, 0)], cell=40)
    # Tutor demo and Your turn: 4 by 2 and 3 by 3 grids
    grid("grid42", [(0, 0, 4, 2)], {"A": (0, 2, -12, -8), "B": (4, 0, 12, 12)}, cell=26)
    grid("grid33", [(0, 0, 3, 3)], {"A": (0, 3, -12, -8), "B": (3, 0, 12, 12)}, cell=26)
    # Normanhurst Boys 2022 Q11(e): 5 by 3 grid of unit squares, A top left, B bottom right
    grid("nbhs22", [(0, 0, 5, 3)], {"A": (0, 3, -12, -8), "B": (5, 0, 12, 12)}, cell=28)
    # St Aloysius 2024 Q8: a 5 by 3 grid, and a 4 by 2 grid joined at its corner; right or up from A to B
    grid("stalo24", [(0, 0, 5, 3), (5, 3, 4, 2)], {"A": (0, 0, -12, 12), "B": (9, 5, 12, -8)}, cell=25)
    grid("stalo24c", [(0, 0, 5, 3), (5, 3, 4, 2)], {"A": (0, 0, -12, 12), "B": (9, 5, 12, -8), "C": (5, 3, -10, -9)}, cell=26)


# ---------------------------------------------------------------- 14E
def sub_label(f, x, y, base, sub, size=12.5):
    """Italic letter with a numeric subscript, centred at (x, y)."""
    f.raw(f'<text x="{x:.1f}" y="{y + size*0.35:.1f}" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="500">'
          f'<tspan font-style="italic">{base}</tspan><tspan dy="3.5" font-size="{size*0.72:.1f}">{sub}</tspan></text>')


def circle_points(name, n, r=70, pad=30, size=14):
    """Points A1..An in order clockwise around a circle, A1 at the top."""
    c = r + pad
    f = Fig(2 * c, 2 * c)
    f.raw(f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    for k in range(n):
        a = radians(90 - 360 * k / n)
        x, y = c + r * cos(a), c - r * sin(a)
        f.dot(x, y, 3)
        sub_label(f, c + (r + 17) * cos(a) - 2, c - (r + 17) * sin(a), "A", k + 1, size)
    save(name, f)


def cross_grid(name, cols, rows, crosses, cpoint, cell=24, pad=22):
    """Grid of unit squares, A top left and B bottom right, with X marks at grid points
    (right, down) in `crosses`; the point cpoint is also marked C."""
    f = Fig(cols * cell + 2 * pad, rows * cell + 2 * pad)
    P = lambda i, j: (pad + i * cell, pad + j * cell)
    for i in range(cols + 1):
        f.line(*P(i, 0), *P(i, rows), color="ink", width=1.2)
    for j in range(rows + 1):
        f.line(*P(0, j), *P(cols, j), color="ink", width=1.2)
    for lab, (i, j, dx, dy) in {"A": (0, 0, -11, -6), "B": (cols, rows, 11, 8), "C": (cpoint[0], cpoint[1], 9, 10)}.items():
        x, y = P(i, j)
        f.dot(x, y, 3.2)
        f.text(x + dx, y + dy, lab, size=12.5, italic=True, weight=600)
    for i, j in crosses:
        x, y = P(i, j)
        h = 5.5
        f.raw(f'<path class="cross" d="M{x - h:.1f},{y - h:.1f} L{x + h:.1f},{y + h:.1f} M{x - h:.1f},{y + h:.1f} L{x + h:.1f},{y - h:.1f}" '
              f'fill="none" stroke="{INK}" stroke-width="1.3"/>')
    save(name, f)


def points_line(name, on, off, line, w, h):
    """Points (dots) with one straight line drawn through some of them."""
    f = Fig(w, h)
    f.line(*line, color="ink", width=1.4)
    for x, y in on + off:
        f.dot(x, y, 5)
    save(name, f)


def tiles(name, top, bottom, n=10, s=30, pad=4):
    """Two rows of n square tiles; tiles numbered 1..n from the left in `top`/`bottom` are shaded."""
    f = Fig(n * s + 2 * pad, 2 * s + 2 * pad)
    for row, shade in ((0, top), (1, bottom)):
        for k in range(n):
            fill = "#c4c8cc" if k + 1 in shade else "#ffffff"
            f.raw(f'<rect class="tile" data-row="{row}" data-col="{k + 1}" x="{pad + k * s}" y="{pad + row * s}" width="{s}" height="{s}" '
                  f'fill="{fill}" stroke="{INK}" stroke-width="1.1"/>')
    save(name, f)


def fig_14e():
    # Example 20: ten points around a circle
    circle_points("circle10", 10)
    # Exercise 14E Q25: a grid 4 squares wide and 6 high; crosses after four moves; C is the middle cross
    cross_grid("grid25", 4, 6, [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4)], (2, 2))
    # Abbotsleigh 2020 Q13(a): nine points, four of them on one line (line y = 50 + (x - 40)/10)
    points_line("abb20pts", on=[(80, 54), (190, 65), (260, 72), (360, 82)],
                off=[(130, 16), (300, 16), (105, 104), (225, 92), (305, 112)], line=(30, 49, 400, 86), w=430, h=125)
    # Abbotsleigh 2024 Q12(c): the example arrangement of shaded tiles
    tiles("abb24tiles", top={1, 3, 4, 10}, bottom={1, 4, 6, 7, 8, 9})


if __name__ == "__main__":
    fig_14a()
    fig_14c()
    fig_14d()
    fig_14e()
