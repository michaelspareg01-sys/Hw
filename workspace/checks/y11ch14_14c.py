"""Check of Lesson 14C (Ordered selections and grouping), tied to the printed HTML.

Reads the printed answers from workspace/build/y11ch14/a_14c.html (lesson
examples C1-C3, textbook homework, past-paper worked solutions) and the printed
results in the concept boxes and worked examples of l14c.html. In a template
'@' marks the printed value; each template must match exactly once in its
block, otherwise the item FAILS. Printed LaTeX is converted to an exact value
(fractions.Fraction; \\times, +, -, powers, factorials, \\dfrac) and compared
with a count made independently from the question, by brute-force enumeration
with itertools wherever it is feasible (permutations of the actual letters,
people, digits, cards, dice). Where a full enumeration is too large (10! lines
of people, 13! books) the count is made by enumerating the positions of the
named people, or the pattern of subjects, and multiplying by the free
orderings; that method is first checked against a full enumeration on a
smaller case.

For every printed chain such as "6!\\times2!\\times2!=2880" EVERY '='-separated
piece must equal the computed count, so a wrong factor in the working fails as
well as a wrong final answer. The terms of printed sums such as "350+120-30"
are checked one by one against the counts of each case and of the overlap. Key
data of each question as printed in l14c.html (numbers of people, letters,
digits, limits) are re-read so that the truths encode the printed questions.
Past-paper structure is checked too: marks add to the intro total, time is
1.5 x marks rounded to the nearest 5 minutes (halves up), numbering, source
labels identical in both files, one hint each, part marks, and each MC letter
is the option equal to the count.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_14c.py
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

from math import isqrt, prod


# ---------------------------------------------------------------- blocks
ANS = read("a_14c.html")
LES = read("l14c.html")
HEAD = "{{ahead:Lesson 14C | Ordered selections and grouping}}"


def ans_blocks(text):
    # labels are kept with their maths by <span style="white-space:nowrap"> wrappers (layout only): strip them
    return {an.strip(): ab.replace('<span style="white-space:nowrap">', "").replace("</span>", "")
            for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S)}


A = ans_blocks(ANS)
sec = ANS.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_14c.html")
report(ANS.count(HEAD) == 2 and ANS.startswith(HEAD) and sec[0].rstrip().endswith(HEAD), "answers headings",
       "the ahead line opens the file and precedes the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}
pps = LES.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l14c.html")
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
    """kind: 'demo' or 'attempt' (one each per concept)."""
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
    """Every '='-separated piece of the printed chain equals truth."""
    pieces = [p for p in tex.split("=") if p.strip()]
    vals = [tex_eval(p, **var) for p in pieces]
    return all(v == Fr(truth) for v in vals), vals


def check(label, block, template, truth):
    try:
        tex = find(block, template)
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex.strip()} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:  # missing or unparsable value fails loudly
        report(False, label, f"ERROR {ex}")


def aligned(label, block, template, truth):
    """A printed \\begin{aligned} display: every '=' piece of every row equals truth."""
    try:
        tex = find(block, template)
        tex = tex.replace("\\\\", "").replace("&", "").strip().rstrip(".").rstrip(",")
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def terms(label, block, template, truths, total):
    """A printed sum such as 350+120-30=440: each term is checked against its case count."""
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
    """Split '<b>a</b> ... <b>b</b> ...' into {letter: text}."""
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


def count(it, cond=lambda x: True):
    return sum(1 for x in it if cond(x))


def num(t):
    return int("".join(t))


VOW = set("AEIOU")


def adjacent(p, x, y):
    return abs(p.index(x) - p.index(y)) == 1


def contiguous(p, items):
    pos = sorted(p.index(x) for x in items)
    return pos[-1] - pos[0] == len(items) - 1


def vowels_together(word):
    v = [c for c in word if c in VOW]
    return count(permutations(word), lambda p: contiguous(p, v))


def numbers_from(digits):
    return [num(t) for r in range(1, len(digits) + 1) for t in permutations(digits, r)]


def roundhalf5(x):
    return 5 * int(Fr(x) / 5 + Fr(1, 2))


# ================================================================ lesson concept boxes and worked examples
c1 = concept(1)
try:
    report(all(tex_eval(find(c1, tpl)) == factorial(k) == count(permutations(range(k)))
               for tpl, k in ((r"The five groups can be ordered in \(@\) ways", 5),
                              (r"the couple can be ordered within their group in \(@\) ways", 2),
                              (r"the three girls within their group in \(@\) ways", 3))),
           "L concept 1 orders", "5! orders of 5 groups, 2! of the couple, 3! of the girls (enumerated)")
except Exception as ex:
    report(False, "L concept 1 orders", f"ERROR {ex}")
report("{{svg:groups9}}" in c1 and os.path.exists(os.path.join(SRC, "svg", "groups9.svg")), "L figure", "groups9 figure inserted and built")
try:
    svg = read(os.path.join("svg", "groups9.svg"))
    labels = re.findall(r">([^<>]+)</text>", svg)
    report(labels[:10:2] == ["G B", "G G G", "B", "B", "B"], "L figure groups", f"{labels[:10:2]}: five groups, couple and three girls")
except Exception as ex:
    report(False, "L figure groups", f"ERROR {ex}")


def queue(boys, girls, couple_pair, group, others_free=True):
    """Count queues of boys B0.. and girls G0..: the couple (G0, B0) adjacent and the
    girls in `group` contiguous. Full enumeration of all orders of the people."""
    people = [f"B{i}" for i in range(boys)] + [f"G{i}" for i in range(girls)]
    return count(permutations(people), lambda p: adjacent(p, *couple_pair) and contiguous(p, group))


we9 = les_block("Worked example 9</span>", "<!-- ============ Concept 2")
n_we9 = queue(4, 4, ("G0", "B0"), ["G1", "G2", "G3"])
check("L WE9", we9, r"\[\text{Hence number of ways}=@.\]", n_we9)
try:
    cells = [tex_eval(c.strip("\\()")) for c in re.findall(r"<td>(.*?)</td>", we9)]
    report(cells == [factorial(5), 2, 6] and cells[0] * cells[1] * cells[2] == n_we9, "L WE9 box cells", f"{cells}")
except Exception as ex:
    report(False, "L WE9 box cells", f"ERROR {ex}")
has("L WE9 question", we9, "Four boys and four girls form a queue at the bus stop. There is one couple who want to stand together, the other three girls want to stand together, but the other three boys don’t care where they stand.")

we10 = les_block("Worked example 10</span>", "<!-- ============ Concept 3")
w7 = list(permutations("ABCDEFG"))
aligned("L WE10 total", we10, r"\text{Number of orderings without restriction}&=@\\", len(w7))
aligned("L WE10 together", we10, r"\text{Number of orderings with A and E together}&=@\end{aligned}", count(w7, lambda p: adjacent(p, "A", "E")))
aligned("L WE10 apart", we10, r"\text{Hence number of orderings with A and E apart}&=@\end{aligned}", count(w7, lambda p: not adjacent(p, "A", "E")))
has("L WE10 question", we10, "seven-letter words can be formed from the letters A, B, C, D, E, F, G if the vowels must be separated by at least one consonant")

c3 = concept(3)
W = range(1000)                                             # whole numbers less than 1000, zero included
we11 = les_block("Worked example 11</span>", "<!-- ============ Homework")
oa, ma = [n for n in W if n % 2 and n > 500], [n for n in W if n % 5 == 0 and n < 200]
ob, mb = [n for n in W if n % 2 and n > 200], [n for n in W if n % 5 == 0 and n < 500]
for lab, tpl, t in (("a odd", r"There are @ odd numbers between 500", len(oa)),
                    ("a mult 5", r"and there are @ multiples of 5 less than 200", len(ma)),
                    ("a total", r"so the total number is @.</p>", len(set(oa) | set(ma))),
                    ("b odd", r"There are @ odd numbers between 200", len(ob)),
                    ("b mult 5", r"and there are @ multiples of 5 less than 500", len(mb)),
                    ("b overlap", r"from 200 to 500 there are @ odd numbers that are multiples of 5", len(set(ob) & set(mb)))):
    try:
        before, after = tpl.split("@")
        hits = re.findall(re.escape(before) + r"(\d+)" + re.escape(after), we11)
        if len(hits) != 1:
            raise LookupError(f"template matched {len(hits)} times: {tpl!r}")
        v = int(hits[0])
        report(v == t, f"L WE11 {lab}", f"printed {v}, computed {t}")
    except Exception as ex:
        report(False, f"L WE11 {lab}", f"ERROR {ex}")
report(not set(oa) & set(ma), "L WE11 a no overlap", "the two cases of part a are disjoint")
terms("L WE11 b total", we11, r"\[\text{Total}=@.\]", [len(ob), len(mb), len(set(ob) & set(mb))], len(set(ob) | set(mb)))
try:
    f = find(les_block("The same principle with sets", "Tutor demo"), r"\[@\]")
    l_, r_ = f.split("=")
    U = [(set(oa), set(ma)), (set(ob), set(mb))]
    ok = l_ == "|A\\cup B|" and r_.rstrip(".") == "|A|+|B|-|A\\cap B|" and all(len(a | b) == len(a) + len(b) - len(a & b) for a, b in U)
    report(ok, "L addition rule", f"{f} (holds for both pairs of cases in WE11)")
except Exception as ex:
    report(False, "L addition rule", f"ERROR {ex}")
has("L WE11 question", we11, "How many whole numbers less than 1000 are odd and greater than 200, or multiples of 5 and less than 500?")

# ================================================================ lesson examples C1-C3 (answers)
for c in ("C1", "C2", "C3"):
    if c not in A or "<b>Your turn.</b>" not in A[c]:
        report(False, c, "answer block missing")
        A[c] = "<b>Your turn.</b>"


def ab(c):
    td, yt = A[c].split("<b>Your turn.</b>")
    return td, yt


# ---- C1
q_td, q_yt = ex_block(c1, "demo"), ex_block(c1, "attempt")
has("C1 TD a question", q_td, "Five boys and three girls form a queue at the canteen. There is one couple who want to stand together, the other two girls want to stand together, but the other four boys don’t care")
has("C1 TD b question", q_td, "the word CAMPING are possible if the vowels must be together")
has("C1 YT a question", q_yt, "Three boys and three girls form a queue. There is one couple who want to stand together, the other two girls want to stand together, but the other two boys don’t care")
has("C1 YT b question", q_yt, "the word TRAIN are possible if the vowels must be together")
td, yt = ab("C1")
try:
    p = parts(td, "ab")
    first_math("C1 TD a", p["a"], queue(5, 3, ("G0", "B0"), ["G1", "G2"]))
    first_math("C1 TD b", p["b"], vowels_together("CAMPING"))
    p = parts(yt, "ab")
    first_math("C1 YT a", p["a"], queue(3, 3, ("G0", "B0"), ["G1", "G2"]))
    first_math("C1 YT b", p["b"], vowels_together("TRAIN"))
except Exception as ex:
    report(False, "C1", f"ERROR {ex}")

# ---- C2
c2 = concept(2)
q_td, q_yt = ex_block(c2, "demo"), ex_block(c2, "attempt")
has("C2 TD a question", q_td, "six-letter words can be formed from the letters A, B, C, D, E, F if the vowels must be separated")
has("C2 TD b question", q_td, "nine people stand in a line if two particular people refuse to stand next to each other")
has("C2 YT a question", q_yt, "five-letter words can be formed from the letters A, B, C, D, E if the vowels must be separated")
has("C2 YT b question", q_yt, "six people sit in a row if two particular people refuse to sit next to each other")
td, yt = ab("C2")
try:
    p = parts(td, "ab")
    first_math("C2 TD a", p["a"], count(permutations("ABCDEF"), lambda w: not adjacent(w, "A", "E")))
    first_math("C2 TD b", p["b"], count(permutations(range(9)), lambda w: not adjacent(w, 0, 1)))
    p = parts(yt, "ab")
    first_math("C2 YT a", p["a"], count(permutations("ABCDE"), lambda w: not adjacent(w, "A", "E")))
    first_math("C2 YT b", p["b"], count(permutations(range(6)), lambda w: not adjacent(w, 0, 1)))
except Exception as ex:
    report(False, "C2", f"ERROR {ex}")

# ---- C3
q_td, q_yt = ex_block(c3, "demo"), ex_block(c3, "attempt")
td, yt = ab("C3")


def cases(lo_odd, hi_mult):
    odd = {n for n in W if n % 2 and n > lo_odd}
    mult = {n for n in W if n % 5 == 0 and n < hi_mult}
    return odd, mult


try:
    for blk, qb, lab, specs in ((td, q_td, "TD", ((600, 300), (300, 600))), (yt, q_yt, "YT", ((700, 100), (400, 700)))):
        p = parts(blk, "abc")
        for L, (lo, hi) in zip("ab", specs):
            has(f"C3 {lab} {L} question", qb, f"odd and greater than {lo}, or multiples of 5 and less than {hi}?")
            o, m = cases(lo, hi)
            tex = maths(p[L])[0]
            tr = [len(o), len(m)] + ([len(o & m)] if o & m else [])
            terms(f"C3 {lab} {L}", "\\(" + tex + "\\)", r"\(@\)", tr, len(o | m))
    has("C3 TD c question", q_td, "using each of the digits 2, 3, 5 and 7 at most once, if the result must be at least 500")
    has("C3 YT c question", q_yt, "using each of the digits 3, 5 and 7 at most once, if the result must be at least 60")
    n4 = numbers_from("2357")
    terms("C3 TD c", "\\(" + maths(parts(td, "abc")["c"])[0] + "\\)", r"\(@\)",
          [count(n4, lambda x: x >= 1000), count(n4, lambda x: 500 <= x < 1000)], count(n4, lambda x: x >= 500))
    n3 = numbers_from("357")
    terms("C3 YT c", "\\(" + maths(parts(yt, "abc")["c"])[0] + "\\)", r"\(@\)",
          [count(n3, lambda x: x >= 100), count(n3, lambda x: 60 <= x < 100)], count(n3, lambda x: x >= 60))
    report(sorted(x for x in n3 if 60 <= x < 100) == [73, 75] and "plus 73 and 75" in yt, "C3 YT c two-digit", "the two-digit numbers are 73 and 75")
    ov = sorted(cases(300, 600)[0] & cases(300, 600)[1])
    report("(the overlap is 305, 315, …, 595)" in td and ov == list(range(305, 596, 10)), "C3 TD b overlap list", f"{ov[0]}..{ov[-1]} step 10, {len(ov)} numbers")
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


for w in ("BOARDS", "RIO", "QUIT", "TROUNCE"):
    has(f"TB1 word {w}", Q[1], f"</span>{w}</span>")
tbcheck(1, "abcd", [vowels_together(w) for w in ("BOARDS", "RIO", "QUIT", "TROUNCE")])
ms = list(permutations("MATHS"))
tbcheck(2, "ab", [count(ms, lambda p: adjacent(p, "T", "H")), count(ms, lambda p: p.index("H") == p.index("T") + 1)])
has("TB3 question", Q[3], "if Andrew and Becky sit together and Dion and Ellie sit together")
single(3, count(permutations("ABCDE"), lambda p: adjacent(p, "A", "B") and adjacent(p, "D", "E")))


# Q4: 13 books. Enumerate the distinct subject patterns (60 060 strings of 3 M, 6 S, 4 E), keep those
# with each subject in one block, and multiply by the orders of the books inside their subject slots.
# The method is checked first against a full enumeration with 2 + 3 + 2 books.
def shelf(m, s, e, full=False):
    if full:
        books = [("M", i) for i in range(m)] + [("S", i) for i in range(s)] + [("E", i) for i in range(e)]
        return count(permutations(books), lambda p: all(contiguous(p, [b for b in books if b[0] == k]) for k in "MSE"))
    n = m + s + e                                       # pattern = places of the M books, then of the S books
    pats = [(pm, ps) for pm in combinations(range(n), m) for ps in combinations([i for i in range(n) if i not in pm], s)]
    ok = count(pats, lambda q: contiguous_idx(list(q[0])) and contiguous_idx(list(q[1]))
               and contiguous_idx([i for i in range(n) if i not in q[0] and i not in q[1]]))
    return ok * factorial(m) * factorial(s) * factorial(e)


def contiguous_idx(ix):
    return ix[-1] - ix[0] == len(ix) - 1


report(shelf(2, 3, 2) == shelf(2, 3, 2, full=True), "TB4 method", f"pattern method {shelf(2, 3, 2)} = full enumeration {shelf(2, 3, 2, full=True)} on 7 books")
has("TB4 question", Q[4], "three different Maths books, six different Science books and four different English books")
single(4, shelf(3, 6, 4))
so = list(permutations("SOLAR"))
ok5 = count(so, lambda p: not (p[0] in VOW and p[1] in VOW))
try:
    pa = tb(5, "ab")
    first_math("TB5a", pa["a"], ok5)
    tex = maths(pa["a"])[0].split("=")[0]
    t1, t2 = tex.split("+")
    report(tex_eval(t1) == count(so, lambda p: p[0] in VOW and p[1] not in VOW) and tex_eval(t2) == count(so, lambda p: p[0] not in VOW),
           "TB5a cases", f"{t1} = starts with a vowel, {t2} = starts with a consonant")
    first_math("TB5b", pa["b"], ok5)
    tex = maths(pa["b"])[0].split("=")[0]
    report(tex_eval(tex.split("-")[1]) == count(so, lambda p: p[0] in VOW and p[1] in VOW), "TB5b complement", f"{tex}: subtracted term = both first positions vowels")
except Exception as ex:
    report(False, "TB5", f"ERROR {ex}")


# Q6: seats 0 driver, 1 front passenger, 2 and 3 back. F father, M mother, C and K children.
def car_ok(p):                                          # p[seat] = person
    if p[0] not in "FM":
        return False
    if p[0] == "F" and p.index("M") < 2:                # father drives: mother in the back
        return False
    return p.index("F") < 2                             # father always in a front seat


cars = [p for p in permutations("FMCK") if car_ok(p)]
try:
    m6 = maths(A["6"])
    report(len(m6) == 3 and tex_eval(m6[0]) == count(cars, lambda p: p[0] == "F") and tex_eval(m6[1]) == count(cars, lambda p: p[0] == "M")
           and tex_eval(m6[2]) == len(cars), "TB6", f"printed {m6}, computed father {count(cars, lambda p: p[0] == 'F')}, mother {count(cars, lambda p: p[0] == 'M')}, total {len(cars)}")
except Exception as ex:
    report(False, "TB6", f"ERROR {ex}")
n789 = numbers_from("789")
try:
    m7 = maths(A["7"])
    ok = (chain_ok(m7[0], count(n789, lambda x: x >= 100))[0] and chain_ok(m7[1], count(n789, lambda x: 80 <= x < 100))[0]
          and tex_eval(m7[2]) == count(n789, lambda x: x >= 80))
    report(ok and len(m7) == 3, "TB7", f"printed {m7}, computed {count(n789, lambda x: x >= 80)}")
except Exception as ex:
    report(False, "TB7", f"ERROR {ex}")
uf = list(permutations("UNIFORM"))
tbcheck(8, "abcd", [count(uf, lambda p: {p[0], p[3], p[6]} == {"U", "I", "O"}), count(uf, lambda p: p[0] == "U" and p[-1] == "M"),
                    count(uf, lambda p: set(p[3:]) == set("NFRM")), count(uf, lambda p: p.index("M") > p.index("U"))])
bh = list(permutations("BEHAVING"))
tbcheck(9, "abc", [count(bh, lambda p: p[-2:] == ("N", "G")), count(bh, lambda p: set(p[:3]) == {"E", "A", "I"}), count(bh, lambda p: contiguous(p, "EAI"))])
tq = list(permutations(range(6)))                       # question 0 shortest, 5 longest
tbcheck(10, "ab", [count(tq, lambda p: p[0] == 0 and p[-1] == 5), count(tq, lambda p: adjacent(p, 0, 5))])
try:
    tex = maths(A["11"])[0]
    lhs, rhs = tex.split("=")
    seqs = [s for k in range(1, 11) for s in product(".-", repeat=k)]
    shown = [int(x) for x in re.findall(r"\d+", lhs)]
    report(int(rhs) == len(seqs) and shown == [2 ** k for k in (1, 2, 3)] + [2 ** 10] and "\\cdots" in lhs, "TB11",
           f"printed {tex}; {len(seqs)} sequences of 1 to 10 symbols enumerated")
except Exception as ex:
    report(False, "TB11", f"ERROR {ex}")
row = list(permutations(["B0", "B1", "B2", "B3", "G0", "G1", "G2", "G3"]))
tbcheck(12, "ab", [count(row, lambda p: all(p[i][0] != p[i + 1][0] for i in range(7))),
                   count(row, lambda p: contiguous(p, ["B0", "B1", "B2", "B3"]) and contiguous(p, ["G0", "G1", "G2", "G3"]))])
ph = list(permutations("PHYSICAL", 5))
tbcheck(13, "abcdef", [count(ph, lambda w: not set(w) & {"I", "A"}), count(ph, lambda w: w[0] == "P" and w[-1] == "S"),
                       count(ph, lambda w: w[0] in VOW), count(ph, lambda w: "Y" in w),
                       count(ph, lambda w: "I" in w and "A" in w and adjacent(w, "I", "A")),
                       count(ph, lambda w: "L" in w and "A" in w and w.index("A") == w.index("L") + 1)])
has("TB13 question", Q[13], "Five-letter words are formed without repetition from the letters of PHYSICAL.")
inc = list(permutations("INCLUDE"))
gap = lambda p: abs(p.index("N") - p.index("D")) - 1
alt = lambda w: all((w[i] in VOW) != (w[i + 1] in VOW) for i in range(len(w) - 1))
tbcheck(14, "abcdefg", [len(inc), count(inc, lambda p: p[0] != "I"), count(inc, lambda p: p[-1] == "L"), count(inc, alt),
                        count(inc, lambda p: p.index("C") == p.index("D") + 1), count(inc, lambda p: gap(p) == 2), count(inc, lambda p: gap(p) > 2)])
inr = list(product("INCLUDE", repeat=7))                # 823 543 words with repetition
tbcheck(15, "abcd", [len(inr), count(inr, lambda w: w[0] != "I"), count(inr, lambda w: w[-1] == "L"), count(inr, alt)])
has("TB15 question", Q[15], "Repeat parts <b>a</b>–<b>d</b> of the previous question if repetition is allowed.")


# Q16: people 0 and 1 are the particular people. Enumerate the places of the named people only,
# times (n - named)! for the others; checked against a full enumeration for n = 7.
def line(n, cond, named):
    return count(permutations(range(n), named), lambda pl: cond(pl, n)) * factorial(n - named)


c_end = lambda pl, n: pl[0] in (0, n - 1)
c_next = lambda pl, n: abs(pl[0] - pl[1]) == 1
c_noend = lambda pl, n: all(x not in (0, n - 1) for x in pl)
for cond, k, lab in ((c_end, 1, "end"), (c_next, 2, "next"), (c_noend, 2, "not at ends")):
    full = count(permutations(range(7)), lambda p: cond([p.index(i) for i in range(k)], 7))
    report(full == line(7, cond, k), f"TB16 method {lab}", f"named-place method = full enumeration ({full}) for n = 7")
try:
    blk = A["16"]
    apart_ = blk.split("<b>b</b>")[0]
    for lab, tpl, t in (("a i", r"<b>a</b> i&nbsp;\(@\)", factorial(10)), ("a ii", r" ii&nbsp;\(@\) &nbsp; iii", line(10, c_end, 1)),
                        ("a iii", r" iii&nbsp;\(@\) &nbsp; iv", line(10, c_next, 2)), ("a iv", r" iv&nbsp;\(@\)<br>", line(10, c_noend, 2))):
        check(f"TB16{lab}", apart_, tpl, t)
    bpart = blk.split("<b>b</b>")[1]
    for lab, tpl, cond, k in (("b i", r"</b> i&nbsp;\(@\) &nbsp; ii&nbsp;", c_end, 1), ("b ii", r" ii&nbsp;\(@\) &nbsp; iii", c_next, 2), ("b iii", r" iii&nbsp;\(@\)", c_noend, 2)):
        tex = find("</b>" + bpart, tpl)
        bad = [n for n in range(3, 9) if tex_eval(tex, n=n) != count(permutations(range(n)), lambda p: cond([p.index(i) for i in range(k)], n))]
        report(not bad, f"TB16{lab}", f"printed {tex} = full enumeration for n = 3..8" + (f" FAILS at {bad}" if bad else ""))
except Exception as ex:
    report(False, "TB16", f"ERROR {ex}")
cin = [f"B{i}" for i in range(5)] + [f"G{i}" for i in range(4)]
single(17, count(permutations(cin), lambda p: adjacent(p, "B0", "B1") and contiguous(p, ["B2", "B3", "B4"])))
has("TB17 question", Q[17], "Five boys and four girls form a queue at the cinema. There are two brothers who want to stand together, the remaining three boys wish to stand together")
eq = list(permutations(range(8)))                       # places 0-3 left queue, 4-7 right; person 0 Jim, 1 Sean, 2 Liam
tbcheck(18, "abc", [len(eq), count(eq, lambda p: p.index(0) < 4), count(eq, lambda p: (p.index(1) < 4) == (p.index(2) < 4))])
sw = list(permutations([1, 2, 3, 4, 5, 6, 7, 8]))     # finishing order by lane
tbcheck(19, "ab", [count(sw, lambda p: p.index(2) == p.index(5) + 1), count(sw, lambda p: p.index(2) > p.index(5))])
hs = list(product(range(5), repeat=5))                  # hs[b] = hostel of backpacker b; 0 and 1 are brother and sister
tbcheck(20, "abc", [len(hs), count(hs, lambda h: len(set(h)) == 5), count(hs, lambda h: h[0] == h[1] and all(x != h[0] for x in h[2:]))])
has("TB20 question", Q[20], "the other three can go to any of the other youth hostels")
n21 = [x for x in numbers_from("13589") if x < 4000]
tbcheck(21, "abcd", [len(n21), count(n21, lambda x: x % 2), count(n21, lambda x: x % 5 == 0), count(n21, lambda x: x % 3 == 0)])
has("TB21 question", Q[21], "Numbers less than 4000 are formed from the digits 1, 3, 5, 8 and 9, without repetition.")


def der(n):
    return count(permutations(range(n)), lambda p: all(p[i] != i for i in range(n)))


try:
    got = {int(k): int(v.replace("\\,", "")) for k, v in re.findall(r"D\((\d)\)=(\d+(?:\\,\d+)*)", A["22"])}
    exp = {n: der(n) for n in range(1, 9)}
    report(got == exp, "TB22", f"printed {got}, enumerated {exp}")
    report(all(der(n) == (n - 1) * (der(n - 1) + der(n - 2)) for n in range(3, 9)) and der(5) == 4 * der(4) + 4 * der(3), "TB22 recurrence",
           "D(n) = (n-1)(D(n-1) + D(n-2)) for n = 3..8, so D(5) = 4D(4) + 4D(3) as printed in part b")
    report(find(Q[22], r"Hence explain why" + "\n" + r"\[@\]") == "D(5)=4\\times D(4)+4\\times D(3).", "TB22 b printed", "part b formula as in the textbook")
    has("TB22 example", Q[22], "DABC is a derangement of ABCD, but DACB is not")
    report(all(i != "ABCD".index(c) for i, c in enumerate("DABC")) and not all(i != "ABCD".index(c) for i, c in enumerate("DACB")), "TB22 example check", "DABC deranged, DACB not")
except Exception as ex:
    report(False, "TB22", f"ERROR {ex}")
qs = sorted(Q)
report(qs == list(range(1, 23)), "TB question numbers", f"{qs}")
ans_q = sorted(int(k) for k in A if k.isdigit())
report(ans_q == list(range(1, 23)), "TB answer numbers", f"{ans_q} (22b is an explanation; every question has a printed answer)")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M == 12, "lesson marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    print(f"NOTE     {M} marks is below 15: house rule 8 (no other clean 14C school item; the rest need 14D), see the task report")
    note = re.search(r'<p class="small">(.*?)</p>', pps[1], re.S).group(1)
    probs = [n_ for n_ in PPQ if "probability" in PPQ[n_]]
    report(probs == [5, 8] and "PP 5 and PP 8 are probability questions" in note and "shorter than usual" in note, "intro note",
           f"probability items {probs}; note names PP 5 and PP 8 and the short exam")
    report(T == roundhalf5(Fr(3, 2) * M), "lesson time", f"{T} min for {M} marks (1.5 x {M} = {float(1.5 * M)})")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for n_ in PPQ:
        sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[n_], re.S)]
        tot = int(re.search(r'<span class="mk">(\d+) marks?</span>', PPQ[n_]).group(1))
        if sub:
            report(sum(sub) == tot, f"PP{n_} part marks", f"parts {sub} sum {sum(sub)}, block {tot}")
        src_q = re.search(r"^(.*?)</span>", PPQ[n_]).group(1)
        src_a = re.search(r"^(.*?)</span>", PPA.get(n_, "")).group(1) if n_ in PPA else None
        report(src_q == src_a, f"PP{n_} source label", src_q)
        report(PPQ[n_].count('<div class="hint"><b>Hint:</b>') == 1, f"PP{n_} hint", "exactly one hint")
except Exception as ex:
    report(False, "lesson structure", f"ERROR {ex}")


def mc(pp, value, pattern, conv=lambda v: tex_eval(v.replace("&#8239;", ""))):
    try:
        opts = {k: conv(v) for k, v in re.findall(pattern, PPQ[pp])}
        letter = re.search(r"<b>Answer \(?([A-D])\)?\.</b>", PPA[pp]).group(1)
        best = [k for k, v in opts.items() if v == value]
        report(len(opts) == 4 and best == [letter], f"PP{pp} MC letter", f"options {[(k, str(v)) for k, v in opts.items()]}; printed {letter}; option equal to {value} is {best}")
    except Exception as ex:
        report(False, f"PP{pp} MC letter", f"ERROR {ex}")


# ---------------------------------------------------------------- PP 1  5 boys and 3 girls, girls together
kids = [f"B{i}" for i in range(5)] + [f"G{i}" for i in range(3)]
q8 = list(permutations(kids))
n1 = count(q8, lambda p: contiguous(p, ["G0", "G1", "G2"]))
has("PP1 question", PPQ.get(1, ""), "5 boys and 3 girls stand in a queue if the girls all stand next to each other")
check("PP1", PPA.get(1, ""), r"\[\text{number of ways}=@.\]", n1)
check("PP1 option A", PPA.get(1, ""), r"Option A, \(@\), ignores", len(q8))
check("PP1 option B", PPA.get(1, ""), r"Option B, \(@\), forgets", count(q8, lambda p: p.index("G0") < p.index("G1") < p.index("G2") and contiguous(p, ["G0", "G1", "G2"])))
mc(1, n1, r"<span>([A-D])\. ([\d&#;]+)</span>")

# ---------------------------------------------------------------- PP 2  OLYMPIC with C and L together
ol = list(permutations("OLYMPIC"))
report(len(set("OLYMPIC")) == 7, "PP2 distinct letters", "OLYMPIC")
check("PP2", PPA.get(2, ""), r"\[\text{number of arrangements}=@.\]", count(ol, lambda p: adjacent(p, "C", "L")))
check("PP2 option B", PPA.get(2, ""), r"Option (B), \(@\), forgets", count(ol, lambda p: p.index("L") == p.index("C") + 1))
mc(2, count(ol, lambda p: adjacent(p, "C", "L")), r"<span>\(([A-D])\) (\d+)</span>")

# ---------------------------------------------------------------- PP 3  EPSILON vowels adjacent (number)
ep = list(permutations("EPSILON"))
n_ep = count(ep, lambda p: contiguous(p, "EIO"))
check("PP3", PPA.get(3, ""), r"\[\text{number of arrangements}=@.\]", n_ep)
has("PP3 question", PPQ.get(3, ""), "ii) the three vowels are adjacent to each other.")
report("PP 4" not in PPA.get(3, "") and "PP 4" not in PPQ.get(3, ""), "PP3 no cross-reference", "no reference to the removed EPSILON item")

# ---------------------------------------------------------------- PP 4  3 girls and 3 boys on a bench, girls apart
bench = list(permutations(["G0", "G1", "G2", "B0", "B1", "B2"]))
apart = lambda p: all(not (p[i][0] == "G" and p[i + 1][0] == "G") for i in range(5))
n3 = count(bench, apart)
check("PP4", PPA.get(4, ""), r"\[\text{number of ways}=@.\]", n3)
check("PP4 boys", PPA.get(4, ""), r"seat them in a row in \(@\) ways", count(permutations("BCD")))
try:
    v = int(find(PPA[4], r"This leaves @ gaps"))
    report(v == 3 + 1, "PP4 gaps", f"{v} gaps around 3 boys")
except Exception as ex:
    report(False, "PP4 gaps", f"ERROR {ex}")
check("PP4 option A", PPA.get(4, ""), r"Option (A), \(@\), counts", count(bench, lambda p: all(p[i][0] != p[i + 1][0] for i in range(5))))
report(apart(("G0", "B0", "B1", "G1", "B2", "G2")), "PP4 GBBGBG", "GBBGBG has the girls apart but does not alternate")
mc(4, n3, r"<span>\(([A-D])\) (\d+)</span>")
has("PP4 question", PPQ.get(4, ""), "three girls and three boys be seated on a bench for a photograph if the girls must sit apart")
# ---------------------------------------------------------------- PP 5  three dice, product a perfect square
dice = list(product(range(1, 7), repeat=3))
sq = lambda t: isqrt(t[0] * t[1] * t[2]) ** 2 == t[0] * t[1] * t[2]
good = [t for t in dice if sq(t)]
blk = PPA.get(5, "")
check("PP5 |S|", blk, r"there are \(|S|=@\) equally", len(dice))
terms("PP5 cases", blk, r"P(\text{perfect square})=\dfrac{@}{216}", [count(good, lambda t: len(set(t)) == 1), count(good, lambda t: len(set(t)) == 2), count(good, lambda t: len(set(t)) == 3)], len(good))
check("PP5 probability", blk, r"\dfrac{2+30+6}{216}=@.\]", Fr(len(good), len(dice)))
check("PP5 two equal", blk, r"This gives \(@\) outcomes.", count(good, lambda t: len(set(t)) == 2))
check("PP5 all different", blk, r"placed on the dice in \(@\) ways", count(good, lambda t: len(set(t)) == 3))
report({tuple(sorted(t)) for t in good if len(set(t)) == 3} == {(2, 3, 6)} and {t for t in good if len(set(t)) == 1} == {(1, 1, 1), (4, 4, 4)},
       "PP5 sets", "only {2,3,6} with distinct scores; only 111 and 444 with equal scores")
sub = [c for r in (1, 2, 3) for c in combinations((2, 3, 6), r) if isqrt(prod(c)) ** 2 == prod(c)]
report(sub == [(2, 3, 6)], "PP5 subsets of 2, 3, 6", f"square products among products of 2, 3, 6: {sub}")
check("PP5 36", blk, r"only \(@\) is a square", 36)
mc(5, Fr(len(good), len(dice)), r"<span>\(([A-D])\) \\\((.+?)\\\)</span>")

# ---------------------------------------------------------------- PP 6  bus: Melania not immediately after Donald
bus = list(permutations(["D", "M", 1, 2, 3, 4, 5]))
aligned("PP6", PPA.get(6, ""), r"\text{number of ways}&=@\end{aligned}", count(bus, lambda p: p.index("M") != p.index("D") + 1))
check("PP6 total", PPA.get(6, ""), r"board in \(@\) orders", len(bus))
check("PP6 unacceptable", PPA.get(6, ""), r"6 groups to order, in \(@\) ways", count(bus, lambda p: p.index("M") == p.index("D") + 1))
has("PP6 question", PPQ.get(6, ""), "In how many ways can the seven people board the bus if Melania refuses to get on immediately following Donald?")

# ---------------------------------------------------------------- PP 7  8 exams, Ext 1 and Ext 2 not consecutive
ex8 = list(permutations(range(8)))
aligned("PP7", PPA.get(7, ""), r"\text{number of ways}&=@\end{aligned}", count(ex8, lambda p: not adjacent(p, 0, 1)))
check("PP7 total", PPA.get(7, ""), r"scheduled in \(@\) ways", len(ex8))
has("PP7 question", PPQ.get(7, ""), "schedule the 8 exams so that Mathematics Extension 1 and Mathematics Extension 2 are NOT consecutive")

# ---------------------------------------------------------------- PP 8  batteries
bat = list(permutations(range(11), 4))                  # batteries 0-6 good, 7-10 defective; places 1-2 projector, 3-4 air conditioner
G = lambda b: b < 7
blk = PPA.get(8, "")
check("PP8 |S|", blk, r"\[|S|=@.\]", len(bat))
check("PP8 (i) count", blk, r"There are \(@\) such selections", count(bat, lambda s: all(G(b) for b in s)))
p_i = Fr(count(bat, lambda s: all(G(b) for b in s)), len(bat))
check("PP8 (i)", blk, r"P(\text{both work})=@.\]", p_i)
check("PP8 (ii) projector", blk, r"its two batteries are good: \(@\) ways", count(permutations(range(11), 2), lambda s: G(s[0]) and G(s[1])))
rest = list(permutations([0, 1, 2, 3, 4, 7, 8, 9, 10], 2))      # after two good ones are used: 5 good and 4 defective left
check("PP8 (ii) AC total", blk, r"chosen in \(@\) ways, of which", len(rest))
check("PP8 (ii) AC good", blk, r"of which \(@\) are both good", count(rest, lambda s: G(s[0]) and G(s[1])))
check("PP8 (ii) AC fails", blk, r"So there are \(@\) ways for it to fail", count(rest, lambda s: not (G(s[0]) and G(s[1]))))
p_ii = Fr(count(bat, lambda s: G(s[0]) and G(s[1]) and not (G(s[2]) and G(s[3]))), len(bat))
aligned("PP8 (ii)", blk, r"P(\text{only the projector works})&=@\end{aligned}", p_ii)
# the ordered/unordered remark: enumerate unordered pairs (projector pair, then a pair from the rest)
un = [(a, c) for a in combinations(range(11), 2) for c in combinations([x for x in range(11) if x not in a], 2)]
u_i = Fr(count(un, lambda q: all(G(x) for x in q[0] + q[1])), len(un))
u_ii = Fr(count(un, lambda q: all(G(x) for x in q[0]) and not all(G(x) for x in q[1])), len(un))
check("PP8 factor", blk, r"matches exactly \(@\) ordered selections", Fr(len(bat), len(un)))
report(u_i == p_i and u_ii == p_ii, "PP8 unordered model", f"unordered pairs give {u_i}, {u_ii}; ordered give {p_i}, {p_ii}")
has("PP8 question", PPQ.get(8, ""), "A drawer contains 11 different batteries of which 7 are good and 4 are defective.")
report(not any(s in LES + ANS for s in ("Sydney Technical High School, 2021", "James Ruse Agricultural High School, 2023")), "removed items",
       "STHS 2021 Q11(c) and JRAHS 2023 Q10 are not in either file")

print(f"\n{COUNT[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{COUNT[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
