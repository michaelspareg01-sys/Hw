r"""Check of Lesson 5E (Integration Part 1 pack): The indefinite integral, tied to the printed HTML.

Reads workspace/build/int1/l5e.html and a_5e.html.
  - Every printed question integrand (tutor demos, your turns, worked examples, Exercise 5E) carries
    data-q="KEY". It is read from the page, converted from TeX to sympy (int3_tex.py plus cube roots and
    mixed numbers) and compared with the textbook transcription typed below (TRANS).
  - Every checked solution / answer block carries data-c="KEY" (the same key as its question, or a
    concept key). Each key must occur exactly once, or the item FAILS. Inside a block, every printed
    equation chain (inline maths, display maths, the rows of aligned environments with continuation rows
    "&=..." joined) is checked member by member:
      indefinite items:  a member with C must differentiate (sympy.diff) to the integrand; a member with x
                         and no C must equal the integrand (a rewrite of it); an integral member must have
                         the same integrand; a member d/dx(...) is differentiated;
      definite items:    an integral member has the same limits and integrand; a member with a bracket
                         [F(x)]_a^b (with any coefficient in front) is checked twice: d/dx of it with F in
                         place of the bracket is the integrand, and with F(b)-F(a) in place it equals the
                         value; every number member equals the value of the integral, found by numerical
                         quadrature (mpmath) of the integrand READ from the page;
      chains with no x, C or integral are identities (all members equal);
      "n =", "a =", "b =" statements: the integrand is a constant times (ax+b)^n with the printed values.
    Equality of functions is tested at four complex points (principal powers) with relative tolerance
    1e-9; numbers are compared as real numbers (odd roots of negatives are real: (-1)^(4/3) = 1).
  - The final answer of every item is compared with the textbook's printed answer (Y12 Ext 1 PDF 891-892,
    transcribed in KEY) or, for the lesson examples, with the hand values in KEY.
The break token "\)\({}" (a line-break point inside a long chain) is removed before reading.
Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5e.py
"""
import os
import re
import sys

import mpmath
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))   # override only for mutation tests
X, C, A, B, N, Aa, Bb, Z = sp.symbols("x C A B n a b Z")
EXTRA = {"x": X, "C": C, "A": A, "B": B, "n": N, "a": Aa, "b": Bb, "Z": Z}
PTS = [0.37 + 0.06j, 1.43 + 0.04j, 2.71 + 0.09j, 5.9 + 0.05j]
OTHER = {A: 1.7, B: 0.6, N: 2.3, Aa: 1.9, Bb: 0.8, C: 0}
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
def prep(s):
    s = s.replace("&amp;", "").replace("&", "").replace("\\div", "/")
    s = re.sub(r"\\sqrt\[(\d)\]\{([^{}]*)\}", r"(\2)^{(1/\1)}", s)
    s = re.sub(r"\\sqrt\s+(\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"(\d+)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)        # mixed number 17\tfrac13
    s = re.sub(r"(?<![A-Za-z\d])(\d+)([A-Za-z])", r"\1 \2", s)   # 12x is a product
    return s.strip().rstrip(".,;:").strip()


def P(s):
    return _tex(prep(s), EXTRA)


def realify(e):
    """Odd roots of negative numbers taken as real (the course convention)."""
    e = sp.sympify(e)
    return e.replace(lambda t: t.is_Pow and t.exp.is_Rational and not t.exp.is_Integer and t.exp.q % 2 == 1,
                     lambda t: sp.real_root(t.base, t.exp.q) ** t.exp.p)


def cnum(e, z):
    sub = dict(OTHER)
    sub[X] = z
    return complex(sp.N(sp.sympify(e).subs(sub), 30))


def feq(e1, e2):
    try:
        for z in PTS:
            u, v = cnum(e1, z), cnum(e2, z)
            if abs(u - v) > 1e-9 * (1 + abs(u) + abs(v)):
                return False
        return True
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def rnum(e):
    return complex(sp.N(realify(sp.sympify(e).subs(OTHER)), 30))


def neq(e1, e2):
    try:
        u, v = rnum(e1), rnum(e2)
        return abs(u - v) < 1e-9 * (1 + abs(u) + abs(v))
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def has_x(e):
    return X in sp.sympify(e).free_symbols


def has_c(e):
    return C in sp.sympify(e).free_symbols


# ------------------------------------------------------------------ HTML
def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("\\)\\({}", "").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def block(html, attr, key):
    pat = re.compile(r"<(\w+)[^>]*\b" + attr + r'="' + re.escape(key) + r'"[^>]*>')
    ms = list(pat.finditer(html))
    if len(ms) != 1:
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
    """Equation chains (lists of member texts) in a block; aligned continuation rows are joined."""
    out = []
    for m in maths(text):
        m = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", m)
        rows, cur = [], None
        for row in m.split("\\\\"):
            row = row.replace("&", "")
            row = re.sub(r",?\s*\\q?quad\s*\\text\{.*$", "", row, flags=re.S).strip()   # comments
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
            for piece in re.split(r",\s*\\qquad", r_):
                mem = [p.strip().rstrip(".,").strip() for p in split_top(piece)]
                mem = [p for p in mem if p]
                if len(mem) >= 2:
                    out.append(mem)
    return out


LIM = r"(\{[^{}]*\}|-?\w)"


def parse_int(s):
    """\\int[_a^b] f dx -> (a, b, f) with a = b = None for an indefinite integral."""
    s = s.replace("\\displaystyle", "").strip()
    m = re.match(r"\\int(?:_" + LIM + r"\^" + LIM + r")?(.*)$", s, re.S)
    if not m:
        raise ValueError(f"not an integral: {s!r}")
    a, b, rest = m.group(1), m.group(2), m.group(3).strip()
    mm = re.fullmatch(r"\\d?frac\{dx\}\{(.*)\}", rest, re.S)
    if mm:
        f = P(r"\frac{1}{" + mm.group(1) + "}")
    else:
        mm = re.fullmatch(r"(.*?)\s*(?:\\,)?\s*dx", rest, re.S)
        if not mm:
            raise ValueError(f"no dx in {s!r}")
        f = P(mm.group(1)) if mm.group(1).strip() else sp.Integer(1)
    if a is None:
        return None, None, f
    return P(a.strip("{}")), P(b.strip("{}")), f


def quad_value(f, a, b):
    g = sp.lambdify(X, realify(f), "mpmath")
    mpmath.mp.dps = 30
    return mpmath.quad(lambda t: mpmath.re(g(t)), [float(a), float(b)])


BR = re.compile(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, re.S)


# ------------------------------------------------------------------ the item checker
def check_block(key, text, spec, final_key=None):
    """spec: ('ind', f) | ('def', f, a, b, v) | ('id',)."""
    kind = spec[0]
    ch = chains(text)
    params, finals, n_mem = {}, [], 0
    if not ch and kind == "ind":                      # a bare primitive such as "C" (the integral of 0)
        for m in maths(text):
            e = P(m)
            if has_c(e):
                ok(feq(sp.diff(e, X), spec[1]), f"{key}: {m}", "(d/dx = integrand)")
                finals.append(e)
                n_mem += 2
        ch = []
    elif not ch:
        ok(False, f"{key}: no equation found")
        return
    for mem in ch:
        tag = f"{key}: {'='.join(mem)}"
        if len(mem) == 2 and mem[0] in ("n", "a", "b"):
            params[mem[0]] = P(mem[1])
            continue
        vals = []
        for t in mem:
            if re.match(r"\\d?frac\{d\}\{dx\}", t):
                vals.append(("DX", sp.diff(P(re.sub(r"^\\d?frac\{d\}\{dx\}", "", t)), X)))
            elif "\\int" in t and not t.lstrip().startswith(("\\int", "\\displaystyle\\int")):
                mm = re.fullmatch(r"(.*?)-\\int(.*?)\\,dx", t.strip(), re.S)   # uv - integral of v du/dx
                vals.append(("UV", P(mm.group(1)) - sp.integrate(P(mm.group(2)), X) + C))
            elif "\\int" in t:
                vals.append(("INT", parse_int(t)))
            elif BR.search(t):
                mm = BR.search(t)
                F = P(mm.group(1))
                lo, hi = P(mm.group(2).strip("{}")), P(mm.group(3).strip("{}"))
                Mz = P(t[:mm.start()] + " Z " + t[mm.end():])
                vals.append(("BR", (Mz, F, lo, hi)))
            else:
                vals.append(("E", P(t)))
        anyx = any(k_ in ("DX", "INT", "BR", "UV") or (k_ == "E" and has_c(v_)) for k_, v_ in vals)
        if kind == "id" or not anyx:
            ref = vals[0][1]
            good = all((feq(v_, ref) if (has_x(v_) or has_x(ref)) else neq(v_, ref)) for k_, v_ in vals[1:])
            ok(good, tag[:110], "(identity)")
            n_mem += len(vals)
            continue
        for t, (k_, v_) in zip(mem, vals):
            lab = f"{key}: {t}"
            n_mem += 1
            if kind == "ind":
                f = spec[1]
                if k_ == "INT":
                    ok(v_[0] is None and feq(v_[2], f), lab, "(same integrand)")
                elif k_ == "DX":
                    ok(feq(v_, f), lab, "(derivative = integrand)")
                elif k_ == "BR":
                    ok(False, lab, "bracket in an indefinite item")
                elif k_ == "UV":
                    ok(feq(sp.diff(v_, X), f), lab, "(uv - integral: d/dx = integrand)")
                elif has_c(v_):
                    ok(feq(sp.diff(v_, X), f), lab, "(d/dx = integrand)")
                    finals.append(v_)
                else:
                    ok(feq(v_, f), lab, "(= integrand)")
            else:
                f, a, b, v = spec[1:]
                if k_ == "INT":
                    ok(v_[0] is not None and neq(v_[0], a) and neq(v_[1], b) and feq(v_[2], f), lab, "(same integral)")
                elif k_ == "BR":
                    Mz, F, lo, hi = v_
                    d_ok = feq(sp.diff(Mz.subs(Z, F), X), f) and neq(lo, a) and neq(hi, b)
                    val = Mz.subs(Z, realify(F).subs(X, hi) - realify(F).subs(X, lo))
                    ok(d_ok and neq(val, v), lab, f"(primitive and value {complex(rnum(val)).real:.6g})")
                elif k_ == "DX":
                    ok(feq(v_, f), lab)
                elif has_c(v_):
                    ok(False, lab, "constant in a definite item")
                elif has_x(v_):
                    ok(feq(v_, f), lab, "(= integrand)")
                else:
                    ok(neq(v_, v), lab, f"(= {float(v):.6g})")
                    finals.append(v_)
    if kind == "ind":                                 # stand-alone primitives such as "so the integral is F + C"
        for m in maths(text):
            if len([q for q in split_top(m) if q.strip()]) == 1 and "\\int" not in m:
                try:
                    e = P(m)
                except Exception:  # noqa: BLE001
                    continue
                if has_c(e) and has_x(e):
                    ok(feq(sp.diff(e, X), spec[1]), f"{key}: {m}", "(d/dx = integrand)")
                    finals.append(e)
    if params:
        f = spec[1]
        pa, pb, pn = params.get("a"), params.get("b"), params.get("n")
        good = None not in (pa, pb, pn)
        if good:
            ratio = sp.sympify(f) / (pa * X + pb) ** pn
            good = feq(sp.diff(ratio, X), 0)
        ok(good, f"{key}: printed n, a, b fit the integrand", str(params))
    ok(n_mem >= 2, f"{key}: members checked", str(n_mem))
    if final_key is not None:
        if not finals:
            ok(False, f"{key}: final answer found")
        else:
            fin = finals[-1]
            if kind == "ind":
                ok(feq(fin.subs(C, 0), final_key), f"{key}: final answer = key", f"{sp.sstr(fin)} vs {sp.sstr(final_key)}")
            else:
                ok(neq(fin, final_key), f"{key}: final answer = key", f"{sp.sstr(fin)} vs {sp.sstr(final_key)}")


# ------------------------------------------------------------------ transcriptions
x = X
sq = sp.sqrt
cb = lambda e: e ** R(1, 3)  # noqa: E731
IND = "ind"
TRANS = {
    # lesson examples (tutor demo d, your turn y) and the textbook worked examples (w)
    "d1a": 7, "d1b": 15 * x**4, "d1c": 6 * x**2 - 4 * x + 3, "y1a": 5, "y1b": 20 * x**3, "y1c": 9 * x**2 + 2 * x - 4,
    "w16a": 9, "w16b": 12 * x**3,
    "d2a": (2 * x + 1)**4, "d2b": (7 - 3 * x)**2, "d2c": 4 * (3 * x - 2)**5,
    "y2a": (5 * x + 2)**3, "y2b": (4 - 3 * x)**5, "y2c": 2 * (4 * x - 1)**7,
    "w17a": (3 * x + 1)**5, "w17b": (5 - 2 * x)**2,
    "d3a": 8 / x**5, "d3b": 1 / (2 * x + 5)**3, "y3a": 6 / x**4, "y3b": 1 / (4 * x - 1)**2,
    "w18a": 12 / x**3, "w18b": 1 / (3 * x + 4)**2,
    "d4a": (x**2 + 2)**2, "d4b": (2 - 1 / x**2) * (2 + 1 / x**2), "y4a": (x**2 - 3)**2, "y4b": (1 / x - 2) * (1 / x + 2),
    "w19a": (x**3 - 1)**2, "w19b": (3 - 1 / x**2) * (3 + 1 / x**2),
    "d5a": (sq(x), 1, 9), "d5b": (1 / sq(x), 1, 9), "y5a": (sq(x), 0, 4), "y5b": (1 / sq(x), 1, 16),
    "w20a": (sq(x), 1, 4), "w20b": (1 / sq(x), 1, 4),
    "d6b": 1 / sq(5 - 4 * x), "y6b": 1 / sq(2 * x + 7), "w21b": 1 / sq(9 - 2 * x),
    # Exercise 5E (PDF 251-253)
    "1a": 4, "1b": 1, "1c": 0, "1d": -2, "1e": x, "1f": x**2, "1g": x**3, "1h": x**7,
    "2a": 2 * x, "2b": 4 * x, "2c": 3 * x**2, "2d": 4 * x**3, "2e": 10 * x**9, "2f": 2 * x**3, "2g": 4 * x**5, "2h": 3 * x**8,
    "3a": x + x**2, "3b": x**4 - x**3, "3c": x**7 + x**10, "3d": 2 * x + 5 * x**4, "3e": 9 * x**8 - 11,
    "3f": 7 * x**13 + 3 * x**8, "3g": 4 - 3 * x, "3h": 1 - x**2 + x**4, "3i": 3 * x**2 - 8 * x**3 + 7 * x**4,
    "4a": x**-2, "4b": x**-3, "4c": x**-8, "4d": 3 * x**-4, "4e": 9 * x**-10, "4f": 10 * x**-6,
    "5a": x**R(1, 2), "5b": x**R(1, 3), "5c": x**R(1, 4), "5d": x**R(2, 3), "5e": x**R(-1, 2), "5f": 4 * x**R(1, 2),
    "6a": x * (x + 2), "6b": x * (4 - x**2), "6c": x**2 * (5 - 3 * x), "6d": x**3 * (x - 5), "6e": (x - 3)**2,
    "6f": (2 * x + 1)**2, "6g": (1 - x**2)**2, "6h": (2 - 3 * x) * (2 + 3 * x), "6i": (x**2 - 3) * (1 - 2 * x),
    "7a": (x**2 + 2 * x) / x, "7b": (x**7 + x**8) / x**6, "7c": (2 * x**3 - x**4) / (4 * x),
    "8a": 1 / x**2, "8b": 1 / x**3, "8c": 1 / x**5, "8d": 1 / x**10, "8e": 3 / x**4, "8f": 5 / x**6, "8g": 7 / x**8,
    "8h": 1 / (3 * x**2), "8i": 1 / (7 * x**5), "8j": -1 / (5 * x**3), "8k": 1 / x**2 - 1 / x**5, "8l": 1 / x**3 + 1 / x**4,
    "9a": sq(x), "9b": cb(x), "9c": 1 / sq(x), "9d": cb(x**2),
    "10a": (sq(x), 0, 9), "10b": (cb(x), 0, 8), "10c": (1 / sq(x), 25, 49), "10d": (cb(x**2), 0, 1),
    "11a": (x + 1)**5, "11b": (x + 2)**3, "11c": (4 - x)**4, "11d": (3 - x)**2, "11e": (3 * x + 1)**4, "11f": (4 * x - 3)**7,
    "11g": (5 - 2 * x)**6, "11h": (1 - 5 * x)**7, "11i": (2 * x + 9)**11, "11j": 3 * (2 * x - 1)**10, "11k": 4 * (5 * x - 4)**6,
    "11l": 7 * (3 - 2 * x)**3,
    "12a": (x / 3 - 7)**4, "12b": (x / 4 - 7)**6, "12c": (1 - x / 5)**3,
    "13a": 1 / (x + 1)**3, "13b": 1 / (x - 5)**4, "13c": 1 / (3 * x - 4)**2, "13d": 1 / (2 - x)**5, "13e": 3 / (x - 7)**6,
    "13f": 8 / (4 * x + 1)**5, "13g": 2 / (3 - 5 * x)**4, "13h": 4 / (5 * (1 - 4 * x)**2), "13i": 7 / (8 * (3 * x + 2)**5),
    "14a": sq(x) * (3 * sq(x) - x), "14b": (sq(x) - 2) * (sq(x) + 2), "14c": (2 * sq(x) - 1)**2,
    "15ai": (x**R(1, 2), 0, 1), "15aii": (x**R(-1, 2), 1, 4), "15aiii": (x**R(1, 3), 0, 8),
    "15bi": (sq(x), 0, 4), "15bii": (x * sq(x), 1, 9), "15biii": (1 / sq(x), 1, 9),
    "16a": ((2 - sq(x)) * (2 + sq(x)), 2, 4), "16b": (sq(x) * (sq(x) - 4), 0, 1), "16c": ((sq(x) - 1)**2, 4, 9),
    "18a": sq(2 * x - 1), "18b": sq(7 - 4 * x), "18c": cb(4 * x - 1), "18d": 1 / sq(3 * x + 5),
    "19a": ((x + 1)**4, 0, 2), "19b": ((2 * x - 5)**3, 2, 3), "19c": ((1 - x)**5, -2, 2), "19d": ((1 - x / 5)**4, 0, 5),
    "19e": (sq(9 - 8 * x), 0, 1), "19f": (1 / sq(x + 2), 2, 7), "19g": (cb(x + 1), -2, 0), "19h": (sq(3 * x + 1), 1, 5),
    "19i": (sq(1 - 5 * x), -3, 0),
    "20bi": x * (x - 1)**4, "20bii": x * sq(1 + x),
}
F_ONLY = {k for k in TRANS if re.fullmatch(r"[2489][a-l]", k)}     # questions that print a function, not an integral
KEY = {
    # hand values for the lesson examples
    "d1a": 7 * x, "d1b": 3 * x**5, "d1c": 2 * x**3 - 2 * x**2 + 3 * x, "y1a": 5 * x, "y1b": 5 * x**4, "y1c": 3 * x**3 + x**2 - 4 * x,
    "w16a": 9 * x, "w16b": 3 * x**4,
    "d2a": (2 * x + 1)**5 / 10, "d2b": -(7 - 3 * x)**3 / 9, "d2c": R(2, 9) * (3 * x - 2)**6,
    "y2a": (5 * x + 2)**4 / 20, "y2b": -(4 - 3 * x)**6 / 18, "y2c": (4 * x - 1)**8 / 16,
    "w17a": (3 * x + 1)**6 / 18, "w17b": -(5 - 2 * x)**3 / 6,
    "d3a": -2 / x**4, "d3b": -1 / (4 * (2 * x + 5)**2), "y3a": -2 / x**3, "y3b": -1 / (4 * (4 * x - 1)),
    "w18a": -6 / x**2, "w18b": -1 / (3 * (3 * x + 4)),
    "d4a": x**5 / 5 + R(4, 3) * x**3 + 4 * x, "d4b": 4 * x + 1 / (3 * x**3), "y4a": x**5 / 5 - 2 * x**3 + 9 * x, "y4b": -1 / x - 4 * x,
    "w19a": x**7 / 7 - x**4 / 2 + x, "w19b": 9 * x + 1 / (3 * x**3),
    "d5a": R(52, 3), "d5b": 4, "y5a": R(16, 3), "y5b": 6, "w20a": R(14, 3), "w20b": 2,
    "d6b": -sq(5 - 4 * x) / 2, "y6b": sq(2 * x + 7), "w21b": -sq(9 - 2 * x),
    # textbook answers (PDF 891 left column foot and right column, PDF 892 top left)
    "1a": 4 * x, "1b": x, "1c": 0, "1d": -2 * x, "1e": x**2 / 2, "1f": x**3 / 3, "1g": x**4 / 4, "1h": x**8 / 8,
    "2a": x**2, "2b": 2 * x**2, "2c": x**3, "2d": x**4, "2e": x**10, "2f": x**4 / 2, "2g": 2 * x**6 / 3, "2h": x**9 / 3,
    "3a": x**2 / 2 + x**3 / 3, "3b": x**5 / 5 - x**4 / 4, "3c": x**8 / 8 + x**11 / 11, "3d": x**2 + x**5, "3e": x**9 - 11 * x,
    "3f": x**14 / 2 + x**9 / 3, "3g": 4 * x - 3 * x**2 / 2, "3h": x - x**3 / 3 + x**5 / 5, "3i": x**3 - 2 * x**4 + 7 * x**5 / 5,
    "4a": -x**-1, "4b": -x**-2 / 2, "4c": -x**-7 / 7, "4d": -x**-3, "4e": -x**-9, "4f": -2 * x**-5,
    "5a": R(2, 3) * x**R(3, 2), "5b": R(3, 4) * x**R(4, 3), "5c": R(4, 5) * x**R(5, 4), "5d": R(3, 5) * x**R(5, 3),
    "5e": 2 * x**R(1, 2), "5f": R(8, 3) * x**R(3, 2),
    "6a": x**3 / 3 + x**2, "6b": 2 * x**2 - x**4 / 4, "6c": R(5, 3) * x**3 - R(3, 4) * x**4, "6d": x**5 / 5 - R(5, 4) * x**4,
    "6e": x**3 / 3 - 3 * x**2 + 9 * x, "6f": R(4, 3) * x**3 + 2 * x**2 + x, "6g": x - R(2, 3) * x**3 + x**5 / 5,
    "6h": 4 * x - 3 * x**3, "6i": x**3 / 3 - x**4 / 2 - 3 * x + 3 * x**2,
    "7a": x**2 / 2 + 2 * x, "7b": x**2 / 2 + x**3 / 3, "7c": x**3 / 6 - x**4 / 16,
    "8a": -1 / x, "8b": -1 / (2 * x**2), "8c": -1 / (4 * x**4), "8d": -1 / (9 * x**9), "8e": -1 / x**3, "8f": -1 / x**5,
    "8g": -1 / x**7, "8h": -1 / (3 * x), "8i": -1 / (28 * x**4), "8j": 1 / (10 * x**2), "8k": 1 / (4 * x**4) - 1 / x,
    "8l": -1 / (2 * x**2) - 1 / (3 * x**3),
    "9a": R(2, 3) * x**R(3, 2), "9b": R(3, 4) * x**R(4, 3), "9c": 2 * sq(x), "9d": R(3, 5) * x**R(5, 3),
    "10a": 18, "10b": 12, "10c": 4, "10d": R(3, 5),
    "11a": (x + 1)**6 / 6, "11b": (x + 2)**4 / 4, "11c": -(4 - x)**5 / 5, "11d": -(3 - x)**3 / 3, "11e": (3 * x + 1)**5 / 15,
    "11f": (4 * x - 3)**8 / 32, "11g": -(5 - 2 * x)**7 / 14, "11h": -(1 - 5 * x)**8 / 40, "11i": (2 * x + 9)**12 / 24,
    "11j": R(3, 22) * (2 * x - 1)**11, "11k": R(4, 35) * (5 * x - 4)**7, "11l": -R(7, 8) * (3 - 2 * x)**4,
    # 12c: the key prints -5/4 (1 - x/4)^4 + C, a slip (its derivative is not (1 - x/5)^3); our answer has x/5
    "12a": R(3, 5) * (x / 3 - 7)**5, "12b": R(4, 7) * (x / 4 - 7)**7, "12c": -R(5, 4) * (1 - x / 5)**4,
    "13a": -1 / (2 * (x + 1)**2), "13b": -1 / (3 * (x - 5)**3), "13c": -1 / (3 * (3 * x - 4)), "13d": 1 / (4 * (2 - x)**4),
    "13e": -3 / (5 * (x - 7)**5), "13f": -1 / (2 * (4 * x + 1)**4), "13g": 2 / (15 * (3 - 5 * x)**3), "13h": 1 / (5 - 20 * x),
    "13i": -7 / (96 * (3 * x + 2)**4),
    "14a": R(3, 2) * x**2 - R(2, 5) * x**R(5, 2), "14b": x**2 / 2 - 4 * x, "14c": 2 * x**2 - R(8, 3) * x**R(3, 2) + x,
    "15ai": R(2, 3), "15aii": 2, "15aiii": 12, "15bi": R(16, 3), "15bii": R(484, 5), "15biii": 4,
    "16a": 2, "16b": R(-13, 6), "16c": R(73, 6),
    "18a": R(1, 3) * (2 * x - 1)**R(3, 2), "18b": -R(1, 6) * (7 - 4 * x)**R(3, 2), "18c": R(3, 16) * (4 * x - 1)**R(4, 3),
    "18d": R(2, 3) * sq(3 * x + 5),
    "19a": R(242, 5), "19b": 0, "19c": R(364, 3), "19d": 1, "19e": R(13, 6), "19f": 2, "19g": 0, "19h": R(112, 9), "19i": R(42, 5),
    "20bi": x * (x - 1)**5 / 5 - (x - 1)**6 / 30, "20bii": R(2, 3) * x * (1 + x)**R(3, 2) - R(4, 15) * (1 + x)**R(5, 2),
}

les, ans = read("l5e.html"), read("a_5e.html")
both = les + ans

# ------------------------------------------------------------------ questions as printed
SPEC = {}
for k, tr in TRANS.items():
    q = block(les, "data-q", k)
    if q is None:
        continue
    ms = maths(q)
    try:
        if k in F_ONLY:
            ok(len(ms) == 1, f"q {k}: one function printed")
            f = P(ms[0])
            ok(feq(f, tr), f"q {k}: printed function = textbook", f"{ms[0]}")
            SPEC[k] = ("ind", sp.sympify(tr))
            continue
        ints = [m for m in ms if "\\int" in m]
        ok(len(ints) == 1, f"q {k}: one integral printed")
        a, b, f = parse_int(ints[0])
        if isinstance(tr, tuple):
            ftr, atr, btr = tr
            ok(a is not None and feq(f, ftr) and neq(a, atr) and neq(b, btr), f"q {k}: printed integral = textbook", ints[0])
            v = quad_value(sp.sympify(ftr), atr, btr)
            SPEC[k] = ("def", sp.sympify(ftr), atr, btr, sp.Float(v, 25))
        else:
            ok(a is None and feq(f, tr), f"q {k}: printed integral = textbook", ints[0])
            SPEC[k] = ("ind", sp.sympify(tr))
    except Exception as err:  # noqa: BLE001
        ok(False, f"q {k}: read", repr(err)[:120])

# exact values of the definite items (sympy) agree with the quadrature
for k, sp_ in SPEC.items():
    if sp_[0] == "def" and k != "19g":
        ex = sp.integrate(sp_[1], (X, sp_[2], sp_[3]))
        ok(neq(ex, sp_[4]), f"{k}: sympy exact value = quadrature", f"{ex}")
ok(neq(SPEC["19g"][4], 0), "19g: real cube root, quadrature = 0")

# ------------------------------------------------------------------ solutions and answers
for k in TRANS:
    if k in SPEC:
        blk = block(both, "data-c", k)
        if blk is not None:
            try:
                check_block(k, blk, SPEC[k], sp.sympify(KEY[k]))
            except Exception as err:  # noqa: BLE001
                ok(False, f"{k}: check", repr(err)[:140])

ok(not feq(sp.diff(-R(5, 4) * (1 - x / 4)**4, X), (1 - x / 5)**3), "12c: the printed key (1 - x/4) is a slip; not used")

# "Steps the book skips" tips after the worked examples: each is checked against its example's integral
TIPS = ("t16b", "t17a", "t17b", "t18a", "t18b", "t19a", "t19b", "t20a", "t20b", "t21b")
for tk in TIPS:
    blk = block(les, "data-c", tk)
    if blk is not None:
        check_block(tk, blk, SPEC["w" + tk[1:]], sp.sympify(KEY["w" + tk[1:]]))
ok(les.count("Steps the book skips: Worked example") == 6, "a tip after each of Worked examples 16-21")
WE = re.findall(r'<span class="tag">Worked example (\d+)</span>(.*?)</div></div>\n<div class="box tip"><div class="bt">Steps the book skips: Worked example (\d+)', les, re.S)
ok([w[0] for w in WE] == [str(i) for i in range(16, 22)] and all(w[0] == w[2] for w in WE), "each tip follows its worked example")
for w in WE:
    ok(not re.search(r"Here \\\(n=|so divide by|Increase the index from", w[1]), f"WE{w[0]}: no pack prose inside the example box")
for nm, frm, vv in (("20bi", "\\(v=\\tfrac15(x-1)^5\\)", (X - 1)**5 / 5), ("20bii", "\\(v=\\tfrac23(1+x)^{\\frac32}\\)", R(2, 3) * (1 + X)**R(3, 2))):
    ok(frm in ans and feq(sp.diff(vv, X), (X - 1)**4 if nm == "20bi" else sp.sqrt(1 + X)), f"Q{nm}: printed v has dv/dx as stated")

# textbook answers present for every question part, demos for every lesson example
ok(sorted(k for k in KEY if not k[0] in "dyw") == sorted(k for k in TRANS if not k[0] in "dyw"), "every exercise part has a key value")
ans_keys = set(re.findall(r'data-c="([^"]+)"', ans))
ok(all(k in ans_keys for k in TRANS if k[0] not in "w"), "every question part has an answer block in a_5e.html",
   str(sorted(k for k in TRANS if k[0] != "w" and k not in ans_keys)))

# concept boxes and tips
for k, spec in (("c1_box", ("ind", X**2 + 1)), ("c1_sum", ("ind", 3 * X**2 + 4 * X - 5)),
                ("c1_def", ("def", X**2 + 1, 0, 3, sp.Integer(12))), ("c1_check", ("id",)), ("c2_check", ("id",)),
                ("c4_exp", ("id",)), ("c5_surd", ("id",)), ("c5_pow", ("id",))):
    blk = block(les, "data-c", k)
    if blk is not None:
        check_block(k, blk, spec)
ok(neq(sp.integrate(X**2 + 1, (X, 0, 3)), 12), "c1_def: sympy value 12")
ok("(9+3+C)-(0+0+C)=12" in les, "c1 tip: constant cancels, printed")
ok(neq(sp.expand((9 + 3 + C) - (0 + 0 + C)), 12), "c1 tip: (9+3+C)-(0+0+C) = 12")

# Box 14 standard forms (printed in the take box) differentiate back
box = les[les.index("14 Standard forms for integration"):]
box = box[:box.index("</div></div>")]
ok("\\int x^n\\,dx=\\frac{x^{n+1}}{n+1}+C" in box and "\\int(ax+b)^n\\,dx=\\frac{(ax+b)^{n+1}}{a(n+1)}+C" in box and "n\\ne-1" in box,
   "Box 14 printed as in the textbook")
ok(feq(sp.diff(X**(N + 1) / (N + 1), X), X**N) and feq(sp.diff((Aa * X + Bb)**(N + 1) / (Aa * (N + 1)), X), (Aa * X + Bb)**N),
   "Box 14: both forms differentiate back (generic a, b, n)")

# textbook sentences with a pack cross-reference, bands, Q17 and Q20a
for s in ("We shall deal with the integration of \\(x^{-1}\\) in Chapter 6.</p></div>",
          "given in the last section of Chapter 4 can now be restated in this new notation.",
          "The only exception to including the constant of integration is when calculating definite integrals"):
    ok(les.count(s) == 1, f"text printed once: {s[:60]}")
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers ============ -->")[0]
qn = re.findall(r'<span class="q-num">(\d+)</span>', hw)
ok(qn == [str(i) for i in range(1, 21)], "Exercise 5E Questions 1-20 in order", str(qn))
bF, rest = hw.split("{{band:D}}")
bD, bE = rest.split("{{band:E}}")
ok(bF.count("q-num") == 7 and bD.count("q-num") == 12 and bE.count("q-num") == 1, "bands F 1-7, D 8-19, E 20 (as the textbook)")
a17 = re.search(r'<span class="an">17</span><div class="ab">(.*?)</div></div>', ans, re.S).group(1)
ok("\\frac{x^0}{0}+C" in a17 and "meaningless" in a17, "Q17 answer: x^0/0 is meaningless")
ok("20bi" in ans_keys and "20a" not in ans_keys and "prove" not in ans.split("Textbook Homework")[1], "Q20a (prove) not answered")

# past-paper section: the timed-practice note (no catalogue row is tagged int1-L6)
pp = les.split("<!-- ============ Past papers ============ -->")[1]
note = "For timed practice, do Questions 8(l), 11(l), 12(c), 13(i), 14(c), 16(c), 18(d) and 19(i) above in 30 minutes."
ok(pp.count(note) == 1 and "class=\"pp\"" not in pp, "timed-practice note, no past-paper question")
for item in re.findall(r"(\d+)\(([a-z]+)\)", note):
    ok(f"{item[0]}{item[1]}" in TRANS, f"note names an existing part: Q{item[0]}({item[1]})")
ok("Past-Paper" not in ans, "answers: no past-paper section")

print(f"\n{NOK[0]} checks passed, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:40], sep="\n  ")
    sys.exit(1)
print("ALL OK")
