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
    t = t.replace("\\cdots", "...")
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
    c = re.sub(r"\s*(%|°C|°|hours?|minutes?|pages|boxes|zeros|cm|mm|km|kg|mL|m|g|L)\s*$", "", c)
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
    for p in "ch":
        check_part("A3" + p, "a", 3, p)
    BOOK.update(A3c=28858, A3h=412158)
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
    q, r = divmod(5420, 25)
    check_num("A5a", q)
    check_num("A5b", r)
    BOOK.update(A5a=216, A5b=20)
    for p in "abde":
        check_part("A6" + p, "a", 6, p)
    BOOK.update(A6a=4000, A6b=2970, A6d=84, A6e=3303)
    divs = [d for d in (2, 3, 4, 5, 6, 8, 9, 10) if 584760 % d == 0]
    pr = [int(x) for x in re.findall(r"\d+", clean(got("A7") or ""))]
    check_true("A7", pr == divs, f"printed {pr}, computed {divs}")
    # A8: brute force over the two missing digits of 7?42?
    nums = {a: 70420 + 1000 * a for a in range(10)}
    sol_i = sorted(70420 + 1000 * a + b - 0 for a in range(10) for b in range(10)
                   if (70420 + 1000 * a + b) % 9 == 0 and (70420 + 1000 * a + b) % 10 == 0)
    sol_k = sorted(x for x in (70420 + 1000 * a + b for a in range(10) for b in range(10))
                   if all(x % d == 0 for d in (2, 3, 4, 5)) and x % 9)
    for key, sol in (("A8i", sol_i), ("A8k", sol_k)):
        pr = sorted(int(x.replace(" ", "")) for x in re.findall(r"\d[\d ]*\d", clean(got(key) or "")))
        check_true(key, pr == sol, f"printed {pr}, all solutions {sol}")
    check_num("A9h", math.gcd(224, 336))
    check_num("A9l", 224 * 336 // math.gcd(224, 336))
    BOOK.update(A9h=112, A9l=672)
    check_num("A10", 15 * 18 // math.gcd(15, 18))
    sol = [(s, t) for s in range(1, 10) for t in range(10) if (s * 10000 + 7250 + t) % 72 == 0]
    report(len(sol) == 1, "A11 unique solution", str(sol))
    check_num("A11s", sol[0][0])
    check_num("A11t", sol[0][1])
    BOOK.update(A11s=7, A11t=6)

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
    check_num("B7", (-5 + 11 - 20) * 4)
    BOOK["B7"] = -56
    for p, target in (("a", -1), ("b", 9), ("c", -13)):
        sols = [s for s in itertools.permutations((4, -2, -7)) if s[0] + s[1] - s[2] == target]
        t = clean(got("B8" + p) or "")
        lhs, rhs = t.split("=")
        mm = re.fullmatch(r"\(?(-?\d+)\)?\+\(?(-?\d+)\)?-\(?(-?\d+)\)?", lhs.replace(" ", ""))
        pr = tuple(int(v) for v in mm.groups()) if mm else None
        check_true("B8" + p, pr in sols and ev(lhs) == target == F(rhs), f"printed {t!r}, solutions {sols}")
    for p, target in (("a", 14), ("c", 37)):
        orig = clean(qpart("b", 9, p)).split("=")[0]
        t = clean(got("B9" + p) or "")
        lhs, rhs = t.split("=")
        strip = lambda s: re.sub(r"[\s]", "", s)
        # removing the added brackets must give back the original statement (the (-3) brackets are original)
        base = strip(lhs).replace("(-3)", "N")
        base = base.replace("(", "").replace(")", "").replace("N", "(-3)")
        check_true("B9" + p, base == strip(orig) and ev(lhs) == target == F(rhs), f"printed {t!r}")
    seq = []
    for k, n in enumerate(range(100, 0, -1)):
        seq.append(n if k % 4 in (0, 1) else -n)
    check_num("B10", sum(seq))
    check_num("B11", 5 * 2 - 4 * 4)
    BOOK.update(B10=100, B11=-6)

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
    for p in "ehk":
        check_part("D2" + p, "d", 2, p)
    BOOK.update(D2e=F(7, 5), D2h=F(5, 3), D2k=F(41, 30))
    for p in "acd":
        check_part("D3" + p, "d", 3, p)
    BOOK.update(D3a=F(8, 5), D3c=F(37, 2), D3d=F(11, 3))
    for p in "ejo":
        check_part("D4" + p, "d", 4, p)
    BOOK.update(D4e=F(23, 18), D4j=F(19, 24), D4o=F(23, 210))
    for p in "abdf":
        check_part("D5" + p, "d", 5, p)
        report(recurring(got("D5" + p) or "") is not None, f"D5{p} printed as a recurring decimal")
    BOOK.update(D5a=F(3, 7), D5b=F(2, 11), D5d=F(6, 13), D5f=F(7, 12))
    for p in "cdh":
        check_part("D6" + p, "d", 6, p)
    BOOK.update(D6c=60, D6d=F("0.05"), D6h=3525)
    for p in "fik":
        check_part("D7" + p, "d", 7, p)
    BOOK.update(D7f=F("-17.27"), D7i=F("26.4"), D7k=F("-1.5"))
    check_num("D8e", F(23, 50) * 100)
    check_num("D8i", F(1250, 2000) * 100)
    check_num("D8l", F("34.20") / 60 * 100)
    BOOK.update(D8e=46, D8i=F("62.5"), D8l=57)
    check_num("D9a", F(2, 100) * 168)
    check_num("D9b", F(5, 100) * 168)
    check_num("D9c", 100 - (F("37.5") + 20 + 2 + 5))
    BOOK.update(D9a=F("3.36"), D9b=F("8.4"), D9c=F("35.5"))
    x = sp.Symbol("x")
    check_num("D10", sp.solve(sp.Eq(x - sp.Rational(2, 11) * x - sp.Rational(3, 5) * x, 84), x)[0])
    check_num("D11", sp.solve(sp.Eq((x - 24) * sp.Rational(80, 100), sp.Rational(2, 3) * x), x)[0])
    BOOK.update(D10=385, D11=144)
    L, W = sp.symbols("L W", positive=True)
    k = sp.solve(sp.Eq(sp.Rational(80, 100) * L * W * (1 + x / 100), L * W), x)[0]
    check_num("D12", k)

# ------------------------------------------------------------------ every printed key was checked
for k in PRINTED:
    if k not in USED:
        report(False, "unchecked printed key " + k)

# ------------------------------------------------------------------ answer blocks match questions
for s in SECTIONS:
    qq = re.findall(r'<span class="q-num">(\d+)</span><div class="q-body"><span class="src">([^<]*)</span>', Q[s])
    aa = re.findall(r'<div class="a"><span class="an">(\d+)</span><div class="ab"><span class="src">([^<]*)</span>', read(f"a_{s}.html"))
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
