r"""Check of Lesson 3 (8H Using congruent triangles to establish properties of quadrilaterals) and the
Chapter 8 review, tied to the printed HTML and the figures.

Reads build/y8cong/a_l3.html and l3.html (answers in <span data-v> / <span data-k>) and the figures svg/l3_*.svg.

Named figures are read as a mathematician reads them: the drawn segments are the <line>s of width 1.5 (and the
dashed lines of width 1.0); the points are the segment ends and the crossing points of segments; each one-letter
label names the nearest point. Equal-length ticks (lines of width 1.2) belong to the segment they cross, parallel
arrows (paths of width 1.3) to the segment they sit on, and angle marks (dots, circles, crosses, arcs, right-angle
marks) to the angle whose arms enclose them.

Every written proof is parsed line by line:
  * every equality (sides, angles, or an angle equal to 90 degrees) is measured in the figure;
  * the reasons are checked: "given" needs matching marks in the figure (same number of ticks, the same angle
    mark) or a fact stated in the question; "common" needs one segment; "alternate angles" needs one arm along
    the joining transversal and the other arms parallel and pointing opposite ways (and any named parallel lines
    really are parallel); "vertically opposite" needs the arms to be opposite rays; "radii" needs segments from
    the circle's centre to the circle;
  * the congruence statement must be a true congruence of the drawn triangles with the vertices in matching order,
    and the equalities listed before it must give the named test under that matching (SSS: three sides; SAS: two
    sides and the angle where they meet, the included angle; AAS: two angles and a side; RHS: right angles, the
    sides opposite them, and one more side);
  * every conclusion drawn from the congruence ("matching sides/angles") must be a pair of matching parts under
    the statement's vertex order, and must hold in the figure.
Unnamed triangle pairs (8H Q6, review Q9) use the Lesson 2 reader (y8cong_pairs.py). Numbers are recomputed:
the area in North Sydney Boys Q3(b)(ii) from the drawn square, angle 45 in 8H Q11c, the pronumerals of review
Q10 from the matching parts, and the multiple-choice answers from the figures and the printed options.
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 workspace/checks/y8cong_l3.py
"""
import os
import re
import sys
from itertools import permutations
from math import atan2, degrees, hypot, sqrt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y8cong_common import (Values, check, check_text, ok, finish, svg, read, plain, dist, ang,  # noqa: E402
                           congruences, svg_texts, label_centre)
import y8cong_pairs as PR  # noqa: E402

V = Values(["a_l3.html", "l3.html"])
L3 = read("l3.html")
TOL_L, TOL_A = 0.6, 0.6


# ======================= reading a named figure =======================

def pdir(v, p):
    return degrees(atan2(-(p[1] - v[1]), p[0] - v[0])) % 360


def adiff(a, b):
    return abs(((a - b) + 180) % 360 - 180)


def on_seg(p, a, b, tol=1.0):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L2 = ax * ax + ay * ay
    t = ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2
    if t < -0.01 or t > 1.01:
        return False
    return hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay) < tol


def seg_isect(a, b, c, d):
    den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
    if abs(den) < 1e-9:
        return None
    t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
    u = -((a[0] - b[0]) * (a[1] - c[1]) - (a[1] - b[1]) * (a[0] - c[0])) / den
    if -1e-6 <= t <= 1 + 1e-6 and -1e-6 <= u <= 1 + 1e-6:
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return None


class Scene:
    def __init__(self, name):
        self.name = name
        s = svg(name)
        L = [((float(a), float(b)), (float(c), float(d)), float(w), dash) for a, b, c, d, w, dash in
             re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="[^"]+" stroke-width="([\d.]+)"( stroke-dasharray)?', s)]
        self.segs = [(a, b) for a, b, w, dash in L if abs(w - 1.5) < 1e-6 or (abs(w - 1.0) < 1e-6 and dash)]
        self.dashed = [(a, b) for a, b, w, dash in L if abs(w - 1.0) < 1e-6 and dash]
        for m in re.finditer(r'<polygon points="([^"]+)" fill="none" fill-opacity="0" stroke="#[0-9a-fA-F]+" stroke-width="1.5"', s):
            P = [tuple(float(t) for t in pt.split(",")) for pt in m.group(1).split()]
            self.segs += [(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]
        self.ticks = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b, w, dash in L if abs(w - 1.2) < 1e-6]
        crosses = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b, w, dash in L if abs(w - 1.05) < 1e-6]
        self.marks = [(c, "x") for c in crosses[::2]]
        self.arrows = []
        for d, w in re.findall(r'<path d="([^"]+)" fill="none" stroke="[^"]+" stroke-width="([\d.]+)"', s):
            nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
            if abs(float(w) - 1.3) < 1e-6:
                self.arrows.append((nums[2], nums[3]))
            elif abs(float(w) - 1.1) < 1e-6:
                if "A" in d:
                    self.marks.append((((nums[0] + nums[-2]) / 2, (nums[1] + nums[-1]) / 2), "arc"))
                elif d.count("L") == 2:
                    self.marks.append(((nums[2], nums[3]), "R"))
        for cx, cy, fill in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="[\d.]+" fill="([^"]+)"', s):
            self.marks.append(((float(cx), float(cy)), "o" if fill == "#fff" else "dot"))
        self.circles = []
        for m in re.finditer(r'd="M([-\d.]+),([-\d.]+) A([-\d.]+),[-\d.]+ 0 1 0 ([-\d.]+),[-\d.]+ A', s):
            x0, y, r, x1 = (float(v) for v in m.groups())
            self.circles.append((((x0 + x1) / 2, y), r))
        nodes = [p for sg in self.segs for p in sg]
        for i in range(len(self.segs)):
            for j in range(i + 1, len(self.segs)):
                q = seg_isect(*self.segs[i], *self.segs[j])
                if q:
                    nodes.append(q)
        self.nodes = nodes
        self.P = {}
        for t, x, y in svg_texts(name):
            if re.fullmatch(r"[A-Z]", t):
                c = (x, y - 4.0)
                self.P[t] = min(nodes, key=lambda p: dist(p, c))
        # a dot drawn on a named point marks the point, not an angle
        self.marks = [(c, k) for c, k in self.marks if min(dist(c, p) for p in self.P.values()) > 1.0] if self.P else self.marks

    def p(self, c):
        return self.P[c]

    def length(self, s):
        return dist(self.P[s[0]], self.P[s[1]])

    def angle(self, s):
        a, v, b = (self.P[c] for c in s)
        return ang(v, a, b)

    def drawn(self, s):
        """The segment between the two named points lies along drawn segments."""
        a, b = self.P[s[0]], self.P[s[1]]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return any(on_seg(a, *sg) and on_seg(b, *sg) for sg in self.segs) or \
            any(on_seg(m, *sg) and on_seg(a, *sg, tol=1.0) for sg in self.segs)

    def ticks_on(self, s):
        a, b = self.P[s[0]], self.P[s[1]]
        return sum(1 for t in self.ticks if on_seg(t, a, b, tol=0.8))

    def arrows_on(self, s):
        a, b = self.P[s[0]], self.P[s[1]]
        return sum(1 for t in self.arrows if on_seg(t, a, b, tol=0.8))

    def marks_in(self, s):
        """Angle marks inside the angle s (e.g. 'ABC' at B), within 26 px of the vertex."""
        a, v, b = (self.P[c] for c in s)
        r1, r2 = pdir(v, a), pdir(v, b)
        w = (r2 - r1) % 360
        if w > 180:
            r1, w = r2, 360 - w
        out = set()
        for c, k in self.marks:
            d = dist(c, v)
            if 0.5 < d < 26 and ((pdir(v, c) - r1) % 360) < w - 0.5 and ((pdir(v, c) - r1) % 360) > 0.5:
                out.add(k)
        return out

    def parallel(self, s, t):
        a, b = self.P[s[0]], self.P[s[1]]
        c, d = self.P[t[0]], self.P[t[1]]
        return adiff(pdir(a, b) % 180, pdir(c, d) % 180) < 0.4 or adiff(pdir(a, b) % 180, pdir(c, d) % 180) > 179.6


# ======================= parsing and checking proofs =======================

def tex_plain(s):
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in (("\\angle", "∠"), ("\\triangle", "△"), ("\\Delta", "△"), ("\\equiv", "≡"), ("\\therefore", "∴"),
                 ("\\parallel", "∥"), ("\\perp", "⊥"), ("^\\circ", "°"), ("\\tfrac12", "½"), ("&ensp;", " "), ("&emsp;", " ")):
        s = s.replace(a, b)
    s = re.sub(r"\\[()]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("∠ ", "∠")


TERM = r"(∠ ?[A-Z]{3}|[A-Z]{2}|90°)"


def parse_eq(math):
    """'∠ABC=∠DEF=90°' -> list of equal pairs of terms."""
    terms = [t.strip().replace(" ", "") for t in math.split("=")]
    if not all(re.fullmatch(TERM.replace(" ?", ""), t) for t in terms):
        return None
    return [(terms[i], terms[i + 1]) for i in range(len(terms) - 1)]


def measure(F, t):
    if t == "90°":
        return 90.0
    if t.startswith("∠"):
        return F.angle(t[1:])
    return F.length(t)


def items_of(line):
    """Equalities in a proof line, with the reason (text in the last brackets)."""
    line = line.replace("∴", "").strip()
    m = re.match(r"(.*?)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", line)
    reason = ""
    body = line
    if m:
        body, reason = m.group(1), m.group(2)
    out = []
    body = body.replace("∠ ", "∠")
    T = r"(?:∠[A-Z]{3}|(?<![A-Za-z])[A-Z]{2}(?![A-Za-z])|90°)"
    for m in re.finditer(T + r"(?: ?= ?" + T + r")+", body):
        pe = parse_eq(m.group(0))
        if pe:
            out += pe
    return out, reason


def alternate_ok(F, x, y):
    """x = 'ABC', y = 'DEF' (angles at B and E): one arm of each is along the transversal BE, the other arms
    are parallel and point opposite ways."""
    v1, v2 = F.p(x[1]), F.p(y[1])
    arms1 = [F.p(x[0]), F.p(x[2])]
    arms2 = [F.p(y[0]), F.p(y[2])]
    t12, t21 = pdir(v1, v2), pdir(v2, v1)
    o1 = [pdir(v1, a) for a in arms1 if adiff(pdir(v1, a), t12) > 0.5]
    o2 = [pdir(v2, b) for b in arms2 if adiff(pdir(v2, b), t21) > 0.5]
    on1 = [a for a in arms1 if adiff(pdir(v1, a), t12) <= 0.5]
    on2 = [b for b in arms2 if adiff(pdir(v2, b), t21) <= 0.5]
    return len(o1) == 1 and len(o2) == 1 and len(on1) == 1 and len(on2) == 1 and adiff(o1[0], o2[0]) > 179.5


def vert_opp_ok(F, x, y):
    if x[1] != y[1]:
        return False
    v = F.p(x[1])
    da = sorted(pdir(v, F.p(c)) for c in (x[0], x[2]))
    db = sorted((pdir(v, F.p(c)) + 180) % 360 for c in (y[0], y[2]))
    return all(adiff(a, b) < 0.5 for a, b in zip(da, db))


def same_seg(a, b):
    return set(a) == set(b)


def check_reason(F, label, a, b, reason, givens):
    r = reason.lower()
    if a.startswith("∠") and b.startswith("∠"):
        x, y = a[1:], b[1:]
        if "alternate" in r:
            ok(alternate_ok(F, x, y), f"{label}: {a} and {b} are alternate angles (arms along the transversal {x[1]}{y[1]}, other arms parallel)")
            for p1, p2 in re.findall(r"([A-Z]{2}) ?∥ ?([A-Z]{2})", reason):
                ok(F.parallel(p1, p2), f"{label}: {p1} ∥ {p2} in the figure")
        if "vertically opposite" in r:
            ok(vert_opp_ok(F, x, y), f"{label}: {a} and {b} are vertically opposite")
        if r.startswith("given"):
            m1, m2 = F.marks_in(x), F.marks_in(y)
            ok((m1 & m2) or f"{a}={b}" in givens or f"{b}={a}" in givens,
               f"{label}: given {a} = {b} is shown by matching marks or stated", f"marks {sorted(m1)} / {sorted(m2)}")
    elif b == "90°":
        x = a[1:]
        if r.startswith("given"):
            ok("R" in F.marks_in(x), f"{label}: given {a} = 90 is marked")
    else:
        if "common" in r:
            ok(same_seg(a, b), f"{label}: {a} = {b} is one common segment")
        if r.startswith("given"):
            ta, tb = F.ticks_on(a), F.ticks_on(b)
            ok((ta and ta == tb) or f"{a}={b}" in givens or f"{b}={a}" in givens or f"{a[::-1]}={b}" in givens
               or f"{a}={b[::-1]}" in givens or f"{b}={a[::-1]}" in givens or f"{b[::-1]}={a}" in givens,
               f"{label}: given {a} = {b} is shown by equal ticks or stated in the question", f"ticks {ta}/{tb}")
        if "radii" in r:
            c, rad = F.circles[0]
            okr = all(any(dist(F.p(ch), c) < 1.0 for ch in s) and any(abs(dist(F.p(ch), c) - rad) < 1.0 for ch in s) for s in (a, b))
            ok(okr, f"{label}: {a} and {b} are radii (centre to circle)")


def supported_by(eqs, n1, n2, P):
    """Parts of the triangles n1 -> n2 (vertex order = matching) that the listed equalities make equal."""
    f = dict(zip(n1, n2))
    sides, angles = set(), set()
    for kind, x, y in eqs:
        for a, b in ((x, y), (y, x)):
            if kind == "S" and set(a) <= set(n1) and "".join(f[c] for c in a) in (b, b[::-1]):
                sides.add(frozenset(a))
            if kind == "A" and set(a) <= set(n1) and f[a[1]] == b[1] and {f[a[0]], f[a[2]]} == {b[0], b[2]}:
                angles.add(a[1])
    return sides, angles


def test_holds(test, sides, angles, n1, P):
    if test == "SSS":
        return len(sides) == 3
    if test == "SAS":
        return any(len(s & t) == 1 and next(iter(s & t)) in angles for s in sides for t in sides if s != t)
    if test == "AAS":
        return len(angles) >= 2 and len(sides) >= 1
    if test == "RHS":
        rights = [v for v in angles if abs(ang(P[v], *[P[c] for c in n1 if c != v]) - 90) < 0.6]
        return any(frozenset(c for c in n1 if c != v) in sides and len(sides) >= 2 for v in rights)
    return False


STATEMENTS = {}


def check_proof(key, fig, label=None, givens=(), extra_eqs=(), text=None):
    """Check a printed proof (data-k key) in figure fig. Returns the statement (n1, n2)."""
    label = label or key
    s = text if text is not None else V.text(key)
    if s is None:
        return None
    F = Scene(fig) if isinstance(fig, str) else fig
    givens = {g.replace(" ", "") for g in givens}
    lines = [tex_plain(x) for x in re.split(r"<br>", s)]
    eqs = list(extra_eqs)
    stmt = None
    for ln in lines:
        mT = re.search(r"△ ?([A-Z]{3}) ?≡ ?△ ?([A-Z]{3}) \((SSS|SAS|AAS|RHS)\)", ln)
        mC = re.match(r"([A-Z]{2}) is (a )?common( side)?", ln)
        if mT:
            n1, n2, test = mT.groups()
            P = {c: F.p(c) for c in n1}
            Q = {c: F.p(c) for c in n2}
            f = dict(zip(n1, n2))
            ok(f in congruences(P, Q, tol=TOL_L), f"{label}: △{n1} ≡ △{n2} is a true congruence of the drawn triangles (vertices in matching order)")
            sides, angles = supported_by(eqs, n1, n2, P)
            ok(test_holds(test, sides, angles, n1, P), f"{label}: the listed equal parts give {test}" + (" (with the included angle)" if test == "SAS" else ""),
               f"sides {[''.join(sorted(x)) for x in sides]}, angles at {sorted(angles)}")
            stmt = (n1, n2)
            STATEMENTS[key] = stmt
        elif mC:
            seg = mC.group(1)
            ok(F.drawn(seg), f"{label}: the common side {seg} is drawn")
            eqs.append(("S", seg, seg))
        else:
            its, reason = items_of(ln)
            ok(bool(its), f"{label}: line read", ln)
            for a, b in its:
                ma, mb = measure(F, a), measure(F, b)
                ok(abs(ma - mb) < (TOL_A if a.startswith("∠") or b == "90°" else TOL_L),
                   f"{label}: {a} = {b} in the figure", f"{ma:.2f} vs {mb:.2f}")
                check_reason(F, label, a, b, reason, givens)
                if b == "90°":
                    eqs.append(("A", a[1:], a[1:]))
                elif a.startswith("∠"):
                    eqs.append(("A", a[1:], b[1:]))
                else:
                    eqs.append(("S", a, b))
    ok(stmt is not None, f"{label}: congruence statement found")
    return F, stmt


def check_conclusion(key, F, stmt, label=None, text=None):
    """Each equality in the conclusion is a pair of matching parts under the statement and holds in the figure."""
    label = label or key
    s = text if text is not None else V.text(key)
    if s is None or stmt is None:
        return
    n1, n2 = stmt
    f = dict(zip(n1, n2))
    f.update({b: a for a, b in zip(n1, n2) if b not in f})
    its, reason = items_of(tex_plain(s))
    ok(bool(its), f"{label}: conclusion read")
    for a, b in its:
        ma, mb = measure(F, a), measure(F, b)
        ok(abs(ma - mb) < TOL_L, f"{label}: {a} = {b} in the figure", f"{ma:.2f} vs {mb:.2f}")
        g = dict(zip(n1, n2))
        h = dict(zip(n2, n1))
        def img(t, m):
            if t.startswith("∠"):
                return "∠" + "".join(m.get(c, "?") for c in t[1:])
            return "".join(m.get(c, "?") for c in t)
        def same(t, u):
            if t.startswith("∠") and u.startswith("∠"):
                return t[2] == u[2] and {t[1], t[3]} == {u[1], u[3]}
            return set(t) == set(u)
        ok(same(img(a, g), b) or same(img(a, h), b) or same(img(b, g), a) or same(img(b, h), a),
           f"{label}: {a} and {b} are matching parts of △{n1} ≡ △{n2}")


# ======================= Concept 1 =======================
F, st = check_proof("ex13", "l3_ex13", "Example 13")
check_conclusion("ex13c", F, st, "Example 13 conclusion")
for z in ("l3_ex13a", "l3_ex13b"):
    Z = Scene(z)
    ok(Z.parallel("AB", "DC") and Z.arrows_on("AB") == Z.arrows_on("DC") == 2, f"{z}: AB ∥ DC, marked with arrows")
Z = Scene("l3_ex13a")
ok(Z.marks_in("BAC") == {"dot"} and Z.marks_in("DCA") == {"dot"} and abs(Z.angle("BAC") - Z.angle("DCA")) < TOL_A,
   "Example 13 explanation: the dots mark the alternate angles BAE and DCE, which are equal")
Z = Scene("l3_ex13b")
ok(Z.marks_in("ABD") == {"o"} and Z.marks_in("CDB") == {"o"} and abs(Z.angle("ABD") - Z.angle("CDB")) < TOL_A,
   "Example 13 explanation: the circles mark the alternate angles ABE and CDE, which are equal")
for fig in ("l3_start", "l3_ex13"):
    S = Scene(fig)
    ok(S.parallel("AB", "DC") and S.parallel("AD", "BC") and abs(S.length("AB") - S.length("DC")) < TOL_L
       and abs(S.length("AD") - S.length("BC")) < TOL_L and dist(S.p("E"), ((S.p("A")[0] + S.p("C")[0]) / 2, (S.p("A")[1] + S.p("C")[1]) / 2)) < 0.6,
       f"{fig}: a parallelogram (marks true), E where the diagonals meet")
    ok(S.ticks_on("AB") == S.ticks_on("DC") and S.ticks_on("AD") == S.ticks_on("BC") and S.arrows_on("AB") == S.arrows_on("DC")
       and S.arrows_on("AD") == S.arrows_on("BC"), f"{fig}: equal ticks and arrows on opposite sides")

F, st = check_proof("d1", "l3_d1", "C1 tutor demo", givens=["PS=QR"])
check_conclusion("d1c", F, st, "C1 tutor demo conclusion")
F, st = check_proof("y1", "l3_y1", "C1 your turn", givens=["AX=CY"])
check_conclusion("y1c", F, st, "C1 your turn conclusion")
ok(on_seg(F.p("E"), F.p("X"), F.p("Y")), "C1 your turn: X, E and Y are collinear in the figure (XY drawn through E)")

# ======================= Concept 2 =======================
F, st = check_proof("d2", "l3_d2", "C2 tutor demo")
check_conclusion("d2c", F, st, "C2 tutor demo conclusion")
ok(all(abs(F.length(s) - F.length("PQ")) < TOL_L for s in ("QR", "RS", "SP")), "C2 tutor demo: PQRS is a rhombus")
F, st = check_proof("y2", "l3_y2", "C2 your turn", givens=["AD=BC", "∠DAB=∠CBA"])
check_conclusion("y2c", F, st, "C2 your turn conclusion")
ok(F.parallel("AB", "DC") and F.marks_in("DAB") == F.marks_in("CBA") == {"arc"}, "C2 your turn: AB ∥ DC and the marked base angles")


def quad(fig):
    """The four corners of a quadrilateral drawn with solid lines (in order round the shape)."""
    S = Scene(fig)
    solid = [sg for sg in S.segs if sg not in S.dashed]
    pts = []
    for sg in solid:
        for p in sg:
            if not any(dist(p, q) < 0.5 for q in pts):
                pts.append(p)
    # keep the points that are ends of two solid segments (corners)
    corners = [p for p in pts if sum(1 for sg in solid if dist(sg[0], p) < 0.5 or dist(sg[1], p) < 0.5) >= 2]
    c = (sum(p[0] for p in corners) / len(corners), sum(p[1] for p in corners) / len(corners))
    corners.sort(key=lambda p: atan2(p[1] - c[1], p[0] - c[0]))
    return S, corners


def props(Q):
    A, B, C, D = Q
    side = [dist(Q[i], Q[(i + 1) % 4]) for i in range(4)]
    par = lambda a, b, c, d: adiff(pdir(a, b) % 180, pdir(c, d) % 180) < 0.4 or adiff(pdir(a, b) % 180, pdir(c, d) % 180) > 179.6
    angs = [ang(Q[i], Q[i - 1], Q[(i + 1) % 4]) for i in range(4)]
    m1 = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    m2 = ((B[0] + D[0]) / 2, (B[1] + D[1]) / 2)
    perp = abs((C[0] - A[0]) * (D[0] - B[0]) + (C[1] - A[1]) * (D[1] - B[1])) < 1e-3 * dist(A, C) * dist(B, D)
    return dict(par1=par(A, B, D, C), par2=par(B, C, A, D), eq_opp=abs(side[0] - side[2]) < TOL_L and abs(side[1] - side[3]) < TOL_L,
                all_eq=max(side) - min(side) < TOL_L, right=all(abs(a - 90) < TOL_A for a in angs),
                bisect=dist(m1, m2) < 0.6, eq_diag=abs(dist(A, C) - dist(B, D)) < TOL_L, perp=perp,
                kite=(abs(side[0] - side[1]) < TOL_L and abs(side[2] - side[3]) < TOL_L) or (abs(side[1] - side[2]) < TOL_L and abs(side[3] - side[0]) < TOL_L))


for fig, need in (("l3_k_kite", ("kite", "perp")), ("l3_k_trap", ()), ("l3_k_para", ("par1", "par2", "eq_opp", "bisect")),
                  ("l3_k_rhom", ("par1", "par2", "all_eq", "bisect", "perp")), ("l3_k_rect", ("par1", "par2", "eq_opp", "right", "eq_diag", "bisect")),
                  ("l3_k_sq", ("par1", "par2", "all_eq", "right", "eq_diag", "bisect", "perp"))):
    S, Q = quad(fig)
    pr = props(Q)
    ok(len(Q) == 4 and all(pr[k] for k in need) and (pr["par1"] or pr["par2"] or fig == "l3_k_kite"), f"Key ideas {fig}: the drawn shape has the listed properties", str({k: pr[k] for k in need}))

# ======================= Homework =======================
# Q1: a diagonal splits each quadrilateral into two congruent triangles
check_text(V, "q1", "diagonal")
for q in "abcd":
    S, Q = quad(f"l3_q1{q}")
    A, B, C, D = Q
    okd = bool(congruences({"a": A, "b": B, "c": C}, {"a": C, "b": D, "c": A})) or bool(congruences({"a": B, "b": C, "c": D}, {"a": D, "b": A, "c": B}))
    ok(okd, f"Q1{q}: a diagonal makes two congruent triangles")

# Q2: the property each figure shows
want = {"a": ("sides", "equal"), "b": ("angles", "equal"), "c": ("diagonals", "bisect"), "d": ("sides", "parallel")}
for q in "abcd":
    s = V.text(f"q2{q}")
    if s is None:
        continue
    words = want[q]
    ok(all(w in plain(s).lower() for w in words), f"Q2{q}: printed property names {words}")
    S, Q = quad(f"l3_q2{q}")
    A, B, C, D = Q
    pr = props(Q)
    ok(pr["par1"] and pr["par2"] and pr["eq_opp"] and pr["bisect"], f"Q2{q}: the figure is a parallelogram")
    nt = lambda a, b: sum(1 for t in S.ticks if on_seg(t, a, b, tol=0.8))
    na = lambda a, b: sum(1 for t in S.arrows if on_seg(t, a, b, tol=0.8))
    if q == "a":
        ok(nt(A, B) == nt(C, D) > 0 and nt(B, C) == nt(D, A) > 0 and nt(A, B) != nt(B, C), "Q2a: ticks show opposite sides equal")
    if q == "b":
        arcs = [c for c, k in S.marks if k == "arc"]
        at = sorted(min(range(4), key=lambda i: dist(Q[i], c)) for c in arcs)
        ok(len(arcs) == 4 and at in ([0, 0, 2, 2], [1, 1, 3, 3]) and abs(ang(Q[at[0]], Q[at[0] - 1], Q[(at[0] + 1) % 4]) - ang(Q[at[2]], Q[at[2] - 1], Q[(at[2] + 1) % 4])) < TOL_A,
           "Q2b: double arcs at two opposite vertices, and those angles are equal", str(at))
    if q == "c":
        E = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
        ok(nt(A, E) == nt(E, C) > 0 and nt(B, E) == nt(E, D) > 0, "Q2c: ticks show each diagonal cut in half")
    if q == "d":
        ok(na(A, B) == na(D, C) > 0 and na(B, C) == na(A, D) > 0 and na(A, B) != na(B, C), "Q2d: arrows show opposite sides parallel")

# Q4: the common side is the drawn diagonal
for q in "abc":
    s = V.text(f"q4{q}")
    if s is None:
        continue
    S = Scene(f"l3_q4{q}")
    name = re.sub(r"[^A-Z]", "", plain(s))
    names = list(S.P)
    sides = [a + b for a in names for b in names if a < b and S.drawn(a + b)]
    tris = [t for t in permutations(names, 3) if t[0] < t[1] < t[2] and all(S.drawn(a + b) for a, b in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])))]
    shared = [sd for sd in sides if sum(1 for t in tris if set(sd) <= set(t)) == 2]
    ok(len(tris) == 2 and len(shared) == 1 and set(shared[0]) == set(name), f"Q4{q}: {name} is the side of both triangles", f"{tris} {shared}")

# Q6 (pack Q5): tests for the pairs
for q in "abcdef":
    s = V.text(f"q6{q}")
    if s is None:
        continue
    tst = PR.test_of(s)
    PR.check_pair(f"l3_q6{q}", tst, f"Q6{q} {tst}")
    Fp = PR.Fig(f"l3_q6{q}")
    allsup = set().union(*[PR.supported(Fp, 0, 1, p) for p in PR.coord_matches(Fp, 0, 1)])
    ok(tst in allsup, f"Q6{q}: printed test among those supported", str(sorted(allsup)))

# Q8 (pack Q6): square EFGH
F, st = check_proof("q8", "l3_q8", "Q8")
check_conclusion("q8c", F, st, "Q8 conclusion")
ok(all(abs(F.angle(a) - 90) < TOL_A for a in ("FEH", "GFE", "HGF", "EHG")) and abs(F.length("EF") - F.length("FG")) < TOL_L, "Q8: EFGH is a square")

# Q9 (pack Q7): parallelogram ABCD, diagonal BD
F = Scene("l3_q9")
eqs = []
for k in ("q9a", "q9b"):
    s = V.text(k)
    if s is None:
        continue
    its, reason = items_of(tex_plain(s))
    for a, b in its:
        ok(abs(measure(F, a) - measure(F, b)) < TOL_A, f"{k}: {a} = {b} in the figure")
        check_reason(F, k, a, b, reason, set())
        eqs.append(("A", a[1:], b[1:]))
s = V.text("q9c")
if s is not None:
    c = re.sub(r"[^A-Z]", "", plain(s))
    ok(set(c) == {"B", "D"} and F.drawn(c), "Q9c: BD is the common side")
    eqs.append(("S", "BD", "BD"))
s = V.text("q9d")
if s is not None:
    tst = PR.test_of(s)
    P = {c: F.p(c) for c in "ABD"}
    sides, angles = supported_by(eqs, "ABD", "CDB", P)
    ok(test_holds(tst, sides, angles, "ABD", P) and {"A": "C", "B": "D", "D": "B"} in congruences(P, {c: F.p(c) for c in "CDB"}),
       f"Q9d: parts a-c give {tst} for △ABD ≡ △CDB, a true congruence")
    STATEMENTS["q9"] = ("ABD", "CDB")
check_conclusion("q9e", F, ("ABD", "CDB"), "Q9e")
ok(F.parallel("AB", "DC") and F.parallel("AD", "BC") and F.arrows_on("AB") == F.arrows_on("DC") == 2 and F.arrows_on("AD") == F.arrows_on("BC") == 1,
   "Q9: the figure's arrows show the two pairs of parallel sides")

# Medium
F, st = check_proof("q10a", "l3_q10", "Q10a", givens=["VW=WT"])
check_conclusion("q10b", F, st, "Q10b")
ok(abs(F.angle("VWU") - 90) < TOL_A and on_seg(F.p("W"), F.p("V"), F.p("T")), "Q10b: VWT is a straight line and VWU = 90 in the figure")
ok(all(abs(F.length(s) - F.length("ST")) < TOL_L for s in ("TU", "UV", "VS")), "Q10: STUV is a rhombus")
F, st = check_proof("q11a", "l3_q11", "Q11a", givens=["MQ=QO", "NQ=PQ"])
check_conclusion("q11b", F, st, "Q11b")
ok(abs(F.angle("MQN") - 90) < TOL_A, "Q11b: MQN = 90 in the figure")
check(V, "q11c", (180 - F.angle("MQN")) / 2, tol=1e-3, label="(base angle of isosceles QMN with apex angle MQN measured)")
ok(abs(F.angle("QMN") - 45) < TOL_A and abs(F.length("QM") - F.length("QN")) < TOL_L, "Q11c: QM = QN and QMN = 45 in the figure")
# Q13: Pythagoras, both diagonals sqrt(a^2 + b^2)
s = V.text("q13")
if s is not None:
    F = Scene("l3_q13")
    a_, b_ = F.length("AD"), F.length("AB")
    ok(plain(s).count("\\sqrt{a^2+b^2}") == 2 and abs(F.length("BD") - sqrt(a_ ** 2 + b_ ** 2)) < TOL_L and abs(F.length("AC") - sqrt(a_ ** 2 + b_ ** 2)) < TOL_L
       and abs(F.angle("DAB") - 90) < TOL_A and abs(F.angle("ABC") - 90) < TOL_A,
       "Q13: BD and AC both equal sqrt(a^2 + b^2) (right angles at A and B, measured)")
# Q15: trapezium
F = Scene("l3_q15")
for k, want in (("q15a", "BAE"), ("q15b", "ABE")):
    s = V.text(k)
    if s is None:
        continue
    got = re.sub(r"[^A-Z]", "", plain(s))
    ok(abs(F.angle(got) - F.angle(want)) < TOL_A and alternate_ok(F, want, got), f"{k}: ∠{got} = ∠{want}, alternate angles")
check_text(V, "q15c", "no pairs of equal sides")
P1 = {c: F.p(c) for c in "ABE"}
ok(not any(congruences(P1, {c: F.p(c) for c in t}) for t in ("CDE",)) and abs(F.length("AB") - F.length("DC")) > 5,
   "Q15c: the triangles ABE and CDE are not congruent in the figure (AB longer than DC)")

# Hard
F, st = check_proof("q12a", "l3_q12", "Q12a")
check_conclusion("q12b", F, st, "Q12b")
check_conclusion("q12c", F, st, "Q12c")
F, st = check_proof("q14", "l3_q14", "Q14")
check_conclusion("q14c", F, st, "Q14 conclusion")
F = Scene("l3_q16")
s = V.text("q16a")
if s is not None:
    ok(F.ticks_on("AD") == F.ticks_on("CD") > 0 and abs(F.angle("DAE") - F.angle("DCE")) < TOL_A and "isosceles" in plain(s),
       "Q16a: AD = CD marked, so isosceles; DAE = DCE in the figure")
F, st = check_proof("q16b", "l3_q16", "Q16b", extra_eqs=[("A", "DAE", "DCE")])
check_conclusion("q16c", F, st, "Q16c")
ok(abs(F.angle("AED") - 90) < TOL_A, "Q16c: AED = 90 in the figure")
F, st = check_proof("q17a", "l3_q17a", "Q17a")
check_conclusion("q17ac", F, st, "Q17a conclusion")
ok(alternate_ok(F, "ABD", "CDB") and alternate_ok(F, "ADB", "CBD") and F.parallel("AB", "DC") and F.parallel("AD", "BC"),
   "Q17a: ABD, CDB and ADB, CBD are alternate pairs; AB ∥ DC and AD ∥ BC")
F, st = check_proof("q17b", "l3_q17b", "Q17b")
check_conclusion("q17bc", F, st, "Q17b conclusion")
ok(alternate_ok(F, "ABE", "CDE") and F.parallel("AB", "DC") and F.parallel("AD", "BC") and abs(F.angle("DAE") - F.angle("BCE")) < TOL_A
   and alternate_ok(F, "DAE", "BCE"), "Q17b: the alternate angles give AB ∥ DC and AD ∥ BC")
F, st = check_proof("q17c", "l3_q17c", "Q17c", givens=["BD=AC", "AC=BD"])
check_conclusion("q17cc", F, st, "Q17c conclusion")
ok(abs(F.angle("DAB") - 90) < TOL_A and "AC = BD" in [t for t, x, y in svg_texts("l3_q17c")], "Q17c: DAB = 90 in the figure, and the figure states AC = BD")

# Baulkham Hills Q17
F = Scene("l3_pp_bh")
s = V.text("bha")
if s is not None:
    its, reason = items_of(tex_plain(s))
    for a, b in its:
        ok(abs(measure(F, a) - measure(F, b)) < TOL_A, f"BH (a): {a} = {b} in the figure")
        check_reason(F, "BH (a)", a, b, reason, set())
ok(abs(F.angle("AEB") - F.angle("DFC")) < TOL_A and on_seg(F.p("E"), F.p("A"), F.p("C")) and on_seg(F.p("F"), F.p("A"), F.p("C")),
   "BH (a): E, F on AC and AEB = DFC in the figure")
ok(F.arrows_on("AB") == F.arrows_on("DC") == 2 and F.arrows_on("EB") == F.arrows_on("DF") == 1 and F.ticks_on("EB") == F.ticks_on("DF") == 1
   and F.parallel("AB", "DC") and F.parallel("EB", "DF") and abs(F.length("EB") - F.length("DF")) < TOL_L, "BH: the marks AB ∥ DC, EB ∥ DF, EB = DF are true")
F, st = check_proof("bhb", "l3_pp_bh", "BH (b)", extra_eqs=[("A", "AEB", "CFD")])
check_conclusion("bhc", F, st, "BH (c)")
# Sydney Grammar 2022 Q7(d)
F = Scene("l3_pp_sg")
ok(abs(F.length("AP") - F.length("PD")) < TOL_L and abs(F.length("BQ") - F.length("QC")) < TOL_L and abs(F.angle("ABC") - 90) < TOL_A
   and abs(F.angle("BCD") - 90) < TOL_A, "SG: ABCD is a rectangle with P, Q the midpoints of AD and BC")
F, st = check_proof("sg", "l3_a_sg", "SG 2022 Q7(d)")
check_conclusion("sgc", F, st, "SG 2022 Q7(d) conclusion")
ok(on_seg(F.p("R"), F.p("B"), F.p("D")) and on_seg(F.p("R"), F.p("P"), F.p("Q")), "SG: R is where PQ meets BD")
# James Ruse 2024 Q13(d)(i)
F, st = check_proof("jr", "l3_pp_jr", "JR 2024 Q13(d)(i)", givens=["AM=CM"])
ok(F.ticks_on("AM") == F.ticks_on("MC") == 2 and "R" in F.marks_in("YMC") and "R" in F.marks_in("ABY"), "JR: the figure marks AM = MC and the right angles at M and B")

# ======================= Past papers =======================
F, st = check_proof("pp1", "l3_pp_nb", "PP1 Normanhurst")
check_conclusion("pp1c", F, st, "PP1 (ii)")
ok("R" in F.marks_in("YWZ") and F.ticks_on("XY") == F.ticks_on("ZY") == 2, "PP1: the figure marks XY = ZY and the right angle at W")
F, st = check_proof("pp2", "l3_pp_ns", "PP2 North Sydney Boys")
k = F.length("AB") / 14
ok(abs(F.length("EC") / k - 4) < 0.05 and abs(F.length("FC") / k - 4) < 0.05 and abs(F.length("BC") / k - 14) < 0.05,
   "PP2: the figure is drawn to scale (side 14, EC = FC = 4)")
Pq = [F.p(c) for c in "AECF"]
area = abs(sum(Pq[i][0] * Pq[(i + 1) % 4][1] - Pq[(i + 1) % 4][0] * Pq[i][1] for i in range(4))) / 2 / k ** 2
check(V, "pp2ii", area, tol=1e-3, label="(area of AECF from the drawn square, shoelace)")
ok(abs(area - (14 * 14 - 2 * 0.5 * 14 * 10)) < 1e-6 or abs(area - 56) < 0.05, "PP2 (ii): 14*14 - 2*(1/2*14*10) = 56 agrees with the shoelace area")
F, st = check_proof("pp3", "l3_pp_st", "PP3 Sydney Tech")
c, r = F.circles[0]
ok(all(abs(dist(F.p(ch), c) - r) < 1.0 for ch in "PQRS") and dist(F.p("O"), c) < 1.0, "PP3: O is the centre; P, Q, R, S lie on the circle (drawn round)")
ok(on_seg(F.p("O"), F.p("Q"), F.p("S")), "PP3: S is on QO extended")
s = V.text("pp3ii")
if s is not None:
    POR = F.angle("POS") + F.angle("SOR")
    ok(abs(POR - 2 * F.angle("PQR")) < TOL_A and "4\\alpha" in s and "2\\angle PQR" in s,
       "PP3 (ii): POR (through S) = 2 PQR in the figure; the printed chain 4 alpha = 2 PQR", f"{POR:.2f} vs {2 * F.angle('PQR'):.2f}")
F, st = check_proof("pp4", "l3_pp_mere", "PP4 Merewether", givens=["BC=AD", "AC=BD"])
check_conclusion("pp4ii", F, st, "PP4 (ii)")
s = V.text("pp4iii")
if s is not None:
    ok(abs(F.length("CP") - F.length("DP")) < TOL_L and abs(F.length("AP") - F.length("BP")) < TOL_L and "CP=AC-AP=BD-BP=DP" in tex_plain(s).replace(" ", ""),
       "PP4 (iii): CP = AC - AP = BD - BP = DP, true in the figure")

# ======================= Chapter 8 review =======================
def options(qnum):
    rev = L3.split("Chapter 8 Review")[1]
    blk = rev.split(f'<span class="q-num">{qnum}</span>')[1].split('<span class="q-num">')[0]
    return {m.group(1): tex_plain(m.group(2)).strip() for m in re.finditer(r"<span>([A-E])&ensp;(.*?)</span>", blk)}


Fp = PR.Fig("l3_r_mc")
T1 = {c: Fp.names[c] for c in "ABC"}
T2 = {c: Fp.names[c] for c in "DEF"}
cm = congruences(T1, T2, tol=TOL_L)
# keep the matching that agrees with the marks (crosses with crosses, dots with dots)
def mk(p):
    for (t, i), A in Fp.angles.items():
        if dist(Fp.tris[t][i], p) < 0.5:
            return A.get("marks", set())
    return set()
good = [f for f in cm if all(mk(T1[a]) == mk(T2[f[a]]) for a in "ABC")]
ok(len(good) == 1, "Review MC: one matching agrees with the marks", str(good))
f = good[0] if good else {}
for q, key, expect in ((1, "r6", "∠" + f.get("A", "?")), (2, "r7", "5 cm"), (3, "r8", "△ABC≡△" + "".join(f.get(c, "?") for c in "ABC")), (4, "r9", "AAS")):
    s = V.text(key)
    if s is None:
        continue
    opt = options(q).get(plain(s).strip())
    ok(opt is not None and opt.replace(" ", "") == expect.replace(" ", ""), f"Review MC{q + 5}: option {plain(s)} = {opt} (computed {expect})")
ok(abs(dist(T2["E"], T2["D"]) - dist(T1["A"], T1["C"])) < TOL_L and f.get("C") == "D" and f.get("A") == "E", "Review MC7: ED matches AC, so ED = AC = 5 cm")
check(V, "r7v", 5, label="(ED = AC)")
sup = set().union(*[PR.supported(Fp, 0, 1, p) for p in PR.coord_matches(Fp, 0, 1)])
ok("AAS" in sup and "SSS" not in sup and "SAS" not in sup and "RHS" not in sup, "Review MC9: AAS is the test the marks support", str(sorted(sup)))
F = Scene("l3_r_mc10")
s = V.text("r10")
if s is not None:
    opt = options(5).get(plain(s).strip())
    eqs = [("S", "AB", "CD"), ("S", "BC", "DA"), ("S", "AC", "AC")]
    ok(F.ticks_on("AB") == F.ticks_on("DC") and F.ticks_on("BC") == F.ticks_on("AD") and F.ticks_on("AB") != F.ticks_on("BC"),
       "Review MC10: the marks give AB = CD and BC = DA; AC is common")
    P = {c: F.p(c) for c in "ABC"}
    sides, angles = supported_by(eqs, "ABC", "CDA", P)
    ok(opt == "SSS" and test_holds("SSS", sides, angles, "ABC", P) and {"A": "C", "B": "D", "C": "A"} in congruences(P, {c: F.p(c) for c in "CDA"}),
       "Review MC10: SSS for △ABC ≡ △CDA", str(opt))
# Short answer Q8: congruent quadrilaterals
s8 = svg("l3_r8")
quads = [[tuple(float(t) for t in pt.split(",")) for pt in m.group(1).split()] for m in re.finditer(r'<polygon points="([^"]+)"', s8)]
labs = {t: (x, y - 4) for t, x, y in svg_texts("l3_r8")}
Qd = {}
for qd in quads:
    for t, c in labs.items():
        v = min(qd, key=lambda p: dist(p, c))
        if dist(v, c) < 25 and min(dist(p, c) for Q2 in quads for p in Q2) == dist(v, c):
            Qd[t] = v
fm = congruences({c: Qd[c] for c in "ABCD"}, {c: Qd[c] for c in "EFGH"}, tol=TOL_L)
ok(len(fm) == 1, "Review SA8: the two quadrilaterals are congruent with one matching", str(fm))
fm = fm[0] if fm else {}
for key, exp in (("r8ai", fm.get("B")), ("r8aii", fm.get("C")), ("r8bi", "".join(sorted(fm.get(c, "?") for c in "AD"))),
                 ("r8bii", "".join(sorted(fm.get(c, "?") for c in "BC"))), ("r8ci", fm.get("C")), ("r8cii", fm.get("A"))):
    s = V.text(key)
    if s is None:
        continue
    got = "".join(sorted(re.sub(r"[^A-Z]", "", plain(s))))
    ok(got == exp, f"Review SA8 {key}: {plain(s)} matches", f"computed {exp}")
for q in "abcd":
    s = V.text(f"r9{q}")
    if s is None:
        continue
    tst = PR.test_of(s)
    PR.check_pair(f"l3_r9{q}", tst, f"Review SA9{q} {tst}")
    Fp = PR.Fig(f"l3_r9{q}")
    allsup = set().union(*[PR.supported(Fp, 0, 1, p) for p in PR.coord_matches(Fp, 0, 1)])
    ok(allsup == {tst}, f"Review SA9{q}: the only test supported is {tst}", str(sorted(allsup)))
# SA10 a: pronumerals from the matching parts
Fp = PR.Fig("l3_r10a")
cm = PR.coord_matches(Fp, 0, 1)
fits = [p for p in cm if all(("dot" in Fp.angles.get((0, i), {}).get("marks", set())) == ("dot" in Fp.angles.get((1, p[i]), {}).get("marks", set())) for i in range(3))]
ok(len(fits) == 1, "Review SA10a: one congruence agrees with the dot marks", str(fits))
if fits:
    p = fits[0]
    ia = [i for i in range(3) if Fp.angles.get((0, i), {}).get("label") == "a"][0]
    lab = Fp.angles.get((1, p[ia]), {}).get("label")
    check(V, "r10a_a", float(lab), label="(the angle matching a)")
    ok(abs(Fp.measured(0, ia) - float(lab)) < TOL_A, "Review SA10a: a drawn to scale")
    sx = [k for k, S_ in Fp.sides.items() if k[0] == 0 and S_.get("label") == "x cm"][0]
    other = Fp.side_info(1, p[sx[1]], p[sx[2]]).get("label")
    check(V, "r10a_x", float(other.split()[0]), label="(the side matching x)")
# SA10 b: parallelogram with a diagonal (unnamed points: read the lines)
s10 = svg("l3_r10b")
Ls = [((float(a), float(b)), (float(c), float(d))) for a, b, c, d in re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="[^"]+" stroke-width="1.5"', s10)]
pts = []
for sg in Ls:
    for q_ in sg:
        if not any(dist(q_, r_) < 0.5 for r_ in pts):
            pts.append(q_)
lab = {t: (x, y - 4) for t, x, y in svg_texts("l3_r10b")}
deg = lambda t: t.endswith("°")
Lv = min(pts, key=lambda q_: dist(q_, lab["18°"]))
Rv = min(pts, key=lambda q_: dist(q_, lab["a°"]))
others = [q_ for q_ in pts if q_ not in (Lv, Rv)]
Tv = min(others, key=lambda q_: dist(q_, lab["5 m"]))
Bv = [q_ for q_ in others if q_ is not Tv][0]
ok(abs(ang(Lv, Tv, Rv) - 18) < TOL_A, "Review SA10b: the 18 degree angle is drawn to scale", f"{ang(Lv, Tv, Rv):.2f}")
check(V, "r10b_a", ang(Rv, Bv, Lv), tol=1e-2, label="(a measured: alternate to 18)")
ok(abs(dist(Bv, Lv) - dist(Tv, Rv)) < TOL_L and adiff(pdir(Lv, Tv) % 180, pdir(Bv, Rv) % 180) < 0.4, "Review SA10b: a parallelogram; x m side matches the 5 m side")
check(V, "r10b_x", 5, label="(x m matches 5 m)")
F, st = check_proof("r12a", "l3_r12", "Review SA12a")
check_conclusion("r12b", F, st, "Review SA12b")
ok(abs(F.angle("AEB") - 90) < TOL_A, "Review SA12b: AEB = 90 in the figure")

finish([V])
