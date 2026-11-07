"""Check of Lesson 6I (Integration Part 2 pack): Integration of the reciprocal function.

The script reads the values PRINTED in workspace/build/int2/l6i.html (tutor demos, your-turn items,
worked examples 33-37, Exercise 6I, the past-paper question) and in a_6i.html (lesson-example
answers, textbook answers, past-paper worked solution). Printed LaTeX is turned into sympy with the
shared helper int3_tex.py, and every result is recomputed independently:
  - every printed chain 'A = B = C' that contains a definite integral or a bracket [F]_a^b is checked
    side by side: each definite integral is evaluated by numerical quadrature (sympy/mpmath, 30
    digits), each bracket by substitution, and all sides must agree;
  - each lesson question's integral must open one of those chains in its answer, so the printed
    value is the value of the question's own integral; 'meaningless' items are checked by finding
    the zero of the denominator strictly between the limits;
  - indefinite integrals are checked by differentiating the printed primitive (log|u| differentiates
    to u'/u) and comparing with the printed integrand; definite answers by quadrature; decimals are
    rounded from the exact value; constants of integration are checked against the given point;
    Q14 is solved with sympy; the series answers of Q18 are recomputed.
It also checks the structure (questions 1-18, bands F 1-6, D 7-16, E 17-18), the past-paper block
(marks, time = 1.5 x marks rounded to 5 min, one hint, the label the same in both files, the
timed-practice note) and that every {{svg:...}} exists. A template must match exactly once; a missing
template FAILS.

Exit status 1 if anything fails. Run: python3 workspace/checks/int2_6i.py
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
t = sp.Symbol("t", real=True)
K = {s: sp.Symbol(s) for s in ("k", "m", "p", "q", "A", "s", "C")}
E = sp.E
FAILS, CNT = [], [0]
TOL = sp.Float("1e-18")


def report(ok, label, detail=""):
    CNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        raise LookupError(f"{where}: pattern matched {len(found)} times: {pattern[:70]!r}")
    return found[0]


# ---------------------------------------------------------------- TeX -> sympy
def prep(s):
    s = s.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "").replace("\\lt", "<").replace("\\gt", ">")
    s = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\\tfrac{\2}{\3})", s)   # 1\tfrac12 -> (1+1/2)
    s = s.replace("\\,", " ").replace("\\ ", " ").replace("\\phantom", "\\PH")
    s = re.sub(r"\\dfrac\{([^{}]*?)\s*d([xt])\}\{([^{}]*)\}", lambda m: "\\dfrac{" + (m.group(1).strip() or "1") + "}{" + m.group(3) + "} d" + m.group(2), s)
    return s.strip().rstrip(".,").strip()


def tex(s, extra=None):
    loc = dict(K)
    loc["t"] = t
    if extra:
        loc.update(extra)
    return T.tex(prep(s), loc)


LIM = r"(\{(?:[^{}]|\{[^{}]*\})*\}|-?\w)"


def unbrace(g):
    return g[1:-1] if g.startswith("{") else g


def num(v):
    return sp.N(v, 30)


def integrand(body):
    """'\\dfrac{4 dx}{5x-1}' or '\\dfrac{1}{x} dx' -> sympy integrand."""
    body = prep(body)
    body = re.sub(r"\\dfrac\{([^{}]*?)\s*d([xt])\}", lambda m: "\\dfrac{" + (m.group(1).strip() or "1") + "}", body)
    body = re.sub(r"\s*d[xt]\s*$", "", body.strip())
    return tex(body)


def side(s):
    """One side of a chain -> sympy, with definite integrals (numerical) and [F]_a^b brackets replaced by values."""
    s = prep(s)
    extra, n = {}, [0]

    def ph(val):
        name = f"Z{n[0]}Z"
        n[0] += 1
        extra[name] = val
        T.LOCAL.setdefault(name, sp.Symbol(name))
        return " " + name + " "

    def brk(mt):
        F = tex(mt.group(1))
        b_, a_ = tex(unbrace(mt.group(3))), tex(unbrace(mt.group(2)))
        return "(" + ph(F.subs(x, b_) - F.subs(x, a_)) + ")"

    s = re.sub(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, brk, s)

    def itg(mt):
        g = integrand(mt.group(3) + " dx")
        a_, b_ = tex(unbrace(mt.group(1))), tex(unbrace(mt.group(2)))
        return "(" + ph(sp.Integral(g, (x, a_, b_)).evalf(30)) + ")"

    s = re.sub(r"\\int_" + LIM + r"\^" + LIM + r"(.*?)\s*dx", itg, s)
    return tex(s, extra)


def clean_line(ln):
    ln = ln.replace("&amp;", "").replace("&", "")
    ln = re.split(r"\\quad|\\qquad|,\\ \\text|\\ \\text\{ of", ln)[0]
    return ln.strip()


def math_segments(html):
    return [a or b for a, b in re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", html, re.S)]


def chain_sides(seg):
    if "aligned" in seg:
        seg = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", seg)
        seg = "".join(clean_line(ln) for ln in seg.split("\\\\"))
    else:
        seg = clean_line(seg)
    sides = [q.strip() for q in T.split_top(prep(seg), "=")]
    return [q for q in sides if q and not q.startswith("\\PH")]


CHAINS = []   # (first side text, last value, where)


def all_chains(html, where):
    cnt = 0
    for seg in math_segments(html):
        if not re.search(r"\\int_|\\Big\[", seg) or "=" not in seg:
            continue
        if any(k in seg for k in ("u'", "f(x)", "f'(x)", "\\doteq", "\\cdots", "t^{2n", "dt", "\\begin{cases}", "\\le")):
            continue  # formula statements and the Q18 / Q16 statements (not evaluations)
        sides = chain_sides(seg)
        if len(sides) < 2:
            continue
        cnt += 1
        try:
            vals = [num(side(q)) for q in sides]
            ok = all(v.is_number and abs(v - vals[0]) < TOL for v in vals)
            report(ok, f"{where} chain {cnt}", " | ".join(sides)[:160] + f"  = {vals[-1]:.12g}" if ok else str(vals))
            CHAINS.append((re.sub(r"\s+", "", sides[0]), vals[-1], where, seg))
        except Exception as err:  # noqa: BLE001
            report(False, f"{where} chain {cnt}", f"ERROR {err} in {seg[:90]!r}")
    return cnt


def starts_chain(qtex, block_where, value=None):
    """A chain in the answers (or worked example) must start with the question's integral."""
    key = re.sub(r"\s+", "", prep(qtex))
    hits = [c for c in CHAINS if c[2] == block_where and c[0].replace("\\left", "") == key]
    return hits


def mean(qint, text, where):
    """'meaningless' item: the denominator has a zero strictly between the limits, named in the text."""
    m = re.match(r"\\int_" + LIM + r"\^" + LIM + r"(.*)", prep(qint))
    a_, b_ = tex(unbrace(m.group(1))), tex(unbrace(m.group(2)))
    g = integrand(m.group(3))
    den = sp.denom(sp.together(g))
    roots = [r for r in sp.solve(den, x) if r.is_real and a_ < r < b_]
    k = grab(text, r"asymptote at \\\(x=(.*?)\\\)", where)
    report(len(roots) == 1 and sp.simplify(tex(k) - roots[0]) == 0, f"{where} meaningless (asymptote inside)", f"{qint} : x = {k}")


def deriv_ok(F, f, syms=()):
    """d/dx F == f, with log|u| differentiated as u'/u."""
    F = F.replace(sp.Abs, lambda a: a)
    d = sp.simplify(sp.diff(F, x) - f)
    if d == 0:
        return True
    for xv in (sp.Rational(7, 3), sp.Rational(13, 5), sp.Rational(31, 7)):
        sub = {x: xv}
        sub.update({s_: sp.Rational(3 + i, 2) for i, s_ in enumerate(syms)})
        if abs(num(d.subs(sub))) > TOL:
            return False
    return True


# ---------------------------------------------------------------- files and blocks
les, ans = read("l6i.html"), read("a_6i.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1]
CON = {}
for c in range(1, 6):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    blocks = re.findall(r'<div class="ex (demo|attempt|worked)"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[c] = {"worked": []}
    for kind, tag, body in blocks:
        if kind == "worked":
            CON[c]["worked"].append((tag, body))
        else:
            CON[c][kind] = body
report([[t_ for t_, _ in CON[c]["worked"]] for c in range(1, 6)] == [[f"Worked example {n}"] for n in range(33, 38)],
       "worked examples", "textbook Examples 33-37 in Concepts 1-5")
report(all("demo" in CON[c] and "attempt" in CON[c] for c in range(1, 6)), "every concept has a tutor demo and a your turn")

parts_ans = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
report(len(parts_ans) == 2 and ans.count("{{ahead:Lesson 6I | Integration of the reciprocal function}}") == 2, "answers headings and sections")
BLK = dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts_ans[0], re.S))
PPA = parts_ans[1]
report(set(BLK) == {f"C{i}" for i in range(1, 6)} | {str(i) for i in range(1, 19)}, "answer blocks", "C1-C5 and Q1-18")

for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}")


def halves(block):
    a_, b_ = block.split("<b>Your turn.</b>")
    return a_, b_


# ---------------------------------------------------------------- generic chains
for c in range(1, 6):
    for i, (tag, body) in enumerate(CON[c]["worked"]):
        all_chains(body, f"WE{32 + c}")
    all_chains(teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split('<div class="ex ')[0], f"C{c} box")
for c in range(1, 6):
    d_, y_ = halves(BLK[f"C{c}"])
    all_chains(d_, f"C{c} demo")
    all_chains(y_, f"C{c} your turn")
all_chains(PPA, "PP")
report(len(CHAINS) >= 20, "chains found", str(len(CHAINS)))


def q_parts(block):
    return dict(re.findall(r'<span class="pl">(\w+)</span>(.*?)</span>(?=<span><span class="pl">|</div>)', block, re.S))


def q_integral(txt):
    return grab(txt, r"\\\((\\displaystyle\\int.*?)\\\)", "question integral").replace("\\displaystyle", "")


# lesson examples: each question's integral opens a checked chain in its answer, or is 'meaningless'
LESSON = [(1, "demo", "C1 demo"), (1, "attempt", "C1 your turn"), (2, "demo", "C2 demo"), (2, "attempt", "C2 your turn"),
          (3, "demo", "C3 demo"), (3, "attempt", "C3 your turn")]
for c, kind, where in LESSON:
    qb = CON[c][kind]
    ab = halves(BLK[f"C{c}"])[0 if kind == "demo" else 1]
    if c == 1:
        items = {lt: grab(qb, rf"<b>{lt}</b> Find(?: the definite integral)? \\\((\\displaystyle\\int.*?)\\\)", f"{where} {lt}").replace("\\displaystyle", "") for lt in "ac"}
    else:
        items = {lt: q_integral(b_) for lt, b_ in q_parts(qb).items()}
    for lt, qi in items.items():
        if "meaningless" in (re.search(rf"<b>{lt}</b>(.*?)(?=<b>[a-d]</b>|$)", ab, re.S).group(1)):
            mean(qi, re.search(rf"<b>{lt}</b>(.*?)(?=<b>[a-d]</b>|$)", ab, re.S).group(1), f"{where} {lt}")
            continue
        hits = starts_chain(qi, where)
        report(len(hits) == 1, f"{where} {lt}: answer chain starts with the question integral", qi + (f" = {hits[0][1]:.10g}" if hits else ""))

# worked examples 33-35: the textbook integrals open the printed chains
for c, where in ((1, "WE33"), (2, "WE34"), (3, "WE35")):
    qb = CON[c]["worked"][0][1]
    items = {"a": grab(qb, r"<b>a</b> Find the definite integral \\\((\\displaystyle\\int.*?)\\\)", "WE33 a").replace("\\displaystyle", "")} if c == 1 \
        else {lt: q_integral(b_) for lt, b_ in q_parts(qb.split('<div class="sol-label">')[0]).items()}
    sol = qb.split('<div class="sol-label">')[1]
    for lt, qi in items.items():
        if lt == "c":
            mean(qi, re.search(r"<b>c</b>(.*?)</p>", sol, re.S).group(1), f"{where} c")
        elif where == "WE35" and lt == "b":
            # the chain is split over two displays: the first display rewrites the integral, the second continues it
            d1, d2 = re.findall(r"\\\[(.*?)\\\]", sol.split("<p><b>b</b></p>")[1], re.S)[:2]
            s1 = chain_sides(d1)
            v = [num(side(q)) for q in s1] + [num(side(q)) for q in chain_sides(d2)]
            truth = num(sp.Integral(x / (9 - x ** 2), (x, 4, 5)).evalf(30))
            report(re.sub(r"\s+", "", s1[0]) == re.sub(r"\s+", "", prep(qi)) and all(abs(w - truth) < TOL for w in v), "WE35 b two-display chain", f"{len(v)} sides = {truth:.10g}")
        else:
            hits = starts_chain(qi, where)
            report(len(hits) == 1, f"{where} {lt}: chain starts with the textbook integral", qi)

# WE33 b, C1 b: decimals and the rectangle bounds
try:
    b33 = CON[1]["worked"][0][1]
    report(grab(b33, r"dx\\doteq([\d.]+)\\\)", "WE33 b") == f"{float(sp.log(2)):.3f}", "WE33 b log 2 = 0.693")
    for who, qb, ab in (("demo", CON[1]["demo"], halves(BLK["C1"])[0]), ("your turn", CON[1]["attempt"], halves(BLK["C1"])[1])):
        lo, b_, hi = grab(qb, r"\\ (\\tfrac\d\d)\\lt\\displaystyle\\int_1\^(\d)\\dfrac1x\\,dx\\lt(\d)\\\)", f"C1 {who} bounds")
        b_ = int(b_)
        dec = grab(ab, r"=\\log_e\d\\doteq([\d.]+)\\\)", f"C1 {who} decimal")
        report(dec == f"{float(sp.log(b_)):.3f}", f"C1 {who} b decimal", dec)
        report(sp.simplify(tex(lo) - sp.Rational(b_ - 1, b_)) == 0 and int(hi) == b_ - 1 and tex(lo) < sp.log(b_) < int(hi),
               f"C1 {who} b rectangle bounds (b-a)/b and (b-a)", f"{lo} < log {b_} < {hi}")
        areas = re.findall(r"its area is \\\((.*?)\\\)", ab)
        report(len(areas) == 2 and all(sp.simplify(tex(T.split_top(prep(z), '=')[0]) - tex(T.split_top(prep(z), '=')[-1])) == 0 for z in areas)
               and sp.simplify(tex(T.split_top(prep(areas[0]), '=')[-1]) - tex(lo)) == 0 and tex(T.split_top(prep(areas[1]), '=')[-1]) == int(hi),
               f"C1 {who} b rectangle areas", " ; ".join(areas))
except Exception as err:  # noqa: BLE001
    report(False, "C1 b / WE33 b", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 4: find the function
def find_fn(qtext, atext, where, given_pt=(0, 0)):
    fp = tex(grab(qtext, r"f'\(x\)=(\\dfrac\{\d\}\{\d-x\})\\\)", f"{where} f'"))
    xs = int(grab(qtext, r"Hence find \\\(f\((\d)\)\\\)", f"{where} point"))
    prim = grab(atext, r"Taking the primitive,\s*\\\(f\(x\)=(.*?)\\\)", f"{where} primitive")
    Cv = grab(atext, r"so \\\(C=(.*?)\\\)", f"{where} C")
    fin = grab(atext, r"Hence \\\(f\(x\)=(.*?)\\\)", f"{where} f")
    val = grab(atext, rf"\\\(f\({xs}\)=(.*?)\\\)", f"{where} value")
    F = tex(prim, {"C": sp.Integer(0)})
    f = tex(fin)
    asym = sp.solve(sp.denom(sp.together(fp)), x)[0]
    ok = deriv_ok(F, fp) and deriv_ok(f, fp) and sp.simplify(f.subs(x, given_pt[0]) - given_pt[1]) == 0
    ok = ok and sp.simplify(tex(Cv) - (given_pt[1] - F.subs(x, given_pt[0]))) == 0
    vals = [tex(z) for z in T.split_top(prep(val), "=")]
    ok = ok and all(sp.simplify(v - f.subs(x, xs)) == 0 for v in vals) and (given_pt[0] - asym) * (xs - asym) > 0
    report(ok, f"{where}", f"f = {fin}; f({xs}) = {val}")


try:
    for who, qb, ab in (("C4 demo", CON[4]["demo"], halves(BLK["C4"])[0]), ("C4 your turn", CON[4]["attempt"], halves(BLK["C4"])[1])):
        find_fn(qb, ab, who)
    b36 = CON[4]["worked"][0][1]
    fp = 2 / (3 - x)
    f36 = tex(grab(b36, r"<td>Hence</td><td>\\\(f\(x\)=(.*?)\\\)", "WE36 f"))
    report(deriv_ok(f36, fp) and f36.subs(x, 0) == 0 and sp.simplify(f36.subs(x, 2) - 2 * sp.log(3)) == 0
           and "\\(f(x)=-2\\ln|3-x|+C,\\)" in b36 and "\\(C=2\\ln3.\\)" in b36 and "\\(\\phantom{f(2)}=2\\ln3.\\)" in b36, "WE36 f and f(2) = 2 ln 3")
except Exception as err:  # noqa: BLE001
    report(False, "Concept 4", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 5: primitive of log x
try:
    for who, ab in (("C5 demo", halves(BLK["C5"])[0]), ("C5 your turn", halves(BLK["C5"])[1])):
        prims = re.findall(r"\\int\\log_ex\\,dx=(x\\log_ex-x)\+C", ab)
        report(len(prims) == 1 and deriv_ok(tex(prims[0]), sp.log(x)), f"{who} primitive x log x - x", str(prims))
    d5 = halves(BLK["C5"])[0]
    disp = re.findall(r"\\\[(.*?)\\\]", d5, re.S)[0]
    sides = chain_sides(disp)
    vals = [tex(q.replace("\\dfrac{d}{dx}(x\\log_ex-x)", "LHS"), {"LHS": sp.diff(x * sp.log(x) - x, x)}) for q in sides]
    report(all(sp.simplify(v - sp.log(x)) == 0 for v in vals), "C5 demo a derivative chain", " = ".join(sides))
    for who, ab, lim in (("C5 demo", halves(BLK["C5"])[0], (1, E ** 2)), ("C5 your turn", halves(BLK["C5"])[1], (E, E ** 2))):
        hits = [c_ for c_ in CHAINS if c_[2] == who]
        truth = num(sp.integrate(sp.log(x), (x, *lim)))
        report(len(hits) == 1 and abs(hits[0][1] - truth) < TOL, f"{who} c value", f"{truth}")
    q5 = CON[5]["demo"] + CON[5]["attempt"]
    report("\\int_1^{e^2}\\log_ex\\,dx" in q5 and "\\int_e^{e^2}\\log_ex\\,dx" in q5, "C5 question limits")
    b37 = CON[5]["worked"][0][1]
    disp = re.findall(r"\\\[(.*?)\\\]", b37, re.S)[0]
    sides = chain_sides(disp)
    vals = [tex(q.replace("\\dfrac{d}{dx}(x\\log_ex)", "LHS").replace("vu'+uv'", "LHS"), {"LHS": sp.diff(x * sp.log(x), x)}) for q in sides]
    report(all(sp.simplify(v - (1 + sp.log(x))) == 0 for v in vals), "WE37 a derivative chain", " = ".join(sides))
    report(deriv_ok(x * sp.log(x) - x, sp.log(x)) and "\\int\\log_ex\\,dx=x\\log_ex-x+C" in b37, "WE37 b primitive")
except Exception as err:  # noqa: BLE001
    report(False, "Concept 5", f"ERROR {err}")

# ---------------------------------------------------------------- textbook homework
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 19)], "textbook questions 1-18", str(sorted(TQ, key=int)))
bands = hw.split("{{band:D}}")
report(bands[0].count('class="q-num"') == 6 and bands[1].split("{{band:E}}")[0].count('class="q-num"') == 10
       and bands[1].split("{{band:E}}")[1].count('class="q-num"') == 2, "bands", "F: Q1-6, D: Q7-16, E: Q17-18 (as the textbook)")


def aparts(n):
    return dict(re.findall(r'<span class="ap6i"><b>(\w+)</b> (.*?)</span>', BLK[n], re.S))


def first(s):
    return re.findall(r"\\\((.*?)\\\)", s, re.S)


def qmath(n):
    out = {}
    for lt, body in q_parts(TQ[n]).items():
        ms = first(body)
        out[lt] = ms[0].replace("\\displaystyle", "") if ms else body
    return out


SYMS = tuple(K[s_] for s_ in ("k", "m", "p", "q", "A", "s"))


def check_indef(n, from_int=True):
    qs, an = qmath(n), aparts(n)
    for lt, qt in qs.items():
        if lt not in an:
            continue
        try:
            if from_int:
                m = re.match(r"\\int(?!_)(.*)", qt.strip())
                if not m:
                    continue
                f = integrand(m.group(1))
            else:
                f = tex(qt)
            F = tex(first(an[lt])[0], {"C": sp.Integer(0), "t": K["s"] if n == "8" else t})
            if n == "8":
                f = f.subs(t, K["s"]) if f.has(t) else f
            report("+C" in first(an[lt])[0].replace(" ", "") and deriv_ok(F, f, SYMS), f"Q{n}{lt} d/dx(primitive) = integrand", f"{qt} -> {first(an[lt])[0]}")
        except Exception as err:  # noqa: BLE001
            report(False, f"Q{n}{lt}", f"ERROR {err}")


K["t"] = sp.Symbol("t")   # Q8(d) uses the constant t
check_indef("1")
check_indef("2")
check_indef("6", from_int=False)
check_indef("7", from_int=False)
check_indef("8")
check_indef("12")
K.pop("t")
report("never negative" in BLK["7"] and "parts <b>g</b> and <b>i</b>" in TQ["7"] and all(num(e_.subs(x, v)) > 0 for e_ in (1 + sp.exp(x), sp.exp(x) + sp.exp(-x)) for v in (-5, 0, 5)),
       "Q7 g and i denominators never negative")
report(sorted(q_parts(TQ["7"])) == list("abcdgi") and sorted(aparts("7")) == list("abcdgi"), "Q7 parts e, f, h omitted (numerator not the derivative)", str(sorted(q_parts(TQ["7"]))))
for lt, qt in qmath("7").items():
    nu_, de_ = re.match(r"\\dfrac\{(.*)\}\{(.*)\}$", qt.strip()).groups()
    report(sp.simplify(sp.diff(tex(de_), x) - tex(nu_)) == 0, f"Q7{lt} numerator is exactly the derivative of the denominator", qt)


def check_def(n, sf=None):
    qs, an = qmath(n), aparts(n)
    for lt, qt in qs.items():
        if not qt.strip().startswith("\\int_"):
            continue
        try:
            txt = an[lt]
            if "meaningless" in txt:
                mean(qt, txt, f"Q{n}{lt}")
                continue
            main = first(txt)[0]
            pieces = T.split_top(prep(main.replace("\\doteq", "=")), "=")
            truth = num(side(qt + "=0".replace("=0", "")) if False else side(qt))
            exact = [num(tex(z)) for z in pieces[:-1]] if sf else [num(tex(z)) for z in pieces]
            ok = all(abs(v - truth) < TOL for v in exact)
            if sf:
                d = pieces[-1].strip()
                ok = ok and float(d) == float(f"{float(truth):.{sf}g}")
            report(ok, f"Q{n}{lt}", f"{qt} = {main}  (quad {float(truth):.8g})")
        except Exception as err:  # noqa: BLE001
            report(False, f"Q{n}{lt}", f"ERROR {err}")


check_def("3")
check_def("4", sf=4)
check_def("5")
check_def("12")
check_def("14") if False else None

# Q9, Q10: f from f' and one value
try:
    an = aparts("9")
    for lt, qt in q_parts(TQ["9"]).items():
        fp_t, pt_t = grab(qt, r"\\\(f'\(x\)=(.*?)\\\) and \\\(f\(1\)=(.*?)\\\)", f"Q9{lt}")
        fp, f1 = tex(fp_t), tex(pt_t)
        fx, f2 = first(an[lt])
        F = tex(fx.split("=", 1)[1])
        v2 = T.split_top(prep(f2), "=")
        report(deriv_ok(F, fp) and sp.simplify(F.subs(x, 1) - f1) == 0 and sp.simplify(tex(v2[1]) - F.subs(x, 2)) == 0, f"Q9{lt}", f"{fx}; {f2}")
    an = aparts("10")
    for lt, fname, pv in (("a", "f", (1, sp.Rational(3, 2))), ("b", "g", (2, -3 * sp.log(2)))):
        qt = q_parts(TQ["10"])[lt]
        fp = tex(grab(qt, r"is \\\((\\dfrac\{.*?\}\{.*?\})\\\)", f"Q10{lt}"))
        F = tex(first(an[lt])[0].split("=", 1)[1])
        report(deriv_ok(F, fp) and sp.simplify(F.subs(x, pv[0]) - pv[1]) == 0 and f"{fname}({pv[0]})" in qt.replace("\\", ""), f"Q10{lt}", first(an[lt])[0])
except Exception as err:  # noqa: BLE001
    report(False, "Q9-Q10", f"ERROR {err}")

# Q11
try:
    an, qp = aparts("11"), q_parts(TQ["11"])
    ya, xa = first(an["a"])
    Y = tex(ya.split("=", 1)[1])
    report(deriv_ok(Y, 1 / (4 * x)) and sp.simplify(Y.subs(x, E ** 2) - 1) == 0 and sp.simplify(Y.subs(x, tex(xa.split("=")[1]))) == 0
           and "y'=\\dfrac{1}{4x}" in qp["a"] and "x=e^2" in qp["a"], "Q11a", f"{ya}; {xa}")
    Y = tex(first(an["b"])[0].split("=", 1)[1])
    report(deriv_ok(Y, 2 / (x + 1)) and Y.subs(x, 0) == 1, "Q11b", first(an["b"])[0])
    yc, y0 = first(an["c"])
    Y = tex(yc.split("=", 1)[1])
    report(deriv_ok(Y, (2 * x + 5) / (x ** 2 + 5 * x + 4)) and sp.simplify(Y.subs(x, 1) - 1) == 0
           and sp.simplify(tex(y0.split("=")[1]) - Y.subs(x, 0)) == 0, "Q11c", f"{yc}; {y0}")
    fam, part, y2 = first(an["d"])
    Fm = tex(fam.split("=", 1)[1], {"C": sp.Integer(0)})
    Yp = tex(part.split("=", 1)[1])
    report(deriv_ok(Fm, (2 + x) / x) and deriv_ok(Yp, (2 + x) / x) and Yp.subs(x, 1) == 1 and sp.simplify(tex(y2.split("=")[1]) - Yp.subs(x, 2)) == 0
           and "+C" in fam, "Q11d", f"{fam}; {part}; {y2}")
    fe, ve = first(an["e"])
    Fe = tex(fe.split("=", 1)[1])
    fpe = sp.diff(Fe.replace(sp.Abs, lambda a: a), x)
    report(sp.simplify(sp.diff(fpe, x) - 1 / x ** 2) == 0 and fpe.subs(x, 1) == 0 and Fe.subs(x, 1) == 3
           and sp.simplify(tex(ve.split("=")[1]) - Fe.subs(x, E)) == 0, "Q11e", f"{fe}; {ve}")
except Exception as err:  # noqa: BLE001
    report(False, "Q11", f"ERROR {err}")

# Q13
try:
    an = aparts("13")
    ms = first(an["a"])
    report(sp.simplify(tex(ms[0].split("=")[1]) - sp.diff(x * sp.log(x) - x, x)) == 0, "Q13a(i)", ms[0])
    report(deriv_ok(tex(ms[1], {"C": sp.Integer(0)}), sp.log(x)) and sp.simplify(tex(ms[2]) - sp.integrate(sp.log(x), (x, sp.sqrt(E), E))) == 0, "Q13a(ii)", f"{ms[1]}; {ms[2]}")
    ms = first(an["b"])
    report(sp.simplify(tex(ms[0].split("=")[1]) - sp.diff(2 * x ** 2 * sp.log(x) - x ** 2, x)) == 0, "Q13b(i)", ms[0])
    report(deriv_ok(tex(ms[1], {"C": sp.Integer(0)}), x * sp.log(x)) and "+C" in ms[1]
           and sp.simplify(tex(ms[2]) - sp.integrate(x * sp.log(x), (x, E, 2))) == 0, "Q13b(ii)", f"{ms[1]}; {ms[2]}")
    ms = first(an["c"])
    report(sp.simplify(tex(ms[0]) - sp.diff(sp.log(x) ** 2, x)) == 0 and sp.simplify(tex(ms[1]) - sp.integrate(sp.log(x) / x, (x, sp.sqrt(E), E))) == 0, "Q13c", f"{ms[0]}; {ms[1]}")
    ms = first(an["d"])
    d1 = T.split_top(prep(ms[0]), "=")
    report(sp.simplify(tex(d1[1]) - sp.diff(sp.log(sp.log(x)), x)) == 0 and deriv_ok(tex(ms[1], {"C": sp.Integer(0)}), 1 / (x * sp.log(x)))
           and deriv_ok(tex(ms[3], {"C": sp.Integer(0)}), 1 / (x * sp.log(x))), "Q13d", f"{ms[0]}; {ms[1]}; {ms[3]}")
    qp = q_parts(TQ["13"])
    report("\\int_{\\sqrt e}^e\\log_ex\\,dx" in qp["a"] and "\\int_e^2x\\log_ex\\,dx" in qp["b"] and "\\int_{\\sqrt e}^e\\dfrac{\\log_ex}{x}\\,dx" in qp["c"], "Q13 question limits")
except Exception as err:  # noqa: BLE001
    report(False, "Q13", f"ERROR {err}")

# Q14: solve for a
try:
    an, qs = aparts("14"), qmath("14")
    a = sp.Symbol("a", real=True)
    for lt, qt in qs.items():
        lhs, rhs = T.split_top(prep(qt), "=")
        m = re.match(r"\\int_" + LIM + r"\^" + LIM + r"(.*)", lhs)
        lo, hi = unbrace(m.group(1)), unbrace(m.group(2))
        F = sp.log(sp.Abs(x))
        expr = F.subs(x, a if hi == "a" else tex(hi)) - F.subs(x, a if lo == "a" else tex(lo)) - tex(rhs)
        other = tex(lo if hi == "a" else hi)
        sol = [r for r in sp.solve(expr.subs(sp.Abs(a), sp.sign(other) * a), a) if sp.sign(r) == sp.sign(other)]
        got = tex(first(an[lt])[0].split("=")[1])
        report(len(sol) == 1 and sp.simplify(got - sol[0]) == 0, f"Q14{lt}", f"{qt}: a = {got}")
except Exception as err:  # noqa: BLE001
    report(False, "Q14", f"ERROR {err}")

# Q15, Q16, Q17
try:
    an = aparts("15")
    report("\\int\\dfrac{e^x}{e^x+1}\\,dx" in TQ["15"] and "\\int_1^e\\Big(x+\\dfrac{1}{x^2}\\Big)^2\\,dx" in TQ["15"] and "x\\,e^x=e^{x+\\log_ex}" in TQ["15"], "Q15 question text")
    report(deriv_ok(tex(first(an["a"])[0], {"C": sp.Integer(0)}), sp.exp(x) / (sp.exp(x) + 1)), "Q15a", first(an["a"])[0])
    report(abs(num(tex(first(an["b"])[0])) - num(sp.Integral((x + 1 / x ** 2) ** 2, (x, 1, E)).evalf(30))) < TOL, "Q15b", first(an["b"])[0])
    report(sp.simplify(tex(first(an["c"])[0].split("=")[1]) - sp.diff(x * sp.exp(x), x)) == 0
           and sp.simplify(sp.exp(x + sp.log(x)) - x * sp.exp(x)) == 0, "Q15c", first(an["c"])[0])
    C1 = sp.Symbol("C1")
    C2 = sp.solve(sp.Eq(sp.log(5 * x) / 5 + sp.Symbol("C2"), sp.log(x) / 5 + C1), sp.Symbol("C2"))
    report("\\(C_2=C_1-\\tfrac15\\log_e5\\)" in BLK["16"] and sp.simplify(sp.expand_log(C2[0], force=True) - (C1 - sp.log(5) / 5)) == 0, "Q16 C2 = C1 - (1/5) log 5")
    pw = grab(BLK["17"], r"\\begin\{cases\}(.*?)\\end\{cases\}", "Q17")
    rows = [r_.split("&amp;") for r_ in pw.split("\\\\")]
    br = {(">" if "\\gt0" in r_[1] else "<"): tex(r_[0]) for r_ in rows}
    report(set(br) == {">", "<"} and sp.simplify(sp.diff(br[">"], x) - 1 / x) == 0 and sp.simplify(sp.diff(br["<"], x) - 1 / x) == 0
           and br[">"].subs(x, 1) == 1 and br["<"].subs(x, -1) == 2 and "(-1,2)" in TQ["17"] and "(1,1)" in TQ["17"], "Q17 branches through (1,1) and (-1,2)", pw)
except Exception as err:  # noqa: BLE001
    report(False, "Q15-Q17", f"ERROR {err}")

# Q18 series answers
try:
    an = aparts("18")
    d_ = first(an["d"])
    report(d_[0] == "\\log_e\\tfrac32\\doteq0.41" and f"{float(sp.log(sp.Rational(3, 2))):.2f}" == "0.41"
           and abs(sum((-1) ** (k + 1) * sp.Rational(1, 2) ** k / k for k in range(1, 12)) - sp.log(sp.Rational(3, 2))) < 0.005, "Q18d(i)", d_[0])
    report(d_[1].replace(" ", "") == "\\log_e2=1-\\tfrac12+\\tfrac13-\\tfrac14+\\cdots", "Q18d(ii) alternating harmonic series", d_[1])
    e_ = first(an["e"])
    report(all(sp.series(sp.log(1 - x), x, 0, 5).removeO().coeff(x, k) == -sp.Rational(1, k) for k in range(1, 5))
           and "-x-\\dfrac{x^2}{2}-\\dfrac{x^3}{3}-\\dfrac{x^4}{4}" in e_[0] and e_[1].endswith(f"\\doteq{float(sp.log(sp.Rational(1, 2))):.2f}"), "Q18e", " ; ".join(e_))
    f_ = first(an["f"])
    xv = tex(f_[0].split("=")[1])
    s5 = 2 * sum(xv ** (2 * k + 1) / (2 * k + 1) for k in range(0, 12))
    report(sp.simplify((1 + xv) / (1 - xv) - 3) == 0 and f_[1] == f"\\log_e3\\doteq{float(sp.log(3)):.5g}" and abs(float(s5) - float(sp.log(3))) < 5e-6, "Q18f", " ; ".join(f_))
except Exception as err:  # noqa: BLE001
    report(False, "Q18", f"ERROR {err}")

# ---------------------------------------------------------------- past paper
try:
    PPS = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">(PP \d)</span>(.*?)</span><span class="mk">(\d+) marks</span></div>(.*?)(?=<div class="pp">|</div>\s*</div>\s*<p>The school)', ppl, re.S)
    PPAS = re.findall(r'<div class="ppa"[^>]*><div class="pp-src"><span><span class="pn">(PP \d)</span>(.*?)</span></div>', PPA, re.S)
    report(len(PPS) == 1 and len(PPAS) == 1 and PPS[0][1] == PPAS[0][1], "one past-paper question, label the same in both files")
    lab = PPS[0][1].replace("&nbsp;", " ").replace('<span style="white-space:nowrap">', "").replace("</span>", "")
    report(lab.startswith("North Sydney Boys High School, 2022, HSC Course Assessment Task 3-Trial Examination, Mathematics")
           and lab.endswith("Extension 1, Q13(a)(i)"), "PP 1 label", lab[:120])
    body = PPS[0][3]
    report(body.count('<div class="hint">') == 1 and PPS[0][2] == "2" and "<b>Hint:</b> what is being integrated here?</div>" in body, "PP 1 marks 2 and one hint")
    intro = grab(ppl, r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", "pp intro")
    report(int(intro[1]) == 2 and int(intro[0]) == 5 * max(1, round(1.5 * 2 / 5)), "PP time and marks", f"{intro}")
    qi = grab(body, r"Find \\\((\\displaystyle\\int.*?)\\\)", "PP integrand")
    f = integrand(re.match(r"\\displaystyle\\int(.*)", qi).group(1))
    report(sp.simplify(f - (1 - sp.log(x)) / (x * sp.log(x))) == 0, "PP integrand as printed on the paper", qi)
    disp = re.findall(r"\\\[(.*?)\\\]", PPA, re.S)
    split = chain_sides(disp[0])
    report(all(sp.simplify(tex(q) - f) == 0 for q in split), "PP split into two fractions", " = ".join(split))
    fin = chain_sides(disp[-1])[-1]
    Fp = tex(fin, {"C": sp.Integer(0)})
    report(deriv_ok(Fp, f), "PP primitive differentiates to the integrand", fin)
    alt = grab(PPA, r"written as \\\((.*?)\\\)\.", "PP log-law form")
    Fa = tex(alt, {"C": sp.Integer(0)})
    report(all(abs(num((Fa - Fp).subs(x, v))) < TOL for v in (sp.Rational(1, 2), 2, 5)), "PP log-law form equals the primitive", alt)
    note = grab(ppl, r"do Questions (.*?) above in (\d+) minutes", "practice note")
    refs = re.findall(r"(\d+)\((\w)\)", note[0])
    report(bool(refs) and all(n in TQ and f'<span class="pl">{lt}</span>' in TQ[n] for n, lt in refs), "timed-practice references", note[0])
except Exception as err:  # noqa: BLE001
    report(False, "past paper", f"ERROR {err}")

print(f"\n{CNT[0]} checks, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
