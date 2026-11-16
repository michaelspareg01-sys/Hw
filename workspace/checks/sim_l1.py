r"""Check of Lesson 1 (the graphical method and substitution), tied to the printed HTML and the figures.

Reads build/sim/l1.html (questions: <span data-q>) and a_l1.html (answers: data-s, data-w, data-c, data-k)
and the figures svg/l1_*.svg. Every pair is re-solved with sympy from the equations AS PRINTED in the
lesson, and compared with the printed solution; every equation printed in the working must hold at that
solution, and every printed check must be true and must substitute into both original equations.
Points on lines (Concept 1, Exercise 3C Q9) are tested by substitution; intercepts are recomputed.
Graphs are read back from the SVG: the scale comes from the tick labels (both axes must have the same
unit, and the Exercise 3C Q10/Q11 grids must be 1 cm to 1 unit), every plotted line must be one of the
printed equations, and the marked point must be the computed intersection, with its printed label.
Multiple-choice keys are recomputed from the printed options (Girraween 2020 from the equations printed
in its figure; Girraween 2023 by reading the slopes, y-intercepts and crossing point of each sketch).
Past-paper labels must be identical in both files and the marks must add to the printed total.
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 -I workspace/checks/sim_l1.py
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_common import (Values, ok, finish, check_pair, equations, maths, tex2sym, points, holds, assignments,  # noqa: E402
                        solve_pair, plotted_lines, marked_points, same_line, on_line, read, svg, svg_texts,
                        axis_scale, clean_tex)
import sympy as sp  # noqa: E402

V = Values(["l1.html", "a_l1.html"])
L1, A1 = read("l1.html"), read("a_l1.html")
x, y = sp.Symbol("x"), sp.Symbol("y")
CM = 96 / 2.54


def pair(key):
    eqs = equations(V.get("q", key))
    ok(len(eqs) == 2, f"{key}: two equations printed", str(eqs))
    return eqs


def yesno(key, truth):
    t = re.sub(r"<[^>]+>", "", V.get("k", key) or "").strip().lower()
    ok(t == ("yes" if truth else "no"), f"{key} {'yes' if truth else 'no'}", f"printed {t!r}")


def intercepts(eq):
    e = sp.expand(eq[0] - eq[1])
    return [(sp.solve(e.subs(y, 0), x)[0], 0), (0, sp.solve(e.subs(x, 0), y)[0])]


def graph(fig, eqs, sol, unit=None, label=True):
    """The plotted lines are exactly the printed equations; the marked point is the solution."""
    L = plotted_lines(fig)
    ok(len(L) == len(eqs) and all(any(same_line(l, e) for l in L) for e in eqs),
       f"{fig}: the plotted lines are the printed equations", f"{len(L)} lines")
    if sol is not None:
        P = marked_points(fig)
        ok(len(P) == 1 and abs(P[0][0] - float(sol["x"])) < 0.03 and abs(P[0][1] - float(sol["y"])) < 0.03,
           f"{fig}: the point of intersection is marked at the solution", str(P))
        ok(all(on_line(l, P[0]) for l in L), f"{fig}: the marked point lies on every plotted line")
        if label:
            want = f"({sp.nsimplify(sol['x'])}, {sp.nsimplify(sol['y'])})"
            ok(want in [t for t, *_ in svg_texts(fig)], f"{fig}: the point is labelled {want}")
    if unit:
        to_xy, ux, uy = axis_scale(fig)
        ok(abs(ux - unit) < 0.05 and abs(uy - unit) < 0.05, f"{fig}: 1 cm to 1 unit on each axis",
           f"{ux:.2f}, {uy:.2f} px per unit; 1 cm = {unit:.2f} px")


# ================= Concept 1: is the point a solution? =================
for pre in ("d1", "y1"):
    (p1,) = points(V.get("q", pre + "p1"))
    (p2,) = points(V.get("q", pre + "p2"))
    (line,) = equations(V.get("q", pre + "l"))
    eqs = pair(pre)
    ok(any(sp.simplify(sp.expand(line[0] - line[1]) - sp.expand(e[0] - e[1])) == 0 for e in eqs),
       f"{pre}: the line of part a is the first equation of the pair")
    sub = lambda p: {"x": p[0], "y": p[1]}  # noqa: E731
    yesno(pre + "a", holds(line, sub(p1)))
    yesno(pre + "b", all(holds(e, sub(p1)) for e in eqs))
    yesno(pre + "c", all(holds(e, sub(p2)) for e in eqs))
    ok(holds(eqs[0], sub(p2)) and not holds(eqs[1], sub(p2)), f"{pre}c: the point is on the first line only (as the answer says)")

# ================= Concept 2: graphical method =================
for pre, fig in (("d2", "l1_d2a"), ("y2", "l1_y2a")):
    e1, = equations(V.get("q", pre + "l1"))
    e2, = equations(V.get("q", pre + "l2"))
    for i, e in ((1, e1), (2, e2)):
        got = points(V.get("k", f"{pre}i{i}"))
        ok(got == intercepts(e), f"{pre}i{i} intercepts", f"printed {got}, computed {intercepts(e)}")
    sol = check_pair(V, pre, [e1, e2], working=False)
    graph(fig, [e1, e2], sol)
for fig in ("l1_d2g", "l1_y2g"):
    axis_scale(fig)
    ok(not plotted_lines(fig), f"{fig}: blank grid")

# worked examples from the book, and the Year 8 7G figure
ex8 = equations(V.get("q", "ex8a")) + equations(V.get("q", "ex8b"))
sol8 = check_pair(V, "ex8", ex8)
graph("l1_ex8", ex8, sol8, label=False)
ok(sol8 == {"x": 4, "y": 1}, "Example 8: the book's estimate (4, 1) is exact")
check_pair(V, "ex21", pair("ex21"))
graph("l1_7g", [(y, 6 - 3 * x), (y, 2 * x + 1)], {"x": 1, "y": 3})
ok("\\((1,3)\\)" in L1 and "y=6-3x" in L1.replace(" ", "") and "y=2x+1" in L1.replace(" ", ""),
   "7G box: the example pair and point are printed")

# ================= Concept 3: substitution =================
for key in ("d3a", "d3b", "y3a", "y3b"):
    check_pair(V, key, pair(key))

# ================= Homework =================
for p in "abcdef":
    check_pair(V, "h1" + p, pair("h1" + p))
check_pair(V, "h2", pair("h2"))

# Exercise 3C Q9: point and line
book9 = {"a": True, "b": False, "c": True, "d": True, "e": True, "f": False}     # book answers (p. 509)
for p in "abcdef":
    q = V.get("q", "h3" + p)
    pt_tex, line_tex = maths(q)[0].split("\\qquad")
    (pt,) = points("\\(" + pt_tex + "\\)")
    (line,) = equations("\\(" + line_tex + "\\)")
    truth = holds(line, {"x": pt[0], "y": pt[1]})
    yesno("h3" + p, truth)
    ok(truth == book9[p], f"h3{p} agrees with the book's answer")

# Exercise 3C Q10 and Q11: graph, read off, confirm
eqs = pair("h4")
for i, e in ((1, eqs[0]), (2, eqs[1])):
    got = points(V.get("k", f"h4i{i}"))
    ok(got == intercepts(e), f"h4i{i} intercepts", f"printed {got}, computed {intercepts(e)}")
sol = check_pair(V, "h4", eqs)
ok(points(V.get("k", "h4b")) == [(sol["x"], sol["y"])], "h4b point read off")
graph("l1_q10a", eqs, sol)
graph("l1_g10", [], None, unit=CM)
book11 = {"a": (-1, 3), "b": (1, -2), "c": (-2, -1)}
for p in "abc":
    eqs = pair("h5" + p)
    sol = check_pair(V, "h5" + p, eqs)
    ok(points(V.get("k", f"h5{p}b")) == [(sol["x"], sol["y"])] and (sol["x"], sol["y"]) == book11[p],
       f"h5{p}b point read off (and the book's answer)")
    for i, e in ((1, eqs[0]), (2, eqs[1])):
        got = points(V.get("k", f"h5{p}i{i}"))
        e0 = sp.expand(e[0] - e[1])
        if e0.subs({x: 0, y: 0}) == 0:          # a line through the origin: two points on it
            ok(len(got) == 2 and (0, 0) in got and all(e0.subs({x: a, y: b}) == 0 for a, b in got),
               f"h5{p}i{i} two points on the line through O", str(got))
        else:
            ok(got == intercepts(e), f"h5{p}i{i} intercepts", f"printed {got}, computed {intercepts(e)}")
    graph(f"l1_q11{p}", eqs, sol)
graph("l1_g11", [], None, unit=CM)

for p in "abcdefgh":
    check_pair(V, "h6" + p, pair("h6" + p))

# Exercise 3C Q13: y = x/2 + c, four parallel lines
(fam,) = equations(V.get("q", "h7"))
c, m = sp.Symbol("c"), sp.Symbol("m")
L = plotted_lines("l1_q13a")
want = [(fam[0], fam[1].subs(c, cv)) for cv in (-2, -1, 1, 2)]
ok(len(L) == 4 and all(any(same_line(l, e) for l in L) for e in want), "l1_q13a: the four lines c = -2, -1, 1, 2")
grads = {round(-l[0] / l[1], 6) for l in L}
ok(grads == {0.5}, "l1_q13a: all four lines have gradient 1/2 (parallel)", str(grads))
t = re.sub(r"<[^>]+>", " ", V.get("k", "h7b")).lower()
ok("parallel" in t and "intercept" in t, "h7b: parallel; c is the y-intercept")
for cv in (-2, -1, 1, 2):
    ok(f"c = {cv}".replace("-", "-") in [s for s, *_ in svg_texts("l1_q13a")], f"l1_q13a: line c = {cv} labelled")

# Exercise 3C Q14: y - 2 = m(x - 1)
(fam,) = equations(V.get("q", "h8"))
want = [(fam[0], fam[1].subs(m, mv)) for mv in (1, 2, sp.Rational(-1, 2), 0)]
L = plotted_lines("l1_q14a")
ok(len(L) == 4 and all(any(same_line(l, e) for l in L) for e in want), "l1_q14a: the four lines m = 1, 2, -1/2, 0")
common = solve_pair(want[:2])
(pt,) = points(V.get("k", "h8b"))
ok((pt[0], pt[1]) == (common["x"], common["y"]) == (1, 2), "h8b: the common point", str(pt))
ok(sp.simplify((fam[0] - fam[1]).subs({x: pt[0], y: pt[1]})) == 0, "h8c: the point satisfies the equation for every m")
P = marked_points("l1_q14a")
ok(len(P) == 1 and all(on_line(l, P[0]) for l in L), "l1_q14a: the marked point is on all four lines")

# ================= Past papers =================
labels_l = re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</span>', L1)
labels_a = re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</span>', A1)
ok(labels_l == labels_a and len(labels_l) == 12, "past-paper labels identical in both files", f"{len(labels_l)} items")
marks = [int(n) for n in re.findall(r'<span class="mk">(\d+) marks?</span>', L1)]
total = int(re.search(r"<b>(\d+) marks</b>", L1).group(1))
mins = int(re.search(r"Suggested time: (\d+) minutes", L1).group(1))
ok(len(marks) == 12 and sum(marks) == total == 21, "mini exam marks add to the printed total", f"{marks} = {sum(marks)}")
ok(mins == 5 * round(1.5 * total / 5), "suggested time is 1.5 x marks to the nearest 5 minutes", f"{mins} min")
ok(15 <= total <= 22, "mini exam is 15-22 marks")


def mc(key, correct):
    t = re.sub(r"<[^>]+>", "", V.get("k", key) or "").strip()
    ok(t == correct, f"{key} key", f"printed {t}, computed {correct}")


# PP1: options are values of x and y
sol = check_pair(V, "pp1", pair("pp1"))
good = [L for L in "ABCD" if assignments(V.get("q", "pp1" + L)) == sol]
ok(len(good) == 1, "pp1: exactly one option is the solution", str(good))
mc("pp1", good[0] if good else "?")

# PP2: the statements
eqs = pair("pp2")
sol = check_pair(V, "pp2", eqs, working=False, check=False) if V.has("s", "pp2") else solve_pair(eqs)
fs = [sp.solve(e[0] - e[1], y)[0] for e in eqs]
grad = [sp.expand(f).coeff(x) for f in fs]
yint = [f.subs(x, 0) for f in fs]
opts = dict(re.findall(r"<b>\(([A-D])\)</b>&ensp;(.*?)</span>", L1[L1.index("PP 2</span>"):L1.index("PP 3</span>")]))
truth = {
    "A": all(v == tex2sym(maths(opts["A"])[-1]) for v in yint),
    "B": [(solve_pair(eqs)["x"], solve_pair(eqs)["y"])] == points(opts["B"]),
    "C": "different gradients" in opts["C"] and grad[0] != grad[1],
    "D": "same gradient" in opts["D"] and grad[0] == grad[1],
}
false = [k for k, v in truth.items() if not v]
ok(false == ["D"] or len(false) == 1, "pp2: exactly one statement is false", str(truth))
mc("pp2", false[0] if len(false) == 1 else "?")

# PP3: equations from the labels in the figure
labs = [t for t, *_ in svg_texts("l1_pp_g20") if "=" in t]
eqs = [tuple(tex2sym(side) for side in lab.replace(" ", "").split("=")) for lab in labs]
ok(len(eqs) == 2, "pp3: the figure shows two labelled lines", str(labs))
sol = check_pair(V, "pp3", eqs)
good = [L for L in "ABCD" if points(V.get("q", "pp3" + L)) == [(sol["x"], sol["y"])]]
ok(len(good) == 1, "pp3: exactly one option is the point", str(good))
mc("pp3", good[0] if good else "?")
# P in the sketch lies left of the y-axis and above the x-axis, as the solution does
T = {t: (px, py) for t, px, py in svg_texts("l1_pp_g20")}
ax = re.search(r'<line class="axy" x1="([\d.]+)"', svg("l1_pp_g20")).group(1)
ay = re.search(r'<line class="axx" x1="[\d.]+" y1="([\d.]+)"', svg("l1_pp_g20")).group(1)
ok(T["P"][0] < float(ax) and T["P"][1] < float(ay) and sol["x"] < 0 < sol["y"], "pp3: P is drawn in the second quadrant")


# PP4: read each sketch
def sketch_lines(fig):
    s = svg(fig)
    gx = float(re.search(r'<line class="axy" x1="([\d.]+)"', s).group(1))
    gy = float(re.search(r'<line class="axx" x1="[\d.]+" y1="([\d.]+)"', s).group(1))
    out = []
    for m_ in re.finditer(r'<line class="sk" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', s):
        x1, y1, x2, y2 = (float(v) for v in m_.groups())
        k = -(y2 - y1) / (x2 - x1)                     # gradient with y upwards
        b = -(y1 + (gx - x1) * (y2 - y1) / (x2 - x1) - gy)   # height of the y-intercept above O
        out.append((k, b, x1, y1, x2, y2))
    return out, gx, gy


eqs = pair("pp4")
sol = check_pair(V, "pp4", eqs)
fs = [sp.solve(e[0] - e[1], y)[0] for e in eqs]
need = sorted((float(sp.expand(f).coeff(x)), float(f.subs(x, 0))) for f in fs)   # (gradient, intercept)
fits = []
for L in "ABCD":
    lines_, gx, gy = sketch_lines(f"l1_pp_g23{L.lower()}")
    have = sorted((k, b) for k, b, *_ in lines_)
    signs = all((k > 0) == (n[0] > 0) and (b > 0) == (n[1] > 0) for (k, b), n in zip(have, need))
    (k1, b1, *_), (k2, b2, *_) = lines_
    xi = (b2 - b1) / (k1 - k2)
    yi = k1 * xi + b1
    quadrant = (xi > 0) == (sol["x"] > 0) and (yi > 0) == (sol["y"] > 0)
    if len(lines_) == 2 and signs and quadrant:
        fits.append(L)
ok(len(fits) == 1, "pp4: exactly one sketch has the right gradients, intercepts and meeting point", str(fits))
mc("pp4", fits[0] if fits else "?")

for key in ("pp5", "pp6", "pp7", "pp8", "pp9", "pp10"):
    check_pair(V, key, pair(key))
check_pair(V, "pp11", equations(V.get("q", "pp11a")) + equations(V.get("q", "pp11b")))
K, = equations(V.get("q", "pp12K"))
Lq, = equations(V.get("q", "pp12L"))
B = (0, sp.solve((K[0] - K[1]).subs(x, 0), y)[0])
ok(points(V.get("k", "pp12B")) == [B], "pp12B: K meets the y-axis at B", str(B))
check_pair(V, "pp12", [K, Lq])
ok(holds(Lq, {"x": -6, "y": 4}) and sp.expand(Lq[1]).coeff(x) == 3, "pp12: the supplied L has gradient 3 through A(-6, 4)")
AB = equations(V.get("q", "pp11a"))[0]
ok(holds(AB, {"x": 1, "y": -22}) and holds(AB, {"x": 5, "y": -2}), "pp11: the supplied AB passes through A(1, -22) and B(5, -2)")

finish([V])
