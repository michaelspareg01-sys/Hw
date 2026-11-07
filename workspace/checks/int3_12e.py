"""Check of Lesson 12E (Integration Part 3 pack): Further integration by substitution.

The script reads the values PRINTED in workspace/build/int3/l12e.html and a_12e.html and recomputes
them independently (sympy for algebra and derivatives, mpmath numerical quadrature for definite
integrals). Nothing is copied from the answers into the script:
  - every display chain (\\[ ... \\]) with an integral, in the lesson and in the answers, is split at its
    '=' signs and each piece is turned into sympy (TeX -> sympy with workspace/checks/int3_tex.py).
    Definite chains: every piece must have the value of the integral on the left, computed by
    numerical quadrature (each \\int in a piece is integrated numerically, each [F]_a^b becomes
    F(b) - F(a)). Indefinite chains: the substitution x = g(u) is read from the printed side column
    ('Let x = ...'), and every piece in x must differentiate to the integrand f(x), every piece in u to
    f(g(u)) g'(u), and every integral piece must have that integrand;
  - every side column is checked: dx = g'(u) du, the radical line (for example sqrt(1-x) = u) at
    sample points of the u-interval used, and each 'When x = A, u = B' line (g(B) = A exactly);
  - the teaching derivations (x = 1 - u^2, x = a sin u, the four Pythagorean substitutions, returning
    to x, the segment formula) are checked by substituting the printed substitution;
  - inline equalities whose pieces are numbers (for example sin u = 3sqrt2/6 = 1/sqrt2) are checked;
  - Textbook homework: each printed answer of Exercise 12E is compared with the integral printed in
    the lesson (derivative for primitives, quadrature for definite integrals), plus Q10 (f' and f(3)),
    Q11 (area) and Q13;
  - Past papers: MC answers (only the keyed option has the value of the integral), PP 3(i) domain,
    marks add to the intro total (15-22), time is 1.5 x marks rounded to 5 min, numbering and source
    labels match in both files, one hint per question.
A template that is not found exactly once FAILS. Exit status 1 on any failure.
Run: python3 workspace/checks/int3_12e.py
"""
import os
import random
import re
import sys

import mpmath as mp
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

x, u, theta = T.x, T.u, T.theta
y = sp.Symbol("y")
a_ = sp.Symbol("a", positive=True)
r_ = sp.Symbol("r", positive=True)
T.LOCAL.update({"y": y, "a": a_, "r": r_})
SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))
FAILS, NCHECK = [], [0]
MATH_BREAK = "\\)\\({}"
mp.mp.dps = 30
VARS = {"x": x, "u": u, "\\theta": theta, "y": y}


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
    assert s[i] == "{", s[i:i + 20]
    d = 0
    for j in range(i, len(s)):
        d += s[j] == "{"
        d -= s[j] == "}"
        if d == 0:
            return s[i + 1:j], j + 1
    raise ValueError("unbalanced " + s[i:i + 30])


def token(s, i):
    """One TeX argument starting at s[i]: {...}, a command such as \\pi, or one character."""
    if s[i] == "{":
        return brace(s, i)
    m = re.match(r"\\[A-Za-z]+", s[i:])
    if m:
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def R(t):
    """An exact sample point."""
    return sp.Rational(str(t))


def clean(s):
    s = s.replace("\\displaystyle", "")
    s = s.replace("\\lt", "<").replace("\\gt", ">")
    # PP 3 prints dx in the numerator, as in the paper
    s = s.replace("\\frac{2x\\,dx}{\\sqrt{1-x^2}}", "\\frac{2x}{\\sqrt{1-x^2}}\\,dx")
    s = re.sub(r"\\sqrt\[3\]\{([^{}]*)\}", r"(\1)^{\\frac13}", s)
    s = re.sub(r"\\sqrt\s+([a-z])", r"\\sqrt{\1}", s)
    s = re.sub(r"\\[,;!]", " ", s).replace("\\ ", " ")
    s = re.sub(r"\\q?quad", " ", s)
    # int3_tex reads a bare multi-digit function argument digit by digit (\sin12x -> sin(1*2*x)): bracket it
    s = re.sub(r"(\\(?:sin|cos|tan|sec)(?:\^(?:\{[^}]*\}|\d))?)(\d{2,}[a-z])", r"\1(\2)", s)
    return s.strip()


def tex(s, extra=None):
    s = clean(s)
    s = re.sub(r"\+\s*[CcDE]\s*$", "", s.strip())
    return T.tex(s, extra=extra)


def var_sym(d):
    return VARS[d]


INT_END = re.compile(r"\s*d(x|u|y|\\theta)(?![a-zA-Z])")


def integrals(s):
    """Replace each \\int[_{a}^{b}] BODY d<v>: definite -> its numerical value (as a Float); indefinite ->
    an unknown function Qk(v). Returns (new string, [(body, lims, var, name)])."""
    out, info, i = "", [], 0
    while True:
        j = s.find("\\int", i)
        if j < 0:
            return out + s[i:], info
        out += s[i:j]
        k = j + 4
        lims = None
        if s.startswith("_", k):
            a, k = token(s, k + 1)
            assert s[k] == "^", s[k:k + 10]
            b, k = token(s, k + 1)
            lims = (a, b)
        m = INT_END.search(s, k)
        body = s[k:m.start()]
        v = var_sym(m.group(1))
        f = tex(body)
        name = f"Q{len(info)}"
        if lims:
            val = quad(f, v, tex(lims[0]), tex(lims[1]))
            out += "(" + mp.nstr(val, 28) + ")"
        else:
            out += f"{name}({sp.sstr(v)})"
        info.append((f, lims, v, name))
        i = m.end()


def quad(f, v, lo, hi):
    g = sp.lambdify(v, f, "mpmath")
    lo, hi = mp.mpf(sp.N(lo, 40)), mp.mpf(sp.N(hi, 40))
    return mp.re(mp.quad(g, [lo, hi]))


def brackets(s):
    """Replace \\Big[F\\Big]_{a}^{b} by F(b) - F(a)."""
    while "\\Big[" in s:
        j = s.index("\\Big[")
        k = s.index("\\Big]", j)
        F = tex(s[j + 5:k])
        m = k + 5
        assert s[m] == "_", s[m:m + 10]
        a, m = token(s, m + 1)
        assert s[m] == "^"
        b, m = token(s, m + 1)
        fs = [v for v in (x, u, theta, y) if F.has(v)]
        assert len(fs) == 1, (F, fs)
        v = fs[0]
        s = s[:j] + "(" + sp.sstr(F.subs(v, tex(b)) - F.subs(v, tex(a))) + ")" + s[m:]
    return s


def piece(s):
    s2, info = integrals(clean(s))
    s2 = brackets(s2)
    extra = {nm: sp.Function(nm) for _, _, _, nm in info}
    return tex(s2, extra=extra), info


def close(a, b, tol=1e-12):
    try:
        a, b = complex(a), complex(b)
    except TypeError:
        return False
    return abs(a - b) <= tol * max(1, abs(a), abs(b))


# ------------------------------------------------------------------ side columns
def parse_side(side):
    """Return dict: g (sympy in w), w, dx (sympy), rad (list of (lhs, rhs)), lims (list of (A, B))."""
    side = re.sub(r"\s+", " ", side.replace("<br>", " "))
    m = re.search(r"Let \\\(x=(.+?)\\\)\.", side)
    if not m:
        return None
    g = tex(m.group(1))
    w = theta if g.has(theta) else (u if g.has(u) else None)
    d = {"g": g, "w": w, "rad": [], "lims": [], "dx": None, "text": side}
    m = re.search(r"Then \\\(dx=(.+?)\\,d(u|\\theta)\\\)", side)
    if m:
        d["dx"] = tex(m.group(1))
    for m in re.finditer(r"and \\\((.+?)=(.+?)\\\)", side):
        d["rad"].append((m.group(1), m.group(2)))
    for m in re.finditer(r"[Ww]hen \\\(x=(.+?)\\\), \\\((?:u|\\theta)=(.+?)\\\)", side):
        d["lims"].append((tex(m.group(1)), tex(m.group(2))))
    return d


def samples_w(sd):
    """Sample points of the substitution variable: inside the interval of the printed limits if there
    are two, otherwise inside (0.2, 1.2) (every indefinite substitution here is valid there)."""
    if len(sd["lims"]) == 2:
        b1, b2 = sorted(sp.N(B, 40) for _, B in sd["lims"])
    else:
        b1, b2 = R(0.2), R(1.2)
    return [b1 + (b2 - b1) * R(t) for t in (0.13, 0.31, 0.5, 0.67, 0.88)]


def check_side(sd, label):
    g, w = sd["g"], sd["w"]
    report(w is not None and sd["dx"] is not None and sp.simplify(sd["dx"] - sp.diff(g, w)) == 0,
           f"{label}: dx = g'(w) dw for x = {g}", f"printed dx = {sd['dx']}")
    for lhs, rhs in sd["rad"]:
        L, R = tex(lhs), tex(rhs)
        ok = all(close(sp.N(L.subs(x, g.subs(w, t)), 30), sp.N(R.subs(w, t), 30), 1e-20) for t in samples_w(sd))
        report(ok, f"{label}: {lhs} = {rhs} when x = {g}")
    for A, B in sd["lims"]:
        report(sp.simplify(g.subs(w, B) - A) == 0, f"{label}: x = {A} gives {w} = {B}", f"g(B) = {sp.simplify(g.subs(w, B))}")


# ------------------------------------------------------------------ chains
def displays_with_side(html):
    """List of (display, side-column text or None) in order of appearance."""
    out = []
    pos = 0
    pair = re.compile(r'<div class="split"[^>]*><div>\s*\\\[((?:(?!\\\]).)+)\\\]\s*</div><div style="border-left[^"]*">\s*<p style="line-height:2.3">(.+?)</p>', re.S)
    paired = {m.start(1): (m.group(1), m.group(2)) for m in pair.finditer(html)}
    # answers: the substitution may also be printed as a paragraph just before the display
    first = re.compile(r'<p class="subst">(.+?)</p>\s*\\\[((?:(?!\\\]).)+)\\\]', re.S)
    paired.update({m.start(2): (m.group(2), m.group(1)) for m in first.finditer(html)})
    for m in re.finditer(r"\\\[(.+?)\\\]", html, flags=re.S):
        st = m.start(1)
        out.append(paired.get(st, (m.group(1), None)))
        pos = m.end()
    return out


def chains_of(d):
    d = d.replace("\\begin{aligned}", "").replace("\\end{aligned}", "")
    chains = []
    for line in re.split(r"\\\\", d):
        if not line.strip():
            continue
        if line.lstrip().startswith("&=") and chains:
            chains[-1] += line
        else:
            chains.append(line)
    return [[p.strip().rstrip(".,") for p in T.split_top(c.replace("&", ""), "=") if p.strip()] for c in chains]


def check_display(d, side, label, need_in=None):
    """Check the integral chains of one display. Returns the number of chains with an integral."""
    sd = parse_side(side) if side else None
    if sd:
        check_side(sd, label + " side")
    n = 0
    for ps in chains_of(d):
        first = next((p for p in ps if "\\int" in p), None)
        if first is None:
            continue
        n += 1
        check_chain(ps, first, sd, label)
        if need_in is not None:
            lhs = ps[0].strip()
            k = need_in.count(lhs)
            if k != 1:
                lhs2 = lhs.replace("\\frac{2x}{\\sqrt{1-x^2}}\\,dx", "\\frac{2x\\,dx}{\\sqrt{1-x^2}}")
                k = need_in.count(lhs2)
            # PP 5 prints its integral in both parts (i) and (ii)
            twice = lhs == "\\int_0^1\\sqrt{\\frac{1-x}{1+x}}\\,dx"
            report(k == (2 if twice else 1), f"printed {'twice' if twice else 'once'}: {label} question in lesson", f"{lhs[:70]} found {k}")
    return n


def check_chain(ps, first, sd, label):
    try:
        e0, info = piece(first)
    except Exception as ex:  # noqa: BLE001
        report(False, f"{label}: parse {first[:50]}", ex)
        return
    f, lims, v, _ = info[0]
    ok, bad = True, ""
    if lims:
        true = quad(f, v, tex(lims[0]), tex(lims[1]))
        for p in ps:
            try:
                e, _ = piece(p)
                val = sp.N(e, 30)
            except Exception as ex:  # noqa: BLE001
                ok, bad = False, f"parse {p[:50]}: {ex}"
                break
            if not close(val, true, 1e-15):
                ok, bad = False, f"{p[:60]} = {val} != {mp.nstr(true, 15)}"
                break
        report(ok, f"{label}: definite chain {first[:60]} ({len(ps)} pieces)", bad or f"value {mp.nstr(true, 12)}")
        return
    # indefinite: needs the substitution unless every piece is in x
    if sd:
        g, w = sd["g"], sd["w"]
        ws = samples_w(sd)
    else:
        g, w, ws = None, None, None
    xs = [R(t) for t in (0.3, 0.55, 0.8, 1.15, 1.6, 2.3, 2.9, 3.4, 4.6)]
    for p in ps:
        try:
            e, inf = piece(p)
        except Exception as ex:  # noqa: BLE001
            ok, bad = False, f"parse {p[:50]}: {ex}"
            break
        subs_d = {}
        for (fb, _, vb, nm) in inf:
            subs_d[sp.Derivative(sp.Function(nm)(vb), vb)] = fb
        fs = e.free_symbols - {sp.Symbol("C")}
        if x in fs or not fs:
            de = sp.diff(e, x).subs(subs_d).doit()
            pts = [t for t in ((g.subs(w, s_) for s_ in ws) if g is not None else xs)]
            good = 0
            for t in pts:
                fv, dv = sp.N(f.subs(x, t), 30), sp.N(de.subs(x, t), 30)
                if fv.is_real and dv.is_real:
                    good += 1
                    if not close(fv, dv, 1e-18):
                        ok, bad = False, f"d/dx({p[:40]}) != f at x={t}"
            if good < 3:
                ok, bad = False, f"too few sample points for {p[:40]}"
        elif w is not None and fs <= {w}:
            target = f.subs(x, g) * sp.diff(g, w)
            de = sp.diff(e, w).subs(subs_d).doit()
            for t in ws:
                if not close(sp.N(de.subs(w, t), 30), sp.N(target.subs(w, t), 30), 1e-18):
                    ok, bad = False, f"d/d{w}({p[:40]}) != f(g)g' at {t}"
        else:
            ok, bad = False, f"no substitution for {p[:40]}"
        if not ok:
            break
    report(ok, f"{label}: indefinite chain {first[:60]} ({len(ps)} pieces)", bad)


def inline_numbers(html, label):
    """Inline equalities: all pieces that are plain numbers must be equal."""
    cnt = 0
    for m in re.findall(r"\\\((.+?)\\\)", html, flags=re.S):
        if "=" not in m or "\\int" in m or "\\le" in m or "\\ge" in m or "<" in m or ">" in m:
            continue
        parts = T.split_top(m, "=")
        if len(parts) < 2:
            continue
        vals = []
        for p in parts:
            try:
                e = tex(p)
            except Exception:  # noqa: BLE001
                continue
            if not e.free_symbols:
                vals.append((p, e))
        if len(vals) < 2:
            continue
        ok = all(close(sp.N(vals[0][1], 30), sp.N(e, 30), 1e-20) for _, e in vals[1:])
        report(ok, f"{label}: inline numbers {m[:70]}")
        cnt += 1
    return cnt


def inline_identities(html, label):
    """Inline identities in one variable (theta or u alone, or x alone): checked at sample points."""
    cnt = 0
    for m in re.findall(r"\\\((.+?)\\\)", html, flags=re.S):
        if "=" not in m or "\\int" in m or "\\le" in m or "\\ge" in m or "<" in m or ">" in m:
            continue
        parts = T.split_top(m, "=")
        if len(parts) < 2:
            continue
        try:
            es = [tex(p) for p in parts]
        except Exception:  # noqa: BLE001
            continue
        fs = set().union(*[e.free_symbols for e in es])
        if len(fs) != 1 or any(not e.free_symbols for e in es):
            continue
        v = fs.pop()
        if v not in (x, theta, u):
            continue
        if not any(e.has(sp.sin, sp.cos, sp.tan, sp.sec, sp.log) for e in es):
            continue
        ok = all(close(sp.N(es[0].subs(v, t), 30), sp.N(e.subs(v, t), 30), 1e-20) for e in es[1:] for t in (R(0.21), R(0.47), R(0.73)))
        report(ok, f"{label}: identity {m[:70]}")
        cnt += 1
    return cnt


# ------------------------------------------------------------------ homework helpers
def lesson_q(lesson, num):
    m = re.search(r'<div class="q"><span class="q-num">%s</span>(.*?)\{\{work' % num, lesson, re.S)
    return m.group(1)


def parts(block, marker):
    pat = r'<span class="pl">([a-h])</span>' if marker == "pl" else r"<b>([a-h])</b>"
    ms = list(re.finditer(pat, block))
    return {m.group(1): block[m.end():(ms[k + 1].start() if k + 1 < len(ms) else len(block))] for k, m in enumerate(ms)}


def romans(block):
    ms = list(re.finditer(r"\((i|ii|iii|iv|v|vi)\) ", block))
    return {m.group(1): block[m.end():(ms[k + 1].start() if k + 1 < len(ms) else len(block))] for k, m in enumerate(ms)}


def answer_block(ans, num):
    m = re.search(r'<div class="a"><span class="an">%s</span><div class="ab">(.*?)</div></div>' % num, ans, re.S)
    if not m:
        report(False, f"answer block {num} missing")
        return ""
    return m.group(1)


def maths(s):
    return re.findall(r"\\\((.+?)\\\)", s, flags=re.S)


def check_value(label, qint, ans):
    """qint: TeX of an integral printed in the lesson; ans: TeX of the printed answer."""
    try:
        _, info = integrals(clean(qint))
        f, lims, v, _ = info[0]
        got = tex(ans)
    except Exception as e:  # noqa: BLE001
        report(False, label, f"parse: {e}")
        return
    if lims:
        true = quad(f, v, tex(lims[0]), tex(lims[1]))
        report(close(sp.N(got, 30), true, 1e-15), label, f"printed {ans} ; quadrature {mp.nstr(true, 15)}")
        return
    d = sp.diff(got, v)
    cands = [R(t) for t in (-4.7, -3.3, -2.6, -1.7, -0.9, -0.6, -0.3, 0.2, 0.35, 0.45, 0.7, 1.3, 1.8, 2.4, 3.6, 4.4, 5.5, 7.1)]
    good, ok = 0, True
    for t in cands:
        fv, dv = sp.N(f.subs(v, t), 30), sp.N(d.subs(v, t), 30)
        if fv.is_real and dv.is_real and fv.is_finite and dv.is_finite:
            good += 1
            ok &= close(fv, dv, 1e-18)
    report(ok and good >= 3, label, f"d/d{v}({ans}) vs {f} at {good} points")


def stem_integral(q):
    m = re.search(r"\\\((?:[IJ]=)?\\displaystyle(\\int.+?d(?:x|u|\\theta))\\\)", q)
    return m.group(1)


# ================================================================== main
def main():
    L, A = read("l12e.html"), read("a_12e.html")
    hw_at = L.index("{{sec:blue:pencil:Textbook homework")
    pp_at = L.index("{{sec:amber:clock:Past-paper homework")
    teach, ppL = L[:hw_at], L[pp_at:]
    tb_at = A.index('<div class="ans-sec">Textbook Homework</div>')
    ppa_at = A.index('<div class="ans-sec">Past-Paper Homework')
    lexA, tbA, ppA = A[:tb_at], A[tb_at:ppa_at], A[ppa_at:]

    print("== Lesson: worked examples and boxes (chains and side columns)")
    k = 0
    for d, side in displays_with_side(teach):
        k += check_display(d, side, "lesson")
    report(k == 3, f"lesson integral chains checked: {k} (Examples 20, 21a and 21b)")
    # Example 21(b) by the segment formula
    m = re.search(r"\\int_\{3\\sqrt2\}\^\{6\}\\sqrt\{36-x\^2\}\\,dx&=\\tfrac12\\times\\tfrac12\\times6\^2\\big\(\\tfrac\{\\pi\}\{2\}-\\sin\\tfrac\{\\pi\}\{2\}\\big\)\\\\&=\\tfrac14\\times36\\times\\big\(\\tfrac\{\\pi\}\{2\}-1\\big\)\\\\&=9\\big\(\\tfrac\{\\pi\}\{2\}-1\\big\)", teach)
    report(bool(m), "Example 21(b) chain printed")
    seg = lambda R, al: R ** 2 * (al - sp.sin(al)) / 2
    report(sp.simplify(seg(6, sp.pi / 2) / 2 - 9 * (sp.pi / 2 - 1)) == 0 and close(quad(sp.sqrt(36 - x ** 2), x, 3 * sp.sqrt(2), 6), sp.N(9 * (sp.pi / 2 - 1), 30), 1e-20),
           "Example 21(b): half segment = 9(pi/2 - 1) = integral")
    # teaching derivations
    once(teach, r"\begin{aligned}\frac{dx}{du}&=-2u\\dx&=-2u\,du\end{aligned}", "x = 1 - u^2: dx")
    once(teach, r"\begin{aligned}1-x&=1-(1-u^2)\\&=u^2\\\sqrt{1-x}&=u\end{aligned}", "x = 1 - u^2: sqrt(1 - x)")
    report(sp.diff(1 - u ** 2, u) == -2 * u and sp.expand(1 - (1 - u ** 2)) == u ** 2, "x = 1 - u^2: dx/du = -2u and 1 - x = u^2")
    once(teach, r"\begin{aligned}a^2-x^2&=a^2-a^2\sin^2u\\&=a^2(1-\sin^2u)\\&=a^2\cos^2u,\end{aligned}", "x = a sin u derivation")
    chain = [tex(p) for p in ("a^2-x^2", "a^2-a^2\\sin^2u", "a^2(1-\\sin^2u)", "a^2\\cos^2u")]
    report(all(sp.simplify(c.subs(x, a_ * sp.sin(u)) - chain[-1]) == 0 for c in chain), "x = a sin u: a^2 - x^2 = a^2 cos^2 u (every line)")
    once(teach, r"\[\text{segment}=\tfrac12r^2\theta-\tfrac12r^2\sin\theta=\tfrac12r^2(\theta-\sin\theta).\]", "segment formula")
    th = sp.Symbol("t", positive=True)
    report(sp.simplify(sp.Rational(1, 2) * r_ ** 2 * th - sp.Rational(1, 2) * r_ * r_ * sp.sin(th) - r_ ** 2 * (th - sp.sin(th)) / 2) == 0, "segment = sector - triangle")
    m = re.search(r"x=a\\sin\\theta:&\\quad (.+?)\\\\x=a\\cos\\theta:&\\quad (.+?)\\\\x=a\\tan\\theta:&\\quad (.+?)\\\\x=a\\sec\\theta:&\\quad (.+?)\\end", teach)
    report(bool(m), "four Pythagorean substitutions printed")
    if m:
        for sub, line in zip((a_ * sp.sin(theta), a_ * sp.cos(theta), a_ * sp.tan(theta), a_ / sp.cos(theta)), m.groups()):
            es = [tex(p) for p in T.split_top(line, "=")]
            ok = len(es) == 3 and all(close(sp.N(es[0].subs(x, sub).subs(a_, R(2.3)).subs(theta, R(t)), 30), sp.N(e.subs(x, sub).subs(a_, R(2.3)).subs(theta, R(t)), 30), 1e-20) for e in es[1:] for t in (0.2, 0.6, 1.1))
            report(ok, f"Pythagorean substitution x = {sub}: {line[:50]}")
    once(teach, r"\[\tan\theta=\frac{\sin\theta}{\cos\theta}=\frac{x}{\sqrt{a^2-x^2}}.\]", "returning to x: tan theta")
    for t in (0.2, 0.7, 1.3):
        report(close(sp.N(sp.tan(t)), sp.N((x / sp.sqrt(a_ ** 2 - x ** 2)).subs({x: 2 * sp.sin(t), a_: 2}))), f"tan theta = x/sqrt(a^2-x^2) at theta={t}")
    once(teach, r"\(\sin\theta=\dfrac{\tan\theta}{\sec\theta}=\dfrac{x}{\sqrt{a^2+x^2}}\)", "returning to x: sin theta for x = a tan theta")
    once(teach, r"\(\sec\theta=\sqrt{1+\tan^2\theta}=\dfrac{\sqrt{a^2+x^2}}{a}\)", "returning to x: sec theta")
    once(teach, r"\(\cos\theta=\sqrt{1-\sin^2\theta}=\dfrac{\sqrt{a^2-x^2}}{a}\)", "returning to x: cos theta")
    for t in (-1.2, -0.4, 0.3, 1.4):
        report(close(sp.N(sp.sin(t)), sp.N((x / sp.sqrt(a_ ** 2 + x ** 2)).subs({x: 3 * sp.tan(t), a_: 3}))), f"sin theta = x/sqrt(a^2+x^2) at theta={t}")
    inline_numbers(teach, "lesson")
    inline_identities(teach, "lesson")

    print("== Lesson Examples (C1-C3): chains, side columns, questions printed in the lesson")
    demo_text = "".join(re.findall(r'<div class="ex (?:demo|attempt)">(.*?)\{\{work', teach, re.S))
    k = 0
    for d, side in displays_with_side(lexA):
        k += check_display(d, side, "C", need_in=demo_text)
    report(k == 12, f"answer integral chains in Lesson Examples: {k} (expect 12)")
    inline_numbers(lexA, "C")
    inline_identities(lexA, "C")
    # C2(b) segment and sector-triangle answers
    once(lexA, r"\int_{2\sqrt2}^{4}\sqrt{16-x^2}\,dx&=\tfrac12\times\tfrac12\times4^2\big(\tfrac{\pi}{2}-\sin\tfrac{\pi}{2}\big)\\&=4\big(\tfrac{\pi}{2}-1\big)\\&=2\pi-4", "C2 demo (b)")
    report(close(seg(4, sp.pi / 2) / 2, quad(sp.sqrt(16 - x ** 2), x, 2 * sp.sqrt(2), 4)) and sp.simplify(seg(4, sp.pi / 2) / 2 - (2 * sp.pi - 4)) == 0, "C2 demo (b): half segment = 2pi - 4")
    once(lexA, r"\int_{0}^{3}\sqrt{36-x^2}\,dx&=\tfrac12\times3\times3\sqrt3+\tfrac12\times6^2\times\tfrac{\pi}{6}\\&=\tfrac{9\sqrt3}{2}+3\pi", "C2 your turn (b)")
    tri_sec = sp.Rational(1, 2) * 3 * 3 * sp.sqrt(3) + sp.Rational(1, 2) * 36 * sp.pi / 6
    report(close(tri_sec, quad(sp.sqrt(36 - x ** 2), x, 0, 3)) and sp.acos(sp.Rational(3, 6)) == sp.pi / 3 and sp.sqrt(36 - 9) == 3 * sp.sqrt(3), "C2 your turn (b): triangle + sector = integral, angle pi/3, height 3sqrt3")
    for q in ("Find \\(\\displaystyle\\int_{2\\sqrt2}^{4}\\sqrt{16-x^2}\\,dx\\)", "Find \\(\\displaystyle\\int_{0}^{3}\\sqrt{36-x^2}\\,dx\\)"):
        once(demo_text, q, q)

    print("== Textbook homework")
    q1 = lesson_q(L, 1)
    check_value("Ex12E Q1c", stem_integral(q1), maths(answer_block(tbA, 1))[0])
    q3 = lesson_q(L, 3)
    check_value("Ex12E Q3c", stem_integral(q3), maths(answer_block(tbA, 3))[0])
    for num, ps in ((2, "ab"), (4, "ab"), (5, "abcd"), (6, "abcdefgh")):
        ql, al = parts(lesson_q(L, num), "pl"), parts(answer_block(tbA, num), "b")
        for p in ps:
            check_value(f"Ex12E Q{num}{p}", maths(ql[p])[0], maths(al[p])[0])
    # Q7 a: I read from the stem of part a
    q7 = parts(lesson_q(L, 7), "pl")
    a7 = answer_block(tbA, 7)
    check_value("Ex12E Q7a", stem_integral(q7["a"]), maths(a7.split("<b>b</b>")[0])[0])
    # the substituted form printed in Q7a: 5 - 4x - x^2 = 9 - u^2 when x = u - 2
    report(sp.expand((5 - 4 * x - x ** 2).subs(x, u - 2) - (9 - u ** 2)) == 0, "Q7a: 5 - 4x - x^2 = 9 - u^2 with x = u - 2")
    for num, part in ((7, "b"), (8, "b"), (9, "b")):
        qr = romans(parts(lesson_q(L, num), "pl")[part])
        ar = romans(answer_block(tbA, num).split("<b>b</b>")[1])
        report(sorted(qr) == sorted(ar), f"Q{num}{part}: roman parts match {sorted(qr)}")
        for rn in qr:
            check_value(f"Ex12E Q{num}{part}({rn})", maths(qr[rn])[0], maths(ar[rn])[0])
    # Q10
    a10 = maths(answer_block(tbA, 10))[0]
    yv = tex(a10.split("=", 1)[1])
    fp = sp.sqrt(x ** 2 - 9) / x
    report(all(close(sp.N(sp.diff(yv, x).subs(x, t)), sp.N(fp.subs(x, t))) for t in (3.2, 4.0, 5.5, 9.0)) and sp.simplify(yv.subs(x, 3)) == 0,
           "Ex12E Q10: y' = sqrt(x^2-9)/x for x > 3 and y(3) = 0", a10)
    once(lesson_q(L, 10), r"\(f'(x)=\dfrac{\sqrt{x^2-9}}{x}\) and \(f(3)=0\)", "Q10 question")
    # Q11
    a11 = maths(answer_block(tbA, 11))[0]
    once(lesson_q(L, 11), r"\(y=\dfrac{x^3}{\sqrt{3-x^2}}\)", "Q11 curve")
    report(close(sp.N(tex(a11), 30), quad(x ** 3 / sp.sqrt(3 - x ** 2), x, 0, 1)), "Ex12E Q11 area = integral 0..1 of x^3/sqrt(3-x^2) (the curve is above the axis there)", a11)
    # Q13
    once(lesson_q(L, 13), r"\(\displaystyle\int_{-2}^{2}\frac{x^2}{e^x+1}\,dx=\int_{-2}^{2}\frac{x^2e^x}{e^x+1}\,dx\)", "Q13a identity printed")
    I1 = mp.quad(lambda t: t ** 2 / (mp.e ** t + 1), [-2, 2])
    I2 = mp.quad(lambda t: t ** 2 * mp.e ** t / (mp.e ** t + 1), [-2, 2])
    report(abs(I1 - I2) < 1e-25, "Q13a the two integrals are equal")
    a13 = maths(answer_block(tbA, 13))[0]
    report(close(sp.N(tex(a13), 30), I1), "Ex12E Q13b", f"{a13} vs {mp.nstr(I1, 15)}")
    # answers that are left out: show-that items only
    nums = re.findall(r'<div class="a"><span class="an">(\d+)</span>', tbA)
    report(nums == ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "13"], f"answer numbers {nums} (Q12 has no printed result)")
    for s_ in ("c12e_ex21", "c12e_tri", "c12e_q12", "a12e_c2demo", "a12e_c2yt"):
        report(os.path.exists(os.path.join(SRC, "svg", s_ + ".svg")) and (L + A).count("{{svg:%s}}" % s_) == 1, f"figure {s_}")

    print("== Past papers")
    k = 0
    for d, side in displays_with_side(ppA):
        k += check_display(d, side, "PP", need_in=ppL)
    report(k == 7, f"PP integral chains checked: {k} (expect 7)")
    inline_numbers(ppA, "PP")
    inline_identities(ppA, "PP")
    # PP5(i) the root simplifies to tan theta with x = cos 2theta
    once(ppA, r"\[\sqrt{\frac{1-x}{1+x}}=\sqrt{\frac{2\sin^2\theta}{2\cos^2\theta}}=\frac{\sin\theta}{\cos\theta},\]", "PP5 root")
    report(all(close(sp.N(sp.sqrt((1 - sp.cos(2 * t)) / (1 + sp.cos(2 * t)))), sp.N(sp.tan(t))) for t in (0.1, 0.4, 0.75)), "PP5 sqrt((1-cos2t)/(1+cos2t)) = tan t on [0, pi/4]")
    # PP5 (i) the target integral is printed and equals the original
    report(close(quad(4 * sp.sin(theta) ** 2, theta, 0, sp.pi / 4), quad(sp.sqrt((1 - x) / (1 + x)), x, 0, 1)), "PP5(i) both integrals have the same value")
    # PP6 side facts
    report(sp.simplify(sp.sqrt(((u - 4) ** 2 + 1) - 1).subs(u, 5.5) - 1.5) == 0, "PP6 sqrt(x-1) = u - 4 for u > 4")
    # MC
    blk = lambda pn: ppL[ppL.index(f'<span class="pn">{pn}</span>'):][:ppL[ppL.index(f'<span class="pn">{pn}</span>'):].index('class="hint"')]
    b1 = blk("PP 1")
    opts = re.findall(r"<span>\(([A-D])\)&ensp;\\\((.+?)\\\)</span>", b1)
    I0 = quad(1 / (x ** 2 + 1) ** 2, x, 0, sp.sqrt(3))
    good = []
    for l_, o in opts:
        _, inf = integrals(clean(o))
        f, lims, v, _ = inf[0]
        if close(quad(f, v, tex(lims[0]), tex(lims[1])), I0):
            good.append(l_)
    report(len(opts) == 4 and good == ["A"], "PP 1 MC: only (A) has the value of the integral", f"good={good}")
    once(ppA, "<b>Answer (A).</b>", "PP 1 answer letter")
    b2 = blk("PP 2")
    opts = re.findall(r"<span>\(([A-D])\)&ensp;\\\((.+?)\\\)</span>", b2)
    I0 = quad(sp.sqrt(1 - y ** 2), y, 0, sp.sqrt(3) / 2)
    good = [l_ for l_, o in opts if close(sp.N(tex(o), 30), I0)]
    report(len(opts) == 4 and good == ["C"], "PP 2 MC: only (C) has the value of the integral", f"good={good}")
    once(ppA, "<b>Answer (C).</b>", "PP 2 answer letter")
    # PP3(i)
    once(ppA, r"so \(x\le-1\) or \(x\ge1\).", "PP3(i) answer")
    und = [t for t in [i / 10 for i in range(-30, 31)] if not (1 - t * t > 0)]
    report(all(t <= -1 or t >= 1 for t in und) and all((t <= -1 or t >= 1) == (t in und) for t in [i / 10 for i in range(-30, 31)]), "PP3(i) f undefined exactly when x <= -1 or x >= 1")
    # marks, time, labels, hints
    marks = [int(m_) for m_ in re.findall(r'<span class="mk">(\d+) marks?</span>', ppL)]
    intro = re.search(r"<b>(\d+) marks</b>", ppL)
    tm = re.search(r"Suggested time: (\d+) minutes", ppL)
    tot = sum(marks)
    report(intro and int(intro.group(1)) == tot and 15 <= tot <= 22, f"PP marks {marks} add to intro {intro.group(1) if intro else None}")
    report(tm and int(tm.group(1)) == 5 * round(1.5 * tot / 5), f"PP time {tm.group(1) if tm else None} = 1.5 x {tot} rounded to 5")
    for pn, exp in (("PP 3", 4), ("PP 5", 4)):
        sub = re.search(pn + r'</span>.*?</div>(.*?)class="hint"', ppL, re.S).group(1)
        sm = [int(v) for v in re.findall(r'<span class="mk">(\d)</span>', sub)]
        report(sum(sm) == exp and len(sm) == 2, f"{pn} part marks {sm} add to {exp}")
    labL = [(p, re.sub(r"(</span>)+$", "", t)) for p, t in re.findall(r'<span class="pn">(PP \d+)</span>(.*?)<span class="mk">', ppL)]
    labA = [(p, re.sub(r"(</span>)+$", "", t)) for p, t in re.findall(r'<span class="pn">(PP \d+)</span>(.*?)</div>', ppA)]
    nl = [p for p, _ in labL]
    report(nl == [f"PP {i}" for i in range(1, 7)], f"PP numbering in lesson {nl}")
    report([p for p, _ in labA] == nl, "PP numbering in answers matches")
    report([s_ for _, s_ in labL] == [s_ for _, s_ in labA], "PP source labels identical in both files")
    report(ppL.count('class="hint"') == 6, f"one hint per PP: {ppL.count('class=\"hint\"')}")

    print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
    if FAILS:
        for f_ in FAILS:
            print("FAIL:", f_)
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    main()
