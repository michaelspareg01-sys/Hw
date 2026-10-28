"""Numeric check of the Lesson 10A past-paper mini exam (Ch 10 pack).

Same method as ch10_pp9e.py. For each item, the script finds the value printed
in the past-paper worked solutions of workspace/build/ch10/a_10a.html (template
with '@' marking the value; the template must match exactly once in that PP
block, otherwise the item FAILS), converts the printed LaTeX to a number, a
function, or a vector function x i + y j, and compares it with a value computed
independently from the question data. The independent values come from root
finding on the displacement functions, numerical derivatives, and a step-by-step
integration of the acceleration (velocity Verlet, exact for constant
acceleration). 'r' items are compared to the printed precision, the others
exactly (1e-9 relative). It also checks the lesson fragment: the marks add to
the total in the intro line (15-22), the time is 1.5 x marks rounded to 5, the
numbering and source labels match, and the MC letter is the option with the
computed value.

Exit status is 1 if anything fails. Run: python3 workspace/checks/ch10_pp10a.py
"""
import os
import re
import sys
from math import sqrt, pi, atan, atan2, sin, cos, tan, hypot, radians, degrees

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("CH10_SRC", os.path.join(HERE, "..", "build", "ch10"))   # override only for mutation tests
FAILS = []
G = 10   # every question here uses g = 10 (PP 1 is checked for symbolic g)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    print(("OK       " if ok else "MISMATCH ") + label + "  " + detail)
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- LaTeX -> Python
def _arg(s, i):
    if s[i] == "{":
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(s[j], 0)
            if depth == 0:
                return s[i + 1:j], j + 1
            j += 1
    return s[i], i + 1


def _conv(s):
    out, i = [], 0
    while i < len(s):
        if s.startswith(("\\dfrac", "\\tfrac", "\\frac"), i):
            i = s.index("frac", i) + 4
            a, i = _arg(s, i)
            b, i = _arg(s, i)
            out.append(f"(({_conv(a)})/({_conv(b)}))")
        elif s.startswith("\\sqrt", i):
            a, i = _arg(s, i + 5)
            out.append(f"sqrt({_conv(a)})")
        elif s.startswith("\\pi", i):
            out.append(" pi ")
            i += 3
        elif s.startswith("\\times", i):
            out.append("*")
            i += 6
        elif s[i] == "\\":
            raise ValueError(f"unknown macro in {s!r}")
        elif s[i] in "{}":
            out.append("(" if s[i] == "{" else ")")
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


FUNCS = {"sqrt": sqrt, "pi": pi, "sin": sin, "cos": cos, "tan": tan}


def tex_to_py(tex):
    s = re.sub(r"\\left|\\right|\\,|\\!|\s", "", tex)
    # trig of a named angle: \cos\alpha^\circ -> cos(al) (al in degrees), \sin\theta -> sin(th)
    s = re.sub(r"\\(sin|cos|tan)\\alpha\^\\circ", r"\1{AL}", s)
    s = re.sub(r"\\(sin|cos|tan)\\theta", r"\1{TH}", s)
    s = re.sub(r"\\(sin|cos|tan)\{", r"\1{", s)
    s = s.replace("\\sin{", "sin{").replace("\\cos{", "cos{").replace("\\tan{", "tan{")
    py = _conv(s).replace("^", "**")
    toks = re.findall(r"\d+\.?\d*|sqrt|sin|cos|tan|AL|TH|pi|[A-Za-z]|\*\*|\S", py)
    res = []
    for t in toks:
        if res:
            p = res[-1]
            left = re.fullmatch(r"\d+\.?\d*|pi|AL|TH|[A-Za-z]|\)", p)
            right = re.fullmatch(r"\d+\.?\d*|sqrt|sin|cos|tan|pi|AL|TH|[A-Za-z]|\(", t)
            if left and right:
                res.append("*")
        res.append(t)
    return "".join(res)


def tex_val(tex, var=None):
    py = tex_to_py(tex)
    if var is None:
        return eval(py, dict(FUNCS))
    return lambda *v: eval(py, dict(FUNCS, **dict(zip(var, v))))


def tex_vec(tex, var):
    """'A\\tv{i}+B\\tv{j}' -> function returning (A, B)."""
    s = tex.strip()
    i = s.index("\\tv{i}")
    a, rest = s[:i], s[i + 6:]
    j = rest.index("\\tv{j}")
    b = rest[:j]
    if rest[j + 6:].strip() not in ("", "."):
        raise ValueError(f"trailing text after j component in {tex!r}")
    if not b.lstrip().startswith(("+", "-")):
        raise ValueError(f"no sign before j component in {tex!r}")
    fa, fb = tex_val(a or "0", var), tex_val(b, var)
    return lambda *v: (fa(*v), fb(*v))


def tex_dms(tex):
    m = re.fullmatch(r"(\d+)\^\\circ(\d+)'", tex.strip())
    if not m:
        raise ValueError(f"not degrees and minutes: {tex!r}")
    return int(m.group(1)) + int(m.group(2)) / 60


def deriv(f, x, h=1e-4):
    return (-f(x + 2 * h) + 8 * f(x + h) - 8 * f(x - h) + f(x - 2 * h)) / (12 * h)


def root(f, a, b):
    fa = f(a)
    for _ in range(200):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
    return (a + b) / 2


def simulate(r0, u, a, t, n=2000):
    """Velocity Verlet from r0 with velocity u under constant acceleration a, up to time t."""
    (x, y), (vx, vy), h = r0, u, t / n
    for _ in range(n):
        x, y = x + vx * h + a[0] * h * h / 2, y + vy * h + a[1] * h * h / 2
        vx, vy = vx + a[0] * h, vy + a[1] * h
    return (x, y), (vx, vy)


# ---------------------------------------------------------------- HTML blocks
ans = read("a_10a.html")
sec = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_10a.html")
if "{{ahead:Lesson 10A | Projectile motion: the time equations}}" not in sec[0].split('<div class="ans-sec">Textbook Homework</div>')[-1]:
    report(False, "answers heading", "{{ahead:Lesson 10A | ...}} missing before the past-paper section")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}

lesson = read("l10a.html")
pps = lesson.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l10a.html")
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}


def printed(pp, template):
    if pp not in PPA:
        raise LookupError(f"PP {pp} solution block missing")
    before, after = template.split("@")
    found = re.findall(re.escape(before) + r"(.+?)" + re.escape(after), PPA[pp], re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times: {template!r}")
    return found[0]


def check(pp, template, expected, mode="e", var=None, samples=((1.3,), (2.0,), (3.7,)), kind="num"):
    label = f"PP{pp} {template}"
    try:
        tex = printed(pp, template)
        if kind == "vec":
            got = tex_vec(tex, var)
            errs = [max(abs(g - e) / max(1, abs(e)) for g, e in zip(got(*v), expected(*v))) for v in samples]
            report(max(errs) < 1e-6, label, f"printed {tex} (vector function of {', '.join(var)})")
            return
        if kind == "dms":
            got = tex_dms(tex)
            report(round(expected * 60) == round(got * 60), label, f"printed {tex}, computed {expected:.4f} deg = {int(expected)} deg {round((expected % 1) * 60)}'")
            return
        if var:
            got = tex_val(tex, var)
            errs = [abs(got(*v) - expected(*v)) / max(1, abs(expected(*v))) for v in samples]
            report(max(errs) < 1e-6, label, f"printed {tex} (function of {', '.join(var)})")
            return
        got = tex_val(tex)
        if mode == "r":
            dec = len(tex.split(".")[1]) if "." in tex else 0
            ok = abs(got - expected) <= 0.5 * 10 ** -dec + 1e-12
        else:
            ok = abs(got - expected) <= 1e-6 * max(1, abs(expected))
        report(ok, label, f"printed {tex} = {got:.6g}, computed {expected:.6g}")
    except Exception as e:  # missing or unparsable value fails loudly
        report(False, label, f"ERROR {e}")


# ---------------------------------------------------------------- lesson structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "lesson marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    report(T == 5 * round(1.5 * M / 5), "lesson time", f"{T} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for n in PPQ:
        sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[n], re.S)]
        tot = int(re.search(r'<span class="mk">(\d+) marks?</span>', PPQ[n]).group(1))
        if sub:
            report(sum(sub) == tot, f"PP{n} part marks", f"parts {sub} sum {sum(sub)}, block {tot}")
        src_q = re.search(r"^(.*?)</span>", PPQ[n]).group(1)
        src_a = re.search(r"^(.*?)</span>", PPA.get(n, "")).group(1) if n in PPA else None
        report(src_q == src_a, f"PP{n} source label", src_q)
    report("\\tv{" in pps[1], "vector form", "at least one question written with \\tv{i}, \\tv{j}")
except Exception as e:
    report(False, "lesson structure", f"ERROR {e}")

# ---------------------------------------------------------------- PP 1  thrown horizontally at 50 from 90 m, symbolic g
def land_time(g):
    # y = 90 + 0 t - g t^2 / 2 (thrown horizontally), first t > 0 with y = 0
    return root(lambda t: 90 - g * t * t / 2, 0, 100)


GS = ((9.8,), (10.0,), (3.7,))
check(1, r"so \(t^2=@\) and", lambda g: land_time(g) ** 2, var=("g",), samples=GS)
check(1, r"and \(t=@=\sqrt{\dfrac{36", land_time, var=("g",), samples=GS)
check(1, r"\times5}{g}}=@\) seconds", land_time, var=("g",), samples=GS)
try:
    opts = dict(re.findall(r"<span>\(([A-D])\) \\\((.+?)\\\) seconds</span>", PPQ[1]))
    vals = {k: tex_val(v, ("g",))(9.8) for k, v in opts.items()}
    best = min(vals, key=lambda k: abs(vals[k] - land_time(9.8)))
    letter = printed(1, "<b>Answer (@).</b>")
    report(len(opts) == 4 and letter == best and abs(vals[best] - land_time(9.8)) < 1e-6, "PP1 MC letter", f"printed {letter}, option with value {land_time(9.8):.6g} (g = 9.8) is {best}")
except Exception as e:
    report(False, "PP1 MC letter", f"ERROR {e}")

# ---------------------------------------------------------------- PP 2  x = 30 sqrt3 t, y = 30 t - 5 t^2
x2 = lambda t: 30 * sqrt(3) * t
y2 = lambda t: 30 * t - 5 * t * t
vx0, vy0 = deriv(x2, 0), deriv(y2, 0)
check(2, r"\dfrac{30}{30\sqrt3}=@,\quad", vy0 / vx0)
check(2, r"\quad\theta=@^\circ.\]", degrees(atan2(vy0, vx0)))
check(2, r"+30^2=@\), so", vx0 ** 2 + vy0 ** 2)
check(2, r'nowrap">\(V=@\) m/s', hypot(vx0, vy0))

# ---------------------------------------------------------------- PP 3  30 m/s at alpha deg from 20 m, a = -10 j
AT = ((35.0, 0.7), (50.0, 1.9), (72.0, 3.3))     # (alpha in degrees, t)
u3 = lambda al: (30 * cos(radians(al)), 30 * sin(radians(al)))
check(3, r"\(\tv{u}=@\).", lambda al, t: u3(degrees(al)), var=("AL", "t"), samples=[(radians(a), t) for a, t in AT], kind="vec")
check(3, r"\[\tv{v}=@.\]", lambda al, t: simulate((0, 20), u3(degrees(al)), (0, -G), t)[1], var=("AL", "t"), samples=[(radians(a), t) for a, t in AT], kind="vec")
check(3, r"\[\tv{r}=@.\]", lambda al, t: simulate((0, 20), u3(degrees(al)), (0, -G), t)[0], var=("AL", "t"), samples=[(radians(a), t) for a, t in AT], kind="vec")

# ---------------------------------------------------------------- PP 4  r = 5 sqrt3 t i + 5(1 + t - t^2) j, pad 1 m high, ceiling 8 m
x4 = lambda t: 5 * sqrt(3) * t
y4 = lambda t: 5 * (1 + t - t * t)
# independent check that the given r matches 10 m/s at 30 deg from 5 m with g = 10
for tt in (0.4, 1.1):
    (sx, sy), _ = simulate((0, 5), (10 * cos(radians(30)), 10 * sin(radians(30))), (0, -G), tt)
    report(abs(sx - x4(tt)) < 1e-9 and abs(sy - y4(tt)) < 1e-9, f"PP4 given r at t={tt}", f"({x4(tt):.6g}, {y4(tt):.6g}) = simulated ({sx:.6g}, {sy:.6g})")
tl = root(lambda t: y4(t) - 1, 0.6, 5)
check(4, r"\[t=@\approx1.5247", tl)
check(4, r"\approx@,\]", tl, "r")
check(4, r"approximately @ seconds", tl, "r")
check(4, r"\times\dfrac{5+\sqrt{105}}{10}\approx@\). The pad", x4(tl), "r")
check(4, r"centred @ m from", x4(tl), "r")
check(4, r"At impact, \(1-2t=@\), so", 1 - 2 * tl)
check(4, r"so \(\dot y=@\). Then", deriv(y4, tl))
vi = hypot(deriv(x4, tl), deriv(y4, tl))
check(4, r"=75+105=@,\quad", vi ** 2)
check(4, r"\quad v=@\approx13.42", vi)
check(4, r"6\sqrt5\approx@.\]", vi, "r")
check(4, r"about @ m/s", vi, "r")
ttop = root(lambda t: deriv(y4, t), 0, 1.5)
check(4, r"so \(t=@\). Then", ttop)
check(4, r"=\dfrac{25}{4}=@\) m", y4(ttop))
check(4, r"\(8-6.25=@\) m", 8 - y4(ttop))

# ---------------------------------------------------------------- PP 5  from (0, 10); at t = 2 velocity 34 at alpha, tan alpha = 8/15, still rising
al5 = atan(8 / 15)
vxB, vyB = 34 * cos(al5), 34 * sin(al5)       # positive components: still rising
# y = 10 + (V sin th) t - 5 t^2 gives ydot = V sin th - 10 t; find V sin th from ydot(2) = vyB by root finding
ydd = deriv(lambda t: deriv(lambda s: -5 * s * s, t), 1.0)   # vertical acceleration of the given r
Vs = root(lambda k: (k + ydd * 2) - vyB, 0, 200)
Vc = vxB
check(5, r"So \(\sin\alpha=@\) and", sin(al5))
check(5, r"\(\cos\alpha=@\). The", cos(al5))
check(5, r"\dot x=34\times\dfrac{15}{17}=@,\qquad", vxB)
check(5, r"\dot y=34\times\dfrac{8}{17}=@.\]", vyB)
check(5, r"so \(V\sin\theta=@\).", Vs)
check(5, r"\tan\theta=\dfrac{36}{30}=@\), so", Vs / Vc)
check(5, r"so \(\theta\approx@\). Squaring", degrees(atan2(Vs, Vc)), kind="dms")
check(5, r"V^2=36^2+30^2=@,\quad", Vs ** 2 + Vc ** 2)
check(5, r"V=\sqrt{2196}=@\approx46.86", hypot(Vs, Vc))
check(5, r"6\sqrt{61}\approx@.\]", hypot(Vs, Vc), "r")
check(5, r"initial speed is \(6\sqrt{61}\approx@\) m", hypot(Vs, Vc), "r")
check(5, r"projection is about \(@\).</p>", degrees(atan2(Vs, Vc)), kind="dms")
# the explosion is before the maximum height (consistency of the question data)
report(vyB > 0 and Vs / G > 2, "PP5 B before maximum height", f"ydot(2) = {vyB:.6g} > 0, top at t = {Vs / G:.6g} s")

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
