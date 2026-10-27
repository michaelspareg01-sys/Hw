import os, sys
from math import sin, cos, tan, asin, acos, atan, pi, sqrt, exp, log
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(g.svg())


def safe(f):
    def g(x):
        try:
            return f(x)
        except ValueError:
            return None
    return g


# 12A worked example 2: y = arccos(x - 1) with A and B
g = Graph(-0.3, 2.4, -0.3, 3.5, 300, 240)
g.axes().xticks([(1, "1"), (2, "2")]).yticks([(pi, "π"), (pi / 2, "π/2"), (5 * pi / 6, ""), (pi / 6, "π/6")])
g.curve(safe(lambda x: acos(x - 1)), "blue", x0=0, x1=2)
g.dot(0, pi).dot(2, 0)
ax, bx = 1 + sqrt(3) / 2, 1 - sqrt(3) / 2
g.dot(ax, pi / 6, "rose").dot(bx, 5 * pi / 6, "rose")
g.label(ax, pi / 6, "A", dx=10, dy=-8, color="rose").label(bx, 5 * pi / 6, "B", dx=10, dy=-8, color="rose")
g.label(0, 5 * pi / 6, "5π/6", dx=-8, anchor="end", size=10.5)
save("acos_shift", g)

# 12A worked example 4: y = arccos(cos x); demo answer y = arcsin(sin x)
g = Graph(-2 * pi, 3 * pi, -0.5, 3.8, 470, 190)
g.axes().xticks([(-2 * pi, "-2π"), (-pi, "-π"), (pi, "π"), (2 * pi, "2π"), (3 * pi, "3π")]).yticks([(pi, "π")])
g.curve(lambda x: acos(cos(x)), "blue", n=1200)
save("acoscos", g)
g = Graph(-pi, 2 * pi, -2, 2, 450, 200)
g.axes().xticks([(-pi, "-π"), (-pi / 2, "-π/2"), (pi / 2, "π/2"), (pi, "π"), (3 * pi / 2, "3π/2"), (2 * pi, "2π")])
g.yticks([(pi / 2, "π/2"), (-pi / 2, "-π/2")])
g.curve(lambda x: asin(max(-1, min(1, sin(x)))), "blue", n=1200)
save("asinsin", g)

# 12A homework answers: y = arccos(x^2), y = arccos(1/x)
g = Graph(-1.4, 1.4, -0.3, 2.0, 300, 200)
g.axes().xticks([(-1, "-1"), (1, "1")]).yticks([(pi / 2, "π/2")])
g.curve(safe(lambda x: acos(x * x)), "blue", x0=-1, x1=1).dot(-1, 0).dot(1, 0)
save("acos_x2", g)
g = Graph(-4, 4, -0.3, 3.6, 360, 200)
g.axes().xticks([(-1, "-1"), (1, "1")]).yticks([(pi, "π"), (pi / 2, "π/2")])
g.hline(pi / 2, x0=-4, x1=4)
g.curve(safe(lambda x: acos(1 / x)), "blue", x0=1, x1=4).curve(safe(lambda x: acos(1 / x)), "blue", x0=-4, x1=-1)
g.dot(1, 0).dot(-1, pi)
save("acos_recip", g)

# NSG 2023 answer: y = arcsin x + arccos x
g = Graph(-1.5, 1.5, -0.3, 2.1, 300, 170)
g.axes().xticks([(-1, "-1"), (1, "1")]).yticks([(pi / 2, "π/2")])
g.curve(lambda x: pi / 2, "blue", x0=-1, x1=1).dot(-1, pi / 2).dot(1, pi / 2)
save("nsg_const", g)

# 12B worked example: area under y = arcsin x from 0 to 1
g = Graph(-1.3, 1.4, -1.9, 1.9, 300, 260)
g.axes().xticks([(-1, "-1"), (1, "1")]).yticks([(pi / 2, "π/2"), (-pi / 2, "-π/2")])
g.fill(safe(lambda x: asin(x)), lambda x: 0, 0, 1, "blue")
g.curve(safe(lambda x: asin(x)), "blue", x0=-1, x1=1).dot(1, pi / 2).dot(-1, -pi / 2)
save("asin_area", g)

# 12B homework answers: Q15 and Q16 graphs
g = Graph(-2.6, 2.6, -0.3, 3.4, 330, 220)
g.axes().xticks([(-2, "-2"), (2, "2")]).yticks([(2, "2"), (0.5, "1/2")])
g.curve(safe(lambda x: sqrt(4 - x * x)), "faint", 1.4, "5 3", x0=-2, x1=2)
g.curve(safe(lambda x: 1 / sqrt(4 - x * x)), "blue", x0=-1.995, x1=1.995)
g.vline(-2, color="faint").vline(2, color="faint")
save("hw15", g)
g = Graph(-4, 4, -0.3, 3.2, 360, 210)
g.axes().xticks([(-2, "-2"), (2, "2")]).yticks([(1, "1"), (2, "2")])
g.curve(lambda x: 0.25 * (x * x + 4), "faint", 1.4, "5 3").curve(lambda x: 4 / (x * x + 4), "blue")
save("hw16", g)

# 12C homework answer: y = (1 + cos 2x)/2 and (1 - cos 2x)/2
g = Graph(0, 2 * pi, -0.3, 1.3, 430, 170)
g.axes().xticks([(pi / 2, "π/2"), (pi, "π"), (3 * pi / 2, "3π/2"), (2 * pi, "2π")]).yticks([(1, "1")])
g.curve(lambda x: cos(x) ** 2, "blue").curve(lambda x: sin(x) ** 2, "rose", dash="6 3")
g.label(0.2, 1.1, "y = ½(1 + cos 2x)", anchor="start", color="blue", size=10.5)
g.label(2.2, 1.18, "y = ½(1 − cos 2x)", anchor="start", color="rose", size=10.5)
save("hw7c", g)

# 12F worked examples
g = Graph(-4.6, 4.8, -0.6, 4.8, 330, 210)
g.axes().xticks([(-4, "-4"), (2, "2"), (4, "4")]).yticks([(4, "4")])
g.fill(safe(lambda x: sqrt(16 - x * x)), lambda x: 0, 2, 4, "blue")
g.curve(safe(lambda x: sqrt(16 - x * x)), "blue", x0=-4, x1=4).vline(2, 0, sqrt(12), color="ink", dash=None)
save("v_semi", g)
g = Graph(-2.6, 2.6, -0.6, 5.0, 300, 220)
g.axes().yticks([(4, "4")])
g.fill(lambda x: 4, lambda x: x * x, -2, 2, "blue")
g.curve(lambda x: x * x, "blue", x0=-2.2, x1=2.2).hline(4, color="ink", dash=None, x0=-2, x1=2)
save("v_para", g)
g = Graph(-2.6, 2.6, -0.6, 4.8, 300, 220)
g.axes().xticks([(-2, "-2"), (2, "2")]).yticks([(4, "4")])
g.fill(lambda x: 4 - x * x, lambda x: 4 - 2 * x, 0, 2, "blue")
g.curve(lambda x: 4 - x * x, "blue", x0=-2.2, x1=2.2).curve(lambda x: 4 - 2 * x, "ink", 1.4, x0=0, x1=2)
g.label(0, 4, "A", dx=8, dy=-6).label(2, 0, "B", dx=6, dy=-10).label(-2, 0, "C", dx=-6, dy=-10)
save("v_between", g)
# King's 2021 Q13(d) region
g = Graph(-1.6, 3.8, -0.8, 5.2, 300, 240)
g.axes()
g.fill(lambda x: x + 1, lambda x: (x - 1) ** 2, 0, 3, "faint", opacity=0.45)
g.curve(lambda x: (x - 1) ** 2, "blue", x0=-1.2, x1=3.3).curve(lambda x: x + 1, "rose", 1.8, x0=-1.5, x1=3.6)
g.label(3.3, 5.0, "y = x + 1", dx=4, anchor="start", color="rose", size=10.5)
g.label(-1.1, 4.6, "y = (x − 1)²", anchor="start", color="blue", size=10.5)
save("kings_region", g)
print("figures written")
