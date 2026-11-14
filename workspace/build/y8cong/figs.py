"""Figures for the Year 8 Congruence pack: helpers (Fig, CF, grids, isometries) and the revision figures.

The helpers are copied from workspace/build/y10circ/figs.py (circles are drawn round: the radius is
rounded first and the chord is then exactly twice the printed radius). Lesson figures live in
figs_l1.py (and later figs_l2.py, figs_l3.py); they import the helpers below.
Book figures are redrawn from the vector coordinates of the Cambridge PDF (PDF points, y down), scaled.
Run: python3 figs.py && python3 figs_l1.py   (writes svg/*.svg)
"""
import os
import sys
from math import sin, cos, atan2, pi, sqrt, radians, degrees, hypot
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from plots import ACC, INK, FAINT, _txt  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")
os.makedirs(OUT, exist_ok=True)


SCALE = 1.3   # printed size: every figure is drawn 1.3 times its pixel size (the viewBox, and so all coordinates, are unchanged)


def save(name, g, rmax=8):
    import re as _re
    from figfit import fit, untangle, separate  # nudges a flagged label (<= rmax px); grows the frame only where a label would be clipped
    svg = fit(untangle(separate(g.svg()), rmax=rmax))
    head, rest = svg.split(">", 1)
    head = _re.sub(r'(width|height)="([\d.]+)"', lambda m: f'{m.group(1)}="{float(m.group(2)) * SCALE:.1f}"', head)
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(head + ">" + rest)


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
        # drawn as a path: svg_overlap treats <circle> as a dot box. Round the radius and the left end
        # first and take the right end from them, so the printed chord is exactly twice the printed
        # radius: two semicircles, never two bulging >180-degree arcs.
        rr = round(r, 1)
        x0, y = round(c[0] - rr, 1), round(c[1], 1)
        x1 = round(x0 + 2 * rr, 1)
        self.items.append(f'<path d="M{x0:.1f},{y:.1f} A{rr:.1f},{rr:.1f} 0 1 0 {x1:.1f},{y:.1f} A{rr:.1f},{rr:.1f} 0 1 0 {x0:.1f},{y:.1f} Z" {f} stroke="{ACC[color]}" stroke-width="{width}"{d}/>')
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




# ---------------- Year 8 congruence helpers ----------------

GRIDC = "#a9d3ee"     # light blue grid lines (the book's grids)


def polar(p, deg, L):
    """Point at distance L from p in direction deg (degrees anticlockwise on the page; screen y is down)."""
    return (p[0] + L * cos(radians(deg)), p[1] - L * sin(radians(deg)))


def bisect_lab(f, v, a1, a2, s, d=20, size=11.5, italic=False):
    """Label s on the bisector of the sector from direction a1 anticlockwise to a2 (degrees), d px from v."""
    span = (a2 - a1) % 360
    m = a1 + span / 2
    return f.text(v[0] + d * cos(radians(m)), v[1] - d * sin(radians(m)), s, size=size, italic=italic)


def falab(f, v, p, q, s, d=20, size=11.5, reflex=False, rmax=14):
    """alab, then nudged (spiral search) to a spot svg_overlap does not flag."""
    a0, a1 = radians(_ang(v, p)), radians(_ang(v, q))
    bx, by = cos(a0) + cos(a1), sin(a0) + sin(a1)
    if hypot(bx, by) < 1e-9:
        bx, by = -sin(a0), cos(a0)
    if reflex:
        bx, by = -bx, -by
    L = hypot(bx, by)
    return ftext(f, v[0] + d * bx / L, v[1] - d * by / L, s, size=size, rmax=rmax)


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def book(s, x0, y0, ox=14, oy=14):
    """Map book PDF coordinates (points, y down) to figure pixels: scale s, (x0, y0) goes to (ox, oy)."""
    return lambda p: ((p[0] - x0) * s + ox, (p[1] - y0) * s + oy)


def fit_iso(src, dst):
    """Least-squares isometry (rotation, or reflection then rotation, plus translation) taking the list of
    points src onto dst (same order). Returns (function, rms error, is_reflection)."""
    n = len(src)
    best = None
    for refl in (False, True):
        S = [(x, -y) if refl else (x, y) for x, y in src]
        cs = centroid(S)
        cd = centroid(dst)
        num = sum((p[0] - cs[0]) * (q[1] - cd[1]) - (p[1] - cs[1]) * (q[0] - cd[0]) for p, q in zip(S, dst))
        den = sum((p[0] - cs[0]) * (q[0] - cd[0]) + (p[1] - cs[1]) * (q[1] - cd[1]) for p, q in zip(S, dst))
        th = atan2(num, den)
        c, s_ = cos(th), sin(th)

        def F(p, refl=refl, cs=cs, cd=cd, c=c, s_=s_):
            x, y = (p[0], -p[1]) if refl else p
            x, y = x - cs[0], y - cs[1]
            return (cd[0] + c * x - s_ * y, cd[1] + s_ * x + c * y)
        err = sqrt(sum((F(p)[0] - q[0]) ** 2 + (F(p)[1] - q[1]) ** 2 for p, q in zip(src, dst)) / n)
        if best is None or err < best[1]:
            best = (F, err, refl)
    return best


def grid(f, G, xs, ys, color=GRIDC, width=0.7):
    """Grid lines for integer x in xs and y in ys; G maps grid coordinates to pixels."""
    for x in xs:
        f.raw(f'<line x1="{G((x, ys[0]))[0]:.1f}" y1="{G((x, ys[0]))[1]:.1f}" x2="{G((x, ys[-1]))[0]:.1f}" '
              f'y2="{G((x, ys[-1]))[1]:.1f}" stroke="{color}" stroke-width="{width}"/>')
    for y in ys:
        f.raw(f'<line x1="{G((xs[0], y))[0]:.1f}" y1="{G((xs[0], y))[1]:.1f}" x2="{G((xs[-1], y))[0]:.1f}" '
              f'y2="{G((xs[-1], y))[1]:.1f}" stroke="{color}" stroke-width="{width}"/>')


def mtext(f, x, y, s, size=10.5, italic=False, anchor="middle"):
    """Text on a white mask (hides the grid lines drawn before it)."""
    from svg_overlap import text_width, text_extent
    w = text_width(s.replace("-", "−"), size)
    up, dn = text_extent(s, size)
    yb = y + size * 0.35
    x0 = {"middle": x - w / 2, "start": x, "end": x - w}[anchor]
    f.raw(f'<rect x="{x0 - 1.5:.1f}" y="{yb - up - 1.5:.1f}" width="{w + 3:.1f}" height="{up + dn + 3:.1f}" fill="#fff"/>')
    return f.text(x, y, s, anchor=anchor, size=size, italic=italic)


def axes(f, G, xr, yr, nums=True, size=10):
    """x- and y-axes with arrows from xr=(xmin, xmax) and yr, unit ticks, numbers and the labels x, y, O."""
    f.arrow(*G((xr[0], 0)), *G((xr[1], 0)), width=1.3, head=6)
    f.arrow(*G((xr[1], 0)), *G((xr[0], 0)), width=1.3, head=6)
    f.arrow(*G((0, yr[0])), *G((0, yr[1])), width=1.3, head=6)
    f.arrow(*G((0, yr[1])), *G((0, yr[0])), width=1.3, head=6)
    if nums:
        for x in range(int(ceil_(xr[0] + 0.5)), int(xr[1] - 0.4) + 1):
            if x:
                p = G((x, 0))
                f.line(p[0], p[1] - 2.5, p[0], p[1] + 2.5, width=1)
                mtext(f, p[0], p[1] + 10, str(x), size=size - 0.5)
        for y in range(int(ceil_(yr[0] + 0.5)), int(yr[1] - 0.4) + 1):
            if y:
                p = G((0, y))
                f.line(p[0] - 2.5, p[1], p[0] + 2.5, p[1], width=1)
                mtext(f, p[0] - 9, p[1], str(y), size=size, anchor="end")
    p = G((xr[1], 0))
    mtext(f, p[0] + 2, p[1] - 9, "x", size=11.5, italic=True)
    p = G((0, yr[1]))
    mtext(f, p[0] + 10, p[1] + 2, "y", size=11.5, italic=True)
    p = G((0, 0))
    mtext(f, p[0] - 7, p[1] - 8, "O", size=11, italic=True)


def ceil_(v):
    from math import ceil
    return ceil(v)


# ---------------- Revision figures (Year 8 6A-6D and 8A-8C key ideas; warm-up) ----------------

def rays_fig(w, h, v, dirs, labels, L=58, d=19, rights=()):
    """Rays from v in the directions dirs (deg). labels: (a1, a2, text) sectors. rights: (a1, a2) right-angle marks."""
    f = CF(w, h)
    for a in dirs:
        q = polar(v, a, L)
        f.seg(v, q)
    for a1, a2 in rights:
        f.right(v, polar(v, a1, 10), polar(v, a2, 10), s=7)
    for a1, a2, s in labels:
        bisect_lab(f, v, a1, a2, s, d=d)
    return f


def fig_rev_angles():
    # 6A: complementary, supplementary, revolution, vertically opposite
    p1 = rays_fig(130, 112, (22, 62), (56, 0, -34), [(0, 56, "a°"), (-34, 0, "b°")], L=72, d=30, rights=[(-34, 56)])
    p2 = rays_fig(130, 112, (65, 70), (0, 90, 180), [(90, 180, "g°"), (0, 90, "h°")], L=58, d=20)
    p3 = rays_fig(130, 112, (65, 58), (60, 125, 200, 270, 350), [], L=52)
    for a1, a2, s in ((60, 125, "p°"), (350, 60, "q°"), (270, 350, "r°"), (200, 270, "s°")):
        bisect_lab(p3, (65, 58), a1, a2, s, d=19)
    p4 = rays_fig(130, 112, (65, 56), (68, 158, 248, 338), [(68, 158, "t°"), (338, 68, "u°"), (248, 338, "v°"), (158, 248, "w°")], L=56, d=19)
    for pnl, cap in ((p1, "a + b = 90"), (p2, "g + h = 180"), (p3, "p + q + r + s = 360"), (p4, "t = v,  u = w")):
        pnl.h += 18
        pnl.text(pnl.w / 2, pnl.h - 8, cap, size=11.5, italic=True)
    save_flat("rev_angles", cat("rev_angles", [p1, p2, p3, p4], gap=14))


def fig_rev_marks():
    # 6A: the markings AB = AD, BC = CD, angle ABC = angle ADC (kite)
    f = CF(140, 120)
    A, B, C, D = (70, 14), (112, 46), (84, 106), (30, 56)
    f.poly([A, B, C, D], color=None, opacity=0)
    f.tick(A, B, 1).tick(A, D, 1).tick(B, C, 2).tick(D, C, 2)
    f.angle(B, A, C, r=12).angle(D, A, C, r=12)
    for p, s in ((A, "A"), (B, "B"), (C, "C"), (D, "D")):
        f.out(p, centroid([A, B, C, D]), s, d=11)
    save("rev_marks", f)


def fig_rev_parallel():
    # 6B: corresponding, alternate, cointerior (pairs on parallel lines)
    panels = []
    for kind in ("corr", "alt", "coint"):
        f = CF(160, 112)
        L1 = ((10, 36), (150, 36))
        L2 = ((10, 82), (150, 82))
        f.seg(*L1).seg(*L2).parr(L1[0], L1[1], t=0.85).parr(L2[0], L2[1], t=0.85)
        T0, T1 = (58, 106), (108, 10)
        f.seg(T0, T1)

        def cut(y):
            t = (y - T0[1]) / (T1[1] - T0[1])
            return (T0[0] + t * (T1[0] - T0[0]), y)
        X1, X2 = cut(36), cut(82)
        up = _ang(X1, T1)          # transversal direction (up)
        if kind == "corr":
            bisect_lab(f, X1, 0, up, "b°", d=25)
            bisect_lab(f, X2, 0, up, "a°", d=25)
            f.text(150, 104, "a = b", anchor="end", size=11, italic=True)
        elif kind == "alt":
            bisect_lab(f, X1, 180, up + 180, "b°", d=25)
            bisect_lab(f, X2, 0, up, "a°", d=25)
            f.text(150, 104, "a = b", anchor="end", size=11, italic=True)
        else:
            bisect_lab(f, X1, up + 180, 360, "y°", d=25)
            bisect_lab(f, X2, 0, up, "x°", d=25)
            f.text(152, 104, "x + y = 180", anchor="end", size=11, italic=True)
        f.h += 16
        f.text(f.w / 2, f.h - 7, {"corr": "corresponding", "alt": "alternate", "coint": "cointerior"}[kind], size=11)
        panels.append(f)
    save_flat("rev_parallel", cat("rev_parallel", panels, gap=14))


def fig_rev_tri():
    # 6C: angle sum; exterior angle theorem; isosceles triangle (apex, base angles, base)
    f1 = CF(150, 110)
    P, Q, R = (40, 16), (56, 90), (140, 90)
    f1.poly([P, Q, R], color=None, opacity=0)
    f1.alab(P, Q, R, "a°", d=31).alab(Q, P, R, "b°", d=17).alab(R, P, Q, "c°", d=24)
    f2 = CF(170, 110)
    A, B, C = (34, 92), (104, 18), (148, 52)
    E = ext(C, A, 1.22)
    f2.seg(B, C).seg(C, E).seg(A, B)
    f2.alab(B, A, C, "x°", d=17).alab(C, A, B, "y°", d=18).alab(A, B, E, "z°", d=17)
    f2.angle(A, B, E, r=10)
    f3 = CF(170, 116)
    T, U, V = (66, 20), (30, 92), (102, 92)
    f3.poly([T, U, V], color=None, opacity=0)
    f3.tick(T, U, 2).tick(T, V, 2)
    f3.angle(U, T, V, r=11).angle(V, T, U, r=11)
    f3.text(66, 10, "apex", size=10.5)
    f3.text(66, 108, "base", size=10.5)
    f3.text(140, 58, "base angles", size=10.5)
    f3.line(122, 70, 94, 86, width=0.8)
    f3.line(116, 70, 40, 86, width=0.8)
    for pnl, cap in ((f1, "a + b + c = 180"), (f2, "Exterior angle  z = x + y"), (f3, "Isosceles")):
        pnl.h += 18
        pnl.text(pnl.w / 2, pnl.h - 8, cap, size=11.5, italic=(pnl is not f3))
    save_flat("rev_tri", cat("rev_tri", [f1, f2, f3], gap=18))


def fig_rev_quad():
    # 6D: angle sum of any quadrilateral (convex and non-convex); parallel sides give cointerior pairs
    f1 = CF(120, 104)
    A, B, C, D = (18, 44), (56, 10), (110, 58), (46, 98)
    f1.poly([A, B, C, D], color=None, opacity=0)
    for v, p, q, s in ((A, D, B, "a°"), (B, A, C, "b°"), (C, B, D, "c°"), (D, C, A, "d°")):
        falab(f1, v, p, q, s, d=23)
    f2 = CF(162, 118)
    A2, B2, C2, D2 = (40, 8), (64, 40), (150, 48), (14, 108)
    f2.poly([A2, B2, C2, D2], color=None, opacity=0)
    f2.reflex(B2, A2, C2, r=8)
    falab(f2, A2, D2, B2, "a°", d=26); falab(f2, B2, A2, C2, "b°", d=17, reflex=True)
    falab(f2, C2, B2, D2, "d°", d=42); falab(f2, D2, C2, A2, "c°", d=28)
    f3 = CF(150, 104)
    P, Q, R, S = (20, 30), (64, 10), (112, 46), (24, 86)
    f3.poly([P, Q, R, S], color=None, opacity=0)
    f3.parr(S, R, t=0.55).parr(P, Q, t=0.6)
    falab(f3, P, S, Q, "a°", d=20); falab(f3, S, R, P, "b°", d=21); falab(f3, R, Q, S, "c°", d=24); falab(f3, Q, P, R, "d°", d=20)
    for pnl, cap in ((f1, "a + b + c + d = 360"), (f2, "a + b + c + d = 360"), (f3, "a + b = 180,  c + d = 180")):
        pnl.h += 18
        pnl.text(pnl.w / 2, pnl.h - 8, cap, size=11.5, italic=True)
    save_flat("rev_quad", cat("rev_quad", [f1, f2, f3], gap=18))


def fig_rev_refl():
    # 8A: reflection in a mirror line (A, B, C and A', B', C')
    f = CF(200, 120)
    A, B, C = (84, 22), (84, 96), (34, 96)
    A2, B2, C2 = (116, 22), (116, 96), (166, 96)
    f.line(100, 6, 100, 114, dash="4 3", width=1.2)
    f.poly([A, B, C], color="blue", opacity=0.12)
    f.poly([A2, B2, C2], color="blue", opacity=0.05, stroke="faint")
    f.line(84, 22, 116, 22, width=0.9, dash="2 2").line(84, 96, 116, 96, width=0.9, dash="2 2")
    f.right((100, 22), (92, 22), (100, 14), s=6).right((100, 96), (92, 96), (100, 88), s=6)
    f.lab(A, "A", dx=-8, dy=-6).lab(B, "B", dx=-8, dy=12).lab(C, "C", dx=-8, dy=8)
    f.lab(A2, "A′", dx=10, dy=-6).lab(B2, "B′", dx=10, dy=12).lab(C2, "C′", dx=8, dy=10)
    save("rev_refl", f)


def fig_rev_rot():
    # 8C: rotation of 90 degrees anticlockwise about C (X, Y, Z to X', Y', Z'), arcs on circles about C
    f = CF(240, 210)
    Cc = (120, 112)
    k = 1.5
    pts = {"X": (8, 16), "Z": (8, 38), "Y": (58, 18)}
    P = {n: (Cc[0] + k * x, Cc[1] - k * y) for n, (x, y) in pts.items()}
    P2 = {n + "′": (Cc[0] - k * y, Cc[1] - k * x) for n, (x, y) in pts.items()}
    for n in ("X", "Z", "Y"):
        r = hypot(*pts[n]) * k
        f.circle(Cc, r, color="rose", width=0.9, dash="3 3")
    f.poly([P["X"], P["Y"], P["Z"]], color="blue", opacity=0.12)
    f.poly([P2["X′"], P2["Y′"], P2["Z′"]], color="blue", opacity=0.05, stroke="faint")
    f.dot(*Cc, r=2.2)
    f.lab(Cc, "C", dx=8, dy=10)
    f.lab(P["X"], "X", dx=-9, dy=6).lab(P["Z"], "Z", dx=-4, dy=-10).lab(P["Y"], "Y", dx=11, dy=4)
    f.lab(P2["X′"], "X′", dx=4, dy=13).lab(P2["Z′"], "Z′", dx=-12, dy=8).lab(P2["Y′"], "Y′", dx=-6, dy=-10)
    save("rev_rot", f)


# ---- warm-up figures (drawn to scale from the given angles, laid out as in the book) ----

def fig_w1():
    # 6A Q4 c, d, g
    v = (62, 52)
    f = rays_fig(124, 104, v, (78.3, 26.3, 258.3, 206.3), [(26.3, 78.3, "52°"), (258.3, 386.3, "a°"), (206.3, 258.3, "b°")], L=50, d=26)
    save("w1c", f)
    v = (62, 52)
    f = rays_fig(124, 104, v, (123.3, 303.3, 157.3, 337.3), [(337.3, 483.3, "146°"), (123.3, 157.3, "a°"), (157.3, 303.3, "b°")], L=62, d=42)
    save("w1d", f)
    v = (62, 56)
    f = rays_fig(124, 104, v, (97.9, 217.9, 337.9), [(337.9, 457.9, "120°"), (97.9, 217.9, "a°"), (217.9, 337.9, "120°")], L=48, d=20)
    save("w1g", f)


def fig_w2():
    # 6B Q4 a: transversal and two parallel lines (110 degrees given)
    f = CF(150, 130)
    up = 101.6
    par = 31.6
    X1, X2 = (70, 42), (80, 92)

    def tline(X):
        return polar(X, par + 180, 62), polar(X, par, 70)
    # make X2 lie on the transversal through X1
    X2 = polar(X1, up + 180, 51)
    a1, b1 = tline(X1)
    a2, b2 = tline(X2)
    f.seg(a1, b1).seg(a2, b2).parr(a1, b1, t=0.85).parr(a2, b2, t=0.85)
    f.seg(polar(X1, up, 34), polar(X2, up + 180, 30))
    bisect_lab(f, X1, up, par + 180, "110°", d=22)
    bisect_lab(f, X2, up, par + 180, "a°", d=17)
    bisect_lab(f, X2, par + 180, up + 180, "b°", d=17)
    save("w2a", f)
    # 6B Q4 c: two parallel lines (arrows up) cut by a transversal; 74 degrees given
    f = CF(170, 110)
    tr = -3.4
    pu = 102.6
    X1 = (52, 52)
    X2 = polar(X1, tr, 64)
    for X in (X1, X2):
        lo, hi = polar(X, pu + 180, 46), polar(X, pu, 46)
        f.seg(lo, hi).parr(lo, hi, t=0.8)
    f.seg(polar(X1, tr + 180, 40), polar(X2, tr, 44))
    bisect_lab(f, X1, tr, pu, "b°", d=17)
    bisect_lab(f, X1, pu + 180, tr + 360, "a°", d=17)
    bisect_lab(f, X1, tr + 180, pu + 180, "c°", d=17)
    bisect_lab(f, X2, pu, tr + 180, "74°", d=20)
    save("w2c", f)


def fig_w3():
    # 6C Q5 a, b, c (isosceles, to scale)
    f = CF(110, 120)
    U, V = (14, 104), (90, 104)
    T = (52, 104 - 38 * tan_(68))
    f.poly([T, U, V], color=None, opacity=0)
    f.tick(T, U, 2).tick(T, V, 2)
    f.alab(U, T, V, "a°", d=17).alab(V, T, U, "68°", d=21)
    save("w3a", f)
    f = CF(170, 110)
    Bm = (110, 96)
    L = polar(Bm, 168.9, 88)
    R = polar(Bm, 168.9 - 106, 88)
    f.poly([L, Bm, R], color=None, opacity=0)
    f.tick(L, Bm, 2).tick(Bm, R, 2)
    f.alab(L, Bm, R, "37°", d=30).alab(Bm, L, R, "a°", d=17)
    save("w3b", f)
    f = CF(230, 96)
    V1, V2 = (14, 82), (14, 14)
    Ap = (14 + 34 / tan_(10), 48)
    f.poly([V2, V1, Ap], color=None, opacity=0)
    f.tick(V2, Ap, 2).tick(V1, Ap, 2)
    f.alab(V1, V2, Ap, "80°", d=21).alab(Ap, V1, V2, "a°", d=62)
    save("w3c", f)


def tan_(deg):
    from math import tan
    return tan(radians(deg))


def quad_angles(P):
    """Interior angles (degrees) of the simple polygon P (any orientation), reflex angles included."""
    n = len(P)
    area = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2
    out = []
    for i in range(n):
        a, v, b = P[i - 1], P[i], P[(i + 1) % n]
        t = (degrees(atan2(a[1] - v[1], a[0] - v[0])) - degrees(atan2(b[1] - v[1], b[0] - v[0]))) % 360
        out.append(t if area > 0 else 360 - t)
    return out


def fig_w4():
    # 6D Q4 a, d, e (to scale)
    f = CF(140, 90)
    BL, BR = (14, 74), (124, 74)
    h = 58
    TL = (BL[0] + h / tan_(70), BL[1] - h)
    TR = (BR[0], BR[1] - h)
    f.poly([TL, TR, BR, BL], color=None, opacity=0)
    f.right(TR, TL, BR, s=7)
    f.alab(TL, BL, TR, "110°", d=20).alab(BL, TL, BR, "70°", d=20).alab(BR, TR, BL, "a°", d=16)
    save("w4a", f)
    # d: 80 (top left), 35 (right), 75 (bottom), a = 170 (left); the book's layout, angles to scale
    f = CF(150, 120)
    P = quad_from([(14, 30), None, None, None], (80, 35, 75, 170), first_dir=8, L01=150, L03=40)
    P = to_frame(P)
    f = CF(max(p[0] for p in P) + 16, max(p[1] for p in P) + 16)
    f.poly(P, color=None, opacity=0)
    V80, V35, V75, Va = P
    falab(f, V80, V35, Va, "80°", d=19); falab(f, V35, V80, V75, "35°", d=36)
    falab(f, V75, V35, Va, "75°", d=30); falab(f, Va, V80, V75, "a°", d=18)
    save("w4d", f)
    # e: a (top left), 37 (right), 23 (bottom), reflex 230 (the dent)
    f = CF(110, 116)
    P = quad_from([(14, 12), None, None, None], (70, 37, 23, 230), first_dir=-10.5, L01=130, L03=40)
    P = to_frame(P)
    Vaa, V37, V23, Vr = P
    f = CF(max(p[0] for p in P) + 30, max(p[1] for p in P) + 16)
    f.poly(P, color=None, opacity=0)
    f.reflex(Vr, Vaa, V23, r=9)
    falab(f, Vaa, V37, Vr, "a°", d=18); falab(f, V37, Vaa, V23, "37°", d=32)
    falab(f, V23, V37, Vr, "23°", d=68); falab(f, Vr, Vaa, V23, "230°", d=24)
    save("w4e", f)


def to_frame(P, pad=14):
    """Translate the points so that the smallest x and y are both pad."""
    mx, my = min(p[0] for p in P), min(p[1] for p in P)
    return [(p[0] - mx + pad, p[1] - my + pad) for p in P]


def quad_from(P, angs, first_dir, L01, L03):
    """Quadrilateral P0 P1 P2 P3 (page coordinates) with interior angles angs at P0..P3 (one may be reflex):
    P1 is L01 from P0 in direction first_dir, P3 is L03 from P0, and P2 closes the shape."""
    P0 = P[0]
    for sgn in (1, -1):
        P1 = polar(P0, first_dir, L01)
        P3 = polar(P0, first_dir - sgn * angs[0], L03)
        try:
            P2 = _isect((P1, _ang(P1, P0) + sgn * angs[1]), (P3, _ang(P3, P0) - sgn * angs[3]))
        except ZeroDivisionError:
            continue
        Q = [P0, P1, P2, P3]
        got = quad_angles(Q)
        if all(abs(g - a) < 1e-6 for g, a in zip(got, angs)):
            return Q
    raise ValueError("no quadrilateral with these angles")


def _isect(r1, r2):
    """Intersection of two rays given as (point, direction in degrees, page convention)."""
    (p, a), (q, b) = r1, r2
    d1 = (cos(radians(a)), -sin(radians(a)))
    d2 = (cos(radians(b)), -sin(radians(b)))
    den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((q[0] - p[0]) * d2[1] - (q[1] - p[1]) * d2[0]) / den
    return (p[0] + t * d1[0], p[1] + t * d1[1])


def fig_w6():
    # 8C Q7: triangle A(-4, 4), B(-4, 1), C(-1, 1) on a grid from -5 to 5
    u = 17
    f = CF(11 * u + 30, 11 * u + 24)
    G = lambda p: (16 + (p[0] + 5.5) * u, 12 + (5.5 - p[1]) * u)
    grid(f, G, range(-5, 6), range(-5, 6))
    axes(f, G, (-5.5, 5.6), (-5.5, 5.6), size=9)
    A, B, C = G((-4, 4)), G((-4, 1)), G((-1, 1))
    f.poly([A, B, C], color=None, opacity=0, stroke="rose", width=1.6)
    for p in (A, B, C):
        f.dot(*p, r=2.2, color="blue")
    mtext(f, A[0] - 10, A[1] - 2, "A", size=11.5, italic=True)
    mtext(f, B[0] - 10, B[1] - 8, "B", size=11.5, italic=True)
    mtext(f, C[0] - 4, C[1] + 11, "C", size=11.5, italic=True)
    save("w6", f)


if __name__ == "__main__":
    fig_rev_angles()
    fig_rev_marks()
    fig_rev_parallel()
    fig_rev_tri()
    fig_rev_quad()
    fig_rev_refl()
    fig_rev_rot()
    fig_w1()
    fig_w2()
    fig_w3()
    fig_w4()
    fig_w6()
