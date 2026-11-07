"""Check of Lesson 6K (Integration Part 2 pack): Calculus with other bases.

The script reads the values PRINTED in workspace/build/int2/l6k.html (tutor demos, your-turn items,
worked examples 39-45, the tip boxes, Exercise 6K, the timed-practice note) and in a_6k.html
(lesson-example answers and textbook answers). Printed LaTeX is turned into sympy with the shared
helper int3_tex.py, extended here so that \\log_2x, \\log_{10}x, \\log_{1.05}x and \\log_ax are read
as log(x)/log(base). Every result is recomputed independently from the QUESTION as printed:
  - change-of-base values: the quotient of natural logs equals the printed logarithm, the printed
    calculator values are truncations of the true logs, the decimals are rounded from the exact
    value, and the x^y checks give back the original number;
  - derivatives by sympy.diff of the printed question function; primitives by differentiating the
    printed answer (the '+C' must be printed); every side of each printed chain is compared;
  - definite integrals and areas by sympy.integrate with the printed limits, the bracket [F]_a^b
    by substitution, and the decimals by rounding;
  - tangents by point and gradient; intersections by substitution; Q20 by solving the tangency
    conditions.
It also checks the structure (worked examples 39-45 in Concepts 1-6, questions 1-20, bands F 1-8,
D 9-18, E 19-20, answer blocks), that every {{svg:...}} exists, and that the timed-practice note
names questions that exist. A template must match exactly once; a missing template FAILS.

Exit status 1 if anything fails. Run: python3 workspace/checks/int2_6k.py
"""
import os
import re
import sys

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, rationalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

SRC = os.environ.get("INT2_SRC", os.path.join(HERE, "..", "build", "int2"))
x = T.x
a = sp.Symbol("a", positive=True)
k = sp.Symbol("k", positive=True)
y = sp.Symbol("y")
FAILS, N = [], [0]
TOL = sp.Float("1e-20")
SAMPLES = (sp.Rational(7, 5), sp.Rational(13, 4), sp.Rational(5, 3))


def report(ok, label, detail=""):
    N[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        raise LookupError(f"{where}: pattern matched {len(found)} times: {pattern[:80]!r}")
    return found[0]


# ---------------------------------------------------------------- TeX -> sympy
LETTER = {c: chr(ord("A") + i) for i, c in enumerate("0123456789")}
LETTER["."] = "P"


def base_cmd(b):
    """\\log_{1.05} -> \\lgbBPAF~ and register lgbBPAF as log(z)/log(1.05)."""
    name = "lgb" + ("a" if b == "a" else "".join(LETTER[c] for c in b))
    if name not in T.FUNCS:
        T.FUNCS[name] = name
        bv = a if b == "a" else sp.nsimplify(b)
        z = sp.Symbol("z_" + name)
        T.LOCAL[name] = sp.Lambda(z, sp.log(z) / sp.log(bv))
    return "\\" + name + "~"


def prep(s):
    s = s.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "")
    s = re.sub(r"\\text\{[^{}]*\}", "", s)
    s = re.sub(r"\\phantom\{(?:[^{}]|\{[^{}]*\})*\}", "", s)
    s = s.replace("\\,", "").replace("\\ ", " ").replace("\\ldots", "")
    s = s.replace("\\big(", "(").replace("\\big)", ")").replace("\\Big(", "(").replace("\\Big)", ")")
    s = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"\\([dt]frac)\s+(\w)(\w)", r"\\\1{\2}{\3}", s)          # \dfrac x3
    s = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\\tfrac{\2}{\3})", s)      # 1\tfrac12
    s = re.sub(r"\\log_\{([\d.]+)\}", lambda m: base_cmd(m.group(1)), s)
    s = re.sub(r"\\log_(\d)", lambda m: base_cmd(m.group(1)), s)
    s = re.sub(r"\\log_a", lambda m: base_cmd("a"), s)
    return s.strip().rstrip(".,").strip()


def tex(s, extra=None):
    loc = {"a": a, "k": k, "C": sp.Integer(0), "y": y}
    if extra:
        loc.update(extra)
    py = T.conv(prep(s))          # prep registers any new \\log_b first
    full = dict(T.LOCAL)
    full.update(loc)
    # decimals are read as exact rationals (log(1.05) must stay exact)
    return parse_expr(py, local_dict=full, transformations=T.TR + (rationalize,))


def num(v):
    return sp.N(v, 40)


def same(u, v, syms=()):
    """Equal as functions of x (and a, k): numerically, to 40 digits, at three sample points."""
    d = sp.sympify(u - v)
    if d == 0:
        return True
    for xv in SAMPLES:
        sub = {x: xv, a: sp.Rational(7, 2), k: sp.Rational(3, 7)}
        if abs(num(d.subs(sub))) > TOL:
            return False
    return True


def sides(seg):
    seg = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", seg).replace("\\\\", "")
    return [q.strip() for q in T.split_top(prep(seg), "=") if q.strip()]


def bracket(s):
    """'\\Big[F\\Big]_a^b' (or [F]_a^b) -> value F(b) - F(a)."""
    m = re.match(r"\\Big\[(.*)\\Big\]_(\{[^{}]*\}|-?\w)\^(\{[^{}]*\}|-?\w)$", s.strip(), re.S)
    if not m:
        return None
    F = tex(m.group(1))
    lo, hi = (tex(g.strip("{}")) for g in (m.group(2), m.group(3)))
    return F.subs(x, hi) - F.subs(x, lo)


def defint(s):
    """'\\int_a^b f dx' -> value."""
    m = re.match(r"\\int_(\{[^{}]*\}|-?\w)\^(\{[^{}]*\}|-?\w)(.*)dx$", prep(s).strip(), re.S)
    if not m:
        return None
    lo, hi = (tex(g.strip("{}")) for g in (m.group(1), m.group(2)))
    f = tex(m.group(3))
    return sp.integrate(f, (x, lo, hi)), f, lo, hi


def value(side):
    v = bracket(side)
    if v is not None:
        return v
    d = defint(side) if side.lstrip().startswith("\\int_") else None
    if d is not None:
        return d[0]
    return tex(side)


def dec_ok(exact, printed, kind, n):
    """kind 'dp' or 'sf': printed decimal string equals the exact value rounded."""
    v = float(num(exact))
    want = f"{v:.{n}f}" if kind == "dp" else f"{float(f'{v:.{n}g}'):.{max(0, n - 1 - int(sp.floor(sp.log(abs(v), 10))))}f}"
    return printed == want, want


# ---------------------------------------------------------------- files and blocks
les, ans = read("l6k.html"), read("a_6k.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1]
CON = {}
for c in range(1, 7):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    blocks = re.findall(r'<div class="ex (demo|attempt|worked)"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<div class="box |$)', seg, re.S)
    CON[c] = {"worked": [], "all": seg}
    for kind, tag, body in blocks:
        if kind == "worked":
            CON[c]["worked"].append((tag, body))
        else:
            CON[c][kind] = body
report([[t_ for t_, _ in CON[c]["worked"]] for c in range(1, 7)]
       == [["Worked example 39"], ["Worked example 40", "Worked example 41"], ["Worked example 42"], ["Worked example 43"], ["Worked example 44"], ["Worked example 45"]],
       "worked examples", "textbook Examples 39-45 in Concepts 1-6")
report(all("demo" in CON[c] and "attempt" in CON[c] for c in range(1, 7)), "every concept has a tutor demo and a your turn")
WE = {int(t_.split()[-1]): b_ for c in CON for t_, b_ in CON[c]["worked"]}
for n_ in WE:
    report('<div class="sol-label">Solution</div>' in WE[n_] and "box tip" not in WE[n_], f"WE{n_} has a solution and no tip inside")

BLK = dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S))
report(set(BLK) == {f"C{i}" for i in range(1, 7)} | {str(i) for i in range(1, 21) if i != 17}, "answer blocks", "C1-C6 and Q1-20 except the show-that Q17")
report(ans.count("{{ahead:Lesson 6K | Calculus with other bases}}") == 1 and "Past-Paper" not in ans, "answers heading (no past-paper section)")
for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}")


def halves(block):
    d_, y_ = block.split("<b>Your turn.</b>")
    return d_, y_


def maths(s):
    return [m1 or m2 for m1, m2 in re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", s, re.S)]


# ---------------------------------------------------------------- Concept 1 / WE39 / Q1
def trunc_ok(printed, truth):
    """'3.688\\,879' (printed with \\ldots) is a truncation of truth."""
    p = printed.replace("\\,", "").replace("\\ldots", "").strip()
    dp = len(p.split(".")[1])
    tv = num(truth)
    return abs(tv - sp.Float(p, 40)) < sp.Float(10) ** (-dp) and (tv - sp.Float(p, 40)) * sp.sign(tv) >= 0


def check_c1(qb, ab, where):
    b = grab(qb, r"Express the function \\\(y=\\log_(\d)x\\\)", f"{where} base")
    items = re.findall(r'<span class="pl">(i+)</span>\\\(\\log_' + b + r'([\d.]+)\\\)', qb)
    report(len(items) == 3, f"{where} three items", str(items))
    pa = grab(ab, r"<b>a</b> \\\((\\log_" + b + r"x=.*?)\\\)", f"{where} a")
    l_, r_ = T.split_top(prep(pa), "=")
    report(same(tex(l_), sp.log(x) / sp.log(int(b))) and same(tex(r_), sp.log(x) / sp.log(int(b))), f"{where} a change of base", pa)
    for lab, v in items:
        line = grab(ab, rf"<b>{lab}</b> \\\((\\log_{b}{re.escape(v)}=.*?)\\\)", f"{where} b {lab}")
        parts = [q.strip() for q in line.replace("\\doteq", "=").split("=")]
        truth = sp.log(sp.nsimplify(v)) / sp.log(int(b))
        q_ok = same(tex(parts[0]), truth) and same(tex(parts[1]), truth)
        nm, dn = re.match(r"\\dfrac\{(.*?)\}\{(.*?)\}", parts[2]).groups()
        t_ok = trunc_ok(nm, sp.log(sp.nsimplify(v))) and trunc_ok(dn, sp.log(int(b)))
        ok_d, want = dec_ok(truth, parts[3], "dp", 4)
        report(q_ok and t_ok and ok_d, f"{where} b {lab} log_{b} {v}", f"{line[:70]} (want {want})")
        chk = grab(ab, rf"<b>{lab}</b> \\\({b}\^\{{({re.escape(parts[3])})\}}\\doteq([\d.]+)\\\)", f"{where} c {lab}")
        back = float(int(b) ** float(chk[0]))
        dpn = len(chk[1].split(".")[1]) if "." in chk[1] else 0
        report(round(back, dpn) == float(chk[1]) and abs(float(chk[1]) - float(v)) < 1e-12, f"{where} c {lab} {b}^{chk[0]} = {back:.6g}", chk[1])


try:
    check_c1(CON[1]["demo"], halves(BLK["C1"])[0], "C1 demo")
    check_c1(CON[1]["attempt"], halves(BLK["C1"])[1], "C1 your turn")
    w = WE[39]
    for v, d in (("30", "2.1133"), ("2", "0.4307"), ("0.07", "-1.6523")):
        seg = grab(w, r"\\\[\\begin\{aligned\}\\log_5" + re.escape(v) + r"(.*?)\\end\{aligned\}\\\]", f"WE39 {v}")
        fr, dd = grab(seg, r"=\\dfrac\{(.*?)\}\{\\log_e5\}\\\\&amp;\\doteq(-?[\d.]+)", f"WE39 {v} parts")
        truth = sp.log(sp.nsimplify(v)) / sp.log(5)
        report(same(tex(fr), sp.log(sp.nsimplify(v))) and dec_ok(truth, dd, "dp", 4)[0] and dd == d, f"WE39 log_5 {v}", dd)
        chk = grab(w, r"\\\(5\^\{" + re.escape(d) + r"\}\\doteq([\d.]+)\\\)", f"WE39 c {v}")
        report(round(5 ** float(d), 4 if v == "0.07" else 0) == float(chk) and chk == v, f"WE39 c 5^{d} = {5 ** float(d):.6g}", chk)
    tipv = grab(CON[1]["all"], r"\\\(5\^\{2\.1133\}=([\d.]+)\\ldots\\\)", "WE39 tip value")
    report(trunc_ok(tipv, sp.Integer(5) ** sp.Rational(21133, 10000)), "WE39 tip 5^2.1133 truncation", tipv)
except Exception as err:  # noqa: BLE001
    report(False, "Concept 1", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 2 / WE40, WE41
def deriv_items(qb, where):
    return re.findall(r'<span class="pl">(\w)</span>\\\((?:y=)?(.*?)\\\)', qb)


try:
    for who, qb, ab in (("C2 demo", CON[2]["demo"], halves(BLK["C2"])[0]), ("C2 your turn", CON[2]["attempt"], halves(BLK["C2"])[1])):
        q1, q2 = qb.split("<b>2</b>")
        for grp, qq in (("1", q1), ("2", q2)):
            for lt, f_ in deriv_items(qq, who):
                f = tex(f_)
                df = sp.diff(f, x)
                key = f"{grp}{lt}"
                if grp == "1":
                    head = grab(ab, rf"<b>{key}</b> Here \\\(\\ y=(.*?)\.\\\)", f"{who} {key} head")
                    hs = T.split_top(prep(head), "=")
                    disp = grab(ab, rf"<b>{key}</b>.*?\\\[(\\begin\{{aligned\}}\\dfrac\{{dy\}}\{{dx\}}.*?)\\\]", f"{who} {key} chain")
                    ds = sides(disp)[1:]
                    ok = prep(hs[0]) == prep(f_) and all(same(tex(z), f) for z in hs) and all(same(tex(z), df) for z in ds)
                    report(ok, f"{who} {key} d/dx {f_}", " = ".join(ds))
                else:
                    line = grab(ab, rf"<b>{key}</b> \\\(\\dfrac\{{d\}}\{{dx\}}(.*?)=(.*?)\\\)", f"{who} {key}")
                    report(prep(line[0]) == prep(f_) and same(tex(line[1]), df), f"{who} {key} d/dx {f_}", line[1])
    w = WE[40]
    for lt, b in (("a", "2"), ("b", "a")):
        col = w.split("<p><b>a</b>")[1].split("</div><div>")[0] if lt == "a" else w.split("<p><b>b</b>")[1]
        f = tex(f"\\log_{b}x")
        ms = maths(col)
        disp = [z for z in ms if "dy" in z][0]
        ys = [z for z in ms if z.startswith("y=")]
        report(all(same(tex(T.split_top(prep(z), "=")[1]), f) for z in ys) and all(same(tex(z), sp.diff(f, x)) for z in sides(disp)[1:]), f"WE40 {lt} log_{b} x", " = ".join(sides(disp)[1:]))
    w = WE[41].split('<div class="sol-label">')[1]
    for b in ("10", "1.05"):
        f_, d_ = grab(w, r"\\\(\\dfrac\{d\}\{dx\}(\\log_\{" + re.escape(b) + r"\}x)=(.*?)\\\)", f"WE41 {b}")
        report(same(tex(d_), sp.diff(tex(f_), x)), f"WE41 d/dx log_{b} x", d_)
except Exception as err:  # noqa: BLE001
    report(False, "Concept 2", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 3 / WE42
try:
    for who, qb, ab in (("C3 demo", CON[3]["demo"], halves(BLK["C3"])[0]), ("C3 your turn", CON[3]["attempt"], halves(BLK["C3"])[1])):
        b = int(grab(qb, r"intercept of \\\(y=\\log_(\d)x\\\)", f"{who} base"))
        g_print = tex(grab(qb, r"has gradient \\\((\\dfrac\{1\}\{\\log_e\d\})\.\\\)", f"{who} gradient"))
        g_want = tex(grab(qb, r"at the \\\(x\\\)-intercept has gradient \\\((.*?)\\\)\.", f"{who} c gradient"))
        f = sp.log(x) / sp.log(b)
        x0 = sp.solve(sp.Eq(f, 0), x)
        report(x0 == [1] and f"\\(x={b}^0=1\\)" in ab and "\\((1,0)\\)" in ab and same(g_print, sp.diff(f, x).subs(x, 1)), f"{who} a intercept (1,0), gradient 1/log {b}")
        yy = grab(ab, r"\\\\y&amp;=(\\dfrac\{x-1\}\{\\log_e\d\})\.", f"{who} b tangent")
        report(same(tex(yy), sp.diff(f, x).subs(x, 1) * (x - 1)), f"{who} b tangent", yy)
        cpart = ab.split("<b>c</b>")[1]
        sol = sp.solve(sp.Eq(1 / sp.log(a), g_want), a)
        cs = [z for z in T.split_top(prep(re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", maths(cpart)[-1]).split("\\\\")[-1]), "=") if z.strip()]
        report(len(sol) == 1 and prep(cs[0]) == "a" and len(cs) >= 2 and all(same(tex(z), sol[0]) for z in cs[1:]), f"{who} c base with gradient {g_want}", f"a = {cs[-1]} ({sol})")
    w = WE[42]
    report(same(sp.diff(tex("\\log_ax"), x).subs(x, 1), 1 / sp.log(a)) and "\\(y'=\\dfrac{1}{\\log_ea},\\ \\)" in w, "WE42 a gradient at (1,0)")
    report(sp.solve(sp.Eq(sp.log(a), 1), a) == [sp.E] and "a&amp;=e^1\\\\&amp;=e," in w, "WE42 b log a = 1 iff a = e")
except Exception as err:  # noqa: BLE001
    report(False, "Concept 3", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 4 / WE43
try:
    for who, qb, ab in (("C4 demo", CON[4]["demo"], halves(BLK["C4"])[0]), ("C4 your turn", CON[4]["attempt"], halves(BLK["C4"])[1]),
                        ("WE43", WE[43].split('<div class="sol-label">')[0], WE[43].split('<div class="sol-label">')[1])):
        items = re.findall(r'<span class="pl">(\w)</span>\\\((.*?)\\\)', qb)
        report(len(items) >= 3, f"{who} items", str(items))
        for lt, e_ in items:
            seg = ab.split(f"<b>{lt}</b>")[1].split("</div>")[0]
            ms = maths(seg)
            ss = [z for m_ in ms for z in sides(m_)]
            truth = tex(e_)
            ok = prep(ss[0]) == prep(e_) and all(same(tex(z), truth) for z in ss) and "e^{" in ss[-1]
            report(ok, f"{who} {lt} {e_} as a power of e", " = ".join(ss))
except Exception as err:  # noqa: BLE001
    report(False, "Concept 4", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 5 / WE44
def grad_table(ab, b, where, sf):
    rows = re.findall(r"<td>(?:Here|Using the standard form,|Hence when \\\(x=0\\\),|)</td><td>\\\((.*?)\\\)</td>", ab)
    f = sp.Integer(b) ** x
    yv = [T.split_top(prep(r_), "=")[-1] for r_ in rows]
    ok = same(tex(yv[0]), f) and same(tex(yv[1]), sp.diff(f, x))
    ok = ok and all(same(tex(z), sp.diff(f, x).subs(x, 0)) for z in yv[2:4])
    d = rows[4].split("\\doteq")[1].rstrip(".")
    okd, want = dec_ok(sp.log(b), d, "sf", sf)
    report(ok and okd and len(rows) == 5, f"{where} y' = {b}^x log {b}, gradient at x = 0", f"{d} (want {want})")


try:
    grad_table(halves(BLK["C5"])[0], 3, "C5 demo", 3)
    grad_table(halves(BLK["C5"])[1], 5, "C5 your turn", 3)
    grad_table(WE[44].split('<div class="sol-label">')[1], 2, "WE44", 3)
    for who, ab, b in (("C5 demo", halves(BLK["C5"])[0], 3), ("C5 your turn", halves(BLK["C5"])[1], 5)):
        report(f"\\int{b}^x\\,dx" in (CON[5]["demo"] if b == 3 else CON[5]["attempt"]), f"{who} b question integral of {b}^x")
        bpart = ab.split("<p><b>b</b>")[1]
        pw = maths(bpart)[0]
        report(all(same(tex(z), sp.Integer(b) ** x) for z in T.split_top(prep(pw), "=")), f"{who} b {b}^x as a power of e", pw)
        disp = [m_ for m_ in maths(bpart) if "aligned" in m_][0]
        ss = sides(disp)
        f = sp.Integer(b) ** x
        ok = re.sub(r"\s", "", ss[0]) == f"\\int{b}^xdx" and all("+C" in z.replace(" ", "") for z in ss[2:])
        for z in ss[1:]:
            z2 = re.sub(r"\\int(.*)dx$", r"\1", z) if z.startswith("\\int") else z
            ok = ok and (same(tex(z2), f) if z.startswith("\\int") else same(sp.diff(tex(z2), x), f))
        report(ok, f"{who} b primitive of {b}^x", " = ".join(ss))
except Exception as err:  # noqa: BLE001
    report(False, "Concept 5", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 6 / WE45
def area_chain(disp, line, curve, where, lim=(0, 1)):
    ss = sides(disp)
    truth = sp.integrate(line - curve, (x, *lim))
    vals = []
    for z in ss[1:]:
        z = re.sub(r"square units", "", z)
        if "\\doteq" in z:
            z = z.split("\\doteq")[0]
        if "upper curve" in z:
            continue
        vals.append(num(value(z)))
    dec = grab(disp, r"\\doteq([\d.]+)\\text\{ square units", f"{where} decimal")
    okd, want = dec_ok(truth, dec, "sf", 4)
    ok = all(abs(v - num(truth)) < TOL for v in vals) and len(vals) >= 4
    report(ok and okd, f"{where} area chain", f"{len(vals)} sides = {float(truth):.8g}; printed {dec} (want {want})")


try:
    for who, qb, ab in (("C6 demo", CON[6]["demo"], halves(BLK["C6"])[0]), ("C6 your turn", CON[6]["attempt"], halves(BLK["C6"])[1]),
                        ("WE45", WE[45].split('<div class="sol-label">')[0], WE[45].split('<div class="sol-label">')[1])):
        ln_, cv_, A_, B_ = grab(qb, r"the line \\\(y=(.*?)\\\) meets the curve \\\(y=(.*?)\\\) at \\\(A\((.*?)\)\\\) and \\\(B\((.*?)\)\\\)", f"{who} question")
        line, curve = tex(ln_), tex(cv_)
        pts = [tuple(tex(c_) for c_ in p_.split(",")) for p_ in (A_, B_)]
        report(all(line.subs(x, px) == py and curve.subs(x, px) == py for px, py in pts), f"{who} A and B on both graphs", f"{A_}; {B_}")
        report(line.subs(x, sp.Rational(1, 2)) > curve.subs(x, sp.Rational(1, 2)), f"{who} the line is the upper curve on (0,1)")
        disp = [m_ for m_ in maths(ab) if "Area" in m_][0]
        report(any(re.sub(r"\s", "", z).startswith("\\int_0^1") for z in sides(disp)[:2]), f"{who} integral from 0 to 1")
        area_chain(disp, line, curve, who)
        if who != "WE45":
            amid = grab(ab, r"At \\\(x=\\tfrac12\\\), \\\(\\ (.*?)\\\) and \\\((.*?)\\\)", f"{who} midpoint")
            l2 = T.split_top(prep(amid[0]), "=")
            c2 = [z.split("\\doteq")[0] for z in T.split_top(prep(amid[1].replace("\\doteq", "=")), "=")]
            report(same(tex(l2[1]), line.subs(x, sp.Rational(1, 2))) and abs(float(tex(c2[-1])) - float(curve.subs(x, sp.Rational(1, 2)))) < 5e-4, f"{who} midpoint values", f"{amid}")
            av = grab(ab, r"<b>a</b> When \\\(x=0\\\): \\\(\\ (.*?)\\\) and \\\((.*?)\\\)\. When \\\(x=1\\\): \\\(\\ (.*?)\\\) and \\\((.*?)\\\)\.", f"{who} a")
            ok = all(same(tex(T.split_top(prep(z), "=")[0]).subs(x, xv), e_.subs(x, xv)) and same(tex(T.split_top(prep(z), "=")[1]), e_.subs(x, xv))
                     for z, e_, xv in ((av[0], line, 0), (av[1], curve, 0), (av[2], line, 1), (av[3], curve, 1)))
            report(ok, f"{who} a substitution", " ; ".join(av))
    tip = CON[6]["all"].split("The lines that Worked example 45 leaves out")[1]
    eq = grab(tip, r"\\\[(\\Big\(\\tfrac12\+1.*?)\\\]", "WE45 tip chain")
    vals = [num(tex(z)) for z in T.split_top(prep(eq), "=")]
    truth = sp.Rational(3, 2) - 1 / sp.log(2)
    report(all(abs(v - num(truth)) < TOL for v in vals), "WE45 tip simplification", f"{len(vals)} sides")
    dd = grab(tip, r"\\\(1\.5-1\.442\\,695\\ldots=0\.057\\,304\\ldots\\doteq0\.05730\\\)", "WE45 tip decimals")
    report(trunc_ok("1.442695", 1 / sp.log(2)) and trunc_ok("0.057304", truth), "WE45 tip decimals 1/log 2 and the area")
    report("\\(2^{\\frac12}=\\sqrt2\\doteq1.414\\)" in tip and f"{float(sp.sqrt(2)):.3f}" == "1.414", "WE45 tip sqrt 2")
except Exception as err:  # noqa: BLE001
    report(False, "Concept 6", f"ERROR {err}")

# ---------------------------------------------------------------- textbook homework
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 21)], "textbook questions 1-20", str(sorted(TQ, key=int)))
bands = hw.split("{{band:D}}")
report(bands[0].count('class="q-num"') == 8 and bands[1].split("{{band:E}}")[0].count('class="q-num"') == 10
       and bands[1].split("{{band:E}}")[1].count('class="q-num"') == 2, "bands", "F: Q1-8, D: Q9-18, E: Q19-20 (as the textbook)")


def qparts(n):
    return dict(re.findall(r'<span class="pl">(\w+)</span>(.*?)</span>(?=<span><span class="pl">|</div>)', TQ[n], re.S))


def aparts(n, blk=None):
    return dict(re.findall(r'<span class="ap6k"><b>(\w+)</b> (.*?)</span>(?= <span class="ap6k">|<br>|</div>|$)', blk or BLK[n], re.S))


def qm(n):
    return {lt: maths(b_)[0] for lt, b_ in qparts(n).items() if maths(b_)}


try:
    # Q1
    an = aparts("1")
    for lt, qt in qm("1").items():
        b, v = re.match(r"\\log_(\d)([\d.]+)$", qt).groups()
        fr, d = maths(an[lt])[0].split("\\doteq")
        truth = sp.log(sp.nsimplify(v)) / sp.log(int(b))
        ok_d, want = dec_ok(truth, d, "sf", 3)
        report(same(tex(fr), truth) and ok_d, f"Q1{lt} {qt}", f"{d} (want {want})")
    # Q2, Q3, Q4, Q5
    for n in ("2", "3", "4", "5"):
        an = aparts(n)
        for lt, qt in qm(n).items():
            f = tex(qt.split("=", 1)[1])
            ms = maths(an[lt])
            ok = True
            if n in ("2", "4"):
                ok = same(tex(ms[0].split("=", 1)[1]), f) and (n != "4" or "e^{" in ms[0]) and (n != "2" or "\\log_e" in ms[0] and "\\log_" + qt.split("\\log_")[1][0] not in ms[0].replace("\\log_e", ""))
            last = ms[-1].replace("\\ ", "").strip()
            yp = last.split("=", 1)[1]
            ok = ok and last.startswith("y'=") and same(tex(yp), sp.diff(f, x))
            report(ok, f"Q{n}{lt} {qt}", an[lt][:90])
    # Q6
    an = aparts("6")
    for lt, qt in qm("6").items():
        f = tex(re.match(r"\\int(.*)dx$", prep(qt)).group(1))
        F = maths(an[lt])[0]
        report("+C" in F and same(sp.diff(tex(F), x), f), f"Q6{lt} {qt}", F)
    # Q7, Q10
    for n, kind, nd in (("7", "sf", 4), ("10", "dp", 4)):
        an = aparts(n)
        for lt, qt in qm(n).items():
            truth = defint(qt)[0]
            ex_, d = maths(an[lt])[0].split("\\doteq")
            ok_d, want = dec_ok(truth, d, kind, nd)
            report(same(tex(ex_), truth) and ok_d, f"Q{n}{lt} {qt}", f"{ex_} = {d} (want {want})")
    # Q8 table
    rows = re.findall(r"<tr><td>\\\((\\log_\w)x\\\)</td>(.*?)</tr>", BLK["8"])
    xs = [tex(v) for v in re.findall(r"<td>\\\((.*?)\\\)</td>", re.search(r"<tr><td>\\\(x\\\)</td>(.*?)</tr>", BLK["8"]).group(1))]
    ok = len(rows) == 3 and [sp.nsimplify(v) for v in xs] == [sp.Rational(1, 4), sp.Rational(1, 2), 1, 2, 4]
    for lg, cells in rows:
        b = {"\\log_2": 2, "\\log_e": sp.E, "\\log_4": 4}[lg]
        vals = re.findall(r"<td>\\\((.*?)\\\)</td>", cells)
        for xv, cv in zip(xs, vals):
            tv = float(sp.log(xv) / sp.log(b))
            ok = ok and abs(float(cv) - round(tv, 2)) < 1e-9
    report(ok and "{{svg:a6k_q8}}" in BLK["8"], "Q8a table (2 d.p.) and Q8b graph", str(rows)[:120])
    # Q9
    an = aparts("9", BLK["9"].replace("<b>c</b> <b>i</b>", "<b>ci</b>").replace("<b>ii</b>", "<b>cii</b>"))
    for lt, b in (("a", 2), ("b", 2), ("ci", 3), ("cii", 5)):
        f = sp.log(x) / sp.log(b)
        ms = maths(an[lt])
        tl = f.subs(x, 1) + sp.diff(f, x).subs(x, 1) * (x - 1)
        if lt == "a":
            report(same(tex(ms[0].split("=")[1]), sp.diff(f, x)) and same(tex(ms[1]), sp.diff(f, x).subs(x, 1)), "Q9a y' and gradient at x = 1", an[lt])
        else:
            report(same(tex(ms[0].split("=")[1]), tl), f"Q9{lt} tangent to log_{b} x at x = 1", ms[0])
    report("\\(y=\\log_3x\\)" in TQ["9"] and "\\(y=\\log_5x\\)" in TQ["9"], "Q9c question functions")
    # Q11
    f = sp.log(x) / sp.log(10)
    hd = maths(BLK["11"].split("<br>")[0])
    report(same(tex(hd[0].split("=")[1]), f) and same(tex(hd[1].split("=")[1]), sp.diff(f, x)), "Q11 y and y'", " ; ".join(hd))
    an = aparts("11", BLK["11"].split("<br>")[1])
    g10 = sp.diff(f, x).subs(x, 10)
    report(same(tex(maths(an["a"])[0]), g10) and f.subs(x, 10) == 1, "Q11a gradient at (10,1)", an["a"])
    L, R = T.split_top(prep(maths(an["b"])[0]), "=")
    Lx = tex(L)
    ysol = sp.solve(Lx, y)
    report(tex(R) == 0 and len(ysol) == 1 and same(ysol[0], 1 + g10 * (x - 10)), "Q11b tangent in general form", maths(an["b"])[0])
    xc = tex(maths(an["c"])[0].split("=")[1])
    report(sp.simplify(sp.diff(f, x).subs(x, xc) - 1) == 0, "Q11c gradient 1", maths(an["c"])[0])
    # Q12
    ms = maths(BLK["12"])
    tans = [tex(z.split("=", 1)[1]) for z in ms[:3]]
    ok = True
    for tl, b in zip(tans, (2, sp.E, 4)):
        g = sp.log(x) / sp.log(b)
        ok = ok and same(tl, g.subs(x, 3) + sp.diff(g, x).subs(x, 3) * (x - 3))
    pt = grab(BLK["12"], r"\\\(\((3-3\\log_e3),\\,0\)\\\)", "Q12b point")
    xp = tex(pt)
    report(ok, "Q12a three tangents at x = 3", " ; ".join(ms[:3]))
    report(all(sp.simplify(tl.subs(x, xp)) == 0 for tl in tans), "Q12b common x-intercept", pt)
    # Q13 - Q16, Q18
    report(all((2 ** x).subs(x, px) == py and (1 + 2 * x - x ** 2).subs(x, px) == py for px, py in ((0, 1), (1, 2))), "Q13a A(0,1), B(1,2) on both curves")
    a13 = grab(BLK["13"], r"\\\(\\Big\((.*?)\\Big\)\\\) square units", "Q13b")
    report(same(tex(a13), sp.integrate(1 + 2 * x - x ** 2 - 2 ** x, (x, 0, 1))) and (1 + 2 * x - x ** 2 - 2 ** x).subs(x, sp.Rational(1, 2)) > 0, "Q13b area", a13)
    i14 = grab(BLK["14"], r"intercepts are \\\(\((0,\d+)\)\\\) and \\\(\((\d+,0)\)\\\)", "Q14 intercepts")
    a14 = grab(BLK["14"], r"area is \\\(\\Big\((.*?)\\Big\)\\\)", "Q14 area")
    f14 = 8 - 2 ** x
    report(f14.subs(x, 0) == int(i14[0].split(",")[1]) and sp.solve(f14, x) == [int(i14[1].split(",")[0])], "Q14 intercepts", str(i14))
    report(same(tex(a14), sp.integrate(f14, (x, 0, 3))), "Q14 area", a14)
    a15 = grab(BLK["15"], r"\\\(\\Big\((.*?)\\Big\)\\\) square units", "Q15b")
    report(same(tex(a15), sp.integrate(3 - 3 ** x, (x, 0, sp.solve(3 - 3 ** x, x)[0]))) and "{{svg:a6k_q15}}" in BLK["15"], "Q15 area (and sketch)", a15)
    an = aparts("16")
    report(all(sp.simplify((x + 1 - 4 ** x).subs(x, xv)) == 0 for xv in (0, sp.Rational(-1, 2))) and (x + 1 - 4 ** x).subs(x, sp.Rational(-1, 4)) > 0
           and "\\big(-\\tfrac12,\\tfrac12\\big)" in TQ["16"], "Q16a intersections, line above the curve")
    i16 = maths(an["b"])[0]
    dv = defint(i16)
    report(dv is not None and dv[2] == sp.Rational(-1, 2) and dv[3] == 0 and same(dv[1], x + 1 - 4 ** x), "Q16b integral", i16)
    report(same(tex(maths(an["c"])[0]), sp.integrate(x + 1 - 4 ** x, (x, sp.Rational(-1, 2), 0))), "Q16c value", maths(an["c"])[0])
    an = aparts("18")
    ms = maths(an["a"])
    report(same(tex(ms[0].split("=")[1]), sp.diff(x * sp.log(x) - x, x)) and "+C" in ms[1] and same(sp.diff(tex(ms[1].split("=")[1]), x), sp.log(x)), "Q18a", " ; ".join(ms))
    report(same(tex(maths(an["b"])[0]), sp.integrate(sp.log(x) / sp.log(10), (x, 1, 10))) and "\\int_1^{10}\\log_{10}x\\,dx" in TQ["18"], "Q18b", maths(an["b"])[0])
    # Q17 show-that items: verify the claim
    ok = True
    for b in (3, 5, a):
        g = sp.log(x) / sp.log(b)
        tl = g.subs(x, sp.E) + sp.diff(g, x).subs(x, sp.E) * (x - sp.E)
        ok = ok and sp.simplify(tl.subs(x, 0)) == 0
    report(ok, "Q17 (no printed answer) tangents at x = e pass through the origin")
    # Q19
    q19 = TQ["19"]
    secs = {s_: q19.split(f'<span class="pl">{s_}</span>Use the standard form')[1].split("</div></span>")[0] for s_ in "abc"}
    a19 = {s_: BLK["19"].split(f"<b>{s_}</b>")[1].split("<br>")[0] for s_ in "abc"}
    for s_ in "abc":
        qi = dict(re.findall(r'<span class="pl">(i+)</span>\\\((.*?)\\\)', secs[s_]))
        ai = dict(re.findall(r'<span class="ap6k"><b>(i+)</b> \\\((.*?)\\\)</span>', a19[s_]))
        for r_ in ("i", "ii", "iii"):
            if s_ in "ab":
                f = tex(qi[r_].split("=", 1)[1])
                report(ai[r_].startswith("y'=") and same(tex(ai[r_].split("=", 1)[1]), sp.diff(f, x)), f"Q19{s_}({r_}) {qi[r_]}", ai[r_])
            else:
                f = tex(re.match(r"\\int(.*)dx$", prep(qi[r_])).group(1))
                report("+C" in ai[r_] and same(sp.diff(tex(ai[r_]), x), f), f"Q19c({r_}) {qi[r_]}", ai[r_])
    # Q20
    b20 = BLK["20"]
    pa = maths(b20.split("<b>a</b>")[1].split("<br>")[0])
    report(same(tex(pa[0].split("=")[1]).subs(k, sp.log(a)), a ** x) and same(tex(pa[1].split("=")[1]).subs(k, sp.log(a)), sp.log(x) / sp.log(a)), "Q20a both equations with base e", " ; ".join(pa))
    pc = maths(b20.split("<b>c</b>")[1].split("<br>")[0])
    ev = [tex(z.split("=")[0]) for z in pc]
    report(same(ev[0], sp.diff(sp.exp(k * x), x)) and same(ev[1], sp.diff(sp.log(x) / k, x)), "Q20c the two gradient equations", " ; ".join(pc))
    sol = sp.solve([sp.Eq(k * sp.exp(k * x), 1), sp.Eq(1 / (k * x), 1)], [k, x], dict=True)
    pd = maths(b20.split("<b>d</b>")[1])
    kv, av = tex(pd[0].split("=")[1]), tex(pd[1].split("=")[1])
    report(len(sol) == 1 and same(kv, sol[0][k]) and same(av, sp.exp(sol[0][k])) and sp.simplify(av ** sp.E - sp.E) == 0, "Q20d k = 1/e, a = e^(1/e)", f"{pd} sol {sol}")
    report("y=\\log_ax" in b20 and "y=\\log_e x" not in b20, "Q20b inverse functions named with base a")
except Exception as err:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    report(False, "textbook homework", f"ERROR {err}")

# ---------------------------------------------------------------- timed-practice note
try:
    report("mini exam" not in ppl and '<div class="pp"' not in ppl and "timed practice" in ppl, "no past-paper questions, timed-practice section")
    note = grab(ppl, r"For timed practice, do Questions (.*?) above in (\d+) minutes\.", "practice note")
    refs = re.findall(r"(\d+)(?:\((\w)\))?", note[0])
    ok = bool(refs)
    for n, lt in refs:
        ok = ok and n in TQ and (not lt or f'<span class="pl">{lt}</span>' in TQ[n])
    report(ok and int(note[1]) % 5 == 0, "timed-practice references exist", f"{note[0]} in {note[1]} min")
    report("have no integration question that first needs this lesson" in ppl, "note wording limited to integration questions (catalogue scope)")
except Exception as err:  # noqa: BLE001
    report(False, "timed-practice note", f"ERROR {err}")

print(f"\n{N[0]} checks, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
