import os, sys
from math import sin, cos, tan, atan, atan2, pi, sqrt, radians, degrees
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    from figfit import fit, untangle, separate  # nudges a flagged label (<= 8 px); grows the frame only where a label would be clipped
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(fit(untangle(separate(g.svg()))))


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


# ---------------- Revision: indices, derivatives, sigma notation, areas ----------------


def fig_rev():
    # the area formulae: rectangle, triangle, trapezium, circle, semicircle, quadrant
    f = Fig(640, 146)
    B = 104                                   # common base line (screen y)
    # rectangle
    f.poly([(12, B), (92, B), (92, 50), (12, 50)], color="blue", opacity=0.16)
    f.text(52, B + 15, "l", italic=True).text(102, 77, "b", italic=True)
    # triangle with its perpendicular height
    f.poly([(122, B), (212, B), (152, 34)], color="blue", opacity=0.16)
    f.line(152, 34, 152, B, color="faint", width=1.2, dash="4 3").right(152, B, 1, -1, 7)
    f.text(167, B + 15, "b", italic=True).text(144, 72, "h", italic=True)
    # trapezium: parallel sides a (top) and b (bottom), perpendicular distance h
    f.poly([(240, B), (338, B), (316, 44), (268, 44)], color="blue", opacity=0.16)
    f.line(292, 44, 292, B, color="faint", width=1.2, dash="4 3").right(292, B, 1, -1, 7)
    f.text(292, 33, "a", italic=True).text(289, B + 15, "b", italic=True).text(284, 76, "h", italic=True)
    # circle with a radius
    f.path("M368,70 A34,34 0 1 0 436,70 A34,34 0 1 0 368,70 Z", color="ink", width=1.6, fill="blue", opacity=0.16)
    f.line(402, 70, 436, 70, width=1.3).dot(402, 70, 2.4).text(419, 62, "r", italic=True)
    # semicircle
    f.path(f"M466,{B} A40,40 0 0 1 546,{B} Z", color="ink", width=1.6, fill="blue", opacity=0.16)
    f.line(506, B, 546, B, width=1.3).dot(506, B, 2.4).text(526, B + 15, "r", italic=True)
    # quadrant
    f.path(f"M574,{B} L574,{B - 52} A52,52 0 0 1 626,{B} Z", color="ink", width=1.6, fill="blue", opacity=0.16)
    f.right(574, B, 1, -1, 7).text(600, B + 15, "r", italic=True)
    for x, s in ((52, "rectangle"), (167, "triangle"), (289, "trapezium"), (402, "circle"), (506, "semicircle"), (600, "quadrant")):
        f.text(x, B + 33, s, size=10.5, color="faint")
    save("shapes", f)

    # upper and lower semicircles y = +-sqrt(a^2 - x^2), drawn with a = 3
    def up(x):
        return sqrt(max(0.0, 9 - x * x))

    for name, sgn in (("semi_up", 1), ("semi_down", -1)):
        lo, hi = (-0.8, 3.9) if sgn > 0 else (-3.9, 0.8)
        g = Graph(-4, 4, lo, hi, w=180, h=122, pad=(12, 30, 18, 14))
        g.axes("x", "y")
        g.curve(lambda x: sgn * up(x), color="blue", width=2, x0=-3, x1=3)
        g.dot(-3, 0, r=2.6).dot(3, 0, r=2.6)
        g.label(-3, 0, "-a", dy=13 if sgn > 0 else -12, size=11)
        g.label(3, 0, "a", dy=13 if sgn > 0 else -12, size=11)
        g.label(0, 3 * sgn, "a" if sgn > 0 else "-a", dx=-8, dy=-8 if sgn > 0 else 9, anchor="end", size=11)
        save(name, g)

    # y = |x|
    g = Graph(-3, 3, -0.6, 3.2, w=160, h=118, pad=(12, 30, 18, 12))
    g.axes("x", "y")
    g.curve(abs, color="blue", width=2)
    g.label(3.0, 0.65, "y = |x|", anchor="end", size=11, color="blue")
    save("abs_v", g)


if __name__ == "__main__":
    fig_rev()   # later lessons add their own figure functions here
