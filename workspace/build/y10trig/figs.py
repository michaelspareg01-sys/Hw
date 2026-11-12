"""Figures for the Year 10 Trigonometry (part 2) pack: python3 figs.py  ->  svg/*.svg

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
        f = ACC[fill] if fill != "none" else "none"
        self.items.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{f}" fill-opacity="{opacity}" stroke="{ACC[color]}" stroke-width="{width}"/>')
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


if __name__ == "__main__":
    fig_rev()
