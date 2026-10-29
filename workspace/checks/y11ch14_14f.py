"""Check of Lesson 14F (Using counting in probability) and the Chapter 14 review, tied to the printed HTML.

Reads the printed answers from workspace/build/y11ch14/a_14f.html (lesson
examples C1-C3, Exercise 14F answers, Chapter 14 review answers, past-paper
worked solutions) and the printed results in the worked examples of
l14f.html. In a template '@' marks the printed value; each template must
match exactly once in its block, otherwise the item FAILS. Printed LaTeX is
converted to an exact value (fractions.Fraction; \\times, \\div, +, -,
powers, factorials, \\dfrac, {}^{n}\\mathrm{P}_{r}, {}^{n}\\mathrm{C}_{r}
and \\binom) and compared with a probability found independently from the
question, by brute-force enumeration: cards are dealt from a labelled
52-card deck (every hand, or every ordered deal), numbers are listed and
tested digit by digit, people, letters and balls are labelled and arranged
or chosen with itertools, all 2 598 960 poker hands are classified, exits
and menus are assigned with itertools.product, and the knockout tournament
is played out over every draw position and every match result. Where a full
enumeration is too large (the 40 students of a past paper, the birthday
problem, ENTERTAINMENT, the 16- and 2^n-player tournaments) the probability
is found by a sequential or reduced method that is first checked against a
full enumeration on smaller cases.

For every printed chain such as "13\\times78\\times\\dfrac{3\\times2\\times1}{52\\times51\\times50}=\\dfrac{39}{850}"
EVERY '='-separated piece must equal the computed value, so a wrong factor
in the working fails as well as a wrong final answer. Decimal answers are
compared with the exact value rounded as the question asks. Algebraic
answers (in n or k) are evaluated at several values and compared with
enumeration. Past-paper structure is checked too: marks add to the intro
total, time is 1.5 x marks rounded to the nearest 5 minutes (halves up),
numbering, source labels identical in both files, one hint each, part marks,
and each MC letter is the only option equal to the answer.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_14f.py
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



# ---------------------------------------------------------------- blocks
from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec = 60

ANS = read("a_14f.html")
LES = read("l14f.html")
HEAD = "{{ahead:Lesson 14F | Using counting in probability}}"
RHEAD = "{{ahead:Chapter 14 Review | Chapter review exercise}}"


def ans_blocks(text):
    return {an.strip(): ab.replace('<span style="white-space:nowrap">', "").replace("</span>", "")
            for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab"[^>]*>(.*?)</div></div>', text, re.S)}


TBSEC = '<div class="ans-sec">Textbook Homework</div>'
PPSEC = '<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>'
RVSEC = '<div class="ans-sec">' + RHEAD + '</div>'
for mark in (TBSEC, PPSEC, RVSEC):
    if ANS.count(mark) != 1:
        sys.exit(f"FAIL: {mark!r} not found exactly once in a_14f.html")
LEXA = ans_blocks(ANS.split(TBSEC)[0])
A = ans_blocks(ANS.split(TBSEC)[1].split(RVSEC)[0])
RA = ans_blocks(ANS.split(RVSEC)[1].split(PPSEC)[0])
ppsec = ANS.split(PPSEC)[1]
report(ANS.count(HEAD) == 2 and ANS.startswith(HEAD) and ANS.split(PPSEC)[0].rstrip().endswith(HEAD)
       and ANS.index(TBSEC) < ANS.index(RVSEC) < ANS.index(PPSEC), "answers headings",
       "ahead line opens the file; Lesson Examples, Textbook Homework, Chapter 14 Review, then the ahead line and the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', ppsec, re.S)}
for mark in ("<!-- ============ Homework ============ -->", "<!-- ============ Past papers ============ -->", "<!-- ============ Chapter review ============ -->"):
    if LES.count(mark) != 1:
        sys.exit(f"FAIL: {mark!r} not found exactly once in l14f.html")
HW = LES.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
PPL = LES.split("<!-- ============ Past papers ============ -->")[1].split("<!-- ============ Chapter review")[0]
RVL = LES.split("<!-- ============ Chapter review ============ -->")[1]
QRE = r'<div class="q"><span class="q-num">(\d+)</span><div class="q-body">(.*?)(?=<div class="q"><span class="q-num">|$)'
Q = {int(n): b for n, b in re.findall(QRE, HW, re.S)}
RQ = {int(n): b for n, b in re.findall(QRE, RVL, re.S)}
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', PPL, re.S)}


def les_block(start, end):
    i = LES.find(start)
    j = LES.find(end, i + 1)
    if i < 0 or j < 0:
        raise LookupError(f"lesson block {start!r} not found")
    return LES[i:j]


def concept(k):
    nxt = f"<!-- ============ Concept {k + 1}" if k < 3 else "<!-- ============ Homework"
    return les_block(f"<!-- ============ Concept {k} ", nxt)


def worked(cblock):
    m = re.findall(r'<div class="ex worked">(.*?)(?=<div class="ex |$)', cblock, re.S)
    if len(m) != 1:
        raise LookupError(f"{len(m)} worked blocks")
    return m[0]


def exq(cblock, kind):
    m = re.findall(r'<div class="ex ' + kind + r'">(.*?)\{\{work:\d+\}\}', cblock, re.S)
    if len(m) != 1:
        raise LookupError(f"{len(m)} '{kind}' blocks")
    return m[0]


def rhs(tex):
    """Drop a leading 'P(...)=' or 'P=' (event names are words, not numbers)."""
    t = tex.strip()
    if t.startswith("P"):
        t = t.split("=", 1)[1]
    return t


def chain(label, tex, truth):
    try:
        t = rhs(tex).strip().rstrip(".,")
        ok, vals = chain_ok(t, truth)
        report(ok, label, f"printed {tex.strip()} -> {[str(v) for v in vals]}, computed {truth}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def tpl(label, block, template, truth):
    try:
        chain(label, find(block, template), truth)
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def sig(x, n):
    """Exact fraction x rounded half-up to n significant figures, as a Fraction."""
    d = Decimal(x.numerator) / Decimal(x.denominator)
    if d == 0:
        return Fr(0)
    e = d.adjusted()
    q = Decimal(1).scaleb(e - n + 1)
    return Fr(d.quantize(q, rounding=ROUND_HALF_UP))


def dp(x, n):
    d = Decimal(x.numerator) / Decimal(x.denominator)
    return Fr(d.quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))


def approx(label, tex, truth, places=None, figs=None):
    """'exact chain \\approx decimal': the exact chain equals truth, the decimal is truth rounded."""
    try:
        exact, dec = tex.split("\\approx")
        chain(label + " exact", exact, truth)
        dec = Fr(dec.strip().rstrip(".,"))
        want = dp(truth, places) if places is not None else sig(truth, figs)
        report(dec == want, label + " decimal", f"printed {dec} ({float(dec)}), computed {float(truth)} rounded = {float(want)}")
    except Exception as ex:
        report(False, label, f"ERROR {ex}")


def P_(count, total):
    return Fr(count, total)


# ---------------------------------------------------------------- the deck, numbers and strings
SUITS = "SHDC"                       # spades, hearts, diamonds, clubs
DECK = [(r, s) for s in SUITS for r in range(1, 14)]   # rank 1 = ace, 11 = jack, 12 = queen, 13 = king
RED = set("HD")
HANDS3 = list(combinations(range(52), 3))
N_H3 = len(HANDS3)


def h3(cond):
    return Fr(ncount(HANDS3, lambda h: cond([DECK[i] for i in h])), N_H3)


def suits(cards):
    return Counter(c[1] for c in cards)


def ranks(cards):
    return Counter(c[0] for c in cards)


def numbers(d):
    return [str(x) for x in range(10 ** (d - 1), 10 ** d)]


def strings(d):
    return ["".join(t) for t in product("0123456789", repeat=d)]


NUM3, NUM4, NUM5 = numbers(3), numbers(4), numbers(5)


def frac_of(nums, cond):
    return Fr(ncount(nums, cond), len(nums))


def increasing(s):
    return all(a < b for a, b in zip(s, s[1:]))


# ================================================================ Concept 1, Worked example 21
try:
    c1 = concept(1)
    w21 = worked(c1)
    deal3 = list(permutations(range(52), 3))
    fav_a = ncount(HANDS3, lambda h: sorted(DECK[i][1] for i in h) == ["C", "H", "H"])
    fav_b = ncount(deal3, lambda d: [DECK[i][1] for i in d] == ["C", "H", "H"])
    tpl("WE21a hands", w21, r"\text{number of unordered hands}=@.\]", N_H3)
    tpl("WE21a club", w21, r"choosing 1 club from 13 in \(@\) ways", ncount(combinations(range(13), 1)))
    tpl("WE21a hearts", w21, r"choosing the 2 hearts from 13 in \(@\) ways", ncount(combinations(range(13), 2)))
    tpl("WE21a hand", w21, r"so the hand can be chosen in \(@\) ways.", fav_a)
    tpl("WE21a P", w21, r"P(\text{1 club and 2 hearts})=@.\]", Fr(fav_a, N_H3))
    tpl("WE21b ordered", w21, r"\text{number of ordered hands}&=@,\\", len(deal3))
    tpl("WE21b such", w21, r"\text{number of such hands in the order }\clubsuit\heartsuit\heartsuit&=@.\end{aligned}", fav_b)
    tpl("WE21b P", w21, r"P(\clubsuit\heartsuit\heartsuit)=@.\]", Fr(fav_b, len(deal3)))
    tpl("WE21 note", w21, r"must be \(@\) of the answer", Fr(fav_b, len(deal3)) / Fr(fav_a, N_H3))
    has("WE21 question", w21, "Three cards are dealt from a pack of 52.")

    # C1 tutor demo (four cards) and your turn (two cards)
    C1 = LEXA["C1"]
    td, yt = C1.split("<b>Your turn.</b>")
    hands4 = list(combinations(range(52), 4))
    fav4 = ncount(hands4, lambda h: sorted(DECK[i][1] for i in h) == ["H", "S", "S", "S"])
    n_deal4, fav4o = 0, 0
    for d in permutations(range(52), 4):
        n_deal4 += 1
        if DECK[d[0]][1] == "H" and DECK[d[1]][1] == "S" and DECK[d[2]][1] == "S" and DECK[d[3]][1] == "S":
            fav4o += 1
    pa = parts(td, "ab")
    m = maths(pa["a"])
    for lab, t, v in zip(("hands", "favourable", "P"), m, (len(hands4), fav4, Fr(fav4, len(hands4)))):
        chain(f"C1 TD a {lab}", t, v)
    m = maths(pa["b"])
    for lab, t, v in zip(("deals", "favourable", "P", "ratio"), m, (n_deal4, fav4o, Fr(fav4o, n_deal4), Fr(fav4o, n_deal4) / Fr(fav4, len(hands4)))):
        chain(f"C1 TD b {lab}", t, v)
    report(len(maths(pa["a"])) == 3 and len(maths(pa["b"])) == 4, "C1 TD pieces", "every printed value read")
    hands2 = list(combinations(range(52), 2))
    deal2 = list(permutations(range(52), 2))
    ya = Fr(ncount(hands2, lambda h: len({DECK[i][1] in RED for i in h}) == 2), len(hands2))
    yb = Fr(ncount(deal2, lambda d: DECK[d[0]][1] in RED and DECK[d[1]][1] not in RED), len(deal2))
    pb = parts(yt, "ab")
    chain("C1 YT a", maths(pb["a"])[0], ya)
    chain("C1 YT b", maths(pb["b"])[0], yb)
    chain("C1 YT b ratio", maths(pb["b"])[1], yb / ya)
    has("C1 TD question", exq(c1, "demo"), r"one heart and three spades are dealt in the order \(\heartsuit\spadesuit\spadesuit\spadesuit\)")
    has("C1 YT question", exq(c1, "attempt"), "Two cards are dealt from a pack of 52.")
except Exception as ex:
    report(False, "Concept 1", f"ERROR {ex}")

# ================================================================ Concept 2, Worked example 22
try:
    c2 = concept(2)
    w22 = worked(c2)
    n5 = len(NUM5)
    tpl("WE22 total", w22, r"Hence the number of five-digit numbers \(=@\).", n5)
    tpl("WE22a fav", w22, r"so the number of favourable numbers is \(@\).", ncount(NUM5, lambda s: s >= "60000"))
    tpl("WE22a P", w22, r"Hence \(P(\text{at least }60\,000)=@\).", frac_of(NUM5, lambda s: s >= "60000"))
    ev = lambda s: set(s) <= set("02468")
    tpl("WE22b count chain", w22, r"Hence number of such numbers \(=@\),</span><br>" + "\n" + r'<span style="margin-left:5mm">and \(P(\text{all digits', ncount(NUM5, ev))
    tpl("WE22b P", w22, r"and \(P(\text{all digits are even})=@\).", frac_of(NUM5, ev))
    dist = lambda s: len(set(s)) == len(s)
    cells = [int(x) for x in re.findall(r"<td>(\d+)</td>", find(w22, r"<th>5th digit</th></tr><tr>@</tr></table>"))]
    pos_choices = [9] + [10 - i for i in range(1, 5)]            # first digit not 0, then without replacement
    report(cells == pos_choices and eval("*".join(map(str, cells))) == ncount(NUM5, dist), "WE22c table", f"printed {cells}, product {eval('*'.join(map(str, cells)))}, enumerated {ncount(NUM5, dist)}")
    tpl("WE22c count", w22, r"so number of such numbers \(=@\)<br>", ncount(NUM5, dist))
    tpl("WE22c P", w22, r"and \(P(\text{digits are distinct})=@\).", frac_of(NUM5, dist))
    inc = lambda s: increasing(s)
    tpl("WE22d count", w22, r'<span style="margin-left:5mm">\(=@\),</span>', ncount(NUM5, inc))
    report(ncount(NUM5, inc) == ncount(combinations("123456789", 5)), "WE22d subsets", "increasing five-digit numbers = 5-subsets of the non-zero digits")
    tpl("WE22d P", w22, r"so \(P(\text{digits are distinct and in increasing order})=@\).", frac_of(NUM5, inc))

    C2 = LEXA["C2"]
    td, yt = C2.split("<b>Your turn.</b>")
    chain("C2 TD total", maths(td)[0], len(NUM4))
    chain("C2 YT total", maths(yt)[0], len(NUM3))
    for tag, blk, nums, lo, digs in (("C2 TD", td, NUM4, "7000", "13579"), ("C2 YT", yt, NUM3, "400", "02468")):
        p_ = parts(blk, "abcd")
        truths = [frac_of(nums, lambda s: s >= lo), frac_of(nums, lambda s: set(s) <= set(digs)), frac_of(nums, dist), frac_of(nums, inc)]
        for L, t in zip("abcd", truths):
            chain(f"{tag} {L}", maths(p_[L])[0], t)
    has("C2 TD question", exq(c2, "demo"), "A four-digit number is chosen at random.")
    has("C2 TD question a", exq(c2, "demo"), "that it is at least 7000,")
    has("C2 TD question b", exq(c2, "demo"), "that it consists only of odd digits,")
    has("C2 YT question", exq(c2, "attempt"), "A three-digit number is chosen at random.")
    has("C2 YT question a", exq(c2, "attempt"), "that it is at least 400,")
    has("C2 YT question b", exq(c2, "attempt"), "that it consists only of even digits,")
except Exception as ex:
    report(False, "Concept 2", f"ERROR {ex}")

# ================================================================ Concept 3, Worked example 23
try:
    c3 = concept(3)
    w23 = worked(c3)
    n5 = len(NUM5)
    no4 = ncount(NUM5, lambda s: "4" not in s)
    no5 = ncount(NUM5, lambda s: "5" not in s)
    no45 = ncount(NUM5, lambda s: "4" not in s and "5" not in s)
    either = ncount(NUM5, lambda s: "4" not in s or "5" not in s)
    both = ncount(NUM5, lambda s: "4" in s and "5" in s)
    tpl("WE23a no 4", w23, r"number of five-digit numbers without a 4 \(=@\),", no4)
    tpl("WE23a with 4", w23, r"so number of five-digit numbers with a 4 \(=@\).", n5 - no4)
    tpl("WE23a P", w23, r"Hence \(P(\text{at least one 4})=@\).", frac_of(NUM5, lambda s: "4" in s))
    tpl("WE23b no 4", w23, r"number without a 4 \(=@\),", no4)
    tpl("WE23b no 5", w23, r"similarly number without a 5 \(=@\),", no5)
    tpl("WE23b neither", w23, r"and number with no 5 and no 4 \(=@\).", no45)
    tpl("WE23b union", w23, r"Hence number with no 5 or no 4 \(=@\),", either)
    tpl("WE23b both", w23, r"and number with at least one 5 and at least one 4 \(=@\).", both)
    tpl("WE23b P", w23, r"Hence \(P(\text{at least one 4 and at least one 5})=@\).", Fr(both, n5))
    S5 = strings(5)
    s3 = ncount(S5, lambda s: s.count("7") == 3)
    s3z = ncount(S5, lambda s: s.count("7") == 3 and s[0] == "0")
    e3 = ncount(NUM5, lambda s: s.count("7") == 3)
    cells = re.findall(r"<td>(.*?)</td>", find(w23, r"<th>choose second non-7</th></tr><tr>@</tr></table>"))
    report(tex_eval(rhs(maths(cells[0])[0]).split("=")[-1]) == ncount(combinations(range(5), 3)) and chain_ok(maths(cells[0])[0], ncount(combinations(range(5), 3)))[0]
           and cells[1:] == ["9", "9"] and 10 * 9 * 9 == s3, "WE23c table 1", f"printed {cells}; strings with exactly three 7s {s3}")
    cells = re.findall(r"<td>(.*?)</td>", find(w23, r"<th>choose the other non-7</th></tr><tr>@</tr></table>"))
    report(chain_ok(maths(cells[0])[0], ncount(combinations(range(4), 3)))[0] and cells[1:] == ["9"] and 4 * 9 == s3z, "WE23c table 2", f"printed {cells}; such strings beginning with 0: {s3z}")
    report(f"giving {s3} such strings." in w23 and f"giving {s3z} such strings." in w23, "WE23c strings", f"{s3} and {s3z}")
    tpl("WE23c numbers", w23, r"Hence there are \(@\) such numbers", e3)
    tpl("WE23c P", w23, r"\(P(\text{number has exactly three 7s})=@\).", Fr(e3, n5))
    forms = [ncount(NUM5, lambda s, k=k: s.count("7") == 4 and s[k] != "7") for k in range(5)]
    e4, e5 = ncount(NUM5, lambda s: s.count("7") == 4), ncount(NUM5, lambda s: s == "77777")
    report(forms == [8, 9, 9, 9, 9] and "There are eight numbers of the first form, and nine of the other four forms, giving 44 numbers altogether." in w23 and e4 == 44 and e5 == 1,
           "WE23d forms", f"numbers with four 7s by the position of the non-7: {forms}, total {e4}; five 7s: {e5}")
    tpl("WE23d count", w23, r"Hence the number with at least three 7s \(=@\),", e3 + e4 + e5)
    tpl("WE23d P", w23, r"and \(P(\text{at least three 7s})=@\).", frac_of(NUM5, lambda s: s.count("7") >= 3))

    C3 = LEXA["C3"]
    td, yt = C3.split("<b>Your turn.</b>")
    for tag, blk, d, x, y, z in (("C3 TD", td, 4, "3", "6", "7"), ("C3 YT", yt, 3, "5", "6", "2")):
        nums, strs = numbers(d), strings(d)
        nx = ncount(nums, lambda s: x not in s)
        nxy = ncount(nums, lambda s: x not in s and y not in s)
        uni = ncount(nums, lambda s: x not in s or y not in s)
        bth = ncount(nums, lambda s: x in s and y in s)
        sz = ncount(strs, lambda s: s.count(z) == 2)
        szz = ncount(strs, lambda s: s.count(z) == 2 and s[0] == "0")
        ez = ncount(nums, lambda s: s.count(z) == 2)
        al = ncount(nums, lambda s: s.count(z) >= 2)
        p_ = parts(blk, "abcd")
        ma = maths(p_["a"])
        truths_a = [nx, len(nums) - nx, Fr(len(nums) - nx, len(nums))]
        mb = maths(p_["b"])
        truths_b = [nxy, uni, bth, Fr(bth, len(nums))]
        mc_ = maths(p_["c"])
        truths_c = [sz, szz, ez, Fr(ez, len(nums))] if d == 4 else [sz, ez, Fr(ez, len(nums))]
        md = [t for t in maths(p_["d"]) if "*" not in t]
        e3_ = ncount(nums, lambda s: s.count(z) == 3)
        truths_d = [e3_, al, Fr(al, len(nums))] if d == 4 else [al, Fr(al, len(nums))]
        for L, ms, ts in (("a", ma, truths_a), ("b", mb, truths_b), ("c", mc_, truths_c), ("d", md, truths_d)):
            report(len(ms) == len(ts), f"{tag} {L} pieces", f"{len(ms)} printed values, {len(ts)} truths")
            for i, (t, v) in enumerate(zip(ms, ts)):
                chain(f"{tag} {L}{i + 1}", t, v)
        if d == 4:
            forms = [ncount(nums, lambda s, k=k: s.count(z) == 3 and s[k] != z) for k in range(4)]
            report(forms == [8, 9, 9, 9] and "\\({*}777\\) gives 8, and \\(7{*}77\\), \\(77{*}7\\), \\(777{*}\\) give 9 each" in p_["d"] and ncount(nums, lambda s: s == z * 4) == 1,
                   f"{tag} d forms", f"three 7s by the position of the non-7: {forms}")
        else:
            report(szz == 1 and "only 022, so 1" in p_["c"] and ncount(nums, lambda s: s == z * 3) == 1 and "222 with three 2s" in p_["d"], f"{tag} c,d words", f"strings 0zz: {szz}")
    has("C3 TD question", exq(c3, "demo"), "A four-digit number is chosen at random.")
    has("C3 TD question b", exq(c3, "demo"), "the number contains at least one three and at least one six,")
    has("C3 TD question c", exq(c3, "demo"), "the number contains exactly two sevens,")
    has("C3 YT question", exq(c3, "attempt"), "A three-digit number is chosen at random.")
    has("C3 YT question b", exq(c3, "attempt"), "the number contains at least one five and at least one six,")
    has("C3 YT question c", exq(c3, "attempt"), "the number contains exactly two twos,")
except Exception as ex:
    report(False, "Concept 3", f"ERROR {ex}")


# ================================================================ Exercise 14F
def tbparts(blk):
    return dict(re.findall(r"<b>([a-j])</b>&nbsp;\\\((.+?)\\\)", blk, re.S))


def tbcheck(qn, truths):
    try:
        got = tbparts(A[str(qn)])
        report(sorted(got) == sorted(truths), f"TB{qn} parts", f"printed parts {sorted(got)}")
        for L, t in truths.items():
            chain(f"TB{qn}{L}", got[L], t)
    except Exception as ex:
        report(False, f"TB{qn}", f"ERROR {ex}")


# Q1: club of 9, men 0..4
com = list(combinations(range(9), 3))
tbcheck(1, {"a": len(com), "b": Fr(ncount(com, lambda c: max(c) < 5), len(com))})
# Q2
d2 = list(combinations(range(1, 11), 4))
tbcheck(2, {"a": Fr(ncount(d2, lambda c: c == (1, 2, 3, 6)), len(d2)), "b": Fr(ncount(d2, lambda c: 9 in c), len(d2)),
            "c": Fr(ncount(d2, lambda c: 8 not in c), len(d2)), "d": Fr(ncount(d2, lambda c: 7 in c and 1 not in c), len(d2))})
# Q3: 3 red, 7 yellow, 5 blue
balls = "R" * 3 + "Y" * 7 + "B" * 5
d3 = [sorted(balls[i] for i in c) for c in combinations(range(15), 3)]
tbcheck(3, {"a": Fr(ncount(d3, lambda c: c == ["Y"] * 3), len(d3)), "b": Fr(ncount(d3, lambda c: len(set(c)) == 1), len(d3)),
            "c": Fr(ncount(d3, lambda c: c == ["B", "R", "R"]), len(d3)), "d": Fr(ncount(d3, lambda c: len(set(c)) == 3), len(d3))})
# Q4: 8 AFL (0..7), 7 soccer (8..14), Ian = 8
d4 = list(combinations(range(15), 5))
soc = lambda c: sum(1 for x in c if x >= 8)
tbcheck(4, {"a": Fr(ncount(d4, lambda c: soc(c) == 0), len(d4)), "b": Fr(ncount(d4, lambda c: soc(c) == 5), len(d4)),
            "c": Fr(ncount(d4, lambda c: soc(c) == 3), len(d4)), "d": Fr(ncount(d4, lambda c: soc(c) >= 1), len(d4)),
            "e": Fr(ncount(d4, lambda c: soc(c) <= 1), len(d4)), "f": Fr(ncount(d4, lambda c: 8 in c), len(d4))})


# Q5 and review Q14: three cards selected at random
def three_card_truths(named, a_rank, b_rank, b2_rank):
    return {
        "named": h3(lambda cs: sorted(cs) == sorted(named)),
        "aces": h3(lambda cs: all(c[0] == 1 for c in cs)),
        "kings": h3(lambda cs: all(c[0] == 13 for c in cs)),
        "diamonds": h3(lambda cs: all(c[1] == "D" for c in cs)),
        "clubs": h3(lambda cs: all(c[1] == "C" for c in cs)),
        "same suit": h3(lambda cs: len(suits(cs)) == 1),
        "picture": h3(lambda cs: all(c[0] >= 11 for c in cs)),
        "2 red 1 black": h3(lambda cs: sum(c[1] in RED for c in cs) == 2),
        "1 red 2 black": h3(lambda cs: sum(c[1] in RED for c in cs) == 1),
        "one each": h3(lambda cs: sorted(c[0] for c in cs) == sorted(a_rank)),
        "two and one": h3(lambda cs: sorted(c[0] for c in cs) == sorted(b_rank)),
        "one diamond": h3(lambda cs: sum(c[1] == "D" for c in cs) == 1),
        "2+ diamonds": h3(lambda cs: sum(c[1] == "D" for c in cs) >= 2),
        "2+ spades": h3(lambda cs: sum(c[1] == "S" for c in cs) >= 2),
    }


t5 = three_card_truths([(11, "S"), (2, "C"), (7, "D")], [7, 8, 9], [7, 7, 6], None)
tbcheck(5, {"a": t5["named"], "b": t5["aces"], "c": t5["diamonds"], "d": t5["same suit"], "e": t5["picture"], "f": t5["2 red 1 black"],
            "g": t5["one each"], "h": t5["two and one"], "i": t5["one diamond"], "j": t5["2+ diamonds"]})
# Q6: with replacement, ordered draws of three cards
d6 = list(product(range(52), repeat=3))


def r6(cond):
    return Fr(ncount(d6, lambda t: cond([DECK[i] for i in t])), len(d6))


tbcheck(6, {"a": r6(lambda cs: sorted(cs) == sorted([(11, "S"), (2, "C"), (7, "D")])), "b": r6(lambda cs: all(c[0] == 1 for c in cs)),
            "c": r6(lambda cs: all(c[1] == "D" for c in cs)), "d": r6(lambda cs: len(suits(cs)) == 1), "e": r6(lambda cs: all(c[0] >= 11 for c in cs)),
            "f": r6(lambda cs: sum(c[1] in RED for c in cs) == 2), "g": r6(lambda cs: sorted(c[0] for c in cs) == [7, 8, 9]),
            "h": r6(lambda cs: sorted(c[0] for c in cs) == [6, 7, 7]), "i": r6(lambda cs: sum(c[1] == "D" for c in cs) == 1),
            "j": r6(lambda cs: sum(c[1] == "D" for c in cs) >= 2)})
# Q7: boys 0,1,2; girls 3,4,5 (specific girls 3, 4)
d7 = list(permutations(range(6)))
boy = lambda x: x < 3
adj = lambda p, a, b: abs(p.index(a) - p.index(b)) == 1
tbcheck(7, {"a": Fr(ncount(d7, lambda p: all(boy(p[i]) != boy(p[i + 1]) for i in range(5))), len(d7)),
            "b": Fr(ncount(d7, lambda p: sum(boy(p[i]) != boy(p[i + 1]) for i in range(5)) == 1), len(d7)),
            "c": Fr(ncount(d7, lambda p: adj(p, 3, 4)), len(d7))})
# Q8: parents 0, 1
d8 = list(permutations(range(5)))
tbcheck(8, {"a": Fr(ncount(d8, lambda p: {p[0], p[4]} == {0, 1}), len(d8)), "b": Fr(ncount(d8, lambda p: adj(p, 0, 1)), len(d8))})
# Q9: Patrick 0, Jessica 1
d9 = list(permutations(range(6)))
tbcheck(9, {"a": Fr(ncount(d9, lambda p: {p[0], p[5]} == {0, 1}), len(d9)), "b": Fr(ncount(d9, lambda p: not adj(p, 0, 1)), len(d9))})
# Q10: PROMISE
d10 = list(permutations("PROMISE"))
V = set("OIE")
tbcheck(10, {"a": Fr(ncount(d10, lambda p: p[0] == "R" and p[-1] == "S"), len(d10)), "b": Fr(ncount(d10, lambda p: adj(p, "P", "R")), len(d10)),
             "c": Fr(ncount(d10, lambda p: abs(p.index("P") - p.index("R")) >= 4), len(d10)),
             "d": Fr(ncount(d10, lambda p: all((p[i] in V) != (p[i + 1] in V) for i in range(6))), len(d10)),
             "e": Fr(ncount(d10, lambda p: max(p.index(v) for v in V) - min(p.index(v) for v in V) == 2), len(d10))})
# Q11: 3,3,4,4,4,5 (distinct numbers, each equally likely)
d11 = sorted(set(permutations("334445")))
tbcheck(11, {"a": Fr(ncount(d11, lambda p: p[-1] == "4"), len(d11)), "b": Fr(ncount(d11, lambda p: p[-1] == "5"), len(d11)),
             "c": Fr(ncount(d11, lambda p: "444" in "".join(p)), len(d11)), "d": Fr(ncount(d11, lambda p: "".join(p) in ("543434", "534343")), len(d11)),
             "e": Fr(ncount(d11, lambda p: "33" not in "".join(p)), len(d11))})
report(len(d11) == 60, "TB11 sample space", f"{len(d11)} different numbers")
# Q12: PRINTER, letters labelled (the two Rs are R1, R2)
d12 = list(permutations(["P", "R1", "I", "N", "T", "E", "R2"]))
gap = lambda p, a, b: abs(p.index(a) - p.index(b)) - 1
tbcheck(12, {"a": Fr(ncount(d12, lambda p: p[0] == "E"), len(d12)), "b": Fr(ncount(d12, lambda p: adj(p, "I", "P")), len(d12)),
             "c": Fr(ncount(d12, lambda p: gap(p, "N", "T") == 3), len(d12)), "d": Fr(ncount(d12, lambda p: gap(p, "N", "T") >= 3), len(d12))})
# Q13: KETTLE labelled
d13 = list(permutations(["K", "E1", "T1", "T2", "L", "E2"]))
grp = lambda p, xs: max(p.index(x) for x in xs) - min(p.index(x) for x in xs) == len(xs) - 1
tbcheck(13, {"a": Fr(ncount(d13, lambda p: adj(p, "E1", "E2")), len(d13)), "b": Fr(ncount(d13, lambda p: not adj(p, "E1", "E2")), len(d13)),
             "c": Fr(ncount(d13, lambda p: adj(p, "E1", "E2") and adj(p, "T1", "T2")), len(d13)),
             "d": Fr(ncount(d13, lambda p: grp(p, ["E1", "E2", "T1", "T2"])), len(d13))})


# Q14: ENTERTAINMENT. Every arrangement of the other 10 letters goes with each set of E positions, so the
# events (which depend only on the E positions) are counted on the 13C3 position sets. Checked first on a short word.
def e_events(pos, n):
    pos = sorted(pos)
    blocks = sum(1 for i in range(len(pos) - 1) if pos[i + 1] - pos[i] == 1)
    return {"together": blocks == 2, "two and one": blocks == 1, "apart": blocks == 0, "ends": pos[0] == 0 and pos[-1] == n - 1}


small = "EEENTNA"
full = sorted(set(permutations(small)))
ok14 = all(Fr(ncount(full, lambda w: e_events([i for i, c in enumerate(w) if c == "E"], len(small))[k]), len(full))
           == Fr(ncount(combinations(range(len(small)), 3), lambda ps: e_events(ps, len(small))[k]), comb(len(small), 3)) for k in ("together", "two and one", "apart", "ends"))
report(ok14, "TB14 method", f"E-position counting agrees with all {len(full)} arrangements of {small}")
pos14 = list(combinations(range(13), 3))
report(Counter("ENTERTAINMENT")["E"] == 3, "TB14 word", "ENTERTAINMENT has three Es")
tbcheck(14, {"a": Fr(ncount(pos14, lambda ps: e_events(ps, 13)["together"]), len(pos14)), "b": Fr(ncount(pos14, lambda ps: e_events(ps, 13)["two and one"]), len(pos14)),
             "c": Fr(ncount(pos14, lambda ps: e_events(ps, 13)["apart"]), len(pos14)), "d": Fr(ncount(pos14, lambda ps: e_events(ps, 13)["ends"]), len(pos14))})
# Q15: fish 0..19 tagged; four selected at random each day
n15, none15 = 0, 0
for c in combinations(range(100), 4):
    n15 += 1
    if c[0] >= 20:
        none15 += 1
p15 = Fr(none15, n15)
week = {k: sum(eval("*".join(["p15" if b else "(1-p15)" for b in bits])) for bits in product([1, 0], repeat=7) if sum(bits) == k) for k in (3, 7)}
try:
    got = tbparts(A["15"])
    for L, t in (("a", p15), ("b", 1 - p15), ("c", week[7]), ("d", week[3])):
        v = tex_eval(got[L])
        report(v == sig(t, 3), f"TB15{L}", f"printed {got[L]}, computed {float(t):.6g}, to 3 s.f. {float(sig(t, 3))}")
except Exception as ex:
    report(False, "TB15", f"ERROR {ex}")
# Q16: 7 white (0..6), 5 black (7..11)
c16 = list(combinations(range(12), 3))
w16 = list(product(range(12), repeat=3))


def tree_all_black(w, b, k):
    out = Fr(0)
    for path in product("WB", repeat=k):           # every path of colours, with the bag changing after each draw
        pr, ww, bb = Fr(1), w, b
        for col in path:
            pr *= Fr(bb if col == "B" else ww, ww + bb)
            ww, bb = (ww + 1, bb - 1) if col == "B" else (ww - 1, bb + 1)
        if path == ("B",) * k:
            out += pr
    return out


tbcheck(16, {"a": Fr(ncount(c16, lambda c: min(c) >= 7), len(c16)), "b": Fr(ncount(w16, lambda t: min(t) >= 7), len(w16)), "c": tree_all_black(7, 5, 3)})
# Q17: divisions of six people into two non-empty groups (unordered)
div17 = {frozenset([frozenset(g), frozenset(set(range(6)) - set(g))]) for r in range(1, 6) for g in combinations(range(6), r)}
sz = lambda d: sorted(len(g) for g in d)
tbcheck(17, {"a": Fr(ncount(div17, lambda d: sz(d) == [3, 3]), len(div17)), "b": Fr(ncount(div17, lambda d: sz(d) == [2, 4]), len(div17)),
             "c": Fr(ncount(div17, lambda d: sz(d) == [1, 5]), len(div17))})
# Q18
d18 = ["".join(p) for p in permutations("34567", 3)]
tbcheck(18, {"a": frac_of(d18, lambda s: s == "473"), "b": frac_of(d18, lambda s: int(s) % 2 == 1), "c": frac_of(d18, lambda s: int(s) % 5 == 0),
             "d": frac_of(d18, lambda s: int(s) % 3 == 0), "e": frac_of(d18, lambda s: s[0] == "4" and s[-1] == "7"), "f": frac_of(d18, lambda s: "3" in s),
             "g": frac_of(d18, lambda s: "3" in s and "5" in s), "h": frac_of(d18, lambda s: "3" in s or "5" in s),
             "i": frac_of(d18, lambda s: set(s) <= set("3579")), "j": frac_of(d18, lambda s: int(s) > 500)})
# Q19: the digits 1, 2, 3, 4 used (each at most once) in numbers of 1 to 4 digits
d19 = ["".join(p) for r in range(1, 5) for p in permutations("1234", r)]
tbcheck(19, {"a": frac_of(d19, lambda s: len(s) == 3), "b": frac_of(d19, lambda s: int(s) % 2 == 0), "c": frac_of(d19, lambda s: int(s) > 200),
             "d": frac_of(d19, lambda s: int(s) % 2 == 1 and int(s) > 3000), "e": frac_of(d19, lambda s: int(s) % 3 == 0)})


# Q20: Labor 0..N-1, Liberal N..N+4
def labor_majority(N):
    cs = list(combinations(range(N + 5), 5))
    return Fr(ncount(cs, lambda c: sum(1 for x in c if x < N) >= 3), len(cs))


try:
    got = tbparts(A["20"])
    chain("TB20a", got["a"], labor_majority(6))
    nmin = next(N for N in range(1, 30) if labor_majority(N) > Fr(3, 4))
    report(got["b"] == f"N={nmin}", "TB20b", f"printed {got['b']}, smallest N with P > 3/4: {nmin} (P = {labor_majority(nmin)}; N - 1 gives {labor_majority(nmin - 1)})")
except Exception as ex:
    report(False, "TB20", f"ERROR {ex}")
# Q21: player = (team, number)
pl21 = [(t, k) for t in "ABCD" for k in range(1, 11)]
c21 = list(combinations(range(40), 5))
tbcheck(21, {"a": Fr(ncount(c21, lambda c: sorted(pl21[i][1] for i in c) == [4, 4, 4, 9, 9]), len(c21)),
             "b": Fr(ncount(c21, lambda c: max(Counter(pl21[i][0] for i in c).values()) >= 4), len(c21))})


# Q22: every poker hand
def classify(cards):
    rk = Counter(c[0] for c in cards)
    shape = sorted(rk.values(), reverse=True)
    vals = set(rk)
    seqs = [set(range(lo, lo + 5)) for lo in range(1, 10)] + [{10, 11, 12, 13, 1}]
    return {"one pair": shape == [2, 1, 1, 1], "two pairs": shape == [2, 2, 1], "three": shape == [3, 1, 1], "four": shape == [4, 1],
            "full house": shape == [3, 2], "straight": vals in seqs, "flush": len({c[1] for c in cards}) == 1,
            "royal": len({c[1] for c in cards}) == 1 and vals == {10, 11, 12, 13, 1}}


cnt22, n22 = Counter(), 0
for h in combinations(range(52), 5):
    n22 += 1
    for k, v in classify([DECK[i] for i in h]).items():
        if v:
            cnt22[k] += 1
try:
    b22 = A["22"]
    got = dict(re.findall(r"<b>([a-h])</b>(?:&nbsp;| )\\\((.+?)\\\)", b22, re.S))
    keys = dict(zip("abcdefgh", ["one pair", "two pairs", "three", "four", "full house", "straight", "flush", "royal"]))
    report(sorted(got) == list("abcdefgh"), "TB22 parts", f"{sorted(got)}")
    for L, k in keys.items():
        chain(f"TB22{L}", got[L], Fr(cnt22[k], n22))
    expl = maths(b22)
    report(chain_ok(expl[0], n22)[0], "TB22 sample space", f"{expl[0]} = {n22}")
    pair_ways = 13 * ncount(combinations(range(4), 2)) * ncount(combinations(range(12), 3)) * 4 ** 3
    twop_ways = ncount(combinations(range(13), 2)) * ncount(combinations(range(4), 2)) ** 2 * 44
    str_ways = 10 * 4 ** 5
    report(pair_ways == cnt22["one pair"] and "{}^{4}\\mathrm{C}_{2}=6" in b22 and "{}^{12}\\mathrm{C}_{3}" in b22 and "4^3" in b22, "TB22a reason", f"13 x 6 x 12C3 x 4^3 = {pair_ways}")
    report(twop_ways == cnt22["two pairs"] and "{}^{13}\\mathrm{C}_{2}" in b22 and "{}^{4}\\mathrm{C}_{2}\\times{}^{4}\\mathrm{C}_{2}" in b22 and "in 44 ways" in b22, "TB22b reason", f"13C2 x 6 x 6 x 44 = {twop_ways}")
    report(str_ways == cnt22["straight"] and "lowest card in 10 ways" in b22 and "4^5" in b22, "TB22f reason", f"10 x 4^5 = {str_ways}")
except Exception as ex:
    report(False, "TB22", f"ERROR {ex}")
# Q23: adults 0..3, exits 0..4
d23 = list(product(range(5), repeat=4))
tbcheck(23, {"a": Fr(ncount(d23, lambda t: len(set(t)) == 1), len(d23)),
             "b": Fr(ncount(d23, lambda t: t[0] == t[1] == t[2] != t[3]), len(d23)),
             "c": Fr(ncount(d23, lambda t: sorted(Counter(t).values()) == [1, 3]), len(d23)),
             "d": Fr(ncount(d23, lambda t: max(Counter(t).values()) <= 2), len(d23))})


# Q24: diners choose courses
def one_unchosen(n):
    ts = list(product(range(n), repeat=n))
    return Fr(ncount(ts, lambda t: len(set(t)) == n - 1), len(ts))


try:
    got = tbparts(A["24"])
    chain("TB24a", got["a"], one_unchosen(5))
    algebra("TB24b", got["b"], lambda n: one_unchosen(int(n)), [dict(n=k) for k in range(2, 8)])
except Exception as ex:
    report(False, "TB24", f"ERROR {ex}")


# Q25: birthdays. Sequential probability, checked by enumeration on a short 'year' first.
def p_common_seq(days, n):
    q = Fr(1)
    for i in range(n):
        q *= Fr(days - i, days)
    return 1 - q


okbd = all(p_common_seq(D, n) == Fr(ncount(product(range(D), repeat=n), lambda t: len(set(t)) < n), D ** n) for D in (5, 7) for n in (2, 3, 4, 5))
report(okbd, "TB25 method", "sequential probability agrees with enumeration for 5- and 7-day years, n = 2..5")
try:
    got = tbparts(A["25"])
    report(tex_eval(got["a"]) == sig(p_common_seq(365, 3), 2), "TB25a", f"printed {got['a']}, computed {float(p_common_seq(365, 3)):.6g}")
    algebra("TB25b", got["b"], lambda n: p_common_seq(365, int(n)), [dict(n=k) for k in (1, 2, 3, 10, 23, 41, 50)])
    n05 = next(n for n in range(1, 100) if p_common_seq(365, n) > Fr(1, 2))
    n09 = next(n for n in range(1, 100) if p_common_seq(365, n) > Fr(9, 10))
    chain("TB25d", got["d"], n05)
    chain("TB25e", got["e"], n09)
    report(sorted(got) == ["a", "b", "d", "e"], "TB25 parts", "c is a graph, no printed answer")
except Exception as ex:
    report(False, "TB25", f"ERROR {ex}")
# Q26: blocks of three consecutive games starting at game 1..5
blk = [set(range(s, s + 3)) for s in range(1, 6)]
d26 = [(m, b) for m in blk for b in blk]
tbcheck(26, {"a": Fr(ncount(d26, lambda mb: 1 in mb[0] and 1 in mb[1]), len(d26)),
             "b": Fr(ncount(d26, lambda mb: bool(mb[0] & mb[1]) and min(mb[0] & mb[1]) == 2), len(d26)),
             "c": Fr(ncount(d26, lambda mb: bool(mb[0] & mb[1])), len(d26))})


# Q27: knockout tournament. Every slot pair for the two players, every result of every match.
@lru_cache(maxsize=None)
def meet(bracket):
    """bracket: tuple of 'a', 'b', 'x'. Returns (P(a and b meet), distribution of the winner label)."""
    if len(bracket) == 1:
        return Fr(0), ((bracket[0], Fr(1)),)
    h = len(bracket) // 2
    m1, w1 = meet(bracket[:h])
    m2, w2 = meet(bracket[h:])
    pm, win = m1 + m2, Counter()
    for l1, p1 in w1:
        for l2, p2 in w2:
            if {l1, l2} == {"a", "b"}:
                pm += p1 * p2
            for l in (l1, l2):                     # each player of the final match wins with probability 1/2
                win[l] += p1 * p2 / 2
    return pm, tuple(sorted(win.items()))


def p_meet(players):
    tot, n = Fr(0), 0
    for i, j in permutations(range(players), 2):
        br = ["x"] * players
        br[i], br[j] = "a", "b"
        tot += meet(tuple(br))[0]
        n += 1
    return tot / n


def p_meet_brute8():
    """Eight players: every draw of a and b and all 2^7 match results, played out directly."""
    tot, n = Fr(0), 0
    for i, j in permutations(range(8), 2):
        for res in product((0, 1), repeat=7):
            rnd, k, met = list(range(8)), 0, False
            while len(rnd) > 1:
                nxt = []
                for q in range(0, len(rnd), 2):
                    x, y = rnd[q], rnd[q + 1]
                    if {x, y} == {i, j}:
                        met = True
                    nxt.append(x if res[k] == 0 else y)
                    k += 1
                rnd = nxt
            tot += Fr(1, 2 ** 7) if met else 0
        n += 1
    return tot / n


try:
    report(p_meet_brute8() == p_meet(8) == Fr(1, 4) and "show that the probability that any two particular players will play each other is \\(\\tfrac14\\)" in Q[27],
           "TB27a", f"8 players: {p_meet_brute8()} by brute force, {p_meet(8)} by the recursion; stem says 1/4")
    got = tbparts(A["27"])
    chain("TB27b", got["b"], p_meet(16))
    algebra("TB27c", got["c"], lambda n: p_meet(2 ** int(n)), [dict(n=k) for k in range(1, 6)])
except Exception as ex:
    report(False, "TB27", f"ERROR {ex}")

report(sorted(Q) == list(range(1, 28)), "TB question numbers", f"{sorted(Q)}")
ans_q = sorted(int(k) for k in A if k.isdigit())
report(ans_q == list(range(1, 28)), "TB answer numbers", f"{ans_q}")
report(HW.count("{{band:F}}") == HW.count("{{band:D}}") == HW.count("{{band:E}}") == 1
       and HW.index('<span class="q-num">9</span>') < HW.index("{{band:D}}") < HW.index('<span class="q-num">10</span>')
       and HW.index('<span class="q-num">25</span>') < HW.index("{{band:E}}") < HW.index('<span class="q-num">26</span>'),
       "TB bands", "F 1-9, D 10-25, E 26-27")

# ================================================================ Chapter 14 review
try:
    report(sorted(RQ) == list(range(1, 15)) and sorted(int(k) for k in RA) == list(range(1, 15)), "review numbers", f"lesson {sorted(RQ)}, answers {sorted(RA)}")
    report(not any(w in RVL for w in ("circle", "peanuts", "monkey", "1500 people", "pigeon")), "review scope", "Q15 (circle) and Q16-17 (pigeonhole) are not printed")
    chain("RV1", maths(RA["1"])[0], ncount(permutations(range(8))))
    g2 = tbparts(RA["2"])
    chain("RV2a", g2["a"], ncount(permutations(range(9), 2)))
    algebra("RV2b", g2["b"], lambda n: Fr(factorial(int(n) + 1), factorial(int(n) - 1)), [dict(n=k) for k in range(1, 9)])
    algebra("RV2c", g2["c"].replace("k", "n"), lambda n: Fr(factorial(int(n) + 1) - factorial(int(n))), [dict(n=k) for k in range(0, 9)])
    g3 = tbparts(RA["3"])
    chain("RV3a", g3["a"], k_subsets(12, 7))
    chain("RV3b", g3["b"], Fr(k_subsets(10, 3), k_subsets(6, 3)))
    chain("RV3c", g3["c"], k_subsets(20, 17))
    report(len(set("JACKSON")) == 7, "RV4 letters", "JACKSON has 7 different letters")
    chain("RV4", maths(RA["4"])[0], ncount(permutations("JACKSON", 4)))
    chain("RV5", maths(RA["5"])[0], ncount(product(range(26), repeat=3)) * ncount(product(range(10), repeat=4)))
    d6r = list(permutations("FOUNDER"))
    vw = set("OUE")
    g6 = tbparts(RA["6"])
    t6 = {"a": ncount(d6r, lambda p: all((p[i] in vw) != (p[i + 1] in vw) for i in range(6))), "b": ncount(d6r, lambda p: p[0] == "N" and p[-1] == "D"),
          "c": ncount(d6r, lambda p: set(p[3:]) == set("FNDR")), "d": ncount(d6r, lambda p: p.index("R") > p.index("U"))}
    for L in "abcd":
        chain(f"RV6{L}", g6[L], t6[L])
    report("(half of the total)" in RA["6"] and 2 * t6["d"] == len(d6r), "RV6d half", "R right of U in exactly half")
    g7 = tbparts(RA["7"])
    n7a = n7b = n7c = 0
    for p in permutations(range(10)):                  # boys 0..4, girls 5..9; the particular boy 0 and girl 5
        n7a += 1
        if sum((p[i] < 5) != (p[i + 1] < 5) for i in range(9)) == 1:
            n7b += 1
        if abs(p.index(0) - p.index(5)) == 1:
            n7c += 1
    for L, t in zip("abc", (n7a, n7b, n7c)):
        chain(f"RV7{L}", g7[L], t)
    chain("RV8", maths(RA["8"])[0], len(set(permutations("REPORTER"))))
    chain("RV9", maths(RA["9"])[0], ncount(permutations("SAMUEL", 3)) + ncount(permutations("SAMUEL", 4)))
    chain("RV10", maths(RA["10"])[0], ncount(product((0, 1), repeat=10), lambda t: sum(t) == 6))
    # Q11: men 0..5 (Mustafa = 0), women 6..15 (Ying Yue = 6)
    c11 = list(combinations(range(16), 7))
    men = lambda c: sum(1 for x in c if x < 6)
    t11 = {"a": len(c11), "b": ncount(c11, lambda c: men(c) == 0), "c": ncount(c11, lambda c: men(c) == 7), "d": ncount(c11, lambda c: men(c) == 2),
           "e": ncount(c11, lambda c: men(c) == 3), "f": ncount(c11, lambda c: 7 - men(c) > men(c)), "g": ncount(c11, lambda c: 0 in c),
           "h": ncount(c11, lambda c: 0 not in c), "i": ncount(c11, lambda c: not (0 in c and 6 in c))}
    p11 = parts(RA["11"], "abcdefghi")
    for L, t in t11.items():
        first_math(f"RV11{L}", p11[L], t)
    c12 = list(combinations(range(8), 5))
    g12 = tbparts(RA["12"])
    chain("RV12a", g12["a"], len(c12))
    chain("RV12b", g12["b"], ncount(combinations(range(8), 4)))
    chain("RV12c", g12["c"], len({frozenset([frozenset(g), frozenset(set(range(8)) - set(g))]) for g in combinations(range(8), 4)}))
    c13 = list(combinations(range(7), 6))                  # men 0..3, women 4..6
    p13 = Fr(ncount(c13, lambda c: sum(1 for x in c if x < 4) > 3), len(c13))
    m13 = maths(RA["13"])
    report(len(m13) == 2, "RV13 pieces", f"{m13}")
    chain("RV13", m13[0], p13)
    chain("RV13 alt", m13[1], p13)
    report(ncount(c13, lambda c: sum(1 for x in c if x < 4) > 3) == ncount(range(4, 7)), "RV13 alt reason", "more men exactly when the one person left out is a woman")
    t14 = three_card_truths([(12, "S"), (3, "C"), (9, "H")], [3, 5, 8], [5, 5, 7], None)
    g14 = tbparts(RA["14"])
    for L, k in zip("abcdefgh", ("named", "kings", "clubs", "same suit", "1 red 2 black", "one each", "two and one", "2+ spades")):
        chain(f"RV14{L}", g14[L], t14[k])
    has("RV14 question", RQ[14], "they are the queen of spades, the three of clubs and the nine of hearts,")
    has("RV2 box", RQ[2], "see Box 2 in Lesson 14A")
    report("Calculating by unrolling factorials" in read("l14a.html") and "Box 2 &nbsp;Calculating by unrolling" in read("l14a.html"), "RV2 box exists", "Box 2 of Lesson 14A is the unrolling box")
except Exception as ex:
    report(False, "review", f"ERROR {ex}")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", PPL)
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', PPL)]
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
        report(src_q == src_a and "Extension&nbsp;1" in src_q and re.search(r",&nbsp;Q\d", src_q) is not None, f"PP{n_} source label", src_q)
        report(PPQ[n_].count('<div class="hint"><b>Hint:</b>') == 1, f"PP{n_} hint", "exactly one hint")
except Exception as ex:
    report(False, "lesson structure", f"ERROR {ex}")


def mc_letter(pp, value, pattern, conv):
    try:
        opts = {k: conv(v) for k, v in re.findall(pattern, PPQ[pp])}
        letter = re.search(r"<b>Answer \(?([A-D])\)?\.</b>", PPA[pp]).group(1)
        hit = [k for k, v in opts.items() if v == value]
        report(len(opts) == 4 and hit == [letter], f"PP{pp} MC letter", f"options {[(k, str(v)) for k, v in opts.items()]}; printed {letter}; option equal to {value} is {hit}")
    except Exception as ex:
        report(False, f"PP{pp} MC letter", f"ERROR {ex}")


# ---------------------------------------------------------------- PP 1: blue 0..4, black 5..10, red 11..13
c1p = list(combinations(range(14), 3))
p1 = Fr(ncount(c1p, lambda c: sum(1 for x in c if x < 5) == 2), len(c1p))
try:
    m1 = maths(PPA[1])
    for t, v in zip(m1[:4], (len(c1p), k_subsets(5, 2), 14 - 5, k_subsets(9, 1))):
        chain("PP1 step", t, v)
    tpl("PP1", PPA[1], r"P(\text{exactly two blue})=@.\]", p1)
    mc_letter(1, p1, r"<span>\(([A-D])\) \\\((.+?)\\\)</span>", tex_eval)
    report("Option (A) forgets to choose the third marble" in PPA[1] and tex_eval(r"\dfrac{{}^{5}\mathrm{C}_{2}}{{}^{14}\mathrm{C}_{3}}") * 9 == p1, "PP1 option A", "A is the answer without the factor 9C1")
except Exception as ex:
    report(False, "PP1", f"ERROR {ex}")
has("PP1 question", PPQ.get(1, ""), "A bag contains 5 identical blue marbles, 6 identical black marbles and 3 identical red marbles. Three marbles are drawn at random.")
# ---------------------------------------------------------------- PP 2: the player's numbers are 0..5
c2p, fav2 = 0, 0
for c in combinations(range(30), 6):
    c2p += 1
    if sum(1 for x in c if x < 6) >= 4:
        fav2 += 1
p2 = Fr(fav2, c2p)
try:
    chain("PP2 draws", maths(PPA[2])[0], c2p)
    aligned("PP2 favourable", PPA[2], r"\[\begin{aligned}\text{number of favourable draws}&=@\end{aligned}\]", fav2)
    approx("PP2 P", find(PPA[2], r"P(\text{at least 4 matches})=@\]"), p2, places=4)
    mc_letter(2, dp(p2, 3), r"<span>([A-D])\. ([\d.]+)</span>", lambda v: Fr(v))
    report("To three decimal places the probability is 0.007." in PPA[2] and dp(p2, 3) == Fr("0.007"), "PP2 rounding", f"{float(p2):.6f}")
except Exception as ex:
    report(False, "PP2", f"ERROR {ex}")
has("PP2 question", PPQ.get(2, ""), "A lottery has 30 numbers and 6 are drawn without replacement.")
# ---------------------------------------------------------------- PP 3: female 0..19, male 20..24
n3, f3 = 0, 0
for c in combinations(range(25), 13):
    n3 += 1
    if c[-1] < 20:
        f3 += 1
try:
    m3 = maths(PPA[3])
    chain("PP3 teams", m3[0], n3)
    chain("PP3 female", m3[1], f3)
    tpl("PP3", PPA[3], r"P(\text{only female players})=@.\]", Fr(f3, n3))
except Exception as ex:
    report(False, "PP3", f"ERROR {ex}")
has("PP3 question", PPQ.get(3, ""), "a team of 13 players is to be chosen from a pool of 25 players consisting of 20 female players and 5 male players.")
# ---------------------------------------------------------------- PP 4
h2 = list(combinations(range(52), 2))
p4 = Fr(ncount(h2, lambda h: any(DECK[i][1] == "H" for i in h)), len(h2))
try:
    m4 = maths(PPA[4])
    chain("PP4 hands", m4[0], len(h2))
    chain("PP4 no heart", m4[1], ncount(h2, lambda h: all(DECK[i][1] != "H" for i in h)))
    tpl("PP4", PPA[4], r"P(\text{at least 1 heart})=@.\]", p4)
    d4o = list(permutations(range(52), 2))
    chain("PP4 ordered check", m4[2], Fr(ncount(d4o, lambda d: any(DECK[i][1] == "H" for i in d)), len(d4o)))
except Exception as ex:
    report(False, "PP4", f"ERROR {ex}")
has("PP4 question", PPQ.get(4, ""), "2 cards are chosen at random, without replacement, from a standard 52-deck of playing cards.")
# ---------------------------------------------------------------- PP 5: girls 0..9, boys 10..17
c5p = list(combinations(range(18), 5))
p5 = Fr(ncount(c5p, lambda c: sum(1 for x in c if x < 10) == 3), len(c5p))
try:
    m5 = maths(PPA[5])
    for t, v in zip(m5[:4], (18, len(c5p), k_subsets(10, 3), k_subsets(8, 2))):
        chain("PP5 step", t, v)
    tpl("PP5", PPA[5], r"P(\text{3 girls and 2 boys})=@.\]", p5)
except Exception as ex:
    report(False, "PP5", f"ERROR {ex}")
has("PP5 question", PPQ.get(5, ""), "A class consists of 10 girls and 8 boys.")
# ---------------------------------------------------------------- PP 6: Jun = 0, Alex = 1
c6p = list(combinations(range(20), 7))
try:
    tpl("PP6 (i)", PPA[6], r"\[\text{number of committees}=@\]", len(c6p))
    chain("PP6 (ii) count", maths(PPA[6])[0], ncount(c6p, lambda c: 0 in c and 1 not in c))
    tpl("PP6 (ii)", PPA[6], r"P(\text{Jun but not Alex})=@.\]", Fr(ncount(c6p, lambda c: 0 in c and 1 not in c), len(c6p)))
except Exception as ex:
    report(False, "PP6", f"ERROR {ex}")
has("PP6 question", PPQ.get(6, ""), "A school has twenty prefects. Jun and Alex are two of those prefects.")


# ---------------------------------------------------------------- PP 7: the friends' classes, by sequential probability
def friends_seq(students, size, friends=4):
    """Distribution of the number of friends in class A: each friend in turn takes a place in A or B."""
    dist = Counter()
    for path in product("AB", repeat=friends):
        pr, a, b, left = Fr(1), size, students - size, students
        for cl in path:
            pr *= Fr(a if cl == "A" else b, left)
            a, b, left = (a - 1, b, left - 1) if cl == "A" else (a, b - 1, left - 1)
        dist[path] += pr
    return dist


def friends_brute(students, size, friends=4):
    dist, n = Counter(), 0
    for A_ in combinations(range(students), size):
        s = set(A_)
        dist[tuple("A" if f in s else "B" for f in range(friends))] += 1
        n += 1
    return {k: Fr(v, n) for k, v in dist.items()}


report(all(friends_seq(N_, N_ // 2) == friends_brute(N_, N_ // 2) for N_ in (8, 10, 12)), "PP7 method", "sequential places agree with listing every class A for 8, 10, 12 students")
seq = friends_seq(40, 20)
p7i = seq[("A",) * 4] + seq[("B",) * 4]
p7_one = seq[("A", "A", "A", "B")]
p7ii = sum(v for k, v in seq.items() if sorted(Counter(k).values()) == [1, 3])
try:
    b7 = PPA[7]
    b7i, b7ii = b7.split("<p>(ii)")
    r1 = find(b7i, r"Since</p>" + "\n" + r"\[@,\]" + "\n" + r"\[P(\text{all four")
    chain("PP7 (i) ratio", r1, seq[("A",) * 4])
    approx("PP7 (i)", find(b7i, r"P(\text{all four in the same class})=@.\]"), p7i, places=3)
    r2 = find(b7ii, r"Since</p>" + "\n" + r"\[@,\]" + "\n" + r"\[P(\text{exactly three")
    chain("PP7 (ii) ratio", r2, p7_one)
    approx("PP7 (ii)", find(b7ii, r"P(\text{exactly three in the same class})=@.\]"), p7ii, places=3)
    chain("PP7 4C3", maths(b7)[[i for i, t in enumerate(maths(b7)) if t.startswith("{}^{4}")][0]], k_subsets(4, 3))
    report(seq[("A",) * 4] == seq[("B",) * 4], "PP7 symmetry", "all in A and all in B are equally likely")
except Exception as ex:
    report(False, "PP7", f"ERROR {ex}")
has("PP7 question", PPQ.get(7, ""), "A group of 40 new Year 7 students is going to be randomly divided into two classes A and B of 20 students each.")

report(not any(s in LES + ANS for s in ("Blacktown Boys’ High School, 2022", "Epping", "Baulkham Hills High School, 2023", "James Ruse", "Western", "Sample 1")),
       "left-out items", "BBHS 2022 Q6, Epping 2024 Q11(a), BHHS 2023 Q11(c)(i), JRAHS 2020 Q14(c), Western 2020 Q10 and STHS Sample 1 Q8 are not used")
print(f"\n{COUNT[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{COUNT[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
