r"""Check of Lesson 5G (Integration Part 1 pack): Areas of compound regions, tied to the printed HTML.

Reads workspace/build/int1/l5g.html and a_5g.html.
  - Every printed working chain carries data-k="KEY" (lesson worked examples and the lesson-example
    answers). Each key must occur exactly once, or the item FAILS. Every member of every chain is read
    from the page and evaluated with sympy: an integral member \int_a^b f dx is integrated exactly, a
    bracket member [F(x)]_a^b gives F(b) - F(a) and F' must equal the integrand of the integral member
    before it, other members are numbers (mixed numbers such as 21\tfrac13 allowed). Every member must
    equal the area of that piece, computed independently from the CURVES READ FROM THE QUESTION STEM:
      'under'  : region under both curves above the x-axis (pieces cut at the meeting point);
      'between': region enclosed between two curves (sympy.solve for the meeting points, area
                 = integral of |top - bottom| between them, the top found by sampling);
      'cross'  : region between two curves from the y-axis to the far meeting point, cut at the near one.
    Rows of the 'meeting point' chains are equations: each must have exactly the roots of f(x) = g(x),
    and the last row's printed roots must be those roots; the printed points must be the meeting points.
  - Every inline or display chain inside the tip boxes, and the parenthetical arithmetic in the answers,
    is an identity: all its members must be equal (numbers, or functions of x tested symbolically).
  - Exercise 5G: every final answer printed in a_5g.html is recomputed independently (sympy): Q1-Q4 from
    the diagrams (transcribed below from the textbook figures, as drawn in figs_5g.py), Q5-Q19 from the
    equations READ from the question stems (intersections by sympy.solve, tangents by sympy.diff, areas
    by exact integration of |top - bottom|, Q17a by solve_univariate_inequality, Q19 by solving for k).
    The displayed integrals in the stems of Q5-Q7, Q9, Q10 and Q12 are evaluated and must equal the
    area. Answers are also compared with the textbook key (Y12 Ext 1 PDF 892), transcribed in KEY with
    the correct part letters (the key prints 5a, 6a, 7a for parts c).
  - Structure: the four concepts each hold demo, your turn and one worked example; the exercise has
    Q1-Q20 with bands F 1-4, D 5-18, E 19-20; there is no past-paper question (the catalogue has no
    int1-L8 row), the timed-practice note is present and names parts that exist; every figure exists.
Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5g.py
"""
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex, split_top  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))   # override only for mutation tests
x = sp.Symbol("x", real=True)
y = sp.Symbol("y", real=True)
k = sp.Symbol("k", real=True)
R = sp.Rational
FAILS, NCHECK = [], [0]


def report(flag, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if flag else "MISMATCH ") + label.replace("\n", " ")[:100]
          + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not flag:
        FAILS.append(label)
    return flag


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


# ------------------------------------------------------------------ TeX -> sympy
def T(s):
    s = s.strip().rstrip(".,;")
    s = re.sub(r"\\text\{\s*u\}\^2", "", s)
    s = re.sub(r"\\text\{[^{}]*\}", "", s)
    s = re.sub(r"\\(?:displaystyle|quad|qquad)", "", s)
    s = re.sub(r"\\sqrt\[3\]\{([^{}]*)\}", r"(\1)^{(1/3)}", s)
    s = re.sub(r"(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)
    s = re.sub(r"(\d+)\\tfrac\{(\d+)\}\{(\d+)\}", r"(\1+\2/\3)", s)
    s = s.replace("\\,", "").replace("\\big", "").replace("\\Big", "")
    return _tex(s, {"x": x, "y": y, "k": k})


def eq(a, b):
    try:
        return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0
    except Exception:
        return False


INT = re.compile(r"\\int_(\{[^{}]*\}|-?\w)\^(\{[^{}]*\}|\w)(.*?)\\,d([xy])")
BRK = re.compile(r"\\Big\[(.*?)\\Big\]_(\{[^{}]*\}|-?\w)\^(\{[^{}]*\}|\w)")


def lim(s):
    return T(s.strip("{}"))


def integrand(s):
    s = s.strip()
    if s.startswith("\\big(") and s.endswith("\\big)"):
        s = s[5:-5]
    return T(s) if s else sp.Integer(1)


def member_value(m, prev_integrand=None, where=""):
    """Value of one chain member; brackets are also checked as primitives of prev_integrand."""
    m = re.sub(r"\\text\{\s*u\}\^2", "", m)
    m = re.sub(r"\\text\{[^{}0-9]*\}|\\quad|\\qquad", "", m).strip()
    if m.startswith("{}"):
        m = m[2:]
    out, ints = m, []
    for mm in list(INT.finditer(m)):
        a, b, f, v = lim(mm.group(1)), lim(mm.group(2)), integrand(mm.group(3)), mm.group(4)
        var = x if v == "x" else y
        ints.append(f)
        out = out.replace(mm.group(0), "(" + str(sp.integrate(f.subs(x, var) if var == y else f, (var, a, b))) + ")", 1)
    for mm in list(BRK.finditer(m)):
        F, a, b = T(mm.group(1)), lim(mm.group(2)), lim(mm.group(3))
        if prev_integrand is not None:
            report(eq(sp.diff(F, x), prev_integrand), f"{where} primitive {mm.group(1)[:40]}",
                   f"F' = {sp.simplify(sp.diff(F, x))}, integrand {prev_integrand}")
        out = out.replace(mm.group(0), "(" + str(F.subs(x, b) - F.subs(x, a)) + ")", 1)
    if out.strip() == "":
        return None, ints
    out = out.replace("**", "^")
    return sp.nsimplify(sp.sympify(T(out))) if not ints and "\\Big" not in m else sp.sympify(_tex_safe(out)), ints


def _tex_safe(s):
    """Expressions in which integrals/brackets were already replaced by sympy text."""
    s = re.sub(r"\\text\{\s*u\}\^2", "", s)
    s = re.sub(r"\\text\{[^{}]*\}", "", s).strip().rstrip(".,;")
    s = re.sub(r"\\(?:quad|qquad)", "", s)
    s = re.sub(r"(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)
    if "\\" in s:
        return T(s)
    return sp.sympify(s.replace("^", "**"))


def block_by_key(html, key):
    found = re.findall(r'<div data-k="%s">(.*?)</div>' % re.escape(key), html, re.S)
    if len(found) != 1:
        report(False, f"block {key} found once", f"found {len(found)}")
        return None
    return found[0]


def rows_of(blk):
    m = re.search(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", blk, re.S)
    return [r for r in m.group(1).split("\\\\")] if m else []


def check_chain(html, key, expected, minimum=3):
    blk = block_by_key(html, key)
    if blk is None:
        return
    members = []
    for r in rows_of(blk):
        r = r.replace("\\{}", "").replace("&", "")
        members += [p for p in split_top(r, "=")]
    used, prev = 0, None
    for m in members:
        m = m.strip()
        try:
            v, ints = member_value(m, prev, key)
        except Exception as err:
            report(False, f"{key} member {m[:50]}", f"ERROR {err}")
            continue
        if ints:
            prev = ints[-1]
        if v is None:
            continue
        used += 1
        report(eq(v, expected), f"{key} member {m[:60]}", f"= {sp.nsimplify(v)}; expected {expected}")
    report(used >= minimum, f"{key}: members checked", f"{used}")


def meeting(f, g):
    return sorted(set(sp.solve(sp.Eq(f, g), x)))


def check_meet(html, key, f, g, pts_text_block=None):
    """Rows are equations with the same roots as f = g; the last row lists the roots."""
    blk = block_by_key(html, key)
    if blk is None:
        return
    roots = meeting(f, g)
    rows = [re.sub(r"^\{\}", "", r.replace("&", "").strip()).rstrip(",.") for r in rows_of(blk)]
    for r in rows[:-1]:
        lhs, rhs = split_top(r, "=")
        sol = sorted(set(sp.solve(sp.Eq(T(lhs), T(rhs)), x)))
        report(sol == roots, f"{key} row {r[:40]}", f"roots {sol} vs {roots}")
    last = rows[-1]
    lhs, rhs = split_top(last, "=")
    got = sorted(T(p) for p in re.split(r"\\text\{\s*or\s*\}", rhs))
    report(lhs.strip() == "x" and got == roots, f"{key} final row {last}", f"{got} vs {roots}")


def printed_points(text):
    return [(T(a), T(b)) for a, b in re.findall(r"\\\(\((-?[\d\\tfrac{}]+),(-?[\d\\tfrac{}]+)\)\\\)", text)]


def stem_curves(stem):
    """The equations y = ... printed in a question stem, in order, without repeats."""
    out = []
    for s in re.findall(r"\\\((.*?)\\\)", stem, re.S):
        for part in re.split(r"\\text\{and\}", s):
            part = part.replace("\\qquad", "").replace("\\quad", "").strip()
            if part.startswith("y="):
                e = T(part[2:])
                if not any(eq(e, o) for o in out):
                    out.append(e)
    return out


def area_between(f, g):
    r = meeting(f, g)
    a, b = r[0], r[-1]
    total = 0
    for lo, hi in zip(r, r[1:]):
        mid = (lo + hi) / 2
        top, bot = (f, g) if (f - g).subs(x, mid) > 0 else (g, f)
        total += sp.integrate(top - bot, (x, lo, hi))
    return sp.nsimplify(total), r, (a, b)


# ------------------------------------------------------------------ read the files
les = read("l5g.html")
ans = read("a_5g.html")
for need in ("<!-- ============ Homework ============ -->", "<!-- ============ Past papers ============ -->"):
    if les.count(need) != 1:
        sys.exit(f"FAIL: {need} not found once in l5g.html")
teach, rest = les.split("<!-- ============ Homework ============ -->")
hw, ppl = rest.split("<!-- ============ Past papers ============ -->")
CON = {}
for c in range(1, 5):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<div class="box |$)', seg, re.S)
    CON[c] = {kind: body for kind, _, body in exs}
    report([kd for kd, _, _ in exs] == ["demo", "attempt", "worked"], f"Concept {c} blocks: demo, your turn, worked example", str([kd for kd, _, _ in exs]))
    report(f"Worked example {c}, line by line" in seg, f"Concept {c}: tip box after the worked example")
CHEAD = re.split(r'<div class="ans-sec">', ans)
report(len(CHEAD) == 3 and CHEAD[1].startswith("Lesson Examples") and CHEAD[2].startswith("Textbook Homework"),
       "answer sections: Lesson Examples, Textbook Homework (no past-paper section)")
ABLK = dict(re.findall(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|$)', ans, re.S))


def stem_of(block):
    return block.split('<div class="sol-label">')[0].split("{{work")[0]


# ------------------------------------------------------------------ Concept 1: regions under two curves
for key, blk, where in (("WE1", CON[1]["worked"], les), ("C1d", CON[1]["demo"], ans), ("C1y", CON[1]["attempt"], ans)):
    cs = stem_curves(stem_of(blk))
    report(len(cs) == 2, f"{key} stem: two curves read", str(cs))
    f1, f2 = cs
    m = meeting(f1, f2)
    report(len(m) == 1, f"{key}: one meeting point", str(m))
    m = m[0]
    z1, z2 = sp.solve(f1, x), sp.solve(f2, x)
    a1, a2 = sp.integrate(f1, (x, z1[0], m)), sp.integrate(f2, (x, m, z2[0]))
    tot = a1 + a2
    numeric = sp.Integral(sp.Min(f1, f2), (x, z1[0], z2[0])).evalf(30)
    report(abs(numeric - tot) < 1e-20, f"{key}: area = integral of min(f1, f2) (numerical check)", f"{tot}")
    if key == "WE1":
        check_chain(les, "WE1c1", a1, 2), check_chain(les, "WE1c2", a2, 3), check_chain(les, "WE1c", tot, 2)
        report(eq(tot, R(2, 3)), "WE1 area = 2/3 (textbook)")
        report(printed_points(blk.split('<div class="sol-label">')[1].split("</p>")[0]) == [(m, f1.subs(x, m))], "WE1 meeting point (1, 1)")
    else:
        check_chain(ans, f"{key}-1", a1, 3), check_chain(ans, f"{key}-2", a2, 4), check_chain(ans, key, tot, 2)
        check_meet(ans, f"{key}-meet", f1, f2)
        report((m, f1.subs(x, m)) in printed_points(ABLK["C1"]), f"{key} printed meeting point ({m}, {f1.subs(x, m)})")
report(eq(sp.integrate((x - 2)**2, x), (x - 2)**3 / 3 - sp.Rational(8, 3)) or eq(sp.diff((x - 2)**3 / 3, x), (x - 2)**2),
       "Concept 1 tip: (x-2)^3/3 is a primitive of (x-2)^2")

# ------------------------------------------------------------------ Concepts 2, 3: between two curves
for c, key, blk, where in ((2, "WE2", CON[2]["worked"], les), (2, "C2d", CON[2]["demo"], ans), (2, "C2y", CON[2]["attempt"], ans),
                           (3, "WE3", CON[3]["worked"], les), (3, "C3d", CON[3]["demo"], ans), (3, "C3y", CON[3]["attempt"], ans)):
    cs = stem_curves(stem_of(blk))
    report(len(cs) == 2, f"{key} stem: two curves read", str(cs))
    f, g = cs
    area, r, (a, b) = area_between(f, g)
    report(len(r) == 2, f"{key}: two meeting points", str(r))
    pts = [(xx, f.subs(x, xx)) for xx in r]
    if key.startswith("WE"):
        check_chain(les, f"{key}c" if c == 2 else f"{key}b", area, 5)
        check_meet(les, f"{key}a", f, g)
        report(printed_points(blk.split('<div class="sol-label">')[1]) [:2] == pts, f"{key} printed points {pts}")
    else:
        check_chain(ans, key, area, 5)
        check_meet(ans, f"{key}-meet", f, g)
        half = ABLK[f"C{c}"].split("<b>Your turn.</b>")[0 if key.endswith("d") else 1]
        report(all(p in printed_points(half) for p in pts), f"{key} printed points {pts}")
    if c == 3:
        crosses = any(sp.solve(e, x) and any(a < rr < b for rr in sp.solve(e, x)) for e in (f, g))
        report(crosses, f"{key}: the region crosses the x-axis (Concept 3)")
    print(f"         {key}: area {area}")
report(eq(area_between((x - 2)**2, x)[0], area_between(x**2 - 4 * x + 2, x - 2)[0]), "WE2 and WE3 have the same area (shift down 2)")

# ------------------------------------------------------------------ Concept 4: curves that cross, from the y-axis
for key, blk, where in (("WE4", CON[4]["worked"], les), ("C4d", CON[4]["demo"], ans), ("C4y", CON[4]["attempt"], ans)):
    cs = stem_curves(stem_of(blk))
    report(len(cs) == 2, f"{key} stem: two curves read", str(cs))
    f, g = cs
    r = meeting(f, g)
    pts = [(xx, f.subs(x, xx)) for xx in r]
    report(printed_points(stem_of(blk)) == pts, f"{key} stem points are the meeting points", str(pts))
    p1 = sp.integrate(sp.Abs(f - g), (x, 0, r[0]))
    p2 = sp.integrate(sp.Abs(f - g), (x, r[0], r[1]))
    left = sp.integrate(g - f, (x, 0, r[0]))       # the second curve is on top in the left-hand piece
    right = sp.integrate(f - g, (x, r[0], r[1]))
    report(eq(left, p1) and eq(right, p2), f"{key}: second curve on top on the left, first on the right")
    if key == "WE4":
        check_chain(les, "WE4L", p1, 4), check_chain(les, "WE4R", p2, 5), check_chain(les, "WE4", p1 + p2, 2)
        report(eq(p1 + p2, 16), "WE4 total 16 (textbook)")
    else:
        check_chain(ans, f"{key}-L", p1, 4), check_chain(ans, f"{key}-R", p2, 5), check_chain(ans, key, p1 + p2, 2)
    print(f"         {key}: pieces {p1}, {p2}")

# ------------------------------------------------------------------ identities in tip boxes and answer notes
def identity_chains(text, where):
    for s in re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", text, re.S):
        s = s[0] or s[1]
        if "=" not in s or "\\int" in s or "\\Big[" in s or "\\frac{d}" in s or "\\begin{aligned}" in s and "&=" not in s:
            continue
        rows = s.replace("\\begin{aligned}", "").replace("\\end{aligned}", "").split("\\\\")
        mem = []
        for r in rows:
            mem += [p for p in split_top(r.replace("&", ""), "=") if p.strip()]
        if len(mem) < 2:
            continue
        txt = s.strip()
        if re.match(r"^(x|y|a|b|n)\s*=", txt):
            mem = mem[1:]                    # "y = 1^2 = 1": the value chain after the variable
            if len(mem) < 2:
                continue
        elif re.match(r"^\d+x\s*=", txt) or txt.startswith("x^2=") or "\\le" in txt or "g(x)" in txt:
            continue
        try:
            vals = [T(m_) for m_ in mem]
        except Exception as err:
            report(False, f"{where} identity {txt[:50]}", f"ERROR {err}")
            continue
        report(all(eq(v, vals[0]) for v in vals), f"{where} identity {txt[:60]}", str(vals[:4]))


TIPS = re.findall(r'<div class="box tip"[^>]*><div class="bt">([^<]*(?:<[^>]+>[^<]*)*?)</div>(.*?)</div>\s*(?=<div|<!--|\n\n|$)', teach, re.S)
nid = NCHECK[0]
for title, body in TIPS:
    identity_chains(body, f"tip '{title[:28]}'")
report(NCHECK[0] - nid >= 25, "tip-box identities checked", f"{NCHECK[0] - nid}")
for c in ("C2",):
    for par in re.findall(r"\(At (.*?)\.\)", ABLK[c], re.S):
        identity_chains(par, f"{c} note")
# specific printed lines
for txt, val in ((r"2\tfrac23+1\tfrac56=\tfrac{16}{6}+\tfrac{11}{6}=\tfrac{27}{6}=4\tfrac12\)", R(9, 2)),
                 (r"-10\tfrac23+13\tfrac13=2\tfrac23\)", R(8, 3))):
    report(les.count(txt) >= 1, f"tip line printed: {txt[2:40]}")

# ------------------------------------------------------------------ Exercise 5G
TQ = dict(re.findall(r'<div class="q"(?: style="[^"]*")?><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"(?: style="[^"]*")?><span class="q-num">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 21)], "Exercise 5G Q1-Q20 present", str(sorted(TQ, key=int)))
bF, rest_ = hw.split("{{band:D}}")
bD, bE = rest_.split("{{band:E}}")
report(hw.count("{{band:F}}") == 1 and [int(q) for q in re.findall(r'class="q-num">(\d+)', bF)] == [1, 2, 3, 4]
       and [int(q) for q in re.findall(r'class="q-num">(\d+)', bD)] == list(range(5, 19))
       and [int(q) for q in re.findall(r'class="q-num">(\d+)', bE)] == [19, 20], "bands F 1-4, D 5-18, E 19-20 (as the textbook)")
for q, n_ in (("1", 8), ("2", 4), ("3", 2), ("4", 2)):
    figs = re.findall(r"\{\{svg:(q5g_%s[a-h])\}\}" % q, TQ[q])
    report(figs == [f"q5g_{q}{l_}" for l_ in "abcdefgh"[:n_]], f"Q{q}: {n_} diagrams in order")


def A(txt):
    return T(txt)


def ans_parts(blk):
    bits = re.split(r"<b>([a-h])</b>", blk)
    out = {}
    for i in range(1, len(bits), 2):
        mm = re.findall(r"\\\((.*?)\\\)", bits[i + 1], re.S)
        out[bits[i]] = mm
    return out


AP = {q: ans_parts(b) for q, b in ABLK.items() if not q.startswith("C")}
report(sorted(AP, key=int) == [str(i) for i in range(1, 20)], "textbook answers Q1-Q19 (Q20 is a show-that)", str(sorted(AP, key=int)))


def first_area(q, p):
    v = AP[q].get(p) if p else re.findall(r"\\\((.*?)\\\)", ABLK[q])
    return A(v[0]) if v else None


KEY = {  # textbook key, PDF 892 (part letters corrected: the key prints 5a, 6a, 7a for the c parts)
    "1": {"a": R(1, 6), "b": R(1, 4), "c": R(3, 10), "d": R(1, 12), "e": R(2, 35), "f": R(125, 6), "g": 36, "h": R(125, 6)},
    "2": {"a": R(4, 3), "b": R(1, 6), "c": R(4, 3), "d": R(9, 2)}, "3": {"a": R(16, 3), "b": R(9, 4)},
    "4": {"a": R(50, 3), "b": R(28, 3)}, "5": {"c": R(9, 2)}, "6": {"c": R(4, 3)}, "7": {"c": 36},
    "8": {"a": R(9, 2), "b": R(125, 6), "c": R(8, 3)}, "9": {"c": 36}, "10": {"c": R(4, 3)},
    "11": {"a": R(9, 2), "b": R(125, 6), "c": R(64, 3)}, "12": {"c": R(1, 3)}, "13": {"c": R(16, 3)},
    "14": {"c": 108}, "15": {"c": R(443, 6)}, "16": {"b": R(1, 16)}, "17": {"b": R(253, 12)}, "18": {"c": R(7, 12)},
}


def cmp(q, p, val):
    got = first_area(q, p)
    tv = KEY[q][p]
    report(got is not None and eq(got, val) and eq(val, tv), f"Q{q}{p}", f"printed {got}; sympy {val}; textbook {tv}")


# Q1: the diagrams (curves and shaded part, as in the textbook figures)
Q1 = {"a": (x, x**2, 0, 1), "b": (x, x**3, 0, 1), "c": (x, x**4, 0, 1), "d": (x**2, x**3, 0, 1), "e": (x**4, x**6, 0, 1),
      "f": (3 * x + 4, x**2, -1, 4), "g": (9 - 2 * x, x**2 + 1, -4, 2), "h": (10 - x**2, x + 4, -3, 2)}
for p, (top, bot, a, b) in Q1.items():
    report(all(eq(top.subs(x, v), bot.subs(x, v)) for v in (a, b)) and (top - bot).subs(x, R(a + b, 2)) > 0,
           f"Q1{p}: the curves meet at the ends of the shaded interval, top above bottom")
    cmp("1", p, sp.integrate(top - bot, (x, a, b)))
# Q2: regions between curves x = right(y), x = left(y)
Q2 = {"a": (2 * y, y**2, 0, 2), "b": (3 * y - 2, y**2, 1, 2), "c": (5 * y - y**2 - 4, 4 - y, 2, 4), "d": (y + 4, y**2 + 2, -1, 2)}
for p, (rt, lf, c_, d_) in Q2.items():
    report(all(eq(rt.subs(y, v), lf.subs(y, v)) for v in (c_, d_)) and (rt - lf).subs(y, R(c_ + d_, 2)) > 0, f"Q2{p}: meeting points and right curve")
    cmp("2", p, sp.integrate(rt - lf, (y, c_, d_)))
report(eq((4 - y).subs(y, 4), 0) and sp.solve(sp.Eq(5 * y - y**2 - 4, 0), y) == [1, 4], "Q2c: the y-axis labels 4 and 1 are where the curves cross it")
# Q3: two areas added; Q4: subtracted
cmp("3", "a", sp.integrate((x + 2)**2, (x, -2, 0)) + sp.integrate((x - 2)**2, (x, 0, 2)))
report(meeting(x**2, (x - 3)**2) == [R(3, 2)] and (x**2).subs(x, R(3, 2)) == R(9, 4), "Q3b meeting point (3/2, 9/4)")
cmp("3", "b", sp.integrate(x**2, (x, 0, R(3, 2))) + sp.integrate((x - 3)**2, (x, R(3, 2), 3)))
h4 = 6 * x - x**2 - 8
report(sp.solve(h4, x) == [2, 4] and sp.maximum(h4, x) == 1, "Q4a: the hump meets the x-axis at 2 and 4 and stays below y = 3")
cmp("4", "a", 6 * 3 - sp.integrate(h4, (x, 2, 4)))
cmp("4", "b", sp.integrate(4 - x**2, (x, -2, 2)) - sp.integrate(1 - x**2, (x, -1, 1)))

# Q5-Q7, Q9, Q10: points from part a, the displayed integrals in part c, the area
for q in ("5", "6", "7", "9", "10"):
    stem = TQ[q]
    pa = stem.split('<span class="pl">b</span>')[0]
    cs = [T(s_) for s_ in re.findall(r"the (?:parabola|line) \\\(y=([^\\]*?(?:\\[a-z]+[^\\]*?)*?)(?:=x\(3-x\))?\\\)", pa)]
    report(len(cs) == 2, f"Q{q}a: parabola and line read", str(cs))
    area, r, _ = area_between(*cs)
    pts = printed_points(pa)
    report(pts == sorted([(xx, cs[0].subs(x, xx)) for xx in r], key=lambda t: t) or sorted(pts) == sorted((xx, cs[0].subs(x, xx)) for xx in r),
           f"Q{q}a: printed points are the intersections", str(pts))
    disp = re.search(r"\\\[(.*?)\\\]", stem, re.S).group(1)
    sides = split_top(disp.rstrip(",. "), "=")
    vals = []
    for sd in sides:
        mm = INT.search(sd)
        a, b, f = lim(mm.group(1)), lim(mm.group(2)), integrand(mm.group(3))
        vals.append((sp.integrate(f, (x, a, b)), f))
    report(len(vals) == 2 and eq(vals[0][1], vals[1][1]) and eq(vals[0][0], area), f"Q{q}c: both printed integrals equal the area", f"{[v[0] for v in vals]} vs {area}")
    cmp(q, "c", area)

# Q8, Q11: pairs of graphs
for q in ("8", "11"):
    for p in "abc":
        sp_ = re.search(r'<span data-q="%s%s">(.*?)</span>(?=<span data-q|\n|</div>)' % (q, p), TQ[q], re.S).group(1)
        cs = [T(s_[2:]) for s_ in re.findall(r"\\\((y=.*?)\\\)", sp_)]
        report(len(cs) == 2, f"Q{q}{p}: two graphs read", str(cs))
        cmp(q, p, area_between(*cs)[0])

# Q12
f12 = re.search(r"\\int_0\^1\\big\(\\sqrt\{x\}-x\^2\\big\)\\,dx", TQ["12"])
report(f12 is not None, "Q12b integral printed")
report(sp.solve(sp.Eq(x**2, sp.sqrt(x)), x) == [0, 1], "Q12: y = x^2 and x = y^2 (y = sqrt x above) meet at x = 0, 1")
cmp("12", "c", sp.integrate(sp.sqrt(x) - x**2, (x, 0, 1)))

# Q13: tangents to x^2 = 8y at A(4, 2) and B(-4, 2)
par = x**2 / 8
report("x^2=8y" in TQ["13"] and "A(4,2)" in TQ["13"] and "B(-4,2)" in TQ["13"], "Q13 stem read")
tA = sp.expand(par.subs(x, 4) + sp.diff(par, x).subs(x, 4) * (x - 4))
tB = sp.expand(par.subs(x, -4) + sp.diff(par, x).subs(x, -4) * (x + 4))
report(eq(A(AP["13"]["b"][0][2:]), tA) and AP["13"]["b"][0].startswith("y="), "Q13b tangent at A", f"{AP['13']['b'][0]} vs y = {tA}")
report(eq(A(KEY_13 := "x-2"), tA), "Q13b textbook y = x - 2")
v13 = sp.integrate(par - tB, (x, -4, 0)) + sp.integrate(par - tA, (x, 0, 4))
report(sp.solve(sp.Eq(tA, tB), x) == [0], "Q13: the tangents meet on the y-axis")
cmp("13", "c", v13)

# Q14: tangent to y = x^3 at x = 2
t14 = sp.expand((x**3).subs(x, 2) + sp.diff(x**3, x).subs(x, 2) * (x - 2))
report(eq(t14, 12 * x - 16) and "y=12x-16" in TQ["14"], "Q14a tangent y = 12x - 16")
report(meeting(x**3, t14) == [-4, 2] and (x**3).subs(x, -4) == -64, "Q14b second meeting point (-4, -64)")
cmp("14", "c", area_between(x**3, t14)[0])

# Q15
cs = [T(s_[2:]) for s_ in re.findall(r"\\\((y=.*?)\\\)", TQ["15"].split('<div class="parts')[0])]
report(len(cs) == 2, "Q15 curves read", str(cs))
area15, r15, _ = area_between(*cs)
report(r15 == [-4, 1, 2], "Q15a x-values -4, 1, 2", str(r15))
pts15 = [(xx, cs[0].subs(x, xx)) for xx in r15]
report(printed_points(ABLK["15"]) == pts15, "Q15a printed points", str(pts15))
cmp("15", "c", area15)

# Q16
cs = [T(s_[2:]) for s_ in re.findall(r"\\\((y=.*?)\\\)", TQ["16"])]
r16 = meeting(*cs)
pts16 = [(xx, cs[0].subs(x, xx)) for xx in r16]
got16 = re.findall(r"\\\(\\big\(\\tfrac12,\\tfrac18\\big\)\\\)", ABLK["16"])
report(pts16 == [(0, 0), (R(1, 2), R(1, 8)), (1, 0)] and len(got16) == 1 and "\\((0,0)\\)" in ABLK["16"] and "\\((1,0)\\)" in ABLK["16"],
       "Q16a points (0,0), (1/2,1/8), (1,0)", str(pts16))
cmp("16", "b", area_between(*cs)[0])

# Q17
f17 = (x + 1) * (x - 1) * (x - 3)
g17 = (x + 1) * (x - 1)
report("f(x)=(x+1)(x-1)(x-3)" in TQ["17"] and "g(x)=(x+1)(x-1)" in TQ["17"], "Q17 stem read")
sol17 = sp.solve_univariate_inequality(f17 > g17, x, relational=False)
report(sol17 == sp.Union(sp.Interval.open(-1, 1), sp.Interval.open(4, sp.oo)) and "\\(-1<x<1\\) or \\(x>4\\)" in ABLK["17"],
       "Q17a f > g for -1 < x < 1 or x > 4", str(sol17))
cmp("17", "b", area_between(f17, g17)[0])

# Q18: y = 12x - 32 - x^2, tangent at x = 5, B on the x-axis, C the nearer x-intercept
c18 = 12 * x - 32 - x**2
report("y=12x-32-x^2" in TQ["18"], "Q18 stem read")
t18 = sp.expand(c18.subs(x, 5) + sp.diff(c18, x).subs(x, 5) * (x - 5))
report(eq(A(AP["18"]["b"][0][2:]), t18) and eq(t18, 2 * x - 7), "Q18b tangent y = 2x - 7", str(t18))
B18 = sp.solve(t18, x)[0]
C18 = min(sp.solve(c18, x))
v18 = sp.integrate(t18, (x, B18, 5)) - sp.integrate(c18, (x, C18, 5))
report(B18 == R(7, 2) and C18 == 4, "Q18c: B = 7/2 and C = 4")
cmp("18", "c", v18)

# Q19: y = kx bisects the area under 4y = 4x - x^2
c19 = x - x**2 / 4
tot19 = sp.integrate(c19, (x, 0, 4))
kk = sp.Symbol("kk", positive=True)
xm = sp.solve(sp.Eq(c19, kk * x), x)
xm = [v for v in xm if v != 0][0]
half = sp.integrate(c19 - kk * x, (x, 0, xm))
sols = [s_ for s_ in sp.solve(sp.Eq(half, tot19 / 2), kk) if s_.is_real and 0 < s_ < 1]
got19 = re.findall(r"\\\(k=(.*?)\\\)", ABLK["19"])
report(len(sols) == 1 and len(got19) == 1 and eq(T(got19[0]), sols[0]) and eq(sols[0], 1 - 1 / sp.cbrt(2)),
       "Q19 k = 1 - 1/cbrt(2)", f"{sols} printed {got19}")

# ------------------------------------------------------------------ past papers: none; timed note
report('class="pp"' not in les and 'class="ppa"' not in ans and "Suggested time" not in les, "no past-paper question (no int1-L8 row in the catalogue)")
note = "For timed practice, do Questions 8(b), 11(c), 13, 15 and 17 above in 30 minutes."
report(ppl.count(note) == 1, "timed-practice note printed once")
report(all(f'data-q="{q}"' in hw for q in ("8b", "11c")) and all(q in TQ for q in ("13", "15", "17")), "timed note names existing parts")
report("{{sec:amber:clock:Past-paper homework:timed practice}}" in ppl, "past-paper section heading (timed practice)")

# ------------------------------------------------------------------ figures
for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}.svg exists")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:40], sep="\n  ")
    sys.exit(1)
print("ALL OK")
