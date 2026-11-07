"""Check of Lesson 12D (Integration Part 3 pack): Integration by substitution.

The script reads the values PRINTED in workspace/build/int3/l12d.html and a_12d.html and recomputes
them with sympy (and mpmath quadrature as a fallback). Nothing is copied from the answers into the script.
  - Every worked solution is laid out as a display (left) and a working column (right). In each one:
      * the working column is checked line by line: 'Let u = g(x)'; 'du = A dx' and 'du/dx = A' (A must be
        g'(x)); 'P dx = Q du' (P must be Q g'(x)); 'x = h(u)' (h(g(x)) must be x); 'When x = a, u = b'
        (b must be g(a)); 'int u^n du/dx dx = F' (F' must be u^n);
      * every chain of the display is split at its '=' signs and each piece is turned into sympy
        (TeX -> sympy with workspace/checks/int3_tex.py; each \\int is replaced by sympy's own integral in
        x or in u, and each [F]_a^b by F(b) - F(a)). Pieces in u are put back into x with u = g(x).
        A definite chain must have the exact value of its first integral at every piece; an indefinite
        chain must differentiate (with respect to x) to the integrand at every piece;
      * the integral on the left of each answer chain must be printed exactly once in the matching
        lesson block (the concept's tutor demo and your turn, or the past-paper question).
  - Other displays and inline identities (index laws, exact values) are checked numerically.
  - Textbook homework: each part of Exercise 12D is read from the lesson, and the printed answer is
    compared with sympy (derivative for primitives, exact value for definite integrals); Q9 is checked as
    an initial-value problem, Q13(c) and Q14 as identities.
  - Past papers: in the MC only the keyed option has the value of the integral; marks add to the intro
    total (15-22); time is 1.5 x marks rounded to 5 min; numbering and source labels match in both files;
    one hint per question.
A template that is not found exactly once FAILS. Exit status 1 on any failure.
Run: python3 workspace/checks/int3_12d.py
"""
import os
import random
import re
import sys

import mpmath
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

x, u, theta = T.x, T.u, T.theta
SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))
FAILS, NCHECK = [], [0]
MATH_BREAK = "\\)\\({}"
POINTS = [0.13, 0.27, 0.41, 0.55, 0.63, 0.74, 0.86, 0.95, 1.12, 1.27, 1.43, 1.61, 1.78, 1.93, 2.4, 2.8, 3.3, -0.35, -0.7, -1.4]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace(MATH_BREAK, "")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100] + ("  " + str(detail).replace("\n", " ")[:160] if detail else ""))
    if not ok:
        FAILS.append(label)
    return ok


def once(hay, needle, label):
    k = hay.count(needle)
    report(k == 1, f"printed once: {label}", f"found {k} times: {needle[:70]}")
    return k == 1


# ------------------------------------------------------------------ TeX helpers
def brace(s, i):
    """s[i] == '{': return (inner, index after the closing brace)."""
    assert s[i] == "{", s[i:i + 20]
    d = 0
    for j in range(i, len(s)):
        d += s[j] == "{"
        d -= s[j] == "}"
        if d == 0:
            return s[i + 1:j], j + 1
    raise ValueError("unbalanced " + s[i:i + 30])


def clean(s):
    s = s.replace("\\displaystyle", "").replace("\\lt", "<").replace("\\gt", ">")
    s = s.replace("\\left(", "(").replace("\\right)", ")")
    s = s.replace("\\ln\\cos x", "\\ln(\\cos x)")
    s = re.sub(r"\\sqrt\s+([a-z])", r"\\sqrt{\1}", s)
    s = s.replace("\\,(-du)", "\\times(-1)\\,du")
    s = re.sub(r"\\frac\{du\}\{dx\}\\,dx", r"\\,du", s)
    # \sqrt[3]{A} -> (A)^{1/3}
    while "\\sqrt[3]" in s:
        j = s.index("\\sqrt[3]")
        inner, k = brace(s, j + 8)
        s = s[:j] + "(" + inner + ")^{\\frac13}" + s[k:]
    # \int[_{a}^{b}]\dfrac{dx}{D}  ->  \int[_{a}^{b}]\dfrac{1}{D}\,dx   (and du)
    out, i = "", 0
    for m in re.finditer(r"\\d?frac\{d(x|u)\}\{", s):
        if m.start() < i:
            continue
        inner, k = brace(s, m.end() - 1)
        out += s[i:m.start()] + "\\dfrac{1}{" + inner + "}\\,d" + m.group(1)
        i = k
    s = out + s[i:]
    s = re.sub(r"\\[,;!]", " ", s).replace("\\ ", " ")
    s = re.sub(r"\\q?quad", " ", s)
    s = re.sub(r"\\(?:big|Big|bigg|Bigg)([()])", r"\1", s)
    # int3_tex lets a function argument run into a following \sqrt (\tan^2x\sqrt{t} -> tan(x sqrt t)^2): cut it
    s = re.sub(r"(\\(?:sin|cos|tan|sec)(?:\^(?:\{[^}]*\}|\d))?[a-z0-9]+)\\sqrt", r"\1\\cdot\\sqrt", s)
    # int3_tex reads a bare multi-digit function argument digit by digit (\sin12x -> sin(1*2*x)): bracket it
    s = re.sub(r"(\\(?:sin|cos|tan|cot|sec|ln)(?:\^(?:\{[^}]*\}|\d))?)(\d{2,}[a-z])", r"\1(\2)", s)
    return s.strip()


def tex(s):
    s = clean(s)
    s = re.sub(r"\+\s*[CcDE](?:_\d)?\s*$", "", s.strip())
    return T.tex(s)


def py(e):
    return "(" + sp.sstr(e) + ")"


VAR = {"x": x, "u": u, "\\theta": theta}


def definite(f, v, a, b):
    try:
        val = sp.integrate(f, (v, a, b))
        if val.has(sp.Integral) or not val.is_number:
            raise ValueError
        return val
    except Exception:  # noqa: BLE001
        fl = sp.lambdify(v, f, "mpmath")
        return sp.Float(mpmath.quad(lambda t: fl(t), [float(a), float(b)]), 25)


def antideriv(f, v):
    val = sp.integrate(f, v)
    if val.has(sp.Integral):
        raise ValueError(f"sympy cannot integrate {f}")
    return val


def integrals(s):
    """Replace each \\int[_{a}^{b}] BODY d<var> by its sympy value; return (new string, info list)."""
    out, info, i = "", [], 0
    while True:
        j = s.find("\\int", i)
        if j < 0:
            return out + s[i:], info
        out += s[i:j]
        k = j + 4
        lims = None
        if s.startswith("_{", k):
            a, k = brace(s, k + 1)
            assert s[k] == "^", s[k:k + 10]
            b, k = brace(s, k + 1)
            lims = (a, b)
        m = re.compile(r"\s*d(x|u|\\theta)(?![a-zA-Z])").search(s, k)
        body = s[k:m.start()]
        v = VAR[m.group(1)]
        f = tex(body)
        if lims:
            val = definite(f, v, tex(lims[0]), tex(lims[1]))
        elif v == u:
            val = antideriv(f, v)
        else:
            val = sp.Integral(f, v)  # left unevaluated: only its derivative (the integrand) is ever used
        info.append((f, lims, v))
        out += py(val)
        i = m.end()


def brackets(s):
    """Replace \\Big[F\\Big]_{a}^{b} by F(b) - F(a)."""
    while "\\Big[" in s:
        j = s.index("\\Big[")
        k = s.index("\\Big]", j)
        F = tex(s[j + 5:k])
        m = k + 5
        assert s[m] == "_", s[m:m + 10]
        a, m = brace(s, m + 1)
        assert s[m] == "^"
        b, m = brace(s, m + 1)
        v = u if F.has(u) else (theta if F.has(theta) else x)
        s = s[:j] + py(F.subs(v, tex(b)) - F.subs(v, tex(a))) + s[m:]
    return s


def piece(s):
    s, info = integrals(clean(s))
    s = brackets(s)
    return tex(s), info


def val_at(e, t, v=x):
    try:
        z = complex(sp.N(e.subs(v, t), 30))
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    if z != z or abs(z) > 1e12 or abs(z.imag) > 1e-12 * max(1, abs(z)):
        return None
    return z.real


def same_fn(a, b, v=x, need=4):
    """a and b agree at the sample points where b is real; at least `need` such points."""
    k = 0
    for t in POINTS:
        vb = val_at(b, t, v)
        if vb is None:
            continue
        va = val_at(a, t, v)
        if va is None or abs(va - vb) > 1e-9 * max(1, abs(vb)):
            return False
        k += 1
    return k >= need


def num_eq(a, b):
    try:
        va, vb = complex(sp.N(a, 30)), complex(sp.N(b, 30))
    except (TypeError, ValueError):
        return False
    return abs(va - vb) <= 1e-12 * max(1, abs(vb))


# ------------------------------------------------------------------ chains
def displays(html):
    return re.findall(r"\\\[(.+?)\\\]", html, flags=re.S)


def chains_of(d):
    """Split an aligned display into chains: a line starting '&=' continues the chain above."""
    d = d.replace("\\begin{aligned}", "").replace("\\end{aligned}", "")
    chains = []
    for line in re.split(r"\\\\|\\qquad\\text\{[^}]*\}\\qquad|\\qquad\\qquad", d):
        if not line.strip():
            continue
        if line.lstrip().startswith("&=") and chains:
            chains[-1] += line
        else:
            chains.append(line)
    return [[p.strip().rstrip(".,") for p in T.split_top(c.replace("&", ""), "=") if p.strip()] for c in chains]


def skip_chain(ps):
    j = " ".join(ps)
    return any(t in j for t in ("F(", "f(", "\\frac{d}{dx}", "^n", "\\text{", "du}{dx}")) or len(ps) < 2


def check_chain(ps, label, g=None, need_in=None):
    """Integral chain: all pieces agree with the first integral. g = u as a function of x (or None)."""
    first = next((p for p in ps if "\\int" in p), None)
    if first is None:
        return check_identity(ps, label)
    try:
        _, info = piece(first)
    except Exception as e:  # noqa: BLE001
        return report(False, f"{label}: parse {first[:40]}", e)
    f, lims, v = info[0]
    ok, bad = True, ""
    whole, _ = piece(first)
    if lims:
        true = whole
    else:
        f = sp.diff(whole, v)
    for p in ps:
        try:
            e, _ = piece(p)
        except Exception as ex:  # noqa: BLE001
            ok, bad = False, f"parse {p[:50]}: {ex}"
            break
        if lims:
            if e.free_symbols or not num_eq(e, true):
                ok, bad = False, f"{p[:60]} != {true}"
                break
        else:
            if v == x and e.has(u):
                if g is None:
                    ok, bad = False, f"{p[:50]} has u but no substitution"
                    break
                e = e.subs(u, g)
            if not same_fn(sp.diff(e, v), f, v):
                ok, bad = False, f"d/d{v}({p[:50]}) != {f}"
                break
    report(ok, f"{label}: chain {first[:60]} ({len(ps)} pieces)", bad)
    if need_in is not None:
        lhs = clean_q(first)
        report(need_in.count(lhs) == 1, f"printed once: {label} question in lesson", f"{lhs[:60]} found {need_in.count(lhs)}")
    return ok


def check_identity(ps, label):
    if any(re.search(r"(?<![a-z\\])d[xu]", p) for p in ps):
        return True
    try:
        es = [tex(brackets(clean(p))) for p in ps]
    except Exception as e:  # noqa: BLE001
        return report(False, f"{label}: parse identity {ps[0][:50]}", e)
    fs = set().union(*[e.free_symbols for e in es])
    if not fs:
        ok = all(num_eq(es[0], e) for e in es[1:])
    elif len(fs) == 1:
        v = fs.pop()
        ok = all(same_fn(es[0], e, v, need=3) for e in es[1:])
    else:
        return True
    return report(ok, f"{label}: identity {' = '.join(ps)[:70]}")


def clean_q(s):
    return s.replace("\\displaystyle", "").strip()


# ------------------------------------------------------------------ working column
def column(col, label):
    """Check the 'Let u = ...' working column; return g(x)."""
    ms = re.findall(r"\\\((.+?)\\\)", col, flags=re.S)
    g, pend_x = None, None
    for m in ms:
        m = m.strip()
        if g is None:
            if not m.startswith("u="):
                report(False, f"{label}: column must start with Let u =", m)
                return None
            g = tex(m[2:])
            continue
        try:
            if m.startswith("x=") and not tex(m[2:]).has(u):
                pend_x = tex(m[2:])
                continue
            if m.startswith("u=") and pend_x is not None:
                ok = num_eq(g.subs(x, pend_x), tex(m[2:]))
                report(ok, f"{label}: when x = {pend_x}, {m}", f"g = {g.subs(x, pend_x)}")
                pend_x = None
                continue
            if m.startswith("x="):
                h = tex(m[2:])
                report(sp.simplify(h.subs(u, g) - x) == 0, f"{label}: {m} inverts u = {g}")
                continue
            mm = re.fullmatch(r"\\dfrac\{du\}\{dx\}=(.+)", m)
            if mm:
                report(same_fn(tex(mm.group(1)), sp.diff(g, x)), f"{label}: {m}")
                continue
            mm = re.fullmatch(r"du=(.*?)(?:\\,)?dx", m)
            if mm:
                a = mm.group(1)
                A = sp.Integer(1) if a == "" else (sp.Integer(-1) if a == "-" else tex(a))
                report(same_fn(A, sp.diff(g, x)), f"{label}: {m}", f"g' = {sp.diff(g, x)}")
                continue
            mm = re.fullmatch(r"(.*?)(?:\\,)?dx=(.*?)(?:\\,)?du", m)
            if mm:
                P = sp.Integer(1) if mm.group(1) == "" else tex(mm.group(1))
                q = mm.group(2)
                Q = sp.Integer(1) if q == "" else (sp.Integer(-1) if q == "-" else tex(q))
                report(same_fn(P, sp.expand(Q * sp.diff(g, x))), f"{label}: {m}")
                continue
            if "\\int" in m:
                lhs, rhs = T.split_top(clean(m), "=")
                _, info = integrals(lhs)
                F = tex(rhs)
                report(same_fn(sp.diff(F, u), info[0][0], u, need=3), f"{label}: {m}")
                continue
        except Exception as e:  # noqa: BLE001
            report(False, f"{label}: column item {m[:50]}", e)
            continue
        report(False, f"{label}: column item not understood", m)
    return g


SPLIT = re.compile(r'<div class="split"[^>]*>\s*<div>(.*?)</div><div style="border-left[^>]*>(.*?)</div></div>', re.S)


def check_region(html, label, need_in=None):
    """All split blocks (display + working column), then the remaining displays and inline maths."""
    n = 0
    for k, m in enumerate(SPLIT.finditer(html)):
        g = column(m.group(2), f"{label} split {k + 1}")
        for d in displays(m.group(1)):
            for ps in chains_of(d):
                if skip_chain(ps):
                    continue
                check_chain(ps, f"{label} split {k + 1}", g=g, need_in=need_in)
                n += 1
    rest = SPLIT.sub("", html)
    for d in displays(rest):
        for ps in chains_of(d):
            if skip_chain(ps):
                continue
            check_chain(ps, f"{label} display", need_in=None)
            n += 1
    for m in re.findall(r"\\\((.+?)\\\)", rest, flags=re.S):
        if "=" not in m or "\\le" in m or "<" in m:
            continue
        ps = [p.strip() for p in T.split_top(m, "=")]
        if skip_chain(ps):
            continue
        if ps[0] in ("u", "x", "du", "y", "y'", "k") or re.fullmatch(r"[a-z]", ps[0]):
            if len(ps) > 2:  # u = 2e^{ln 1/2} = 2 x 1/2 = 1: the computation after 'u =' must agree
                check_identity(ps[1:], f"{label} inline")
            continue
        if "\\frac{d}" in m or "\\dfrac{d}" in m:
            continue
        check_chain(ps, f"{label} inline")
    return n


# ------------------------------------------------------------------ blocks
def lesson_q(lesson, num):
    m = re.search(r'<div class="q"><span class="q-num">%s</span>(.*?)\{\{work' % num, lesson, re.S)
    return m.group(1)


def parts(block, marker):
    pat = r'<span class="pl">([a-j])</span>' if marker == "pl" else r"<b>([a-j])</b>"
    ms = list(re.finditer(pat, block))
    return {m.group(1): block[m.end():(ms[k + 1].start() if k + 1 < len(ms) else len(block))] for k, m in enumerate(ms)}


def answer_block(ans, num):
    m = re.search(r'<div class="a"><span class="an">%s</span><div class="ab">(.*?)</div></div>' % num, ans, re.S)
    if not m:
        report(False, f"answer block {num} missing")
        return ""
    return m.group(1)


def maths(s):
    return re.findall(r"\\\((.+?)\\\)", s, flags=re.S)


def check_value(label, q, a):
    """q: the integral printed in the lesson; a: the printed answer."""
    _, info = integrals(clean(q))
    f, lims, v = info[0]
    try:
        got = tex(a)
    except Exception as e:  # noqa: BLE001
        return report(False, label, f"parse {a}: {e}")
    if lims:
        true = definite(f, v, tex(lims[0]), tex(lims[1]))
        return report(num_eq(got, true), label, f"printed {a} ; exact {sp.nsimplify(true)}")
    return report(same_fn(sp.diff(got, v), f, v), label, f"d/d{v}({a}) vs {f}")


def concept_blocks(teach):
    idx = [m.start() for m in re.finditer(r"\{\{sec:teal:key:Concept \d", teach)]
    return [teach[a:b] for a, b in zip(idx, idx[1:] + [len(teach)])]


# ================================================================== main
def main():
    L, A = read("l12d.html"), read("a_12d.html")
    hw_at = L.index("{{sec:blue:pencil:Textbook homework")
    pp_at = L.index("{{sec:amber:clock:Past-paper homework")
    teach, ppL = L[:hw_at], L[pp_at:]
    tb_at = A.index('<div class="ans-sec">Textbook Homework</div>')
    ppa_at = A.index('<div class="ans-sec">Past-Paper Homework')
    lexA, tbA, ppA = A[:tb_at], A[tb_at:ppa_at], A[ppa_at:]

    print("== Lesson: concept boxes and Worked examples 14-19")
    n = check_region(teach, "lesson")
    report(n >= 8, f"lesson chains checked: {n}")
    for k in range(14, 20):
        once(teach, f"Worked example {k}</span>", f"Worked example {k}")
    # Examples 18 and 19 keep the book's lines; the bracket evaluation is in a titled tip after each
    once(teach, "Tip: the arithmetic in Example 18</div>", "tip after Example 18")
    once(teach, "Tip: the bracket in Example 19</div>", "tip after Example 19")
    ex18 = teach[teach.index("Worked example 18</span>"):teach.index("Tip: the arithmetic in Example 18")]
    ex19 = teach[teach.index("Worked example 19</span>"):teach.index("Tip: the bracket in Example 19")]
    report("\\big(0-0\\big)" not in ex18 and ex18.count("\\\\&=") == 4, "Example 18 has the book's 6 pieces only")
    report("(-1)^7-1^7" not in ex19 and ex19.count("\\\\&=") == 3, "Example 19 has the book's 5 pieces only")
    ntip = 0
    for d in displays(teach):
        if "\\Big[" in d and "\\int" not in d:
            for ps in chains_of(d):
                ntip += check_identity(ps, "tip bracket") is True
    report(ntip == 2, f"two tip bracket evaluations checked: {ntip}")

    print("== Lesson Examples C1-C4 (each question printed in its concept's demo / your turn)")
    cons = concept_blocks(teach)
    report(len(cons) == 4, f"four concepts: {len(cons)}")
    total = 0
    for k, blk in enumerate(re.findall(r'<div class="a"><span class="an">(C\d)</span><div class="ab">(.*?)</div></div>\s*(?=<div class="a">|<div class="ans-sec">|$)', lexA, re.S)):
        cname, body = blk
        ci = int(cname[1]) - 1
        demos = "".join(re.findall(r'<div class="ex (?:demo|attempt)">(.*?)\{\{work', cons[ci], re.S))
        total += check_region(body, cname, need_in=clean_q(demos))
    report(total == 12, f"answer chains in Lesson Examples: {total} (expect 12)")

    print("== Textbook homework (Exercise 12D)")
    q1 = lesson_q(L, 1)
    check_value("Ex12D Q1c", maths(q1)[0], maths(answer_block(tbA, 1))[0])
    q3 = lesson_q(L, 3)
    check_value("Ex12D Q3c", maths(q3)[0], maths(answer_block(tbA, 3))[0])
    for num, ps in ((2, "abcdef"), (4, "abcdef"), (5, "abcdefghij"), (7, "abcd"), (8, "abcd"), (11, "ab")):
        ql, al = parts(lesson_q(L, num), "pl"), parts(answer_block(tbA, num), "b")
        for p in ps:
            check_value(f"Ex12D Q{num}{p}", maths(ql[p])[0], maths(al[p])[0])
    # Q5: every given substitution is consistent with its integral (the u-integral has the same value)
    # Q6 area
    q6 = lesson_q(L, 6)
    yq = tex(re.search(r"\\\(y=(.+?)\\\)", q6).group(1))
    once(q6, r"\(x=1\)", "Q6 line x = 1")
    xs = [i / 400 for i in range(401)]
    report(all(float(yq.subs(x, t)) >= 0 for t in xs), "Q6 curve is not below the x-axis on [0, 1]")
    a6 = maths(answer_block(tbA, 6))[0]
    report(num_eq(tex(a6), definite(yq, x, 0, 1)), "Ex12D Q6 area", f"printed {a6}")
    # Q9
    q9 = parts(lesson_q(L, 9), "pl")
    a9 = parts(answer_block(tbA, 9), "b")
    grad = tex(maths(q9["a"])[0])
    pt = re.search(r"\\big\(0,(.+?)\\big\)", q9["a"]).group(1)
    ya = tex(maths(a9["a"])[0].split("=", 1)[1])
    report(same_fn(sp.diff(ya, x), grad) and num_eq(ya.subs(x, 0), tex(pt)), "Ex12D Q9a: y' is the gradient and y(0) matches", f"{ya}")
    ypp = tex(maths(q9["b"])[0].split("=", 1)[1])
    ab = maths(a9["b"])
    yp = tex(ab[0].split("=", 1)[1])
    yb = tex(ab[1].split("=", 1)[1])
    report(maths(q9["b"])[1:4] == ["x=0", "y'=1", "y=\\tfrac12"], "Ex12D Q9b initial conditions read", maths(q9["b"])[1:4])
    report(same_fn(sp.diff(yp, x), ypp) and num_eq(yp.subs(x, 0), 1), "Ex12D Q9b y' satisfies y'' and y'(0) = 1", f"{yp}")
    report(same_fn(sp.diff(yb, x), yp) and num_eq(yb.subs(x, 0), sp.Rational(1, 2)), "Ex12D Q9b y satisfies y' and y(0) = 1/2", f"{yb}")
    # Q10
    q10 = lesson_q(L, 10)
    ints = [m for m in maths(q10) if m.startswith("\\displaystyle\\int_")]
    a10 = maths(answer_block(tbA, 10))
    report(len(ints) == 2 and len(a10) == 2, f"Q10b two integrals and two answers: {len(ints)} {len(a10)}")
    for k in range(2):
        check_value(f"Ex12D Q10b({'i' * (k + 1)})", ints[k], a10[k])
    once(q10, r"\(\dfrac{d}{dx}(\sec x)=\sec x\tan x\)", "Q10a")
    report(sp.simplify(sp.diff(sp.sec(x), x) - sp.sec(x) * sp.tan(x)) == 0, "Q10a d/dx sec x = sec x tan x")
    # Q12, Q13
    check_value("Ex12D Q12", maths(lesson_q(L, 12))[1], maths(answer_block(tbA, 12))[0])
    q13 = parts(lesson_q(L, 13), "pl")
    a13 = parts(answer_block(tbA, 13), "b")
    i13 = maths(q13["a"])[1]
    check_value("Ex12D Q13a", i13, maths(a13["a"])[0])
    check_value("Ex12D Q13b (the same integral)", i13, maths(a13["b"])[0])
    idn = maths(q13["c"])[0].split("=")
    report(same_fn(tex(idn[0]), tex(idn[1]), need=5) and "0\\lt x\\lt1" in q13["c"], "Ex12D Q13c identity holds for 0 < x < 1")
    for t in (0.02, 0.3, 0.5, 0.7, 0.98):
        report(abs(float(tex(idn[0]).subs(x, t)) - float(tex(idn[1]).subs(x, t))) < 1e-12, f"Q13c at x = {t}")
    # Q14 show that
    m14 = maths(lesson_q(L, 14))[1]
    lhs, rhs = T.split_top(clean(m14.replace("\\displaystyle", "")), "=")
    _, info = integrals(lhs)
    f, lims, v = info[0]
    report(abs(float(definite(f, x, tex(lims[0]), tex(lims[1]))) - float(tex(rhs))) < 1e-12, "Ex12D Q14 printed value is true", f"{lims} {rhs}")
    g14 = x - 1 / x
    report(sp.simplify(g14.subs(x, tex(lims[1]))) == sp.sqrt(2) and g14.subs(x, 1) == 0, "Q14 u-limits are 0 and sqrt 2")
    # bands
    report(L.index("{{band:F}}") < L.index('q-num">1<') and L.index("{{band:D}}") < L.index('q-num">6<') < L.index("{{band:E}}") < L.index('q-num">14<'),
           "bands F 1-5, D 6-13, E 14")
    for k in range(1, 15):
        once(L[hw_at:pp_at], f'<span class="q-num">{k}</span>', f"Ex12D Q{k}")

    print("== Past papers")
    pps_L = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span><span class="mk">(\d+) marks?</span></div>(.*?)<div class="hint">(.*?)</div>', ppL, re.S)
    pps_A = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span></div>(.*?)(?=<div class="ppa">|$)', ppA, re.S)
    report(len(pps_L) == 8 and len(pps_A) == 8, f"8 questions in both files: {len(pps_L)} {len(pps_A)}")
    marks = sum(int(p[2]) for p in pps_L)
    intro = re.search(r"<b>Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks</b>", ppL)
    report(intro and int(intro.group(2)) == marks and 15 <= marks <= 22, f"marks total {marks} = intro {intro.group(2) if intro else None}")
    report(intro and int(intro.group(1)) == 5 * round(1.5 * marks / 5), f"time {intro.group(1) if intro else None} = 1.5 x {marks} rounded to 5")
    report(ppL.count('<div class="hint">') == 8, "one hint per question")
    for (nl, sl, mk, q, h), (na, sa, body) in zip(pps_L, pps_A):
        report(nl == na and sl == sa, f"PP {nl}: same number and label in both files", sl[:60])
        check_region(body, f"PP {na}", need_in=clean_q(q))
    # MC: only (B) has the value of the integral
    q1 = pps_L[0][3]
    opts = re.findall(r"<span>\((A|B|C|D)\)&ensp;\\\((.+?)\\\)</span>", q1)
    stem = maths(q1)[1]
    _, info = integrals(clean(stem))
    f, lims, v = info[0]
    true = definite(f, x, tex(lims[0]), tex(lims[1]))
    good = [k for k, o in opts if num_eq(piece(o)[0], true)]
    report(good == ["B"], f"PP1 only option B has the value of the integral: {good}")
    once(ppA, "<b>Answer (B).</b>", "PP1 answer (B)")
    once(maths(q1)[0], "u=\\tan x", "PP1 substitution")

    print()
    print(f"{NCHECK[0]} checks, {len(FAILS)} failures")
    if FAILS:
        print("FAILED:", *FAILS, sep="\n  ")
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    main()
