r"""Check of Lesson 5C (Integration Part 1 pack): The definite integral and its properties.

The script reads the values PRINTED in workspace/build/int1/l5c.html (worked examples, tutor demo and
your-turn questions, every textbook question, the past-paper questions) and in a_5c.html (lesson-example
answers, textbook answers, past-paper solutions), and compares them with independent computation.

  - Every chain of working (each \begin{aligned} block, and each inline chain that contains an integral)
    is read member by member. Each member is turned into sympy: definite integrals \int_a^b ... dx are
    evaluated with sympy.integrate, evaluation brackets [F(x)]_a^b with F(b) - F(a), mixed numbers such as
    4\tfrac12 are read as 4 + 1/2. Every member must equal the left-hand side, which is evaluated with
    sympy.integrate (never with the page's own arithmetic).
  - Every inline chain of plain numbers (areas such as \tfrac12\times4\times4=8) is checked the same way.
  - The questions' integrals are read from the stems and integrated with sympy; the printed answers must
    equal them, and must equal the textbook key (Ext 1 Y12 PDF 889-890), transcribed below.
  - Exercise 5C Q12 (lines and quadrants) uses sympy Piecewise; Q18 and Q19 use numeric and symbolic
    integrals; Q16 checks the signs of the integrals.
  - Past papers: labels in both files, marks add to 3, time 1.5 x marks rounded up to 5 minutes, one hint
    each, PP1 key (B) agrees with the recreated graph, PP2 only option C equals the integral, PP3 integral is 0.
A template must match exactly once, otherwise the item FAILS. Exit status 1 if anything fails.
Run: python3 workspace/checks/int1_5c.py
"""
import math
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex, split_top  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))
FAILS, NCHECK = [], [0]
x = sp.Symbol("x", real=True)
N = sp.Symbol("N", positive=True)
h = sp.Symbol("h", positive=True)          # stands for epsilon
EXTRA = {"N": N, "h": h}


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100]
          + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def present(block, text, where):
    c = block.count(text)
    report(c == 1, f"{where} printed once: {text[:70]}", f"found {c} times")


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def eq(a, b):
    try:
        d = sp.simplify(sp.sympify(a) - sp.sympify(b))
        if d == 0:
            return True
        return d.is_number and abs(complex(sp.N(d))) < 1e-12
    except Exception:
        return False


# ---------------------------------------------------------------- TeX -> value
def _token(s, j):
    """A TeX limit at s[j]: {...}, \\cmd or one character. Returns (text, next index)."""
    if s[j] == "{":
        d, k = 0, j
        while True:
            d += s[k] == "{"
            d -= s[k] == "}"
            if d == 0:
                return s[j + 1:k], k + 1
            k += 1
    if s[j] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[j:])
        return m.group(0), j + len(m.group(0))
    return s[j], j + 1


def clean(s):
    s = s.replace("\\displaystyle", "").replace("\\varepsilon", "{h}")
    s = re.sub(r"\\sqrt\s+(\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"\\textbf\{[^}]*\}", "", s)
    s = re.sub(r"\\qquad\\text.*$", "", s, flags=re.S)
    s = re.sub(r",?(?:\\ )?\\text\{[^}]*\}(\\textbf\{[^}]*\})?", "", s)
    s = re.sub(r"\\q?quad", "", s)
    s = re.sub(r"\\(?:Bigg|bigg|Big|big|left|right)(?=[\[\]()|.])", "", s)
    s = s.strip().rstrip(".,").strip()
    s = re.sub(r"(?<![\d.}^_])(\d+)\\tfrac(\d)(\d)", r"{(\1+\2/\3)}", s)          # 4\tfrac12 -> 4 + 1/2
    return s


def val(s):
    """Evaluate a printed TeX member: definite integrals and [F]_a^b brackets are worked out by sympy."""
    s = clean(s)
    while "\\int_" in s:
        i = s.index("\\int_")
        lo, j = _token(s, i + 5)
        if s[j] != "^":
            raise ValueError(f"no upper limit in {s!r}")
        hi, j = _token(s, j + 1)
        k, d = j, 0
        while not (d == 0 and s.startswith("dx", k)):
            d += s[k] in "{(["
            d -= s[k] in "})]"
            k += 1
            if k >= len(s):
                raise ValueError(f"no dx in {s!r}")
        body = s[j:k].replace("\\,", "").strip() or "1"
        v = sp.integrate(_tex(body, EXTRA), (x, _tex(lo, EXTRA), _tex(hi, EXTRA)))
        s = s[:i] + "{(" + sp.latex(sp.simplify(v)) + ")}" + s[k + 2:]
    while True:
        m = None
        for i, c in enumerate(s):
            if c != "[":
                continue
            d, k = 0, i
            while k < len(s):
                d += s[k] == "["
                d -= s[k] == "]"
                if d == 0:
                    break
                k += 1
            if k + 1 < len(s) and s[k + 1] == "_":
                m = (i, k)
                break
        if not m:
            break
        i, k = m
        lo, j = _token(s, k + 2)
        hi, j = _token(s, j + 1)
        F = _tex(s[i + 1:k], EXTRA)
        v = F.subs(x, _tex(lo, EXTRA)) - F.subs(x, _tex(hi, EXTRA))
        s = s[:i] + "{(" + sp.latex(sp.simplify(-v)) + ")}" + s[j:]
    return _tex(s, EXTRA)


def check_chain(members, where, lhs_value=None):
    """members[0] is the left-hand side; every member must equal it (or lhs_value)."""
    try:
        ref = val(members[0]) if lhs_value is None else lhs_value
    except Exception as err:
        report(False, f"{where} LHS {members[0][:50]}", f"ERROR {err}")
        return None
    good, bad = 0, []
    for m in members[1:]:
        if not m.strip():
            continue
        try:
            v = val(m)
        except Exception as err:
            bad.append(f"{m[:40]} ERROR {err}")
            continue
        if eq(v, ref):
            good += 1
        else:
            bad.append(f"{m[:50]} = {v}")
    report(not bad and good >= 1, f"{where}: {members[0][:60]}", f"= {ref}; {good} members agree" + ("; BAD " + " | ".join(bad) if bad else ""))
    return ref


def aligned_blocks(text):
    return re.findall(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", text, re.S)


def block_members(blk):
    rows = [r for r in blk.split("\\\\")]
    first = rows[0]
    lhs, rhs = first.split("&", 1)
    out = [lhs]
    for r in rows:
        r = r.split("&", 1)[1] if "&" in r else r
        out += [p for p in split_top(r.lstrip("="), "=")]
    return out


def chains_in(text, where, skip=()):
    """Check every aligned block; returns the list of LHS values in order."""
    vals = []
    for n_, blk in enumerate(aligned_blocks(text)):
        if any(sk in blk for sk in skip):
            continue
        vals.append(check_chain(block_members(blk), f"{where} chain {n_ + 1}"))
    return vals


def inline_math(text):
    return re.findall(r"\\\((.*?)\\\)", text, re.S)


def inline_integral_chains(text, where):
    n_ = 0
    for m in inline_math(text):
        if "\\int" in m and "=" in m and not re.search(r"\\le|<|>|\\ge|(?<![A-Za-z])[fgFG]\(", m):
            n_ += 1
            check_chain(split_top(m, "="), f"{where} inline")
    return n_


def numeric_chains(text, where):
    n_ = 0
    for m in inline_math(text):
        if "=" not in m or re.search(r"\\le|\\ge|<|>", m):
            continue
        if re.search(r"[A-Za-z]", re.sub(r"\\[A-Za-z]+", "", m)):
            continue
        n_ += 1
        check_chain(split_top(m, "="), f"{where} arithmetic")
    return n_


def I(f, a, b):
    return sp.integrate(f, (x, a, b))


# ---------------------------------------------------------------- read the files
les = read("l5c.html")
ans = read("a_5c.html")
for need in ("<!-- ============ Homework ============ -->", "<!-- ============ Past papers ============ -->"):
    if les.count(need) != 1:
        sys.exit(f"FAIL: {need} not found once in l5c.html")
teach, rest = les.split("<!-- ============ Homework ============ -->")
hw, ppl = rest.split("<!-- ============ Past papers ============ -->")
CON = {}
for c in range(1, 6):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[c] = {"teach": seg, "demo": [b for k_, _, b in exs if k_ == "demo"], "attempt": [b for k_, _, b in exs if k_ == "attempt"],
              "worked": [b for k_, _, b in exs if k_ == "worked"]}
    expect = ["demo", "attempt", "worked"] + (["worked"] if c == 4 else [])
    report([k_ for k_, _, _ in exs] == expect, f"Concept {c} blocks", str([k_ for k_, _, _ in exs]))
WE = [w for c in range(1, 6) for w in CON[c]["worked"]]
report(len(WE) == 6 and all(f"Worked example {i + 1}" in les for i in range(6)), "six worked examples (textbook Examples 7-12)")
TQ = dict(re.findall(r'<span class="q-num">(\d+)</span><div class="q-body">(.*?)(?=<span class="q-num">|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 20)], "textbook questions 1-19", str(sorted(TQ, key=int)))
fpart, rest2 = hw.split("{{band:D}}")
dpart, epart = rest2.split("{{band:E}}")
report(fpart.count('class="q-num"') == 8 and dpart.count('class="q-num"') == 9 and epart.count('class="q-num"') == 2
       and hw.count("{{band:F}}") == 1, "bands F: Q1-8, D: Q9-17, E: Q18-19 (as the textbook)")
secs = ans.split('<div class="ans-sec">')
report(len(secs) == 4 and secs[1].startswith("Lesson Examples") and secs[2].startswith("Textbook Homework")
       and secs[3].startswith("Past-Paper Homework"), "answer sections in order")
BLK = dict(re.findall(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S))
report(sorted(k for k in BLK if k.startswith("C")) == ["C1", "C2", "C3", "C4", "C5"], "answers C1-C5")
report(sorted((k for k in BLK if not k.startswith("C")), key=int) == [str(i) for i in range(1, 20)], "answers Q1-19 (17a show-that: none)")

# ---------------------------------------------------------------- the boxes
for box in (r"5 The definite integral as the sum of signed areas", r"6 Integrating odd and even functions",
            r"7 Dissection of the interval", r"8 Intervals of zero width", r"9 Reversing the interval",
            r"10 Integral of a sum", r"11 Integral of a multiple", r"12 Inequality"):
    present(teach, f'<div class="bt">{box}</div>', "box title")
for t in (r"\int_a^b f(x)\,dx=+\,\text{area }A-\text{area }B+\text{area }C.",
          r"If \(f(x)\) is odd, then \(\displaystyle\int_{-a}^{a}f(x)\,dx=0\)",
          r"If \(f(x)\) is even, then \(\displaystyle\int_{-a}^{a}f(x)\,dx=2\int_0^a f(x)\,dx\)",
          r"\[\int_a^b f(x)\,dx=\int_a^c f(x)\,dx+\int_c^b f(x)\,dx\]", r"\[\int_a^a f(x)\,dx=0\]",
          r"\[\int_b^a f(x)\,dx=-\int_a^b f(x)\,dx.\]", r"\[F(a)-F(b)=-\big(F(b)-F(a)\big).\]",
          r"\[\int_a^b\big(f(x)+g(x)\big)\,dx=\int_a^b f(x)\,dx+\int_a^b g(x)\,dx\]",
          r"\[\int_a^b kf(x)\,dx=k\int_a^b f(x)\,dx\]", r"\int_a^b f(x)\,dx\le\int_a^b g(x)\,dx."):
    present(teach, t, "box text")
# the boxes hold for sample functions (sympy)
fs, gs = x ** 3 - 2 * x + 1, x ** 2 + 3
report(eq(I(fs, -1, 3), I(fs, -1, 1) + I(fs, 1, 3)) and I(fs, 2, 2) == 0 and eq(I(fs, 3, -1), -I(fs, -1, 3))
       and eq(I(fs + gs, 0, 2), I(fs, 0, 2) + I(gs, 0, 2)) and eq(I(5 * fs, 0, 2), 5 * I(fs, 0, 2)), "Boxes 7-11 hold (sympy sample)")
report(I(x ** 3 - 4 * x, -2, 2) == 0 and eq(I(x ** 2 + 1, -2, 2), 2 * I(x ** 2 + 1, 0, 2)), "Box 6 examples (sympy)")

# ---------------------------------------------------------------- every chain of working
ans_skip = ("g(-x)", "g(1-t)", "g(x)\\,dx")
nchains = len([v for v in chains_in(ans, "answers", skip=ans_skip)])
report(nchains == 24, "answers: 24 integral chains checked", str(nchains))
for i, w in enumerate(WE):
    chains_in(w, f"WE{i + 1}")
report(inline_integral_chains(ans, "answers") >= 8, "answers: inline integral chains found")
report(numeric_chains(ans, "answers") >= 8, "answers: inline arithmetic chains found")
report(numeric_chains(teach, "lesson") >= 4, "lesson: inline arithmetic chains found")

# ---------------------------------------------------------------- worked examples = textbook values
def last_member(blk):
    return val(block_members(blk)[-1])


TBW = [(0, [(x - 4, 0, 4, -8), (x - 4, 4, 6, 2), (x - 4, 0, 6, -6)]),
       (1, [(x ** 3 - 4 * x, -2, 2, 0), (x ** 2 + 1, -2, 2, sp.Rational(28, 3))]),
       (2, [(x - 1, 2, 4, 4), (x - 1, 4, 2, -4)]),
       (3, [(x ** 2 + x + 1, 0, 1, sp.Rational(11, 6)), (x ** 2 + x + 1, 0, 1, sp.Rational(11, 6))]),
       (4, [(10 * x ** 3, 1, 3, 200), (10 * x ** 3, 1, 3, 200)])]
for wi, items in TBW:
    blks = aligned_blocks(WE[wi])
    ok = len(blks) == len(items)
    for blk, (f_, a_, b_, tb) in zip(blks, items):
        ok &= eq(last_member(blk), tb) and eq(I(f_, a_, b_), tb) and eq(val(block_members(blk)[0]), tb)
    report(ok, f"WE{wi + 1}: final values = sympy = textbook Example {wi + 7}", str([t[3] for t in items]))
present(WE[0], r"area \(\tfrac12\times4\times4=8\)", "WE1 triangle OAB")
present(WE[0], r"area \(\tfrac12\times2\times2=2\)", "WE1 triangle BMC")
present(WE[0], r"\(2-8=-6\)", "WE1 c")
present(WE[1], r"\(\displaystyle\int_{-2}^{2}(x^3-4x)\,dx=0\), because the integrand is odd.", "WE2 a")
present(WE[1], r"(Check: \((-x)^3-4(-x)=-x^3+4x=-(x^3-4x)\).)", "WE2 check")
report(sp.expand((-x) ** 3 - 4 * (-x) + (x ** 3 - 4 * x)) == 0, "x^3 - 4x is odd")
present(WE[5], r"\(0\le4-x^2\le4\)", "WE6 b")
present(WE[5], r"\[0\le\int_{-2}^{2}(4-x^2)\,dx\le16.\]", "WE6 b conclusion")
report(0 <= I(4 - x ** 2, -2, 2) <= 16 and I(4, -2, 2) == 16, "WE6: 0 <= 32/3 <= 16, rectangle 16")

# ---------------------------------------------------------------- tutor demos and your turns: questions vs answers
def ans_split(key):
    d, y = BLK[key].split("<b>Your turn.</b>")
    return d, y


QA = {  # concept: (demo integrals, your-turn integrals) printed in the questions, each must appear in the answer
    1: ([r"\int_0^3(x-3)\,dx", r"\int_3^5(x-3)\,dx", r"\int_0^5(x-3)\,dx"], [r"\int_0^2(x-2)\,dx", r"\int_2^5(x-2)\,dx", r"\int_0^5(x-2)\,dx"]),
    2: ([r"\int_{-3}^{3}(x^3-9x)\,dx", r"\int_{-3}^{3}(x^2+1)\,dx"], [r"\int_{-1}^{1}(x^3-x)\,dx", r"\int_{-1}^{1}(3x^2+1)\,dx"]),
    3: ([r"\int_0^3x^2\,dx", r"\int_0^1x^2\,dx+\int_1^3x^2\,dx", r"\int_2^2(x^3+5)\,dx", r"\int_1^3(x+1)\,dx", r"\int_3^1(x+1)\,dx"],
        [r"\int_0^4x\,dx", r"\int_0^1x\,dx+\int_1^4x\,dx", r"\int_{-3}^{-3}(x^2-4x)\,dx", r"\int_2^5(x-2)\,dx", r"\int_5^2(x-2)\,dx"]),
    4: ([r"\int_0^2(x^2+x+1)\,dx", r"\int_0^2x^2\,dx+\int_0^2x\,dx+\int_0^2 1\,dx", r"\int_1^2 6x^3\,dx", r"6\int_1^2x^3\,dx"],
        [r"\int_0^3(x^2+1)\,dx", r"\int_0^3x^2\,dx+\int_0^3 1\,dx", r"\int_1^2 4x^3\,dx", r"4\int_1^2x^3\,dx"]),
    5: ([r"\int_{-3}^{3}(9-x^2)\,dx\le54"], [r"\int_{-1}^{1}(1-x^2)\,dx\le2"]),
}
for c, (dq, yq) in QA.items():
    d_, y_ = ans_split(f"C{c}")
    for blk, a_blk, items, nm in ((CON[c]["demo"][0], d_, dq, "demo"), (CON[c]["attempt"][0], y_, yq, "your turn")):
        for it in items:
            report(blk.count(it) == 1 and a_blk.count(it) >= 1, f"C{c} {nm}: {it[:50]} in question and answer",
                   f"question {blk.count(it)}, answer {a_blk.count(it)}")
# final values of the lesson-example answers (independent sympy)
FINAL = {
    "C1": [I(x - 3, 0, 3), I(x - 3, 3, 5), I(x - 3, 0, 5), I(x - 2, 0, 2), I(x - 2, 2, 5), I(x - 2, 0, 5)],
    "C2": [I(x ** 3 - 9 * x, -3, 3), I(x ** 2 + 1, -3, 3), I(x ** 3 - x, -1, 1), I(3 * x ** 2 + 1, -1, 1)],
    "C3": [I(x + 1, 1, 3), I(x + 1, 3, 1), I(x - 2, 2, 5), I(x - 2, 5, 2)],
    "C4": [I(x ** 2 + x + 1, 0, 2)] * 2 + [I(6 * x ** 3, 1, 2)] * 2 + [I(x ** 2 + 1, 0, 3)] * 2 + [I(4 * x ** 3, 1, 2)] * 2,
    "C5": [I(9 - x ** 2, -3, 3), I(1 - x ** 2, -1, 1)],
}
for key, exp in FINAL.items():
    got = [last_member(b) for b in aligned_blocks(BLK[key])]
    report(len(got) == len(exp) and all(eq(g, e) for g, e in zip(got, exp)), f"{key}: final values = sympy", f"{got} vs {exp}")
# C1 triangle explanations, C2 symmetry and C3, C5 statements
a1d, a1y = ans_split("C1")
present(a1d, r"area \(\tfrac12\times3\times3=4\tfrac12\)", "C1 demo lower triangle")
present(a1d, r"area \(\tfrac12\times2\times2=2\)", "C1 demo upper triangle")
present(a1d, r"\(2-4\tfrac12=-2\tfrac12\)", "C1 demo c")
present(a1y, r"area \(\tfrac12\times2\times2=2\)", "C1 your turn lower")
present(a1y, r"area \(\tfrac12\times3\times3=4\tfrac12\)", "C1 your turn upper")
present(a1y, r"\(4\tfrac12-2=2\tfrac12\)", "C1 your turn c")
for f_ in (x ** 3 - 9 * x, x ** 3 - x):
    report(sp.expand(f_.subs(x, -x) + f_) == 0, f"{f_} is odd")
for f_ in (x ** 2 + 1, 3 * x ** 2 + 1, 9 - x ** 2, 1 - x ** 2):
    report(sp.expand(f_.subs(x, -x) - f_) == 0, f"{f_} is even")
present(BLK["C3"], r"\(\displaystyle\int_2^2(x^3+5)\,dx=0\)", "C3 demo b")
present(BLK["C3"], r"\(\displaystyle\int_{-3}^{-3}(x^2-4x)\,dx=0\)", "C3 your turn b")
c5d, c5y = ans_split("C5")
present(c5d, r"area \(6\times9=54\)", "C5 demo rectangle")
present(c5d, r"and \(0\le36\le54\)", "C5 demo check")
present(c5y, r"area \(2\times1=2\)", "C5 your-turn rectangle")
present(c5y, r"and \(0\le\tfrac43\le2\)", "C5 your-turn check")
report(I(9, -3, 3) == 54 and I(1, -1, 1) == 2 and 0 <= I(9 - x ** 2, -3, 3) <= 54 and 0 <= I(1 - x ** 2, -1, 1) <= 2, "C5 bounds (sympy)")

# ---------------------------------------------------------------- textbook homework
def q_int(qn, template):
    (s,) = grab(TQ[qn], template, f"Q{qn}")
    return val(s)


def printed_val(qn, template):
    (s,) = grab(BLK[qn], template, f"answer {qn}")
    return val(s)


def cmp(label, printed, sym, key):
    report(eq(printed, sym) and eq(sym, key), label, f"printed {printed}; sympy {sym}; key {key}")


# Q1
v1, v2 = I(2 * x - 3, 4, 5), I(2 * x - 3, 5, 4)
present(TQ["1"], r"\(\displaystyle\int_4^5(2x-3)\,dx\) and \(\displaystyle\int_5^4(2x-3)\,dx\)", "Q1 stem")
present(BLK["1"], r"The values are 6 and \(-6\), which differ by a factor of \(-1\).", "Q1 key")
report(v1 == 6 and v2 == -6, "Q1 sympy 6 and -6")
# Q2: the stems are true equalities, and the printed LHS = RHS values
for p, tmpl, key in (("a", r"<span class=\"pl\">a</span>\(@\)</span>", 2), ("b", r"<span class=\"pl\">b</span>\(@\)</span>", sp.Rational(27, 4)),
                     ("c", r"<span class=\"pl\">c</span>\(@\)</span>", 0)):
    (s,) = grab(TQ["2"], tmpl.replace('\\"', '"'), "Q2")
    sides = split_top(s, "=")
    ok = len(sides) == 2 and eq(val(sides[0]), val(sides[1])) and eq(val(sides[0]), key)
    report(ok, f"Q2{p} both sides = {key}", s[:70])
for p, key in (("a", "2"), ("b", r"6\tfrac34"), ("c", "0")):
    present(BLK["2"], f"<b>{p}</b> \\(LHS=RHS={key}\\)", f"Q2{p} answer")
# Q3, Q10: zero width and odd integrands
report(eq(q_int("3", r"<span class=\"pl\">a</span>\(\displaystyle@=0\)".replace('\\"', '"')), 0)
       and eq(q_int("3", r"<span class=\"pl\">b</span>\(\displaystyle@=0\)".replace('\\"', '"')), 0), "Q3 both integrals are 0 (sympy)")
q10 = re.findall(r'<span class="pl">([a-f])</span>\\\(\\displaystyle(.*?)\\\)', TQ["10"])
report(len(q10) == 6, "Q10 six integrals")
for p, s in q10:
    report(eq(val(s), 0), f"Q10{p} = 0 (sympy)", s[:50])
for p, why in (("a", "The interval has zero width."), ("b", "The interval has zero width."), ("c", "The integrand is odd."),
               ("d", "The integrand is odd."), ("e", "The integrand is odd."), ("f", "The integrand is odd.")):
    present(BLK["10"], f"<b>{p}</b> 0. {why}", f"Q10{p} answer")
for f_ in (x ** 3, x ** 3 - 25 * x, sp.sin(x), x / (1 + x ** 2)):
    report(sp.simplify(f_.subs(x, -x) + f_) == 0, f"Q10 {f_} is odd")
# Q4, Q5 signs (stems), Q6, Q7, Q8
for p, a_, b_, sign in (("a", 0, 1, -1), ("b", 1, 2, 1), ("c", 0, 2, 0), ("d", -2, 2, -1)):
    report(sp.sign(I(x - 1, a_, b_)) == sign, f"Q4{p} sign of the integral from {a_} to {b_}")
    word = {-1: "negative", 1: "positive", 0: "zero"}[sign]
    lims = f"{a_}^{b_}" if a_ >= 0 else f"{{{a_}}}^{{{b_}}}"
    present(TQ["4"], f'<span class="pl">{p}</span>\\(\\displaystyle\\int_{lims}(x-1)\\,dx\\) is {word}', f"Q4{p} stem")
for t in (r"\int_{-1}^{1}(1-x^2)\,dx\) is positive", r"\int_1^3(1-x^2)\,dx\) is negative", r"\int_{-1}^{0}(1-x^2)\,dx=\int_0^1(1-x^2)\,dx\)",
          r"\int_0^{\frac12}(1-x^2)\,dx>\int_{\frac12}^{1}(1-x^2)\,dx\)"):
    present(TQ["5"], t, "Q5 stem")
report(I(1 - x ** 2, -1, 1) > 0 and I(1 - x ** 2, 1, 3) < 0 and I(1 - x ** 2, -1, 0) == I(1 - x ** 2, 0, 1)
       and I(1 - x ** 2, 0, sp.Rational(1, 2)) > I(1 - x ** 2, sp.Rational(1, 2), 1), "Q5 a-d (sympy)")
present(TQ["6"], r"If \(\displaystyle\int_1^3f(x)\,dx=7\)", "Q6a stem")
present(TQ["6"], r"If \(\displaystyle\int_2^1g(x)\,dx=-5\)", "Q6b stem")
present(BLK["6"], r"<b>a</b> \(-7\) &nbsp; <b>b</b> 5", "Q6 answers (Box 9)")
report(I(2 * x, 0, 1) > I(x, 0, 1), "Q7 1 > 1/2")
present(BLK["8"], r"\(\displaystyle\int_{-2}^{1}x^3\,dx\)", "Q8 single integral")
report(I(x ** 3, -2, 0) + I(x ** 3, 0, 1) == I(x ** 3, -2, 1) == sp.Rational(-15, 4), "Q8 = -15/4 < 0 (sympy)")
# Q9: values from the stems, printed answers, textbook key
q9 = re.findall(r'(?:<span class="pl">([a-e])</span>)?(i{1,3})&ensp;\\\((.*?)\\\)', TQ["9"])
Q9KEY = {"a": [6, -6], "b": [5, 5], "c": [45, 30, 15], "d": [48, 3, 45], "e": [0, 0]}
cur, got9 = None, {}
for p, r_, s in q9:
    cur = p or cur
    got9.setdefault(cur, []).append(val(s))
report(sorted(got9) == list("abcde"), "Q9 parts a-e read")
for p, key in Q9KEY.items():
    line = re.search(rf"<b>{p}</b> (i .*?)(?:<br>|$)", BLK["9"], re.S).group(1)
    nums = re.findall(r"(?:^|&nbsp; )i{1,3} (\\\(-6\\\)|-?\d+)", line)
    nums = [int(n_.replace("\\(", "").replace("\\)", "")) for n_ in nums]
    report(nums == key and all(eq(a_, b_) for a_, b_ in zip(got9.get(p, []), key)) and len(got9.get(p, [])) == len(key),
           f"Q9{p}: printed {nums} = sympy {got9.get(p)} = key {key}")
# Q11
present(BLK["11"], r"<b>c</b> \(\tfrac14\) and \(\tfrac13\)", "Q11c")
report(I(x ** 3, 0, 1) == sp.Rational(1, 4) and I(x ** 2, 0, 1) == sp.Rational(1, 3), "Q11c sympy 1/4, 1/3")
report(sp.solve(x ** 2 - x ** 3, x) == [0, 1], "Q11a meet at x = 0, 1")
# Q12: lines and quadrants (Piecewise), printed sums and key
f12a = sp.Piecewise((sp.sqrt(1 - x ** 2), x <= 1), (-(x - 1), x <= 2), (2 * x - 5, x <= 3), (sp.sqrt(1 - (x - 3) ** 2), True))
f12b = sp.Piecewise((1 - sp.sqrt(1 - x ** 2), x <= 1), (2 - x, x <= 3), (-sp.sqrt(1 - (x - 3) ** 2), True))
for p, f_, key in (("a", f12a, sp.pi / 2 - sp.Rational(1, 2)), ("b", f12b, 1 - sp.pi / 2)):
    sym = sp.nsimplify(sp.integrate(f_, (x, 0, 4)))
    (s,) = grab(BLK["12"], f"<b>{p}</b> \\(@\\)", "Q12")
    members = split_top(s, "=")
    report(len(members) == 2 and eq(val(members[0]), key) and eq(val(members[1]), key) and eq(sym, key),
           f"Q12{p} = {key}", f"printed {s}; sympy {sym}")
report(f12a.subs(x, 0) == 1 and f12a.subs(x, 1) == 0 and f12a.subs(x, 2) == -1 and f12a.subs(x, 3) == 1 and f12a.subs(x, 4) == 0
       and f12b.subs(x, 0) == 0 and f12b.subs(x, 1) == 1 and f12b.subs(x, 3) == -1 and f12b.subs(x, 4) == 0, "Q12 graph points (textbook figure)")
# Q13, Q14 (stems integrated, printed values, key)
for qn, part, key in (("13", "a", [5, sp.Rational(25, 2)]), ("13", "b", [25, sp.Rational(35, 2), sp.Rational(55, 2)]),
                      ("14", "a", [sp.Rational(1, 2), 18, 8]), ("14", "b", [-sp.Rational(1, 2), -18, -8])):
    seg = TQ[qn].split(f'<span class="pl">{part}</span>')[1].split('<span class="pl">')[0]
    stems = [val(s) for s in re.findall(r"i{1,3}&ensp;\\\((.*?)\\\)", seg)]
    line = re.search(rf"<b>{part}</b> (.*?)(?:<br>|</div>)", BLK[qn], re.S).group(1)
    printed = [val(s) if "\\" in s or not s.strip().lstrip("-").isdigit() else int(s)
               for s in re.findall(r"i{1,3} (?:\\\()?((?:(?!&nbsp;|\\\)).)+)(?:\\\))?", line)]
    report(len(stems) == len(key) and all(eq(a_, b_) for a_, b_ in zip(stems, key)) and len(printed) == len(key)
           and all(eq(a_, b_) for a_, b_ in zip(printed, key)), f"Q{qn}{part}: printed = sympy = key {key}", f"{printed} {stems}")
# Q15: only part b (part a omitted, doubtful), even integrand
b_, d_, f_, k_ = sp.symbols("b d f k", positive=True)
ev15 = b_ * x ** 4 + d_ * x ** 2 + f_
report(sp.simplify(I(ev15, -k_, k_) - 2 * I(ev15, 0, k_)) == 0, "Q15b identity (sympy)")
report('<span class="pl">a</span>' not in TQ["15"] and TQ["15"].count('<span class="pl">b</span>') == 1, "Q15: only part b printed")
present(BLK["15"], "<b>b</b> The function is even, so its graph is symmetrical about the \\(y\\)-axis.", "Q15b key")
# Q16: a, c, d (b omitted, doubtful); all false
report(re.findall(r'<span class="pl">([a-d])</span>', TQ["16"]) == ["a", "c", "d"], "Q16 parts a, c, d")
report(I(2 ** x, -1, 1) > 0 and I(1 / x, -2, -1) < 0 and I(1 / x, 2, 1) < 0, "Q16 a, c, d are false (sympy)")
present(BLK["16"], r"<b>a</b> false &nbsp; <b>c</b> false &nbsp; <b>d</b> false", "Q16 answers")
# Q17: the stems of a and the values of b
for s in re.findall(r"Show that \\\((.*?)\\\)", TQ["17"]):
    mem = split_top(s.rstrip("."), "=")
    report(len(mem) == 4 and all(eq(val(m), 1) for m in mem), "Q17a stem chain = 1", s[:70])
seg = TQ["17"].split('<span class="pl">b</span>')[1]
stems17 = [val(s) for _, s in re.findall(r"<span>(i|ii|iii|iv|v|vi)&ensp;\\\((.*?)\\\)</span>", seg)]
key17 = [3, 4, -sp.Rational(7, 3), sp.Rational(10, 3), sp.Rational(182, 3), 33]
line = BLK["17"]
pr17 = [val(s) for s in re.findall(r"(?:^|&nbsp; |<b>b</b> )(?:i|ii|iii|iv|v|vi) (?:\\\()?((?:(?!&nbsp;|\\\)|</div>).)+)", line)]
report(len(stems17) == 6 and all(eq(a_, b_) for a_, b_ in zip(stems17, key17)), "Q17b sympy = key", str(stems17))
report(len(pr17) == 6 and all(eq(a_, b_) for a_, b_ in zip(pr17, key17)), "Q17b printed = key", str(pr17))
# Q18 (degrees for a and b)
deg = sp.pi / 180
report(abs(sp.N(sp.integrate(sp.sin(deg * x) ** 3, (x, -90, 90)))) < 1e-12, "Q18a = 0")
report(abs(sp.N(sp.integrate(sp.sin(4 * deg * x) * sp.cos(2 * deg * x), (x, -30, 30)))) < 1e-12, "Q18b = 0")
report(sp.N(sp.Integral(2 ** (-x ** 2), (x, -1, 1))) > 0, "Q18c > 0, so false")
report(I(2 ** x, 0, 1) < I(3 ** x, 0, 1), "Q18d true")
report(sp.N(I(2 ** x, -1, 0)) > sp.N(I(3 ** x, -1, 0)), "Q18e false")
tt = sp.Symbol("t")
report(all(sp.N(sp.Integral(1 / (1 + tt ** n_), (tt, 0, 1))) <= sp.N(sp.Integral(1 / (1 + tt ** (n_ + 1)), (tt, 0, 1))) for n_ in range(1, 7)), "Q18f true for n = 1..6")
for p, word in (("a", "True"), ("b", "True"), ("c", "False"), ("d", "True"), ("e", "False"), ("f", "True")):
    present(BLK["18"], f"<b>{p}</b> {word}, as", f"Q18{p}")
# Q19
for p, f_, lo, hi, lim_var, lim_to, lim in (("a", 1 / x ** 2, 1, N, N, sp.oo, 1), ("b", 1 / x ** 2, h, 1, h, 0, sp.oo),
                                             ("c", 1 / sp.sqrt(x), 1, N, N, sp.oo, sp.oo), ("d", 1 / sp.sqrt(x), h, 1, h, 0, 2)):
    sym = sp.simplify(sp.integrate(f_, (x, lo, hi)))
    (s,) = grab(BLK["19"], f"<b>{p}</b> The integral is \\(@\\), which", "Q19")
    pv = val(s)
    report(eq(pv, sym) and sp.limit(sym, lim_var, lim_to, "+") == lim, f"Q19{p}: {s} = {sym}, limit {lim}")
# textbook explanation answers that are copied from the key
for qn, t in (("3", "<b>a</b> The interval has width zero. &nbsp; <b>b</b> \\(y=x\\) is an odd function."),
              ("7", "The area under the line \\(y=2x\\) from \\(x=0\\) to \\(x=1\\) is greater than the area under \\(y=x\\)."),
              ("8", "The area below the \\(x\\)-axis is greater than the area above.")):
    present(BLK[qn], t, f"Q{qn} key")

# ---------------------------------------------------------------- past papers
PPQ = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span><span class="mk">(\d+) marks?</span></div>(.*?)(?=<div class="pp">|$)', ppl, re.S)
PPA = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span></div>(.*?)(?=<div class="ppa">|$)', ans, re.S)
report(len(PPQ) == 3 and len(PPA) == 3, "three past-paper questions, three solutions")
LABELS = ["Sydney Technical High School, 2021, Extension 1 Mathematics, Trial HSC, Q6",
          "Abbotsleigh, 2023, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q10",
          "Epping Boys High School, 2024, Trial Higher School Certificate Examination, Mathematics Extension 1, Q12(c)(ii)"]
for (num, lab, mk, body), (num2, lab2, sol), want in zip(PPQ, PPA, LABELS):
    clean_l = re.sub(r"\s+", " ", re.sub("<[^>]+>|&nbsp;", " ", lab)).replace(" ,", ",").strip()
    report(lab == lab2 and num == num2 and clean_l == want, f"PP{num} label (both files)", clean_l)
    report(body.count('class="hint"') == 1, f"PP{num} one hint")
    report(int(mk) == 1, f"PP{num} 1 mark")
tot = re.search(r"<span><b>(\d+) marks?</b></span>", ppl).group(1)
(tm,) = grab(ppl, "<b>Suggested time: @ minutes</b>", "pp intro")
report(int(tot) == sum(int(m) for _, _, m, _ in PPQ) == 3, "PP marks total 3")
report(int(tm) == max(5, 5 * math.ceil(1.5 * int(tot) / 5)), "PP time 1.5 x marks rounded up to 5 min", tm)
present(ppl, "For more timed practice, do Questions 9(d), 10(f), 12(b), 14, 17(b) and 18(b) above in 25 minutes.", "timed-practice note")
# PP1: key B; the recreated graph agrees (B greatest)
sys.path.insert(0, SRC)
from figs_5c import stf  # noqa: E402
import numpy as np  # noqa: E402


def num_int(a_, b_, n_=20000):
    xs = np.linspace(a_, b_, n_ + 1)
    ys = np.array([stf(v) for v in xs])
    return float(np.trapz(ys, xs)) if hasattr(np, "trapz") else float(np.trapezoid(ys, xs))


opts = {"A": num_int(0, 1), "B": num_int(0, 2), "C": num_int(0, 7), "D": num_int(0, 8)}
report(max(opts, key=opts.get) == "B" and abs(stf(2)) < 1e-9 and abs(stf(6)) < 1e-9 and abs(stf(8)) < 1e-9,
       "PP1: recreated graph (zeros 2, 6, 8) gives B greatest = school key B", str({k_: round(v, 3) for k_, v in opts.items()}))
present(PPQ[0][3], r"<span>(B)&ensp;\(\displaystyle\int_0^2f(x)\,dx\)</span>", "PP1 option B")
present(PPA[0][2], "<b>Answer (B).</b>", "PP1 answer")
# PP2: only C equals the integral; the solution chain
v_pp2 = sp.integrate(sp.acos(x), (x, -1, 1))
o2 = dict(re.findall(r"<span>\(([A-D])\)&ensp;\\\((.*?)\\\)</span>", PPQ[1][3]))
match = [k_ for k_, s in o2.items() if eq(val(s), v_pp2)]
report(sorted(o2) == list("ABCD") and match == ["C"] and eq(v_pp2, sp.pi), "PP2: only (C) = integral = pi (school key C)", str(o2))
present(PPA[1][2], "<b>Answer (C).</b>", "PP2 answer")
g2 = sp.acos(x) - sp.pi / 2
blks = aligned_blocks(PPA[1][2])
mem = block_members(blks[0])
ok = len(mem) >= 4
for m in mem:
    e_ = _tex(clean(m).replace("g(-x)", r"(\cos^{-1}(-x)-\tfrac{\pi}{2})").replace("-g(x)", r"-(\cos^{-1}(x)-\tfrac{\pi}{2})"), EXTRA)
    ok &= all(abs(complex(sp.N(e_.subs(x, t) - (-g2.subs(x, t))))) < 1e-12 for t in (-0.9, -0.3, 0.2, 0.7))
report(ok, "PP2: g(-x) chain equals -g(x) at sample points", str(len(mem)))
mem = block_members(blks[1])
ok = True
for m in mem:
    m2 = clean(m).replace("g(x)", r"(\cos^{-1}(x)-\tfrac{\pi}{2})")
    ok &= eq(val(m2), sp.pi)
report(ok and len(mem) == 4, "PP2: integral-of-a-sum chain = pi")
report(all(abs(sp.N((g2.subs(x, -x) + g2).subs(x, t))) < 1e-12 for t in (-0.95, -0.4, 0.1, 0.6, 1)), "PP2: g is odd (numeric)")
# PP3: integral 0; the symmetry chain
g3 = 2 * sp.acos(x - 1) - sp.pi
report(sp.simplify(sp.integrate(g3, (x, 0, 2))) == 0, "PP3: integral from 0 to 2 is 0 (sympy)")
present(PPQ[2][3], r"Hence, explain why \(\displaystyle\int_0^2\big[2\cos^{-1}(x-1)-\pi\big]\,dx=0\)", "PP3 stem")
mem = block_members(aligned_blocks(PPA[2][2])[0])
ok = len(mem) == 6
for m in mem:
    s_ = clean(m)
    s_ = s_.replace("-g(1+t)", r"-(2\cos^{-1}(t)-\pi)").replace("g(1-t)", r"(2\cos^{-1}(-t)-\pi)")
    e_ = _tex(s_, {"t": sp.Symbol("t")})
    ok &= all(abs(complex(sp.N(e_.subs(sp.Symbol("t"), t) - g3.subs(x, 1 - t)))) < 1e-12 for t in (0.1, 0.5, 0.9))
report(ok, "PP3: g(1-t) = -g(1+t) chain at sample points")
report(abs(sp.N(sp.integrate(g3, (x, 0, 1)) - sp.Abs(sp.integrate(g3, (x, 1, 2))))) < 1e-12 and sp.N(sp.integrate(g3, (x, 0, 1))) > 0, "PP3: areas P and Q equal")
present(PPA[2][2], r"=\text{area }P-\text{area }Q=0.\]", "PP3 conclusion")

# ---------------------------------------------------------------- figures referenced exist
for name in set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans)):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}.svg exists")
print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:40], sep="\n  ")
    sys.exit(1)
print("ALL OK")
