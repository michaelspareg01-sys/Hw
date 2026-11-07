"""Check of the Integration Part 2 Revision section, tied to the HTML.

Reads workspace/build/int2/revision.html and a_rev.html.
  1. Summary boxes: every standard derivative / integral form printed in the boxes (6B, 6G, 6K, 7B, Part 1)
     is parsed from the HTML and verified with sympy; the exact-value and boundary-angle tables are
     compared with sympy's sin, cos, tan; the radian conversions are recomputed.
  2. The nine worked examples: the givens are read from each question line, every printed result and
     every printed equality chain in the solution is parsed and verified (sympy diff / integrate / exact values),
     and compared with the textbook's printed results.
  3. The six warm-up questions: the givens are read from revision.html, the answers are recomputed with
     sympy, every equality chain in a_rev.html is verified piece by piece, and each final result is compared
     with the textbook's printed answer (Y12 PDF 863, 869, 874, 881).
Every template must match exactly once, otherwise the item FAILS.  Exit status 1 if anything fails.
Run: python3 workspace/checks/int2_rev.py

tex2sympy() and helpers are importable by the later int2 lesson checks.
"""
import os
import re
import sys

import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application, rationalize)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("INT2_SRC", os.path.join(HERE, "..", "build", "int2"))   # override only for mutation tests

x, a, b, u, n, k, C = sp.symbols("x a b u n k C")
TRANS = standard_transformations + (implicit_multiplication_application, rationalize)
LOCAL = {"x": x, "a": a, "b": b, "u": u, "n": n, "k": k, "C": C, "E": sp.E, "pi": sp.pi,
         "ln": sp.log, "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sec": sp.sec,
         "sqrt": sp.sqrt, "Rational": sp.Rational}

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


# ----------------------------------------------------------------- LaTeX -> sympy
def _group(s, i, op="{", cl="}"):
    """s[i] == op; return (contents, index after the matching cl)."""
    assert s[i] == op, (s, i)
    depth = 0
    for j in range(i, len(s)):
        if s[j] == op:
            depth += 1
        elif s[j] == cl:
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError("unbalanced: " + s)


def _arg(s, i):
    """A TeX argument at s[i]: a {group} or a single character (skipping spaces)."""
    while s[i] == " ":
        i += 1
    if s[i] == "{":
        return _group(s, i)
    if s[i] == "\\":                       # a control word such as \pi
        m = re.match(r"\\[a-zA-Z]+", s[i:])
        return s[i:i + m.end()], i + m.end()
    return s[i], i + 1


FUNCS = {r"\log_e": "ln", r"\ln": "ln", r"\sin": "sin", r"\cos": "cos", r"\tan": "tan", r"\sec^2": "secsq", r"\sec": "sec"}


def tex2py(t):
    s = t
    for w in (r"\left", r"\right", r"\Bigg", r"\bigg", r"\Big", r"\big", r"\displaystyle", r"\!", "&"):
        s = s.replace(w, "")
    for w in (r"\qquad", r"\quad", r"\,"):
        s = s.replace(w, " ")
    s = s.replace(r"\ ", " ").replace(r"\times", "*").replace(r"\cdot", "*")
    s = re.sub(r"(\d+)\^\\circ", r"(\1*pi/180)", s)                       # degrees
    s = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)       # mixed numbers such as 5\tfrac13
    s = s.replace(r"\pi", " pi ")
    # fractions
    while True:
        m = re.search(r"\\[dt]?frac", s)
        if not m:
            break
        n1, j = _arg(s, m.end())
        n2, j = _arg(s, j)
        s = s[:m.start()] + "((" + n1 + ")/(" + n2 + "))" + s[j:]
    # roots
    while True:
        m = re.search(r"\\sqrt", s)
        if not m:
            break
        j = m.end()
        if s[j] == "[":
            idx, j = _group(s, j, "[", "]")
            r, j = _arg(s, j)
            s = s[:m.start()] + "((" + r + ")**(Rational(1," + idx + ")))" + s[j:]
        else:
            r, j = _arg(s, j)
            s = s[:m.start()] + "sqrt(" + r + ")" + s[j:]
    # functions -> tokens
    for tex, name in FUNCS.items():
        s = s.replace(tex, " §" + name + "§ ")
    # e^{...}, e^x  (e not part of a word)
    while True:
        m = re.search(r"(?<![A-Za-z§])e\^", s)
        if not m:
            break
        r, j = _arg(s, m.end())
        s = s[:m.start()] + "exp(" + r + ")" + s[j:]
    s = re.sub(r"(?<![A-Za-z§])e(?![A-Za-z§])", "E", s)
    # powers
    while "^" in s:
        i = s.index("^")
        r, j = _arg(s, i + 1)
        s = s[:i] + "**(" + r + ")" + s[j:]
    s = s.replace("{", "(").replace("}", ")")
    # function application, innermost (rightmost) first
    while "§" in s:
        i = s.rindex("§", 0, s.rindex("§"))
        j = s.index("§", i + 1)
        name = s[i + 1:j]
        p = j + 1
        while p < len(s) and s[p] == " ":
            p += 1
        start = p
        while p < len(s):
            c = s[p]
            if c == "(":
                _, p = _group(s, p, "(", ")")
            elif s.startswith("**", p):
                p += 2
                if s[p] == "(":
                    _, p = _group(s, p, "(", ")")
                else:
                    p += 1
            elif c.isalnum() or c == ".":
                p += 1
            elif c == " " and p + 1 < len(s) and (s[p + 1].isalnum() or s[p + 1] == "(") and p > start and \
                    s[p - 1] not in "+-*/=,":
                # a space inside an argument such as 'tan(3/2) x' is not allowed: stop
                break
            else:
                break
        argt = s[start:p]
        rep = f"sec({argt})**2" if name == "secsq" else f"{name}({argt})"
        s = s[:i] + rep + s[p:]
    return s


def trig_arg(t):
    """The argument of the (single) sin, cos or tan in a TeX expression, read from the TeX itself
    (sympy would rewrite sin(3x - pi/3) or cos(1 - x) into another form)."""
    m = re.search(r"\\(sin|cos|tan)(.*)$", t, re.S)
    rest = m.group(2).strip()
    for o, c in ((r"\Big(", r"\Big)"), (r"\big(", r"\big)"), ("(", ")")):
        if rest.startswith(o) and rest.endswith(c):
            return tex2sympy(rest[len(o):-len(c)])
    return tex2sympy(rest)


def tex2sympy(t):
    return parse_expr(tex2py(t), local_dict=LOCAL, transformations=TRANS)


# ----------------------------------------------------------------- comparisons
PTS = [sp.Rational(3, 10), sp.Rational(7, 10), sp.Rational(11, 10), sp.Rational(17, 10)]


def equal(e1, e2):
    if isinstance(e1, sp.MatrixBase) or isinstance(e2, sp.MatrixBase):
        return sp.Matrix(e1) == sp.Matrix(e2)
    d = sp.simplify(sp.expand_log(sp.expand(sp.sympify(e1) - sp.sympify(e2)), force=True))
    if d == 0:
        return True
    vals = [sp.Rational(7, 3), sp.Rational(-2, 5), sp.Rational(5, 4), sp.Rational(13, 7), sp.Rational(3, 11)]
    others = sorted((s_ for s_ in d.free_symbols if s_ != x), key=str)
    subs_o = {s_: vals[i % len(vals)] + i for i, s_ in enumerate(others)}
    for p in PTS:
        v = complex(sp.N(d.subs(subs_o).subs(x, p), 30))
        if abs(v) > 1e-20:
            return False
    return True


def same(label, got, exp):
    try:
        res = equal(got, exp)
    except Exception as ex:                # noqa: BLE001
        fail(f"{label}: compare error {ex}")
        return
    if res:
        ok(f"{label}: {got}")
    else:
        fail(f"{label}: printed {got}, expected {exp}")


def split_eq(t):
    """Split a TeX chain on top-level '=' signs."""
    out, depth, cur = [], 0, ""
    for c in t:
        if c in "{([":
            depth += 1
        elif c in "})]":
            depth -= 1
        if c == "=" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += c
    out.append(cur)
    return [p.replace("&", "").strip().rstrip(".,").strip() for p in out]


def value(piece):
    """Evaluate one TeX piece: derivative operator, definite integral, bracket evaluation or plain expression."""
    p = piece.replace(r"\displaystyle", "").replace("&", "").strip()
    m = re.match(r"^\\dfrac\{d\}\{dx\}(.*)$", p, re.S)
    if m:
        return sp.diff(tex2sympy(m.group(1)), x)
    m = re.match(r"^(\d*)\\int_\{?(-?\w+)\}?\^\{?(-?\w+)\}?(.*?)dx$", p, re.S)
    if m:
        f = tex2sympy(m.group(4))
        lo, hi = tex2sympy(m.group(2)), tex2sympy(m.group(3))
        mult = int(m.group(1)) if m.group(1) else 1
        return mult * sp.integrate(f, (x, lo, hi))
    m = re.match(r"^\\Big\[(.*)\\Big\]_\{(.+?)\}\^\{(.+?)\}$", p, re.S)
    if m:
        F = tex2sympy(m.group(1))
        return F.subs(x, tex2sympy(m.group(3))) - F.subs(x, tex2sympy(m.group(2)))
    return tex2sympy(p)


def chain(label, tex, target, skip_first=True):
    """Every piece of the chain (after the first, which names the quantity) must equal target."""
    pieces = split_eq(tex)
    if skip_first:
        pieces = pieces[1:]
    if not pieces:
        fail(f"{label}: empty chain")
        return None
    last = None
    for i, pc in enumerate(pieces):
        try:
            v = value(pc)
        except Exception as ex:            # noqa: BLE001
            fail(f"{label} piece {i + 1} '{pc}' does not parse: {ex}")
            continue
        same(f"{label} piece {i + 1}", v, target)
        last = v
    return last


def one(rx, text, label, flags=re.S):
    m = re.findall(rx, text, flags)
    if len(m) != 1:
        fail(f"{label}: found {len(m)} times")
        return None
    return m[0]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def maths(block):
    return re.findall(r"\\\((.*?)\\\)", block, re.S)


def main():
    rev = read("revision.html")
    arev = read("a_rev.html")

    def box(title):
        return one(r'<div class="bt">' + re.escape(title) + r'</div>(.*?)</div>\n\n', rev, f"box '{title}'") or ""

    def example(title):
        return one(r'<span class="ex-title">' + re.escape(title) + r'</span>(.*?)</div></div>\n\n', rev, f"example '{title}'") or ""

    def has(label, block, tex):
        c = block.count(tex)
        if c == 1:
            ok(f"{label}: printed once")
        else:
            fail(f"{label}: '{tex}' printed {c} times")
        return c == 1

    def identity(label, block, tex, lhs_fn=None):
        """A printed identity 'LHS=RHS': both sides evaluated and compared."""
        if not has(label, block, tex):
            return
        L, R = split_eq(tex)[:2]
        same(label, value(R), value(L) if lhs_fn is None else lhs_fn(L))

    def antideriv(label, block, tex, integrand):
        """A printed indefinite integral '\\int f dx = F + C': F' must equal f (and f read back)."""
        if not has(label, block, tex):
            return
        L, R = split_eq(tex)[:2]
        m = re.match(r"^\\int(.*?)dx$", L.strip(), re.S)
        f = sp.sympify(0) if not m else tex2sympy(m.group(1))
        same(label + " integrand", f, integrand)
        F = tex2sympy(R).subs(C, 0)
        same(label + " F' = f", sp.diff(F, x), f)

    # ======================= 1. summary boxes =======================
    b1 = box("Three standard derivatives for exponential functions (6B)")
    for t in (r"\dfrac{d}{dx}\,e^x=e^x", r"\dfrac{d}{dx}\,e^{ax+b}=a\,e^{ax+b}"):
        identity("6B box " + t, b1, t)
    if has("6B box chain form", b1, r"\dfrac{d}{dx}\,e^u=e^u\,\dfrac{du}{dx}\quad\text{OR}\quad\dfrac{d}{dx}\,e^{f(x)}=e^{f(x)}f'(x)"):
        g = x ** 3 - 2 * x                    # test function for the chain-rule forms
        same("6B box chain form on f = x^3-2x", sp.diff(sp.exp(g), x), sp.exp(g) * sp.diff(g, x))

    b2 = box("The derivative of the logarithmic function (6F, 6G)")
    identity("6G log x", b2, r"\dfrac{d}{dx}\log_e x=\dfrac1x")
    identity("6G log(ax+b)", b2, r"\dfrac{d}{dx}\log_e(ax+b)=\dfrac{a}{ax+b}")
    has("6G proof x = e^y", b2, r"\(x=e^y,\)")
    has("6G proof dy/dx = 1/x", b2, r"\(\dfrac{dy}{dx}=\dfrac1x.\)")
    yv = sp.Symbol("y")
    same("6G proof: dx/dy = e^y and reciprocal = 1/x", 1 / sp.diff(sp.exp(yv), yv).subs(yv, sp.log(x)), 1 / x)

    b3 = box("Exponential and logarithmic functions with other bases (6K)")
    aa = sp.Symbol("a", positive=True)
    has("6K a = e^{log a}", b3, r"\ a=e^{\log_e a}\)")
    same("6K a^x = e^{x log a}", sp.exp(x * sp.log(aa)), aa ** x)
    has("6K a^x derivative line 1", b3, r"\(\phantom{\dfrac{d}{dx}\,a^x}=e^{x\log_e a}\times\log_e a,\)")
    has("6K a^x derivative line 2", b3, r"\(\phantom{\dfrac{d}{dx}\,a^x}=a^x\log_e a,\)")
    same("6K d/dx a^x = a^x log a", sp.diff(aa ** x, x), aa ** x * sp.log(aa))
    if has("6K boxed forms", b3, r"\dfrac{d}{dx}\,a^x=a^x\log_e a\qquad\text{and}\qquad\dfrac{d}{dx}\log_a x=\dfrac{1}{x\log_e a}"):
        same("6K d/dx log_a x", sp.diff(sp.log(x) / sp.log(aa), x), 1 / (x * sp.log(aa)))

    b4 = box("Standard derivatives of the trigonometric functions (7B)")
    al = one(r"\\\[\\begin\{aligned\}(\\dfrac\{d\}\{dx\}\\sin x.*?)\\end\{aligned\}\\\]", b4, "7B basic forms") or ""
    al2 = one(r"\\\[\\begin\{aligned\}(\\dfrac\{d\}\{dx\}\\sin\(ax\+b\).*?)\\end\{aligned\}\\\]", b4, "7B ax+b forms") or ""
    for blk, nm, cnt in ((al, "7B basic", 3), (al2, "7B ax+b", 3)):
        lines = [ln for ln in blk.split(r"\\") if ln.strip()]
        if len(lines) != cnt:
            fail(f"{nm}: {len(lines)} lines")
        for ln in lines:
            L, R = split_eq(ln.replace("&", ""))
            same(f"{nm} {L}", value(R), value(L))
    for t in (r"\dfrac{d}{dx}\sin x=\cos x=\sin\big(x+\tfrac{\pi}{2}\big)", r"\dfrac{d}{dx}\cos x=-\sin x=\cos\big(x+\tfrac{\pi}{2}\big)"):
        if has("7B phase " + t, b4, t):
            p = split_eq(t)
            for q in p[1:]:
                same("7B phase piece " + q, value(q), value(p[0]))
    for f_, dn in ((sp.sin, 2), (sp.cos, 2), (sp.sin, 4), (sp.cos, 4)):
        nm = "sin" if f_ is sp.sin else "cos"
        sign = "-" if dn == 2 else ""
        t = rf"\dfrac{{d^{dn}}}{{dx^{dn}}}\{nm} x={sign}\{nm} x"
        if has(f"7B d{dn} {nm}", b4, t):
            same(f"7B d{dn} {nm}", tex2sympy(split_eq(t)[1]), sp.diff(f_(x), x, dn))

    b5 = box("Log laws, the inverse identities and change of base (Year 11 Advanced 7D, 6F)")
    X, Y, A = sp.symbols("X Y A", positive=True)
    for t, lhs, rhs in ((r"\log_a xy=\log_a x+\log_a y", sp.log(X * Y) / sp.log(A), (sp.log(X) + sp.log(Y)) / sp.log(A)),
                        (r"\log_a\dfrac xy=\log_a x-\log_a y", sp.log(X / Y) / sp.log(A), (sp.log(X) - sp.log(Y)) / sp.log(A)),
                        (r"\log_a x^n=n\log_a x", sp.log(X ** 3) / sp.log(A), 3 * sp.log(X) / sp.log(A))):
        if has("log law " + t, b5, t):
            same("log law " + t, sp.expand_log(lhs, force=True), sp.expand_log(rhs, force=True))
    for t, e1, e2 in ((r"\log_a1=0", sp.log(1) / sp.log(A), 0), (r"\log_a a=1", sp.log(A) / sp.log(A), 1),
                      (r"\log_a\sqrt a=\tfrac12", sp.log(sp.sqrt(A)) / sp.log(A), sp.Rational(1, 2)),
                      (r"\log_a\tfrac1a=-1", sp.log(1 / A) / sp.log(A), -1),
                      (r"\log_a\tfrac1x=-\log_a x", sp.log(1 / X) / sp.log(A), -sp.log(X) / sp.log(A))):
        if has("particular value " + t, b5, t):
            same("particular value " + t, sp.simplify(sp.expand_log(e1, force=True)), e2)
    has("inverse identity log e^x", b5, r"\log_e e^x=x")
    same("inverse identity e^{log x}", sp.exp(sp.log(X)), X)
    has("change of base", b5, r"\log_b x=\dfrac{\log_e x}{\log_e b}")

    b6 = box("Radian measure (Year 11 Advanced 9G)")
    has("conversions", b6, r"\ 360^\circ=2\pi,\quad180^\circ=\pi,\quad90^\circ=\tfrac{\pi}{2}\)")
    m = one(r"=\\dfrac\{180\^\\circ\}\{\\pi\}\\doteq(\d+)\^\\circ(\d+)'", b6, "1 radian in degrees")
    if m:
        deg = sp.N(180 / sp.pi, 15)
        mins = round((float(deg) - int(deg)) * 60)
        if (int(m[0]), int(m[1])) == (int(deg), mins):
            ok(f"1 radian = {m[0]} deg {m[1]} min")
        else:
            fail(f"1 radian printed {m}, computed {int(deg)} deg {mins} min")
    m = one(r"=\\dfrac\{\\pi\}\{180\}\\doteq(0\.\d+)", b6, "1 degree in radians")
    if m:
        if sp.Float(m) == sp.Float(round(float(sp.pi / 180), 4)):
            ok(f"1 degree = {m}")
        else:
            fail(f"1 degree printed {m}")

    b7 = box("Exact values and angles of any size (Year 11 Advanced 5A, 5D, 5E, 9G)")
    tabs = re.findall(r'<table class="ev">(.*?)</table>', b7, re.S)
    if len(tabs) != 2:
        fail(f"exact value tables: {len(tabs)}")
    else:
        rows = re.findall(r"<tr>(.*?)</tr>", tabs[0], re.S)
        heads = [h for h in re.findall(r"<th>\\\((.*?)\\\)</th>", rows[0])]
        if heads != [r"\theta", r"\sin\theta", r"\cos\theta", r"\tan\theta"]:
            fail(f"special table header {heads}")
        fns = [sp.sin, sp.cos, sp.tan]
        nchk = 0
        for r_ in rows[1:]:
            cells = re.findall(r"<td>\\\((.*?)\\\)</td>", r_)
            th = tex2sympy(cells[0])
            for fn, c in zip(fns, cells[1:]):
                if equal(tex2sympy(c), fn(th)):
                    nchk += 1
                else:
                    fail(f"special table {fn.__name__}({cells[0]}) printed {c}")
        if nchk == 9 and len(rows) == 4:
            ok("special-angle table: 9 values agree with sympy")
        else:
            fail(f"special-angle table: {nchk} of 9 agree")
        rows = re.findall(r"<tr>(.*?)</tr>", tabs[1], re.S)
        angs = [tex2sympy(h) for h in re.findall(r"<th>\\\((.*?)\\\)</th>", rows[0])[1:]]
        nchk = 0
        for r_, fn in zip(rows[1:], fns):
            cells = re.findall(r"<td>(.*?)</td>", r_)[1:]
            for th, c in zip(angs, cells):
                c = c.replace(r"\(", "").replace(r"\)", "")
                ev = fn(th)
                if c == "*":
                    good = ev == sp.zoo or not ev.is_finite
                else:
                    good = equal(tex2sympy(c), ev)
                if good:
                    nchk += 1
                else:
                    fail(f"boundary table {fn.__name__}({th}) printed {c}")
        if nchk == 12 and angs == [0, sp.pi / 2, sp.pi, 3 * sp.pi / 2]:
            ok("boundary-angle table: 12 values agree with sympy")
        else:
            fail(f"boundary-angle table: {nchk} of 12 agree, angles {angs}")

    b8 = box("Integration basics from Part 1 (5B–5I)")
    antideriv("5E x^n", b8, r"\int x^n\,dx=\dfrac{x^{n+1}}{n+1}+C", x ** n)
    antideriv("5E (ax+b)^n", b8, r"\int(ax+b)^n\,dx=\dfrac{(ax+b)^{n+1}}{a(n+1)}+C", (a * x + b) ** n)
    has("FTC", b8, r"\int_a^b f(x)\,dx=\Big[F(x)\Big]_a^b=F(b)-F(a)")
    has("reverse chain u form", b8, r"\int u^n\,\dfrac{du}{dx}\,dx=\dfrac{u^{n+1}}{n+1}+C")
    g = x ** 2 + 1
    same("reverse chain rule on f = x^2+1, n = 3", sp.diff(g ** 4 / 4, x), g ** 3 * sp.diff(g, x))
    same("odd function integral (x^3 on [-2,2])", sp.integrate(x ** 3, (x, -2, 2)), 0)
    same("even function integral (x^2 on [-2,2])", sp.integrate(x ** 2, (x, -2, 2)), 2 * sp.integrate(x ** 2, (x, 0, 2)))

    # ======================= 2. worked examples =======================
    def qparts(block):
        """Question parts before the Solution label: {letter: TeX of the given}."""
        q = block.split('<div class="sol-label">')[0]
        return dict(re.findall(r'<span class="pl">([a-z])</span>\\\((.*?)\\\)</span>', q, re.S))

    def rhs(t):
        return tex2sympy(split_eq(t)[-1])

    # --- 6B Example 4 (book: a e^x - e^-x, b 20e^{4x-3}, c -1/2 e^{2-x/2}, d 1/2 e^{x/2} - 1/2 e^{-x/2})
    e = example("Textbook Example 4 (6B)")
    qp = qparts(e)
    book = {"a": "exp(x)-exp(-x)", "b": "20*exp(4*x-3)", "c": "-exp(2-x/2)/2", "d": "exp(x/2)/2-exp(-x/2)/2"}
    sol = e.split('<div class="sol-label">')[1] if '<div class="sol-label">' in e else ""
    for L in "abcd":
        if L not in qp:
            fail(f"6B Ex4 {L}: given missing")
            continue
        f = rhs(qp[L])
        d = sp.diff(f, x)
        same(f"6B Ex4 {L} book answer = sympy", sp.sympify(book[L]), d)
        part = one(r"<b>" + L + r"</b>(.*?)</p>", sol, f"6B Ex4 part {L}") or ""
        yp = [t for t in maths(part) if t.strip().startswith(r"\quad y'=")]
        if len(yp) != 1:
            fail(f"6B Ex4 {L}: printed y' found {len(yp)} times")
        else:
            chain(f"6B Ex4 {L} y'", yp[0].replace(r"\quad", ""), d)
        ab = re.findall(r"\\\(a=(.*?)\\\) and \\\(b=(.*?)\\\)", part)
        if L in "abc":
            if len(ab) != 1:
                fail(f"6B Ex4 {L}: a, b found {len(ab)} times")
            else:
                ex_ = sp.log(f.as_independent(x)[1] if L != "a" else sp.exp(-x))  # exponent ax+b of the e term
                ex_ = sp.expand(ex_)
                same(f"6B Ex4 {L} a", tex2sympy(ab[0][0]), sp.diff(ex_, x))
                same(f"6B Ex4 {L} b", tex2sympy(ab[0][1]), ex_.subs(x, 0))
    pd = one(r"<span style=\"margin-left:9.5mm\">\\\((y=.*?)\\\)</span>", sol, "6B Ex4 d index form")
    if pd:
        chain("6B Ex4 d index form", pd, rhs(qp.get("d", "0")))

    # --- 6B Example 5 (book: a -2x e^{1-x^2}, b 8e^{2x}(e^{2x}-3)^3)
    e = example("Textbook Example 5 (6B)")
    qp = qparts(e)
    for L, bk, uu, du, dy in (("a", "-2*x*exp(1-x**2)", "1-x^2", "-2x", "e^u"), ("b", "8*exp(2*x)*(exp(2*x)-3)**3", "e^{2x}-3", "2e^{2x}", "4u^3")):
        f = rhs(qp[L])
        d = sp.diff(f, x)
        same(f"6B Ex5 {L} book answer", sp.sympify(bk), d)
        al_ = [t for t in maths(e) if t.startswith(r"\begin{aligned}[t]\dfrac{dy}{dx}") and (("1-x^2" in t) == (L == "a"))]
        if len(al_) != 1:
            fail(f"6B Ex5 {L}: working block found {len(al_)} times")
        else:
            body = al_[0].replace(r"\begin{aligned}[t]", "").replace(r"\end{aligned}", "").replace(r"\\", "")
            pieces = split_eq(body)[2:]            # skip dy/dx and dy/du x du/dx
            for i, pc in enumerate(pieces):
                same(f"6B Ex5 {L} line {i + 1}", value(pc), d)
        has(f"6B Ex5 {L} u", e, rf"Let \(u={uu}\)")
        same(f"6B Ex5 {L} du/dx", tex2sympy(du), sp.diff(tex2sympy(uu), x))
        has(f"6B Ex5 {L} dy/du", e, rf"\(\dfrac{{dy}}{{du}}={dy}\)")

    # --- 6G Example 28 (book: a 4/(4x-9), b 1/(x-2), c 2x/(4+x^2))
    e = example("Textbook Example 28 (6G)")
    qp = qparts(e)
    books = {"a": "4/(4*x-9)", "b": "1/(x-2)", "c": "2*x/(4+x**2)"}
    for L in "abc":
        d = sp.diff(rhs(qp[L]), x)
        same(f"6G Ex28 {L} book answer", sp.sympify(books[L]), d)
    t = one(r"Thus \\\(\\ (y'=\\dfrac\{4\}\{4x-9\})\.\\\)", e, "6G Ex28 a result")
    if t:
        chain("6G Ex28 a", t, sp.diff(rhs(qp["a"]), x))
    t1 = one(r"<td>Thus</td><td>\\\((y'=.*?)\\\)</td>", e, "6G Ex28 b line 1")
    t2 = one(r"<td>\\\(\\phantom\{y'\}(=.*?),\\\)</td>", e, "6G Ex28 b line 2")
    if t1 and t2:
        db = sp.diff(rhs(qp["b"]), x)
        chain("6G Ex28 b line 1", t1, db)
        chain("6G Ex28 b line 2", "y'" + t2, db)
    t = one(r"\\\((y'=\\dfrac\{2x\}\{4\+x\^2\})\.\\\)", e, "6G Ex28 c result")
    if t:
        chain("6G Ex28 c", t, sp.diff(rhs(qp["c"]), x))
    has("6G Ex28 c u'", e, r"Then \(u'=2x\)")

    # --- 7B Example 4 (book: a gradient 0, b gradient -1)
    e = example("Textbook Example 4 (7B)")
    qp = qparts(e)
    for L, bk in (("a", 0), ("b", -1)):
        f = rhs(qp[L])
        d = sp.diff(f, x)
        val = d.subs(x, sp.pi / 4)
        same(f"7B Ex4 {L} book gradient", sp.sympify(bk), val)
        part = one(r"<p><b>" + L + r"</b></p><table class=\"steps\">(.*?)</table>", e, f"7B Ex4 {L} steps") or ""
        cells = re.findall(r"<td>\\\((.*?)\\\)</td>", part)
        if len(cells) != 5:
            fail(f"7B Ex4 {L}: {len(cells)} lines")
            continue
        chain(f"7B Ex4 {L} function", cells[0], f)
        chain(f"7B Ex4 {L} derivative", cells[1], d)
        for i, c in enumerate(cells[2:]):
            chain(f"7B Ex4 {L} at pi/4 line {i + 1}", c.replace(r"\phantom{y'}", "y'"), val)

    # --- 7B Example 7 (book: a -7 sin 7x, b 12 cos(3x - pi/3), c 3/2 sec^2 (3x/2))
    e = example("Textbook Example 7 (7B)")
    qp = qparts(e)
    sol = e.split('<div class="sol-label">')[1]
    books = {"a": -7 * sp.sin(7 * x), "b": 12 * sp.cos(3 * x - sp.pi / 3), "c": sp.Rational(3, 2) * sp.sec(3 * x / 2) ** 2}
    for L in "abc":
        f = rhs(qp[L])
        d = sp.diff(f, x)
        same(f"7B Ex7 {L} book answer", books[L], d)
        part = one(r"<b>" + L + r"</b>(.*?)</p>", sol, f"7B Ex7 {L}") or ""
        ab = re.findall(r"so \\\(a=(.*?)\\\) and \\\(b=(.*?)\\\)", part)
        res = re.findall(r"\\\(\\ \\dfrac\{dy\}\{dx\}=(.*?)\.\\\)", part)
        arg = trig_arg(qp[L])
        if len(ab) == 1:
            same(f"7B Ex7 {L} a", tex2sympy(ab[0][0]), sp.diff(arg, x))
            same(f"7B Ex7 {L} b", tex2sympy(ab[0][1]), arg.subs(x, 0))
        else:
            fail(f"7B Ex7 {L}: a, b found {len(ab)} times")
        if len(res) == 1:
            same(f"7B Ex7 {L} dy/dx", tex2sympy(res[0]), d)
        else:
            fail(f"7B Ex7 {L}: dy/dx found {len(res)} times")

    # --- 6F Example 21 (book: 6, 1, -1, -1/2, 10, 0.1)
    e = example("Textbook Example 21 (6F)")
    qp = qparts(e)
    sol = e.split('<div class="sol-label">')[1]
    books = {"a": 6, "b": 1, "c": -1, "d": sp.Rational(-1, 2), "e": 10, "f": sp.Rational(1, 10)}
    for L in "abcdef":
        g = tex2sympy(qp[L])
        same(f"6F Ex21 {L} book", sp.nsimplify(books[L]), sp.simplify(g))
        t = one(r"<b>" + L + r"</b> \\\((.*?)\\\)</span>", sol, f"6F Ex21 {L} solution")
        if t:
            if split_eq(t)[0] != qp[L]:
                fail(f"6F Ex21 {L}: solution starts {split_eq(t)[0]}, question {qp[L]}")
            chain(f"6F Ex21 {L}", t, g)

    # --- Year 11 Advanced Example 15 (9G) (book: a -1/sqrt2, b 2/sqrt3)
    e = example("Year 11 Advanced Example 15 (9G)")
    qp = qparts(e)
    for L, bk in (("a", -1 / sp.sqrt(2)), ("b", 2 / sp.sqrt(3))):
        g = sp.sin(5 * sp.pi / 4) if L == "a" else sp.sec(11 * sp.pi / 6)
        same(f"Adv Ex15 {L} given", tex2sympy(qp[L]), g)
        same(f"Adv Ex15 {L} book", bk, g)
        blk = [t for t in maths(e) if t.startswith(r"\begin{aligned}[t]" + (r"\sin" if L == "a" else r"\sec"))]
        if len(blk) != 1:
            fail(f"Adv Ex15 {L}: working found {len(blk)} times")
            continue
        body = blk[0].replace(r"\begin{aligned}[t]", "").replace(r"\end{aligned}", "").replace(r"\\", "")
        chain(f"Adv Ex15 {L}", body, g, skip_first=False)
    has("Adv Ex15 a quadrant", e, r"\(\frac{5\pi}{4}\) is in the third quadrant, with related angle \(\frac{\pi}{4}\)")
    has("Adv Ex15 b quadrant", e, r"\(\frac{11\pi}{6}\) is in the fourth quadrant, with related angle \(\frac{\pi}{6}\)")
    for ang, q_, rel in ((5 * sp.pi / 4, 3, sp.pi / 4), (11 * sp.pi / 6, 4, sp.pi / 6)):
        quad = int(ang // (sp.pi / 2)) + 1
        rl = min(abs(ang - m_ * sp.pi) for m_ in range(3))
        same(f"Adv Ex15 quadrant of {ang}", quad, q_)
        same(f"Adv Ex15 related angle of {ang}", rl, rel)

    # --- 5F Example 22 (book: 10 2/3 square units)
    e = example("Textbook Example 22 (5F)")
    blk = one(r"\\\(\\begin\{aligned\}\[t\](\\int_\{-2\}\^\{2\}.*?)\\end\{aligned\}\\\)", e, "5F Ex22 working")
    area = sp.integrate(4 - x ** 2, (x, -2, 2))
    same("5F Ex22 book 10 2/3", sp.Rational(32, 3), area)
    same("5F Ex22 roots of 4 - x^2", sp.Matrix(sorted(sp.solve(4 - x ** 2, x))), sp.Matrix([-2, 2]))
    if blk:
        body = blk.replace(r"\\", "")
        chain("5F Ex22", body, area, skip_first=False)
    has("5F Ex22 conclusion", e, r"the required area is \(10\tfrac23\) square units")

    # --- 5I Example 36
    e = example("Textbook Example 36 (5I)")
    cells = re.findall(r"<td>\\\((.*?)\\\)</td>", e)
    yv36 = (x ** 3 + 5) ** 4
    d36 = sp.diff(yv36, x)
    if len(cells) != 4:
        fail(f"5I Ex36 a: {len(cells)} lines")
    else:
        chain("5I Ex36 y", cells[0], yv36)
        for i, c in enumerate(cells[2:]):
            chain(f"5I Ex36 dy/dx line {i + 1}", c.replace(r"\phantom{\dfrac{dy}{dx}}", "y"), d36)
    t = one(r"Reversing this, \\\(\\ \\displaystyle\\int12x\^2\(x\^3\+5\)\^3\\,dx=(.*?)\\\)", e, "5I Ex36 b")
    if t:
        same("5I Ex36 b primitive' = integrand", sp.diff(tex2sympy(t.rstrip(".")), x), 12 * x ** 2 * (x ** 3 + 5) ** 3)
    t = one(r"\\int x\^2\(x\^3\+5\)\^3\\,dx=(.*?)\+C\\\)", e, "5I Ex36 c")
    if t:
        same("5I Ex36 c primitive' = integrand", sp.diff(tex2sympy(t), x), x ** 2 * (x ** 3 + 5) ** 3)

    # ======================= 3. warm-up =======================
    ans = dict((an.strip(), ab_) for an, ab_ in re.findall(r'<div class="a"><span class="an">([^<]+)</span><div class="ab"[^>]*>(.*?)</div></div>\n', arev + "\n", re.S))
    for q in "123456":
        if q not in ans:
            fail(f"answer block {q} missing")
            ans[q] = ""

    def qblock(nq):
        return one(r'<span class="q-num">%d</span>(.*?)\{\{work' % nq, rev, f"warm-up question {nq}") or ""

    def wparts(qb):
        return dict(re.findall(r'<span class="pl">([a-z])</span>\\\((.*?)\\\)</span>', qb, re.S))

    def apart(blk, L):
        """Text of answer part L, up to the next part label or the end."""
        return one(r"<b>" + L + r"</b>(.*?)(?=<b>[a-z]</b>|$)", blk, f"answer part {L}") or ""

    # ---- Q1: Exercise 6B Q1 b, c, d, g, h (book: 12e^{3x}, 2e^{x/3}, e^{-2x}, -3e^{-3x+4}, -2e^{-2x-7})
    qb = qblock(1)
    if "Exercise 6B Q1" not in qb:
        fail("Q1 source label")
    P = wparts(qb)
    book = ["12*exp(3*x)", "2*exp(x/3)", "exp(-2*x)", "-3*exp(-3*x+4)", "-2*exp(-2*x-7)"]
    for (L, g), bk in zip(sorted(P.items()), book):
        f = rhs(g)
        d = sp.diff(f, x)
        same(f"Q1{L} sympy = textbook answer", sp.sympify(bk), d)
        part = apart(ans["1"], L)
        ab = re.findall(r"Here \\\(a=(.*?)\\\) and \\\(b=(.*?)\\\)", part)
        ex_ = sp.expand(sp.log(f.as_independent(x)[1]))
        if len(ab) == 1:
            same(f"Q1{L} a", tex2sympy(ab[0][0]), sp.diff(ex_, x))
            same(f"Q1{L} b", tex2sympy(ab[0][1]), ex_.subs(x, 0))
        else:
            fail(f"Q1{L}: a and b found {len(ab)} times")
        t = [m_ for m_ in maths(part) if m_.startswith("y'=")]
        if len(t) == 1:
            chain(f"Q1{L} y'", t[0], d)
        else:
            fail(f"Q1{L}: y' found {len(t)} times")
    if len(P) != 5:
        fail(f"Q1: {len(P)} parts")

    # ---- Q2: Exercise 6G Q8 a, b, c (book: (2x+3)/(x^2+3x+2), 6x^2/(1+2x^3), e^x/(e^x-2))
    qb = qblock(2)
    if "Exercise 6G Q8" not in qb:
        fail("Q2 source label")
    P = wparts(qb)
    book = ["(2*x+3)/(x**2+3*x+2)", "6*x**2/(1+2*x**3)", "exp(x)/(exp(x)-2)"]
    for (L, g), bk in zip(sorted(P.items()), book):
        f = tex2sympy(g)
        d = sp.diff(f, x)
        same(f"Q2{L} sympy = textbook answer", sp.sympify(bk), d)
        part = apart(ans["2"], L)
        mm = maths(part)
        if len(mm) != 3:
            fail(f"Q2{L}: {len(mm)} maths items")
            continue
        uu = tex2sympy(split_eq(mm[0])[1])
        same(f"Q2{L} u is the log argument", sp.exp(f), uu)
        chain(f"Q2{L} u'", mm[1], sp.diff(uu, x))
        if not mm[2].startswith(r"\dfrac{d}{dx}" + g.replace(r"\ln", r"\ln")):
            fail(f"Q2{L}: derivative line does not restate the question")
        chain(f"Q2{L} derivative", mm[2], d, skip_first=False)

    # ---- Q3: Exercise 6G Q12 a, b, d, g (book: 3/x, 1/(3x), 1/(2x-4), log 2)
    qb = qblock(3)
    if "Exercise 6G Q12" not in qb:
        fail("Q3 source label")
    P = wparts(qb)
    book = ["3/x", "1/(3*x)", "1/(2*x-4)", "log(2)"]
    for (L, g), bk in zip(sorted(P.items()), book):
        f = rhs(g)
        d = sp.diff(f, x)
        same(f"Q3{L} sympy = textbook answer", sp.sympify(bk), d)
        part = apart(ans["3"], L)
        ys = [m_ for m_ in maths(part) if m_.startswith("y=")]
        yps = [m_ for m_ in maths(part) if m_.startswith("y'=")]
        if len(ys) != 1 or len(yps) != 1:
            fail(f"Q3{L}: y found {len(ys)}, y' found {len(yps)}")
            continue
        chain(f"Q3{L} y (log laws)", ys[0], f)
        chain(f"Q3{L} y'", yps[0], d)

    # ---- Q4: Exercise 7B Q2 e, g, i, k (book: 2cos(2x-1), 2sin(1-x), -21cos(2-3x), 3cos((x+1)/2))
    qb = qblock(4)
    if "Exercise 7B Q2" not in qb:
        fail("Q4 source label")
    P = wparts(qb)
    book = [2 * sp.cos(2 * x - 1), 2 * sp.sin(1 - x), -21 * sp.cos(2 - 3 * x), 3 * sp.cos((x + 1) / 2)]
    for (L, g), bk in zip(sorted(P.items()), book):
        f = tex2sympy(g)
        d = sp.diff(f, x)
        same(f"Q4{L} sympy = textbook answer", bk, d)
        part = apart(ans["4"], L)
        mm = maths(part)
        arg = trig_arg(g)
        am = [m_ for m_ in mm if m_.startswith("a=")]
        if len(am) == 1:
            same(f"Q4{L} a", tex2sympy(am[0][2:]), sp.diff(arg, x))
        else:
            fail(f"Q4{L}: a found {len(am)} times")
        dm = [m_ for m_ in mm if m_.startswith(r"\dfrac{d}{dx}")]
        if len(dm) == 1:
            if not split_eq(dm[0])[0].endswith(g):
                fail(f"Q4{L}: derivative line does not restate the question")
            chain(f"Q4{L} derivative", dm[0], d, skip_first=False)
        else:
            fail(f"Q4{L}: derivative found {len(dm)} times")

    # ---- Q5: Exercise 7B Q4 (book: f'(x) = -2 sin 2x; 0, -1, -sqrt3, -2)
    qb = qblock(5)
    if "Exercise 7B Q4" not in qb:
        fail("Q5 source label")
    fq = one(r"If \\\(f\(x\)=(.*?)\\\)", qb, "Q5 f")
    f = tex2sympy(fq or "0")
    fp = sp.diff(f, x)
    same("Q5 f'(x) = textbook -2 sin 2x", -2 * sp.sin(2 * x), fp)
    t = one(r"so \\\((f'\(x\)=.*?)\\\)", ans["5"], "Q5 printed f'(x)")
    if t:
        chain("Q5 f'(x)", t.rstrip("."), fp)
    P = wparts(qb)
    book = [0, -1, -sp.sqrt(3), -2]
    for (L, g), bk in zip(sorted(P.items()), book):
        arg = re.match(r"f'(?:\\big\()?(.*?)(?:\\big\))?$", g).group(1)
        val = fp.subs(x, tex2sympy(arg))
        same(f"Q5{L} value = textbook answer", bk, val)
        part = apart(ans["5"], L)
        mm = maths(part)
        if len(mm) != 1 or split_eq(mm[0])[0] != g:
            fail(f"Q5{L}: answer line does not restate {g}")
            continue
        chain(f"Q5{L}", mm[0], val)

    # ---- Q6: Exercise 5B Q4 c, d, e, f (book: 9, 30, 96, 10)
    qb = qblock(6)
    if "Exercise 5B Q4" not in qb:
        fail("Q6 source label")
    P = wparts(qb)
    book = [9, 30, 96, 10]
    for (L, g), bk in zip(sorted(P.items()), book):
        v = value(g)
        same(f"Q6{L} sympy = textbook answer", bk, v)
        blk = one(r"<b>" + L + r"</b> \\\(\\begin\{aligned\}\[t\](.*?)\\end\{aligned\}\\\)", ans["6"], f"Q6{L} working")
        if not blk:
            continue
        body = blk.replace(r"\\", "")
        if split_eq(body)[0] != g.replace(r"\displaystyle", ""):
            fail(f"Q6{L}: working does not restate the question")
        chain(f"Q6{L}", body, v, skip_first=False)
    t = one(r"so this is also \\\((2\\displaystyle\\int_0\^2\(5x\^4\+6x\^2\)\\,dx=2\\times48=96)\\\)\.", ans["6"], "Q6c even note")
    if t:
        chain("Q6c even note", t, 96, skip_first=False)

    print(f"\n{checked} checks passed, {fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
