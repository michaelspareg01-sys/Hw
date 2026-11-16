r"""Shared helpers for the Simultaneous Equations checks (sim_rev.py, sim_l1.py, ...).

The HTML is read as printed. Tags:
  <span data-q="K">  a question item: its equations, expression or values, in TeX (lesson files);
  <span data-s="K">  a printed solution of pair K, e.g. \(x=3\), \(y=-1\) (answers);
  <div  data-w="K">  printed working for K: every equation in it must hold at the solution of K;
  <div  data-c="K">  the printed check for K: every equality in it must be numerically true, and it
                     must contain at least two equalities (one per original equation);
  <span data-v="K">  a printed number (the value after the last "=", or the whole span);
  <span data-k="K">  a printed answer in words, letters or coordinates.
Every key must occur exactly once in the files read, and every key read must be checked, or the check
FAILS. TeX is turned into sympy expressions by tex2sym (fractions, mixed numbers 3\tfrac{3}{5},
\times, \div, implicit products); nothing is evaluated from the text in any other way.
Graphs are read from build/sim/svg/*.svg: the plotted lines (class "ln"), the marked points (class
"ix"/"pt") and the tick labels (class "tx"/"ty"), whose positions give the scale of each axis.
"""
import os
import re
from fractions import Fraction
from math import hypot

import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application, convert_xor)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("SIM_SRC", os.path.join(HERE, "..", "build", "sim"))
FAILS, NOK = [], [0]
TR = standard_transformations + (implicit_multiplication_application, convert_xor)
LETTERS = {c: sp.Symbol(c) for c in "abcdhkmnpqrstuvwxyz"}


def ok(flag, label, detail=""):
    if flag:
        NOK[0] += 1
        print("OK       " + label + ("  " + detail if detail else ""))
    else:
        FAILS.append(label)
        print("MISMATCH " + label + ("  " + detail if detail else ""))
    return flag


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def _blocks(names, tag, attr):
    """{key: [inner html]} for <tag attr="key"> ... </tag>, balancing nested tags of the same name."""
    out = {}
    for n in names:
        s = read(n)
        for m in re.finditer(r'<%s %s="([^"]+)"[^>]*>' % (tag, attr), s):
            i, depth = m.end(), 1
            while depth:
                a, b = s.find("<" + tag, i), s.find("</%s>" % tag, i)
                if a != -1 and a < b:
                    depth += 1
                    i = a + len(tag) + 1
                else:
                    depth -= 1
                    i = b + len(tag) + 3
            out.setdefault(m.group(1), []).append(s[m.end():i - len(tag) - 3])
    return out


# ---------------- TeX to sympy ----------------

def _brace(s, i):
    """s[i] == '{': return (content, index after the matching '}')."""
    depth, j = 0, i
    while True:
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1


def _fracs(s):
    out, i = [], 0
    while i < len(s):
        m = re.match(r"\\[dt]?frac", s[i:])
        if m:
            num, j = _brace(s, i + m.end())
            den, k = _brace(s, j)
            mixed = m.group(0) == "\\tfrac" and out and out[-1].isdigit()
            frac = f"(({_fracs(num)})/({_fracs(den)}))"
            out.append(("+" if mixed else "") + frac)
            if mixed:          # 3\tfrac{3}{5} -> (3+3/5): wrap the whole number
                k0 = len(out) - 2
                while k0 >= 0 and out[k0].isdigit():
                    k0 -= 1
                out.insert(k0 + 1, "(")
                out.append(")")
            i = k
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def clean_tex(s):
    s = s.replace("−", "-").replace("&minus;", "-").replace("\\left", "").replace("\\right", "")
    s = re.sub(r"\\[,;!: ]|\\quad|\\qquad|~", " ", s)
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    s = re.sub(r"\\text\{[^}]*\}", " ", s)
    return s


def tex2sym(s):
    s = _fracs(clean_tex(s))
    s = s.replace("{", "(").replace("}", ")")
    s = re.sub(r"\s+", "", s)
    if not s:
        raise ValueError("empty expression")
    return parse_expr(s, local_dict=LETTERS, transformations=TR, evaluate=True)


def maths(html):
    """The TeX of every \\( \\) and \\[ \\] in an HTML fragment, in order."""
    return [m.group(1) or m.group(2) for m in re.finditer(r"\\\((.+?)\\\)|\\\[(.+?)\\\]", html, re.S)]


def equations(html):
    """Every equation in the maths of a fragment: a list of (lhs, rhs) sympy pairs. A chain a = b = c gives
    (a, b) and (b, c). Rows of aligned/array/cases environments are split; & and alignment are ignored."""
    out = []
    for t in maths(html):
        t = re.sub(r"\\(begin|end)\{[a-z*]+\}(\{[a-z]+\})?", " ", t)
        for row in re.split(r"\\\\", t):
            row = row.replace("&", "")
            row = re.sub(r"\\quad.*$", "", row)               # annotations such as \quad(-2)
            if "\\neq" in row or "\\ne " in row:
                continue
            parts = [p for p in row.split("=")]
            if len(parts) < 2 or any(not p.strip() for p in parts):
                continue
            syms = [tex2sym(p) for p in parts]
            out += list(zip(syms[:-1], syms[1:]))
    return out


def assignments(html):
    """{symbol name: value} from a printed solution such as \\(x=3\\), \\(y=-\\frac{1}{2}\\)."""
    out = {}
    for t in maths(html):
        t = re.sub(r"\\[,;!: ]", " ", t)
        for piece in re.split(r",(?![^{]*\})", t):
            m = re.fullmatch(r"\s*([a-z])\s*=\s*(.+?)\s*", piece)
            if m:                                   # a chain y = 2(2) = 4: the value is the last part
                out[m.group(1)] = sp.nsimplify(tex2sym(m.group(2).split("=")[-1]))
    return out


def points(html):
    """Every coordinate pair (a, b) printed in the maths of a fragment."""
    out = []
    for t in maths(html):
        t = clean_tex(t)
        for m in re.finditer(r"\(\s*([^(),]+?)\s*,\s*([^(),]+?)\s*\)", t):
            try:
                out.append((sp.nsimplify(tex2sym(m.group(1))), sp.nsimplify(tex2sym(m.group(2)))))
            except Exception:
                pass
    return out


def solve_pair(eqs, names=None):
    """Solve a list of (lhs, rhs) equations; returns {name: value} for a unique solution, else None."""
    exprs = [sp.expand(l - r) for l, r in eqs]
    syms = sorted(set().union(*[e.free_symbols for e in exprs]), key=lambda s: s.name)
    if names:
        syms = [sp.Symbol(n) for n in names]
    sol = sp.solve(exprs, syms, dict=True)
    if len(sol) != 1 or set(sol[0]) != set(syms):
        return None
    return {k.name: sp.nsimplify(v) for k, v in sol[0].items()}


def holds(eq, sub):
    l, r = eq
    return sp.simplify((l - r).subs({sp.Symbol(k): v for k, v in sub.items()})) == 0


class Values:
    def __init__(self, names):
        self.names = names
        self.d = {a: _blocks(names, "span", "data-" + a) for a in ("q", "s", "v", "k")}
        for a in ("w", "c"):
            d = _blocks(names, "div", "data-" + a)
            for k, v in _blocks(names, "span", "data-" + a).items():
                d.setdefault(k, []).extend(v)
            self.d[a] = d
        self.used = set()

    def get(self, attr, key):
        self.used.add((attr, key))
        v = self.d[attr].get(key, [])
        if len(v) != 1:
            ok(False, f"data-{attr}={key}", f"found {len(v)} times (must be exactly once)")
            return None
        return v[0]

    def has(self, attr, key):
        return key in self.d[attr]

    def keys(self, attr):
        return sorted(self.d[attr])

    def num(self, key):
        s = self.get("v", key)
        if s is None:
            return None
        t = maths(s)
        expr = t[-1] if t else re.sub(r"<[^>]+>", "", s)
        return sp.nsimplify(tex2sym(expr.split("=")[-1]))

    def unused(self):
        allk = {(a, k) for a in self.d for k in self.d[a]}
        return sorted(allk - self.used)


def check_num(V, key, expect, label=""):
    got = V.num(key)
    if got is None:
        return
    ok(sp.simplify(got - expect) == 0, f"{key} {label}".strip(), f"printed {got}, computed {expect}")


def check_pair(V, key, eqs, label="", working=True, check=True):
    """Solve the printed pair, compare with the printed solution, test the working and the check."""
    sol = solve_pair(eqs)
    ok(sol is not None, f"{key}: the pair has exactly one solution", str(sol))
    if sol is None:
        return None
    s = V.get("s", key)
    if s is not None:
        got = assignments(s)
        if not got and len(points(s)) == 1 and set(sol) == {"x", "y"}:
            (px, py), = points(s)
            got = {"x": px, "y": py}
        ok(got == sol, f"{key} solution {label}".strip(), f"printed {got}, computed {sol}")
    if working:
        w = V.get("w", key)
        if w is not None:
            eqw = equations(w)
            ok(len(eqw) >= 2, f"{key}: working has lines", f"{len(eqw)} equations")
            bad = [f"{l} = {r}" for l, r in eqw if not holds((l, r), sol)]
            ok(not bad, f"{key}: every working line holds at the solution", "; ".join(bad))
    if check:
        c = V.get("c", key)
        if c is not None:
            eqc = equations(c)
            bad = [f"{l} = {r}" for l, r in eqc if not holds((l, r), sol)]
            ok(len(eqc) >= 2 and not bad, f"{key}: printed check is true", f"{len(eqc)} equalities; " + "; ".join(bad))
            # the check must show both original equations: each one, at the solution, appears
            vals = {sp.nsimplify(e.subs({sp.Symbol(k): v for k, v in sol.items()})) for pair in eqc for e in pair}
            for l, r in eqs:
                lv = sp.nsimplify(l.subs({sp.Symbol(k): v for k, v in sol.items()}))
                ok(lv in vals, f"{key}: check substitutes into {l} = {r}", f"value {lv}")
    return sol


def finish(vals_list=()):
    for v in vals_list:
        for attr, k in v.unused():
            ok(False, f"data-{attr}={k}", "printed value has no check")
    print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
    if FAILS:
        for f in FAILS:
            print("  FAIL", f)
        raise SystemExit(1)


# ---------------- SVG graphs ----------------

def svg(name):
    return read(os.path.join("svg", name + ".svg"))


def svg_texts(name, cls=None):
    out = []
    for m in re.finditer(r"<text([^>]*)>(.*?)</text>", svg(name), re.S):
        a = m.group(1)
        c = re.search(r'class="([^"]+)"', a)
        if cls and (not c or c.group(1) != cls):
            continue
        x = float(re.search(r'\sx="([-\d.]+)"', a).group(1))
        y = float(re.search(r'\sy="([-\d.]+)"', a).group(1))
        size = float(re.search(r'font-size="([\d.]+)"', a).group(1))
        # y is the baseline; the pack's labels are centred 0.35 em above it
        out.append((re.sub(r"<[^>]+>", "", m.group(2)).replace("−", "-").strip(), x, y - 0.35 * size))
    return out


def tick_marks(name):
    """Positions of the tick marks: short lines (6 px) across the x-axis (vertical) and the y-axis."""
    xs, ys = [], []
    for m in re.finditer(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="[^"]+" '
                         r'stroke-width="1.1"/>', svg(name)):
        x1, y1, x2, y2 = (float(v) for v in m.groups())
        if abs(x1 - x2) < 1e-6 and abs(abs(y2 - y1) - 6) < 0.01:
            xs.append(x1)
        elif abs(y1 - y2) < 1e-6 and abs(abs(x2 - x1) - 6) < 0.01:
            ys.append(y1)
    return xs, ys


def axis_scale(name):
    """Fit px = p0 + k * value for each axis: each tick label is matched to its nearest tick mark (labels
    may be moved aside where a plotted line crosses an axis), and the tick-mark positions are fitted
    against the printed values. Returns (to_xy, unit_x, unit_y)."""
    def fit(pairs):
        n = len(pairs)
        mv = sum(v for v, p in pairs) / n
        mp = sum(p for v, p in pairs) / n
        k = sum((v - mv) * (p - mp) for v, p in pairs) / sum((v - mv) ** 2 for v, p in pairs)
        res = max(abs(mp + k * (v - mv) - p) for v, p in pairs)
        return mp - k * mv, k, res
    tx, ty = tick_marks(name)
    xs = [(float(t), min(tx, key=lambda q: abs(q - x))) for t, x, y in svg_texts(name, "tx")]
    ys = [(float(t), min(ty, key=lambda q: abs(q - y))) for t, x, y in svg_texts(name, "ty")]
    ok(len(xs) >= 2 and len(ys) >= 2, f"{name}: at least two tick labels on each axis", f"{len(xs)}, {len(ys)}")
    ok(len({p for v, p in xs}) == len(xs) and len({p for v, p in ys}) == len(ys),
       f"{name}: each tick label has its own tick mark")
    x0, kx, rx = fit(xs)
    y0, ky, ry = fit(ys)
    ok(rx < 0.6 and ry < 0.6, f"{name}: tick marks are evenly spaced", f"residuals {rx:.2f}, {ry:.2f} px")
    ok(abs(kx + ky) < 0.02 * abs(kx), f"{name}: drawn to scale (same unit on both axes)", f"{kx:.2f} and {-ky:.2f} px")

    def to_xy(px, py):
        return ((px - x0) / kx, (py - y0) / ky)
    return to_xy, kx, -ky


def plotted_lines(name):
    """[(a, b, c, eq_attr)] for each class="ln" line: a x + b y = c in coordinates, normalised."""
    to_xy, _, _ = axis_scale(name)
    out = []
    for m in re.finditer(r'<line class="ln"([^>]*)/>', svg(name)):
        a = m.group(1)
        g = {k: float(re.search(r'\s%s="([-\d.]+)"' % k, a).group(1)) for k in ("x1", "y1", "x2", "y2")}
        e = re.search(r'data-eq="([^"]+)"', a)
        (u1, v1), (u2, v2) = to_xy(g["x1"], g["y1"]), to_xy(g["x2"], g["y2"])
        A, B = v2 - v1, -(u2 - u1)
        C = A * u1 + B * v1
        n = hypot(A, B)
        out.append((A / n, B / n, C / n, e.group(1) if e else None, (u1, v1), (u2, v2)))
    return out


def marked_points(name, cls="ix"):
    to_xy, _, _ = axis_scale(name)
    out = []
    for m in re.finditer(r'<circle class="%s"([^>]*)/>' % cls, svg(name)):
        a = m.group(1)
        cx = float(re.search(r'\scx="([-\d.]+)"', a).group(1))
        cy = float(re.search(r'\scy="([-\d.]+)"', a).group(1))
        out.append(to_xy(cx, cy))
    return out


def on_line(line, p, tol=0.03):
    a, b, c = line[:3]
    return abs(a * p[0] + b * p[1] - c) < tol


def same_line(line, eq, tol=0.03):
    """Does the drawn line coincide with the sympy equation eq = (lhs, rhs)?"""
    x, y = sp.Symbol("x"), sp.Symbol("y")
    e = sp.expand(eq[0] - eq[1])
    A, B, C = float(e.coeff(x)), float(e.coeff(y)), -float(e.subs({x: 0, y: 0}))
    n = hypot(A, B)
    a, b, c = line[:3]
    s = 1 if A * a + B * b > 0 else -1
    return abs(a - s * A / n) < tol and abs(b - s * B / n) < tol and abs(c - s * C / n) < tol * max(1, abs(c))
