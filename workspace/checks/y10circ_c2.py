r"""Check of Lesson C2 (Year 10 Circle Geometry: angles at the centre and circumference), tied to the HTML.

Reads build/y10circ/lc2.html, a_c2.html and the lesson figures svg/c2*.svg.
  - Every printed number in the answers and the lesson's worked results is a <span data-v="KEY">; each
    key must occur exactly once and every key must be checked. The two answers that are expressions in
    theta (PP 5) are evaluated at a measured theta.
  - Given angles are read from the figure labels (svg text) or from the question text.
  - Every answer is recomputed with coordinates on a circle: points are placed by bisection on a measured
    angle (never by the theorem being taught), and the answer is then MEASURED (angles by the dot
    product, arcs / angles at the centre from the polar angles of the points, so reflex angles come out
    directly, circumradii from the circumcentre).
Exit status 1 on any failure.  Run: python3 workspace/checks/y10circ_c2.py
"""
import os
import re
import sys
from math import cos, sin, radians, degrees, atan2, hypot, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y10circ_common import Values, check, svg_has, svg_labels, ok, finish, read, ang, dist  # noqa: E402

V = Values(["a_c2.html", "lc2.html"])
LES = read("lc2.html")
O = (0.0, 0.0)


def U(deg, r=1.0):
    return (r * cos(radians(deg)), r * sin(radians(deg)))


def polar(p):
    return degrees(atan2(p[1], p[0])) % 360


def bisect(f, lo, hi, n=200):
    flo = f(lo)
    for _ in range(n):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def setup(insc):
    """A, B symmetric about the top of the unit circle, P at the bottom, placed so that angle APB = insc."""
    s = bisect(lambda s: ang(U(270), U(90 + s), U(90 - s)) - insc, 1e-7, 180 - 1e-7)
    A, B, P = U(90 + s), U(90 - s), U(270)
    ok(abs(ang(P, A, B) - insc) < 1e-9, f"setup({insc}) angle placed")
    return A, B, P


def arc_top(A, B):
    """Angle at the centre on the side of the top point (from A anticlockwise... measured from polar angles)."""
    return (polar(A) - polar(B)) % 360


def central_for(insc):
    A, B, P = setup(insc)
    return arc_top(A, B)


def insc_for(central):
    """A, B placed with the given angle at the centre (on the top side); the angle measured at three points of the other arc."""
    A, B = U(90 + central / 2), U(90 - central / 2)
    vals = [ang(U(q), A, B) for q in (270 - 0.3 * (180 - central / 2), 270, 270 + 0.2 * (180 - central / 2))]
    ok(max(vals) - min(vals) < 1e-9, f"insc_for({central}): same at three points")
    return vals[0]


def same_arc(insc):
    A, B, P = setup(insc)
    s = degrees(atan2(A[1], A[0])) - 90
    q = 270 + 0.4 * (180 - s)                 # another point of the bottom arc
    return ang(U(q), A, B)


def opposite(insc):
    A, B, P = setup(insc)
    return ang(U(90), A, B)                   # fourth vertex on the top arc: APBT is a cyclic quadrilateral


def exterior(insc):
    A, B, P = setup(insc)
    T = U(90)
    E = (2 * T[0] - A[0], 2 * T[1] - A[1])    # AT produced beyond T
    return ang(T, E, B)


def deg_labels(fig):
    return [float(l[:-1]) for l in svg_labels(fig) if re.fullmatch(r"\d+(\.\d+)?°", l)]


def one(fig):
    g = deg_labels(fig)
    ok(len(g) == 1, f"{fig}: one given angle read", str(g))
    return g[0] if g else float("nan")


# ---------------- Lesson examples ----------------
check(V, "d1a", central_for(one("c2d1a")), label="centre angle measured")
check(V, "d1b", insc_for(one("c2d1b")), label="angle at circumference measured")
check(V, "d1c", central_for(one("c2d1c")), label="reflex centre angle measured")
check(V, "y1a", central_for(one("c2y1a")))
check(V, "y1b", insc_for(one("c2y1b")))
check(V, "y1c", central_for(one("c2y1c")))
check(V, "w_q3a", central_for(one("c2q3a")), label="MP Q3(a) worked")
for k in ("d2a", "d2b", "y2a", "y2b"):
    check(V, k, same_arc(one("c2" + k)), label="same arc, measured at another point")
check(V, "w_q4a", same_arc(one("c2q4a")), label="MP Q4(a) worked")
for k in ("d3a", "d3b", "y3a", "y3b"):
    check(V, k, opposite(one("c2" + k)), label="opposite vertex measured")
check(V, "w_q6a", opposite(one("c2q6a")), label="MP Q6(a) worked")
for k in ("d3c", "y3c"):
    check(V, k, exterior(one("c2" + k)), label="exterior angle measured")


def quad(aA, aB, aC, L1=0.9):
    """Quadrilateral with interior angles A, B, C (A at the origin, AB along the x-axis); D where the rays meet."""
    A, B = (0.0, 0.0), (1.0, 0.0)
    dB = radians(180 - aB)                     # direction of BC
    C = (B[0] + L1 * cos(dB), B[1] + L1 * sin(dB))
    dC = dB + radians(180 - aC)                # direction of CD
    dA = radians(aA)                           # direction of AD
    # solve C + t (cos dC, sin dC) = s (cos dA, sin dA)
    a11, a12, b1 = cos(dC), -cos(dA), -C[0]
    a21, a22, b2 = sin(dC), -sin(dA), -C[1]
    det = a11 * a22 - a12 * a21
    t = (b1 * a22 - a12 * b2) / det
    D = (C[0] + t * cos(dC), C[1] + t * sin(dC))
    ok(abs(ang(A, B, D) - aA) < 1e-9 and abs(ang(B, A, C) - aB) < 1e-9 and abs(ang(C, B, D) - aC) < 1e-9, f"quad({aA},{aB},{aC}) built")
    # circumcircle of A, B, C; is D on it?
    ax, ay, bx, by, cx, cy = A[0], A[1], B[0], B[1], C[0], C[1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    R = hypot(ax - ux, ay - uy)
    return ang(D, C, A), abs(hypot(D[0] - ux, D[1] - uy) - R)


def nums(pattern, k=1):
    m = re.findall(pattern, LES)
    ok(len(m) >= k, f"text givens: {pattern}", str(m[:2]))
    return [float(x) for x in m[k - 1]]


aA, aB, aC = nums(r"\\angle [AP]=(\d+)\^\\circ\\\), \\\(\\angle [BQ]=(\d+)\^\\circ\\\) and \\\(\\angle [CR]=(\d+)\^\\circ", 1)
Dm, off = quad(aA, aB, aC)
check(V, "d4", Dm, label="angle D measured")
check(V, "d4_AC", aA + aC)
ok(off < 1e-9, "demo C4: D lies on the circle through A, B, C (cyclic)", f"offset {off:.2e}")
aA, aB, aC = nums(r"\\angle [AP]=(\d+)\^\\circ\\\), \\\(\\angle [BQ]=(\d+)\^\\circ\\\) and \\\(\\angle [CR]=(\d+)\^\\circ", 2)
Dm, off = quad(aA, aB, aC)
check(V, "y4", Dm, label="angle S measured")
check(V, "y4_PR", aA + aC)
ok(off > 1e-3, "your turn C4: S is not on the circle through P, Q, R (not cyclic)", f"offset {off:.4f}")


def circumradius(a, A, B=70.0):
    """Triangle with BC = a, angle B given and angle A placed by bisection; circumradius from the circumcentre."""
    Bp, Cp = (0.0, 0.0), (a, 0.0)

    def apex(Cang):
        # A from B along angle B, from C along angle Cang
        dB, dC = radians(B), radians(180 - Cang)
        t = a * sin(radians(Cang)) / sin(radians(180 - B - Cang))
        return (t * cos(dB), t * sin(dB))
    Cang = bisect(lambda c: ang(apex(c), Bp, Cp) - A, 1e-6, 180 - B - 1e-6)
    Ap = apex(Cang)
    ax, ay, bx, by, cx, cy = Ap[0], Ap[1], Bp[0], Bp[1], Cp[0], Cp[1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return hypot(ax - ux, ay - uy)


a1, A1 = nums(r"\\triangle ABC\\\), \\\(a=(\d+)\\\) cm and \\\(A=(\d+)\^\\circ", 1)
R1 = circumradius(a1, A1)
check(V, "d5_2R", 2 * R1); check(V, "d5", R1)
a2, A2 = nums(r"\\triangle ABC\\\), \\\(a=(\d+)\\\) cm and \\\(A=(\d+)\^\\circ", 2)
check(V, "y5", round(circumradius(a2, A2), 2), label=f"R = {circumradius(a2, A2):.5f} to 2 dp")

# ---------------- Homework ----------------
check(V, "h2b", insc_for(one("c2q3b")))
check(V, "h2c", central_for(one("c2q3c")))
check(V, "h2d", insc_for(one("c2q3d")))
g = one("c2q3e"); check(V, "h2e_x", central_for(g)); check(V, "h2e_y", same_arc(g))
g = one("c2q3f"); check(V, "h2f_x", central_for(g)); check(V, "h2f_z", same_arc(g))
check(V, "h3b", same_arc(one("c2q4b"))); check(V, "h3c", same_arc(one("c2q4c")))
check(V, "h4b", opposite(one("c2q6b")))
ok("y" in svg_labels("c2q6c"), "c2q6c: right angle marked, y shown")
check(V, "h4c", opposite(90))
check(V, "h5b", same_arc(one("c2q8b"))); check(V, "h5c", opposite(one("c2q8c"))); check(V, "h5d", central_for(one("c2q8d")))
# Q5 (reflex angles)
check(V, "h6a", central_for(one("c2q5a")), label="reflex measured")
check(V, "h6b", insc_for(one("c2q5b")))
g = one("c2q5c"); A, B = U(90 + g / 2), U(90 - g / 2); check(V, "h6c", (polar(B) - polar(A)) % 360, label="reflex arc measured")
g = one("c2q5d"); A, B = U(90 + g / 2), U(90 - g / 2); check(V, "h6d", (polar(B) - polar(A)) % 360)
g = one("c2q5e"); A, B = U(90 + g / 2), U(90 - g / 2); check(V, "h6e_p", insc_for(g)); check(V, "h6e_q", (polar(B) - polar(A)) % 360)
g = one("c2q5f"); A, B = U(90 + g / 2), U(90 - g / 2); check(V, "h6f_x", (polar(B) - polar(A)) % 360); check(V, "h6f_y", ang(U(90), A, B), label="angle at a point of the minor arc")
g = one("c2q5g"); A, B, P = setup(g); a_ = arc_top(A, B); check(V, "h6g_a", a_); check(V, "h6g_b", (polar(B) - polar(A)) % 360); check(V, "h6g_c", ang(U(90), A, B))
g = one("c2q5h"); A, B = U(90 + g / 2), U(90 - g / 2); check(V, "h6h_x", (polar(B) - polar(A)) % 360); check(V, "h6h_y", ang(U(90), A, B)); check(V, "h6h_z", ang(U(270), A, B))
g = one("c2q5i"); A, B, P = setup(g); f_ = arc_top(A, B); check(V, "h6i_f", f_); check(V, "h6i_g", (polar(B) - polar(A)) % 360); check(V, "h6i_h", ang(U(90), A, B))

# Q16: Sydney Boys 2021 Part G (e), a scalene triangle
from math import sqrt as _s


def eq_out(p, q, away):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    h = _s(3) / 2
    c1, c2 = (mx - h * dy, my + h * dx), (mx + h * dy, my - h * dx)
    return c1 if dist(c1, away) > dist(c2, away) else c2


def circumc(a, b, c):
    ax, ay, bx, by, cx, cy = a[0], a[1], b[0], b[1], c[0], c[1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    return (((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d,
            ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d)


for (A, B, C) in (((0.0, 0.0), (5.0, 0.3), (1.7, 3.9)), ((0.0, 0.0), (6.2, 0.0), (2.1, 2.4))):
    X, Y, Z = eq_out(A, B, C), eq_out(B, C, A), eq_out(A, C, B)
    P, Q, R = circumc(A, B, X), circumc(B, C, Y), circumc(A, C, Z)
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    t = ((B[0] - P[0]) * dx + (B[1] - P[1]) * dy) / (dx * dx + dy * dy)
    Fp = (P[0] + t * dx, P[1] + t * dy)
    Op = (2 * Fp[0] - B[0], 2 * Fp[1] - B[1])
    ok(abs(dist(Op, R) - dist(A, R)) < 1e-9, "Napoleon: O lies on circle AOCZ")
    sides = sorted([dist(P, Q), dist(Q, R), dist(R, P)])
    ok(sides[2] - sides[0] < 1e-9, "Napoleon: PQR equilateral", str([round(s, 6) for s in sides]))
    res = (ang(Op, A, B), ang(Op, B, C), ang(Op, A, C), ang(P, R, Q))
check(V, "h16_AOB", res[0]); check(V, "h16_BOC", res[1]); check(V, "h16_AOC", res[2]); check(V, "h16_RPQ", res[3])

# ---------------- Past papers ----------------
# PP1: exterior angle 76 at D (E on CD produced); angle ABC
g = one("c2pp1")
C_, D_, B_ = U(265), U(15), U(165)
t = bisect(lambda t: ang(D_, U(t), (2 * D_[0] - C_[0], 2 * D_[1] - C_[1])) - g, 16, 164)
A_ = U(t)
check(V, "pp1", ang(B_, A_, C_), label="angle ABC measured")
# PP2: diameter AC, angle BAC = 55, D on the lower arc
g = one("c2pp2")
A_, C_ = U(180), U(0)
tb = bisect(lambda t: ang(A_, U(t), C_) - g, 1e-6, 180 - 1e-6)
B_ = U(tb)
D_ = U(297)
check(V, "pp2_ABC", ang(B_, A_, C_)); check(V, "pp2_BCA", ang(C_, B_, A_)); check(V, "pp2", ang(D_, A_, B_))
# PP3: angle BCA = 46, angle DAC = 55; X = AC meet BD; m = angle BXA
gl = deg_labels("c2pp3")
ok(sorted(gl) == [46.0, 55.0], "c2pp3 givens read", str(gl))
A_, C_ = U(330), U(125)
tB = bisect(lambda t: ang(C_, U(t), A_) - 46, 331, 484)
B_ = U(tB)
tD = bisect(lambda t: ang(A_, U(t), C_) - 55, 126, 329)
D_ = U(tD)


def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


X_ = inter(A_, C_, B_, D_)
check(V, "pp3_CBD", ang(B_, C_, D_)); check(V, "pp3", ang(X_, B_, A_), label="angle BXA measured")
# PP4: AOB a diameter, angle ADO = 40; x = angle DCB
g = one("c2pp4") if len(deg_labels("c2pp4")) == 1 else 40.0
A_, B_ = U(145), U(325)
tD = bisect(lambda t: ang(U(t), A_, O) - g, 146, 320)
D_ = U(tD)
C_ = U(tD + 0.55 * (325 - tD))
check(V, "pp4_OAD", ang(A_, O, D_)); check(V, "pp4", ang(C_, D_, B_), label="angle DCB measured")
# PP5: AB || ED, C on the arc between B and D; expressions in theta evaluated at the measured theta
for cdeg in (335, 345):
    A_, B_, E_, D_, C_ = U(160), U(20), U(230), U(310), U(cdeg)
    F_ = inter(A_, D_, B_, E_)
    x_, y_, th = ang(A_, B_, D_), ang(F_, E_, D_), ang(C_, B_, D_)
    ok(abs(2 * x_ + y_ - 180) < 1e-9, f"PP5(i) 2x + y = 180 measured (C at {cdeg})")
    for key, val in (("pp5_x", x_), ("pp5_y", y_)):
        V.used.add(key)
        raw = V.d.get(key, [])
        ok(len(raw) == 1, f"data-v={key} found once")
        if raw:
            expr0 = re.sub(r"\\\(|\\\)", "", raw[0]).split("=", 1)[1]
            expr = re.sub(r"(\d)\\theta", r"\1*\\theta", expr0).replace("\\theta", f"({th})")
            ok(abs(eval(expr) - val) < 1e-9, f"{key} printed '{raw[0]}' at theta = {th:.4f}", f"{eval(expr):.6f} vs measured {val:.6f}")

svg_has("c2pp5", "x", "θ", "y")
finish([V])
