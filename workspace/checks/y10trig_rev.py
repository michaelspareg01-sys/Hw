r"""Check of the Year 10 Trigonometry (part 2) revision page, tied to the HTML.

Reads workspace/build/y10trig/revision.html and a_rev.html.
  1. Givens: every number the warm-up questions and worked examples rely on is read from the printed
     question text (each pattern must match exactly once in revision.html, or the item FAILS).
  2. Answers: every final answer in a_rev.html carries data-v="KEY" (each key exactly once). It is
     parsed and compared with an independent computation (Python math) from the givens READ in step 1,
     rounded as the question asks, and with the Year 11 Advanced book's printed answer
     (PDF 546 for 5B, PDF 549 for 5K), transcribed in BOOK below.
  3. Worked examples: Example 2 (theta = 59 deg 45') and Example 29 (theta = 117 deg 17') are recomputed.
Exit status 1 if anything fails.  Run: python3 workspace/checks/y10trig_rev.py
"""
import os
import re
import sys
from math import atan, acos, asin, sin, cos, tan, sqrt, radians, degrees

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


def plain(html):
    s = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", s.replace("&amp;", "&"))


LES = plain(open(os.path.join(SRC, "revision.html"), encoding="utf-8").read())
ANS_RAW = open(os.path.join(SRC, "a_rev.html"), encoding="utf-8").read()


def given(pattern, label):
    m = re.findall(pattern, LES)
    if len(m) != 1:
        ok(False, f"given {label}", f"pattern found {len(m)} times: {pattern}")
        return None
    v = m[0]
    if not re.search(r"\((?!\?)", pattern):
        return True
    return tuple(float(t) for t in v) if isinstance(v, tuple) else float(v)


def val(key):
    m = re.findall(r'data-v="%s">([^<]*)<' % key, ANS_RAW)
    if len(m) != 1:
        ok(False, f"answer {key}", f"found {len(m)} times")
        return None
    return m[0].strip()


def num(s):
    return float(re.match(r"-?\d+(?:\.\d+)?", s).group(0))


def dm(s):
    m = re.match(r"(\d+)°(\d+)′", s)
    return int(m.group(1)), int(m.group(2))


def to_dm(deg):
    d = int(deg)
    m = round((deg - d) * 60)
    if m == 60:
        d, m = d + 1, 0
    return d, m


BOOK = {"w1": "038°T", "w2": 77, "w3": 23, "w4a": 28.3, "w4b": 17.3, "w4c": 12.5, "w4d": 36.2, "w4e": 12.6,
        "w4f": 23.2, "w5a": 59, "w5b": 55, "w5c": 40, "w6a": (44, 25), "w6b": 10}

# ---- 1. givens read from the printed questions
g = {}
g["n"] = given(r"sails (\d+) nautical miles due north", "5B Q4 north leg")
g["e"] = given(r"then (\d+) nautical miles due east", "5B Q4 east leg")
g["d"], g["brg"] = (given(r"Eleni drives (\d+) km on a bearing of (\d+)°T", "5B Q7") or (None, None))
g["dep"] = given(r"angle of depression of \\\(C\\\) from \\\(W\\\) is (\d+)°", "5B Q8 angle")
g["bc"] = given(r"the car is (\d+) metres from the base", "5B Q8 distance")
g["k7"] = given(r"AB=(\d+)\\\) cm, \\\(BC=(\d+)\\\) cm and \\\(CA=(\d+)\\\) cm", "5K Q7 sides")
g["ex2"] = given(r"\\tan\\theta&=\\frac\{(\d+)\}\{(\d+)\}", "Example 2")
g["ex29"] = given(r"6\^2&=3\^2\+4\^2", "Example 29")

# 5K Q1/Q2 data come from the figures: read the label text of each svg
SVG = os.path.join(SRC, "svg")


def labels(name):
    s = open(os.path.join(SVG, name + ".svg"), encoding="utf-8").read()
    return [t for t in re.findall(r">([^<>]+)</text>", s)]


def need(name, items):
    labs = labels(name)
    for it in items:
        ok(labs.count(it) == 1, f"figure {name} label {it!r}", f"labels {labs}")


need("rev_k1a", ["x", "23", "43°", "57°"])
need("rev_k1b", ["x", "13.5", "52°"])
need("rev_k1c", ["x", "11", "13", "62°"])
need("rev_k1d", ["x", "24", "41°30′"])
need("rev_k1e", ["x", "7.4", "9.2", "98°"])
need("rev_k1f", ["x", "18", "54°", "49°"])
need("rev_k2a", ["θ", "10", "11", "12"])
need("rev_k2b", ["θ", "9", "8", "67°"])
need("rev_k2c", ["θ", "13", "17"])
need("rev_k7", ["4 cm", "5 cm", "7 cm"])
need("rev_w1", ["78", "61", "θ"])
need("rev_w2", ["120 km", "130°"])
need("rev_w6", ["7 m", "73°"])

# ---- 2. answers
calc = {}
if g["n"] and g["e"]:
    calc["w1"] = "%03d°T" % round(degrees(atan(g["e"] / g["n"])))
if g["d"]:
    calc["w2"] = round(g["d"] * cos(radians(180 - g["brg"])))
if g["dep"]:
    calc["w3"] = round(g["bc"] * tan(radians(g["dep"])))
calc["w4a"] = round(23 * sin(radians(57)) / sin(radians(43)), 1)
calc["w4b"] = round(13.5 * tan(radians(52)), 1)
calc["w4c"] = round(sqrt(11 ** 2 + 13 ** 2 - 2 * 11 * 13 * cos(radians(62))), 1)
calc["w4d"] = round(24 / sin(radians(41.5)), 1)
calc["w4e"] = round(sqrt(7.4 ** 2 + 9.2 ** 2 - 2 * 7.4 * 9.2 * cos(radians(98))), 1)
calc["w4f"] = round(18 * sin(radians(180 - 54 - 49)) / sin(radians(49)), 1)
calc["w5a"] = round(degrees(acos((10 ** 2 + 12 ** 2 - 11 ** 2) / (2 * 10 * 12))))
calc["w5b"] = round(degrees(asin(8 * sin(radians(67)) / 9)))
calc["w5c"] = round(degrees(acos(13 / 17)))
if g["k7"]:
    ab, bc, ca = g["k7"]
    B = degrees(acos((ab ** 2 + bc ** 2 - ca ** 2) / (2 * ab * bc)))
    calc["w6a"] = to_dm(B)
    calc["w6b"] = round(0.5 * ab * bc * sin(radians(B)))

for key in BOOK:
    v = val(key)
    if v is None:
        continue
    if key == "w1":
        got = v
    elif key == "w6a":
        got = dm(v)
    else:
        got = num(v)
    ok(got == calc.get(key), f"{key} computed", f"printed {v!r}, computed {calc.get(key)!r}")
    ok(got == BOOK[key], f"{key} book answer", f"printed {v!r}, book {BOOK[key]!r}")

# working lines that carry intermediate values
for pat, want, lab in [(r"290-286\\cos62\^\\circ\\doteqdot([\d.]+)", 290 - 286 * cos(radians(62)), "w4c x^2"),
                       (r"139\.4-136\.16\\cos98\^\\circ\\doteqdot([\d.]+)", 7.4 ** 2 + 9.2 ** 2 - 136.16 * cos(radians(98)), "w4e x^2"),
                       (r"\\sin\\theta=\\dfrac\{8\\sin67\^\\circ\}\{9\}\\doteqdot([\d.]+)", 8 * sin(radians(67)) / 9, "w5b sin"),
                       (r"14\\sin44\^\\circ25'\\doteqdot([\d.]+)", 14 * sin(radians(44 + 25 / 60)), "w6b area"),
                       (r"120\\cos50\^\\circ\\\\ &amp;\\doteqdot([\d.]+)", 120 * cos(radians(50)), "w2 SF"),
                       (r"7\\tan73\^\\circ\\\\ &amp;\\doteqdot([\d.]+)", 7 * tan(radians(73)), "w3 WB")]:
    m = re.findall(pat, ANS_RAW)
    if ok(len(m) == 1, f"working {lab} present", f"found {len(m)}"):
        ok(abs(float(m[0]) - want) < 0.006 + 1e-9, f"working {lab} value", f"printed {m[0]}, computed {want:.4f}")
ok(abs(2 * 7.4 * 9.2 - 136.16) < 1e-9 and abs(7.4 ** 2 + 9.2 ** 2 - 139.4) < 1e-9,
   "w4e constants 139.4 and 136.16")
ok(2 * 11 * 13 == 286 and 11 ** 2 + 13 ** 2 == 290, "w4c constants 290 and 286")

# ---- 3. worked examples
if g["ex2"]:
    o, a = g["ex2"]
    ok(to_dm(degrees(atan(o / a))) == (59, 45), "Example 2: tan^-1(12/7) = 59 deg 45'")
ok(3 ** 2 + 4 ** 2 - 6 ** 2 == -11 and 2 * 3 * 4 == 24, "Example 29: 24 cos(theta) = -11")
ok(to_dm(degrees(acos(-11 / 24))) == (117, 17), "Example 29: theta = 117 deg 17'")

print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
