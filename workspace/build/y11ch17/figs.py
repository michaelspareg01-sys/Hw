import os, sys
from math import sin, cos, tan, atan, atan2, pi, sqrt, radians, degrees, e
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
        fs = size * 1.0
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


def _box(x, y, s, anchor, size):
    if "/" in s:
        num, den = s.split("/", 1)
        w = max(len(num), len(den)) * size * 0.6 + 4
        h = 2.2 * size
    else:
        w = len(s) * size * 0.6 + 4
        h = 1.2 * size
    x0 = {"middle": x - w / 2, "start": x, "end": x - w}[anchor]
    return (x0, y - h / 2, x0 + w, y + h / 2)


def _hit(b1, b2, pad=2):
    return not (b1[2] + pad < b2[0] or b2[2] + pad < b1[0] or b1[3] + pad < b2[1] or b2[3] + pad < b1[1])


def ticks(g, xt=(), yt=(), size=12, dots=()):
    """Tick marks and labels with white backgrounds. A y label that would collide with an x label or a dot
    moves to the right of the axis; an x label that collides with a dot moves above the axis; a label that
    still collides is left out (the tick mark stays)."""
    for v, s in xt:
        x = g.X(v)
        g.items.append(f'<line x1="{x:.1f}" y1="{g._y0 - 3:.1f}" x2="{x:.1f}" y2="{g._y0 + 3:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    for v, s in yt:
        y = g.Y(v)
        g.items.append(f'<line x1="{g._x0 - 3:.1f}" y1="{y:.1f}" x2="{g._x0 + 3:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    dboxes = [(g.X(dx) - 5, g.Y(dy) - 5, g.X(dx) + 5, g.Y(dy) + 5) for dx, dy in dots]
    placed = []
    for v, s in xt:
        if not s:
            continue
        dy = 22 if "/" in s else 16
        for yy in (g._y0 + dy, g._y0 - dy):
            bx = _box(g.X(v), yy, s, "middle", size)
            if not any(_hit(bx, d) for d in dboxes):
                g.items.append(lab(g.X(v), yy, s, size=size))
                placed.append(bx)
                break
    for v, s in yt:
        if not s:
            continue
        for xx, an in ((g._x0 - 8, "end"), (g._x0 + 8, "start")):
            bx = _box(xx, g.Y(v), s, an, size)
            if not any(_hit(bx, d) for d in dboxes + placed):
                g.items.append(lab(xx, g.Y(v), s, an, size=size))
                placed.append(bx)
                break


def graph(name, fns, xr, yr, xt=(), yt=(), w=300, h=170, pad=(30, 34, 22, 28), dots=(), hollow=(),
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
    ticks(g, xt, yt, dots=list(dots) + list(hollow))
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



# ---------------- 17A ----------------
from math import exp, log


def sq(v):
    return sqrt(v) if v >= 0 else None


def fig_17a():
    yx = (lambda x: x, "faint", "5 4")
    # e^x and log x
    graph("a_explog", [yx, (exp, "blue"), (lambda x: log(x) if x > 0 else None, "teal", None, 0.02, 3.6)],
          (-2.2, 3.6), (-2.2, 3.6), xt=[(1, "1"), (2, "2"), (e, "e")], yt=[(1, "1"), (2, "2"), (e, "e")], w=190, h=190, labels=[(1.25, 3.4, "y = eˣ", -6, 0, "end"), (3.4, 1.22, "y = logₑ x", 0, -14, "end"),
                                         (3.1, 3.3, "y = x", -4, 0, "end")])
    par = lambda x: (x - 2) ** 2
    graph("a_par1", [(par, "blue", None, -0.1, 4.1)], (-0.4, 4.4), (-0.6, 5), xt=[(2, "2")], yt=[(4, "4")], w=150, h=118, hl=[3])
    graph("a_par2", [yx, (par, "blue", None, 2, 4.4), (lambda x: 2 + sq(x) if x >= 0 else None, "teal", None, 0, 5)],
          (-0.4, 5), (-0.4, 5), xt=[(2, "2"), (4, "4")], yt=[(2, "2"), (4, "4")], w=150, h=140,
          dots=[(2, 0), (0, 2)])
    graph("a_par3", [yx, (par, "blue", None, -0.1, 2), (lambda x: 2 - sq(x) if x >= 0 else None, "teal", None, 0, 5)],
          (-0.4, 5), (-0.6, 5), xt=[(2, "2"), (4, "4")], yt=[(2, "2"), (4, "4")], w=150, h=140,
          dots=[(2, 0), (0, 2), (1, 1)], labels=[(1, 1, "(1, 1)", 6, -9, "start")])
    # Example 2
    graph("a_ex2", [yx, (lambda x: (x - 1) ** 2 + 2, "blue", None, -0.6, 1), (lambda x: 1 - sq(x - 2) if x >= 2 else None, "teal", None, 2, 5.2)],
          (-1.5, 5.2), (-2.4, 5.2), xt=[(1, "1"), (2, "2"), (3, "3")], yt=[(1, "1"), (2, "2"), (3, "3")], w=190, h=205, dots=[(1, 2), (2, 1)],
          labels=[(-0.5, 4.75, "y = g(x)", 6, 0, "start"), (4.0, -1.95, "y = g⁻¹(x)", 0, 0, "middle"), (4.6, 4.6, "y = x", -4, 13, "end")])
    cub = lambda x: (x - 2) ** 2 * (x + 1)
    graph("a_ex3a", [(cub, "blue", None, -1.3, 3.1)], (-1.6, 3.4), (-1.5, 5.4), xt=[(-1, "-1"), (2, "2")], yt=[(4, "4")],
          w=170, h=130, dots=[(0, 4), (2, 0)])
    # inverse of f on [0, 2]: solve numerically by bisection (f decreasing there)
    def finv(yv, f=cub, lo=0.0, hi=2.0):
        if yv < -1e-9 or yv > 4 + 1e-9:
            return None
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid) > yv:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    m = finv(0)  # placeholder
    # M: root of x^3 - 3x^2 - x + 4 = 0 in [0, 2]
    lo, hi = 0.0, 2.0
    g = lambda x: x ** 3 - 3 * x ** 2 - x + 4
    for _ in range(60):
        mid = (lo + hi) / 2
        if g(lo) * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
    M = (lo + hi) / 2
    graph("a_ex3c", [yx, (cub, "blue", None, 0, 2), (finv, "teal", None, 0, 4)], (-0.5, 4.7), (-0.5, 4.7),
          xt=[(2, "2"), (4, "4")], yt=[(2, "2"), (4, "4")], w=170, h=170, dots=[(M, M)],
          labels=[(M, M, "M", 7, -8, "start"), (0.15, 4.1, "y = f(x)", 4, 0, "start"), (3.9, 0.35, "y = f⁻¹(x)", 0, -12, "middle"),
                  (4.4, 4.4, "y = x", -4, 13, "end")])
    graph("a_q18", [(lambda x: 2 * x / (1 + x * x), "blue")], (-4.5, 4.5), (-1.6, 1.6), xt=[(1, "1"), (-1, "-1")],
          yt=[(1, "1"), (-1, "-1")], w=240, h=175, hl=[1, -1], labels=[(2.8, 0.62, "g(x)", 0, -10, "middle")])
    graph("a_pp5", [(lambda x: 1 / (x * x + 1), "rose", None, 0, 3.2)], (-0.4, 3.3), (-0.2, 1.2),
          xt=[(0.5, "0.5"), (1, "1"), (1.5, "1.5"), (2, "2"), (2.5, "2.5"), (3, "3")], yt=[(0.5, "0.5"), (1, "1")],
          w=320, h=130, dots=[(0, 1)])



def cbrt(v):
    return v ** (1 / 3) if v >= 0 else -((-v) ** (1 / 3))


def bisect_inv(f, yv, lo, hi, n=60):
    """Inverse of a monotonic f on [lo, hi] at yv (None outside the range)."""
    a, b = f(lo), f(hi)
    if not (min(a, b) - 1e-12 <= yv <= max(a, b) + 1e-12):
        return None
    inc = b > a
    for _ in range(n):
        mid = (lo + hi) / 2
        if (f(mid) < yv) == inc:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pair(name, f, finv, xr, yr, xt, yt, fdom=(None, None), idom=(None, None), w=170, h=170, dots=(), hollow=(),
         labels=(), hl=(), vl=()):
    """f (blue), its inverse (teal) and the mirror y = x (faint dashed)."""
    fns = [(lambda x: x, "faint", "5 4"), (f, "blue", None, fdom[0], fdom[1])]
    if finv is not None:
        fns.append((finv, "teal", None, idom[0], idom[1]))
    return graph(name, fns, xr, yr, xt=xt, yt=yt, w=w, h=h, dots=dots, hollow=hollow, labels=labels, hl=hl, vl=vl)


def fig_17a_ans():
    # C2 tutor demo and your turn
    pair("aa_c2d", lambda x: (x - 3) ** 2 + 1, lambda x: 3 - sq(x - 1) if x >= 1 else None, (-1, 10.5), (-1, 10.5),
         [(1, "1"), (3, "3"), (10, "10")], [(1, "1"), (3, "3"), (10, "10")], fdom=(-0.15, 3), idom=(1, 10.5),
         dots=[(3, 1), (1, 3)], labels=[(0.6, 9.2, "g", 6, 0, "start"), (9.2, 0.8, "g⁻¹", 0, -10, "middle")])
    pair("aa_c2y", lambda x: (x - 2) ** 2 - 1, lambda x: 2 - sq(x + 1) if x >= -1 else None, (-2, 5.5), (-2, 5.5),
         [(-1, "-1"), (1, "1"), (2, "2"), (3, "3")], [(-1, "-1"), (1, "1"), (2, "2"), (3, "3")], fdom=(-0.45, 2), idom=(-1, 5.5),
         dots=[(2, -1), (-1, 2)], labels=[(-0.4, 5.0, "g", 6, 0, "start"), (5.0, -0.2, "g⁻¹", 0, -11, "middle")])
    # C3 tutor demo: y = (x - 1)^2 (x + 2)
    c3 = lambda x: (x - 1) ** 2 * (x + 2)
    graph("aa_c3da", [(c3, "blue", None, -2.3, 2.0)], (-2.6, 2.4), (-1.6, 5.6), xt=[(-2, "-2"), (-1, "-1"), (1, "1")],
          yt=[(2, "2"), (4, "4")], w=170, h=150, dots=[(-1, 4), (1, 0)])
    pair("aa_c3dc", c3, lambda y: bisect_inv(c3, y, -1, 1), (-1.6, 4.6), (-1.6, 4.6), [(-1, "-1"), (1, "1"), (4, "4")],
         [(-1, "-1"), (1, "1"), (4, "4")], fdom=(-1, 1), idom=(0, 4), dots=[(-1, 4), (1, 0), (4, -1), (0, 1)])
    c3y = lambda x: (x + 1) ** 2 * (x - 1)
    graph("aa_c3ya", [(c3y, "blue", None, -2.0, 1.45)], (-2.3, 1.8), (-2.2, 2.2), xt=[(-1, "-1"), (1, "1")],
          yt=[(-1, "-1"), (1, "1")], w=170, h=150, dots=[(-1, 0), (1 / 3, -32 / 27)])
    pair("aa_c3yc", c3y, lambda y: bisect_inv(c3y, y, -1, 1 / 3), (-1.6, 0.9), (-1.6, 0.9), [(-1, "-1")], [(-1, "-1")],
         fdom=(-1, 1 / 3), idom=(-32 / 27, 0), w=170, h=170, dots=[(-1, 0), (1 / 3, -32 / 27), (0, -1), (-32 / 27, 1 / 3)])
    # 2d
    pair("aa_2d", sqrt, lambda x: x * x, (-0.5, 4.6), (-0.5, 4.6), [(1, "1"), (2, "2"), (4, "4")], [(1, "1"), (2, "2"), (4, "4")],
         fdom=(0, 4), idom=(0, 2), dots=[(4, 2), (2, 4), (0, 0)], labels=[(3.4, 1.84, "F", 0, 12, "middle"), (1.85, 3.4, "F⁻¹", -10, 0, "end")])
    T = [(1, "1"), (-1, "-1")]
    pair("aa_3a", lambda x: 2 * x, lambda x: x / 2, (-2.5, 2.5), (-2.5, 2.5), T, T,
         labels=[(1.1, 2.2, "f", -8, 0, "end"), (2.2, 1.1, "f⁻¹", 0, 12, "middle")], w=150, h=150)
    pair("aa_3b", lambda x: x ** 3 + 1, lambda x: cbrt(x - 1), (-2.5, 2.5), (-2.5, 2.5), T, T,
         labels=[(0.9, 2.2, "f", -8, 0, "end"), (2.2, 1.1, "f⁻¹", 0, 12, "middle")], w=150, h=150)
    g = Graph(-1.7, 1.7, -1.7, 1.7, w=150, h=150, pad=(30, 34, 22, 28)).axes()
    g.curve(lambda x: x, color="faint", dash="5 4")
    g.curve(lambda x: sq(1 - x * x), color="blue", x0=-1, x1=1)
    g.curve(lambda y: sq(1 - y * y), color="teal", x0=-1, x1=1)  # placeholder, replaced below
    g.items.pop()
    import math as _m
    pts = " ".join(f"{g.X(_m.sqrt(max(0, 1 - y * y))):.1f},{g.Y(y):.1f}" for y in [(-1 + 2 * i / 200) for i in range(201)])
    g.items.append(f'<polyline points="{pts}" fill="none" stroke="{ACC["teal"]}" stroke-width="2.2"/>')
    ticks(g, T, T)
    save("aa_3c", g)
    g = Graph(-5, 5, -5, 5, w=150, h=150, pad=(30, 34, 22, 28)).axes()
    g.curve(lambda x: x, color="faint", dash="5 4")
    g.curve(lambda x: x * x - 4, color="blue", x0=-3, x1=3)
    pts = " ".join(f"{g.X(y * y - 4):.1f},{g.Y(y):.1f}" for y in [(-3 + 6 * i / 200) for i in range(201)])
    g.items.append(f'<polyline points="{pts}" fill="none" stroke="{ACC["teal"]}" stroke-width="2.2"/>')
    ticks(g, [(-4, "-4"), (2, "2")], [(-4, "-4"), (2, "2")])
    save("aa_3d", g)
    pair("aa_3e", lambda x: 2 ** x, lambda x: log(x, 2) if x > 0 else None, (-3, 3.5), (-3, 3.5), T, T, fdom=(-3, 1.8),
         idom=(0.13, 3.5), labels=[(-1.6, 0.55, "f", 0, -12, "middle"), (2.6, 1.38, "f⁻¹", 0, 12, "middle")], w=150, h=150)
    pair("aa_3f", lambda x: sq(x - 3), lambda x: x * x + 3, (-0.6, 6.5), (-0.6, 6.5), [(3, "3")], [(3, "3")],
         fdom=(3, 6.5), idom=(0, 1.9), dots=[(3, 0), (0, 3)], labels=[(5.6, 1.6, "f", 0, 12, "middle"), (1.6, 5.6, "f⁻¹", -8, 0, "end")], w=150, h=150)
    # 8
    F8 = lambda x: x * x + 2 * x + 4
    pair("aa_8", F8, lambda x: -1 + sq(x - 3) if x >= 3 else None, (-1.8, 6), (-1.8, 6), [(-1, "-1"), (3, "3"), (4, "4")],
         [(-1, "-1"), (3, "3"), (4, "4")], fdom=(-1, 0.6), idom=(3, 6), dots=[(-1, 3), (3, -1)],
         labels=[(0.6, 5.36, "F", 7, 0, "start"), (5.3, 0.6, "F⁻¹", 0, -11, "middle")])
    # 9
    pair("aa_9", lambda x: 1 - log(x) if x > 0 else None, lambda x: exp(1 - x), (-1.2, 4.2), (-1.2, 4.2), [(1, "1"), (e, "e")],
         [(1, "1"), (e, "e")], fdom=(0.05, 4.2), idom=(-0.4, 4.2), labels=[(0.25, 3.2, "f", 7, 0, "start"), (3.6, 0.3, "f⁻¹", 0, -12, "middle")])
    # 10
    g10 = lambda x: (x + 2) / (x + 1) if x > -1 else None
    pair("aa_10", g10, lambda x: (2 - x) / (x - 1) if x > 1 else None, (-1.6, 5), (-1.6, 5), [(-1, "-1"), (1, "1"), (2, "2")],
         [(-1, "-1"), (1, "1"), (2, "2")], fdom=(-0.75, 5), idom=(1.2, 5), vl=[-1, 1], hl=[1, -1],
         dots=[(sqrt(2), sqrt(2))], labels=[(sqrt(2), sqrt(2), "(√2, √2)", 8, 2, "start"), (4.7, 1.17, "g", 0, -12, "middle"), (4.3, -0.33, "g⁻¹", 0, 11, "middle")], w=190, h=190)
    # 11
    pair("aa_11", lambda x: -x ** 3, lambda x: cbrt(-x), (-2, 2), (-2, 2), T, T, dots=[(-1, 1), (0, 0), (1, -1)],
         labels=[(-1.2, 1.73, "y = −x³", 6, 0, "start")], w=160, h=160)
    # 13
    g13 = lambda x: (x + 2) ** 2 - 4
    pair("aa_13", g13, lambda x: -2 + sq(x + 4) if x >= -4 else None, (-5, 3.2), (-5, 3.2), [(-4, "-4"), (-2, "-2")],
         [(-4, "-4"), (-2, "-2")], fdom=(-4.6, 0.75), idom=(-4, 3.2), dots=[(-2, -4), (-4, -2)],
         labels=[(-4.4, 1.8, "g", -6, 0, "end"), (2.6, 0.6, "g⁻¹", 0, -12, "middle")], w=180, h=180)
    # 14
    F14 = lambda x: x ** 3 - 3 * x
    pair("aa_14", F14, lambda y: bisect_inv(F14, y, -1, 1), (-2.4, 2.4), (-2.4, 2.4), [(-2, "-2"), (-1, "-1"), (1, "1"), (2, "2")],
         [(-2, "-2"), (2, "2")], fdom=(-2.05, 2.05), idom=(-2, 2), dots=[(-1, 2), (1, -2), (sqrt(3), 0), (-sqrt(3), 0)],
         labels=[(1.75, 1.0, "F", 6, 0, "start"), (2.0, -0.85, "F⁻¹", 0, 11, "middle")], w=190, h=190)
    # 16
    f16 = lambda x: x - 1 / x if x > 0 else None
    pair("aa_16", f16, lambda x: 0.5 * (x + sqrt(4 + x * x)), (-3.4, 3.4), (-3.4, 3.4), [(1, "1")], [(1, "1")],
         fdom=(0.25, 3.4), labels=[(2.4, 1.98, "f", 0, 12, "middle"), (-2.6, 0.38, "f⁻¹", 0, -12, "middle")], w=170, h=170)
    # 18 c and d
    g18 = lambda x: 2 * x / (1 + x * x)
    graph("aa_18c", [(lambda x: x, "faint", "5 4"), (lambda x: bisect_inv(g18, x, -1, 1) if abs(x) <= 1 else None, "teal", None, -1, 1)],
          (-1.6, 1.6), (-1.6, 1.6), xt=T, yt=T, w=150, h=150, dots=[(1, 1), (-1, -1)])
    gi = lambda x: (1 + sqrt(1 - x * x)) / x if 0 < abs(x) <= 1 else None
    graph("aa_18d", [(gi, "teal", None, -1, -0.32), (gi, "teal", None, 0.32, 1)], (-1.6, 1.6), (-3.4, 3.4), xt=T, yt=T,
          w=150, h=170, dots=[(1, 1), (-1, -1)])
    # 19
    f19 = lambda x: (x * x - 4 * x + 24) / 6
    pair("aa_19", f19, lambda x: 2 + sq(6 * x - 20) if x >= 10 / 3 else None, (-0.6, 7.2), (-0.6, 7.2), [(2, "2"), (4, "4"), (6, "6")],
         [(2, "2"), (4, "4"), (6, "6")], fdom=(-0.2, 7.2), idom=(10 / 3, 7.2), dots=[(2, 10 / 3), (0, 4), (10 / 3, 2), (4, 4), (6, 6)],
         labels=[(0.4, 3.4, "f", 0, 13, "middle"), (6.6, 4.5, "f⁻¹", 0, 12, "middle")], w=190, h=190)
    # 20
    sh = lambda x: 0.5 * (exp(x) - exp(-x))
    graph("aa_20", [(lambda x: x, "faint", "5 4"), (sh, "blue", None, -2.2, 2.2), (lambda x: log(x + sqrt(x * x + 1)), "teal")],
          (-3, 3), (-3, 3), xt=T, yt=T, w=180, h=180, labels=[(1.55, 2.3, "sinh x", -7, 0, "end"), (2.6, 1.7, "sinh⁻¹x", 0, 12, "middle")])
    # PP 6: inverse of 2x^3 + 1
    f6 = lambda x: 2 * x ** 3 + 1
    c = cbrt(-0.5)
    pair("aa_pp6", f6, lambda x: cbrt((x - 1) / 2), (-2.3, 2.3), (-2.3, 2.3), T, T, fdom=(-1.3, 0.95),
         dots=[(-1, -1), (1, 0), (0, c), (0, 1), (c, 0)],
         labels=[(1, 0, "(1, 0)", 6, -11, "start"), (-1, -1, "(−1, −1)", 6, 9, "start"), (0.75, 1.9, "f", -8, 0, "end"), (2.0, 0.8, "f⁻¹", 0, -12, "middle")], w=190, h=190)



# ---------------- 17B ----------------
from math import asin, acos


def unit_triangle(name, ang_deg, legs, w=180, h=170, r=60):
    """Quadrant diagram for Example 5: circle, ray at ang_deg, perpendicular to the x-axis, side labels.
    legs = (hyp_label, opp_label, adj_label)."""
    f = Fig(w, h)
    cx, cy = w / 2 - 10, h / 2
    f.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    f.line(cx - r - 10, cy, cx + r + 10, cy, width=1.1)
    f.line(cx, cy + r + 10, cx, cy - r - 10, width=1.1)
    a = radians(ang_deg)
    ux, uy = cos(a), -sin(a)                 # unit vector along the ray (screen coordinates)
    px, py = cx + r * ux, cy + r * uy
    f.arrow(cx, cy, cx + (r + 14) * ux, cy + (r + 14) * uy, color="blue", width=1.8)
    f.line(px, py, px, cy, color="ink", width=1.3)
    sy = 1 if py > cy else -1                # opposite side goes down (1) or up (-1) from the axis
    f.right(px, cy, -1 if ux > 0 else 1, sy, s=6)
    hyp, opp, adj = legs
    nx, ny = -uy, ux                         # normal to the ray
    if ny * sy < 0:                          # point the normal away from the triangle
        nx, ny = -nx, -ny
    f.raw(lab(cx + 0.5 * r * ux + 13 * nx, cy + 0.5 * r * uy + 13 * ny, hyp, size=12))
    f.raw(lab(px + (9 if ux > 0 else -9), (py + cy) / 2, opp, "start" if ux > 0 else "end", size=12))
    f.raw(lab((cx + px) / 2, cy - sy * 11, adj, size=12))
    f.raw(lab(cx + (r + 14) * ux + 12 * nx, cy + (r + 14) * uy + 12 * ny, "α", size=13))
    save(name, f)


def fig_17b():
    T2 = pi_ticks(-2, 2, 0.5)
    # sine with A, B, C, D at the stationary points
    graph("b_sin", [(sin, "blue")], (-2 * PI, 2 * PI), (-1.5, 1.5), xt=T2, yt=[(1, "1"), (-1, "-1")], w=540, h=118,
          labels=[(-1.5 * PI, 1, "A", 0, -11, "middle"), (-PI / 2, -1, "B", 0, 12, "middle"), (PI / 2, 1, "C", 0, -11, "middle"),
                  (1.5 * PI, -1, "D", 0, 12, "middle")], dots=[(-1.5 * PI, 1), (-PI / 2, -1), (PI / 2, 1), (1.5 * PI, -1)])
    yx = (lambda x: x, "faint", "5 4")
    graph("b_sinr", [yx, (sin, "blue", None, -PI / 2, PI / 2)], (-2.0, 2.0), (-2.0, 2.0),
          xt=[(-PI / 2, "-π/2"), (PI / 2, "π/2")], yt=[(1, "1"), (-1, "-1")], w=180, h=180, dots=[(-PI / 2, -1), (PI / 2, 1)])
    graph("b_asin", [yx, (lambda x: asin(x) if abs(x) <= 1 else None, "teal", None, -1, 1)], (-2.0, 2.0), (-2.0, 2.0),
          xt=[(-1, "-1"), (1, "1")], yt=[(-PI / 2, "-π/2"), (PI / 2, "π/2")], w=180, h=180, dots=[(-1, -PI / 2), (1, PI / 2)])
    graph("b_cos", [(cos, "blue")], (-2 * PI, 2 * PI), (-1.5, 1.5), xt=T2, yt=[(1, "1"), (-1, "-1")], w=540, h=118,
          labels=[(-PI, -1, "A", 0, 12, "middle"), (0, 1, "B", 9, -11, "middle"), (PI, -1, "C", 0, 12, "middle"), (2 * PI, 1, "D", -2, -11, "middle")],
          dots=[(-PI, -1), (0, 1), (PI, -1), (2 * PI, 1)])
    t = (lambda x: PI / 2 - x, "rose", "3 3")
    graph("b_cosr", [yx, t, (cos, "blue", None, 0, PI)], (-1.6, 3.6), (-1.6, 3.6), xt=[(PI / 2, "π/2"), (PI, "π")],
          yt=[(1, "1"), (-1, "-1"), (PI / 2, "π/2")], w=190, h=190, dots=[(0, 1), (PI, -1)])
    graph("b_acos", [yx, t, (lambda x: acos(x) if abs(x) <= 1 else None, "teal", None, -1, 1)], (-1.6, 3.6), (-1.6, 3.6),
          xt=[(-1, "-1"), (1, "1"), (PI / 2, "π/2")], yt=[(PI / 2, "π/2"), (PI, "π")], w=190, h=190, dots=[(-1, PI), (1, 0)])

    def tn(x):
        return None if abs(cos(x)) < 1e-3 else tan(x)
    graph("b_tan", [(tn, "blue")], (-2 * PI, 2 * PI), (-3.2, 3.2), xt=T2, yt=[], w=540, h=128,
          vl=[k * PI / 2 for k in (-3, -1, 1, 3)])
    graph("b_tanr", [yx, (tn, "blue", None, -PI / 2 + 0.02, PI / 2 - 0.02)], (-2.2, 2.2), (-2.2, 2.2),
          xt=[(-PI / 2, "-π/2"), (-PI / 4, ""), (PI / 4, ""), (PI / 2, "π/2")], yt=[(1, "1"), (-1, "-1")], w=180, h=180,
          vl=[-PI / 2, PI / 2])
    graph("b_atan", [yx, (atan, "teal")], (-2.6, 2.6), (-2.2, 2.2), xt=[(-1, "-1"), (1, "1")],
          yt=[(-PI / 2, "-π/2"), (PI / 2, "π/2")], w=190, h=170, hl=[-PI / 2, PI / 2])
    unit_triangle("b_ex5a", -24, ("5", "1", "√24"))
    unit_triangle("b_ex5b", 36.87, ("5", "3", "4"))
    # Exercise 17B Q1: y = cos^-1 x on a fine grid (0.1 units)
    xs0, xs1, ys0, ys1 = -1, 1, 0, 3.3
    W, H, pl, pr, pt, pb = 330, 470, 34, 30, 20, 26
    g = Graph(xs0, xs1, ys0, ys1, w=W, h=H, pad=(pl, pr, pt, pb))
    for i in range(0, 21):
        xv = -1 + i * 0.1
        heavy = i % 5 == 0
        g.items.append(f'<line x1="{g.X(xv):.1f}" y1="{g.Y(0):.1f}" x2="{g.X(xv):.1f}" y2="{g.Y(3.3):.1f}" stroke="{FAINT}" stroke-width="{0.9 if heavy else 0.4}"/>')
    for j in range(0, 34):
        yv = j * 0.1
        heavy = j % 5 == 0
        g.items.append(f'<line x1="{g.X(-1):.1f}" y1="{g.Y(yv):.1f}" x2="{g.X(1):.1f}" y2="{g.Y(yv):.1f}" stroke="{FAINT}" stroke-width="{0.9 if heavy else 0.4}"/>')
    g.axes()
    g.curve(lambda x: acos(x) if abs(x) <= 1 else None, color="blue", x0=-1, x1=1, n=800)
    g.dot(-1, PI)
    g.dot(1, 0)
    ticks(g, [(-1, "-1"), (1, "1")], [(1, "1"), (2, "2"), (3, "3")])
    g.items.append(lab(g.X(0) + 9, g.Y(PI / 2), "π/2", "start", size=12))
    g.items.append(lab(g.X(0) + 9, g.Y(PI), "π", "start", size=12))
    save("b_q1", g)



# ---------------- 17C ----------------
def fn(f, lo=None, hi=None):
    def g(x):
        if lo is not None and x < lo - 1e-12:
            return None
        if hi is not None and x > hi + 1e-12:
            return None
        try:
            return f(x)
        except ValueError:
            return None
    return g


SIN = fn(lambda x: asin(x), -1, 1)
COS = fn(lambda x: acos(x), -1, 1)
P2, P4 = PI / 2, PI / 4


def fig_17c():
    pt = lambda k, d: (k * PI / d, None)
    # Example 6
    graph("c_ex6a", [(lambda x: P2 + atan(x + 1), "blue")], (-4.5, 2.6), (-0.5, 3.6), xt=[(-2, "-2"), (-1, "-1")],
          yt=[(P4, "π/4"), (P2, "π/2"), (3 * P4, "3π/4"), (PI, "π")], w=210, h=170, hl=[PI], dots=[(-2, P4), (-1, P2), (0, 3 * P4)])
    graph("c_ex6b", [(fn(lambda x: asin(-x) - P2, -1, 1), "blue", None, -1, 1)], (-1.6, 1.6), (-3.6, 0.6), xt=[(-1, "-1"), (1, "1")],
          yt=[(-P2, "-π/2"), (-PI, "-π")], w=170, h=170, dots=[(-1, 0), (1, -PI)])
    graph("c_comp", [(SIN, "blue", None, -1, 1), (COS, "teal", None, -1, 1)], (-1.6, 1.6), (-1.9, 3.6), xt=[(-1, "-1"), (1, "1")],
          yt=[(P4, "π/4"), (P2, "π/2"), (PI, "π"), (-P2, "-π/2")], w=200, h=200, hl=[P4], dots=[(-1, -P2), (1, P2), (-1, PI), (1, 0)],
          labels=[(0.55, asin(0.55), "sin⁻¹x", 6, 6, "start"), (-0.62, acos(-0.62), "cos⁻¹x", -6, 0, "end")])
    T1 = [(1, "1"), (-1, "-1")]
    graph("c_ss", [(lambda x: x, "blue", None, -1, 1)], (-1.6, 1.6), (-1.6, 1.6), xt=T1, yt=T1, w=150, h=150, dots=[(-1, -1), (1, 1)])
    graph("c_cc", [(lambda x: x, "blue", None, -1, 1)], (-1.6, 1.6), (-1.6, 1.6), xt=T1, yt=T1, w=150, h=150, dots=[(-1, -1), (1, 1)])
    graph("c_tt", [(lambda x: x, "blue")], (-1.6, 1.6), (-1.6, 1.6), xt=[], yt=[], w=150, h=150)
    graph("c_cic", [(lambda x: acos(cos(x)), "blue")], (-3.3 * PI, 3.3 * PI), (-0.6, 3.8), xt=[(k * PI, l) for k, l in
          ((-3, "-3π"), (-2, "-2π"), (-1, "-π"), (1, "π"), (2, "2π"), (3, "3π"))], yt=[(PI, "π")], w=520, h=120)
    # PP figures
    graph("c_pp1", [(lambda x: 3 * atan(x), "ink")], (-6, 6), (-5.5, 5.5), xt=[], yt=[], w=300, h=130, hl=[1.5 * PI, -1.5 * PI],
          labels=[(0, 0, "O", -9, 9, "middle")])
    T3 = [(-3, "-3"), (3, "3")]
    graph("c_pp3a", [(fn(lambda x: 2 * asin(x / 3), -3, 3), "ink", None, -3, 3)], (-4, 4), (-3.9, 3.9), xt=T3,
          yt=[(PI, "π"), (P2, "π/2"), (-P2, "-π/2"), (-PI, "-π")], w=170, h=150, dots=[(-3, -PI), (3, PI)])
    graph("c_pp3b", [(fn(lambda x: 1.5 * PI * sin(x / 2 * P2 * 2 / PI) if False else 2 * asin(x / 2) * 1.5, -2, 2), "ink", None, -2, 2)],
          (-3, 3), (-5.3, 6.1), xt=[(-2, "-2"), (2, "2")], yt=[(1.5 * PI, "3π/2"), (PI, "π"), (P2, "π/2"), (-P2, "-π/2"), (-PI, "-π"), (-1.5 * PI, "-3π/2")],
          w=170, h=150, dots=[(-2, -1.5 * PI), (2, 1.5 * PI)])
    graph("c_pp3c", [(fn(lambda x: 2 * acos(x / 3), -3, 3), "ink", None, -3, 3)], (-4, 4), (-0.8, 7.0), xt=T3,
          yt=[(2 * PI, "2π"), (1.5 * PI, "3π/2"), (PI, "π"), (P2, "π/2")], w=170, h=150, dots=[(-3, 2 * PI), (3, 0)])
    graph("c_pp3d", [(fn(lambda x: -2 * asin(x / 3), -3, 3), "ink", None, -3, 3)], (-4, 4), (-3.9, 3.9), xt=T3,
          yt=[(PI, "π"), (P2, "π/2"), (-P2, "-π/2"), (-PI, "-π")], w=170, h=150, dots=[(-3, PI), (3, -PI)])
    graph("c_pp5", [(lambda x: acos(sin(x)), "ink")], (-2.2 * PI, 2.2 * PI), (-2.0, 3.8),
          xt=[(-2 * PI, "-2π"), (-1.5 * PI, "-3π/2"), (-PI, "-π"), (-P2, "-π/2"), (P2, "π/2"), (PI, "π"), (1.5 * PI, "3π/2"), (2 * PI, "2π")],
          yt=[(PI, "π"), (P2, "π/2"), (-P2, "-π/2")], w=480, h=140)
    graph("c_pp6", [(fn(lambda x: 2 * acos(2 * x - 3), 1, 2), "rose", None, 1, 2)], (-0.4, 2.6), (-0.5, 7), xt=[], yt=[],
          w=300, h=130, labels=[(1, 2 * PI, "A", 0, -12, "middle")])
    # NSG 2023 grid graph: y = (2/pi) acos(x/3) on a 0.5-unit grid, -4..4 by -2..6
    g = Graph(-4, 4, -2, 6.6, w=250, h=265, pad=(30, 30, 20, 26))
    for i in range(17):
        xv = -4 + i * 0.5
        g.items.append(f'<line x1="{g.X(xv):.1f}" y1="{g.Y(-2):.1f}" x2="{g.X(xv):.1f}" y2="{g.Y(6):.1f}" stroke="{FAINT}" stroke-width="{0.9 if i % 4 == 0 else 0.45}"/>')
    for j in range(17):
        yv = -2 + j * 0.5
        g.items.append(f'<line x1="{g.X(-4):.1f}" y1="{g.Y(yv):.1f}" x2="{g.X(4):.1f}" y2="{g.Y(yv):.1f}" stroke="{FAINT}" stroke-width="{0.9 if j % 4 == 0 else 0.45}"/>')
    g.axes()
    g.curve(fn(lambda x: 2 / PI * acos(x / 3), -3, 3), color="ink", width=2.6, x0=-3, x1=3, n=800)
    ticks(g, [(-4, "-4"), (-2, "-2"), (2, "2"), (4, "4")], [(-2, "-2"), (2, "2"), (4, "4"), (6, "6")])
    save("c_pp8", g)



def fig_17c_ans():
    T1 = [(1, "1"), (-1, "-1")]
    yp = [(P2, "π/2"), (-P2, "-π/2")]
    W = dict(w=170, h=160)
    # lesson examples
    graph("ca_d1a", [(lambda x: atan(x - 1) - P2, "blue")], (-3.5, 4.5), (-3.6, 0.7), xt=[(1, "1"), (2, "2")],
          yt=[(-P4, "-π/4"), (-P2, "-π/2"), (-3 * P4, "-3π/4"), (-PI, "-π")], hl=[-PI], dots=[(0, -3 * P4), (1, -P2), (2, -P4)], w=200, h=160)
    graph("ca_d1b", [(fn(lambda x: acos(-x) + P2, -1, 1), "blue", None, -1, 1)], (-1.6, 1.6), (-0.5, 5.7), xt=T1,
          yt=[(P2, "π/2"), (PI, "π"), (1.5 * PI, "3π/2")], dots=[(-1, P2), (0, PI), (1, 1.5 * PI)], **W)
    graph("ca_y1a", [(lambda x: atan(x + 2) + P4, "blue")], (-5.5, 2.5), (-1.2, 2.9), xt=[(-3, "-3"), (-2, "-2"), (-1, "-1")],
          yt=[(-P4, "-π/4"), (P4, "π/4"), (P2, "π/2"), (3 * P4, "3π/4")], hl=[-P4, 3 * P4], dots=[(-3, 0), (-2, P4), (-1, P2)], w=270, h=160)
    graph("ca_y1b", [(fn(lambda x: asin(-x) + P2, -1, 1), "blue", None, -1, 1)], (-1.6, 1.6), (-0.5, 3.7), xt=T1,
          yt=[(P2, "π/2"), (PI, "π")], dots=[(-1, PI), (0, P2), (1, 0)], **W)
    T13 = [(-1 / 3, "-1/3"), (1 / 3, "1/3")]
    graph("ca_d3a", [(lambda x: 3 * x, "blue", None, -1 / 3, 1 / 3)], (-0.6, 0.6), (-1.5, 1.5), xt=T13, yt=T1, dots=[(-1 / 3, -1), (1 / 3, 1)], w=150, h=150)
    graph("ca_d3b", [(lambda x: x + 2, "blue")], (-3, 2), (-1.5, 3.5), xt=[(-2, "-2")], yt=[(2, "2")], w=150, h=150)
    graph("ca_y3a", [(lambda x: x / 3, "blue", None, -3, 3)], (-4, 4), (-1.5, 1.5), xt=[(-3, "-3"), (3, "3")], yt=T1, dots=[(-3, -1), (3, 1)], w=150, h=150)
    graph("ca_y3b", [(lambda x: 2 * x, "blue")], (-1.6, 1.6), (-2.5, 2.5), xt=T1, yt=[(2, "2"), (-2, "-2")], w=150, h=150)
    # Exercise 17C
    graph("ca_1a", [(atan, "blue")], (-4, 4), (-2.1, 2.1), xt=T1, yt=yp, hl=[P2, -P2], **W)
    graph("ca_1b", [(COS, "blue", None, -1, 1)], (-1.6, 1.6), (-0.5, 3.7), xt=T1, yt=[(P2, "π/2"), (PI, "π")], dots=[(-1, PI), (1, 0)], **W)
    graph("ca_1c", [(SIN, "blue", None, -1, 1)], (-1.6, 1.6), (-2.1, 2.1), xt=T1, yt=yp, dots=[(-1, -P2), (1, P2)], **W)
    graph("ca_2a", [(fn(lambda x: asin(x - 1), 0, 2), "blue", None, 0, 2)], (-0.6, 2.6), (-2.1, 2.1), xt=[(1, "1"), (2, "2")], yt=yp,
          dots=[(0, -P2), (2, P2)], **W)
    graph("ca_2b", [(fn(lambda x: acos(x + 1), -2, 0), "blue", None, -2, 0)], (-2.6, 0.6), (-0.5, 3.7), xt=[(-2, "-2"), (-1, "-1")],
          yt=[(P2, "π/2"), (PI, "π")], dots=[(-2, PI), (0, 0)], **W)
    graph("ca_2c", [(lambda x: atan(x) + P2, "blue")], (-4, 4), (-0.5, 3.6), xt=[], yt=[(P2, "π/2"), (PI, "π")], hl=[PI], **W)
    graph("ca_3a", [(fn(lambda x: -acos(x), -1, 1), "blue", None, -1, 1)], (-1.6, 1.6), (-3.7, 0.5), xt=T1, yt=[(-P2, "-π/2"), (-PI, "-π")],
          dots=[(-1, -PI), (1, 0)], **W)
    graph("ca_3b", [(lambda x: atan(-x), "blue")], (-4, 4), (-2.1, 2.1), xt=[], yt=yp, hl=[P2, -P2], **W)
    graph("ca_3c", [(SIN, "blue", None, -1, 1)], (-1.6, 1.6), (-2.1, 2.1), xt=T1, yt=yp, dots=[(-1, -P2), (1, P2)], **W)
    graph("ca_4a", [(COS, "blue", None, -1, 1), (fn(lambda x: asin(x) - P2, -1, 1), "teal", None, -1, 1)], (-1.6, 2.6), (-3.7, 3.7),
          xt=T1, yt=[(PI, "π"), (P2, "π/2"), (-P2, "-π/2"), (-PI, "-π")], dots=[(-1, PI), (1, 0), (-1, -PI)], w=240, h=200,
          labels=[(-0.55, acos(-0.55), "cos⁻¹x", -6, 0, "end"), (0.3, -2.7, "sin⁻¹x − π/2", 0, 0, "start")])
    graph("ca_4bi", [(lambda x: atan(-x), "blue")], (-4, 4), (-2.1, 2.1), xt=[], yt=yp, hl=[P2, -P2], **W)
    graph("ca_4bii", [(COS, "blue", None, -1, 1), (fn(lambda x: acos(-x), -1, 1), "teal", None, -1, 1)], (-1.6, 1.6), (-0.5, 3.7),
          xt=T1, yt=[(P2, "π/2"), (PI, "π")], dots=[(-1, PI), (1, 0), (-1, 0), (1, PI)], hl=[P2], **W)
    graph("ca_5", [(fn(lambda x: asin(1 - x), 0, 2), "blue", None, 0, 2)], (-0.6, 2.6), (-2.1, 2.1), xt=[(1, "1"), (2, "2")], yt=yp,
          dots=[(0, P2), (1, 0), (2, -P2)], **W)
    graph("ca_6a", [(fn(lambda x: acos(1 - x), 0, 2), "blue", None, 0, 2)], (-0.6, 2.6), (-0.5, 3.7), xt=[(1, "1"), (2, "2")],
          yt=[(P2, "π/2"), (PI, "π")], dots=[(0, 0), (2, PI)], **W)
    graph("ca_6b", [(fn(lambda x: -asin(x + 1), -2, 0), "blue", None, -2, 0)], (-2.6, 0.6), (-2.1, 2.1), xt=[(-2, "-2"), (-1, "-1")], yt=yp,
          dots=[(-2, P2), (0, -P2)], **W)
    graph("ca_6c", [(lambda x: -atan(1 - x), "blue")], (-3, 5), (-2.1, 2.1), xt=[(1, "1")], yt=yp + [(-P4, "-π/4")], hl=[P2, -P2], **W)
    graph("ca_7a", [(lambda x: 2 * x, "blue", None, -0.5, 0.5)], (-1.4, 1.4), (-1.5, 1.5), xt=[(-0.5, "-1/2"), (0.5, "1/2")], yt=T1,
          dots=[(-0.5, -1), (0.5, 1)], w=150, h=150)
    graph("ca_7b", [(lambda x: x / 2, "blue", None, -2, 2)], (-2.6, 2.6), (-1.5, 1.5), xt=[(-2, "-2"), (2, "2")], yt=T1,
          dots=[(-2, -1), (2, 1)], w=150, h=150)
    graph("ca_7c", [(lambda x: x - 1, "blue")], (-2, 3), (-2.5, 2.5), xt=[(1, "1")], yt=[(-1, "-1")], w=150, h=150)
    graph("ca_8", [(fn(lambda x: sqrt(1 - x * x), -1, 1), "blue", None, -1, 1)], (-1.6, 1.6), (-0.4, 1.5), xt=T1, yt=[(1, "1")],
          dots=[(-1, 0), (1, 0)], w=170, h=120)
    tt = lambda x: None if abs(cos(x)) < 0.02 else atan(tan(x))
    graph("ca_9", [(tt, "blue")], (-2.3 * PI, 2.3 * PI), (-2.2, 2.2), xt=[(-2 * PI, "-2π"), (-PI, "-π"), (PI, "π"), (2 * PI, "2π")], yt=yp,
          hl=[P2, -P2], hollow=[(k * P2, s_ * P2) for k in (-3, -1, 1, 3) for s_ in (1, -1)], w=300, h=150)
    graph("ca_10", [(lambda x: asin(cos(x)), "blue")], (-2.3 * PI, 2.3 * PI), (-2.2, 2.2), xt=[(-2 * PI, "-2π"), (-PI, "-π"), (PI, "π"), (2 * PI, "2π")],
          yt=yp, w=300, h=150)
    graph("ca_11d", [(lambda x: asin(sin(x)), "blue")], (-2.3 * PI, 2.3 * PI), (-2.2, 2.2), xt=[(-2 * PI, "-2π"), (-PI, "-π"), (PI, "π"), (2 * PI, "2π")],
          yt=yp, w=300, h=150)
    graph("ca_11e", [(lambda x: acos(sin(x)), "blue")], (-2.3 * PI, 2.3 * PI), (-0.6, 3.8), xt=[(-1.5 * PI, "-3π/2"), (-P2, "-π/2"), (P2, "π/2"), (1.5 * PI, "3π/2")],
          yt=[(P2, "π/2"), (PI, "π")], w=300, h=150)
    # past-paper answer sketches
    graph("ca_pp9", [(fn(lambda x: 4 * acos(x / 6) - P2, -6, 6), "blue", None, -6, 6)], (-7.5, 7.5), (-2.4, 12.3), xt=[(-6, "-6"), (6, "6")],
          yt=[(3.5 * PI, "7π/2"), (1.5 * PI, "3π/2"), (-P2, "-π/2")], dots=[(-6, 3.5 * PI), (0, 1.5 * PI), (6, -P2)], w=200, h=200)
    graph("ca_pp10", [(fn(lambda x: asin(3 * x + 1), -2 / 3, 0), "blue", None, -2 / 3, 0), (COS, "teal", None, -1, 1)], (-1.9, 1.4), (-2.1, 3.7),
          xt=[(-1, "-1"), (-2 / 3, "-2/3"), (1, "1")], yt=[(P2, "π/2"), (PI, "π"), (-P2, "-π/2")], dots=[(0, P2), (-2 / 3, -P2), (-1, PI), (1, 0)],
          labels=[(-0.66, asin(3 * -0.66 + 1), "arcsin(3x + 1)", -7, 8, "end"), (0.55, acos(0.55), "arccos x", 7, 0, "start")], w=250, h=200)
    graph("ca_pp11i", [(fn(lambda x: asin((4 * x - 1) / 2), -0.25, 0.75), "blue", None, -0.25, 0.75)], (-0.6, 1.1), (-2.1, 2.1),
          xt=[(-0.25, "-1/4"), (0.25, "1/4"), (0.75, "3/4")], yt=[(P2, "π/2"), (-PI / 6, "-π/6"), (-P2, "-π/2")],
          dots=[(-0.25, -P2), (0.75, P2), (0.25, 0), (0, -PI / 6)], w=190, h=170)
    graph("ca_pp11ii", [(fn(lambda x: asin((4 * abs(x) - 1) / 2), -0.75, 0.75), "blue", None, -0.75, 0.75)], (-1.1, 1.1), (-0.9, 2.1),
          xt=[(-0.75, "-3/4"), (-0.25, "-1/4"), (0.25, "1/4"), (0.75, "3/4")], yt=[(P2, "π/2")],
          dots=[(-0.75, P2), (0.75, P2)], hollow=[(-0.25, 0), (0.25, 0)], w=210, h=150)



# ---------------- 17D ----------------
def fig_17d():
    # proof of cos(a - b): circle, rays to A (angle a) and B (angle b)
    f = Fig(200, 190)
    cx, cy, r = 95, 100, 70
    f.raw(f'<path d="M{cx - r},{cy} A{r},{r} 0 1 1 {cx + r},{cy} A{r},{r} 0 1 1 {cx - r},{cy}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    f.arrow(cx - r - 14, cy, cx + r + 18, cy, width=1.1)
    f.arrow(cx, cy + r + 12, cx, cy - r - 16, width=1.1)
    for ang, name in ((110, "A"), (35, "B")):
        a = radians(ang)
        px, py = cx + r * cos(a), cy - r * sin(a)
        f.line(cx, cy, px, py, color="blue", width=1.8)
        f.dot(px, py, 3)
        f.raw(lab(px + 15 * cos(a), py - 15 * sin(a), name, size=12, bg=False))
    f.line(cx + r * cos(radians(110)), cy - r * sin(radians(110)), cx + r * cos(radians(35)), cy - r * sin(radians(35)), color="faint", width=1.2, dash="4 3")
    f.arc(cx, cy, 16, 0, 35)
    f.arc(cx, cy, 26, 0, 110)
    f.arc(cx, cy, 36, 35, 110, color="rose")
    f.raw(lab(cx + 22 * cos(radians(17)) + 4, cy - 22 * sin(radians(17)), "β", size=12))
    f.raw(lab(cx - 30, cy - 14, "α", size=12))
    f.raw(lab(cx + 52 * cos(radians(72)), cy - 52 * sin(radians(72)), "α − β", size=11, color=ACC["rose"]))
    f.raw(lab(cx - 10, cy + 12, "O", size=12, bg=False))
    f.raw(lab(cx + r + 22, cy + 10, "x", size=12, bg=False, italic=True))
    f.raw(lab(cx - 9, cy - r - 14, "y", size=12, bg=False, italic=True))
    save("d_proof", f)
    # Example 8 triangles
    def tri(name, opp, adj, hyp, ang_lab, w=120, h=95, flip=False):
        f = Fig(w, h)
        x0, y0, x1, y1 = 18, h - 18, w - 30, 16
        if flip:   # angle below the axis: right angle at top right
            f.poly([(x0, 16), (x1, 16), (x1, h - 18)], color="blue", opacity=0.08)
            f.right(x1, 16, -1, 1, s=7)
            f.raw(lab((x0 + x1) / 2, 8, adj, size=12, bg=False))
            f.raw(lab(x1 + 6, (16 + h - 18) / 2, opp, "start", size=12, bg=False))
            f.raw(lab((x0 + x1) / 2 - 10, (16 + h - 18) / 2 + 12, hyp, size=12, bg=False))
            f.raw(lab(x0 + 34, 28, ang_lab, size=12))
        else:
            f.poly([(x0, y0), (x1, y0), (x1, y1)], color="blue", opacity=0.08)
            f.right(x1, y0, -1, -1, s=7)
            f.raw(lab((x0 + x1) / 2, y0 + 11, adj, size=12, bg=False))
            f.raw(lab(x1 + 6, (y0 + y1) / 2, opp, "start", size=12, bg=False))
            f.raw(lab((x0 + x1) / 2 - 10, (y0 + y1) / 2 - 8, hyp, size=12, bg=False))
            f.raw(lab(x0 + 34, y0 - 10, ang_lab, size=12))
        save(name, f)
    tri("d_ex8a", "1", "2√2", "3", "α")
    tri("d_ex8b", "3", "4", "5", "β", flip=True)
    # Q16
    f = Fig(300, 100)
    R_, Q_, P_, T_ = (20, 80), (155, 80), (245, 80), (155, 20)
    f.poly([R_, P_, T_], color="blue", opacity=0.06)
    f.line(*Q_, *T_, width=1.3)
    f.right(Q_[0], Q_[1], 1, -1, s=7)
    for (x_, y_), n_, dx, dy in ((R_, "R", -10, 4), (Q_, "Q", 0, 13), (P_, "P", 10, 4), (T_, "T", 0, -11)):
        f.raw(lab(x_ + dx, y_ + dy, n_, size=12, bg=False))
    f.raw(lab(88, 92, "3 cm", size=11, bg=False))
    f.raw(lab(200, 92, "2 cm", size=11, bg=False))
    f.raw(lab(150, 58, "1 cm", "end", size=11, bg=False))
    f.raw(lab(75, 72, "β", size=12))
    f.raw(lab(215, 73, "α", size=12))
    save("d_q16", f)
    # Q17: two 6 x 3 rectangles sharing the diagonal PQ
    import math as m
    sc = 22
    W_, H_ = 6 * sc, 3 * sc
    P0 = (30, 150)
    rect1 = [(P0[0], P0[1]), (P0[0] + W_, P0[1]), (P0[0] + W_, P0[1] - H_), (P0[0], P0[1] - H_)]
    Q0 = (P0[0] + W_, P0[1] - H_)
    d = m.atan2(3, 6)
    rot = 2 * d                      # reflect the rectangle in the diagonal
    def rp(x, y):
        dx, dy = x - P0[0], -(y - P0[1])
        X = dx * m.cos(rot) - dy * m.sin(rot)
        Y = dx * m.sin(rot) + dy * m.cos(rot)
        return (P0[0] + X, P0[1] - Y)
    # second rectangle: reflection of the first in PQ
    def refl(x, y):
        dx, dy = x - P0[0], -(y - P0[1])
        c2, s2 = m.cos(2 * d), m.sin(2 * d)
        X = dx * c2 + dy * s2
        Y = dx * s2 - dy * c2
        return (P0[0] + X, P0[1] - Y)
    rect2 = [refl(*p) for p in rect1]
    f = Fig(230, 175)
    f.poly(rect1, color="blue", opacity=0.05)
    f.poly(rect2, color="teal", opacity=0.05)
    f.line(P0[0], P0[1], Q0[0], Q0[1], color="faint", dash="4 3", width=1.2)
    f.raw(lab(P0[0] - 9, P0[1] + 6, "P", size=12, bg=False))
    f.raw(lab(Q0[0] + 9, Q0[1] - 4, "Q", size=12, bg=False))
    f.raw(lab(P0[0] + 13, P0[1] - 22, "α", size=12))
    save("d_q17", f)



# ---------------- 17E ----------------
def fig_17e():
    import math as m
    h = 10 * m.sqrt(3)
    sc = 7.0
    ox, oy = 20, 22
    A_, B_, C_ = (ox, oy), (ox + 20 * sc, oy), (ox + 30 * sc, oy)
    W_ = (C_[0], oy + h * sc)
    f = Fig(int(C_[0] + 40), int(W_[1] + 22))
    f.line(*A_, *C_, width=1.4)
    f.line(*C_, *W_, width=1.4, dash="4 3", color="faint")
    f.line(*A_, *W_, color="blue", width=1.5)
    f.line(*B_, *W_, color="blue", width=1.5)
    f.right(C_[0], C_[1], -1, 1, s=7)
    for (x_, y_), n_, dx, dy in ((A_, "A", -10, -2), (B_, "B", 0, -11), (C_, "C", 10, -2), (W_, "W", 0, 13)):
        f.raw(lab(x_ + dx, y_ + dy, n_, size=12, bg=False))
    f.raw(lab((A_[0] + B_[0]) / 2, oy - 10, "20 m", size=11, bg=False))
    f.raw(lab((B_[0] + C_[0]) / 2, oy - 10, "10 m", size=11, bg=False))
    f.raw(lab(C_[0] + 8, (C_[1] + W_[1]) / 2, "h", "start", size=12, bg=False))
    f.raw(lab(A_[0] + 34, oy + 9, "θ", size=12))
    f.raw(lab(B_[0] + 17, oy + 14, "2θ", size=12))
    save("e_q11", f)


if __name__ == "__main__":
    for _name, _f in list(globals().items()):
        if _name.startswith("fig_") and callable(_f):
            _f()
