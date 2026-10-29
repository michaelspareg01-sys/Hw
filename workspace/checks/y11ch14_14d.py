"""Check of Lesson 14D (Ordered selections with identical elements), tied to the printed HTML.

Reads the printed answers from workspace/build/y11ch14/a_14d.html (lesson
examples C1-C3, textbook homework, past-paper worked solutions) and the printed
results in the concept boxes and worked examples of l14d.html. In a template
'@' marks the printed value; each template must match exactly once in its
block, otherwise the item FAILS. Printed LaTeX is converted to an exact value
(fractions.Fraction; \\times, +, -, powers, factorials, \\dfrac) and compared
with a count made independently from the question by brute-force enumeration:
the distinct arrangements of the actual letters are listed one by one (a
next-permutation generator over the sorted multiset, or a set of
itertools.permutations), and conditions are tested on each arrangement. Grid
paths are counted on the grid read back from the built SVG figures (the line
segments, the dots and their labels), so the figure, the question and the
answer are tied together. Where a full enumeration is too large (Q10 and Q17)
the count is made by enumerating the two independent pieces, and that method
is first checked against a full enumeration on a smaller case.

For every printed chain such as "\\dfrac{8!}{3!\\times5!}=56" EVERY
'='-separated piece must equal the computed count, so a wrong factor in the
working fails as well as a wrong final answer. The terms of printed sums are
checked one by one against the counts of each case. Key data of each question
as printed in l14d.html (words, numbers) are re-read so that the truths encode
the printed questions. Past-paper structure is checked too: marks add to the
intro total, time is 1.5 x marks rounded to the nearest 5 minutes (halves up),
numbering, source labels identical in both files, one hint each, part marks,
and each MC letter is the option equal to the count.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_14d.py
"""
import os
import re
import string
import sys
from fractions import Fraction as Fr
from itertools import permutations, product, combinations
from math import factorial, perm, log10

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH14_SRC", os.path.join(HERE, "..", "build", "y11ch14"))   # override only for mutation tests
FAILS = []
COUNT = [0]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    COUNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label + "  " + detail)
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- LaTeX -> exact Python
VARS = "nrabck"


def _arg(s, i):
    if s[i] == "{":
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(s[j], 0)
            if depth == 0:
                return s[i + 1:j], j + 1
            j += 1
    return s[i], i + 1


def _conv(s):
    out, i = [], 0
    while i < len(s):
        if s.startswith("{}^", i):                       # {}^{n}\mathrm{P}_{r}  or  {}^{n}P_{r}
            top, i = _arg(s, i + 3)
            if s.startswith("\\mathrm{P}", i):
                i += len("\\mathrm{P}")
            elif s[i] == "P":
                i += 1
            else:
                raise ValueError(f"expected P after {{}}^ in {s!r}")
            if s[i] != "_":
                raise ValueError(f"expected subscript in {s!r}")
            sub, i = _arg(s, i + 1)
            out.append(f"PP(({_conv(top)}),({_conv(sub)}))")
        elif s.startswith(("\\dfrac", "\\tfrac", "\\frac"), i):
            i = s.index("frac", i) + 4
            a, i = _arg(s, i)
            b, i = _arg(s, i)
            out.append(f"(({_conv(a)})/({_conv(b)}))")
        elif s[i] == "\\":
            raise ValueError(f"unknown macro in {s!r}")
        elif s[i] == "{":
            out.append("(")
            i += 1
        elif s[i] == "}":
            out.append(")")
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def _clean(tex):
    s = tex
    for a in ("\\left", "\\right", "\\displaystyle", "&thinsp;", "&nbsp;"):
        s = s.replace(a, "")
    s = re.sub(r"\\text\{[^}]*\}", "", s)
    s = re.sub(r"\\[,!;]|\\ |\s|&", "", s)
    s = s.replace("\\times", "*").replace("\\cdot", "*")
    return s


def tex_to_py(tex):
    s = _conv(_clean(tex))
    toks = re.findall(r"PP|\d+|[A-Za-z]|\S", s)
    out = []
    for t in toks:                                       # factorial: wrap the operand on its left
        if t != "!":
            out.append(t)
            continue
        if out and out[-1] == ")":
            depth, j = 0, len(out) - 1
            while True:
                depth += {")": 1, "(": -1}.get(out[j], 0)
                if depth == 0:
                    break
                j -= 1
            if j > 0 and out[j - 1] == "PP":
                j -= 1
            grp = out[j:]
            del out[j:]
            out += ["F", "("] + grp + [")"]
        elif out and re.fullmatch(r"\d+|[" + VARS + "]", out[-1]):
            v = out.pop()
            out += ["F", "(", v, ")"]
        else:
            raise ValueError(f"factorial with no operand in {tex!r}")
    res, prev = [], None
    for t in out:
        if prev is not None:
            left = re.fullmatch(r"\d+|[" + VARS + r"]|\)", prev)
            right = re.fullmatch(r"\d+|[" + VARS + r"F]|PP|\(", t)
            if left and right:
                res.append("*")
        if re.fullmatch(r"[A-Za-z]", t) and t not in VARS + "F":
            raise ValueError(f"unknown letter {t!r} in {tex!r}")
        res.append(f"Fr({t})" if t.isdigit() else ("**" if t == "^" else t))
        prev = t
    return "".join(res)


def fact(v):
    v = Fr(v)
    if v.denominator != 1 or v < 0:
        raise ValueError(f"factorial of {v}")
    return Fr(factorial(int(v)))


def P(n, r):
    n, r = Fr(n), Fr(r)
    if n.denominator != 1 or r.denominator != 1 or not 0 <= r <= n:
        raise ValueError(f"P({n},{r}) undefined")
    return Fr(perm(int(n), int(r)))


def tex_eval(tex, **var):
    env = {"Fr": Fr, "F": fact, "PP": P, "__builtins__": {}}
    env.update({k: Fr(v) for k, v in var.items()})
    return Fr(eval(tex_to_py(tex), env))


from collections import Counter
from math import comb, prod


# ---------------------------------------------------------------- enumeration helpers
def distinct(word):
    """Every distinct arrangement of the multiset of letters, generated one by one."""
    a = sorted(word)
    n = len(a)
    while True:
        yield tuple(a)
        i = n - 2
        while i >= 0 and a[i] >= a[i + 1]:
            i -= 1
        if i < 0:
            return
        j = n - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
        a[i + 1:] = reversed(a[i + 1:])


def count(it, cond=lambda x: True):
    return sum(1 for x in it if cond(x))


def ndist(word, cond=lambda x: True):
    return count(distinct(word), cond)


report(ndist("AABC") == len(set(permutations("AABC"))) == 12 and ndist("SOCKS") == len(set(permutations("SOCKS"))),
       "generator", "next-permutation generator agrees with set(itertools.permutations) on AABC and SOCKS")
VOW = set("AEIOU")


def together(p, c):
    i = [k for k, x in enumerate(p) if x == c]
    return i[-1] - i[0] == len(i) - 1


def block(p, cs):
    i = sorted(k for k, x in enumerate(p) if x in cs)
    return i[-1] - i[0] == len(i) - 1


def adjacent(p, x, y):
    return abs(p.index(x) - p.index(y)) == 1


def roundhalf5(x):
    return 5 * int(Fr(x) / 5 + Fr(1, 2))


# ---------------------------------------------------------------- grids read from the SVG figures
def svg_grid(name):
    svg = read(os.path.join("svg", name + ".svg"))
    segs = [tuple(float(v) for v in m) for m in re.findall(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg)]
    dots = [(float(x), float(y)) for x, y in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
    labels = re.findall(r'<circle[^>]*/><text[^>]*>([^<]+)</text>', svg)
    xs = sorted({s[0] for s in segs} | {s[2] for s in segs})
    cell = min(b - a for a, b in zip(xs, xs[1:]))
    edges = set()
    for x1, y1, x2, y2 in segs:                         # split each grid line into unit edges
        k = round(max(abs(x2 - x1), abs(y2 - y1)) / cell)
        pts = [(round(x1 + (x2 - x1) * t / k), round(y1 + (y2 - y1) * t / k)) for t in range(k + 1)]
        edges |= {frozenset(e) for e in zip(pts, pts[1:])}
    pts = dict(zip(labels, [(round(x), round(y)) for x, y in dots]))
    path = re.search(r'<path d="M([^"]+)"', svg)
    route = [tuple(round(float(v)) for v in q.split(",")) for q in path.group(1).split(" L")] if path else None
    return edges, pts, round(cell), route


def paths(name, start, end, dirs, via=None):
    """Monotone paths along the drawn edges. dirs: 'RD' (right or down) or 'RU' (right or up), screen y down."""
    edges, pts, c, _ = svg_grid(name)
    step = {"R": (c, 0), "D": (0, c), "U": (0, -c)}
    A, B = pts[start], pts[end]
    memo = {}

    def walk(p, seen):
        if p == B:
            return 1 if via is None or seen else 0
        key = (p, seen)
        if key not in memo:
            tot = 0
            for d in dirs:
                q = (p[0] + step[d][0], p[1] + step[d][1])
                if frozenset((p, q)) in edges:
                    tot += walk(q, seen or (via is not None and q == pts[via]))
            memo[key] = tot
        return memo[key]
    return walk(A, via is not None and A == pts.get(via))


def grid_size(name):
    edges, pts, c, _ = svg_grid(name)
    xs = {p[0] for e in edges for p in e}
    ys = {p[1] for e in edges for p in e}
    return (max(xs) - min(xs)) // c, (max(ys) - min(ys)) // c


# ---------------------------------------------------------------- blocks
ANS = read("a_14d.html")
LES = read("l14d.html")
HEAD = "{{ahead:Lesson 14D | Ordered selections with identical elements}}"


def ans_blocks(text):
    return {an.strip(): ab.replace('<span style="white-space:nowrap">', "").replace("</span>", "")
            for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S)}


A = ans_blocks(ANS)
sec = ANS.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_14d.html")
report(ANS.count(HEAD) == 2 and ANS.startswith(HEAD) and sec[0].rstrip().endswith(HEAD), "answers headings",
       "the ahead line opens the file and precedes the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}
pps = LES.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l14d.html")
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
HW = LES.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
Q = {int(n): b for n, b in re.findall(r'<div class="q"><span class="q-num">(\d+)</span><div class="q-body">(.*?)(?=<div class="q"><span class="q-num">|$)', HW, re.S)}


def les_block(start, end):
    i = LES.find(start)
    j = LES.find(end, i + 1)
    if i < 0 or j < 0:
        raise LookupError(f"lesson block {start!r} not found")
    return LES[i:j]


def concept(k):
    nxt = f"<!-- ============ Concept {k + 1}" if k < 3 else "<!-- ============ Homework"
    return les_block(f"<!-- ============ Concept {k} ", nxt)


def ex_block(cblock, kind):
    m = re.findall(r'<div class="ex ' + kind + r'">(.*?)\{\{work:\d+\}\}', cblock, re.S)
    if len(m) != 1:
        raise LookupError(f"{len(m)} '{kind}' blocks")
    return m[0]


def find(block, template):
    before, after = template.split("@")
    found = re.findall(re.escape(before) + r"(.+?)" + re.escape(after), block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times: {template!r}")
    return found[0]


def chain_ok(tex, truth, **var):
    pieces = [p for p in tex.split("=") if p.strip()]
    vals = [tex_eval(p, **var) for p in pieces]
    return all(v == Fr(truth) for v in vals), vals


def check(label, block, template, truth):
    try:
        tex = find(block, template)
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex.strip()} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def aligned(label, block, template, truth):
    try:
        tex = find(block, template)
        tex = tex.replace("\\\\", "").replace("&", "").strip().rstrip(".").rstrip(",")
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def terms(label, block, template, truths, total):
    """A printed sum such as 180+120+120=420: each term is checked against its case count."""
    try:
        tex = find(block, template)
        pieces = tex.split("=")
        ts = re.findall(r"[+-]?[^+-]+", pieces[0].replace("\\,", ""))
        vals = [abs(tex_eval(t.lstrip("+"))) for t in ts]
        ok = vals == [Fr(t) for t in truths] and all(tex_eval(p) == total for p in pieces)
        report(ok, label, f"printed {tex} -> terms {[str(v) for v in vals]}, computed terms {truths}, total {total}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def has(label, block, phrase):
    n = block.count(phrase)
    report(n >= 1, label, f"question text contains {phrase!r}" + ("" if n else "  (NOT FOUND: question changed?)"))


def parts(block, letters):
    out = {}
    for i, L in enumerate(letters):
        a = block.index(f"<b>{L}</b>")
        b = block.index(f"<b>{letters[i + 1]}</b>", a) if i + 1 < len(letters) else len(block)
        out[L] = block[a + len(f"<b>{L}</b>"):b]
    return out


def maths(s):
    return re.findall(r"\\\((.+?)\\\)", s, re.S)


def first_math(label, s, truth, **var):
    try:
        tex = maths(s)[0]
        ok, vals = chain_ok(tex, truth, **var)
        report(ok, label, f"printed {tex} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def omit_cases(word, k):
    """{letter omitted: number of k-letter words} for the k-letter words of word (k = len - 1)."""
    out = {}
    for x in sorted(set(word)):
        rest = list(word)
        rest.remove(x)
        out[x] = ndist(rest)
    total = len(set(permutations(word, k)))
    return out, total


# ================================================================ Concept 1
c1 = concept(1)
pbox = les_block('<div class="bt">Counting with identical elements</div>', "Box 10")
pr = ndist("PRESSES")
aligned("L PRESSES 7!", pbox, r"we would conclude that</p>" + "\n" + r"\[\text{number of ways}=@\]", len(list(permutations("PRESSES"))))
check("L PRESSES", pbox, r"Taking account of both overcountings,</p>" + "\n" + r"\[\text{number of ways}=@.\]", pr)
check("L 2!", pbox, r"But we have <i>overcounted by a factor of</i> \(@\), because the Es", len(list(permutations("EE"))))
check("L 3!", pbox, r"We have also <i>overcounted by a factor of</i> \(@\), because the three", len(list(permutations("SSS"))))
# Box 10 formula: the printed formula with the r_i read as numbers, against enumeration for several words
try:
    f10 = find(c1, r"\[\text{number of words}=@.\]")
    ok = f10 == r"\dfrac{n!}{r_1!\times r_2!\times\cdots\times r_k!}"
    bad = []
    for w in ("PRESSES", "SOCKS", "TATTOO", "BANANA", "AABBBC"):
        c = Counter(w).values()
        if factorial(len(w)) // prod(factorial(v) for v in c) != ndist(w):
            bad.append(w)
    report(ok and not bad, "L Box 10", f"printed {f10}; n!/(r1! ... rk!) = enumeration for PRESSES, SOCKS, TATTOO, BANANA, AABBBC")
except Exception as ex:
    report(False, "L Box 10", f"ERROR {ex}")
we12 = les_block("Worked example 12</span>", "<!-- ============ Concept 2")
has("L WE12 question", we12, "Three identical wine glasses and five identical tumblers")
check("L WE12 a", we12, r"so</p>" + "\n" + r"\[\text{number of ways}=@.\]", ndist("WWWTTTTT"))
check("L WE12 b", we12, r"2 of another, so</p>" + "\n" + r"\[\text{number of ways}=@\quad", ndist("WWCTTTNN"))   # 2 plain W, chipped C, 3 old T, 2 new N
report("2 alike of one type, 1 of another, 3 of another, 2 of another" in we12 and "3 alike of one type and 5 alike of another" in we12,
       "L WE12 types", "the types 3+5 and 2+1+3+2 are as in the computation")
for blk, lab, a_, b_, c_ in ((ex_block(c1, "demo"), "C1 TD", "MMMMCCCCC", "MMMXCCCDD", "PEPPER"), (ex_block(c1, "attempt"), "C1 YT", "VVJJJJ", "VXJJKK", "TOOTH")):
    try:
        has(f"{lab} c word", blk, f"the word {c_}?")
        part = parts(A["C1"].split("<b>Your turn.</b>")[0 if lab == "C1 TD" else 1], "abc")
        first_math(f"{lab} a", part["a"], ndist(a_))
        first_math(f"{lab} b", part["b"], ndist(b_))
        first_math(f"{lab} c", part["c"], ndist(c_))
    except Exception as ex:
        report(False, lab, f"ERROR {ex}")
has("C1 TD data", ex_block(c1, "demo"), "Four identical mugs and five identical cups")
has("C1 TD data b", ex_block(c1, "demo"), "one of the mugs becomes clearly chipped, and two cups break and are replaced by two identical cups different from the other three")
has("C1 YT data", ex_block(c1, "attempt"), "Two identical vases and four identical jars")
has("C1 YT data b", ex_block(c1, "attempt"), "one of the vases becomes clearly chipped, and two jars break and are replaced by two identical jars different from the other two")

# ================================================================ Concept 2
c2 = concept(2)
try:
    f11 = find(c2, r"\[\text{number of words}=@.\]")
    ok = f11 == r"\dfrac{n!}{r!\times(n-r)!}"
    bad = [(n_, r_) for n_ in range(1, 9) for r_ in range(n_ + 1)
           if tex_eval(f11.replace("r!", "(" + str(r_) + ")!").replace("(n-r)", f"({n_}-{r_})").replace("n!", f"({n_})!")) != ndist("Y" * r_ + "N" * (n_ - r_))]
    report(ok and not bad, "L Box 11", f"printed {f11}; equals enumeration of r Ys and n - r Ns for n = 1..8")
except Exception as ex:
    report(False, "L Box 11", f"ERROR {ex}")
report(find(c2, r"The answer to part <b>a</b> was \(@\)") == r"\dfrac{8!}{3!\times5!}" and Fr(factorial(8), 6 * 120) == ndist("WWWTTTTT"), "L Box 11 intro", "8!/(3!5!) is WE12 a")
try:
    W_, H_ = grid_size("grid32")
    np32 = paths("grid32", "A", "B", "RD")
    report((W_, H_) == (3, 2) and "the 3 by 2 grid" in c2, "L grid figure", f"figure is {W_} by {H_}")
    check("L grid paths", c2, r"\[\text{number of paths}=@.\]", np32)
    report(np32 == ndist("RRRDD"), "L grid = words", f"{np32} paths = {ndist('RRRDD')} words with 3 Rs and 2 Ds")
    _, pts, c, route = svg_grid("grid32")
    word = "".join("R" if b[0] > a[0] else "D" for a, b in zip(route, route[1:]))
    report(route[0] == pts["A"] and route[-1] == pts["B"] and word == find(c2, "The path drawn is @."), "L grid drawn path", f"drawn path reads {word}")
except Exception as ex:
    report(False, "L grid", f"ERROR {ex}")
we13 = les_block("Worked example 13</span>", "<!-- ============ Concept 3")
has("L WE13 question", we13, "Six women and four men form a queue at the bus stop.")
check("L WE13 a", we13, r"\[\text{Number of patterns}=@.\]", ndist("WWWWWWMMMM"))
check("L WE13 b", we13, r"\[\text{Hence number of ways}=@.\]", len(list(product("WM", repeat=10))))
cells = re.findall(r"<td>(\d+)</td>", we13)
report(cells == ["2"] * 10, "L WE13 table", f"{len(cells)} cells of 2 (each place a man or a woman)")
td, yt = ex_block(c2, "demo"), ex_block(c2, "attempt")
has("C2 TD a question", td, "Five women and three men form a queue")
has("C2 TD b question", td, "a queue of eight adults")
has("C2 YT a question", yt, "Four women and two men form a queue")
has("C2 YT b question", yt, "a queue of six adults")
report("{{svg:grid42}}" in td and "{{svg:grid33}}" in yt and "right or down" in td and "right or down" in yt, "C2 figures", "grid42 in the demo, grid33 in your turn, moves right or down")
try:
    a_td, a_yt = A["C2"].split("<b>Your turn.</b>")
    p_ = parts(a_td, "abc")
    first_math("C2 TD a", p_["a"], ndist("WWWWWMMM"))
    first_math("C2 TD b", p_["b"], len(list(product("WM", repeat=8))))
    first_math("C2 TD c", p_["c"], paths("grid42", "A", "B", "RD"))
    report(grid_size("grid42") == (4, 2) and "four Rs and two Ds" in p_["c"], "C2 TD c grid", f"grid42 is {grid_size('grid42')}")
    p_ = parts(a_yt, "abc")
    first_math("C2 YT a", p_["a"], ndist("WWWWMM"))
    first_math("C2 YT b", p_["b"], len(list(product("WM", repeat=6))))
    first_math("C2 YT c", p_["c"], paths("grid33", "A", "B", "RD"))
    report(grid_size("grid33") == (3, 3) and "three Rs and three Ds" in p_["c"], "C2 YT c grid", f"grid33 is {grid_size('grid33')}")
except Exception as ex:
    report(False, "C2", f"ERROR {ex}")

# ================================================================ Concept 3
we14 = les_block("Worked example 14</span>", "<!-- ============ Homework")
oc, tot = omit_cases("PRESSES", 6)
check("L WE14 S omitted", we14, r"If an S is omitted, there are then 2 Es and 2 Ss, so</p>" + "\n" + r"\[\text{number of words}=@.\]", oc["S"])
check("L WE14 E omitted", we14, r"If an E is omitted, there are then 3 Ss, so</p>" + "\n" + r"\[\text{number of words}=@.\]", oc["E"])
aligned("L WE14 P or R omitted", we14, r"\[\begin{aligned}\text{number of words}&=@\end{aligned}\]", oc["P"] + oc["R"])
terms("L WE14 total", we14, r"\[\text{Hence the total number of words is }@.\]", [oc["S"], oc["E"], oc["P"] + oc["R"]], tot)
report(sum(oc.values()) == tot, "L WE14 cases", f"cases {oc} add to {tot} six-letter words of PRESSES (enumerated)")
c3 = concept(3)
has("C3 TD question", ex_block(c3, "demo"), "six-letter words can be formed by using the letters of the word ‘ADDRESS’")
has("C3 YT question", ex_block(c3, "attempt"), "five-letter words can be formed by using the letters of the word ‘LETTER’")
try:
    a_td, a_yt = A["C3"].split("<b>Your turn.</b>")
    oc, tot = omit_cases("ADDRESS", 6)
    m = maths(a_td)
    ok = (tex_eval(m[0].split("=")[0]) == oc["D"] + oc["S"] == tex_eval(m[0].split("=")[1]) and oc["D"] == oc["S"]
          and tex_eval(m[1].split("=")[0]) == oc["A"] + oc["R"] + oc["E"] == tex_eval(m[1].split("=")[1])
          and "D or S is omitted (2 cases)" in a_td and "A, R or E is omitted (3 cases)" in a_td)
    report(ok, "C3 TD cases", f"printed {m[:2]}; enumerated {oc}")
    terms("C3 TD total", "\\(" + m[2] + "\\)", r"\(@\)", [oc["D"] + oc["S"], oc["A"] + oc["R"] + oc["E"]], tot)
    oc, tot = omit_cases("LETTER", 5)
    m = maths(a_yt)
    ok = (tex_eval(m[0].split("=")[0]) == oc["E"] + oc["T"] == tex_eval(m[0].split("=")[1])
          and tex_eval(m[1].split("=")[0]) == oc["L"] + oc["R"] == tex_eval(m[1].split("=")[1])
          and "E or T is omitted (2 cases)" in a_yt and "L or R is omitted (2 cases)" in a_yt)
    report(ok, "C3 YT cases", f"printed {m[:2]}; enumerated {oc}")
    terms("C3 YT total", "\\(" + m[2] + "\\)", r"\(@\)", [oc["E"] + oc["T"], oc["L"] + oc["R"]], tot)
except Exception as ex:
    report(False, "C3", f"ERROR {ex}")


# ================================================================ textbook homework
def tb(qn, letters):
    if str(qn) not in A:
        raise LookupError(f"answer {qn} missing")
    return parts(A[str(qn)], letters)


def tbcheck(qn, letters, truths):
    try:
        pa = tb(qn, letters)
        for L, t in zip(letters, truths):
            first_math(f"TB{qn}{L}", pa[L], t)
    except Exception as ex:
        report(False, f"TB{qn}", f"ERROR {ex}")


def single(qn, truth):
    first_math(f"TB{qn}", A.get(str(qn), ""), truth)


def roman(blk, labels, truths, tag):
    for r_, t in zip(labels, truths):
        try:
            v = find(blk, f" {r_}&nbsp;\\(@\\)")
            report(tex_eval(v) == t, f"{tag} {r_}", f"printed {v}, computed {t}")
        except Exception as ex:
            report(False, f"{tag} {r_}", f"ERROR {ex}")


W1 = ["BOB", "ALAN", "SNEEZE", "TASMANIA", "BEGINNER", "FOOTBALLS", "EQUILATERAL", "COMMITTEE", "WOOLLOOMOOLOO"]
for L, w in zip("abcdefghi", W1):
    has(f"TB1 word {w}", Q[1], f'<span class="pl">{L}</span>{w}</span>')
tbcheck(1, "abcdefghi", [ndist(w) for w in W1])
has("TB2 digits", Q[2], "The six digits 1, 1, 1, 2, 2, 3")
single(2, ndist("111223"))
tbcheck(3, "abc", [ndist("TTTTTH"), ndist("HHHHTT"), ndist("TTTHHH")])
tbcheck(4, "abcd", [ndist("ABCDEFGH"), ndist("RRRRRRRW"), ndist("RRRRRRWB"), ndist("RRRWWWBB")])
ch = list(distinct("GGGGGRRR"))
tbcheck(5, "ab", [len(ch), count(ch, lambda p: p[0] == p[-1] == "G")])
lights = list(product("RG", repeat=8))
n6 = count(lights, lambda p: p.count("R") == 3)
try:
    pa = tb(6, "ab")
    first_math("TB6a", pa["a"], n6)
    other = [r for r in range(9) if r != 3 and count(lights, lambda p: p.count("R") == r) == n6]
    first_math("TB6b", pa["b"], other[0])
    report(len(other) == 1, "TB6b unique", f"other numbers of red lights with {n6} ways: {other}")
except Exception as ex:
    report(False, "TB6", f"ERROR {ex}")
so = list(distinct("SOCKS"))
tbcheck(7, "abcd", [len(so), count(so, lambda p: together(p, "S")), count(so, lambda p: not together(p, "S")), count(so, lambda p: p.index("K") < p.index("C"))])
report(2 * count(so, lambda p: p.index("K") < p.index("C")) == len(so) and "(half of them)" in A["7"], "TB7d half", "K left of C in exactly half")
sl = list(distinct("SLOOPS"))
try:
    a8, b8 = A["8"].split("<b>b</b>")
    roman(a8, ["i", "ii", "iii", "iv"], [len(sl), count(sl, lambda p: together(p, "O")), count(sl, lambda p: not together(p, "O")),
                                       count(sl, lambda p: together(p, "O") and together(p, "S"))], "TB8a")
    first_math("TB8b", b8, ndist("TATTOO", lambda p: not together(p, "O")))
except Exception as ex:
    report(False, "TB8", f"ERROR {ex}")
de = list(distinct("DECISIONS"))
alt = lambda p: all((p[i] in VOW) != (p[i + 1] in VOW) for i in range(len(p) - 1))
tbcheck(9, "abcd", [len(de), count(de, alt), count(de, lambda p: all(c in VOW for c in p[:4])), count(de, lambda p: p.index("N") > p.index("D"))])
report(2 * count(de, lambda p: p.index("N") > p.index("D")) == len(de) and "(half of them)" in A["9"], "TB9d half", "N right of D in exactly half")


# Q10: the vowels fill the vowel places and the consonants the consonant places, independently.
def same_places(word, full=False):
    if full:
        pat = [c in VOW for c in word]
        return ndist(word, lambda p: [c in VOW for c in p] == pat)
    v = [c for c in word if c in VOW]
    k = [c for c in word if c not in VOW]
    return ndist(v) * ndist(k)


report(same_places("TATTOO") == same_places("TATTOO", True) and same_places("DECISIONS") == same_places("DECISIONS", True),
       "TB10 method", "vowel-places x consonant-places = full enumeration for TATTOO and DECISIONS")
has("TB10 word", Q[10], "PROPORTIONALITY")
single(10, same_places("PROPORTIONALITY"))
fm = list(product("YN", repeat=10))
yes = lambda p: p.count("Y")
tbcheck(11, "abcdefgh", [len(fm), count(fm, lambda p: p[0] == p[-1] == "Y"), count(fm, lambda p: yes(p) == 2), count(fm, lambda p: yes(p) == 5),
                         count(fm, lambda p: yes(p) > 7), count(fm, lambda p: yes(p) % 2), count(fm, lambda p: yes(p) == 3 and together(p, "Y")),
                         count(fm, lambda p: p[0] == p[-1] == "Y" and yes(p) == 6)])
code = lambda k: count(product("YGP", repeat=k), lambda p: p.count("Y") <= 3 and p.count("G") <= 2 and p.count("P") <= 1)
has("TB12 limits", Q[12], "no more than three yellow dots, no more than two green dots and no more than one purple dot")
tbcheck(12, "ab", [code(6), code(5)])
tbcheck(13, "ab", [len(set(permutations("STRESS", 5))), len(set(permutations("BANANA", 5)))])
tr = list(distinct("TRANSITION"))
tbcheck(14, "abcdefg", [len(tr), count(tr, lambda p: together(p, "I")), count(tr, lambda p: together(p, "I") and together(p, "N") and together(p, "T")),
                        count(tr, lambda p: p[0] == p[-1] == "N"), count(tr, lambda p: p[0] == "N" and p[-1] != "N"),
                        count(tr, lambda p: p[0] != "N" and p[-1] != "N"), count(tr, lambda p: block(p, VOW))])


# Q15b: with k colours, the most patterns come from the best split of the 10 marbles; enumerate each split.
def splits(n, k, m=1):
    if k == 1:
        if n >= m:
            yield (n,)
        return
    for a in range(m, n // k + 1):
        for r in splits(n - a, k - 1, a):
            yield (a,) + r


def best(k):
    return max(ndist("".join(string.ascii_uppercase[i] * a for i, a in enumerate(s))) for s in splits(10, k))


try:
    pa = tb(15, "ab")
    first_math("TB15a", pa["a"], count(permutations(range(10))))
    bests = {k: best(k) for k in (1, 2, 3, 4)}
    kmin = min(k for k in bests if bests[k] >= 10000)
    first_math("TB15b", pa["b"], kmin)
    print(f"NOTE     TB15b: best number of patterns with k colours {bests}")
except Exception as ex:
    report(False, "TB15", f"ERROR {ex}")
gu = list(distinct("GUMTREE"))
E2 = lambda p: [k for k, x in enumerate(p) if x == "E"]
gap = lambda p: E2(p)[1] - E2(p)[0] - 1
try:
    a16 = A["16"]
    first_math("TB16a", parts(a16, "a")["a"].split("<b>b</b>")[0], len(gu))
    first_math("TB16b", a16.split("<b>b</b>")[1].split("<b>c</b>")[0], count(gu, lambda p: together(p, "E")))
    roman(a16.split("<b>c</b>")[1].split("<b>d</b>")[0], ["i", "ii", "iii", "iv", "v"], [count(gu, lambda p: gap(p) == k) for k in range(1, 6)], "TB16c")
    n16d = count(gu, lambda p: E2(p)[0] < p.index("G") < E2(p)[1])
    first_math("TB16d", a16.split("<b>d</b>")[1].split("<b>e</b>")[0], n16d)
    report(3 * n16d == len(gu), "TB16d third", "one third of all arrangements, as printed")
    first_math("TB16e", a16.split("<b>e</b>")[1].split("<b>f</b>")[0], count(gu, lambda p: p.index("M") < E2(p)[0] < p.index("U") < E2(p)[1]))
    first_math("TB16f", a16.split("<b>f</b>")[1], count(gu, lambda p: p.index("G") < p.index("U") < p.index("M")))
    ins = set()                                         # insert U, M, T, R successively into EGE
    for w in [("E", "G", "E")]:
        cur = {w}
        for c in "UMTR":
            cur = {s[:i] + (c,) + s[i:] for s in cur for i in range(len(s) + 1)}
        ins |= cur
    report(len(ins) == n16d, "TB16d insertion", f"inserting U, M, T, R into EGE gives {len(ins)} words")
except Exception as ex:
    report(False, "TB16", f"ERROR {ex}")


# Q17: place the KOALA letters in order in a choice of 5 places, and the GUMTREE letters in the rest.
def koala(a, b, full=False):
    if full:
        return ndist(a + b, lambda p: [c for c in p if c in set(b)] == list(b))
    n = len(a) + len(b)
    return count(combinations(range(n), len(b))) * ndist(a)


report(koala("TREE", "ALA") == koala("TREE", "ALA", True) and koala("GUM", "KOALA") == koala("GUM", "KOALA", True), "TB17 method",
       "places-then-fill = full enumeration for TREE+ALA and GUM+KOALA")
single(17, koala("GUMTREE", "KOALA"))
single(18, ndist("AABBCCDD", lambda p: all(p[i] != p[i + 1] for i in range(7))))
# Q19
ab4 = list(permutations("ABCD"))
fixed = lambda p, S: all(p["ABCD".index(c)] == c for c in S)
try:
    a19 = A["19"]
    first_math("TB19a", a19.split("<b>b</b>")[0], len(ab4))
    b19 = a19.split("<b>b</b>")[1].split("<b>c</b>")[0]
    m = maths(b19)
    report(all(count(ab4, lambda p: fixed(p, c)) == tex_eval(m[0].split("=")[1]) == tex_eval(m[0].split("=")[0]) for c in "ABCD")
           and tex_eval(m[1].split("=")[0]) == sum(count(ab4, lambda p: fixed(p, c)) for c in "ABCD") == tex_eval(m[1].split("=")[1]),
           "TB19b", f"printed {m}; each of A, B, C, D fixed in {count(ab4, lambda p: fixed(p, 'A'))} permutations")
    c19 = a19.split("<b>c</b>")[1].split("<b>d</b>")[0]
    m = maths(c19)
    pairs = list(combinations("ABCD", 2))
    v = int(find(c19, "and there are @ pairs of letters"))
    report(tex_eval(m[0]) == count(ab4, lambda p: fixed(p, "AB")) and v == len(pairs)
           and tex_eval(m[1].split("=")[0]) == sum(count(ab4, lambda p: fixed(p, s)) for s in pairs) == tex_eval(m[1].split("=")[1]),
           "TB19c", f"printed {m}, {v} pairs")
    d19 = maths(a19.split("<b>d</b>")[1].split("<b>g</b>")[0])[0]
    lhs, expr, val = d19.split("=")
    der = count(ab4, lambda p: all(p[i] != c for i, c in enumerate("ABCD")))
    ts = [abs(tex_eval(t.lstrip("+"))) for t in re.findall(r"[+-]?[^+-]+", expr)]
    ie = [sum(count(ab4, lambda p: fixed(p, s)) for s in combinations("ABCD", k)) for k in range(5)]
    report(lhs == "D(4)" and tex_eval(expr) == tex_eval(val) == der and ts == ie, "TB19d", f"printed {d19}; inclusion-exclusion terms {ie}, derangements {der}")
    import math as _m
    rat = [Fr(factorial(n_), count(permutations(range(n_)), lambda p: all(p[i] != i for i in range(n_)))) for n_ in range(2, 9)]
    report(abs(float(rat[-1]) - _m.e) < 1e-4 and "converges to \\(e\\)" in a19 and "\\dfrac{1}{e}" in a19, "TB19g", f"n!/D(n) for n = 8 is {float(rat[-1]):.6f}, near e")
except Exception as ex:
    report(False, "TB19", f"ERROR {ex}")
has("TB19 c printed", Q[19], "In doing part B, however")
report(sorted(Q) == list(range(1, 20)), "TB question numbers", f"{sorted(Q)}")
ans_q = sorted(int(k) for k in A if k.isdigit())
report(ans_q == list(range(1, 20)), "TB answer numbers", f"{ans_q} (19e, 19f are explanations)")
report(HW.count("{{band:F}}") == HW.count("{{band:D}}") == HW.count("{{band:E}}") == 1
       and HW.index("{{band:D}}") < HW.index('<span class="q-num">6</span>') and HW.index("{{band:E}}") < HW.index('<span class="q-num">16</span>')
       and HW.index('<span class="q-num">15</span>') < HW.index("{{band:E}}"), "TB bands", "F 1-5, D 6-15, E 16-19")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "lesson marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    report(T == roundhalf5(Fr(3, 2) * M), "lesson time", f"{T} min for {M} marks (1.5 x {M} = {float(1.5 * M)})")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    note = re.search(r'<p class="small">(.*?)</p>', pps[1], re.S).group(1)
    probs = [n_ for n_ in PPQ if "probability" in PPQ[n_]]
    grids = [n_ for n_ in PPQ if "{{svg:" in PPQ[n_]]
    report(probs == [8, 9] and grids == [10, 11] and "PP 8 and PP 9 are probability questions" in note and "PP 10 and PP 11 count paths on a grid" in note,
           "intro note", f"probability items {probs}, grid items {grids}")
    for n_ in PPQ:
        sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[n_], re.S)]
        tot_ = int(re.search(r'<span class="mk">(\d+) marks?</span>', PPQ[n_]).group(1))
        if sub:
            report(sum(sub) == tot_, f"PP{n_} part marks", f"parts {sub} sum {sum(sub)}, block {tot_}")
        src_q = re.search(r"^(.*?)</span>", PPQ[n_]).group(1)
        src_a = re.search(r"^(.*?)</span>", PPA.get(n_, "")).group(1) if n_ in PPA else None
        report(src_q == src_a and "Extension&nbsp;1" in src_q and re.search(r"Extension&nbsp;1( Mathematics)?,&nbsp;Q", src_q), f"PP{n_} source label", src_q)
        report(PPQ[n_].count('<div class="hint"><b>Hint:</b>') == 1, f"PP{n_} hint", "exactly one hint")
except Exception as ex:
    report(False, "lesson structure", f"ERROR {ex}")


def mc(pp, value, pattern, conv=lambda v: tex_eval(v.replace("&#8239;", ""))):
    try:
        opts = {k: conv(v) for k, v in re.findall(pattern, PPQ[pp])}
        letter = re.search(r"<b>Answer \(?([A-D])\)?\.</b>", PPA[pp]).group(1)
        hit = [k for k, v in opts.items() if v == value]
        report(len(opts) == 4 and hit == [letter], f"PP{pp} MC letter", f"options {[(k, str(v)) for k, v in opts.items()]}; printed {letter}; option equal to {value} is {hit}")
    except Exception as ex:
        report(False, f"PP{pp} MC letter", f"ERROR {ex}")


MC_PLAIN = r"<span>([A-D])\. (\d+)</span>"
MC_PAREN = r"<span>\(([A-D])\) (\d+|\\\(.+?\\\))</span>"
MC_FRAC = r"<span>([A-D])\. \\\((.+?)\\\)</span>"
MC_PFRAC = r"<span>\(([A-D])\) \\\((.+?)\\\)</span>"
strip_m = lambda v: tex_eval(v.replace("\\(", "").replace("\\)", ""))

# ---------------------------------------------------------------- PP 1 EXCELLENT
has("PP1 question", PPQ.get(1, ""), "In how many ways can the letters of the word EXCELLENT be arranged?")
n1 = ndist("EXCELLENT")
check("PP1", PPA.get(1, ""), r"\[\text{number of arrangements}=@.\]", n1)
check("PP1 option D", PPA.get(1, ""), r"Option D, \(@\), treats", count(permutations("EXCELLENT")))
check("PP1 option C", PPA.get(1, ""), r"Option C, \(@\), allows", ndist(["E", "X", "C", "E", "L1", "L2", "E", "N", "T"]))
mc(1, n1, MC_PLAIN)
# ---------------------------------------------------------------- PP 2 chairs
has("PP2 question", PPQ.get(2, ""), "Two of the chairs are to be painted black.")
check("PP2", PPA.get(2, ""), r"\[\text{number of arrangements}=@.\]", ndist(["black", "black", "blue", "green", "yellow", "grey"]))
# ---------------------------------------------------------------- PP 3 SPUDDLE beginning with P
sp = list(distinct("SPUDDLE"))
n3 = count(sp, lambda p: p[0] == "P")
has("PP3 question", PPQ.get(3, ""), "SPUDDLE which begins with the letter P")
check("PP3", PPA.get(3, ""), r"\[\text{number of arrangements}=@.\]", n3)
check("PP3 option A", PPA.get(3, ""), r"Option A, \(@\), is", len(sp))
mc(3, n3, MC_FRAC)
# ---------------------------------------------------------------- PP 4 TABLECLOTH
has("PP4 question", PPQ.get(4, ""), "ten-letter arrangements can be made using the letters of the word TABLECLOTH")
check("PP4", PPA.get(4, ""), r"\[\text{number of arrangements}=@.\]", ndist("TABLECLOTH"))
report("two Ts and two Ls" in PPA.get(4, "") and sorted(k for k, v in Counter("TABLECLOTH").items() if v > 1) == ["L", "T"], "PP4 repeats", "T and L are the repeated letters")
# ---------------------------------------------------------------- PP 5 MILO or SAVVAS
b5 = PPA.get(5, "")
check("PP5 MILO", b5, r"so MILO has \(@\) arrangements", ndist("MILO"))
check("PP5 SAVVAS", b5, r"By Box 10 it has</p>" + "\n" + r"\[@\]", ndist("SAVVAS"))
try:
    a_, b_ = find(b5, r"<p>Since \(@\), SAVVAS has more").split("&gt;")
    report(int(a_) == ndist("SAVVAS") > ndist("MILO") == int(b_), "PP5 compare", f"{a_} > {b_}")
except Exception as ex:
    report(False, "PP5 compare", f"ERROR {ex}")
# ---------------------------------------------------------------- PP 6 EXTENSION, Es together
ext = list(distinct("EXTENSION"))
n6 = count(ext, lambda p: together(p, "E"))
check("PP6", PPA.get(6, ""), r"\[\text{number of arrangements}=@.\]", n6)
report(count(ext, lambda p: together(p, "E")) == ndist(["EE", "X", "T", "N", "S", "I", "O", "N"]), "PP6 glue", "Es together = arrangements of EE, X, T, N, S, I, O, N")
mc(6, n6, MC_FRAC)
has("PP6 question", PPQ.get(6, ""), "<b>EXTENSION</b> be arranged if the letter E’s are to be together?")
# ---------------------------------------------------------------- PP 7 STATISTICS
st = list(distinct("STATISTICS"))
check("PP7 (i)", PPA.get(7, ""), r"\[\text{number of arrangements}=@.\]", len(st))
aligned("PP7 (ii)", PPA.get(7, ""), r"\[\begin{aligned}\text{number of arrangements}&=@\end{aligned}\]", count(st, lambda p: adjacent(p, "A", "C")))
report(count(st, lambda p: p.index("C") == p.index("A") + 1) * 2 == count(st, lambda p: adjacent(p, "A", "C"))
       and count(st, lambda p: p.index("C") == p.index("A") + 1) == ndist(["AC", "S", "S", "S", "T", "T", "T", "I", "I"]), "PP7 (ii) glue",
       "AC glued: 9 items, and CA doubles it")
check("PP7 2!", PPA.get(7, ""), r"The group can be ordered in \(@\) ways (AC or CA)", 2)
has("PP7 question", PPQ.get(7, ""), "where the A and C are next to each other?")
# ---------------------------------------------------------------- PP 8 CALCULUS
b8 = PPA.get(8, "")
tiles = list(permutations(range(8)))                    # 8 labelled tiles C C A L L U U S
lab = "CCALLUUS"
words = Counter(tuple(lab[i] for i in t) for t in tiles)
n_ca = len(words)
fav = sum(1 for w in words if w[0] == w[-1] == "C")
check("PP8 |S|", b8, r"\[|S|=@.\]", n_ca)
check("PP8 |E|", b8, r"\[|E|=@.\]", fav)
check("PP8 P", b8, r"P(\text{C at the start and the end})=@.\]", Fr(fav, n_ca))
report(set(words.values()) == {8}, "PP8 equally likely", f"every distinct word comes from {set(words.values())} of the 8! tile orders")
check("PP8 8", b8, r"each different arrangement comes from exactly \(@\) of", 8)
report(Fr(fav, n_ca) == Fr(sum(1 for t in tiles if lab[t[0]] == lab[t[-1]] == "C"), len(tiles)), "PP8 tiles model", "same probability with labelled tiles")
mc(8, Fr(fav, n_ca), MC_PFRAC)
# ---------------------------------------------------------------- PP 9 ASCHAM
b9 = PPA.get(9, "")
cards = "AACHMS"
cw = Counter(tuple(cards[i] for i in t) for t in permutations(range(6)))
check("PP9 words", b9, r"form is</p>" + "\n" + r"\[@.\]", len(cw))
report(set(cw.values()) == {2} and tuple("ASCHAM") in cw, "PP9 equally likely", "every word comes from 2 card orders; ASCHAM is one of the words")
check("PP9 2", b9, r"each one comes from exactly \(@\) of", 2)
check("PP9 P", b9, r"\[P(\text{ASCHAM})=@.\]", Fr(1, len(cw)))
check("PP9 option C", b9, r"Option C, \(@\), forgets", Fr(1, count(permutations(cards))))
mc(9, Fr(1, len(cw)), MC_FRAC)
has("PP9 question", PPQ.get(9, ""), "Each of the letters A, A, C, H, M, and S is written on a separate card.")
# ---------------------------------------------------------------- PP 10 grid, right or down
try:
    n10 = paths("nbhs22", "A", "B", "RD")
    report(grid_size("nbhs22") == (5, 3) and "5 unit squares wide and 3 unit squares high" in PPA.get(10, ""), "PP10 grid", f"figure is {grid_size('nbhs22')}")
    check("PP10", PPA.get(10, ""), r"\[\text{number of paths}=@.\]", n10)
    _, pts, c, _ = svg_grid("nbhs22")
    report(pts["A"][0] < pts["B"][0] and pts["A"][1] < pts["B"][1], "PP10 A top left", "A is above and left of B (right or down)")
    report("{{svg:nbhs22}}" in PPQ.get(10, "") and "moving right or down along the grid lines" in PPQ.get(10, ""), "PP10 question", "figure and wording")
except Exception as ex:
    report(False, "PP10", f"ERROR {ex}")
# ---------------------------------------------------------------- PP 11 two grids, right or up
try:
    n11 = paths("stalo24", "A", "B", "RU")
    n11c = paths("stalo24c", "A", "B", "RU", via="C")
    ac, cb = paths("stalo24c", "A", "C", "RU"), paths("stalo24c", "C", "B", "RU")
    e1, p1_, _, _ = svg_grid("stalo24")
    e2, p2_, _, _ = svg_grid("stalo24c")
    report(n11 == n11c == paths("stalo24c", "A", "B", "RU") and ac * cb == n11, "PP11 through C", f"{n11} paths, all through C: {ac} x {cb}")
    report(grid_size("stalo24") == (9, 5) and len(e1) == len(e2) == (5 * 4 + 6 * 3) + (4 * 3 + 5 * 2) - 0, "PP11 grids", f"{len(e1)} unit edges (5 by 3 and 4 by 2 blocks)")
    b11 = PPA.get(11, "")
    check("PP11 A to C", b11, r"5 steps right and 3 steps up: \(@\) paths", ac)
    check("PP11 C to B", b11, r"4 steps right and 2 steps up: \(@\) paths", cb)
    check("PP11", b11, r"\[\text{number of paths}=@.\]", n11)
    mc(11, n11, MC_PAREN, conv=strip_m)
    report("{{svg:stalo24}}" in PPQ.get(11, "") and "Moving only right or up" in PPQ.get(11, ""), "PP11 question", "figure and wording")
except Exception as ex:
    report(False, "PP11", f"ERROR {ex}")
# ---------------------------------------------------------------- PP 12 tiddlywinks
proc = sum(1 for six in combinations(range(10), 6) for top in permutations(six, 4))
labels = ["1", "2", "3", "4", "F", "F", "O", "O", "O", "O"]
report(proc == ndist(labels), "PP12 labels", f"{proc} processes (choose 6, place 4 of them) = {ndist(labels)} label words")
check("PP12", PPA.get(12, ""), r"\[\text{number of ways}=@.\]", proc)
check("PP12 option D", PPA.get(12, ""), r"Option (D), \(@\), only", count(permutations(range(10), 4)))
mc(12, proc, MC_PFRAC)
has("PP12 question", PPQ.get(12, ""), "Out of a group of 10 professional tiddlywinks players, 6 are to be selected for the final round")

report(not any(s in LES + ANS for s in ("Killara High School, 2023", "PROBABILITY", "North Sydney Girls High School, 2023")), "left-out items",
       "Killara 2023 Q7, Hornsby 2023 Q4 and NSG 2023 Q5 are not used")
print(f"\n{COUNT[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{COUNT[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
