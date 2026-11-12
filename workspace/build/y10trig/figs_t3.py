"""Figures for Lesson T3 (the ambiguous case) of the Year 10 Trigonometry (part 2) pack.

python3 figs_t3.py  ->  svg/t3_*.svg, svg/pp3_*.svg

Every triangle is drawn from its true geometry (solved from the given data), then turned or flipped
to match the layout of the source diagram (Year 11 Advanced book 5I/5J or the past paper), with the
same labels. tri() scales each figure to fit its box.
"""
import os
import sys
from math import sin, cos, tan, asin, atan2, sqrt, radians, degrees, hypot, pi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figs import Fig, save, right_mark, ACC  # noqa: E402

R = radians


def aa(L, a, b):
    """Base PQ of length L on the x-axis, angle a at P and b at Q (degrees); third vertex R above."""
    t = L * sin(R(b)) / sin(R(a + b))
    return {"P": (0.0, 0.0), "Q": (L, 0.0), "R": (t * cos(R(a)), t * sin(R(a)))}


def sas(c, b, A):
    """P at the origin, PQ = c along the x-axis, PR = b at angle A above it."""
    return {"P": (0.0, 0.0), "Q": (c, 0.0), "R": (b * cos(R(A)), b * sin(R(A)))}


def transform(pts, rot=0.0, flipx=False, flipy=False):
    out = {}
    for k, (x, y) in pts.items():
        if flipx:
            x = -x
        if flipy:
            y = -y
        c, s = cos(R(rot)), sin(R(rot))
        out[k] = (x * c - y * s, x * s + y * c)
    return out


def tri(name, pts, poly=("P", "Q", "R"), sides=(), angles=(), names=(), rights=(), extra=None,
        rot=0.0, flipx=False, flipy=False, maxw=250, maxh=160, pad=26, size=11, keep=None, dashed=()):
    """Draw a figure. pts: math coordinates (y up). sides: (U, V, label, flip, off). angles: (V, label,
    rr or None, arc r). names: (V, label, dx, dy). rights: (V, U, W). extra(f, S) draws more in screen
    coordinates S[vertex]."""
    pts = transform(pts, rot, flipx, flipy)
    use = keep or list(pts)
    xs = [pts[k][0] for k in use]
    ys = [pts[k][1] for k in use]
    sc = min((maxw - 2 * pad) / (max(xs) - min(xs) or 1), (maxh - 2 * pad) / (max(ys) - min(ys) or 1))
    S = {k: (pad + (x - min(xs)) * sc, pad + (max(ys) - y) * sc) for k, (x, y) in pts.items()}
    W = pad * 2 + (max(xs) - min(xs)) * sc
    H = pad * 2 + (max(ys) - min(ys)) * sc
    f = Fig(int(W + 1), int(H + 1))
    if poly:
        f.poly([S[k] for k in poly], color=None, opacity=0, width=1.5)
    for a, b in dashed:
        f.line(*S[a], *S[b], width=1.2, dash="4 3")
    cx = sum(S[k][0] for k in poly) / len(poly) if poly else W / 2
    cy = sum(S[k][1] for k in poly) / len(poly) if poly else H / 2
    for (u, v, lab, *opt) in sides:
        off = opt[1] if len(opt) > 1 else 6 + 2.9 * len(lab)
        mx, my = (S[u][0] + S[v][0]) / 2, (S[u][1] + S[v][1]) / 2
        dx, dy = S[v][0] - S[u][0], S[v][1] - S[u][1]
        n = hypot(dx, dy)
        nx, ny = dy / n, -dx / n
        if (mx + nx - cx) ** 2 + (my + ny - cy) ** 2 < (mx - cx) ** 2 + (my - cy) ** 2:
            nx, ny = -nx, -ny
        if opt and opt[0]:
            nx, ny = -nx, -ny
        f.text(mx + off * nx, my + off * ny + 3.5, lab, size=size, italic=(lab in ("x", "a", "b", "c", "θ", "h")))
    for (v, lab, *opt) in angles:
        others = opt[2] if len(opt) >= 3 and opt[2] else [k for k in poly if k != v][:2]
        V = S[v]
        a1 = atan2(-(S[others[0]][1] - V[1]), S[others[0]][0] - V[0])
        a2 = atan2(-(S[others[1]][1] - V[1]), S[others[1]][0] - V[0])
        d = (a2 - a1 + 3 * pi) % (2 * pi) - pi
        half = abs(d) / 2
        r = opt[1] if len(opt) > 1 and opt[1] else 13
        f.arc(V[0], V[1], r, degrees(a1), degrees(a1 + d))
        rr = opt[0] if opt and opt[0] else max(r + 12, min(56, (4 + 3 * len(lab)) / max(sin(half), 0.1) + 4))
        m = a1 + d / 2
        ndx, ndy = (opt[3], opt[4]) if len(opt) > 4 else (0, 0)
        f.text(V[0] + rr * cos(m) + ndx, V[1] - rr * sin(m) + 3.5 + ndy, lab, size=size - 0.5, italic=(lab == "θ"))
    for (v, u, w) in rights:
        right_mark(f, S[v], S[u], S[w], 7)
    for (v, lab, dx, dy) in names:
        f.text(S[v][0] + dx, S[v][1] + dy, lab, size=size + 0.5, italic=True)
    if extra:
        extra(f, S)
    save(name, f)
    return S


def fig_t3():
    # ---------- book examples (5I, PDF 208-210) ----------
    p = sas(4, 3, 135)
    tri("t3_ex23", p, sides=[("P", "R", "3"), ("P", "Q", "4")], angles=[("P", "135°", -18, 13, None, -4, 0)], rot=-15)
    p = sas(24, 7, 67)
    tri("t3_ex24", p, sides=[("P", "R", "x"), ("P", "Q", "24 m")], angles=[("P", "67°", 24)], maxh=90)
    p = sas(12, 13, 50 + 17 / 60)
    tri("t3_ex25", p, sides=[("P", "R", "13 cm"), ("P", "Q", "12 cm")], angles=[("P", "θ", 24)])
    p = aa(1, 45, 60)
    tri("t3_ex26", p, sides=[("P", "R", "7√6"), ("Q", "R", "14")], angles=[("P", "45°", 24), ("Q", "θ", 22)])
    # construction: base ray from P, arc of radius 14 about R cuts it twice (60 and 120 degrees)
    L = 7 * sqrt(6)
    P0 = (0.0, 0.0)
    Rv = (L * cos(R(45)), L * sin(R(45)))
    q1 = (Rv[0] + 14 * cos(R(-60)), 0.0)
    q2 = (Rv[0] - 14 * cos(R(60)), 0.0)
    pts = {"P": P0, "R": Rv, "Q1": q1, "Q2": q2, "E": (q1[0] + 4, 0.0)}

    def con(f, S):
        f.line(*S["P"], *S["E"], width=1.4)
        f.line(*S["P"], *S["R"], width=1.4)
        f.line(*S["R"], *S["Q1"], width=1.3, dash="4 3")
        f.line(*S["R"], *S["Q2"], width=1.3, dash="4 3")
        rr = hypot(S["R"][0] - S["Q1"][0], S["R"][1] - S["Q1"][1])
        f.arc(S["R"][0], S["R"][1], rr, -48, -132, color="faint", width=1.0)
        f.arc(S["P"][0], S["P"][1], 16, 0, 45)
        f.text(S["P"][0] - 4, S["P"][1] - 16, "45°", size=10, anchor="end")
        f.text(S["Q1"][0] - 24, S["Q1"][1] - 8, "60°", size=10)
        f.text(S["Q2"][0] + 2, S["Q2"][1] + 16, "120°", size=10)
        f.text((S["P"][0] + S["R"][0]) / 2 - 16, (S["P"][1] + S["R"][1]) / 2 - 4, "7√6", size=10.5)
        f.text((S["R"][0] + S["Q1"][0]) / 2 + 13, (S["R"][1] + S["Q1"][1]) / 2, "14", size=10.5)
    tri("t3_ex26c", pts, poly=None, extra=con, maxw=200, maxh=120)
    p = aa(1, 80, 34 + 15 / 60)
    tri("t3_ex27", p, sides=[("P", "R", "4"), ("Q", "R", "7")], angles=[("P", "80°", 22), ("Q", "θ", 24)])

    # ---------- Exercise 5I Q1 (PDF 210) ----------
    tri("t3_q1a", aa(1, 60, 50), sides=[("P", "Q", "10"), ("P", "R", "x")], angles=[("Q", "50°"), ("R", "70°")], maxw=175, maxh=135)
    tri("t3_q1b", aa(1, 40, 30), sides=[("P", "Q", "x"), ("Q", "R", "3")], angles=[("P", "40°", 34), ("R", "110°", -16, 12, None, 0, 0)], maxw=175, maxh=120)
    tri("t3_q1c", aa(1, 85, 40), flipy=True, sides=[("P", "Q", "4"), ("Q", "R", "x")], angles=[("P", "85°", 22), ("R", "55°")], maxw=175, maxh=135)
    tri("t3_q1d", aa(1, 75, 40), flipy=True, sides=[("P", "Q", "x"), ("Q", "R", "2")], angles=[("P", "75°", 22), ("R", "65°")], maxw=175, maxh=125)
    tri("t3_q1e", aa(1, 71, 46), sides=[("P", "R", "7"), ("R", "Q", "x")], angles=[("P", "71°", 22), ("Q", "46°")], maxw=175, maxh=135)
    tri("t3_q1f", aa(1, 38, 24), flipy=True, sides=[("P", "Q", "5"), ("Q", "R", "x")], angles=[("P", "38°", 34, 13, None, 0, 0), ("R", "118°", -18, 12, None, 0, 0)], maxw=175, maxh=120)
    # Q2
    tri("t3_q2a", aa(1, 70, 50), sides=[("P", "R", "12"), ("Q", "R", "a")], angles=[("P", "70°", 22), ("R", "60°", 22)], maxw=175, maxh=135)
    tri("t3_q2b", aa(1, 80, 75), rot=-40, sides=[("P", "Q", "20"), ("Q", "R", "b")], angles=[("R", "25°", -16, 13, None, 0, 0), ("Q", "75°", 26, 12, None, 3, 0)], maxw=150, maxh=130)
    tri("t3_q2c", aa(1, 48, 20), flipy=True, sides=[("P", "Q", "15"), ("P", "R", "c")], angles=[("P", "48°", 34, 13, None, 0, 0), ("R", "112°", -18, 12, None, 0, 0)], maxw=175, maxh=120)
    # Q3 (drawn with the acute answer)
    tri("t3_q3a", aa(1, 48.74, 61.26), sides=[("P", "Q", "5"), ("Q", "R", "4")], angles=[("P", "θ", 22), ("R", "70°", 22)], maxw=175, maxh=135)
    tri("t3_q3b", aa(1, 42.16, 52.84), flipy=True, sides=[("P", "Q", "10"), ("P", "R", "8")], angles=[("Q", "θ", 22), ("R", "85°", 22)], maxw=175, maxh=125)
    tri("t3_q3c", aa(1, 37.02, 42.98), sides=[("P", "R", "9"), ("P", "Q", "13")], angles=[("R", "100°", 22), ("Q", "θ", 24)], maxw=175, maxh=120)
    tri("t3_q3d", aa(1, 72, 19.61), flipy=True, rot=35, sides=[("P", "R", "6"), ("R", "Q", "17")], angles=[("P", "72°", 22), ("Q", "θ", 44, 14)], maxw=175, maxh=135)
    tri("t3_q3e", aa(1, 27.08, 28.92), flipy=True, sides=[("P", "Q", "12"), ("P", "R", "7")], angles=[("R", "124°", 22), ("Q", "θ", 28)], maxw=175, maxh=120)
    tri("t3_q3f", aa(1, 53, 84.74), rot=37, sides=[("R", "Q", "19"), ("Q", "P", "16")], angles=[("P", "53°", 26, 13, None, 3, 0), ("R", "θ", 26)], maxw=130, maxh=130)
    # Q4
    tri("t3_q4a", sas(4, 3, 50), sides=[("P", "R", "3 cm"), ("P", "Q", "4 cm")], angles=[("P", "50°", 22)], maxw=175, maxh=125)
    p = sas(8, 5, 70)
    tri("t3_q4b", p, rot=-(180 - 70) / 2 - 90 + 180 - 70 + 35 - 35 + 0, sides=[("P", "R", "5 cm"), ("P", "Q", "8 cm")], angles=[("P", "70°", 22)], maxw=175, maxh=135)
    tri("t3_q4c", sas(7, 7, 115), rot=180 + 32.5, sides=[("P", "R", "7 cm"), ("P", "Q", "7 cm")], angles=[("P", "115°", 22)], maxw=175, maxh=110)
    # Q8: 22 deg at P, PR = 9, RQ = 5, two positions of Q
    for k, th in (("a", 42.40), ("b", 137.60)):
        p = aa(1, 22, 180 - 22 - th) if k == "b" else aa(1, 22, 180 - 22 - th)
        tri(f"t3_q8{k}", p, sides=[("P", "R", "9 cm"), ("Q", "R", "5 cm")], angles=[("P", "22°", 60, 16, None, 0, -1)], maxw=175, maxh=100)
    # Q9: 36 deg at Q (bottom-right), QR = 6, PR = 4: two positions of P
    for k, th in (("a", 61.85), ("b", 118.15)):
        tri(f"t3_q9{k}", aa(1, th, 36), sides=[("P", "R", "4 cm"), ("Q", "R", "6 cm")], angles=[("Q", "36°", 30)], maxw=175, maxh=120)

    # Q11 (PDF 212): A south, B 67 km north, C north-east
    A = (0.0, 0.0)
    B = (0.0, 67.0)
    C = (146.77 * sin(R(39)), 146.77 * cos(R(39)))

    def q11(f, S):
        f.arrow(S["B"][0], S["B"][1], S["B"][0], S["B"][1] - 30, width=1.2, head=6)
        f.arc(S["B"][0], S["B"][1], 14, 90, 90 - 63)
        f.text(S["B"][0] + 10, S["B"][1] - 24, "63°", size=10.5)
        f.arc(S["A"][0], S["A"][1], 18, 90, 90 - 39)
        f.text(S["A"][0] + 16, S["A"][1] - 44, "39°", size=10.5)
    tri("t3_q11", {"A": A, "B": B, "C": C}, poly=("A", "B", "C"), sides=[("A", "B", "67 km", False, 20)],
        names=[("A", "A", -10, 4), ("B", "B", -10, 4), ("C", "C", 9, -2)], extra=q11, maxw=150, maxh=150)
    # Q12: path inclined 12 deg, AB = 20, elevation 34 deg
    Bp = (20 * cos(R(12)), 20 * sin(R(12)))
    Tp = (Bp[0], Bp[1] + 9.04)

    def q12(f, S):
        f.line(S["A"][0], S["A"][1], S["B"][0] + 4, S["A"][1], width=1.1, dash="4 3", color="faint")
        right_mark(f, S["B"], S["T"], (S["B"][0], S["A"][1]), 7) if False else None
    tri("t3_q12", {"A": (0, 0), "B": Bp, "T": Tp}, poly=("A", "B", "T"), extra=q12,
        names=[("A", "A", -6, 12), ("B", "B", 8, 12), ("T", "T", 8, -4)], maxw=160, maxh=110)
    # Q14 (area 48)
    tri("t3_q14a", sas(16, 12, 30), sides=[("P", "R", "12 m"), ("P", "Q", "x")], angles=[("P", "30°", 34)], maxw=175, maxh=100)
    p = sas(11.35, 9, 70)
    tri("t3_q14b", p, rot=-125, sides=[("P", "R", "9 m"), ("P", "Q", "x")], angles=[("P", "70°", 22)], maxw=140, maxh=120)
    tri("t3_q14c", sas(36, 3.48, 130), rot=-80, sides=[("P", "R", "x"), ("P", "Q", "36 m")], angles=[("P", "130°", 20)], maxw=140, maxh=130)
    # Q15 (area 72)
    tri("t3_q15a", sas(18, 16, 30), sides=[("P", "R", "16 cm"), ("P", "Q", "18 cm")], angles=[("P", "θ", 30)], maxw=175, maxh=110)
    tri("t3_q15b", sas(24, 20, 17.45), rot=-50, sides=[("P", "R", "20 cm"), ("P", "Q", "24 cm")], angles=[("P", "θ", -14, 13, None, 0, 0)], maxw=130, maxh=130)
    tri("t3_q15c", sas(12, 10, 75), rot=180 - 40, sides=[("P", "Q", "12 cm"), ("P", "R", "10 cm")], angles=[("P", "θ", 22)], maxw=140, maxh=120)
    # Q16 (exact values)
    for k, (a, b) in zip("abcd", ((60, 45), (30, 45), (45, 60), (45, 30))):
        tri(f"t3_q16{k}", aa(1, a, b), sides=[("P", "R", "6"), ("Q", "R", "x")], angles=[("P", f"{a}°", 30 if a > 30 else 40, 13, None, 0, -1), ("Q", f"{b}°", 30 if b > 30 else 42, 13, None, 0, -1)], maxw=175, maxh=110)
    # Q17: isosceles, apex 35 deg
    s = 11.05
    pts = {"T": (0, 0), "L": (-s * sin(R(17.5)), -s * cos(R(17.5))), "M": (s * sin(R(17.5)), -s * cos(R(17.5)))}

    def ticks(f, S):
        for u in ("L", "M"):
            mx, my = (S["T"][0] + S[u][0]) / 2, (S["T"][1] + S[u][1]) / 2
            dx, dy = S[u][0] - S["T"][0], S[u][1] - S["T"][1]
            n = hypot(dx, dy)
            f.line(mx - 4 * dy / n, my + 4 * dx / n, mx + 4 * dy / n, my - 4 * dx / n, width=1.2)
    tri("t3_q17", pts, poly=("T", "L", "M"), angles=[("T", "35°", 40, 16)], extra=ticks, maxw=110, maxh=120)
    # 5J Q14, Q15 (PDF 217)
    tri("t3_j14", sas(8, 5, 60), sides=[("P", "R", "x"), ("P", "Q", "8"), ("Q", "R", "7")], angles=[("P", "60°", 22)], maxw=175, maxh=120)
    x = 3 * sqrt(3) + sqrt(7)
    pts = {"A": (0, 0), "B": (6 * cos(R(-12)), 6 * sin(R(-12)))}
    # C on the ray from A at -42 deg (30 deg below AB), at distance x
    pts["C"] = (x * cos(R(-42)), x * sin(R(-42)))
    tri("t3_j15", pts, poly=("A", "B", "C"), sides=[("A", "B", "6 cm"), ("B", "C", "4 cm"), ("A", "C", "x cm")],
        angles=[("A", "30°", 34, 14, ("B", "C"), 4, 2)], names=[("A", "A", -8, -6), ("B", "B", 9, -4), ("C", "C", 6, 12)], maxw=160, maxh=130)


def fig_t3_pp():
    # Hard / mini exam / review past-paper figures
    # Scots 2023 Q19: P top-left 21 deg 23', R bottom (theta, obtuse), Q bottom-right
    p = aa(1, 21 + 23 / 60, 180 - 21 - 23 / 60 - 127.72)
    p = {"P": p["R"], "Q": p["Q"], "R": p["P"]}  # rename so P is the 21 deg 23' vertex
    tri("pp3_sc23_19", aa(5.9, 127.72, 180 - 127.72 - (21 + 23 / 60)), sides=[("P", "Q", "5.9 cm"), ("Q", "R", "12.8 cm")],
        angles=[("R", "21°23′", -22, 16, None, 0, 0), ("P", "θ", 20, 10, None, 0, -2)], maxw=240, maxh=140)
    # SBHS 2021 Part D (b)(i): A top-left, C bottom-left, B right (drawn with C = 135 deg)
    tri("pp3_sb21_d", aa(1, 135.22, 25), names=[("R", "A", -4, -8), ("P", "C", -2, 15), ("Q", "B", 9, 4)], maxw=220, maxh=130)
    # Baulkham Hills 2020 Q14: theta top, 6 left, 10 base, 35 deg bottom-right (drawn with theta = 73 deg)
    tri("pp3_bh20_14", aa(10, 180 - 35 - 72.93, 35), sides=[("P", "R", "6"), ("P", "Q", "10")], angles=[("Q", "35°", 30), ("R", "θ", 22)], maxw=240, maxh=140)
    # Girraween 2020 Q22(b): 60 deg at the top-left vertex, 8 cm left side, x cm right side, y cm base
    p = sas(11, 8, 60)  # P = top-left vertex, PQ = x = 11, PR = 8
    tri("pp3_g20_22b", p, flipy=True, rot=-30, sides=[("P", "R", "8 cm"), ("P", "Q", "x cm"), ("R", "Q", "y cm")],
        angles=[("P", "60°", 22)], maxw=220, maxh=140)
    # Girraween 2020 Q22(c): P, Q 30 km east, R 12 km on 070 deg T
    P = (0, 0)
    Q = (30, 0)
    Rr = (12 * sin(R(70)), 12 * cos(R(70)))

    def g22c(f, S):
        f.arrow(S["P"][0], S["P"][1], S["P"][0], S["P"][1] - 40, width=1.2, head=6)
        f.text(S["P"][0] - 8, S["P"][1] - 40, "N", size=11, italic=True)
        f.arc(S["P"][0], S["P"][1], 16, 90, 20)
        f.text(S["P"][0] + 6, S["P"][1] - 22, "70°", size=10)
        f.dot(*S["R"], 2.4).dot(*S["Q"], 2.4)
        f.text((S["P"][0] + S["R"][0]) / 2 + 24, (S["P"][1] + S["R"][1]) / 2 + 1, "12 km", size=11)
        f.text((S["P"][0] + S["Q"][0]) / 2, S["P"][1] + 16, "30 km", size=11)
    tri("pp3_g20_22c", {"P": P, "Q": Q, "R": Rr}, poly=None, extra=lambda f, S: (f.line(*S["P"], *S["R"], width=1.5), f.line(*S["P"], *S["Q"], width=1.5), g22c(f, S)),
        sides=[],
        names=[("P", "P", -6, 14), ("Q", "Q", 6, 14), ("R", "R", 8, -4)], maxw=220, maxh=100)
    # SBHS 2024 Part B Q4
    sA = 4 / 9
    cA = sqrt(1 - sA * sA)
    pts = {"A": (0, 0), "B": (18 * cA, 18 * sA), "D": (24 * cA, 24 * sA), "E": (30, 0), "C": (18 * cA, 0)}

    def sb24(f, S):
        f.line(*S["A"], *S["D"], width=1.5).line(*S["D"], *S["E"], width=1.5).line(*S["A"], *S["E"], width=1.5)
        f.line(*S["B"], *S["C"], width=1.5)
        right_mark(f, S["C"], S["A"], S["B"], 7)
    tri("pp3_sb24_b4", pts, poly=None, extra=sb24, sides=[],
        names=[("A", "A", -8, 6), ("B", "B", -4, -10), ("C", "C", 0, 15), ("D", "D", 6, -8), ("E", "E", 8, 6)], maxw=260, maxh=110)
    # NSG 2023 Q20(a): A, B on 050 T at 150 km, C on 080 T at 157.7 km, BC = 80 km
    Bx, By = 150 * sin(R(50)), 150 * cos(R(50))
    AC = 160 * sin(R(80.364))
    Cx, Cy = AC * sin(R(80)), AC * cos(R(80))

    def nsg(f, S):
        for (u, ang, lab) in (("B", 50, "050°T"), ("C", 80, "080°T")):
            x0, y0 = S[u]
            x1, y1 = x0 + 50 * sin(R(ang)), y0 - 50 * cos(R(ang))
            f.arrow(x0, y0, x1, y1, width=1.1, head=5, dash="3 3")
            f.text(x1 + 6, y1 - 2, lab, size=10.5, anchor="start")
    tri("pp3_nsg23_20", {"A": (0, 0), "B": (Bx, By), "C": (Cx, Cy)}, poly=("A", "B", "C"), extra=nsg,
        sides=[("A", "B", "150 km", False, 26), ("B", "C", "80 km", False, 22)],
        names=[("A", "A", -8, 6), ("B", "B", -6, -8), ("C", "C", 0, 15)], maxw=260, maxh=150)
    # SBHS 2020 Q20: 8 cm left side, 61 deg bottom-left, 42 deg bottom-right, b cm right side
    tri("pp3_sb20_20", aa(1, 61, 42), sides=[("P", "R", "8 cm"), ("Q", "R", "b cm")], angles=[("P", "61°", 22), ("Q", "42°", 26)], maxw=220, maxh=130)
    # NBCS 2022 Q5: 35 deg at the top-right vertex, 30 m and 20 m, base 17.8 m
    p = sas(30, 20, 35)
    tri("pp3_nb22_5", p, rot=180 + 35 + 0, flipx=False,
        sides=[("P", "Q", "30 m"), ("P", "R", "20 m"), ("Q", "R", "17.8 m")], angles=[("P", "35°", 48, 14, None, 0, 0)], maxw=200, maxh=120)
    # SBHS 2022 Part D Q4 (second): BCD straight, C between B and D
    Cpt = (0.0, 0.0)
    ang = 25.0                                  # direction of CB below the horizontal
    Bpt = (6 * cos(R(-ang)), 6 * sin(R(-ang)))
    Dpt = (-7.16 * cos(R(-ang)), -7.16 * sin(R(-ang)))
    aAC = -ang - 130                            # angle ACB = 130 measured from CB
    Apt = (7.9 * cos(R(aAC)), 7.9 * sin(R(aAC)))

    def sb22(f, S):
        f.line(*S["D"], *S["B"], width=1.5).line(*S["A"], *S["D"], width=1.5).line(*S["A"], *S["C"], width=1.5).line(*S["A"], *S["B"], width=1.5)
        f.arc(S["C"][0], S["C"][1], 9, -ang - 130, -ang, color="ink", width=1.1)
        f.text(S["C"][0] + 4, S["C"][1] + 22, "130°", size=10.5)
    tri("pp3_sb22_d4", {"A": Apt, "B": Bpt, "C": Cpt, "D": Dpt}, poly=None, extra=sb22,
        sides=[("A", "D", "6.4 cm", False, 24), ("A", "C", "7.9 cm", True, 14), ("C", "B", "6 cm", False, 14)],
        names=[("A", "A", -8, 6), ("B", "B", 8, 6), ("C", "C", 2, -8), ("D", "D", -4, -8)], maxw=240, maxh=130)
    # Girraween 2022 Q25(b): theta at the top, right side vertical 515.5, 74 deg 24' at the left vertex, 416.6 lower side
    th = 51.12
    top = (0.0, 515.5)
    br = (0.0, 0.0)
    left_ang = 74.4
    # left vertex L: |L - br| = 416.6, angle at L = 74.4, angle at top = theta
    ang_br = 180 - th - left_ang                # angle at the bottom-right vertex
    Lp = (-416.6 * sin(R(ang_br)), 416.6 * cos(R(ang_br)))
    tri("pp3_g22_25b", {"T": top, "B": br, "L": Lp}, poly=("T", "B", "L"),
        sides=[("T", "B", "515.5", False, 18), ("L", "B", "416.6", False, 14)],
        angles=[("T", "θ", 24, 13, ("B", "L")), ("L", "74°24′", 36, 13, ("T", "B"))], maxw=150, maxh=150)
    # review: Sydney Grammar 2020 Q3(b): B top, C left (60 deg), A bottom-right
    p = sas(6, 5, 60)                           # P = C, PQ = CA = 6, PR = CB = 5
    tri("pp3_sgs20_3b", p, rot=-20, sides=[("P", "R", "5 cm"), ("P", "Q", "6 cm")], angles=[("P", "60°", 22)],
        names=[("P", "C", -9, 4), ("Q", "A", 8, 6), ("R", "B", 0, -8)], maxw=170, maxh=130)
    # review: Scots 2023 Q18: A top-left (65 deg), C right, B bottom
    p = sas(18, 25, 65)                          # P = A, PQ = AC = 18, PR = AB = 25
    tri("pp3_sc23_18", p, flipy=True, rot=-20, sides=[("P", "Q", "18 km"), ("P", "R", "25 km")], angles=[("P", "65°", 22)],
        names=[("P", "A", -4, -8), ("Q", "C", 9, 4), ("R", "B", 0, 15)], maxw=150, maxh=130)


if __name__ == "__main__":
    fig_t3()
    fig_t3_pp()
