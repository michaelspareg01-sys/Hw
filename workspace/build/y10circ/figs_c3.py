"""Figures for Lesson C3 (Tangents and secants) and the chapter review. Run: python3 figs_c3.py

Sources: AMSI TIMES Circle Geometry pp. 18-27 (concept figures, Exercises 16-25); Maths Pathway
'Chords, Secants, and Tangents' (Q7-Q9) and 'Intersecting Chords and Secants' (all); the past papers.
Figures with given lengths or angles are constructed exactly from the given data (model coordinates,
then mapped to the page), unless the source says NOT TO SCALE, where the layout of the source is kept
but the geometry is still exact.
"""
from math import sin, cos, tan, radians, degrees, sqrt, atan2, hypot, asin, acos, pi
from figs import CF, ext, foot
from figs import save as _save


def save(name, f):
    _save(name, f, rmax=30)


# ---------------------------------------------------------------- model helpers (y up)
def rot(v, deg):
    a = radians(deg)
    return (v[0] * cos(a) - v[1] * sin(a), v[0] * sin(a) + v[1] * cos(a))


def add(p, q, k=1.0):
    return (p[0] + k * q[0], p[1] + k * q[1])


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def unit(v):
    L = hypot(*v)
    return (v[0] / L, v[1] / L)


def circum(a, b, c):
    ax, ay, bx, by, cx, cy = a[0], a[1], b[0], b[1], c[0], c[1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), hypot(ax - ux, ay - uy)


def line_circle(p, d, c, r):
    """Parameters t (sorted) where p + t d meets the circle (d a unit vector)."""
    px, py = p[0] - c[0], p[1] - c[1]
    b = px * d[0] + py * d[1]
    disc = b * b - (px * px + py * py - r * r)
    if disc < 0:
        return []
    s = sqrt(disc)
    return sorted((-b - s, -b + s))


def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def onm(c, r, deg):
    return (c[0] + r * cos(radians(deg)), c[1] + r * sin(radians(deg)))


class G(CF):
    """CF with a model frame: fit(points, pad) chooses scale and origin so the model points fill the canvas."""

    def frame(self, pts, pad=16, extra=()):
        xs = [p[0] for p in list(pts) + list(extra)]
        ys = [p[1] for p in list(pts) + list(extra)]
        sx = (self.w - 2 * pad) / max(max(xs) - min(xs), 1e-9)
        sy = (self.h - 2 * pad) / max(max(ys) - min(ys), 1e-9)
        self.s = min(sx, sy)
        self.ox = pad + (self.w - 2 * pad - self.s * (max(xs) - min(xs))) / 2 - self.s * min(xs)
        self.oy = pad + (self.h - 2 * pad - self.s * (max(ys) - min(ys))) / 2 + self.s * max(ys)
        return self

    def T(self, p):
        return (self.ox + self.s * p[0], self.oy - self.s * p[1])

    def C(self, c, r, **kw):
        return self.circle(self.T(c), self.s * r, **kw)

    def S(self, p, q, **kw):
        return self.seg(self.T(p), self.T(q), **kw)

    def D(self, p, r=2.2):
        return self.pdot(self.T(p), r)

    def L(self, p, s, dx=0, dy=0, size=11.5, italic=True):
        return self.lab(self.T(p), s, dx=dx, dy=dy, size=size, italic=italic)

    def O(self, p, c, s, d=11, size=11.5, italic=True):
        return self.out(self.T(p), self.T(c), s, d=d, size=size, italic=italic)

    def A(self, v, p, q, s="", n=1, r=11, d=None, size=11, italic=None, reflex=False):
        V, P, Q = self.T(v), self.T(p), self.T(q)
        if reflex:
            self.reflex(V, P, Q, r=r, n=n)
        else:
            self.angle(V, P, Q, r=r, n=n)
        if s:
            it = italic if italic is not None else (s.replace("°", "").isalpha() or s in "αβγθ")
            self.alab(V, P, Q, s, d=d or r + 13, size=size, italic=it, reflex=reflex)
        return self

    def R(self, v, p, q, s=6):
        return self.right(self.T(v), self.T(p), self.T(q), s=s)

    def SL(self, p, q, s, side=1, d=9, t=0.5, size=10.5, italic=None):
        """Label s beside segment pq (model points), on side +1 (left of p->q on the page) or -1."""
        P, Q = self.T(p), self.T(q)
        mx, my = P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])
        Lq = hypot(Q[0] - P[0], Q[1] - P[1])
        nx, ny = (Q[1] - P[1]) / Lq, -(Q[0] - P[0]) / Lq
        it = italic if italic is not None else s.isalpha()
        return self.text(mx + side * d * nx, my + side * d * ny, s, size=size, italic=it)

    def DIM(self, p, q, s, off=12, side=1, size=10.5, italic=None):
        """Dimension line parallel to pq, offset by off px, arrowheads both ends, label s at its middle."""
        P, Q = self.T(p), self.T(q)
        Lq = hypot(Q[0] - P[0], Q[1] - P[1])
        nx, ny = side * (Q[1] - P[1]) / Lq, -side * (Q[0] - P[0]) / Lq
        a = (P[0] + off * nx, P[1] + off * ny)
        b = (Q[0] + off * nx, Q[1] + off * ny)
        self.arrow(a[0], a[1], b[0], b[1], "faint", 0.9, 5)
        self.arrow(b[0], b[1], a[0], a[1], "faint", 0.9, 5)
        it = italic if italic is not None else s.isalpha()
        self.text((a[0] + b[0]) / 2 + 9 * nx, (a[1] + b[1]) / 2 + 9 * ny, s, size=size, italic=it)
        return self


# ---------------------------------------------------------------- Concept 1: tangent and radius
def concept1():
    # AMSI p18: secant, tangent, missing line
    f = G(420, 110)
    for k, (kind, cx) in enumerate((("secant", 70), ("tangent", 210), ("miss", 350))):
        c, r = (cx, 66), 38
        f.circle(c, r)
        if kind == "secant":
            f.seg((cx - 62, 82), (cx + 50, 36)).text(cx + 40, 26, "secant", size=10, italic=False)
        elif kind == "tangent":
            t = CF.on(c, r, 105)
            d = (cos(radians(15)), -sin(radians(15)))
            f.seg((t[0] - 62 * d[0], t[1] - 62 * d[1]), (t[0] + 62 * d[0], t[1] + 62 * d[1])).text(cx + 34, 14, "tangent", size=10, italic=False)
        else:
            f.seg((cx - 50, 26), (cx + 56, 6))
    save("c3_three", f)

    # AMSI p19 proof a, c: tangent l at T perpendicular to OT, P another point of l
    f = G(150, 130).frame([(-1.2, -1.05), (1.15, 1.45)], pad=10)
    O, T = (0.25, -0.1), None
    T = onm(O, 1, 140)
    u = unit(rot(sub(T, O), 90))
    P = add(T, u, -1.15)
    f.C(O, 1).S(O, T).S(add(T, u, 0.7), add(T, u, -1.45)).S(O, P, dash="4 3", width=1.2).R(T, O, P)
    f.D(O).O(T, O, "T").L(P, "P", dx=8, dy=-4)
    save("c3_tproof1", f)
    # proof b: t not perpendicular, M foot of perpendicular, U with UM = MT
    f = G(190, 120).frame([(-0.95, -0.15), (1.0, 1.0)], pad=12)
    O = (0.0, 0.0)
    T = onm(O, 1, 150)
    d = unit((cos(radians(14)), sin(radians(14))))   # line t through T, not perpendicular to OT
    M = foot(O, T, add(T, d))
    U = add(M, sub(M, T))
    f.items.append("")
    pa, pb = f.T(onm(O, 1, 100)), f.T(onm(O, 1, 205))
    cc = f.T(O)
    rr = f.s
    f.raw(f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{rr:.1f},{rr:.1f} 0 0 0 {pb[0]:.1f},{pb[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.6"/>')
    f.S(add(T, d, -0.3), add(U, d, 0.35)).S(O, T).S(O, M).S(O, U, dash="4 3", width=1.2).R(M, U, O)
    f.tick(f.T(T), f.T(M), n=2).tick(f.T(M), f.T(U), n=2)
    f.D(O).D(T).L(O, "O", dx=0, dy=12).L(T, "T", dx=-2, dy=-9).L(M, "M", dx=0, dy=-9).L(U, "U", dx=2, dy=-9)
    f.L(add(T, d, -0.3), "t", dx=-4, dy=-9)
    save("c3_tproof2", f)
    # MP box: angle between tangent and radius
    f = G(150, 110).frame([(-1.6, -1.15), (1.6, 1.05)], pad=8)
    O = (0, 0)
    T = (0, -1)
    f.C(O, 1).S(O, T).S((-1.5, -1), (1.5, -1)).D(O).R(T, O, (1, -1)).text(f.T(T)[0] + 18, f.T(T)[1] - 9, "90°", size=10)
    save("c3_mpbox", f)

    # MP Q7 a, b: measure the angle (exact right angles)
    for nm, deg in (("c3q7a", 270), ("c3q7b", 135)):
        f = G(150, 130).frame([(-1.55, -1.25), (1.55, 1.25)], pad=8)
        O = (0, 0)
        T = onm(O, 1, deg)
        u = unit(rot(sub(T, O), 90))
        f.C(O, 1).S(O, T).S(add(T, u, -1.3), add(T, u, 1.3)).D(O).A(T, O, add(T, u, 1), "", n=1 if nm.endswith("a") else 2, r=10)
        save(nm, f)

    # MP Q8 a, b and demos: x + 37 = 90 (chord-free: a line from T making 37 deg with the tangent)
    def q8a(nm, given, var):
        f = G(170, 130).frame([(-1.3, -1.25), (2.4, 1.2)], pad=8)
        O = (0, 0)
        T = (0, -1)
        q = add(T, (cos(radians(given)), sin(radians(given))), 2.6)
        f.C(O, 1).S(O, T).S((-1.25, -1), (1.7, -1)).S(T, q).D(O)
        f.A(T, O, q, var, n=2, r=12, d=24).A(T, (1.7, -1), q, f"{given}°", r=18, d=40)
        save(nm, f)
    q8a("c3q8a", 37, "x")
    q8a("c3d1a", 42, "x")
    q8a("c3y1a", 33, "x")

    def q8b(nm, given, var):
        f = G(170, 140).frame([(-1.6, -1.2), (1.3, 1.5)], pad=8)
        O = (0.25, -0.15)
        T = onm(O, 1, 135)
        u = unit(rot(sub(T, O), 90))
        down = add(T, (0, -1), 1.9)            # a line from T going straight down, as on the sheet
        f.C(O, 1).S(O, T).S(add(T, u, -0.9), add(T, u, 0.9)).S(T, add(T, (0, 1), 0.05)).S(T, down).D(O)
        f.A(T, add(T, u, -1), down, var, n=2, r=10, d=20).A(T, down, O, f"{given}°", r=15, d=30)
        save(nm, f)
    # MP Q8(b): angle between the vertical line and the radius is 31, y between tangent and vertical line
    f = G(170, 140).frame([(-1.6, -1.25), (1.3, 1.5)], pad=8)
    O = (0.0, 0.0)
    T = onm(O, 1, 124)                         # direction of TO is 304 deg; vertical down is 270 deg: 34 deg apart
    T = onm(O, 1, 90 + 31)                     # radius TO makes 31 deg with the downward vertical through T
    u = unit(rot(sub(T, O), 90))
    down = add(T, (0, -1), 2.0)
    f.C(O, 1).S(O, T).S(add(T, u, -0.9), add(T, u, 0.9)).S(T, down).D(O)
    tl = add(T, u, 1) if add(T, u, 1)[0] < T[0] else add(T, u, -1)
    f.A(T, tl, down, "y", n=2, r=10, d=19).A(T, down, O, "31°", r=15, d=31)
    save("c3q8b", f)

    # Pythagoras demo: radius r, tangent from P, OP given (our own)
    for nm, r_, op in (("c3d1b", 5, 13), ("c3y1b", 8, 17)):
        f = G(190, 110).frame([(-1.2, -1.1), (op / r_ + 0.2, 1.1)], pad=10)
        O = (0, 0)
        P = (op / r_, 0)
        a = acos(r_ / op)
        T = (cos(a), sin(a))
        f.C(O, 1).S(O, T).S(T, P).S(O, P).D(O).D(P).R(T, O, P)
        f.L(O, "O", dx=-9, dy=2).O(T, O, "T").L(P, "P", dx=9, dy=2)
        f.SL(O, T, f"{r_} cm", side=1, d=10).SL(O, P, f"{op} cm", side=-1, d=10)
        save(nm, f)


# ---------------------------------------------------------------- Concept 2: tangents from an external point
def concept2():
    # AMSI p19: construction of tangents from P (dashed circle on OP)
    f = G(200, 120).frame([(-2.2, -1.2), (1.1, 1.2)], pad=8)
    O, P = (0, 0), (-2.0, 0)
    M = (-1.0, 0)
    a = acos(0.5)
    T, U = (-cos(a), sin(a)), (-cos(a), -sin(a))
    f.C(O, 1).C(M, 1, dash="4 3", width=1.1).S(P, O).S(P, T, dash="4 3", width=1.1).S(P, U, dash="4 3", width=1.1)
    f.D(M).D(P).L(O, "O", dx=9, dy=0).L(P, "P", dx=-9, dy=0).L(M, "M", dx=0, dy=12).O(T, M, "T").O(U, M, "U")
    save("c3_constr", f)

    # AMSI Ex 16: quadrilateral with an incircle (A top, B right, C bottom, D left)
    f = G(200, 110).frame([(-2.4, -1.3), (2.4, 1.25)], pad=6)
    O = (0, 0)
    tang = [onm(O, 1, d) for d in (65, 115, 245, 295)]

    def tl(d1, d2):
        p1, p2 = onm(O, 1, d1), onm(O, 1, d2)
        return inter(p1, add(p1, rot(p1, 90)), p2, add(p2, rot(p2, 90)))
    A, D, C, B = tl(65, 115), tl(115, 245), tl(245, 295), tl(295, 65)
    f.C(O, 1).poly([f.T(A), f.T(B), f.T(C), f.T(D)], color=None, opacity=0)
    f.L(A, "A", dy=-8).L(B, "B", dx=9).L(C, "C", dy=13).L(D, "D", dx=-9)
    save("c3_ex16", f)

    # AMSI p20: direct and indirect common tangents
    f = G(420, 132)
    c1, r1, c2, r2 = (60, 70), 40, (165, 82), 26
    f.circle(c1, r1).circle(c2, r2)
    # direct tangent (above both)
    d = hypot(c2[0] - c1[0], c2[1] - c1[1])
    base = atan2(c2[1] - c1[1], c2[0] - c1[0])
    phi = acos((r1 - r2) / d)
    n = (cos(base - phi), sin(base - phi))
    p1 = (c1[0] + r1 * n[0], c1[1] + r1 * n[1])
    p2 = (c2[0] + r2 * n[0], c2[1] + r2 * n[1])
    f.seg(ext(p1, p2, -0.9), ext(p1, p2, 1.5), width=1.4)
    f.text(90, 128, "Direct common tangent", size=10, italic=False, color="faint")
    c1, r1, c2, r2 = (270, 66), 40, (370, 52), 24
    f.circle(c1, r1).circle(c2, r2)
    d = hypot(c2[0] - c1[0], c2[1] - c1[1])
    base = atan2(c2[1] - c1[1], c2[0] - c1[0])
    phi = acos((r1 + r2) / d)
    n = (cos(base - phi), sin(base - phi))
    p1 = (c1[0] + r1 * n[0], c1[1] + r1 * n[1])
    p2 = (c2[0] - r2 * n[0], c2[1] - r2 * n[1])
    f.seg(ext(p1, p2, -0.9), ext(p1, p2, 1.6), width=1.4)
    f.text(330, 128, "Indirect common tangent", size=10, italic=False, color="faint")
    save("c3_common", f)

    # AMSI p21: circles touching externally and internally at T
    f = G(300, 110)
    for (c1, r1, c2, r2, tx) in (((50, 55), 42, (124, 55), 32, 92), ((210, 55), 42, (226, 55), 26, 252)):
        f.circle(c1, r1).circle(c2, r2).seg((tx, 8), (tx, 102), width=1.3).pdot((tx, 55), 2.2).text(tx + 7, 22, "T", size=11, italic=True)
    save("c3_touch", f)

    # AMSI p21: incentre of a triangle, bisectors marked
    f = G(260, 150).frame([(0, 0), (6, 3.3)], pad=12)
    A, B, C = (0, 0), (2.0, 3.0), (6.0, 0)
    a, b, c = hypot(*sub(B, C)), hypot(*sub(A, C)), hypot(*sub(A, B))
    I = ((a * A[0] + b * B[0] + c * C[0]) / (a + b + c), (a * A[1] + b * B[1] + c * C[1]) / (a + b + c))
    rI = abs(I[1])
    f.C(I, rI).poly([f.T(A), f.T(B), f.T(C)], color=None, opacity=0).S(A, I).S(B, I).S(C, I).D(I)
    for v, p, q, s in ((A, C, I, "α"), (A, I, B, "α"), (B, A, I, "β"), (B, I, C, "β"), (C, I, A, "γ"), (C, B, I, "γ")):
        f.A(v, p, q, "", r=16)
        f.alab(f.T(v), f.T(p), f.T(q), s, d=(46 if v is C else 30), size=9.5, italic=True)
    f.L(A, "A", dx=-8, dy=5).L(B, "B", dy=-8).L(C, "C", dx=8, dy=5).L(I, "I", dx=6, dy=-7)
    save("c3_incentre", f)
    # Exercise 18: feet L, M, N of the perpendiculars from I
    f = G(260, 140).frame([(0, 0), (6, 3.0)], pad=12)
    A, B, C = (0, 0), (2.4, 2.8), (6.0, 0)
    a, b, c = hypot(*sub(B, C)), hypot(*sub(A, C)), hypot(*sub(A, B))
    I = ((a * A[0] + b * B[0] + c * C[0]) / (a + b + c), (a * A[1] + b * B[1] + c * C[1]) / (a + b + c))
    Lf, Mf, Nf = foot(I, B, C), foot(I, C, A), foot(I, A, B)
    f.poly([f.T(A), f.T(B), f.T(C)], color=None, opacity=0).S(A, I).S(B, I).S(C, I, dash="4 3", width=1.1)
    for Fp, p in ((Lf, C), (Mf, C), (Nf, B)):
        f.S(I, Fp, dash="4 3", width=1.1).R(Fp, p, I, s=5)
    f.A(A, C, I, "α", r=18, d=34, size=9.5).A(A, I, B, "α", r=18, d=34, size=9.5).A(B, A, I, "β", r=14, d=26, size=9.5).A(B, I, C, "β", r=14, d=26, size=9.5)
    f.L(A, "A", dx=-8, dy=5).L(B, "B", dy=-8).L(C, "C", dx=8, dy=5).L(Lf, "L", dx=8, dy=-4).L(Mf, "M", dy=12).L(Nf, "N", dx=-9, dy=-3)
    save("c3_ex18", f)

    # MP Q9(a) and demos: tangents AB (at B) and AC (at C), angle CAB given
    def q9a(nm, given, lab=True):
        f = G(170, 130).frame([(-2.6, -1.2), (1.25, 1.8)], pad=10)
        O = (0, 0)
        B = (0, -1)
        hb = radians(given / 2)
        A = (-1 / tan(hb), -1)
        Cp = onm(O, 1, 270 - (180 - given))
        Cp = onm(O, 1, -90 - (180 - given))
        f.C(O, 1).S(A, (1.2, -1)).S(A, add(A, sub(Cp, A), 1.5)).S(O, B).S(O, Cp).D(O).D(A).D(B).D(Cp)
        f.L(A, "A", dx=-4, dy=13, italic=False).L(B, "B", dy=13, italic=False).O(Cp, A, "C", d=10, italic=False).L(O, "O", dx=9, dy=-2, italic=False)
        save(nm, f)
    q9a("c3q9a", 70)
    q9a("c3d2a", 64)
    q9a("c3y2a", 52)
    # MP Q9(b): AB tangent at B (line ABD), BC chord, O on AC, angle CBD = 60
    f = G(200, 110).frame([(-3.2, -1.15), (1.6, 1.2)], pad=10)
    O = (0, 0)
    B = (0, -1)
    Cp = onm(O, 1, 30)                          # angle CBD = 60 deg: C on the circle with BC at 60 deg to BD
    A = inter(Cp, O, (-5, -1), (5, -1))
    D_ = (1.5, -1)
    f.C(O, 1).S(add(A, (-0.25, 0)), D_).S(A, Cp).S(O, B).S(B, Cp).D(O).D(A).D(B).D(Cp).D(D_)
    f.L(A, "A", dy=13, italic=False).L(B, "B", dy=13, italic=False).L(D_, "D", dy=13, italic=False).O(Cp, O, "C", italic=False).L(O, "O", dx=-2, dy=-10, italic=False)
    save("c3q9b", f)
    # demo / your turn: two tangents PA, PB, angle PAB given (our own)
    for nm, g in (("c3d2b", 66), ("c3y2b", 74)):
        f = G(190, 120).frame([(-1.2, -1.2), (2.9, 1.2)], pad=10)
        O = (0, 0)
        A, B = onm(O, 1, 90 - (90 - g) * 0 - 0), None
        th = 2 * g                                 # angle AOB at the centre (tangent-chord angle g = half of it)
        A, B = onm(O, 1, th / 2), onm(O, 1, -th / 2)
        P = (1 / cos(radians(th / 2)), 0)
        f.C(O, 1).S(P, A).S(P, B).S(A, B).D(P)
        f.A(A, B, P, f"{g}°", r=12, d=26).O(A, O, "A").O(B, O, "B").L(P, "P", dx=12, dy=-6)
        save(nm, f)


# ---------------------------------------------------------------- Concept 3: alternate segment theorem
def concept3():
    # AMSI p22: three diagrams, Q moving to A
    for nm, qd in (("c3_as1", 160), ("c3_as2", 205), ("c3_as3", None)):
        f = G(140, 130).frame([(-1.25, -1.45), (1.6, 1.25)], pad=6)
        O = (0, 0)
        P, B, A = onm(O, 1, 95), onm(O, 1, -5), onm(O, 1, 265)
        tdir = unit(rot(sub(A, O), 90))
        if tdir[0] < 0:
            tdir = (-tdir[0], -tdir[1])
        f.C(O, 1).S(P, A).S(P, B).S(A, B).A(P, A, B, "", r=11)
        if qd is not None:
            Q = onm(O, 1, qd)
            Ue = add(A, sub(A, Q), 0.45)
            f.S(Q, B).S(Q, Ue).A(Q, A, B, "", r=11)
            f.O(Q, O, "Q").L(Ue, "U", dx=6, dy=8)
        else:
            Ue = add(A, tdir, 0.85)
            f.S(A, Ue).A(A, B, Ue, "", r=12).L(Ue, "U", dx=8, dy=2)
        f.O(P, O, "P").O(B, O, "B").O(A, O, "A")
        save(nm, f)
    # theorem figure
    f = G(150, 130).frame([(-1.2, -1.2), (1.9, 1.15)], pad=6)
    O = (0, 0)
    P, B, A = onm(O, 1, 120), onm(O, 1, 10), onm(O, 1, 270)
    f.C(O, 1).S(P, A).S(P, B).S(A, B).S(A, (1.75, -1)).A(P, A, B, "", r=11).A(A, B, (1.75, -1), "", r=12)
    f.O(P, O, "P").O(B, O, "B").O(A, O, "A").L((1.75, -1), "U", dx=8, dy=2)
    save("c3_asthm", f)

    # three cases (chord AB, tangent BU at B, P on the far arc)
    def case(nm, adeg, pdeg, dashed=False, radii=False):
        f = G(140, 130).frame([(-1.2, -1.2), (1.75, 1.2)], pad=6)
        O = (0, 0)
        B = (0, -1)
        A, P = onm(O, 1, adeg), onm(O, 1, pdeg)
        D_ = (0, 1)
        f.C(O, 1).S(P, A).S(P, B).S(A, B).S(B, (1.6, -1)).D(O)
        if dashed:
            f.S(B, D_, dash="4 3", width=1.1).S(D_, A, dash="4 3", width=1.1).O(D_, O, "D")
        if radii:
            f.S(O, A, dash="4 3", width=1.1).S(O, B, dash="4 3", width=1.1)
        f.A(P, A, B, "α", r=10, d=19)
        f.O(P, O, "P").O(B, O, "B").O(A, O, "A").L((1.6, -1), "U", dx=8, dy=2).L(O, "O", dx=8, dy=-2)
        save(nm, f)
    case("c3_case1", 90, 165)
    case("c3_case2", 10, 140, dashed=True)
    case("c3_case3", 155, 200, dashed=True)
    case("c3_ex19a", 10, 140, radii=True)
    case("c3_ex19b", 155, 200, radii=True)

    # Exercise 20: circles touching at T, common tangent STU; AQ and BP straight lines through T
    f = G(220, 150).frame([(-2.3, -1.45), (1.75, 1.45)], pad=8)
    T = (0, 0)
    c1, r1 = (-1.15, 0.2), None
    r1 = hypot(*c1)
    u = unit(sub(T, c1))
    r2 = 0.7
    c2 = add(T, u, r2)
    tdir = rot(u, 90)
    A = onm(c1, r1, 120)
    B = onm(c1, r1, 255)
    dA = unit(sub(T, A))
    dB = unit(sub(T, B))
    tq = line_circle(T, dA, c2, r2)
    Q = add(T, dA, max(tq))
    tp = line_circle(T, dB, c2, r2)
    Pp = add(T, dB, max(tp))
    f.C(c1, r1).C(c2, r2).S(A, Q).S(B, Pp).S(A, B).S(Pp, Q).S(add(T, tdir, 1.35), add(T, tdir, -1.35))
    f.A(A, B, T, "α", r=10, d=19)
    f.L(A, "A", dx=-6, dy=-8).L(B, "B", dx=-2, dy=13).L(Q, "Q", dx=9, dy=4).L(Pp, "P", dx=6, dy=-8).L(T, "T", dx=9, dy=8)
    f.L(add(T, tdir, 1.35), "S", dx=6, dy=-4).L(add(T, tdir, -1.35), "U", dx=-6, dy=8)
    save("c3_ex20", f)

    # demos (our own): tangent at A, chord AB, angle between = g; P in the alternate segment
    def asdemo(nm, g, mark_at):
        f = G(160, 140).frame([(-1.25, -1.25), (1.9, 1.2)], pad=8)
        O = (0, 0)
        A = (0, -1)
        B = onm(O, 1, 270 + 2 * g)             # tangent-chord angle g at A
        P = onm(O, 1, 270 + 2 * g + 0.55 * (360 - 2 * g))
        U = (1.75, -1)
        f.C(O, 1).S(P, A).S(P, B).S(A, B).S((-1.0, -1), U)
        if mark_at == "A":
            f.A(A, B, U, f"{g}°", r=14, d=30).A(P, A, B, "x", r=11, d=21)
        else:
            f.A(P, A, B, f"{g}°", r=11, d=26).A(A, B, U, "y", r=14, d=26)
        f.O(P, O, "P").O(B, O, "B").O(A, O, "A").L(U, "U", dx=8, dy=2)
        save(nm, f)
    asdemo("c3d3a", 58, "A")
    asdemo("c3d3b", 47, "P")
    asdemo("c3y3a", 64, "A")
    asdemo("c3y3b", 39, "P")


# ---------------------------------------------------------------- Concepts 4 and 5: chords, secants, tangent-secant
def chords_fig(nm, a1, b1, a2, b2, phi, labels, w=160, h=140, rot0=0, lab_side=(1, 1, 1, 1), dots=True, letters=None, centre=True,
               note=None, exact=True):
    """Two chords through M: chord 1 with intercepts a1 (towards p1) and b1, chord 2 with a2, b2, at angle phi.
    labels: four strings for the segments (Mp1, Mq1, Mp2, Mq2), '' to skip."""
    M = (0.0, 0.0)
    if exact:
        assert abs(a1 * b1 - a2 * b2) < 1e-9, nm  # given lengths satisfy the theorem
    b2 = a1 * b1 / a2                             # (illustrative figures: the fourth length is computed)
    d1 = rot((1, 0), rot0)
    d2 = rot(d1, phi)
    p1, q1 = add(M, d1, -a1), add(M, d1, b1)
    p2, q2 = add(M, d2, -a2), add(M, d2, b2)
    c, r = circum(p1, q1, p2)
    assert abs(hypot(*sub(q2, c)) - r) < 1e-9 * r
    f = G(w, h).frame([add(c, (-r, -r)), add(c, (r, r))], pad=12)
    f.C(c, r).S(p1, q1).S(p2, q2)
    if dots:
        for p in (p1, q1, p2, q2, M):
            f.D(p, 2)
    if centre:
        f.D(c, 2.2)
    for (p, q), s, sd in zip(((p1, M), (M, q1), (p2, M), (M, q2)), labels, lab_side):
        if s:
            f.SL(p, q, s, side=sd, d=9, size=10.5)
    if letters:
        for k, p in zip(("p1", "q1", "p2", "q2", "M"), (p1, q1, p2, q2, M)):
            if letters.get(k):
                if k == "M":
                    f.L(p, letters[k], dx=letters.get("Mdx", 9), dy=letters.get("Mdy", -6), italic=False)
                else:
                    f.O(p, c, letters[k], italic=False)
    if note:
        note(f, dict(p1=p1, q1=q1, p2=p2, q2=q2, M=M, c=c, r=r))
    save(nm, f)
    return dict(p1=p1, q1=q1, p2=p2, q2=q2, M=M, c=c, r=r)


def secants_fig(nm, o1, w1, o2, w2, phi, w=200, h=140, rot0=180, letters=None, segs=(), dims=None, labs=None, dot_c=True,
                centre_on_1=False, note=None, pad=12, tangent=None, exact=True):
    """Two secants from M: on ray 1 the points at distances o1 (near) and w1 (far); on ray 2 at o2 and w2."""
    M = (0.0, 0.0)
    if exact:
        assert abs(o1 * w1 - o2 * w2) < 1e-9, nm
    w2 = o1 * w1 / o2
    d1 = rot((1, 0), rot0)
    d2 = rot(d1, phi)
    n1, f1 = add(M, d1, o1), add(M, d1, w1)
    n2, f2 = add(M, d2, o2), add(M, d2, w2)
    c, r = circum(n1, f1, n2)
    assert abs(hypot(*sub(f2, c)) - r) < 1e-9 * r, nm
    pts = [add(c, (-r, -r)), add(c, (r, r)), M]
    f = G(w, h).frame(pts, pad=pad)
    f.C(c, r).S(M, f1).S(M, f2)
    for s in segs:
        P = dict(n1=n1, f1=f1, n2=n2, f2=f2, M=M)
        f.S(P[s[0]], P[s[1]], dash=s[2] if len(s) > 2 else None, width=1.2 if len(s) > 2 else 1.6)
    for p in (M, n1, f1, n2, f2):
        f.D(p, 2)
    if dot_c:
        f.D(c, 2.2)
    P = dict(n1=n1, f1=f1, n2=n2, f2=f2, M=M, c=c)
    if letters:
        for k, s in letters.items():
            if k == "M":
                f.L(M, s, dx=letters.get("_Mdx", -9) if False else 0, dy=0, italic=False) if False else None
                f.text(f.T(M)[0] + (10 if d1[0] < 0 else -10), f.T(M)[1] + 4, s, size=11.5)
            elif not k.startswith("_"):
                f.O(P[k], c, s, italic=False)
    if dims:
        for (a, b, s, off, side) in dims:
            f.DIM(P[a], P[b], s, off=off, side=side)
    if labs:
        for (a, b, s, side, d) in labs:
            f.SL(P[a], P[b], s, side=side, d=d)
    if note:
        note(f, P)
    save(nm, f)
    return P


def concept45():
    # MP recall: similar triangles ABC ~ DEF
    f = G(200, 110)
    A, B, Cc = (40, 18), (28, 60), (62, 96)
    k = 1.75
    D, E, Fp = (96, 100), (92, 46), (178, 8)
    f.poly([A, B, Cc], color=None, opacity=0).poly([D, E, Fp], color=None, opacity=0)
    f.lab(A, "A", dy=-7, italic=False).lab(B, "B", dx=-8, italic=False).lab(Cc, "C", dy=12, italic=False)
    f.lab(D, "D", dy=12, italic=False).lab(E, "E", dx=-8, dy=-3, italic=False).lab(Fp, "F", dx=6, dy=-5, italic=False)
    f.angle(A, B, Cc, r=8).angle(B, A, Cc, r=8, n=2).angle(Cc, A, B, r=10, n=3)
    f.angle(D, E, Fp, r=8).angle(E, D, Fp, r=8, n=2).angle(Fp, D, E, r=10, n=3)
    save("c3_sim", f)

    # AMSI p24: intersecting chords AB and PQ at M
    chords_fig("c3_ic1", 1.6, 0.9, 1.15, 1.25, 83, ["", "", "", ""], rot0=20, letters=dict(p1="A", q1="B", p2="P", q2="Q", M="M", Mdx=2, Mdy=12),
               dots=False, centre=False, exact=False)
    chords_fig("c3_ic2", 1.6, 0.9, 1.15, 1.25, 83, ["", "", "", ""], rot0=20, letters=dict(p1="A", q1="B", p2="P", q2="Q", M="M", Mdx=2, Mdy=12),
               dots=False, centre=False, exact=False, note=lambda f, P: (f.S(P["p1"], P["p2"], dash="4 3", width=1.1), f.S(P["q1"], P["q2"], dash="4 3", width=1.1)))
    # MP box: ab = xy
    chords_fig("c3_mpchords", 1.5, 0.45, 0.6, 1.1, 82, ["a", "b", "x", "y"], rot0=-8, lab_side=(1, 1, -1, -1), dots=True, exact=False)

    # MP Q1 (A = chords BD and CE meet)
    chords_fig("c3iq1", 1.05, 0.4, 0.75, 0.55, 76, ["", "", "", ""], rot0=-20, letters=dict(p1="B", q1="D", p2="E", q2="C", M="A", Mdx=9, Mdy=-6), exact=False)
    # MP Q2(a): chords JK and HL meet at I
    chords_fig("c3iq2a", 0.75, 0.65, 1.3, 0.38, 63, ["", "", "", ""], rot0=2, letters=dict(p1="J", q1="K", p2="L", q2="H", M="I", Mdx=4, Mdy=13), exact=False)
    # MP Q2(b): chord 1 = f and t, chord 2 = w and d
    chords_fig("c3iq2b", 0.85, 0.75, 0.45, 1.25, -85, ["f", "t", "w", "d"], rot0=25, lab_side=(1, 1, 1, 1), exact=False)
    # MP Q3 a-d and the demo / your turn (to scale)
    chords_fig("c3iq3a", 6, 10, 5, 12, 25, ["6", "x", "5", "12"], rot0=-10, lab_side=(1, -1, -1, 1))
    chords_fig("c3iq3b", 8, 3, 4, 6, 63, ["8", "3", "4", "y"], rot0=-60, lab_side=(1, 1, 1, 1))
    chords_fig("c3iq3c", 4, 2.25, 3, 3, 90, ["4", "m", "3", "3"], rot0=0, lab_side=(1, 1, -1, -1))
    chords_fig("c3iq3d", 6, 1, 2, 3, 60, ["6", "1", "k", "3"], rot0=0, lab_side=(-1, -1, 1, 1))
    chords_fig("c3d4a", 6, 4, 3, 8, 70, ["6", "4", "3", "x"], rot0=-10, lab_side=(1, 1, 1, 1))
    chords_fig("c3d4b", 5, 8, 10, 4, 50, ["5", "8", "10", "y"], rot0=0, lab_side=(1, 1, -1, -1))
    chords_fig("c3y4a", 9, 2, 3, 6, 65, ["9", "2", "3", "x"], rot0=-10, lab_side=(1, 1, 1, 1))
    chords_fig("c3y4b", 4, 6, 8, 3, 55, ["4", "6", "8", "y"], rot0=0, lab_side=(1, 1, -1, -1))

    # AMSI p25: secants ABM and PQM from M (A far, B near; P far, Q near)
    for nm, segs in (("c3_sec1", ()), ("c3_sec2", (("f1", "f2", "4 3"), ("n1", "n2", "4 3"))), ("c3_ex23", (("f1", "n2", "4 3"), ("n1", "f2", "4 3")))):
        secants_fig(nm, 0.62, 1.65, 0.48, 2.14, 38, rot0=180, letters=dict(n1="B", f1="A", n2="Q", f2="P", M="M"), segs=segs, dot_c=False, w=200, h=120, exact=False)
    # tangent and secant from M: intro (rotating secant) and Exercise 24
    def tsfig(nm, dashed):
        M = (0.0, 0.0)
        o, wv = 0.62, 1.65
        d1 = (-1, 0)
        Bp, Ap = add(M, d1, o), add(M, d1, wv)
        t = sqrt(o * wv)
        # T on a ray at angle phi below, at distance t; circle through A, B, T is then tangent to MT at T
        phi = 52
        d2 = rot(d1, phi)
        T = add(M, d2, t)
        c, r = circum(Ap, Bp, T)
        f = G(200, 130).frame([add(c, (-r, -r)), add(c, (r, r)), M], pad=12)
        f.C(c, r).S(M, Ap).S(M, add(M, d2, t * 1.25))
        for p in (M, Ap, Bp, T):
            f.D(p, 2)
        if dashed == "intro":
            d3 = rot(d1, 38)
            ts = line_circle(M, d3, c, r)
            Q, Pq = add(M, d3, ts[0]), add(M, d3, ts[1])
            f.S(M, Pq, dash="4 3", width=1.1).D(Q, 2).O(Q, c, "Q", italic=False)
        else:
            f.S(Ap, T, dash="4 3", width=1.1).S(Bp, T, dash="4 3", width=1.1)
        f.O(Ap, c, "A", italic=False).O(Bp, c, "B", italic=False).O(T, c, "T", italic=False).L(M, "M", dx=9, dy=2, italic=False)
        save(nm, f)
    tsfig("c3_ts", "intro")
    tsfig("c3_ex24", "ex24")
    # MP box: secants ab = xy with dimension arrows
    secants_fig("c3_mpsec", 0.75, 2.3, 0.85, 2.03, -38, rot0=58, dims=[("M", "f1", "b", 32, 1), ("M", "n1", "a", 13, 1), ("M", "n2", "x", 13, -1), ("M", "f2", "y", 32, -1)],
                w=230, h=190, pad=34, exact=False)
    # MP Q4 (P external; Q, R on one secant; S, T on the other; QS and RT joined)
    secants_fig("c3iq4", 0.95, 2.6, 1.3, 1.9, -22, rot0=28, letters=dict(n1="Q", f1="R", n2="S", f2="T", M="P"),
                segs=(("n1", "n2"), ("f1", "f2")), w=200, h=130, exact=False)
    # MP Q5(a) (E external; F, I on one; G, H on the other; FG and IH joined)
    secants_fig("c3iq5a", 0.85, 2.4, 1.15, 1.77, -22, rot0=35, letters=dict(n1="F", f1="I", n2="G", f2="H", M="E"),
                segs=(("n1", "n2"), ("f1", "f2")), w=170, h=130, exact=False)
    # MP Q5(b): dimension arrows k, p (whole and outer of the upper secant), t, m
    secants_fig("c3iq5b", 0.95, 2.6, 0.8, 3.1, 18, rot0=182, dims=[("M", "f1", "k", 24, -1), ("M", "n1", "p", 11, -1), ("M", "n2", "t", 14, 1), ("M", "f2", "m", 32, 1)],
                segs=(("f1", "f2"),), w=210, h=150, pad=26, exact=False)
    # MP Q6 a-d (to scale) and the demo / your turn
    secants_fig("c3iq6a", 15, 30, 18, 25, -22, rot0=0, dims=[("M", "f1", "x", 24, 1), ("M", "f2", "25", 24, -1)],
                labs=[("M", "n1", "15", 1, 8), ("M", "n2", "18", -1, 8)], w=210, h=130, pad=24)
    secants_fig("c3iq6b", 10, 48, 12, 40, 40, rot0=155, dims=[("M", "f1", "z", 24, -1), ("M", "f2", "40", 24, 1)],
                labs=[("M", "n1", "10", -1, 8), ("M", "n2", "12", 1, 8)], w=190, h=150, pad=24)
    secants_fig("c3iq6c", 5.25, 8, 6, 7, -30, rot0=30, dims=[("M", "f1", "8", 24, 1), ("M", "f2", "7", 22, -1)],
                labs=[("M", "n1", "5.25", 1, 9), ("M", "n2", "t", -1, 8)], w=210, h=130, pad=24)
    cosd = (24 ** 2 + 28 ** 2 - 64) / (2 * 24 * 28)
    secants_fig("c3iq6d", 20, 36, 24, 30, degrees(acos(cosd)), rot0=180, dims=[("M", "f1", "36", 24, -1), ("M", "f2", "30", 22, 1)],
                labs=[("M", "n1", "n", -1, 8), ("M", "n2", "24", 1, 8)], w=220, h=130, pad=24)
    secants_fig("c3d5a", 12, 28, 16, 21, -24, rot0=0, dims=[("M", "f1", "x", 24, 1), ("M", "f2", "21", 24, -1)],
                labs=[("M", "n1", "12", 1, 8), ("M", "n2", "16", -1, 8)], w=210, h=130, pad=24)
    secants_fig("c3y5a", 10, 35, 14, 25, -24, rot0=0, dims=[("M", "f1", "x", 24, 1), ("M", "f2", "25", 24, -1)],
                labs=[("M", "n1", "10", 1, 8), ("M", "n2", "14", -1, 8)], w=210, h=130, pad=24)

    # tangent-secant demo / your turn: MB = o, MA = w, find tangent MT
    for nm, o, wv in (("c3d5b", 4, 9), ("c3y5b", 4, 16)):
        M = (0.0, 0.0)
        d1 = (-1, 0)
        Bp, Ap = add(M, d1, o), add(M, d1, wv)
        t = sqrt(o * wv)
        d2 = rot(d1, 48)
        T = add(M, d2, t)
        c, r = circum(Ap, Bp, T)
        f = G(210, 130).frame([add(c, (-r, -r)), add(c, (r, r)), M], pad=14)
        f.C(c, r).S(M, Ap).S(M, add(M, d2, t * 1.2))
        for p in (M, Ap, Bp, T):
            f.D(p, 2)
        f.O(Ap, c, "A").O(Bp, c, "B", d=12).O(T, c, "T").L(M, "M", dx=9, dy=2)
        f.SL(M, Bp, f"{o}", side=-1, d=8).SL(Bp, Ap, f"{wv - o}", side=-1, d=8)
        save(nm, f)

    # AMSI Ex 25: three circles, common chords AB, PQ, ST
    f = G(200, 130).frame([(-2.1, -1.55), (2.3, 1.45)], pad=6)
    c1, r1 = (-0.95, 0.3), 1.15
    c2, r2 = (0.95, 0.25), 1.1
    c3, r3 = (0.1, -0.75), 0.8

    def meet(ca, ra, cb, rb):
        d = hypot(*sub(cb, ca))
        a = (ra * ra - rb * rb + d * d) / (2 * d)
        h = sqrt(ra * ra - a * a)
        u = unit(sub(cb, ca))
        m = add(ca, u, a)
        n = rot(u, 90)
        return add(m, n, h), add(m, n, -h)
    A1, B1 = meet(c1, r1, c2, r2)
    P1, Q1 = meet(c2, r2, c3, r3)
    S1, T1 = meet(c1, r1, c3, r3)
    f.C(c1, r1).C(c2, r2).C(c3, r3)
    f.L(A1, "A", dx=4, dy=-8).L(B1, "B", dx=2, dy=12).L(P1, "P", dx=8, dy=-2).L(Q1, "T", dx=4, dy=12).L(S1, "S", dx=-8, dy=-2).L(T1, "Q", dx=-4, dy=12)
    save("c3_ex25", f)


# ---------------------------------------------------------------- past papers
def pastpapers():
    # PP1 Baulkham Hills 2020 Q9: tangents at A and B meet at T; P on the circle; chords AP, PB; centre O
    f = G(230, 140).frame([(-2.75, -1.25), (1.5, 1.6)], pad=6)
    O = (0, 0)
    A, B = onm(O, 1, 120), onm(O, 1, 250)
    T = inter(A, add(A, rot(A, 90)), B, add(B, rot(B, 90)))
    P = onm(O, 1, 60)
    f.C(O, 1, width=1.2).S(T, add(T, sub(A, T), 1.9), width=1.2).S(T, add(T, sub(B, T), 1.5), width=1.2).S(A, P, width=1.2).S(P, B, width=1.2)
    f.D(O).D(A).D(B).D(P)
    f.L(O, "O", dy=-9, italic=True).L(A, "A", dx=-6, dy=-8).L(B, "B", dy=13).L(P, "P", dx=9, dy=-4).L(T, "T", dx=-9, dy=2)
    f.A(T, A, B, "θ", r=12, d=22)
    save("c3pp1", f)
    # PP2 Girraween 2020 Q16: AB tangent at A, BC = 2, CD = 5 (exact)
    M = (0.0, 0.0)
    d1 = rot((-1, 0), -25)
    Cp, Dp = add(M, d1, 2), add(M, d1, 7)
    t = sqrt(14)
    d2 = rot(d1, 34)
    Ap = add(M, d2, t)
    c, r = circum(Cp, Dp, Ap)
    f = G(160, 110).frame([add(c, (-r, -r)), add(c, (r, r)), M], pad=10)
    f.C(c, r, width=1.2).S(M, Ap, width=1.2).S(M, Dp, width=1.2)
    f.O(Ap, c, "A", d=8).L(M, "B", dx=8, dy=0).O(Cp, c, "C", d=-8).O(Dp, c, "D", d=9)
    save("c3pp2", f)
    # PP3 Girraween 2020 Q17: chords 4 (top) and 6 (bottom); 5 and x (NOT TO SCALE)
    chords_fig("c3pp3", 6, 4, 4.8, 5, -60, ["6", "4", "x", "5"], rot0=95, lab_side=(1, 1, 1, 1), dots=False, centre=False, w=120, h=110)
    # PP4 Sydney Boys 2022 Part B Q3: tangents PA, PB; 71 deg at A between AB and AP
    f = G(220, 120).frame([(-1.1, -1.05), (2.95, 1.05)], pad=10)
    O = (0, 0)
    g = 71
    A, B = onm(O, 1, g), onm(O, 1, -g)
    P = (1 / cos(radians(g)), 0)
    f.C(O, 1, width=1.2).S(A, P, width=1.2).S(B, P, width=1.2).S(A, B, width=1.2)
    f.A(A, B, P, "71°", r=11, d=22).L(A, "A", dy=-8).L(B, "B", dy=13).L(P, "P", dx=9, dy=2)
    save("c3pp4", f)
    # PP5 Sydney Boys 2020 Q21: tangent AB at T; P, Q, R on the circle; angle BTQ = 70
    f = G(170, 160).frame([(-1.45, -2.0), (1.15, 1.35)], pad=8)
    O = (0, 0)
    Tt = onm(O, 1, 180)
    Qq = onm(O, 1, 180 + 2 * 70 - 180) if False else onm(O, 1, 180 + 140)   # tangent-chord angle 70 -> arc TQ = 140
    Pp = onm(O, 1, 60)
    Rr = onm(O, 1, 285)
    up = rot(sub(Tt, O), 90)                 # tangent direction at T
    tA = add(Tt, unit(up), -1.05) if add(Tt, unit(up), -1.05)[1] > 0 else add(Tt, unit(up), 1.05)
    tB = add(Tt, sub(Tt, tA), 1.6)
    tA = add(Tt, sub(tA, Tt), 0.95)
    f.C(O, 1, color="blue", width=1.2).S(tA, tB, color="blue", width=1.1)
    for p, q in ((Tt, Pp), (Pp, Qq), (Tt, Qq), (Tt, Rr), (Rr, Qq)):
        f.S(p, q, color="blue", width=1.1)
    f.A(Tt, tB, Qq, "70°", r=14, d=28).A(Pp, Tt, Qq, "α", r=9, d=17).A(Rr, Tt, Qq, "β", r=9, d=17)
    f.L(tA, "A", dx=-8, dy=-2).L(tB, "B", dx=0, dy=13).L(Tt, "T", dx=-11, dy=2).O(Pp, O, "P").O(Qq, O, "Q").O(Rr, O, "R")
    save("c3pp5", f)
    # PP6 Baulkham Hills 2020 Q20: secants from P: x outside then 3 inside; 4 outside then 6 inside (exact with x = 5)
    secants_fig("c3pp6", 5, 8, 4, 10, 30, rot0=195, labs=[("M", "n1", "x", -1, 8), ("n1", "f1", "3", -1, 8), ("M", "n2", "4", 1, 8), ("n2", "f2", "6", 1, 8)],
                letters=dict(M="P"), dot_c=False, w=200, h=130)
    # PP7 Girraween 2020 Q25(a): C, R, Q on the circle, O centre, angle RCQ = 70; tangents at R and Q meet at P
    f = G(220, 140).frame([(-1.15, -1.2), (2.4, 1.2)], pad=10)
    O = (0, 0)
    R, Q = onm(O, 1, 70), onm(O, 1, -70)
    Cc = onm(O, 1, 160)
    P = (1 / cos(radians(70)), 0)
    f.C(O, 1).S(Cc, R).S(Cc, Q).S(O, R).S(O, Q).S(R, P).S(Q, P)
    f.S(R, add(R, sub(R, P), 0.18)).S(Q, add(Q, sub(Q, P), 0.18))
    f.A(Cc, R, Q, "70°", r=12, d=26).A(O, R, Q, "a°", r=9, d=19).A(P, R, Q, "b°", r=12, d=24)
    f.O(Cc, O, "C", italic=False).O(R, O, "R", italic=False).O(Q, O, "Q", italic=False).L(P, "P", dx=9, dy=2, italic=False).L(O, "O", dx=-9, dy=0, italic=False)
    save("c3pp7", f)
    # PP8 Sydney Boys 2024 Part C Q7: incircle of triangle STU, S = 34, angle QPT = 46 => T = 88, U = 58
    Sv = (0.0, 0.0)
    angS, angT = 34.0, 88.0
    Tv = (5.0, 0.0)
    Uv = inter(Sv, rot((1, 0), angS), Tv, add(Tv, rot((-1, 0), -angT)))
    a, b, c = hypot(*sub(Tv, Uv)), hypot(*sub(Sv, Uv)), hypot(*sub(Sv, Tv))
    I = ((a * Sv[0] + b * Tv[0] + c * Uv[0]) / (a + b + c), (a * Sv[1] + b * Tv[1] + c * Uv[1]) / (a + b + c))
    rI = I[1]
    Pv, Qv, Rv = foot(I, Sv, Tv), foot(I, Tv, Uv), foot(I, Sv, Uv)
    Vv = inter(Rv, Qv, Sv, Tv)
    f = G(260, 130).frame([Sv, Tv, Uv, Vv], pad=14)
    f.C(I, rI).S(Sv, Vv).S(Sv, Uv).S(Tv, Uv).S(Rv, Vv).S(Pv, Qv)
    f.A(Vv, Sv, Rv, "", r=16)
    f.L(Sv, "S", dx=-8, dy=4).L(Tv, "T", dy=13).L(Uv, "U", dy=-8).L(Pv, "P", dy=13).L(Qv, "Q", dx=8, dy=-4).L(Rv, "R", dx=-6, dy=-8).L(Vv, "V", dx=9, dy=2)
    save("c3pp8", f)


def hard_sb23():
    # Sydney Boys 2023 Part F Q3: circles C1, C2 meet at P; tangents PQ (to C2) and PR (to C1); AD || PQ, BC || PR
    O1, r1 = (0.0, 0.0), 1.0
    O2, r2 = (0.95, -1.05), 0.68
    d = hypot(*sub(O2, O1))
    aa = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = sqrt(r1 * r1 - aa * aa)
    u = unit(sub(O2, O1))
    m = add(O1, u, aa)
    P1, P2 = add(m, rot(u, 90), h), add(m, rot(u, 90), -h)
    P = P1 if P1[0] < P2[0] else P2
    tq = unit(rot(sub(P, O2), 90))                # tangent to C2 at P
    if tq[1] < 0:
        tq = (-tq[0], -tq[1])
    ts = line_circle(P, tq, O1, r1)
    Q = add(P, tq, max(ts))
    tr = unit(rot(sub(P, O1), 90))                # tangent to C1 at P
    if tr[0] < 0:
        tr = (-tr[0], -tr[1])
    ts = line_circle(P, tr, O2, r2)
    R = add(P, tr, max(ts))
    D, A = add(O1, tq, r1), add(O1, tq, -r1)
    Cc, B = add(O2, tr, r2), add(O2, tr, -r2)
    X, Y = add(P, tr, -0.55), add(P, tq, -0.45)
    f = G(250, 230).frame([add(O1, (-r1, -r1)), add(O1, (r1, r1)), add(O2, (r2, -r2)), X, Y], pad=12)
    f.C(O1, r1).C(O2, r2).S(A, D).S(B, Cc).S(Y, add(Q, tq, 0.25)).S(X, add(R, tr, 0.2))
    f.S(A, P, dash="4 3", width=1.1).S(D, P, dash="4 3", width=1.1)
    f.parr(f.T(A), f.T(D), t=0.62).parr(f.T(P), f.T(Q), t=0.7).parr(f.T(B), f.T(Cc), n=2, t=0.62).parr(f.T(P), f.T(R), n=2, t=0.75)
    for p in (A, D, P, Q, R, B, Cc, X, Y, O1, O2):
        f.D(p, 2)
    f.L(A, "A", dx=-2, dy=12).L(D, "D", dy=-8).L(Q, "Q", dx=9, dy=0).L(R, "R", dx=2, dy=-9).L(Cc, "C", dx=9, dy=0).L(B, "B", dx=-4, dy=12)
    f.L(P, "P", dx=8, dy=10).L(X, "X", dx=-2, dy=12).L(Y, "Y", dx=6, dy=10)
    f.L(add(O1, (-0.72, 0.72)), "𝒞₁", dx=-8, dy=-6, italic=False).L(add(O2, (0.5, -0.5)), "𝒞₂", dx=10, dy=8, italic=False)
    save("c3hd1", f)


def review():
    # R1 Sydney Boys 2020 Q34: perpendicular chords AB, CD meet at P; AP = 6, PB = 4, CP = 2 (exact: PD = 12)
    P = (0.0, 0.0)
    dAB = rot((1, 0), 27)
    A, B = add(P, dAB, -6), add(P, dAB, 4)
    dCD = rot(dAB, -90)
    Cc, D = add(P, dCD, -2), add(P, dCD, 12)
    c, r = circum(A, B, Cc)
    f = G(220, 220).frame([add(c, (-r, -r)), add(c, (r, r))], pad=12)
    f.C(c, r, width=1.2).S(A, B, width=1.2).S(Cc, D, width=1.2).R(P, B, Cc, s=7).D(c, 2)
    f.L(c, "O", dy=12).O(A, c, "A", italic=True).O(B, c, "B").O(Cc, c, "C").O(D, c, "D").L(P, "P", dx=2, dy=13)
    f.SL(A, P, "6", side=-1, d=9).SL(P, B, "4", side=-1, d=9).SL(Cc, P, "2", side=1, d=8)
    save("c3r1", f)
    # R2 Sydney Boys 2021 Part F (c): AB a diameter, TP tangent at T, angle ATP = 111 (exact)
    O = (0, 0)
    Bb, Aa = onm(O, 1, -20), onm(O, 1, 160)
    Tt = onm(O, 1, -20 + 42)
    Pp = inter(Tt, add(Tt, rot(Tt, 90)), Aa, Bb)
    f = G(220, 150).frame([(-1.1, -1.1), (1.1, 1.1), Pp], pad=12)
    f.C(O, 1, width=1.2).S(Aa, Pp, width=1.2).S(Aa, Tt, width=1.2).S(Tt, Pp, width=1.2).S(Tt, Bb, width=1.2).D(O, 2)
    T_, A_, P_ = f.T(Tt), f.T(Aa), f.T(Pp)
    a0, a1 = atan2(-(A_[1] - T_[1]), A_[0] - T_[0]), atan2(-(P_[1] - T_[1]), P_[0] - T_[0])
    rr = 12
    x0, y0 = T_[0] + rr * cos(a0), T_[1] - rr * sin(a0)
    x1, y1 = T_[0] + rr * cos(a1), T_[1] - rr * sin(a1)
    f.raw(f'<path d="M{T_[0]:.1f},{T_[1]:.1f} L{x0:.1f},{y0:.1f} A{rr},{rr} 0 0 1 {x1:.1f},{y1:.1f} Z" fill="#8a96a3" fill-opacity="0.7" stroke="#1f2a37" stroke-width="0.8"/>')
    f.text(T_[0] - 30, T_[1] + 18, "111°", size=10.5)
    f.L(O, "O", dy=12).O(Aa, O, "A").O(Bb, O, "B", d=12).O(Tt, O, "T").L(Pp, "P", dx=9, dy=4)
    save("c3r2", f)
    # R3 Sydney Boys 2022 Part F Q3: rectangle ABCD, AF a diameter of a semicircle with tangent BC; AE = 6 (exact, r = 3.4)
    r = 3.4
    O = (0.0, 0.0)
    Fq, Aq = (-r, 0.0), (r, 0.0)
    dD = r - 36 / (2 * r)
    Dq = (dD, 0.0)
    Cq, Bq = (dD, r), (r, r)
    Eq = (dD, sqrt(r * r - dD * dD))
    f = G(220, 150).frame([Fq, Aq, Bq, Cq, (0, r)], pad=14)
    T0 = f.T(Fq)
    f.raw(f'<path d="M{f.T(Fq)[0]:.1f},{f.T(Fq)[1]:.1f} A{f.s * r:.1f},{f.s * r:.1f} 0 0 1 {f.T(Aq)[0]:.1f},{f.T(Aq)[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.6"/>')
    f.S(Fq, Aq).poly([f.T(Aq), f.T(Bq), f.T(Cq), f.T(Dq)], color=None, opacity=0).S(Eq, Aq, dash="3 2", width=1.1)
    f.SL(Eq, Aq, "6 cm", side=1, d=9)
    f.L(Fq, "F", dx=-4, dy=13, italic=True).L(Dq, "D", dx=2, dy=13).L(Aq, "A", dx=9, dy=6).L(Bq, "B", dx=9, dy=-4).L(Cq, "C", dx=-6, dy=-8).L(Eq, "E", dx=-9, dy=-2)
    save("c3r3", f)
    # R4 Girraween 2020 Q25(d): AT tangent at T, TA = TC, angle ACT = 25 (exact)
    Tt = (0.0, 0.0)
    a = 3.0
    Aa = (-a, 0.0)
    Cc = (a * cos(radians(50)), a * sin(radians(50)))
    k = a / (2 * sin(radians(50)))
    O = (0.0, k)
    dv = unit(sub(Cc, Aa))
    ts = line_circle(Aa, dv, O, k)
    Bb = add(Aa, dv, ts[0])
    f = G(220, 160).frame([Aa, (-k, 2 * k), (k, 0)], pad=12)
    f.C(O, k, width=1.2).S(Aa, Cc, width=1.2).S(Aa, Tt, width=1.2).S(Tt, Cc, width=1.2).S(Bb, Tt, width=1.2)
    f.tick(f.T(Aa), f.T(Tt)).tick(f.T(Tt), f.T(Cc))
    f.A(Cc, Aa, Tt, "25°", r=16, d=30).A(Bb, Aa, Tt, "x", r=10, d=18)
    f.L(Aa, "A", dx=-8, dy=2).L(Bb, "B", dx=-6, dy=-8).L(Cc, "C", dx=8, dy=-2).L(Tt, "T", dx=2, dy=13)
    save("c3r4", f)


if __name__ == "__main__":
    concept1()
    concept2()
    concept3()
    concept45()
    pastpapers()
    hard_sb23()
    review()
