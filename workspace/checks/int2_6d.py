"""Check of Lesson 6D (Integration Part 2 pack): Integration of exponential functions.

The script reads the values PRINTED in workspace/build/int2/l6d.html (tutor demos, your-turn items,
worked examples, the tip box, the textbook exercise, the past-paper question) and in a_6d.html
(lesson-example answers, textbook answers, past-paper worked solution). Printed LaTeX is turned into
sympy with the shared helper int3_tex.py, and every result is recomputed independently:
  - every printed chain 'A = B = C' that starts with an integral (inline or in an aligned display)
    is checked line by line: a definite integral by sympy.integrate with the printed limits, the
    bracket notation [F]_a^b by substitution, and an indefinite integral by differentiating each
    side (the '+C' is dropped) and comparing with the integrand;
  - each answer is matched to its question by the integrand and limits read from the lesson file,
    so an answer printed against the wrong question fails;
  - primitives are checked by differentiation, definite integrals by sympy.integrate, functions
    found from f'(x) and one value by differentiating and substituting, oddness by f(-x) = -f(x),
    and decimals by rounding the exact value.
It also checks the past-paper block: the intro marks equal the part marks, the time is 1.5 x marks
rounded to 5 minutes, one hint, the source label is the same in both files, and the timed-practice
note is present. A template must match exactly once; a missing template FAILS.

Exit status 1 if anything fails. Run: python3 workspace/checks/int2_6d.py
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
q, k, s, p, m, A, t, R = sp.symbols("q k s p m A t R")
EXTRA = {"q": q, "k": k, "s": s, "p": p, "m": m, "A": A, "t": t, "C": sp.Integer(0)}
FAILS, N = [], [0]


def report(ok, label, detail=""):
    N[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + detail.replace("\n", " ")[:160] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- TeX -> sympy
def prep(t_):
    t_ = t_.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "")
    t_ = re.sub(r"\\text\{[^{}]*\}", "", t_)
    t_ = re.sub(r"\\sqrt\[3\]\{([^{}]*)\}", r"(\1)^{\\frac13}", t_)
    t_ = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", t_)
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


def chain(text, label):
    """Check a printed chain 'LHS = S1 = S2 ...' (sides split at top-level '=')."""
    sides = [q_ for q_ in T.split_top(prep(text).replace("\\\\", " "), "=") if q_.strip()]
    try:
        vals = [side(q_) for q_ in sides]
    except Exception as err:  # noqa: BLE001
        report(False, label, f"ERROR {err} in {text[:80]!r}")
        return
    definite = "\\int_" in text or "\\Big[" in text and "\\int" not in text
    if definite or not any(v.has(sp.Integral) for v in vals):
        ok = all(same(vals[0], v) for v in vals[1:])
    else:
        d = [sp.diff(v, x).doit() for v in vals]
        ok = all(same(d[0], e) for e in d[1:])
    report(ok and len(vals) >= 2, label, f"{len(vals)} sides: " + " | ".join(sides)[:150])


def math_segments(html):
    """Inline \\(...\\) and display \\[...\\] maths, in order."""
    return re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", html, re.S)


def aligned_chain(body):
    """An aligned display 'L&=A\\\\&=B...' or '&L\\\\&\\quad=A...' -> one chain string."""
    body = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", body)
    lines = [ln.replace("&amp;", "").replace("\\quad", "").strip() for ln in body.split("\\\\")]
    return "".join(lines)


def all_chains(html, where):
    cnt = 0
    for inl, disp in math_segments(html):
        seg = inl or disp
        if "\\int" not in seg or "=" not in seg:
            continue
        if "aligned" in seg:
            seg = aligned_chain(seg)
        if "OR" in seg or "u^" in seg or "f(x)" in seg or "F(x)" in seg or "u\\," in seg:
            continue  # general formulas (Box 4, the reverse chain rule), not computed values
        cnt += 1
        chain(seg, f"{where} chain {cnt}")
    return cnt


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        raise LookupError(f"{where}: pattern matched {len(found)} times: {pattern[:60]!r}")
    return found[0]


def intparts(t_):
    """'\\int_a^b g\\,dx' -> (a, b, g) as sympy; a, b None if indefinite."""
    mt = re.match(r"\s*\\int(?:_" + LIM + r"\^" + LIM + r")?(.*?)\s*dx\s*$", prep(t_), re.S)
    if not mt:
        raise ValueError(f"not an integral: {t_!r}")
    a = tex(unbrace(mt.group(1))) if mt.group(1) else None
    b = tex(unbrace(mt.group(2))) if mt.group(2) else None
    return a, b, tex(mt.group(3))


def value_of(t_):
    a, b, g = intparts(t_)
    return sp.integrate(g, (x, a, b))


def lhs_int(seg):
    return T.split_top(prep(seg), "=")[0]


# ---------------------------------------------------------------- files and blocks
les, ans = read("l6d.html"), read("a_6d.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1]
CON = {}
for c in range(1, 6):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    blocks = re.findall(r'<div class="ex (demo|attempt|worked)"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[c] = {"demo": None, "attempt": None, "worked": []}
    for kind, tag, body in blocks:
        if kind == "worked":
            CON[c]["worked"].append((tag, body))
        else:
            CON[c][kind] = body
    CON[c]["all"] = seg
report([[t_ for t_, _ in CON[c]["worked"]] for c in range(1, 6)] ==
       [["Worked example 11"], ["Worked example 12"], ["Worked example 13", "Worked example 14"], ["Worked example 15"], ["Worked example 16"]],
       "worked examples", "textbook Examples 11-16 in Concepts 1-5")
report(all(CON[c]["demo"] and CON[c]["attempt"] for c in range(1, 6)), "every concept has a tutor demo and a your turn")

parts_ans = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
report(len(parts_ans) == 2 and ans.count("{{ahead:Lesson 6D | Integration of exponential functions}}") == 2, "answers headings and sections")
BLK = dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts_ans[0], re.S))
PPA = parts_ans[1]


def halves(block):
    a_, b_ = block.split("<b>Your turn.</b>")
    return a_, b_


# ---------------------------------------------------------------- generic chains everywhere
n1 = all_chains(teach, "lesson teaching")
n2 = all_chains(ans, "answers")
report(n1 >= 8 and n2 >= 15, "chains found", f"lesson {n1}, answers {n2}")


# ---------------------------------------------------------------- lesson examples C1-C5
def qparts(block):
    return dict(re.findall(r'<span class="pl">(\w)</span>(.*?)</span>', block, re.S))


def first_math(t_):
    return re.findall(r"\\\((.*?)\\\)", t_, re.S)


# C1: answers start with the same integral as the question; last side differentiates to the integrand
for who, qb, ab in (("demo", CON[1]["demo"], halves(BLK["C1"])[0]), ("your turn", CON[1]["attempt"], halves(BLK["C1"])[1])):
    qs = qparts(qb)
    for lt in "abc":
        try:
            qi = first_math(qs[lt])[0]
            seg = [z for z in first_math(grab(ab, rf"<b>{lt}</b>(.*?)(?:<br>|$)", f"C1 {who} {lt}")) if "\\int" in z][0]
            a1, b1, g1 = intparts(qi)
            a2, b2, g2 = intparts(lhs_int(seg))
            last = side(T.split_top(prep(seg), "=")[-1])
            report(same(g1, g2) and same(sp.diff(last, x), g1), f"C1 {who} {lt}", f"{qi} -> {seg}")
        except Exception as err:  # noqa: BLE001
            report(False, f"C1 {who} {lt}", f"ERROR {err}")

# C2: the display in the answer starts with the question's integral and ends at the exact value
for who, qb, ab in (("demo", CON[2]["demo"], halves(BLK["C2"])[0]), ("your turn", CON[2]["attempt"], halves(BLK["C2"])[1])):
    qs = qparts(qb)
    disp = re.findall(r"\\\[(.*?)\\\]", ab, re.S)
    for i, lt in enumerate("ab"):
        try:
            qi = first_math(qs[lt])[0]
            ch = aligned_chain(disp[i])
            a1, b1, g1 = intparts(qi)
            a2, b2, g2 = intparts(lhs_int(ch))
            v = side(T.split_top(prep(ch), "=")[-1])
            report(same(g1, g2) and a1 == a2 and b1 == b2 and same(v, sp.integrate(g1, (x, a1, b1))), f"C2 {who} {lt}", f"{qi} = {v}")
        except Exception as err:  # noqa: BLE001
            report(False, f"C2 {who} {lt}", f"ERROR {err}")

# C3: functions from f'(x) and one value
for who, qb, ab in (("demo", CON[3]["demo"], halves(BLK["C3"])[0]), ("your turn", CON[3]["attempt"], halves(BLK["C3"])[1])):
    try:
        fd, x0, y0 = grab(qb, r"\\\(f'\(x\)=(.*?)\\\) and that \\\(f\((.*?)\)=(.*?)\\\)", f"C3 {who} f data")
        xh = grab(qb, r"Hence find \\\(f\((.*?)\)\\\)", f"C3 {who} f hence")
        f = tex(grab(ab, r"Hence \\\(f\(x\)=(.*?)\\\)", f"C3 {who} f(x)"))
        report(same(sp.diff(f, x), tex(fd)) and same(f.subs(x, tex(x0)), tex(y0)), f"C3 {who} 1a f(x)", f"f = {f}")
        cval = tex(grab(ab, r"so \\\(C=(.*?)\\\)\.", f"C3 {who} C"))
        report(same(f - sp.diff(f, x).integrate(x), cval) or same((f - (tex(fd)).integrate(x)), cval), f"C3 {who} 1a C", str(cval))
        sides = T.split_top(prep(grab(ab, r"<b>1b</b> \\\((.*?)\\\)", f"C3 {who} 1b")), "=")
        report(sides[0].strip() == f"f({xh})" and all(same(tex(z), f.subs(x, tex(xh))) for z in sides[1:]), f"C3 {who} 1b", " = ".join(sides))
        yd, x1, y1 = grab(qb, r"\\\(y'=(.*?)\\\) and \\\(y\((.*?)\)=(.*?)\\\)", f"C3 {who} y data")
        yh = grab(qb, r"Hence find \\\(y\((.*?)\)\\\)", f"C3 {who} y hence")
        y = tex(grab(ab, r"Hence \\\(y=(.*?)\\\)", f"C3 {who} y"))
        report(same(sp.diff(y, x), tex(yd)) and same(y.subs(x, tex(x1)), tex(y1)), f"C3 {who} 2a y", f"y = {y}")
        cval = tex(grab(ab, r"and \\\(C=(.*?)\\\)\.", f"C3 {who} C2"))
        report(same(y - tex(yd).integrate(x), cval), f"C3 {who} 2a C", str(cval))
        sides = T.split_top(prep(grab(ab, r"<b>2b</b> \\\((.*?)\\\)", f"C3 {who} 2b")), "=")
        report(sides[0].strip() == f"y({yh})" and all(same(tex(z), y.subs(x, tex(yh))) for z in sides[1:]), f"C3 {who} 2b", " = ".join(sides))
        for z in re.findall(r"Substituting \\\([fy]\(.*?\)=.*?\\\), \\\\? ?\\\((.*?)\\\)", ab):
            pass
    except Exception as err:  # noqa: BLE001
        report(False, f"C3 {who}", f"ERROR {err}")

# C4: chain-rule derivative, the definite integral, and oddness
for who, qb, ab in (("demo", CON[4]["demo"], halves(BLK["C4"])[0]), ("your turn", CON[4]["attempt"], halves(BLK["C4"])[1])):
    try:
        fn = tex(grab(qb, r"differentiate \\\((.*?)\\\)\.", f"C4 {who} function"))
        qi = grab(qb, r"Hence find \\\((.*?)\\\)\.", f"C4 {who} integral")
        der = tex(T.split_top(grab(ab, r"Then \\\(\\dfrac\{dy\}\{dx\}=(.*?)\\\)\.", f"C4 {who} dy/dx"), "=")[-1])
        report(same(der, sp.diff(fn, x)), f"C4 {who} a", str(der))
        a1, b1, g1 = intparts(qi)
        seg = grab(ab, r"so \\\((\\displaystyle\\int_.*?)\\\)", f"C4 {who} b")
        a2, b2, g2 = intparts(lhs_int(seg))
        report(same(g1, g2) and a1 == a2 and b1 == b2 and same(side(T.split_top(prep(seg), "=")[-1]), sp.integrate(g1, (x, a1, b1))) and same(g1, der),
               f"C4 {who} b", seg)
        report(same(g1.subs(x, -x), -g1) and a1 == -b1, f"C4 {who} c odd", str(g1))
        oddline = grab(ab, r"because \\\((4\(-x\).*?)\\\)", f"C4 {who} odd line")
        l_, r_ = T.split_top(prep(oddline), "=")
        report(same(tex(l_), g1.subs(x, -x)) and same(tex(r_), -g1), f"C4 {who} c line", oddline)
    except Exception as err:  # noqa: BLE001
        report(False, f"C4 {who}", f"ERROR {err}")

# C5: the display starts with the question's integral; the result differentiates to the integrand
for who, qb, ab in (("demo", CON[5]["demo"], ans.split("<b>Tutor demo.</b> Let \\(u=1+e^{2x}")[1].split("<b>Your turn.</b>")[0]),
                    ("your turn", CON[5]["attempt"], ans.split("<b>Your turn.</b> Let \\(u=1-e^{3x}")[1].split("</div></div></div></div>")[0])):
    try:
        qi = grab(qb, r"find \\\((.*?)\\\)\.", f"C5 {who} q")
        ch = aligned_chain(grab(ab, r"\\\[(.*?)\\\]", f"C5 {who} display"))
        a1, b1, g1 = intparts(qi)
        a2, b2, g2 = intparts(T.split_top(prep(ch), "=")[0])
        res = side(T.split_top(prep(ch), "=")[-1])
        report(same(g1, g2) and same(sp.diff(res, x), g1), f"C5 {who}", f"result {res}")
    except Exception as err:  # noqa: BLE001
        report(False, f"C5 {who}", f"ERROR {err}")

# ---------------------------------------------------------------- worked examples (textbook lines)
we = {t_: b_ for c in range(1, 6) for t_, b_ in CON[c]["worked"]}
try:
    b13 = we["Worked example 13"]
    f13 = tex(grab(b13, r"Hence</td><td>\\\(f\(x\)=(.*?)\\\)", "WE13 f"))
    report(same(sp.diff(f13, x), sp.exp(x)) and same(f13.subs(x, 1), 0), "WE13 a", str(f13))
    v = [tex(z) for z in re.findall(r"<td>\\\((?:f\(0\)|\\phantom\{f\(0\)\})=(.*?)\\\)</td>", b13)]
    report(len(v) == 2 and all(same(z, f13.subs(x, 0)) for z in v), "WE13 b", str(v))
    b14 = we["Worked example 14"]
    y14 = tex(grab(b14, r"Hence</td><td>\\\(y=(.*?)\\\)", "WE14 y"))
    report(same(sp.diff(y14, x), 1 + 2 * sp.exp(-x)) and same(y14.subs(x, 0), 1), "WE14 a", str(y14))
    v = [tex(z) for z in re.findall(r"<td>\\\((?:y\(1\)|\\phantom\{y\(1\)\})=(.*?)\\\)</td>", b14)]
    report(len(v) == 2 and all(same(z, y14.subs(x, 1)) for z in v), "WE14 b", str(v))
    b12 = we["Worked example 12"]
    note = grab(b12, r"top and bottom by \\\(e\\\): \\\(\\ (.*?)\\\)\.", "WE12 note")
    vals = [tex(z) for z in T.split_top(prep(note), "=")]
    report(all(same(z, (sp.E ** 2 - 1) / (2 * sp.E)) for z in vals), "WE12 note chain", note)
    b15 = we["Worked example 15"]
    report(same(tex("2(-x)e^{(-x)^2}"), -tex("2xe^{x^2}")) and "2(-x)e^{(-x)^2}=-2xe^{x^2}" in b15, "WE15 odd note")
except Exception as err:  # noqa: BLE001
    report(False, "worked examples", f"ERROR {err}")

# ---------------------------------------------------------------- textbook homework
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 21)], "textbook questions 1-20", str(sorted(TQ, key=int)))
bands = hw.split("{{band:D}}")
report(bands[0].count('class="q-num"') == 4 and bands[1].split("{{band:E}}")[0].count('class="q-num"') == 12
       and bands[1].split("{{band:E}}")[1].count('class="q-num"') == 4, "bands", "F: Q1-4, D: Q5-16, E: Q17-20 (as the textbook)")
report("7" in TQ and '<span class="pl">h</span>' not in TQ["7"], "Q7(h) omitted (doubtful stem)")


def aparts(n):
    blk = BLK[n]
    got = dict(re.findall(r'<span class="ap6d"><b>(\w)</b> (.*?)</span>', blk, re.S))
    return got


def mathof(t_):
    return [z for z in re.findall(r"\\\((.*?)\\\)", t_, re.S)]


def strip_c(t_):
    return re.sub(r"\+C$", "", prep(t_))


def check_prim(n, integral=True):
    qs, an = qparts(TQ[n]), aparts(n)
    report(sorted(qs) == sorted(an), f"Q{n} parts", f"q {''.join(sorted(qs))} a {''.join(sorted(an))}")
    for lt in sorted(qs):
        try:
            qm = mathof(qs[lt])[0]
            g = intparts(qm)[2] if integral else tex(qm)
            am = mathof(an[lt])[0]
            F = tex(strip_c(am))
            report(prep(am).endswith("+C") and same(sp.diff(F, x), g), f"Q{n}{lt}", f"{qm} -> {am}")
        except Exception as err:  # noqa: BLE001
            report(False, f"Q{n}{lt}", f"ERROR {err}")


def check_def(n):
    qs, an = qparts(TQ[n]), aparts(n)
    report(sorted(qs) == sorted(an), f"Q{n} parts", f"q {''.join(sorted(qs))} a {''.join(sorted(an))}")
    for lt in sorted(qs):
        try:
            qm = mathof(qs[lt])[0]
            am = mathof(an[lt])[0]
            report(same(tex(am), value_of(qm)), f"Q{n}{lt}", f"{qm} = {am}")
        except Exception as err:  # noqa: BLE001
            report(False, f"Q{n}{lt}", f"ERROR {err}")


for n in ("1", "7", "9", "13", "15"):
    check_prim(n)
for n in ("3", "6", "8", "17"):
    check_prim(n, integral=False)
for n in ("2", "11"):
    check_def(n)

# Q4
try:
    an = aparts("4")
    F4 = tex(strip_c(mathof(an["a"])[0].split("=")[1]))
    report(same(sp.diff(F4, x), sp.exp(2 * x)), "Q4a", mathof(an["a"])[0])
    cb, fb = mathof(an["b"])
    fb_ = tex(fb.split("=")[1])
    report(same(sp.diff(fb_, x), sp.exp(2 * x)) and same(fb_.subs(x, 0), -2) and same(tex(cb.split("=")[1]), fb_ - F4), "Q4b", f"{cb}, {fb}")
    v1, v2 = mathof(an["c"])
    report(same(tex(v1.split("=")[1]), fb_.subs(x, 1)) and same(tex(v2.split("=")[1]), fb_.subs(x, 2)), "Q4c", f"{v1}, {v2}")
except Exception as err:  # noqa: BLE001
    report(False, "Q4", f"ERROR {err}")

# Q5
qs, an = qparts(TQ["5"]), aparts("5")
for lt in "abcdefgh":
    try:
        fd, cond = mathof(qs[lt])
        x0, y0 = re.match(r"f(?:\\big)?\((.*?)(?:\\big)?\)=(.*)", prep(cond)).groups()
        fa, f1 = mathof(an[lt])
        F = tex(fa.split("=", 1)[1])
        report(same(sp.diff(F, x), tex(fd.split("=", 1)[1])) and same(F.subs(x, tex(x0)), tex(y0))
               and same(tex(f1.split("=", 1)[1]), F.subs(x, 1)), f"Q5{lt}", f"{fd}, {cond} -> {fa}, {f1}")
    except Exception as err:  # noqa: BLE001
        report(False, f"Q5{lt}", f"ERROR {err}")

# Q10
try:
    an = aparts("10")
    ya, yi = mathof(an["a"])[0], mathof(an["a"])[2]
    Y = tex(ya.split("=")[1])
    report(same(sp.diff(Y, x), sp.exp(x - 1)) and same(Y.subs(x, 1), 1) and same(tex(yi), Y.subs(x, 0)), "Q10a", f"{ya}, intercept {yi}")
    yb, asy = mathof(an["b"])[0], mathof(an["b"])[1]
    Y = tex(yb.split("=")[1])
    report(same(sp.diff(Y, x), sp.exp(2 - x)) and same(Y.subs(x, 0), 1) and same(tex(asy.split("=")[1]), sp.limit(Y, x, sp.oo)), "Q10b", f"{yb}, {asy}")
    fc, f0 = mathof(an["c"])
    F = tex(fc.split("=")[1])
    report(same(sp.diff(F, x), sp.exp(x) + 1 / sp.E) and same(F.subs(x, -1), -1) and same(tex(f0.split("=")[1]), F.subs(x, 0)), "Q10c", f"{fc}, {f0}")
    F = tex(mathof(an["d"])[0].split("=")[1])
    report(same(sp.diff(F, x, 2), sp.exp(x) - sp.exp(-x)) and same(F.subs(x, 0), 0) and same(sp.diff(F, x).subs(x, 0), 0), "Q10d", str(F))
except Exception as err:  # noqa: BLE001
    report(False, "Q10", f"ERROR {err}")

# Q12 (i) derivatives, (ii) primitives / value; Q14
qs, an = qparts(TQ["12"]), aparts("12")
for lt in "abcd":
    try:
        fq, iq = mathof(qs[lt])
        fn = tex(fq.split("=")[-1])
        di, ii = mathof(an[lt])
        report(same(tex(di), sp.diff(fn, x)), f"Q12{lt}(i)", f"{fq} -> {di}")
        a1, b1, g1 = intparts(iq)
        if a1 is None:
            report(prep(ii).endswith("+C") and same(sp.diff(tex(strip_c(ii)), x), g1), f"Q12{lt}(ii)", f"{iq} -> {ii}")
        else:
            report(same(tex(ii), sp.integrate(g1, (x, a1, b1))), f"Q12{lt}(ii)", f"{iq} = {ii}")
    except Exception as err:  # noqa: BLE001
        report(False, f"Q12{lt}", f"ERROR {err}")
qs, an = qparts(TQ["14"]), aparts("14")
for lt in "ab":
    try:
        fq, iq = mathof(qs[lt])
        d_, v_ = mathof(an[lt])
        report(same(tex(d_.split("=")[1]), sp.diff(tex(fq.split("=")[1]), x)) and same(tex(v_), value_of(iq)), f"Q14{lt}", f"{d_}; {iq} = {v_}")
    except Exception as err:  # noqa: BLE001
        report(False, f"Q14{lt}", f"ERROR {err}")

# Q16(b)
try:
    iq = mathof(qparts(TQ["16"])["b"])[0]
    g = intparts(iq)[2]
    report(same(g.subs(x, -x), -g) and same(tex(mathof(aparts("16")["b"])[0]), value_of(iq)), "Q16b", iq)
except Exception as err:  # noqa: BLE001
    report(False, "Q16b", f"ERROR {err}")

# Q20 decimals
try:
    an = aparts("20")
    alpha_exact = sp.Rational(1)
    alpha = sum(sp.Rational(1, 2) ** (2 * j) / sp.factorial(2 * j) for j in range(0, 12))   # series, x = 0.5
    report(abs(alpha - sp.cosh(sp.Rational(1, 2))) < sp.Rational(1, 10 ** 12), "Q20 series = cosh 0.5", f"{sp.N(alpha, 12)}")
    a_pr = re.search(r"\\alpha\\doteq([\d.]+)", an["b"]).group(1)
    report(a_pr == f"{float(alpha):.4f}", "Q20b alpha 4 d.p.", a_pr)
    up, dn = re.findall(r"\\doteq([\d.]+)", an["d"])
    al = sp.Float(a_pr, 30)
    report(up == f"{float(al + sp.sqrt(al ** 2 - 1)):.2f}" and dn == f"{float(al - sp.sqrt(al ** 2 - 1)):.2f}"
           and up == f"{float(sp.exp(sp.Rational(1, 2))):.2f}" and dn == f"{float(sp.exp(-sp.Rational(1, 2))):.2f}", "Q20d roots 2 d.p.", f"{up}, {dn}")
    c1, c2 = re.findall(r"=([\d.]+)\\ldots", BLK["20"])
    report(f"{float(sp.exp(sp.Rational(1, 2))):.6f}".startswith(c1) and f"{float(sp.exp(-sp.Rational(1, 2))):.6f}".startswith(c2), "Q20d calculator values", f"{c1}, {c2}")
    # u = e^0.5 solves u^2 - 2 alpha u + 1 = 0 with alpha = cosh 0.5 exactly
    u = sp.exp(sp.Rational(1, 2))
    report(same(u ** 2 - 2 * sp.cosh(sp.Rational(1, 2)).rewrite(sp.exp) * u + 1, 0), "Q20c identity")
except Exception as err:  # noqa: BLE001
    report(False, "Q20", f"ERROR {err}")

report(set(BLK) == {"C1", "C2", "C3", "C4", "C5"} | {str(i) for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20)},
       "answer blocks", "C1-C5 and Q1-17, 20 (16a, 18, 19, 20a, 20c are 'show' items with no textbook result)")

# ---------------------------------------------------------------- past paper
try:
    LABEL = "Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q11(b)</span>"
    report(ppl.count(LABEL) == 1 and PPA.count(LABEL) == 1, "PP 1 label in both files")
    intro = grab(ppl, r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", "pp intro")
    sub = [int(z) for z in re.findall(r'<span class="mk">(\d+)</span></div>', ppl)]
    tot = int(grab(ppl, r'<span class="mk">(\d+) marks</span>', "pp marks"))
    tmin, marks = int(intro[0]), int(intro[1])
    report(sub == [2, 3] and tot == 5 and marks == 5 and tmin == 5 * int(1.5 * marks / 5 + 0.5), "PP marks and time", f"parts {sub}, total {tot}, {tmin} min")
    report(ppl.count('<div class="hint">') == 1 and "timed practice" in ppl, "one hint and a timed-practice note")
    y = x * sp.exp(-x)
    # (i) the derivative chain in the solution
    disp = re.findall(r"\\\[(.*?)\\\]", PPA, re.S)
    lines = T.split_top(prep(aligned_chain(disp[0])), "=")
    vals = [tex(z.replace("u'v+v'u", "0")) for z in lines[2:]]
    report(lines[1].strip() == "u'v+v'u" and all(same(v, sp.diff(y, x)) for v in vals), "PP (i) dy/dx", " = ".join(lines))
    # (ii) the reversed statement and the final chain (also covered by the generic chain check)
    rev = prep(disp[1])
    l_, r_ = T.split_top(rev, "=")
    report(same(value_of(l_), side(r_)), "PP (ii) reversing (i)", rev)
    final = T.split_top(prep(aligned_chain(disp[2])), "=")
    report(same(side(final[-1]), sp.integrate(y, (x, 0, 1))) and same(side(final[-1]), 1 - 2 / sp.E), "PP (ii) value", final[-1])
except Exception as err:  # noqa: BLE001
    report(False, "past paper", f"ERROR {err}")

# timed-practice note points to existing textbook questions
try:
    note = grab(ppl, r"do Questions (.*?) above in (\d+) minutes", "practice note")
    refs = re.findall(r"(\d+)\((\w)\)", note[0])
    ok = refs and all(n in TQ and f'<span class="pl">{lt}</span>' in TQ[n] for n, lt in refs)
    report(bool(ok), "timed-practice references", note[0])
except Exception as err:  # noqa: BLE001
    report(False, "timed-practice note", f"ERROR {err}")

print(f"\n{N[0]} checks, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
