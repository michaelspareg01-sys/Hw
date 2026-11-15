"""Triangle-pair reader shared by the Lesson 3 check: a copy of the figure reader and test logic of
y8cong_l2.py (unchanged), kept as a module so it can be imported without running the Lesson 2 checks.

A figure's triangles are its 3-point <polygon>s; tick marks (width 1.2) go to the nearest side, angle marks and
labels to the angle they sit in; supported() lists the tests (SSS, SAS with the included angle, AAS, RHS) that
the marked equal parts give for a matching of the vertices; check_pair() also requires the matching to be a true
congruence of the coordinates.
"""
import re
from itertools import permutations
from math import atan2, degrees, hypot
from y8cong_common import ok, svg, svg_texts, label_centre, dist, ang, congruences, plain

TOL_L, TOL_A = 0.6, 0.6


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


