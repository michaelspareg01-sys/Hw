"""Numeric root finder for checking trig equations: roots(f, a, b) -> sorted roots (incl. tangential)."""
from math import *
def roots(f, a, b, n=200000, tol=1e-9):
    out = []
    def g(x):
        try: return f(x)
        except (ZeroDivisionError, ValueError): return float('nan')
    xs = [a + (b-a)*i/n for i in range(n+1)]
    ys = [g(x) for x in xs]
    for i in range(n):
        y0, y1 = ys[i], ys[i+1]
        if y0 != y0 or y1 != y1: continue
        if abs(y0) < 1e-12: out.append(xs[i]); continue
        if y0*y1 < 0 and abs(y0) < 1 and abs(y1) < 1:
            lo, hi = xs[i], xs[i+1]
            for _ in range(80):
                m = (lo+hi)/2
                if g(lo)*g(m) <= 0: hi = m
                else: lo = m
            out.append((lo+hi)/2)
    if abs(ys[-1]) < 1e-12: out.append(b)
    # tangential roots: local minima of |f| near zero
    for i in range(1, n):
        if ys[i]==ys[i] and ys[i-1]==ys[i-1] and ys[i+1]==ys[i+1]:
            if abs(ys[i]) < 1e-6 and abs(ys[i]) <= abs(ys[i-1]) and abs(ys[i]) <= abs(ys[i+1]):
                out.append(xs[i])
    out.sort(); res = []
    for r in out:
        if not res or abs(r - res[-1]) > 1e-6: res.append(r)
    return res
def deg(rs): return [round(degrees(r), 4) for r in rs]
def dms(d): 
    m = round(d*60); return f"{m//60}d {m%60}'"
def pis(rs): return [round(r/pi, 5) for r in rs]
