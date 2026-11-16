"""Figures for Lesson 1 (the graphical method and substitution). Run after figs.py: python3 figs_l1.py

Book figures are redrawn to scale from their equations. Blank grids for the homework use 1 cm to
1 unit where the book asks for that scale (Exercise 3C Q10 and Q11). Answer graphs are drawn to scale
with the point of intersection marked and labelled. The two past-paper sketches are redrawn from the
scanned papers (pixel coordinates of the scans), not to scale, as printed.
"""
from figs import Plane, Sketch, save, CM, INK


def two_lines(name, xr, yr, l1, l2, ix, unit=22.0, grid=True, guides=True, colors=("blue", "rose"),
              pad=(22, 22, 20, 20), names=None):
    """Lines l1, l2 = (a, b, c, 'eq') meaning ax + by = c, labelled with their equations (names);
    ix = the intersection, marked with a dot, dashed guides and its coordinates."""
    p = Plane(*xr, *yr, unit=unit, grid=grid, pad=pad)
    for (a, b, c, eq), col, nm in zip((l1, l2), colors, names):
        p.line(a, b, c, col, eq=eq)
    if ix:
        if guides:
            p.guides(*ix)
        p.dot(*ix)
        p.plabel(ix[0], ix[1], "(" + ", ".join(str(v) for v in ix) + ")")
    for (a, b, c, eq), col, nm in zip((l1, l2), colors, names):
        p.llabel(a, b, c, nm, col)
    save(name, p)
    return p


# ---------- Concept 1: Year 8 7G Key ideas figure: y = 6 - 3x and y = 2x + 1 meet at (1, 3) ----------
def f_7g():
    p = Plane(0, 3, 0, 6, unit=28, grid=False, pad=(22, 40, 16, 16), xticks=[1, 2, 3], yticks=[1, 2, 3, 4, 5])
    p.line(3, 1, 6, "blue", eq="y=6-3x", lo=0.0)
    p.line(-2, 1, 1, "rose", eq="y=2x+1", lo=0.0)
    p.dot(1, 3)
    p.label(1, 3, "(1, 3)", "start", size=11.5, dx=10, dy=-1)
    p.label(2.05, 4.35, "Point of", "start", size=11.5)
    p.label(2.05, 3.8, "intersection", "start", size=11.5)
    save("l1_7g", p)


# ---------- Concept 2: Year 11 Advanced Example 8 (3C), to scale ----------
def f_ex8():
    p = Plane(-1, 7, -4, 4, unit=26, grid=False, xticks=[3, 4, 6], yticks=[-3, 1, 3], pad=(24, 22, 16, 16))
    p.line(1, 2, 6, "blue", eq="x+2y-6=0")
    p.line(1, -1, 3, "rose", eq="y=x-3")
    p.guides(4, 1)
    p.dot(4, 1)
    save("l1_ex8", p)


def grids():
    # tutor demo and your turn (Concept 2): blank grids
    save("l1_d2g", Plane(-1, 9, -3, 5, unit=CM * 0.6))
    save("l1_y2g", Plane(-1, 8, -3, 8, unit=CM * 0.55))
    # homework: Exercise 3C Q10 and Q11 at 1 cm to 1 unit; Q13 and Q14 sketches
    save("l1_g10", Plane(-2, 6, -2, 6, unit=CM, pad=(10, 14, 14, 10), axis_extra=0.3))
    save("l1_g11", Plane(-4, 3, -3, 4, unit=CM, pad=(10, 14, 14, 10), axis_extra=0.3))
    save("l1_g13", Plane(-4, 4, -4, 4, unit=CM * 0.75))


def answers():
    # C2 tutor demo: x + 2y - 8 = 0 and y = x - 2 meet at (4, 2)
    two_lines("l1_d2a", (-1, 9), (-3, 5), (1, 2, 8, "x+2y-8=0"), (1, -1, 2, "y=x-2"), (4, 2), unit=26,
              names=("x + 2y − 8 = 0", "y = x − 2"), pad=(22, 22, 16, 16))
    # C2 your turn: x + y - 7 = 0 and y = 2x - 2 meet at (3, 4)
    two_lines("l1_y2a", (-1, 8), (-3, 8), (1, 1, 7, "x+y-7=0"), (2, -1, 2, "y=2x-2"), (3, 4), unit=28,
              names=("x + y − 7 = 0", "y = 2x − 2"), pad=(22, 22, 16, 16))
    # Exercise 3C Q10: x + y = 5 and x - y = 1 meet at (3, 2)
    two_lines("l1_q10a", (-2, 6), (-2, 6), (1, 1, 5, "x+y=5"), (1, -1, 1, "x-y=1"), (3, 2), unit=32,
              names=("x + y = 5", "x − y = 1"))
    # Exercise 3C Q11
    two_lines("l1_q11a", (-4, 3), (-3, 4), (1, 1, 2, "x+y=2"), (1, -1, -4, "x-y=-4"), (-1, 3), unit=34,
              names=("x + y = 2", "x − y = −4"))
    two_lines("l1_q11b", (-4, 3), (-3, 4), (1, -1, 3, "x-y=3"), (2, 1, 0, "2x+y=0"), (1, -2), unit=34,
              names=("x − y = 3", "2x + y = 0"))
    two_lines("l1_q11c", (-4, 3), (-3, 4), (1, 2, -4, "x+2y=-4"), (2, -1, -3, "2x-y=-3"), (-2, -1), unit=34,
              names=("x + 2y = −4", "2x − y = −3"))
    # Exercise 3C Q13: y = x/2 + c for c = -2, -1, 1, 2 (parallel lines)
    p = Plane(-4, 4, -4, 4, unit=32)
    for c, col in ((-2, "blue"), (-1, "rose"), (1, "teal"), (2, "violet")):
        p.line(-1, 2, 2 * c, col, eq=f"y=x/2+({c})")
    for c, col in ((-2, "blue"), (-1, "rose"), (1, "teal"), (2, "violet")):
        p.llabel(-1, 2, 2 * c, f"c = {c}", col, ts=(0.9, 0.1, 0.8, 0.2))
    save("l1_q13a", p)
    # Exercise 3C Q14: y - 2 = m(x - 1) for m = 1, 2, -1/2, 0, all through (1, 2)
    p = Plane(-4, 4, -4, 4, unit=32)
    L = (((-1, 1, 1, "m=1"), "blue", "m = 1"), ((-2, 1, 0, "m=2"), "rose", "m = 2"),
         ((1, 2, 5, "m=-1/2"), "teal", "m = −½"), ((0, 1, 2, "m=0"), "violet", "m = 0"))
    for (a, b, c, eq), col, nm in L:
        p.line(a, b, c, col, eq=eq)
    p.guides(1, 2)
    p.dot(1, 2)
    p.plabel(1, 2, "(1, 2)")
    for (a, b, c, eq), col, nm in L:
        p.llabel(a, b, c, nm, col, ts=(0.9, 0.1, 0.8, 0.2, 0.7, 0.3))
    save("l1_q14a", p)


# ---------- past papers (sketches, not to scale) ----------
def pp_girraween20():
    """Girraween 2020 Part A Q11: from the scan (zoom 3), shifted by (-250, -70) and scaled by 0.75."""
    k, ox, oy = 0.75, 250, 70
    T = lambda x, y: ((x - ox) * k, (y - oy) * k)  # noqa: E731
    s = Sketch(330, 200)
    s.text(*T(425, 84), "NOT TO SCALE", size=11, mask=False)
    ax0, ax1 = T(268, 232), T(578, 232)
    s.arrow(*ax0, *ax1, cls="axx")
    ay0, ay1 = T(407, 318), T(407, 125)
    s.arrow(*ay0, *ay1, cls="axy")
    s.line(*T(272, 290), *T(480, 140), cls="sk")      # x - y = -7
    s.line(*T(276, 143), *T(512, 282), cls="sk")      # x + y = 1
    s.text(*T(488, 128), "x − y = −7", "start", size=11.5, mask=False)
    s.text(*T(470, 304), "x + y = 1", "start", size=11.5, mask=False)
    s.text(*T(396, 136), "y", "end", size=12, mask=False)
    s.text(*T(574, 252), "x", "middle", size=12, mask=False)
    s.text(*T(392, 186), "P", "end", size=11.5, mask=False)
    s.text(*T(398, 252), "O", "end", size=11.5, mask=False)
    save("l1_pp_g20", s)


def pp_girraween23():
    """Girraween 2023 MC Q8: four sketches, from the scan (zoom 2.2): axes and two lines in each."""
    panels = {
        "A": dict(yax=(291, 205, 452), xax=(365, 228, 480), lines=[(228, 365, 445, 255), (228, 325, 460, 283)]),
        "B": dict(yax=(834, 205, 452), xax=(365, 775, 1015), lines=[(793, 388, 965, 217), (818, 232, 997, 410)]),
        "C": dict(yax=(307, 68, 345), xax=(244, 240, 520), lines=[(279, 291, 496, 99), (289, 93, 491, 296)]),
        "D": dict(yax=(880, 76, 348), xax=(250, 812, 1080), lines=[(816, 272, 1015, 78), (870, 310, 983, 80)]),
    }
    k = 0.62
    for lab, P in panels.items():
        x0 = min(P["xax"][1], P["yax"][0]) - 14
        y0 = min(P["yax"][1], P["xax"][0]) - 14
        T = lambda x, y: ((x - x0) * k, (y - y0) * k)  # noqa: E731
        w = (P["xax"][2] - x0 + 22) * k
        h = (max(P["yax"][2], P["xax"][0]) - y0 + 10) * k
        s = Sketch(w, h)
        yx, yt, yb = P["yax"]
        xy, xl, xr = P["xax"]
        s.arrow(*T(xl, xy), *T(xr, xy), cls="axx", head=6)
        s.arrow(*T(yx, yb), *T(yx, yt), cls="axy", head=6)
        for (a, b, c, d) in P["lines"]:
            s.line(*T(a, b), *T(c, d), color="#5b6470", cls="sk")
        s.text(*T(yx - 10, yt + 2), "y", "end", size=11, mask=False, italic=True)
        s.text(*T(xr - 2, xy + 16), "x", "middle", size=11, mask=False, italic=True)
        s.text(*T(yx - 8, xy - 12 if lab == "C" else xy + 18), "O", "end", size=11, mask=False, italic=True)
        save(f"l1_pp_g23{lab.lower()}", s)


if __name__ == "__main__":
    f_7g()
    f_ex8()
    grids()
    answers()
    pp_girraween20()
    pp_girraween23()
    print("lesson 1 figures written")
