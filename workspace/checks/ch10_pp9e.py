"""Numeric check of the Lesson 9E past-paper mini exam (Ch 10 pack).

For each item, the script finds the value printed in the past-paper worked
solutions of workspace/build/ch10/a_rev_9e.html (template with '@' marking the
value; the template must match exactly once in that PP block, otherwise the item
FAILS), converts the printed LaTeX to a number or to a function of the named
variable, and compares it with a value computed independently from the question
data (numerical derivatives, geometry). 'r' items are compared to the printed
precision, the others exactly (1e-9 relative). It also checks the lesson
fragment: the marks add to the total in the intro line, the time is 1.5 x marks
rounded to 5, and the MC letter matches the option with the computed value.

Exit status is 1 if anything fails. Run: python3 workspace/checks/ch10_pp9e.py
"""
import os
import re
import sys
from math import sqrt, pi, atan, hypot

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("CH10_SRC", os.path.join(HERE, "..", "build", "ch10"))   # override only for mutation tests
FAILS = []


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    print(("OK       " if ok else "MISMATCH ") + label + "  " + detail)
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- LaTeX -> Python
def _arg(s, i):
    """Return (argument, next index) for a TeX macro argument at s[i]."""
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
        elif s[i] == "\\":
            raise ValueError(f"unknown macro in {s!r}")
        elif s[i] in "{}":
            out.append("(" if s[i] == "{" else ")")
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def tex_to_py(tex):
    s = re.sub(r"\\left|\\right|\\,|\\!|\s", "", tex)
    py = _conv(s).replace("^", "**")
    toks = re.findall(r"\d+\.?\d*|sqrt|pi|[A-Za-z]|\*\*|\S", py)
    res = []
    for t in toks:
        if res:
            p = res[-1]
            left = re.fullmatch(r"\d+\.?\d*|pi|[A-Za-z]|\)", p)
            right = re.fullmatch(r"\d+\.?\d*|sqrt|pi|[A-Za-z]|\(", t)
            if left and right:
                res.append("*")
        res.append(t)
    return "".join(res)


def tex_val(tex, var=None):
    py = tex_to_py(tex)
    if var is None:
        return eval(py, {"sqrt": sqrt, "pi": pi})
    return lambda v: eval(py, {"sqrt": sqrt, "pi": pi, var: v})


def deriv(f, x, h=1e-3):
    """Five-point central difference."""
    return (-f(x + 2 * h) + 8 * f(x + h) - 8 * f(x - h) + f(x - 2 * h)) / (12 * h)


# ---------------------------------------------------------------- HTML blocks
ans = read("a_rev_9e.html")
sec = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_rev_9e.html")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}

lesson = read("l09e.html")
pps = lesson.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l09e.html")
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}


def printed(pp, template):
    if pp not in PPA:
        raise LookupError(f"PP {pp} solution block missing")
    before, after = template.split("@")
    found = re.findall(re.escape(before) + r"(.+?)" + re.escape(after), PPA[pp], re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times: {template!r}")
    return found[0]


def check(pp, template, expected, mode="e", var=None, samples=(1.3, 2.0, 3.7)):
    label = f"PP{pp} {template}"
    try:
        tex = printed(pp, template)
        if var:
            got = tex_val(tex, var)
            errs = [abs(got(v) - expected(v)) / max(1, abs(expected(v))) for v in samples]
            report(max(errs) < 1e-9, label, f"printed {tex} (function of {var})")
            return
        got = tex_val(tex)
        if mode == "r":
            dec = len(tex.split(".")[1]) if "." in tex else 0
            ok = abs(got - expected) <= 0.5 * 10 ** -dec + 1e-12
        else:
            ok = abs(got - expected) <= 1e-9 * max(1, abs(expected))
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
        src_q = re.search(r"^(.*?)</span>", PPQ[n]).group(1)
        src_a = re.search(r"^(.*?)</span>", PPA.get(n, "")).group(1) if n in PPA else None
        report(src_q == src_a, f"PP{n} source label", src_q)
except Exception as e:
    report(False, "lesson structure", f"ERROR {e}")

# ---------------------------------------------------------------- PP 1  balloon, dV/dt = 200 pi, r = 10
dr = 200 * pi / (4 * pi * 10 ** 2)
check(1, r"10^2}=@\) cm s", dr)
try:
    opts = dict(re.findall(r"<span>\(([A-D])\) ([\d.]+) cm s", PPQ[1]))
    best = min(opts, key=lambda k: abs(float(opts[k]) - dr))
    letter = printed(1, "<b>Answer (@).</b>")
    report(len(opts) == 4 and letter == best and abs(float(opts[best]) - dr) < 1e-9, "PP1 MC letter", f"printed {letter}, option with value {dr} is {best}")
except Exception as e:
    report(False, "PP1 MC letter", f"ERROR {e}")

# ---------------------------------------------------------------- PP 2  dr/dt = 2, r = 8
dA = deriv(lambda r: pi * r * r, 8) * 2
check(2, r"=2\pi\times8\times2=@.\]", dA)
check(2, r"increasing at \(@\) cm", dA)
check(2, r"(about @ cm", dA, "r")

# ---------------------------------------------------------------- PP 3  searchlight 6 m from path, 1.2 m/s, x = 8
theta = lambda x: atan(x / 6)
dth = deriv(theta, 8) * 1.2
check(3, r"\cos\theta=\dfrac{6}{10}=@\)", 6 / hypot(6, 8))
check(3, r"\times1.2=@=0.072", dth)
check(3, r"=\dfrac{9}{125}=@.\]", dth)
check(3, r"rotating at \(@\) radians", dth)

# ---------------------------------------------------------------- PP 4  cone radius 3, height 5, 1.5 L/min out, h = 1
Vh = lambda h: pi * (3 * h / 5) ** 2 * h / 3
dh = (-1.5 / 1000) / deriv(Vh, 1)
check(4, r"\right)^2h=@,\qquad", Vh, var="h")
check(4, r"\(\dfrac{dh}{dt}=@\approx", dh)
check(4, r"\approx@\). The water", dh, "r")
check(4, r"falling at \(@\approx", -dh)
check(4, r"falling at \(\dfrac{1}{240\pi}\approx@\) m/min", -dh, "r")
check(4, r"about @ mm per minute", -dh * 1000, "r")

# ---------------------------------------------------------------- PP 5  table radius 3, height 1, lamp h above table
def shadow_radius(h):
    # ray from the lamp (0, h + 1) through the table rim (3, 1), continued to the ground y = 0
    t = (h + 1) / h          # parameter along (3, -h) at which y reaches 0
    return 3 * t


A5 = lambda h: pi * shadow_radius(h) ** 2
check(5, r"\rho=\dfrac{3(h+1)}{h}=@.\]", shadow_radius, var="h")
check(5, r"\(A=\pi\rho^2=@\).", A5, var="h")
check(5, r"\times\dfrac43=@\)", deriv(A5, 3))
check(5, r"\times\left(-\dfrac{3}{100}\right)=@.\]", deriv(A5, 3) * (-3 / 100))
check(5, r"shadow is increasing at \(@\)", deriv(A5, 3) * (-3 / 100))

# ---------------------------------------------------------------- PP 6  cone height 2 in sphere radius R, dV/dt = 8, R = 2
r6 = lambda R: sqrt(R ** 2 - (2 - R) ** 2)        # rim point on the sphere, centre R below vertex
l6 = lambda R: hypot(r6(R), 2)
A6 = lambda R: pi * r6(R) * l6(R)
dRdt = 8 / deriv(lambda R: 4 / 3 * pi * R ** 3, 2)
check(6, r"\quad r^2=@.\]", lambda R: r6(R) ** 2, var="R")
check(6, r"l^2=r^2+2^2=@\)", lambda R: l6(R) ** 2, var="R")
check(6, r"=4\pi\sqrt{(R-1)R}=@.\]", A6, var="R", samples=(1.2, 2.0, 2.9))
check(6, r"\(\dfrac{dR}{dt}=\dfrac{8}{4\pi R^2}=@\)", lambda R: 8 / deriv(lambda s: 4 / 3 * pi * s ** 3, R), var="R")
check(6, r"\(R=2\), \(\dfrac{dR}{dt}=@\)", dRdt)
check(6, r"\dfrac{6\pi}{\sqrt2}=@\)", deriv(A6, 2))
check(6, r"\dfrac{1}{2\pi}=@.\]", deriv(A6, 2) * dRdt)
check(6, r"increasing at \(@\) units", deriv(A6, 2) * dRdt)

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
