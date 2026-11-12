r"""Check of Lesson T2 (Year 10 Trigonometry part 2): Exact values and trigonometric equations, tied to the HTML.

Reads workspace/build/y10trig/lt2.html (questions) and a_t2.html (answers).
  - Equations: every equation item carries data-q="KEY" in lt2.html. Its printed TeX is compared with the
    transcription in EQ below (equation and domain), and the equation itself is given there as a Python
    function f(x) = 0 with its domain. The FULL solution set is then found by brute force: a scan of the
    domain in steps of 0.001 degrees (sign changes refined by bisection, plus exact zeros and touching
    points found on a whole-degree / half-degree grid). The printed answer (data-v="KEY", each key exactly
    once) is parsed (degrees, degrees and minutes, decimals) and must match the whole set, at the
    rounding the question asks for. Book / sheet / school answers (transcribed in BOOK) are compared too.
  - Exact values and given-one-find-another: the printed values are parsed (surds and fractions) and
    compared with sympy's exact values, computed from the data typed in VAL (each also tied to the
    printed question text).
Exit status 1 if anything fails.  Run: python3 workspace/checks/y10trig_t2.py
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


LES = open(os.path.join(SRC, "lt2.html"), encoding="utf-8").read()
ANS = open(os.path.join(SRC, "a_t2.html"), encoding="utf-8").read()


def _inner(html, attr, key):
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
        return ""
    s = re.sub(r'<span class="pl">.*?</span>', "", s)
    return re.sub(r"\s+", "", s.replace("&amp;", "&"))


def v(key):
    s, n = _inner(ANS, "data-v", key)
    if s is None:
        ok(False, f"answer {key}", f"data-v found {n} times")
        return None
    return s.replace("−", "-").strip()


# ------------------------------------------------------------------ brute-force solution sets
S, C, T = (lambda d: math.sin(math.radians(d))), (lambda d: math.cos(math.radians(d))), (lambda d: math.tan(math.radians(d)))


def solve(f, lo, hi, closed=True, step=0.001):
    """All x in [lo, hi] (or (lo, hi)) with f(x) = 0, by scanning."""
    out = []
    # exact zeros and touching points on a fine rational grid (multiples of 0.5 degree)
    k = math.ceil(lo * 2)
    while k / 2 <= hi + 1e-12:
        x = k / 2
        try:
            if abs(f(x)) < 1e-9:
                out.append(x)
        except (ValueError, ZeroDivisionError):
            pass
        k += 1
    n = int(round((hi - lo) / step))
    prev = None
    for i in range(n + 1):
        x = lo + i * step
        try:
            fx = f(x)
        except (ValueError, ZeroDivisionError):
            prev = None
            continue
        if prev is not None and prev[1] * fx < 0 and abs(prev[1] - fx) < 0.5:   # a crossing, not an asymptote
            a, b = prev[0], x
            for _ in range(80):
                m = (a + b) / 2
                if f(a) * f(m) <= 0:
                    b = m
                else:
                    a = m
            out.append((a + b) / 2)
        prev = (x, fx)
    r = []
    for x in sorted(out):
        if not r or abs(x - r[-1]) > 1e-4:
            r.append(x)
    if not closed:
        r = [x for x in r if lo + 1e-9 < x < hi - 1e-9]
    return r


def parse_angles(s):
    """'x = 5°44′ or 174°16′' -> [5.7333, 174.2667]; also decimals and plain degrees."""
    s = s.replace("\\circ", "°").replace("^", "").replace("\\doteqdot", "").replace("\\", " ")
    s = s.replace("{", "").replace("}", "").replace("'", "′")
    vals = []
    for m in re.finditer(r"(-?\d+(?:\.\d+)?)\s*°?\s*(?:(\d+)′)?", s):
        d = float(m.group(1))
        if m.group(2):
            d = d + (1 if d >= 0 else -1) * int(m.group(2)) / 60
        vals.append(d)
    return vals


def round_to(x, mode):
    if mode == "deg":
        return round(x)
    if mode == "min":
        return round(x * 60) / 60
    if mode == "2dp":
        return round(x, 2)
    return x


# key: (printed question TeX after whitespace removal (substring), f, lo, hi, closed, rounding, book answer)
EQ = {
    "d4a": (r"\cosx=1\),for\(0^\circ\lex\le720^\circ", lambda x: C(x) - 1, 0, 720, True, "exact", None),
    "d4b": (r"\cosx=0\),for\(0^\circ\lex\le720^\circ", lambda x: C(x), 0, 720, True, "exact", None),
    "y4a": (r"\sinx=1\),for\(0^\circ\lex\le720^\circ", lambda x: S(x) - 1, 0, 720, True, "exact", None),
    "y4b": (r"\tanx=0\),for\(0^\circ\lex\le720^\circ", lambda x: T(x), 0, 720, True, "exact", None),
    "d5a": (r"\cosx=-\dfrac{\sqrt3}{2}\),for\(-180^\circ\lex\le180^\circ", lambda x: C(x) + math.sqrt(3) / 2, -180, 180, True, "exact", None),
    "d5b": (r"\sinx=0.6\),for\(0^\circ\lex\le360^\circ\),correcttothenearestdegree", lambda x: S(x) - 0.6, 0, 360, True, "deg", None),
    "y5a": (r"\tanx=-1\),for\(-180^\circ\lex\le180^\circ", lambda x: T(x) + 1, -180, 180, True, "exact", None),
    "y5b": (r"\cosx=-0.35\),for\(0^\circ\lex\le360^\circ\),correcttothenearestdegree", lambda x: C(x) + 0.35, 0, 360, True, "deg", None),
    "d6": (r"\sinx=2\cosx\),where\(0^\circ\lex\le360^\circ\),correcttothenearestdegree", lambda x: S(x) - 2 * C(x), 0, 360, True, "deg", None),
    "y6": (r"\sqrt3\sinx=\cosx\),where\(0^\circ\lex\le360^\circ", lambda x: math.sqrt(3) * S(x) - C(x), 0, 360, True, "exact", None),
    "d7a": (r"\cos2x=\tfrac12\),where\(0^\circ\lex\le360^\circ", lambda x: C(2 * x) - 0.5, 0, 360, True, "exact", None),
    "d7b": (r"\tan(x-60^\circ)=1\),where\(0^\circ\lex\le360^\circ", lambda x: T(x - 60) - 1, 0, 360, True, "exact", None),
    "y7a": (r"\sin2x=\dfrac{\sqrt3}{2}\),where\(0^\circ\lex\le360^\circ", lambda x: S(2 * x) - math.sqrt(3) / 2, 0, 360, True, "exact", None),
    "y7b": (r"\cos(x+45^\circ)=-\tfrac12\),where\(0^\circ\lex\le360^\circ", lambda x: C(x + 45) + 0.5, 0, 360, True, "exact", None),
    # Exercise 5H Q1, Q2, Q3 (book answers PDF 548)
    "e9a": (r"\sin\theta=\dfrac{\sqrt3}{2}", lambda x: S(x) - math.sqrt(3) / 2, 0, 360, True, "exact", [60, 120]),
    "e9c": (r"\tan\theta=1", lambda x: T(x) - 1, 0, 360, True, "exact", [45, 225]),
    "e9d": (r"\tan\theta=\sqrt3", lambda x: T(x) - math.sqrt(3), 0, 360, True, "exact", [60, 240]),
    "e9e": (r"\cos\theta=-\dfrac{1}{\sqrt2}", lambda x: C(x) + 1 / math.sqrt(2), 0, 360, True, "exact", [135, 225]),
    "e9f": (r"\tan\theta=-\sqrt3", lambda x: T(x) + math.sqrt(3), 0, 360, True, "exact", [120, 300]),
    "e9h": (r"\cos\theta=-\dfrac{\sqrt3}{2}", lambda x: C(x) + math.sqrt(3) / 2, 0, 360, True, "exact", [150, 210]),
    "e10a": (r"\sin\theta=1", lambda x: S(x) - 1, 0, 360, True, "exact", [90]),
    "e10b": (r"\cos\theta=1", lambda x: C(x) - 1, 0, 360, True, "exact", [0, 360]),
    "e10c": (r"\cos\theta=0", lambda x: C(x), 0, 360, True, "exact", [90, 270]),
    "e10d": (r"\cos\theta=-1", lambda x: C(x) + 1, 0, 360, True, "exact", [180]),
    "e10e": (r"\tan\theta=0", lambda x: T(x), 0, 360, True, "exact", [0, 180, 360]),
    "e10f": (r"\sin\theta=-1", lambda x: S(x) + 1, 0, 360, True, "exact", [270]),
    "e11a": (r"\cosx=\tfrac37", lambda x: C(x) - 3 / 7, 0, 360, True, "deg", [65, 295]),
    "e11b": (r"\sinx=0.1234", lambda x: S(x) - 0.1234, 0, 360, True, "deg", [7, 173]),
    "e11c": (r"\tanx=7", lambda x: T(x) - 7, 0, 360, True, "deg", [82, 262]),
    "e11d": (r"\sinx=-\tfrac23", lambda x: S(x) + 2 / 3, 0, 360, True, "deg", [222, 318]),
    "e11e": (r"\tanx=-\tfrac{20}{9}", lambda x: T(x) + 20 / 9, 0, 360, True, "deg", [114, 294]),
    "e11f": (r"\cosx=-0.77", lambda x: C(x) + 0.77, 0, 360, True, "deg", [140, 220]),
    # Maths Pathway Q8 (sheet answers p10): between 0 and 360
    "e12a": (r"4\sin(x)=3", lambda x: 4 * S(x) - 3, 0, 360, True, "2dp", [48.59, 131.41]),
    "e12b": (r"\tan(x)+5=60", lambda x: T(x) + 5 - 60, 0, 360, True, "2dp", [88.96, 268.96]),
    "e12c": (r"2\cos(x)=-1", lambda x: 2 * C(x) + 1, 0, 360, True, "2dp", [120, 240]),
    "e12d": (r"5\tan(x)+12=0", lambda x: 5 * T(x) + 12, 0, 360, True, "2dp", [112.62, 292.62]),
    # Exercise 5H Q4, Q5, Q6 (selected parts)
    "m17a": (r"\sin\alpha=0.1", lambda x: S(x) - 0.1, 0, 360, True, "min", [5 + 44 / 60, 174 + 16 / 60]),
    "m17b": (r"\cos\alpha=-0.1", lambda x: C(x) + 0.1, 0, 360, True, "min", [95 + 44 / 60, 264 + 16 / 60]),
    "m18a": (r"\tanx=-0.3", lambda x: T(x) + 0.3, -180, 180, True, "min", [-(16 + 42 / 60), 163 + 18 / 60]),
    "m18b": (r"\cosx=0", lambda x: C(x), -180, 180, True, "exact", [-90, 90]),
    "m18d": (r"\sinx=-0.7", lambda x: S(x) + 0.7, -180, 180, True, "min", [-(135 + 34 / 60), -(44 + 26 / 60)]),
    "m19a": (r"2\cos\theta-1=0", lambda x: 2 * C(x) - 1, 0, 720, True, "exact", [60, 300, 420, 660]),
    "m19d": (r"\tan\theta=\sqrt2-1", lambda x: T(x) - (math.sqrt(2) - 1), 0, 720, True, "min", [22.5, 202.5, 382.5, 562.5]),
    # Maths Pathway Q9: open ranges
    "m20a": (r"450^\circ\ltx\lt720^\circ\):&ensp;\(8\sin(x)=7", lambda x: 8 * S(x) - 7, 450, 720, False, "2dp", [478.96]),
    "m20b": (r"360^\circ\ltx\lt540^\circ\):&ensp;\(3\tan(x)+4=40", lambda x: 3 * T(x) + 4 - 40, 360, 540, False, "2dp", [445.24]),
    "m20c": (r"90^\circ\ltx\lt270^\circ\):&ensp;\(7\sin(x)=-4", lambda x: 7 * S(x) + 4, 90, 270, False, "2dp", [214.85]),
    "m20d": (r"-180^\circ\ltx\lt0^\circ\):&ensp;\(11\cos(x)=6", lambda x: 11 * C(x) - 6, -180, 0, False, "2dp", [-56.94]),
    # past papers in the bands (school answers)
    "m21": (r"\tan\theta=-\dfrac{1}{\sqrt3}\)for\(0\le\theta\le360^\circ", lambda x: T(x) + 1 / math.sqrt(3), 0, 360, True, "exact", [150, 330]),
    "m23": (r"\sinx=-\dfrac{\sqrt3}{2}\)for\(0^\circ\lex\le360^\circ", lambda x: S(x) + math.sqrt(3) / 2, 0, 360, True, "exact", [240, 300]),
    # Hard: 5H Q9, Q7, Q8 (book answers PDF 548) and past papers
    "h31a": (r"\sin\theta=\cos\theta", lambda x: S(x) - C(x), 0, 360, True, "exact", [45, 225]),
    "h31b": (r"\sin\theta+\cos\theta=0", lambda x: S(x) + C(x), 0, 360, True, "exact", [135, 315]),
    "h31c": (r"\sin\theta=\sqrt3\cos\theta", lambda x: S(x) - math.sqrt(3) * C(x), 0, 360, True, "exact", [60, 240]),
    "h31d": (r"\sqrt3\sin\theta+\cos\theta=0", lambda x: math.sqrt(3) * S(x) + C(x), 0, 360, True, "exact", [150, 330]),
    "h33a": (r"\sin2x=\tfrac12", lambda x: S(2 * x) - 0.5, 0, 360, True, "exact", [15, 75, 195, 255]),
    "h33c": (r"\cos2x=-\dfrac{1}{\sqrt2}", lambda x: C(2 * x) + 1 / math.sqrt(2), 0, 360, True, "min", [67.5, 112.5, 247.5, 292.5]),
    "h33d": (r"\sin2x=-1", lambda x: S(2 * x) + 1, 0, 360, True, "exact", [135, 315]),
    "h34a": (r"\tan(\alpha-45^\circ)=\dfrac{1}{\sqrt3}", lambda x: T(x - 45) - 1 / math.sqrt(3), 0, 360, True, "exact", [75, 255]),
    "h34b": (r"\sin(\alpha+30^\circ)=-\dfrac{\sqrt3}{2}", lambda x: S(x + 30) + math.sqrt(3) / 2, 0, 360, True, "exact", [210, 270]),
    "h34c": (r"\cos(\alpha+60^\circ)=1", lambda x: C(x + 60) - 1, 0, 360, True, "exact", [300]),
    "h34d": (r"\cos(\alpha-75^\circ)=-\dfrac{1}{\sqrt2}", lambda x: C(x - 75) + 1 / math.sqrt(2), 0, 360, True, "exact", [210, 300]),
    "h35": (r"\tan(\alpha-45^\circ)=-\dfrac{1}{\sqrt3}\)for\(0^\circ\le\alpha\le360^\circ", lambda x: T(x - 45) + 1 / math.sqrt(3), 0, 360, True, "exact", [15, 195]),
    # worked examples (printed in the lesson, checked against their printed lines)
    "w15a": (r"\sinx=-1\),for\(0^\circ\lex\le720^\circ", lambda x: S(x) + 1, 0, 720, True, "exact", [270, 630]),
    "w15b": (r"\sinx=0\),for\(0^\circ\lex\le720^\circ", lambda x: S(x), 0, 720, True, "exact", [0, 180, 360, 540, 720]),
    "w16": (r"\sinx=-\tfrac12\),for\(-180^\circ\lex\le180^\circ", lambda x: S(x) + 0.5, -180, 180, True, "exact", [-150, -30]),
    "w17": (r"\tanx=-3\),for\(0^\circ\lex\le360^\circ\),correcttothenearestdegree", lambda x: T(x) + 3, 0, 360, True, "deg", [108, 288]),
    "w19": (r"\tan2x=\sqrt3\),where\(0^\circ\lex\le360^\circ", lambda x: T(2 * x) - math.sqrt(3), 0, 360, True, "exact", [30, 120, 210, 300]),
    "w20": (r"\sin(x-250^\circ)=\dfrac{\sqrt3}{2}\),where\(0^\circ\lex\le360^\circ", lambda x: S(x - 250) - math.sqrt(3) / 2, 0, 360, True, "exact", [10, 310]),
    "w21": (r"\sinx+\sqrt3\cosx=0\),where\(0^\circ\lex\le360^\circ", lambda x: S(x) + math.sqrt(3) * C(x), 0, 360, True, "exact", [120, 300]),
}
WORKED_PRINTED = {"w15a": r"\(x=270^\circ\) or \(630^\circ\)", "w15b": r"\(x=0^\circ\), \(180^\circ\), \(360^\circ\), \(540^\circ\) or \(720^\circ\)",
                  "w16": r"\(x=-150^\circ\) or \(-30^\circ\)", "w17": r"\(x\doteqdot108^\circ\) or \(288^\circ\)",
                  "w19": r'\(x=30^\circ,\ 120^\circ,\ 210^\circ\) or <span style="white-space:nowrap">\(300^\circ\)', "w20": r"\(x=10^\circ\) or \(310^\circ\)",
                  "w21": r"\(x=120^\circ\) or \(300^\circ\)"}

for key, (tex, f, lo, hi, closed, mode, book) in EQ.items():
    qt = q(key)
    ok(tex in qt, f"{key} question text", f"printed {qt[:90]!r}")
    true = solve(f, lo, hi, closed)
    want = [round_to(x, mode) for x in true]
    if key in WORKED_PRINTED:
        printed = parse_angles(WORKED_PRINTED[key]) if WORKED_PRINTED[key] in LES else None
        ok(printed is not None, f"{key} printed solution line present")
        if printed is not None:
            ok(len(printed) == len(true) and all(abs(a_ - b_) < 1e-6 for a_, b_ in zip(sorted(printed), sorted(want))), f"{key} brute-force set", f"printed {printed}, computed {want}")
            ok(sorted(printed) == sorted(book), f"{key} book answer")
        continue
    a = v(key)
    if a is None:
        continue
    got = parse_angles(a)
    good = len(got) == len(true) and all(abs(g - w) < (1e-6 if mode != "min" else 1 / 120) for g, w in zip(sorted(got), sorted(want)))
    ok(good, f"{key} brute-force set over [{lo}, {hi}]", f"printed {[round(g, 4) for g in got]}, computed {[round(w, 4) for w in want]}")
    if book is not None:
        ok(len(got) == len(book) and all(abs(g - b) < 1e-6 for g, b in zip(sorted(got), sorted(book))), f"{key} book/sheet/school answer", f"{book}")

# omitted book parts (final review: they repeat past-paper items) must be absent from both files
for k in ("e9b", "e9g", "m15b", "m17c", "m17g", "m14a", "h26d"):
    ok(f'data-q="{k}"' not in LES and f'data-v="{k}"' not in ANS, f"{k} omitted from both files")

# no-solution item
ok(solve(lambda x: S(x) - 3, 0, 360) == [] and v("m17e") == "no solutions" and r"\sin\alpha=3" in q("m17e"), "m17e sin = 3 has no solutions")

# ------------------------------------------------------------------ exact values (sympy)
def tex2sym(t):
    t = t.replace(" ", "").replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    t = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", t)
    t = re.sub(r"\\sqrt(\d)", r"sqrt(\1)", t)
    for _ in range(3):
        t = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", t)
        t = re.sub(r"\\frac(\d)(\d)", r"((\1)/(\2))", t)
        t = re.sub(r"\\frac(\d)\{([^{}]+)\}", r"((\1)/(\2))", t)
    t = re.sub(r"(\d)sqrt", r"\1*sqrt", t)
    t = re.sub(r"(\d)\(", r"\1*(", t)
    t = t.replace("\\pm", "PM")
    return t


def val(key):
    a = v(key)
    if a is None:
        return None
    m = re.fullmatch(r"\\\((.*)\\\)", a)
    t = tex2sym((m.group(1) if m else a).split("=")[-1])
    if t.startswith("PM"):
        e = sp.sympify(t[2:].replace("PM", ""))
        return ("pm", sp.nsimplify(e))
    return sp.nsimplify(sp.sympify(t))


def same(a, b):
    if isinstance(a, tuple) or isinstance(b, tuple):
        return isinstance(a, tuple) and isinstance(b, tuple) and a[0] == b[0] and sp.simplify(a[1] - b[1]) == 0
    return a is not None and sp.simplify(a - b) == 0


d = lambda deg: sp.pi * sp.Integer(deg) / 180
sin, cos, tan, sq, R = (lambda x: sp.sin(d(x))), (lambda x: sp.cos(d(x))), (lambda x: sp.tan(d(x))), sp.sqrt, sp.Rational
VAL = {
    # key: (question substring, exact value, book answer or None)
    "d1a": (r"\cos^245^\circ+\sin30^\circ", cos(45) ** 2 + sin(30), None),
    "d1b": (r"\tan30^\circ\times\tan60^\circ", tan(30) * tan(60), None),
    "y1a": (r"\sin^260^\circ+\cos60^\circ", sin(60) ** 2 + cos(60), None),
    "y1b": (r"\cos30^\circ\times\tan30^\circ", cos(30) * tan(30), None),
    "e1a": (r"\sin60^\circ", sin(60), sq(3) / 2), "e1b": (r"\tan30^\circ", tan(30), 1 / sq(3)), "e1c": (r"\cos45^\circ", cos(45), 1 / sq(2)),
    "e2a": (r"\sin45^\circ\cos45^\circ+\sin30^\circ", sin(45) * cos(45) + sin(30), 1),
    "e2b": (r"\sin60^\circ\cos30^\circ-\cos60^\circ\sin30^\circ", sin(60) * cos(30) - cos(60) * sin(30), R(1, 2)),
    "e2c": (r"1+\tan^260^\circ", 1 + tan(60) ** 2, 4),
}
for key, (tex, exact, book) in VAL.items():
    qt = q(key) if key[0] != "d" and key[0] != "y" else LES.replace(" ", "")
    ok(tex in qt, f"{key} question text")
    got = val(key)
    ok(same(got, sp.nsimplify(sp.simplify(exact))), f"{key} exact value", f"printed {v(key)}, exact {sp.simplify(exact)}")
    if book is not None:
        ok(same(got, sp.nsimplify(book)), f"{key} book answer")

# sine-rule demos (triangle angles read from the figures) and Example 22
for name, key, xang, kang, k in (("t2_d1", "d1c", 45, 120, 8), ("t2_y1", "y1c", 30, 120, 6)):
    labs = re.findall(r">([^<>]+)</text>", open(os.path.join(SRC, "svg", name + ".svg"), encoding="utf-8").read())
    ok(sorted(labs) == sorted([f"{xang}°", f"{kang}°", str(k), "x"]), f"{name} figure labels", str(labs))
    ok(xang + kang < 180, f"{name} angle sum < 180")
    ok(same(val(key), sp.nsimplify(k * sin(xang) / sin(kang))), f"{key} sine rule exact", v(key))
ok(sp.simplify(12 * sin(30) / sin(135) - 6 * sq(2)) == 0 and "&amp;=6\\sqrt2.\\end{aligned}" in LES, "Example 22: x = 6 sqrt2")

# complementary angles
ok("\\sin40^\\circ=\\cos x" in LES and "\\cos15^\\circ=\\sin x" in LES, "C2 a questions printed")
for key, want, chk in (("d2a", 50, abs(math.sin(math.radians(40)) - math.cos(math.radians(50))) < 1e-12),
                       ("y2a", 75, abs(math.cos(math.radians(15)) - math.sin(math.radians(75))) < 1e-12)):
    ok(parse_angles(v(key)) == [want] and chk, f"{key} complementary angle")
ok(v("d2b") == r"\(\tan\theta\)" and v("y2b") == r"\(\sin\theta\)" and v("e5a") == r"\(\cos\theta\)" and v("e5d") == r"\(\tan\phi\)", "C2 and 5G Q5 identities (book 5G 5a cos theta, 5d tan phi)")
for th in (17, 63, 128, 251):
    ok(abs(math.cos(math.radians(90 - th)) / math.cos(math.radians(th)) - math.tan(math.radians(th))) < 1e-9
       and abs(math.sin(math.radians(90 - th)) * math.tan(math.radians(th)) - math.sin(math.radians(th))) < 1e-9
       and abs(math.cos(math.radians(90 - th)) / math.sin(math.radians(90 - th)) - math.tan(math.radians(th))) < 1e-9, f"identities at {th}")
ok(v("d2c") == r"\(0\)" and v("y2c") == r"\(0\)" and abs(math.sin(math.radians(25)) - math.cos(math.radians(65))) < 1e-12
   and abs(math.cos(math.radians(32)) - math.sin(math.radians(58))) < 1e-12, "C2 c parts = 0")


# given one, find another: (key, given (func, value), quadrants allowed, wanted func, book)
def others(func, value, quads):
    """All values of sin, cos, tan for angles with func = value in the given quadrants (brute force over degrees + exact)."""
    res = set()
    for qd in quads:
        sx, sy = {1: (1, 1), 2: (-1, 1), 3: (-1, -1), 4: (1, -1)}[qd]
        vv = sp.nsimplify(value)
        if func == "sin":
            if sp.sign(vv) not in (sy, 0):
                continue
            y, r = vv, 1
            x = sx * sp.sqrt(r ** 2 - y ** 2)
        elif func == "cos":
            if sp.sign(vv) not in (sx, 0):
                continue
            x, r = vv, 1
            y = sy * sp.sqrt(r ** 2 - x ** 2)
        else:
            if sp.sign(vv) != sx * sy:
                continue
            x = sx * 1
            y = vv * x
            r = sp.sqrt(x ** 2 + y ** 2)
        res.add((sp.nsimplify(sp.simplify(y / r)), sp.nsimplify(sp.simplify(x / r)), sp.nsimplify(sp.simplify(y / x))))
    return res


FIND = {
    "d3a": ("cos", R(2, 7), (1, 4), "sin", None), "d3b": ("cos", R(2, 7), (4,), "sin", None),
    "y3a": ("cos", R(-1, 3), (2, 3), "sin", None), "y3b": ("cos", R(-1, 3), (3,), "sin", None),
    "e8a": ("cos", R(1, 3), (1,), "tan", 2 * sq(2)), "e8b": ("cos", R(-4, 5), (2,), "tan", R(-3, 4)),
    "e8c": ("cos", R(1, 2), (4,), "sin", -sq(3) / 2), "e8d": ("tan", R(-2, 3), (4,), "cos", 3 / sq(13)),
    "e8e": ("cos", R(-40, 41), (2,), "sin", R(9, 41)), "e8f": ("sin", 1 / sq(5), (1,), "tan", R(1, 2)),
    "m15a": ("tan", R(1, 3), (1, 3), "sin", ("pm", 1 / sq(10))),
    "m15c": ("sin", R(3, 5), (1, 2), "cos", ("pm", R(4, 5))), "m15d": ("cos", R(-2, 3), (2, 3), "tan", ("pm", sq(5) / 2)),
    "m15e": ("sin", R(-12, 13), (3, 4), "tan", ("pm", R(12, 5))), "m15f": ("tan", -2 / sq(3), (2, 4), "cos", ("pm", sq(3) / sq(7))),
    "m16a": ("cos", R(4, 5), (4,), "tan", R(-3, 4)), "m16b": ("tan", R(-8, 15), (2,), "cos", R(-15, 17)),
    "m16c": ("sin", R(1, 4), (2,), "cos", -sq(15) / 4), "m16d": ("tan", R(35, 12), (1,), "sin", R(35, 37)),
    "m16e": ("sin", R(-21, 29), (4,), "tan", R(-21, 20)), "m16f": ("cos", R(-5, 6), (2,), "sin", sq(11) / 6),
}
IDX = {"sin": 0, "cos": 1, "tan": 2}
QUAD_OK = {  # condition in the printed question that fixes the quadrants
    "e8a": "acute", "e8b": "obtuse", "e8c": "reflex", "e8d": "reflex", "e8e": r"0^\circ\le\theta\le180^\circ",
    "e8f": r"-90^\circ\le\theta\le90^\circ", "m16a": r"\sin\alpha\lt0", "m16b": r"\sin\theta\gt0", "m16c": r"\tan\theta\lt0",
    "m16d": r"\cos\theta\gt0", "m16e": r"\cos\theta\gt0", "m16f": r"\tan\theta\lt0"}
for key, (func, value, quads, want, book) in FIND.items():
    if key in QUAD_OK:
        ok(QUAD_OK[key] in q(key), f"{key} quadrant condition printed")
    sols = others(func, value, quads)
    vals = sorted({s[IDX[want]] for s in sols}, key=lambda z: float(z))
    expect = ("pm", vals[-1]) if len(vals) == 2 and sp.simplify(vals[0] + vals[1]) == 0 else (vals[0] if len(vals) == 1 else None)
    got = val(key)
    ok(expect is not None and same(got, expect), f"{key} {want} given {func} = {value}, quadrants {quads}", f"printed {v(key)}, computed {vals}")
    if book is not None:
        ok(same(got, book if isinstance(book, tuple) else sp.nsimplify(book)), f"{key} book answer")
# 5F Q1 figures (x, y, r labels) and answers
for part in "abcd":
    labs = re.findall(r">([^<>]+)</text>", open(os.path.join(SRC, "svg", f"t2_f1{part}.svg"), encoding="utf-8").read())
    nums = [int(t.replace("−", "-")) for t in labs if re.fullmatch(r"−?\d+", t)]
    xs = {"a": (8, 15, 17), "b": (-6, 8, 10), "c": (-24, -7, 25), "d": (20, -21, 29)}[part]
    ok(sorted(nums) == sorted(xs) and xs[0] ** 2 + xs[1] ** 2 == xs[2] ** 2, f"5F Q1{part} figure labels", str(labs))
    x, y, r = xs
    for k, want in (("s", R(y, r)), ("c", R(x, r)), ("t", R(y, x))):
        ok(same(val(f"e7{part}{k}"), want), f"e7{part}{k}", v(f"e7{part}{k}"))
# Example 11 and 5F Q11, 5A Q15
ok(others("sin", R(1, 5), (1, 2)) == {(R(1, 5), 2 * sq(6) / 5, 1 / (2 * sq(6))), (R(1, 5), -2 * sq(6) / 5, -1 / (2 * sq(6)))}, "Example 11 values")
p_, q_ = sp.symbols("p q", positive=True)
ok(v("h30c") == r"\(-\dfrac{\sqrt{q^2-p^2}}{q}\)" and v("h30t") == r"\(-\dfrac{p}{\sqrt{q^2-p^2}}\)", "h30 printed forms")
for pv, qv in ((1, 2), (3, 5), (2, 7)):
    th = math.pi - math.asin(pv / qv)
    ok(abs(math.cos(th) + math.sqrt(qv * qv - pv * pv) / qv) < 1e-12 and abs(math.tan(th) + pv / math.sqrt(qv * qv - pv * pv)) < 1e-12, f"h30 numeric p={pv}, q={qv}")
al = math.atan(math.sqrt(5) / 2)
ok(same(val("h26b"), 3) and same(val("h26s"), sq(5) / 3) and same(val("h26c"), R(2, 3))
   and abs(math.sin(al) - math.sqrt(5) / 3) < 1e-12 and abs(math.cos(al) - 2 / 3) < 1e-12, "5A Q15 (book: 3, sqrt5/3, 2/3)")

# ------------------------------------------------------------------ past papers (mini exam)
ok(parse_angles(v("pp1")) == [60] and [x for x in range(1, 90) if abs(math.sin(math.radians(x)) - math.cos(math.radians(30))) < 1e-9] == [60], "pp1 x = 60")
ok(v("pp2") == "A" and all(abs(math.cos(math.radians(90 - t)) / math.sin(math.radians(180 - t)) - 1) < 1e-9 for t in (10, 55, 130, 200)), "pp2 A (= 1)")
ok(v("pp3") == "A" and [round(x) for x in solve(lambda x: S(x) + 0.5, 0, 360)] == [210, 330] and "(A)&ensp;\\(\\theta=210^\\circ\\) and \\(\\theta=330^\\circ\\)" in LES, "pp3 A")
ok(v("pp4") == "B" and abs(30 * math.tan(math.radians(30)) - 10 * math.sqrt(3)) < 1e-12 and "(B)&ensp;\\(10\\sqrt3\\)" in LES, "pp4 B = 10 sqrt3")
ok(same(val("pp5"), sp.nsimplify(tan(150) + sin(45))) and same(val("pp5"), (3 * sq(2) - 2 * sq(3)) / 6) and "\\tan150^\\circ+\\sin45^\\circ" in LES, "pp5 (school: (3sqrt2 - 2sqrt3)/6)")
ok(same(val("pp6"), ("pm", 1 / sq(5))) and "\\cos\\theta=\\dfrac{2}{\\sqrt5}" in LES, "pp6 +-1/sqrt5 (school)")
ok(sorted(parse_angles(v("pp7"))) == [round(x) for x in solve(lambda x: 1 + math.sqrt(3) * T(x) - 2, 0, 360)] == [30, 210] and "1+\\sqrt3\\tan\\theta=2" in LES, "pp7 30, 210 (school)")
ok(sorted(parse_angles(v("pp8"))) == [round(x) for x in solve(lambda x: S(180 - x) - S(90 - x), 0, 360)] == [45, 225] and "\\sin(180^\\circ-\\theta)=\\sin(90^\\circ-\\theta)" in LES, "pp8 45, 225 (school)")
ok(sorted(parse_angles(v("pp9a"))) == [round(x) for x in solve(lambda x: S(x) - 0.416, 0, 360)] == [25, 155] and "\\sin\\theta=0.416" in LES, "pp9 (i) 25, 155 (school)")
ok(sorted(parse_angles(v("pp9b"))) == [round(x) for x in solve(lambda x: C(x) + 0.302, 0, 360)] == [108, 252] and "\\cos\\theta=-0.302" in LES, "pp9 (ii) 108, 252 (school)")
first2 = [round(x, 2) for x in solve(lambda x: 20 * C(x) + 147 - 150, 0, 720)][:2]
ok(sorted(parse_angles(v("pp10"))) == first2 == [81.37, 278.63] and "h=20\\cos x^\\circ+147" in LES, "pp10 81.37, 278.63 (school)")
# Hard Q26: Hornsby Girls 2021 Q12 (trapezium). AD = AX + XY + YD, computed exactly from the givens.
_ax = 12 * sp.sin(sp.pi / 4); _bx = 12 * sp.cos(sp.pi / 4); _yd = _bx * sp.tan(sp.pi * (150 - 90) / 180)
_ad = sp.nsimplify(_ax + 4 * sq(2) + _yd)
_opts = {"A": 6 * sq(2) + 6 * sq(6), "B": 10 * sq(2) + 2 * sq(6), "C": 10 * sq(2) + 6 * sq(6), "D": 16 * sq(2) + 6 * sq(6)}
_hit = [k for k, e in _opts.items() if sp.simplify(e - _ad) == 0]
ok(_hit == ["C"] and v("h32") == "C", "h32 Hornsby Q12 AD = 10sqrt2 + 6sqrt6 (key C)", str(_ad))
ok(all(t in q("h32") for t in (r"AB=12", r"BC=4\sqrt2", r"\angleABX=45^\circ", r"\angleBCD=150^\circ")), "h32 givens printed")
ok("C.&ensp;\\(10\\sqrt2+6\\sqrt6\\)" in LES, "h32 option C printed")
_svg = open(os.path.join(SRC, "svg", "pp_hgs21_12.svg"), encoding="utf-8").read()
ok(all(t in _svg for t in (">12 m<", ">4√2 m<", ">45°<", ">150°<")), "h32 figure labels")
ok(v("m22") == "C" and all(abs((math.sin(math.radians(t)) ** 2 + math.cos(math.radians(t)) * math.cos(math.radians(90 - t))) /
                              (math.cos(math.radians(t)) ** 2 + math.sin(math.radians(t)) * math.sin(math.radians(90 - t))) - math.tan(math.radians(t))) < 1e-9
                          for t in (10, 55, 130, 200)), "m22 Hornsby C (tan)")
# ------------------------------------------------------------------ Concept 3: Pythagorean identity and proofs
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
_TR = standard_transformations + (implicit_multiplication_application, convert_xor)
th, al, be, ph, Asym, xs = sp.symbols("th al be ph A x")
_NS = {"th": th, "al": al, "be": be, "ph": ph, "A": Asym, "x": xs, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt, "pi": sp.pi}


def _braced(t, i):
    """t[i] == '{': return (content, index after the closing brace)."""
    depth, j = 0, i
    while True:
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                return t[i + 1:j], j + 1
        j += 1


def tex(t):
    """A small TeX-to-sympy converter for the expressions printed in the proofs (sin, cos, tan, powers,
    fractions, surds, degrees, Greek letters)."""
    t = t.replace("&amp;", "&").replace("\\left", "").replace("\\right", "")
    for b in ("\\Bigg", "\\bigg", "\\Big", "\\big"):
        t = t.replace(b, "")
    t = re.sub(r"\\[,;!]|\\quad|\\qquad|~", " ", t)
    t = t.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac").replace("\\times", "*").replace("\\cdot", "*")
    for g, r in (("\\theta", "th"), ("\\alpha", "al"), ("\\beta", "be"), ("\\varphi", "ph"), ("\\phi", "ph")):
        t = t.replace(g, " " + r + " ")
    while "\\frac" in t:
        i = t.index("\\frac")
        if t[i + 5] == "{":
            a, j = _braced(t, i + 5)
        else:
            a, j = t[i + 5], i + 6
        if t[j] == "{":
            b, k = _braced(t, j)
        else:
            b, k = t[j], j + 1
        t = t[:i] + f"(({a})/({b}))" + t[k:]
    t = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", t)
    t = re.sub(r"\\sqrt\s*(\d+)", r"sqrt(\1)", t)
    t = re.sub(r"(\d+)\s*\^\\circ", r"(\1*pi/180)", t)
    t = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", t)

    def trig(m):
        f, pw, arg = m.group(1), m.group(2), m.group(3).strip()
        core = f"{f}({arg})"
        return f"({core})^{pw}" if pw else core
    for _ in range(3):
        t = re.sub(r"\\(sin|cos|tan)\s*(?:\^(\d))?\s*(\([^()]*(?:\([^()]*\)[^()]*)*\)|[A-Za-z]+\b|\d+)", trig, t)
    t = t.replace("{", "(").replace("}", ")")
    return parse_expr(t, local_dict=_NS, transformations=_TR)


def eq0(e):
    if sp.simplify(sp.expand_trig(e)) == 0:
        return True
    return sp.simplify(sp.trigsimp(sp.together(e))) == 0


ANG = (0.3, 0.71, 1.13, 2.2, 3.5, 4.0, 5.5)


def num_eq(e1, e2):
    syms = list((e1 - e2).free_symbols)
    for a in ANG:
        sub = {s_: a + 0.17 * k for k, s_ in enumerate(syms)}
        try:
            d = complex(sp.N((e1 - e2).subs(sub)))
        except (TypeError, ZeroDivisionError):
            continue
        if abs(d) > 1e-9:
            return False
    return True


def proof(key, lhs_t, rhs_t, qtext):
    """The identity lhs = rhs is true (sympy + numeric). The printed proof in data-v=key is a chain
    'LHS = E1 = E2 = ... = RHS' (or RHS = ... chains): every link is equal, it starts at the side it
    names and it ends at the other side."""
    ok(re.sub(r"\s+", "", qtext) in re.sub(r"\s+", "", q(key) or ""), f"{key} statement printed", qtext)
    L_, R_ = tex(lhs_t), tex(rhs_t)
    ok(eq0(L_ - R_) and num_eq(L_, R_), f"{key} identity {lhs_t} = {rhs_t} (sympy and numeric)")
    raw = v(key)
    if raw is None:
        return
    body = re.sub(r"^\\\[\\begin\{aligned\}|\\end\{aligned\}\\\]$", "", raw.replace("&amp;", "&").strip())
    lines = [ln for ln in re.split(r"\\\\", body) if ln.strip()]
    chains, cur = [], None
    for ln in lines:
        ln = re.sub(r"\\q?quad\s*\\text\{[^}]*\}(?:[^\\&]*\))?", "", ln)
        ln = re.sub(r"&&\\text\{.*$", "", ln).strip().rstrip(".").strip()
        m = re.match(r"\\text\{(LHS|RHS)\}\s*&?=\s*(.*)$", ln)
        if m:
            cur = [m.group(1), []]
            chains.append(cur)
            ln = m.group(2)
        else:
            ln = re.sub(r"^&?=\s*", "", ln)
        cur[1].append(ln.strip().rstrip(".").strip())
    good = bool(chains)
    ends = []
    for side, exprs in chains:
        start = L_ if side == "LHS" else R_
        other = R_ if side == "LHS" else L_
        vals = []
        for e in exprs:
            if e in ("\\text{RHS}", "\\text{LHS}"):
                vals.append(R_ if e == "\\text{RHS}" else L_)
            else:
                try:
                    vals.append(tex(e))
                except Exception as exc:  # an unreadable printed line is a failure, not a crash
                    ok(False, f"{key} printed line readable", f"{e!r}: {exc}")
                    return
        good &= num_eq(vals[0], start) and eq0(vals[0] - start)
        for a_, b_ in zip(vals, vals[1:]):
            good &= num_eq(a_, b_) and eq0(a_ - b_)
        ends.append((exprs[-1], vals[-1], other))
    if len(chains) == 1:
        e, val, other = ends[0]
        good &= e in ("\\text{RHS}", "\\text{LHS}") and eq0(val - other)
    else:
        good &= eq0(ends[0][1] - ends[1][1])
    ok(good, f"{key} printed proof: every line equal, ends at the target", f"{len(lines)} lines")


# demos and your turns, Worked example 12 (printed in the lesson)
ok(sp.simplify(tex(r"4\sin^2\theta+4\cos^2\theta") - tex(v("dp3a").strip("\\()"))) == 0 and v("dp3a") == r"\(4\)", "dp3a 4(sin^2+cos^2) = 4")
proof("dp3b", r"(1-\sin^2\theta)\tan^2\theta", r"\sin^2\theta", r"Prove that \((1-\sin^2\theta)\tan^2\theta=\sin^2\theta\)")
ok(eq0(tex(r"3-3\cos^2\theta") - tex(r"3\sin^2\theta")) and v("yp3a") == r"\(3\sin^2\theta\)", "yp3a 3 - 3cos^2 = 3 sin^2")
proof("yp3b", r"\tan\theta\,(1-\sin^2\theta)", r"\sin\theta\cos\theta", r"Prove that \(\tan\theta\,(1-\sin^2\theta)=\sin\theta\cos\theta\)")
_w12 = LES[LES.index('data-q="w12"'):]
_w12 = _w12[_w12.index("\\[\\begin{aligned}"):_w12.index("\\end{aligned}\\]") + len("\\end{aligned}\\]")]
ANS_SAVE = ANS
ANS = ANS + f'<span data-v="w12chk">{_w12}</span>'
LES_SAVE = LES
LES = LES + '<span data-q="w12chk">Prove that \\((1-\\cos\\theta)(1+\\cos\\theta)=\\sin^2\\theta\\)</span>'
proof("w12chk", r"(1-\cos\theta)(1+\cos\theta)", r"\sin^2\theta", r"Prove that \((1-\cos\theta)(1+\cos\theta)=\sin^2\theta\)")
ANS, LES = ANS_SAVE, LES_SAVE
ok(r"Prove that \((1-\cos\theta)(1+\cos\theta)=\sin^2\theta\)" in LES, "Worked example 12 statement (book)")

# Easy: 5G Q1, Q4, Q6/Q7 (book answers PDF 547)
ok(abs(math.sin(math.radians(16)) - math.cos(math.radians(74))) < 1e-12 and "0.2756" in v("e3a") and round(math.sin(math.radians(16)), 4) == 0.2756, "e3a sin16 = cos74 = 0.2756")
ok(abs(math.sin(math.radians(23)) ** 2 + math.cos(math.radians(23)) ** 2 - 1) < 1e-12 and v("e3d") == "1.0000"
   and round(math.sin(math.radians(23)) ** 2, 4) == 0.1527 and round(math.cos(math.radians(23)) ** 2, 4) == 0.8473
   and "0.3907" in ANS and "0.9205" in ANS, "e3d sin^2 23 + cos^2 23 = 1 (0.1527 + 0.8473)")
proof("e4a", r"\tan\theta\cos\theta", r"\sin\theta", r"\(\tan\theta\cos\theta=\sin\theta\)")
ok(v("e6a") == r"\(1\)" and r"\sin^2\alpha+\cos^2\alpha" in q("e6a"), "e6a sin^2 + cos^2 = 1 (book 1)")
ok(v("e6b") == r"\(\cos^2\beta\)" and eq0(tex(r"1-\sin^2\beta") - tex(r"\cos^2\beta")) and r"1-\sin^2\beta" in q("e6b"), "e6b 1 - sin^2 = cos^2 (book)")
# Medium: 5G Q8b, Q11, Fort St 2022 D Q2, NBCS 2022 Q33
ok(v("m13b") == r"\(\tan^2\beta\)" and eq0(tex(r"\frac{\sin^2\beta}{\cos^2\beta}") - tex(r"\tan^2\beta")), "m13b sin^2/cos^2 = tan^2 (book)")
for k_, l_, r_ in (("m14b", r"(1+\tan^2\alpha)\cos^2\alpha", "1"),
                   ("m14c", r"(\sin A+\cos A)^2", r"1+2\sin A\cos A"), ("m14d", r"\cos^2 x-\sin^2 x", r"1-2\sin^2 x"),
                   ("m14f", r"3\cos^2\theta-2", r"1-3\sin^2\theta"), ("m14i", r"\cos^4 x+\cos^2 x\sin^2 x", r"\cos^2 x")):
    proof(k_, l_, r_, f"\\({l_}={r_}\\)")
proof("m25", r"\frac{\cos(90^\circ-\theta)\sin\theta}{\sin(90^\circ-\theta)\cos\theta}", r"\tan^2\theta",
      r"\(\dfrac{\cos\big(90^\circ-\theta\big)\sin\theta}{\sin\big(90^\circ-\theta\big)\cos\theta}=\tan^2\theta\)")
_AC = sp.sqrt(sp.Integer(2) + 4)
ok(v("m24a") == r"\(AC=\sqrt6\)" and _AC == sp.sqrt(6), "m24a AC = sqrt6 (school)")
ok(sp.simplify(sp.sqrt(2) / _AC - sp.sqrt(3) / 3) == 0 and v("m24b") == r"\(\dfrac{\sqrt3}{3}\)", "m24b cos A = sqrt3/3 (school)")
_sA, _cA = 2 / _AC, sp.sqrt(2) / _AC
ok(sp.simplify(_sA ** 2 + _cA ** 2 - 1) == 0, "m24c sin^2 A + cos^2 A = 1 with the triangle's values")
proof("m24c", r"\Big(\dfrac{2}{\sqrt6}\Big)^2+\Big(\dfrac{\sqrt3}{3}\Big)^2", "1", r"Show that \(\sin^2 A+\cos^2 A=1\)")
_s = open(os.path.join(SRC, "svg", "pp_nbcs22_33.svg"), encoding="utf-8").read()
ok(all(t in _s for t in (">√2 cm<", ">2 cm<", ">A<", ">B<", ">C<", ">NOT TO SCALE<")), "NBCS 2022 Q33 figure labels")
# Hard: 5A Q15d, 5G Q13c, North Sydney Boys 2022 Q24(a)-(d)
proof("h29c", r"\sin^4 A-\cos^4 A", r"\sin^2 A-\cos^2 A", r"\(\sin^4 A-\cos^4 A=\sin^2 A-\cos^2 A\)")
c_th = sp.symbols("c_th")
xpos = sp.symbols("xpos", positive=True)
_cos = sp.solve(sp.Eq((6 * sp.sqrt(7)) ** 2, xpos ** 2 + (3 * xpos) ** 2 - 2 * xpos * 3 * xpos * c_th), c_th)[0]
ok(sp.simplify(_cos - (5 * xpos ** 2 - 126) / (3 * xpos ** 2)) == 0 and "5x^2-126" in v("h28a"), "h28a cosine rule gives (5x^2 - 126)/(3x^2)")
ok(sp.simplify(sp.expand(9 * xpos ** 4 * (27 / xpos ** 2 + ((5 * xpos ** 2 - 126) / (3 * xpos ** 2)) ** 2 - 1)) - (16 * xpos ** 4 - 1017 * xpos ** 2 + 15876)) == 0
   and v("h28c") == r"\(16x^4-1017x^2+15876=0\)", "h28c identity gives 16x^4 - 1017x^2 + 15876 = 0")
_roots = sorted(sp.solve(16 * xpos ** 4 - 1017 * xpos ** 2 + 15876, xpos))
ok(_roots == [sp.Rational(21, 4), 6] and v("h28d") == r"\(x=6\) or \(x=\dfrac{21}{4}\)", "h28d x = 6 or 21/4 (school)", str(_roots))
for xv in (6, sp.Rational(21, 4)):
    ct = (5 * xv ** 2 - 126) / (3 * xv ** 2)
    st = sp.sqrt(27) / xv
    ok(abs(float(ct ** 2 + st ** 2) - 1) < 1e-12 and 0 < float(ct) < 1, f"h28 x = {xv}: cos and sin consistent, theta acute")
    T = math.acos(float(ct))
    D = (float(xv) * math.cos(T), float(xv) * math.sin(T))
    Ap, Cp = (0, 6 * math.sqrt(3)), (3 * float(xv), 0)
    ok(abs(math.dist(D, Ap) - float(xv)) < 1e-9 and abs(math.dist(D, Cp) - 6 * math.sqrt(7)) < 1e-9 and abs(math.sin(T) - float(st)) < 1e-12,
       f"h28 x = {xv}: coordinates give AD = DB = x, CD = 6 sqrt7, sin theta = sqrt27/x")
ok(v("h28b") == r"\(\sin\theta=\dfrac{\sqrt{27}}{x}\)" and "3\\sqrt3" in ANS, "h28b sin theta = sqrt27/x")
_s = open(os.path.join(SRC, "svg", "pp_nsb22_24.svg"), encoding="utf-8").read()
ok(all(t in _s for t in (">A<", ">B<", ">C<", ">D<", ">6√3 cm<", ">6√7 cm<", ">x cm<", ">3x cm<", ">θ°<", ">Diagram not to scale<")), "NSB 2022 Q24 figure labels")

marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', LES.split("Past-paper homework:mini exam")[1])]
ok(sum(marks) == 19 and "<b>19 marks</b>" in LES and "Suggested time: 30 minutes" in LES and 5 * round(1.5 * 19 / 5) == 30, "mini exam 19 marks, 30 minutes", str(marks))

print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
