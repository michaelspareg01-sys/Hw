"""Check of Lesson 17B (Y12 Ext 1 Ch 17 pack): Binomial distributions.

The script reads the values PRINTED in workspace/build/ch17/a_17b.html (lesson examples, textbook
homework, past-paper worked solutions), in l17b.html (worked examples, the data inside the tutor
demos, your-turn items and questions, the simulation tables, the MC options) and in the SVG
figures svg/c17b_*.svg and svg/a17b_*.svg. Each value is found with a template ('@' marks the
printed text); a template must match exactly once in its block, otherwise the item FAILS.
Printed LaTeX ({}^nC_x, \\tfrac, \\dfrac, \\sqrt, powers, decimals with thin spaces) is turned
into an exact sympy number and compared with an independent computation:
  - distributions of small experiments are found by ENUMERATING outcomes (coins 2^n, dice 6^n,
    a 52-card deck, two dice), never from the formula; larger n use Fraction + math.comb,
    cross-checked by convolving n one-stage distributions;
  - means and variances are recomputed from the distribution itself (sum x P, sum x^2 P - mu^2)
    and compared with np and npq; the lemma is checked for every n <= 14;
  - simulation statistics are recomputed from the frequency tables printed in the lesson;
  - decimals are compared with the exact value rounded half-up (d.p. or s.f.);
  - inequalities for n, p and k are solved by search or with sympy;
  - SVG figures: column heights and dot heights are read from the SVG and must be proportional to
    the probabilities or relative frequencies (to 0.6% of the tallest).
It also checks the past-paper block: marks add to the intro total (15-22), time is 1.5 x marks
rounded to 5 minutes, part marks add to each question's marks, numbering and source labels match
in both files, one hint per question, and each MC letter is the only option equal to the value.

Exit status 1 if anything fails. Run: python3 workspace/checks/ch17_17b.py
"""
import itertools
import math
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, getcontext
from fractions import Fraction as F

import sympy as sp
from sympy.parsing.sympy_parser import (implicit_multiplication_application, parse_expr, rationalize,
                                        standard_transformations)

getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("CH17_SRC", os.path.join(HERE, "..", "build", "ch17"))   # override only for mutation tests
FAILS = []
NCHECK = [0]
n_, p_, k_ = sp.symbols("n p k")
SYMS = {"n": n_, "p": p_, "k": k_, "binomial": sp.binomial, "sqrt": sp.sqrt}
TR = standard_transformations + (implicit_multiplication_application, rationalize)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100] + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- independent probability tools
def enum_dist(n, p):
    """Distribution of the number of successes, by enumerating all 2^n S/F sequences."""
    d = [F(0)] * (n + 1)
    for seq in itertools.product((1, 0), repeat=n):
        pr = F(1)
        for s in seq:
            pr *= p if s else 1 - p
        d[sum(seq)] += pr
    return d


def conv_dist(n, p):
    d = [F(1)]
    for _ in range(n):
        e = [F(0)] * (len(d) + 1)
        for k, v in enumerate(d):
            e[k] += v * (1 - p)
            e[k + 1] += v * p
        d = e
    return d


def pmf(n, x, p):
    return math.comb(n, x) * F(p) ** x * (1 - F(p)) ** (n - x)


_CROSS = set()


def dist(n, p):
    p = F(p)
    d = [pmf(n, x, p) for x in range(n + 1)]
    if (n, p) not in _CROSS:
        other = enum_dist(n, p) if n <= 14 else conv_dist(n, p)
        report(other == d and sum(d) == 1, f"cross-check Bin({n}, {p})", "formula = " + ("enumeration" if n <= 14 else "convolution"))
        _CROSS.add((n, p))
    return d


def moments(d):
    mu = sum(x * v for x, v in enumerate(d))
    return mu, sum(x * x * v for x, v in enumerate(d)) - mu * mu


DIE = range(1, 7)


def dice_dist(n, faces):
    """Number of dice (of n) showing a face in `faces`, by enumerating 6^n outcomes."""
    d = [F(0)] * (n + 1)
    for fs in itertools.product(DIE, repeat=n):
        d[sum(f in faces for f in fs)] += F(1, 6 ** n)
    return d


# ---------------------------------------------------------------- printed LaTeX -> exact value
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
        elif t.startswith("\\NCR", i):
            u, i = _arg(t, i + 4)
            v, i = _arg(t, i)
            out.append(f" binomial({_conv(u)},{_conv(v)})")
        elif t.startswith("\\sqrt", i):
            u, i = _arg(t, i + 5)
            out.append(f" sqrt({_conv(u)})")
        elif t.startswith("\\times", i):
            out.append("*")
            i += 6
        elif t[i] == "^":
            u, i = _arg(t, i + 1)
            out.append(f"**({_conv(u)})")
        elif t[i] == "\\":
            raise ValueError(f"unknown macro in {t!r}")
        elif t[i] in "{}":
            out.append("(" if t[i] == "{" else ")")
            i += 1
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def clean(t):
    t = re.sub(r"<[^>]+>", "", t).replace("\\(", "").replace("\\)", "")
    t = re.sub(r"\{\}\^(\{[^{}]*\}|\w)C_(\{[^{}]*\}|\w)", r"\\NCR{\1}{\2}", t)
    t = re.sub(r"\\left|\\right|\\bigg|\\Big|\\big|\\qquad|\\quad|\\,|\\;|\\!|&nbsp;|&ensp;|\s", "", t)
    return t.rstrip(".,")


def tex(t):
    s = _conv(clean(t))
    s = re.sub(r"(?<![\w.])(\d+\.\d+)", r"Rational('\1')", s)
    return parse_expr(s, local_dict=dict(SYMS), transformations=TR)


def val(t):
    return sp.nsimplify(sp.expand_func(tex(t)).doit()) if "sqrt" in clean(t) else sp.expand_func(tex(t)).doit()


def exact(t):
    e = sp.expand_func(tex(t)).doit()
    if not e.is_Rational:
        raise ValueError(f"not rational: {t!r} -> {e}")
    return F(int(e.p), int(e.q))


def _dec(v):
    if isinstance(v, F):
        return Decimal(v.numerator) / Decimal(v.denominator)
    if isinstance(v, int):
        return Decimal(v)
    return Decimal(str(sp.N(v, 50)))


def rnd(v, places):
    q = Decimal(1).scaleb(-places)
    return str(_dec(v).quantize(q, rounding=ROUND_HALF_UP))


def sf(v, digits):
    d = _dec(v)
    return rnd(v, digits - 1 - d.adjusted())


def dec(t):
    return clean(t).replace("\\ldots", "")


# ---------------------------------------------------------------- HTML blocks
ans = read("a_17b.html")
les = read("l17b.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_17b.html")
report(ans.count("{{ahead:Lesson 17B | Binomial distributions}}") == 2, "answers headings", "{{ahead:Lesson 17B | ...}} twice")
report(parts[0].count('<div class="ans-sec">Lesson Examples</div>') == 1 and parts[0].count('<div class="ans-sec">Textbook Homework</div>') == 1
       and parts[0].index("Lesson Examples") < parts[0].index("Textbook Homework"), "answers sections", "Lesson Examples, Textbook Homework, then Past-Paper solutions")
BLK = {}
for mt in re.finditer(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts[0], re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
PPA = {int(k): v for k, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}
pps = les.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l17b.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
PPQ = {int(k): v for k, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
TQ = {k: v for k, v in re.findall(r'<div class="q"(?: style="[^"]*")?><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"|\{\{band|$)', hw, re.S)}
CON = {}
for k in range(1, 6):
    seg = teach.split(f"<!-- ============ Concept {k} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[k] = {"seg": seg, "demo": [b for kd, _, b in exs if kd == "demo"][0], "attempt": [b for kd, _, b in exs if kd == "attempt"][0],
              "worked": [b for kd, _, b in exs if kd == "worked"], "tags": [t for kd, t, _ in exs if kd == "worked"]}
    report([kd for kd, _, _ in exs][:3] == ["demo", "attempt", "worked"], f"Concept {k} blocks", "tutor demo, your turn, worked example(s)")
report([CON[k]["tags"] for k in range(1, 6)] == [["Worked example"], ["Worked example 6"], ["Worked example 7"], ["Worked example 8"], ["Worked example 9", "Worked example 10"]],
       "worked example tags", "the Bernoulli proof 'from the text' and Examples 6-10")
report(sorted(TQ, key=int) == ["1", "2", "3", "4", "5", "6", "8", "9", "10", "11", "14", "15"], "textbook question numbers", str(sorted(TQ, key=int)))
fb, rest = hw.split("{{band:D}}")
db, eb = rest.split("{{band:E}}")
report(hw.count("{{band:F}}") == 1 and re.findall(r'q-num">(\d+)', fb) == ["1", "2", "3", "4", "5", "6"]
       and re.findall(r'q-num">(\d+)', db) == ["8", "9", "10", "11"] and re.findall(r'q-num">(\d+)', eb) == ["14", "15"],
       "bands", "F: Q1-6 (Q7 omitted), D: Q8-11 (Q12 omitted), E: Q14d, Q15 (Q13, Q14a-c omitted), as the textbook bands")
report(re.findall(r'<span class="pl">(\w)</span>', TQ["14"]) == ["d"], "Q14 only part d", "")


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\&).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def ex_eq(block, where, template, *expected):
    label = f"{where} {template[:70]}"
    try:
        got = grab(block, template, where)
        ok = len(got) == len(expected) and all(sp.simplify(val(g) - sp.nsimplify(e if not isinstance(e, F) else sp.Rational(e.numerator, e.denominator))) == 0
                                               for g, e in zip(got, expected))
        report(ok, label, "printed " + " | ".join(got))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def approx(block, where, template, value, mode, k):
    label = f"{where} {template[:70]}"
    try:
        (g,) = grab(block, template, where)
        want = rnd(value, k) if mode == "dp" else sf(value, k)
        report(dec(g) == want, label, f"printed {dec(g)}, exact {float(sp.N(value)) if not isinstance(value, F) else float(value):.10g} -> {want}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def present(block, where, text):
    report(block.count(text) == 1, f"{where} data", f"{text[:80]!r} appears {block.count(text)} time(s)")


def num_in(block, where, template):
    (g,) = grab(block, template, where)
    return exact(g)


def R(f):
    return sp.Rational(f.numerator, f.denominator)


# ================================================================ Concept 1: notation, Bernoulli
c1 = CON[1]
for lab in ("2 Binomial and Bernoulli distributions",):
    present(c1["seg"], "Box 2", lab)
present(c1["seg"], "Bernoulli box", r"\[\mu=p\qquad\text{and}\qquad\sigma^2=pq,\]")
# the worked proof: recompute mean and variance of a two-value distribution symbolically
q_ = 1 - p_
we = c1["worked"][0]
present(we, "WE Bernoulli", r"&amp;=0\times q+1\times p\\&amp;=p.")
present(we, "WE Bernoulli", r"&amp;=(0^2\times q+1^2\times p)-p^2\\&amp;=p-p^2\\&amp;=p(1-p)\\&amp;=pq")
report(sp.expand((0 * q_ + 1 * p_)) == p_ and sp.expand((0 ** 2 * q_ + 1 * p_) - p_ ** 2 - p_ * q_) == 0, "WE Bernoulli algebra", "mu = p, sigma^2 = pq")
# demo / your turn
dm, at, A1 = c1["demo"], c1["attempt"], BLK["C1"]
dtur, atur = A1.split("<b>Your turn.</b>")
cards = [(r, s) for r in range(13) for s in "HDSC"]
spec = {"demo": [(F(1, 2), 9), (F(len([f for f in DIE if f in (5, 6)]), 6), 12), (F(sum(1 for c in cards if c[1] == "C"), 52), 1)],
        "turn": [(F(1, 2), 15), (F(1, 6), 10), (F(1, 6), 1)]}
present(dm, "C1 demo", "tossed 9 times"); present(dm, "C1 demo", "thrown 12 times"); present(dm, "C1 demo", "is a club, and 0 if it is not")
present(at, "C1 turn", "tossed 15 times"); present(at, "C1 turn", "thrown 10 times"); present(at, "C1 turn", "shows a six, and 0 if it does not")
for blk, key in ((dtur, "demo"), (atur, "turn")):
    got = re.findall(r"X\\sim B\((\d+),\\tfrac(\d)(\d)\)", blk)
    report([(F(int(a), int(b)), int(nn)) for nn, a, b in got] == spec[key], f"C1 {key} a: B(n, p)", str(got))
for blk, ablk, where in ((dm, dtur, "C1 demo"), (at, atur, "C1 turn")):
    p = num_in(blk, where, r"<b>b</b> \(Y\sim B(1,@)\)")
    d = enum_dist(1, p)
    mu, var = moments(d)
    for tmpl, v in ((r"\(\mu=@\)<br>", mu), (r"\(\sigma^2=@\)<br>", var)):
        try:
            (g,) = grab(ablk, tmpl, where)
            sides = [t for t in g.split("=") if t]
            report(len(sides) >= 2 and all(exact(t) == v for t in sides), f"{where} b {tmpl[3:9]} chain", g)
        except Exception as err:
            report(False, f"{where} b {tmpl}", f"ERROR {err}")
    try:
        (g,) = grab(ablk, r"\(\sigma=@\)", where)
        sides = re.split(r"=|\\doteq", g)
        ok = sp.simplify(val(sides[0]) - sp.sqrt(R(var))) == 0
        ok = ok and (dec(sides[-1]) == sf(sp.sqrt(R(var)), 3) if "doteq" in g else sp.simplify(val(sides[-1]) - sp.sqrt(R(var))) == 0)
        report(ok and mu == p and var == p * (1 - p), f"{where} b sigma", g)
    except Exception as err:
        report(False, f"{where} b sigma", f"ERROR {err}")

# ================================================================ Concept 2: mean and variance of B(n, p)
c2 = CON[2]
present(c2["seg"], "Lemma b", r"x(x-1)\times{}^nC_x=n(n-1)\times{}^{n-2}C_{x-2}")
present(c2["seg"], "Lemma a", r"x\times{}^nC_x=n\times{}^{n-1}C_{x-1}")
report(all(x * math.comb(n, x) == n * math.comb(n - 1, x - 1) for n in range(1, 15) for x in range(1, n + 1))
       and all(x * (x - 1) * math.comb(n, x) == n * (n - 1) * math.comb(n - 2, x - 2) for n in range(2, 15) for x in range(2, n + 1)),
       "lemma a and b for n <= 14", "")
ok = True
for n in range(1, 13):
    for p in (F(1, 10), F(1, 3), F(1, 2), F(4, 5)):
        d = enum_dist(n, p)
        mu, var = moments(d)
        exx1 = sum(x * (x - 1) * v for x, v in enumerate(d))
        ok = ok and mu == n * p and var == n * p * (1 - p) and exx1 == n * (n - 1) * p * p and exx1 + mu - mu * mu == var
report(ok, "E(X) = np, E(X(X-1)) = n(n-1)p^2, Var = npq by enumeration", "n = 1..12, four values of p")
present(c2["seg"], "Box 3", "3 Mean and variance of a binomial distribution")
present(c2["seg"], "Box 3", r"\[\mu=np\qquad\text{and}\qquad\sigma^2=npq\qquad\text{and}\qquad\sigma=\sqrt{npq}.\]")
# Worked example 6
we6 = c2["worked"][0]
n6, p6 = int(num_in(we6, "WE6", r"parameters \(n=@\)")), num_in(we6, "WE6", r"and \(p=@\).<br>")
d6 = dist(n6, p6)
mu6, var6 = moments(d6)
ex_eq(we6, "WE6", r"\mu&amp;=np\\&amp;=20\times0.1\\&amp;=@\end{aligned}", mu6)
ex_eq(we6, "WE6", r"&amp;=20\times0.1\times0.9\\&amp;=@\end{aligned}", var6)
approx(we6, "WE6", r"\sigma&amp;=\sqrt{1.8}\\&amp;\doteq@\end{aligned}", sp.sqrt(R(var6)), "dp", 3)
ex_eq(we6, "WE6", r"P(X=2)&amp;={}^{20}C_2\,p^2q^{18}\\&amp;=@\\&amp;\doteq", d6[2])
approx(we6, "WE6", r"\times(0.9)^{18}\\&amp;\doteq@.\end{aligned}", d6[2], "dp", 3)
s6 = sp.sqrt(R(var6))
try:
    lo, hi = grab(we6, r"&amp;=P(@\le X\le@)\\&amp;=P(X=1", "WE6")
    report(dec(lo) == rnd(R(mu6) - s6, 3) and dec(hi) == rnd(R(mu6) + s6, 3), "WE6 c interval", f"{lo}, {hi}")
except Exception as err:
    report(False, "WE6 c interval", f"ERROR {err}")
xs6 = [x for x in range(n6 + 1) if R(mu6) - s6 <= x <= R(mu6) + s6]
report(xs6 == [1, 2, 3], "WE6 c values in interval", str(xs6))
ex_eq(we6, "WE6", r"&amp;=@\\&amp;\qquad+1140", sum(d6[x] for x in xs6) - 1140 * F(1, 10) ** 3 * F(9, 10) ** 17)
report(math.comb(20, 1) == 20 and math.comb(20, 2) == 190 and math.comb(20, 3) == 1140, "WE6 coefficients 20, 190, 1140", "")
approx(we6, "WE6", r"\times(0.9)^{17}\\&amp;\doteq@.\end{aligned}", sum(d6[x] for x in xs6), "dp", 3)
# C2 demo / your turn
A2 = BLK["C2"]
a2d, a2t = A2.split("<b>Your turn.</b>")
for blk, ablk, where in ((c2["demo"], a2d, "C2 demo"), (c2["attempt"], a2t, "C2 turn")):
    n = int(num_in(blk, where, r"parameters \(n=@\)"))
    p = num_in(blk, where, r"and \(p=@\).<br>")
    d = dist(n, p)
    mu, var = moments(d)
    sd = sp.sqrt(R(var))
    try:
        g = grab(ablk, r"<b>a</b> \(\mu=np=@\), &ensp; \(\sigma^2=npq=@\), &ensp; \(\sigma=@\)<br>", where)
        report(exact(g[0].split("=")[-1]) == mu and exact(g[0].split("=")[0]) == mu and exact(g[1].split("=")[-1]) == var
               and exact(g[1].split("=")[0]) == var and sp.simplify(val(g[2].split("=")[-1]) - sd) == 0 and sp.simplify(val(g[2].split("=")[0]) - sd) == 0,
               f"{where} a", " | ".join(g))
    except Exception as err:
        report(False, f"{where} a", f"ERROR {err}")
    m = int(mu)
    ex_eq(ablk, where, r"<b>b</b> \(P(X=" + str(m) + r")=@\doteq", d[m])
    approx(ablk, where, r"\big)^{" + str(n - m) + r"}\doteq@\)<br>" if "big" in ablk.split("<b>b</b>")[1].split("<br>")[0] else r"(0.8)^{20}\doteq@\)<br>", d[m], "dp", 3)
    xs = [x for x in range(n + 1) if R(mu) - sd <= x <= R(mu) + sd]
    try:
        lo, hi = grab(ablk, r"=P(@\le X\le@)=", where)
        report([int(lo), int(hi)] == [xs[0], xs[-1]], f"{where} c whole values in interval", f"{lo}..{hi}")
        (g,) = grab(ablk, r"\le X\le" + hi + r")=@\doteq", where)
        e = tex(g).subs({sp.Symbol("p"): R(p), sp.Symbol("q"): 1 - R(p)})
        report(sp.nsimplify(e) == R(sum(d[x] for x in xs)), f"{where} c terms", g[:60])
        approx(ablk, where, r"\le X\le" + hi + r")=" + g + r"\doteq@\)<br>", sum(d[x] for x in xs), "dp", 3)
    except Exception as err:
        report(False, f"{where} c", f"ERROR {err}")
present(a2d, "C2 demo d", "25 multiple-choice questions, each with five options")
present(a2t, "C2 turn d", "a die is thrown 18 times, and \\(X\\) is the number of times it shows a 5 or a 6")
report(F(1, 5) == F(1, 5) and F(len([f for f in DIE if f >= 5]), 6) == F(1, 3), "C2 d models", "five options p = 1/5; a 5 or a 6 p = 1/3")

# ================================================================ Concept 3: conditions on mu and sigma
c3 = CON[3]
we7 = c3["worked"][0]
n7, p7 = int(num_in(we7, "WE7", r"parameters \(n=@\)")), num_in(we7, "WE7", r"and \(p=@\).<br>")
mu7, var7 = moments(dist(n7, p7))
ex_eq(we7, "WE7", r"&amp;=100\times\tfrac15\\&amp;=@,\end{aligned}", mu7)
ex_eq(we7, "WE7", r"&amp;=100\times\tfrac15\times\tfrac45\\&amp;=@,\end{aligned}", var7)
ex_eq(we7, "WE7", r"\sigma&amp;=\sqrt{16}\\&amp;=@.\end{aligned}", sp.sqrt(R(var7)))
nmin = next(n for n in range(1, 10 ** 5) if n * p7 * (1 - p7) < F(n * n, 10 ** 4))
ex_eq(we7, "WE7", r"\text{Hence}\quad n&amp;&gt;@,\quad", nmin - 1)
report(all(F(m * m, 10 ** 4) > m * p7 * (1 - p7) for m in (nmin, nmin + 5)) and not (F((nmin - 1) ** 2, 10 ** 4) > (nmin - 1) * p7 * (1 - p7)), "WE7 b by search", f"smallest n = {nmin}")
pp = sp.Symbol("pp")
r7 = sorted(sp.solve(100 * pp ** 2 - 100 * pp + 1, pp), key=float)
present(we7, "WE7", r"\(\Delta=9600=40^2\times6\)")
report(100 ** 2 - 4 * 100 * 1 == 9600 == 40 ** 2 * 6, "WE7 discriminant", "")
for g, r in zip(grab(we7, r"&amp;\doteq@&amp;&amp;\doteq@,\end{aligned}", "WE7"), r7):
    report(dec(g) == rnd(r, 4), "WE7 c root", f"{g} vs {sp.N(r)}")
for t, r in ((r"&amp;=\tfrac12-\tfrac15\sqrt6&amp;", r7[0]), (r"&amp;&amp;=\tfrac12+\tfrac15\sqrt6\\", r7[1])):
    present(we7, "WE7 c exact roots", t)
report(sp.simplify(r7[0] - (sp.Rational(1, 2) - sp.sqrt(6) / 5)) == 0, "WE7 c root form", str(r7))
present(we7, "WE7", "(roughly, less than 0.01)")
present(we7, "WE7", "(roughly, greater than 0.99)")
A3 = BLK["C3"]
a3d, a3t = A3.split("<b>Your turn.</b>")
for blk, ablk, where in ((c3["demo"], a3d, "C3 demo"), (c3["attempt"], a3t, "C3 turn")):
    n = int(num_in(blk, where, r"parameters \(n=@\)"))
    p = num_in(blk, where, r"and \(p=@\).<br>")
    pct = num_in(blk, where, r"less than @% of the number")
    bound = num_in(blk, where, r"the standard deviation is less than @? Can")
    mu, var = moments(dist(n, p))
    try:
        g = grab(ablk, r"<b>a</b> \(\mu=np=@\), &ensp; \(\sigma^2=npq=@\), &ensp; \(\sigma=@\)<br>", where)
        report(exact(g[0].split("=")[-1]) == mu and exact(g[1].split("=")[-1]) == var and exact(g[0].split("=")[0]) == mu and exact(g[1].split("=")[0]) == var
               and sp.simplify(val(g[2]) - sp.sqrt(R(var))) == 0, f"{where} a", " | ".join(g))
    except Exception as err:
        report(False, f"{where} a", f"ERROR {err}")
    nmin = next(m for m in range(1, 10 ** 5) if m * p * (1 - p) < (pct / 100 * m) ** 2)
    ex_eq(ablk, where, r"Hence \(n&gt;@\), because", nmin - 1)
    roots = sorted(sp.solve(n * pp * (1 - pp) - R(bound) ** 2, pp), key=float)
    try:
        g = grab(ablk, r"are \(p=@\), that is, \(p\doteq@\) and \(p\doteq@\)", where)
        e = g[0].split("=")
        pm = [tex(s.replace("\\pm", "+")) for s in e] + [tex(s.replace("\\pm", "-")) for s in e]
        ok = all(sp.simplify(sp.expand_func(x) - roots[1]) == 0 for x in pm[:len(e)]) and all(sp.simplify(sp.expand_func(x) - roots[0]) == 0 for x in pm[len(e):])
        report(ok and dec(g[1]) == rnd(roots[0], 4) and dec(g[2]) == rnd(roots[1], 4), f"{where} c roots", f"{g[0]} ; {g[1]}, {g[2]}")
        lo, hi = grab(ablk, r"(roughly, less than @). Yes: \(p\) can be increased to more than \(\tfrac12+\tfrac{1}{@", where)
        report(dec(lo) == rnd(roots[0], 3), f"{where} c rough lower", lo)
        (hi2,) = grab(ablk, r"(roughly, more than @).<br>", where)
        report(dec(hi2) == rnd(roots[1], 3), f"{where} c rough upper", hi2)
    except Exception as err:
        report(False, f"{where} c", f"ERROR {err}")
    mean_d = num_in(blk, where, r"has mean @ and variance")
    var_d = num_in(blk, where, r"and variance @. Find")
    sol = [(m, F(mean_d, m)) for m in range(1, 1000) if F(mean_d, m) <= 1 and m * F(mean_d, m) * (1 - F(mean_d, m)) == var_d]
    try:
        g = grab(ablk, r"<b>d</b> \(q=@\), so \(p=@\), and \(n=@\).", where)
        report(len(sol) == 1 and exact(g[0].split("=")[-1]) == 1 - sol[0][1] and exact(g[0].split("=")[1]) == 1 - sol[0][1]
               and exact(g[1]) == sol[0][1] and exact(g[2].split("=")[-1]) == sol[0][0], f"{where} d", f"{g} vs search {sol}")
    except Exception as err:
        report(False, f"{where} d", f"ERROR {err}")

# ================================================================ Concept 4: skewness
c4 = CON[4]
seg4 = c4["seg"]
mu20, var20 = moments(enum_dist(20, F(1, 2)))
present(seg4, "coins", r"\(\mu=np=10\)")
approx(seg4, "coins", r"\(\sigma=\sqrt{npq}=\sqrt5\doteq@\)", sp.sqrt(R(var20)), "dp", 3)
report(var20 == 5 and mu20 == 10, "coins mean 10, variance 5", "")
present(seg4, "coins", r"\[P(X=7)={}^{20}C_7\times\big(\tfrac12\big)^7\times\big(\tfrac12\big)^{13}={}^{20}C_{13}\times\big(\tfrac12\big)^{13}\times\big(\tfrac12\big)^7=P(X=13).\]")
report(math.comb(20, 7) == math.comb(20, 13), "20C7 = 20C13", "")
d16 = dist(20, F(1, 6))
mu16, var16 = moments(d16)
ex_eq(seg4, "die", r"with mean \(\mu=3\tfrac13\doteq3.333\) and standard deviation \(\sigma=@\doteq1.667\)", sp.sqrt(R(var16)))
report(mu16 == F(10, 3) and rnd(mu16, 3) == "3.333" and rnd(sp.sqrt(R(var16)), 3) == "1.667", "die mean 3 1/3 = 3.333, sd 1.667", "")
d56 = dist(20, F(5, 6))
report(moments(d56)[0] == F(50, 3) and rnd(moments(d56)[0], 3) == "16.667" and moments(d56)[1] == var16, "not-six: mean 16 2/3, same sd", "")
present(seg4, "not-six", r"\(\mu=16\tfrac23\doteq16.667\) and the same standard deviation \(\sigma=\tfrac53\doteq1.667\)")
report(all(d16[x] == d56[20 - x] for x in range(21)), "reflection in x = 10", "")
present(seg4, "reflection", r"P(7\text{ sixes})={}^{20}C_7\times\big(\tfrac16\big)^7\times\big(\tfrac56\big)^{13}={}^{20}C_{13}\times\big(\tfrac56\big)^{13}\times\big(\tfrac16\big)^7=P(13\text{ non-sixes})")
present(seg4, "Box 4", r"symmetric about \(x=\tfrac12n\)")
present(seg4, "Box 4", r"reflects the graph in \(x=\tfrac12n\)")
sds = [math.sqrt(48 * p * (1 - p)) for p in (0.5, 0.4, 0.3, 0.2, 0.1, 0.05)]
report(all(a > b for a, b in zip(sds, sds[1:])), "Box 4: sd decreases as p moves to 0", str([round(s, 3) for s in sds]))
we8 = c4["worked"][0]
dX, dY = dist(100, F(1, 2)), dist(100, F(1, 10))
vX, vY = moments(dX)[1], moments(dY)[1]
ex_eq(we8, "WE8", r"&amp;=100\times\tfrac12\times\tfrac12\\&amp;=@,\\", vX)
ex_eq(we8, "WE8", r"&amp;=100\times\tfrac{1}{10}\times\tfrac{9}{10}\\&amp;=@,\\", vY)
ex_eq(we8, "WE8", r"\text{so}\quad\sigma_X&amp;=@.\end", sp.sqrt(R(vX)))
ex_eq(we8, "WE8", r"\text{so}\quad\sigma_Y&amp;=@.\end", sp.sqrt(R(vY)))
present(we8, "WE8", r"\(\sigma_X:\sigma_Y=5:3\)")
report(sp.sqrt(R(vX)) / sp.sqrt(R(vY)) == sp.Rational(5, 3), "WE8 ratio 5:3", "")
A4 = BLK["C4"]
a4d, a4t = A4.split("<b>Your turn.</b>")
for blk, ablk, where in ((c4["demo"], a4d, "C4 demo"), (c4["attempt"], a4t, "C4 turn")):
    n = int(num_in(blk, where, r"both consist of @ Bernoulli trials"))
    py = num_in(blk, where, r'and for <span style="white-space:nowrap">\(Y\),</span> \(p=@\).<br>')
    vx, vy = moments(dist(n, F(1, 2)))[1], moments(dist(n, py))[1]
    sx, sy = sp.sqrt(R(vx)), sp.sqrt(R(vy))
    try:
        g = grab(ablk, r"\(\sigma_X^2=@\), so \(\sigma_X=@\). &ensp; \(\sigma_Y^2=@\), so \(\sigma_Y=@\). The ratio is \(\sigma_X:\sigma_Y=@:@\)", where)
        ok = exact(g[0].split("=")[-1]) == vx and exact(g[0].split("=")[0]) == vx and sp.simplify(val(g[1]) - sx) == 0
        ok = ok and exact(g[2].split("=")[-1]) == vy and exact(g[2].split("=")[0]) == vy and sp.simplify(val(g[3]) - sy) == 0
        ok = ok and sp.simplify(val(g[4]) / val(g[5]) - sx / sy) == 0
        report(ok, f"{where} a", " | ".join(g))
    except Exception as err:
        report(False, f"{where} a", f"ERROR {err}")
    present(ablk, where, rf"symmetric about \(x={n // 2}\)")
    present(ablk, where, rf"peak near \(\mu={int(n * py)}\)")
    pz = 1 - py
    dz = dist(n, pz)
    mz, vz = moments(dz)
    report(all(dz[x] == dist(n, py)[n - x] for x in range(n + 1)), f"{where} c Z is Y reflected", "")
    try:
        g = grab(ablk, r"\(Z\sim B(" + str(n) + r",@)\), so \(\mu=@\) and \(\sigma=@\)", where)
        report(exact(g[0]) == pz and exact(g[1].split("=")[-1]) == mz and exact(g[1].split("=")[0]) == mz
               and sp.simplify(val(g[2].split("=")[-1]) - sp.sqrt(R(vz))) == 0 and sp.simplify(val(g[2].split("=")[0]) - sp.sqrt(R(vz))) == 0, f"{where} c", " | ".join(g))
    except Exception as err:
        report(False, f"{where} c", f"ERROR {err}")
    present(ablk, where, rf"reflected in \(x={n // 2}\)")
try:
    (g,) = grab(a4t, r"(about \(@:1\))", "C4 turn")
    report(dec(g) == rnd(2 * sp.sqrt(3) / 3, 2), "C4 turn ratio decimal", g)
except Exception as err:
    report(False, "C4 turn ratio decimal", f"ERROR {err}")

# ================================================================ Concept 5: simulations
c5 = CON[5]


def table_rows(block):
    rows = {}
    for th, tds in re.findall(r"<tr><th[^>]*>(.*?)</th>(.*?)</tr>", block, re.S):
        rows.setdefault(clean(th), []).append([clean(t) for t in re.findall(r"<td[^>]*>(.*?)</td>", tds)])
    return rows


def sim_stats(fr):
    N = sum(fr)
    m = F(sum(x * v for x, v in enumerate(fr)), N)
    return N, m, F(sum(x * x * v for x, v in enumerate(fr)), N) - m * m


def check_theory(block, where, n, p, places, ptxt):
    """Probability table printed to `places` d.p. (book style: tiny values to their first digit)."""
    d = dist(n, p)
    rows = table_rows(block)
    try:
        xs = rows["x"][0]
        pr = rows["P(X=x)"][0]
        report(xs == [str(x) for x in range(n + 1)] and len(pr) == n + 1, f"{where} table x row", str(xs))
        for x, t in enumerate(pr):
            want = rnd(d[x], places)
            if t != want and F(t) != 0:                                # book prints 0.0002, 0.00002: one significant figure
                want = sf(d[x], 1)
            report(t == want or (F(t) == 0 and float(d[x]) < 5 * 10 ** -(places + 2)), f"{where} P(X={x})", f"printed {t}, exact {float(d[x]):.6g}")
    except Exception as err:
        report(False, f"{where} table", f"ERROR {err}")
    return d


def check_sim(qblock, ablock, where, mean_t, s_t, s_places=2):
    rq = table_rows(qblock)
    fr = [int(v) for v in rq["f"][0]]
    N, m, s2 = sim_stats(fr)
    ra = table_rows(ablock)
    got = ra["f_r"][-1]
    report(len(got) == len(fr) and all(F(g) == F(f, N) for g, f in zip(got, fr)), f"{where} relative frequencies", " ".join(got))
    approx(ablock, where, mean_t, m, "dp", 2)
    approx(ablock, where, s_t, sp.sqrt(R(s2)), "dp", s_places)
    return fr, N, m, s2


we9, we10 = c5["worked"]
present(we9, "WE9", "toss 10 coins and count the number of heads")
d9 = check_theory(we9, "WE9", 10, F(1, 2), 3, "")
m9, v9 = moments(d9)
present(we9, "WE9", rf"\mu=np={m9},\qquad\sigma^2=npq={float(v9)},\qquad\sigma=\sqrt{{2.5}}\doteq{rnd(sp.sqrt(R(v9)), 2)}.")
r9 = table_rows(we9)
fr9 = [int(v) for v in r9["f"][0]]
N9, mm9, s29 = sim_stats(fr9)
report(N9 == 100 and all(F(g) == F(f, 100) for g, f in zip(r9["f_r"][0], fr9)), "WE9 f_r = f/100", " ".join(r9["f_r"][0]))
approx(we9, "WE9", r"Calculation gives \(\bar x=@\)", mm9, "dp", 2)
approx(we9, "WE9", r"and \(s\doteq@\).", sp.sqrt(R(s29)), "dp", 2)
d10 = check_theory(we10, "WE10", 10, F(1, 6), 3, "")
m10, v10 = moments(d10)
present(we10, "WE10", rf"\mu=np={rnd(m10, 3)},\qquad\sigma^2=npq={rnd(v10, 3)},\qquad\sigma\doteq{rnd(sp.sqrt(R(v10)), 3)}.")
r10 = table_rows(we10)
fr10 = [int(v) for v in r10["f"][0]]
N10, mm10, s210 = sim_stats(fr10)
report(N10 == 100 and all(F(g) == F(f, 100) for g, f in zip(r10["f_r"][0], fr10)), "WE10 f_r = f/100", " ".join(r10["f_r"][0]))
approx(we10, "WE10", r"Calculation gives \(\bar x=@\)", mm10, "dp", 2)
approx(we10, "WE10", r"and \(s\doteq@\).", sp.sqrt(R(s210)), "dp", 2)
A5 = BLK["C5"]
a5d, a5t = A5.split("<b>Your turn.</b>")
for qb, ab, where, n, faces in ((c5["demo"], a5d, "C5 demo", 8, None), (c5["attempt"], a5t, "C5 turn", 8, (5, 6))):
    present(qb, where, "toss 8 coins and count the number of heads" if faces is None else "roll 8 dice and count the number of dice showing a 5 or a 6")
    d = enum_dist(n, F(1, 2)) if faces is None else dice_dist(n, faces)
    p = F(1, 2) if faces is None else F(1, 3)
    report(d == dist(n, p), f"{where} enumeration = B({n}, {p})", "")
    check_theory(ab, where, n, p, 3, "")
    mu, var = moments(d)
    try:
        g = grab(ab, r"so \(\mu=np=@\), &ensp; \(\sigma^2=npq=@\), &ensp; \(\sigma@\).", where)
        okm = (exact(g[0]) == mu) if faces is None else dec(g[0]) == rnd(mu, 3)
        okv = (exact(g[1]) == var) if faces is None else dec(g[1]) == rnd(var, 3)
        sg = g[2].lstrip("=").split("\\doteq")
        oks = dec(sg[-1]) == (rnd(sp.sqrt(R(var)), 2) if faces is None else rnd(sp.sqrt(R(var)), 3))
        if faces is None:
            oks = oks and sp.simplify(val(sg[0]) - sp.sqrt(R(var))) == 0
        report(okm and okv and oks, f"{where} a mean, variance, sd", " | ".join(g))
    except Exception as err:
        report(False, f"{where} a", f"ERROR {err}")
    fr, N, m, s2 = check_sim(qb, ab, where, r"{100}=@\) &ensp; and", r"-\bar x^2}=\sqrt{\dfrac{" + ("1846" if faces is None else "868") + r"}{100}-" + ("4.04" if faces is None else "2.62") + r"^2}\doteq@\)")
    try:
        g = grab(ab, r"\(\bar x=\dfrac{\sum xf}{\sum f}=\dfrac{@}{@}=", where)
        report(int(g[0]) == sum(x * v for x, v in enumerate(fr)) and int(g[1]) == N, f"{where} sum xf", str(g))
        g = grab(ab, r"-\bar x^2}=\sqrt{\dfrac{@}{@}-@^2}", where)
        report(int(g[0]) == sum(x * x * v for x, v in enumerate(fr)) and int(g[1]) == N and F(dec(g[2])) == m, f"{where} sum x^2 f", str(g))
    except Exception as err:
        report(False, f"{where} sums", f"ERROR {err}")


# ---------------------------------------------------------------- SVG figures: proportional heights
def svg_rect_heights(name):
    s = read(os.path.join("svg", name + ".svg"))
    return [float(h) for h in re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="([\d.]+)"', s)]


def prop_ok(got, want):
    if not got or len(got) != len(want):
        return False
    kmax = max(range(len(want)), key=lambda i: want[i])
    sc = got[kmax] / float(want[kmax])
    return all(abs(g - sc * float(w)) <= 0.006 * got[kmax] + 0.06 for g, w in zip(got, want))


for name, vals in (("c17b_ex9a", d9), ("c17b_ex10a", d10), ("a17b_d_th", dist(8, F(1, 2))), ("a17b_y_th", dist(8, F(1, 3))),
                   ("c17b_ex9b", [F(f, 100) for f in fr9]), ("c17b_ex10b", [F(f, 100) for f in fr10]),
                   ("a17b_d_sim", [F(int(v), 100) for v in table_rows(c5["demo"])["f"][0]]),
                   ("a17b_y_sim", [F(int(v), 100) for v in table_rows(c5["attempt"])["f"][0]])):
    nz = [v for v in vals if v > 0]
    report(prop_ok(svg_rect_heights(name), nz), f"SVG {name} column heights", f"{len(svg_rect_heights(name))} columns")
for name, n, p in (("c17b_coin20", 20, F(1, 2)), ("c17b_die20", 20, F(1, 6)), ("c17b_die20r", 20, F(5, 6))):
    s = read(os.path.join("svg", name + ".svg"))
    cy = [float(v) for v in re.findall(r'<circle cx="[\d.]+" cy="([\d.]+)"', s)]
    y0 = float(re.search(r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="\1"', s).group(1))
    report(len(cy) == n + 1 and prop_ok([y0 - c for c in cy], dist(n, p)), f"SVG {name} dot heights", f"{len(cy)} dots")
for name, p in (("c17b_q6", F(1, 4)), ("a17b_q6e", F(3, 4))):
    s = read(os.path.join("svg", name + ".svg"))
    pts = re.findall(r'<polyline points="([^"]+)"', s)[-1].split()
    ys = [float(t.split(",")[1]) for t in pts]
    y0 = float(re.search(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="[\d.]+" y2="\2" stroke="#1f2a37"', s).group(2))
    d = dist(48, p)
    report(len(ys) == 49 and prop_ok([y0 - y for y in ys], d), f"SVG {name} polygon of B(48, {p})", "")
    xs = [float(t.split(",")[0]) for t in pts]
    peak = max(range(49), key=lambda i: d[i])
    report(max(range(49), key=lambda i: -ys[i]) == peak, f"SVG {name} peak at x = {peak}", "")

# ================================================================ textbook homework answers
T, A = TQ, BLK
# Q1
present(T["1"], "Q1", "whether the result is less than five")
present(T["1"], "Q1", "a head on tossing an unfair coin is 0.4")
ex_eq(A["1"], "Q1b", r"less than five (\(n=10\), \(p=@\))", F(len([f for f in DIE if f < 5]), 6))
ex_eq(A["1"], "Q1d", r"(\(n=20\), \(p=@\))", 1 - F(4, 10))
ex_eq(A["1"], "Q1g", r"(\(n=50\), \(p=@\))", F(1, 100))
# Q2: ways and probabilities by enumerating 2^6 coin sequences
ways = [sum(1 for s in itertools.product("HT", repeat=6) if s.count("H") == x) for x in range(7)]
r2 = table_rows(A["2"])
try:
    report([int(v) for v in r2["Numberofways"][0]] == ways + [64], "Q2a ways", str(r2["Numberofways"][0]))
    report([exact(v) for v in r2["Probability"][0]] == [F(w, 64) for w in ways] + [1], "Q2a probabilities", "")
except Exception as err:
    report(False, "Q2a", f"ERROR {err}")
d2 = [F(w, 64) for w in ways]
m2, v2 = moments(d2)
present(A["2"], "Q2b", "<b>b</b> 3 heads")
report(max(range(7), key=lambda x: d2[x]) == 3, "Q2b mode", "")
try:
    g = grab(A["2"], r"<b>c</b> \(\mu=\sum xp=@\), &ensp; variance \(=\sum x^2p-\mu^2=@-@=@\)", "Q2")
    report(exact(g[0]) == m2 and F(g[1]) == sum(x * x * v for x, v in enumerate(d2)) and F(g[2]) == m2 ** 2 and F(g[3]) == v2, "Q2c", str(g))
    g = grab(A["2"], r"\(np=6\times\tfrac12=@\) and \(npq=6\times\tfrac12\times\tfrac12=@\)", "Q2")
    report(exact(g[0]) == m2 and exact(g[1]) == v2, "Q2d np, npq agree with the table", str(g))
except Exception as err:
    report(False, "Q2c/d", f"ERROR {err}")
# Q3
deck = [(r, s) for r in range(1, 14) for s in "HDSC"]
pc = F(sum(1 for r, s in deck if r >= 11), 52)
for part, d in (("a", enum_dist(5, F(1, 2))), ("b", dice_dist(5, (5, 6))), ("c", dist(5, pc))):
    blk = A["3"].split(f"<b>{part}</b>")[1].split("<b>")[0] if part != "c" else A["3"].split("<b>c</b>")[1]
    rows = table_rows(blk)
    mu, var = moments(d)
    try:
        pr = rows["P(X=x)"][0]
        if part == "c":
            report(pr == [rnd(v, 3) for v in d], f"Q3{part} table (3 d.p.)", " ".join(pr))
        else:
            report([exact(v) for v in pr] == d, f"Q3{part} table (exact)", " ".join(pr))
        mx = max(d)
        modes = [x for x in range(6) if d[x] == mx]
        (gm,) = grab(blk, r"mode \(=@\)", f"Q3{part}") if part == "c" else grab(blk, r"mode \(=@\) or", f"Q3{part}")
        report(int(gm) == modes[0] and (part == "c" or f"or {modes[-1]}," in blk) and len(modes) == (1 if part == "c" else 2), f"Q3{part} mode", f"{modes}")
        g = grab(blk, r"mean \(@\), &ensp; SD \(@\)", f"Q3{part}")
        if part == "c":
            report(dec(g[0].replace("\\doteq", "")) == rnd(mu, 3) and dec(g[1].replace("\\doteq", "")) == rnd(sp.sqrt(R(var)), 3), "Q3c mean, SD (3 d.p.)", str(g))
        else:
            report(exact(g[0].lstrip("=")) == mu and sp.simplify(val(g[1].lstrip("=")) - sp.sqrt(R(var))) == 0, f"Q3{part} mean, SD", str(g))
    except Exception as err:
        report(False, f"Q3{part}", f"ERROR {err}")
report(pc == F(3, 13), "Q3c court cards p = 12/52", "")
# Q4
nr = 24
pw = F(8, 20)
present(T["4"], "Q4", "any of the 24 meat raffles")
present(T["4"], "Q4", "buys 8 of the 20 tickets in each raffle")
d4 = dist(nr, pw)
m4, v4 = moments(d4)
try:
    g = grab(A["4"], r"The expected value is @ wins and the standard deviation is @.<br>", "Q4")
    report(F(g[0]) == m4 and F(g[1]) ** 2 == v4, "Q4a", str(g))
    (g,) = grab(A["4"], r"Larry’s result is @ standard deviations below", "Q4")
    report(F(g) == (m4 - 6) / F(g and grab(A["4"], r"standard deviation is @.<br>", "Q4")[0]), "Q4b", g)
except Exception as err:
    report(False, "Q4", f"ERROR {err}")
# Q5: at least two sixes with 6, 12, 24 dice
for lab, nd, tmpl in (("a", 6, r"<b>a</b> @ (about @%); \(\text{E}(X)=@\), \(\sigma\doteq@\)"),
                      ("b(i)", 12, r"(i) @ (about @%); \(\text{E}(X)=@\), \(\sigma\doteq@\)"),
                      ("b(ii)", 24, r"(ii) @ (about @%); \(\text{E}(X)=@\), \(\sigma\doteq@\)")):
    d = dice_dist(nd, (6,)) if nd == 6 else dist(nd, F(1, 6))
    pv = 1 - d[0] - d[1]
    mu, var = moments(d)
    try:
        g = grab(A["5"], tmpl, "Q5")
        report(g[0] == rnd(pv, 3) and g[1] == rnd(pv * 100, 0).split(".")[0] and F(g[2]) == mu and g[3] == rnd(sp.sqrt(R(var)), 2), f"Q5{lab}", str(g))
    except Exception as err:
        report(False, f"Q5{lab}", f"ERROR {err}")
# Q6
d6q = dist(48, F(1, 4))
m6q, v6q = moments(d6q)
present(T["6"], "Q6", r"\(n=48\) and \(p=0.25\)")
try:
    g = grab(A["6"], r"<b>b</b> mean @, standard deviation @<br>", "Q6")
    report(F(g[0]) == m6q and F(g[1]) ** 2 == v6q, "Q6b", str(g))
    g = grab(A["6"], r"The mode is @, which has a probability of about @.<br>", "Q6")
    mode = max(range(49), key=lambda x: d6q[x])
    report(int(g[0]) == mode and g[1] == rnd(d6q[mode], 2), "Q6c", f"{g}, exact P = {float(d6q[mode]):.4f}")
    g = grab(A["6"], r"bounded by \([@,@]\)", "Q6")
    sd = sp.sqrt(R(v6q))
    report([F(g[0]), F(g[1])] == [m6q - 2 * F(int(sd)), m6q + 2 * F(int(sd))] and sd == int(sd), "Q6d", str(g))
    present(A["6"], "Q6", "reflected horizontally in \\(x=24\\)")
    present(A["6"], "Q6a", "right skewed (positively)")
except Exception as err:
    report(False, "Q6", f"ERROR {err}")
# Q8
d8, d8b = dist(48, F(1, 4)), dist(100, F(1, 5))
m8, v8 = moments(d8)
m8b, v8b = moments(d8b)
try:
    (g,) = grab(A["8"], r"<b>a</b> \(\text{E}(X)=@\).", "Q8")
    report(F(g) == m8, "Q8a", g)
    g = grab(A["8"], r"<b>b</b> @ &ensp; <b>c</b> @ &ensp; <b>d</b> \(\text{E}(Y)=@\), \(\sigma=@\)<br>", "Q8")
    report(F(g[0]) ** 2 == v8 and F(g[1]) == (24 - m8) / F(g[0]) and F(g[2]) == m8b and F(g[3]) ** 2 == v8b, "Q8b-d", str(g))
    present(A["8"], "Q8e", "she is five standard deviations above the mean")
    report((40 - m8b) / 4 == 5, "Q8e five", "")
    present(A["8"], "Q8f", "75% is 36 out of 48, which is 8 standard deviations above the mean. 60% is 60 out of 100, which is 10 standard deviations")
    report((F(75, 100) * 48 - m8) / 3 == 8 and (F(60, 100) * 100 - m8b) / 4 == 10, "Q8f 8 and 10", "")
except Exception as err:
    report(False, "Q8", f"ERROR {err}")
# Q9
present(T["9"], "Q9", "Team A runs a trial with 50 patients, of whom 45 show improvement")
present(T["9"], "Q9", "Team B runs a trial with 90 patients, of whom 74 show improvement")
for team, n, got in (("A", 50, 45), ("B", 90, 74)):
    mu, var = moments(dist(n, F(7, 10)))
    sd = sp.sqrt(R(var))
    try:
        g = grab(A["9"], rf"Team {team}: \(\mu=@\), \(\sigma\doteq@\), and {got} is about \(@\sigma\)", "Q9")
        report(F(g[0]) == mu and g[1] == rnd(sd, 2) and g[2] == rnd((got - R(mu)) / sd, 2), f"Q9 team {team}", str(g))
    except Exception as err:
        report(False, f"Q9 team {team}", f"ERROR {err}")
present(A["9"], "Q9", "Thus Team A’s changes")
# Q10
d10q = dist(100, F(15, 100))
m10q, v10q = moments(d10q)
s10 = sp.sqrt(R(v10q))
xs10 = [x for x in range(101) if R(m10q) - s10 / 2 <= x <= R(m10q) + s10 / 2]
try:
    g = grab(A["10"], r"mean \(=@\), standard deviation \(\doteq@\)<br>", "Q10")
    report(F(g[0]) == m10q and g[1] == rnd(s10, 2), "Q10a", str(g))
    present(A["10"], "Q10b", "the probability of 14, 15 or 16 people")
    report(xs10 == [14, 15, 16], "Q10b values", str(xs10))
    g = grab(A["10"], r"This is about @ (@%).", "Q10")
    pv = sum(d10q[x] for x in xs10)
    report(g[0] == rnd(pv, 3) and g[1] == rnd(pv * 100, 1), "Q10b probability", f"{g}, exact {float(pv):.6f}")
except Exception as err:
    report(False, "Q10", f"ERROR {err}")
# Q11
try:
    (g,) = grab(A["11"], r"<b>a</b> \(\sigma^2=@\)", "Q11")
    sides = g.split("=")
    report(all(sp.expand(tex(s) - n_ * p_ * (1 - p_)) == 0 for s in sides), "Q11a quadratic", g)
    vmax = sp.maximum(n_ * p_ * (1 - p_), p_, sp.Interval(0, 1)) if False else (n_ * p_ * (1 - p_)).subs(p_, sp.Rational(1, 2))
    crit = sp.solve(sp.diff(n_ * p_ * (1 - p_), p_), p_)
    present(A["11"], "Q11d", r"at \(p=\tfrac12\), where \(\sigma^2=n\times\tfrac12\times\tfrac12=\tfrac n4\)")
    report(crit == [sp.Rational(1, 2)] and sp.simplify(vmax - n_ / 4) == 0, "Q11d vertex", str(crit))
    report(sp.simplify((n_ * p_ * (1 - p_)).subs(p_, 1 - p_) - n_ * p_ * (1 - p_)) == 0, "Q11b symmetry p -> 1 - p", "")
except Exception as err:
    report(False, "Q11", f"ERROR {err}")
s = read(os.path.join("svg", "a17b_q11.svg"))
pts = [tuple(map(float, t.split(","))) for t in [m for m in re.findall(r'<path d="M([^"]+)"', s) if " L" in m][0].replace(" L", " ").split()]
x0, xe = pts[0][0], pts[-1][0]
yb = pts[0][1]
top = min(pts, key=lambda t: t[1])
report(abs(pts[-1][1] - yb) < 0.2 and abs((top[0] - x0) / (xe - x0) - 0.5) < 0.011 and
       all(abs((yb - y) - (yb - top[1]) * 4 * ((x - x0) / (xe - x0)) * (1 - (x - x0) / (xe - x0))) < 0.3 for x, y in pts),
       "SVG a17b_q11 parabola, vertex at p = 1/2", f"{len(pts)} points")
# Q15: geometric distribution mean by summing the series
ok = True
for pg in (F(1, 20), F(1, 3), F(1, 2), F(4, 5)):
    part = sum(x * pg * (1 - pg) ** (x - 1) for x in range(1, 1500))      # partial sums of p + 2pq + 3pq^2 + ...
    ok = ok and abs(float(part) - float(1 / pg)) < 1e-9
    probs = [pg * (1 - pg) ** (x - 1) for x in range(1, 6)]
    first = [pg if x == 1 else (1 - pg) ** (x - 1) * pg for x in range(1, 6)]     # x - 1 failures then a success
    ok = ok and probs == first
report(ok, "Q15a geometric mean = 1/p (partial sums, four values of p)", "")
present(A["15"], "Q15a", r"(iii) \(\mu=\dfrac1p\)")
try:
    g = grab(A["15"], r"\(p=\tfrac{1}{@}\), thus the mean waiting time is \(\mu=\dfrac1p=@\) time periods, or \(5\times20=@\) minutes", "Q15")
    present(T["15"], "Q15b", "with 20 patients waiting")
    present(T["15"], "Q15b", "Every 5 minutes")
    report(int(g[0]) == 20 and int(g[1]) == 20 and int(g[2]) == 100, "Q15b", str(g))
except Exception as err:
    report(False, "Q15b", f"ERROR {err}")
report(set(BLK) == {"C1", "C2", "C3", "C4", "C5"} | {"1", "2", "3", "4", "5", "6", "8", "9", "10", "11", "14", "15"}, "answer blocks", f"{sorted(BLK, key=lambda t: (len(t), t))}")

# ================================================================ past papers
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(v) for v in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    TT, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M} (house rule: 15-22)")
    report(TT == 5 * round(1.5 * M / 5), "PP time", f"{TT} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)) and len(marks) == len(PPQ), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for k in PPQ:
        subs = [int(s) for s in re.findall(r'<span class="mk">(\d)</span></div>', PPQ[k])]
        if subs:
            report(sum(subs) == marks[k - 1], f"PP{k} part marks", f"{subs} = {marks[k - 1]}")
        sq = re.search(r"^(.*?)</span><span class=\"mk\">", PPQ[k], re.S).group(1)
        sa = re.search(r"^(.*?)</span></div>", PPA[k], re.S).group(1)
        report(sq == sa, f"PP{k} source label", re.sub("<[^>]+>|&nbsp;", " ", sq)[:90])
        report(PPQ[k].count('<div class="hint">') == 1, f"PP{k} hint", "exactly one hint")
        hint = re.search(r'<div class="hint"><b>Hint:</b> (.*?)</div>', PPQ[k]).group(1)
        bad = re.search(r"\d|complement|list|tree|compare|worked example|start with|write|in terms of|whole number|rule of thumb|think of", re.sub(r"\\\(.*?\\\)|Box \d", "", hint), re.I)
        report(hint.endswith("?") and not bad, f"PP{k} hint is a starting question (no value, step or technique)", hint)
except Exception as err:
    report(False, "PP structure", f"ERROR {err}")


def mc_text(block):
    return dict(re.findall(r"<span>([A-D])\.&ensp;(.+?)</span>", block))


# PP1: 12 trials, p = 0.7
nP, pP = int(num_in(PPQ[1], "PP1", "the number of successes in @ independent")), num_in(PPQ[1], "PP1", r"is \(p=@\) in each trial")
mu, var = moments(dist(nP, pP))
opts = {L: tuple(F(v) for v in re.findall(r"is ([\d.]+)", t)) for L, t in mc_text(PPQ[1]).items()}
good = [L for L, (a, b) in opts.items() if a == mu and b == var]
report(len(opts) == 4 and good == ["B"] and "<b>Answer B.</b>" in PPA[1], "PP1 MC letter", f"{good}")
present(PPA[1], "PP1", rf"\mu=np=12\times0.7={float(mu)}\qquad\text{{and}}\qquad\sigma^2=npq=12\times0.7\times0.3={float(var)}.")
report(rnd(sp.sqrt(R(var)), 2) == "1.59", "PP1 1.59 = sqrt(2.52)", "")
# PP2
mu = moments(dist(15, F(29, 100)))[0]
opts = {L: F(clean(t)) for L, t in mc_text(PPQ[2]).items()}
good = [L for L, v in opts.items() if v == mu]
report(good == ["C"] and "<b>Answer C.</b>" in PPA[2], "PP2 MC letter", f"mean {mu}: {good}")
present(PPA[2], "PP2", r"\[\mu=np=15\times0.29=4.35.\]")
report(15 * F(71, 100) == F(1065, 100), "PP2 10.65 = 15 x 0.71", "")
# PP3: find (n, p) with np = 225 and npq = 144 by search over n
mean3, var3 = num_in(PPQ[3], "PP3", "The mean value of \\(X\\) is @ and"), num_in(PPQ[3], "PP3", "variance of \\(X\\) is @. What")
sol = [(n, F(mean3, n)) for n in range(1, 5000) if F(mean3, n) <= 1 and n * F(mean3, n) * (1 - F(mean3, n)) == var3]
opts = {L: F(clean(t)) for L, t in mc_text(PPQ[3]).items()}
good = [L for L, v in opts.items() if sol and v == sol[0][1]]
report(len(sol) == 1 and good == ["D"] and "<b>Answer D.</b>" in PPA[3], "PP3 MC letter", f"(n, p) = {sol}, {good}")
ex_eq(PPA[3], "PP3", r"\[q=\frac{144}{225}=@,\qquad", 1 - sol[0][1])
ex_eq(PPA[3], "PP3", r"\text{so}\qquad p=1-0.64=@.\]", sol[0][1])
ex_eq(PPA[3], "PP3", r"(Also \(n=225\div0.36=@\)", sol[0][0])
# PP4
mu, var = moments(dist(10000, F(8, 10))) if False else (10000 * F(8, 10), 10000 * F(8, 10) * F(2, 10))
report(sum(x * pmf(200, x, F(8, 10)) for x in range(201)) == 200 * F(8, 10), "PP4 np check (n = 200 by summation)", "")
ex_eq(PPA[4], "PP4", r"<b>(i)</b> \(E(X)=np=10\,000\times0.8=@\)</p>", mu)
ex_eq(PPA[4], "PP4", r"\(\text{Var}(X)=npq=10\,000\times0.8\times0.2=@\)", var)
ex_eq(PPA[4], "PP4", r"is \(\sigma=\sqrt{1600}=@\)", sp.sqrt(R(var)))
present(PPQ[4], "PP4", "cures a disease is 0.8. The drug is administered to 10&nbsp;000 patients")
# PP5: two dice, sum 7
p7 = F(sum(1 for a in DIE for b in DIE if a + b == 7), 36)
ex_eq(PPQ[5], "PP5", r"the probability of a sum of 7 is \(p=@\)", p7)
d = dist(30, p7)
mu, var = moments(d)
ex_eq(PPA[5], "PP5", r"\text{E}(X)=np=30\times\tfrac16=@\qquad", mu)
ex_eq(PPA[5], "PP5", r"=30\times\tfrac16\times\tfrac56=@\ (", var)
approx(PPA[5], "PP5", r"\ (\doteq@).\]", var, "dp", 2)
# PP6
pS = num_in(PPQ[6], "PP6", "In a certain school, @% of Year 12")
report(pS / 100 < F(1, 2), "PP6 p < 1/2", str(pS / 100))
present(PPA[6], "PP6", "the distribution is positively skewed (skewed to the right)")
ex_eq(PPA[6], "PP6", r"Extension 1 is \(p=@\). Since", pS / 100)
# PP7: mean = 2 sd with p = 0.2: search n
p7k = num_in(PPQ[7], "PP7", r"\(X\sim Bin(n,@)\)")
sol = [n for n in range(1, 2000) if (n * p7k) ** 2 == 4 * n * p7k * (1 - p7k)]
opts = {L: int(clean(t)) for L, t in mc_text(PPQ[7]).items()}
good = [L for L, v in opts.items() if v in sol]
report(sol == [16] and good == ["D"] and "<b>Answer D.</b>" in PPA[7], "PP7 MC letter", f"n = {sol}, {good}")
present(PPA[7], "PP7", r"(Check: the mean is 3.2 and the standard deviation is \(\sqrt{2.56}=1.6\).)")
report(16 * p7k == F(32, 10) and 16 * p7k * (1 - p7k) == F(256, 100), "PP7 check values", "")
# PP8: 30 coins
d = dist(30, F(1, 2))
mu, var = moments(d)
sd = sp.sqrt(R(var))
ex_eq(PPA[8], "PP8", r"so \(\mu=np=@\), \(\sigma^2", mu)
ex_eq(PPA[8], "PP8", r"\times\tfrac12\times\tfrac12=@\) and", var)
approx(PPA[8], "PP8", r"\(\sigma=\sqrt{7.5}\doteq@\).</p>", sd, "dp", 3)
try:
    lo, hi = grab(PPA[8], r"&amp;=P(@\le X\le@)\\", "PP8")
    report(dec(lo) == rnd(R(mu) - sd, 3) and dec(hi) == rnd(R(mu) + sd, 3), "PP8 interval", f"{lo}, {hi}")
except Exception as err:
    report(False, "PP8 interval", f"ERROR {err}")
xs = [x for x in range(31) if R(mu) - sd <= x <= R(mu) + sd]
present(PPA[8], "PP8", r"P(X=13,\,14,\,15,\,16\text{ or }17)")
report(xs == [13, 14, 15, 16, 17], "PP8 values", str(xs))
ex_eq(PPA[8], "PP8", r"&amp;=@\\&amp;\doteq0.638", sum(d[x] for x in xs))
approx(PPA[8], "PP8", r"\\&amp;\doteq@\end{aligned}", sum(d[x] for x in xs), "dp", 3)
# PP9
mu9, var9 = num_in(PPQ[9], "PP9", r"\(\mu=@\) and"), num_in(PPQ[9], "PP9", r"\(\sigma^2=@\)")
sol = [(n, F(mu9, n)) for n in range(1, 2000) if F(mu9, n) <= 1 and n * F(mu9, n) * (1 - F(mu9, n)) == var9]
report(len(sol) == 1 and sol[0] == (18, F(2, 3)), "PP9 (n, p) by search", str(sol))
ex_eq(PPA[9], "PP9", r"\qquad q=@,\qquad", 1 - sol[0][1])
ex_eq(PPA[9], "PP9", r"\text{so}\qquad p=1-\tfrac13=@.\]", sol[0][1])
ex_eq(PPA[9], "PP9", r"so \(n=12\div\tfrac23=@\).", sol[0][0])
present(PPA[9], "PP9", "a number greater than 2 (that is, 3, 4, 5 or 6, with probability \\(\\tfrac46=\\tfrac23\\) on each roll)")
report(F(len([f for f in DIE if f > 2]), 6) == sol[0][1], "PP9 (iii) die event has p = 2/3", "")
d = dist(18, sol[0][1])
ex_eq(PPA[9], "PP9", r"P(X=4)=@=\frac", d[4])
ex_eq(PPA[9], "PP9", r"\big)^{14}=@\doteq", d[4])
approx(PPA[9], "PP9", r"}{3^{18}}\doteq@.\]", d[4], "sf", 3)
# PP10: k yellow marbles
ex_eq(PPA[10], "PP10", r"so \(P(\text{blue})=@\).", F(3) / (8 + k_) if False else sp.Rational(3) / (8 + k_))
try:
    (g,) = grab(PPA[10], r"\frac{5+k}{8+k}=@.\]", "PP10")
    report(sp.simplify(tex(g) - 4 * 3 / (8 + k_) * (5 + k_) / (8 + k_)) == 0, "PP10 Var(X) formula", g)
except Exception as err:
    report(False, "PP10 Var", f"ERROR {err}")
present(PPA[10], "PP10", r"k^2+k-11&amp;&gt;0.")
report(sp.expand(sp.Rational(5, 4) * (sp.Rational(8, 10) * (8 + k_) ** 2 - 12 * (5 + k_)) - (k_ ** 2 + k_ - 11)) == 0, "PP10 quadratic", "")
rts = sorted(sp.solve(k_ ** 2 + k_ - 11, k_), key=float)
try:
    g = grab(PPA[10], r"that is, \(k\doteq@\) and \(k\doteq@\).", "PP10")
    report(dec(g[0]) == rnd(rts[0], 2) and dec(g[1]) == rnd(rts[1], 2), "PP10 roots", str(g))
except Exception as err:
    report(False, "PP10 roots", f"ERROR {err}")


def var_k(k):
    return moments(dist(4, F(3, 8 + k)))[1]


kmin = next(k for k in range(0, 100) if var_k(k) < F(8, 10))
report(kmin == 3 and all(var_k(k) < F(8, 10) for k in range(3, 40)), "PP10 smallest k by search", f"k = {kmin}")
present(PPA[10], "PP10", "so the smallest value is \\(k=3\\)")
try:
    g = grab(PPA[10], r"\(k=2\) gives \(\text{Var}(X)=\tfrac{12\times7}{100}=@\), and \(k=3\) gives \(\text{Var}(X)=\tfrac{12\times8}{121}\doteq@\)", "PP10")
    report(F(g[0]) == var_k(2) and g[1] == rnd(var_k(3), 3), "PP10 checks k = 2, 3", str(g))
except Exception as err:
    report(False, "PP10 check", f"ERROR {err}")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failed")
if FAILS:
    print("FAILED:", *FAILS, sep="\n  ")
    sys.exit(1)
print("ALL OK")
