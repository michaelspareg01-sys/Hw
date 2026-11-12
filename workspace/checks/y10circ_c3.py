r"""Check of Lesson C3 (Year 10 Circle Geometry: tangents and secants) and the chapter review, tied to the HTML.

Reads build/y10circ/lc3.html, a_c3.html and the lesson figures svg/c3*.svg.
  - Every printed number in the answers and the lesson's worked results is a <span data-v="KEY">; each key
    must occur exactly once and every key must be checked. The one answer that is an expression in theta
    (PP 1) is a <span data-e="KEY"> and is evaluated at two measured values of theta.
  - Given lengths and angles are read from the figure labels (svg text) or the question text.
  - Every configuration is BUILT with coordinates from the given data: points on circles, tangent points
    from the external point, and unknown positions found by bisection on a measured length or angle (never
    with the theorem being taught). The answer is then MEASURED: angles by the dot product, lengths by
    distance, intercepts as distances to the intersection points of a line with the circle. The products of
    the intercepts are therefore checked numerically, not assumed.
  - The construction of the Sydney Boys 2023 two-circle figure is checked: A, P, C collinear and
    angle APX = angle DPQ.
Exit status 1 on any failure.  Run: python3 workspace/checks/y10circ_c3.py
"""
import os
import re
import sys
from math import cos, sin, radians, degrees, atan2, hypot, sqrt, acos, pi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y10circ_common import Values, check, svg_labels, ok, finish, read, ang, dist  # noqa: E402

V = Values(["a_c3.html", "lc3.html"])
LES = read("lc3.html")
ANS = read("a_c3.html")
O = (0.0, 0.0)


def U(deg, r=1.0, c=O):
    return (c[0] + r * cos(radians(deg)), c[1] + r * sin(radians(deg)))


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


def hits(p, d, c, r):
    """Intersections of the line p + t d (d a unit vector) with the circle, as (t, point), sorted by t."""
    px, py = p[0] - c[0], p[1] - c[1]
    b = px * d[0] + py * d[1]
    disc = b * b - (px * px + py * py - r * r)
    if disc < 0:
        return []
    s = sqrt(disc)
    return [(t, (p[0] + t * d[0], p[1] + t * d[1])) for t in (-b - s, -b + s)]


def unit(v):
    L = hypot(*v)
    return (v[0] / L, v[1] / L)


def tangent_points(P, c=O, r=1.0):
    """Points of contact of the tangents from P (by the right angle at the point of contact)."""
    d = dist(P, c)
    a0 = degrees(atan2(P[1] - c[1], P[0] - c[0]))
    h = degrees(acos(r / d))
    return U(a0 + h, r, c), U(a0 - h, r, c)


def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def labels_num(fig):
    out = []
    for l in svg_labels(fig):
        m = re.fullmatch(r"(\d+(?:\.\d+)?)(°| cm)?", l)
        if m:
            out.append(float(m.group(1)))
    return out


def deg_labels(fig):
    return [float(l[:-1]) for l in svg_labels(fig) if re.fullmatch(r"\d+(\.\d+)?°", l)]


def one_deg(fig):
    g = deg_labels(fig)
    ok(len(g) == 1, f"{fig}: one given angle read", str(g))
    return g[0] if g else float("nan")


# ---------------- intersecting chords: build and measure ----------------
def chord_other(a1, b1, a2, phi=57.0, R=None):
    """Chord 1 has intercepts a1, b1 at M. A second chord through M, turned so that one intercept is a2
    (bisection on its direction); return the measured other intercept."""
    R = R or (a1 + b1) / 2 * 1.37
    h = sqrt(R * R - ((a1 + b1) / 2) ** 2)
    A, B = (-(a1 + b1) / 2, h), ((a1 + b1) / 2, h)
    M = (A[0] + a1, h)

    def near(phi_):
        d = (cos(radians(phi_)), sin(radians(phi_)))
        (t0, P0), (t1, P1) = hits(M, d, O, R)
        return dist(M, P1), dist(M, P0)
    lo, hi = 1.0, 179.0
    f = lambda p: near(p)[0] - a2  # noqa: E731
    vals = [f(181 + k) for k in range(0, 358)]
    k = next(i for i in range(len(vals) - 1) if (vals[i] > 0) != (vals[i + 1] > 0))
    p = bisect(f, 181 + k, 182 + k)
    first, other = near(p)
    ok(abs(first - a2) < 1e-9, f"chord_other({a1},{b1},{a2}) placed")
    ok(abs(dist(A, M) - a1) < 1e-12 and abs(dist(M, B) - b1) < 1e-12, f"chord_other({a1},{b1}) first chord built")
    return other


def secant_build(o1, w1, R=None, need=None):
    """Circle centre O, radius R; external point M with a secant whose outer part is o1 and whole is w1.
    need = (value, 'o' or 'w'): the radius is made large enough for a second secant with that outer part / whole."""
    R = R or (w1 - o1) / 2 * 1.3
    if need:
        P_, (kv, wh) = o1 * w1, need
        R = max(R, 1.3 * ((P_ - kv * kv) / (2 * kv) if wh == "o" else (kv * kv - P_) / (2 * kv)))
    d = sqrt(o1 * w1 + R * R)                       # chosen so that the measured intercepts are o1 and w1 (checked)
    M = (d, 0.0)
    psi = acos((o1 + w1) / (2 * d))
    dd = (-cos(psi), sin(psi))
    (t0, P0), (t1, P1) = hits(M, dd, O, R)
    ok(abs(t0 - o1) < 1e-9 and abs(t1 - w1) < 1e-9, f"secant_build({o1},{w1}) intercepts measured")
    return M, R


def secant_other(o1, w1, known, which):
    """Second secant from the same M with outer part (which='o') or whole (which='w') equal to known."""
    M, R = secant_build(o1, w1, need=(known, which))

    def meas(psi):
        dd = (-cos(radians(psi)), -sin(radians(psi)))
        hs = hits(M, dd, O, R)
        return hs[0][0], hs[1][0]
    lim = degrees(acos(sqrt(1 - (R / dist(M, O)) ** 2))) - 1e-7      # the tangent direction
    lim = degrees(atan2(R, sqrt(dist(M, O) ** 2 - R ** 2))) - 1e-7
    f = (lambda p: meas(p)[0] - known) if which == "o" else (lambda p: meas(p)[1] - known)
    p = bisect(f, 0.0, lim)
    o2, w2 = meas(p)
    return (w2 if which == "o" else o2)


def tangent_from(o1, w1):
    M, R = secant_build(o1, w1)
    T1, T2 = tangent_points(M, O, R)
    ok(abs(ang(T1, O, M) - 90) < 1e-9, "tangent point: right angle at T")
    return dist(M, T1)


# ---------------- Concept 1 ----------------
g = one_deg("c3d1a")
T = (0.0, -1.0)
tang = (1.0, -1.0)
q = (cos(radians(g)), -1 + sin(radians(g)))
check(V, "d1a", ang(T, O, q), label="angle between radius and the line, measured")
g = one_deg("c3y1a")
q = (cos(radians(g)), -1 + sin(radians(g)))
check(V, "y1a", ang(T, O, q))
g = one_deg("c3q8a")
q = (cos(radians(g)), -1 + sin(radians(g)))
m = re.search(r"Q8\(a\): keep for homework.*?x&amp;=(\d+)\^\\circ", LES, re.S)
ok(m is not None and abs(float(m.group(1)) - ang(T, O, q)) < 1e-9, "lesson MP Q8(a) x measured", m.group(1) if m else "")
V.d.pop("w_q8a", None)
for key, fig in (("d1b", "c3d1b"), ("y1b", "c3y1b")):
    r_, op = sorted(labels_num(fig))
    P = (op, 0.0)
    T1, _ = tangent_points(P, O, r_)
    check(V, key, dist(P, T1), label="tangent length measured")


# ---------------- Concept 2 ----------------
def two_tangents(angle_at_A):
    """External point A at distance d placed by bisection so that the measured angle between the tangents is given."""
    def angle(d):
        T1, T2 = tangent_points((d, 0.0))
        return ang((d, 0.0), T1, T2)
    d = bisect(lambda d: angle(d) - angle_at_A, 1.0000001, 200)
    A = (d, 0.0)
    T1, T2 = tangent_points(A)
    return A, T1, T2


for key, fig in (("d2a", "c3d2a"), ("y2a", "c3y2a")):
    gg = float(re.search(r"\\angle CAB=(\d+)\^\\circ", LES[LES.index(f"svg:{fig}") - 400:LES.index(f"svg:{fig}")]).group(1))
    A, B, C = two_tangents(gg)
    check(V, key, ang(O, B, C), label="angle COB measured")
A, B, C = two_tangents(70)
m = re.search(r"\\angle COB&amp;=(\d+)\^\\circ\\end", LES)
ok(m is not None and abs(float(m.group(1)) - ang(O, B, C)) < 1e-9, "lesson MP Q9(a) angle COB measured", m.group(1) if m else "")
for key, fig in (("d2b", "c3d2b"), ("y2b", "c3y2b")):
    gg = one_deg(fig)

    def angPAB(d):
        A, B = tangent_points((d, 0.0))
        return ang(A, (d, 0.0), B)
    d = bisect(lambda d: angPAB(d) - gg, 1.0000001, 200)
    A, B = tangent_points((d, 0.0))
    check(V, key, ang((d, 0.0), A, B), label="angle APB measured")


# ---------------- Concept 3: alternate segment ----------------
def alt_setup(tangent_chord=None, inscribed=None):
    A = (0.0, -1.0)
    Uu = (2.0, -1.0)                                # tangent at A (perpendicular to OA)

    def B_of(t):
        return U(t)
    if tangent_chord is not None:
        t = bisect(lambda t: ang(A, B_of(t), Uu) - tangent_chord, -89.999, 269.999 - 180)
    else:
        P = U(150.0)
        t = bisect(lambda t: ang(U(200.0), A, B_of(t)) - inscribed, -89.999, 89.0)
    B = B_of(t)
    P = U(t + 0.55 * (270 - t + 0.0) if False else (t + (270 - t) * 0.55))
    return A, B, P, Uu


for key in ("d3a", "y3a"):
    gg = one_deg("c3" + key)
    A, B, P, Uu = alt_setup(tangent_chord=gg)
    ok(abs(ang(A, B, Uu) - gg) < 1e-9, f"{key} placed")
    check(V, key, ang(P, A, B), label="angle in the alternate segment measured")
for key in ("d3b", "y3b"):
    gg = one_deg("c3" + key)
    A = (0.0, -1.0)
    Uu = (2.0, -1.0)
    P = U(150.0)
    t = bisect(lambda t: ang(P, A, U(t)) - gg, -89.999, 120.0)
    B = U(t)
    ok(abs(ang(P, A, B) - gg) < 1e-9, f"{key} placed")
    check(V, key, ang(A, B, Uu), label="tangent-chord angle measured")


# ---------------- Concept 4 and 5: products of intercepts, measured ----------------
def fig_lengths(fig):
    return labels_num(fig)


l = fig_lengths("c3d4a")      # 6, 4, 3, x
ok(l == [6.0, 4.0, 3.0], "c3d4a lengths read", str(l))
check(V, "d4a", chord_other(6, 4, 3), label="other intercept measured")
l = fig_lengths("c3d4b")
ok(l == [5.0, 8.0, 10.0], "c3d4b lengths read", str(l))
check(V, "d4b", chord_other(5, 8, 10))
l = fig_lengths("c3y4a")
ok(l == [9.0, 2.0, 3.0], "c3y4a lengths read", str(l))
check(V, "y4a", chord_other(9, 2, 3))
l = fig_lengths("c3y4b")
ok(l == [4.0, 6.0, 8.0], "c3y4b lengths read", str(l))
check(V, "y4b", chord_other(4, 6, 8))
l = fig_lengths("c3iq3a")
ok(l == [6.0, 5.0, 12.0], "c3iq3a lengths read", str(l))
m = re.search(r"Q3\(a\): keep for homework.*?&amp;=(\d+)\\end", LES, re.S)
ok(m is not None and abs(float(m.group(1)) - chord_other(5, 12, 6)) < 1e-9, "lesson MP Q3(a) x measured", m.group(1) if m else "")
V.d.pop("w_iq3a", None)
l = fig_lengths("c3iq3b")
ok(sorted(l) == [3.0, 4.0, 8.0], "c3iq3b lengths read", str(l))
check(V, "h4b", chord_other(8, 3, 4))
l = fig_lengths("c3iq3c")
ok(sorted(l) == [3.0, 3.0, 4.0], "c3iq3c lengths read", str(l))
check(V, "h4c", chord_other(3, 3, 4))
l = fig_lengths("c3iq3d")
ok(sorted(l) == [1.0, 3.0, 6.0], "c3iq3d lengths read", str(l))
check(V, "h4d", chord_other(6, 1, 3))

# secants: (figure, outer of known secant, whole of known secant, known value on the other, which, key)
for fig, o1, w1, kn, wh, key in (("c3d5a", 16, 21, 12, "o", "d5a"), ("c3y5a", 14, 25, 10, "o", "y5a"),
                                 ("c3iq6b", 12, 40, 10, "o", "h6b"), ("c3iq6c", 5.25, 8, 7, "w", "h6c"),
                                 ("c3iq6d", 24, 30, 36, "w", "h6d")):
    l = sorted(fig_lengths(fig))
    ok(sorted([o1, w1, kn]) == l, f"{fig} lengths read", str(l))
    check(V, key, secant_other(o1, w1, kn, wh), label="other intercept measured on a built secant")
l = sorted(fig_lengths("c3iq6a"))
ok(l == [15.0, 18.0, 25.0], "c3iq6a lengths read", str(l))
m = re.search(r"Q6\(a\): keep for homework.*?&amp;=(\d+)\\end", LES, re.S)
ok(m is not None and abs(float(m.group(1)) - secant_other(18, 25, 15, "o")) < 1e-9, "lesson MP Q6(a) x measured", m.group(1) if m else "")
V.d.pop("w_iq6a", None)
for key, fig in (("d5b", "c3d5b"), ("y5b", "c3y5b")):
    l = fig_lengths(fig)
    ok(len(l) == 2, f"{fig} lengths read", str(l))
    check(V, key, tangent_from(l[0], l[0] + l[1]), label="tangent length measured")

# ---------------- homework ----------------
for key in ("h1a", "h1b"):
    T1, _ = tangent_points((3.0, 0.4))
    check(V, key, ang(T1, O, (3.0, 0.4)), label="radius and tangent at a constructed tangent point")
q = (0.0, 0.0)
T = U(121.0)
tdir = (cos(radians(31)), sin(radians(31)))
# MP Q8(b): the vertical line through T makes 31 deg with the radius; y is between it and the tangent
down = (T[0], T[1] - 2)
check(V, "h2", 90 - ang(T, down, O), label="angle between the tangent and the vertical line")
ok(abs(ang(T, down, O) - 31) < 1e-9, "Q8(b) construction: 31 deg between the line and the radius")
# MP Q9(b)
B = (0.0, -1.0)
D = (2.0, -1.0)
t = bisect(lambda t: ang(B, U(t), D) - 60, -89.99, 89.99)
C = U(t)
A = inter(C, O, (-9.0, -1.0), (9.0, -1.0))
check(V, "h7_OBC", ang(B, O, C)); check(V, "h7_BOC", ang(O, B, C)); check(V, "h7_BOA", ang(O, B, A)); check(V, "h7", ang(A, O, B))


def common_tangents(c1, r1, c2, r2):
    """Number of lines tangent to both circles: roots in phi of |n.(c2-c1) - r1| = r2 with n = (cos phi, sin phi),
    the line being n.x = n.c1 + r1. Sign changes and touching minima are both counted."""
    def g(ph):
        n = (cos(ph), sin(ph))
        return abs(n[0] * (c2[0] - c1[0]) + n[1] * (c2[1] - c1[1]) - r1) - r2
    N = 200000
    vals = [g(0.1234 + 2 * pi * k / N) for k in range(N + 1)]
    cnt = sum(1 for k in range(N) if (vals[k] > 0) != (vals[k + 1] > 0))
    cnt += sum(1 for k in range(1, N) if abs(vals[k]) < 1e-7 and ((vals[k - 1] > vals[k] < vals[k + 1]) or (vals[k - 1] < vals[k] > vals[k + 1]))
               and (vals[k - 1] > 0) == (vals[k + 1] > 0))
    return cnt


for key, (c1, r1, c2, r2) in (("h11_i", ((0, 0), 2, (0.4, 0), 1)), ("h11_ii", ((0, 0), 2, (1, 0), 1)), ("h11_iii", ((0, 0), 2, (2, 0), 1)),
                              ("h11_iv", ((0, 0), 2, (3, 0), 1)), ("h11_v", ((0, 0), 2, (4.5, 0), 1))):
    check(V, key, common_tangents(c1, r1, c2, r2), label="common tangent lines counted")

# ---------------- past papers ----------------
# PP1: tangents from T at angle theta; angle APB for P on the far arc; printed expression evaluated
raw = re.findall(r'<span data-e="pp1_TAB">(.*?)</span>', ANS)
ok(len(raw) == 1, "data-e=pp1_TAB found once")
expr = raw[0].split("=")[-1].replace("\\)", "").replace("^\\circ", "").replace("\\dfrac{\\theta}{2}", "(th/2)")
for th in (40.0, 73.0):
    Tp, A1, B1 = two_tangents(th)
    ta = degrees(atan2(A1[1], A1[0]))
    tb = degrees(atan2(B1[1], B1[0]))
    P = U(180.0)                                   # a point of the arc away from T
    meas = ang(P, A1, B1)
    ok(abs(eval(expr, {"th": th}) - meas) < 1e-9, f"PP1 angle APB at theta={th}", f"printed {expr} -> {eval(expr, {'th': th}):.6f}, measured {meas:.6f}")
    ok(abs(ang(A1, Tp, B1) - meas) < 1e-9, f"PP1 angle TAB equals APB at theta={th}")
ok("<b>B</b>" in ANS[ANS.index("PP 1"):ANS.index("PP 2")], "PP1 answer B")
# PP2: tangent AB, BC = 2, CD = 5
check(V, "pp2", tangent_from(2, 7) ** 2, label="AB^2 measured")
ok(abs(tangent_from(2, 7) - sqrt(14)) < 1e-9, "PP2 AB = sqrt 14 measured")
# PP3: chords 4 and 6; 5 and x
check(V, "pp3", chord_other(4, 6, 5), label="x measured")
# PP4
A = None


def angPAB(d):
    A, B = tangent_points((d, 0.0))
    return ang(A, (d, 0.0), B)


d = bisect(lambda d: angPAB(d) - 71, 1.0000001, 200)
A, B = tangent_points((d, 0.0))
check(V, "pp4", ang((d, 0.0), A, B))
# PP5: tangent at T; angle BTQ = 70; P on the far arc, R on the near arc
Tt = U(180.0)
Bt = (-1.0, -2.0)
t = bisect(lambda t: ang(Tt, Bt, U(t)) - 70, 180.001, 359.999)
Qq = U(t)
Pp, Rr = U(60.0), U((180 + t) / 2)
check(V, "pp5a", ang(Pp, Tt, Qq)); check(V, "pp5b", ang(Rr, Tt, Qq))
# PP6: secants from P: x outside then 3 inside; 4 outside then 6 inside
M_, R_ = secant_build(4, 10)


def outer_for_chord(chord):
    def meas(psi):
        dd = (-cos(radians(psi)), -sin(radians(psi)))
        hs = hits(M_, dd, O, R_)
        return hs[0][0], hs[1][0] - hs[0][0]
    lim = degrees(atan2(R_, sqrt(dist(M_, O) ** 2 - R_ ** 2))) - 1e-7
    p = bisect(lambda p: meas(p)[1] - chord, 0.0, lim)
    return meas(p)[0]


check(V, "pp6", outer_for_chord(3), label="x measured")
# PP7: angle RCQ = 70, tangents at R and Q meet at P
P7 = None
t = bisect(lambda t: ang(U(180), U(t), U(-t)) - 70, 0.001, 179.999)
R7, Q7 = U(t), U(-t)
P7 = inter(R7, (R7[0] - R7[1], R7[1] + R7[0]), Q7, (Q7[0] + Q7[1], Q7[1] - Q7[0]))
check(V, "pp7a", ang(O, R7, Q7)); check(V, "pp7b", ang(P7, R7, Q7))
# PP8: incircle; S from tangents at P and R with angle 34; T from tangents at P and Q with angle QPT = 46


def tl(p, q):
    return inter(p, (p[0] - p[1], p[1] + p[0]), q, (q[0] - q[1], q[1] + q[0]))


P8 = U(270.0)
r8 = bisect(lambda t: ang(tl(P8, U(t)), P8, U(t)) - 34, 90.001, 269.0)
R8 = U(r8)
S8 = tl(P8, R8)
q8 = bisect(lambda t: ang(P8, U(t), tl(P8, U(t))) - 46, -89.999, 89.0)
Q8 = U(q8)
T8 = tl(P8, Q8)
U8 = tl(Q8, R8)
V8 = inter(R8, Q8, S8, P8)
ok(abs(ang(S8, P8, R8) - 34) < 1e-9 and abs(ang(P8, Q8, T8) - 46) < 1e-9, "PP8 built with the given angles")
check(V, "pp8_SRP", ang(R8, S8, P8)); check(V, "pp8", ang(V8, P8, Q8), label="angle PVQ measured")

# Hard Q22: Sydney Boys 2023 two circles
O1, r1 = (0.0, 0.0), 1.0
O2, r2 = (0.95, -1.05), 0.68
dd = dist(O1, O2)
aa = (r1 * r1 - r2 * r2 + dd * dd) / (2 * dd)
h = sqrt(r1 * r1 - aa * aa)
u = unit((O2[0] - O1[0], O2[1] - O1[1]))
m_ = (O1[0] + aa * u[0], O1[1] + aa * u[1])
Pc = [(m_[0] - h * u[1], m_[1] + h * u[0]), (m_[0] + h * u[1], m_[1] - h * u[0])]
for P in Pc:
    tq = unit((-(P[1] - O2[1]), P[0] - O2[0]))
    tr = unit((-(P[1] - O1[1]), P[0] - O1[0]))
    Q = hits(P, tq, O1, r1)
    Q = max(Q, key=lambda z: abs(z[0]))[1]
    if dist(Q, P) < 1e-9:
        tq = (-tq[0], -tq[1])
    R = max(hits(P, tr, O2, r2), key=lambda z: abs(z[0]))[1]
    Q = max(hits(P, tq, O1, r1), key=lambda z: abs(z[0]))[1]
    D, A = (O1[0] + r1 * unit((Q[0] - P[0], Q[1] - P[1]))[0], O1[1] + r1 * unit((Q[0] - P[0], Q[1] - P[1]))[1]), None
    uq = unit((Q[0] - P[0], Q[1] - P[1]))
    ur = unit((R[0] - P[0], R[1] - P[1]))
    D, A = (O1[0] + r1 * uq[0], O1[1] + r1 * uq[1]), (O1[0] - r1 * uq[0], O1[1] - r1 * uq[1])
    Cc, Bb = (O2[0] + r2 * ur[0], O2[1] + r2 * ur[1]), (O2[0] - r2 * ur[0], O2[1] - r2 * ur[1])
    X = (P[0] - ur[0], P[1] - ur[1])
    cross = (A[0] - P[0]) * (Cc[1] - P[1]) - (A[1] - P[1]) * (Cc[0] - P[0])
    ok(abs(cross) < 1e-12 and ang(P, A, Cc) > 179.999, "SBHS 2023 F3(b): A, P, C collinear (measured)", f"angle APC = {ang(P, A, Cc):.9f}")
    ok(abs(ang(P, A, X) - ang(P, D, Q)) < 1e-9, "SBHS 2023 F3(a): angle APX = angle DPQ (measured)")

# ---------------- chapter review ----------------
# R1: AP = 6, PB = 4, CP = 2, AB perpendicular to CD
Pp = (0.0, 0.0)
A1, B1, C1 = (-6.0, 0.0), (4.0, 0.0), (0.0, 2.0)
ax, ay, bx, by, cx, cy = A1[0], A1[1], B1[0], B1[1], C1[0], C1[1]
dd = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / dd
uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / dd
Oc = (ux, uy)
Rr = dist(Oc, A1)
D1 = max(hits(Pp, (0.0, -1.0), Oc, Rr), key=lambda z: z[0])[1]
check(V, "r1_PD", dist(Pp, D1))
Rm = ((C1[0] + D1[0]) / 2, (C1[1] + D1[1]) / 2)
Qm = ((A1[0] + B1[0]) / 2, (A1[1] + B1[1]) / 2)
check(V, "r1_CR", dist(C1, Rm)); check(V, "r1_AQ", dist(A1, Qm)); check(V, "r1_OR", dist(Oc, Rm))
check(V, "r1sq", Rr ** 2, label="radius squared measured")
ok(abs(Rr - 5 * sqrt(2)) < 1e-9 and "OD=\\sqrt{50}=5\\sqrt2" in ANS, "R1 radius 5 sqrt 2 printed and measured")
# R2: diameter AB, angle ATP = 111
Aa, Bb = U(180.0), U(0.0)


def atp(t):
    T = U(t)
    P = inter(T, (T[0] - T[1], T[1] + T[0]), Aa, Bb)
    return ang(T, Aa, P)


t = bisect(lambda t: atp(t) - 111, 0.5, 89.5)
T2 = U(t)
P2 = inter(T2, (T2[0] - T2[1], T2[1] + T2[0]), Aa, Bb)
check(V, "r2_BTP", ang(T2, Bb, P2)); check(V, "r2", ang(Aa, Bb, T2))
# R3: two different semicircle radii, AE = 6 each time: the area is the same
for rr in (3.4, 4.2):
    def ae(dx):
        E = (dx, sqrt(rr * rr - dx * dx))
        return dist(E, (rr, 0.0))
    dx = bisect(lambda x: ae(x) - 6, -rr + 1e-9, rr - 1e-9)
    area = (rr - dx) * rr                        # AD x CD, with CD = height of the tangent line y = r
    if rr == 3.4:
        check(V, "r3", area, label=f"area measured (r = {rr})")
    else:
        ok(abs(area - 18) < 1e-9, f"R3 area also 18 with r = {rr}", f"{area:.9f}")
# R4: tangent at T (y = 0), TA = TC, angle ACT = 25
T4 = (0.0, 0.0)


def build4(a):
    A = (-a, 0.0)
    k = 1.0
    # C on the circle centre (0, k), radius k, with TC = a (bisection along the circle)
    t = bisect(lambda t: dist(T4, U(t, k, (0.0, k))) - a, -90.0, 90.0)
    C = U(t, k, (0.0, k))
    return A, C


a4 = bisect(lambda a: ang(build4(a)[1], build4(a)[0], T4) - 25, 0.05, 1.999)
A4, C4 = build4(a4)
Bh = hits(A4, unit((C4[0] - A4[0], C4[1] - A4[1])), (0.0, 1.0), 1.0)
B4 = Bh[0][1]
check(V, "r4_TAC", ang(A4, T4, C4)); check(V, "r4_ATB", ang(T4, A4, B4)); check(V, "r4", ang(B4, A4, T4), label="x measured")

finish([V])
