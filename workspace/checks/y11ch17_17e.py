"""Check of Lesson 17E (Y11 Ch 17 pack): The double-angle formulae.

Reads the PRINTED answers (data-k spans) in a_17e.html and questions in l17e.html. Each simplified
double-angle expression is compared NUMERICALLY with the original expression (40 random points,
degrees converted to radians); exact values are compared with sympy's evaluation of the original
expression; the parametric eliminations are checked by substituting the parameter back; the
identities set in the exercise are spot-checked numerically. The past-paper block is checked (marks,
time, labels, hints, MC keys, every MC option tested). Exit 1 on failure.
Run: python3 workspace/checks/y11ch17_17e.py
"""
import sympy as sp
from y11ch17_common import (read, get, maths, tex, check, finish, x, A as Asym, al, th,
                            eq_value, pp_block, mc_key, num_equal)

L = read("l17e.html")
A = read("a_17e.html")
pi, s, c, t = sp.pi, sp.sin, sp.cos, sp.tan
d = lambda v: v * pi / 180
R = sp.Rational
asin, acos, atan, sqrt = sp.asin, sp.acos, sp.atan, sp.sqrt

for q in [r"\tan30^\circ", r"\tan135^\circ", r"\tan22\tfrac12^\circ", r"\cos\Big(2\sin^{-1}\dfrac23\Big)", r"\sin\big(2\tan^{-1}2\big)",
          r"\cos\Big(2\tan^{-1}\dfrac12\Big)", r"\sin\Big(2\cos^{-1}\Big(-\dfrac13\Big)\Big)", r"\sin\Big(2\cos^{-1}\dfrac45\Big)"]:
    check(q in L, f"question {q} printed")

def val(key, expected):
    sv = get(A, key)
    if sv is None:
        return
    got = tex(maths(sv))
    check(num_equal(got, expected), f"{key}: printed {maths(sv)} vs {expected}")

def last(key, expected):
    """Value after the last '=' of a printed chain."""
    eq_value(A, key, expected, key)

last("d1b", 1 / c(2 * x)); last("y1b", 1 / s(2 * x))
check(num_equal(2 * s(x) * c(x) * (c(x) ** 2 + s(x) ** 2), s(2 * x)), "C1 demo a identity")
check(num_equal(2 * s(x) * c(x) * (c(x) ** 2 - s(x) ** 2), s(4 * x) / 2), "C1 your turn a identity")
last("d2", t(d(15))); last("y2", t(d(R(135, 2))))
val("d3a", c(2 * asin(R(2, 3)))); val("d3b", s(2 * atan(2)))
val("y3a", c(2 * atan(R(1, 2)))); val("y3b", s(2 * acos(R(-1, 3))))
ex1 = {"1a": 2 * s(x) * c(x), "1b": c(th) ** 2 - s(th) ** 2, "1c": 2 * t(al) / (1 - t(al) ** 2), "1d": 2 * s(d(20)) * c(d(20)),
       "1e": 2 * c(d(50)) ** 2 - 1, "1f": 2 * t(d(70)) / (1 - t(d(70)) ** 2), "1g": 2 * s(3 * th) * c(3 * th),
       "1h": 1 - 2 * s(2 * Asym) ** 2, "1i": 2 * t(4 * x) / (1 - t(4 * x) ** 2)}
for k, e in ex1.items():
    val(k, e)
val("3a", c(2 * acos(R(4, 5)))); val("3b", c(2 * asin(R(2, 3)))); val("3c", s(2 * asin(R(5, 13)))); val("3d", t(2 * atan(R(1, 2))))
val("4", s(2 * (pi - asin(R(3, 4)))))
val("8a", c(2 * acos(R(1, 3)))); val("8b", s(2 * acos(R(6, 7)))); val("8c", t(2 * atan(-2)))
val("9b", t(pi / 8)); val("16a", c(pi / 4))
# 10: eliminate theta
y10a = tex(maths(get(A, "10a")).split("=")[-1]); y10b = tex(maths(get(A, "10b")).split("=")[-1])
check(num_equal(y10a.subs(x, 2 + c(th)), c(2 * th)), "10a y(x(theta)) = cos 2theta")
check(num_equal(y10b.subs(x, t(th) + 1), t(2 * th)), "10b y(x(theta)) = tan 2theta")
# exercise identities (spot checks)
for lhs, rhs in [(c(x) ** 4 - s(x) ** 4, c(2 * x)), (c(2 * x) + c(x), (c(x) + 1) * (2 * c(x) - 1)), (s(2 * Asym) / (1 - c(2 * Asym)), 1 / t(Asym)),
                 (c(th) - s(th) * s(2 * th), c(th) * c(2 * th)), (t(pi / 4 + al) - t(pi / 4 - al), 2 * t(2 * al)),
                 ((s(2 * th) + s(th)) / (c(2 * th) + c(th) + 1), t(th)), (c(3 * th), 4 * c(th) ** 3 - 3 * c(th)),
                 (1 / t(2 * al) + t(al), 1 / s(2 * al)), (s(3 * Asym) / s(Asym) + c(3 * Asym) / c(Asym), 4 * c(2 * Asym)),
                 (t(2 * x) / t(x), 1 + 1 / c(2 * x)), ((1 + s(2 * al)) / (1 + c(2 * al)), (1 + t(al)) ** 2 / 2),
                 (1 / s(4 * Asym) + 1 / t(4 * Asym), (1 / t(Asym) - t(Asym)) / 2)]:
    check(num_equal(lhs, rhs), f"exercise identity {lhs} = {rhs}")
check(abs(float(8 * c(2 * pi / 9) ** 3 - 6 * c(2 * pi / 9) + 1)) < 1e-12, "Q12b root")
check(abs(float(2 * atan(2) - (pi - acos(R(3, 5))))) < 1e-12, "Q15")
check(abs(float(c(pi / 8) - sqrt(2 + sqrt(2)) / 2)) < 1e-12 and abs(float(c(pi / 16) - sqrt(2 + sqrt(2 + sqrt(2))) / 2)) < 1e-12, "Q16b")
check(abs(float(t(d(R(165, 2))) - (sqrt(6) + sqrt(3) + sqrt(2) + 2))) < 1e-12, "Q17c")
h = 10 * sqrt(3)
check(sp.simplify(2 * (h / 30) / (1 - (h / 30) ** 2) - h / 10) == 0, "Q11d h = 10 sqrt3")
# past papers
pp_block(L, A)
o1 = {"A": s(x) ** 2 - c(x) ** 2, "B": 2 * (s(x) ** 2 + 1), "C": 2 * s(x) ** 2, "D": 2 * (1 + c(x) ** 2)}
check([k for k, e in o1.items() if num_equal(e, 1 - c(2 * x))] == ["C"], "PP1 only C"); val("pp1", 1 - c(2 * x)); mc_key(A, "PP 1", "C")
v2 = s(2 * (pi - asin(sqrt(3) / 2)))
o2 = {"A": -sqrt(3) / 4, "B": -sqrt(3) / 2, "C": sqrt(3) / 4, "D": sqrt(3) / 2}
check([k for k, e in o2.items() if num_equal(e, v2)] == ["B"], "PP2 only B"); val("pp2", v2); mc_key(A, "PP 2", "B")
v3 = t(2 * (pi - asin(R(28, 100))))
o3 = {"A": R(527, 336), "B": -R(527, 336), "C": R(336, 527), "D": -R(336, 527)}
check([k for k, e in o3.items() if num_equal(e, v3)] == ["D"], "PP3 only D"); val("pp3", v3); mc_key(A, "PP 3", "D")
val("pp4", s(2 * acos(R(-1, 3))))
val("pp5", t(2 * acos(R(12, 13)))); val("pp6", t(2 * asin(R(2, 3))))
val("pp7", c(2 * acos(R(2, 5))))  # cos 4A with cos 2A = 2/5
check(num_equal(s(Asym) * s(5 * Asym) + c(Asym) * c(5 * Asym), c(4 * Asym)), "PP7 reduces to cos 4A")
check(num_equal(s(2 * x) / (1 + c(2 * x)), t(x)), "PP8 (i)"); val("pp8", 1 / t(d(15)))
sv9 = get(A, "pp9")
if sv9:
    got = tex(maths(sv9).split("=")[-1])
    sols = [r for r in sp.solve(4 * x ** 2 + 2 * x - 1, x) if r > 0]
    check(num_equal(got, sols[0]) and num_equal(got, s(pi / 10)), "PP9 sin x = (sqrt5 - 1)/4 = sin(pi/10)")
check(abs(float(c(3 * pi / 10) - s(pi / 5))) < 1e-12, "PP9 pi/10 solves cos3x = sin2x")
check(abs(float(s(pi / 5) * c(pi / 10) - sqrt(5) / 4)) < 1e-12, "PP9 (iii)")
finish("y11ch17_17e")
