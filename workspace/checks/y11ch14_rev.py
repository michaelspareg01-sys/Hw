"""Check of the Chapter 14 revision warm-up answers, tied to the HTML.

Reads the printed values from workspace/build/y11ch14/a_rev.html (and the given
data of questions 3 and 5 from revision.html). Each template must match exactly
once in its answer block, otherwise the item FAILS. In a template '@' marks a
number or fraction (\\dfrac{a}{b}, \\dfrac ab or an integer) and '~' marks a
comma-separated list of integers. Every printed value is compared with a value
recomputed by brute-force enumeration (itertools, fractions).

Exit status is 1 if anything fails.  Run: python3 workspace/checks/y11ch14_rev.py
"""
import os
import re
import sys
from fractions import Fraction as F
from itertools import product, permutations

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH14_SRC", os.path.join(HERE, "..", "build", "y11ch14"))   # override only for mutation tests

VAL = r"(\\dfrac(?:\{\d+\}\{\d+\}|\d\d)|\d+)"
LST = r"(\d+(?:,\d+)*)"


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def to_frac(s):
    m = re.fullmatch(r"\\dfrac\{(\d+)\}\{(\d+)\}", s) or re.fullmatch(r"\\dfrac(\d)(\d)", s)
    if m:
        return F(int(m.group(1)), int(m.group(2)))
    return F(int(s))


def compile_template(t):
    out = []
    for ch in t:
        out.append(VAL if ch == "@" else LST if ch == "~" else re.escape(ch))
    return re.compile("".join(out))


def blocks(text):
    d = {}
    for an, ab in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>', text, re.S):
        d[an.strip()] = ab
    return d


fails = 0
checked = 0


def check(label, block, template, expected):
    """expected: list of Fractions / ints / sets, one per placeholder, in order."""
    global fails, checked
    rx = compile_template(template)
    found = rx.findall(block)
    if len(found) != 1:
        print(f"FAIL {label}: template matched {len(found)} times: {template}")
        fails += 1
        return
    got = found[0] if isinstance(found[0], tuple) else (found[0],)
    if len(got) != len(expected):
        print(f"FAIL {label}: template has {len(got)} placeholders, {len(expected)} expected values")
        fails += 1
        return
    for i, (g, e) in enumerate(zip(got, expected)):
        if isinstance(e, (set, frozenset)):
            ok = {int(x) for x in g.split(",")} == set(e)
            shown = g
        else:
            ok = to_frac(g) == F(e)
            shown = g
        checked += 1
        if ok:
            print(f"OK   {label} [{i + 1}] {shown}")
        else:
            print(f"FAIL {label} [{i + 1}]: printed {shown}, recomputed {e}")
            fails += 1


rev = read("revision.html")
ans = blocks(read("a_rev.html"))
for q in "12345":
    if q not in ans:
        print(f"FAIL: answer block {q} missing")
        fails += 1
if fails:
    sys.exit(1)


def prob(event, space):
    return F(sum(1 for x in space if event(x)), len(space))


# ---- Q1: die, E = even or multiple of 3 ----
S = list(range(1, 7))
E = {x for x in S if x % 2 == 0 or x % 3 == 0}
notE = set(S) - E
pE = F(len(E), len(S))
b = ans["1"]
check("Q1a", b, r"\(S=\{~\}\) and \(E=\{~\}\)", [set(S), E])
check("Q1b", b, r"\(P(E)=@=@\)", [pE, pE])
check("Q1c", b, r"The complement is \(\{~\}\), so \(P(\overline E)=1-@=@\)", [notE, pE, 1 - pE])

# ---- Q2: cards ----
deck = list(product(range(1, 14), "CDHS"))        # rank 1..13 (11, 12, 13 are J, Q, K), suit
court = lambda c: c[0] >= 11
red = lambda c: c[1] in "DH"
king = lambda c: c[0] == 13
assert len(deck) == 52
p_heart = prob(lambda c: c[1] == "H", deck)
p_court = prob(court, deck)
p_notcourt = prob(lambda c: not court(c), deck)
p_redking = prob(lambda c: red(c) or king(c), deck)
n_red = sum(1 for c in deck if red(c))
n_king = sum(1 for c in deck if king(c))
n_redking = sum(1 for c in deck if red(c) and king(c))
b = ans["2"]
check("Q2a", b, r"<b>a</b> \(@=@\) &nbsp; <b>b</b>", [p_heart, p_heart])
check("Q2b", b, r"<b>b</b> \(@=@\) &nbsp; <b>c</b>", [p_court, p_court])
check("Q2c", b, r"<b>c</b> \(1-@=@\) &nbsp; <b>d</b>", [p_court, p_notcourt])
check("Q2d counts", b, r"There are @ red cards and @ kings, and the @ red kings", [n_red, n_king, n_redking])
check("Q2d", b, r"\(P=\dfrac{@+@-@}{52}=@=@\)", [n_red, n_king, n_redking, p_redking, p_redking])

# ---- Q3: class, soccer / tennis (givens read from revision.html) ----
m = re.findall(r"In a class of (\d+) students, (\d+) play soccer, (\d+) play tennis and (\d+) play both sports", rev)
if len(m) != 1:
    print("FAIL Q3 givens: not found exactly once in revision.html")
    sys.exit(1)
N, a, t, both = map(int, m[0])
soccer = set(range(0, a))
tennis = set(range(a - both, a - both + t))
assert len(soccer & tennis) == both and len(soccer | tennis) <= N
students = range(N)
n_union = sum(1 for s in students if s in soccer or s in tennis)
n_neither = N - n_union
n_soc_only = len(soccer - tennis)
n_ten_only = len(tennis - soccer)
n_exactly_one = sum(1 for s in students if (s in soccer) != (s in tennis))
b = ans["3"]
check("Q3a", b, r"\(@+@-@=@\), so \(@\) play neither and \(P=\dfrac{@}{@}=@\)",
      [a, t, both, n_union, n_neither, n_neither, N, F(n_neither, N)])
check("Q3b", b, r"Soccer only is \(@-@=@\) and tennis only is \(@-@=@\), so \(P=\dfrac{@+@}{@}=@\)",
      [a, both, n_soc_only, t, both, n_ten_only, n_soc_only, n_ten_only, N, F(n_exactly_one, N)])

# ---- Q4: four coin tosses ----
space = list(product("HT", repeat=4))
b = ans["4"]
check("Q4a", b, r"\(2\times2\times2\times2=@\) outcomes", [len(space)])
check("Q4b", b, r"\(P(\text{first two heads})=@\times@=@\)",
      [F(1, 2), F(1, 2), prob(lambda o: o[0] == "H" and o[1] == "H", space)])
check("Q4c", b, r"1-P(\text{no tails})=1-@=@\)",
      [prob(lambda o: "T" not in o, space), prob(lambda o: "T" in o, space)])

# ---- Q5: bag, two discs without replacement (givens read from revision.html) ----
m = re.findall(r"A bag holds (\d+) red and (\d+) blue discs", rev)
if len(m) != 1:
    print("FAIL Q5 givens: not found exactly once in revision.html")
    sys.exit(1)
nr, nb = map(int, m[0])
discs = ["R"] * nr + ["B"] * nb
pairs = list(permutations(range(len(discs)), 2))        # ordered draws without replacement
col = lambda p: (discs[p[0]], discs[p[1]])
p_rr = prob(lambda p: col(p) == ("R", "R"), pairs)
p_diff = prob(lambda p: col(p)[0] != col(p)[1], pairs)
p_atleast_b = prob(lambda p: "B" in col(p), pairs)
p_first_r = prob(lambda p: discs[p[0]] == "R", pairs)
p_first_b = prob(lambda p: discs[p[0]] == "B", pairs)
p_second_r_given_r = F(nr - 1, len(discs) - 1)
p_second_b_given_r = F(nb, len(discs) - 1)
p_second_r_given_b = F(nr, len(discs) - 1)
n_pairs = len(pairs)
b = ans["5"]
check("Q5a", b, r"<b>a</b> \(@\times@=@=@\)", [p_first_r, p_second_r_given_r,
      F(sum(1 for p in pairs if col(p) == ("R", "R")), n_pairs), p_rr])
check("Q5b", b, r"<b>b</b> \(P(RB)+P(BR)=@\times@+@\times@=@=@\)",
      [p_first_r, p_second_b_given_r, p_first_b, p_second_r_given_b,
       F(sum(1 for p in pairs if col(p)[0] != col(p)[1]), n_pairs), p_diff])
check("Q5c", b, r"<b>c</b> \(1-P(\text{both red})=1-@=@\)", [p_rr, p_atleast_b])

print(f"\n{checked} printed values checked, {fails} failures")
sys.exit(1 if fails else 0)
