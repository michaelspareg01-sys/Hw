import os, sys
from math import sin, cos, tan, atan, pi, sqrt, exp, log
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(g.svg())


def rng(a, b, step=1.0):
    n = int(round((b - a) / step))
    return [a + i * step for i in range(n + 1)]


def ticks(a, b):
    return [(v, str(v)) for v in range(a, b + 1) if v != 0]


def euler(f, x0, y0, x1, h=0.002, ylim=10):
    """Integrate y' = f(x, y) from (x0, y0) to x1 (either direction); returns a function sampled curve."""
    pts = [(x0, y0)]
    x, y = x0, y0
    s = h if x1 > x0 else -h
    while (x1 - x) * s > 0 and abs(y) < ylim:
        k1 = f(x, y); k2 = f(x + s / 2, y + s / 2 * k1); k3 = f(x + s / 2, y + s / 2 * k2); k4 = f(x + s, y + s * k3)
        y += s / 6 * (k1 + 2 * k2 + 2 * k3 + k4); x += s
        pts.append((x, y))
    return pts


def poly(g, pts, color="blue", width=2.0):
    s = [f"{g.X(x):.1f},{g.Y(y):.1f}" for x, y in pts if g.ymin - 0.5 <= y <= g.ymax + 0.5]
    if len(s) > 1:
        g.items.append(f'<polyline points="{" ".join(s)}" fill="none" stroke="#2563eb" stroke-width="{width}"/>')


def field_graph(f, a=4, w=300, h=300, step=1.0, curves=(), skip=None, length=12):
    g = Graph(-a - 0.4, a + 0.4, -a - 0.4, a + 0.4, w, h, pad=(24, 26, 18, 24))
    g.axes().xticks(ticks(-a, a)).yticks(ticks(-a, a))
    g.field(f, rng(-a, a, step), rng(-a, a, step), length=length, skip=skip)
    for c in curves:
        if callable(c):
            g.curve(c, "blue", 2.0)
        else:
            poly(g, c)
    return g


# ---------- lesson figures ----------
# 13A: family y = Ae^x - x - 1 for A = 1, -1, 0
g = Graph(-3, 3, -4, 4, 330, 240)
g.axes().xticks(ticks(-3, 3)).yticks(ticks(-4, 4))
g.curve(lambda x: exp(x) - x - 1, "blue").curve(lambda x: -exp(x) - x - 1, "rose").curve(lambda x: -x - 1, "teal")
g.hline(0, x0=-3, x1=3, color="faint")
g.curve(lambda x: -x, "faint", 1.3, "5 3")
g.label(1.6, 3.4, "A = 1", anchor="start", size=10.5, color="blue")
g.label(0.9, -3.4, "A = −1", anchor="start", size=10.5, color="rose")
g.label(-2.9, 2.4, "A = 0", anchor="start", size=10.5, color="teal")
g.label(-2.9, 3.4, "x + y = 0", anchor="start", size=10.5, color="faint")
save("family", g)

# 13B Concept 1: y' = x/2, with three solution curves y = x^2/4 + C
save("sf_halfx", field_graph(lambda x, y: x / 2, curves=(lambda x: x * x / 4 - 2, lambda x: x * x / 4, lambda x: x * x / 4 + 2)))
# 13B worked example: y' = -x/y with circles
circ = []
for r in (1, 2, 3):
    circ.append([(r * cos(t / 100 * 2 * pi), r * sin(t / 100 * 2 * pi)) for t in range(101)])
save("sf_circles", field_graph(lambda x, y: -x / y, curves=circ))
# 13B: y' = x + y with solutions through origin, and y = -x - 1
f = lambda x, y: x + y
c1 = euler(f, 0, 0, 1.6) [::-1] + euler(f, 0, 0, -4.4)
c2 = euler(f, 0, -1.3, 1.4)[::-1] + euler(f, 0, -1.3, -4.4)
save("sf_xpy", field_graph(f, curves=(c1, c2, lambda x: -x - 1)))
# 13B constant solutions: y' = (y-2)(y+2)/4
f = lambda x, y: (y - 2) * (y + 2) / 4
g = field_graph(f, curves=())
for y0 in (1, -1, -3, 2.1):
    poly(g, euler(f, -4.4, y0, 4.4, ylim=6))
g.hline(2, color="rose", dash="6 3", width=1.6).hline(-2, color="teal", dash="6 3", width=1.6)
save("sf_const", g)
# 13D logistic y' = y(1 - y)
f = lambda x, y: y * (1 - y)
g = Graph(-4.4, 4.4, -1.4, 2.4, 330, 220, pad=(24, 26, 18, 24))
g.axes().xticks(ticks(-4, 4)).yticks([(1, "1"), (2, "2"), (-1, "-1")])
g.field(f, rng(-4, 4, 0.5), rng(-1, 2, 0.5), length=10)
g.curve(lambda x: 1 / (1 + exp(-x)), "blue", 2.2)
g.curve(lambda x: 1 / (1 - 0.5 * exp(-x)), "rose", 2.0, x0=-log(2) + 0.02)
g.curve(lambda x: 1 / (1 - 2 * exp(-x)), "teal", 2.0, x1=log(2) - 0.02)
g.hline(1, color="faint").hline(0, color="faint")
save("logistic", g)

# ---------- past-paper figures ----------
save("pp_bb22", field_graph(lambda x, y: y / 2, a=3))
save("pp_gos22", field_graph(lambda x, y: x / y - y * y, a=3, step=0.5, length=9))
save("pp_nbhs23", field_graph(lambda x, y: (x * x - y * y) / 4, a=3, step=0.5, length=9))
save("pp_kws23", field_graph(lambda x, y: x * y, a=3, step=0.5, length=9))
save("pp_abb24", field_graph(lambda x, y: (x * x + y * y) / (x * y), a=3, step=0.5, length=9,
                             skip=lambda x, y: abs(x) < 0.4 or abs(y) < 0.4))
save("pp_asc24", field_graph(lambda x, y: (x + y) / x, a=3, step=0.5, length=9))
save("pp_st20", field_graph(lambda x, y: -x / (1 + y * y), a=2, step=0.25, length=8))
g = Graph(-1.5, 3.5, -2.5, 1.5, 300, 230, pad=(24, 26, 18, 24))
g.axes().xticks(ticks(-1, 3)).yticks(ticks(-2, 1))
g.dot(0, -1).dot(1, -1)
g.label(0, -1, "A(0, −1)", dx=-6, dy=16, anchor="end", size=10.5).label(1, -1, "B(1, −1)", dx=6, dy=16, anchor="start", size=10.5)
save("pp_bb23", g)

# ---------- answer figures ----------
save("ans_halfx_m1", field_graph(lambda x, y: x / 2 - 1, a=3, curves=(lambda x: x * x / 4 - x,)))
f = lambda x, y: -x / 2 - y
g = field_graph(f, curves=(lambda x: 0.5 - x / 2,))
for x0, y0 in ((-2, 0), (2, 0)):
    poly(g, euler(f, x0, y0, 4.4)); poly(g, euler(f, x0, y0, -4.4, ylim=8))
save("ans_q7", g)
f = lambda x, y: -x / (1 + y * y)
g = field_graph(f, a=2, step=0.25, length=8)
poly(g, euler(f, -1, 1, 2.3)); poly(g, euler(f, -1, 1, -2.3))
save("ans_st20", g)
save("sf_q7", field_graph(lambda x, y: -x / 2 - y))
save("sf_q13", field_graph(lambda x, y: -y / x, a=3, step=0.5, length=9))
save("sf_q14", field_graph(lambda x, y: 2 * y / x, a=3, step=0.5, length=9))
print("figures written")
