"""Check of Lesson 14B (Counting ordered selections), tied to the printed HTML.

Reads the printed answers from workspace/build/y11ch14/a_14b.html (lesson
examples C1-C4, textbook homework, past-paper worked solutions) and the printed
results in the concept boxes and worked examples of l14b.html. In a template
'@' marks the printed value; each template must match exactly once in its
block, otherwise the item FAILS. Printed LaTeX is converted to an exact value
(fractions.Fraction; \\times, powers, factorials, \\dfrac, and {}^{n}P_{r}) and
compared with a count made independently from the question, almost always by
brute-force enumeration with itertools (permutations / product over the actual
letters, digits or people). Where a full enumeration is too large (10^7 phone
numbers, 6.76 million licence plates, 10! queues) the count is made by
enumerating independent parts and multiplying, or by a dynamic-programming
count over positions; this is said at each place.

For every printed chain such as "5\\times5\\times8\\times3\\times6!=432\\,000" EVERY
'='-separated piece must equal the computed count, so a wrong factor in the
working fails as well as a wrong final answer. Key data in each question as
printed in l14b.html (the numbers of people, the digits, the letters) are
re-read so that the truths below encode the questions actually printed.
Past-paper structure is checked too: marks add to the intro total, time is
1.5 x marks rounded to 5 minutes, numbering, source labels identical in both
files, one hint each, and each MC letter is the option equal to the count.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_14b.py
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


# ---------------------------------------------------------------- blocks
ANS = read("a_14b.html")
LES = read("l14b.html")
HEAD = "{{ahead:Lesson 14B | Counting ordered selections}}"


def ans_blocks(text):
    # labels are kept with their maths by <span style="white-space:nowrap"> wrappers (layout only): strip them
    return {an.strip(): ab.replace('<span style="white-space:nowrap">', "").replace("</span>", "")
            for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S)}


A = ans_blocks(ANS)
sec = ANS.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_14b.html")
report(ANS.count(HEAD) == 2 and ANS.startswith(HEAD) and sec[0].rstrip().endswith(HEAD), "answers headings",
       "the ahead line opens the file and precedes the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}
pps = LES.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l14b.html")
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
    nxt = f"<!-- ============ Concept {k + 1}" if k < 4 else "<!-- ============ Homework"
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


def first_math(label, s, truth):
    try:
        tex = maths(s)[0]
        ok, vals = chain_ok(tex, truth)
        report(ok, label, f"printed {tex} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def count(it, cond=lambda x: True):
    return sum(1 for x in it if cond(x))


def num(t):
    return int("".join(t))


UP = string.ascii_uppercase
VOW = set("AEIOU")
CON = [c for c in UP if c not in VOW]
report(len(UP) == 26 and len(VOW) == 5 and len(CON) == 21, "alphabet", "26 letters, 5 vowels, 21 consonants (y is a consonant)")
DIG = "0123456789"

# ================================================================ lesson concept boxes and worked examples
c1 = concept(1)
check("L outfits 12x6", c1, r"The answer is \(@\). Each", count(product(range(12), range(6))))
check("L outfits sum", c1, "so</p>\n" + r"\[\text{number of outfits}=@.\]", count(product(range(12), range(6))))
check("L outfits four stages", c1, r"choices into account,</p>" + "\n" + r"\[\text{number of outfits}=@.\]", count(product(range(12), range(6), range(8), range(87))))
check("L box diagram outfits", c1, r"\[\text{Number of outfits}=@.\]", count(product(range(12), range(6), range(8), range(87))))
try:
    cells = re.findall(r"<td>(\d+)</td>", c1[c1.index("<table"):c1.index("</table>")])
    report([int(c) for c in cells] == [12, 6, 8, 87], "L box diagram cells", f"{cells}")
except Exception as ex:
    report(False, "L box diagram cells", f"ERROR {ex}")
we3 = les_block("Worked example 3</span>", "<!-- ============ Concept 2")
pat3 = [CON, VOW, CON, VOW, CON]       # positions 1, 3, 5 consonants; 2, 4 vowels
n_we3 = 1
for cls in pat3:                        # independent stages: count the letters allowed in each place
    n_we3 *= sum(1 for ch in UP if ch in cls)
check("L WE3 words", we3, r"\[\text{Number of words}=@.\]", n_we3)
cells = re.findall(r"<td>(\d+)</td>", we3)
report([int(c) for c in cells] == [len(c) for c in pat3], "L WE3 box cells", f"{cells}")
has("L WE3 question", we3, "the second and fourth letters are vowels and the other three letters are consonants")

c2 = concept(2)
we4 = les_block("Worked example 4</span>", "<!-- ============ Concept 3")
odd6 = list(product("13579", repeat=6))
check("L WE4a", we4, r"the number of such numbers is \(@\).</p>", len(odd6))
check("L WE4b no 7", we4, r"so there are \(@\) of them.", count(odd6, lambda t: "7" not in t))
check("L WE4b", we4, r"\text{number of numbers}=@.\]", count(odd6, lambda t: "7" in t))

c3 = concept(3)
abcde = "ABCDE"
check("L 5P3", c3, r"\(\{\text{A},\text{B},\text{C},\text{D},\text{E}\}\) is \(@\).</p>", count(permutations(abcde, 3)))
try:
    der = find(c3, r"\begin{aligned}\text{Hence }{}^{n}\mathrm{P}_{r}&=@\end{aligned}")
    lines = [ln.replace("&", "").strip().lstrip("=").rstrip(".") for ln in der.split("\\\\")]
    # line 1 has '\cdots' and lines 2 '\times\cdots\times': check them as products for many n, r
    def prod_range(n, r):
        out = 1
        for i in range(r):
            out *= n - i
        return out
    ok = lines[0].strip() == "n(n-1)(n-2)(n-3)\\cdots(n-r+1)" and lines[1].strip().startswith("\\dfrac{n(n-1)(n-2)(n-3)\\times\\cdots\\times2\\times1}{(n-r)(n-r-1)\\times\\cdots\\times2\\times1}")
    vals = all(tex_eval(lines[2], n=n, r=r) == prod_range(n, r) == count(permutations(range(n), r)) for n in range(0, 8) for r in range(0, n + 1))
    report(ok and vals, "L nPr derivation", f"lines {[ln.strip()[:40] for ln in lines]}; n!/(n-r)! = n(n-1)...(n-r+1) = enumerated count, 0<=r<=n<=7")
except Exception as ex:
    report(False, "L nPr derivation", f"ERROR {ex}")
try:
    box5 = find(c3, r"distinct letters is" + "\n" + r"\[@\]</li>")
    l_, r_ = box5.rstrip(".").split("=")
    report(all(tex_eval(l_, n=n, r=r) == tex_eval(r_, n=n, r=r) == count(permutations(range(n), r)) for n in range(0, 8) for r in range(0, n + 1)), "L Box 5 formula", box5)
except Exception as ex:
    report(False, "L Box 5 formula", f"ERROR {ex}")
try:
    tex = find(c3, r"the number of permutations is \(@\)</p>")
    report(all(all(v == count(permutations(range(n))) for v in chain_ok(tex, 0, n=n)[1]) for n in range(0, 8)), "L nPn = n!", tex)
    tex = find(c3, r"distinct orderings of the set, is \(@\)</p>")
    report(all(all(v == count(permutations(range(n))) for v in chain_ok(tex, 0, n=n)[1]) for n in range(0, 8)), "L Box 6", tex)
except Exception as ex:
    report(False, "L nPn", f"ERROR {ex}")
we5 = les_block("Worked example 5</span>", "Worked example 6</span>")
n16 = count(permutations(range(16), 4))
check("L WE5 product", we5, r"Hence there are \(@\) possible", n16)
check("L WE5 value", we5, r"(which evaluates to \(@\)).", n16)
report([int(c) for c in re.findall(r"<td>(\d+)</td>", we5)] == [16, 15, 14, 13], "L WE5 box cells", "16 15 14 13")
has("L WE5 question", we5, "a class of 16 select a committee consisting of a president, a vice-president, a treasurer and a secretary")
we6 = les_block("Worked example 6</span>", "Worked example 7</span>")
nz = "123456789"
for k, lab in ((8, "8"), (9, "9")):
    try:
        tex = find(we6, r"\text{Number of " + lab + r"-digit numbers}&=@\end{aligned}")
        tex = tex.replace("\\\\", "").replace("&", "")
        ok, vals = chain_ok(tex, count(permutations(nz, k)))
        report(ok, f"L WE6 {lab}-digit", f"printed {tex} -> {[str(v) for v in vals]}, computed {count(permutations(nz, k))}")
    except Exception as ex:
        report(False, f"L WE6 {lab}-digit", f"ERROR {ex}")


def sig(x, s):
    """x rounded to s significant figures, as (mantissa, exponent)."""
    e = int(log10(x))
    m = round(float(x) / 10 ** e, s - 1)
    if m >= 10:
        m, e = round(m / 10, s - 1), e + 1
    return m, e


def approx(label, block, template, exact, sf):
    try:
        tex = find(block, template)
        m = re.fullmatch(r"([\d.]+)\\times10\^\{(\d+)\}", tex.strip())
        got = (float(m.group(1)), int(m.group(2)))
        exp = sig(exact, sf)
        report(abs(got[0] - exp[0]) < 1e-9 and got[1] == exp[1], label, f"printed {tex}, computed {exp[0]}x10^{exp[1]} ({sf} s.f.)")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


we7 = les_block("Worked example 7</span>", "<!-- ============ Concept 4")
check("L WE7 20!", we7, r"With 20 people, number of ways \(=@\ \ (", factorial(20))
check("L WE7 40!", we7, r"With 40 people, number of ways \(=@\ \ (", factorial(40))
try:
    aps = re.findall(r"\(\\doteq([\d.]+\\times10\^\{\d+\})\)", we7)
    for tex, exact, lab in zip(aps, (factorial(20), factorial(40)), ("20!", "40!")):
        m = re.fullmatch(r"([\d.]+)\\times10\^\{(\d+)\}", tex)
        exp = sig(exact, 2)
        report((float(m.group(1)), int(m.group(2))) == exp, f"L WE7 {lab} approx", f"printed {tex}, computed {exp}")
    report(len(aps) == 2, "L WE7 approx count", f"{len(aps)} approximations")
except Exception as ex:
    report(False, "L WE7 approx", f"ERROR {ex}")
approx("L WE7 ratio", we7, r"in about \(@\) times more", Fr(factorial(40), factorial(20)), 1)
has("L WE7 question", we7, "In how many ways can 20 people form a queue? Will the number of ways double with 40 people?")


def queues(n_people, size, left_only, right_only, same):
    """Two queues: places 0..size-1 left, size..2size-1 right. Enumerate the places of the
    named people only (all of them), then the others fill the remaining places in (rest)! ways,
    checked against a full enumeration when it is small."""
    named = [left_only, right_only] + list(same)
    k = 0
    for places in permutations(range(2 * size), len(named)):
        pos = dict(zip(named, places))
        if pos[left_only] < size and pos[right_only] >= size and (pos[same[0]] < size) == (pos[same[1]] < size):
            k += 1
    return k * factorial(n_people - len(named))


def queues_full(n_people, size, left_only, right_only, same):
    k = 0
    for p in permutations(range(n_people)):          # p[place] = person
        pos = {per: i for i, per in enumerate(p)}
        if pos[left_only] < size and pos[right_only] >= size and (same is None or (pos[same[0]] < size) == (pos[same[1]] < size)):
            k += 1
    return k


we8 = les_block("Worked example 8</span>", "<!-- ============ Homework")
n8 = queues_full(8, 4, 0, 1, (2, 3))
report(n8 == queues(8, 4, 0, 1, (2, 3)), "queue method", f"named-people enumeration agrees with the full 8! enumeration ({n8})")
try:
    tex = find(we8, r"\text{Hence number of ways}&=@\end{aligned}").replace("\\\\", "").replace("&", "").rstrip(".")
    ok, vals = chain_ok(tex.rstrip("."), n8)
    report(ok, "L WE8", f"printed {tex} -> {[str(v) for v in vals]}, computed {n8} (all 8! orders enumerated)")
except Exception as ex:
    report(False, "L WE8", f"ERROR {ex}")
cells = re.findall(r"<td>(.*?)</td>", we8)
try:
    cv = [tex_eval(c.strip("\\()")) for c in cells]
    report(cv == [4, 4, 6, 2, 24], "L WE8 box cells", f"{cells}")
except Exception as ex:
    report(False, "L WE8 box cells", f"ERROR {ex}")
has("L WE8 question", we8, "Eight people form two queues, each with four people.")

# ================================================================ lesson examples C1-C4 (answers)
for c in ("C1", "C2", "C3", "C4"):
    if c not in A or "<b>Your turn.</b>" not in A[c]:
        report(False, c, "answer block missing")
        A[c] = "<b>Your turn.</b>"


def ab(c):
    td, yt = A[c].split("<b>Your turn.</b>")
    return td, yt


# ---- C1
q_td, q_yt = ex_block(c1, "demo"), ex_block(c1, "attempt")
td, yt = ab("C1")
for lab, ph in (("TD a", "shirt from her 10 shirts, a skirt from her 4 skirts, a pair of shoes from her 7 pairs and a hat from her 3 hats"),
                ("TD b", "four-letter words can be formed in which the first and last letters are vowels and the middle two letters are consonants")):
    has(f"C1 {lab} question", q_td, ph)
for lab, ph in (("YT a", "5 entrées, 8 mains and 4 desserts"),
                ("YT b", "three-letter words can be formed in which the first and last letters are consonants and the middle letter is a vowel")):
    has(f"C1 {lab} question", q_yt, ph)
try:
    p = parts(td, "ab")
    first_math("C1 TD a", p["a"], count(product(range(10), range(4), range(7), range(3))))
    first_math("C1 TD b", p["b"], count(product(UP, repeat=4), lambda w: w[0] in VOW and w[3] in VOW and w[1] not in VOW and w[2] not in VOW))
    p = parts(yt, "ab")
    first_math("C1 YT a", p["a"], count(product(range(5), range(8), range(4))))
    first_math("C1 YT b", p["b"], count(product(UP, repeat=3), lambda w: w[0] not in VOW and w[2] not in VOW and w[1] in VOW))
except Exception as ex:
    report(False, "C1", f"ERROR {ex}")

# ---- C2
q_td, q_yt = ex_block(c2, "demo"), ex_block(c2, "attempt")
has("C2 TD question", q_td, "five-digit numbers can be formed entirely from the digits 1, 2, 3 and 4")
has("C2 TD b question", q_td, "contain at least one 4")
has("C2 YT question", q_yt, "four-letter words can be formed from the letters A, B, C, D, E and F")
has("C2 YT b question", q_yt, "contain at least one A")
td, yt = ab("C2")
try:
    w = list(product("1234", repeat=5))
    p = parts(td, "ab")
    first_math("C2 TD a", p["a"], len(w))
    first_math("C2 TD b", p["b"], count(w, lambda t: "4" in t))
    w = list(product("ABCDEF", repeat=4))
    p = parts(yt, "ab")
    first_math("C2 YT a", p["a"], len(w))
    first_math("C2 YT b", p["b"], count(w, lambda t: "A" in t))
except Exception as ex:
    report(False, "C2", f"ERROR {ex}")

# ---- C3
q_td, q_yt = ex_block(c3, "demo"), ex_block(c3, "attempt")
for lab, ph in (("TD a", "a club of 14 members choose a president, a vice-president and a secretary"),
                ("TD b", "six-digit numbers, and how many seven-digit numbers, can be formed from the digits 1, 2, 3, 4, 5, 6 and 7 if no repetition"),
                ("TD c", "In how many ways can 10 people form a queue? Will the number of ways double with 20 people?"),
                ("TD d", "Write \\({}^{6}\\mathrm{P}_{4}\\) as a product")):
    has(f"C3 {lab} question", q_td, ph)
for lab, ph in (("YT a", "a class of 25 choose a captain and a vice-captain"),
                ("YT b", "four-digit numbers, and how many five-digit numbers, can be formed from the digits 1, 2, 3, 4 and 5 if no repetition"),
                ("YT c", "6 different books be arranged in a row"),
                ("YT d", "Write \\({}^{8}\\mathrm{P}_{3}\\) as a product")):
    has(f"C3 {lab} question", q_yt, ph)
td, yt = ab("C3")
try:
    p = parts(td, "abcd")
    first_math("C3 TD a", p["a"], count(permutations(range(14), 3)))
    m = maths(p["b"])
    for tex, k in zip(m, (6, 7)):
        ok, vals = chain_ok(tex, count(permutations("1234567", k)))
        report(ok, f"C3 TD b {k}-digit", f"printed {tex} -> {[str(v) for v in vals]}")
    report(len(m) == 2, "C3 TD b parts", f"{len(m)} values")
    m = maths(p["c"])
    ok, vals = chain_ok(m[0], factorial(10))           # 10! = 3 628 800 queues (10! enumerations avoided: math.factorial)
    report(ok and factorial(10) == count(permutations(range(8))) * 9 * 10, "C3 TD c 10!", f"printed {m[0]}")
    t20 = re.fullmatch(r"20!\\doteq([\d.]+)\\times10\^\{(\d+)\}", m[1])
    report(bool(t20) and (float(t20.group(1)), int(t20.group(2))) == sig(factorial(20), 2), "C3 TD c 20!", f"printed {m[1]}, computed {sig(factorial(20), 2)}")
    t = re.fullmatch(r"([\d.]+)\\times10\^\{(\d+)\}", m[2])
    report(bool(t) and (float(t.group(1)), int(t.group(2))) == sig(Fr(factorial(20), factorial(10)), 2), "C3 TD c ratio", f"printed {m[2]}, computed {sig(Fr(factorial(20), factorial(10)), 2)}")
    first_math("C3 TD d", p["d"], count(permutations(range(6), 4)))
    p = parts(yt, "abcd")
    first_math("C3 YT a", p["a"], count(permutations(range(25), 2)))
    m = maths(p["b"])
    for tex, k in zip(m, (4, 5)):
        ok, vals = chain_ok(tex, count(permutations("12345", k)))
        report(ok, f"C3 YT b {k}-digit", f"printed {tex} -> {[str(v) for v in vals]}")
    report(len(m) == 2, "C3 YT b parts", f"{len(m)} values")
    first_math("C3 YT c", p["c"], count(permutations(range(6))))
    first_math("C3 YT d", p["d"], count(permutations(range(8), 3)))
except Exception as ex:
    report(False, "C3", f"ERROR {ex}")

# ---- C4
c4 = concept(4)
q_td, q_yt = ex_block(c4, "demo"), ex_block(c4, "attempt")
for lab, ph in (("TD a", "Ten people form two queues, each with five people. Alice will only stand in the left-hand queue, Bob will only stand in the right-hand queue, and Carl and Dina insist on standing in the same queue"),
                ("TD b", "odd four-digit numbers can be formed from the digits 1, 2, 3, 4, 5, 6 and 7 if no repetition"),
                ("TD c", "four-digit numbers can be formed from the digits 0, 1, 2, 3, 4 and 5 if no repetition")):
    has(f"C4 {lab} question", q_td, ph)
for lab, ph in (("YT a", "Six people form two queues, each with three people. Ann will only stand in the left-hand queue and Ben will only stand in the right-hand queue"),
                ("YT b", "even three-digit numbers can be formed from the digits 1, 2, 3, 4, 5 and 6 if no repetition"),
                ("YT c", "three-digit numbers can be formed from the digits 0, 1, 2, 3 and 4 if no repetition")):
    has(f"C4 {lab} question", q_yt, ph)
td, yt = ab("C4")
try:
    p = parts(td, "abc")
    first_math("C4 TD a", p["a"], queues(10, 5, 0, 1, (2, 3)))      # named people enumerated, others 6!
    first_math("C4 TD b", p["b"], count(permutations("1234567", 4), lambda t: int(t[-1]) % 2 == 1))
    first_math("C4 TD c", p["c"], count(permutations("012345", 4), lambda t: t[0] != "0"))
    p = parts(yt, "abc")
    first_math("C4 YT a", p["a"], queues_full(6, 3, 0, 1, None))
    first_math("C4 YT b", p["b"], count(permutations("123456", 3), lambda t: int(t[-1]) % 2 == 0))
    first_math("C4 YT c", p["c"], count(permutations("01234", 3), lambda t: t[0] != "0"))
except Exception as ex:
    report(False, "C4", f"ERROR {ex}")


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


# Q1, Q2: printed lists must be exactly the permutations
try:
    got = re.findall(r"[A-Z]{3}", A["1"])
    exp = {"".join(p) for p in permutations("DOG")}
    n1 = int(re.search(r"There are (\d+):", A["1"]).group(1))
    report(set(got) == exp and len(got) == len(exp) == n1, "TB1", f"listed {len(got)} distinct {sorted(got)}, says {n1}, computed {len(exp)}")
    got = re.findall(r"[A-Z]{3}", A["2"])
    exp = {"F" + "".join(p) for p in permutations("EGHI", 2)}
    report(set(got) == exp and len(got) == len(exp), "TB2", f"listed {len(got)}, computed {len(exp)}")
    has("TB1 question", Q[1], "the word DOG")
    has("TB2 question", Q[2], "the letters EFGHI, beginning with F, taken three at a time")
except Exception as ex:
    report(False, "TB1/2", f"ERROR {ex}")

has("TB3 question", Q[3], "the word FRIEND")
tbcheck(3, "ab", [count(permutations("FRIEND", 4)), count(permutations("FRIEND", 6))])
has("TB4 question", Q[4], "the digits 5, 6, 7, 8 and 9")
tbcheck(4, "ab", [count(permutations("56789", 4)), count(product("56789", repeat=4))])
try:
    m = maths(A["5"])
    t3 = list(permutations("23456", 3))
    for tex, t, lab in zip(m, (len(t3), count(t3, lambda x: num(x) > 400)), ("all", "> 400")):
        ok, vals = chain_ok(tex, t)
        report(ok, f"TB5 {lab}", f"printed {tex}, computed {t}")
    report(len(m) == 2, "TB5 parts", f"{len(m)} values")
    has("TB5 question", Q[5], "the digits 2, 3, 4, 5 and 6 if no digit can be repeated? How many of these are greater than 400?")
except Exception as ex:
    report(False, "TB5", f"ERROR {ex}")
single(6, count(permutations(range(7))))
tbcheck(7, "abc", [count(permutations(range(10), 3)), count(permutations("12345", 3)), count(permutations(range(100), 3))])
tbcheck(8, "abc", [count(product(range(1, 10), repeat=3)), count(product(range(100), repeat=3)), count(product("01", repeat=10))])
tbcheck(9, "ab", [count(permutations(range(8))), count(permutations(range(8), 3))])
tbcheck(10, "ab", [count(product("HT", range(1, 7))), count(product("HT", "HT", range(1, 7), range(1, 7), range(1, 7)))])
single(11, count(product(range(4), range(3), range(5), range(2), range(6))))
single(12, count(product(range(6), range(8))))


# Q13: eight-digit phone numbers starting with 9. 10^7 numbers is too many to enumerate quickly,
# so count with a dynamic programme over the 8 positions (state = last digit), which handles
# both per-position conditions and the odd/even alternation of part d.
def phone_n(n, allowed, adjacent=lambda a, b: True):
    ways = {9: 1}                                     # first digit is 9
    for pos in range(1, n):
        new = {}
        for last, w in ways.items():
            for d in range(10):
                if allowed(pos, d) and adjacent(last, d):
                    new[d] = new.get(d, 0) + w
        ways = new
    return sum(ways.values())


def phone(allowed, adjacent=lambda a, b: True):
    return phone_n(8, allowed, adjacent)


# the DP itself checked by brute force on 5-digit strings starting with 9
small = count(product(range(10), repeat=4), lambda t: all(x != 0 for x in t) and all((a % 2) != (b % 2) for a, b in zip((9,) + t, t)))
alt = lambda a, b: (a % 2) != (b % 2)
nozero = lambda pos, d: d != 0
report(phone_n(5, nozero, alt) == small, "TB13 DP self-test", f"DP {phone_n(5, nozero, alt)} = brute force {small} on 5-digit strings")
tbcheck(13, "abcd", [phone(lambda p, d: True), phone(lambda p, d: p < 7 or d % 2 == 1), phone(lambda p, d: d % 2 == 1), phone(nozero, alt)])
has("TB13 question", Q[13], "consist of eight digits. Let us consider those starting with the digit 9")
pins = list(product(DIG, repeat=4))
tbcheck(14, "abcd", [len(pins), count(pins, lambda t: len(set(t)) == 4), count(pins, lambda t: all(int(x) % 2 for x in t)), count(pins, lambda t: t[0] == t[-1])])
f15 = list(permutations(nz, 4))
tbcheck(15, "abcde", [len(f15), count(f15, lambda t: t[-1] == "1"), count(f15, lambda t: int(t[-1]) % 2 == 0), count(f15, lambda t: num(t) % 5 == 0), count(f15, lambda t: num(t) > 7000)])
has("TB15 question", Q[15], "\\(1,\\ 2,\\ \\ldots\\ 8,\\ 9\\)")
f16 = list(product(nz, repeat=4))
tbcheck(16, "abcde", [len(f16), count(f16, lambda t: t[-1] == "1"), count(f16, lambda t: int(t[-1]) % 2 == 0), count(f16, lambda t: num(t) % 5 == 0), count(f16, lambda t: num(t) > 7000)])
# Q17: two letters then four digits; the letters and digits are independent, so enumerate each part and multiply
L2, D4 = list(product(UP, repeat=2)), list(product(DIG, repeat=4))
tbcheck(17, "abcd", [len(L2) * len(D4),
                      count(L2, lambda t: t[0] != t[1]) * count(D4, lambda t: len(set(t)) == 4),
                      count(L2, lambda t: t[1] == "X") * count(D4, lambda t: t[2] == "3"),
                      count(L2, lambda t: sorted(t) == ["D", "Q"]) * count(D4, lambda t: sorted(t) == ["3", "6", "7", "9"])])
nb = list(permutations("NUMBER"))
tbcheck(18, "abcd", [len(nb), count(nb, lambda t: t[0] == "N"), count(nb, lambda t: t[0] == "N" and t[-1] == "U"), count(nb, lambda t: t.index("N") < t.index("U"))])
# Q19: an eight has 4 bow-side and 4 stroke-side seats; women 0,1,2 bow only, 3,4 stroke only
single(19, count(permutations(range(8)), lambda p: all(p.index(w) < 4 for w in (0, 1, 2)) and all(p.index(w) >= 4 for w in (3, 4))))
single(20, count(permutations(range(5), 3), lambda t: t[0] in (0, 1)))
f21 = list(permutations("23456"))
tbcheck(21, "abc", [len(f21), count(f21, lambda t: num(t) > 56432), count(f21, lambda t: num(t) < 56432)])
try:
    f22 = [t for r in range(1, 5) for t in permutations("2345", r)]
    blk = A["22"]
    for lab, tpl, t in (("i", r"<b>a</b> i&nbsp;\(@\)", len(f22)), ("ii", r"ii&nbsp;\(@\)", count(f22, lambda x: int(x[-1]) % 2 == 0))):
        check(f"TB22a {lab}", blk, tpl, t)
    report("<b>b</b>" not in blk and "Repeat the two parts" not in Q[22], "TB22b omitted", "doubtful part b (repetition allowed gives infinitely many integers) left out of question and answers")
except Exception as ex:
    report(False, "TB22", f"ERROR {ex}")
f23 = [t for t in permutations("01234") if t[0] != "0"]
tbcheck(23, "abc", [len(f23), count(f23, lambda t: int(t[-1]) % 2 == 1), count(f23, lambda t: num(t) % 5 == 0)])
try:
    pa = tb(24, "ab")
    rs = [r for r in range(0, 9) if perm(8, r) == 336]
    ns = [n for n in range(1, 40) if 7 * perm(2 * n, n) == 4 * perm(2 * n + 1, n)]
    for L, sols, var in (("a", rs, "r"), ("b", ns, "n")):
        tex = maths(pa[L])[0]
        m = re.fullmatch(var + r"=(\d+)", tex)
        report(bool(m) and len(sols) == 1 and int(m.group(1)) == sols[0], f"TB24{L}", f"printed {tex}, solutions found {sols}")
    qa = find(Q[24], r"If \(@\), find the value of \(r\)")
    l_, r_ = qa.split("=")
    report(all(tex_eval(l_, r=r) == perm(8, r) for r in range(9)) and tex_eval(r_) == 336, "TB24a question", qa)
    qb = find(Q[24], r"b</span>If \(@\), find \(n\)")
    l_, r_ = qb.split("=")
    report(all(tex_eval(l_, n=n) == 7 * perm(2 * n, n) and tex_eval(r_, n=n) == 4 * perm(2 * n + 1, n) for n in range(1, 9)), "TB24b question", qb)
    # part c: the printed identities must be true (catches a transcription slip)
    for lab, tpl, lo in (("i", r"<span>i&nbsp; \(@\)</span>", 1), ("ii", r"<span>ii&nbsp; \(@\)</span>", 2)):
        tex = find(Q[24], tpl)
        l_, r_ = tex.split("=")
        pairs = [(n, r) for n in range(lo + 2, 12) for r in range(lo, n - 1)]
        bad = [(n, r) for n, r in pairs if tex_eval(l_, n=n, r=r) != tex_eval(r_, n=n, r=r)]
        report(not bad, f"TB24c {lab} identity", f"{tex} holds for {len(pairs)} (n, r)" + (f" FAILS at {bad[:3]}" if bad else ""))
except Exception as ex:
    report(False, "TB24", f"ERROR {ex}")
five = range(10000, 100000)
nz5 = [num(t) for t in product(nz, repeat=5)]
try:
    pa = tb(25, "abcd")
    first_math("TB25a", pa["a"], count(five, lambda x: x % 3 == 0))
    first_math("TB25b", pa["b"], count(nz5, lambda x: x % 3 == 0))
    first_math("TB25c", pa["c"], count(nz5, lambda x: x % 2 == 0))
    first_math("TB25d", pa["d"], count(nz5, lambda x: x % 6 == 0))
except Exception as ex:
    report(False, "TB25", f"ERROR {ex}")
qs = sorted(Q)
report(qs == list(range(1, 26)), "TB question numbers", f"{qs}")
ans_q = sorted(int(k) for k in A if k.isdigit())
report(ans_q == list(range(1, 26)), "TB answer numbers", f"{ans_q} (24c is a proof; every question has a printed answer)")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 1 <= M <= 22, "lesson marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    if M < 15:
        print(f"NOTE     {M} marks is below 15: house rule 8 (too few clean 14B school questions), see the task report")
    report(T == 5 * round(1.5 * M / 5), "lesson time", f"{T} min for {M} marks")
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


def mc(pp, value, pattern):
    try:
        opts = {k: int(v) for k, v in re.findall(pattern, PPQ[pp])}
        letter = re.search(r"<b>Answer \(?([A-D])\)?\.</b>", PPA[pp]).group(1)
        best = [k for k, v in opts.items() if v == value]
        report(len(opts) == 4 and best == [letter], f"PP{pp} MC letter", f"options {opts}; printed {letter}; option equal to {value} is {best}")
    except Exception as ex:
        report(False, f"PP{pp} MC letter", f"ERROR {ex}")


# ---------------------------------------------------------------- PP 1  numbers > 2100 from 1, 2, 3, 4
all1 = [num(t) for r in range(1, 5) for t in permutations("1234", r)]
n1 = count(all1, lambda x: x > 2100)
has("PP1 question", PPQ.get(1, ""), "greater than 2100 can be formed with the digits 1, 2, 3, 4 if no digit is to be used more than once")
check("PP1 total", PPA.get(1, ""), r"\[\text{number of numbers}=@.\]", n1)
check("PP1 first digit 3 or 4", PPA.get(1, ""), r"There are \(@\) of them.", count(all1, lambda x: x >= 3000))
check("PP1 first digit 2", PPA.get(1, ""), r"So all \(@\) of them", count(all1, lambda x: 2000 <= x < 3000 and x > 2100))
report(count(all1, lambda x: 2000 <= x < 3000) == count(all1, lambda x: 2000 <= x < 3000 and x > 2100) and min(x for x in all1 if 2000 <= x < 3000) == 2134,
       "PP1 smallest with 2", "every four-digit number beginning with 2 is at least 2134")
report(max(x for x in all1 if x < 1000) == 432, "PP1 three digits", "largest number with three digits or fewer is 432")
check("PP1 option C", PPA.get(1, ""), r"Option (C), \(@\), counts", count(permutations("1234")))
mc(1, n1, r"<span>\(([A-D])\) (\d+)</span>")

# ---------------------------------------------------------------- PP 2  8 people, Lily left of Ben
n2 = count(permutations(range(8)), lambda p: p.index(0) < p.index(1))
check("PP2", PPA.get(2, ""), r"\[\text{number of ways}=@.\]", n2)
check("PP2 total", PPA.get(2, ""), r"line in \(@\) ways.", count(permutations(range(8))))

# ---------------------------------------------------------------- PP 3  5 of 6 in a line, two oldest of those at the ends
n3 = 0
for S in combinations(range(6), 5):                    # ages 0..5, larger is older
    old = set(sorted(S)[-2:])
    n3 += count(permutations(S), lambda p: {p[0], p[-1]} == old)
check("PP3", PPA.get(3, ""), r"\[\text{number of ways}=@.\]", n3)
report(count(combinations(range(6), 5)) == 6, "PP3 selections", "6 ways to select 5 of 6 (one left out)")
check("PP3 option A", PPA.get(3, ""), r"Option A, \(@\), ignores", count(permutations(range(6), 5)))
mc(3, n3, r"<span>([A-D])\. (\d+)</span>")

# ---------------------------------------------------------------- PP 4  CONSIDER begins with SI
w = "CONSIDER"
report(len(set(w)) == len(w), "PP4 distinct letters", w)
arr = list(permutations(w))
p4 = Fr(count(arr, lambda t: t[0] == "S" and t[1] == "I"), len(arr))
check("PP4", PPA.get(4, ""), r"P(\text{begins with SI})=@.\]", p4)
check("PP4 |S|", PPA.get(4, ""), r"there are \(|S|=@\) equally", len(arr))
check("PP4 |E|", PPA.get(4, ""), r"so \(|E|=@\). Hence", count(arr, lambda t: t[:2] == ("S", "I")))

# ---------------------------------------------------------------- PP 5  numbers > 6000 from 1, 4, 5, 7, 8
all5 = [num(t) for r in range(1, 6) for t in permutations("14578", r)]
has("PP5 question", PPQ.get(5, ""), "greater than 6000 can be formed with the digits 1, 4, 5, 7, 8 if no digit is repeated")
check("PP5 four-digit", PPA.get(5, ""), r"\[\text{four-digit numbers}=@.\]", count(all5, lambda x: 6000 < x < 10000))
check("PP5 five-digit", PPA.get(5, ""), r"\[\text{five-digit numbers}=@.\]", count(all5, lambda x: x > 6000 and x >= 10000))
check("PP5 total", PPA.get(5, ""), r"greater than 6000 is \(@\).</p>", count(all5, lambda x: x > 6000))

# ---------------------------------------------------------------- PP 6  EPSILON, N left of L
check("PP6", PPA.get(6, ""), r"\[\text{number of arrangements}=@.\]", count(permutations("EPSILON"), lambda t: t.index("N") < t.index("L")))
check("PP6 total", PPA.get(6, ""), r"so there are \(@\) arrangements", count(permutations("EPSILON")))

# ---------------------------------------------------------------- PP 7  nP(r-1)/a = nPr/b = nP(r+1)/c  =>  b^2 = a(b+c)
try:
    qtex = find(PPQ[7], r"\[@\]")
    l1, l2, l3 = qtex.split("=")
    NR = [(n, r) for n in range(2, 12) for r in range(1, n)]
    blk = PPA[7]
    al = re.findall(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", blk, re.S)
    rows = [ln.replace("&", "").strip().rstrip(",").rstrip(".") for ln in al[0].split("\\\\")]
    bad = []
    for k_ in (1, Fr(1, 3), 7):
        for n, r in NR:
            a, b, c = Fr(perm(n, r - 1)) / k_, Fr(perm(n, r)) / k_, Fr(perm(n, r + 1)) / k_
            env = dict(n=n, r=r, a=a, b=b, c=c, k=k_)
            if not (tex_eval(l1, **env) == tex_eval(l2, **env) == tex_eval(l3, **env) == k_):
                bad.append(("stem", n, r))
            for i, (row, truth) in enumerate(zip(rows, (b / a, c / b))):
                if any(tex_eval(pc, **env) != truth for pc in row.split("=")):
                    bad.append((f"row {i + 1}", n, r))
            if b * b != a * (b + c):
                bad.append(("result", n, r))
    report(not bad and len(rows) == 2, "PP7 working", f"{len(rows)} rows, every '=' piece checked at {3 * len(NR)} (n, r, k)" + (f" FAILS {bad[:3]}" if bad else ""))
    ta, tb_, tc = find(blk, r"Then \(a=@\), \(b"), find(blk, r"\(b=@\) and \(c"), find(blk, r"and \(c=@\). Using")
    okd = all(tex_eval(ta, n=n, r=r, k=3) == Fr(perm(n, r - 1), 3) and tex_eval(tb_, n=n, r=r, k=3) == Fr(perm(n, r), 3) and tex_eval(tc, n=n, r=r, k=3) == Fr(perm(n, r + 1), 3) for n, r in NR)
    report(okd, "PP7 a, b, c", f"a = {ta}, b = {tb_}, c = {tc}")
    fin = [ln.replace("&", "").strip().rstrip(".") for ln in al[1].split("\\\\")]
    okf = True
    for n, r in NR:
        a, b, c = Fr(perm(n, r - 1)), Fr(perm(n, r)), Fr(perm(n, r + 1))
        for ln in fin:
            l_, r_ = ln.split("=")
            okf &= tex_eval(l_, a=a, b=b, c=c) == tex_eval(r_, a=a, b=b, c=c)
    report(okf and fin[-1] == "b^2=a(b+c)", "PP7 conclusion", f"{fin}")
    h = find(blk, r"Hence \(@\), that is")
    l_, r_ = h.split("=")
    report(all(tex_eval(l_, a=perm(n, r - 1), b=perm(n, r), c=perm(n, r + 1)) == tex_eval(r_, a=perm(n, r - 1), b=perm(n, r), c=perm(n, r + 1)) for n, r in NR), "PP7 b/a = c/b + 1", h)
except Exception as ex:
    report(False, "PP7", f"ERROR {ex}")

# ---------------------------------------------------------------- PP 8  4-digit numbers 1xxx with exactly one pair
def one_pair(s):
    cnt = sorted(s.count(d) for d in set(s))
    return s[0] == "1" and cnt == [1, 1, 2]


nums8 = [str(x) for x in range(1000, 10000)]
n8i = count(nums8, lambda s: one_pair(s) and s.count("1") == 2)
n8ii = count(nums8, one_pair)
check("PP8 (i)", PPA.get(8, ""), r"\[\text{number of numbers}=@.\]", n8i)
check("PP8 (ii) case 2", PPA.get(8, ""), r"So there are \(@\) numbers in this case.", n8ii - n8i)
check("PP8 (ii) total", PPA.get(8, ""), r"\[\text{total}=@.\]", n8ii)
has("PP8 question", PPQ.get(8, ""), "A 4-digit number begins with 1 and has exactly one pair of identical digits (not necessarily adjacent).")

print(f"\n{COUNT[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{COUNT[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
