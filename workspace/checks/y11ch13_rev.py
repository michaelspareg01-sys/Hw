"""Check of the Chapter 13 revision warm-up answers, tied to the HTML.

Reads the printed values from workspace/build/y11ch13/a_rev.html and the given data of each
question from revision.html (the frequency table of Q4, the word of Q1/Q2/Q3 conditions, the
sums of Q5).  Every template ('@' = an integer or a decimal) must match exactly once in its
answer block, otherwise the item FAILS.  Probabilities are recomputed by enumerating the
sample space (cards, coin sequences, ordered draws) with fractions.Fraction; the mean and
standard deviation of Q4 are recomputed from the table printed in revision.html.

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch13_rev.py
"""
import os
import re
import sys
from fractions import Fraction as F
from itertools import product, permutations
from math import sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH13_SRC", os.path.join(HERE, "..", "build", "y11ch13"))   # override only for mutation tests

NUM = r"(\d+(?:\.\d+)?)"


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def blocks(text):
    d = {}
    for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S):
        d[an.strip()] = ab
    return d


fails = 0
checked = 0


def fail(msg):
    global fails
    print("FAIL " + msg)
    fails += 1


def ok(msg):
    global checked
    checked += 1
    print("OK   " + msg)


def check(label, block, template, expected):
    """Template with '@' for each number; must match exactly once; values compared in order (as Fractions)."""
    parts = template.split("{@}")                  # a braced number may be printed with or without braces: \dfrac3{13}
    rx = re.compile(r"\{?" + NUM + r"\}?").pattern.join(
        "".join(NUM if ch == "@" else re.escape(ch) for ch in p) for p in parts)
    rx = re.compile(rx)
    found = rx.findall(block)
    if len(found) != 1:
        fail(f"{label}: template matched {len(found)} times: {template}")
        return
    got = found[0] if isinstance(found[0], tuple) else (found[0],)
    if len(got) != len(expected):
        fail(f"{label}: {len(got)} placeholders, {len(expected)} expected values")
        return
    for i, (g, e) in enumerate(zip(got, expected)):
        if F(g) == F(e):
            ok(f"{label} [{i + 1}] {g}")
        else:
            fail(f"{label} [{i + 1}]: printed {g}, recomputed {e}")


def qblock(rev, num):
    m = re.findall(r'<span class="q-num">%d</span>(.*?)\{\{work' % num, rev, re.S)
    if len(m) != 1:
        fail(f"revision.html question {num} not found exactly once")
        sys.exit(1)
    return m[0]


def part(qb, letter):
    m = re.findall(r'<span class="pl">%s</span>(.*?)</span>' % letter, qb, re.S)
    if len(m) != 1:
        fail(f"given part {letter} not found exactly once")
        sys.exit(1)
    return m[0]


def need(label, text, pattern):
    """Given data must be exactly what the check assumes (one match)."""
    m = re.findall(pattern, text, re.S)
    if len(m) != 1:
        fail(f"{label}: given text does not match {pattern!r}")
        sys.exit(1)
    return m[0]


rev = read("revision.html")
ans = blocks(read("a_rev.html"))
for q in "12345":
    if q not in ans:
        fail(f"answer block {q} missing")
if fails:
    sys.exit(1)

# ---------------- Q1: a card from a pack of 52 ----------------
q1 = qblock(rev, 1)
b = ans["1"]
need("Q1 stem", q1, r"pack of (52) playing cards \(the (12) jacks, queens and kings are the court cards\)")
need("Q1a", part(q1, "a"), r"a court card,")
need("Q1b", part(q1, "b"), r"not a court card,")
need("Q1c", part(q1, "c"), r"a heart or a king\.")
deck = list(product(["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"], ["hearts", "diamonds", "clubs", "spades"]))
N = len(deck)
assert N == 52
court = [c for c in deck if c[0] in "JQK"]
notcourt = [c for c in deck if c[0] not in "JQK"]
hearts = [c for c in deck if c[1] == "hearts"]
kings = [c for c in deck if c[0] == "K"]
hk = [c for c in deck if c[1] == "hearts" or c[0] == "K"]
both = [c for c in hearts if c in kings]
p_court = F(len(court), N)
p_not = F(len(notcourt), N)
p_hk = F(len(hk), N)
assert p_not == 1 - p_court
check("Q1a count", b, r"There are @ court cards", [len(court)])
check("Q1a", b, r"\(P(\text{court card})=\dfrac{@}{@}=\dfrac{@}{@}\)", [len(court), N, p_court.numerator, p_court.denominator])
check("Q1b", b, r"\(P(\text{not a court card})=1-\dfrac{@}{@}=\dfrac{@}{@}\)", [p_court.numerator, p_court.denominator, p_not.numerator, p_not.denominator])
check("Q1c counts", b, r"There are @ hearts and @ kings", [len(hearts), len(kings)])
check("Q1c", b, r"\(P(\text{heart or king})=\dfrac{@}{@}+\dfrac{@}{@}-\dfrac{@}{@}=\dfrac{@}{@}=\dfrac{@}{@}\)",
      [len(hearts), N, len(kings), N, len(both), N, len(hk), N, p_hk.numerator, p_hk.denominator])

# ---------------- Q2: a coin tossed three times ----------------
q2 = qblock(rev, 2)
b = ans["2"]
need("Q2 stem", q2, r"A coin is tossed (three) times")
need("Q2a", part(q2, "a"), r"all three tosses are heads,")
need("Q2b", part(q2, "b"), r"there is at least one head,")
need("Q2c", part(q2, "c"), r"there are exactly two heads\.")
seqs = list(product("HT", repeat=3))
p_hhh = F(sum(1 for s in seqs if s.count("H") == 3), len(seqs))
p_alo = F(sum(1 for s in seqs if s.count("H") >= 1), len(seqs))
two = ["".join(s) for s in seqs if s.count("H") == 2]
p_two = F(len(two), len(seqs))
check("Q2a", b, r"\(P(HHH)=\dfrac{@}{@}\times\dfrac{@}{@}\times\dfrac{@}{@}=\dfrac{@}{@}\)", [1, 2, 1, 2, 1, 2, p_hhh.numerator, p_hhh.denominator])
check("Q2b", b, r"\(P(\text{at least one head})=1-P(TTT)=1-\dfrac{@}{@}=\dfrac{@}{@}\)", [p_hhh.numerator, p_hhh.denominator, p_alo.numerator, p_alo.denominator])
listed = re.findall(r"\\\(([HT]{3})\\\)", need("Q2c text", b, r"<b>c</b>(.*?)each with"))
if sorted(listed) != sorted(two):
    fail(f"Q2c listed outcomes {listed}, enumeration gives {sorted(two)}")
else:
    ok(f"Q2c listed outcomes {listed}")
check("Q2c", b, r"each with probability \(\dfrac{@}{@}\). So \(P(\text{exactly two heads})=\dfrac{@}{@}\)", [1, len(seqs), p_two.numerator, p_two.denominator])

# ---------------- Q3: two marbles, with and without replacement ----------------
q3 = qblock(rev, 3)
b = ans["3"]
need("Q3 stem", q3, r"bag of (three) red and (two) blue marbles")
need("Q3a", part(q3, "a"), r"replaced before the second is drawn,")
need("Q3b", part(q3, "b"), r"not replaced\.")
bag = ["R"] * 3 + ["B"] * 2
with_rep = list(product(range(5), repeat=2))
without = list(permutations(range(5), 2))
pa = F(sum(1 for i, j in with_rep if bag[i] == "R" and bag[j] == "R"), len(with_rep))
pb = F(sum(1 for i, j in without if bag[i] == "R" and bag[j] == "R"), len(without))
check("Q3a", b, r"independent: \(P(RR)=\dfrac{@}{@}\times\dfrac{@}{@}=\dfrac{@}{@}\)", [3, 5, 3, 5, pa.numerator, pa.denominator])
check("Q3b", b, r"there are @ red in @: \(P(RR)=\dfrac{@}{@}\times\dfrac{@}{@}=\dfrac{@}{@}\)", [2, 4, 3, 5, 2, 4, pb.numerator, pb.denominator])

# ---------------- Q4: frequency table (read from revision.html) ----------------
q4 = qblock(rev, 4)
b = ans["4"]
xs = [int(v) for v in re.findall(r"<td>(\d+)</td>", need("Q4 x row", q4, r"<th>\\\(x\\\)</th>((?:<td>\d+</td>)+)</tr>"))]
fs = [int(v) for v in re.findall(r"<td>(\d+)</td>", need("Q4 f row", q4, r"<th>\\\(f\\\)</th>((?:<td>\d+</td>)+)</tr>"))]
need("Q4 stem", q4, r"spun (50) times")
need("Q4a", part(q4, "a"), r"Find the relative frequency")
need("Q4b", part(q4, "b"), r"Find the mean")
need("Q4c", part(q4, "c"), r"standard deviation")
n = sum(fs)
assert n == 50 and len(xs) == len(fs) == 4
fr = [F(f, n) for f in fs]
assert sum(fr) == 1
mean = sum(x * r for x, r in zip(xs, fr))
ex2 = sum(x * x * r for x, r in zip(xs, fr))
var = ex2 - mean ** 2
assert var == sum(r * (x - mean) ** 2 for x, r in zip(xs, fr))      # second route: mean of squared deviations
sd = sqrt(var)
fl = lambda v: v                                  # keep exact Fractions for the comparison
check("Q4a", b, r"\(f_r=\dfrac f{@}\): \(@,\ @,\ @,\ @\). Check: \(@+@+@+@=@\)", [n] + [fl(r) for r in fr] * 2 + [1])
check("Q4b", b, r"\(\bar x=\sum x\,f_r=1(@)+2(@)+3(@)+4(@)=@+@+@+@=@\)",
      [fl(r) for r in fr] + [fl(x * r) for x, r in zip(xs, fr)] + [fl(mean)])
check("Q4c", b, r"\(\sum x^2f_r=1(@)+4(@)+9(@)+16(@)=@+@+@+@=@\), so \(\sigma^2=@-@^2=@-@=@\) and \(\sigma=\sqrt{@}=@\)",
      [fl(r) for r in fr] + [fl(x * x * r) for x, r in zip(xs, fr)] + [fl(ex2), fl(ex2), fl(mean), fl(ex2), fl(mean ** 2), fl(var), fl(var), F(round(sd, 9)).limit_denominator(10**6)])
assert abs(sd - 0.96) < 1e-12 and F(96, 100) ** 2 == var   # the printed sd is exact: 0.96^2 = 0.9216

# ---------------- Q5: sigma notation ----------------
q5 = qblock(rev, 5)
b = ans["5"]
terms = [int(t) for t in need("Q5a", part(q5, "a"), r"Write \\\(((?:\d+\+)+\d+)\\\) in sigma notation").split("+")]
need("Q5b given", part(q5, "b"), r"Given \\\(\\sum p\(x\)=1\\\) and \\\(\\sum x\\,p\(x\)=2\\\), find \\\(\\sum\(3x\+1\)\\,p\(x\)\\\)\.")
m = re.findall(r"=\\displaystyle\\sum_\{k=1\}\^\{(\d+)\}(\d+)k=", b)
if len(m) != 1:
    fail("Q5a sigma form not matched exactly once")
else:
    top, c = int(m[0][0]), int(m[0][1])
    if [c * k for k in range(1, top + 1)] == terms:
        ok(f"Q5a printed sigma form reproduces the terms {terms}")
    else:
        fail(f"Q5a printed sigma form gives {[c * k for k in range(1, top + 1)]}, given {terms}")
    check("Q5a value", b, r"=@(@+@+@+@)=@", [c] + list(range(1, top + 1)) + [sum(terms)])
# (b): every distribution with sum p = 1 and sum x p = 2 gives sum (3x+1) p = 7; test several exact ones
tests = [([1, 2, 3], [F(1, 4), F(1, 2), F(1, 4)]), ([0, 2, 4], [F(1, 3)] * 3),
         ([1, 3], [F(1, 2), F(1, 2)]), ([0, 1, 2, 3, 4], [F(1, 16), F(4, 16), F(6, 16), F(4, 16), F(1, 16)])]
vals = set()
for xs5, ps in tests:
    assert sum(ps) == 1 and sum(x * p for x, p in zip(xs5, ps)) == 2
    vals.add(sum((3 * x + 1) * p for x, p in zip(xs5, ps)))
assert len(vals) == 1
val = vals.pop()
check("Q5b", b, r"=3(@)+@=@", [2, 1, val])

print(f"\n{checked} printed values checked, {fails} failures")
sys.exit(1 if fails else 0)
