r"""Check of Lesson 5H (Integration Part 1 pack): The trapezoidal rule.

The script reads the values PRINTED in workspace/build/int1/l5h.html (worked examples, tips, tutor-demo and
your-turn questions, every textbook question, the past-paper question) and in a_5h.html (lesson-example
answers, textbook answers, past-paper solution), and compares them with independent computation.

  - Every trapezoidal estimate is recomputed numerically from the function or the table READ FROM THE
    QUESTION (stem integrand and limits, or the printed table), with the number of subintervals stated,
    by an own implementation of the rule (never the page's arithmetic). Exact values use sympy.integrate.
  - Every chain of working (each \begin{aligned} block and each inline chain) is read member by member.
    Members holding an integral sign are skipped (they are the left-hand side); every other member is
    evaluated (f(k) is replaced by the function value at k) and must equal the independent value: exactly
    when it has no decimals; within half a unit of the last printed digit when it is a rounded number
    (so the printed rounding is checked); within a small relative tolerance when it is an expression built
    from rounded table values.
  - Spreadsheet tables (Worked example 35 tip, C4 answers): each printed value of phi, each doubled value,
    the row sums and the final products are recomputed to six decimal places.
  - The river graphs: the values read off the graphs in the answers equal the data the SVG is drawn from
    (figs_5h.py), and the Example 34 table equals the drawn curve at t = 4, 6, ..., 24.
  - Textbook key (Ext 1 Y12 PDF 892-893) transcribed below; every printed answer agrees with it except the
    reported key slip Q12 (key 5900, correct 2950).
  - Past paper: label in both files, 1 mark, 5 minutes, one hint (neutral), answer A checked numerically.
A template must match exactly once, otherwise the item FAILS. Exit status 1 if anything fails.
Run: python3 workspace/checks/int1_5h.py
"""
import math
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))
sys.path.insert(0, os.path.join(HERE, "..", "build", "int1"))
import figs_5h  # noqa: E402  (data of the two river graphs)

FAILS, NCHECK = [], [0]
x = sp.Symbol("x", real=True)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100]
          + ("  " + str(detail).replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def present(block, text, where):
    c = block.count(text)
    report(c == 1, f"{where} printed once: {text[:70]}", f"found {c} times")


def block(html, key):
    """The element carrying data-c="key" or data-q="key" (balanced tags), exactly once."""
    hits = [m.start() for m in re.finditer(r'data-[cq]="%s"' % re.escape(key), html)]
    if len(hits) != 1:
        report(False, f"block {key} found once", f"found {len(hits)}")
        return ""
    st = html.rfind("<", 0, hits[0])
    tag = re.match(r"<(\w+)", html[st:]).group(1)
    depth, i = 0, st
    pat = re.compile(r"<(/?)%s\b" % tag)
    for m in pat.finditer(html, st):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html[st:html.index(">", m.start()) + 1]
    return html[st:]


def grab(blk, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, blk, re.S)
    if len(found) != 1:
        report(False, f"{where} template once: {template[:60]}", f"matched {len(found)}")
        return None
    return found[0] if isinstance(found[0], tuple) else (found[0],)


# ---------------------------------------------------------------- TeX -> number
def prep(s):
    s = s.replace(r"\displaystyle", "")
    s = re.sub(r"\\text(bf)?\{[^{}]*\}", "", s)
    s = s.replace(r"\doteqdot", "=").replace(r"\div", "/").replace(r"\%", "").replace(r"\,", "")
    s = s.replace(r"\log_{10}x", r"(\ln x)/(\ln10)").replace(r"\log_a", r"\ln~").replace(r"\log_e", r"\ln~")
    s = re.sub(r"\\sqrt\[3\]\{([^{}]*)\}", r"{(\1)}^{(1/3)}", s)
    s = re.sub(r"\\sqrt\[3\](\d)", r"{\1}^{(1/3)}", s)
    s = re.sub(r"\\sqrt (\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"(?<![\d.}^_{])(\d+)\\tfrac(\{[^{}]*\}|\d)(\{[^{}]*\}|\d)", r"{(\1+\\tfrac\2\3)}", s)
    return s


def bracket(s):
    """[F(x)]_a^b written as \\Big[F\\Big]_a^b: F(b) - F(a)."""
    m = re.fullmatch(r"\s*\\Big\[(.*)\\Big\]_(\{[^{}]*\}|-?\d)\^(\{[^{}]*\}|\d)\s*", s, re.S)
    if not m:
        return None
    F = _tex(prep(m.group(1)))
    lo, hi = (_tex(prep(g.strip("{}"))) for g in (m.group(2), m.group(3)))
    return float(F.subs(x, hi) - F.subs(x, lo))


def num(s, fvals=None):
    br = bracket(s.strip().rstrip(".,"))
    if br is not None:
        return br
    s = prep(s)
    if fvals:
        s = re.sub(r"f\(([-\d.]+)\)", lambda m: "{(" + str(fvals(float(m.group(1)))) + ")}", s)
    s = s.strip().rstrip(".,; ")
    v = _tex(s)
    return complex(sp.N(v, 30)).real


def decimals(s):
    m = re.fullmatch(r"\s*-?\d+\.(\d+)\s*", s)
    return len(m.group(1)) if m else (0 if re.fullmatch(r"\s*-?\d+\s*", s) else None)


def members(math):
    """Members of a chain: aligned rows joined, split at top-level = and \\doteqdot."""
    m = math.replace(r"\begin{aligned}", "").replace(r"\end{aligned}", "")
    m = m.replace("&", "").replace(r"\\", " ").replace(r"\qquad", " ").replace(r"\quad", " ")
    m = re.sub(r"\\textbf\{[a-z]\}", "", m)
    m = m.replace(r"\doteqdot", "=")
    parts, depth, cur = [], 0, ""
    for ch in m:
        if ch in "{([":
            depth += 1
        elif ch in "})]":
            depth -= 1
        if ch == "=" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip().rstrip(".,") for p in parts if p.strip()]


def chain(math_text, expected, where, fvals=None, rel=2e-4, skip_first=True):
    """Check every member of a chain against the independent value `expected`."""
    ms = members(math_text)
    if len(ms) < 2:
        report(False, f"{where}: chain has members", math_text[:60])
        return
    for k, mem in enumerate(ms):
        if r"\int" in mem:
            continue
        try:
            v = num(mem, fvals)
        except Exception as e:  # noqa: BLE001
            report(False, f"{where} member {k} parses", f"{mem[:60]} {e}")
            continue
        d = decimals(mem)
        if d is not None:
            tol = 0.5 * 10 ** (-d) + 1e-12 if d > 0 else (1e-12 if float(mem) == expected else 0.5 + 1e-12)
            if d == 0 and abs(float(mem) - expected) > 1e-9:
                tol = 0.5 + 1e-12                     # an integer rounding (2 s.f. answer such as 37)
        elif re.search(r"\d\.\d", prep(mem)):
            tol = rel * max(1.0, abs(expected))
        else:
            tol = 1e-9 * max(1.0, abs(expected))
        report(abs(v - expected) <= tol, f"{where} member {k}: {mem[:55]}", f"value {v:.8g} expected {expected:.10g}")


def maths(blk):
    return re.findall(r"\\\[(.+?)\\\]", blk, re.S) + re.findall(r"\\\((.+?)\\\)", blk, re.S)


def trap(f, a, b, n):
    h = (b - a) / n
    return h / 2 * (f(a) + f(b) + 2 * sum(f(a + r * h) for r in range(1, n)))


def trap_data(ys, h):
    return h / 2 * (ys[0] + ys[-1] + 2 * sum(ys[1:-1]))


def fn(texstr):
    e = _tex(prep(texstr))
    g = sp.lambdify(x, e, "math")
    return e, g


def table_rows(blk):
    rows = re.findall(r"<tr>(.*?)</tr>", blk, re.S)
    out = []
    for r in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)
        out.append([c.replace(r"\(", "").replace(r"\)", "").strip() for c in cells])
    return out


def cellnum(c):
    return num(c) if c not in ("", "&emsp;") else None


L = read("l5h.html")
A = read("a_5h.html")
LESSON_END = L.index("<!-- ============ Homework")
HW = L[LESSON_END:L.index("<!-- ============ Past papers")]

# ================================================================ Concept 1: Worked example 32 and tip
we = block(L, "we32")
f32 = lambda t: 1 / t  # noqa: E731
stem = grab(we, r"Find approximations of \(\displaystyle\int_@^@\frac1x\,dx\)", "WE32 stem")
a32, b32 = (float(stem[0]), float(stem[1])) if stem else (1, 5)
t = table_rows(block(we, "we32t"))
report([num(c) for c in t[0][1:]] == [1, 2, 3, 4, 5], "WE32 table x row")
report(all(abs(num(c) - 1 / k) < 1e-12 for c, k in zip(t[1][1:], range(1, 6))), "WE32 table 1/x row")
ms = maths(we)
ca = [m for m in ms if r"\frac{5-1}{2}" in m]
report(len(ca) == 1, "WE32a chain found")
T1 = trap(f32, a32, b32, 1)
if ca:
    chain(ca[0], T1, "WE32a", fvals=f32)
report(abs(T1 - 12 / 5) < 1e-12, "WE32a independent value 2 2/5")
cb = [m for m in ms if r"1\tfrac{41}{60}" in m]
report(len(cb) == 1, "WE32b chain found")
T4 = trap(f32, a32, b32, 4)
if cb:
    chain(cb[0], T4, "WE32b", fvals=f32)
present(we, r"\int_1^5\frac1x\,dx=\int_1^2\frac1x\,dx+\int_2^3\frac1x\,dx+\int_3^4\frac1x\,dx+\int_4^5\frac1x\,dx", "WE32 dissection")
tip = block(L, "t32")
for m in maths(tip):
    if "=" in m and r"\tfrac{41}{60}" in m:
        chain(m, T4, "tip32 b")
present(tip, r"\(\dfrac{5-1}{2}=2\)", "tip32")
present(tip, r"\(1+\tfrac15=\tfrac65\)", "tip32")
present(tip, r"\(2\times\tfrac65=\tfrac{12}{5}=2\tfrac25\)", "tip32")
report(abs(num(r"\tfrac{12}{5}") - T1) < 1e-12 and abs(num(r"\tfrac{202}{120}") - T4) < 1e-12, "tip32 fractions")

# ================================================================ Concept 2: Worked example 33 and tip
we = block(L, "we33")
st = grab(we, r"approximate \(\displaystyle\int_@^@(@)\,dx\)", "WE33 stem")
fe, f33 = fn(st[2])
a, b = float(st[0]), float(st[1])
t = table_rows(block(we, "we33t"))
report(num(t[1][1]) == f33(a) and num(t[1][2]) == f33(b), "WE33 table 199, 375", t[1])
c = [m for m in maths(we) if r"\frac{5-1}{2}" in m][0]
chain(c, trap(f33, a, b, 1), "WE33a", fvals=f33)
yp = grab(we, r"Differentiating, \(y'=@\)", "WE33 y'")
ypp = grab(we, r"and \(y''=@\)", "WE33 y''")
report(sp.simplify(_tex(yp[0]) - sp.diff(fe, x)) == 0, "WE33 y' = 200-4x^3")
report(sp.simplify(_tex(ypp[0].rstrip(".")) - sp.diff(fe, x, 2)) == 0, "WE33 y'' = -12x^2")
report(all(sp.diff(fe, x, 2).subs(x, v) < 0 for v in [a + k * (b - a) / 50 for k in range(51)]), "WE33 y''<0 on [1,5]")
exact33 = float(sp.integrate(fe, (x, a, b)))
tip = block(L, "t33")
for m in maths(tip):
    if r"\Big[" in m:
        chain(m, exact33, "tip33 exact")
    elif m.startswith("f(1)="):
        chain(m, f33(1), "tip33 f(1)", fvals=f33)
    elif m.startswith("f(5)="):
        chain(m, f33(5), "tip33 f(5)", fvals=f33)
present(tip, r"\(2\times574=1148\)", "tip33")
report(exact33 > trap(f33, a, b, 1), "WE33 underestimate confirmed", exact33)

# Box 19 sign statements: concave up over, concave down under, linear exact (numerical spot checks)
report(trap(lambda t: t * t, 0, 2, 3) > 8 / 3 and trap(lambda t: -t * t, 0, 2, 3) < -8 / 3
       and abs(trap(lambda t: 3 * t + 1, 0, 2, 1) - 8) < 1e-12, "Box 19 statements on samples")
present(block(L, "box19"), "If the curve is concave up, the trapezoidal rule overestimates the integral.", "Box 19")
present(block(L, "box18"), r"\int_a^b f(x)\,dx\doteqdot\frac{b-a}{2}\Big(f(a)+f(b)\Big)", "Box 18")

# ================================================================ Concept 3: formula (identity checks)
b20 = block(L, "box20")
present(b20, r"\int_a^b f(x)\,dx\doteqdot\frac h2\Big(f(a)+2f(x_1)+2f(x_2)+\cdots+2f(x_{n-1})+f(b)\Big)", "Box 20")
present(b20, r"where \(h=\dfrac{b-a}{n}\) and \(x_r=a+rh\)", "Box 20")
present(block(L, "rearr"), r"\frac{b-a}{2n}\bigg(f(a)+f(b)+2\Big(f(x_1)+f(x_2)+\cdots+f(x_{n-1})\Big)\bigg)", "rearrangement")
dv = block(L, "deriv")
present(dv, r"\(a=x_0\) and \(b=x_n\)", "derivation endpoints")
present(dv, r"\int_a^{x_1}f(x)\,dx+\int_{x_1}^{x_2}f(x)\,dx+\cdots", "derivation dissection")
for n in (2, 5, 7):
    g = math.sin
    aa, bb = 0.3, 2.1
    h = (bb - aa) / n
    pieces = sum(h / 2 * (g(aa + r * h) + g(aa + (r + 1) * h)) for r in range(n))
    box20 = h / 2 * (g(aa) + 2 * sum(g(aa + r * h) for r in range(1, n)) + g(bb))
    rea = (bb - aa) / (2 * n) * (g(aa) + g(bb) + 2 * sum(g(aa + r * h) for r in range(1, n)))
    report(abs(pieces - box20) < 1e-12 and abs(box20 - rea) < 1e-12, f"Box 20 = sum of trapezia = rearrangement (n={n})")

# ================================================================ Worked example 34 and tip
we = block(L, "we34")
t1 = table_rows(block(we, "we34t1"))
ts = [num(c) for c in t1[0][1:]]
flows = [num(c) for c in t1[1][1:]]
report(ts == list(range(4, 25, 2)), "WE34 times 4..24")
creek = figs_5h.pchip(figs_5h.CREEK_FLOW)
report(all(abs(creek(tt) - q) < 1e-9 for tt, q in zip(ts, flows)), "WE34 table = drawn creek curve")
t2 = table_rows(block(we, "we34t2"))
R = [num(c) for c in t2[1][1:]]
report(all(abs(r - q * 3600 / 1e6) < 1e-9 for r, q in zip(R, flows)), "WE34 R = flow x 3600 / 10^6", R)
present(we, r"Here \(h=2\) and \(n=10\)", "WE34")
T34 = trap_data([q * 3600 / 1e6 for q in flows], 2)
report(abs(T34 - 223.2) < 1e-9, "WE34 independent value 223.2", T34)
cs = [m for m in maths(we) if "223.2" in m]
report(len(cs) == 2, "WE34 two chains")
Rf = dict(zip(ts, [q * 3600 / 1e6 for q in flows]))
for k, m in enumerate(cs):
    ms_ = members(m)
    # the explicit sums (members without f(...) and dots) are checked in full
    for mem in ms_[2:]:
        v = num(mem)
        report(abs(v - T34) < 1e-9, f"WE34 chain {k + 1}: {mem[:50]}", v)
    if k == 0:
        terms = [float(u) for u in re.findall(r"[\d.]+", ms_[2])]
        want = [Rf[4]] + [2 * Rf[tt] for tt in range(6, 23, 2)] + [Rf[24]]
        report(len(terms) == 11 and all(abs(p - q) < 1e-9 for p, q in zip(terms, want)), "WE34 chain 1 terms", terms)
    else:
        present(m, r"\frac{24-4}{20}", "WE34 second formula factor")
        report(abs((24 - 4) / 20 - 1) < 1e-12, "WE34 (b-a)/(2n) = 1")
        inner = re.search(r"2\(([\d.+\s\\qquad]+)\)", m.replace("\\\\", "").replace("&", "").replace(r"\qquad", ""))
        vals = [float(u) for u in re.findall(r"[\d.]+", inner.group(1))] if inner else []
        report(vals == [Rf[tt] for tt in range(6, 23, 2)], "WE34 chain 2 middle values", vals)
        present(m, r"2.16+2\times110.52", "WE34 chain 2")
        report(abs(sum(vals) - 110.52) < 1e-9, "WE34 middle sum 110.52")
present(we, "about 223 million cubic feet", "WE34 conclusion")
tip = block(L, "t34")
for p, q in re.findall(r"2\\times([\d.]+)=([\d.]+)", tip):
    report(abs(2 * float(p) - float(q)) < 1e-9, f"tip34 2 x {p} = {q}")
report(len(re.findall(r"2\\times([\d.]+)=([\d.]+)", tip)) == 9, "tip34 nine doubled values")
for p, q in re.findall(r"(\d+)\\times3600=(\d+(?:\\,\d{3})*)", tip):
    report(int(p) * 3600 == int(q.replace(r"\,", "")), f"tip34 {p} x 3600")
present(tip, r"\(2.16+221.04=223.2\)", "tip34")
report(abs(0.36 + 1.8 - 2.16) < 1e-12 and abs(2 * 110.52 - 221.04) < 1e-9, "tip34 arithmetic")

# ================================================================ Worked example 35, tip and spreadsheet
phi = lambda t: math.exp(-t * t / 2) / math.sqrt(2 * math.pi)  # noqa: E731
we = block(L, "we35")
for p, q in (("0", "0.398942"), ("0.1", "0.396953"), ("1", "0.241971")):
    present(we, r"\phi(%s)=%s" % (p, q), "WE35")
    report(f"{phi(float(p)):.6f}" == q, f"WE35 phi({p}) to 6 dp")
present(we, r"\int_0^1\phi(x)\,dx\doteqdot0.341", "WE35 result")
T35 = trap(phi, 0, 1, 10)
report(f"{T35:.3f}" == "0.341", "WE35 trapezoidal estimate rounds to 0.341", T35)
exact35 = 0.5 * math.erf(1 / math.sqrt(2))
present(we, "The correct value to four decimal places is 0.3413.", "WE35")
report(f"{exact35:.4f}" == "0.3413" and T35 < exact35, "WE35 correct value 0.3413 and estimate smaller", exact35)
report(all((v * v - 1) * phi(v) < 0 for v in [k / 100 for k in range(100)]), "phi concave down on [0,1)")
present(we, r"\(\tfrac12h=0.05\)", "WE35")
present(we, "<code>=L4*0.05</code>", "WE35")


def sheet_check(blk, a, h, where, transposed):
    rows = table_rows(blk)
    if transposed:                         # columns: label | x | phi | row 4
        body = [r for r in rows[1:] if len(r) >= 3 and r[0] not in ("L4", "L5")]
        xs = [num(r[-3]) for r in body]
        ph = [r[-2] for r in body]
        r4 = [r[-1] for r in body]
    else:
        xs = [num(c) for c in rows[0][1:]]
        ph, r4 = rows[1][1:], rows[2][1:]
    want_x = [round(a + k * h, 10) for k in range(11)]
    report(len(xs) == 11 and all(abs(p - q) < 1e-12 for p, q in zip(xs, want_x)), f"{where} x-values", xs)
    report(all(f"{phi(q):.6f}" == p for p, q in zip(ph, want_x)), f"{where} phi values (6 dp)")
    w = [phi(want_x[0])] + [2 * phi(v) for v in want_x[1:-1]] + [phi(want_x[-1])]
    report(all(f"{p:.6f}" == q for p, q in zip(w, r4)), f"{where} row 4 values (6 dp)", r4[:3])
    return sum(w), h / 2 * sum(w)


S, T = sheet_check(block(L, "t35t"), 0, 0.1, "tip35 sheet", True)
tip = block(L, "t35")
rows = table_rows(block(tip, "t35t"))
L4 = [r for r in rows if r and r[0] == "L4"][0][1]
L5 = [r for r in rows if r and r[0] == "L5"][0][1]
report(f"{S:.6f}" == L4 and f"{T:.6f}" == L5, "tip35 L4 and L5", (L4, L5))
present(tip, r"\(L4\doteqdot%s\)" % L4, "tip35")
present(tip, r"\(0.05\times%s\doteqdot%s\)" % (L4, L5), "tip35")
present(tip, "The estimate 0.3411 is a little smaller than the correct value 0.3413", "tip35")
report(f"{T:.4f}" == "0.3411", "tip35 estimate 0.3411")

# ================================================================ lesson examples: questions and answers
# C1 (12/x on [1,4]; 60/x on [2,5]): one and three subintervals
for key, akey, tkey in (("c1d", "c1", "c1dt"), ("c1y", "c1", "c1yt")):
    q = block(L, key)
    st = grab(q, r"Find approximations of \(\displaystyle\int_@^@@\,dx\)", key)
    e, g = fn(st[2])
    a, b = float(st[0]), float(st[1])
    present(q, "three subintervals", key)
    tb = table_rows(block(A, tkey))
    report(all(abs(num(c) - g(num(xx))) < 1e-12 for xx, c in zip(tb[0][1:], tb[1][1:])) and
           [num(c) for c in tb[0][1:]] == [a + k for k in range(4)], f"{key} answer table")
ans = block(A, "c1")
demo, yt = ans.split("<b>Your turn.</b>")
for part, (a, b, g) in ((demo, (1, 4, lambda t: 12 / t)), (yt, (2, 5, lambda t: 60 / t))):
    cs = [m for m in maths(part) if r"\begin{aligned}" in m]
    report(len(cs) == 2, "C1 two chains")
    chain(cs[0], trap(g, a, b, 1), f"C1 a [{a},{b}]", fvals=g)
    chain(cs[1], trap(g, a, b, 3), f"C1 b [{a},{b}]", fvals=g)

# C2 (50x - x^4 and x^3 + 1 on [1,3])
ans = block(A, "c2")
demo, yt = ans.split("<b>Your turn.</b>")
for key, part, sign in (("c2d", demo, -1), ("c2y", yt, 1)):
    st = grab(block(L, key), r"approximate \(\displaystyle\int_@^@(@)\,dx\)", key)
    e, g = fn(st[2])
    a, b = float(st[0]), float(st[1])
    T1 = trap(g, a, b, 1)
    ex = float(sp.integrate(e, (x, a, b)))
    cs = [m for m in maths(part) if r"\begin{aligned}" in m]
    chain(cs[0], T1, f"{key} trapezoidal", fvals=g)
    chain(cs[1], ex, f"{key} exact")
    for m in maths(part):
        if m.startswith("f(1)=") or m.startswith("f(3)="):
            chain(m, g(float(m[2])), f"{key} {m[:4]}", fvals=g)
    d2 = sp.diff(e, x, 2)
    yp = grab(part, r"so \(y'=@\)", key)
    ypp = grab(part, r"and \(y''=@\)", key)
    report(sp.simplify(_tex(yp[0]) - sp.diff(e, x)) == 0 and sp.simplify(_tex(ypp[0]) - d2) == 0, f"{key} y', y''")
    report(all(sign * d2.subs(x, a + k * (b - a) / 40) > 0 for k in range(41)), f"{key} concavity sign")
    report((ex - T1) * sign < 0, f"{key} over/under statement agrees", (T1, ex))
    present(part, "overestimates" if sign > 0 else "underestimates", key)

# C3 (dam, tank)
q = block(L, "c3d")
tq = table_rows(block(q, "c3dt"))
tt = [num(c) for c in tq[0][1:]]
fl = [num(c) for c in tq[1][1:]]
ans = block(A, "c3")
demo, yt = ans.split("<b>Your turn.</b>")
tr = table_rows(block(A, "c3dR"))
Rd = [num(c) for c in tr[1][1:]]
report(all(abs(r - v * 3600 / 1e6) < 1e-9 for r, v in zip(Rd, fl)), "C3 demo R = flow x 0.0036", Rd)
present(demo, r"\(50\times3600=180\,000\)", "C3 demo")
present(demo, r"\(900\times3600=3\,240\,000\)", "C3 demo")
Td = trap_data([v * 3600 / 1e6 for v in fl], tt[1] - tt[0])
Rmap = dict(zip(tt, [v * 3600 / 1e6 for v in fl]))
cs = [m for m in maths(demo) if r"\begin{aligned}" in m]
report(len(cs) == 2, "C3 demo two chains")
for k, m in enumerate(cs):
    chain(m, Td, f"C3 demo chain {k + 1}", fvals=lambda v: Rmap[int(round(v))])
present(demo, "About 31.6 million cubic metres", "C3 demo")
report(abs(Td - 31.59) < 1e-9, "C3 demo independent value 31.59", Td)
q = block(L, "c3y")
tq = table_rows(block(q, "c3yt"))
tt = [num(c) for c in tq[0][1:]]
fl = [num(c) for c in tq[1][1:]]
Ty = trap_data(fl, tt[1] - tt[0])
fmap = dict(zip(tt, fl))
cs = [m for m in maths(yt) if r"\begin{aligned}" in m]
for k, m in enumerate(cs):
    chain(m, Ty, f"C3 your turn chain {k + 1}", fvals=lambda v: fmap[int(round(v))])
present(yt, "About 1225 litres", "C3 your turn")

# C4 (spreadsheets)
ans = block(A, "c4")
for key, tkey, a, b in (("c4d", "c4dt", 0, 0.5), ("c4y", "c4yt", 1, 2)):
    st = grab(block(L, key), r"the integral \(\displaystyle\int_@^{@}\phi(x)\,dx\)", key)
    report((float(st[0]), float(st[1])) == (a, b), f"{key} limits read", st)
    present(block(L, key), "using the trapezoidal rule with 10 subintervals", key)
    h = (b - a) / 10
    S, T = sheet_check(block(A, tkey), a, h, f"{key} sheet", True)
    Tn = trap(phi, a, b, 10)
    report(abs(T - Tn) < 1e-15, f"{key} sheet = trapezoidal rule")
    part = ans.split("<b>Your turn.</b>")[0 if key == "c4d" else 1]
    c = [m for m in maths(part) if r"\begin{aligned}" in m][0]
    present(c, f"{S:.6f}", f"{key} L4 in chain")
    present(part, f"The sum of row 4 is \\(L4\\doteqdot{S:.6f}\\)", f"{key} L4 stated")
    present(c, f"{T:.6f}", f"{key} L5 in chain")
    chain(c, Tn, f"{key} chain", rel=1e-6)
    hh = (b - a) / 100
    T100 = trap(phi, a, b, 100)
    present(part, f"(With 100 subintervals the estimate is {T100:.4f}.)", f"{key} 100 subintervals")
    conc = "underestimate" if key == "c4d" else "overestimate"
    present(part, f"so this is an {conc}", key)
    ok = all(((v * v - 1) * phi(v) < 0) == (key == "c4d") for v in [a + (k + 0.5) * (b - a) / 50 for k in range(50)])
    report(ok and ((T100 > Tn) == (key == "c4d")), f"{key} concavity and direction")
present(ans, r"type <code>=L4*0.025</code>, because \(\tfrac12h=0.025\)", "C4 demo")

# ================================================================ textbook exercise
report('q-num">7<' not in HW, "Q7 (doubtful table) omitted")
for n in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17):
    report(HW.count(f'<span class="q-num">{n}</span>') == 1, f"Q{n} printed once")
report(HW.index("{{band:D}}") < HW.index('q-num">8<') and HW.index("{{band:E}}") < HW.index('q-num">15<')
       and HW.index("{{band:D}}") > HW.index('q-num">6<') and HW.index("{{band:E}}") > HW.index('q-num">14<'),
       "bands F 1-6, D 8-14, E 15-17 as in the textbook")
KEY = {"1a": 40, "1b": 22, "1c": -26, "2a": 164, "3": 30, "5b": 10, "5c": sp.Rational(32, 3), "5d": 6.25,
       "6b": sp.Rational(101, 10), "8a": "0.73", "8b": "4.5", "8c": "3.4", "8d": "37", "9a": "1.12",
       "9b": "0.705", "9c": "22.9", "9d": "0.167", "10": 9.2, "11": 550, "12": 5900, "13a": "0.7489",
       "13b": "3.0", "15d": 876400}


def ansblk(n):
    return block(A, f"a{n}")


# Q1
q = block(L, "q1")
tabs = re.findall(r"<table.*?</table>", q, re.S)
a1 = ansblk(1)
for lab, tb in zip("abc", tabs):
    rows = table_rows(tb)
    xs = [num(c) for c in rows[0][1:]]
    ys = [num(c) for c in rows[1][1:]]
    T = (ys[0] + ys[1]) / 2 * (xs[1] - xs[0])
    got = grab(a1, r"<b>%s</b> \(@\)" % lab, f"A1{lab}")
    if got:
        chain(got[0], T, f"A1{lab}")
    report(T == KEY["1" + lab], f"Q1{lab} key {KEY['1' + lab]}")
# Q2
rows = table_rows(block(L, "q2"))
xs = [num(c) for c in rows[0][1:]]
ys = [num(c) for c in rows[1][1:]]
T2 = (ys[0] + ys[1]) / 2 * (xs[1] - xs[0]) + (ys[1] + ys[2]) / 2 * (xs[2] - xs[1])
for m in maths(ansblk(2)):
    if "=" in m and not m.startswith("h="):
        chain(m, T2, "A2 " + m[:12])
report(T2 == KEY["2a"] and abs(trap_data(ys, xs[1] - xs[0]) - T2) < 1e-12, "Q2 key 164 and formula agrees")
# Q3
rows = table_rows(block(L, "q3"))
xs = [num(c) for c in rows[0][1:]]
ys = [num(c) for c in rows[1][1:]]
T3 = trap_data(ys, xs[1] - xs[0])
for m in maths(ansblk(3)):
    if "=" in m and not m.startswith("h="):
        chain(m, T3, "A3")
report(abs(T3 - KEY["3"]) < 1e-12, "Q3 key 30")
# Q5
q = block(L, "q5")
st = grab(q, r"approximate \(\displaystyle\int_@^@@\,dx\)", "Q5 stem")
e5, g5 = fn(st[2])
a, b = float(st[0]), float(st[1])
a5 = ansblk(5)
rows = table_rows(a5)
report([num(c) for c in rows[1][1:]] == [g5(v) for v in range(5)], "A5a table", rows[1])
T5 = trap(g5, a, b, 4)
ex5 = sp.integrate(e5, (x, a, b))
for m in maths(a5):
    if r"\Big[" in m:
        chain(m, float(ex5), "A5c exact")
    elif m.startswith(r"\tfrac12(0+"):
        chain(m, T5, "A5b")
    elif m.startswith(r"10\tfrac23-10"):
        chain(m, float(ex5) - T5, "A5d error")
    elif m.startswith(r"\tfrac23\div"):
        chain(m.replace(r"\times100\%", r"\times100"), float((ex5 - T5) / ex5 * 100), "A5d percent")
report(abs(T5 - KEY["5b"]) < 1e-12 and abs(float(ex5) - float(KEY["5c"])) < 1e-12 and abs(float((ex5 - T5) / ex5 * 100) - KEY["5d"]) < 1e-9,
       "Q5 key 10, 10 2/3, 6 1/4 %", (T5, ex5))
report(sp.diff(e5, x, 2) == -2, "A5 y'' = -2")
# Q6
q = block(L, "q6")
st = grab(q, r"approximate \(\displaystyle\int_@^@@\,dx\)", "Q6 stem")
e6, g6 = fn(st[2])
a, b = float(st[0]), float(st[1])
a6 = ansblk(6)
rows = table_rows(a6)
report(all(abs(num(c) - g6(v)) < 1e-12 for c, v in zip(rows[1][1:], range(1, 6))), "A6a table", rows[1])
T6 = trap(g6, a, b, 4)
for m in maths(a6):
    if m.startswith(r"\tfrac12\big(6"):
        chain(m, T6, "A6b")
report(abs(T6 - KEY["6b"]) < 1e-12, "Q6 key 10 1/10")
present(a6, r"\(y'=-6x^{-2}\) and \(y''=12x^{-3}\)", "A6c")
report(sp.simplify(sp.diff(e6, x, 2) - _tex(r"12x^{-3}")) == 0, "A6c y'' = 12x^-3 (and Q6c stem)")
present(q, r"\(y''=12x^{-3}\)", "Q6c stem")

# Q8 and Q9: integrands read from the stems
for qn, n, letters in ((8, 2, "abcd"), (9, 4, "abcd")):
    q = block(L, f"q{qn}")
    items = re.findall(r'<span class="pl">([a-d])</span>\\\(\\displaystyle\\int_(\{[^}]*\}|\d)\^(\{[^}]*\}|\d)(.+?)\\,dx\\\)', q)
    report(len(items) == 4, f"Q{qn} four integrals read", len(items))
    aq = ansblk(qn)
    present(q, "three function values" if qn == 8 else "five function values", f"Q{qn}")
    for lab, lo, hi, integ in items:
        lo, hi = float(lo.strip("{}")), float(hi.strip("{}"))
        e, g = fn(integ)
        T = trap(g, lo, hi, n)
        # answer line for this part: from <b>lab</b> to the next <b> or end
        seg = re.search(r"<b>%s</b>(.*?)(?=<b>[a-d]</b>|</div></div>)" % lab, aq, re.S).group(1)
        hstr = grab(seg, r"\(h=@\)", f"A{qn}{lab} h")
        report(hstr is not None and abs(num(hstr[0]) - (hi - lo) / n) < 1e-12, f"A{qn}{lab} h = {(hi - lo) / n}")
        ms_ = [m for m in maths(seg) if not m.startswith("h=")]
        joined = "=".join(ms_)
        chain(joined, T, f"A{qn}{lab}", rel=3e-4)
        final = members(joined)[-1]
        report(final == KEY[f"{qn}{lab}"], f"Q{qn}{lab} key {KEY[f'{qn}{lab}']}", final)
        # the rounding asked for: 2 s.f. (Q8) or 3 s.f. (Q9)
        sf = 2 if qn == 8 else 3
        r = float(f"{T:.{sf}g}")
        report(abs(float(final) - r) < 1e-12, f"Q{qn}{lab} rounded to {sf} s.f.", (T, final))
# Q10
rows = table_rows(block(L, "q10"))
ts = [num(c) for c in rows[0][1:]]
vs = [num(c) for c in rows[1][1:]]
T10 = trap_data(vs, ts[1] - ts[0])
for m in maths(ansblk(10)):
    if "=" in m and not m.startswith("h="):
        chain(m, T10, "A10")
present(ansblk(10), "9.2\\) metres", "A10")
report(abs(T10 - KEY["10"]) < 1e-12, "Q10 key 9.2")
# Q11, Q12: values from the SVGs drawn for the questions
svg11 = open(os.path.join(SRC, "svg", "q5h_11.svg"), encoding="utf-8").read()
svg12 = open(os.path.join(SRC, "svg", "q5h_12.svg"), encoding="utf-8").read()
lab11 = re.findall(r">(\d+)</text>", svg11)
lab12 = re.findall(r">(\d+)</text>", svg12)
report(lab11 == ["20", "18", "17", "0", "10", "20", "30", "40"], "Q11 figure labels", lab11)
report(sorted(lab12[:7], key=int) == sorted(["5", "10", "13", "14", "11", "7", "3"], key=int) and lab12[-4:] == ["0", "100", "200", "300"],
       "Q12 figure labels", lab12)
T11 = trap_data([0, 20, 18, 17, 0], 10)
T12 = trap_data([5, 10, 13, 14, 11, 7, 3], 50)
for m in maths(ansblk(11)):
    if "=" in m and not m.startswith("h="):
        chain(m.replace(r"\ \text{m}^2", ""), T11, "A11")
for m in maths(ansblk(12)):
    if "=" in m and not m.startswith("h="):
        chain(m.replace(r"\ \text{m}^2", ""), T12, "A12")
report(T11 == KEY["11"], "Q11 key 550")
report(T12 == 2950 and KEY["12"] == 2 * T12, "Q12: correct 2950; key 5900 is a slip (double)", T12)
present(block(L, "q12"), "measured at 50-metre intervals", "Q12 stem")
present(block(L, "q11"), "at 10-metre intervals", "Q11 stem")
# Q13
q = block(L, "q13")
st = grab(q, r"approximate \(\displaystyle\int_@^@@\,dx\)", "Q13 stem")
e13, g13 = fn(st[2])
T13 = trap(g13, float(st[0]), float(st[1]), 4)
a13 = ansblk(13)
c = [m for m in maths(a13) if m.startswith(r"\tfrac18")][0]
chain(c, T13, "A13a", rel=1e-6)
report(members(c)[-1] == KEY["13a"] and f"{T13:.4f}" == "0.7489", "Q13a key 0.7489 (4 dp)")
c = [m for m in maths(a13) if m.startswith(r"\pi")][0]
pv = members(c)
report(abs(num(pv[1]) - 4 * 0.7489) < 1e-12 and pv[-1] == "3.0" and f"{4 * T13:.1f}" == "3.0" and 4 * T13 < math.pi,
       "Q13b pi ~ 3.0 and less than pi", pv)
report(abs(float(sp.integrate(e13, (x, 0, 1))) - math.pi / 4) < 1e-12, "Q13 integral is pi/4")
# Q14
q = block(L, "q14")
present(q, r"\int_1^5\ln x\,dx\doteqdot\ln54", "Q14 stem")
c = [m for m in maths(ansblk(14)) if r"\ln54" in m][0]
tail = r"&\doteqdot\ln54,\ \text{since }\sqrt{2880}\doteqdot53.7."
present(c, tail, "A14 last line")
ms_ = members(c.replace(tail, ""))
T14 = trap(math.log, 1, 5, 4)
report(len(ms_) == 5, "A14 chain members", len(ms_))
for mem in ms_[1:]:
    report(abs(num(mem) - T14) < 1e-12, f"A14 member {mem[:40]}")
report(f"{math.sqrt(2880):.1f}" == "53.7" and round(math.sqrt(2880)) == 54, "A14 sqrt(2880) = 53.7, which rounds to 54")
report(1 * 4 * 9 * 16 * 5 == 2880, "A14 product 2880")
# Q15
a15 = ansblk(15)
n15 = 12000
lo, hi = 2 * n15 * math.sqrt(n15) / 3, math.sqrt(n15) * (4 * n15 + 3) / 6
s15 = sum(math.sqrt(k) for k in range(1, n15 + 1))
present(a15, r"\(876\,356\le\text{sum}\le876\,411\)", "A15d bounds")
report(math.floor(lo) == 876356 and math.floor(hi) == 876410 and round(hi) == 876411 and lo <= s15 <= hi, "A15d bounds values", (lo, hi, s15))
report(round(lo, -2) == round(hi, -2) == KEY["15d"], "Q15d key 876 400")
present(a15, r"\(876\,400\)", "A15d")
ns = sp.Symbol("n", positive=True)
report(sp.simplify(sp.Rational(2, 3) * ns * sp.sqrt(ns) + sp.sqrt(ns) / 2 - sp.sqrt(ns) * (4 * ns + 3) / 6) == 0, "A15c algebra")
for nn in (1, 2, 5, 30):
    S = sum(math.sqrt(k) for k in range(1, nn + 1))
    report(2 * nn * math.sqrt(nn) / 3 <= S <= math.sqrt(nn) * (4 * nn + 3) / 6 + 1e-12, f"Q15 inequalities hold for n={nn}")
# Q16
q = block(L, "q16")
items = re.findall(r'<span class="pl">([a-c])</span>\\\(\\displaystyle\\int_(\d+)\^\{(\d+)\}(.+?)\\,dx\\\)', q)
report(len(items) == 3, "Q16 three integrals read", len(items))
rows = table_rows(block(A, "a16t"))
ns16 = [int(c) for c in rows[0][1:]]
report(ns16 == [5, 10, 20, 100], "A16 subinterval counts")
for (lab, lo, hi, integ), row in zip(items, rows[1:]):
    e, g = fn(integ)
    vals = [trap(g, float(lo), float(hi), n) for n in ns16]
    report(row[0] == lab and all(f"{v:.4f}" == c for v, c in zip(vals, row[1:])), f"A16{lab} estimates (4 dp)", row)
    ex = float(sp.integrate(e, (x, float(lo), float(hi)))) if lab != "c" else math.sqrt(math.pi) / 2 * math.erf(10)
    report(abs(vals[-1] - ex) < abs(vals[0] - ex), f"A16{lab} estimates approach the integral")
    trend = "decrease" if lab in "ac" else "increase"
    report(all((vals[i + 1] < vals[i]) == (trend == "decrease") for i in range(3) if abs(vals[i + 1] - vals[i]) > 1e-9), f"A16{lab} {trend}")
present(block(A, "a16"), "In parts <b>a</b> and <b>c</b> the estimates decrease, and in part <b>b</b> they increase.", "A16")
# Q17: readings equal the data the graph is drawn from
q17 = figs_5h.pchip(figs_5h.Q17_FLOW)
a17 = ansblk(17)
ra = grab(a17, "<b>a</b> Flow rates @ m³/s give", "A17a readings")
rb = grab(a17, "<b>b</b> Flow rates @ m³/s give", "A17b readings")
ra = [float(v) for v in re.findall(r"[\d.]+", ra[0])]
rb = [float(v) for v in re.findall(r"[\d.]+", rb[0])]
report(all(abs(q17(t) - v) < 1e-9 for t, v in zip((0, 6, 12, 18), ra)) and len(ra) == 4, "A17a readings = graph at 17:40 .. 11:40", ra)
report(all(abs(q17(t) - v) < 1e-9 for t, v in zip(range(24, 43, 3), rb)) and len(rb) == 7, "A17b readings = graph at 05/05 17:40 .. 06/05 11:40", rb)
report(figs_5h.Q17_TIMES[0] == "04/05/2004 17:40" and figs_5h.Q17_TIMES[4] == "05/05/2004 17:40", "Q17 axis times")
Ra = [num(c) for c in table_rows(block(A, "a17a"))[1][1:]]
Rb = [num(c) for c in table_rows(block(A, "a17b"))[1][1:]]
report(all(abs(p - 3.6 * v) < 1e-9 for p, v in zip(Ra, ra)), "A17a R = 3.6 x flow", Ra)
report(all(abs(p - 3.6 * v) < 1e-9 for p, v in zip(Rb, rb)), "A17b R = 3.6 x flow", Rb)
Va, Vb = trap_data(Ra, 6), trap_data(Rb, 3)
m17 = maths(a17)
for i, m in enumerate(m17):
    if r"\tfrac62" in m:
        chain(m, Va, "A17a volume")
    elif r"\tfrac32" in m:
        report(m17[i + 1].startswith("=1.5"), "A17b chain continues on the next line")
        chain(m + m17[i + 1], Vb, "A17b volume")
present(a17, "about 144 thousand cubic metres", "A17a")
present(a17, "about 509 thousand cubic metres", "A17b")
report(round(Va) == 144 and round(Vb) == 509, "A17 rounded volumes", (Va, Vb))
c = [m for m in maths(a17) if m.startswith("508.68")][0]
report(abs(num(members(c)[1]) - Vb / Va) < 0.05 and members(c)[1] == "3.5", "A17c ratio 3.5", Vb / Va)
peak_t = max((t / 100 for t in range(3000, 3800)), key=q17)
report(33.5 <= peak_t <= 34.5, "A17 peak near 06/05/2004 03:40 (t = 34 h)", peak_t)
rain = dict(figs_5h.Q17_RAIN)
report(max(rain, key=rain.get) > 30 and max(rain, key=rain.get) < 31, "A17 heaviest rain just after 23:40 (t = 30 h)")

# ================================================================ past paper
LAB = "Sydney Grammar School, 2023, Trial Examination, Form VI Mathematics <span style=\"white-space:nowrap\">Extension 1, Q3</span>"
for name, html in (("lesson", L), ("answers", A)):
    present(html, LAB, f"PP1 label in {name}")
pp = block(L, "pp1")
present(L, "<b>Suggested time: 5 minutes</b></span><span><b>1 mark</b>", "pp-intro")
report(pp.count('class="hint"') == 1, "PP1 one hint")
hint = re.search(r'<div class="hint">(.*?)</div>', pp, re.S).group(1)
bad = [w for w in ("trapez", "rule", "formula", "width", "height", "average", "log", "law", "add", "multiply", "2", "4")
       if w in hint.lower()]
report(not bad, "PP1 hint is a neutral starting question", bad)
report(pp.count('<span class="mk">1 mark</span>') == 1, "PP1 marks 1")
report(math.floor(1.5 * 1 / 5 + 0.999) * 5 == 5, "time 1.5 x 1 mark -> 5 minutes")
opts = re.findall(r"<span>\(([A-D])\)&ensp;\\\((.+?)\\\)</span>", pp)
report([o[0] for o in opts] == list("ABCD"), "PP1 four options")
for base in (3.0, math.e, 10.0):
    lg = lambda v: math.log(v) / math.log(base)  # noqa: E731
    T = (4 - 2) / 2 * (lg(2) + lg(4))
    vals = {"A": 3 * lg(2), "B": lg(6), "C": (lg(2) + lg(4)) / 2, "D": 3 * base / 2}
    report(abs(vals["A"] - T) < 1e-12 and all(abs(vals[k] - T) > 1e-3 for k in "BCD"), f"PP1 only (A) equals the estimate (a={base:.3g})")
for o, t_ in opts:
    report(abs(num(t_.replace(r"\dfrac", r"\frac")) - {"A": 3 * math.log(2), "B": math.log(6), "C": (math.log(2) + math.log(4)) / 2, "D": None}.get(o, 0)) < 1e-12
           if o != "D" else "3a" in t_, f"PP1 option {o} as printed: {t_}")
ppa = block(A, "pp1")
chain([m for m in maths(ppa) if r"\begin{aligned}" in m][0].replace(r"\text{Area}", ""), 3 * math.log(2), "PP1 solution chain")
present(ppa, "<b>Answer (A).</b>", "PP1 answer")
present(ppa, r"\log_a(2\times4)=\log_a8", "PP1 option B reason")
# timed-practice note: the questions it names exist
note = re.search(r'<p class="small">(.*?)</p>', L[L.index("<!-- ============ Past papers"):], re.S).group(1)
present(note, "do Questions 5, 9(c), 12, 13 and 14 above in 25 minutes", "timed-practice note")
report('q-num">5<' in HW and '<span class="pl">c</span>\\(\\displaystyle\\int_4^8' in block(L, "q9") and all(f'q-num">{n}<' in HW for n in (12, 13, 14)),
       "timed-practice questions exist")

# ================================================================ summary
print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:")
    for f_ in FAILS:
        print("  " + f_)
    sys.exit(1)
print("ALL OK")
