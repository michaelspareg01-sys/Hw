"""Figures for Lesson 5H, the trapezoidal rule (kept apart from figs.py, which the scaffold task owns).

Run: python3 workspace/build/int1/figs_5h.py   (writes svg/c5h_*.svg, svg/q5h_*.svg, svg/p5h_*.svg, svg/a5h_*.svg)

The data used to draw the two river graphs (CREEK_FLOW, Q17_FLOW) are module constants, so the check
script can confirm that the values read off the graphs in the lesson are the values the graphs show.
"""
import os
import sys
from math import log, sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Graph, Fig, save, ACC, INK, FAINT  # noqa: E402

LINE = "#cdd4dd"


def zero(x):
    return 0.0


def pchip(pts):
    """Monotone cubic (Fritsch-Carlson) through the points [(x, y), ...]; returns a function of x.
    The curve passes exactly through every point and does not overshoot between them."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    hs = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / hs[i] for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * hs[i] + hs[i - 1], hs[i] + 2 * hs[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        i = max(k for k in range(n - 1) if xs[k] <= x)
        h = hs[i]
        t = (x - xs[i]) / h
        h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
        h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        return h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1]
    return f


def seg(g, x0, y0, x1, y1, color="ink", width=1.3, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ''
    g.items.append(f'<line x1="{g.X(x0):.1f}" y1="{g.Y(y0):.1f}" x2="{g.X(x1):.1f}" y2="{g.Y(y1):.1f}" '
                   f'stroke="{ACC[color]}" stroke-width="{width}"{dd}/>')


def text(items, x, y, s, anchor="middle", size=11, italic=False, weight=500, rotate=None, color=INK):
    st = ' font-style="italic"' if italic else ''
    rt = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ''
    items.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" '
                 f'font-weight="{weight}"{st}{rt}>{s}</text>')


# ---------------------------------------------------------------- data of the two river graphs
# Example 34 (Peachtree Creek): flow rate in cubic feet per second against t in hours. The values at
# t = 4, 6, ..., 24 are the book's table; the other points only shape the curve.
CREEK_FLOW = [(0, 60), (2, 70), (3, 80), (4, 100), (5, 250), (6, 600), (7, 2600), (8, 5500), (9, 6450),
              (10, 6700), (11, 6450), (12, 5800), (13, 5250), (14, 4800), (15, 4450), (16, 4100), (17, 3000),
              (18, 1800), (19, 1150), (20, 800), (21, 680), (22, 600), (23, 550), (24, 500)]
CREEK_RAIN = [(0.9, .005), (1.2, .04), (1.9, .01), (2.2, .02), (2.5, .012), (2.8, .015), (3.1, .01), (3.5, .012),
              (4.2, .005), (4.6, .025), (4.9, .01), (5.2, .045), (5.5, .06), (5.8, .065), (6.1, .35),
              (6.35, .23), (6.6, .08), (6.85, .06), (7.1, .11), (7.35, .12), (7.6, .09), (7.85, .12),
              (8.1, .09), (8.35, .095), (8.6, .095), (8.85, .065), (9.1, .03), (10.0, .01), (14.0, .008),
              (21.8, .006), (22.9, .01), (23.6, .012)]

# Exercise 5H Q17 (Turia River, Control Point X): flow rate (Caudal) in cubic metres per second against
# the time in hours after 04/05/2004 17:40. The grid times 0, 6, 12, 18 (part a) and 24, 27, ..., 42
# (part b) are read off in the answers; the other points only shape the curve.
Q17_FLOW = [(0, 2.4), (6, 2.2), (12, 2.1), (15, 2.15), (18, 2.3), (20, 2.7), (21.5, 3.1), (22.5, 3.25),
            (24, 3.3), (25.5, 3.6), (27, 4.0), (28.5, 5.6), (30, 7.6), (31.5, 10.0), (33, 12.7), (34, 14.7),
            (34.6, 14.0), (35.1, 14.5), (36, 11.0), (37.5, 8.6), (39, 7.4), (42, 6.3), (45, 5.9), (48, 5.3),
            (51, 4.6), (54, 4.4), (57, 4.3), (60, 3.9), (63, 3.7), (66, 3.6), (69, 3.4), (72, 3.2)]
Q17_RAIN = [(14.6, 1.4), (15.1, 4.4), (15.6, 0.7), (16.0, 1.4), (16.5, 2.8), (16.9, 1.2), (17.4, 1.5),
            (19.5, 0.7), (19.9, 1.5), (22.2, 2.2), (23.2, 0.8), (24.3, 6.7), (24.7, 3.0), (25.1, 3.0),
            (25.5, 3.0), (25.9, 5.0), (26.3, 5.8), (26.7, 3.0), (27.1, 3.7), (27.5, 3.0), (27.9, 3.0),
            (28.3, 3.0), (28.7, 3.0), (29.1, 3.0), (29.5, 3.1), (30.4, 3.9), (30.8, 14.7), (31.2, 9.8),
            (31.6, 0.8), (32.0, 9.6), (32.4, 9.4), (32.8, 5.8), (33.3, 1.4), (33.7, 1.5), (39.5, 0.8)]
Q17_TIMES = ["04/05/2004 17:40", "04/05/2004 23:40", "05/05/2004 05:40", "05/05/2004 11:40",
             "05/05/2004 17:40", "05/05/2004 23:40", "06/05/2004 05:40", "06/05/2004 11:40",
             "06/05/2004 17:40", "06/05/2004 23:40", "07/05/2004 05:40", "07/05/2004 11:40"]


# ---------------------------------------------------------------- lesson figures
def lesson():
    # Box 18: one trapezium, the chord joining (a, f(a)) and (b, f(b)) above a concave-up curve
    def f(x):
        return 1.0 + 0.09 * (x - 1.2) ** 2

    a, b = 1.5, 4.6
    g = Graph(-0.3, 5.3, -0.3, 2.4, w=240, h=165, pad=(40, 26, 22, 22))
    g.fill(f, zero, a, b, opacity=0.28)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.4, x0=0.9, x1=5.0)
    seg(g, a, f(a), b, f(b), width=1.1)
    g.vline(a, 0, f(a), color="ink", dash="", width=1.0).vline(b, 0, f(b), color="ink", dash="", width=1.0)
    g.hline(f(a), x0=0, x1=a).hline(f(b), x0=0, x1=b)
    g.label(a, 0, "a", dy=12, italic=True).label(b, 0, "b", dy=12, italic=True)
    g.label(0, f(a), "f(a)", dx=-5, anchor="end", italic=True, size=10.5)
    g.label(0, f(b), "f(b)", dx=-5, anchor="end", italic=True, size=10.5)
    save("c5h_one", g)

    # Example 32: y = 1/x from 1 to 5, the single chord and the four chords
    g = Graph(-0.3, 6.0, -0.2, 1.75, w=230, h=190, pad=(24, 26, 22, 22))
    g.fill(lambda x: 1 / x, zero, 1, 5, opacity=0.28)
    g.axes("x", "y")
    g.curve(lambda x: 1 / x, color="ink", width=1.4, x0=0.6, x1=5.8)
    seg(g, 1, 1, 5, 0.2, width=1.0)
    for k in range(1, 5):
        seg(g, k, 1 / k, k + 1, 1 / (k + 1), width=1.0)
    for k in range(1, 6):
        g.vline(k, 0, 1 / k, color="ink", dash="", width=0.9)
    g.xticks([(1, "1"), (3, "3"), (5, "5")])
    g.yticks([(1, "1")])
    save("c5h_e32", g)

    # The n subintervals of width h (as in the book: four on the left, three on the right)
    fg = Fig(520, 54)
    y = 30
    left, right = [40, 90, 140, 190, 240], [320, 370, 420, 470]
    fg.line(20, y, 500, y, width=1.3)
    for X in left + right:
        fg.line(X, y - 4, X, y + 4, width=1.3)
    for ticks in (left, right):
        for i in range(len(ticks) - 1):
            fg.text((ticks[i] + ticks[i + 1]) / 2, 12, "h", italic=True, size=11.5)
    fg.text(280, 13, "· · ·", size=11).text(280, 47, "· · ·", size=11)

    def sub(base, s):
        return (f'<tspan font-style="italic">{base}</tspan><tspan dy="3" font-size="8.5">{s}</tspan>'
                f'<tspan dy="-3"></tspan>')
    labs = [(40, sub("x", "0"), True), (90, sub("x", "1"), False), (140, sub("x", "2"), False),
            (190, sub("x", "3"), False), (370, sub("x", "n−2"), False), (420, sub("x", "n−1"), False)]
    for X, s, pre in labs:
        s = ('<tspan font-style="italic">a</tspan> = ' + s) if pre else s
        fg.raw(f'<text x="{X}" y="47" text-anchor="{"end" if pre else "middle"}" font-size="11.5" fill="{INK}" '
               f'dx="{8 if pre else 0}">{s}</text>')
    fg.raw(f'<text x="{470 - 6}" y="47" text-anchor="start" font-size="11.5" fill="{INK}">{sub("x", "n")}'
           f' = <tspan font-style="italic">b</tspan></text>')
    save("c5h_div", fg)

    creek()


def creek():
    """Example 34: rainfall and streamflow at Peachtree Creek (recreated; axis titles set horizontally)."""
    W, H = 520, 300
    L, R, T, B = 50, 470, 62, 252
    fg = Fig(W, H)
    X = lambda t: L + (R - L) * t / 24
    Y = lambda q: B - (B - T) * q / 7500
    YR = lambda r: B - (B - T) * r / 0.4
    for k in range(1, 6):
        fg.line(L, Y(1500 * k), R, Y(1500 * k), color="faint", width=0.6)
    for t, r in CREEK_RAIN:
        fg.items.append(f'<rect x="{X(t) - 1.6:.1f}" y="{YR(r):.1f}" width="3.2" height="{B - YR(r):.1f}" '
                        f'fill="#38bdf8" fill-opacity="0.85"/>')
    q = pchip(CREEK_FLOW)
    pts = " ".join(f"{X(t / 10):.1f},{Y(q(t / 10)):.1f}" for t in range(0, 241))
    fg.items.append(f'<polyline points="{pts}" fill="none" stroke="#dc2626" stroke-width="1.6"/>')
    fg.line(L, T, L, B, width=1.0).line(R, T, R, B, width=1.0).line(L, T, R, T, width=1.0).line(L, B, R, B, width=1.0)
    for t in range(0, 25):
        fg.line(X(t), B, X(t), B + (4 if t % 2 == 0 else 2.5), width=0.8)
    for k in range(6):
        text(fg.items, L - 5, Y(1500 * k) + 4, f"{1500 * k}", anchor="end", size=10)
        text(fg.items, R + 5, YR(0.08 * k) + 4, f"{0.08 * k:.2f}".rstrip("0").rstrip(".") if k else "0", anchor="start", size=10)
    for t in range(0, 25, 2):
        text(fg.items, X(t), B + 16, f"{t}:00", size=8.6)
    text(fg.items, L - 40, T - 10, "Streamflow, in cubic feet per second", anchor="start", size=10)
    text(fg.items, R + 36, T - 10, "Rainfall, in inches", anchor="end", size=10)
    text(fg.items, (L + R) / 2, 16, "Rainfall and streamflow at Peachtree Creek, Dec. 24, 2002", size=11.5, weight=700)
    # legend last, on a white box
    fg.items.append(f'<rect x="{R - 112}" y="{T + 4}" width="104" height="31" fill="#fff" stroke="{INK}" stroke-width="0.8"/>')
    fg.line(R - 104, T + 12, R - 86, T + 12, color="rose", width=1.8)
    fg.items.append(f'<rect x="{R - 104}" y="{T + 23}" width="18" height="4" fill="#38bdf8"/>')
    text(fg.items, R - 82, T + 16, "Streamflow", anchor="start", size=10)
    text(fg.items, R - 82, T + 29, "Rainfall", anchor="start", size=10)
    save("c5h_creek", fg)


# ---------------------------------------------------------------- textbook exercise figures
def exercise():
    # Q11: the lake, widths 20, 18, 17 at 10-metre intervals
    top = pchip([(0, 0), (0.6, 4.5), (3, 8.5), (10, 11), (20, 8), (30, 4), (34, 6.2), (37, 6.4), (39.2, 3.5), (40, 0)])
    bot = pchip([(0, 0), (0.6, -3.5), (3, -6.8), (10, -9), (20, -10), (30, -13), (35, -10.5), (38, -6.5), (39.4, -3), (40, 0)])
    g = Graph(0, 40, -14, 12, w=230, h=150, pad=(14, 14, 8, 26))
    xs = [i / 10 for i in range(0, 401)]
    path = " ".join(f"{g.X(x):.1f},{g.Y(top(x)):.1f}" for x in xs) + " " + \
        " ".join(f"{g.X(x):.1f},{g.Y(bot(x)):.1f}" for x in reversed(xs))
    g.items.append(f'<polygon points="{path}" fill="#7dd3fc" fill-opacity="0.45" stroke="{INK}" stroke-width="1.1"/>')
    for v, wd in ((10, "20"), (20, "18"), (30, "17")):
        seg(g, v, bot(v), v, top(v), width=0.9)
        g.label(v - 2.6, (top(v) + bot(v)) / 2, wd, size=11)
    for v in (0, 10, 20, 30, 40):
        lo = bot(v) if v not in (0, 40) else 0
        seg(g, v, lo - 0.6, v, -15.8, color="faint", width=0.9, dash="3 2")
        g.items.append(f'<text x="{g.X(v):.1f}" y="{g.h - 6}" text-anchor="middle" font-size="11" fill="{INK}">{v}</text>')
    save("q5h_11", g)

    # Q12: the rock cutting, heights 5, 10, 13, 14, 11, 7, 3 at 50-metre intervals
    hts = [5, 10, 13, 14, 11, 7, 3]
    prof = pchip([(50 * i, hts[i]) for i in range(7)])
    g = Graph(0, 300, 0, 16, w=230, h=130, pad=(14, 16, 8, 22))
    xs = [i for i in range(0, 301)]
    path = f"{g.X(0):.1f},{g.Y(0):.1f} " + " ".join(f"{g.X(x):.1f},{g.Y(prof(x)):.1f}" for x in xs) + \
        f" {g.X(300):.1f},{g.Y(0):.1f}"
    g.items.append(f'<polygon points="{path}" fill="#d1d5db" stroke="{INK}" stroke-width="1.1"/>')
    for i in range(1, 6):
        seg(g, 50 * i, 0, 50 * i, hts[i], width=0.9)
    for i, hh in enumerate(hts):
        if i == 6:
            g.label(300, 1.6, "3", dx=8, size=11)
        else:
            g.label(50 * i + 17, min(hh, prof(50 * i + 17)) * 0.42, str(hh), size=11)
    for v in (0, 100, 200, 300):
        g.items.append(f'<text x="{g.X(v):.1f}" y="{g.h - 5}" text-anchor="middle" font-size="11" fill="{INK}">{v}</text>')
    save("q5h_12", g)

    q17()


def q17():
    """Exercise 5H Q17: the Turia River hydrograph (recreated; the book's rotated date-time labels are set
    in two lines, time above day/month, and the axis titles are set horizontally)."""
    W, H = 580, 360
    L, R, T, B = 48, 512, 78, 286
    fg = Fig(W, H)
    X = lambda t: L + (R - L) * t / 72
    Y = lambda q: B - (B - T) * q / 16
    for k in range(1, 9):
        fg.line(L, Y(2 * k), R, Y(2 * k), color="faint", width=0.7, dash="4 3")
    for i in range(1, 12):
        fg.line(X(6 * i), T, X(6 * i), B, color="faint", width=0.7, dash="4 3")
    for t, r in Q17_RAIN:
        fg.items.append(f'<rect x="{X(t) - 1.8:.1f}" y="{Y(r):.1f}" width="3.6" height="{B - Y(r):.1f}" '
                        f'fill="#38bdf8" fill-opacity="0.9"/>')
    q = pchip(Q17_FLOW)
    pts = " ".join(f"{X(t / 10):.1f},{Y(q(t / 10)):.1f}" for t in range(0, 721))
    fg.items.append(f'<polyline points="{pts}" fill="none" stroke="#dc2626" stroke-width="1.5"/>')
    fg.line(L, T, L, B, width=1.0).line(R, T, R, B, width=1.0).line(L, B, R, B, width=1.0).line(L, T, R, T, width=1.0)
    for k in range(0, 10):
        yy = B - (B - T) * 0.5 * k / 4.5
        fg.line(R, yy, R + 3, yy, width=0.8)
    for i in range(13):
        fg.line(X(6 * i), B, X(6 * i), B + 4, width=0.8)
    for k in range(0, 9):
        text(fg.items, L - 6, Y(2 * k) + 4, f"{2 * k}", anchor="end", size=10.5)
    for k in range(0, 10):
        yy = B - (B - T) * 0.5 * k / 4.5
        text(fg.items, R + 6, yy + 4, f"{0.5 * k:g}", anchor="start", size=10.5)
    for i, lab in enumerate(Q17_TIMES):
        day, tm = lab.split(" ")
        text(fg.items, X(6 * i), B + 17, tm, size=9.5)
        text(fg.items, X(6 * i), B + 30, day[:5], size=9.5)
    text(fg.items, L - 40, T - 12, "Caudal en m³/s", anchor="start", size=10.5)
    text(fg.items, R + 40, T - 12, "Lluvia en mm", anchor="end", size=10.5)
    text(fg.items, (L + R) / 2, H - 10, "Fecha (día/mes, 2004)", size=11, weight=700)
    text(fg.items, (L + R) / 2, 16, "Punto de control X", size=12, weight=700)
    fg.items.append(f'<rect x="{L + 95}" y="26" width="250" height="22" fill="#fff" stroke="{INK}" stroke-width="0.8"/>')
    fg.items.append(f'<rect x="{L + 105}" y="35" width="20" height="5" fill="#38bdf8"/>')
    fg.line(L + 215, 37.5, L + 241, 37.5, color="rose", width=1.8)
    text(fg.items, L + 130, 42, "LLUVIA", anchor="start", size=11)
    text(fg.items, L + 245, 42, "Caudal de entrada", anchor="start", size=11)
    save("q5h_17", fg)


# ---------------------------------------------------------------- past paper
def pastpaper():
    # SGS 2023 Q3: y = log_a x, shaded from x = 2 to x = 4
    g = Graph(-0.6, 5.8, -1.4, 2.1, w=250, h=175, pad=(18, 30, 22, 14))
    g.fill(lambda x: log(x), zero, 2, 4, color="faint", opacity=0.55)
    g.axes("x", "y")
    g.curve(lambda x: log(x), color="ink", width=1.2, x0=0.27, x1=5.85)
    g.vline(2, 0, log(2), color="ink", width=1.0).vline(4, 0, log(4), color="ink", width=1.0)
    g.xticks([(1, ""), (2, ""), (3, ""), (4, ""), (5, "")])
    for v in (1, 2, 3, 4, 5):
        g.label(v, 0, str(v), dx=(4 if v == 1 else 0), dy=13, size=11)
    g.label(0, 0, "0", dx=-9, dy=12, size=11)
    g.items.append(f'<text x="{g.X(3.75):.1f}" y="{g.Y(1.78):.1f}" text-anchor="middle" font-size="11.5" fill="{INK}">'
                   f'<tspan font-style="italic">y</tspan> = log<tspan dy="3" font-size="8" font-style="italic">a</tspan>'
                   f'<tspan dy="-3"> </tspan><tspan font-style="italic">x</tspan></text>')
    save("p5h_sgs", g)


# ---------------------------------------------------------------- answer figures
def answers():
    # Q4a: concave up, chord above; Q4b: concave down, chord below
    for name, f in (("a5h_q4a", lambda x: 0.6 + 0.1 * (x - 0.6) ** 2), ("a5h_q4b", lambda x: 2.0 - 0.16 * (x - 3.6) ** 2)):
        a, b = 1.0, 4.4
        g = Graph(-0.2, 5.2, -0.2, 2.4, w=190, h=130, pad=(14, 26, 22, 20))
        g.fill(f, zero, a, b, opacity=0.25)
        g.axes("x", "y")
        g.curve(f, color="ink", width=1.4, x0=0.5, x1=4.9)
        seg(g, a, f(a), b, f(b), color="rose", width=1.3)
        g.vline(a, 0, f(a), color="ink", dash="", width=1.0).vline(b, 0, f(b), color="ink", dash="", width=1.0)
        g.label(a, 0, "a", dy=12, italic=True).label(b, 0, "b", dy=12, italic=True)
        save(name, g)

    # Q5c: y = x(4 - x) with the four chords
    f = lambda x: x * (4 - x)
    g = Graph(-0.5, 4.8, -0.6, 4.6, w=200, h=170, pad=(22, 26, 22, 20))
    g.fill(f, zero, 0, 4, opacity=0.25)
    g.axes("x", "y")
    g.curve(f, color="ink", width=1.4, x0=0, x1=4)
    for k in range(4):
        seg(g, k, f(k), k + 1, f(k + 1), color="rose", width=1.3)
    for k in (1, 2, 3):
        g.vline(k, 0, f(k), color="ink", dash="", width=0.9)
    g.xticks([(1, "1"), (2, "2"), (3, "3"), (4, "4")])
    g.yticks([(3, "3"), (4, "4")])
    save("a5h_q5", g)


if __name__ == "__main__":
    lesson()
    exercise()
    pastpaper()
    answers()
    print("ok")
