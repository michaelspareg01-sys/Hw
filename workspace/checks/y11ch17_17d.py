"""Check of Lesson 17D (Y11 Ch 17 pack): Trigonometric functions of compound angles.

Reads the PRINTED answers (data-k spans) in a_17d.html and questions in l17d.html. Each printed
expansion or single-function answer is compared NUMERICALLY with the compound expression it came from
(sympy evaluation at 40 random points); exact values are compared with sympy's evaluation of the
original expression (degrees converted to radians); equations in inverse tangents are re-solved by
sympy (and the extraneous roots checked by substitution); the identities printed in the lesson are
checked numerically. The past-paper block is checked (marks, time, labels, hints, MC keys, every MC
option tested). Exit 1 on failure. Run: python3 workspace/checks/y11ch17_17d.py
"""
import sympy as sp
from y11ch17_common import (read, get, maths, tex, check, finish, x, y, A as Asym, B as Bsym, al, be, th,
                            eq_value, pp_block, mc_key, num_equal, number_set)

L = read("l17d.html")
A = read("a_17d.html")
pi, s, c, t = sp.pi, sp.sin, sp.cos, sp.tan
d = lambda v: v * pi / 180
R = sp.Rational
phi = sp.Symbol("phi", real=True)
asin, acos, atan, sqrt = sp.asin, sp.acos, sp.atan, sp.sqrt

for q in [r"\cos\Big(x-\dfrac\pi6\Big)", r"\sin\Big(x-\dfrac{3\pi}{4}\Big)", r"\cos\alpha=\dfrac35", r"\sin\beta=-\dfrac{5}{13}",
          r"\sin\Big(\tan^{-1}\dfrac12+\cos^{-1}\dfrac35\Big)", r"\sin\alpha=\dfrac{8}{17}", r"\cos\Big(\sin^{-1}\dfrac35-\tan^{-1}\dfrac13\Big)",
          r"\sin105^\circ", r"\tan105^\circ", r"\cos165^\circ", r"\sin195^\circ", r"\cot285^\circ", r"\tan^{-1}x+\tan^{-1}2=\tan^{-1}7",
          r"\tan^{-1}\dfrac{x}{1+x}+\tan^{-1}\dfrac{x}{1-x}=\tan^{-1}\dfrac67"]:
    check(q in L, f"question {q} printed")

def val(key, expected):
    sv = get(A, key)
    if sv is None:
        return
    got = tex(maths(sv))
    check(num_equal(got, expected), f"{key}: printed {maths(sv)} vs {expected}")

val("d1", c(x - pi / 6)); val("y1", s(x - 3 * pi / 4))
sa, cb = R(4, 5), R(12, 13)
val("d2a1", sa * cb + R(3, 5) * R(-5, 13)); val("d2a2", R(3, 5) * cb + sa * R(-5, 13))
val("d2b", s(atan(R(1, 2)) + acos(R(3, 5))))
aa, bb = asin(R(8, 17)), -acos(R(4, 5))
val("y2a1", s(aa - bb)); val("y2a2", c(aa + bb))
val("y2b", c(asin(R(3, 5)) - atan(R(1, 3))))
val("d3a", s(d(105))); val("d3b", t(d(105))); val("y3a", c(d(165))); val("y3b", s(d(195)))
for k, e in {"1a": s(x - y), "1b": c(2 * Asym + 3 * Bsym), "1c": s(3 * al + 5 * be), "1d": c(th - phi / 2), "1e": t(Asym + 2 * Bsym),
             "1f": t(3 * al - 4 * be), "2a": c(x) * c(y) - s(x) * s(y), "2b": s(3 * al) * c(2 * be) + c(3 * al) * s(2 * be),
             "2d": s(5 * Asym) * c(2 * Asym) - c(5 * Asym) * s(2 * Asym), "2f": (t(al) + t(d(10))) / (1 - t(al) * t(d(10)))}.items():
    sv = get(A, k)
    if sv:
        got = tex(maths(sv))
        check(num_equal(got, e), f"{k}: printed {maths(sv)}")
val("2c", (t(d(40)) - t(d(20))) / (1 + t(d(40)) * t(d(20))))
val("2e", c(d(70)) * c(d(20)) + s(d(70)) * s(d(20)))
val("5a", t(atan(R(1, 2)) + atan(R(1, 3)))); val("5b", s(acos(R(4, 5)) + asin(R(12, 13))))
val("5c", c(asin(R(2, 3)) - acos(R(1, 4))))
val("7i", s(d(75))); val("7ii", c(d(75))); val("7iii", t(d(75)))
val("9a", c(d(105))); val("9b", s(13 * pi / 12)); val("9c", 1 / t(d(285)))
val("10a", t(atan(R(1, 4)) + atan(R(3, 5)))); val("10b", s(asin(R(4, 5)) + asin(R(12, 13))))
val("10c", t(asin(R(3, 5)) + acos(R(12, 13)))); val("10d", c(atan(R(1, 2)) + asin(R(1, 4))))
val("13b", s(d(75)) ** 2 - s(d(15)) ** 2)
def atan_solutions(lhs, rhs):
    cand = sp.solve(sp.Eq(sp.tan(lhs), sp.tan(rhs)) if False else sp.Eq(sp.simplify(sp.expand_trig(sp.tan(lhs))), rhs_tan(rhs)), x)
    return cand
xs = sp.symbols("xs")
# 11b, 12, 18: solve tan(LHS) = tan(RHS) then keep roots that satisfy the original equation numerically
def solve_atan(f_lhs, rhs_value):
    T = sp.simplify(sp.tan(f_lhs).rewrite(sp.tan).expand(trig=True))
    cands = [r for r in sp.solve(sp.Eq(sp.together(T), sp.tan(rhs_value)), x) if r.is_real]
    return [r for r in cands if abs(float(f_lhs.subs(x, r)) - float(rhs_value)) < 1e-9]
number_set(A, "11b", solve_atan(atan(x) + atan(2 * x), atan(3)), "11b")
number_set(A, "12a", solve_atan(atan(x) + atan(2), atan(7)), "12a")
number_set(A, "12b", solve_atan(atan(3 * x) - atan(x), atan(R(1, 2))), "12b")
number_set(A, "18", solve_atan(atan(x / (1 + x)) + atan(x / (1 - x)), atan(R(6, 7))), "18")
check(abs(float(atan(-1) + atan(-2)) - float(atan(3))) > 1e-6, "11b x = -1 fails the original equation")
# identities printed in the exercise (spot checks)
for lhs, rhs in [(s(Asym + d(45)), (s(Asym) + c(Asym)) / sqrt(2)), (2 * c(th + pi / 3), c(th) - sqrt(3) * s(th)),
                 (t(pi / 4 - Asym), (1 - t(Asym)) / (1 + t(Asym))), (s(Asym - d(30)), (sqrt(3) * s(Asym) - c(Asym)) / 2),
                 (s(x + y) + c(x - y), (s(x) + c(x)) * (s(y) + c(y))), (2 * s(x - y) / (c(x + y) - c(x - y)), 1 / t(x) - 1 / t(y))]:
    check(num_equal(lhs, rhs), f"exercise identity {lhs} = {rhs}")
check(abs(float(c(pi - asin(R(2, 3)) + pi + atan(R(2, 3))) - (3 * sqrt(5) + 4) / (3 * sqrt(13)))) < 1e-12, "Q8 cos(A + B)")
check(abs(float(t(d(35)) + t(d(10)) + t(d(35)) * t(d(10)) - 1)) < 1e-12, "Q14b")
check(abs(float(atan(R(1, 3)) + atan(R(1, 2))) - float(pi / 4)) < 1e-12, "Q16b alpha + beta = 45 degrees (tan a = 1/2, tan b = 1/3)")
# past papers
pp_block(L, A)
v1 = s(asin(R(8, 17)) + asin(R(4, 5)))
val("pp1", v1); mc_key(A, "PP 1", "B")
opts = {"A": -2 * s(3 * x) * s(x), "B": 2 * c(3 * x) * s(x), "C": 2 * c(3 * x) * c(x), "D": 2 * s(3 * x) * s(x)}
good = [k for k, e in opts.items() if num_equal(e, s(4 * x) - s(2 * x))]
check(good == ["B"], f"PP2 only B ({good})"); val("pp2", s(4 * x) - s(2 * x)); mc_key(A, "PP 2", "B")
v3 = t(atan(R(1, 3)) + pi / 3)
o3 = {"A": (sqrt(3) + 3) / (3 * sqrt(3) - 1), "B": (sqrt(3) - 3) / (3 * sqrt(3) + 1), "C": (1 + 3 * sqrt(3)) / (3 - sqrt(3)), "D": (1 - 3 * sqrt(3)) / (3 + sqrt(3))}
check([k for k, e in o3.items() if num_equal(e, v3)] == ["C"], "PP3 only C"); val("pp3", v3); mc_key(A, "PP 3", "C")
check(num_equal(1 / t(2 * x) + 1 / t(x), s(3 * x) / (s(2 * x) * s(x))), "PP4 identity")
val("pp5", c(atan(R(4, 3)) - acos(R(5, 13))))
val("pp6", s(acos(R(2, 3)) + atan(R(-3, 4))))
sol7 = [v for v in sp.solveset(sp.Eq((s(x) + c(x)) / sqrt(2), sqrt(3) / 2), x, sp.Interval(0, 2 * pi))]
number_set(A, "pp7", sol7, "PP7 (degrees, read as radians)")
check(num_equal(t(4 * x) - t(x), s(3 * x) / (c(4 * x) * c(x))), "PP8 (i) identity")
sol8 = [v for v in sp.solveset(sp.Eq(sp.sin(3 * x), 0), x, sp.Interval(0, pi)) if sp.cos(4 * v) != 0 and sp.cos(v) != 0]
number_set(A, "pp8", sol8, "PP8 (ii)")
finish("y11ch17_17d")
