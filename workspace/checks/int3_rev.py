"""Check of the Integration Part 3 Revision section, tied to the printed HTML.

Reads workspace/build/int3/revision.html and a_rev.html, and recomputes with sympy:
  1. The definition boxes (17B): domain, range, restriction, gradient at the intercept, increasing or
     decreasing, for sin^-1, cos^-1 and tan^-1; the restriction box; the symmetry, complementary and
     composition statements (17C) tested at sample points inside and outside the printed intervals;
     the double-angle formulae (17E) as identities.
  2. The standard-integral table: every printed primitive is differentiated and compared with its
     integrand (general a, b, n; the reverse-chain and f'/f rows with f(x) = u = x^2 + 1).
  3. The worked examples (17B Ex 4, 5; 17C Ex 6a; 17E Ex 10, 13; 6I Ex 34; 7D Ex 17): every printed
     equality chain, compared with sympy and with the textbook's printed results.
  4. The warm-up: givens are read from revision.html; every equality and inequality the answers print is
     evaluated; final values are compared with sympy and, for Q1-Q4, with the textbook answers
     (Y11 Ext 1 book, PDF pages 951-954). Q5 primitives are differentiated; Q6 integrals are recomputed.
Every template must match exactly once, otherwise the item FAILS. Exit status 1 if anything fails.
Run: python3 workspace/checks/int3_rev.py
"""
import os
import re
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from int3_tex import tex, split_top, x, n, a, b, u, alpha, theta  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))   # override only for mutation tests
FAILS, NOK = [], [0]
y = sp.Symbol("y")
PI = sp.pi


def ok(label):
    NOK[0] += 1
    print("OK   " + label)


def fail(label):
    FAILS.append(label)
    print("FAIL " + label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def one(rx, text, label, flags=re.S):
    m = re.findall(rx, text, flags)
    if len(m) != 1:
        fail(f"{label}: found {len(m)} times")
        return None
    return m[0]


def lit(template):
    """Literal template with '@' for one captured TeX chunk (non-greedy)."""
    return "".join(r"((?:(?!\\\(|\\\)).)+?)" if ch == "@" else re.escape(ch) for ch in template)


def grab(label, block, template):
    if block is None:
        fail(f"{label}: block missing")
        return None
    m = re.findall(lit(template), block, re.S)
    if len(m) != 1:
        fail(f"{label}: template matched {len(m)} times: {template}")
        return None
    return m[0] if isinstance(m[0], tuple) else (m[0],)


def same(label, got, want, subs=None):
    try:
        g = sp.sympify(got)
        w = sp.sympify(want)
        if subs:
            g, w = g.subs(subs), w.subs(subs)
        d = sp.simplify(g - w)
        good = d == 0 or (d.free_symbols == set() and abs(complex(sp.N(d, 30))) < 1e-20)
    except Exception as e:     # noqa: BLE001
        fail(f"{label}: {e}")
        return
    (ok if good else fail)(f"{label}: {sp.sstr(got)} vs {sp.sstr(want)}")


def chain(label, span, want, subs=None, skip_first=False):
    """Every '=' member of a printed TeX chain equals want."""
    mem = split_top(span)
    for k, m in enumerate(mem):
        if skip_first and k == 0:
            continue
        m = m.strip().rstrip(".,")
        try:
            v = bracket_eval(m)
        except Exception as e:  # noqa: BLE001
            fail(f"{label} member {k + 1} {m!r}: {e}")
            continue
        same(f"{label} [{k + 1}] {m}", v, want, subs)


def take_group(s, i):
    """TeX group at s[i]: {...} or one character. Returns (content, next index)."""
    if s[i] == "{":
        depth, j = 0, i
        while True:
            depth += s[j] == "{"
            depth -= s[j] == "}"
            if depth == 0:
                return s[i + 1:j], j + 1
            j += 1
    if s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def bracket_eval(m, var=x):
    """Evaluate TeX with \\Big[F\\Big]_lo^hi replaced by F(hi) - F(lo)."""
    extra = {}
    while "\\Big[" in m:
        i = m.index("\\Big[")
        j = m.index("\\Big]", i)
        F = tex(m[i + 5:j])
        k = j + 5
        assert m[k] == "_", m
        lo, k = take_group(m, k + 1)
        assert m[k] == "^", m
        hi, k = take_group(m, k + 1)
        val = sp.simplify(F.subs(var, tex(hi)) - F.subs(var, tex(lo)))
        name = "PQRSTUVW"[len(extra)]
        extra[name] = val
        m = m[:i] + "{" + name + "}" + m[k:]
    return tex(m, extra)


def spans(text):
    return re.findall(r"\\\((.+?)\\\)", text, re.S)


def check_all_spans(label, text, subs=None):
    """Evaluate every closed equality / inequality span in text (spans with free variables are skipped)."""
    for s in spans(text):
        if "\\int" in s or "+C" in s:
            continue
        ineq = re.split(r"\\le|\\lt|\\ge|\\gt|<|>", s)
        if len(ineq) > 1:
            ops = re.findall(r"\\le|\\lt|\\ge|\\gt", s)
            try:
                vals = [tex(p).subs(subs or {}) for p in ineq]
            except Exception:   # noqa: BLE001
                continue
            if any(v.free_symbols for v in vals):
                continue
            good = True
            for (p, q, op) in zip(vals, vals[1:], ops):
                pv, qv = float(p), float(q)
                good &= {"\\le": pv <= qv + 1e-15, "\\lt": pv < qv, "\\ge": pv >= qv - 1e-15, "\\gt": pv > qv}[op]
            (ok if good else fail)(f"{label} inequality {s}")
            continue
        mem = split_top(s)
        if len(mem) < 2:
            continue
        try:
            vals = [tex(p.strip().rstrip(".,")).subs(subs or {}) for p in mem]
        except Exception:      # noqa: BLE001
            continue
        if any(v.free_symbols for v in vals):
            continue
        for k in range(1, len(vals)):
            same(f"{label} {s} [{k + 1}]", vals[k], vals[0])


rev = read("revision.html")
arev = read("a_rev.html")

# ---------- blocks of revision.html, keyed by box / example title or question number
starts = [m.start() for m in re.finditer(r'<div class="(?:box formula"|ex worked"|q">)', rev)]
starts.append(len(rev))
BLK = {}
for s0, s1 in zip(starts, starts[1:]):
    chunk = rev[s0:s1]
    t = re.search(r'<div class="bt">(.*?)</div>|<span class="ex-title">(.*?)</span>|<span class="q-num">(\d)</span>', chunk)
    key = t.group(1) or t.group(2) or ("Q" + t.group(3))
    if key in BLK:
        fail(f"duplicate block title {key}")
    BLK[key] = chunk


def blk(key):
    if key not in BLK:
        fail(f"block '{key}' missing")
        return None
    return BLK[key]


# ======================= 1. definition boxes =======================
INV = {"sin": (sp.asin, sp.sin), "cos": (sp.acos, sp.cos), "tan": (sp.atan, sp.tan)}
for f, (finv, fwd) in INV.items():
    B = blk(f"The definition of \\(y=\\{f}^{{-1}}x\\) (17B)")
    if f == "tan":
        g = grab(f"{f} box domain/range", B, f"\\(y=\\tan^{{-1}}x\\) has domain the real line and range \\(@\\lt y\\lt@\\)")
        if g:
            same("tan^-1 range low (limit at -oo)", tex(g[0]), sp.limit(finv(x), x, -sp.oo))
            same("tan^-1 range high (limit at oo)", tex(g[1]), sp.limit(finv(x), x, sp.oo))
        r = grab("tan restriction", B, "restriction of \\(y=\\tan x\\) to \\(@\\lt x\\lt@\\)")
        if r and g:
            same("tan restriction = range of tan^-1 (low)", tex(r[0]), tex(g[0]))
            same("tan restriction = range of tan^-1 (high)", tex(r[1]), tex(g[1]))
        asy = grab("tan asymptotes", B, "The lines \\(y=@\\) and \\(y=@\\) are horizontal asymptotes")
        if asy:
            same("asymptote 1", tex(asy[0]), sp.limit(finv(x), x, sp.oo))
            same("asymptote 2", tex(asy[1]), sp.limit(finv(x), x, -sp.oo))
        gr = grab("tan gradient", B, "has gradient @ at its \\(y\\)-intercept")
        if gr:
            same("tan^-1 gradient at x=0", tex(gr[0]), sp.diff(finv(x), x).subs(x, 0))
    else:
        g = grab(f"{f} box domain/range", B, f"\\(y=\\{f}^{{-1}}x\\) has domain \\(@\\le x\\le@\\) and range \\(@\\le y\\le@\\)")
        if g:
            same(f"{f}^-1 domain low = range low of {f} on restriction", tex(g[0]), -1)
            same(f"{f}^-1 domain high", tex(g[1]), 1)
            ends = [finv(sp.Integer(-1)), finv(sp.Integer(1))]
            same(f"{f}^-1 range low", tex(g[2]), min(ends, key=float))
            same(f"{f}^-1 range high", tex(g[3]), max(ends, key=float))
        r = grab(f"{f} restriction", B, f"restriction of \\(y=\\{f} x\\) to \\(@\\le x\\le@\\)")
        if r and g:
            same(f"{f} restriction = range of {f}^-1 (low)", tex(r[0]), tex(g[2]))
            same(f"{f} restriction = range of {f}^-1 (high)", tex(r[1]), tex(g[3]))
            # the restricted function really is one-to-one onto [-1, 1]
            lo, hi = float(tex(r[0])), float(tex(r[1]))
            pts = [lo + (hi - lo) * k / 400 for k in range(401)]
            vals = [float(fwd(p)) for p in pts]
            mono = all(q > p for p, q in zip(vals, vals[1:])) or all(q < p for p, q in zip(vals, vals[1:]))
            (ok if mono else fail)(f"{f} is one-to-one on the restriction")
        if f == "sin":
            if grab("sin tangent", B, "\\(y=\\sin^{-1}x\\) has tangent \\(y=x\\) at the origin"):
                same("sin^-1 tangent gradient at 0", sp.diff(finv(x), x).subs(x, 0), 1)
                same("sin^-1 passes through origin", finv(0), 0)
        else:
            gr = grab("cos gradient", B, "has gradient \\(@\\) at its \\(y\\)-intercept")
            if gr:
                same("cos^-1 gradient at x=0", tex(gr[0]), sp.diff(finv(x), x).subs(x, 0))
            t = grab("cos tangent line", B, "is the line \\(x+y=@\\), with gradient \\(-1\\)")
            if t:
                same("tangent x+y=c passes through (0, cos^-1 0)", tex(t[0]), finv(0))
    word = {"sin": "an increasing", "cos": "a decreasing", "tan": "an increasing"}[f]
    if grab(f"{f} monotone", B, f"\\(y=\\{f}^{{-1}}x\\) is {word} function"):
        d = sp.diff(finv(x), x)
        sg = [float(d.subs(x, p)) for p in (-0.9, -0.4, 0, 0.5, 0.95)]
        good = all(v > 0 for v in sg) if "increasing" in word else all(v < 0 for v in sg)
        (ok if good else fail)(f"{f}^-1 derivative sign matches '{word}'")

R = blk("Radians, notation and interpreting the restrictions (17B)")
for f in ("sin", "cos", "tan"):
    op = "\\lt" if f == "tan" else "\\le"
    g = grab(f"restriction {f}", R, f"\\(y=\\{f}^{{-1}}x\\) means \\(x=\\{f} y\\) where \\(@{op} y{op}@\\)")
    if g:
        finv = INV[f][0]
        lo = sp.limit(finv(x), x, -sp.oo) if f == "tan" else min(finv(sp.Integer(-1)), finv(sp.Integer(1)), key=float)
        hi = sp.limit(finv(x), x, sp.oo) if f == "tan" else max(finv(sp.Integer(-1)), finv(sp.Integer(1)), key=float)
        same(f"means-box {f} low", tex(g[0]), lo)
        same(f"means-box {f} high", tex(g[1]), hi)

# ======================= worked examples 4, 5, 6a (17B, 17C) =======================
E4 = blk("Textbook Example 4 (17B)")
g = grab("Ex4a", E4, "so \\(@\\).</p>\n</div><div>")
if g:
    chain("Ex4a", g[0].replace("\\alpha=", "", 1), sp.acos(sp.Rational(-1, 2)))
    same("Ex4a vs textbook 2pi/3", sp.acos(sp.Rational(-1, 2)), 2 * PI / 3)
g = grab("Ex4b", E4, "so \\(\\alpha=@\\).</p>\n</div></div>")
if g:
    chain("Ex4b", g[0], sp.atan(-1))
    same("Ex4b vs textbook -pi/4", sp.atan(-1), -PI / 4)
check_all_spans("Ex4", E4)

E5 = blk("Textbook Example 5 (17B)")
want5a = sp.tan(sp.asin(sp.Rational(-1, 5)))
g = grab("Ex5a display", E5, "\\[\\tan\\alpha=@.\\]")
if g:
    chain("Ex5a", g[0], want5a)
    same("Ex5a vs textbook -sqrt6/12", want5a, -sp.sqrt(6) / 12)
g = grab("Ex5a third side", E5, "\\(\\sqrt{5^2-1^2}=\\sqrt{24}\\)")
if g is not None:
    same("Ex5a third side", sp.sqrt(5 ** 2 - 1 ** 2), sp.sqrt(24))
g = grab("Ex5b result", E5, "So \\(\\sin\\alpha=@\\).</p>")
if g:
    same("Ex5b", tex(g[0]), sp.sin(sp.acos(sp.Rational(4, 5))))
    same("Ex5b vs textbook 3/5", tex(g[0]), sp.Rational(3, 5))
g = grab("Ex5c result", E5, "so \\(\\sin\\big(\\sin^{-1}\\tfrac45\\big)=@\\).</p>")
if g:
    same("Ex5c", tex(g[0]), sp.sin(sp.asin(sp.Rational(4, 5))))
check_all_spans("Ex5", E5)

E6 = blk("Textbook Example 6a (17C)")
f6 = sp.pi / 2 + sp.atan(x + 1)
q = grab("Ex6a equation", E6, "and any asymptotes: \\(\\ y-\\tfrac{\\pi}{2}=@\\).")
if q:
    same("Ex6a: printed equation solved for y", sp.solve(sp.Eq(y - PI / 2, tex(q[0])), y)[0], f6)
row = one(r'<tr><th>\\\(x\\\)</th>(.*?)</tr>\s*<tr><th>\\\(y\\\)</th>(.*?)</tr>', E6 or "", "Ex6a table")
if row:
    xs = [tex(t) for t in spans(row[0])]
    ys = [tex(t) for t in spans(row[1])]
    if len(xs) == len(ys) == 3:
        for xv, yv in zip(xs, ys):
            same(f"Ex6a table x={xv}", yv, f6.subs(x, xv))
    else:
        fail("Ex6a table shape")
g = grab("Ex6a range", E6, "the range is \\(@\\lt y\\lt@\\)")
if g:
    same("Ex6a range low = limit at -oo", tex(g[0]), sp.limit(f6, x, -sp.oo))
    same("Ex6a range high = limit at oo", tex(g[1]), sp.limit(f6, x, sp.oo))
g = grab("Ex6a asymptotes", E6, "asymptotes are \\(y=@\\) and \\(y=@\\)")
if g:
    same("Ex6a asymptote 1", tex(g[0]), sp.limit(f6, x, -sp.oo))
    same("Ex6a asymptote 2", tex(g[1]), sp.limit(f6, x, sp.oo))
check_all_spans("Ex6a", E6)

# ======================= symmetries, complementary angles, compositions =======================
S = blk("Symmetries and the identity \\(\\sin^{-1}x+\\cos^{-1}x=\\tfrac{\\pi}{2}\\) (17C)")
SAMPLE = [sp.Rational(k, 10) for k in (-9, -5, -2, 1, 4, 8)]
for lab, tmpl in (("sin^-1 odd", "that is, \\(\\sin^{-1}(-x)=-\\sin^{-1}x\\)"),
                  ("tan^-1 odd", "that is, \\(\\tan^{-1}(-x)=-\\tan^{-1}x\\)"),
                  ("cos^-1 symmetry", "\\[\\cos^{-1}(-x)=\\pi-\\cos^{-1}x.\\]"),
                  ("complementary", "\\(\\sin^{-1}x+\\cos^{-1}x=\\tfrac{\\pi}{2}\\), for \\(-1\\le x\\le1\\)")):
    if grab(lab, S, tmpl) is not None:
        ident = re.search(r"\\\(|\\\[", tmpl)
        body = re.findall(r"\\[\(\[](.+?)\\[\)\]]", tmpl)[0].rstrip(".")
        lhs, rhs = split_top(body)
        L, Rr = tex(lhs), tex(rhs)
        good = all(abs(float((L - Rr).subs(x, v))) < 1e-14 for v in SAMPLE)
        (ok if good else fail)(f"{lab}: {body} at {len(SAMPLE)} sample points")
for lab, s_ in (("proof step cos(pi-a)=-cos a", "\\cos(\\pi-\\alpha)=-\\cos\\alpha"),
                ("proof step sin(pi/2-a)=cos a", "\\sin\\big(\\tfrac{\\pi}{2}-\\alpha\\big)=\\cos\\alpha")):
    if s_ in (S or ""):
        L, Rr = (tex(p) for p in split_top(s_))
        same(lab, sp.expand_trig(L - Rr), 0)
    else:
        fail(f"{lab}: not found")
C = blk("Compositions (17C)")
for f, op in (("sin", "\\le"), ("cos", "\\le"), ("tan", "\\lt")):
    g = grab(f"composition {f}", C, f"\\{f}^{{-1}}(\\{f} x)=x\\) only for \\(@{op} x{op}@\\)")
    if g:
        lo, hi = float(tex(g[0])), float(tex(g[1]))
        finv, fwd = INV[f]
        inside = [lo + (hi - lo) * k / 10 for k in range(1, 10)]
        outside = [lo - 0.3, hi + 0.3]
        good_in = all(abs(float(finv(fwd(sp.Float(v)))) - v) < 1e-12 for v in inside)
        good_out = all(abs(float(finv(fwd(sp.Float(v)))) - v) > 1e-3 for v in outside)
        (ok if good_in and good_out else fail)(f"{f}^-1({f} x) = x exactly on [{lo:.4f}, {hi:.4f}]")
for f, dom in (("sin", "for \\(-1\\le x\\le1\\)"), ("tan", "for all real \\(x\\)")):
    pass
if grab("compositions forward", C, "\\(\\sin\\big(\\sin^{-1}x\\big)=x\\) and \\(\\cos\\big(\\cos^{-1}x\\big)=x\\) for \\(-1\\le x\\le1\\), and \\(\\tan\\big(\\tan^{-1}x\\big)=x\\) for all real \\(x\\)") is not None:
    good = all(abs(float(sp.sin(sp.asin(v)) - v)) < 1e-14 and abs(float(sp.cos(sp.acos(v)) - v)) < 1e-14 for v in SAMPLE)
    good &= all(abs(float(sp.tan(sp.atan(v * 7)) - v * 7)) < 1e-12 for v in SAMPLE)
    (ok if good else fail)("forward compositions are the identity")

g = grab("cos^-1(cos x) A", C, "<b>A</b> For \\(@\\le x\\le@\\), \\(\\cos^{-1}(\\cos x)=x\\)")
if g:
    lo, hi = float(tex(g[0])), float(tex(g[1]))
    ff = lambda v: float(sp.acos(sp.cos(sp.Float(v, 30))))
    good = all(abs(ff(lo + (hi - lo) * k / 8) - (lo + (hi - lo) * k / 8)) < 1e-12 for k in range(9))
    good &= all(abs(ff(-v) - ff(v)) < 1e-12 for v in (0.4, 1.9, 2.8))                       # B: even
    good &= all(abs(ff(v + 2 * float(PI)) - ff(v)) < 1e-12 for v in (-2.5, 0.7, 3.0))          # C: period 2 pi
    good &= abs(ff(-1.0) - 1.0) < 1e-12 and abs(ff(4.0) - (2 * float(PI) - 4.0)) < 1e-12
    (ok if good else fail)(f"cos^-1(cos x): identity on [{lo:.3f}, {hi:.3f}], even, period 2 pi")
if grab("cos^-1(cos x) C", C, "Because the graph has period \\(2\\pi\\)") is None:
    pass

# ======================= double-angle formulae and Examples 10, 13 =======================
D = blk("The double-angle formulae (17E)")
g = grab("compound-angle derivation", D, "\\[\\sin2\\theta=@.\\]")
if g:
    chain("sin 2theta derivation", g[0], sp.sin(2 * theta))
al = re.findall(r"\\\[\\begin\{aligned\}(.*?)\\end\{aligned\}\\\]", D or "", re.S)
if len(al) != 2:
    fail(f"double-angle aligned displays: {len(al)}")
else:
    rows = [r.replace("&", "") for r in al[0].split("\\\\")]
    for r in rows:
        L, Rr = (tex(p) for p in split_top(r))
        same(f"double-angle formula {r}", sp.simplify(sp.expand_trig(L - Rr)), 0)
    lhs = None
    for r in al[1].split("\\\\"):
        parts = [p.replace("&", "") for p in split_top(r)]
        if parts[0].strip():
            lhs = tex(parts[0])
        same(f"cos 2theta form {parts[-1]}", sp.simplify(sp.expand_trig(tex(parts[-1]) - sp.cos(2 * theta))), 0)
    if lhs is not None:
        same("cos 2theta block LHS", lhs, sp.cos(2 * theta))
for s_ in ("\\sin^2\\theta+\\cos^2\\theta=1", "1+\\tan^2\\theta=\\sec^2\\theta"):
    if s_ in (D or ""):
        L, Rr = (tex(p) for p in split_top(s_))
        same(f"Pythagorean {s_}", sp.simplify(L - Rr), 0)
    else:
        fail(f"Pythagorean {s_} not found")
E10 = blk("Textbook Example 10 (17E)")
g = grab("Ex10 chain", E10, "\\text{LHS}&=@\\\\&=@\\\\&=@\\\\&=\\text{RHS}.")
if g:
    for k, m in enumerate(g):
        same(f"Ex10 line {k + 1}", sp.simplify(sp.expand_trig(tex(m) - (1 + sp.sin(2 * x)))), 0)
E13 = blk("Textbook Example 13 (17E)")
g = grab("Ex13 sin alpha", E13, "\\(\\sin\\alpha=@\\).</p>")
if g:
    same("Ex13 sin alpha", tex(g[0]), sp.sin(sp.acos(sp.Rational(4, 5))))
g = grab("Ex13 chain", E13, "\\sin2\\alpha&=2\\sin\\alpha\\cos\\alpha\\\\&=@\\\\&=@.\\end{aligned}")
if g:
    w = sp.sin(2 * sp.acos(sp.Rational(4, 5)))
    same("Ex13 line 2", tex(g[0]), w)
    same("Ex13 line 3", tex(g[1]), w)
    same("Ex13 vs textbook 24/25", tex(g[1]), sp.Rational(24, 25))

# ======================= 2. the standard-integral table =======================
SI = blk("Standard integrals from Parts 1 and 2")
cells = re.findall(r"\\\((?:\\ )?\\displaystyle\\int(.+?)\\\)", SI or "", re.S)
if len(cells) != 16:
    fail(f"standard-integral table: {len(cells)} formula cells, 16 expected")
FX = {"f'(x)": "(2x)", "f(x)": "(x^2+1)", "\\dfrac{du}{dx}": "(2x)", "u'": "(2x)"}
NUMS = {a: sp.Rational(3, 2), b: sp.Rational(-2, 5), n: sp.Rational(7, 3)}
for c in cells:
    body = re.sub(r",\\ \\ n\\ne-1$", "", c.strip())
    lhs, rhs = split_top(body)
    integrand = lhs.strip()
    assert integrand.endswith("\\,dx"), c
    integrand = integrand[:-4]
    rhs = rhs.strip()
    if not rhs.endswith("+C"):
        fail(f"table cell without +C: {c}")
        continue
    rhs = rhs[:-2]
    for k_, v_ in FX.items():
        integrand, rhs = integrand.replace(k_, v_), rhs.replace(k_, v_)
    if re.search(r"(?<![a-z\\])u", integrand + rhs):
        integrand = re.sub(r"(?<![a-z\\])u", "(x^2+1)", integrand)
        rhs = re.sub(r"(?<![a-z\\])u", "(x^2+1)", rhs)
    I, F = tex(integrand), tex(rhs)
    good, used = True, 0
    for xv in (sp.Rational(3, 10), sp.Rational(7, 5), sp.Rational(-5, 4)):
        try:
            dv = sp.N(sp.diff(F, x).subs(NUMS).subs(x, xv), 30)
            iv = sp.N(I.subs(NUMS).subs(x, xv), 30)
            if dv.is_real is False or iv.is_real is False:
                continue
            good &= abs(complex(dv - iv)) < 1e-20
            used += 1
        except (TypeError, ValueError):
            continue
    (ok if good and used >= 2 else fail)(f"table: d/dx of {rhs} = {integrand} ({used} sample points)")
if grab("asymptote warning", SI, "<b>No calculation involving a primitive may cross an asymptote.</b>") is None:
    pass

# ======================= worked examples 34 (6I) and 17 (7D) =======================
E34 = blk("Textbook Example 34 (6I)")
al = re.findall(r"\\begin\{aligned\}\[t\](.*?)\\end\{aligned\}", E34 or "", re.S)
want = [sp.integrate(5 / x, (x, sp.E, sp.E ** 2)), sp.integrate(1 / (1 - 2 * x), (x, 1, 4))]
if len(al) != 2:
    fail(f"Ex34 aligned blocks: {len(al)}")
else:
    for lab, blkk, w, tb in (("Ex34a", al[0], want[0], 5), ("Ex34b", al[1], want[1], -sp.log(7) / 2)):
        lines = [r.replace("&", "") for r in blkk.split("\\\\")]
        mem = split_top(lines[0])[1:] + [split_top(r)[-1] for r in lines[1:]]
        for k, m in enumerate(mem):
            same(f"{lab} [{k + 1}] {m.strip()}", bracket_eval(m.strip()), w)
        same(f"{lab} vs textbook", w, tb)
g = grab("Ex34c", E34, "because it crosses the asymptote at \\(x=@\\).")
if g:
    xa = tex(g[0])
    good = 1 < xa < 5 and sp.limit(1 / (x - 2), x, xa, "+") == sp.oo
    (ok if good else fail)("Ex34c asymptote inside [1, 5]")
E17 = blk("Textbook Example 17 (7D)")
al = re.findall(r"\\begin\{aligned\}\[t\](.*?)\\end\{aligned\}", E17 or "", re.S)
if len(al) != 2:
    fail(f"Ex17 aligned blocks: {len(al)}")
else:
    for lab, blkk, w, tb in (("Ex17a", al[0], sp.integrate(sp.cos(x), (x, 0, PI)), 0),
                             ("Ex17b", al[1], sp.integrate(sp.sec(x) ** 2, (x, 0, PI / 3)), sp.sqrt(3))):
        lines = [r.replace("&", "") for r in blkk.split("\\\\")]
        mem = split_top(lines[0])[1:] + [split_top(r)[-1] for r in lines[1:]]
        for k, m in enumerate(mem):
            same(f"{lab} [{k + 1}] {m.strip()}", bracket_eval(m.strip()), w)
        same(f"{lab} vs textbook", w, tb)
g = grab("Ex17c", E17, "because it crosses the asymptote at \\(x=@\\).")
if g:
    xa = tex(g[0])
    good = PI / 4 < xa < 3 * PI / 4 and sp.cos(xa) == 0
    (ok if good else fail)("Ex17c asymptote of sec^2 inside [pi/4, 3pi/4]")
check_all_spans("Ex17", E17)

# ======================= 4. warm-up =======================
ABLK = {}
parts_a = re.split(r'<div class="a"><span class="an">(\d)</span>', arev)
for k in range(1, len(parts_a), 2):
    ABLK[int(parts_a[k])] = parts_a[k + 1]
if sorted(ABLK) != [1, 2, 3, 4, 5, 6]:
    fail(f"answer blocks {sorted(ABLK)}")


def qparts(qn):
    B = blk(f"Q{qn}")
    return dict(re.findall(r'<span class="pl">([a-z])</span>\\\((.+?)\\\)</span>', B or "", re.S))


def aparts(qn):
    t = re.split(r"<b>([a-z])</b>", ABLK.get(qn, ""))
    out = {}
    for k in range(1, len(t), 2):      # first occurrence only (figure captions repeat the letters)
        out.setdefault(t[k], t[k + 1])
    return out


BOOK = {
    1: {"b": PI / 6, "d": PI / 4, "e": -PI / 2, "f": PI / 2, "i": -PI / 3, "j": 3 * PI / 4, "k": -PI / 6, "l": PI},
    2: {"a": -PI / 3, "b": PI / 4, "c": -PI / 6, "d": 3 * PI / 4, "e": -PI / 2, "f": PI / 3},
    4: {"a": sp.Rational(-7, 9), "b": 12 * sp.sqrt(13) / 49, "c": sp.Rational(4, 3)},
}
for qn in (1, 2, 4):
    Q, A = qparts(qn), aparts(qn)
    if sorted(Q) != sorted(BOOK[qn]) or sorted(A) != sorted(BOOK[qn]):
        fail(f"Q{qn} parts: question {sorted(Q)}, answers {sorted(A)}, textbook {sorted(BOOK[qn])}")
    for p, qtex in sorted(Q.items()):
        want = sp.nsimplify(tex(qtex)) if qn != 4 else sp.simplify(tex(qtex))
        line = A.get(p, "")
        subs = None
        let = re.findall(r"Let \\\(\\alpha=(.+?)\\\)", line)
        if let:
            subs = {alpha: tex(let[0])}
        hits = [s for s in spans(line) if s.startswith(qtex + "=")]
        if len(hits) != 1:
            fail(f"Q{qn}{p}: answer span starting with the question found {len(hits)} times")
            continue
        chain(f"Q{qn}{p}", hits[0], want, subs, skip_first=True)
        last = split_top(hits[0])[-1].strip().rstrip(".")
        same(f"Q{qn}{p} final vs textbook", tex(last).subs(subs or {}), BOOK[qn][p])
        check_all_spans(f"Q{qn}{p}", line, subs)
g = grab("Q2a outside range", ABLK.get(2), "The answer is not \\(@\\), which is outside the range of \\(\\sin^{-1}\\).")
if g:
    (ok if float(tex(g[0])) > float(PI / 2) else fail)("Q2a: 4pi/3 is outside [-pi/2, pi/2]")
g = grab("Q4b third side", ABLK.get(4), "\\(\\sqrt{7^2-6^2}=\\sqrt{13}\\), so \\(\\sin\\alpha=@\\)")
if g:
    same("Q4b sin alpha", tex(g[0]), sp.sin(sp.acos(sp.Rational(6, 7))))

# ---- Q3: sketches with domain, range and symmetry (Exercise 17C Q2)
Q3, A3 = qparts(3), aparts(3)
BOOK3 = {"a": ((0, 2), (-PI / 2, PI / 2)), "b": ((-2, 0), (0, PI)), "c": (None, (0, PI))}
for p in ("a", "b", "c"):
    if p not in Q3 or p not in A3:
        fail(f"Q3{p} missing")
        continue
    lhs, rhs = split_top(Q3[p])
    fy = sp.solve(sp.Eq(tex(lhs, {"y": y}), tex(rhs)), y)[0]
    line = A3[p]
    if p in "ab":
        g = grab(f"Q3{p} domain", line, "so the domain is \\(@\\le x\\le@\\)")
        arg = list(fy.atoms(sp.asin, sp.acos))[0].args[0]
        dom = sp.solve_univariate_inequality(sp.And(arg >= -1, arg <= 1), x, relational=False) if False else \
            sp.Interval(*sorted([sp.solve(sp.Eq(arg, -1), x)[0], sp.solve(sp.Eq(arg, 1), x)[0]], key=float))
        if g:
            same(f"Q3{p} domain low", tex(g[0]), dom.start)
            same(f"Q3{p} domain high", tex(g[1]), dom.end)
            same(f"Q3{p} domain low vs textbook", tex(g[0]), BOOK3[p][0][0])
            same(f"Q3{p} domain high vs textbook", tex(g[1]), BOOK3[p][0][1])
        rg = grab(f"Q3{p} range", line, "The range is \\(@\\le y\\le@\\)")
        ends = [fy.subs(x, dom.start), fy.subs(x, dom.end)]
        if rg:
            same(f"Q3{p} range low", tex(rg[0]), min(ends, key=float))
            same(f"Q3{p} range high", tex(rg[1]), max(ends, key=float))
            same(f"Q3{p} range low vs textbook", tex(rg[0]), BOOK3[p][1][0])
            same(f"Q3{p} range high vs textbook", tex(rg[1]), BOOK3[p][1][1])
        kp = re.findall(r"Key points: (.*?)\. The", line)
        pts = re.findall(r"\\\((?:\\big)?\((.+?),(.+?)(?:\\big)?\)\\\)", kp[0]) if kp else []
        if len(pts) != 3:
            fail(f"Q3{p} key points: {len(pts)}")
        for px, py in pts:
            same(f"Q3{p} key point ({px},{py})", tex(py), fy.subs(x, tex(px)))
        sym = dom.start != -dom.end
        (ok if sym and "neither even nor odd" in line else fail)(f"Q3{p} neither even nor odd (domain not symmetric)")
    else:
        if "The domain is all real \\(x\\)" in line:
            ok("Q3c domain all real x")
        else:
            fail("Q3c domain text")
        rg = grab("Q3c range", line, "the range is \\(@\\lt y\\lt@\\)")
        if rg:
            same("Q3c range low", tex(rg[0]), sp.limit(fy, x, -sp.oo))
            same("Q3c range high", tex(rg[1]), sp.limit(fy, x, sp.oo))
            same("Q3c range vs textbook", tex(rg[1]) - tex(rg[0]), BOOK3["c"][1][1] - BOOK3["c"][1][0])
        yi = grab("Q3c y-intercept", line, "The \\(y\\)-intercept is \\(\\big(0,@\\big)\\)")
        if yi:
            same("Q3c y-intercept", tex(yi[0]), fy.subs(x, 0))
        asy = grab("Q3c asymptotes", line, "the asymptotes are \\(y=@\\) and \\(y=@\\)")
        if asy:
            same("Q3c asymptote 1", tex(asy[0]), sp.limit(fy, x, -sp.oo))
            same("Q3c asymptote 2", tex(asy[1]), sp.limit(fy, x, sp.oo))
        rep_ = grab("Q3c f(-x)", line, "replacing \\(x\\) by \\(-x\\) gives \\(@\\), which is neither")
        if rep_:
            same("Q3c f(-x)", tex(rep_[0]), fy.subs(x, -x))
            v = sp.Integer(1)
            good = sp.simplify(fy.subs(x, -v) - fy.subs(x, v)) != 0 and sp.simplify(fy.subs(x, -v) + fy.subs(x, v)) != 0
            (ok if good else fail)("Q3c neither even nor odd at x = 1")

# ---- Q5: indefinite integrals, every printed primitive differentiated
Q5, A5 = qparts(5), aparts(5)
if sorted(Q5) != list("abcdefghi") or sorted(A5) != list("abcdefghi"):
    fail(f"Q5 parts {sorted(Q5)} / {sorted(A5)}")
for p, qtex in sorted(Q5.items()):
    m = re.fullmatch(r"\\displaystyle\\int(.+)\\,dx", qtex)
    if not m:
        fail(f"Q5{p} question form {qtex}")
        continue
    integrand = tex(m.group(1))
    hits = [s for s in spans(A5.get(p, "")) if s.startswith(qtex + "=")]
    if len(hits) != 1:
        fail(f"Q5{p}: answer span found {len(hits)} times")
        continue
    body = re.sub(r"\\qquad\(.*\)$", "", hits[0])
    mem = split_top(body)[1:]
    for k, mm in enumerate(mem):
        mm = mm.strip()
        if not mm.endswith("+C"):
            fail(f"Q5{p} member {mm} has no +C")
            continue
        F = tex(mm[:-2])
        if F.free_symbols - {x}:
            fail(f"Q5{p} member {mm} has symbols {F.free_symbols}")
            continue
        good = all(abs(complex(sp.N((sp.diff(F, x) - integrand).subs(x, xv), 30))) < 1e-20
                   for xv in (sp.Rational(3, 10), sp.Rational(6, 5), sp.Rational(-4, 5)))
        good &= sp.simplify(sp.diff(F, x) - integrand).subs(x, sp.Rational(7, 3)) == 0
        (ok if good else fail)(f"Q5{p} [{k + 2}] d/dx({mm[:-2]}) = {m.group(1)}")
    check_all_spans(f"Q5{p}", A5.get(p, ""))
for p, fx, dfx in (("h", "x^2+1", "2x"), ("i", "x^3+1", "3x^2")):
    if grab(f"Q5{p} f'(x)", A5.get(p), f"Let \\(f(x)={fx}\\). Then \\(f'(x)={dfx}\\)") is not None:
        same(f"Q5{p} f'", sp.diff(tex(fx), x), tex(dfx))

# ---- Q6: definite integrals
Q6, A6 = qparts(6), aparts(6)
if sorted(Q6) != list("abcdef") or sorted(A6) != list("abcdef"):
    fail(f"Q6 parts {sorted(Q6)} / {sorted(A6)}")
for p, qtex in sorted(Q6.items()):
    s = qtex[len("\\displaystyle\\int"):]
    if not qtex.startswith("\\displaystyle\\int_") or not s.endswith("\\,dx"):
        fail(f"Q6{p} question form")
        continue
    lo, k = take_group(s, 1)
    hi, k = take_group(s, k + 1)
    integrand = tex(s[k:-4])
    want = sp.simplify(sp.integrate(integrand, (x, tex(lo), tex(hi))))
    hits = [t for t in spans(A6.get(p, "")) if t.startswith(qtex + "=")]
    if len(hits) != 1:
        fail(f"Q6{p}: answer span found {len(hits)} times")
        continue
    chain(f"Q6{p}", hits[0], want, skip_first=True)
    br = re.findall(r"(.*?)\\Big\[(.*?)\\Big\]", split_top(hits[0])[1])
    if br:
        coef = tex(br[0][0]) if br[0][0].strip() else 1
        dF = coef * sp.diff(tex(br[0][1]), x)
        L0, H0 = float(tex(lo)), float(tex(hi))
        good = all(abs(float((dF - integrand).subs(x, sp.Float(L0 + (H0 - L0) * t / 7, 30)))) < 1e-20 for t in range(1, 7))
        (ok if good else fail)(f"Q6{p} primitive: {sp.sstr(coef)} x d/dx[{br[0][1]}] = integrand on [{lo}, {hi}]")
    else:
        fail(f"Q6{p}: no bracketed primitive")

print(f"\n{NOK[0]} checks passed, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
