r"""Check of Lesson 5B (Integration Part 1 pack): The fundamental theorem of calculus.

The script reads the values PRINTED in workspace/build/int1/l5b.html (the integrals of the tutor demos,
your-turn items, worked examples, every textbook question and the past-paper question) and in a_5b.html
(lesson-example answers, textbook answers, past-paper solution). Each value is found with a template
('@' marks the printed TeX); a template must match exactly once in its block, otherwise the item FAILS.
Printed TeX is turned into sympy (workspace/checks/int3_tex.py, plus mixed numbers such as 89\tfrac16)
and compared with an independent computation:
  - every definite integral: sympy.integrate of the integrand READ from the lesson page;
  - every member of every printed working chain (aligned rows) equals the sympy value of the integral;
  - the primitive written in square brackets differentiates back to the integrand (sympy.diff), and
    the bracket evaluated at the printed limits equals the integral;
  - the area checks (triangle, trapezium) and the circle argument are recomputed from the formulae;
  - the 'meaningless' integrals have a pole of the integrand inside the interval (sympy.singularities);
  - Q10, Q11: k solved with sympy.solve from the stems read from the page (k > 0);
  - Q12: the integral of the piecewise f read from the figure description (quadrants, lines);
  - Q16: sympy.diff of the integral with a variable upper limit (Q17 is omitted as a later-method item).
The textbook's printed answers (Ext 1 Y12 PDF 889) are transcribed below and compared as well.
Past paper: marks add to the intro total, time 1.5 x marks rounded up to 5 minutes (min 5), labels match
in both files, one hint (a neutral question: no numbers, no method words), and the MC letter is the only option equal to the value of the integral, computed
from f(x) = max(0, 1 - |x|) (the printed graph) with sympy.

Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5b.py
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
t = sp.Symbol("t", real=True)
k = sp.Symbol("k", positive=True)
R = sp.Rational


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
    """Printed TeX -> sympy (mixed numbers, brackets and spacing handled here)."""
    s = s.strip().rstrip(".,")
    s = re.sub(r"\\(?:displaystyle|left|right|quad|qquad|phantom\{[^}]*\})", "", s)
    s = re.sub(r"(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)             # 89\tfrac16 -> (89+1/6)
    s = re.sub(r"(\d+)\\tfrac\{(\d+)\}\{(\d+)\}", r"(\1+\2/\3)", s)
    s = s.replace("\\,", "").replace("\\ ", "").replace("\\Big", "").replace("\\big", "")
    s = s.replace("\\times", "*")
    return _tex(s, {"k": k, "t": t})


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


INT_RX = re.compile(r"\\int_(\{[^}]*\}|-?\w)\^(\{[^}]*\}|\w)\s*(.+?)\\?,?\s*d([xt])$")


def parse_int(s, where):
    """\\int_a^b f\\,dx (as printed) -> (a, b, f)."""
    s = s.replace("\\displaystyle", "").strip()
    m = re.fullmatch(r"\\int_(\{[^}]*\}|-?\w)\^(\{[^}]*\}|\w)\s*(.*?)\s*(?:\\,)?\s*d([xt])", s)
    if not m:
        raise ValueError(f"cannot read integral {s!r} in {where}")
    a, b, f = m.group(1).strip("{}"), m.group(2).strip("{}"), m.group(3).strip()
    if f == "":
        f = "1"
    if f.startswith("\\frac{") and f.endswith("}") and m.group(4) == "x" and f.count("\\frac") == 1 and "dx" in f:
        pass
    if f.startswith("(") and f.endswith(")") and f.count("(") == 1:
        f = f[1:-1]
    return T(a), T(b), T(f)


def value(a, b, f):
    return sp.nsimplify(sp.integrate(f, (x, a, b)))


def aligned_rows(block, start_marker, where, first=False):
    """Rows of the aligned environment that contains (or starts at) start_marker."""
    i = block.find(start_marker)
    if i < 0 or (block.count(start_marker) != 1 and not first):
        raise LookupError(f"marker {start_marker!r} found {block.count(start_marker)} times in {where}")
    j = block.rfind("\\begin{aligned}", 0, i + len("\\begin{aligned}"))
    e = block.index("\\end{aligned}", j)
    return block[j + len("\\begin{aligned}"):e].split("\\\\")


def bracket_ok(m, where, integrand, a, b, val):
    """A member \\Big[F(x)\\Big]_a^b: F' = integrand and F(b) - F(a) = val."""
    mm = re.fullmatch(r"\s*\\Big\[(.*)\\Big\]_(\{[^}]*\}|-?\w)\^(\{[^}]*\}|\w)\s*", m)
    if not mm:
        return False
    F = T(mm.group(1))
    lo, hi = T(mm.group(2).strip("{}")), T(mm.group(3).strip("{}"))
    ok1 = eq(sp.diff(F, x), integrand)
    ok2 = eq(lo, a) and eq(hi, b) and eq(F.subs(x, hi) - F.subs(x, lo), val)
    report(ok1 and ok2, f"{where} primitive {mm.group(1)[:40]}", f"F'={sp.simplify(sp.diff(F, x))} vs {integrand}; limits {lo},{hi}")
    return True


def check_chain(block, marker, where, a, b, f, minimum=2, first=False):
    """Every member of the aligned chain after marker: integrals of the same value, brackets checked as
    primitives, other members equal to the value. \\text and lines with \\cdots are skipped."""
    val = value(a, b, f)
    try:
        rows = aligned_rows(block, marker, where, first)
    except Exception as err:
        report(False, f"{where} chain", f"ERROR {err}")
        return val
    used = 0
    for r in rows:
        r = re.sub(r"\\qquad\\text\{\(.*$", "", r)           # a trailing annotation '(...)' (may hold maths)
        r = re.sub(r"\\qquad\\text\{.*?\}", "", r)
        r = re.sub(r"\\text\{[^}]*\}", "", r)
        r = r.replace("&", "")
        for m in split_top(r, "="):
            m = m.strip().rstrip(".")
            m = re.sub(r"^\\quad|^\\qquad\\quad", "", m).strip()
            if not m:
                continue
            if m.startswith("-(0-0+0)"):
                continue
            if "\\int" in m:
                try:
                    A, B, Fx = parse_int(m, where)
                    used += 1
                    report(eq(value(A, B, Fx), val), f"{where} integral {m[:50]}", f"{value(A, B, Fx)} vs {val}")
                except Exception as err:
                    report(False, f"{where} integral {m[:50]}", f"ERROR {err}")
                continue
            if "\\Big[" in m:
                used += 1
                if not bracket_ok(m, where, f, a, b, val):
                    report(False, f"{where} bracket {m[:50]}", "unreadable")
                continue
            try:
                v = T(m)
            except Exception as err:
                report(False, f"{where} member {m[:50]}", f"ERROR {err}")
                continue
            used += 1
            report(eq(v, val), f"{where} member {m[:60]}", f"= {sp.nsimplify(v)}; expected {val}")
    report(used >= minimum, f"{where}: members checked", f"{used} members")
    return val


les = read("l5b.html")
ans = read("a_5b.html")
for need in ("<!-- ============ Homework ============ -->", "<!-- ============ Past papers ============ -->"):
    if les.count(need) != 1:
        sys.exit(f"FAIL: {need} not found once in l5b.html")
teach, rest = les.split("<!-- ============ Homework ============ -->")
hw, ppl = rest.split("<!-- ============ Past papers ============ -->")
CON = {}
for c in range(1, 7):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[c] = {kind: body for kind, _, body in exs}
    want = ["demo", "attempt"] if c == 6 else ["demo", "attempt", "worked"]
    report([kd for kd, _, _ in exs] == want, f"Concept {c} blocks", str([kd for kd, _, _ in exs]))
TQ = dict(re.findall(r'<div class="q"(?: style="[^"]*")?><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"><span class="q-num">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 17)], "textbook questions 1-16 (Q17 omitted: later method)", str(sorted(TQ, key=int)))
bF, bD = hw.split("{{band:D}}")
report(hw.count("{{band:F}}") == 1 and "{{band:E}}" not in hw and bF.count('class="q-num"') == 5 and bD.count('class="q-num"') == 11,
       "bands", "F: Q1-5, D: Q6-16 (as the textbook; the E band held only Q17)")
parts_a = ans.split('<div class="ans-sec">')
report(len(parts_a) == 4 and parts_a[1].startswith("Lesson Examples") and parts_a[2].startswith("Textbook Homework")
       and parts_a[3].startswith("Past-Paper Homework"), "answer sections", "Lesson Examples, Textbook Homework, Past-Paper")
BLK = dict(re.findall(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S))


def items(block, where):
    """Lettered integrals \\(\\displaystyle\\int...\\) in a question/example block -> {letter: (a, b, f, tex)}."""
    out = {}
    for lab, s in re.findall(r'<span class="pl">([a-z]+)</span>\\\((\\displaystyle\\int.*?)\\\)', block, re.S):
        try:
            a, b, f = parse_int(s, where)
            out[lab] = (a, b, f, s.replace("\\displaystyle", ""))
        except Exception as err:
            report(False, f"{where}{lab} read", f"ERROR {err}")
    return out


def demo_answer_halves(a_block):
    d, y = a_block.split("<b>Your turn.</b>")
    return d, y


def letter_parts(block):
    bits = re.split(r"<b>([a-d])</b>", block)
    return {bits[i]: bits[i + 1] for i in range(1, len(bits), 2)}


# ---------------------------------------------------------------- lesson examples C1-C5: chains
EXPECT = {  # independent hand values for the demo / your-turn items (also recomputed by sympy)
    1: ({"a": 9, "b": 12}, {"a": 2, "b": 6}),
    2: ({"a": R(7, 3), "b": 39, "c": 8, "d": 12}, {"a": R(4, 3), "b": R(46, 3), "c": 32, "d": 15}),
    3: ({"a": R(50, 3), "b": R(99, 2)}, {"a": R(41, 6), "b": R(38, 3)}),
    4: ({"a": R(86, 3), "b": 14}, {"a": 16, "b": R(7, 2)}),
    5: ({"a": R(3, 4), "b": R(3, 8)}, {"a": R(2, 3), "b": R(15, 64)}),
}
for c in range(1, 6):
    dq, yq = items(CON[c]["demo"], f"C{c} demo"), items(CON[c]["attempt"], f"C{c} your turn")
    da, ya = demo_answer_halves(BLK[f"C{c}"])
    for tag, qd, ablk, exp in (("demo", dq, da, EXPECT[c][0]), ("your turn", yq, ya, EXPECT[c][1])):
        report(sorted(qd) == sorted(exp), f"C{c} {tag} parts", str(sorted(qd)))
        lp = letter_parts(ablk)
        for lab, (a, b, f, s) in qd.items():
            v = value(a, b, f)
            report(eq(v, exp.get(lab, None)), f"C{c} {tag} {lab} sympy = hand value", f"{s[:40]} = {v}")
            blk = lp.get(lab, "")
            if "\\begin{aligned}" in blk:
                first = re.search(r"\\begin\{aligned\}(.*?)&", blk).group(1)
                check_chain(blk, "\\begin{aligned}", f"C{c} {tag} {lab}", a, b, f, first=True)
            else:
                mm = maths_ = re.findall(r"\\\((.*?)\\\)", blk, re.S)
                chain = [m for m in mm if "\\int" in m and "=" in m]
                ok = len(chain) == 1
                if ok:
                    for mem in split_top(chain[0].replace("\\displaystyle", ""), "="):
                        mem = mem.strip()
                        if "\\int" in mem:
                            ok &= eq(value(*parse_int(mem, "C")[:3]), v)
                        elif "\\Big[" in mem:
                            ok &= bracket_ok(mem, f"C{c} {tag} {lab}", f, a, b, v)
                        else:
                            ok &= eq(T(mem), v)
                report(ok, f"C{c} {tag} {lab} inline chain", chain[0][:80] if chain else "missing")

# C1 area checks (triangle / trapezium) printed in the answers
for tag, txt, base_h, val in (("demo a", r"\tfrac12\times3\times6=9", None, 9),
                              ("demo b", r"\dfrac{1+7}{2}\times3=4\times3=12", None, 12),
                              ("yt a", r"\tfrac12\times1\times4=2", None, 2),
                              ("yt b", r"\dfrac{1+5}{2}\times2=3\times2=6", None, 6)):
    present(BLK["C1"], txt, f"C1 {tag} area")
    mem = split_top(txt, "=")
    report(all(eq(T(m), val) for m in mem), f"C1 {tag} area members = {val}")
for lab, (b_, h_) in (("demo a", (3, 6)), ("yt a", (1, 4))):
    report(eq(R(1, 2) * b_ * h_, sp.integrate(2 * x if lab == "demo a" else 4 * x, (x, 0, b_))), f"C1 {lab} triangle = integral")
report(eq(R(1 + 7, 2) * 3, sp.integrate(2 * x - 3, (x, 2, 5))) and (2 * 2 - 3, 2 * 5 - 3) == (1, 7), "C1 demo b trapezium sides 1, 7")
report(eq(R(1 + 5, 2) * 2, sp.integrate(2 * x - 5, (x, 3, 5))) and (2 * 3 - 5, 2 * 5 - 5) == (1, 5), "C1 yt b trapezium sides 1, 5")

# WE3b expansion line printed in the lesson
present(CON[3]["worked"], r"\((x-4)(x-6)=x^2-6x-4x+24=x^2-10x+24\)", "WE3b expansion (tip)")
report(eq(sp.expand((x - 4) * (x - 6)), x**2 - 6 * x - 4 * x + 24) and eq(x**2 - 6 * x - 4 * x + 24, x**2 - 10 * x + 24), "WE3b expansion values")
present(CON[3]["worked"], r"\(x(x+1)=x^2+x\)", "WE3a expansion")
report(eq(sp.expand(x * (x + 1)), x**2 + x), "WE3a expansion value")

# C3/C4 expansions and splits printed in the answers
for txt, lhs, rhs in ((r"\((x-5)(x-6)=x^2-6x-5x+30=x^2-11x+30\)", (x - 5) * (x - 6), x**2 - 11 * x + 30),
                      (r"\((x-3)(x-4)=x^2-4x-3x+12=x^2-7x+12\)", (x - 3) * (x - 4), x**2 - 7 * x + 12),
                      (r"\(x(x+2)=x^2+2x\)", x * (x + 2), x**2 + 2 * x), (r"\(x(x+3)=x^2+3x\)", x * (x + 3), x**2 + 3 * x)):
    present(BLK["C3"], txt, "C3 expansion")
    report(eq(sp.expand(lhs), rhs), f"C3 expansion {txt[2:30]}")
for txt, lhs, rhs in ((r"\dfrac{4x^4-3x^2}{x^2}=\dfrac{4x^4}{x^2}-\dfrac{3x^2}{x^2}=4x^2-3", (4 * x**4 - 3 * x**2) / x**2, 4 * x**2 - 3),
                      (r"\dfrac{x^3-3x^4}{x^3}=\dfrac{x^3}{x^3}-\dfrac{3x^4}{x^3}=1-3x", (x**3 - 3 * x**4) / x**3, 1 - 3 * x),
                      (r"\dfrac{6x^4+2x^2}{x^2}=6x^2+2", (6 * x**4 + 2 * x**2) / x**2, 6 * x**2 + 2),
                      (r"\dfrac{2x^3-x^4}{x^3}=2-x", (2 * x**3 - x**4) / x**3, 2 - x)):
    present(BLK["C4"], txt, "C4 split")
    report(eq(lhs, rhs), f"C4 split {txt[:30]}")

# C5 part c and C6: meaningless integrals, circle
for blk, s, where in ((CON[5]["demo"], r"\int_{-2}^{1}\frac{1}{x^2}\,dx", "C5 demo c"), (CON[5]["attempt"], r"\int_{-1}^{2}x^{-3}\,dx", "C5 yt c")):
    present(blk, s, where)
    m = re.match(r"\\int_\{(-?\d+)\}\^\{?(-?\d+)\}?(.*)\\,dx", s)
    a, b, f = int(m.group(1)), int(m.group(2)), T(m.group(3))
    sing = [p for p in sp.singularities(f, x) if a <= p <= b]
    report(sing == [0], f"{where}: pole of the integrand inside [{a},{b}]", str(sing))
for r_, area, half in ((4, "16\\pi", "4\\pi"), (7, "49\\pi", "7\\pi")):
    blk = BLK["C6"]
    present(blk, f"\\(2\\pi r=2\\pi\\times4=8\\pi\\)" if r_ == 4 else "\\(2\\pi\\times7=14\\pi\\)", f"C6 r={r_} circumference")
    report(blk.count(f"={area}") >= 2 and eq(T(area), sp.pi * r_**2) and eq(T(half), sp.pi * r_), f"C6 r={r_}: length {half}, area {area}")
for r_, demo in ((4, CON[6]["demo"]), (7, CON[6]["attempt"])):
    present(demo, f"A circle has radius {r_}.", f"C6 radius {r_}")

# ---------------------------------------------------------------- worked examples (textbook Examples 2-6)
WE = {1: ({"a": 4, "b": 6}), 2: ({"a": R(5, 3), "b": R(236, 3)}), 3: ({"a": R(535, 6), "b": 36}),
      4: ({"a": 5, "b": 6}), 5: ({"a": R(4, 5), "b": R(7, 24)})}
for c in range(1, 6):
    w = CON[c]["worked"]
    q = items(w.split('<div class="sol-label">')[0], f"WE{c}")
    sol = w.split('<div class="sol-label">')[1]
    report(sorted(q) == ["a", "b"], f"WE{c} parts a, b")
    for lab, (a, b, f, s) in q.items():
        v = value(a, b, f)
        report(eq(v, WE[c][lab]), f"WE{c}{lab} {s[:40]} = textbook value", f"{v}")
        # the chain whose first member is this integral (or the &-led row) inside the solution
        starts = [m.start() for m in re.finditer(r"\\begin\{aligned\}", sol)]
        found = False
        for st in starts:
            seg = sol[st:sol.index("\\end{aligned}", st)]
            head = seg[len("\\begin{aligned}"):].split("&", 1)[0].strip()
            if head == "":
                head = seg[len("\\begin{aligned}&"):].split("\\\\", 1)[0].strip()
            try:
                A, B, Fx = parse_int(head, "WE")
            except Exception:
                continue
            if eq(A, a) and eq(B, b) and eq(sp.simplify(Fx - f), 0):
                check_chain(sol[st:], "\\begin{aligned}", f"WE{c}{lab}", a, b, f, minimum=4, first=True)
                found = True
                break
        report(found, f"WE{c}{lab} working chain found")
# 'Steps the book skips' tips after the worked examples: every member of each printed chain = the value
def tipchk(c, txt, val, label):
    tip = CON[c]["worked"].split('<div class="box tip"')[1] if '<div class="box tip"' in CON[c]["worked"] else ""
    present(tip, txt, f"WE{c} tip {label}")
    mem = [m_.replace("\\Big", "").replace("\\big", "") for m_ in split_top(txt, "=")]
    try:
        report(all(eq(T(m_), val) for m_ in mem), f"WE{c} tip {label}: every member = {val}", txt[:80])
    except Exception as err:
        report(False, f"WE{c} tip {label}", f"ERROR {err}")


for c, txt, val, lab in (
        (1, r"2^2-0^2=4-0=4", 4, "a"), (1, r"2-0=2", 2, "a base"), (1, r"2\times2=4", 4, "a height"),
        (1, r"\big(4^2-3\times4\big)-\big(2^2-3\times2\big)=(16-12)-(4-6)=6", 6, "b"),
        (1, r"4-2=2", 2, "b width"), (1, r"2\times2-3=1", 1, "b side"), (1, r"2\times4-3=5", 5, "b side"),
        (1, r"\dfrac{1+5}{2}\times2=3\times2=6", 6, "b area"),
        (2, r"\tfrac53\times1^3-\tfrac53\times0^3=\tfrac53-0=\tfrac53", R(5, 3), "a"),
        (2, r"\big(25\times4-\tfrac13\times4^3\big)-\big(25\times0-\tfrac13\times0^3\big)=\big(100-\tfrac13\times64\big)-(0-0)", R(236, 3), "b"),
        (2, r"100-\tfrac{64}{3}=\tfrac{300}{3}-\tfrac{64}{3}=\tfrac{236}{3}=78\tfrac23", R(236, 3), "b arithmetic"),
        (3, r"\dfrac{216}{3}+\dfrac{36}{2}=72+18", 90, "a value at 6"),
        (3, r"\dfrac13+\dfrac12=\dfrac26+\dfrac36=\dfrac56", R(5, 6), "a value at 1"),
        (3, r"\Big(\dfrac{216}{3}+\dfrac{36}{2}\Big)-\Big(\dfrac13+\dfrac12\Big)=(72+18)-\Big(\dfrac26+\dfrac36\Big)=90-\tfrac56=89\tfrac16", R(535, 6), "a"),
        (3, r"\dfrac{27}{3}-5\times9+24\times3=9-45+72", 36, "b value at 3"),
        (4, r"\big(-2-(-2)^2\big)-\big(-3-(-3)^2\big)=(-2-4)-(-3-9)=6", 6, "b"),
        (5, r"-\dfrac15-\Big(-\dfrac11\Big)=-\dfrac15-(-1)=\dfrac45", R(4, 5), "a"),
        (5, r"-\dfrac{1}{3\times8}-\Big(-\dfrac{1}{3\times1}\Big)=-\dfrac{1}{24}-\Big(-\dfrac13\Big)=-\dfrac{1}{24}+\dfrac{8}{24}=\dfrac{7}{24}", R(7, 24), "b")):
    tipchk(c, txt, val, lab)
present(CON[1]["worked"], r"\(\dfrac{d}{dx}x^2=2x\)", "WE1 tip derivative")
for c, txt, l_, r_ in ((4, r"\dfrac{3x^4}{x^2}=3x^2", 3 * x**4 / x**2, 3 * x**2), (4, r"\dfrac{2x^2}{x^2}=2", 2 * x**2 / x**2, 2),
                       (4, r"\dfrac{x^3}{x^3}=1", x**3 / x**3, 1), (4, r"\dfrac{2x^4}{x^3}=2x", 2 * x**4 / x**3, 2 * x)):
    present(CON[c]["worked"], txt, f"WE{c} tip split")
    report(eq(l_, r_), f"WE{c} tip split {txt[:30]}")
# WE1 area checks
w1 = CON[1]["worked"]
for marker, val in ((r"\text{area of triangle}", 4), (r"\text{area of trapezium}", 6)):
    rows = aligned_rows(w1, marker, "WE1 areas")
    mem = [m.strip().rstrip(".") for r in rows for m in split_top(r.replace("&", ""), "=") if m.strip() and "\\text" not in m]
    report(rows[0].startswith(marker), f"WE1 {marker[6:]} rows found")
    report(len(mem) >= 2 and all(eq(T(m), val) for m in mem), f"WE1 {marker[6:]} = {val}", str(mem))
present(w1, r"parallel sides \(2\times2-3=1\) and \(2\times4-3=5\)", "WE1 trapezium sides")
# Concept 2 box examples
c2 = teach.split("<!-- ============ Concept 2 ============ -->")[1].split("<!-- ============")[0]
present(c2, r"\((16-12)-(4-6)=4-(-2)=6\)", "C2 brackets example")
report(eq(16 - 12 - 4 - 6, -6) and eq((16 - 12) - (4 - 6), 6), "C2 brackets example values (6 and the wrong -6)")
(g,) = grab(c2, r"\[\Big[\tfrac13(x+1)^3\Big]_0^1=@,\]", "C2 zero example")
mem = split_top(g, "=")
report(all(eq(T(m), sp.integrate((x + 1)**2, (x, 0, 1))) for m in mem) and eq(sp.diff((x + 1)**3 / 3, x), (x + 1)**2),
       "C2 zero example: every member = integral of (x+1)^2 on [0,1]", g)
present(c2, r"\((-2)^2=4\), \((-2)^3=-8\), \((-1)^4=1\)", "C2 powers")
report(((-2)**2, (-2)**3, (-1)**4) == (4, -8, 1) and R(2, 3)**3 == R(8, 27), "C2 powers values")
# Concept 5 warning chain
c5 = teach.split("<!-- ============ Concept 5 ============ -->")[1].split("<!-- ============")[0]
rows = aligned_rows(c5, r"\int_{-1}^{1}x^{-4}\,dx", "C5 warning")
mem = [m.strip().rstrip(".") for r in rows[1:] for m in split_top(r.replace("&", ""), "=") if m.strip()]
Fw = x**-3 / -3
report(all(eq(T(m), Fw.subs(x, 1) - Fw.subs(x, -1)) for m in mem) and eq(Fw.subs(x, 1) - Fw.subs(x, -1), R(-2, 3)),
       "C5 warning: the (invalid) bracket arithmetic gives -2/3", str(mem))
report(list(sp.singularities(x**-4, x)) == [0], "C5 warning: x^-4 has its asymptote at 0")
(g,) = grab(c5, r"gives \(@\).</p></div>", "C5 warning tip")
mem = [m_.replace("\\Big", "") for m_ in split_top(g, "=")]
report(all(eq(T(m_), R(-2, 3)) for m_ in mem), "C5 warning tip: every member = -2/3", g[:80])
c6 = teach.split("<!-- ============ Concept 6 ============ -->")[1]
present(c6, r"\(\text{length}\times\text{height}=\pi r\times r=\pi r^2.\)", "C6 tip rectangle area")
present(c5, r"\frac{x^{-3}}{-3}=-\frac{1}{3x^3}", "C5 conversion")
report(eq(x**-3 / -3, -1 / (3 * x**3)), "C5 conversion value")

# ---------------------------------------------------------------- textbook homework
TB = {  # textbook key (PDF 889)
    "1": {"a": 1, "b": 15, "c": 16, "d": 84, "e": 19, "f": 243, "g": 62, "h": 2, "i": 1},
    "3": {"a": 30, "b": 6, "c": 33, "d": 18, "e": 132, "f": 2, "g": 23, "h": 44, "i": 60},
    "4": {"a": 2, "b": 2, "c": 9, "d": 30, "e": 96, "f": 10},
    "5": {"a": R(27, 2), "b": R(14, 3), "c": R(117, 4), "d": 2, "e": R(125, 6), "f": 98},
    "6": {"a": 24, "b": 18, "c": R(8, 3), "d": 21, "e": R(1, 4), "f": R(8, 15)},
    "7": {"a": 42, "b": 14, "c": 62, "d": R(25, 3), "e": R(20, 3), "f": 6},
    "8": {"a": R(1, 24), "b": R(20, 27), "c": R(7, 8)},
    "13": {"a": R(3, 2), "b": R(5, 8), "c": R(127, 3)},
    "14": {"a": R(40, 3), "b": R(1019, 120), "c": R(1, 24)},
}
TBR = {"2": {"i": 4, "ii": 25, "iii": 1}, "9a": {"i": R(1, 10), "ii": R(5, 36), "iii": 15}, "9b": {"i": R(1, 2), "ii": R(15, 32), "iii": 7}}
NPARTS = {"1": 9, "3": 9, "4": 6, "5": 6, "6": 6, "7": 6, "8": 3, "13": 3, "14": 3}


def printed_letter_answers(blk):
    bits = re.split(r"<b>([a-i])</b>", blk)
    out = {}
    for i in range(1, len(bits), 2):
        txt = re.sub(r"&nbsp;|<[^>]+>", " ", bits[i + 1]).strip()
        mm = re.findall(r"\\\((.*?)\\\)", txt)
        out[bits[i]] = mm[0] if mm else txt.split()[0]
    return out


for qn, tb in TB.items():
    q = items(TQ[qn], f"Q{qn}")
    report(len(q) == NPARTS[qn] == len(tb), f"Q{qn} parts read", f"{len(q)}")
    pa = printed_letter_answers(BLK[qn])
    for p, tv in tb.items():
        try:
            a, b, f, s = q[p]
            v = value(a, b, f)
            got = T(pa[p])
            report(eq(got, v) and eq(v, tv), f"Q{qn}{p} {s[:40]}", f"printed {pa[p]} ; sympy {v} ; textbook {tv}")
        except Exception as err:
            report(False, f"Q{qn}{p}", f"ERROR {err}")


def roman_items(block):
    out = {}
    for lab, s in re.findall(r'<span class="pl">(i{1,3})</span>\\\((\\displaystyle\\int.*?)\\\)', block, re.S):
        out[lab] = parse_int(s, "roman")
    return out


def roman_answers(blk):
    out = {}
    for lab, s in re.findall(r"\((i{1,3}|iv)\)\s*(\\\(.*?\\\)|\d+)", blk):
        out[lab] = s[2:-2] if s.startswith("\\(") else s
    return out


q2 = roman_items(TQ["2"])
a2 = roman_answers(BLK["2"].split("<b>b</b>")[0])
for p, tv in TBR["2"].items():
    a, b, f = q2[p]
    report(eq(value(a, b, f), tv) and eq(T(a2[p]), tv), f"Q2a({p})", f"printed {a2[p]}, sympy {value(a, b, f)}")
q9a = roman_items(TQ["9"].split('<span class="pl">b</span>')[0])
q9b = roman_items(TQ["9"].split('<span class="pl">b</span>')[1])
a9a = roman_answers(BLK["9"].split("<b>b</b>")[0])
a9b = roman_answers(BLK["9"].split("<b>b</b>")[1])
for qq, aa, key, nm in ((q9a, a9a, TBR["9a"], "Q9a"), (q9b, a9b, TBR["9b"], "Q9b")):
    for p, tv in key.items():
        a, b, f = qq[p]
        report(eq(value(a, b, f), tv) and eq(T(aa[p]), tv), f"{nm}({p})", f"printed {aa[p]}, sympy {value(a, b, f)}")

# Q10: k from the stems
s10 = TQ["10"]
(i1,) = grab(s10, r"Show that \(\displaystyle@=3k-6\)", "Q10a(i)")
a, b, f = parse_int(i1.replace("^k", "^{k}"), "Q10a")
report(eq(sp.integrate(f, (x, a, b)), 3 * k - 6), "Q10a(i) integral = 3k - 6")
sol = sp.solve(sp.Eq(sp.integrate(f, (x, a, b)), 18), k)
report(sol == [8] and "<b>a</b> (ii) \\(k=8\\)" in BLK["10"], "Q10a(ii) k = 8", str(sol))
(i2,) = grab(s10, r"Show that \(\displaystyle@=\tfrac12k^2\)", "Q10b(i)")
a, b, f = parse_int(i2, "Q10b")
report(eq(sp.integrate(f, (x, a, b)), k**2 / 2), "Q10b(i) integral = k^2/2")
sol = sp.solve(sp.Eq(sp.integrate(f, (x, a, b)), 18), k)
report(sol == [6] and "<b>b</b> (ii) \\(k=6\\)" in BLK["10"], "Q10b(ii) k = 6 (positive)", str(sol))

# Q11
K11 = {"a": 1, "b": 4, "c": 8, "d": 3, "e": 3, "f": 2}
a11 = dict(re.findall(r"<b>([a-f])</b> \\\(k=(\d+)\\\)", BLK["11"]))
for lab, s in re.findall(r'<span class="pl">([a-f])</span>\\\((\\displaystyle\\int.*?)\\\)', TQ["11"], re.S):
    lhs, rhs = s.rsplit("=", 1)
    a, b, f = parse_int(lhs, "Q11")
    sol = [r_ for r_ in sp.solve(sp.Eq(sp.integrate(f, (x, a, b)), T(rhs)), k) if r_.is_positive]
    report(sol == [K11[lab]] and int(a11.get(lab, -1)) == K11[lab], f"Q11{lab} k = {K11[lab]}", f"{s[:50]} -> {sol}; printed {a11.get(lab)}")

# Q12: the sketches (quadrants of radius 1, lines), integral by sympy
import mpmath  # noqa: E402
f12a = lambda v: mpmath.sqrt(max(0, 1 - (v - 1)**2)) if v <= 1 else (2 - v if v <= 2 else (v - 2 if v <= 3 else mpmath.sqrt(max(0, 1 - (v - 3)**2))))  # noqa: E731
f12b = lambda v: 1 - mpmath.sqrt(max(0, 1 - v**2)) if v <= 1 else (1 if v <= 2 else (3 - v if v <= 3 else mpmath.sqrt(max(0, 1 - (v - 4)**2))))  # noqa: E731
v12a = sp.nsimplify(sp.integrate(sp.sqrt(1 - x**2), (x, -1, 0)) + sp.integrate(2 - x, (x, 1, 2)) + sp.integrate(x - 2, (x, 2, 3))
                    + sp.integrate(sp.sqrt(1 - x**2), (x, 0, 1)))
v12b = sp.nsimplify(sp.integrate(1 - sp.sqrt(1 - x**2), (x, 0, 1)) + 1 + sp.integrate(3 - x, (x, 2, 3)) + sp.integrate(sp.sqrt(1 - x**2), (x, -1, 0)))
pa = printed_letter_answers(BLK["12"])
report(eq(T(pa["a"]), v12a) and eq(v12a, 1 + sp.pi / 2), "Q12a", f"printed {pa['a']}, sympy {v12a}")
report(eq(T(pa["b"]), v12b) and eq(v12b, R(5, 2)), "Q12b", f"printed {pa['b']}, sympy {v12b}")
for nm, fn, vv in (("a", f12a, v12a), ("b", f12b, v12b)):
    q = mpmath.quad(fn, [0, 1, 2, 3, 4])
    report(abs(q - float(vv)) < 1e-9, f"Q12{nm} numeric quadrature of the sketched f", f"{q}")

# Q15c: which integrals cross the asymptote x = 3
mean = []
for lab, s in re.findall(r'<span class="pl">(i{1,3})</span>\\\((\\displaystyle\\int.*?)\\\)', TQ["15"], re.S):
    a, b, f = parse_int(s, "Q15")
    if [p for p in sp.singularities(f, x) if a < p < b]:
        mean.append(lab)
report(mean == ["ii"] and "Part (ii) is meaningless" in BLK["15"], "Q15c: only (ii) crosses x = 3", str(mean))
report(list(sp.singularities(x**-2, x)) == [0] and "asymptote \\(x=0\\)" in BLK["15"] and BLK["C5"].count("asymptote at \\(x=0\\)") == 2, "Q15b and C5c: asymptote x = 0")

# Q16 differential form
a_ = sp.Symbol("a", positive=True)
A16 = {"i": x**2, "ii": x**3 + 3 * x, "iii": 1 / x, "iv": (x**3 - 3)**4}
I16 = {"i": sp.integrate(t**2, (t, 1, x)), "ii": sp.integrate(t**3 + 3 * t, (t, 2, x)),
       "iii": sp.Integral(1 / t, (t, a_, x)), "iv": sp.Integral((t**3 - 3)**4, (t, a_, x))}
a16 = roman_answers(BLK["16"])
for p, tv in A16.items():
    d = sp.diff(I16[p], x)
    report(eq(d, tv) and eq(T(a16[p]), tv), f"Q16a({p})", f"printed {a16[p]}, d/dx = {d}")

# answers present only for items with a final answer
report(sorted((k_ for k_ in BLK if not k_.startswith("C")), key=int) == [str(i) for i in range(1, 17)],
       "textbook answers Q1-16 (show-that parts omitted inside Q10, Q16b)")
report("(i)" not in BLK["10"] and "V'(x)" not in les + ans, "Q10(i) not answered; Q17 absent from both files")

# ---------------------------------------------------------------- past paper
PPQ = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span><span class="mk">(\d+) marks?</span></div>(.*?)(?=<div class="pp">|$)', ppl, re.S)
PPA = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span></div>(.*?)(?=<div class="ppa">|$)', ans, re.S)
report(len(PPQ) == 1 and len(PPA) == 1, "one past-paper question, one solution")
num, lab, mk, body = PPQ[0]
clean = re.sub(r"\s+", " ", re.sub("<[^>]+>|&nbsp;", " ", lab)).replace(" ,", ",").strip()
report(lab == PPA[0][1] and clean == "North Sydney Boys High School, 2022, HSC Course Assessment Task 3-Trial Examination, Mathematics Extension 1, Q10",
       "PP1 source label (both files, as printed on the cover)", clean)
tot = re.search(r"<span><b>(\d+) marks?</b></span>", ppl).group(1)
(tm,) = grab(ppl, "<b>Suggested time: @ minutes</b>", "pp intro")
report(int(tot) == int(mk) == 1, "PP marks total 1")
report(int(tm) == max(5, 5 * math.ceil(1.5 * int(tot) / 5)), "PP time 1.5 x marks rounded to 5 min (min 5)", tm)
report(body.count('class="hint"') == 1, "PP1 one hint")
hint = re.search(r'<div class="hint"><b>Hint:</b>(.*?)</div>', body, re.S).group(1)
METHOD = ("integrat", "primitive", "substitut", "fundamental", "theorem", "area", "expand", "symmetr", "line",
          "gradient", "equation", "between", "limit", "square", "x^2", "x^")
report(not re.search(r"\d", hint) and not any(w in hint.lower() for w in METHOD) and hint.strip().endswith("?"),
       "PP1 hint is a neutral starting question (no numbers, no method words)", hint.strip())
present(ppl, "For more timed practice, do Questions 4(f), 6(f), 7(f), 11(f), 13(c) and 14(b) above in 25 minutes.", "timed-practice note")
present(body, r"\int_{-1}^{1}f(x^2-1)\,dx", "PP1 stem integral")
present(body, "{{svg:p5b_nsb}}", "PP1 graph")
fg = sp.Max(0, 1 - sp.Abs(x))                     # the printed graph: peak (0, 1), zero for |x| >= 1
u = sp.Symbol("u", real=True)
comp = sp.Piecewise((0, x**2 - 1 <= -1), (x**2 - 1 + 1, x**2 - 1 <= 0), (1 - (x**2 - 1), x**2 - 1 <= 1), (0, True))
val = sp.integrate(comp, (x, -1, 1))
report(eq(val, R(2, 3)) and eq(sp.integrate(fg.subs(x, x**2 - 1).rewrite(sp.Piecewise), (x, -1, 1)), val),
       "PP1 value of the integral from the graph = 2/3", str(val))
opts = {}
for l_, s in re.findall(r"<span>([A-D])\.&ensp;\\\((.*?)\\\)</span>", body):
    opts[l_] = T(s)
report(sorted(opts) == list("ABCD") and [l_ for l_, v in opts.items() if eq(v, val)] == ["D"], "PP1 MC: only D equals the integral", str(opts))
sol = PPA[0][2]
present(sol, "<b>Answer D.</b>", "PP1 answer letter")
rows = aligned_rows(sol, r"\begin{aligned}\int_{-1}^{1}f(x^2-1)\,dx", "PP1 solution")
memb = [m.strip().rstrip(".") for r in rows for m in split_top(r.replace("&", ""), "=") if m.strip()][1:]
okm = True
for m in memb:
    if "\\int" in m:
        a, b, f = parse_int(m, "PP1")
        okm &= eq(value(a, b, f), val)
    elif "\\Big[" in m:
        okm &= bracket_ok(m, "PP1", x**2, -1, 1, val)
    else:
        okm &= eq(T(m), val)
report(okm and len(memb) >= 3, "PP1 solution chain", str(memb))
present(sol, r"\[f(x^2-1)=(x^2-1)+1=x^2\quad\text{for }-1\le x\le1.\]", "PP1 composite")
report(all(eq(comp.subs(x, xv), xv**2) for xv in (R(-1), R(-1, 2), R(0), R(1, 3), R(1))), "PP1 f(x^2-1) = x^2 on [-1, 1]")
report(eq(opts["B"], sp.integrate(x**2, (x, 0, 1))), "PP1 distractor note (B is the integral from 0 to 1)")

# ---------------------------------------------------------------- figures referenced exist
for name in set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans)):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}.svg exists")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:40], sep="\n  ")
    sys.exit(1)
print("ALL OK")
