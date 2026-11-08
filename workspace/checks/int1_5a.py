r"""Check of Lesson 5A (Integration Part 1 pack): Areas and the definite integral.

The script reads the values PRINTED in workspace/build/int1/l5a.html (worked examples, the data of the
tutor demos and your-turn items, every textbook question and the past-paper question) and in a_5a.html
(lesson-example answers, textbook answers, past-paper solution). Each value is found with a template
('@' marks the printed TeX); a template must match exactly once in its block, otherwise the item FAILS.
Printed TeX is turned into sympy (workspace/checks/int3_tex.py, plus mixed numbers such as 4\tfrac12)
and compared with an independent computation:
  - definite integrals of lines, |x| and semicircles: sympy.integrate (with Abs and sqrt), never the area
    formula the page uses;
  - upper and lower rectangle sums: exact fractions.Fraction sums of the function at the strip ends
    (decimals for 2^x and ln x), with each printed member of each chain compared;
  - the limit proofs: every printed line of every chain (lines without '...') is compared, as a function
    of n, with sympy.summation of the rectangle heights, and the limits with sympy.limit;
  - Q17: the trapezium sum by sympy.summation; Q13/Q14: the exact integrals behind the counted squares.
The textbook's printed answers (Ext 1 Y12 PDF 888-889) are transcribed below and compared as well.
Past paper: marks add to the intro total, the time is 1.5 x marks rounded up to 5 minutes, labels match
in both files, one hint, and the MC letter is the only option equal to the value of the integral.

Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5a.py
"""
import math
import os
import re
import sys
from fractions import Fraction as F

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex, split_top  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))
FAILS, NCHECK = [], [0]
x = sp.Symbol("x", real=True)
n = sp.Symbol("n", positive=True, integer=True)
k = sp.Symbol("k", positive=True, integer=True)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100]
          + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def T(s):
    """Printed TeX -> sympy (mixed numbers, \\ldots and spacing handled here)."""
    s = s.strip().rstrip(".,")
    s = re.sub(r"\\(?:displaystyle|left|right|quad|qquad)", "", s)
    s = re.sub(r"(\d)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)        # 4\tfrac12 -> (4+1/2)
    s = re.sub(r"(\d)\\tfrac\{(\d+)\}\{(\d+)\}", r"(\1+\2/\3)", s)
    s = s.replace("\\,", "").replace("\\ ", "")
    s = re.sub(r"\\([dt]?frac)\s+(\w)(\w)", r"\\\1{\2}{\3}", s)      # \frac nn -> \frac{n}{n}
    s = re.sub(r"\\sqrt\s+(\w)", r"\\sqrt{\1}", s)
    return sp.nsimplify(_tex(s, {"n": n})) if "n" not in s else _tex(s, {"n": n})


def eq(a, b):
    try:
        return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0
    except Exception:
        return False


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def present(block, text, where):
    c = block.count(text)
    report(c == 1, f"{where} printed once: {text[:60]}", f"found {c} times")


def chain(block, where, template, value, sep="="):
    """'@' holds a chain A=B=C (TeX); every non-text member equals value."""
    label = f"{where} {template[:60]}"
    try:
        (g,) = grab(block, template, where)
        sides = [s for s in split_top(g, sep) if s.strip()]
        vals = [T(s) for s in sides if "\\text" not in s]
        ok = len(vals) >= 1 and all(eq(v, value) for v in vals)
        report(ok, label, f"printed {g[:120]} -> {vals[:6]}; expected {value}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def aligned_rows(block, start_marker, where):
    """Rows of the first \\begin{aligned}...\\end{aligned} after start_marker: list of row strings."""
    i = block.find(start_marker)
    if i < 0 or block.count(start_marker) != 1:
        raise LookupError(f"marker {start_marker!r} found {block.count(start_marker)} times in {where}")
    j = block.index("\\begin{aligned}", i)
    e = block.index("\\end{aligned}", j)
    return block[j + len("\\begin{aligned}"):e].split("\\\\")


def check_rows(block, marker, where, value, fn=None):
    """Every member after '&=' in every row (skipping \\text members and rows with \\cdots/\\dots) equals value."""
    try:
        rows = aligned_rows(block, marker, where)
    except Exception as err:
        report(False, f"{where} {marker}", f"ERROR {err}")
        return
    used = 0
    for r in rows:
        r = re.sub(r"\\qquad\(.*?\)", "", re.sub(r"\\qquad\\text\{.*?\}", "", r))
        rhs = r.split("&", 1)[1] if "&" in r else r
        rhs = rhs.lstrip("=")
        for m in split_top(rhs, "="):
            m = m.strip()
            if not m or "\\text" in m or "\\cdots" in m or "\\dots" in m or "\\pi r" in m:
                continue
            m = m.replace("\\big(", "(").replace("\\big)", ")")
            try:
                v = T(m)
            except Exception as err:
                report(False, f"{where} row member {m[:50]}", f"ERROR {err}")
                continue
            used += 1
            report(eq(v, value), f"{where} member {m[:60]}", f"= {sp.simplify(v)}; expected {value}")
    report(used >= 1, f"{where} {marker[:30]}: members checked", f"{used} members")


def lettered(block):
    """Split an answer block at <b>a</b>, <b>b</b>, ... -> {letter: text}."""
    bits = re.split(r"<b>([a-p])</b>", block)
    return {bits[i]: bits[i + 1] for i in range(1, len(bits), 2)}


def maths(text):
    return re.findall(r"\\\((.*?)\\\)", text, re.S)


def integral(f, a, b):
    return sp.nsimplify(sp.integrate(f, (x, a, b)))


def parse_int(s, where):
    """\\int_a^b f\\,dx -> (a, b, f)."""
    m = re.fullmatch(r"\s*\\(?:displaystyle)?\\?int_(\{[^}]*\}|-?\w)\^(\{[^}]*\}|\w)\s*(.+?)\\,dx\s*", s.replace("\\displaystyle", ""))
    if not m:
        raise ValueError(f"cannot read integral {s!r} in {where}")
    a, b, f = m.group(1).strip("{}"), m.group(2).strip("{}"), m.group(3).strip()
    if f.startswith("(") and f.endswith(")"):
        f = f[1:-1]
    return T(a), T(b), _tex(f.replace("\\sqrt x", "\\sqrt{x}"))


les = read("l5a.html")
ans = read("a_5a.html")
for need in ("<!-- ============ Homework ============ -->", "<!-- ============ Past papers ============ -->"):
    if les.count(need) != 1:
        sys.exit(f"FAIL: {need} not found once in l5a.html")
teach, rest = les.split("<!-- ============ Homework ============ -->")
hw, ppl = rest.split("<!-- ============ Past papers ============ -->")
CON = {}
for c in range(1, 5):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[c] = {kind: body for kind, _, body in exs}
    report([kd for kd, _, _ in exs] == (["demo", "attempt"] if c in (1, 3, 4) else ["demo", "attempt", "worked"]),
           f"Concept {c} blocks", str([kd for kd, _, _ in exs]))
TQ = dict(re.findall(r'<div class="q"(?: style="[^"]*")?><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"|\{\{band|</div>\{\{work:\d+\}\}</div>\n<div class="q">|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 18)], "textbook questions 1-17", str(sorted(TQ, key=int)))
bands = hw.split("{{band:D}}")
report(hw.count("{{band:F}}") == 1 and bands[0].count('class="q-num"') == 7
       and bands[1].split("{{band:E}}")[0].count('class="q-num"') == 7 and hw.split("{{band:E}}")[1].count('class="q-num"') == 3,
       "bands", "F: Q1-7, D: Q8-14, E: Q15-17 (as the textbook)")
parts_a = ans.split('<div class="ans-sec">')
report(len(parts_a) == 4 and parts_a[1].startswith("Lesson Examples") and parts_a[2].startswith("Textbook Homework")
       and parts_a[3].startswith("Past-Paper Homework"), "answer sections", "Lesson Examples, Textbook Homework, Past-Paper")
BLK = dict(re.findall(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S))

# ---------------------------------------------------------------- Concept 1 (definition)
d1, y1 = CON[1]["demo"], CON[1]["attempt"]
a1 = BLK["C1"]
dm, yt = a1.split("<b>Your turn.</b>")
for blk, q, expect_int, f_b, ab_b, f_c, ab_c in (
        (d1, dm, r"\displaystyle\int_1^4x^3\,dx", 9 - x ** 2, (0, 3), x + 1, (-2, 1)),
        (y1, yt, r"\displaystyle\int_4^9\sqrt x\,dx", 4 - x ** 2, (-2, 2), x - 1, (0, 3))):
    present(q, expect_int, "C1 answer integral")
    # part b: integrand never negative on the interval (checked on a fine grid and at the ends)
    a_, b_ = ab_b
    pts = [a_ + (b_ - a_) * i / 400 for i in range(401)]
    report(all(f_b.subs(x, p) >= 0 for p in pts), f"C1 part b: {f_b} >= 0 on [{a_}, {b_}]")
    present(blk, r"\displaystyle\int_0^3(9-x^2)\,dx" if a_ == 0 else r"\displaystyle\int_{-2}^{2}(4-x^2)\,dx", "C1 part b question")
    a_, b_ = ab_c
    neg = [p for p in [a_ + (b_ - a_) * i / 400 for i in range(401)] if f_c.subs(x, p) < 0]
    zero = sp.solve(f_c, x)[0]
    report(bool(neg) and abs(max(neg) - zero) < 0.02 and min(neg) == a_,
           f"C1 part c: {f_c} < 0 exactly on [{a_}, {zero})", "the answer names this interval")
present(dm, r"For \(-2\le x<-1\), \(x+1<0\)", "C1 demo c")
present(yt, r"For \(0\le x<1\), \(x-1<0\)", "C1 your-turn c")

# ---------------------------------------------------------------- Concept 2 (area formulae)
we1 = CON[2]["worked"]
WE1 = {"a": (1, 4, x - 1, sp.Rational(9, 2)), "b": (2, 4, x - 1, 4), "c": (-2, 2, sp.Abs(x), 4),
       "d": (-5, 5, sp.sqrt(25 - x ** 2), sp.Rational(25, 2) * sp.pi)}            # textbook Example 1 values
qline = we1.split('<div class="sol-label">')[0]
for p, (a_, b_, f, tb) in WE1.items():
    try:
        (s,) = grab(qline, f'<span class="pl">{p}</span>\\(@\\)</span>', "WE1 question")
        A, B, Fx = parse_int(s, "WE1")
        val = integral(Fx, A, B)
        report((A, B) == (a_, b_) and eq(Fx, f) and eq(val, tb), f"WE1 {p} question and value", f"{s} = {val}; textbook {tb}")
    except Exception as err:
        report(False, f"WE1 {p} question", f"ERROR {err}")
        val = tb
    check_rows(we1, f"<p><b>{p}</b>", f"WE1 {p}", val)
present(we1, r"with base \(4-1=3\) and height \(3\)", "WE1 a")
present(we1, r"with width \(4-2=2\) and parallel sides of length 1 and 3", "WE1 b")
present(we1, "The shaded region is a semi-circle with radius 5.", "WE1 d")
# the 'Steps the book skips' tip after Worked example 1 (the pack's added lines)
t1 = we1.split('<div class="box tip"')[1]
present(t1, r"the value of \(x-1\) at \(x=4\), which is \(4-1=3\)", "WE1 tip a")
for txt, val in ((r"\dfrac{1+3}{2}\times2=2\times2=4", 4), (r"2\times\big(\tfrac12\times2\times2\big)=2\times2=4", 4), (r"4-1=3", 3)):
    present(t1, txt, "WE1 tip")
    report(all(eq(T(m.replace("\\big", "")), val) for m in split_top(txt, "=")), f"WE1 tip chain {txt[:40]} = {val}")
present(t1, r"the values of \(x-1\) at \(x=2\) and at \(x=4\)", "WE1 tip b")
report((2 - 1, 4 - 1) == (1, 3) and abs(-2) == 2 == abs(2), "WE1 tip: heights 1, 3 (x-1 at 2, 4) and 2 (|x| at -2, 2)")
present(t1, r"gives \(x^2+y^2=25\) with \(y\ge0\)", "WE1 tip d")

a2 = BLK["C2"]
dm, yt = a2.split("<b>Your turn.</b>")
for blk, q, where in ((CON[2]["demo"], dm, "C2 demo"), (CON[2]["attempt"], yt, "C2 your turn")):
    for p in "abcd":
        try:
            (s,) = grab(blk, f'<span class="pl">{p}</span>\\(@\\)</span>', where)
            A, B, Fx = parse_int(s, where)
            val = integral(Fx, A, B)
            g = lettered(q)[p]
            m = re.search(r"\\\(\\displaystyle(\\int.*?\\,dx)=(.*?)\\\)", g)
            A2, B2, F2 = parse_int(m.group(1), where)
            report((A2, B2) == (A, B) and eq(F2, Fx), f"{where} {p} answer repeats the question", m.group(1))
            members = [T(t) for t in split_top(m.group(2), "=")]
            report(all(eq(v, val) for v in members), f"{where} {p} every member = {val}", m.group(2))
        except Exception as err:
            report(False, f"{where} {p}", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 3 (trapping)
def sums(fn, a_, b_, m):
    w = F(b_ - a_, m) if isinstance(a_, int) else (b_ - a_) / m
    ys = [fn(a_ + w * i) for i in range(m + 1)]
    return w * sum(ys[:-1]), w * sum(ys[1:])          # increasing functions: lower = left ends


c3 = CON[3]["attempt"]
we2b = c3.split('<div class="box concept"')[1].split('<div class="box tip"')[0]       # the book's lines (PDF 216)
we2 = c3.split('<div class="box tip"')[1]                                              # the pack's steps
bsegs = re.split(r"<p>In the (first|second|third|fourth) picture,</p>", we2b)
bpics = dict(zip(bsegs[1::2], bsegs[2::2]))
for name, m in (("first", 2), ("second", 3), ("third", 4), ("fourth", 5)):
    lo, up = sums(lambda t: t * t, 0, 1, m)
    rows = bpics.get(name, "").split("\\begin{aligned}")[1].split("\\end{aligned}")[0].split("\\\\") if name in bpics else []
    if len(rows) == 3:                     # a long first line set on two rows: lower < A, then < upper
        rows = [rows[0] + rows[1].replace("\\qquad", ""), rows[2]]
    good = len(rows) == 2
    for r in rows:
        L, R = r.replace("&", "").split("<A<")
        good &= eq(T(L.replace("\\Big", "").replace("\\big", "")), lo) and eq(T(R.replace("\\Big", "").replace("\\big", "")), up)
    report(good, f"WE2 book box, {name} picture: both rows are lower < A < upper", f"{lo} < A < {up}, {len(rows)} rows")
segs = re.split(r"<p>In the (first|second|third|fourth) picture", we2)
pics = dict(zip(segs[1::2], segs[2::2]))
for name, m in (("first", 2), ("second", 3), ("third", 4), ("fourth", 5)):
    lo, up = sums(lambda t: t * t, 0, 1, m)
    blk = pics.get(name, "")
    present(blk, f"strips of width \\(\\tfrac1{m}\\)", f"WE2 {name} picture")
    rows = blk.split("\\begin{aligned}")[1].split("\\end{aligned}")[0].split("\\\\") if "\\begin{aligned}" in blk else []
    if m <= 3:
        good = len(rows) >= 3
        for r in rows:
            L, R = r.replace("&", "").split("<A<")
            good &= eq(T(L), lo) and eq(T(R), up)
        report(good, f"WE2 {name} picture: every row is lower < A < upper", f"{lo} < A < {up}, {len(rows)} rows")
    else:
        good = len(rows) == 2
        for r, v in zip(rows, (lo, up)):
            members = [s for s in split_top(r.replace("&", ""), "=") if s.strip()]
            good &= all(eq(T(s), v) for s in members)
        report(good, f"WE2 {name} picture: lower and upper chains", f"{lo}, {up}")
    (L, R) = grab(blk, "so \\(@<A<@\\)", f"WE2 {name}") if m > 3 else (None, None)
    if m > 3:
        report(eq(T(L), lo) and eq(T(R), up), f"WE2 {name} picture: final sandwich", f"{L} < A < {R}")
textbook_bounds = {2: (F(1, 8), F(5, 8)), 3: (F(5, 27), F(14, 27)), 4: (F(14, 64), F(30, 64)), 5: (F(30, 125), F(55, 125))}
report(all(sums(lambda t: t * t, 0, 1, m) == textbook_bounds[m] for m in textbook_bounds), "WE2 = textbook bounds (PDF 216)")
try:
    dec = re.search(r"As decimals, the four sandwiches are (.*?): the bounds", we2, re.S).group(1)
    nums = re.findall(r"0\.\d+", dec)
    exp = [float(v) for m in (2, 3, 4, 5) for v in sums(lambda t: t * t, 0, 1, m)]
    ok = len(nums) == 8 and all(abs(float(a) - b) < 10 ** -(len(a) - 2) for a, b in zip(nums, exp))
    report(ok, "WE2 decimals", f"{nums} vs {[round(e, 5) for e in exp]}")
except Exception as err:
    report(False, "WE2 decimals", f"ERROR {err}")

a3 = BLK["C3"]
dm, yt = a3.split("<b>Your turn.</b>")
for blk, q, fn, B_, box, where in ((CON[3]["demo"], dm, lambda t: t ** 3, 1, 1, "C3 demo"),
                                   (CON[3]["attempt"], yt, lambda t: t ** 2, 2, 8, "C3 your turn")):
    present(blk, f"0<A<{box}" if box != 1 else "0<A<1", f"{where} question")
    present(blk, f"0\\le x\\le{B_}\\) into 2 strips", f"{where} question")
    present(blk, "with 4 strips", f"{where} question")
    present(q, f"Hence \\(0<A<{box}\\)", f"{where} a")
    for m, part in ((2, "b"), (4, "c")):
        lo, up = sums(fn, 0, B_, m)
        try:
            seg = q.split(f"<b>{part}</b>")[1].split("<br>")[0]
            low = re.search(r"Lower: \\\((.*?)\\\)", seg).group(1)
            upp = re.search(r"Upper: \\\((.*?)\\\)", seg).group(1)
            fin = re.search(r"So \\\((.*?)<A<(.*?)\\\)", seg)
            lv = [T(s) for s in split_top(low, "=")]
            uv = [T(s) for s in split_top(upp, "=")]
            report(all(eq(v, lo) for v in lv), f"{where} {part} lower sum chain = {lo}", low[:90])
            report(all(eq(v, up) for v in uv), f"{where} {part} upper sum chain = {up}", upp[:90])
            report(eq(T(fin.group(1)), lo) and eq(T(fin.group(2)), up), f"{where} {part} bounds", fin.group(0)[:60])
        except Exception as err:
            report(False, f"{where} {part}", f"ERROR {err}")
present(dm, r"shows that \(A=\tfrac14=\tfrac{16}{64}\)", "C3 demo exact value")
report(eq(integral(x ** 3, 0, 1), sp.Rational(16, 64)), "int_0^1 x^3 dx = 16/64")

# ---------------------------------------------------------------- Concept 4 (limits)
def sum_closed(h, lo_k, hi_k, w):
    return sp.simplify(w * sp.summation(h, (k, lo_k, hi_k)))


seg4 = teach.split("<!-- ============ Concept 4 ============ -->")[1].split('<div class="ex demo"')[0]
we3 = seg4.split('<div class="bt">The limiting process:')[1]       # the book's steps A-D, then the pack's tip
U = sum_closed((k / n) ** 2, 1, n, 1 / n)
L = sum_closed((k / n) ** 2, 1, n - 1, 1 / n)
check_rows(we3, "<p><b>B</b>", "WE3 upper sum", U)
check_rows(we3, "<p><b>C</b>", "WE3 lower sum", L)
report(sp.limit(U, n, sp.oo) == sp.Rational(1, 3) and sp.limit(L, n, sp.oo) == sp.Rational(1, 3), "WE3 limits are 1/3")
present(we3, r"upper rectangles has limit \(\tfrac13\) as \(n\to\infty\)", "WE3 B limit")
present(we3, r"has limit \(\tfrac13\times1\times1=\tfrac13\).", "WE3 tip limit")
present(we3, r"\(6n^3=3\times n\times n\times2n\)", "WE3 tip factor")
report(sp.expand(6 * n ** 3 - 3 * n * n * 2 * n) == 0, "6n^3 = 3 x n x n x 2n")
try:
    (g,) = grab(we3, r'<li data-c="t3b2">To split the fraction, write \(6n^3=3\times n\times n\times2n\):' + "\n" + r'\[\begin{aligned}@\end{aligned}\]</li>', "WE3 tip")
    mem = split_top(g.replace("&", "").replace("\\\\", "").rstrip("."), "=")
    report(len(mem) == 3 and all(eq(T(m_), U) for m_ in mem), "WE3 tip: every member of the split = upper sum", g[:90])
except Exception as err:
    report(False, "WE3 tip split chain", f"ERROR {err}")
present(we3, r"&=\frac1n\times\frac{1}{n^2}\times(1^2+2^2+\cdots+n^2)\\&=\frac{1}{n^3}(1^2+2^2+\cdots+n^2).", "WE3 tip common factor")
present(we3, r"also has limit \(\tfrac13\) as \(n\to\infty\)", "WE3 C limit")
present(we3, r"so it follows that \(A=\tfrac13\)", "WE3 D")
# the formula quoted in the box and used in the proofs
report(sp.simplify(sp.summation(k ** 2, (k, 1, n)) - n * (n + 1) * (2 * n + 1) / 6) == 0, "sum of squares formula")
report(sp.simplify(sp.summation(k, (k, 1, n)) - n * (n + 1) / 2) == 0, "sum 1..n formula (your turn)")
present(teach, r"1^2+2^2+\cdots+n^2=\tfrac16n(n+1)(2n+1).", "Concept 4 box formula")
present(teach, r"\tfrac16(n-1)\big((n-1)+1\big)\big(2(n-1)+1\big)=\tfrac16(n-1)n(2n-1)", "Concept 4 tip substitution")
report(sp.expand(((n - 1) * ((n - 1) + 1) * (2 * (n - 1) + 1) - (n - 1) * n * (2 * n - 1))) == 0, "n-1 substitution identity")

a4 = BLK["C4"]
dm, yt = a4.split("<b>Your turn.</b>")
U2 = sum_closed((2 * k / n) ** 2, 1, n, 2 / n)
L2 = sum_closed((2 * k / n) ** 2, 1, n - 1, 2 / n)
check_rows(dm, "<b>B</b>", "C4 demo upper sum", U2)
check_rows(dm, "<b>C</b>", "C4 demo lower sum", L2)
report(sp.limit(U2, n, sp.oo) == sp.Rational(8, 3) == sp.limit(L2, n, sp.oo) == integral(x ** 2, 0, 2), "C4 demo limits = 8/3 = sympy integral")
present(dm, r"so \(A=\tfrac83\)", "C4 demo D")
present(CON[4]["demo"], r"A=\displaystyle\int_0^2x^2\,dx", "C4 demo question")
U1 = sum_closed(k / n, 1, n, 1 / n)
L1 = sum_closed(k / n, 1, n - 1, 1 / n)
check_rows(yt, "<b>B</b>", "C4 your-turn upper sum", U1)
check_rows(yt, "<b>C</b>", "C4 your-turn lower sum", L1)
report(sp.limit(U1, n, sp.oo) == sp.Rational(1, 2) == sp.limit(L1, n, sp.oo) == integral(x, 0, 1), "C4 your-turn limits = 1/2")
present(CON[4]["attempt"], r"A=\displaystyle\int_0^1x\,dx", "C4 your-turn question")
present(yt, r"Hence \(A=\tfrac12\)", "C4 your-turn D")

# ---------------------------------------------------------------- textbook homework
TB4 = {"a": 6, "b": 12, "c": 8, "d": 9, "e": 2, "f": F(25, 2), "g": 6, "h": 20}
TB5 = {"a": 8, "b": 25, "c": 9, "d": 24, "e": 36, "f": 24, "g": 9, "h": 8}
TB6 = {"a": 15, "b": 15, "c": 25, "d": 40, "e": F(25, 2), "f": 12, "g": 16, "h": 24, "i": 8, "j": 18, "k": 4, "l": 16,
       "m": 4, "n": 16, "o": F(25, 2), "p": F(25, 2)}
TB7 = {"a": 8 * sp.pi, "b": sp.Rational(25, 4) * sp.pi}
for qn, tb in (("4", TB4), ("5", TB5), ("6", TB6), ("7", TB7)):
    for p, tv in tb.items():
        try:
            (s,) = grab(TQ[qn], f'<span class="pl">{p}</span>\\(@\\)', f"Q{qn}")
            A, B, Fx = parse_int(s, f"Q{qn}")
            val = integral(Fx, A, B)
            g = re.sub(r"&nbsp;|<[^>]+>|\(a (semi|quad).*", "", lettered(BLK[qn])[p]).strip()
            mm = maths(g)
            g = mm[0] if mm else g
            got = T(g)
            report(eq(got, val) and eq(val, tv), f"Q{qn}{p} {s[:40]}", f"printed {g} ; sympy {val} ; textbook {tv}")
        except Exception as err:
            report(False, f"Q{qn}{p}", f"ERROR {err}")

# Q1-3, Q8: chord and rectangle areas
chain(BLK["1"], "Q1a", r"<b>a</b> \(@\ \text{u}^2\)", sp.Rational(1, 2))
chain(BLK["2"], "Q2a", r"<b>a</b> \(@\ \text{u}^2\)", sp.Rational(1, 16))
chain(BLK["2"], "Q2b", r"<b>b</b> \(@\ \text{u}^2\)", sp.Rational(5, 16))
chain(BLK["2"], "Q2c", r"trapezium, \(@\)", sp.Rational(3, 8))
tri = sp.Rational(1, 2) * 1 * 1                                           # triangle OAB, A(1,0), B(1,1)
report(eq(tri, sp.Rational(1, 2)) and integral(x ** 2, 0, 1) < tri, "Q1 triangle OAB above the curve")
ocd = sp.Rational(1, 2) * sp.Rational(1, 2) * sp.Rational(1, 4)
cabd = sp.Rational(1, 2) * (sp.Rational(1, 4) + 1) * sp.Rational(1, 2)
report(ocd == sp.Rational(1, 16) and cabd == sp.Rational(5, 16) and ocd + cabd == sp.Rational(3, 8), "Q2 independent areas")
q3 = sum(sp.Rational(1, 4) * (sp.Rational(i, 4) ** 2 + sp.Rational(i + 1, 4) ** 2) / 2 for i in range(4))
report(q3 == sp.Rational(11, 32) and integral(x ** 2, 0, 1) < q3 < sp.Rational(3, 8), "Q3 four trapezia = 11/32 (stem)", str(q3))
present(TQ["3"], r"\int_0^1x^2\,dx<\tfrac{11}{32}", "Q3 stem")
lo8, up8 = sums(lambda t: t * t, 0, 1, 4)
chain(BLK["8"], "Q8a", r"<b>a</b> \(@\ \text{u}^2\)", lo8)
chain(BLK["8"], "Q8b", r"<b>b</b> \(@\ \text{u}^2\)", up8)
present(TQ["8"], r"\tfrac{7}{32}<\int_0^1x^2\,dx<\tfrac{15}{32}", "Q8c stem")
report((lo8, up8) == (F(7, 32), F(15, 32)), "Q8 = textbook 7/32, 15/32")


def rounded(v, dp):
    return math.floor(v * 10 ** dp + 0.5) / 10 ** dp


# Q9, Q10: the stems' bounds (rounded) and our printed decimals
for qn, fn, a_, b_, cases, exact_v in (("9", lambda t: 2 ** t, 0.0, 1.0, ((1, "1", "2", 0), (2, "1.2", "1.7", 1), (4, "1.3", "1.6", 1)), 1 / math.log(2)),
                                       ("10", math.log, 2.0, 4.0, ((2, "1.79", "2.48", 2), (4, "1.98", "2.33", 2), (8, "2.07", "2.24", 2)), 6 * math.log(2) - 2)):
    for m, ls, us, dp in cases:
        lo, up = sums(fn, a_, b_, m)
        ok = rounded(lo, dp) == float(ls) and rounded(up, dp) == float(us)
        report(ok, f"Q{qn} stem with {m} rectangles: {ls} < I < {us}", f"sums {lo:.5f}, {up:.5f}")
        tmpl = f"{ls}<\\int" if qn == "10" or m > 1 else "1<\\int"
        present(TQ[qn], tmpl if m > 1 or qn == "10" else "\\(1<\\int_0^1 2^x\\,dx<2\\)", f"Q{qn} stem {m}")
    report(abs(float(sp.integrate(sp.Pow(2, x) if qn == "9" else sp.log(x), (x, a_, b_))) - exact_v) < 1e-12, f"Q{qn} exact value")
lo, up = sums(lambda t: 2 ** t, 0.0, 1.0, 2)
chain(BLK["9"], "Q9b lower", r"<b>b</b> \(@\doteq1.21\)", sp.Rational(1, 2) * (1 + sp.sqrt(2)))
chain(BLK["9"], "Q9b upper", r"and \(@\doteq1.71\)<br>", sp.Rational(1, 2) * (sp.sqrt(2) + 2))
report(rounded(lo, 2) == 1.21 and rounded(up, 2) == 1.71, "Q9b decimals 1.21, 1.71")
l4, u4 = sums(lambda t: 2 ** t, 0.0, 1.0, 4)
present(BLK["9"], "<b>c</b> about 1.32 and 1.57", "Q9c")
report(rounded(l4, 2) == 1.32 and rounded(u4, 2) == 1.57, "Q9c decimals", f"{l4:.4f} {u4:.4f}")
present(BLK["9"], r"\frac{1}{\ln2}\doteq1.44", "Q9d")
report(rounded(1 / math.log(2), 2) == 1.44, "1/ln 2 = 1.44")
chain(BLK["10"], "Q10a lower", r"<b>a</b> \(@\doteq1.79\)", sp.log(6))
chain(BLK["10"], "Q10a upper", r"and \(@\doteq2.48\)<br>", sp.log(12))
for m, ls, us in ((4, "1.98", "2.33"), (8, "2.07", "2.24")):
    lo, up = sums(math.log, 2.0, 4.0, m)
    present(BLK["10"], f"about {ls} and {us}", f"Q10 {m} rectangles")
    report(rounded(lo, 2) == float(ls) and rounded(up, 2) == float(us), f"Q10 {m} rectangles decimals")
present(BLK["10"], r"=6\ln2-2\doteq2.16", "Q10d")
report(rounded(6 * math.log(2) - 2, 2) == 2.16, "6 ln 2 - 2 = 2.16")

# Q11: the stems (exact fractions and their decimals)
f11 = lambda t: 1 / (1 + t)  # noqa: E731
for m, lo_s, up_s, dec in ((1, r"\dfrac12", "1", None), (2, r"\tfrac{7}{12}", r"\tfrac56", ("0.58", "0.83")),
                           (3, r"\tfrac{37}{60}", r"\tfrac{47}{60}", ("0.62", "0.78")), (4, r"\tfrac{533}{840}", r"\tfrac{319}{420}", ("0.63", "0.76"))):
    up, lo = sums(f11, 0, 1, m)                                         # decreasing: left ends give the upper sum
    present(TQ["11"], f"{lo_s}<A<{up_s}", f"Q11 stem {m}")
    report(eq(T(lo_s), lo) and eq(T(up_s), up), f"Q11 stem with {m} rectangles exact", f"{lo} < A < {up}")
    if dec:
        present(TQ["11"], f"{dec[0]}<A<{dec[1]}", f"Q11 stem {m} decimals")
        report(rounded(float(lo), 2) == float(dec[0]) and rounded(float(up), 2) == float(dec[1]), f"Q11 decimals {m}")
report(abs(float(integral(1 / (x + 1), 0, 1)) - 0.693147) < 1e-6, "Q11f ln 2 = 0.693147...")
present(TQ["11"], r"\ln2=0.693\,147\ldots", "Q11f stem")

# Q13, Q14: counted squares behind the printed answers
present(BLK["13"], r"approximately 133 squares. \(\tfrac{133}{400}\doteq0.33\)", "Q13a")
report(round(float(integral(x ** 2, 0, 1)) * 400) == 133 and rounded(133 / 400, 2) == 0.33, "Q13a 400/3 = 133 squares")
(g1, g2) = grab(BLK["13"], r"(i) \(@\) &nbsp; (ii) \(@\)", "Q13b")
report(eq(T(g1), integral(x ** 2, 0, sp.Rational(1, 2))) and eq(T(g2), integral(x ** 2, sp.Rational(1, 2), 1))
       and eq(T(g1) + T(g2), sp.Rational(1, 3)), "Q13b exact values 1/24, 7/24", f"{g1}, {g2}")
q14 = integral(sp.sqrt(1 - x ** 2), 0, 1)
present(BLK["14"], "<b>a</b> about 314 squares &nbsp; <b>b</b> 0.79 &nbsp; <b>c</b> 3.16", "Q14")
report(round(float(q14) * 400) == 314 and rounded(float(q14), 2) == 0.79 and rounded(4 * 0.79, 2) == 3.16, "Q14 values", f"{float(q14):.5f}")

# Q17: area of the polygon by trapezia
trap = sp.simplify(sp.summation(((k - 1) ** 2 + k ** 2) / (2 * n ** 2) / n, (k, 1, n)))
(g,) = grab(BLK["17"], r"<b>a</b> \(@\)<br>", "Q17a")
report(eq(T(g), trap) and sp.limit(trap, n, sp.oo) == sp.Rational(1, 3), "Q17a polygon area = 1/3 + 1/(6n^2)", f"{g} vs {trap}")
present(BLK["17"], "lie above the curve", "Q17b")

# answers present only for items with a final answer
report(sorted(k_ for k_ in BLK if not k_.startswith("C")) == sorted(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "13", "14", "17"], key=int)
       or sorted((k_ for k_ in BLK if not k_.startswith("C")), key=int) == ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "13", "14", "17"],
       "textbook answers: Q1-11, 13, 14, 17 (12 technology, 15-16 proofs)", str(sorted((k_ for k_ in BLK if not k_.startswith("C")), key=int)))

# ---------------------------------------------------------------- past paper
PPQ = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span><span class="mk">(\d+) marks?</span></div>(.*?)(?=<div class="pp">|$)', ppl, re.S)
PPA = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span></div>(.*?)(?=<div class="ppa">|$)', ans, re.S)
report(len(PPQ) == 1 and len(PPA) == 1, "one past-paper question, one solution")
num, lab, mk, body = PPQ[0]
clean = re.sub(r"\s+", " ", re.sub("<[^>]+>|&nbsp;", " ", lab)).replace(" ,", ",").strip()
report(lab == PPA[0][1] and clean == "James Ruse Agricultural High School, 2023, Year 12 Trial HSC Examination, Mathematics Extension 1, Q4",
       "PP1 source label (both files, as printed on the cover)", clean)
tot = re.search(r"<span><b>(\d+) marks?</b></span>", ppl).group(1)
(tm,) = grab(ppl, "<b>Suggested time: @ minutes</b>", "pp intro")
report(int(tot) == int(mk) == 1, "PP marks total 1")
report(int(tm) == max(5, 5 * math.ceil(1.5 * int(tot) / 5)), "PP time 1.5 x marks rounded to 5 min (min 5)", tm)
report(body.count('class="hint"') == 1, "PP1 one hint")
present(ppl, "For more timed practice, do Questions 5(d), 6(h), 6(o), 7(a), 8 and 11(c) above in 25 minutes.", "timed-practice note")
fpw = sp.Piecewise((2, x < 3), (x - 1, True))
present(body, r"f(x)=\begin{cases}2, & x<3\\ x-1, & x\ge3\end{cases}", "PP1 stem f(x)")
present(body, r"\int_1^5 f(x)\,dx", "PP1 stem integral")
val = sp.integrate(fpw, (x, 1, 5))
opts = dict(re.findall(r"<span>([A-D])\.&ensp;(\d+)</span>", body))
report(sorted(opts) == list("ABCD") and [l for l, v in opts.items() if int(v) == val] == ["D"], "PP1 MC: only D equals the integral", f"{opts}, value {val}")
sol = PPA[0][2]
present(sol, "<b>Answer D.</b>", "PP1 answer letter")
check_rows(sol, r"\[\begin{aligned}\int_1^5f(x)\,dx", "PP1 solution chain", val)
report(eq(2 * (3 - 1) + sp.Rational(2 + 4, 2) * (5 - 3), val), "PP1 rectangle + trapezium = sympy integral")
report(int(opts["B"]) == sp.integrate(x - 1, (x, 3, 5)) and int(opts["C"]) == 2 * (5 - 1), "PP1 distractor notes (B trapezium, C rectangle of height 2)")

# ---------------------------------------------------------------- figures referenced exist
for name in set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans)):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}.svg exists")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:40], sep="\n  ")
    sys.exit(1)
print("ALL OK")
