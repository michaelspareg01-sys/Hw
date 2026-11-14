"""Shared helpers for the Year 8 Congruence checks (y8cong_rev.py, y8cong_l1.py, ...).

Printed numbers are tagged in the HTML as <span data-v="KEY">...</span> (the last number in the span is
the value) and printed non-numeric answers (letters, names, statements, vectors) as
<span data-k="KEY">...</span>. Every key must occur exactly once in the files read, and every key read
must be checked, or the check FAILS. Figures are read from build/y8cong/svg/*.svg: polygons, polylines,
lines, circle paths and text labels with their positions, in the SVG's own coordinates (viewBox).
"""
import os
import re
from itertools import permutations
from math import atan2, degrees, hypot, acos

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y8CONG_SRC", os.path.join(HERE, "..", "build", "y8cong"))
FAILS, NOK = [], [0]


def ok(flag, label, detail=""):
    if flag:
        NOK[0] += 1
        print("OK       " + label + ("  " + detail if detail else ""))
    else:
        FAILS.append(label)
        print("MISMATCH " + label + ("  " + detail if detail else ""))
    return flag


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def _spans(names, attr):
    out = {}
    for n in names:
        s = read(n)
        # spans may contain nested <b>..</b> or other spans: match to the balancing </span>
        for m in re.finditer(r'<span %s="([^"]+)">' % attr, s):
            i, depth = m.end(), 1
            while depth:
                a, b = s.find("<span", i), s.find("</span>", i)
                if a != -1 and a < b:
                    depth += 1
                    i = a + 5
                else:
                    depth -= 1
                    i = b + 7
            out.setdefault(m.group(1), []).append(s[m.end():i - 7])
    return out


def num(s):
    """The last number printed in s (TeX or text)."""
    s = s.replace("−", "-").replace("&minus;", "-")
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    m = re.findall(r"-?\d+(?:\.\d+)?", s)
    return float(m[-1])


def plain(s):
    """Text of a printed answer without tags or TeX markup; \\angle becomes 'ang '."""
    s = re.sub(r"<b>[ivx]+</b>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\\angle", " ang ").replace("\\triangle", " tri ").replace("\\equiv", " == ")
    s = re.sub(r"\\[()]", " ", s)
    s = re.sub(r"&\w+;", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def caps(s):
    """Upper-case tokens of a printed answer, in order (vertex names, sides, triangles)."""
    return re.findall(r"\b[A-Z]+\b", plain(s))


class Values:
    def __init__(self, names):
        self.v = _spans(names, "data-v")
        self.k = _spans(names, "data-k")
        self.used = set()

    def _one(self, d, key, attr):
        self.used.add((attr, key))
        v = d.get(key, [])
        if len(v) != 1:
            ok(False, f"{attr}={key}", f"found {len(v)} times (must be exactly once)")
            return None
        return v[0]

    def num(self, key):
        s = self._one(self.v, key, "data-v")
        return None if s is None else num(s)

    def text(self, key):
        return self._one(self.k, key, "data-k")

    def unused(self):
        allk = {("data-v", k) for k in self.v} | {("data-k", k) for k in self.k}
        return sorted(allk - self.used)


def check(vals, key, expect, tol=1e-6, label=""):
    got = vals.num(key)
    if got is None:
        return
    ok(abs(got - expect) <= tol * max(1, abs(expect)), f"{key} {label}".strip(), f"printed {got:g}, computed {expect:.6g}")


def check_text(vals, key, expect, label=""):
    """expect: a list of upper-case tokens, or a lower-case word that must appear in the printed text."""
    s = vals.text(key)
    if s is None:
        return
    if isinstance(expect, list):
        got = caps(s)
        ok(got == expect, f"{key} {label}".strip(), f"printed {got}, computed {expect}")
    else:
        got = plain(s).lower()
        ok(expect.lower() in got, f"{key} {label}".strip(), f"printed {got!r}, expected to contain {expect!r}")


# ---------------- SVG reading ----------------

def svg(name):
    return read(os.path.join("svg", name + ".svg"))


def svg_texts(name):
    """[(text, x, y)] for every <text> (x, y = anchor point and baseline; the label centre is about y - 4)."""
    out = []
    for m in re.finditer(r"<text([^>]*)>(.*?)</text>", svg(name), re.S):
        a = m.group(1)
        x = float(re.search(r'\sx="([-\d.]+)"', a).group(1))
        y = float(re.search(r'\sy="([-\d.]+)"', a).group(1))
        out.append((re.sub(r"<[^>]+>", "", m.group(2)).strip(), x, y))
    return out


def svg_labels(name):
    return [t for t, x, y in svg_texts(name)]


def svg_has(name, *labels):
    have = svg_labels(name)
    for lab in labels:
        ok(lab in have, f"figure {name} shows label {lab!r}")


def polygons(name, tag="polygon"):
    out = []
    for m in re.finditer(r'<%s points="([^"]+)"' % tag, svg(name)):
        out.append([tuple(float(t) for t in pt.split(",")) for pt in m.group(1).split()])
    return out


def lines(name):
    out = []
    for m in re.finditer(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="([^"]+)" stroke-width="([\d.]+)"', svg(name)):
        out.append(((float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4))), m.group(5), float(m.group(6))))
    return out


def circles(name):
    """(centre, radius) of every full circle drawn as two arcs 'M x0,y A r,r 0 1 0 x1,y A ...'."""
    out = []
    for m in re.finditer(r'd="M([-\d.]+),([-\d.]+) A([-\d.]+),([-\d.]+) 0 1 0 ([-\d.]+),([-\d.]+) A', svg(name)):
        x0, y, r, _, x1, _ = (float(v) for v in m.groups())
        out.append((((x0 + x1) / 2, y), r))
    return out


def label_centre(t, x, y):
    return (x, y - 4.0)


def name_vertices(name, letters, shapes=None):
    """Map each single label in letters (e.g. 'ABC', or ['A', "A′"]) to the nearest vertex of the
    polygons and polylines of the figure. Returns {letter: (x, y)}."""
    verts = []
    for P in (shapes if shapes is not None else polygons(name) + polygons(name, "polyline")):
        verts += P
    texts = svg_texts(name)
    out = {}
    for L in letters:
        hits = [label_centre(t, x, y) for t, x, y in texts if t == L]
        if len(hits) != 1:
            ok(False, f"figure {name} label {L}", f"found {len(hits)} times")
            continue
        c = hits[0]
        v = min(verts, key=lambda p: hypot(p[0] - c[0], p[1] - c[1]))
        out[L] = v
    return out


def dist(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])


def ang(v, p, q):
    a = (p[0] - v[0], p[1] - v[1])
    b = (q[0] - v[0], q[1] - v[1])
    c = (a[0] * b[0] + a[1] * b[1]) / (hypot(*a) * hypot(*b))
    return degrees(acos(max(-1.0, min(1.0, c))))


def congruences(P, Q, tol=0.6):
    """All bijections f: names of P -> names of Q (dicts of points) that keep every pairwise distance."""
    a, b = list(P), list(Q)
    res = []
    if len(a) != len(b):
        return res
    for perm in permutations(b):
        if all(abs(dist(P[a[i]], P[a[j]]) - dist(Q[perm[i]], Q[perm[j]])) <= tol
               for i in range(len(a)) for j in range(i + 1, len(a))):
            res.append(dict(zip(a, perm)))
    return res


def orient(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def iso_kind(P, Q, f):
    """For a distance-keeping matching f of the point dicts P -> Q, say what isometry it is:
    'translation', 'rotation' or 'reflection' (an orientation-reversing isometry; it may include a slide)."""
    a = list(P)
    o1 = orient(P[a[0]], P[a[1]], P[a[2]])
    o2 = orient(Q[f[a[0]]], Q[f[a[1]]], Q[f[a[2]]])
    if o1 * o2 < 0:
        return "reflection"
    d = [(Q[f[k]][0] - P[k][0], Q[f[k]][1] - P[k][1]) for k in a]
    if all(abs(v[0] - d[0][0]) < 0.6 and abs(v[1] - d[0][1]) < 0.6 for v in d):
        return "translation"
    return "rotation"


def is_pure_reflection(P, Q, f):
    """True if the orientation-reversing matching f is a reflection in a line (no slide): the midpoints of
    each point and its image lie on one line perpendicular to every joining segment."""
    a = list(P)
    mids = [((P[k][0] + Q[f[k]][0]) / 2, (P[k][1] + Q[f[k]][1]) / 2) for k in a]
    # all midpoints collinear and each segment P->f(P) perpendicular to that line
    m0 = mids[0]
    far = max(mids, key=lambda m: dist(m, m0))
    ux, uy = far[0] - m0[0], far[1] - m0[1]
    L = hypot(ux, uy)
    if L < 1e-9:
        return False
    ux, uy = ux / L, uy / L
    for k, m in zip(a, mids):
        if abs((m[0] - m0[0]) * uy - (m[1] - m0[1]) * ux) > 0.6:
            return False
        sx, sy = Q[f[k]][0] - P[k][0], Q[f[k]][1] - P[k][1]
        if abs(sx * ux + sy * uy) > 0.6:
            return False
    return True


def finish(vals_list=()):
    for v in vals_list:
        for attr, k in v.unused():
            ok(False, f"{attr}={k}", "printed value has no check")
    print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
    if FAILS:
        for f in FAILS:
            print("  FAIL", f)
        raise SystemExit(1)
