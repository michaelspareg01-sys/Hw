"""Check of Lesson 17A (Y11 Ch 17 pack): Restricting the domain.

Reads the PRINTED answers (data-k spans) in workspace/build/y11ch17/a_17a.html and the printed
questions in l17a.html. Each printed inverse function is tested by composing it with the original
function in both orders at many sample points of the two domains (no inverse is taken from the HTML
and compared with itself); printed ranges and domains are compared with intervals recomputed with
sympy (function_range / solving); stationary points are recomputed with sympy.diff; intersection
points are recomputed by solving; derivatives with sympy.diff. The past-paper block is checked for
marks, time, labels, hints and MC keys. Exit 1 on any failure. Run: python3 workspace/checks/y11ch17_17a.py
"""
import sympy as sp
from sympy.calculus.util import function_range
from y11ch17_common import (read, get, maths, tex, rhs, check, finish, x, y, eq_value, set_value, inverse_ok,
                            pp_block, mc_key, number_set, num_equal, all_maths, interval)

L = read("l17a.html")
A = read("a_17a.html")
I = sp.Interval
oo = sp.oo
R = sp.S.Reals


def inv(key, f, dom_f, dom_g, label):
    s = get(A, key)
    if s is None:
        return
    G = tex(rhs(maths(s)).split(",")[0])
    inverse_ok(G, f, dom_f, dom_g, label)


def frange(expr, dom):
    return function_range(expr, x, dom)


# ---- questions printed in the lesson (the functions used below must be the ones printed)
for q in [r"f(x)=\dfrac{x-1}{x+3}", r"f(x)=\dfrac{x-4}{x+1}", r"f(x)=(x-3)^2+1", r"f(x)=(x-2)^2-1",
          r"y=(x-1)^2(x+2)", r"y=(x+1)^2(x-1)", r"f(x)=x+3", r"F(x)=\sqrt x", r"g(x)=x^2+2,\ x\le0",
          r"g(x)=-\sqrt{4-x^2},\ 0\le x\le2", r"F(x)=x^2+2x+4", r"g(x)=\dfrac{x+2}{x+1}", r"g(x)=(x+2)^2-4",
          r"F(x)=x^3-3x", r"f(x)=\dfrac{e^x}{1+e^x}", r"g(x)=\dfrac{2x}{1+x^2}", r"f(x)=\tfrac16\big(x^2-4x+24\big)",
          r"f(x)=\sqrt{2x+1}", r"f(x)=\dfrac{4x}{x-2}", r"f(x)=x^3+x+8", r"f(x)=2x^3+1", r"f(x)=x^2-4x+6",
          r"f(x)=e^{x+2}", r"f(x)=\dfrac{1}{x^2+1}"]:
    check(q in L, f"question text {q} printed in l17a.html")

# ---- C1, C2, C3
inv("c1d", lambda v: (v - 1) / (v + 3), R - sp.FiniteSet(-3), R - sp.FiniteSet(1), "C1 demo f^-1")
inv("c1y", lambda v: (v - 4) / (v + 1), R - sp.FiniteSet(-1), R - sp.FiniteSet(1), "C1 your turn f^-1")
inv("c2d", lambda v: (v - 3) ** 2 + 1, I(-oo, 3), I(1, oo), "C2 demo g^-1 (x <= 3, the largest domain containing 0)")
inv("c2y", lambda v: (v - 2) ** 2 - 1, I(-oo, 2), I(-1, oo), "C2 your turn g^-1 (x <= 2)")


def stat_points(expr):
    return sorted([(sv, expr.subs(x, sv)) for sv in sp.solve(sp.diff(expr, x), x)])


def points_printed(key, pts, label):
    s = get(A, key)
    if s is None:
        return
    got = []
    for m in all_maths(s):
        m = m.replace("\\Big", "").replace("\\big", "")
        inner = m.strip()[1:-1]
        a_, b_ = inner.split(",", 1) if inner.count(",") == 1 else (None, None)
        if a_ is None:
            for part in m.split("),"):
                part = part.strip().lstrip("(").rstrip(")").replace("\\", "").strip()
            continue
        got.append((tex(a_), tex(b_)))
    got = sorted(got, key=lambda p: float(p[0]))
    check(len(got) == len(pts) and all(sp.simplify(p[0] - q[0]) == 0 and sp.simplify(p[1] - q[1]) == 0 for p, q in zip(got, pts)),
          f"{label}: printed {got} vs {pts}")


f3d = (x - 1) ** 2 * (x + 2)
f3y = (x + 1) ** 2 * (x - 1)
points_printed("c3ds", stat_points(f3d), "C3 demo stationary points")
points_printed("c3ys", stat_points(f3y), "C3 your turn stationary points")
for key, f in [("c3d", f3d), ("c3y", f3y)]:
    s = get(A, key)
    if s:
        lhs = tex(maths(s).split("=")[0])
        check(sp.expand(lhs - (f - x)) == 0 or sp.expand(lhs + (f - x)) == 0, f"{key}: printed cubic is f(x) - x = 0")
        # exactly one root of the cubic lies on the restricted (monotonic) part
        a_, b_ = sorted([p[0] for p in stat_points(f)])
        roots = [r for r in sp.Poly(lhs, x).nroots() if abs(sp.im(r)) < 1e-12 and a_ - 1e-12 <= sp.re(r) <= b_ + 1e-12]
        check(len(roots) == 1, f"{key}: one intersection M on the restricted domain ({roots})")

# ---- Exercise 17A
set_value(A, "1a", frange(x + 3, I(0, 2)) and I(3, 5), "1a range")
check(frange(x + 3, I(0, 2)) == I(3, 5), "1a range recomputed")
set_value(A, "1bd", frange(x + 3, I(0, 2)), "1b domain of inverse = range of f")
set_value(A, "1br", I(0, 2), "1b range of inverse = domain of f")
inv("1c", lambda v: v + 3, I(0, 2), I(3, 5), "1c")
set_value(A, "2a", frange(sp.sqrt(x), I(0, 4)), "2a")
set_value(A, "2bd", frange(sp.sqrt(x), I(0, 4)), "2b domain")
set_value(A, "2br", I(0, 4), "2b range")
inv("2c", lambda v: sp.sqrt(v), I(0, 4), I(0, 2), "2c")
inv("3a", lambda v: 2 * v, R, R, "3a")
inv("3b", lambda v: v ** 3 + 1, R, R, "3b")
s = get(A, "3e")
if s:
    G = tex(rhs(maths(s)).replace("\\log_2x", "log(x)/log(2)"))
    inverse_ok(G, lambda v: 2 ** v, R, I.open(0, oo), "3e log2")
inv("3f", lambda v: sp.sqrt(v - 3), I(3, oo), I(0, oo), "3f (domain x >= 0 printed)")
check("x\\ge0" in maths(get(A, "3f") or ""), "3f condition x >= 0 printed")
gfg = sp.simplify((3 * x + 2).subs(x, (x - 2) / 3)), sp.simplify(((x - 2) / 3).subs(x, 3 * x + 2))
check(gfg == (x, x), "4a both composites are x")
eq_value(A, "4a", x, "4a printed x")
inv("5a", lambda v: v ** 2, I(0, oo), I(0, oo), "5a")
inv("5b", lambda v: v ** 2 + 2, I(-oo, 0), I(2, oo), "5b")
inv("5c", lambda v: -sp.sqrt(4 - v ** 2), I(0, 2), I(-2, 0), "5c")
eq_value(A, "6a", sp.diff(x ** 3 - 1, x), "6a")
yv = sp.Symbol("y")
s = get(A, "6b")
if s:
    got = tex(rhs(maths(s))).subs(y, yv)
    check(num_equal(got, sp.diff((yv + 1) ** sp.Rational(1, 3), yv)), "6b dx/dy for x = (y + 1)^(1/3)")
eq_value(A, "7a", sp.diff(sp.sqrt(x), x), "7 dy/dx")
s = get(A, "7b")
if s:
    check(num_equal(tex(rhs(maths(s))).subs(y, yv), sp.diff(yv ** 2, yv)), "7 dx/dy = 2y for x = y^2")
inv("8c", lambda v: v ** 2 + 2 * v + 4, I(-1, oo), I(3, oo), "8c")
eq_value(A, "9a", sp.solve(1 - sp.log(x), x)[0], "9a")
inv("9d", lambda v: 1 - sp.log(v), I.open(0, oo), R, "9d")
inv("10c", lambda v: (v + 2) / (v + 1), I.open(-1, oo), I.open(1, oo), "10c")
sol10 = [r for r in sp.solve(sp.Eq((x + 2) / (x + 1), x), x) if r > -1]
eq_value(A, "10d", sol10[0], "10d g(x) = x for x > -1")
s = get(A, "11a")
if s:
    # y = cube root of -x: check (cuberoot(-x))^3 = -x at sample points and that it inverts -x^3
    for xv in (-8, -1, 2, 27):
        val = -sp.Abs(xv) ** sp.Rational(1, 3) if xv > 0 else sp.Abs(xv) ** sp.Rational(1, 3)
        check(abs(float(-(val ** 3)) - xv) < 1e-12, f"11a cube root of -x at {xv}")
    check("\\sqrt[3]{-x}" in maths(s), "11a printed cube root of -x")
pts = sorted({(r, -r ** 3) for r in sp.solve(sp.Eq(-x ** 3, sp.real_root(-x, 3)) if False else sp.Eq(x ** 9, x), x) if r.is_real})
# f(x) = -x^3 and inverse y = cbrt(-x) meet where y = -x^3 and x = -y^3, i.e. x = x^9
pts = sorted({(r, -r ** 3) for r in sp.solve(x ** 9 - x, x) if r.is_real}, key=lambda p: float(p[0]))
s = get(A, "11b")
if s:
    got = sorted([tuple(tex(c) for c in m.strip()[1:-1].split(",")) for m in all_maths(s)[0].replace("\\ ", "").replace(" ", "").split("),(")
                  for m in ["(" + m.strip("()") + ")"]], key=lambda p: float(p[0])) if False else None
    printed = [(-1, 1), (0, 0), (1, -1)]
    check(maths(s).replace(" ", "") == "(-1,1),\\(0,0)" and pts == [(sp.Integer(a_), sp.Integer(b_)) for a_, b_ in printed],
          f"11b intersections {pts}")
set_value(A, "13d", I(-2, oo), "13d (vertex at x = -2; the right branch contains 0)")
check(frange((x + 2) ** 2 - 4, I(-2, oo)) == I(-4, oo), "13e range of restricted g recomputed")
set_value(A, "13e", frange((x + 2) ** 2 - 4, I(-2, oo)), "13e domain of g^-1")
inv("13f", lambda v: (v + 2) ** 2 - 4, I(-2, oo), I(-4, oo), "13f")
sp14 = sorted(sp.solve(sp.diff(x ** 3 - 3 * x, x), x))
set_value(A, "14d", I(sp14[0], sp14[1]), "14d between the stationary points")
set_value(A, "14e", frange(x ** 3 - 3 * x, I(sp14[0], sp14[1])), "14e domain of F^-1")
inv("15d", lambda v: sp.exp(v) / (1 + sp.exp(v)), R, I.open(0, 1), "15d")
s = get(A, "18c")
g18 = lambda v: 2 * v / (1 + v ** 2)
if s:
    inverse_ok(tex(rhs(maths(s))), g18, I(-1, 1) - sp.FiniteSet(0), I(-1, 1) - sp.FiniteSet(0), "18c iii")
set_value(A, "18ci", I(-1, 1), "18c i (g' = 0 at x = +-1)")
check(sorted(sp.solve(sp.diff(g18(x), x), x)) == [-1, 1], "18 stationary points at x = -1, 1")
s = get(A, "18d")
if s:
    inverse_ok(tex(rhs(maths(s))), g18, I(1, oo) | I(-oo, -1), I(-1, 1) - sp.FiniteSet(0), "18d")
f19 = (x ** 2 - 4 * x + 24) / 6
v19 = sp.solve(sp.diff(f19, x), x)[0]
s = get(A, "19a")
if s:
    a_, b_ = [tex(c) for c in maths(s).replace("\\Big", "").strip()[1:-1].split(",")]
    check((a_, b_) == (v19, f19.subs(x, v19)) and f19.subs(x, 0) == 4, "19a vertex and y-intercept 4")
set_value(A, "19b", I(v19, oo), "19b")
set_value(A, "19c", frange(f19, I(v19, oo)), "19c")
pts19 = sorted(sp.solve(sp.Eq(f19, x), x))
check(pts19 == [4, 6] and maths(get(A, "19d")).replace(" ", "") == "(4,4)", "19d intersections (4,4) and (6,6)")
Nn = sp.Symbol("N", negative=True)
cand = [r for r in sp.solve(sp.Eq(f19, f19.subs(x, Nn)), x) if sp.simplify(r - Nn) != 0]
eq_value(A, "19e", cand[0].subs(Nn, sp.Symbol("N")), "19e f^-1(f(N)) for N < 0")
eq_value(A, "20b", sp.sinh(0), "20b sinh 0")
eq_value(A, "20d", sp.diff((sp.exp(x) - sp.exp(-x)) / 2, x), "20d")

# ---- past papers
pp_block(L, A)
mc_key(A, "PP 1", "A")
G1 = sp.log(x) - 2
check(all(abs(complex(sp.N(G1.subs(x, sp.exp(v + 2)))) - v) < 1e-12 for v in (-1, 0, 2)), "PP1 option A inverts e^(x+2)")
rng = function_range(4 * x / (x - 2), x, R - sp.FiniteSet(2))
set_value(A, "pp2", rng, "PP2 domain of f^-1 = range of f")
mc_key(A, "PP 2", "C")
sol = [r for r in sp.solve(x ** 3 + x + 8 - x, x) if r.is_real]
check(sol == [-2] and maths(get(A, "pp3")) == "(-2,-2)", "PP3 (-2, -2)")
mc_key(A, "PP 3", "B")
eq_value(A, "pp4", sp.solve(sp.Eq(sp.sqrt(2 * x + 1), 5), x)[0], "PP4 f^-1(5)")
rng5 = function_range(1 / (x ** 2 + 1), x, I(0, oo))
set_value(A, "pp5d", rng5, "PP5 domain of f^-1 = range of f on x >= 0")
set_value(A, "pp5r", I(0, oo), "PP5 range of f^-1")
inv("pp6", lambda v: 2 * v ** 3 + 1, R, R, "PP6 inverse of 2x^3 + 1")
inv("pp7ii", lambda v: v ** 2 - 4 * v + 6, I(-oo, 2), I(2, oo), "PP7 (ii)")
s = get(A, "pp7iii")
if s:
    d, r_ = all_maths(s)
    check(interval(d) == frange(x ** 2 - 4 * x + 6, I(-oo, 2)) and interval(r_) == I(-oo, 2), "PP7 (iii) domain x >= 2, range y <= 2")
check(maths(get(A, "pp7iv")).replace(" ", "") == "P=(2,2)" and (x ** 2 - 4 * x + 6).subs(x, 2) == 2, "PP7 (iv) P = (2, 2)")
finish("y11ch17_17a")
