r"""Check of Lesson T1 (Year 10 Trigonometry part 2): Angles of any size, tied to the printed HTML.

Reads workspace/build/y10trig/lt1.html (questions) and a_t1.html (answers), plus the label text of the
homework figures in svg/.
  - Every checked question carries data-q="KEY" in lt1.html; its TeX (sin/cos/tan of an angle, an angle,
    a gradient, a pair of points) is READ from the page and the answer is computed independently with
    sympy (exact values: sympy.sin(pi*deg/180) etc.) or math (decimals, angles, gradients).
  - Every final answer in a_t1.html carries data-v="KEY". Each key must occur exactly once in its file,
    or the item FAILS. The printed answer is parsed (exact surds and fractions via a small TeX converter,
    signs, quadrants, angle lists, words) and compared with the computation.
  - Book / sheet answers: the Year 11 Advanced answers (PDF 547 for 5D/5E, 550 for 6B) and the Maths
    Pathway answer pages, transcribed in BOOK below, are compared with the printed answers as well.
  - Lesson examples (tutor demos, your turns, Worked example 10, Example 6) and the past-paper solutions
    are recomputed from the numbers in their printed questions.
Exit status 1 if anything fails.  Run: python3 workspace/checks/y10trig_t1.py
"""
import math
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y10TRIG_SRC", os.path.join(HERE, "..", "build", "y10trig"))
FAILS, NOK = [], [0]


def ok(flag, label, detail=""):
    if flag:
        NOK[0] += 1
        print("OK       " + label + ("  " + detail if detail else ""))
    else:
        FAILS.append(label)
        print("MISMATCH " + label + ("  " + detail if detail else ""))
    return flag


LES = open(os.path.join(SRC, "lt1.html"), encoding="utf-8").read()
ANS = open(os.path.join(SRC, "a_t1.html"), encoding="utf-8").read()


def _inner(html, attr, key):
    """Inner HTML of the element carrying attr="key" (must be unique)."""
    pat = re.compile(r'<(span|td)([^>]*)\s%s="%s"([^>]*)>' % (attr, re.escape(key)))
    ms = list(pat.finditer(html))
    if len(ms) != 1:
        return None, len(ms)
    m = ms[0]
    tag, i, depth = m.group(1), m.end(), 1
    while depth:
        o = html.find("<" + tag, i)
        c = html.find("</" + tag + ">", i)
        if o != -1 and o < c:
            depth += 1
            i = o + 1
        else:
            depth -= 1
            i = c + len(tag) + 3
    return html[m.end():i - len(tag) - 3], 1


def q(key):
    s, n = _inner(LES, "data-q", key)
    if s is None:
        ok(False, f"question {key}", f"data-q found {n} times")
        return None
    s = re.sub(r'<span class="pl">.*?</span>', "", s)
    m = re.search(r"\\\((.*)\\\)", s, re.S)
    return (m.group(1) if m else s).strip()


def v(key):
    s, n = _inner(ANS, "data-v", key)
    if s is None:
        ok(False, f"answer {key}", f"data-v found {n} times")
        return None
    s = s.replace("−", "-").replace("&lt;", "<").replace("&gt;", ">").strip()
    m = re.fullmatch(r"\\\((.*)\\\)", s, re.S)
    return m.group(1).strip() if m else s


# ------------------------------------------------------------------ parsing
def tex2sym(t):
    t = t.replace(" ", "").replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    sign = 1
    if t.startswith("-"):
        sign, t = -1, t[1:]
    if t == "undefined":
        return None

    def atom(s):
        s = s.strip("{}")
        if s.startswith("\\sqrt"):
            r = s[5:].strip("{}")
            return sp.sqrt(sp.Integer(r))
        return sp.Rational(s)

    m = re.fullmatch(r"\\frac(\{[^{}]*(?:\{[^{}]*\})?[^{}]*\}|\d)(\{[^{}]*(?:\{[^{}]*\})?[^{}]*\}|\d)", t)
    if m:
        return sign * atom(m.group(1)) / atom(m.group(2))
    return sign * atom(t)


def ans_sym(key):
    s = v(key)
    if s is None:
        return "MISSING"
    if s == "undefined":
        return None
    return tex2sym(s)


def angle_of(t):
    t = t.replace(" ", "").replace("−", "-")
    m = re.fullmatch(r"\(?(-?\d+)(\\tfrac12)?\^\\circ\)?", t)
    if not m:
        raise ValueError(f"angle? {t!r}")
    return int(m.group(1)) + (0.5 if m.group(2) else 0)


def fn_of(t):
    m = re.fullmatch(r"\\(sin|cos|tan)\s*\(?(-?\d+)\^\\circ\)?", t.replace(" ", ""))
    if not m:
        raise ValueError(f"function? {t!r}")
    return m.group(1), int(m.group(2))


def exact(fn, deg):
    a = sp.pi * sp.Integer(deg) / 180
    if fn == "tan" and sp.cos(a) == 0:
        return None
    return sp.nsimplify(sp.simplify({"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}[fn](a)))


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) < 1e-12


def fnum(fn, deg):
    return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[fn](math.radians(deg))


def quad(deg):
    d = deg % 360
    return 1 + int(d // 90) if d % 90 else None


def related(deg):
    d = deg % 360
    return min(d % 180, 180 - d % 180)


def angles_in(s):
    return [int(x) for x in re.findall(r"-?\d+", s.replace("−", "-"))]


ORD = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4}

BOOK = {  # Year 11 Advanced answers (PDF 547, 550) and Maths Pathway answer pages, transcribed
    "e1": [270, 330, 15, 165, 70, (0, 360)], "e2": [4, 1, 2, 4, 3, 4, 3, 1], "e3": "+++--+--",
    "e5": "++--+--+-+---++-", "e6": [10, 30, 50, 20, 80, 70, 70, 80, 10, 20],
    "e7": ["-\\tan50", "\\cos50", "-\\sin40", "\\tan80", "-\\cos10", "-\\sin40", "-\\cos5", "\\sin55", "-\\tan35",
           "\\sin85", "-\\cos85", "\\tan25"],
    "e8": ["0", "-1", "0", "0", "1", "1", "-1", "undefined", "0", "0", "undefined", "0"],
    "e9": ["\\frac{\\sqrt3}{2}", "\\frac{\\sqrt3}{2}", "-\\frac{\\sqrt3}{2}", "-\\frac{\\sqrt3}{2}", "\\frac{1}{\\sqrt2}",
           "-\\frac{1}{\\sqrt2}", "-\\frac{1}{\\sqrt2}", "\\frac{1}{\\sqrt2}", "\\frac{1}{\\sqrt3}", "-\\frac{1}{\\sqrt3}",
           "\\frac{1}{\\sqrt3}", "-\\frac{1}{\\sqrt3}"],
    "e10": [0.27, -1.00, 0.41, 3.08], "e11": [45, 120, 76, 30],
    "e4": [[70, 430, -290, -650], [100, 460, -260, -620], [140, 500, -220, -580], [200, 560, -160, -520],
            [240, 600, -120, -480], [340, 700, -20, -380]],
    "m13": [("4/5", "3/5", "4/3"), ("3/5", "-4/5", "-3/4"), ("-2/sqrt(5)", "-1/sqrt(5)", "2"), ("-5/13", "12/13", "-5/12")],
    "m14": ["-1/2", "1", "-1/2", "1/sqrt(2)", "sqrt(3)", "-sqrt(3)/2", "-1", "1/2", "-1/sqrt(2)", "-sqrt(3)/2", "-1/2", "-sqrt(3)"],
    "m15": [60, 20, 30, 60, 70, 10, 50, 40],
    "m16": ["1/2", "-sqrt(3)/2", "sqrt(3)", "1/sqrt(2)", "-1/sqrt(3)", "-1/sqrt(2)", "sqrt(3)", "-sqrt(3)/2", "1/sqrt(2)",
            "-1/2", "-1/2", "1"],
    "m17": [0.26, -0.97, -1, -0.5, -0.97, 1.73, -0.87, 0.87],
    "m18": [(390, 510), (-30, -150), (455, 625), (530, 550)],
    "e12": ["less", "equal", "less", "more"],
    "m20": [((-2, 0), (0, 6), "3", 72), ((2, 0), (0, 1), "-1/2", 153), ((-4, 0), (0, -3), "-3/4", 143), ((3, 0), (0, -2), "2/3", 34)],
    "h23a": [0.5, -0.5, 0.95, 0.95, 0.59, 0.81, -0.89, 0.45, -0.81, 0.59],
    "h23b": [(30, 150), (120, 240), (64, 116), (53, 307), (53, 127), (143, 217), (204, 336), (107, 253)],
    "h24": [0.42, -0.91, 0.91, -0.42, 0.49, 0.49], "h26": ["-\\sin", "\\cos", "-\\tan", "\\sin", "-\\sin", "-\\cos", "\\tan"],
    "h27": [3.73, 1, 2.41, 0.32],
}
L = "abcdefghijklmnop"

# ------------------------------------------------------------------ exact-value families
for fam, n in (("d5", 3), ("y5", 3), ("e8", 12), ("e9", 12), ("m14", 12), ("m16", 12)):
    for i in range(n):
        key = fam + L[i]
        qt = q(key)
        if qt is None:
            continue
        fn, deg = fn_of(qt)
        want = exact(fn, deg)
        got = ans_sym(key)
        if got == "MISSING":
            continue
        ok(same(got, want), f"{key} {fn} {deg}", f"printed {v(key)!r}, exact {want}")
        if fam in BOOK:
            b = BOOK[fam][i]
            bv = None if b == "undefined" else (tex2sym(b) if "\\" in b or b.lstrip("-").isdigit() else sp.sympify(b))
            ok(same(got, bv), f"{key} book answer", f"book {b}")

# ------------------------------------------------------------------ signs, quadrants, related angles, equivalents
for i in range(8):
    key = "e3" + L[i]
    fn, deg = fn_of(q(key))
    want = "Positive" if fnum(fn, deg) > 0 else "Negative"
    ok(v(key) == want, f"{key} sign of {fn} {deg}", f"printed {v(key)}")
    ok((v(key)[0] == "P") == (BOOK["e3"][i] == "+"), f"{key} sheet answer")
for i in range(16):
    key = "e5" + L[i]
    fn, deg = fn_of(q(key))
    want = "+" if fnum(fn, deg) > 0 else "-"
    ok(v(key) == want, f"{key} sign of {fn} {deg}", f"printed {v(key)}")
    ok(v(key) == BOOK["e5"][i], f"{key} book answer")
for fam, n in (("e6", 10), ("m15", 8)):
    for i in range(n):
        key = fam + L[i]
        deg = angle_of(q(key))
        got = angles_in(v(key))
        ok(got == [related(deg)], f"{key} related angle of {deg}", f"printed {v(key)}")
        ok(got == [BOOK[fam][i]], f"{key} book answer")
for i in range(8):
    key = "e2" + L[i]
    deg = angle_of(q(key))
    got = ORD.get(v(key).split()[0])
    ok(got == quad(deg) and v(key).endswith("quadrant"), f"{key} quadrant of {deg}", f"printed {v(key)}")
    ok(got == BOOK["e2"][i], f"{key} sheet answer")
for i in range(6):
    key = "e1" + L[i]
    deg = angle_of(q(key))
    got = angles_in(v(key))
    want = [deg % 360] if deg % 360 else [0, 360]
    ok(got == want, f"{key} equivalent of {deg}", f"printed {v(key)}")
    b = BOOK["e1"][i]
    ok(got == (list(b) if isinstance(b, tuple) else [b]), f"{key} sheet answer")

# 5E Q3: ratio of an acute angle with a sign
for i in range(12):
    key = "e7" + L[i]
    fn, deg = fn_of(q(key))
    a = v(key)
    m = re.fullmatch(r"(-?)\\(sin|cos|tan)(\d+)\^\\circ", a.replace(" ", ""))
    if not ok(bool(m), f"{key} form", a):
        continue
    val = (-1 if m.group(1) else 1) * fnum(m.group(2), int(m.group(3)))
    ok(0 < int(m.group(3)) < 90 and abs(val - fnum(fn, deg)) < 1e-9, f"{key} {fn} {deg} = {a}")
    ok(a.replace("^\\circ", "") == BOOK["e7"][i], f"{key} book answer")

# 6B Q6 and Q7
for i in range(4):
    key = "e10" + L[i]
    deg = angle_of(q(key))
    got = float(v(key))
    ok(abs(got - round(math.tan(math.radians(deg)), 2)) < 1e-9 and re.fullmatch(r"-?\d+\.\d\d", v(key)),
       f"{key} tan {deg}", f"printed {v(key)}")
    ok(got == BOOK["e10"][i], f"{key} book answer")
for i in range(4):
    key = "e11" + L[i]
    m = tex2sym(q(key))
    alpha = math.degrees(math.atan(float(m)))
    alpha = alpha + 180 if alpha < 0 else alpha
    got = angles_in(v(key))
    ok(got == [round(alpha)], f"{key} inclination for gradient {m}", f"printed {v(key)}, computed {alpha:.2f}")
    ok(got == [BOOK["e11"][i]], f"{key} book answer")

# ------------------------------------------------------------------ Medium
# 5D Q5: ray angles from the figure's labels (20 deg right of y-axis, ...)
labs = re.findall(r">([^<>]+)</text>", open(os.path.join(SRC, "svg", "hw_5d5.svg"), encoding="utf-8").read())
ok(sorted(labs) == sorted(["a", "b", "c", "d", "e", "f", "20°", "10°", "40°", "20°", "30°", "20°"]), "5D Q5 figure labels", str(labs))
rays = [90 - 20, 90 + 10, 180 - 40, 180 + 20, 270 - 30, 360 - 20]
for i, r in enumerate(rays):
    key = "e4" + L[i]
    got = angles_in(v(key))
    pos = [g for g in got if 0 < g < 720]
    neg = [g for g in got if -720 < g < 0]
    ok(len(got) == 4 and len(pos) == 2 and len(neg) == 2 and all((g - r) % 360 == 0 for g in got) and len(set(got)) == 4,
       f"{key} ray {r}", f"printed {got}")
    ok(got == BOOK["e4"][i], f"{key} book answer")
# 5D Q6: points and radii from the figures
for i, (name, part) in enumerate((("hw_5d6a", "a"), ("hw_5d6b", "b"), ("hw_5d6c", "c"), ("hw_5d6d", "d"))):
    labs = re.findall(r">([^<>]+)</text>", open(os.path.join(SRC, "svg", name + ".svg"), encoding="utf-8").read())
    pt = [l for l in labs if l.startswith("(")][0].replace("−", "-")
    x, y = (int(t) for t in re.findall(r"-?\d+", pt))
    rl = [l for l in labs if l not in (pt.replace("-", "−"), "θ") and not l.startswith("(")][0]
    r = sp.sqrt(x * x + y * y)
    ok(r == (sp.sqrt(5) if rl == "√5" else sp.Integer(rl)), f"m13{part} radius label {rl} = sqrt(x^2+y^2)")
    for k, want in (("s", sp.Integer(y) / r), ("c", sp.Integer(x) / r), ("t", sp.Rational(y, x))):
        got = ans_sym(f"m13{part}{k}")
        ok(same(got, want), f"m13{part}{k}", f"printed {v('m13' + part + k)}, computed {want}")
        ok(same(got, sp.sympify(BOOK["m13"][i]["sct".index(k)])), f"m13{part}{k} book answer")
# Maths Pathway Symmetry Q9 (table values, two decimal places)
for i in range(8):
    key = "m17" + L[i]
    fn, deg = fn_of(q(key))
    got = float(v(key))
    ok(abs(got - fnum(fn, deg)) < 0.011, f"{key} {fn} {deg}", f"printed {got}, true {fnum(fn, deg):.4f}")
    ok(got == BOOK["m17"][i], f"{key} sheet answer")
# Maths Pathway Graphs Q5 (brute force over whole degrees)
spec = [("sin", 30, 360, 540), ("sin", 330, -180, 180), ("cos", 95, 450, 630), ("cos", 170, 360, 720)]
for i, (fn, ref, lo, hi) in enumerate(spec):
    key = "m18" + L[i]
    want = sorted(x for x in range(lo + 1, hi) if abs(fnum(fn, x) - fnum(fn, ref)) < 1e-9)
    got = angles_in(v(key))
    ok(sorted(got) == want, f"{key} {fn} = {fn} {ref} in ({lo}, {hi})", f"printed {got}, computed {want}")
    ok(tuple(got) == BOOK["m18"][i], f"{key} sheet answer")
for t, vals in (("pathway question text", None),):
    for txt in ("between 360° and 540° have the same sine value as 30°", "between −180° and 180° have the same sine value as 330°",
                "between 450° and 630° have the same cosine value as 95°", "between 360° and 720° have the same cosine value as 170°"):
        ok(LES.count(txt) == 1, f"m18 question text '{txt}'")
# Maths Pathway Graphs Q9(a) table
for j, deg in enumerate((-180, -90, 0, 90, 180)):
    for fn, c in (("sin", "s"), ("cos", "c"), ("tan", "t")):
        key = f"m19{c}{j + 1}"
        got = ans_sym(key)
        ok(same(got, exact(fn, deg)), f"{key} {fn} {deg}", f"printed {v(key)}")
# 6B Q8
for i in range(4):
    key = "e12" + L[i]
    xs = [int(t) for t in re.findall(r"-?\d+", q(key).replace("−", "-"))]
    x1, y1, x2, y2 = xs
    m = sp.Rational(y2 - y1, x2 - x1)
    want = "less" if m < 1 else ("equal" if m == 1 else "more")
    ok(v(key) == want == BOOK["e12"][i], f"{key} gradient {m}", f"printed {v(key)}")
# 6B Q17: lines (a, b, c) with ax + by = c, checked against the printed question
LINES = {"a": ("y=3x+6", (-3, 1, 6)), "b": ("y=-\\tfrac12x+1", (sp.Rational(1, 2), 1, 1)),
         "c": ("3x+4y+12=0", (3, 4, -12)), "d": ("\\dfrac x3-\\dfrac y2=1", (sp.Rational(1, 3), sp.Rational(-1, 2), 1))}
for i, p in enumerate("abcd"):
    key = "m20" + p
    txt, (A, B, C) = LINES[p]
    ok(q(key).replace(" ", "") == txt.replace(" ", ""), f"{key} question", q(key))
    xA, yB = sp.Rational(C) / A, sp.Rational(C) / B
    m = -sp.Rational(A) / B
    alpha = math.degrees(math.atan(float(m)))
    alpha = alpha + 180 if alpha < 0 else alpha
    gA, gB = angles_in(v(key + "A")), angles_in(v(key + "B"))
    ok(gA == [xA, 0] and gB == [0, yB], f"{key} intercepts", f"printed {v(key + 'A')}, {v(key + 'B')}")
    ok(same(ans_sym(key + "m"), m), f"{key} gradient", f"printed {v(key + 'm')}, computed {m}")
    ok(angles_in(v(key + "al")) == [round(alpha)], f"{key} inclination", f"computed {alpha:.2f}")
    b = BOOK["m20"][i]
    ok(tuple(gA) == b[0] and tuple(gB) == b[1] and same(ans_sym(key + "m"), sp.sympify(b[2]))
       and angles_in(v(key + "al")) == [b[3]], f"{key} book answer")

# ------------------------------------------------------------------ Hard
for i, r in enumerate(("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x")):
    key = "h23a" + r
    fn, deg = fn_of(q(key))
    got = float(v(key))
    ok(abs(got - fnum(fn, deg)) < 0.011, f"{key} {fn} {deg}", f"printed {got}, true {fnum(fn, deg):.4f}")
    ok(got == BOOK["h23a"][i], f"{key} book answer")
for i, r in enumerate(("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")):
    key = "h23b" + r
    m = re.fullmatch(r"\\(sin|cos)x=(-?[\d.]+)", q(key).replace(" ", ""))
    fn, k = m.group(1), float(m.group(2))
    base = math.degrees(math.asin(k) if fn == "sin" else math.acos(k))
    sols = sorted(((base if fn == "cos" else base) % 360, ((180 - base) if fn == "sin" else (360 - base)) % 360))
    got = sorted(angles_in(v(key)))
    ok(len(got) == 2 and all(abs(g - s) <= 1.0 for g, s in zip(got, sols)), f"{key} {fn} x = {k}",
       f"printed {got}, true {[round(s, 2) for s in sols]}")
    ok(tuple(got) == BOOK["h23b"][i], f"{key} book answer")
ok(sorted(angles_in(v("h23c"))) == [45, 225] == sorted(x for x in range(0, 361) if abs(math.sin(math.radians(x)) - math.cos(math.radians(x))) < 1e-9),
   "h23c sin x = cos x")
s25, c25 = 0.42, 0.91
ok("\\sin25^\\circ\\doteqdot0.42" in LES and "\\cos25^\\circ\\doteqdot0.91" in LES, "h24 given values printed")
H24 = {"a": s25, "b": -c25, "c": c25, "d": -s25, "e": -s25 + c25, "f": c25 - s25}
for i, p in enumerate("abcdef"):
    key = "h24" + p
    qt = q(key).replace(" ", "")
    true = sum(sg * fnum(fn, int(d)) for sg, fn, d in
               [((-1 if t[0] == "-" else 1), t[1], t[2]) for t in re.findall(r"(^|[-+])\\(sin|cos)(\d+)\^\\circ", qt)])
    got = float(v(key))
    ok(abs(got - round(H24[p], 2)) < 1e-9 and abs(true - H24[p]) < 0.02, f"{key} {qt}", f"printed {got}, true {true:.4f}")
    ok(got == BOOK["h24"][i], f"{key} book answer")
# 5E Q14 (both sides, exact)
th = 150
ok(same(ans_sym("h25al"), exact("sin", 2 * th)) and same(ans_sym("h25ar"), 2 * exact("sin", th) * exact("cos", th)), "h25a both sides")
th = 225
ok(same(ans_sym("h25bl"), exact("cos", 3 * th)) and same(ans_sym("h25br"), 4 * exact("cos", th) ** 3 - 3 * exact("cos", th)), "h25b both sides")
A, B = 300, 240
ok(same(ans_sym("h25cl"), exact("sin", A + B)) and same(ans_sym("h25cr"), exact("sin", A) * exact("cos", B) + exact("cos", A) * exact("sin", B)), "h25c both sides")
ok("when \\(\\theta=150^\\circ\\)" in LES and "when \\(\\theta=225^\\circ\\)" in LES and "\\(A=300^\\circ\\) and \\(B=240^\\circ\\)" in LES, "h25 question values")
# 5E Q15: identities tested at several angles
for i, p in enumerate("abcefgh"):
    key = "h26" + p
    m = re.fullmatch(r"\\(sin|cos|tan)\((.*)\)", q(key).replace(" ", ""))
    fn, inner = m.group(1), m.group(2).replace("^\\circ", "").replace("\\theta", "t")
    a = re.fullmatch(r"(-?)\\(sin|cos|tan)\\theta", v(key).replace(" ", ""))
    good = bool(a)
    for t in (17.0, 63.0, 128.0, 251.0):
        lhs = fnum(fn, eval(inner, {"t": t}))
        rhs = (-1 if a.group(1) else 1) * fnum(a.group(2), t) if a else None
        good = good and abs(lhs - rhs) < 1e-9
    ok(good, f"{key} {q(key)} = {v(key)}")
    ok(a and (a.group(1) + "\\" + a.group(2)) == BOOK["h26"][i], f"{key} book answer")
for i, p in enumerate("abcd"):
    key = "h27" + p
    beta = angle_of(q(key))
    want = math.tan(math.radians(90 - beta))
    got = float(v(key))
    ok(abs(got - round(want, 2)) < 1e-9, f"{key} acute angle {beta} with the y-axis", f"printed {got}, true {want:.4f}")
    ok(got == BOOK["h27"][i], f"{key} book answer")

# ------------------------------------------------------------------ lesson examples
def chk_list(key, ref, npos=2, nneg=2):
    got = angles_in(v(key))
    ok(len(got) == npos + nneg and sum(g > 0 for g in got) == npos and all((g - ref) % 360 == 0 for g in got)
       and len(set(got)) == len(got), f"{key} same ray as {ref}", f"printed {got}")


ok("same ray as 50°" in LES and "same ray as 70°" in LES, "C1 questions 50° and 70°")
chk_list("d1a", 50)
chk_list("y1a", 70)
for key, deg in (("d1bi", -120), ("d1bii", 470), ("y1bi", -150), ("y1bii", 520)):
    ok(angles_in(v(key)) == [deg % 360], f"{key} {deg}", v(key))
ok("radius 13 at the point \\(P(-5,12)\\)" in LES and "radius 17 at the point \\(P(8,-15)\\)" in LES, "C2 questions")
for pre, (x, y, r) in (("d2", (-5, 12, 13)), ("y2", (8, -15, 17))):
    ok(x * x + y * y == r * r, f"{pre} OP = {r}")
    for k, want in (("s", sp.Rational(y, r)), ("c", sp.Rational(x, r)), ("t", sp.Rational(y, x))):
        ok(same(ans_sym(pre + k), want), f"{pre}{k}", f"printed {v(pre + k)}")
for pre, degs in (("d3", (450, -90)), ("y3", (540, -270))):
    for part, deg in zip("ab", degs):
        ok(f"\\(\\theta={deg}^\\circ\\)" in LES, f"{pre}{part} question {deg}")
        for fn, k in (("sin", "s"), ("cos", "c"), ("tan", "t")):
            ok(same(ans_sym(pre + part + k), exact(fn, deg)), f"{pre}{part}{k} {fn} {deg}", v(pre + part + k))
for pre, degs in (("d4", (115, 250, -60)), ("y4", (165, 320, 400))):
    for part, deg in zip("abc", degs):
        ok(f"\\(\\theta={deg}^\\circ\\)" in LES, f"{pre}{part} question {deg}")
        signs = re.findall(r"[+-]", v(pre + part))
        want = ["+" if fnum(fn, deg) > 0 else "-" for fn in ("sin", "cos", "tan")]
        ok(signs == want, f"{pre}{part} signs of {deg}", f"printed {signs}")
ok("\\sin35^\\circ\\doteqdot0.57" in LES and "\\cos35^\\circ\\doteqdot0.82" in LES and "\\tan35^\\circ\\doteqdot0.70" in LES, "C6 demo givens")
ok("\\sin55^\\circ\\doteqdot0.82" in LES and "\\cos55^\\circ\\doteqdot0.57" in LES and "\\tan55^\\circ\\doteqdot1.43" in LES, "C6 your-turn givens")
for ref, given in ((35, (0.57, 0.82, 0.70)), (55, (0.82, 0.57, 1.43))):
    for fn, g in zip(("sin", "cos", "tan"), given):
        ok(abs(fnum(fn, ref) - g) < 0.005 + 1e-9, f"C6 given {fn} {ref} = {g}")
for pre, ref, degs in (("d6", 35, (145, 325)), ("y6", 55, (125, 235))):
    for part, deg in zip("ab", degs):
        for fn, k, gi in (("sin", "s", 0), ("cos", "c", 1), ("tan", "t", 2)):
            got = float(v(pre + part + k))
            sign = 1 if fnum(fn, deg) > 0 else -1
            want = sign * {35: (0.57, 0.82, 0.70), 55: (0.82, 0.57, 1.43)}[ref][gi]
            ok(abs(got - want) < 1e-9 and abs(abs(fnum(fn, deg)) - abs(fnum(fn, ref))) < 1e-9, f"{pre}{part}{k} {fn} {deg}", f"printed {got}")
for key, fn in (("d7", "cos"), ("y7", "sin")):
    zeros = [x for x in range(0, 361) if abs(fnum(fn, x)) < 1e-9]
    ok(angles_in(v(key + "a")) == zeros, f"{key}a zeros of {fn}", v(key + "a"))
    neg = [x for x in range(0, 361) if fnum(fn, x) < -1e-9]
    ok(angles_in(v(key + "b")) == [neg[0] - 1, neg[-1] + 1] and "<" in v(key + "b"), f"{key}b {fn} negative", v(key + "b"))
    other = [x for x in range(0, 360) if x != 50 and abs(fnum(fn, x) - fnum(fn, 50)) < 1e-9]
    ok(angles_in(v(key + "c")) == other, f"{key}c same {fn} as 50", v(key + "c"))
for pre, A, Bp in (("d8", (-2, 4), (-4, 0)), ("y8", (-4, 3), (-8, 0))):
    ok(f"\\(A({A[0]},{A[1]})\\), \\(B({Bp[0]},{Bp[1]})\\)" in LES, f"{pre} question points")
    mAB = (0 - A[1]) / (Bp[0] - A[0])
    mAO = (0 - A[1]) / (0 - A[0])
    aAB = math.degrees(math.atan(mAB)) % 180
    aAO = math.degrees(math.atan(mAO)) % 180
    ok(angles_in(v(pre + "ab")) == [round(aAB)] and angles_in(v(pre + "ao")) == [round(aAO)], f"{pre} inclinations",
       f"computed {aAB:.2f}, {aAO:.2f}")
    iso = abs((180 - aAO) - aAB) < 1e-9 and abs(math.hypot(A[0] - Bp[0], A[1]) - math.hypot(*A)) < 1e-9
    ok(iso and v(pre + "b") == "isosceles", f"{pre}b isosceles")
# Worked example 10 and Example 6 printed values
for key, fn, deg, tex in (("w10a", "tan", 300, "-\\sqrt3."), ("w10b", "sin", -210, "\\tfrac12."), ("w10c", "cos", 570, "-\\frac{\\sqrt3}{2}.")):
    ok(fn_of(q(key)) == (fn, deg), f"{key} question")
    ok(LES.count(tex) >= 1 and same(tex2sym(tex.rstrip(".")), exact(fn, deg)), f"{key} printed value {tex}")
ok(round(math.degrees(math.atan(5 / 3))) == 59 and round(180 - math.degrees(math.atan(5 / 3))) == 121, "Example 6: 59 and 121 degrees")

# ------------------------------------------------------------------ past papers
# MC items: the data are read from the printed figure and the options from the printed question
def svg_labels(name):
    return re.findall(r">([^<>]+)</text>", open(os.path.join(SRC, "svg", name + ".svg"), encoding="utf-8").read())


def mc_options(after):
    seg = LES.split(after, 1)[1].split('<div class="hint">', 1)[0]
    return {k: int(d) for k, d in re.findall(r"\(?([A-D])[).]&ensp;(\d+)°", seg)}


pm = [re.fullmatch(r"P\((-?\d+), (-?\d+)\)", t.replace("−", "-")) for t in svg_labels("pp_nbcs22_13")]
px, py = [(int(m.group(1)), int(m.group(2))) for m in pm if m][0]
ok("\\(P\\) has coordinates \\((%d,%d)\\)" % (px, py) in LES, "m21 printed P matches the figure", f"P({px}, {py})")
opts = mc_options("Section I Q13 (1 mark)")
want = round(math.degrees(math.atan2(py, px)))
ok(len(opts) == 4 and [k for k, d in opts.items() if d == want] == [v("m21")], "m21 NBCS Q13: answer letter", f"options {opts}, angle {want}")
ok(angles_in(v("m22")) == [x for x in range(0, 361) if abs(math.cos(math.radians(x))) < 1e-9], "m22 cos = 0")
ok(v("h28") == "B" and "B.&ensp;\\(y=\\sin(-x)^\\circ\\)" in LES
   and all(abs(math.sin(math.radians(-x)) + math.sin(math.radians(x))) < 1e-12 for x in range(-180, 361, 15)), "h28 SBHS Q8: B")
quads = [k for k in (1, 2, 3, 4) if fnum("sin", 90 * k - 45) > 0 and fnum("cos", 90 * k - 45) < 0]
ok(v("pp1") == "B" and quads == [2] and "B.&ensp;Quadrant 2" in LES, "pp1 quadrant 2 = B")
obt = [x for x in range(91, 180) if abs(fnum("tan", x) + fnum("tan", 50)) < 1e-9]
ok(v("pp2") == "A" and obt == [130] and "(A)&ensp;\\(\\theta=130^\\circ\\)" in LES, "pp2 130 = A")


def stmt_true(p, q_, quad_):
    sg = {"sin": [1, 1, -1, -1], "cos": [1, -1, -1, 1], "tan": [1, -1, 1, -1]}
    ok_quads = [k for k in range(4) if sg[p[0]][k] == p[1] and sg[q_[0]][k] == q_[1]]
    return ok_quads == [quad_ - 1]


S = {"A": (("cos", 1), ("sin", -1), 4), "B": (("cos", 1), ("tan", 1), 3), "C": (("tan", -1), ("cos", -1), 2), "D": (("sin", 1), ("tan", 1), 1)}
wrong = [k for k, (p, q_, qq) in S.items() if not stmt_true(p, q_, qq)]
ok(v("pp3") == "B" and wrong == ["B"], "pp3 incorrect statement B")
labs = svg_labels("pp_gir23_3")
ints = [int(t.replace("−", "-")) for t in labs if re.fullmatch(r"−?\d+", t)]
xi = [n for n in ints if n > 0][0]
yi = [n for n in ints if n < 0][0]
grad = (0 - yi) / (xi - 0)                     # line through (xi, 0) and (0, yi)
want = round(math.degrees(math.atan(grad)))
opts = mc_options("Multiple <span")
ok(len(opts) == 4 and [k for k, d in opts.items() if d == want] == [v("pp4")], "pp4 Girraween Q3: answer letter", f"intercepts {xi}, {yi}; options {opts}; angle {want}")
acute = [x for x in range(1, 90) if abs(fnum("cos", x) - fnum("cos", 286)) < 1e-9]
ok(angles_in(v("pp5")) == acute == [74] and "\\cos\\theta=\\cos286^\\circ" in LES, "pp5 74")
m6 = re.search(r"y=(\d+)x-\d+", q("pp6") or "")
if ok(bool(m6), "pp6 question line read"):
    a6 = math.degrees(math.atan(int(m6.group(1))))
    d6, mi6 = int(a6), round((a6 - int(a6)) * 60)
    got6 = re.fullmatch(r"(\d+)\^\\circ(\d+)'", v("pp6"))
    ok(got6 is not None and (int(got6.group(1)), int(got6.group(2))) == (d6, mi6) == (75, 58), "pp6 inclination to the nearest minute (school 75°58′)", f"computed {d6}°{mi6}′, printed {v('pp6')}")
ok(angles_in(v("pp7")) == [related(480)] and "represent 480°" in LES, "pp7 related angle of 480")
PP8 = LES.split('<span class="pn">PP 8</span>', 1)[1].split('<div class="hint">', 1)[0]
m8 = re.search(r"the point \\\(P\((-?\d+),(-?\d+)\)\\\)", PP8)
r8 = re.search(r"Given \\\(OP=(\d+)\\\) units", PP8)
if ok(bool(m8 and r8), "pp8 P and OP read from the question"):
    x8, y8, r8v = int(m8.group(1)), int(m8.group(2)), int(r8.group(1))
    ok(x8 * x8 + y8 * y8 == r8v * r8v, "pp8 OP consistent with P")
    ok(same(ans_sym("pp8s"), sp.Rational(y8, r8v)) and same(ans_sym("pp8t"), sp.Rational(y8, x8)), "pp8 sin and tan", f"P({x8},{y8}), r={r8v}")
val = (exact("sin", 150) + exact("cos", 300)) / (exact("tan", 750) - exact("tan", 120))
ok(same(ans_sym("pp10"), sp.simplify(val)) and "\\dfrac{\\sin150^\\circ+\\cos300^\\circ}{\\tan750^\\circ-\\tan120^\\circ}" in LES, "pp10", str(sp.simplify(val)))
ok(same(ans_sym("pp11a"), exact("cos", 45)) and same(ans_sym("pp11b"), exact("sin", 240)) and same(ans_sym("pp11c"), exact("tan", 420) ** 2), "pp11")
marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', LES.split("Past-paper homework:mini exam")[1])]
ok(sum(marks) == 17 and "<b>17 marks</b>" in LES and "Suggested time: 25 minutes" in LES and 5 * round(1.5 * 17 / 5) == 25,
   "mini exam 17 marks, 25 minutes", str(marks))

print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
