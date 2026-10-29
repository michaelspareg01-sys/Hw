"""Check of Lesson 13B (Y11 Ch 13 pack): Expected value.

The script reads the values PRINTED in workspace/build/y11ch13/a_13b.html (lesson examples and
textbook homework answers) and in l13b.html (the concept boxes, worked examples, and the data
given inside the tutor demos, your-turn items and textbook questions).  Every distribution
table is parsed cell by cell (rows x / p(x) / xp(x) with a Sum column, or the transposed
column layout); every inline value is found with a template ('@' marks the printed value), and
a template must match exactly once in its block, otherwise the item FAILS.  Printed LaTeX
(\\tfrac, mixed numbers such as 3\\tfrac12, decimals) is turned into an exact rational.

Each printed result is compared with an independent computation using fractions.Fraction:
  - distributions are found by ENUMERATING the sample space (coins, dice, card pairs, friends
    and their cash, boxes in the shop, the weighted die, the slot machine's 6^3 rolls), with
    the data read from the printed statements, never copied from the answers;
  - E(X) is recomputed as the exact sum of x p(x); every xp(x) cell and every Sum cell is
    checked; E(aX + b) results are checked against the transformed tables;
  - the infinite sums (Wulf, St Petersburg) are checked with sympy summation;
  - the figures are checked by re-running figs.build_13b() with the plotting call recorded.
No simulation is used.  It also checks the structure (concepts, demos, your-turns, worked
examples, answer blocks, bands).  Lesson 13B has no past-paper mini exam (house rule 8: no clean
school-paper item in the catalogue needs only E(X) of a given distribution); the script checks
that no half-built past-paper block is present.

Exit status 1 if anything fails.  Run: python3 workspace/checks/y11ch13_13b.py
"""
import os
import re
import sys
from fractions import Fraction as F
from itertools import permutations, product

import sympy as sp
from sympy.parsing.sympy_parser import (implicit_multiplication, parse_expr, rationalize,
                                        standard_transformations)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH13_SRC", os.path.join(HERE, "..", "build", "y11ch13"))   # override only for mutation tests
FAILS = []
NCHECK = [0]
K = sp.Symbol("k")
TR = standard_transformations + (implicit_multiplication, rationalize)
MONEY = '<span style="white-space:nowrap">\\(\\$\\)'


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label + ("  " + detail if detail else ""))
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- printed LaTeX -> exact value
def _arg(t, i):
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
        if t.startswith(("\\tfrac", "\\dfrac", "\\frac"), i):
            i = t.index("frac", i) + 4
            u, i = _arg(t, i)
            v, i = _arg(t, i)
            if out and re.match(r"\d", out[-1][-1:] or ""):
                out.append("+")                 # mixed number such as 3\tfrac12
            out.append(f"(({_conv(u)})/({_conv(v)}))")
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


def strip(cell):
    c = re.sub(r"<[^>]+>", "", cell)
    c = c.replace("\\(", "").replace("\\)", "").replace("&nbsp;", " ").replace("\\$", "")
    return re.sub(r"\\,|\\;|\\!|\\ ", "", c).strip()


def sym(t):
    t = strip(t)
    return parse_expr(_conv(t.replace(" ", "")), local_dict={"k": K}, transformations=TR)


def val(t):
    e = sp.nsimplify(sym(t))
    if not e.is_Rational:
        raise ValueError(f"not a number: {t!r}")
    return F(int(e.p), int(e.q))


def plain(t):
    """Statement text with the money markup removed: '$560 cash'."""
    t = t.replace(MONEY, "$").replace("\\(\\$\\)", "$")
    return re.sub(r"\s+", " ", re.sub(r"</?span[^>]*>", "", t))


# ---------------------------------------------------------------- HTML blocks
ans = read("a_13b.html")
les = read("l13b.html")
report(ans.count("{{ahead:Lesson 13B | Expected value}}") == 1, "answers heading", "{{ahead:Lesson 13B | Expected value}} once")
PPN = les.split("<!-- ============ Past papers ============ -->")
report(len(PPN) == 2 and "{{sec:amber:clock:Past-paper homework:timed practice}}" in PPN[1] and "Questions 8, 9, 11 (after Question 2) and 12 above in 25 minutes" in PPN[1]
       and "Past-Paper" not in ans and "pp-intro" not in les and 'class="pp"' not in les,
       "past-paper note only (controller ruling: no in-scope school-paper item; answers have no PP section)", "")
BLK = {}
for mt in re.finditer(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers ============ -->")[0]
teach = les.split("<!-- ============ Homework ============ -->")[0]
TQ = {k: v for k, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S)}
EX = re.findall(r'<div class="ex (demo|attempt|worked)"><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<!-- =====|$)', teach, re.S)
DEMO = [b for k, _, b in EX if k == "demo"]
YT = [b for k, _, b in EX if k == "attempt"]
WORK = {t: b for k, t, b in EX if k == "worked" and t != "Worked example"}
WFT = [b for k, t, b in EX if k == "worked" and t == "Worked example"]
report(len(DEMO) == 3 and len(YT) == 3 and sorted(WORK) == ["Worked example 3", "Worked example 4"] and len(WFT) == 1,
       "lesson structure", f"{len(DEMO)} demos, {len(YT)} your turns, worked {sorted(WORK)} + {len(WFT)} from the text")
report(len(re.findall(r"\{\{sec:teal:key:Concept (\d)", teach)) == 3, "three concepts", "")
report('<div class="box take"><div class="bt">6 Expected value of a discrete probability distribution</div>' in teach, "Box 6 present", "")


def src(key):
    if key not in BLK:
        raise LookupError(f"answer block {key} missing")
    return BLK[key]


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\|</td>|<br>|</span>).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def chain(block, template, expected, where, min_sides=2):
    label = f"{where}: {template}"
    try:
        (g,) = grab(block, template, where)
        sides = [t for t in g.split("=") if t.strip()]
        vals = [val(t) for t in sides]
        report(len(sides) >= min_sides and all(v == expected for v in vals), label, f"printed {g}, expected {expected}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def value(block, template, expected, where):
    label = f"{where}: {template}"
    try:
        got = grab(block, template, where)
        exp = expected if isinstance(expected, tuple) else (expected,)
        ok = len(got) == len(exp) and all(val(g) == e for g, e in zip(got, exp))
        report(ok, label, f"printed {got}, expected {exp}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def tables(block):
    out = []
    for t in re.findall(r'<table class="t"[^>]*>(.*?)</table>', block, re.S):
        rows = [[strip(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)] for r in re.findall(r"<tr>(.*?)</tr>", t, re.S)]
        out.append(rows)
    return out


def hnorm(h):
    return re.sub(r"\s+|\\text\{|\}|\{", "", h)


def ev(d):
    return sum(F(x) * p for x, p in d.items())


def ev_table(block, k, d, where, names=("x", "p(x)", "xp(x)"), columns=False, show_x=None):
    """Table k: rows (or columns) x / p(x) / xp(x) with a final Sum entry.  d: {x: probability}."""
    label = f"{where} table {k + 1}"
    try:
        tb = tables(block)[k]
        if columns:
            tb = [list(r) for r in zip(*tb)]
        if len(tb) != 3:
            raise ValueError(f"{len(tb)} rows")
        hx, hp, hxp = tb
        heads_ok = (hnorm(hx[0]), hnorm(hp[0]), hnorm(hxp[0])) == tuple(hnorm(n) for n in names)
        sum_ok = hx[-1] == "Sum"
        xs = [val(c) for c in hx[1:-1]]
        ps = [val(c) for c in hp[1:-1]]
        xps = [val(c) for c in hxp[1:-1]]
        ok = heads_ok and sum_ok and xs == [F(x) for x in d] and ps == list(d.values())
        ok = ok and all(xp == x * p for x, p, xp in zip(xs, ps, xps))
        ok = ok and val(hp[-1]) == sum(ps) == 1 and val(hxp[-1]) == ev(d)
        report(ok, label, f"x {hx[1:-1]} | p {hp[1:]} | xp {hxp[1:]} ; E = {ev(d)}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def dist(outcomes, key=lambda o: o):
    outcomes = list(outcomes)
    d = {}
    for o in outcomes:
        kk = key(o)
        d[kk] = d.get(kk, 0) + F(1, len(outcomes))
    return dict(sorted(d.items()))


WORDS = {"no": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "twelve": 12, "sixteen": 16, "twenty": 20}


def cash_people(stmt):
    """'One has $560 cash, four have $350 cash, ... Five have no cash' -> list of amounts, one per person."""
    t = plain(stmt)
    people = []
    for w, amt in re.findall(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:has|have)\s+\$(\d+)\s+cash", t, re.I):
        people += [int(amt)] * WORDS[w.lower()]
    for w in re.findall(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+have\s+no\s+cash", t, re.I):
        people += [0] * WORDS[w.lower()]
    total = WORDS[re.search(r"\b(\w+) friends", t).group(1).lower()]
    return people, total


# ================================================================ LESSON: concept boxes
coins4 = dist(product("HT", repeat=4), key=lambda o: o.count("H"))
rob = pick = thief = {}
try:
    tb = tables(teach)
    t1, t2 = tb[0], tb[1]
    ok = [val(c) for c in t1[0][1:]] == list(coins4) and [val(c) for c in t1[1][1:]] == list(coins4.values()) and hnorm(t1[1][0]) == "P(X=x)"
    ok = ok and t2[0] == t1[0] and t2[1][1:] == t1[1][1:] and hnorm(t2[1][0]) == "p(x)"
    report(ok, "Concept 1: the four-coin tables (P(X = x) and p(x)), enumerated", " | ".join(t1[1][1:]))
except Exception as err:
    report(False, "Concept 1 tables", f"ERROR {err}")
E4 = ev(coins4)
chain(teach, r"\[\text{mean}=\frac{0+1+2+3+4}{5}=@.\]", F(sum(range(5)), 5), "ordinary mean", 2)
chain(teach, r"\[\text{mean}=0\times\tfrac15+1\times\tfrac15+2\times\tfrac15+3\times\tfrac15+4\times\tfrac15=@.\]", F(sum(range(5)), 5), "mean with weights 1/n", 2)
try:
    hits = re.findall(r"\\\[\\begin\{aligned\}\\text\{weighted mean\}&amp;=(.*?),\\ \\text\{which is called", teach, re.S)
    if len(hits) != 1:
        raise LookupError(f"weighted mean display found {len(hits)} times")
    g = hits[0]
    lines = [s.strip().lstrip("&amp;=").strip() for s in g.split("\\\\")]
    first = sym(lines[0])
    terms = [x * p for x, p in coins4.items()]
    second = [val(t) for t in lines[1].split("+")]
    report(F(str(sp.nsimplify(first))) == E4 and second == terms and val(lines[2]) == E4 and val(lines[3]) == E4 == 2,
           "weighted mean of the four coins: each line", " | ".join(lines))
except Exception as err:
    report(False, "weighted mean display", f"ERROR {err}")
ev_table(teach, 2, coins4, "setting out (rows)")
ev_table(teach, 3, coins4, "setting out (columns)", columns=True)
report("\\(\\text{E}(X)=\\sum xp(x)\\), summing over all values of the distribution." in teach, "formula E(X) = sum x p(x)", "")

# Worked example (from the text): no values beyond the graph; Worked example 3: the robbery
try:
    people, total = cash_people(WORK["Worked example 3"])
    report(len(people) == total == 20, "Worked example 3: 20 friends in the statement", str(sorted(people)))
    rob = dist(people)
    ev_table(WORK["Worked example 3"], 0, rob, "Worked example 3")
    value(WORK["Worked example 3"], MONEY + "@</span>.</p>", ev(rob), "Worked example 3 expected gain")
except Exception as err:
    report(False, "Worked example 3", f"ERROR {err}")
die = dist(range(1, 7))
ev_table(WORK["Worked example 4"], 0, die, "Worked example 4")
value(WORK["Worked example 4"], r"Each value has probability \(@\)", F(1, 6), "Worked example 4")
value(WORK["Worked example 4"], r"the expected value on the die is \(\mu=@\).", ev(die), "Worked example 4 mu")
try:
    (g,) = grab(WORK["Worked example 4"], r"in Worked example 3: the expected value was " + MONEY + "@</span>", "WE4 back-reference")
    report(F(g) == ev(rob) and F(g) not in [F(p) for p in people], "WE4: $140 is Example 3's expected value and nobody had $140", g)
except Exception as err:
    report(False, "WE4 back-reference", f"ERROR {err}")

# ================================================================ lesson examples C1-C3
d6 = range(1, 7)
d4 = range(1, 5)
sum2 = dist(product(d6, repeat=2), key=sum)
tsum = dist(product(d4, repeat=2), key=sum)
report("Two dice are thrown, and \\(X\\) is the sum of the two numbers showing." in DEMO[0] and "each with its four faces numbered 1, 2, 3 and 4" in YT[0], "C1 statements", "")


def p_table(block, k, d, where):
    label = f"{where} table {k + 1}"
    try:
        hx, hp = tables(block)[k]
        ok = hnorm(hx[0]) == "x" and hnorm(hp[0]) == "p(x)" and [val(c) for c in hx[1:]] == list(d) and [val(c) for c in hp[1:]] == list(d.values())
        report(ok and sum(val(c) for c in hp[1:]) == 1, label, " | ".join(hp[1:]))
    except Exception as err:
        report(False, label, f"ERROR {err}")


c1 = src("C1").split("<b>Your turn.</b>")
p_table(c1[0], 0, sum2, "C1 demo")
p_table(c1[1], 0, tsum, "C1 your turn")
try:
    pairs = sorted((int(a), int(b)) for a, b in re.findall(r"\\\(\((\d),(\d)\)\\\)", c1[0]))
    report(pairs == sorted(o for o in product(d6, repeat=2) if sum(o) == 7), "C1 demo: the six pairs with sum 7", str(pairs))
    pairs = sorted((int(a), int(b)) for a, b in re.findall(r"\\\(\((\d),(\d)\)\\\)", c1[1]))
    report(pairs == sorted(o for o in product(d4, repeat=2) if sum(o) == 5), "C1 your turn: the four pairs with sum 5", str(pairs))
except Exception as err:
    report(False, "C1 pairs", f"ERROR {err}")
for blk, d, c, who in ((c1[0], sum2, 7, "demo"), (c1[1], tsum, 5, "your turn")):
    sym_ok = all(d.get(c - j, 0) == d.get(c + j, 0) for j in range(0, 12))
    value(blk, r"symmetric about \(x=@\)", F(c), f"C1 {who}: axis of symmetry")
    value(blk, r"centre of the distribution is \(x=@\).", F(c), f"C1 {who}: centre")
    report(sym_ok and ev(d) == c, f"C1 {who}: the distribution is symmetric about {c} (and E(X) = {ev(d)})", "")

# C2: the pickpocket (rows) and the thief (columns), data read from the statements
c2 = src("C2").split("<b>Your turn.</b>")
try:
    people, total = cash_people(DEMO[1])
    report(len(people) == total == 16, "C2 demo: 16 friends in the statement", str(sorted(people)))
    pick = dist(people)
    ev_table(c2[0], 0, pick, "C2 demo")
    value(c2[0], r"Each friend is chosen with probability \(@\).", F(1, total), "C2 demo")
    value(c2[0], "expected gain is " + MONEY + "@</span>.", ev(pick), "C2 demo expected gain")
except Exception as err:
    report(False, "C2 demo", f"ERROR {err}")
try:
    people, total = cash_people(YT[1])
    report(len(people) == total == 10, "C2 your turn: 10 friends in the statement", str(sorted(people)))
    thief = dist(people)
    ev_table(c2[1], 0, thief, "C2 your turn (columns)", columns=True)
    value(c2[1], r"Each friend is chosen with probability \(@\).", F(1, total), "C2 your turn")
    value(c2[1], "expected gain is " + MONEY + "@</span>.", ev(thief), "C2 your turn expected gain")
except Exception as err:
    report(False, "C2 your turn", f"ERROR {err}")

# C3: uniform dice
c3 = src("C3").split("<b>Your turn.</b>")
oct8 = dist(range(1, 9))
dod = dist(range(1, 13))
report("eight faces numbered 1 to 8" in DEMO[2] and "twelve faces numbered 1 to 12" in YT[2], "C3 statements", "")
ev_table(c3[0], 0, oct8, "C3 demo")
value(c3[0], r"Each value has probability \(@\).", F(1, 8), "C3 demo")
chain(c3[0], r"Hence \(\mu=@\).", ev(oct8), "C3 demo mu", 2)
value(c3[1], r"Each value has probability \(@\).", F(1, 12), "C3 your turn")
try:
    (g,) = grab(c3[1], r"The \(xp(x)\) row is \(@\)", "C3 your turn row")
    report([val(t) for t in g.split(",") if "dots" not in t] == [F(1, 12), F(2, 12), F(12, 12)], "C3 your turn: xp row 1/12, 2/12, ..., 12/12", g)
except Exception as err:
    report(False, "C3 your turn row", f"ERROR {err}")
try:
    (g,) = grab(c3[1], r"\[\text{E}(X)=\tfrac{1+2+\cdots+12}{12}=@.\]", "C3 your turn E")
    report(all(val(t) == ev(dod) for t in g.split("=")) and sum(range(1, 13)) == 78, "C3 your turn: E(X) = 78/12 = 6 1/2", g)
except Exception as err:
    report(False, "C3 your turn E", f"ERROR {err}")
value(c3[1], r"So \(\mu=@\).", ev(dod), "C3 your turn mu")
for blk, d, who in ((c3[0], oct8, "demo"), (c3[1], dod, "your turn")):
    report("This is not one of the numbers on the die." in blk and ev(d) not in d, f"C3 {who}: mu is not a face value", str(ev(d)))

# ================================================================ textbook homework
def q_dist(qblock, k, names=("x", "p(x)")):
    """A printed exercise table: values row and probability row -> {x: p}."""
    tb = tables(qblock)[k]
    hx, hp = tb[0], tb[1]
    if hnorm(hx[0]) != names[0] or hnorm(hp[0]) != names[1]:
        raise ValueError(f"headers {hx[0]!r}, {hp[0]!r}")
    cols = [i for i in range(1, len(hx)) if hx[i] != "Sum"]
    return {val(hx[i]): val(hp[i]) for i in cols}


# Q1
for k, part in enumerate("abc"):
    try:
        d = q_dist(TQ["1"], k)
        report(sum(d.values()) == 1, f"Q1{part} printed table adds to 1", "")
        blk = re.search(rf"<b>{part}</b>(.*?)(?=<b>[a-z]</b>|$)", src("1"), re.S).group(1)
        ev_table(blk, 0, d, f"A1{part}")
        value(blk, r"Hence \(\text{E}(X)=@\).", ev(d), f"A1{part}")
    except Exception as err:
        report(False, f"A1{part}", f"ERROR {err}")

# Q2: payout by die face, from the statement
try:
    st = plain(TQ["2"])
    report("charged 40 cents if the die shows 1, 2 or 3, they are charged nothing for 4, and they receive 30 cents or 60 cents respectively for 5 or 6" in st, "Q2 statement", "")
    pay = {1: -40, 2: -40, 3: -40, 4: 0, 5: 30, 6: 60}
    g2 = dist(d6, key=lambda f: pay[f])
    tq = tables(TQ["2"])[0]
    report([val(r[0]) for r in tq[1:-1]] == list(g2), "Q2 printed x column", str([r[0] for r in tq]))
    ev_table(src("2"), 0, g2, "A2a (columns)", columns=True)
    value(src("2"), r"<b>b</b> Expected value \(=@\)", ev(g2), "A2b")
    value(src("2"), r"per game is @ cents.", -ev(g2), "A2c")
    value(src("2"), r"\(100\times(-5)=@\) cents.", 100 * ev(g2), "A2d")
    value(src("2"), r"the casino expects to make @ cents profit", -100 * ev(g2), "A2d casino")
except Exception as err:
    report(False, "A2", f"ERROR {err}")

# Q3 (simulation): no answer; the printed theory table and the predicted frequencies
try:
    ev_table(TQ["3"], 0, coins4, "Q3 theory table")
    m = re.search(r"the results ([\d, ]+) that the theoretical", TQ["3"]).group(1)
    report([int(v) for v in m.split(",")] == [int(32 * p) for p in coins4.values()], "Q3 predicted frequencies (32 trials)", m)
    m = re.search(r"probabilities ([\d., ]+)\. If", TQ["3"]).group(1)
    report([F(v) for v in m.split(", ")] == list(coins4.values()), "Q3 probabilities as decimals", m)
    report("3" not in BLK, "Q3 has no answer block (simulation)", "")
except Exception as err:
    report(False, "Q3", f"ERROR {err}")

# Q4 (x_i, p_i)
for k, part in enumerate("ab"):
    try:
        d = q_dist(TQ["4"], k, names=("x_i", "p_i"))
        blk = re.search(rf"<b>{part}</b>(.*?)(?=<b>[a-z]</b>|$)", src("4"), re.S).group(1)
        ev_table(blk, 0, d, f"A4{part}", names=("x_i", "p_i", "x_ip_i"))
        value(blk, r"So \(\text{E}(X)=@\).", ev(d), f"A4{part}")
    except Exception as err:
        report(False, f"A4{part}", f"ERROR {err}")

# Q5: a box chosen at random, then an item from it
try:
    st = plain(TQ["5"])
    pr = dict((w.lower(), F(v)) for w, v in re.findall(r"an? (pencil|eraser|pen) costs \$(\d+(?:\.\d+)?)", st, re.I))
    nb = dict((w, WORDS[n]) for n, w in re.findall(r"(\w+) boxes of (pencils|erasers|pens)", st))
    boxes = [pr["pencil"]] * nb["pencils"] + [pr["eraser"]] * nb["erasers"] + [pr["pen"]] * nb["pens"]
    d5 = dist(boxes)
    blk = src("5").split("<b>b</b>")[0]
    ev_table(blk, 0, d5, "A5a")
    value(blk, "The expected value is " + MONEY + "@</span>.", ev(d5), "A5a")
    value(src("5"), "the expected cost is " + MONEY + "@</span>.", 100 * ev(d5), "A5b (Fiona and her 99 friends)")
    report("Fiona and her 99 friends" in TQ["5"], "Q5 b: 100 people", "")
except Exception as err:
    report(False, "A5", f"ERROR {err}")

# Q6: X, Y = 2X, Z = X + 1
try:
    dX = q_dist(TQ["6"], 0, names=("x", "P(X=x)"))
    dY = q_dist(TQ["6"], 1, names=("y", "P(Y=y)"))
    dZ = q_dist(TQ["6"], 2, names=("z", "P(Z=z)"))
    report(dY == {2 * x: p for x, p in dX.items()} and dZ == {x + 1: p for x, p in dX.items()} and sum(dX.values()) == 1, "Q6 printed tables are X, 2X, X + 1", "")
    value(src("6"), r"<b>a</b> \(\text{E}(X)=@\)", ev(dX), "A6a")
    value(src("6"), r"(i) \(\text{E}(Y)=@\)", ev(dY), "A6b(i)")
    value(src("6"), r"(i) \(\text{E}(Z)=@\)", ev(dZ), "A6c(i)")
    report(ev(dY) == 2 * ev(dX) and ev(dZ) == ev(dX) + 1 and src("6").count("(ii) Yes") == 2, "A6 (ii): both agree", "")
except Exception as err:
    report(False, "A6", f"ERROR {err}")

# Q7: E(aX + b) with E(X) = 5
try:
    e7 = F(int(re.search(r"the property that \\\(\\text\{E\}\(X\)=(\d+)\\\)", TQ["7"]).group(1)))
    forms = re.findall(r'<span class="pl">([a-f])</span>\\\(\\text\{E\}(.*?)\\\)</span>', TQ["7"])
    for part, expr in forms:
        e = strip(expr).replace("\\big", "")
        lin = sp.expand(parse_expr(_conv(e), local_dict={"X": sp.Symbol("X")}, transformations=TR))
        a_, b_ = sp.Poly(lin, sp.Symbol("X")).all_coeffs() if sp.Poly(lin, sp.Symbol("X")).degree() == 1 else (0, lin)
        want = F(str(a_)) * e7 + F(str(b_))
        tpl = rf"<b>{part}</b> \(@\)" if part == "c" else (r"<b>f</b> @</div>" if part == "f" else rf"<b>{part}</b> @ ")
        value(src("7"), tpl, want, f"A7{part} E{strip(expr)}")
    report(len(forms) == 6, "Q7 six parts", str([f for f, _ in forms]))
except Exception as err:
    report(False, "A7", f"ERROR {err}")

# Q8: three coins
c3c = dist(product("HT", repeat=3), key=lambda o: o.count("H"))
ev_table(src("8"), 0, c3c, "A8")
value(src("8"), r"The expected value is \(@\), as might", ev(c3c), "A8")

# Q9: two cards without replacement, number of hearts (all 52 x 51 ordered pairs)
deck = [(r, s) for s in "HDSC" for r in range(13)]
hearts = dist(permutations(deck, 2), key=lambda o: sum(c[1] == "H" for c in o))
ev_table(src("9"), 0, hearts, "A9")
value(src("9"), r"The expected value is \(@\).", ev(hearts), "A9")

# Q10: difference of two dice
diff = dist(product(d6, repeat=2), key=lambda o: abs(o[0] - o[1]))
report(list(diff) == [0, 1, 2, 3, 4, 5] and "the integers 0, 1, 2, 3, 4, 5" in TQ["10"], "Q10 sample space 0-5", "")
ev_table(src("10"), 0, diff, "A10d")
value(src("10"), r"Hence \(\text{E}(X)=@\).", ev(diff), "A10d")

# Q11: the weighted die, 50% more likely to show each of 1, 2, 3 than each of 4, 5, 6
try:
    report("50% more likely to turn up each of the results 1, 2 or 3 as to turn up 4, 5 or 6" in TQ["11"], "Q11 statement", "")
    faces = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6, 6]           # weights 3 : 2 (50% more), as 15 equally likely tickets
    w = dist(faces)
    report(w[1] == F(3, 2) * w[4], "Q11 weights: 1.5 times as likely", "")
    (g,) = grab(src("11"), r"<b>a</b> \(@\)<br>", "A11a")
    report([val(t) for t in g.split(",\\ ")] == [w[f] for f in d6], "A11a probabilities of 1-6", g)
    e11 = sum(F(pay[f]) * w[f] for f in d6)
    value(src("11"), r"<b>b</b> \(@\), so the bank", e11, "A11b")
    value(src("11"), r"expects to make @ cents each game", -e11, "A11b bank")
except Exception as err:
    report(False, "A11", f"ERROR {err}")

# Q12: slot machine, fruit ratio 1 : 2 : 3 in each position, payouts 11 : 2 : 1
try:
    report("in the ratio \\(1:2:3\\)" in TQ["12"] and "in the ratio \\(11:2:1\\)" in TQ["12"] and "feeding a " + MONEY + "1</span> coin" in TQ["12"], "Q12 statement", "")
    reel = ["O"] + ["S"] * 2 + ["A"] * 3
    rolls = dist(product(reel, repeat=3), key=lambda o: "".join(o) if len(set(o)) == 1 else "Other")
    po = {"OOO": 11 * K, "SSS": 2 * K, "AAA": K, "Other": 0}
    value(src("12"), r"\(P(\text{Orange})=@\), \(P(\text{Strawberry})=@\), \(P(\text{Apple})=@\)", (F(1, 6), F(2, 6), F(3, 6)), "A12a")
    hd, xs, ps = tables(src("12"))[0]
    order = hd[1:-1]
    ok = order == ["OOO", "SSS", "AAA", "Other"] and all(sp.simplify(sym(xs[i + 1]) - po[o]) == 0 for i, o in enumerate(order))
    ok = ok and [val(p) for p in ps[1:-1]] == [rolls[o] for o in order] and val(ps[-1]) == 1
    report(ok, "A12b table (6^3 rolls enumerated)", " | ".join(ps[1:]))
    epay = sum(po[o] * sp.Rational(rolls[o].numerator, rolls[o].denominator) for o in po)
    ksol = sp.solve(sp.Eq(epay, 1), K)
    report(ksol == [4], "A12c: break even gives k = 4", str(ksol))
    (g,) = grab(src("12"), MONEY + r"1</span> paid in: \(\text{E}(X)=@\), so", "A12c chain")
    sides = g.split("=")
    report(all(sp.simplify(sym(s) - epay) == 0 for s in sides[:-1]) and val(sides[-1]) == 1, "A12c chain equals E(payout) and 1", g)
    value(src("12"), r"so \(k=@\) and", F(4), "A12c k")
    value(src("12"), r"OOO pays \(11k=@\) dollars", F(11 * 4), "A12c OOO")
    value(src("12"), "The payout will be " + MONEY + "@</span>", F(44), "A12c payout")
    value(src("12"), "profit would be " + MONEY + "@</span>, accounting", F(44 - 1), "A12c profit")
except Exception as err:
    report(False, "A12", f"ERROR {err}")

# Q13: Wulf, mu = sum n / 2^n = 2
nn = sp.Symbol("n", integer=True, positive=True)
mu = sp.summation(nn / 2 ** nn, (nn, 1, sp.oo))
report(mu == 2, "Q13 sum n/2^n = 2 (sympy)", str(mu))
try:
    (g,) = grab(src("13"), r"Subtracting (3) from (4), \(\mu=@\).", "A13b")
    report(val(g) == mu, "A13b mu", g)
    disp = re.search(r"\\\[\\begin\{aligned\}(.*?)\\end\{aligned\}\\\]", src("13"), re.S).group(1)
    rows = [r for r in disp.split("\\\\")]

    def series(row):
        rhs = row.split("&amp;=")[1].split("&amp;&amp;")[0]
        return [t for t in rhs.split("+") if "cdots" not in t]
    s1, s2, s3, s4 = (series(r) for r in rows)
    v1 = [sym(t) for t in s1]
    v2 = [sym(t) for t in s2]
    v3 = [sym(t) for t in s3]
    v4 = [sym(t) for t in s4]
    ok = v1 == [sp.Rational(n, 2 ** n) for n in range(1, 7)] and v2 == [2 * x for x in v1]
    ok = ok and v3 == [sp.Rational(1, 2 ** n) for n in range(0, 6)] and v4 == [2 * x for x in v3]
    report(ok, "A13b series (1)-(4): first six terms", "")
    report(sp.summation(sp.Rational(1, 1) / 2 ** (nn - 1), (nn, 1, sp.oo)) == mu, "A13 series (3) also sums to 2", "")
    report("expect to get a head on the second throw" in src("13"), "A13c second throw", "")
except Exception as err:
    report(False, "A13", f"ERROR {err}")
report("show that" in TQ["13"] and "2\\mu-\\mu=1+\\tfrac12+\\tfrac14+\\tfrac18+\\tfrac1{16}+\\tfrac1{32}+\\cdots" in TQ["13"], "Q13 statement series", "")

# Q14: St Petersburg, each term 2^n x 1/2^n = 1
try:
    (g,) = grab(src("14"), r"\(\begin{aligned}\text{E}(X)&amp;=@\\&amp;=", "A14")
    terms = [t for t in g.split("+") if "cdots" not in t]
    report([sym(t) for t in terms] == [sp.Integer(1)] * 4 and [strip(t) for t in terms][0] == "2\\times\\tfrac12".replace("\\tfrac", "\\tfrac"), "A14 first terms each 1", g)
    report(sp.summation(2 ** nn * sp.Rational(1, 1) / 2 ** nn, (nn, 1, sp.oo)) == sp.oo and "\\to\\infty" in src("14"), "A14 E(X) -> infinity", "")
    report("initially contains " + MONEY + "2</span>" in TQ["14"] and "charged " + MONEY + "40</span>" in TQ["14"], "Q14 statement", "")
except Exception as err:
    report(False, "A14", f"ERROR {err}")

report(all(q in TQ and "[Simulation experiment]" not in TQ[q] for q in ("8", "9", "11", "12")), "timed-practice questions exist and are not simulations", "")
want_blocks = ["1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "C1", "C2", "C3"]
report(sorted(BLK, key=lambda t: (len(t), t)) == sorted(want_blocks, key=lambda t: (len(t), t)), "answer blocks (Q3 is a simulation with no answer)", str(sorted(BLK, key=lambda t: (len(t), t))))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 15)], "textbook questions 1-14", str(sorted(TQ, key=int)))
report(re.findall(r"\{\{band:([FDE])\}\}", hw) == ["F", "D", "E"] and hw.index("{{band:D}}") < hw.index('q-num">5<') and hw.index('q-num">4<') < hw.index("{{band:D}}")
       and hw.index("{{band:E}}") < hw.index('q-num">11<') and hw.index('q-num">10<') < hw.index("{{band:E}}"), "bands F 1-4, D 5-10, E 11-14", "")

# ================================================================ figures (recorded from figs.build_13b)
sys.path.insert(0, os.path.join(HERE, "..", "build"))
sys.path.insert(0, SRC)
try:
    import figs                                    # noqa: E402
    rec = {}
    figs.dist_graph = lambda name, xs, ps, yt, **kw: rec.__setitem__(name, (list(xs), [F(p) for p in ps], [F(v) for v, _ in yt], [lab for _, lab in yt], kw))
    figs.build_13b()
    want = {"c13b_coins": coins4, "c13b_rob": rob, "c13b_die": die, "a13b_sum": sum2, "a13b_tsum": tsum,
            "a13b_pick": pick, "a13b_thief": thief, "a13b_oct": oct8, "a13b_dodec": dod}
    for name, d in want.items():
        xs, ps, yv, ylab, kw = rec[name]
        ok = xs == list(d) and ps == list(d.values()) and set(yv) <= set(ps) | {F(k, 20) for k in range(1, 6)} | {F(k, 16) for k in range(1, 5)}
        ok = ok and all(val(lb) == v for v, lb in zip(yv, ylab)) and kw.get("ylab") == "p(x)"
        report(ok and os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}", f"x {xs}, P {[str(p) for p in ps]}")
        report((les + ans).count("{{svg:" + name + "}}") == 1, f"figure {name} used once", "")
    report(set(rec) == set(want), "figures: build_13b draws exactly these", str(sorted(rec)))
except Exception as err:
    report(False, "figures", f"ERROR {err}")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{NCHECK[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
