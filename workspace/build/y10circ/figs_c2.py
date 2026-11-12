"""Figures for Lesson C2 (Angles at the centre and circumference). Run: python3 figs_c2.py

Sources: AMSI TIMES Circle Geometry pp. 11-17 (concept figures, Exercises 6-13); Maths Pathway
'Arcs and Angles in Circles' (boxes, Q1-Q6, Q8(b)-(d)); the past papers. Each figure follows the
layout of the source diagram (point positions read off the page), not necessarily drawn to scale.
"""
from math import sin, cos, radians, degrees, sqrt, atan2, hypot
from figs import CF, ext, foot
from figs import save as _save


def save(name, f):
    _save(name, f, rmax=30)


def F(name, pts, segs=(), dashed=(), angs=(), letters=None, w=150, h=140, r=54, c=None, dot_o=True,
      dots=True, extra=None, shade=None, circle=True, ldist=11, lsize=11.5, litalic=True, ccolor="ink"):
    """Circle figure. pts: key -> degrees on the circle, 'O' for the centre, or (x, y) in pixels.
    segs / dashed: 2-character strings of point keys. angs: (v, p, q, text, n, reflex, d).
    letters: key -> printed label (placed outward from the centre)."""
    f = CF(w, h)
    c = c or (w / 2, h / 2)
    P = {}
    for k, v in pts.items():
        if v == "O":
            P[k] = c
        elif isinstance(v, tuple):
            P[k] = v
        else:
            P[k] = CF.on(c, r, v)
    if shade:
        shade(f, P, c, r)
    if circle:
        f.circle(c, r, color=ccolor)
    for s in segs:
        f.seg(P[s[0]], P[s[1]])
    for s in dashed:
        f.seg(P[s[0]], P[s[1]], dash="4 3", width=1.2)
    for a in angs:
        v, p, q, txt = a[0], a[1], a[2], a[3]
        n = a[4] if len(a) > 4 else 1
        rf = a[5] if len(a) > 5 else False
        d = a[6] if len(a) > 6 else 24
        rr = a[7] if len(a) > 7 else 11
        if rf:
            f.reflex(P[v], P[p], P[q], r=rr - 3, n=n)
        else:
            f.angle(P[v], P[p], P[q], r=rr, n=n)
        if txt:
            it = txt.isalpha() or txt in ("α", "β", "γ", "δ", "θ")
            f.alab(P[v], P[p], P[q], txt, d=d, size=11, italic=it, reflex=rf)
    if dots:
        for k, v in pts.items():
            if v != "O" and not isinstance(v, tuple):
                f.pdot(P[k], 2)
    if dot_o and "O" in pts.values():
        f.pdot(c, 2.4)
    for k, t in (letters or {}).items():
        if pts[k] == "O":
            continue
        f.out(P[k], c, t, d=ldist, size=lsize, italic=litalic)
    if extra:
        extra(f, P, c, r)
    save(name, f)
    return P


def below(f, c, rr=9, n=1):
    for k in range(n):
        q = rr + 3 * k
        f.raw(f'<path d="M{c[0] - q:.1f},{c[1]:.1f} A{q},{q} 0 0 0 {c[0] + q:.1f},{c[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.1"/>')


def lab_o(txt, dx, dy, it=True):
    def e(f, P, c, r):
        f.text(c[0] + dx, c[1] + dy, txt, size=11.5, italic=it)
    return e


# ---------------------------------------------------------------- AMSI concept figures
def amsi():
    L = {k: k for k in "ABPQOCD"}
    # p11: minor arc, semicircle, major arc
    F("c2_arcs1", {"A": 205, "B": 280, "P": 70, "O": "O"}, segs=("AP", "BP", "OA", "OB"),
      angs=(("P", "A", "B", ""), ("O", "A", "B", "", 1, False, 0, 9)), letters={"A": "A", "B": "B", "P": "P"}, extra=lab_o("O", 8, -9))
    F("c2_arcs2", {"A": 180, "B": 0, "P": 65, "O": "O"}, segs=("AP", "BP", "AB"),
      letters={"A": "A", "B": "B", "P": "P"},
      extra=lambda f, P, c, r: (f.right(P["P"], P["A"], P["B"], s=6), below(f, c), f.text(c[0], c[1] + 22, "180°", size=10.5)))
    F("c2_arcs3", {"A": 150, "B": 15, "P": 70, "O": "O"}, segs=("AP", "BP", "OA", "OB"),
      angs=(("P", "A", "B", ""), ("O", "A", "B", "", 1, True, 0, 9)), letters={"A": "A", "B": "B", "P": "P"}, extra=lab_o("O", 2, -9))
    # p11 proof, three cases
    F("c2_case1", {"A": 210, "B": 330, "P": 90, "Q": 270, "O": "O"}, segs=("AP", "BP", "OA", "OB"), dashed=("PQ",),
      angs=(("P", "A", "B", ""), ("O", "A", "B", "", 1, False, 0, 9), ("A", "O", "P", "α", 1, False, 22), ("B", "P", "O", "β", 1, False, 22)),
      letters={"A": "A", "B": "B", "P": "P", "Q": "Q"}, extra=lab_o("O", 9, -7))
    F("c2_case2", {"A": 210, "B": 300, "P": 30, "O": "O"}, segs=("AP", "BP", "OB"),
      angs=(("P", "A", "B", ""), ("O", "A", "B", "", 1, False, 0, 9), ("B", "P", "O", "β", 1, False, 22)),
      letters={"A": "A", "B": "B", "P": "P"}, extra=lab_o("O", -6, -10))
    F("c2_case3", {"A": 215, "B": 300, "P": 3, "Q": 183, "O": "O"}, segs=("AP", "BP", "OA", "OB"), dashed=("QP",),
      angs=(("P", "A", "B", ""), ("O", "A", "B", "", 1, False, 0, 9), ("A", "O", "P", "α", 1, False, 24), ("B", "O", "P", "β", 1, False, 22)),
      letters={"A": "A", "B": "B", "P": "P", "Q": "Q"}, extra=lab_o("O", 0, -11))
    # p12 example: punter at P, horse from A to B
    F("c2_punter", {"A": 25, "B": 320, "P": 255, "O": "O"}, dashed=("OA", "OB", "PA", "PB"),
      angs=(("O", "A", "B", "2θ", 1, False, 18), ("P", "A", "B", "θ", 1, False, 22)), letters={"A": "A", "B": "B", "P": "P"},
      extra=lab_o("O", -9, 0))
    # p12 angles on the same arc
    def arcdash(f, P, c, r):
        a0, a1 = 210, 330
        pa, pb = CF.on(c, r, a0), CF.on(c, r, a1)
        f.raw(f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{r},{r} 0 0 0 {pb[0]:.1f},{pb[1]:.1f}" fill="none" stroke="#ffffff" stroke-width="3"/>'
              f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{r},{r} 0 0 0 {pb[0]:.1f},{pb[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.4" stroke-dasharray="4 3"/>')
        f.text(c[0] + 5, c[1] - 9, "O", size=11.5)
    F("c2_samearc", {"A": 210, "B": 330, "P": 100, "Q": 60, "O": "O"}, segs=("AP", "BP", "AQ", "BQ"), dashed=("OA", "OB"),
      angs=(("P", "A", "B", ""), ("Q", "A", "B", ""), ("O", "A", "B", "", 1, False, 0, 8)), letters={"A": "A", "B": "B", "P": "P", "Q": "Q"}, extra=arcdash)
    # p13 alternative terminology: angle in the major segment, two angles in the same segment
    def segshade(a0, a1):
        def s(f, P, c, r):
            pa, pb = CF.on(c, r, a0), CF.on(c, r, a1)
            f.raw(f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{r},{r} 0 1 0 {pb[0]:.1f},{pb[1]:.1f} Z" fill="#2563eb" fill-opacity="0.16" stroke="none"/>')
        return s

    def dash_minor(a0, a1):
        def e(f, P, c, r):
            pa, pb = CF.on(c, r, a0), CF.on(c, r, a1)
            f.raw(f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{r},{r} 0 0 0 {pb[0]:.1f},{pb[1]:.1f}" fill="none" stroke="#ffffff" stroke-width="3"/>'
                  f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{r},{r} 0 0 0 {pb[0]:.1f},{pb[1]:.1f}" fill="none" stroke="#1f2a37" stroke-width="1.4" stroke-dasharray="4 3"/>')
        return e
    F("c2_seg1", {"A": 215, "B": 345, "P": 75}, segs=("AB", "AP", "BP"), angs=(("P", "A", "B", ""),), letters={"A": "A", "B": "B", "P": "P"},
      shade=segshade(345, 215), extra=dash_minor(215, 345), w=140, h=124, r=50)
    F("c2_seg2", {"A": 240, "B": 345, "P": 165, "Q": 60}, segs=("AB", "AP", "BP", "AQ", "BQ"),
      angs=(("P", "A", "B", ""), ("Q", "A", "B", "", 2)), letters={"A": "A", "B": "B", "P": "P", "Q": "Q"},
      shade=segshade(345, 240), w=140, h=124, r=50)


def amsi_triangles():
    # p13 altitudes: acute and obtuse triangles
    f = CF(360, 90)
    A, B, C = (10, 82), (190, 82), (82, 10)
    f.poly([A, B, C], color=None, opacity=0).seg(C, (82, 82), dash="4 3", width=1.2).right((82, 82), B, C, s=6)
    A, B, C = (290, 82), (350, 82), (264, 10)
    f.poly([A, B, C], color=None, opacity=0).seg(C, (264, 82), dash="4 3", width=1.2).seg((264, 82), A, dash="4 3", width=1.2).right((264, 82), A, C, s=6)
    save("c2_alt", f)
    # p13 orthocentre theorem
    f = CF(180, 110)
    A, B, C = (10, 100), (170, 100), (86, 12)
    f.poly([A, B, C], color=None, opacity=0)
    for v, p, q in ((C, A, B), (A, B, C), (B, C, A)):
        Fo = foot(v, p, q)
        f.seg(v, Fo, dash="4 3", width=1.2).right(Fo, q, v, s=5)
    f.lab(A, "A", dx=-8, dy=4).lab(B, "B", dx=8, dy=4).lab(C, "C", dy=-8)
    save("c2_ortho", f)
    # Exercise 7: altitudes AP, BQ meet at H; CH produced meets AB at R; circles on HC and AB
    A, B, C = (88, 12), (40, 132), (230, 132)
    P_ = foot(A, B, C)
    Q_ = foot(B, A, C)
    # H = intersection of AP and BQ
    def inter(p1, p2, p3, p4):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    H = inter(A, P_, B, Q_)
    R_ = inter(C, H, A, B)
    f = CF(250, 170)
    m1 = ((H[0] + C[0]) / 2, (H[1] + C[1]) / 2)
    m2 = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    f.circle(m1, hypot(H[0] - C[0], H[1] - C[1]) / 2).circle(m2, hypot(A[0] - B[0], A[1] - B[1]) / 2)
    f.poly([A, B, C], color=None, opacity=0).seg(A, P_).seg(B, Q_).seg(C, R_, dash="4 3", width=1.2)
    f.right(P_, C, A, s=5).right(Q_, A, B, s=5)
    for p, t, dx, dy in ((A, "A", 0, -8), (B, "B", -8, 6), (C, "C", 8, 6), (P_, "P", 2, 12), (Q_, "Q", 9, -4), (H, "H", 9, -2), (R_, "R", -9, -2)):
        f.pdot(p, 1.8).lab(p, t, dx=dx, dy=dy, size=11)
    save("c2_ex7", f)


def amsi_cyclic():
    # p14 circumcircle with perpendicular bisectors; a cyclic quadrilateral; construction of the circumcentre
    def perp_bis(f, p, q, c, n, ext_=16):
        m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        f.seg(ext(c, m, -0.3) if False else c, ext(c, m, 1 + ext_ / max(hypot(m[0] - c[0], m[1] - c[1]), 1)), dash="3 3", width=1.0)
        f.tick(p, m, n=n).tick(m, q, n=n)
    F("c2_circum", {"A": 240, "B": 300, "C": 90 + 0, "O": "O"}, segs=("AB", "BC", "CA"), dot_o=False,
      extra=lambda f, P, c, r: [perp_bis(f, P[a], P[b], c, n) for a, b, n in (("A", "B", 2), ("B", "C", 3), ("C", "A", 1))], w=130, h=124, r=50)
    F("c2_cquad", {"A": 165, "B": 75, "C": 345, "D": 240}, segs=("AB", "BC", "CD", "DA"), dots=False, w=130, h=124, r=50)
    F("c2_constr", {"A": 115, "B": 50, "C": 330, "D": 220, "O": "O"}, segs=("AB", "BC", "CD", "DA"), dots=False,
      extra=lambda f, P, c, r: ([perp_bis(f, P[a], P[b], c, n) for a, b, n in (("A", "D", 2), ("D", "C", 2))], f.text(c[0] + 9, c[1] + 2, "O", size=11)), w=130, h=124, r=50)
    # p15 opposite angles proof
    F("c2_opp", {"A": 190, "B": 80, "C": 10, "D": 300, "O": "O"}, segs=("AB", "BC", "CD", "DA"), dashed=("OB", "OD"),
      angs=(("O", "B", "D", "α", 1, False, 16, 8), ("O", "B", "D", "γ", 1, True, 16, 8)), letters={k: k for k in "ABCD"}, extra=lab_o("O", 0, 13))
    # Exercise 8: diagonals; alpha, beta at A, gamma, delta at C
    F("c2_ex8", {"A": 190, "B": 85, "C": 350, "D": 270}, segs=("AB", "BC", "CD", "DA", "BD"), dashed=("AC",),
      angs=(("A", "C", "D", "α", 1, False, 17), ("A", "B", "C", "β", 1, False, 22), ("C", "D", "A", "γ", 1, False, 17), ("C", "A", "B", "δ", 1, False, 22)),
      letters={k: k for k in "ABCD"})
    # exterior angle
    def extp(f, P, c, r):
        Pp = ext(P["B"], P["C"], 1.8)
        f.seg(P["C"], Pp, dash="4 3", width=1.2).angle(P["C"], Pp, P["D"], r=11).alab(P["C"], Pp, P["D"], "α", d=20, size=11, italic=True)
        f.lab(Pp, "P", dx=8, dy=2)
    F("c2_ext", {"A": 200, "B": 110, "C": 40, "D": 300}, segs=("AB", "BC", "CD", "DA"), angs=(("A", "B", "D", "α", 1, False, 20),),
      letters={k: k for k in "ABCD"}, extra=extp, w=190)
    # Exercise 9: two circles meet at B and Q; A, B, C, X and P, Q, R, X are straight lines
    def second(p, q, cen, rad):
        ux, uy = q[0] - p[0], q[1] - p[1]
        Lq = hypot(ux, uy); ux, uy = ux / Lq, uy / Lq
        px, py = p[0] - cen[0], p[1] - cen[1]
        b = px * ux + py * uy
        t = -b + sqrt(b * b - (px * px + py * py - rad * rad))
        return (p[0] + t * ux, p[1] + t * uy)
    f = CF(230, 120)
    c1, r1 = (70, 60), 52
    yl = c1[1] + 34                                # the line PQRX is horizontal, as in the source
    hw = sqrt(r1 * r1 - 34 * 34)
    P_, Q = (c1[0] - hw, yl), (c1[0] + hw, yl)
    X = (220, yl)
    A = CF.on(c1, r1, 103)
    B = second(A, X, c1, r1)
    mx, my = (B[0] + Q[0]) / 2, (B[1] + Q[1]) / 2
    dx, dy = Q[0] - B[0], Q[1] - B[1]
    L = hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    if nx < 0:
        nx, ny = -nx, -ny
    c2 = (mx + 10 * nx, my + 10 * ny)
    r2 = hypot(c2[0] - B[0], c2[1] - B[1])
    Cp = second(B, X, c2, r2)
    Rp = second(Q, X, c2, r2)
    f.circle(c1, r1).circle(c2, r2).seg(A, X).seg(P_, X).seg(A, P_, dash="4 3", width=1.2).seg(B, Q, dash="4 3", width=1.2)
    f.pdot(c1, 1.6).angle(A, B, P_, r=10).alab(A, B, P_, "α", d=18, size=11, italic=True)
    for p, t, ddx, ddy in ((A, "A", 0, -8), (B, "B", 2, -10), (Cp, "C", 4, -9), (P_, "P", -8, 8), (Q, "Q", -3, 12), (Rp, "R", 2, 12), (X, "X", 9, 2)):
        f.lab(p, t, dx=ddx, dy=ddy, size=11)
    save("c2_ex9", f)
    # Exercise 10: cyclic trapezium ABCD with AB || DC, BC produced to P, AD and BC produced meet at M
    def trap(f, P, c, r):
        M = None
        A_, B_, C_, D_ = P["A"], P["B"], P["C"], P["D"]
        def inter(p1, p2, p3, p4):
            x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        M = inter(A_, D_, B_, C_)
        f.seg(C_, M, dash="4 3", width=1.2).seg(D_, M, dash="4 3", width=1.2)
        Pp = ext(C_, M, 0.45)
        f.pdot(Pp, 2).lab(Pp, "P", dx=8, dy=-2).lab(M, "M", dx=6, dy=9)
        f.parr(A_, B_, t=0.55).parr(D_, C_, t=0.55)
    F("c2_ex10", {"A": 195, "B": 95, "C": 345, "D": 305}, segs=("AB", "BC", "CD", "DA"), letters={k: k for k in "ABCD"}, extra=trap, w=200, h=150, r=52, c=(70, 66))
    # converse proof: ABCD with C outside the circle through A, B, D; X on DC
    f = CF(220, 130)
    c, r = (80, 70), 54
    A, D, B = CF.on(c, r, 205), CF.on(c, r, 140), CF.on(c, r, 330)
    X = CF.on(c, r, 60)
    Cq = ext(D, X, 1.85)
    f.circle(c, r).pdot(c, 1.6).seg(A, B).seg(B, Cq).seg(D, Cq).seg(A, D, dash="4 3", width=1.2).seg(X, B, dash="4 3", width=1.2)
    for p, t in ((A, "A"), (B, "B"), (D, "D"), (X, "X")):
        f.out(p, c, t)
    f.lab(Cq, "C", dx=6, dy=-6)
    save("c2_conv", f)
    # Exercise 12: trapezium with equal adjacent acute angles (the source labels the right vertex A again: here B)
    f = CF(170, 90)
    A, B, C, D = (14, 76), (156, 76), (126, 14), (44, 14)
    f.poly([A, B, C, D], color=None, opacity=0).angle(A, B, D, r=11).angle(B, C, A, r=11)
    f.alab(A, B, D, "α", d=24, size=11, italic=True).alab(B, C, A, "α", d=24, size=11, italic=True)
    f.lab(A, "A", dx=-8, dy=6).lab(B, "B", dx=8, dy=6).lab(C, "C", dx=8, dy=-4).lab(D, "D", dx=-8, dy=-4)
    save("c2_ex12", f)


def amsi_sine():
    f = CF(130, 100)
    A, B, C = (66, 10), (12, 88), (118, 88)
    f.poly([A, B, C], color=None, opacity=0)
    f.lab(A, "A", dy=-8).lab(B, "B", dx=-8, dy=4).lab(C, "C", dx=8, dy=4)
    f.text(65, 98, "a", size=11, italic=True).text(28, 46, "c", size=11, italic=True).text(102, 46, "b", size=11, italic=True)
    save("c2_sine_t", f)
    F("c2_sine_c", {"A": 105, "B": 215, "C": 325, "P": 35, "O": "O"}, segs=("AB", "BC", "CA"), dashed=("BP",),
      letters={"A": "A", "B": "B", "C": "C"}, extra=lab_o("O", -2, -9), w=130, h=124, r=50)
    F("c2_sine1", {"A": 110, "B": 210, "C": 330, "P": 30, "O": "O"}, segs=("AB", "BC", "CA"), dashed=("BP", "PC"),
      angs=(("A", "B", "C", "α", 1, False, 18),), letters={"A": "A", "B": "B", "C": "C", "P": "P"}, extra=lab_o("O", -2, -9), w=130, h=124, r=50)
    F("c2_sine2", {"A": 110, "B": 215, "C": 50, "P": 35, "O": "O"}, segs=("AB", "BC", "CA"), dashed=("BP", "PC"),
      angs=(("A", "B", "C", "α", 1, False, 18),), letters={"A": "A", "B": "B", "C": "C", "P": "P"}, extra=lab_o("O", 0, 12), w=130, h=124, r=50)
    F("c2_sine3", {"A": 110, "B": 205, "C": 25, "O": "O"}, segs=("AB", "BC", "CA"),
      angs=(("A", "B", "C", "α", 1, False, 18),), letters={"A": "A", "B": "B", "C": "C"}, extra=lab_o("O", 0, 12), w=130, h=124, r=50)


# ---------------------------------------------------------------- Maths Pathway boxes and questions
def mp():
    W, H, R = 130, 118, 48
    kw = dict(w=W, h=H, r=R)
    # box: arc AB; angle at the centre; angle at C
    def bluearc(f, P, c, r):
        pa, pb = CF.on(c, r, 235), CF.on(c, r, 305)
        f.raw(f'<path d="M{pa[0]:.1f},{pa[1]:.1f} A{r},{r} 0 0 0 {pb[0]:.1f},{pb[1]:.1f}" fill="none" stroke="#2563eb" stroke-width="3"/>')
    F("c2_mpbox1", {"A": 235, "B": 305, "O": "O"}, letters={"A": "A", "B": "B"}, extra=bluearc, litalic=False, **kw)
    F("c2_mpbox2", {"A": 235, "B": 305, "O": "O"}, segs=("OA", "OB"), angs=(("O", "A", "B", ""),), letters={"A": "A", "B": "B"}, extra=bluearc, litalic=False, **kw)
    F("c2_mpbox3", {"A": 245, "B": 295, "C": 90, "O": "O"}, segs=("CA", "CB"), angs=(("C", "A", "B", ""),), letters={"A": "A", "B": "B", "C": "C"}, extra=bluearc, litalic=False, **kw)
    F("c2_mpbox4", {"A": 230, "B": 310, "C": 90, "O": "O"}, segs=("CA", "CB", "OA", "OB"), angs=(("C", "A", "B", "a", 1, False, 24), ("O", "A", "B", "2a", 2, False, 22)), **kw)
    F("c2_mpbox5", {"A": 120, "B": 60, "C": 215, "D": 325}, segs=("AD", "BC", "AC", "BD"), angs=(("A", "C", "D", "a°", 1, False, 36), ("B", "C", "D", "a°", 1, False, 36)), w=160, h=146, r=62)
    F("c2_mpbox6", {"A": 100, "B": 20, "C": 275, "D": 185}, segs=("AB", "BC", "CD", "DA"), angs=(("A", "D", "B", "x", 1, False, 24), ("C", "B", "D", "y", 2, False, 24)), **kw)

    # Q1 a-i: are the two marked angles subtended by the same arc?
    F("c2q1a", {"T": 100, "L": 260, "R": 330, "O": "O"}, segs=("TL", "TR", "OL", "OR"), angs=(("T", "L", "R", ""), ("O", "L", "R", "", 2, False, 0, 9)), **kw)
    F("c2q1b", {"a": 5, "b": 330, "c": 220, "d": 275, "O": "O"}, segs=("Oa", "Ob", "Oc", "Od"), angs=(("O", "c", "d", "", 1, False, 0, 10), ("O", "b", "a", "", 1, False, 0, 13)), **kw)
    F("c2q1c", {"P": 125, "Q": 55, "L": 250, "R": 290}, segs=("PL", "PR", "QL", "QR"), angs=(("P", "L", "R", "", 1, False, 0, 14), ("Q", "L", "R", "", 2, False, 0, 14)), **kw)
    F("c2q1d", {"L": 200, "R": 330, "B": 280, "O": "O"}, segs=("OL", "OR", "LB", "BR"), angs=(("O", "L", "R", "", 1, True, 0, 11), ("B", "L", "R", "", 2, False, 0, 11)), **kw)
    F("c2q1e", {"L": 200, "R": 330, "B": 280, "O": "O"}, segs=("OL", "OR", "LB", "BR"), angs=(("O", "L", "R", "", 1, False, 0, 9), ("B", "L", "R", "", 2, False, 0, 11)), **kw)
    F("c2q1f", {"L": 180, "R": 0, "T": 115, "O": "O"}, segs=("LR", "TL", "TR"), angs=(("T", "L", "R", "", 2, False, 0, 11),), extra=lambda f, P, c, r: below(f, c, 10), **kw)
    F("c2q1g", {"T": 115, "L": 220, "B": 270, "R": 330, "O": "O"}, segs=("TL", "TR", "LB", "BR"), angs=(("T", "L", "R", "", 2, False, 0, 11), ("B", "L", "R", "", 1, False, 0, 10)), **kw)
    F("c2q1h", {"L": 235, "M": 300, "R": 10, "O": "O"}, segs=("OL", "OM", "LR", "RM"), angs=(("O", "L", "M", "", 1, False, 0, 9), ("R", "L", "M", "", 2, False, 0, 12)), **kw)
    F("c2q1i", {"P": 120, "Q": 70, "L": 165, "R": 345, "O": "O"}, segs=("PL", "PR", "QL", "QR"), angs=(("P", "L", "R", "", 2, False, 0, 11), ("Q", "L", "R", "", 1, False, 0, 11)), **kw)

    # Q2: prove angle BOC = 2 angle BAC
    F("c2q2", {"A": 90, "B": 225, "C": 330, "O": "O"}, segs=("AB", "AC", "AO", "OB", "OC"),
      angs=(("A", "B", "O", "x", 1, False, 26, 14), ("A", "O", "C", "y", 1, False, 26, 14)), letters={"A": "A", "B": "B", "C": "C"}, litalic=False,
      extra=lab_o("O", 0, 14, False), **kw)

    # Q3 a-f and demo / your turn versions
    def q3a(nm, t30, tx):
        F(nm, {"T": 105, "L": 255, "R": 325, "O": "O"}, segs=("TL", "TR", "OL", "OR"),
          angs=(("T", "L", "R", t30, 2, False, 30, 12), ("O", "L", "R", tx, 1, False, 20, 10)), **kw)
    q3a("c2q3a", "30°", "x")
    q3a("c2d1a", "35°", "x")
    q3a("c2y1a", "32°", "x")
    def q3b(nm, t, ty):
        F(nm, {"T": 108, "L": 210, "R": 330, "O": "O"}, segs=("OT", "OL", "TR", "LR"),
          angs=(("O", "T", "L", t, 1, False, 26, 12), ("R", "T", "L", ty, 2, False, 26, 12)), **kw)
    q3b("c2q3b", "102°", "y")
    q3b("c2d1b", "116°", "y")
    q3b("c2y1b", "96°", "y")
    F("c2q3c", {"L": 160, "T": 80, "R": 0, "O": "O"}, segs=("LT", "LR", "OT", "OR"),
      angs=(("L", "T", "R", "40°", 2, False, 30, 12), ("O", "T", "R", "z", 1, False, 20, 10)), **kw)
    F("c2q3d", {"T": 48, "R": 0, "B": 250, "O": "O"}, segs=("OT", "OR", "TB", "BR"),
      angs=(("O", "T", "R", "48°", 1, False, 24, 9), ("B", "T", "R", "x", 2, False, 28, 12)), **kw)
    F("c2q3e", {"P": 160, "Q": 205, "T": 55, "B": 295, "O": "O"}, segs=("PT", "PB", "QT", "QB", "OT", "OB"),
      angs=(("P", "T", "B", "60°", 3, False, 30, 10), ("Q", "T", "B", "y", 2, False, 28, 10), ("O", "T", "B", "x", 1, False, 18, 9)), w=160, h=146, r=62)
    F("c2q3f", {"Z": 115, "L": 160, "T": 50, "R": 0, "O": "O"}, segs=("LT", "LR", "ZR", "ZT", "OT", "OR"),
      angs=(("L", "T", "R", "25°", 2, False, 32, 12), ("Z", "T", "R", "z", 1, False, 20, 9), ("O", "T", "R", "x", 3, False, 20, 8)), **kw)
    # reflex versions (MP Q5(a) style) for the demo and your turn
    def q5a(nm, t, tx):
        F(nm, {"T": 120, "L": 195, "R": 30, "O": "O"}, segs=("TL", "TR", "OL", "OR"),
          angs=(("T", "L", "R", t, 2, False, 26, 10), ("O", "L", "R", tx, 1, True, 20, 11)), **kw)
    q5a("c2q5a", "160°", "x")
    q5a("c2d1c", "150°", "x")
    q5a("c2y1c", "145°", "x")
    F("c2q5b", {"T": 80, "M": 40, "R": 0, "O": "O"}, segs=("OT", "OR", "TM", "MR"),
      angs=(("O", "T", "R", "280°", 1, True, 24, 12), ("M", "T", "R", "y", 2, False, 18, 9)), **kw)
    F("c2q5c", {"L": 110, "R": 50, "O": "O"}, segs=("OL", "OR"),
      angs=(("O", "L", "R", "60°", 1, False, 26, 9), ("O", "L", "R", "z", 2, True, 22, 12)), **kw)
    F("c2q5d", {"L": 250, "R": 335, "O": "O"}, segs=("OL", "OR"),
      angs=(("O", "L", "R", "270°", 1, True, 24, 11), ("O", "L", "R", "a°", 2, False, 22, 9)), **kw)
    F("c2q5e", {"T": 85, "L": 185, "B": 310, "O": "O"}, segs=("OT", "OL", "LB", "TB"),
      angs=(("O", "T", "L", "100°", 2, False, 26, 9), ("O", "T", "L", "q", 1, True, 18, 14), ("B", "T", "L", "p", 1, False, 26, 12)), **kw)
    F("c2q5f", {"L": 160, "T": 90, "R": 20, "O": "O"}, segs=("OL", "OR", "LT", "TR"),
      angs=(("O", "L", "R", "120°", 1, False, 17, 7), ("O", "L", "R", "x", 1, True, 20, 13), ("T", "L", "R", "y", 2, False, 15, 9)), extra=lambda f, P, c, r: None, w=160, h=146, r=62)
    F("c2q5g", {"L": 150, "T": 60, "R": 0, "B": 240, "O": "O"}, segs=("LT", "TR", "LB", "BR", "OL", "OR"),
      angs=(("B", "L", "R", "75°", 2, False, 30, 11), ("O", "L", "R", "a", 1, False, 18, 8), ("O", "L", "R", "b", 2, True, 16, 11), ("T", "L", "R", "c", 1, False, 18, 9)), w=160, h=146, r=62)
    F("c2q5h", {"T": 80, "M": 40, "R": 0, "B": 225, "O": "O"}, segs=("OT", "OR", "TM", "MR", "BT", "BR"),
      angs=(("O", "T", "R", "80°", 1, False, 18, 8), ("O", "T", "R", "x", 1, True, 18, 12), ("M", "T", "R", "y", 2, False, 15, 8), ("B", "T", "R", "z", 2, False, 26, 12)), w=160, h=146, r=62)
    F("c2q5i", {"T": 120, "U": 30, "V": 320, "B": 270, "O": "O"}, segs=("TB", "TU", "UV", "VB", "OU", "OB"),
      angs=(("V", "U", "B", "130°", 2, False, 28, 9), ("O", "U", "B", "g", 1, False, 18, 9), ("O", "U", "B", "f", 1, True, 18, 12), ("T", "U", "B", "h", 2, False, 22, 11)), w=160, h=146, r=62)

    # Q4 a-c (angles on the same arc) and versions
    def q4a(nm, t, tx):
        F(nm, {"L": 160, "T": 119, "R": 5, "B": 290, "O": "O"}, segs=("LT", "LR", "TB", "BR"),
          angs=(("L", "T", "R", tx, 1, False, 24, 12), ("B", "T", "R", t, 2, False, 26, 11)), **kw)
    q4a("c2q4a", "57°", "x")
    q4a("c2d2a", "62°", "x")
    q4a("c2y2a", "53°", "x")
    def q4b(nm, t, ty):
        F(nm, {"L": 180, "T": 72, "R": 0, "B": 265, "O": "O"}, segs=("LR", "LT", "TB", "BR"),
          angs=(("L", "T", "R", t, 1, False, 30, 14), ("B", "T", "R", ty, 2, False, 26, 12)), **kw)
    q4b("c2q4b", "36°", "y")
    q4b("c2d2b", "41°", "y")
    q4b("c2y2b", "28°", "y")
    F("c2q4c", {"P": 150, "Q": 205, "T": 50, "B": 263}, segs=("PQ", "PB", "QT", "TB"),
      angs=(("P", "Q", "B", "z", 1, False, 22, 12), ("T", "Q", "B", "29°", 1, False, 26, 12)), **kw)

    # Q6 a-c (cyclic quadrilaterals) and versions
    def q6a(nm, t, tx):
        F(nm, {"B": 125, "R": 10, "D": 235, "L": 190}, segs=("BR", "RD", "DL", "LB"),
          angs=(("R", "B", "D", t, 1, False, 28, 12), ("L", "B", "D", tx, 2, False, 22, 11)), **kw)
    q6a("c2q6a", "55°", "x")
    q6a("c2d3a", "64°", "x")
    q6a("c2y3a", "48°", "x")
    def q6b(nm, t, ta):
        F(nm, {"T": 85, "U": 30, "R": 355, "B": 265}, segs=("TB", "TU", "UR", "RB"),
          angs=(("U", "T", "R", t, 2, False, 30, 9), ("B", "T", "R", ta, 1, False, 30, 14)), **kw)
    q6b("c2q6b", "140°", "a")
    q6b("c2d3b", "128°", "a")
    q6b("c2y3b", "135°", "a")
    F("c2q6c", {"L": 160, "T": 70, "R": 300, "B": 250}, segs=("LT", "TR", "RB", "BL"),
      angs=(("R", "T", "B", "y", 1, False, 22, 12),), extra=lambda f, P, c, r: f.right(P["L"], P["T"], P["B"], s=7), **kw)
    # exterior angle demo / your turn (our own, drawn like AMSI page 15)
    def extv(nm, t, var):
        def e(f, P, c, r):
            Pp = ext(P["B"], P["C"], 1.8)
            f.seg(P["C"], Pp, dash="4 3", width=1.2).angle(P["C"], Pp, P["D"], r=11).alab(P["C"], Pp, P["D"], t, d=24, size=11)
            f.lab(Pp, "P", dx=8, dy=2)
        F(nm, {"A": 200, "B": 110, "C": 40, "D": 300}, segs=("AB", "BC", "CD", "DA"), angs=(("A", "B", "D", var, 1, False, 20),),
          letters={k: k for k in "ABCD"}, extra=e, w=190)
    extv("c2d3c", "71°", "x")
    extv("c2y3c", "83°", "x")

    # Q8 b-d
    F("c2q8b", {"K": 115, "T": 75, "L": 210, "R": 272}, segs=("KL", "KR", "TL", "TR"),
      angs=(("K", "L", "R", "k", 1, False, 24, 12), ("T", "L", "R", "31°", 1, False, 34, 12)), **kw)
    F("c2q8c", {"A": 115, "B": 40, "C": 331, "D": 235}, segs=("AB", "BC", "CD", "DA"),
      angs=(("B", "A", "C", "108°", 2, False, 28, 9), ("D", "A", "C", "m", 1, False, 22, 12)), **kw)
    F("c2q8d", {"T": 95, "L": 210, "R": 354, "O": "O"}, segs=("TL", "TR", "OL", "OR"),
      angs=(("T", "L", "R", "72°", 2, False, 24, 9), ("O", "L", "R", "z", 2, False, 20, 9)), **kw)


# ---------------------------------------------------------------- past papers
def pastpapers():
    # SBHS 2021 Part B (p): A, B, C, D concyclic, CDE straight, 76 deg exterior angle at D
    def ppe(f, P, c, r):
        E = ext(P["C"], P["D"], 1.55)
        f.seg(P["D"], E).angle(P["D"], P["A"], E, r=12).alab(P["D"], P["A"], E, "76°", d=22, size=10.5)
        f.lab(E, "E", dx=6, dy=-6)
    F("c2pp1", {"A": 62, "B": 165, "C": 265, "D": 15}, segs=("AB", "BC", "CD", "DA"), letters={k: k for k in "ABCD"}, extra=ppe,
      w=200, h=150, r=62, c=(84, 76), dots=True)
    # SBHS 2023 Part C Q4: A, B, C, D on a circle centre O; AOC a diameter; angle BAC = 55
    F("c2pp2", {"A": 180, "B": 110, "C": 0, "D": 297, "O": "O"}, segs=("AC", "AB", "BC", "BD", "AD"),
      angs=(("A", "B", "C", "55°", 1, False, 30, 16),), letters={k: k for k in "ABCD"}, extra=lab_o("O", 0, 13),
      w=200, h=180, r=78, dots=False)
    # Girraween 2020 Q25(b): chords CA and BD meet; 46 at C, 55 at A, m at the intersection
    def gb(f, P, c, r):
        A_, B_, C_, D_ = P["A"], P["B"], P["C"], P["D"]
        def inter(p1, p2, p3, p4):
            x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        X = inter(A_, C_, B_, D_)
        f.angle(X, B_, A_, r=10).alab(X, B_, A_, "m°", d=20, size=10.5, italic=True)
        f.pdot(c, 2)
    F("c2pp3", {"A": 330, "B": 30, "C": 125, "D": 220}, segs=("CA", "BD", "CB", "DA"),
      angs=(("C", "B", "A", "46°", 1, False, 30, 13), ("A", "D", "C", "55°", 1, False, 30, 13)), letters={k: k for k in "ABCD"}, extra=gb,
      w=170, h=140, r=58, litalic=False)
    # Girraween 2020 Q25(c): AOB a diameter, D and C on the circle, angle ADO = 40, x at C
    F("c2pp4", {"A": 145, "B": 325, "D": 245, "C": 288, "O": "O"}, segs=("AB", "AD", "DC", "CB", "DO"),
      angs=(("D", "A", "O", "40°", 1, False, 26, 12), ("C", "D", "B", "x°", 1, False, 18, 9)), letters={k: k for k in "ABCD"}, extra=lab_o("O", 4, -9),
      w=170, h=150, r=62)
    # SBHS 2024 Part E Q2: ABCDE on a circle, AB || ED, AD and BE meet at F; x at A, y at F, theta at C
    def sb24(f, P, c, r):
        A_, B_, D_, E_ = P["A"], P["B"], P["D"], P["E"]
        def inter(p1, p2, p3, p4):
            x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        Fp = inter(A_, D_, B_, E_)
        f.angle(Fp, E_, D_, r=9).alab(Fp, E_, D_, "y", d=16, size=10.5, italic=True)
        f.pdot(Fp, 1.8).lab(Fp, "F", dx=0, dy=-9, size=10.5)
    F("c2pp5", {"A": 160, "B": 20, "C": 335, "D": 290, "E": 230}, segs=("AB", "AD", "BE", "ED", "BC", "CD"),
      angs=(("A", "B", "D", "x", 1, False, 24, 12), ("C", "B", "D", "θ", 1, False, 18, 10)), letters={k: k for k in "ABCDE"}, extra=sb24,
      w=180, h=150, r=64, litalic=False, lsize=10.5)


def napoleon():
    # SBHS 2021 Part G (e): scalene ABC, equilateral triangles ABX, BCY, ACZ outward; circles C1 (ABX, centre P), C2 (BCY, centre Q)
    from math import sqrt as s3
    A, B, C = (100.0, 150.0), (180.0, 60.0), (190.0, 200.0)
    def eq_out(p, q, away):
        # third vertex of the equilateral triangle on pq, on the side away from the point 'away'
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        dx, dy = q[0] - p[0], q[1] - p[1]
        h = s3(3) / 2
        c1 = (mx - h * dy, my + h * dx)
        c2 = (mx + h * dy, my - h * dx)
        return c1 if hypot(c1[0] - away[0], c1[1] - away[1]) > hypot(c2[0] - away[0], c2[1] - away[1]) else c2
    X = eq_out(A, B, C)
    Y = eq_out(B, C, A)
    Z = eq_out(A, C, B)
    P = ((A[0] + B[0] + X[0]) / 3, (A[1] + B[1] + X[1]) / 3)
    Q = ((B[0] + C[0] + Y[0]) / 3, (B[1] + C[1] + Y[1]) / 3)
    R = ((A[0] + C[0] + Z[0]) / 3, (A[1] + C[1] + Z[1]) / 3)
    rP, rQ = hypot(P[0] - A[0], P[1] - A[1]), hypot(Q[0] - B[0], Q[1] - B[1])
    # O: the second intersection of the two circles (reflection of B in line PQ)
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    t = ((B[0] - P[0]) * dx + (B[1] - P[1]) * dy) / (dx * dx + dy * dy)
    Fp = (P[0] + t * dx, P[1] + t * dy)
    O = (2 * Fp[0] - B[0], 2 * Fp[1] - B[1])
    for nm, showR in (("c2nap1", False), ("c2nap2", True)):
        x0 = min(X[0], Z[0], P[0] - rP, Q[0] - rQ) - 22
        y0 = min(X[1], P[1] - rP, Q[1] - rQ) - 8
        x1 = max(Y[0], Q[0] + rQ) + 16
        y1 = max(Z[1], Q[1] + rQ, P[1] + rP) + 14
        f = CF(int(x1 - x0), int(y1 - y0))
        sh = (-x0, -y0)
        T = lambda p: (p[0] + sh[0], p[1] + sh[1])  # noqa: E731
        f.circle(T(P), rP).circle(T(Q), rQ)
        for p, q in ((A, B), (B, C), (C, A), (A, X), (B, X), (B, Y), (C, Y), (A, Z), (C, Z)):
            f.seg(T(p), T(q), width=1.3)
        f.pdot(T(P), 2).pdot(T(Q), 2).pdot(T(O), 2)
        for p, s, ddx, ddy in ((A, "A", -9, 6), (B, "B", 4, -9), (C, "C", 2, 13), (X, "X", -10, 0), (Y, "Y", 10, 0), (Z, "Z", -9, 6),
                               (P, "P", -9, 0), (Q, "Q", 9, 0), (O, "O", 8, 10)):
            f.lab(T(p), s, dx=ddx, dy=ddy, size=11.5)
        f.text(T(P)[0] - rP - 4, T(P)[1] + 32, "C₁", size=11, italic=True)
        f.text(T(Q)[0] + rQ * 0.55, T(Q)[1] + rQ * 0.95, "C₂", size=11, italic=True)
        if showR:
            f.pdot(T(R), 2).lab(T(R), "R", dx=-9, dy=0, size=11.5)
        save(nm, f)
    return A, B, C


if __name__ == "__main__":
    amsi()
    amsi_triangles()
    amsi_cyclic()
    amsi_sine()
    mp()
    pastpapers()
    napoleon()
