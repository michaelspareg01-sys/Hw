"""Check of the Chapter 15 revision warm-up answers, tied to the HTML.

Reads the printed values from workspace/build/y11ch15/a_rev.html and the given
data of each question from revision.html.  Every template (numbers: '@') and every
regex must match exactly once in its answer block, otherwise the item FAILS.
Printed algebra is parsed with sympy and compared with independently recomputed
values; counting answers are brute-forced with itertools.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch15_rev.py
"""
import os
import re
import sys
from fractions import Fraction as F
from itertools import permutations, combinations
from math import comb, factorial

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH15_SRC", os.path.join(HERE, "..", "build", "y11ch15"))   # override only for mutation tests

VAL = r"(\d+)"
x, n = sp.symbols("x n")
TRANS = standard_transformations + (implicit_multiplication_application,)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def blocks(text):
    d = {}
    for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S):
        d[an.strip()] = ab
    return d


fails = 0
checked = 0


def fail(msg):
    global fails
    print("FAIL " + msg)
    fails += 1


def ok(msg):
    global checked
    checked += 1
    print("OK   " + msg)


def check(label, block, template, expected):
    """Template with '@' for each integer; must match exactly once; values compared in order."""
    rx = re.compile("".join(VAL if ch == "@" else re.escape(ch) for ch in template))
    found = rx.findall(block)
    if len(found) != 1:
        fail(f"{label}: template matched {len(found)} times: {template}")
        return
    got = found[0] if isinstance(found[0], tuple) else (found[0],)
    if len(got) != len(expected):
        fail(f"{label}: {len(got)} placeholders, {len(expected)} expected values")
        return
    for i, (g, e) in enumerate(zip(got, expected)):
        if int(g) == e:
            ok(f"{label} [{i + 1}] {g}")
        else:
            fail(f"{label} [{i + 1}]: printed {g}, recomputed {e}")


def to_sympy(s):
    """Convert the limited LaTeX used in this file to a sympy expression."""
    s = s.replace("\\Big", "").replace("\\,", "").replace("\\times", "*").replace("\\left", "").replace("\\right", "")
    s = re.sub(r"\\dfrac(\d)([\dx])", r"((\1)/(\2))", s)
    s = re.sub(r"\\sqrt\[(\d+)\]\{([^{}]*)\}", r"((\2)**(1/\1))", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", s)
    for _ in range(4):
        s = re.sub(r"\\dfrac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
    s = re.sub(r"\^(\d+)", r"**\1", s)
    s = s.replace("{", "(").replace("}", ")")
    return parse_expr(s, local_dict={"x": x, "n": n}, transformations=TRANS)


def chain(label, block, regex, expected, symbols=None):
    """regex (exactly one match, one group) captures a printed chain a=b=c; every link must equal `expected`."""
    found = re.findall(regex, block, re.S)
    if len(found) != 1:
        fail(f"{label}: regex matched {len(found)} times: {regex}")
        return
    links = found[0].split("=")
    for i, link in enumerate(links):
        try:
            val = to_sympy(link)
        except Exception as e:                                   # unparsable printed text is a failure
            fail(f"{label} link {i + 1} '{link}' unparsable: {e}")
            continue
        if sp.simplify(val - expected) == 0:
            ok(f"{label} link {i + 1} '{link}'")
        else:
            fail(f"{label} link {i + 1} '{link}' = {val}, recomputed {expected}")


def qblock(rev, num):
    m = re.findall(r'<span class="q-num">%d</span>(.*?)\{\{work' % num, rev, re.S)
    if len(m) != 1:
        fail(f"revision.html question {num} not found exactly once")
        sys.exit(1)
    return m[0]


def part(qb, letter):
    m = re.findall(r'<span class="pl">%s</span>(.*?)</span>' % letter, qb, re.S)
    if len(m) != 1:
        fail(f"given part {letter} not found exactly once")
        sys.exit(1)
    return m[0]


def math_of(s):
    m = re.findall(r"\\\((.*?)\\\)", s)
    if len(m) != 1:
        fail(f"expected one math group in given: {s!r}")
        sys.exit(1)
    return m[0]


rev = read("revision.html")
ans = blocks(read("a_rev.html"))
for q in "12345":
    if q not in ans:
        fail(f"answer block {q} missing")
if fails:
    sys.exit(1)

# ---------------- Q1: factorial quotient and nCr values (givens read from revision) ----------------
q1 = qblock(rev, 1)
b = ans["1"]
m = re.fullmatch(r"\\dfrac\{(\d+)!\}\{(\d+)!\}", math_of(part(q1, "a")))
a1, a2 = int(m.group(1)), int(m.group(2))
check("Q1a", b, r"\(\dfrac{@!}{@!}=@\times@=@\)",
      [a1, a2, a1, a1 - 1, factorial(a1) // factorial(a2)])      # 7!/5! = 7 x 6 = 42
m = re.fullmatch(r"\{\}\^(\d+)C_(\d+)", math_of(part(q1, "b")))
nb, rb = int(m.group(1)), int(m.group(2))
check("Q1b", b, r"\({}^@C_@=\dfrac{@\times@\times@}{@\times@\times@}=@\)",
      [nb, rb, nb, nb - 1, nb - 2, 3, 2, 1, comb(nb, rb)])
m = re.fullmatch(r"\{\}\^\{(\d+)\}C_\{(\d+)\}, using .*", part(q1, "c").replace("\\(", "").replace("\\)", "").strip())
nc, rc = int(m.group(1)), int(m.group(2))
sym = nc - rc
check("Q1c", b, r"\({}^{@}C_{@}={}^{@}C_{@}=\dfrac{@\times@}{@\times@}=@\)",
      [nc, rc, nc, sym, nc, nc - 1, sym, 1, comb(nc, rc)])
assert comb(nc, rc) == comb(nc, sym)
terms = [(int(p), int(r)) for p, r in re.findall(r"\{\}\^\{(\d+)\}C_\{?(\d+)\}?", math_of(part(q1, "d")))]
if len(terms) != 4:
    fail("Q1d given should have 4 terms")
else:
    v = [comb(*t) for t in terms]
    check("Q1d pair 1", b, r"\({}^{@}C_@={}^{@}C_{@}=@\) and", [terms[0][0], terms[0][1], terms[3][0], terms[3][1], v[0]])
    check("Q1d pair 2", b, r"and \({}^{@}C_@={}^{@}C_@=@\), so the sum is", [terms[1][0], terms[1][1], terms[2][0], terms[2][1], v[1]])
    check("Q1d sum", b, r"so the sum is \(@+@+@+@=@\)", v + [sum(v)])

# ---------------- Q2: nC1, nC2 in terms of n; nC2 = 45 ----------------
q2 = qblock(rev, 2)
b = ans["2"]
for N in range(2, 40):
    assert comb(N, 1) == N and comb(N, 2) == N * (N - 1) // 2
chain("Q2a nC1", b, r"\{\}\^nC_1=(.*?)\\\) and", n)                     # a chain whose links must equal n
found = re.findall(r"\{\}\^nC_1=\\dfrac\{n!\}\{1!\\,\(n-1\)!\}=n\\\)", b)
if len(found) != 1:
    fail("Q2a nC1 formula line not matched exactly once")
else:
    ok("Q2a nC1 formula line")
found = re.findall(r"\{\}\^nC_2=\\dfrac\{n!\}\{2!\\,\(n-2\)!\}=\\dfrac\{n\(n-1\)\}\{2\}", b)
if len(found) != 1:
    fail("Q2a nC2 formula line not matched exactly once")
else:
    ok("Q2a nC2 formula line")
found = re.findall(r"=\\dfrac\{(n\(n-1\))\}\{(\d+)\}", b)
if len(found) != 1:
    fail("Q2a printed closed form not found")
else:
    expr = to_sympy(found[0][0]) / int(found[0][1])
    if all(expr.subs(n, N) == comb(N, 2) for N in range(2, 40)):
        ok(f"Q2a printed closed form n(n-1)/2 agrees with comb(N,2) for N=2..39")
    else:
        fail("Q2a closed form wrong")
m = re.findall(r"\\\(\{\}\^nC_2=(\d+)\\\)", part(q2, "b"))
if len(m) != 1:
    fail("Q2b given not found")
    sys.exit(1)
target = int(m[0])
sols = [N for N in range(2, 500) if comb(N, 2) == target]
if len(sols) != 1:
    fail(f"Q2b brute force gives {sols}")
    sys.exit(1)
N0 = sols[0]
quad = sp.expand(n * (n - 1) - 2 * target)
check("Q2b", b, r"\(\dfrac{n(n-1)}{2}=@\) gives \(n^2-n-@=0\), so \((n-@)(n+@)=0\). Since \(n>0\), \(n=@\).",
      [target, 2 * target, N0, N0 - 1, N0])
assert sp.expand((n - N0) * (n + N0 - 1) - quad) == 0

# ---------------- Q3: index laws (givens read from revision) ----------------
q3 = qblock(rev, 3)
b = ans["3"]
ga, gb, gc, gd = (to_sympy(math_of(part(q3, l))) for l in "abcd")
chain("Q3a", b, r"<b>a</b> \\\((.*?)\\\)<br><b>b</b>", ga)
chain("Q3b", b, r"<b>b</b> \\\((.*?)\\\)<br><b>c</b>", gb)
chain("Q3c", b, r"<b>c</b> \\\((.*?)\\\)<br><b>d</b>", gc)
chain("Q3d", b, r"<b>d</b> \\\((.*?)\\\)$", gd)
exp3 = {"a": 8 * x**6, "b": 9 * x, "c": -8 / x**3, "d": sp.Rational(1, 4)}      # independent expectations
for l, g in zip("abcd", (ga, gb, gc, gd)):
    if sp.simplify(g - exp3[l]) == 0:
        ok(f"Q3{l} given simplifies to {exp3[l]}")
    else:
        fail(f"Q3{l} given = {g}, not {exp3[l]}")

# ---------------- Q4: expansions (givens read from revision) ----------------
q4 = qblock(rev, 4)
b = ans["4"]
g4a = to_sympy(re.findall(r"Expand \\\((.*?)\\\)\.", part(q4, "a"))[0])
g4b = to_sympy(re.findall(r"Expand and simplify \\\((.*?)\\\)\.", part(q4, "b"))[0])
g4c = to_sympy(re.findall(r"expansion of \\\((.*?)\\\)\.", part(q4, "c"))[0])
chain("Q4a", b, r"<b>a</b> \\\((.*?)\\\)<br><b>b</b>", sp.expand(g4a))
chain("Q4b", b, r"<b>b</b> \\\((.*?)\\\)<br><b>c</b>", sp.expand(g4b))
coef = sp.Poly(sp.expand(g4c), x).coeff_monomial(x**2)
chain("Q4c coefficient", b, r"so the coefficient is \\\((.*?)\\\)", coef)
pc = re.findall(r"come from \\\((.*?)\\\) and \\\((.*?)\\\), so", b)
if len(pc) != 1:
    fail("Q4c contributing pairs not matched exactly once")
else:
    c1 = sp.Poly(sp.expand((1 + 2 * x)), x).all_coeffs()[::-1]
    c2 = sp.Poly(sp.expand((3 - x + x**2)), x).all_coeffs()[::-1]
    pairs = {sp.expand(c1[i] * x**i * c2[j] * x**j) for i in range(len(c1)) for j in range(len(c2)) if i + j == 2}
    printed = {sp.expand(to_sympy(s)) for s in pc[0]}
    if printed == pairs and sum(sp.Poly(p, x).coeff_monomial(x**2) for p in pairs) == coef:
        ok(f"Q4c contributing products {sorted(map(str, printed))}")
    else:
        fail(f"Q4c products printed {printed}, recomputed {pairs}")

# ---------------- Q5: arrangements of AAABB ----------------
q5 = qblock(rev, 5)
b = ans["5"]
word = re.findall(r"letters \\\(([A-Z]+)\\\)", part(q5, "a"))
if len(word) != 1:
    fail("Q5 given word not found")
    sys.exit(1)
word = word[0]
arr = len(set(permutations(word)))
cnt = sorted(word.count(c) for c in set(word))                       # [2, 3] for AAABB
nn, rr = len(word), cnt[0]
check("Q5a", b, r"\(\dfrac{@!}{@!\,@!}=\dfrac{@}{@}=@\)",
      [nn, cnt[1], cnt[0], factorial(nn), factorial(cnt[0]) * factorial(cnt[1]), arr])
check("Q5b", b, r"\(@={}^@C_@\)", [arr, nn, rr])
subsets = sum(1 for _ in combinations(range(nn), rr))               # positions of the two Bs
if subsets == arr == comb(nn, rr):
    ok(f"Q5b brute force: {arr} arrangements = {subsets} position subsets = comb({nn},{rr})")
else:
    fail("Q5b counts differ")
check("Q5b other", b, r"gives \({}^@C_@\), which is also @", [nn, nn - rr, comb(nn, nn - rr)])

print(f"\n{checked} printed values checked, {fails} failures")
sys.exit(1 if fails else 0)
