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


# Figures for the Chapter 13 pack are added by the lesson tasks (save(name, graph) writes svg/<name>.svg).

from fractions import Fraction as Fr


def dist_graph(name, xs, ps, yt, w=250, h=160, xpad=0.6, ylab="P(X = x)", xlabels=None):
    """Dot graph of a probability distribution: values on the x-axis, probabilities up."""
    ymax = float(max(ps)) * 1.18
    lo = min(0, min(xs))
    g = Graph(lo - 0.35, max(xs) + xpad, 0, ymax, w=w, h=h, pad=(44, 30, 26, 30))
    g.axes("x", "")
    g.items.append(_txt(g.X(max(g.xmin, 0)) + 8, g.Y(ymax) - 10, ylab, "start", size=11.5, italic=True))
    g.xticks([(x, str(x) if xlabels is None else xlabels[i]) for i, x in enumerate(xs)])
    g.yticks([(float(v), lab) for v, lab in yt])
    for x, p in zip(xs, ps):
        g.dot(x, float(p), r=3.4)
    save(name, g)


def bartext(x, y, s, size=13, anchor="middle"):
    """Italic letters; a letter followed by ' is drawn with a bar over it (the complement)."""
    spans, i = [], 0
    while i < len(s):
        ch = s[i]
        bar = i + 1 < len(s) and s[i + 1] == "'"
        if ch == " ":
            spans.append('<tspan> </tspan>')
        else:
            if bar and i > 0 and s[i - 1] == "'":
                spans.append('<tspan>\u2009</tspan>')      # keep two bars apart
            st = ' style="text-decoration:overline"' if bar else ""
            spans.append(f'<tspan{st}>{ch}</tspan>')
        i += 2 if bar else 1
    return (f'<text x="{x:.1f}" y="{y + size * 0.35:.1f}" text-anchor="{anchor}" font-size="{size}" '
            f'font-style="italic" fill="{INK}">' + "".join(spans) + "</text>")


def tree2(name, first, w=430, h=230):
    """Two-stage tree. first/second: lists of (branch label, probability label); leaves get outcome and probability."""
    f = Fig(w, h)
    x0, x1, x2 = 40, 150, 260
    f.text(x0 - 8, h / 2, "Start", anchor="end", size=11.5)
    f.text(x1, 14, "1st draw", size=10.5, color="faint").text(x2, 14, "2nd draw", size=10.5, color="faint")
    f.text(x2 + 70, 14, "outcome", size=10.5, color="faint").text(x2 + 140, 14, "probability", size=10.5, color="faint")
    n1 = len(first)
    rows = []
    for i, (lab1, p1, outs) in enumerate(first):
        y1 = 30 + (h - 40) * (i + 0.5) / n1
        f.line(x0, h / 2, x1 - 14, y1, width=1.3)
        f.raw(bartext(x1, y1, lab1))
        f.text((x0 + x1) / 2 - (4 if y1 < h / 2 else 12), (h / 2 + y1) / 2 + (-17 if y1 < h / 2 else 15), p1, size=11, color="blue")
        for j, (lab2, p2, outlab, prob) in enumerate(outs):
            y2 = y1 + (j - (len(outs) - 1) / 2) * (h - 40) / (n1 * len(outs))
            f.line(x1 + 12, y1, x2 - 14, y2, width=1.3)
            f.raw(bartext(x2, y2, lab2))
            f.text((x1 + x2) / 2 + 2, (y1 + y2) / 2 + (-17 if y2 < y1 else 15), p2, size=11, color="blue")
            f.raw(bartext(x2 + 70, y2, outlab))
            f.text(x2 + 140, y2, prob, size=12.5)
    save(name, f)


def build_13a():
    # lesson: four coins, number of heads (13A text)
    dist_graph("c13a_coins", [0, 1, 2, 3, 4], [Fr(1, 16), Fr(4, 16), Fr(6, 16), Fr(4, 16), Fr(1, 16)],
               [(Fr(1, 16), "1/16"), (Fr(4, 16), "4/16"), (Fr(6, 16), "6/16")])
    # lesson: Example 1, a die
    dist_graph("c13a_die", [1, 2, 3, 4, 5, 6], [Fr(1, 6)] * 6, [(Fr(1, 6), "1/6")], h=120)
    # lesson: the deterministic experiment
    dist_graph("c13a_det", [4], [1], [(1, "1")], w=150, h=110)
    # answers C1: two dice, number of sixes; die twice, number of results less than 3
    dist_graph("a13a_sixes", [0, 1, 2], [Fr(25, 36), Fr(10, 36), Fr(1, 36)],
               [(Fr(1, 36), "1/36"), (Fr(10, 36), "10/36"), (Fr(25, 36), "25/36")], w=210)
    dist_graph("a13a_less3", [0, 1, 2], [Fr(4, 9), Fr(4, 9), Fr(1, 9)],
               [(Fr(1, 9), "1/9"), (Fr(4, 9), "4/9")], w=210)
    # answers C3: five cards 2, 4, 6, 8, 10; tetrahedral die 1, 3, 5, 7
    dist_graph("a13a_cards", [2, 4, 6, 8, 10], [Fr(1, 5)] * 5, [(Fr(1, 5), "1/5")], w=250, h=110, xpad=1.0)
    dist_graph("a13a_tetra", [1, 3, 5, 7], [Fr(1, 4)] * 4, [(Fr(1, 4), "1/4")], w=230, h=110, xpad=1.0)
    # answers Exercise 13A Q8(a)(i): two draws with replacement, court card C or not
    C, N = "C", "C'"
    tree2("a13a_q8tree", [
        (C, "3/13", [(C, "3/13", "CC", "9/169"), (N, "10/13", "CC'", "30/169")]),
        (N, "10/13", [(C, "3/13", "C'C", "30/169"), (N, "10/13", "C'C'", "100/169")]),
    ])


if __name__ == "__main__":
    build_13a()
