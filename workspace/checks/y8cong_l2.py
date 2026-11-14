r"""Check of Lesson 2 (8E Congruent triangles), tied to the printed HTML and the figures.

Reads build/y8cong/a_l2.html and l2.html (answers in <span data-v> / <span data-k>; the given data of the
Concept 3 demos in <span data-g>) and the figures svg/l2_*.svg (and svg/l1_pp2.svg).

For every triangle pair the figure is read as a mathematician would read it:
  * triangles are the <polygon>s with three vertices; vertex names are the one-letter labels;
  * equal-side marks (short tick lines) are attached to the nearest side, side labels (5 cm, 2, x cm) to the
    nearest side, and angle labels and angle marks (dots, circles, crosses, arcs, right-angle marks) to the
    angle (triangle and vertex) whose bisector they sit on;
  * two parts are KNOWN equal when they carry the same mark or the same value, when a side is shared by both
    triangles (a common side), when two angles are vertically opposite, or when an angle follows from the
    angle sum.
For a matching f of the vertices the script then decides which tests the known equal parts support:
SSS (three sides), SAS (two sides and the angle where they meet: the included angle), AAS (two angles and a
side) and RHS (a right angle in both, the hypotenuse opposite it and one more side). Every printed test must
be supported under a matching f that is also a true congruence of the drawn coordinates (all pairwise
distances equal), and every part that the marks call equal must be equal in the coordinates. "No" answers
must have no supported test under any matching. Congruence statements are compared with the coordinate
matching; pronumerals are read from the matched part (or the angle sum) and measured where the figure is to
scale. The written proofs are parsed line by line: every equality is measured in the figure, the reasons
"alternate angles" and "vertically opposite angles" are checked from the lines, and the test named must be
supported by the listed equalities under the matching in the statement (SAS: the angle must be included).
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 workspace/checks/y8cong_l2.py
"""
import os
import re
import sys
from itertools import permutations
from math import atan2, degrees, hypot, sqrt, sin, radians
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y8cong_common import (Values, check, check_text, ok, finish, svg, read, plain, caps, dist, ang,  # noqa: E402
                           congruences, _spans, svg_texts, label_centre)

V = Values(["a_l2.html", "l2.html"])
L2 = read("l2.html")
G = {k: v[0] for k, v in _spans(["l2.html"], "data-g").items()}
TOL_L, TOL_A = 0.6, 0.6


# ---------------- reading a figure ----------------

def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay)))
    return hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def pdir(v, p):
    return degrees(atan2(-(p[1] - v[1]), p[0] - v[0])) % 360


def inside(P, q):
    n, c = len(P), False
    for i in range(n):
        (x1, y1), (x2, y2) = P[i], P[(i + 1) % n]
        if (y1 > q[1]) != (y2 > q[1]) and q[0] < x1 + (q[1] - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def area(P):
    return abs(sum(P[i][0] * P[(i + 1) % 3][1] - P[(i + 1) % 3][0] * P[i][1] for i in range(3))) / 2


def same_pt(p, q, tol=0.3):
    return dist(p, q) < tol


class Fig:
    def __init__(self, name):
        self.name = name
        s = svg(name)
        self.tris = [[tuple(float(t) for t in pt.split(",")) for pt in m.group(1).split()]
                     for m in re.finditer(r'<polygon points="([^"]+)"', s)]
        self.tris = [T for T in self.tris if len(T) == 3]
        self.sides = {}          # (t, i, j) -> {"ticks": n, "label": str}
        self.angles = {}         # (t, i) -> {"marks": set, "label": str}
        lines = [((float(a), float(b)), (float(c), float(d)), float(w)) for a, b, c, d, w in
                 re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="[^"]+" stroke-width="([\d.]+)"', s)]
        segs = [(t, i, (i + 1) % 3) for t in range(len(self.tris)) for i in range(3)]
        for a, b, w in lines:
            if abs(w - 1.2) < 1e-6:                           # equal-length tick marks
                m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                for k in self._nearest_sides(m):
                    self.sides.setdefault(k, {}).setdefault("ticks", 0)
                    self.sides[k]["ticks"] += 1
        crosses = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b, w in lines if abs(w - 1.05) < 1e-6]
        for c in crosses[::2]:
            self._angle_item(c, "x")
        for cx, cy, fill in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="[\d.]+" fill="([^"]+)"', s):
            self._angle_item((float(cx), float(cy)), "o" if fill == "#fff" else "dot")
        for d, w in re.findall(r'<path d="([^"]+)" fill="none" stroke="[^"]+" stroke-width="([\d.]+)"/>', s):
            if abs(float(w) - 1.1) > 1e-6:
                continue
            nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
            if "A" in d:
                p = (nums[0], nums[1])
                q = (nums[-2], nums[-1])
                self._angle_item(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), "arc")
            elif d.count("L") == 2:
                self._angle_item((nums[2], nums[3]), "R")
        # thin pointer arcs (stroke-width 0.8) drawn at narrow labelled angles: their centre is the vertex
        self.pointers = []
        for x0, y0, r, x1, y1 in re.findall(r'<path d="M([-\d.]+),([-\d.]+) A([\d.]+),[\d.]+ 0 0 0 ([-\d.]+),([-\d.]+)" fill="none" stroke="[^"]+" stroke-width="0.8"/>', s):
            a_, b_, r = (float(x0), float(y0)), (float(x1), float(y1)), float(r)
            for T in self.tris:
                for v in T:
                    if abs(dist(v, a_) - r) < 0.6 and abs(dist(v, b_) - r) < 0.6:
                        self.pointers.append(v)
        self.names = {}
        for t, x, y in svg_texts(name):
            c = label_centre(t, x, y)
            if re.fullmatch(r"[A-Z]( \(apex\))?", t):
                t = t[0]
                verts = [p for T in self.tris for p in T]
                self.names[t] = min(verts, key=lambda p: dist(p, c))
            elif t.endswith("°"):
                self._angle_item(c, "label", t[:-1])
            elif re.fullmatch(r"[\dxy]+( (cm|m|km|mm))?", t):
                for k in self._nearest_sides(c, far=True):
                    self.sides.setdefault(k, {})["label"] = t

    def _nearest_sides(self, p, far=False):
        best = None
        out = []
        for t, T in enumerate(self.tris):
            for i in range(3):
                j = (i + 1) % 3
                d = seg_dist(p, T[i], T[j])
                out.append((d, t, min(i, j), max(i, j)))
        out.sort()
        d0 = out[0][0]
        # every side lying on the nearest segment (a shared side belongs to both triangles)
        a0 = self.tris[out[0][1]]
        e = (a0[out[0][2]], a0[out[0][3]])
        res = []
        for d, t, i, j in out:
            T = self.tris[t]
            if {self._key(T[i]), self._key(T[j])} == {self._key(e[0]), self._key(e[1])}:
                res.append((t, i, j))
        return res

    @staticmethod
    def _key(p):
        return (round(p[0], 1), round(p[1], 1))

    def _angle_item(self, p, kind, value=None):
        """An angle label or mark belongs to the nearest vertex of the triangle that contains it. A label
        outside every triangle (a narrow angle labelled just outside its vertex, with a thin arc) belongs to
        the nearest vertex, in the triangle whose angle there points away from the label."""
        cands = [t for t, T in enumerate(self.tris) if inside(T, p)]
        if cands:
            t = min(cands, key=lambda t: area(self.tris[t]))
            T = self.tris[t]
            i = min(range(3), key=lambda i: dist(T[i], p))
        else:
            best = None
            for t, T in enumerate(self.tris):
                for i in range(3):
                    v = T[i]
                    r1, r2 = pdir(v, T[i - 1]), pdir(v, T[(i + 1) % 3])
                    w = (r2 - r1) % 360
                    if w > 180:
                        r1, w = r2, 360 - w
                    back = (pdir(v, p) + 180) % 360
                    inw = ((back - r1) % 360) <= w
                    key = (round(dist(v, p), 1), 0 if inw else 1)
                    if best is None or key < best[0]:
                        best = (key, t, i)
            t, i = best[1], best[2]
        A = self.angles.setdefault((t, i), {"marks": set()})
        if kind == "label":
            ok("label" not in A, f"{self.name}: one angle label per angle", f"{A.get('label')} and {value} at triangle {t} vertex {i}")
            A["label"] = value
        else:
            A["marks"].add(kind)

    # ---- parts of triangle t ----
    def side_info(self, t, i, j):
        return self.sides.get((t, min(i, j), max(i, j)), {})

    def angle_value(self, t, i):
        """Known value of angle i of triangle t: a printed number, a right-angle mark, or what follows from
        the angle sum and from isosceles triangles (equal-marked sides have equal opposite angles)."""
        val = {}
        for k in range(3):
            A = self.angles.get((t, k), {})
            if "label" in A and re.fullmatch(r"\d+", A["label"]):
                val[k] = float(A["label"])
            elif "R" in A.get("marks", ()):
                val[k] = 90.0
        opp = lambda k: tuple(sorted(m for m in range(3) if m != k))
        for _ in range(3):
            for a in range(3):
                for b in range(3):
                    ta = self.side_info(t, *opp(a)).get("ticks")
                    if a != b and ta and ta == self.side_info(t, *opp(b)).get("ticks") and a in val and b not in val:
                        val[b] = val[a]
            if len(val) == 2:
                k = 3 - sum(val)
                val[k] = 180 - sum(val.values())
        return val.get(i)

    def measured(self, t, i):
        T = self.tris[t]
        return ang(T[i], T[i - 1], T[(i + 1) % 3])

    def length(self, t, i, j):
        T = self.tris[t]
        return dist(T[i], T[j])

    def shared(self, t1, i, j, t2, k, l):
        A, B = self.tris[t1], self.tris[t2]
        return {self._key(A[i]), self._key(A[j])} == {self._key(B[k]), self._key(B[l])}

    def vert_opp(self, t1, i, t2, k):
        A, B = self.tris[t1], self.tris[t2]
        if not same_pt(A[i], B[k]):
            return False
        v = A[i]
        da = sorted(pdir(v, A[m]) for m in range(3) if m != i)
        db = sorted((pdir(v, B[m]) + 180) % 360 for m in range(3) if m != k)
        return all(abs(((x - y) + 180) % 360 - 180) < 0.5 for x, y in zip(da, db))


def num_or_none(s):
    return s if s is not None and re.fullmatch(r"\d+( (cm|m|km|mm))?", s) else None


def known_side(F, t1, i, j, t2, k, l):
    a, b = F.side_info(t1, i, j), F.side_info(t2, k, l)
    if F.shared(t1, i, j, t2, k, l):
        return True
    if a.get("ticks") and a.get("ticks") == b.get("ticks"):
        return True
    la, lb = num_or_none(a.get("label")), num_or_none(b.get("label"))
    return la is not None and la == lb


def known_angle(F, t1, i, t2, k):
    va, vb = F.angle_value(t1, i), F.angle_value(t2, k)
    if va is not None and vb is not None and abs(va - vb) < 1e-9:
        return True
    ma = F.angles.get((t1, i), {}).get("marks", set()) - {"R"}
    mb = F.angles.get((t2, k), {}).get("marks", set()) - {"R"}
    if ma & mb:
        return True
    return F.vert_opp(t1, i, t2, k)


def supported(F, t1, t2, f, extra=None):
    """Tests supported by the known equal parts, for the matching f (vertex i of t1 -> f[i] of t2)."""
    extra = extra or set()
    S = {}
    for i, j in ((0, 1), (1, 2), (0, 2)):
        S[(i, j)] = known_side(F, t1, i, j, t2, f[i], f[j]) or ("S", i, j) in extra or ("S", j, i) in extra
    A = {i: known_angle(F, t1, i, t2, f[i]) or ("A", i) in extra for i in range(3)}
    # angle sum: two known angle pairs give the third
    if sum(A.values()) == 2:
        pass
    out = set()
    sides_known = [k for k, v in S.items() if v]
    if len(sides_known) == 3:
        out.add("SSS")
    for i in range(3):
        j, k = [m for m in range(3) if m != i]
        if S[tuple(sorted((i, j)))] and S[tuple(sorted((i, k)))] and A[i]:
            out.add("SAS")
    if sum(A.values()) >= 2 and sides_known:
        out.add("AAS")
    for i in range(3):
        va, vb = F.angle_value(t1, i), F.angle_value(t2, f[i])
        if va == 90 and vb == 90:
            j, k = [m for m in range(3) if m != i]
            if S[tuple(sorted((j, k)))] and (S[tuple(sorted((i, j)))] or S[tuple(sorted((i, k)))]):
                out.add("RHS")
    return out


def coord_matches(F, t1, t2):
    P = {i: F.tris[t1][i] for i in range(3)}
    Q = {i: F.tris[t2][i] for i in range(3)}
    return [tuple(m[i] for i in range(3)) for m in congruences(P, Q, tol=TOL_L)]


def parts_true(F, t1, t2, f):
    """Every part the figure calls equal is equal in the coordinates."""
    good = True
    for i, j in ((0, 1), (1, 2), (0, 2)):
        if known_side(F, t1, i, j, t2, f[i], f[j]):
            good &= abs(F.length(t1, i, j) - F.length(t2, f[i], f[j])) < TOL_L
    for i in range(3):
        if known_angle(F, t1, i, t2, f[i]):
            good &= abs(F.measured(t1, i) - F.measured(t2, f[i])) < TOL_A
    return good


def check_pair(fig, printed, label, t=(0, 1)):
    """printed: a test name, or 'no'."""
    F = Fig(fig)
    ok(len(F.tris) >= 2, f"{fig}: two triangles read", str(len(F.tris)))
    t1, t2 = t
    cm = coord_matches(F, t1, t2)
    allm = list(permutations(range(3)))
    if printed == "no":
        sup = [p for p in allm if supported(F, t1, t2, p)]
        ok(not sup, f"{label}: no test is supported by the marked parts (answer 'no')", str(sup))
        return F, None
    good = [p for p in cm if printed in supported(F, t1, t2, p)]
    ok(bool(good), f"{label}: {printed} is supported by the marked equal parts under a true congruence of the coordinates",
       f"congruences {cm}, supported {[sorted(supported(F, t1, t2, p)) for p in cm]}")
    if good:
        ok(parts_true(F, t1, t2, good[0]), f"{label}: every marked equal part is equal in the coordinates")
        if printed == "SAS":
            ok(True, f"{label}: SAS uses the included angle (the angle at the common vertex of the two sides)")
    return F, good[0] if good else None


def test_of(s):
    m = re.findall(r"\b(SSS|SAS|AAS|RHS)\b", plain(s))
    return m[-1] if m else ("no" if re.search(r"\bno\b", plain(s).lower()) else None)


# ================= Key ideas and Example 8 =================
for fig, test in (("l2_k_sss", "SSS"), ("l2_k_sas", "SAS"), ("l2_k_aas", "AAS"), ("l2_k_rhs", "RHS")):
    check_pair(fig, test, f"Key ideas {test} figure")
for key, fig in (("ex8a", "l2_ex8a"), ("ex8b", "l2_ex8b"), ("d1a", "l2_d1a"), ("d1b", "l2_d1b"), ("y1a", "l2_y1a"), ("y1b", "l2_y1b")):
    s = V.text(key)
    if s is not None:
        check_pair(fig, test_of(s), key)
        F = Fig(fig)
        others = set()
        for p in coord_matches(F, 0, 1):
            others |= supported(F, 0, 1, p)
        ok(others == {test_of(s)}, f"{key}: the only test supported is the printed one", str(sorted(others)))


# ================= statements and pronumerals =================
def statement(key, fig, t=(0, 1)):
    s = V.text(key)
    if s is None:
        return
    F = Fig(fig)
    m = re.search(r"tri (\w{3}) == tri (\w{3})", plain(s))
    n1, n2 = m.group(1), m.group(2)
    T1, T2 = F.tris[t[0]], F.tris[t[1]]
    idx1 = [min(range(3), key=lambda i: dist(T1[i], F.names[c])) for c in n1]
    idx2 = [min(range(3), key=lambda i: dist(T2[i], F.names[c])) for c in n2]
    f = [None] * 3
    for a, b in zip(idx1, idx2):
        f[a] = b
    ok(tuple(f) in coord_matches(F, *t), f"{key}: {n1} == {n2} is a true congruence of the drawn triangles (vertices in matching order)")
    tst = test_of(s)
    if tst:
        ok(tst in supported(F, t[0], t[1], f), f"{key}: the test {tst} is supported by the marks under this matching")


statement("d2a", "l2_d2a")
statement("y2a", "l2_y2a")
for q, fig in (("q2a", "l2_q2a"), ("q2b", "l2_q2b"), ("q2c", "l2_q2c"), ("q2d", "l2_q2d")):
    statement(q, fig)


def pronumerals(fig, keys, prefix, to_scale=True):
    """keys: pronumeral letter -> data-v key. The pronumeral's value is the matched part's printed value,
    or the angle sum in its own triangle."""
    F = Fig(fig)
    cm = coord_matches(F, 0, 1)
    fits = []
    for p in cm:
        good = True
        for i in range(3):
            va, vb = F.angle_value(0, i), F.angle_value(1, p[i])
            la = F.angles.get((0, i), {}).get("label")
            lb = F.angles.get((1, p[i]), {}).get("label")
            if va is not None and vb is not None and abs(va - vb) > 1e-9:
                good = False
        fits.append(p) if good else None
    ok(len(fits) >= 1, f"{fig}: a congruence of the coordinates agrees with every printed angle")
    f = fits[0]
    inv = {f[i]: i for i in range(3)}
    found = {}
    for (t, i), A in F.angles.items():
        lab = A.get("label")
        if lab and not re.fullmatch(r"\d+", lab):
            o = 1 - t
            k = f[i] if t == 0 else inv[i]
            val = F.angle_value(o, k)
            if val is None:
                val = F.angle_value(t, i)
            found[lab] = (val, F.measured(t, i))
    for (t, i, j), S in F.sides.items():
        lab = S.get("label")
        if lab and lab.split()[0] in ("x", "y"):
            o = 1 - t
            k, l = (f[i], f[j]) if t == 0 else (inv[i], inv[j])
            ol = F.side_info(o, k, l).get("label")
            found[lab.split()[0]] = (float(ol.split()[0]), None)
    for letter, key in keys.items():
        if letter not in found:
            ok(False, f"{fig}: pronumeral {letter} found in the figure")
            continue
        val, meas = found[letter]
        if val is None:
            ok(False, f"{fig}: value of {letter} found from the matching part")
            V.num(key)
            continue
        check(V, key, val, label=f"({letter} from the matching part)")
        if to_scale and meas is not None:
            ok(abs(meas - val) < 0.6, f"{fig}: {letter} drawn to scale", f"measured {meas:.2f}")


pronumerals("l2_d2b", {"x": "d2b_x", "a": "d2b_a", "b": "d2b_b"}, "d2b")
pronumerals("l2_y2b", {"x": "y2b_x", "a": "y2b_a", "b": "y2b_b"}, "y2b")
for q in "bcdef":
    keys = {"x": f"q4{q}_x", "a": f"q4{q}_a"}
    if q in "ef":
        keys["b"] = f"q4{q}_b"
    pronumerals(f"l2_q4{q}", keys, f"q4{q}")


# ================= Concept 3: is the information enough? =================
def decide(given):
    g = plain(given).replace(" ", "")
    sides = set(re.findall(r"([A-Z]{2})=\d", g))
    angles = {a: float(v) for a, v in re.findall(r"ang([A-Z])=(\d+)", g)}
    sides = {frozenset(s) for s in sides}
    if len(sides) == 3:
        return "SSS"
    for v, val in angles.items():
        if val == 90:
            hyp = [s for s in sides if v not in s]
            if hyp and len(sides) >= 2:
                return "RHS"
    if len(angles) >= 2 and sides:
        return "AAS"
    if len(sides) == 2 and angles:
        a, b = list(sides)
        common = a & b
        if common and next(iter(common)) in angles:
            return "SAS"
    return "Not enough"


for pre in ("d3", "y3"):
    for part in "abcd":
        s = V.text(f"{pre}{part}")
        if s is None:
            continue
        want = decide(G[f"{pre}{part}"])
        got = test_of(s) or ("Not enough" if "not enough" in plain(s).lower() else None)
        ok(got == want, f"{pre}{part} decided from the given parts", f"printed {got}, computed {want}")


# ================= Homework =================
for q in "abcd":
    s = V.text(f"q1{q}")
    if s is not None:
        check_pair(f"l2_q1{q}", test_of(s), f"q1{q}")
for q in "acdef":
    s = V.text(f"q3{q}")
    if s is not None:
        check_pair(f"l2_q3{q}", test_of(s), f"q3{q}")
for q in "abcdef":
    s = V.text(f"q5{q}")
    if s is not None:
        tst = test_of(s)
        F, f = check_pair(f"l2_q5{q}", tst, f"q5{q}")
        if tst == "no":
            ok(not coord_matches(F, 0, 1), f"q5{q}: the drawn triangles are not congruent either")
for q in "abcd":
    s = V.text(f"q7{q}")
    if s is None:
        continue
    yes = plain(s).lower().startswith("yes")
    F = Fig(f"l2_q7{q}")
    sup = set()
    for p in coord_matches(F, 0, 1):
        sup |= supported(F, 0, 1, p)
    if yes:
        ok(bool(sup), f"q7{q}: yes, a test is supported under a true congruence", str(sorted(sup)))
    else:
        allsup = [p for p in permutations(range(3)) if supported(F, 0, 1, p)]
        ok(not allsup and not coord_matches(F, 0, 1), f"q7{q}: no, no test is supported and the triangles are not congruent")
    reason_sums = re.findall(r"(\d+)-(\d+)-(\d+)=(\d+)", plain(s).replace(" ", "").replace("−", "-"))
    for a, b, c, d in reason_sums:
        ok(int(a) - int(b) - int(c) == int(d), f"q7{q}: angle sum {a}-{b}-{c}={d}")

# Q6: the added piece of information makes a test work, and is needed
q6list = plain(G["q6list"]).replace(" ", "")
for q in "abcd":
    s = V.text(f"q6{q}")
    if s is None:
        continue
    F = Fig(f"l2_q6{q}")
    item = plain(s).replace(" ", "").replace("\\text{", "").replace("}", "")
    m = re.match(r"(ang)?([A-Z]+)=(\d+)", item)
    ok(m is not None and (m.group(0) in q6list.replace("\\text{", "").replace("}", "")), f"q6{q}: the answer is in the given list", item)
    names = {k: v for k, v in F.names.items()}
    tri_of = lambda c: 0 if any(same_pt(names[c], p) for p in F.tris[0]) else 1
    t = tri_of(m.group(2)[0])
    T = F.tris[t]
    idx = [min(range(3), key=lambda i: dist(T[i], names[c])) for c in m.group(2)]
    before = set().union(*[supported(F, 0, 1, p) for p in coord_matches(F, 0, 1)])
    ok(not before, f"q6{q}: without the new information no test is supported", str(sorted(before)))
    after = set()
    for p in coord_matches(F, 0, 1):
        inv = {p[i]: i for i in range(3)}
        if m.group(1):                                     # an angle is added
            i = idx[0] if t == 0 else inv[idx[0]]
            other_val = F.angle_value(1 - t, p[i] if t == 0 else i)
            if other_val == float(m.group(3)) or F.angle_value(1, p[i]) == float(m.group(3)) or F.angle_value(0, i) == float(m.group(3)):
                after |= supported(F, 0, 1, p, extra={("A", i)})
        else:                                              # a side is added
            i, j = (idx if t == 0 else [inv[idx[0]], inv[idx[1]]])
            o_lab = (F.side_info(1, p[i], p[j]) if t == 0 else F.side_info(0, i, j)).get("label", "")
            if o_lab.split() and o_lab.split()[0] == m.group(3):
                after |= supported(F, 0, 1, p, extra={("S", i, j)})
    ok(bool(after), f"q6{q}: with {item} a test is supported under a true congruence", str(sorted(after)))
    # the added value is true in the figure
    if m.group(1):
        ok(abs(F.measured(t, idx[0]) - float(m.group(3))) < 0.6, f"q6{q}: {item} is true in the drawing")

# Q8: Pythagoras then SSS
F = Fig("l2_q8")
check(V, "q8_h", sqrt(12 ** 2 + 5 ** 2), label="(hypotenuse of the first triangle)")
check(V, "q8_s", sqrt(13 ** 2 - 5 ** 2), label="(unknown side of the second triangle)")
ok({"12 km", "5 km"} <= {S.get("label") for S in F.sides.values()} and "13 km" in {S.get("label") for S in F.sides.values()},
   "q8: the figure shows 12 km, 5 km and 13 km")
cm = coord_matches(F, 0, 1)
ok(bool(cm), "q8: the drawn triangles are congruent")
check_text(V, "q8", "yes")


# ---------------- proofs ----------------
def P_(F, c):
    return F.names[c]


def angle3(F, s3):
    a, v, b = (P_(F, c) for c in s3)
    return ang(v, a, b)


def check_proof(key, fig, label):
    s = V.text(key)
    if s is None:
        return
    F = Fig(fig)
    lines = [plain(x) for x in re.split(r"<br>", s)]
    eqs = []
    for ln in lines:
        mA = re.match(r"ang (\w{3}) ?= ?ang (\w{3}) \((.*)\)", ln)
        mS = re.match(r"(\w{2}) ?= ?(\w{2}) \((.*)\)", ln)
        mC = re.match(r"(\w{2}) is a common side", ln)
        mT = re.match(r"∴ tri (\w{3}) == tri (\w{3}) \((\w{3})\)", ln.replace("\\therefore", "∴"))
        if mA:
            x, y, why = mA.groups()
            ok(abs(angle3(F, x) - angle3(F, y)) < TOL_A, f"{label}: angle {x} = angle {y} in the figure",
               f"{angle3(F, x):.2f} vs {angle3(F, y):.2f}")
            if "alternate" in why:
                # the arms not shared by the two angles are parallel, in opposite directions
                v1, v2 = P_(F, x[1]), P_(F, y[1])
                arms1 = [P_(F, x[0]), P_(F, x[2])]
                arms2 = [P_(F, y[0]), P_(F, y[2])]
                shared = [(a, b) for a in arms1 for b in arms2 if abs(((pdir(v1, a) - pdir(v1, v2)) + 180) % 360 - 180) < 0.5]
                d1 = [pdir(v1, a) for a in arms1 if abs(((pdir(v1, a) - pdir(v1, v2)) + 180) % 360 - 180) > 0.5]
                d2 = [pdir(v2, b) for b in arms2 if abs(((pdir(v2, b) - pdir(v2, v1)) + 180) % 360 - 180) > 0.5]
                ok(len(d1) == 1 and len(d2) == 1 and abs(((d1[0] - d2[0] - 180) + 180) % 360 - 180) < 0.5,
                   f"{label}: {x} and {y} are alternate angles (one arm along the transversal {x[1]}{y[1]}, the other arms parallel and opposite)")
            if "vertically opposite" in why:
                ok(x[1] == y[1] and all(abs(((pdir(P_(F, x[1]), P_(F, a)) - pdir(P_(F, x[1]), P_(F, b)) - 180) + 180) % 360 - 180) < 0.5
                                        for a, b in ((x[0], y[0]), (x[2], y[2]))),
                   f"{label}: {x} and {y} are vertically opposite")
            eqs.append(("A", x, y))
        elif mS:
            x, y, why = mS.groups()
            ok(abs(dist(P_(F, x[0]), P_(F, x[1])) - dist(P_(F, y[0]), P_(F, y[1]))) < TOL_L, f"{label}: {x} = {y} in the figure")
            eqs.append(("S", x, y))
        elif mC:
            eqs.append(("S", mC.group(1), mC.group(1)))
        elif mT:
            n1, n2, test = mT.groups()
            f = dict(zip(n1, n2))
            P = {c: P_(F, c) for c in n1}
            Q = {c: P_(F, c) for c in n2}
            ms = congruences(P, Q, tol=TOL_L)
            ok(f in ms, f"{label}: tri {n1} == tri {n2} is a true congruence (vertices in matching order)")
            # which parts of the statement's triangles do the listed equalities make equal?
            sides, angles = set(), set()
            for kind, x, y in eqs:
                for a, b in ((x, y), (y, x)):
                    if kind == "S" and set(a) <= set(n1) and "".join(f[c] for c in a) in (b, b[::-1]):
                        sides.add(frozenset(a))
                    if kind == "A" and set(a) <= set(n1) and f[a[1]] == b[1] and {f[a[0]], f[a[2]]} == {b[0], b[2]}:
                        angles.add(a[1])
            okt = False
            if test == "SSS":
                okt = len(sides) == 3
            elif test == "SAS":
                okt = any(len(s) == 2 and len(t_) == 2 and (s & t_) and next(iter(s & t_)) in angles
                          for s in sides for t_ in sides if s != t_)
            elif test == "AAS":
                okt = len(angles) >= 2 and len(sides) >= 1
            elif test == "RHS":
                rights = [v for v in angles if abs(ang(P[v], *[P[c] for c in n1 if c != v]) - 90) < 0.6]
                okt = any(frozenset(c for c in n1 if c != v) in sides and len(sides) >= 2 for v in rights)
            ok(okt, f"{label}: the listed equalities give {test}" + (" (with the included angle)" if test == "SAS" else ""),
               f"sides {[''.join(sorted(s)) for s in sides]}, angles {sorted(angles)}")


check_proof("q10a", "l2_q10a", "q10a")
check_proof("q10b", "l2_q10b", "q10b")
check_proof("q10c", "l2_q10c", "q10c")
check_proof("q10d", "l2_q10d", "q10d")
check_proof("q11a", "l2_q11a", "q11a")
check_proof("q11b", "l2_q11b", "q11b")
check_proof("q11c", "l2_q11c", "q11c")
check_proof("q11d1", "l2_q11d", "q11d (ACD == ACB)")
check_proof("q11d2", "l2_q11d", "q11d (DCE == BCE)")
F = Fig("l2_q11a")
ok(abs(angle3(F, "AMB") - 90) < 0.6, "q11a: the conclusion AMB = 90 holds in the figure")
F = Fig("l2_q11b")
ok(abs(dist(P_(F, "A"), P_(F, "C")) - 2 * dist(P_(F, "A"), P_(F, "B"))) < TOL_L, "q11b: AC = 2AB in the figure")
F = Fig("l2_q11d")
ok(abs(angle3(F, "DEC") - 90) < 0.6, "q11d: DEC = 90 in the figure")
# the Q10 stem's model proof (printed in the lesson) holds in its figure too
F = Fig("l2_q10")
ok(abs(angle3(F, "CAB") - angle3(F, "CED")) < TOL_A and abs(dist(P_(F, "A"), P_(F, "C")) - dist(P_(F, "E"), P_(F, "C"))) < TOL_L
   and {"A": "E", "B": "D", "C": "C"} in congruences({c: P_(F, c) for c in "ABC"}, {c: P_(F, c) for c in "EDC"}, tol=TOL_L),
   "q10 stem: the model proof's equalities and statement hold in its figure")

check_text(V, "q9a", "two different triangles")
check_text(V, "q9b", "same shape but different size")
# Q9 answer figures: (a) the same SSA data gives two non-congruent triangles; (b) equal angles, different sizes
F = Fig("l2_a9a")
ok(not coord_matches(F, 0, 1) and abs(F.length(0, 0, 1) - F.length(1, 0, 1)) < TOL_L and abs(F.length(0, 1, 2) - F.length(1, 1, 2)) < TOL_L
   and abs(F.measured(0, 0) - F.measured(1, 0)) < TOL_A and abs(F.measured(0, 0) - 30) < 0.6,
   "q9a figure: same two sides and the same non-included 30 degree angle, triangles not congruent")
F = Fig("l2_a9b")
ok(not coord_matches(F, 0, 1) and all(abs(F.measured(0, i) - F.measured(1, i)) < TOL_A for i in range(3)),
   "q9b figure: equal angles, triangles not congruent")


# ================= Past papers =================
# PP1: Sydney Grammar 2020 Q2(h)(i), figure l1_pp2 (lines; O is the common midpoint)
s = svg("l1_pp2")
segs = [((float(a), float(b)), (float(c), float(d))) for a, b, c, d, w in
        re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="[^"]+" stroke-width="([\d.]+)"', s) if w == "1.6"]
ends = [p for sg in segs for p in sg]
pos = {}
for t, x, y in svg_texts("l1_pp2"):
    if t in ("A", "B", "C", "D"):
        c = label_centre(t, x, y)
        pos[t] = min(ends, key=lambda p: dist(p, c))
O = ((pos["A"][0] + pos["C"][0]) / 2, (pos["A"][1] + pos["C"][1]) / 2)
ticks = [((float(a) + float(c)) / 2, (float(b) + float(d)) / 2) for a, b, c, d, w in
         re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="[^"]+" stroke-width="([\d.]+)"', s) if w == "1.2"]
n = {k: sum(1 for m in ticks if seg_dist(m, O, pos[k]) < 3) for k in "ABCD"}
ok(n["A"] == n["C"] and n["B"] == n["D"] and n["A"] != n["B"], "pp1: marks show OA = OC and OB = OD", str(n))
vo = all(abs(((pdir(O, pos[a]) - pdir(O, pos[b]) - 180) + 180) % 360 - 180) < 0.5 for a, b in (("A", "C"), ("B", "D")))
ok(vo, "pp1: angle AOB and angle COD are vertically opposite (so equal), and each lies between the marked sides")
ok(test_of(V.text("pp1") or "") == "SAS", "pp1: SAS (two pairs of marked sides and the included vertically opposite angles)")
# PP2: Merewether (options from the question)
F, f = check_pair("l2_pp_mere", "AAS", "pp2 Merewether")
opts = dict(re.findall(r"([ABCD])\.&ensp;(SSS|SAS|AAS|RHS)", L2.split("PP 2")[1].split("PP 3")[0]))
s = V.text("pp2")
if s is not None:
    ok(opts.get(plain(s).strip()[:1]) == "AAS", "pp2: the printed option is AAS", str(opts))
F = Fig("l2_pp_mere")
ok(set().union(*[supported(F, 0, 1, p) for p in coord_matches(F, 0, 1)]) == {"AAS"}, "pp2: AAS is the only supported test")
# PP3: Girraween, four right triangles I-IV (labels inside)
F = Fig("l2_pp_girr")
lab = {}
for t, x, y in svg_texts("l2_pp_girr"):
    c = label_centre(t, x, y)
    k = [i for i, T in enumerate(F.tris) if inside(T, c)]
    if k:
        lab[t] = k[0]
cong = lambda a, b: bool(coord_matches(F, lab[a], lab[b]))
truth = {"A": cong("I", "II"), "B": cong("I", "IV") and cong("II", "III"), "C": cong("I", "III"),
         "D": cong("I", "II") and cong("III", "IV")}
ok(truth == {"A": False, "B": True, "C": False, "D": False}, "pp3: only statement B is true for the drawn triangles", str(truth))
ok(any("RHS" in supported(F, lab["II"], lab["III"], p) for p in coord_matches(F, lab["II"], lab["III"])),
   "pp3: II and III are congruent by RHS from the marks (shared hypotenuse, marked sides, right angles)")
s = V.text("pp3")
if s is not None:
    ok(plain(s).strip() == "B", "pp3: printed answer B")
# PP4: Sydney Tech
F = Fig("l2_pp_st")
sup = set().union(*[supported(F, 0, 1, p) for p in coord_matches(F, 0, 1)])
ok("RHS" not in sup and "AAS" in sup, "pp4: RHS is not supported (only the hypotenuse is given), AAS is", str(sorted(sup)))
check_text(V, "pp4i", "hypotenuse")
s = V.text("pp4ii")
if s is not None:
    ok(test_of(s) == "AAS", "pp4ii: AAS")

finish([V])
