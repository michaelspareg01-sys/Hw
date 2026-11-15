"""Figures for Lesson 3 (8H Using congruent triangles to establish properties of quadrilaterals) and the
Chapter 8 review. Run after figs.py: python3 figs_l3.py

Named figures are drawn as scenes: points with letter names (math coordinates, y up), segments, equal-length
ticks, parallel arrows, right-angle marks, angle marks and labels. Every shape is constructed exactly from
its defining property (a parallelogram from two side vectors, a kite from its axis, a rhombus from equal
sides, and so on), so every mark in a figure is true in the coordinates. The layouts follow the book's
figures (workspace/sources/y8/chapter 8.pdf, PDF pages 47-52 and 57-60) and the past papers.
Unnamed triangle pairs (8H Q6, review Q9 and Q10a, the multiple-choice pair) reuse the Lesson 2 pair helpers.
"""
from math import sin, cos, radians, degrees, atan2, hypot, sqrt, tan
from figs import CF, save, ftext, centroid, _ang, ACC
from figs_l2 import (pair, draw, shift_all, tri_angles, tri_sas, tri_sides, fit_sim, iso, _clean, I3)
from svg_overlap import text_width

BLUE = "blue"


def _nm(s):
    """Split a run of point names: a name is one character, or '_' and one character."""
    out, i = [], 0
    while i < len(s):
        if s[i] == "_":
            out.append(s[i:i + 2])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return out


class Scene:
    """A named figure. P: {name: (x, y)} in math units (y up); k: pixels per unit."""

    def __init__(self, P, k=40.0, pad=26, extra_w=0, extra_h=0):
        xs = [p[0] for p in P.values()]
        ys = [p[1] for p in P.values()]
        x0, y1 = min(xs), max(ys)
        self.P = {n: ((x - x0) * k + pad, (y1 - y) * k + pad) for n, (x, y) in P.items()}
        self.k, self.pad, self.x0, self.y1 = k, pad, x0, y1
        W = (max(xs) - x0) * k + 2 * pad + extra_w
        H = (y1 - min(ys)) * k + 2 * pad + extra_h
        self.f = CF(round(W), round(H))
        self.segs = []
        self.later = []

    def m2p(self, x, y):
        return ((x - self.x0) * self.k + self.pad, (self.y1 - y) * self.k + self.pad)

    def seg(self, *names, dash=False, faint=False):
        for s in names:
            n0, n1 = _nm(s)
            a, b = self.P[n0], self.P[n1]
            if faint:
                self.f.line(a[0], a[1], b[0], b[1], color="faint", width=1.0, dash="4 3")
            elif dash:
                self.f.line(a[0], a[1], b[0], b[1], color="rose", width=1.0, dash="4 3")
            else:
                self.f.line(a[0], a[1], b[0], b[1], color=BLUE, width=1.5)
            self.segs.append((n0, n1))
        return self

    def tick(self, s, n=1, t=0.5):
        a, b = _nm(s)
        self.f.tick(self.P[a], self.P[b], n, t=t)
        return self

    def arrow(self, s, n=1, t=0.5):
        a, b = _nm(s)
        self.f.parr(self.P[a], self.P[b], n=n, t=t, color=BLUE)
        return self

    def right(self, s, size=7):
        a, v, b = (self.P[c] for c in _nm(s))
        self.f.right(v, a, b, s=size)
        return self

    def mark(self, s, kind, r=None):
        a, v, b = (self.P[c] for c in _nm(s))
        a0, a1 = radians(_ang(v, a)), radians(_ang(v, b))
        bx, by = cos(a0) + cos(a1), sin(a0) + sin(a1)
        L = hypot(bx, by)
        half = _wedge(v, a, b) / 2
        rr = r or max(11.0, 5.5 / max(sin(radians(half)), 0.1))
        q = (v[0] + rr * bx / L, v[1] - rr * by / L)
        if kind == "dot":
            self.f.dot(q[0], q[1], r=2.0)
        elif kind == "o":
            self.f.raw(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2.2" fill="#fff" stroke="{ACC["ink"]}" stroke-width="0.9"/>')
        elif kind == "x":
            for dx, dy in ((2.6, 2.6), (2.6, -2.6)):
                self.f.line(q[0] - dx, q[1] - dy, q[0] + dx, q[1] + dy, width=1.05)
        elif kind in ("arc", "arc2"):
            self.f.angle(v, a, b, r=r or 13, n=1 if kind == "arc" else 2)
        return self

    def names(self, which=None, size=12.5, d=8.0, avoid=()):
        for n in (which if which is not None else [n for n in self.P if not n.startswith("_")]):
            self.later.append(("name", n, size, d))
        return self

    def alab(self, s, text, size=12):
        self.later.append(("alab", s, text, size))
        return self

    def slab(self, s, text, size=12, side=None):
        self.later.append(("slab", s, text, size, side))
        return self

    def text(self, x, y, s, size=12, italic=False):
        q = self.m2p(x, y)
        self.later.append(("text", q, s, size, italic))
        return self

    # ---- label placement ----
    def _dirs(self, p):
        out = []
        for a, b in self.segs:
            A, B = self.P[a], self.P[b]
            if _close(A, p):
                out.append(_ang(p, B))
            elif _close(B, p):
                out.append(_ang(p, A))
            elif _on_seg(p, A, B):
                out.append(_ang(p, A))
                out.append(_ang(p, B))
        return sorted(d % 360 for d in out)

    def _place_name(self, n, size, d):
        p = self.P[n]
        dirs = self._dirs(p)
        cands = []
        if not dirs:
            cands = [90, 270, 0, 180]
        else:
            gaps = []
            for i, a in enumerate(dirs):
                b = dirs[(i + 1) % len(dirs)] + (360 if i + 1 == len(dirs) else 0)
                gaps.append((b - a, (a + b) / 2))
            gaps.sort(reverse=True)
            cands = [g[1] for g in gaps]
            # also try slight rotations of the best direction
            best = cands[0]
            cands = [best, best + 15, best - 15, best + 30, best - 30] + cands[1:]
        base = len(self.f.items)
        w = text_width(n, size)
        for extra in (0, 4, 8, 13):
            for a in cands:
                ux, uy = cos(radians(a)), -sin(radians(a))
                dd = d + extra + 0.5 * w * abs(ux) + 0.38 * size * abs(uy)
                self.f.items = self.f.items[:base]
                self.f.text(p[0] + dd * ux, p[1] + dd * uy, n, size=size, italic=True)
                if _clean(self.f, n):
                    return
        self.f.items = self.f.items[:base]
        a = cands[0]
        self.f.text(p[0] + (d + 6) * cos(radians(a)), p[1] - (d + 6) * sin(radians(a)), n, size=size, italic=True)

    def _place_alab(self, s, text, size):
        a, v, b = (self.P[c] for c in _nm(s))
        a0, a1 = radians(_ang(v, a)), radians(_ang(v, b))
        bx, by = cos(a0) + cos(a1), sin(a0) + sin(a1)
        L = hypot(bx, by)
        ux, uy = bx / L, -by / L
        half = _wedge(v, a, b) / 2
        d0 = max(16.0, 8.5 / max(sin(radians(half)), 0.08))
        base = len(self.f.items)
        for k in (1.0, 1.2, 1.45, 1.75, 2.1, 2.5, 3.0):
            q = (v[0] + d0 * k * ux, v[1] + d0 * k * uy)
            self.f.items = self.f.items[:base]
            self.f.text(q[0], q[1], text, size=size)
            if _clean(self.f, text):
                return
        self.f.items = self.f.items[:base]
        ftext(self.f, v[0] + d0 * ux, v[1] + d0 * uy, text, size=size)

    def _place_slab(self, s, text, size, side):
        n0, n1 = _nm(s)
        A, B = self.P[n0], self.P[n1]
        m = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        c = centroid(list(self.P.values()))
        ux, uy = B[0] - A[0], B[1] - A[1]
        L = hypot(ux, uy)
        nx, ny = -uy / L, ux / L
        if (m[0] - c[0]) * nx + (m[1] - c[1]) * ny < 0:
            nx, ny = -nx, -ny
        if side == "in":
            nx, ny = -nx, -ny
        it = text.split()[0] in ("x", "y")
        w = text_width(text, size)
        base = len(self.f.items)
        for dd0, sg in ((6, 1), (10, 1), (15, 1), (6, -1), (10, -1)):
            dd = dd0 + 0.5 * w * abs(nx) + 0.45 * size * abs(ny)
            self.f.items = self.f.items[:base]
            ftext(self.f, m[0] + sg * dd * nx, m[1] + sg * dd * ny, text, size=size, italic=it, rmax=10)
            if _clean(self.f, text):
                return

    def save(self, name):
        for item in self.later:
            if item[0] == "name":
                self._place_name(item[1], item[2], item[3])
            elif item[0] == "alab":
                self._place_alab(item[1], item[2], item[3])
            elif item[0] == "slab":
                self._place_slab(item[1], item[2], item[3], item[4])
            elif item[0] == "text":
                q = item[1]
                ftext(self.f, q[0], q[1], item[2], size=item[3], italic=item[4], rmax=10)
        save(name, self.f)


def _close(p, q, tol=0.5):
    return hypot(p[0] - q[0], p[1] - q[1]) < tol


def _on_seg(p, a, b, tol=0.6):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L2 = ax * ax + ay * ay
    t = ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2
    if t <= 0.01 or t >= 0.99:
        return False
    return hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay) < tol


def _wedge(v, a, b):
    d = abs((_ang(v, a) - _ang(v, b)) % 360)
    return min(d, 360 - d)


def isect(a, b, c, d):
    """Intersection of lines ab and cd (math coordinates)."""
    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    x4, y4 = d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def para(A, u, v):
    """Parallelogram ABCD from A and side vectors u = AB, v = AD."""
    B = (A[0] + u[0], A[1] + u[1])
    D = (A[0] + v[0], A[1] + v[1])
    C = (B[0] + v[0], B[1] + v[1])
    return A, B, C, D


def pol(L, deg):
    return (L * cos(radians(deg)), L * sin(radians(deg)))


def mid(p, q):
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


# ======================= Concept 1 =======================

def fig_start():
    A, B, C, D = para((0, 0), (3.0, 0), (1.0, 1.7))
    S = Scene(dict(A=A, B=B, C=C, D=D, E=mid(A, C)), k=40)
    S.seg("AB", "BC", "CD", "DA").seg("AC", "BD", dash=True)
    S.tick("AB", 2, t=0.33).tick("DC", 2, t=0.33).tick("AD", 1, t=0.32).tick("BC", 1, t=0.32)
    S.arrow("AB", 2, t=0.66).arrow("DC", 2, t=0.66).arrow("AD", 1, t=0.66).arrow("BC", 1, t=0.66)
    S.names().save("l3_start")


def fig_ex13():
    A, B, C, D = para((0, 0), (3.0, 0), (1.1, 2.0))
    E = mid(A, C)
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=40)
    S.seg("AB", "BC", "CD", "DA").seg("AC", "BD", dash=True)
    S.tick("AB", 2, t=0.66).tick("DC", 2, t=0.66).tick("AD", 1, t=0.4).tick("BC", 1, t=0.4)
    S.arrow("AB", 2, t=0.4).arrow("DC", 2, t=0.4).arrow("AD", 1, t=0.66).arrow("BC", 1, t=0.66)
    S.names().save("l3_ex13")
    # explanation: the two Z shapes
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=26, pad=22)
    S.seg("AB", "CD", "AC").seg("BD", faint=True)
    S.arrow("AB", 2, t=0.6).arrow("DC", 2, t=0.6)
    S.mark("BAC", "dot").mark("DCA", "dot")
    S.names(size=15).save("l3_ex13a")
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=26, pad=22)
    S.seg("AB", "CD", "BD").seg("AC", faint=True)
    S.arrow("AB", 2, t=0.6).arrow("DC", 2, t=0.6)
    S.mark("ABD", "o").mark("CDB", "o")
    S.names(size=15).save("l3_ex13b")


def fig_c1_demos():
    # tutor demo: parallelogram PQRS, diagonals meet at M
    P, Q, R, Sv = para((0, 0), (3.4, 0), (1.3, 1.9))
    S = Scene(dict(P=P, Q=Q, R=R, S=Sv, M=mid(P, R)), k=40)
    S.seg("PQ", "QR", "RS", "SP", "PR", "QS")
    S.tick("PQ", 2, t=0.3).tick("SR", 2, t=0.3).tick("PS", 1, t=0.3).tick("QR", 1, t=0.3)
    S.arrow("PQ", 2, t=0.75).arrow("SR", 2, t=0.75).arrow("PS", 1, t=0.7).arrow("QR", 1, t=0.7)
    S.names().save("l3_d1")
    # your turn: parallelogram ABCD, diagonals meet at E; AX = CY
    A, B, C, D = para((0, 0), (4.0, 0), (1.2, 2.2))
    X = (1.4, 0.0)
    Y = (C[0] - 1.4, C[1])
    S = Scene(dict(A=A, B=B, C=C, D=D, E=mid(A, C), X=X, Y=Y), k=38)
    S.seg("AB", "BC", "CD", "DA", "AC", "XY").seg("BD", dash=True)
    S.tick("AX", 1).tick("CY", 1)
    S.arrow("XB", 2, t=0.55).arrow("DY", 2, t=0.45).arrow("AD", 1, t=0.6).arrow("BC", 1, t=0.6)
    S.names().save("l3_y1")


# ======================= Concept 2 =======================

def fig_keyideas():
    # kite: axis horizontal, right angle where the diagonals meet
    L, Rr = (0, 0), (3.4, 0)
    E = (0.9, 0)
    T, Bm = (0.9, 0.85), (0.9, -0.85)
    S = Scene(dict(_L=L, _T=T, _R=Rr, _B=Bm, _E=E), k=34, pad=12)
    S.seg("_L_T", "_T_R", "_R_B", "_B_L")
    S.seg("_L_R", "_T_B", dash=True)
    S.tick("_L_T", 1).tick("_L_B", 1).tick("_T_R", 2).tick("_B_R", 2)
    S.right("_T_E_R", size=6)
    S.save("l3_k_kite")
    # trapezium
    S = Scene(dict(_A=(0, 0), _B=(3.6, 0), _C=(2.3, 1.3), _D=(0.6, 1.3)), k=34, pad=12)
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_A_C", "_B_D", dash=True)
    S.arrow("_A_B", 1, t=0.55).arrow("_D_C", 1, t=0.55)
    S.save("l3_k_trap")
    # parallelogram
    A, B, C, D = para((0, 0), (3.4, 0), (-0.8, 1.6))
    S = Scene(dict(_A=A, _B=B, _C=C, _D=D), k=34, pad=12)
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_A_C", "_B_D", dash=True)
    S.arrow("_B_A", 2, t=0.5).arrow("_C_D", 2, t=0.5).arrow("_A_D", 1, t=0.5).arrow("_B_C", 1, t=0.5)
    S.save("l3_k_para")
    # rhombus (right angle where the diagonals meet)
    A, B, C, D = para((0, 0), (2.2, 0), pol(2.2, 60))
    S = Scene(dict(_A=A, _B=B, _C=C, _D=D, _E=mid(A, C)), k=34, pad=12)
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_A_C", "_B_D", dash=True)
    for s in ("_A_B", "_B_C", "_D_C", "_A_D"):
        S.tick(s, 2, t=0.65)
    S.arrow("_A_B", 2, t=0.35).arrow("_D_C", 2, t=0.35).arrow("_A_D", 1, t=0.35).arrow("_B_C", 1, t=0.35)
    S.right("_C_E_B", size=6)
    S.save("l3_k_rhom")
    # rectangle
    A, B, C, D = para((0, 0), (3.0, 0), (0, 1.6))
    S = Scene(dict(_A=A, _B=B, _C=C, _D=D), k=34, pad=12)
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_A_C", "_B_D", dash=True)
    S.arrow("_A_B", 2).arrow("_D_C", 2).arrow("_A_D", 1).arrow("_B_C", 1)
    for s in ("_B_A_D", "_C_B_A", "_D_C_B", "_A_D_C"):
        S.right(s, size=6)
    S.save("l3_k_rect")
    # square
    A, B, C, D = para((0, 0), (2.2, 0), (0, 2.2))
    S = Scene(dict(_A=A, _B=B, _C=C, _D=D, _E=mid(A, C)), k=34, pad=12)
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_A_C", "_B_D", dash=True)
    S.arrow("_A_B", 2, t=0.38).arrow("_D_C", 2, t=0.38).arrow("_A_D", 1, t=0.38).arrow("_B_C", 1, t=0.38)
    for s in ("_A_B", "_B_C", "_D_C", "_A_D"):
        S.tick(s, 2, t=0.68)
    for s in ("_B_A_D", "_C_B_A", "_D_C_B", "_A_D_C"):
        S.right(s, size=6)
    S.right("_C_E_B", size=6)
    S.save("l3_k_sq")


def fig_c2_demos():
    # tutor demo: rhombus PQRS with diagonal PR
    P, Q, R, Sv = para((0, 0), (2.8, 0), pol(2.8, 58))
    S = Scene(dict(P=P, Q=Q, R=R, S=Sv), k=40)
    S.seg("PQ", "QR", "RS", "SP", "PR")
    for s in ("PQ", "QR", "SR", "PS"):
        S.tick(s, 1)
    S.names().save("l3_d2")
    # your turn: trapezium ABCD with AB parallel to DC, AD = BC and equal base angles
    A, B, C, D = (0, 0), (6.0, 0), (4.5, 2.6), (1.5, 2.6)
    S = Scene(dict(A=A, B=B, C=C, D=D), k=30)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.arrow("AB", 1, t=0.5).arrow("DC", 1, t=0.5)
    S.tick("AD", 1).tick("BC", 1)
    S.mark("DAB", "arc", r=16).mark("CBA", "arc", r=16)
    S.names().save("l3_y2")


# ======================= Homework =======================

def fig_q1():
    shapes = {
        "l3_q1a": [(0, 0), (2.4, 0), (2.4, 1.3), (0, 1.3)],
        "l3_q1b": [(0, 0), (1.8, 0), (1.8, 1.8), (0, 1.8)],
        "l3_q1c": [(0, 0), (1.15, 0.8), (2.3, 0), (1.15, -0.8)],
        "l3_q1d": [(0, 0), (1.3, 0), (2.6, 2.4), (1.3, 2.4)],
    }
    for name, Q in shapes.items():
        S = Scene({f"_{i}": p for i, p in enumerate(Q)}, k=34, pad=8)
        S.seg("_0_1", "_1_2", "_2_3", "_3_0")
        S.save(name)


def _pg(k=34, pad=12):
    A, B, C, D = para((0, 0), (3.0, 0), (0.9, 1.4))
    return Scene(dict(_A=A, _B=B, _C=C, _D=D), k=k, pad=pad)


def fig_q2():
    S = _pg()
    S.seg("_A_B", "_B_C", "_C_D", "_D_A")
    S.tick("_A_B", 2).tick("_D_C", 2).tick("_A_D", 1).tick("_B_C", 1)
    S.save("l3_q2a")
    S = _pg()
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_D_B", dash=True)
    S.mark("_B_A_D", "arc2").mark("_D_C_B", "arc2")
    S.save("l3_q2b")
    A, B, C, D = para((0, 0), (3.0, 0), (0.9, 1.4))
    S = Scene(dict(_A=A, _B=B, _C=C, _D=D, _E=mid(A, C)), k=34, pad=12)
    S.seg("_A_B", "_B_C", "_C_D", "_D_A").seg("_A_C", "_B_D", dash=True)
    S.tick("_A_E", 2).tick("_E_C", 2).tick("_D_E", 1).tick("_E_B", 1)
    S.save("l3_q2c")
    S = _pg()
    S.seg("_A_B", "_B_C", "_C_D", "_D_A")
    S.arrow("_A_B", 2).arrow("_D_C", 2).arrow("_A_D", 1).arrow("_B_C", 1)
    S.save("l3_q2d")


def fig_q4():
    S = Scene(dict(A=(0, 0), B=(3.0, 0), C=(3.0, 1.4), D=(0, 1.4)), k=36)
    S.seg("AB", "BC", "CD", "DA", "AC").names().save("l3_q4a")
    S = Scene(dict(A=(-0.8, 0.95), D=(0, 1.3), C=(0.8, 0.95), B=(0, -1.3)), k=36)
    S.seg("AD", "DC", "CB", "BA", "DB").names().save("l3_q4b")
    A, B, C, D = (0, 1.5), (1.6, 1.5), (2.4, 0), (0.8, 0)
    S = Scene(dict(A=A, B=B, C=C, D=D), k=36)
    S.seg("AB", "BC", "CD", "DA", "DB").names().save("l3_q4c")


def fig_q5():
    S = Scene(dict(A=(0, 1.9), B=(1.9, 1.9), C=(1.9, 0), D=(0, 0)), k=38)
    S.seg("AB", "BC", "CD", "DA").seg("AC", "BD", dash=True)
    S.names().save("l3_q5")


def fig_q6():
    # a: AAS, two triangles through X (a half-turn about X)
    X = (0.0, 0.0)
    P1, P2 = (1.0, 1.75), (1.0, -0.45)
    Q1, Q2 = (-1.0, -1.75), (-1.0, 0.45)
    k = 50
    T1 = [(X[0] * k, -X[1] * k), (P1[0] * k, -P1[1] * k), (P2[0] * k, -P2[1] * k)]
    T2 = [(X[0] * k, -X[1] * k), (Q1[0] * k, -Q1[1] * k), (Q2[0] * k, -Q2[1] * k)]
    (T1, T2), W, H = shift_all([T1, T2], pad=16)
    from figs import CF as _CF
    f = _CF(W, H)
    draw(f, [T1, T2], [dict(ticks={(1, 2): 2}, marks={1: "dot", 2: "x"}), dict(ticks={(1, 2): 2}, marks={1: "dot", 2: "x"})])
    save("l3_q6a", f)
    # b: RHS, rectangle cut by a diagonal; right angles top-left and bottom-right; ticks on the short sides
    TL, TR, BR, BL = (0, 0), (120, 0), (120, 54), (0, 54)
    (T1, T2), W, H = shift_all([[TL, BL, TR], [BR, TR, BL]], pad=16)
    f = _CF(W, H)
    draw(f, [T1, T2], [dict(marks={0: "R"}, ticks={(0, 1): 2}), dict(marks={0: "R"}, ticks={(0, 1): 2})])
    save("l3_q6b", f)
    # c: SSS, right isosceles triangle split from the right-angle vertex to the midpoint of the hypotenuse
    k = 46
    R, Lp, T = (0, 0), (-2 * k, 0), (0, -2 * k)
    M = mid(Lp, T)
    (T1, T2), W, H = shift_all([[Lp, M, R], [T, M, R]], pad=16)
    f = _CF(W, H)
    draw(f, [T1, T2], [dict(ticks={(0, 1): 1, (0, 2): 2}), dict(ticks={(0, 1): 1, (0, 2): 2})])
    save("l3_q6c", f)
    # d: SAS, two triangles through X (a half-turn); the angles at X are marked with dots
    k = 46
    S1, L1 = (-0.35, 0.95), (1.9, 0.95)
    T1 = [(0, 0), (S1[0] * k, -S1[1] * k), (L1[0] * k, -L1[1] * k)]
    T2 = [(0, 0), (-S1[0] * k, S1[1] * k), (-L1[0] * k, L1[1] * k)]
    (T1, T2), W, H = shift_all([T1, T2], pad=16)
    f = _CF(W, H)
    draw(f, [T1, T2], [dict(ticks={(0, 1): 1, (0, 2): 2}, marks={0: "dot"}), dict(ticks={(0, 1): 1, (0, 2): 2}, marks={0: "dot"})])
    save("l3_q6d", f)
    # e: AAS, parallelogram cut by the diagonal from bottom-left to top-right
    k = 40
    A, B, C, D = para((0, 0), (2.6, 0), (-0.75, 1.25))
    pg = lambda p: (p[0] * k, -p[1] * k)
    A, B, C, D = pg(A), pg(B), pg(C), pg(D)
    (T1, T2), W, H = shift_all([[D, A, C], [B, C, A]], pad=16)
    f = _CF(W, H)
    draw(f, [T1, T2], [dict(marks={0: "x", 1: "dot"}), dict(marks={0: "x", 1: "dot"})])
    save("l3_q6e", f)
    # f: SSS, square cut by a diagonal; all four sides marked equal
    TL, TR, BR, BL = (0, 0), (84, 0), (84, 84), (0, 84)
    (T1, T2), W, H = shift_all([[BL, TL, TR], [TR, BR, BL]], pad=16)
    f = _CF(W, H)
    draw(f, [T1, T2], [dict(ticks={(0, 1): 2, (1, 2): 2}), dict(ticks={(0, 1): 2, (1, 2): 2})])
    save("l3_q6f", f)


def fig_q8_q9():
    s = 2.0
    S = Scene(dict(E=(0, 0), F=(s, 0), G=(s, s), H=(0, s), I=(s / 2, s / 2)), k=40)
    S.seg("EF", "FG", "GH", "HE", "EG", "FH")
    S.tick("HG", 2).tick("EF", 2).tick("HE", 1).tick("FG", 1)
    for r in ("FEH", "GFE", "HGF", "EHG"):
        S.right(r, size=6)
    S.names().save("l3_q8")
    A, B, C, D = para((0, 0), (2.4, 0), (0.6, 1.2))
    S = Scene(dict(A=A, B=B, C=C, D=D), k=40)
    S.seg("AB", "BC", "CD", "DA", "DB")
    S.arrow("AB", 2).arrow("DC", 2).arrow("AD", 1).arrow("BC", 1)
    S.names().save("l3_q9")


def fig_q10_q13():
    # Q10 rhombus STUV (S bottom-left, T bottom-right, U top-right, V top-left), diagonals meet at W
    Sv, T, U, V = para((0, 0), (1.9, 0), pol(1.9, 64))
    Sv, T, U, V = Sv, T, U, V
    W = mid(Sv, U)
    S = Scene(dict(S=Sv, T=T, U=U, V=V, W=W), k=44)
    S.seg("ST", "TU", "UV", "VS", "VT", "SU")
    for s_ in ("VU", "ST", "VS", "TU"):
        S.tick(s_, 2, t=0.62)
    S.tick("VW", 1).tick("WT", 1)
    S.arrow("VU", 2, t=0.35).arrow("ST", 2, t=0.35).arrow("SV", 1, t=0.35).arrow("TU", 1, t=0.35)
    S.names().save("l3_q10")
    # Q11 square MNOP (M bottom-left, N bottom-right, O top-right, P top-left), diagonals meet at Q
    s = 2.0
    S = Scene(dict(M=(0, 0), N=(s, 0), O=(s, s), P=(0, s), Q=(s / 2, s / 2)), k=40)
    S.seg("MN", "NO", "OP", "PM", "MO", "NP")
    for s_ in ("MN", "NO", "PO", "MP"):
        S.tick(s_, 1)
    S.names().save("l3_q11")
    # Q12 kite ABCD: C top, D left, B right, A bottom; diagonal DB
    D, B = (0, 0), (3.2, 0)
    C, A = (0.85, 0.95), (0.85, -0.95)
    S = Scene(dict(A=A, B=B, C=C, D=D), k=40)
    S.seg("DC", "CB", "BA", "AD", "DB")
    S.tick("DC", 1).tick("DA", 1).tick("CB", 2).tick("AB", 2)
    S.names().save("l3_q12")
    # Q13 rectangle ABCD with both diagonals
    S = Scene(dict(A=(0, 0), B=(3.2, 0), C=(3.2, 1.5), D=(0, 1.5)), k=40)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.tick("DC", 2).tick("AB", 2).tick("AD", 1).tick("BC", 1)
    for r in ("BAD", "CBA", "DCB", "ADC"):
        S.right(r, size=6)
    S.names().save("l3_q13")
    # Q14 rectangle ABCD with diagonal DB and parallel marks
    S = Scene(dict(A=(0, 0), B=(3.2, 0), C=(3.2, 1.6), D=(0, 1.6)), k=40)
    S.seg("AB", "BC", "CD", "DA", "DB")
    S.arrow("DC", 2).arrow("AB", 2).arrow("AD", 1).arrow("BC", 1)
    S.names().save("l3_q14")


def fig_q15_q17():
    # Q15 trapezium ABCD: AB parallel to DC, diagonals meet at E
    A, B, C, D = (0, 0), (3.6, 0), (1.9, 1.35), (0.65, 1.35)
    E = isect(A, C, B, D)
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=44)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.arrow("AB", 1, t=0.7).arrow("DC", 1, t=0.55)
    S.names().save("l3_q15")
    # Q16 kite ABCD: D top, A left, C right, B bottom; diagonals AC and DB meet at E
    D, B = (0, 1.0), (0, -2.6)
    A, C = (-1.0, 0.0), (1.0, 0.0)
    E = (0, 0)
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=40)
    S.seg("AD", "DC", "CB", "BA", "AC", "DB")
    S.tick("AD", 1).tick("DC", 1).tick("AB", 2).tick("CB", 2)
    S.mark("ADE", "dot", r=14).mark("CDE", "dot", r=14)
    S.names().save("l3_q16")
    # Q17a: ABCD with opposite sides equal (D top-left, C top-right, A bottom, B bottom-right)
    A, B, C, D = para((0, 0), (1.9, 0), (-1.15, 2.4))
    E = mid(A, C)
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=40)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.tick("DC", 2).tick("AB", 2).tick("DA", 1).tick("CB", 1)
    S.names().save("l3_q17a")
    # Q17b: diagonals bisect each other
    A, B, C, D = para((0, 0), (2.8, 0), (0.8, 1.35))
    E = mid(A, C)
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E), k=42)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.tick("DE", 1).tick("EB", 1).tick("AE", 2).tick("EC", 2)
    S.names().save("l3_q17b")
    # Q17c: parallelogram with equal diagonals (drawn as it turns out: a rectangle)
    S = Scene(dict(A=(0, 0), B=(2.9, 0), C=(2.9, 1.5), D=(0, 1.5)), k=40, extra_h=14)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.arrow("DC", 2).arrow("AB", 2).arrow("AD", 1).arrow("BC", 1)
    S.text(1.45, -0.62, "AC = BD", size=12, italic=True)
    S.names().save("l3_q17c")


# ======================= Past papers =======================

def fig_pp():
    # Normanhurst Boys 2025 Q8(a): isosceles XYZ, YW perpendicular to XZ
    S = Scene(dict(X=(0, 0), Z=(3.2, 0), Y=(1.6, 4.0), W=(1.6, 0)), k=36)
    S.seg("XZ", "ZY", "YX", "YW")
    S.tick("XY", 2).tick("ZY", 2)
    S.right("YWZ", size=7)
    S.names().save("l3_pp_nb")
    # North Sydney Boys 2020 Q3(b): square ABCD of side 14, EC = FC = 4
    k = 9.0
    A, B, C, D = (0, 14), (14, 14), (14, 0), (0, 0)
    E, F = (14, 4), (10, 0)
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E, F=F), k=k)
    S.seg("AB", "BE", "EC", "CF", "FD", "DA", "AE", "AF")
    S.tick("EC", 1).tick("FC", 1)
    S.names().save("l3_pp_ns")
    # Sydney Tech 2024 Q16(c): circle centre O; PQ = QR; QO extended meets the circle at S
    r = 2.2
    O = (0, 0)
    Q = (0, r)
    P = pol(r, 205)
    R = pol(r, -25)
    Sv = (0, -r)
    k = 34
    S = Scene(dict(O=O, P=P, Q=Q, R=R, S=Sv, _w=(-r, 0), _e=(r, 0)), k=k)
    c = S.P["O"]
    S.f.circle(c, r * k, color="ink", width=1.6)
    S.seg("QP", "QR", "OP", "OR", "QS")
    S.tick("QP", 1).tick("QR", 1)
    S.names(["O", "P", "Q", "R", "S"]).save("l3_pp_st")
    # Merewether 2023 Q4: ABCD with AD = BC and AC = BD (an isosceles trapezium), diagonals meet at P
    A, B, C, D = (0, 0), (3.0, 0), (3.6, 2.2), (-0.6, 2.2)
    Pp = isect(A, C, B, D)
    S = Scene(dict(A=A, B=B, C=C, D=D, P=Pp), k=40)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    S.names().save("l3_pp_mere")
    # Baulkham Hills 2020 Q17: AB parallel DC, EB parallel DF, EB = DF; E and F on AC
    D = (0, 0)
    C = (5.0, 0.8)
    A = (0.75, 3.0)
    B = (A[0] + C[0] - D[0], A[1] + C[1] - D[1])
    E = (A[0] + 0.3 * (C[0] - A[0]), A[1] + 0.3 * (C[1] - A[1]))
    F = (A[0] + 0.7 * (C[0] - A[0]), A[1] + 0.7 * (C[1] - A[1]))
    S = Scene(dict(A=A, B=B, C=C, D=D, E=E, F=F), k=38)
    S.seg("AB", "BC", "CD", "DA", "AC", "EB", "DF")
    S.arrow("AB", 2, t=0.6).arrow("DC", 2, t=0.6).arrow("EB", 1, t=0.6).arrow("DF", 1, t=0.6)
    S.tick("EB", 1, t=0.4).tick("DF", 1, t=0.4)
    S.names().save("l3_pp_bh")
    # Sydney Grammar 2022 Q7(d): rectangle ABCD (A top-left, D top-right), P and Q midpoints of AD and BC
    S = Scene(dict(A=(0, 1.6), D=(4.0, 1.6), C=(4.0, 0), B=(0, 0), P=(2.0, 1.6), Q=(2.0, 0)), k=40)
    S.seg("AP", "PD", "DC", "CQ", "QB", "BA")
    S.f.pdot(S.P["P"], r=2.0).pdot(S.P["Q"], r=2.0)
    S.names().save("l3_pp_sg")
    S = Scene(dict(A=(0, 1.6), D=(4.0, 1.6), C=(4.0, 0), B=(0, 0), P=(2.0, 1.6), Q=(2.0, 0), R=(2.0, 0.8)), k=40)
    S.seg("AP", "PD", "DC", "CQ", "QB", "BA", "PQ", "BD")
    S.f.pdot(S.P["P"], r=2.0).pdot(S.P["Q"], r=2.0)
    S.names().save("l3_a_sg")
    # James Ruse 2024 Q13(d): right triangle ABC, M midpoint of AC, MY perpendicular to AC
    A, B, C = (0, 3.0), (0, 0), (5.0, 0)
    M = mid(A, C)
    Y = (M[0] - M[1] * 3 / 5, 0)
    S = Scene(dict(A=A, B=B, C=C, M=M, Y=Y), k=36, extra_w=60)
    S.seg("AB", "BY", "YC", "CA", "AY", "MY")
    S.tick("AM", 2).tick("MC", 2)
    S.right("ABY", size=6).right("YMC", size=6)
    S.text(6.4, 2.5, "NOT TO", size=10).text(6.4, 2.1, "SCALE", size=10)
    S.names().save("l3_pp_jr")


# ======================= Chapter review =======================

def fig_review():
    # MC 6-9: triangles ABC and FED (FED is a half-turn of ABC); A = E (cross), B = F (dot), AB = FE (tick)
    ABC = [(116.0, 748.0), (190.0, 748.0), (112.0, 685.0)]
    FED = [(308.0, 683.0), (232.0, 683.0), (318.0, 748.0)]
    # vertices: ABC = [A, B, C]; FED listed as [E, F, D] so that index i matches index i
    pair("l3_r_mc", ABC, FED, I3,
         dict(names=["A", "B", "C"], ticks={(0, 1): 1}, marks={0: "x", 1: "dot"}),
         dict(names=["E", "F", "D"], ticks={(0, 1): 1}, marks={0: "x", 1: "dot"}), s=1.25)
    # MC 10: parallelogram ABCD (A top-left, B top-right, C bottom-right, D bottom-left), dashed AC
    A, B, C, D = (0.6, 1.3), (3.2, 1.3), (2.6, 0), (0, 0)
    S = Scene(dict(A=A, B=B, C=C, D=D), k=36)
    S.seg("AB", "BC", "CD", "DA").seg("AC", dash=True)
    S.tick("AB", 1).tick("DC", 1).tick("AD", 2).tick("BC", 2)
    S.names().save("l3_r_mc10")
    # SA 8: congruent darts ABCD and EFGH (EFGH is a rotation of ABCD)
    src = [(118.0, 363.0), (172.0, 390.0), (197.0, 378.0), (160.0, 437.0)]
    dst = [(283.0, 436.0), (333.0, 412.0), (360.0, 423.0), (330.0, 367.0)]
    img = iso(src, dst)
    k = 1.25
    src = [(x * k, y * k) for x, y in src]
    img = [(x * k, y * k) for x, y in img]
    (Q1, Q2), W, H = shift_all([src, img], pad=20)
    from figs import CF as _CF
    f = _CF(W, H)
    f.poly(Q1, color=None, opacity=0, stroke=BLUE, width=1.5)
    f.poly(Q2, color=None, opacity=0, stroke=BLUE, width=1.5)
    for Q, nm in ((Q1, "ABCD"), (Q2, "EFGH")):
        for i, n in enumerate(nm):
            v = Q[i]
            a, b = Q[i - 1], Q[(i + 1) % 4]
            u1 = (a[0] - v[0], a[1] - v[1])
            u2 = (b[0] - v[0], b[1] - v[1])
            l1, l2 = hypot(*u1), hypot(*u2)
            bx, by = u1[0] / l1 + u2[0] / l2, u1[1] / l1 + u2[1] / l2
            L = hypot(bx, by) or 1
            c = centroid(Q)
            # outside the shape: away from the bisector into the shape (for the reflex vertex, the bisector side)
            inside_dir = (bx / L, by / L)
            from figs_l2 import _clean as _c2
            from svg_overlap import check_string
            cross = u1[0] * u2[1] - u1[1] * u2[0]
            base = len(f.items)
            for dd in (12, 15, 19):
                for sgn in (-1, 1):
                    f.items = f.items[:base]
                    f.text(v[0] + sgn * dd * inside_dir[0], v[1] + sgn * dd * inside_dir[1] + 4.5, n, size=12.5, italic=True)
                    if _c2(f, n) and _outside(Q, (v[0] + sgn * dd * inside_dir[0], v[1] + sgn * dd * inside_dir[1])):
                        break
                else:
                    continue
                break
    save("l3_r8", f)
    # SA 9 a: RHS
    pair("l3_r9a", [(128.0, 596.0), (186.0, 596.0), (128.0, 692.0)], [(208.0, 707.0), (265.0, 707.0), (208.0, 610.0)], I3,
         dict(marks={0: "R"}, ticks={(0, 1): 1, (1, 2): 2}), dict(marks={0: "R"}, ticks={(0, 1): 1, (1, 2): 2}),
         canon=tri_sas(0, 1, 2, 58, 96, 90), s=1.2)
    # b: SAS (included angle marked with a dot)
    pair("l3_r9b", [(540.0, 690.0), (492.0, 690.0), (452.0, 600.0)], [(522.0, 593.0), (568.0, 593.0), (608.0, 686.0)], I3,
         dict(marks={0: "dot"}, ticks={(0, 1): 1, (0, 2): 2}), dict(marks={0: "dot"}, ticks={(0, 1): 1, (0, 2): 2}),
         canon=tri_sas(0, 1, 2, 48, 126, 45), s=1.2)
    # c: SSS
    pair("l3_r9c", [(180.0, 735.0), (128.0, 827.0), (197.0, 827.0)], [(277.0, 827.0), (226.0, 735.0), (295.0, 735.0)], I3,
         dict(ticks={(0, 1): 3, (0, 2): 2, (1, 2): 1}), dict(ticks={(0, 1): 3, (0, 2): 2, (1, 2): 1}), s=1.2)
    # d: AAS
    pair("l3_r9d", [(452.0, 810.0), (550.0, 732.0), (540.0, 805.0)], [(662.0, 840.0), (586.0, 780.0), (598.0, 733.0)], I3,
         dict(marks={0: "x", 2: "dot"}, ticks={(0, 1): 2}), dict(marks={0: "x", 2: "dot"}, ticks={(0, 1): 2}),
         canon=tri_angles((42, 30, 108), (0, 1, 125)), s=1.2)
    # SA 10 a: a at the top (matching 25 degrees), dot angles, x cm matching 3 cm
    pair("l3_r10a", [(128.0, 900.0), (193.0, 972.0), (160.0, 1015.0)], [(258.0, 1022.0), (285.0, 927.0), (238.0, 905.0)], I3,
         dict(angles={0: "a°"}, marks={1: "dot"}, sides={(1, 2): "x cm"}),
         dict(angles={0: "25°"}, marks={1: "dot"}, sides={(1, 2): "3 cm"}),
         canon=tri_angles((25, 100, 55), (1, 2, 3)), s=1.25)
    # SA 10 b: parallelogram with a diagonal; 18 degrees and a (alternate), 5 m and x m (opposite sides)
    L = (0, 0)
    u = pol(4.3, 13.0)
    w = pol(3.75, -5.0)
    TR, BRv = u, w
    BL = (BRv[0] - u[0], BRv[1] - u[1])
    S = Scene(dict(_L=L, _T=TR, _R=BRv, _B=BL), k=40)
    S.seg("_L_T", "_T_R", "_R_B", "_B_L", "_L_R")
    S.arrow("_L_T", 2, t=0.82).arrow("_B_R", 2, t=0.22).arrow("_B_L", 1, t=0.55).arrow("_R_T", 1, t=0.55)
    S.alab("_T_L_R", "18°").alab("_B_R_L", "a°")
    S.slab("_T_R", "5 m").slab("_B_L", "x m")
    S.save("l3_r10b")
    # SA 12: square ABCD, diagonals meet at E, AE = EC
    s = 2.0
    S = Scene(dict(A=(0, 0), B=(s, 0), C=(s, s), D=(0, s), E=(s / 2, s / 2)), k=40)
    S.seg("AB", "BC", "CD", "DA", "AC", "BD")
    for s_ in ("AB", "BC", "DC", "AD"):
        S.tick(s_, 2)
    S.tick("AE", 1).tick("EC", 1)
    S.names().save("l3_r12")


def _outside(Q, p):
    n, c = len(Q), False
    for i in range(n):
        (x1, y1), (x2, y2) = Q[i], Q[(i + 1) % n]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return not c


if __name__ == "__main__":
    fig_start(); fig_ex13(); fig_c1_demos(); fig_keyideas(); fig_c2_demos()
    fig_q1(); fig_q2(); fig_q4(); fig_q5(); fig_q6(); fig_q8_q9(); fig_q10_q13(); fig_q15_q17()
    fig_pp(); fig_review()
