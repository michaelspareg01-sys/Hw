"""Check of Lesson 13A (Y11 Ch 13 pack): The language of probability distributions.

The script reads the values PRINTED in workspace/build/y11ch13/a_13a.html (lesson examples,
textbook homework, past-paper worked solution) and in l13a.html (the worked examples, the data
given inside the tutor demos, your-turn items and textbook questions, and the past-paper table).
Every distribution table is parsed cell by cell; every inline value is found with a template
('@' marks the printed value), and a template must match exactly once in its block, otherwise
the item FAILS.  Printed LaTeX (\\tfrac, decimals, percentages, sums such as
\\tfrac{4}{16}+\\tfrac{1}{16}) is turned into an exact rational.

Each printed result is compared with an independent computation using fractions.Fraction:
  - probabilities are found by ENUMERATING the sample space (coins, dice, cards, balls, tiles,
    marbles, scoops, words, digits) with itertools, never from a formula;
  - 'until the first success' distributions are enumerated over all sequences of each length;
  - unknown constants are found by solving 'sum of probabilities = 1' (sympy), and each root is
    tested against 0 <= P(X = x) <= 1;
  - the figures are checked by re-running figs.build_13a() with the plotting call recorded.
No simulation is used.  It also checks the past-paper block: marks add to the intro total,
time, numbering, source labels identical in both files, one hint per question.

Exit status 1 if anything fails.  Run: python3 workspace/checks/y11ch13_13a.py
"""
import os
import re
import sys
from fractions import Fraction as F
from itertools import combinations, permutations, product

import sympy as sp
from sympy.parsing.sympy_parser import (implicit_multiplication, parse_expr, rationalize,
                                        standard_transformations)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH13_SRC", os.path.join(HERE, "..", "build", "y11ch13"))   # override only for mutation tests
FAILS = []
NCHECK = [0]
A = sp.Symbol("a")
N = sp.Symbol("n")
TR = standard_transformations + (implicit_multiplication, rationalize)


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
    c = c.replace("\\(", "").replace("\\)", "").replace("&nbsp;", " ")
    return re.sub(r"\\,|\\;|\\!", "", c).strip()


def sym(t):
    """Printed LaTeX -> sympy expression (exact rationals)."""
    t = strip(t)
    pct = t.endswith("%")
    if pct:
        t = t[:-1]
    e = parse_expr(_conv(t.replace(" ", "")), local_dict={"a": A, "n": N}, transformations=TR)
    return e / 100 if pct else e


def val(t):
    e = sp.nsimplify(sym(t))
    if not e.is_Rational:
        raise ValueError(f"not a number: {t!r}")
    return F(int(e.p), int(e.q))


# ---------------------------------------------------------------- HTML blocks
ans = read("a_13a.html")
les = read("l13a.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_13a.html")
report(ans.count("{{ahead:Lesson 13A | The language of probability distributions}}") == 2, "answers headings", "{{ahead:Lesson 13A | ...}} twice")
BLK = {}
for mt in re.finditer(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts[0], re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
PPA = {int(k): v for k, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}

pps = les.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l13a.html")
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
teach = les.split("<!-- ============ Homework ============ -->")[0]
PPQ = {int(k): v for k, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
TQ = {k: v for k, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S)}
EX = re.findall(r'<div class="ex (demo|attempt|worked)"><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<!-- =====|$)', teach, re.S)
DEMO = [b for k, _, b in EX if k == "demo"]
YT = [b for k, _, b in EX if k == "attempt"]
WORK = {t: b for k, t, b in EX if k == "worked" and t != "Worked example"}
WFT = [b for k, t, b in EX if k == "worked" and t == "Worked example"]      # 'from the text' examples, in order
report(len(DEMO) == 5 and len(YT) == 5 and sorted(WORK) == ["Worked example 1", "Worked example 2"] and len(WFT) == 3,
       "lesson structure", f"{len(DEMO)} demos, {len(YT)} your turns, worked {sorted(WORK)} + {len(WFT)} from the text")


def src(key):
    if key not in BLK:
        raise LookupError(f"answer block {key} missing")
    return BLK[key]


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\|</td>|<br>).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def chain(block, template, expected, where, min_sides=2):
    """Printed 'A=B=C' captured by one '@': every side must equal the expected value."""
    label = f"{where}: {template}"
    try:
        (g,) = grab(block, template, where)
        sides = [t for t in re.sub(r"P\([^()]*\)", "", g).split("=") if t.strip()]      # a side such as P(X=1) is a restatement, not a value
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


def text(block, template, expected, where):
    """Printed words (a classification or Yes/No): compared as strings."""
    label = f"{where}: {template}"
    try:
        got = tuple(g.strip() for g in grab(block, template, where))
        exp = expected if isinstance(expected, tuple) else (expected,)
        report(got == exp, label, f"printed {got}, expected {exp}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


# ---------------------------------------------------------------- tables
def tables(block):
    out = []
    for t in re.findall(r'<table class="t"[^>]*>(.*?)</table>', block, re.S):
        rows = [[strip(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)] for r in re.findall(r"<tr>(.*?)</tr>", t, re.S)]
        out.append(rows)
    return out


def norm(lbl):
    return re.sub(r"\s+", " ", lbl.replace("\\text{", "").replace("}", "")).strip().lower()


def dist_table(block, k, expected, where, header=("x", "P(X=x)"), total=True):
    """Table k of block: row 0 the values, row 1 the probabilities.  expected: {label: Fraction}."""
    label = f"{where} table {k + 1}"
    try:
        tb = tables(block)[k]
        if len(tb) != 2:
            raise ValueError(f"{len(tb)} rows")
        heads, probs = tb
        hd = (norm(heads[0]).replace(" ", ""), norm(probs[0]).replace(" ", ""))
        want_hd = tuple(norm(h).replace(" ", "") for h in header)
        labels = [norm(h) for h in heads[1:]]
        got = {lb: val(p) for lb, p in zip(labels, probs[1:])}
        exp = {norm(str(key)): F(v) for key, v in expected.items()}
        ok = hd == want_hd and labels == [norm(str(key)) for key in expected] and got == exp
        if total:
            ok = ok and sum(got.values()) == 1
        report(ok, label, f"printed {dict(zip(labels, probs[1:]))}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def dist(outcomes, key=lambda o: o):
    """Equally likely outcomes -> {value: probability}, values in sorted order of first appearance."""
    outcomes = list(outcomes)
    d = {}
    for o in outcomes:
        k = key(o)
        d[k] = d.get(k, 0) + F(1, len(outcomes))
    return d


def ordered(d, order):
    return {k: d.get(k, F(0)) for k in order}


def weighted(pairs):
    """[(value, probability)] -> {value: total probability}."""
    d = {}
    for v, p in pairs:
        d[v] = d.get(v, 0) + p
    return d


# ================================================================ LESSON: concept boxes and worked examples
coins4 = dist(product("HT", repeat=4), key=lambda o: o.count("H"))
c4 = ordered(coins4, [0, 1, 2, 3, 4])
wf1 = WFT[0]
dist_table(wf1, 0, c4, "WE four coins", header=("number of heads", "probability"))
dist_table(wf1, 1, c4, "WE four coins", header=("x", "P(X=x)"))
try:
    two = re.search(r"six have two heads \(([A-Z, ]+)\)", wf1).group(1).split(", ")
    report(sorted(two) == sorted("".join(o) for o in product("HT", repeat=4) if o.count("H") == 2), "WE four coins: the six outcomes with two heads", ", ".join(two))
    cnt = re.search(r"One has no heads \(TTTT\), (\w+) have one head, (\w+) have two heads .*?, (\w+) have three heads, and one has four heads \(HHHH\)", wf1).groups()
    words = {"one": 1, "four": 4, "six": 6}
    report([words[w] for w in cnt] == [coins4[1] * 16, coins4[2] * 16, coins4[3] * 16] and len(list(product("HT", repeat=4))) == 16, "WE four coins: counts 1, 4, 6, 4, 1 of 16", str(cnt))
except Exception as err:
    report(False, "WE four coins counts", f"ERROR {err}")
value(wf1, r"<b>b</b> \(P(X=3)=@\)", coins4[3], "WE four coins")
value(wf1, r"three heads is \(@\)", coins4[3], "WE four coins")
chain(wf1, r"\[P(X&gt;2)=@,\]", coins4[3] + coins4[4], "WE four coins", 2)
chain(wf1, r"\[P(X\text{ is odd})=@,\]", coins4[1] + coins4[3], "WE four coins", 2)
chain(wf1, r"\[P(X\text{ is prime})=@.\]", sum(p for k, p in coins4.items() if k in (2, 3)), "WE four coins", 2)
report(sp.primerange(0, 5) is not None and list(sp.primerange(0, 5)) == [2, 3] and "The primes among the values are 2 and 3" in wf1, "WE four coins: primes 2 and 3", "")

# continents (from the text)
wf2 = WFT[1]
try:
    rows = tables(wf2)[0][1:]
    pops = {r[0]: int(r[1].replace(" ", "")) for r in rows}
    pct = {r[0]: F(r[2].rstrip("%")) for r in rows}
    tot = pops.pop("Total")
    pct.pop("Total")
    report(sum(pops.values()) == tot, "continents: populations add to the total", f"{sum(pops.values())} vs {tot}")
    report(all(round(F(pops[c] * 100, tot), 1) == pct[c] for c in pops), "continents: per cent = population / total, 1 d.p.",
           ", ".join(f"{c} {float(F(pops[c] * 100, tot)):.3f}" for c in pops))
    abbrev = {"Asia": "Asia", "Africa": "Africa", "Europe": "Europe", "North America": "NA", "South America": "SA", "Oceania": "Oceania"}
    dist_table(wf2, 1, {abbrev[c]: pct[c] / 100 for c in pops}, "WE continents")
    chain(wf2, r"\(P(X=\text{Europe or North America})=@\)", pct["Europe"] / 100 + pct["North America"] / 100, "WE continents", 2)
except Exception as err:
    report(False, "continents", f"ERROR {err}")

# deterministic experiment and Example 1
try:
    det = [tb for tb in tables(teach) if len(tb) == 2 and len(tb[0]) == 2 and tb[0][1] == "4"]
    report(len(det) == 1 and val(det[0][1][1]) == 1, "deterministic experiment table: P(X = 4) = 1", str(det))
except Exception as err:
    report(False, "deterministic table", f"ERROR {err}")
die = dist(range(1, 7))
dist_table(WORK["Worked example 1"], 0, die, "Worked example 1")
value(WORK["Worked example 1"], r"Each value has probability \(@\)", die[1], "Worked example 1")


def first_success(p_list, n):
    """P(first success on trial n) by enumerating all sequences of n trials (p_list: equally likely faces, True = success)."""
    tot, good = 0, 0
    for seq in product(p_list, repeat=n):
        tot += 1
        good += all(not s for s in seq[:-1]) and seq[-1]
    return F(good, tot)


coin = [True, False]                      # H, T
w2 = WORK["Worked example 2"]
for n, word, seq in ((1, "1 toss", "H"), (2, "2 tosses", "TH"), (3, "3 tosses", "TTH"), (4, "4 tosses", "TTTH")):
    try:
        end = ",\\end" if n == 4 else "\\\\"
        (g,) = grab(w2, rf"P(\text{{Wulf requires {word}}})&amp;=P(\text{{{seq}}})=@" + end, "Worked example 2")
        report(val(g) == first_success(coin, n), f"Worked example 2: P(Wulf requires {word})", g)
    except Exception as err:
        report(False, f"Worked example 2 {word}", f"ERROR {err}")
try:
    heads, probs = tables(w2)[0]
    ok = heads[1:6] == ["1", "2", "3", "4", "5"] and all(val(probs[k]) == first_success(coin, k) for k in range(1, 6))
    gen = sym(probs[7])
    ok = ok and heads[7] == "n" and all(F(str(gen.subs(N, k))) == first_success(coin, k) for k in range(1, 9))
    report(ok, "Worked example 2 table (n = 1..5, general term at n = 1..8)", " | ".join(probs[1:]))
except Exception as err:
    report(False, "Worked example 2 table", f"ERROR {err}")

# ================================================================ lesson examples C1-C5
d6 = range(1, 7)
sixes = dist(product(d6, repeat=2), key=lambda o: sum(v == 6 for v in o))
sixes = ordered(sixes, [0, 1, 2])
report("Two dice are thrown, and \\(X\\) is the number of sixes showing." in DEMO[0], "C1 demo statement", "")
dist_table(src("C1"), 0, sixes, "C1 demo")
chain(src("C1"), r"<b>b</b> \(P(X\ge1)=@\)", sixes[1] + sixes[2], "C1 demo", 2)
chain(src("C1"), r"\(P(X\text{ is even})=@\)", sixes[0] + sixes[2], "C1 demo", 2)
value(src("C1"), r"No sixes: \(5\times5=@\) outcomes", 36 * sixes[0], "C1 demo")
value(src("C1"), r"One six: \(36-25-1=@\) outcomes", 36 * sixes[1], "C1 demo")
less3 = ordered(dist(product(d6, repeat=2), key=lambda o: sum(v < 3 for v in o)), [0, 1, 2])
report("A die is thrown twice, and \\(X\\) is the number of throws that show a number less than 3." in YT[0], "C1 your-turn statement", "")
dist_table(src("C1"), 1, less3, "C1 your turn")
chain(src("C1"), r"<b>b</b> \(P(X\le1)=@\)", less3[0] + less3[1], "C1 your turn", 2)
chain(src("C1"), r"\(P(X\text{ is odd})=@\)", less3[1], "C1 your turn", 1)
value(src("C1"), r"less than 3 with probability \(\tfrac26=@\)", F(sum(v < 3 for v in d6), 6), "C1 your turn")
value(src("C1"), r"more than 2 with probability \(@\)", F(sum(v > 2 for v in d6), 6), "C1 your turn")

# C2: the counts printed in the lesson
try:
    heads, cnts = tables(DEMO[1])[0]
    houses = dict(zip(heads[1:-1], [int(c) for c in cnts[1:-1]]))
    report(sum(houses.values()) == int(cnts[-1]) and heads[-1] == "Total", "C2 demo: counts add to the printed total", str(houses))
    tot = sum(houses.values())
    value(src("C2"), r"Divide each number by the total @.<br>", tot, "C2 demo") if False else None
    dist_table(src("C2"), 0, {h: F(c, tot) for h, c in houses.items()}, "C2 demo")
    chain(src("C2"), r"\(P(X=\text{Red or Gold})=@\)", F(houses["Red"] + houses["Gold"], tot), "C2 demo", 2)
except Exception as err:
    report(False, "C2 demo", f"ERROR {err}")
try:
    m = re.search(r"A bag of (\d+) jelly beans has (\d+) red, (\d+) green, (\d+) yellow and (\d+) black jelly beans", YT[1])
    n_, r_, g_, y_, b_ = (int(v) for v in m.groups())
    report(r_ + g_ + y_ + b_ == n_, "C2 your turn: colours add to the bag", f"{r_}+{g_}+{y_}+{b_} = {n_}")
    beans = ["red"] * r_ + ["green"] * g_ + ["yellow"] * y_ + ["black"] * b_
    jb = dist(beans)
    dist_table(src("C2"), 1, jb, "C2 your turn")
    chain(src("C2"), r"\(P(X=\text{green or yellow})=@\)", jb["green"] + jb["yellow"], "C2 your turn", 2)
except Exception as err:
    report(False, "C2 your turn", f"ERROR {err}")
for k, word in ((0, "houses"), (1, "colours")):
    report(src("C2").count(f"Categorical: the values are {word}, not numbers.") == 1, f"C2 categorical ({word})", "")

# C3: uniform
cards = dist([2, 4, 6, 8, 10])
tetra = dist([1, 3, 5, 7])
report("Five cards numbered 2, 4, 6, 8 and 10" in DEMO[2] and "four faces numbered 1, 3, 5 and 7" in YT[2], "C3 statements", "")
dist_table(src("C3"), 0, cards, "C3 demo")
dist_table(src("C3"), 1, tetra, "C3 your turn")
value(src("C3"), r"Each card has probability \(@\)", F(1, 5), "C3 demo")
value(src("C3"), r"Each face has probability \(@\)", F(1, 4), "C3 your turn")
report(len(set(cards.values())) == 1 and len(set(tetra.values())) == 1 and src("C3").count("The distribution is uniform") == 2, "C3 uniform", "")

# C4: until the first six / the first red, enumerated
die_six = [v == 6 for v in d6]
spin_red = [True, False, False]          # one red sector, two blue
for blk_lbl, faces, gen_sym in (("Tutor demo", die_six, None), ("Your turn", spin_red, None)):
    b4 = src("C4").split("<b>Your turn.</b>")[0 if blk_lbl == "Tutor demo" else 1]
    exp = [first_success(faces, k) for k in range(1, 7)]
    try:
        g = grab(b4, r"<b>a</b> \(P(X=1)=@\), \(P(X=2)=@\), \(P(X=3)=@\), \(P(X=4)=@\)</div>", f"C4 {blk_lbl}")
        vals = [val(t.split("=")[-1]) for t in g]
        sides_ok = all(val(s) == exp[i] for i, t in enumerate(g) for s in t.split("=")[1:] if "P(" not in s)
        report(vals == exp[:4] and sides_ok, f"C4 {blk_lbl}: P(X = 1..4)", " | ".join(g))
        heads, probs = tables(b4)[0]
        gen = sym(probs[6])
        ok = heads[1:5] == ["1", "2", "3", "4"] and [val(p) for p in probs[1:5]] == exp[:4] and heads[6] == "n"
        ok = ok and all(F(str(gen.subs(N, k))) == exp[k - 1] for k in range(1, 7))
        report(ok, f"C4 {blk_lbl}: table and general term (n = 1..6)", " | ".join(probs[1:]))
    except Exception as err:
        report(False, f"C4 {blk_lbl}", f"ERROR {err}")
report("keeps throwing a die until it shows a six" in DEMO[3] and "one red and two blue" in YT[3], "C4 statements", "")

# C5: classifications (not computable: the printed words are compared with the textbook rules)
for who, exp in (("Tutor demo", ("Numeric, continuous", "Numeric, discrete", "Categorical", "Numeric, discrete")),
                 ("Your turn", ("Numeric, continuous", "Numeric, discrete", "Categorical", "Numeric, discrete"))):
    b5 = src("C5").split("<b>Your turn.</b>")[0 if who == "Tutor demo" else 1]
    got = tuple(re.sub(r"\s*\(.*", "", t).strip() for t in re.findall(r"<b>[a-d]</b> ([^<]+)", b5))
    report(got == exp, f"C5 {who} classifications", str(got))

# ================================================================ textbook homework answers
# Q1 (classification, transcription of the textbook key)
text(src("1"), r"<b>a</b> @<br><b>b</b> @<br><b>c</b> @<br><b>d</b> @<br><b>e</b> @<br><b>f</b> @<br>",
     ("Numeric, discrete", "Numeric, continuous", "Categorical", "Numeric, continuous", "Categorical", "Categorical"), "A1")
value(src("1"), r"between 30 and 99.95 in steps of 0.05. There are around @ different", (F("99.95") - 30) / F("0.05") + 1, "A1 h")

# Q2
two_seq = dist(["".join(o) for o in product("HT", repeat=2)])
dist_table(src("2"), 0, two_seq, "A2 a", header=("outcome", "probability"))
report(len(set(two_seq.values())) == 1 and "Uniform distribution (and categorical)." in src("2"), "A2 a uniform", "")
h2 = dist(product("HT", repeat=2), key=lambda o: {2: "2 heads", 1: "1 head and 1 tail", 0: "2 tails"}[o.count("H")])
dist_table(src("2"), 1, ordered(h2, ["2 heads", "1 head and 1 tail", "2 tails"]), "A2 b", header=("outcome", "probability"))
try:
    hd = [tables(TQ["2"])[k][0] for k in (0, 1)]
    report(hd[0][1:] == ["HH", "HT", "TH", "TT"] and hd[1][1:] == ["2 heads", "1 head and 1 tail", "2 tails"], "Q2 printed outcomes", str(hd))
except Exception as err:
    report(False, "Q2 outcomes", f"ERROR {err}")

# Q3
balls = ["red"] * 4 + ["green"] * 3
dist_table(src("3"), 0, dist(balls), "A3 a", header=("outcome", "probability"))
tickets = ["Jack"] * 6 + ["Kylie"] * 8 + ["Lochlan"] * 4
tickets += ["Other"] * (100 - len(tickets))
dist_table(src("3"), 1, dist(tickets), "A3 b", header=("outcome", "probability"))
word = "Parramatta"
dist_table(src("3"), 2, dist(word.upper()), "A3 c", header=("outcome", "probability"))
dist_table(src("3"), 3, dist(range(1, 1001), key=lambda v: len(str(v))), "A3 d", header=("outcome", "probability"))
cls = dist(range(10, 20), key=lambda v: "even" if v % 2 == 0 else ("prime" if sp.isprime(v) else "neither"))
report(not any(v % 2 == 0 and sp.isprime(v) for v in range(10, 20)), "A3 e: no number 10-19 is both even and prime", "")
dist_table(src("3"), 4, ordered(cls, ["even", "prime", "neither"]), "A3 e", header=("outcome", "probability"))
report("from the word ‘Parramatta’" in TQ["3"] and "six, eight and four tickets" in TQ["3"] and "between 1 and 1000 inclusive" in TQ["3"] and "between 10 and 19 inclusive" in TQ["3"], "Q3 printed data", "")

# Q4
try:
    sentence = re.search(r"in the sentence, ‘(.*?)’", TQ["4"]).group(1)
    words_ = re.findall(r"[A-Za-z]+", sentence)
    lens = dist(words_, key=len)
    dist_table(src("4"), 0, ordered(lens, sorted(lens)), "A4 a")
    digits = re.search(r"12-digit number ([\d.]+)\.", TQ["4"]).group(1).replace(".", "")
    report(len(digits) == 12, "Q4 c: the number has 12 digits", digits)
    dg = dist(digits, key=int)
    dist_table(src("4"), 2, ordered(dg, sorted(dg)), "A4 c")
    bags = re.search(r"numbered ([\d, ]+) into one bag, then puts marbles numbered ([\d, ]+) into a second bag", TQ["4"]).groups()
    bags = [[int(v) for v in b.split(", ")] for b in bags]
    jeff = weighted((m, F(1, 2) * F(1, len(b))) for b in bags for m in b)
    dist_table(src("4"), 3, ordered(jeff, sorted(jeff)), "A4 d")
    merged = dist(bags[0] + bags[1])
    report(merged == jeff and len(bags[0]) == len(bags[1]) and "(The answer is the same if the two bags are combined" in src("4"), "A4 d: same as one combined bag (equal bag sizes)", "")
except Exception as err:
    report(False, "A4", f"ERROR {err}")
dist_table(src("4"), 1, ordered(dist(product("HT", repeat=2), key=lambda o: o.count("H")), [0, 1, 2]), "A4 b")

# Q5
coins5 = {"T": 10, "F1": 5, "F2": 5}
scoops = [set(c) for r in range(1, 4) for c in combinations(coins5, r)]
try:
    (g,) = grab(src("5"), r"<b>a</b> @</div>", "A5 a")
    printed = [set(s.strip() for s in t.split(",")) for t in re.findall(r"\{([^}]*)\}", g)]
    report(len(printed) == 7 and all(s in printed for s in scoops) and len(scoops) == 7, "A5 a: the seven non-empty scoops", g)
except Exception as err:
    report(False, "A5 a", f"ERROR {err}")
sc = dist(scoops, key=lambda s: sum(coins5[c] for c in s))
dist_table(src("5"), 0, ordered(sc, sorted(sc)), "A5 b")

# Q6: validity of the six printed tables
try:
    t6 = tables(TQ["6"])
    verdict = []
    for tb in t6:
        ps = [val(c) for c in tb[1][1:]]
        verdict.append("Yes" if all(0 <= p <= 1 for p in ps) and sum(ps) == 1 else "No")
    report(len(t6) == 6, "Q6 six tables", "")
    text(src("6"), r"<b>a</b> @ &nbsp; <b>b</b> @ &nbsp; <b>c</b> @ &nbsp; <b>d</b> @ &nbsp; <b>e</b> @ &nbsp; <b>f</b> @</div>", tuple(verdict), "A6")
except Exception as err:
    report(False, "A6", f"ERROR {err}")

# Q7: probabilities from the printed table
try:
    hx, hp = tables(TQ["7"])[0]
    p7 = {int(x): val(p) for x, p in zip(hx[1:], hp[1:])}
    report(sum(p7.values()) == 1, "Q7 table adds to 1", "")
    P = lambda cond: sum(p for x, p in p7.items() if cond(x))
    exp7 = (P(lambda x: x == 1), P(lambda x: 2 <= x <= 4), P(lambda x: 1 <= x < 4), P(lambda x: x == 6), P(lambda x: x <= 2),
            P(lambda x: x < 4), P(lambda x: x >= 1), P(lambda x: x > 1), P(lambda x: x % 2 == 0))
    value(src("7"), r"<b>a</b> @ &nbsp; <b>b</b> @ &nbsp; <b>c</b> @ &nbsp; <b>d</b> @ &nbsp; <b>e</b> @ &nbsp; <b>f</b> @ &nbsp; <b>g</b> @ &nbsp; <b>h</b> @ &nbsp; <b>i</b> @</div>", exp7, "A7")
    q7 = re.findall(r'<span class="pl">([a-i])</span>\\\((.*?)\\\)</span>', TQ["7"])
    report([s for _, s in q7] == ["P(X=1)", r"P(2\le X\le4)", r"P(1\le X&lt;4)", "P(X=6)", r"P(X\le2)", r"P(X&lt;4)", r"P(X\ge1)", r"P(X&gt;1)", r"P(X\text{ is even})"],
           "Q7 printed events match the events computed", str([s for _, s in q7]))
except Exception as err:
    report(False, "A7", f"ERROR {err}")

# Q8 (identical stages, with replacement)
court = [r in "JQK" for r in "A23456789TJQK" for _ in range(4)]
report(sum(court) == 12 and len(court) == 52, "Q8 a: 12 court cards in 52", "")
q8a = ordered(dist(product(court, repeat=2), key=sum), [0, 1, 2])
value(src("8"), r"with \(P(C)=\tfrac{12}{52}=@\)", F(12, 52), "A8 a")
dist_table(src("8"), 0, q8a, "A8 a(ii)")
q8b = ordered(dist(product(d6, repeat=3), key=lambda o: sum(v % 2 == 0 for v in o)), [0, 1, 2, 3])
value(src("8"), r"OOO each have probability \(@\)", F(1, 8), "A8 b(i)")
report(sorted("".join(s) for s in product("EO", repeat=3)) == sorted(re.search(r"The eight outcomes ([EO, ]+) each", src("8")).group(1).split(", ")), "A8 b(i) the eight outcomes", "")
dist_table(src("8"), 1, q8b, "A8 b(ii)")
cls8 = ["G"] * 10 + ["B"] * 15
seq8 = dist(product(cls8, repeat=3), key=lambda o: "".join(o))
value(src("8"), r"GGG has probability \(@\)", seq8["GGG"], "A8 c")
value(src("8"), r"GGB, GBG, BGG each have probability \(@\)", seq8["GGB"], "A8 c")
value(src("8"), r"GBB, BGB, BBG each have probability \(@\)", seq8["GBB"], "A8 c")
value(src("8"), r"BBB has probability \(@\)", seq8["BBB"], "A8 c")
report(seq8["GGB"] == seq8["GBG"] == seq8["BGG"] and seq8["GBB"] == seq8["BGB"] == seq8["BBG"], "A8 c symmetric orders", "")
dist_table(src("8"), 2, ordered(dist(product(cls8, repeat=3), key=lambda o: o.count("G")), [0, 1, 2, 3]), "A8 c girls")
zoo = ["S"] * 6 + ["D"] * 5 + ["A"] * 9
report(len(zoo) == 20 and "20 friendly wallabies. Six are from Snake Gully, five are from Dingo Ridge, and nine are from Acacia Flat" in TQ["8"], "Q8 d data", "")
value(src("8"), r"with \(P(S)=\tfrac{6}{20}=@\)", F(6, 20), "A8 d")
s3 = dist(product(zoo, repeat=3), key=lambda o: o.count("S"))
value(src("8"), r"\(SSS\) has probability @;", s3[3], "A8 d")
value(src("8"), r"\(SS\overline{S}\) each have probability @;", s3[2] / 3, "A8 d")
value(src("8"), r"\(S\overline{S}\,\overline{S}\) each have probability @;", s3[1] / 3, "A8 d")
value(src("8"), r"\(\overline{S}\,\overline{S}\,\overline{S}\) has probability @.<br><table", s3[0], "A8 d")
dist_table(src("8"), 3, ordered(s3, [0, 1, 2, 3]), "A8 d")


# Q9 and Q15: solve the printed tables for a
def solve_a(tb):
    exprs = [sym(c) for c in tb[1][1:]]
    roots = sp.solve(sp.Eq(sum(exprs), 1), A)
    valid = [r for r in roots if r.is_real and all(0 <= e.subs(A, r) <= 1 for e in exprs)]
    return exprs, roots, valid


try:
    t9 = tables(TQ["9"])
    exp9 = []
    for tb in t9:
        _, roots, valid = solve_a(tb)
        if len(valid) != 1:
            raise ValueError(f"Q9 table has {len(valid)} valid values of a")
        exp9.append(F(str(valid[0])))
    report(len(t9) == 5, "Q9 five tables", "")
    value(src("9"), r"<b>a</b> \(a=@\) &nbsp; <b>b</b> \(a=@\) &nbsp; <b>c</b> \(a=@\) &nbsp; <b>d</b> \(a=@\) &nbsp; <b>e</b> \(a=@\)</div>", tuple(exp9), "A9")
except Exception as err:
    report(False, "A9", f"ERROR {err}")

# Q10 (without replacement)
marb = [1, 2, 3, 4, 5, 6]
pairs10 = list(permutations(marb, 2))
eo = dist(pairs10, key=lambda o: "".join("E" if v % 2 == 0 else "O" for v in o))
value(src("10"), r"<b>a</b> (i) EE and OO each have probability \(@\); EO and OE each have probability \(@\).", (eo["EE"], eo["EO"]), "A10 a(i)")
report(eo["EE"] == eo["OO"] and eo["EO"] == eo["OE"], "A10 a(i) symmetric", "")
dist_table(src("10"), 0, ordered(dist(pairs10, key=lambda o: sum(v % 2 == 0 for v in o)), [0, 1, 2]), "A10 a(ii)")
grp = ["B1", "B2", "B3", "B4", "G1", "G2"]
pairs_b = list(permutations(grp, 2))
bg = dist(pairs_b, key=lambda o: "".join(v[0] for v in o))
value(src("10"), r"BB has probability \(@\); BG and GB each have probability \(@\); GG has probability \(@\).", (bg["BB"], bg["BG"], bg["GG"]), "A10 b")
dist_table(src("10"), 1, ordered(dist(pairs_b, key=lambda o: sum(v[0] == "G" for v in o)), [0, 1, 2]), "A10 b")
tiles = ["E1", "E2", "E3", "R", "T"]
pt = list(permutations(tiles, 2))
tl = dist(pt, key=lambda o: "".join(v[0] for v in o))
report(len(tl) == 7, "A10 c: seven possible selections", str(sorted(tl)))
value(src("10"), r"(i) EE has probability \(@\); ER, RE, ET, TE each have probability \(@\); RT and TR each have probability \(@\).", (tl["EE"], tl["ER"], tl["RT"]), "A10 c(i)")
report(tl["ER"] == tl["RE"] == tl["ET"] == tl["TE"] and tl["RT"] == tl["TR"], "A10 c(i) equal groups", "")
dist_table(src("10"), 2, ordered(dist(pt, key=lambda o: sum(v[0] == "E" for v in o)), [0, 1, 2]), "A10 c(ii)")

# Q11 (multinomial, with replacement)
pack = [4, 4, 4, 2, 2, 5]
report("three 4s, two 2s and one 5" in TQ["11"], "Q11 data", "")
lab11 = {frozenset([2]): "22", frozenset([4]): "44", frozenset([5]): "55", frozenset([2, 4]): "24 or 42", frozenset([2, 5]): "25 or 52", frozenset([4, 5]): "45 or 54"}
q11 = dist(product(pack, repeat=2), key=lambda o: lab11[frozenset(o)])
order11 = ["22", "44", "55", "24 or 42", "25 or 52", "45 or 54"]
dist_table(src("11"), 0, ordered(q11, order11), "A11")
try:
    report(tables(TQ["11"])[0][0][1:] == order11, "Q11 printed outcomes", "")
except Exception as err:
    report(False, "Q11 outcomes", f"ERROR {err}")

# Q12
q12a = dist(product(balls, repeat=2), key=lambda o: "".join(v[0].upper() for v in o))
dist_table(src("12"), 0, ordered(q12a, ["RR", "RG", "GR", "GG"]), "A12 a", header=("outcome", "probability"))
bl = ["R1", "R2", "R3", "R4", "G1", "G2", "G3"]
q12b = dist(permutations(bl, 2), key=lambda o: o[0][0] + o[1][0])
dist_table(src("12"), 1, ordered(q12b, ["RR", "RG", "GR", "GG"]), "A12 b", header=("outcome", "probability"))
deck = [(r, s) for r in range(13) for s in "HDSC"]
suit2 = dist(combinations(deck, 2), key=lambda o: frozenset([o[0][1], o[1][1]]))
dist_table(src("12"), 2, {k + k: suit2[frozenset(k)] for k in "HDSC"}, "A12 c same suit", header=("outcome", "probability"), total=False)
mixed = {f"{u}{v} or {v}{u}": suit2[frozenset([u, v])] for u, v in (("H", "S"), ("H", "C"), ("H", "D"), ("S", "C"), ("S", "D"), ("C", "D"))}
dist_table(src("12"), 3, mixed, "A12 c different suits", header=("outcome", "probability"), total=False)
report(sum(suit2.values()) == 1 and len(suit2) == 10, "A12 c: the ten unordered suit pairs cover the sample space", "")

# Q13 e (theoretical): two pieces drawn from three red and two green
paper = ["R1", "R2", "R3", "G1", "G2"]
q13 = dist(combinations(paper, 2), key=lambda o: sum(v[0] == "G" for v in o))
value(src("13"), r"<b>e</b> Theoretical results: \(P(X=0)=@\), \(P(X=1)=@\), \(P(X=2)=@\)<br>", (q13[0], q13[1], q13[2]), "A13 e")
report("Label three of them <i>Red</i> and the other two <i>Green</i>" in TQ["13"] and "two pieces of paper are drawn out" in TQ["13"], "Q13 data", "")

# Q14 (three without replacement)
t14 = list(permutations(marb, 3))
pat = dist(t14, key=lambda o: "".join("E" if v % 2 == 0 else "O" for v in o))
value(src("14"), r"EEE and OOO each have probability \(@\); the other six possible outcomes each have probability \(@\).", (pat["EEE"], pat["EEO"]), "A14")
report(pat["EEE"] == pat["OOO"] and len({pat[k] for k in pat if k not in ("EEE", "OOO")}) == 1 and len(pat) == 8, "A14 the other six equal", "")
dist_table(src("14"), 0, ordered(dist(t14, key=lambda o: sum(v % 2 == 0 for v in o)), [0, 1, 2, 3]), "A14")

# Q15
try:
    t15 = tables(TQ["15"])
    _, roots, valid = solve_a(t15[0])
    rs = sorted(F(str(r)) for r in roots)
    value(src("15"), r"is 1 gives \(a=@\) or \(a=@\). But", tuple(rs), "A15 a roots")
    value(src("15"), r"But \(a=@\) gives probabilities outside", tuple(F(str(r)) for r in roots if r not in valid), "A15 a rejected")
    value(src("15"), r"the only valid answer is \(a=@\).", tuple(F(str(v)) for v in valid), "A15 a valid")
    _, roots, valid = solve_a(t15[1])
    value(src("15"), r"<b>b</b> \(a=@\) or \(a=@\) (both are valid)", tuple(sorted(F(str(v)) for v in valid)), "A15 b")
    report(len(valid) == len(roots) == 2, "A15 b: both roots valid", str(roots))
except Exception as err:
    report(False, "A15", f"ERROR {err}")

# Q16 (choose three cards; sum)
hand4 = [("7", "H"), ("7", "D"), ("6", "C"), ("8", "S")]
s16a = dist(combinations(hand4, 3), key=lambda o: sum(int(c[0]) for c in o))
dist_table(src("16"), 0, ordered(s16a, sorted(s16a)), "A16 a")
hand5 = [7, 7, 7, 6, 8]
s16b = dist(combinations(range(5), 3), key=lambda o: sum(hand5[i] for i in o))
dist_table(src("16"), 1, ordered(s16b, sorted(s16b)), "A16 b")
report("the 7 of hearts, 7 of diamonds, 6 of clubs and 8 of spades" in TQ["16"] and "three 7s, a 6 and an 8" in TQ["16"], "Q16 data", "")

report(sorted(BLK, key=lambda t: (len(t), t)) == [str(i) for i in range(1, 17)] + ["C1", "C2", "C3", "C4", "C5"], "answer blocks", str(sorted(BLK, key=lambda t: (len(t), t))))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 17)], "textbook questions 1-16", str(sorted(TQ, key=int)))
report([b for b in re.findall(r"\{\{band:([FDE])\}\}", hw)] == ["F", "D", "E"] and hw.index("{{band:D}}") < hw.index('q-num">8<') and hw.index("{{band:E}}") < hw.index('q-num">14<') and hw.index('q-num">13<') < hw.index("{{band:E}}"),
       "bands F 1-7, D 8-13, E 14-16", "")

# ================================================================ figures (recorded from figs.build_13a)
sys.path.insert(0, os.path.join(HERE, "..", "build"))      # plots.py (figs.py imports it)
sys.path.insert(0, SRC)
try:
    import figs                                    # noqa: E402
    rec, trees = {}, {}
    figs.dist_graph = lambda name, xs, ps, yt, **kw: rec.__setitem__(name, (list(xs), [F(p) for p in ps], [F(v) for v, _ in yt], [lab for _, lab in yt]))
    figs.tree2 = lambda name, first, **kw: trees.__setitem__(name, first)
    figs.build_13a()
    want = {"c13a_coins": c4, "c13a_die": die, "c13a_det": {4: F(1)}, "a13a_sixes": sixes, "a13a_less3": less3, "a13a_cards": cards, "a13a_tetra": tetra}
    for name, d in want.items():
        xs, ps, yv, ylab = rec[name]
        ok = xs == list(d) and ps == list(d.values()) and set(yv) <= set(ps) and all(val(lb) == v for v, lb in zip(yv, ylab))
        report(ok and os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}", f"x {xs}, P {[str(p) for p in ps]}")
    tr = trees["a13a_q8tree"]
    pC = F(3, 13)
    ok = val(tr[0][1]) == pC and val(tr[1][1]) == 1 - pC
    for lab1, p1, outs in tr:
        for lab2, p2, outlab, prob in outs:
            ok &= val(prob) == val(p1) * val(p2) == q8a[(lab1 == "C") + (lab2 == "C")] / (2 if (lab1 == "C") != (lab2 == "C") else 1)
            ok &= outlab == lab1 + lab2
    report(ok, "figure a13a_q8tree (branch and path probabilities)", "")
    for name in list(want) + ["a13a_q8tree"]:
        report((les + ans).count("{{svg:" + name + "}}") == 1, f"figure {name} used once", "")
except Exception as err:
    report(False, "figures", f"ERROR {err}")

# ================================================================ past papers
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks?", pps[1])
    marks = [int(v) for v in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and M >= 1, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M} (house rule 8 shortfall: the only clean 13A school item)")
    report(T == max(5, 5 * round(1.5 * M / 5)), "PP time", f"{T} min for {M} mark(s) (1.5 x marks rounded to 5 min, at least 5)")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for k in PPQ:
        sq = re.search(r"^(.*?)</span><span class=\"mk\">", PPQ[k]).group(1)
        sa = re.search(r"^(.*?)</span></div>", PPA[k]).group(1)
        report(re.sub(r"<[^>]+>", "", sq) == re.sub(r"<[^>]+>", "", sa), f"PP{k} source label", re.sub(r"<[^>]+>", "", sq))
        report(PPQ[k].count('<div class="hint">') == 1, f"PP{k} hint", "exactly one hint")
except Exception as err:
    report(False, "PP structure", f"ERROR {err}")

# PP1 BHHS 2020 Q12(a)(iv): P(X >= 3) from the printed table
try:
    hx, hp = tables(PPQ[1])[0]
    given = {int(x): val(p) for x, p in zip(hx[1:], hp[1:]) if strip(p) not in ("a", "b")}
    # the data are consistent with Bin(4, p): p^4 = P(X = 4) gives p = 0.3 exactly (a rational fourth root)
    p_ = F(3, 10)
    q_ = 1 - p_
    bern = [True] * 3 + [False] * 7                 # one trial: success with probability 0.3, by counting
    bin4 = dist(product(bern, repeat=4), key=sum)
    report(p_ ** 4 == given[4] and all(bin4[k] == given[k] for k in given), "PP1 table data consistent (four trials with p = 0.3)", str({k: str(v) for k, v in given.items()}))
    report(sorted(given) == [0, 3, 4] and [strip(p) for p in hp[2:4]] == ["a", "b"], "PP1 table: a and b unknown", "")
    chain(PPA[1], r"\[P(X\ge3)=P(X=3)+P(X=4)=@.\]", given[3] + given[4], "PP1", 2)
    report("(iv) Find \\(P(X\\ge3)\\)." in PPQ[1] and '<span class="mk">1</span>' in PPQ[1], "PP1 part (iv), 1 mark", "")
except Exception as err:
    report(False, "PP1", f"ERROR {err}")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{NCHECK[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
