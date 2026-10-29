"""Check of Lesson 14A (Factorial notation), tied to the printed HTML.

Reads the printed answers from workspace/build/y11ch14/a_14a.html (lesson
examples C1-C3, textbook homework, past-paper worked solutions) and the printed
results in the worked examples and concept boxes of l14a.html. In a template
'@' marks the printed value; each template must match exactly once in its
block, otherwise the item FAILS. Printed LaTeX is converted to an exact
expression (fractions.Fraction, factorials, powers, pronumerals n, k, r, x) and
compared with a value computed independently from the question:
  - counts by brute-force enumeration (itertools.permutations / product),
  - quotients, sums and identities of factorials from the original expression
    with math.factorial, at several whole-number values of n,
  - derivatives with sympy.diff, prime powers by repeated division,
  - Stirling's percentage error with math.
It also re-reads the question data printed in l14a.html (Exercise 14A Q2, Q3,
Q5, Q6, Q7 and the past-paper statements) so the answers match the questions as
printed, and checks the past-paper structure: marks add to the intro total, the
time is 1.5 x marks rounded to 5 minutes, numbering and source labels match in
both files, and the MC letter is the option with the computed value.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_14a.py
"""
import os
import re
import sys
from fractions import Fraction as Fr
from itertools import permutations, product, combinations
from math import factorial, sqrt, pi, e as E

import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH14_SRC", os.path.join(HERE, "..", "build", "y11ch14"))   # override only for mutation tests
FAILS = []
COUNT = [0]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    COUNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label + "  " + detail)
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- LaTeX -> exact Python
def _arg(s, i):
    if s[i] == "{":
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(s[j], 0)
            if depth == 0:
                return s[i + 1:j], j + 1
            j += 1
    return s[i], i + 1


def _conv(s):
    out, i = [], 0
    while i < len(s):
        if s.startswith(("\\dfrac", "\\tfrac", "\\frac"), i):
            i = s.index("frac", i) + 4
            a, i = _arg(s, i)
            b, i = _arg(s, i)
            out.append(f"(({_conv(a)})/({_conv(b)}))")
        elif s[i] == "\\":
            raise ValueError(f"unknown macro in {s!r}")
        elif s[i] in "{[":
            out.append("(")
            i += 1
        elif s[i] in "}]":
            out.append(")")
            i += 1
        elif s[i] == "^":
            out.append("^")
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def _clean(tex):
    s = tex
    for a in ("\\left", "\\right", "\\displaystyle", "&thinsp;", "&nbsp;"):
        s = s.replace(a, "")
    s = re.sub(r"\\text\{[^}]*\}", "", s)
    s = re.sub(r"\\[,!;]|\\ |\s|&", "", s)
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    return s


def tex_to_py(tex):
    s = _conv(_clean(tex))
    toks = re.findall(r"\d+|[A-Za-z]|\^|\S", s)
    # factorials: wrap the operand to the left of each '!'
    out = []
    for t in toks:
        if t != "!":
            out.append(t)
            continue
        if out and out[-1] == ")":
            depth, j = 0, len(out) - 1
            while True:
                depth += {")": 1, "(": -1}.get(out[j], 0)
                if depth == 0:
                    break
                j -= 1
            grp = out[j:]
            del out[j:]
            out += ["F"] + grp
        elif out and re.fullmatch(r"\d+|[nkrx]", out[-1]):
            v = out.pop()
            out += ["F", "(", v, ")"]
        else:
            raise ValueError(f"factorial with no operand in {tex!r}")
    res, prev = [], None
    for t in out:
        if prev is not None:
            left = re.fullmatch(r"\d+|[nkrx]|\)", prev)
            right = re.fullmatch(r"\d+|[nkrxF]|\(", t)
            if left and right:
                res.append("*")
        if re.fullmatch(r"[A-Za-z]", t) and t not in "nkrxF":
            raise ValueError(f"unknown letter {t!r} in {tex!r}")
        res.append(f"Fr({t})" if t.isdigit() else ("**" if t == "^" else t))
        prev = t
    return "".join(res)


def fact(v):
    v = Fr(v)
    if v.denominator != 1 or v < 0:
        raise ValueError(f"factorial of {v}")
    return Fr(factorial(int(v)))


def tex_eval(tex, **var):
    env = {"Fr": Fr, "F": fact, "__builtins__": {}}
    env.update({k: Fr(v) for k, v in var.items()})
    return Fr(eval(tex_to_py(tex), env))


# ---------------------------------------------------------------- blocks
ANS = read("a_14a.html")
LES = read("l14a.html")


def ans_blocks(text):
    # labels are kept with their maths by <span style="white-space:nowrap"> wrappers (layout only): strip them
    return {an.strip(): ab.replace('<span style="white-space:nowrap">', "").replace("</span>", "") for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S)}


A = ans_blocks(ANS)
sec = ANS.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_14a.html")
if ANS.count("{{ahead:Lesson 14A | Factorial notation}}") != 2 or not ANS.startswith("{{ahead:Lesson 14A | Factorial notation}}"):
    report(False, "answers headings", "{{ahead:Lesson 14A | Factorial notation}} must open the file and precede the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}
pps = LES.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l14a.html")
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
HW = LES.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
Q = {int(n): b for n, b in re.findall(r'<div class="q"><span class="q-num">(\d+)</span><div class="q-body">(.*?)(?=<div class="q"><span class="q-num">|$)', HW, re.S)}


def les_block(start, end):
    i = LES.find(start)
    j = LES.find(end, i + 1)
    if i < 0 or j < 0:
        raise LookupError(f"lesson block {start!r} not found")
    return LES[i:j]


def find(block, template):
    before, after = template.split("@")
    found = re.findall(re.escape(before) + r"(.+?)" + re.escape(after), block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times: {template!r}")
    return found[0]


NS = range(4, 10)          # whole-number sample values (all factorials below stay defined)


def check(label, block, template, truth, var=None, samples=None):
    """truth: a number, or a function of the variables in var (compared at the samples)."""
    try:
        tex = find(block, template)
        if var is None:
            got, exp = tex_eval(tex), Fr(truth)
            report(got == exp, label, f"printed {tex.strip()} = {got}, computed {exp}")
            return
        samples = samples or [(v,) for v in NS]
        bad = []
        for smp in samples:
            env = dict(zip(var, smp))
            g, e_ = tex_eval(tex, **env), Fr(truth(*smp))
            if g != e_:
                bad.append(f"{env}: {g} vs {e_}")
        report(not bad, label, f"printed {tex.strip()} (as a function of {', '.join(var)}, {len(samples)} samples)" + (f"  {bad[:2]}" if bad else ""))
    except Exception as ex:  # missing or unparsable value fails loudly
        report(False, label, f"ERROR {ex}")


def split_parts(block, letters):
    """Split '<b>a</b> ... <b>b</b> ...' into {letter: text}."""
    out = {}
    for i, L in enumerate(letters):
        a = block.index(f"<b>{L}</b>")
        b = block.index(f"<b>{letters[i + 1]}</b>", a) if i + 1 < len(letters) else len(block)
        out[L] = block[a + len(f"<b>{L}</b>"):b]
    return out


def last_math(s):
    """Value after the last '=' in the last \\( \\) of a part (or the whole math if no '=')."""
    m = re.findall(r"\\\((.+?)\\\)", s, re.S)
    if not m:
        return s.replace("&nbsp;", "").strip()
    return m[-1].split("=")[-1]


def perm_count(n, r=None):
    return sum(1 for _ in permutations(range(n), n if r is None else r))


x = sympy.Symbol("x")


def dsym(expr, k, xv):
    v = sympy.diff(expr, x, k).subs(x, sympy.Rational(xv))
    return Fr(str(sympy.nsimplify(v)))


XS = (Fr(3, 2), Fr(2), Fr(-5, 3))

# ================================================================ lesson concept boxes and worked examples
c1 = les_block("Concept 1:", "<!-- ============ Concept 2")
check("L concept: 5! evaluates to", c1, r"\qquad\text{(which evaluates to @).}", perm_count(5))
table = re.findall(r"\\\((\d+)!=(?:(\d+)\\times(\d+)!=)?([\d\\,]+)\\\)", c1[c1.index("<table"):c1.index("</table>")])
report(len(table) == 12, "L table count", f"{len(table)} entries 0! .. 11!")
for n_, a_, b_, v in table:
    n_, val = int(n_), int(v.replace("\\,", ""))
    ok = val == factorial(n_) and (not a_ or (int(a_) == n_ and int(b_) == n_ - 1))
    report(ok, f"L table {n_}!", f"printed {v} (recursive form {a_ or '-'} x {b_ or '-'}!), computed {factorial(n_)}")
we0 = les_block("<span class=\"tag\">Worked example</span>", "<!-- ============ Concept 2")
check("L WE queue of five", we0, r"5\times4\times3\times2\times1=5!=@.\]", perm_count(5))
check("L WE fifth derivative", we0, r"y^{(5)}&=5\times4\times3\times2\times1=5!=@.\end", dsym(x ** 5, 5, 1))
c2 = les_block("Concept 2:", "<!-- ============ Concept 3")
check("L Box 2 7!/4!", c2, r"=7\times6\times5=@.\]", Fr(factorial(7), factorial(4)))
check("L Box 2 (n+2)!", c2, r"With pronumerals, \((n+2)!=@\) and", lambda n: fact(n + 2), ("n",))
check("L Box 2 n!", c2, r"\) and \(n!=@\).</p>", lambda n: fact(n), ("n",))
we1 = les_block("Worked example 1</span>", "<!-- ============ Concept 3")
check("L WE1a", we1, r"&=10\times9\times8\\ &=@\end{aligned}", Fr(factorial(10), factorial(7)))
check("L WE1b", we1, r"{(n-1)!}\\ &=@\end{aligned}", lambda n: fact(n + 2) / fact(n - 1), ("n",))
try:
    tex = find(we1, r"\underbrace{@}_{r\text{ factors}}")
    ok = tex == "n(n-1)(n-2)\\cdots(n-r+1)"
    prod_ok = all(Fr(factorial(nn), factorial(nn - rr)) == Fr(sympy.prod([nn - i for i in range(rr)])) for nn in range(0, 12) for rr in range(0, nn + 1))
    report(ok and prod_ok, "L WE1c r factors", f"printed {tex}; n!/(n-r)! = product of the r factors n, n-1, ..., n-r+1 for all 0 <= r <= n <= 11")
except Exception as ex:
    report(False, "L WE1c r factors", f"ERROR {ex}")
c3 = les_block("Concept 3:", "<div class=\"ex demo\">")
check("L concept 3 1/8!", c3, r"=\dfrac{10\times9}{10\times9\times8!}=@\qquad", Fr(1, factorial(8)))
check("L concept 3 1/n!", c3, r"\qquad\dfrac{1}{n!}=@.\]</li>", lambda n: 1 / fact(n), ("n",))
check("L concept 3 8!-7!", c3, r"=(8-1)\times7!=@.\]", factorial(8) - factorial(7))
we2 = les_block("Worked example 2</span>", "<!-- ============ Homework")
check("L WE2a", we2, r"-\dfrac{1}{10!}\\ &=@\end{aligned}", Fr(1, factorial(8)) - Fr(1, factorial(10)))
check("L WE2b", we2, r"+\dfrac{1}{(n+1)!}\\ &=@\end{aligned}", lambda n: 1 / fact(n) + 1 / fact(n + 1), ("n",))

# ================================================================ lesson examples C1-C3 (answers)
for c in ("C1", "C2", "C3"):
    if c not in A:
        report(False, c, "answer block missing")
td1, yt1 = A["C1"].split("<b>Your turn.</b>")
check("C1 TD a 6!", td1, r"=6!=@\) &nbsp;", perm_count(6))
check("C1 TD b y4", td1, r"y^{(4)}=4\times3\times2\times1=4!=@\) &nbsp;", dsym(x ** 4, 4, 2))
check("C1 TD c 10!", td1, r"10!=10\times9!=@\) and", 10 * 362880)
check("C1 TD c 8!", td1, r"\dfrac{9!}{9}=@\)", Fr(362880, 9))
report(factorial(9) == 362880 and factorial(10) == 10 * 362880 and factorial(8) == 362880 // 9, "C1 given 9!", "9! = 362 880 as given in the lesson")
check("C1 YT a 7!", yt1, r"<b>a</b>&nbsp;\(7!=@\)", perm_count(7))
check("C1 YT b y'''", yt1, r"y'''=3\times2\times1=3!=@\) &nbsp;", dsym(x ** 3, 3, 2))
check("C1 YT c 8!", yt1, r"8!=8\times7!=@\) and", 8 * 5040)
check("C1 YT c 6!", yt1, r"\dfrac{7!}{7}=@\)", Fr(5040, 7))

C2Q = {"td": {"a": lambda n: Fr(factorial(9), factorial(6)), "b": lambda n: fact(n + 3) / fact(n),
              "c": lambda n: fact(n) / fact(n - 4), "d": lambda n: Fr(factorial(8), factorial(5) * factorial(3))},
       "yt": {"a": lambda n: Fr(factorial(11), factorial(8)), "b": lambda n: fact(n + 4) / fact(n + 1),
              "c": lambda n: fact(n) / fact(n - 3), "d": lambda n: Fr(factorial(9), factorial(6) * factorial(3))}}
C3Q = {"td": {"a": lambda n: Fr(1, factorial(7)) - Fr(1, factorial(9)), "b": lambda n: 1 / fact(n + 1) + 1 / fact(n + 2),
              "c": lambda n: factorial(10) - factorial(9), "d": lambda n: fact(n + 2) - fact(n + 1)},
       "yt": {"a": lambda n: Fr(1, factorial(6)) + Fr(1, factorial(8)), "b": lambda n: 1 / fact(n - 1) - 1 / fact(n),
              "c": lambda n: factorial(7) + factorial(5), "d": lambda n: fact(n) + fact(n - 1)}}
# the questions as printed in the lesson must be the ones the truths encode
LQ = {("C2", "td"): les_block("Cancelling by unrolling", "<div class=\"ex attempt\">"),
      ("C2", "yt"): les_block("<span class=\"ex-title\">Same method</span>", "<div class=\"ex worked\">"),
      ("C3", "td"): les_block("Common denominators, then a common factor", "<div class=\"ex attempt\">"),
      ("C3", "yt"): les_block("<span class=\"ex-title\">Same methods</span>", "<div class=\"ex worked\">")}
for c, qs in (("C2", C2Q), ("C3", C3Q)):
    td, yt = A[c].split("<b>Your turn.</b>")
    for who, blk in (("td", td), ("yt", yt)):
        parts = split_parts(blk, "abcd")
        qparts = dict(re.findall(r'<span class="pl">([a-d])</span>\\\((.+?)\\\)</span>', LQ[(c, who)]))
        for L in "abcd":
            lab = f"{c} {who.upper()} {L}"
            try:
                tex = last_math(parts[L])
                bad = [n for n in NS if tex_eval(tex, n=n) != Fr(qs[who][L](n))]
                qbad = [n for n in NS if tex_eval(qparts[L], n=n) != Fr(qs[who][L](n))]
                report(not bad and not qbad, lab, f"printed {tex} ; question {qparts[L]}" + (f"  FAIL at n={bad or qbad}" if bad or qbad else ""))
            except Exception as ex:
                report(False, lab, f"ERROR {ex}")

# ================================================================ textbook homework
def tb(qn, letters):
    if str(qn) not in A:
        raise LookupError(f"answer {qn} missing")
    return split_parts(A[str(qn)], letters)


def qparts(qn):
    return dict(re.findall(r'<span class="pl">([a-h])</span>\\\((.+?)\\\)</span>', Q[qn]))


# Q1: arrangements in a row, brute force for the small cases, box argument for the big ones
def boxes(n):
    out = 1
    for k in range(n, 0, -1):     # n choices for the first place, n - 1 for the next, ...
        out *= k
    return out


p1 = tb(1, "abcde")
for L, truth in zip("abcde", (perm_count(8), perm_count(4), perm_count(3), boxes(101), boxes(20))):
    try:
        tex = last_math(p1[L])
        report(tex_eval(tex) == truth, f"TB1{L}", f"printed {tex}, computed {truth if truth < 10**8 else str(truth)[:12] + '...'}")
    except Exception as ex:
        report(False, f"TB1{L}", f"ERROR {ex}")

# Q2, Q3: numbers; truths hardcoded from the textbook, and the printed questions re-read
f = factorial
TB23 = {2: [f(3), f(5), f(1), Fr(f(15), f(14)), Fr(f(10), f(8) * f(2)), Fr(f(15), f(13) * f(3)), Fr(f(12), f(3) * f(9)), Fr(f(8), f(4) * f(4))],
        3: [f(7), f(10), f(0), Fr(f(9), f(4)), Fr(f(8), f(3)), Fr(f(10), f(5) * f(3) * f(2)), Fr(f(15), f(3) * f(5) * f(9)), Fr(f(12), f(2) * f(3) * f(4) * f(5))]}
for qn, truths in TB23.items():
    pa, qp = tb(qn, "abcdefgh"), qparts(qn)
    for L, t in zip("abcdefgh", truths):
        try:
            got = int(re.sub(r"&thinsp;|&nbsp;|\s", "", pa[L]))
            qv = tex_eval(qp[L])
            report(got == t and qv == t, f"TB{qn}{L}", f"printed {got}, question {qp[L]} = {qv}, computed {t}")
        except Exception as ex:
            report(False, f"TB{qn}{L}", f"ERROR {ex}")

# Q4: derivatives of x^6
p4 = tb(4, "abcdefg")
for k, L in enumerate("abcdefg", start=1):
    check(f"TB4{L}", p4[L], r"\(@\)", lambda xv, k=k: dsym(x ** 6, k, xv), ("x",), [(v,) for v in XS])

# Q5, Q6, Q7: simplifications in n (question re-read from the lesson)
TB567 = {5: {"a": lambda n: fact(n) / fact(n - 1), "b": lambda n: n * fact(n - 1), "c": lambda n: n * fact(n - 1) / fact(n),
             "d": lambda n: fact(n + 1) / fact(n - 1), "e": lambda n: fact(n + 2) / fact(n), "f": lambda n: fact(n - 2) / fact(n),
             "g": lambda n: fact(n - 2) * fact(n - 1) / (fact(n) * fact(n - 3)), "h": lambda n: fact(n) * fact(n - 1) / fact(n + 1)},
         6: {"a": lambda n: f(8) - f(7), "b": lambda n: fact(n + 1) - fact(n), "c": lambda n: f(8) + f(6),
             "d": lambda n: fact(n + 1) + fact(n - 1), "e": lambda n: f(9) + f(8) + f(7), "f": lambda n: fact(n + 1) + fact(n) + fact(n - 1)},
         7: {"a": lambda n: 1 / fact(n) + 1 / fact(n - 1), "b": lambda n: 1 / fact(n) - 1 / fact(n + 1), "c": lambda n: 1 / fact(n + 1) - 1 / fact(n - 1)}}
for qn, truths in TB567.items():
    pa, qp = tb(qn, "".join(truths)), qparts(qn)
    for L, t in truths.items():
        try:
            tex = last_math(pa[L])
            bad = [n for n in NS if tex_eval(tex, n=n) != Fr(t(Fr(n)))]
            qbad = [n for n in NS if tex_eval(qp[L], n=n) != Fr(t(Fr(n)))]
            report(not bad and not qbad, f"TB{qn}{L}", f"printed {tex} ; question {qp[L]}" + (f"  FAIL at n={bad or qbad}" if bad or qbad else ""))
        except Exception as ex:
            report(False, f"TB{qn}{L}", f"ERROR {ex}")

# Q8: higher derivatives of x^n and 1/x (sympy), as functions of n, k, x
b8 = A.get("8", "")
a8, bb8 = b8.split("<b>b</b>") if "<b>b</b>" in b8 else ("", "")
NX = [(nn, xv) for nn in (3, 5, 7) for xv in XS]
check("TB8a i", a8, r"i \(@\) &nbsp; ii", lambda nn, xv: dsym(x ** nn, 1, xv), ("n", "x"), NX)
check("TB8a ii", a8, r"ii \(@\) &nbsp; iii", lambda nn, xv: dsym(x ** nn, 2, xv), ("n", "x"), NX)
check("TB8a iii", a8, r"iii \(@\) &nbsp; iv", lambda nn, xv: dsym(x ** nn, nn, xv), ("n", "x"), NX)
NKX = [(nn, kk, xv) for nn in (4, 6) for kk in range(0, nn + 1) for xv in XS[:2]]
check("TB8a iv", a8, r"\cdots(n-k+1)\,x^{n-k}=@\)", lambda nn, kk, xv: dsym(x ** nn, kk, xv), ("n", "k", "x"), NKX)
try:
    tex = find(a8, r"iv \(@=\dfrac")
    ok = tex == "n(n-1)(n-2)\\cdots(n-k+1)\\,x^{n-k}"
    report(ok, "TB8a iv product form", f"printed {tex} (k factors n, n-1, ..., n-k+1)")
except Exception as ex:
    report(False, "TB8a iv product form", f"ERROR {ex}")
for lab, tpl, k in (("i", r"i \(@\) &nbsp; ii", 1), ("ii", r"ii \(@\) &nbsp; iii", 2), ("iii", r"iii \(@\) &nbsp; iv", 5)):
    check(f"TB8b {lab}", bb8, tpl, lambda xv, k=k: dsym(1 / x, k, xv), ("x",), [(v,) for v in XS])
check("TB8b iv", bb8, r"iv \(@\)", lambda nn, xv: dsym(1 / x, nn, xv), ("n", "x"), [(nn, xv) for nn in range(1, 8) for xv in XS])

# Q9: sum of k x k!
check("TB9b", A.get("9", ""), r"<b>b</b>&nbsp;\(@\)", lambda nn: sum(kk * factorial(kk) for kk in range(1, int(nn) + 1)), ("n",), [(v,) for v in range(1, 10)])


# Q10: largest powers dividing 10! and 100! (repeated division)
def largest_power(base, N):
    v, m = 0, factorial(N)
    while m % base == 0:
        m //= base
        v += 1
    return v


b10 = A.get("10", "")
a10, bb10 = b10.split("<b>b</b>") if "<b>b</b>" in b10 else ("", "")
for blk, N, items in ((a10, 10, (("i", 2, r"i \(@\) &nbsp; ii"), ("ii", 10, r"ii \(@\) &nbsp; "))),
                      (bb10, 100, (("i", 2, r"i \(@\) &nbsp; ii"), ("ii", 5, r"ii \(@\) &nbsp; iii"), ("iii", 7, r"iii \(@\) &nbsp; iv"), ("iv", 13, r"iv \(@\)")))):
    for lab, p, tpl in items:
        try:
            tex = find(blk, tpl)
            m = re.fullmatch(r"(\d+)\^\{?(\d+)\}?", tex)
            ok = m and int(m.group(1)) == p and int(m.group(2)) == largest_power(p, N)
            report(bool(ok), f"TB10 {N}! {lab}", f"printed {tex}, computed {p}^{largest_power(p, N)}")
        except Exception as ex:
            report(False, f"TB10 {N}! {lab}", f"ERROR {ex}")

# Q12: k/(k+1)!, partial sums, closed form and limit
b12 = A.get("12", "")
try:
    p12 = split_parts(b12, "abcd")
    for L, truth in (("a", [Fr(k, factorial(k + 1)) for k in range(1, 6)]),
                     ("b", [sum(Fr(k, factorial(k + 1)) for k in range(1, nn + 1)) for nn in range(1, 6)])):
        tex = re.findall(r"\\\((.+?)\\\)", p12[L])[0]
        got = [tex_eval(t) for t in tex.split(",\\ ")]
        report(got == truth, f"TB12{L}", f"printed {[str(g) for g in got]}, computed {[str(t) for t in truth]}")
except Exception as ex:
    report(False, "TB12ab", f"ERROR {ex}")
check("TB12c S_n", b12, r"\(S_n=@\). The limit", lambda nn: sum(Fr(k, factorial(k + 1)) for k in range(1, int(nn) + 1)), ("n",), [(v,) for v in range(1, 12)])
S40 = sum(Fr(k, factorial(k + 1)) for k in range(1, 41))
check("TB12c limit", b12, r"The limit is @.<br>", 1)
report(0 < 1 - S40 < Fr(1, 10 ** 40), "TB12c limit numeric", f"1 - S_40 = {float(1 - S40):.3g}")
report(all(Fr(k, factorial(k + 1)) == Fr(1, factorial(k)) - Fr(1, factorial(k + 1)) for k in range(1, 30)), "TB12d identity", "k/(k+1)! = 1/k! - 1/(k+1)! for k = 1..29")
try:
    tex = find(b12, r"The sum can be written as \(@\).")
    terms = re.findall(r"\\left\((.+?)\\right\)", tex)
    first = [tex_eval(t) for t in terms[:-1]]
    last = terms[-1]
    ok = first == [Fr(k, factorial(k + 1)) for k in range(1, len(first) + 1)] and all(tex_eval(last, n=nn) == Fr(nn, factorial(nn + 1)) for nn in range(1, 9))
    report(ok, "TB12d collapsing terms", f"{len(terms)} bracketed terms; each equals k/(k+1)!")
except Exception as ex:
    report(False, "TB12d collapsing terms", f"ERROR {ex}")

# Q13: double factorials
even = 1
for k in range(2, 31, 2):
    even *= k
odd = 1
for k in range(1, 30, 2):
    odd *= k
b13 = A.get("13", "")
check("TB13a", b13, r"<b>a</b>&nbsp;\(@\) &nbsp;", even)
check("TB13b first", b13, r"<b>b</b>&nbsp;\(@\) or", odd)
check("TB13b second", b13, r"or \(@\) &nbsp;", odd)
check("TB13c", b13, r"<b>c</b>&nbsp;\(@\)", Fr(even, odd))


# Q14: Stirling's percentage error
def stirling_err(n):
    return (factorial(n) - sqrt(2 * pi) * n ** (n + 0.5) * E ** (-n)) / factorial(n) * 100


try:
    got = A["14"].strip()
    m = re.fullmatch(r"([\d.]+)%", got)
    report(bool(m) and abs(float(m.group(1)) - stirling_err(60)) <= 0.005, "TB14 60!", f"printed {got}, computed {stirling_err(60):.4f}%")
    for nn, tpl in ((3, "approximately @% for \\(3!\\)"), (10, "and @% for \\(10!\\)")):
        tex = find(Q[14], tpl)
        report(abs(float(tex) - stirling_err(nn)) <= 0.005, f"TB14 question {nn}!", f"printed {tex}%, computed {stirling_err(nn):.4f}%")
except Exception as ex:
    report(False, "TB14", f"ERROR {ex}")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 1 <= M <= 22, "lesson marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    if M < 15:
        print(f"NOTE     {M} marks is below 15: house rule 8 (too few clean 14A school questions), see the task report")
    report(T == 5 * round(1.5 * M / 5), "lesson time", f"{T} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for n_ in PPQ:
        sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[n_], re.S)]
        tot = int(re.search(r'<span class="mk">(\d+) marks?</span>', PPQ[n_]).group(1))
        if sub:
            report(sum(sub) == tot, f"PP{n_} part marks", f"parts {sub} sum {sum(sub)}, block {tot}")
        src_q = re.search(r"^(.*?)</span>", PPQ[n_]).group(1)
        src_a = re.search(r"^(.*?)</span>", PPA.get(n_, "")).group(1) if n_ in PPA else None
        report(src_q == src_a, f"PP{n_} source label", src_q)
        report(PPQ[n_].count('<div class="hint"><b>Hint:</b>') == 1, f"PP{n_} hint", "exactly one hint")
except Exception as ex:
    report(False, "lesson structure", f"ERROR {ex}")

# ---------------------------------------------------------------- PP 1  PIN, four of the digits 0-9, no repeats
pins = sum(1 for _ in permutations(range(10), 4))
check("PP1 count", PPA.get(1, ""), r"=\dfrac{10!}{6!}=@.\]", pins)
check("PP1 10!/6!", PPA.get(1, ""), r"10\times9\times8\times7=@=5040", pins)
check("PP1 option C", PPA.get(1, ""), r"Option (C), \(10\,000=@\)", sum(1 for _ in product(range(10), repeat=4)))
check("PP1 option B", PPA.get(1, ""), r"Option (B), 210, is \(@\)", sum(1 for _ in combinations(range(10), 4)))
try:
    opts = {k: int(v.replace("&nbsp;", "")) for k, v in re.findall(r"<span>\(([A-D])\) ([\d&nbsp;]+)</span>", PPQ[1])}
    letter = find(PPA[1], "<b>Answer (@).</b>")
    best = [k for k, v in opts.items() if v == pins]
    report(len(opts) == 4 and best == [letter], "PP1 MC letter", f"options {opts}; printed {letter}; option with {pins} is {best}")
except Exception as ex:
    report(False, "PP1 MC letter", f"ERROR {ex}")

# ---------------------------------------------------------------- PP 2  EPSILON beginning with P, ending with S
word = "EPSILON"
report(len(set(word)) == len(word), "PP2 distinct letters", word)
eps = sum(1 for p in set(permutations(word)) if p[0] == "P" and p[-1] == "S")
check("PP2 count", PPA.get(2, ""), r"\text{number of arrangements}=5!=@.\]", eps)
check("PP2 5!", PPA.get(2, ""), r"in \(@\) ways.</p>", eps)


# ---------------------------------------------------------------- PP 3, PP 4, PP 6  identities, every printed line
def aligned_lines(block):
    m = re.search(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", block, re.S)
    lines = [ln for ln in m.group(1).split("\\\\")]
    out = []
    for ln in lines:
        ln = ln.replace("\\text{LHS}", "").replace("=\\text{RHS}.", "").replace("=\\text{RHS}", "").strip()
        ln = ln.lstrip("&").lstrip("=")
        out.append(ln)
    return out


def identity(pp, lhs, rhs, q_tpl, ns):
    blk = PPA.get(pp, "")
    try:
        qtex = find(PPQ[pp], q_tpl)
        ql, qr = qtex.split("=")
        okq = all(tex_eval(ql, n=n) == lhs(n) and tex_eval(qr, n=n) == rhs(n) for n in ns)
        report(okq and all(lhs(n) == rhs(n) for n in ns), f"PP{pp} statement", f"question {qtex} holds for n in {list(ns)[0]}..{list(ns)[-1]}")
        lines = aligned_lines(blk)
        for i, ln in enumerate(lines):
            bad = [n for n in ns if tex_eval(ln, n=n) != lhs(n)]
            report(not bad, f"PP{pp} line {i + 1}", ln + (f"  FAIL at n={bad}" if bad else ""))
    except Exception as ex:
        report(False, f"PP{pp} identity", f"ERROR {ex}")


identity(3, lambda n: 1 / fact(n + 1) - (n + 1) / fact(n + 2), lambda n: 1 / fact(n + 2), r"\[@\]</div>", range(0, 10))
check("PP3 unrolled", PPA.get(3, ""), r"so \(\dfrac{1}{(n+1)!}=@\). Hence", lambda n: 1 / fact(n + 1), ("n",))
identity(4, lambda n: 1 / fact(n + 2) - (n + 1) / fact(n + 3), lambda n: 2 / fact(n + 3), r"Show that \(@\), where", range(0, 10))
check("PP4 unrolled", PPA.get(4, ""), r"so \(\dfrac{1}{(n+2)!}=@\). Hence", lambda n: 1 / fact(n + 2), ("n",))
identity(6, lambda n: (n + 1) * (fact(n) * n + fact(n - 1) * (2 * n - 1) + fact(n - 2) * (n - 1)), lambda n: fact(n + 2),
         r"Show that \(@\)</div>", range(2, 12))
check("PP6 n! n", PPA.get(6, ""), r"so \(n!\,n=@\). Also", lambda n: fact(n) * n, ("n",))
check("PP6 (n-2)!(n-1)", PPA.get(6, ""), r"Also \((n-2)!\,(n-1)=@\). Hence", lambda n: fact(n - 2) * (n - 1), ("n",))

# ---------------------------------------------------------------- PP 5  (n+2)! = 72 n!
sols = [n for n in range(0, 200) if factorial(n + 2) == 72 * factorial(n)]
check("PP5 answer", PPA.get(5, ""), r"Hence \(n=@\).</p>", sols[0] if len(sols) == 1 else -1)
report(sols == [7], "PP5 brute force", f"whole numbers 0..199 with (n+2)! = 72 n!: {sols}")
try:
    qtex = find(PPQ[5], r"Solve \(@\)</div>")
    ql, qr = qtex.split("=")
    report(all(tex_eval(ql, n=n) == fact(n + 2) and tex_eval(qr, n=n) == 72 * fact(n) for n in range(0, 9)), "PP5 statement", qtex)
    m = re.search(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", PPA[5], re.S)
    lines = [ln.replace("&", "").strip().rstrip(",") for ln in m.group(1).split("\\\\")]
    ref = lambda n: (n - 7) * (n + 10)
    for i, ln in enumerate(lines):
        l_, r_ = ln.split("=")
        d = lambda n: tex_eval(l_, n=n) - tex_eval(r_, n=n)
        ratio = {d(n) / ref(n) for n in (0, 1, 2, 3, 5, 9)}
        report(len(ratio) == 1 and 0 not in ratio, f"PP5 line {i + 1}", f"{ln}  (a nonzero multiple of (n-7)(n+10))")
    r1, r2 = re.search(r"so \\\(n=(-?\d+)\\\) or \\\(n=(-?\d+)\\\)", PPA[5]).groups()
    report({int(r1), int(r2)} == {7, -10} and all(ref(int(v)) == 0 for v in (r1, r2)), "PP5 roots", f"printed {r1}, {r2}")
    check("PP5 check 9!", PPA[5], r"Check: \(9!=@\) and", factorial(9))
    check("PP5 check 72x7!", PPA[5], r"72\times7!=72\times5040=@\).</p>", 72 * factorial(7))
except Exception as ex:
    report(False, "PP5 working", f"ERROR {ex}")

print(f"\n{COUNT[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{COUNT[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
