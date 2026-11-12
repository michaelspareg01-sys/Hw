"""Shared helpers for the Year 10 Circle Geometry checks (y10circ_rev.py, y10circ_c1.py, ...).

Printed values are tagged in the HTML as <span data-v="KEY">number</span> (answers and working) and
given data as <span data-g="KEY">number</span> (questions). Every key must occur exactly once in the
files read, or the check FAILS. SVG figure labels are read from build/y10circ/svg/*.svg.
"""
import os
import re
from math import atan2, degrees, hypot, acos

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y10CIRC_SRC", os.path.join(HERE, "..", "build", "y10circ"))
FAILS, NOK = [], [0]


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


def tagged(names, attr="data-v"):
    """{key: [printed strings]} for every <span attr="key">...</span> in the named files."""
    out = {}
    for n in names:
        for m in re.finditer(r'<span %s="([^"]+)">(.*?)</span>' % attr, read(n), re.S):
            out.setdefault(m.group(1), []).append(m.group(2))
    return out


def num(s):
    """The last number printed in s (TeX or text): e.g. '\\(\\dfrac{10}{5}=2\\)' gives 2, '\\(a=-3.5^\\circ\\)' gives -3.5."""
    s = s.replace("−", "-").replace("&minus;", "-")
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    m = re.findall(r"-?\d+(?:\.\d+)?", s)
    return float(m[-1])


class Values:
    def __init__(self, names, attr="data-v"):
        self.d = tagged(names, attr)
        self.used = set()
        self.attr = attr

    def get(self, key):
        self.used.add(key)
        v = self.d.get(key, [])
        if len(v) != 1:
            ok(False, f"{self.attr}={key}", f"found {len(v)} times (must be exactly once)")
            return None
        return num(v[0])

    def unused(self):
        return sorted(set(self.d) - self.used)


def check(vals, key, expect, tol=1e-6, label=""):
    got = vals.get(key)
    if got is None:
        return
    ok(abs(got - expect) <= tol * max(1, abs(expect)), f"{key} {label}".strip(), f"printed {got:g}, computed {expect:.6g}")


def svg_labels(name):
    s = read(os.path.join("svg", name + ".svg"))
    return [re.sub(r"<[^>]+>", "", m.group(1)) for m in re.finditer(r"<text[^>]*>(.*?)</text>", s, re.S)]


def svg_has(name, *labels):
    have = svg_labels(name)
    for lab in labels:
        ok(lab in have, f"figure {name} shows label {lab!r}")


def ang(v, p, q):
    """Angle pvq in degrees from coordinates."""
    a = (p[0] - v[0], p[1] - v[1])
    b = (q[0] - v[0], q[1] - v[1])
    c = (a[0] * b[0] + a[1] * b[1]) / (hypot(*a) * hypot(*b))
    return degrees(acos(max(-1.0, min(1.0, c))))


def dist(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])


def polygons(name):
    """List of point lists of the <polygon> elements of a figure (as drawn)."""
    s = read(os.path.join("svg", name + ".svg"))
    out = []
    for m in re.finditer(r'<polygon points="([^"]+)"', s):
        out.append([tuple(float(t) for t in pt.split(",")) for pt in m.group(1).split()])
    return out


def finish(vals_list=()):
    for v in vals_list:
        for k in v.unused():
            ok(False, f"{v.attr}={k}", "printed value has no check")
    print(f"\n{NOK[0]} OK, {len(FAILS)} FAIL")
    if FAILS:
        for f in FAILS:
            print("  FAIL", f)
        raise SystemExit(1)
