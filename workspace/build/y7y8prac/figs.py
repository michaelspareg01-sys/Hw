"""Figures for the Year 7-8 Angles and Measurement practice pack.

Run: python3 workspace/build/y7y8prac/figs.py   (writes svg/*.svg)

Every diagram recreates a textbook diagram (ICE-EM Mathematics 7 3rd ed, Cambridge Maths NSW
Year 8 2nd ed). Points are placed in model coordinates (x right, y up); angles are drawn at
their true size wherever the data allow, so the pictures are faithful as well as tidy.
"""
import os, sys
from math import sin, cos, tan, atan, atan2, pi, sqrt, radians, degrees
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt  # noqa: F401  (house header)

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)
BLUE = "#2b4aa0"          # textbook-style line colour
FILL = "#a9bde0"
ZOOM = 1.0                # printed size factor
TS = 1.12                 # text size factor for all labels
GS = 0.9                  # geometry scale factor for all diagrams


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(g.svg())


def pol(p, r, a):
    """Point at distance r from p in direction a degrees (anticlockwise from +x)."""
    return (p[0] + r * cos(radians(a)), p[1] + r * sin(radians(a)))


def dirn(p, q):
    return degrees(atan2(q[1] - p[1], q[0] - p[0]))


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def meet(p1, a1, p2, a2):
    """Intersection of the line through p1 at angle a1 with the line through p2 at angle a2."""
    d1 = (cos(radians(a1)), sin(radians(a1)))
    d2 = (cos(radians(a2)), sin(radians(a2)))
    den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Geo:
    """Geometry diagram in model units (y up). s = pixels per unit."""

    def __init__(self, s=40, pad=4):
        self.s, self.pad = s * GS, pad
        self.items = []          # (kind, data)
        self.P = {}
        self.ext = []            # model-space points for the bounding box
        self.tbox = []           # pixel boxes for text: (cx, cy, w, h) in model coords + px
        self.angles = []         # (label, drawn size in degrees) for every labelled angle

    # ---------- points
    def pt(self, name, p):
        self.P[name] = p
        return p

    def _p(self, a):
        return self.P[a] if isinstance(a, str) else a

    # ---------- primitives
    def seg(self, a, b, color=BLUE, width=1.3, dash=None, e0=0, e1=0):
        p, q = self._p(a), self._p(b)
        d = dirn(p, q)
        p2, q2 = pol(p, -e0, d), pol(q, e1, d)
        self.items.append(("line", (p2, q2, color, width, dash)))
        self.ext += [p2, q2]
        return self

    def ray(self, a, ang, length, **kw):
        p = self._p(a)
        return self.seg(p, pol(p, length, ang), **kw)

    def poly(self, pts, fill=None, color=BLUE, width=1.3, opacity=1.0, closed=True, dash=None):
        pts = [self._p(x) for x in pts]
        self.items.append(("poly", (pts, fill, color, width, opacity, closed, dash)))
        self.ext += pts
        return self

    def circle(self, c, r, color=BLUE, width=1.3, fill="none"):
        c = self._p(c)
        self.items.append(("circle", (c, r, color, width, fill)))
        self.ext += [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)]
        return self

    def dot(self, a, r=2.2, color=BLUE):
        self.items.append(("dot", (self._p(a), r, color)))
        return self

    def text(self, p, s, size=11.5, italic=False, anchor="middle", color=INK, dx=0, dy=0):
        """Text centred (vertically) at model point p, shifted by (dx, dy) pixels (dy down)."""
        p = self._p(p)
        size = size * TS
        self.items.append(("text", (p, s, size, italic, anchor, color, dx, dy)))
        w = len(s) * size * 0.56
        cx = {"middle": 0, "start": w / 2, "end": -w / 2}[anchor] + dx
        self.tbox.append((p, cx, dy, w, size * 1.05))
        return self

    def lab(self, a, s, ang, dist=11, size=11.5, italic=True):
        """Point label placed dist pixels from point a in direction ang (degrees)."""
        p = self._p(a)
        dx, dy = dist * cos(radians(ang)), -dist * sin(radians(ang))
        return self.text(p, s, size=size, italic=italic, dx=dx, dy=dy)

    def ang(self, v, a, b, s="", r=16, lr=None, arc=True, size=10.5, color=BLUE, reflex=False,
            ldx=0, ldy=0, double=False, italic=False):
        """Angle at v between rays v->a and v->b (the non-reflex one unless reflex=True).
        a, b may be points or directions in degrees."""
        v = self._p(v)
        da = a if isinstance(a, (int, float)) else dirn(v, self._p(a))
        db = b if isinstance(b, (int, float)) else dirn(v, self._p(b))
        span = (db - da) % 360
        if (span > 180) != reflex:
            da, db = db, da
            span = 360 - span
        if s:
            self.angles.append((s, span, v, da, da + span))
        if arc:
            self.items.append(("arc", (v, r, da, span, color)))
            self.ext += [pol(v, (r + 2) / self.s, da + span * k / 12) for k in range(13)]
            if double:
                self.items.append(("arc", (v, r + 3, da, span, color)))
        if s:
            mid = da + span / 2
            lr = lr if lr is not None else r + 11
            self.text(v, s, size=size, italic=italic, dx=lr * cos(radians(mid)) + ldx,
                      dy=-lr * sin(radians(mid)) + ldy)
        return self

    def angtxt(self, v, a, b, s, lr=20, size=10.5, ldx=0, ldy=0, reflex=False, italic=False):
        return self.ang(v, a, b, s, lr=lr, arc=False, size=size, ldx=ldx, ldy=ldy, reflex=reflex,
                        italic=italic)

    def right(self, v, a, b, sz=7, color=BLUE):
        v = self._p(v)
        da = a if isinstance(a, (int, float)) else dirn(v, self._p(a))
        db = b if isinstance(b, (int, float)) else dirn(v, self._p(b))
        self.items.append(("right", (v, da, db, sz, color)))
        return self

    def arr(self, a, b, n=1, t=0.5, color=BLUE, size=6.5):
        """n parallel-line arrowheads on segment a->b, pointing towards b, centred at fraction t."""
        p, q = self._p(a), self._p(b)
        self.items.append(("arr", (p, q, n, t, color, size)))
        return self

    def tick(self, a, b, n=1, t=0.5, color=BLUE, size=5):
        p, q = self._p(a), self._p(b)
        self.items.append(("tick", (p, q, n, t, color, size)))
        return self

    def dim(self, a, b, color=BLUE, off=0, head=5):
        """Double-headed dimension arrow from a to b, offset off pixels to the left of a->b."""
        p, q = self._p(a), self._p(b)
        self.items.append(("dim", (p, q, color, off, head)))
        self.ext += [p, q]
        return self

    # ---------- rendering
    def svg(self):
        s = self.s
        xs = [p[0] * s for p in self.ext] or [0]
        ys = [-p[1] * s for p in self.ext] or [0]
        for p, cx, cy, w, h in self.tbox:
            X, Y = p[0] * s + cx, -p[1] * s + cy
            xs += [X - w / 2, X + w / 2]
            ys += [Y - h / 2, Y + h / 2]
        x0, x1 = min(xs) - self.pad, max(xs) + self.pad
        y0, y1 = min(ys) - self.pad, max(ys) + self.pad

        def X(p):
            return p[0] * s - x0

        def Y(p):
            return -p[1] * s - y0
        out = []
        for kind, d in self.items:
            if kind == "line":
                p, q, c, w, dash = d
                ds = f' stroke-dasharray="{dash}"' if dash else ''
                out.append(f'<line x1="{X(p):.1f}" y1="{Y(p):.1f}" x2="{X(q):.1f}" y2="{Y(q):.1f}" '
                           f'stroke="{c}" stroke-width="{w}"{ds} stroke-linecap="round"/>')
            elif kind == "poly":
                pts, fill, c, w, op, closed, dash = d
                pp = " ".join(f"{X(p):.1f},{Y(p):.1f}" for p in pts)
                tag = "polygon" if closed else "polyline"
                f = fill or "none"
                ds = f' stroke-dasharray="{dash}"' if dash else ''
                out.append(f'<{tag} points="{pp}" fill="{f}" fill-opacity="{op}" stroke="{c}" '
                           f'stroke-width="{w}"{ds} stroke-linejoin="round"/>')
            elif kind == "circle":
                c, r, col, w, fill = d
                out.append(f'<circle cx="{X(c):.1f}" cy="{Y(c):.1f}" r="{r * s:.1f}" fill="{fill}" '
                           f'stroke="{col}" stroke-width="{w}"/>')
            elif kind == "dot":
                p, r, c = d
                out.append(f'<circle cx="{X(p):.1f}" cy="{Y(p):.1f}" r="{r}" fill="{c}"/>')
            elif kind == "text":
                p, t, size, it, anchor, c, dx, dy = d
                st = ' font-style="italic"' if it else ''
                out.append(f'<text x="{X(p) + dx:.1f}" y="{Y(p) + dy + size * 0.36:.1f}" '
                           f'text-anchor="{anchor}" font-size="{size}" fill="{c}"{st}>{esc(t)}</text>')
            elif kind == "arc":
                v, r, da, span, c = d
                cx, cy = X(v), Y(v)
                x0a, y0a = cx + r * cos(radians(da)), cy - r * sin(radians(da))
                x1a, y1a = cx + r * cos(radians(da + span)), cy - r * sin(radians(da + span))
                large = 1 if span > 180 else 0
                out.append(f'<path d="M{x0a:.1f},{y0a:.1f} A{r},{r} 0 {large} 0 {x1a:.1f},{y1a:.1f}" '
                           f'fill="none" stroke="{c}" stroke-width="1"/>')
            elif kind == "right":
                v, da, db, sz, c = d
                cx, cy = X(v), Y(v)
                ax, ay = sz * cos(radians(da)), -sz * sin(radians(da))
                bx, by = sz * cos(radians(db)), -sz * sin(radians(db))
                out.append(f'<path d="M{cx + ax:.1f},{cy + ay:.1f} L{cx + ax + bx:.1f},{cy + ay + by:.1f} '
                           f'L{cx + bx:.1f},{cy + by:.1f}" fill="none" stroke="{c}" stroke-width="1"/>')
            elif kind == "arr":
                p, q, n, t, c, size = d
                a = atan2(-(q[1] - p[1]), q[0] - p[0])
                m = lerp(p, q, t)
                mx, my = X(m), Y(m)
                for k in range(n):
                    off = (k - (n - 1) / 2) * 4.5
                    tx, ty = mx + (off + size / 2) * cos(a), my + (off + size / 2) * sin(a)
                    p1 = (tx - size * cos(a - 0.45), ty - size * sin(a - 0.45))
                    p2 = (tx - size * cos(a + 0.45), ty - size * sin(a + 0.45))
                    out.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{tx:.1f},{ty:.1f} L{p2[0]:.1f},{p2[1]:.1f}" '
                               f'fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="round"/>')
            elif kind == "tick":
                p, q, n, t, c, size = d
                a = atan2(-(q[1] - p[1]), q[0] - p[0])
                m = lerp(p, q, t)
                mx, my = X(m), Y(m)
                nx, ny = -sin(a), cos(a)
                for k in range(n):
                    off = (k - (n - 1) / 2) * 3.2
                    cx, cy = mx + off * cos(a), my + off * sin(a)
                    out.append(f'<line x1="{cx - size * nx:.1f}" y1="{cy - size * ny:.1f}" x2="{cx + size * nx:.1f}" '
                               f'y2="{cy + size * ny:.1f}" stroke="{c}" stroke-width="1.1"/>')
            elif kind == "dim":
                p, q, c, off, head = d
                a = atan2(-(q[1] - p[1]), q[0] - p[0])
                nx, ny = sin(a) * off, -cos(a) * off
                u1, v1, u2, v2 = X(p) + nx, Y(p) + ny, X(q) + nx, Y(q) + ny
                out.append(f'<line x1="{u1:.1f}" y1="{v1:.1f}" x2="{u2:.1f}" y2="{v2:.1f}" stroke="{c}" stroke-width="0.9"/>')
                for (hx, hy, aa) in ((u2, v2, a), (u1, v1, a + pi)):
                    p1 = (hx - head * cos(aa - 0.45), hy - head * sin(aa - 0.45))
                    p2 = (hx - head * cos(aa + 0.45), hy - head * sin(aa + 0.45))
                    out.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{hx:.1f},{hy:.1f} L{p2[0]:.1f},{p2[1]:.1f}" '
                               f'fill="none" stroke="{c}" stroke-width="0.9"/>')
        w, h = x1 - x0, y1 - y0
        z = ZOOM
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w * z:.1f}" '
                f'height="{h * z:.1f}" font-family="Inter, Arial, sans-serif">' + "".join(out) + "</svg>")


def line_through(g, p, ang, back, fwd, **kw):
    """Draw the line through p at angle ang, from distance back behind p to fwd ahead."""
    return g.seg(pol(p, -back, ang), pol(p, fwd, ang), **kw)


# =====================================================================================
FIGS = {}


def fig(fn):
    FIGS[fn.__name__] = fn
    return fn


# ------------------------------------------------------------------ A1 notation
@fig
def a1_concurrent():                     # Y7 Ex 6A Q3
    g = Geo(46)
    X = (0, 0); A = pol(X, 2.3, -100)
    B = meet(A, 30, X, -60); C = meet(A, 30, X, -10)
    line_through(g, X, 30, 1.4, 2.8)                 # XY
    line_through(g, A, 30, 1.2, 3.6)                 # line AC
    line_through(g, X, -10, 1.4, 3.6)                # through C
    line_through(g, X, -60, 1.4, 3.3)                # through B
    line_through(g, X, -100, 1.9, 2.9)               # through A
    g.arr(X, pol(X, 2.8, 30), t=0.5).arr(pol(A, -1.2, 30), pol(A, 3.6, 30), t=0.66)
    g.lab(X, "X", 140, 15).lab(pol(X, 2.8, 30), "Y", 75, 10)
    g.lab(A, "A", 205, 12).lab(B, "B", -20, 13).lab(C, "C", -35, 13)
    return g


@fig
def a1_fivelines():                      # Y7 Ex 6B Q2
    g = Geo(50)
    O = (0, 0); P = (-2.1, -2.35)
    dl, dv, dr = -116, -90, -61
    A = meet(P, 15, O, dl); B = meet(P, 15, O, dv); C = meet(P, 15, O, dr)
    K = meet(P, -11, O, dl); L = meet(P, -11, O, dv); M = meet(P, -11, O, dr)
    g.ray(O, dl, 3.4).ray(O, dv, 3.3).seg(O, M, e1=0.05)
    g.seg(P, C, e1=1.2).seg(P, M, e1=0.05)
    g.lab(O, "O", 90, 11).lab(P, "P", 185, 11).lab(A, "A", 140, 13).lab(B, "B", 215, 12)
    g.lab(C, "C", 40, 13).lab(K, "K", 225, 13).lab(L, "L", -40, 13).lab(M, "M", -15, 13)
    return g


@fig
def a1_quad():                           # Y7 Ex 6B Q7a
    g = Geo(46)
    A, B, C, D = (1.3, 3.0), (3.6, 2.7), (2.4, 0), (0, 1.0)
    g.poly([A, B, C, D]).seg(D, B)
    g.lab(A, "A", 100, 10).lab(B, "B", 10, 11).lab(C, "C", -90, 11).lab(D, "D", 190, 11)
    return g


@fig
def a1_tetra():                          # Y7 Ex 6B Q7b
    g = Geo(46)
    A, B, C, D = (1.8, 3.3), (0, 0.85), (1.8, 0), (3.5, 2.0)
    g.poly([B, C, D], fill=FILL, color=BLUE, opacity=0.9)
    g.seg(A, B).seg(A, C).seg(A, D).seg(B, D, color=ACC["rose"], dash="3 2", width=1.1)
    g.lab(A, "A", 90, 10).lab(B, "B", 190, 11).lab(C, "C", -90, 11).lab(D, "D", 15, 11)
    return g


@fig
def a1_perp():                           # Y8 Ex 6A Q5
    g = Geo(50)
    O = (0, 0)
    for nm, d, ln in (("A", 32, 2.1), ("D", 212, 2.1), ("B", 68, 1.95), ("E", 248, 1.95), ("C", 122, 1.75)):
        g.ray(O, d, ln, width=1.5)
        g.lab(pol(O, ln, d), nm, d, 11, size=12)
    g.right(O, 122, 212, 8)
    g.lab(O, "O", -20, 13, size=12)
    return g


# ------------------------------------------------------------------ A2 measuring and classifying
def _cls(name, d0, d1, kind):
    g = Geo(40)
    V = (0, 0)
    g.ray(V, d0, 1.6).ray(V, d1, 1.6)
    if kind == "right":
        g.right(V, d0, d1, 6)
    else:
        g.ang(V, d0, d1, r=12 if kind != "reflex" else 10, reflex=(kind == "reflex"))
    return g


@fig
def a2_cls_a():
    return _cls("a", 0, 32, "acute")


@fig
def a2_cls_b():
    return _cls("b", 0, 128, "obtuse")


@fig
def a2_cls_c():
    g = Geo(40)
    V = (0, 0)
    g.ray(V, 52, 1.8).ray(V, 110, 1.8)
    g.ang(V, 52, 110, r=17, reflex=True)          # the book draws the reflex angle as a large circle round the vertex
    return g


@fig
def a2_cls_d():
    return _cls("d", 0, 90, "right")


@fig
def a2_rev4():                           # Y7 Ch 6 Review Q4
    g = Geo(48)
    O = (0, 0)
    g.ray(O, 0, 3.0).ray(O, 90, 2.9).ray(O, 58, 2.6)
    g.right(O, 0, 90, 7)
    g.angtxt(O, 58, 90, "32°", lr=40, ldx=3)
    g.lab((3.0, 0), "A", 0, 9).lab((0, 2.9), "B", 90, 10).lab(pol(O, 2.6, 58), "C", 70, 10).lab(O, "O", -90, 12)
    return g


# ------------------------------------------------------------------ A3 angles at a point
@fig
def a3_5e():                             # Y7 Ex 6D Q5e
    g = Geo(48)
    O = (0, 0)
    g.seg((-1.8, 0), (1.6, 0)).ray(O, 150, 1.85).ray(O, 50, 1.9)
    g.angtxt(O, 150, 180, "30°", lr=34, ldy=-1).angtxt(O, 50, 150, "100°", lr=19)
    g.lab((-1.8, 0), "X", -90, 10).lab(O, "O", -90, 11).lab((1.6, 0), "B", -90, 10)
    g.lab(pol(O, 1.85, 150), "Y", 120, 9).lab(pol(O, 1.9, 50), "A", 60, 9)
    return g


@fig
def a3_5k():                             # Y7 Ex 6D Q5k
    g = Geo(46)
    O = (0, 0)
    g.seg((-2.1, 0), (2.6, 0))
    for nm, d, ln in (("A", 150, 2.1), ("N", 100, 2.2), ("M", 60, 2.3), ("L", 30, 2.4), ("K", 10, 2.6)):
        g.ray(O, d, ln)
        g.lab(pol(O, ln, d), nm, d, 9)
    for (d0, d1, s, lr) in ((100, 150, "50°", 30), (60, 100, "40°", 32), (30, 60, "30°", 42),
                            (10, 30, "20°", 58), (0, 10, "10°", 80)):
        g.angtxt(O, d0, d1, s, lr=lr)
    g.lab((-2.1, 0), "B", -90, 10).lab(O, "O", -90, 11).lab((2.6, 0), "J", -90, 10)
    return g


@fig
def a3_5l():                             # Y7 Ex 6D Q5l
    g = Geo(46)
    O = (0, 0)
    rays = (("B", 120), ("C", 40), ("D", -30), ("E", -90), ("F", -140), ("G", 180), ("A", 150))
    for nm, d in rays:
        ln = 2.3 if nm in "CF" else 1.8
        g.ray(O, d, ln)
        g.lab(pol(O, ln, d), nm, d, 10)
    for (d0, d1, s) in ((40, 120, "80°"), (-30, 40, "70°"), (-90, -30, "60°"), (-140, -90, "50°"),
                        (180, 220, "40°"), (150, 180, "30°")):
        g.angtxt(O, d0, d1, s, lr=30)
    g.lab(O, "O", 75, 10)
    return g


@fig
def a3_7g():                             # Y7 Ex 6D Q7g
    g = Geo(50)
    W = (0, 0)
    g.seg((0, 1.7), (0, -1.7)); line_through(g, W, 40, 1.9, 1.6); g.ray(W, -10, 1.7)
    g.lab((0, 1.7), "U", 175, 10).lab((0, -1.7), "D", 185, 10).lab(pol(W, 1.6, 40), "R", 45, 9)
    g.lab(pol(W, -1.9, 40), "L", 220, 9).lab(pol(W, 1.7, -10), "T", -10, 9).lab(W, "W", 245, 15)
    g.angtxt(W, 90, 220, "130°", lr=34).angtxt(W, 40, 90, "β", lr=18, size=12)
    g.angtxt(W, -10, 40, "α", lr=25, size=12).angtxt(W, 270, 350, "80°", lr=28)
    return g


@fig
def a3_7h():                             # Y7 Ex 6D Q7h
    g = Geo(52)
    M = (0, 0); D = (2.2, 0); B = (-1.6, 0); X = (3.9, 0)
    A = meet(M, 110, D, 140); C = meet(M, -70, D, 210); Y = pol(D, 1.7, 30)
    g.seg(B, X).seg(A, C).seg(A, D).seg(C, Y).seg(B, A).seg(B, C)
    g.lab(A, "A", 95, 10).lab(B, "B", 180, 10).lab(C, "C", -90, 11).lab(M, "M", 225, 12)
    g.lab(D, "D", -60, 12).lab(X, "X", 0, 9).lab(Y, "Y", 30, 9)
    g.angtxt(M, 110, 180, "α", lr=17, size=12).angtxt(M, 0, 110, "β", lr=17, size=12, ldx=3)
    g.angtxt(M, -70, 0, "70°", lr=22).angtxt(D, 140, 180, "40°", lr=28)
    g.angtxt(D, 30, 140, "θ", lr=15, size=12).angtxt(D, 0, 30, "γ", lr=30, size=12)
    g.angtxt(D, -150, 0, "150°", lr=34, ldy=4)
    return g


@fig
def a3_8c():                             # Y7 Ex 6D Q8c
    g = Geo(50)
    V = (0, 0)
    g.seg((-2.0, 0), (2.4, 0)); line_through(g, V, 40, 1.6, 2.0); g.ray(V, 20, 2.15)
    g.lab((-2.0, 0), "D", -90, 10).lab((2.4, 0), "C", -90, 10).lab(V, "V", -90, 12)
    g.lab(pol(V, 2.0, 40), "A", 40, 9).lab(pol(V, -1.6, 40), "B", 220, 9).lab(pol(V, 2.15, 20), "M", 20, 10)
    g.angtxt(V, 180, 220, "40°", lr=34).angtxt(V, 20, 40, "θ", lr=46, size=12).angtxt(V, 0, 20, "θ", lr=58, size=12)
    return g


@fig
def a3_8g():                             # Y7 Ex 6D Q8g
    g = Geo(50)
    F = (0, 0)
    g.seg((-1.7, 0), (2.0, 0)); line_through(g, F, 60, 1.9, 1.75); g.ray(F, 270, 1.7)
    g.lab((-1.7, 0), "E", -90, 10).lab((2.0, 0), "G", -90, 10).lab(pol(F, 1.75, 60), "M", 30, 9)
    g.lab(pol(F, -1.9, 60), "N", 200, 9).lab((0, -1.7), "P", 0, 9)
    g.angtxt(F, 60, 180, "θ", lr=16, size=12, ldx=-4).angtxt(F, 0, 60, "60°", lr=24)
    g.angtxt(F, 270, 360, "3γ", lr=20, size=11.5).angtxt(F, 240, 270, "γ", lr=34, size=12)
    return g


@fig
def a3_8h():                             # Y7 Ex 6D Q8h
    g = Geo(50)
    K = (0, 0)
    g.seg((-2.1, 0), (2.6, 0)).ray(K, 65, 1.6)
    g.lab((-2.1, 0), "J", -90, 10).lab(K, "K", -90, 11).lab((2.6, 0), "L", -90, 10).lab(pol(K, 1.6, 65), "D", 30, 9)
    g.angtxt(K, 65, 180, "α + 50", lr=34, ldy=-4).angtxt(K, 0, 65, "α", lr=22, size=12)
    return g


@fig
def a3_y13():                            # Y8 Ex 6A Q13 (not drawn to scale)
    g = Geo(50)
    O = (0, 0)
    line_through(g, O, 35, 1.6, 1.7); g.ray(O, 84, 1.9)
    g.angtxt(O, 84, 215, "(a − 90)°", lr=34, ldx=-12, ldy=-4, italic=True).angtxt(O, 35, 84, "(a + 50)°", lr=64, ldx=28, ldy=-8, italic=True)
    return g


@fig
def a3_y14e():                           # Y8 Ex 6A Q14e
    g = Geo(62)
    O = (0, 0)
    for d, ln in ((92, 1.25), (122, 1.3), (62, 1.3), (212, 1.8), (-28, 2.1)):
        g.ray(O, d, ln)
    g.angtxt(O, 92, 122, "a°", lr=36, italic=True, ldx=-2).angtxt(O, 62, 92, "a°", lr=36, italic=True, ldx=2)
    g.angtxt(O, 122, 212, "(3a)°", lr=28, ldx=-6, italic=True).angtxt(O, -28, 62, "(3a)°", lr=28, ldx=6, italic=True)
    g.angtxt(O, 212, 332, "(4a)°", lr=20, italic=True)
    return g


@fig
def a3_y14f():                           # Y8 Ex 6A Q14f
    g = Geo(48)
    O = (0, 0)
    g.seg((0, 1.7), (0, -2.3)); line_through(g, O, 50, 2.4, 1.8)
    g.angtxt(O, 270, 410, "(7a + 21)°", lr=40, ldx=16, italic=True)
    g.angtxt(O, 230, 270, "(3a − 11)°", lr=92, ldx=-4, italic=True)
    return g


# ------------------------------------------------------------------ A4 transversals and parallel lines
@fig
def a4_y2():                             # Y8 Ex 6B Q2
    g = Geo(50)
    B = (0, 0); C = (1.15, 0.6)
    g.seg((0, 1.5), (0, -1.3)).seg((1.15, 1.5), (1.15, -1.3)).seg(pol(B, -1.3, dirn(B, C)), pol(C, 1.3, dirn(B, C)))
    g.lab((0, 1.5), "F", 90, 9, size=12).lab((1.15, 1.5), "H", 90, 9, size=12).lab((0, -1.3), "E", -90, 10, size=12)
    g.lab((1.15, -1.3), "G", -90, 10, size=12).lab(pol(C, 1.3, dirn(B, C)), "D", 20, 10, size=12)
    g.lab(pol(B, -1.3, dirn(B, C)), "A", 200, 10, size=12).lab(B, "B", 150, 13, size=12).lab(C, "C", 150, 13, size=12)
    return g


@fig
def a4_7d():                             # Y7 Ex 6E Q7d
    g = Geo(46)
    T = (0, 0); S = pol(T, 4.1, 52); R = pol(S, -3.3, 10); U = pol(T, 3.2, 10)
    g.seg(R, S).seg(S, T).seg(T, U)
    g.arr(R, S, t=0.5).arr(T, U, t=0.5)
    g.lab(R, "R", 150, 10).lab(S, "S", 80, 10).lab(T, "T", 230, 10).lab(U, "U", -45, 10)
    g.angtxt(S, 190, 232, "α", lr=30, size=12).angtxt(T, 10, 52, "42°", lr=34)
    return g


@fig
def a4_7g():                             # Y7 Ex 6E Q7g
    g = Geo(46)
    G = (0, 0); F = (2.5, 0); D = pol(G, 2.6, 64); E = (D[0] + 2.5, D[1])
    g.poly([G, D, E, F])
    g.arr(D, E).arr(G, F).arr(G, D, 2).arr(F, E, 2)
    g.lab(G, "G", 210, 10).lab(F, "F", -60, 10).lab(D, "D", 100, 10).lab(E, "E", 70, 10)
    g.angtxt(D, 0, 244, "116°", lr=24, ldx=4).angtxt(E, 180, 244, "θ", lr=22, size=12)
    return g


@fig
def a4_7k():                             # Y7 Ex 6E Q7k
    g = Geo(46)
    B = (0, 0); A = (3.6, 0); O = (2.3, 0); D = pol(B, 2.7, -69)
    C = meet(D, dirn(D, O), A, 111)
    g.seg(B, A).seg(B, D).seg(D, C).seg(C, A)
    g.arr(B, D, t=0.55).arr(C, A, t=0.5)
    g.lab(B, "B", 160, 10).lab(A, "A", -10, 10).lab(O, "O", -60, 12).lab(D, "D", -90, 10).lab(C, "C", 90, 10)
    g.angtxt(B, -69, 0, "69°", lr=26).angtxt(A, 111, 180, "β", lr=22, size=12)
    return g


@fig
def a4_8f():                             # Y7 Ex 6E Q8f
    g = Geo(46)
    A = (0, 0); B = (2.6, 0); E = (3.7, 0)
    C = meet(A, 71, B, 121); X = pol(B, 2.9, 71); F = lerp(A, C, 0.48)
    g.seg(A, E).seg(A, C).seg(C, B).seg(B, X)
    g.arr(A, C, t=0.55).arr(B, X, t=0.55)
    g.lab(A, "A", -90, 11).lab(B, "B", -90, 11).lab(E, "E", -90, 10).lab(C, "C", 45, 10).lab(X, "X", 40, 9)
    g.lab(F, "F", 180, 10)
    g.angtxt(A, 0, 71, "71°", lr=24).angtxt(C, 251, 301, "50°", lr=28)
    g.angtxt(B, 71, 121, "β", lr=19, size=12).angtxt(B, 0, 71, "α", lr=19, size=12)
    return g


@fig
def a4_8h():                             # Y7 Ex 6E Q8h
    g = Geo(50)
    h = 1.5
    C = (0, h); A = (h / tan(radians(43)), 0); B = (A[0] + h / tan(radians(76)), h)
    L = (-0.3, 0); M = (A[0] + 1.3, 0)
    g.seg(L, M).seg(C, B).seg(C, A).seg(B, A)
    g.arr(C, B, t=0.5).arr(L, A, t=0.55)
    g.lab(C, "C", 180, 10).lab(B, "B", 0, 10).lab(A, "A", -90, 11).lab(L, "L", -90, 10).lab(M, "M", -90, 10)
    g.angtxt(C, -43, 0, "43°", lr=30).angtxt(B, 180, 256, "76°", lr=26)
    g.angtxt(A, 137, 180, "γ", lr=26, size=12).angtxt(A, 0, 76, "θ", lr=17, size=12)
    return g


@fig
def a4_y7b():                            # Y8 Ex 6B Q7b
    g = Geo(48)
    V1 = (0, 0); L = pol(V1, -3.0, 15); V2 = pol(V1, 2.1, 235); R = pol(V2, 1.9, 15)
    g.seg(L, V1).seg(V1, V2).seg(V2, R)
    g.arr(L, V1, t=0.75).arr(V2, R, t=0.6)
    g.angtxt(V1, 195, 235, "40°", lr=26, ldy=-2)
    g.ang(V2, 15, 55, "a°", r=9, lr=22, reflex=True, italic=True, ldx=-6, ldy=4)
    return g


@fig
def a4_y7e():                            # Y8 Ex 6B Q7e
    g = Geo(42)
    P = (0, 0); Q = pol(P, 3.2, 25); R = pol(Q, 5.0, 236); S = meet(R, 25, P, -40)
    g.seg(P, Q).seg(Q, R).seg(R, S).seg(S, P)
    g.arr(P, Q, t=0.55).arr(R, S, t=0.5)
    g.angtxt(P, -40, 25, "65°", lr=24, ldx=4).angtxt(R, 25, 56, "31°", lr=32)
    g.angtxt(Q, 205, 236, "a°", lr=30, italic=True)
    return g


@fig
def a4_y7i():                            # Y8 Ex 6B Q7i
    g = Geo(48)
    L = (0, 0); Bm = pol(L, 2.3, -60); T = meet(L, 22, Bm, 55); Z = pol(T, 1.3, 300)
    g.poly([L, T, Bm]).seg(T, Z)
    g.arr(Bm, L, t=0.45).arr(Z, T, t=0.45)
    g.angtxt(L, -60, 22, "82°", lr=24).angtxt(T, 202, 235, "a°", lr=30, italic=True)
    g.angtxt(T, 235, 300, "65°", lr=22)
    return g


@fig
def a4_y9a():                            # Y8 Ex 6B Q9a
    g = Geo(46)
    A = (0, 0); O = (2.0, 0)
    g.seg(A, O).ray(A, 76, 1.8).ray(O, 76, 1.8)
    g.arr(A, pol(A, 1.8, 76), t=0.75).arr(O, pol(O, 1.8, 76), t=0.75)
    g.lab(A, "A", 225, 11, size=12).lab(O, "O", -60, 11, size=12).lab(pol(O, 1.8, 76), "B", 60, 9, size=12)
    g.angtxt(A, 0, 76, "a°", lr=20, italic=True)
    return g


@fig
def a4_y9b():                            # Y8 Ex 6B Q9b
    g = Geo(46)
    B = (0, 0); O = pol(B, 2.6, 62); A = pol(O, -2.8, 22); R = pol(B, 2.2, 22)
    g.seg(A, O).seg(O, B).seg(B, R)
    g.arr(A, O, t=0.6).arr(B, R, t=0.6)
    g.ang(B, 22, 62, "a°", r=11, lr=24, reflex=True, italic=True, ldx=-6, ldy=4)
    g.lab(A, "A", 200, 10, size=12).lab(O, "O", 30, 10, size=12).lab(B, "B", -40, 16, size=12)
    return g


@fig
def a4_y9c():                            # Y8 Ex 6B Q9c
    g = Geo(46)
    B = (0, 0); R = pol(B, 3.2, 22); O = meet(B, 58, R, 135); A = pol(O, -2.6, 22)
    g.seg(A, O).poly([O, R, B])
    g.arr(A, O, t=0.6).arr(B, R, t=0.6)
    g.angtxt(O, dirn(O, B), dirn(O, R), "b°", lr=24, italic=True)
    g.angtxt(R, dirn(R, B), dirn(R, O), "a°", lr=26, italic=True)
    g.lab(A, "A", 200, 10, size=12).lab(O, "O", 90, 10, size=12).lab(B, "B", 200, 10, size=12)
    return g


# ------------------------------------------------------------------ A5 further problems, proving parallel
@fig
def a5_g1a():                            # Y7 Ex 6G Q1a
    g = Geo(46)
    C = (0, 0); Z = (2.9, 0); B = pol(C, 3.4, 51); A = (B[0] - 2.9, B[1])
    g.seg(A, B).seg(B, C).seg(C, Z)
    g.lab(A, "A", 180, 9).lab(B, "B", 20, 10).lab(C, "C", 200, 10).lab(Z, "Z", 0, 9)
    g.angtxt(B, 180, 231, "51°", lr=34).angtxt(C, 0, 51, "51°", lr=34)
    return g


@fig
def a5_g1c():                            # Y7 Ex 6G Q1c
    g = Geo(46)
    I = (0, 0); L = (2.0, 0)
    line_through(g, I, 75, 1.4, 1.6); line_through(g, L, 75, 1.4, 1.6); g.seg(I, L)
    g.lab(pol(I, 1.6, 75), "H", 160, 9).lab(pol(I, -1.4, 75), "J", 200, 9).lab(I, "I", 180, 11)
    g.lab(pol(L, 1.6, 75), "K", 20, 9).lab(pol(L, -1.4, 75), "M", -20, 9).lab(L, "L", 0, 11)
    g.angtxt(I, 0, 75, "75°", lr=22).angtxt(L, 75, 180, "105°", lr=24)
    return g


@fig
def a5_g1f():                            # Y7 Ex 6G Q1f
    g = Geo(46)
    G = (0, 0); E = pol(G, 4.0, 25); D = meet(G, 100, E, 180); F = meet(G, 0, E, 275)
    g.poly([D, E, F, G]).seg(G, E)
    g.lab(D, "D", 135, 10).lab(E, "E", 60, 10).lab(F, "F", -60, 10).lab(G, "G", -110, 11)
    g.angtxt(E, 180, 205, "25°", lr=40).angtxt(E, 205, 275, "70°", lr=22)
    g.angtxt(G, 25, 100, "75°", lr=24).angtxt(G, 0, 25, "25°", lr=40)
    return g


@fig
def a5_f1c():                            # Y7 Ex 6F Q1c
    g = Geo(48)
    B = (0, 0); A = (-0.8, 0); C = (2.5, 0); M = pol(B, 2.4, 250); D = pol(B, 2.4, 290); E = (D[0] + 1.6, D[1])
    g.seg(A, C).seg(B, M).seg(B, D).seg(D, E)
    g.arr(B, C, t=0.6).arr(D, E, t=0.55)
    g.lab(A, "A", 90, 9).lab(B, "B", 90, 9).lab(C, "C", 90, 9).lab(M, "M", 225, 9).lab(D, "D", -90, 10).lab(E, "E", -90, 10)
    g.angtxt(B, 180, 250, "70°", lr=24).angtxt(B, 250, 290, "40°", lr=32).angtxt(B, 290, 360, "α", lr=20, size=12)
    g.angtxt(D, 0, 110, "θ", lr=18, size=12)
    return g


@fig
def a5_f1e():                            # Y7 Ex 6F Q1e
    g = Geo(48)
    A = (0, 0); B = pol(A, 3.0, 16); C = meet(A, 86, B, 166); J = pol(C, -0.9, 16); K = pol(C, 3.0, 16)
    g.seg(J, K).poly([A, B, C])
    g.arr(C, K, t=0.6).arr(A, B, t=0.6)
    g.lab(J, "J", 150, 9).lab(K, "K", 60, 9).lab(C, "C", 100, 10).lab(A, "A", -100, 10).lab(B, "B", -30, 10)
    g.angtxt(C, 196, 266, "α", lr=18, size=12).angtxt(C, 266, 346, "γ", lr=18, size=12).angtxt(C, -14, 16, "β", lr=40, size=12)
    g.angtxt(A, 16, 86, "70°", lr=22).angtxt(B, 166, 196, "30°", lr=38)
    return g


@fig
def a5_f1h():                            # Y7 Ex 6F Q1h
    g = Geo(48)
    O = (0, 0); P = (0, 2.0); S = (0, -2.0)
    Q = (2.0 / tan(radians(60)), 2.0); R = (-2.0 / tan(radians(60)), -2.0); A = (-1.6, 0); B = (1.6, 0)
    g.seg(P, S).seg(P, Q).seg(R, S).seg(A, B).seg(R, Q)
    g.right(P, 0, 270, 7)
    g.arr(P, Q, t=0.6).arr(A, B, t=0.78).arr(R, S, t=0.5)
    g.lab(P, "P", 90, 10).lab(Q, "Q", 45, 10).lab(R, "R", 190, 10).lab(S, "S", 0, 10).lab(A, "A", 180, 10).lab(B, "B", 0, 10)
    g.lab(O, "O", -25, 13)
    g.angtxt(O, 90, 180, "α", lr=16, size=12).angtxt(O, 180, 240, "β", lr=19, size=12).angtxt(O, 240, 270, "γ", lr=34, size=12)
    g.angtxt(R, 0, 60, "60°", lr=22)
    return g


@fig
def a5_f2b():                            # Y7 Ex 6F Q2b
    g = Geo(48)
    Q = (0, 0); P = (-3.4, 0); F = pol(Q, -2.6, 25); G = pol(Q, 1.0, 25); R = pol(Q, 1.0, -18)
    O = meet(P, 25, Q, 162)
    g.seg(P, (1.0, 0)).seg(P, O).seg(O, R).seg(F, G)
    g.arr(P, O, t=0.55).arr(F, Q, t=0.45)
    g.ang(O, P, Q, r=14)
    g.lab(P, "P", 160, 10).lab(O, "O", 90, 10).lab(Q, "Q", 95, 11).lab(F, "F", 210, 9).lab(G, "G", 40, 9).lab(R, "R", -30, 9)
    g.angtxt(Q, 0, 25, "25°", lr=44).angtxt(Q, -18, 0, "18°", lr=44)
    return g


@fig
def a5_f2d():                            # Y7 Ex 6F Q2d
    g = Geo(48)
    P = (0, 1.05); Q = (0, -1.05); O = meet(P, -20, Q, 30); X = (-1.5, 1.05); Z = (-1.5, -1.05); Y = (O[0] + 1.3, 0)
    Y = (O[0] + 1.3, O[1])
    g.seg(X, P).seg(P, O).seg(Z, Q).seg(Q, O).seg(O, Y)
    g.arr(X, P, t=0.55).arr(Z, Q, t=0.55).arr(O, Y, t=0.6)
    g.ang(O, P, Q, r=14)
    g.lab(X, "X", 150, 9).lab(P, "P", 80, 10).lab(Z, "Z", 210, 9).lab(Q, "Q", -80, 10).lab(O, "O", -60, 14).lab(Y, "Y", 0, 9)
    g.angtxt(P, 180, 340, "160°", lr=18, ldy=4).angtxt(Q, 30, 180, "150°", lr=18, ldy=-4)
    return g


@fig
def a5_f4d():                            # Y7 Ex 6F Q4d
    g = Geo(46)
    I = (0, 0); H = pol(I, 3.3, -40); G = (H[0], H[1] + 2.2); F = (0, G[1] + H[0] * tan(radians(40)))
    g.poly([F, G, H, I])
    g.arr(I, F, t=0.45).arr(H, G, t=0.5).arr(G, F, 2, t=0.5).arr(H, I, 2, t=0.3)
    g.lab(F, "F", 100, 10).lab(G, "G", 30, 11).lab(H, "H", -45, 10).lab(I, "I", 200, 10)
    g.angtxt(G, 140, 270, "130°", lr=24, ldx=-4).angtxt(H, 90, 140, "γ + 10°", lr=54, ldx=-2)
    return g


@fig
def a5_f4h():                            # Y7 Ex 6F Q4h
    g = Geo(46)
    N = (0, 0); O = (2.9, 0); L = (0, 1.8); M = meet(L, 0, O, 110)
    g.poly([L, M, O, N])
    g.arr(L, M, t=0.5).arr(N, O, t=0.5)
    g.lab(L, "L", 150, 10).lab(M, "M", 60, 10).lab(N, "N", 210, 10).lab(O, "O", -30, 10)
    g.angtxt(L, 270, 360, "γ", lr=18, size=12).angtxt(N, 0, 90, "γ", lr=18, size=12)
    g.angtxt(M, 180, 290, "θ + 40°", lr=34, ldx=-8).angtxt(O, 110, 180, "θ", lr=22, size=12)
    return g


@fig
def a5_g2b():                            # Y7 Ex 6G Q2b
    g = Geo(48)
    C = (0, 0); D = pol(C, 4.0, 20); O = meet(C, 70, D, 165); A = pol(C, 1.35, 70); B = meet(A, 20, D, 165)
    g.seg(C, O).seg(O, D).seg(D, C).seg(A, B)
    g.lab(O, "O", 90, 10).lab(A, "A", 180, 10).lab(B, "B", 60, 10).lab(C, "C", -110, 10).lab(D, "D", 0, 10)
    g.angtxt(A, 20, 70, "50°", lr=22).angtxt(C, 20, 70, "50°", lr=24)
    g.angtxt(B, 165, 200, "β", lr=34, size=12).angtxt(D, 165, 200, "35°", lr=36)
    return g


@fig
def a5_g2d():                            # Y7 Ex 6G Q2d
    g = Geo(48)
    C = (0, 0); A = (0.75, 1.9); D = meet(A, -40, C, 0)
    B = meet(A, 0, C, 30)          # angle ABC = 30 (B on the top line, CB at 30 degrees)
    V = meet(A, dirn(A, D), C, 30)
    g.seg(A, B).seg(C, D).seg(A, D).seg(C, B)
    g.lab(A, "A", 120, 10).lab(B, "B", 60, 10).lab(C, "C", 200, 10).lab(D, "D", -30, 10).lab(V, "V", 0, 14)
    g.angtxt(A, dirn(A, D), 0, "40°", lr=28).angtxt(B, 180, 210, "30°", lr=36)
    g.angtxt(D, 180, dirn(D, A), "40°", lr=30).angtxt(C, 0, 30, "γ", lr=34, size=12)
    return g


# ------------------------------------------------------------------ A6 triangles (Y8 6C)
@fig
def a6_7d():
    g = Geo(46)
    L = (0, 0); R = pol(L, 3.6, 13); T = meet(L, 63, R, 133)
    g.poly([L, R, T]).seg(T, pol(T, 0.9, 133))
    g.angtxt(T, 133, 243, "110°", lr=26, ldx=-6, italic=False).angtxt(R, 133, 193, "60°", lr=28)
    g.angtxt(L, 13, 63, "a°", lr=22, italic=True)
    return g


@fig
def a6_7e():
    g = Geo(46)
    P = (0, 0); Q = pol(P, 3.0, 15); S = pol(P, 3.0, -85)
    g.poly([P, Q, S]).seg(Q, pol(Q, 0.9, 15))
    g.tick(P, Q, 2).tick(P, S, 2)
    g.angtxt(P, -85, 15, "100°", lr=22, ldx=4).angtxt(Q, 15, dirn(Q, S) + 360, "a°", lr=18, italic=True)
    return g


@fig
def a6_7f():
    g = Geo(46)
    X = (0, 0); A = pol(X, 1.7, 98); R = meet(X, 33, A, 333)
    g.seg(pol(X, -0.9, 98), A).seg(pol(X, -1.2, 33), R).seg(A, R)
    g.angtxt(A, 278, 333, "a°", lr=20, italic=True).angtxt(R, 153, 213, "60°", lr=24)
    g.angtxt(X, 278, 393, "115°", lr=22, ldx=6)
    return g


@fig
def a6_9a():
    g = Geo(46)
    T = (0, 0); B = (0, -1.9); R = meet(T, -20, B, 35)
    line_through(g, T, 35, 1.8, 1.6); line_through(g, B, 35, 0.8, 2.6)
    g.seg(T, R).seg(T, B)
    g.arr(pol(T, -1.8, 35), T, t=0.5).arr(pol(B, -0.8, 35), B, t=0.5)
    g.angtxt(T, -20, 35, "55°", lr=22).angtxt(T, -90, -20, "70°", lr=20, ldx=2)
    g.angtxt(B, 35, 90, "a°", lr=20, italic=True)
    return g


@fig
def a6_9b():
    g = Geo(46)
    Bv = (0, 0); R = pol(Bv, 1.8, 43); TL = meet(Bv, 103, R, 138)
    g.poly([Bv, R, TL]).ray(R, 103, 1.3)
    g.arr(Bv, TL, t=0.45).arr(R, pol(R, 1.3, 103), t=0.75)
    g.angtxt(R, 103, 138, "35°", lr=46).angtxt(R, 138, 223, "85°", lr=26)
    g.angtxt(Bv, 43, 103, "a°", lr=20, italic=True)
    return g


@fig
def a6_9c():
    g = Geo(46)
    BL = (0, 0); TL = pol(BL, 1.8, 106); TR = meet(TL, 0, BL, 25)
    g.seg(TL, (TR[0] + 0.9, TL[1])).seg(BL, (TR[0] + 0.5, 0)).seg(BL, TL).seg(BL, TR)
    g.arr(TR, (TR[0] + 0.9, TL[1]), t=0.6).arr(BL, (TR[0] + 0.5, 0), t=0.75)
    g.angtxt(TL, 0, 286, "74°", lr=20, ldx=2).angtxt(BL, 25, 106, "81°", lr=20)
    g.angtxt(BL, 0, 25, "a°", lr=34, italic=True)
    return g


@fig
def a6_10c():
    g = Geo(48)
    A = (0, 0); B = pol(A, 3.1, 34); C = pol(A, 3.1, -2); D = lerp(B, C, 0.5)
    g.poly([A, B, C]).seg(A, D)
    g.tick(A, B, 2).tick(A, C, 2)
    g.right(D, dirn(D, A), dirn(D, B), 7)
    g.lab(A, "A", 190, 10, size=12).lab(B, "B", 70, 10, size=12).lab(C, "C", -20, 10, size=12).lab(D, "D", 20, 11, size=12)
    g.angtxt(B, dirn(B, A), dirn(B, C), "72°", lr=24).angtxt(A, -2, 16, "a°", lr=38, italic=True)
    return g


@fig
def a6_10e():
    g = Geo(48)
    C = (0, 0); A = pol(C, 2.0, 160); B = pol(C, 2.0, 209); D = pol(C, 1.5, 29); E = pol(C, 1.5, -20)
    g.seg(A, E).seg(B, D).seg(A, B)
    g.tick(A, C, 2).tick(B, C, 2)
    g.lab(A, "A", 150, 10, size=12).lab(B, "B", 230, 10, size=12).lab(C, "C", 90, 12, size=12)
    g.lab(D, "D", 30, 10, size=12).lab(E, "E", -20, 10, size=12)
    g.angtxt(C, -20, 29, "49°", lr=24).angtxt(B, 29, dirn(B, A), "a°", lr=22, italic=True)
    return g


@fig
def a6_10f():
    g = Geo(48)
    B = (0, 0); C = pol(B, 3.2, 35); A = meet(B, 95, C, 185); D = pol(C, 0.9, 35)
    g.seg(B, D).seg(A, B).seg(A, C)
    g.right(A, 275, 5, 7)
    g.lab(A, "A", 110, 10, size=12).lab(B, "B", 220, 10, size=12).lab(C, "C", -60, 12, size=12).lab(D, "D", 30, 10, size=12)
    g.angtxt(C, 35, 185, "150°", lr=16, ldy=-6).angtxt(B, 35, 95, "a°", lr=20, italic=True)
    return g


@fig
def a6_11():
    g = Geo(48)
    O = (0, 0); A = pol(O, 1.5, 200); B = pol(O, 1.5, -20)
    g.circle(O, 1.5).poly([O, A, B]).dot(O, 2.4)
    g.lab(O, "O", 90, 11, size=12).lab(A, "A", 200, 11, size=12).lab(B, "B", -20, 11, size=12)
    return g


# ------------------------------------------------------------------ A7 quadrilaterals (Y8 6D)
@fig
def a7_3a():
    g = Geo(46)
    Bt = (0, 0); R = pol(Bt, 1.9, 40); L = pol(Bt, 1.4, 116); T = (R[0] + L[0], R[1] + L[1])
    g.poly([Bt, R, T, L])
    g.arr(Bt, R, t=0.5).arr(L, T, t=0.5).arr(Bt, L, 2, t=0.5).arr(R, T, 2, t=0.5)
    g.angtxt(Bt, 40, 116, "76°", lr=20).angtxt(R, 116, 220, "a°", lr=20, italic=True)
    g.angtxt(T, 220, 296, "b°", lr=20, italic=True)
    return g


@fig
def a7_3c():
    g = Geo(46)
    BR = (0, 0); TR = pol(BR, 1.6, 98); TL = pol(TR, 0.9, 150); BL = pol(BR, 1.8, 150)
    g.poly([BR, TR, TL, BL])
    g.arr(TR, TL, t=0.55).arr(BR, BL, t=0.55)
    g.angtxt(TR, 150, 278, "a°", lr=18, italic=True).angtxt(BR, 98, 150, "52°", lr=24)
    return g


@fig
def a7_6a():
    g = Geo(48)
    L = (0, 0); T = pol(L, 1.6, 35); Bm = pol(L, 2.3, -50); C = meet(T, 255, Bm, 103)
    g.poly([L, T, C, Bm])
    g.angtxt(T, 215, 255, "40°", lr=34, ldx=-4).angtxt(L, -50, 35, "85°", lr=20).angtxt(Bm, 103, 130, "27°", lr=32)
    g.ang(C, dirn(C, T), dirn(C, Bm), "a°", r=9, lr=20, italic=True)
    return g


@fig
def a7_6c():
    g = Geo(46)
    Bm = (0, 0); T = pol(Bm, 3.6, 80); R = pol(T, 2.5, 6); C = meet(R, 203, Bm, 58)
    g.poly([Bm, T, R, C]).seg(T, pol(T, 0.7, 80))
    g.angtxt(T, 6, 80, "74°", lr=22).angtxt(R, 186, 203, "17°", lr=46).angtxt(Bm, 58, 80, "22°", lr=40)
    g.ang(C, dirn(C, R), dirn(C, Bm), "a°", r=9, lr=20, italic=True)
    return g


@fig
def a7_6d():
    g = Geo(46)
    BL = (0, 0); BR = (2.0, 0); TL = pol(BL, 1.5, 74); TR = (TL[0] + 2.0, TL[1])
    g.poly([BL, BR, TR, TL]).seg(TR, (TR[0] + 0.9, TR[1])).seg(TR, pol(TR, 0.8, 74))
    g.arr(TL, TR, t=0.45).arr(BL, BR, t=0.5).arr(BL, TL, 2, t=0.5).arr(BR, TR, 2, t=0.5)
    g.angtxt(TL, 254, 360, "106°", lr=22, ldx=2).angtxt(TR, 0, 74, "a°", lr=18, italic=True)
    return g


@fig
def a7_6e():
    g = Geo(50)
    s_ = 2.0
    A = (0, 0); B = (s_, 0); D = pol(A, s_, -62); C = (D[0] + s_, D[1])
    g.poly([A, B, C, D]).seg(A, C, color=ACC["rose"], dash="3 2", width=1).seg(B, D, color=ACC["rose"], dash="3 2", width=1)
    g.tick(A, B, t=0.6).tick(D, C, t=0.6).tick(A, D).tick(B, C)
    g.angtxt(A, -31, 0, "31°", lr=34).angtxt(D, 0, 59, "a°", lr=22, italic=True)
    return g


def _turns(start, d0, turns, lens):
    """Polygon from a start point, first direction d0, clockwise turns (degrees) and side lengths."""
    pts = [start]
    d = d0
    for t, ln in zip([0] + turns, lens):
        d -= t
        pts.append(pol(pts[-1], ln, d))
    return pts


@fig
def a7_7a():
    g = Geo(46)
    T = (0, 0); Bm = (0, -2.7); L = meet(T, 215, Bm, 120); R = meet(T, 325, Bm, 60)
    g.poly([T, R, Bm, L])
    g.tick(T, L, 1).tick(T, R, 1).tick(L, Bm, 2).tick(R, Bm, 2)
    g.angtxt(L, dirn(L, Bm), dirn(L, T), "95°", lr=22).angtxt(R, dirn(R, T), dirn(R, Bm), "(5x)°", lr=26, ldx=-2, italic=True)
    return g


@fig
def a7_7b():
    g = Geo(46)
    L = (0, 0); Tp = pol(L, 1.6, 40); Bm = pol(L, 1.8, -80); R = meet(Tp, 315, Bm, 15)
    g.poly([L, Tp, R, Bm])
    g.angtxt(Tp, 220, 315, "95°", lr=20).angtxt(L, -80, 40, "(2x)°", lr=24, ldx=4, italic=True)
    g.angtxt(R, 135, 195, "x°", lr=22, italic=True).angtxt(Bm, 15, 100, "85°", lr=20)
    return g


@fig
def a7_7c():
    g = Geo(60)
    L = (0, 0); T1 = pol(L, 2.2, 45); T2 = pol(T1, 1.2, 9); R = meet(T2, -63, L, 9)
    g.poly([L, T1, T2, R])
    g.angtxt(L, 9, 45, "x°", lr=32, italic=True).angtxt(T1, 225, 369, "(4x)°", lr=24, ldx=4, italic=True)
    g.angtxt(T2, 189, 297, "(3x)°", lr=22, italic=True).angtxt(R, 117, 189, "(2x)°", lr=26, ldx=-4, italic=True)
    return g


# ------------------------------------------------------------------ B2 perimeter (Y7 9D)
def _side(g, p, q, s, off=11, size=11, italic=False):
    """Label s beside segment p-q, off pixels to the right of the direction p->q."""
    m = lerp(p, q, 0.5)
    a = radians(dirn(p, q))
    g.text(m, s, size=size, italic=italic, dx=off * sin(a), dy=off * cos(a))
    return g


@fig
def b2_1d():
    g = Geo(38)
    BL, BR, TR, TL = (0, 0), (2.6, 0), (1.5, 1.85), (0.55, 2.3)
    g.poly([BL, BR, TR, TL])
    _side(g, BL, TL, "18", -10); _side(g, TL, TR, "7", -10); _side(g, TR, BR, "12", -11); _side(g, BL, BR, "15", 11)
    return g


@fig
def b2_1e():
    g = Geo(38)
    A, B, C = (0, 0), (2.9, 0), (1.45, 1.55)
    g.poly([A, B, C])
    _side(g, A, C, "17", -10); _side(g, C, B, "17", -10); _side(g, A, B, "16", 11)
    return g


@fig
def b2_1f():
    g = Geo(38)
    A, B, C, D = (0, 0), (2.5, 0), (2.5, 1.85), (0, 1.85)
    g.poly([A, B, C, D]).tick(A, B).tick(D, C).tick(B, C, 2).tick(A, D, 2)
    _side(g, B, C, "17", -16); _side(g, A, B, "23", 12)
    return g


@fig
def b2_5d():
    g = Geo(38)
    BL, BR, TR, TL = (0, 0), (2.3, 0), (1.4, 1.6), (0.5, 2.1)
    g.poly([BL, BR, TR, TL])
    _side(g, BL, TL, "4b", -12, italic=True); _side(g, TL, TR, "a", -10, italic=True)
    _side(g, TR, BR, "2b", -12, italic=True); _side(g, BL, BR, "3a", 11, italic=True)
    return g


@fig
def b2_5e():
    g = Geo(38)
    A, B, C = (0, 0), (2.9, 0), (1.45, 2.05)
    g.poly([A, B, C])
    _side(g, A, C, "4a", -12, italic=True); _side(g, C, B, "4a", -12, italic=True); _side(g, A, B, "3b", 11, italic=True)
    return g


@fig
def b2_5f():
    g = Geo(38)
    A, B, C, D = (0, 0), (2.5, 0), (2.5, 2.05), (0, 2.05)
    g.poly([A, B, C, D]).tick(A, B).tick(D, C).tick(B, C, 2).tick(A, D, 2)
    _side(g, B, C, "6y", -16, italic=True); _side(g, A, B, "7x", 12, italic=True)
    return g


@fig
def b2_8():
    g = Geo(15)
    pts = [(0, 0), (0, 10), (2, 10), (2, 7.2), (5.8, 7.2), (5.8, 2.2), (7.3, 2.2), (7.3, 1.1), (10, 1.1), (10, 0)]
    g.poly(pts)
    _side(g, (0, 0), (0, 10), "10 m", -20); _side(g, (0, 0), (10, 0), "10 m", 11)
    return g


# ------------------------------------------------------------------ B3 area of rectangles and composite shapes (Y7 9F)
@fig
def b3_2d():
    g = Geo(19)
    pts = [(0, 0), (0, 9), (6, 9), (6, 6), (7, 6), (7, 0)]
    g.poly(pts)
    _side(g, (0, 0), (0, 9), "9 m", -17); _side(g, (0, 0), (7, 0), "7 m", 11)
    g.text((6, 7.5), "3 m", size=10.5, dx=-17)
    g.text((7, 6), "1 m", size=10.5, dx=18, dy=8)
    return g


@fig
def b3_2f():
    g = Geo(23)
    pts = [(0, 0), (0, 6), (6, 6), (6, 3), (7, 3), (7, 1), (8, 1), (8, 0)]
    g.poly(pts)
    _side(g, (0, 0), (0, 6), "6 cm", -20); _side(g, (0, 6), (6, 6), "6 cm", -10)
    g.text((6, 4.5), "3 cm", size=10.5, dx=-20).text((7, 3), "1 cm", size=10.5, dx=18, dy=-8)
    g.text((7, 2), "2 cm", size=10.5, dx=-20).text((8, 1), "1 cm", size=10.5, dx=18, dy=-8)
    return g


@fig
def b3_2h():
    g = Geo(23)
    pts = [(0, 0), (0, 6), (8, 6), (8, 4), (2, 4), (2, 2), (6, 2), (6, 0)]
    g.poly(pts).seg((6, 0), (8, 0), color=ACC["rose"], dash="2 2", width=1)
    g.dim((8.8, 4), (8.8, 0))
    _side(g, (0, 0), (0, 6), "6 m", -16); _side(g, (0, 6), (8, 6), "8 m", -10)
    g.text((5, 4), "6 m", size=10.5, dy=-9).text((2, 3), "2 m", size=10.5, dx=14).text((4, 2), "4 m", size=10.5, dy=-9)
    g.text((8.8, 2), "4 m", size=10.5, dx=16)
    return g


@fig
def b3_5():
    g = Geo(20)
    rects = [(1.25, -0.3, 1, 5), (3.5, -1.0, 1, 5), (0.9, 2.5, 5, 1), (-0.3, 1.0, 5, 1)]
    for (x, y, w, h) in rects:
        g.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill=FILL, opacity=1)
    return g


# ------------------------------------------------------------------ B4 triangles and parallelograms (Y7 9G)
RED = ACC["rose"]


@fig
def b4_1c():
    g = Geo(19)
    T = (0, 4); A = (1.0, 0); B = (14.0, 0)
    g.poly([T, A, B]).seg(T, (0, 0), color=RED, dash="3 2", width=1).seg((0, 0), A, color=RED, dash="3 2", width=1)
    g.right((0, 0), 0, 90, 6)
    _side(g, (0, 0), T, "4 cm", -22); _side(g, A, B, "13 cm", 11)
    return g


@fig
def b4_1d():
    g = Geo(15)
    A = (0, 0); B = (14, 0); T = (5, 12)
    g.poly([A, B, T]).seg(T, (5, 0), color=RED, dash="3 2", width=1)
    g.right((5, 0), 0, 90, 6)
    _side(g, A, T, "13 mm", -24); _side(g, T, B, "15 mm", -24); _side(g, A, B, "14 mm", 11)
    g.text((5, 4), "12 mm", size=10.5, dx=-22)
    return g


@fig
def b4_7b():
    g = Geo(17)
    pts = [(0, 0), (8, 0), (8, 3), (5, 6), (0, 3)]
    g.poly(pts).seg((5, 6), (8, 6), color=RED, dash="3 2", width=1)
    g.dim((8.8, 6), (8.8, 3)).dim((8.8, 3), (8.8, 0))
    g.text((8.8, 4.5), "3 km", size=10.5, dx=18).text((8.8, 1.5), "3 km", size=10.5, dx=18)
    _side(g, (0, 0), (8, 0), "8 km", 11)
    return g


@fig
def b4_7c():
    g = Geo(13)
    pts = [(0, 0), (11, 0), (11, 12), (5, 12)]
    g.poly(pts)
    _side(g, (0, 0), (11, 0), "11 cm", 11); _side(g, (5, 12), (11, 12), "6 cm", -10); _side(g, (11, 0), (11, 12), "12 cm", -22)
    return g


@fig
def b4_7d():
    g = Geo(11)
    TL = (-8, 0); TM = (0, 0); R = (6, -5); Bm = (0, -15)
    g.poly([TL, TM, R, Bm]).seg(TM, Bm, color=RED, dash="3 2", width=1)
    g.seg(TM, (6, 0), color=RED, dash="3 2", width=1).seg((6, 0), R, color=RED, dash="3 2", width=1)
    g.right(TM, 180, 270, 6).right((6, 0), 180, 270, 6)
    g.text((-4, 0), "8 mm", size=10.5, dy=10).text((3, 0), "6 mm", size=10.5, dy=-10).text((0, -6), "15 mm", size=10.5, dx=-22)
    return g


@fig
def b4_8a():
    g = Geo(9)
    S = 17
    g.poly([(0, 0), (S, 0), (S, S), (0, S)], fill=FILL, opacity=0.95)
    g.poly([(12, S), (S, 5), (5, 0), (0, 12)], fill="#ffffff", opacity=1)
    g.dim((0, S + 1.6), (12, S + 1.6)).dim((12, S + 1.6), (S, S + 1.6))
    g.text((6, S + 1.6), "12 m", size=10.5, dy=-9).text((14.5, S + 1.6), "5 m", size=10.5, dy=-9)
    for p, q, n in (((0, S), (12, S), 2), ((12, S), (S, S), 1), ((S, S), (S, 5), 2), ((S, 5), (S, 0), 1),
                    ((S, 0), (5, 0), 2), ((5, 0), (0, 0), 1), ((0, 0), (0, 12), 2), ((0, 12), (0, S), 1)):
        g.tick(p, q, n)
    return g


@fig
def b4_8d():
    g = Geo(14)
    g.poly([(0, 0), (13, 0), (13, 11), (0, 11)], fill=FILL, opacity=0.95)
    g.poly([(3, 3), (10, 3), (6.5, 8)], fill="#ffffff", opacity=1)
    g.dim((0, 3), (3, 3)).dim((10, 3), (13, 3)).dim((3, 3), (3, 0)).dim((6.5, 8), (6.5, 11)).dim((4.6, 3), (4.6, 8))
    g.seg((4.6, 8), (6.5, 8), color=RED, dash="2 2", width=1)
    g.text((1.5, 3), "3 m", size=10.5, dy=-9).text((11.5, 3), "3 m", size=10.5, dy=-9).text((3, 1.5), "3 m", size=10.5, dx=16)
    g.text((6.5, 9.5), "3 m", size=10.5, dx=16).text((4.6, 6.4), "5 m", size=10.5, dx=-14).text((6.5, 3), "7 m", size=10.5, dy=-9)
    return g


@fig
def b4_15():
    g = Geo(26)
    A, B, C, D = (0, 4), (8, 4), (8, 0), (0, 0)
    X, Y = (2, 4), (6, 0)
    g.poly([A, B, C, D], width=1.0).poly([D, X, B, Y], fill=FILL, opacity=0.95, width=1.6)
    g.lab(A, "A", 150, 10).lab(X, "X", 90, 10).lab(B, "B", 30, 10).lab(D, "D", 210, 10).lab(Y, "Y", -90, 11).lab(C, "C", -30, 10)
    return g


# ------------------------------------------------------------------ B5 special quadrilaterals (Y8 3D)
@fig
def b5_3d():
    g = Geo(42)
    A = (0, 1.3); B = (1.4, 1.3); C = (2.1, 0); D = (0.7, 0)
    g.poly([A, B, C, D]).seg(A, C, color=RED, dash="3 2", width=1)
    g.tick(A, B).tick(D, C).tick(A, D).tick(B, C)
    g.text(lerp(A, C, 0.45), "5 cm", size=11, dx=4, dy=-10)
    g.dim((2.0, -0.95), (2.9, 0.65))
    g.text((2.45, -0.15), "3 cm", size=11, dx=24)
    return g


@fig
def b5_3h():
    g = Geo(7.5)
    L = (-7, 3); T = (0, 10); Bm = (0, -10); R = (23, 0)
    g.poly([T, R, Bm, L]).seg(T, Bm, color=RED, dash="3 2", width=1)
    g.tick(L, T, 1).tick(L, Bm, 1).tick(T, R, 2).tick(Bm, R, 2)
    g.dim((-7, -13.5), (23, -13.5))
    g.text((0, 2), "20 mm", size=11, dx=26).text((8, -13.5), "30 mm", size=11, dy=11)
    return g


@fig
def b5_3k():
    g = Geo(18)
    # parallel sides 9 m and 4 m, 5 m apart, drawn slanting as in the book
    u = (cos(radians(40)), sin(radians(40))); n = (cos(radians(-50)), sin(radians(-50)))
    P = (0, 0); Q = (9 * u[0], 9 * u[1])
    P2 = (P[0] + 5 * n[0] + 0.6 * u[0], P[1] + 5 * n[1] + 0.6 * u[1]); Q2 = (P2[0] + 4 * u[0], P2[1] + 4 * u[1])
    g.poly([P, Q, Q2, P2])
    g.arr(P, Q, t=0.45).arr(P2, Q2, t=0.6)
    F = lerp(P, Q, 0.25); G2 = (F[0] + 5 * n[0], F[1] + 5 * n[1])
    g.seg(F, G2, color=RED, dash="3 2", width=1).right(F, -50, 40, 6)
    g.text(lerp(P, Q, 0.5), "9 m", size=11, dx=-10, dy=-12).text(lerp(F, G2, 0.55), "5 m", size=11, dx=14)
    g.text(lerp(P2, Q2, 0.4), "4 m", size=11, dx=14, dy=4)
    return g


@fig
def b5_3l():
    g = Geo(5.2)
    u = (cos(radians(22)), sin(radians(22))); n = (cos(radians(112)), sin(radians(112)))
    P = (0, 0); Q = (50 * u[0], 50 * u[1])
    P2 = (P[0] + 16 * n[0] + 22 * u[0], P[1] + 16 * n[1] + 22 * u[1]); Q2 = (P2[0] + 20 * u[0], P2[1] + 20 * u[1])
    g.poly([P, Q, Q2, P2])
    g.arr(P, Q, t=0.75).arr(P2, Q2, t=0.4)
    F = lerp(P, Q, 0.62); G2 = (F[0] + 16 * n[0], F[1] + 16 * n[1])
    g.seg(F, G2, color=RED, dash="3 2", width=1).right(F, 112, 202, 6)
    g.text(lerp(P2, Q2, 0.45), "20 mm", size=11, dx=-8, dy=-15).text(lerp(F, G2, 0.5), "16 mm", size=11, dx=26)
    g.text(lerp(P, Q, 0.62), "50 mm", size=11, dx=10, dy=14)
    return g


@fig
def b5_5():
    g = Geo(1.6)
    O = (0, 0); L = (-30, 0); R = (30, 0); T = (0, 30); Bm = (0, -60)
    g.poly([T, R, Bm, L]).seg(L, R, width=1.8).seg(T, Bm, width=1.8).dot(O, 2.6)
    g.tick(L, O).tick(O, R).tick(O, T)
    g.dim((40, 0), (40, -60))
    g.text((40, -30), "60 cm", size=11, dx=24)
    g.text((-30, 0), "30 cm", size=11, dx=-34, dy=-20)
    g.items.append(("line", ((-38, 12), (-16, 1.5), BLUE, 0.9, None)))
    return g


@fig
def b5_10a():
    g = Geo(26)
    P0 = (0, 0); P1 = (3.0, 0); P3 = (0.9, 1.6); P2 = (3.9, 1.6)
    g.poly([P0, P1, P2, P3])
    g.arr(P0, P1, 2, t=0.6).arr(P3, P2, 2, t=0.6).arr(P0, P3, t=0.55).arr(P1, P2, t=0.55)
    g.seg((1.6, 0), (1.6, 1.6), color=RED, dash="3 2", width=1).right((1.6, 0), 0, 90, 6)
    g.text((1.6, 0.8), "x", size=11.5, italic=True, dx=10).text((2.3, 0), "2x", size=11.5, italic=True, dy=12)
    return g


@fig
def b5_10b():
    g = Geo(38)
    T = (0, 1.0); Bm = (0, -2.0); L = (-1.2, 0); R = (1.2, 0); O = (0, 0)
    g.poly([T, R, Bm, L]).seg(L, R, color=RED, dash="3 2", width=1).seg(T, Bm, color=RED, dash="3 2", width=1)
    g.tick(L, T, 1).tick(T, R, 1).tick(L, Bm, 2).tick(R, Bm, 2)
    g.text((0, 0.5), "b", size=11.5, italic=True, dx=8).text((-0.6, 0), "a", size=11.5, italic=True, dy=-8)
    g.text((0.6, 0), "a", size=11.5, italic=True, dy=-8).text((0, -0.6), "2b", size=11.5, italic=True, dx=10)
    return g


@fig
def b5_10c():
    g = Geo(22)
    # trapezium with parallel sides 3a (top) and 5a (bottom), height 2a, both tilted by 6 degrees
    u = (cos(radians(6)), sin(radians(6)))
    n = (-u[1], u[0])
    BL = (0, 0); BR = (5 * u[0], 5 * u[1])
    TL = (0.15 * u[0] + 2 * n[0], 0.15 * u[1] + 2 * n[1]); TR = (TL[0] + 3 * u[0], TL[1] + 3 * u[1])
    g.poly([BL, BR, TR, TL])
    g.arr(TL, TR, t=0.6).arr(BL, BR, t=0.6)
    F = (0.3 * u[0], 0.3 * u[1]); G2 = (F[0] + 2 * n[0], F[1] + 2 * n[1])
    g.seg(F, G2, color=RED, dash="3 2", width=1).right(F, 6, 96, 6)
    g.text(lerp(TL, TR, 0.5), "3a", size=11.5, italic=True, dy=-10).text(lerp(F, G2, 0.5), "2a", size=11.5, italic=True, dx=12)
    g.text(lerp(BL, BR, 0.5), "5a", size=11.5, italic=True, dy=12)
    return g


@fig
def b5_11():
    g = Geo(13)
    BL = (0, 0); BR = (10, 0); h = 8; dx = sqrt(100 - 64)
    TL = (dx, h); TR = (dx + 10, h)
    g.poly([BL, BR, TR, TL])
    g.seg((dx + 0.6, 0), (dx + 0.6, h), color=RED, dash="3 2", width=1).right((dx + 0.6, 0), 0, 90, 6)
    g.tick(BL, BR, 2).tick(TL, TR, 2).tick(BL, TL, 2).tick(BR, TR, 2)
    g.text((dx + 0.6, h / 2), "8 cm", size=11, dx=20).text(lerp(BR, TR, 0.5), "10 cm", size=11, dx=24)
    return g


# ------------------------------------------------------------------ C mixed challenge
@fig
def c_r7b():                             # Y7 Ch 6 Review Q7b
    g = Geo(46)
    A = (0, 0); C = (3.2, 0); T = meet(A, 55, C, 145); R = pol(C, 1.5, 55); E = (4.3, 0)
    g.seg(A, E).seg(A, T).seg(T, C).seg(C, R)
    g.right(T, dirn(T, A), dirn(T, C), 7)
    g.arr(A, T, t=0.5).arr(C, R, t=0.6)
    g.angtxt(A, 0, 55, "55°", lr=22).angtxt(C, 145, 180, "α", lr=36, size=12)
    return g


@fig
def c_r7d():                             # Y7 Ch 6 Review Q7d
    g = Geo(50)
    V = (0, 0); T = pol(V, 1.0, 57); Bb = pol(V, 1.6, -30)
    g.seg(V, T).seg(T, (T[0] + 2.6, T[1])).seg(pol(V, 0.5, 150), Bb).seg(Bb, (T[0] + 2.6, Bb[1]))
    g.seg((-0.9, 0), (T[0] + 2.6, 0), color=RED, dash="4 3", width=1.1)
    g.arr(T, (T[0] + 2.6, T[1]), t=0.6).arr((-0.9, 0), (T[0] + 2.6, 0), t=0.75).arr(Bb, (T[0] + 2.6, Bb[1]), t=0.5)
    g.angtxt(V, 57, 150, "α", lr=18, size=12).angtxt(T, 0, 237, "123°", lr=24, ldx=6)
    g.angtxt(Bb, 0, 150, "150°", lr=16, ldy=-8)
    return g


@fig
def c_ch1():                             # Y7 Ch 6 Challenge Q1
    g = Geo(44)
    P0 = (0, 0); P1 = pol(P0, 1.6, -60); P2 = pol(P1, 2.0, 30); P3 = pol(P2, 2.5, -40); P4 = pol(P3, 1.9, 25)
    P5 = pol(P4, 1.6, -60)
    g.poly([P0, P1, P2, P3, P4, P5], closed=False)
    g.arr(P0, P1, t=0.45).arr(P4, P5, t=0.45)
    g.right(P1, 120, 30, 7)
    g.angtxt(P2, 210, 320, "110°", lr=22).angtxt(P3, 25, 140, "115°", lr=22).angtxt(P4, 205, 300, "α", lr=20, size=12)
    return g


def _zig(g, top_y, T, V1, V2, B, bot_y, xl=-3.0, xr=None):
    xr = xr if xr is not None else V2[0] - 0.9
    g.seg((xl, top_y), T).seg(T, V1).seg(V1, V2).seg(V2, B).seg((xl, bot_y), (xr, bot_y))
    g.arr((xl, top_y), (T[0], top_y), t=0.4).arr((xl, bot_y), (xr, bot_y), t=0.2)


@fig
def c_ch2a():                            # Y7 Ch 6 Challenge Q2a: 20 at T, alpha at V1, 50 at V2, 30 at B
    g = Geo(42)
    al = 40
    T = (1.6, 0); V1 = pol(T, 1.8, 200); V2 = pol(V1, 4.2, 20 - al)
    B = meet(V2, 250 - al, (0, -3.7), 0)
    _zig(g, 0, T, V1, V2, B, B[1], xr=V2[0] - 0.8)
    g.angtxt(T, 180, 200, "20°", lr=48).angtxt(V1, 20 - al, 20, "α", lr=36, size=12)
    g.angtxt(V2, 200 - al, 250 - al, "50°", lr=36).angtxt(B, 0, 30, "30°", lr=46)
    return g


@fig
def c_ch2b():                            # Y7 Ch 6 Challenge Q2b: gamma at T, x at V1, beta at V2, alpha at B
    g = Geo(42)
    ga, x, be = 14, 30, 34
    al = ga - x + be
    T = (1.6, 0); V1 = pol(T, 1.8, 180 + ga); V2 = pol(V1, 4.2, ga - x)
    B = meet(V2, 180 + ga - x + be, (0, -3.7), 0)
    _zig(g, 0, T, V1, V2, B, B[1], xr=V2[0] - 0.8)
    g.angtxt(T, 180, 180 + ga, "γ", lr=50, size=12).angtxt(V1, ga - x, ga, "x", lr=40, size=11.5, italic=True)
    g.angtxt(V2, 180 + ga - x, 180 + ga - x + be, "β", lr=40, size=12).angtxt(B, 0, al, "α", lr=50, size=12)
    return g


@fig
def c_r8a():                             # Y7 Ch 9 Review Q8a
    g = Geo(24)
    pts = [(0, 11), (6, 11), (6, 12), (9, 12), (9, 9), (8, 9), (8, 5), (6, 5), (6, 0), (3, 0), (3, 5), (0, 5)]
    g.poly(pts)
    labs = [("6 m", 0, 1, 11), ("1 m", 1, 2, -16), ("3 m", 2, 3, -11), ("3 m", 3, 4, -16), 
            ("4 m", 5, 6, 16), ("2 m", 6, 7, 11), ("3 m", 8, 9, -11), ("5 m", 9, 10, -16),
            ("3 m", 10, 11, -11), ("6 m", 11, 0, -16)]
    for s, i, j, off in labs:
        _side(g, pts[i], pts[j], s, off)
    g.text((9, 9), "1 m", size=10.5, dx=15, dy=9)
    return g


@fig
def c_r8b():                             # Y7 Ch 9 Review Q8b
    g = Geo(19)
    T = (0, 18); Q1 = (0, 12); Q2 = (0, 10); R1 = (6, 10); Q3 = (0, 6); R2 = (6, 6); B = (-2, 0); Q4 = (-2, 6); L = (-8, 6)
    g.poly([T, R1, Q2, Q3, R2, B, Q4, L, Q1])
    g.seg(Q1, Q2, color=RED, dash="2 2", width=1).seg(Q4, Q3, color=RED, dash="2 2", width=1)
    for s, p, q, off in (("10 km", T, R1, -24), ("6 km", R1, Q2, -11), ("4 km", Q2, Q3, 24), ("6 km", Q3, R2, -11),
                         ("10 km", R2, B, -24), ("6 km", B, Q4, -24), ("6 km", Q4, L, -11), ("10 km", L, Q1, -24),
                         ("6 km", Q1, T, -24)):
        _side(g, p, q, s, off)
    g.text((0, 11), "2 km", size=10.5, dx=18).text((-1, 6), "2 km", size=10.5, dy=-10)
    return g


@fig
def c_ch4():                             # Y7 Ch 9 Challenge Q4
    g = Geo(21)
    grass = [(0, 0), (0, 9), (8, 9), (8, 6), (12, 6), (12, 9), (16, 9), (16, 0), (12, 0), (12, 3), (8, 3), (8, 0)]
    path = [(-1, -1), (-1, 10), (9, 10), (9, 7), (11, 7), (11, 10), (17, 10), (17, -1), (11, -1), (11, 2), (9, 2), (9, -1)]
    g.poly(path, color=RED, width=1, dash="4 3")
    g.poly(grass, fill=FILL, color=FILL, opacity=1)
    g.text((8, 7.5), "3 m", size=10.5, dx=-14).text((14, 9), "4 m", size=10.5, dy=10).text((0, 4.5), "9 m", size=10.5, dx=14)
    g.text((10, 3), "4 m", size=10.5, dy=-14).text((12, 1.5), "3 m", size=10.5, dx=14).text((4, 0), "8 m", size=10.5, dy=-10)
    g.dim((16, -0.4), (17, -0.4)).dim((15.6, 0), (15.6, -1))
    g.text((15.6, -0.5), "1 m", size=10.5, dx=-15)
    return g


# ------------------------------------------------------------------ fix round: new figures
@fig
def a1_10a():                            # Y8 Ex 6A Q10a
    g = Geo(48)
    B = (0, 0)
    g.ray(B, 90, 1.6).ray(B, 0, 1.8).ray(B, 37, 1.8)
    g.right(B, 0, 90, 7)
    g.lab((0, 1.6), "A", 90, 9, size=12).lab((1.8, 0), "D", 0, 9, size=12).lab(pol(B, 1.8, 37), "C", 40, 9, size=12)
    g.lab(B, "B", 200, 11, size=12)
    g.angtxt(B, 0, 37, "x°", lr=26, italic=True)
    return g


@fig
def a1_10b():                            # Y8 Ex 6A Q10b
    g = Geo(48)
    B = (0, 0)
    g.seg((-1.3, 0), (1.3, 0)).ray(B, 125, 1.0)
    g.lab((-1.3, 0), "D", -90, 10, size=12).lab(B, "B", -90, 11, size=12).lab((1.3, 0), "A", -90, 10, size=12)
    g.lab(pol(B, 1.0, 125), "C", 110, 9, size=12)
    g.angtxt(B, 125, 180, "x°", lr=24, italic=True)
    return g


@fig
def a1_10c():                            # Y8 Ex 6A Q10c
    g = Geo(48)
    B = (0, 0)
    g.seg((-1.3, 0), (1.3, 0)); line_through(g, B, 125, 1.4, 1.1)
    g.lab((-1.3, 0), "E", 180, 9, size=12).lab((1.3, 0), "A", 0, 9, size=12).lab(B, "B", 45, 13, size=12)
    g.lab(pol(B, 1.1, 125), "D", 120, 9, size=12).lab(pol(B, -1.4, 125), "C", -60, 9, size=12)
    g.angtxt(B, 125, 180, "x°", lr=24, italic=True)
    return g


@fig
def a1_10d():                            # Y8 Ex 6A Q10d
    g = Geo(48)
    B = (0, 0)
    g.ray(B, 75, 1.6).ray(B, 40, 1.6)
    g.ang(B, 40, 75, "x°", r=17, lr=30, reflex=True, italic=True, ldx=-4, ldy=6)
    g.lab(pol(B, 1.6, 75), "A", 80, 9, size=12).lab(pol(B, 1.6, 40), "C", 30, 9, size=12).lab(B, "B", 235, 8, size=11)
    return g


@fig
def b2_ch14():                           # Y7 Ch 9 Challenge Q14
    g = Geo(13)
    pts = [(0, 0), (0, 10), (3.2, 10), (3.2, 9), (6.05, 9), (6.05, 7.95), (7.9, 7.95), (7.9, 7.3), (9.4, 7.3),
           (9.4, 6.65), (15.3, 6.65), (15.3, 1.05), (16, 1.05), (16, 0)]
    g.poly(pts)
    _side(g, (0, 0), (0, 10), "10 m", -20); _side(g, (0, 0), (16, 0), "16 m", 11)
    return g


@fig
def b4_8c():                             # Y7 Ex 9G Q8c (not to scale in the book either)
    g = Geo(24)
    A, Bb, T = (0, 0), (10, 0), (7.4, 5)
    g.poly([A, Bb, T], fill=FILL, opacity=0.95)
    g.poly([(4.25, 2.5), (6.25, 2.5), (5.25, 0.5)], fill="#ffffff", opacity=1)
    g.poly([(5.95, 0.5), (8.95, 0.5), (7.3, 4.5)], fill="#ffffff", opacity=1)
    g.seg(T, (11.6, 5), color=RED, dash="3 2", width=1).seg((7.3, 4.5), (12.4, 4.5), color=RED, dash="3 2", width=1)
    g.seg((8.95, 0.5), (12.4, 0.5), color=RED, dash="3 2", width=1).seg(Bb, (11.6, 0), color=RED, dash="3 2", width=1)
    g.dim((11.6, 5), (11.6, 0)).dim((12.4, 4.5), (12.4, 0.5)).dim((3.85, 2.5), (3.85, 0.5))
    g.seg((3.85, 0.5), (5.25, 0.5), color=RED, dash="2 2", width=1)
    g.text((11.6, 2.5), "5 m", size=10.5, dx=-15).text((12.4, 2.5), "4 m", size=10.5, dx=15)
    g.text((3.85, 1.5), "2 m", size=10.5, dx=-14).text((5.25, 2.5), "2 m", size=10.5, dy=-9)
    g.text((7.45, 0.5), "3 m", size=10.5, dy=-9).text((5, 0), "10 m", size=10.5, dy=11)
    return g


@fig
def c_ch3():                             # Y7 Ch 6 Challenge Q3: gamma at T, x at V1, alpha at V2, beta at B
    g = Geo(42)
    ga, x, al = 45, 143, 30
    T = (0, 0); V1 = pol(T, 1.6, -ga)
    d1 = 180 - ga - x                            # direction V1 -> V2
    V2 = pol(V1, 3.6, d1)
    d2 = d1 + 180 + al                           # direction V2 -> B
    B = meet(V2, d2, (0, -2.4), 0)
    be = d2 - 180                                # direction B -> V2, measured from the bottom line
    g.seg((-3.0, 0), (3.8, 0)).seg(T, V1).seg(V1, V2).seg(V2, B).seg((-3.0, B[1]), (3.8, B[1]))
    g.arr((-3.0, 0), (-0.2, 0), t=0.6).arr((-3.0, B[1]), (B[0], B[1]), t=0.6)
    g.angtxt(T, -ga, 0, "γ", lr=22, size=12).angtxt(V1, d1, 180 - ga, "x", lr=16, size=11.5, italic=True)
    g.angtxt(V2, d1 + 180, d2, "α", lr=40, size=12).angtxt(B, 0, be, "β", lr=56, size=12)
    return g


if __name__ == "__main__":
    for name, fn in FIGS.items():
        save(name, fn())
    print(len(FIGS), "figures written")
