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


def vel_box(name, horiz, vert, hyp, ang, ang_at_top=False, w=150, h=120):
    """Velocity resolution rectangle: diagonal = velocity, sides = components."""
    f = Fig(w, h)
    x0, x1, y0, y1 = 34, w - 22, 14, h - 24
    f.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color=None, stroke="faint", width=1.1)
    if not ang_at_top:   # moving upwards: from bottom-left to top-right
        f.arrow(x0, y1, x1, y0, "blue", 2.2)
        f.arc(x0, y1, 18, 0, degrees(atan2(y1 - y0, x1 - x0)))
        f.text(x0 + 30, y1 - 7, ang, "start", size=11)
    else:                # moving downwards: from top-left to bottom-right
        f.arrow(x0, y0, x1, y1, "blue", 2.2)
        f.arc(x0, y0, 18, -degrees(atan2(y1 - y0, x1 - x0)), 0)
        f.text(x0 + 30, y0 + 9, ang, "start", size=11)
    f.text((x0 + x1) / 2, y1 + 15, horiz, size=11.5)
    f.text(x0 - 5, (y0 + y1) / 2, vert, "end", size=11.5)
    f.text((x0 + x1) / 2 + 12, (y0 + y1) / 2 - 4, hyp, "start", size=11.5, color="blue")
    save(name, f)


# ---------------- 9E ----------------
# inverted cone with water (tutor demo / homework 5 style)
f = Fig(190, 170)
f.raw(f'<ellipse cx="95" cy="22" rx="70" ry="12" fill="none" stroke="{INK}" stroke-width="1.5"/>')
f.line(25, 22, 95, 160).line(165, 22, 95, 160)
f.raw(f'<ellipse cx="95" cy="80" rx="40.5" ry="7" fill="{ACC["blue"]}" fill-opacity=".25" stroke="{ACC["blue"]}" stroke-width="1.4"/>')
f.poly([(54.5, 80), (135.5, 80), (95, 160)], color="blue", opacity=0.18, stroke="blue", width=1.2)
f.line(95, 80, 135.5, 80, "ink", 1.3).text(115, 72, "r", italic=True)
f.line(95, 80, 95, 160, "ink", 1.1, "4 3").text(101, 124, "h", "start", italic=True)
save("cone", f)

# ladder against a wall
f = Fig(210, 170)
f.line(40, 10, 40, 150, "ink", 2.2).line(30, 150, 200, 150, "ink", 2.2)
for k in range(8):
    f.line(30, 20 + 17 * k, 40, 12 + 17 * k, "faint", 1)
f.line(40, 40, 150, 150, "blue", 3)
f.right(40, 150, 1, -1, 9)
f.text(102, 88, "5 m", "start", size=11.5, color="blue")
f.dim(40, 162, 150, 162).text(95, 158, "x", italic=True)
f.text(30, 95, "y", "end", italic=True)
f.arc(150, 150, 22, 135, 180).text(118, 142, "θ", italic=True)
save("ladder", f)

# observer and plane (demo)
f = Fig(250, 130)
f.line(10, 112, 240, 112, "ink", 1.6)
f.dot(30, 112).text(30, 125, "A", italic=True)
f.dot(200, 112).text(200, 125, "B", italic=True)
f.line(30, 112, 200, 28, "blue", 1.8).line(200, 28, 200, 112, "faint", 1.2, "4 3")
f.right(200, 112, -1, -1, 8)
f.raw(f'<path d="M188,28 l24,0 l-6,-4 l-10,0 z" fill="{INK}"/>')
f.arrow(176, 18, 140, 18, "ink", 1.2)
f.text(158, 11, "600 km/h", size=10.5)
f.text(207, 72, "2 km", "start", size=11)
f.text(115, 125, "x", italic=True)
f.arc(30, 112, 24, 0, 26).text(60, 104, "θ", "start", italic=True)
save("plane", f)

# 9E Q6 diagram (650 km/h, 1.5 km)
f = Fig(230, 120)
f.line(10, 102, 220, 102, "ink", 1.6)
f.dot(30, 102).text(30, 115, "A", italic=True)
f.dot(180, 102).text(180, 115, "B", italic=True)
f.line(30, 102, 180, 26, "blue", 1.8).line(180, 26, 180, 102, "faint", 1.2, "4 3")
f.right(180, 102, -1, -1, 8)
f.raw(f'<path d="M168,26 l24,0 l-6,-4 l-10,0 z" fill="{INK}"/>')
f.arrow(205, 14, 168, 14, "ink", 1.2)
f.text(200, 8, "650 km/h", "start", size=10)
f.text(186, 66, "1.5 km", "start", size=11)
f.text(105, 115, "x", italic=True)
f.arc(30, 102, 22, 0, 27).text(57, 95, "θ", "start", italic=True)
save("q6plane", f)

# 9E Q8 trough cross-section
f = Fig(230, 120)
f.poly([(20, 20), (120, 20), (70, 70)], color=None, stroke="ink")
f.poly([(36, 36), (104, 36), (70, 70)], color="blue", opacity=0.25, stroke="blue", width=1.3)
f.line(70, 36, 70, 70, "ink", 1.1, "4 3").text(76, 56, "h", "start", italic=True)
f.right(70, 70, 1, -1, 0)
f.raw(f'<path d="M64,64 L70,58 L76,64" fill="none" stroke="{INK}" stroke-width="1.1"/>')
f.text(70, 92, "cross-section", size=10.5, color="faint")
# oblique view of the prism
f.poly([(140, 30), (200, 30), (215, 18), (155, 18)], color=None, stroke="ink", width=1.2)
f.poly([(140, 30), (200, 30), (170, 62)], color=None, stroke="ink", width=1.2)
f.line(170, 62, 185, 50, "ink", 1.2).line(215, 18, 185, 50, "ink", 1.2)
f.text(208, 46, "x", "start", italic=True)
save("trough", f)

# 9E Q11 car and truck
f = Fig(300, 70)
f.line(10, 46, 290, 46, "ink", 1.4)
f.raw(f'<rect x="20" y="34" width="22" height="10" rx="3" fill="{ACC["rose"]}"/>')
f.raw(f'<rect x="120" y="22" width="44" height="22" fill="{FAINT}"/><rect x="164" y="30" width="12" height="14" fill="{INK}"/>')
f.line(240, 46, 240, 20, "ink", 1.2).raw(f'<rect x="228" y="12" width="40" height="12" fill="#fff" stroke="{INK}" stroke-width="1"/>')
f.text(248, 18, "lane", size=8.5)
f.dim(31, 58, 142, 58).text(86, 54, "C", italic=True)
f.dim(176, 58, 240, 58).text(208, 54, "L", italic=True)
f.text(31, 26, "V", italic=True).text(142, 14, "V", italic=True)
save("overtake", f)

# 9E Q12 chord in a circle
f = Fig(170, 160)
cx, cy, R = 80, 80, 62
th = 50
ax, ay = cx + R * cos(radians(th)), cy - R * sin(radians(th))
bx, by = ax, cy + R * sin(radians(th))
f.path(f"M{ax:.1f},{ay:.1f} A{R},{R} 0 0 1 {bx:.1f},{by:.1f} Z", "blue", 1.2, fill="blue", opacity=0.22)
f.raw(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
f.line(cx, cy, ax, ay).line(cx, cy, bx, by).line(ax, ay, bx, by)
f.line(cx, cy, ax, cy, "ink", 1.1, "4 3").text((cx + ax) / 2, cy - 6, "x", italic=True)
f.arc(cx, cy, 14, -th, th).text(cx - 4, cy - 6, "2θ", "end", size=11)
f.text(cx + 14, cy + 34, "r", italic=True).text(ax + 6, ay - 6, "A", "start", italic=True)
save("chord", f)

# 9E Q13 radars
f = Fig(260, 140)
A, B, Q, P = (20, 120), (100, 120), (220, 120), (220, 20)
f.line(10, 120, 240, 120, "ink", 1.4)
f.line(*A, *P, "blue", 1.6).line(*B, *P, "blue", 1.6).line(*Q, *P, "faint", 1.2, "4 3")
f.right(220, 120, -1, -1, 8)
for (x, y, lab) in ((20, 120, "A"), (100, 120, "B"), (220, 120, "Q"), (220, 20, "P")):
    f.dot(x, y)
f.text(20, 134, "A", italic=True).text(100, 134, "B", italic=True).text(220, 134, "Q", italic=True).text(228, 18, "P", "start", italic=True)
f.text(60, 134, "100 m", size=10.5).text(160, 134, "x", italic=True).text(228, 72, "h", "start", italic=True)
f.arc(20, 120, 26, 0, degrees(atan2(100, 200))).text(50, 112, "α", "start", italic=True)
f.arc(100, 120, 22, 0, degrees(atan2(100, 120))).text(126, 110, "β", "start", italic=True)
save("radars", f)


# ---------------- 10A ----------------
vel_box("res60", "ẋ = 12 cos 60°", "ẏ", "12", "60°")
vel_box("resm60", "ẋ = 12 cos 60°", "ẏ", "12", "60°", ang_at_top=True)
vel_box("res43", "ẋ = 4", "ẏ = 3", "v", "θ")
vel_box("res52", "ẋ = 5", "ẏ = -2", "v", "θ", ang_at_top=True)

# Example 3: from a 25 m stand, 40 m/s at 30 deg
g = Graph(-12, 190, -30, 26, 360, 200, pad=(34, 40, 18, 22))
g.axes()
g.curve(lambda x: -5 * (x / (20 * sqrt(3))) ** 2 + 20 * (x / (20 * sqrt(3))), "blue", 2.2, x0=0, x1=100 * sqrt(3))
g.hline(-25, color="ink", dash=None, x0=-12, x1=190, width=1.4)
g.items.insert(0, f'<rect x="{g.X(-12)}" y="{g.Y(0)}" width="{g.X(0) - g.X(-12)}" height="{g.Y(-25) - g.Y(0)}" fill="{ACC["blue"]}" fill-opacity=".16"/>')
g.vline(0, -25, 0, color="ink", dash=None, width=1.4)
g.label(0, -12.5, "25 m", dx=-6, anchor="end")
g.label(0, 0, "30°", dx=26, dy=-9)
g.label(100 * sqrt(3), -25, "range", dy=12)
g.dot(40 * sqrt(3), 20, "blue").label(40 * sqrt(3), 20, "top of flight", dy=-11)
save("stand", g)

# Example 4: gun and fortress
g = Graph(0, 2300, 0, 1350, 300, 190, pad=(34, 30, 18, 26))
g.axes().xticks([(2000, "2000")]).yticks([(1000, "1000")])
g.curve(lambda x: -5 * x ** 2 / (200 ** 2 * 0.5) + x, "blue", 2.0, x0=0, x1=2000)
g.curve(lambda x: -5 * x ** 2 * 10 / 200 ** 2 + 3 * x, "rose", 2.0, x0=0, x1=2000)
g.dot(2000, 1000).label(2000, 1000, "F", dx=10, dy=-6, anchor="start")
g.vline(2000, 0, 1000)
g.hline(1000, x0=0, x1=2000)
save("fortress", g)

# ---------------- 10B ----------------
g = Graph(-1, 13, -0.6, 5.2, 330, 180, pad=(30, 40, 18, 30))
g.axes()
g.curve(lambda x: x * (12 - x) / 7.2, "blue", 2.2, x0=0, x1=12)
g.dot(12, 0).label(12, 0, "V²sin 2α / g", dy=16)
g.dot(9, 9 * 3 / 7.2).label(9, 9 * 3 / 7.2, "P(x, y)", dx=8, dy=-8, anchor="start")
g.label(0, 0, "α", dx=20, dy=-8)
save("range", g)

# region within reach (Example 5c)
V2g = 4.0
g = Graph(-5, 5, -0.5, 2.6, 330, 170, pad=(30, 30, 18, 24))
g.axes().xticks([(-4, "-V²/g"), (4, "V²/g")])
g.fill(lambda x: (16 - x * x) / 8, lambda x: 0, -4, 4, "teal", opacity=0.16)
g.curve(lambda x: (16 - x * x) / 8, "teal", 2.2, x0=-4, x1=4)
for T in (0.5, 1, 2, 3.5):
    g.curve(lambda x, T=T: x * T - x * x * (1 + T * T) / 8, "blue", 1.3, x0=0, x1=8 * T / (1 + T * T))
g.label(0, 2, "V²/2g", dx=8, dy=-10, anchor="start")
save("safety", g)

# Exercise 10B Q12 diagram
g = Graph(-1, 20, -0.5, 6.5, 260, 150, pad=(26, 30, 16, 26))
g.axes()
R = 18
g.curve(lambda x: x * (1 - x / R), "blue", 2.0, x0=0, x1=R)
x1, x2 = 6, 12
g.hline(4, x0=0, x1=x2).vline(x1, 0, 4).vline(x2, 0, 4)
g.yticks([(4, "4")]).xticks([(x1, "x₁"), (x2, "x₂")])
g.dot(x1, 4).dot(x2, 4)
g.label(9, 4, "6", dy=-9)
save("q12path", g)

print("figures written")
