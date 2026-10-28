"""Numeric check of the Lesson 10B past-paper mini exam (Ch 10 pack).

Same method as ch10_pp9e.py and ch10_pp10a.py. For each item, the script finds
the value printed in the past-paper worked solutions of
workspace/build/ch10/a_10b.html (template with '@' marking the value; the
template must match exactly once in that PP block, otherwise the item FAILS),
converts the printed LaTeX to a number or a function of the named variables,
and compares it with a value computed independently from the question data.
The independent values come from a step-by-step integration of the
acceleration (velocity Verlet, exact for constant acceleration), bisection
roots, numerical maximisation and brute-force angle scans. 'r' items are
compared to the printed precision, the others exactly (1e-6 relative). It also
checks the lesson fragment: the marks add to the total in the intro line
(15-22), the time is 1.5 x marks rounded to 5, the numbering, part marks and
source labels match, and the MC letter is the option with the computed value.

Exit status is 1 if anything fails. Run: python3 workspace/checks/ch10_pp10b.py
"""
import os
import random
import re
import sys
from math import sqrt, pi, atan, sin, cos, tan, radians, degrees

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


FUNCS = {"sqrt": sqrt, "pi": pi, "sin": sin, "cos": cos, "tan": tan, "sec": lambda z: 1 / cos(z)}
ANG = {"alpha": "AL", "theta": "TH"}


def tex_to_py(tex):
    s = re.sub(r"\\left|\\right|\\,|\\!|\s", "", tex)
    # \sec^2\alpha -> sec{AL}^2 ;  \sin2\theta -> sin{2*TH} ;  \cos\alpha^\circ -> cos{AL} (angles in radians here)
    s = re.sub(r"\\(sin|cos|tan|sec)\^(\d)\\(alpha|theta)(?:\^\\circ)?", lambda m: f"{m[1]}{{{ANG[m[3]]}}}^{m[2]}", s)
    s = re.sub(r"\\(sin|cos|tan|sec)(\d*)\\(alpha|theta)(?:\^\\circ)?",
               lambda m: f"{m[1]}{{{m[2] + '*' if m[2] else ''}{ANG[m[3]]}}}", s)
    py = _conv(s).replace("^", "**")
    toks = re.findall(r"\d+\.?\d*|sqrt|sin|cos|tan|sec|AL|TH|pi|[A-Za-z]|\*\*|\S", py)
    res = []
    for t in toks:
        if res:
            p = res[-1]
            left = re.fullmatch(r"\d+\.?\d*|pi|AL|TH|[A-Za-z]|\)", p)
            right = re.fullmatch(r"\d+\.?\d*|sqrt|sin|cos|tan|sec|pi|AL|TH|[A-Za-z]|\(", t)
            if left and right:
                res.append("*")
        res.append(t)
    return "".join(res)


def tex_val(tex, var=None):
    py = tex_to_py(tex)
    if var is None:
        return eval(py, dict(FUNCS))
    return lambda *v: eval(py, dict(FUNCS, **dict(zip(var, v))))


def tex_dms(tex):
    m = re.fullmatch(r"(\d+)\^\\circ(\d+)'", tex.strip())
    if not m:
        raise ValueError(f"not degrees and minutes: {tex!r}")
    return int(m.group(1)) + int(m.group(2)) / 60


def root(f, a, b):
    fa = f(a)
    if (fa > 0) == (f(b) > 0):
        raise ValueError("root not bracketed")
    for _ in range(200):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
    return (a + b) / 2


def simulate(r0, u, a, t, n=400):
    """Velocity Verlet from r0 with velocity u under constant acceleration a, up to time t."""
    (x, y), (vx, vy), h = r0, u, t / n
    for _ in range(n):
        x, y = x + vx * h + a[0] * h * h / 2, y + vy * h + a[1] * h * h / 2
        vx, vy = vx + a[0] * h, vy + a[1] * h
    return (x, y), (vx, vy)


def flight(r0, speed, ang, g):
    """Time of flight back to the launch height and the horizontal range, by root finding on the simulation."""
    u = (speed * cos(ang), speed * sin(ang))
    yv = lambda t: simulate(r0, u, (0, -g), t, 50)[0][1] - r0[1]
    tf = root(yv, 1e-6 * speed / g + 1e-9, 4 * speed / g)
    return tf, simulate(r0, u, (0, -g), tf, 50)[0][0] - r0[0]


def path_y(r0, speed, ang, g, x):
    """Height at horizontal distance x (time from the x motion, height from the simulation)."""
    return simulate(r0, (speed * cos(ang), speed * sin(ang)), (0, -g), x / (speed * cos(ang)))[0][1]


# ---------------------------------------------------------------- HTML blocks
ans = read("a_10b.html")
sec = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(sec) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_10b.html")
head_ok = sec[0].rstrip().endswith("{{ahead:Lesson 10B | Projectile motion: the equation of path}}")
report(head_ok and "{{ahead:Chapter 10 Review | Chapter review exercise}}" in sec[0], "answers heading",
       "{{ahead:Lesson 10B | ...}} directly before the past-paper section, after the Chapter 10 review answers")
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', sec[1], re.S)}

lesson = read("l10b.html")
pps = lesson.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l10b.html")
pps[1] = pps[1].split("<!-- ============ Chapter review ============ -->")[0]
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}


def printed(pp, template):
    if pp not in PPA:
        raise LookupError(f"PP {pp} solution block missing")
    before, after = template.split("@")
    found = re.findall(re.escape(before) + r"(.+?)" + re.escape(after), PPA[pp], re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times: {template!r}")
    return found[0]


def check(pp, template, expected, mode="e", var=None, samples=None, kind="num"):
    label = f"PP{pp} {template}".replace("\n", " ")
    try:
        tex = printed(pp, template)
        if kind == "dms":
            got = tex_dms(tex)
            report(round(expected * 60) == round(got * 60), label, f"printed {tex}, computed {expected:.4f} deg = {int(expected)} deg {round((expected % 1) * 60)}'")
            return
        if var:
            got = tex_val(tex, var)
            errs = [abs(got(*v) - expected(*v)) / max(1, abs(expected(*v))) for v in samples]
            report(max(errs) < 1e-6, label, f"printed {tex} (function of {', '.join(var)}, {len(samples)} samples, max rel err {max(errs):.1e})")
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
        report(PPQ[n].count('<div class="hint">') == 1 and "{{work:" in PPQ[n], f"PP{n} hint and work box", "one hint, one work box")
    report("Q13(d)(iii)" in PPQ[3] and "(i)" not in PPQ[3].replace("(iii)", ""), "PP3 only part (iii)",
           "NSG 2020 Q13(d)(i)-(ii) are used in 10A; only (iii) here, with r from (ii) given in the stem")
    report("30t\\sin\\alpha^\\circ-5t^2+20" in PPQ[3], "PP3 stem supplies r", "result of (ii) given")
except Exception as e:
    report(False, "lesson structure", f"ERROR {e}")

random.seed(10)

# ---------------------------------------------------------------- PP 1  path y = -3x^2 + 2x + 4, back to its starting height
y1 = lambda x: -3 * x * x + 2 * x + 4
d1 = root(lambda x: y1(x) - y1(0), 1e-6, 10)
check(1, r"so the original height is @. Put", y1(0))
check(1, r"(the start) or \(x=@\). It", d1)
try:
    opts = dict(re.findall(r"<span>\(([A-D])\) (.+?) units?</span>", PPQ[1]))
    vals = {k: tex_val(v.replace("\\(", "").replace("\\)", "")) for k, v in opts.items()}
    best = min(vals, key=lambda k: abs(vals[k] - d1))
    letter = printed(1, "<b>Answer (@).</b>")
    report(len(opts) == 4 and letter == best and abs(vals[best] - d1) < 1e-9, "PP1 MC letter", f"printed {letter}, option with value {d1:.6g} is {best}")
except Exception as e:
    report(False, "PP1 MC letter", f"ERROR {e}")

# ---------------------------------------------------------------- PP 2  x = Vt cos th, y = Vt sin th - g t^2 / 2 (symbolic g and V)
XTVG = [(random.uniform(0.1, 60), radians(random.uniform(5, 85)), random.uniform(5, 40), random.choice((9.8, 10.0, 3.7))) for _ in range(4)]
check(2, r"From \(x=Vt\cos\theta\), \(t=@\). Substituting", lambda x, th, V, g: root(lambda t: V * t * cos(th) - x, 0, 1e3), var=("x", "TH", "V", "g"), samples=XTVG)
check(2, r"{V\cos\theta}\right)^2=@.\]", lambda x, th, V, g: path_y((0, 0), V, th, g, x), var=("x", "TH", "V", "g"), samples=XTVG)
check(2, r"the cartesian equation is \(y=@\).</p>", lambda x, th, V, g: path_y((0, 0), V, th, g, x), var=("x", "TH", "V", "g"), samples=XTVG)
try:
    stem = re.search(r"cartesian equation of the path is given by \\\((.+?)\\\)\.</div>", PPQ[2]).group(1)
    report(stem == "y=" + printed(2, r"the cartesian equation is \(y=@\).</p>"), "PP2 result matches the question", stem)
except Exception as e:
    report(False, "PP2 result matches the question", f"ERROR {e}")

# ---------------------------------------------------------------- PP 3  30 m/s at alpha from 20 m, a = -10 j; target (90, 1)
y3 = lambda x, a: path_y((0, 20), 30, a, 10, x)
XA = [(random.uniform(0, 120), radians(random.uniform(5, 85))) for _ in range(4)]
check(3, r"{900\cos^2\alpha}+20=@.\]", y3, var=("x", "AL"), samples=XA)
check(3, r"\text{so}\quad@=0.\]", lambda a: 1 - y3(90, a), var=("AL",), samples=[(xa[1],) for xa in XA])
a_lo = root(lambda a: y3(90, a) - 1, radians(1), radians(45))
a_hi = root(lambda a: y3(90, a) - 1, radians(45), radians(89))
try:
    ex = printed(3, r"=\dfrac{90\pm\sqrt{3420}}{90}=@.\]")
    vals = sorted(tex_val(ex.replace("\\pm", s)) for s in "+-")
    ok = abs(vals[0] - tan(a_lo)) < 1e-6 and abs(vals[1] - tan(a_hi)) < 1e-6
    report(ok, "PP3 exact roots", f"printed {ex} = {vals[0]:.6g}, {vals[1]:.6g}; computed tan = {tan(a_lo):.6g}, {tan(a_hi):.6g}")
    ex = printed(3, r"\tan\alpha=\dfrac{90\pm\sqrt{@}}{90}")
    report(tex_val(ex) == 90 ** 2 - 4 * 45 * 26, "PP3 discriminant", f"printed {ex}, computed {90 ** 2 - 4 * 45 * 26}")
except Exception as e:
    report(False, "PP3 exact roots", f"ERROR {e}")
check(3, r"So \(\tan\alpha\approx@\) or", tan(a_lo), "r")
check(3, r"or \(\tan\alpha\approx@\), giving", tan(a_hi), "r")
check(3, r"giving \(\alpha\approx@\) or", degrees(a_lo), kind="dms")
check(3, r"or \(\alpha\approx@\).</p>", degrees(a_hi), kind="dms")
low = min(min(y3(90 * i / 200, a) for i in range(201)) for a in (a_lo, a_hi))
report(low > 0, "PP3 target reached in flight", f"lowest point of either path for 0 <= x <= 90 is {low:.4g} m > 0")

# ---------------------------------------------------------------- PP 4  x = Vt cos a, y = Vt sin a - 5t^2 (g = 10)
VA = [(random.uniform(5, 400), radians(random.uniform(5, 85))) for _ in range(4)]
check(4, r"the time of flight is \(t=@\). Substituting", lambda V, a: flight((0, 0), V, a, 10)[0], var=("V", "AL"), samples=VA)
check(4, r"\dfrac{V\sin\alpha}{5}=@=\dfrac{V^2\sin2", lambda V, a: flight((0, 0), V, a, 10)[1], var=("V", "AL"), samples=VA)
check(4, r"\cos\alpha}{5}=@.\]", lambda V, a: flight((0, 0), V, a, 10)[1], var=("V", "AL"), samples=VA)


def rmax(V):
    """Golden-section maximum of the simulated range over the angle; returns (angle in degrees, range)."""
    lo, hi, k = radians(1), radians(89), (sqrt(5) - 1) / 2
    for _ in range(80):
        m1, m2 = hi - k * (hi - lo), lo + k * (hi - lo)
        if flight((0, 0), V, m1, 10)[1] < flight((0, 0), V, m2, 10)[1]:
            lo = m1
        else:
            hi = m2
    return degrees((lo + hi) / 2), flight((0, 0), V, (lo + hi) / 2, 10)[1]


try:
    a_opt = rmax(50.0)[0]
    report(abs(a_opt - tex_val(printed(4, r"occurs when \(\alpha=@^\circ\), and"))) < 1e-3, "PP4 angle of maximum range", f"printed 45, numerical maximum at {a_opt:.5f} deg")
except Exception as e:
    report(False, "PP4 angle of maximum range", f"ERROR {e}")
check(4, r"R_{\max}=\dfrac{V^2\times1}{10}=@.\]", lambda V: rmax(V)[1], var=("V",), samples=[(20.0,), (137.0,)])
Vmin = root(lambda V: flight((0, 0), V, pi / 4, 10)[1] - 12000, 100, 1000)
check(4, r"so it must be within the maximum range: \(\dfrac{V^2}{10}\ge@\). Then", 12000)
check(4, r"Then \(V^2\ge@\), so", Vmin ** 2)
check(4, r"V\ge\sqrt{120\,000}=@\approx", Vmin)
check(4, r"\approx@&gt;343.\]", Vmin, "r")
report(Vmin > 343 and flight((0, 0), 343, pi / 4, 10)[1] < 12000, "PP4 343 m/s is too slow", f"minimum speed {Vmin:.6g} > 343; best range at 343 m/s is {flight((0, 0), 343, pi / 4, 10)[1]:.6g} m < 12000 m")

# ---------------------------------------------------------------- PP 5  r = Vt cos th i + (Vt sin th - g t^2/2) j, h = V^2/2g
G4 = 9.8
y4 = lambda x, th, h: path_y((0, 0), sqrt(2 * G4 * h), th, G4, x)
XTH = [(random.uniform(0.1, 30), radians(random.uniform(5, 85)), random.uniform(2, 40)) for _ in range(4)]
check(5, r"{2V^2\cos^2\theta}=@,\]", y4, var=("x", "TH", "h"), samples=XTH)
ABHT = [(random.uniform(0.5, 20), random.uniform(0, 10), random.uniform(2, 30), radians(random.uniform(5, 85))) for _ in range(4)]
check(5, r"rearranging,</p>" + "\n" + r"\[@=0.\]", lambda a, b, h, th: -4 * h * (y4(a, th, h) - b), var=("a", "b", "h", "TH"), samples=ABHT)
disc = lambda a, b, h: (-4 * h * a) ** 2 - 4 * a * a * (a * a + 4 * h * b)
check(5, r"positive:</p>" + "\n" + r"\[@&gt;0,\quad", disc, var=("a", "b", "h"), samples=[s[:3] for s in ABHT])
check(5, r"that is,}\quad@&gt;0.\]", disc, var=("a", "b", "h"), samples=[s[:3] for s in ABHT])
try:
    parts = printed(5, r"this gives \(a^2&lt;@\).</p>").split("=")
    errs = [abs(tex_val(p, ("h", "b"))(h, b) - 4 * h * (h - b)) for p in parts for _, b, h, _ in ABHT]
    report(len(parts) == 2 and max(errs) < 1e-9, "PP5 (ii) bound", f"printed {'='.join(parts)} = 4h(h-b)")
except Exception as e:
    report(False, "PP5 (ii) bound", f"ERROR {e}")


def angles_through(a, b, h, n=1500):
    """Brute force: angles in (0, 90) deg whose path passes through (a, b), from sign changes on a grid."""
    f = lambda th: a * tan(th) - a * a / (4 * h * cos(th) ** 2) - b      # path from the vector r(t), t = a / (V cos th)
    grid = [radians(90 * (i + 0.5) / n) for i in range(n)]
    return [root(f, p, q) for p, q in zip(grid, grid[1:]) if (f(p) > 0) != (f(q) > 0)]


bad, prod_err, n2 = 0, 0.0, 0
for _ in range(300):
    h, a, b = random.uniform(1, 20), random.uniform(0.2, 40), random.uniform(0, 20)
    roots = angles_through(a, b, h)
    if (len(roots) == 2) != (a * a < 4 * h * (h - b) - 1e-6) and abs(a * a - 4 * h * (h - b)) > 1e-3:
        bad += 1
    if len(roots) == 2:
        n2 += 1
        prod_err = max(prod_err, abs(tan(roots[0]) * tan(roots[1]) - tex_val(printed(5, r"\tan\theta_1\tan\theta_2=@=1+"), ("a", "b", "h"))(a, b, h)))
        if max(roots) < radians(45):
            bad += 1
report(bad == 0, "PP5 brute force", f"300 random (a, b, h): two angles exactly when a^2 < 4h(h-b); in {n2} two-angle cases the larger angle is never below 45 deg")
report(prod_err < 1e-6, "PP5 product of roots", f"printed product formula matches tan(th1)tan(th2) from the scan (max err {prod_err:.1e})")

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
