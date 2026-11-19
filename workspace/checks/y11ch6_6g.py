"""Revision 6G: every printed simplification, identity, elimination and the past-paper answers,
read from r6g.html / a_6g.html and recomputed numerically with sympy."""
import math, re
import sympy as sp
from y11ch6_common import *

L, A = read("r6g.html"), read("a_6g.html")
S, P, E, F, ANS = spans(L, "data-s"), spans(L, "data-p"), spans(L, "data-e"), spans(L, "data-f"), spans(A, "data-a")

for k, q in S.items():                       # simplify / independent of theta: question equals printed answer
    a = need(ANS, k, "answer")
    if a is None: continue
    check(num_equal(tex(q), tex(a)), f"{k}: {q} != {a}")
for k, a in ANS.items():
    if k.startswith("g") and k not in S and k not in E:
        fail(f"answer {k} has no question")

for k, q in P.items():                       # identities to prove: every side agrees (catches typos)
    sides = re.sub(r"^\\\(|\\\)$", "", q.strip()).split("=")
    ex = [tex(s) for s in sides]
    for i in range(1, len(ex)):
        check(num_equal(ex[0], ex[i]), f"identity {k} fails: {q}")

th = sp.Symbol("theta")
for k in E:                                   # elimination: printed relation holds along the curve
    x = tex(re.sub(r"x=", "", E[k], count=1)); y = tex(re.sub(r"y=", "", F[k], count=1))
    rel = re.sub(r"^\\\(|\\\)$", "", need(ANS, k, "answer").strip()).split("=")
    X, Y = sp.Symbol("x"), sp.Symbol("y")
    lhs, rhs = tex(rel[0]), tex(rel[1])
    d = sp.lambdify([X, Y], lhs - rhs, "math")
    fx, fy = sp.lambdify(list(x.free_symbols), x, "math"), sp.lambdify(list(y.free_symbols), y, "math")
    worst = max(abs(d(fx(t), fy(t))) for t in [0.3, 0.7, 1.1, 2.0, 2.6, 4.0, 5.5])
    check(worst < 1e-9, f"{k}: relation {rel} fails, residual {worst}")

# PP 2: cosec t - cot t = 4/5. Brute force over 0 < t < 360 degrees, then tan t.
g = lambda t: 1 / math.sin(math.radians(t)) - 1 / math.tan(math.radians(t)) - 0.8
rs = roots_deg(g, 0.01, 359.99)
check(len(rs) == 1, f"PP2 roots {rs}")
printed = tex(re.sub(r"\\tan\\theta=", "", need(ANS, "pp2", "answer")))
for r in rs:
    check(abs(math.tan(math.radians(r)) - float(printed)) < 1e-6, f"PP2 tan = {math.tan(math.radians(r))}, printed {printed}")
finish("y11ch6_6g")
