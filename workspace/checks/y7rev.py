"""Check of the Year 7 revision practice pack (workspace/build/y7rev).

What it checks (exit status 1 if anything fails):
  1. Every answer printed in a_*.html is read from its <span data-k="KEY"> (each key must occur exactly
     once; a missing or unexpected key is a FAIL) and compared with an INDEPENDENT computation:
       * arithmetic parts: the expression is read from the QUESTION html (q_*.html, the part with that
         question number and part letter), turned into exact Python (fractions.Fraction, standard
         order of operations) and evaluated; the printed answer must equal it;
       * word problems: recomputed here from the question data with Fraction arithmetic;
       * puzzles (missing digits, sign boxes, brackets): every possibility is enumerated by brute force;
       * algebra: sympy (expand / simplify / solve);
       * probability: the sample space is enumerated and counted.
  2. The printed answers are compared with the ICE-EM answer key (a known key slip is noted, not failed).
  3. Each answer block has the same number and source label as its question.
  4. The cover: the minutes add up, and the core list for each section matches the stars in the questions.

Run: python3 workspace/checks/y7rev.py
"""
import itertools
import math
import os
import re
import sys
from fractions import Fraction as F

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y7REV_SRC", os.path.join(HERE, "..", "build", "y7rev"))
SECTIONS = [s for s in "abcdefghi" if os.path.exists(os.path.join(SRC, f"q_{s}.html"))]
FAILS, NOTES = [], []
N = [0]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def report(ok, label, detail=""):
    N[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label + ("  " + detail if detail else ""))
    if not ok:
        FAILS.append(label)


# ------------------------------------------------------------------ printed answers
ANS_HTML = "".join(read(f"a_{s}.html") for s in SECTIONS)
PRINTED = {}
for m in re.finditer(r'<span data-k="([^"]+)">(.*?)</span>', ANS_HTML, flags=re.S):
    k = m.group(1)
    if k in PRINTED:
        report(False, "duplicate key " + k)
    PRINTED[k] = m.group(2)


def clean(t):
    """HTML + MathJax source -> plain text with ASCII operators."""
    t = re.sub(r"<sup>(\d+)</sup>", r"^\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("&#8201;", " ").replace("&thinsp;", " ").replace("&nbsp;", " ").replace("&ensp;", " ")
    t = t.replace("\\(", "").replace("\\)", "").replace("\\,", "").replace("\\;", " ")
    t = t.replace("\\left", "").replace("\\right", "").replace("\\$", "$").replace("^\\circ", "°")
    t = t.replace("−", "-").replace("\\times", "*").replace("\\div", "/").replace("\\dots", "...")
    t = t.replace("\\cdots", "...").replace("\\%", "%")
    return t.strip()


def frac_tex(t):
    """\\tfrac{a}{b}, \\dfrac{..}{..}, \\frac{..}{..} and mixed numerals -> bracketed Python."""
    pat = re.compile(r"\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}")
    while True:
        t2 = re.sub(r"(\d+)\s*\\[dt]?frac\s*\{(\d+)\}\s*\{(\d+)\}", r"(\1+(\2)/(\3))", t)   # mixed numeral
        t2 = pat.sub(r"((\1)/(\2))", t2)
        if t2 == t:
            return t
        t = t2


def to_py(t):
    """Arithmetic LaTeX -> Python source with every number wrapped as Fraction."""
    t = clean(t)
    t = frac_tex(t)
    t = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", t)
    t = re.sub(r"\^(\d)", r"**\1", t)
    t = t.replace("{", "(").replace("}", ")")
    t = re.sub(r"(\d)\s+(\d)", r"\1\2", t)                         # thin-space digit groups
    t = re.sub(r"(\d+(?:\.\d+)?)", r"F('\1')", t)
    return t


def ev(t):
    src = to_py(t)
    if re.search(r"[A-Za-z_]", re.sub(r"F\('[\d.]+'\)", "", src)):
        raise ValueError("not arithmetic: " + src)
    return eval(src, {"F": F, "__builtins__": {}})


def recurring(t):
    """0.\\dot{4}2857\\dot{1} or 0.58\\dot{3} -> Fraction."""
    t = clean(t).replace(" ", "")
    neg = t.startswith("-")
    t = t.lstrip("-")
    m = re.fullmatch(r"(\d+)\.((?:\d|\\dot\{\d\})+)", t)
    if not m or "\\dot" not in t:
        return None
    whole, dec = m.group(1), m.group(2)
    digits = re.findall(r"\\dot\{(\d)\}|(\d)", dec)
    seq = [(a or b, bool(a)) for a, b in digits]
    dots = [i for i, (_, d) in enumerate(seq) if d]
    i0, i1 = dots[0], dots[-1]
    pre = "".join(c for c, _ in seq[:i0])
    rep = "".join(c for c, _ in seq[i0:i1 + 1])
    val = F(int(whole)) + (F(int(pre)) / 10 ** len(pre) if pre else 0)
    val += F(int(rep), (10 ** len(rep) - 1) * 10 ** len(pre))
    return -val if neg else val


def num(t):
    """Printed number (integer, decimal, fraction, mixed numeral, recurring decimal, money, percentage,
    with an optional unit) -> Fraction.  Returns None if it cannot be read."""
    r = recurring(t)
    if r is not None:
        return r
    c = clean(t)
    c = re.sub(r"(\d)\s+(\d)", r"\1\2", c)
    c = re.sub(r"(\d)\s+(\d)", r"\1\2", c)
    c = c.replace("$", "")
    c = re.sub(r"^[a-z]\s*=\s*", "", c)
    c = re.sub(r"\s*(%|°C|°|hours?|minutes?|months|seconds|pages|boxes|zeros|square units|cm|mm|km|kg|mL|m|g|L)\s*$", "", c)
    c = c.replace("%", "").strip()
    try:
        return ev(c)
    except Exception:
        return None


# ------------------------------------------------------------------ question parts
Q = {s: read(f"q_{s}.html") for s in SECTIONS}


def qblock(sec, n):
    """The html of question n in section sec."""
    m = re.search(r'<span class="q-num">%d</span><div class="q-body">(.*?)(?=<div class="q"><span class="q-num">|\Z)' % n,
                  Q[sec], flags=re.S)
    if not m:
        raise KeyError(f"question {sec.upper()}{n} not found")
    return m.group(1)


def qpart(sec, n, letter):
    """Math of part `letter` of question n (the first \\( ... \\) after the part label)."""
    b = qblock(sec, n)
    m = re.search(r'<span class="pl(?: ll)?">%s</span>(.*?)</span>' % re.escape(letter), b, flags=re.S)
    if not m:
        raise KeyError(f"part {sec.upper()}{n}{letter} not found")
    body = m.group(1)
    mm = re.findall(r"\\\((.*?)\\\)", body, flags=re.S)
    return " ".join(mm) if mm else body


def qpart_raw(sec, n, letter):
    """Whole html of part `letter` of question n."""
    b = qblock(sec, n)
    m = re.search(r'<span class="pl(?: ll)?">%s</span>(.*?)</span>(?=<span>|</div>)' % re.escape(letter), b, flags=re.S)
    if not m:
        raise KeyError(f"part {sec.upper()}{n}{letter} not found")
    return m.group(1)


def got(key):
    if key not in PRINTED:
        report(False, key, "MISSING printed answer")
        return None
    return PRINTED[key]


USED = set()


def check_num(key, want, label=""):
    USED.add(key)
    if isinstance(want, sp.Basic):
        want = F(str(sp.nsimplify(want)))
    t = got(key)
    if t is None:
        return
    v = num(t)
    report(v is not None and v == F(want), key + (" " + label if label else ""),
           f"printed {clean(t)!r} = {v}, computed {F(want)}")


def check_part(key, sec, n, letter):
    """Arithmetic part: evaluate the QUESTION expression and compare with the printed answer."""
    try:
        want = ev(qpart(sec, n, letter))
    except Exception as e:
        report(False, key, f"cannot evaluate question part: {e}")
        USED.add(key)
        return
    check_num(key, want, f"[{qpart(sec, n, letter)[:40]}]")


def check_true(key, ok, detail=""):
    USED.add(key)
    got(key)
    report(ok, key, detail)


def prime_powers(t):
    """'2^5 * 3^5' -> {2: 5, 3: 5}  (bases and exponents as printed)."""
    c = clean(t).replace(" ", "")
    out = {}
    for f in c.split("*"):
        m = re.fullmatch(r"(\d+)(?:\^\{?(\d+)\}?)?", f)
        if not m:
            return None
        b, e = int(m.group(1)), int(m.group(2) or 1)
        out[b] = out.get(b, 0) + e
    return out


def isprime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))


def check_factorisation(key, n):
    USED.add(key)
    pp = prime_powers(got(key) or "")
    ok = pp is not None and all(isprime(b) for b in pp) and math.prod(b ** e for b, e in pp.items()) == n
    report(ok, key, f"printed {clean(got(key) or '')!r}, number {n}")


# expected = dict filled by the sections below; BOOK = ICE-EM answer key values
BOOK = {}

# ================================================================== A Operations with numbers
if "a" in SECTIONS:
    for p in "adfi":
        check_part("A1" + p, "a", 1, p)
    BOOK.update(A1a=5, A1d=23, A1f=440, A1i=246)
    for p in "ab":
        check_part("A2" + p, "a", 2, p)
    check_part("A3h", "a", 3, "h")
    BOOK.update(A3h=412158)
    # A4: printed mixed numeral must equal the quotient, with proper fraction part in simplest form
    for p in "ab":
        key = "A4" + p
        USED.add(key)
        t = clean(got(key) or "")
        m = re.fullmatch(r"(\d+)\\tfrac\{(\d+)\}\{(\d+)\}", t.replace(" ", ""))
        want = ev(qpart("a", 4, p))
        ok = bool(m) and int(m.group(1)) + F(int(m.group(2)), int(m.group(3))) == want \
            and math.gcd(int(m.group(2)), int(m.group(3))) == 1 and int(m.group(2)) < int(m.group(3))
        report(ok, key, f"printed {t!r}, quotient {want}")
    for p in "abde":
        check_part("A5" + p, "a", 5, p)
    BOOK.update(A5a=4000, A5b=2970, A5d=84, A5e=3303)
    divs = [d for d in (2, 3, 4, 5, 6, 8, 9, 10) if 584760 % d == 0]
    pr = [int(x) for x in re.findall(r"\d+", clean(got("A6") or ""))]
    check_true("A6", pr == divs, f"printed {pr}, computed {divs}")
    check_num("A7h", math.gcd(224, 336))
    check_num("A7l", 224 * 336 // math.gcd(224, 336))
    BOOK.update(A7h=112, A7l=672)
    check_num("A8", 15 * 18 // math.gcd(15, 18))
    sol = [(s, t) for s in range(1, 10) for t in range(10) if (s * 10000 + 7250 + t) % 72 == 0]
    report(len(sol) == 1, "A9 unique solution", str(sol))
    check_num("A9s", sol[0][0])
    check_num("A9t", sol[0][1])
    BOOK.update(A9s=7, A9t=6)

# ================================================================== B Computation with integers
if "b" in SECTIONS:
    for p in "cfjl":
        check_part("B1" + p, "b", 1, p)
    BOOK.update(B1c=14, B1f=9, B1j=44, B1l=1550)
    check_num("B2a", 22 - (-3))
    check_num("B2b", -3 - 22)
    BOOK.update(B2a=25, B2b=-25)
    for p in "adfi":
        check_part("B3" + p, "b", 3, p)
    BOOK.update(B3a=36, B3d=6300, B3f=-204, B3i=-6)
    # B4: enumerate the 8 ways to fill the boxes (left to right, as written)
    for p, (nums4, target) in (("a", ((8, 4, -2, 3), -12)), ("b", ((3, 4, -5, 6), -10))):
        sols = []
        for ops in itertools.product("*/", repeat=3):
            v = F(nums4[0])
            for o, x in zip(ops, nums4[1:]):
                v = v * x if o == "*" else v / x
            if v == target:
                sols.append(ops)
        t = clean(got("B4" + p) or "")
        lhs, rhs = t.split("=")
        pr_ops = tuple(re.findall(r"[*/]", lhs))
        pr_nums = tuple(int(x) for x in re.findall(r"-?\d+", lhs.replace("(", " ").replace(")", " ")))
        check_true("B4" + p, pr_nums == nums4 and pr_ops in sols and ev(lhs) == F(rhs) == target,
                   f"printed {t!r}, solutions {sols}")
    for p in "bdfh":
        check_part("B5" + p, "b", 5, p)
    BOOK.update(B5b=-2, B5d=-1, B5f=-29, B5h=15)
    prof = {"a": 120 * (5 - 2) - 500, "b": 120 * (8 - 2) - 500, "c": 60 * (5 - 2) + 60 * (8 - 2) - 500}
    for p, v in prof.items():
        t = clean(got("B6" + p) or "")
        mm = re.match(r"\$(\d+)\s+(loss|profit)", t)
        ok = bool(mm) and (int(mm.group(1)) if mm.group(2) == "profit" else -int(mm.group(1))) == v
        check_true("B6" + p, ok, f"printed {t!r}, computed {v}")
    for p, target in (("a", -1), ("b", 9), ("c", -13)):
        sols = [s for s in itertools.permutations((4, -2, -7)) if s[0] + s[1] - s[2] == target]
        t = clean(got("B7" + p) or "")
        lhs, rhs = t.split("=")
        mm = re.fullmatch(r"\(?(-?\d+)\)?\+\(?(-?\d+)\)?-\(?(-?\d+)\)?", lhs.replace(" ", ""))
        pr = tuple(int(v) for v in mm.groups()) if mm else None
        check_true("B7" + p, pr in sols and ev(lhs) == target == F(rhs), f"printed {t!r}, solutions {sols}")
    seq = []
    for k, n in enumerate(range(100, 0, -1)):
        seq.append(n if k % 4 in (0, 1) else -n)
    check_num("B8", sum(seq))
    check_num("B9", 5 * 2 - 4 * 4)
    BOOK.update(B8=100, B9=-6)

# ================================================================== C Indices
if "c" in SECTIONS:
    for p, n in (("c", 2 * 2 * 2 * 2 ** 2 * 3 * 3 * 3 ** 3), ("f", 3 ** 2 * 7 ** 2 * 3 * 7 ** 3)):
        key = "C1" + p
        USED.add(key)
        pp = prime_powers(got(key) or "")
        qv = ev(qpart("c", 1, p))
        ok = pp is not None and len(pp) == 2 and math.prod(b ** e for b, e in pp.items()) == n == qv
        report(ok, key, f"printed {clean(got(key) or '')!r}")
    for p in "cdfg":
        check_part("C2" + p, "c", 2, p)
    BOOK.update(C2c=100, C2d=400, C2f=64, C2g=600000)
    for p in "abdf":
        tex = clean(qpart("c", 3, p)).replace("\\square", "x").replace("{", "(").replace("}", ")")
        lhs, rhs = tex.split("=")
        x = sp.Symbol("x")
        e = sp.sympify(lhs.replace("^", "**")) - sp.sympify(rhs.replace("^", "**"))
        sol = [s for s in range(0, 20) if e.subs(x, s) == 0]
        check_num("C3" + p, sol[0] if len(sol) == 1 else -999)
    BOOK.update(C3a=5, C3b=9, C3d=1, C3f=3)
    for p, n in (("c", 36), ("d", 96), ("f", 841)):
        check_factorisation("C4" + p, n)
    for p, n in (("g", 625), ("i", 1444), ("j", 5625)):
        r = math.isqrt(n)
        report(r * r == n, f"C5{p} perfect square")
        check_num("C5" + p, r)
    BOOK.update(C5g=25, C5i=38, C5j=75)
    for p in "abdg":
        check_part("C6" + p, "c", 6, p)
    BOOK.update(C6a=64, C6b=-121, C6d=-81, C6g=-125)
    for p in "cgh":
        check_part("C7" + p, "c", 7, p)
    BOOK.update(C7c=-256, C7g=-108, C7h=-7)
    for p in "cf":
        check_part("C8" + p, "c", 8, p)
    BOOK.update(C8c=F("-0.091"), C8f=F("-0.0064"))

    def zeros(n):
        s = str(n)
        return len(s) - len(s.rstrip("0"))
    for p, n in (("d", 2 ** 3 * 5 ** 4), ("f", 2 ** 21 * 5 ** 20), ("g", 2 ** 23 * 5 ** 20)):
        check_num("C9" + p, zeros(n))
    BOOK.update(C9d=3, C9f=20, C9g=20)

    def nfactors(n):
        return len(sp.divisors(n))
    check_num("C10a", nfactors(2 ** 20))
    check_num("C10b", nfactors(3 ** 6))
    check_num("C10c", nfactors(2 ** 20 * 3 ** 6))
    BOOK.update(C10a=21, C10b=7, C10c=147)

# ================================================================== D Fractions, decimals and percentages
if "d" in SECTIONS:
    for p in "qrtu":
        check_part("D1" + p, "d", 1, p)
        t = clean(got("D1" + p) or "")
        mm = re.search(r"\\tfrac\{(\d+)\}\{(\d+)\}", t)
        if mm:
            report(math.gcd(int(mm.group(1)), int(mm.group(2))) == 1, f"D1{p} in simplest form")
    BOOK.update(D1q=7, D1r=F(3, 5), D1t=F(6, 13), D1u=F(3, 2))
    # D2: a fraction of a quantity, read from the question text "Find a/b of N"
    for p in "abc":
        mm = re.search(r"\\tfrac\{(\d+)\}\{(\d+)\}\\\) of (?:\\\(\\\$)?([\d ]+)", qpart_raw("d", 2, p))
        check_num("D2" + p, F(int(mm.group(1)), int(mm.group(2))) * int(mm.group(3).replace(" ", "")))
    BOOK.update(D2a=12, D2b=15, D2c=1400)
    for p in "ek":
        check_part("D3" + p, "d", 3, p)
    BOOK.update(D3e=F(7, 5), D3k=F(41, 30))
    for p in "acd":
        check_part("D4" + p, "d", 4, p)
    BOOK.update(D4a=F(8, 5), D4c=F(37, 2), D4d=F(11, 3))
    for p in "ejo":
        check_part("D5" + p, "d", 5, p)
    BOOK.update(D5e=F(23, 18), D5j=F(19, 24), D5o=F(23, 210))
    for p in "abdf":
        check_part("D6" + p, "d", 6, p)
        report(recurring(got("D6" + p) or "") is not None, f"D6{p} printed as a recurring decimal")
    BOOK.update(D6a=F(3, 7), D6b=F(2, 11), D6d=F(6, 13), D6f=F(7, 12))
    for p in "fik":
        check_part("D7" + p, "d", 7, p)
    BOOK.update(D7f=F("-17.27"), D7i=F("26.4"), D7k=F("-1.5"))
    check_num("D8e", F(23, 50) * 100)
    check_num("D8i", F(1250, 2000) * 100)
    check_num("D8l", F("34.20") / 60 * 100)
    BOOK.update(D8e=46, D8i=F("62.5"), D8l=57)
    # D9: x% of a quantity, read from the question text "x% of N"
    for p in "dgj":
        mm = re.search(r"([\d.]+)% of ([\d.]+)", qpart_raw("d", 9, p))
        check_num("D9" + p, F(mm.group(1)) / 100 * F(mm.group(2)))
    BOOK.update(D9d=18, D9g=F("73.2"), D9j=236)
    x = sp.Symbol("x")
    check_num("D10", sp.solve(sp.Eq((x - 24) * sp.Rational(80, 100), sp.Rational(2, 3) * x), x)[0])
    BOOK.update(D10=144)
    L, W = sp.symbols("L W", positive=True)
    pct = int(re.search(r"length decreased by (\d+)%", qblock("d", 11)).group(1))
    k = sp.solve(sp.Eq(sp.Rational(100 - pct, 100) * L * W * (1 + x / 100), L * W), x)[0]
    check_num("D11", k)

# ------------------------------------------------------------------ algebra helpers (sympy)
LETTERS = {c: sp.Symbol(c) for c in "abcdefghjkmnpqrstuvwxyz"}


def alg(t):
    """Printed or question LaTeX -> sympy expression (implicit multiplication made explicit)."""
    t = clean(t).replace("$", "")
    t = frac_tex(t)
    t = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", t)
    t = re.sub(r"\^(\d)", r"**\1", t)
    t = t.replace("{", "(").replace("}", ")").replace(" ", "")
    for _ in range(3):
        t = re.sub(r"(\d|\))(?=[a-z(])", r"\1*", t)
        t = re.sub(r"([a-z])(?=[a-z(\d])", r"\1*", t)
    return sp.sympify(t, locals=LETTERS)


def nterms(e):
    return len(sp.Add.make_args(sp.expand(e)))


def raw_terms(t):
    """Number of terms as PRINTED (top-level + and - signs, outside brackets)."""
    c = clean(t).replace(" ", "")
    depth, n = 0, 1
    for i, ch in enumerate(c):
        depth += ch in "({"
        depth -= ch in ")}"
        if ch in "+-" and depth == 0 and i > 0 and c[i - 1] not in "^*/(":
            n += 1
    return n


def check_simplify(key, sec, n, letter):
    """Printed simplification must equal the question expression and be fully collected."""
    USED.add(key)
    q = alg(qpart(sec, n, letter))
    p = alg(got(key) or "0")
    ok = sp.expand(q - p) == 0 and raw_terms(got(key) or "0") == nterms(q)
    report(ok, key, f"question {sp.expand(q)}, printed {p}")


def check_expr(key, want):
    USED.add(key)
    p = alg(got(key) or "0")
    report(sp.simplify(p - want) == 0, key, f"printed {p}, want {want}")


def check_eq(key, sec, n, letter):
    """Solve the question equation with sympy; printed 'x = value' must match."""
    USED.add(key)
    lhs, rhs = clean(qpart(sec, n, letter)).split("=")
    eq = alg(lhs) - alg(rhs)
    var = list(eq.free_symbols)
    sol = sp.solve(eq, var[0])
    t = clean(got(key) or "")
    pv, pval = t.split("=")
    v = num(pval)
    ok = len(var) == 1 and pv.strip() == str(var[0]) and len(sol) == 1 and v is not None and F(str(sol[0])) == v
    report(ok, key, f"solution {var[0]} = {sol}, printed {t!r}")


def nums_list(t):
    """'12.2, 12.1, ...' or '3\\tfrac12,\\ 2\\tfrac12' -> list of Fractions."""
    c = clean(t).replace("\\ ", " ")
    return [num(x) for x in c.split(",")]


import json
FIG = json.load(open(os.path.join(SRC, "svg", "figdata.json"))) if os.path.exists(os.path.join(SRC, "svg", "figdata.json")) else {}

# ================================================================== E Algebraic techniques
if "e" in SECTIONS:
    for p in "acd":
        check_simplify("E1" + p, "e", 1, p)
    for p in "abf":
        check_simplify("E2" + p, "e", 2, p)
    for p in "ab":
        check_simplify("E3" + p, "e", 3, p)
    for p in "fgh":
        check_simplify("E4" + p, "e", 4, p)
    for p in "ab":
        check_simplify("E5" + p, "e", 5, p)
    x = LETTERS["x"]
    # E6: the expressions built here from the words of the question
    check_expr("E6d", (5 * x - 2) / 5)
    check_expr("E6j", 4 * (sp.Rational(2, 5) * x - 3))
    check_expr("E6k", sp.Rational(3, 7) * (23 - sp.Rational(4, 9) * x))
    check_expr("E7ai", 1000 - x)
    check_expr("E7aii", 1000 - 5 * x)
    for key, xv in (("E7bi", 100), ("E7bii", 200), ("E7biii", 250)):
        check_num(key, 1000 - 5 * xv)
    m, n_ = LETTERS["m"], LETTERS["n"]
    for p in "acd":
        check_num("E8" + p, alg(qpart("e", 8, p)).subs({m: 6, n_: sp.Rational(1, 2)}))
    w = LETTERS["w"]
    for p in "def":
        check_num("E9" + p, alg(qpart("e", 9, p)).subs(w, -2))
    bc = 16 / x
    per = 2 * (x + bc)
    check_expr("E10a", bc)
    check_expr("E10b", per)
    check_num("E10c", per.subs(x, 4))
    check_num("E10d", per.subs(x, sp.Rational(1, 4)))
    BOOK.update(E7bi=500, E7bii=0, E7biii=-250, E8a=66, E8c=F(25, 4), E8d=34, E9d=64, E9e=12, E9f=-48,
                E10c=16, E10d=F(257, 2))

# ================================================================== F Equations
if "f" in SECTIONS:
    for (q, parts) in ((1, "djl"), (2, "ekp"), (3, "ab"), (4, "ghi"), (5, "df"), (6, "bd")):
        for p in parts:
            check_eq(f"F{q}{p}", "f", q, p)
    x = LETTERS["x"]
    check_expr("F7a", 4 * (3 * x + 2))
    check_num("F7b", sp.solve(sp.Eq(4 * (3 * x + 2), 50), x)[0])
    b = sp.Symbol("b")
    bb = sp.solve(sp.Eq(b + (b + 16) + (b + 16 + 8), 400), b)[0]
    check_num("F8b", bb)
    check_num("F8j", bb + 16)
    check_num("F8d", bb + 24)
    r = sp.Symbol("r")
    check_num("F9", sp.solve(sp.Eq(r - 12, 2 * ((60 - r) + 12)), r)[0])
    A, B, C = sp.symbols("A B C")
    sol = sp.solve([A + B - 27, B + C - 33, A + C - 30], [A, B, C])
    check_num("F10a", sol[A])
    check_num("F10b", sol[B])
    check_num("F10c", sol[C])
    BOOK.update(F1d=3, F1j=204, F1l=84, F2e=F(48, 5), F2k=-20, F2p=F(14, 5), F4g=F(16, 3), F4h=F(-9, 4), F4i=11,
                F5d=9, F5f=F(81, 28), F6b=20, F6d=5, F8b=120, F8j=136, F8d=144, F9=52)

# ================================================================== G Linear relationships
if "g" in SECTIONS:
    for p in "cd":
        given = [F(v) for v in re.findall(r"\d+\.\d", qpart("g", 1, p))]
        dlt = given[1] - given[0]
        report(given[2] - given[1] == dlt, f"G1{p} pattern has a common difference")
        want = [given[-1] + dlt * k for k in range(1, 6)]
        USED.add("G1" + p)
        report(nums_list(got("G1" + p) or "") == want, "G1" + p, f"want {[float(v) for v in want]}")
    pts = re.findall(r"([A-G])\((-?\d+),\s*(-?\d+)\)", clean(got("G2") or ""))
    pr = [(int(a), int(b)) for _, a, b in pts]
    check_true("G2", [l for l, _, _ in pts] == list("ABCDEFG") and pr == [tuple(v) for v in FIG.get("g_coords", [])],
               f"printed {pr}")
    # G3: which plotted sets are linear? (points read from the figure data; collinear by cross products)
    def collinear(pts):
        (x0_, y0_), (x1_, y1_) = pts[0], pts[1]
        return all((x1_ - x0_) * (y - y0_) == (y1_ - y0_) * (x - x0_) for x, y in pts[2:])
    lin = [k for k in "PQR" if collinear(FIG.get("g_lin" + k, [(0, 0), (1, 1), (0, 1)]))]
    report(len(lin) == 2, "G3 two of the three sets are linear", str(lin))
    check_true("G3", re.findall(r"\b[PQR]\b", clean(got("G3") or "")) == lin, f"linear sets {lin}")
    rule = lambda xv: -xv + F(1, 2)
    want = [rule(xv) for xv in range(-3, 4)]
    check_true("G4", nums_list(got("G4") or "") == want, f"want {want}")
    report([tuple(map(F, map(str, p))) for p in FIG.get("g_ans12c", [])] == [(F(xv), rule(xv)) for xv in range(-3, 4)],
           "G4 answer graph points")
    counts = [FIG.get(f"g_tri{k}") for k in range(1, 5)]          # matches counted in the drawn diagrams
    report(counts[:3] == [3, 5, 7], "G5 figure matches the table (3, 5, 7)", str(counts))
    t = sp.Symbol("t")
    slope = counts[1] - counts[0]
    report(all(counts[k + 1] - counts[k] == slope for k in range(3)), "G5 figure grows by a constant")
    rule4 = slope * t + (counts[0] - slope)
    check_true("G5a", [int(v) for v in re.findall(r"\d+", clean(got("G5a") or ""))] == [int(rule4.subs(t, k)) for k in (4, 5, 6)])
    check_num("G5b", slope)
    tt = clean(got("G5d") or "").split("=")
    check_true("G5d", tt[0].strip() == "m" and sp.expand(alg(tt[1]) - rule4) == 0, f"rule {rule4}")
    qb = qblock("g", 6)
    tables = re.findall(r'<table class="ct sm">(.*?)</table>', qb, flags=re.S)
    for p, tab in zip("cdf", tables):
        rows = re.findall(r"<tr><th>\\\((\w)\\\)</th>(.*?)</tr>", tab, flags=re.S)
        (v1, r1), (v2, r2) = rows
        xs = [num(c) for c in re.findall(r"<td>(.*?)</td>", r1)]
        ys = [num(c) for c in re.findall(r"<td>(.*?)</td>", r2)]
        tt = clean(got("G6" + p) or "").split("=")
        e = alg(tt[1])
        sym = LETTERS[v1]
        mm = re.fullmatch(r"(-?\d+)\*" + v1 + r"-(\d+)", tt[1].replace(" ", ""))
        ok = tt[0].strip() == v2 and bool(mm) and all(e.subs(sym, xv) == yv for xv, yv in zip(xs, ys))
        check_true("G6" + p, ok, f"printed {tt}, table {xs} -> {ys}")
    listed = [alg(r) for r in re.findall(r"\\\(y=([^\\]*)\\\)", qblock("g", 7))]
    report(len(listed) == 6, "G7 six rules listed")
    xs_ = LETTERS["x"]
    for p in "acf":
        tt = clean(got("G7" + p) or "").split("=")
        e = alg(tt[1])
        pts = FIG.get("g8" + p, [])
        fits = [rr for rr in listed if all(rr.subs(xs_, a) == b_ for a, b_ in pts)]
        check_true("G7" + p, len(fits) == 1 and sp.expand(e - fits[0]) == 0 and len(pts) > 3, f"fits {fits}")
    mo = sp.Symbol("m")
    d_rule = 1000 - 20 * mo
    check_true("G8a", [int(v) for v in re.findall(r"\d+", clean(got("G8a") or ""))] == [int(d_rule.subs(mo, k)) for k in range(2, 7)])
    tt = clean(got("G8b") or "").split("=")
    check_true("G8b", tt[0].strip() == "d" and sp.expand(alg(tt[1]) - d_rule) == 0)
    check_num("G8c", d_rule.subs(mo, 10))
    check_num("G8d", sp.solve(d_rule, mo)[0])
    c_ = sp.Symbol("c")
    cval = sp.solve(sp.Eq(2, 2 * 3 + c_), c_)[0]
    check_true("G9a", clean(got("G9a") or "").replace(" ", "") == f"c={cval}", str(cval))
    xi = sp.solve(2 * xs_ + cval, xs_)[0]
    check_true("G9bx", re.sub(r"\s", "", clean(got("G9bx") or "")) == f"({xi},0)")
    check_true("G9by", re.sub(r"\s", "", clean(got("G9by") or "")) == f"(0,{cval})")
    check_num("G9c", F(1, 2) * abs(xi) * abs(cval))
    BOOK.update(G5b=2, G8c=800, G8d=50)

# ================================================================== H Probability (enumeration)
if "h" in SECTIONS:
    def P(space, event):
        return F(sum(1 for o in space if event(o)), len(space))
    discs = ["R"] * 3 + ["B"] * 3
    check_num("H1cr", P(discs, lambda o: o == "R"))
    check_num("H1cb", P(discs, lambda o: o == "B"))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    check_num("H1d", P(["Fri"], lambda o: o == days[days.index("Thu") + 1]))     # the only possible tomorrow
    check_num("H1e", P(["1 Feb"], lambda o: o == "1 May"))
    marbles = list(range(1, 11))
    check_true("H2a", [int(v) for v in re.findall(r"\d+", clean(got("H2a") or ""))] == marbles)
    check_true("H2b", [int(v) for v in re.findall(r"\d+", clean(got("H2b") or ""))] == [m_ for m_ in marbles if m_ % 2])
    sweets = ["red"] * 10 + ["green"] * 9 + ["yellow"] * 6 + ["blue"] * 5
    check_num("H3b", P(sweets, lambda o: o in ("green", "yellow")))
    check_num("H3c", P(sweets, lambda o: o != "red"))
    check_num("H3e", P(sweets, lambda o: o not in ("yellow", "blue")))
    cards = list(range(1, 21))
    check_num("H4a", P(cards, lambda c: c % 2 == 1 and c % 3 == 0))
    check_num("H4b", P(cards, lambda c: c % 2 == 1 or c % 3 == 0))
    check_num("H4c", P(cards, lambda c: c >= 15))
    beans = [("G", "N")] * 250 + [("R", "N")] * 400 + [("G", "D")] * 175 + [("R", "D")] * 75
    check_num("H5a", P(beans, lambda o: o[1] == "D"))
    check_num("H5b", P(beans, lambda o: o[0] == "G"))
    check_num("H5c", P(beans, lambda o: o == ("G", "N")))
    check_num("H5d", P(beans, lambda o: o == ("R", "D")))
    check_num("H5e", P(beans, lambda o: o[0] == "R"))
    hv = FIG.get("h_venn", {})                                                       # counts drawn in the Venn figure
    venn = [(1, 0)] * hv.get("T only", 0) + [(1, 1)] * hv.get("both", 0) + [(0, 1)] * hv.get("S only", 0) + [(0, 0)] * hv.get("neither", 0)  # (tennis, swims)
    report(len(venn) == 60, "H6 Venn diagram holds 60 students")
    cnt = lambda f: sum(1 for v in venn if f(v))
    cells = {"ts": cnt(lambda v: v == (1, 1)), "tn": cnt(lambda v: v == (1, 0)), "tt": cnt(lambda v: v[0] == 1),
             "ns": cnt(lambda v: v == (0, 1)), "nn": cnt(lambda v: v == (0, 0)), "nt": cnt(lambda v: v[0] == 0),
             "as": cnt(lambda v: v[1] == 1), "an": cnt(lambda v: v[1] == 0), "at": len(venn)}
    for k_, v in cells.items():
        check_num("H6_" + k_, v)
    check_num("H6bi", P(venn, lambda v: v == (0, 1)))
    check_num("H6bii", P(venn, lambda v: v == (0, 0)))
    added = next(k for k in range(1, 200) if P(venn + [(1, 0)] * k, lambda v: v[0] == 1) == F(1, 2))
    check_num("H6c", added)
    removed = [k for k in range(0, 16) if F(15 - k, 23 - k) == F(1, 3)]
    report(len(removed) == 1, "H7 unique number removed")
    check_num("H7", removed[0])
    tickets = list(range(1, 51))
    check_num("H8f", P(tickets, lambda n: "7" in str(n)))
    check_num("H8h", P(tickets, lambda n: "2" in str(n)))
    check_num("H8i", P(tickets, lambda n: str(n).count("2") == 1))
    check_num("H8j", P(tickets, lambda n: "2" not in str(n)))
    bl = sp.Symbol("b")
    bv = sp.solve(sp.Eq(sp.Rational(1, 3) + bl + bl + 2 * bl, 1), bl)[0]
    check_num("H9", 360 * 2 * bv)
    BOOK.update(H1cr=F(1, 2), H1cb=F(1, 2), H1d=1, H1e=0, H3b=F(1, 2), H3c=F(2, 3), H3e=F(19, 30), H5a=F(5, 18),
                H5b=F(17, 36), H5c=F(5, 18), H5d=F(1, 12), H5e=F(19, 36), H7=11, H8f=F(1, 10), H8h=F(7, 25),
                H8i=F(13, 50), H8j=F(18, 25))

# ================================================================== I Mixed challenge
if "i" in SECTIONS:
    for p in "abc":
        check_part("I1" + p, "i", 1, p)
    BOOK.update(I1a=22, I1b=24, I1c=23)
    for p in "ab":
        items = [x.strip() for x in clean(qpart("i", 2, p)).replace("\\ ", " ").split(",")]
        val = lambda s_: num(s_.replace("%", "")) / 100 if "%" in s_ else num(s_)
        pr = [x.strip() for x in clean(got("I2" + p) or "").replace("\\ ", " ").split(",")]
        prv = [val(x) for x in pr]
        check_true("I2" + p, sorted(prv) == prv and sorted(prv) == sorted(val(x) for x in items) and len(set(prv)) == 3,
                   f"printed {pr} = {[float(v) for v in prv]}")
    for p in "abc":
        check_part("I3" + p, "i", 3, p)
    BOOK.update(I3a=F(17, 2), I3b=F(1, 5), I3c=F(4, 3))
    check_num("I4", F(2, 3) * F(3, 4) * F(4, 5))
    gaps = [F(1), F(5, 4), F(6, 5), F(7, 6)]
    tbest = next(F(k, 60) for k in range(1, 100000) if all((F(k, 60) / g).denominator == 1 for g in gaps))
    check_num("I5", tbest)
    xx = LETTERS["x"]
    check_num("I6", sp.solve(sp.Eq(xx + 13, 4 - xx / 2), xx)[0])
    BOOK.update(I4=F(2, 5), I5=210, I6=-6)
    balls = [("red", k) for k in range(1, 9)] + [("blue", k) for k in range(9, 15)] + [("green", k) for k in range(15, 25)]
    prime = lambda k: k > 1 and all(k % d for d in range(2, k))
    P2 = lambda e: F(sum(1 for b_ in balls if e(b_)), len(balls))
    check_num("I7d", P2(lambda b_: b_[0] == "green" and b_[1] % 2))
    check_num("I7e", P2(lambda b_: b_[0] in ("green", "red")))
    check_num("I7g", P2(lambda b_: b_[1] % 5 == 0))
    check_num("I7h", P2(lambda b_: prime(b_[1])))
    BOOK.update(I7d=F(5, 24), I7e=F(3, 4), I7g=F(1, 6), I7h=F(3, 8))
    pairs = [(a_, b_) for a_ in range(1, 40) for b_ in range(1, 40) if (a_ + b_) % 2]
    stmts = {1: lambda a_, b_: max(a_, b_) % min(a_, b_) != 0,
             2: lambda a_, b_: (a_ * b_) % 2 == 0,
             3: lambda a_, b_: abs(a_ - b_) % 2 == 0,
             4: lambda a_, b_: a_ * b_ > a_ + b_,
             5: lambda a_, b_: ((a_ + 1) * b_) % 2 == 0}          # 1 added to the first number (either one)
    for k, f in stmts.items():
        vals = {f(a_, b_) for a_, b_ in pairs}
        verdict = "always true" if vals == {True} else "always false" if vals == {False} else "sometimes true and sometimes false"
        check_true(f"I8_{k}", clean(got(f"I8_{k}") or "") == verdict, verdict)

# ------------------------------------------------------------------ figures: every svg used exists, every svg is used
USEDSVG = set(re.findall(r"\{\{svg:([\w-]+)\}\}", "".join(Q.values()) + ANS_HTML))
HAVE = {f[:-4] for f in os.listdir(os.path.join(SRC, "svg")) if f.endswith(".svg")} if os.path.isdir(os.path.join(SRC, "svg")) else set()
report(USEDSVG <= HAVE, "every figure used exists", str(sorted(USEDSVG - HAVE)))
report(HAVE <= USEDSVG, "every figure drawn is used", str(sorted(HAVE - USEDSVG)))

# ------------------------------------------------------------------ cover: times and core sets
EST = {  # minutes per question (all questions), core question numbers
    "a": ([3, 2, 3, 3, 4, 3, 3, 3, 5], [1, 5, 6, 9]),
    "b": ([3, 2, 2, 3, 4, 4, 3, 3, 3], [1, 5, 6, 8]),
    "c": ([2, 3, 2, 3, 4, 2, 2, 3, 2, 4], [1, 4, 7, 9, 10]),
    "d": ([2, 2, 2, 3, 5, 4, 3, 3, 2, 4, 3], [5, 6, 10, 11]),
    "e": ([2, 2, 2, 3, 3, 3, 3, 3, 2, 4], [4, 5, 8, 10]),
    "f": ([2, 2, 2, 3, 3, 3, 2, 3, 3, 3], [1, 6, 8, 9, 10]),
    "g": ([2, 2, 2, 4, 4, 3, 2, 3, 4], [2, 5, 8, 9]),
    "h": ([2, 1, 2, 3, 3, 5, 3, 3, 3], [6, 7, 9]),
    "i": ([2, 2, 4, 2, 4, 3, 3, 4], [3, 6, 8]),
}
if os.path.exists(os.path.join(SRC, "cover.html")) and len(SECTIONS) == 9:
    COVER = read("cover.html")
    tot_all = tot_core = 0
    for sec_, (times, core) in EST.items():
        nq = len(re.findall(r'<span class="q-num">\d+</span>', Q[sec_]))
        a_ = sum(times)
        c_ = sum(times[k - 1] for k in core)
        tot_all += a_
        tot_core += c_
        report(len(times) == nq, f"{sec_.upper()} one time estimate per question", f"{nq} questions")
        stars = [int(k) for k in re.findall(r'<span class="q-num">(\d+)</span><div class="q-body"><span class="src">[^<]*</span><span class="star">', Q[sec_])]
        report(stars == core, f"{sec_.upper()} stars match the core list", str(stars))
        tl = re.search(r'<p class="tline">About (\d+) minutes\. Core: questions ([\d, and]+)\.</p>', Q[sec_])
        tl_core = [int(k) for k in re.findall(r"\d+", tl.group(2))] if tl else None
        report(bool(tl) and int(tl.group(1)) == a_ and tl_core == core, f"{sec_.upper()} timing line", tl.group(0) if tl else "missing")
        row = re.search(r"<tr><td>%s &nbsp;[^<]*</td><td>([\d, ]+)</td><td class=\"m\">(\d+) min</td><td class=\"m\">(\d+) min</td></tr>" % sec_.upper(), COVER)
        report(bool(row) and [int(k) for k in row.group(1).split(",")] == core and int(row.group(2)) == a_ and int(row.group(3)) == c_,
               f"{sec_.upper()} cover row", f"all {a_}, core {c_}")
        nwarm = sum(1 for k in range(1, nq + 1) if k not in core and times[k - 1] <= 2)
    mt = re.search(r"<td><b>Total</b></td><td></td><td class=\"m\">(\d+) h (\d+) min</td><td class=\"m\">(\d+) h (\d+) min</td>", COVER)
    report(bool(mt) and int(mt.group(1)) * 60 + int(mt.group(2)) == tot_all and int(mt.group(3)) * 60 + int(mt.group(4)) == tot_core,
           "cover totals", f"all {tot_all} min, core {tot_core} min")
    report(180 <= tot_all <= 245 and 110 <= tot_core <= 125, "about 3 to 4 hours in all, about 2 hours core")

# ------------------------------------------------------------------ every printed key was checked
for k in PRINTED:
    if k not in USED:
        report(False, "unchecked printed key " + k)

# ------------------------------------------------------------------ answer blocks match questions
for s in SECTIONS:
    qq = re.findall(r'<span class="q-num">(\d+)</span><div class="q-body"><span class="src">([^<]*)</span>', Q[s])
    aa = re.findall(r'<div class="a"><span class="an">(\d+)</span><div class="ab"[^>]*><span class="src">([^<]*)</span>', read(f"a_{s}.html"))
    report(qq == aa and [int(n) for n, _ in qq] == list(range(1, len(qq) + 1)),
           f"{s.upper()} answers match questions (number and source)", f"{len(qq)} questions")
    report(8 <= len(qq) <= 14, f"{s.upper()} has 8 to 14 questions")

# ------------------------------------------------------------------ textbook answer key
KNOWN_SLIPS = {}
for k, v in BOOK.items():
    g = num(PRINTED.get(k, ""))
    if g == F(v):
        report(True, "book key " + k)
    elif k in KNOWN_SLIPS:
        NOTES.append(k + ": " + KNOWN_SLIPS[k])
        print("NOTE     book key " + k + "  " + KNOWN_SLIPS[k])
    else:
        report(False, "book key " + k, f"printed {g}, book {v}")

print()
print(f"{N[0]} checks, {len(FAILS)} failures")
for n in NOTES:
    print("note:", n)
if FAILS:
    print("FAILED:", ", ".join(FAILS[:40]))
    sys.exit(1)
print("ALL OK")
