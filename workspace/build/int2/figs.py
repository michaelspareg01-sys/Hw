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




# ---------------- Revision (Part 2 prerequisites) ----------------
from math import exp, log


def zero(x):
    return 0


def fig_rev():
    # y = e^x and y = log_e x, reflections of each other in y = x (6F, 6G)
    g = Graph(-2.6, 3.4, -2.6, 3.4, w=220, h=210, pad=(14, 32, 18, 16))
    g.axes("x", "y")
    g.curve(lambda x: x, color="faint", width=1.2, dash="4 3")
    g.curve(exp, color="blue", width=2, x1=log(3.4))
    g.curve(lambda x: log(x) if x > 0 else None, color="teal", width=2, x0=exp(-2.6))
    g.dot(0, 1, r=2.6).dot(1, 0, r=2.6)
    g.label(0, 1, "1", dx=-8, dy=-2, anchor="end", size=13)
    g.label(1, 0, "1", dy=14, size=13)
    g.label(0, 2.6, "y = eˣ", anchor="end", dx=-8, color="blue", size=13)
    g.label(1.2, -0.75, "y = logₑ x", anchor="start", dy=10, color="teal", size=13)
    g.label(2.4, 1.9, "y = x", anchor="start", color="faint", size=12.5)
    save("exp_log", g)

    # the two special triangles, with angles in radians (Year 11 Advanced 5A, 9G)
    f = Fig(300, 150)
    A, B, C = (40, 18), (40, 118), (140, 118)
    f.poly([A, B, C], color="blue", opacity=0.08)
    f.right(B[0], B[1], 1, -1)
    f.text(28, 70, "1", size=13).text(90, 134, "1", size=13).text(102, 60, "√2", size=13)
    f.text(52, 46, "π/4", size=12, anchor="start").text(110, 100, "π/4", size=12, anchor="end")
    P, R, Q = (196, 8), (196, 124), (263, 124)
    f.poly([P, R, Q], color="teal", opacity=0.08)
    f.right(R[0], R[1], 1, -1)
    f.text(182, 68, "√3", size=13).text(229, 140, "1", size=13).text(240, 58, "2", size=13)
    f.text(206, 44, "π/6", size=12, anchor="start").text(247, 106, "π/3", size=12, anchor="end")
    save("special", f)

    # the ASTC diagram, with the boundary angles in radians
    f = Fig(170, 150)
    cx, cy, r = 85, 75, 52
    f.arrow(cx - r - 6, cy, cx + r + 8, cy, width=1.3, head=6).arrow(cx, cy + r + 6, cx, cy - r - 8, width=1.3, head=6)
    f.text(cx + 26, cy - 26, "A", size=15, weight=700, color="blue").text(cx - 26, cy - 26, "S", size=15, weight=700, color="blue")
    f.text(cx - 26, cy + 26, "T", size=15, weight=700, color="blue").text(cx + 26, cy + 26, "C", size=15, weight=700, color="blue")
    f.text(cx + r + 14, cy + 14, "0", size=11).text(cx + 13, cy - r - 4, "π/2", size=11, anchor="start")
    f.text(cx - r - 10, cy + 14, "π", size=11).text(cx + 13, cy + r + 2, "3π/2", size=11, anchor="start")
    save("astc", f)

    # Year 11 Advanced Example 15 (9G): 5pi/4 and 11pi/6 with their related angles
    def quad(ang, lab, rel, w=170, h=130):
        cx, cy, r = w / 2, h / 2, 50
        f = Fig(w, h)
        f.line(cx - r - 8, cy, cx + r + 8, cy, width=1.3).line(cx, cy + r + 8, cx, cy - r - 8, width=1.3)
        t = radians(ang)
        ex, ey = cx + r * cos(t), cy - r * sin(t)
        f.line(cx, cy, ex, ey, color="blue", width=2.4).dot(ex, ey, r=3.4, color="blue")
        ref = 180 if cos(t) < 0 else 0
        a0, a1 = (ang, ref) if ang < ref else (ref, ang)
        f.arc(cx, cy, 24, a0, a1, color="ink", width=1.3)
        mid = radians((a0 + a1) / 2)
        f.text(cx + 40 * cos(mid), cy - 40 * sin(mid) + 2, rel, size=13)
        f.text(ex + (12 if cos(t) >= 0 else -12), ey + 16, lab, size=13, anchor="start" if cos(t) >= 0 else "end")
        return f
    save("q5pi4", quad(225, "5π/4", "π/4"))
    save("q11pi6", quad(-30, "11π/6", "π/6"))

    # Textbook Example 22 (5F): the region under y = 4 - x^2
    g = Graph(-2.8, 2.8, -0.6, 4.6, w=210, h=150, pad=(14, 30, 16, 18))
    g.fill(lambda x: 4 - x * x, zero, -2, 2, color="blue", opacity=0.22)
    g.axes("x", "y")
    g.curve(lambda x: 4 - x * x, color="ink", width=1.8, x0=-2.25, x1=2.25)
    g.xticks([(-2, ""), (2, "")])
    g.label(-2, 0, "-2", dx=-9, dy=12, size=11).label(2, 0, "2", dx=9, dy=12, size=11)
    g.label(0, 4, "4", dx=-7, dy=-6, anchor="end", size=11)
    g.label(1.5, 3.1, "y = 4 - x²", anchor="start", size=11)
    save("ex22", g)


if __name__ == "__main__":
    fig_rev()   # later lessons add their own figure functions here
