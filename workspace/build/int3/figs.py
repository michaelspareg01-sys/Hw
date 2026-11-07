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



# ---------------- helpers for curve graphs ----------------
from math import asin, acos
from plots import ACC as _ACC

H = pi / 2


def tip(g, f, x, toward, color="blue", head=7):
    """Arrowhead at the end (x, f(x)) of a curve, pointing away from the point at x - toward*h."""
    h = 1e-3 * (g.xmax - g.xmin)
    xa, ya = g.X(x), g.Y(f(x))
    xb, yb = g.X(x - toward * h), g.Y(f(x - toward * h))
    a = atan2(ya - yb, xa - xb)
    p1 = (xa - head * cos(a - 0.4), ya - head * sin(a - 0.4))
    p2 = (xa - head * cos(a + 0.4), ya - head * sin(a + 0.4))
    g.items.append(f'<path d="M{xa:.1f},{ya:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} z" fill="{_ACC[color]}"/>')
    return g


def diag(g, x0, x1, f=lambda x: x, color="faint"):
    """Dashed straight line (default y = x) from x0 to x1."""
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(f(x0)):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(f(x1)):.1f}" '
                   f'stroke="{_ACC[color]}" stroke-width="1.1" stroke-dasharray="4 3"/>')
    return g


def new(xmin, xmax, ymin, ymax, w, h):
    g = Graph(xmin, xmax, ymin, ymax, w=w, h=h, pad=(14, 30, 18, 14))
    g.axes("x", "y")
    return g


# ---------------- Revision: inverse trigonometric functions (Y11 Ext 1 Ch 17) ----------------
def fig_rev():
    W, Hh = 168, 132
    # y = sin x restricted to -pi/2 <= x <= pi/2
    g = new(-2.4, 2.4, -1.45, 1.45, W, Hh)
    diag(g, -1.4, 1.4)
    g.curve(sin, color="faint", width=1.3, dash="4 3", x0=-2.3, x1=-H)
    g.curve(sin, color="faint", width=1.3, dash="4 3", x0=H, x1=2.3)
    g.curve(sin, color="blue", width=2.2, x0=-H, x1=H)
    g.dot(-H, -1).dot(H, 1)
    g.vline(H, 0, 1, dash="3 3").vline(-H, -1, 0, dash="3 3")
    g.xticks([(-H, ""), (H, "")]).yticks([(1, "1"), (-1, "-1")])
    g.label(H, 0, "π/2", dy=16, size=10.5).label(-H, 0, "-π/2", dy=-18, size=10.5)
    save("rev_sin", g)
    # y = sin^-1 x
    g = new(-1.7, 1.7, -1.95, 1.95, W, Hh)
    diag(g, -1.7, 1.7)
    g.curve(asin, color="blue", width=2.2, x0=-1, x1=1, n=800)
    g.dot(-1, -H).dot(1, H)
    g.hline(H, x0=0, x1=1, dash="3 3").hline(-H, x0=-1, x1=0, dash="3 3")
    g.xticks([(-1, "-1"), (1, "1")]).yticks([(H, "π/2"), (-H, "")])
    g.label(0, -H, "-π/2", dx=12, anchor="start", size=10.5)
    save("rev_asin", g)
    # y = cos x restricted to 0 <= x <= pi, with tangent x + y = pi/2 at (pi/2, 0)
    g = new(-0.9, 3.9, -1.45, 1.45, W, Hh)
    diag(g, H - 1.35, H + 1.35, lambda x: H - x)
    g.curve(cos, color="faint", width=1.3, dash="4 3", x0=-0.85, x1=0)
    g.curve(cos, color="faint", width=1.3, dash="4 3", x0=pi, x1=3.85)
    g.curve(cos, color="blue", width=2.2, x0=0, x1=pi)
    g.dot(0, 1).dot(pi, -1)
    g.vline(pi, -1, 0, dash="3 3")
    g.xticks([(H, ""), (pi, "π")], below=False).yticks([(1, "1"), (-1, "-1")])
    g.label(H, 0, "π/2", dx=-9, dy=16, size=10.5)
    save("rev_cos", g)
    # y = cos^-1 x
    g = new(-1.7, 2.1, -0.55, 3.6, W, Hh)
    diag(g, H - 1.9, H + 0.55, lambda x: H - x)
    g.curve(acos, color="blue", width=2.2, x0=-1, x1=1, n=800)
    g.dot(-1, pi).dot(1, 0)
    g.hline(pi, x0=-1, x1=0, dash="3 3")
    g.xticks([(-1, "-1"), (1, "1")]).yticks([(H, "π/2"), (pi, "")])
    g.label(0, pi, "π", dx=7, anchor="start", size=11)
    save("rev_acos", g)
    # y = tan x restricted to -pi/2 < x < pi/2
    g = new(-2.2, 2.2, -2.7, 2.7, W, Hh)
    diag(g, -2.2, 2.2)
    g.vline(H, dash="4 3").vline(-H, dash="4 3")
    g.curve(tan, color="blue", width=2.2, x0=-1.2, x1=1.2)
    tip(g, tan, 1.2, 1)
    tip(g, tan, -1.2, -1)
    g.xticks([(-H, ""), (H, "")])
    g.label(H, 0, "π/2", dx=9, dy=16, size=10.5).label(-H, 0, "-π/2", dx=-14, dy=18, size=10.5)
    save("rev_tan", g)
    # y = tan^-1 x
    g = new(-3.7, 3.7, -2.0, 2.0, W, Hh)
    diag(g, -1.95, 1.95)
    g.hline(H, dash="4 3").hline(-H, dash="4 3")
    g.curve(atan, color="blue", width=2.2, x0=-3.6, x1=3.6)
    tip(g, atan, 3.6, 1)
    tip(g, atan, -3.6, -1)
    g.yticks([(H, ""), (-H, "")])
    g.label(0, H, "π/2", dx=-8, dy=13, anchor="end", size=10.5)
    g.label(0, -H, "-π/2", dx=9, dy=-13, anchor="start", size=10.5)
    save("rev_atan", g)
    # sin^-1 x and cos^-1 x on one set of axes, reflections of each other in y = pi/4
    g = new(-2.2, 2.0, -1.9, 3.5, 220, 210)
    g.hline(pi / 4, dash="4 3", x0=-1.5, x1=1.5)
    g.curve(asin, color="blue", width=2.0, x0=-1, x1=1, n=800)
    g.curve(acos, color="rose", width=2.0, x0=-1, x1=1, n=800)
    g.dot(-1, -H, color="blue").dot(1, H, color="blue").dot(-1, pi, color="rose").dot(1, 0, color="rose")
    g.xticks([(-1, "-1"), (1, "1")]).yticks([(pi, "π"), (H, ""), (pi / 4, ""), (-H, "-π/2")])
    g.label(0, H, "π/2", dx=9, dy=-14, anchor="start", size=10.5)
    g.label(-1.5, pi / 4, "π/4", dx=-4, anchor="end", size=10.5)
    g.label(1, H, "y = sin⁻¹x", dx=7, anchor="start", size=10, color="blue")
    g.label(1, 0, "y = cos⁻¹x", dx=7, dy=-12, anchor="start", size=10, color="rose")
    save("rev_comp", g)
    # Example 6a (17C): y - pi/2 = tan^-1(x + 1)
    f = lambda x: H + atan(x + 1)
    g = new(-4.5, 3.5, -0.4, 3.75, 280, 200)
    g.hline(pi, dash="4 3")
    for xv in (-2, -1, 0):
        g.vline(xv, 0, f(xv), dash="3 3")
        g.hline(f(xv), x0=xv, x1=0, dash="3 3")
        g.dot(xv, f(xv), r=2.6)
    g.curve(f, color="blue", width=2.2, x0=-4.4, x1=3.3)
    tip(g, f, 3.3, 1)
    tip(g, f, -4.4, -1)
    g.xticks([(-2, "-2"), (-1, "-1")]).yticks([(pi, "π"), (3 * pi / 4, ""), (H, "π/2"), (pi / 4, "π/4")])
    g.label(0, 3 * pi / 4, "3π/4", dx=9, dy=11, anchor="start", size=10.5)
    save("ex6a", g)


def fig_arev():
    W, Hh = 172, 150
    # Exercise 17C Q2a: y = sin^-1(x - 1)
    f = lambda x: asin(max(-1, min(1, x - 1)))
    g = new(-0.6, 2.6, -1.95, 1.95, W, Hh)
    g.curve(f, color="blue", width=2.2, x0=0, x1=2, n=800)
    g.dot(0, -H).dot(2, H)
    g.hline(H, x0=0, x1=2, dash="3 3").vline(2, 0, H, dash="3 3")
    g.xticks([(1, "1"), (2, "2")]).yticks([(H, "π/2"), (-H, "-π/2")])
    save("a_q3a", g)
    # Q2b: y = cos^-1(x + 1)
    f = lambda x: acos(max(-1, min(1, x + 1)))
    g = new(-2.6, 0.9, -0.5, 3.6, W, Hh)
    g.curve(f, color="blue", width=2.2, x0=-2, x1=0, n=800)
    g.dot(-2, pi).dot(0, 0)
    g.vline(-2, 0, pi, dash="3 3").hline(pi, x0=-2, x1=0, dash="3 3")
    g.xticks([(-2, "-2"), (-1, "-1")]).yticks([(H, "π/2"), (pi, "π")])
    save("a_q3b", g)
    # Q2c: y - pi/2 = tan^-1 x
    f = lambda x: H + atan(x)
    g = new(-4.5, 4.5, -0.4, 3.75, W, Hh)
    g.hline(pi, dash="4 3")
    g.curve(f, color="blue", width=2.2, x0=-4.3, x1=4.3)
    tip(g, f, 4.3, 1)
    tip(g, f, -4.3, -1)
    g.yticks([(pi, "π"), (H, "")])
    g.label(0, H, "π/2", dx=10, dy=10, anchor="start", size=10.5)
    save("a_q3c", g)


def circle_tri(name, adj, opp, hyp_lab, adj_lab, opp_lab, w=150, h=130):
    """Circle with a ray at the angle whose cosine is adj/r and sine is opp/r, dropped perpendicular,
    and the three sides labelled (the textbook's quadrant diagram for Examples 5 and 13)."""
    cx, cy, R = w / 2, h / 2, 46
    r = sqrt(adj * adj + opp * opp)
    px, py = cx + R * adj / r, cy - R * opp / r
    f = Fig(w, h)
    f.raw(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{ACC["ink"]}" stroke-width="1.3"/>')
    f.line(cx - R - 10, cy, cx + R + 12, cy, width=1.1).line(cx, cy + R + 10, cx, cy - R - 10, width=1.1)
    ex, ey = cx + (R + 16) * adj / r, cy - (R + 16) * opp / r
    f.arrow(cx, cy, ex, ey, color="blue", width=1.6)
    f.line(px, py, px, cy, width=1.3)
    sy = 1 if opp > 0 else -1
    f.right(px, cy, -1, -sy, 6)
    f.text((cx + px) / 2, cy + (12 if opp > 0 else -6), adj_lab, size=11)
    f.text(px + 4, (py + cy) / 2, opp_lab, anchor="start", size=11)
    mx, my = (cx + px) / 2, (cy + py) / 2
    nx, ny = -sy * opp / r, -sy * adj / r   # unit normal on the side away from the triangle
    f.text(mx + 9 * nx, my + 9 * ny + 4, hyp_lab, size=11)
    f.text(ex + 8, ey + (4 if opp > 0 else 10), "α", anchor="start", size=12, italic=True)
    save(name, f)


def fig_rev_tri():
    circle_tri("ex5a", 4, -2.3, "5", "√24", "1")   # not to scale, like the textbook diagram
    circle_tri("ex5b", 4, 3, "5", "4", "3")


if __name__ == "__main__":
    fig_rev()
    fig_rev_tri()
    fig_arev()   # later lessons add their own figure functions here
