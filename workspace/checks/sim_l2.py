r"""Check of Lesson 2 (the elimination method), tied to the printed HTML.

Reads build/sim/l2.html (questions: <span data-q>) and a_l2.html (answers: data-s, data-w, data-c, data-k).
Every pair is re-solved with sympy from the equations AS PRINTED in the lesson and compared with the
printed solution; every equation printed in the working must hold at that solution (so a wrong
multiple, sum or difference fails), and every printed check must be true and must substitute into both
original equations. Concept 3's printed choice of method is recomputed from the pair (a variable
already the subject -> substitution; equal or opposite coefficients -> elimination).
The hidden pairs (surds, indices) are checked twice: the printed linear pair is solved, and that
solution must satisfy the ORIGINAL printed equation(s); for the surd item the parts must be rational
and the surd part must be irrational, so the split into a pair is valid.
Multiple-choice keys are recomputed: PP 1 from the options' points; PP 2 by testing which option is a
y-free combination of the two printed equations. PP 7 and Hard Q10 values (p + q, c + a) and the PP 10
concurrency verdict are recomputed. Labels must agree in both files; marks must add to the total.
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 -I workspace/checks/sim_l2.py
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_common import (Values, ok, finish, check_pair, equations, points, holds, assignments,  # noqa: E402
                        solve_pair, read, maths)
import sympy as sp  # noqa: E402

V = Values(["l2.html", "a_l2.html"])
L2, A2 = read("l2.html"), read("a_l2.html")
x, y = sp.Symbol("x"), sp.Symbol("y")


def pair(key, n=2):
    eqs = equations(V.get("q", key))
    ok(len(eqs) == n, f"{key}: {n} equations printed", str(eqs))
    return eqs


def word(key):
    return re.sub(r"<[^>]+>", "", V.get("k", key) or "").strip().lower()


def coeffs(eq):
    e = sp.expand(eq[0] - eq[1])
    return {s.name: e.coeff(s) for s in e.free_symbols}


def subject(eq):
    """The variable that is alone on one side (y = ..., x = ...), or None."""
    for side, other in ((eq[0], eq[1]), (eq[1], eq[0])):
        if side.is_Symbol and side not in other.free_symbols:
            return side.name
    return None


# ================= Concepts 1 and 2 =================
for key in ("d1a", "d1b", "y1a", "y1b", "d2a", "d2b", "y2a", "y2b"):
    eqs = pair(key)
    check_pair(V, key, eqs)
    c1, c2 = coeffs(eqs[0]), coeffs(eqs[1])
    direct = any(abs(c1[v]) == abs(c2[v]) for v in c1)
    ok(direct == key.startswith(("d1", "y1")), f"{key}: {'no multiplying needed' if direct else 'a multiple is needed'} "
       f"(the concept it is set under)")
check_pair(V, "ex22", pair("ex22"))

# ================= Concept 3: choose a method =================
for key in ("d3a", "d3b", "y3a", "y3b"):
    eqs = pair(key)
    check_pair(V, key, eqs)
    if any(subject(e) for e in eqs):
        want = "substitution"
    else:
        c1, c2 = coeffs(eqs[0]), coeffs(eqs[1])
        want = "elimination" if any(abs(c1[v]) == abs(c2[v]) for v in c1) else "?"
    ok(word(key) == want, f"{key}: the better method is {want}", f"printed {word(key)!r}")

# ================= Homework =================
book2 = {"a": (3, 2), "b": (1, -2), "c": (4, 1), "d": (-1, 3), "e": (2, 2), "f": (-2, -3)}   # answers PDF 518
for p in "abcdef":
    eqs = pair("h1" + p)
    sol = check_pair(V, "h1" + p, eqs)
    vs = sorted(sol)
    ok((sol[vs[0]], sol[vs[1]]) == book2[p], f"h1{p} agrees with the book's answer", str(sol))
book4 = {"a": (-1, 3), "b": (5, 2), "c": (-4, 3), "d": (2, -6), "e": (1, 2), "f": (16, -24), "g": (1, 6),
         "h": (5, -2), "i": (5, 6), "j": (7, 5)}
for p in "abcdefghij":
    sol = check_pair(V, "h4" + p, pair("h4" + p))
    ok((sol["x"], sol["y"]) == book4[p], f"h4{p} agrees with the book's answer", str(sol))
for key in ("hws1a", "h2", "h3", "h5", "h6", "h7", "h8", "h9"):
    check_pair(V, key, pair(key))

# Q10: c + a
sol = check_pair(V, "h10", pair("h10"))
check_val = sol["c"] + sol["a"]
ok(sp.nsimplify(maths(V.get("k", "h10"))[0]) == check_val, "h10: c + a", f"computed {check_val}")

# Q11: surds. The printed pair, then the original equation
(orig,) = equations(V.get("q", "h11"))
lin = equations(V.get("q", "h11p"))
sol = check_pair(V, "h11", lin)
a, b = sp.Symbol("a"), sp.Symbol("b")
ok(holds(orig, sol), "h11: the solution satisfies the original surd equation")
ok(all(e.subs({a: sol["a"], b: sol["b"]}).is_rational for e in (a + 2 * b,))
   and not sp.sqrt(3 * sol["a"] - sol["b"]).is_rational and sp.sqrt(3 * sol["a"] - sol["b"]) == 2 * sp.sqrt(5),
   "h11: rational part 2 and surd part 2 sqrt 5 match separately")
ok(lin[0] == (a + 2 * b, 2) and sp.expand(lin[1][0]) == 3 * a - b and lin[1][1] == 20,
   "h11: the pair is the rational parts and the squared surd parts", str(lin))

# Q12: indices, a = 2^p and b = 2^q
orig = equations(V.get("q", "h12"))
lin = equations(V.get("q", "h12p"))
sol = check_pair(V, "h12", lin)
p_, q_ = sp.Symbol("p"), sp.Symbol("q")
sub = {a: 2 ** sol["p"], b: 2 ** sol["q"]}
ok(len(orig) == 2 and all(sp.simplify(l.subs(sub) - r) == 0 for l, r in orig), "h12: a = 2^p, b = 2^q satisfy ab = 32 and 2a^2 b = 32")
ok(all(v.is_integer for v in sol.values()), "h12: p and q are integers")
# the linear pair follows from the originals: compare exponents of 2
for (l, r), (ll, rr) in zip(orig, lin):
    expo = sp.simplify(sp.log(l.subs({a: 2 ** p_, b: 2 ** q_}), 2) - sp.log(r, 2))
    ok(sp.simplify(sp.expand_log(expo, force=True) - (ll - rr)) == 0, f"h12: {l} = {r} gives {ll} = {rr}")

# Q13: indices
orig = equations(V.get("q", "h13"))
lin = equations(V.get("q", "h13p"))
sol = check_pair(V, "h13", lin)
ok(len(orig) == 2 and all(holds(e, sol) for e in orig), "h13: the solution satisfies 4^(x+y) = 64 and 7^(2x-y) = 49 sqrt 7")
ok(sp.simplify(sp.log(64, 4) - 3) == 0 and sp.simplify(sp.log(49 * sp.sqrt(7), 7) - sp.Rational(5, 2)) == 0,
   "h13: exponents 3 and 5/2")

# ================= Past papers =================
labels_l = re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</span>', L2)
labels_a = re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</span>', A2)
ok(labels_l == labels_a and len(labels_l) == 10, "past-paper labels identical in both files", f"{len(labels_l)} items")
hard_l = re.findall(r'<span class="muted small">([^<]*(?:School|College)[^<]*)</span>', L2)
hard_a = re.findall(r'<span class="muted small">([^<]*(?:School|College)[^<]*)</span>', A2)
ok(hard_l == hard_a and len(hard_l) == 6, "Hard-band school labels identical in both files", f"{len(hard_l)}")
marks = [int(n) for n in re.findall(r'<span class="mk">(\d+) marks?</span>', L2)]
total = int(re.search(r"<b>(\d+) marks</b>", L2).group(1))
mins = int(re.search(r"Suggested time: (\d+) minutes", L2).group(1))
ok(len(marks) == 10 and sum(marks) == total and 15 <= total <= 22, "mini exam marks add to the printed total (15-22)",
   f"{marks} = {sum(marks)}")
ok(mins == 5 * round(1.5 * total / 5), "suggested time is 1.5 x marks to the nearest 5 minutes", f"{mins} min")


def mc(key, correct):
    t = re.sub(r"<[^>]+>", "", V.get("k", key) or "").strip()
    ok(t == correct, f"{key} key", f"printed {t}, computed {correct}")


sol = check_pair(V, "pp1", pair("pp1"))
good = [L for L in "ABCD" if points(V.get("q", "pp1" + L)) == [(sol["x"], sol["y"])]]
ok(len(good) == 1, "pp1: exactly one option is the solution", str(good))
mc("pp1", good[0] if good else "?")

e1, e2 = [sp.expand(l - r) for l, r in pair("pp2")]
yfree = sp.expand(e1 - e1.coeff(y) / e2.coeff(y) * e2)          # the y-free combination of (1) and (2)
good = []
for L in "ABCD":
    (opt,) = equations(V.get("q", "pp2" + L))
    oe = sp.expand(opt[0] - opt[1])
    if oe.coeff(y) == 0 and sp.simplify(oe / yfree).is_number:
        good.append(L)
ok(len(good) == 1, "pp2: exactly one option is a y-free combination of the two equations", str(good))
mc("pp2", good[0] if good else "?")

for key in ("pp3", "pp4", "pp5", "pp6", "pp8", "pp9"):
    check_pair(V, key, pair(key))
sol = check_pair(V, "pp7", pair("pp7"))
ok(sp.nsimplify(maths(V.get("k", "pp7"))[0]) == sol["p"] + sol["q"], "pp7: p + q", str(sol["p"] + sol["q"]))
three = pair("pp10", 3)
sol = check_pair(V, "pp10", three[:2])
conc = holds(three[2], sol)
ok(word("pp10") == ("yes" if conc else "no"), "pp10: concurrent", f"third line holds: {conc}")

for key, method in (("pp3", "elimination"), ("pp6", "elimination"), ("pp8", "elimination"), ("h9", "elimination")):
    src = V.d["q"][key][0]
    stem = L2[:L2.index(src)][-400:]
    ok(method in stem.lower(), f"{key}: the question names the {method} method and the answer uses it")

finish([V])
