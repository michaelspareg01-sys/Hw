"""Figures for the Year 10 Circle Geometry pack: helpers (Fig, CF) and the revision figures.

Lesson figures live in figs_c1.py (and later figs_c2.py, figs_c3.py); they import the helpers below.
Run: python3 figs.py && python3 figs_c1.py   (writes svg/*.svg)
"""
import os
import sys
from math import sin, cos, atan2, pi, sqrt, radians, degrees, hypot
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from plots import ACC, INK, FAINT, _txt  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")
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

    def text(self, x, y, s, anchor="middle", size=12, color="ink", italic=False, weight=500):
        self.items.append(_txt(x, y, s, anchor, size=size, color=ACC[color], italic=italic, weight=weight))
        return self

    def dot(self, x, y, r=2.6, color="ink"):
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{ACC[color]}"/>')
        return self

    def raw(self, s):
        self.items.append(s)
        return self

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="Inter, Arial, sans-serif">' + "".join(self.items) + "</svg>")


def _ang(p, q):
    """Direction of q from p in degrees, measured anticlockwise on the page (screen y is down)."""
    return degrees(atan2(-(q[1] - p[1]), q[0] - p[0]))


class CF(Fig):
    """Geometry figure with point helpers. Points are (x, y) pixel pairs."""

    def circle(self, c, r, color="ink", width=1.6, dash=None, fill=None, opacity=0.18):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        f = f'fill="{ACC[fill]}" fill-opacity="{opacity}"' if fill else 'fill="none"'
        self.items.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r:.1f}" {f} stroke="{ACC[color]}" stroke-width="{width}"{d}/>')
        return self

    @staticmethod
    def on(c, r, deg):
        """Point on the circle with centre c and radius r at angle deg (anticlockwise from the right)."""
        return (c[0] + r * cos(radians(deg)), c[1] - r * sin(radians(deg)))

    def seg(self, p, q, color="ink", width=1.6, dash=None):
        return self.line(p[0], p[1], q[0], q[1], color, width, dash)

    def pdot(self, p, r=2.6, color="ink"):
        return self.dot(p[0], p[1], r, color)

    def lab(self, p, s, dx=0, dy=0, size=12, italic=True, color="ink", anchor="middle"):
        return self.text(p[0] + dx, p[1] + dy, s, anchor=anchor, size=size, italic=italic, color=color)

    def out(self, p, c, s, d=11, size=12, italic=True, color="ink"):
        """Label s placed d px from p, directly away from the point c."""
        a = atan2(p[1] - c[1], p[0] - c[0])
        return self.text(p[0] + d * cos(a), p[1] + d * sin(a), s, size=size, italic=italic, color=color)

    def tick(self, p, q, n=1, s=4.5, gap=3.2, color="ink", t=0.5):
        """n short marks across the segment pq at the fraction t along it (equal-length marks)."""
        mx, my = p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
        L = hypot(q[0] - p[0], q[1] - p[1])
        ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        nx, ny = -uy, ux
        for k in range(n):
            o = (k - (n - 1) / 2) * gap
            cx, cy = mx + o * ux, my + o * uy
            self.line(cx - s * nx, cy - s * ny, cx + s * nx, cy + s * ny, color, 1.2)
        return self

    def angle(self, v, p, q, r=14, n=1, color="ink", gap=3.0, width=1.1):
        """Arc(s) at vertex v between rays vp and vq, through the smaller angle."""
        a0, a1 = _ang(v, p), _ang(v, q)
        d = (a1 - a0) % 360
        if d > 180:
            a0, a1 = a1, a0
            d = 360 - d
        for k in range(n):
            rr = r + k * gap
            x0, y0 = v[0] + rr * cos(radians(a0)), v[1] - rr * sin(radians(a0))
            x1, y1 = v[0] + rr * cos(radians(a0 + d)), v[1] - rr * sin(radians(a0 + d))
            self.items.append(f'<path d="M{x0:.1f},{y0:.1f} A{rr},{rr} 0 0 0 {x1:.1f},{y1:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"/>')
        return self

    def reflex(self, v, p, q, r=14, n=1, color="ink", gap=3.0, width=1.1):
        """Arc(s) at vertex v between rays vp and vq, through the larger (reflex) angle."""
        a0, a1 = _ang(v, p), _ang(v, q)
        d = (a1 - a0) % 360
        if d < 180:
            a0, a1 = a1, a0
            d = 360 - d
        for k in range(n):
            rr = r + k * gap
            x0, y0 = v[0] + rr * cos(radians(a0)), v[1] - rr * sin(radians(a0))
            x1, y1 = v[0] + rr * cos(radians(a0 + d)), v[1] - rr * sin(radians(a0 + d))
            self.items.append(f'<path d="M{x0:.1f},{y0:.1f} A{rr},{rr} 0 1 0 {x1:.1f},{y1:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"/>')
        return self

    def alab(self, v, p, q, s, d=24, size=11.5, italic=False, color="ink", reflex=False):
        """Label s on the bisector of angle pvq, d px from v (the reflex side if reflex=True)."""
        a0, a1 = radians(_ang(v, p)), radians(_ang(v, q))
        bx, by = cos(a0) + cos(a1), sin(a0) + sin(a1)
        if hypot(bx, by) < 1e-9:
            bx, by = -sin(a0), cos(a0)
        if reflex:
            bx, by = -bx, -by
        L = hypot(bx, by)
        return self.text(v[0] + d * bx / L, v[1] - d * by / L, s, size=size, italic=italic, color=color)

    def right(self, v, p, q, s=7, color="ink"):
        """Right-angle mark at v between rays vp and vq."""
        def unit(a):
            L = hypot(a[0] - v[0], a[1] - v[1])
            return ((a[0] - v[0]) / L, (a[1] - v[1]) / L)
        u, w = unit(p), unit(q)
        a = (v[0] + s * u[0], v[1] + s * u[1])
        b = (v[0] + s * (u[0] + w[0]), v[1] + s * (u[1] + w[1]))
        c = (v[0] + s * w[0], v[1] + s * w[1])
        self.items.append(f'<path d="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} L{c[0]:.1f},{c[1]:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="1.1"/>')
        return self

    def parr(self, p, q, n=1, t=0.5, s=6, color="ink"):
        """n arrowheads on segment pq at fraction t, pointing from p to q (parallel-line marks)."""
        L = hypot(q[0] - p[0], q[1] - p[1])
        ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        for k in range(n):
            mx = p[0] + t * (q[0] - p[0]) + (k - (n - 1) / 2) * 5 * ux
            my = p[1] + t * (q[1] - p[1]) + (k - (n - 1) / 2) * 5 * uy
            a = atan2(uy, ux)
            p1 = (mx - s * cos(a - 0.45), my - s * sin(a - 0.45))
            p2 = (mx - s * cos(a + 0.45), my - s * sin(a + 0.45))
            self.items.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{mx:.1f},{my:.1f} L{p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="1.3"/>')
        return self


def ftext(f, x, y, s, size=11, italic=False, color="ink", rmax=14):
    """Text centred near (x, y), nudged (spiral search, <= rmax px) to a spot svg_overlap does not flag."""
    from svg_overlap import check_string
    base = len(f.items)
    for r in range(0, rmax + 1):
        for k in range(16 if r else 1):
            dx, dy = (r * cos(2 * pi * k / 16), r * sin(2 * pi * k / 16)) if r else (0, 0)
            f.items = f.items[:base]
            f.text(x + dx, y + dy, s, size=size, italic=italic, color=color)
            probs = [p for p in check_string(f.svg()) if p.startswith(repr(s.replace("-", "\u2212")) ) or p.startswith(repr(s))]
            if not probs:
                return f
    f.items = f.items[:base]
    return f.text(x, y, s, size=size, italic=italic, color=color)


def ext(p, q, k):
    """The point p + k (q - p)."""
    return (p[0] + k * (q[0] - p[0]), p[1] + k * (q[1] - p[1]))


def foot(p, a, b):
    """Foot of the perpendicular from p to the line ab."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    return (a[0] + t * dx, a[1] + t * dy)


def cat(name, panels, gap=18, labels=None, size=12):
    """Join several CF panels side by side into one figure (optional bold part letters at top left)."""
    W = sum(p.w for p in panels) + gap * (len(panels) - 1)
    H = max(p.h for p in panels)
    f = Fig(W, H)
    x = 0
    for i, p in enumerate(panels):
        f.raw(f'<g transform="translate({x},0)">' + "".join(p.items) + "</g>")
        x += p.w + gap
    return f


def save_flat(name, f):
    """save() for a figure built with cat(): translate groups are flattened first."""
    from figfit import flatten
    f2 = Fig(f.w, f.h)
    f2.items = [flatten(f.svg())[len(f.svg().split(">", 1)[0]) + 1:-len("</svg>")]]
    save(name, f2)


# ---------------- Revision: Year 7 to 9 geometry ----------------


def tri_mark(f, v, p, q, txt, d=22, size=11.5, n=1, r=13):
    f.angle(v, p, q, r=r, n=n)
    if txt:
        f.alab(v, p, q, txt, d=d, size=size)


def fig_rev():
    # --- parallel lines: corresponding, alternate, co-interior (Year 8 6B Key ideas) ---
    panels = []
    for kind in ("corr", "alt", "coint"):
        f = CF(170, 112)
        L1 = ((12, 34), (158, 34))
        L2 = ((12, 82), (158, 82))
        f.seg(*L1).seg(*L2).parr(L1[0], L1[1], t=0.82).parr(L2[0], L2[1], t=0.82)
        T0, T1 = (58, 104), (112, 10)
        f.seg(T0, T1)
        def cut(y):
            t = (y - T0[1]) / (T1[1] - T0[1])
            return (T0[0] + t * (T1[0] - T0[0]), y)
        X1, X2 = cut(34), cut(82)
        up, rt, lt, dn = T1, (158, 34), (12, 34), T0
        if kind == "corr":
            f.angle(X1, rt, up, r=11).text(X1[0] + 20, X1[1] - 12, "a°", size=10.5, italic=True)
            f.angle(X2, (158, 82), up, r=11)and ftext(f, X2[0] + 20, X2[1] - 12, "b°", size=10.5, italic=True)
            f.text(118, 108, "corresponding", size=10, color="faint")
        elif kind == "alt":
            f.angle(X1, lt, dn, r=11).text(X1[0] - 20, X1[1] + 12, "a°", size=10.5, italic=True)
            f.angle(X2, (158, 82), up, r=11)and ftext(f, X2[0] + 20, X2[1] - 12, "b°", size=10.5, italic=True)
            f.text(118, 108, "alternate", size=10, color="faint")
        else:
            f.angle(X1, rt, dn, r=11).text(X1[0] + 18, X1[1] + 13, "y°", size=10.5, italic=True)
            f.angle(X2, (158, 82), up, r=11).text(X2[0] + 20, X2[1] - 12, "x°", size=10.5, italic=True)
            f.text(118, 108, "co-interior", size=10, color="faint")
        panels.append(f)
    save_flat("rev_parallel", cat("rev_parallel", panels, gap=22))

    # --- isosceles triangle and exterior angle (Year 8 6C Key ideas) ---
    f = CF(170, 132)
    A, B, C = (85, 14), (35, 112), (135, 112)
    f.poly([A, B, C], color=None, opacity=0)
    f.tick(A, B).tick(A, C)
    f.angle(B, A, C, r=12).angle(C, A, B, r=12)
    f.lab(A, "apex", dy=-6, size=10, italic=False, color="faint")
    f.text(85, 128, "base", size=10, color="faint")
    g = CF(190, 132)
    P, Q, R = (60, 18), (20, 110), (130, 110)
    E = (180, 110)
    g.poly([P, Q, R], color=None, opacity=0).seg(R, E)
    g.angle(P, Q, R, r=12).alab(P, Q, R, "x°", d=24, size=11, italic=True)
    g.angle(Q, P, R, r=12).alab(Q, P, R, "y°", d=24, size=11, italic=True)
    g.angle(R, P, E, r=13).alab(R, P, E, "z°", d=26, size=11, italic=True)
    g.text(110, 128, "z = x + y", size=10.5, color="faint")
    save_flat("rev_isos_ext", cat("rev_isos_ext", [f, g], gap=40))

    # --- Year 8 Example 3 (6C): two triangles ---
    f = CF(150, 104)
    A, B, C = (102, 12), (14, 92), (122, 92)
    f.poly([A, B, C], color=None, opacity=0)
    f.angle(A, B, C, r=12).alab(A, B, C, "a°", d=24, size=11, italic=True)
    f.angle(B, A, C, r=14).alab(B, A, C, "38°", d=34, size=11)
    f.angle(C, A, B, r=11).alab(C, A, B, "92°", d=26, size=11)
    g = CF(150, 104)
    P, Q, R = (18, 14), (24, 96), (136, 46)
    g.poly([P, Q, R], color=None, opacity=0).tick(P, R).tick(Q, R)
    g.angle(P, Q, R, r=12).alab(P, Q, R, "a°", d=24, size=11, italic=True)
    g.angle(R, P, Q, r=16).alab(R, P, Q, "26°", d=34, size=11)
    save_flat("rev_ex3", cat("rev_ex3", [f, g], gap=40))

    # --- Year 8 Example 13 (8H): parallelogram with diagonals ---
    f = CF(210, 120)
    A, B, C, D = (20, 104), (140, 104), (190, 18), (70, 18)
    f.poly([A, B, C, D], color=None, opacity=0)
    f.seg(A, C, color="rose", dash="4 3").seg(B, D, color="rose", dash="4 3")
    E = (105, 61)
    f.parr(A, D, t=0.55).parr(B, C, t=0.55).parr(A, B, n=2, t=0.5).parr(D, C, n=2, t=0.5)
    f.tick(A, B, n=1, t=0.3).tick(D, C, n=1, t=0.3)
    f.lab(A, "A", dx=-9, dy=6).lab(B, "B", dx=8, dy=6).lab(C, "C", dx=9, dy=-4).lab(D, "D", dx=-9, dy=-4)
    f.lab(E, "E", dx=0, dy=-12)
    save("rev_ex13", f)


def tri(f, pts, ticks=(), right=None):
    f.poly(pts, color=None, opacity=0)
    for (i, j, n) in ticks:
        f.tick(pts[i], pts[j], n=n)
    if right is not None:
        v = pts[right]
        f.right(v, pts[right - 1], pts[(right + 1) % len(pts)])
    return f


def inlab(f, pts, k, s, d=14, size=11, italic=False):
    """Label s inside the triangle at vertex k, on the bisector, d px from the vertex (no arc, as in the book)."""
    v, p, q = pts[k], pts[k - 1], pts[(k + 1) % 3]
    from svg_overlap import text_width
    a0, a1 = radians(_ang(v, p)), radians(_ang(v, q))
    half = abs(((degrees(a1 - a0) + 180) % 360) - 180) / 2
    need = (text_width(s, size) / 2 + 0.45 * size + 3) / max(sin(radians(half)), 0.05)
    la, lb, lc = hypot(p[0] - q[0], p[1] - q[1]), hypot(v[0] - q[0], v[1] - q[1]), hypot(v[0] - p[0], v[1] - p[1])
    ix = (la * v[0] + lb * p[0] + lc * q[0]) / (la + lb + lc)
    iy = (la * v[1] + lb * p[1] + lc * q[1]) / (la + lb + lc)
    dI = hypot(ix - v[0], iy - v[1])
    return f.alab(v, p, q, s, d=min(max(d, need), 0.66 * dI), size=size, italic=italic)


def olab(f, pts, i, j, s, d=10, size=10.5, t=0.5):
    """Label s beside side ij of the polygon pts, d px outside it."""
    p, q = pts[i], pts[j]
    cx, cy = sum(a for a, _ in pts) / len(pts), sum(b for _, b in pts) / len(pts)
    mx, my = p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
    L = hypot(q[0] - p[0], q[1] - p[1])
    nx, ny = (q[1] - p[1]) / L, -(q[0] - p[0]) / L
    if nx * (cx - mx) + ny * (cy - my) > 0:
        nx, ny = -nx, -ny
    return f.text(mx + d * nx, my + d * ny + 0.0, s, size=size)


def apex(p, q, ap, aq):
    """Third vertex R of triangle PQR with angle ap at P and aq at Q, on the upper side of PQ on the page."""
    base = atan2(-(q[1] - p[1]), q[0] - p[0])        # direction p->q, maths sense
    L = hypot(q[0] - p[0], q[1] - p[1])
    ar = 180 - ap - aq
    pr = L * sin(radians(aq)) / sin(radians(ar))
    a = base + radians(ap)
    return (p[0] + pr * cos(a), p[1] - pr * sin(a))


def fig_warm():
    # --- Warm-up Q1: Year 8 Ex 6C Q6 a-c (isosceles triangles, drawn to scale) ---
    a = CF(140, 136)
    L, R = (12, 128), (128, 128)
    T = apex(L, R, 65, 65)
    P = [T, L, R]
    tri(a, P, ticks=((0, 1, 2), (0, 2, 2)))
    inlab(a, P, 0, "50°", d=26)
    inlab(a, P, 1, "a°", d=22, italic=True)
    b = CF(110, 132)
    Bv, Rv = (22, 124), (92, 98)           # equal sides meet at the right vertex (100 deg)
    T = apex(Bv, Rv, 40, 100)
    P = [T, Bv, Rv]
    tri(b, P, ticks=((0, 2, 2), (2, 1, 2)))
    inlab(b, P, 0, "a°", d=30, italic=True)
    inlab(b, P, 2, "100°", d=26)
    c = CF(140, 132)
    Bv = (26, 124)
    from math import cos as _c, sin as _s
    T = (Bv[0] - 6, Bv[1] - 112)           # top-left vertex, equal sides from the bottom vertex
    ang0 = degrees(atan2(-(T[1] - Bv[1]), T[0] - Bv[0]))
    Rr = CF.on(Bv, 112, ang0 - 28)
    P = [T, Bv, Rr]
    tri(c, P, ticks=((0, 1, 2), (2, 1, 2)))
    inlab(c, P, 0, "a°", d=22, italic=True)
    inlab(c, P, 1, "28°", d=40)
    for nm, f in (("w1a", a), ("w1b", b), ("w1c", c)):
        save(nm, f)

    # --- Warm-up Q2: Year 8 Ex 6C Q10 a, b, e ---
    a = CF(200, 150)
    B, C = (12, 112), (118, 100)
    A = apex(B, C, 60, 60)
    D, E = ext(B, C, 1.55), ext(A, C, 1.42)
    a.poly([A, B, C], color=None, opacity=0).seg(C, D).seg(C, E)
    a.tick(A, B).tick(A, C, t=0.45).tick(B, C)
    a.alab(C, D, E, "a°", d=17, size=11, italic=True)
    a.lab(A, "A", dy=-9).lab(B, "B", dx=-9, dy=4).lab(C, "C", dx=-10, dy=12).lab(D, "D", dx=10, dy=0).lab(E, "E", dx=8, dy=8)
    b = CF(150, 150)
    A, B = (150, 10), (44, 146)
    C = apex(B, A, 29, 22)
    C = apex(A, B, 22, 29) if C[0] > 90 else C
    b.poly([A, B, C], color=None, opacity=0)
    b.reflex(C, A, B, r=7)
    b.alab(C, A, B, "a°", d=20, size=11, italic=True, reflex=True)
    ftext(b, A[0] - 38, A[1] + 40, "22°", size=11, rmax=26)
    inlab(b, [A, B, C], 1, "29°", d=32)
    b.lab(A, "A", dx=9, dy=-2).lab(B, "B", dx=-2, dy=13).lab(C, "C", dx=6, dy=-11)
    e = CF(180, 130)
    C = (96, 64)
    A = CF.on(C, 82, 155.5)
    B = CF.on(C, 82, 155.5 + 49)
    E, D = ext(A, C, 1.75), ext(B, C, 1.75)
    e.seg(A, B).seg(A, E).seg(B, D)
    e.tick(A, C, n=2).tick(B, C, n=2)
    e.alab(C, D, E, "49°", d=22, size=11)
    inlab(e, [B, C, A], 0, "a°", d=22, italic=True)
    e.lab(A, "A", dx=-9, dy=-2).lab(B, "B", dx=-9, dy=6).lab(C, "C", dx=-1, dy=-14).lab(D, "D", dx=9, dy=-2).lab(E, "E", dx=9, dy=4)
    for nm, f in (("w2a", a), ("w2b", b), ("w2e", e)):
        save(nm, f)

    # --- Warm-up Q3: Year 8 Ex 8E Q3 a-d (choose a congruence test) ---
    pa = CF(250, 112)
    for ox, oy in ((0, 0), (122, 34)):
        Bv, Cv = (ox + 34, oy + 58), (ox + 112, oy + 58)
        Av = CF.on(Bv, 52, 110)
        P = [Av, Bv, Cv]
        pa.poly(P, color=None, opacity=0)
        olab(pa, P, 0, 1, "3 cm", d=20)
        olab(pa, P, 1, 2, "4 cm", d=11)
        pa.text(Bv[0] + 18, Bv[1] - 14, "110°", size=10.5)
    pa.h = 128
    pb = CF(250, 116)
    # first: sides 4 (long), 1 (short), 3; second: the same three sides
    def sss(o, rot):
        p0 = o
        p1 = (o[0] + 4 * 24 * cos(radians(rot)), o[1] - 4 * 24 * sin(radians(rot)))
        # third vertex: 3 from p0 and 1 from p1
        d = 4.0
        a_ = (3 ** 2 + d ** 2 - 1) / (2 * d)
        h_ = sqrt(max(0, 9 - a_ * a_))
        ux, uy = cos(radians(rot)), -sin(radians(rot))
        p2 = (o[0] + 24 * (a_ * ux - h_ * uy), o[1] + 24 * (a_ * uy + h_ * ux))
        return [p0, p1, p2]
    P = [(66, 8), (8, 108), (70, 62)]
    pb.poly(P, color=None, opacity=0)
    olab(pb, P, 0, 1, "4 cm", d=14)
    olab(pb, P, 0, 2, "1 cm", d=16)
    olab(pb, P, 1, 2, "3 cm", d=16, t=0.5)
    Q = [(140, 8), (178, 56), (216, 44)]
    pb.poly(Q, color=None, opacity=0)
    olab(pb, Q, 0, 1, "3 cm", d=14)
    olab(pb, Q, 0, 2, "4 cm", d=14)
    olab(pb, Q, 1, 2, "1 cm", d=14)
    pc = CF(250, 124)
    hyp = 7 * 15
    P = [(46, 12), (46, 12 + 4 * 15), (46 + sqrt(49 - 16) * 15, 12)]
    P = [(46, 12), (46 + sqrt(49 - 16) * 15 * 0 + 0, 12 + 0), (0, 0)]
    A0 = (46, 12)
    Bx = (46, 12 + sqrt(49 - 16) * 15)      # vertical leg sqrt(33) units, horizontal leg 4 units
    Cx = (46 + 4 * 15, 12)
    P = [A0, Bx, Cx]
    pc.poly(P, color=None, opacity=0).right(A0, Bx, Cx)
    olab(pc, P, 0, 2, "4 cm", d=10)
    olab(pc, P, 1, 2, "7 cm", d=14)
    # the book's first triangle labels the vertical side 4 cm: keep the book's labelling
    pc.items = pc.items[:2]
    P = [A0, (46, 12 + 4 * 15 * 1.6), (46 + 0.0, 12)]
    Bv = (46, 112)
    Cv = (46 + 40, 12)
    P = [A0, Bv, Cv]
    pc.items = []
    pc.poly(P, color=None, opacity=0).right(A0, Bv, Cv)
    olab(pc, P, 0, 1, "4 cm", d=18)
    olab(pc, P, 1, 2, "7 cm", d=20)
    Rv, Lv, Tv = (196, 112), (152, 112), (196, 10)
    Q = [Rv, Lv, Tv]
    pc.poly(Q, color=None, opacity=0).right(Rv, Lv, Tv)
    olab(pc, Q, 0, 1, "4 cm", d=11)
    olab(pc, Q, 1, 2, "7 cm", d=16)
    pd = CF(250, 124)
    Bl, Rt = (10, 116), (100, 78)
    Tp = apex(Bl, Rt, 50, 80)
    P = [Tp, Bl, Rt]
    pd.poly(P, color=None, opacity=0)
    inlab(pd, P, 1, "50°", d=24, size=10.5)
    inlab(pd, P, 2, "80°", d=20, size=10.5)
    olab(pd, P, 0, 2, "3 cm", d=16)
    Tl, Tr = (132, 10), (222, 26)
    Bt = apex(Tr, Tl, 80, 50)
    Bt = (2 * ((Tl[0] + Tr[0]) / 2) - Bt[0], Bt[1]) if Bt[1] < Tl[1] else Bt
    Q = [Tl, Tr, Bt]
    pd.poly(Q, color=None, opacity=0)
    inlab(pd, Q, 0, "50°", d=20, size=10.5)
    inlab(pd, Q, 1, "80°", d=20, size=10.5)
    olab(pd, Q, 1, 2, "3 cm", d=18)
    for nm, f in (("w3a", pa), ("w3b", pb), ("w3c", pc), ("w3d", pd)):
        save(nm, f)

    # --- Warm-up Q4: Year 8 Ex 8G Q3 a-d (similar triangles) ---
    ga = CF(250, 150)
    k = 5.4
    A_ = (30, 84)
    C_, B_ = (30, 84 - 12 * k), (30 + 5 * k, 84)
    T1 = [C_, A_, B_]
    ga.poly(T1, color=None, opacity=0)
    ga.lab(C_, "C", dy=-9).lab(A_, "A", dx=-4, dy=13).lab(B_, "B", dx=5, dy=13)
    olab(ga, T1, 0, 1, "12 m", d=18)
    olab(ga, T1, 0, 2, "13 m", d=18)
    ga.text(45, 98, "5 m", size=10.5)
    D_ = (226, 134)
    F_, E_ = (226, 134 - 24 * k), (226 - 10 * k, 134)
    T2 = [F_, E_, D_]
    ga.poly(T2, color=None, opacity=0)
    ga.lab(F_, "F", dy=-8).lab(E_, "E", dx=-9, dy=4).lab(D_, "D", dx=9, dy=4)
    olab(ga, T2, 0, 1, "26 m", d=16)
    olab(ga, T2, 0, 2, "24 m", d=18)
    olab(ga, T2, 1, 2, "10 m", d=11)
    ga.h = 152
    gb = CF(250, 150)
    A_, B_ = (14, 14), (110, 14)
    C_ = (64, 128)                          # the book does not draw this pair to scale
    T1 = [C_, A_, B_]
    gb.poly(T1, color=None, opacity=0)
    gb.lab(A_, "A", dx=-8, dy=-4).lab(B_, "B", dx=8, dy=-4).lab(C_, "C", dy=13)
    inlab(gb, T1, 1, "75°", d=20, size=10.5)
    inlab(gb, T1, 2, "80°", d=20, size=10.5)
    D_, E_ = (150, 96), (240, 96)
    F_ = (198, 8)
    T2 = [F_, D_, E_]
    gb.poly(T2, color=None, opacity=0)
    gb.lab(D_, "D", dx=-8, dy=8).lab(E_, "E", dx=8, dy=8).lab(F_, "F", dy=-8)
    inlab(gb, T2, 1, "75°", d=20, size=10.5)
    inlab(gb, T2, 2, "80°", d=20, size=10.5)
    gc = CF(290, 150)
    k = 11
    A_ = (62, 14)
    C_ = (A_[0] + 3 * k * 1.9, 14)
    B_ = CF.on(A_, 5 * k * 1.9, 240)
    T1 = [A_, C_, B_]
    gc.poly(T1, color=None, opacity=0)
    gc.lab(A_, "A", dx=-2, dy=-9).lab(C_, "C", dx=8, dy=-4).lab(B_, "B", dx=-8, dy=4)
    olab(gc, T1, 0, 1, "3 m", d=8)
    olab(gc, T1, 0, 2, "5 m", d=12)
    ftext(gc, A_[0] + 6, A_[1] + 10, "120°", size=10)
    D_ = (226, 136)
    F_ = (D_[0] - 6 * k * 1.1, 136)
    E_ = CF.on(D_, 10 * k * 1.1, 60)
    T2 = [D_, E_, F_]
    gc.poly(T2, color=None, opacity=0)
    gc.lab(E_, "E", dx=6, dy=-8).lab(D_, "D", dx=6, dy=12).lab(F_, "F", dx=-9, dy=4)
    olab(gc, T2, 0, 1, "10 m", d=18)
    olab(gc, T2, 2, 0, "6 m", d=11)
    ftext(gc, D_[0] - 14, D_[1] - 22, "120°", size=10)
    gd = CF(270, 120)
    k = 7.5
    A_ = (18, 14)
    C_ = (18 + 11 * k, 14)
    B_ = (18, 14 + sqrt(169 - 121) * k)
    T1 = [A_, C_, B_]
    gd.poly(T1, color=None, opacity=0).right(A_, C_, B_)
    gd.lab(A_, "A", dx=-9, dy=-2).lab(C_, "C", dx=9, dy=0).lab(B_, "B", dx=-9, dy=4)
    olab(gd, T1, 0, 1, "11 m", d=9)
    olab(gd, T1, 1, 2, "13 m", d=12)
    k2 = 5.6
    D_ = (256, 108)
    F_ = (256 - 22 * k2, 108)
    E_ = (256, 108 - sqrt(26 ** 2 - 22 ** 2) * k2)
    T2 = [E_, D_, F_]
    gd.poly(T2, color=None, opacity=0).right(D_, E_, F_)
    gd.lab(E_, "E", dx=0, dy=-8).lab(D_, "D", dx=8, dy=8).lab(F_, "F", dx=-9, dy=2)
    olab(gd, T2, 0, 2, "26 m", d=12)
    olab(gd, T2, 2, 1, "22 m", d=12)
    for nm, f in (("w4a", ga), ("w4b", gb), ("w4c", gc), ("w4d", gd)):
        save(nm, f)

    # --- Warm-up Q5: Year 8 Ex 8H Q5 (square ABCD with diagonals) ---
    f = CF(120, 110)
    A, B, C, D = (20, 14), (100, 14), (100, 94), (20, 94)
    f.poly([A, B, C, D], color=None, opacity=0)
    f.seg(A, C, color="rose", dash="4 3").seg(B, D, color="rose", dash="4 3")
    f.lab(A, "A", dx=-9, dy=-2).lab(B, "B", dx=9, dy=-2).lab(C, "C", dx=9, dy=6).lab(D, "D", dx=-9, dy=6)
    save("w5", f)


if __name__ == "__main__":
    fig_rev()
    fig_warm()
