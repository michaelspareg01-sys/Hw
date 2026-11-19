"""Lesson 6K and the Chapter 6 review (Q16-Q35): recompute every printed answer from the question
data (typed in independently from the book) with math; equations solved by brute force; identities
and simplifications checked numerically with sympy."""
import math, re
import sympy as sp
from y11ch6_common import *

L, A = read("l6k.html"), read("a_6k.html")
V = spans(A, "data-v"); K = spans(L, "data-k")
r, d = math.radians, math.degrees
sin, cos, tan, asin, acos, sq = math.sin, math.cos, math.tan, math.asin, math.acos, math.sqrt
cot = lambda a: 1 / tan(r(a))
def val(s):
    if "^\\circ" in s: return parse_angles(s)
    return float(tex(s))
def num(k, x, dp):
    s = need(V, k, "answer")
    if s is None: return
    check(abs(val(s) - round(x, dp)) < 1e-9, f"{k}: printed {s}, computed {x:.5f}")
def ang(k, xs, mins=False, src=None):
    s = need(src or V, k, "answer")
    if s is None: return
    v = val(s)
    if len(v) != len(xs): fail(f"{k}: {v} vs {xs}"); return
    for p, x in zip(sorted(v), sorted(xs)):
        check(round(x * 60) == round(p * 60) if mins else round(x) == p, f"{k}: printed {p}, computed {x:.4f}")
def exact(k, x):
    s = need(V, k, "answer")
    if s is not None: check(abs(val(s) - x) < 1e-9, f"{k}: printed {s}, computed {x}")
sr = lambda a, Aa, B: a * sin(r(B)) / sin(r(Aa))
cr = lambda b, c, Aa: sq(b * b + c * c - 2 * b * c * cos(r(Aa)))
ca = lambda a, b, c: d(acos((b * b + c * c - a * a) / (2 * b * c)))
def bearing(p, q): return d(math.atan2(q[0] - p[0], q[1] - p[1])) % 360
def pol(dist, brg): return (dist * sin(r(brg)), dist * cos(r(brg)))

# lesson examples
num("kd1a", sr(9, 71, 48), 2); num("kd1b", cr(7, 10, 35), 2); ang("kd1c", [ca(9, 5, 7)], True)
num("ky1a", sr(12, 63, 52), 2); num("ky1b", cr(8, 11, 72), 2); ang("ky1c", [ca(11, 6, 8)], True)
Bw = d(asin(11 * sin(r(40)) / 8)); ang("wx1", [Bw, 180 - Bw], True, K); check(40 + 180 - Bw < 180, "worked example: obtuse B possible")
for k, (d1, b1, d2, b2) in (("kd2", (8, 90, 5, 40)), ("ky2", (9, 0, 6, 110))):
    Ap, Bp = pol(d1, b1), pol(d2, b2)
    num(k + "a", math.dist(Ap, Bp), 2); ang(k + "b", [bearing(Ap, Bp)], True); num(k + "c", .5 * d1 * d2 * sin(r(abs(b1 - b2))), 2)
Ap, Bp = pol(6, 0), pol(10, 120)
check(abs(math.dist(Ap, Bp) - 14) < 1e-9, "Example 31a: AB = 14")
bA = bearing(Ap, Bp); m31 = round(bA * 60)
check("141^\\circ47'" in L and f"{m31 // 60}^\\circ{m31 % 60}'" == "141^\\circ47'", f"Example 31b bearing {bA}")
check("38^\\circ13'" in L and round(d(acos(11 / 14)) * 60) == 38 * 60 + 13, "Example 31b angle A")

# Exercise 6K
num("k1a", sr(23, 43, 57), 1); num("k1b", 13.5 * tan(r(52)), 1); num("k1c", cr(11, 13, 62), 1)
num("k1d", 24 / sin(r(41.5)), 1); num("k1e", cr(7.4, 9.2, 98), 1); num("k1f", sr(18, 49, 77), 1)
ang("k2a", [ca(11, 10, 12)]); ang("k2b", [d(asin(8 * sin(r(67)) / 9))]); ang("k2c", [d(acos(13 / 17))])
ang("k2d", [d(asin(7.2 * sin(r(116)) / 10.8))]); ang("k2e", [d(math.atan(8.6 / 6.8))]); ang("k2f", [ca(21, 19, 5)])
num("k3a", sr(27, 90, 73), 0); num("k3b", sr(40, 55, 35), 0)                          # sine rule in the right triangle
ang("k3c", [d(asin(11 * sin(r(90)) / 14))]); ang("k3d", [ca(15, 8, 17)])                # sine rule / cosine rule
num("k4b", sr(40, 72, 55) * sin(r(53)), 0)
num("k5c", sr(20, 37, 31) * cos(r(68)), 0)
BD = cr(6.7, 8.3, 101); num("k6a", BD, 1); ang("k6b", [d(asin(9.2 * sin(r(73)) / BD))])
B7 = ca(5, 4, 7); ang("k7a", [B7], True); num("k7b", .5 * 4 * 7 * sin(r(B7)), 0)
XY = 25 / sin(r(72)); num("k8b", sr(XY, 42, 66), 0); check(abs(round(XY, 1) - 26.3) < 1e-9, "6K Q8a")
check(abs(25 / tan(r(72)) + 25 / tan(r(42)) - sr(XY, 42, 66)) < 1e-9, "6K Q8c")
s9 = d(acos((13 ** 2 + 14 ** 2 - 15 ** 2) / (2 * 13 * 14))); check(abs(.5 * 13 * 14 * sin(r(s9)) - 84) < 1e-9, "6K Q9")
Q10 = pol(53, 26); R10 = (Q10[0] + 78, Q10[1]); num("k10b", math.dist((0, 0), R10), 0)
check(abs(ca(math.dist((0, 0), R10), 53, 78) - 116) < 1e-9, "6K Q10a")
g = d(asin(60 * sin(r(7)) / 10)); ang("k11a", [g, 180 - g], True)
num("k11b", sr(10, 7, 180 - 7 - g), 1); num("k11b2", sr(10, 7, 180 - 7 - (180 - g)), 1)
num("k12d", 70 / sin(r(20)) * sin(r(15)) / sin(r(95)), 0)
num("k13b", cr(38 * tan(r(64)), 38 * tan(r(68)), 80), 0)
num("k14b", 300 * sin(r(43)) / sin(r(78)) * tan(r(32)), 0)
BC = cr(8.3, 15.2, 57); num("k15", 60 * (15.2 / 50 - (8.3 + BC) / 80), 1)
AC = cr(4, 7, 62); ACD = d(asin(4 * sin(r(62)) / AC)); ang("k16a", [ACD], True); ang("k16c", [180 - (180 - 31 - ACD)], True)
xb = 9 / (1 - cos(r(50))); num("k17", 2 * xb, 1)
for (a, b, c) in ((7, 8, 10), (5, 6, 9)):                                                # 6K Q18c and Q21 identities
    m = sq((2 * a * a + 2 * c * c - b * b) / 4); check(abs(a * a + c * c - 2 * m * m - b * b / 2) < 1e-9, "6K Q18c")
    s_ = (a + b + c) / 2; Cc = ca(c, a, b); check(abs(.5 * a * b * sin(r(Cc)) - sq(s_ * (s_ - a) * (s_ - b) * (s_ - c))) < 1e-9, "Heron")

# review
P = spans(L, "data-p"); S = spans(L, "data-s"); AN = spans(A, "data-a")
for k, q in S.items():
    check(num_equal(tex(q), tex(need(AN, k, "answer"))), f"{k}")
for k, q in P.items():
    sides = re.sub(r"^\\\(|\\\)$", "", q.strip()).split("=")
    check(num_equal(tex(sides[0]), tex(sides[1])), f"identity {k}")
SOL = spans(A, "data-sol")
for m in re.finditer(r'<span data-eq="([\w-]+)" data-dom="(-?\d+),(-?\d+)">(.*?)</span>', L, re.S):
    key, lo, hi, q = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
    lhs, rhs = re.sub(r"^\\\(|\\\)$", "", q.strip()).split("=")
    e = tex(lhs) - tex(rhs); var = [s for s in e.free_symbols if str(s) in ("x", "theta")]
    fn = sp.lambdify(var, e, "math")
    roots = roots_deg(lambda t: fn(math.radians(t)), lo, hi)
    pr = parse_angles(need(SOL, key, "solution") or "")
    if len(roots) != len(pr): fail(f"{key}: {roots} vs {pr}"); continue
    for x, p in zip(sorted(roots), sorted(pr)):
        check(abs(x - p) < 1e-6 or (p == int(p) and round(x) == p) or round(x * 60) == round(p * 60), f"{key}: {x} vs {p}")
check(len(re.findall(r'data-dom="0,360"', L)) == 15, "review: 15 equations, all on 0 to 360 degrees")
check(L.count("Solve each trigonometric equation for \\(0^\\circ\\le x\\le360^\\circ\\)") == 1, "review Q18 domain printed")
num("r20a", sr(7, 47, 63), 1); num("r20b", cr(8, 9, 75), 1); num("r20c", sr(15, 112, 28), 1); num("r20d", cr(9.3, 17.2, 18.5), 1)
num("r21a", .5 * 8 * 10 * sin(r(42)), 0); num("r21b", .5 * 9.8 * 12.3 * sin(r(112 + 36 / 60)), 0)
ang("r22a", [ca(7, 6, 8)], True); ang("r22b", [d(asin(10 * sin(r(77)) / 13))], True)
ang("r22c", [d(asin(16 * sin(r(131 + 19 / 60)) / 29))], True); ang("r22d", [ca(23.8, 13.9, 10.7)], True)
C23 = ca(10, 7, 8); num("r23", .5 * 7 * 8 * sin(r(C23)), 0)
exact("r24a", 30 / (.5 * 24 * sin(r(60)))); B24 = d(asin(18 / (.5 * 9 * 8))); ang("r24b", [B24, 180 - B24])
num("r25b", 600 * sin(r(7)) / sin(r(160)) * sin(r(13)), 0)
num("r26b", 50 * sin(r(15)) / sin(r(10)) * sin(r(25)), 1)
Q27 = pol(140, 50); R27 = (Q27[0] + 260 * sin(r(130)), Q27[1] + 260 * cos(r(130)))
num("r27b", math.dist((0, 0), R27), 0); ang("r27c", [bearing((0, 0), R27)]); check(abs(ca(math.dist((0, 0), R27), 140, 260) - 100) < 1e-9, "review Q27a")
num("r28b", cr(10 * tan(r(74)), 10 * tan(r(77)), 70), 0)
BC29 = 8 * tan(r(40)); num("r29a", BC29 * sin(r(35)) / sin(r(23)), 2)
num("r29b", cr(6, 7, 85) * sin(r(37)), 2)
APB = ca(7, 4, 6); num("r29c", 6 * sin(r(APB)) / sin(r(180 - APB - 65)), 2)
AB30 = 12 * tan(r(62)) * tan(r(64)); num("r30c", AB30 - 12, 0)
AP30 = 12 / cos(r(62)); PQ30 = AP30 * sin(r(64 - 28)) / sin(r(90 - 64))   # part d: sine rule in APQ, angle PAQ = 36, angle AQP = 26
check(round(PQ30) == 34 and abs(PQ30 - (AB30 - 12)) < 1e-9, f"review Q30d {PQ30}")
ST1 = 86 * sin(r(60.75)) / sin(r(65.75)); num("r31b", ST1 * sin(r(53.5)), 0)
h2 = 200 ** 2 / (cot(42) ** 2 + cot(35) ** 2 - 2 * cot(35) * cot(42) * cos(r(74))); num("r34c", sq(h2), 0)
check((270 - 196) == 74, "review Q34a: P is on bearing 270 from B, Q on 196")
h, x = 1.0, 4 / (sq(11) - sq(3)); check(abs(2 * h * h - (x * x - sq(3) * h * x)) < 1e-9, "review Q35c")
check(abs((sq(3) * h) ** 2 - (h * h + x * x - 2 * h * x * cos(r(30)))) < 1e-9, "review Q35b with BD = sqrt3 h, CD = h")
check(abs(cos(r(36)) * cos(r(72)) - .25) < 1e-12, "review Q33c")
finish("y11ch6_6k")
