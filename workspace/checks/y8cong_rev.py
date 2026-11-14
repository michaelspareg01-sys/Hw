r"""Check of the Year 8 Congruence revision warm-up, tied to the printed HTML and the figures.

Reads build/y8cong/a_rev.html (printed numbers in <span data-v>, printed vectors and coordinates in
<span data-k>), the question text in revision.html and the warm-up figures svg/w*.svg. The figures are
drawn to scale, so each answer is checked two ways: (1) recomputed from the GIVEN angle labels, using the
relationship that the coordinates show (which sector a label sits in: opposite or next to the given one;
which vertex of an isosceles triangle is the apex), and (2) measured from the drawing. Vectors are
recomputed from the points in the question text, and rotated coordinates from the triangle read off the
grid in svg/w6.svg. Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 workspace/checks/y8cong_rev.py
"""
import os
import re
import sys
from math import atan2, degrees, hypot, cos, sin, radians
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from y8cong_common import (Values, check, ok, finish, svg_texts, lines, polygons, read, plain, dist, ang,  # noqa: E402
                           label_centre)

V = Values(["a_rev.html"])


def deg_of(t):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)°", t)
    return float(m.group(1)) if m else None


def page_dir(v, p):
    """Direction of p from v, degrees anticlockwise on the page (y down), in [0, 360)."""
    return degrees(atan2(-(p[1] - v[1]), p[0] - v[0])) % 360


# ---------- Q1: rays from one point (6A Q4 c, d, g) ----------
def ray_sectors(fig):
    L = [(p, q) for p, q, col, w in lines(fig)]
    v = L[0][0]
    ok(all(dist(p, v) < 0.2 for p, q in L), f"{fig}: every ray starts at one vertex")
    dirs = sorted(page_dir(v, q) for p, q in L)
    secs = [(dirs[i], dirs[(i + 1) % len(dirs)], (dirs[(i + 1) % len(dirs)] - dirs[i]) % 360) for i in range(len(dirs))]
    labs = {}
    for t, x, y in svg_texts(fig):
        c = label_centre(t, x, y)
        a = page_dir(v, c)
        k = next(i for i, (a0, a1, s) in enumerate(secs) if (a - a0) % 360 < s)
        labs.setdefault(t, []).append(k)
    return secs, labs


for fig, key in (("w1c", "w1c"), ("w1d", "w1d")):
    secs, labs = ray_sectors(fig)
    ok(len(secs) == 4, f"{fig}: two straight lines (four rays)")
    gk = [(deg_of(t), ks[0]) for t, ks in labs.items() if deg_of(t) is not None]
    ok(len(gk) == 1, f"{fig}: one given angle", str(gk))
    g, kg = gk[0]
    ok(abs(secs[kg][2] - g) < 0.5, f"{fig}: given {g:g}° drawn to scale", f"drawn {secs[kg][2]:.2f}")
    for name in ("a", "b"):
        k = labs[name + "°"][0]
        rel = (k - kg) % 4
        want = g if rel == 2 else 180 - g        # opposite sector: vertically opposite; next sector: straight line
        check(V, f"{key}_{name}", want, label=f"({'vertically opposite' if rel == 2 else 'straight line'} from the figure)")
        ok(abs(secs[k][2] - want) < 0.5, f"{fig}: {name} drawn to scale", f"drawn {secs[k][2]:.2f}")

secs, labs = ray_sectors("w1g")
ok(len(secs) == 3, "w1g: three rays")
given = [deg_of(t) for t in labs for _ in labs[t] if deg_of(t) is not None]
ok(sorted(given) == [120, 120], "w1g: given angles read", str(given))
check(V, "w1g_a", 360 - sum(given), label="(revolution)")
ok(abs(secs[labs["a°"][0]][2] - (360 - sum(given))) < 0.5, "w1g: a drawn to scale")


# ---------- Q2: parallel lines cut by a transversal (6B Q4 a, c) ----------
def transversal(fig):
    L = [(p, q) for p, q, col, w in lines(fig) if dist(p, q) > 40]
    dirs = [page_dir(p, q) % 180 for p, q in L]
    # the two parallel lines share a direction; the transversal is the other line
    par = [i for i in range(len(L)) if sum(abs(((dirs[i] - dirs[j]) + 90) % 180 - 90) < 0.25 for j in range(len(L))) == 2]
    tr = [i for i in range(len(L)) if i not in par]
    ok(len(par) == 2 and len(tr) == 1, f"{fig}: two parallel lines and one transversal", str(dirs))
    T = L[tr[0]]

    def meet(A, B):
        (x1, y1), (x2, y2) = A
        (x3, y3), (x4, y4) = B
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    X = [meet(T, L[i]) for i in par]
    u = (T[1][0] - T[0][0], T[1][1] - T[0][1])
    P = L[par[0]]
    w = (P[1][0] - P[0][0], P[1][1] - P[0][1])
    theta = ang((0, 0), u, w)                     # angle between the line directions u and w
    labs = []
    for t, x, y in svg_texts(fig):
        c = label_centre(t, x, y)
        Xn = min(X, key=lambda p: dist(p, c))
        dx, dy = c[0] - Xn[0], c[1] - Xn[1]
        det = u[0] * w[1] - u[1] * w[0]
        al = (dx * w[1] - dy * w[0]) / det
        be = (u[0] * dy - u[1] * dx) / det
        labs.append((t, (al > 0) == (be > 0)))    # True: the sector between +u and +w (or -u and -w)
    return theta, labs


for fig, keys in (("w2a", ("a", "b")), ("w2c", ("a", "b", "c"))):
    theta, labs = transversal(fig)
    g = [(deg_of(t), same) for t, same in labs if deg_of(t) is not None][0]
    th = g[0] if g[1] else 180 - g[0]               # the angle between the line directions, from the given label
    ok(abs(theta - th) < 0.5, f"{fig}: drawn to scale", f"drawn {theta:.2f}, from label {th:g}")
    for k in keys:
        same = [s for t, s in labs if t == k + "°"][0]
        check(V, f"{fig}_{k}", th if same else 180 - th, label="(sector read from the figure)")


# ---------- Q3: isosceles triangles (6C Q5) ----------
def inside(P, q):
    n, c = len(P), False
    for i in range(n):
        (x1, y1), (x2, y2) = P[i], P[(i + 1) % n]
        if (y1 > q[1]) != (y2 > q[1]) and q[0] < x1 + (q[1] - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def vertex_labels(fig, P):
    """{label: vertex index}: the vertex whose angle (the interior wedge, or for a label drawn outside, the
    exterior wedge) has the label nearest its bisector (perpendicular distance in px)."""
    out = {}
    n = len(P)
    for t, x, y in svg_texts(fig):
        c = label_centre(t, x, y)
        best = None
        for i in range(n):
            v = P[i]
            r1, r2 = page_dir(v, P[i - 1]), page_dir(v, P[(i + 1) % n])
            for a0, a1 in ((r1, r2), (r2, r1)):
                w = (a1 - a0) % 360
                mid = a0 + w / 2
                off = abs(((page_dir(v, c) - mid) + 180) % 360 - 180)
                if off <= w / 2:
                    score = dist(v, c) * sin(radians(off)) + 0.3 * dist(v, c)   # near the bisector, and near the vertex
                    if best is None or score < best[0]:
                        best = (score, i)
        out[t] = best[1]
    return out


for fig in ("w3a", "w3b", "w3c"):
    P = polygons(fig)[0]
    A = [ang(P[i], P[i - 1], P[(i + 1) % 3]) for i in range(3)]
    sides = [dist(P[(i + 1) % 3], P[(i + 2) % 3]) for i in range(3)]      # side opposite vertex i
    eq = [i for i in range(3) if abs(sides[(i + 1) % 3] - sides[(i + 2) % 3]) < 0.3]
    ok(len(eq) == 1, f"{fig}: isosceles (two equal sides meet at one apex)", str([round(s, 2) for s in sides]))
    apex = eq[0]
    vl = vertex_labels(fig, P)
    gname = [t for t in vl if deg_of(t) is not None][0]
    g, gi, ai = deg_of(gname), vl[gname], vl["a°"]
    ok(abs(A[gi] - g) < 0.5, f"{fig}: given {g:g}° drawn to scale", f"drawn {A[gi]:.2f}")
    if gi == apex:
        want = (180 - g) / 2
    elif ai == apex:
        want = 180 - 2 * g
    else:
        want = g
    check(V, fig, want, label="(base angles of an isosceles triangle)")
    ok(abs(A[ai] - want) < 0.5, f"{fig}: a drawn to scale", f"drawn {A[ai]:.2f}")


# ---------- Q4: quadrilateral angle sum (6D Q4) ----------
def interior(P):
    n = len(P)
    area = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2
    out = []
    for i in range(n):
        a, v, b = P[i - 1], P[i], P[(i + 1) % n]
        t = (degrees(atan2(a[1] - v[1], a[0] - v[0])) - degrees(atan2(b[1] - v[1], b[0] - v[0]))) % 360
        out.append(t if area > 0 else 360 - t)
    return out


for fig in ("w4a", "w4d", "w4e"):
    P = polygons(fig)[0]
    A = interior(P)
    vl = vertex_labels(fig, P)
    given = {deg_of(t): i for t, i in vl.items() if deg_of(t) is not None}
    if fig == "w4a":
        rights = [i for i in range(4) if abs(A[i] - 90) < 0.5 and i not in given.values() and i != vl["a°"]]
        ok(len(rights) == 1, "w4a: the unlabelled corner is the marked right angle")
        given[90.0] = rights[0]
    ok(len(given) == 3 and all(abs(A[i] - g) < 0.5 for g, i in given.items()), f"{fig}: given angles drawn to scale",
       str({g: round(A[i], 2) for g, i in given.items()}))
    want = 360 - sum(given)
    check(V, fig, want, label="(angle sum of a quadrilateral)")
    ok(abs(A[vl["a°"]] - want) < 0.5, f"{fig}: a drawn to scale", f"drawn {A[vl['a°']]:.2f}")


# ---------- Q5: translation vectors (8B Q5) ----------
q5 = read("revision.html").split("Year 8 Exercise 8B Q5")[1].split("q-num")[0]
pts = re.findall(r'class="pl">(\w)</span>\\\((\w)\((-?\d+),(-?\d+)\)\\\) to \\\((\w)\'\((-?\d+),(-?\d+)\)\\\)', q5)
ok([p[0] for p in pts] == ["a", "d", "e", "j"], "8B Q5 parts read from the question", str([p[0] for p in pts]))
for part, n1, x1, y1, n2, x2, y2 in pts:
    s = V.text(f"w5{part}")
    if s is None:
        continue
    got = [int(v) for v in re.findall(r"-?\d+", s.replace("−", "-"))]
    want = [int(x2) - int(x1), int(y2) - int(y1)]
    ok(got == want, f"w5{part} vector {n1}({x1},{y1}) to {n2}'({x2},{y2})", f"printed {got}, computed {want}")


# ---------- Q6: rotation about the origin (8C Q7), points read from the grid ----------
def grid_frame(fig):
    L = lines(fig)
    axes_ = [(p, q) for p, q, col, w in L if abs(w - 1.3) < 1e-6]
    hx = [p[1] for p, q in axes_ if abs(p[1] - q[1]) < 1e-6]
    vy = [p[0] for p, q in axes_ if abs(p[0] - q[0]) < 1e-6]
    gx = sorted({round(p[0], 1) for p, q, col, w in L if abs(w - 0.7) < 1e-6 and abs(p[0] - q[0]) < 1e-6})
    u = (gx[-1] - gx[0]) / (len(gx) - 1)
    O = (vy[0], hx[0])
    return O, u


O, u = grid_frame("w6")
P = polygons("w6")[0]
vl = vertex_labels("w6", P)
tri = {k: (round((P[vl[k]][0] - O[0]) / u, 6), round(-(P[vl[k]][1] - O[1]) / u, 6)) for k in "ABC"}
ok(tri == {"A": (-4, 4), "B": (-4, 1), "C": (-1, 1)}, "w6: triangle read from the grid", str(tri))
q7 = plain(read("a_rev.html").split("Year 8 Exercise 8C Q7")[1].split("<b>a</b>")[0])
ok("A(-4,4)" in q7.replace(" ", "").replace("−", "-") or "A(−4,4)" in q7, "answer restates A(-4, 4)")
for part, turn in (("a", -180), ("b", -90), ("c", 90)):
    t = radians(turn)
    want = {k: (round(x * cos(t) - y * sin(t)), round(x * sin(t) + y * cos(t))) for k, (x, y) in tri.items()}
    s = V.text(f"w6{part}")
    if s is None:
        continue
    got = {m[0]: (int(m[1]), int(m[2])) for m in re.findall(r"([ABC])'\((-?\d+),(-?\d+)\)", plain(s).replace("−", "-").replace(" ", ""))}
    ok(got == want, f"w6{part} rotation {abs(turn)} degrees {'anticlockwise' if turn > 0 else 'clockwise'}", f"printed {got}, computed {want}")

finish([V])
