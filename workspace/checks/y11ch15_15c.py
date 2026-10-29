"""Check of Lesson 15C (Y11 Ch 15 pack): The binomial theorem.

The script reads the values PRINTED in workspace/build/y11ch15/a_15c.html (lesson examples,
textbook homework, past-paper worked solutions) and in l15c.html (the 16-word expansion of
(x + y)^4, worked examples 9 and 10, the Concept 3 worked example, the results printed inside
textbook questions, the past-paper questions and options). Each value is found with a template
('@' marks the printed LaTeX); a template must match exactly once in its block, otherwise the
item FAILS. The printed LaTeX (including {}^nC_r, \\dbinom and n!) is converted to a sympy
expression and compared with an independent computation:
  - expansions are built by repeated multiplication (sympy expand of the product of n brackets),
    never from the binomial formula, and coefficients are read off them;
  - every printed nCr value is compared with a brute-force count of subsets (itertools);
  - results in terms of n are compared, for n = 4..12, with coefficients of the expanded power;
  - equations for n are solved by trying every whole number n = 0..60;
  - decimal and significant-figure approximations are recomputed with exact integers.
It also checks the lesson fragment: past-paper marks add to the intro total (15-22), time is
1.5 x marks rounded to 5 minutes, numbering and source labels match in both files, one hint per
question, and the MC letter is the one option equal to the computed value.

Exit status 1 if anything fails. Run: python3 workspace/checks/y11ch15_15c.py
"""
import itertools
import os
import re
import sys
from fractions import Fraction

import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH15_SRC", os.path.join(HERE, "..", "build", "y11ch15"))
FAILS = []
x, y, a, b, h, n, p, q, k, A, B = sp.symbols("x y a b h n p q k A B")
SYMS = {"x": x, "y": y, "a": a, "b": b, "h": h, "n": n, "p": p, "q": q, "k": k, "A": A, "B": B,
        "binomial": sp.binomial, "factorial": sp.factorial}
TR = standard_transformations + (implicit_multiplication_application,)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:110] + "  " + detail.replace("\n", " ")[:160])
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- independent counting
_PASCAL = [[1]]


def ncr(m, r):
    """Number of r-subsets of an m-set: brute-force enumeration for m <= 18, otherwise
    Pascal's triangle built by addition (rows checked against enumeration up to 18)."""
    if r < 0 or r > m:
        return 0
    if m <= 18:
        return sum(1 for _ in itertools.combinations(range(m), r))
    while len(_PASCAL) <= m:
        prev = _PASCAL[-1]
        _PASCAL.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return _PASCAL[m][r]


def power(base, e):
    """(base)^e by repeated multiplication."""
    res = sp.Integer(1)
    for _ in range(e):
        res = sp.expand(res * base)
    return res


def deg(t, var):
    return sp.degree(t * var ** 200, var) - 200


def term(e, j, var=x):
    return sp.Add(*[t for t in sp.Add.make_args(sp.expand(e)) if deg(t, var) == j])


# ---------------------------------------------------------------- LaTeX -> sympy
def _arg(t, i):
    while t[i] == " ":
        i += 1
    if t[i] == "{":
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(t[j], 0)
            if depth == 0:
                return t[i + 1:j], j + 1
            j += 1
    return t[i], i + 1


def _conv(t):
    out, i = [], 0
    while i < len(t):
        if t.startswith(("\\dfrac", "\\tfrac", "\\frac"), i):
            i = t.index("frac", i) + 4
            u, i = _arg(t, i)
            v, i = _arg(t, i)
            out.append(f"(({_conv(u)})/({_conv(v)}))")
        elif t.startswith(("\\dbinom", "\\binom"), i):
            i = t.index("binom", i) + 5
            u, i = _arg(t, i)
            v, i = _arg(t, i)
            out.append(f" binomial({_conv(u)},{_conv(v)})")
        elif t.startswith("\\NCR", i):            # placeholder made by clean(): \NCR{n}{r}
            u, i = _arg(t, i + 4)
            v, i = _arg(t, i)
            out.append(f" binomial({_conv(u)},{_conv(v)})")
        elif t.startswith("\\sqrt", i):
            u, i = _arg(t, i + 5)
            out.append(f" sqrt({_conv(u)})")
        elif t.startswith("\\times", i):
            out.append("*")
            i += 6
        elif t.startswith("\\div", i):
            out.append("/")
            i += 4
        elif t[i] == "^":
            u, i = _arg(t, i + 1)
            out.append(f"**({_conv(u)})")
        elif t[i] == "\\":
            raise ValueError(f"unknown macro in {t!r}")
        elif t[i] in "{}":
            out.append("(" if t[i] == "{" else ")")
            i += 1
        elif t[i] == "!":
            out.append("!")
            i += 1
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def clean(t):
    t = re.sub(r"\{\}\^(\{[^{}]*\}|\w)C_(\{[^{}]*\}|\w)", r"\\NCR{\1}{\2}", t)
    t = re.sub(r"\\left|\\right|\\bigg|\\Big|\\big|\\qquad|\\quad|\\,|\\;|\\!|&nbsp;|\s", "", t)
    return re.sub(r"[+-]?\\cdots", "", t).replace("{}", "")


def tex(t):
    """Printed LaTeX -> sympy expression (n! is read as factorial(n))."""
    s = _conv(clean(t))
    s = re.sub(r"(\w+|\([^()]*\))!", r"factorial(\1)", s)
    return parse_expr(s, local_dict=dict(SYMS), transformations=TR)


def same(u, v):
    d = sp.expand_func(sp.expand(u - v))
    if sp.simplify(sp.combsimp(d)) == 0:
        return True
    if n in d.free_symbols:                    # results in terms of n: test whole numbers
        return all(sp.simplify(d.subs(n, nn)) == 0 for nn in range(4, 13))
    return False


# ---------------------------------------------------------------- HTML blocks
ans = read("a_15c.html")
les = read("l15c.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_15c.html")
report(ans.count("{{ahead:Lesson 15C | The binomial theorem}}") == 2, "answers headings", "{{ahead:Lesson 15C | ...}} twice")
BLK = {}
for mt in re.finditer(r'<div class="a"><span class="an">([^<]+)</span><div class="ab"[^>]*>(.*?)(?=<div class="a"><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts[0], re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
PPA = {int(kk): v for kk, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}
pps = les.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l15c.html")
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
PPQ = {int(kk): v for kk, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
WORKED = {kk: v for kk, v in re.findall(r'<span class="tag">Worked example( \d+|)</span>(.*?)(?=<div class="ex |<!-- =====|$)', les, re.S)}
WORKED = {kk.strip() or "C3": v for kk, v in WORKED.items()}
TQ = {kk: v for kk, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|<div class="page-break|$)', hw, re.S)}
LES = {"proof": les.split('<div class="box formula"><div class="bt">Proving the binomial theorem</div>')[1].split('<div class="box take">')[0],
       "c2": les.split("<!-- ============ Concept 2 ============ -->")[1].split('<div class="box take">')[0],
       "c3": les.split("<!-- ============ Concept 3 ============ -->")[1].split('<div class="ex demo">')[0]}


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\&).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def src(kind, key):
    table = {"A": BLK, "PP": PPA, "W": WORKED, "Q": TQ, "PQ": PPQ, "L": LES}[kind]
    if key not in table:
        raise LookupError(f"{kind} {key} block missing")
    return table[key]


def check(kind, key, template, expected):
    label = f"{kind}{key} {template}"
    try:
        got = grab(src(kind, key), template, f"{kind} {key}")
        exp = expected if isinstance(expected, tuple) else (expected,)
        if len(exp) != len(got):
            raise ValueError("number of '@' does not match expected values")
        report(all(same(tex(g), e) for g, e in zip(got, exp)), label, "printed " + " | ".join(got))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def sides(g, template):
    out = [t for t in re.split(r"=|\\approx", g) if t.strip()]
    lhs = re.split(r"\\\[|\\\(", template.split("@")[0])[-1]
    return out, lhs


def check_chain(kind, key, template, expected, min_sides=1, use_lhs=True, approx=None):
    """Printed 'A=B=C': every exact side equals expected; a side after \\approx must be
    expected rounded as approx = ('sf', digits)."""
    label = f"{kind}{key} {template}"
    try:
        (g,) = grab(src(kind, key), template, f"{kind} {key}")
        exact, apx = (re.split(r"\\approx", g) + [None])[:2]
        sd = [t.rstrip(".,") for t in exact.split("=") if t.strip()]
        lhs = re.split(r"\\\[|\\\(", template.split("@")[0])[-1]
        if use_lhs and lhs.endswith("=") and lhs[:-1].strip():
            sd.insert(0, lhs[:-1])
        ok = len(sd) >= min_sides and all(same(tex(t), expected) for t in sd)
        if approx:
            ok &= apx is not None and sigfig_ok(apx.rstrip(".,"), expected, approx)
        elif apx is not None:
            ok = False
        report(ok, label, f"printed {g}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def sigfig_ok(printed, exact, digits):
    """printed like 1.848\\times10^5: mantissa with digits significant figures."""
    m = re.fullmatch(r"(\d)\.(\d+)\\times10\^\{?(\d+)\}?", printed.strip())
    if not m or len(m.group(2)) != digits - 1:
        return False
    mant, e = Fraction(m.group(1) + "." + m.group(2)), int(m.group(3))
    ex = Fraction(int(exact))
    want = round(ex / Fraction(10) ** e, digits - 1)
    return mant == want and 1 <= ex / Fraction(10) ** e < 10


def aligned_rows(block, lead, where):
    """Rows of the first aligned environment after the text lead."""
    if block.count(lead) != 1:
        raise LookupError(f"lead {lead!r} found {block.count(lead)} times in {where}")
    body = re.search(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", block.split(lead)[1], re.S).group(1)
    return [r.strip() for r in body.split("\\\\")]


def check_rows(kind, key, lead, expected, count):
    """Rows '&A', '&=B', ... all equal expected (trailing full stop allowed)."""
    label = f"{kind}{key} rows after {lead[:40]}"
    try:
        rw = [re.sub(r"^&=?|[.,]$", "", r) for r in aligned_rows(src(kind, key), lead, f"{kind} {key}")]
        ok = len(rw) == count and all(same(tex(t), expected) for t in rw)
        report(ok, label, " | ".join(rw))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def whole_solutions(eq, lo=0, hi=60):
    """Whole numbers n in [lo, hi] satisfying eq (sympy expression = 0), with nCr as counts."""
    out = []
    for nn in range(lo, hi + 1):
        val = sp.expand_func(eq).subs(n, nn) if n in eq.free_symbols else eq
        try:
            if sp.simplify(val) == 0:
                out.append(nn)
        except Exception:
            pass
    return out


def nc(m, r):
    return sp.Integer(ncr(m, r))


# ================================================================ lesson: proof by counting words
try:
    rows = re.search(r"\\begin\{array\}\{lll\}(.*?)\\end\{array\}", LES["proof"], re.S).group(1).split("\\\\")
    words = [re.findall(r"[xy]{4}", r.split("&")[1]) for r in rows]
    allw = ["".join(w) for w in itertools.product("xy", repeat=4)]
    ok = len(rows) == 5 and sorted(sum(words, [])) == sorted(allw)
    ok &= all(all(w.count("y") == i for w in ws) for i, ws in enumerate(words))
    labels = [re.findall(r"(\d) \}?x", r) for r in rows]
    report(ok and len(sum(words, [])) == 16, "lesson 16 words of (x+y)^4", f"rows {[len(w) for w in words]}")
    collected = sum(len(ws) * x ** (4 - i) * y ** i for i, ws in enumerate(words))
    check("L", "proof", r"this becomes \(@\).", collected)
    report(same(collected, power(x + y, 4)), "lesson collected words = (x+y)^4", str(collected))
    check_chain("L", "proof", r"There are \(@\) such words.", sp.Integer(len(words[2])), 2)
    check("L", "proof", r"gives \(2^4=@\) terms", sp.Integer(len(allw)))
except Exception as err:
    report(False, "lesson proof", f"ERROR {err}")

# lesson questions really are the ones answered (each appears once in l15c.html)
for qs in (r"\(x^9\) in \((1+x)^{13}\)", r"\(x^4y^5\) in \((x+y)^9\)", r"\(A^4B^4\) in \((3A-2B)^8\)", r"\(a^{n-3}b^3\) in \((a-3b)^n\)",
           r"\(x^6\) in \((1+x)^{10}\)", r"\(x^5y^3\) in \((x+y)^8\)", r"\(A^3B^3\) in \((2A-5B)^6\)", r"\(a^{n-2}b^2\) in \((a+4b)^n\)",
           r"<b>a</b> \({}^nC_2=66\)", r"<b>b</b> \({}^nC_2+{}^nC_1+{}^nC_0=37\)", r"<b>a</b> \({}^nC_2=28\)", r"<b>b</b> \({}^nC_2+{}^nC_1+{}^nC_0=16\)",
           r"expansion of \(\Big(x^3-\dfrac2x\Big)^{12}\), find", r"expansion of \(\Big(x+\dfrac{2}{x^2}\Big)^9\), find"):
    report(les.count(qs) == 1, "lesson question", f"{qs} appears {les.count(qs)} time(s)")

# ================================================================ worked example 9 (textbook Example 9)
e = power(1 + x, 12)
check("W", "9", r"<b>a</b> \((1+x)^{12}=\cdots+@+\cdots\)", term(e, 8))
check_rows("W", "9", "so the coefficient of \\(x^8\\) is</p>", e.coeff(x, 8), 3)
report(e.coeff(x, 8) == ncr(12, 8), "W9a coefficient = 12C8 (subsets)", str(ncr(12, 8)))
e = power(x + y, 7)
check("W", "9", r"<b>b</b> \((x+y)^7=\cdots+@+\cdots\)", term(e, 3))
check_rows("W", "9", "so the term in \\(x^3y^4\\) is</p>", term(e, 3), 3)
e = power(2 * A - 3 * B, 10)
check("W", "9", r"<b>c</b> \((2A-3B)^{10}=\cdots+@+\cdots\)", term(e, 5, A))
check_rows("W", "9", "so the coefficient of \\(A^5B^5\\) is</p>", sp.Poly(e, A, B).coeff_monomial(A ** 5 * B ** 5), 4)
try:
    (g,) = grab(WORKED["9"], r"&=-@.\end{aligned}", "W 9")
    report(sp.factorint(tex(g)) == sp.factorint(-sp.Poly(e, A, B).coeff_monomial(A ** 5 * B ** 5)) and set(re.findall(r"(\d+)\^", g)) <= {"2", "3"},
           "W9c factored into primes", g)
except Exception as err:
    report(False, "W9c primes", f"ERROR {err}")


def general_term_ok(printed, base, mono):
    """printed: coefficient (times mono) in terms of n; compare with expanded (base)^n, n = 4..12."""
    for nn in range(4, 13):
        ee = power(base.subs(n, nn), nn)
        mm = mono.subs(n, nn)
        want = sp.Poly(ee, a, b).coeff_monomial(mm)
        got = sp.expand_func(printed.subs(n, nn))
        if sp.simplify(got - want * mm) != 0:
            return False
    return True


try:
    rw = [re.sub(r"^&=?|[.,]$", "", r) for r in aligned_rows(WORKED["9"], "so the term in \\(a^{n-4}b^4\\) is</p>", "W 9")]
    report(len(rw) == 3 and all(general_term_ok(tex(t), a - 2 * b, a ** (n - 4) * b ** 4) for t in rw), "W9d rows, n = 4..12", " | ".join(rw))
    (g,) = grab(WORKED["9"], r"<b>d</b> \((a-2b)^n=\cdots+@+\cdots\)", "W 9")
    report(general_term_ok(tex(g), a - 2 * b, a ** (n - 4) * b ** 4), "W9d theorem term", g)
except Exception as err:
    report(False, "W9d", f"ERROR {err}")

# ================================================================ concept 2 and worked example 10
for templ, val in ((r"\[{}^nC_0=\dfrac{n!}{0!\,n!}=@\qquad", 0), (r"\qquad{}^nC_1=\dfrac{n!}{1!\,(n-1)!}=@\qquad", 1), (r"\qquad{}^nC_2=\dfrac{n!}{2!\,(n-2)!}=@\]", 2)):
    try:
        (g,) = grab(LES["c2"], templ, "concept 2")
        lhs = re.search(r"=(\\dfrac\{n!\}\{.*?\})=@", templ).group(1)
        ok = all(tex(g).subs(n, nn) == ncr(nn, val) and tex(lhs).subs(n, nn) == ncr(nn, val) for nn in range(2, 15))
        report(ok, f"concept 2: nC{val}", f"printed {g}, n = 2..14 against subset counts")
    except Exception as err:
        report(False, f"concept 2 nC{val}", f"ERROR {err}")


def check_eq_rows(kind, key, lead, eq0, final, count):
    """Each aligned row 'L&=R' has the same whole-number solutions n >= 0 as eq0 = 0; and the
    printed final value is the only solution."""
    label = f"{kind}{key} equation rows after {lead[:30]}"
    try:
        rw = aligned_rows(src(kind, key), lead, f"{kind} {key}")
        sol0 = whole_solutions(eq0)
        oks = []
        for r in rw:
            lh, rh = r.split("&=")
            oks.append(whole_solutions(tex(lh) - tex(rh)) == sol0)
        report(len(rw) == count and all(oks) and sol0 == [final], label, f"{rw}, solutions n >= 0: {sol0}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


try:
    w10a, w10b = WORKED["10"].split("<p><b>b</b></p>")
    LES["w10a"], LES["w10b"] = w10a.split("<p><b>a</b></p>")[1], w10b
    for kk, eq0 in (("w10a", sp.binomial(n, 2) - 55), ("w10b", sp.binomial(n, 2) + sp.binomial(n, 1) + sp.binomial(n, 0) - 29)):
        (fin,) = grab(LES[kk], r"Because \(n\ge0\), \(n=@\).", kk)
        check_eq_rows("L", kk, "\\[", eq0, int(fin), 3 if kk == "w10a" else 5)
except Exception as err:
    report(False, "W10", f"ERROR {err}")

# ================================================================ concept 3 and its worked example
check_chain("L", "c3", r"For example, \(\Big(x^3-\dfrac2x\Big)^{12}=@\).", power(x ** 3 - 2 / x, 12), 2)
e = sp.expand(power(x + 1 / x, 20) * power(x - 1 / x, 20))
W3 = WORKED["C3"]
check_chain("W", "C3", r"and \(\big(x+x^{-1}\big)\big(x-x^{-1}\big)=@\),", sp.expand((x + 1 / x) * (x - 1 / x)), 2)
check_chain("W", "C3", r"\[\Big(x+\dfrac1x\Big)^{20}\Big(x-\dfrac1x\Big)^{20}=@.\]", e, 2)
check("W", "C3", r"The first term \(\big(x^2\big)^{20}\) has \(@\).", x ** max(deg(t, x) for t in sp.Add.make_args(e)))
try:
    (st, ) = grab(W3, r"goes down by @. The power", "W C3")
    (nst,) = grab(W3, r"is reached after @ steps", "W C3")
    degs = sorted({deg(t, x) for t in sp.Add.make_args(power(x ** 2 - x ** -2, 20))}, reverse=True)
    report(all(u - v == int(st) for u, v in zip(degs, degs[1:])) and degs.index(0) == int(nst), "W C3 step and number of steps", f"{st}, {nst}")
except Exception as err:
    report(False, "W C3 steps", f"ERROR {err}")
try:
    rw = [re.sub(r"^&=?|[.,]$", "", r) for r in aligned_rows(W3, "so the term independent of \\(x\\) is</p>", "W C3")]
    ok = len(rw) == 4 and all(same(tex(t), e.coeff(x, 0)) for t in rw[:3])
    ok &= rw[3].startswith("\\approx") and sigfig_ok(rw[3][len("\\approx"):], e.coeff(x, 0), 4)
    report(ok and e.coeff(x, 0) == ncr(20, 10), "W C3 rows (exact, then 4 s.f.)", " | ".join(rw))
except Exception as err:
    report(False, "W C3 rows", f"ERROR {err}")

# ================================================================ results printed inside textbook questions
try:
    report(all(sp.binomial(nn, 2) + sp.binomial(nn + 1, 2) == nn ** 2 for nn in range(0, 40)), "Q12c identity nC2 + (n+1)C2 = n^2", "n = 0..39")
    (g,) = grab(TQ["12"], r"show that \(@\), and verify", "Q 12")
    lh, rh = g.split("=")
    report(all(tex(lh).subs(n, nn) == ncr(nn, 2) + ncr(nn + 1, 2) and tex(rh).subs(n, nn) == nn ** 2 for nn in range(2, 15)), "Q12c printed", g)
    report(all((7 ** m + 2) % 3 == 0 and (5 ** m + 3) % 4 == 0 for m in range(1, 60)), "Q16(a)(b) divisibility", "n = 1..59")
    report((5 ** 42 - 2 ** 48) % 9 == 0 and 5 ** 42 - 2 ** 41 * (2 + 3 * 42) == 5 ** 42 - 2 ** 48, "Q16c: 5^42 - 2^48 divisible by 9 (a = 5, b = 2, c = 3, n = 42)", "")
    report(all((((bb + cc) ** m - bb ** (m - 1) * (bb + cc * m)) % cc ** 2) == 0 for bb in range(1, 7) for cc in range(1, 7) for m in range(1, 9)), "Q16c general", "b, c 1..6, n 1..8")
    (g,) = grab(TQ["7"], r'padding:1mm 0">\(@\)</span>', "Q 7")
    lh, rh = g.split("=")
    report(same(tex(lh).subs({n: 8, sp.Symbol("r"): 3}), nc(8, 2) + nc(8, 3)) and same(tex(rh).subs({n: 8, sp.Symbol("r"): 3}), nc(9, 3)) and nc(8, 2) + nc(8, 3) == nc(9, 3),
           "Q7a identity at n = 8, r = 3", g)
    (g,) = grab(TQ["20"], r'padding:1mm 0">\((1+x)^n=@.\)</span>', "Q 20")
    report(all(same(tex(g).subs(n, nn), sp.expand(power(1 + x, nn) - sp.Add(*[t for t in sp.Add.make_args(power(1 + x, nn)) if deg(t, x) > 3]))) for nn in range(3, 9)),
           "Q20a printed series, n = 3..8", g)
except Exception as err:
    report(False, "results in questions", f"ERROR {err}")
report(sorted(TQ, key=int) == [str(i) for i in range(1, 21)], "textbook questions 1-20", f"{sorted(TQ, key=int)}")
report(hw.count("{{band:F}}") == hw.count("{{band:D}}") == hw.count("{{band:E}}") == 1 and hw.index('q-num">10<') < hw.index("{{band:D}}") < hw.index('q-num">11<')
       and hw.index('q-num">17<') < hw.index("{{band:E}}") < hw.index('q-num">18<'), "bands F 1-10, D 11-17, E 18-20", "")

# ================================================================ lesson examples (C1-C3)
C1 = BLK.get("C1", "")
tdemo, yturn = C1.split("<b>Your turn.</b>") if "<b>Your turn.</b>" in C1 else ("", "")
BLK["C1t"], BLK["C1y"] = tdemo, yturn
check_chain("A", "C1t", r"<b>a</b> \(@\)<br>", power(1 + x, 13).coeff(x, 9), 3, use_lhs=False)
report(ncr(13, 9) == 715, "C1 13C9 by subsets", str(ncr(13, 9)))
check_chain("A", "C1t", r"<b>b</b> \(@\)<br>", term(power(x + y, 9), 4), 2, use_lhs=False)
eC = sp.Poly(power(3 * A - 2 * B, 8), A, B).coeff_monomial(A ** 4 * B ** 4)
check_chain("A", "C1t", r"<b>c</b> \(@\)<br>", eC, 3, use_lhs=False)
try:
    (g,) = grab(BLK["C1t"], r"<b>c</b> \({}^8C_4\times3^4\times2^4=90720=@\)", "C1t")
    report(sp.factorint(tex(g)) == sp.factorint(eC) and re.fullmatch(r"(\d+(\^\d+)?\\times)*\d+(\^\d+)?", g) is not None, "C1t c primes", g)
except Exception as err:
    report(False, "C1t c primes", f"ERROR {err}")
try:
    (g,) = grab(BLK["C1t"], r"<b>d</b> \(@\)<br>", "C1t")
    report(all(general_term_ok(tex(t), a - 3 * b, a ** (n - 3) * b ** 3) for t in g.split("=")) and len(g.split("=")) == 2, "C1t d, n = 4..12", g)
except Exception as err:
    report(False, "C1t d", f"ERROR {err}")
check_chain("A", "C1y", r"<b>a</b> \(@\)<br>", power(1 + x, 10).coeff(x, 6), 2, use_lhs=False)
check_chain("A", "C1y", r"<b>b</b> \(@\)<br>", term(power(x + y, 8), 5), 2, use_lhs=False)
eC = sp.Poly(power(2 * A - 5 * B, 6), A, B).coeff_monomial(A ** 3 * B ** 3)
check_chain("A", "C1y", r"<b>c</b> \(@\)<br>", eC, 3, use_lhs=False)
try:
    (g,) = grab(BLK["C1y"], r"=-20000=-@\)", "C1y")
    report(sp.factorint(tex(g)) == sp.factorint(-eC), "C1y c primes", g)
    (g,) = grab(BLK["C1y"], r"<b>d</b> \(@\)</div>", "C1y")
    report(all(general_term_ok(tex(t), a + 4 * b, a ** (n - 2) * b ** 2) for t in g.split("=")) and len(g.split("=")) == 2, "C1y d, n = 4..12", g)
except Exception as err:
    report(False, "C1y c/d", f"ERROR {err}")
for templ, eq0 in ((r"<b>Tutor demo.</b><br><b>a</b> \(@\), so \(@\) and \(n=@\)<br>", sp.binomial(n, 2) - 66),
                   (r"and \(n=12\)<br><b>b</b> \(@\), so \(@\) and \(n=@\)<br>", sp.binomial(n, 2) + sp.binomial(n, 1) + 1 - 37),
                   (r"<b>Your turn.</b><br><b>a</b> \(@\), so \(@\) and \(n=@\)<br>", sp.binomial(n, 2) - 28),
                   (r"and \(n=8\)<br><b>b</b> \(@\), so \(@\) and \(n=@\)</div>", sp.binomial(n, 2) + sp.binomial(n, 1) + 1 - 16)):
    try:
        g1, g2, g3 = grab(BLK["C2"], templ, "C2")
        sol0 = whole_solutions(eq0)
        ok = all(whole_solutions(tex(t.split("=")[0]) - tex(t.split("=")[1])) == sol0 for t in (g1, g2)) and sol0 == [int(g3)]
        report(ok, f"AC2 {templ[:34]}", f"{g1} | {g2} | n = {g3}; whole-number solutions {sol0}")
    except Exception as err:
        report(False, f"AC2 {templ[:30]}", f"ERROR {err}")


C3 = BLK.get("C3", "")
for half, base, top_ in ((C3.split("<b>Your turn.</b>")[0], x ** 3 - 2 / x, 12), (C3.split("<b>Your turn.</b>")[-1], x + 2 / x ** 2, 9)):
    e = power(base, top_)
    degs = sorted({deg(t, x) for t in sp.Add.make_args(e)}, reverse=True)
    try:
        st, first = grab(half, r"go down by @ from \(x^@\).", "C3")
        first = tex(first)
        report(int(first) == degs[0] and all(u - v == int(st) for u, v in zip(degs, degs[1:])), f"AC3 {base} step", f"{st} from x^{first}")
        for mt in re.finditer(r"<b>[ab]</b> \\\(x\^\{?(-?\d+)\}?\\\) after (\d+) steps: \\\((.*?)\\\)", half):
            j, nst, chain = int(mt.group(1)), int(mt.group(2)), mt.group(3)
            sd = chain.split("=")
            report(degs.index(j) == nst and len(sd) == 3 and all(same(tex(t), term(e, j)) for t in sd), f"AC3 {base} term in x^{j}", chain)
        report(len(re.findall(r"after \d+ steps", half)) == 2, f"AC3 {base} two parts", "")
    except Exception as err:
        report(False, f"AC3 {base}", f"ERROR {err}")

# ================================================================ textbook homework answers
check("A", "1", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)</div>", (nc(4, 3), nc(6, 3), nc(9, 1), nc(7, 3)))
check("A", "2", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)</div>", (nc(5, 2), nc(8, 8), nc(11, 10), nc(10, 4)))
check("A", "3", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\) &nbsp; <b>e</b> \(@\) &nbsp; <b>f</b> \(@\)</div>",
      (nc(15, 10), nc(13, 5), nc(12, 7), nc(12, 3) / nc(5, 2), nc(15, 8) / nc(6, 4), nc(19, 6) / nc(7, 5)))
e4 = power(1 + x, 4)
try:
    vals = re.findall(r"\\\(\{\}\^4C_(\d)=(\d+)\\\)", BLK["4"])
    report([int(r) for r, _ in vals] == [0, 1, 2, 3, 4] and all(int(v) == e4.coeff(x, int(r)) for r, v in vals), "A4a values from (1+x)^4", str(vals))
except Exception as err:
    report(False, "A4a", f"ERROR {err}")
check("A", "4", r"<b>b</b> (i) \(@\) (ii) \(@\)</div>", (e4.subs(x, 1), e4.subs(x, -1)))
check("A", "5", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)</div>",
      (nc(6, 0) + nc(6, 2) + nc(6, 4) + nc(6, 6), nc(6, 1) + nc(6, 3) + nc(6, 5), sum(nc(m, 2) for m in range(2, 6)), sum(nc(5, r) ** 2 for r in range(6))))
check("A", "6", r"<b>a</b> (i) both are \(@\) (ii) both are \(@\)<br>", (nc(8, 3), nc(7, 4)))
report(nc(8, 3) == nc(8, 5) and nc(7, 4) == nc(7, 3), "A6a pairs equal", "")
try:
    (g,) = grab(BLK["6"], r"<b>b</b> \(n=@\) &nbsp;", "6")
    sol = [m for m in range(3, 60) if ncr(m, 3) == ncr(m, 2)]
    report(sol == [int(g)], "A6b", f"printed {g}, brute force {sol}")
    g1, g2 = grab(BLK["6"], r"<b>c</b> \(n=@\) or \(n=@\)</div>", "6")
    sol = [m for m in range(0, 13) if ncr(12, m) == ncr(12, 4)]
    report(sol == sorted([int(g1), int(g2)]), "A6c", f"printed {g1}, {g2}, brute force {sol}")
    g1, g2 = grab(BLK["7"], r"<b>b</b> (i) \(n=@\) (ii) \(n=@\)</div>", "7")
    s1 = [m for m in range(4, 60) if ncr(m, 4) == ncr(5, 3) + ncr(5, 4)]
    s2 = [m for m in range(8, 60) if ncr(m, 7) + ncr(m, 8) == ncr(11, 8)]
    report(s1 == [int(g1)] and s2 == [int(g2)], "A7b", f"printed {g1}, {g2}, brute force {s1}, {s2}")
except Exception as err:
    report(False, "A6/A7", f"ERROR {err}")
check("A", "8", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)</div>",
      (term(power(1 + x, 18), 5), term(power(1 + 6 * x, 12), 9), term(power(1 - 7 * x, 8), 3), power(1 + 3 * x, 7).coeff(x, 2)))
bh = sp.Symbol("bh", positive=True)                 # b^(1/2)
e9d = power(a - bh, 20)
check("A", "9", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)</div>",
      (term(power(2 + x, 7), 2), sp.Poly(power(x + y / 2, 14), x, y).coeff_monomial(x ** 9 * y ** 5) * x ** 9 * y ** 5,
       sp.Poly(power(x / 2 - 3 * y ** 2, 11), x, y).coeff_monomial(x ** 10 * y ** 2) * x ** 10 * y ** 2,
       sp.Poly(e9d, a, bh).coeff_monomial(a ** 2 * bh ** 18) * a ** 2 * b ** 9))
e10a, e10b = power(5 + 2 * x, 15), power(2 - 3 * x, 17)
s10a = [v for v in sp.solve(sp.Eq(term(e10a, 10), term(e10a, 11)), x) if v != 0]
s10b = [v for v in sp.solve(sp.Eq(term(e10b, 13), term(e10b, 14)), x) if v != 0]
check("A", "10", r"<b>a</b> \(x=@\) &nbsp; <b>b</b> \(x=@\)</div>", (s10a[0] if len(s10a) == 1 else sp.nan, s10b[0] if len(s10b) == 1 else sp.nan))


def ratio_ok(g, u, v):
    lh, rh = g.split(":")
    return same(tex(lh) * v, tex(rh) * u) and tex(rh).is_Integer and (tex(lh) / x ** deg(tex(lh), x)).is_Integer and sp.gcd(tex(lh) / x ** deg(tex(lh), x), tex(rh)) == 1


try:
    e = power(1 + x, 16)
    g = grab(BLK["11"], r"<b>a</b> \(@\) &nbsp;", "11")[0]
    report(ratio_ok(g, term(e, 13), term(e, 11)), "A11a", g)
    e = power(1 + x, 20)
    g = grab(BLK["11"], r"<b>b</b> \(@\) &nbsp;", "11")[0]
    report(ratio_ok(g, e.coeff(x, 14), e.coeff(x, 5)), "A11b", g)
    e = power(2 + x, 18)
    g = grab(BLK["11"], r"<b>c</b> \(@\)</div>", "11")[0]
    report(ratio_ok(g, e.coeff(x, 10), e.coeff(x, 16)), "A11c", g)
except Exception as err:
    report(False, "A11", f"ERROR {err}")
try:
    got = grab(BLK["12"], r"<b>a</b> (i) \(@\) (ii) \(@\) (iii) \(@\) (iv) \(@\)<br>", "12")
    report(all(all(tex(g).subs(n, nn) == ncr(nn, r) for nn in range(r, 16)) for r, g in enumerate(got)), "A12a formulae nC0..nC3 vs subset counts", " | ".join(got))
    got = grab(BLK["12"], r"<b>b</b> (i) \(@\) (ii) \(@\) (iii) \(@\) (iv) \(@\) (v) \(@\) (vi) \(@\)</div>", "12")
    eqs = [lambda m: ncr(9, 2) - ncr(m, 1) == ncr(6, 3), lambda m: ncr(m, 2) == 36, lambda m: ncr(m, 2) + ncr(6, 2) == ncr(7, 2),
           lambda m: ncr(m, 2) + ncr(m, 1) == 22 - ncr(m, 0), lambda m: ncr(m, 1) + ncr(m, 2) == ncr(5, 2), lambda m: ncr(m, 3) + ncr(m, 2) == 8 * ncr(m, 1)]
    sols = [[m for m in range(1, 40) if f(m)] for f in eqs]
    report(all(s == [int(g)] for s, g in zip(sols, got)), "A12b brute force", f"printed {got}, solutions {sols}")
except Exception as err:
    report(False, "A12", f"ERROR {err}")
try:
    for part, t1, t2 in (("a", 28, 364), ("b", sp.Rational(-10, 3), 5)):
        g1, g2 = grab(BLK["13"], rf"<b>{part}</b> \(a=@\) and \(n=@\)", "13")
        av, nv = tex(g1), int(g2)
        e = power(1 + av * x, nv)
        sols = [(aa, m) for m in range(1, 40) for aa in [sp.Rational(t1, m)] if sp.binomial(m, 2) * aa ** 2 == t2]
        report(e.coeff(x, 1) == t1 and e.coeff(x, 2) == t2 and sols == [(av, nv)], f"A13{part}", f"a = {av}, n = {nv}; search {sols}")
except Exception as err:
    report(False, "A13", f"ERROR {err}")
try:
    g1, g2 = grab(BLK["14"], r"<b>a</b> \(n=@\) &nbsp; <b>b</b> \(n=@\)</div>", "14")
    s1 = [m for m in range(6, 40) if 9 * power(2 + 3 * x, m).coeff(x, 5) == 4 * power(2 + 3 * x, m).coeff(x, 6)]
    s2 = [m for m in range(10, 40) if 2 * power(1 + 3 * x, m).coeff(x, 8) == power(1 + 3 * x, m).coeff(x, 10)]
    report(s1 == [int(g1)] and s2 == [int(g2)], "A14 by expanding n = 6..39", f"printed {g1}, {g2}; found {s1}, {s2}")
except Exception as err:
    report(False, "A14", f"ERROR {err}")
e15 = sp.expand(power(x + 1 / x, 40) * power(x - 1 / x, 40))
check_chain("A", "15", r"\(@\)</div>", e15.coeff(x, 0), 1, use_lhs=False, approx=4)
try:
    g = grab(BLK["17"], r"<b>b</b> \(@\)</div>", "17")[0]
    report(all(same(tex(g).subs(n, m), sp.limit((power(x + h, m) - x ** m) / h, h, 0)) for m in range(1, 9)), "A17b first principles, n = 1..8", g)
    g = grab(BLK["17"], r"<b>a</b> \(@\)<br>", "17")[0]
    terms = [t for t in re.split(r"\+", g) if "cdots" not in t]
    ok = all(same(tex(t).subs(n, m), term(power(x + h, m), m - j, x)) for m in range(4, 9)
             for j, t in [(0, terms[0]), (1, terms[1]), (2, terms[2]), (m, terms[3])])
    report(ok and len(terms) == 4, "A17a printed terms, n = 4..8", g)
except Exception as err:
    report(False, "A17", f"ERROR {err}")
try:
    rows = re.findall(r"<b>([abc])</b> (\d+) points, (.*?)(?:<br>|</div>)", BLK["19"])
    names = {"segments": 2, "triangles": 3, "quadrilaterals": 4, "quadrilateral": 4, "pentagon": 5, "pentagons": 5, "triangle": 3}
    ok = len(rows) == 3
    for part, pts, rest in rows:
        m = int(pts)
        for cnt, word in re.findall(r"(\d+) (\w+)", rest):
            ok &= int(cnt) == len(list(itertools.combinations(range(m), names[word])))
        ok &= len(re.findall(r"(\d+) (\w+)", rest)) == m - 1
    (g,) = grab(BLK["19"], r"<b>d</b> \(@\)</div>", "19")
    ok &= int(g) == len(list(itertools.combinations(range(7), 5)))
    report(ok, "A19 polygons from points on a circle (enumerated)", str(rows) + " d " + g)
except Exception as err:
    report(False, "A19", f"ERROR {err}")
try:
    fns = [1 / (1 - x), 1 / (1 - x) ** 2, 1 / (1 + x) ** 2, sp.sqrt(1 + x)]
    got = grab(BLK["20"], r"<b>b</b> (i) \(@\)<br>(ii) \(@\)<br>(iii) \(@\)<br>(iv) \(@\)<br>", "20")
    report(all(same(tex(g), sp.series(f, x, 0, 4).removeO()) for g, f in zip(got, fns)), "A20b power series to x^3", " | ".join(got))
    rw = [re.sub(r"^(\\text\{LHS\})?&=|\.$", "", r) for r in aligned_rows(BLK["20"], "Using part b(i),", "20")]
    report(len(rw) == 4 and same(tex(rw[2]), sp.series(sp.diff(1 / (1 - x), x), x, 0, 3).removeO()) and same(sp.diff(tex(rw[1].replace("\\dfrac{d}{dx}", "")), x), tex(rw[2])),
           "A20c rows", " | ".join(rw))
except Exception as err:
    report(False, "A20", f"ERROR {err}")
# Q18: the printed proof, and a brute-force check of the result for primes up to 13
try:
    (g,) = grab(BLK["18"], r"The second member of row \(n\) is \(@\). Suppose", "18")
    report(len(g.split("=")) == 2 and all(tex(t).subs(n, m) == ncr(m, 1) for t in g.split("=") for m in range(2, 15)), "A18 second member nC1 = n", g)
    (g,) = grab(BLK["18"], r"Then \({}^nC_r\times r!\,(n-r)!=@\), so", "18")
    sd = g.split("=")
    report(len(sd) == 2 and all(same(tex(t).subs({n: m}), sp.factorial(m)) for t in sd for m in range(2, 12))
           and all(ncr(m, r) * sp.factorial(r) * sp.factorial(m - r) == sp.factorial(m) for m in range(2, 12) for r in range(0, m + 1)),
           "A18 nCr r!(n-r)! = n!", g)
    (g,) = grab(BLK["18"], r"Also \(@\). So every", "18")
    report(all(tex(t).subs(n, m) == m for m in range(2, 15) for t in [r"{}^nC_1", r"{}^nC_{n-1}"]) and g.split("=")[-1] == "n", "A18 nC1 = nC(n-1) = n", g)
    primes = [m for m in range(2, 14) if all(m % d for d in range(2, m))]
    report(primes == [2, 3, 5, 7, 11, 13] and all(ncr(m, r) % m == 0 for m in primes for r in range(1, m)),
           "A18 brute force: n | nCr for 1 <= r <= n-1, primes n <= 13", str(primes))
except Exception as err:
    report(False, "A18", f"ERROR {err}")
# answered questions: 7a, 12c, 16, 20a are show/verify items with no final answer
report(set(BLK) == {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "17", "18", "19", "20", "C1", "C2", "C3", "C1t", "C1y"},
       "answer blocks", f"{sorted(BLK, key=lambda t: (len(t), t))}")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(v) for v in re.findall(r'<span class="pp-src"|<span class="mk">(\d+) marks?</span>', pps[1]) if v]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M} (house rule: 15-22)")
    report(T == 5 * round(1.5 * M / 5), "PP time", f"{T} min for {M} marks")
    subs = re.findall(r'<span class="mk">(\d)</span></div>', PPQ[4])
    report([int(s) for s in subs] == [1, 2] and marks[3] == 3, "PP4 part marks 1 + 2 = 3", str(subs))
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for kk in PPQ:
        sq = re.search(r"^(.*?)</span>", PPQ[kk]).group(1)
        sa = re.search(r"^(.*?)</span>", PPA[kk]).group(1) if kk in PPA else None
        report(sq == sa, f"PP{kk} source label", sq)
        report(PPQ[kk].count('<div class="hint">') == 1, f"PP{kk} hint", "exactly one hint")
except Exception as err:
    report(False, "PP structure", f"ERROR {err}")


def mc(pp, expected):
    try:
        opts = dict(re.findall(r"<span>\(([A-D])\) \\\((.+?)\\\)</span>", PPQ[pp]))
        good = [L for L, v in opts.items() if same(tex(v), expected)]
        (letter,) = grab(PPA[pp], "<b>Answer (@).</b>", f"PP {pp}")
        report(len(opts) == 4 and good == [letter], f"PP{pp} MC letter", f"printed {letter}, option(s) equal to {expected}: {good}")
    except Exception as err:
        report(False, f"PP{pp} MC letter", f"ERROR {err}")


def steps_ok(pp, e, target, templ_step=r"goes down by @. The power", templ_n=r"is reached after @ steps"):
    try:
        degs = sorted({deg(t, x) for t in sp.Add.make_args(e)}, reverse=True)
        (st,) = grab(PPA[pp], templ_step, f"PP {pp}")
        (ns,) = grab(PPA[pp], templ_n, f"PP {pp}")
        report(all(u - v == int(st) for u, v in zip(degs, degs[1:])) and degs.index(target) == int(ns), f"PP{pp} step {st}, {ns} steps", f"powers {degs[:4]}...")
    except Exception as err:
        report(False, f"PP{pp} steps", f"ERROR {err}")


# PP1 SGS 2020: coefficient of x^3 in (2 - 3x)^8
e = power(2 - 3 * x, 8)
check("PQ", 1, r"expansion of \(@\)?", (2 - 3 * x) ** 8)
check("PP", 1, r"\[(2-3x)^8=\cdots+@+\cdots\]", term(e, 3))
check_chain("PP", 1, r"Here \({}^8C_3=@\), so", nc(8, 3), 2)
check_chain("PP", 1, r"\[56\times32\times(-27x^3)=@.\]", term(e, 3), 2)
check("PP", 1, r"The coefficient is \(@\). <b>", e.coeff(x, 3))
mc(1, e.coeff(x, 3))
# PP2 SGS 2022: constant term of (4x^2 - 1/x)^9
e = power(4 * x ** 2 - 1 / x, 9)
check("PQ", 2, r"expansion of \(@\)?", (4 * x ** 2 - 1 / x) ** 9)
check_chain("PP", 2, r"Write \(@\). The first", e, 2)
check("PP", 2, r"\big)^9\) has \(@\). From", x ** 18)
steps_ok(2, e, 0)
check_chain("PP", 2, r"\[{}^9C_6\times\big(4x^2\big)^3\times\big(-x^{-1}\big)^6=@.\]", e.coeff(x, 0), 3)
mc(2, e.coeff(x, 0))
# PP3 Abbotsleigh 2023: coefficient of x^6 in (2x - p)^9 is -672000
e = power(2 * x - p, 9)
check("PQ", 3, r"The coefficient of the term in \(x^6\) is \(@\).", sp.Integer(-672000))
check("PP", 3, r"\[(2x-p)^9=\cdots+@+\cdots\]", term(e, 6))
check_chain("PP", 3, r"coefficient of \(x^6\) is \(@\). Then", e.coeff(x, 6), 2, use_lhs=False)
try:
    g1, g2, g3 = grab(PPA[3], r"\[@,\quad\text{so}\quad@\quad\text{and}\quad p=@.\]", "PP 3")
    real = [v for v in sp.solve(sp.Eq(e.coeff(x, 6), -672000), p) if v.is_real]
    ok = all(set(v for v in sp.solve(sp.Eq(tex(t.split("=")[0]), tex(t.split("=")[1])), p) if v.is_real) == set(real) for t in (g1, g2))
    report(ok and real == [tex(g3)], "PP3 p", f"{g1} | {g2} | p = {g3}; real solutions {real}")
except Exception as err:
    report(False, "PP3 p", f"ERROR {err}")
# PP4 NSG 2023: coefficient of x^k in (2 + 3x)^6; coefficient of x^3 in (2 + 3x)^6 (1 - 4x^2)
e = power(2 + 3 * x, 6)
try:
    (g,) = grab(PPA[4], r"so the coefficient of \(x^k\) is \(@\).</p>", "PP 4")
    report(all(tex(g).subs(k, kk) == e.coeff(x, kk) for kk in range(7)), "PP4(i) coefficient of x^k, k = 0..6", g)
    (g,) = grab(PPA[4], r"\[(2+3x)^6=\cdots+@+\cdots\]", "PP 4")
    report(all(sp.expand(tex(g).subs(k, kk)) == term(e, kk) for kk in range(7)), "PP4(i) theorem term", g)
except Exception as err:
    report(False, "PP4(i)", f"ERROR {err}")
check_chain("PP", 4, r"\[{}^6C_3\times2^3\times3^3=@\quad", e.coeff(x, 3), 2)
check_chain("PP", 4, r"\quad{}^6C_1\times2^5\times3=@.\]", e.coeff(x, 1), 2)
check_chain("PP", 4, r"\[4320-4\times576=@.\]", sp.expand(e * (1 - 4 * x ** 2)).coeff(x, 3), 2)
# PP5 NSG 2020: term independent of x in (2x^2 - 3/x)^9
e = power(2 * x ** 2 - 3 / x, 9)
check("PQ", 5, r"expansion of \(@\).</div>", (2 * x ** 2 - 3 / x) ** 9)
check_chain("PP", 5, r"Write \(@\). The first", e, 2)
check("PP", 5, r"\big)^9\) has \(@\). From", x ** 18)
steps_ok(5, e, 0)
check_chain("PP", 5, r"\[{}^9C_6\times\big(2x^2\big)^3\times\big(-3x^{-1}\big)^6=@.\]", e.coeff(x, 0), 3)
# PP6 NSB 2020: term independent of x in (x^2 - 1/x^2)^10
e = power(x ** 2 - 1 / x ** 2, 10)
check("PQ", 6, r"in the expansion \(@\)</div>", (x ** 2 - 1 / x ** 2) ** 10)
check_chain("PP", 6, r"Write \(@\). The first", e, 2)
check("PP", 6, r"\big)^{10}\) has \(@\). From", x ** 20)
steps_ok(6, e, 0)
check_chain("PP", 6, r"\[{}^{10}C_5\times\big(x^2\big)^5\times\big(-x^{-2}\big)^5=@.\]", e.coeff(x, 0), 3)
# PP7 Hornsby 2023: coefficients of x^6 and x^8 in (1 + 2x)^n in ratio 7:3
try:
    sol = [m for m in range(8, 60) if 3 * power(1 + 2 * x, m).coeff(x, 6) == 7 * power(1 + 2 * x, m).coeff(x, 8)]
    (g,) = grab(PPA[7], r"Hence \(n=@\).</p>", "PP 7")
    report(sol == [int(g)], "PP7 n by expanding n = 8..59", f"printed {g}, found {sol}")
    (g,) = grab(PPA[7], r"\[\dfrac{{}^nC_6\times2^6}{{}^nC_8\times2^8}=@.\]", "PP 7")
    lhs7 = tex(r"\dfrac{{}^nC_6\times2^6}{{}^nC_8\times2^8}")
    report(whole_solutions(lhs7 - tex(g), 8, 60) == sol and all(lhs7.subs(n, m) == Fraction(power(1 + 2 * x, m).coeff(x, 6), power(1 + 2 * x, m).coeff(x, 8)) for m in range(8, 12)),
           "PP7 ratio equation", g)
    check_chain("PP", 7, r"<p>Now</p>" + "\n" + r"\[\dfrac{{}^nC_6}{{}^nC_8}=@,\]", sp.binomial(n, 6) / sp.binomial(n, 8), 2)
    rw = aligned_rows(PPA[7], "<p>so</p>", "PP 7")
    eq0 = 3 * sp.binomial(n, 6) * 2 ** 6 - 7 * sp.binomial(n, 8) * 2 ** 8
    sols = [whole_solutions(tex(r.split("&=")[0]) - tex(r.split("&=")[1]), 8, 60) for r in rw]
    report(len(rw) == 4 and all(s == sol for s in sols), "PP7 rows, solutions with n >= 8", f"{sols}")
    allroots = [sp.solve(tex(r.split("&=")[0]) - tex(r.split("&=")[1]), n) for r in rw]
    report(sorted(allroots[-1]) == [4, 9] and sorted(allroots[1]) == [4, 9], "PP7 quadratic roots 4 and 9", str(allroots))
    g1, g2 = grab(PPA[7], r"are \(@\) and \(@\). So</p>", "PP 7")
    report(all(sp.expand_func(tex(g1)).subs(n, m) == power(1 + 2 * x, m).coeff(x, 6) and sp.expand_func(tex(g2)).subs(n, m) == power(1 + 2 * x, m).coeff(x, 8) for m in range(8, 14)),
           "PP7 printed coefficients vs expansion, n = 8..13", f"{g1} | {g2}")
except Exception as err:
    report(False, "PP7", f"ERROR {err}")
# PP8 NBHS 2021: coefficients of x^17 and x^27 in (px^3 - q/x^2)^9 equal => p = 6q
e = power(p * x ** 3 - q / x ** 2, 9)
check_chain("PP", 8, r"Write \(@\). The first", e, 2)
check_chain("PP", 8, r"The first term is \(@\), so", term(e, 27), 2)
check("PP", 8, r"coefficient of \(x^{27}\) is \(@\). From", e.coeff(x, 27))
try:
    (lst,) = grab(PPA[8], r"goes down by 5: \(@\) The term", "PP 8")
    printed = [int(t) for t in re.findall(r"x\^\{(\d+)\}", lst)]
    degs = sorted({deg(t, x) for t in sp.Add.make_args(e)}, reverse=True)
    (ns,) = grab(PPA[8], r"is reached after @ steps", "PP 8")
    report(printed == degs[:3] and all(u - v == 5 for u, v in zip(degs, degs[1:])) and degs.index(17) == int(ns), "PP8 powers and steps", f"{printed}, {ns}")
except Exception as err:
    report(False, "PP8 powers", f"ERROR {err}")
check_chain("PP", 8, r"\[{}^9C_2\times\big(px^3\big)^7\times\big(-qx^{-2}\big)^2=@.\]", term(e, 17), 2)
try:
    (g,) = grab(PPA[8], r"so \(@\). Since \(p\ne0\)", "PP 8")
    lh, rh = g.split("=")
    report(same(tex(lh) - tex(rh), e.coeff(x, 27) - e.coeff(x, 17)), "PP8 equation", g)
    (g,) = grab(PPA[8], r"Since \(p\ne0\), \(@\). Since", "PP 8")
    lh, rh = g.split("=")
    pp_ = sp.Symbol("pp", positive=True)
    qq_ = sp.Symbol("qq", positive=True)
    sol_print = sp.solve(sp.Eq(tex(lh).subs({p: pp_, q: qq_}), tex(rh).subs({p: pp_, q: qq_})), pp_)
    sol_true = sp.solve(sp.Eq(e.coeff(x, 27), e.coeff(x, 17)).subs({p: pp_, q: qq_}), pp_)
    report(sol_print == sol_true == [6 * qq_], "PP8 p = 6q for positive p, q", f"{sol_print}, {sol_true}")
except Exception as err:
    report(False, "PP8 conclusion", f"ERROR {err}")

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
