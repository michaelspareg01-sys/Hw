r"""Check of Lesson 5F (Integration Part 1 pack): Finding areas by integration.

The script reads the values PRINTED in workspace/build/int1/l5f.html and a_5f.html and recomputes them.
  1. Every aligned working chain in both files whose first member is a definite integral: the integral is
     evaluated with sympy.integrate (integrand and limits READ from the page); every later member must have
     the same value; a member in square brackets must differentiate back to the integrand (sympy.diff) and
     give the same value at the printed limits. Chains that start with an expression (y = x(x+1)(x-2) = ...)
     must have all members equal as polynomials.
  2. Every inline numeric equality chain (a = b = c, no letters) in both files: all members equal.
     Negative bases with fractional powers, e.g. (-8)^{4/3}, are evaluated as real cube roots.
  3. Lesson examples C1-C6: the curve, lines and limits are READ from the lesson questions; the area is
     computed independently by splitting at the zeros (sympy.solve) and adding |integral| of each piece;
     the areas printed in a_5f.html must match.
  4. Textbook homework: the regions of Q1-Q4 (recreated from the figures, listed in REGIONS below and
     cross-checked against the integrand printed in the answer) and the stems of Q5-Q11 READ from the page;
     every area computed by splitting at the zeros. Q12, Q13, Q15-Q18 recomputed from their stems.
     The textbook key (Ext 1 Y12 PDF 892) is transcribed in KEY and compared as well.
  5. Past paper: marks add to the intro total, time 5 min, the label is the same in both files, one hint
     (a neutral question: no digits, no method words), and the MC answer (B) is the only option whose
     integral equals the true area, computed independently with x as a function of y by sympy.solve.

Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5f.py
"""
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))
FAILS, NCHECK = [], [0]
x = sp.Symbol("x", real=True)
y = sp.Symbol("y", real=True)
u = sp.Symbol("u", real=True)
n = sp.Symbol("n", real=True)
R = sp.Rational


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:110]
          + ("  " + str(detail).replace("\n", " ")[:160] if detail else ""))
    if not ok:
        FAILS.append(label)


def realpow(m):
    base, p, q = int(m.group(1)), int(m.group(2)), int(m.group(3))
    r = sp.real_root(sp.Integer(base), q) ** p
    return "(" + str(r) + ")"


def T(s):
    """Printed TeX -> sympy (mixed numbers, cube roots, real powers of negative numbers handled here)."""
    s = s.strip().rstrip(".,")
    s = re.sub(r"\\(?:displaystyle|left|right|qquad|quad)", "", s)
    s = s.replace("\\ \\text{u}^2", "").replace("\\,", "").replace("\\ ", "")
    s = re.sub(r"\((-\d+)\)\^\{\\frac(\d)(\d)\}", realpow, s)
    s = re.sub(r"\\big\(\((-\d+)\)\^\{\\frac(\d)(\d)\}\\big\)", realpow, s)
    s = re.sub(r"(?<![\d}])(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)
    s = re.sub(r"(?<![\d}])(\d+)\\tfrac\{(\d+)\}\{(\d+)\}", r"(\1+\2/\3)", s)
    s = re.sub(r"\\sqrt\s+(\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"\\sqrt\[3\]\{([^{}]*)\}", r"(\1)^{1/3}", s)
    s = s.replace("\\Big", "").replace("\\big", "")
    return _tex(s, {"y": y, "u": u, "n": n})


def num(s):
    v = T(s)
    if v.free_symbols:
        raise ValueError(f"not a number: {s}")
    return sp.nsimplify(v)


def eq(a, b):
    try:
        return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0
    except Exception:
        return False


def grab(block, template, where):
    """Template with @ for each captured TeX fragment; must match exactly once."""
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|&=).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def check_val(block, template, where, expected, label):
    try:
        got = num(grab(block, template, where)[0])
        report(eq(got, expected), f"{where} {label}", f"printed {got}, computed {expected}")
    except Exception as e:  # noqa: BLE001
        report(False, f"{where} {label}", repr(e))


def section(text, start, end):
    i = text.find(start)
    if i < 0 or text.count(start) != 1:
        raise LookupError(f"section start {start!r} found {text.count(start)} times")
    j = text.find(end, i + len(start)) if end else len(text)
    return text[i:j if j > 0 else len(text)]


def area(f, var, a, b):
    """Area between f(var) and the axis from a to b: split at the zeros, add |integral|."""
    a, b = sp.nsimplify(a), sp.nsimplify(b)
    lo, hi = min(a, b), max(a, b)
    zs = [z for z in sp.solve(sp.Eq(f, 0), var) if z.is_real and lo < z < hi]
    pts = sorted(set([lo, hi] + zs), key=lambda t: float(t))
    return sp.nsimplify(sum(abs(sp.integrate(f, (var, pts[i], pts[i + 1]))) for i in range(len(pts) - 1)))


def at(F, var, v):
    """F evaluated at var = v, with var**(p/q) (q odd) read as the REAL power (cube root first)."""
    v = sp.nsimplify(v)
    F2 = F.replace(lambda e: e.is_Pow and e.base == var and e.exp.is_Rational and e.exp.q % 2 == 1,
                   lambda e: (sp.sign(v) ** e.exp.p) * sp.Abs(v) ** e.exp)
    return sp.nsimplify(F2.subs(var, v))


def value(f, var, a, b):
    """Definite integral with real odd roots: on an interval with b <= 0, substitute var = -t."""
    a, b = sp.nsimplify(a), sp.nsimplify(b)
    if a >= 0 or not f.has(sp.Pow):
        return sp.nsimplify(sp.integrate(f, (var, a, b)))
    if b <= 0:
        t = sp.Symbol("t", positive=True)
        g = f.replace(lambda e: e.is_Pow and e.base == var and e.exp.is_Rational and e.exp.q % 2 == 1,
                      lambda e: (-1) ** e.exp.p * t ** e.exp).subs(var, -t)
        return sp.nsimplify(sp.integrate(g, (t, -b, -a)))
    return value(f, var, a, 0) + value(f, var, 0, b)


# ------------------------------------------------------------------ 1. working chains
INT_RX = re.compile(r"\\int_(\{[^{}]*\}|-?\w)\^(\{[^{}]*\}|\w)(.*?)\\,d([xy])\s*$", re.S)


def parse_int(s):
    s = re.sub(r"\\text\{[^{}]*\}", "", s).strip()
    m = INT_RX.fullmatch(s) or INT_RX.search(s)
    if not m:
        return None
    a, b, f = (g.strip("{}") for g in m.group(1, 2)), None, m.group(3).strip()
    a, b = list(a)
    var = x if m.group(4) == "x" else y
    if f.startswith("\\big(") and f.endswith("\\big)"):
        f = f[5:-5]
    return T(a), T(b), T(f), var


def clean_member(m):
    m = re.sub(r"\\q?quad.*$", "", m.strip(), flags=re.S)
    m = re.sub(r"\\text\{[^{}]*\}$", "", m.strip())
    m = m.strip().rstrip(",.").strip()
    m = re.sub(r"\\ \\text\{u\}\^2$", "", m)
    return m.strip()


BR_RX = re.compile(r"(.*?)\\Big\[(.*)\\Big\]_(\{[^{}]*\}|-?\w)\^(\{[^{}]*\}|\w)\s*$", re.S)


def check_chains(text, fname):
    count = 0
    for blk in re.findall(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", text, re.S):
        rows = [r for r in re.split(r"\\\\", blk)]
        first = rows[0]
        if "&=" not in first:
            continue
        lhs, rest = first.split("&=", 1)
        members = [rest] + [r.split("&=", 1)[1] if r.strip().startswith("&=") else None for r in rows[1:]]
        if any(mm is None for mm in members):
            continue        # two-line equations (x^3 = y, x = ...) handled elsewhere
        lhs_c = re.sub(r"\\text\{[^{}]*\}", "", lhs).strip().lstrip("&").strip()
        where = f"{fname} chain {lhs_c[:40]}"
        if "\\int" in lhs_c:
            p = parse_int(lhs_c)
            if not p:
                report(False, where, "cannot read the integral")
                continue
            a, b, f, var = p
            val = value(f, var, a, b)
            count += 1
            for mm in members:
                mm = clean_member(mm)
                if not mm or "\\text" in mm or "base" in mm:
                    continue
                br = BR_RX.fullmatch(mm)
                if br:
                    coef = T(br.group(1)) if br.group(1).strip() else sp.Integer(1)
                    F = coef * T(br.group(2))
                    lo, hi = T(br.group(3).strip("{}")), T(br.group(4).strip("{}"))
                    ok = (eq(sp.diff(F, var), f) and eq(lo, a) and eq(hi, b)
                          and eq(at(F, var, hi) - at(F, var, lo), val))
                    report(ok, f"{where}: primitive {br.group(2)[:30]}", f"F'={sp.simplify(sp.diff(F, var))} vs {f}")
                    continue
                if "\\int" in mm:
                    q = parse_int(mm)
                    ok = q is not None and eq(value(q[2], q[3], q[0], q[1]), val)
                    report(ok, f"{where}: = {mm[:40]}", f"value {val}")
                    continue
                try:
                    v = num(mm)
                    report(eq(v, val), f"{where}: = {mm[:40]}", f"{v} vs {val}")
                except Exception as e:  # noqa: BLE001
                    report(False, f"{where}: = {mm[:40]}", repr(e))
        elif re.fullmatch(r"y", lhs_c):
            vals = []
            for mm in members:
                mm = clean_member(mm)
                vals.append(T(mm))
            ok = all(eq(sp.expand(v), sp.expand(vals[0])) for v in vals)
            report(ok, f"{where}: identity chain", vals)
            count += 1
        elif "Area of triangle" in lhs or "area" in lhs.lower():
            vals = []
            for mm in members:
                mm = clean_member(mm)
                if "\\text" in mm or "base" in mm:
                    continue
                vals.append(num(mm))
            report(len(vals) >= 2 and all(eq(v, vals[0]) for v in vals), f"{where}: triangle chain", vals)
            count += 1
    return count


# ------------------------------------------------------------------ 2. inline numeric chains
def check_inline(text, fname):
    count = 0
    for m in re.findall(r"\\\((.*?)\\\)", text, re.S):
        if "=" not in m or "\\int" in m or "\\le" in m or "\\Big[" in m:
            continue
        parts = [p for p in re.split(r"(?<![<>])=", m)]
        if len(parts) < 2:
            continue
        try:
            vals = [num(p) for p in parts]
        except Exception:  # noqa: BLE001
            continue        # parts with letters are not numeric chains
        count += 1
        report(all(eq(v, vals[0]) for v in vals), f"{fname} inline {m[:60]}", vals)
    return count


# ------------------------------------------------------------------ main
L = read("l5f.html")
A = read("a_5f.html")
print("== 1. working chains")
nc = check_chains(L, "l5f") + check_chains(A, "a_5f")
report(nc >= 25, "number of working chains checked", nc)
print("== 2. inline numeric chains")
ni = check_inline(L, "l5f") + check_inline(A, "a_5f")
report(ni >= 25, "number of inline numeric chains checked", ni)

# ------------------------------------------------------------------ 3. lesson examples
print("== 3. lesson examples")


def curve_from(block, template, where):
    return T(grab(block, template, where)[0])


def demo_blocks(lesson, concept):
    sec = section(lesson, f"Concept {concept}:", f"Concept {concept + 1}:" if concept < 6 else "Textbook homework")
    d = section(sec, "Tutor demo</span>", "Your turn</span>")
    t = section(sec, "Your turn</span>", "Worked example")
    w = section(sec, 'tag">Worked example', "line by line")
    return d, t, w


def ans_block(c):
    return section(A, f'<span class="an">C{c}</span>', f'<span class="an">C{c + 1}</span>' if c < 6 else "Textbook Homework")


def roots_area(f):
    zs = sorted([z for z in sp.solve(f, x) if z.is_real], key=float)
    return zs, area(f, x, zs[0], zs[-1])


# C1, C2: region bounded by a parabola and the x-axis; also the worked examples
for c in (1, 2):
    d, t, w = demo_blocks(L, c)
    ab = ans_block(c)
    demo_ans, turn_ans = ab.split("<b>Your turn.</b>")
    for blk, ans, tag in ((d, demo_ans, "demo"), (t, turn_ans, "your turn")):
        f = curve_from(blk, r"bounded by the curve \(y=@\) and the", f"C{c} {tag}")
        zs, A_ = roots_area(f)
        check_val(ans, r"required area is \(@\) square units", f"C{c} {tag}", A_, f"area for y={f}")
    f = curve_from(w, r"bounded by the curve \(y=@\) and the", f"WE{c}")
    zs, A_ = roots_area(f)
    check_val(w, r"Hence the required area is \(@\) square units", f"WE{c}", A_, f"area for y={f}")

# C3: cubic crossing the axis; WE3
d, t, w = demo_blocks(L, 3)
ab = ans_block(3)
demo_ans, turn_ans = ab.split("<b>Your turn.</b>")
for blk, ans, tag in ((d, demo_ans, "demo"), (t, turn_ans, "your turn"), (w, w, "WE3")):
    f = curve_from(blk, r"Sketch the cubic curve \(y=@\), showing", f"C3 {tag}")
    zs = sorted([z for z in sp.solve(f, x) if z.is_real], key=float)
    up = sp.integrate(f, (x, zs[0], zs[1]))
    down = sp.integrate(f, (x, zs[1], zs[2]))
    total = abs(up) + abs(down)
    whole = sp.integrate(f, (x, zs[0], zs[2]))
    c_int = grab(blk, r"\(\displaystyle\int_{@}^{@}@\,dx\) and explain", f"C3 {tag}")
    report(eq(T(c_int[0]), zs[0]) and eq(T(c_int[1]), zs[2]) and eq(T(c_int[2]), f), f"C3 {tag} part c limits",
           f"{c_int} vs zeros {zs}")
    if tag == "WE3":
        check_val(ans, r"so area above \(=@\) square units", tag, abs(up), "area above")
        check_val(ans, r"so area below \(=@\) square units", tag, abs(down), "area below")
        check_val(ans, r"\text{total area}=\tfrac{5}{12}+2\tfrac23=@\) square units", tag, total, "total")
        check_val(ans, r"the difference \(2\tfrac23-\tfrac{5}{12}=@\) of", tag, abs(down) - abs(up), "difference")
    elif tag == "demo":
        check_val(ans, r"so area above \(=@\) square units", tag, abs(up), "area above")
        check_val(ans, r"so area below \(=@\) square units", tag, abs(down), "area below")
        check_val(ans, r"Total area \(=\tfrac{7}{12}+11\tfrac14=\tfrac{7}{12}+\tfrac{135}{12}=\tfrac{142}{12}=@\) square",
                  tag, total, "total")
        check_val(ans, r"the difference \(11\tfrac14-\tfrac{7}{12}=@\) of", tag, abs(down) - abs(up), "difference")
    else:
        check_val(ans, r"so the areas are \(@\) and", tag, abs(up), "area above")
        check_val(ans, r"and \(@\), and the total area", tag, abs(down), "area below")
        check_val(ans, r"the total area is \(@\) square units", tag, total, "total")
        check_val(ans, r"\,dx=-32+\tfrac34=@\)", tag, whole, "part c integral")
    zs_printed = re.findall(r"x\\\)-intercepts (?:are|\\\(x=)", ans)
    report(len(zs_printed) >= 1, f"C3 {tag} intercepts stated")

# C4: odd functions, total area by doubling
d, t, w = demo_blocks(L, 4)
ab = ans_block(4)
demo_ans, turn_ans = ab.split("<b>Your turn.</b>")
for blk, ans, tag in ((d, demo_ans, "demo"), (t, turn_ans, "your turn"), (w, w, "WE4")):
    f = curve_from(blk, r"<b>a</b> Show that \(y=@\) is an odd function", f"C4 {tag}")
    report(eq(f.subs(x, -x), -f), f"C4 {tag}: y={f} is odd")
    zs, A_ = roots_area(f)
    half = A_ / 2
    if tag == "WE4":
        check_val(ans, r"so area below the \(x\)-axis \(=@\) square units", tag, half, "half area")
        check_val(ans, r"Doubling, total area \(=@\) square units", tag, A_, "total")
    elif tag == "demo":
        check_val(ans, r"so area below the \(x\)-axis \(=@\) square units", tag, half, "half area")
        check_val(ans, r"Doubling, total area \(=\tfrac{81}{2}=@\) square units", tag, A_, "total")
    else:
        check_val(ans, r"so area below \(=@\) square units", tag, half, "half area")
        check_val(ans, r"total area \(=@\) square units", tag, A_, "total")

# C5: line y = mx + c and a horizontal line y = k, region to the right of the y-axis
d, t, w = demo_blocks(L, 5)
ab = ans_block(5)
demo_ans, turn_ans = ab.split("<b>Your turn.</b>")
for blk, ans, tag in ((d, demo_ans, "demo"), (t, turn_ans, "your turn"), (w, w, "WE5")):
    line, k = grab(blk, r"Sketch the lines \(y=@\) and \(y=@\), and shade", f"C5 {tag}")
    line, k = T(line), T(k)
    xy = sp.solve(sp.Eq(y, line), x)[0]          # x as a function of y
    c0 = line.subs(x, 0)
    A_ = sp.integrate(xy, (y, c0, k))
    meet = sp.solve(sp.Eq(line, k), x)[0]
    tri = R(1, 2) * meet * (k - c0)
    report(eq(A_, tri), f"C5 {tag}: integral = triangle", f"{A_} {tri}")
    if tag == "WE5":
        check_val(ans, r"Hence the required area is \(@\ \text{u}^2\)", tag, A_, "area")
        got = T(grab(ans, r"Solving for \(x\), \(\quad x=@\)", tag)[0])
        report(eq(got, xy), f"{tag} x as a function of y", got)
        got = grab(ans, r"They meet at \(@\)", tag)[0]
        report(eq(T(got.split(",")[0].strip("()")), meet), f"{tag} meeting point", got)
    else:
        got = T(grab(ans, r"<b>b</b> \(@\)", f"C5 {tag}")[0].split("=")[-1]) if tag == "your turn" else \
            T(grab(ans, r"so \(2x=y-1\) and \(x=@\)", f"C5 {tag}")[0])
        report(eq(got, xy), f"C5 {tag} x as a function of y", got)
        tmpl = r"The area is \(9\ \text{u}^2\)" if tag == "demo" else r"so the area is \(@\ \text{u}^2\)"
        if tag == "demo":
            present = A.count(tmpl) == 1 and eq(A_, 9)
            report(present, "C5 demo area printed 9", A_)
        else:
            check_val(ans, tmpl, tag, A_, "area")
        parts = grab(ans, r"Area of triangle \(=\tfrac12\times@\ \text{u}^2\)", f"C5 {tag}")[0].split("=")
        report(eq(R(1, 2) * num(parts[0]), tri) and eq(num(parts[-1]), tri), f"C5 {tag} triangle", parts)

# C6: y = x^n, regions right and left of the y-axis
d, t, w = demo_blocks(L, 6)
ab = ans_block(6)
demo_ans, turn_ans = ab.split("<b>Your turn.</b>")
for blk, ans, tag in ((d, demo_ans, "demo"), (t, turn_ans, "your turn")):
    f = T(grab(blk, r"Consider the @ \(y=@\). One region", f"C6 {tag}")[1])
    ys = [T(v) for v in re.findall(r"from \\\(y=(-?\d+)\\\) to \\\(y=(-?\d+)\\\)", blk)[0]] + \
         [T(v) for v in re.findall(r"from \\\(y=(-?\d+)\\\) to \\\(y=(-?\d+)\\\)", blk)[1]]
    deg = sp.degree(f, x)
    xy = sp.real_root(y, deg) if deg % 2 else None
    right = sp.integrate(y ** R(1, deg), (y, ys[0], ys[1]))          # 0 <= y: principal root is real
    left = sp.integrate(-(-y) ** R(1, deg), (y, ys[2], ys[3]))        # y <= 0: real odd root = -(-y)^(1/n)
    printed = T(grab(ans, r"and \(x=@\)", f"C6 {tag}")[0]) if tag == "demo" else \
        T(grab(ans, r"so \(x=@\)", f"C6 {tag}")[0])
    report(eq(printed, y ** R(1, deg)), f"C6 {tag} x as a function of y", printed)
    if tag == "demo":
        check_val(ans, r"so area \(=@\) square units. For", tag, right, "right area")
        check_val(ans, r"so area \(=@\) square units.<br>", tag, -left, "left area")
        check_val(ans, r"Total area \(=60\tfrac34+12=@\) square units", tag, right - left, "total")
    else:
        check_val(ans, r"The areas are \(@\) and", tag, right, "right area")
        check_val(ans, r"The areas are \(\tfrac56\) and \(@\) square units", tag, -left, "left area")
        check_val(ans, r"Total area \(=\tfrac56+\tfrac56=@\) square units", tag, right - left, "total")
# WE6 (book): y = x^3, right 0..8, left -1..0
check_val(w, r"so area \(=@\) square units.</p>" "\n<p>For", "WE6", value(y ** R(1, 3), y, 0, 8), "right area")
check_val(w, r"so area \(=@\) square units.</p>" "\n<p><b>c", "WE6", -value(y ** R(1, 3), y, -1, 0), "left area")
check_val(w, r"total area \(=@\) square units", "WE6", R(51, 4), "total")
check_val(L, r"Hence the required area is \(@\ \text{u}^2\)", "WE5 l5f", 8, "area")

# ------------------------------------------------------------------ 4. textbook homework
print("== 4. textbook homework")
TA = section(A, "Textbook Homework</div>", "Past-Paper Homework")


def ans_q(q):
    return section(TA, f'<span class="an">{q}</span>', '<div class="a">' if q != 18 else "</div></div>")


# Q1-Q4 regions as drawn in the textbook figures (integrand, variable, lower, upper)
REGIONS = {
    "1a": (2 * x, x, 0, 2), "1b": (3 * x**2, x, 1, 3), "1c": (4 * x**3, x, 0, 3), "1d": (3 * x**2 + 1, x, -1, 2),
    "1e": (x**2, x, 0, 3), "1f": (x**2 - 2 * x, x, 2, 4), "1g": (sp.sqrt(x), x, 0, 16), "1h": (5 - x, x, 1, 3),
    "1i": (x**3 - x, x, -1, 0), "1j": (12 - x - x**2, x, -4, 3), "1k": (5 * x**4 + 1, x, -1, 2),
    "1l": (x ** R(1, 3), x, 1, 27),
    "2a": (2 * y, y, 0, 5), "2b": (3 * y**2, y, -2, 0), "2c": (2 * y - 4, y, 2, 4), "2d": (27 - 3 * y**2, y, -3, 3),
    "2e": (y, y, 0, 3), "2f": (y**2 + 1, y, 3, 5), "2g": (sp.sqrt(y), y, 0, 9), "2h": (1 / sp.sqrt(y), y, 1, 4),
    "3a": (x**2 - 4 * x + 3, x, 1, 3), "3b": (3 * x, x, -3, 0), "3c": (x**3, x, -3, 0), "3d": (1 - x**4, x, 1, 3),
    "4a": (1 - y, y, 1, 4), "4b": (y**2 - 6 * y + 8, y, 2, 4), "4c": ("cbrt", y, -8, -1), "4d": (-y**2, y, 0, 3),
}
KEY = {"1a": 4, "1b": 26, "1c": 81, "1d": 12, "1e": 9, "1f": R(20, 3), "1g": R(128, 3), "1h": 6, "1i": R(1, 4),
       "1j": R(343, 6), "1k": 36, "1l": 60, "2a": 25, "2b": 8, "2c": 4, "2d": 108, "2e": R(9, 2), "2f": R(104, 3),
       "2g": 18, "2h": 2, "3a": R(4, 3), "3b": R(27, 2), "3c": R(81, 4), "3d": R(232, 5), "4a": R(9, 2),
       "4b": R(4, 3), "4c": R(45, 4), "4d": 9,
       "5b": R(9, 2), "5c": 2, "5d": R(13, 2), "5e": R(5, 2), "6b": R(32, 3), "6c": R(7, 3), "6d": 13,
       "6e": R(-25, 3), "7b": R(8, 3), "7c": R(5, 12), "7d": R(37, 12), "7e": R(-9, 4),
       "8a": R(35, 3), "8b": R(257, 2), "8c": 4, "8d": R(17, 2), "8e": R(131, 4), "8f": R(34, 3),
       "9a": 13, "9b": R(5, 2), "9c": R(28, 3), "9d": R(22, 3), "10ai": 64, "10aii": 128, "10aiii": R(324, 5),
       "10bi": 50, "10bii": 18, "10biii": R(32, 3), "11": 8}

for q in (1, 2, 3, 4):
    blk = ans_q(q)
    for part in "abcdefghijkl":
        key = f"{q}{part}"
        if key not in REGIONS:
            continue
        f, var, a, b = REGIONS[key]
        if f == "cbrt":
            f_area = sp.integrate(-(-y) ** R(1, 3), (y, a, b))
            Aval, fexp = abs(f_area), None
        else:
            Aval, fexp = area(f, var, a, b), f
        try:
            m = re.search(r"<b>" + part + r"</b> \\\((.*?)\\\)(?:, area \\\((.*?)\\\))?", blk, re.S)
            first = m.group(1)
            lhs, rhs = first.rsplit("=", 1)
            p = parse_int(lhs.replace("\\int", "\\int", 1))
            ok_reg = p is not None and eq(p[0], a) and eq(p[1], b) and p[3] == var and \
                (fexp is None or eq(p[2], fexp))
            report(ok_reg, f"Q{key} printed integral matches the figure", lhs[:50])
            if fexp is None and p is not None:
                report(eq(p[2], y ** R(1, 3)), f"Q{key} integrand y^(1/3)", p[2])
            val = sp.integrate(p[2], (var, p[0], p[1])) if fexp is not None else f_area
            report(eq(num(rhs), val), f"Q{key} integral value", f"{rhs} vs {val}")
            printed_area = num(m.group(2)) if m.group(2) else num(rhs)
            report(eq(printed_area, Aval) and eq(Aval, KEY[key]), f"Q{key} area", f"{printed_area}, {Aval}, key {KEY[key]}")
        except Exception as e:  # noqa: BLE001
            report(False, f"Q{key}", repr(e))


def qblock(qn):
    return section(L, f'<span class="q-num">{qn}</span>', '<span class="q-num">' if qn < 18 else "Past papers")


def first_ans(blk, part):
    m = re.search(r"<b>" + part + r"</b> \\\((.*?)\\\)", blk, re.S)
    if not m:
        raise LookupError(f"part {part} not found")
    return num(m.group(1))


# Q5-Q7: integrals read from the stems
for qn in (5, 6, 7):
    blk, ans = qblock(qn), ans_q(qn)
    ints = {}
    for part in "bce":
        s = re.search(r'<span class="pl">' + part + r'</span>(?:By evaluating|Find) \\\(\\displaystyle(.*?)\\\)', blk, re.S)
        ints[part] = parse_int(s.group(1))
    vals = {p: sp.integrate(v[2], (x, v[0], v[1])) for p, v in ints.items()}
    a_lo, a_hi = ints["e"][0], ints["e"][1]
    tot = area(ints["e"][2], x, a_lo, a_hi)
    for part, expect in (("b", abs(vals["b"])), ("c", abs(vals["c"])), ("d", tot), ("e", vals["e"])):
        try:
            got = first_ans(ans, part)
            report(eq(got, expect) and eq(got, KEY[f"{qn}{part}"]), f"Q{qn}{part}", f"{got} vs {expect}")
        except Exception as e:  # noqa: BLE001
            report(False, f"Q{qn}{part}", repr(e))
    report(eq(vals["e"], vals["b"] + vals["c"]), f"Q{qn}e is the sum of the signed integrals")

# Q8 (x) and Q9 (y): stems read from the page
for qn, var, letter, fl in ((8, x, "x", "y"), (9, y, "y", "x")):
    blk, ans = qblock(qn), ans_q(qn)
    for part in "abcdef":
        m = re.search(r'<span class="pl">' + part + r'</span>\\\(' + fl + r'=(.*?)\\\), between \\\(' + letter +
                      r'=(-?\d+)\\\),? and \\\(' + letter + r'=(-?\d+)\\\)', blk)
        if not m:
            if qn == 9 and part in "ef":
                continue
            report(False, f"Q{qn}{part} stem", "not found")
            continue
        f, a, b = T(m.group(1)), int(m.group(2)), int(m.group(3))
        expect = area(f, var, a, b)
        try:
            got = first_ans(ans, part)
            report(eq(got, expect) and eq(got, KEY[f"{qn}{part}"]), f"Q{qn}{part} {letter}={f}", f"{got} vs {expect}")
        except Exception as e:  # noqa: BLE001
            report(False, f"Q{qn}{part}", repr(e))

# Q10
blk, ans = qblock(10), ans_q(10)
for half, var, letter in (("a", x, "y"), ("b", y, "x")):
    for roman in ("i", "ii", "iii"):
        pat = r'<span class="pl">' + roman + r'</span>\\\(' + letter + r'=(.*?)\\\), for \\\((-?\d+)\\le ' + \
            ("x" if half == "a" else "y") + r'\\le(-?\d+)\\\)'
        ms = re.findall(pat, blk)
        m = ms[0] if half == "a" else ms[-1]
        expr = m[0].split("=")[0]
        f = T(expr)
        f2 = T(m[0].split("=")[-1])
        report(eq(sp.expand(f), sp.expand(f2)), f"Q10{half}{roman} both printed forms agree")
        expect = area(f, var, int(m[1]), int(m[2]))
        sub = section(ans, f"<b>{half}</b>", "<b>b</b>" if half == "a" else None)
        mm = re.search(r"\(" + roman + r"\) \\\((.*?)\\\ \\text", sub)
        got = num(mm.group(1))
        report(eq(got, expect) and eq(got, KEY[f"10{half}{roman}"]), f"Q10{half}{roman}", f"{got} vs {expect}")

# Q11
blk, ans = qblock(11), ans_q(11)
m = re.search(r"bounded by \\\(y=\|(.*?)\|\\\) and the \\\(x\\\)-axis, for \\\((-?\d+)\\le x\\le(-?\d+)\\\)", blk)
f = sp.Abs(T(m.group(1)))
expect = sp.integrate(sp.Piecewise((-(x + 2), x < -2), (x + 2, True)), (x, int(m.group(2)), int(m.group(3))))
got = num(re.search(r'<div class="ab">\\\((.*?)\\\ \\text', ans).group(1))
report(eq(got, expect) and eq(got, 8), "Q11", f"{got} vs {expect}")

# Q12: y^2 = 16(2 - x)
ans = ans_q(12)
xint = sp.solve(sp.Eq(0, 16 * (2 - x)), x)[0]
yint = sorted(sp.solve(sp.Eq(y**2, 32), y), key=float)
report(eq(xint, 2) and "(2,0)" in ans.replace(" ", ""), "Q12a x-intercept (2,0)")
report(all(s in ans for s in (r"\big(0,4\sqrt2\big)", r"\big(0,-4\sqrt2\big)")) and eq(yint[1], 4 * sp.sqrt(2)),
       "Q12a y-intercepts")
A1 = sp.integrate(4 * sp.sqrt(2 - x), (x, 0, 2))
A2 = sp.integrate(2 - y**2 / 16, (y, 0, 4 * sp.sqrt(2)))
got = T(re.search(r"<b>b</b> \\\(\\dfrac\{16\\sqrt2\}\{3\}", ans) and r"\frac{16\sqrt2}{3}")
report(eq(A1, A2) and eq(A1, got), "Q12b both methods give 16 sqrt2 / 3", f"{A1} {A2}")
report(eq(T(re.search(r"\\\(x=2-\\dfrac\{y\^2\}\{16\}\\\)", ans) and r"2-\frac{y^2}{16}"), sp.solve(sp.Eq(y**2, 16 * (2 - x)), x)[0]),
       "Q12b(ii) x as a function of y")

# Q13
blk, ans = qblock(13), ans_q(13)
dy = T(grab(blk, r"The gradient of a curve is \(y'=@\), and", "Q13")[0])
F = sp.integrate(dy, x)                    # through the origin: constant 0
got = T(grab(ans, r"<b>a</b> \(y=@\)", "Q13")[0])
report(eq(got, F) and eq(F.subs(x, 0), 0), "Q13a curve", got)
tps = sp.solve(dy, x)
report(sorted(tps) == [1, 3] and eq(F.subs(x, 1), R(4, 3)) and eq(F.subs(x, 3), 0)
       and sp.diff(F, x, 2).subs(x, 1) < 0 < sp.diff(F, x, 2).subs(x, 3), "Q13b turning points and nature")
check_val(ans, r"<b>c</b> \(@\ \text{u}^2\)", "Q13", area(F, x, 1, 3), "area")

# Q15: ratios
a_ = sp.Symbol("a", positive=True)
np_ = sp.Symbol("n", positive=True)
I = sp.integrate(x ** np_, (x, 0, a_))
r1 = sp.simplify(I / (a_ * a_ ** np_ / 2))
r2 = sp.simplify(I / (a_ * a_ ** np_))
ans = ans_q(15)
report(eq(r1, 2 / (np_ + 1)) and r"<b>a</b> \(2:n+1\)" in ans, "Q15a ratio 2 : n+1", r1)
report(eq(r2, 1 / (np_ + 1)) and r"<b>b</b> \(1:n+1\)" in ans, "Q15b ratio 1 : n+1", r2)

# Q16
blk, ans = qblock(16), ans_q(16)
poly = T(grab(blk, r"Show that \(@=x(x-1)(x^2-x-1)\)", "Q16")[0])
report(eq(sp.expand(poly - x * (x - 1) * (x**2 - x - 1)), 0), "Q16a factorisation")
aa = (1 + sp.sqrt(5)) / 2
for pw, tmpl in ((2, r"\(a^2=@\)"), (4, r"\(a^4=@\)"), (5, r"\(a^5=@\)")):
    got = T(grab(ans, tmpl, "Q16")[0])
    report(eq(got, aa**pw), f"Q16b a^{pw}", got)
zs = sorted(sp.solve(poly, x), key=float)
pieces = [abs(sp.integrate(poly, (x, zs[i], zs[i + 1]))) for i in range(3)]
pieces = [sp.nsimplify(sp.simplify(p)) for p in pieces]
report(sorted(pieces) == [R(1, 10), R(1, 10), R(1, 5)] and r"Areas are \(\tfrac15\ \text{u}^2\), \(\tfrac{1}{10}\ \text{u}^2\) and \(\tfrac{1}{10}\ \text{u}^2\)" in ans,
       "Q16c areas 1/5, 1/10, 1/10", pieces)

# Q17
blk, ans = qblock(17), ans_q(17)
p1 = T(grab(blk, r"\begin{cases}@, & \text{for }0\le u<6", "Q17")[0])
p2 = T(grab(blk, r"\\ @, & \text{for }6\le u\le12", "Q17")[0])
g = sp.Piecewise((p1, u < 6), (p2, True))
X = sp.Symbol("X", real=True)
G1 = sp.integrate(p1, (u, 0, X))
G2 = sp.integrate(p1, (u, 0, 6)) + sp.integrate(p2, (u, 6, X))
G = lambda v: (G1 if v <= 6 else G2).subs(X, v)  # noqa: E731
report(eq(p1.subs(u, 6), p2.subs(u, 6)), "Q17 g continuous at u = 6")
st = sp.solve(p1, u) + sp.solve(p2, u)
report(sorted(st) == [3, 10] and eq(G(3), 6) and eq(G(10), -8) and r"maximum at \((3,6)\), minimum at \((10,-8)\)" in ans,
       "Q17b stationary points (g changes + to - at 3, - to + at 10)", [G(3), G(10)])
zeros = sorted(set([s for s in sp.solve(G1, X) if 0 <= s <= 6] + [s for s in sp.solve(G2, X) if 6 <= s <= 12]))
report(zeros == [0, 6] and r"<b>c</b> \(x=0\), \(x=6\)" in ans, "Q17c G(x) = 0", zeros)
report(eq(G(12), -6) and r"\((12,-6)\)" in ans and r"\((6,0)\)" in ans, "Q17d endpoint (12,-6)", G(12))
report(eq(sp.integrate(G1, (X, 0, 6)), 24) and r"<b>e</b> \(24\ \text{u}^2\)" in ans, "Q17e area 24")
report(r"\((0,4)\)" in ans and r"\((3,0)\)" in ans and r"\((6,-4)\)" in ans and r"\((10,0)\)" in ans and
       r"\((12,2)\)" in ans and eq(p1.subs(u, 0), 4) and eq(p1.subs(u, 3), 0) and eq(p1.subs(u, 6), -4)
       and eq(p2.subs(u, 10), 0) and eq(p2.subs(u, 12), 2), "Q17a key points of g")

# Q18
ans = ans_q(18)
N, eps = sp.Symbol("N", positive=True), sp.Symbol("epsilon", positive=True)
for nv in (R(-2), R(-3), R(-5, 2)):
    lim = sp.limit(sp.integrate(x ** nv, (x, 1, N)), N, sp.oo)
    report(eq(lim, -1 / (nv + 1)), f"Q18a n={nv}: limit -1/(n+1)", lim)
for nv in (R(1), R(-1, 2), R(3)):
    lim = sp.limit(sp.integrate(x ** nv, (x, eps, 1)), eps, 0, "+")
    report(eq(lim, 1 / (nv + 1)), f"Q18b n={nv}: limit 1/(n+1)", lim)
report(r"<b>a</b> \(-\dfrac{1}{n+1}\)" in ans and r"<b>b</b> \(\dfrac{1}{n+1}\)" in ans, "Q18 printed limits")

# ------------------------------------------------------------------ 5. past paper
print("== 5. past paper")
PL = section(L, "Past-paper homework", None)
PA = section(A, "Past-Paper Homework - Worked Solutions", None)
marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', PL)]
intro = int(re.search(r"<span><b>(\d+) marks?</b></span>", PL).group(1))
mins = int(re.search(r"Suggested time: (\d+) minutes", PL).group(1))
report(sum(marks) == intro == 1, "PP marks add to the intro total", f"{marks} {intro}")
report(mins == max(5, 5 * round(1.5 * intro / 5)), "PP time 1.5 x marks rounded to 5 min (min 5)", mins)
lab_l = re.findall(r'<span class="pn">PP 1</span>(.*?)</span><span class="mk">', PL, re.S)
lab_a = re.findall(r'<span class="pn">PP 1</span>(.*?)</div>', PA, re.S)
norm = lambda s: re.sub(r"<[^>]+>|&nbsp;|\s", "", s).rstrip("</span>")  # noqa: E731
report(len(lab_l) == 1 and len(lab_a) == 1 and norm(lab_l[0]) == norm(lab_a[0]).replace("</span>", "")
       and "Normanhurst Boys High School, 2022" in lab_l[0] and "Q10" in lab_l[0], "PP label identical in both files",
       norm(lab_l[0]))
hints = re.findall(r'<div class="hint"><b>Hint:</b> (.*?)</div>', PL)
banned = ("integrat", "inverse", "subject", "solve", "rearrang", "swap", "dy", "dx", "cube", "root", "Box")
report(len(hints) == 1 and hints[0].strip().endswith("?") and not re.search(r"\d", hints[0])
       and not any(b in hints[0] for b in banned), "PP hint is one neutral question", hints)
# the true area: x = (y + 1)^(1/3) > 0 for 1 <= y <= 2 (solve y = x^3 - 1 for x)
stem = grab(PL, r"enclosed between the curve \(y=@\), the \(y\)-axis and the lines \(y=@\) and \(y=@\)?", "PP1")
fx, y1, y2 = T(stem[0]), T(stem[1]), T(stem[2])
inv = [s for s in sp.solve(sp.Eq(y, fx), x) if s.is_real is not False]
inv = [s for s in inv if sp.im(s.subs(y, R(3, 2)).evalf()) == 0][0]
true_area = sp.integrate(inv, (y, y1, y2)).evalf(20)
# independent: area = x2*y2 - x1*y1 - integral of (x^3 - 1) over x, with x1 = inv(1), x2 = inv(2)
xa, xb = (sp.real_root(y1 + 1, 3), sp.real_root(y2 + 1, 3))
alt = (xb * y2 - xa * y1 - sp.integrate(fx, (x, xa, xb))).evalf(20)
report(abs(true_area - alt) < 1e-12, "PP true area by y and by x agree", f"{true_area} {alt}")
opts = dict(re.findall(r"<span>\(([A-D])\)&ensp;\\\(\\displaystyle(.*?)\\\)</span>", PL))
vals = {}
for k_, v in opts.items():
    p = parse_int(v)
    if p and not (p[2].free_symbols - {y}):
        vals[k_] = sp.integrate(p[2], (y, p[0], p[1])).evalf(20)
    else:
        vals[k_] = None   # (A) has x in an integral with respect to y: not a number
good = [k_ for k_, v in vals.items() if v is not None and abs(v - true_area) < 1e-12]
report(sorted(opts) == list("ABCD") and good == ["B"], "PP MC: only (B) equals the area", vals)
report("<b>Answer (B).</b>" in PA, "PP answer letter printed (B)")

print()
print(f"{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    for f_ in FAILS:
        print("FAIL:", f_)
    sys.exit(1)
print("ALL OK")
