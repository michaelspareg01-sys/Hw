"""Numeric check of the Ch 10 answers, tied to the HTML fragments.

Part 1 (HTML-tied). For every numeric answer printed in the answer fragments
workspace/build/ch10/a_rev_9e.html, a_10a.html, a_10b.html (warm-up, lesson
examples C1-C3, textbook homework, chapter review) and in the lesson worked
examples (l09e.html, l10a.html, l10b.html), the script
  1. locates the answer block (fragment heading, answer section, answer number;
     or the lesson file and worked-example number),
  2. extracts the printed value(s) with a template in which '@' marks a value,
     (the template must match exactly once, otherwise the item FAILS),
  3. converts the printed LaTeX to a number (or to a function of the named
     variables, for answers such as x = 30t), and
  4. compares it with a value recomputed independently from the question's
     given data, to the printed precision ('r' items: half a unit in the last
     printed place, half a minute for d°m'; 'e' items: exact to 1e-9).
Printed functions are compared with the recomputed function at several sample
values of their variables.

Part 2 (identities). "Show that" results that have no printed answer are
checked as identities, using arbitrary values of V, g, theta etc. These are
NOT tied to the HTML and are counted separately.

Exit status is 1 if anything fails. Run: python3 workspace/checks/ch10_textbook.py
"""
import os
import re
import sys
from math import sqrt, pi, sin, cos, tan, atan, asin, acos, radians, degrees

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("CH10_SRC", os.path.join(HERE, "..", "build", "ch10"))   # override only for mutation tests
G = 10

# --------------------------------------------------------------------------
# HTML block extraction
# --------------------------------------------------------------------------
def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


ANS_RE = re.compile(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)</div></div>\s*(?=<div class="a">|<div class="ans-sec">|\{\{ahead:|@@|$)', re.S)


def answer_blocks():
    blocks = {}
    for name in ("a_rev_9e.html", "a_10a.html", "a_10b.html"):
        text = read(name)
        parts = re.split(r"\{\{ahead:([^|}]+)", text)
        for i in range(1, len(parts), 2):
            head, body = parts[i].strip(), parts[i + 1]
            secs = re.split(r'<div class="ans-sec">([^<]+)</div>', body)
            chunks = [(None, secs[0])] + [(secs[j].strip(), secs[j + 1]) for j in range(1, len(secs), 2)]
            for sec, chunk in chunks:
                for an, ab in ANS_RE.findall(chunk):
                    key = (head, sec, an.strip())
                    if key in blocks:
                        raise SystemExit(f"duplicate answer block {key}")
                    blocks[key] = ab
    return blocks


def worked_blocks():
    blocks = {}
    for lesson, name in (("9E", "l09e.html"), ("10A", "l10a.html"), ("10B", "l10b.html")):
        text = read(name)
        for chunk in re.split(r'(?=<div class="ex )|(?=<!-- =)', text):
            m = re.search(r'<span class="tag">Worked example (\d+)</span>', chunk)
            if m:
                blocks[(lesson, "WE", m.group(1))] = chunk
    return blocks


BLOCKS = answer_blocks()
BLOCKS.update(worked_blocks())


def block(key):
    head, sec, an = key[:3]
    if sec == "WE":
        return BLOCKS.get((head, sec, an))
    text = BLOCKS.get((head, sec, an))
    if text is None or len(key) == 3:
        return text
    i = text.find("<b>Your turn.</b>")
    if i < 0:
        return None
    return text[:i] if key[3] == "demo" else text[i:]


# --------------------------------------------------------------------------
# LaTeX -> Python
# --------------------------------------------------------------------------
KNOWN = {"sqrt", "pi", "cosd", "sind"}
NS = {"sqrt": sqrt, "pi": pi, "cosd": lambda d: cos(radians(d)), "sind": lambda d: sin(radians(d))}


def _arg(s, i):
    if s[i] == "{":
        depth, j = 0, i
        while True:
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    return s[i + 1:j], j + 1
            j += 1
    if s[i] == "\\":                                   # a command such as \pi as the argument
        m = re.match(r"\\[A-Za-z]+", s[i:])
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def _conv(s):
    out, i = "", 0
    while i < len(s):
        for cmd in ("\\dfrac", "\\tfrac", "\\frac"):
            if s.startswith(cmd, i):
                a, i = _arg(s, i + len(cmd))
                b, i = _arg(s, i)
                out += f"\x01(({_conv(a)})/({_conv(b)}))\x02"
                break
        else:
            if s.startswith("\\sqrt", i):
                a, i = _arg(s, i + 5)
                out += f"\x01sqrt({_conv(a)})\x02"
            elif s.startswith("\\pi", i):
                out += "\x01pi\x02"
                i += 3
            elif s.startswith("\\times", i):
                out += "*"
                i += 6
            elif s[i] == "^":
                a, i = _arg(s, i + 1)
                out += f"**({_conv(a)})"
            elif s[i] == "{":
                a, i = _arg(s, i)
                out += f"({_conv(a)})"
            elif s[i] == "\\":
                raise ValueError(f"unsupported LaTeX in {s!r}")
            else:
                out += s[i]
                i += 1
    return out


def to_python(tex):
    s = tex.strip()
    for a, b in (("\\left", ""), ("\\right", ""), ("\\,", ""), ("\\ ", ""), ("\\ell", "l"), (" ", "")):
        s = s.replace(a, b)
    s = re.sub(r"\\(cos|sin)(\d+)\^\\circ", lambda m: "\x01" + m.group(1) + "d(" + m.group(2) + ")\x02", s)
    e = _conv(s)
    e = re.sub(r"(?<=[\w)])\x01", "*", e).replace("\x01", "")
    e = re.sub(r"\x02(?=[\w(])", "*", e).replace("\x02", "")
    e = re.sub(r"(?<=\d)(?=[A-Za-z(])", "*", e)
    e = re.sub(r"(?<=\))(?=[\w(])", "*", e)
    # split runs of letters that are not known function names into single variables
    e = re.sub(r"[A-Za-z]+", lambda m: m.group(0) if m.group(0) in KNOWN else "*".join(m.group(0)), e)
    e = re.sub(r"\b([A-Za-z])\(", r"\1*(", e)          # single variable followed by (
    return e


ANGLE = re.compile(r"(-?)(\d+(?:\.\d+)?)\^\\circ(?:(\d+)')?$")


def parse(tex):
    """Return (value or function, tolerance-for-'r', variables)."""
    t = tex.strip()
    m = ANGLE.match(t)
    if m:
        sign = -1 if m.group(1) else 1
        if m.group(3) is not None:
            return sign * (float(m.group(2)) + int(m.group(3)) / 60), 0.5 / 60 + 1e-9, ()
        dec = m.group(2).split(".")
        return sign * float(m.group(2)), 0.5 * 10 ** -(len(dec[1]) if len(dec) > 1 else 0) + 1e-9, ()
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        dec = t.split(".")
        return float(t), 0.5 * 10 ** -(len(dec[1]) if len(dec) > 1 else 0) + 1e-9, ()
    e = to_python(t)
    names = sorted(set(re.findall(r"\b[A-Za-z]\b", e)) - KNOWN)
    if names:
        code = compile(e, tex, "eval")
        return (lambda env, code=code: eval(code, dict(NS), dict(env))), 0, tuple(names)
    return eval(e, dict(NS)), 0, ()


SAMPLES = [
    {"t": 0.37, "x": 0.41, "h": 1.3, "r": 2.2, "l": 3.1, "V": 7.3, "g": 9.7, "C": 11.0, "L": 23.0, "T": 0.6},
    {"t": 1.9, "x": -0.25, "h": 4.1, "r": 0.7, "l": 1.4, "V": 13.0, "g": 10.0, "C": 3.0, "L": 5.0, "T": 1.7},
    {"t": 3.3, "x": 0.83, "h": 0.6, "r": 5.0, "l": 9.0, "V": 21.0, "g": 9.8, "C": 40.0, "L": 900.0, "T": 3.1},
]

# --------------------------------------------------------------------------
# checking
# --------------------------------------------------------------------------
tied, ident = [], []


def tpl_regex(tpl):
    anchor_start = tpl.startswith("^")
    anchor_end = tpl.endswith("$")
    core = tpl[1 if anchor_start else 0: len(tpl) - (1 if anchor_end else 0)]
    pieces = core.split("@")
    rx = r"((?:(?!\\\(|\\\)|\\\[|\\\]).)+?)".join(re.escape(p) for p in pieces)
    return ("^" if anchor_start else "") + rx + ("$" if anchor_end else "")


def A(name, key, tpl, expected, kinds=None):
    """HTML-tied check. expected: value or tuple of values; a value may be a
    function env -> number for printed functions. kinds: string of 'e'/'r'."""
    if not isinstance(expected, tuple):
        expected = (expected,)
    kinds = kinds or "e" * len(expected)
    text = block(key)
    if text is None:
        tied.append(False)
        print(f"FAIL     {name}: answer block {key} not found")
        return
    found = list(re.finditer(tpl_regex(tpl), text, re.S))
    if len(found) != 1:
        tied.append(False)
        print(f"FAIL     {name}: template matched {len(found)} times in {key}: {tpl}")
        return
    caps = found[0].groups()
    if len(caps) != len(expected) or len(kinds) != len(expected):
        raise SystemExit(f"{name}: {len(caps)} captures, {len(expected)} expected values, kinds {kinds!r}")
    for cap, exp, kind in zip(caps, expected, kinds):
        label = f"{name} [{cap}]"
        try:
            val, rtol, names = parse(cap)
        except Exception as err:  # unparseable printed value
            tied.append(False)
            print(f"FAIL     {label}: cannot read printed value ({err})")
            continue
        if callable(exp) and not callable(val):         # printed constant for a function, e.g. xdot = 15sqrt3
            val = (lambda e, c=val: c)
            names = ()
        if callable(val) != callable(exp):
            tied.append(False)
            print(f"FAIL     {label}: printed {'function' if callable(val) else 'number'}, expected {'function' if callable(exp) else 'number'}")
            continue
        if callable(val):
            try:
                errs = [abs(val(s) - exp(s)) / max(1.0, abs(exp(s))) for s in SAMPLES]
                ok = max(errs) < 1e-9
                msg = f"function of ({','.join(names) or 'constant'}), max rel err {max(errs):.1e}"
            except Exception as err:
                ok, msg = False, f"cannot evaluate ({err})"
        else:
            tol = rtol if kind == "r" else 1e-9 * max(1.0, abs(exp))
            ok = abs(val - exp) <= tol
            msg = f"printed {val:.6g}, computed {exp:.6g}"
        tied.append(ok)
        print(f"{'OK      ' if ok else 'MISMATCH'} {label}: {msg}")


def I(name, lhs, rhs):
    """Identity check with arbitrary values (not tied to the HTML)."""
    ok = abs(lhs - rhs) <= 1e-9 * max(1.0, abs(rhs))
    ident.append(ok)
    print(f"{'OK      ' if ok else 'MISMATCH'} [identity] {name}: {lhs:.6g} vs {rhs:.6g}")


def roots(a, b, c):
    D = b * b - 4 * a * c
    return ((-b + sqrt(D)) / (2 * a), (-b - sqrt(D)) / (2 * a))


def simpson(f, a, b, n=200):
    h = (b - a) / n
    return h / 3 * (f(a) + f(b) + sum((4 if k % 2 else 2) * f(a + k * h) for k in range(1, n)))


def proj(V, ang_deg, g=G):
    """Time equations from the given launch data: (xdot, x, ydot, y) as env functions."""
    u, w = V * cos(radians(ang_deg)), V * sin(radians(ang_deg))
    return (lambda e: u, lambda e: u * e["t"], lambda e: w - g * e["t"], lambda e: w * e["t"] - g * e["t"] ** 2 / 2), u, w


def path(V, ang_deg, g=G):
    """Cartesian path recomputed by eliminating t numerically: y at x."""
    u, w = V * cos(radians(ang_deg)), V * sin(radians(ang_deg))
    return lambda e: w * (e["x"] / u) - g / 2 * (e["x"] / u) ** 2


def deriv(f, var):
    def d(e, f=f, var=var):
        hh = 1e-5
        e1, e2 = dict(e), dict(e)
        e1[var] += hh
        e2[var] -= hh
        return (f(e1) - f(e2)) / (2 * hh)
    return d


def fn(f):
    return lambda e: f(e)


# ==========================================================================
# Warm-up
# ==========================================================================
W = ("Chapter revision", None)
xw = lambda t: t * t - 6 * t + 5
A("W1a", W + ("1",), r"<b>a</b> \(v=@\), \(a=@\)",
  (deriv(lambda e: xw(e["t"]), "t"), 2))
tst = 6 / 2
A("W1b", W + ("1",), r"when \(t=@\), at \(x=@\)", (tst, xw(tst)))
dist = abs(xw(3) - xw(0)) + abs(xw(4) - xw(3))
A("W1c distance", W + ("1",), r"the distance is \(9+1=@\) m", dist)
A("W1c average velocity", W + ("1",), r"Average velocity \(=\dfrac{-3-5}{4}=@\) m/s", (xw(4) - xw(0)) / 4)
A("W1c average speed", W + ("1",), r"average speed \(=\dfrac{10}{4}=@\) m/s", dist / 4)
v2 = lambda t: 3 + simpson(lambda s: 6 * s - 4, 0, t)
A("W2 velocity and displacement", W + ("2",), r"^\(\dot x=@\), \(x=@\).",
  (lambda e: v2(e["t"]), lambda e: simpson(v2, 0, e["t"], 40)))
A("W2 discriminant", W + ("2",), r"\(\Delta=@<0\)", (-4) ** 2 - 4 * (6 / 2) * 3)
A("W3 velocity and displacement", W + ("3",), r"^\(\dot x=@\), \(x=@\).",
  (lambda e: 20 - G * e["t"], lambda e: 20 * e["t"] - G / 2 * e["t"] ** 2))
A("W3 greatest height", W + ("3",), r"Greatest height @ m when \(t=@\)", (20 ** 2 / (2 * G), 20 / G))
A("W3 landing", W + ("3",), r"ground when \(t=@\), with \(\dot x=@\), so the speed is @ m/s",
  (2 * 20 / G, 20 - G * 4, abs(20 - G * 4)))
A("W4", W + ("4",), r"\(40\cos30^\circ=@\), \(40\sin30^\circ=@\); \(\theta\doteq@\); \(\sqrt{36+64}=@\)",
  (40 * cos(radians(30)), 40 * sin(radians(30)), degrees(atan(3 / 4)), sqrt(6 ** 2 + 8 ** 2)), "eere")
A("W5", W + ("5",), r"=2\pi r\times3=@\) when", 2 * pi * 4 * 3)

# ==========================================================================
# Lesson 9E: examples
# ==========================================================================
L9 = ("Lesson 9E", "Lesson Examples")
A("9E C1 demo b", L9 + ("C1", "demo"), r"\(4\pi\times25\times2=@\) mm³/s", 4 * pi * 5 ** 2 * 2)
r3 = 36 * pi / (4 / 3 * pi)
A("9E C1 demo c", L9 + ("C1", "demo"), r"gives \(r^3=@\), \(r=@\); then", (r3, r3 ** (1 / 3)))
A("9E C1 demo c rate", L9 + ("C1", "demo"), r"so \(\dfrac{dr}{dt}=@\) mm/s", 72 * pi / (4 * pi * r3 ** (2 / 3)))
A("9E C1 turn", L9 + ("C1", "turn"), r"\(\dfrac{dA}{dt}=2x\times0.2=@\). <b>a</b> @ m²/s",
  (lambda e: 2 * e["x"] * 0.2, 2 * 4 * 0.2))
A("9E C1 turn b", L9 + ("C1", "turn"), r"so \(x=@\) m.", 2 / (2 * 0.2))
A("9E C2 demo a", L9 + ("C2", "demo"), r"\(V=\tfrac13\pi\left(\tfrac12h\right)^2h=@\) &nbsp;",
  lambda e: pi / 3 * (e["h"] / 2) ** 2 * e["h"])
A("9E C2 demo b", L9 + ("C2", "demo"), r"and \(\dfrac{dh}{dt}=@\doteq@\) cm/s",
  (12 / (pi / 4 * 4 ** 2), 12 / (pi / 4 * 4 ** 2)), "er")
A("9E C2 turn", L9 + ("C2", "turn"), r"the depth increases at @ cm/s", 9 * pi / (pi * 3 ** 2))
d3 = (sin(pi / 6) ** 2 / 2) * 600
A("9E C3 demo b", L9 + ("C3", "demo"), r"300\sin^2\theta=@\) radians per hour", d3)
A("9E C3 demo b deg", L9 + ("C3", "demo"), r"\div3600\doteq@^\circ\) per second", d3 * 180 / pi / 3600, "r")
d3t = sin(radians(30)) ** 2 / 80 * 4
A("9E C3 turn", L9 + ("C3", "turn"), r"=\dfrac{\sin^2\theta}{20}=@\doteq@\) rad/s \(\doteq@^\circ\) per second",
  (d3t, d3t, degrees(d3t)), "err")
WE9 = ("9E", "WE")
rr = (18 / (2 * pi / 3)) ** (1 / 3)
A("9E WE1 b", WE9 + ("1",), r"=2\pi\times36\times3=@\ \text{mm}^3", 2 * pi * 6 ** 2 * 3)
A("9E WE1 c r", WE9 + ("1",), r"and \(r=@\).</p>", rr)
A("9E WE1 c rate", WE9 + ("1",), r"\dfrac{dr}{dt}=@\ \text{mm/s}\doteq@\ \text{mm/s}",
  (90 / (2 * pi * rr ** 2), 90 / (2 * pi * rr ** 2)), "er")
A("9E WE2", WE9 + ("2",), r"\times0.3=@\ \text{m/s}", -3 / sqrt(5 ** 2 - 3 ** 2) * 0.3)
c2 = (120 / sqrt(120 ** 2 + 50 ** 2)) ** 2
A("9E WE3", WE9 + ("3",), r"\times\dfrac{1}{24}=@.\]", c2 / 120 * 5)
A("9E WE3 dec", WE9 + ("3",), r"increasing at \(\dfrac{6}{169}\doteq@\) radians", c2 / 120 * 5, "r")
A("9E WE3 deg", WE9 + ("3",), r"\dfrac{180}{\pi}\doteq@^\circ\) per second", degrees(c2 / 120 * 5), "r")

# ==========================================================================
# Exercise 9E
# ==========================================================================
H9 = ("Lesson 9E", "Textbook Homework")
A("9E Q1", H9 + ("1",), r"<b>b</b> @ m²/s &nbsp; <b>c</b> @ metres &nbsp; <b>d</b> @ m²",
  (0.2 * 5, 1.4 / 0.2, (0.6 / 0.2) ** 2))
A("9E Q2a", H9 + ("2",), r"\(A=@\)", lambda e: (e["l"] / sqrt(2)) ** 2)
A("9E Q2c,d", H9 + ("2",), r"(i) @ m²/s (ii) @ m²/s &nbsp; <b>d</b> @ metres",
  (10 / 2, sqrt(2 * 18) / 2, 17 * 2))
A("9E Q3", H9 + ("3",), r"<b>a</b> @ m³/s &nbsp; <b>b</b> @ m²/s",
  (4 * pi * 2 ** 2 * 0.3, 8 * pi * 4 * 0.3), "rr")
r4 = sqrt(200 / (4 * pi * 0.5))
A("9E Q4", H9 + ("4",), r"<b>b</b> \(@\) cm/s &nbsp; <b>c</b> \(r=@\) cm, \(V=@\) cm³",
  (200 / (4 * pi * 15 ** 2), r4, 4 / 3 * pi * r4 ** 3))
A("9E Q5a", H9 + ("5",), r"(2r)=@\), which", lambda e: pi / 3 * e["r"] ** 2 * (2 * e["r"]))
A("9E Q5b", H9 + ("5",), r"<b>b</b> \(@\) cm/s", 5 / (2 * pi * (10 / 2) ** 2))
th6 = pi / 3
d6 = 650 / (1.5 / sin(th6) ** 2)
A("9E Q6", H9 + ("6",), r"<b>b</b> @ radians per hour, about @ degrees", (d6, d6 * 180 / pi / 3600), "er")
d7 = 50 * sin(radians(15)) ** 2 / 100
A("9E Q7", H9 + ("7",), r"\doteq@\) radians per minute, about @ degrees", (d7, degrees(d7)), "rr")
A("9E Q8a", H9 + ("8",), r"<b>a</b> \(V=@\) cm³", lambda e: 0.5 * (2 * e["h"]) * e["h"] * 100 * e["x"])
A("9E Q8b loss", H9 + ("8",), r"\(0.1\times200xh=@\) cm³",
  lambda e: 0.1 * (2 * e["h"]) * (100 * e["x"]))
hh8, xx8 = 7.0, 3.0
A("9E Q8b rate", H9 + ("8",), r"at a constant @ cm/day",
  0.1 * (2 * hh8) * (100 * xx8) / (100 * 2 * hh8 * xx8))
A("9E Q10a", H9 + ("10",), r"<b>a</b> \(\dfrac{dx}{dt}=@\)",
  lambda e: -2 * sin(acos(e["x"])))
A("9E Q10b", H9 + ("10",), r"<b>b</b> \(@\) m/s.", -2 * sin(acos(0)))


def acc11(e):
    T = e["L"] / e["V"]
    return 2 * (e["C"] + e["L"] - e["V"] * T) / T ** 2


A("9E Q11a", H9 + ("11",), r"<b>a</b> \(@\) m/s²", acc11)
L11 = 2 * 50 / (100 / 90 - 1)
A("9E Q11d", H9 + ("11",), r"<b>d</b> @ metres", L11 + 50)
th12 = acos(1 / 2)
A("9E Q12d", H9 + ("12",), r"<b>d</b> @$",
  2 ** 2 * (1 - cos(2 * th12)) * (-1 / sqrt(2 ** 2 - 1)) * (-sqrt(3)))
xq = 100 * tan(pi / 6) / (tan(pi / 4) - tan(pi / 6))
ad, bd = 5 / 36 * (sqrt(3) - 1), 5 / 18 * (sqrt(3) - 1)
dxdt = (ad * (xq + 100) / cos(pi / 6) ** 2 - bd * xq / cos(pi / 4) ** 2) / (tan(pi / 4) - tan(pi / 6))
A("9E Q13", H9 + ("13",), r"\(x=h=@\) metres &nbsp; <b>d</b> \(\dfrac{dx}{dt}=@\) m/s, so the speed is @ km/h",
  (xq, dxdt, abs(dxdt) * 3.6))

# ==========================================================================
# Lesson 10A: examples
# ==========================================================================
L10 = ("Lesson 10A", "Lesson Examples")
A("10A C1 demo a", L10 + ("C1", "demo"), r"(i) \(\tv{v}=@\tv{i}+@\tv{j}\) (ii) \(\tv{v}=@\tv{i}-@\tv{j}\)",
  (20 * cos(radians(30)), 20 * sin(radians(30)), 20 * cos(radians(45)), 20 * sin(radians(45))))
A("10A C1 demo b", L10 + ("C1", "demo"),
  r"(i) \(v=@\) m/s, \(\theta=\tan^{-1}@\doteq@\) (ii) \(v=@\) m/s, \(\theta=-\tan^{-1}@\doteq@\)",
  (sqrt(6 ** 2 + 8 ** 2), 8 / 6, degrees(atan(8 / 6)), sqrt(12 ** 2 + 5 ** 2), 5 / 12, degrees(atan(-5 / 12))), "eereer")
A("10A C1 turn a", L10 + ("C1", "turn"), r"(i) \(@\tv{i}+@\tv{j}\) (ii) \(@\tv{i}-@\tv{j}\)",
  (16 * cos(radians(60)), 16 * sin(radians(60)), 16 * cos(radians(30)), 16 * sin(radians(30))))
A("10A C1 turn b", L10 + ("C1", "turn"), r"(i) @ m/s at \(\tan^{-1}@\doteq@\) (ii) \(@\) m/s at \(@\)",
  (sqrt(5 ** 2 + 12 ** 2), 12 / 5, degrees(atan(12 / 5)), sqrt(7 ** 2 + 7 ** 2), degrees(atan(-7 / 7))), "eerer")
(fx, fX, fy, fY), u, w = proj(30, 30)
A("10A C2 demo a", L10 + ("C2", "demo"), r"\(\dot x=@\), \(x=@\); \(\ddot y=-10\), \(\dot y=@\), \(y=@\).", (fx, fX, fy, fY))
A("10A C2 demo b", L10 + ("C2", "demo"), r"at \(t=@\) s, height @ m above", (w / G, w ** 2 / (2 * G)))
t = max(roots(-G / 2, w, 20))
vy = w - G * t
A("10A C2 demo c", L10 + ("C2", "demo"), r"so \(t=@\) s. Range \(@\doteq@\) m.", (t, u * t, u * t), "eer")
A("10A C2 demo c impact", L10 + ("C2", "demo"),
  r"\(\dot y=@\), so \(v=\sqrt{1300}=@\doteq@\) m/s at \(\tan^{-1}\dfrac{25}{15\sqrt3}\doteq@\) below",
  (vy, sqrt(u * u + vy * vy), sqrt(u * u + vy * vy), degrees(atan(-vy / u))), "eerr")
(fx, fX, fy, fY), u, w = proj(20, 30)
A("10A C2 turn", L10 + ("C2", "turn"),
  r"\(\dot x=@\), \(x=@\), \(\dot y=@\), \(y=@\). Greatest height @ m (at \(t=@\)); flight time @ s; range \(@\doteq@\) m.",
  (fx, fX, fy, fY, w * w / (2 * G), w / G, 2 * w / G, u * 2 * w / G, u * 2 * w / G), "eeeeeeeer")
# target (200, 40) at 50 m/s: (g x^2 / 2V^2) T^2 - x T + (y + g x^2 / 2V^2) = 0
k = G * 200 ** 2 / (2 * 50 ** 2)
Ta, Tb = sorted(roots(k, -200, 40 + k))
A("10A C3 demo a", L10 + ("C3", "demo"), r"\(\tan\alpha=@\) or \(@\): \(\alpha=@\) or \(\alpha\doteq@\)",
  (Ta, Tb, degrees(atan(Ta)), degrees(atan(Tb))), "eeer")
A("10A C3 demo b", L10 + ("C3", "demo"), r"\(t=@\doteq@\) s, or \(t=@\doteq@\) s.",
  (200 / (50 * cos(atan(Ta))), 200 / (50 * cos(atan(Ta))), 200 / (50 * cos(atan(Tb))), 200 / (50 * cos(atan(Tb)))), "erer")
k = G * 80 ** 2 / (2 * 40 ** 2)
Ta, Tb = sorted(roots(k, -80, 40 + k))
A("10A C3 turn", L10 + ("C3", "turn"), r"so \(\alpha=@\) or \(\tan^{-1}@\doteq@\).",
  (degrees(atan(Ta)), Tb, degrees(atan(Tb))), "eer")
WE10 = ("10A", "WE")
A("10A WE1 a(i)", WE10 + ("1",), r"(i) \(\dot x=12\cos60^\circ=@\) m/s and \(\dot y=12\sin60^\circ=@\) m/s",
  (12 * cos(radians(60)), 12 * sin(radians(60))))
A("10A WE1 a(ii)", WE10 + ("1",), r"(ii) \(\dot x=12\cos60^\circ=@\) m/s and \(\dot y=-12\sin60^\circ=@\) m/s",
  (12 * cos(radians(-60)), 12 * sin(radians(-60))))
A("10A WE1 b(i)", WE10 + ("1",), r"so \(v=@\) m/s, and \(\tan\theta=\tfrac34\), so \(\theta\doteq@\)",
  (sqrt(4 ** 2 + 3 ** 2), degrees(atan(3 / 4))), "er")
A("10A WE1 b(ii)", WE10 + ("1",), r"so \(v=@\) m/s, and \(\tan\theta=-\tfrac25\), so \(\theta\doteq@\)",
  (sqrt(5 ** 2 + 2 ** 2), degrees(atan(-2 / 5))), "er")
(fx, fX, fy, fY), u, w = proj(40, 30)
A("10A WE2 b", WE10 + ("2",),
  r"From (5), \(t=@\) seconds. From (6), \(y=-20+40=@\) metres above the stand, and from (3), \(x=@\) metres",
  (w / G, w * w / (2 * G), u * w / G))
A("10A WE2 b speed", WE10 + ("2",), r"the speed is \(\dot x=@\) m/s", u)
t = max(roots(-G / 2, w, 25))
vy = w - G * t
A("10A WE2 c", WE10 + ("2",), r"and \(t=@\) (\(t=-1\)", t)
A("10A WE2 c range", WE10 + ("2",), r"the horizontal range is \(x=@\) metres", u * t)
A("10A WE2 c speed", WE10 + ("2",), r"the impact speed is \(v=@\) m/s", sqrt(u * u + vy * vy))
A("10A WE2 c angle", WE10 + ("2",), r"so \(\theta\doteq@\): the impact", degrees(atan(vy / u)), "r")
k = G * 2000 ** 2 / (2 * 200 ** 2)
Ta, Tb = sorted(roots(k, -2000, 1000 + k))
A("10A WE3 a", WE10 + ("3",), r"\(\alpha=45^\circ\) or \(\tan^{-1}3\doteq@\).</p>", degrees(atan(Tb)), "r")
A("10A WE3 a low", WE10 + ("3",), r"giving \(\tan\alpha=1\) or 3, and \(\alpha=@\) or", degrees(atan(Ta)))
aOF = degrees(atan(1000 / 2000))
A("10A WE3 b", WE10 + ("3",),
  r"\(\tan^{-1}\tfrac12\doteq@\) to the horizontal, so the \(45^\circ\) shot is inclined at \(@\) to \(OF\), and the \(71^\circ34'\) shot is inclined at \(@\) to the vertical",
  (aOF, degrees(atan(Ta)) - aOF, 90 - degrees(atan(Tb))), "rrr")
for T, lab in ((Ta, "45"), (Tb, "tan3")):
    a = atan(T)
    tF = 2000 / (200 * cos(a))
    vxF, vyF = 200 * cos(a), 200 * sin(a) - G * tF
    if lab == "45":
        A("10A WE3 c flight 45", WE10 + ("3",), r"\(t=\dfrac{10}{\cos45^\circ}=@\) seconds", tF)
        A("10A WE3 c vy 45", WE10 + ("3",), r"+200\times\tfrac{1}{\sqrt2}=@\), so", vyF)
        A("10A WE3 c speed 45", WE10 + ("3",), r"<b>horizontally</b> at \(@\) m/s", vxF)
    else:
        A("10A WE3 c flight tan3", WE10 + ("3",), r"so \(t=\dfrac{10}{\cos\alpha}=@\) seconds", tF)
        A("10A WE3 c components", WE10 + ("3",), r"+60\sqrt{10}=@\), and from (2), \(\dot x=@\).", (vyF, vxF))
        A("10A WE3 c speed", WE10 + ("3",), r"so \(v=@\) m/s. Also \(\tan\theta=\dfrac{\dot y}{\dot x}=@\), so \(\theta=-\tan^{-1}2\doteq@\).",
          (sqrt(vxF ** 2 + vyF ** 2), vyF / vxF, degrees(atan(vyF / vxF))), "eer")

# ==========================================================================
# Exercise 10A
# ==========================================================================
H10 = ("Lesson 10A", "Textbook Homework")
(fx, fX, fy, fY), u, w = proj(30 * sqrt(2), 45)
A("10A Q1", H10 + ("1",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> \(t=@\) seconds &nbsp; <b>d</b> @ m &nbsp; <b>e</b> \(t=@\) seconds &nbsp; <b>f</b> @ m",
  (fX, fY, 2 * w / G, u * 2 * w / G, w / G, w * w / (2 * G)))
(fx, fX, fy, fY), u, w = proj(40, 30)
A("10A Q2", H10 + ("2",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> (i) \(t=@\) seconds (ii) \(@\) m (iii) @ m",
  (fX, fY, 2 * w / G, u * 2 * w / G, w * w / (2 * G)))
(fx, fX, fy, fY), u, w = proj(20, 60)
e1 = {"t": 1}
A("10A Q3", H10 + ("3",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> (i) @ m (ii) @ m/s",
  (fX, fY, sqrt(fX(e1) ** 2 + fY(e1) ** 2), sqrt(fx(e1) ** 2 + fy(e1) ** 2)), "eerr")
(fx, fX, fy, fY), u, w = proj(60, degrees(atan(4 / 3)))
e3 = {"t": 3}
A("10A Q4", H10 + ("4",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> @ m",
  (fX, fY, sqrt(fX(e3) ** 2 + fY(e3) ** 2)), "eer")


def vec_answers(name, key, ux, uy):
    ttop = uy / G
    A(name, key, r"<b>a</b> \(\tv{v}=@\tv{i}+@\tv{j}\) &nbsp; <b>b</b> \(\tv{r}=@\tv{i}+@\tv{j}\)",
      (lambda e: ux, lambda e: uy - G * e["t"], lambda e: ux * e["t"], lambda e: uy * e["t"] - G / 2 * e["t"] ** 2))
    return ttop


ttop = vec_answers("10A Q5a,b", H10 + ("5",), 8, 6)
A("10A Q5c", H10 + ("5",), r"(i) @ m/s (ii) \(@\tv{i}-@\tv{j}\) (iii) \(@\tv{i}+@\tv{j}\)",
  (sqrt(8 ** 2 + 6 ** 2), 8 * 2, -(6 * 2 - 5 * 4), 8 * ttop, 6 * ttop - 5 * ttop ** 2))
A("10A Q6a", H10 + ("6",), r"\(\dot x=@\), \(\dot y=@\)",
  (deriv(lambda e: 40 * e["t"], "t")({"t": 0}), deriv(lambda e: -5 * e["t"] ** 2 + 25 * e["t"], "t")({"t": 0})))
A("10A Q7", H10 + ("7",), r"<b>a</b> \(\tv{v}=@\tv{i}+@\tv{j}\) &nbsp; <b>b</b> \(@\tv{i}+@\tv{j}\)",
  (8 / 2, (-12 + 5 * 4) / 2, 4 * 0.5, 4 * 0.5 - 5 * 0.25))
(fx, fX, fy, fY), u, w = proj(12, -30)
t9 = max(roots(-5, w, 11))
A("10A Q9", H10 + ("9",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> @ second &nbsp; <b>d</b> @ m",
  (fX, fY, t9, u * t9), "eeer")
(fx, fX, fy, fY), u, w = proj(6, 45)
t10 = max(roots(-5, w, 2))
A("10A Q10", H10 + ("10",), r"<b>a</b> @ seconds &nbsp; <b>b</b> @ m", (t10, u * t10), "rr")
a11 = radians(36)
A("10A Q11", H10 + ("11",), r"^@ m/s", sqrt(5 * 20 ** 2 / (cos(a11) ** 2 * (20 * tan(a11) - 10))), "r")
tc = 2 * 60 / (60 - 20)
A("10A Q13", H10 + ("13",), r"collide @ second after \(P_2\) is projected (at \(@\tv{i}+@\tv{j}\))",
  (tc - 2, 20 * tc, 30 * tc - 5 * tc ** 2))
k = G * 20 ** 2 / (2 * (20 * sqrt(2)) ** 2)
Ta, Tb = sorted(roots(k, -20, 15 + k))
A("10A Q14c", H10 + ("14",), r"\(\theta=@\) or \(\theta\doteq@\)", (degrees(atan(Ta)), degrees(atan(Tb))), "er")
k = G * 100 ** 2 / (2 * 50 ** 2)
Ta, Tb = sorted(roots(k, -100, 25 + k))
res15 = []
for T in (Ta, Tb):
    a = atan(T)
    tP = 100 / (50 * cos(a))
    vx, vy = 50 * cos(a), 50 * sin(a) - G * tP
    res15.append((tP, sqrt(vx * vx + vy * vy), -degrees(atan(vy / vx))))
I("10A Q15 both speeds equal", res15[0][1], res15[1][1])
A("10A Q15b", H10 + ("15",), r"(i) \(@\) s and \(@\) s (ii) \(@\doteq@\) m/s in both cases, at angles of \(@\) and \(@\) (below)",
  (res15[0][0], res15[1][0], res15[0][1], res15[0][1], res15[0][2], res15[1][2]), "eeerer")
# Q18c: speed ratio at h/2 and h is sqrt5 : sqrt2 -> 1 + tan^2/2 = 5/2
A("10A Q18c", H10 + ("18",), r"\(\theta=@\)", degrees(atan(sqrt(2 * (5 / 2 - 1)))))

# ==========================================================================
# Lesson 10B: examples
# ==========================================================================
LB = ("Lesson 10B", "Lesson Examples")
pB = lambda e: -5 * (e["x"] / 30) ** 2 + 40 * (e["x"] / 30)
R = max(roots(-5 / 900, 40 / 30, 0))
A("10B C1 demo", LB + ("C1", "demo"),
  r"so \(y=@\). &nbsp; <b>b</b> \(y=0\) gives the range \(x=@\) m; the greatest height is at \(x=@\): \(y=@\) m.",
  (pB, R, R / 2, pB({"x": R / 2})))
A("10B C1 demo c", LB + ("C1", "demo"), r"\(\dfrac{dy}{dx}=@\), which", fn(lambda e: -2 * 5 * e["x"] / 900 + 40 / 30))
A("10B C1 demo c angle", LB + ("C1", "demo"), r"the angle of projection is \(\tan^{-1}\tfrac43\doteq@\)", degrees(atan(40 / 30)), "r")
pT = lambda e: -5 * (e["x"] / 20) ** 2 + 15 * (e["x"] / 20)
R = max(roots(-5 / 400, 15 / 20, 0))
A("10B C1 turn", LB + ("C1", "turn"),
  r"\(y=@\). Range @ m, greatest height @ m (at \(x=@\)), angle of projection \(\tan^{-1}\tfrac34\doteq@\)",
  (pT, R, pT({"x": R / 2}), R / 2, degrees(atan(15 / 20))), "eeeer")
s2 = 45 * G / 30 ** 2
A("10B C2 demo", LB + ("C2", "demo"), r"so \(\sin2\alpha=@\), \(2\alpha", s2)
A("10B C2 demo angles", LB + ("C2", "demo"), r"and \(\alpha=@\) or \(@\). The maximum range is \(\dfrac{V^2}{g}=@\) m.",
  (degrees(asin(s2)) / 2, 90 - degrees(asin(s2)) / 2, 30 ** 2 / G))
s2 = 20 * sqrt(3) * G / 20 ** 2
a1, a2 = degrees(asin(s2)) / 2, 90 - degrees(asin(s2)) / 2
A("10B C2 turn", LB + ("C2", "turn"),
  r"\(\sin2\alpha=@\), so \(\alpha=@\) or \(@\). Greatest heights \(\dfrac{V^2\sin^2\alpha}{2g}\): @ m and @ m.",
  (s2, a1, a2, (20 * sin(radians(a1))) ** 2 / (2 * G), (20 * sin(radians(a2))) ** 2 / (2 * G)))
A("10B C3 demo a", LB + ("C3", "demo"), r"=\dfrac{10}{800}=@\).", G / (2 * 20 ** 2))
k = G * 20 ** 2 / (2 * 20 ** 2)
Ta, Tb = sorted(roots(k, -20, 5 + k))
A("10B C3 demo b", LB + ("C3", "demo"), r"\(T=2\pm\sqrt2\): \(\alpha\doteq@\) or \(@\).",
  (degrees(atan(Tb)), degrees(atan(Ta))), "rr")
k = G * 40 ** 2 / (2 * 20 ** 2)
A("10B C3 demo c", LB + ("C3", "demo"), r"with \(\Delta=@<0\)", (40 ** 2 - 4 * k * (10 + k)) / 10 ** 2)
k = G * 30 ** 2 / (2 * 30 ** 2)
Ta, Tb = sorted(roots(k, -30, 10 + k))
A("10B C3 turn", LB + ("C3", "turn"), r"\(T=3\pm\sqrt6\): \(\alpha\doteq@\) or \(@\).",
  (degrees(atan(Tb)), degrees(atan(Ta))), "rr")
WEB = ("10B", "WE")
p1 = path(20, 60)
A("10B WE1 a", WEB + ("1",), r"\times\dfrac{x}{10}=@.\]", p1)
R1 = 2 * 20 ** 2 * sin(radians(60)) * cos(radians(60)) / G
A("10B WE1 b", WEB + ("1",), r"or \(x=@\). The range is \(20\sqrt3\doteq@\) m.", (R1, R1), "er")
A("10B WE1 c", WEB + ("1",), r"Differentiating, \(\dfrac{dy}{dx}=@\).</p>", deriv(p1, "x"))
sl = deriv(p1, "x")({"x": 15 * sqrt(3)})
A("10B WE1 c slope", WEB + ("1",), r"+\sqrt3=@\).</p>", sl)
A("10B WE1 c angle", WEB + ("1",), r"\(\theta\doteq@\). The ball", degrees(atan(sl)), "r")

# ==========================================================================
# Exercise 10B
# ==========================================================================
HB = ("Lesson 10B", "Textbook Homework")
y1 = lambda x: -5 / 324 * x * x + 4 / 3 * x
r1, r2 = sorted(roots(5 / 324, -4 / 3, 19))
A("10B Q1", HB + ("1",), r"<b>a</b> @ m &nbsp; <b>b</b> @ m or @ m &nbsp; <b>c</b> \(\dfrac{dy}{dx}=@\)",
  (y1(12), r1, r2, deriv(lambda e: y1(e["x"]), "x")), "rere")
p2 = lambda x: -5 * (x / 48) ** 2 + 20 * (x / 48)
R2 = max(roots(-5 / 48 ** 2, 20 / 48, 0))
sl2 = (p2(120 + 1e-6) - p2(120 - 1e-6)) / 2e-6
A("10B Q2b", HB + ("2",), r"(i) @ m (ii) @ m (iii) \(@\) (iv) \(@\) below",
  (R2, p2(R2 / 2), degrees(atan(20 / 48)), -degrees(atan(sl2))), "eerr")
p3 = lambda x: (x / 3) - 5 * (x / 3) ** 2
A("10B Q3", HB + ("3",), r"<b>a</b> \(@\) &nbsp; <b>d</b> (i) \(@\) above the horizontal (ii) \(@\) below",
  (sqrt(3 ** 2 + 1), degrees(atan((p3(0.15 + 1e-6) - p3(0.15 - 1e-6)) / 2e-6)), -degrees(atan((1 - 10 * 0.15) / 3))), "err")
A("10B Q4", HB + ("4",), r"<b>a</b> \(y=@\) &nbsp; <b>b</b> @ m &nbsp; <b>c</b> \(@\) below",
  (lambda e: -5 * (e["x"] / 5) ** 2, 5 * sqrt(20 / 5), degrees(atan(G * sqrt(20 / 5) / 5))), "eer")
(fx, fX, fy, fY), u, w = proj(24, 30)
p5 = path(24, 30)
D = max(roots(-5 / u ** 2, w / u, 6))
A("10B Q5", HB + ("5",), r"<b>a</b> \(\dot x=@\), \(\dot y=@\), \(x=@\), \(y=@\) &nbsp; <b>d</b> \(D\doteq@\)",
  (fx, fy, fX, fY, D), "eeeer")
a6 = radians(27)
V2 = 5 * 35 ** 2 / (cos(a6) ** 2 * (60 - 35 * tan(a6)))
A("10B Q6b", HB + ("6",), r"(i) @ m/s (ii) \(@\) below",
  (sqrt(V2), degrees(atan(tan(a6) + G * 35 / (V2 * cos(a6) ** 2)))), "rr")
s7 = 75 * G / 30 ** 2
A("10B Q7b", HB + ("7",), r"\(\theta\doteq@\) or \(@\)", (degrees(asin(s7)) / 2, 90 - degrees(asin(s7)) / 2), "rr")
A("10B Q8b", HB + ("8",), r"<b>b</b> \(@\)", degrees(asin(sqrt(15 * 2 * G / 20 ** 2))))
k = G * 3000 ** 2 / (2 * 200 ** 2)
Ta, Tb = sorted(roots(k, -3000, 500 + k))
A("10B Q9b", HB + ("9",), r"<b>b</b> \(@\) or \(@\)", (degrees(atan(Tb)), degrees(atan(Ta))), "rr")
A("10B Q11a", HB + ("11",), r"<b>a</b> \(x=@\), \(y=@\)",
  (lambda e: e["V"] * e["t"] * cos(pi / 4), lambda e: -e["g"] * e["t"] ** 2 / 2 + e["V"] * e["t"] * sin(pi / 4)))
A("10B Q12c(ii)", HB + ("12",), r"\(R=@\) metres", max(roots(1, -16, -6 ** 2)))

# ==========================================================================
# Chapter review
# ==========================================================================
RV = ("Chapter 10 Review", None)
(fx, fX, fy, fY), u, w = proj(60, 40)
A("Rev Q1", RV + ("1",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> (i) \(t\doteq@\) seconds (ii) @ m (iii) @ m",
  (fX, fY, 2 * w / G, u * 2 * w / G, w * w / (2 * G)), "eerrr")
(fx, fX, fy, fY), u, w = proj(30, 60)
t2 = max(roots(-5, w, 40))
A("Rev Q2", RV + ("2",), r"<b>a</b> @ m &nbsp; <b>b</b> @ m &nbsp; <b>c</b> @ m/s",
  (w * w / (2 * G), u * t2, sqrt(u * u + (w - G * t2) ** 2)), "err")
(fx, fX, fy, fY), u, w = proj(25, degrees(atan(4 / 3)))
A("Rev Q3", RV + ("3",), r"<b>b</b> \(x=@\), \(y=@\) &nbsp; <b>c</b> \(@\) m",
  (fX, fY, sqrt(fX({"t": 1}) ** 2 + fY({"t": 1}) ** 2)))
(fx, fX, fy, fY), u, w = proj(10, 45)
p4 = path(10, 45)
R4 = u * 2 * w / G
xa, xb = sorted(roots(-G / (2 * u * u), w / u, -2.1))
A("Rev Q4a", RV + ("4",), r"<b>a</b> \(\dot x=@\), \(x=@\), \(\dot y=@\), \(y=@\)", (fx, fX, fy, fY))
A("Rev Q4b,c,d", RV + ("4",),
  r"range: @ metres, maximum height: @ metres when \(x=@\) &nbsp; <b>c</b> (i) @ metres (ii) \(\tan^{-1}@\) below the horizontal &nbsp; <b>d</b> (i) \(x=@\) (ii) \(\tan^{-1}@\) above",
  (R4, p4({"x": R4 / 2}), R4 / 2, p4({"x": 8}), -deriv(p4, "x")({"x": 8}), xa, deriv(p4, "x")({"x": xa})))
vec_answers("Rev Q5a,b", RV + ("5",), 24, 18)
A("Rev Q5c", RV + ("5",), r"(i) @ m/s (ii) \(@\tv{i}-@\tv{j}\) (iii) \(@\tv{i}+@\tv{j}\)",
  (sqrt(24 ** 2 + 18 ** 2), 24 * 4, -(18 * 4 - 5 * 16), 24 * 1.8, 18 * 1.8 - 5 * 1.8 ** 2))
ux6, uy6 = 24 * sqrt(5) / 2, (28 + 5 * 4) / 2
A("Rev Q6", RV + ("6",), r"<b>a</b> \(\tv{v}=@\tv{i}+@\tv{j}\) &nbsp; <b>b</b> \(@\tv{i}+@\tv{j}\)",
  (ux6, uy6, 3 * ux6, 3 * uy6 - 5 * 9))
A("Rev Q6c", RV + ("6",), r"\(\dot y=@<0\)", uy6 - G * 3)
uy7 = G * 3 / 2
A("Rev Q7b", RV + ("7",), r"<b>b</b> @ m", uy7 ** 2 / (2 * G))
ux8, uy8 = 5 * cos(atan(2)), 5 * sin(atan(2))
tf8 = 2 * uy8 / G
A("Rev Q8a", RV + ("8",), r"Initially \(\dot x=@\) and \(\dot y=@\).", (ux8, uy8))
A("Rev Q8b", RV + ("8",), r"<b>b</b> \(\dot x=@\), \(x=@\), \(\dot y=@\), \(y=@\) &nbsp;",
  (lambda e: ux8, lambda e: ux8 * e["t"], lambda e: uy8 - G * e["t"], lambda e: uy8 * e["t"] - 5 * e["t"] ** 2))
A("Rev Q8d,e", RV + ("8",), r"<b>d</b> @ metre &nbsp; <b>e</b> @ metres", (uy8 ** 2 / (2 * G), ux8 * tf8))
A("Rev Q8f", RV + ("8",), r"<b>f</b> \(\dot x=@\), \(\dot y=@\), \(v=@\) m/s, \(\theta=-\tan^{-1}@\)",
  (ux8, uy8 - G * tf8, sqrt(ux8 ** 2 + (uy8 - G * tf8) ** 2), -(uy8 - G * tf8) / ux8))
A("Rev Q8g", RV + ("8",), r"<b>g</b> \(y=@\)$", lambda e: uy8 * (e["x"] / ux8) - 5 * (e["x"] / ux8) ** 2)
a9 = radians(26)
A("Rev Q9", RV + ("9",), r"^@ m/s", sqrt(5 * 30 ** 2 / (cos(a9) ** 2 * (30 * tan(a9) - 12))), "r")
# pack Q10 = textbook Ch 10 review Q11: 15 m/s at 60 deg, slope 30 deg
p10 = path(15, 60)
xl = (tan(radians(60)) - tan(radians(30))) / (G / (2 * (15 * cos(radians(60))) ** 2))
A("Rev Q10 (textbook Q11)", RV + ("10",), r"<b>b</b> \(y=@\) &nbsp; <b>c</b> (i) @ m (ii) \(@\) seconds",
  (p10, xl / cos(radians(30)), xl / (15 * cos(radians(60)))))
I("Rev Q10 landing point is on the slope", p10({"x": xl}), xl * tan(radians(30)))
# pack Q11 = Ch 9 review Q18: ladder 500 cm, foot 140 cm, 5 cm/s
yl = sqrt(500 ** 2 - 140 ** 2)
A("Rev Q11 (Ch 9 Q18)", RV + ("11",), r"<b>a</b> \(@\) cm/s &nbsp; <b>b</b> \(@\) radians per second",
  (-140 / yl * 5, -5 / yl))

# ==========================================================================
# Part 2: identities with arbitrary values (not tied to the HTML)
# ==========================================================================
for V, thd, g in ((17.0, 50.0, 9.8), (23.0, 31.0, 10.0)):
    th = radians(thd)
    H = (V * sin(th)) ** 2 / (2 * g)
    Rg = 2 * V * V * sin(th) * cos(th) / g
    tt = 2 * V * sin(th) / g
    I(f"10A Q16a(i) greatest height V={V},θ={thd}", V * sin(th) * (V * sin(th) / g) - g / 2 * (V * sin(th) / g) ** 2, V ** 2 * sin(th) ** 2 / (2 * g))
    I(f"10A Q16a(ii) range V={V},θ={thd}", V * cos(th) * tt, V ** 2 * sin(2 * th) / g)
    for kk in (1, -1):
        t = (sqrt(2) + kk) * sqrt(H) / sqrt(g)
        I(f"10A Q18b height h/2 at t (k={kk}) V={V},θ={thd}", V * t * sin(th) - g * t * t / 2, H / 2)
    # 10A Q18a: find the greatest height by a ternary search on y(t), with no formula for H
    lo, hi = 0.0, tt
    for _ in range(200):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if V * m1 * sin(th) - g * m1 * m1 / 2 < V * m2 * sin(th) - g * m2 * m2 / 2:
            lo = m1
        else:
            hi = m2
    hnum = V * lo * sin(th) - g * lo * lo / 2
    I(f"10A Q18a V^2 sin^2θ = 2gh, h by search, V={V},θ={thd}", V ** 2 * sin(th) ** 2, 2 * g * hnum)
    xv = Rg / 2
    I(f"10B Q8a vertex x V={V},θ={thd}", xv, V * V * sin(2 * th) / (2 * g))
    I(f"10B Q8a vertex y V={V},θ={thd}", xv * tan(th) - g * xv * xv / (2 * V * V * cos(th) ** 2), V * V * sin(th) ** 2 / (2 * g))
    I(f"10B Q12b path V={V},θ={thd}", 0.3 * Rg * tan(th) - g * (0.3 * Rg) ** 2 / (2 * V * V * cos(th) ** 2), 0.3 * Rg * (1 - 0.3) * tan(th))
th = atan(4 / 5)
I("10A Q16b range = 5 x height at θ = arctan 4/5", sin(2 * th), 5 * sin(th) ** 2 / 2)
V, g = 13.0, 9.8
th = asin(sqrt(2 * 2 * g) / V)
I("10A Q17 tunnel range (V=13, g=9.8)", V * V * sin(2 * th) / g, sqrt(16 / g * (V * V - 4 * g)))
th = atan(1 / 3)
kk = 1 / 45
for d, sgn in ((60, -1), (30, 1)):
    X, Y = d * cos(th), sgn * d * sin(th)
    I(f"10B Q11c point {d} m along the hill is on y = x - gx²/V²", X - X * X * kk / cos(th), Y)
Cc, Vv, Ll = 7.0, 3.0, 11.0
I("9E Q11b passing speed (C=7,V=3,L=11)", Vv + acc11({"C": Cc, "V": Vv, "L": Ll}) * Ll / Vv, Vv * (1 + 2 * Cc / Ll))

# --------------------------------------------------------------------------
nt, ni = len(tied), len(ident)
bad = (nt - sum(tied)) + (ni - sum(ident))
print(f"\nHTML-tied values: {sum(tied)}/{nt} OK")
print(f"Identity checks (arbitrary values, not tied to HTML): {sum(ident)}/{ni} OK")
print("ALL OK" if bad == 0 else f"{bad} FAILED")
sys.exit(1 if bad else 0)
