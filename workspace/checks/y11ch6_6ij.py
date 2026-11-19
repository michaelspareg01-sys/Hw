"""Revision 6I-6J: recompute every printed answer in a_6ij.html from the question data (typed in
independently from the book), with math; also check that each figure carries the printed data."""
import math, re, os
from y11ch6_common import *

A = read("a_6ij.html"); V = spans(A, "data-v")
r, d = math.radians, math.degrees
sin, cos, asin, acos, sq = math.sin, math.cos, math.asin, math.acos, math.sqrt
def val(k):
    s = need(V, k, "answer")
    if s is None: return None
    if "^\\circ" in s: return parse_angles(s)
    return float(tex(s))
def num(k, x, dp):           # printed value equals x rounded to dp places
    v = val(k)
    if v is None: return
    check(abs(v - round(x, dp)) < 1e-9, f"{k}: printed {v}, computed {x:.5f}")
def ang(k, xs, mins=False):  # printed angles equal computed ones (nearest degree or minute)
    v = val(k)
    if v is None: return
    if len(v) != len(xs): fail(f"{k}: {v} vs {xs}"); return
    for p, x in zip(sorted(v), sorted(xs)):
        check(round(x * 60) == round(p * 60) if mins else round(x) == p, f"{k}: printed {p}, computed {x:.4f}")
def exact(k, x):
    v = val(k)
    if v is not None: check(abs(v - x) < 1e-9, f"{k}: printed {v}, computed {x}")
sr = lambda a, A, B: a * sin(r(B)) / sin(r(A))             # side opposite B, given a opposite A
cr = lambda b, c, A: sq(b * b + c * c - 2 * b * c * cos(r(A)))
ca = lambda a, b, c: d(acos((b * b + c * c - a * a) / (2 * b * c)))   # angle opposite a

num("i1a", sr(10, 70, 50), 1); num("i1c", sr(4, 55, 85), 1); num("i1e", sr(7, 46, 71), 1)
ang("i3b", [d(asin(8 * sin(r(85)) / 10))]); ang("i3d", [d(asin(6 * sin(r(72)) / 17))]); ang("i3f", [d(asin(16 * sin(r(53)) / 19))])
num("i4a", .5 * 3 * 4 * sin(r(50)), 0); num("i4b", .5 * 5 * 8 * sin(r(70)), 0); num("i4c", .5 * 7 * 7 * sin(r(115)), 0)
num("i5b", sr(7.5, 43, 101), 2); num("i5c", sr(7.5, 43, 36), 2)
A6 = 52 + 21 / 60; B6 = d(asin(2.7 * sin(r(A6)) / 2.8)); check(2.7 < 2.8, "6I Q6 only acute B")
ang("i6a", [B6], True); ang("i6b", [180 - A6 - B6], True); num("i6c", .5 * 2.8 * 2.7 * sin(r(180 - A6 - B6)), 2)
num("j1b", cr(5, 6, 50), 1); num("j1d", cr(8, 10, 115), 1); num("j1f", cr(14, 13, 131), 1)
ang("j2a", [ca(2, 3, 3)]); ang("j2c", [ca(10, 9, 7)]); ang("j2e", [ca(12, 6, 8)])
exact("j3a", cr(3, 4, 60)); exact("j3b", cr(1, 2, 120)); exact("j4a", sq(9 + 4 - 12 * 0.25))
s7 = d(asin(9 * sin(r(22)) / 5)); ang("i7", [s7, 180 - s7])
P9 = 25 + 50 / 60; Q9 = d(asin(15 * sin(r(P9)) / 7)); ang("i9a", [Q9, 180 - Q9], True)
num("i9b", sr(7, P9, 180 - P9 - Q9), 1); num("i9b2", sr(7, P9, 180 - P9 - (180 - Q9)), 1)
exact("i12a", 12 * (2 / 3) / (1 / 4)); exact("i12b", 25 * (3 / 5) / 21)
exact("i13a", 48 / (.5 * 12 * sin(r(30)))); num("i13c", 48 / (.5 * 36 * sin(r(130))), 2)
t = d(asin(72 / (.5 * 16 * 18))); ang("i14a", [t, 180 - t], True); check(72 / (.5 * 12 * 10) > 1, "6I Q14c has no solution")
exact("i15a", sr(6, 45, 60)); exact("i15d", sr(6, 30, 45))
SP = 250 * sin(r(144)) / sin(r(12)); num("i17c", SP * sin(r(42)), 0)
check(abs((180 - 42 - 90) - (180 - 54 - 90) - 12) < 1e-9 and 180 - (42 - 18) - 12 == 144, "6I Q17a angles")
ang("j5a", [ca(5, 6, 7)], True); exact("j5c", (16 + 16 - 25) / 32)
num("j6", cr(120, 180, 136 - 72), 0)
ang("j8", [ca(5, 16, 19), ca(19, 5, 16)], True)
c9 = sq(31 ** 2 + 24 ** 2 - 2 * 31 * 24 * 59 / 62); check(abs(c9 - 11) < 1e-9, "6J Q9a"); check(abs(ca(31, 24, 11) - 120) < 1e-9, "6J Q9b")
r10 = cr(5 * sq(3), 11, 150); exact("j10a", r10); exact("j10b", (11 ** 2 + r10 ** 2 - 75) / (2 * 11 * r10))
BP = cr(3, 6, 120); exact("j12b", BP); check(abs((9 + BP ** 2 - 81) / (2 * 3 * BP) + sq(7) / 14) < 1e-12, "6J Q12c")
cot = lambda a: 1 / math.tan(r(a))
x13 = sq(63 ** 2 / (cot(22) ** 2 + cot(27) ** 2 - 2 * cot(22) * cot(27) * cos(r(51)))); check(round(x13) == 32, f"6J Q13c {x13}")
for xx in (3 * sq(3) + sq(7), 3 * sq(3) - sq(7)):
    check(abs(xx * xx - 6 * sq(3) * xx + 20) < 1e-9 and abs(cr(6, xx, 30) - 4) < 1e-9, "6J Q15")
exact("i20a", 12 / sin(r(60))); check(abs(1 / sin(r(150)) - 2) < 1e-12, "6I Q20b ratio 2:1")
exact("i21d", sin(r(15)))
# 6I Q22 is not used: its part (a) is doubtful (tan of angle B T1 T2 is not cot 36/cot 25; see the report).
for n in (2, 3, 5, 10):
    sides = [n * n + n + 1, 2 * n + 1, n * n - 1]
    ang("j16", [ca(*sides)])
L2 = 64 / (2 * (1 - cos(r(30)))); check(abs((1 - 16 / (2 * L2)) - (6 + sq(3)) / 8) < 1e-12, "6J Q17")

# figures carry the printed data
FIG = {"i1a": ["10", "x", "70°", "50°"], "i1c": ["4", "x", "85°", "55°"], "i1e": ["7", "x", "71°", "46°"],
       "i3b": ["10", "8", "85°", "θ"], "i3d": ["6", "17", "72°", "θ"], "i3f": ["16", "19", "53°", "θ"],
       "i4a": ["3 cm", "4 cm", "50°"], "i4b": ["5 cm", "8 cm", "70°"], "i4c": ["7 cm", "115°"],
       "j1b": ["5", "6", "50°", "x"], "j1d": ["8", "10", "115°", "x"], "j1f": ["13", "14", "131°", "x"],
       "j2a": ["3", "2", "θ"], "j2c": ["10", "9", "7", "θ"], "j2e": ["12", "6", "8", "θ"],
       "j3a": ["3", "4", "60°", "x"], "j3b": ["1", "2", "120°", "x"], "j4a": ["3", "2", "a", "A", "B", "C"],
       "i7a": ["9 cm", "5 cm", "22°"], "i7b": ["9 cm", "5 cm", "22°"], "i13a": ["12 m", "30°", "x"],
       "i13c": ["36 m", "130°", "x"], "i14a": ["16 cm", "18 cm", "θ"], "i14c": ["12 cm", "10 cm", "θ"],
       "i15a": ["6", "60°", "45°", "x"], "i15d": ["6", "45°", "30°", "x"], "i17": ["250 m", "42°", "18°", "54°"],
       "j5a": ["5", "6", "7"], "j5c": ["5", "4", "θ"], "j6": ["120 Nm", "180 Nm"], "j12": ["9 cm", "3 cm", "60°", "x"],
       "j13": ["63 m", "22°", "27°", "51°", "x m"], "j15": ["6 cm", "4 cm", "x cm", "30°"], "i21": ["β", "α", "x", "y", "h"]}
for nm, labs in FIG.items():
    with open(os.path.join(ROOT, "svg", nm + ".svg"), encoding="utf-8") as f:
        texts = re.findall(r">([^<>]+)</text>", f.read())
    for l in labs:
        check(l in texts, f"figure {nm} lacks label {l}")
finish("y11ch6_6ij")
