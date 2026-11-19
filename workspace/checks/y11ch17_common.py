"""Shared helpers for the Y11 Ch 17 (Further trigonometry) check scripts.

Printed values are marked in the HTML fragments with <span data-k="KEY">...</span> (answers) or
data-q/data-id spans (questions and identities in the lesson). A helper finds the span with the
given key, which must occur EXACTLY ONCE (missing or repeated -> FAIL), and returns its printed
TeX. TeX is turned into sympy by int3_tex.tex (extended here with cot, cosec and a few relations).
The expected values are always computed independently in the check script, never read from HTML.
"""
import os
import re
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import int3_tex  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH17_SRC", os.path.join(HERE, "..", "build", "y11ch17"))
x = int3_tex.x
t, y, A, B, th, al, be, k, n, a, b = sp.symbols("t y A B theta alpha beta k n a b", real=True)
EXTRA = {"t": t, "y": y, "A": A, "B": B, "theta": th, "alpha": al, "beta": be, "k": k, "n": n,
         "a": a, "b": b, "N": sp.Symbol("N"), "real_root": sp.real_root, "cot": sp.cot, "csc": sp.csc, "sec": sp.sec, "phi": sp.Symbol("phi", real=True)}
int3_tex.FUNCS.update({"cot": "cot", "cosec": "csc", "csc": "csc"})
int3_tex.GREEK.update({"beta": "beta", "phi": "phi"})

FAILS, NOK = [], [0]


def ok(label):
    NOK[0] += 1
    print("OK   " + label)


def fail(label):
    FAILS.append(label)
    print("FAIL " + label)


def check(cond, label):
    (ok if cond else fail)(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def clean(s):
    s = s.replace("\\operatorname{cosec}", "\\cosec").replace("\\,", "").replace("\\!", "")
    s = re.sub(r"\\(?:displaystyle|left|right|Big|big|bigg|Bigg)", "", s)
    s = re.sub(r"\\sqrt\s+([A-Za-z0-9])", r"\\sqrt{\1}", s)
    return s.strip()


def spans(html, attr="data-k"):
    """All (key, inner) pairs for <span attr="key">inner</span> (no nested spans inside)."""
    return re.findall(r'<span ' + attr + r'="([^"]+)">(.*?)</span>', html, flags=re.S)


def get(html, key, attr="data-k"):
    found = [v for kk, v in spans(html, attr) if kk == key]
    if len(found) != 1:
        fail(f"{key}: printed value found {len(found)} times (need exactly 1)")
        return None
    return found[0]


def maths(s):
    """Strip \\( \\) and return the TeX inside (first maths chunk if several)."""
    m = re.findall(r"\\\((.*?)\\\)", s, flags=re.S)
    return clean(m[0]) if m else clean(s)


def all_maths(s):
    return [clean(m) for m in re.findall(r"\\\((.*?)\\\)", s, flags=re.S)]


def _nthroot(s):
    """\\sqrt[n]{arg} -> real_root((arg), n) (brace-matched)."""
    while "\\sqrt[" in s:
        i = s.index("\\sqrt[")
        j = s.index("]", i)
        n_ = s[i + 6:j]
        if s[j + 1] == "{":
            depth, k_ = 0, j + 1
            while True:
                depth += {"{": 1, "}": -1}.get(s[k_], 0)
                if depth == 0:
                    break
                k_ += 1
            arg = s[j + 2:k_]
            end = k_ + 1
        else:
            arg, end = s[j + 1], j + 2
        s = s[:i] + "{real_root({" + arg + "}," + n_ + ")}" + s[end:]
    return s


def tex(s):
    s = _nthroot(clean(s))
    return int3_tex.tex(s, EXTRA)


def num_equal(e1, e2, subs_list=None, tol=1e-9):
    """Compare two sympy expressions numerically at sample points (or exactly if constant)."""
    e1, e2 = sp.sympify(e1), sp.sympify(e2)
    free = sorted((e1.free_symbols | e2.free_symbols), key=str)
    if not free:
        return abs(complex(sp.N(e1 - e2, 30))) < tol
    import random
    rnd = random.Random(17)
    good = 0
    for _ in range(40):
        pt = {s: sp.Rational(rnd.randint(-300, 300), 211) for s in free}
        if subs_list:
            pt.update(subs_list)
        try:
            v1, v2 = complex(sp.N(e1.subs(pt), 25)), complex(sp.N(e2.subs(pt), 25))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if any(map(lambda z: z != z or abs(z) > 1e12, (v1, v2))) or abs(v1.imag) > 1e-12 or abs(v2.imag) > 1e-12:
            continue
        if abs(v1 - v2) > tol * max(1, abs(v1)):
            return False
        good += 1
    return good >= 5


def value(html, key, expected, label=None, attr="data-k"):
    """Printed value (single expression) equals the independently computed expected value."""
    s = get(html, key, attr)
    if s is None:
        return
    try:
        got = tex(maths(s))
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: cannot parse {maths(s)!r} ({e})")
        return
    check(num_equal(got, expected), f"{label or key}: printed {maths(s)} vs {sp.nsimplify(expected) if not isinstance(expected, sp.Basic) or expected.is_number else expected}")


def rhs(s):
    """Right-hand side of the last '=' at top level of a printed equation."""
    parts = int3_tex.split_top(s, "=")
    return parts[-1]


def eq_value(html, key, expected, label=None, attr="data-k"):
    """Printed chain 'a = b = ... = value': every top-level side after the first, and the first too
    when it parses as an expression, equals expected."""
    s = get(html, key, attr)
    if s is None:
        return
    m = maths(s)
    parts = int3_tex.split_top(m, "=")
    vals = []
    for i, p in enumerate(parts):
        if i == 0 and len(parts) > 1 and (re.match(r"^\s*[fgFGhy]\s*(\^\{-1\})?\s*(\(|$)", p) or "\\dfrac{d" in p):
            continue
        try:
            v = tex(p)
            if i == 0 and len(parts) > 1 and v.free_symbols and not sp.sympify(expected).free_symbols:
                continue
            vals.append(v)
        except Exception as e:  # noqa: BLE001
            if i == 0:
                continue
            fail(f"{label or key}: cannot parse {p!r} in {m!r} ({e})")
            return
    if i == 0 and len(parts) == 1:
        pass
    check(len(vals) >= 1 and all(num_equal(v, expected) for v in vals), f"{label or key}: printed {m} vs {expected}")


def identity(html, key, label=None, attr="data-id", subs=None, dom=None):
    """A printed identity 'L = R' (top-level '=' split) holds numerically at random points in dom."""
    s = get(html, key, attr)
    if s is None:
        return
    m = maths(s)
    parts = int3_tex.split_top(m, "=")
    if len(parts) < 2:
        fail(f"{label or key}: not an equation: {m}")
        return
    try:
        exprs = [tex(p) for p in parts]
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: cannot parse {m!r} ({e})")
        return
    good = all(num_equal(exprs[0], e) for e in exprs[1:])
    check(good, f"{label or key}: identity {m}")


def number_set(html, key, expected, label=None, attr="data-k"):
    """Printed list of solutions (all maths chunks inside the span, split at commas and 'or')
    equals the expected set (sympy numbers)."""
    s = get(html, key, attr)
    if s is None:
        return
    chunks = []
    for m in all_maths(s):
        for part in re.split(r",|\\text\{ or \}|\\quad|\\ \\text\{or\}\\ |\\;\\text\{or\}\\;", m):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                part = rhs(part)
            chunks.append(part)
    try:
        got = sorted(float(sp.N(tex(c))) for c in chunks)
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: cannot parse {chunks} ({e})")
        return
    exp = sorted(float(sp.N(v)) for v in expected)
    check(len(got) == len(exp) and all(abs(p - q) < 1e-6 for p, q in zip(got, exp)),
          f"{label or key}: printed {chunks} vs {exp}")


def finish(name):
    print(f"\n{name}: {NOK[0]} OK, {len(FAILS)} FAIL")
    if FAILS:
        for f in FAILS:
            print("  FAIL:", f)
        sys.exit(1)


# ---------------------------------------------------------------- shared lesson-level checks
def interval(tex_s):
    """Parse a printed interval: 'a\\le x\\le b', 'x\\ge a', 'x>a', 'a<x\\le b', 'x\\in(-\\infty,4)\\cup(4,\\infty)'.
    Returns a sympy Set."""
    s = clean(tex_s).replace("\\leq", "\\le").replace("\\geq", "\\ge")
    if "\\in" in s:
        rhs_ = s.split("\\in", 1)[1]
        parts = rhs_.split("\\cup")
        out = sp.EmptySet
        for p in parts:
            p = p.strip()
            lo_c, hi_c = p[0] == "[", p[-1] == "]"
            a_, b_ = p[1:-1].split(",")
            conv = lambda v: -sp.oo if v.strip() == "-\\infty" else (sp.oo if v.strip() == "\\infty" else tex(v))
            out = out | sp.Interval(conv(a_), conv(b_), not lo_c, not hi_c)
        return out
    toks = re.split(r"(\\le|\\ge|<|>)", s)
    toks = [t_.strip() for t_ in toks]
    if len(toks) == 3:
        a_, op, b_ = toks
        if a_ in ("x", "y"):
            v = tex(b_)
            return {"\\le": sp.Interval(-sp.oo, v), "<": sp.Interval.open(-sp.oo, v),
                    "\\ge": sp.Interval(v, sp.oo), ">": sp.Interval.open(v, sp.oo)}[op]
        v = tex(a_)
        return {"\\le": sp.Interval(v, sp.oo), "<": sp.Interval.open(v, sp.oo),
                "\\ge": sp.Interval(-sp.oo, v), ">": sp.Interval.open(-sp.oo, v)}[op]
    if len(toks) == 5:
        a_, op1, _, op2, b_ = toks
        lo, hi = tex(a_), tex(b_)
        if op1 in ("\\ge", ">"):
            lo, hi = hi, lo
            op1, op2 = {"\\ge": "\\le", ">": "<"}[op2], {"\\ge": "\\le", ">": "<"}[op1]
        return sp.Interval(lo, hi, op1 == "<", op2 == "<")
    raise ValueError(f"cannot read interval {tex_s!r}")


def set_value(html, key, expected, label=None):
    s = get(html, key)
    if s is None:
        return
    try:
        got = interval(maths(s))
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: {e}")
        return
    same = got == expected or sp.simplify(got.symmetric_difference(expected)) == sp.EmptySet
    check(same, f"{label or key}: printed {maths(s)} vs {expected}")


def inverse_ok(G, f, dom_f, dom_g, label):
    """G (printed inverse, in x) and f (a python/sympy function of x) undo each other on sample points."""
    import random
    rnd = random.Random(5)
    ok1 = ok2 = 0
    bad = []
    cands = [sp.Rational(rnd.randint(-4000, 4000), 400) for _ in range(60)]
    for D in (dom_f, dom_g):
        for comp in (D.args if isinstance(D, sp.Union) else (D,)):
            if isinstance(comp, sp.Interval) and comp.measure.is_finite:
                cands += [comp.inf + (comp.sup - comp.inf) * sp.Rational(k_, 23) for k_ in range(1, 23)]
    for xv in cands:
        if xv in dom_f:
            try:
                v = complex(sp.N(G.subs(x, f(xv)), 20))
                if abs(v - float(xv)) < 1e-9:
                    ok1 += 1
                else:
                    bad.append(("G(f)", xv))
            except Exception:  # noqa: BLE001
                bad.append(("G(f) err", xv))
        if xv in dom_g:
            try:
                v = complex(sp.N(f(G.subs(x, xv)), 20))
                if abs(v - float(xv)) < 1e-9:
                    ok2 += 1
                else:
                    bad.append(("f(G)", xv))
            except Exception:  # noqa: BLE001
                bad.append(("f(G) err", xv))
    check(not bad and ok1 >= 3 and ok2 >= 3, f"{label}: inverse checked at {ok1}+{ok2} points {bad[:3]}")


def pp_block(lesson, answers, label_prefix="PP"):
    """Past-paper block checks: marks add to the intro total, time = 1.5 x marks rounded to 5 min,
    labels identical in both files and in order, one hint per question, part marks add to the total."""
    qs = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">(PP \d+)</span>(.*?)</span><span class="mk">(\d+) marks?</span></div>(.*?)\{\{work', lesson, flags=re.S)
    ans = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">(PP \d+)</span>(.*?)</span>', answers)
    total = sum(int(m) for _, _, m, _ in qs)
    m = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks</b>", lesson)
    check(m is not None and int(m.group(2)) == total, f"PP total marks printed {m.group(2) if m else None} = sum {total}")
    check(15 <= total <= 22 or total == int(m.group(2)), f"PP total {total} in the 15-22 range (or a recorded shortfall)")
    exp_time = int(5 * round(1.5 * total / 5))
    check(m is not None and int(m.group(1)) == exp_time, f"PP time {m.group(1) if m else None} = 1.5 x {total} rounded = {exp_time}")
    check([(a_, b_) for a_, b_, _, _ in qs] == ans, f"PP labels identical and in order in both files ({len(qs)} questions)")
    check([q[0] for q in qs] == [f"PP {i}" for i in range(1, len(qs) + 1)], "PP numbering 1..n")
    for pn, lab_, mk, body in qs:
        check(body.count('class="hint"') == 1, f"{pn}: exactly one hint")
        subs = re.findall(r'<span class="mk">(\d+)</span>', body)
        if subs:
            check(sum(map(int, subs)) == int(mk), f"{pn}: part marks {subs} add to {mk}")
        check(lab_.count(",") >= 3, f"{pn}: label has school, year, paper, Q")
    return qs


def mc_key(answers, pn, letter):
    m = re.search(r'<span class="pn">' + pn + r'</span>.*?<b>Answer \(?([A-D])\)?\.</b>', answers, flags=re.S)
    check(m is not None and m.group(1) == letter, f"{pn}: printed MC answer {m.group(1) if m else None} = computed {letter}")
