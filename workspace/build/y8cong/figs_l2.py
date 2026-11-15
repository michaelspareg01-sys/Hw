"""Figures for Lesson 2 (8E Congruent triangles). Run after figs.py: python3 figs_l2.py

Triangle pairs are placed from the vector coordinates of workspace/sources/y8/chapter 8.pdf (PDF pages
27-33 and 54; points, y down). The first triangle of a pair is drawn TO SCALE from its given data (sides
and angles), fitted by a similarity to the book's position; the second is the exact isometric image of the
first under the matching the marks show, fitted to the book's position. So every pair the book calls
congruent is exactly congruent, and every equal-part mark is true in the coordinates. Pairs the book
marks as NOT congruent (8E Q5a, Q5d, Q7a, Q7d) are drawn from their own data.
Two book items have impossible data (sides 1, 3 and 4 in 8E Q3b and Q4a) and are not drawn.
"""
from math import sin, cos, radians, degrees, atan2, hypot, sqrt, asin
from figs import CF, save, fit_iso, falab, ftext, centroid, _ang, ACC, polar

S = 1.6          # book points to figure pixels


# ---------------- geometry helpers ----------------

def tri_sides(a):
    """Triangle with side a[m] opposite vertex m (math coordinates, y up)."""
    a0, a1, a2 = a
    x = (a1 ** 2 + a2 ** 2 - a0 ** 2) / (2 * a2)
    y = sqrt(max(a1 ** 2 - x ** 2, 0))
    return [(0.0, 0.0), (a2, 0.0), (x, y)]


def tri_angles(A, side):
    """Triangle with angles A[m] (degrees) at vertex m and the side (i, j) of length L; side=(i, j, L)."""
    i, j, L = side
    k = 3 - i - j
    R = L / sin(radians(A[k]))
    return tri_sides([R * sin(radians(A[m])) for m in range(3)])


def tri_sas(i, j, k, Lij, Lik, ang):
    """Triangle with the angle ang (degrees) at vertex i between sides i-j (Lij) and i-k (Lik)."""
    out = [None] * 3
    out[i] = (0.0, 0.0)
    out[j] = (Lij, 0.0)
    out[k] = (Lik * cos(radians(ang)), Lik * sin(radians(ang)))
    return out


def fit_sim(src, dst):
    """Least-squares similarity (scale, rotation, optional reflection, translation) of src onto dst."""
    best = None
    for refl in (False, True):
        P = [(x, -y) if refl else (x, y) for x, y in src]
        cs, cd = centroid(P), centroid(dst)
        a = sum((p[0] - cs[0]) * (q[0] - cd[0]) + (p[1] - cs[1]) * (q[1] - cd[1]) for p, q in zip(P, dst))
        b = sum((p[0] - cs[0]) * (q[1] - cd[1]) - (p[1] - cs[1]) * (q[0] - cd[0]) for p, q in zip(P, dst))
        n = sum((p[0] - cs[0]) ** 2 + (p[1] - cs[1]) ** 2 for p in P)
        c, s = a / n, b / n
        out = [(cd[0] + c * (p[0] - cs[0]) - s * (p[1] - cs[1]), cd[1] + s * (p[0] - cs[0]) + c * (p[1] - cs[1])) for p in P]
        err = sum(hypot(p[0] - q[0], p[1] - q[1]) for p, q in zip(out, dst))
        if best is None or err < best[0]:
            best = (err, out)
    return best[1]


def iso(src, dst):
    F, err, refl = fit_iso(src, dst)
    return [F(p) for p in src]


def bk(pts, s=S):
    return [(x * s, y * s) for x, y in pts]


def shift_all(groups, pad=26):
    pts = [p for g in groups for p in g]
    mx, my = min(p[0] for p in pts), min(p[1] for p in pts)
    W = max(p[0] for p in pts) - mx + 2 * pad
    H = max(p[1] for p in pts) - my + 2 * pad
    return [[(p[0] - mx + pad, p[1] - my + pad) for p in g] for g in groups], W, H


# ---------------- drawing ----------------

def mark(f, P, i, kind):
    v, a, b = P[i], P[i - 1], P[(i + 1) % 3]
    if kind == "R":
        f.right(v, a, b, s=7)
        return
    a0, a1 = radians(_ang(v, a)), radians(_ang(v, b))
    bx, by = cos(a0) + cos(a1), sin(a0) + sin(a1)
    L = hypot(bx, by)
    r = 11
    q = (v[0] + r * bx / L, v[1] - r * by / L)
    if kind == "dot":
        f.dot(q[0], q[1], r=2.0)
    elif kind == "o":
        f.raw(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2.2" fill="#fff" stroke="{ACC["ink"]}" stroke-width="0.9"/>')
    elif kind == "x":
        for dx, dy in ((2.6, 2.6), (2.6, -2.6)):
            f.line(q[0] - dx, q[1] - dy, q[0] + dx, q[1] + dy, width=1.05)
    elif kind in ("arc", "arc2"):
        f.angle(v, a, b, r=13, n=1 if kind == "arc" else 2)


def angle_at(P, i):
    v, a, b = P[i], P[i - 1], P[(i + 1) % 3]
    ux, uy = a[0] - v[0], a[1] - v[1]
    wx, wy = b[0] - v[0], b[1] - v[1]
    c = (ux * wx + uy * wy) / (hypot(ux, uy) * hypot(wx, wy))
    return degrees(acos_(c))


def acos_(c):
    from math import acos
    return acos(max(-1.0, min(1.0, c)))


def side_label(f, P, i, j, s, d=11, size=12.5, centre=None):
    m = ((P[i][0] + P[j][0]) / 2, (P[i][1] + P[j][1]) / 2)
    c = centre or centroid(P)
    ux, uy = P[j][0] - P[i][0], P[j][1] - P[i][1]
    L = hypot(ux, uy)
    nx, ny = -uy / L, ux / L
    if (m[0] - c[0]) * nx + (m[1] - c[1]) * ny < 0:
        nx, ny = -nx, -ny
    it = ("x" in s.split()[0] or "y" in s.split()[0])
    from svg_overlap import text_width
    d = d - 5 + 0.5 * text_width(s, size) * abs(nx) + 0.45 * size * abs(ny)
    base = len(f.items)
    for dd, sg in ((d, 1), (d + 6, 1), (d + 12, 1), (d, -1), (d + 6, -1)):
        f.items = f.items[:base]
        ftext(f, m[0] + sg * dd * nx, m[1] + sg * dd * ny, s, size=size, italic=it, rmax=16)
        if _clean(f, s):
            return


def _clean(f, s):
    import sys as _s
    from svg_overlap import check_string
    probs = check_string(f.svg())
    probs = [p for p in probs if "clipped by the frame" not in p]      # save() grows the frame for these
    return not any(p.startswith(repr(s.replace("-", "\u2212"))) or p.startswith(repr(s)) or ("label " + repr(s)) in p
                   for p in probs)


def angle_label(f, P, i, s, size=12):
    """Angle label on the bisector inside the angle, at a spot nearer to this vertex than to the other two
    (so the label reads as this angle's). A narrow angle that leaves no such spot gets a thin arc (width 0.8,
    not an equal-angle mark) and its label just outside the vertex, on the bisector extended backwards."""
    from svg_overlap import text_width
    v, a, b = P[i], P[i - 1], P[(i + 1) % 3]
    a0, a1 = radians(_ang(v, a)), radians(_ang(v, b))
    bx, by = cos(a0) + cos(a1), sin(a0) + sin(a1)
    L = hypot(bx, by)
    ux, uy = bx / L, -by / L                       # page direction of the bisector (into the angle)
    half = angle_at(P, i) / 2
    d0 = max(17.0, 9.5 / max(sin(radians(half)), 0.08))
    base = len(f.items)

    def own(q):
        return all(hypot(q[0] - v[0], q[1] - v[1]) < hypot(q[0] - w[0], q[1] - w[1]) for w in (a, b))
    for sz in (size, size - 1.5):
        for k in (1.0, 1.2, 1.45, 1.75, 2.1, 2.5, 0.85):
            q = (v[0] + d0 * k * ux, v[1] + d0 * k * uy)
            if not own(q):
                continue
            f.items = f.items[:base]
            f.text(q[0], q[1], s, size=sz)
            if _clean(f, s):
                return
    # outside the vertex
    a0d, a1d = _ang(v, a), _ang(v, b)
    dd = (a1d - a0d) % 360
    if dd > 180:
        a0d, dd = a1d, 360 - dd
    rr = 16
    x0, y0 = v[0] + rr * cos(radians(a0d)), v[1] - rr * sin(radians(a0d))
    x1, y1 = v[0] + rr * cos(radians(a0d + dd)), v[1] - rr * sin(radians(a0d + dd))
    arc = f'<path d="M{x0:.1f},{y0:.1f} A{rr},{rr} 0 0 0 {x1:.1f},{y1:.1f}" fill="none" stroke="{ACC["ink"]}" stroke-width="0.8"/>'
    w = text_width(s, size - 1)
    for dist_ in (12, 16, 20, 26):
        f.items = f.items[:base]
        f.raw(arc)
        d = dist_ + 0.5 * w * abs(ux) + 0.4 * size * abs(uy)
        q = (v[0] - d * ux, v[1] - d * uy)
        if min(ALLV, key=lambda w: hypot(q[0] - w[0], q[1] - w[1])) not in (v,) and \
                hypot(q[0] - v[0], q[1] - v[1]) > min(hypot(q[0] - w[0], q[1] - w[1]) for w in ALLV) + 0.5:
            continue
        f.text(q[0], q[1], s, size=size - 1)
        if _clean(f, s):
            return
    # last resort: keep the label inside, on the bisector
    f.items = f.items[:base]
    f.text(v[0] + d0 * ux, v[1] + d0 * uy, s, size=size - 1.5)


ALLV = []


def draw(f, tris, anns):
    """tris: list of triangles (3 points); anns: matching list of dicts with optional keys
    names, sides {(i, j): text}, ticks {(i, j): n}, angles {i: text}, marks {i: kind}."""
    ALLV[:] = [p for P in tris for p in P]
    for P in tris:
        f.poly(P, color=None, opacity=0, stroke="blue", width=1.5)
    for P, A in zip(tris, anns):
        for (i, j), n in A.get("ticks", {}).items():
            f.tick(P[i], P[j], n)
        for i, k in A.get("marks", {}).items():
            mark(f, P, i, k)
    for P, A in zip(tris, anns):
        if A.get("names"):
            c = centroid(P)
            for p, s in zip(P, A["names"]):
                if s:
                    f.out(p, c, s, d=11 + (A.get("size", 12) - 12) / 2, size=A.get("size", 12))
    for P, A in zip(tris, anns):
        for i, s in A.get("angles", {}).items():
            angle_label(f, P, i, s, size=A.get("size", 12))
        for (i, j), s in A.get("sides", {}).items():
            side_label(f, P, i, j, s, size=A.get("size", 12.5))


def pair(name, b1, b2, fmap, ann1, ann2, canon=None, s=S, t2=None, post=None):
    """b1, b2: book triangles; fmap[i] = index in b2 of the vertex matching vertex i of b1.
    canon: triangle with the given data (any position) for the first triangle, or None to keep the book's.
    t2: optional book-position triangle for a NON-congruent second triangle (used as given)."""
    D1 = bk(b1, s)
    T1 = fit_sim(canon, D1) if canon else D1
    if t2 is None:
        D2 = bk(b2, s)
        img = iso(T1, [D2[fmap[i]] for i in range(3)])
        T2 = [None] * 3
        for i in range(3):
            T2[fmap[i]] = img[i]
    else:
        # a non-congruent second triangle, drawn at the SAME scale as the first (equal marks mean equal lengths)
        src = canon if canon else b1
        k = hypot(T1[1][0] - T1[0][0], T1[1][1] - T1[0][1]) / hypot(src[1][0] - src[0][0], src[1][1] - src[0][1])
        T2 = iso([(p[0] * k, p[1] * k) for p in t2], bk(b2, s))
    (T1, T2), W, H = shift_all([T1, T2])
    f = CF(W, H)
    draw(f, [T1, T2], [ann1, ann2])
    if post:
        post(f, T1, T2)
    save(name, f)


# ---------------- Concept 1: the four tests (Key ideas, Example 8) ----------------

def fig_keyideas():
    I = {0: 0, 1: 1, 2: 2}
    pair("l2_k_sss", [(351.4, 92.6), (336.4, 129.8), (392.9, 129.8)], [(428.7, 92.6), (413.7, 129.8), (470.2, 129.8)], I,
         dict(ticks={(0, 1): 1, (0, 2): 2, (1, 2): 3}), dict(ticks={(0, 1): 1, (0, 2): 2, (1, 2): 3}))
    pair("l2_k_sas", [(321.1, 174.3), (342.7, 232.3), (382.1, 238.7)], [(467.8, 174.9), (406.3, 182.1), (390.7, 218.8)], I,
         dict(ticks={(0, 1): 2, (1, 2): 1}, marks={1: "dot"}), dict(ticks={(0, 1): 2, (1, 2): 1}, marks={1: "dot"}))
    pair("l2_k_aas", [(367.9, 270.5), (363.3, 293.9), (293.5, 332.0)], [(375.5, 305.3), (393.7, 290.0), (472.0, 304.1)], I,
         dict(ticks={(0, 2): 1}, marks={1: "o", 2: "dot"}), dict(ticks={(0, 2): 1}, marks={1: "o", 2: "dot"}))
    pair("l2_k_rhs", [(395.9, 376.3), (324.6, 376.3), (324.6, 416.8)], [(467.2, 375.2), (467.2, 446.5), (426.7, 446.5)], I,
         dict(ticks={(0, 1): 2, (0, 2): 1}, marks={1: "R"}), dict(ticks={(0, 1): 2, (0, 2): 1}, marks={1: "R"}),
         canon=tri_sas(1, 0, 2, 71.3, 40.5, 90))


EX8A = ([(77.3, 163.3), (95.7, 114.5), (147.4, 157.6)], [(194.8, 180.8), (159.5, 142.3), (221.3, 115.6)])
EX8B = ([(290.7, 129.7), (341.7, 129.7), (341.7, 164.3)], [(403.7, 129.6), (352.7, 129.6), (352.7, 164.3)])
I3 = {0: 0, 1: 1, 2: 2}


def aas_pair(name, A0, A1, L, unit="cm"):
    """Example 8a layout: angle A0 at vertex 0, A1 at vertex 1, side L between vertex 0 and vertex 2."""
    a = dict(angles={0: f"{A0}°", 1: f"{A1}°"}, sides={(0, 2): f"{L} {unit}"})
    pair(name, EX8A[0], EX8A[1], I3, a, a, canon=tri_angles((A0, A1, 180 - A0 - A1), (0, 2, L)))


def rhs_pair(name, leg, hyp, unit="m"):
    """Example 8b layout: right angle at vertex 1, leg between vertices 0 and 1, hypotenuse 0-2."""
    a = dict(marks={1: "R"}, sides={(0, 1): f"{leg} {unit}", (0, 2): f"{hyp} {unit}"})
    pair(name, EX8B[0], EX8B[1], I3, a, a, canon=tri_sas(1, 0, 2, leg, sqrt(hyp ** 2 - leg ** 2), 90))


def fig_example8():
    aas_pair("l2_ex8a", 60, 70, 5)
    rhs_pair("l2_ex8b", 12, 15)
    aas_pair("l2_d1a", 55, 65, 6)
    rhs_pair("l2_d1b", 6, 10)
    aas_pair("l2_y1a", 40, 75, 7)
    rhs_pair("l2_y1b", 5, 13)


# ---------------- Concept 2: statements and matching parts (demos) ----------------

def fig_concept2():
    # tutor demo a: PQR and its image MNL (SAS: PQ one mark, PR two marks, included angle at P)
    T1 = [(20.0, 104.0), (130.0, 112.0), (62.0, 24.0)]
    pair("l2_d2a", T1, [(250.0, 40.0), (166.0, 96.0), (240.0, 116.0)], {0: 0, 1: 1, 2: 2},
         dict(names=["P", "Q", "R"], ticks={(0, 1): 1, (0, 2): 2}, marks={0: "arc"}),
         dict(names=["M", "N", "L"], ticks={(0, 1): 1, (0, 2): 2}, marks={0: "arc"}), s=1.0)
    # tutor demo b: angles 35 and 105, side 8 cm between them; image has x cm, a and b
    pair("l2_d2b", [(20.0, 100.0), (150.0, 100.0), (120.0, 30.0)], [(280.0, 30.0), (175.0, 58.0), (200.0, 116.0)],
         {0: 0, 1: 1, 2: 2}, dict(angles={0: "35°", 1: "105°"}, sides={(0, 1): "8 cm"}),
         dict(angles={0: "35°", 1: "a°", 2: "b°"}, sides={(0, 1): "x cm"}),
         canon=tri_angles((35, 105, 40), (0, 1, 8)), s=1.0)
    # your turn a: ABC and its image FDE (SSS)
    pair("l2_y2a", [(20.0, 30.0), (40.0, 110.0), (140.0, 80.0)], [(265.0, 110.0), (180.0, 44.0), (265.0, 30.0)],
         {0: 0, 1: 1, 2: 2}, dict(names=["K", "L", "M"], ticks={(0, 1): 1, (1, 2): 2, (0, 2): 3}),
         dict(names=["T", "R", "S"], ticks={(0, 1): 1, (1, 2): 2, (0, 2): 3}), s=1.0)
    # your turn b: angles 38 and 102, side 9 cm between them
    pair("l2_y2b", [(20.0, 20.0), (150.0, 20.0), (176.0, 142.0)], [(345.0, 142.0), (215.0, 142.0), (189.0, 20.0)],
         {0: 0, 1: 1, 2: 2}, dict(angles={0: "38°", 1: "102°"}, sides={(0, 1): "9 cm"}),
         dict(angles={0: "38°", 1: "a°", 2: "b°"}, sides={(0, 1): "x cm"}),
         canon=tri_angles((38, 102, 40), (0, 1, 9)), s=0.85)


# ---------------- Concept 3: how much information is enough ----------------

def fig_start():
    """Let's start: three triangles with the same 30 degree angle and the same 3 cm side."""
    f = CF(560, 150)
    u = 44
    for k, t in enumerate((1.25, 2.1, 3.9)):
        x0 = 30 + k * 180
        Bl, Br = (x0, 128.0), (x0 + 3 * u, 128.0)
        apex = polar(Br, 150, t * u)
        P = [Bl, Br, apex]
        f.poly(P, color=None, opacity=0, stroke="blue", width=1.5)
    for k, t in enumerate((1.25, 2.1, 3.9)):
        x0 = 30 + k * 180
        Bl, Br = (x0, 128.0), (x0 + 3 * u, 128.0)
        apex = polar(Br, 150, t * u)
        falab(f, Br, Bl, apex, "30°", d=42, size=11)
        f.text(x0 + 1.5 * u, 141, "3 cm", size=11)
    save("l2_start", f)


def fig_ssa():
    """Investigation 'Exploring SSA': a 30 degree angle, a 5 cm side and two places for the 3 cm side."""
    u = 26.0
    A = (20.0, 130.0)
    B = (A[0] + 5 * u, A[1])
    t1, t2 = 5 * cos(radians(30)) - sqrt(9 - 25 * sin(radians(30)) ** 2), 5 * cos(radians(30)) + sqrt(9 - 25 * sin(radians(30)) ** 2)
    P1, P2 = polar(A, 30, t1 * u), polar(A, 30, t2 * u)
    f = CF(250, 150)
    f.line(A[0], A[1], *polar(A, 30, 6.7 * u), color="blue", width=1.5)
    f.line(A[0], A[1], B[0] + 14, B[1], color="blue", width=1.5)
    f.line(B[0], B[1], P1[0], P1[1], color="rose", width=1.0, dash="4 3")
    f.line(B[0], B[1], P2[0], P2[1], color="rose", width=1.0, dash="4 3")
    r = 3 * u
    a1, a2 = _ang(B, P1), _ang(B, P2)
    p1, p2 = polar(B, a1 + 12, r), polar(B, a2 - 12, r)
    f.raw(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} A{r:.1f},{r:.1f} 0 0 0 {p2[0]:.1f},{p2[1]:.1f}" fill="none" '
          f'stroke="{ACC["rose"]}" stroke-width="0.9" stroke-dasharray="3 3"/>')
    f.dot(*B, r=2.0)
    f.angle(A, B, P2, r=16)
    falab(f, A, B, P2, "30°", d=30, size=11)
    f.text((A[0] + B[0]) / 2, A[1] + 13, "5 cm", size=11)
    m1 = ((B[0] + P1[0]) / 2, (B[1] + P1[1]) / 2)
    ftext(f, m1[0] - 2, m1[1] - 10, "3 cm", size=11)
    m2 = ((B[0] + P2[0]) / 2, (B[1] + P2[1]) / 2)
    ftext(f, m2[0] + 20, m2[1], "3 cm", size=11)
    save("l2_ssa", f)


# ---------------- Homework: Exercise 8E ----------------

def fig_q1():
    p = {"a": ([(88.0, 363.5), (88.0, 419.0), (106.5, 396.0)], [(120.1, 362.9), (120.1, 418.4), (138.6, 395.4)]),
         "b": ([(383.7, 361.8), (395.4, 386.4), (325.4, 389.6)], [(403.1, 388.7), (401.8, 361.5), (467.5, 385.5)]),
         "c": ([(86.2, 425.3), (102.7, 453.1), (142.7, 448.8)], [(196.8, 426.5), (192.0, 458.4), (153.3, 469.5)]),
         "d": ([(325.9, 487.7), (338.5, 428.7), (368.2, 477.0)], [(423.3, 426.8), (398.0, 481.6), (379.7, 427.9)])}
    pair("l2_q1a", *p["a"], I3, dict(ticks={(0, 1): 3, (0, 2): 2, (1, 2): 1}), dict(ticks={(0, 1): 3, (0, 2): 2, (1, 2): 1}))
    pair("l2_q1b", *p["b"], I3, dict(ticks={(0, 1): 1, (1, 2): 2}, marks={0: "R"}), dict(ticks={(0, 1): 1, (1, 2): 2}, marks={0: "R"}),
         canon=tri_sas(0, 1, 2, 27.2, 64.6, 90))
    pair("l2_q1c", *p["c"], I3, dict(ticks={(0, 1): 1, (1, 2): 2}, marks={1: "dot"}), dict(ticks={(0, 1): 1, (1, 2): 2}, marks={1: "dot"}))
    pair("l2_q1d", *p["d"], I3, dict(ticks={(0, 1): 1}, marks={0: "o", 2: "dot"}), dict(ticks={(0, 1): 1}, marks={0: "o", 2: "dot"}))


def fig_q2():
    pair("l2_q2a", [(87.8, 535.1), (90.0, 575.4), (149.3, 570.4)], [(165.9, 535.2), (168.2, 575.4), (227.4, 570.4)], I3,
         dict(names=["A", "B", "C"]), dict(names=["E", "F", "D"]))
    pair("l2_q2b", [(352.6, 534.3), (355.9, 582.3), (329.8, 600.9)], [(376.8, 534.2), (373.5, 582.2), (399.6, 600.8)], I3,
         dict(names=["A", "B", "C"]), dict(names=["F", "E", "D"]))
    pair("l2_q2c", [(95.1, 653.6), (168.3, 621.1), (155.1, 650.1)], [(250.3, 624.2), (178.8, 660.4), (209.7, 668.4)], I3,
         dict(names=["X", "Y", "Z"]), dict(names=["U", "S", "T"]))
    # d: isosceles triangle ABD cut by AC (C the foot of the perpendicular from A)
    A, B, C, D = bk([(357.7, 628.1), (329.8, 691.3), (357.7, 691.3), (385.6, 691.3)])
    (T1, T2), W, H = shift_all([[A, B, C], [A, D, C]])
    f = CF(W, H)
    f.poly(T1, color=None, opacity=0, stroke="blue", width=1.5)
    f.poly(T2, color=None, opacity=0, stroke="blue", width=1.5)
    for p, s, dx, dy in ((T1[0], "A", 0, -10), (T1[1], "B", -4, 13), (T1[2], "C", 0, 13), (T2[1], "D", 4, 13)):
        f.lab(p, s, dx=dx, dy=dy)
    save("l2_q2d", f)


def fig_q3():
    pair("l2_q3a", [(97.7, 89.3), (116.5, 125.1), (167.7, 124.6)], [(188.3, 107.7), (207.2, 143.5), (258.4, 142.9)], I3,
         dict(sides={(0, 1): "3 cm", (1, 2): "4 cm"}, angles={1: "110°"}), dict(sides={(0, 1): "3 cm", (1, 2): "4 cm"}, angles={1: "110°"}),
         canon=tri_sas(1, 0, 2, 3, 4, 110))
    pair("l2_q3c", [(143.8, 169.3), (109.1, 169.3), (109.1, 229.9)], [(165.3, 230.7), (200.0, 230.7), (200.0, 170.0)],
         {0: 2, 1: 1, 2: 0}, dict(marks={1: "R"}, sides={(1, 2): "4 cm", (0, 2): "7 cm"}),
         dict(marks={1: "R"}, sides={(0, 1): "4 cm", (0, 2): "7 cm"}), canon=tri_sas(1, 2, 0, 4, sqrt(33), 90))
    pair("l2_q3d", [(294.5, 222.1), (337.2, 203.1), (316.7, 167.9)], [(360.9, 168.4), (406.8, 177.3), (394.8, 216.3)], I3,
         dict(angles={0: "50°", 1: "80°"}, sides={(1, 2): "3 cm"}), dict(angles={0: "50°", 1: "80°"}, sides={(1, 2): "3 cm"}),
         canon=tri_angles((50, 80, 50), (1, 2, 3)), s=2.1)
    # e: rectangle cut by a diagonal; 2 cm sides, 10 cm diagonal, right angles at TL and BR
    k = 16.0
    w = sqrt(96)
    TL, TR, BR, BL = (0.0, 0.0), (w * k, 0.0), (w * k, 2 * k), (0.0, 2 * k)
    (T1, T2), W, H = shift_all([[TL, BL, TR], [BR, TR, BL]], pad=44)
    f = CF(W, H)
    draw(f, [T1, T2], [dict(marks={0: "R"}, sides={(0, 1): "2 cm"}), dict(marks={0: "R"}, sides={(0, 1): "2 cm"})])
    m = ((T1[1][0] + T1[2][0]) / 2, (T1[1][1] + T1[2][1]) / 2)
    ftext(f, m[0] - 22, m[1] - 9, "10 cm", size=11.5)
    save("l2_q3e", f)
    # f: two right triangles sharing the 5 cm side; 80 degrees at the top corners, 10 degrees at the bottom (not to scale, as in the book)
    # drawn with the book's proportions (to scale, the 10 degree angles are too thin to label)
    Bt, M, L, R = bk([(335.6, 358.1), (335.6, 257.9), (294.3, 257.9), (376.9, 257.9)])
    (T1, T2), W, H = shift_all([[L, M, Bt], [R, M, Bt]], pad=22)
    f = CF(W + 40, H)
    T1 = [(p[0] + 20, p[1]) for p in T1]
    T2 = [(p[0] + 20, p[1]) for p in T2]
    draw(f, [T1, T2], [dict(angles={0: "80°", 2: "10°"}), dict(angles={0: "80°", 2: "10°"})])
    m = ((T1[1][0] + T1[2][0]) / 2, (T1[1][1] + T1[2][1]) / 2)
    ftext(f, m[0] + 16, m[1] - 18, "5 cm", size=11.5)
    save("l2_q3f", f)


def fig_q4():
    pair("l2_q4b", [(293.9, 452.9), (353.7, 424.3), (339.0, 393.7)], [(430.6, 436.2), (364.9, 428.6), (368.8, 394.8)], I3,
         dict(marks={1: "R"}, angles={0: "20°"}, sides={(0, 1): "x cm"}, size=14), dict(marks={1: "R"}, angles={0: "a°"}, sides={(0, 1): "9 cm"}, size=14),
         canon=tri_angles((20, 90, 70), (0, 1, 9)), s=2.1)
    pair("l2_q4c", [(94.3, 499.8), (127.8, 533.3), (120.8, 573.8)], [(212.2, 534.3), (164.9, 534.3), (141.2, 500.7)], I3,
         dict(angles={0: "18°", 2: "a°"}, sides={(0, 2): "5 cm"}), dict(angles={0: "18°", 2: "24°"}, sides={(0, 2): "x cm"}),
         canon=tri_angles((18, 138, 24), (0, 2, 5)), s=2.1)
    # d: parallelogram P3 P0 P1 P2 cut by the diagonal P2 P0 (upper triangle P2 P1 P0, lower triangle P2 P3 P0)
    # lower triangle: angle 30 at P2, dot angle at P3; choose the dot angle 115 so the shape is like the book's
    # drawn to scale: top side P2 P1 and bottom side P3 P0 both 5 units, angle P3 P2 P0 = 30 degrees
    from math import atan, tan
    sl = 0.2
    h = 5 / (tan(radians(30) - atan(sl)) + sl)
    u = 14.0
    P2, P1 = (0.0, 0.0), (5 * u, 0.0)
    P3, P0 = (-sl * h * u, h * u), ((5 - sl * h) * u, h * u)
    (T_up, T_low), W, H = shift_all([[P2, P1, P0], [P2, P3, P0]])
    f = CF(W, H)
    draw(f, [T_up, T_low], [dict(marks={1: "dot"}, angles={2: "a°"}, sides={(0, 1): "5 cm"}),
                            dict(marks={1: "dot"}, angles={0: "30°"}, sides={(1, 2): "x cm"})])
    save("l2_q4d", f)
    # e: two triangles crossing at X (the common midpoint); angles 25 and 95, dots for the third angles
    top = tri_angles((25, 60, 95), (1, 2, 4))           # vertices: Q2 (b), Q1 (dot), X (95)
    top = fit_sim(top, bk([(85.2, 584.0), (176.2, 584.0), (151.7, 613.25)]))
    Q2, Q1, X = top
    Q3 = (2 * X[0] - Q2[0], 2 * X[1] - Q2[1])
    Q0 = (2 * X[0] - Q1[0], 2 * X[1] - Q1[1])
    (Tt, Tb), W, H = shift_all([[Q2, Q1, X], [Q3, Q0, X]])
    f = CF(W, H)
    draw(f, [Tt, Tb], [dict(angles={0: "b°", 2: "95°"}, marks={1: "dot"}, sides={(1, 2): "4 cm"}),
                       dict(angles={0: "25°", 2: "a°"}, marks={1: "dot"}, sides={(1, 2): "x cm"})])
    save("l2_q4e", f)
    # f: two right triangles crossing at Y; 50 degrees, 11 cm
    top = tri_angles((40, 50, 90), (0, 2, 11))           # vertices: R1 (dot), R2 (a), Y (right angle)
    top = fit_sim(top, bk([(293.8, 584.1), (364.8, 584.1), (348.65, 612.85)]))
    R1, R2, Y = top
    R0 = (2 * Y[0] - R1[0], 2 * Y[1] - R1[1])
    R3 = (2 * Y[0] - R2[0], 2 * Y[1] - R2[1])
    (Tt, Tb), W, H = shift_all([[R1, R2, Y], [R0, R3, Y]])
    f = CF(W, H)
    draw(f, [Tt, Tb], [dict(marks={0: "dot", 2: "R"}, angles={1: "a°"}, sides={(0, 2): "11 cm"}),
                       dict(marks={0: "dot"}, angles={1: "50°", 2: "b°"}, sides={(0, 2): "x cm"})])
    save("l2_q4f", f)


def fig_q5():
    # a: right triangles, 11 m hypotenuse with legs 9 m and 8 m: not congruent
    pair("l2_q5a", [(85.5, 91.6), (85.5, 122.1), (139.3, 122.1)], [(194.3, 91.1), (169.6, 91.1), (169.6, 140.3)], I3,
         dict(marks={1: "R"}, sides={(0, 2): "11 m", (1, 2): "9 m"}), dict(marks={1: "R"}, sides={(1, 2): "8 m", (0, 2): "11 m"}),
         canon=tri_sas(1, 2, 0, 9, sqrt(121 - 81), 90), t2=tri_sas(1, 2, 0, 8, sqrt(121 - 64), 90))
    pair("l2_q5b", [(350.1, 91.9), (307.9, 117.4), (294.4, 90.6)], [(418.7, 116.4), (376.4, 90.9), (362.9, 117.6)], I3,
         dict(sides={(1, 2): "1", (0, 1): "2"}, marks={1: "dot"}), dict(sides={(1, 2): "1", (0, 1): "2"}, marks={1: "dot"}),
         canon=tri_sas(1, 2, 0, 1, 2, 85))
    pair("l2_q5c", [(86.0, 150.9), (100.7, 182.8), (156.7, 174.7)], [(167.7, 186.3), (176.6, 152.2), (233.2, 150.5)], I3,
         dict(sides={(0, 2): "10"}, marks={0: "x", 1: "dot"}), dict(sides={(0, 2): "10"}, marks={0: "x", 1: "dot"}),
         canon=tri_angles((47, 96, 37), (0, 2, 10)))
    # d: side 2 and double marks; the second triangle has only one double-marked side: not enough to decide
    pair("l2_q5d", [(301.8, 150.8), (340.3, 170.2), (301.8, 189.2)], [(391.0, 150.8), (352.5, 170.2), (391.0, 189.2)], I3,
         dict(sides={(0, 2): "2"}, ticks={(0, 1): 2, (1, 2): 2}), dict(sides={(0, 2): "2"}, ticks={(0, 1): 2}),
         canon=tri_sides((2.2, 2.0, 2.2)), t2=tri_sides((2.7, 2.0, 2.2)))
    pair("l2_q5e", [(92.9, 243.7), (92.9, 213.2), (134.9, 213.2)], [(190.0, 244.4), (190.0, 213.9), (148.0, 213.9)], I3,
         dict(marks={1: "R"}, sides={(0, 1): "5", (1, 2): "7"}), dict(marks={1: "R"}, sides={(0, 1): "5", (1, 2): "7"}),
         canon=tri_sas(1, 0, 2, 5, 7, 90))
    pair("l2_q5f", [(324.6, 250.3), (294.1, 250.3), (294.1, 204.3)], [(366.5, 215.7), (336.0, 215.7), (336.0, 261.7)], I3,
         dict(marks={1: "R", 2: "dot"}, sides={(0, 1): "5"}), dict(marks={1: "R", 2: "dot"}, sides={(0, 1): "5"}),
         canon=tri_sas(1, 0, 2, 5, 7.5, 90))


def fig_q6():
    pair("l2_q6a", [(91.0, 370.1), (91.0, 419.3), (119.7, 419.3)], [(169.5, 419.1), (169.5, 369.9), (140.7, 369.9)], I3,
         dict(names=["A", "C", "B"], marks={1: "R"}, sides={(0, 2): "6 m", (1, 2): "3 m"}),
         dict(names=["D", "F", "E"], marks={1: "R"}, sides={(0, 2): "6 m"}), canon=tri_sas(1, 2, 0, 3, sqrt(27), 90))
    pair("l2_q6b", [(307.0, 369.3), (342.4, 369.3), (299.4, 415.4)], [(370.2, 405.0), (364.4, 370.1), (416.9, 405.0)], I3,
         dict(names=["A", "B", "C"], angles={0: "100°"}, sides={(1, 2): "20 mm"}),
         dict(names=["D", "E", "F"], angles={0: "100°", 1: "30°"}, sides={(1, 2): "20 mm"}), canon=tri_angles((100, 30, 50), (1, 2, 20)))
    pair("l2_q6c", [(115.5, 459.8), (140.8, 522.7), (96.1, 502.1)], [(227.8, 460.9), (181.2, 510.1), (181.2, 460.9)], I3,
         dict(names=["A", "B", "C"], sides={(0, 1): "9 cm", (1, 2): "7 cm"}),
         dict(names=["D", "E", "F"], sides={(0, 1): "9 cm", (1, 2): "7 cm", (0, 2): "6 cm"}), canon=tri_sides((7, 6, 9)))
    # labels drawn larger (size 16) so they print at 8 pt or more when the figure is scaled into its column
    pair("l2_q6d", [(301.4, 529.9), (350.5, 459.9), (364.9, 499.9)], [(383.3, 460.3), (457.5, 502.7), (453.5, 460.3)], I3,
         dict(names=["C", "", "B"], sides={(0, 1): "26 m", (0, 2): "21 m"}, size=16),
         dict(names=["", "G", "F"], angles={0: "20°"}, sides={(0, 1): "26 m", (0, 2): "21 m"}, size=16), canon=tri_sas(0, 1, 2, 26, 21, 20), s=2.0,
         post=_name_e_above)


def _name_e_above(f, T1, T2):
    """Names A and E placed after the angle label, so the narrow 20 degree angle can be labelled just
    outside E: E above its vertex, A to the left of its vertex."""
    for v, s, tries in ((T2[0], "E", ((0, -15), (6, -16), (-6, -16), (0, -20))),
                        (T1[1], "A", ((-13, -4), (-14, 2), (-12, -10), (-16, -6)))):
        base = len(f.items)
        for dx, dy in tries:
            f.items = f.items[:base]
            f.text(v[0] + dx, v[1] + dy, s, size=16, italic=True)
            if _clean(f, s):
                break


def fig_q7():
    # a: isosceles, base angle 75 (apex 30) against apex 35, all four marked sides equal: not congruent
    L = 2.4
    pair("l2_q7a", [(102.4, 583.4), (119.2, 621.6), (85.5, 621.6)], [(149.0, 621.3), (167.9, 583.1), (130.2, 583.1)], I3,
         dict(ticks={(0, 1): 2, (0, 2): 2}, angles={2: "75°"}), dict(ticks={(0, 1): 2, (0, 2): 2}, angles={0: "35°"}),
         canon=tri_sas(0, 1, 2, L, L, 30), t2=tri_sas(0, 1, 2, L, L, 35), s=2.2)
    pair("l2_q7b", [(331.4, 607.7), (294.1, 583.7), (294.1, 631.7)], [(342.4, 607.8), (379.8, 583.8), (379.8, 631.8)], I3,
         dict(ticks={(0, 1): 2, (0, 2): 2}, angles={0: "100°"}), dict(ticks={(0, 1): 2, (0, 2): 2}, angles={1: "40°"}),
         canon=tri_sas(0, 1, 2, 2.4, 2.4, 100), s=2.2)
    pair("l2_q7c", [(92.5, 680.7), (85.5, 641.4), (140.5, 680.7)], [(206.7, 653.1), (214.6, 698.2), (151.5, 653.1)], I3,
         dict(angles={0: "100°", 1: "50°"}, sides={(0, 2): "5 cm"}), dict(angles={0: "100°", 2: "30°"}, sides={(0, 2): "5 cm"}),
         canon=tri_angles((100, 50, 30), (0, 2, 5)), s=2.2)
    pair("l2_q7d", [(311.9, 641.9), (329.9, 678.9), (294.4, 696.2)], [(360.9, 668.9), (389.0, 641.9), (415.0, 668.9)], I3,
         dict(marks={1: "R"}, angles={0: "35°"}, sides={(0, 1): "10 cm"}, size=14), dict(marks={1: "R"}, angles={0: "65°"}, sides={(1, 2): "10 cm"}, size=14),
         canon=tri_angles((35, 90, 55), (0, 1, 10)), t2=tri_angles((65, 90, 25), (1, 2, 10)), s=2.2)


def fig_q8():
    pair("l2_q8", [(100.4, 191.5), (100.4, 102.1), (147.3, 102.1)], [(211.8, 86.8), (211.8, 176.2), (164.9, 176.2)], I3,
         dict(marks={1: "R"}, sides={(0, 1): "12 km", (1, 2): "5 km"}), dict(marks={1: "R"}, sides={(0, 2): "13 km", (1, 2): "5 km"}),
         canon=tri_sas(1, 0, 2, 12, 5, 90), s=1.2)


def fig_q10_q11():
    # Q10 stem: AB parallel to DE, AE and BD cross at C, AC = EC
    def crossing(name, A, B, D, E, ticks, arrows, names=("A", "B", "C", "D", "E")):
        A, B, D, E = bk([A, B, D, E])
        C = ((A[0] + E[0]) / 2, (A[1] + E[1]) / 2)
        D = (2 * C[0] - B[0], 2 * C[1] - B[1])
        (T1, T2), W, H = shift_all([[A, B, C], [E, D, C]])
        f = CF(W, H)
        f.poly(T1, color=None, opacity=0, stroke="blue", width=1.5)
        f.poly(T2, color=None, opacity=0, stroke="blue", width=1.5)
        f.parr(T1[0], T1[1], t=0.55, color="blue").parr(T2[1], T2[0], t=0.55, color="blue")
        f.tick(T1[0], T1[2], ticks).tick(T2[2], T2[0], ticks)
        c = T1[2]
        for p, s, dx, dy in ((T1[0], names[0], -6, -9), (T1[1], names[1], 6, -9), (T2[1], names[3], -8, 9), (T2[0], names[4], 6, 11)):
            f.lab(p, s, dx=dx, dy=dy)
        ftext(f, c[0] + 10, c[1] - 2, names[2], size=12, italic=True)
        save(name, f)
    crossing("l2_q10", (124.9, 309.1), (179.6, 309.1), (90.9, 351.8), (145.6, 351.8), 1, None)
    crossing("l2_q10a", (87.4, 513.9), (134.9, 513.9), (116.9, 550.9), (164.3, 550.9), 2, None)
    # 10b: isosceles ACD (AD = CD) with DB bisecting the angle at D; B on AC
    A, B, C, D = bk([(299.0, 574.3), (331.3, 574.3), (363.6, 574.3), (331.3, 514.3)])
    (T1, T2), W, H = shift_all([[A, B, D], [C, B, D]])
    f = CF(W, H)
    draw(f, [T1, T2], [dict(ticks={(0, 2): 2, (1, 2): 1}, marks={2: "dot"}), dict(ticks={(0, 2): 2}, marks={2: "dot"})])
    for p, s, dx, dy in ((T1[0], "A", -8, 10), (T1[1], "B", 0, 13), (T2[0], "C", 8, 10), (T1[2], "D", 0, -10)):
        f.lab(p, s, dx=dx, dy=dy)
    save("l2_q10b", f)
    # 10c: parallelogram ABCD with diagonal AC
    A, B, C, D = bk([(107.7, 613.6), (170.5, 613.6), (153.5, 643.4), (90.7, 643.4)])
    (T1, T2), W, H = shift_all([[A, B, C], [C, D, A]])
    f = CF(W, H)
    f.poly(T1, color=None, opacity=0, stroke="blue", width=1.5)
    f.poly(T2, color=None, opacity=0, stroke="blue", width=1.5)
    A, B, C, D = T1[0], T1[1], T1[2], T2[1]
    f.parr(A, B, n=2, color="blue").parr(D, C, n=2, color="blue").parr(D, A, color="blue").parr(C, B, color="blue")
    for p, s, dx, dy in ((A, "A", -2, -10), (B, "B", 4, -10), (C, "C", 4, 12), (D, "D", -4, 12)):
        f.lab(p, s, dx=dx, dy=dy)
    save("l2_q10c", f)
    # 10d: kite-like ABCD with right angles at B and D, BC = DC, diagonal AC
    k = 1.6
    A = (0.0, 0.0)
    C = (62 * k, 0.0)
    ang = degrees(asin(37 / 62))
    Bp = polar(A, ang, 62 * k * cos(radians(ang)))
    Dp = polar(A, -ang, 62 * k * cos(radians(ang)))
    (T1, T2), W, H = shift_all([[A, Bp, C], [A, Dp, C]], pad=20)
    f = CF(W, H)
    draw(f, [T1, T2], [dict(marks={1: "R"}, ticks={(1, 2): 2, (0, 2): 1}), dict(marks={1: "R"}, ticks={(1, 2): 2})])
    for p, s, dx, dy in ((T1[0], "A", -10, 4), (T1[1], "B", 0, -10), (T1[2], "C", 10, 4), (T2[1], "D", 0, 13)):
        f.lab(p, s, dx=dx, dy=dy)
    save("l2_q10d", f)
    # 11a: isosceles ABC (apex A) with M the midpoint of BC
    A, B, C = bk([(131.6, 169.3), (91.2, 244.3), (172.0, 244.3)])
    M = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
    (T1, T2), W, H = shift_all([[A, B, M], [A, C, M]])
    f = CF(W + 30, H)
    draw(f, [T1, T2], [dict(ticks={(0, 1): 2, (1, 2): 1}), dict(ticks={(0, 1): 2, (1, 2): 1})])
    f.lab(T1[0], "A (apex)", dx=26, dy=-8).lab(T1[1], "B", dx=-6, dy=12).lab(T1[2], "M", dy=13).lab(T2[1], "C", dx=6, dy=12)
    save("l2_q11a", f)
    # 11b: AE parallel to DC, ED and AC cross at B, EB = BD
    A, E, D = bk([(102.5, 341.6), (90.0, 387.2), (163.1, 313.3)])
    Bm = ((E[0] + D[0]) / 2, (E[1] + D[1]) / 2)
    C = (2 * Bm[0] - A[0], 2 * Bm[1] - A[1])
    (T1, T2), W, H = shift_all([[A, E, Bm], [C, D, Bm]])
    f = CF(W, H)
    f.poly(T1, color=None, opacity=0, stroke="blue", width=1.5)
    f.poly(T2, color=None, opacity=0, stroke="blue", width=1.5)
    f.parr(T1[1], T1[0], t=0.55, color="blue").parr(T2[0], T2[1], t=0.55, color="blue")
    f.tick(T1[1], T1[2], 2).tick(T2[2], T2[1], 2)
    for p, s, dx, dy in ((T1[0], "A", -4, -9), (T1[1], "E", -6, 12), (T2[1], "D", 6, -8), (T2[0], "C", 4, 12)):
        f.lab(p, s, dx=dx, dy=dy)
    ftext(f, T1[2][0], T1[2][1] + 14, "B", size=12, italic=True)
    save("l2_q11b", f)
    # 11c: kite ABCD (D top, B bottom) with dashed diagonal BD
    A, Bk, C, D = bk([(97.1, 473.4), (127.1, 536.6), (157.1, 473.4), (127.1, 446.6)])
    (T1, T2), W, H = shift_all([[A, Bk, D], [C, Bk, D]])
    f = CF(W, H)
    f.poly([T1[0], T1[2], T2[0], T1[1]], color=None, opacity=0, stroke="blue", width=1.5)
    f.raw(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in T1)}" fill="none" stroke="none"/>')
    f.raw(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in T2)}" fill="none" stroke="none"/>')
    f.line(T1[1][0], T1[1][1], T1[2][0], T1[2][1], color="faint", width=1.0, dash="4 3")
    f.tick(T1[0], T1[2], 1).tick(T2[0], T2[2], 1).tick(T1[0], T1[1], 2).tick(T2[0], T2[1], 2)
    for p, s, dx, dy in ((T1[0], "A", -10, 0), (T1[1], "B", 0, 13), (T2[0], "C", 10, 0), (T1[2], "D", 0, -10)):
        f.lab(p, s, dx=dx, dy=dy)
    save("l2_q11c", f)
    # 11d: rhombus ABCD with diagonals meeting at E
    side = 52 * S
    A = (0.0, 0.0)
    Bv = (side, 0.0)
    Dv = polar(A, 64.1, side)
    Cv = (Bv[0] + Dv[0] - A[0], Bv[1] + Dv[1] - A[1])
    E = ((A[0] + Cv[0]) / 2, (A[1] + Cv[1]) / 2)
    (Q,), W, H = shift_all([[A, Bv, Cv, Dv, E]])
    A, Bv, Cv, Dv, E = Q
    f = CF(W, H)
    f.poly([A, Bv, Cv, Dv], color=None, opacity=0, stroke="blue", width=1.5)
    for t in ([A, Cv, Dv], [A, Cv, Bv], [Dv, Cv, E], [Bv, Cv, E]):
        f.raw(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in t)}" fill="none" stroke="none"/>')
    f.line(A[0], A[1], Cv[0], Cv[1], color="rose", width=1.0, dash="4 3").line(Bv[0], Bv[1], Dv[0], Dv[1], color="rose", width=1.0, dash="4 3")
    f.parr(A, Bv, n=2, t=0.4, color="blue").parr(Dv, Cv, n=2, t=0.4, color="blue").parr(A, Dv, t=0.4, color="blue").parr(Bv, Cv, t=0.4, color="blue")
    for p, q in ((A, Bv), (Bv, Cv), (Cv, Dv), (Dv, A)):
        f.tick(p, q, 2, t=0.65)
    for p, s, dx, dy in ((A, "A", -6, 12), (Bv, "B", 4, 12), (Cv, "C", 6, -8), (Dv, "D", -4, -9)):
        f.lab(p, s, dx=dx, dy=dy)
    ftext(f, E[0], E[1] - 12, "E", size=12, italic=True)
    save("l2_q11d", f)


def fig_answers_q9():
    """Answer figures: (a) two different triangles from the same two sides and non-included angle;
    (b) two triangles with the same three angles and different sizes."""
    u = 24.0
    A = (14.0, 100.0)
    B = (A[0] + 5 * u, A[1])
    t1 = 5 * cos(radians(30)) - sqrt(9 - 25 * sin(radians(30)) ** 2)
    t2 = 5 * cos(radians(30)) + sqrt(9 - 25 * sin(radians(30)) ** 2)
    T1 = [A, B, polar(A, 30, t1 * u)]
    T2 = [(p[0] + 150, p[1]) for p in [A, B, polar(A, 30, t2 * u)]]
    f = CF(300, 120)
    draw(f, [T1, T2], [dict(sides={(0, 1): "5 cm", (1, 2): "3 cm"}, angles={0: "30°"}),
                       dict(sides={(0, 1): "5 cm", (1, 2): "3 cm"}, angles={0: "30°"})])
    save("l2_a9a", f)
    small = fit_sim(tri_angles((50, 60, 70), (0, 1, 3)), [(14, 110), (124, 110), (64, 30)])
    big = [(170 + 1.4 * (p[0] - 14), 130 + 1.4 * (p[1] - 110)) for p in small]
    f = CF(340, 150)
    draw(f, [small, big], [dict(angles={0: "50°", 1: "60°", 2: "70°"}), dict(angles={0: "50°", 1: "60°", 2: "70°"})])
    save("l2_a9b", f)


# ---------------- Past papers ----------------

def fig_pp():
    # Merewether 2023 Section III Part A Q2 (AAS): 38 at the top left, 74 at the bottom, 18 on the right side
    T1 = tri_angles((38, 68, 74), (1, 2, 18))            # vertices: top-left (38), top-right, bottom (74)
    pair("l2_pp_mere", [(30.0, 10.0), (120.0, 14.0), (95.0, 80.0)], [(250.0, 80.0), (180.0, 80.0), (210.0, 16.0)],
         {0: 1, 1: 0, 2: 2}, dict(angles={0: "38°", 2: "74°"}, sides={(1, 2): "18"}),
         dict(angles={1: "38°", 2: "74°"}, sides={(0, 2): "18"}), canon=T1, s=1.0)
    # Girraween 2020 Q14: four right triangles around a point P (I, II, III, IV)
    t, uu = 1.0, 1.415
    P = (0.0, 0.0)
    w = sqrt(uu ** 2 - t ** 2)
    k = 70.0
    d0 = 168.3
    V2 = polar(P, d0, uu * k)                               # page directions (degrees anticlockwise)
    a_ii = degrees(atan2(t, uu))                            # angle at P in II and III
    V3 = polar(P, d0 - a_ii, hypot(t, uu) * k)              # II: right angle at V2, legs V2V3 = t, V2P = uu
    V4 = polar(P, d0 - 2 * a_ii, uu * k)                    # III: right angle at V4, legs V4V3 = t, V4P = uu
    a_i = degrees(atan2(t, w))                              # angle at P in I and IV
    V1 = polar(P, d0 + a_i, w * k)                          # I: right angle at V1, legs V1V2 = t, V1P = w
    V5 = polar(P, d0 - 2 * a_ii - a_i, w * k)               # IV: right angle at V5, legs V5V4 = t, V5P = w
    tris = [[P, V1, V2], [P, V2, V3], [P, V3, V4], [P, V4, V5]]
    tris, W, H = shift_all(tris)
    f = CF(W, H)
    for T in tris:
        f.poly(T, color=None, opacity=0, stroke="ink", width=1.1)
    f.right(tris[0][1], tris[0][0], tris[0][2], s=6)
    f.right(tris[1][1], tris[1][0], tris[1][2], s=6)
    f.right(tris[2][2], tris[2][0], tris[2][1], s=6)
    f.right(tris[3][2], tris[3][0], tris[3][1], s=6)
    f.tick(tris[0][1], tris[0][2], 1).tick(tris[1][1], tris[1][2], 1).tick(tris[2][1], tris[2][2], 1).tick(tris[3][1], tris[3][2], 1)
    for T, s in zip(tris, ("I", "II", "III", "IV")):
        c = centroid(T)
        f.text(c[0], c[1], s, size=11.5)
    save("l2_pp_girr", f)
    # Sydney Tech 2025 Q12(e): RST and UVW, right angles at R and U, hypotenuse 8, 53 degrees at S and V
    T = tri_angles((90, 53, 37), (1, 2, 8))                 # vertices R, S, T
    pair("l2_pp_st", [(10.0, 100.0), (60.0, 100.0), (10.0, 10.0)], [(130.0, 100.0), (180.0, 100.0), (130.0, 10.0)], I3,
         dict(names=["R", "S", "T"], marks={0: "R"}, angles={1: "53°"}, sides={(1, 2): "8"}),
         dict(names=["U", "V", "W"], marks={0: "R"}, angles={1: "53°"}, sides={(1, 2): "8"}), canon=[(p[0] * 12, p[1] * 12) for p in T], s=1.5)


if __name__ == "__main__":
    fig_keyideas(); fig_example8(); fig_concept2(); fig_start(); fig_ssa()
    fig_q1(); fig_q2(); fig_q3(); fig_q4(); fig_q5(); fig_q6(); fig_q7(); fig_q8(); fig_q10_q11(); fig_answers_q9(); fig_pp()
