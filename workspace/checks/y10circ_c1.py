r"""Check of Lesson C1 (Year 10 Circle Geometry: chords, radii and angles), tied to the printed HTML.

Reads build/y10circ/lc1.html, a_c1.html and the lesson figures svg/*.svg.
  - Every printed number in the answers (and the worked-example results in the lesson) is a
    <span data-v="KEY">; each key must be found exactly once and every key must be checked.
    The MP Q4 and Q5(b) results, printed inside aligned displays, are read from their blocks by pattern.
  - The given data are read from the page: from the figure labels (svg text) or from the question text.
  - Every angle and length is recomputed from the given data with coordinates: points are placed on
    circles, unknown positions are found by bisection on a measured angle or length (never by the
    theorem being taught), and the answer is then MEASURED (angles by the dot product, lengths by
    distance, areas by the shoelace formula on a 20000-point polygon).
Exit status 1 on any failure.  Run: python3 workspace/checks/y10circ_c1.py
"""
import os
import re
import sys
from math import cos, sin, radians, degrees, pi, hypot, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y10circ_common import Values, check, svg_has, svg_labels, ok, finish, read, ang, dist  # noqa: E402

V = Values(["a_c1.html", "lc1.html"])
LES = read("lc1.html")


def onc(c, r, deg):
    return (c[0] + r * cos(radians(deg)), c[1] + r * sin(radians(deg)))


def bisect(f, lo, hi, n=200):
    """Root of f on [lo, hi] (f changes sign)."""
    flo = f(lo)
    for _ in range(n):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def line_dist(p, a, b):
    return abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / dist(a, b)


def shoelace(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


def deg_label(fig):
    return [float(l[:-1]) for l in svg_labels(fig) if re.fullmatch(r"\d+(\.\d+)?°", l)]


def len_label(fig, unit):
    return [float(l[:-len(unit)]) for l in svg_labels(fig) if re.fullmatch(r"\d+(\.\d+)? " + unit, l)]


def text_num(pattern, src=LES, k=1):
    m = re.findall(pattern, src)
    ok(len(m) >= k, f"given read from text: {pattern}", str(m[:3]))
    return float(m[k - 1]) if m else float("nan")


O = (0.0, 0.0)

# ---------------- C1: diameter, circumference, area (perimeter and area of a 20000-gon) ----------------
for key, r in (("d1", text_num(r"A circle has radius ([\d.]+) cm", k=1)), ("y1", text_num(r"A circle has radius ([\d.]+) cm", k=2))):
    poly = [onc(O, r, 360 * i / 20000) for i in range(20000)]
    per = sum(dist(poly[i], poly[(i + 1) % 20000]) for i in range(20000))
    check(V, f"{key}_d", dist(onc(O, r, 0), onc(O, r, 180)), label="diameter measured")
    check(V, f"{key}_C", per / pi, tol=1e-6, label="circumference / pi (polygon)")
    check(V, f"{key}_A", shoelace(poly) / pi, tol=1e-6, label="area / pi (polygon)")
ok(abs(text_num(r"A circle has radius ([\d.]+) cm", k=1) - 6) < 1e-9 and abs(text_num(r"A circle has radius ([\d.]+) cm", k=2) - 4.5) < 1e-9, "C1 radii are 6 and 4.5")


# ---------------- C2: perpendicular from the centre ----------------
def half_chord(half, h=2.7):
    """Radius perpendicular to a chord: the chord meets the circle where |x| = half; measure the other half."""
    R = sqrt(half * half + h * h)
    xs = [x for x in (sqrt(R * R - h * h), -sqrt(R * R - h * h))]
    P, Q, M = (xs[1], -h), (xs[0], -h), (0.0, -h)
    return dist(M, Q), dist(M, P)


for key, fig, unit in (("d2a", "d2a", "cm"), ("y2a", "y2a", "m"), ("h3", "mpq5a", "m")):
    g = len_label(fig, unit)
    ok(len(g) == 1, f"{fig} given length read", str(g))
    other, given = half_chord(g[0])
    ok(abs(given - g[0]) < 1e-9, f"{fig} construction reproduces the given half")
    check(V, key, other, label="other half measured")


def q5b(given):
    """Vertical chord x = a, radius OE along the x-axis through its midpoint M; S on the circle with angle TMS = given."""
    R, a = 5.0, 2.2
    hh = sqrt(R * R - a * a)
    T, M, E = (a, hh), (a, 0.0), (R, 0.0)
    ok(abs(dist(T, M) - dist(M, (a, -hh))) < 1e-12, f"q5b({given}) M bisects the chord")

    def S_of(t):
        return onc(O, R, t)
    t = bisect(lambda t: ang(M, T, S_of(t)) - given, 0.0, 89.0)
    S = S_of(t)
    ok(abs(ang(M, T, S) - given) < 1e-9, f"q5b({given}) S placed with angle {given}")
    return ang(M, S, E)


for key, fig in (("d2b", "d2b"), ("y2b", "y2b")):
    g = deg_label(fig)
    ok(len(g) == 1, f"{fig} given angle read", str(g))
    check(V, key, q5b(g[0]), label="angle SME measured")
# MP Q5(b) worked example (lesson): read the aligned result
m = re.search(r"Q5\(b\): keep for homework.*?q&amp;=90\^\\circ-30\^\\circ\\\\&amp;=(\d+)\^\\circ", LES, re.S)
ok(m is not None, "lesson MP Q5(b) result found")
if m:
    g = deg_label("mpq5b")
    ok(g == [30.0], "mpq5b given 30 deg", str(g))
    ok(abs(float(m.group(1)) - q5b(30)) < 1e-6, "lesson MP Q5(b) q", f"printed {m.group(1)}, measured {q5b(30):.6f}")
# MP Q4 worked example: angle ACO with C the midpoint of chord AB
m = re.search(r"Q4: keep for homework.*?\\angle ACO&amp;=\\frac\{180\^\\circ\}\{2\}\\\\&amp;=(\d+)\^\\circ", LES, re.S)
ok(m is not None, "lesson MP Q4 result found")
if m:
    A, B = onc(O, 5, 205), onc(O, 5, 335)
    Cm = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    ok(abs(float(m.group(1)) - ang(Cm, A, O)) < 1e-9, "lesson MP Q4 angle ACO", f"measured {ang(Cm, A, O):.9f}")


def chord_dist(L, R):
    """A chord of length L in a circle of radius R, placed by bisection on the central angle; distance from O."""
    A = onc(O, R, 37)
    phi = bisect(lambda p: dist(A, onc(O, R, 37 + p)) - L, 1e-9, 180)
    B = onc(O, R, 37 + phi)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    return dist(A, M), line_dist(O, A, B)


for key, k in (("d2c", 1), ("y2c", 2)):
    L = text_num(r"A chord of length (\d+) cm is drawn in a circle of radius \d+ cm", k=k)
    R = text_num(r"A chord of length \d+ cm is drawn in a circle of radius (\d+) cm", k=k)
    am, d = chord_dist(L, R)
    check(V, f"{key}_AM", am, label="half chord measured")
    check(V, key, d, label="distance from centre measured")


# ---------------- C3: equal chords and equal angles ----------------
def radius_for(L, angle):
    """Radius of the circle in which a chord of length L subtends the given angle at the centre (bisection)."""
    return bisect(lambda R: dist(onc(O, R, 0), onc(O, R, angle)) - L, L / 2 + 1e-9, 1000 * L)


def other_angle(L, angle):
    """Equal chord placed elsewhere in the same circle (by bisection on its length); its angle at the centre."""
    R = radius_for(L, angle)
    P = onc(O, R, 200)
    p = bisect(lambda t: dist(P, onc(O, R, 200 + t)) - L, 1e-9, 180)
    Q = onc(O, R, 200 + p)
    return ang(O, P, Q), ang(P, O, Q)


def other_chord(L, angle):
    R = radius_for(L, angle)
    P, Q = onc(O, R, 210), onc(O, R, 210 + angle)
    return dist(P, Q)


for key, fig, unit in (("d3a", "d3a", "m"), ("y3a", "y3a", "m"), ("w_mpq3b", "mpq3b", "m")):
    a = deg_label(fig)
    L = len_label(fig, unit)
    ok(len(a) == 1 and len(L) == 2 and L[0] == L[1], f"{fig} givens read (one angle, two equal chords)", f"{a} {L}")
    centre, base = other_angle(L[0], a[0])
    check(V, key, centre, label="angle at centre of the equal chord, measured")
    if key != "w_mpq3b":
        check(V, key[0] + "3c", base, label="base angle measured")
for key, fig, unit in (("d3b", "d3b", "cm"), ("y3b", "y3b", "cm"), ("h2", "mpq3a", "cm")):
    a = deg_label(fig)
    L = len_label(fig, unit)
    ok(len(a) == 2 and a[0] == a[1] and len(L) == 1, f"{fig} givens read (two equal angles, one chord)", f"{a} {L}")
    check(V, key, other_chord(L[0], a[0]), label="chord measured")

# ---------------- C4: angles in a semicircle ----------------
A_, B_ = (-1.0, 0.0), (1.0, 0.0)


def place_P(at, given):
    """P on the upper semicircle with angle PAB (at='A') or PBA (at='B') equal to given, by bisection."""
    if at == "A":
        t = bisect(lambda t: ang(A_, onc(O, 1, t), B_) - given, 1e-6, 180 - 1e-6)
    else:
        t = bisect(lambda t: ang(B_, onc(O, 1, t), A_) - given, 1e-6, 180 - 1e-6)
    return onc(O, 1, t)


g = deg_label("d4a")
ok(g == [28.0], "d4a given angle read", str(g))
ok(abs(text_num(r"with \\\(\\angle A=(\d+)\^\\circ\\\)") - g[0]) < 1e-9, "d4a text and figure agree")
P = place_P("A", g[0])
check(V, "d4_APO", ang(P, A_, O)); check(V, "d4_APB", ang(P, A_, B_)); check(V, "d4_BPO", ang(P, B_, O)); check(V, "d4_B", ang(B_, P, A_))
g = deg_label("y4a")
ok(g == [57.0], "y4a given angle read", str(g))
P = place_P("B", g[0])
check(V, "y4_BPO", ang(P, B_, O)); check(V, "y4_APB", ang(P, A_, B_)); check(V, "y4_APO", ang(P, A_, O)); check(V, "y4_A", ang(A_, P, B_))
for key, k in (("d4b", 1), ("y4b", 2)):
    ac = text_num(r"with \\\(AC=(\d+)\\\) cm and \\\(BC=\d+\\\) cm", k=k)
    bc = text_num(r"with \\\(AC=\d+\\\) cm and \\\(BC=(\d+)\\\) cm", k=k)
    C, A, B = (0.0, 0.0), (ac, 0.0), (0.0, bc)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    check(V, f"{key}_AB", dist(A, B)); check(V, key, dist(C, M), label="CM measured")

# homework Q4 (MP arcs Q7) and Q5 (Q8a): angles subtended by a diameter, P anywhere
for key in ("h4a", "h4c", "h4b_z", "h5"):
    angs = [ang(onc(O, 1, t), A_, B_) for t in (17, 63, 101, 154, 211, 333)]
    ok(max(abs(a - angs[0]) for a in angs) < 1e-9, f"{key} angle independent of P")
    check(V, key, angs[0])
check(V, "h4b_y", ang(O, A_, B_), label="angle AOB along a diameter")
svg_has("mpa7a", "180°", "x"); svg_has("mpa7b", "y", "z"); svg_has("mpa7c", "x"); svg_has("mpa8a", "a")

# homework Q6 (MP Q3d): concentric circles
a = deg_label("mpq3d")
big = len_label("mpq3d", "m")
ok(a == [65.0] and sorted(big) == [3.0, 6.0, 6.0], "mpq3d givens read", f"{a} {big}")
Rb = radius_for(6, 65)
P = onc(O, Rb, 300)
t_ = bisect(lambda t: dist(P, onc(O, Rb, 300 + t)) - 6, 1e-9, 180)
check(V, "h6_t", t_, label="angle of the second 6 m chord")
rs = radius_for(3, 65)
check(V, "h6_w", dist(onc(O, rs, 300), onc(O, rs, 300 + t_)), label="small chord on the same radii")

# homework Q7 (MP Q6a): two circles; foot of O on the line at B, foot of P at C
ab = text_num(r"\\\(AB=(\d+)\\text\{ mm\}\\\)")


def line_circle(cen, R):
    """x-coordinates where the circle meets the x-axis."""
    h = cen[1]
    w = sqrt(R * R - h * h)
    return sorted((cen[0] - w, cen[0] + w))


Oc = (0.0, 3.3)                                   # O at height 3.3 above B = (0, 0); circle O through A = (-AB, 0)
RO = dist(Oc, (-ab, 0.0))
xA, xC = line_circle(Oc, RO)                       # A and C: where circle O meets the line
Bx = 0.0
Cx = xC
Pc = (Cx, -3.3)                                   # P below the line, its foot at C; circle P through B (equal radius)
RP = dist(Pc, (Bx, 0.0))
xB, xD = line_circle(Pc, RP)
ok(abs(xB - Bx) < 1e-9, "Q6a: circle P passes through B")
check(V, "h7_BC", Cx - Bx, label="BC measured")
check(V, "h7_CD", xD - Cx, label="CD measured")
check(V, "h7", xD - xA, label="AD measured")

# homework Q8 (MP Q6b)
g52 = text_num(r"\\\(\\angle IHD=(\d+)\^\\circ\\\)")
G, R6 = (0.0, 0.0), 10.0
yH = -8.2
H = (0.0, yH)
D = (sqrt(R6 * R6 - yH * yH), yH)
d = (cos(radians(g52)), sin(radians(g52)))
# chord BF through H in direction d (angle IHD = g52 with D on the +x side)
px, py = H
b = px * d[0] + py * d[1]
disc = sqrt(b * b - (px * px + py * py - R6 * R6))
F = (H[0] + (-b + disc) * d[0], H[1] + (-b + disc) * d[1])
Bq = (H[0] + (-b - disc) * d[0], H[1] + (-b - disc) * d[1])
I = ((F[0] + Bq[0]) / 2, (F[1] + Bq[1]) / 2)        # BI = IF
ok(abs(ang(H, I, D) - g52) < 1e-9, "Q6b construction has angle IHD as given")
check(V, "h8_GHD", ang(H, G, D)); check(V, "h8_GHI", ang(H, G, I)); check(V, "h8_GIH", ang(I, G, H)); check(V, "h8", ang(G, I, H))

# homework Q11 (MP Q6c)
AB5 = text_num(r"\\\(AB=(\d+)\\text\{ m\}\\\)")
BC4 = text_num(r"\\\(BC=(\d+)\\text\{ m\}\\\)")
A = (0.0, 0.0)
B = (AB5, 0.0)
mid = (AB5 / 2, 0.0)
# C on the circle with diameter AB with BC = 4 (bisection on the position)
t = bisect(lambda t: dist(B, onc(mid, AB5 / 2, t)) - BC4, 1e-9, 180 - 1e-9)
C = onc(mid, AB5 / 2, t)
check(V, "h11_ACB", ang(C, A, B), label="angle ACB measured")
check(V, "h11_AC", dist(A, C))
# larger circle: centre on line BC, through A and B; D the second point of line AC on it
u = ((C[0] - B[0]) / dist(B, C), (C[1] - B[1]) / dist(B, C))
s = bisect(lambda s: dist((B[0] + s * u[0], B[1] + s * u[1]), A) - s, 1e-9, 100)
O2 = (B[0] + s * u[0], B[1] + s * u[1])
v = ((C[0] - A[0]) / dist(A, C), (C[1] - A[1]) / dist(A, C))
k = bisect(lambda k: dist((A[0] + k * v[0], A[1] + k * v[1]), O2) - s, dist(A, C) + 1e-6, 100)
Dp = (A[0] + k * v[0], A[1] + k * v[1])
check(V, "h11", dist(C, Dp), label="CD measured")

# ---------------- past papers ----------------
# PP2: regular pentagon in a circle, AF a diameter
Vx = [onc(O, 1, 90 + 72 * i) for i in range(5)]           # A, E, D, C, B anticlockwise (A at the top)
Ap, Bp = Vx[0], Vx[4]
Fp = onc(O, 1, 270)
ok(max(dist(Vx[i], Vx[(i + 1) % 5]) for i in range(5)) - min(dist(Vx[i], Vx[(i + 1) % 5]) for i in range(5)) < 1e-12, "PP2 pentagon regular")
check(V, "pp2_AOB", ang(O, Ap, Bp)); check(V, "pp2_BOF", ang(O, Bp, Fp)); check(V, "pp2", ang(Bp, O, Fp))
# PP3: diameter AOD, radius 9, angle ADC = 35; segment area numerically
g = deg_label("pp3")
r9 = len_label("pp3", "cm")
ok(g == [35.0] and r9 == [9.0, 9.0], "PP3 givens read", f"{g} {r9}")
r = r9[0]
Ad, Dd = (-r, 0.0), (r, 0.0)
tc = bisect(lambda t: ang(Dd, Ad, onc(O, r, t)) - g[0], 90.0001, 179.999)
Cc = onc(O, r, tc)
check(V, "pp3_OCD", ang(Cc, O, Dd)); check(V, "pp3_AOC", ang(O, Ad, Cc))
arc = [onc(O, r, tc + (180 - tc) * i / 20000) for i in range(20001)]
sector = shoelace([O] + arc)
tri = shoelace([O, Ad, Cc])
check(V, "pp3_sector", sector, tol=2e-3, label="sector (printed to 3 dp)")
check(V, "pp3_tri", tri, tol=2e-3, label="triangle (printed to 3 dp)")
seg = shoelace(arc)
check(V, "pp3", float(f"{seg:.3g}"), label=f"segment {seg:.6f} to 3 s.f.")
svg_has("pp4", "I", "J", "K", "O")

finish([V])
