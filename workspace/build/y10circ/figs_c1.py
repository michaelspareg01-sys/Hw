"""Figures for Lesson C1 (Chords, radii and angles). Run: python3 figs_c1.py  (writes svg/c1_*.svg etc.)

Sources: AMSI TIMES Circle Geometry pp. 5-11 (concept figures, Exercises 1-5); Maths Pathway sheets
'Chords, Secants, and Tangents' (Q1-Q6) and 'Arcs and Angles in Circles' (Q7, Q8a); the past papers.
Each figure is redrawn to follow the source diagram (layout, labels and marks).
"""
from math import sin, cos, radians, degrees, sqrt, atan2, hypot, asin, pi
from figs import CF, Fig, ext, foot, ftext, _ang
from figs import save as _save


def save(name, f):
    _save(name, f, rmax=30)

C0 = (70, 64)


def circ(w=140, h=130, c=None, r=54):
    f = CF(w, h)
    c = c or (w / 2, h / 2)
    f.circle(c, r)
    return f, c, r


def label_line(f, p, q, s, d=9, size=10.5, t=0.5, side=1, color="ink"):
    mx, my = p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
    L = hypot(q[0] - p[0], q[1] - p[1])
    nx, ny = (q[1] - p[1]) / L, -(q[0] - p[0]) / L
    return f.text(mx + side * d * nx, my + side * d * ny, s, size=size, color=color)


def chord_lab(f, p, q, c, s, d=10, size=10.5, inside=False, t=0.5, italic=False):
    """Label s beside chord pq, d px from its point at fraction t, away from the centre c (or towards it)."""
    mx, my = p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
    L = hypot(q[0] - p[0], q[1] - p[1])
    nx, ny = (q[1] - p[1]) / L, -(q[0] - p[0]) / L
    if (nx * (c[0] - mx) + ny * (c[1] - my) > 0) != inside:
        nx, ny = -nx, -ny
    return f.text(mx + d * nx, my + d * ny, s, size=size, italic=italic)


# ---------------------------------------------------------------- Concept 1
def concept1():
    # AMSI p5: secant, diameter, radius, chord
    f, c, r = circ(230, 140, (110, 72), 58)
    f.seg((40, 30), (226, 30))                       # secant across the top
    f.text(208, 22, "secant", size=10.5, italic=False)
    d0, d1 = CF.on(c, r, 200), CF.on(c, r, 20)
    f.seg(d0, d1).pdot(c, 2.4)
    label_line(f, c, d1, "diameter", d=9, size=10.5, t=0.15)
    rr = CF.on(c, r, 238)
    f.seg(c, rr)
    f.text(76, 100, "radius", size=10.5)
    ch0, ch1 = CF.on(c, r, 245), CF.on(c, r, 318)
    f.seg(ch0, ch1)
    label_line(f, ch0, ch1, "chord", d=10, size=10.5, t=0.6)
    save("c1_terms", f)

    # Maths Pathway: chord, secant, tangent (three panels)
    for nm, kind in (("c1_mp_chord", "chord"), ("c1_mp_secant", "secant"), ("c1_mp_tangent", "tangent")):
        f, c, r = circ(140, 120, (70, 56), 44)
        if kind == "chord":
            p, q = CF.on(c, r, 235), CF.on(c, r, 5)
            f.seg(p, q).pdot(p).pdot(q)
        elif kind == "secant":
            p, q = CF.on(c, r, 215), CF.on(c, r, 22)
            f.seg(ext(p, q, -0.35), ext(p, q, 1.35)).pdot(p).pdot(q)
        else:
            t = (c[0], c[1] + r)
            f.seg((t[0] - 50, t[1]), (t[0] + 50, t[1])).pdot(t)
        save(nm, f)

    # AMSI p6: symmetries (rotation; reflection in diameter AOB; P to Q)
    a, c, r = circ(130, 110, (60, 55), 46)
    a.pdot(c, 2.2).lab(c, "O", dx=-9, dy=1)
    p1, p2 = CF.on(c, r, 35), CF.on(c, r, -20)
    a.seg(c, p1, width=1.3).seg(c, p2, width=1.3).angle(c, p1, p2, r=10).alab(c, p1, p2, "θ", d=18, size=11)
    a.items.append('<path d="M118,74 A62,62 0 0 0 118,30" fill="none" stroke="#1f2a37" stroke-width="1.2"/>')
    a.arrow(118.5, 34, 117.6, 29, head=6)
    b, c, r = circ(120, 110, (60, 55), 46)
    A, B = CF.on(c, r, 215), CF.on(c, r, 35)
    b.seg(A, B).pdot(c, 2.2).lab(c, "O", dx=3, dy=10).out(A, c, "A").out(B, c, "B")
    g, c, r = circ(130, 116, (62, 58), 46)
    P, Q = CF.on(c, r, 100), CF.on(c, r, -50)
    A, B = CF.on(c, r, 205), CF.on(c, r, 25)
    g.seg(c, P, dash="3 3", width=1.2).seg(c, Q, dash="3 3", width=1.2).seg(A, B, dash="3 3", width=1.2)
    g.pdot(c, 2.2).lab(c, "O", dx=-4, dy=11).out(P, c, "P").out(Q, c, "Q").out(A, c, "A").out(B, c, "B")
    g.alab(c, P, B, "θ/2", d=27, size=9.5).alab(c, B, Q, "θ/2", d=27, size=9.5)
    for nm, f in (("c1_sym_a", a), ("c1_sym_b", b), ("c1_sym_c", g)):
        save(nm, f)

    # AMSI p6: congruent circles (same radius) and similar circles
    f = CF(230, 150)
    for (cx, cy, rr, nm, rl) in ((50, 38, 30, "O", "r"), (170, 38, 30, "Z", "R"), (50, 112, 30, "O", "r"), (176, 110, 40, "Z", "R")):
        cc = (cx, cy)
        f.circle(cc, rr).pdot(cc, 2.2)
        e = CF.on(cc, rr, 40)
        f.seg(cc, e, width=1.3).lab(cc, nm, dx=-4, dy=12, size=11)
        label_line(f, cc, e, rl, d=11, size=11, t=0.5)
    save("c1_cong", f)

    # Our own: a chord AB divides the circle into two segments; angle APB subtended at P
    f, c, r = circ(150, 132, (74, 64), 52)
    A, B = CF.on(c, r, 200), CF.on(c, r, -20)
    f.raw(f'<path d="M{A[0]:.1f},{A[1]:.1f} A{r},{r} 0 0 0 {B[0]:.1f},{B[1]:.1f} Z" fill="#2563eb" fill-opacity="0.16" stroke="none"/>')
    f.seg(A, B)
    P = CF.on(c, r, 105)
    f.seg(A, P, color="blue", width=1.3).seg(B, P, color="blue", width=1.3).angle(P, A, B, r=12, color="blue")
    f.out(A, c, "A").out(B, c, "B").out(P, c, "P")
    f.text(74, 98, "minor segment", size=9.5, color="faint")
    f.text(74, 73.5, "major segment", size=9, color="faint")
    save("c1_seg", f)


# Small "chord / secant / tangent / none" panels. kind: chord, diam, secant, tangent, radius, outside, ray
def panel(name, kind, rot=0.0, w=96, h=90):
    f = CF(w, h)
    c, r = (w / 2, h / 2), 30
    f.circle(c, r)
    if kind == "chord":
        p, q = CF.on(c, r, 200 + rot), CF.on(c, r, 320 + rot)
        f.seg(p, q).pdot(p, 2).pdot(q, 2)
    elif kind == "chord2":
        p, q = CF.on(c, r, 150 + rot), CF.on(c, r, 20 + rot)
        f.seg(p, q).pdot(p, 2).pdot(q, 2)
    elif kind == "diam":
        p, q = CF.on(c, r, 180 + rot), CF.on(c, r, rot)
        f.seg(p, q).pdot(p, 2).pdot(q, 2)
    elif kind == "secant":
        p, q = CF.on(c, r, 140 + rot), CF.on(c, r, 300 + rot)
        f.seg(ext(p, q, -0.45), ext(p, q, 1.45))
    elif kind == "secant_dot":
        p, q = CF.on(c, r, 160 + rot), CF.on(c, r, 330 + rot)
        f.seg(ext(p, q, -0.4), q).pdot(q, 2)
    elif kind == "tangent":
        t = CF.on(c, r, 90 + rot)
        u = (cos(radians(rot)), -sin(radians(rot)))
        f.seg((t[0] - 40 * u[0], t[1] - 40 * u[1]), (t[0] + 40 * u[0], t[1] + 40 * u[1])).pdot(t, 2)
    elif kind == "radius":
        p = CF.on(c, r, 250 + rot)
        f.seg(c, p).pdot(c, 2).pdot(p, 2)
    elif kind == "outside":
        a = radians(225 + rot)
        p = (c[0] + (r + 8) * cos(a) - 30 * sin(a), c[1] - (r + 8) * sin(a) - 30 * cos(a))
        q = (c[0] + (r + 8) * cos(a) + 30 * sin(a), c[1] - (r + 8) * sin(a) + 30 * cos(a))
        f.seg(p, q)
    elif kind == "inside":
        p, q = (c[0] - 14, c[1] + 6), (c[0] + 16, c[1] - 10)
        f.seg(p, q)
    save(name, f)


def demos1():
    # Maths Pathway Q1 a-l (worked a-f; homework g-l), drawn after the sheet
    spec = {"mpq1a": ("secant", -5), "mpq1b": ("chord", 60), "mpq1c": ("outside", 0), "mpq1d": ("tangent", 12),
            "mpq1e": ("radius", 30), "mpq1f": ("diam", 0),
            "mpq1g": ("chord2", 0), "mpq1h": ("secant_dot", 0), "mpq1i": ("tangent", -92), "mpq1j": ("radius", 20),
            "mpq1k": ("tangent", 150), "mpq1l": ("secant", 75)}
    for nm, (k, rot) in spec.items():
        panel(nm, k, rot)
    # tutor demo and your turn (our own panels)
    for nm, (k, rot) in {"d1a": ("tangent", 40), "d1b": ("diam", 60), "d1c": ("secant", 30), "d1d": ("inside", 0),
                         "d1e": ("chord", -40), "d1f": ("radius", 100),
                         "y1a": ("chord2", 40), "y1b": ("outside", 90), "y1c": ("tangent", -40), "y1d": ("secant", 110),
                         "y1e": ("radius", 200), "y1f": ("diam", 125)}.items():
        panel(nm, k, rot)


# ---------------------------------------------------------------- Concept 2
def concept2():
    # AMSI p7: chord AB with radii OA, OB (isosceles), equal-radius marks
    f, c, r = circ(140, 128, (72, 66), 52)
    A, B = CF.on(c, r, 80), CF.on(c, r, 200)
    f.seg(A, B).seg(c, A).seg(c, B).pdot(c, 2.2)
    f.tick(c, A, n=2).tick(c, B, n=2)
    f.out(A, c, "A").out(B, c, "B").lab(c, "O", dx=8, dy=8)
    save("c2_iso", f)

    # AMSI p7 theorem: the three lines coincide (dashed axis through O and the midpoint)
    f, c, r = circ(150, 132, (80, 70), 52)
    A, B = CF.on(c, r, 172), CF.on(c, r, 72)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    f.seg(A, B).seg(c, A).seg(c, B).pdot(c, 2.2)
    far = ext(M, c, 2.3)
    f.seg(ext(M, c, -0.45), far, dash="4 3", width=1.2)
    f.right(M, A, c, s=6)
    f.tick(A, M, n=3, t=0.5).tick(M, B, n=3, t=0.5)
    f.tick(c, A, n=2, t=0.55).tick(c, B, n=2, t=0.55)
    f.angle(c, A, M, r=13).angle(c, M, B, r=13)
    f.out(A, c, "A").out(B, c, "B").lab(c, "O", dx=10, dy=4)
    save("c2_thm", f)

    # Maths Pathway: radius perpendicular to a chord / radius bisecting a chord
    for nm in ("c2_mp1", "c2_mp2"):
        f, c, r = circ(130, 120, (65, 56), 46)
        y = c[1] + 30
        hw = sqrt(r * r - 30 * 30)
        P, Q, M = (c[0] - hw, y), (c[0] + hw, y), (c[0], y)
        f.seg(P, Q).seg(c, (c[0], c[1] + r)).pdot(c, 2.2).pdot(P, 2).pdot(Q, 2)
        f.right(M, Q, c, s=6).tick(P, M, n=2, color="blue").tick(M, Q, n=2, color="blue")
        save(nm, f)

    # AMSI Exercise 2: circle radius 1, O top, chord AB, M midpoint, OM perpendicular, angle theta
    f, c, r = circ(150, 130, (75, 62), 56)
    A, B = CF.on(c, r, 208), CF.on(c, r, 332)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    f.seg(A, B).seg(c, A).seg(c, B).seg(c, M).pdot(c, 2.2)
    f.right(M, B, c, s=6).tick(A, M, n=2).tick(M, B, n=2)
    f.angle(c, A, M, r=11).alab(c, A, M, "θ", d=19, size=11)
    label_line(f, c, A, "1", d=8, size=11, side=-1)
    f.out(A, c, "A").out(B, c, "B").lab(c, "O", dx=0, dy=-9).lab(M, "M", dx=0, dy=13)
    save("c2_ex2", f)

    # Maths Pathway Q5a and the demo / your-turn versions: radius perpendicular to a chord
    def q5a(name, left_txt, right_txt):
        f, c, r = circ(140, 120, (70, 54), 48)
        y = c[1] + 28
        hw = sqrt(r * r - 28 * 28)
        P, Q, M = (c[0] - hw, y), (c[0] + hw, y), (c[0], y)
        f.seg(P, Q).seg(c, (c[0], c[1] + r)).pdot(c, 2.2).pdot(P, 2).pdot(Q, 2).pdot(M, 2).pdot((c[0], c[1] + r), 2)
        f.right(M, Q, c, s=6)
        f.text((P[0] + M[0]) / 2, y - 7, left_txt, size=10.5)
        f.text((Q[0] + M[0]) / 2 + 4, y - 7, right_txt, size=11, italic=right_txt.isalpha())
        save(name, f)
    q5a("mpq5a", "2 m", "u")
    q5a("d2a", "3.5 cm", "u")
    q5a("y2a", "4.5 m", "v")

    # Maths Pathway Q5b and versions: radius bisects a vertical chord; q between a segment and the radius
    def q5b(name, given, var):
        f, c, r = circ(150, 132, (64, 68), 54)
        x = c[0] + 26
        hh = sqrt(r * r - 26 * 26)
        T, Bt, M = (x, c[1] - hh), (x, c[1] + hh), (x, c[1])
        E = (c[0] + r, c[1])
        f.seg(T, Bt).seg(c, E).pdot(c, 2.2).pdot(T, 2).pdot(Bt, 2).pdot(E, 2)
        f.tick(T, M, n=2, t=0.45).tick(M, Bt, n=2, t=0.55)
        # point S on the circle with angle TMS = given
        a = radians(90 - given)
        # ray from M at direction (cos a, sin a) in maths sense
        dx, dy = cos(a), sin(a)
        bq = (M[0] - c[0]) * dx + 0
        # solve |M + t d - c| = r for t > 0 (screen coords: y down)
        ux, uy = dx, -dy
        px, py = M[0] - c[0], M[1] - c[1]
        b = px * ux + py * uy
        t = -b + sqrt(b * b - (px * px + py * py - r * r))
        S = (M[0] + t * ux, M[1] + t * uy)
        f.seg(M, S).pdot(S, 2)
        f.angle(M, T, S, r=12).angle(M, S, E, r=16)
        mid = radians(90 - given / 2)
        f.seg((M[0] + 9 * cos(mid), M[1] - 9 * sin(mid)), (M[0] + 9 * cos(mid) + 14, M[1] - 9 * sin(mid) - 64), width=0.8)
        f.text(M[0] + 9 * cos(mid) + 16, M[1] - 9 * sin(mid) - 70, f"{given}°", size=10.5)
        f.alab(M, S, E, var, d=24, size=11, italic=True)
        save(name, f)
    q5b("mpq5b", 30, "q")
    q5b("d2b", 35, "q")
    q5b("y2b", 22, "p")

    # Maths Pathway Q4: O centre, chord AB with midpoint C, OC produced to P on the circle
    f, c, r = circ(150, 136, (75, 60), 54)
    yc = c[1] + 34
    hw = sqrt(r * r - 34 * 34)
    A, B, Cm, P = (c[0] - hw, yc), (c[0] + hw, yc), (c[0], yc), (c[0], c[1] + r)
    f.seg(A, B).seg(c, A).seg(c, B).seg(c, P).pdot(c, 2.2).pdot(A, 2).pdot(B, 2).pdot(Cm, 2).pdot(P, 2)
    f.tick(A, Cm, n=2).tick(Cm, B, n=2)
    f.lab(c, "O", dy=-10, italic=False).lab(A, "A", dx=-9, dy=2, italic=False).lab(B, "B", dx=9, dy=2, italic=False)
    f.lab(Cm, "C", dx=8, dy=10, italic=False).lab(P, "P", dy=12, italic=False)
    save("mpq4", f)


# ---------------------------------------------------------------- Concept 3
def concept3():
    # AMSI p7: major and minor arcs (sectors shaded)
    f, c, r = circ(200, 132, (100, 66), 52)
    A, B = CF.on(c, r, 110), CF.on(c, r, 0)
    f.raw(f'<path d="M{c[0]:.1f},{c[1]:.1f} L{B[0]:.1f},{B[1]:.1f} A{r},{r} 0 0 0 {A[0]:.1f},{A[1]:.1f} Z" fill="#2563eb" fill-opacity="0.12" stroke="none"/>')
    f.raw(f'<path d="M{c[0]:.1f},{c[1]:.1f} L{A[0]:.1f},{A[1]:.1f} A{r},{r} 0 1 0 {B[0]:.1f},{B[1]:.1f} Z" fill="#2563eb" fill-opacity="0.38" stroke="none"/>')
    f.circle(c, r)
    f.seg(c, A).seg(c, B).pdot(c, 2.2)
    f.out(A, c, "A").out(B, c, "B").lab(c, "O", dx=-2, dy=12)
    f.text(172, 18, "minor arc", size=10, italic=False)
    f.text(30, 108, "major arc", size=10, italic=False)
    save("c3_arc", f)

    # AMSI p8 proof: chords AB and PQ equal, triangles AOB and POQ
    f, c, r = circ(140, 128, (70, 64), 52)
    A, B, P, Q = CF.on(c, r, 112), CF.on(c, r, 20), CF.on(c, r, -20), CF.on(c, r, 248)
    f.seg(A, B).seg(P, Q).seg(c, A).seg(c, B).seg(c, P).seg(c, Q).pdot(c, 2.2)
    f.tick(A, B, n=2).tick(P, Q, n=2)
    f.out(A, c, "A").out(B, c, "B").out(P, c, "P").out(Q, c, "Q").lab(c, "O", dx=-10, dy=2)
    save("c3_proof", f)

    # Maths Pathway box: equal chords <-> equal angles at the centre
    for nm, mark in (("c3_mp1", "chords"), ("c3_mp2", "angles")):
        f, c, r = circ(130, 120, (65, 58), 46)
        A, B = CF.on(c, r, 125), CF.on(c, r, 80)
        P, Q = CF.on(c, r, 340), CF.on(c, r, 255)
        # the sheet's chords subtend about 50 deg and 85 deg drawn; keep two equal chords
        A, B = CF.on(c, r, 150), CF.on(c, r, 85)
        P, Q = CF.on(c, r, -15), CF.on(c, r, -80)
        f.seg(A, B).seg(P, Q).seg(c, A).seg(c, B).seg(c, P).seg(c, Q).pdot(c, 2.2)
        if mark == "chords":
            f.tick(A, B, n=1, color="blue").tick(P, Q, n=1, color="blue")
            f.angle(c, A, B, r=8, color="blue").angle(c, P, Q, r=8, color="faint")
        else:
            f.angle(c, A, B, r=8, color="blue").angle(c, P, Q, r=8, color="blue")
            f.tick(A, B, n=1, color="faint").tick(P, Q, n=1, color="faint")
        save(nm, f)

    # Maths Pathway Q3b style: two equal chords, one central angle given, the other y
    def q3b(name, chord, given, var):
        f, c, r = circ(170, 140, (85, 70), 60)
        A, B = CF.on(c, r, 158), CF.on(c, r, 200 + 0)
        ang = given
        A, B = CF.on(c, r, 160 - 0), CF.on(c, r, 160 + ang + 0)
        A = CF.on(c, r, 180 - ang / 2 + 22)
        B = CF.on(c, r, 180 + ang / 2 + 22)
        P = CF.on(c, r, 22 - ang / 2 - 24)
        Q = CF.on(c, r, 22 + ang / 2 - 24)
        A, B = CF.on(c, r, 160 - ang / 2 + 0), CF.on(c, r, 160 + ang / 2 + 40)
        # draw as on the sheet: chord on the left (vertical-ish) and on the right
        A, B = CF.on(c, r, 165), CF.on(c, r, 165 + ang)
        P, Q = CF.on(c, r, 15 - ang), CF.on(c, r, 15)
        A, B = B, A
        f.seg(A, B).seg(P, Q).seg(c, A).seg(c, B).seg(c, P).seg(c, Q).pdot(c, 2.2)
        for p in (A, B, P, Q):
            f.pdot(p, 2)
        f.angle(c, A, B, r=12).angle(c, P, Q, r=12, n=2)
        f.alab(c, A, B, f"{given}°", d=24, size=10.5)
        f.alab(c, P, Q, var, d=24, size=11, italic=True)
        chord_lab(f, A, B, c, chord, d=r * (1 - cos(radians(given / 2))) + 17, size=10)
        chord_lab(f, P, Q, c, chord, d=r * (1 - cos(radians(given / 2))) + 17, size=10)
        save(name, f)
    q3b("mpq3b", "7 m", 55, "y")
    q3b("d3a", "9 m", 48, "y")
    q3b("y3a", "5 m", 62, "z")

    # Maths Pathway Q3a style: two chords subtending equal angles at the centre
    def q3a(name, chord, given, var):
        f, c, r = circ(190, 160, (95, 80), 70)
        A, B = CF.on(c, r, 150), CF.on(c, r, 150 - given)
        P, Q = CF.on(c, r, 210), CF.on(c, r, 210 + given)
        f.seg(A, B).seg(P, Q).seg(c, A).seg(c, B).seg(c, P).seg(c, Q).pdot(c, 2.2)
        for p in (A, B, P, Q):
            f.pdot(p, 2)
        f.angle(c, A, B, r=7, n=2, gap=2.6).angle(c, P, Q, r=7, n=2, gap=2.6)
        dd = 0.62 * r * cos(radians(given / 2))
        f.alab(c, A, B, f"{given}°", d=dd, size=10.5)
        f.alab(c, P, Q, f"{given}°", d=dd, size=10.5)
        chord_lab(f, A, B, c, chord, d=9, size=10)
        chord_lab(f, P, Q, c, var, d=10, size=11, italic=True)
        save(name, f)
    q3a("mpq3a", "2 cm", 120, "x")
    q3a("d3b", "3 cm", 105, "x")
    q3a("y3b", "2.5 cm", 130, "x")

    # Maths Pathway Q3d: concentric circles; large chords 6 m, small chords 3 m and w
    f = CF(240, 206)
    c = (120, 102)
    R, r = 84, 46
    f.circle(c, R).circle(c, r).pdot(c, 2.2)
    a1, a2 = 158, 158 + 65           # first pair of radii (65 deg)
    b1, b2 = -40, 25                 # second pair (t)
    b1, b2 = 0, -65
    L1, L2 = CF.on(c, R, a1), CF.on(c, R, a2)
    S1, S2 = CF.on(c, r, a1), CF.on(c, r, a2)
    M1, M2 = CF.on(c, R, b1), CF.on(c, R, b2)
    T1, T2 = CF.on(c, r, b1), CF.on(c, r, b2)
    for p, q in ((c, L1), (c, L2), (c, M1), (c, M2), (L1, L2), (M1, M2), (S1, S2), (T1, T2)):
        f.seg(p, q, width=1.3)
    for p in (L1, L2, S1, S2, M1, M2, T1, T2):
        f.pdot(p, 2)
    f.angle(c, S1, S2, r=9).angle(c, T1, T2, r=9, n=2)
    f.seg((c[0] - 8, c[1] - 6), (c[0] - 34, c[1] - 66), width=0.8).text(c[0] - 38, c[1] - 72, "65°", size=10.5)
    f.alab(c, T1, T2, "t", d=17, size=11, italic=True)
    chord_lab(f, L1, L2, c, "6 m", d=R * (1 - cos(radians(32.5))) + 17, size=10)
    chord_lab(f, S1, S2, c, "3 m", d=11, size=10, inside=True)
    chord_lab(f, M1, M2, c, "6 m", d=R * (1 - cos(radians(32.5))) + 17, size=10)
    chord_lab(f, T1, T2, c, "w", d=10, size=11, inside=True, italic=True)
    save("mpq3d", f)

    # Maths Pathway Q2: O centre; A, B, C, D on the circle, angle AOB = angle COD marked
    f, c, r = circ(160, 150, (80, 70), 62)
    A, B, Cc, D = CF.on(c, r, 202), CF.on(c, r, 258), CF.on(c, r, 282), CF.on(c, r, 338)
    for p in (A, B, Cc, D):
        f.seg(c, p).pdot(p, 2)
    f.seg(A, B).seg(Cc, D).pdot(c, 2.2)
    f.angle(c, A, B, r=10, n=2).angle(c, Cc, D, r=10, n=2)
    f.lab(c, "O", dy=-10, italic=False).lab(A, "A", dx=-9, dy=2, italic=False).lab(B, "B", dx=-2, dy=13, italic=False)
    f.lab(Cc, "C", dx=4, dy=13, italic=False).lab(D, "D", dx=9, dy=2, italic=False)
    save("mpq2", f)


# ---------------------------------------------------------------- Concept 4
def semi_fig(name, angA=None, angB=None, lab_a=None, lab_b=None, show_radius=False, right=True, rect=False, pdeg=110):
    f, c, r = circ(160, 132, (80, 70), 56)
    A, B = CF.on(c, r, 198), CF.on(c, r, 18)
    P = CF.on(c, r, pdeg)
    f.seg(A, B).seg(A, P).seg(B, P).pdot(c, 2.2)
    if show_radius:
        f.seg(P, c, dash="3 3", width=1.2)
    if right:
        f.right(P, A, B, s=6)
    if lab_a:
        f.alab(A, P, B, lab_a, d=22, size=10.5, italic=lab_a.isalpha() or lab_a in "αβ")
    if lab_b:
        f.alab(B, A, P, lab_b, d=22, size=10.5, italic=lab_b in "αβ")
    if rect:
        Q = CF.on(c, r, pdeg + 180)
        f.seg(P, Q, dash="3 3", width=1.2).seg(A, Q, dash="3 3", width=1.2).seg(B, Q, dash="3 3", width=1.2)
        f.out(Q, c, "Q")
    f.out(A, c, "A").out(B, c, "B").out(P, c, "P").lab(c, "O", dx=3, dy=12)
    save(name, f)


def concept4():
    semi_fig("c4_semi")
    semi_fig("c4_proof", lab_a="α", lab_b="β", show_radius=True)
    semi_fig("c4_ex3", lab_a="α", lab_b="β", show_radius=True, right=False, rect=True)
    # tutor demo / your turn: same diagram, one angle given (drawn to scale)
    for nm, a_given, b_given in (("d4a", 28, None), ("y4a", None, 57)):
        if a_given:
            pdeg = 180 - 2 * a_given          # angle POB = 2 * angle A  (P on the circle)
            semi_fig(nm, lab_a=f"{a_given}°", show_radius=True, right=False, pdeg=pdeg)
        else:
            pdeg = 2 * b_given
            semi_fig(nm, lab_b=f"{b_given}°", show_radius=True, right=False, pdeg=pdeg)

    # AMSI p10: constructing a right angle at the endpoint A of an interval AX
    f = CF(200, 140)
    A, X = (24, 112), (190, 112)
    c = (78, 66)
    r = hypot(A[0] - c[0], A[1] - c[1])
    P = (2 * c[0] - A[0], A[1])                   # second intersection with AX (horizontal line)
    Q = (2 * c[0] - P[0], 2 * c[1] - P[1])
    f.circle(c, r).seg(A, X).seg(P, Q, dash="4 3", width=1.2).seg(A, (A[0], Q[1] - 12), dash="4 3", width=1.2)
    f.pdot(c, 2.2).tick(Q, c, n=2).tick(c, P, n=2).right(A, X, Q, s=6)
    f.lab(A, "A", dx=-4, dy=13).lab(P, "P", dx=2, dy=13).lab(X, "X", dx=0, dy=13).lab(Q, "Q", dx=-10, dy=-4).lab(c, "O", dx=9, dy=-5)
    save("c4_constr", f)

    # AMSI p10: converse theorem, rectangle ACBR with M the midpoint of AB
    f = CF(170, 140)
    C, A, B, R = (30, 120), (150, 120), (30, 18), (150, 18)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    f.seg(C, A).seg(C, B).seg(A, B).seg(B, R, dash="4 3", width=1.2).seg(R, A, dash="4 3", width=1.2).seg(C, R, dash="4 3", width=1.2)
    f.right(C, A, B, s=7).pdot(M, 2.4).tick(B, M, n=2).tick(M, A, n=2)
    f.lab(C, "C", dx=-9, dy=6).lab(A, "A", dx=9, dy=6).lab(B, "B", dx=-9, dy=-4).lab(R, "R", dx=9, dy=-4).lab(M, "M", dx=11, dy=-2)
    save("c4_conv", f)

    # AMSI Exercise 4: building front and the photographer (right angle)
    f = CF(190, 110)
    f.poly([(20, 10), (170, 10), (170, 34), (20, 34)], color="blue", opacity=0.5)
    Ph = (120, 96)
    f.seg((22, 36), Ph, dash="4 3", width=1.2).seg((168, 36), Ph, dash="4 3", width=1.2).right(Ph, (22, 36), (168, 36), s=6)
    save("c4_ex4", f)

    # AMSI Exercise 5: plank AB against the wall OB, midpoint M
    f = CF(150, 160)
    O, A, B = (40, 150), (120, 150), (40, 10)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    f.seg((40, 2), O).seg(O, (146, 150)).seg(B, A).right(O, A, B, s=7).pdot(M, 2.4)
    f.tick(B, M, n=2).tick(M, A, n=2)
    f.lab(O, "O", dx=0, dy=13).lab(A, "A", dx=0, dy=13).lab(B, "B", dx=-10, dy=2).lab(M, "M", dx=11, dy=-2)
    label_line(f, B, M, "ℓ/2", d=14, size=10.5, side=-1)
    label_line(f, M, A, "ℓ/2", d=14, size=10.5, side=-1)
    save("c4_ex5", f)

    # Maths Pathway 'Arcs and Angles' Q7 a-c and Q8a
    def a7(name, kind):
        f, c, r = circ(140, 124, (70, 62), 52)
        if kind == "a":               # vertical diameter, P on the right; centre angle 180 marked; x at P
            T, Bt = CF.on(c, r, 95), CF.on(c, r, 275)
            P = CF.on(c, r, 30)
            f.seg(T, Bt).seg(T, P).seg(P, Bt).pdot(c, 2.4)
            f.reflex(c, T, Bt, r=8, n=2) if False else f.items.append(
                f'<path d="M{c[0] + 8 * cos(radians(95)):.1f},{c[1] - 8 * sin(radians(95)):.1f} A8,8 0 0 0 {c[0] + 8 * cos(radians(275)):.1f},{c[1] - 8 * sin(radians(275)):.1f}" fill="none" stroke="#1f2a37" stroke-width="1.1"/>'
                f'<path d="M{c[0] + 11 * cos(radians(95)):.1f},{c[1] - 11 * sin(radians(95)):.1f} A11,11 0 0 0 {c[0] + 11 * cos(radians(275)):.1f},{c[1] - 11 * sin(radians(275)):.1f}" fill="none" stroke="#1f2a37" stroke-width="1.1"/>')
            f.text(c[0] - 30, c[1] + 2, "180°", size=10.5)
            f.angle(P, T, Bt, r=12, n=2).alab(P, T, Bt, "x", d=24, size=11, italic=True)
            for p in (T, Bt, P):
                f.pdot(p, 2)
        elif kind == "b":             # horizontal diameter, y at centre (above), P below with z
            L, R_ = CF.on(c, r, 178), CF.on(c, r, 2)
            P = CF.on(c, r, 268)
            f.seg(L, R_).seg(L, P).seg(R_, P).pdot(c, 2.4)
            f.items.append(f'<path d="M{c[0] - 8:.1f},{c[1]:.1f} A8,8 0 0 1 {c[0] + 8:.1f},{c[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.1"/>'
                           f'<path d="M{c[0] - 11:.1f},{c[1]:.1f} A11,11 0 0 1 {c[0] + 11:.1f},{c[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.1"/>')
            f.text(c[0], c[1] - 19, "y", size=11, italic=True)
            f.angle(P, L, R_, r=12).alab(P, L, R_, "z", d=24, size=11, italic=True)
            for p in (L, R_, P):
                f.pdot(p, 2)
        else:                         # diameter from upper right to lower left through the centre; x at P (upper left)
            T, Bt = CF.on(c, r, 70), CF.on(c, r, 250)
            P = CF.on(c, r, 140)
            f.seg(T, Bt).seg(P, T).seg(P, Bt).pdot(c, 2.4)
            f.angle(P, T, Bt, r=12, n=2).alab(P, T, Bt, "x", d=24, size=11, italic=True)
            for p in (T, Bt, P):
                f.pdot(p, 2)
        save(name, f)
    a7("mpa7a", "a")
    a7("mpa7b", "b")
    a7("mpa7c", "c")
    f, c, r = circ(150, 110, (75, 60), 48)
    L, R_ = (c[0] - r, c[1]), (c[0] + r, c[1])
    P = CF.on(c, r, 96)
    f.seg(L, R_).seg(L, P).seg(P, R_).pdot(c, 2.4).pdot(L, 2).pdot(R_, 2).pdot(P, 2)
    f.angle(P, L, R_, r=12, n=2).alab(P, L, R_, "a", d=25, size=11, italic=True)
    save("mpa8a", f)


# ---------------------------------------------------------------- Maths Pathway Q6 a-c and AMSI Exercise 1
def q6():
    # 6a: circles centres O and P meet; line A-B-C-D; OR perpendicular to the line at B, PS perpendicular at C
    f = CF(260, 190)
    k = 13.0
    # coordinates in units: line along direction u; B at 0, C at 4, A at -4, D at 8 (AB = BC = CD by construction)
    base = (124, 120)
    ang = radians(70)                         # the line A..D rises to the right on the page
    u = (cos(ang), -sin(ang))
    n = (sin(ang), cos(ang))                  # unit normal, pointing to the page left/down side
    def pt(s, h=0.0):
        return (base[0] + k * (s * u[0] + h * n[0]), base[1] + k * (s * u[1] + h * n[1]))
    h1 = 4.1
    O, P = pt(0, -h1 * 1.0), pt(4, h1)       # O on one side of the line (foot B), P on the other (foot C)
    O = pt(0, 0)
    O = (base[0] - k * h1 * n[0] * -1, 0)
    Bp, Cp = pt(0), pt(4)
    O = (Bp[0] - k * h1 * n[0], Bp[1] - k * h1 * n[1])
    P = (Cp[0] + k * h1 * n[0], Cp[1] + k * h1 * n[1])
    rO = k * sqrt(16 + h1 * h1)
    A, D = pt(-4), pt(8)
    f.circle(O, rO).circle(P, rO)
    f.seg(A, D)
    # R: on circle P along OB produced; S: on circle O along PC produced
    def hit(cen, rad, frm, to):
        dx, dy = to[0] - frm[0], to[1] - frm[1]
        L = hypot(dx, dy); dx, dy = dx / L, dy / L
        px, py = frm[0] - cen[0], frm[1] - cen[1]
        b = px * dx + py * dy
        t = -b + sqrt(b * b - (px * px + py * py - rad * rad))
        return (frm[0] + t * dx, frm[1] + t * dy)
    R = hit(O, rO, Bp, (Bp[0] + (Bp[0] - O[0]), Bp[1] + (Bp[1] - O[1])))     # radius OR of circle O through B
    S = hit(P, rO, Cp, (Cp[0] + (Cp[0] - P[0]), Cp[1] + (Cp[1] - P[1])))     # radius PS of circle P through C
    f.seg(O, R).seg(P, S)
    for p in (O, P, A, Bp, Cp, D, R, S):
        f.pdot(p, 2.2)
    f.right(Bp, R, Cp, s=5).right(Cp, S, Bp, s=5)
    f.lab(O, "O", dx=-10, dy=0, italic=False).lab(P, "P", dx=10, dy=2, italic=False)
    f.lab(A, "A", dx=0, dy=12, italic=False).lab(D, "D", dx=0, dy=-9, italic=False)
    f.lab(Bp, "B", dx=-9, dy=6, italic=False).lab(Cp, "C", dx=10, dy=-4, italic=False)
    f.lab(R, "R", dx=9, dy=6, italic=False).lab(S, "S", dx=-12, dy=-2, italic=False)
    save("mpq6a", f)

    # 6b: circle centre G; chord AD with midpoint H (GH perpendicular); chord BF through H, I its midpoint on GE
    f = CF(200, 184)
    G = (92, 74)
    r = 76
    yH = G[1] + 66
    hw = sqrt(r * r - 66 * 66)
    A, D, H = (G[0] - hw, yH), (G[0] + hw, yH), (G[0], yH)
    th = radians(52)                                  # angle IHD = 52 deg
    d = (cos(th), -sin(th))
    # chord through H in direction d: intersections with the circle
    px, py = H[0] - G[0], H[1] - G[1]
    b = px * d[0] + py * d[1]
    disc = sqrt(b * b - (px * px + py * py - r * r))
    F = (H[0] + (-b + disc) * d[0], H[1] + (-b + disc) * d[1])
    Bq = (H[0] + (-b - disc) * d[0], H[1] + (-b - disc) * d[1])
    I = foot(G, Bq, F)
    E = ext(G, I, r / hypot(I[0] - G[0], I[1] - G[1]))
    C = (G[0], G[1] + r)
    f.circle(G, r).seg(A, D).seg(G, C).seg(Bq, F).seg(G, E)
    for p in (A, D, H, F, Bq, I, E, G, C):
        f.pdot(p, 2.2)
    f.lab(G, "G", dx=-2, dy=-10, italic=False).lab(A, "A", dx=-6, dy=12, italic=False).lab(D, "D", dx=8, dy=12, italic=False)
    f.lab(H, "H", dx=-9, dy=-7, italic=False).lab(F, "F", dx=9, dy=-4, italic=False).lab(Bq, "B", dx=-9, dy=10, italic=False)
    f.lab(C, "C", dx=6, dy=12, italic=False).lab(I, "I", dx=-3, dy=13, italic=False).lab(E, "E", dx=9, dy=6, italic=False)
    save("mpq6b", f)

    # 6c: small circle with diameter AB; C on it with BC = 4, AC = 3; large circle with diameter BE (C on BE); line AC meets it at D
    k = 21.0
    B = (150, 168)
    A = (B[0] - 5 * k * cos(radians(24)), B[1] - 5 * k * sin(radians(24)))
    # C on the circle with diameter AB, with AC = 3 and BC = 4 (C on the upper side)
    ab = (A[0] - B[0], A[1] - B[1])
    L = hypot(*ab)
    ub = (ab[0] / L, ab[1] / L)
    angB = asin(3 / 5)
    rot = (ub[0] * cos(angB) - ub[1] * sin(angB), ub[0] * sin(angB) + ub[1] * cos(angB))
    C = (B[0] + 4 * k * rot[0], B[1] + 4 * k * rot[1])
    if C[1] > ((A[1] + B[1]) / 2):
        rot = (ub[0] * cos(-angB) - ub[1] * sin(-angB), ub[0] * sin(-angB) + ub[1] * cos(-angB))
        C = (B[0] + 4 * k * rot[0], B[1] + 4 * k * rot[1])
    m1 = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    # large circle: centre on line BC, equidistant from A and B
    dx, dy = C[0] - B[0], C[1] - B[1]
    t = ((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2) / (2 * ((A[0] - B[0]) * dx + (A[1] - B[1]) * dy))
    O2 = (B[0] + t * dx, B[1] + t * dy)
    R2 = hypot(O2[0] - B[0], O2[1] - B[1])
    E = (2 * O2[0] - B[0], 2 * O2[1] - B[1])
    D = (2 * C[0] - A[0], 2 * C[1] - A[1])
    f = CF(250, 230)
    f.circle(m1, 2.5 * k).circle(O2, R2)
    f.seg(A, B).seg(B, E).seg(A, D)
    for p in (A, B, C, D, E, m1, O2):
        f.pdot(p, 2.2)
    f.lab(A, "A", dx=-10, dy=0, italic=False).lab(B, "B", dx=6, dy=13, italic=False).lab(C, "C", dx=2, dy=-11, italic=False)
    f.lab(D, "D", dx=9, dy=-5, italic=False).lab(E, "E", dx=-6, dy=-9, italic=False)
    save("mpq6c", f)

    # AMSI Exercise 1: a line l; the line l with points P and Q
    f = CF(170, 104)
    f.seg((10, 42), (160, 6)).text(98, 16, "ℓ", size=13, italic=True)
    f.seg((14, 100), (160, 56)).text(152, 46, "ℓ", size=13, italic=True)
    P, Q = (46, 90.4), (112, 70.5)
    f.pdot(P, 2.4).pdot(Q, 2.4).lab(P, "P", dx=0, dy=13).lab(Q, "Q", dx=2, dy=-10)
    save("c1_ex1", f)


# ---------------------------------------------------------------- past papers
def pastpapers():
    # PP1: Sydney Boys 2020 Q40(b): Diagram 1 (sphere with a dent) and Diagram 2 (cross-section)
    f = CF(170, 160)
    c, r = (84, 80), 70
    f.circle(c, r, width=1.3)
    f.raw(f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="{r}" ry="9" fill="none" stroke="#8a96a3" stroke-width="0.8"/>')
    for k in (0.15, 0.35, 0.55, 0.75, 0.92):
        f.raw(f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="{r * k:.1f}" ry="{r}" fill="none" stroke="#8a96a3" stroke-width="0.6"/>')
    f.raw(f'<ellipse cx="118" cy="40" rx="18" ry="12" transform="rotate(35 118 40)" fill="#ffffff" stroke="#1f2a37" stroke-width="1.6"/>')
    f.text(84, 158, "Diagram 1", size=9.5, italic=False, color="faint")
    save("pp1a", f)
    f = CF(220, 190)
    A = (82, 92)
    R1 = 70.0
    s = R1 / 100
    Bc = (A[0] + 120 * s * cos(radians(52)), A[1] - 120 * s * sin(radians(52)))
    R2 = 40 * s
    # intersections X, Y of the two circles
    dd = 120 * s
    a = (R1 * R1 - R2 * R2 + dd * dd) / (2 * dd)
    h = sqrt(R1 * R1 - a * a)
    ux, uy = (Bc[0] - A[0]) / dd, (Bc[1] - A[1]) / dd
    Mx, My = A[0] + a * ux, A[1] + a * uy
    X = (Mx + h * uy, My - h * ux)
    Y = (Mx - h * uy, My + h * ux)
    if X[0] > Y[0]:
        X, Y = Y, X
    # large circle drawn thick except the dent; small circle faint, its inner arc thick
    aX, aY = _ang(A, X), _ang(A, Y)
    f.raw(f'<path d="M{X[0]:.1f},{X[1]:.1f} A{R1},{R1} 0 1 0 {Y[0]:.1f},{Y[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="2.2"/>')
    f.circle(Bc, R2, color="faint", width=0.8)
    f.raw(f'<path d="M{X[0]:.1f},{X[1]:.1f} A{R2},{R2} 0 0 0 {Y[0]:.1f},{Y[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="2.2"/>')
    f.seg(A, X, color="faint", width=0.8).seg(A, Y, color="faint", width=0.8).seg(Bc, X, color="faint", width=0.8).seg(Bc, Y, color="faint", width=0.8)
    f.pdot(A, 1.8).pdot(Bc, 1.8)
    f.lab(A, "A", dx=-2, dy=12, size=10).lab(Bc, "B", dx=9, dy=2, size=10).lab(X, "X", dx=-4, dy=-7, size=10).lab(Y, "Y", dx=8, dy=8, size=10)
    label_line(f, A, X, "100", d=8, size=9.5, t=0.6, side=1)
    label_line(f, X, Bc, "40", d=7, size=9.5, t=0.45, side=1)
    f.text(176, 140, "AB = 120", size=9.5, italic=True)
    f.text(110, 182, "Diagram 2", size=9.5, italic=False, color="faint")
    save("pp1b", f)

    # PP2: Sydney Boys 2022 Part A Q9: regular pentagon ABCDE in a circle, then AF a diameter, shaded kite
    for nm, second in (("pp2a", False), ("pp2b", True)):
        f = CF(170, 160)
        c, r = (85, 80), 66
        f.circle(c, r, dash="3 3", width=1.0)
        V = {L: CF.on(c, r, 90 + 72 * i) for i, L in enumerate("AEDCB")}
        F = CF.on(c, r, 270)
        if second:
            f.poly([V["E"], c, V["B"], F], color="faint", opacity=0.45, stroke="ink", width=1.2)
            f.seg(V["A"], F, width=1.2)
        f.poly([V[L] for L in "ABCDE"], color=None, opacity=0, width=2.0)
        if not second:
            for L in "ABCDE":
                f.seg(c, V[L], dash="3 3", width=1.0)
        f.pdot(c, 1.8).lab(c, "O", dx=-7, dy=9 if not second else -5, size=9.5, italic=False)
        for L in "ABCDE":
            f.out(V[L], c, L, d=10, size=9.5, italic=False)
        if second:
            f.lab(F, "F", dx=0, dy=12, size=9.5, italic=False)
        save(nm, f)

    # PP3: Sydney Boys 2021 Part E(a): diameter AOD, radius 9, angle ADC = 35, shaded segment ABC
    f = CF(250, 196)
    c, r = (110, 96), 82
    A, D = (c[0] - r, c[1]), (c[0] + r, c[1])
    C = CF.on(c, r, 117)                   # drawn near the source (not to scale, as the paper says)
    f.raw(f'<path d="M{A[0]:.1f},{A[1]:.1f} A{r},{r} 0 0 1 {C[0]:.1f},{C[1]:.1f} Z" fill="#8a96a3" fill-opacity="0.7" stroke="none"/>')
    f.circle(c, r).seg(A, D).seg(A, C).seg(C, D).seg(c, C)
    f.angle(D, A, C, r=20).alab(D, A, C, "35°", d=34, size=10.5)
    f.lab(A, "A", dx=-9, dy=2).lab(D, "D", dx=10, dy=2).lab(C, "C", dx=-2, dy=-9).lab(c, "O", dx=0, dy=13)
    B = CF.on(c, r, 145)
    f.out(B, c, "B", d=11)
    label_line(f, A, c, "9 cm", d=9, size=10, side=1)
    label_line(f, c, C, "9 cm", d=10, size=10, side=1, t=0.55)
    f.text(232, 14, "Diagram NOT", size=9.5, italic=False).text(240, 27, "accurately drawn", size=9.5, italic=False)
    save("pp3", f)

    # PP4: Merewether 2023 Section III Part B Q2: circle centre O, chord IK, OJ perpendicular to IK
    f = CF(160, 150)
    c, r = (80, 80), 64
    I, K = CF.on(c, r, 145), CF.on(c, r, 35)
    J = ((I[0] + K[0]) / 2, I[1])
    f.circle(c, r, color="rose").seg(I, K, color="rose").seg(c, I, color="rose").seg(c, K, color="rose").seg(c, J, color="rose")
    f.pdot(c, 2.6, color="rose")
    f.lab(I, "I", dx=-6, dy=-7).lab(K, "K", dx=6, dy=-7).lab(J, "J", dx=0, dy=-8).lab(c, "O", dx=-3, dy=14)
    save("pp4", f)


if __name__ == "__main__":
    concept1()
    demos1()
    concept2()
    concept3()
    concept4()
    q6()
    pastpapers()
