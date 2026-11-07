r"""Check of Lesson 5I (Integration Part 1 pack): The reverse chain rule, and the Chapter 5 review, tied to
the printed HTML.

Reads workspace/build/int1/l5i.html and a_5i.html.
  - Every printed question (tutor demos, your turns, worked examples, Exercise 5I, the past papers and the
    review) carries data-q="KEY". The function or integral is read from the page, converted from TeX to
    sympy (int3_tex.py) and compared with the textbook transcription typed below (TRANS).
  - Every checked solution / answer block carries data-c="KEY"; each key must occur exactly once, or the
    item FAILS. Inside a block, every equation chain (inline maths, display maths, aligned rows joined at
    "&=") is checked member by member, according to the kind of item:
      der  (find d/dx F):   "Let y = ..." members equal F; members after dy/dx, f'(x) or y' equal F'(x);
                            a chain led by d/dx(G) has every member equal to G'(x); the final answer is the
                            last member of the last chain about F, compared with the key;
      ind  (indefinite):    each chain has its own integrand g (from its integral, its d/dx member or its
                            member with C), which must be a constant multiple of the item's integrand f;
                            an integral member k*int(h) needs k*h = g; a member with C differentiates to g;
                            a member with x and no C equals g or differentiates to g (a primitive written
                            without C, as the book does when reversing); the final answer is the last
                            member with C in a chain whose g is f, compared with the key (up to a constant);
      def  (definite):      an integral member k*int_a^b(h) has the item's limits, h a constant multiple of
                            f, and k*int = the value; a bracket member c[F]_a^b has F' a constant multiple
                            of f and value c(F(b) - F(a)); every number member equals the value, which is
                            found by sympy and checked by numerical quadrature of the integrand READ from
                            the page;
      chains with no integral, d/dx or C are identities (all members equal), after u is replaced by the
      item's inside function.
    "Let u = ..." side columns and the "u = ..., du/dx = ..., n = ..." notes (data-s) are checked:
    du/dx = u'(x); y(u(x)) = F; dy/du = y'(u); int u^n du/dx dx = G(u) needs G'(u) = u^n; a printed n
    needs the integrand to be a constant times u^n du/dx.
  - Final answers are compared with the textbook key (Y12 Ext 1 PDF 893 right column and PDF 894 left
    column, transcribed in KEY) or, for the lesson examples, with hand values.
  - Custom checks: the review Questions 4-7, 9-11 and 15, Exercise Questions 17 and 18, the past-paper
    options, the textbook boxes 21 and 22, the bands, the hints and the timed-practice note.
Break tokens "\)\({}" and "\)\(\displaystyle{}" (line-break points in long chains) are removed before
reading; maths preceded by <!--nc--> is prose, not checked as a chain.
Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5i.py
"""
import math
import os
import re
import sys

import mpmath
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))   # override only for mutation tests
X, C, N, U, T, Y, K, UP, Z = sp.symbols("x C n u t y k Up Z")
EXTRA = {"x": X, "C": C, "c": C, "n": N, "u": U, "t": T, "y": Y, "k": K, "Up": UP, "Z": Z}
PTS = [0.37 + 0.06j, 1.43 + 0.04j, 2.71 + 0.09j, 5.9 + 0.05j, -1.6 + 0.07j]
R = sp.Rational
FAILS, NOK = [], [0]


def ok(flag, label, detail=""):
    if flag:
        NOK[0] += 1
        print("OK       " + label[:110] + ("  " + detail[:120] if detail else ""))
    else:
        FAILS.append(label)
        print("MISMATCH " + label[:110] + ("  " + detail[:160] if detail else ""))
    return flag


# ------------------------------------------------------------------ TeX -> sympy
LABELS = (r"\frac{dy}{dx}", r"\frac{dy}{du}\times\frac{du}{dx}", "A(x)", "f'(x)", "y'", r"\text{Area}", "f(x)")


def norm(s):
    s = s.replace("&amp;", "").replace("&", "").replace("\\dfrac", "\\frac").replace("\\displaystyle", "")
    s = re.sub(r"\\text\{(Let|Then|Hence|and|Here) \}", "", s)
    s = s.replace("\\,", " ").replace("\\;", " ").replace("\\quad", " ").replace("\\qquad", " ")
    return s.strip()


def prep(s):
    s = norm(s)
    s = s.replace("\\div", "/").replace("\\text{ u}^2", "")
    s = re.sub(r"\\sqrt\s+(\w)", r"\\sqrt{\1}", s)
    s = s.replace("\\big(f(x)\\big)", "(u)").replace("f'(x)", "(Up)").replace("f(x)", "(u)")
    s = s.replace("\\frac{du}{dx}", "(Up)")
    s = re.sub(r"(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)        # mixed number 8\tfrac23
    s = re.sub(r"(?<![A-Za-z\d])(\d+)([A-Za-z])", r"\1 \2", s)   # 12x is a product
    return s.strip().rstrip(".,;:").strip()


def P(s):
    return _tex(prep(s), EXTRA)


def realify(e):
    e = sp.sympify(e)
    return e.replace(lambda t: t.is_Pow and t.exp.is_Rational and not t.exp.is_Integer and t.exp.q % 2 == 1,
                     lambda t: sp.real_root(t.base, t.exp.q) ** t.exp.p)


def cnum(e, z):
    return complex(sp.N(sp.sympify(e).subs({X: z, C: 0, T: z, Y: z}), 30))


def feq(e1, e2):
    try:
        for z in PTS:
            a, b = cnum(e1, z), cnum(e2, z)
            if abs(a - b) > 1e-9 * (1 + abs(a) + abs(b)):
                return False
        return True
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def rnum(e):
    return complex(sp.N(realify(sp.sympify(e)), 30))


def neq(e1, e2):
    try:
        a, b = rnum(e1), rnum(e2)
        return abs(a - b) < 1e-9 * (1 + abs(a) + abs(b))
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def xeq(e1, e2):
    """Equal as functions if either has x, otherwise as numbers."""
    return feq(e1, e2) if (has_x(e1) or has_x(e2)) else neq(e1, e2)


def has_x(e):
    return bool(sp.sympify(e).free_symbols & {X, T, Y})


def has_c(e):
    return C in sp.sympify(e).free_symbols


def const_ratio(g, f):
    try:
        return feq(sp.diff(sp.sympify(g) / sp.sympify(f), X), 0)
    except Exception:  # noqa: BLE001
        return False


# ------------------------------------------------------------------ HTML
def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        s = fh.read()
    s = s.replace("\\)\\(\\displaystyle{}", "").replace("\\)\\({}", "")
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def block(html, attr, key, quiet=False):
    pat = re.compile(r"<(\w+)[^>]*\b" + attr + r'="' + re.escape(key) + r'"[^>]*>')
    ms = list(pat.finditer(html))
    if len(ms) != 1:
        if not quiet:
            ok(False, f"{attr}={key}", f"found {len(ms)} times")
        return None
    m = ms[0]
    tag, i, depth = m.group(1), m.end(), 1
    opener, closer = re.compile(r"<" + tag + r"\b"), "</" + tag + ">"
    while depth:
        j = html.find(closer, i)
        o = opener.search(html, i)
        if o and o.start() < j:
            depth, i = depth + 1, o.end()
        else:
            depth, i = depth - 1, j + len(closer)
    return html[m.end():i - len(closer)]


def drop_side(text):
    """Remove nested data-s spans (side notes) from a solution block."""
    while True:
        m = re.search(r'<span[^>]*data-s="[^"]*"[^>]*>', text)
        if not m:
            return text
        j = text.find("</span>", m.end())
        text = text[:m.start()] + text[j + 7:]


def maths(text):
    out = []
    for m in re.finditer(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", text, re.S):
        if re.search(r"<!--nc-->\s*$", text[max(0, m.start() - 12):m.start()]):
            continue
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    return out


def split_top(s, sep="="):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in "{([":
            depth += 1
        elif ch in "})]":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def chains(text):
    out = []
    for m in maths(text):
        m = re.sub(r"\\begin\{aligned\}(\[t\])?|\\end\{aligned\}", "", m)
        rows, cur = [], None
        for row in m.split("\\\\"):
            row = row.replace("&", "").strip()
            if re.fullmatch(r"(\\q?quad\s*)?\\text\{[^}]*\}\s*C?,?", row):      # "for some constant C," rows
                continue
            row = re.sub(r",?\s*\\q?quad\s*\\text\{(for some|using|here|\(here).*$", "", row, flags=re.S).strip()
            row = re.sub(r"^\\quad\s*", "", row).strip()
            if not row:
                continue
            if row.startswith("=") and cur is not None:
                cur += row
            else:
                if cur is not None:
                    rows.append(cur)
                cur = row
        if cur is not None:
            rows.append(cur)
        for r_ in rows:
            mem = [p.strip().rstrip(".,").strip() for p in split_top(r_)]
            mem = [p for p in mem if p]
            if len(mem) >= 2:
                out.append(mem)
    return out


LIM = r"(\{[^{}]*\}|-?\w)"


def parse_int(s):
    """[k]\\int[_a^b] h d(var) -> (k, a, b, h, var); limits None for an indefinite integral."""
    s = norm(s)
    i = s.index("\\int")
    pre = s[:i].strip()
    if pre.endswith("\\times"):
        pre = pre[:-6]
    k = P(pre) if pre not in ("", "+") else sp.Integer(1)
    if pre == "-":
        k = sp.Integer(-1)
    m = re.match(r"\\int(?:_" + LIM + r"\^" + LIM + r")?(.*)$", s[i:], re.S)
    a, b, rest = m.group(1), m.group(2), m.group(3).strip()
    mm = re.fullmatch(r"(.*?)\s*d([xty])", rest, re.S)
    if not mm:
        raise ValueError(f"no d(var) in {s!r}")
    var = {"x": X, "t": T, "y": Y}[mm.group(2)]
    h = P(mm.group(1)) if mm.group(1).strip() else sp.Integer(1)
    h = h.subs(var, X)
    if a is None:
        return k, None, None, h, var
    return k, P(a.strip("{}")), P(b.strip("{}")), h, var


BR = re.compile(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, re.S)


def quad_value(f, a, b):
    g = sp.lambdify(X, realify(f), "mpmath")
    mpmath.mp.dps = 30
    return mpmath.quad(lambda t: mpmath.re(g(t)), [float(a), float(b)])


def is_label(t):
    t = norm(t)
    return t in LABELS or t in ("y",) or re.fullmatch(r"\\frac\{dy\}\{du\}", t) is not None


# ------------------------------------------------------------------ the item checker
def member(t, Uf):
    """Classify one chain member: (kind, value)."""
    tn = norm(t)
    if tn == "y":
        return "Y", None
    if is_label(tn):
        return "L", None
    if tn.startswith("\\frac{d}{dx}"):
        e = P(tn[len("\\frac{d}{dx}"):])
        if Uf is not None:
            e = e.subs(U, Uf)
        return "DX", (e, sp.diff(e, X))
    if "\\int" in tn:
        k, a, b, h, var = parse_int(tn)
        return "INT", (k, a, b, h)
    mm = BR.search(tn)
    if mm:
        var = T if re.search(r"(?<![a-z\\])t", mm.group(1)) else (Y if re.search(r"(?<![a-z\\])y", mm.group(1)) else X)
        F = P(mm.group(1)).subs(var, X)
        lo, hi = P(mm.group(2).strip("{}")), P(mm.group(3).strip("{}"))
        Mz = P(tn[:mm.start()] + " Z " + tn[mm.end():])
        return "BR", (Mz, F, lo, hi)
    e = P(tn)
    if Uf is not None:
        e = e.subs(U, Uf)
    return "E", e


def check_block(key, text, spec, final_key=None, Uf=None):
    """spec: ('der', F) | ('ind', f) | ('def', f, a, b, v) | ('id',)."""
    kind = spec[0]
    text = drop_side(text)
    finals, n_mem = [], 0
    for mem in chains(text):
        tag = f"{key}: {'='.join(mem)}"
        if norm(mem[0]) == "n" and len(mem) == 2:
            continue
        try:
            vals = [member(t, Uf) for t in mem]
        except Exception as err:  # noqa: BLE001
            ok(False, tag[:110], "read: " + repr(err)[:100])
            continue
        kinds = [k_ for k_, _ in vals]
        active = any(k_ in ("DX", "INT", "BR") or (k_ == "E" and has_c(v_)) for k_, v_ in vals)
        n_mem += len(vals)
        # identity chains (no integral, d/dx, bracket or C)
        if not active and "Y" not in kinds and not (kind == "der" and "L" in kinds):
            ev = [v_ for k_, v_ in vals if k_ == "E"]
            if len(ev) < 2:                            # a statement such as dy/du = 4u^3 (checked in the side column)
                continue
            ok(all(xeq(e, ev[0]) for e in ev[1:]), tag[:110], "(identity)")
            continue
        if kind == "der":
            F = spec[1]
            if "Y" in kinds:
                ok(all(feq(v_, F) for k_, v_ in vals if k_ == "E"), tag[:110], "(y = F)")
                continue
            if kinds[0] == "DX":
                G, dG = vals[0][1]
                good = all(feq(v_, dG) for k_, v_ in vals[1:] if k_ == "E")
                good = good and all(feq(v_[1], dG) for k_, v_ in vals[1:] if k_ == "DX")
                ok(good, tag[:110], "(each member = derivative of the first)")
                if feq(G, F):
                    finals.append([v_ for k_, v_ in vals if k_ == "E"][-1] if "E" in kinds else dG)
                continue
            dF = sp.diff(F, X)
            ok(all(feq(v_, dF) for k_, v_ in vals if k_ == "E"), tag[:110], "(= F')")
            if kinds[-1] == "E":
                finals.append(vals[-1][1])
            continue
        if kind in ("ind", "id"):
            f = spec[1] if kind == "ind" else None
            g = None
            for k_, v_ in vals:
                if k_ == "INT":
                    g = v_[0] * v_[3]
                    break
                if k_ == "DX":
                    g = v_[1]
                    break
                if k_ == "E" and has_c(v_):
                    g = sp.diff(v_, X)
                    break
            if f is not None:
                ok(g is not None and const_ratio(g, f), f"{key}: chain integrand is a multiple of f", tag[:80])
            good = True
            for t, (k_, v_) in zip(mem, vals):
                if k_ == "INT":
                    good &= v_[1] is None and feq(v_[0] * v_[3], g)
                elif k_ == "DX":
                    good &= feq(v_[1], g)
                elif k_ == "BR":
                    good = False
                elif k_ == "E" and has_c(v_):
                    good &= feq(sp.diff(v_, X), g)
                elif k_ == "E":
                    good &= feq(v_, g) or feq(sp.diff(v_, X), g)
            ok(good, tag[:110], "(members agree with the chain's integrand)")
            if f is not None and g is not None and feq(g, f):
                cs = [v_ for k_, v_ in vals if k_ == "E" and has_c(v_)]
                if cs:
                    finals.append(cs[-1])
            continue
        if kind == "def":
            f, a, b, v = spec[1:5]
            good = True
            for t, (k_, v_) in zip(mem, vals):
                if k_ == "INT":
                    k0, a0, b0, h = v_
                    lim = a0 is not None and xeq(a0, a) and xeq(b0, b)
                    if lim and not has_x(b):
                        val = k0 * sp.Float(quad_value(h, a, b), 25)
                    elif lim:
                        val = k0 * sp.integrate(h.subs(X, T), (T, a, b))
                    else:
                        val = None
                    good &= lim and const_ratio(h, f) and val is not None and xeq(val, v)
                elif k_ == "BR":
                    Mz, F, lo, hi = v_
                    dd = sp.diff(Mz.subs(Z, F), X)
                    val = Mz.subs(Z, realify(F).subs(X, hi) - realify(F).subs(X, lo))
                    good &= const_ratio(dd, f) and xeq(lo, a) and xeq(hi, b) and xeq(val, v)
                elif k_ == "E":
                    good &= (not has_c(v_)) and xeq(v_, v)
                elif k_ == "DX":
                    good = False
            ok(good, tag[:110], f"(value {sp.sstr(v)[:30]})")
            ev = [v_ for k_, v_ in vals if k_ == "E"]
            if ev:
                finals.append(ev[-1])
            continue
    if kind == "ind":                                 # stand-alone primitives such as "x^2/2 + 2x + C"
        for m in maths(text):
            if len([q for q in split_top(m) if q.strip()]) == 1 and "\\int" not in m:
                try:
                    e = P(m)
                except Exception:  # noqa: BLE001
                    continue
                if has_c(e) and has_x(e):
                    ok(feq(sp.diff(e, X), spec[1]), f"{key}: {m}", "(d/dx = integrand)")
                    finals.append(e)
                    n_mem += 2
    ok(n_mem >= 2, f"{key}: members checked", str(n_mem))
    if final_key is not None:
        if not finals:
            ok(False, f"{key}: final answer found")
            return
        fin = finals[-1]
        if kind == "ind":
            good = feq(sp.diff(fin.subs(C, 0) - final_key, X), 0)
        else:
            good = xeq(fin, final_key)
        ok(good, f"{key}: final answer = key", f"{sp.sstr(fin)[:60]} vs {sp.sstr(final_key)[:60]}")


def check_side(key, text, f, F=None):
    """Side notes: u (or f(x)), du/dx, y = y(u), dy/du, int u^n du/dx dx = G(u), n."""
    Uf, Yu, n = None, None, None
    for mem in chains(text):
        lab = norm(mem[0])
        try:
            if lab in ("u", "f(x)"):
                vals = [P(t) for t in mem[1:]]
                Uf = vals[0]
                ok(all(feq(v, Uf) for v in vals), f"{key} side: u = {mem[1]}")
            elif lab in ("\\frac{du}{dx}", "f'(x)"):
                ok(Uf is not None and all(feq(P(t), sp.diff(Uf, X)) for t in mem[1:]), f"{key} side: du/dx = {mem[-1]}")
            elif lab == "y":
                Yu = P(mem[1])
                ok(F is not None and feq(Yu.subs(U, Uf), F), f"{key} side: y = {mem[1]} gives F")
            elif lab == "\\frac{dy}{du}":
                ok(Yu is not None and sp.simplify(P(mem[1]) - sp.diff(Yu, U)) == 0, f"{key} side: dy/du = {mem[1]}")
            elif lab == "n":
                n = P(mem[1])
                ratio = f / (Uf ** n * sp.diff(Uf, X))
                ok(feq(sp.diff(ratio, X), 0), f"{key} side: n = {mem[1]}: integrand = const * u^n du/dx")
            elif "\\int" in lab:
                body = re.sub(r"\\int\s*", "", prep(mem[0]))
                body = re.sub(r"\s*dx$", "", body).strip()
                e = _tex(body, EXTRA)
                powr = sp.simplify(e / UP)
                nn = sp.simplify(sp.diff(powr, U) * U / powr)
                G = P(mem[1])
                ok(sp.simplify(sp.diff(G, U) - U ** nn) == 0 and Uf is not None
                   and feq(sp.diff(f / (Uf ** nn * sp.diff(Uf, X)), X), 0), f"{key} side: int u^{nn} du/dx dx = {mem[1]}")
            else:
                ok(False, f"{key} side: unread statement {'='.join(mem)}")
        except Exception as err:  # noqa: BLE001
            ok(False, f"{key} side: {'='.join(mem)}", repr(err)[:100])
    return Uf


# ------------------------------------------------------------------ transcriptions
x = X
sq = sp.sqrt
D, I = "der", "ind"
TRANS = {
    # lesson examples: d tutor demo, y your turn, w worked example (der: F; ind: f; def: (f, a, b))
    "d1a": (D, (x**4 - 3)**5), "d1b": (I, 20 * x**3 * (x**4 - 3)**4), "d1c": (I, x**3 * (x**4 - 3)**4),
    "y1a": (D, (x**2 + 7)**3), "y1b": (I, 6 * x * (x**2 + 7)**2), "y1c": (I, x * (x**2 + 7)**2),
    "w36a": (D, (x**3 + 5)**4), "w36b": (I, 12 * x**2 * (x**3 + 5)**3), "w36c": (I, x**2 * (x**3 + 5)**3),
    "d2a": (D, 1 / (4 + x**3)), "d2b": (I, x**2 / (4 + x**3)**2), "y2a": (D, 1 / (9 + x**2)), "y2b": (I, x / (9 + x**2)**2),
    "w37a": (D, 1 / (1 + x**2)), "w37b": (I, x / (1 + x**2)**2),
    "d3": (I, x**3 * (x**4 + 2)**5), "y3": (I, x * (x**2 - 3)**4), "w38": (I, x**2 * (x**3 + 5)**3),
    "d4a": (I, x * sq(9 - x**2)), "d4b": ("def", (x * sq(9 - x**2), 0, 3)), "d4c": ("none", (x * sq(9 - x**2), 0, 4)),
    "y4a": (I, x * sq(4 - x**2)), "y4b": ("def", (x * sq(4 - x**2), 0, 2)), "y4c": ("none", (x * sq(4 - x**2), 0, 3)),
    "w39a": (I, x * sq(1 - x**2)), "w39b": ("none", (x * sq(1 - x**2), 0, 2)),
    # Exercise 5I (PDF 283-286)
    "1a": (D, (2 * x + 3)**4), "1bi": (I, 8 * (2 * x + 3)**3), "1bii": (I, 16 * (2 * x + 3)**3),
    "2a": (D, (3 * x - 5)**3), "2bi": (I, 9 * (3 * x - 5)**2), "2bii": (I, 27 * (3 * x - 5)**2),
    "3a": (D, (1 + 4 * x)**5), "3bi": (I, 20 * (1 + 4 * x)**4), "3bii": (I, 10 * (1 + 4 * x)**4),
    "4a": (D, (1 - 2 * x)**4), "4bi": (I, -8 * (1 - 2 * x)**3), "4bii": (I, -2 * (1 - 2 * x)**3),
    "5a": (D, (4 * x + 3)**-1), "5bi": (I, -4 * (4 * x + 3)**-2), "5bii": (I, (4 * x + 3)**-2),
    "6a": (D, (2 * x - 5)**R(1, 2)), "6bi": (I, (2 * x - 5)**R(-1, 2)), "6bii": (I, R(1, 3) * (2 * x - 5)**R(-1, 2)),
    "7a": (D, (x**2 + 3)**4), "7bi": (I, 8 * x * (x**2 + 3)**3), "7bii": (I, 40 * x * (x**2 + 3)**3),
    "8a": (D, (x**3 - 1)**5), "8bi": (I, 15 * x**2 * (x**3 - 1)**4), "8bii": (I, 3 * x**2 * (x**3 - 1)**4),
    "9a": (D, sq(2 * x**2 + 3)), "9bi": (I, 2 * x / sq(2 * x**2 + 3)), "9bii": (I, x / sq(2 * x**2 + 3)),
    "10a": (D, (sq(x) + 1)**3), "10bi": (I, 3 * (sq(x) + 1)**2 / (2 * sq(x))), "10bii": (I, (sq(x) + 1)**2 / sq(x)),
    "11a": (D, (x**3 + 3 * x**2 + 5)**4), "11bi": (I, 12 * (x**2 + 2 * x) * (x**3 + 3 * x**2 + 5)**3),
    "11bii": (I, (x**2 + 2 * x) * (x**3 + 3 * x**2 + 5)**3),
    "12a": (D, (5 - x**2 - x)**7), "12bi": (I, (-14 * x - 7) * (5 - x**2 - x)**6), "12bii": (I, (2 * x + 1) * (5 - x**2 - x)**6),
    "13a": (I, 5 * (5 * x + 4)**3), "13b": (I, -3 * (1 - 3 * x)**5), "13c": (I, 2 * x * (x**2 - 5)**7),
    "13d": (I, 3 * x**2 * (x**3 + 7)**4), "13e": (I, 6 * x / (3 * x**2 + 2)**2), "13f": (I, -6 * x**2 / sq(9 - 2 * x**3)),
    "14a": (I, 10 * x * (5 * x**2 + 3)**2), "14b": (I, 2 * x * (x**2 + 1)**3), "14c": (I, 12 * x**2 * (1 + 4 * x**3)**5),
    "14d": (I, x * (1 + 3 * x**2)**4), "14e": (I, x**3 * (1 - x**4)**7), "14f": (I, 3 * x**2 * sq(x**3 - 1)),
    "14g": (I, x * sq(5 * x**2 + 1)), "14h": (I, 2 * x / sq(x**2 + 3)), "14i": (I, (x + 1) / sq(4 * x**2 + 8 * x + 1)),
    "14j": (I, x / (x**2 + 5)**3),
    "15a": ("def", (x**2 * (x**3 + 1)**4, -1, 1)), "15b": ("def", (x / (5 * x**2 + 1)**3, 0, 1)),
    "15c": ("def", (x * sq(1 - 4 * x**2), 0, R(1, 2))), "15d": ("def", ((x + 5) * (x**2 + 10 * x + 3)**2, -3, -1)),
    "16a": (I, (1 - 1 / x)**5 / x**2), "16b": ("def", (1 / (sq(x) * (1 + sq(x))**2), 1, 4)),
    # past papers
    "pp1": (I, x / sq(1 - x**2)), "pp2": (I, x / sq(9 - x**2)),
    # Chapter 5 review (PDF 287-289)
    "r1a": ("def", (3 * x**2, 0, 1)), "r1b": ("def", (x, 1, 2)), "r1c": ("def", (4 * x**3, 2, 5)), "r1d": ("def", (x**4, -1, 1)),
    "r1e": ("def", (2 * x, -4, -2)), "r1f": ("def", (x**2, -3, -1)), "r1g": ("def", (x + 3, 0, 2)), "r1h": ("def", (2 * x - 5, -1, 4)),
    "r1i": ("def", (x**2 - 2 * x + 1, -3, 1)),
    "r2a": ("def", (x * (x - 1), 1, 3)), "r2b": ("def", ((x + 1) * (x - 3), -1, 0)), "r2c": ("def", ((2 * x - 1)**2, 0, 1)),
    "r3a": ("def", ((x**2 - 3 * x) / x, 1, 2)), "r3b": ("def", ((3 * x**4 - 4 * x**2) / x**2, 2, 3)),
    "r3c": ("def", ((x**3 - 2 * x**4) / x**2, -2, -1)),
    "r5a": ("def", (x**3 - 5 * x + 4, 3, 3)), "r5b": ("def", (x**3, -2, 2)), "r5c": ("def", (x**3 - 9 * x, -3, 3)),
    "r8a": (I, x + 2), "r8b": (I, x**3 + 3 * x**2 - 5 * x + 1), "r8c": (I, x * (x - 1)), "r8d": (I, (x - 3) * (2 - x)),
    "r8e": (I, x**-2), "r8f": (I, 1 / x**7), "r8g": (I, sq(x)), "r8h": (I, (x + 1)**4), "r8i": (I, (2 * x - 3)**5),
    "r12a": (D, (3 * x + 4)**6), "r12bi": (I, 18 * (3 * x + 4)**5), "r12bii": (I, 9 * (3 * x + 4)**5),
    "r13a": (D, (x**2 - 1)**3), "r13bi": (I, 6 * x * (x**2 - 1)**2), "r13bii": (I, x * (x**2 - 1)**2),
    "r14a": (I, 3 * x**2 * (x**3 + 1)**4), "r14b": (I, 2 * x / (x**2 - 5)**3),
    "r15": ("def", (x / sq(x**2 + 3), 0, 1)),
}
# blocks with no printed question of their own (figure questions, parts of a question, second notations)
EXTRA_SPEC = {
    "w38f": ("w38", None), "w39af": ("w39a", None),
    "r9a": ("def", (x**2, -3, 1)), "r9b": ("def", (x**3 - 4 * x, -2, 0)), "r9c": ("def", (x**2 - 4 * x + 3, 1, 3)),
    "r9d": ("def", (2 * x - 6, 3, 4)), "r9e": ("def", (x - x**2, 0, 1)), "r9f": ("def", (x**2 - x**4, -1, 1)),
    "r9g": ("def", (3 * x - 2 - x**2, 1, 2)), "r9h": ("def", ((1 - x**2) - (x - 1), -2, 1)),
    "r10b": ("def", ((x + 2) - (x**2 - 3 * x + 5), 1, 3)), "17d": ("def", (x * sq(x**2 - 1), 1, 3)),
    "18b": ("def2", (x * (7 - x**2)**3, 0, sq(7))), "17b": (D, x * sq(x**2 - 1)), "18a": (D, x * (7 - x**2)**3),
}
KEY = {
    # hand values for the lesson examples
    "d1a": 20 * x**3 * (x**4 - 3)**4, "d1c": (x**4 - 3)**5 / 20, "y1a": 6 * x * (x**2 + 7)**2, "y1c": (x**2 + 7)**3 / 6,
    "w36a": 12 * x**2 * (x**3 + 5)**3, "w36c": (x**3 + 5)**4 / 12,
    "d2a": -3 * x**2 / (4 + x**3)**2, "d2b": -1 / (3 * (4 + x**3)), "y2a": -2 * x / (9 + x**2)**2, "y2b": -1 / (2 * (9 + x**2)),
    "w37a": -2 * x / (1 + x**2)**2, "w37b": -1 / (2 * (1 + x**2)),
    "d3": (x**4 + 2)**6 / 24, "y3": (x**2 - 3)**5 / 10, "w38": (x**3 + 5)**4 / 12, "w38f": (x**3 + 5)**4 / 12,
    "d4a": -(9 - x**2)**R(3, 2) / 3, "d4b": 9, "y4a": -(4 - x**2)**R(3, 2) / 3, "y4b": R(8, 3),
    "w39a": -(1 - x**2)**R(3, 2) / 3, "w39af": -(1 - x**2)**R(3, 2) / 3,
    # textbook answers, Exercise 5I (PDF 893)
    "1a": 8 * (2 * x + 3)**3, "1bi": (2 * x + 3)**4, "1bii": 2 * (2 * x + 3)**4,
    "2a": 9 * (3 * x - 5)**2, "2bi": (3 * x - 5)**3, "2bii": 3 * (3 * x - 5)**3,
    "3a": 20 * (1 + 4 * x)**4, "3bi": (1 + 4 * x)**5, "3bii": (1 + 4 * x)**5 / 2,
    "4a": -8 * (1 - 2 * x)**3, "4bi": (1 - 2 * x)**4, "4bii": (1 - 2 * x)**4 / 4,
    "5a": -4 * (4 * x + 3)**-2, "5bi": (4 * x + 3)**-1, "5bii": -(4 * x + 3)**-1 / 4,
    "6a": (2 * x - 5)**R(-1, 2), "6bi": (2 * x - 5)**R(1, 2), "6bii": (2 * x - 5)**R(1, 2) / 3,
    "7a": 8 * x * (x**2 + 3)**3, "7bi": (x**2 + 3)**4, "7bii": 5 * (x**2 + 3)**4,
    "8a": 15 * x**2 * (x**3 - 1)**4, "8bi": (x**3 - 1)**5, "8bii": (x**3 - 1)**5 / 5,
    "9a": 2 * x / sq(2 * x**2 + 3), "9bi": sq(2 * x**2 + 3), "9bii": sq(2 * x**2 + 3) / 2,
    "10a": 3 * (sq(x) + 1)**2 / (2 * sq(x)), "10bi": (sq(x) + 1)**3, "10bii": R(2, 3) * (sq(x) + 1)**3,
    "11a": 12 * (x**2 + 2 * x) * (x**3 + 3 * x**2 + 5)**3, "11bi": (x**3 + 3 * x**2 + 5)**4, "11bii": (x**3 + 3 * x**2 + 5)**4 / 12,
    "12a": -7 * (2 * x + 1) * (5 - x**2 - x)**6, "12bi": (5 - x**2 - x)**7, "12bii": -(5 - x**2 - x)**7 / 7,
    "13a": (5 * x + 4)**4 / 4, "13b": (1 - 3 * x)**6 / 6, "13c": (x**2 - 5)**8 / 8, "13d": (x**3 + 7)**5 / 5,
    "13e": -1 / (3 * x**2 + 2), "13f": 2 * sq(9 - 2 * x**3),
    "14a": (5 * x**2 + 3)**3 / 3, "14b": (x**2 + 1)**4 / 4, "14c": (1 + 4 * x**3)**6 / 6, "14d": (1 + 3 * x**2)**5 / 30,
    "14e": -(1 - x**4)**8 / 32, "14f": R(2, 3) * (x**3 - 1)**R(3, 2), "14g": (5 * x**2 + 1)**R(3, 2) / 15,
    "14h": 2 * sq(x**2 + 3), "14i": sq(4 * x**2 + 8 * x + 1) / 4, "14j": -1 / (4 * (x**2 + 5)**2),
    "15a": R(32, 15), "15b": R(7, 144), "15c": R(1, 12), "15d": 936,
    "16a": (1 - 1 / x)**6 / 6, "16b": R(1, 3),
    # 17(b) f'(x); 17(d) area: the key prints it as part "c" (a label slip), the value is part d's
    "17b": (2 * x**2 - 1) / sq(x**2 - 1), "17d": R(16, 3) * sq(2), "18b": R(2401, 4),
    # past-paper answers: options D (Ascham) and A (SBHS)
    "pp1": -sq(1 - x**2), "pp2": -sq(9 - x**2),
    # Chapter 5 review (PDF 893 right column foot, PDF 894 left column)
    "r1a": 1, "r1b": R(3, 2), "r1c": 609, "r1d": R(2, 5), "r1e": -12, "r1f": R(26, 3), "r1g": 8, "r1h": -10, "r1i": R(64, 3),
    "r2a": R(14, 3), "r2b": R(-5, 3), "r2c": R(1, 3), "r3a": R(-3, 2), "r3b": 15, "r3c": R(-37, 6),
    "r8a": x**2 / 2 + 2 * x, "r8b": x**4 / 4 + x**3 - R(5, 2) * x**2 + x, "r8c": x**3 / 3 - x**2 / 2,
    "r8d": -x**3 / 3 + R(5, 2) * x**2 - 6 * x, "r8e": -1 / x, "r8f": -1 / (6 * x**6), "r8g": R(2, 3) * x**R(3, 2),
    "r8h": (x + 1)**5 / 5, "r8i": (2 * x - 3)**6 / 12,
    "r12a": 18 * (3 * x + 4)**5, "r12bi": (3 * x + 4)**6, "r12bii": (3 * x + 4)**6 / 2,
    "r13a": 6 * x * (x**2 - 1)**2, "r13bi": (x**2 - 1)**3, "r13bii": (x**2 - 1)**3 / 6,
    "r14a": (x**3 + 1)**5 / 5, "r14b": -1 / (2 * (x**2 - 5)**2), "r10b": R(4, 3),
}
AREA_KEY = {"r9a": R(28, 3), "r9b": 4, "r9c": R(4, 3), "r9d": 1, "r9e": R(1, 6), "r9f": R(4, 15), "r9g": R(1, 6), "r9h": R(9, 2)}
# inside functions u for the identity chains of the lesson blocks and the tips
UFUN = {"w36a": x**3 + 5, "d1a": x**4 - 3, "y1a": x**2 + 7, "c1_chain": x**3 + 5, "t36a": x**3 + 5, "t37a": 1 + x**2,
        "t38": x**3 + 5, "t39a": 1 - x**2}

les, ans = read("l5i.html"), read("a_5i.html")
both = les + ans


def exact_value(f, a, b):
    if f.has(sp.sqrt(X)) or not f.is_rational_function(X):
        ex = sp.integrate(f, (X, a, b))
    else:
        ex = sp.integrate(f, (X, a, b))
    return sp.nsimplify(sp.simplify(ex)) if not ex.has(sp.Integral) else None


# ------------------------------------------------------------------ questions as printed
SPEC = {}
for k, (kind, tr) in TRANS.items():
    q = block(les, "data-q", k)
    if q is None:
        continue
    ms = maths(q)
    try:
        if kind == D:
            m0 = norm(ms[0])
            m0 = m0[len("\\frac{d}{dx}"):] if m0.startswith("\\frac{d}{dx}") else m0
            ok(feq(P(m0), tr), f"q {k}: printed function = textbook", ms[0][:60])
            SPEC[k] = (D, sp.sympify(tr))
            continue
        ints = [[p_ for p_ in split_top(m) if "\\int" in p_][0] for m in ms if "\\int" in m]
        if kind == I and not ints:
            ok(feq(P(ms[-1]), tr), f"q {k}: printed function = textbook", ms[-1][:60])
            SPEC[k] = (I, sp.sympify(tr))
            continue
        ok(len(ints) >= 1, f"q {k}: integral printed")
        kk, a, b, f, var = parse_int(ints[0])
        if kind == I:
            ok(a is None and feq(kk * f, tr), f"q {k}: printed integral = textbook", ints[0][:60])
            SPEC[k] = (I, sp.sympify(tr))
        else:
            ftr, atr, btr = tr
            ok(a is not None and feq(kk * f, ftr) and neq(a, atr) and neq(b, btr), f"q {k}: printed integral = textbook", ints[0][:60])
            if kind == "def":
                v = sp.Float(quad_value(sp.sympify(ftr), atr, btr), 25)
                ex = exact_value(sp.sympify(ftr), atr, btr)
                ok(ex is not None and neq(ex, v), f"q {k}: sympy exact value = quadrature", sp.sstr(ex))
                SPEC[k] = ("def", sp.sympify(ftr), atr, btr, ex if ex is not None else v)
            else:
                SPEC[k] = ("none", sp.sympify(ftr), atr, btr)
    except Exception as err:  # noqa: BLE001
        ok(False, f"q {k}: read", repr(err)[:120])

for k, (kind, tr) in EXTRA_SPEC.items():
    if tr is None:
        SPEC[k] = SPEC[kind]
    elif kind in ("def", "def2"):
        f, a, b = tr
        ex = exact_value(f, a, b)
        if kind == "def2":                        # 18(b): twice the integral over [0, sqrt 7] (odd curve)
            ex = 2 * ex
        SPEC[k] = ("def", f, a, b, ex)
    else:
        SPEC[k] = (kind, tr)

# ------------------------------------------------------------------ solutions and answers
DONE = set()
for k, sp_ in SPEC.items():
    if sp_[0] == "none":
        continue
    if k in ("r15", "r5a", "r5b", "r5c"):
        continue
    blk = block(both, "data-c", k)
    if blk is None:
        continue
    DONE.add(k)
    fk = sp.sympify(KEY[k]) if k in KEY else None
    side = re.findall(r'data-s="' + re.escape(k) + '"', both)
    Uf = None
    if side:
        sb = block(both, "data-s", k)
        f_side = sp_[1] if sp_[0] in (I, "def") else None
        F_side = sp_[1] if sp_[0] == D else None
        if sp_[0] == "def" and k == "18b":
            f_side = sp_[1]
        Uf = check_side(k, sb, f_side if f_side is not None else sp.diff(sp_[1], X), F_side)
    try:
        spec = sp_ if sp_[0] != "def" else sp_[:5]
        check_block(k, blk, spec, fk, UFUN.get(k, Uf))
    except Exception as err:  # noqa: BLE001
        ok(False, f"{k}: check", repr(err)[:140])

# every question part with a printed answer in the key has an answer block
need = [k for k in TRANS if not k.startswith(("w", "r5", "r15")) and TRANS[k][0] != "none" and k not in ("d1b", "y1b", "w36b")]
ans_keys = set(re.findall(r'data-c="([^"]+)"', ans))
ok(all(k in ans_keys for k in need), "every question part has an answer block in a_5i.html",
   str([k for k in need if k not in ans_keys]))
ok(all(k in KEY for k in TRANS if not k.startswith(("w", "r5", "r15", "d4c", "y4c")) and TRANS[k][0] != "none"
       and k not in ("d1b", "y1b", "w36b")), "every checked part has a key or hand value",
   str([k for k in TRANS if k not in KEY and TRANS[k][0] != "none"]))

# "a primitive" parts (b of the Example 36 pattern) and the worked examples' second notations
for k in ("d1b", "y1b", "w36b"):
    blk = block(both, "data-c", k)
    if blk is not None:
        check_block(k, blk, SPEC[k], None, UFUN.get(k))
        ok(re.search(r"=\(x\^\d[^)]*\)\^\d\\\)", norm(blk)) is not None or "Reversing this" in blk, f"{k}: reversing line printed")

# meaningless definite integrals (Worked example 39b and the demo parts c)
for k, lim in (("w39b", 1), ("d4c", 3), ("y4c", 2)):
    blk = block(both, "data-c", k)
    f, a, b = SPEC[k][1:4]
    ok(blk is not None and "meaningless" in blk and f"undefined for \\(x>{lim}\\)" in blk, f"{k}: meaningless, undefined for x > {lim}")
    rad = [a_ for a_ in sp.preorder_traversal(f) if a_.is_Pow and a_.exp == R(1, 2)][0].base
    ok(neq(rad.subs(X, lim), 0) and float(rad.subs(X, lim + R(1, 2))) < 0 and lim < b, f"{k}: radicand 0 at x = {lim}, negative beyond, b = {b}")

# tips after the worked examples
TIPS = {"t36a": ("w36c",), "t36c": ("w36c",), "t37a": ("w37b",), "t37b": ("w37b",), "t38": ("w38",), "t39a": ("w39a",)}
for tk, (wk,) in TIPS.items():
    blk = block(les, "data-c", tk)
    if blk is not None:
        check_block(tk, blk, SPEC[wk], None, UFUN.get(tk))
ok(les.count("Steps the book skips: Worked example") == 4, "a tip after each of Worked examples 36-39")
WE = re.findall(r'<span class="tag">Worked example (\d+)</span>.*?<div class="box tip"><div class="bt">Steps the book skips: Worked example (\d+)', les, re.S)
ok([w[0] for w in WE] == ["36", "37", "38", "39"] and all(w[0] == w[1] for w in WE), "each tip follows its worked example", str(WE))
for wnum in ("36", "37", "38", "39"):
    seg = les.split(f'<span class="tag">Worked example {wnum}</span>')[1].split('<div class="box')[0]
    ok(not re.search(r"Here \\\(n=|so divide by|Putting \\\(u", seg), f"WE{wnum}: no pack prose inside the example box")

# concept boxes: the chain-rule example, the formula derivation, Boxes 21 and 22, the Q13 display
for k, spec, Uf in (("c1_box", (D, (X**3 + 5)**4), None), ("c1_chain", (D, (X**3 + 5)**4), X**3 + 5)):
    blk = block(les, "data-c", k)
    if blk is not None:
        check_block(k, blk, spec, 4 * (X**3 + 5)**3 * 3 * X**2, Uf)
FORMS = {
    "c3_d": [r"\frac{d}{dx}(u^n)=nu^{n-1}\frac{du}{dx}", r"\frac{d}{dx}\big(f(x)\big)^n=n\big(f(x)\big)^{n-1}f'(x)"],
    "c3_r": [r"\int u^{n-1}\frac{du}{dx}\,dx=\frac{u^n}{n}", r"\int\big(f(x)\big)^{n-1}f'(x)\,dx=\frac{\big(f(x)\big)^n}{n}"],
    "c3_f": [r"\int u^n\frac{du}{dx}\,dx=\frac{u^{n+1}}{n+1}", r"\int\big(f(x)\big)^nf'(x)\,dx=\frac{\big(f(x)\big)^{n+1}}{n+1}"],
    "c4_box": [r"\int u^n\frac{du}{dx}\,dx=\frac{u^{n+1}}{n+1}+C", r"\int\big(f(x)\big)^nf'(x)\,dx=\frac{\big(f(x)\big)^{n+1}}{n+1}+C"],
    "q13_form": [r"\int f'(x)\big(f(x)\big)^n\,dx=\frac{\big(f(x)\big)^{n+1}}{n+1}+C", r"\int u^n\frac{du}{dx}\,dx=\frac{u^{n+1}}{n+1}+C"],
}
for k, strs in FORMS.items():
    blk = block(les, "data-c", k)
    ok(blk is not None and all(s_ in blk for s_ in strs), f"{k}: formula printed as in the textbook")
g_ = sp.Function("g")(X)
ok(sp.simplify(sp.diff(g_**N, X) - N * g_**(N - 1) * sp.diff(g_, X)) == 0, "c3_d: chain rule for powers (generic g, n)")
ok(sp.simplify(sp.diff(g_**(N + 1) / (N + 1), X) - g_**N * sp.diff(g_, X)) == 0, "c3_f / Box 22: the formula differentiates back")
ok(sp.simplify(sp.diff(g_**N / N, X) - g_**(N - 1) * sp.diff(g_, X)) == 0, "c3_r: the reversed forms differentiate back")
for s_ in ("Once a chain-rule differentiation, or any differentiation, has been performed, the result can be written down in reverse as an indefinite integral.",
           "The vital step in using this formula is to identify \\(u\\) or \\(f(x)\\) and its derivative.",
           "It is best not to add the arbitrary constant until the last line, because it would be pointless to divide \\(C\\) by 12 as well.",
           "Notice that the two notations differ only in the working in the right-hand column.",
           "To use the formula, we have to write the integrand as a product."):
    ok(les.count(s_) == 1, f"textbook sentence printed once: {s_[:60]}")

# ------------------------------------------------------------------ Exercise Q17 and Q18 (custom)
F17 = X * sp.sqrt(X**2 - 1)
a17 = ans.split('<span class="an">17</span>')[1].split('<span class="an">18</span>')[0]
ok("\\(x\\le-1\\) or \\(x\\ge1\\)" in a17, "17a: domain x <= -1 or x >= 1")
xr = sp.Symbol("x", real=True)
dom = sp.solve_univariate_inequality(xr**2 - 1 >= 0, xr, relational=False)
ok(dom == sp.Union(sp.Interval(-sp.oo, -1), sp.Interval(1, sp.oo)), "17a: sympy domain", str(dom))
crit = sp.solve(sp.Eq(2 * xr**2 - 1, 0), xr)
ok(all(abs(float(c)) < 1 for c in crit) and "\\(x=\\pm\\dfrac{1}{\\sqrt2}\\)" in a17, "17b: f'(x) = 0 only at x = +-1/sqrt2, outside the domain")
b17c = block(ans, "data-c", "17c")
m17 = [m for m in maths(b17c) if m.startswith("f(-x)")]
if ok(len(m17) == 1, "17c: odd-function chain printed"):
    mem = split_top(m17[0])
    ok(feq(P(mem[1]), -F17) and feq(P(mem[2]), -F17) and norm(mem[3]) == "-f(x)", "17c: f(-x) = -f(x)", m17[0])
ok(sp.simplify(F17.subs(X, -xr) + F17.subs(X, xr)) == 0, "17c: sympy f(-x) + f(x) = 0")
ok("{{svg:a5i_17c}}" in a17 and "{{svg:a5i_18a}}" in ans and "{{svg:a5i_r10b}}" in ans, "sketches included")
F18 = X * (7 - X**2)**3
d18 = sp.diff(F18, X)
st = sorted(sp.solve(sp.Eq(d18, 0), X), key=float)
ok([float(s_) for s_ in st] == [-math.sqrt(7), -1, 1, math.sqrt(7)], "18a: stationary points x = +-1, +-sqrt7", str(st))
ok(F18.subs(X, 1) == 216 and F18.subs(X, -1) == -216, "18a: y(1) = 216, y(-1) = -216")
sgn = lambda v: float(d18.subs(X, v))  # noqa: E731
ok(sgn(0.9) > 0 > sgn(1.1) and sgn(-1.1) < 0 < sgn(-0.9) and sgn(2.5) < 0 and sgn(2.8) < 0 and sgn(-2.5) < 0 and sgn(-2.8) < 0,
   "18a: max at 1, min at -1, horizontal inflections at +-sqrt7 (sign tests)")
a18 = ans.split('<span class="an">18</span>')[1].split("{{ahead")[0]
ok("\\((1,216)\\) is a maximum turning point" in a18 and "\\((-1,-216)\\) is a minimum turning point" in a18
   and "horizontal points of inflection" in a18, "18a: nature printed")
ok(neq(2 * sp.integrate(F18, (X, 0, sp.sqrt(7))), R(2401, 4)) and "600\\tfrac14" in a18, "18b: area 600 1/4")
ok(neq(sp.integrate(F18, (X, -sp.sqrt(7), sp.sqrt(7))), 0), "18b: signed integral over [-sqrt7, sqrt7] is 0 (odd), so twice the half")
ok(not feq(sp.diff(F17, X), 0), "17b: f'(x) not identically 0")

# ------------------------------------------------------------------ review: Q4, Q5, Q6, Q7, Q9 areas, Q11, Q15
kk_ = sp.Symbol("k")
ok(sp.simplify(sp.integrate(5, (X, 4, kk_)) - (5 * kk_ - 20)) == 0 and sp.solve(5 * kk_ - 20 - 10, kk_) == [6], "r4a: 5k - 20, k = 6")
b4 = block(ans, "data-c", "r4aii")
ok(b4 is not None and "\\(k=6\\)" in b4 and "\\(5k=30\\)" in b4, "r4a ii printed k = 6")
sol = sp.solve(sp.integrate(2 * X - 1, (X, 0, kk_)) - 6, kk_)
ok(sp.simplify(sp.integrate(2 * X - 1, (X, 0, kk_)) - (kk_**2 - kk_)) == 0 and sorted(sol) == [-2, 3], "r4b: k^2 - k = 6, k = 3 or -2")
b4 = block(ans, "data-c", "r4bii")
ok(b4 is not None and "\\((k-3)(k+2)=0\\)" in b4 and "\\(k=3\\)" in b4 and sp.expand((kk_ - 3) * (kk_ + 2)) == kk_**2 - kk_ - 6,
   "r4b ii printed k = 3")
for k, why in (("r5a", "zero width"), ("r5b", "odd"), ("r5c", "odd")):
    f, a, b = SPEC[k][1:4]
    blk = block(ans, "data-c", k)
    ok(sp.integrate(f, (X, a, b)) == 0 and blk is not None and blk.strip().startswith("<b>") and "\\(0\\)" in blk and why in blk,
       f"{k}: value 0, reason '{why}'")
    if why == "odd":
        ok(sp.simplify(f.subs(X, -X) + f) == 0, f"{k}: integrand is odd (sympy)")
        m5 = [m for m in maths(blk) if m.startswith("(-x)")][0]
        mem = split_top(m5)
        ok(feq(P(mem[0]), -f) and feq(P(mem[1]), -f), f"{k}: printed odd identity", m5)
pw6a = sp.Piecewise((2 * X, X <= 2), (4, True))
pw6b = 2 - X
for k, val, ref in (("r6a", 8, sp.integrate(pw6a, (X, 0, 3))), ("r6b", R(3, 2), sp.integrate(pw6b, (X, 0, 3)))):
    blk = block(ans, "data-c", k)
    ch = [c for c in chains(blk)]
    ch = [c for c in ch if any("\\int" in m for m in c)]
    ok(len(ch) == 1, f"{k}: one chain with the integral")
    mem = [m for m in ch[0] if "\\int" not in m]
    ok(len(mem) >= 3 and all(neq(P(m), val) for m in mem) and neq(ref, val), f"{k}: area formulae give {val}", "=".join(mem)[:80])
for k, g, a, b, Aref in (("r7ai", 4 - T, -2, X, 4 * X - X**2 / 2 + 10), ("r7aii", T**-2, 2, X, R(1, 2) - 1 / X)):
    q = block(les, "data-q", k)
    m = [mm for mm in maths(q) if "\\int" in mm][0]
    kq, aq, bq, hq, vq = parse_int(m.split("=", 1)[1])
    ok(vq == T and neq(aq, a) and bq == X and feq(hq, g.subs(T, X)), f"q {k}: printed signed area function", m)
    ex = sp.integrate(g, (T, a, X))
    ok(feq(ex, Aref), f"{k}: sympy A(x)", sp.sstr(ex))
    blk = block(ans, "data-c", k)
    check_block(k, blk, ("def", g.subs(T, X), a, X, ex), Aref)
for k, F in (("r7bi", 4 * X - X**2 / 2 + 10), ("r7bii", R(1, 2) - 1 / X)):
    blk = block(ans, "data-c", k)
    check_block(k, blk, (D, F), sp.diff(F, X))
ok(feq(sp.diff(sp.integrate(4 - T, (T, -2, X)), X), 4 - X) and feq(sp.diff(sp.integrate(T**-2, (T, 2, X)), X), X**-2), "r7b: sympy d/dx A(x)")
for k, g, a in (("r7ci", T**5 - 5 * T**3 + 1, 7), ("r7cii", (T**2 + 4) / (T**2 - 1), 3)):
    q = block(les, "data-q", k)
    m = [mm for mm in maths(q) if "\\int" in mm][0]
    _, aq, bq, hq, vq = parse_int(norm(m)[len("\\frac{d}{dx}"):])
    ok(neq(aq, a) and feq(hq, g.subs(T, X)), f"q {k}: printed", m)
    blk = block(ans, "data-c", k)
    val = P(maths(blk)[0])
    ok(feq(val, g.subs(T, X)), f"{k}: answer = integrand with t replaced by x", maths(blk)[0])
    ok(feq(sp.diff(sp.integrate(g, (T, a, X)), X), g.subs(T, X)), f"{k}: sympy d/dx of the integral (FTC)")
for k, area in AREA_KEY.items():
    blk = block(ans, "data-c", k)
    am = [m for m in maths(blk) if "\\text{ u}^2" in m]
    ok(len(am) == 1 and neq(P(am[0]), area) and neq(abs(SPEC[k][4]), area), f"{k}: area = key {area}", am[0] if am else "")
for k, area in (("r10b", R(4, 3)), ("17d", R(16, 3) * sp.sqrt(2)), ("18b", R(2401, 4))):
    blk = block(ans, "data-c", k)
    ok("\\text{ u}^2" in blk and neq(SPEC[k][4], area), f"{k}: area with units = {area}")
# intersections in review Q10 (the sketch and limits)
ok(sorted(sp.solve(sp.Eq(X**2 - 3 * X + 5, X + 2), X)) == [1, 3], "r10: curves meet at x = 1 and x = 3")
# trapezoidal rule (review Q11)
b11 = block(ans, "data-c", "r11a")
ok("\\(h=1\\)" in b11 and "<td>2</td><td>4</td><td>8</td>" in b11, "r11a: h = 1 and the values 2, 4, 8")
t11a = 1 / 2 * (2 + 2 * 4 + 8)
ok(t11a == 9 and "=9\\)" in b11.replace(" ", ""), "r11a: trapezoidal value 9 (key 9)")
b11 = block(ans, "data-c", "r11b")
vals = [float(v) for v in re.findall(r"<td>(0(?:\.\d+)?)</td>", b11)]
xs = [1, 1.5, 2, 2.5, 3]
ok(len(vals) == 5 and all(abs(v - round(math.log10(x_), 4)) < 1e-9 for v, x_ in zip(vals, xs)), "r11b: table of log10 x to 4 d.p.", str(vals))
tb = 0.25 * (vals[0] + 2 * sum(vals[1:4]) + vals[4])
exact_t = 0.25 * (math.log10(1) + 2 * (math.log10(1.5) + math.log10(2) + math.log10(2.5)) + math.log10(3))
ok(abs(2 * sum(vals[1:4]) + vals[4] - 2.2271) < 1e-9 and "2.2271" in b11 and "0.5568" in b11 and abs(tb - 0.556775) < 1e-9,
   "r11b: 2.2271 and 0.5568 printed and recomputed", f"{tb:.6f}")
ok(f"{exact_t:.2g}" == "0.56" and "\\doteqdot0.56" in b11.replace(" ", ""), "r11b: 0.56 to two significant figures (key 0.56)", f"{exact_t:.6f}")
ok(neq(SPEC["r15"][4], 2 - sp.sqrt(3)), "r15: value 2 - sqrt3 (show that, no answer printed)")
ok("r15" not in ans_keys and "r10a" not in ans_keys and "r4ai" not in ans_keys, "show-that parts not answered")

# ------------------------------------------------------------------ past papers: options, labels, hints
pp = les.split("<!-- ============ Past papers ============ -->")[1].split("<!-- ============ Chapter review ============ -->")[0]
opts1 = re.findall(r"<span>([A-D])\.&ensp;\\\((.*?)\\\)</span>", pp.split('data-q="pp2"')[0])
opts2 = re.findall(r"<span>([A-D])\.&ensp;\\\((.*?)\\\)</span>", pp.split('data-q="pp2"')[1])
for name, opts, f, right in (("pp1", opts1, X / sp.sqrt(1 - X**2), "D"), ("pp2", opts2, X / sp.sqrt(9 - X**2), "A")):
    good = [L for L, o in opts if feq(sp.diff(P(o), X), f)]
    ok(len(opts) == 4 and good == [right], f"{name}: only option {right} differentiates to the integrand", str(good))
ok("The answer is <b>D</b>" in ans and "The answer is <b>A</b>" in ans, "past papers: answers D and A printed")
LAB1 = "Ascham School, 2020, Mathematics Extension 1 Trial HSC <span style=\"white-space:nowrap\">Examination,&nbsp;Q5</span>"
LAB2 = "Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q10</span>"
ok(les.count(LAB1) == 1 and ans.count(LAB1) == 1 and les.count(LAB2) == 1 and ans.count(LAB2) == 1, "source labels in both PDFs")
ok("<b>2 marks</b>" in pp and "Suggested time: 5 minutes" in pp, "pp-intro: 2 marks, 5 minutes")
hints = re.findall(r'<div class="hint"><b>Hint:</b>(.*?)</div>', les)
BAD = ("chain", "substitut", "product", "quotient", "rule", "derivative", "differentiat", "part (", "worked example", "formula")
ok(len(hints) == 2 and all(h.strip().endswith("?") and not any(b_ in h.lower() for b_ in BAD) and not re.search(r"\d", h) for h in hints),
   "hints are neutral questions", str(hints))
note = "For more timed practice, do Questions 14(g), 14(i), 14(j), 15(b), 15(d), 16(b) and 17(d) above in 25 minutes."
ok(pp.count(note) == 1, "timed-practice note printed")
for item in re.findall(r"(\d+)\(([a-z]+)\)", note):
    ok(f"{item[0]}{item[1]}" in TRANS or item == ("17", "d"), f"note names an existing part: Q{item[0]}({item[1]})")

# ------------------------------------------------------------------ bands, numbering
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers ============ -->")[0]
qn = re.findall(r'<span class="q-num">(\d+)</span>', hw)
ok(qn == [str(i) for i in range(1, 19)], "Exercise 5I Questions 1-18 in order", str(qn))
bF, rest = hw.split("{{band:D}}")
bD, bE = rest.split("{{band:E}}")
ok(bF.count("q-num") == 12 and bD.count("q-num") == 3 and bE.count("q-num") == 3, "bands F 1-12, D 13-15, E 16-18 (as the textbook)")
rv = les.split("<!-- ============ Chapter review ============ -->")[1]
qn = re.findall(r'<span class="q-num">(\d+)</span>', rv)
ok(qn == [str(i) for i in range(1, 16)], "Chapter 5 review Questions 1-15 in order", str(qn))
ok(ans.count("{{ahead:Review | Chapter review exercise}}") == 1, "review answers under the Review ahead")
an = re.findall(r'<span class="an">(\d+)</span>', ans.split("{{ahead:Review")[1])
ok(an == [str(i) for i in range(1, 15)], "review answers 1-14 (15 is show-that)", str(an))
for svg in ["q5i_r6a", "q5i_r6b"] + [f"q5i_r9{c}" for c in "abcdefgh"]:
    ok(rv.count("{{svg:" + svg + "}}") == 1, f"review figure {svg} placed")

print(f"\n{NOK[0]} checks passed, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:60], sep="\n  ")
    sys.exit(1)
print("ALL OK")
