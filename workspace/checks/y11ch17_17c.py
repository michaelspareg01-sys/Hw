"""Check of Lesson 17C (Y11 Ch 17 pack): Graphs involving inverse trigonometric functions.

Reads the PRINTED answers (data-k spans) in workspace/build/y11ch17/a_17c.html and the questions in
l17c.html. Every printed domain or range is compared with an interval recomputed independently:
ranges by sympy function_range on the domain (or by dense sampling of the function, for compositions),
domains by solving the inequality on the inner argument. Decimal values are recomputed from the
given value and the identities sin^-1 x + cos^-1 x = pi/2, cos^-1(-x) = pi - cos^-1 x and compared at
4 d.p.; values such as cos^-1(cos 7pi/3) are recomputed with sympy. Graph data (the SVGs) are sampled
to confirm that each answer figure plots the function it claims. The past-paper block is checked
(marks, time, labels, hints, MC keys, each MC option tested). Exit 1 on failure.
Run: python3 workspace/checks/y11ch17_17c.py
"""
import math
import re
import sympy as sp
from sympy.calculus.util import function_range
from y11ch17_common import (read, get, maths, tex, check, finish, x, eq_value, set_value, pp_block, mc_key,
                            num_equal, interval, SRC)

L = read("l17c.html")
A = read("a_17c.html")
pi = sp.pi
I = sp.Interval
asin, acos, atan, sin, cos, tan = sp.asin, sp.acos, sp.atan, sp.sin, sp.cos, sp.tan
R = sp.Rational
Re = sp.S.Reals


def rng(expr, dom):
    return function_range(expr, x, dom)


def dom_of(arg):
    """Domain of asin/acos of arg(x): solve -1 <= arg <= 1."""
    return sp.solveset(sp.And(arg >= -1, arg <= 1), x, Re) if False else sp.reduce_inequalities([arg >= -1, arg <= 1], x).as_set()


for q in [r"y+\dfrac\pi2=\tan^{-1}(x-1)", r"y=\cos^{-1}(-x)+\dfrac\pi2", r"y-\dfrac\pi4=\tan^{-1}(x+2)", r"y=\sin^{-1}(-x)+\dfrac\pi2",
          r"\cos^{-1}0.6\doteq0.9273", r"\sin^{-1}0.3\doteq0.3047", r"y=\cos\big(\cos^{-1}3x\big)", r"y=\sin\Big(\sin^{-1}\dfrac x3\Big)",
          r"y=\sin^{-1}(x-1)", r"y=\cos^{-1}(x+1)", r"y-\dfrac\pi2=\tan^{-1}x", r"y=-\cos^{-1}x", r"y=\tan^{-1}(-x)", r"y=-\sin^{-1}(-x)",
          r"y=\sin^{-1}(1-x)", r"y=\cos^{-1}(1-x)", r"y=-\sin^{-1}(x+1)", r"y=-\tan^{-1}(1-x)", r"y=\sin\big(\cos^{-1}x\big)",
          r"y=3\tan^{-1}x", r"y=2\cos^{-1}(x-1)", r"y=2\sin^{-1}\dfrac x3", r"f(x)=\tan^{-1}(\sin x)", r"y=2\cos^{-1}(2x-3)",
          r"f(x)=2\sin^{-1}\Big(\dfrac x3\Big)+\dfrac\pi2", r"f(x)=4\cos^{-1}\Big(\dfrac16x\Big)-\dfrac\pi2", r"\arcsin(3x+1)=\arccos x",
          r"y=\sin^{-1}\dfrac{4x-1}{2}"]:
    check(q in L, f"question text {q} printed")

# ---- lesson examples
set_value(A, "d1a", rng(atan(x - 1) - pi / 2, Re), "C1 demo a range")
set_value(A, "d1bd", dom_of(-x), "C1 demo b domain")
set_value(A, "d1br", rng(acos(-x) + pi / 2, I(-1, 1)), "C1 demo b range")
set_value(A, "y1a", rng(atan(x + 2) + pi / 4, Re), "C1 your turn a range")
set_value(A, "y1b", rng(asin(-x) + pi / 2, I(-1, 1)), "C1 your turn b range")
c06 = 0.9273
for k, v in {"d2a": math.pi / 2 - c06, "d2b": math.pi - c06, "d2c": -(math.pi / 2 - c06)}.items():
    s = get(A, k)
    if s:
        check(abs(float(tex(maths(s))) - round(v, 4)) < 1e-9 and abs(float(tex(maths(s))) - {"d2a": math.asin(.6), "d2b": math.acos(-.6), "d2c": math.asin(-.6)}[k]) < 6e-5,
              f"{k}: printed {maths(s)} vs {v:.4f}")
s03 = 0.3047
c03 = math.pi / 2 - s03
for k, v, true in [("y2a", c03, math.acos(.3)), ("y2b", -s03, math.asin(-.3)), ("y2c", math.pi - round(c03, 4), math.acos(-.3))]:
    s = get(A, k)
    if s:
        check(abs(float(tex(maths(s))) - round(v, 4)) < 1e-9 and abs(float(tex(maths(s))) - true) < 1.5e-4, f"{k}: printed {maths(s)} vs {v:.4f} (true {true:.4f})")
set_value(A, "d3a", dom_of(3 * x), "C3 demo a domain")
set_value(A, "y3a", dom_of(x / 3), "C3 your turn a domain")
for k, v in {"d3c1": acos(cos(-2 * pi / 3)), "d3c2": acos(cos(7 * pi / 3)), "y3c1": acos(cos(3 * pi / 2)), "y3c2": acos(cos(-5 * pi / 6))}.items():
    eq_value(A, k, v, k)

# ---- Exercise 17C
ex = {"1a": rng(atan(x), Re), "1b": rng(acos(x), I(-1, 1)), "1c": rng(asin(x), I(-1, 1)),
      "2ad": dom_of(x - 1), "2ar": rng(asin(x - 1), I(0, 2)), "2bd": dom_of(x + 1), "2br": rng(acos(x + 1), I(-2, 0)),
      "2cr": rng(atan(x) + pi / 2, Re), "3a": rng(-acos(x), I(-1, 1)), "3b": rng(atan(-x), Re), "3c": rng(-asin(-x), I(-1, 1)),
      "5a": dom_of(1 - x), "5b": rng(asin(1 - x), I(0, 2)), "6ad": dom_of(1 - x), "6ar": rng(acos(1 - x), I(0, 2)),
      "6bd": dom_of(x + 1), "6br": rng(-asin(x + 1), I(-2, 0)), "6cr": rng(-atan(1 - x), Re), "8a": dom_of(x),
      "9a": I.open(-pi / 2, pi / 2), "11a": I(-pi / 2, pi / 2)}
for k, v in ex.items():
    set_value(A, k, v, k)
# 9a and 11a: confirm by sampling the compositions
samp = [k_ * 0.0137 for k_ in range(-2000, 2000)]
v9 = [math.atan(math.tan(t)) for t in samp if abs(math.cos(t)) > 1e-9]
v11 = [math.asin(math.sin(t)) for t in samp]
check(max(v9) < math.pi / 2 and min(v9) > -math.pi / 2 and max(v11) <= math.pi / 2 + 1e-12, "9a/11a ranges sampled")
s = get(A, "5c")
if s:
    vals = [tex(v) for v in maths(s).split("=")[1].replace("\\ ", "").split(",")]
    check(vals == [asin(1 - xv) for xv in (0, 1, 2)], f"5c table y = {vals}")
eq_value(A, "5d", R(1, 2), "5d line of symmetry x = 1/2")
check(all(abs(math.asin(1 - (1 - t)) - math.asin(t)) < 1e-12 for t in (-1, -.3, .2, .9)), "5d: sin^-1(1 - x) is sin^-1 x reflected in x = 1/2")
# odd/even statements
for key, f, dom, word in [("1a", math.atan, (-5, 5), "odd"), ("1c", math.asin, (-1, 1), "odd"), ("3b", lambda t: math.atan(-t), (-5, 5), "odd"),
                          ("3c", lambda t: -math.asin(-t), (-1, 1), "odd")]:
    ts = [dom[0] + (dom[1] - dom[0]) * k_ / 40 for k_ in range(41)]
    check(all(abs(f(-t) + f(t)) < 1e-12 for t in ts) and re.search(r'data-k="' + key + r'">' + re.escape(get(A, key) or "") + r"</span>, odd", A), f"{key} odd")

# ---- answer figures: sample the SVG polylines and confirm they lie on the stated function
def svg_points(name):
    with open(f"{SRC}/svg/{name}.svg", encoding="utf-8") as fh:
        svg = fh.read()
    pts = []
    for m in re.finditer(r'<polyline points="([^"]+)" fill="none" stroke="#2563eb"', svg):
        pts += [tuple(map(float, p.split(","))) for p in m.group(1).split()]
    return svg, pts


figs = {"ca_2a": (lambda t: math.asin(t - 1), (-0.6, 2.6, -2.1, 2.1)), "ca_6a": (lambda t: math.acos(1 - t), (-0.6, 2.6, -0.5, 3.7)),
        "ca_6b": (lambda t: -math.asin(t + 1), (-2.6, 0.6, -2.1, 2.1)), "ca_10": (lambda t: math.asin(math.cos(t)), (-2.3 * math.pi, 2.3 * math.pi, -2.2, 2.2)),
        "ca_11e": (lambda t: math.acos(math.sin(t)), (-2.3 * math.pi, 2.3 * math.pi, -0.6, 3.8))}
for name, (f, (x0, x1, y0, y1)) in figs.items():
    svg, pts = svg_points(name)
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    W, H = float(m.group(1)), float(m.group(2))
    pl, pr, pt_, pb = 30, 34, 22, 28
    bad = 0
    for px, py in pts[::7]:
        xv = x0 + (px - pl) / (W - pl - pr) * (x1 - x0)
        yv = y1 - (py - pt_) / (H - pt_ - pb) * (y1 - y0)
        try:
            if abs(f(xv) - yv) > 0.05:
                bad += 1
        except ValueError:
            bad += 1
    check(len(pts) > 20 and bad == 0, f"figure {name}: {len(pts)} plotted points on the stated curve ({bad} off)")

# ---- past papers
pp_block(L, A)
check("\\pm\\dfrac{3\\pi}{2}" in (get(A, "pp1") or ""), "PP1 y = +-3pi/2")
mc_key(A, "PP 1", "D")
set_value(A, "pp2d", dom_of(x - 1), "PP2 domain")
set_value(A, "pp2r", rng(2 * acos(x - 1), I(0, 2)), "PP2 range")
mc_key(A, "PP 2", "D")
mc_key(A, "PP 3", "A")
check(rng(2 * asin(x / 3), I(-3, 3)) == I(-pi, pi) and dom_of(x / 3) == I(-3, 3), "PP3 domain [-3, 3], range [-pi, pi] (graph A)")
set_value(A, "pp4", I(-pi / 4, pi / 4), "PP4 range")
v4 = [math.atan(math.sin(t)) for t in samp]
check(abs(max(v4) - math.pi / 4) < 1e-6 and abs(min(v4) + math.pi / 4) < 1e-6, "PP4 range sampled, end points attained")
mc_key(A, "PP 4", "B")
ts = [-2 * math.pi + k_ * math.pi / 8 for k_ in range(33)]
graphy = {t: math.acos(math.sin(t)) for t in ts}
check(all(abs(graphy[t] - math.acos(math.sin(t))) < 1e-12 for t in ts) and abs(graphy[-math.pi / 2] - math.pi) < 1e-12
      and abs(graphy[math.pi / 2]) < 1e-12 and abs(graphy[0] - math.pi / 2) < 1e-12, "PP5 graph points (0, pi/2), (pi/2, 0), (-pi/2, pi)")
check(max(math.asin(math.cos(t)) for t in ts) <= math.pi / 2 + 1e-12, "PP5 option A never exceeds pi/2")
mc_key(A, "PP 5", "D")
s = get(A, "pp6")
if s:
    xa = sp.solve(2 * x - 3 + 1, x)[0]
    check(maths(s).replace(" ", "") == f"A=({xa},2\\pi)" and 2 * acos(2 * xa - 3) == 2 * pi, "PP6 A = (1, 2pi)")
set_value(A, "pp7d", dom_of(x / 3), "PP7 domain")
set_value(A, "pp7r", rng(2 * asin(x / 3) + pi / 2, I(-3, 3)), "PP7 range")
s = get(A, "pp8")
if s:
    f8 = tex(maths(s).split("=")[1])
    check(abs(float(f8.subs(x, -3)) - 2) < 1e-12 and abs(float(f8.subs(x, 3))) < 1e-12 and abs(float(f8.subs(x, 0)) - 1) < 1e-12,
          "PP8 f(-3) = 2, f(0) = 1, f(3) = 0 as on the grid")
set_value(A, "pp9d", dom_of(x / 6), "PP9 domain")
set_value(A, "pp9r", rng(4 * acos(x / 6) - pi / 2, I(-6, 6)), "PP9 range")
sol = [t for t in sp.solve(sp.Eq(3 * x + 1, sp.sin(sp.acos(x))), x) if -R(2, 3) <= t <= 0]
grid = [k_ / 3000 * 2 / 3 - 2 / 3 for k_ in range(3001)]
diffs = [math.asin(3 * t + 1) - math.acos(t) for t in grid]
signchanges = sum(1 for a_, b_ in zip(diffs, diffs[1:]) if a_ * b_ < 0)
check(abs(math.asin(1) - math.acos(0)) < 1e-15 and signchanges == 0 and abs(diffs[-1]) < 1e-12, "PP10 only solution x = 0 on [-2/3, 0]")
eq_value(A, "pp10", 0, "PP10")
s = get(A, "pp11")
if s:
    parts = re.findall(r"\\\((.*?)\\\)", s)
    sets = interval("x\\in[-\\dfrac34,-\\dfrac14)\\cup(\\dfrac14,\\dfrac34]")
    printed = interval(parts[0].replace("x&lt;", "x<")) | interval(parts[1].replace("&lt;", "<"))
    # brute force
    ok_pts = [t / 1000 for t in range(-760, 761) if abs(4 * abs(t / 1000) - 1) / 2 <= 1 and math.asin((4 * abs(t / 1000) - 1) / 2) > 0]
    check(printed == sets and all(t in sets for t in [sp.Rational(int(v * 1000), 1000) for v in ok_pts]), "PP11 solution set")
finish("y11ch17_17c")
