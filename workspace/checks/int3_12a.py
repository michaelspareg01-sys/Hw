"""Check of Lesson 12A (Integration Part 3): Inverse trigonometric functions, differentiating.

Reads the values PRINTED in workspace/build/int3/l12a.html (boxes, worked examples, the functions
in the tutor demos, your-turn items, textbook questions and past-paper questions) and in a_12a.html
(lesson-example answers, textbook answers, past-paper worked solutions). Each item is found with a
literal template ('@' marks a captured TeX chunk); a template must match exactly once, otherwise
the item FAILS. Printed TeX is turned into sympy with int3_tex.tex and compared with an
independent computation:
  - every printed derivative is compared with sympy.diff of the function printed in the question,
    numerically at several points of the domain (complex or undefined points are skipped, and at
    least three points must agree to 1e-9);
  - points on curves are checked by substitution (on the curve, and gradient as stated);
  - tables of values are recomputed from the function; decimals are recomputed and rounded;
  - "show that" statements printed in the questions are verified (derivative zero, stated
    second derivative, stated maximum, stated rate, stated identity);
  - the definite integral in PP 6 is recomputed with sympy.integrate;
  - the textbook answers are compared with the values in the answer pages of the Y12 book
    (PDF 924, printed 898), which were typed into TEXTBOOK below.
It also checks the past-paper block: marks add to the intro total (15-22), time is 1.5 x marks
rounded to 5 minutes, part marks add to each question's marks, numbering and source labels match
in both files, one hint per question, and each MC letter is the only option equal to the value.

Exit status 1 if anything fails. Run: python3 workspace/checks/int3_12a.py
"""
import math
import os
import random
import re
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from int3_tex import a, b, split_top, tex, x  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))   # override only for mutation tests
FAILS, NOK = [], [0]
PI = sp.pi
u_, up_, w_, wp_ = sp.symbols("u up w wp")


def ok(label):
    NOK[0] += 1
    print("OK   " + label)


def fail(label):
    FAILS.append(label)
    print("FAIL " + label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


L = read("l12a.html")
A = read("a_12a.html")


def lit(template):
    return "".join(r"((?:(?!\\\(|\\\)).)+?)" if ch == "@" else re.escape(ch) for ch in template)


def grab(label, block, template, n=None):
    if block is None:
        fail(f"{label}: block missing")
        return None
    m = re.findall(lit(template), block, re.S)
    if len(m) != 1:
        fail(f"{label}: template matched {len(m)} times: {template[:90]}")
        return None
    return m[0] if isinstance(m[0], tuple) else (m[0],)


def between(label, text, start, end):
    i = text.find(start)
    if i < 0 or text.find(start, i + 1) >= 0:
        fail(f"{label}: start marker found {text.count(start)} times: {start[:60]}")
        return None
    j = text.find(end, i + len(start))
    if j < 0:
        fail(f"{label}: end marker missing")
        return None
    return text[i:j]


def T(s, extra=None):
    s = s.strip().rstrip(".,")
    s = s.replace("\\sqrt x", "\\sqrt{x}")      # helper needs a braced argument after \sqrt and a space
    s = s.replace(r"\sin^{-1}\tfrac14(2x-3)", r"\sin^{-1}\big(\tfrac14(2x-3)\big)")
    try:
        return tex(s, extra)
    except Exception as e:  # noqa: BLE001
        fail(f"cannot parse {s[:70]!r}: {type(e).__name__}")
        return sp.nan


def num(e, xv, extra=None):
    sub = {x: xv}
    if extra:
        sub.update(extra)
    v = complex(sp.N(e.subs(sub), 30))
    return v


def same_fn(label, got, want, pts, extra=None, need=3):
    """Two expressions in x agree at the sample points where both are real and finite."""
    good, used = True, 0
    for p in pts:
        try:
            g, w = num(got, p, extra), num(want, p, extra)
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if any(math.isnan(z.real) or math.isinf(z.real) for z in (g, w)) or abs(g.imag) > 1e-12 or abs(w.imag) > 1e-12:
            continue
        used += 1
        if abs(g.real - w.real) > 1e-9 * max(1, abs(w.real)):
            good = False
    if used < need:
        fail(f"{label}: only {used} usable sample points")
        return
    (ok if good else fail)(f"{label}: {sp.sstr(got)}  vs  {sp.sstr(want)}  ({used} points)")


def same(label, got, want):
    try:
        d = sp.N(sp.sympify(got) - sp.sympify(want), 40)
        tol = 1e-12 if (sp.sympify(got).atoms(sp.Float) or sp.sympify(want).atoms(sp.Float)) else 1e-25
        good = abs(complex(d)) < tol
    except Exception as e:  # noqa: BLE001
        fail(f"{label}: {e}")
        return
    (ok if good else fail)(f"{label}: {sp.sstr(got)} vs {sp.sstr(want)}")


rng = random.Random(12)
P_ALL = [-3.7, -2.2, -1.3, -0.83, -0.61, -0.37, -0.21, -0.07, 0.04, 0.13, 0.29, 0.41, 0.58, 0.73, 0.88, 0.97,
         1.21, 1.6, 2.4, 3.3]
P_AB = {a: sp.Rational(3, 10), b: sp.Rational(-1, 5)}
P_LIN = [-2.9, -1.4, -0.3, 0.2, 0.9, 1.7, 3.2, 4.1, 5.0]   # for ax+b with a = 0.3, b = -0.2


def deriv_check(label, f_tex, d_tex, pts=P_ALL, extra=None):
    f, d = T(f_tex), T(d_tex)
    same_fn(label, d, sp.diff(f, x), pts, extra)


def last_rhs(s):
    """Last member of a printed '=' chain (top level), with \\end{aligned} etc. removed."""
    s = re.sub(r"\\end\{aligned\}|\\begin\{aligned\}|\\\\|&", " ", s)
    return split_top(s)[-1]


def blocks(text, cls):
    """Answer blocks keyed by their number: <div class="a"><span class="an">N</span>..."""
    out = {}
    parts = re.split(r'(?=<div class="a"[^>]*><span class="an">)', text)
    for p in parts:
        m = re.match(r'<div class="a"[^>]*><span class="an">([^<]+)</span>', p)
        if m:
            if m.group(1) in out:
                fail(f"duplicate answer block {m.group(1)}")
            out[m.group(1)] = p
    return out


AB = blocks(A, "a")


def ans(key):
    if key not in AB:
        fail(f"answer block {key} missing")
        return None
    return AB[key]


def qblock(n):
    m = re.findall(r'<div class="q"><span class="q-num">%d</span>(.*?)(?=<div class="q"><span class="q-num">|\{\{band|<!-- =====)' % n, L, re.S)
    if len(m) != 1:
        fail(f"question {n}: found {len(m)} times")
        return None
    return m[0]


def part(label, block, letter):
    """TeX of a part '<span class="pl">L</span>\\(...\\)' in a question block."""
    g = grab(label, block, '<span class="pl">%s</span>\\(@\\)' % letter)
    return g[0] if g else None


def apart(label, block, letter):
    """TeX of an answer part '<b>L</b> \\(...\\)'."""
    g = grab(label, block, '<b>%s</b> \\(@\\)' % letter)
    return g[0] if g else None


# ======================= A. Boxes 1-3 =======================
want = {"sin": sp.asin, "cos": sp.acos, "tan": sp.atan}
for f, F in want.items():
    g = grab(f"Box 1 {f}", L, "\\(\\displaystyle\\frac{d}{dx}\\%s^{-1}x=@\\)" % f)
    if g:
        same_fn(f"Box 1 d/dx {f}^-1 x", T(g[0]), sp.diff(F(x), x), P_ALL)
box2 = between("Box 2", L, '<div class="bt">2 Further standard forms', "</div>\n<div")
for f, F in want.items():
    g = grab(f"Box 2 {f}", box2, "\\frac{d}{dx}\\%s^{-1}(ax+b)&=@\\\\" % f) if f != "tan" else \
        grab(f"Box 2 {f}", box2, "\\frac{d}{dx}\\tan^{-1}(ax+b)&=@\\end{aligned}")
    if g:
        same_fn(f"Box 2 d/dx {f}^-1(ax+b)", T(g[0]), sp.diff(F(a * x + b), x), P_LIN, P_AB)
lin = between("Linear extensions box", L, '<div class="bt">Linear extensions</div>', "</div></div>")
for f, F, end in (("cos", sp.acos, ",\\\\"), ("tan", sp.atan, ".\\end{aligned}")):
    g = grab(f"linear ext {f}", lin, "\\frac{d}{dx}\\%s^{-1}(ax+b)&=@\\times a=@" % f + end)
    if g:
        U = a * x + b
        same_fn(f"linear ext {f} first member (u = ax+b)", T(g[0], {"u": u_}).subs(u_, U) * a, sp.diff(F(U), x), P_LIN, P_AB)
        same_fn(f"linear ext {f} last member", T(g[1]), sp.diff(F(U), x), P_LIN, P_AB)
box3 = between("Box 3", L, '<div class="bt">3 Chain-rule extensions', "<!-- ")
U0 = sp.sin(x) / 2 + sp.Rational(1, 10)       # a sample inside function
for f, F in want.items():
    sign = "-" if f == "cos" else ""
    g = grab(f"Box 3 u-form {f}", box3, "\\frac{d}{dx}\\%s^{-1}u&=@\\\\" % f) if f != "tan" else \
        grab(f"Box 3 u-form {f}", box3, "\\frac{d}{dx}\\tan^{-1}u&=@\\end{aligned}")
    if g:
        e = T(g[0].replace("u'", "{up}"), {"up": up_, "u": u_})
        same_fn(f"Box 3 u-form {f}", e.subs({up_: sp.diff(U0, x), u_: U0}), sp.diff(F(U0), x), P_ALL)
    tmpl = ("\\frac{d}{dx}\\%s^{-1}f(x)&=@\\\\" % f) if f != "tan" else "\\frac{d}{dx}\\tan^{-1}f(x)&=@\\end{aligned}"
    g = grab(f"Box 3 f-form {f}", box3, tmpl)
    if g:
        e = T(g[0].replace("f'(x)", "{wp}").replace("f(x)", "{w}"), {"wp": wp_, "w": w_})
        same_fn(f"Box 3 f-form {f}", e.subs({wp_: sp.diff(U0, x), w_: U0}), sp.diff(F(U0), x), P_ALL)
lc = between("Chain-rule box", L, '<div class="bt">Chain-rule extensions</div>', "</div></div>")
g = grab("chain-rule box display", lc, "\\frac{dy}{dx}=\\frac{dy}{du}\\times\\frac{du}{dx}=@\\times u'=@.\\]")
if g:
    same_fn("chain-rule box: dy/du for sin^-1 u", T(g[0], {"u": u_}).subs(u_, U0), 1 / sp.sqrt(1 - U0 ** 2), P_ALL)

# ======================= B. Derivations (Concept 1) =======================
der = between("derivation A/B", L, '<div class="bt">Differentiating \\(\\sin^{-1}x\\) and', '<div class="box concept"><div class="bt">Differentiating \\(\\tan')
yv = sp.Symbol("y")
for f, s0, rng_y in (("sin", "cos", (-1.4, 1.4)), ("cos", "sin", (0.2, 3.0))):
    g = grab(f"derivation {f}: root line", der, "\\begin{aligned}\\%s y&=+\\sqrt{1-\\%s^2y}\\\\&=\\sqrt{1-x^2}" % (s0, f))
    if g is not None:
        good = all(abs(float(getattr(sp, s0)(t)) - math.sqrt(1 - float(getattr(sp, f)(t)) ** 2)) < 1e-12
                   for t in [rng_y[0] + k * (rng_y[1] - rng_y[0]) / 7 for k in range(8)])
        (ok if good else fail)(f"derivation {f}: {s0} y = +sqrt(1 - {f}^2 y) on the restricted range")
tder = between("derivation tan", L, '<div class="bt">Differentiating \\(\\tan^{-1}x\\)</div>', "</div></div></div>")
g = grab("derivation tan", tder, "\\frac{dx}{dy}&=\\sec^2y\\\\&=1+\\tan^2y")
if g is not None:
    same("sec^2 y = 1 + tan^2 y", sp.simplify(sp.sec(yv) ** 2 - 1 - sp.tan(yv) ** 2), 0)

# ======================= C. Worked examples =======================
we1 = between("WE1", L, '<span class="tag">Worked example 1</span>', "<!-- ============ Concept 2")
g = grab("WE1a chain", we1, "y'&=vu'+uv'\\\\&=@\\\\&=@\\end{aligned}")
if g:
    for k, s in enumerate(g):
        deriv_check(f"WE1a line {k + 2}", r"x\tan^{-1}x", s)
g = grab("WE1b chain", we1, "\\frac{dy}{dx}&=\\frac{dy}{du}\\times\\frac{du}{dx}\\\\&=@\\\\&=@\\end{aligned}")
if g:
    for k, s in enumerate(g):
        same_fn(f"WE1b line {k + 2}", T(s), sp.diff(sp.asin(a * x + b), x), P_LIN, P_AB)

we2 = between("WE2", L, '<span class="tag">Worked example 2</span>', "<!-- ============ Concept 3")


def tangent_points(label, block, F, m, template_pts):
    g = grab(label + " points", block, template_pts)
    if not g:
        return
    pts = [(T(g[0]), T(g[1])), (T(g[2]), T(g[3]))]
    for (px, py), nm in zip(pts, "AB"):
        same(f"{label} {nm} on the curve", F(px), py)
        same(f"{label} {nm} gradient", sp.diff(F(x), x).subs(x, px), m)
    # these are the only two such points: solve F'(x) = m
    sols = sp.solve(sp.Eq(sp.diff(F(x), x) ** 2, m ** 2), x)
    sols = [s for s in sols if abs(complex(sp.N(sp.diff(F(x), x).subs(x, s))) - m) < 1e-12]
    same(f"{label} exactly two such points", len(sols), 2)


tangent_points("WE2", we2, lambda t: sp.acos(t - 1), -2,
               "points are \\(A\\big(@,@\\big)\\) and \\(B\\big(@,@\\big)\\)")
g = grab("WE2 working", we2, "\\\\ (x-1)^2&=@\\\\x-1&=@\\ \\text{ or }\\ {-@}\\\\x&=@\\ \\text{ or }\\ @,\\end{aligned}")
if g:
    same("WE2 (x-1)^2", T(g[0]), sp.Rational(3, 4))
    same("WE2 x-1", T(g[1]) ** 2, sp.Rational(3, 4))
    same("WE2 x-1 other", T(g[2]), T(g[1]))
    same("WE2 x roots", T(g[3]) + T(g[4]), 2)
    same("WE2 x roots", (T(g[3]) - 1) ** 2, sp.Rational(3, 4))
g = grab("WE2 domain", we2, "that is, \\(0\\le x\\le2\\), and the range is \\(0\\le y\\le\\pi\\)")
if g is not None:
    ok("WE2 domain 0..2 (x-1 in [-1,1]) and range 0..pi printed")

we3 = between("WE3", L, '<span class="tag">Worked example 3</span>', "<!-- ============ Concept 4")
g = grab("WE3a", we3, "&=\\frac{1}{\\sqrt{1-x^2}}+\\frac{-1}{\\sqrt{1-x^2}}\\\\&=0\\end{aligned}")
if g is not None:
    same_fn("WE3a derivative is zero", sp.Integer(0), sp.diff(sp.asin(x) + sp.acos(x), x), P_ALL)
g = grab("WE3b", we3, "so \\(C=@\\)")
if g:
    same("WE3b constant", T(g[0]), sp.asin(0) + sp.acos(0))

we4 = between("WE4", L, '<span class="tag">Worked example 4</span>', "<!-- ============ Concept 5")


def table_check(label, block, F):
    rows = re.findall(r"<tr><th>\\\((.)\\\)</th>(.*?)</tr>", block, re.S)
    if len(rows) != 2:
        fail(f"{label}: table rows found {len(rows)}")
        return
    xs = re.findall(r"<td>(.*?)</td>", rows[0][1])
    ys = re.findall(r"<td>(.*?)</td>", rows[1][1])
    if len(xs) != len(ys):
        fail(f"{label}: table columns differ")
        return
    for xs_, ys_ in zip(xs, ys):
        if "ldots" in xs_:
            continue
        xv = T(xs_.replace("\\(", "").replace("\\)", ""))
        if ys_ == "undefined":
            try:
                val = complex(sp.N(F(xv)))
                bad = math.isfinite(val.real)
            except (TypeError, ValueError, ZeroDivisionError):
                bad = False
            (fail if bad else ok)(f"{label}: undefined at x = {xv}")
            continue
        yv_ = T(ys_.replace("\\(", "").replace("\\)", ""))
        same(f"{label}: x = {xv}", F(xv), yv_)


table_check("WE4 table", we4, lambda t: sp.acos(sp.cos(t)))
g = grab("WE4 chain", we4, "\\frac{dy}{dx}&=@\\\\&=@.\\end{aligned}")
if g:
    for k, s in enumerate(g):
        same_fn(f"WE4 dy/dx line {k + 1}", T(s), sp.diff(sp.acos(sp.cos(x)), x), [0.3, 1.2, 2.8, 3.5, 4.4, 6.0, -0.5, -2.2, 7.0])
g = grab("WE4 tip chain", we4, "\\frac{dy}{dx}=\\frac{dy}{du}\\times\\frac{du}{dx}=@=@.\\]")
if g:
    for k, s in enumerate(g):
        same_fn(f"WE4 tip line {k + 2}", T(s), sp.diff(sp.acos(sp.cos(x)), x), [0.3, 1.2, 2.8, 3.5, 4.4, 6.0, -0.5, -2.2, 7.0])
for xv, d in ((0.7, 1), (2.6, 1), (3.9, -1), (5.6, -1)):    # quadrants 1, 2, 3, 4
    same(f"WE4 gradient {d} in quadrant", sp.N(sp.diff(sp.acos(sp.cos(x)), x).subs(x, xv)), d)

we5 = between("WE5", L, '<span class="tag">Worked example 5</span>', "<!-- ============ Homework")
for k, s in enumerate(re.findall(r"&=(\\frac\{-5e\^\{-5x\}\}\{1\+e\^\{-10x\}\})\.", we5)):
    deriv_check(f"WE5 result {k + 1}", r"\tan^{-1}e^{-5x}", s)
if len(re.findall(r"&=(\\frac\{-5e\^\{-5x\}\}\{1\+e\^\{-10x\}\})\.", we5)) != 2:
    fail("WE5: expected two printed results")

# ======================= D. Lesson examples C1-C5 (answers) =======================
def demo_texts(concept_marker, end_marker):
    blk = between(concept_marker, L, concept_marker, end_marker)
    d = between("demo", blk, '<span class="tag">Tutor demo</span>', '<span class="tag">Your turn</span>')
    y = between("your turn", blk, '<span class="tag">Your turn</span>', '<span class="tag">Worked example')
    return d, y


def items_ab(block):
    return re.findall(r"<b>([ab])</b> \\\((.+?)\\\)", block)


d1, y1 = demo_texts("<!-- ============ Concept 1", "<!-- ============ Concept 2")
c1 = ans("C1")
if c1 and d1 and y1:
    fs = [s for _, s in items_ab(d1)] + [s for _, s in items_ab(y1)]
    fs = [s.split("=", 1)[1] for s in fs]
    rhs = [last_rhs(s) for s in re.findall(r"\\\[(.*?)\\\]", c1, re.S)]
    if len(fs) != 4 or len(rhs) != 4:
        fail(f"C1: {len(fs)} functions, {len(rhs)} results")
    else:
        for k, (f, r) in enumerate(zip(fs, rhs)):
            pts, ex = (P_LIN, P_AB) if "ax+b" in f else (P_ALL, None)
            same_fn(f"C1 item {k + 1} d/dx {f}", T(r), sp.diff(T(f), x), pts, ex)

d2, y2 = demo_texts("<!-- ============ Concept 2", "<!-- ============ Concept 3")
c2 = ans("C2")
if c2:
    cd = between("C2 demo", c2, "<b>Tutor demo.</b>", "<b>Your turn.</b>")
    cy = c2[c2.find("<b>Your turn.</b>"):]
    fd = grab("C2 demo curve", d2, "on the curve \\(y=@\\) where the tangent has gradient @.")
    fy = grab("C2 your-turn curve", y2, "on the curve \\(y=@\\) where the tangent has gradient \\(@\\).")
    if fd and fy:
        Fd, Fy = T(fd[0]), T(fy[0])
        tangent_points("C2 demo", cd, sp.Lambda(x, Fd), int(fd[1]),
                       "points are \\(A\\big(@,@\\big)\\) and<br>\\(B\\big(@,@\\big)\\)")
        tangent_points("C2 your turn", cy, sp.Lambda(x, Fy), int(T(fy[1])),
                       "points are \\(A\\big(@,@\\big)\\) and<br>\\(B\\big(@,@\\big)\\)")
        for lab, blk_, F, tmpl in (("C2 demo", cd, Fd, "The endpoints are \\(\\big(@,@\\big)\\) and \\(\\big(@,@\\big)\\)"),
                                   ("C2 your turn", cy, Fy, "The endpoints are \\((@,@)\\) and \\((@,@)\\)")):
            g = grab(lab + " endpoints", blk_, tmpl)
            if g:
                for k in (0, 2):
                    same(f"{lab} endpoint x = {g[k]}", F.subs(x, T(g[k])), T(g[k + 1]))
                    inside = sp.N(F.subs(x, T(g[k]) + (sp.Rational(1, 1000) if k == 0 else -sp.Rational(1, 1000))))
                    outside = F.subs(x, T(g[k]) - (sp.Rational(1, 1000) if k == 0 else -sp.Rational(1, 1000)))
                    (ok if inside.is_real and not sp.N(outside).is_real else fail)(f"{lab} endpoint {g[k]} is an end of the domain")
        g = grab("C2 demo crossing", cd, "crosses the \\(x\\)-axis at \\(x=@\\)")
        if g:
            same("C2 demo x-intercept", Fd.subs(x, T(g[0])), 0)
        g = grab("C2 your-turn point", cy, "passes through \\(\\big(@,@\\big)\\)")
        if g:
            same("C2 your turn midpoint", Fy.subs(x, T(g[0])), T(g[1]))

d3, y3 = demo_texts("<!-- ============ Concept 3", "<!-- ============ Concept 4")
c3 = ans("C3")
if c3 and d3 and y3:
    for lab, q, part_ in (("demo", d3, between("C3d", c3, "<b>Tutor demo.</b>", "<b>Your turn.</b>")),
                          ("your turn", y3, c3[c3.find("<b>Your turn.</b>"):])):
        g = grab(f"C3 {lab} function", q, "<b>a</b> Differentiate \\(@\\).")
        if not g:
            continue
        F = T(g[0])
        same_fn(f"C3 {lab}: derivative of {g[0]} is zero", sp.Integer(0), sp.diff(F, x), P_ALL)
        h = grab(f"C3 {lab} single term", part_, "\\dfrac{d}{dx}@=@=@\\).")
        if h:
            same_fn(f"C3 {lab} d/dx {h[0]}", T(h[2]), sp.diff(T(h[0]), x), P_ALL)
            same_fn(f"C3 {lab} d/dx {h[0]} (middle)", T(h[1]), sp.diff(T(h[0]), x), P_ALL)
        h = grab(f"C3 {lab} constant", part_, "so \\(C=@\\)")
        if h:
            same(f"C3 {lab} constant", T(h[0]), F.subs(x, 0))
            same_fn(f"C3 {lab} identity holds", F, T(h[0]) + 0 * x, P_ALL)

d4, y4 = demo_texts("<!-- ============ Concept 4", "<!-- ============ Concept 5")
c4 = ans("C4")
if c4 and d4 and y4:
    c4d = between("C4 demo", c4, "<b>Tutor demo.</b>", "<b>Your turn.</b>")
    c4y = c4[c4.find("<b>Your turn.</b>"):]
    for lab, q, blk_ in (("demo", d4, c4d), ("your turn", y4, c4y)):
        g = grab(f"C4 {lab} function", q, "Use calculus to sketch \\(y=@\\).")
        if not g:
            continue
        s = g[0].replace(r"\tan^{-1}\tan x", r"\tan^{-1}(\tan x)").replace(r"\cos^{-1}\cos2x", r"\cos^{-1}(\cos2x)")
        F = T(s)
        table_check(f"C4 {lab} table", blk_, sp.Lambda(x, F))
        for disp in re.findall(r"\\\[(.*?)\\\]", blk_, re.S):
            mem = split_top(re.sub(r"\\begin\{aligned\}|\\end\{aligned\}|\\\\|&", " ", disp))
            for k, m in enumerate(mem[3 if "dy}{du" in disp else 1:]):
                same_fn(f"C4 {lab} dy/dx member {k + 1}", T(m), sp.diff(F, x), [0.3, 0.7, 1.2, 1.9, 2.4, 2.9, -0.4, -1.1, 4.0])
    for xv, d in ((0.4, 1), (1.3, 1), (2.0, 1), (-1.0, 1)):
        same(f"C4 demo gradient at {xv}", sp.N(sp.diff(sp.atan(sp.tan(x)), x).subs(x, xv)), d)
    for xv, d in ((0.4, 2), (1.3, 2), (1.9, -2), (2.9, -2)):
        same(f"C4 your turn gradient at {xv}", sp.N(sp.diff(sp.acos(sp.cos(2 * x)), x).subs(x, xv)), d)
    g = grab("C4 your turn intervals", c4y, "\\(\\dfrac{dy}{dx}=2\\) for \\(0<x<\\tfrac{\\pi}{2}\\) and \\(\\dfrac{dy}{dx}=-2\\) for \\(\\tfrac{\\pi}{2}<x<\\pi\\)")
    if g is not None:
        ok("C4 your turn: gradient 2 on (0, pi/2) and -2 on (pi/2, pi) printed (checked above)")

d5, y5 = demo_texts("<!-- ============ Concept 5", "<!-- ============ Homework")
c5 = ans("C5")
if c5 and d5 and y5:
    fs = [s for _, s in items_ab(d5)] + [s for _, s in items_ab(y5)]
    res = re.findall(r"\\\[\\frac\{d\}\{dx\}(.*?)=(.*)\.\\\]", c5)
    if len(fs) != 4 or len(res) != 4:
        fail(f"C5: {len(fs)} functions, {len(res)} results")
    else:
        for k, (f, (fl, chain)) in enumerate(zip(fs, res)):
            same_fn(f"C5 item {k + 1} function as printed in the answer", T(fl), T(f), P_ALL)
            mem = split_top(chain)
            for j, m in enumerate(mem[1:]):
                same_fn(f"C5 item {k + 1} d/dx {f} member {j + 2}", T(m), sp.diff(T(f), x), P_ALL)
    for lab, poly, want_ in (("demo", "x^2-1", 2 * x ** 2 - x ** 4), ("your turn", "1-x^2", 2 * x ** 2 - x ** 4)):
        g = grab(f"C5 {lab} 1-u^2", c5, "Here \\(u=%s\\)" % poly + " and \\(u'=@\\). Also \\(1-u^2=1-@=@\\)")
        if g:
            same_fn(f"C5 {lab} u'", T(g[0]), sp.diff(T(poly), x), P_ALL)
            same_fn(f"C5 {lab} u^2 expanded", T(g[1]), T(poly) ** 2, P_ALL)
            same_fn(f"C5 {lab} 1-u^2", T(g[2]), 1 - T(poly) ** 2, P_ALL)

# ======================= E. Textbook homework =======================
TEXTBOOK = {   # answers printed in the Y12 book (PDF 924), typed from the rendered page
    "2": {"a": "-1/sqrt(1-x**2)", "b": "1/(1+x**2)", "c": "2/sqrt(1-4*x**2)", "d": "3/(1+9*x**2)",
          "e": "-5/sqrt(1-25*x**2)", "f": "-1/sqrt(1-x**2)", "g": "2*x/sqrt(1-x**4)", "h": "3*x**2/(1+x**6)",
          "i": "1/(x**2+4*x+5)", "j": "1/sqrt(2*x-x**2)", "k": "asin(x)+x/sqrt(1-x**2)", "l": "2*x*atan(x)+1",
          "m": "1/sqrt(25-x**2)", "n": "4/(16+x**2)", "o": "-1/(2*sqrt(x-x**2))", "p": "1/(2*(1+x)*sqrt(x))",
          "q": "-1/(1+x**2)"},
    "9": {"a": "acos(x)", "b": "3*exp(3*x)/sqrt(1-exp(6*x))", "c": "2/sqrt(7+12*x-4*x**2)", "d": "1/(x**2-2*x+2)",
          "e": "exp(x)/sqrt(1-exp(2*x))", "f": "1/(2*sqrt(1-x**2)*asin(x))", "g": "1/(2*x*sqrt(log(x)*(1-log(x))))",
          "h": "asin(sqrt(1-x))/(2*sqrt(x))-1/(2*sqrt(1-x))", "i": "1/(1+x**2)"},
    "12": {"a": "1/sqrt(4-x**2)", "b": "-1/sqrt(2*x-x**2)", "c": "1/(2*(1+x)*sqrt(x))"},
    "18": {"a": "3*exp(3*x)/(1+exp(6*x))", "b": "3*x**2/sqrt(1-x**6)", "c": "-1/(x*sqrt(1-log(x)**2))"},
}
P_POS = [0.05, 0.11, 0.23, 0.37, 0.48, 0.61, 0.77, 0.9, 0.98, 1.3, 1.9, 2.5, 2.7, 3.1]
for qn, pts in (("2", P_ALL + P_POS), ("9", P_ALL + P_POS), ("12", P_ALL + P_POS), ("18", P_ALL + P_POS)):
    qb, ab_ = qblock(int(qn)), ans(qn)
    for letter, want_s in TEXTBOOK[qn].items():
        ftex = part(f"Q{qn}{letter} question", qb, letter)
        atex = apart(f"Q{qn}{letter} answer", ab_, letter)
        if ftex is None or atex is None:
            continue
        if "=" in ftex:
            ftex = ftex.split("=", 1)[1]
        F = T(ftex)
        got = T(atex)
        same_fn(f"Q{qn}{letter} d/dx {ftex}", got, sp.diff(F, x), pts)
        same_fn(f"Q{qn}{letter} printed = textbook answer", got, sp.sympify(want_s, locals={"x": x}), pts)

# Q1: gradients from the formula, rounded to 2 d.p.
ab1, qb1 = ans("1"), qblock(1)
if ab1 and qb1:
    qx = re.findall(r"<td>\\\((.*?)\\\)</td>", re.findall(r"<tr><th>\\\(x\\\)</th>(.*?)</tr>", qb1, re.S)[0])
    rows = re.findall(r"<tr><th>(.*?)</th>(.*?)</tr>", ab1, re.S)
    axs = re.findall(r"<td>\\\((.*?)\\\)</td>", rows[0][1])
    avs = re.findall(r"<td>(.*?)</td>", rows[1][1])
    same("Q1 x row matches question", int(axs == qx and len(axs) == 9), 1)
    for xs_, v in zip(axs, avs):
        xv = float(T(xs_))
        if abs(xv) == 1:
            (ok if v == "vertical" else fail)(f"Q1 x = {xv}: vertical tangent")
            continue
        exact = 1 / math.sqrt(1 - xv * xv)
        (ok if f"{exact:.2f}" == v else fail)(f"Q1 x = {xv}: printed {v}, formula {exact:.4f}")

# Q3: gradients at points
qb, ab_ = qblock(3), ans("3")
want3 = {"a": 2, "b": 2, "c": 1, "d": -1}
for letter in "abcd":
    g = grab(f"Q3{letter}", qb, '<span class="pl">%s</span>\\(y=@\\), at \\(x=@\\)' % letter)
    h = grab(f"Q3{letter} answer", ab_, "<b>%s</b> " % letter + "@ &nbsp;") if letter != "d" else grab("Q3d answer", ab_, "<b>d</b> \\(@\\)")
    if g and h:
        val = sp.diff(T(g[0]), x).subs(x, T(g[1]))
        same(f"Q3{letter} gradient of {g[0]} at {g[1]}", T(h[0].replace("\\(", "").replace("\\)", "")), val)
        same(f"Q3{letter} = textbook", val, want3[letter])

# Q4: tangent and normal
qb, ab_ = qblock(4), ans("4")
for letter in "ab":
    g = grab(f"Q4{letter}", qb, '<span class="pl">%s</span>\\(y=@\\), at \\(x=@\\)' % letter)
    h = grab(f"Q4{letter} answer", ab_, "<b>%s</b> Tangent is \\(y=@\\), normal is \\(y=@\\)" % letter)
    if g and h:
        F, x0 = T(g[0]), T(g[1])
        m = sp.diff(F, x).subs(x, x0)
        y0 = F.subs(x, x0)
        same_fn(f"Q4{letter} tangent", T(h[0]), y0 + m * (x - x0), P_ALL)
        same_fn(f"Q4{letter} normal", T(h[1]), y0 - (x - x0) / m, P_ALL)
same_fn("Q4a tangent = textbook", T(r"-6x+\pi"), 2 * sp.acos(3 * x).diff(x).subs(x, 0) * x + 2 * sp.acos(0), P_ALL)

# Q5, Q6: constant functions
qb5, ab5 = qblock(5), ans("5")
g = grab("Q5 answer", ab5, "<b>b</b> \\(@\\)")
if g:
    same_fn("Q5 derivative zero", sp.Integer(0), sp.diff(sp.asin(x) + sp.acos(x), x), P_ALL)
    same("Q5b constant", T(g[0]), sp.asin(sp.Rational(1, 3)) + sp.acos(sp.Rational(1, 3)))
qb6, ab6 = qblock(6), ans("6")
for letter, xs in (("a", P_ALL), ("b", P_POS)):
    f6 = part(f"Q6{letter}", qb6, letter)
    v6 = grab(f"Q6{letter} answer", ab6, "<b>%s</b> \\(@\\)" % letter)
    if f6 and v6:
        F = T(f6)
        same_fn(f"Q6{letter} derivative of {f6} is zero", sp.Integer(0), sp.diff(F, x), xs)
        same_fn(f"Q6{letter} constant value", F, T(v6[0]) + 0 * x, xs)

# Q7: f'' and concavity
qb7 = qblock(7)
g = grab("Q7a", qb7, "If \\(f(x)=@\\), show that \\(f''(x)=@\\).")
if g:
    F = T(g[0])
    same_fn("Q7a f''", T(g[1]), sp.diff(F, x, 2), P_ALL)
    conc = "concave up" if sp.diff(F, x, 2).subs(x, -1) > 0 else "concave down"
    h = grab("Q7b answer", ans("7"), "<b>b</b> @</div>")
    if h:
        (ok if h[0].strip() == conc else fail)(f"Q7b {h[0]} ({conc})")

# Q8: show-that value
g = grab("Q8", qblock(8), "curve \\(y=@\\) at the point where \\(x=@\\) is \\(@\\).")
if g:
    same("Q8 gradient", sp.diff(T(g[0]), x).subs(x, T(g[1])), T(g[2]))

# Q10: show-that results
qb10 = qblock(10)
g = grab("Q10a(i)", qb10, "If \\(y=@\\), show that \\(y''=@\\).")
if g:
    Y = T(g[0])
    same_fn("Q10a(i) y''", T(g[1]), sp.diff(Y, x, 2), P_ALL)
    same_fn("Q10a(ii) (1-x^2)y''-xy'-2 = 0", (1 - x ** 2) * sp.diff(Y, x, 2) - x * sp.diff(Y, x) - 2, sp.Integer(0), P_ALL)
g = grab("Q10b", qb10, "Show that \\(y=@\\) satisfies")
if g:
    Y = T(g[0])
    same_fn("Q10b (1-x^2)y''-xy'-y = 0", (1 - x ** 2) * sp.diff(Y, x, 2) - x * sp.diff(Y, x) - Y, sp.Integer(0), P_ALL)

# Q11
ab11 = ans("11")
g = grab("Q11", ab11, "<b>b</b> \\(x=@\\)")
h = grab("Q11c", ab11, "\\(\\dfrac{dx}{dy}=@\\ge0\\)")
k_ = grab("Q11d", ab11, "\\(\\dfrac{dy}{dx}=@\\)</div>")
if g and h and k_:
    Y = sp.Symbol("y")  # parse_expr makes y a plain Symbol
    xy = T(g[0])
    same_fn("Q11b x(y) inverts y = sin^-1 2x", xy.subs(Y, sp.asin(2 * x)), x, [-0.45, -0.3, -0.1, 0.2, 0.33, 0.49])
    dxdy = T(h[0])
    same("Q11c dx/dy", sp.simplify(dxdy - sp.diff(xy, Y)), 0)
    same_fn("Q11d dy/dx", T(k_[0]), sp.diff(sp.asin(2 * x), x), P_ALL)
    good = all(float(dxdy.subs(Y, t)) >= 0 for t in [-1.5707, -1.0, 0, 0.8, 1.5707])
    (ok if good else fail)("Q11c dx/dy >= 0 on the range")

# Q13
qb13, ab13 = qblock(13), ans("13")
g = grab("Q13 f", qb13, "Consider the function \\(f(x)=@\\).")
h = grab("Q13c", ab13, "<b>c</b> \\(@\\)")
if g and h:
    F = T(g[0])
    same_fn("Q13c f'", T(h[0]), sp.diff(F, x), P_ALL)
    same("Q13d f'(0) = 0", sp.diff(F, x).subs(x, 0), 0)
    same("Q13d f''(0) < 0", int(bool(sp.N(sp.diff(F, x, 2).subs(x, 0)) < 0)), 1)
    same_fn("Q13b even", F.subs(x, -x), F, P_ALL)

# Q14: picture
qb14 = qblock(14)
g = grab("Q14", qb14, "Show that \\(\\theta=@\\).")
h = grab("Q14b", qb14, "when the viewer is \\(@\\) metres")
k_ = grab("Q14c", qb14, "at \\(E\\) is \\(@\\).")
if g and h and k_:
    th = T(g[0])
    # independent: angle between EB and ET from coordinates E(0,0), B(x,3), T(x,4)
    ang = sp.atan2(4, x) - sp.atan2(3, x)
    same_fn("Q14a theta", th, ang, P_POS)
    crit = [s for s in sp.solve(sp.diff(th, x), x) if s.is_positive]
    same("Q14b critical point", crit[0] if len(crit) == 1 else sp.nan, T(h[0]))
    same("Q14b maximum (theta'' < 0)", int(bool(sp.N(sp.diff(th, x, 2).subs(x, T(h[0]))) < 0)), 1)
    same("Q14c maximum angle", th.subs(x, T(h[0])), T(k_[0]))

# Q15
qb15 = qblock(15)
g = grab("Q15a", qb15, "Show that \\(\\theta=@\\).")
h = grab("Q15b", qb15, "\\(\\dfrac{d\\theta}{dt}=@\\) radians per hour")
k_ = grab("Q15c answer", ans("15"), "<b>c</b> \\(@\\) rad/s")
if g and h and k_:
    th = T(g[0])
    same_fn("Q15a theta = atan2(6, x)", th, sp.atan2(6, x), P_POS)
    rate = sp.diff(th, x) * 600
    same_fn("Q15b dtheta/dt", T(h[0]), rate, P_ALL)
    same("Q15c rate of decrease at x = 3 (rad/s)", T(k_[0]), -rate.subs(x, 3) / 3600)

# Q16
g = grab("Q16", qblock(16), "domain of \\(f(x)=@\\), and")
if g:
    F = T(g[0])
    same_fn("Q16b f' = 0", sp.Integer(0), sp.diff(F, x), P_ALL)
    same_fn("Q16a odd", F.subs(x, -x), -F, P_ALL)

# Q17
qb17, ab17 = qblock(17), ans("17")
g = grab("Q17 f", qb17, "Consider the function \\(f(x)=@\\).")
h = grab("Q17b", qb17, "show that \\(f'(x)=@\\).")
if g and h:
    F = T(g[0])
    P_OUT = [-4.1, -2.7, -1.6, -1.1, 1.05, 1.4, 2.2, 3.9, 6.0]
    same_fn("Q17b f'", T(h[0]), sp.diff(F, x), P_OUT)
    d1_ = grab("Q17d x>1", ab17, "When \\(x>1\\), \\(f'(x)=@\\),")
    d2_ = grab("Q17d x<-1", ab17, "when \\(x<-1\\), \\(f'(x)=@\\).")
    if d1_ and d2_:
        same_fn("Q17d x > 1", T(d1_[0]), sp.diff(F, x), [1.05, 1.4, 2.2, 3.9, 6.0])
        same_fn("Q17d x < -1", T(d2_[0]), sp.diff(F, x), [-4.1, -2.7, -1.6, -1.1])
    lims = grab("Q17f", ab17, "<b>f</b> (i) \\(@\\) &nbsp; (ii) \\(@\\)")
    if lims:
        same("Q17f(i)", T(lims[0]), sp.limit(F, x, sp.oo))
        same("Q17f(ii)", T(lims[1]), sp.limit(F, x, -sp.oo))
    same("Q17e f' > 0 outside [-1, 1]", int(all(bool(sp.N(sp.diff(F, x).subs(x, t)) > 0) for t in (-5, -1.2, 1.2, 5))), 1)

# Q19, Q20, Q21
g = grab("Q19 g", qblock(19), "What is the domain of \\(g(x)=@\\)?")
h = grab("Q19b", qblock(19), "Show that \\(g'(x)=@\\).")
k_ = grab("Q19c answer", ans("19"), "<b>c</b> \\(g(x)=@\\) for \\(0\\le x\\le1\\)")
if g and h and k_:
    G = T(g[0])
    same_fn("Q19b g'", T(h[0]), sp.diff(G, x), P_ALL)
    same_fn("Q19c constant on [0, 1]", G, T(k_[0]) + 0 * x, [0.0, 0.1, 0.35, 0.6, 0.9, 1.0])
    same("Q19c not constant for x < 0", int(bool(abs(sp.N(G.subs(x, -0.5) - T(k_[0]))) > 0.1)), 1)
g = grab("Q20 answer", ans("20"), "\\(\\tan^{-1}\\dfrac{x+2}{1-2x}\\) is \\(@\\) for \\(x<\\tfrac12\\), and is \\(@\\) for \\(x>\\tfrac12\\)")
if g:
    F = sp.atan((x + 2) / (1 - 2 * x))
    same_fn("Q20 x < 1/2", T(g[0]), F, [-5, -2, -0.7, 0, 0.3, 0.49])
    same_fn("Q20 x > 1/2", T(g[1]), F, [0.51, 0.8, 1.5, 4, 20])
    same_fn("Q9i/Q20 derivative", sp.diff(F, x), 1 / (1 + x ** 2), P_ALL)
g = grab("Q21", qblock(21), "\\(f(x)=@\\).")
h = grab("Q21b", qblock(21), "Show that \\(f'(x)=@\\).")
if g and h:
    F = T(g[0])
    same_fn("Q21b f'", T(h[0]), sp.diff(F, x), [0.3, 1.2, 2.0, 3.0, 4.5, -0.8, -2.4])
    same("Q21a odd", sp.simplify(F.subs(x, -x) + F), 0)
    for xv, d in ((0.5, 1), (2.0, -1), (4.0, -1), (5.5, 1)):
        same(f"Q21d f'({xv}) = {d} (cos {'>' if d > 0 else '<'} 0)", sp.N(sp.diff(F, x).subs(x, xv)), d)
        same(f"Q21d sign of cos({xv})", sp.sign(sp.N(sp.cos(xv))), d)

# Omitted textbook item: Q16(c) must not be printed (doubtful in the textbook)
(fail if '<span class="pl">c</span>' in (qblock(16) or "") else ok)("Q16c omitted")

# ======================= F. Past papers =======================
pps_q = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span><span class="mk">(\d+) marks?</span></div>(.*?)(?=<div class="pp">|$)', L, re.S)
pps_a = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)</span></div>(.*?)(?=<div class="ppa">|$)', A, re.S)
same("PP count questions", len(pps_q), 9)
same("PP count answers", len(pps_a), 9)
same("PP numbering", int([int(p[0]) for p in pps_q] == list(range(1, len(pps_q) + 1))), 1)
for (nq, lq, _, _), (na, la, _) in zip(pps_q, pps_a):
    (ok if (nq, lq) == (na, la) else fail)(f"PP {nq} label matches in both files")
tot = sum(int(p[2]) for p in pps_q)
intro = grab("pp-intro", L, "<span><b>Suggested time: @ minutes</b></span><span><b>@ marks</b></span>")
if intro:
    same("PP total marks = intro", tot, int(intro[1]))
    same("PP marks in 15..22", int(15 <= tot <= 22), 1)
    same("PP time = 1.5 x marks to nearest 5", int(intro[0]), 5 * round(1.5 * tot / 5))
for n_, lab, mk, body in pps_q:
    (ok if body.count('<div class="hint">') == 1 else fail)(f"PP {n_} has exactly one hint")
    subs = re.findall(r'<span class="mk">(\d+)</span>', body)
    if subs:
        same(f"PP {n_} part marks add up", sum(map(int, subs)), int(mk))
PQ = {int(p[0]): p[3] for p in pps_q}
PA = {int(p[0]): p[2] for p in pps_a}


def mc(label, n_, value, letter_want, pts=P_ALL):
    opts = re.findall(r"<span>([A-D])\.&ensp;\\\((.*?)\\\)</span>", PQ[n_])
    if len(opts) != 4:
        fail(f"{label}: {len(opts)} options")
        return
    eq = []
    for let, o in opts:
        e = T(o)
        good = True
        for p in pts:
            try:
                g_, w_ = num(e, p), num(value, p)
            except (TypeError, ValueError, ZeroDivisionError):
                continue
            if abs(g_.imag) > 1e-12 or abs(w_.imag) > 1e-12 or math.isnan(g_.real) or math.isnan(w_.real):
                continue
            if abs(g_ - w_) > 1e-9:
                good = False
        if good:
            eq.append(let)
    same(f"{label}: options equal to the value {eq}", int(eq == [letter_want]), 1)
    g = grab(label + " answer letter", PA[n_], "<b>Answer @.</b>")
    if g:
        same(f"{label}: printed answer {g[0]}", int(g[0] == letter_want), 1)


g = grab("PP1 function", PQ[1], "What is the derivative of \\(@\\)?")
if g:
    mc("PP1", 1, sp.diff(T(g[0]), x), "B")
g = grab("PP2 function", PQ[2], "What is the derivative of \\(@\\)?")
if g:
    mc("PP2", 2, sp.diff(T(g[0]), x), "C")
    h = grab("PP2 chain", PA[2], "\\Big)&=@\\\\&=@\\\\&=@.\\end{aligned}")
    if h:
        for k, s in enumerate(h):
            same_fn(f"PP2 line {k + 1}", T(s), sp.diff(T(g[0]), x), P_ALL)
g = grab("PP3 function", PQ[3], "Find \\(\\dfrac{d}{dx}\\big(@\\big)\\).")
h = grab("PP3 result", PA[3], "=-\\frac{u'}{\\sqrt{1-u^2}}=@=@.\\]")
if g and h:
    for k, s in enumerate(h):
        same_fn(f"PP3 member {k + 1}", T(s), sp.diff(T(g[0]), x), P_ALL)
g = grab("PP4 function", PQ[4], "if \\(y=@\\)</div>")
h = grab("PP4 chain", PA[4], "&=vu'+uv'\\\\&=@\\\\&=@.\\end{aligned}")
if g and h:
    for k, s in enumerate(h):
        same_fn(f"PP4 line {k + 2}", T(s), sp.diff(T(g[0]), x), P_ALL)
g = grab("PP5 curve", PQ[5], "the curve \\(y=@\\) at the point where \\(x=@\\) passes")
if g:
    F, x0 = T(g[0]), T(g[1])
    y0, m = F.subs(x, x0), sp.diff(F, x).subs(x, x0)
    normal = y0 - (x - x0) / m
    same("PP5 normal through the origin", normal.subs(x, 0), 0)
    h = grab("PP5 point", PA[5], "So the point is \\(\\big(@,@\\big)\\).")
    rows5 = re.findall(r"\\\\y&=(.*?)(?=\\\\|\\end)", PA[5])
    k_ = (rows5[-1].rstrip("."),) if len(rows5) == 2 else None
    if k_ is None:
        fail(f"PP5: {len(rows5)} normal rows")
    if h and k_:
        same("PP5 point x", T(h[0]), x0)
        same("PP5 point y", T(h[1]), y0)
        same_fn("PP5 normal line", T(k_[0]), normal, P_ALL)
g = grab("PP6 integral", PQ[6], "\\(\\displaystyle\\int_0^{\\sqrt3}\\tan^{-1}x\\,dx\\)")
rows6 = re.findall(r"\\\\&=(.*?)(?=\\\\|\\end)", PA[6])
h = (rows6[-1].rstrip("."),) if rows6 else None
if g is not None and h:
    exact = sp.integrate(sp.atan(x), (x, 0, sp.sqrt(3)))
    same("PP6 integral", T(h[0]), exact)
    same("PP6 = school value pi sqrt3/3 - ln4/2", exact, PI * sp.sqrt(3) / 3 - sp.log(4) / 2)
    chainpp6 = re.findall(r"\\\\&=(.*?)(?=\\\\|\\end)", between("PP6 chain", PA[6], "\\int_0^{\\sqrt3}\\tan^{-1}x\\,dx&=", "\\end{aligned}") or "")
    for k, s in enumerate(chainpp6):
        if "\\Big[" in s:
            continue
        same(f"PP6 line {k + 2}", T(s), exact)
g = grab("PP7 statement", PQ[7], "Show that \\(\\dfrac{d}{dx}\\bigg(@\\bigg)=@\\)</div>")
if g:
    F = T(g[0])
    same_fn("PP7 stated derivative", T(g[1]), sp.diff(F, x), P_ALL)
    rows = re.findall(r"\\\\&=(.*?)(?=\\\\|\\end)", PA[7])
    for k, s in enumerate(rows):
        same_fn(f"PP7 line {k + 2}", T(s.replace("\\dfrac", "\\frac")), sp.diff(F, x), P_ALL)
g = grab("PP8 curve", PQ[8], "the curve \\(g(x)=@\\) at the point \\(A\\) with \\(x\\) coordinate \\(@\\) is \\(@\\).")
h = grab("PP8 b", PA[8], "\\quad\\text{and}\\quad b=@=@.\\]")
if g and h:
    bb = sp.Symbol("bb", nonzero=True)
    G = T(g[0]).subs(b, bb)
    grad = sp.diff(G, x).subs(x, T(g[1]).subs(b, bb))
    sols = sp.solve(sp.Eq(grad, T(g[2])), bb)
    same("PP8 one solution", len(sols), 1)
    same("PP8 b", T(h[0]), sols[0])
    same("PP8 b (second form)", T(h[1]), sols[0])
    k_ = grab("PP8 gradient", PA[8], "=\\frac{2\\pi}{3\\sqrt3\\,b}.\\]")
    if k_ is not None:
        for bv in (sp.Rational(1, 2), sp.Integer(-3), sp.Integer(5)):
            same(f"PP8 g'(b/2) formula at b = {bv}", grad.subs(bb, bv), 2 * PI / (3 * sp.sqrt(3) * bv))
g = grab("PP9 f", PQ[9], "Given that \\(f(x)=@\\) for")
if g:
    F = T(g[0])
    same_fn("PP9 f' = 0", sp.Integer(0), sp.diff(F, x), P_POS[:9])
    rows = re.findall(r"(?:f'\(x\)&=|\\\\&=)(.*?)(?=\\\\|\\end)", PA[9])
    if len(rows) != 4:
        fail(f"PP9: {len(rows)} lines")
    for k, s in enumerate(rows):
        same_fn(f"PP9 line {k + 1}", T(s), sp.diff(F, x), P_POS[:9])
    h = grab("PP9 root", PA[9], "so \\(\\sqrt{1-(2x-1)^2}=@\\)")
    if h:
        same_fn("PP9 sqrt(1-(2x-1)^2)", T(h[0]), sp.sqrt(1 - (2 * x - 1) ** 2), P_POS[:9])

print()
print(f"{NOK[0]} OK, {len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
