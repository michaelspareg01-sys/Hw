"""Check of Lesson 7D (Integration Part 2 pack): Integrating the trigonometric functions.

The script reads the values PRINTED in workspace/build/int2/l7d.html (concept boxes, tutor demos,
your-turn items, worked examples 16-22, the tips, Exercise 7D, the past-paper mini exam) and in
a_7d.html (lesson-example answers, textbook answers, past-paper worked solutions). Printed LaTeX is
turned into sympy with the shared helper int3_tex.py, and every result is recomputed independently:
  - every printed display chain 'A = B = C ...' that starts with an integral, a bracket [F]_a^b or a
    numeric expression is checked line by line: definite integrals by numerical quadrature (mpmath),
    brackets by substitution, arithmetic by evaluation; indefinite chains are checked by
    differentiating every side (each side's derivative must equal the integrand at sample points);
  - each lesson question (demo, your turn, worked example, past paper) is matched with the chain in
    the solutions that starts with the same integral, and its last line must equal the value found
    here with sympy.integrate;
  - the exercise questions are compared with an independent transcription of the textbook (typed in
    this script as python/sympy), and every printed textbook answer is recomputed: primitives by
    differentiation, definite integrals by sympy and quadrature, functions from their derivative and
    a known value, the parametric items (n, a, b, u, v) at several values;
  - multiple-choice past papers: every option is differentiated and exactly one must match;
  - structure: worked examples 16-22 (no 23), questions 1-22 with bands F 1-8, D 9-19, E 20-22, the
    past-paper block (marks, time = 1.5 x marks rounded to 5 min, one neutral hint per question,
    labels the same in both files), every {{svg:...}} exists.
A template must match exactly once; a missing template FAILS. Exit status 1 if anything fails.
Run: python3 workspace/checks/int2_7d.py
"""
import os
import random
import re
import sys

import mpmath as mp
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

SRC = os.environ.get("INT2_SRC", os.path.join(HERE, "..", "build", "int2"))
x = T.x
pi = sp.pi
n_, a_, b_, u_, v_, k_, A_, C_, D_ = sp.symbols("n a b u v k A C D")
T.FUNCS["cot"] = "cot"
T.FUNCS["csc"] = "csc"
T.LOCAL["cot"] = sp.cot
T.LOCAL["csc"] = sp.csc
EXTRA = {"C": sp.Integer(0), "D": sp.Integer(0), "c": sp.Integer(0), "k": k_, "A": A_, "n": n_}
FAILS, CNT = [], [0]


def report(ok, label, detail=""):
    CNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + str(detail).replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- TeX -> sympy
def prep(t_):
    t_ = t_.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "")
    t_ = re.sub(r"\\phantom\{[^{}]*\}", "", t_)
    t_ = re.sub(r"\\text\{[^{}]*\}", "", t_)
    t_ = t_.replace("\\operatorname{cosec}", "\\csc ")
    t_ = re.sub(r"\\(sin|cos|tan|sec)\\pi ([a-z])", r"\\\1(\\pi \2)", t_)
    t_ = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", t_)
    t_ = re.sub(r"\\ln\\(sin|cos)(\\tfrac\{[^{}]*\}\{[^{}]*\})", r"\\ln(\\\1\2)", t_)   # ln sin(pi/4)
    t_ = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\\tfrac{\2}{\3})", t_)   # mixed numbers
    t_ = t_.replace("\\div", "/").replace("\\,", " ").replace("\\ ", " ").replace("d\\theta", " dx").replace("\\theta", " x").replace("dx", " dx")
    return t_.strip().rstrip(".,").strip()


def tex(t_, extra=None):
    loc = dict(EXTRA)
    if extra:
        loc.update(extra)
    return T.tex(prep(t_), loc)


LIM = r"(\{(?:[^{}]|\{[^{}]*\})*\}|\\pi|-?\w)"


def unbrace(g):
    return g[1:-1] if g.startswith("{") else g


def side(t_):
    """One side -> sympy. Definite integrals become numbers (quadrature), brackets are substituted,
    indefinite integrals become sympy Integral objects (their derivative is the integrand)."""
    t_ = prep(t_).replace("d x", "dx")
    extra, cnt = {}, [0]

    def ph(val):
        name = f"Z{cnt[0]}Z"
        cnt[0] += 1
        extra[name] = val
        T.LOCAL.setdefault(name, sp.Symbol(name))
        return " " + name + " "

    def brk(mt):
        F = tex(mt.group(1))
        return "(" + ph(F.subs(x, tex(unbrace(mt.group(3)))) - F.subs(x, tex(unbrace(mt.group(2))))) + ")"

    t_ = re.sub(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, brk, t_)

    def itg(mt):
        g = tex(mt.group(3))
        if mt.group(1):
            lo, hi = tex(unbrace(mt.group(1))), tex(unbrace(mt.group(2)))
            return "(" + ph(("DEF", g, lo, hi)) + ")"
        return "(" + ph(sp.Integral(g, x)) + ")"

    t_ = re.sub(r"\\int(?:_" + LIM + r"\^" + LIM + r")?(.*?)\s*dx", itg, t_)
    # definite integrals are kept as tuples until evaluation (they may contain the symbol k)
    expr = tex(t_, {k2: (sp.Symbol(k2) if isinstance(v2, tuple) else v2) for k2, v2 in extra.items()})
    defs = {sp.Symbol(k2): v2 for k2, v2 in extra.items() if isinstance(v2, tuple)}
    return expr, defs


def quad(g, lo, hi):
    f = sp.lambdify(x, g, "mpmath")
    return mp.quad(f, [float(lo), float(hi)])


def numval(expr, defs, at):
    """Numeric value of a side with symbols substituted from 'at' (x, k, ...)."""
    e = expr
    for s_, (_, g, lo, hi) in defs.items():
        e = e.subs(s_, quad(g.subs(at), lo.subs(at), hi.subs(at)))
    return complex(sp.N(e.subs(at)))


def deriv(expr, defs, at):
    if defs:
        raise ValueError("definite integral in an indefinite chain")
    d = sp.diff(expr.doit() if False else expr, x)
    return complex(sp.N(d.subs(at)))


XS = [0.31, 0.62, 1.13, 1.37, 2.05, 2.71]
KS = [0.4, 0.7, 1.9]
LABEL = re.compile(r"^\s*(\\text\{area\}|y'|y|f\(x\))\s*$")
CHAINS = []          # (where, first side tex, last value, kind)


def chain(seg, where):
    rows = []
    for r_ in seg.split("\\\\"):
        r_ = re.sub(r"\\qquad.*$", "", r_.strip())          # comments after \qquad
        rows.append(r_.replace("&amp;", "").replace("\\quad", "").strip())
    text = "".join(rows)
    sides = [s_ for s_ in T.split_top(text, "=") if s_.strip()]
    if sides and LABEL.match(prep(sides[0]) if "\\text" not in sides[0] else sides[0].strip()):
        sides = sides[1:]
    if len(sides) < 2:
        return None
    try:
        vals = [side(s_) for s_ in sides]
    except Exception as err:  # noqa: BLE001
        report(False, f"{where}", f"PARSE ERROR {err} in {text[:90]!r}")
        return None
    free = set().union(*[v[0].free_symbols for v in vals]) - set(sp.Symbol(k2) for v in vals for k2 in map(str, v[1]))
    free = {s_ for s_ in free if not re.match(r"Z\d+Z", str(s_))}
    indefinite = any(v[0].has(sp.Integral) for v in vals) or ("C" in text and "\\int_" not in text)
    ok, detail = True, ""
    try:
        if indefinite:
            for xv in XS:
                ds = [deriv(v[0], v[1], {x: xv}) for v in vals]
                if any(abs(d - ds[0]) > 1e-8 * (1 + abs(ds[0])) for d in ds[1:]):
                    ok, detail = False, f"derivatives differ at x={xv}: {ds}"
                    break
            kind = "indef"
        else:
            pts = [{k_: kv} for kv in KS] if k_ in free else [{}]
            if x in free:
                pts = [{x: xv} for xv in XS[:3]]
            for at in pts:
                ns = [numval(v[0], v[1], at) for v in vals]
                if any(abs(z - ns[0]) > 1e-9 * (1 + abs(ns[0])) for z in ns[1:]):
                    ok, detail = False, f"values differ at {at}: {[complex(round(z.real, 6), round(z.imag, 6)) for z in ns]}"
                    break
            kind = "def"
    except Exception as err:  # noqa: BLE001
        ok, detail, kind = False, f"EVAL ERROR {err}", "?"
    report(ok, where, detail or f"{len(sides)} sides: " + " | ".join(sides)[:140])
    CHAINS.append((where, sides[0].strip(), vals[-1], kind, sides))
    return vals[-1]


def displays(html):
    return re.findall(r"\\\[(.*?)\\\]", html, re.S)


SKIP = ("u^n", "u'", "f'(x)", "\\big(f(x)\\big)", "\\sin x=x-", "A(2\\sin", "\\int u^", "\\cos^5\\pi-\\cos^50\\big)\\end")


def all_chains(html, where):
    m = 0
    for d in displays(html):
        body = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", d)
        if "=" not in body or any(s_ in d for s_ in SKIP[:6]) or "\\int u^" in d:
            continue
        first = re.sub(r"\\qquad.*", "", body.split("\\\\")[0])
        if not ("\\int" in body or "\\Big[" in body or re.search(r"\\tan\\tfrac|\\sin\\tfrac|\\cos\\tfrac", body)):
            continue
        if re.search(r"(^|\\\\)\s*(-?\d|C|\\ln1|\\ln\\Big|k\+|2\\sqrt3\\sin k\+2\\cos k-2&amp;=2)", body) and "\\int" not in first and "\\Big[" not in first:
            continue          # equations solved for a constant (checked by templates below)
        m += 1
        chain(body, f"{where} display {m}")
    return m


def same_tex(p, q):
    return re.sub(r"\s|\\displaystyle|\\,|&amp;|&", "", p) == re.sub(r"\s|\\displaystyle|\\,|&amp;|&", "", q)


def find_chain(first_tex, where):
    hits = [c for c in CHAINS if same_tex(c[1], first_tex)]
    return hits


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        report(False, where, f"pattern matched {len(found)} times: {pattern[:80]!r}")
        return None
    return found[0]


def eqnum(p, q, tol=1e-9):
    return abs(complex(sp.N(p)) - complex(sp.N(q))) < tol * (1 + abs(complex(sp.N(q))))


# ---------------------------------------------------------------- files and blocks
les, ans = read("l7d.html"), read("a_7d.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1]
parts_ans = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
report(len(parts_ans) == 2 and ans.count("{{ahead:Lesson 7D | Integrating the trigonometric functions}}") == 2,
       "answers: ahead, Lesson Examples, Textbook Homework, ahead, Past-Paper Worked Solutions")
BLK = dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)',
                      parts_ans[0], re.S))
PPA = parts_ans[1]

for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}")

tags = re.findall(r'<span class="tag">(Worked example \d+)</span>', les)
report(tags == [f"Worked example {i}" for i in (16, 17, 18, 19, 20, 21, 22)], "worked examples 16-22 in order (Example 23 not used)", tags)
for c in range(1, 7):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    report(seg.count('<div class="ex demo">') >= 1 and seg.count('<div class="ex attempt">') >= 1, f"Concept {c} has a tutor demo and a your turn")
for blk in re.findall(r'<div class="ex worked">(.*?)</div></div>\n', teach, re.S):
    report("box tip" not in blk and "Note:" not in blk, "worked example holds only the book's lines (no pack note inside)", blk[:60])

# ---------------------------------------------------------------- all display chains
nl = all_chains(teach + hw, "lesson")   # the past-paper questions are statements to prove or solve, not chains
na = all_chains(ans, "answers")
report(nl == 12 and na == 28, "number of checked display chains (all of them)", f"lesson {nl}, answers {na}")


def check_q(first, expected, where):
    hits = find_chain(first, where)
    ok = len(hits) >= 1 and all(h[3] == "def" for h in hits)
    if ok:
        for h in hits:
            val, defs = h[2]
            ok = ok and eqnum(numval(val, defs, {}), expected)
    report(ok, where, f"{len(hits)} chain(s) start with {first[:60]!r}; expected {expected}")


def check_indef(first, integrand, where):
    hits = find_chain(first, where)
    ok = len(hits) >= 1
    for h in hits:
        val, defs = h[2]
        ok = ok and h[3] == "indef" and all(abs(deriv(val, defs, {x: xv}) - complex(sp.N(integrand.subs(x, xv)))) < 1e-9 for xv in XS)
    report(ok, where, f"{len(hits)} chain(s) start with {first[:60]!r}")


I = sp.integrate
# Worked examples and tips (lesson), lesson examples (answers): question -> independent value
DEF_ITEMS = [
    (r"\int_0^\pi\sin x\,dx", I(sp.sin(x), (x, 0, pi)), "WE16 area 2"),
    (r"\int_0^\pi\cos x\,dx", I(sp.cos(x), (x, 0, pi)), "WE17a"),
    (r"\int_0^{\frac{\pi}{3}}\sec^2x\,dx", sp.tan(pi / 3), "WE17b"),
    (r"\int_\pi^{2\pi}\sin\tfrac14x\,dx", I(sp.sin(x / 4), (x, pi, 2 * pi)), "WE18a (book 18b)"),
    (r"\int_0^{\frac{\pi}{8}}\sec^2(2x+\pi)\,dx", sp.tan(5 * pi / 4) / 2 - sp.tan(pi) / 2, "WE18b (book 18c)"),
    (r"\int_0^\pi\sin x\cos^4x\,dx", I(sp.sin(x) * sp.cos(x) ** 4, (x, 0, pi)), "WE22b and the formula tip"),
    (r"\int_0^{\frac{\pi}{2}}\cos x\,dx", 1, "C1 demo area"),
    (r"\int_0^{\frac{\pi}{2}}\sin x\,dx", 1, "C1 your-turn area"),
    (r"\int_0^{2\pi}\cos x\,dx", I(sp.cos(x), (x, 0, 2 * pi)), "C2 demo a"),
    (r"\int_0^{\frac{\pi}{4}}\sec^2x\,dx", sp.tan(pi / 4), "C2 demo b"),
    (r"\int_{\frac{\pi}{2}}^{\frac{3\pi}{2}}\cos x\,dx", I(sp.cos(x), (x, pi / 2, 3 * pi / 2)), "C2 your turn a"),
    (r"\int_0^{\frac{\pi}{6}}\sec^2x\,dx", sp.tan(pi / 6), "C2 your turn b"),
    (r"\int_0^{\frac{\pi}{4}}\cos2x\,dx", I(sp.cos(2 * x), (x, 0, pi / 4)), "C3 demo a"),
    (r"\int_0^\pi\sin\tfrac13x\,dx", I(sp.sin(x / 3), (x, 0, pi)), "C3 demo b"),
    (r"\int_0^{\frac{\pi}{6}}\sec^2(2x+\pi)\,dx", (sp.tan(4 * pi / 3) - sp.tan(pi)) / 2, "C3 demo c"),
    (r"\int_0^{\frac{\pi}{8}}\cos4x\,dx", I(sp.cos(4 * x), (x, 0, pi / 8)), "C3 your turn a"),
    (r"\int_0^{\frac{3\pi}{2}}\sin\tfrac13x\,dx", I(sp.sin(x / 3), (x, 0, 3 * pi / 2)), "C3 your turn b"),
    (r"\int_0^{\frac{\pi}{12}}\sec^2(3x+\pi)\,dx", (sp.tan(5 * pi / 4) - sp.tan(pi)) / 3, "C3 your turn c"),
    (r"\int_0^\pi\sin x\cos^6x\,dx", I(sp.sin(x) * sp.cos(x) ** 6, (x, 0, pi)), "C6 demo b"),
    (r"\int_0^{\frac{\pi}{3}}\sin x\cos^2x\,dx", I(sp.sin(x) * sp.cos(x) ** 2, (x, 0, pi / 3)), "C6 your turn b"),
    (r"\int_0^{\frac{\pi}{6}}\sin x\cos x\,dx", I(sp.sin(x) * sp.cos(x), (x, 0, pi / 6)), "PP 4"),
    (r"\int_{\frac{\pi}{3}}^{\frac{\pi}{2}}(\operatorname{cosec}x+\cot x)\,dx", I(1 / sp.sin(x) + sp.cos(x) / sp.sin(x), (x, pi / 3, pi / 2)), "PP 8"),
    (r"\int_1^e\dfrac1x\,dx", 1, "Note: three simple results"),
]
for first, val, where in DEF_ITEMS:
    check_q(first, sp.simplify(val), where)

IND_ITEMS = [
    (r"\int\cot x\,dx", sp.cot(x), "WE19a"), (r"\int\tan x\,dx", sp.tan(x), "WE19b and PP 1"),
    (r"\int\cot2x\,dx", sp.cot(2 * x), "C4 demo a"), (r"\int\tan2x\,dx", sp.tan(2 * x), "C4 demo b"),
    (r"\int\cot3x\,dx", sp.cot(3 * x), "C4 your turn a"), (r"\int\tan3x\,dx", sp.tan(3 * x), "C4 your turn b"),
    (r"\int\cos x\sin^6x\,dx", sp.cos(x) * sp.sin(x) ** 6, "C7 demo"), (r"\int\sin x\cos^6x\,dx", sp.sin(x) * sp.cos(x) ** 6, "C7 your turn"),
    (r"\int\sec^2\theta\tan^2\theta\,d\theta", sp.sec(x) ** 2 * sp.tan(x) ** 2, "PP 2 (theta written as x)"),
    (r"\int\sin x\cos^3x\,dx", sp.sin(x) * sp.cos(x) ** 3, "PP 3"),
    (r"\int\Big(\dfrac{\cos x}{\sin x}+x\Big)\,dx", sp.cot(x) + x, "PP 6"),
    (r"\int\sin x\cos x\,dx", sp.sin(x) * sp.cos(x), "Ex 7D Q17a statement"),
]
for first, g, where in IND_ITEMS:
    check_indef(first, g, where)

# the questions themselves must be printed (lesson side)
for q_ in [r"\int_0^{2\pi}\cos x\,dx", r"\int_0^{\frac{\pi}{4}}\sec^2x\,dx", r"\int_{\frac{\pi}{3}}^{\frac{2\pi}{3}}\sec^2x\,dx",
           r"\int_{\frac{\pi}{2}}^{\frac{3\pi}{2}}\cos x\,dx", r"\int_0^{\frac{\pi}{6}}\sec^2x\,dx", r"\int_{\frac{\pi}{6}}^{\frac{5\pi}{6}}\sec^2x\,dx",
           r"\int_0^{\frac{\pi}{4}}\cos2x\,dx", r"\int_0^\pi\sin\tfrac13x\,dx", r"\int_0^{\frac{\pi}{6}}\sec^2(2x+\pi)\,dx",
           r"\int_0^{\frac{\pi}{8}}\cos4x\,dx", r"\int_0^{\frac{3\pi}{2}}\sin\tfrac13x\,dx", r"\int_0^{\frac{\pi}{12}}\sec^2(3x+\pi)\,dx",
           r"\(\cot2x\)", r"\(\tan2x\)", r"\(\cot3x\)", r"\(\tan3x\)", r"\int_0^\pi\sin x\cos^6x\,dx", r"\int_0^{\frac{\pi}{3}}\sin x\cos^2x\,dx",
           r"\int\cos x\sin^6x\,dx", r"\int\sin x\cos^6x\,dx", r"differentiate \(\cos^7x\)", r"differentiate \(\cos^3x\)"]:
    report(teach.count(q_) == 1, f"lesson question printed once: {q_[:60]}")

# the meaningless items (asymptote between the limits) in the answers and WE17c
for lo, hi, where in [(pi / 3, 2 * pi / 3, "C2 demo c"), (pi / 6, 5 * pi / 6, "C2 your turn c"), (pi / 4, 3 * pi / 4, "WE17c")]:
    crosses = bool(lo < pi / 2 < hi)
    report(crosses, f"{where}: x = pi/2 lies between the limits (meaningless)")
report(len(re.findall(r"meaningless because it crosses the asymptote at \\\(x=\\frac\{\\pi\}\{2\}\\\)", ans)) == 2, "C2 c answers say meaningless")

# ---------------------------------------------------------------- lesson tables: WE20, WE21 and C5 answers
we = teach.split("Worked example 20</span>")[1].split("Worked example 21</span>")[0]
report(all(s_ in we for s_ in [r"\(y=\sin x+C,\)", r"\(3=\sin0+C\)", r"\(C=3.\)", r"\(y=\sin x+3.\)", r"\(\phantom{y}=4,\)"]), "WE20 lines printed")
f20 = sp.sin(x) + 3
report(sp.diff(f20, x) == sp.cos(x) and f20.subs(x, 0) == 3 and f20.subs(x, pi / 2) == 4, "WE20 recomputed: y = sin x + 3, f(pi/2) = 4")
we = teach.split("Worked example 21</span>")[1].split("Worked example 22</span>")[0]
report(all(s_ in we for s_ in [r"\(f(x)=-\tfrac12\cos2x+C,\)", r"\(1=-\tfrac12\cos2\pi+C\)", r"\(C=1\tfrac12.\)", r"\(f(x)=-\tfrac12\cos2x+1\tfrac12.\)",
                                r"=1\tfrac12,\)"]), "WE21 lines printed")
f21 = -sp.cos(2 * x) / 2 + sp.Rational(3, 2)
report(sp.diff(f21, x) == sp.sin(2 * x) and f21.subs(x, pi) == 1 and f21.subs(x, pi / 4) == sp.Rational(3, 2), "WE21 recomputed")
we = teach.split("Worked example 22</span>")[1]
report(r"\(\phantom{\dfrac{dy}{dx}}=-5\sin x\cos^4x.\)" in we and sp.diff(sp.cos(x) ** 5, x).equals(-5 * sp.sin(x) * sp.cos(x) ** 4), "WE22a derivative")

c5 = BLK.get("C5", "")


def c5val(pattern, where):
    return grab(c5, pattern, where)


# demo 1: y' = sin x, (0, 2); demo 2: f' = cos 2x, f(pi/4) = 1; turn 1: y' = -sin x, (0, 4); turn 2: f' = cos 2x, f(pi/2) = 2
for (pat, fprint, d_, x0, y0, xq, yq_pat, where) in [
        (r"Hence \\\(f\(x\)=3-\\cos x\\\)", 3 - sp.cos(x), sp.sin(x), 0, 2, pi / 2, r"Then \\\(f\\big\(\\frac\{\\pi\}\{2\}\\big\)=3-\\cos\\frac\{\\pi\}\{2\}=3-0=(\d+)\\\)", "C5 demo 1"),
        (r"Hence \\\(f\(x\)=\\tfrac12\\sin2x\+\\tfrac12\\\)", sp.sin(2 * x) / 2 + sp.Rational(1, 2), sp.cos(2 * x), pi / 4, 1, pi / 12, r"=\\tfrac12\\times\\tfrac12\+\\tfrac12=\\tfrac(\d)(\d)\\\)", "C5 demo 2"),
        (r"Hence \\\(f\(x\)=\\cos x\+3\\\)", sp.cos(x) + 3, -sp.sin(x), 0, 4, pi, r"Then \\\(f\(\\pi\)=\\cos\\pi\+3=-1\+3=(\d)\\\)", "C5 your turn 1"),
        (r"Hence \\\(f\(x\)=\\tfrac12\\sin2x\+2\\\)", sp.sin(2 * x) / 2 + 2, sp.cos(2 * x), pi / 2, 2, pi / 4, r"=\\tfrac12\\times1\+2=(2)\\tfrac(1)(2)\\\)", "C5 your turn 2")]:
    got = c5val(pat, where + " f(x) printed")
    g = c5val(yq_pat, where + " value printed")
    if g is not None:
        if isinstance(g, tuple) and len(g) == 3:
            printed = int(g[0]) + sp.Rational(int(g[1]), int(g[2]))
        elif isinstance(g, tuple):
            printed = sp.Rational(int(g[0]), int(g[1]))
        else:
            printed = int(g)
        report(sp.simplify(sp.diff(fprint, x) - d_) == 0 and sp.simplify(fprint.subs(x, x0) - y0) == 0 and sp.simplify(fprint.subs(x, xq) - printed) == 0,
               where + " recomputed", f"{fprint}, value {printed}")
# the questions of C5 in the lesson
for s_ in [r"\(y'=\sin x\), and the graph of the function has \(y\)-intercept \((0,2)\)", r"\(f'(x)=\cos2x\) and \(f\big(\frac{\pi}{4}\big)=1\)",
           r"find \(f\big(\frac{\pi}{12}\big)\)", r"\(y'=-\sin x\), and the graph of the function has \(y\)-intercept \((0,4)\)",
           r"find \(f(\pi)\)", r"\(f'(x)=\cos2x\) and \(f\big(\frac{\pi}{2}\big)=2\)"]:
    report(teach.count(s_) == 1, "C5 question printed: " + s_[:60])

c6 = BLK.get("C6", "")
for pat, expr in [(r"=-7\\sin x\\cos\^6x\\\)", sp.cos(x) ** 7), (r"=-3\\sin x\\cos\^2x\\\)", sp.cos(x) ** 3)]:
    got = grab(c6, pat, "C6 derivative printed " + pat[:12])
    m = re.search(r"-(\d)\\\\sin x\\\\cos\\\^(\d)x", pat)
    report(got is not None and sp.simplify(sp.diff(expr, x) + int(m.group(1)) * sp.sin(x) * sp.cos(x) ** int(m.group(2))) == 0, "C6 derivative recomputed", str(expr))

# ---------------------------------------------------------------- Exercise 7D: structure and transcription
qn = re.findall(r'<span class="q-num">(\d+)</span>', hw)
report(qn == [str(i) for i in range(1, 23)], "exercise questions 1-22 in order", qn)
bands = [hw.index("{{band:F}}"), hw.index("{{band:D}}"), hw.index("{{band:E}}")]
report(bands[0] < hw.index('q-num">1<') and hw.index('q-num">8<') < bands[1] < hw.index('q-num">9<')
       and hw.index('q-num">19<') < bands[2] < hw.index('q-num">20<'), "bands F 1-8, D 9-19, E 20-22")


def qblock(nq):
    return hw.split(f'<span class="q-num">{nq}</span>')[1].split('<span class="q-num">')[0]


def parts(nq, sub=None):
    blk = qblock(nq)
    return dict(re.findall(r'<span class="pl">([a-z]+)</span>\\\((.*?)\\\)</span>', blk, re.S))


def integrand_of(t_):
    m = re.match(r"\\displaystyle\\int(?:_" + LIM + r"\^" + LIM + r")?(.*?)\\,dx$", t_.strip(), re.S)
    if not m:
        raise ValueError(t_)
    g = tex(m.group(3))
    lims = (tex(unbrace(m.group(1))), tex(unbrace(m.group(2)))) if m.group(1) else None
    return g, lims


S, Cc, Tt, Sc = sp.sin, sp.cos, sp.tan, sp.sec
R = sp.Rational
BOOK = {   # the textbook's exercise, typed independently: integrand (and limits)
    1: dict(a=Sc(x) ** 2, b=Cc(x), c=S(x), d=-S(x), e=2 * Cc(x), f=Cc(2 * x), g=Cc(x) / 2, h=Cc(x / 2), i=S(2 * x), j=Sc(5 * x) ** 2, k=Cc(3 * x),
            l=Sc(x / 3) ** 2, m=S(x / 2), n=-Cc(x / 5), o=-4 * S(2 * x), p=S(x / 4) / 4, q=12 * Sc(x / 3) ** 2, r=2 * Cc(x / 3)),
    2: dict(a=(Cc(x), 0, pi / 2), b=(Cc(x), 0, pi / 6), c=(S(x), pi / 4, pi / 2), d=(Sc(x) ** 2, 0, pi / 3), e=(2 * Cc(2 * x), 0, pi / 4),
            f=(S(2 * x), 0, pi / 3), g=(Sc(x / 2) ** 2, 0, pi / 2), h=(Cc(x / 2), pi / 3, pi), i=(2 * S(x) - S(2 * x), 0, pi)),
    6: dict(a=Cc(x + 2), b=Cc(2 * x + 1), c=S(x + 2), d=S(2 * x + 1), e=Cc(3 * x - 2), f=S(7 - 5 * x), g=Sc(4 - x) ** 2, h=Sc((1 - x) / 3) ** 2, i=S((1 - x) / 3)),
    16: dict(a=(S(x) * Cc(x) ** 8, 0, pi), b=(S(x) * Cc(x) ** n_, 0, pi / 2), c=(Cc(x) * S(x) ** 7, -pi / 2, pi / 2), d=(Cc(x) * S(x) ** n_, 0, pi / 6),
             e=(Sc(x) ** 2 * Tt(x) ** 7, 0, pi / 3), f=(Sc(x) ** 2 * Tt(x) ** n_, 0, pi / 4)),
}
for nq, book in BOOK.items():
    pr = parts(nq)
    report(sorted(pr) == sorted(book), f"Q{nq}: parts", sorted(pr))
    for lab, want in book.items():
        if lab not in pr:
            continue
        try:
            g, lims = integrand_of(pr[lab])
        except Exception as err:  # noqa: BLE001
            report(False, f"Q{nq}{lab} parse", err)
            continue
        if isinstance(want, tuple):
            ok = lims is not None and sp.simplify(lims[0] - want[1]) == 0 and sp.simplify(lims[1] - want[2]) == 0
            ok = ok and all(eqnum(g.subs({x: xv, n_: 3}), want[0].subs({x: xv, n_: 3})) for xv in (0.3, 0.9))
        else:
            ok = lims is None and all(eqnum(g.subs(x, xv), want.subs(x, xv)) for xv in (0.3, 0.9, 1.4))
        report(ok, f"Q{nq}{lab} transcription", pr[lab][:60])

# other question texts (spot transcription of every remaining question)
TEXTS = {
    3: [r"\(\dfrac{dy}{dx}=\sin x\). If the curve passes through the origin", r"\(y'=\cos x-2\sin2x\)", r"\(\dfrac{dy}{dx}=\sin x+\cos x\), and \(y=-2\) when \(x=\pi\)"],
    4: [r"\(\displaystyle\int_0^\pi\sin x\,dx=2\)", r"\(\displaystyle\int_0^{\frac{7\pi}{4}}\sin x\,dx\)", "{{svg:q7d_q4}}"],
    7: [r"\(\displaystyle\int\Big(6\cos3x-4\sin\tfrac12x\Big)\,dx\)", r"\(\displaystyle\int\Big(8\sec^22x-10\cos\tfrac14x+12\sin\tfrac13x\Big)\,dx\)"],
    8: [r"\(f'(x)=\pi\cos\pi x\) and \(f(0)=0\)", r"\(f'(x)=\cos\pi x\) and \(f(0)=\frac{1}{2\pi}\)", r"\(f''(x)=18\cos3x\) and \(f'(0)=f\big(\frac{\pi}{2}\big)=1\)"],
    9: [r"\int a\sin(ax+b)\,dx", r"\int\pi^2\cos\pi x\,dx", r"\int\dfrac1u\sec^2(v+ux)\,dx", r"\int\dfrac{a}{\cos^2ax}\,dx"],
    10: [r"\(1+\tan^2x=\ldots\)", r"\int_0^{\frac{\pi}{3}}\dfrac{2}{1-\sin^2x}\,dx"],
    11: [r"\int_0^{\frac{\pi}{6}}\dfrac{\cos x}{1+\sin x}\,dx\doteqdot0.4"],
    12: [r"\int_0^{\frac{\pi}{4}}\tan x\,dx=\tfrac12\ln2", r"\int_{\frac{\pi}{6}}^{\frac{\pi}{2}}\cot x\,dx"],
    13: [r"\(\dfrac{d}{dx}(\sin^5x)\)", r"\int\sin^4x\cos x\,dx", r"\(\dfrac{d}{dx}(\tan^3x)\)", r"\int\tan^2x\sec^2x\,dx"],
    14: [r"\int_0^{\frac{\pi}{2}}\cos x\,e^{\sin x}\,dx", r"\int_0^{\frac{\pi}{4}}\sec^2x\,e^{\tan x}\,dx"],
    15: [r"\dfrac{d}{dx}(\sin x-x\cos x)=x\sin x", r"\int_0^{\frac{\pi}{2}}x\sin x\,dx", r"\dfrac{d}{dx}\big(\tfrac13\cos^3x-\cos x\big)=\sin^3x", r"\int_0^{\frac{\pi}{3}}\sin^3x\,dx"],
    17: [r"\int\sin x\cos x\,dx=\tfrac12\sin^2x+C=-\tfrac14\cos2x+D."],
    18: [r"\dfrac{d}{dx}\big(x\sin2x\big)", r"\int_0^{\frac{\pi}{4}}x\cos2x\,dx"],
    19: [r"\dfrac{d}{dx}(\tan^3x)=3(\sec^4x-\sec^2x)", r"\int_0^{\frac{\pi}{4}}\sec^4x\,dx"],
    20: [r"\sin(A+B)+\sin(A-B)=2\sin A\cos B", r"\int_0^{\frac{\pi}{2}}2\sin3x\cos2x\,dx", r"\int_0^\pi\sin3x\cos4x\,dx", r"\int_{-\pi}^\pi\sin mx\cos nx\,dx=0"],
    21: [r"A(2\sin x+\cos x)+B(2\cos x-\sin x)=7\sin x+11\cos x.", r"\int_0^{\frac{\pi}{2}}\dfrac{7\sin x+11\cos x}{2\sin x+\cos x}\,dx=\dfrac12(5\pi+6\ln2)"],
    22: [r"\dfrac{x^{4n+1}}{(4n+1)!}\le\sin x+\dfrac{x^{4n+3}}{(4n+3)!}", r"\cos x\le1-\dfrac{x^2}{2!}+\dfrac{x^4}{4!}", r"\cos x\ge1-\dfrac{x^2}{2!}"],
}
for nq, lst in TEXTS.items():
    blk = qblock(nq)
    for s_ in lst:
        report(blk.count(s_) == 1, f"Q{nq} text: {s_[:55]}")
# the printed statements that are facts must be true
report(eqnum(I(Cc(x) / (1 + S(x)), (x, 0, pi / 6)), sp.log(R(3, 2))) and round(float(sp.log(R(3, 2))), 1) == 0.4, "Q11b: ln(3/2) = 0.405..., about 0.4")
report(sp.simplify(I(Tt(x), (x, 0, pi / 4)) - sp.log(2) / 2) == 0, "Q12a statement: integral of tan x from 0 to pi/4 = (1/2) ln 2")
report(sp.simplify(sp.diff(S(x) - x * Cc(x), x) - x * S(x)) == 0 and sp.simplify(sp.diff(Cc(x) ** 3 / 3 - Cc(x), x) - S(x) ** 3) == 0, "Q15 statements")
report(sp.simplify(sp.diff(Tt(x) ** 3, x) - 3 * (Sc(x) ** 4 - Sc(x) ** 2)) == 0, "Q19a statement")
report(eqnum(I((7 * S(x) + 11 * Cc(x)) / (2 * S(x) + Cc(x)), (x, 0, pi / 2)), (5 * pi + 6 * sp.log(2)) / 2), "Q21b statement (numerical)")
report(all(abs(sum((-1) ** j * xv ** (2 * j + 1) / sp.factorial(2 * j + 1) for j in range(2 * nn + 1)) - mp.sin(xv)) >= 0
           and float(sum((-1) ** j * xv ** (2 * j + 1) / sp.factorial(2 * j + 1) for j in range(2 * nn + 1))) >= float(mp.sin(xv)) - 1e-15
           and float(sum((-1) ** j * xv ** (2 * j + 1) / sp.factorial(2 * j + 1) for j in range(2 * nn + 1))) <= float(mp.sin(xv) + mp.mpf(xv) ** (4 * nn + 3) / mp.factorial(4 * nn + 3)) + 1e-15
           for nn in (1, 2, 3) for xv in (0.5, 1.5, 3.0)), "Q22d inequality holds (n = 1, 2, 3; x = 0.5, 1.5, 3)")

# ---------------------------------------------------------------- textbook answers
def items(nq):
    blk = BLK.get(str(nq), "")
    if not blk:
        report(False, f"answer block {nq} missing")
    return blk, dict(re.findall(r'<b>([a-z]+)</b> \\\((.*?)\\\)(?:</span>|,)', blk, re.S))


def prim_ok(F, g, extra_subs=None):
    sub = extra_subs or {}
    d = sp.diff(F, x)
    return all(eqnum(d.subs(sub).subs(x, xv), g.subs(sub).subs(x, xv)) for xv in (0.21, 0.47, 0.83, 1.31))


blk, it = items(1)
report(sorted(it) == sorted(BOOK[1]), "A1 parts", sorted(it))
for lab, g in BOOK[1].items():
    if lab in it:
        report(prim_ok(tex(it[lab]), g), f"A1{lab}: derivative of the printed primitive", it[lab])
blk, it = items(2)
for lab, (g, lo, hi) in BOOK[2].items():
    report(lab in it and eqnum(tex(it[lab]), I(g, (x, lo, hi))), f"A2{lab}", it.get(lab))
blk, it = items(3)
for lab, (d_, x0, y0) in dict(a=(S(x), 0, 0), b=(Cc(x) - 2 * S(2 * x), 0, 0), c=(S(x) + Cc(x), pi, -2)).items():
    F = tex(it[lab].split("=", 1)[1]) if lab in it else None
    report(F is not None and prim_ok(F, d_) and sp.simplify(F.subs(x, x0) - y0) == 0, f"A3{lab}", it.get(lab))
# Q4: counts and exact values
blk = BLK.get("4", "")
ex4 = {"i": pi / 4, "ii": pi / 2, "iii": 3 * pi / 4, "iv": 5 * pi / 4, "v": 3 * pi / 2, "vi": 7 * pi / 4}
cnts = grab(blk, r"about (\d+), (\d+), (\d+), (\d+), (\d+) and (\d+) little squares", "A4 counts")
vals4 = [I(S(x), (x, 0, u)) for u in ex4.values()]
report(cnts is not None and [int(c) for c in cnts] == [round(100 * float(v)) for v in vals4], "A4b counts = 100 x exact value", cnts)
report(grab(blk, r"<b>a</b> about (\d+) little squares, that is, about 2 square units", "A4a") == "200" and I(S(x), (x, 0, pi)) == 2, "A4a 200 squares")
approx = re.findall(r"<b>(i|ii|iii|iv|v|vi)</b> \\\((?:\\doteq)?([\d.]+)\\\)", blk.split("<b>c</b>")[0])
report([a for a, _ in approx] == list(ex4) and all(abs(float(p) - float(v)) < 0.005 for (_, p), v in zip(approx, vals4)), "A4b decimals", approx)
cpart = blk.split("<b>c</b>")[1]
exact = re.findall(r"<b>(i|ii|iii|iv|v|vi)</b> \\\((.*?)\\\)", cpart)
report([a for a, _ in exact] == list(ex4) and all(sp.simplify(tex(p) - v) == 0 for (_, p), v in zip(exact, vals4)), "A4c exact values", exact)
blk, it = items(6)
for lab, g in BOOK[6].items():
    report(lab in it and prim_ok(tex(it[lab]), g), f"A6{lab}", it.get(lab))
blk, it = items(7)
report(prim_ok(tex(it["a"]), 6 * Cc(3 * x) - 4 * S(x / 2)) and prim_ok(tex(it["b"]), 8 * Sc(2 * x) ** 2 - 10 * Cc(x / 4) + 12 * S(x / 3)), "A7a, A7b")
blk = BLK.get("8", "")
m8 = re.findall(r"<b>([abc])</b> \\\(f\(x\)=(.*?)\\\)(?:, \\\(f\\big\(\\tfrac1(\d)\\big\)=(.*?)\\\))?", blk)
d8 = {"a": (pi * Cc(pi * x), 0, 0, 3), "b": (Cc(pi * x), 0, 1 / (2 * pi), 6)}
for lab, fx, den, fv in m8:
    F = tex(fx)
    if lab in d8:
        g, x0, y0, dd = d8[lab]
        report(prim_ok(F, g) and sp.simplify(F.subs(x, x0) - y0) == 0 and int(den) == dd and sp.simplify(F.subs(x, R(1, dd)) - tex(fv)) == 0, f"A8{lab}", fx)
    else:
        report(sp.simplify(sp.diff(F, x, 2) - 18 * Cc(3 * x)) == 0 and sp.diff(F, x).subs(x, 0) == 1 and sp.simplify(F.subs(x, pi / 2) - 1) == 0, "A8c", fx)
report(len(m8) == 3, "A8 three parts found")
blk, it = items(9)
sub9 = {a_: R(3, 2), b_: R(1, 3), u_: R(5, 4), v_: R(2, 7)}
loc9 = {"a": a_, "b": b_, "u": u_, "v": v_}
for lab, g in dict(a=a_ * S(a_ * x + b_), b=pi ** 2 * Cc(pi * x), c=Sc(v_ + u_ * x) ** 2 / u_, d=a_ / Cc(a_ * x) ** 2).items():
    report(lab in it and prim_ok(tex(it[lab], loc9), g, sub9), f"A9{lab}", it.get(lab))
blk = BLK.get("10", "")
report(r"\(1+\tan^2x=\sec^2x\)" in blk and prim_ok(tex(grab(blk, r"\\ (\\tan x-x\+C)\\\)", "A10a")), Tt(x) ** 2), "A10a")
report(r"\(1-\sin^2x=\cos^2x\)" in blk and sp.simplify(tex(grab(blk, r"\\cos\^2x\\\), \\\(\\ (2\\sqrt3)\\\)", "A10b")) - I(2 / Cc(x) ** 2, (x, 0, pi / 3))) == 0, "A10b")
report(r"\(\log_e|f(x)|+C\)" in BLK.get("11", ""), "A11a")
blk = BLK.get("12", "")
report(r"\int\tan x\,dx=-\ln|\cos x|+C" in blk and prim_ok(-sp.log(sp.Abs(Cc(x))), Tt(x)), "A12a")
report(r"=\ln2\)" in blk and sp.simplify(I(Cc(x) / S(x), (x, pi / 6, pi / 2)) - sp.log(2)) == 0, "A12b")
blk = BLK.get("13", "")
m13 = re.findall(r"<b>([ab])</b> \\\((.*?)\\\), \\\(\\ (.*?)\\\)", blk)
for (lab, dv, pv), (fn, g) in zip(m13, [(S(x) ** 5, S(x) ** 4 * Cc(x)), (Tt(x) ** 3, Tt(x) ** 2 * Sc(x) ** 2)]):
    report(eqnum(tex(dv).subs(x, 0.7), sp.diff(fn, x).subs(x, 0.7)) and prim_ok(tex(pv), g), f"A13{lab}", dv + " ; " + pv)
report(len(m13) == 2, "A13 two parts")
blk = BLK.get("14", "")
m14 = re.findall(r"<b>([ab])</b> \\\((.*?)\\\), \\\(\\ (.*?)\\\)", blk)
for (lab, dv, val), (fn, g, hi) in zip(m14, [(sp.exp(S(x)), Cc(x) * sp.exp(S(x)), pi / 2), (sp.exp(Tt(x)), Sc(x) ** 2 * sp.exp(Tt(x)), pi / 4)]):
    report(eqnum(tex(dv).subs(x, 0.7), sp.diff(fn, x).subs(x, 0.7)) and eqnum(tex(val), I(g, (x, 0, hi))), f"A14{lab}", dv + " ; " + val)
report(len(m14) == 2, "A14 two parts")
blk, it = items(15)
report(sp.simplify(tex(it["a"]) - I(x * S(x), (x, 0, pi / 2))) == 0 and sp.simplify(tex(it["b"]) - I(S(x) ** 3, (x, 0, pi / 3))) == 0, "A15a, A15b", it)
blk, it = items(16)
for lab, (g, lo, hi) in BOOK[16].items():
    ok = lab in it
    for nn in (1, 2, 5) if ok else ():
        ok = ok and eqnum(tex(it[lab]).subs(n_, nn), sp.integrate(g.subs(n_, nn), (x, lo, hi)))
    report(ok, f"A16{lab} (n = 1, 2, 5 where n appears)", it.get(lab))
blk = BLK.get("17", "")
report(r"\sin^2x=\tfrac12(1-\cos2x)" in blk and r"where \(D=C+\tfrac14\)" in blk
       and sp.simplify(S(x) ** 2 / 2 - (-Cc(2 * x) / 4 + R(1, 4))) == 0, "A17b reconciliation (D = C + 1/4)")
blk = BLK.get("18", "")
d18, v18 = grab(blk, r"\\\((\\sin2x\+2x\\cos2x)\\\), \\\(\\ (.*?)\\\)", "A18") or ("", "0")
report(sp.simplify(tex(d18) - sp.diff(x * S(2 * x), x)) == 0 and sp.simplify(tex(v18) - I(x * Cc(2 * x), (x, 0, pi / 4))) == 0, "A18", v18)
blk, it = items(19)
report(sp.simplify(tex(it["b"]) - I(Sc(x) ** 4, (x, 0, pi / 4))) == 0, "A19b", it.get("b"))
blk = BLK.get("20", "")
m20 = re.findall(r"<b>(i|ii)</b> \\\((.*?)\\\)", blk)
report([a for a, _ in m20] == ["i", "ii"] and sp.simplify(tex(m20[0][1]) - I(2 * S(3 * x) * Cc(2 * x), (x, 0, pi / 2))) == 0
       and sp.simplify(tex(m20[1][1]) - I(S(3 * x) * Cc(4 * x), (x, 0, pi))) == 0, "A20b i, ii", m20)
for mm in range(1, 5):
    for nn in range(1, 5):
        if sp.integrate(S(mm * x) * Cc(nn * x), (x, -pi, pi)) != 0:
            report(False, f"Q20c fails for m={mm}, n={nn}")
blk = BLK.get("21", "")
sol = sp.solve([2 * A_ - sp.Symbol("B") - 7, A_ + 2 * sp.Symbol("B") - 11], [A_, sp.Symbol("B")])
report(grab(blk, r"\\\(A=(\d+)\\\), \\\(B=(\d+)\\\)", "A21a") == (str(sol[A_]), str(sol[sp.Symbol("B")])), "A21a", sol)
# answered questions and omitted ones
report(sorted(int(k2) for k2 in BLK if k2.isdigit()) == [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
       "answers given for every item with a final answer (not Q5 technology, Q22 proofs)")

# ---------------------------------------------------------------- past papers
WANT = [("PP 1", "Sydney Grammar School, 2020, Trial Examination, Form VI Mathematics Extension 1, Q7", 1, None),
        ("PP 2", "Caringbah High School, 2021, Year 12 Mathematics Extension 1 HSC Course Assessment Task 4, Q6", 1, None),
        ("PP 3", "Cherrybrook Technology High School, 2020, Year 12 AP4, Mathematics Extension 1, Q5", 1, None),
        ("PP 4", "Caringbah High School, 2020, Higher School Certificate Trial Examination, Mathematics Extension 1, Q11(b)", 2, None),
        ("PP 5", "Fort Street High School, 2020, Trial Higher School Certificate Examination, Mathematics Extension 1, Q12(e)", 2, None),
        ("PP 6", "Hornsby Girls High School, 2022, Mathematics Extension 1, Year 12 Higher School Certificate Trial Examination Term 3, Q14(a)", 3, None),
        ("PP 7", "Abbotsleigh, 2023, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q11(d)(ii)", 3, [3]),
        ("PP 8", "Killara High School, 2020, Mathematics Extension 1 Trial HSC Examination, Q12(d)(ii)", 3, [3])]


def clean(s_):
    s_ = re.sub(r"<[^>]+>", "", s_).replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s_).strip()


ppq = re.split(r'(?=<div class="pp"><div class="pp-src">)', ppl)[1:]
ppa = re.split(r'(?=<div class="ppa"><div class="pp-src">)', PPA)[1:]
report(len(ppq) == 8 and len(ppa) == 8, "8 past-paper questions and 8 solutions")
total = 0
for (pn, lab, mk, sub), q_, s_ in zip(WANT, ppq, ppa):
    src = re.search(r'<span class="pn">(PP \d)</span>(.*?)</span><span class="mk">(\d+) marks?</span>', q_, re.S)
    srca = re.search(r'<span class="pn">(PP \d)</span>(.*?)</span></div>', s_, re.S)
    subs = [int(z) for z in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', q_, re.S)]
    ok = src and src.group(1) == pn and clean(src.group(2)) == lab and int(src.group(3)) == mk and srca and srca.group(1) == pn and clean(srca.group(2)) == lab
    ok = ok and (sub is None or subs == sub) and q_.count('<div class="hint">') == 1
    report(bool(ok), f"{pn} label (both files), marks, one hint", lab[:60])
    total += mk
report(total == 16, "mini exam total 16 marks", total)
tm = grab(ppl, r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", "pp-intro")
report(tm is not None and int(tm[1]) == total and int(tm[0]) == 5 * round(1.5 * total / 5), "time = 1.5 x marks rounded to 5 min", tm)
hints = re.findall(r'<div class="hint"><b>Hint:</b> (.*?)</div>', ppl)
bad = re.compile(r"rule|chain|product|quotient|substitut|reverse|differentiat|log|identity|formula|primitive|tan|sin|cos|cot|sec|square|power|\\\(|\d|compare|worked|split|balanc|derivative")
report(len(hints) == 8 and all(h.endswith("?") and not bad.search(re.sub(r"\\\(f\\\)", "", h)) for h in hints), "hints: neutral starting questions only", hints)

# MC: differentiate every option; exactly one must match the integrand, and it must be the printed answer
MC = [(0, sp.tan(x), "D"), (1, sp.sec(x) ** 2 * sp.tan(x) ** 2, "B"), (2, sp.sin(x) * sp.cos(x) ** 3, "B")]
for idx, g, keyed in MC:
    opts = re.findall(r'<span class="pl">\(?([A-D])\)?\.?</span>\\\((.*?)\\\)</span>', ppq[idx], re.S)
    good = []
    for letter, o in opts:
        o2 = o.replace("y=", "")
        F = tex(o2, {"A": sp.Integer(3)})
        if prim_ok(F, g):
            good.append(letter)
    printed = re.findall(r"answer is <b>\(?([A-D])\)?</b>", ppa[idx])
    report(len(opts) == 4 and good == [keyed] and printed == [keyed], f"PP {idx + 1} MC: exactly one option differentiates back", f"{good} printed {printed}")

# PP 5: y'' = -sec^2(2x), y'(pi/8) = -1 -> y'(pi/12)
yp = sp.integrate(-sp.sec(2 * x) ** 2, x)
Cs = sp.solve(sp.Eq(yp.subs(x, pi / 8) + sp.Symbol("K"), -1), sp.Symbol("K"))[0]
want5 = sp.simplify(yp.subs(x, pi / 12) + Cs)
got5 = grab(ppa[4], r"The exact gradient at \\\(x=\\dfrac\{\\pi\}\{12\}\\\) is \\\((.*?)\\\)\.", "PP 5 final")
report(got5 is not None and sp.simplify(tex(got5) - want5) == 0, "PP 5 gradient", f"{got5} vs {want5}")
report(r"\(C=-\tfrac12\)" in re.sub(r"&amp;", "", ppa[4]).replace("C=-\\tfrac12.", "\\(C=-\\tfrac12\\)") or "C&amp;=-\\tfrac12." in ppa[4], "PP 5 constant C = -1/2 printed")
report(sp.simplify(Cs + R(1, 2)) == 0, "PP 5 constant recomputed", Cs)
# PP 6: f' = cot x + x, f(pi/2) = 0
got6 = grab(ppa[5], r"\\\[f\(x\)=(.*?)\.\\\]", "PP 6 final")
F6 = tex(got6) if got6 else sp.Integer(0)
report(prim_ok(F6, sp.cot(x) + x) and sp.simplify(F6.subs(x, pi / 2)) == 0, "PP 6 f(x) recomputed", got6)
report("C&amp;=-\\dfrac{\\pi^2}{8}" in ppa[5], "PP 6 constant printed")
# PP 7: solve the equation on [0, 2pi]
kk = sp.Symbol("kk", real=True)
eq7 = sp.integrate(2 * sp.sqrt(3) * sp.cos(x) - 2 * sp.sin(x), (x, 0, kk)) - 2
roots7 = [r_ for r_ in sp.solveset(sp.simplify(eq7), kk, sp.Interval(0, 2 * pi))]
got7 = grab(ppa[6], r"k=\\tfrac\{\\pi\}\{2\}-\\tfrac\{\\pi\}\{6\}=(\\tfrac\{\\pi\}\{3\})\.", "PP 7 final")
report(got7 is not None and len(roots7) == 1 and sp.simplify(roots7[0] - tex(got7)) == 0, "PP 7 k = pi/3 is the only solution", roots7)
report(sp.simplify(2 * sp.sqrt(3) * sp.sin(x) + 2 * sp.cos(x) - 4 * sp.sin(x + pi / 6)) == 0, "PP 7 stem identity (part (i)) is true")
# PP 8: the identity of part (i) and the value
report(sp.simplify(sp.csc(x) + sp.cot(x) - sp.cot(x / 2)) == 0 or all(eqnum((sp.csc(x) + sp.cot(x) - sp.cot(x / 2)).subs(x, xv), 0) for xv in (0.4, 1.1, 2.3)),
       "PP 8 stem identity (part (i)) is true")
report(sp.simplify(I(sp.cot(x / 2), (x, pi / 3, pi / 2)) - sp.log(2)) == 0 and re.search(r"&amp;=\\ln2\.\\end", ppa[7]) is not None, "PP 8 = ln 2")
# PP question texts
for idx, s_ in [(0, r"correct primitive of \(\tan x\)"), (1, r"\int\sec^2\theta\tan^2\theta\,d\theta"), (2, r"\(\dfrac{dy}{dx}=\sin x\cos^3x\)"),
                (3, r"\int_0^{\frac{\pi}{6}}\sin x\cos x\,dx"), (4, r"\(\Big(\dfrac{\pi}{8},2\Big)\) and has a gradient of \(-1\)"),
                (4, r"\(y''=-\sec^2(2x)\)"), (5, r"\(f'(x)=\cot x+x\) and \(f\Big(\dfrac{\pi}{2}\Big)=0\)"),
                (6, r"\int_0^k\big(2\sqrt3\cos x-2\sin x\big)\,dx=2."), (6, r"\(0\le k\le2\pi\)"), (7, r"\int_{\frac{\pi}{3}}^{\frac{\pi}{2}}(\operatorname{cosec}x+\cot x)\,dx")]:
    report(s_ in ppq[idx], f"PP {idx + 1} text: {s_[:50]}")

# equation displays: every printed row must hold for the solved constant (PP 5, PP 6, PP 7) and the log-law tip
def eq_rows(html, start, subs, where):
    d = [z for z in displays(html) if z.lstrip().startswith(start)]
    if len(d) != 1:
        report(False, where, f"{len(d)} displays start with {start!r}")
        return
    body = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", d[0])
    rows = [z.replace("&amp;", "") for r_ in body.split("\\\\") for z in r_.split("\\qquad") if "=" in z]
    ok = True
    for r_ in rows:
        sides = T.split_top(r_.replace("\\log_e|\\cos x|^{-1}", "\\log_e(|\\cos x|^{-1})"), "=")   # log of the power
        vals = [tex(z, {"C": subs.get("C", sp.Integer(0))}).subs(subs) for z in sides]
        for xv in (0.37, 1.21):
            ok = ok and all(eqnum(v.subs(x, xv), vals[0].subs(x, xv)) for v in vals[1:])
    report(ok and len(rows) >= 1, where, f"{len(rows)} rows")


eq_rows(PPA, r"\begin{aligned}-1&amp;=-\tfrac12\tan", {"C": -R(1, 2)}, "PP 5 equation rows hold with C = -1/2")
eq_rows(PPA, r"\begin{aligned}\ln\Big|\sin", {"C": -pi ** 2 / 8}, "PP 6 equation rows hold with C = -pi^2/8")
eq_rows(PPA, r"\begin{aligned}2\sqrt3\sin k", {k_: pi / 3}, "PP 7 equation rows hold with k = pi/3")
eq_rows(PPA, r"k+\tfrac{\pi}{6}=\tfrac{\pi}{2}", {k_: pi / 3}, "PP 7 last line")
eq_rows(teach, r"-\log_e|\cos x|=\log_e|\cos x|^{-1}", {}, "Concept 3 tip: log-law line")

print(f"\n{CNT[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS, sep="\n  ")
    sys.exit(1)
