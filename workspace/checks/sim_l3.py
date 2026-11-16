r"""Check of Lesson 3 (problem solving) and the chapter review, tied to the printed HTML and the box plot.

Reads build/sim/l3.html (problems: <span data-q>) and a_l3.html (answers: data-d definitions, data-p the
printed pair of equations, data-w working, data-s solution, data-c check, data-k answer in words).

For every word problem:
  * the numbers of the story are read from the PRINTED problem text (digits, $ and %, fractions, number
    words such as "twice", "one-third", "twenty-four", "Ten thousand"); the numbers the model uses must
    occur in that text, in order;
  * a model of the story builds the expected pair of equations from those numbers, in the printed
    pronumerals; each printed equation must be the same as one model equation (up to a nonzero factor)
    and the two printed equations must cover both model equations;
  * each pronumeral must be defined in the printed definition with the quantity it stands for;
  * the printed pair is re-solved with sympy: printed solution, working lines and check as in L1 and L2;
  * the answer in words must contain the requested values (with units changed where the question asks).
The box-plot item reads the five-number summaries from svg/l3_bp.svg and its axis labels.
Algebraic review items are re-solved; the MC keys are recomputed (Scots 2020 from the options; Pymble
2021 Q12 by testing each printed line of the given working in order). Labels must agree in both files,
and the mini-exam marks must add to the printed total (15-22) with time 1.5 x marks.
Every key must be found once and checked. Exit status 1 on any failure.
Run: python3 -I workspace/checks/sim_l3.py
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_common import (Values, ok, finish, check_pair, equations, points, holds, assignments,  # noqa: E402
                        solve_pair, read, maths, story_numbers, subsequence, same_equation, plain_text, svg,
                        svg_texts)
import sympy as sp  # noqa: E402

V = Values(["l3.html", "a_l3.html"])
L3, A3 = read("l3.html"), read("a_l3.html")
S = {c: sp.Symbol(c) for c in "abcdfghjklmnpqrstuvwxyFGJKL"}
x, y = S["x"], S["y"]
R = sp.Rational


def bp_fraction(subject, v, side):
    """Fraction of a box plot above or below the value v, read from svg/l3_bp.svg (v must be a quartile)."""
    for m in re.finditer(r'<g class="bp" data-five="([^"]+)">', svg("l3_bp")):
        five = [float(t) for t in m.group(1).split()]
        if (subject == "French") == (m.start() == svg("l3_bp").index('<g class="bp"')):
            k = five.index(float(v))
            assert k in (1, 2, 3), "value is not a quartile"
            below = R(k, 4)
            return below if side == "below" else 1 - below
    raise KeyError(subject)


# key: (numbers used, in the order they appear in the story; model(n, S) -> two equations (lhs, rhs);
#       definitions {pronumeral: keyword}; answer values(sol) -> values that the sentence must contain)
P = {
    "d1a": ([50, 14], lambda n: [(x + y, n[0]), (x - y, n[1])], {"x": "larger", "y": "smaller"}, None),
    "d1b": ([4, 3, 20, 71], lambda n: [(S["m"] + S["s"], n[2]), (n[0] * S["m"] + n[1] * S["s"], n[3])],
            {"m": "muffin", "s": "scone"}, None),
    "d1c": ([4, 5, 2], lambda n: [(S["a"], S["b"] + n[0]), (S["a"] - n[1], n[2] * (S["b"] - n[1]))],
            {"a": "Ali", "b": "Ben"}, None),
    "y1a": ([41, 9], lambda n: [(x + y, n[0]), (x - y, n[1])], {"x": "larger", "y": "smaller"}, None),
    "y1b": ([2, 5, 30, 93], lambda n: [(S["p"] + S["n"], n[2]), (n[0] * S["p"] + n[1] * S["n"], n[3])],
            {"p": "pen", "n": "notebook"}, None),
    "y1c": ([6, 4, 3], lambda n: [(S["k"], S["l"] + n[0]), (S["k"] - n[1], n[2] * (S["l"] - n[1]))],
            {"k": "Kim", "l": "Lee"}, None),
    "ex14": ([60, 2], lambda n: [(S["l"] + S["j"], n[0]), (S["j"], n[1] * S["l"])], {"l": "Luke", "j": "Jane"}, None),
    "d2a": ([5, 2, 150, 480], lambda n: [(S["a"] + S["c"], n[2]), (n[0] * S["a"] + n[1] * S["c"], n[3])],
            {"a": "adult", "c": "child"}, None),
    "d2b": ([31, 4, 2], lambda n: [(S["m"] + S["s"], n[0]), (S["m"] + n[1], n[2] * (S["s"] + n[1]))],
            {"m": "Mia", "s": "Sam"}, None),
    "y2a": ([6, 10, 40, 316], lambda n: [(S["s"] + S["l"], n[2]), (n[0] * S["s"] + n[1] * S["l"], n[3])],
            {"s": "small", "l": "large"}, None),
    "y2b": ([38, 3, 3], lambda n: [(S["t"] + S["a"], n[0]), (S["t"] - n[1], n[2] * (S["a"] - n[1]))],
            {"t": "Tom", "a": "Ann"}, None),
    "w1": ([112, 22], lambda n: [(x + y, n[0]), (x - y, n[1])], {"x": "larger", "y": "smaller"}, None),
    "w2": ([9, 83], lambda n: [(S["w"] - S["l"], n[0]), (S["w"] + S["l"], n[1])], {"w": "winning", "l": "losing"}, None),
    "w3": ([28, 6, 3], lambda n: [(S["f"], S["d"] + n[0]), (S["f"] + n[1], n[2] * (S["d"] + n[1]))],
           {"f": "father", "d": "daughter"}, None),
    "w4": ([2, 5, 101, 331], lambda n: [(x + y, n[2]), (n[0] * x + n[1] * y, n[3])], {"x": "$2", "y": "$5"}, None),
    "b6a": ([16, 90], lambda n: [(x - y, n[0]), (x + y, n[1])], {"x": "larger", "y": "smaller"}, None),
    "b6b": ([75, 4], lambda n: [(S["p"] + S["q"], n[0]), (S["p"], n[1] * S["q"])], {"p": "pen", "q": "pencil"}, None),
    "b6c": ([7, 2, 4, 5, 4, R(44, 10)], lambda n: [(n[0] * S["a"] + n[1] * S["r"], 100 * n[2]),
                                                    (n[3] * S["a"] + n[4] * S["r"], 100 * n[5])],
            {"a": "apple", "r": "orange"}, None),
    "b6d": ([2, 8, 3, 418], lambda n: [(S["a"], n[0] * S["c"]), (n[1] * S["a"] + n[2] * S["c"], n[3])],
            {"a": "adult", "c": "children"}, None),
    "b6e": ([3, 12, 2], lambda n: [(S["m"], n[0] * S["s"]), (S["m"] + n[1], n[2] * (S["s"] + n[1]))],
            {"m": "man", "s": "son"}, None),
    "b6f": ([357, 21], lambda n: [(S["f"] + S["g"], n[0]), (S["f"] - S["g"], n[1])], {"f": "for", "g": "against"}, None),
    "w5": ([4, 20, R(1, 3), 2], lambda n: [(n[0] * S["b"] - S["a"], n[1]), (S["b"] - n[2] * S["a"], n[3])],
           {"b": "Brian", "a": "Andrew"}, None),
    "w6": ([150, 8, 5, 3, 2, 2], lambda n: [(n[1] * x + n[2] * y, n[0]), (n[3] * x - n[4] * y, n[5])],
           {"x": "8 pieces", "y": "5 pieces"}, None),
    "w7": ([1, 110, 60, 50, 100], lambda n: [(n[1] * S["s"] + n[2] * S["j"], 1000 * n[0]),
                                              (n[3] * S["s"] + n[4] * S["j"], 1000 * n[0])],
           {"s": "standard", "j": "jumbo"}, None),
    "w10": ([432, 80, 32, 6], lambda n: [(S["h"] + S["t"], n[3]), (n[1] * S["h"] + n[2] * S["t"], n[0])],
            {"h": "highway", "t": "town"}, lambda s: [s["h"]]),
    "w12": ([52, 36, 200, 40], lambda n: [(x + y, n[2]), (n[0] * x / 100 + n[1] * y / 100, n[3] * n[2] / 100)],
            {"x": "52%", "y": "36%"}, None),
    "b8a": ([320, 20, 10, 23], lambda n: [(n[1] * S["t"] + n[2] * S["n"], n[0]), (S["t"] + S["n"], n[3])],
            {"t": "$20", "n": "$10"}, None),
    "b8b": ([16, 2, 8], lambda n: [(n[1] * (S["u"] + S["v"]), n[0]), (n[2] * (S["u"] - S["v"]), n[0])],
            {"u": "faster", "v": "slower"}, None),
    "w9": ([R(15, 2), R(100, 3), 100, 50], lambda n: [(x, y), (n[0] * n[1] / 100 - n[1] / 100 * x + n[2] / 100 * y,
                                                             n[3] / 100 * n[0])],
           {"x": "drained", "y": "added"}, lambda s: [s["x"]]),
    "w11": ([8, 80, 10, 110], lambda n: [(S["d"], n[1] * S["t"]), (S["d"], n[3] * (S["t"] - (n[2] - n[0])))],
            {"t": "hours after 8", "d": "distance"}, "time"),
    "w13": ([45, 840, R(3, 4)], lambda n: [(n[0] * (S["u"] + S["v"]) / 60, n[1]), (S["u"], n[2] * S["v"])],
            {"u": "first", "v": "other"}, None),
    "w15": ([1, R(1, 5), 1, R(1, 7)], lambda n: [(S["a"] + n[0], n[1] * S["b"]), (S["a"], n[3] * (S["b"] - n[2]))],
            {}, lambda s: [s["a"] / s["b"]]),
    "w16": ([1, R(4, 5), 1, R(5, 2)], lambda n: [((S["v"] + n[0]) * n[1], S["v"]),
                                                  (sp.expand((S["v"] - n[2]) * (S["t"] + n[3]) - S["v"] * S["t"]), 0)],
            {"v": "speed", "t": "time"}, lambda s: [s["v"] * s["t"]]),
    "h17": ([30, R(1, 3), 30, R(3, 10)], lambda n: [(S["r"] + n[0], n[1] * (S["r"] + y + n[0])),
                                                    (S["r"] + n[0], n[3] * (S["r"] + y + n[0] + n[2]))],
            {"r": "red", "y": "yellow"}, lambda s: [s["r"] / (s["r"] + s["y"])]),
    "h18": ([2, 70, 5, 80], lambda n: [(bp_fraction("Geography", n[1], "above") * S["G"],
                                        n[0] * bp_fraction("French", n[1], "above") * S["F"]),
                                       (bp_fraction("French", n[3], "below") * S["F"],
                                        bp_fraction("Geography", n[3], "below") * S["G"] + n[2])],
            {"F": "French", "G": "Geography"}, lambda s: [s["G"]]),
    "pp1": ([2, 3, 5, 70], lambda n: [(x - y, n[0]), (n[1] * x + n[2] * y, n[3])], {"x": "hot chocolate", "y": "bubble tea"}, None),
    "pp2": ([2, 3, 100, 242], lambda n: [(S["d"] + S["w"], n[2]), (n[0] * S["d"] + n[1] * S["w"], n[3])],
            {"d": "drinks", "w": "wedges"}, None),
    "pp3": ([20, 2, 3, 52], lambda n: [(x + y, n[0]), (n[1] * x + n[2] * y, n[3])], {"x": "2-mark", "y": "3-mark"}, None),
    "pp4": ([3, 2, 150], lambda n: [(2 * x + 2 * y, n[2]), (n[1] * y, n[0] * x)], {"x": "shorter", "y": "longer"}, None),
    "pp5": ([6, 3, 3, 2], lambda n: [(S["L"] - n[0], n[1] * (S["K"] - n[0])), (S["L"] + n[2], n[3] * (S["K"] + n[2]))],
            {"L": "Lydia", "K": "Keiko"}, None),
    "pp6": ([3, 7, 12, 5, 9], lambda n: [(n[1] * S["L"], n[0] * S["J"]), (n[4] * (S["L"] + n[2]), n[3] * (S["J"] + n[2]))],
            {"L": "Lynne", "J": "Jeff"}, None),
    "pp7": ([1, 24, 6, 2], lambda n: [(sp.expand((x + n[0]) * (S["t"] - n[1] / 60) - x * S["t"]), 0),
                                      (sp.expand((x + n[2]) * (S["t"] - n[3]) - x * S["t"]), 0)],
            {"x": "speed", "t": "time"}, lambda s: [s["x"] * s["t"]]),
    "r4": ([10000, 80, 60, 640000], lambda n: [(S["a"] + S["b"], n[0]), (n[1] * S["a"] + n[2] * S["b"], n[3])],
           {"a": "$80", "b": "$60"}, None),
    "r8": ([6, 7, 250, 13, 11, 460], lambda n: [(n[0] * S["h"] + n[1] * S["c"], n[2]),
                                                (n[4] * S["h"] + n[3] * S["c"], n[5])],
           {"h": "horse", "c": "cow"}, None),
}

for key, (nums, model, defs, wants) in P.items():
    story = V.get("q", key) or ""
    have = story_numbers(story)
    ok(subsequence([sp.nsimplify(v) for v in nums], have), f"{key}: the model's numbers occur in the printed story",
       f"model {nums}; story {have}")
    try:
        expect = model([sp.nsimplify(v) for v in nums])
    except (ValueError, KeyError, AssertionError) as err:
        ok(False, f"{key}: the story model can be built", repr(err))
        continue
    printed = equations(V.get("p", key))
    ok(len(printed) == 2, f"{key}: two printed equations", str(printed))
    used = set()
    for e in printed:
        hit = [i for i, m in enumerate(expect) if same_equation(e, m)]
        ok(len(hit) >= 1, f"{key}: printed {e[0]} = {e[1]} matches the story", f"model {expect}")
        used.update(hit)
    ok(used == {0, 1}, f"{key}: the printed pair covers both facts of the story")
    # definitions
    d = plain_text(V.get("d", key) or "") if V.has("d", key) else ""
    pos = {sym: [m.start() for m in re.finditer(r"(?<![A-Za-z$])%s(?![A-Za-z])" % sym, d)] for sym in defs}
    for sym, word in defs.items():
        if not pos[sym]:
            ok(False, f"{key}: {sym} is defined", d[:90])
            continue
        start = pos[sym][0]
        later = [p[0] for s2, p in pos.items() if s2 != sym and p and p[0] > start]
        window = d[start:min(later) if later else len(d)]
        ok(word.lower() in window.lower(), f"{key}: {sym} is defined as the {word}", window.strip()[:70])
    # solve
    sol = check_pair(V, key, printed)
    if sol is None:
        continue
    ok(all(holds(e, sol) for e in expect), f"{key}: the solution satisfies the story's equations")
    # answer in words
    ans = V.get("k", key) or ""
    got = story_numbers(ans)
    if wants == "time":
        t = sol["t"]
        mins = int(round((8 + t) * 60))
        hh, mm = divmod(mins, 60)
        clock = f"{hh - 12 if hh > 12 else hh}:{mm:02d} {'p.m.' if hh >= 12 else 'a.m.'}"
        ok(clock in plain_text(ans), f"{key}: answer time {clock}", plain_text(ans))
        continue
    need = wants(sol) if wants else list(sol.values())
    ok(all(any(sp.simplify(sp.nsimplify(g) - v) == 0 for g in got) for v in need), f"{key}: the answer in words",
       f"needs {need}; printed numbers {got}")

# book answers (Year 11 Advanced answers PDF 518) and catalogue answers
book = {"b6a": {53, 37}, "b6b": {60, 15}, "b6c": {40, 60}, "b6d": {44, 22}, "b6e": {36, 12}, "b6f": {189, 168},
        "b8a": {9, 14}, "b8b": {5, 3}, "pp1": {10, 8}, "pp2": {58, 42}, "pp3": {8, 12}, "pp4": {30, 45},
        "pp5": {33, 15}, "pp6": {18, 42}, "pp7": {24, 10}, "h17": {60, 180}, "h18": {60, 80}}
for key, want in book.items():
    sol = solve_pair(equations(V.d["p"][key][0]))
    ok(set(sol.values()) == want, f"{key}: agrees with the book or the school's answer", str(sol))

# ================= Chapter review: algebra items =================
for key in ("r3", "r5", "r6", "r7", "r9", "r10", "r11", "r12"):
    eqs = equations(V.get("q", key))
    ok(len(eqs) == 2, f"{key}: two equations printed")
    check_pair(V, key, eqs)
sol = check_pair(V, "r1", equations(V.get("q", "r1")))
good = [L for L in "ABCD" if sp.nsimplify(maths(V.get("q", "r1" + L))[0]) == sol["y"]]
ok(len(good) == 1, "r1: exactly one option is y", str(good))
ok(re.sub(r"<[^>]+>", "", V.get("k", "r1")).strip() == (good[0] if good else "?"), "r1 key")

# Pymble 2021 Q12: test each printed line of the given working in order
e1, = equations(V.get("q", "r2a"))
e2, = equations(V.get("q", "r2b"))
l1, = equations(V.get("q", "r2L1"))
l2, = equations(V.get("q", "r2L2"))
l3, = equations(V.get("q", "r2L3"))
l4, = equations(V.get("q", "r2L4"))
E = lambda e: sp.expand(e[0] - e[1])  # noqa: E731
okline = {
    "A": sp.expand(E(l1) - 2 * E(e1)) == 0,
    "B": sp.expand(E(l2) - (E(e2) + E(l1))) == 0,
    "C": sp.solve(E(l2), x) == sp.solve(E(l3), x),
    "D": sp.expand(E(l4) - E(e1).subs(x, sp.solve(E(l3), x)[0])) == 0,
}
first_bad = next((k for k in "ABCD" if not okline[k]), "?")
ok(re.sub(r"<[^>]+>", "", V.get("k", "r2")).strip() == first_bad, "r2: the first wrong line", str(okline))
true = solve_pair([e1, e2])
c = V.get("c", "r2")
ok(all(holds(e, true) for e in equations(c)) and len(equations(c)) >= 2, "r2: the corrected solution is checked", str(true))

# Sydney Boys 2022 Q18(e)
lq, = equations(V.get("q", "r13l"))
cq, = equations(V.get("q", "r13c"))
sol = check_pair(V, "r13", [lq, cq], working=False)
wl = equations(V.get("w", "r13"))
sub_a = dict(sol, a=sol["y"])                         # T = (5 - 2a, a), so a is the y-coordinate
ok(len(wl) >= 3 and all(holds(e, sub_a) for e in wl), "r13: every working line holds (with a = y of T)",
   "; ".join(f"{l} = {r}" for l, r in wl if not holds((l, r), sub_a)))
a_ = sp.Symbol("a")
ok(sp.expand(E(lq).subs({x: 5 - 2 * a_, y: a_})) == 0, "r13: (5 - 2a, a) lies on l for every a")
ok(holds(lq, {"x": -1, "y": 3}) and sp.expand(E(lq)).coeff(x) * sp.expand(E(cq)).coeff(x)
   + sp.expand(E(lq)).coeff(y) * sp.expand(E(cq)).coeff(y) == 0 and holds(cq, {"x": 1, "y": -2}),
   "r13: l passes through A(-1, 3); CB passes through B(1, -2) and is perpendicular to l")
T = {t: (px, py) for t, px, py in svg_texts("r_sb22")}
ok(set("ABCT") <= set(T), "r_sb22: the figure labels A, B, C and T")

# ================= labels, marks, time =================
labels_l = re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</span>', L3)
labels_a = re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</span>', A3)
ok(labels_l == labels_a and len(labels_l) == 7, "past-paper labels identical in both files", f"{len(labels_l)}")
lab = r'<span class="muted small">([^<]*(?:School|College)[^<]*)</span>'
ok(re.findall(lab, L3) == re.findall(lab, A3) and len(re.findall(lab, L3)) == 13,
   "Hard-band and review school labels identical in both files", str(len(re.findall(lab, L3))))
marks = [int(n) for n in re.findall(r'<span class="mk">(\d+) marks?</span>', L3)]
subs = re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', L3, re.S)
total = int(re.search(r"<b>(\d+) marks</b>", L3).group(1))
mins = int(re.search(r"Suggested time: (\d+) minutes", L3).group(1))
ok(sum(marks) == total and 15 <= total <= 22, "mini exam marks add to the printed total (15-22)", f"{marks} = {sum(marks)}")
ok(sum(int(s) for s in subs) == marks[0] + marks[1], "PP 1 and PP 2 part marks add to their totals", str(subs))
ok(mins == 5 * round(1.5 * total / 5), "suggested time is 1.5 x marks to the nearest 5 minutes", f"{mins} min")

finish([V])
