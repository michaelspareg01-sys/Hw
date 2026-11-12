r"""Check of Lesson T3 (Year 10 Trigonometry part 2): The ambiguous case, tied to the printed HTML.

Reads workspace/build/y10trig/lt3.html (questions), a_t3.html (answers) and the label text of the T3
figures in svg/.
  - Every triangle is solved independently from its data with a small solver: AAS (sine rule for a side),
    ASS (sine rule for an angle, returning BOTH cases where they exist and rejecting a case whose angle sum
    is not below 180 degrees), SAS (cosine rule / area), area -> side and area -> angle (both angles).
    For every triangle produced, the solver asserts that the angles sum to 180 degrees and that the sides
    satisfy the triangle inequality and the sine rule.
  - The data of each item are typed in DATA and tied to the page: the printed question text must contain
    them, or the figure's label text must contain them (each figure must carry exactly its labels).
  - Every answer in a_t3.html carries data-v="KEY" (each key exactly once). It is parsed (degrees, degrees
    and minutes, decimals, surds, letters) and compared with the solver at the question's rounding, and
    with the book's answer (Year 11 Advanced PDF 548, 5I; PDF 549, 5J) or the school's answer.
Exit status 1 if anything fails.  Run: python3 workspace/checks/y10trig_t3.py
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


LES = open(os.path.join(SRC, "lt3.html"), encoding="utf-8").read()
ANS = open(os.path.join(SRC, "a_t3.html"), encoding="utf-8").read()
LESF = re.sub(r"\s+", "", LES)


def _inner(html, key):
    ms = list(re.finditer(r'<span data-v="%s">' % re.escape(key), html))
    if len(ms) != 1:
        return None, len(ms)
    i, depth = ms[0].end(), 1
    while depth:
        o, c = html.find("<span", i), html.find("</span>", i)
        if o != -1 and o < c:
            depth, i = depth + 1, o + 1
        else:
            depth, i = depth - 1, c + 7
    return html[ms[0].end():i - 7], 1


def v(key):
    s, n = _inner(ANS, key)
    if s is None:
        ok(False, f"answer {key}", f"data-v found {n} times")
        return ""
    return s.strip()


def printed(*frags):
    """Every fragment (whitespace ignored) must appear in the lesson page."""
    miss = [f for f in frags if re.sub(r"\s+", "", f) not in LESF]
    return not miss, miss


def labels(name):
    return sorted(re.findall(r">([^<>]+)</text>", open(os.path.join(SRC, "svg", name + ".svg"), encoding="utf-8").read()))


def fig(name, want):
    ok(labels(name) == sorted(want), f"figure {name} labels", f"{labels(name)} vs {sorted(want)}")


def angles_of(s):
    """'49^\\circ46'' / '49°' / '\\theta\\doteqdot41^\\circ49' or 138^\\circ11'' -> list of degrees."""
    s = s.replace("\\circ", "°").replace("^", "").replace("{", "").replace("}", "").replace("′", "'")
    out = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*°\s*(?:(\d+)')?", s):
        out.append(float(m.group(1)) + (int(m.group(2)) / 60 if m.group(2) else 0))
    return out


def num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None


S = lambda d: math.sin(math.radians(d))
C = lambda d: math.cos(math.radians(d))


# ------------------------------------------------------------------ solver
def check_tri(a, b, c, A, B, Cc, label):
    good = abs(A + B + Cc - 180) < 1e-7 and min(A, B, Cc) > 0 and a + b > c and b + c > a and a + c > b
    good = good and abs(a / S(A) - b / S(B)) < 1e-6 * a / S(A) and abs(a / S(A) - c / S(Cc)) < 1e-6 * a / S(A)
    ok(good, f"{label}: triangle valid (angle sum 180, triangle inequality, sine rule)")
    return good


def aas(side, opp, want_opp, third=None, label=""):
    """Side `side` opposite angle `opp`; return the side opposite angle `want_opp`."""
    other = 180 - opp - want_opp
    x = side * S(want_opp) / S(opp)
    y = side * S(other) / S(opp)
    check_tri(side, x, y, opp, want_opp, other, label)
    return x


def ass(known_ang, side_opp_known, side_opp_unknown, label=""):
    """Sine rule for an angle: all valid triangles (both cases where they exist)."""
    s = side_opp_unknown * S(known_ang) / side_opp_known
    if s > 1 + 1e-12:
        return []
    a1 = math.degrees(math.asin(min(1, s)))
    res = []
    for ang in sorted({a1, 180 - a1}):
        third = 180 - known_ang - ang
        if third <= 1e-9:
            continue
        third_side = side_opp_known * S(third) / S(known_ang)
        if check_tri(side_opp_known, side_opp_unknown, third_side, known_ang, ang, third, f"{label} case {ang:.2f}"):
            res.append(ang)
    return res


def sas_side(b, c, A, label=""):
    a = math.sqrt(b * b + c * c - 2 * b * c * C(A))
    B = math.degrees(math.acos((a * a + c * c - b * b) / (2 * a * c)))
    check_tri(a, b, c, A, B, 180 - A - B, label)
    return a


def area_to_angle(area, p, q):
    s = 2 * area / (p * q)
    if s > 1:
        return []
    a = math.degrees(math.asin(s))
    out = sorted({a, 180 - a})
    for t in out:
        r = sas_side(p, q, t, f"area->angle {t:.2f}")
        ok(abs(0.5 * p * q * S(t) - area) < 1e-9, f"area->angle {t:.2f} gives area {area}")
    return out


def dm(x):
    d = int(x)
    m = round((x - d) * 60)
    return (d + 1, 0) if m == 60 else (d, m)


def same_dm(got, want):
    return len(got) == len(want) and all(dm(g) == dm(w) for g, w in zip(sorted(got), sorted(want)))


def same_deg(got, want):
    return len(got) == len(want) and all(round(g) == round(w) for g, w in zip(sorted(got), sorted(want)))


# ------------------------------------------------------------------ lesson examples
ok(printed(r"sides 5 and 8 and an included angle of 120°")[0], "C1 demo text")
ok(sp.simplify(sp.sympify("10*sqrt(3)") - sp.Rational(1, 2) * 5 * 8 * sp.sin(sp.pi * 2 / 3)) == 0 and v("d1") == r"\(10\sqrt3\)", "C1 demo exact area 10 sqrt3")
ok(printed(r"sides 6 and 10 and an included angle of 150°")[0] and v("y1") == r"\(15\)" and abs(0.5 * 60 * S(150) - 15) < 1e-12, "C1 your turn area 15")
ok(printed("has area 40 m², and two of its sides, \\(x\\) m and 15 m, include an angle of 58°")[0], "C2 demo a text")
ok(float(v("d2a")) == float(f"{80 / (15 * S(58)):.4g}"), "C2 demo a x (4 s.f.)", v("d2a"))
ok(printed("has area 30 cm², and two of its sides are 10 cm and 9 cm")[0] and same_dm(angles_of(v("d2b")), area_to_angle(30, 10, 9)), "C2 demo b both angles", v("d2b"))
ok(printed("has area 50 m², and two of its sides, \\(x\\) m and 20 m, include an angle of 64°")[0] and float(v("y2a")) == float(f"{100 / (20 * S(64)):.4g}"), "C2 YT a", v("y2a"))
ok(printed("has area 21 cm², and two of its sides are 8 cm and 7 cm")[0] and same_dm(angles_of(v("y2b")), area_to_angle(21, 8, 7)), "C2 YT b both angles", v("y2b"))
ok(printed(r"\(\angle B=45^\circ\), \(AC=10\) and \(BC=5\sqrt6\)")[0] and same_deg(angles_of(v("d3")), ass(45, 10, 5 * math.sqrt(6), "C3 demo")), "C3 demo both cases", v("d3"))
ok(printed(r"\(\angle Q=30^\circ\), \(PR=4\) and \(QR=4\sqrt2\)")[0] and same_deg(angles_of(v("y3")), ass(30, 4, 4 * math.sqrt(2), "C3 YT")), "C3 YT both cases", v("y3"))
ok(printed(r"\(\angle C=75^\circ\), \(AB=8\) and \(BC=5\)")[0] and same_dm(angles_of(v("d4")), ass(75, 8, 5, "C4 demo")), "C4 demo one case", v("d4"))
ok(printed(r"\(\angle Z=70^\circ\), \(XY=9\) and \(YZ=6\)")[0] and same_dm(angles_of(v("y4")), ass(70, 9, 6, "C4 YT")), "C4 YT one case", v("y4"))
# worked examples 23-27 (values printed in the boxes)
fig("t3_ex23", ["3", "4", "135°"])
ok(abs(0.5 * 12 * S(135) - 3 * math.sqrt(2)) < 1e-12 and "3\\sqrt2\\text{ square units.}" in LES, "Example 23: 3 sqrt2")
fig("t3_ex24", ["x", "24 m", "67°"])
ok(f"{72 / (12 * S(67)):.4g}" == "6.518" and "6.518\\text{ metres.}" in LES, "Example 24: 6.518")
fig("t3_ex25", ["13 cm", "12 cm", "θ"])
ok(same_dm(area_to_angle(60, 13, 12), [50 + 17 / 60, 129 + 43 / 60]) and "50^\\circ17'\\) or \\(129^\\circ43'" in LES, "Example 25: 50 17' or 129 43'")
fig("t3_ex26", ["7√6", "14", "45°", "θ"])
ok(same_deg(ass(45, 14, 7 * math.sqrt(6), "Example 26"), [60, 120]) and "\\(\\theta=60^\\circ\\) or \\(120^\\circ\\)" in LES, "Example 26: 60 or 120")
fig("t3_ex27", ["4", "7", "80°", "θ"])
ok(same_dm(ass(80, 7, 4, "Example 27"), [34.25]) and "\\theta\\doteqdot34^\\circ15'\\) is the only solution" in LES, "Example 27: 34 15' only")

# ------------------------------------------------------------------ Exercise 5I (book answers PDF 548)
Q1 = {"a": ("t3_q1a", ["10", "x", "50°", "70°"], 10, 70, 50, 8.2), "b": ("t3_q1b", ["x", "3", "40°", "110°"], 3, 40, 110, 4.4),
      "c": ("t3_q1c", ["4", "x", "85°", "55°"], 4, 55, 85, 4.9), "d": ("t3_q1d", ["x", "2", "75°", "65°"], 2, 75, 65, 1.9),
      "e": ("t3_q1e", ["7", "x", "71°", "46°"], 7, 46, 71, 9.2), "f": ("t3_q1f", ["5", "x", "38°", "118°"], 5, 118, 38, 3.5)}
for p, (name, labs, side, opp, want, book) in Q1.items():
    fig(name, labs)
    x = round(aas(side, opp, want, label=f"5I Q1{p}"), 1)
    ok(num(v(f"e1{p}")) == x == book, f"5I Q1{p} x = {x}", f"printed {v('e1' + p)}, book {book}")
Q2 = {"a": ("t3_q2a", ["12", "a", "70°", "60°"], 12, 50, 70, 14.72), "b": ("t3_q2b", ["20", "b", "25°", "75°"], 20, 25, 80, 46.61),
      "c": ("t3_q2c", ["15", "c", "48°", "112°"], 15, 112, 20, 5.53)}
for p, (name, labs, side, opp, want, book) in Q2.items():
    fig(name, labs)
    x = round(aas(side, opp, want, label=f"5I Q2{p}"), 2)
    ok(num(v(f"e2{p}")) == x == book, f"5I Q2{p} = {x}", f"printed {v('e2' + p)}, book {book}")
Q3 = {"a": ("t3_q3a", ["5", "4", "70°", "θ"], 70, 5, 4, 49), "b": ("t3_q3b", ["10", "8", "85°", "θ"], 85, 10, 8, 53),
      "c": ("t3_q3c", ["9", "13", "100°", "θ"], 100, 13, 9, 43), "d": ("t3_q3d", ["6", "17", "72°", "θ"], 72, 17, 6, 20),
      "e": ("t3_q3e", ["12", "7", "124°", "θ"], 124, 12, 7, 29), "f": ("t3_q3f", ["19", "16", "53°", "θ"], 53, 19, 16, 42)}
for p, (name, labs, K, sk, su, book) in Q3.items():
    fig(name, labs)
    sols = ass(K, sk, su, f"5I Q3{p}")
    ok(len(sols) == 1 and angles_of(v(f"e3{p}")) == [round(sols[0])] == [book], f"5I Q3{p} single solution {sols}", f"printed {v('e3' + p)}")
Q4 = {"a": ("t3_q4a", ["3 cm", "4 cm", "50°"], 3, 4, 50, 5), "b": ("t3_q4b", ["5 cm", "8 cm", "70°"], 5, 8, 70, 19),
      "c": ("t3_q4c", ["7 cm", "7 cm", "115°"], 7, 7, 115, 22)}
for p, (name, labs, b, c, A, book) in Q4.items():
    fig(name, labs)
    sas_side(b, c, A, f"5I Q4{p}")
    ar = round(0.5 * b * c * S(A))
    ok(num(v(f"e4{p}")) == ar == book, f"5I Q4{p} area {ar}", v(f"e4{p}"))
# Q5, Q6, Q7
ok(printed(r"\(A=43^\circ\), \(B=101^\circ\) and \(a=7.5\) cm")[0], "5I Q5 text")
ok(num(v("m8b")) == round(aas(7.5, 43, 101, label="5I Q5"), 2) == 10.80 and num(v("m8c")) == round(7.5 * S(36) / S(43), 2) == 6.46, "5I Q5 b, c (book 10.80, 6.46)")
ok(printed(r"\(y=32\) cm, \(Y=58^\circ\) and \(Z=52^\circ\)")[0], "5I Q6 text")
per = 32 + aas(32, 58, 70, label="5I Q6") + 32 * S(52) / S(58)
ok(num(v("m9b")) == round(per) == 97, "5I Q6 perimeter (book 97)", f"{per:.2f}")
ok(printed(r"\(a=2.8\) cm, \(b=2.7\) cm and \(A=52^\circ21'\)")[0], "5I Q7 text")
A7 = 52 + 21 / 60
B7 = ass(A7, 2.8, 2.7, "5I Q7")
ok(len(B7) == 1 and dm(B7[0]) == (49, 46) and angles_of(v("m10a")) and dm(angles_of(v("m10a"))[0]) == (49, 46), "5I Q7a B = 49 46' (single)")
Bm = 49 + 46 / 60
Cm = 180 - A7 - Bm
ok(dm(Cm) == (77, 53) and dm(angles_of(v("m10b"))[0]) == (77, 53), "5I Q7b C = 77 53'")
ok(num(v("m10c")) == round(0.5 * 2.8 * 2.7 * S(Cm), 2) == 3.70, "5I Q7c area 3.70")
# Q8, Q9, Q10
fig("t3_q8a", ["9 cm", "5 cm", "22°"])
fig("t3_q8b", ["9 cm", "5 cm", "22°"])
s8 = ass(22, 5, 9, "5I Q8")
ok(same_deg(angles_of(v("m11")), s8) and [round(x) for x in s8] == [42, 138], "5I Q8 both cases (book 42, 138)", v("m11"))
fig("t3_q9a", ["4 cm", "6 cm", "36°"])
fig("t3_q9b", ["4 cm", "6 cm", "36°"])
s9 = ass(36, 4, 6, "5I Q9")
ok(same_deg(angles_of(v("m12")), s9) and [round(x) for x in s9] == [62, 118], "5I Q9 both cases (book 62, 118)", v("m12"))
ok(printed(r"\(p=7\) cm, \(q=15\) cm and \(\angle P=25^\circ50'\)")[0], "5I Q10 text")
P10 = 25 + 50 / 60
s10 = ass(P10, 7, 15, "5I Q10")
ok(same_dm(angles_of(v("m13a")), s10) and [dm(x) for x in s10] == [(69, 2), (110, 58)], "5I Q10a both cases (book 69 2', 110 58')", v("m13a"))
rs = [round(7 * S(180 - P10 - Q) / S(P10), 1) for Q in s10]
ok([num(v("m13b1")), num(v("m13b2"))] == rs == [16.0, 11.0], "5I Q10b r (book 16.0, 11.0)", str(rs))
# Q11, Q12, Q13
fig("t3_q11", ["67 km", "63°", "39°", "A", "B", "C"])
AC = aas(67, 24, 117, label="5I Q11")
BC = 67 * S(39) / S(24)
ok(num(v("m14")) == round(67 + AC + BC) == 317, "5I Q11 total 317 km", f"{67 + AC + BC:.2f}")
ok(printed("inclined at 12° to the horizontal", "elevation of the top \\(T\\) of the flagpole from \\(A\\) is 34°", "\\(AB=20\\) m")[0], "5I Q12 text")
ok(34 - 12 == 22 and 90 + 12 == 102 and num(v("m15b")) == round(aas(20, 180 - 22 - 102, 22, label="5I Q12")) == 9, "5I Q12 height 9 m")
ok(num(v("m16a")) == 12 * (2 / 3) / (1 / 4) == 32, "5I Q13a b = 32")
ok(v("m16b") == r"\(\dfrac57\)" and sp.Rational(25) * sp.Rational(3, 5) / 21 == sp.Rational(5, 7), "5I Q13b sin P = 5/7")
# Q14, Q15 (area 48, 72)
for p, (name, labs, other, A, book) in {"a": ("t3_q14a", ["12 m", "x", "30°"], 12, 30, 16.0), "b": ("t3_q14b", ["9 m", "x", "70°"], 9, 70, 11.35),
                                        "c": ("t3_q14c", ["x", "36 m", "130°"], 36, 130, 3.48)}.items():
    fig(name, labs)
    x = 96 / (other * S(A))
    sas_side(other, x, A, f"5I Q14{p}")
    ok(abs(num(v(f"m17{p}")) - round(x, 2)) < 1e-9 and round(x, 2) == book, f"5I Q14{p} x = {x:.4f}", v(f"m17{p}"))
for p, (name, labs, a, b, book) in {"a": ("t3_q15a", ["16 cm", "18 cm", "θ"], 16, 18, [30, 150]),
                                     "b": ("t3_q15b", ["20 cm", "24 cm", "θ"], 20, 24, [17 + 27 / 60, 162 + 33 / 60]),
                                     "c": ("t3_q15c", ["12 cm", "10 cm", "θ"], 12, 10, [])}.items():
    fig(name, labs)
    th = area_to_angle(72, a, b)
    if book:
        ok(same_dm(angles_of(v(f"m18{p}")), th) and same_dm(th, book), f"5I Q15{p} {th}", v(f"m18{p}"))
    else:
        ok(th == [] and v(f"m18{p}") == "no solutions", "5I Q15c no solutions (sin = 1.2)")
# Q16, Q17
for p, (a, b, book) in zip("abcd", ((60, 45, "3*sqrt(6)"), (30, 45, "3*sqrt(2)"), (45, 60, "2*sqrt(6)"), (45, 30, "6*sqrt(2)"))):
    fig(f"t3_q16{p}", ["6", "x", f"{a}°", f"{b}°"])
    exact = sp.nsimplify(6 * sp.sin(sp.pi * a / 180) / sp.sin(sp.pi * b / 180))
    aas(6, b, a, label=f"5I Q16{p}")
    got = sp.sympify(re.sub(r"\\\((\d)\\sqrt(\d)\\\)", r"\1*sqrt(\2)", v(f"h20{p}")))
    ok(sp.simplify(got - exact) == 0 and sp.simplify(got - sp.sympify(book)) == 0, f"5I Q16{p} = {exact}", v(f"h20{p}"))
fig("t3_q17", ["35°"])
s17 = math.sqrt(70 / S(35))
sas_side(s17, s17, 35, "5I Q17")
ok(num(v("h21")) == round(s17, 1) == 11.0, "5I Q17 11.0 cm", f"{s17:.4f}")
# 5J Q14, Q15 (book PDF 549: 3 or 5)
fig("t3_j14", ["x", "8", "7", "60°"])
xs = sorted(float(r) for r in sp.solve(sp.Symbol("x") ** 2 + 64 - 8 * sp.Symbol("x") - 49, sp.Symbol("x")))
for x in xs:
    ok(abs(math.sqrt(x * x + 64 - 2 * x * 8 * C(60)) - 7) < 1e-9, f"5J Q14 x = {x} gives side 7")
ok([float(t) for t in re.findall(r"\d+", v("h22"))] == xs == [3.0, 5.0], "5J Q14 x = 3 or 5")
fig("t3_j15", ["A", "B", "C", "6 cm", "4 cm", "x cm", "30°"])
for x in (3 * math.sqrt(3) + math.sqrt(7), 3 * math.sqrt(3) - math.sqrt(7)):
    ok(abs(x * x - 6 * math.sqrt(3) * x + 20) < 1e-9 and abs(math.sqrt(x * x + 36 - 12 * x * C(30)) - 4) < 1e-9, f"5J Q15 x = {x:.4f} gives BC = 4")

# ------------------------------------------------------------------ past papers
fig("pp3_nb22_5", ["30 m", "20 m", "17.8 m", "35°"])
ok(round(sas_side(30, 20, 35, "NBCS22 Q5"), 1) == 17.8, "NBCS 2022 Q5: third side 17.8 consistent")
ok(v("e5") == "C" and round(0.5 * 600 * S(35)) == 172 and printed("(C)&ensp;172 m²")[0], "NBCS 2022 Q5: C = 172")
fig("pp3_sb20_20", ["8 cm", "b cm", "61°", "42°"])
b20 = aas(8, 42, 61, label="SBHS20 Q20")
ok(num(v("e6a")) == float(f"{b20:.2g}") == 10, "SBHS 2020 Q20a b = 10 (2 s.f.)")
ok(num(v("e6b")) == float(f"{0.5 * 8 * b20 * S(77):.2g}") == 41, "SBHS 2020 Q20b area 41 (school 41)")
ok(printed(r"sides \(c=24\), \(b=31\) and angle \(ABC=60^\circ\)")[0], "NSB 2022 Q10 text")
s18 = ass(60, 31, 24, "NSB22 Q10")
ok(same_dm(angles_of(v("m19")), s18) and dm(s18[0]) == (42, 6), "NSB 2022 Q10b 42 6' only (school)")
fig("pp3_sb22_d4", ["A", "B", "C", "D", "6.4 cm", "7.9 cm", "6 cm", "130°"])
s23 = ass(180 - 130, 6.4, 7.9, "SBHS22 D4")
ok(len(s23) == 2 and angles_of(v("h24")) == [round(min(s23))] == [71], "SBHS 2022 D Q4 acute ADC = 71 (school; both triangles exist)", str(s23))
fig("pp3_g22_25b", ["θ", "74°24′", "515.5", "416.6"])
s24 = ass(74.4, 515.5, 416.6, "Girraween22 Q25b")
ok(len(s24) == 1 and same_dm(angles_of(v("e7")), s24) and dm(s24[0]) == (51, 7), "Girraween 2022 Q25(b) 51 7' (school)")
fig("pp3_fs22_6b", ["46°", "11.7", "8.9", "θ"])
sH25 = ass(46, 8.9, 11.7, "FortSt22 Q6b")
ok(printed(r"find all possible values of angle \(\theta\) (to the nearest degree)?")[0] and same_deg(angles_of(v("h25")), sH25)
   and [round(x) for x in sH25] == [71, 109], "Hard Q25 Fort St 2022 Q6(b): 71 or 109, both valid (school)", str(sH25))
fig("pp3_g20_22c", ["N", "P", "Q", "R", "70°", "12 km", "30 km"])
RQ = sas_side(12, 30, 20, "Girraween20 Q22c")
ok(num(v("h26a")) == round(RQ) == 19, "Girraween 2020 Q22(c)(i) 19 km (school)", f"{RQ:.3f}")
Qang = ass(20, RQ, 12, "Girraween20 Q22c ii")
ok(len(Qang) == 1 and num(v("h26b")) == round(270 + Qang[0]) == 282, "Girraween 2020 Q22(c)(ii) 282 T (school)", f"{Qang}")
# mini exam
ok(printed(r"\(\angle D=42^\circ\), \(d=5\) cm and \(f=7\) cm")[0], "PP1 text")
sF = ass(42, 5, 7, "Hornsby Q9")
ok(r"\(F\doteqdot69.52^\circ\)" in ANS and r"110.48^\circ" in ANS and [round(x, 2) for x in sF] == [69.52, 110.48], "PP1 printed working 69.52, 110.48")
ok(len(sF) == 2 and v("pp1") == "C" and round(max(sF)) == 110 and printed("C.&ensp;110°")[0], "PP1 obtuse F = 110 = C (school)")
fig("pp3_sc23_19", ["21°23′", "12.8 cm", "5.9 cm", "θ"])
sP2 = ass(21 + 23 / 60, 5.9, 12.8, "Scots23 Q19")
ok(len(sP2) == 2 and same_dm(angles_of(v("pp2")), [max(sP2)]) and dm(max(sP2)) == (127, 43), "PP2 obtuse 127 43' (school)")
ok(printed(r"\(AB=5\) cm, \(AC=3\) cm, \(\angle B=25^\circ\), and \(\angle C\) is obtuse")[0], "PP3 text")
sP3 = ass(25, 3, 5, "SBHS21 D b(i)")
ok(len(sP3) == 2 and angles_of(v("pp3")) == [round(max(sP3))] == [135], "PP3 obtuse C = 135 (school)")
fig("pp3_bh20_14", ["6", "10", "35°", "θ"])
sP4 = ass(35, 6, 10, "BH20 Q14")
ok(same_deg(angles_of(v("pp4")), sP4) and [round(x) for x in sP4] == [73, 107], "PP4 73 or 107 (school)")
fig("pp3_g20_22b", ["8 cm", "x cm", "y cm", "60°"])
xP5 = 2 * 22 * math.sqrt(3) / (8 * S(60))
ok(abs(xP5 - 11) < 1e-9 and v("pp5a") == r"\(x=11\)", "PP5(i) x = 11 (school)")
ok(abs(sas_side(8, 11, 60, "Girraween20 Q22b") ** 2 - 97) < 1e-9 and v("pp5b") == r"\(y=\sqrt{97}\)", "PP5(ii) y = sqrt97 (school)")
fig("pp3_sb24_b4", ["A", "B", "C", "D", "E", "18 cm", "6 cm", "8 cm"])
ok(printed(r"\(AB=18\) cm, \(BD=6\) cm, \(BC=8\) cm, and the area of triangle \(ADE=160\) cm²")[0], "PP6 text")
AE = 2 * 160 / ((18 + 6) * (8 / 18))
ok(abs(AE - 30) < 1e-9 and v("pp6") == r"\(AE=30.00\)", "PP6 AE = 30.00 (school 30)")
ok(printed("150 km away on a bearing of 050°T", "80 km from \\(B\\) and on a bearing of 080°T from \\(A\\)", "\\(A\\) is further from \\(C\\) than from \\(B\\)")[0], "PP7 text")
fig("pp3_nsg23_20", ["A", "B", "C", "150 km", "80 km", "050°T", "080°T"])
sC = ass(80 - 50, 80, 150, "NSG23 Q20a")
valid = []
for c in sC:
    Bang = 180 - 30 - c
    ACd = 80 * S(Bang) / S(30)
    if ACd > 150:
        valid.append(Bang)
ok(len(sC) == 2 and len(valid) == 1 and same_dm(angles_of(v("pp7")), [180 - valid[0]]) and dm(180 - valid[0]) == (99, 38), "PP7 turn 99 38' (school)", str(valid))
marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', LES.split("Past-paper homework:mini exam")[1].split("Chapter review")[0])]
ok(sum(marks) == 21 and "<b>21 marks</b>" in LES and "Suggested time: 30 minutes" in LES and 5 * round(1.5 * 21 / 5) == 30, "mini exam 21 marks, 30 minutes", str(marks))
# chapter review
ok(printed(r"the line \(y=-x\) makes")[0] and angles_of(v("r1")) == [math.degrees(math.atan(-1)) % 180] == [135], "R1 135")
ok(printed(r"\(\cos45^\circ+\tan120^\circ\)")[0] and v("r2") == r"\(\dfrac{1}{\sqrt2}-\sqrt3\)" and abs(C(45) + math.tan(math.radians(120)) - (1 / math.sqrt(2) - math.sqrt(3))) < 1e-12, "R2 1/sqrt2 - sqrt3")
sol3 = [x for x in range(0, 361) if abs(math.tan(math.radians(x)) + 1) < 1e-9]
ok(printed(r"\(\tan\theta=-1\)")[0] and angles_of(v("r3")) == sol3 == [135, 315], "R3 135, 315 (brute force)")
sol4 = [x for x in range(0, 361) if abs(C(x) + C(225)) < 1e-9]
ok(printed(r"\(\cos x=-\cos225^\circ\)")[0] and angles_of(v("r4")) == sol4 == [45, 315], "R4 45, 315 (brute force)")
fig("pp3_fs21_6", ["20°", "25cm", "10cm", "θ"])
sR5 = ass(20, 10, 25, "FortSt21 Q6")
ok(printed(r"Find the value(s) of angle \(\theta\) to the nearest degree.")[0] and same_deg(angles_of(v("r5")), sR5)
   and [round(x) for x in sR5] == [59, 121], "R5 Fort St 2021 Q6: 59 or 121, both valid (school)", str(sR5))
fig("pp3_sgs20_3b", ["A", "B", "C", "5 cm", "6 cm", "60°"])
ok(abs(sas_side(5, 6, 60, "SGS20 Q3b") ** 2 - 31) < 1e-9 and v("r6a") == r"\(AB=\sqrt{31}\)", "R6(i) sqrt31 (school)")
ok(v("r6b") == r"\(\dfrac{15\sqrt3}{2}\)" and abs(0.5 * 30 * S(60) - 15 * math.sqrt(3) / 2) < 1e-12, "R6(ii) 15 sqrt3 / 2 (school)")

print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
