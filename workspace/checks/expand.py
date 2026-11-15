"""Independent check for the expansion homework: parse every printed question and answer from the HTML,
expand the question with sympy, and compare. Also checks the printed working line equals the question.
Exit 1 on any failure."""
import re, sys, html
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
D = sys.argv[1] if len(sys.argv) > 1 else "/home/user/Hw/workspace/build/expand/"
K = int(sys.argv[2]) if len(sys.argv) > 2 else 8   # numeric questions per type
T = standard_transformations + (implicit_multiplication_application,)
x, y, a, b = sp.symbols('x y a b')
L = {'x': x, 'y': y, 'a': a, 'b': b}
def P(s):
    s = s.replace("^", "**").replace(")(", ")*(")
    return parse_expr(s, local_dict=L, transformations=T)
fails, n = [], 0
def ok(c, m):
    global n; n += 1
    if not c: fails.append(m)
A = open(D + "a_all.html").read()
Q = open(D + "q_all.html").read()
items = re.findall(r'<b>(\w)</b> \\\((.*?)=(.*?)=\\\) <span data-k="(T\d[a-h])" data-q="([^"]+)">\\\((.*?)\\\)</span>', A)
lets = re.findall(r'(?:<b>c</b> |<div class="ab">)\\\(([^<]*?)=([^<]*?)=\\\) <span data-k="(T\dL)" data-q="([^"]+)">\\\((.*?)\\\)</span>', A)
ok(len(items) == 8*K, f"{8*K} numeric answers found ({len(items)})")
ok(len(lets) == 8, f"8 letter answers found ({len(lets)})")
qs = re.findall(r'<span class="pl">(\w)</span>\\\((.*?)\\\)</div>', Q)
ok(len(qs) == 8*K, f"{8*K} numeric questions found ({len(qs)})")
for (lab, qt, work, key, dq, ans), (ql, qq) in zip(items, qs):
    ok(lab == ql and qt == qq == dq, f"{key}: question text matches between booklets ({qq} / {qt})")
    e = sp.expand(P(qt))
    ok(sp.expand(P(work)) == e, f"{key}: working line {work} equals {qt}")
    ok(sp.expand(P(ans)) == e, f"{key}: answer {ans} equals expansion of {qt}")
    # simplified: number of terms equals number of distinct monomials
    ok(len(sp.Add.make_args(P(ans))) == len(sp.Add.make_args(e)), f"{key}: answer fully collected ({ans})")
    ok("1x" not in ans.replace("+1x", "X") or True, "")
    ok(not re.search(r'(?<![0-9])1[xy]', ans), f"{key}: no coefficient 1 written ({ans})")
for qt, work, key, dq, ans in lets:
    e = sp.expand(P(qt))
    ok(sp.expand(P(work)) == e, f"{key}: working line {work}")
    ok(sp.expand(P(ans)) == e, f"{key}: letter answer {ans}")
# the letter question printed in each section matches its type heading
heads = re.findall(r'<span class="tform">\\\((.*?)\\\)</span>', Q)
lq = re.findall(r'Expand and simplify \\\((.*?)\\\), where', Q) or re.findall(r'<span class="pl">c</span>\\\((.*?)\\\) <span class="lw">', Q)
ok(heads == lq and len(heads) == 8, "letter questions match the type headings")
# each numeric question has the shape of its type
shape = {"(x+a)(x+b)": r"\(x\+\d+\)\(x\+\d+\)", "(x+a)(x-b)": r"\(x\+\d+\)\(x-\d+\)", "(x-a)(x+b)": r"\(x-\d+\)\(x\+\d+\)",
         "(x-a)(x-b)": r"\(x-\d+\)\(x-\d+\)", "(x+y+a)(x+b)": r"\(x\+y\+\d+\)\(x\+\d+\)", "(x+a)(x+y+b)": r"\(x\+\d+\)\(x\+y\+\d+\)",
         "(x-a)(x+a)": r"\(x-(\d+)\)\(x\+\1\)", "(x-a)^2": r"\(x-\d+\)\^2"}
for i, h in enumerate(heads):
    for lab, qq in qs[K*i:K*i+K]:
        ok(re.fullmatch(shape[h], qq) is not None, f"type {i+1} {lab}: {qq} has the form {h}")
    nums = [tuple(map(int, re.findall(r"\d+", qq.replace("^2", "")))) for _, qq in qs[K*i:K*i+K]]
    ok(len(set(nums)) == K, f"type {i+1}: {K} different questions")
    if h in ("(x+a)(x-b)", "(x-a)(x+b)"):
        ok(all(t[0] != t[1] for t in nums), f"type {i+1}: a and b differ (else it is a difference of squares)")
print(f"{n - len(fails)} OK, {len(fails)} FAIL")
for f in fails: print("  FAIL", f)
sys.exit(1 if fails else 0)
