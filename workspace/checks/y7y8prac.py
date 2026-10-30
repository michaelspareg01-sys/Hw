"""Check of the Year 7-8 Angles and Measurement practice pack (workspace/build/y7y8prac).

What it checks (exit status 1 if anything fails):
  1. Every answer printed in a_a.html, a_b.html, a_c.html is read from its <span data-k="KEY"> (each key must
     occur exactly once; a missing or unexpected key is a FAIL) and compared with an INDEPENDENT computation
     made here from the question data: angle sums, rays at a point modelled by their directions,
     parallel-line facts modelled with direction angles, clock angles, unit conversions with exact
     fractions, perimeters and areas by the shoelace formula on vertex lists, enumeration of angle names,
     brute-force searches for the unknowns in angle equations, sympy for algebraic answers.
  2. Every labelled angle in every figure (figs.py records the size each arc is DRAWN at) is compared
     with its label: a number label must equal the drawn size; a letter label (α, a°, (5x)° ...) is
     evaluated with the PRINTED answers and must equal the drawn size. The figures are built from the
     question data, so this is a second, geometric check of the answers (and of figure fidelity).
  3. The question data printed in q_a.html, q_b.html, q_c.html (values, units) appear as expected.
  4. The cover: the minutes add up, and the core list for each section matches the stars in the questions.
  5. Each answer is compared with the textbook answer key; a known key slip is reported, not failed.

Run: python3 workspace/checks/y7y8prac.py
"""
import itertools
import math
import os
import re
import sys
from fractions import Fraction as F

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y7Y8_SRC", os.path.join(HERE, "..", "build", "y7y8prac"))
FAILS, NOTES = [], []
N = [0]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def report(ok, label, detail=""):
    N[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label + ("  " + detail if detail else ""))
    if not ok:
        FAILS.append(label)


# ------------------------------------------------------------------ reading printed answers
ANS_HTML = "".join(read(f) for f in ("a_a.html", "a_b.html", "a_c.html"))
PRINTED = {}
for m in re.finditer(r'<span data-k="([^"]+)">(.*?)</span>', ANS_HTML, flags=re.S):
    k = m.group(1)
    if k in PRINTED:
        FAILS.append("duplicate key " + k)
        print("MISMATCH duplicate key", k)
    PRINTED[k] = m.group(2)


def clean(t):
    t = re.sub(r"<sup>2</sup>", "^2", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("\\(", "").replace("\\)", "")
    t = re.sub(r"\\tfrac\{(\d+)\}\{(\d+)\}", r" \1/\2", t)
    t = t.replace("\\,", "").replace("^\\circ", "°").replace("\\$", "$")
    t = t.replace("\\angle ", "∠").replace("\\angle", "∠").replace("\\parallel", "∥").replace("\\perp", "⊥")
    t = t.replace("\\triangle", "△")
    return t.strip()


def num(t):
    """Printed number (possibly with thin-space groups, a mixed number, a unit) -> (Fraction, unit)."""
    t = clean(t)
    mm = re.match(r"^(\d+)\s+(\d+)/(\d+)\s*(.*)$", t)           # mixed number, e.g. 16 4/11
    if mm:
        return int(mm.group(1)) + F(int(mm.group(2)), int(mm.group(3))), mm.group(4).strip()
    m = re.match(r"^\$?\s*([\d ]+(?:\.[\d ]+)?)(?:\s+(\d+)/(\d+))?\s*(.*)$", t)
    if not m:
        return None, t
    whole = F(m.group(1).replace(" ", ""))
    if m.group(2):
        whole += F(int(m.group(2)), int(m.group(3)))
    unit = m.group(4).strip()
    if t.startswith("$"):
        unit = "$"
    return whole, unit


def names(t):
    """Set of angle / line names in a printed list, each normalised (∠ABC == ∠CBA)."""
    t = clean(t)
    out = set()
    for a in re.findall(r"∠\s*([A-Z])([A-Z])([A-Z])", t):
        out.add("∠" + a[1] + "".join(sorted((a[0], a[2]))))
    return out


SYM = {s: sp.Symbol(s) for s in ("a", "b", "x", "y", "d", "α", "β", "γ", "θ")}


def expr(t):
    t = clean(t)
    t = re.sub(r"^[A-Za-z∠]*\s*=", "", t) if "=" in t else t
    t = t.replace("°", "").replace("−", "-").replace("^", "**").replace("\\alpha", "α").replace("\\beta", "β")
    t = t.replace("\\gamma", "γ").replace("\\theta", "θ")
    t = re.sub(r"(\d)([a-zαβγθ(])", r"\1*\2", t)
    t = re.sub(r"([a-zαβγθ)])([a-zαβγθ(])", r"\1*\2", t)
    t = re.sub(r"([a-zαβγθ)])([a-zαβγθ(])", r"\1*\2", t)
    return sp.sympify(t, locals=SYM)


EXPECT = {}          # key -> (kind, value[, unit])


def want_num(key, value, unit=""):
    EXPECT[key] = ("num", F(value), unit)


def want_str(key, value):
    EXPECT[key] = ("str", value)


def want_set(key, value):
    EXPECT[key] = ("set", value)


def want_expr(key, value):
    EXPECT[key] = ("expr", value)


# ------------------------------------------------------------------ geometry helpers (independent)
def norm(a):
    return a % 360


def between(u, v):
    """Size of the non-reflex angle between rays at directions u and v (degrees)."""
    d = abs(norm(u) - norm(v)) % 360
    return min(d, 360 - d)


def solve_int(f, lo=-400, hi=400, step=F(1, 2)):
    """Brute-force search for the value t (half-degree steps) with f(t) == 0; must be unique."""
    sols = []
    t = F(lo)
    while t <= hi:
        if f(t) == 0:
            sols.append(t)
        t += step
    assert len(sols) == 1, sols
    return sols[0]


def shoelace(pts):
    s = 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        s += F(x1) * F(y2) - F(x2) * F(y1)
    return abs(s) / 2


def perim(pts):
    return sum(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))


def angle_names(edges):
    """All angles formed at the vertices by pairs of edges meeting there (brute force)."""
    out = set()
    verts = set("".join(edges))
    for v in verts:
        ends = sorted({e.replace(v, "") for e in edges if v in e})
        for p, q in itertools.combinations(ends, 2):
            out.add("∠" + v + "".join(sorted((p, q))))
    return out


# ================================================================== A1 notation
want_str("A1.1a", "AB∥DC"); want_str("A1.1b", "BC∥AD"); want_str("A1.1c", "B"); want_str("A1.1d", "C")
want_str("A1.1e", "No")
want_str("A1.2a", "AX,BX,CX,YX"); want_str("A1.2b", "AC∥XY"); want_str("A1.2c", "B"); want_str("A1.2d", "CX")
want_str("A1.2e", "A,B,C"); want_str("A1.2f", "None")
want_str("A1.3a", "concurrent"); want_str("A1.3b", "yes"); want_str("A1.3c", "no")
want_str("A1.3d", "rayPAandrayPK"); want_str("A1.3e", "rayAP,rayAB,rayAOandrayAK")
want_set("A1.4a", angle_names(["AB", "BC", "CD", "DA", "BD"]))                      # quadrilateral + diagonal BD
want_set("A1.4b", angle_names(["AB", "AC", "AD", "BC", "CD", "BD"]))               # tetrahedron
assert len(EXPECT["A1.4a"][1]) == 8 and len(EXPECT["A1.4b"][1]) == 12

# Y8 6A Q5: rays from O.  D is opposite A, E is opposite B, and the right angle is between OC and OD.
RAY = {"A": 32, "B": 68, "D": 212, "E": 248}
RAY["C"] = RAY["D"] - 90
ANG = {}
for p, q in itertools.combinations(RAY, 2):
    ANG["∠O" + "".join(sorted(p + q))] = between(RAY[p], RAY[q])
AOB, BOC, AOE, AOC = ANG["∠OAB"], ANG["∠OBC"], ANG["∠OAE"], ANG["∠OAC"]
vo = {k for k in ANG if set(k[2:]) == {"D", "E"}}                 # opposite rays of OA and OB
comp = {k for k, v in ANG.items() if v + BOC == 90}
supp_AOE = {k for k, v in ANG.items() if v + AOE == 180}
supp_AOC = {k for k, v in ANG.items() if v + AOC == 180 and k != "∠OAC"}
EXPECT["A1.5ai"] = ("subset", vo)
EXPECT["A1.5aii"] = ("subset", comp)
EXPECT["A1.5aiii"] = ("subset", supp_AOE)
EXPECT["A1.5aiv"] = ("subset", supp_AOC)
assert between(RAY["A"], RAY["C"]) == 90                     # AD (the line through A and D) is perpendicular to OC
want_str("A1.5bi", "AD⊥OC"); want_str("A1.5bii", "OC⊥OD")

# ================================================================== A2 measuring and classifying
for p, x in zip("abcde", (15, 35, 72, 88, 56)):
    want_num("A2.1" + p, 90 - x, "°")
for p, x in zip("abcde", (160, 100, 75, 88, 146)):
    want_num("A2.2" + p, 180 - x, "°")
for p, (u, v, refl) in zip("abcd", ((0, 32, False), (0, 128, False), (58, 105, True), (0, 90, False))):
    size = 360 - between(u, v) if refl else between(u, v)
    want_str("A2.3" + p, "acute" if size < 90 else "right" if size == 90 else "obtuse" if size < 180 else "reflex")


def clock(h, m=0):
    hour = (h % 12) * 30 + m * F(1, 2)
    minute = m * 6
    d = abs(hour - minute) % 360
    return min(d, 360 - d)


for p, h in zip("abcdefgh", (6, 3, 13, 14, 4, 20, 10, 7)):
    want_num("A2.4" + p, clock(h), "°")
for p, mins in zip("abcdefgh", (60, 30, 45, 5, 50, 25, 120, 90)):
    want_num("A2.5" + p, mins * 6, "°")
want_num("A2.6a", between(0, 90 - 32), "°"); want_num("A2.6b", 360 - between(0, 90 - 32), "°")

# ================================================================== A3 angles at a point
want_num("A3.1e", between(0, 180 - 30 - 100), "°")             # OA direction from OB after 30 and 100
ray = 0                                             # OJ along 0; then OK, OL, OM, ON, OA anticlockwise
for gap in (10, 20, 30, 40, 50):
    ray += gap
want_num("A3.1k", between(ray, 180), "°")           # OB along 180
ray = 0                                             # 6D Q5l: OD along 0, then round the point to OA
for gap in (70, 80):                                # D->C->B anticlockwise
    ray += gap
rayB = ray
ray = 0
for gap in (60, 50, 40, 30):                        # D->E->F->G->A clockwise
    ray -= gap
want_num("A3.1l", between(rayB, ray), "°")
# 6D Q7g: U up (90), D down, L at 90+130, R opposite L, T at 270+80.
U, L = 90, 90 + 130
R, T, D = L - 180, 270 + 80, 270
want_num("A3.2g_b", between(U, R), "°"); want_num("A3.2g_a", between(R, T), "°")
# 6D Q7h: at M: MB 180, MD 0, angle DMC = 70 below, so MC = -70 and MA = 110 (A, M, C collinear)
MA, MB, MD = 110, 180, 0
want_num("A3.2h_a", between(MA, MB), "°"); want_num("A3.2h_b", between(MA, MD), "°")
# at D: DM 180, DX 0, angle MDA = 40 above, angle CDX = 150 below, Y opposite C
DA, DC = 180 - 40, -150
DY = DC + 180
want_num("A3.2h_g", between(DY, 0), "°"); want_num("A3.2h_t", between(DA, DY), "°")
# 6D Q8c: angle DVB = 40, A opposite B, VM bisects angle AVC
VB = 180 + 40
VA = VB - 180
want_num("A3.3c", F(between(VA, 0), 2), "°")
# 6D Q8g: FM at 60, FN opposite, FP below with angle NFP = g and angle PFG = 3g
FM = 60
FN = FM + 180
want_num("A3.3g_t", between(180, FM), "°")
want_num("A3.3g_g", solve_int(lambda g: (FN + g) + 3 * g - 360), "°")
want_num("A3.3h", solve_int(lambda al: al + 50 + al - 180), "°")
for p, k in zip("abcd", (1, 2, 4, 10)):
    want_num("A3.4" + p, F(360 * k, k + 8), "°")
want_num("A3.5", solve_int(lambda a: (a + 50) + (a - 90) - 180))
want_num("A3.6e", solve_int(lambda a: a + a + 3 * a + 4 * a + 3 * a - 360))
want_num("A3.6f", solve_int(lambda a: (7 * a + 21) + (3 * a - 11) - 180))

# ================================================================== A4 transversals
# Y8 6B Q2: B on line FE, C on line HG (both vertical); transversal A-B-C-D.  Each ray: (kind, sign).
rays = {"B": {"A": ("t", -1), "C": ("t", 1), "F": ("l", 1), "E": ("l", -1)},
        "C": {"B": ("t", -1), "D": ("t", 1), "H": ("l", 1), "G": ("l", -1)}}


def pair_rel(v, p, q, rel):
    """Angle at v between rays p, q -> the angle related to it by rel."""
    other = "C" if v == "B" else "B"
    sig = {rays[v][p], rays[v][q]}
    t = next(s for k, s in sig if k == "t"); l = next(s for k, s in sig if k == "l")
    if rel == "corr":
        w, tt, ll = other, t, l
    elif rel == "alt":
        w, tt, ll = other, -t, -l
    elif rel == "coint":
        w, tt, ll = other, -t, l
    else:                                     # vertically opposite
        w, tt, ll = v, -t, -l
    rr = [n for n, s in rays[w].items() if s in {("t", tt), ("l", ll)}]
    # interior angles (alt, coint) must lie between the lines: the transversal ray at B points to C and vice versa
    return "∠" + w + "".join(sorted(rr))


for key, (v, p, q, rel) in {"a": ("B", "A", "F", "corr"), "b": ("C", "B", "G", "corr"),
                            "c": ("B", "F", "C", "alt"), "d": ("B", "C", "E", "alt"),
                            "e": ("C", "H", "B", "coint"), "f": ("B", "E", "C", "coint"),
                            "g": ("B", "A", "E", "vo"), "h": ("C", "H", "B", "vo")}.items():
    want_set("A4.1" + key, {pair_rel(v, p, q, rel)})
# 6E Q7d: TU and RS at 10 degrees, angle STU = 42 so TS at 52; alpha is the angle at S between SR and ST
want_num("A4.2d", between(10 + 180, 52 + 180), "°")
# 6E Q7g: DE and GF horizontal, DG and EF parallel; angle GDE = 116 so DG points at 360-116
DG = -116
want_num("A4.2g", between(180, DG), "°")                 # at E: E->D (180) and E->F (same direction as D->G)
# 6E Q7k: B-O-A horizontal, BD at -69, CA parallel to BD (pointing from C to A)
want_num("A4.2k", between(180, -69 + 180), "°")           # at A: AO (180) and AC (opposite of C->A)
# 6E Q8f: A at origin, AB along 0, angle CAB 71, angle ACB 50, BX parallel to AC
BC = 180 - (180 - 71 - 50)
want_num("A4.3f_a", between(0, 71), "°"); want_num("A4.3f_b", between(BC, 71), "°")
# 6E Q8h: CB and LM horizontal; angle BCA 43, angle CBA 76
CA = -43
BA = 180 + 76
want_num("A4.3h_g", between(180, CA + 180), "°"); want_num("A4.3h_t", between(0, BA + 180), "°")
# Y8 6B Q7b: top line at 15, angle 40 at the top vertex; reflex angle at the lower vertex
V1V2 = 195 + 40
want_num("A4.4b", 360 - between(V1V2 + 180, 15))
# Y8 6B Q7e: PQ at 25, R->S at 25; angle at R between RS and RQ is 31; a is the angle PQR
RQ = 25 + 31                            # at R: R->S along 25, R->Q at 25 + 31
want_num("A4.4e", between(205, RQ + 180))   # at Q: Q->P (205) and Q->R
# Y8 6B Q7i: left side (B->L) parallel to the ray at T (T->Z reversed); angles 82 at L, 65 at T
BL_dir = 120                            # B->L
LT = (BL_dir + 180) + 82                # L->B is 300; L->T is 300 + 82
TZ = BL_dir + 180                       # ray at T points the same way as L->B
TB = TZ - 65
want_num("A4.4i", between(LT + 180, TB))
a_, b_ = sp.symbols("a b")
want_expr("A4.5a", 180 - a_); want_expr("A4.5b", 360 - a_); want_expr("A4.5c", 180 - a_ - b_)

# ================================================================== A5 further problems, proving parallel
want_str("A5.1a", "AB∥CZ"); want_str("A5.1c", "HJ∥KM"); want_str("A5.1f", "DE∥GF")
# 6F Q1c: angle ABM 70, MBD 40, alpha = DBC; theta = angle BDE with DE parallel to AC
BD = 180 + 70 + 40
want_num("A5.2c_a", between(BD, 0), "°"); want_num("A5.2c_t", between(BD + 180, 0), "°")
# 6F Q1e: AB at 16, JK parallel; angle CAB 70, CBA 30
AC = 16 + 70
BCdir = 196 - 30
want_num("A5.2e_a", between(196, AC + 180), "°"); want_num("A5.2e_b", between(BCdir + 180, 16), "°")
want_num("A5.2e_g", between(AC + 180, BCdir + 180), "°")
# 6F Q1h: PQ, AB, RS horizontal; PS vertical; angle SRO = 60 so RQ at 60
OR = 60 + 180                                      # R->O at 60 (angle SRO), so O->R at 240
want_num("A5.2h_a", between(90, 180), "°"); want_num("A5.2h_b", between(180, OR), "°")
want_num("A5.2h_g", between(OR, 270), "°")
# 6F Q2b: FG at 25 above QR side... angle GQ(right) 25, (right)QR 18; PO parallel to FG
QF, QR = 25 + 180, -18                         # angle FQR at Q (straight line through Q)
OP, OQ = 25 + 180, -18                         # at O: OP parallel to QF, OQ along QR (O, Q, R collinear)
assert between(QF, QR) == between(OP, OQ)
want_num("A5.3b", between(OP, OQ), "°")
# 6F Q2d: X->P and Z->Q and O->Y horizontal; angle XPO 160 (PO at -20), angle ZQO 150 (QO at 30)
want_num("A5.3d", between(-20 + 180, 30 + 180), "°")
want_num("A5.4d", solve_int(lambda g: g + 10 + 130 - 180), "°")
want_num("A5.4h_g", solve_int(lambda g: g + g - 180), "°")
want_num("A5.4h_t", solve_int(lambda t: t + 40 + t - 180), "°")
# 6G Q2b: CD at 20, CO at 70, angle CDO 35; B on OD with AB parallel to CD
want_num("A5.5b", between(20 + 180, 200 - 35), "°")
# 6G Q2d: AB and CD horizontal; angle ABC 30 -> CB at 30; gamma is angle BCD
want_num("A5.5d", between(30, 0), "°")

# ================================================================== A6 triangles
for k, v in zip("abcdefgh", ("right-angled triangle", "isosceles triangle", "acute-angled triangle",
                             "equilateral triangle", "obtuse-angled triangle", "equilateral triangle",
                             "isosceles triangle", "scalene triangle")):
    want_str("A6.1" + k, v)
want_num("A6.2d", solve_int(lambda a: a + 60 + (180 - 110) - 180))
want_num("A6.2e", 180 - F(180 - 100, 2))
want_num("A6.2f", 180 - 60 - (180 - 115))
want_num("A6.3a", 180 - 70 - 55); want_num("A6.3b", 180 - 35 - 85); want_num("A6.3c", 180 - 74 - 81)
want_num("A6.4c", 180 - 90 - 72); want_num("A6.4e", F(180 - 49, 2)); want_num("A6.4f", 180 - 90 - (180 - 150))
want_str("A6.5a", "Isosceles"); want_set("A6.5b", {"∠ABO", "∠BAO"})
want_num("A6.5c", 30, "°"); want_num("A6.5d", 180 - 2 * 36, "°"); want_num("A6.5e", F(180 - 100, 2), "°")

# ================================================================== A7 quadrilaterals
BtR, BtL = 40, 40 + 76                                # 6D Q3a: parallelogram, 76 at the bottom vertex
want_num("A7.1a_a", between(BtR + 180, BtL))   # at R: R->Bt and R->T (parallel to Bt->L)
want_num("A7.1a_b", between(BtL + 180, BtR + 180))     # at T: T->R is opposite Bt->L, T->L is opposite Bt->R
want_num("A7.1c", 180 - 52)
want_num("A7.2b_a", 2); want_num("A7.2b_b", 90); want_num("A7.2c_a", 5); want_num("A7.2c_b", 70)
want_num("A7.3a", 360 - (360 - 40 - 85 - 27))
want_num("A7.3c", 360 - (360 - (180 - 74) - 17 - 22))
want_num("A7.3d", 180 - 106)
want_num("A7.3e", F(180 - 2 * 31, 2))
want_num("A7.4a", solve_int(lambda x: 5 * x - 95)); want_num("A7.4b", solve_int(lambda x: 95 + 2 * x + x + 85 - 360))
want_num("A7.4c", solve_int(lambda x: 4 * x + 3 * x + 2 * x + x - 360))
# Y8 6D Q9: each quadrilateral as a set of properties; "X is a type of Y" iff X has all of Y's properties
PROPS = {"square": {"4 right angles", "4 equal sides", "2 pairs parallel"},
         "rectangle": {"4 right angles", "2 pairs parallel"},
         "rhombus": {"4 equal sides", "2 pairs parallel"},
         "parallelogram": {"2 pairs parallel"}}
for k, (x, y) in zip("abcdef", (("square", "rectangle"), ("rectangle", "square"), ("square", "rhombus"),
                                 ("rectangle", "parallelogram"), ("parallelogram", "square"),
                                 ("rhombus", "parallelogram"))):
    want_str("A7.5" + k, "true" if PROPS[y] <= PROPS[x] else "false")
want_str("A7.6", "No")

# ================================================================== B1 units
MM = {"mm": F(1), "cm": F(10), "m": F(1000), "km": F(1000000), "µm": F(1, 1000)}
for k, (v, u, to) in {"e": (27, "mm", "cm"), "h": (F(19, 10), "m", "cm"), "k": (F(634, 100), "km", "m"),
                      "l": (200000, "mm", "km"), "n": (2901, "m", "km"), "s": (F(5, 8), "cm", "mm")}.items():
    want_num("B1.1" + k, F(v) * MM[u] / MM[to], to)
want_num("B1.2", 1000 // 20 + 1)
want_num("B1.3", (5 * 100 - 60) / F(2), "cm")
want_num("B1.4", F(51, 10) * MM["km"] / MM["µm"], "µm")
want_num("B1.5", F(36525 * 24 * 60, 10 ** 6), "min")
want_num("B1.6", F(1760 * 3 * 12) * F(254, 100) / 100 / 1000, "km")

# ================================================================== B2 perimeter
want_num("B2.1d", 18 + 7 + 12 + 15); want_num("B2.1e", 17 + 17 + 16); want_num("B2.1f", 2 * (17 + 23))
want_num("B2.2a", 2 * (F(23, 10) + F(36, 10)), "m"); want_num("B2.2b", 2 * (F(98, 10) + F(64, 10)), "m")
aa, bb, xx, yy = sp.symbols("a b x y")
want_expr("B2.3d", 4 * bb + aa + 2 * bb + 3 * aa); want_expr("B2.3e", 4 * aa + 4 * aa + 3 * bb)
want_expr("B2.3f", 2 * 7 * xx + 2 * 6 * yy)
stair = [(0, 0), (0, 10), (2, 10), (2, F(72, 10)), (F(58, 10), F(72, 10)), (F(58, 10), F(22, 10)), (F(73, 10), F(22, 10)),
         (F(73, 10), F(11, 10)), (10, F(11, 10)), (10, 0)]
want_num("B2.4", F(round(perim(stair) * 1000), 1000), "m")
want_num("B2.5", F(516, 10) * 2 + F(1685, 100), "m")
want_num("B2.6", 5 * F(13, 10) * MM["mm"] / MM["m"], "m")

# ================================================================== B3 area
want_num("B3.1a", 5 * F(85, 100), "m^2"); want_num("B3.1b", F(800, 1000) * 2, "km^2")
want_num("B3.2a", 7 * 6, "cm^2"); want_num("B3.2b", F(27, 9), "cm"); want_num("B3.2c", F(85, 17), "m")
want_num("B3.2d", F(144, 12), "km")
tiles = (8 * F(54, 10) + F(27, 10) * F(89, 10) + 3 * F(133, 10)) * 100 * 100
want_num("B3.3", tiles * F(450, 100), "$")
want_num("B3.4d", shoelace([(0, 0), (0, 9), (6, 9), (6, 6), (7, 6), (7, 0)]), "m^2")
want_num("B3.4f", shoelace([(0, 0), (0, 6), (6, 6), (6, 3), (7, 3), (7, 1), (8, 1), (8, 0)]), "cm^2")
want_num("B3.4h", shoelace([(0, 0), (0, 6), (8, 6), (8, 4), (2, 4), (2, 2), (6, 2), (6, 0)]), "m^2")
# 9F Q5: count unit cells covered by the four 5 m by 1 m rectangles (positions as in the figure)
cells = set()
for (x, y, w, h) in ((1, 0, 1, 5), (4, -1, 1, 5), (0, 3, 5, 1), (1, 1, 5, 1)):
    for i in range(w):
        for j in range(h):
            cells.add((x + i, y + j))
want_num("B3.5", len(cells), "m^2")

# ================================================================== B4 triangles and parallelograms
want_num("B4.1c", F(13 * 4, 2), "cm^2"); want_num("B4.1d", F(14 * 12, 2), "mm^2")
want_num("B4.2b", shoelace([(0, 0), (8, 0), (8, 3), (5, 6), (0, 3)]), "km^2")
want_num("B4.2c", shoelace([(0, 0), (11, 0), (11, 12), (5, 12)]), "cm^2")
want_num("B4.2d", shoelace([(-8, 0), (0, 0), (6, -5), (0, -15)]), "mm^2")
want_num("B4.3a", 17 * 17 - shoelace([(12, 17), (17, 5), (5, 0), (0, 12)]), "m^2")
want_num("B4.3d", 13 * 11 - shoelace([(3, 3), (10, 3), (F(13, 2), 8)]), "m^2")
want_num("B4.4a", 8 * 13, "cm^2"); want_num("B4.4b", 14 * 12, "m^2")
h = next(h for h in range(1, 20) if 2 * h * h == 18)
want_num("B4.5h", h, "cm"); want_num("B4.5b", 2 * h, "cm")
want_num("B4.6", shoelace([(0, 0), (2, 4), (8, 4), (6, 0)]), "cm^2")

# ================================================================== B5 special quadrilaterals
want_num("B5.1d", F(5 * 3, 2), "cm^2"); want_num("B5.1h", F(20 * 30, 2), "mm^2")
want_num("B5.1k", F(5 * (9 + 4), 2), "m^2"); want_num("B5.1l", F(16 * (20 + 50), 2), "mm^2")
want_num("B5.2b", F(5 * (4 + 10), 2), "m^2"); want_num("B5.2c", F(13 * (3 + 10), 2), "cm^2")
kite = [(0, F(3, 10)), (F(3, 10), 0), (0, F(-6, 10)), (F(-3, 10), 0)]
want_num("B5.3", shoelace(kite), "m^2")
want_num("B5.4", F(8, 2) * F(145, 10) * 20, "$")
xs = next(x for x in range(1, 20) if F(2, 2) * (x + 3 * x) == 12)
want_num("B5.5a", xs, "cm"); want_num("B5.5b", 3 * xs, "cm")
want_expr("B5.6a", 2 * xx * xx); want_expr("B5.6b", F(1, 2) * (2 * aa) * (3 * bb)); want_expr("B5.6c", F(1, 2) * 2 * aa * (3 * aa + 5 * aa))
want_str("B5.7", "No")

# ================================================================== C mixed challenge
# Review Q7b: left side and right ray parallel (direction 55); right angle at the top
TA = 55 + 180; TC = TA + 90                   # right angle at the top vertex T
want_num("C.1b", between(TC + 180, 180), "°")  # at C: C->T and C->A
# Review Q7d: V->T makes 180-123 above the dashed line, V->B makes 180-150 below; alpha is outside
want_num("C.1d", between(180 - 123, 180 - (180 - 150)), "°")


def zig_last(first, corners):
    """Walk a path: start direction `first`; at each corner (angle, turn) the path turns left (+1) or right (-1)
    by 180 - angle.  Returns the final direction."""
    d = first
    for angle, turn in corners:
        d += turn * (180 - angle)
    return norm(d)


# Challenge Q1: first arrowed segment at -60; corners: 90 (left), 110 (right), 115 (left), alpha (right)
want_num("C.2", solve_int(lambda al: norm(zig_last(-60, [(90, 1), (110, -1), (115, 1), (al, -1)]) - norm(-60)), 0, 180), "°")
# Challenge Q2a: top line points right (0); at its end the path turns back by 20 (corner 20), etc.
want_num("C.3a", solve_int(lambda al: norm(zig_last(0, [(20, -1), (al, 1), (50, -1), (30, 1)])) - 0, 0, 180), "°")
g_, be_, al_, x_ = sp.symbols("γ β α x")
xsol = sp.solve(sp.Eq((0 - (180 - g_) + (180 - x_) - (180 - be_) + (180 - al_)), 0), x_)[0]
want_expr("C.3b", xsol)
want_num("C.4", solve_int(lambda t: 6 * t - t / 2 - 90, 0, 60, F(1, 11)), "minutes")
p8a = [(0, 11), (6, 11), (6, 12), (9, 12), (9, 9), (8, 9), (8, 5), (6, 5), (6, 0), (3, 0), (3, 5), (0, 5)]
want_num("C.5a_p", F(round(perim(p8a))), "m"); want_num("C.5a_a", shoelace(p8a), "m^2")
p8b = [(0, 18), (6, 10), (0, 10), (0, 6), (6, 6), (-2, 0), (-2, 6), (-8, 6), (0, 12)]
want_num("C.5b_p", F(round(perim(p8b))), "km"); want_num("C.5b_a", shoelace(p8b), "km^2")
assert all(abs(math.hypot(*d) - 10) < 1e-9 for d in ((6, 8), (8, 6)))       # the 10 km sides fit
want_num("C.6a", F(3 * 4, 2), "cm^2"); want_num("C.6b", F(2 * 6, 5), "cm")
grass = [(0, 0), (0, 9), (8, 9), (8, 6), (12, 6), (12, 9), (16, 9), (16, 0), (12, 0), (12, 3), (8, 3), (8, 0)]
outer = [(-1, -1), (-1, 10), (9, 10), (9, 7), (11, 7), (11, 10), (17, 10), (17, -1), (11, -1), (11, 2), (9, 2), (9, -1)]
want_num("C.7a", shoelace(grass), "m^2"); want_num("C.7p", F(round(perim(grass))), "m")
want_num("C.7c", shoelace(outer) - shoelace(grass), "m^2")

# ------------------------------------------------------------------ compare printed with expected
UNITS_OK = {"°", "", "m", "cm", "mm", "km", "µm", "min", "minutes", "$", "m^2", "cm^2", "mm^2", "km^2"}
for key, spec in EXPECT.items():
    if key not in PRINTED:
        report(False, key, "MISSING from the answers HTML")
        continue
    raw = PRINTED[key]
    kind = spec[0]
    if kind == "num":
        v, u = num(raw)
        ok = v is not None and v == spec[1] and u == spec[2]
        report(ok, key, f"printed {clean(raw)!r}; computed {spec[1]} {spec[2]}")
    elif kind == "str":
        t = re.sub(r"\s+", "", clean(raw)).replace(",and", ",").lower()
        w = re.sub(r"\s+", "", spec[1]).replace(",and", ",").lower()
        report(t == w, key, f"printed {clean(raw)!r}; expected {spec[1]!r}")
    elif kind in ("set", "subset"):
        got = names(raw)
        ok = (got == spec[1]) if kind == "set" else (bool(got) and got <= spec[1])
        report(ok, key, f"printed {sorted(got)}; computed {sorted(spec[1])}")
    elif kind == "expr":
        e = expr(raw)
        report(sp.simplify(e - spec[1]) == 0, key, f"printed {e}; computed {sp.expand(spec[1])}")
for key in PRINTED:
    if key not in EXPECT:
        report(False, key, "printed but not checked (unexpected key)")

# ------------------------------------------------------------------ figures: drawn angles against labels
sys.path.insert(0, SRC)
import figs  # noqa: E402

NOT_TO_SCALE = {"a3_y13"}                     # Y8 Ex 6A Q13 says 'not drawn to scale' and asks what is wrong
LETTERS = {   # figure -> {symbol: answer key}
    "a3_7g": {"α": "A3.2g_a", "β": "A3.2g_b"}, "a3_7h": {"α": "A3.2h_a", "β": "A3.2h_b", "γ": "A3.2h_g", "θ": "A3.2h_t"},
    "a3_8c": {"θ": "A3.3c"}, "a3_8g": {"θ": "A3.3g_t", "γ": "A3.3g_g"}, "a3_8h": {"α": "A3.3h"},
    "a3_y14e": {"a": "A3.6e"}, "a3_y14f": {"a": "A3.6f"},
    "a4_7d": {"α": "A4.2d"}, "a4_7g": {"θ": "A4.2g"}, "a4_7k": {"β": "A4.2k"},
    "a4_8f": {"α": "A4.3f_a", "β": "A4.3f_b"}, "a4_8h": {"γ": "A4.3h_g", "θ": "A4.3h_t"},
    "a4_y7b": {"a": "A4.4b"}, "a4_y7e": {"a": "A4.4e"}, "a4_y7i": {"a": "A4.4i"},
    "a5_f1c": {"α": "A5.2c_a", "θ": "A5.2c_t"}, "a5_f1e": {"α": "A5.2e_a", "β": "A5.2e_b", "γ": "A5.2e_g"},
    "a5_f1h": {"α": "A5.2h_a", "β": "A5.2h_b", "γ": "A5.2h_g"}, "a5_f4d": {"γ": "A5.4d"},
    "a5_f4h": {"γ": "A5.4h_g", "θ": "A5.4h_t"}, "a5_g2b": {"β": "A5.5b"}, "a5_g2d": {"γ": "A5.5d"},
    "a6_7d": {"a": "A6.2d"}, "a6_7e": {"a": "A6.2e"}, "a6_7f": {"a": "A6.2f"}, "a6_9a": {"a": "A6.3a"},
    "a6_9b": {"a": "A6.3b"}, "a6_9c": {"a": "A6.3c"}, "a6_10c": {"a": "A6.4c"}, "a6_10e": {"a": "A6.4e"},
    "a6_10f": {"a": "A6.4f"}, "a7_3a": {"a": "A7.1a_a", "b": "A7.1a_b"}, "a7_3c": {"a": "A7.1c"},
    "a7_5b": {"b": "A7.2b_b"}, "a7_5c": {"b": "A7.2c_b"}, "a7_6a": {"a": "A7.3a"}, "a7_6c": {"a": "A7.3c"},
    "a7_6d": {"a": "A7.3d"}, "a7_6e": {"a": "A7.3e"}, "a7_7a": {"x": "A7.4a"}, "a7_7b": {"x": "A7.4b"},
    "a7_7c": {"x": "A7.4c"}, "c_r7b": {"α": "C.1b"}, "c_r7d": {"α": "C.1d"}, "c_ch1": {"α": "C.2"},
    "c_ch2a": {"α": "C.3a"},
}
FREE = {"a4_y9a", "a4_y9b", "a4_y9c", "c_ch2b"}    # letters with no fixed value (algebraic answers)
def segments(g):
    out = []
    for kind, d in g.items:
        if kind == "line":
            out.append((d[0], d[1]))
        elif kind == "poly":
            pts = d[0]
            pairs = list(zip(pts, pts[1:] + pts[:1])) if d[5] else list(zip(pts, pts[1:]))
            out += pairs
    return out


def arm_drawn(segs, v, ang):
    """Is there a drawn segment leaving the vertex v in direction ang (within 0.3 degrees)?"""
    for p, q in segs:
        for a, b in ((p, q), (q, p)):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 1e-9:
                continue
            # v must lie on segment a-b (not at its far end b)
            cross = (b[0] - a[0]) * (v[1] - a[1]) - (b[1] - a[1]) * (v[0] - a[0])
            t = ((v[0] - a[0]) * (b[0] - a[0]) + (v[1] - a[1]) * (b[1] - a[1])) / (L * L)
            if abs(cross) / L > 1e-6 or not (-1e-9 <= t < 1 - 1e-9):
                continue
            d = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            if between(d, ang) < 0.3:
                return True
    return False


for name, fn in figs.FIGS.items():
    g = fn()
    segs = segments(g)
    for lab, size, v, da, db in g.angles:
        report(arm_drawn(segs, v, da) and arm_drawn(segs, v, db), f"fig {name} '{lab}' arms drawn")
        m = re.fullmatch(r"(\d+)°", lab)
        if m:
            if name in NOT_TO_SCALE:
                continue
            report(abs(size - int(m.group(1))) < 0.05, f"fig {name} '{lab}'", f"drawn {size:.2f}°")
            continue
        if name in FREE or name in NOT_TO_SCALE:
            continue
        subs = LETTERS.get(name)
        if subs is None:
            report(False, f"fig {name} '{lab}'", "letter label with no answer key mapped")
            continue
        t = lab.replace("°", "").replace("−", "-")
        t = re.sub(r"(\d)([a-zαβγθ(])", r"\1*\2", t)
        val = sp.sympify(t, locals={s: sp.Symbol(s) for s in subs})
        if any(k not in PRINTED for k in subs.values()):
            report(False, f"fig {name} '{lab}'", "answer key missing")
            continue
        val = val.subs({sp.Symbol(s): num(PRINTED[k])[0] for s, k in subs.items()})
        report(abs(float(val) - size) < 0.05, f"fig {name} '{lab}'", f"label = {float(val):g} with printed answers; drawn {size:.2f}°")

# ------------------------------------------------------------------ question data printed in the questions
Q = read("q_a.html") + read("q_b.html") + read("q_c.html")
for s in ("15°", "35°", "72°", "88°", "56°", "160°", "100°", "75°", "146°", "nine friends (including Jack)",
          "Markers on the road are placed 20 m apart", "60 cm wide", "The length of the wall from left to right is 5 m",
          "5.1 km", "36 525 days", "1760 yards in a mile", "2.54 cm equals 1 inch", "length 2.3 m and width 3.6 m",
          "length 9.8 m and width 6.4 m", "51.6 m down each of the two sides and 16.85 m across the back",
          "side length 1.3 mm", "length 5 m and width 85 cm", "length 800 m and width 2 km", "8 m by 5.4 m, 2.7 m by 8.9 m and 300 cm by 13.3 m",
          r"costs \(\$4.50\)", "each with length 5 m and width 1 m", "area of the parallelogram is 18 cm", "length 8 cm and height 4 cm",
          "height 4 cm and base 2 cm", r"charges \(\$20\)", "diagonals are 8 m and 14.5 m", "2 cm apart", "three times the length",
          "is 12 cm", r"\(AC=4\) cm, \(AB=3\) cm and \(BC=5\) cm", "A path 1 metre wide", "exactly 90°"):
    report(s in Q, "question data: " + s[:60])
# figure labels that carry the measurement data
SVG = {n: read(os.path.join("svg", n + ".svg")) for n in figs.FIGS}
for n, labs in {"b2_1d": ["18", "7", "12", "15"], "b2_1e": ["17", "16"], "b2_1f": ["17", "23"], "b2_8": ["10 m"],
                "b3_2d": ["9 m", "7 m", "3 m", "1 m"], "b3_2f": ["6 cm", "3 cm", "1 cm", "2 cm"],
                "b3_2h": ["8 m", "6 m", "2 m", "4 m"], "b4_1c": ["4 cm", "13 cm"], "b4_1d": ["12 mm", "14 mm"],
                "b4_7b": ["3 km", "8 km"], "b4_7c": ["6 cm", "12 cm", "11 cm"], "b4_7d": ["8 mm", "6 mm", "15 mm"],
                "b4_8a": ["12 m", "5 m"], "b4_8d": ["3 m", "5 m", "7 m"], "b4_11a": ["8 cm", "13 cm"],
                "b4_11b": ["14 m", "12 m"], "b5_3d": ["5 cm", "3 cm"], "b5_3h": ["20 mm", "30 mm"],
                "b5_3k": ["9 m", "5 m", "4 m"], "b5_3l": ["20 mm", "16 mm", "50 mm"], "b5_4b": ["4 m", "5 m", "10 m"],
                "b5_4c": ["13 cm", "3 cm", "10 cm"], "b5_5": ["30 cm", "60 cm"], "b5_11": ["8 cm", "10 cm"],
                "c_r8a": ["6 m", "1 m", "3 m", "4 m", "2 m", "5 m"], "c_r8b": ["10 km", "6 km", "4 km", "2 km"],
                "c_ch4": ["3 m", "4 m", "9 m", "8 m", "1 m"]}.items():
    for lab in labs:
        report(">" + lab + "<" in SVG[n], f"figure {n} shows '{lab}'")

# ------------------------------------------------------------------ cover: times and core sets
COVER = read("cover.html")
EST = {   # section -> per-question minutes (the estimates in the report), core questions
    "A1": ([2, 2, 2, 3, 2], [1, 3, 4, 5]), "A2": ([1, 1, 1, 3, 2, 2], [1, 4, 5, 6]),
    "A3": ([3, 3, 3, 3, 2, 2], [1, 2, 3, 5]), "A4": ([3, 3, 3, 3, 3], [1, 2, 4, 5]),
    "A5": ([2, 4, 4, 3, 3], [1, 2, 3, 4]), "A6": ([2, 3, 4, 4, 3], [1, 2, 3, 4]),
    "A7": ([2, 2, 5, 4, 2, 2], [1, 3, 4]), "B1": ([2, 2, 2, 1, 3, 3], [1, 2, 5, 6]),
    "B2": ([1, 1, 2, 3, 2, 1], [1, 3, 4]), "B3": ([2, 2, 4, 4, 2], [1, 3, 4]),
    "B4": ([1, 4, 4, 2, 2, 2], [1, 2, 5, 6]), "B5": ([3, 2, 2, 2, 3, 2, 1], [1, 3, 5]),
    "C": ([3, 3, 5, 4, 6, 3, 5], [2]),
}
rows = re.findall(r"<tr><td>(A\d|B\d|C) &nbsp;.*?</td><td>([\d, ]*)</td><td class=\"m\">(\d+) min</td><td class=\"m\">(\d+) min</td></tr>", COVER)
report(len(rows) == len(EST), "cover rows", f"{len(rows)} sections")
tot_all = tot_core = 0
# questions and stars per section, from the question files
sec_q = {}
for m in re.finditer(r"\{\{sec:\w+:\w+:(A\d|B\d|C) [^}]*\}\}(.*?)(?=\{\{sec:|\Z)", Q, flags=re.S):
    qs = re.findall(r'<span class="q-num">(\d+)</span><div class="q-body">(.*?)(?=<div class="q"><span class="q-num">|\Z)', m.group(2), flags=re.S)
    sec_q[m.group(1)] = [(int(n), None) for n, body in qs]
for sec, core, mall, mcore in rows:
    est, cq = EST[sec]
    core = [int(c) for c in core.split(",") if c.strip()]
    report(int(mall) == sum(est), f"cover {sec} all minutes", f"{mall} vs {sum(est)}")
    report(int(mcore) == sum(est[i - 1] for i in cq), f"cover {sec} core minutes", f"{mcore}")
    report(core == cq, f"cover {sec} core list", f"{core}")
    qs = sec_q.get(sec, [])
    report([n for n, _ in qs] == list(range(1, len(est) + 1)), f"{sec} question numbering", f"{[n for n, _ in qs]}")
    tot_all += sum(est); tot_core += sum(est[i - 1] for i in cq)
starred = {}
for m in re.finditer(r"\{\{sec:\w+:\w+:(A\d|B\d|C) [^}]*\}\}(.*?)(?=\{\{sec:|\Z)", Q, flags=re.S):
    starred[m.group(1)] = [int(n) for n in re.findall(r'<span class="q-num">(\d+)</span><div class="q-body"><span class="src">[^<]*</span><span class="star">', m.group(2))]
for sec in EST:
    report(starred.get(sec) == EST[sec][1], f"{sec} stars in the questions", f"{starred.get(sec)}")
mt = re.search(r"<td><b>Total</b></td><td></td><td class=\"m\">(\d+) h (\d+) min</td><td class=\"m\">(\d+) h (\d+) min</td>", COVER)
report(bool(mt) and int(mt.group(1)) * 60 + int(mt.group(2)) == tot_all and int(mt.group(3)) * 60 + int(mt.group(4)) == tot_core,
       "cover totals", f"all {tot_all} min, core {tot_core} min")
report(170 <= tot_all <= 210 and 110 <= tot_core <= 130, "about 3 hours in all, about 2 hours core")

# ------------------------------------------------------------------ textbook answer keys
BOOK = {"A3.1e": 50, "A3.1k": 30, "A3.1l": 30, "A3.2g_a": 50, "A3.2g_b": 50, "A3.2h_a": 70, "A3.2h_b": 110,
        "A3.2h_g": 30, "A3.2h_t": 110, "A3.3c": 20, "A3.3g_g": 30, "A3.3g_t": 120, "A3.3h": 65,
        "A3.4a": 40, "A3.4b": 72, "A3.4c": 120, "A3.4d": 200, "A3.5": 110, "A3.6e": 30, "A3.6f": 17,
        "A4.2d": 42, "A4.2g": 64, "A4.2k": 69, "A4.3f_a": 71, "A4.3f_b": 50, "A4.3h_g": 43, "A4.3h_t": 76,
        "A4.4b": 320, "A4.4e": 31, "A4.4i": 33, "A5.2c_a": 70, "A5.2c_t": 110, "A5.2e_a": 70, "A5.2e_b": 30,
        "A5.2e_g": 80, "A5.2h_a": 90, "A5.2h_b": 60, "A5.2h_g": 30, "A5.3b": 137, "A5.3d": 50, "A5.4d": 40,
        "A5.4h_g": 90, "A5.4h_t": 70, "A5.5b": 35, "A5.5d": 30, "A6.2d": 50, "A6.2e": 140, "A6.2f": 55,
        "A6.3a": 55, "A6.3b": 60, "A6.3c": 25, "A6.4c": 18, "A6.4e": F(655, 10), "A6.4f": 60, "A6.5c": 30,
        "A6.5d": 108, "A6.5e": 40, "A7.1a_a": 104, "A7.1a_b": 76, "A7.1c": 128, "A7.2b_a": 2, "A7.2b_b": 90,
        "A7.2c_a": 5, "A7.2c_b": 70, "A7.3a": 152, "A7.3c": 145, "A7.3d": 74, "A7.3e": 59, "A7.4a": 19,
        "A7.4b": 60, "A7.4c": 36, "A2.6a": 58, "A2.6b": 302,
        "B1.1e": F(27, 10), "B1.1h": 190, "B1.1k": 6340, "B1.1l": F(2, 10), "B1.1n": F(2901, 1000), "B1.1s": F(625, 100),
        "B1.2": 51, "B1.3": 220, "B1.4": 5100000000, "B1.5": F(52596, 1000), "B1.6": F(1609344, 10 ** 6),
        "B2.1d": 52, "B2.1e": 50, "B2.1f": 80, "B2.2a": F(118, 10), "B2.2b": F(324, 10), "B2.4": 40,
        "B2.5": F(12005, 100), "B2.6": F(65, 10000), "B3.1a": F(425, 100), "B3.1b": F(16, 10), "B3.2a": 42,
        "B3.2b": 3, "B3.2c": 5, "B3.2d": 12, "B3.3": 4820850, "B3.4d": 60, "B3.4f": 40, "B3.4h": 32, "B3.5": 16,
        "B4.1c": 26, "B4.1d": 84, "B4.2b": 36, "B4.2c": 102, "B4.2d": 105, "B4.3a": 120, "B4.3d": F(1255, 10),
        "B4.4a": 104, "B4.4b": 168, "B4.5h": 3, "B4.5b": 6, "B4.6": 24, "B5.1d": F(75, 10), "B5.1h": 300,
        "B5.1k": F(325, 10), "B5.1l": 560, "B5.2b": 35, "B5.2c": F(845, 10), "B5.3": F(27, 100), "B5.4": 1160,
        "B5.5a": 3, "B5.5b": 9, "C.1b": 35, "C.1d": 93, "C.2": 95, "C.3a": 40, "C.4": F(180, 11),
        "C.5a_p": 42, "C.5a_a": 68, "C.5b_p": 64, "C.5b_a": 72, "C.6a": 6, "C.6b": F(12, 7), "C.7a": 120,
        "C.7p": 62, "C.7c": 66}
for i, v in enumerate((75, 55, 18, 2, 34)):
    BOOK["A2.1" + "abcde"[i]] = v
for i, v in enumerate((20, 80, 105, 92, 34)):
    BOOK["A2.2" + "abcde"[i]] = v
for i, v in enumerate((180, 90, 30, 60, 120, 120, 60, 150)):
    BOOK["A2.4" + "abcdefgh"[i]] = v
for i, v in enumerate((360, 180, 270, 30, 300, 150, 720, 540)):
    BOOK["A2.5" + "abcdefgh"[i]] = v
KNOWN_SLIPS = {"C.6b": "book key prints AX = 12/7 cm; AX = 2 x 6 / 5 = 2.4 cm (area of triangle ABC with base BC)"}
for k, v in BOOK.items():
    got = num(PRINTED.get(k, ""))[0]
    if got == F(v):
        report(True, "book key " + k)
    elif k in KNOWN_SLIPS:
        NOTES.append(k + ": " + KNOWN_SLIPS[k])
        print("NOTE     book key " + k + "  " + KNOWN_SLIPS[k])
    else:
        report(False, "book key " + k, f"printed {got}, book {v}")
# 9E Q7a: the book key prints the unit 'cm^3'; the area is 42 cm^2 (printed with cm^2 above)
NOTES.append("B3.2a: book key prints '42 cm^3'; the area unit is cm^2")

print()
print(f"{N[0]} checks, {len(FAILS)} failures")
for n in NOTES:
    print("note:", n)
if FAILS:
    print("FAILED:", ", ".join(FAILS[:40]))
    sys.exit(1)
print("ALL OK")
