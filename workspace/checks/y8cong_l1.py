r"""Check of Lesson 1 (8D Congruent figures), tied to the printed HTML and the figures.

Reads build/y8cong/a_l1.html and l1.html (printed answers in <span data-v> / <span data-k>) and the
figures svg/l1_*.svg. Every correspondence answer is recomputed from the drawn coordinates: the vertex
labels are attached to the nearest drawn vertex, every bijection of the vertices that keeps all pairwise
distances is found by brute force (permutations), and the printed vertices, sides and angles are compared
with the images under that matching. 'Congruent pairs' are found by testing every pair of drawn shapes.
Transformations are classified from the matching (orientation, pure translation, single mirror line) and
the Q14 composites are applied to the shapes read off the grid. Q7 counts every triangle whose sides lie
on the drawn lines (all triples of the 25 crossing points, exact Fraction arithmetic). The past-paper
answers are recomputed from the congruence statement and the given data printed in the question.
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 workspace/checks/y8cong_l1.py
"""
import os
import re
import sys
from fractions import Fraction as Fr
from itertools import combinations
from collections import Counter
from math import atan2, degrees, hypot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y8cong_common import (Values, check, check_text, ok, finish, svg_texts, lines, polygons, circles, read,  # noqa: E402
                           plain, caps, dist, ang, congruences, iso_kind, is_pure_reflection, name_vertices,
                           label_centre)

V = Values(["a_l1.html", "l1.html"])
A1 = read("a_l1.html")
L1 = read("l1.html")


def centroid(P):
    return (sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P))


def as_dict(P):
    return {i: p for i, p in enumerate(P)}


def unique_match(P, Q, what):
    m = congruences(P, Q)
    ok(len(m) == 1, f"{what}: exactly one matching keeps every length", f"{len(m)} found")
    return m[0] if m else None


def turn_angle(P, Q, f):
    """Signed turn (degrees, anticlockwise on the page) of a direction-preserving matching P -> Q."""
    a, b = list(P)[:2]
    t1 = degrees(atan2(-(P[b][1] - P[a][1]), P[b][0] - P[a][0]))
    t2 = degrees(atan2(-(Q[f[b]][1] - Q[f[a]][1]), Q[f[b]][0] - Q[f[a]][0]))
    return ((t2 - t1 + 180) % 360) - 180


def grid_unit(fig):
    gx = sorted({round(p[0], 1) for p, q, col, w in lines(fig) if abs(w - 0.7) < 1e-6 and abs(p[0] - q[0]) < 1e-6})
    return (gx[-1] - gx[0]) / (len(gx) - 1)


def named_shapes(fig):
    """{label: polygon} for figures whose labels sit inside (or next to) the shapes."""
    polys = polygons(fig)
    out = {}
    for t, x, y in svg_texts(fig):
        c = label_centre(t, x, y)
        out[t] = min(polys, key=lambda P: dist(centroid(P), c))
    return out


# ================= Concept 1: congruent or not (grid shapes) =================
for fig, base, pre, extra in (("l1_d1", "P", "d1", "bottom"), ("l1_y1", "Q", "y1", "left")):
    S = named_shapes(fig)
    u = grid_unit(fig)
    B = as_dict(S[base])
    for k in "ABCD":
        Q = as_dict(S[k])
        ms = congruences(B, Q) if len(B) == len(Q) else []
        if not ms:
            want = "not congruent"
        else:
            kinds = {iso_kind(B, Q, f) for f in ms}
            want = sorted(kinds)[0] if len(kinds) == 1 else None
            if want == "reflection":
                ok(any(is_pure_reflection(B, Q, f) for f in ms), f"{fig} {k}: a single mirror line maps {base} onto {k}")
            ok(want is not None, f"{fig} {k}: one kind of transformation", str(kinds))
        check_text(V, f"{pre}_{k}", want, label=f"({base} to {k} from the coordinates)")
        tail = re.search(r'data-k="%s_%s">[^<]*</span>([^<]*)' % (pre, k), A1).group(1)
        if want == "translation":
            f = ms[0]
            dx, dy = (Q[f[0]][0] - B[0][0]) / u, -(Q[f[0]][1] - B[0][1]) / u
            words = f"{round(abs(dx))} units {'right' if dx > 0 else 'left'}" + (f" and {round(abs(dy))} units {'up' if dy > 0 else 'down'}" if abs(dy) > 1e-6 else "")
            if abs(dx) < 1e-6:
                words = f"{round(abs(dy))} units {'up' if dy > 0 else 'down'}"
            ok(words in tail, f"{fig} {k}: translation described as {words!r}", tail.strip())
        if want == "rotation":
            f = ms[0]
            t = turn_angle(B, Q, f)
            desc = "180" if abs(abs(t) - 180) < 0.5 else f"90^\\circ\\) {'anticlockwise' if t > 0 else 'clockwise'}" if abs(abs(t) - 90) < 0.5 else None
            ok(desc is not None and desc in tail, f"{fig} {k}: rotation of {t:.1f} degrees described", tail.strip())
        if want == "reflection":
            f = [m for m in ms if is_pure_reflection(B, Q, m)][0]
            mids = [((B[i][0] + Q[f[i]][0]) / 2) for i in B]
            vertical = max(mids) - min(mids) < 0.6
            ok(("vertical line" in tail) == vertical, f"{fig} {k}: mirror line {'vertical' if vertical else 'not vertical'}", tail.strip())
        if want == "not congruent":
            def side(P, which):
                n = len(P)
                E = [(P[i], P[(i + 1) % n]) for i in range(n)]
                if which == "bottom":
                    e = max((e for e in E if abs(e[0][1] - e[1][1]) < 1e-6), key=lambda e: e[0][1])
                else:
                    e = min((e for e in E if abs(e[0][0] - e[1][0]) < 1e-6), key=lambda e: e[0][0])
                return dist(*e) / u
            sk = "Dbase" if pre == "d1" else "Cleft"
            sb = "Pbase" if pre == "d1" else "Qleft"
            check(V, f"{pre}_{sk}", side(S[k], extra), label=f"({extra} side of {k}, grid units)")
            check(V, f"{pre}_{sb}", side(S[base], extra), label=f"({extra} side of {base}, grid units)")
            ok(abs(side(S[k], extra) - side(S[base], extra)) > 0.5, f"{fig}: so {k} is not congruent to {base}")

# circles: radii from the question text
qs = re.findall(r"Circle 1 has radius (\d+) cm, circle 2 has diameter (\d+) cm and circle 3 has diameter (\d+) cm", L1)
ok(len(qs) == 2, "circle questions read (demo and your turn)", str(qs))
for pre, (r1, d2, d3) in zip(("d1", "y1"), qs):
    r = {1: int(r1), 2: int(d2) / 2, 3: int(d3) / 2}
    check(V, f"{pre}_r2", r[2], label="(radius = diameter / 2)")
    check(V, f"{pre}_r3", r[3], label="(radius = diameter / 2)")
    pair = [(i, j) for i, j in combinations((1, 2, 3), 2) if r[i] == r[j]]
    ok(len(pair) == 1, f"{pre}: one pair of circles with equal radii", str(pair))
    s = V.text(f"{pre}_circ")
    if s is not None:
        got = [int(v) for v in re.findall(r"\d", plain(s))]
        ok(got == list(pair[0]), f"{pre}_circ congruent circles", f"printed {got}, computed {list(pair[0])}")


# ================= Concept 2: corresponding parts =================
def two_shapes(fig, n1, n2):
    pos = name_vertices(fig, n1 + n2)
    P = {k: pos[k] for k in n1}
    Q = {k: pos[k] for k in n2}
    return P, Q


def interior_angles(P):
    ks = list(P)
    n = len(ks)
    return {ks[i]: ang(P[ks[i]], P[ks[i - 1]], P[ks[(i + 1) % n]]) for i in range(n)}


def sides(P):
    ks = list(P)
    n = len(ks)
    return {ks[i] + ks[(i + 1) % n]: dist(P[ks[i]], P[ks[(i + 1) % n]]) for i in range(n)}


# tutor demo quadrilaterals PQRS -> WXYZ
P, Q = two_shapes("l1_d2q", "PQRS", "WXYZ")
f = unique_match(P, Q, "l1_d2q")
if f:
    check_text(V, "d2a", [f["S"]], label="(vertex S)")
    check_text(V, "d2b", [f["P"] + f["Q"]], label="(side PQ)")
    check_text(V, "d2c", [f["Q"]], label="(angle Q)")
    g = {v: k for k, v in f.items()}                       # WXYZ -> PQRS
    t = turn_angle(Q, P, g)
    ok(iso_kind(Q, P, g) == "rotation" and abs(t - 90) < 0.5, "WXYZ onto PQRS is a quarter turn anticlockwise", f"{t:.2f}")
    ok("quarter turn anticlockwise" in A1 and "with \\(Y\\) on \\(P\\), \\(Z\\) on \\(Q\\), \\(W\\) on \\(R\\) and \\(X\\) on \\(S\\)" in A1,
       "demo answer states the turn and the matching")
    A = interior_angles(P)
    Sd = sides(P)
    ok(max(A, key=A.get) == "S", "S has the largest angle of PQRS", str({k: round(v, 1) for k, v in A.items()}))
    ok(max(Sd, key=Sd.get) == "PQ" and min(Sd, key=Sd.get) == "SP", "PQ is the longest side and SP the shortest", str({k: round(v, 1) for k, v in Sd.items()}))
# tutor demo triangles LMN -> TRS (marks: right angle at L)
P, Q = two_shapes("l1_d2t", "LMN", "TRS")
f = unique_match(P, Q, "l1_d2t")
if f:
    ok(abs(interior_angles(P)["L"] - 90) < 0.5 and abs(interior_angles(Q)[f["L"]] - 90) < 0.5, "d2t: right angles at L and its match")
    check_text(V, "d2d", ["LMN", f["L"] + f["M"] + f["N"]], label="(congruence statement)")
# your turn quadrilaterals ABCD -> EFGH
P, Q = two_shapes("l1_y2q", "ABCD", "EFGH")
f = unique_match(P, Q, "l1_y2q")
if f:
    check_text(V, "y2a", [f["B"]], label="(vertex B)")
    check_text(V, "y2b", [f["C"] + f["D"]], label="(side CD)")
    check_text(V, "y2c", [f["A"]], label="(angle A)")
    g = {v: k for k, v in f.items()}
    ok(iso_kind(Q, P, g) == "reflection" and is_pure_reflection(Q, P, g), "EFGH onto ABCD is a reflection")
    xs = [(P[k][0] + Q[f[k]][0]) / 2 for k in P]
    ok(max(xs) - min(xs) < 0.6, "the mirror line is vertical")
    A = interior_angles(P)
    Sd = sides(P)
    ok(max(A, key=A.get) == "B", "B has the largest angle of ABCD", str({k: round(v, 1) for k, v in A.items()}))
    ok(max(Sd, key=Sd.get) == "CD" and min(Sd, key=Sd.get) == "AB", "CD is the longest side and AB the shortest", str({k: round(v, 1) for k, v in Sd.items()}))
P, Q = two_shapes("l1_y2t", "PQR", "YZX")
f = unique_match(P, Q, "l1_y2t")
if f:
    ok(abs(interior_angles(P)["P"] - 90) < 0.5 and abs(interior_angles(Q)[f["P"]] - 90) < 0.5, "y2t: right angles at P and its match")
    check_text(V, "y2d", ["PQR", f["P"] + f["Q"] + f["R"]], label="(congruence statement)")
# key ideas triangles: ABC == FDE as the book says
P, Q = two_shapes("l1_keytri", "ABC", "FDE")
f = unique_match(P, Q, "l1_keytri")
if f:
    ok(f == {"A": "F", "B": "D", "C": "E"}, "key ideas figure: A->F, B->D, C->E (so ABC == FDE)", str(f))

# Example 7 (book answers printed in the lesson)
P, Q = two_shapes("l1_ex7", "ABCD", "EFGH")
f = unique_match(P, Q, "l1_ex7")
if f:
    check_text(V, "ex7a", [f["C"]], label="(Example 7 vertex C)")
    check_text(V, "ex7b", [f["A"] + f["B"]], label="(Example 7 side AB)")
    check_text(V, "ex7c", [f["C"]], label="(Example 7 angle C)")
    A = interior_angles(P)
    ok(min(A, key=A.get) == "A" and max(A, key=A.get) == "C", "Example 7: angle A smallest, angle C largest", str({k: round(v, 1) for k, v in A.items()}))
    ok(max(sides(P), key=sides(P).get) == "AB", "Example 7: AB is the longest side")
    g = {v: k for k, v in f.items()}
    ok(iso_kind(Q, P, g) == "rotation" and abs(abs(turn_angle(Q, P, g)) - 180) < 0.5, "Example 7: a half turn takes EFGH onto ABCD")


# ================= Homework =================
for q, n2, kind in (("q1", "DEF", "reflection"), ("q2", "DEF", "translation"), ("q3", "DEF", "rotation")):
    P, Q = two_shapes(f"l1_{q}", "ABC", n2)
    f = unique_match(P, Q, f"l1_{q}")
    if not f:
        continue
    ok(iso_kind(P, Q, f) == kind, f"{q}: the figure shows a {kind}", iso_kind(P, Q, f))
    if kind == "reflection":
        ok(is_pure_reflection(P, Q, f), f"{q}: a single mirror line")
    check_text(V, f"{q}a", "yes", label="(congruent)")
    check_text(V, f"{q}b", [f["A"], f["B"], f["C"]], label="(vertices A, B, C)")
    check_text(V, f"{q}c", [f["A"] + f["B"], f["B"] + f["C"], f["A"] + f["C"]], label="(sides AB, BC, AC)")
    check_text(V, f"{q}d", [f["B"], f["C"], f["A"]], label="(angles B, C, A)")

P, Q = two_shapes("l1_q4", "ABCD", "EFGH")
f = unique_match(P, Q, "l1_q4")
if f:
    check_text(V, "q4a", [f["A"], f["D"]]); check_text(V, "q4b", [f["A"] + f["D"], f["C"] + f["D"]]); check_text(V, "q4c", [f["C"], f["A"]])
    ok(iso_kind(P, Q, f) == "rotation" and abs(abs(turn_angle(P, Q, f)) - 180) < 0.5, "q4: a half turn (as the answer note says)")
    ok(all(f[k] == v for k, v in zip("ABCD", "EFGH")), "q4: note's matching A-E, B-F, C-G, D-H")
P, Q = two_shapes("l1_q5", "ABCDE", "FGHIJ")
f = unique_match(P, Q, "l1_q5")
if f:
    check_text(V, "q5a", [f["A"], f["D"]]); check_text(V, "q5b", [f["A"] + f["E"], f["C"] + f["D"]]); check_text(V, "q5c", [f["C"], f["E"]])
    Sd = sides(P)
    ok(max(Sd, key=Sd.get) == "BC" and min(Sd, key=Sd.get) == "CD", "q5 note: BC longest, CD shortest", str({k: round(v, 1) for k, v in Sd.items()}))
    Sq = sides(Q)
    ok(max(Sq, key=Sq.get) in ("GH", "HG") and min(Sq, key=Sq.get) in ("HI", "IH"), "q5 note: GH longest, HI shortest", str({k: round(v, 1) for k, v in Sq.items()}))
    ok(all(f[k] == v for k, v in zip("ABCDE", "FGHIJ")), "q5: note's matching A-F, B-G, C-H, D-I, E-J")


def congruent_pairs(fig, tol=1.0):
    polys = polygons(fig)
    circs = circles(fig)
    items = [("P", P) for P in polys] + [("C", c) for c in circs]
    names = {}
    for t, x, y in svg_texts(fig):
        c = label_centre(t, x, y)
        k = min(range(len(items)), key=lambda i: dist(centroid(items[i][1]) if items[i][0] == "P" else items[i][1][0], c))
        names[k] = t
    ok(len(names) == len(items), f"{fig}: one label for each shape", f"{len(names)} labels, {len(items)} shapes")
    pairs = []
    for i, j in combinations(range(len(items)), 2):
        (ti, a), (tj, b) = items[i], items[j]
        if ti != tj:
            continue
        if ti == "C":
            same = abs(a[1] - b[1]) < 0.5
        else:
            same = len(a) == len(b) and bool(congruences(as_dict(a), as_dict(b), tol=tol))
        if same:
            pairs.append(frozenset((names[i], names[j])))
    return set(pairs)


for q in ("q6", "q8"):
    want = congruent_pairs(f"l1_{q}")
    s = V.text(q)
    if s is not None:
        t = caps(s)
        got = {frozenset(t[i:i + 2]) for i in range(0, len(t), 2)}
        ok(got == want and len(t) == 6, f"{q} congruent pairs", f"printed {sorted(map(sorted, got))}, computed {sorted(map(sorted, want))}")

# Q7: triangles on the drawn lines
blue = [(p, q) for p, q, col, w in lines("l1_q7") if col.lower() == "#2563eb"]
xs = sorted({round(p[0], 1) for p, q in blue} | {round(q[0], 1) for p, q in blue})
x0, u = xs[0], (xs[-1] - xs[0]) / 4
ybot = max(max(p[1], q[1]) for p, q in blue)
segs = [((Fr(round((p[0] - x0) / u)), Fr(round((ybot - p[1]) / u))), (Fr(round((q[0] - x0) / u)), Fr(round((ybot - q[1]) / u)))) for p, q in blue]
ok(len(segs) == 16, "q7: 16 drawn segments (5 + 5 grid lines, 6 diagonals)", str(len(segs)))


def inter(s, t):
    (x1, y1), (x2, y2) = s
    (x3, y3), (x4, y4) = t
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if d == 0:
        return None
    a = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    b = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d
    return (x1 + a * (x2 - x1), y1 + a * (y2 - y1)) if 0 <= a <= 1 and 0 <= b <= 1 else None


pts = {p for s, t in combinations(segs, 2) for p in [inter(s, t)] if p}


def on_drawn(p, q):
    for a, b in segs:
        col = lambda r: (b[0] - a[0]) * (r[1] - a[1]) - (b[1] - a[1]) * (r[0] - a[0]) == 0
        win = lambda r: min(a[0], b[0]) <= r[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= r[1] <= max(a[1], b[1])
        if col(p) and col(q) and win(p) and win(q):
            return True
    return False


count = Counter()
for p, q, r in combinations(sorted(pts), 3):
    area = abs((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])) / 2
    if area and on_drawn(p, q) and on_drawn(q, r) and on_drawn(p, r):
        count[area] += 1
ok(len(pts) == 25, "q7: 25 crossing points", str(len(pts)))
q7text = L1.split("Year 8 Exercise 8D Q7")[1].split("q-num")[0]
areas = [Fr(1, 2) if "dfrac12" in a else Fr(int(a)) for a in re.findall(r'class="pl">[a-e]</span>area (\\\(\\dfrac12\\\)|\d+)\?', q7text)]
ok(areas == [Fr(1, 2), 1, 2, 4, 8], "q7: areas read from the question", str(areas))
for part, a in zip("abcde", areas):
    check(V, f"q7{part}", count[a], label=f"(triangles of area {a})")

# Q9: corresponding vertices
for q, n1, n2 in (("q9a", "ABC", "DEF"), ("q9b", "ABCD", "WXYZ"), ("q9c", "ABCD", "WXYZ"), ("q9d", "ABCDE", "STXZW")):
    P, Q = two_shapes(f"l1_{q}", n1, n2)
    f = unique_match(P, Q, f"l1_{q}")
    s = V.text(q)
    if f and s is not None:
        t = caps(s)
        got = {t[i]: t[i + 1] for i in range(0, len(t), 2)}
        ok(got == f, f"{q} corresponding vertices", f"printed {got}, computed {f}")
# Q9d note: D and S join the double-marked (longer) sides; ED is the longer of them
P, Q = two_shapes("l1_q9d", "ABCDE", "STXZW")
ok(dist(P["E"], P["D"]) > dist(P["D"], P["C"]) and dist(Q["W"], Q["S"]) > dist(Q["S"], Q["X"]), "q9d note: ED > DC and WS > SX")

# Q10 isosceles triangle cut at the midpoint M
pos = name_vertices("l1_q10", "ABC", polygons("l1_q10"))
M = ((pos["A"][0] + pos["B"][0]) / 2, (pos["A"][1] + pos["B"][1]) / 2)
t = [x for x in svg_texts("l1_q10") if x[0] == "M"][0]
ok(dist(label_centre(*t), M) < 16, "q10: M is labelled at the midpoint of AB")
T1, T2 = {"A": pos["A"], "M": M, "C": pos["C"]}, {"B": pos["B"], "M": M, "C": pos["C"]}
ms = congruences(T1, T2)
check_text(V, "q10a", ["AMC", "BMC"], label="(the two triangles)")
ok({"A": "B", "M": "M", "C": "C"} in ms, "q10: AMC matches BMC (A-B, M-M, C-C)")
check_text(V, "q10b", "yes" if ms else "no", label="(congruent)")

# Q11 kite
pos = name_vertices("l1_q11", "ABCD")
tri = lambda s: {k: pos[k] for k in s}
check_text(V, "q11ai", ["ABD", "CBD"]); check_text(V, "q11bi", ["ABC", "ACD"])
m1 = congruences(tri("ABD"), tri("CBD"))
m2 = congruences(tri("ABC"), tri("ACD"))
ok({"A": "C", "B": "B", "D": "D"} in m1, "q11a: ABD matches CBD")
check_text(V, "q11aii", "yes" if m1 else "no", label="(cut along BD)")
check_text(V, "q11bii", "no" if not m2 else "yes", label="(cut along AC)")
ok(dist(pos["A"], pos["B"]) < dist(pos["A"], pos["D"]), "q11b note: AB and BC are the short sides")

# Q12 parallelogram (a general one): each diagonal gives two congruent triangles
Pg = {"A": (0.0, 0.0), "B": (5.0, 0.0), "C": (7.0, 3.0), "D": (2.0, 3.0)}
t1 = congruences({k: Pg[k] for k in "ABC"}, {k: Pg[k] for k in "CDA"})
t2 = congruences({k: Pg[k] for k in "ABD"}, {k: Pg[k] for k in "CDB"})
check_text(V, "q12", "yes" if (t1 and t2) else "no", label="(both diagonals, general parallelogram)")
check_text(V, "q13", "equal radii", label="(the book's Key idea)")

# Q14 composite transformations on the grid
L = lines("l1_q14")
ax = [(p, q) for p, q, col, w in L if abs(w - 1.3) < 1e-6]
Oy = [p[1] for p, q in ax if abs(p[1] - q[1]) < 1e-6][0]
Ox = [p[0] for p, q in ax if abs(p[0] - q[0]) < 1e-6][0]
u14 = grid_unit("l1_q14")
S = named_shapes("l1_q14")
G = {k: {(round((x - Ox) / u14, 6), round(-(y - Oy) / u14, 6)) for x, y in P} for k, P in S.items()}
ok(G["A"] == {(-3, 4), (-2, 4), (-2, 3), (-1, 3), (-1, 2), (-3, 2)} and G["B"] == {(-4, -1), (-4, -3), (-3, -3)},
   "q14: shapes A and B read from the grid", str(sorted(G["A"])))


def apply(desc, pts):
    """Apply the printed transformations (in order) and the printed translation vector to the points."""
    d = plain(desc).replace("−", "-")
    out = set(pts)
    ops = list(re.finditer(r"reflection in the ([xy]) -axis|rotation (anticlockwise )?about the origin \(0,0\) by (\d+)\^\\circ", d))
    for m in ops:
        if m.group(1) == "x":
            out = {(x, -y) for x, y in out}
        elif m.group(1) == "y":
            out = {(-x, y) for x, y in out}
        elif m.group(3) == "180":
            out = {(-x, -y) for x, y in out}
        elif m.group(3) == "90" and m.group(2):
            out = {(-y, x) for x, y in out}
        elif m.group(3) == "90":
            out = {(y, -x) for x, y in out}
    vec = [int(v) for v in re.search(r"\\begin\{bmatrix\}(-?\d+)\\\\(-?\d+)\\end", desc.replace("−", "-")).groups()]
    return {(x + vec[0], y + vec[1]) for x, y in out}, len(ops)


for part, src, dst, nops in (("a", "A", "A′", 1), ("b", "A", "A′", 1), ("c", "B", "B′", 1), ("d", "B", "B′", 2), ("e", "C", "C′", 2), ("f", "C", "C′", 1)):
    s = V.text(f"q14{part}")
    if s is None:
        continue
    img, n = apply(s, G[src])
    ok(img == G[dst] and n == nops, f"q14{part}: printed transformations take {src} onto {dst}", f"{sorted(img)} vs {sorted(G[dst])}, {n} step(s)")


# ================= Past papers =================
# PP1: statement and given lengths from the question; figure drawn as that congruence
q = L1.split("PP 1")[1].split("PP 2")[0]
st = re.search(r"\\triangle (\w{3})\\equiv\\triangle (\w{3})", q)
given = dict(re.findall(r"(\w{2})=(\d+)", q))
f = dict(zip(st.group(1), st.group(2)))
inv = {v: k for k, v in f.items()}
yz = "".join(sorted(inv[c] for c in "YZ"))
check(V, "pp1", int(given[yz] if yz in given else given[yz[::-1]]), label="(YZ matches BC)")
P, Q = two_shapes("l1_pp1", "ABC", "XYZ")
m = unique_match(P, Q, "l1_pp1")
ok(m == f, "pp1 figure: drawn as ABC == XYZ", str(m))
ok(abs(dist(P["B"], P["C"]) / dist(P["A"], P["B"]) - 7 / 3) < 0.02 and abs(dist(P["A"], P["C"]) / dist(P["A"], P["B"]) - 5 / 3) < 0.02,
   "pp1 figure: sides in the ratio 3 : 7 : 5")
# PP2: statement OAB == OCD; the given angle BAO; the figure's O is the common midpoint of AC and BD
q = L1.split("PP 2")[1]
st = re.findall(r"\\triangle (\w{3})\\equiv\\triangle (\w{3})", q)[0]
f = dict(zip(*st))
g = int(re.search(r"\\angle BAO=(\d+)", q).group(1))
want = g if (f["A"], f["B"]) == ("C", "D") and f["O"] == "O" else None
check(V, "pp2", want, label="(angle OCD matches angle OAB = angle BAO)")
segs2 = [(p, q2) for p, q2, col, w in lines("l1_pp2") if abs(w - 1.6) < 1e-6]
ends = [p for s in segs2 for p in s]
pos = {}
for t, x, y in svg_texts("l1_pp2"):
    if t in "ABCD" and len(t) == 1:
        c = label_centre(t, x, y)
        pos[t] = min(ends, key=lambda p: dist(p, c))
O = ((pos["A"][0] + pos["C"][0]) / 2, (pos["A"][1] + pos["C"][1]) / 2)
O2 = ((pos["B"][0] + pos["D"][0]) / 2, (pos["B"][1] + pos["D"][1]) / 2)
ok(dist(O, O2) < 1.0, "pp2 figure: AC and BD bisect each other at O (OA = OC, OB = OD)")
ok({"O": "O", "A": "C", "B": "D"} in congruences({"O": O, "A": pos["A"], "B": pos["B"]}, {"O": O, "C": pos["C"], "D": pos["D"]}),
   "pp2 figure: OAB matches OCD")

finish([V])
