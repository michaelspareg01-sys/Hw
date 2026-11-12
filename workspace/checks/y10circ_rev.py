r"""Check of the Year 10 Circle Geometry revision warm-up, tied to the printed HTML and figures.

Reads build/y10circ/a_rev.html (every printed number is a <span data-v="KEY">) and the warm-up figures
svg/w*.svg. The given angles and lengths are read from the figure labels, the answers are recomputed
from them (angle sums, isosceles base angles, side ratios), and the triangles that are drawn to scale
are measured from their coordinates. Every data-v key must be found exactly once and every key must be
checked. Exit status 1 on any failure.  Run: python3 workspace/checks/y10circ_rev.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y10circ_common import Values, check, svg_has, polygons, ang, ok, finish, svg_labels  # noqa: E402

V = Values(["a_rev.html"])


def given(fig, unit="°"):
    labs = [l for l in svg_labels(fig) if l.endswith(unit) and l[:-len(unit)].strip().replace(".", "").isdigit()]
    return [float(l.replace(unit, "").strip()) for l in labs]


# Q1: isosceles triangles (apex angle given in a and b? read the labels)
svg_has("w1a", "50°", "a°"); svg_has("w1b", "100°", "a°"); svg_has("w1c", "28°", "a°")
for k, apex in (("w1a", 50), ("w1b", 100), ("w1c", 28)):
    g = given(k)
    ok(g == [apex], f"{k} given angle read from figure", str(g))
    check(V, k, (180 - g[0]) / 2, label="base angle = (180 - apex)/2")
    # drawn to scale: measure the triangle
    P = polygons(k)[0]
    A = sorted(ang(P[i], P[i - 1], P[(i + 1) % 3]) for i in range(3))
    ok(min(abs(x - g[0]) for x in A) < 0.5 and sum(abs(x - (180 - g[0]) / 2) < 0.5 for x in A) >= 2,
       f"{k} figure drawn to scale", f"angles {[round(x, 1) for x in A]}")

# Q2a: equilateral triangle, vertically opposite angle
check(V, "w2a_ACB", 60, label="equilateral")
check(V, "w2a", 60, label="vertically opposite")
P = polygons("w2a")[0]
ok(all(abs(ang(P[i], P[i - 1], P[(i + 1) % 3]) - 60) < 0.5 for i in range(3)), "w2a figure equilateral")
# Q2b: reflex angle
svg_has("w2b", "22°", "29°", "a°")
g = sorted(given("w2b"))
check(V, "w2b_ACB", 180 - g[0] - g[1], label="angle sum")
check(V, "w2b", 360 - (180 - g[0] - g[1]), label="revolution")
# Q2e: isosceles with vertically opposite angle
svg_has("w2e", "49°", "a°")
g = given("w2e")[0]
check(V, "w2e_ACB", g, label="vertically opposite")
check(V, "w2e", (180 - g) / 2, label="(180 - 49)/2")

# Q4: side ratios read from the figures
def lens(fig):
    return [float(l.replace(" m", "")) for l in svg_labels(fig) if l.endswith(" m")]
a = lens("w4a")          # order drawn: 12, 13, 5 (ABC) then 26, 24, 10 (DEF)
ok(sorted(a) == [5, 10, 12, 13, 24, 26], "w4a lengths read", str(a))
check(V, "w4a_1", 10 / 5); check(V, "w4a_2", 24 / 12); check(V, "w4a_3", 26 / 13)
ok(5 ** 2 + 12 ** 2 == 13 ** 2 and 10 ** 2 + 24 ** 2 == 26 ** 2, "w4a both triangles right-angled (consistent data)")
c = lens("w4c")
ok(sorted(c) == [3, 5, 6, 10], "w4c lengths read", str(c))
check(V, "w4c_1", 10 / 5); check(V, "w4c_2", 6 / 3)
d = lens("w4d")
ok(sorted(d) == [11, 13, 22, 26], "w4d lengths read", str(d))
check(V, "w4d_1", 26 / 13); check(V, "w4d_2", 22 / 11)
svg_has("w4b", "75°", "80°")

finish([V])
