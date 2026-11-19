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



PI = pi


def pi_ticks(lo, hi, step=0.5, skip=()):
    """Tick list at multiples of step*pi, labelled kπ/2 style (stacked fractions)."""
    from fractions import Fraction
    out = []
    k = Fraction(lo).limit_denominator(12)
    st = Fraction(step).limit_denominator(12)
    while k <= Fraction(hi).limit_denominator(12) + Fraction(1, 1000):
        if k != 0 and float(k) not in skip:
            n, d = k.numerator, k.denominator
            s = "-" if n < 0 else ""
            n = abs(n)
            num = "π" if n == 1 else f"{n}π"
            lab = f"{s}{num}" if d == 1 else f"{s}{num}/{d}"
            out.append((float(k) * pi, lab))
        k += st
    return out


def lab(x, y, s, anchor="middle", size=12, color=INK, bg=True, italic=False):
    """SVG text with an optional white background. 'a/b' is a stacked fraction (sign in the numerator)."""
    s = s.replace("-", "−")
    out = []
    if "/" in s:
        num, den = s.split("/", 1)
        fs = size * 0.92
        w = max(len(num), len(den)) * fs * 0.58 + 3
        ax = {"middle": x, "start": x + w / 2, "end": x - w / 2}[anchor]
        if bg:
            out.append(f'<rect x="{ax - w/2 - 1.5:.1f}" y="{y - fs - 3:.1f}" width="{w + 3:.1f}" height="{2 * fs + 7:.1f}" fill="#fff"/>')
        out.append(f'<text x="{ax:.1f}" y="{y - 2:.1f}" text-anchor="middle" font-size="{fs:.1f}" fill="{color}">{num}</text>')
        out.append(f'<line x1="{ax - w/2 + 1:.1f}" y1="{y + 1:.1f}" x2="{ax + w/2 - 1:.1f}" y2="{y + 1:.1f}" stroke="{color}" stroke-width="1"/>')
        out.append(f'<text x="{ax:.1f}" y="{y + fs + 1:.1f}" text-anchor="middle" font-size="{fs:.1f}" fill="{color}">{den}</text>')
        return "".join(out)
    w = len(s) * size * 0.56 + 3
    x0 = {"middle": x - w / 2, "start": x - 1.5, "end": x - w + 1.5}[anchor]
    if bg:
        out.append(f'<rect x="{x0:.1f}" y="{y - size * 0.45:.1f}" width="{w:.1f}" height="{size * 1.1:.1f}" fill="#fff"/>')
    st = ' font-style="italic"' if italic else ''
    out.append(f'<text x="{x:.1f}" y="{y + size * 0.35:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}"{st}>{s}</text>')
    return "".join(out)


def ticks(g, xt=(), yt=(), size=12):
    for v, s in xt:
        x = g.X(v)
        g.items.append(f'<line x1="{x:.1f}" y1="{g._y0 - 3:.1f}" x2="{x:.1f}" y2="{g._y0 + 3:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    for v, s in yt:
        y = g.Y(v)
        g.items.append(f'<line x1="{g._x0 - 3:.1f}" y1="{y:.1f}" x2="{g._x0 + 3:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    for v, s in xt:
        if s:
            dy = 21 if "/" in s else 15
            g.items.append(lab(g.X(v), g._y0 + dy, s, size=size))
    for v, s in yt:
        if s:
            g.items.append(lab(g._x0 - 6, g.Y(v), s, "end", size=size))


def graph(name, fns, xr, yr, xt=(), yt=(), w=300, h=170, pad=(30, 26, 18, 30), dots=(), hollow=(),
          labels=(), hl=(), vl=(), xlabel="x", ylabel="y"):
    """fns: list of (f, color, dash, x0, x1). labels: (x, y, text, dx, dy, anchor)."""
    g = Graph(xr[0], xr[1], yr[0], yr[1], w=w, h=h, pad=pad).axes(xlabel, ylabel)
    for y in hl:
        g.hline(y)
    for x in vl:
        g.vline(x)
    for item in fns:
        f, col = item[0], item[1]
        dash = item[2] if len(item) > 2 else None
        x0 = item[3] if len(item) > 3 else None
        x1 = item[4] if len(item) > 4 else None
        g.curve(f, color=col, dash=dash, x0=x0, x1=x1, n=600)
    ticks(g, xt, yt)
    for (x, y) in dots:
        g.dot(x, y)
    for (x, y) in hollow:
        g.dot(x, y, hollow=True)
    for L in labels:
        x, y, s = L[0], L[1], L[2]
        dx = L[3] if len(L) > 3 else 0
        dy = L[4] if len(L) > 4 else 0
        an = L[5] if len(L) > 5 else "start"
        g.items.append(lab(g.X(x) + dx, g.Y(y) + dy, s, an))
    save(name, g)
    return g


# ---------------- revision ----------------
def fig_rev():
    from math import isfinite
    T = pi_ticks(-2, 2, 0.5)
    graph("rev_sin", [(sin, "blue")], (-2 * PI, 2 * PI), (-1.4, 1.4), xt=T, yt=[(1, "1"), (-1, "-1")], w=540, h=100)
    graph("rev_cos", [(cos, "blue")], (-2 * PI, 2 * PI), (-1.4, 1.4), xt=T, yt=[(1, "1"), (-1, "-1")], w=540, h=100)

    def tn(x):
        if abs(cos(x)) < 1e-3:
            return None
        return tan(x)
    graph("rev_tan", [(tn, "blue")], (-2 * PI, 2 * PI), (-3.2, 3.2), xt=T, yt=[(1, "1"), (-1, "-1")], w=540, h=128,
          vl=[k * PI / 2 for k in (-3, -1, 1, 3)])


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("fig_") and callable(fn):
            fn()
