"""Check of Lesson 14E (Counting unordered selections), tied to the printed HTML.

Reads the printed answers from workspace/build/y11ch14/a_14e.html (lesson
examples C1-C5, textbook homework, past-paper worked solutions) and the printed
results in the concept boxes and worked examples of l14e.html. In a template
'@' marks the printed value; each template must match exactly once in its
block, otherwise the item FAILS. Printed LaTeX is converted to an exact value
(fractions.Fraction; \\times, \\div, +, -, powers, factorials, \\dfrac,
{}^{n}\\mathrm{P}_{r}, {}^{n}\\mathrm{C}_{r} and \\binom) and compared with a
count made independently from the question, by brute-force enumeration:
subsets are listed with itertools.combinations, committees are built from
labelled people, card hands are dealt one by one, triangles on a circle are
tested for overlap with coordinates, cube colourings are reduced by the 24
rotations generated from two quarter turns, grid paths are walked on the
grids read back from the built SVG figures, and the past-paper diagrams
(nine points, two rows of tiles) are read back from their SVGs. Where a full
enumeration is too large (Ex 14E Q12, Q29 for n = 6) the count is made by a
method that is first checked against a full enumeration on smaller cases.

For every printed chain such as "{}^{8}\\mathrm{C}_{5}=\\dfrac{8!}{3!\\times5!}=56"
EVERY '='-separated piece must equal the computed count, so a wrong factor in
the working fails as well as a wrong final answer. Algebraic answers (in n, r,
a, b, c) are evaluated at several values and compared with enumeration.
Past-paper structure is checked too: marks add to the intro total, time is
1.5 x marks rounded to the nearest 5 minutes (halves up), numbering, source
labels identical in both files, one hint each, part marks, and each MC letter
is the only option equal to the count.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_14e.py
"""
import os
import re
import sys
from collections import Counter
from fractions import Fraction as Fr
from functools import lru_cache
from itertools import combinations, permutations, product
from math import factorial, perm, comb, cos, sin, pi

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
        if s.startswith("{}^", i):                       # {}^{n}\mathrm{P}_{r}  or  {}^{n}\mathrm{C}_{r}
            top, i = _arg(s, i + 3)
            if s.startswith("\\mathrm{P}", i):
                fn, i = "PP", i + len("\\mathrm{P}")
            elif s.startswith("\\mathrm{C}", i):
                fn, i = "CC", i + len("\\mathrm{C}")
            else:
                raise ValueError(f"expected P or C after {{}}^ in {s!r}")
            if s[i] != "_":
                raise ValueError(f"expected subscript in {s!r}")
            sub, i = _arg(s, i + 1)
            out.append(f"{fn}(({_conv(top)}),({_conv(sub)}))")
        elif s.startswith(("\\dbinom", "\\tbinom", "\\binom"), i):
            i = s.index("binom", i) + 5
            a, i = _arg(s, i)
            b, i = _arg(s, i)
            out.append(f"CC(({_conv(a)}),({_conv(b)}))")
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
    for a in ("\\left", "\\right", "\\displaystyle", "&thinsp;", "&nbsp;", "\\qquad", "\\quad"):
        s = s.replace(a, "")
    s = re.sub(r"\\text\{[^}]*\}", "", s)
    s = re.sub(r"\\[,!;]|\\ |\s|&", "", s)
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    return s


def tex_to_py(tex):
    s = _conv(_clean(tex))
    toks = re.findall(r"PP|CC|\d+\.\d+|\d+|[A-Za-z]|\S", s)
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
            if j > 0 and out[j - 1] in ("PP", "CC"):
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
            left = re.fullmatch(r"\d+(\.\d+)?|[" + VARS + r"]|\)", prev)
            right = re.fullmatch(r"\d+(\.\d+)?|[" + VARS + r"F]|PP|CC|\(", t)
            if left and right:
                res.append("*")
        if re.fullmatch(r"[A-Za-z]", t) and t not in VARS + "F":
            raise ValueError(f"unknown letter {t!r} in {tex!r}")
        res.append(f"Fr('{t}')" if re.fullmatch(r"\d+(\.\d+)?", t) else ("**" if t == "^" else t))
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


def C(n, r):
    """nCr for reading printed notation only (truths never use it)."""
    n, r = Fr(n), Fr(r)
    if n.denominator != 1 or r.denominator != 1 or not 0 <= r <= n:
        raise ValueError(f"C({n},{r}) undefined")
    return Fr(comb(int(n), int(r)))


def tex_eval(tex, **var):
    env = {"Fr": Fr, "F": fact, "PP": P, "CC": C, "__builtins__": {}}
    env.update({k: Fr(v) for k, v in var.items()})
    return Fr(eval(tex_to_py(tex), env))


# ---------------------------------------------------------------- enumeration helpers
def ncount(it, cond=lambda x: True):
    return sum(1 for x in it if cond(x))


def subsets(xs):
    xs = list(xs)
    for k in range(len(xs) + 1):
        yield from combinations(xs, k)


def k_subsets(n, k):
    """Number of k-member subsets of an n-member set, by listing them."""
    return ncount(combinations(range(n), k))


def distinct(word):
    """Every distinct arrangement of the multiset of letters (next-permutation)."""
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


def roundhalf5(x):
    return 5 * int(Fr(x) / 5 + Fr(1, 2))


# ---------------------------------------------------------------- blocks
ANS = read("a_14e.html")
LES = read("l14e.html")
HEAD = "{{ahead:Lesson 14E | Counting unordered selections}}"


def ans_blocks(text):
    return {an.strip(): ab.replace('<span style="white-space:nowrap">', "").replace("</span>", "")
            for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S)}


A = ans_blocks(ANS)
sec = ANS.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_14e.html")
report(ANS.count(HEAD) == 2 and ANS.startswith(HEAD) and sec[0].rstrip().endswith(HEAD), "answers headings",
       "the ahead line opens the file and precedes the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}
pps = LES.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l14e.html")
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
    nxt = f"<!-- ============ Concept {k + 1}" if k < 5 else "<!-- ============ Homework"
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
    pieces = [p for p in tex.split("=") if _clean(p)]      # a piece that is only words (\text{...}) is skipped
    vals = [tex_eval(p, **var) for p in pieces]
    return all(v == Fr(truth) for v in vals), vals


def check(label, block, template, truth):
    try:
        tex = find(block, template)
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex.strip()} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def aligned_tex(tex):
    return tex.replace("\\\\", "").replace("&", "").replace("\\begin{aligned}", "").replace("\\end{aligned}", "").strip().rstrip(".").rstrip(",")


def aligned(label, block, template, truth):
    try:
        tex = aligned_tex(find(block, template))
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def rows(label, block, template, truths):
    """An aligned display whose lines are separate chains, each with its own truth."""
    try:
        tex = find(block, template)
        lines = [aligned_tex(x) for x in tex.split("\\\\")]
        oks = []
        for ln, t in zip(lines, truths):
            ok, vals = chain_ok(ln, t)
            oks.append(ok)
        report(len(lines) == len(truths) and all(oks), label, f"printed lines {lines}, computed {truths}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def algebra(label, tex, truth_fn, values):
    """Every '='-piece of a printed formula in n (or r, a, ...) equals the enumerated count at each value."""
    try:
        pieces = [p for p in tex.split("=") if _clean(p)]
        bad = [(v, [str(tex_eval(p, **v)) for p in pieces], truth_fn(**v)) for v in values
               if any(tex_eval(p, **v) != truth_fn(**v) for p in pieces)]
        report(not bad, label, f"printed {tex} agrees with enumeration at {len(values)} values" + (f"; BAD {bad[:2]}" if bad else ""))
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def has(label, block, phrase):
    n = block.count(phrase)
    report(n >= 1, label, f"text contains {phrase!r}" + ("" if n else "  (NOT FOUND: question changed?)"))


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


def sets_in(s):
    s = re.sub(r"\\\(.*?\\\)", "", s, flags=re.S)
    return [tuple(x.split(", ")) for x in re.findall(r"\{([A-Z0-9](?:, [A-Z0-9]+)*)\}", s)]


def factors_prime(tex):
    """'2^4\\times3\\times7\\times13' -> True if every base is prime."""
    bases = [int(re.match(r"(\d+)", f).group(1)) for f in _clean(tex).split("*")]
    return all(b > 1 and all(b % d for d in range(2, b)) for b in bases)


def roman(blk, labels, truths, tag):
    for r_, t in zip(labels, truths):
        try:
            found = re.findall(r"(?<![a-z])" + r_ + r"&nbsp;\\\((.+?)\\\)", blk, re.S)
            if len(found) != 1:
                raise LookupError(f"{r_} found {len(found)} times")
            v = found[0]
            ok, vals = chain_ok(v, t)
            report(ok, f"{tag} {r_}", f"printed {v} -> {[str(x) for x in vals]}, computed {t}")
        except Exception as ex:
            report(False, f"{tag} {r_}", f"ERROR {ex}")


# ---------------------------------------------------------------- geometry: points on a circle
def circle_pts(n):
    return [(cos(2 * pi * k / n), sin(2 * pi * k / n)) for k in range(n)]


def orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def seg_cross(p, q, r, s):
    return orient(p, q, r) * orient(p, q, s) < 0 and orient(r, s, p) * orient(r, s, q) < 0


def inside(pt, tri):
    o = [orient(tri[i], tri[(i + 1) % 3], pt) for i in range(3)]
    return all(x > 0 for x in o) or all(x < 0 for x in o)


def overlap(t1, t2):
    e1 = [(t1[i], t1[(i + 1) % 3]) for i in range(3)]
    e2 = [(t2[i], t2[(i + 1) % 3]) for i in range(3)]
    return (any(seg_cross(*a, *b) for a in e1 for b in e2) or any(inside(p, t2) for p in t1) or any(inside(p, t1) for p in t2))


def triangle_pairs(n):
    pts = circle_pts(n)
    tris = list(combinations(range(n), 3))
    pairs = [(a, b) for a, b in combinations(tris, 2) if not set(a) & set(b)]
    ov = ncount(pairs, lambda ab: overlap([pts[i] for i in ab[0]], [pts[i] for i in ab[1]]))
    return len(tris), len(pairs), len(pairs) - ov, ov


TP = {n: triangle_pairs(n) for n in (7, 8, 10, 12)}

# ================================================================ Concept 1
c1 = concept(1)
try:
    tab = re.search(r'<table class="t subsets".*?</table>', c1, re.S).group(0)
    trs = re.findall(r"<tr>(.*?)</tr>", tab, re.S)
    ok, det = True, []
    for k, tr in enumerate(trs):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        n_ = int(cells[0])
        got = sorted(sets_in(cells[2])) if k else ([()] if "varnothing" in cells[2] else None)
        want = sorted(combinations("ABCDE", k))
        good = n_ == len(want) and got == want and cells[1].startswith(f"{k}-member")
        ok &= good
        det.append(f"{k}:{n_}{'' if good else '!'}")
    report(ok and len(trs) == 6, "L subsets table", f"rows {det}; every listed subset matches itertools.combinations of ABCDE")
except Exception as ex:
    report(False, "L subsets table", f"ERROR {ex}")
try:
    t = find(c1, r"This makes \(@\) subsets altogether.")
    lhs, tot = t.split("=")
    terms_ = [int(x) for x in lhs.split("+")]
    report(terms_ == [k_subsets(5, k) for k in range(6)] and int(tot) == ncount(subsets("ABCDE")) == sum(terms_), "L 32 subsets", f"printed {t}")
except Exception as ex:
    report(False, "L 32 subsets", f"ERROR {ex}")
yn5 = list(product("YN", repeat=5))
aligned("L total 2^5", c1, r"\[\begin{aligned}\text{Total number of subsets}&=\text{number of 5-letter words made up of Ys and Ns}@\end{aligned}\]", len(yn5))
aligned("L 3-member", c1, r"\[\begin{aligned}\text{Number of 3-member subsets}&=\text{number of 5-letter words with 3 Ys and 2 Ns}@\end{aligned}\]", ncount(yn5, lambda w: w.count("Y") == 3))
code = {"".join("Y" if c in S_ else "N" for c in "ABCDE"): S_ for S_ in ("ABD", "E")}
report("YYNYN \\(\\longleftrightarrow\\) {A, B, D}" in c1 and "NNNNY \\(\\longleftrightarrow\\) {E}" in c1 and code == {"YYNYN": "ABD", "NNNNY": "E"},
       "L Y/N code", "YYNYN <-> {A, B, D} and NNNNY <-> {E}")
try:
    gtot = find(c1, r"\[\begin{aligned}\text{total number of subsets}&=@\\")
    algebra("L general total", gtot, lambda n: ncount(subsets(range(int(n)))), [dict(n=n_) for n_ in range(0, 11)])
    gen = find(c1, r"\text{number of }r\text{-member subsets}&=@,\ \text{ for }")
    algebra("L general r-subsets", gen, lambda n, r: k_subsets(int(n), int(r)), [dict(n=n_, r=r_) for n_ in range(0, 9) for r_ in range(n_ + 1)])
    box = les_block("Box 12 &nbsp;Counting the subsets of a set", "<p>The last bullet point")
    f12 = find(box, r"Number of \(r\)-member subsets of \(S={}^{n}\mathrm{C}_{r}=@\)")
    algebra("L Box 12 formula", "{}^{n}\\mathrm{C}_{r}=" + f12, lambda n, r: k_subsets(int(n), int(r)), [dict(n=n_, r=r_) for n_ in range(0, 9) for r_ in range(n_ + 1)])
    tot12 = find(box, r"Total number of subsets of \(S=@\)")
    algebra("L Box 12 total", tot12, lambda n: ncount(subsets(range(int(n)))), [dict(n=n_) for n_ in range(0, 11)])
    s12 = find(box, r"<li>\(@\).</li></ul>")
    ok = all(sum(k_subsets(n_, k) for k in range(n_ + 1)) == ncount(subsets(range(n_))) == tex_eval(s12.split("=")[1], n=n_) for n_ in range(0, 10))
    report(ok and s12.startswith("{}^{n}\\mathrm{C}_{0}+{}^{n}\\mathrm{C}_{1}+{}^{n}\\mathrm{C}_{2}+\\cdots+{}^{n}\\mathrm{C}_{n}"), "L Box 12 sum", f"printed {s12}; sum of r-subset counts = all subsets, n = 0..9")
except Exception as ex:
    report(False, "L Box 12", f"ERROR {ex}")
proof = les_block("A proof moving from ordered selections", "<div class=\"ex demo\">")
check("L 5P3", proof, r"from the five letters A, B, C, D and E is \(@\).", ncount(permutations("ABCDE", 3)))
check("L 3P3", proof, r"there are \(@\) ways of ordering", ncount(permutations("BCE")))
check("L 60/6", proof, r"Hence the number of three-member subsets is \(@\), as required.", k_subsets(5, 3))
words = re.search(r'<p style="margin-left:8mm">([A-Z, ]+) \\\(\\longleftrightarrow\\\) \{B, C, E\}</p>', proof)
report(words is not None and sorted(words.group(1).split(", ")) == sorted("".join(p) for p in permutations("BCE")), "L BCE words", "the six words are the orderings of BCE")
try:
    gp = find(proof, r"\[@.\]")
    algebra("L nPr / rPr", gp, lambda n, r: k_subsets(int(n), int(r)), [dict(n=n_, r=r_) for n_ in range(1, 9) for r_ in range(1, n_ + 1)])
except Exception as ex:
    report(False, "L nPr / rPr", f"ERROR {ex}")
we15 = les_block("Worked example 15</span>", "Worked example 16</span>")
aligned("L WE15 a", we15, r"<p><b>a</b></p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]", k_subsets(8, 5))
try:
    b15 = aligned_tex(find(we15, r"<p><b>b</b></p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]"))
    algebra("L WE15 b", b15, lambda n: k_subsets(int(n), 3), [dict(n=n_) for n_ in range(3, 12)])
except Exception as ex:
    report(False, "L WE15 b", f"ERROR {ex}")
we16 = les_block("Worked example 16</span>", "<!-- ============ Concept 2")
aligned("L WE16", we16, r"\[\begin{aligned}@\end{aligned}\]", k_subsets(16, 5))
try:
    last = aligned_tex(find(we16, r"\[\begin{aligned}@\end{aligned}\]")).split("=")[-1]
    report(factors_prime(last), "L WE16 primes", f"{last} is a product of primes")
except Exception as ex:
    report(False, "L WE16 primes", f"ERROR {ex}")
# Concept 1 demo / your turn
td, yt = ex_block(c1, "demo"), ex_block(c1, "attempt")
has("C1 TD set", td, r"Let \(T=\{1,2,3,4,5,6\}\).")
has("C1 YT set", yt, r"Let \(U=\{\mathrm{A},\mathrm{B},\mathrm{C},\mathrm{D}\}\).")
try:
    a_td, a_yt = A["C1"].split("<b>Your turn.</b>")
    p_ = parts(a_td, "abcde")
    first_math("C1 TD a", p_["a"], ncount(subsets(range(1, 7))))
    first_math("C1 TD b", p_["b"], ncount(combinations(range(1, 7), 4)))
    has("C1 TD c question", td, r"<b>c</b> \({}^{9}\mathrm{C}_{4}\)")
    first_math("C1 TD c", p_["c"], k_subsets(9, 4))
    algebra("C1 TD d", maths(p_["d"])[0], lambda n: k_subsets(int(n), 4), [dict(n=n_) for n_ in range(4, 13)])
    first_math("C1 TD e", p_["e"], k_subsets(15, 4))
    report(factors_prime(maths(p_["e"])[0].split("=")[-1]), "C1 TD e primes", maths(p_["e"])[0].split("=")[-1])
    p_ = parts(a_yt, "abcde")
    first_math("C1 YT a", p_["a"], ncount(subsets("ABCD")))
    report(sorted(sets_in(p_["b"])) == sorted(combinations("ABCD", 2)), "C1 YT b list", f"{sets_in(p_['b'])}")
    first_math("C1 YT b", p_["b"], k_subsets(4, 2))
    first_math("C1 YT c", p_["c"], k_subsets(7, 3))
    algebra("C1 YT d", maths(p_["d"])[0], lambda n: k_subsets(int(n), 2), [dict(n=n_) for n_ in range(2, 13)])
    first_math("C1 YT e", p_["e"], k_subsets(12, 5))
    report(factors_prime(maths(p_["e"])[0].split("=")[-1]), "C1 YT e primes", maths(p_["e"])[0].split("=")[-1])
except Exception as ex:
    report(False, "C1", f"ERROR {ex}")

# ================================================================ Concept 2
c2 = concept(2)
try:
    prs = re.findall(r"<td>\{([A-E, ]+)\} \\\(\\longleftrightarrow\\\) \{([A-E, ]+)\}</td>", c2)
    pairs = [(tuple(a.split(", ")), tuple(b.split(", "))) for a, b in prs]
    ok = sorted(p[0] for p in pairs) == sorted(combinations("ABCDE", 2)) and all(sorted(set("ABCDE") - set(a)) == list(b) for a, b in pairs)
    report(ok and len(pairs) == 10, "L complement table", f"{len(pairs)} pairs, each 2-subset with its complement")
except Exception as ex:
    report(False, "L complement table", f"ERROR {ex}")
check("L 5C2 = 5C3", c2, r"This confirms that \(@\).", k_subsets(5, 2))
report(k_subsets(5, 2) == k_subsets(5, 3), "L 5C2 = 5C3 counts", "10 = 10")
try:
    b13 = find(c2, r"<ul><li>\(@\)</li>")
    algebra("L Box 13", b13, lambda n, r: k_subsets(int(n), int(r)), [dict(n=n_, r=r_) for n_ in range(0, 9) for r_ in range(n_ + 1)])
    report("Let \\(n\\) and \\(r\\) be whole numbers with \\(0\\le r\\le n\\)" in c2, "L Box 13 condition", "printed 0 <= r <= n")
except Exception as ex:
    report(False, "L Box 13", f"ERROR {ex}")
we17 = les_block("Worked example 17</span>", "<!-- ============ Concept 3")
try:
    m = find(we17, r"\[@\]").split("\\qquad\\qquad")
    ok = all(chain_ok(x, t)[0] for x, t in zip(m, (k_subsets(7, 2), k_subsets(7, 5)))) and k_subsets(7, 2) == k_subsets(7, 5)
    report(ok and len(m) == 2, "L WE17", f"printed {m}; 7C2 = 7C5 = {k_subsets(7, 2)}")
except Exception as ex:
    report(False, "L WE17", f"ERROR {ex}")
try:
    a_td, a_yt = A["C2"].split("<b>Your turn.</b>")
    for lab, blk, n_, r_, big, sm, ppl, out in (("C2 TD", a_td, 9, 2, 20, 18, 9, 7), ("C2 YT", a_yt, 8, 3, 15, 13, 7, 5)):
        p_ = parts(blk, "abc")
        m = maths(p_["a"])
        report(len(m) == 2 and chain_ok(m[0], k_subsets(n_, r_))[0] and chain_ok(m[1], k_subsets(n_, n_ - r_))[0]
               and m[0].startswith(f"{{}}^{{{n_}}}\\mathrm{{C}}_{{{r_}}}") and m[1].startswith(f"{{}}^{{{n_}}}\\mathrm{{C}}_{{{n_ - r_}}}"),
               f"{lab} a", f"printed {m}, computed {k_subsets(n_, r_)} both")
        first_math(f"{lab} b", p_["b"], k_subsets(big, sm))
        first_math(f"{lab} c", p_["c"], k_subsets(ppl, out))
    has("C2 TD b question", ex_block(c2, "demo"), r"evaluate \({}^{20}\mathrm{C}_{18}\)")
    has("C2 YT b question", ex_block(c2, "attempt"), r"evaluate \({}^{15}\mathrm{C}_{13}\)")
    has("C2 TD c question", ex_block(c2, "demo"), "seven people out of nine")
    has("C2 YT c question", ex_block(c2, "attempt"), "five people out of seven")
except Exception as ex:
    report(False, "C2", f"ERROR {ex}")


# ================================================================ Concept 3: doubles tennis
def tennis(n, women):
    """People 0..n-1; Maria = 0, Alex = 1; women are 0..women-1 (Maria a woman, Alex a woman too when women > 1).
    Counts: (a) all fours, (b) Maria in and Alex out, (c) 2 men and 2 women, (d) women in majority,
    and the two cases of (d)."""
    fours = list(combinations(range(n), 4))
    w = lambda f: sum(1 for x in f if x < women)
    return (len(fours), ncount(fours, lambda f: 0 in f and 1 not in f), ncount(fours, lambda f: w(f) == 2),
            ncount(fours, lambda f: w(f) > 2), ncount(fours, lambda f: w(f) == 3), ncount(fours, lambda f: w(f) == 4))


c3 = concept(3)
we18 = les_block("Worked example 18</span>", "<!-- ============ Concept 4")
t10 = tennis(10, 4)
has("L WE18 question", we18, "Ten people meet to play doubles tennis.")
has("L WE18 c question", we18, "If there are four women and six men")
check("L WE18 a", we18, r"<p><b>a</b> \(\text{Number of ways}=@.\)</p>", t10[0])
check("L WE18 b", we18, r"Hence \(\text{number of ways}=@.\)", t10[1])
rows("L WE18 c", we18, r"<p><b>c</b></p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]",
     [ncount(combinations(range(4), 2)), ncount(combinations(range(6), 2)), t10[2]])
rows("L WE18 d", we18, r"<p><b>d</b></p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]", [t10[4], t10[5], t10[3]])
try:
    a_td, a_yt = A["C3"].split("<b>Your turn.</b>")
    for lab, blk, n_, w_ in (("C3 TD", a_td, 12, 5), ("C3 YT", a_yt, 9, 4)):
        t = tennis(n_, w_)
        p_ = parts(blk, "abcd")
        first_math(f"{lab} a", p_["a"], t[0])
        first_math(f"{lab} b", p_["b"], t[1])
        first_math(f"{lab} c", p_["c"], t[2])
        first_math(f"{lab} d", p_["d"], t[3])
        d_ = maths(p_["d"])[0].split("=")[1].split("+")
        report([tex_eval(x) for x in d_] == [t[4], t[5]], f"{lab} d cases", f"printed terms {d_}, computed 3 women {t[4]}, 4 women {t[5]}")
    has("C3 TD question", ex_block(c3, "demo"), "Twelve people meet to play doubles tennis.")
    has("C3 TD women", ex_block(c3, "demo"), "If there are five women and seven men")
    has("C3 YT question", ex_block(c3, "attempt"), "Nine people meet to play doubles tennis.")
    has("C3 YT women", ex_block(c3, "attempt"), "If there are four women and five men")
except Exception as ex:
    report(False, "C3", f"ERROR {ex}")


# ================================================================ Concept 4: subsets with conditions
def cond_counts(S, out, inn):
    subs = list(subsets(S))
    return (ncount(subs, lambda s: len(s) >= 2), ncount(subs, lambda s: len(s) >= 2 and out not in s),
            ncount(subs, lambda s: len(s) >= 2 and out not in s and inn in s))


c4 = concept(4)
we19 = les_block("Worked example 19</span>", "<!-- ============ Concept 5")
S19 = (2, 4, 6, 8, 10, 12)
w19 = cond_counts(S19, 8, 10)
has("L WE19 set", we19, r"Let \(S=\{2,4,6,8,10,12\}\)")
rows("L WE19 a", we19, r"<p><b>a</b></p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]",
     [ncount(subsets(S19), lambda s: len(s) <= 1), w19[0]])
rows("L WE19 b", we19, r"\(T=\{2,4,6,10,12\}\).</p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]",
     [ncount(subsets([x for x in S19 if x != 8]), lambda s: len(s) <= 1), w19[1]])
report(tuple(int(x) for x in find(we19, r"\(T=\{@\}\)").split(",")) == tuple(x for x in S19 if x != 8), "L WE19 T", "T is S without 8")
report(tuple(int(x) for x in find(we19, r"\(U=\{@\}\)").split(",")) == tuple(x for x in S19 if x not in (8, 10)), "L WE19 U", "U is S without 8 and 10 (commas as printed)")
try:
    tex = find(we19, r"\(U=\{2,4,6,12\}\).</p>" + "\n" + r"\[\begin{aligned}@\end{aligned}\]")
    l1, l2 = tex.split("\\\\")
    ok = tex_eval(aligned_tex(l1).split("=")[-1]) == ncount(combinations((2, 4, 6, 12), 0)) and chain_ok(aligned_tex(l2), w19[2])[0]
    report(ok, "L WE19 c", f"printed {tex}; computed {w19[2]}")
except Exception as ex:
    report(False, "L WE19 c", f"ERROR {ex}")
try:
    a_td, a_yt = A["C4"].split("<b>Your turn.</b>")
    for lab, blk, S_, out, inn in (("C4 TD", a_td, (3, 6, 9, 12, 15, 18, 21), 9, 21), ("C4 YT", a_yt, (5, 10, 15, 20, 25), 10, 25)):
        t = cond_counts(S_, out, inn)
        p_ = parts(blk, "abc")
        for L, v in zip("abc", t):
            first_math(f"{lab} {L}", p_[L], v)
        sb, sc = [tuple(int(x) for x in m.split(", ")) for m in re.findall(r"\{(\d+(?:, \d+)+)\}", p_["b"] + p_["c"])]
        report(sb == tuple(x for x in S_ if x != out) and sc == tuple(x for x in S_ if x not in (out, inn)), f"{lab} sets", f"{sb}, {sc}")
    has("C4 TD set", ex_block(c4, "demo"), r"\(S=\{3,6,9,12,15,18,21\}\)")
    has("C4 TD conds", ex_block(c4, "demo"), "do not contain 9 but do contain 21?")
    has("C4 YT set", ex_block(c4, "attempt"), r"\(S=\{5,10,15,20,25\}\)")
    has("C4 YT conds", ex_block(c4, "attempt"), "do not contain 10 but do contain 25?")
except Exception as ex:
    report(False, "C4", f"ERROR {ex}")

# ================================================================ Concept 5: triangles on a circle
c5 = concept(5)
we20 = les_block("Worked example 20</span>", "<!-- ============ Homework")
t10_ = TP[10]
check("L WE20 a", we20, r"\[\text{number of triangles}=@.\]", t10_[0])
check("L WE20 10C6", we20, r"first choose 6 points out of 10, which can be done in \(@\) ways.", k_subsets(10, 6))
check("L WE20 5C2", we20, r"the other 2 points in its triangle, which can be done in \(@\) ways.</p>", k_subsets(5, 2))
check("L WE20 b", we20, r"\[\text{Hence number of pairs of triangles}=@.\]", t10_[1])
check("L WE20 c i", we20, r"\(\text{the number of non-overlapping pairs}=@.\)", t10_[2])
check("L WE20 c ii", we20, r"\(\text{number of overlapping pairs}=@.\)", t10_[3])
# 6 points in cyclic order make two non-overlapping triangles in exactly 3 ways
pts6 = circle_pts(6)
splits6 = [(a, tuple(sorted(set(range(6)) - set(a)))) for a in combinations(range(6), 3) if 0 in a]
non6 = ncount(splits6, lambda ab: not overlap([pts6[i] for i in ab[0]], [pts6[i] for i in ab[1]]))
report(non6 == 3 and "into two non-overlapping triangles in 3 ways" in we20, "L WE20 3 ways", f"{non6} of the {len(splits6)} splits of 6 cyclic points do not overlap")
try:
    svg = read(os.path.join("svg", "circle10.svg"))
    labs = re.findall(r'<tspan font-style="italic">A</tspan><tspan[^>]*>(\d+)</tspan>', svg)
    dots = re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="3"', svg)
    from math import atan2
    ang = [atan2(-(float(y) - 100), float(x) - 100) for x, y in dots]
    clockwise = all(((ang[k] - ang[k + 1]) % (2 * pi)) < pi for k in range(len(ang) - 1))
    report(labs == [str(k) for k in range(1, 11)] and len(dots) == 10 and clockwise and "{{svg:circle10}}" in we20, "L WE20 figure",
           f"{len(dots)} points labelled A1..A10 in order around the circle")
except Exception as ex:
    report(False, "L WE20 figure", f"ERROR {ex}")
try:
    a_td, a_yt = A["C5"].split("<b>Your turn.</b>")
    for lab, blk, n_ in (("C5 TD", a_td, 8), ("C5 YT", a_yt, 7)):
        t = TP[n_]
        p_ = parts(blk, "abc")
        first_math(f"{lab} a", p_["a"], t[0])
        first_math(f"{lab} b", p_["b"], t[1])
        roman(p_["c"], ["i", "ii"], [t[2], t[3]], f"{lab} c")
    has("C5 TD question", ex_block(c5, "demo"), r"Eight points \(A_1,A_2,\ldots,A_8\)")
    has("C5 YT question", ex_block(c5, "attempt"), r"Seven points \(A_1,A_2,\ldots,A_7\)")
except Exception as ex:
    report(False, "C5", f"ERROR {ex}")


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


# Q1
try:
    pairs1 = re.search(r"combinations: (.*?)\.</div>", A["1"] + "</div>").group(1).replace(" and ", ", ").split(", ")
    report(sorted(pairs1) == sorted("".join(c) for c in combinations("PQRST", 2)), "TB1 list", f"{pairs1}")
    first_math("TB1", A["1"], k_subsets(5, 2))
    has("TB1 names", Q[1], "five people called P, Q, R, S and T")
except Exception as ex:
    report(False, "TB1", f"ERROR {ex}")
tbcheck(2, "abcd", [k_subsets(7, 2), k_subsets(7, 3), k_subsets(6, 2), k_subsets(9, 5)])
try:
    roman(A["3"].split("<b>b</b>")[0], ["i", "ii"], [k_subsets(10, 2), k_subsets(10, 8)], "TB3a")
    b3 = maths(A["3"].split("<b>b</b>")[1])
    report(len(b3) >= 2 and chain_ok(b3[0], k_subsets(10, 2))[0] and b3[1] == "{}^{n}\\mathrm{C}_{r}={}^{n}\\mathrm{C}_{n-r}", "TB3b", f"printed {b3[:2]}")
except Exception as ex:
    report(False, "TB3", f"ERROR {ex}")
# Q4: men 0..11, women 12..19
g4 = list(combinations(range(20), 8))
men = lambda g: sum(1 for x in g if x < 12)
tbcheck(4, "ab", [ncount(g4, lambda g: men(g) == 5), ncount(g4, lambda g: men(g) == 4)])
f5 = list(combinations(range(1, 9), 4))
odd = lambda s: sum(x % 2 for x in s)
tbcheck(5, "abcde", [len(f5), ncount(f5, lambda s: odd(s) == 2), ncount(f5, lambda s: odd(s) == 1), ncount(f5, lambda s: odd(s) == 0), ncount(f5, lambda s: odd(s) >= 1)])
# Q7: men 0..5, women 6..13; particular man = 0
c7 = list(combinations(range(14), 5))
m7 = lambda s: sum(1 for x in s if x < 6)
tbcheck(7, "abcdefgh", [len(c7), ncount(c7, lambda s: m7(s) == 0), ncount(c7, lambda s: m7(s) == 5), ncount(c7, lambda s: m7(s) == 2),
                        ncount(c7, lambda s: m7(s) == 1), ncount(c7, lambda s: m7(s) <= 2), ncount(c7, lambda s: 0 in s), ncount(c7, lambda s: 0 not in s)])
eq = list(combinations("EQUATION", 4))
tbcheck(8, "abc", [len(eq), ncount(eq, lambda s: all(c in "AEIOU" for c in s)), ncount(eq, lambda s: "Q" in s)])
has("TB8 word", Q[8], "the word EQUATION taken four at a time")
t9 = list(combinations("ABCDEFGHIJKL", 7))
tbcheck(9, "abcde", [len(t9), ncount(t9, lambda s: "C" in s), ncount(t9, lambda s: "J" not in s and "K" not in s),
                     ncount(t9, lambda s: "A" in s and "H" not in s), ncount(t9, lambda s: ("F" in s) != ("L" in s))])
nums = [str(x) for x in range(10000, 100000)]
desc = ncount(nums, lambda d: all(d[i] > d[i + 1] for i in range(4)))
asc = ncount(nums, lambda d: all(d[i] < d[i + 1] for i in range(4)))
try:
    roman(A["10"].split("<b>b</b>")[0], ["i", "ii"], [desc, asc], "TB10a")
    report("cannot begin with a zero" in A["10"] and "only be arranged in one way" in A["10"], "TB10 notes", "zero note and one-way note")
except Exception as ex:
    report(False, "TB10", f"ERROR {ex}")
single(11, ncount(distinct("SSSSSSFFFFTT")))


# Q12: distributions into labelled groups of sizes 8, 6, 4, 2. The sequential-choice method is checked
# against full enumeration of label words on a smaller case, then applied.
def seq_choose(n, sizes):
    tot, left = 1, n
    for s_ in sizes:
        tot *= ncount(combinations(range(left), s_)) if left <= 12 else comb(left, s_)
        left -= s_
    return tot


def walkers_girls(boys, girls, sizes):
    """sizes = (bus, car, bike, walk); walkers chosen from the girls only, then the rest in turn."""
    return seq_choose(girls, (sizes[-1],)) * seq_choose(boys + girls - sizes[-1], sizes[:-1])


small = (3, 2, 2, 1)
labels = "M" * 3 + "C" * 2 + "B" * 2 + "W"
people_small = list(distinct(labels))                      # each word assigns persons 0..7 to groups
full_small = len(people_small)
full_small_b = ncount(people_small, lambda w: all(w[i] != "W" for i in range(4)))   # persons 0..3 are boys
report(full_small == seq_choose(8, small) and full_small_b == walkers_girls(4, 4, small), "TB12 method",
       f"8 students into 3, 2, 2, 1: enumeration {full_small} and {full_small_b} (no boy walks) = sequential choice")
tbcheck(12, "ab", [seq_choose(20, (8, 6, 4, 2)), walkers_girls(10, 10, (8, 6, 4, 2))])
# Q13: ten points on a parabola (no three collinear)
pts13 = [(x, x * x) for x in range(10)]
col = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) == 0
tri13 = [t for t in combinations(range(10), 3) if not col(*(pts13[i] for i in t))]


def line_key(p, q):
    a, b = q[1] - p[1], p[0] - q[0]
    c = a * p[0] + b * p[1]
    g = __import__("math").gcd(__import__("math").gcd(a, b), c) or 1
    a, b, c = a // g, b // g, c // g
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return (a, b, c)


tbcheck(13, "abcd", [len({line_key(pts13[i], pts13[j]) for i, j in combinations(range(10), 2)}), len(tri13),
                     ncount(tri13, lambda t: 0 in t), ncount(tri13, lambda t: 0 in t and 1 in t)])
pts14 = [(x, 0) for x in range(5)] + [(x, x * x + 1) for x in range(10, 15)]
coltr = [t for t in combinations(range(10), 3) if col(*(pts14[i] for i in t))]
report(all(set(t) <= set(range(5)) for t in coltr), "TB14 model", "the only collinear triples are among the five points on the line")
tbcheck(14, "ab", [len(coltr), ncount(combinations(range(10), 3)) - len(coltr)])
# Q15: deal every five-card hand
RANKS, SUITS = range(13), "SHDC"
deck = [(r_, s_) for r_ in RANKS for s_ in SUITS]
c15 = [0] * 6
for h in combinations(deck, 5):
    su = [c[1] for c in h]
    rk = Counter(c[0] for c in h)
    c15[0] += all(s_ in "SC" for s_ in su)
    c15[1] += all(s_ == "D" for s_ in su)
    c15[2] += rk[12] == 4                                   # rank 12 = king
    c15[3] += su.count("D") == 3 and su.count("C") == 2
    c15[4] += rk[0] == 3 and sorted(rk.values()) == [2, 3]  # rank 0 = two
    c15[5] += sorted(rk.values()) == [2, 3]
tbcheck(15, "abcdef", c15)


# Q16: divide n people into two unnamed groups
def two_groups(n):
    divs = {frozenset([frozenset(g), frozenset(set(range(n)) - set(g))]) for k in range(1, n) for g in combinations(range(n), k)}
    return ncount(divs, lambda d: len({len(x) for x in d}) == 2), ncount(divs, lambda d: len({len(x) for x in d}) == 1)


try:
    a16 = A["16"]
    g6, g4_, g8 = two_groups(6), two_groups(4), two_groups(8)
    roman(a16.split("<b>b</b>")[0], ["i", "ii"], g6, "TB16a")
    roman(a16.split("<b>b</b>")[1].split("<b>c</b>")[0], ["i", "ii"], g4_, "TB16b")
    roman(a16.split("<b>c</b>")[1], ["i", "ii"], g8, "TB16c")
except Exception as ex:
    report(False, "TB16", f"ERROR {ex}")
diag = lambda n: ncount(combinations(range(n), 2), lambda e: (e[1] - e[0]) % n not in (1, n - 1))
try:
    p17 = tb(17, "abcd")
    for L, n_ in zip("abc", (4, 5, 10)):
        first_math(f"TB17{L}", p17[L], diag(n_))
    algebra("TB17d", maths(p17["d"])[0], lambda n: diag(int(n)), [dict(n=n_) for n_ in range(4, 14)])
except Exception as ex:
    report(False, "TB17", f"ERROR {ex}")
try:
    t12 = TP[12]
    p18 = A["18"]
    first_math("TB18a", p18.split("<b>a</b>")[1], t12[0])
    first_math("TB18b", p18.split("<b>b</b>")[1], t12[1])
    roman(p18.split("<b>c</b>")[1], ["i", "ii"], [t12[2], t12[3]], "TB18c")
except Exception as ex:
    report(False, "TB18", f"ERROR {ex}")
S20 = list(range(1, 20, 2))
sub19 = list(subsets(S20))
tbcheck(19, "abcd", [len(sub19), ncount(sub19, lambda s: len(s) >= 3), ncount(sub19, lambda s: len(s) >= 3 and 7 not in s),
                     ncount(sub19, lambda s: len(s) >= 3 and 7 not in s and 19 in s)])
has("TB19 set", Q[19], r"\(S=\{1,3,5,7,9,11,13,15,17,19\}\)")
pr20 = list(combinations(range(1, 10), 2))
tbcheck(20, "abcde", [ncount(pr20, lambda p: sum(p) % 2 == 0), ncount(pr20, lambda p: sum(p) % 2 == 1), ncount(pr20, lambda p: sum(p) % 3 == 0),
                      ncount(pr20, lambda p: sum(p) % 5 == 0), ncount(pr20, lambda p: sum(p) % 6 == 0)])
splits10 = {frozenset([frozenset(g), frozenset(set(range(10)) - set(g))]) for g in combinations(range(10), 5)}
tbcheck(21, "ab", [k_subsets(10, 5), len(splits10)])
ump = set()
for u in range(9):
    rest = [x for x in range(9) if x != u]
    for g in combinations(rest, 4):
        ump.add((u, frozenset([frozenset(g), frozenset(set(rest) - set(g))])))
apart = ncount(ump, lambda x: not any({0, 1} <= t for t in x[1]))
tbcheck(22, "ab", [len(ump), apart])
ndiv = lambda N: ncount(range(1, N + 1), lambda d: N % d == 0)
try:
    p23 = tb(23, "abcd")
    first_math("TB23a", p23["a"], ndiv(2 ** 3 * 3 ** 2))
    first_math("TB23b", p23["b"], ndiv(1000000))
    first_math("TB23c", p23["c"], ndiv(315000))
    has("TB23 data", Q[23], r'\(2^3\times3^2\)</span><span><span class="pl">b</span>\(1\,000\,000\)</span><span><span class="pl">c</span>\(315\,000\)')
    algebra("TB23d", maths(p23["d"])[0], lambda a, b, c: ndiv(2 ** int(a) * 5 ** int(b) * 13 ** int(c)),
            [dict(a=a_, b=b_, c=c_) for a_ in range(3) for b_ in range(3) for c_ in range(2)])
except Exception as ex:
    report(False, "TB23", f"ERROR {ex}")
# Q24: rotations of a cube act on the faces U D F B L R
yaw = (0, 1, 5, 4, 2, 3)        # face i moves to position yaw[i]: F->R, R->B, B->L, L->F
pitch = (2, 3, 1, 0, 4, 5)      # U->F, F->D, D->B, B->U
group = {tuple(range(6))}
while True:
    new = {tuple(g[h[i]] for i in range(6)) for g in group for h in (yaw, pitch)} | group
    if new == group:
        break
    group = new
cubes = {min(tuple(col[g.index(i)] for i in range(6)) for g in group) for col in permutations(range(6))}
report(len(group) == 24, "TB24 rotations", f"{len(group)} rotations generated")
tbcheck(24, "ab", [len(cubes), len(group)])


# Q25: grid read from its SVG
def svg_lines(name):
    svg = read(os.path.join("svg", name + ".svg"))
    segs = [tuple(float(v) for v in m) for m in re.findall(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg)]
    dots = [(round(float(x)), round(float(y))) for x, y in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
    labs = re.findall(r'<circle[^>]*/><text[^>]*>([^<]+)</text>', svg)
    crosses = [(round((float(a) + float(c)) / 2), round((float(b) + float(d)) / 2))
               for a, b, c, d in re.findall(r'<path class="cross" d="M([\d.]+),([\d.]+) L([\d.]+),([\d.]+) M', svg)]
    return svg, segs, dict(zip(labs, dots)), crosses


try:
    _, segs, pts, crosses = svg_lines("grid25")
    xs = sorted({s_[0] for s_ in segs} | {s_[2] for s_ in segs})
    ys = sorted({s_[1] for s_ in segs} | {s_[3] for s_ in segs})
    cell = round(xs[1] - xs[0])
    edges = set()
    for x1, y1, x2, y2 in segs:
        k = round(max(abs(x2 - x1), abs(y2 - y1)) / cell)
        q = [(round(x1 + (x2 - x1) * t / k), round(y1 + (y2 - y1) * t / k)) for t in range(k + 1)]
        edges |= {frozenset(e) for e in zip(q, q[1:])}
    top, second = round(ys[0]), round(ys[0]) + cell

    def walks(start, end, banned=lambda e: False, via=None):
        @lru_cache(None)
        def w(p, seen):
            if p == end:
                return 1 if via is None or seen else 0
            tot = 0
            for dx, dy in ((cell, 0), (0, cell)):
                q = (p[0] + dx, p[1] + dy)
                e = frozenset((p, q))
                if e in edges and not banned(e):
                    tot += w(q, seen or q == via)
            return tot
        return w(start, start == via)

    Apt, Bpt, Cpt = pts["A"], pts["B"], pts["C"]
    horiz = lambda e, y: len({p[1] for p in e}) == 1 and next(iter(e))[1] == y
    W_, H_ = (len(xs) - 1), (len(ys) - 1)
    report((W_, H_) == (4, 6) and Apt == (round(xs[0]), round(ys[0])) and Bpt == (round(xs[-1]), round(ys[-1])), "TB25 grid",
           f"grid {W_} wide and {H_} high, A top left, B bottom right; ten moves")
    p25 = A["25"]
    roman(p25, ["i", "ii", "iii", "iv"], [walks(Apt, Bpt), walks(Apt, Bpt, via=Cpt), walks(Apt, Bpt, lambda e: horiz(e, top)),
                                          walks(Apt, Bpt, lambda e: horiz(e, second))], "TB25a")
    four = sorted(crosses) == sorted((Apt[0] + i * cell, Apt[1] + (4 - i) * cell) for i in range(5)) and Cpt in crosses
    split = sum(walks(Apt, X) * walks(X, Bpt) for X in crosses)
    report(four and split == walks(Apt, Bpt), "TB25b crosses", f"the 5 crosses are the points 4 moves from A (C among them); sum of A-X-B paths = {split}")
    for lab, tex in zip(("TB25b", "TB25c", "TB25d"), re.findall(r"\\\[(\{\}\^\{1[02]\}.*?)\.\\\]", Q[25], re.S)):
        l_, r_ = tex.split("=")
        report(tex_eval(l_) == tex_eval(r_), f"{lab} identity", f"{tex[:40]}... both sides {tex_eval(l_)}")
except Exception as ex:
    report(False, "TB25", f"ERROR {ex}")
single(26, ncount(product(range(101), repeat=2), lambda ab: 0 <= 200 - ab[0] - ab[1] <= 100))
single(27, ncount(combinations(range(1, 31), 3), lambda t: sum(t) % 3 == 0))


# Q28: doubles tennis structures (pairs inside games, games unordered)
def pairings(xs):
    xs = list(xs)
    if not xs:
        yield ()
        return
    a = xs[0]
    for i in range(1, len(xs)):
        for rest in pairings(xs[1:i] + xs[i + 1:]):
            yield (frozenset((a, xs[i])),) + rest


def games(players):
    out = set()
    for pr in pairings(players):
        for grp in pairings(list(range(len(pr)))):
            out.add(frozenset(frozenset(pr[i] for i in g) for g in grp))
    return out


g4s, g8s, g12 = games(range(4)), games(range(8)), games(range(12))
mixed = ncount(g12, lambda s: all(len({x < 6 for x in pair}) == 2 for game in s for pair in game))   # men 0..5
try:
    first_math("TB28a", A["28"].split("<b>a</b>")[1], len(g4s))
    first_math("TB28b", A["28"].split("<b>b</b>")[1], len(g8s))
    roman(A["28"].split("<b>c</b>")[1], ["i", "ii"], [len(g12), mixed], "TB28c")
except Exception as ex:
    report(False, "TB28", f"ERROR {ex}")


# Q29: arrangements of two identical shirts in each of n styles with no two identical shirts adjacent
def dp_count(n, restrict=True):
    @lru_cache(None)
    def f(counts, last):
        if sum(counts) == 0:
            return 1
        tot = 0
        for i, c in enumerate(counts):
            if c and (i != last or not restrict):
                tot += f(counts[:i] + (c - 1,) + counts[i + 1:], i)
        return tot
    return f((2,) * n, -1)


brute = {n: ncount(distinct("".join(chr(65 + i) * 2 for i in range(n))), lambda w: all(w[i] != w[i + 1] for i in range(len(w) - 1))) for n in range(1, 5)}
tot_b = {n: ncount(distinct("".join(chr(65 + i) * 2 for i in range(n)))) for n in range(1, 5)}
report(all(brute[n] == dp_count(n) and tot_b[n] == dp_count(n, False) for n in range(1, 5)), "TB29 method", f"DP = enumeration for n = 1..4: {brute}")
try:
    seq = maths(A["29"].split("are", 1)[1])
    vals = [tex_eval(x) for x in seq]
    allowed = [vals[0]] + vals[1::2]                    # 0 (undefined), then (count, ratio) pairs
    ratios = vals[2::2]
    want = [dp_count(n) for n in range(1, 7)]
    want_r = [Fr(round(dp_count(n, False) / dp_count(n), 3)).limit_denominator(1000) for n in range(2, 7)]
    report(allowed == want and [float(r) for r in ratios] == [float(x) for x in want_r] and "(ratio undefined)" in A["29"], "TB29b",
           f"printed allowed {[str(v) for v in allowed]}, ratios {[float(r) for r in ratios]}; computed {want}, {[float(x) for x in want_r]}")
except Exception as ex:
    report(False, "TB29b", f"ERROR {ex}")
# Q30
strings = lambda zeros, ones: ncount(distinct("0" * zeros + "1" * ones))
try:
    a30 = A["30"].split("<b>b</b>")[0]
    for r_, ones in zip(["i", "ii", "iii", "iv"], range(4)):
        v = re.findall(r"(?<![a-z])" + r_ + r"&nbsp;\\\((.+?)\\\)", a30)
        if len(v) != 1:
            raise LookupError(f"TB30 {r_} found {len(v)} times")
        v = v[0]
        algebra(f"TB30a {r_}", v, lambda a, ones=ones: strings(int(a), ones), [dict(a=a_) for a_ in range(0, 6)])
    v = re.findall(r"(?<![a-z])v&nbsp;\\\((.+?)\\\)", a30)
    if len(v) != 1:
        raise LookupError(f"TB30 v found {len(v)} times")
    v = v[0]
    algebra("TB30a v", v, lambda a, r: strings(int(a), int(r)), [dict(a=a_, r=r_) for a_ in range(0, 5) for r_ in range(0, 5)])
    e30 = maths(A["30"].split("<b>e</b>")[1].split("<b>f</b>")[0])[-1]
    N_ = lambda a, b: sum(strings(int(a), k) for k in range(int(b) + 1))
    algebra("TB30e", e30, N_, [dict(a=a_, b=b_) for a_ in range(0, 5) for b_ in range(0, 5)])
    c30 = A["30"].split("<b>c</b>")[1].split("<b>d</b>")[0]
    report("\\(a+1\\) 0s and \\(b\\) 1s" in c30 and "\\(a+b+1\\)" in c30, "TB30c", "a + 1 0s, b 1s, length a + b + 1")
    f_tex = find(Q[30], r'<span class="pl">f</span>Show that \(@\).')
    l_, r_ = f_tex.split("=")
    ok = all(N_(a_, b_) == sum(tex_eval(f"{{}}^{{a+{k}}}\\mathrm{{C}}_{{{k}}}", a=a_) for k in range(b_ + 1)) == tex_eval(r_, a=a_, b=b_)
             for a_ in range(5) for b_ in range(5))
    report(ok, "TB30f identity", "aC0 + ... + (a+b)Cb = (a+b+1)Cb = N by enumeration")
except Exception as ex:
    report(False, "TB30", f"ERROR {ex}")
report(sorted(Q) == [1, 2, 3, 4, 5] + list(range(7, 31)), "TB question numbers", f"{sorted(Q)} (Q6 left out as doubtful)")
ans_q = sorted(int(k) for k in A if k.isdigit())
report(ans_q == [1, 2, 3, 4, 5] + list(range(7, 31)), "TB answer numbers", f"{ans_q}")
report(HW.count("{{band:F}}") == HW.count("{{band:D}}") == HW.count("{{band:E}}") == 1
       and HW.index("{{band:D}}") < HW.index('<span class="q-num">8</span>') and HW.index('<span class="q-num">7</span>') < HW.index("{{band:D}}")
       and HW.index("{{band:E}}") < HW.index('<span class="q-num">26</span>') and HW.index('<span class="q-num">25</span>') < HW.index("{{band:E}}"),
       "TB bands", "F 1-7, D 8-25, E 26-30")
report("three identical green balls" not in LES, "TB Q6 omitted", "Q6 (identical balls, answers count them as distinct) is not printed")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "lesson marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    report(T == roundhalf5(Fr(3, 2) * M), "lesson time", f"{T} min for {M} marks (1.5 x {M} = {float(1.5 * M)})")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for n_ in PPQ:
        sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[n_], re.S)]
        tot_ = int(re.search(r'<span class="mk">(\d+) marks?</span>', PPQ[n_]).group(1))
        if sub:
            report(sum(sub) == tot_, f"PP{n_} part marks", f"parts {sub} sum {sum(sub)}, block {tot_}")
        src_q = re.search(r"^(.*?)</span>", PPQ[n_]).group(1)
        src_a = re.search(r"^(.*?)</span>", PPA.get(n_, "")).group(1) if n_ in PPA else None
        report(src_q == src_a and re.search(r"Extension&nbsp;1( Mathematics| HSC Trial Examination)?,&nbsp;Q", src_q) is not None, f"PP{n_} source label", src_q)
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


MC_PLAIN = r"<span>([A-D])\. ([\d&#;]+)</span>"
MC_PAREN = r"<span>\(([A-D])\) ([\d&#;]+)</span>"

# ---------------------------------------------------------------- PP 1
n1 = k_subsets(20, 4)
has("PP1 question", PPQ.get(1, ""), "How many different ways can 4 people be chosen from a group of 20 people?")
check("PP1", PPA.get(1, ""), r"\[\text{number of ways}=@.\]", n1)
check("PP1 option C", PPA.get(1, ""), r"Option C, \(@\), counts", ncount(permutations(range(20), 4)))
report(ncount(permutations(range(20), 4)) == n1 * ncount(permutations(range(4))), "PP1 4!", "each group counted 4! times")
mc(1, n1, MC_PLAIN)
# ---------------------------------------------------------------- PP 2: men 0..4, women 5..9
c2s = list(combinations(range(10), 3))
sexes = lambda c: {x < 5 for x in c}
n2 = ncount(c2s, lambda c: len(sexes(c)) == 2)
b2 = PPA.get(2, "")
check("PP2 total", b2, r"With no restriction there are \(@\) committees.", len(c2s))
check("PP2 all male", b2, r"are all male, \(@\), or", ncount(c2s, lambda c: sexes(c) == {True}))
check("PP2 all female", b2, r"or all female, \(@\). Hence", ncount(c2s, lambda c: sexes(c) == {False}))
check("PP2", b2, r"\[\text{number of committees}=@.\]", n2)
check("PP2 case", b2, r"two men and one woman give \(@\), and", ncount(c2s, lambda c: sum(x < 5 for x in c) == 2))
has("PP2 question", PPQ.get(2, ""), "5 male and 5 female teachers")
mc(2, n2, MC_PAREN)
# ---------------------------------------------------------------- PP 3: Year 11 = 0..9, Year 12 = 10..24
t3 = list(combinations(range(25), 5))
y11 = lambda t: sum(1 for x in t if x < 10)
n3 = ncount(t3, lambda t: 2 <= y11(t) <= 3)
aligned("PP3", PPA.get(3, ""), r"\[\begin{aligned}\text{number of teams}&=@\end{aligned}\]", n3)
try:
    terms3 = aligned_tex(find(PPA.get(3, ""), r"\[\begin{aligned}\text{number of teams}&=@\end{aligned}\]")).split("=")[1].split("+")
    report([tex_eval(x) for x in terms3] == [ncount(t3, lambda t: y11(t) == 2), ncount(t3, lambda t: y11(t) == 3)], "PP3 cases", f"terms {terms3}")
except Exception as ex:
    report(False, "PP3 cases", f"ERROR {ex}")
has("PP3 question", PPQ.get(3, ""), "There are ten Year 11 students and fifteen Year 12 students")
mc(3, n3, MC_PLAIN)


# ---------------------------------------------------------------- PP 4: captain and vice captain
def teams_cv(n, r):
    return ncount((t, c, v) for t in combinations(range(n), r) for c in t for v in t if v != c)


try:
    vals4 = [dict(n=n_, r=r_) for n_ in range(3, 8) for r_ in range(2, n_)]
    opts = dict(re.findall(r"<span>([A-D])\. \\\((.+?)\\\)</span>", PPQ[4]))
    ok_opts = {}
    for k, v in opts.items():
        good = True
        for d in vals4:
            try:
                good &= tex_eval(v, **d) == teams_cv(d["n"], d["r"])
            except ValueError:
                good = False
        ok_opts[k] = good
    letter = re.search(r"<b>Answer \(?([A-D])\)?\.</b>", PPA[4]).group(1)
    report(len(opts) == 4 and [k for k, g in ok_opts.items() if g] == [letter], "PP4 MC letter", f"options agreeing with enumeration for 2 <= r < n <= 7: {ok_opts}; printed {letter}")
    d4 = find(PPA[4], r"\[\text{number of ways}=@.\]")
    algebra("PP4 answer", d4, lambda n, r: teams_cv(int(n), int(r)), vals4)
    alt = find(PPA[4], r"This gives \(@\). That form")
    algebra("PP4 other method", alt, lambda n, r: teams_cv(int(n), int(r)), vals4)
except Exception as ex:
    report(False, "PP4", f"ERROR {ex}")
# ---------------------------------------------------------------- PP 5: boys 0..13 (Henry = 0), girls 0..12 (Olivia = 0)
reps = [(b, g) for b in combinations(range(14), 2) for g in combinations(range(13), 2)]
b5 = PPA.get(5, "")
try:
    m5 = re.findall(r"\\\[\\text\{number of ways\}=(.+?)\.\\\]", b5)
    ok1, v1 = chain_ok(m5[0], len(reps))
    ok2, v2 = chain_ok(m5[1], ncount(reps, lambda bg: 0 in bg[0] and 0 in bg[1]))
    report(ok1, "PP5 (i)", f"printed {m5[0]}, computed {len(reps)}")
    report(ok2, "PP5 (ii)", f"printed {m5[1]}, computed {ncount(reps, lambda bg: 0 in bg[0] and 0 in bg[1])}")
except Exception as ex:
    report(False, "PP5", f"ERROR {ex}")
has("PP5 question", PPQ.get(5, ""), "In a class of 27 students, there are 14 boys and 13 girls.")
# ---------------------------------------------------------------- PP 6: Peter = 0, May = 1
c6 = list(combinations(range(10), 5))
check("PP6 total", PPA.get(6, ""), r"With no restriction there are \(@\) committees.", len(c6))
check("PP6 both", PPA.get(6, ""), r"from the other 8 candidates in \(@\) ways.", ncount(c6, lambda c: 0 in c and 1 in c))
check("PP6", PPA.get(6, ""), r"\[\text{number of committees}=@.\]", ncount(c6, lambda c: not (0 in c and 1 in c)))
has("PP6 question", PPQ.get(6, ""), "Peter and May are two of ten candidates for a committee.")
# ---------------------------------------------------------------- PP 7: nine points read from the figure
try:
    svg7, segs7, _, _ = svg_lines("abb20pts")
    d7 = [(Fr(x), Fr(y)) for x, y in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="5"', svg7)]
    colf = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) == 0
    trip = list(combinations(range(len(d7)), 3))
    coll = [t for t in trip if colf(*(d7[i] for i in t))]
    (x1, y1, x2, y2), = segs7
    L_ = ((Fr(x1), Fr(y1)), (Fr(x2), Fr(y2)))
    online = [p for p in d7 if colf(L_[0], L_[1], p)]
    report(len(d7) == 9 and len(online) == 4 and all(set(t) <= {d7.index(p) for p in online} for t in coll), "PP7 figure",
           f"{len(d7)} points, {len(online)} on the drawn line, collinear triples only among those: {len(coll)}")
    check("PP7", PPA.get(7, ""), r"\[\text{number of triangles}=@.\]", len(trip) - len(coll))
except Exception as ex:
    report(False, "PP7", f"ERROR {ex}")
has("PP7 question", PPQ.get(7, ""), "Nine points are drawn on a page as shown, with four of them lying on one line.")
# ---------------------------------------------------------------- PP 8: left 0..7, right 8..23
n8, n8b = 0, 0
for t in combinations(range(24), 12):
    n8 += 1
    if sum(1 for x in t if x < 8) > 6:
        n8b += 1
b8 = PPA.get(8, "")
check("PP8 (i)", b8, r"\[\text{number of ways}=@.\]", n8)
aligned("PP8 (ii)", b8, r"\[\begin{aligned}\text{number of ways}&=@\end{aligned}\]", n8b)
has("PP8 question", PPQ.get(8, ""), "8 left-handed students and 16 right-handed students")
# ---------------------------------------------------------------- PP 9: twelve people into two groups of six
div9 = {frozenset([frozenset(g), frozenset(set(range(12)) - set(g))]) for g in combinations(range(12), 6)}
b9 = PPA.get(9, "")
check("PP9 12C6", b9, r"in \(@\) ways, leaves", k_subsets(12, 6))
check("PP9 (i)", b9, r"\[\text{number of ways}=@.\]" + "\n" + "<p>(ii)", len(div9))
check("PP9 (ii)", b9, r"so nothing is counted twice:</p>" + "\n" + r"\[\text{number of ways}=@.\]", ncount(div9, lambda d: any({0, 1} <= g for g in d)))
# ---------------------------------------------------------------- PP 10: dancers
sols = [n_ for n_ in range(3, 40) if k_subsets(n_, 3) == 3 * k_subsets(n_, 2)]
b10 = PPA.get(10, "")
try:
    lines = find(b10, r"\[\begin{aligned}@\end{aligned}\]").split("\\\\")
    eqs = [aligned_tex(x).split("=") for x in lines]
    ok = all(tex_eval(l_, n=n_) == tex_eval(r_, n=n_) for l_, r_ in eqs for n_ in sols) and all(
        (tex_eval(eqs[1][0], n=n_) == k_subsets(n_, 3)) and (tex_eval(eqs[1][1], n=n_) == 3 * k_subsets(n_, 2)) for n_ in range(3, 15))
    report(ok, "PP10 equation", f"printed {lines}; both sides are the enumerated counts, equal at n = {sols}")
    fin = find(b10, r"\[\dfrac{n-2}{6}=\dfrac{3}{2},\qquad n-2=9,\qquad @\]")
    ok = tex_eval(r"\dfrac{n-2}{6}", n=11) == Fr(3, 2) and tex_eval("n-2", n=11) == 9
    report(sols == [11] and fin == "n=11." and ok and "There are 11 dancers." in b10, "PP10", f"solutions in 3..39: {sols}; printed {fin}")
    chk = find(b10, r"Check: \(@\).")
    a_, b_, c_, d_ = chk.split("=")
    report(tex_eval(a_) == tex_eval(b_) == tex_eval(c_) == tex_eval(d_) == k_subsets(11, 3) == 3 * k_subsets(11, 2), "PP10 check", chk)
except Exception as ex:
    report(False, "PP10", f"ERROR {ex}")
# ---------------------------------------------------------------- PP 11: tiles
n11 = ncount(((t, b) for t in combinations(range(10), 4) for b in combinations(range(10), 6)), lambda tb_: len(set(tb_[0]) & set(tb_[1])) == 2)
check("PP11", PPA.get(11, ""), r"\[\text{number of ways}=@.\]", n11)
try:
    svg11 = read(os.path.join("svg", "abb24tiles.svg"))
    tl = re.findall(r'<rect class="tile" data-row="(\d)" data-col="(\d+)"[^>]*fill="(#[0-9a-f]+)"', svg11)
    top_ = {int(c) for r_, c, f in tl if r_ == "0" and f != "#ffffff"}
    bot_ = {int(c) for r_, c, f in tl if r_ == "1" and f != "#ffffff"}
    report(len(tl) == 20 and len(top_) == 4 and len(bot_) == 6 and len(top_ & bot_) == 2, "PP11 figure", f"example: top {sorted(top_)}, bottom {sorted(bot_)}, overlap {sorted(top_ & bot_)}")
    pieces = [find(PPA[11], t) for t in (r"top row: \(@\) ways.", r"above shaded tiles: \(@\) ways.", r"under a shaded top tile: \(@\) ways.")]
    report([chain_ok(p, v)[0] for p, v in zip(pieces, (k_subsets(10, 4), k_subsets(4, 2), k_subsets(6, 4)))] == [True] * 3, "PP11 steps", f"{pieces}")
except Exception as ex:
    report(False, "PP11 figure", f"ERROR {ex}")
has("PP11 question", PPQ.get(11, ""), "exactly two shaded tiles in the top row are directly above a shaded tile in the bottom row")

report(not any(s in LES + ANS for s in ("Ascham School, 2024", "Caringbah High School, 2021", "Killara High School, 2021", "North Sydney Boys", "Pymble")),
       "left-out items", "Ascham 2024 Q14(e), Caringbah 2021 Q7, Killara 2021 Q7, NSB 2020 Q14(a) and PLC 2023 Q14(b) are not used")
print(f"\n{COUNT[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{COUNT[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
