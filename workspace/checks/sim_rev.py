r"""Check of the Simultaneous Equations revision warm-up, tied to the printed HTML and the answer graph.

Reads the questions in build/sim/revision.html (<span data-q>) and the printed answers in a_rev.html
(<span data-v> numbers, <span data-k> coordinates and gradients). Every answer is recomputed with sympy
from the question as printed: Q1 by substitution, Q2 and Q3 by solving, the Q4 table from the rule, Q5
by putting y = 0 and x = 0, Q6 from the rule in the form y = mx + b. The Q4 answer graph svg/rev_w4a.svg
is read back: the plotted line must be the rule and every plotted point must be a table point on it.
The working of Q2 and Q3 is also tested: every equation printed in it must hold at the solution.
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 -I workspace/checks/sim_rev.py
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_common import (Values, ok, finish, check_num, equations, maths, tex2sym, points, holds,  # noqa: E402
                        plotted_lines, marked_points, same_line, on_line, read, assignments, axis_scale)
import sympy as sp  # noqa: E402

V = Values(["revision.html", "a_rev.html"])
A = read("a_rev.html")
x, y = sp.Symbol("x"), sp.Symbol("y")

# Q1: evaluate 2x - 3y
expr = tex2sym(maths(V.get("q", "w1"))[0])
for p in "adf":
    vals = assignments(V.get("q", f"w1{p}"))
    check_num(V, f"w1{p}", expr.subs({sp.Symbol(k): v for k, v in vals.items()}), "2x - 3y")

# Q2, Q3: solve one linear equation; the working shown before the answer must hold at the solution
for key in ("w2b", "w2d", "w2e", "w2h", "w3a", "w3d", "w3h"):
    (eq,) = equations(V.get("q", key))
    var = (eq[0] - eq[1]).free_symbols.pop()
    sol = sp.solve(eq[0] - eq[1], var)
    ok(len(sol) == 1, f"{key}: one solution", str(sol))
    check_num(V, key, sol[0], f"{eq[0]} = {eq[1]}")
    m = re.search(r'<b>%s</b>(.*?)</div>' % key[-1], A[A.index("Exercise 2B Q8" if key.startswith("w2") else "Exercise 2E Q7"):], re.S)
    lines = [e for e in equations(m.group(1)) if not (e[0].is_number and e[1].is_number and e[0] == e[1])]
    bad = [f"{l} = {r}" for l, r in lines if not holds((l, r), {var.name: sol[0]})]
    ok(len(lines) >= 3 and not bad, f"{key}: every working line holds at {var} = {sol[0]}", f"{len(lines)} lines; " + "; ".join(bad))

# Q4: table and graph of y = 3 - x
(rule,) = equations(V.get("q", "w4c"))
f = sp.solve(rule[0] - rule[1], y)[0]
for xv, k in zip(range(-3, 4), ("m3", "m2", "m1", "0", "1", "2", "3")):
    check_num(V, f"w4c_{k}", f.subs(x, xv), f"y at x = {xv}")
L = plotted_lines("rev_w4a")
ok(len(L) == 1 and same_line(L[0], rule), "rev_w4a: the plotted line is y = 3 - x", str([l[:3] for l in L]))
P = marked_points("rev_w4a", "pt")
ok(sorted(round(p[0], 2) for p in P) == list(range(-3, 4)) and all(on_line(L[0], p) for p in P),
   "rev_w4a: the seven table points are plotted on the line", str([(round(a, 2), round(b, 2)) for a, b in P]))

# Q5: axis intercepts
for p in "bcd":
    (eq,) = equations(V.get("q", f"w5{p}"))
    e = eq[0] - eq[1]
    xi = sp.solve(e.subs(y, 0), x)[0]
    yi = sp.solve(e.subs(x, 0), y)[0]
    got = points(V.get("k", f"w5{p}"))
    ok(got == [(xi, 0), (0, yi)], f"w5{p} intercepts", f"printed {got}, computed {[(xi, 0), (0, yi)]}")

# Q6: gradient and y-intercept
for p in "aej":
    (eq,) = equations(V.get("q", f"w6{p}"))
    f = sp.expand(sp.solve(eq[0] - eq[1], y)[0])
    got = assignments(V.get("k", f"w6{p}"))
    want = {"m": f.coeff(x), "b": f.subs(x, 0)}
    ok(got == want, f"w6{p} gradient and y-intercept", f"printed {got}, computed {want}")

# revision figures: the Example 2 graph and the 7E figure are y = 2x - 1 through the labelled points
for fig in ("rev_7b", "rev_7e"):
    L = plotted_lines(fig)
    ok(len(L) == 1 and same_line(L[0], (y, 2 * x - 1)), f"{fig}: the line is y = 2x - 1")
    P = marked_points(fig, "pt")
    ok(P and all(on_line(L[0], p) for p in P), f"{fig}: every marked point is on the line", str(len(P)))
axis_scale("rev_w4")

finish([V])
