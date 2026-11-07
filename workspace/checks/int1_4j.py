r"""Check of Lesson 4J (Integration Part 1): Primitive functions, tied to the printed HTML.

Reads workspace/build/int1/l4j.html (concept boxes, worked examples, tutor demo / your turn questions,
Exercise 4J questions) and a_4j.html (lesson-example answers, textbook homework answers).

Every checked block carries an invisible attribute data-c="KEY" (answers, worked solutions, concept
claims) or data-q="KEY" (a printed question function). Each key must occur exactly once, or the item
FAILS. Inside a block every printed equation chain (inline maths, display maths and the rows of aligned
environments, continuation rows "&=..." included) is converted from TeX to sympy (int3_tex.py plus
cube/fifth roots and mixed numbers) and checked by its left-hand side:
  y, f(x)            primitive:  d/dx of each member = the given derivative (members with C or D), or
                                 = the particular solution found independently (members without);
  dy/dx, y', f'(x)   = the given derivative (first-order items); for second-order items d/dx of the
                       member = f''(x) (members with C), or = the particular solution's derivative;
  y'', f''(x)        = the given second derivative;
  f(4), f(0), ...    = the independent particular solution at that point (also y in keys "KEY@v");
  d/dx(E)            = sympy's derivative of E;
  a, n               = the coefficient of x and the index of Box 17, as given in the spec;
  numbers = ...      = equations in the constants: true when the constants found from the printed
                       general primitive and the conditions are substituted;
  anything else      = an identity (all members equal; for an item, equal to the given function).
The constants are solved (sympy.solve) from the PRINTED general primitive and the conditions, and the
resulting particular solution is compared with an independent one (sympy.integrate + solve). Equality
is tested numerically at four complex points (small positive argument, so that principal-value powers
agree) with a relative tolerance of 1e-9. A row naming a condition ("y = 5", "y' = 4") must match a
condition of the item.

Each question function printed in l4j.html (data-q) is compared with the textbook transcription below,
and the question texts without data-q are matched as exact substrings (once each). Each final answer
is compared with the textbook's printed answer (Y12 Ext 1 PDF 887, transcribed below): primitives up
to a constant, particular solutions exactly. Exit status 1 if anything fails.
Run: python3 workspace/checks/int1_4j.py
"""
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))   # override only for mutation tests
X, T, C, D, A, B, N, K = sp.symbols("x t C D a b n k")
EXTRA = {"x": X, "t": T, "C": C, "D": D, "a": A, "b": B, "n": N, "k": K}
CONSTS = {C, D}
PTS = [0.37 + 0.06j, 1.43 + 0.04j, 2.71 + 0.09j, 5.9 + 0.05j]
OTHER = {A: 1.7, B: 0.6, N: 2.3, K: 1.9}
FAILS, NOK = [], [0]


def ok(flag, label, detail=""):
    if flag:
        NOK[0] += 1
        print("OK       " + label + ("  " + detail if detail else ""))
    else:
        FAILS.append(label)
        print("MISMATCH " + label + ("  " + detail if detail else ""))
    return flag


# ------------------------------------------------------------------ TeX -> sympy
def prep(s):
    s = s.replace("&amp;", "").replace("&", "")
    s = re.sub(r"\\sqrt\[(\d)\]\{([^{}]*)\}", r"(\2)^{(1/\1)}", s)
    s = re.sub(r"\\sqrt\s+(\w)", r"\\sqrt{\1}", s)
    s = re.sub(r"(\d)\\tfrac(\d)(\d)", r"(\1+\2/\3)", s)          # mixed number 4\tfrac12
    s = re.sub(r"(?<![A-Za-z])(\d)([A-Za-z])", r"\1 \2", s)                     # 0x is a product, not a hex literal
    return s.strip().rstrip(".,;:").strip()


def P(s):
    try:
        return _tex(prep(s), EXTRA)
    except Exception as exc:  # noqa: BLE001
        ok(False, "parse " + s[:80], repr(exc)[:80])
        return sp.nan


def num(e, z):
    sub = {X: z, T: z}
    sub.update(OTHER)
    return complex(sp.N(sp.sympify(e).subs(sub), 30))


def eq(e1, e2):
    try:
        for z in PTS:
            u, v = num(e1, z), num(e2, z)
            if abs(u - v) > 1e-9 * (1 + abs(u) + abs(v)):
                return False
        return True
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def has_var(e):
    return bool(sp.sympify(e).free_symbols & {X, T})


def has_const(e):
    return bool(sp.sympify(e).free_symbols & CONSTS)


# ------------------------------------------------------------------ HTML blocks
def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


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
    """Inline and display maths in document order; those marked <!--nc--> are left out."""
    out = []
    for m in re.finditer(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", text, re.S):
        before = text[max(0, m.start() - 45):m.start()]
        if re.search(r"<!--nc-->(<span style=\"white-space:nowrap\">)?$", before):
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
    """List of (lhs_text_or_None_for_continuation, [member texts])."""
    out = []
    for m in maths(text):
        m = re.sub(r"\\begin\{aligned\}(\[t\])?|\\end\{aligned\}", "", m)
        for row in m.split("\\\\"):
            row = row.replace("&amp;", "").replace("&", "").strip()
            if not row or "=" not in row:
                continue
            if re.search(r"\\(lt|gt|ne|le|ge|text)\b", row):
                print("         (skipped row: " + row[:70] + ")")
                continue
            parts = [p.strip() for p in split_top(row)]
            if parts[0] == "":
                out.append((None, parts[1:]))
            else:
                out.append((parts[0], parts[1:]))
    return out


F_NAMES = {"y", "f(x)", "F(x)"}
D1_NAMES = {"y'", "f'(x)", r"\dfrac{dy}{dx}", r"\dfrac{dy}{dt}"}
D2_NAMES = {"y''", "f''(x)"}


# ------------------------------------------------------------------ independent solutions
def solve_indep(sp_):
    """Independent particular solution (sympy integrate + solve), or None if there are no conditions."""
    var = sp_.get("var", X)
    conds = sp_.get("conds", [])
    if not conds:
        return None
    k1, k2 = sp.symbols("k1 k2")
    if sp_["order"] == 1:
        g = sp.integrate(sp_["f"], var) + k1
        eqs = [sp.Eq(g.subs(var, x0), v) for kind, x0, v in conds]
        sol = sp.solve(eqs, [k1], dict=True)
    else:
        g1 = sp.integrate(sp_["f2"], var) + k1
        g = sp.integrate(g1, var) + k2
        eqs = [sp.Eq((g if kind == "y" else g1).subs(var, x0), v) for kind, x0, v in conds]
        sol = sp.solve(eqs, [k1, k2], dict=True)
    if len(sol) != 1:
        raise ValueError("independent solve failed")
    return sp.simplify(g.subs(sol[0]))


# ------------------------------------------------------------------ item checker
FORMS = {}


def check_item(key, text, sp_):
    kind = sp_["kind"]
    var = sp_.get("var", X)
    order = sp_.get("order", 1)
    given = sp_.get("f") if order == 1 else sp_.get("f2")
    conds = sp_.get("conds", [])
    at = float(key.split("@")[1]) if "@" in key else None
    names = sp_.get("names", {})
    branches = sp_.get("branches")                    # Q18: particular solution per sign of x
    part = solve_indep(sp_) if kind == "prim" and not branches else None
    ch = chains(text)
    if not ch:
        ok(False, key, "no equation found")
        return

    def particular_at(v):
        if branches:
            return branches[0 if v > 0 else 1].subs(var, v)
        return part.subs(var, v)

    def is_particular(e):
        if branches:
            return any(eq(e, b_) for b_ in branches)
        return part is not None and eq(e, part)

    # pass 1: roles, and the printed general primitives
    rows, lhs, role, anchor = [], None, None, None
    for L, mem in ch:
        if L is not None:
            lhs = L
            Lc = L.replace(" ", "")
            if Lc.startswith(r"\dfrac{d}{dx}"):
                role = ("OP", P(Lc[len(r"\dfrac{d}{dx}"):]))
            elif kind == "id":
                role, mem, anchor = "ID", [L] + mem, P(L)
            elif Lc in names:
                role = ("N", names[Lc])
            elif Lc in ("x", "t"):
                role = "SKIP"
            elif Lc in ("a", "n"):
                role = ("PAR", Lc)
            elif re.fullmatch(r"f\((-?[\d.]+)\)", Lc):
                role = ("V", float(re.fullmatch(r"f\((-?[\d.]+)\)", Lc).group(1)))
            elif Lc in F_NAMES:
                role = ("V", at) if at is not None else "F"
            elif Lc in D1_NAMES:
                role = "D1"
            elif Lc in D2_NAMES:
                role = "D2"
            else:
                e = P(L)
                if has_var(e):
                    role = "F" if has_const(e) else "GIVEN"
                elif has_const(e) and not conds and not sp_.get("consts"):
                    role = "F"
                else:
                    role = "EQ"
                mem, anchor = [L] + mem, e
        rows.append((lhs, role, anchor, [(m_, P(m_)) for m_ in mem]))

    fgen = dgen = None
    if isinstance(sp_.get("form"), str) and sp_["form"] in FORMS:
        fgen = FORMS[sp_["form"]]
    elif sp_.get("form") is not None and not isinstance(sp_.get("form"), str):
        fgen = sp_["form"]
    for lhs, role, anchor, mem in rows:
        for t_, e in mem:
            if role == "F" and has_const(e) and fgen is None:
                fgen = e
            if role == "D1" and order == 2 and has_const(e) and dgen is None:
                dgen = e
    if fgen is not None:
        FORMS[key] = fgen

    # constants from the printed general primitive(s) and the conditions
    consts = dict(sp_.get("consts", {}))
    if conds and not consts and at is None:
        if fgen is None:
            ok(False, key, "no printed general primitive to solve the constants from")
            return
        unknown = sorted((sp.sympify(fgen).free_symbols | (sp.sympify(dgen).free_symbols if dgen is not None else set())) & CONSTS, key=str)
        eqs = []
        for kd, x0, v in conds:
            if kd == "y":
                eqs.append(sp.Eq(fgen.subs(var, x0), v))
            else:
                eqs.append(sp.Eq((dgen if dgen is not None else sp.diff(fgen, var)).subs(var, x0), v))
        sol = sp.solve(eqs, unknown, dict=True)
        if len(sol) != 1:
            ok(False, key, f"constants not determined: {sol}")
            return
        consts = sol[0]
        if part is not None:
            ok(eq(fgen.subs(consts), part), f"{key}: printed general primitive + conditions = independent solution",
               f"{sp.sstr(sp.simplify(fgen.subs(consts)))}; constants {consts}")
        if order == 2 and dgen is not None:
            ok(eq(sp.diff(fgen, var).subs(consts), dgen.subs(consts)), f"{key}: d/dx of printed f(x) = printed f'(x)")

    # pass 2: check every member
    finals_f, finals_c, nv = [], [], 0
    for lhs, role, anchor, mem in rows:
        for t_, e in mem:
            lab = f"{key}: {(lhs or '') + ' = ' if role not in ('ID', 'EQ', 'GIVEN') else ''}{t_}"[:110]
            if role == "SKIP":
                continue
            if isinstance(role, tuple) and role[0] == "PAR":
                ok(sp_.get("params", {}).get(role[1]) is not None and eq(e, sp_["params"][role[1]]), lab)
                continue
            if role in ("F", "D1") and not has_var(e) and not has_const(e) and conds:
                kd = "y" if role == "F" else "dy"
                ok(any(k_ == kd and eq(e, v) for k_, x0, v in conds), lab, "(a condition of the question)")
                continue
            if role == "ID":
                ok(eq(e, anchor), lab)
            elif isinstance(role, tuple) and role[0] == "OP":
                ok(eq(e, sp.diff(role[1], var)), lab, "(derivative)")
            elif isinstance(role, tuple) and role[0] == "N":
                ok(eq(e, role[1]), lab)
            elif isinstance(role, tuple) and role[0] == "V":
                ok(eq(e, particular_at(role[1])), lab, f"(value at {role[1]:g})")
                nv += 1
            elif role == "GIVEN":
                ok(eq(e, given), lab, "(the given function)")
            elif role == "EQ":
                ok(eq(e.subs(consts), anchor.subs(consts)), lab, f"(with {consts})" if consts else "")
            elif role == "D2":
                ok(eq(e, sp_["f2"]), lab, "(the given second derivative)")
            elif role == "D1":
                if order == 1:
                    ok(not has_const(e) and eq(e, given), lab, "(the given derivative)")
                elif has_const(e):
                    ok(eq(sp.diff(e, var), sp_["f2"]), lab, "(d/dx = f'')")
                else:
                    ok(eq(e, sp.diff(part, var)), lab, "(derivative of the particular solution)")
            elif role == "F":
                if has_const(e):
                    if order == 1:
                        ok(eq(sp.diff(e, var), given), lab, "(d/dx = the given derivative)")
                    else:
                        ok(eq(sp.diff(e, var, 2), sp_["f2"]), lab, "(d2/dx2 = f'')")
                    finals_c.append(e)
                elif part is not None or branches:
                    ok(is_particular(e), lab, "(the particular solution)")
                    finals_f.append(e)
                else:
                    ok(False, lab, "a primitive without its constant")
    # completeness and the textbook's answer
    if kind == "prim" and at is None:
        if conds:
            if not ok(bool(finals_f), f"{key}: final particular solution printed") or "tb" not in sp_:
                return
            tb = P(sp_["tb"])
            if branches:
                ok(len(finals_f) >= 2 and all(any(eq(f_, b_) for f_ in finals_f) for b_ in branches),
                   f"{key}: both branches agree with the textbook answer")
            else:
                ok(eq(finals_f[-1], tb), f"{key}: final answer = textbook answer {sp_['tb']}")
        else:
            if not ok(bool(finals_c), f"{key}: general primitive with its constant printed") or "tb" not in sp_:
                return
            tb = P(sp_["tb"])
            ok(has_const(tb) and eq(sp.diff(finals_c[-1], var), sp.diff(tb, var)),
               f"{key}: final answer = textbook answer {sp_['tb']} (up to the constant)")
    if at is not None:
        ok(nv >= 1, f"{key}: value printed")
        if "tb" in sp_:
            last = [e for lhs, role, anchor, mem in rows if isinstance(role, tuple) and role[0] == "V" for t_, e in mem][-1]
            ok(eq(last, P(sp_["tb"])), f"{key}: value = textbook answer {sp_['tb']}")


# ------------------------------------------------------------------ specs (textbook transcription)
x, t = X, T


def prim(f, tb=None, conds=None, form=None, params=None, order=1, var=None, **kw):
    d = {"kind": "prim", "order": order, "conds": conds or []}
    if order == 1:
        d["f"] = f
    else:
        d["f2"] = f
    if tb is not None:
        d["tb"] = tb
    if form is not None:
        d["form"] = form
    if params is not None:
        d["params"] = params
    if var is not None:
        d["var"] = var
    d.update(kw)
    return d


R = sp.Rational
ID = {"kind": "id"}
# lesson: concept claims and worked examples (l4j.html)
LESSON = {
    "c1_list": ID, "we_c1": ID, "we_c1b": ID, "c2_prim": ID, "c3_rule": ID, "c3_sum": ID, "c3_tip": ID,
    "c4_neg": ID, "c4_frac": ID, "c5_rule": ID,
    "c2_cond": prim(2 * x, conds=[("y", 2, 7)], form=x ** 2 + C),
    "we_c2": prim(2 * x, conds=[("y", 2, 7)], form=x ** 2 + C),
    "e26a": prim(x ** 3 + x ** 2 + x + 1, tb=r"\tfrac14x^4+\tfrac13x^3+\tfrac12x^2+x+C"),
    "e26b": prim(5 * x ** 3 + 7, tb=r"\tfrac54x^4+7x+C"),
    "e27a": prim(1 / x ** 2, tb=r"-\dfrac1x+C"),
    "e27b": prim(sp.sqrt(x), tb=r"\tfrac23x^{\frac32}+C"),
    "e28a": prim((3 * x + 1) ** 4, tb=r"\dfrac{(3x+1)^5}{15}+C", params={"a": 3, "n": 4}),
    "e28b": prim((1 - 3 * x) ** 6, tb=r"-\dfrac{(1-3x)^7}{21}+C", params={"a": -3, "n": 6}),
    "e28c": prim(1 / (x + 1) ** 2, tb=r"-\dfrac{1}{x+1}+C", params={"a": 1, "n": -2}),
    "e28d": prim(sp.sqrt(x + 1), tb=r"\tfrac23(x+1)^{\frac32}+C", params={"a": 1, "n": R(1, 2)}),
    "e29": prim(6 * x ** 2 + 1, tb=r"2x^3+x-6", conds=[("y", 2, 12)]),
    "e30": prim(12 * (x - 1) ** 2, order=2, conds=[("y", 0, 0), ("y", 1, 0)]),
}
# the data-q questions of l4j.html (worked examples, tutor demos, your turns, Exercise 4J)
QUESTIONS = {
    "e26a": x ** 3 + x ** 2 + x + 1, "e26b": 5 * x ** 3 + 7, "e27a": 1 / x ** 2, "e27b": sp.sqrt(x),
    "e28a": (3 * x + 1) ** 4, "e28b": (1 - 3 * x) ** 6, "e28c": 1 / (x + 1) ** 2, "e28d": sp.sqrt(x + 1),
}
# answers (a_4j.html): lesson examples
f1, g1 = (x + 1) ** 2, x ** 2 + 2 * x
f2, g2 = (x - 3) ** 2, x ** 2 - 6 * x + 2
ANS = {
    "d1": {"kind": "names", "names": {"f(x)": f1, "f'(x)": sp.diff(f1, x), "g'(x)": sp.diff(g1, x), "f(x)-g(x)": sp.expand(f1 - g1)}},
    "y1": {"kind": "names", "names": {"f(x)": f2, "f'(x)": sp.diff(f2, x), "g'(x)": sp.diff(g2, x), "f(x)-g(x)": sp.expand(f2 - g2)}},
    "d2": prim(3 * x ** 2, conds=[("y", 2, 5)]),
    "y2": prim(4 * x ** 3, conds=[("y", 1, -2)]),
    "d3a": prim(x ** 4 + x ** 3 + x ** 2 + 3), "d3b": prim(4 * x ** 5 - 2), "d3c": prim((2 * x + 1) * (x - 3)),
    "y3a": prim(x ** 5 + x ** 2 + x + 4), "y3b": prim(3 * x ** 4 + 5), "y3c": prim((x + 3) * (x - 1)),
    "d4a": prim(4 / x ** 3), "d4b": prim(x ** R(2, 3)), "y4a": prim(6 / x ** 4), "y4b": prim(x * sp.sqrt(x)),
    "d5a": prim((2 * x + 5) ** 3, params={"a": 2, "n": 3}), "d5b": prim((3 - 2 * x) ** 5, params={"a": -2, "n": 5}),
    "d5c": prim((x + 3) ** -3, params={"a": 1, "n": -3}), "d5d": prim(sp.sqrt(4 * x + 1), params={"a": 4, "n": R(1, 2)}),
    "y5a": prim((4 * x + 3) ** 5, params={"a": 4, "n": 5}), "y5b": prim((2 - 5 * x) ** 4, params={"a": -5, "n": 4}),
    "y5c": prim((x - 4) ** -3, params={"a": 1, "n": -3}), "y5d": prim(sp.sqrt(x + 3), params={"a": 1, "n": R(1, 2)}),
    "d6a": prim(12 * x ** 2 - 2, conds=[("y", 1, 5)]), "d6b": prim((2 * x - 1) ** 3, conds=[("y", 1, 2)]),
    "y6a": prim(6 * x ** 2 + 2 * x, conds=[("y", 1, 7)]), "y6b": prim((3 * x + 1) ** 2, conds=[("y", 0, 1)]),
    "d7a": prim(12 * (x - 2) ** 2, order=2, conds=[("y", 2, 0), ("y", 0, 0)]),
    "d7b": prim(6 * x - 2, order=2, conds=[("dy", 1, 4), ("y", 1, 3)]),
    "y7a": prim(6 * (x + 1), order=2, conds=[("y", 0, 0), ("y", 1, 6)]),
    "y7b": prim(12 * x + 2, order=2, conds=[("dy", 0, 1), ("y", 0, -2)]),
}
for k_ in ("d3a", "d3b", "d3c", "y3a", "y3b", "y3c", "d4a", "d4b", "y4a", "y4b", "d5a", "d5b", "d5c", "d5d", "y5a", "y5b", "y5c", "y5d"):
    QUESTIONS[k_] = ANS[k_]["f"]

# Exercise 4J (Y12 Ext 1 PDF 206-207) and its answers (PDF 887)
EX = {
    "1a": (x ** 6, r"\tfrac17x^7+C"), "1b": (x ** 3, r"\tfrac14x^4+C"), "1c": (x ** 10, r"\tfrac{1}{11}x^{11}+C"),
    "1d": (3 * x, r"\tfrac32x^2+C"), "1e": (sp.Integer(5), r"5x+C"), "1f": (5 * x ** 9, r"\tfrac12x^{10}+C"),
    "1g": (21 * x ** 6, r"3x^7+C"), "1h": (sp.Integer(0), r"C"),
    "2a": (x ** 2 + x ** 4, r"\tfrac13x^3+\tfrac15x^5+C"), "2b": (4 * x ** 3 - 5 * x ** 4, r"x^4-x^5+C"),
    "2c": (2 * x ** 2 + 5 * x ** 7, r"\tfrac23x^3+\tfrac58x^8+C"), "2d": (x ** 2 - x + 1, r"\tfrac13x^3-\tfrac12x^2+x+C"),
    "2e": (3 - 4 * x + 16 * x ** 7, r"3x-2x^2+2x^8+C"), "2f": (3 * x ** 2 - 4 * x ** 3 - 5 * x ** 4, r"x^3-x^4-x^5+C"),
    "3a": (x * (x - 3), r"\tfrac13x^3-\tfrac32x^2+C"), "3b": ((x + 1) * (x - 2), r"\tfrac13x^3-\tfrac12x^2-2x+C"),
    "3c": ((3 * x - 1) * (x + 4), r"x^3+\tfrac{11}{2}x^2-4x+C"), "3d": (x ** 2 * (5 * x ** 3 - 4 * x), r"\tfrac56x^6-x^4+C"),
    "3e": (2 * x ** 3 * (4 * x ** 4 + 1), r"x^8+\tfrac12x^4+C"), "3f": ((x - 3) * (1 + x ** 2), r"\tfrac12x^2+\tfrac14x^4-3x-x^3+C"),
    "5a": (1 / x ** 2, r"-\dfrac1x+C"), "5b": (1 / x ** 3, r"-\dfrac{1}{2x^2}+C"), "5c": (-2 / x ** 3, r"\dfrac{1}{x^2}+C"),
    "5d": (-3 / x ** 4, r"\dfrac{1}{x^3}+C"), "5e": (1 / x ** 2 - 1 / x ** 3, r"-\dfrac1x+\dfrac{1}{2x^2}+C"),
    "6a": (sp.sqrt(x), r"\tfrac23x^{\frac32}+C"), "6b": (1 / sp.sqrt(x), r"2\sqrt x+C"), "6c": (x ** R(1, 3), r"\tfrac34x^{\frac43}+C"),
    "6d": (2 / sp.sqrt(x), r"4\sqrt x+C"), "6e": (x ** R(3, 5), r"\tfrac58x^{\frac85}+C"),
    "9a": ((x + 1) ** 3, r"\tfrac14(x+1)^4+C"), "9b": ((x - 2) ** 5, r"\tfrac16(x-2)^6+C"), "9c": ((x + 5) ** 2, r"\tfrac13(x+5)^3+C"),
    "9d": ((2 * x + 3) ** 4, r"\tfrac{1}{10}(2x+3)^5+C"), "9e": ((3 * x - 4) ** 6, r"\tfrac{1}{21}(3x-4)^7+C"),
    "9f": ((5 * x - 1) ** 3, r"\tfrac{1}{20}(5x-1)^4+C"), "9g": ((1 - x) ** 3, r"-\tfrac14(1-x)^4+C"),
    "9h": ((1 - 7 * x) ** 3, r"-\tfrac{1}{28}(1-7x)^4+C"), "9i": (1 / (x - 2) ** 4, r"\dfrac{-1}{3(x-2)^3}+C"),
    "9j": (1 / (1 - x) ** 10, r"\dfrac{1}{9(1-x)^9}+C"),
    "10a": (sp.sqrt(x + 1), r"\tfrac23(x+1)^{\frac32}+C"), "10b": (sp.sqrt(x - 5), r"\tfrac23(x-5)^{\frac32}+C"),
    "10c": (sp.sqrt(1 - x), r"-\tfrac23(1-x)^{\frac32}+C"), "10d": (sp.sqrt(2 * x - 7), r"\tfrac13(2x-7)^{\frac32}+C"),
    "10e": (sp.sqrt(3 * x - 4), r"\tfrac29(3x-4)^{\frac32}+C"),
}
for k_, (f_, tb_) in EX.items():
    ANS[k_] = prim(f_, tb=tb_)
    QUESTIONS[k_] = f_
EIGHT = {"8a": (-4 * x, "4-2x^2"), "8b": (sp.Integer(3), "3x-1"), "8c": (3 * x ** 2, "x^3+1"), "8d": (-1 / x ** 2, r"\dfrac1x+1")}
for k_, (f_, tb_) in EIGHT.items():
    ANS[k_] = prim(f_, tb=tb_, conds=[("y", 1, 2)])
    QUESTIONS[k_] = f_
ANS.update({
    "4a": prim(2 * x + 3), "4ai": prim(2 * x + 3, conds=[("y", 0, 3)], form="4a", tb="x^2+3x+3"),
    "4aii": prim(2 * x + 3, conds=[("y", 1, 8)], form="4a", tb="x^2+3x+4"),
    "4b": prim(9 * x ** 2 + 4), "4bi": prim(9 * x ** 2 + 4, conds=[("y", 0, 1)], form="4b", tb="3x^3+4x+1"),
    "4bii": prim(9 * x ** 2 + 4, conds=[("y", 1, 5)], form="4b", tb="3x^3+4x-2"),
    "4c": prim(3 * x ** 2 - 4 * x + 7), "4ci": prim(3 * x ** 2 - 4 * x + 7, conds=[("y", 0, 0)], form="4c", tb="x^3-2x^2+7x"),
    "4cii": prim(3 * x ** 2 - 4 * x + 7, conds=[("y", 1, -1)], form="4c", tb="x^3-2x^2+7x-7"),
    "7": prim(sp.sqrt(x)), "7a": prim(sp.sqrt(x), conds=[("y", 0, 1)], form="7", tb=r"\tfrac23x^{\frac32}+1"),
    "7b": prim(sp.sqrt(x), conds=[("y", 9, 2)], form="7", tb=r"\tfrac23x^{\frac32}-16"),
    "11a": prim((x - 1) ** 4, conds=[("y", 1, 0)], tb=r"\tfrac15(x-1)^5"),
    "11b": prim((2 * x + 1) ** 3, conds=[("y", 0, -1)], tb=r"\tfrac18(2x+1)^4-\tfrac98"),
    "11c": prim(sp.sqrt(2 * x + 1), conds=[("y", 0, R(1, 3))], tb=r"\tfrac13(2x+1)^{\frac32}"),
    "12a": prim(3 * x ** 4 - x ** 3 + 1, conds=[("y", 0, 0)], tb=r"\tfrac35x^5-\tfrac14x^4+x"),
    "12b": prim(2 + 3 * x ** 2 - x ** 3, conds=[("y", 2, 6)], tb=r"-\tfrac14x^4+x^3+2x-2"),
    "12c": prim((2 - 5 * x) ** 3, conds=[("y", R(1, 5), 1)], tb=r"-\tfrac{1}{20}(2-5x)^4+\tfrac{21}{20}"),
    "13": prim(8 * t ** 3 - 6 * t ** 2 + 5, conds=[("y", 0, 4)], var=t, tb="2t^4-2t^3+5t+4"),
    "13@2": prim(8 * t ** 3 - 6 * t ** 2 + 5, conds=[("y", 0, 4)], var=t, tb="30"),
    "15": prim(6 * x + 4, order=2, conds=[("dy", 1, 2), ("y", 1, 4)], tb="x^3+2x^2-5x+6"),
    "16b": prim(x ** 2 - 10 * x + 41, conds=[("y", 3, -34)]),
    "17": prim(8 - 6 * x, order=2, conds=[("y", 1, 6), ("y", -1, 8)], tb="-x^3+4x^2+3"),
    "18": prim(-1 / x ** 2, conds=[("y", 1, 2), ("y", -1, 2)], tb=r"\dfrac1x+1",
               consts={C: 2 - sp.Integer(1) / 1, D: 2 - sp.Integer(1) / (-1)}, branches=[1 / x + 1, 1 / x + 3]),
})
# question texts without a data-q function: exact substrings of l4j.html (each exactly once)
QTEXT = [
    r"Let \(f(x)=(x+1)^2\) and \(g(x)=x^2+2x\).", r"Let \(f(x)=(x-3)^2\) and \(g(x)=x^2-6x+2\).",
    r"whose derivative is \(3x^2\), and check", r"passes through the point \((2,5)\).",
    r"whose derivative is \(4x^3\), and check", r"passes through the point \((1,-2)\).",
    r"say \((2,7)\)", r"whose graph passes through the point \((2,7)\).",
    r"<b>a</b> Given that \(\dfrac{dy}{dx}=12x^2-2\), and \(y=5\) when \(x=1\)",
    r"<b>b</b> Given that \(\dfrac{dy}{dx}=(2x-1)^3\), and \(y=2\) when \(x=1\)",
    r"<b>a</b> Given that \(\dfrac{dy}{dx}=6x^2+2x\), and \(y=7\) when \(x=1\)",
    r"<b>b</b> Given that \(\dfrac{dy}{dx}=(3x+1)^2\), and \(y=1\) when \(x=0\)",
    r"Given that \(\dfrac{dy}{dx}=6x^2+1\), and \(y=12\) when \(x=2\)",
    r"<b>a</b> Given that \(f''(x)=12(x-2)^2\), and \(f(2)=f(0)=0\), find \(f(3)\).",
    r"<b>b</b> Given that \(y''=6x-2\), and that when \(x=1\), \(y'=4\) and \(y=3\)",
    r"<b>a</b> Given that \(f''(x)=6(x+1)\), and \(f(0)=0\) and \(f(1)=6\), find \(f(2)\).",
    r"<b>b</b> Given that \(y''=12x+2\), and that when \(x=0\), \(y'=1\) and \(y=-2\)",
    r"Given that \(f''(x)=12(x-1)^2\), and \(f(0)=f(1)=0\), find \(f(4)\).",
    r"\(y'=2x+3\) and:&ensp;<b>i</b> \(y=3\) when \(x=0\),&ensp;<b>ii</b> \(y=8\) when \(x=1\).",
    r"\(y'=9x^2+4\) and:&ensp;<b>i</b> \(y=1\) when \(x=0\),&ensp;<b>ii</b> \(y=5\) when \(x=1\).",
    r"\(y'=3x^2-4x+7\) and:&ensp;<b>i</b> \(y=0\) when \(x=0\),&ensp;<b>ii</b> \(y=-1\) when \(x=1\).",
    r"Find \(y\) as a function of \(x\) if \(\dfrac{dy}{dx}=\sqrt x\) and:",
    r'<span class="pl">a</span>\(y=1\) when \(x=0\),</span><span><span class="pl">b</span>\(y=2\) when \(x=9\).',
    r"passing through \(A(1,2)\).",
    r"Find \(y\) if \(y'=(x-1)^4\), given that \(y=0\) when \(x=1\).",
    r"Find \(y\) if \(y'=(2x+1)^3\), given that \(y=-1\) when \(x=0\).",
    r"Find \(y\) if \(y'=\sqrt{2x+1}\), given that \(y=\tfrac13\) when \(x=0\).",
    r'Find the equation of the curve through the origin whose gradient is <span style="white-space:nowrap">\(\dfrac{dy}{dx}=3x^4-x^3+1\).',
    r"Find the curve passing through \((2,6)\) with gradient function \(\dfrac{dy}{dx}=2+3x^2-x^3\).",
    r"Find the curve through the point \(\big(\tfrac15,1\big)\) with gradient function \(y'=(2-5x)^3\).",
    r"Find \(y\) if \(\dfrac{dy}{dt}=8t^3-6t^2+5\), and \(y=4\) when \(t=0\). Hence find \(y\) when \(t=2\).",
    r"Find \(y\) if \(y''=6x+4\), given that when \(x=1\), \(y'=2\) and \(y=4\).",
    r"second derivative \(f''(x)=2x-10\). Its graph passes through the point \((3,-34)\), and at this point the tangent has a gradient of 20.",
    r"Show that \(f'(x)=x^2-10x+41\).", r"cuts the \(y\)-axis at \((0,-121)\).",
    r"If \(y''=8-6x\), show that \(y=4x^2-x^3+Cx+D\), for some constants \(C\) and \(D\).",
    r"passes through the points \((1,6)\) and \((-1,8)\).",
    r"\(f'(x)=-\dfrac{1}{x^2}\). Find the equation of the curve, given that \(f(1)=f(-1)=2\).",
]


def main():
    L, Aw = read("l4j.html"), read("a_4j.html")
    print("== question functions printed in l4j.html (data-q) against the transcription")
    for k_, f_ in QUESTIONS.items():
        b_ = block(L, "data-q", k_)
        if b_ is None:
            continue
        ms = maths(b_)
        last = split_top(ms[0])[-1] if ms else ""
        ok(bool(ms) and eq(P(last), f_), f"question {k_}: {last}", f"= {sp.sstr(f_)}")
    for s_ in QTEXT:
        ok(L.count(s_) == 1, "question text: " + s_[:90], f"found {L.count(s_)}")
    # results stated in the questions themselves (16a, 17): checked independently
    f16 = sp.integrate(2 * x - 10, x)
    c16 = sp.solve(sp.Eq(f16.subs(x, 3) + sp.Symbol("k"), 20), sp.Symbol("k"))[0]
    ok(sp.expand(f16 + c16 - (x ** 2 - 10 * x + 41)) == 0, "Q16a: f'(x) = x^2 - 10x + 41 from f''(x) = 2x - 10 and f'(3) = 20")
    ok(sp.expand(sp.diff(4 * x ** 2 - x ** 3 + C * x + D, x, 2) - (8 - 6 * x)) == 0, "Q17: y = 4x^2 - x^3 + Cx + D has y'' = 8 - 6x")
    print("== concept claims and worked examples in l4j.html")
    for k_, s_ in LESSON.items():
        b_ = block(L, "data-c", k_)
        if b_ is not None:
            check_item(k_, b_, s_)
    print("== answers in a_4j.html")
    for k_, s_ in ANS.items():
        b_ = block(Aw, "data-c", k_)
        if b_ is not None:
            check_item(k_, b_, s_)
    # every data-c key in the files is covered by a spec
    for fname, txt, keys in (("l4j.html", L, LESSON), ("a_4j.html", Aw, ANS)):
        found = set(re.findall(r'data-c="([^"]+)"', txt))
        ok(found == set(keys), f"{fname}: data-c keys all checked", f"unchecked {sorted(found - set(keys))}, missing {sorted(set(keys) - found)}")
    found = set(re.findall(r'data-q="([^"]+)"', L))
    ok(found == set(QUESTIONS), "l4j.html: data-q keys all checked", f"unchecked {sorted(found - set(QUESTIONS))}")
    print(f"\n{NOK[0]} OK, {len(FAILS)} failures")
    if FAILS:
        for f_ in FAILS:
            print("FAIL", f_)
        sys.exit(1)


if __name__ == "__main__":
    main()
