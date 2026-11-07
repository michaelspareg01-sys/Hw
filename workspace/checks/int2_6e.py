"""Check of Lesson 6E (Integration Part 2 pack): Applications of integration (areas with e^x).

The script reads the values PRINTED in workspace/build/int2/l6e.html (tutor demos, your-turn items,
worked examples 17 and 18, the integrating-with-respect-to-y tip, Exercise 6E, the past-paper mini
exam) and in a_6e.html (lesson-example answers, textbook answers, past-paper worked solutions).
Printed LaTeX is turned into sympy with the shared helper int3_tex.py and every result is recomputed
independently:
  - every printed chain 'A = B = C' that starts with an integral or [F]_a^b (inline or aligned, in x
    or in y) is checked line by line: definite integrals with sympy.integrate, brackets by
    substitution, plain arithmetic by simplification;
  - each region of the lesson and the exercise is set up here from its description (curves, lines,
    limits) and its area is found with sympy (and, for the past papers, also numerically by a
    second route); the printed answer must match, and the question text must contain the curve and
    limits used;
  - decimals are compared with the exact values rounded as asked; the trapezoidal estimate is
    recomputed; limits use sympy.limit; derivatives use sympy.diff.
It also checks the structure (questions 1-17, bands F 1-6, D 7-15, E 16-17, Q12(b) omitted), the
past-paper block (marks, time = 1.5 x marks rounded to 5 min, one hint per question, labels the same
in both files, the timed-practice note) and that every {{svg:...}} exists. A template must match
exactly once; a missing template FAILS.

Exit status 1 if anything fails. Run: python3 workspace/checks/int2_6e.py
"""
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

SRC = os.environ.get("INT2_SRC", os.path.join(HERE, "..", "build", "int2"))
x = T.x
y = sp.Symbol("y", real=True)
N, delta = sp.symbols("N delta", positive=True)
E = sp.E
EXTRA = {"N": N, "delta": delta, "C": sp.Integer(0)}
FAILS, CNT = [], [0]


def report(ok, label, detail=""):
    CNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- TeX -> sympy
def prep(t_):
    t_ = t_.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "")
    t_ = t_.replace("\\qquad\\text{(the number }e\\text{ is a constant)}", "")
    t_ = re.sub(r"\\text\{[^{}]*\}", "", t_)
    t_ = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", t_)
    # mixed numbers: 3\tfrac23 -> (3+\tfrac23)
    t_ = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\\tfrac{\2}{\3})", t_)
    t_ = t_.replace("\\,", " ").replace("\\ ", " ")
    return t_.strip().rstrip(".,").strip()


def tex(t_, extra=None):
    loc = dict(EXTRA)
    if extra:
        loc.update(extra)
    return T.tex(prep(t_), loc)


LIM = r"(\{(?:[^{}]|\{[^{}]*\})*\}|-?\w)"


def unbrace(g):
    return g[1:-1] if g.startswith("{") else g


def side(t_):
    """One side of a chain -> sympy, with integrals and [F]_a^b brackets replaced by values."""
    t_ = prep(t_)
    extra, n = {}, [0]

    def ph(val):
        name = f"Z{n[0]}Z"
        n[0] += 1
        extra[name] = val
        return " " + name + " "

    def brk(mt):
        F = tex(mt.group(1))
        return "(" + ph(F.subs(x, tex(unbrace(mt.group(3)))) - F.subs(x, tex(unbrace(mt.group(2))))) + ")"

    t_ = re.sub(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, brk, t_)

    def itg(mt):
        g = tex(mt.group(3))
        if mt.group(1):
            return "(" + ph(sp.integrate(g, (x, tex(unbrace(mt.group(1))), tex(unbrace(mt.group(2)))))) + ")"
        return "(" + ph(sp.Integral(g, x)) + ")"

    t_ = re.sub(r"\\int(?:_" + LIM + r"\^" + LIM + r")?(.*?)\s*dx", itg, t_)
    for name in extra:
        T.LOCAL.setdefault(name, sp.Symbol(name))
    return tex(t_, extra)


def same(a, b):
    return sp.simplify(sp.expand(a - b)) == 0


def to_x(seg):
    """An integral in y: rename the variable y to x (the regions are set up independently below)."""
    return seg.replace("dy", "dx").replace("e^y", "e^x").replace("ey", "ex").replace("y", "x")


def chain(text, label):
    t0 = to_x(text) if "dy" in text else text
    sides = [q_ for q_ in T.split_top(prep(t0).replace("\\\\", " "), "=") if q_.strip()]
    try:
        vals = [side(q_) for q_ in sides]
    except Exception as err:  # noqa: BLE001
        report(False, label, f"ERROR {err} in {text[:80]!r}")
        return None
    ok = all(same(vals[0], v) for v in vals[1:])
    report(ok and len(vals) >= 2, label, f"{len(vals)} sides: " + " | ".join(sides)[:150])
    return vals[-1]


def math_segments(html):
    return re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", html, re.S)


def aligned_chain(body):
    body = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", body)
    lines = [ln.replace("&amp;", "").replace("\\quad", "").strip() for ln in body.split("\\\\")]
    return "".join(lines)


def all_chains(html, where):
    cnt = 0
    for inl, disp in math_segments(html):
        seg = inl or disp
        if not ("\\int_" in seg or "\\Big[" in seg) or "=" not in seg:
            continue
        if "aligned" in seg:
            seg = aligned_chain(seg)
        if "f(x)" in seg or "N" in seg or "\\infty" in seg or "\\delta" in seg:
            continue  # the formula box and the limit items (checked separately)
        seg = seg.replace("\\text{area}", "")
        if seg.strip().startswith("=") and seg.count("=") == 1:
            continue  # a statement 'area = A - B' (its value is checked with the past papers)
        cnt += 1
        chain(seg, f"{where} chain {cnt}")
    return cnt


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        raise LookupError(f"{where}: pattern matched {len(found)} times: {pattern[:70]!r}")
    return found[0]


def area_between(top, bottom, a, b, var=x):
    return sp.integrate(top - bottom, (var, a, b))


# ---------------------------------------------------------------- files and blocks
les, ans = read("l6e.html"), read("a_6e.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1]
CON = {}
for c in (1, 2):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    blocks = re.findall(r'<div class="ex (demo|attempt|worked)"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<div class="box|$)', seg, re.S)
    CON[c] = {"worked": []}
    for kind, tag, body in blocks:
        if kind == "worked":
            CON[c]["worked"].append((tag, body))
        else:
            CON[c][kind] = body
    CON[c]["all"] = seg
report([[t_ for t_, _ in CON[c]["worked"]] for c in (1, 2)] == [["Worked example 17"], ["Worked example 18"]],
       "worked examples", "textbook Examples 17 and 18 in Concepts 1 and 2")
report(all("demo" in CON[c] and "attempt" in CON[c] for c in (1, 2)), "every concept has a tutor demo and a your turn")

parts_ans = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
report(len(parts_ans) == 2 and ans.count("{{ahead:Lesson 6E | Applications of integration}}") == 2, "answers headings and sections")
BLK = dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts_ans[0], re.S))
PPA = parts_ans[1]

# every figure exists
for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}")

# ---------------------------------------------------------------- generic chains everywhere
n1 = all_chains(teach, "lesson teaching")
n2 = all_chains(ans, "answers")
report(n1 >= 3 and n2 >= 10, "chains found", f"lesson {n1}, answers {n2}")


def last_display_value(block, i):
    disp = re.findall(r"\\\[(.*?)\\\]", block, re.S)
    seg = aligned_chain(disp[i]).replace("\\text{area}", "")
    seg = to_x(seg) if "dy" in seg else seg
    return side(T.split_top(prep(seg), "=")[-1]), seg


# ---------------------------------------------------------------- Concept 1: demo, your turn, WE17
def halves(block):
    a_, b_ = block.split("<b>Your turn.</b>")
    return a_, b_


for who, qb, ab in (("demo", CON[1]["demo"], halves(BLK["C1"])[0]), ("your turn", CON[1]["attempt"], halves(BLK["C1"])[1])):
    try:
        k = int(grab(qb, r"sketch \\\(y=e\^x-e\^(\d)\\\)", f"C1 {who} curve"))
        f = sp.exp(x) - E ** k
        yi = grab(ab, r"When \\\(x=0\\\), \\\(\\ y=(.*?)\\\)\.", f"C1 {who} y-int")
        vals = [tex(z) for z in T.split_top(prep(yi), "=")]
        report(all(same(v, f.subs(x, 0)) for v in vals), f"C1 {who} y-intercept", yi)
        xi = tex(grab(ab, r"so \\\(x=(.*?)\\\)\.", f"C1 {who} x-int"))
        report(same(f.subs(x, xi), 0) and len(sp.solve(sp.Eq(f, 0), x)) == 1, f"C1 {who} x-intercept", str(xi))
        asy = tex(grab(ab, r"moves down to \\\(y=(.*?)\\\)\.", f"C1 {who} asymptote"))
        report(same(asy, sp.limit(f, x, -sp.oo)), f"C1 {who} asymptote", str(asy))
        val, seg = last_display_value(ab, 0)
        exact = sp.integrate(f, (x, 0, xi))
        report(same(val, exact) and "\\int_0^" + str(k) + "(e^x-e^" + str(k) + ")" in seg.replace(" ", ""), f"C1 {who} integral", f"{seg[:60]} = {val}")
        area = tex(grab(ab, r"Hence the area is \\\((.*?)\\\) square units", f"C1 {who} area"))
        report(exact < 0 and same(area, -exact) and same(area, area_between(0, f, 0, xi)), f"C1 {who} area", str(area))
    except Exception as err:  # noqa: BLE001
        report(False, f"C1 {who}", f"ERROR {err}")

try:
    b17 = CON[1]["worked"][0][1]
    v, seg = last_display_value(b17, 0)
    report(same(v, sp.integrate(sp.exp(x) - E, (x, 0, 1))) and same(v, -1), "WE17 b integral", str(v))
    report("Hence the required area is \\(1\\) square unit" in b17, "WE17 area 1")
    report("\\(\\phantom{y}=1-e.\\)" in b17 and "\\(\\phantom{e^x}x=1.\\)" in b17 and "\\(y=-e\\)" in b17, "WE17 a intercepts and asymptote printed")
    note = grab(b17, r"In the second line, \\\((.*?)\\\) and \\\((.*?)\\\), so the value is \\\((.*?)\\\)\.", "WE17 note")
    report(same(tex(note[0].split("=")[0]), 0) and same(tex(note[1].split("=")[0]), 1)
           and all(same(tex(z), -1) for z in T.split_top(prep(note[2]), "=")[1:]), "WE17 note arithmetic", " ; ".join(note))
except Exception as err:  # noqa: BLE001
    report(False, "WE17", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 2: demo, your turn, WE18, tip
for who, qb, ab in (("demo", CON[2]["demo"], halves(BLK["C2"])[0]), ("your turn", CON[2]["attempt"], halves(BLK["C2"])[1])):
    try:
        b = int(grab(qb, r"from \\\(x=0\\\) to \\\(x=(\d)\\\)", f"C2 {who} limit"))
        L = int(grab(qb, r"interval \\\(-(\d)\\le x\\le", f"C2 {who} interval"))
        report(L == b, f"C2 {who} sketch interval matches", f"[-{L},{L}]")
        # e^x above x^2 for x > 0 (claim in the answer): minimum of e^x - x^2 on [0, b] is positive
        g = sp.exp(x) - x ** 2
        mins = [g.subs(x, t_ / 100) for t_ in range(0, 100 * b + 1)]
        report(min(float(m) for m in mins) > 0, f"C2 {who} e^x above x^2 on [0,{b}]")
        val, seg = last_display_value(ab, 0)
        report(same(val, sp.integrate(g, (x, 0, b))), f"C2 {who} area", f"{seg[:50]} ... = {val}")
    except Exception as err:  # noqa: BLE001
        report(False, f"C2 {who}", f"ERROR {err}")
try:
    approx = grab(BLK["C2"], r"\\\(e\^3\\doteq([\d.]+)\\\)", "C2 e^3")
    report(approx == f"{float(sp.exp(3)):.1f}", "C2 e^3 decimal", approx)
    b18 = CON[2]["worked"][0][1]
    v, _ = last_display_value(b18, 0)
    report(same(v, sp.integrate(sp.exp(x) - x ** 2, (x, 0, 2))), "WE18 area e^2 - 3 2/3", str(v))
    note = grab(b18, r"In the third line, \\\((.*?)\\\) and \\\((.*?)\\\), so the value is \\\((.*?)\\\)\.", "WE18 note")
    report(same(tex(note[0].split("=")[0]), tex(note[0].split("=")[1])) and same(tex(note[1].split("=")[1]), 1)
           and all(same(tex(z), v) for z in T.split_top(prep(note[2]), "=")), "WE18 note arithmetic", " ; ".join(note))
    tip = teach.split("Integrating with respect to \\(y\\)")[1]
    v, seg = last_display_value(tip, 0)
    report(same(v, sp.integrate(sp.exp(y), (y, 0, 1))) and same(v, sp.integrate(1 - sp.log(x), (x, 1, E)) + 1), "tip: area by y = e - 1 (and by x)", str(v))
except Exception as err:  # noqa: BLE001
    report(False, "Concept 2 extras", f"ERROR {err}")

# ---------------------------------------------------------------- textbook homework
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 18)], "textbook questions 1-17", str(sorted(TQ, key=int)))
bands = hw.split("{{band:D}}")
report(bands[0].count('class="q-num"') == 6 and bands[1].split("{{band:E}}")[0].count('class="q-num"') == 9
       and bands[1].split("{{band:E}}")[1].count('class="q-num"') == 2, "bands", "F: Q1-6, D: Q7-15, E: Q16-17 (as the textbook)")
report("8-2^x" not in hw and "2^x" not in hw and '<span class="pl">' not in TQ["12"], "Q12(b) omitted (needs 6K)")
report(set(BLK) == {"C1", "C2"} | {str(i) for i in range(1, 18)}, "answer blocks", "C1, C2 and Q1-17")


def aparts(n):
    return dict(re.findall(r'<span class="ap6e"><b>(\w+)</b> (.*?)</span>', BLK[n], re.S))


def first(t_):
    return re.findall(r"\\\((.*?)\\\)", t_, re.S)


def has(n, *snips):
    body = TQ[n].replace(" ", "")
    miss = [s_ for s_ in snips if s_.replace(" ", "") not in body]
    report(not miss, f"Q{n} question text", "missing " + ", ".join(miss) if miss else ", ".join(snips)[:150])


def exact_and_dec(n, lt, exact, txt, dp=None, sf=None):
    ms = first(txt)
    main = ms[0]
    parts_ = T.split_top(prep(main.replace("\\doteq", "=")), "=")
    ok = same(tex(parts_[0]), exact)
    det = f"{main} vs {sp.nsimplify(exact)}"
    if len(parts_) > 1:
        d = parts_[1].strip()
        if sf:
            want = f"{float(sp.N(exact, 20)):.{sf}g}"
            ok = ok and (float(d) == float(want))
        elif dp is not None:
            ok = ok and d == f"{float(sp.N(exact, 20)):.{dp}f}"
    report(ok, f"Q{n}{lt}", det)


# Q1
has("1", "\\int_0^1e^x", "\\int_{-1}^0e^x", "\\int_{-2}^0e^x", "\\int_{-3}^0e^x", "10 divisions to 1 unit")
an = aparts("1")
for lt, lo in (("i", 0), ("ii", -1), ("iii", -2), ("iv", -3)):
    try:
        hi = 1 if lt == "i" else 0
        lo_ = 0 if lt == "i" else lo
        exact_and_dec("1a", lt, sp.integrate(sp.exp(x), (x, lo_, hi)), an[lt], dp=2)
    except Exception as err:  # noqa: BLE001
        report(False, f"Q1a{lt}", f"ERROR {err}")
try:
    sq = re.findall(r"About (\d+)(?:, (\d+) and (\d+))? little squares", BLK["1"])
    want = [[round(100 * float(sp.exp(1) - 1))], [round(100 * float(1 - sp.exp(-k))) for k in (1, 2, 3)], [100]]
    got = [[int(z) for z in t_ if z] for t_ in sq]
    report(got == want, "Q1 b-d counted squares (100 x exact value, rounded)", f"{got} vs {want}")
    report(same(sp.integrate(sp.exp(x), (x, -sp.oo, 0)), 1) and "exactly \\(1\\)" in BLK["1"], "Q1d total area exactly 1")
except Exception as err:  # noqa: BLE001
    report(False, "Q1 counting", f"ERROR {err}")

# Q2 (exact and 4 s.f.)
has("2", "y=e^{2x}", "x=0\\) to \\(x=3", "y=e^{-x}", "x=0\\) to \\(x=1", "y=e^{\\frac13x}", "x=-3\\) to \\(x=0")
an = aparts("2")
for lt, f, a_, b_ in (("a", sp.exp(2 * x), 0, 3), ("b", sp.exp(-x), 0, 1), ("c", sp.exp(x / 3), -3, 0)):
    try:
        exact_and_dec(2, lt, sp.integrate(f, (x, a_, b_)), an[lt], sf=4)
    except Exception as err:  # noqa: BLE001
        report(False, f"Q2{lt}", f"ERROR {err}")

# Q3, Q4
has("3", "y=e^{x+3}", "-2\\le x\\le0", "y=e^{2x-1}", "0\\le x\\le1", "y=e^{-2x-1}", "-2\\le x\\le-1", "y=e^{\\frac13x+2}", "0\\le x\\le3")
an = aparts("3")
for lt, f, a_, b_ in (("a", sp.exp(x + 3), -2, 0), ("b", sp.exp(2 * x - 1), 0, 1), ("c", sp.exp(-2 * x - 1), -2, -1), ("d", sp.exp(x / 3 + 2), 0, 3)):
    try:
        exact_and_dec(3, lt, sp.integrate(f, (x, a_, b_)), an[lt])
    except Exception as err:  # noqa: BLE001
        report(False, f"Q3{lt}", f"ERROR {err}")
has("4", "y=e^{\\frac12x}", "x=-1\\) and \\(x=2", "y=e^{-x}", "the line \\(x=1")
an = aparts("4")
for lt, f, a_, b_ in (("a", sp.exp(x / 2), -1, 2), ("b", sp.exp(-x), 0, 1)):
    try:
        exact_and_dec(4, lt, sp.integrate(f, (x, a_, b_)), an[lt])
    except Exception as err:  # noqa: BLE001
        report(False, f"Q4{lt}", f"ERROR {err}")

# Q5 (2 d.p.)
has("5", "y=e^x+e^{-x}", "x=-2\\) to \\(x=2", "y=x^2+e^x", "x=-3\\) to \\(x=3")
an = aparts("5")
for lt, f, a_, b_ in (("a", sp.exp(x) + sp.exp(-x), -2, 2), ("b", x ** 2 + sp.exp(x), -3, 3)):
    try:
        report(min(float(f.subs(x, t_ / 10)) for t_ in range(10 * a_, 10 * b_ + 1)) > 0, f"Q5{lt} curve above the axis")
        exact_and_dec(5, lt, sp.integrate(f, (x, a_, b_)), an[lt], dp=2)
    except Exception as err:  # noqa: BLE001
        report(False, f"Q5{lt}", f"ERROR {err}")

# Q6: regions set up from the descriptions
has("6", "y=e^{-x}\\) and the lines \\(x=2\\) and \\(y=1", "y=e-e^x", "y=e^x-1\\) and the line \\(x=-1", "x=2\\), \\(y=e^{-x}-2",
    "y=e^{-x}-e\\) and the coordinate axes", "y=3-e^{-x}\\), the \\(x\\)-axis, and the lines \\(x=-1\\) and \\(x=2")
an = aparts("6")
R6 = {
    "a": area_between(1, sp.exp(-x), 0, 2),                    # between y = 1 (top) and y = e^{-x}, x = 0 .. 2
    "b": area_between(E - sp.exp(x), 0, 0, sp.solve(E - sp.exp(x), x)[0]),
    "c": area_between(0, sp.exp(x) - 1, -1, 0),                # below the axis
    "d": area_between(0, sp.exp(-x) - 2, 0, 2),
    "e": area_between(0, sp.exp(-x) - E, sp.solve(sp.exp(-x) - E, x)[0], 0),
    "f": area_between(3 - sp.exp(-x), 0, -1, 2),
}
report(float((3 - sp.exp(-x)).subs(x, -1)) > 0 and float((sp.exp(-x) - 2).subs(x, 0)) < 0, "Q6 sign checks (f above, d below the axis)")
for lt in "abcdef":
    try:
        exact_and_dec(6, lt, R6[lt], an[lt])
    except Exception as err:  # noqa: BLE001
        report(False, f"Q6{lt}", f"ERROR {err}")

# Q7: printed integral and value
has("7", "y=e^x\\) and \\(y=x+1", "y=e^x\\) and \\(y=1-x", "x=0\\) to \\(x=1")
for lt, line in (("a", x + 1), ("b", 1 - x)):
    try:
        seg = grab(BLK["7"], rf"<b>{lt}</b> \\\((\\displaystyle\\int_0\^1.*?)\\\) u", f"Q7{lt}")
        l_, r_ = T.split_top(prep(seg), "=")
        g = intparts_g = tex(re.match(r"\\int_0\^1(.*)dx", l_.strip()).group(1))
        report(same(intparts_g, sp.exp(x) - line) and same(tex(r_), sp.integrate(sp.exp(x) - line, (x, 0, 1)))
               and min(float(g.subs(x, t_ / 20)) for t_ in range(1, 21)) > 0, f"Q7{lt}", seg)
    except Exception as err:  # noqa: BLE001
        report(False, f"Q7{lt}", f"ERROR {err}")

# Q8, Q9, Q10 (symmetry)
try:
    f8 = sp.Min(sp.exp(x), sp.exp(-x))
    full = sp.integrate(sp.exp(x), (x, -1, 0)) + sp.integrate(sp.exp(-x), (x, 0, 1))
    report(same(full, 2 * sp.integrate(sp.exp(-x), (x, 0, 1))) and same(tex(first(aparts("8")["b"])[0]), full), "Q8b", first(aparts("8")["b"])[0])
    full9 = sp.integrate(E - sp.exp(-x), (x, -1, 0)) + sp.integrate(E - sp.exp(x), (x, 0, 1))
    report(same(tex(first(aparts("9")["b"])[0]), full9) and same(full9, 2 * sp.integrate(E - sp.exp(x), (x, 0, 1))), "Q9b", str(full9))
    g10 = sp.exp(x) - sp.exp(-x)
    report(same(g10.subs(x, -x), -g10) and same(tex(first(aparts("10")["b"])[0]), sp.integrate(g10, (x, -3, 3))), "Q10b odd, integral 0")
    full10 = -sp.integrate(g10, (x, -3, 0)) + sp.integrate(g10, (x, 0, 3))
    report(same(tex(first(aparts("10")["d"])[0]), full10), "Q10d", str(sp.simplify(full10)))
except Exception as err:  # noqa: BLE001
    report(False, "Q8-Q10", f"ERROR {err}")

# Q11, Q12, Q13
try:
    report(same((x ** 2).subs(x, -1), sp.exp(x + 1).subs(x, -1)), "Q11a intersection at x = -1")
    report(min(float((sp.exp(x + 1) - x ** 2).subs(x, t_ / 20)) for t_ in range(-19, 1)) > 0, "Q11 e^{x+1} on top on (-1, 0]")
    c11 = re.search(r"<b>c</b> \\\((.*?)\\\) u", BLK["11"]).group(1)
    report(same(tex(c11), area_between(sp.exp(x + 1), x ** 2, -1, 0)), "Q11c", c11)
    has("12", "y=e^x\\) and \\(y=x", "\\(x=2\\)")
    v12 = re.search(r"\\\((\(e\^2-3\))\\\) square units", BLK["12"]).group(1)
    report(same(tex(v12), area_between(sp.exp(x), x, 0, 2)), "Q12", v12)
    an = aparts("13")
    exact_and_dec(13, "a", sp.integrate(sp.exp(x), (x, 0, 1)), an["a"], dp=4)
    trap = sp.Rational(1, 4) * (sp.exp(0) + 2 * sp.exp(sp.Rational(1, 2)) + sp.exp(1))
    report(first(an["b"])[0] == f"{float(trap):.4f}", "Q13b trapezoidal, h = 1/2", first(an["b"])[0])
    report(float(trap) > float(E - 1) and sp.diff(sp.exp(x), x, 2).subs(x, 0) > 0 and "greater" in an["c"] and "concave up" in an["c"],
           "Q13c greater, concave up")
except Exception as err:  # noqa: BLE001
    report(False, "Q11-Q13", f"ERROR {err}")

# Q14 - Q17
try:
    an = aparts("14")
    d14, p14 = first(an["a"])[0], first(an["a"])[2]
    report(same(tex(d14.split("=")[1]), sp.diff(sp.exp(-x ** 2), x)) and same(sp.diff(tex(p14), x), x * sp.exp(-x ** 2)), "Q14a", f"{d14}; {p14}")
    v1, v2 = first(an["b"])[2], first(an["b"])[5]
    h = x * sp.exp(-x ** 2)
    report(same(tex(v1.split("=")[1]), sp.integrate(h, (x, 0, 2))) and same(tex(v2), 2 * sp.integrate(h, (x, 0, 2)))
           and same(h.subs(x, -x), -h), "Q14b", f"{v1}; {v2}")
    an = aparts("15")
    i1, l1 = first(an["a"])
    I1 = sp.integrate(sp.exp(x), (x, N, 0))
    report(same(tex(i1), I1) and same(tex(l1), sp.limit(1 - sp.exp(x), x, -sp.oo)), "Q15a", f"{i1}, {l1}")
    i2, l2 = first(an["b"])
    I2 = sp.integrate(sp.exp(-x), (x, 0, N))
    report(same(tex(i2), I2) and same(tex(l2), sp.limit(I2, N, sp.oo)), "Q15b", f"{i2}, {l2}")
    c15 = first(an["c"])[0]
    I3 = sp.integrate(2 * x * sp.exp(-x ** 2), (x, 0, N))
    report(same(tex(T.split_top(prep(c15), "=")[1]), I3) and same(sp.limit(I3, N, sp.oo), 1) and "just \\(1\\)" in an["c"], "Q15c", c15)
    an = aparts("16")
    a16 = tex(first(an["a"])[0])
    I16 = sp.integrate(sp.exp(sp.sqrt(x)) / sp.sqrt(x), (x, delta, 1))
    report(same(a16, I16) and same(tex(first(an["b"])[0]), sp.limit(a16, delta, 0, "+")), "Q16", f"{a16}")
    an = aparts("17")
    d1, i17 = first(an["a"])
    report(same(tex(d1.split("=")[1]), sp.diff(x * sp.exp(-x), x)), "Q17a derivative", d1)
    I17 = sp.integrate(x * sp.exp(-x), (x, 0, N))
    report(same(tex(i17.split("=")[1]), I17), "Q17a integral", i17)
    report(same(tex(first(an["b"])[0]), sp.limit(I17, N, sp.oo)), "Q17b limit 1")
    d2, i2c = first(an["c"])
    report(same(tex(d2.split("=")[1]), sp.diff(x ** 2 * sp.exp(-x), x)) and same(tex(i2c.split("=")[1]), sp.integrate(x ** 2 * sp.exp(-x), (x, 0, sp.oo))), "Q17c", i2c)
except Exception as err:  # noqa: BLE001
    report(False, "Q14-Q17", f"ERROR {err}")

# ---------------------------------------------------------------- past papers
PPS = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">(PP \d)</span>(.*?)</span><span class="mk">(\d+) marks</span></div>(.*?)(?=<div class="pp">|<p>The school trial)', ppl, re.S)
PPAS = dict((a_, (b_, c_)) for a_, b_, c_ in re.findall(r'<div class="ppa"[^>]*><div class="pp-src"><span><span class="pn">(PP \d)</span>(.*?)</span></div>(.*?)(?=<div class="ppa"|$)', PPA, re.S))
report([p_[0] for p_ in PPS] == ["PP 1", "PP 2", "PP 3", "PP 4"] and sorted(PPAS) == ["PP 1", "PP 2", "PP 3", "PP 4"], "four past-paper questions in both files")
LABELS = {"PP 1": ("Pymble Ladies' College, 2023", "Q13(d)", [1, 2]),
          "PP 2": ("Fort Street High School, 2020", "Q11(c)", [2, 2]),
          "PP 3": ("Caringbah High School, 2020", "Q14(c)(i)(ii)", [1, 3]),
          "PP 4": ("Saint Ignatius' College, Riverview, 2024", "Q13(d)(ii)", [3])}
tot = 0
for pn, lab, mk, body in PPS:
    want = LABELS[pn]
    sub = [int(z) for z in re.findall(r'<span class="mk">(\d+)</span></div>', body)]
    tot += int(mk)
    report(lab.startswith(want[0]) and lab.replace("&nbsp;", " ").rstrip("</span>").endswith(want[1]) and PPAS[pn][0] == lab
           and sub == want[2] and sum(sub) == int(mk) and body.count('<div class="hint">') == 1, f"{pn} label, marks, hint", f"{lab[:60]} {sub}")
intro = grab(ppl, r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", "pp intro")
tmin, marks = int(intro[0]), int(intro[1])
report(marks == tot == 14 and tmin == 5 * round(1.5 * marks / 5), "PP total and time", f"{marks} marks, {tmin} min")

try:
    # PP 1: y = log_e(x - 1)
    s1 = PPAS["PP 1"][1]
    report(same(tex(grab(s1, r"\\\(\\ y=(.*?)\\\)\.", "PP1 (i)").split("=")[-1]), sp.log(E + 1 - 1)), "PP1 (i) y = 1")
    xa = sp.solve(sp.log(x - 1), x)[0]
    A1 = sp.integrate((E + 1) - (sp.exp(y) + 1), (y, 0, 1))
    A1b = sp.integrate(sp.log(x - 1), (x, xa, E + 1))
    v, _ = last_display_value(s1, 0)
    report(xa == 2 and same(v, A1) and same(A1, A1b) and "\\(1\\) square unit" in s1, "PP1 (ii) area 1 (by y and by x)", f"{v}")
    # PP 2: f = e^{x/2} + 1 and its normal at x = 0
    s2 = PPAS["PP 2"][1]
    f2 = sp.exp(x / 2) + 1
    m = -1 / sp.diff(f2, x).subs(x, 0)
    normal = m * x + f2.subs(x, 0)
    disp = re.findall(r"\\\[(.*?)\\\]", s2, re.S)
    eqs = T.split_top(prep(aligned_chain(disp[0]).split("y-2")[1]), "=") if False else None
    report("\\(y=-2x+2\\)" in s2 and same(normal, -2 * x + 2), "PP2 (i) normal y = -2x + 2", str(normal))
    xr = sp.solve(normal, x)[0]
    A2 = sp.integrate(f2 - normal, (x, 0, xr))
    v, _ = last_display_value(s2, 1)
    A2num = sp.Integral(f2 - normal, (x, 0, 1)).evalf()
    report(xr == 1 and same(v, A2) and abs(float(v) - float(A2num)) < 1e-9, "PP2 (ii) area 2 sqrt e - 2", str(v))
    # PP 3: f = 1 + ln x, inverse e^{x-1}
    s3 = PPAS["PP 3"][1]
    v, _ = last_display_value(s3, 0)
    report(same(v, sp.diff(x * sp.log(x), x)) and same(v, 1 + sp.log(x)), "PP3 (i) derivative", str(v))
    finv = sp.exp(x - 1)
    report(same((1 + sp.log(x)).subs(x, finv), x), "PP3 inverse e^{x-1}")
    A3 = sp.integrate(finv, (x, 0, 1)) - sp.integrate(1 + sp.log(x), (x, sp.exp(-1), 1))
    A3y = sp.integrate(sp.exp(y - 1) - sp.Max(0, y), (y, 0, 1))  # by symmetry in y = x: area = 2 * (area between y = x and the inverse, plus the axes part)
    # independent numeric route: integrate (top - bottom) on a fine grid of x
    import math
    ns, tot3 = 20000, 0.0
    for i in range(ns):
        xm = (i + 0.5) / ns
        bottom = max(0.0, 1 + math.log(xm))
        tot3 += (math.exp(xm - 1) - bottom) / ns
    v, _ = last_display_value(s3, 2)
    report(same(v, A3) and same(A3, 1 - 2 / E) and abs(tot3 - float(A3)) < 1e-6, "PP3 (ii) area 1 - 2/e", f"{v}, numeric {tot3:.8f}")
    # PP 4: f = ln(2x/3), normal at x = 3e^2/2
    s4 = PPAS["PP 4"][1]
    f4 = sp.log(2 * x / 3)
    a = 3 * E ** 2 / 2
    n4 = -1 / sp.diff(f4, x).subs(x, a) * (x - a) + f4.subs(x, a)
    report(same(sp.expand(n4), -3 * E ** 2 * x / 2 + 9 * E ** 4 / 4 + 2) and "y=-\\dfrac{3e^2x}{2}+\\dfrac{9e^4}{4}+2" in PPS[3][3], "PP4 normal (supplied in the stem)")
    xA = sp.solve(n4, x)[0]
    report(same(xA, a + 4 / (3 * E ** 2)) and "x=\\dfrac{3e^2}{2}+\\dfrac{4}{3e^2}" in s4, "PP4 normal meets the x-axis", str(xA))
    A4 = sp.integrate((a + (2 - y) * 2 / (3 * E ** 2)) - sp.Rational(3, 2) * sp.exp(y), (y, 0, 2))
    A4x = sp.Integral(f4, (x, sp.Rational(3, 2), a)).evalf() + (xA - a) * 2 / 2
    v, _ = last_display_value(s4, 2)
    trap = last_display_value(s4, 0)[0]
    report(same(trap, (a + xA) / 2 * 2), "PP4 trapezium", str(trap))
    report(same(v, A4) and abs(float(A4x) - float(A4)) < 1e-9, "PP4 area 3e^2/2 + 3/2 + 4/(3e^2)", f"{sp.simplify(v)} = {float(v):.6f}")
except Exception as err:  # noqa: BLE001
    report(False, "past papers", f"ERROR {err}")

# timed-practice note points to existing textbook questions
try:
    note = grab(ppl, r"do Questions (.*?) above in (\d+) minutes", "practice note")
    refs = re.findall(r"(\d+)\((\w)\)", note[0])
    ok = refs and all(n in TQ and f'<span class="pl">{lt}</span>' in TQ[n] for n, lt in refs)
    report(bool(ok), "timed-practice references", note[0])
except Exception as err:  # noqa: BLE001
    report(False, "timed-practice note", f"ERROR {err}")

print(f"\n{CNT[0]} checks, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
