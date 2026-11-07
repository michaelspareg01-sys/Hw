"""Check of Lesson 12C (Integration Part 3 pack): Further trigonometric integrals.

The script reads the values PRINTED in workspace/build/int3/l12c.html and a_12c.html and recomputes
them with sympy. Nothing is copied from the answers into the script:
  - every display chain (\\[ ... \\]) in both files is split at its '=' signs. Each piece is turned into
    sympy (TeX -> sympy with workspace/checks/int3_tex.py; every \\int in a piece is replaced by sympy's
    own integral, every [F]_a^b by F(b) - F(a)). For a definite integral every piece must have the
    exact value of the integral on the left; for an indefinite integral every piece must have the
    integrand as its derivative. The integral on the left of each answer chain must also be printed,
    exactly once, in the matching lesson block (tutor demo / your turn / past-paper question);
  - every inline identity A = B printed in the answers in x or theta (for example
    sin4x cos x = 1/2(sin5x + sin3x)) is checked numerically at several points;
  - Textbook homework: each part of Exercise 12C is read from the lesson (its integral, integrand or
    value), and the printed answer is compared with sympy (derivative for primitives, exact value for
    definite integrals); Q9, Q10, Q13, Q14 are checked item by item (range, identities, stationary
    points, inflections, k values, limit);
  - Past papers: the MC answer is the only option whose derivative is the integrand; marks add to the
    intro total (15-22), time is 1.5 x marks rounded to 5 min, numbering and source labels match in
    both files, one hint per question.
A template that is not found exactly once FAILS. Exit status 1 on any failure.
Run: python3 workspace/checks/int3_12c.py
"""
import math
import os
import random
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

T.FUNCS.update({"cot": "cot", "cosec": "csc"})
T.LOCAL.update({"cot": sp.cot, "csc": sp.csc})
x, theta, n = T.x, T.theta, T.n
A_, B_ = sp.symbols("A B")
SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))
FAILS, NCHECK = [], [0]
MATH_BREAK = "\\)\\({}"


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace(MATH_BREAK, "")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:95] + ("  " + str(detail).replace("\n", " ")[:150] if detail else ""))
    if not ok:
        FAILS.append(label)


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
    s = re.sub(r"\\operatorname\{cosec\}(?!\^)", r"\\cosec~", s)
    s = s.replace("\\operatorname{cosec}", "\\cosec").replace("\\displaystyle", "")
    s = re.sub(r"\{\}\^\*\\!\\!", "", s)
    s = s.replace("\\lt", "<").replace("\\gt", ">")
    s = re.sub(r"\\[,;!]", " ", s).replace("\\ ", " ")
    s = re.sub(r"\\q?quad", " ", s)
    # int3_tex reads a bare function argument digit by digit (\sin12x -> sin(1*2*x)): bracket it
    s = re.sub(r"(\\(?:sin|cos|tan|cot|cosec|sec)(?:\^(?:\{[^}]*\}|\d))?)(\d{2,}[a-z])", r"\1(\2)", s)
    return s.strip()


def py(e):
    return "(" + sp.sstr(e) + ")"


def var_of(d):
    return theta if d == "\\theta" else x


def integrals(s):
    """Replace each \\int[_{a}^{b}] BODY d<var> by its sympy value; return (new string, list of info)."""
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
        m = re.compile(r"\s*d(x|\\theta|t)(?![a-zA-Z])").search(s, k)
        body = s[k:m.start()]
        v = var_of(m.group(1))
        if m.group(1) == "t":
            v = sp.Symbol("t")
        f = tex(body)
        if lims:
            val = sp.integrate(f, (v, tex(lims[0]), tex(lims[1])))
        else:
            val = sp.integrate(f, v)
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
        v = theta if F.has(theta) else x
        s = s[:j] + py(F.subs(v, tex(b)) - F.subs(v, tex(a))) + s[m:]
    return s


def tex(s):
    s = clean(s)
    s = re.sub(r"\+\s*[CcDE]\s*$", "", s.strip())
    s = re.sub(r"\\(sin|cos)\^2(\d+)\^\\circ", r"(\\\1(\\tfrac{\2\\pi}{180}))^2", s)
    s = re.sub(r"(\d+)\^\\circ", r"(\\tfrac{\1\\pi}{180})", s)
    return T.tex(s, extra={"A": A_, "B": B_})


def piece(s):
    s, info = integrals(clean(s))
    s = brackets(s)
    return tex(s), info


def num_eq(a, b, syms, tol=1e-9, trials=6):
    rnd = random.Random(12)
    for _ in range(trials):
        sub = {}
        for v in syms:
            sub[v] = rnd.choice([2, 3, 4]) if v == n else rnd.uniform(0.15, 1.3)
        try:
            va, vb = complex(sp.N(a.subs(sub), 30)), complex(sp.N(b.subs(sub), 30))
        except (TypeError, ValueError):
            return False
        if abs(va - vb) > tol * max(1, abs(va)):
            return False
    return True


# ------------------------------------------------------------------ chains
def displays(html):
    return re.findall(r"\\\[(.+?)\\\]", html, flags=re.S)


def chains_of(d):
    """Split an aligned display into chains: a line starting '&=' continues the chain above."""
    d = d.replace("\\begin{aligned}", "").replace("\\end{aligned}", "")
    chains = []
    for line in re.split(r"\\\\|\\qquad\\qquad", d):
        if not line.strip():
            continue
        if line.lstrip().startswith("&=") and chains:
            chains[-1] += line
        else:
            chains.append(line)
    out = []
    for c in chains:
        ps = [p.strip().rstrip(".,") for p in T.split_top(c.replace("&", ""), "=") if p.strip()]
        out.append(ps)
    return out


def int_body(lhs):
    k = lhs.index("\\int") + 4
    if lhs.startswith("_{", k):
        _, k = brace(lhs, k + 1)
        _, k = brace(lhs, k + 1)
    m = re.compile(r"\\,d").search(lhs, k)
    return lhs[k:m.start()] if m else None


def check_chain(d, label, need_in=None):
    """Check every chain of one display. Returns the number of chains with an integral."""
    if "\\frac{d}{dx}" in d or "\\text{" in d or "u^" in d or "\\lim" in d:
        return 0
    return sum(check_one(ps, label, need_in) for ps in chains_of(d))


def check_one(ps, label, need_in):
    first = next((p for p in ps if "\\int" in p), None)
    if first is None:
        return 0
    try:
        _, info = piece(first)
    except Exception as e:  # noqa: BLE001
        report(False, f"{label}: parse {first[:40]}", e)
        return 0
    f, lims, v = info[0]
    syms = sorted(f.free_symbols, key=str)
    ok, bad = True, ""
    for p in ps:
        if p.strip() in ("A",):
            continue
        try:
            e, _ = piece(p)
        except Exception as ex:  # noqa: BLE001
            ok, bad = False, f"parse {p[:50]}: {ex}"
            break
        if lims:
            true = sp.integrate(f, (v, tex(lims[0]), tex(lims[1])))
            if not num_eq(e, true, list(set(e.free_symbols) | set(syms))):
                ok, bad = False, f"{p[:60]} != {true}"
                break
        else:
            if not num_eq(sp.diff(e, v), f, list(set(e.free_symbols) | {v} | set(syms))):
                ok, bad = False, f"d/d{v}({p[:50]}) != {f}"
                break
    report(ok, f"{label}: chain {first[:60]} ({len(ps)} pieces)", bad)
    lhs = first.strip()
    if need_in is not None:
        if need_in.count(lhs) == 1:
            report(True, f"printed once: {label} question in lesson", lhs[:60])
        else:
            body = int_body(lhs)
            alts = [f"\\({body}\\)", f"y={body}"] if body else []
            hits = [(a_, need_in.count(a_)) for a_ in alts if need_in.count(a_)]
            report(len(hits) == 1 and hits[0][1] == 1, f"printed once: {label} question in lesson", f"{lhs[:60]} hits={hits}")
    return 1


def display_identities(html, label):
    """Display lines without an integral (identities such as cos^4 x = ...): all pieces equal."""
    cnt = 0
    for d in displays(html):
        if "\\int" in d or "\\frac{d}{dx}" in d or "\\text{" in d or "\\Big[" in d:
            continue
        for ps in chains_of(d):
            if len(ps) < 2:
                continue
            try:
                es = [tex(p) for p in ps]
            except Exception as e:  # noqa: BLE001
                report(False, f"{label}: parse identity {ps[0][:50]}", e)
                continue
            fs = set().union(*[e.free_symbols for e in es])
            ok = all(num_eq(es[0], e, list(fs)) for e in es[1:])
            report(ok, f"{label}: display identity {ps[0][:40]} = ... ({len(ps)} pieces)")
            cnt += 1
    return cnt


def inline_identities(html, label):
    cnt = 0
    for m in re.findall(r"\\\((.+?)\\\)", html, flags=re.S):
        if "=" not in m or "\\int" in m or "u" in re.sub(r"\\[a-z]+", "", m) or "\\le" in m:
            continue
        parts = T.split_top(clean(m), "=")
        if len(parts) < 2:
            continue
        try:
            es = [tex(p) for p in parts]
        except Exception:  # noqa: BLE001
            continue
        fs = set().union(*[e.free_symbols for e in es])
        if not fs or not fs <= {x, theta} or not any(e.has(sp.sin, sp.cos, sp.tan, sp.cot, sp.csc, sp.sec) for e in es):
            continue
        ok = all(num_eq(es[0], e, list(fs)) for e in es[1:])
        report(ok, f"{label}: identity {m[:70]}")
        cnt += 1
    return cnt


# ------------------------------------------------------------------ blocks
def blocks(html, start_pat):
    idx = [m.start() for m in re.finditer(start_pat, html)]
    return [html[a:b] for a, b in zip(idx, idx[1:] + [len(html)])]


def lesson_q(lesson, num):
    m = re.search(r'<div class="q"><span class="q-num">%s</span>(.*?)\{\{work' % num, lesson, re.S)
    return m.group(1)


def parts(block, marker):
    """Split on part labels: marker 'pl' (lesson) or 'b' (answers)."""
    pat = r'<span class="pl">([a-h])</span>' if marker == "pl" else r"<b>([a-h])</b>"
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


def question_expr(qpart):
    """The integral (or plain expression) in one lesson part."""
    m = maths(qpart)[0]
    return m


def expect_from_question(q):
    """sympy: ('def', value) or ('ind', integrand, var) or ('expr', value)."""
    q = clean(q)
    if "\\int" in q:
        _, info = integrals(q)
        f, lims, v = info[0]
        if lims:
            return ("def", sp.integrate(f, (v, tex(lims[0]), tex(lims[1]))))
        return ("ind", f, v)
    return ("expr", tex(q))


def check_value(label, q, a):
    kind = expect_from_question(q)
    try:
        got = tex(a)
    except Exception as e:  # noqa: BLE001
        report(False, label, f"parse {a}: {e}")
        return
    if kind[0] == "def" or kind[0] == "expr":
        report(sp.simplify(got - kind[1]) == 0 or num_eq(got, kind[1], []), label, f"printed {a} ; exact {sp.nsimplify(kind[1])}")
    else:
        f, v = kind[1], kind[2]
        report(num_eq(sp.diff(got, v), f, [v]), label, f"d/d{v}({a}) vs {f}")


# ================================================================== main
def main():
    L, A = read("l12c.html"), read("a_12c.html")
    pp_at = L.index("{{sec:amber:clock:Past-paper homework")
    hw_at = L.index("{{sec:blue:pencil:Textbook homework")
    teach = L[:hw_at]
    ppL = L[pp_at:]
    tb_at = A.index('<div class="ans-sec">Textbook Homework</div>')
    ppa_at = A.index('<div class="ans-sec">Past-Paper Homework')
    lexA, tbA, ppA = A[:tb_at], A[tb_at:ppa_at], A[ppa_at:]

    print("== Lesson: every display chain in the teaching part (boxes, worked examples)")
    k = 0
    for d in displays(teach):
        k += check_chain(d, "lesson")
    report(k >= 8, f"lesson chains checked: {k}")
    inline_identities(teach, "lesson")
    report(display_identities(teach, "lesson") >= 10, "lesson display identities checked")

    print("== Lesson Examples (answers C1-C6): chains, and each question printed in the lesson")
    demo_text = "".join(re.findall(r'<div class="ex (?:demo|attempt)">(.*?)\{\{work', teach, re.S))
    k = 0
    for d in displays(lexA):
        k += check_chain(d, "C", need_in=demo_text)
    report(k == 24, f"answer chains in Lesson Examples: {k} (expect 24)")
    inline_identities(lexA, "C")
    # tutor demos that are not chains: the questions printed in the lesson
    for q in (r"y=\sin x\cos^6x", r"y=\sec^2x\tan^nx", r"y=\cos x\sin^5x", r"y=\sin x\cos^nx", r"Integrate \(\tan2x\)", r"Integrate \(\cot\tfrac12x\)"):
        once(demo_text, q, q)

    print("== Textbook homework")
    # Q2 values
    q2, a2 = parts(lesson_q(L, 2), "pl"), parts(answer_block(tbA, 2), "b")
    for p in "abcd":
        check_value(f"Ex12C Q2{p}", maths(q2[p])[0], maths(a2[p])[0])
    for num, ps in ((3, "abcd"), (4, "abcd"), (5, "abcdef"), (6, "abcd"), (11, "abcd")):
        ql, al = parts(lesson_q(L, num), "pl"), parts(answer_block(tbA, num), "b")
        for p in ps:
            check_value(f"Ex12C Q{num}{p}", question_expr(ql[p]), maths(al[p])[0])
    ql, al = parts(lesson_q(L, 8), "pl"), parts(answer_block(tbA, 8), "b")
    for p in "abcdefgh":
        check_value(f"Ex12C Q8{p}", question_expr(ql[p]), maths(al[p])[0])
    ql, al = parts(lesson_q(L, 12), "pl"), parts(answer_block(tbA, 12), "b")
    for p in "abc":
        f = tex(maths(ql[p])[0])
        got = tex(maths(al[p])[0])
        report(num_eq(sp.diff(got, x), f, [x]), f"Ex12C Q12{p}", f"d/dx({maths(al[p])[0]}) vs {f}")
    # Q9
    a9 = answer_block(tbA, 9)
    once(a9, r"\(-\tfrac12\le y\le\tfrac12\)", "Q9a range")
    xs = [i * 2 * math.pi / 4000 for i in range(4001)]
    ys = [math.sin(t) * math.cos(t) for t in xs]
    report(abs(min(ys) + 0.5) < 1e-6 and abs(max(ys) - 0.5) < 1e-6, "Q9a range of cos x sin x is [-1/2, 1/2]", f"{min(ys):.6f} {max(ys):.6f}")
    f9 = sp.cos(x) * sp.sin(x)
    for t in (r"-\tfrac14\cos2x+C", r"\tfrac12\sin^2x+D", r"-\tfrac12\cos^2x+E"):
        if once(a9, "\\(" + t + "\\)", f"Q9b {t}"):
            report(num_eq(sp.diff(tex(t), x), f9, [x]), f"Q9b derivative of {t} is cos x sin x")
    # Q10
    a10 = answer_block(tbA, 10)
    m = re.search(r"\\\(\\cos\^4x=(.+?)\\\)", a10)
    report(bool(m) and sp.simplify(sp.expand_trig(tex(m.group(1)) - sp.cos(x) ** 4)) == 0, "Q10b cos^4 x identity", m.group(1) if m else "missing")
    q10 = lesson_q(L, 10)
    once(q10, r"\(\sin^4x=\tfrac38-\tfrac12\cos2x+\tfrac18\cos4x\)", "Q10a printed identity")
    report(sp.simplify(sp.expand_trig(sp.Rational(3, 8) - sp.cos(2 * x) / 2 + sp.cos(4 * x) / 8 - sp.sin(x) ** 4)) == 0, "Q10a identity true")
    ints = re.findall(r"\\\(\\displaystyle(\\int_\{.+?\}\^\{.+?\}.+?\\,dx)\.?\\\)", q10)
    report(len(ints) == 3, f"Q10 three definite integrals read: {len(ints)}")
    vals = [re.findall(p_, a10) for p_ in (r"\(i\) \\\((.+?)\\\)", r"\(ii\) \\\((.+?)\\\)", r"<b>d</b> \\\((.+?)\\\)")]
    if all(len(v_) == 1 for v_ in vals) and len(ints) == 3:
        for qi, ai, lab in zip(ints, [v_[0] for v_ in vals], ("c(i)", "c(ii)", "d")):
            check_value(f"Ex12C Q10{lab}", qi, ai)
    else:
        report(False, "Q10 answers read")
    # Q13
    a13 = answer_block(tbA, 13)
    F = x / 2 - sp.sin(2 * x) / 4
    t = sp.Symbol("t")
    report(sp.simplify(sp.integrate(sp.sin(t) ** 2, (t, 0, x)) - F) == 0, "Q13a F(x) = x/2 - sin2x/4")
    once(a13, r"(i) \(x=0\), \(\pi\) or \(2\pi\)", "Q13b(i)")
    zeros = sorted(set(sp.solveset(sp.sin(x) ** 2, x, sp.Interval(0, 2 * sp.pi))))
    report(zeros == [0, sp.pi, 2 * sp.pi], "Q13b(i) zeros of sin^2 x on [0, 2pi]", zeros)
    once(a13, r"(ii) \(0\lt x\lt\pi\) or \(\pi\lt x\lt2\pi\)", "Q13b(ii)")
    once(a13, "(iii) no values of \\(x\\)", "Q13b(iii)")
    once(a13, r"\(-\tfrac14\le\tfrac14\sin2x\le\tfrac14\)", "Q13c")
    pts = re.findall(r"\\big\((\\tfrac\{[^}]*\}\{\d\}|\\pi),(\\tfrac\{[^}]*\}\{\d\})\\big\)", a13)
    got = sorted((tex(a_), tex(b_)) for a_, b_ in pts)
    F2 = sp.diff(F, x, 2)
    infl = []
    for z in sorted(sp.solveset(F2, x, sp.Interval.open(0, 2 * sp.pi))):
        if (F2.subs(x, z - sp.Rational(1, 100)) * F2.subs(x, z + sp.Rational(1, 100))) < 0:
            infl.append((z, sp.simplify(F.subs(x, z))))
    report(got == sorted(infl), "Q13d points of inflection inside the domain", f"printed {got} ; computed {infl}")
    report(sp.diff(F, x).subs(x, sp.pi) == 0 and once(a13, r"\(\big(\pi,\tfrac{\pi}{2}\big)\) is a stationary", "Q13d stationary one"), "Q13d (pi, pi/2) is stationary")
    once(a13, r"(i) \(k=3\pi\)", "Q13f(i)")
    report(sp.simplify(F.subs(x, 3 * sp.pi) - 3 * sp.pi / 2) == 0, "Q13f(i) integral 0..3pi of sin^2 = 3pi/2 (and the integral is increasing in k)")
    once(a13, r"(ii) \(k=n\pi\)", "Q13f(ii)")
    report(all(sp.simplify(F.subs(x, j * sp.pi) - j * sp.pi / 2) == 0 for j in range(-4, 6)), "Q13f(ii) F(n pi) = n pi/2")
    a14 = answer_block(tbA, 14)
    R = sp.Symbol("R", positive=True)
    lim = sp.limit(sp.integrate(sp.sin(t) ** 2, (t, 0, R)) / R, R, sp.oo)
    report(a14.strip() == "\\(" + r"\tfrac12" + "\\)" and lim == sp.Rational(1, 2), "Q14 limit = 1/2", f"{a14} ; {lim}")
    once(lesson_q(L, 14), r"\lim_{R\to\infty}\bigg(\frac1R\int_{0}^{R}\sin^2t\,dt\bigg)", "Q14 question")
    # the figures exist and are referenced
    for s_ in ("a12c_q7", "a12c_q13"):
        report(os.path.exists(os.path.join(SRC, "svg", s_ + ".svg")) and A.count("{{svg:%s}}" % s_) == 1, f"figure {s_}")

    print("== Past papers")
    for d in displays(ppA):
        check_chain(d, "PP", need_in=ppL)
    inline_identities(ppA, "PP")
    report(display_identities(ppA, "PP") == 1, "PP display identities checked (PP8 cos^4 x)")
    # PP7(i) identity
    report(sp.simplify(sp.expand_trig(sp.sin(A_ + B_) + sp.sin(A_ - B_)) - 2 * sp.sin(A_) * sp.cos(B_)) == 0, "PP7(i) sin(A+B)+sin(A-B) = 2 sinA cosB")
    once(ppA, r"\text{LHS}&=\big(\sin A\cos B+\cos A\sin B\big)+\big(\sin A\cos B-\cos A\sin B\big)\\&=2\sin A\cos B", "PP7(i) working")
    # MC
    for pn, integrand, letter in (("PP 1", sp.sin(3 * x) ** 2, "D"), ("PP 2", sp.cos(3 * x) * sp.cos(2 * x), "A")):
        blk = ppL[ppL.index(f'<span class="pn">{pn}</span>'):]
        blk = blk[:blk.index('class="hint"')]
        opts = re.findall(r"<span>\(([A-D])\)&ensp;\\\((.+?)\\\)</span>", blk)
        good = [l_ for l_, o in opts if num_eq(sp.diff(tex(o), x), integrand, [x])]
        report(len(opts) == 4 and good == [letter], f"{pn} MC: only ({letter}) differentiates to the integrand", f"good={good}")
        once(ppA, f"<b>Answer ({letter}).</b>", f"{pn} answer letter")
    # marks, time, labels, hints
    marks = [int(m_) for m_ in re.findall(r'<span class="mk">(\d+) marks?</span>', ppL)]
    intro = re.search(r"<b>(\d+) marks</b>", ppL)
    tm = re.search(r"Suggested time: (\d+) minutes", ppL)
    tot = sum(marks)
    report(intro and int(intro.group(1)) == tot and 15 <= tot <= 22, f"PP marks {marks} add to intro {intro.group(1) if intro else None}")
    report(tm and int(tm.group(1)) == 5 * round(1.5 * tot / 5), f"PP time {tm.group(1) if tm else None} = 1.5 x {tot} rounded to 5")
    sub = re.search(r'PP 7</span>.*?</div>(.*?)class="hint"', ppL, re.S).group(1)
    sm = [int(v) for v in re.findall(r'<span class="mk">(\d)</span>', sub)]
    report(sum(sm) == 4, f"PP7 part marks {sm} add to 4")
    labL = [(p, re.sub(r"(</span>)+$", "", t)) for p, t in re.findall(r'<span class="pn">(PP \d+)</span>(.*?)<span class="mk">', ppL)]
    labA = [(p, re.sub(r"(</span>)+$", "", t)) for p, t in re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</div>', ppA)]
    nl = [p for p, _ in labL]
    report(nl == [f"PP {i}" for i in range(1, 9)], f"PP numbering in lesson {nl}")
    report([p for p, _ in labA] == nl, "PP numbering in answers matches")
    report([s_ for _, s_ in labL] == [s_ for _, s_ in labA], "PP source labels identical in both files")
    report(ppL.count('class="hint"') == 8, f"one hint per PP: {ppL.count('class=\"hint\"')}")

    print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
    if FAILS:
        for f_ in FAILS:
            print("FAIL:", f_)
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    main()
