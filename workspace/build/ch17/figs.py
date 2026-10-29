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


# ---------------- Revision: the normal distribution (Advanced Ch 16D-16F) ----------------
from math import exp, erf

R2PI = sqrt(2 * pi)


def phi(z):
    return exp(-z * z / 2) / R2PI


def Phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def zero(z):
    return 0


def normal(a=None, b=None, w=150, h=96, ticks=(), peak=True, inflect=False, lab_size=10.5, color="blue"):
    """Standard normal curve y = phi(z) on [-3.4, 3.4], shaded from a to b (None = no shading)."""
    g = Graph(-3.4, 3.4, 0, 0.52 if peak else 0.45, w=w, h=h, pad=(10, 16, 16, 18))
    if a is not None or b is not None:
        lo = -3.4 if a is None else a
        hi = 3.4 if b is None else b
        g.fill(phi, zero, lo, hi, color=color, opacity=0.3)
    g.axes("z", "φ(z)")
    g.curve(phi, color="ink", width=1.6)
    for v in ticks:
        g.xticks([(v, f"{v:g}")])
    if peak:
        g.label(0, phi(0), "1/√2π", dx=5, dy=-14, anchor="start", size=lab_size)
        g.label(0, phi(0), "≈ 0.4", dx=31, dy=-14, anchor="start", size=lab_size)
    if inflect:
        for s in (-1, 1):
            g.vline(s, 0, phi(1), color="faint", dash="3 3")
            g.dot(s, phi(1), r=2.4)
        g.hline(phi(1), color="faint", dash="3 3", x0=-1, x1=1)
        g.label(-1, phi(1), "0.24", dx=-6, dy=-2, anchor="end", size=lab_size)
    return g


def fig_rev():
    # features of the standard normal curve (Box 7)
    save("phi_pdf", normal(w=210, h=120, ticks=(-1, 1), inflect=True, lab_size=11))
    # Phi(z) as the area to the left of z, with a z marker on the axis
    for name, w, h, tk in (("phi_area", 210, 120, (-3, -2, -1, 1, 3)), ("phi_area_small", 190, 104, (-3, -2, -1, 3))):
        zz = 1.6
        g = normal(None, zz, w=w, h=h, ticks=tk, peak=False)
        g.vline(zz, 0, phi(zz), color="ink", dash="", width=1.2)
        g.xticks([(zz, "")])
        g.label(zz, 0, "z", dy=14, italic=True, size=11.5)
        g.label(0.62, 0.11, "Φ(z)", size=11.5, color="blue")
        save(name, g)
    # Example 10 (16D)
    save("ex10a", normal(None, 2, ticks=(2,)))
    save("ex10b1", normal(2, None, ticks=(2,)))
    save("ex10b2", normal(None, -2, ticks=(-2,)))
    save("ex10b3", normal(0, 2, ticks=(2,)))
    save("ex10b4", normal(-2, 2, ticks=(-2, 2)))
    # symmetry worked example (pack's own values)
    save("sym_a", normal(-2.3, -0.6, w=170, h=104, ticks=(-2.3, -0.6)))
    save("sym_b", normal(-1.4, 0.9, w=170, h=104, ticks=(-1.4, 0.9)))
    # the empirical rule: within 1, 2 and 3 standard deviations
    for k in (1, 2, 3):
        g = normal(-k, k, w=128, h=82, ticks=(-k, k), peak=False)
        for s in (-1, 1):
            g.dot(s * k, phi(k), r=2.4)
        g.label([2.15, 2.15, 2.55][k - 1], 0.31, ["68%", "95%", "99.7%"][k - 1], size=11, color="blue")
        save(f"emp{k}", g)
    # graph of the CDF y = Phi(z), with the horizontal lines at heights 0.75 and 0.9 (Example 13)
    g = Graph(-3.4, 3.4, 0, 1.05, w=220, h=165, pad=(10, 16, 14, 18))
    g.axes("z", "y")
    g.hline(1, color="faint", dash="3 3")
    for p, q in ((0.75, 0.6745), (0.9, 1.2816)):
        g.hline(p, color="rose", dash="4 3", x0=0, x1=q)
        g.vline(q, 0, p, color="rose", dash="4 3")
    g.curve(Phi, color="blue", width=2)
    g.yticks([(0.5, "0.5"), (0.75, "0.75"), (0.9, "0.9"), (1, "")])
    g.label(-3.3, 1, "y = 1", dy=-8, anchor="start", size=10.5, color="faint")
    g.xticks([(-3, "-3"), (-2, "-2"), (-1, "-1"), (2, ""), (3, "3")])
    g.label(0.6745, 0, "Q₃", dx=-5, dy=14, size=10.5, color="rose")
    g.label(1.2816, 0, "1.28", dx=9, dy=14, size=10.5, color="rose")
    g.label(2.3, 0.8, "y = Φ(z)", size=11, color="blue")
    save("Phi_cdf", g)
    # general normal N(mu, sigma^2): coordinate t = (x - mu)/sigma + 4, so the y-axis sits to the left
    g = Graph(0, 8, 0, 0.45, w=250, h=140, pad=(16, 18, 18, 20))

    def f(t):
        return phi(t - 4)
    g.fill(f, zero, 3, 5, color="blue", opacity=0.16)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.6)
    for t in (3, 5):
        g.vline(t, 0, phi(1), color="faint", dash="3 3")
        g.dot(t, phi(1), r=2.4)
    g.vline(4, 0, phi(0), color="faint", dash="3 3")
    g.hline(phi(0), color="faint", dash="3 3", x0=0, x1=4)
    g.label(0, phi(0), "1/σ√2π", dx=6, dy=-9, anchor="start", size=11.5)
    g.xticks([(3, "μ-σ"), (4, "μ"), (5, "μ+σ")])
    save("gen_normal", g)


if __name__ == "__main__":
    fig_rev()   # later lessons add their own figure functions here
