"""Figures for the Year 10 Trigonometry (part 2) pack: python3 figs.py  ->  svg/*.svg (every figure,
including Lesson T3's, which live in figs_t3.py and are drawn from the main block below)

Copied structure: workspace/build/int1/figs.py (Fig class, save via figfit).
Each figure redraws a diagram of its source (Year 11 Advanced book, Maths Pathway sheet or past paper)
with the same labels and layout; figures marked "our own" belong to pack-written examples.
"""
import os
import sys
from math import sin, cos, tan, atan2, pi, sqrt, radians, degrees, hypot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    from figfit import fit, untangle, separate  # nudges a flagged label (<= 8 px); grows the frame where a label would be clipped
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(fit(untangle(separate(g.svg()))))


class Fig:
    """Plain geometry diagram in pixel coordinates (y downwards)."""

    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def line(self, x1, y1, x2, y2, color="ink", width=1.6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ACC[color]}" stroke-width="{width}"{d} stroke-linecap="round"/>')
        return self

    def arrow(self, x1, y1, x2, y2, color="ink", width=1.6, head=7, dash=None):
        self.line(x1, y1, x2, y2, color, width, dash)
        a = atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head * cos(a - 0.4), y2 - head * sin(a - 0.4))
        p2 = (x2 - head * cos(a + 0.4), y2 - head * sin(a + 0.4))
        self.items.append(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} z" fill="{ACC[color]}"/>')
        return self

    def poly(self, pts, color="blue", opacity=0.18, stroke="ink", width=1.6, closed=True):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        fill = ACC[color] if color else "none"
        self.items.append(f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" stroke="{ACC[stroke]}" stroke-width="{width}" stroke-linejoin="round"/>')
        return self

    def circle(self, cx, cy, r, color="ink", width=1.5, fill="none", opacity=1):
        # drawn as a path (two half arcs), so that svg_overlap.py tests the curve, not its bounding box
        f = ACC[fill] if fill != "none" else "none"
        self.items.append(f'<path d="M{cx - r:.1f},{cy:.1f} A{r:.1f},{r:.1f} 0 1 0 {cx + r:.1f},{cy:.1f} A{r:.1f},{r:.1f} 0 1 0 {cx - r:.1f},{cy:.1f} Z" '
                          f'fill="{f}" fill-opacity="{opacity}" stroke="{ACC[color]}" stroke-width="{width}"/>')
        return self

    def path(self, d, color="blue", width=2.2, dash=None, fill="none", opacity=1):
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        f = ACC[fill] if fill != "none" else "none"
        self.items.append(f'<path d="{d}" fill="{f}" fill-opacity="{opacity}" stroke="{ACC[color]}" stroke-width="{width}"{ds} stroke-linejoin="round"/>')
        return self

    def arc(self, cx, cy, r, a0, a1, color="faint", width=1.3):
        """Arc from angle a0 to a1 (degrees, anticlockwise from +x on screen, i.e. upwards)."""
        x0, y0 = cx + r * cos(radians(a0)), cy - r * sin(radians(a0))
        x1, y1 = cx + r * cos(radians(a1)), cy - r * sin(radians(a1))
        large = 1 if abs(a1 - a0) > 180 else 0
        sweep = 0 if a1 > a0 else 1
        self.items.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"/>')
        return self

    def text(self, x, y, s, anchor="middle", size=12, color="ink", italic=False, weight=500):
        self.items.append(_txt(x, y, s, anchor, size=size, color=ACC[color], italic=italic, weight=weight))
        return self

    def dot(self, x, y, r=3, color="ink"):
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{ACC[color]}"/>')
        return self

    def raw(self, s):
        self.items.append(s)
        return self

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="Inter, Arial, sans-serif">' + "".join(self.items) + "</svg>")


# ---------------- geometry helpers (screen coordinates, y downwards) ----------------

def _dir(V, P):
    """Direction of P seen from V, in degrees anticlockwise from +x (upwards on screen)."""
    return degrees(atan2(-(P[1] - V[1]), P[0] - V[0]))


def _short(a0, a1):
    d = (a1 - a0 + 540) % 360 - 180
    return a0, a0 + d


def angle_arc(f, V, P, Q, r=16, color="faint"):
    a0, a1 = _short(_dir(V, P), _dir(V, Q))
    f.arc(V[0], V[1], r, a0, a1, color=color)


def angle_label(f, V, P, Q, s, rr=28, size=11.5, italic=False, color="ink"):
    a0, a1 = _short(_dir(V, P), _dir(V, Q))
    m = radians((a0 + a1) / 2)
    f.text(V[0] + rr * cos(m), V[1] - rr * sin(m) + 1, s, size=size, italic=italic, color=color)


def right_mark(f, V, P, Q, s=8):
    ux, uy = (P[0] - V[0]), (P[1] - V[1])
    n = hypot(ux, uy); ux, uy = ux / n * s, uy / n * s
    vx, vy = (Q[0] - V[0]), (Q[1] - V[1])
    n = hypot(vx, vy); vx, vy = vx / n * s, vy / n * s
    f.items.append(f'<path d="M{V[0]+ux:.1f},{V[1]+uy:.1f} L{V[0]+ux+vx:.1f},{V[1]+uy+vy:.1f} L{V[0]+vx:.1f},{V[1]+vy:.1f}" '
                   f'fill="none" stroke="{INK}" stroke-width="1.1"/>')


def side_label(f, P, Q, s, off=11, size=11.5, italic=False, flip=False):
    """Label at the midpoint of PQ, offset perpendicular (to the left of P->Q, or right if flip)."""
    mx, my = (P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    n = hypot(dx, dy)
    nx, ny = dy / n, -dx / n
    if flip:
        nx, ny = -nx, -ny
    f.text(mx + off * nx, my + off * ny + 1, s, size=size, italic=italic)


def triangle(f, A, B, C, fill=False):
    f.poly([A, B, C], color="blue" if fill else None, opacity=0.08 if fill else 0, width=1.5)


# ---------------- Revision: Topic 11 (Trigonometry C) ----------------

def fig_rev():
    # 5A: sides of a right-angled triangle named from the angle theta (book p149)
    f = Fig(220, 96)
    A, B, C = (20, 80), (170, 80), (170, 16)
    triangle(f, A, B, C)
    right_mark(f, B, A, C, 8)
    angle_arc(f, A, B, C, 26)
    angle_label(f, A, B, C, "θ", 38, italic=True)
    side_label(f, A, C, "hyp", 10)
    side_label(f, C, B, "opp", 18, flip=False)
    side_label(f, A, B, "adj", 12, flip=True)
    save("rev_sides", f)

    # 5A Example 2: theta at the top, opposite side 12 (base), adjacent side 7 (vertical)
    f = Fig(220, 100)
    A, B, C = (20, 84), (170, 84), (170, 22)
    triangle(f, A, B, C)
    right_mark(f, B, A, C, 8)
    angle_arc(f, C, A, B, 18)
    angle_label(f, C, A, B, "θ", 30, italic=True)
    side_label(f, C, B, "7", 10)
    side_label(f, A, B, "12", 12, flip=True)
    save("rev_ex2", f)

    # 5B: compass bearings and true bearings (book p156), two roses
    f = Fig(470, 200)
    for cx, kind in ((105, "compass"), (345, "true")):
        cy, R = 92, 66
        f.arrow(cx, cy, cx, cy - R - 6, width=1.3, head=6)
        f.arrow(cx, cy, cx, cy + R + 6, width=1.3, head=6)
        f.arrow(cx, cy, cx + R + 6, cy, width=1.3, head=6)
        f.arrow(cx, cy, cx - R - 6, cy, width=1.3, head=6)
        rays = [(110, "N20°W" if kind == "compass" else "340°T"), (60, "N30°E" if kind == "compass" else "030°T"),
                (-20, "S70°E" if kind == "compass" else "110°T"), (-135, "S45°W" if kind == "compass" else "225°T")]
        for a, s in rays:
            ex, ey = cx + R * cos(radians(a)), cy - R * sin(radians(a))
            f.arrow(cx, cy, ex, ey, width=1.3, head=6)
            lx, ly = cx + (R + 14) * cos(radians(a)), cy - (R + 12) * sin(radians(a))
            f.text(lx, ly, s, size=11)
        if kind == "compass":
            f.text(cx, cy - R - 16, "N", size=11.5).text(cx, cy + R + 20, "S", size=11.5)
            f.text(cx + R + 18, cy, "E", size=11.5).text(cx - R - 18, cy, "W", size=11.5)
            f.arc(cx, cy, 22, 90, 110).text(cx + 30 * cos(radians(132)), cy - 30 * sin(radians(132)), "20°", size=10.5)
            f.arc(cx, cy, 26, 60, 90).text(cx + 36 * cos(radians(40)), cy - 36 * sin(radians(40)), "30°", size=10.5)
            f.arc(cx, cy, 22, -90, -20).text(cx + 22, cy + 22, "70°", size=10.5)
            f.arc(cx, cy, 16, -135, -90).text(cx - 12, cy + 26, "45°", size=10.5)
            f.text(cx, cy + R + 36, "Compass bearing", size=11, color="faint")
        else:
            f.text(cx, cy - R - 16, "000°T", size=11).text(cx, cy + R + 20, "180°T", size=11)
            f.text(cx + R + 30, cy, "090°T", size=11).text(cx - R - 30, cy, "270°T", size=11)
            f.text(cx, cy + R + 36, "True bearing", size=11, color="faint")
    save("rev_bearings", f)

    # 5I: labelling convention for triangle ABC (book p206)
    f = Fig(170, 110)
    A, B, C = (110, 18), (148, 92), (22, 92)
    triangle(f, A, B, C)
    f.text(A[0], A[1] - 9, "A", size=11.5, italic=True).text(B[0] + 9, B[1] + 4, "B", size=11.5, italic=True)
    f.text(C[0] - 9, C[1] + 4, "C", size=11.5, italic=True)
    side_label(f, C, A, "b", 10, italic=True)
    side_label(f, A, B, "c", 10, italic=True)
    side_label(f, C, B, "a", 11, italic=True, flip=True)
    save("rev_abc", f)

    # 5J Example 29: sides 3, 4, 6 with theta between 3 and 4 (book p215)
    f = Fig(200, 110)
    T, P, Q = (60, 76), (24, 14), (182, 94)       # theta vertex, top-left, right
    triangle(f, T, P, Q)
    angle_arc(f, T, P, Q, 14)
    angle_label(f, T, P, Q, "θ", 26, italic=True)
    side_label(f, P, T, "3", 10, flip=True)
    side_label(f, T, Q, "4", 11, flip=True)
    side_label(f, P, Q, "6", 11)
    save("rev_ex29", f)

    # ---- warm-up diagrams ----
    # 5B Q4: X bottom, Y top-left (right angle), Z top-right; XY = 78, YZ = 61
    f = Fig(150, 150)
    X, Y, Z = (40, 132), (40, 22), (126, 22)
    triangle(f, X, Y, Z)
    right_mark(f, Y, X, Z, 8)
    f.text(X[0], X[1] + 13, "X", size=11.5, italic=True).text(Y[0] - 10, Y[1], "Y", size=11.5, italic=True)
    f.text(Z[0] + 10, Z[1], "Z", size=11.5, italic=True)
    side_label(f, Y, X, "78", 13, flip=True)
    side_label(f, Y, Z, "61", 10)
    angle_arc(f, X, Y, Z, 20)
    angle_label(f, X, Y, Z, "θ", 30, italic=True)
    save("rev_w1", f)

    # 5B Q7: start S, 120 km on a bearing of 130 deg T to E, then due west to F (due south of S)
    f = Fig(190, 150)
    S = (40, 34)
    L = 150
    E = (S[0] + L * sin(radians(130)) * 0.9, S[1] - L * cos(radians(130)) * 0.9)
    F = (S[0], E[1])
    f.arrow(S[0], S[1], S[0], S[1] - 26, width=1.3, head=6)
    f.line(*S, *E, width=1.5).line(*E, *F, width=1.5).line(*F, *S, width=1.5)
    right_mark(f, F, S, E, 8)
    f.arc(S[0], S[1], 14, 90, 90 - 130, color="faint")
    f.text(S[0] + 22, S[1] - 14, "130°", size=11)
    side_label(f, S, E, "120 km", 16)
    save("rev_w2", f)

    # 5B Q8: W top, car C on the street, B the base of the building; BC = 7 m, depression 73 deg
    f = Fig(130, 150)
    W, B, C = (40, 22), (40, 132), (78, 132)
    f.line(*W, *B, width=1.5).line(*B, *C, width=1.5).line(*W, *C, width=1.5)
    f.line(W[0], W[1], W[0] + 70, W[1], color="faint", width=1.2, dash="4 3")
    right_mark(f, B, W, C, 7)
    angle_arc(f, W, (W[0] + 60, W[1]), C, 20)
    angle_label(f, W, (W[0] + 60, W[1]), C, "73°", 32, size=10.5)
    f.text(W[0] - 9, W[1] - 2, "W", size=11.5, italic=True).text(B[0] - 9, B[1] + 4, "B", size=11.5, italic=True)
    f.text(C[0] + 9, C[1] + 4, "C", size=11.5, italic=True)
    f.text((B[0] + C[0]) / 2, B[1] + 13, "7 m", size=11)
    save("rev_w6", f)

    # 5K Q1 a-f (book p220)
    def k(name, P, labels, rights=(), arcs=(), w=170, h=120):
        f = Fig(w, h)
        triangle(f, *P)
        for (i, j, l) in rights:
            right_mark(f, P[i], P[j], P[l], 7)
        for (i, j, l, s, rr) in arcs:
            angle_arc(f, P[i], P[j], P[l], 14)
            angle_label(f, P[i], P[j], P[l], s, rr, size=10.5, italic=(s == "θ"))
        for (i, j, s, off, flip) in labels:
            side_label(f, P[i], P[j], s, off, italic=(s == "x"), flip=flip)
        save(name, f)

    k("rev_k1a", [(18, 96), (150, 96), (88, 20)], [(0, 2, "x", 10, False), (2, 1, "23", 11, False)],
      arcs=[(0, 1, 2, "43°", 34), (1, 2, 0, "57°", 32)])
    k("rev_k1b", [(30, 22), (156, 22), (74, 88)], [(0, 2, "13.5", 16, True), (2, 1, "x", 10, True)],
      rights=[(2, 0, 1)], arcs=[(0, 1, 2, "52°", 30)])
    k("rev_k1c", [(30, 98), (148, 98), (64, 18)], [(2, 0, "11", 10, True), (0, 1, "13", 12, True), (2, 1, "x", 10, False)],
      arcs=[(0, 1, 2, "62°", 28)])
    k("rev_k1d", [(26, 14), (26, 116), (160, 116)], [(0, 1, "24", 12, True), (0, 2, "x", 11, False)],
      rights=[(1, 0, 2)], arcs=[(2, 0, 1, "41°30′", 44)], w=180, h=134)
    k("rev_k1e", [(22, 100), (110, 82), (124, 14)], [(0, 2, "x", 11, False), (1, 2, "9.2", 13, True), (0, 1, "7.4", 12, True)],
      arcs=[(1, 0, 2, "98°", 22)])
    k("rev_k1f", [(22, 118), (150, 18), (164, 128)], [(0, 1, "x", 11, False), (1, 2, "18", 12, False)],
      arcs=[(1, 0, 2, "54°", 28), (0, 2, 1, "49°", 32)], w=180, h=140)
    # 5K Q2 a-c
    k("rev_k2a", [(26, 96), (150, 96), (70, 18)], [(0, 2, "10", 11, False), (2, 1, "11", 11, False), (0, 1, "12", 12, True)],
      arcs=[(0, 1, 2, "θ", 24)])
    k("rev_k2b", [(26, 124), (146, 124), (80, 14)], [(2, 1, "9", 11, False), (0, 1, "8", 12, True)],
      arcs=[(2, 0, 1, "θ", 26), (0, 1, 2, "67°", 30)], w=170, h=140)
    k("rev_k2c", [(22, 76), (160, 76), (106, 18)], [(0, 2, "13", 11, False), (0, 1, "17", 12, True)],
      rights=[(2, 0, 1)], arcs=[(0, 1, 2, "θ", 30)], h=100)
    # 5K Q7: AB = 4, AC = 5, BC = 7 (book p222)
    f = Fig(190, 120)
    B, C = (24, 100), (170, 100)
    A = (B[0] + 4 * 20.857 * cos(radians(44.415)), B[1] - 4 * 20.857 * sin(radians(44.415)))
    triangle(f, A, B, C)
    f.text(A[0], A[1] - 9, "A", size=11.5, italic=True).text(B[0] - 9, B[1] + 4, "B", size=11.5, italic=True)
    f.text(C[0] + 9, C[1] + 4, "C", size=11.5, italic=True)
    side_label(f, B, A, "4 cm", 18)
    side_label(f, A, C, "5 cm", 16)
    side_label(f, B, C, "7 cm", 12, flip=True)
    save("rev_k7", f)


# ---------------- Lesson T1: angles of any size ----------------

def axes(f, cx, cy, R, lab=True, ext=14, xlab="x", ylab="y", width=1.3):
    f.arrow(cx - R - ext, cy, cx + R + ext, cy, width=width, head=6)
    f.arrow(cx, cy + R + ext, cx, cy - R - ext, width=width, head=6)
    if lab:
        f.text(cx + R + ext + 8, cy + 4, xlab, size=11.5, italic=True)
        f.text(cx - 9, cy - R - ext + 2, ylab, size=11.5, italic=True)


def ray(f, cx, cy, a, L, color="ink", width=1.6, head=7):
    f.arrow(cx, cy, cx + L * cos(radians(a)), cy - L * sin(radians(a)), color=color, width=width, head=head)


def pt(cx, cy, a, L):
    return (cx + L * cos(radians(a)), cy - L * sin(radians(a)))


def unit_ticks(f, cx, cy, R):
    for (x, y, s, dx, dy) in ((cx + R, cy, "1", 7, 12), (cx - R, cy, "-1", -9, 12), (cx, cy - R, "1", 8, -7), (cx, cy + R, "-1", -10, 9)):
        f.text(x + dx, y + dy, s, size=10.5)


def fig_t1():
    # 5D p181: rays for 100, 40 (= -320, 400), 200 (= -160), 320 (= -40)
    f = Fig(260, 200)
    cx, cy = 120, 104
    axes(f, cx, cy, 80)
    for a, s, dx, dy, anc in ((100, "100°", -10, -4, "end"), (40, "−320°, 40°, 400°", 4, -10, "start"),
                              (200, "−160°, 200°", -6, 14, "middle"), (320, "−40°, 320°", 8, 14, "start")):
        ray(f, cx, cy, a, 86)
        x, y = pt(cx, cy, a, 86)
        f.text(x + dx, y + dy, s, size=11, anchor=anc)
    save("t1_rays", f)

    # Maths Pathway, Graphs of trig functions: equivalent angles (-45 deg and 410 deg)
    f = Fig(400, 186)
    for cx, cap in ((95, "−45° is equivalent to 315°"), (300, "410° is equivalent to 50°")):
        cy, R = 80, 60
        f.circle(cx, cy, R, width=1.3)
        axes(f, cx, cy, R, ext=16)
        unit_ticks(f, cx, cy, R)
        f.text(cx, cy + R + 36, cap, size=11.5, color="blue")
    cx, cy, R = 95, 80, 60
    f.line(cx, cy, *pt(cx, cy, -45, R), color="blue", width=1.6)
    f.arc(cx, cy, 16, 0, -45, color="blue")
    f.text(cx + 30, cy + 18, "−45°", size=11, color="blue", anchor="start")
    cx = 300
    f.line(cx, cy, *pt(cx, cy, 50, R), color="blue", width=1.6)
    f.circle(cx, cy, 10, color="blue", width=1.2)
    f.arc(cx, cy, 18, 0, 50, color="blue")
    f.text(cx + 34, cy - 15, "410°", size=11, color="blue")
    save("t1_equiv", f)

    # 5D p182: definition diagram, circle radius r, ray theta through P(x, y)
    f = Fig(190, 170)
    cx, cy, R = 80, 86, 50
    axes(f, cx, cy, R, ext=22)
    f.circle(cx, cy, R)
    P = pt(cx, cy, 52, R)
    ray(f, cx, cy, 52, R + 26)
    f.dot(*P, 2.8)
    f.text(P[0] + 8, P[1] + 4, "P(x, y)", size=11.5, anchor="start", italic=True)
    f.text(P[0] + 20, P[1] - 26, "θ", size=12, italic=True)
    f.text(cx + R + 6, cy + 13, "r", size=11.5, italic=True)
    save("t1_def", f)

    # 5D p182: agreement with the earlier definition (first-quadrant arc, P, M)
    f = Fig(190, 160)
    cx, cy, R = 40, 130, 100
    f.arrow(cx - 20, cy, cx + R + 24, cy, width=1.3, head=6).arrow(cx, cy + 14, cx, cy - R - 20, width=1.3, head=6)
    f.text(cx + R + 30, cy + 4, "x", size=11.5, italic=True).text(cx - 9, cy - R - 16, "y", size=11.5, italic=True)
    f.arc(cx, cy, R, -8, 100, color="ink", width=1.4)
    P = pt(cx, cy, 52, R)
    M = (P[0], cy)
    ray(f, cx, cy, 52, R + 26)
    f.dot(*P, 2.8)
    f.line(*P, *M, width=1.3)
    right_mark(f, M, (cx, cy), P, 7)
    angle_arc(f, (cx, cy), (cx + 20, cy), P, 18)
    f.text(cx + 27, cy - 9, "θ", size=11.5, italic=True)
    f.text(P[0] + 8, P[1] + 2, "P(x, y)", size=11.5, anchor="start", italic=True)
    f.text(P[0] + 20, P[1] - 26, "θ", size=12, italic=True)
    side_label(f, (cx, cy), P, "r", 10, italic=True)
    f.text(P[0] + 8, (P[1] + cy) / 2, "y", size=11.5, italic=True)
    f.text((cx + M[0]) / 2, cy + 13, "x", size=11.5, italic=True)
    f.text(M[0], cy + 14, "M", size=11.5, italic=True, anchor="start")
    f.text(cx - 9, cy + 12, "O", size=11.5, italic=True)
    f.text(cx + R + 8, cy + 13, "r", size=11.5, italic=True)
    save("t1_agree", f)

    # Maths Pathway, The Unit Circle: the unit circle box
    f = Fig(170, 160)
    cx, cy, R = 82, 80, 58
    f.circle(cx, cy, R)
    axes(f, cx, cy, R, ext=10)
    unit_ticks(f, cx, cy, R)
    f.line(cx, cy, *pt(cx, cy, 72, R), color="blue", width=1.6)
    f.arc(cx, cy, 14, 0, 72, color="blue")
    f.text(cx + 22, cy - 18, "θ", size=12, italic=True, color="blue")
    save("t1_unit", f)

    # Maths Pathway, The Unit Circle Q4(a) answer: 30 deg, (0.87, 0.5), sides 1, 0.87, 0.5
    def mp_tri(name, a, plab, lab1, labx, laby, alab):
        f = Fig(200, 170)
        cx, cy, R = 84, 84, 62
        f.circle(cx, cy, R)
        axes(f, cx, cy, R, ext=10, lab=False)
        unit_ticks(f, cx, cy, R)
        P = pt(cx, cy, a, R)
        M = (P[0], cy)
        f.line(cx, cy, *P, color="blue", width=1.7)
        f.line(*P, *M, color="faint", width=1.2, dash="3 2")
        right_mark(f, M, (cx, cy), P, 7)
        f.arc(cx, cy, 14, 0, a, color="blue")
        lx, ly = pt(cx, cy, a / 2, 38)
        f.text(lx, ly + 3, alab, size=9.5, color="blue")
        f.text(P[0] + 6, P[1] - 8, plab, size=11, anchor="start")
        side_label(f, (cx, cy), P, lab1, 9, size=11, italic=(lab1 == "1" and False))
        f.text(P[0] + 10, (P[1] + cy) / 2 + 2, laby, size=11, italic=(laby == "y"))
        f.text((cx + M[0]) / 2, cy + 13, labx, size=11, italic=(labx == "x"))
        save(name, f)

    mp_tri("t1_mp4", 30, "(0.87, 0.5)", "1", "0.87", "0.5", "30°")
    mp_tri("t1_mp5", 50, "(x, y)", "1", "x", "y", "θ")

    # Maths Pathway, Using Symmetry Q1(a): the tangent line x = 1 and tan 40 deg = 0.84
    f = Fig(210, 190)
    cx, cy, R = 92, 98, 62
    f.circle(cx, cy, R)
    axes(f, cx, cy, R, ext=12, lab=False)
    unit_ticks(f, cx, cy, R)
    f.line(cx + R, cy - R - 20, cx + R, cy + R + 20, width=1.4)
    T = (cx + R, cy - R * tan(radians(40)))
    f.line(cx, cy, *pt(cx, cy, 40, R), color="blue", width=1.7)
    f.line(*pt(cx, cy, 40, R), *T, color="faint", width=1.2, dash="3 2")
    f.line(cx, cy, *pt(cx, cy, 220, R + 20), color="faint", width=1.2, dash="3 2")
    f.dot(*T, 2.6)
    f.arc(cx, cy, 15, 0, 40, color="blue")
    f.text(cx + 28, cy - 9, "40°", size=10.5, color="blue")
    f.text(T[0] + 6, T[1] - 6, "(1, 0.84)", size=11, anchor="start")
    save("t1_tanline", f)

    # 5D p182: boundary angles
    f = Fig(250, 200)
    cx, cy, R = 120, 100, 54
    f.circle(cx, cy, R)
    f.arrow(cx - R - 40, cy, cx + R + 40, cy, width=1.3, head=6).arrow(cx, cy + R + 34, cx, cy - R - 34, width=1.3, head=6)
    for x, y in ((cx + R, cy), (cx - R, cy), (cx, cy - R), (cx, cy + R)):
        f.dot(x, y, 2.8)
    f.text(cx + R + 18, cy + 15, "(r, 0)", size=11, italic=True).text(cx - R - 18, cy + 15, "(−r, 0)", size=11, italic=True)
    f.text(cx - 22, cy - R - 9, "(0, r)", size=11, italic=True).text(cx - 26, cy + R + 14, "(0, −r)", size=11, italic=True)
    f.text(cx + R + 34, cy - 9, "0°", size=11).text(cx - R - 34, cy - 9, "180°", size=11)
    f.text(cx + 18, cy - R - 26, "90°", size=11).text(cx + 20, cy + R + 28, "270°", size=11)
    save("t1_boundary", f)

    # 5E p186: numbering of the quadrants
    f = Fig(160, 110)
    f.line(80, 6, 80, 104, width=1.3).line(6, 55, 154, 55, width=1.3)
    for x, y, s in ((43, 26, "2nd"), (117, 26, "1st"), (43, 76, "3rd"), (117, 76, "4th")):
        f.text(x, y, s, size=11).text(x, y + 16, "quadrant", size=11)
    save("t1_quads", f)

    # 5E p186: rays for 30, 150, 210, 330 deg
    f = Fig(220, 170)
    cx, cy = 110, 86
    f.line(cx - 92, cy, cx + 92, cy, width=1.3).line(cx, cy - 76, cx, cy + 76, width=1.3)
    f.text(cx + 98, cy + 4, "x", size=11.5, italic=True).text(cx - 8, cy - 72, "y", size=11.5, italic=True)
    for a, s, anc in ((30, "30°", "start"), (150, "150°", "end"), (210, "210°", "end"), (330, "330°", "start")):
        ray(f, cx, cy, a, 80, width=1.5, head=6)
        x, y = pt(cx, cy, a, 94)
        f.text(x, y + (-6 if a < 180 else 12), s, size=11, anchor=anc)
        lo, hi = {30: (0, 30), 150: (150, 180), 210: (180, 210), 330: (-30, 0)}[a]
        f.arc(cx, cy, 22, lo, hi, color="faint")
        lx, ly = pt(cx, cy, (lo + hi) / 2, 56)
        f.text(lx, ly + (4 if a < 180 else 1), "30°", size=10)
    save("t1_30", f)

    # 5E p186: signs of x and y in the four quadrants
    f = Fig(190, 160)
    cx, cy, R = 95, 82, 46
    f.circle(cx, cy, R)
    f.arrow(cx - R - 26, cy, cx + R + 30, cy, width=1.3, head=6).arrow(cx, cy + R + 26, cx, cy - R - 28, width=1.3, head=6)
    f.text(cx + R + 32, cy + 13, "x", size=11.5, italic=True).text(cx - 9, cy - R - 24, "y", size=11.5, italic=True)
    for a, s, anc in ((45, "(+, +)", "start"), (135, "(−, +)", "end"), (225, "(−, −)", "end"), (315, "(+, −)", "start")):
        ray(f, cx, cy, a, R + 14, width=1.3, head=6)
        P = pt(cx, cy, a, R)
        f.dot(*P, 2.6)
        f.text(P[0] + (8 if anc == "start" else -8), P[1] + 4, s, size=11, anchor=anc)
    save("t1_signs", f)

    # 5E p187: the ASTC diagram
    f = Fig(150, 110)
    f.line(75, 6, 75, 104, width=1.3).line(6, 55, 144, 55, width=1.3)
    for x, y, s in ((40, 34, "S"), (110, 34, "A"), (40, 82, "T"), (110, 82, "C")):
        f.text(x, y, s, size=13)
    save("t1_astc", f)

    # 5E p187: points P, Q, R, S on a circle of radius r at 30, 150, 210, 330 deg
    f = Fig(240, 200)
    cx, cy, R = 120, 100, 70
    f.circle(cx, cy, R)
    f.arrow(cx - R - 30, cy, cx + R + 30, cy, width=1.3, head=6).arrow(cx, cy + R + 22, cx, cy - R - 26, width=1.3, head=6)
    f.text(cx + R + 36, cy + 4, "x", size=11.5, italic=True).text(cx - 9, cy - R - 22, "y", size=11.5, italic=True)
    for a, s, lab, anc in ((30, "30°", "P", "start"), (150, "150°", "Q", "end"), (210, "210°", "R", "end"), (330, "330°", "S", "start")):
        ray(f, cx, cy, a, R + 16, width=1.3, head=6)
        P = pt(cx, cy, a, R)
        f.dot(*P, 2.6)
        x, y = pt(cx, cy, a, R + 22)
        f.text(x, y + (-4 if a < 180 else 10), s, size=10.5, anchor=anc)
        f.text(P[0] + (9 if anc == "start" else -9), P[1] + (10 if a < 180 else -4), lab, size=11.5, italic=True)
    for a in (30, 150, 210, 330):
        ref = 0 if a in (30, 330) else 180
        lo, hi = (ref, a) if a in (30, 150) else ((a, ref) if a == 210 else (-30, 0))
        f.arc(cx, cy, 20, lo, hi, color="faint")
        mid = {30: 15, 150: 165, 210: 195, 330: -15}[a]
        x, y = pt(cx, cy, mid, 52)
        f.text(x, y + (1.5 if a < 180 else 1), "30°", size=9.5)
    save("t1_pqrs", f)

    # 5E Example 10: quadrant diagrams for 300, -210 and 570 deg
    def qd(name, a, lab, rel, ref, ccw=True):
        f = Fig(170, 150)
        cx, cy = 85, 74
        f.line(cx - 66, cy, cx + 66, cy, width=1.3).line(cx, cy - 64, cx, cy + 64, width=1.3)
        ray(f, cx, cy, a, 64, width=1.6, head=7)
        x, y = pt(cx, cy, a, 74)
        f.text(x, y + 4, lab, size=11)
        lo, hi = sorted((ref, a % 360 if ref == 0 else (a % 360)))
        if ref == 360:
            lo, hi = a % 360, 360
        f.arc(cx, cy, 18, lo, hi, color="faint")
        x, y = pt(cx, cy, (lo + hi) / 2, 46)
        f.text(x, y + 4, rel, size=10.5)
        save(name, f)

    qd("t1_ex10a", 300, "300°", "60°", 360)
    qd("t1_ex10b", 150, "−210°", "30°", 180)
    qd("t1_ex10c", 210, "570°", "30°", 180)

    # Maths Pathway, Using Symmetry Q3(a) answer: main angle 140 deg, reference 40 deg, (-0.77, 0.64)
    f = Fig(220, 170)
    cx, cy, R = 120, 86, 60
    f.circle(cx, cy, R)
    axes(f, cx, cy, R, ext=10, lab=False)
    unit_ticks(f, cx, cy, R)
    P = pt(cx, cy, 140, R)
    M = (P[0], cy)
    f.line(cx, cy, *P, color="blue", width=1.7)
    f.line(*P, *M, color="faint", width=1.2, dash="3 2")
    f.arc(cx, cy, 14, 0, 140, color="blue")
    f.text(cx + 18, cy - 18, "140°", size=10.5, color="blue")
    f.arc(cx, cy, 20, 140, 180, color="faint")
    lx, ly = pt(cx, cy, 160, 36)
    f.text(lx, ly + 3, "40°", size=10, color="faint")
    f.text(P[0] - 4, P[1] - 10, "(−0.77, 0.64)", size=11, anchor="end")
    save("t1_sym140", f)

    # 5E p175: the graphs of sin x, cos x and tan x for -360 <= x <= 360
    ticks = [(v, f"{v}°") for v in (-360, -270, -180, -90, 90, 180, 270, 360)]
    for name, fn, lab in (("t1_gsin", lambda t: sin(radians(t)), "y = sin x"), ("t1_gcos", lambda t: cos(radians(t)), "y = cos x")):
        g = Graph(-380, 380, -1.3, 1.3, w=620, h=120, pad=(14, 28, 16, 22))
        g.axes("x", "y")
        g.xticks(ticks)
        g.yticks([(1, ""), (-1, "-1")])
        g.label(0, 1, "1", dx=-8, dy=10 if name == "t1_gcos" else 0, anchor="end", size=11)
        g.curve(fn, color="blue", width=2)
        g.label(-380, 1.15, lab, anchor="start", size=11.5, color="blue")
        save(name, g)
    g = Graph(-380, 380, -2.6, 2.6, w=620, h=150, pad=(14, 28, 16, 22))
    g.axes("x", "y")
    g.xticks([(v, f"{v}°") for v in (-360, -180, 180, 360)] + [(-270, ""), (-90, ""), (90, ""), (270, "")])
    g.yticks([(1, ""), (-1, "")])
    g.label(0, 1, "1", dx=-7, anchor="end", size=11).label(0, -1, "-1", dx=7, anchor="start", size=11)
    for a in (-270, -90, 90, 270):
        g.vline(a, color="faint")
        g.label(a, 0, f"{a}°", anchor="start", dx=4, dy=14, size=11)
    for k in range(-2, 3):
        g.curve(lambda t: tan(radians(t)), color="blue", width=2, x0=max(-380, k * 180 - 82), x1=min(380, k * 180 + 82))
    g.label(-380, 2.35, "y = tan x", anchor="start", size=11.5, color="blue")
    g.hline(1, x0=0, x1=45).vline(45, 0, 1).hline(-1, x0=-45, x1=0).vline(-45, -1, 0)
    g.label(45, 0, "45°", dy=14, size=10.5).label(-45, 0, "−45°", dy=-13, size=10.5)
    save("t1_gtan", g)

    # 6B p227: angle of inclination, acute and obtuse
    f = Fig(420, 170)
    for k, (cx, a) in enumerate(((110, 45), (300, 135))):
        cy = 96
        f.arrow(cx - 80, cy, cx + 86, cy, width=1.3, head=6).arrow(cx, cy + 62, cx, cy - 84, width=1.3, head=6)
        f.text(cx + 98, cy + 4, "x", size=11.5, italic=True).text(cx - 9, cy - 80, "y", size=11.5, italic=True)
        f.arrow(cx - 80 * cos(radians(a)), cy + 80 * sin(radians(a)), *pt(cx, cy, a, 96), width=1.6, head=7)
        f.arrow(*pt(cx, cy, a, 0), *pt(cx, cy, a + 180, 82), width=1.6, head=7)
        P = pt(cx, cy, a, 68)
        M = (P[0], cy)
        f.line(*P, *M, color="faint", width=1.2, dash="3 2")
        right_mark(f, M, (cx, cy), P, 7)
        f.path(f"M{cx},{cy} L{cx + 16},{cy} A16,16 0 0 0 {pt(cx, cy, a, 16)[0]:.1f},{pt(cx, cy, a, 16)[1]:.1f} Z", color="blue", width=1, fill="blue", opacity=0.35)
        x, y = pt(cx, cy, a / 2 if a < 90 else a * 0.62, 30)
        f.text(x, y + 4, "α", size=12, italic=True)
        f.text(P[0] + (-10 if a < 90 else 10), P[1] - 8, "P", size=11.5, italic=True)
        f.text(M[0], cy + 14, "M", size=11.5, italic=True)
        f.text(cx + (10 if a < 90 else -10), cy + 14, "O", size=11.5, italic=True)
    save("t1_incl", f)

    # 6B Example 6: A(-3, 5), B(-6, 0), O(0, 0)
    g = Graph(-7, 1, -0.8, 5.8, w=200, h=150, pad=(10, 22, 14, 18))
    g.axes("x", "y")
    g.items.append(f'<polygon points="{g.X(-3)},{g.Y(5)} {g.X(-6)},{g.Y(0)} {g.X(0)},{g.Y(0)}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    g.hline(5, x0=-3, x1=0)
    g.vline(-3, 0, 5)
    g.label(-3, 5, "A", dy=-9, italic=True)
    g.label(-6, 0, "B", dx=-6, dy=-9, italic=True)
    g.label(0, 0, "O", dx=-8, dy=11, italic=True)
    g.label(-6, 0, "−6", dy=13, size=10.5)
    g.label(-3, 0, "−3", dy=13, size=10.5)
    g.label(0, 5, "5", dx=8, size=10.5, anchor="start")
    save("t1_ex6", g)

    # Maths Pathway, The Unit Circle Q7: an unknown angle in the second quadrant
    f = Fig(200, 170)
    cx, cy, R = 100, 86, 62
    f.circle(cx, cy, R)
    axes(f, cx, cy, R, ext=12)
    unit_ticks(f, cx, cy, R)
    P = pt(cx, cy, 142, R)
    M = (P[0], cy)
    f.line(cx, cy, *P, color="blue", width=1.7)
    f.line(*P, *M, color="faint", width=1.2, dash="3 2")
    right_mark(f, M, (cx, cy), P, 7)
    f.arc(cx, cy, 13, 0, 142, color="blue")
    f.text(cx + 14, cy - 22, "θ°", size=11, color="blue", italic=True)
    save("t1_mpq7", f)

    # Maths Pathway, Graphs of Trigonometric Functions Q6 and Q7: sin and cos for 0 to 360 with key points
    for name, fn, lab in (("t1_mp6", lambda t: sin(radians(t)), "sin(θ)"), ("t1_mp7", lambda t: cos(radians(t)), "cos(θ)")):
        g = Graph(-30, 390, -1.3, 1.3, w=330, h=120, pad=(14, 24, 18, 14))
        g.axes("θ", lab)
        g.xticks([(90, ""), (180, ""), (270, ""), (360, "")])
        g.yticks([(1, "1" if name == "t1_mp6" else ""), (-1, "-1")])
        if name == "t1_mp7":
            g.label(0, 1, "1", dx=-8, dy=11, anchor="end", size=11)
        g.curve(fn, color="blue", width=2, x0=-25, x1=380)
        for v in (0, 90, 180, 270, 360):
            g.dot(v, round(fn(v)), color="blue", r=3)
        for v in (90, 180, 270, 360):
            up = round(fn(v)) < 0 or (round(fn(v)) == 0 and fn(v + 10) < 0)
            g.label(v, 0, f"{v}°", dx=12 if round(fn(v)) == 0 else 0, dy=-12 if up else 13, size=10.5)
        save(name, g)


def fig_t1_hw():
    # 5D Q5 (book p184): rays a-f
    f = Fig(270, 240)
    cx, cy = 135, 116
    f.line(cx - 108, cy, cx + 108, cy, width=1.3).line(cx, cy - 104, cx, cy + 108, width=1.3)
    for a, s in ((70, "a"), (100, "b"), (140, "c"), (200, "d"), (240, "e"), (340, "f")):
        ray(f, cx, cy, a, 92, width=1.5, head=6)
        x, y = pt(cx, cy, a, 104)
        f.text(x, y + 4, s, size=12, color="green", weight=700)
    for lo, hi, s, r, m in ((70, 90, "20°", 30, 52), (90, 100, "10°", 44, 116), (140, 180, "40°", 30, 160),
                            (180, 200, "20°", 56, 190), (240, 270, "30°", 34, 258), (340, 360, "20°", 56, 350)):
        f.arc(cx, cy, r, lo, hi, color="faint")
        x, y = pt(cx, cy, m, r + 14)
        f.text(x, y + (4 if m < 180 else 1), s, size=10.5)
    save("hw_5d5", f)

    # 5D Q6 a-d (book p184)
    for name, (X, Y), rl, plab in (("hw_5d6a", (3, 4), "5", "(3, 4)"), ("hw_5d6b", (-4, 3), "5", "(−4, 3)"),
                                    ("hw_5d6c", (-1, -2), "√5", "(−1, −2)"), ("hw_5d6d", (12, -5), "13", "(12, −5)")):
        f = Fig(170, 150)
        cx, cy, R = 82, 74, 42
        f.line(cx - R - 22, cy, cx + R + 22, cy, width=1.2).line(cx, cy - R - 26, cx, cy + R + 26, width=1.2)
        f.circle(cx, cy, R, width=1.3)
        a = degrees(atan2(Y, X))
        P = pt(cx, cy, a, R)
        ray(f, cx, cy, a, R + 24, width=1.5, head=6)
        f.dot(*P, 2.6)
        right = X > 0
        f.text(P[0] + (8 if right else -8), P[1] + (12 if Y < 0 else -6), plab, size=11, anchor="start" if right else "end")
        e = pt(cx, cy, a, R + 34)
        f.text(e[0] + (4 if right else -4) + (8 if Y < 0 and right else 0), e[1] + 4 - (10 if Y < 0 and right else 0), "θ", size=12, italic=True)
        f.text(cx + R + 8, cy + (13 if Y > 0 else -7), rl, size=11, anchor="start")
        save(name, f)

    # 5D Q8 (book p185): sin x and cos x on a grid
    g = Graph(-40, 400, -1.25, 1.25, w=560, h=260, pad=(30, 20, 14, 18))
    for v in range(-40, 401, 10):
        g.vline(v, -1.25, 1.25, color="faint", dash=None, width=0.6 if v % 90 else 1.0)
    for k in range(-12, 13):
        y = k / 10
        g.hline(y, x0=-40, x1=400, color="faint", dash=None, width=1.0 if k % 5 == 0 else 0.6)
    g.items.append(f'<line x1="{g.X(0)}" y1="{g.Y(-1.25)}" x2="{g.X(0)}" y2="{g.Y(1.25)}" stroke="{INK}" stroke-width="1.3"/>')
    g.items.append(f'<line x1="{g.X(-40)}" y1="{g.Y(0)}" x2="{g.X(400)}" y2="{g.Y(0)}" stroke="{INK}" stroke-width="1.3"/>')
    g.curve(lambda t: sin(radians(t)), color="ink", width=1.6, x0=0, x1=360)
    g.curve(lambda t: cos(radians(t)), color="ink", width=1.6, x0=0, x1=360)
    for v, dx in ((90, -12), (180, -12), (270, 13)):
        g.items.append(f'<rect x="{g.X(v) + dx - 15:.1f}" y="{g.Y(0) + 6:.1f}" width="30" height="13" fill="#fff"/>')
        g.label(v, 0, f"{v}°", dx=dx, dy=13, size=11)
    g.items.append(f'<rect x="{g.X(360) - 12:.1f}" y="{g.Y(0.15) - 7:.1f}" width="30" height="13" fill="#fff"/>')
    g.label(360, 0.15, "360°", dx=3, size=11)
    for v, s in ((1, "1"), (0, "0"), (-1, "-1")):
        g.items.append(f'<rect x="{g.X(-40) + 4:.1f}" y="{g.Y(v) - 7:.1f}" width="16" height="13" fill="#fff"/>')
        g.label(-40, v, s, dx=12, size=11)
    g.items.append(f'<rect x="{g.X(110):.1f}" y="{g.Y(1.18) - 7:.1f}" width="60" height="13" fill="#fff"/>')
    g.label(140, 1.18, "y = sin x", size=11, italic=True)
    g.items.append(f'<rect x="{g.X(290):.1f}" y="{g.Y(1.18) - 7:.1f}" width="60" height="13" fill="#fff"/>')
    g.label(320, 1.18, "y = cos x", size=11, italic=True)
    save("hw_5d8", g)

    # NBCS 2022 Section I Q13: interval OP with P(4, 5)
    f = Fig(240, 150)
    cx, cy = 70, 108
    f.arrow(cx - 60, cy, cx + 150, cy, width=1.2, head=6).arrow(cx, cy + 36, cx, cy - 98, width=1.2, head=6)
    f.text(cx + 156, cy + 4, "x", size=11.5, italic=True).text(cx - 8, cy - 94, "y", size=11.5, italic=True)
    P = (cx + 4 * 17, cy - 5 * 17)
    f.line(cx, cy, cx + 1.45 * (P[0] - cx), cy + 1.45 * (P[1] - cy), width=1.4)
    f.dot(*P, 2.4).text(P[0] + 6, P[1] + 2, "P(4, 5)", size=11, anchor="start")
    f.arrow(*pt(cx, cy, 8, 20), *pt(cx, cy, 46, 20), width=1.1, head=5)
    f.text(cx + 30, cy - 12, "θ", size=11.5, italic=True)
    f.text(cx - 8, cy + 13, "O", size=11.5, italic=True)
    f.text(cx + 128, cy - 40, "NOT TO SCALE", size=10.5)
    save("pp_nbcs22_13", f)

    # Girraween 2023 MC Q3: line k through (2, 0) and (0, -4), angle at the x-intercept
    f = Fig(330, 170)
    cx, cy, u = 70, 96, 17
    f.arrow(cx - 50, cy, cx + 210, cy, width=1.2, head=6).arrow(cx, cy + 60, cx, cy - 86, width=1.2, head=6)
    f.text(cx + 216, cy + 4, "x", size=11.5, italic=True).text(cx - 8, cy - 82, "y", size=11.5, italic=True)
    X2 = (cx + 2 * u, cy)
    v = 15
    f.line(cx - 0.3 * u, cy + 4.6 * v, cx + 4.6 * u, cy - 5.2 * v, width=1.4)
    f.text(cx + 4.6 * u + 6, cy - 5.2 * v - 2, "k", size=11.5, italic=True)
    f.line(cx - 4, cy + 4 * v, cx + 4, cy + 4 * v, width=1.1)
    f.arc(X2[0], X2[1], 14, 0, 58, color="ink", width=1.1)
    f.text(X2[0] - 6, cy + 14, "2", size=11).text(cx - 14, cy + 4 * v + 4, "−4", size=11)
    f.text(X2[0] + 24, cy - 12, "Ø", size=11.5)
    f.text(cx + 160, cy - 50, "DIAGRAM NOT TO SCALE", size=10)
    save("pp_gir23_3", f)

    # Sydney Boys 2021 Part C (f): ray OP through P(-3, 4), OP = 5
    f = Fig(190, 150)
    cx, cy = 120, 92
    f.arrow(cx - 100, cy, cx + 60, cy, width=1.2, head=6).arrow(cx, cy + 50, cx, cy - 86, width=1.2, head=6)
    f.text(cx + 66, cy + 4, "x", size=11.5, italic=True).text(cx - 8, cy - 82, "y", size=11.5, italic=True)
    P = (cx - 3 * 14, cy - 4 * 14)
    f.arrow(cx, cy, cx - 3 * 20, cy - 4 * 20, width=1.4, head=6)
    f.dot(*P, 2.4).text(P[0] - 6, P[1] + 2, "P(−3, 4)", size=10.5, anchor="end")
    f.text((cx + P[0]) / 2 - 8, (cy + P[1]) / 2 - 2, "5", size=10.5)
    f.arc(cx, cy, 14, 0, 126.87, color="ink", width=1.1)
    f.text(cx + 12, cy - 18, "θ", size=11.5, italic=True)
    f.text(cx - 9, cy + 13, "O", size=11.5, italic=True)
    save("pp_sbhs21_f", f)

    # Sydney Boys 2020 Q8: the graph y = sin(-x)
    g = Graph(-200, 400, -2, 2, w=560, h=200, pad=(20, 24, 16, 14))
    for v in (-180, -90, 90, 180, 270, 360):
        g.vline(v, -2, 2, color="faint", dash=None, width=0.8)
    for v in (-2, -1, 1, 2):
        g.hline(v, color="faint", dash=None, width=0.8)
    g.axes("x", "y")
    g.curve(lambda t: -sin(radians(t)), color="ink", width=1.8, x0=-198, x1=398)
    for v in (-180, -90, 90, 180, 270, 360):
        g.items.append(f'<rect x="{g.X(v) + 3:.1f}" y="{g.Y(0) + 4:.1f}" width="28" height="13" fill="#fff"/>')
        g.label(v, 0, str(v).replace("-", "−"), dx=17, dy=11, size=10.5)
    for v in (-2, -1, 1, 2):
        g.label(0, v, str(v), dx=-6, anchor="end", size=10.5)
    save("pp_sbhs20_8", g)


class _S:
    def __init__(self, s):
        self.s = s

    def svg(self):
        return self.s


def fig_t1_ans():
    from plots import quadrant
    for name, a, lab in (("a_mpg1a", -90, "−90°"), ("a_mpg1b", -30, "−30°"), ("a_mpg1c", 375, "375°"),
                         ("a_mpg1d", -195, "−195°"), ("a_mpg1e", 430, "430°"), ("a_mpg1f", 720, "720°")):
        save(name, _S(quadrant(a, lab, w=130, h=110)))
    f = Fig(160, 140)
    cx, cy = 80, 70
    f.line(cx - 64, cy, cx + 64, cy, width=1.3).line(cx, cy - 62, cx, cy + 62, width=1.3)
    ray(f, cx, cy, 120, 62, color="blue", width=1.8)
    x, y = pt(cx, cy, 120, 72)
    f.text(x - 4, y, "480°", size=11)
    f.arc(cx, cy, 18, 120, 180, color="faint")
    x, y = pt(cx, cy, 150, 36)
    f.text(x, y + 4, "60°", size=10.5)
    save("a_sgs480", f)
    # North Sydney Girls 2022 Q16(c): y = tan x for 0 <= x <= 180
    g = Graph(0, 190, -3, 3, w=260, h=170, pad=(22, 26, 14, 14))
    g.axes("x", "y")
    g.xticks([(45, ""), (135, ""), (180, "180°")])
    g.vline(90)
    g.curve(lambda t: tan(radians(t)), color="blue", width=2, x0=0, x1=88)
    g.curve(lambda t: tan(radians(t)), color="blue", width=2, x0=92, x1=180)
    g.label(90, 0, "90°", dx=4, dy=-12, anchor="start", size=10.5)
    g.dot(45, 1, r=2.4).dot(135, -1, r=2.4)
    g.label(45, 1, "(45°, 1)", dx=-6, dy=-8, anchor="end", size=10.5)
    g.label(135, -1, "(135°, −1)", dx=6, dy=10, anchor="start", size=10.5)
    save("a_nsg_tan", g)
    # Sydney Grammar 2020 Q6(c)(i): y = cos theta for 0 <= theta <= 360
    g = Graph(0, 380, -1.3, 1.3, w=300, h=130, pad=(22, 26, 14, 14))
    g.axes("θ", "y")
    g.xticks([(90, "90°"), (180, ""), (270, "270°"), (360, "")])
    g.label(180, 0, "180°", dy=-12, size=11).label(360, 0, "360°", dy=-12, size=11)
    g.yticks([(1, "1"), (-1, "-1")])
    g.curve(lambda t: cos(radians(t)), color="blue", width=2, x0=0, x1=360)
    save("a_sgs_cos", g)
    # Maths Pathway Graphs Q9(b): sin, cos, tan for -180 <= theta <= 180
    for name, fn, lab in (("a_mpg9s", lambda t: sin(radians(t)), "y = sin θ"), ("a_mpg9c", lambda t: cos(radians(t)), "y = cos θ"),
                          ("a_mpg9t", lambda t: tan(radians(t)), "y = tan θ")):
        g = Graph(-200, 200, -1.5, 1.5, w=230, h=130, pad=(10, 24, 14, 14))
        g.axes("θ", "")
        g.xticks([(-180, ""), (-90, ""), (90, ""), (180, "")])
        g.label(-180, 0, "−180°", dy=-12 if name == "a_mpg9s" else 13, size=10)
        g.label(180, 0, "180°", dy=-12 if name == "a_mpg9t" else 13, size=10)
        g.yticks([(1, ""), (0.5, ""), (-0.5, ""), (-1, "")])
        if name == "a_mpg9t":
            for k in (-1, 0, 1):
                g.curve(fn, color="blue", width=2, x0=max(-180, k * 180 - 56), x1=min(180, k * 180 + 56))
            g.vline(-90).vline(90)
        else:
            g.curve(fn, color="blue", width=2, x0=-180, x1=180)
        if name == "a_mpg9t":
            g.label(-90, 0, "−90°", dx=-4, dy=-12, anchor="end", size=10).label(90, 0, "90°", dx=4, dy=-12, anchor="start", size=10)
            g.label(200, 1.45, lab, anchor="end", size=11, color="blue")
        else:
            g.label(-90, 0, "−90°", dy=13 if name != "a_mpg9s" else -12, size=10)
            g.label(90, 0, "90°", dy=-12 if name != "a_mpg9c" else 13, size=10)
            g.label(0, 1.5, lab, dx=6, dy=0, anchor="start", size=11, color="blue")
        g.label(0, 1, "1", dx=-5, dy=-6 if name == "a_mpg9c" else 0, anchor="end", size=10)
        g.label(0, -1, "−1", dx=5, anchor="start", size=10)
        save(name, g)


# ---------------- Lesson T2: exact values and trigonometric equations ----------------

def qrays(name, rays, arcs=(), w=190, h=150, labs=()):
    """Quadrant diagram (book style): axes, rays at given angles with end labels, related-angle arcs."""
    f = Fig(w, h)
    cx, cy = w / 2, h / 2
    f.line(cx - 72, cy, cx + 72, cy, width=1.3).line(cx, cy - 64, cx, cy + 64, width=1.3)
    for a, lab in rays:
        ray(f, cx, cy, a, 60, width=1.6, head=7)
        if lab:
            x, y = pt(cx, cy, a, 72)
            f.text(x, y + 4, lab, size=10.5)
    for lo, hi, s in arcs:
        f.arc(cx, cy, 20, lo, hi, color="faint")
        axis_end = lo if lo % 90 == 0 else hi
        m = 0.65 * axis_end + 0.35 * (hi if axis_end == lo else lo)
        x, y = pt(cx, cy, m, 46)
        f.text(x, y + (3.5 if m % 360 < 180 else 3), s, size=9.5)
    for x, y, s in labs:
        f.text(x, y, s, size=11)
    save(name, f)


def fig_t2():
    # 5A p150: half a square (ABC) and half an equilateral triangle (PQR)
    f = Fig(400, 150)
    C, B, A = (30, 126), (130, 126), (130, 26)
    f.poly([(30, 26), (130, 26), B, C], color=None, opacity=0, width=1.0, stroke="faint")
    f.items[-1] = f.items[-1].replace('stroke-width="1.0"', 'stroke-width="1.0" stroke-dasharray="4 3"')
    triangle(f, C, B, A)
    right_mark(f, B, C, A, 8)
    f.text(A[0] + 8, A[1] - 2, "A", size=11.5, italic=True).text(B[0] + 9, B[1] + 6, "B", size=11.5, italic=True)
    f.text(C[0] - 9, C[1] + 6, "C", size=11.5, italic=True)
    side_label(f, C, A, "√2", 11)
    side_label(f, B, A, "1", 9, flip=True)
    side_label(f, C, B, "1", 11, flip=True)
    angle_arc(f, C, B, A, 16)
    angle_label(f, C, B, A, "45°", 32, size=10.5)
    angle_arc(f, A, C, B, 16)
    angle_label(f, A, C, B, "45°", 40, size=10.5)
    P, Q, R = (300, 14), (300, 126), (364.7, 126)
    S = (235.3, 126)
    f.line(*S, *P, width=1.5).line(*S, *R, width=1.5).line(*P, *R, width=1.5)
    f.line(*P, *Q, width=1.2, dash="4 3")
    right_mark(f, Q, R, P, 8)
    f.text(P[0], P[1] - 8, "P", size=11.5, italic=True).text(Q[0], Q[1] + 15, "Q", size=11.5, italic=True)
    f.text(R[0] + 9, R[1] + 6, "R", size=11.5, italic=True)
    side_label(f, Q, P, "√3", 12)
    side_label(f, P, R, "2", 10, flip=True)
    side_label(f, Q, R, "1", 11, flip=True)
    angle_arc(f, P, Q, R, 18)
    f.text(P[0] + 12, P[1] + 4, "30°", size=10, anchor="start")
    angle_arc(f, R, P, Q, 16)
    angle_label(f, R, P, Q, "60°", 30, size=10.5)
    save("t2_special", f)

    # 5G p182: complementary angles, acute proof triangle
    f = Fig(230, 124)
    A, B, C = (20, 106), (180, 106), (180, 32)
    triangle(f, A, B, C)
    right_mark(f, B, A, C, 8)
    angle_arc(f, A, B, C, 22)
    angle_label(f, A, B, C, "θ", 34, italic=True)
    angle_arc(f, C, A, B, 16)
    f.text(C[0] - 28, C[1] - 12, "90° − θ", size=10.5)
    side_label(f, A, C, "c", 10, italic=True)
    side_label(f, B, C, "a", 10, italic=True, flip=False)
    side_label(f, A, B, "b", 12, italic=True, flip=True)
    save("t2_comp", f)

    # 5G p183: reflection of P(x, y) in y = x gives P'(y, x) at 90 - theta
    f = Fig(230, 210)
    cx, cy, R = 104, 96, 56
    f.circle(cx, cy, R)
    f.arrow(cx - R - 22, cy, cx + R + 26, cy, width=1.3, head=6).arrow(cx, cy + R + 20, cx, cy - R - 24, width=1.3, head=6)
    f.text(cx + R + 30, cy - 6, "x", size=11.5, italic=True).text(cx - 9, cy - R - 20, "y", size=11.5, italic=True)
    f.line(cx - 76, cy + 76, cx + 76, cy - 76, color="faint", width=1.2, dash="4 3")
    f.text(cx + 82, cy - 78, "y = x", size=10.5, italic=True)
    th = 122
    P = pt(cx, cy, th, R)
    Pp = pt(cx, cy, 90 - th, R)
    ray(f, cx, cy, th, R + 20, width=1.5, head=6)
    ray(f, cx, cy, 90 - th, R + 20, width=1.5, head=6)
    f.dot(*P, 2.6).dot(*Pp, 2.6)
    f.text(P[0] - 8, P[1] + 2, "P(x, y)", size=10.5, anchor="end", italic=True)
    f.text(Pp[0] + 4, Pp[1] + 16, "P′(y, x)", size=10.5, anchor="start", italic=True)
    e = pt(cx, cy, th, R + 30)
    f.text(e[0], e[1] + 4, "θ", size=11.5, italic=True)
    e = pt(cx, cy, 90 - th, R + 28)
    f.text(e[0] + 4, e[1] + 30, "90° − θ", size=10.5, anchor="start")
    f.text(cx - 16, cy - 7, "O", size=11, italic=True)
    save("t2_reflect", f)

    # 5F Example 11: sin theta = 1/5, rays in quadrants 1 and 2
    f = Fig(220, 170)
    cx, cy, R = 110, 104, 60
    f.circle(cx, cy, R)
    f.arrow(cx - R - 22, cy, cx + R + 22, cy, width=1.3, head=6).arrow(cx, cy + R + 10, cx, cy - R - 26, width=1.3, head=6)
    f.text(cx + R + 28, cy + 4, "x", size=11.5, italic=True).text(cx - 9, cy - R - 22, "y", size=11.5, italic=True)
    a = degrees(atan2(1, sqrt(24)))
    for ang, xl, sg in ((a, "2√6", 1), (180 - a, "−2√6", -1)):
        P = pt(cx, cy, ang * 4.2 if False else ang, R)
        # draw with the true height 1/5 of r scaled up so the triangle is visible
        P = (cx + sg * R * 0.85, cy - R * 0.53)
        f.line(cx, cy, *P, width=1.5)
        ray(f, cx, cy, degrees(atan2(cy - P[1], (P[0] - cx))), R + 22, width=1.5, head=6)
        M = (P[0], cy)
        f.line(*P, *M, width=1.2)
        right_mark(f, M, (cx, cy), P, 7)
        f.dot(*P, 2.6)
        f.text(P[0] - sg * 4, P[1] + 15, "1", size=11, anchor="end" if sg > 0 else "start")
        f.text((cx + P[0]) / 2 - sg * 5, (cy + P[1]) / 2 - 9, "5", size=11)
        f.text(M[0] - sg * 4, cy + 14, xl, size=10.5, anchor="end" if sg > 0 else "start")
        e = pt(cx, cy, degrees(atan2(cy - P[1], (P[0] - cx))), R + 32)
        f.text(e[0], e[1] + 4, "θ", size=11.5, italic=True)
    save("t2_ex11", f)

    # 5F Q1 a-d (book p193)
    def circ(name, X, Y, lab_r, lab_x, lab_y, theta_side=1):
        f = Fig(150, 140)
        cx, cy, R = 72, 70, 44
        f.circle(cx, cy, R)
        f.line(cx - R - 18, cy, cx + R + 18, cy, width=1.2).line(cx, cy - R - 18, cx, cy + R + 18, width=1.2)
        a = degrees(atan2(Y, X))
        P = pt(cx, cy, a, R)
        M = (P[0], cy)
        ray(f, cx, cy, a, R + 18, width=1.5, head=6)
        f.line(*P, *M, width=1.2)
        right_mark(f, M, (cx, cy), P, 6)
        e = pt(cx, cy, a, R + 28)
        f.text(e[0], e[1] + 4, "θ", size=11.5, italic=True)
        mx, my = (cx + P[0]) / 2, (cy + P[1]) / 2
        nx, ny = -(P[1] - cy), (P[0] - cx)
        nn = hypot(nx, ny)
        nx, ny = nx / nn, ny / nn
        if nx * (M[0] - mx) + ny * (M[1] - my) > 0:
            nx, ny = -nx, -ny
        if Y > 0:
            f.text(cx + (-6 if X > 0 else 6), my + 4, lab_r, size=10.5, anchor="end" if X > 0 else "start")
        else:
            f.text(mx + 11 * nx, my + 11 * ny + 4, lab_r, size=10.5)
        f.text(P[0] + (8 if X > 0 else -8), (P[1] + cy) / 2 + 4, lab_y, size=10.5, anchor="start" if X > 0 else "end")
        f.text((cx + M[0]) / 2, cy + (13 if Y > 0 else -6), lab_x, size=10.5)
        save(name, f)

    circ("t2_f1a", 8, 15, "17", "8", "15")
    circ("t2_f1b", -6, 8, "10", "−6", "8")
    circ("t2_f1c", -24, -7, "25", "−24", "−7")
    circ("t2_f1d", 20, -21, "29", "20", "−21")

    # 5H Example 15: y = sin x for 0 <= x <= 720
    g = Graph(-30, 800, -1.3, 1.3, w=310, h=130, pad=(14, 24, 16, 14))
    g.axes("x", "y")
    g.yticks([(1, "1"), (-1, "-1")])
    g.curve(lambda t: sin(radians(t)), color="blue", width=2, x0=-20, x1=740)
    for v in (270, 630):
        g.vline(v, -1, 0)
    g.hline(-1, x0=0, x1=630)
    g.xticks([(270, ""), (360, ""), (630, ""), (720, "")])
    g.label(270, 0, "270°", dx=0, dy=-11, size=10).label(630, 0, "630°", dx=-3, dy=-11, anchor="end", size=10)
    g.label(360, 0, "360°", dx=4, dy=13, anchor="start", size=10).label(720, 0, "720°", dx=4, dy=13, anchor="start", size=10)
    save("t2_ex15", g)

    qrays("t2_ex16", [(210, "−150°"), (330, "−30°")], [(180, 210, "30°"), (330, 360, "30°")])
    qrays("t2_ex17", [(108.43, "108°"), (288.43, "288°")], [(108.43, 180, "72°"), (288.43, 360, "72°")])
    qrays("t2_ex19", [(60, "60°, 420°"), (240, "240°, 600°")], [(0, 60, "60°"), (180, 240, "60°")], w=230)
    qrays("t2_ex20", [(60, "60°"), (120, "−240°")], [(0, 60, "60°"), (120, 180, "60°")])

    # Maths Pathway: sin x = 1/2 on the unit circle, solutions 30 and 150
    f = Fig(190, 160)
    cx, cy, R = 95, 80, 56
    f.circle(cx, cy, R)
    axes(f, cx, cy, R, ext=12)
    unit_ticks(f, cx, cy, R)
    for a, dash in ((30, None), (150, "3 2")):
        f.line(cx, cy, *pt(cx, cy, a, R), color="blue", width=1.6, dash=dash)
    f.line(*pt(cx, cy, 150, R), *pt(cx, cy, 30, R), color="faint", width=1.0, dash="3 2")
    f.arc(cx, cy, 16, 0, 30, color="blue")
    f.text(cx + 34, cy - 8, "30°", size=10, color="blue")
    save("t2_mp", f)

    # 5I Example 22 (book p193) and the two demo triangles (our own), drawn with their true angles:
    # base CB horizontal, angle b at B (right end), obtuse angle c at C (left end of base), x = CA opposite b
    def obtuse(name, b, c, k, w=240, CB=110.0, rb=44, rc=30):
        sb, cb_ = sin(radians(b)), cos(radians(b))
        sc, cc = sin(radians(c)), cos(radians(c))
        s_ = CB / (cb_ + sb * cc / sc)
        t_ = s_ * sb / sc
        Ax, Ay = t_ * cc, -t_ * sc
        x0 = 24 - min(Ax, 0)
        y0 = 24 - Ay
        C, B, A = (x0, y0), (x0 + CB, y0), (x0 + Ax, y0 + Ay)
        f = Fig(max(w, int(B[0] + 30)), int(y0 + 30))
        triangle(f, A, B, C)
        angle_arc(f, B, A, C, 26)
        if rb:
            angle_label(f, B, A, C, f"{b}°", rb, size=10.5)
        else:
            f.text(B[0] + 6, B[1] - 6, f"{b}°", size=10.5, anchor="start")
        angle_arc(f, C, B, A, 12)
        angle_label(f, C, B, A, f"{c}°", rc, size=10.5)
        side_label(f, A, B, k, 11)
        side_label(f, A, C, "x", 10, italic=True, flip=True)
        save(name, f)

    obtuse("t2_ex22", 30, 135, "12")
    obtuse("t2_d1", 45, 120, "8", CB=60.0, rb=None, rc=24)
    obtuse("t2_y1", 30, 120, "6")

    # NBCS 2022 Section I Q16: flagpole
    f = Fig(250, 150)
    P, T, A = (60, 100), (60, 14), (220, 134)
    f.line(*P, *T, width=1.5).line(*T, *A, width=1.5).line(*P, *A, width=1.5)
    right_mark(f, P, T, A, 8)
    f.dot(*P, 2.4).dot(*A, 2.4)
    f.text(P[0] - 9, P[1] + 4, "P", size=11.5, italic=True).text(A[0] + 9, A[1] + 4, "A", size=11.5, italic=True)
    f.text(P[0] - 10, (P[1] + T[1]) / 2, "h", size=11.5, italic=True)
    side_label(f, P, A, "30 m", 12, flip=True)
    angle_arc(f, A, P, T, 22)
    angle_label(f, A, P, T, "30°", 58, size=10.5)
    f.text(180, 40, "NOT TO SCALE", size=10.5)
    save("pp_nbcs22_16", f)

    # Sydney Boys 2024 Part C Q6: clock face with the hour hand at x degrees
    f = Fig(180, 160)
    cx, cy, R = 90, 76, 52
    f.path(f"M{cx - R - 14},{cy + R + 22} L{cx - R - 14},{cy} A{R + 14},{R + 14} 0 0 1 {cx + R + 14},{cy} L{cx + R + 14},{cy + R + 22} Z",
           color="ink", width=1.4, fill="faint", opacity=0.25)
    f.circle(cx, cy, R, fill="none")
    f.raw(f'<path d="M{cx - R},{cy} A{R},{R} 0 1 0 {cx + R},{cy} A{R},{R} 0 1 0 {cx - R},{cy} Z" fill="#fff" stroke="none"/>')
    f.circle(cx, cy, R)
    for s, (dx, dy) in (("12", (0, -R + 12)), ("3", (R - 10, 4)), ("6", (0, R - 6)), ("9", (-R + 10, 4))):
        f.text(cx + dx, cy + dy, s, size=10.5)
    f.line(cx, cy, cx, cy - R + 20, color="faint", width=1.1, dash="3 2")
    hx, hy = pt(cx, cy, 90 - 70, 36)
    f.line(cx, cy, hx, hy, width=2.6)
    f.dot(cx, cy, 2.6)
    f.arc(cx, cy, 16, 90, 20, color="ink", width=1.0)
    f.text(cx + 10, cy - 22, "x°", size=10.5, italic=True)
    save("pp_sbhs24_6", f)


if __name__ == "__main__":
    fig_rev()
    fig_t1()
    fig_t1_hw()
    fig_t1_ans()
    fig_t2()
    import figs_t3  # Lesson T3 figures (module imports Fig and save from this file)
    figs_t3.fig_t3()
    figs_t3.fig_t3_pp()
