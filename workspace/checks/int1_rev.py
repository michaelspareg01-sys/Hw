r"""Check of the Integration Part 1 Revision section, tied to the HTML.

Reads workspace/build/int1/revision.html and a_rev.html. Every printed expression is converted from its
TeX source to sympy (a small converter below: \frac, \sqrt, \sqrt[n], ^, \times, \div, mixed-number indices
such as x^{-1\frac12}) and compared, numerically at three points and by simplify, with an independent result:
  1. Summary boxes: every equation in every box is classified. Identities are checked as chains (each
     member equal to the first); the two derivative examples and the (ax+b)^n formula are differentiated by
     sympy; the sigma example is summed by sympy. An unclassified equation is a FAIL.
  2. Worked examples (Year 11 Examples 5, 10, 17, 21, 23, 24, 25; Year 12 Example 21; the area example):
     every line of every chain is compared with the question's expression (for y = / f(x) = lines), with
     sympy's derivative of it (for dy/dx = / f'(x) = lines), with u, y(u), du/dx, dy/du for the chain rule,
     with sympy sums for sigma, and with the area formulae evaluated at the question's values.
  3. Warm-up (five questions): the givens are read from revision.html and also compared with the textbook questions
     (transcribed below); every member of every printed chain in a_rev.html is checked as in 2, and each
     final answer is compared with the textbook's printed answer (Y11 Advanced PDF 552-553, 559-560;
     Y12 Ext 1 PDF 853), transcribed below.
Every block must be found exactly once and every part must be present, otherwise the item FAILS.
Exit status 1 if anything fails.  Run: python3 workspace/checks/int1_rev.py
"""
import os
import sys
import re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import sympy as sp

x, a, b, n, u, h, r, m, l = sp.symbols("x a b n u h r m l", positive=True)
NS = {"x": x, "a": a, "b": b, "n": n, "u": u, "h": h, "r": r, "m": m, "l": l, "sqrt": sp.sqrt, "pi": sp.pi}
TR = standard_transformations + (implicit_multiplication_application,)


def _arg(s, i):
    """Return (argument text, next index) for a TeX macro argument at s[i]: {group} or one character."""
    while i < len(s) and s[i] == " ":
        i += 1
    if s[i] == "{":
        depth, j = 0, i
        while True:
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    return s[i + 1:j], j + 1
            j += 1
    if s[i] == "\\":
        mt = re.match(r"\\[a-zA-Z]+", s[i:])
        return mt.group(0), i + len(mt.group(0))
    return s[i], i + 1


def conv(s):
    out, i = [], 0
    while i < len(s):
        if s.startswith("\\frac", i):
            A, i = _arg(s, i + 5)
            B, i = _arg(s, i)
            out.append(f"(({conv(A)})/({conv(B)}))")
        elif s.startswith("\\sqrt", i):
            i += 5
            if s[i] == "[":
                j = s.index("]", i)
                k = s[i + 1:j]
                A, i = _arg(s, j + 1)
                out.append(f"(({conv(A)})**(1/({k})))")
            else:
                A, i = _arg(s, i)
                out.append(f" sqrt({conv(A)}) ")
        elif s.startswith("\\pi", i):
            out.append(" pi "); i += 3
        elif s[i] == "^":
            A, i = _arg(s, i + 1)
            out.append(f"**({conv(A)})")
        elif s[i] == "{":
            A, i = _arg(s, i)
            out.append(f"({conv(A)})")
        elif s[i] == "\\":
            mt = re.match(r"\\[a-zA-Z]+", s[i:])
            raise ValueError(f"unknown macro {mt.group(0) if mt else s[i:i+5]} in {s!r}")
        else:
            out.append(s[i]); i += 1
    return "".join(out)


def clean(s):
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    for t in ("\\displaystyle", "\\left", "\\right", "\\Big", "\\big", "\\,", "\\ ", "&"):
        s = s.replace(t, "")
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\cdots", "...")
    s = re.sub(r"\\text\{\s*cm\}\^2", "", s)
    s = re.sub(r"(\d+)\\frac(\d)(\d)", r"(\1+\2/\3)", s)            # mixed numbers such as 1\frac12
    s = re.sub(r"(\d+)\\frac\{(\d+)\}\{(\d+)\}", r"(\1+\2/\3)", s)
    return s.strip().rstrip(".,")


def top_split(s, sep):
    parts, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        if depth == 0 and s.startswith(sep, i):
            parts.append(cur); cur = ""; i += len(sep); continue
        cur += c; i += 1
    parts.append(cur)
    return parts


def S(tex):
    t = clean(tex)
    if "\\div" in t:
        L, R = top_split(t, "\\div")
        return S(L) / S(R)
    return parse_expr(conv(t), local_dict=NS, transformations=TR)


PTS = [{x: sp.Rational(37, 100), a: sp.Rational(13, 10), b: sp.Rational(27, 10), n: sp.Rational(17, 10), u: sp.Rational(9, 10), m: sp.Rational(23, 10), h: 3, r: 2, l: 5},
       {x: sp.Rational(29, 10), a: sp.Rational(7, 10), b: sp.Rational(11, 10), n: 3, u: sp.Rational(21, 10), m: sp.Rational(1, 3), h: 1, r: 4, l: 2},
       {x: sp.Rational(5, 4), a: 4, b: sp.Rational(1, 2), n: sp.Rational(1, 2), u: 3, m: 2, h: 7, r: 1, l: 3}]


def equal(e1, e2):
    if sp.simplify(e1 - e2) == 0:
        return True
    try:
        return all(abs(complex(sp.N((e1 - e2).subs(p), 30))) < 1e-20 for p in PTS)
    except TypeError:
        return False


# =============================== harness ===============================
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))   # override only for mutation tests
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


def one(rx, text, label, flags=re.S):
    found = re.findall(rx, text, flags)
    if len(found) != 1:
        fail(f"{label}: found {len(found)} times")
        print(f"\n{checked} checks passed, {fails} failures")
        sys.exit(1)
    return found[0]


def maths(block):
    return [p or q for p, q in re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", block, re.S)]


def same(label, tex, target):
    try:
        e = S(tex)
    except Exception as exc:                         # unparsable printed text is a failure, never a skip
        fail(f"{label}: cannot read {tex!r} ({exc})")
        return
    if equal(e, target):
        ok(f"{label}: {tex}")
    else:
        fail(f"{label}: printed {tex} = {e}, expected {target}")


def lines_of(t):
    """Split a math segment into lines: aligned environments split at \\\\, comments and words removed."""
    t = t.replace("\\begin{aligned}[t]", "").replace("\\end{aligned}", "")
    t = re.sub(r"\\text\{(Let|Then|Hence|and) \}", "", t)
    # a \qquad starts a comment such as '(here a = 4, b = -1 and n = 7)' or '(convert to index form)'
    return [re.sub(r"\\qquad.*$", "", ln).replace("&", "").strip() for ln in t.split("\\\\") if ln.strip()]


def chains(segments):
    """[(lhs, [members])] from a list of math segments; a line starting with '=' continues the last chain."""
    out = []
    for seg in segments:
        for ln in lines_of(seg):
            parts = top_split(ln, "=")
            if parts[0].strip() == "" and out:
                out[-1][1].extend(p for p in parts[1:])
            else:
                out.append((parts[0].strip(), list(parts[1:])))
    return out


DY = ("\\dfrac{dy}{dx}", "\\frac{dy}{dx}", "f'(x)")
YS = ("y", "f(x)")


def check_calculus(label, segs, given, need_y=True):
    """y/f(x) chains equal the given function, dy/dx or f'(x) chains equal its derivative,
    u, y(u), du/dx, dy/du chains are consistent with a chain-rule decomposition of the given function."""
    d = sp.diff(given, x)
    U = Yu = None
    seen_d = seen_y = False
    last_d = None
    for lhs, mem in chains(segs):
        if lhs in YS and mem and "u" in str(S(mem[0]).free_symbols):
            Yu = S(mem[0])
            for k, t in enumerate(mem):
                same(f"{label} y(u) [{k + 1}]", t, Yu)
        elif lhs in YS:
            seen_y = True
            for k, t in enumerate(mem):
                same(f"{label} {lhs} [{k + 1}]", t, given)
        elif lhs in DY:
            seen_d = True
            for k, t in enumerate(mem):
                if "du" in t:
                    if t.replace(" ", "") != "\\dfrac{dy}{du}\\times\\dfrac{du}{dx}":
                        fail(f"{label}: unexpected chain-rule member {t}")
                    continue
                same(f"{label} {lhs} [{k + 1}]", t, d)
                last_d = t
        elif lhs == "u":
            U = S(mem[0])
        elif lhs == "\\dfrac{du}{dx}":
            if U is None:
                fail(f"{label}: du/dx before u"); continue
            for k, t in enumerate(mem):
                same(f"{label} du/dx [{k + 1}]", t, sp.diff(U, x))
        elif lhs == "\\dfrac{dy}{du}":
            if Yu is None:
                fail(f"{label}: dy/du before y(u)"); continue
            for k, t in enumerate(mem):
                same(f"{label} dy/du [{k + 1}]", t, sp.diff(Yu, u))
        else:
            fail(f"{label}: unclassified chain {lhs} = {mem}")
    if U is not None or Yu is not None:
        if U is None or Yu is None:
            fail(f"{label}: incomplete chain-rule decomposition")
        else:
            if equal(Yu.subs(u, U), given):
                ok(f"{label} y(u(x)) = given function")
            else:
                fail(f"{label}: y(u) with u = {U} is {Yu.subs(u, U)}, not {given}")
    if not seen_d:
        fail(f"{label}: no derivative line")
    if need_y and not seen_y:
        fail(f"{label}: no y = line")
    return last_d


def consistent(label, tex, subs=None):
    """Every member of the chain tex (split at top-level '=' and \\qquad) is equal to the first member."""
    for piece in tex.split("\\qquad"):
        mem = [p for p in top_split(piece, "=")]
        if len(mem) < 2:
            continue
        try:
            first = S(mem[0])
        except Exception as exc:
            fail(f"{label}: cannot read {mem[0]!r} ({exc})")
            continue
        if subs:
            first = first.subs(subs)
        for k, t in enumerate(mem[1:]):
            same(f"{label} [{k + 2}]", t, first)


def parts_of(block, n=None):
    """Answer or solution parts: {letter: text} split at <b>x</b>."""
    bits = re.split(r"<b>([a-z])</b>", block)
    out = {bits[i]: bits[i + 1] for i in range(1, len(bits) - 1, 2)}
    if n is not None and sorted(out) != [chr(97 + k) for k in range(n)]:
        fail(f"parts found {sorted(out)}, expected {n}")
    return out


def qparts(block):
    """Question parts: {letter: math text} from <span class="pl">x</span>\\(...\\)."""
    return dict(re.findall(r'<span class="pl">([a-z])</span>\\\((.*?)\\\)', block, re.S))


rev = read("revision.html")
arev = read("a_rev.html")

# ======================= 1. summary boxes =======================


def box(title):
    return one(r'<div class="bt">' + re.escape(title) + r'</div>(.*?)</div>\n\n', rev, f"box '{title}'")


BOXES = {
    "Index laws, zero and negative indices (Year 11, 7A)": {
        "id": [r"a^m\times a^n=a^{m+n}", r"a^m\div a^n=a^{m-n}", r"(a^m)^n=a^{mn}", r"(ab)^n=a^n\times b^n",
               r"\Big(\dfrac ab\Big)^n=\dfrac{a^n}{b^n}", r"a^3\div a^3=1", r"a^{3-3}=a^0", r"a^0=1",
               r"a^2\div a^3=\frac1a", r"a^{2-3}=a^{-1}", r"a^{-1}=\frac1a",
               r"a^0=1\qquad a^{-1}=\dfrac1a\qquad a^{-2}=\dfrac{1}{a^2}\qquad a^{-n}=\dfrac{1}{a^n}.",
               r"\Big(\dfrac23\Big)^{-3}=\Big(\dfrac32\Big)^3=\dfrac{27}{8}",
               r"\frac{5}{x^2}=5\times\frac{1}{x^2}=5x^{-2}", r"\frac{1}{3x^5}=\frac13\times\frac{1}{x^5}=\tfrac13x^{-5}"],
        "skip": [r"a^n=a\times a\times\cdots\times a"]},          # definition with n factors
    "Fractional indices (Year 11, 7B)": {
        "id": [r"\big(\sqrt a\big)^2=a", r"\big(a^{\frac12}\big)^2=a^1=a", r"a^{\frac12}=\sqrt a", r"a^{\frac13}=\sqrt[3]a",
               r"a^{\frac1n}=\sqrt[n]a\qquad a^{\frac mn}=\big(\sqrt[n]a\big)^m=\sqrt[n]{a^m}\qquad a^{-\frac mn}=\dfrac{1}{a^{\frac mn}},",
               r"\Big(\dfrac{8}{27}\Big)^{-\frac43}=\Big(\dfrac{27}{8}\Big)^{\frac43}=\Big(\dfrac32\Big)^4=\dfrac{81}{16}",
               r"\sqrt x=x^{\frac12}\qquad\dfrac{1}{\sqrt x}=x^{-\frac12}\qquad\sqrt[3]{x^2}=x^{\frac23}",
               r"x\sqrt x=x^1\times x^{\frac12}=x^{\frac32}\qquad\dfrac{1}{x\sqrt x}=x^{-\frac32}",
               r"x^{1\frac12}=x^{\frac32}", r"x^{-1\frac12}=x^{-\frac32}", r"\sqrt9=9^{\frac12}=3"],
        "skip": []},
    "Differentiating powers of \\(x\\) (Year 11, 8C, 8E, 8F)": {
        "id": [r"x^3(x-10)=x^4-10x^3"],
        "deriv": [(r"y=x^{-4}", r"\frac{dy}{dx}=-4x^{-5}"), (r"y=x^{\frac52}", r"\frac{dy}{dx}=\tfrac52x^{\frac32}")],
        "skip": [r"f(x)=x^n", r"f'(x)=nx^{n-1}", r"f(x)=g(x)+k(x)", r"f'(x)=g'(x)+k'(x)", r"f(x)=ag(x)", r"f'(x)=ag'(x)"]},
    "The chain rule (Year 11, 8G)": {
        "id": [],
        "skip": [r"y=\sqrt{25-x^2}", r"u=25-x^2", r"y=\sqrt u", r"\dfrac{dy}{dx}=\dfrac{dy}{du}\times\dfrac{du}{dx}.",
                 r"u=ax+b", r"y=u^n", r"\dfrac{du}{dx}=a", r"\dfrac{dy}{du}=nu^{n-1}",
                 r"\dfrac{d}{dx}(ax+b)^n=an(ax+b)^{n-1}.", r"\dfrac{d}{dx}\big(f(x)\big)^n=n\big(f(x)\big)^{n-1}f'(x)"]},
    "Sums of terms and sigma notation (Year 12, 1E)": {
        "id": [],
        "skip": [r"S_n=T_1+T_2+T_3+\cdots+T_n", r"T_1=S_1", r"T_n=S_n-S_{n-1}", r"\sum_{n=5}^{20}T_n=T_5+T_6+T_7+T_8+\cdots+T_{20},",
                 r"\sum_{n=2}^{5}n^2=2^2+3^2+4^2+5^2=4+9+16+25=54.", r"n=2", r"n=5", r"5-2+1=4", r"S_1=T_1",
                 r"S_2=T_1+T_2", r"S_3=T_1+T_2+T_3", r"\displaystyle\sum_{x=a}^{b}f(x)\,\delta x"]},
    "Area formulae": {
        "id": [],
        "skip": [r"A=lb", r"A=\tfrac12bh=\tfrac12\times\text{base}\times\text{height}", r"A=\tfrac12(a+b)h", r"A=\pi r^2",
                 r"A=\tfrac12\pi r^2", r"A=\tfrac14\pi r^2"]},
    "Circles and semicircles (Year 11, 3G), and the graph of \\(y=|x|\\) (4D)": {
        "id": [],
        "skip": [r"x^2+y^2=a^2", r"y=\sqrt{a^2-x^2}", r"y=-\sqrt{a^2-x^2}", r"y=|x|", r"y=x", r"y=-x"]},
}
for title, spec in BOXES.items():
    body = box(title)
    segs = [t.strip() for t in maths(body) if "=" in t]
    known = set(spec["id"]) | set(spec["skip"]) | {t for pair in spec.get("deriv", []) for t in pair}
    for t in segs:
        if t not in known:
            fail(f"box '{title}': unclassified equation {t}")
    for t in known:
        if t not in segs:
            fail(f"box '{title}': expected equation missing: {t}")
    for t in spec["id"]:
        consistent(f"box {title[:22]} identity", t)
    for yt, dt in spec.get("deriv", []):
        same(f"box derivative of {yt}", dt.split("=", 1)[1], sp.diff(S(yt.split("=", 1)[1]), x))
# general formulae in the boxes, checked by sympy
k = sp.symbols("k", integer=True)
same("box power rule x^n", "nx^{n-1}", sp.diff(x ** n, x))
same("box (ax+b)^n rule", "an(ax+b)^{n-1}", sp.diff((a * x + b) ** n, x))
same("box chain rule for y = sqrt(25 - x^2) with u = 25 - x^2",
     str(sp.diff(sp.sqrt(u), u).subs(u, 25 - x ** 2) * sp.diff(25 - x ** 2, x)).replace("**", "^").replace("*", ""),
     sp.diff(sp.sqrt(25 - x ** 2), x))
sig = box("Sums of terms and sigma notation (Year 12, 1E)")
mem = top_split(one(r"\\\[(\\sum_\{n=2\}\^\{5\}n\^2=.*?)\.\\\]", sig, "sigma example"), "=")
terms = [i ** 2 for i in range(2, 6)]
same("box sigma example powers", mem[1], sum(terms))
if [int(v) for v in re.findall(r"\d+", mem[2])] == terms:
    ok(f"box sigma example terms {mem[2]}")
else:
    fail(f"box sigma example terms {mem[2]} != {terms}")
same("box sigma example total", mem[3], sp.summation(k ** 2, (k, 2, 5)))
same("box sigma number of terms", one(r"There are \\\((5-2\+1=\d+)\\\) terms", sig, "term count").split("=")[1], len(terms))

# ======================= 2. worked examples =======================


def example(title):
    """The textbook example box, followed by its 'Steps the book skips' tip (the pack's notes), if any."""
    box, tip = one(r'<span class="ex-title">' + re.escape(title) + r'</span>(.*?)</div></div>\n'
                   r'(?:<div class="box tip"[^>]*><p style="margin:0"><span class="bt"[^>]*>Steps the book skips: '
                   + re.escape(title.split(" (")[0]) + r'</span>(.*?)</p></div>\n)?\n', rev, f"example '{title}'")
    if '<p class="small">' in box or "box tip" in box:
        fail(f"{title}: pack note inside the textbook box")
    return box + ('<div class="tipnotes">' + tip + "</div>" if tip else "")


def split_q_s(blk, title):
    if blk.count('<div class="sol-label">Solution</div>') != 1:
        fail(f"{title}: solution label")
    blk, _, tip = blk.partition('<div class="tipnotes">')
    q, s = blk.split('<div class="sol-label">Solution</div>')
    notes = tip.rsplit("</div>", 1)[0]
    return q, s, notes


def check_notes(title, notes, subs_by_seg=None):
    for t in maths(notes):
        if "=" not in t:
            continue
        sub = (subs_by_seg or {}).get(t)
        consistent(f"{title} note", t, sub)


# Year 11 Example 5 (7A) and Example 10 (7B): each chain equals the question's expression
for title, nparts in (("Year 11 Example 5 (7A)", 3), ("Year 11 Example 10 (7B)", 4)):
    q, s, notes = split_q_s(example(title), title)
    given = qparts(q)
    sol = parts_of(s, nparts)
    if len(given) != nparts:
        fail(f"{title}: {len(given)} question parts")
    for p, txt in sol.items():
        segs = maths(txt)
        if len(segs) != 1:
            fail(f"{title} {p}: {len(segs)} math segments"); continue
        lns = lines_of(segs[0])
        mem = top_split(lns[0], "=") + [t for ln in lns[1:] for t in top_split(ln, "=")[1:]]
        if mem[0].strip() != given[p].strip():
            fail(f"{title} {p}: solution starts {mem[0]!r}, question {given[p]!r}")
        target = S(given[p])
        for i, t in enumerate(mem[1:]):
            same(f"{title} {p} [{i + 2}]", t, target)
    check_notes(title, notes)
# the final forms asked for
ex5 = parts_of(split_q_s(example("Year 11 Example 5 (7A)"), "")[1])
for p, fin in (("a", r"\dfrac{1}{x^6}"), ("b", r"\dfrac2a"), ("c", r"\dfrac{1}{2^{3n}}")):     # book PDF 266
    last = top_split(lines_of(maths(ex5[p])[0])[-1], "=")[-1]
    if last.strip() == fin:
        ok(f"Example 5 {p} final form {fin} (no negative index), as the textbook")
    else:
        fail(f"Example 5 {p} final form {last}")

# Year 11 Examples 17, 21, 23 (8E, 8F): y/f(x) and derivative chains
for title, nparts in (("Year 11 Example 17 (8E)", 3), ("Year 11 Example 21 (8F)", 3), ("Year 11 Example 23 (8F)", 2)):
    q, s, notes = split_q_s(example(title), title)
    given = {p: S(t.split("=", 1)[1]) for p, t in qparts(q).items()}
    if len(given) != nparts:
        fail(f"{title}: {len(given)} question parts")
    for p, txt in parts_of(s, nparts).items():
        check_calculus(f"{title} {p}", maths(txt), given[p])
    check_notes(title, notes)
# textbook printed final answers (Y11 Advanced PDF 325, 330)
BOOKFIN = {("Year 11 Example 17 (8E)", "a"): r"-\dfrac{1}{x^2}", ("Year 11 Example 17 (8E)", "b"): r"-\dfrac{10}{x^3}",
           ("Year 11 Example 17 (8E)", "c"): r"-\dfrac{5}{3x^6}", ("Year 11 Example 21 (8F)", "a"): r"\dfrac{6}{\sqrt x}",
           ("Year 11 Example 21 (8F)", "b"): r"\dfrac{2}{\sqrt x}", ("Year 11 Example 21 (8F)", "c"): r"-\dfrac{3}{2x\sqrt x}",
           ("Year 11 Example 23 (8F)", "a"): r"5x^{-\frac12}+3x^{-1\frac12}", ("Year 11 Example 23 (8F)", "b"): r"-2x^{-1\frac12}"}
for (title, p), fin in BOOKFIN.items():
    txt = parts_of(split_q_s(example(title), title)[1])[p]
    last = top_split(lines_of(maths(txt)[0])[-1], "=")[-1].strip()
    if last == fin:
        ok(f"{title} {p} final answer printed as the textbook: {fin}")
    else:
        fail(f"{title} {p} final answer {last}, textbook {fin}")

# Year 11 Example 24 (8G): full chain-rule setting-out
title = "Year 11 Example 24 (8G)"
q, s, notes = split_q_s(example(title), title)
given = {p: S(t) for p, t in qparts(q).items()}
for p, txt in parts_of(s, 2).items():
    check_calculus(f"{title} {p}", maths(txt), given[p])
for t, U in ((r"6u^5=6(x^2+1)^5", x ** 2 + 1), (r"35u^4=35(3x+4)^4", 3 * x + 4)):
    if t in maths(notes):
        consistent(f"{title} note (u = {U})", t, {u: U})
    else:
        fail(f"{title} note {t} missing")
for p, fin in (("a", r"12x(x^2+1)^5."), ("b", r"105(3x+4)^4.")):              # book PDF 334
    if ("&=" + fin) in parts_of(s)[p]:
        ok(f"{title} {p} final answer as the textbook: {fin}")
    else:
        fail(f"{title} {p} final answer {fin} not found")

# Year 11 Example 25 (8G)
title = "Year 11 Example 25 (8G)"
q, s, notes = split_q_s(example(title), title)
given = {p: S(t.split("=", 1)[1]) for p, t in qparts(q).items()}
sol = parts_of(s, 3)
for p, txt in sol.items():
    check_calculus(f"{title} {p}", maths(txt), given[p])
for p, (av, bv, nv) in (("a", ("4", "-1", "7")), ("b", ("3", "-8", "-1")), ("c", ("5", "3", "\\tfrac12"))):
    g = given[p]
    base = [f for f in sp.preorder_traversal(g) if isinstance(f, sp.Pow) and f.base.is_polynomial(x) and sp.degree(f.base, x) == 1]
    lin = sp.Poly(base[0].base, x)
    if f"(here }}a={av},\\ b={bv}\\text{{ and }}n={nv})" in sol[p] and (lin.coeffs()[0], lin.coeffs()[1], base[0].exp) == (S(av), S(bv), S(nv)):
        ok(f"{title} {p}: a = {av}, b = {bv}, n = {nv} agree with the function")
    else:
        fail(f"{title} {p}: a, b, n comment")
for p, fin in (("a", r"28(4x-1)^6"), ("b", r"-\dfrac{3}{(3x-8)^2}"), ("c", r"\dfrac{5}{2\sqrt{5x+3}}")):   # book PDF 335
    last = top_split(lines_of(maths(sol[p])[0])[-1], "=")[-1].strip()
    same(f"{title} {p} final = textbook {fin}", last, S(fin))

# Year 12 Example 21 (1E): sums
title = "Year 12 Example 21 (1E)"
q, s, notes = split_q_s(example(title), title)
qs = qparts(q)


def sigma(tex):
    lo, hi, body = one(r"\\sum_\{n=(-?\d+)\}\^\{(-?\d+)\}(.*)$", tex.replace("\\displaystyle", "").strip(), f"sigma {tex}")
    f = S(body).subs(n, k)
    return [f.subs(k, i) for i in range(int(lo), int(hi) + 1)], sp.summation(f, (k, int(lo), int(hi)))


def check_sum(label, chain_members, given_tex, expand=True):
    terms, total = sigma(given_tex)
    if chain_members[0].replace("\\displaystyle", "").strip() != given_tex.replace("\\displaystyle", "").strip():
        fail(f"{label}: chain starts {chain_members[0]}")
    if expand:
        got = [int(v) for v in re.findall(r"[+-]?\d+", chain_members[1].replace(" ", ""))]
        if got == terms:
            ok(f"{label}: terms {chain_members[1]}")
        else:
            fail(f"{label}: printed terms {got}, computed {terms}")
    same(f"{label}: total", chain_members[-1], total)
    return terms, total


for p, txt in parts_of(s, 2).items():
    lns = lines_of(maths(txt)[0])
    mem = top_split(lns[0], "=") + [t for ln in lns[1:] for t in top_split(ln, "=")[1:]]
    check_sum(f"{title} {p}", mem, qs[p])
check_notes(title, notes)
same(f"{title} a = textbook 114", "114", sigma(qs["a"])[1])          # book PDF 53
same(f"{title} b = textbook -22", "-22", sigma(qs["b"])[1])

# Using the area formulae (the pack's own example, in a titled tip)
title = "Using the area formulae"
ablk = one(r'<div class="box tip" data-ex="area"><div class="bt">Our own example: using the area formulae</div>\n(.*?)</div>\n\n', rev, "area example tip")
q, s = ablk.split("<p style=\"margin:1mm 0 0.5mm\"><b>Solution.</b></p>")
s = s.split("<p>Leave")[0]                     # the closing advice names part b; it is not working
qa = one(r"parallel sides (\d+) cm and (\d+) cm, at a perpendicular distance of (\d+) cm apart", q, "area a")
qb = one(r"a quadrant of radius (\d+) cm", q, "area b")
qc = one(r"a triangle with base (\d+) cm and perpendicular height (\d+) cm", q, "area c")
AREA = {"a": (sp.Rational(1, 2) * (int(qa[0]) + int(qa[1])) * int(qa[2]), {a: int(qa[0]), b: int(qa[1]), h: int(qa[2])}),
        "b": (sp.pi * int(qb) ** 2 / 4, {r: int(qb)}),
        "c": (sp.Rational(1, 2) * int(qc[0]) * int(qc[1]), {b: int(qc[0]), h: int(qc[1])})}
FORM = {"a": r"\tfrac12(a+b)h", "b": r"\tfrac14\pi r^2", "c": r"\tfrac12bh"}
for p, txt in parts_of(s, 3).items():
    lns = lines_of(maths(txt)[0])
    mem = top_split(lns[0], "=")[1:] + [t for ln in lns[1:] for t in top_split(ln, "=")[1:]]
    if mem[0] != FORM[p]:
        fail(f"{title} {p}: formula {mem[0]}")
    val, sub = AREA[p]
    same(f"{title} {p} formula at the given values", str(S(mem[0]).subs(sub)), val)
    for i, t in enumerate(mem[1:]):
        same(f"{title} {p} [{i + 2}]", t, val)

# ======================= 3. warm-up =======================


def qblock(nq):
    return one(r'<div class="q"><span class="q-num">' + str(nq) + r'</span>(.*?)\{\{work:\d+\}\}', rev, f"warm-up Q{nq}")


def ablock(nq):
    return one(r'<div class="a"><span class="an">' + str(nq) + r'</span><div class="ab">(.*?)</div></div>', arev, f"answer {nq}")


LABEL = {1: "Year 11 Exercise 7B Q13", 2: "Year 11 Exercise 8E Q5", 3: "Year 11 Exercise 8G Q4",
         4: "Year 11 Exercise 8G Q8", 5: "Year 12 Exercise 1E Q4"}
for nq, lab in LABEL.items():
    for blk, where in ((qblock(nq), "question"), (ablock(nq), "answer")):
        if f'<span class="muted small">{lab}</span>' in blk:
            ok(f"Q{nq} {where} labelled {lab}")
        else:
            fail(f"Q{nq} {where} label {lab} missing")

# Textbook questions (book part letter -> expression), Y11 Advanced PDF 274, 327, 331, 337; Y12 PDF 54.
BOOKQ = {
    1: {"a": r"\dfrac{1}{\sqrt x}", "b": r"\dfrac{12}{\sqrt x}", "c": r"-\dfrac{5}{\sqrt x}", "d": r"\dfrac{15}{\sqrt[3]x}",
        "e": r"-\dfrac{4}{\sqrt[3]{x^2}}", "f": r"x\sqrt x", "g": r"\dfrac{5}{x\sqrt x}", "h": r"8x^2\sqrt x"},
    2: {"a": r"\dfrac{x^3+x^2}{x}", "b": r"\dfrac{x^3+x^2}{x^5}", "c": r"\dfrac{4x-5x^4}{x^2}", "d": r"\dfrac{6x^2+6x^6}{2x^6}"},
    3: {"a": r"(5x-7)^5", "c": r"9(5x+3)^4", "d": r"(4-3x)^7", "f": r"(4x-5)^{-7}", "g": r"2(3x+7)^{-5}", "i": r"3(5-7x)^{-4}"},
    4: {"a": r"(5-x^2)^3", "b": r"(3x^2+7)^7", "d": r"(3x^3-7)^5", "e": r"(x^3-x^2)^{-5}"},
    5: {"a": r"\sum_{n=1}^{6}2n", "b": r"\sum_{n=1}^{6}(3n+2)", "d": r"\sum_{n=5}^{8}n^2", "f": r"\sum_{n=0}^{5}2^n",
        "g": r"\sum_{n=2}^{4}3^n", "j": r"\sum_{n=5}^{105}4", "k": r"\sum_{n=0}^{4}(-1)^n(n+5)"},
}
# Textbook printed answers, keyed by the book's part letters (Y11 Advanced PDF 553, 559, 560; Y12 PDF 853)
BOOKA = {
    1: {"a": r"x^{-\frac12}", "b": r"12x^{-\frac12}", "c": r"-5x^{-\frac12}", "d": r"15x^{-\frac13}", "e": r"-4x^{-\frac23}",
        "f": r"x^{1\frac12}", "g": r"5x^{-1\frac12}", "h": r"8x^{2\frac12}"},
    2: {"a": r"2x+1", "b": r"-2x^{-3}-3x^{-4}", "c": r"-4x^{-2}-10x", "d": r"-12x^{-5}"},
    3: {"a": r"25(5x-7)^4", "c": r"180(5x+3)^3", "d": r"-21(4-3x)^6", "f": r"-28(4x-5)^{-8}", "g": r"-30(3x+7)^{-6}", "i": r"84(5-7x)^{-5}"},
    4: {"a": r"-6x(5-x^2)^2", "b": r"42x(3x^2+7)^6", "d": r"45x^2(3x^3-7)^4", "e": r"-5(3x^2-2x)(x^3-x^2)^{-6}"},
    5: {"a": "42", "b": "75", "d": "174", "f": "63", "g": "117", "j": "404", "k": "7"},
}


def printed_givens(nq):
    blk = qblock(nq)
    return {p: (t.split("=", 1)[1] if t.startswith("y=") else t) for p, t in qparts(blk).items()}


for nq in range(1, 6):
    pg = printed_givens(nq)
    book = list(BOOKQ[nq].items())
    if len(pg) != len(book):
        fail(f"Q{nq}: {len(pg)} printed parts, {len(book)} chosen from the book")
        continue
    for (mine, tex), (bl, btex) in zip(sorted(pg.items()), book):
        if nq == 5:
            if sigma(tex) == sigma(btex):
                ok(f"Q5{mine} = Exercise 1E Q4{bl}: {tex}")
            else:
                fail(f"Q5{mine} differs from Exercise 1E Q4{bl}")
        else:
            same(f"Q{nq}{mine} = book Q{bl}", tex, S(btex))

# Q1: each member equals the given expression; the final member is a single power c x^k, as the textbook's answer
pg, ans = printed_givens(1), parts_of(ablock(1), 8)
for (p, txt), (bl, btex) in zip(sorted(ans.items()), BOOKA[1].items()):
    segs = maths(txt)
    mem = top_split(segs[0], "=")
    if mem[0] != pg[p]:
        fail(f"Q1{p}: answer starts {mem[0]}, question {pg[p]}")
    for i, t in enumerate(mem[1:]):
        same(f"Q1{p} [{i + 2}]", t, S(pg[p]))
    if re.fullmatch(r"-?\d*x\^\{-?\\frac\d\d\}", mem[-1]):
        ok(f"Q1{p}: final {mem[-1]} is one power of x with a fractional or negative index")
    else:
        fail(f"Q1{p}: final {mem[-1]} is not of the form c x^k")
    same(f"Q1{p} final = textbook Q13{bl} {btex}", mem[-1], S(btex))
    for t in segs[1:]:                                # '(also written x^{1\frac12})'
        same(f"Q1{p} mixed-number form", t.split("written ")[-1], S(pg[p]))

# Q2: y chains = given, dy/dx chains = derivative; compare with the textbook
pg, ans = printed_givens(2), parts_of(ablock(2), 4)
for (p, txt), (bl, btex) in zip(sorted(ans.items()), BOOKA[2].items()):
    last = check_calculus(f"Q2{p}", maths(txt), S(pg[p]))
    same(f"Q2{p} final = textbook {bl} {btex}", last, sp.diff(S(pg[p]), x))
    same(f"Q2{p} textbook answer {btex} = derivative", btex, sp.diff(S(pg[p]), x))
    if "\\frac" in last:
        fail(f"Q2{p}: final derivative {last} not left with negative indices")

# Q3, Q4: chain rule
for nq, npart in ((3, 6), (4, 4)):
    pg, ans = printed_givens(nq), parts_of(ablock(nq), npart)
    for (p, txt), (bl, btex) in zip(sorted(ans.items()), BOOKA[nq].items()):
        last = check_calculus(f"Q{nq}{p}", maths(txt), S(pg[p]), need_y=False)
        if last.replace(" ", "") == btex:
            ok(f"Q{nq}{p} final printed as the textbook: {btex}")
        else:
            fail(f"Q{nq}{p} final {last}, textbook {btex}")
        same(f"Q{nq}{p} textbook answer = sympy derivative", btex, sp.diff(S(pg[p]), x))
    if nq == 3:                                       # the standard-form factors a x n x coefficient
        for p, txt in ans.items():
            mem = top_split(maths(txt)[0], "=")
            g = S(pg[p])
            lin = [f for f in sp.preorder_traversal(g) if isinstance(f, sp.Pow) and sp.degree(f.base, x) == 1][0]
            coef = sp.simplify(g / lin)
            factors = [S(v) for v in top_split(clean(mem[1]), "*")[:-1]]
            expect = ([coef] if coef != 1 else []) + [sp.Poly(lin.base, x).coeffs()[0], lin.exp]
            if sorted(factors, key=str) == sorted(expect, key=str):
                ok(f"Q3{p}: factors {factors} = coefficient, a and n")
            else:
                fail(f"Q3{p}: factors {factors}, expected {expect}")

# Q5: sigma notation
pg, ans = printed_givens(5), parts_of(ablock(5), 7)
for (p, txt), (bl, btex) in zip(sorted(ans.items()), BOOKA[5].items()):
    segs = maths(txt)
    mem = top_split(segs[0], "=")
    if p == "f":
        terms, total = sigma(pg[p])
        if mem[1].replace(" ", "") == r"4+4+4+\cdots+4" and set(terms) == {4}:
            ok("Q5f expansion 4+4+4+...+4")
        else:
            fail(f"Q5f expansion {mem}")
        cnt = top_split(segs[1], "=")
        same("Q5f number of terms", cnt[0], len(terms))
        same("Q5f number of terms", cnt[1], len(terms))
        tot = top_split(segs[2], "=")
        same("Q5f total", tot[0], total)
        same("Q5f total", tot[1], total)
        same("Q5f = textbook 404", btex, total)
        continue
    terms, total = check_sum(f"Q5{p}", mem, pg[p])
    same(f"Q5{p} = textbook Q4{bl} {btex}", btex, total)

print(f"\n{checked} checks passed, {fails} failures")
sys.exit(1 if fails else 0)
