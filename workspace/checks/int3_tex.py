"""Small TeX -> sympy converter for the int3 check scripts (no antlr needed).

Handles the forms printed in the Integration Part 3 pack: \\dfrac/\\tfrac/\\frac (braced or single-token
arguments), \\sqrt, \\pi, powers, e^{...}, |...| and \\lvert...\\rvert, \\log_e, \\ln, sin/cos/tan/sec with
an optional square (\\sin^2x), the inverse functions (\\sin^{-1}, \\arcsin, ...), greek letters, and
function arguments written without brackets (\\sin2x, \\cos\\tfrac12x, \\sec^23x), which take the run of
numbers, letters, fractions and powers that follows.
"""
import re

import sympy as sp
from sympy.parsing.sympy_parser import (implicit_multiplication_application, parse_expr,
                                        standard_transformations)

x = sp.Symbol("x", real=True)
n, a, b, u = sp.symbols("n a b u")
theta, alpha = sp.symbols("theta alpha")
TR = standard_transformations + (implicit_multiplication_application,)
LOCAL = {"x": x, "n": n, "a": a, "b": b, "u": u, "theta": theta, "alpha": alpha, "e": sp.E, "pi": sp.pi,
         "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sec": sp.sec, "asin": sp.asin, "acos": sp.acos,
         "atan": sp.atan, "log": sp.log, "sqrt": sp.sqrt, "Abs": sp.Abs}

FUNCS = {"sin": "sin", "cos": "cos", "tan": "tan", "sec": "sec", "arcsin": "asin", "arccos": "acos",
         "arctan": "atan", "ln": "log"}
GREEK = {"alpha": "alpha", "theta": "theta", "pi": "pi"}
STRIP = r"\\left|\\right|\\Bigg|\\bigg|\\Big|\\big|\\displaystyle|\\,|\\;|\\!|\\ |\\qquad|\\quad"


class P:
    def __init__(self, s):
        self.s, self.i = s, 0

    def peek(self, k=0):
        j = self.i + k
        return self.s[j] if j < len(self.s) else ""

    def cmd(self):
        m = re.match(r"\\([A-Za-z]+)", self.s[self.i:])
        return m.group(1) if m else None

    def group(self):
        """One TeX argument: {...} or a single character / command. Returns python text."""
        if self.peek() == "{":
            depth, j = 0, self.i
            while True:
                c = self.s[j]
                depth += c == "{"
                depth -= c == "}"
                if depth == 0:
                    break
                j += 1
            inner = self.s[self.i + 1:j]
            self.i = j + 1
            return "(" + conv(inner) + ")"
        c = self.cmd()
        if c:
            self.i += len(c) + 1
            return GREEK.get(c, c)
        ch = self.peek()
        self.i += 1
        return ch

    def atom(self):
        """A single factor for a function-argument run, or None if the next token ends the run."""
        c = self.cmd()
        if c in ("dfrac", "tfrac", "frac"):
            self.i += len(c) + 1
            num, den = self.group(), self.group()
            return f"(({num})/({den}))"
        if c == "sqrt":
            self.i += 5
            return f"sqrt({self.group()})"
        if c in GREEK:
            self.i += len(c) + 1
            return GREEK[c]
        ch = self.peek()
        if ch and (ch.isdigit() or ch == "." or (ch.isalpha() and ch != "C")):
            self.i += 1
            return ch
        return None

    def run(self):
        """Function argument without brackets: atoms and powers until something else."""
        out = []
        while True:
            if self.peek() == "^" and out:
                self.i += 1
                out.append("**" + self.group())
                continue
            t = self.atom()
            if t is None:
                break
            out.append(t)
        if not out:
            raise ValueError(f"empty function argument at {self.s[self.i:self.i + 20]!r}")
        return "(" + " ".join(out) + ")"

    def bracket(self, open_, close):
        depth, j = 0, self.i
        while j < len(self.s):
            if self.s[j] == open_:
                depth += 1
            elif self.s[j] == close:
                depth -= 1
                if depth == 0:
                    break
            j += 1
        inner = self.s[self.i + 1:j]
        self.i = j + 1
        return "(" + conv(inner) + ")"

    def func_arg(self):
        while self.peek() in ("~", " "):
            self.i += 1
        if self.peek() == "(":
            return self.bracket("(", ")")
        if self.peek() == "|":
            j = self.s.index("|", self.i + 1)
            inner = self.s[self.i + 1:j]
            self.i = j + 1
            return "(Abs(" + conv(inner) + "))"
        return self.run()


def conv(s):
    s = re.sub(STRIP, "", s)
    s = s.replace("\\lvert", "|").replace("\\rvert", "|").replace("\\log_e", "\\ln~")
    s = s.replace("\\times", "*").replace("\\cdot", "*")
    for f in ("sin", "cos", "tan"):
        s = s.replace(f"\\{f}^{{-1}}", f"\\arc{f}~")
    p, out = P(s), []
    while p.i < len(s):
        c = p.cmd()
        if c in FUNCS:
            p.i += len(c) + 1
            power = ""
            if p.peek() == "^":
                p.i += 1
                power = "**" + p.group()
            out.append(" " + FUNCS[c] + "(" + p.func_arg() + ")" + power + " ")
            continue
        if c in ("dfrac", "tfrac", "frac", "sqrt") or c in GREEK:
            out.append(" " + p.atom() + " ")
            continue
        if c:
            raise ValueError(f"unknown command \\{c} in {s!r}")
        ch = p.peek()
        if ch == "~":
            p.i += 1
        elif ch == "{":
            out.append(p.group())
        elif ch == "|":
            j = s.index("|", p.i + 1)
            out.append("Abs(" + conv(s[p.i + 1:j]) + ")")
            p.i = j + 1
        elif ch == "^":
            p.i += 1
            out.append("**" + p.group())
        elif ch == "[":
            out.append(p.bracket("[", "]"))
        else:
            out.append(ch)
            p.i += 1
    return "".join(out)


def tex(s, extra=None):
    """Parse TeX text into a sympy expression."""
    loc = dict(LOCAL)
    if extra:
        loc.update(extra)
    return parse_expr(conv(s), local_dict=loc, transformations=TR)


def split_top(s, sep="="):
    """Split at top-level separators (outside braces and brackets)."""
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


if __name__ == "__main__":
    tests = {
        r"\sin^{-1}\tfrac12": sp.pi / 6,
        r"\cos^{-1}\Big(-\tfrac{1}{\sqrt2}\Big)": 3 * sp.pi / 4,
        r"\arctan\big(3\tan\tfrac{7\pi}{6}\big)": sp.pi / 3,
        r"2\times\tfrac{\sqrt{13}}{7}\times\tfrac67": 12 * sp.sqrt(13) / 49,
        r"-\tfrac12\log_e7": -sp.log(7) / 2,
        r"\tfrac12\big(e^2-1\big)": (sp.E ** 2 - 1) / 2,
        r"\dfrac{2\times(-2)}{1-(-2)^2}": sp.Rational(4, 3),
        r"\log_e\lvert-7\rvert-\log_e\lvert-1\rvert": sp.log(7),
        r"-\cos\tfrac{\pi}{3}+\cos0": sp.Rational(1, 2),
        r"5\big(\log_ee^2-\log_ee\big)": 5,
    }
    for k, v in tests.items():
        got = tex(k)
        assert sp.simplify(got - v) == 0, (k, conv(k), got)
    fx = {
        r"\cos\tfrac12x": sp.cos(x / 2), r"\sec^23x": sp.sec(3 * x) ** 2, r"\sin4x": sp.sin(4 * x),
        r"2\sin\tfrac12x": 2 * sp.sin(x / 2), r"\tfrac12\log_e|2x+5|": sp.log(sp.Abs(2 * x + 5)) / 2,
        r"e^{-2x}": sp.exp(-2 * x), r"\dfrac{(2x+1)^5}{10}": (2 * x + 1) ** 5 / 10,
        r"2\cos^2\alpha-1": 2 * sp.cos(alpha) ** 2 - 1, r"\sin^2\theta+\cos^2\theta": 1,
        r"\tfrac{\pi}{2}+\tan^{-1}(x+1)": sp.pi / 2 + sp.atan(x + 1),
    }
    for k, v in fx.items():
        got = tex(k)
        assert sp.simplify(got - v) == 0, (k, conv(k), got)
    print("int3_tex self-test OK")
