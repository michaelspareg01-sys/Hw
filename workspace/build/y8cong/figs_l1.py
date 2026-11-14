"""Figures for Lesson 1 (8D Congruent figures). Run after figs.py: python3 figs_l1.py

Book figures are redrawn from the vector coordinates of workspace/sources/y8/chapter 8.pdf (PDF pages
22-26, points, y down). Where the book means two figures to be congruent but draws them a little
unequal (Exercise 8D Q3 and Q9d, the Key ideas triangles), the second figure is the exact isometric
image of the first, fitted to the book's position (fit_iso), so every 'congruent' pair is truly congruent.
"""
from figs import (falab, CF, Fig, save, save_flat, cat, book, fit_iso, grid, axes, mtext, centroid, ftext, polar,
                  _ang, ACC, GRIDC)
from math import hypot


def labels(f, pts, names, c=None, d=10, size=12):
    c = c or centroid(pts)
    for p, s in zip(pts, names):
        f.out(p, c, s, d=d, size=size)


def shape(f, pts, names=None, d=10, fill=None, stroke="ink", width=1.6, size=12):
    f.poly(pts, color=fill, opacity=0.14 if fill else 0, stroke=stroke, width=width)
    if names:
        labels(f, pts, names, d=d, size=size)


def iso_image(src, dst_book):
    """Exact isometric image of src, fitted to the book's (slightly unequal) points dst_book."""
    F, err, refl = fit_iso(src, dst_book)
    return [F(p) for p in src]


# ---------------- Concept 1 ----------------

def fig_start():
    T = book(1.5, 73.1, 244.1)
    f = CF(180, 94)
    q1 = [T(p) for p in ((118.1, 244.1), (73.1, 263.1), (73.1, 287.1), (108.1, 287.1))]
    q2 = [T(p) for p in ((132.7, 287.1), (177.7, 268.1), (177.7, 244.1), (142.7, 244.1))]
    shape(f, q1, stroke="blue")
    shape(f, q2, stroke="blue")
    save("l1_start", f)


def fig_four():
    T = book(1.5, 85.5, 439.9)
    f = CF(380, 90)
    for q in (((125.2, 479.6), (108.5, 457.9), (85.5, 457.9), (85.5, 479.6)),
              ((157.9, 479.6), (174.5, 457.9), (197.5, 457.9), (197.5, 479.6)),
              ((230.4, 439.9), (252.0, 456.6), (252.0, 479.6), (230.4, 479.6)),
              ((323.0, 479.6), (306.4, 457.9), (283.4, 457.9), (283.4, 479.6))):
        shape(f, [T(p) for p in q], stroke="blue")
    save("l1_four", f)


def marks_tri(f, P, kinds, r=10):
    """Angle marks at the vertices P[i]: 'R' right angle, 'dot' filled dot, 'o' open circle."""
    n = len(P)
    for i, k in enumerate(kinds):
        v, a, b = P[i], P[i - 1], P[(i + 1) % n]
        c = centroid(P)
        ux, uy = c[0] - v[0], c[1] - v[1]
        L = hypot(ux, uy)
        if k == "R":
            f.right(v, a, b, s=7)
        elif k == "dot":
            f.dot(v[0] + r * ux / L, v[1] + r * uy / L, r=2.0)
        elif k == "o":
            f.raw(f'<circle cx="{v[0] + r * ux / L:.1f}" cy="{v[1] + r * uy / L:.1f}" r="2.2" fill="#fff" stroke="{ACC["ink"]}" stroke-width="0.9"/>')


def fig_keytri():
    T = book(1.6, 329.0, 512.0)
    A, B, C = T((338.0, 578.2)), T((366.3, 589.4)), T((357.5, 529.2))
    F, D, E = iso_image([A, B, C], [T((447.3, 546.1)), T((459.7, 519.9)), T((394.0, 520.8))])
    f = CF(240, 140)
    shape(f, [A, B, C], ["A", "B", "C"], stroke="blue")
    shape(f, [F, D, E], ["F", "D", "E"], stroke="blue")
    marks_tri(f, [A, B, C], ["R", "dot", "o"], r=12)
    marks_tri(f, [F, D, E], ["R", "dot", "o"], r=12)
    save("l1_keytri", f)


def grid_shapes(name, shapes, W=16, H=8, u=16):
    """Shapes on a square grid (no axes). shapes: (name, grid points, fill). Labels sit inside the shapes."""
    f = CF(W * u + 8, H * u + 8)
    G = lambda p: (4 + p[0] * u, 4 + (H - p[1]) * u)
    grid(f, G, range(0, W + 1), range(0, H + 1))
    for nm, pts, fill in shapes:
        P = [G(p) for p in pts]
        f.poly(P, color=fill, opacity=0.22, stroke="ink", width=1.5)
    for nm, pts, fill in shapes:
        P = [G(p) for p in pts]
        c = centroid(P)
        mtext(f, c[0], c[1], nm, size=12, italic=False)
    save(name, f)


def fig_demo1():
    P = [(1, 1), (4, 1), (4, 2), (2, 3), (1, 3)]
    A = [(11 - x, y) for x, y in P]                       # reflection in the line x = 5.5
    B = [(x + 11, y + 4) for x, y in P]                   # translation 11 right, 4 up
    C = [(-y + 9, x + 3) for x, y in P]                   # rotation 90 degrees anticlockwise (about (3, 6))
    D = [(1, 5), (5, 5), (5, 6), (2, 7), (1, 7)]          # stretched: bottom side 4 units, not 3
    grid_shapes("l1_d1", [("P", P, "blue"), ("A", A, None), ("B", B, None), ("C", C, None), ("D", D, None)])
    Q = [(1, 1), (3, 1), (4, 2), (2, 3), (1, 2)]
    A = [(15 - x, 8 - y) for x, y in Q]                   # rotation 180 degrees
    B = [(10 - x, y) for x, y in Q]                       # reflection in the line x = 5
    C = [(6, 5), (8, 5), (9, 6), (7, 7), (6, 7)]          # left side 2 units, not 1
    D = [(x, y + 4) for x, y in Q]                        # translation 4 up
    grid_shapes("l1_y1", [("Q", Q, "blue"), ("A", A, None), ("B", B, None), ("C", C, None), ("D", D, None)])


# ---------------- Concept 2 ----------------

def fig_ex7():
    T = book(1.5, 82.3, 138.5, ox=16, oy=18)
    A, B, C, D = (T(p) for p in ((82.3, 138.5), (138.6, 169.5), (129.6, 189.2), (82.3, 189.2)))
    E, H, G, F = iso_image([A, B, C, D], [T(p) for p in ((285.0, 195.4), (228.7, 164.3), (237.7, 144.6), (285.0, 144.6))])
    f = CF(340, 112)
    shape(f, [A, B, C, D], ["A", "B", "C", "D"], stroke="blue")
    shape(f, [E, H, G, F], ["E", "H", "G", "F"], stroke="blue")
    save("l1_ex7", f)


def quad_pair(name, src, names1, mapping, names2, place, w=330, h=130, rot=None, refl=False):
    """src: first quadrilateral (page px); its congruent image is rotated by rot degrees (and reflected in a
    vertical line first if refl) and moved so that its centroid is at place. names2[i] labels image of src[i]."""
    from math import cos, sin, radians
    c = centroid(src)
    out = []
    for x, y in src:
        x, y = x - c[0], y - c[1]
        if refl:
            x = -x
        a = radians(rot or 0)
        out.append((place[0] + x * cos(a) + y * sin(a), place[1] - x * sin(a) + y * cos(a)))
    f = CF(w, h)
    shape(f, src, names1, stroke="blue")
    shape(f, out, names2, stroke="blue")
    save(name, f)


def tri_pair(name, src, names1, kinds, rot, refl, place, names2, w=300, h=120):
    from math import cos, sin, radians
    c = centroid(src)
    out = []
    for x, y in src:
        x, y = x - c[0], y - c[1]
        if refl:
            x = -x
        a = radians(rot)
        out.append((place[0] + x * cos(a) + y * sin(a), place[1] - x * sin(a) + y * cos(a)))
    f = CF(w, h)
    shape(f, src, names1, stroke="blue")
    shape(f, out, names2, stroke="blue")
    marks_tri(f, src, kinds, r=12)
    marks_tri(f, out, kinds, r=12)
    save(name, f)


def fig_demo2():
    # Tutor demo: PQRS and its image under a 90 degree clockwise turn; P->Y, Q->Z, R->W, S->X
    quad_pair("l1_d2q", [(16, 20), (110, 36), (84, 100), (16, 84)], ["P", "Q", "R", "S"], None,
              ["Y", "Z", "W", "X"], (196, 66), w=262, h=132, rot=-90)
    # Tutor demo triangles: L right angle, M dot, N circle; image by reflection and turn: L->T, M->R, N->S
    tri_pair("l1_d2t", [(20, 96), (74, 96), (20, 22)], ["L", "M", "N"], ["R", "dot", "o"], rot=150, refl=True,
             place=(162, 64), names2=["T", "R", "S"], w=222, h=124)
    # Your turn: ABCD and its image under a reflection; A->G, B->F, C->E, D->H
    quad_pair("l1_y2q", [(16, 30), (70, 16), (120, 70), (36, 98)], ["A", "B", "C", "D"], None,
              ["G", "F", "E", "H"], (228, 53.5), w=294, h=124, rot=0, refl=True)
    # Your turn triangles: P right angle, Q dot, R circle; image by a turn: P->Y, Q->Z, R->X
    tri_pair("l1_y2t", [(18, 96), (104, 96), (18, 24)], ["P", "Q", "R"], ["R", "dot", "o"], rot=-120, refl=False,
             place=(192, 62), names2=["Y", "Z", "X"], w=250, h=124)


# ---------------- Homework (Exercise 8D) ----------------

def fig_q1_3():
    # Q1 reflection in the dashed line
    T = book(1.5, 331.9, 412.0, ox=14, oy=16)
    f = CF(240, 66)
    A, B, C = T((331.9, 435.1)), T((379.1, 435.1)), T((379.1, 412.0))
    E, D, F = T((421.4, 435.1)), T((468.6, 435.1)), T((421.4, 412.0))
    f.line(T((398.8, 405))[0], 4, T((398.8, 405))[0], 64, dash="4 3", width=1.1)
    shape(f, [A, B, C], ["A", "B", "C"], stroke="blue")
    shape(f, [D, E, F], ["D", "E", "F"], stroke="blue")
    save("l1_q1", f)
    # Q2 translation
    T = book(1.5, 335.8, 531.9, ox=14, oy=16)
    f = CF(232, 76)
    A, B, C = T((335.8, 561.4)), T((393.4, 561.4)), T((351.2, 531.9))
    D, E, F = T((410.0, 562.2)), T((467.6, 562.2)), T((425.4, 532.7))
    shape(f, [A, B, C], stroke="blue")
    shape(f, [D, E, F], stroke="blue")
    f.lab(A, "A", dx=-5, dy=12).lab(B, "B", dx=-2, dy=13).lab(C, "C", dy=-9)
    f.lab(D, "D", dx=4, dy=13).lab(E, "E", dx=6, dy=12).lab(F, "F", dy=-9)
    save("l1_q2", f)
    # Q3 rotation (DEF is drawn as the exact image of ABC)
    T = book(1.5, 343.0, 63.1, ox=16, oy=16)
    A, B, C = T((343.0, 90.9)), T((397.5, 86.9)), T((416.8, 63.1))
    D, E, F = iso_image([A, B, C], [T((446.6, 68.6)), T((446.8, 118.1)), T((469.1, 129.6))])
    f = CF(230, 128)
    shape(f, [A, B, C], ["A", "B", "C"], stroke="blue")
    shape(f, [D, E, F], ["D", "E", "F"], stroke="blue")
    save("l1_q3", f)


def fig_q4_5():
    T = book(1.5, 338.3, 196.2, ox=16, oy=16)
    f = CF(230, 92)
    shape(f, [T(p) for p in ((338.3, 196.2), (356.4, 196.2), (380.2, 235.6), (338.3, 235.6))], ["A", "D", "C", "B"], stroke="blue")
    shape(f, [T(p) for p in ((418.8, 196.2), (460.8, 196.2), (460.8, 235.6), (442.7, 235.6))], ["G", "F", "E", "H"], stroke="blue")
    save("l1_q4", f)
    T = book(1.5, 333.8, 292.8, ox=16, oy=16)
    f = CF(240, 132)
    shape(f, [T(p) for p in ((333.8, 292.8), (360.8, 292.8), (398.5, 306.7), (398.5, 326.5), (333.8, 326.5))],
          ["A", "E", "D", "C", "B"], stroke="blue")
    shape(f, [T(p) for p in ((428.7, 292.8), (448.5, 292.8), (462.4, 330.6), (462.4, 357.6), (428.7, 357.6))],
          ["H", "I", "J", "F", "G"], stroke="blue")
    save("l1_q5", f)


def fig_q6():
    s = 1.2
    T = book(s, 71.4, 388.5, ox=12, oy=12)
    f = CF(int(381 * s) + 24, int(262 * s) + 24)
    tris = {"A": ((71.7, 424.7), (92.3, 389.0), (112.9, 424.7)), "B": ((175.8, 419.1), (196.9, 389.2), (213.6, 449.0)),
            "F": ((183.8, 529.1), (193.0, 476.9), (181.9, 474.9), (172.7, 527.1)),
            "G": ((239.3, 475.4), (271.7, 486.5), (261.7, 501.3)),
            "H": ((344.0, 486.9), (366.2, 475.2), (362.0, 500.0), (380.0, 517.6), (355.1, 521.2), (344.0, 543.7),
                  (332.8, 521.2), (308.0, 517.6), (326.0, 500.0), (321.7, 475.2)),
            "J": ((72.5, 580.2), (104.9, 591.2), (94.9, 606.1)), "N": ((391.2, 650.0), (390.8, 580.2), (451.4, 614.8))}
    rects = {"C": (279.9, 388.5, 354.6, 420.5), "I": (405.0, 474.8, 437.0, 549.6), "L": (238.2, 579.6, 277.8, 619.3),
             "M": (321.6, 579.6, 339.6, 597.6)}
    circs = {"D": ((404.0, 408.4), 19.9), "E": ((106.3, 509.8), 34.9), "K": ((174.6, 599.5), 19.85)}
    labs = {"A": (92.6, 411.9), "B": (192.6, 416.6), "C": (317.1, 405.2), "D": (404.1, 409.1), "E": (106.3, 510.5),
            "F": (182.7, 502.7), "G": (259.4, 490.6), "H": (343.7, 506.7), "I": (420.7, 512.9), "J": (91.5, 594.7),
            "K": (174.4, 600.2), "L": (258.1, 600.1), "M": (330.3, 589.3), "N": (413.0, 615.8)}
    for k, pts in tris.items():
        f.poly([T(p) for p in pts], color=None, opacity=0, stroke="blue", width=1.4)
    for k, (x0, y0, x1, y1) in rects.items():
        f.poly([T((x0, y0)), T((x1, y0)), T((x1, y1)), T((x0, y1))], color=None, opacity=0, stroke="blue", width=1.4)
    for k, (c, r) in circs.items():
        f.circle(T(c), r * s, color="blue", width=1.4)
    for k, p in labs.items():
        q = T(p)
        ftext(f, q[0], q[1], k, size=10.5, rmax=18)
    save("l1_q6", f)


def fig_q7():
    u = 30
    f = CF(4 * u + 56, 4 * u + 44)
    G = lambda p: (12 + p[0] * u, 10 + (4 - p[1]) * u)
    for k in range(5):
        f.seg(G((k, 0)), G((k, 4)), color="blue", width=1.3)
        f.seg(G((0, k)), G((4, k)), color="blue", width=1.3)
    for a, b in (((0, 0), (4, 4)), ((0, 4), (4, 0)), ((0, 2), (2, 4)), ((2, 4), (4, 2)), ((4, 2), (2, 0)), ((2, 0), (0, 2))):
        f.seg(G(a), G(b), color="blue", width=1.3)
    # dimension arrows: 4 by 4
    y = G((0, 0))[1] + 14
    f.arrow(G((2, 0))[0] - 12, y, G((0, 0))[0], y, width=0.9, head=6).arrow(G((2, 0))[0] + 12, y, G((4, 0))[0], y, width=0.9, head=6)
    f.line(G((0, 0))[0], y - 4, G((0, 0))[0], y + 4, width=0.9).line(G((4, 0))[0], y - 4, G((4, 0))[0], y + 4, width=0.9)
    f.text(G((2, 0))[0], y, "4", size=12)
    x = G((4, 0))[0] + 16
    f.arrow(x, G((0, 2))[1] - 12, x, G((0, 4))[1], width=0.9, head=6).arrow(x, G((0, 2))[1] + 12, x, G((0, 0))[1], width=0.9, head=6)
    f.line(x - 4, G((0, 4))[1], x + 4, G((0, 4))[1], width=0.9).line(x - 4, G((0, 0))[1], x + 4, G((0, 0))[1], width=0.9)
    f.text(x, G((0, 2))[1], "4", size=12)
    save("l1_q7", f)


def fig_q8():
    s = 1.15
    T = book(s, 71.4, 233.9, ox=12, oy=12)
    f = CF(int(383 * s) + 24, int(222 * s) + 24)
    tris = {"A": ((71.4, 234.1), (71.4, 264.9), (126.6, 264.9)), "B": ((175.5, 286.2), (230.9, 259.4), (234.7, 234.5)),
            "C": ((280.2, 279.4), (301.5, 234.4), (322.9, 279.4)), "D": ((383.9, 269.0), (445.7, 233.9), (453.6, 249.4)),
            "E": ((83.8, 302.1), (92.3, 324.3), (71.8, 339.1)), "F": ((222.2, 302.0), (175.8, 343.8), (208.6, 378.1)),
            "G": ((280.9, 317.6), (303.8, 323.7), (316.4, 301.7)), "H": ((411.2, 317.3), (446.3, 301.8), (384.1, 383.7)),
            "I": ((71.6, 398.5), (92.0, 398.5), (81.4, 423.0)), "J": ((176.0, 455.1), (206.8, 455.1), (206.8, 399.9)),
            "K": ((322.9, 398.5), (301.5, 443.5), (280.2, 398.5))}
    labs = {"A": (88.6, 255.9), "B": (220.4, 257.1), "C": (301.3, 262.9), "D": (435.3, 249.3), "E": (83.1, 321.7),
            "F": (199.9, 342.6), "G": (300.0, 316.6), "H": (416.2, 327.3), "I": (81.6, 406.6), "J": (196.5, 436.9),
            "K": (301.1, 415.4)}
    for k, pts in tris.items():
        f.poly([T(p) for p in pts], color=None, opacity=0, stroke="blue", width=1.4)
    for k, p in labs.items():
        q = T(p)
        ftext(f, q[0], q[1], k, size=10.5, rmax=18)
    save("l1_q8", f)


def fig_q9():
    T = book(1.5, 91.3, 500.8, ox=14, oy=16)
    f = CF(160, 104)
    shape(f, [T(p) for p in ((91.3, 549.6), (120.0, 549.6), (91.3, 502.6))], ["A", "B", "C"], stroke="blue")
    shape(f, [T(p) for p in ((177.3, 500.8), (148.6, 500.8), (148.6, 547.8))], ["D", "E", "F"], stroke="blue")
    save("l1_q9a", f)
    T = book(1.5, 298.6, 498.2, ox=14, oy=16)
    f = CF(240, 116)
    shape(f, [T(p) for p in ((331.9, 499.2), (352.9, 499.2), (352.9, 554.9), (298.6, 554.9))], ["A", "B", "C", "D"], stroke="blue")
    shape(f, [T(p) for p in ((435.9, 498.2), (435.9, 553.9), (414.9, 553.9), (381.6, 498.2))], ["W", "X", "Y", "Z"], stroke="blue")
    save("l1_q9b", f)
    T = book(1.5, 86.5, 597.7, ox=14, oy=18)
    f = CF(232, 72)
    A, B, C, D = (T(p) for p in ((86.5, 597.7), (109.8, 597.7), (139.8, 597.7), (125.5, 622.7)))
    W, X, Z, Y = (T(p) for p in ((222.5, 623.3), (199.2, 623.3), (169.2, 623.3), (183.5, 598.3)))
    f.poly([A, C], color=None, opacity=0, stroke="blue", closed=False)
    f.poly([B, C, D], color=None, opacity=0, stroke="blue")
    f.poly([Z, W], color=None, opacity=0, stroke="blue", closed=False)
    f.poly([Z, X, Y], color=None, opacity=0, stroke="blue")
    for p, s, dy in ((A, "A", -10), (B, "B", -10), (C, "C", -10)):
        f.lab(p, s, dy=dy)
    f.lab(D, "D", dy=12)
    for p, s, dy in ((W, "W", 12), (X, "X", 12), (Z, "Z", 12)):
        f.lab(p, s, dy=dy)
    f.lab(Y, "Y", dy=-10)
    save("l1_q9c", f)
    # Q9d: pentagons with equal-side marks; STXZW is drawn as the exact image of ABCDE (A->T, B->Z, C->X, D->S, E->W)
    T = book(1.5, 302.7, 596.8, ox=16, oy=18)
    A, B, C, D, E = (T(p) for p in ((326.8, 602.6), (354.5, 596.8), (352.4, 625.0), (324.8, 646.9), (302.7, 617.3)))
    Tt, Zz, Xx, Ss, Ww = iso_image([A, B, C, D, E], [T(p) for p in ((418.5, 641.9), (446.4, 647.0), (443.5, 618.8), (415.3, 597.6), (394.0, 627.8))])
    f = CF(250, 104)
    P1 = [A, B, C, D, E]
    P2 = [Tt, Zz, Xx, Ss, Ww]
    shape(f, P1, ["A", "B", "C", "D", "E"], stroke="blue")
    shape(f, P2, ["T", "Z", "X", "S", "W"], stroke="blue")
    for p, q, n in ((A, E, 1), (A, B, 1), (B, C, 1), (E, D, 2), (D, C, 2)):
        f.tick(p, q, n)
    for p, q, n in ((Tt, Ww, 1), (Zz, Tt, 1), (Xx, Zz, 1), (Ww, Ss, 2), (Ss, Xx, 2)):
        f.tick(p, q, n)
    save("l1_q9d", f)


def fig_q10_11():
    T = book(1.6, 413.4, 68.3, ox=16, oy=16)
    A, B, C, M = T((413.4, 143.6)), T((478.0, 143.6)), T((445.7, 68.3)), T((445.7, 143.6))
    f = CF(136, 156)
    f.seg(C, M, color="rose", width=1.1, dash="4 3")
    shape(f, [A, B, C], stroke="blue")
    f.tick(A, C, 2).tick(B, C, 2).tick(A, M, 1).tick(M, B, 1)
    f.lab(A, "A", dx=-6, dy=13).lab(B, "B", dx=6, dy=13).lab(M, "M", dy=13).lab(C, "C", dy=-10)
    save("l1_q10", f)
    T = book(1.6, 407.4, 190.9, ox=18, oy=16)
    A, B, C, D = T((407.4, 212.1)), T((439.7, 190.9)), T((472.0, 212.1)), T((439.7, 270.9))
    f = CF(140, 162)
    f.seg(A, C, color="rose", width=1.1, dash="4 3").seg(B, D, color="rose", width=1.1, dash="4 3")
    shape(f, [A, B, C, D], ["A", "B", "C", "D"], stroke="blue")
    f.tick(A, B, 1).tick(B, C, 1).tick(A, D, 2).tick(C, D, 2)
    save("l1_q11", f)


def fig_q14():
    u = 21
    f = CF(11 * u + 34, 11 * u + 26)
    G = lambda p: (18 + (p[0] + 5.5) * u, 12 + (5.5 - p[1]) * u)
    grid(f, G, range(-6, 7), range(-6, 7))
    shp = {"A": ([(-3, 4), (-2, 4), (-2, 3), (-1, 3), (-1, 2), (-3, 2)], "violet", 0.35),
           "A′": ([(2, 0), (4, 0), (4, 2), (3, 2), (3, 1), (2, 1)], "violet", 0.15),
           "B": ([(-4, -1), (-4, -3), (-3, -3)], "rose", 0.4),
           "B′": ([(1, 4), (2, 4), (2, 2)], "rose", 0.15),
           "C": ([(3, 4), (4, 5), (5, 5), (5, 4), (4, 3)], "green", 0.15),
           "C′": ([(-1, -1), (0, -2), (-1, -3), (-2, -3), (-2, -2)], "green", 0.35)}
    for k, (pts, col, op) in shp.items():
        f.poly([G(p) for p in pts], color=col, opacity=op, stroke=col, width=1.6)
    axes(f, G, (-6, 6.3), (-6, 6.3))
    for k, p in (("A", (-2.5, 4.5)), ("A′", (4.6, 1.3)), ("B", (-3.6, -3.6)), ("B′", (1.5, 4.5)), ("C", (5.6, 4.5)),
                 ("C′", (-1.6, -3.6))):
        q = G(p)
        mtext(f, q[0], q[1], k, size=12, italic=True)
    save("l1_q14", f)


# ---------------- Past papers ----------------

def fig_pp():
    # Sydney Grammar 2023 Q1(e): triangles ABC and XYZ (vector coordinates of the paper, p2)
    T = book(0.95, 127.3, 361.8, ox=16, oy=18)
    f = CF(290, 104)
    B, A, C = T((127.3, 369.9)), T((189.0, 363.7)), T((249.3, 447.7))
    X, Y, Z = T((332.4, 445.8)), T((394.2, 439.6)), T((272.2, 361.8))
    shape(f, [A, B, C], ["A", "B", "C"], width=1.0)
    shape(f, [X, Y, Z], ["X", "Y", "Z"], width=1.0)
    ftext(f, (A[0] + B[0]) / 2, (A[1] + B[1]) / 2 - 9, "3", size=11.5)
    ftext(f, (B[0] + C[0]) / 2 - 7, (B[1] + C[1]) / 2 + 10, "7", size=11.5)
    ftext(f, (A[0] + C[0]) / 2 + 10, (A[1] + C[1]) / 2 - 4, "5", size=11.5)
    save("l1_pp1", f)
    # Sydney Grammar 2020 Q2(h): AC and BD cross at O, their common midpoint (image measured from the paper, p4)
    s = 0.3
    O = (76, 70)
    P = {"B": (367, 48), "C": (613, 97), "O": (506, 227), "A": (399, 357), "D": (646, 407)}
    Q = {k: (O[0] + (x - 506) * s, O[1] + (y - 227) * s) for k, (x, y) in P.items()}
    A, B, C, D = Q["A"], Q["B"], Q["C"], Q["D"]
    f = CF(152, 140)
    f.seg(A, C).seg(B, D).seg(A, B).seg(C, D)
    f.tick(O, B, 2).tick(O, D, 2).tick(O, A, 1).tick(O, C, 1)
    f.lab(B, "B", dx=-8, dy=-6).lab(C, "C", dx=8, dy=-6).lab(A, "A", dx=-4, dy=13).lab(D, "D", dx=6, dy=12)
    f.lab(O, "O", dx=0, dy=15)
    falab(f, A, B, O, "65°", d=26, size=10.5)
    save("l1_pp2", f)


if __name__ == "__main__":
    fig_start(); fig_four(); fig_keytri(); fig_demo1(); fig_ex7(); fig_demo2()
    fig_q1_3(); fig_q4_5(); fig_q6(); fig_q7(); fig_q8(); fig_q9(); fig_q10_11(); fig_q14(); fig_pp()
