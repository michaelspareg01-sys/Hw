"""Lesson 6H: every equation printed in l6h.html (demos, your turns, worked examples, Exercise 6H)
is solved by brute force over the domain printed with it, and compared with the printed solutions
(l6h.html for the worked examples, a_6h.html for the rest)."""
import math, re
import sympy as sp
from y11ch6_common import *

L, A = read("l6h.html"), read("a_6h.html")
SOL = spans(L, "data-sol"); SOL.update(spans(A, "data-sol"))
DOM = re.compile(r"(-?\d+)(?:\^\\circ)?\s*\\le\s*\\?([a-z]+)\s*\\le\s*(-?\d+)\^\\circ")
n_eq = 0
for m in re.finditer(r'<span data-eq="([\w-]+)" data-dom="(-?\d+),(-?\d+)">(.*?)</span>', L, re.S):
    key, lo, hi, q = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
    n_eq += 1
    # the domain the student sees: just after the equation, or else in the question stem before it
    win = L[m.end():m.end() + 160]
    cut = min([i for i in (win.find('<span class="pl"'), win.find('</div>'), win.find('<br>')) if i >= 0] + [160])
    after = DOM.search(win[:cut])
    if after:
        pr = (int(after.group(1)), int(after.group(3)))
    else:
        start = max(L.rfind('class="q-body"', 0, m.start()), L.rfind('class="pp-q"', 0, m.start()))
        ds = list(DOM.finditer(L, start, m.start()))
        pr = (int(ds[-1].group(1)), int(ds[-1].group(3))) if ds else None
    check(pr == (lo, hi), f"{key}: printed domain {pr} vs data-dom {(lo, hi)}")
    lhs, rhs = re.sub(r"^\\\(|\\\)$", "", q.strip()).split("=")
    e = tex(lhs) - tex(rhs)
    var = [s for s in e.free_symbols if str(s) in ("x", "theta", "alpha")]
    check(len(var) == 1, f"{key}: variables {e.free_symbols}")
    fn = sp.lambdify(var, e, "math")
    roots = roots_deg(lambda d: fn(math.radians(d)), lo, hi)
    s = need(SOL, key, "solution")
    if s is None: continue
    if "aligned" in s:
        s = s.split("x&=")[-1]
    printed = [] if "no solution" in s else parse_angles(s)
    check(len(printed) > 0 or "no solution" in s, f"{key}: could not read '{s}'")
    if len(roots) != len(printed):
        fail(f"{key}: roots {[round(r, 4) for r in roots]} vs printed {printed}"); continue
    for r, p in zip(sorted(roots), sorted(printed)):
        exact = abs(r - p) < 1e-6
        if p == int(p):
            good = exact or round(r) == p
        else:
            good = exact or round(r * 60) == round(p * 60)
        check(good, f"{key}: root {r:.5f} printed {p}")
for k in SOL:
    if not re.search(r'data-eq="%s"' % k, L):
        fail(f"solution {k} has no equation")
for k, q in spans(L, "data-p").items():                      # identities in the past-paper set
    sides = re.sub(r"^\\\(|\\\)$", "", q.strip()).split("=")
    check(num_equal(tex(sides[0]), tex(sides[1])), f"identity {k}")
print("equations checked:", n_eq)
finish("y11ch6_6h")
