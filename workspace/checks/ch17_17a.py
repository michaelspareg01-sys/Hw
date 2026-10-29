"""Check of Lesson 17A (Y12 Ext 1 Ch 17 pack): Binomial probability.

The script reads the values PRINTED in workspace/build/ch17/a_17a.html (lesson examples, textbook
homework, past-paper worked solutions), in l17a.html (worked examples, the data inside the tutor
demos, your-turn items, textbook questions and past-paper questions, the MC options) and in the
tree diagrams svg/c17a_tree.svg, svg/a17a_spin.svg, svg/a17a_heart.svg. Each value is found with a
template ('@' marks the printed LaTeX); a template must match exactly once in its block, otherwise
the item FAILS. Printed LaTeX ({}^nC_x, \\tfrac, \\dfrac, powers, decimals with thin spaces) is
turned into an exact sympy number and compared with an independent computation:
  - probabilities of small experiments are found by ENUMERATING every outcome (dice faces, suits,
    coin sequences, Bernoulli sequences with itertools.product), never from the formula;
  - larger n use exact fractions.Fraction with math.comb, cross-checked by a convolution of
    n one-stage distributions (no binomial coefficients) for every n used;
  - decimal answers are compared with the exact value rounded half-up (d.p. or s.f.), and
    truncated decimals ('0.013 07...') with the leading digits of the exact value;
  - 'how many trials' answers are found by searching n = 1, 2, 3, ... with exact fractions.
It also checks the past-paper block: marks add to the intro total (15-22), time is 1.5 x marks
rounded to 5 minutes, part marks add to each question's marks, numbering and source labels match
in both files, one hint per question, and the MC letter is the only option equal to the value.

Exit status 1 if anything fails. Run: python3 workspace/checks/ch17_17a.py
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
n_, a_, b_, c_ = sp.symbols("n a b c")
SYMS = {"n": n_, "a": a_, "b": b_, "c": c_, "binomial": sp.binomial}
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
    """Distribution of the number of successes, by convolving n one-stage distributions."""
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
    """Formula values, cross-checked once per (n, p) against enumeration (n <= 14) or convolution."""
    p = F(p)
    d = [pmf(n, x, p) for x in range(n + 1)]
    if (n, p) not in _CROSS:
        other = enum_dist(n, p) if n <= 14 else conv_dist(n, p)
        report(other == d and sum(d) == 1, f"cross-check Bin({n}, {p})", "formula = " + ("enumeration" if n <= 14 else "convolution"))
        _CROSS.add((n, p))
    return d


def P(n, p, xs):
    d = dist(n, p)
    return sum(d[x] for x in xs)


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
        elif t.startswith("\\sqrt[3]", i):
            u, i = _arg(t, i + 8)
            out.append(f" Rational(1,1)*({_conv(u)})**(Rational(1,3))")
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
    t = re.sub(r"\\left|\\right|\\bigg|\\Big|\\big|\\qquad|\\quad|\\,|\\;|\\!|&nbsp;|\s", "", t)
    return t.rstrip(".,")


def tex(t):
    s = _conv(clean(t))
    s = re.sub(r"(?<![\w.])(\d+\.\d+)", r"Rational('\1')", s)     # decimals stay exact
    return parse_expr(s, local_dict=dict(SYMS), transformations=TR)


def exact(t):
    e = sp.expand_func(tex(t)).doit()
    if not e.is_Rational:
        raise ValueError(f"not rational: {t!r} -> {e}")
    return F(int(e.p), int(e.q))


def rnd(v, places):
    """Exact fraction v rounded half-up to `places` decimal places, as a string."""
    q = Decimal(1).scaleb(-places)
    return str((Decimal(v.numerator) / Decimal(v.denominator)).quantize(q, rounding=ROUND_HALF_UP))


def sf(v, digits):
    d = Decimal(v.numerator) / Decimal(v.denominator)
    e = d.adjusted()
    return rnd(v, digits - 1 - e)


def dec(t):
    """Printed decimal (thin spaces allowed) -> plain string."""
    return clean(t).replace("\\ldots", "")


# ---------------------------------------------------------------- HTML blocks
ans = read("a_17a.html")
les = read("l17a.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_17a.html")
report(ans.count("{{ahead:Lesson 17A | Binomial probability}}") == 2, "answers headings", "{{ahead:Lesson 17A | ...}} twice")
report(parts[0].count('<div class="ans-sec">Lesson Examples</div>') == 1 and parts[0].count('<div class="ans-sec">Textbook Homework</div>') == 1,
       "answers sections", "Lesson Examples, Textbook Homework, then Past-Paper solutions")
BLK = {}
for mt in re.finditer(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts[0], re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
PPA = {int(k): v for k, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}
pps = les.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l17a.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
PPQ = {int(k): v for k, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
TQ = {k: v for k, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S)}
CON = {}
for k in range(1, 7):
    seg = teach.split(f"<!-- ============ Concept {k} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[k] = {kind: body for kind, _, body in exs}
    CON[k]["tag"] = [t for kind, t, _ in exs if kind == "worked"][0]
    report([kind for kind, _, _ in exs] == ["demo", "attempt", "worked"], f"Concept {k} blocks", "tutor demo, your turn, worked example")
report([CON[k]["tag"] for k in range(1, 7)] == ["Worked example 1", "Worked example", "Worked example 2", "Worked example 3", "Worked example 4", "Worked example 5"],
       "worked example tags", "Examples 1-5 and the 'from the text' die example")
report(sorted(TQ, key=int) == [str(i) for i in range(1, 23)], "textbook questions 1-22", str(sorted(TQ, key=int)))
report(hw.count("{{band:F}}") == 1 and hw.split("{{band:D}}")[0].count('class="q-num"') == 7
       and hw.split("{{band:D}}")[1].split("{{band:E}}")[0].count('class="q-num"') == 13 and hw.split("{{band:E}}")[1].count('class="q-num"') == 2,
       "bands", "F: Q1-7, D: Q8-20, E: Q21-22 (as the textbook)")


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\&).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def ex_eq(block, where, template, *expected):
    """Every '@' printed as an exact expression equal to the expected exact value."""
    label = f"{where} {template[:70]}"
    try:
        got = grab(block, template, where)
        ok = len(got) == len(expected) and all(exact(g) == F(e) for g, e in zip(got, expected))
        report(ok, label, "printed " + " | ".join(got))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def chain(block, where, template, value, n_min=2):
    """Printed 'A=B=C' (an '@' holding an = chain): every side equals value."""
    label = f"{where} {template[:70]}"
    try:
        (g,) = grab(block, template, where)
        sides = [s for s in g.split("=") if s.strip()]
        ok = len(sides) >= n_min and all(exact(s) == F(value) for s in sides)
        report(ok, label, "printed " + g)
    except Exception as err:
        report(False, label, f"ERROR {err}")


def approx(block, where, template, value, mode, k):
    """'@' is a decimal: exact value rounded to k d.p. (mode 'dp') or k s.f. (mode 'sf')."""
    label = f"{where} {template[:70]}"
    try:
        (g,) = grab(block, template, where)
        want = rnd(F(value), k) if mode == "dp" else sf(F(value), k)
        report(dec(g) == want, label, f"printed {dec(g)}, exact {float(value):.10g} -> {want}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def trunc(block, where, template, value):
    """'@' is '0.013\\,07\\ldots': the leading digits of the exact value."""
    label = f"{where} {template[:70]}"
    try:
        (g,) = grab(block, template, where)
        s = dec(g)
        k = len(s.split(".")[1])
        want = str((Decimal(F(value).numerator) / Decimal(F(value).denominator)).quantize(Decimal(1).scaleb(-k), rounding="ROUND_DOWN"))
        report(g.strip().endswith("\\ldots") and s == want, label, f"printed {s}..., exact {float(value):.12g}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def between(block, start, end, where):
    if block.count(start) != 1:
        raise LookupError(f"start marker found {block.count(start)} times in {where}: {start!r}")
    return block.split(start)[1].split(end)[0]


def present(block, where, text):
    report(block.count(text) == 1, f"{where} data", f"{text[:80]!r} appears {block.count(text)} time(s)")


WORDS = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "ten": 10, "twelve": 12, "twenty": 20}


def num_in(block, where, template):
    (g,) = grab(block, template, where)
    g = g.strip()
    return WORDS[g.lower()] if g.lower() in WORDS else F(g)


DIE = range(1, 7)
SUITS = "HDSC"

# ================================================================ Concept 2: a die thrown four times
we = CON[2]["worked"]
dist4 = [F(0)] * 5
for faces in itertools.product(DIE, repeat=4):          # 1296 equally likely outcomes
    dist4[sum(f == 6 for f in faces)] += F(1, 1296)
present(we, "WE die", "A die is thrown four times.")
rows = re.findall(r"<tr><td>(\d) six(?:es)?</td><td>(.*?)</td><td>(.*?)</td></tr>", we)
report(len(rows) == 5, "WE die table rows", str(len(rows)))
for x, expr, apx in rows:
    x = int(x)
    try:
        report(exact(expr) == dist4[x], f"WE die table P(X={x}) expression", clean(expr))
        report(dec(apx) == rnd(dist4[x], 5), f"WE die table P(X={x}) approximation", f"{dec(apx)} vs {rnd(dist4[x], 5)}")
    except Exception as err:
        report(False, f"WE die row {x}", f"ERROR {err}")
report(sum(dist4) == 1 and "Sum \\(=1\\)" in we, "WE die sum = 1", "")
ex_eq(we, "WE die", r"\[P(X=2)=@.\]", dist4[2])
ex_eq(we, "WE die", r"so for example \(P(\text{SSFF})=@=\tfrac{25}{1296}\)", F(1, 6) ** 2 * F(5, 6) ** 2)
ex_eq(we, "WE die", r"obtained in \({}^4C_2=@\) different ways", sum(1 for s in itertools.product("SF", repeat=4) if s.count("S") == 2))
try:
    g = between(we, r"\[\begin{aligned}\big(\tfrac16+\tfrac56\big)^4&amp;=", r"\end{aligned}\]", "WE die").rstrip(".")
    terms = [t for t in re.split(r"\+(?={}\^4C)", g.replace("\\\\&amp;\\qquad", "")) if t.strip()]
    report(len(terms) == 5 and [exact(t) for t in terms] == dist4, "WE die expansion terms = P(X=0..4)", f"{len(terms)} terms")
except Exception as err:
    report(False, "WE die expansion", f"ERROR {err}")
try:
    (g,) = grab(we, r"\[(x+y)^4=@.\]", "WE die")
    xx, yy = sp.symbols("x y")
    e = parse_expr(_conv(clean(g)).replace("x", "*x").replace("y", "*y").replace("(*", "(").lstrip("*"), local_dict={"x": xx, "y": yy, "binomial": sp.binomial}, transformations=TR)
    report(sp.expand(sp.expand_func(e) - (xx + yy) ** 4) == 0, "WE die (x+y)^4 expansion", g[:60])
except Exception as err:
    report(False, "WE die (x+y)^4", f"ERROR {err}")


# tree diagrams: every leaf outcome and probability, by enumeration
def tree_ok(name, labs, p_s, stages):
    svg = read(os.path.join("svg", name + ".svg"))
    leaves = re.findall(r">([" + labs + r"]{" + str(stages) + r"})</text><text[^>]*>(\d+)/(\d+)</text>", svg)
    seqs = ["".join(s) for s in itertools.product(labs, repeat=stages)]
    ok = [o for o, _, _ in leaves] == seqs
    for o, u, v in leaves:
        pr = F(1)
        for ch in o:
            pr *= p_s if ch == labs[0] else 1 - p_s
        ok &= F(int(u), int(v)) == pr and int(v) == (p_s.denominator ** stages)
    report(ok and len(leaves) == 2 ** stages, f"tree {name}", f"{len(leaves)} leaves, outcomes in order, probabilities = products")


tree_ok("c17a_tree", "SF", F(1, 6), 4)
tree_ok("a17a_spin", "RN", F(1, 3), 3)
tree_ok("a17a_heart", "HN", F(1, 4), 3)

# ================================================================ Concept 1 (answers are words)
b1 = BLK["C1"]
for t in ("<b>a</b> (i) Yes. Success is ‘an even number’, with \\(p=\\tfrac36=\\tfrac12\\)", "(ii) No. There are six outcomes",
          "(iii) Yes. Success is ‘a heart’, with \\(p=\\tfrac{13}{52}=\\tfrac14\\)", "<b>b</b> (i) Yes, with \\(n=10\\) and \\(p=\\tfrac12\\)",
          "(i) Yes. Success is ‘lands on 5’, with \\(p=\\tfrac15\\)", "with \\(p=\\tfrac26=\\tfrac13\\)", "<b>b</b> (i) Yes, with \\(n=8\\) and \\(p=\\tfrac16\\)"):
    present(b1, "C1", t)
report(F(sum(1 for f in DIE if f % 2 == 0), 6) == F(1, 2) and F(sum(1 for f in DIE if f > 4), 6) == F(1, 3), "C1 p values by counting faces", "")
for t in ("A coin is tossed 10 times", "A die is thrown 8 times, and \\(X\\) is the number of threes", "it shows a number greater than 4"):
    present(teach, "C1 lesson", t)

# ================================================================ Concept 2 answers
for key, p, lab, den, var in (("demo", F(1, 3), "\\tfrac13", 27, "spin"), ("yt", F(1, 4), "\\tfrac14", 64, "heart")):
    blk = BLK["C2"].split("<b>Your turn.</b>")[0 if key == "demo" else 1]
    d3 = enum_dist(3, p)
    for x in range(4):
        chain(blk, f"C2 {key}", rf"\(P(X={x})=@\)", d3[x], 2)
    try:
        (g,) = grab(blk, r"<b>c</b> \(@\)</div>", f"C2 {key}")
        lhs, rhs = g.split("=")
        terms = rhs.split("+")
        (g2,) = grab(blk, '4mm">\\(=@=1\\)', f"C2 {key}")
        report(exact(lhs) == 1 and [exact(t) for t in terms] == d3 and [exact(t) for t in g2.split("+")] == d3,
               f"C2 {key} expansion terms = P(X=0..3), sum 1", g2)
    except Exception as err:
        report(False, f"C2 {key} expansion", f"ERROR {err}")
present(CON[2]["demo"], "C2 demo", "lands on red with probability \\(\\tfrac13\\). It is spun three times")
present(CON[2]["attempt"], "C2 your turn", "This is done three times, and \\(X\\) is the number of hearts.")

# ================================================================ Concept 3: worked example 2 and answers C3
we = CON[3]["worked"]
d6 = [F(0)] * 7
for suits in itertools.product(SUITS, repeat=6):        # 4^6 equally likely suit sequences
    d6[suits.count("C")] += F(1, 4 ** 6)
for g, v in (("1215", d6[2]), ("1458", d6[1]), ("3367", 1 - d6[0]), ("154", d6[4] + d6[5] + d6[6])):
    report(F(int(g), 4 ** 6) == v and we.count(f"\\frac{{{g}}}{{4^6}}") == 1, f"WE2 {g}/4^6 by enumeration", "")
ex_eq(we, "WE2", r"P(\text{two are clubs})&amp;=@\\&amp;=\frac{15\times3^4}{4^6}", d6[2])
ex_eq(we, "WE2", r"&amp;=@\\&amp;=\frac{1215}{4^6}", d6[2])
ex_eq(we, "WE2", r"P(\text{one is a club})&amp;=@\\&amp;=\frac{6\times3^5}{4^6}", d6[1])
ex_eq(we, "WE2", r"&amp;=@\\&amp;=\frac{1458}{4^6}", d6[1])
ex_eq(we, "WE2", r"&amp;=1-@\qquad", d6[0])
ex_eq(we, "WE2", r"\text{or }1-@\Big)", d6[0])
ex_eq(we, "WE2", r"P(\text{six are clubs})\\&amp;=@\\&amp;=\frac{15\times3^2", d6[4] + d6[5] + d6[6])
ex_eq(we, "WE2", r"\\&amp;=@\\&amp;=\frac{154}{4^6}", d6[4] + d6[5] + d6[6])

dm = CON[3]["demo"]
nn = num_in(dm, "C3 demo", "A die is thrown @ times.")
present(dm, "C3 demo", "if it shows a number less than 3")
d7 = [F(0)] * (nn + 1)
for faces in itertools.product(DIE, repeat=nn):          # 6^7 = 279 936 outcomes
    d7[sum(f < 3 for f in faces)] += F(1, 6 ** nn)
blk = BLK["C3"].split("<b>Your turn.</b>")
for lab, v in (("a", d7[2]), ("b", d7[1]), ("c", 1 - d7[0]), ("d", d7[6] + d7[7])):
    chain(blk[0], "C3 demo", f"<b>{lab}</b> \\(@\\)<br>", v, 3)
yt = CON[3]["attempt"]
nn = num_in(yt, "C3 yt", '<div class="ex-body">\n@ cards are drawn at random')
d5 = [F(0)] * (nn + 1)
for suits in itertools.product(SUITS, repeat=nn):
    d5[suits.count("H")] += F(1, 4 ** nn)
for lab, v in (("a", d5[2]), ("b", d5[1]), ("c", 1 - d5[0]), ("d", d5[4] + d5[5])):
    chain(blk[1], "C3 yt", f"<b>{lab}</b> \\(@\\)" + ("<br>" if lab != "d" else ""), v, 3)

# ================================================================ Concept 4: p = q = 1/2
we = CON[4]["worked"]
ex_eq(we, "WE3", r"P(50\text{ heads})&amp;=@\\", F(math.comb(100, 50), 2 ** 100))
ex_eq(we, "WE3", r"\\&amp;=@\\&amp;\doteq", F(math.comb(100, 50), 2 ** 100))
approx(we, "WE3", r"&amp;\doteq@.\end{aligned}", F(math.comb(100, 50), 2 ** 100), "sf", 4)
coin = lambda m, x: F(sum(1 for s in itertools.product((0, 1), repeat=m) if sum(s) == x), 2 ** m) if m <= 20 else pmf(m, x, F(1, 2))
blk = BLK["C4"].split("<b>Your turn.</b>")
m = int(num_in(CON[4]["demo"], "C4 demo", "A coin is tossed @ times."))
for lab, x in (("a", 10), ("b", 12)):
    try:
        (g,) = grab(blk[0], f"<b>{lab}</b> \\(P({x}\\text{{ heads}})=@\\)", "C4 demo")
        sides = re.split(r"=|\\doteq", g)
        v = coin(m, x)
        report(exact(sides[0]) == v and exact(sides[1]) == v and dec(sides[2]) == sf(v, 4), f"C4 demo {lab}", g)
    except Exception as err:
        report(False, f"C4 demo {lab}", f"ERROR {err}")
m = int(num_in(CON[4]["attempt"], "C4 yt", "A coin is tossed @ times."))
for lab, x in (("a", 15), ("b", 18)):
    try:
        (g,) = grab(blk[1], f"<b>{lab}</b> \\(P({x}\\text{{ heads}})=@\\)", "C4 yt")
        sides = re.split(r"=|\\doteq", g)
        v = coin(m, x)
        report(exact(sides[0]) == v and dec(sides[1]) == sf(v, 4), f"C4 yt {lab}", g)
    except Exception as err:
        report(False, f"C4 yt {lab}", f"ERROR {err}")

# ================================================================ Concept 5: experimental probabilities
we = CON[5]["worked"]
present(we, "WE4", "1% of its bulbs are defective. If it packs its bulbs in boxes of 50")
d = dist(50, F(1, 100))
ex_eq(we, "WE4", r"<b>a</b> \(P(X=0)=@\doteq", d[0])
approx(we, "WE4", r"\doteq@\)</p>", d[0], "sf", 3)
ex_eq(we, "WE4", r"&amp;=1-@\\&amp;\doteq", d[0] + d[1])
approx(we, "WE4", r"\\&amp;\doteq@\end{aligned}", 1 - d[0] - d[1], "sf", 3)


def least_n(q, c):
    k = 1
    while not (1 - q ** k > c):
        k += 1
    return k


for key, blk_l, blk_a in (("demo", CON[5]["demo"], BLK["C5"].split("<b>Your turn.</b>")[0]),
                          ("yt", CON[5]["attempt"], BLK["C5"].split("<b>Your turn.</b>")[1])):
    try:
        if key == "demo":
            pct = num_in(blk_l, "C5 demo", "that @% of its eggs are cracked")
            size = num_in(blk_l, "C5 demo", "packed in trays of @.")
            c = num_in(blk_l, "C5 demo", "at least one cracked egg is more than @?")
        else:
            pct = num_in(blk_l, "C5 yt", "that @% of its seeds fail")
            size = num_in(blk_l, "C5 yt", "sold in packets of @.")
            c = num_in(blk_l, "C5 yt", "at least one fails is more than @?")
        p = F(pct) / 100
        d = dist(int(size), p)
        ex_eq(blk_a, f"C5 {key}", r"<b>a</b> \(P(X=0)=@\doteq", d[0])
        approx(blk_a, f"C5 {key}", r"<b>a</b> \(P(X=0)=" + {"demo": "0.98^{30}", "yt": "0.95^{40}"}[key] + r"\doteq@\)", d[0], "sf", 3)
        ex_eq(blk_a, f"C5 {key}", r"<b>b</b> \(P(X\ge2)=1-@\doteq", d[0] + d[1])
        approx(blk_a, f"C5 {key}", r"\big)\doteq@\)<br>", 1 - d[0] - d[1], "sf", 3)
        q = 1 - p
        k = least_n(q, c)
        approx(blk_a, f"C5 {key}", r"\dfrac{\ln" + {"demo": "0.1}{\\ln0.98", "yt": "0.05}{\\ln0.95"}[key] + r"}\doteq@\)", F(math.log(1 - c) / math.log(q)).limit_denominator(10 ** 12), "dp", 2)
        (g,) = grab(blk_a, r"\doteq" + {"demo": "113.97", "yt": "58.40"}[key] + r"\). So @ ", f"C5 {key}")
        report(int(g) == k, f"C5 {key} least n (search)", f"printed {g}, search {k}")
        (u, v) = grab(blk_a, r"(Check: \(" + {"demo": "0.98", "yt": "0.95"}[key] + "^{" + str(k - 1) + r"}\doteq@\) and \(" + {"demo": "0.98", "yt": "0.95"}[key] + "^{" + str(k) + r"}\doteq@\).)", f"C5 {key}")
        report(dec(u) == rnd(q ** (k - 1), 4) and dec(v) == rnd(q ** k, 4) and q ** (k - 1) >= 1 - c > q ** k, f"C5 {key} check values", f"{u} {v}")
    except Exception as err:
        report(False, f"C5 {key}", f"ERROR {err}")

# ================================================================ Concept 6: compound stages
we = CON[6]["worked"]
present(we, "WE5", "making 20 shirts a day, of which 2% are defective. Fay works faster, making 30 shirts a day, of which 4%")
pj = F(20, 50) * F(2, 100) + F(30, 50) * F(4, 100)
ex_eq(we, "WE5", r"\\&amp;=@\\&amp;=\frac{4}{125},", pj)
ex_eq(we, "WE5", r"so \(p=@\) and \(q=\tfrac{121}{125}\)", pj)
ex_eq(we, "WE5", r"and \(q=@\). Let", 1 - pj)
d = dist(30, pj)
ex_eq(we, "WE5", r"P(X=2)\\&amp;=@\\&amp;\doteq", d[0] + d[1] + d[2])
approx(we, "WE5", r"&amp;\doteq@.\end{aligned}", d[0] + d[1] + d[2], "sf", 3)
for key, blk_l, blk_a, names in (("demo", CON[6]["demo"], BLK["C6"].split("<b>Your turn.</b>")[0], ("Machine A makes @ bolts an hour, of which @% are faulty. Machine B makes @ bolts an hour, of which @% are faulty", "packed in boxes of @.")),
                                 ("yt", CON[6]["attempt"], BLK["C6"].split("<b>Your turn.</b>")[1], ("Oven 1 bakes @ loaves an hour, of which @% are burnt. Oven 2 bakes @ loaves an hour, of which @% are burnt", "packed in crates of @."))):
    try:
        na, pa, nb, pb = [F(t) for t in grab(blk_l, names[0], f"C6 {key}")]
        (size,) = grab(blk_l, names[1], f"C6 {key}")
        p = na / (na + nb) * pa / 100 + nb / (na + nb) * pb / 100
        (g,) = grab(blk_a, r"\times\tfrac{" + ("5" if key == "demo" else "10") + r"}{100}=@\)", f"C6 {key}")
        report(F(dec(g)) == p, f"C6 {key} p", f"printed {g}, computed {p}")
        (g,) = grab(blk_a, r"so \(q=@\).", f"C6 {key}")
        report(F(dec(g)) == 1 - p, f"C6 {key} q", g)
        d = dist(int(size), p)
        ex_eq(blk_a, f"C6 {key}", r"\(P(X\le1)=@\doteq", d[0] + d[1])
        approx(blk_a, f"C6 {key}", r"\doteq@\).", d[0] + d[1], "sf", 3)
    except Exception as err:
        report(False, f"C6 {key}", f"ERROR {err}")

# ================================================================ textbook homework answers
A = BLK
# Q1: five children, enumerate 2^5
fam = list(itertools.product("BG", repeat=5))
g_ = lambda cond: F(sum(1 for s in fam if cond(s)), len(fam))
ex_eq(A["1"], "Q1", r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)",
      g_(lambda s: s.count("G") == 0), g_(lambda s: s.count("G") == 2), g_(lambda s: s.count("G") == 1), g_(lambda s: s.count("G") >= 1))
present(TQ["2"], "Q2", "a chance of \\(\\tfrac15\\) of hitting a boundary")
ex_eq(A["2"], "Q2", r"\(@\)", enum_dist(6, F(1, 5))[2])
ex_eq(A["3"], "Q3", r"<b>b</b> \(@\)", enum_dist(12, F(1300, 2000))[12])
d = enum_dist(12, F(1, 6))
ex_eq(A["4"], "Q4", r"<b>a</b> \(@\) &nbsp;", d[3])
ex_eq(A["4"], "Q4", r"<b>b</b> \(@\)<br>", d[8])
ex_eq(A["4"], "Q4", r"<b>c</b> \(@\)", d[10] + d[11] + d[12])
d = enum_dist(6, F(1, 6))
for lab, v in (("a", d[2]), ("b", d[0] + d[1]), ("c", 1 - d[0] - d[1])):
    approx(A["5"], "Q5", f"<b>{lab}</b> @" + (" &nbsp;" if lab != "c" else "</div>"), v, "dp", 4)
d = dist(20, F(9, 10))
ex_eq(A["6"], "Q6", r"<b>a</b> \(@\) &nbsp;", d[18] + d[19] + d[20])
ex_eq(A["6"], "Q6", r"<b>b</b> \(@\)", 1 - d[20])
d = enum_dist(10, F(9, 100))
ex_eq(A["7"], "Q7", r"<b>a</b> \(@\)<br>", d[0] + d[1] + d[2])
ex_eq(A["7"], "Q7", r"<b>b</b> \(@\)", 1 - d[0] - d[1])
lst = grab(A["8"], "<b>a</b> @<br>", "Q8")[0].split(", ")
win = ["".join(s) for s in itertools.product("HT", repeat=4) if s.count("H") == 2]
report(sorted(lst) == sorted(win) and len(lst) == 6, "Q8a list of orderings", ", ".join(lst))
ex_eq(A["8"], "Q8", r"wins is \(\tfrac{6}{2^4}=@\)", F(len(win), 16))
chain(A["8"], "Q8", r"There are \(@\) arrangements", len(set(itertools.permutations("HHTT"))), 3)
report(A["9"].split("</div>")[0] == rnd(sum(enum_dist(5, F(55, 100))[3:]), 3), "Q9 3 d.p.", A["9"].split("</div>")[0])
ex_eq(A["10"], "Q10", r"\(@\)", dist(31, F(95, 100))[28])
d = enum_dist(10, F(12, 1000))
approx(A["11"], "Q11", "<b>a</b> (i) @ &nbsp;", d[1], "dp", 5)
approx(A["11"], "Q11", "(ii) @ &nbsp;", 1 - d[0], "dp", 5)
# 11b: prize after k-1 misses is 10000k; it exceeds 200000 when the first win is at draw k >= 21
pw = sum(F(988, 1000) ** (k - 1) * F(12, 1000) for k in range(21, 4000))
approx(A["11"], "Q11", "<b>b</b> @</div>", pw + F(988, 1000) ** 3999, "dp", 5)
report(abs(float(pw) - float(F(988, 1000) ** 20)) < 1e-15, "Q11b sum of first-win probabilities = 0.988^20", "")
ex_eq(A["12"], "Q12", r"<b>a</b> @ &nbsp; <b>b</b> @</div>", least_n(F(5, 6), F(95, 100)), least_n(F(1, 2), F(99, 100)))
three = list(itertools.product("BG", repeat=3))
p3b = F(sum(1 for s in three if s.count("B") == 3), 8)
pmore = F(sum(1 for s in three if s.count("B") > s.count("G")), 8)
approx(A["13"], "Q13", "<b>a</b> (i) @ &nbsp;", 1 - (1 - p3b) ** 5, "dp", 3)
approx(A["13"], "Q13", "(ii) @<br>", pmore ** 5, "dp", 3)
rain = F(18, 30)
w5 = list(itertools.product("RF", repeat=5))
pr = lambda s: math.prod(rain if ch == "R" else 1 - rain for ch in s)
v15a = pr("FFRRR")
v15b = sum(pr(s) for s in w5 if s.count("R") > s.count("F"))
for lab, v, tail in (("a", v15a, " &nbsp;"), ("b", v15b, "</div>")):
    try:
        (g, h) = grab(A["15"], f"<b>{lab}</b> @ (exactly @)" + tail, "Q15")
        report(g == rnd(v, 4) and F(h) == v, f"Q15{lab} 4 d.p. and exact value", f"printed {g} ({h}), exact {v} = {float(v)}")
    except Exception as err:
        report(False, f"Q15{lab}", f"ERROR {err}")
# Q16: each serve is an ace (1/15), in but not an ace (8/10 - 1/15) or out (2/10)
sv = {"A": F(1, 15), "I": F(8, 10) - F(1, 15), "O": F(2, 10)}
s4 = list(itertools.product("AIO", repeat=4))
prs = lambda s: math.prod(sv[ch] for ch in s)
v16 = (sum(prs(s) for s in s4 if "O" not in s), sum(prs(s) for s in s4 if s.count("A") >= 3), sum(prs(s) for s in s4 if s.count("A") == 3 and s.count("I") == 1))
for lab, v in zip("abc", v16):
    approx(A["16"], "Q16", f"<b>{lab}</b> @" + (" &nbsp;" if lab != "c" else "</div>"), v, "dp", 6)
cars = [F(65, 100)] * 6 + [F(80, 100)] * 4
s10 = list(itertools.product((0, 1), repeat=10))
prc = lambda s: math.prod(cars[i] if s[i] else 1 - cars[i] for i in range(10))
v17a = sum(prc(s) for s in s10 if sum(s[:6]) == 3 and sum(s[6:]) == 1)
v17b = sum(prc(s) for s in s10 if sum(s) == 4)
approx(A["17"], "Q17", "<b>a</b> @ &nbsp;", v17a, "dp", 4)
approx(A["17"], "Q17", "<b>b</b> @</div>", v17b, "dp", 4)
p18 = F(4, 5) * F(1, 100) + F(1, 5) * F(1, 50)
ex_eq(A["18"], "Q18", r"<b>a</b> \(@\)<br>", p18)
d = enum_dist(10, p18)
ex_eq(A["18"], "Q18", r"<b>b</b> (i) \(@\) &nbsp;", d[10])
ex_eq(A["18"], "Q18", r"(ii) \(@\) &nbsp;", d[5])
ex_eq(A["18"], "Q18", r"(iii) \(@\)</div>", d[0] + d[1])
bags = [("R",) * 3 + ("W",) * 5, ("R",) * 4 + ("W",) * 4]
p19 = sum(F(1, 2) * F(bg.count("R"), len(bg)) for bg in bags)
ex_eq(A["19"], "Q19", r"<b>a</b> \(@\)<br>", p19)
d = enum_dist(8, p19)
ex_eq(A["19"], "Q19", r"<b>b</b> (i) \(@\) &nbsp;", d[3])
ex_eq(A["19"], "Q19", r"(ii) \(@\)</div>", 1 - d[0] - d[1] - d[2])
ev = F(sum(1 for fs in itertools.product(DIE, repeat=6) if sum(f % 2 == 0 for f in fs) > 3), 6 ** 6)
hd = F(sum(1 for s in itertools.product("HT", repeat=8) if s.count("H") > 4), 2 ** 8)
ex_eq(A["20"], "Q20", r"<b>a</b> @ &nbsp; <b>b</b> @</div>", round(100 * ev), round(60 * hd))
report(abs(100 * ev - round(100 * ev)) < F(1, 2) and abs(60 * hd - round(60 * hd)) < F(1, 2), "Q20 expected counts", f"{float(100 * ev)} {float(60 * hd)}")
balls = list(itertools.combinations(range(1, 21), 4))
p21 = F(sum(1 for s in balls if 19 in s), len(balls))
report(p21 == F(1, 5) and "is 0.2." in TQ["21"], "Q21 P(19 drawn) = 0.2 by enumeration", str(p21))
d = enum_dist(5, p21)
approx(A["21"], "Q21", "<b>a</b> @ &nbsp;", d[2], "dp", 4)
try:
    (g,) = grab(A["21"], "<b>b</b> @ &nbsp;", "Q21")
    report(F(g) == 1 - d[0] - d[1], "Q21b exact decimal", f"printed {g}, exact {float(1 - d[0] - d[1])}")
    (g,) = grab(A["21"], r"<b>c</b> (i) \(@\)</div>", "Q21")
    e = tex(g)
    ok = all(e.subs(n_, m) == sp.Rational(sum(1 for s in balls if max(s) <= m), len(balls)) for m in range(4, 21))
    report(ok, "Q21c(i) formula vs enumeration for n = 4..20", g)
except Exception as err:
    report(False, "Q21", f"ERROR {err}")
try:
    (g,) = grab(A["22"], r"<b>a</b> \(@\)<br>", "Q22")
    report(sp.expand(tex(g) - (a_ + b_ + c_) ** 3) == 0, "Q22a expansion", g)
except Exception as err:
    report(False, "Q22a", f"ERROR {err}")
team = {"H": F(65, 100), "C": F(24, 100), "S": F(11, 100)}
t3 = list(itertools.product("HCS", repeat=3))
prt = lambda s: math.prod(team[ch] for ch in s)
v22 = (sum(prt(s) for s in t3 if sorted(s) == ["C", "H", "S"]), sum(prt(s) for s in t3 if s.count("C") == 2), sum(prt(s) for s in t3 if len(set(s)) < 3))
for lab, v, tail in (("(i)", v22[0], " &nbsp;"), ("(ii)", v22[1], " &nbsp;"), ("(iii)", v22[2], "</div>")):
    approx(A["22"], "Q22", f"{lab} @{tail}", v, "dp", 5)
report(set(BLK) == {"C1", "C2", "C3", "C4", "C5", "C6"} | {str(i) for i in range(1, 23)}, "answer blocks", f"{sorted(BLK, key=lambda t: (len(t), t))}")

# ================================================================ past papers
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(v) for v in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M} (house rule: 15-22)")
    report(T == 5 * round(1.5 * M / 5), "PP time", f"{T} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)) and len(marks) == len(PPQ), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for k in PPQ:
        subs = [int(s) for s in re.findall(r'<span class="mk">(\d)</span></div>', PPQ[k])]
        if subs:
            report(sum(subs) == marks[k - 1], f"PP{k} part marks", f"{subs} = {marks[k - 1]}")
        sq = re.search(r"^(.*?)</span><span class=\"mk\">", PPQ[k], re.S).group(1)
        sa = re.search(r"^(.*?)</span></div>", PPA[k], re.S).group(1)
        report(sq == sa, f"PP{k} source label", re.sub("<[^>]+>|&nbsp;", " ", sq)[:90])
        report(PPQ[k].count('<div class="hint">') == 1, f"PP{k} hint", "exactly one hint")
except Exception as err:
    report(False, "PP structure", f"ERROR {err}")

# PP1 (school answer C: two outcomes)
present(PPA[1], "PP1", "<b>Answer C.</b>")
present(PPQ[1], "PP1", "C.&ensp;Choosing a red pen from a container that contains red, black and blue pens")
# PP2: options from the lesson; exactly one equals P(X = 9)
v = enum_dist(10, F(2, 3))[9]
try:
    opts = dict(re.findall(r"<span>([A-D])\.&ensp;\\\((.+?)\\\)</span>", PPQ[2]))
    good = [L for L, e in opts.items() if exact(e) == v]
    report(len(opts) == 4 and good == ["D"] and "<b>Answer D.</b>" in PPA[2], "PP2 MC letter", f"options equal to P(X=9): {good}")
    (g,) = grab(PPA[2], r"\[P(X=9)=@.\]", "PP2")
    report(all(exact(s) == v for s in g.split("=")), "PP2 chain", g)
except Exception as err:
    report(False, "PP2", f"ERROR {err}")
# PP3: five dice, enumerate 6^5
v = F(sum(1 for fs in itertools.product(DIE, repeat=5) if fs.count(6) == 2), 6 ** 5)
try:
    (g,) = grab(PPA[3], r"\[P(X=2)=@.\]", "PP3")
    sd = re.split(r"=|\\doteq", g)
    report(all(exact(s) == v for s in sd[:-1]) and dec(sd[-1]) == rnd(v, 4), "PP3", g)
except Exception as err:
    report(False, "PP3", f"ERROR {err}")
# PP4: five questions with four options, enumerate 4^5 (option 0 correct)
v = F(sum(1 for s in itertools.product(range(4), repeat=5) if s.count(0) == 3), 4 ** 5)
chain(PPA[4], "PP4", r"\[P(X=3)=@.\]", v, 3)
present(PPQ[4], "PP4", "Each question has four alternative answers.")
# PP5
pct = num_in(PPQ[5], "PP5", "knows that @% of the toy cars")
size = num_in(PPQ[5], "PP5", "boxes of @ cars")
d = dist(int(size), F(pct) / 100)
ex_eq(PPA[5], "PP5", r"<b>(i)</b> \(P(X=5)=@=0.013", d[5])
trunc(PPA[5], "PP5", r"\times0.97^{45}=@\doteq", d[5])
approx(PPA[5], "PP5", r"\ldots\doteq@\)</p>" + "\n<p><b>(ii)", d[5], "dp", 4)
ex_eq(PPA[5], "PP5", r"P(X\ge1)=1-P(X=0)=@=0.781", 1 - d[0])
trunc(PPA[5], "PP5", r"=1-0.97^{50}=@\doteq", 1 - d[0])
approx(PPA[5], "PP5", r"\ldots\doteq@\)</p></div>", 1 - d[0], "dp", 4)
# PP6
pp6 = num_in(PPQ[6], "PP6", "during a race is @. The car")
nr = num_in(PPQ[6], "PP6", "competes in a @ race series")
d = dist(int(nr), pp6)
ex_eq(PPA[6], "PP6", r"\(P(X=3)=@=0.236", d[3])
trunc(PPA[6], "PP6", r"0.8^9=@\doteq0.24", d[3])
approx(PPA[6], "PP6", r"\ldots\doteq@\)</p>", d[3], "dp", 2)
ex_eq(PPA[6], "PP6", r"P(X\le3)&amp;=@\\&amp;=0.794", sum(d[:4]))
trunc(PPA[6], "PP6", r"\\&amp;=@\doteq0.79", sum(d[:4]))
approx(PPA[6], "PP6", r"\ldots\doteq@\end{aligned}", sum(d[:4]), "dp", 2)
# PP7
pc = num_in(PPQ[7], "PP7", "indicate that @% of bags contain 50 lollipops")
nb = num_in(PPQ[7], "PP7", "A batch of @ bags is sampled")
d = dist(int(nb), 1 - F(pc) / 100)
ex_eq(PPA[7], "PP7", r"\(P(X=2)=@=0.227", d[2])
trunc(PPA[7], "PP7", r"0.92^{13}=@\doteq0.2273", d[2])
approx(PPA[7], "PP7", r"\ldots\doteq@\)</p>", d[2], "dp", 4)
ex_eq(PPA[7], "PP7", r"\\&amp;=1-@\\&amp;=0.112", d[0] + d[1] + d[2])
trunc(PPA[7], "PP7", r"\\&amp;=@\doteq0.1130", 1 - d[0] - d[1] - d[2])
approx(PPA[7], "PP7", r"\ldots\doteq@\end{aligned}", 1 - d[0] - d[1] - d[2], "dp", 4)
# PP8: two dice total 9 (enumerate 36), six rounds
p9 = F(sum(1 for u in DIE for w in DIE if u + w == 9), 36)
present(PPQ[8], "PP8", "a total of 9 when throwing two dice. Six rounds")
ex_eq(PPA[8], "PP8", r"probability \(p=@=\tfrac19\)", p9)
d = enum_dist(6, p9)
ex_eq(PPA[8], "PP8", r"&amp;=P(X=5)+P(X=6)\\&amp;=@\\", d[5] + d[6])
try:
    (g,) = grab(PPA[8], r"\\&amp;=\frac{48}{9^6}+@\end{aligned}", "PP8")
    sd = re.split(r"=|\\doteq", g)
    report(exact("\\frac{48}{9^6}+" + sd[0]) == d[5] + d[6] and exact(sd[1]) == d[5] + d[6] and dec(sd[2]) == sf(d[5] + d[6], 3), "PP8 value and 3 s.f.", g)
except Exception as err:
    report(False, "PP8", f"ERROR {err}")
# PP9
pa, pb = num_in(PPQ[9], "PP9", "that @% of Farm A"), num_in(PPQ[9], "PP9", "while @% of Farm B")
pdet = F(2, 3) * F(pa) / 100 + F(1, 3) * F(pb) / 100
present(PPQ[9], "PP9", "twice as likely to be sourced from Farm A than Farm B")
chain(PPA[9], "PP9", r"\\&amp;=@.\end{aligned}", pdet, 3)
report(pdet == F(19, 30), "PP9 (i) result 19/30", str(pdet))
d = dist(10, pdet)
ex_eq(PPA[9], "PP9", r"\\&amp;=@\\&amp;=0.929", sum(d[:9]))
trunc(PPA[9], "PP9", r"\\&amp;=@\doteq0.93", sum(d[:9]))
approx(PPA[9], "PP9", r"\ldots\doteq@\end{aligned}", sum(d[:9]), "dp", 2)
# PP10: p^3 = 0.512 exactly gives p = 4/5; test the options
try:
    p3 = F(num_in(PPQ[10], "PP10", "three consecutive days is @. The probability"))
    target = F(num_in(PPQ[10], "PP10", "a period of n days is @. What"))
    p = next(F(k, 1000) for k in range(1, 1001) if F(k, 1000) ** 3 == p3)
    opts = dict(re.findall(r"<span>([A-D])\.&ensp;(\d+)</span>", PPQ[10]))
    good = [L for L, m in opts.items() if pmf(int(m), 2, p) == target]
    report(p == F(4, 5) and good == ["B"] and "<b>Answer B.</b>" in PPA[10], "PP10 MC letter", f"p = {p}, options giving {target}: {good}")
    for m in (4, 5, 6, 7):
        (g,) = grab(PPA[10], f"\\(n={m}\\) gives \\(@\\)", "PP10")
        lhs, rhs = g.split("=")
        report(exact(lhs) == pmf(m, 2, p) and F(dec(rhs)) == pmf(m, 2, p), f"PP10 n = {m}", g)
except Exception as err:
    report(False, "PP10", f"ERROR {err}")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failed")
if FAILS:
    print("FAILED:", *FAILS, sep="\n  ")
    sys.exit(1)
print("ALL OK")
