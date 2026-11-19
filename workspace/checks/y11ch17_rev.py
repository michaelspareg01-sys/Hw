"""Check of the Y11 Ch 17 revision warm-up (revision.html questions, a_rev.html answers).

Reads the printed answers (data-k spans in a_rev.html) and the printed questions in revision.html,
and recomputes each with sympy: the inverse function by solving x = f(y), exact values by sympy's
trigonometric evaluation, equation solutions by sympy.solveset on the stated interval, and the
second-quadrant values from cos^2 + sin^2 = 1 with the quadrant signs.
Exit status 1 on any failure. Run: python3 workspace/checks/y11ch17_rev.py
"""
import sympy as sp
from y11ch17_common import (read, get, maths, tex, value, eq_value, number_set, check, finish, x, rhs)

Q = read("revision.html")
A = read("a_rev.html")
pi = sp.pi

# Q1: the printed f(x) = (x+1)/3 in the question
check(r"Let \(f(x)=\dfrac{x+1}{3}\)" in Q, "Q1 question text f(x) = (x+1)/3 printed once")
yy = sp.Symbol("yy")
finv = sp.solve(sp.Eq(x, (yy + 1) / 3), yy)[0]
eq_value(A, "w1a", finv, "Q1a f^-1(x)")
s = get(A, "w1a")
if s:
    g = tex(rhs(maths(s)))
    check(sp.simplify(((g + 1) / 3) - x) == 0 and sp.simplify(g.subs(x, (x + 1) / 3) - x) == 0, "Q1b both composites are x")

# Q2 exact values (question angles typed from revision.html, checked to be printed there)
for key, txt, val in [("w2a", r"\sin\dfrac{2\pi}{3}", sp.sin(2 * pi / 3)), ("w2b", r"\cos\dfrac{5\pi}{4}", sp.cos(5 * pi / 4)),
                      ("w2c", r"\tan\Big(-\dfrac\pi6\Big)", sp.tan(-pi / 6)), ("w2d", r"\sin\dfrac{11\pi}{6}", sp.sin(11 * pi / 6))]:
    check(txt in Q, f"Q2 {key} question {txt} printed")
    eq_value(A, key, val, f"Q2 {key}")
# Q3 solutions in [-pi, pi]
I = sp.Interval(-pi, pi)
for key, eq in [("w3a", sp.sin(x) + sp.Rational(1, 2)), ("w3b", sp.cos(x) - 1 / sp.sqrt(2)), ("w3c", sp.tan(x) + sp.sqrt(3))]:
    sols = sp.solveset(eq, x, I)
    number_set(A, key, list(sols), f"Q3 {key}")
check(r"\cos\theta=-\dfrac{5}{13}" in Q, "Q4 question printed")
c = sp.Rational(-5, 13)
sn = sp.sqrt(1 - c ** 2)          # second quadrant: sine positive
eq_value(A, "w4s", sn, "Q4 sin")
eq_value(A, "w4t", sn / c, "Q4 tan")
s = get(A, "w5b")
if s:
    check(maths(s) == r"-\dfrac\pi2\le x\le\dfrac\pi2", "Q5b interval [-pi/2, pi/2]")
finish("y11ch17_rev")
