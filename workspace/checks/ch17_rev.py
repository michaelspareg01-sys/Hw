"""Check of the Chapter 17 Revision section (Advanced Ch 16 normal review), tied to the HTML.

Reads workspace/build/ch17/revision.html and a_rev.html.
  1. The standard normal table printed in revision.html: 40 rows z = 0.0 .. 3.9, columns +.00 .. +.09.
     Every printed value is compared with Phi(z) = (1 + erf(z/sqrt 2))/2 rounded to 4 d.p., and with the
     values printed in the textbook's table (CambridgeMATHS Ext 1 Y12, Exercise 17C, PDF pages 829-830,
     book pages 803-804), transcribed below.
  2. Printed values in the summary boxes and the four textbook worked examples (10, 13, 15, 17).
  3. The six warm-up questions: the givens are read from revision.html, the answers are recomputed with
     math.erf (table look-up: z to 2 d.p., Phi to 4 d.p., as the textbook does) and compared with every
     printed value in a_rev.html and with the textbook's printed answers (PDF pages 956-958).
Every template ('@' = one number) must match exactly once in its block, otherwise the item FAILS.
Exit status 1 if anything fails.  Run: python3 workspace/checks/ch17_rev.py
"""
import os
import re
import sys
from decimal import Decimal as D, ROUND_HALF_UP
from math import erf, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("CH17_SRC", os.path.join(HERE, "..", "build", "ch17"))   # override only for mutation tests

# Textbook table (PDF 829-830): row z (first decimal place) -> values for +.00 .. +.09
BOOK = {
    "0.0": "0.5000 0.5040 0.5080 0.5120 0.5160 0.5199 0.5239 0.5279 0.5319 0.5359",
    "0.1": "0.5398 0.5438 0.5478 0.5517 0.5557 0.5596 0.5636 0.5675 0.5714 0.5753",
    "0.2": "0.5793 0.5832 0.5871 0.5910 0.5948 0.5987 0.6026 0.6064 0.6103 0.6141",
    "0.3": "0.6179 0.6217 0.6255 0.6293 0.6331 0.6368 0.6406 0.6443 0.6480 0.6517",
    "0.4": "0.6554 0.6591 0.6628 0.6664 0.6700 0.6736 0.6772 0.6808 0.6844 0.6879",
    "0.5": "0.6915 0.6950 0.6985 0.7019 0.7054 0.7088 0.7123 0.7157 0.7190 0.7224",
    "0.6": "0.7257 0.7291 0.7324 0.7357 0.7389 0.7422 0.7454 0.7486 0.7517 0.7549",
    "0.7": "0.7580 0.7611 0.7642 0.7673 0.7704 0.7734 0.7764 0.7794 0.7823 0.7852",
    "0.8": "0.7881 0.7910 0.7939 0.7967 0.7995 0.8023 0.8051 0.8078 0.8106 0.8133",
    "0.9": "0.8159 0.8186 0.8212 0.8238 0.8264 0.8289 0.8315 0.8340 0.8365 0.8389",
    "1.0": "0.8413 0.8438 0.8461 0.8485 0.8508 0.8531 0.8554 0.8577 0.8599 0.8621",
    "1.1": "0.8643 0.8665 0.8686 0.8708 0.8729 0.8749 0.8770 0.8790 0.8810 0.8830",
    "1.2": "0.8849 0.8869 0.8888 0.8907 0.8925 0.8944 0.8962 0.8980 0.8997 0.9015",
    "1.3": "0.9032 0.9049 0.9066 0.9082 0.9099 0.9115 0.9131 0.9147 0.9162 0.9177",
    "1.4": "0.9192 0.9207 0.9222 0.9236 0.9251 0.9265 0.9279 0.9292 0.9306 0.9319",
    "1.5": "0.9332 0.9345 0.9357 0.9370 0.9382 0.9394 0.9406 0.9418 0.9429 0.9441",
    "1.6": "0.9452 0.9463 0.9474 0.9484 0.9495 0.9505 0.9515 0.9525 0.9535 0.9545",
    "1.7": "0.9554 0.9564 0.9573 0.9582 0.9591 0.9599 0.9608 0.9616 0.9625 0.9633",
    "1.8": "0.9641 0.9649 0.9656 0.9664 0.9671 0.9678 0.9686 0.9693 0.9699 0.9706",
    "1.9": "0.9713 0.9719 0.9726 0.9732 0.9738 0.9744 0.9750 0.9756 0.9761 0.9767",
    "2.0": "0.9772 0.9778 0.9783 0.9788 0.9793 0.9798 0.9803 0.9808 0.9812 0.9817",
    "2.1": "0.9821 0.9826 0.9830 0.9834 0.9838 0.9842 0.9846 0.9850 0.9854 0.9857",
    "2.2": "0.9861 0.9864 0.9868 0.9871 0.9875 0.9878 0.9881 0.9884 0.9887 0.9890",
    "2.3": "0.9893 0.9896 0.9898 0.9901 0.9904 0.9906 0.9909 0.9911 0.9913 0.9916",
    "2.4": "0.9918 0.9920 0.9922 0.9925 0.9927 0.9929 0.9931 0.9932 0.9934 0.9936",
    "2.5": "0.9938 0.9940 0.9941 0.9943 0.9945 0.9946 0.9948 0.9949 0.9951 0.9952",
    "2.6": "0.9953 0.9955 0.9956 0.9957 0.9959 0.9960 0.9961 0.9962 0.9963 0.9964",
    "2.7": "0.9965 0.9966 0.9967 0.9968 0.9969 0.9970 0.9971 0.9972 0.9973 0.9974",
    "2.8": "0.9974 0.9975 0.9976 0.9977 0.9977 0.9978 0.9979 0.9979 0.9980 0.9981",
    "2.9": "0.9981 0.9982 0.9982 0.9983 0.9984 0.9984 0.9985 0.9985 0.9986 0.9986",
    "3.0": "0.9987 0.9987 0.9987 0.9988 0.9988 0.9989 0.9989 0.9989 0.9990 0.9990",
    "3.1": "0.9990 0.9991 0.9991 0.9991 0.9992 0.9992 0.9992 0.9992 0.9993 0.9993",
    "3.2": "0.9993 0.9993 0.9994 0.9994 0.9994 0.9994 0.9994 0.9995 0.9995 0.9995",
    "3.3": "0.9995 0.9995 0.9995 0.9996 0.9996 0.9996 0.9996 0.9996 0.9996 0.9997",
    "3.4": "0.9997 0.9997 0.9997 0.9997 0.9997 0.9997 0.9997 0.9997 0.9997 0.9998",
    "3.5": "0.9998 0.9998 0.9998 0.9998 0.9998 0.9998 0.9998 0.9998 0.9998 0.9998",
    "3.6": "0.9998 0.9998 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999",
    "3.7": "0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999",
    "3.8": "0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999",
    "3.9": "1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000",
}

NUM = r"(-?\d+(?:\.\d+)?)"
fails = 0
checked = 0


def fail(msg):
    global fails
    fails += 1
    print("FAIL " + msg)


def ok(msg):
    global checked
    checked += 1
    print("OK   " + msg)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def Phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def q4(x):
    return D(repr(x)).quantize(D("0.0001"), ROUND_HALF_UP)


def T(z):
    """Table look-up as the textbook does it: z to 2 d.p., Phi(z) to 4 d.p., symmetry for z < 0."""
    z = D(str(z)).quantize(D("0.01"), ROUND_HALF_UP)
    if z < 0:
        return 1 - T(-z)
    return q4(Phi(float(z)))


def rnd(x, places):
    return D(str(x)).quantize(D(1).scaleb(-places), ROUND_HALF_UP)


def check(label, block, template, expected):
    """template: literal text with '@' for each number; must match exactly once; numbers compared in order."""
    rx = re.compile("".join(NUM if ch == "@" else re.escape(ch) for ch in template))
    found = rx.findall(block)
    if len(found) != 1:
        fail(f"{label}: template matched {len(found)} times: {template}")
        return
    got = found[0] if isinstance(found[0], tuple) else (found[0],)
    if len(got) != len(expected):
        fail(f"{label}: {len(got)} numbers in template, {len(expected)} expected")
        return
    for i, (g, e) in enumerate(zip(got, expected)):
        if D(g) == D(str(e)):
            ok(f"{label} [{i + 1}] {g}")
        else:
            fail(f"{label} [{i + 1}]: printed {g}, recomputed {e}")


def same(label, a, b):
    if D(str(a)) == D(str(b)):
        ok(f"{label}: {a}")
    else:
        fail(f"{label}: {a} != {b}")


def one(rx, text, label, flags=re.S):
    m = re.findall(rx, text, flags)
    if len(m) != 1:
        fail(f"{label}: found {len(m)} times")
        print(f"\n{checked} checks passed, {fails} failures")
        sys.exit(1)
    return m[0]


rev = read("revision.html")
arev = read("a_rev.html")

# ======================= 1. the standard normal table =======================
tab = one(r'<table class="snt">(.*?)</table>', rev, "standard normal table")
head = re.findall(r"<th>\+\.(\d\d)</th>", tab)
if head == [f"{c:02d}" for c in range(10)]:
    ok("table header +.00 .. +.09 (second decimal place)")
else:
    fail(f"table header columns {head}")
if "second decimal place" in tab:
    ok("table header 'second decimal place'")
else:
    fail("table header text missing")
rows = re.findall(r'<tr(?: class="gap")?><td class="z">(\d\.\d)</td>((?:<td>\d\.\d{4}</td>){10})</tr>', tab)
if [r for r, _ in rows] != [f"{k / 10:.1f}" for k in range(40)]:
    fail(f"table rows are not z = 0.0 .. 3.9 in order: {[r for r, _ in rows]}")
if len(re.findall(r"<tr", tab)) != 42:
    fail("table has rows that are not header or data rows")
n_erf = n_book = 0
for r, cells in rows:
    vals = re.findall(r"<td>(\d\.\d{4})</td>", cells)
    book = BOOK[r].split()
    for c, v in enumerate(vals):
        z = D(r) + D(c) / 100
        e = q4(Phi(float(z)))
        if D(v) == e:
            n_erf += 1
        else:
            fail(f"table z={z}: printed {v}, erf gives {e}")
        if v == book[c]:
            n_book += 1
        else:
            fail(f"table z={z}: printed {v}, textbook prints {book[c]}")
same("table values agreeing with erf (of 400)", n_erf, 400)
same("table values agreeing with the textbook table (of 400)", n_book, 400)
for r in BOOK:                                     # the transcription itself agrees with erf
    for c, v in enumerate(BOOK[r].split()):
        if q4(Phi(float(D(r) + D(c) / 100))) != D(v):
            fail(f"textbook value z={r}+.0{c} {v} differs from erf")
ok("all 400 textbook table values agree with erf to 4 d.p.")

# ======================= 2. summary boxes and textbook examples =======================


def box(title):
    return one(r'<div class="bt">' + re.escape(title) + r'</div>(.*?)</div>\n\n', rev, f"box '{title}'")


def example(n):
    return one(r'<span class="ex-title">Textbook Example ' + str(n) + r' \(16[DEF]\)</span>(.*?)</div></div>\n\n', rev, f"Example {n}")


b1 = box("The standard normal distribution (16D)")
check("box1 1/sqrt(2pi)", b1, r"\dfrac{1}{\sqrt{2\pi}}\doteq@", [rnd(1 / sqrt(2 * 3.141592653589793), 1)])
check("box1 Phi(1.63) look-up", b1, r"\(\Phi(1.63)\) is in row 1.6, column \(+.03\), so \(\Phi(1.63)\doteq@\)", [T(1.63)])

b2 = box("The empirical rule, and reading the table in reverse (16D)")
k1, k2, k3 = (q4(2 * Phi(k) - 1) for k in (1, 2, 3))
check("box2 empirical", b2, r"\(P(-1\le Z\le1)\doteq@\doteq@\%\), \(P(-2\le Z\le2)\doteq@\doteq@\%\) and \(P(-3\le Z\le3)\doteq@\doteq@\%\)",
      [k1, rnd(100 * k1, 0), k2, rnd(100 * k2, 0), k3, rnd(100 * k3, 1)])
check("box2 symmetry use", b2, r"\(P(Z\gt1)\doteq\tfrac12(100\%-68\%)=@\%\) and \(P(0\le Z\le2)\doteq\tfrac12\times95\%=@\%\)",
      [(100 - 68) / D(2), D(95) / 2])
q3 = 0.0
lo, hi = 0.0, 2.0
for _ in range(80):                                # bisection for the upper quartile of Z
    q3 = (lo + hi) / 2
    lo, hi = (q3, hi) if Phi(q3) < 0.75 else (lo, q3)
check("box2 quartiles", b2, r"\(Q_1\doteq@\) and \(Q_3\doteq@\), and \(\text{IQR}\doteq@\)",
      [rnd(-q3, 2), rnd(q3, 2), rnd(2 * q3, 2)])
check("box2 IQR criterion", b2, r"outside \(@\le z\le@\)", [-rnd(q3 + 1.5 * 2 * q3, 2), rnd(q3 + 1.5 * 2 * q3, 2)])

e10 = example(10)
t2 = T(2)
check("Ex10 a", e10, r"\(P(Z\le2)=\Phi(2)=@.\)", [t2])
check("Ex10 b i", e10, r"\(\ \doteq1-@\ \doteq@.\)", [t2, 1 - t2])
check("Ex10 b ii", e10, r"\(\ \doteq@\), from part i.", [1 - t2])
check("Ex10 b iii", e10, r"\(\doteq@-@\)</span>, because exactly half the scores are below the mean, \(\ \doteq@.\)", [t2, T(0), t2 - T(0)])
check("Ex10 b iv", e10, r"\(P(-2\le Z\le2)=\Phi(2)-\Phi(-2)\ \doteq@-@\), by part ii, \(\ \doteq@\)", [t2, T(-2), t2 - T(-2)])
check("Ex10 b iv OR", e10, r"\(\ \doteq2\times@\), by part iii, \(\ \doteq@.\)", [t2 - T(0), 2 * (t2 - T(0))])

e13 = example(13)
a1, a2 = T(1.2), T(1.3)
dec9 = D("1.2") + D("0.1") * (D("0.9") - a1) / (a2 - a1)
check("Ex13 a", e13, r"\(\Phi(1.2)\doteq@\) and \(\Phi(1.3)\doteq@\), with difference \(@\) making the 9th decile about \(@\)",
      [a1, a2, a2 - a1, rnd(dec9, 2)])
b1v, b2v = T(0.6), T(0.7)
q3i = D("0.6") + D("0.1") * (D("0.75") - b1v) / (b2v - b1v)
check("Ex13 b", e13, r"\(\Phi(0.6)\doteq@\) and \(\Phi(0.7)\doteq@\), with difference \(@\)", [b1v, b2v, b2v - b1v])
check("Ex13 b Q3 Q1", e13, r"Thus \(Q_3\doteq@\), and because \(\phi(z)\) is even, \(Q_1\doteq@\)", [rnd(q3i, 3), -rnd(q3i, 3)])
iqr = 2 * rnd(q3i, 3)
check("Ex13 c", e13, r"the IQR is about \(@\), so \(Q_3+1.5\times\text{IQR}\doteq@\)", [rnd(iqr, 2), rnd(rnd(q3i, 3) + D("1.5") * rnd(iqr, 2), 2)])
check("Ex13 c outliers", e13, r"=2\big(1-\Phi(@)\big)\\&\doteq@,", [D("2.70"), rnd(2 * (1 - T(2.70)), 3)])
check("Ex13 c per 1000", e13, r"roughly @ in @ scores", [rnd(2 * (1 - T(2.70)) * 1000, 0), 1000])
check("Ex13 note", e13, r"five significant figures, \(Q_3\doteq@\)", [D(f"{q3:.5g}")])

e15 = example(15)
check("Ex15 a", e15, r"\(z=\dfrac{x-@}{@}\quad\text{and}\quad x=@+@z.\)", [100, 20, 100, 20])
check("Ex15 b i", e15, r"P(X\le@)\\&\quad=P(Z\le@)\\&\quad=@", [110, D(110 - 100) / 20, rnd(T(0.5), 2)])
check("Ex15 b ii", e15, r"P(X\ge@)&=P(Z\ge@)\\&=P(Z\le@)\qquad(\phi(x)\text{ is even})\\&=@", [90, D(90 - 100) / 20, D(100 - 90) / 20, rnd(T(0.5), 2)])
c1, c2 = T(2.0), T(2.1)
zc = D("2.0") + D("0.1") * (D("0.98") - c1) / (c2 - c1)
check("Ex15 c", e15, r"\(\Phi(2.0)=@\) and \(\Phi(2.1)=@\),<br>so by interpolation, \(\Phi(@)=@\)", [c1, c2, rnd(zc, 2), D("0.98")])
check("Ex15 c a", e15, r"\(a=@+@\times@=@\)", [100, 20, rnd(zc, 2), rnd(100 + 20 * rnd(zc, 2), 0)])

e17 = example(17)
check("Ex17 a i", e17, r"By the empirical rule, \(P(-1\le Z\le1)=@\%\),<br>and using the complement, \(P(Z\lt-1\text{ or }Z\gt1)=@\%\),<br>so by the even symmetry, \(P(Z\lt-1)=@\%\div2=@\%\)",
      [68, 32, 32, 16])
same("Ex17 a i z-score of 100 g", D(100 - 102) / 2, -1)
same("Ex17 a ii z-score of 105 g", D(105 - 102) / 2, D("1.5"))
check("Ex17 a ii", e17, r"\(P(Z\le1.5)=@\%\),<br>so using complements, \(P(Z\gt1.5)=@\%\)", [rnd(100 * T(1.5), 0), 100 - rnd(100 * T(1.5), 0)])
check("Ex17 b", e17, r"\(P(Z\le3.1)=@\)", [rnd(T(3.1), 3)])
check("Ex17 b sym", e17, r"\(P(Z\le-3.1)=@\)", [1 - rnd(T(3.1), 3)])
check("Ex17 b mean", e17, r"\(\mu=100+3.1\times2=@\)", [100 + D("3.1") * 2])

# ======================= 3. warm-up =======================
ans = {}
for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', arev, re.S):
    ans[an.strip()] = ab
for q in "123456":
    if q not in ans:
        fail(f"answer block {q} missing")


def qblock(n):
    return one(r'<span class="q-num">%d</span>(.*?)\{\{work' % n, rev, f"warm-up question {n}")


def parts(qb):
    return re.findall(r'<span class="pl">([a-z]+)</span>(.*?)</span>', qb, re.S)


def interval(s, var="Z"):
    """'Z\\le1.3' etc. -> (lo, hi, equal); None means infinite."""
    s = s.replace(" ", "")
    m = re.fullmatch(var + r"=" + NUM, s)
    if m:
        return D(m.group(1)), D(m.group(1)), True
    m = re.fullmatch(var + r"\\(le|lt)" + NUM, s)
    if m:
        return None, D(m.group(2)), False
    m = re.fullmatch(var + r"\\(ge|gt)" + NUM, s)
    if m:
        return D(m.group(2)), None, False
    m = re.fullmatch(NUM + r"\\(le|lt)" + var + r"\\(le|lt)" + NUM, s)
    if m:
        return D(m.group(1)), D(m.group(4)), False
    raise ValueError(s)


def prob_table(lo, hi, eq):
    if eq:
        return D(0)
    top = D(1) if hi is None else T(hi)
    bot = D(0) if lo is None else T(lo)
    return top - bot


# ---- Q1: Exercise 16D Q9 (book answers a 0.9032, b 0, c 0.3446, g 0.2119, i 0.0689, j 0.8893) ----
qb = qblock(1)
P1 = parts(qb)
book1 = ["0.9032", "0", "0.3446", "0.2119", "0.0689", "0.8893"]
iv1 = [interval(one(r"\\\(P\((.*?)\)\\\)", t, f"Q1{l} given")) for l, t in P1]
v1 = [prob_table(*iv) for iv in iv1]
for (l, _), v, bk in zip(P1, v1, book1):
    same(f"Q1{l} recomputed = textbook answer", v, bk)
b = ans["1"]
(lo, hi, _), = [iv1[0]]
check("Q1a", b, r"<b>a</b> \(P(Z\le@)=\Phi(@)\doteq@\)", [hi, hi, v1[0]])
check("Q1b", b, r"<b>b</b> \(P(Z=@)=@\)", [iv1[1][0], 0])
check("Q1c", b, r"<b>c</b> \(P(Z\gt@)=1-\Phi(@)\doteq1-@=@\)", [iv1[2][0], iv1[2][0], T(iv1[2][0]), v1[2]])
h = iv1[3][1]
check("Q1d", b, r"<b>d</b> \(P(Z\le@)=P(Z\ge@)=1-\Phi(@)\doteq1-@=@\)", [h, -h, -h, T(-h), v1[3]])
lo, hi, _ = iv1[4]
check("Q1e", b, r"<b>e</b> \(P(@\le Z\le@)=\Phi(@)-\Phi(@)\doteq@-@=@\)", [lo, hi, hi, lo, T(hi), T(lo), v1[4]])
lo, hi, _ = iv1[5]
check("Q1f", b, r"<b>f</b> \(P(@\le Z\le@)=\Phi(@)-\big(1-\Phi(@)\big)\doteq@-@=@\)", [lo, hi, hi, -lo, T(hi), 1 - T(-lo), v1[5]])

# ---- Q2: Exercise 16D Q12, empirical rule (book answers b 84%, d 16%, e 49.85%, h 2.35%, k 81.5%) ----
EMP = {1: D(68), 2: D(95), 3: D("99.7")}


def C(z):
    """Empirical-rule percentage P(Z <= z) for whole-number z (None = infinity)."""
    if z is None:
        return D(100)
    z = int(z)
    if z == 0:
        return D(50)
    half = EMP[abs(z)] / 2
    return 50 + half if z > 0 else 50 - half


qb = qblock(2)
P2 = parts(qb)
book2 = ["84", "16", "49.85", "2.35", "81.5"]
iv2 = [interval(one(r"\\\(P\((.*?)\)\\\)", t, f"Q2{l} given")) for l, t in P2]
v2 = [C(hi) - (D(0) if lo is None else C(lo)) for lo, hi, _ in iv2]
for (l, _), v, bk in zip(P2, v2, book2):
    same(f"Q2{l} recomputed = textbook answer", v, bk)
b = ans["2"]
check("Q2a", b, r"<b>a</b> \(P(Z\le1)\doteq@\%+@\%=@\%\)", [C(0), C(1) - C(0), v2[0]])
check("Q2b", b, r"<b>b</b> \(P(Z\lt-1)\doteq\tfrac12(@\%-@\%)=@\%\)", [100, EMP[1], v2[1]])
check("Q2c", b, r"<b>c</b> \(P(0\le Z\le3)\doteq\tfrac12\times@\%=@\%\)", [EMP[3], v2[2]])
check("Q2d", b, r"<b>d</b> \(P(-3\lt Z\le-2)\doteq\tfrac12(@\%-@\%)=@\%\)", [EMP[3], EMP[2], v2[3]])
check("Q2e", b, r"<b>e</b> \(P(-2\le Z\lt1)\doteq@\%+@\%=@\%\)", [EMP[2] / 2, EMP[1] / 2, v2[4]])

# ---- Q3: Exercise 16D Q14, table in reverse (book answers a 0.6, c 1.2, d -0.8, e 1.1) ----
TABLE = {D(k) / 100: T(D(k) / 100) for k in range(400)}


def inverse(p):
    zs = [z for z, v in TABLE.items() if v == p]
    if len(zs) != 1:
        fail(f"table value {p} occurs {len(zs)} times")
        return None
    return zs[0]


qb = qblock(3)
P3 = parts(qb)
g = [one(r"\\\(P\((.*?)\)=(\d\.\d{4})\\\)", t, f"Q3{l} given") for l, t in P3]
book3 = ["0.6", "1.2", "-0.8", "1.1"]
b = ans["3"]
# a: P(Z < a) = p
assert g[0][0] == r"Z\lt a"
pa = D(g[0][1]); za = inverse(pa)
check("Q3a", b, r"<b>a</b> \(\Phi(a)=@\), so \(a=@\)", [pa, za])
# b: P(Z < -a) = p, so Phi(a) = 1 - p
assert g[1][0] == r"Z\lt-a"
pb = D(g[1][1]); zb = inverse(1 - pb)
check("Q3b", b, r"<b>b</b> \(P(Z\lt-a)=1-\Phi(a)=@\), so \(\Phi(a)=@\) and \(a=@\)", [pb, 1 - pb, zb])
# c: P(Z < a) = p < 0.5, so Phi(-a) = 1 - p
assert g[2][0] == r"Z\lt a" and D(g[2][1]) < D("0.5")
pc = D(g[2][1]); zc3 = -inverse(1 - pc)
check("Q3c", b, r"\(\Phi(-a)=1-@=@\), so \(-a=@\) and \(a=@\)", [pc, 1 - pc, -zc3, zc3])
# d: P(-a <= Z < a) = p, so Phi(a) = (1 + p)/2
assert g[3][0] == r"-a\le Z\lt a"
pd = D(g[3][1]); zd = inverse((1 + pd) / 2)
check("Q3d", b, r"\(P(-a\le Z\lt a)=2\Phi(a)-1=@\), so \(\Phi(a)=@\) and \(a=@\)", [pd, (1 + pd) / 2, zd])
for l, z, bk in zip("abcd", (za, zb, zc3, zd), book3):
    same(f"Q3{l} recomputed = textbook answer", z, bk)

# ---- Q4: Exercise 16E Q6 a, c, d, f (book answers 0.9876, 0.2119, 0.9032, 0.0606) ----
qb = qblock(4)
P4 = parts(qb)
book4 = ["0.9876", "0.2119", "0.9032", "0.0606"]
b = ans["4"]
labs = "abcd"
for i, (l, t) in enumerate(P4):
    pr = one(r"\\\(P\((.*?)\)\\\)", t, f"Q4{l} given prob")
    mu = D(one(r"\\mu=" + NUM, t, f"Q4{l} mu"))
    sg = D(one(r"\\sigma=" + NUM, t, f"Q4{l} sigma"))
    lo, hi, _ = interval(pr, "X")
    zlo = None if lo is None else (lo - mu) / sg
    zhi = None if hi is None else (hi - mu) / sg
    v = prob_table(zlo, zhi, False)
    same(f"Q4{l} recomputed = textbook answer", v, book4[i])
    if l == "a":
        check("Q4a z", b, r"\(z=\dfrac{@-@}{@}=@\) and \(z=\dfrac{@-@}{@}=@\), so<br>\(P(3\le X\le7)", [lo, mu, sg, zlo, hi, mu, sg, zhi])
        check("Q4a P", b, r"=P(@\le Z\le@)=2\Phi(@)-1\doteq2\times@-1=@\)", [zlo, zhi, zhi, T(zhi), v])
    if l == "b":
        check("Q4b z", b, r"\(z=\dfrac{@-@}{@}=@\), so<br>\(P(X\le8)", [hi, mu, sg, zhi])
        check("Q4b P", b, r"=P(Z\le@)=1-\Phi(@)\doteq1-@=@\)", [zhi, -zhi, T(-zhi), v])
    if l == "c":
        check("Q4c z", b, r"\(z=\dfrac{@-@}{@}=@\), so<br>\(P(X\ge-39)", [lo, mu, sg, zlo])
        check("Q4c P", b, r"=P(Z\ge@)=\Phi(@)\doteq@\)", [zlo, -zlo, v])
    if l == "d":
        check("Q4d z", b, r"\(z=\dfrac{@-@}{@}=@\) and \(z=\dfrac{@-@}{@}=@\), so<br>\(P(3\lt X\le5)", [lo, mu, sg, zlo, hi, mu, sg, zhi])
        check("Q4d P", b, r"=P(@\lt Z\le@)=\Phi(@)-\Phi(@)\doteq@-@=@.\)", [zlo, zhi, -zlo, -zhi, T(-zlo), T(-zhi), v])

# ---- Q5: Exercise 16F Q2 (book answers 3, 50, 1630) ----
qb = qblock(5)
mu = D(one(r"with mean " + NUM, qb, "Q5 mean"))
sg = D(one(r"standard deviation " + NUM, qb, "Q5 sd"))
N = D(one(r"cohort of " + NUM, qb, "Q5 cohort"))
P5 = dict(parts(qb))
xa = D(one(r"more than " + NUM, P5["a"], "Q5a"))
xb = D(one(r"less than " + NUM, P5["b"], "Q5b"))
xc1, xc2 = (D(v) for v in one(r"between " + NUM + " and " + NUM, P5["c"], "Q5c"))
za5, zb5, zc1, zc2 = ((x - mu) / sg for x in (xa, xb, xc1, xc2))
pa5 = 100 - C(za5)
pb5 = C(zb5)
pc5 = C(zc2) - C(zc1)
b = ans["5"]
check("Q5a", b, r"\(z=\dfrac{@-@}{@}=@\). By the empirical rule, \(P(Z\gt3)\doteq\tfrac12(100\%-@\%)=@\%\), so about \(@\times@=@\)",
      [xa, mu, sg, za5, EMP[3], pa5, N, pa5 / 100, N * pa5 / 100])
check("Q5b", b, r"\(z=\dfrac{@-@}{@}=@\). \(P(Z\lt-2)\doteq\tfrac12(100\%-@\%)=@\%\), so about \(@\times@=@\)",
      [xb, mu, sg, zb5, EMP[2], pb5, N, pb5 / 100, N * pb5 / 100])
check("Q5c", b, r"\(z=\dfrac{@-@}{@}=@\) and \(z=\dfrac{@-@}{@}=@\). \(P(-1\lt Z\lt2)\doteq@\%+@\%=@\%\), so about \(@\times@=@\)",
      [xc1, mu, sg, zc1, xc2, mu, sg, zc2, C(0) - C(zc1), C(zc2) - C(0), pc5, N, pc5 / 100, N * pc5 / 100])
for l, v, bk in zip("abc", (N * pa5 / 100, N * pb5 / 100, N * pc5 / 100), ("3", "50", "1630")):
    same(f"Q5{l} recomputed = textbook answer", v, bk)

# ---- Q6: Exercise 16F Q7 (book answers b 186 cm, c ii 197 cm) ----
qb = qblock(6)
mu1 = D(one(r"with mean " + NUM + " cm", qb, "Q6 mean"))
sg1 = D(one(r"standard deviation " + NUM + " cm", qb, "Q6 sd"))
mu2, sg2 = (D(v) for v in one(r"are respectively " + NUM + " and " + NUM + " centimetres", qb, "Q6 Dinaric"))
p1 = D(one(r"so that " + NUM + r"% of this population", qb, "Q6 90%")) / 100
p2 = D(one(r"so that " + NUM + r"% of adult males", qb, "Q6 95%")) / 100
best = min(TABLE, key=lambda z: (abs(TABLE[z] - p1), z))
b = ans["6"]
check("Q6a", b, r"\(\Phi(@)\doteq@\) and \(\Phi(@)\doteq@\). The closer value to \(@\) is \(@\), so \(z\doteq@\)",
      [best, TABLE[best], best + D("0.01"), TABLE[best + D("0.01")], p1, TABLE[best], best])
h1 = mu1 + best * sg1
check("Q6b", b, r"\(x=\mu+\sigma z=@+@\times@=@\), so the doorway must be about @ cm", [mu1, best, sg1, h1, rnd(h1, 0)])
lo95 = max(z for z in TABLE if TABLE[z] < p2)
hi95 = min(z for z in TABLE if TABLE[z] > p2)
same("Q6c 0.95 lies exactly halfway between table entries", p2 - TABLE[lo95], TABLE[hi95] - p2)
mid = (lo95 + hi95) / 2
check("Q6c i", b, r"\(\Phi(@)\doteq@\) and \(\Phi(@)\doteq@\). The value \(@\) lies halfway between them, so \(z\doteq@\), and \(@\) is a reasonable estimate (@ rounds to @)",
      [lo95, TABLE[lo95], hi95, TABLE[hi95], p2, mid, rnd(mid, 2), mid, rnd(mid, 2)])
i1, i2 = T(1.6), T(1.7)
zint = D("1.6") + D("0.1") * (p2 - i1) / (i2 - i1)
check("Q6c i interp", b, r"between \(\Phi(1.6)\doteq@\) and \(\Phi(1.7)\doteq@\) also gives about \(@\)", [i1, i2, rnd(zint, 2)])
h2 = mu2 + rnd(mid, 2) * sg2
check("Q6c ii", b, r"\(x=@+@\times@=@\), so the door must be about @ cm", [mu2, rnd(mid, 2), sg2, h2, rnd(h2, 0)])
same("Q6b recomputed = textbook answer 186", rnd(h1, 0), 186)
same("Q6c ii recomputed = textbook answer 197", rnd(h2, 0), 197)

print(f"\n{checked} checks passed, {fails} failures")
sys.exit(1 if fails else 0)
