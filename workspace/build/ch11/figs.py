import os, sys
from math import sin, cos, pi, sqrt, radians
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, quadrant

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, svg):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)


PI_TICKS = [(pi / 2, "π/2"), (pi, "π"), (3 * pi / 2, "3π/2"), (2 * pi, "2π")]

# 11A worked example: y = sin^2 x
g = Graph(0, 2 * pi, -0.3, 1.25, 430, 190)
g.axes().xticks([(pi / 4, ""), (pi / 2, "π/2"), (3 * pi / 4, ""), (pi, "π"), (3 * pi / 2, "3π/2"), (2 * pi, "2π")])
g.yticks([(1, "1"), (0.5, "1/2")])
g.hline(0.5, x0=0, x1=2 * pi).hline(1, x0=0, x1=2 * pi)
g.curve(lambda x: sin(x) ** 2, "blue")
save("sin2", g.svg())

# answers: y = cos^2 x and y = 2cos^2 x
g = Graph(0, 2 * pi, -0.3, 1.25, 430, 190)
g.axes().xticks(PI_TICKS).yticks([(1, "1"), (0.5, "1/2")])
g.hline(0.5).curve(lambda x: cos(x) ** 2, "blue")
save("cos2", g.svg())
g = Graph(0, 2 * pi, -0.4, 2.4, 430, 190)
g.axes().xticks(PI_TICKS).yticks([(2, "2"), (1, "1")])
g.hline(1).curve(lambda x: 2 * cos(x) ** 2, "blue")
save("twocos2", g.svg())

# 11B intro: sin x, cos x and their sum
g = Graph(0, 2 * pi, -1.6, 1.7, 450, 230)
g.axes().xticks(PI_TICKS).yticks([(1, "1"), (-1, "-1"), (sqrt(2), "√2"), (-sqrt(2), "-√2")])
g.curve(sin, "faint", 1.4, "5 3").curve(cos, "faint", 1.4, "1.5 3")
g.curve(lambda x: sin(x) + cos(x), "blue", 2.4)
g.label(2.45, 0.95, "y = sin x", color="faint", size=10.5)
g.label(5.65, 1.05, "y = cos x", color="faint", size=10.5)
g.label(1.2, 1.55, "y = sin x + cos x", dx=70, color="blue", size=11)
save("sumwave", g.svg())

# Example: y = sqrt2 sin(x + pi/4)
g = Graph(0, 2 * pi, -1.75, 1.85, 450, 230)
g.axes().xticks([(pi / 4, "π/4"), (3 * pi / 4, "3π/4"), (5 * pi / 4, "5π/4"), (7 * pi / 4, "7π/4"), (2 * pi, "2π")])
g.yticks([(sqrt(2), "√2"), (1, "1"), (-sqrt(2), "-√2")])
g.hline(sqrt(2), x0=0, x1=pi / 4).vline(pi / 4, 0, sqrt(2)).hline(-sqrt(2), x0=0, x1=5 * pi / 4).vline(5 * pi / 4, -sqrt(2), 0)
g.curve(lambda x: sqrt(2) * sin(x + pi / 4), "blue")
g.dot(3 * pi / 4, 0).dot(7 * pi / 4, 0).dot(pi / 4, sqrt(2)).dot(5 * pi / 4, -sqrt(2))
save("root2sin", g.svg())

# Example: y = 3 sin x - 4 cos x = 5cos(x - 143 deg), with y = -2
D = radians
g = Graph(-180, 180, -5.9, 5.9, 520, 260, pad=(36, 44, 22, 30))
f = lambda x: 3 * sin(D(x)) - 4 * cos(D(x))
g.axes().xticks([(-180, "-180°"), (-127, "-127°"), (-37, ""), (53, "53°"), (143, ""), (180, "180°")])
g.yticks([(5, "5"), (-5, "-5")])
g.hline(5, x0=0, x1=143).vline(143, 0, 5).hline(-5, x0=-37, x1=0).vline(-37, -5, 0)
g.hline(-2, color="rose", dash="6 3", width=1.6)
g.vline(-103, -2, 0, color="rose").vline(30, -2, 0, color="rose")
g.curve(f, "blue")
g.label(-37, -5, "-37°", dy=13, size=10.5)
g.label(143, 5, "143°", dx=16, dy=-2, anchor="start", size=10.5)
g.label(-103, 0, "-103°", dy=-12, size=10.5, color="rose")
g.label(30, 0, "30°", dx=4, dy=-12, anchor="start", size=10.5, color="rose")
g.label(98, -2, "y = -2", dy=-11, color="rose", size=10.5)
save("fivecos", g.svg())

# quadrant pictures for the auxiliary angle
save("q45", quadrant(45, "π/4"))
save("q315", quadrant(-45, "7π/4"))
save("q143", quadrant(143, "143°"))

# answers: y = 2 sin(x + pi/6) (tutor demo 11B)
g = Graph(0, 2 * pi, -2.5, 2.6, 450, 230)
g.axes().xticks([(pi / 3, "π/3"), (5 * pi / 6, "5π/6"), (4 * pi / 3, "4π/3"), (11 * pi / 6, "11π/6"), (2 * pi, "2π")])
g.yticks([(2, "2"), (1, "1"), (-2, "-2")])
g.hline(2, x0=0, x1=pi / 3).vline(pi / 3, 0, 2).hline(-2, x0=0, x1=4 * pi / 3).vline(4 * pi / 3, -2, 0)
g.curve(lambda x: 2 * sin(x + pi / 6), "blue").dot(0, 1)
save("twosin6", g.svg())

# answers: sqrt2 sin(x - pi/4) (attempt) and inequality picture sqrt3 sin x + cos x >= 1
g = Graph(0, 2 * pi, -1.75, 1.85, 450, 220)
g.axes().xticks([(pi / 4, "π/4"), (3 * pi / 4, "3π/4"), (5 * pi / 4, "5π/4"), (7 * pi / 4, "7π/4"), (2 * pi, "2π")])
g.yticks([(sqrt(2), "√2"), (-1, "-1"), (-sqrt(2), "-√2")])
g.hline(sqrt(2), x0=0, x1=3 * pi / 4).vline(3 * pi / 4, 0, sqrt(2)).hline(-sqrt(2), x0=0, x1=7 * pi / 4).vline(7 * pi / 4, -sqrt(2), 0)
g.curve(lambda x: sqrt(2) * sin(x - pi / 4), "blue").dot(0, -1)
save("root2sinm", g.svg())

g = Graph(0, 2 * pi, -2.5, 2.6, 450, 230)
g.axes().xticks([(2 * pi / 3, "2π/3"), (pi, "π"), (2 * pi, "2π")]).yticks([(2, "2"), (1, "1"), (-2, "-2")])
g.hline(1, color="rose", dash="6 3", width=1.6)
g.curve(lambda x: 2 * sin(x + pi / 6), "blue")
g.shade_x(0, 2 * pi / 3, "teal").dot(2 * pi, 0, "teal").dot(0, 0, "teal").dot(2 * pi / 3, 0, "teal")
g.label(6.1, 1, "y = 1", dy=-11, anchor="end", color="rose", size=10.5)
save("ineq", g.svg())

# revision answer: y = 2 sin(x - pi/4)
g = Graph(0, 2 * pi, -2.5, 2.6, 450, 220)
g.axes().xticks([(pi / 4, "π/4"), (3 * pi / 4, "3π/4"), (5 * pi / 4, "5π/4"), (7 * pi / 4, "7π/4"), (2 * pi, "2π")])
g.yticks([(2, "2"), (-2, "-2"), (-sqrt(2), "-√2")])
g.curve(lambda x: 2 * sin(x - pi / 4), "blue").dot(0, -sqrt(2))
save("rev_sin", g.svg())

# homework answer sketches 11B
g = Graph(0, 2 * pi, -1.75, 1.85, 430, 210)
g.axes().xticks([(3 * pi / 4, "3π/4"), (pi / 2, "π/2"), (pi, "π"), (7 * pi / 4, "7π/4"), (2 * pi, "2π")])
g.yticks([(sqrt(2), "√2"), (-1, "-1"), (-sqrt(2), "-√2")])
g.hline(-1, color="rose", dash="6 3", width=1.4).curve(lambda x: cos(x) - sin(x), "blue")
g.dot(pi / 2, -1, "rose").dot(pi, -1, "rose")
save("hw3f", g.svg())

g = Graph(0, 2 * pi, -2.4, 2.5, 430, 210)
g.axes().xticks([(pi / 6, "π/6"), (5 * pi / 6, "5π/6"), (3 * pi / 2, "3π/2"), (2 * pi, "2π")])
g.yticks([(2, "2"), (1, "1"), (-2, "-2")])
g.hline(1, color="rose", dash="6 3", width=1.4).curve(lambda x: sqrt(3) * cos(x) - sin(x), "blue")
g.dot(pi / 6, 1, "rose").dot(3 * pi / 2, 1, "rose")
save("hw5f", g.svg())

g = Graph(0, 2 * pi, -1.75, 1.85, 430, 210)
g.axes().xticks([(pi / 4, "π/4"), (pi / 2, "π/2"), (pi, "π"), (5 * pi / 4, "5π/4"), (2 * pi, "2π")])
g.yticks([(sqrt(2), "√2"), (1, "1"), (-1, "-1"), (-sqrt(2), "-√2")])
g.hline(1, color="rose", dash="6 3", width=1.4).curve(lambda x: sin(x) - cos(x), "blue")
g.shade_x(pi / 2, pi, "teal")
save("hw19", g.svg())
print("figures written")
