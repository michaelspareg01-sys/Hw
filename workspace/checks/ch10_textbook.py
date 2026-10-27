"""Numeric check of every numeric answer printed in the Ch 10 answer fragments.

Covers: warm-up (revision.html), lesson examples C1-C3 (tutor demos, your turns,
worked examples) of 9E, 10A, 10B, textbook homework (Ex 9E, 10A, 10B) and the
chapter review (Ch 10 review Q1-9, Ch 9 review Q18 as Q10).

Each item recomputes the value from the question data and compares it with the
value printed in workspace/build/ch10/a_*.html (or in the lesson worked
examples). Prints OK / MISMATCH per item.

Run: python3 workspace/checks/ch10_textbook.py
"""
from math import sqrt, pi, sin, cos, tan, atan, asin, radians, degrees, isclose

results = []


def check(name, computed, printed, tol=None):
    """printed is the value shown in the HTML. tol defaults to half a unit in
    the last printed place when rounding is implied, else a tight relative tol."""
    if tol is None:
        tol = 1e-9 * max(1.0, abs(printed))
    ok = abs(computed - printed) <= tol
    results.append(ok)
    print(f"{'OK      ' if ok else 'MISMATCH'} {name}: computed {computed:.6g}, printed {printed:.6g}")


def dms(d, m):
    return d + m / 60


def deg_min(x):
    """Round degrees to nearest minute, return (d, m)."""
    tot = round(x * 60)
    return tot // 60, tot % 60


def check_dm(name, angle_deg, d, m):
    got = deg_min(angle_deg)
    ok = got == (d, m)
    results.append(ok)
    print(f"{'OK      ' if ok else 'MISMATCH'} {name}: computed {got[0]}°{got[1]}', printed {d}°{m}'")


def roots(a, b, c):
    D = b * b - 4 * a * c
    if D < 0:
        return None
    return ((-b + sqrt(D)) / (2 * a), (-b - sqrt(D)) / (2 * a))


# =================== Warm-up ===================
x = lambda t: t * t - 6 * t + 5
check("W1b stationary t", 6 / 2, 3)
check("W1b position", x(3), -4)
dist = abs(x(3) - x(0)) + abs(x(4) - x(3))
check("W1c distance", dist, 10)
check("W1c average velocity", (x(4) - x(0)) / 4, -2)
check("W1c average speed", dist / 4, 2.5)
check("W2 discriminant of 3t^2-4t+3 (negative)", 16 - 36 < 0, True)
check("W3 greatest height", 20 * 2 - 5 * 4, 20)
check("W3 return time", 20 / 5, 4)
check("W3 return speed", abs(20 - 10 * 4), 20)
check("W4 40cos30 = 20sqrt3", 40 * cos(radians(30)), 20 * sqrt(3))
check("W4 40sin30", 40 * sin(radians(30)), 20)
check("W4 tan^-1 3/4 nearest degree", round(degrees(atan(0.75))), 37)
check("W4 sqrt(36+64)", sqrt(36 + 64), 10)
check("W5 dA/dt", 2 * pi * 4 * 3, 24 * pi)

# =================== 9E lesson ===================
check("9E C1 demo b", 4 * pi * 25 * 2, 200 * pi)
r = (36 * pi * 3 / (4 * pi)) ** (1 / 3)
check("9E C1 demo c r", r, 3)
check("9E C1 demo c dr/dt", 72 * pi / (4 * pi * r * r), 2)
check("9E C1 your turn a", 0.4 * 4, 1.6)
check("9E C1 your turn b", 2 / 0.4, 5)
# worked example 1 (textbook Example 18)
check("9E WE1 b", 2 * pi * 36 * 3, 216 * pi)
r = (18 * 3 / (2 * pi)) ** (1 / 3)
check("9E WE1 c r = 3 pi^-1/3", r, 3 * pi ** (-1 / 3))
check("9E WE1 c dr/dt = 5 pi^-1/3", 90 / (2 * pi * r * r), 5 * pi ** (-1 / 3))
check("9E WE1 c dr/dt ~ 3.4", 90 / (2 * pi * r * r), 3.4, 0.05)
# C2: cone r = h/2, V = pi h^3/12
check("9E C2 demo b dh/dt", 12 / (pi / 4 * 16), 3 / pi)
check("9E C2 demo b ~0.95", 3 / pi, 0.95, 0.005)
check("9E C2 your turn", 9 * pi / (pi * 9), 1)
# WE2 ladder 5 m, dx/dt = 0.3, x = 3
check("9E WE2 dy/dt", -3 / sqrt(25 - 9) * 0.3, -0.225)
# C3 plane 2 km, 600 km/h, theta = pi/6
th = pi / 6
dthdt = -(sin(th) ** 2) / 2 * (-600)
check("9E C3 demo rad/h", dthdt, 75)
check("9E C3 demo deg/s", dthdt * 180 / pi / 3600, 1.19, 0.005)
th = radians(30)
dthdt = -(sin(th) ** 2) / 80 * (-4)
check("9E C3 your turn rad/s", dthdt, 0.0125)
check("9E C3 your turn deg/s", degrees(dthdt), 0.72, 0.005)
# WE3 balloon 5 m/s, 120 m, h = 50
c2 = (120 / 130) ** 2
check("9E WE3 rad/s", c2 * 5 / 120, 6 / 169)
check("9E WE3 rad/s ~0.0355", 6 / 169, 0.0355, 0.00005)
check("9E WE3 deg/s", degrees(6 / 169), 2.03, 0.005)

# =================== Exercise 9E ===================
check("9E Q1b", 0.2 * 5, 1)
check("9E Q1c", 1.4 / 0.2, 7)
check("9E Q1d", (0.6 / 0.2) ** 2, 9)
# Q2 A = l^2/2, dA/dt = -l/2
check("9E Q2c(i)", 10 / 2, 5)
check("9E Q2c(ii)", sqrt(2 * 18) / 2, 3)
check("9E Q2d", 17 * 2, 34)
check("9E Q3a", 1.2 * pi * 4, 15.1, 0.05)
check("9E Q3b", 2.4 * pi * 4, 30.2, 0.05)
check("9E Q4b", 200 / (4 * pi * 225), 2 / (9 * pi))
r = sqrt(200 / (4 * pi * 0.5))
check("9E Q4c r", r, 10 / sqrt(pi))
check("9E Q4c V", 4 / 3 * pi * r ** 3, 4000 / (3 * sqrt(pi)))
# Q5 h = 2r: V = 2/3 pi r^3, dV/dt = 2 pi r^2 dr/dt, h = 10 -> r = 5
check("9E Q5a V = (1/3)pi r^2 (2r) = (2/3) pi r^3 at r=1.7", pi * 1.7 ** 2 * 2 * 1.7 / 3, 2 / 3 * pi * 1.7 ** 3)
check("9E Q5b", 5 / (2 * pi * 25), 1 / (10 * pi))
# Q6 x = 3/(2 tan th), dx/dt = -650, th = pi/3
th = pi / 3
d6 = 650 * 2 * sin(th) ** 2 / 3
check("9E Q6b rad/h", d6, 325)
check("9E Q6b deg/s nearest", round(d6 * 180 / pi / 3600), 5)
# Q7 x = 100/tan th, dx/dt = -50, th = 15 deg
d7 = 50 * sin(radians(15)) ** 2 / 100
check("9E Q7 rad/min", d7, 0.5 * sin(radians(15)) ** 2)
check("9E Q7 rad/min ~0.0335", d7, 0.0335, 0.00005)
check("9E Q7 deg/min nearest", round(degrees(d7)), 2)
# Q8 isosceles right-angled cross-section: width 2h, length 100x cm
hh, xx = 7.0, 3.0
check("9E Q8a V = 100 h^2 x", 0.5 * (2 * hh) * hh * (100 * xx), 100 * hh ** 2 * xx)
dVdt = -0.1 * (2 * hh) * (100 * xx)
check("9E Q8b rate of fall of depth (cm/day)", -dVdt / (200 * xx * hh), 0.1)
# Q10 unit circle, speed 2, above x-axis: dx/dt = -2 sqrt(1-x^2)
phi = 1.1
check("9E Q10a at phi=1.1", -2 * sin(phi), -2 * sqrt(1 - cos(phi) ** 2))
check("9E Q10b at x=0", -2 * sqrt(1 - 0), -2)
# Q11: a = 2CV^2/L^2 ; passing speed V(1+2C/L); d: V=90, limit 100, C=50
Cc, Vv, Ll = 50.0, 90.0, None
Ll = 2 * Cc / (100 / Vv - 1)
check("9E Q11d L", Ll, 900, 1e-6)
check("9E Q11d distance before lane", Ll + Cc, 950, 1e-6)
# check a: car from rest-relative frame: s = C + L in time L/V with initial V
Cc, Vv, Ll = 7.0, 3.0, 11.0
T = Ll / Vv
acc = 2 * (Cc + Ll - Vv * T) / T ** 2
check("9E Q11a acceleration", acc, 2 * Cc * Vv ** 2 / Ll ** 2)
check("9E Q11b passing speed", Vv + acc * T, Vv * (1 + 2 * Cc / Ll))
# Q12 r = 2, x = 1, dx/dt = -sqrt3
rr, xx = 2.0, 1.0
th = atan(sqrt(rr * rr - xx * xx) / xx)
dAdth = rr * rr * (1 - cos(2 * th))
dthdx = -1 / sqrt(rr * rr - xx * xx)
check("9E Q12d", dAdth * dthdx * (-sqrt(3)), 6)
# Q13
xq = 100 * tan(pi / 6) / (tan(pi / 4) - tan(pi / 6))
check("9E Q13c x", xq, 50 * (sqrt(3) + 1))
check("9E Q13c h", xq * tan(pi / 4), 50 * (sqrt(3) + 1))
ad = 5 / 36 * (sqrt(3) - 1)
bd = 5 / 18 * (sqrt(3) - 1)
a, b = pi / 6, pi / 4
dxdt = (ad * (xq + 100) / cos(a) ** 2 - bd * xq / cos(b) ** 2) / (tan(b) - tan(a))
check("9E Q13d dx/dt", dxdt, -500 / 9)
check("9E Q13d speed km/h", abs(dxdt) * 3.6, 200)

# =================== 10A lesson ===================
check("10A C1 demo a(i) x", 20 * cos(radians(30)), 10 * sqrt(3))
check("10A C1 demo a(i) y", 20 * sin(radians(30)), 10)
check("10A C1 demo a(ii) x", 20 * cos(radians(45)), 10 * sqrt(2))
check("10A C1 demo b(i) v", sqrt(36 + 64), 10)
check("10A C1 demo b(i) angle", round(degrees(atan(8 / 6))), 53)
check("10A C1 demo b(ii) v", sqrt(144 + 25), 13)
check("10A C1 demo b(ii) angle", round(degrees(atan(-5 / 12))), -23)
check("10A C1 turn a(i) y", 16 * sin(radians(60)), 8 * sqrt(3))
check("10A C1 turn a(ii) x", 16 * cos(radians(30)), 8 * sqrt(3))
check("10A C1 turn b(i)", sqrt(25 + 144), 13)
check("10A C1 turn b(i) angle", round(degrees(atan(12 / 5))), 67)
check("10A C1 turn b(ii)", sqrt(49 + 49), 7 * sqrt(2))
check("10A C1 turn b(ii) angle", degrees(atan(-1)), -45)
check("10A WE1 a(i) y", 12 * sin(radians(60)), 6 * sqrt(3))
check("10A WE1 b(i) angle", round(degrees(atan(3 / 4))), 37)
check("10A WE1 b(ii) v", sqrt(29), sqrt(29))
check("10A WE1 b(ii) angle", round(degrees(atan(-2 / 5))), -22)
# C2 demo: 30 m/s at 30 deg from 20 m platform
u, w = 30 * cos(radians(30)), 30 * sin(radians(30))
check("10A C2 demo top time", w / 10, 1.5)
check("10A C2 demo top height", w * w / 20, 11.25)
t = max(roots(-5, w, 20))
check("10A C2 demo flight time", t, 4)
check("10A C2 demo range", u * t, 60 * sqrt(3))
check("10A C2 demo range ~103.9", u * t, 103.9, 0.05)
vy = w - 10 * t
check("10A C2 demo impact vy", vy, -25)
check("10A C2 demo impact speed", sqrt(u * u + vy * vy), 10 * sqrt(13))
check("10A C2 demo impact speed ~36.1", sqrt(u * u + vy * vy), 36.1, 0.05)
check("10A C2 demo impact angle", round(degrees(atan(-vy / u))), 44)
u, w = 20 * cos(radians(30)), 20 * sin(radians(30))
check("10A C2 turn height", w * w / 20, 5)
check("10A C2 turn flight", 2 * w / 10, 2)
check("10A C2 turn range", u * 2 * w / 10, 20 * sqrt(3))
# WE2 = textbook Example 3
u, w = 40 * cos(radians(30)), 20
check("10A WE2 top time", w / 10, 2)
check("10A WE2 top height", -5 * 4 + 20 * 2, 20)
check("10A WE2 top x", u * 2, 40 * sqrt(3))
t = max(roots(-5, 20, 25))
check("10A WE2 flight", t, 5)
check("10A WE2 range", u * t, 100 * sqrt(3))
vy = -10 * t + 20
check("10A WE2 impact speed", sqrt(u * u + vy * vy), 10 * sqrt(21))
check_dm("10A WE2 impact angle", degrees(atan(-vy / u)), 40, 54)
# C3 demo: 50 m/s, target (200, 40)
T1, T2 = roots(2, -5, 3)
check("10A C3 demo tan roots", max(T1, T2), 1.5)
check("10A C3 demo tan roots", min(T1, T2), 1)
check_dm("10A C3 demo angle", degrees(atan(1.5)), 56, 19)
for T in (1, 1.5):  # verify the target is hit
    a = atan(T)
    t = 200 / (50 * cos(a))
    check(f"10A C3 demo hits target, tan={T}", -5 * t * t + 50 * t * sin(a), 40, 1e-9)
check("10A C3 demo flight 45", 4 / cos(radians(45)), 4 * sqrt(2))
check("10A C3 demo flight 45 ~5.66", 4 * sqrt(2), 5.66, 0.005)
check("10A C3 demo flight tan 1.5", 4 / cos(atan(1.5)), 2 * sqrt(13))
check("10A C3 demo flight ~7.21", 2 * sqrt(13), 7.21, 0.005)
for T in (1, 3):
    a = atan(T)
    t = 80 / (40 * cos(a))
    check(f"10A C3 turn hits target, tan={T}", -5 * t * t + 40 * t * sin(a), 40, 1e-9)
check_dm("10A C3 turn angle", degrees(atan(3)), 71, 34)
# WE3 = textbook Example 4: 200 m/s, F (2000, 1000)
for T in (1, 3):
    a = atan(T)
    t = 2000 / (200 * cos(a))
    check(f"10A WE3 hits fortress, tan={T}", -5 * t * t + 200 * t * sin(a), 1000, 1e-6)
check_dm("10A WE3 a high angle", degrees(atan(3)), 71, 34)
check_dm("10A WE3 b OF inclination", degrees(atan(0.5)), 26, 34)
check_dm("10A WE3 b low shot to OF", 45 - degrees(atan(0.5)), 18, 26)
check_dm("10A WE3 b high shot to vertical", 90 - degrees(atan(3)), 18, 26)
check("10A WE3 c flight 45", 10 / cos(radians(45)), 10 * sqrt(2))
check("10A WE3 c vy 45", -10 * 10 * sqrt(2) + 200 * sin(radians(45)), 0, 1e-9)
check("10A WE3 c speed 45", 200 * cos(radians(45)), 100 * sqrt(2))
a = atan(3)
t = 10 / cos(a)
check("10A WE3 c flight tan3", t, 10 * sqrt(10))
vx, vy = 200 * cos(a), -10 * t + 200 * sin(a)
check("10A WE3 c vy tan3", vy, -40 * sqrt(10))
check("10A WE3 c vx tan3", vx, 20 * sqrt(10))
check("10A WE3 c speed tan3", sqrt(vx * vx + vy * vy), 100 * sqrt(2))
check_dm("10A WE3 c angle tan3 (below)", -degrees(atan(vy / vx)), 63, 26)

# =================== Exercise 10A (g = 10) ===================
g = 10
# Q1 30sqrt2 at 45: xdot = 30, ydot0 = 30
check("10A Q1c", 2 * 30 / g, 6)
check("10A Q1d", 30 * 6, 180)
check("10A Q1e", 30 / g, 3)
check("10A Q1f", 30 * 30 / (2 * g), 45)
check("10A Q1a xdot", 30 * sqrt(2) * cos(radians(45)), 30)
check("10A Q2a xdot", 40 * cos(radians(30)), 20 * sqrt(3))
check("10A Q2c(i)", 2 * 20 / g, 4)
check("10A Q2c(ii)", 20 * sqrt(3) * 4, 80 * sqrt(3))
check("10A Q2c(iii)", 400 / 20, 20)
x1, y1 = 10, -5 + 10 * sqrt(3)
check("10A Q3c(i)", sqrt(x1 * x1 + y1 * y1), 15.9, 0.05)
check("10A Q3c(ii)", sqrt(10 ** 2 + (-10 + 10 * sqrt(3)) ** 2), 12.4, 0.05)
check("10A Q4a xdot", 60 * 3 / 5, 36)
check("10A Q4a ydot0", 60 * 4 / 5, 48)
check("10A Q4c", sqrt((36 * 3) ** 2 + (-45 + 48 * 3) ** 2), 146.5, 0.05)
vx, vy = 36, -30 + 48
check("10A Q4d speed", sqrt(vx * vx + vy * vy), 18 * sqrt(5))
check("10A Q4d angle", vy / vx, 0.5)
check("10A Q5c(i)", sqrt(64 + 36), 10)
check("10A Q5c(ii) x", 16, 16)
check("10A Q5c(ii) y", 12 - 20, -8)
tt = 6 / 10
check("10A Q5c(iii) x", 8 * tt, 4.8)
check("10A Q5c(iii) y", 6 * tt - 5 * tt * tt, 1.8)
check("10A Q6b speed", sqrt(40 ** 2 + 25 ** 2), 5 * sqrt(89))
check("10A Q6b angle", round(degrees(atan(25 / 40))), 32)
check("10A Q7a Vcos", 8 / 2, 4)
check("10A Q7a Vsin", (-12 + 20) / 2, 4)
check("10A Q7b x", 4 * 0.5, 2)
check("10A Q7b y", 4 * 0.5 - 5 * 0.25, 0.75)
check("10A Q8a Vcos", 30 / 2, 15)
check("10A Q8a Vsin", (30 + 20) / 2, 25)
check("10A Q8b V", sqrt(15 ** 2 + 25 ** 2), 5 * sqrt(34))
t = max(roots(-5, -6, 11))
check("10A Q9c", t, 1)
check("10A Q9d", 6 * sqrt(3) * t, 10.4, 0.05)
check("10A Q9e", (10 * t + 6) / (6 * sqrt(3)), 8 * sqrt(3) / 9)
u = 6 * cos(radians(45))
t = max(roots(-5, u, 2))
check("10A Q10a", t, 1.19, 0.005)
check("10A Q10b", u * t, 5.03, 0.005)
a = radians(36)
V = sqrt(5 * 400 / (cos(a) ** 2 * (20 * tan(a) - 10)))
check("10A Q11", round(V), 26)
a = asin(sqrt(15) / 10)
check("10A Q12 greatest height", (20 * sin(a)) ** 2 / (2 * g), 3)
# Q13: P1 at time t, P2 at time t-2
t = 2 * 60 / (60 - 20)
check("10A Q13 x match time", t, 3)
check("10A Q13 y P1", 30 * t - 5 * t * t, 45)
check("10A Q13 y P2", 50 * (t - 2) - 5 * (t - 2) ** 2, 45)
check("10A Q13 x", 20 * t, 60)
T1, T2 = roots(1, -8, 7)
check("10A Q14c", degrees(atan(min(T1, T2))), 45)
check_dm("10A Q14c", degrees(atan(max(T1, T2))), 81, 52)
for T in (1, 7):
    th = atan(T)
    t = 20 / (20 * sqrt(2) * cos(th))
    check(f"10A Q14 passes (20,15), tan={T}", 20 * sqrt(2) * t * sin(th) - 5 * t * t, 15, 1e-9)
# Q15 50 m/s through (100, 25)
for T, tP, ang in ((0.5, sqrt(5), 0.0), (4.5, sqrt(85), 76.0)):
    a = atan(T)
    t = 100 / (50 * cos(a))
    check(f"10A Q15 passes P, tan={T}", -5 * t * t + 50 * t * sin(a), 25, 1e-9)
    check(f"10A Q15b(i) tan={T}", t, tP)
    vx, vy = 50 * cos(a), 50 * sin(a) - 10 * t
    check(f"10A Q15b(ii) speed tan={T}", sqrt(vx * vx + vy * vy), 20 * sqrt(5))
    check(f"10A Q15b(ii) speed ~44.7 tan={T}", sqrt(vx * vx + vy * vy), 44.7, 0.05)
    check(f"10A Q15b(ii) angle below tan={T}", round(-degrees(atan(vy / vx)), 1), ang, 1e-9)
# Q16b: range = 5 * height  ->  tan = 4/5
th = atan(4 / 5)
check("10A Q16b", sin(2 * th) / g, 5 * sin(th) ** 2 / (2 * g))
# Q17: tunnel 2 m: range = sqrt(16/g (V^2 - 4g)); check with V = 13, g = 9.8
V, gg = 13.0, 9.8
s2 = 2 * 2 * gg / V ** 2                      # sin^2 from V^2 sin^2/(2g) = 2
th = asin(sqrt(s2))
check("10A Q17 range formula", V * V * sin(2 * th) / gg, sqrt(16 / gg * (V * V - 4 * gg)))
# Q18: b times, c theta = 60
V, th, gg = 17.0, radians(50), 9.8
h = (V * sin(th)) ** 2 / (2 * gg)
for k in (1, -1):
    t = (sqrt(2) + k) * sqrt(h) / sqrt(gg)
    check(f"10A Q18b height h/2 at t (k={k})", V * t * sin(th) - gg * t * t / 2, h / 2, 1e-9)
th = radians(60)
h = (V * sin(th)) ** 2 / (2 * gg)
vtop = V * cos(th)
vhalf = sqrt(V * V - 2 * gg * (h / 2))           # energy: v^2 = V^2 - 2g(height)
check("10A Q18c ratio^2", (vhalf / vtop) ** 2, 5 / 2)

# =================== 10B lesson ===================
check("10B C1 demo range", (4 / 3) * 180, 240)
check("10B C1 demo height", -(120 ** 2) / 180 + 4 / 3 * 120, 80)
check_dm("10B C1 demo angle", degrees(atan(4 / 3)), 53, 8)
check("10B C1 turn range", 0.75 * 80, 60)
check("10B C1 turn height", -(30 ** 2) / 80 + 0.75 * 30, 11.25)
check_dm("10B C1 turn angle", degrees(atan(0.75)), 36, 52)
# WE1: 20 m/s at 60
check("10B WE1 b range", sqrt(3) * 20, 20 * sqrt(3))
check("10B WE1 b range ~34.6", 20 * sqrt(3), 34.6, 0.05)
check("10B WE1 c slope", -15 * sqrt(3) / 10 + sqrt(3), -sqrt(3) / 2)
check_dm("10B WE1 c angle below", degrees(atan(sqrt(3) / 2)), 40, 54)
# C2
check("10B C2 demo sin2a", 45 / 90, 0.5)
check("10B C2 demo max range", 900 / 10, 90)
check("10B C2 turn sin2a", 20 * sqrt(3) / 40, sqrt(3) / 2)
check("10B C2 turn heights 30", 400 * sin(radians(30)) ** 2 / 20, 5)
check("10B C2 turn heights 60", 400 * sin(radians(60)) ** 2 / 20, 15)
# C3 demo V = 20: y = xT - x^2(1+T^2)/80
check("10B C3 demo a coefficient", 10 / (2 * 400), 1 / 80)
T1, T2 = roots(1, -4, 2)
for T in (T1, T2):
    check(f"10B C3 demo passes (20,5) T={T:.3f}", 20 * T - 400 * (1 + T * T) / 80, 5, 1e-9)
check("10B C3 demo angle hi", round(degrees(atan(T1))), 74)
check("10B C3 demo angle lo", round(degrees(atan(T2))), 30)
check("10B C3 demo (40,10) no roots", roots(2, -4, 3) is None, True)
check("10B C3 turn coefficient", 10 / (2 * 900), 1 / 180)
T1, T2 = roots(1, -6, 3)
for T in (T1, T2):
    check(f"10B C3 turn passes (30,10) T={T:.3f}", 30 * T - 900 * (1 + T * T) / 180, 10, 1e-9)
check("10B C3 turn angle hi", round(degrees(atan(T1))), 80)
check("10B C3 turn angle lo", round(degrees(atan(T2))), 29)

# =================== Exercise 10B ===================
y = lambda x: -5 / 324 * x * x + 4 / 3 * x
check("10B Q1a", y(12), 13.8, 0.05)
r1, r2 = roots(5 / 324, -4 / 3, 19)
check("10B Q1b small", min(r1, r2), 18, 1e-9)
check("10B Q1b large", max(r1, r2), 68.4, 0.05)
dy = lambda x: -10 / 324 * x + 4 / 3
check("10B Q1c coefficient", 10 / 324, 5 / 162)
check("10B Q1c(ii)", dy(18), 7 / 9)
check("10B Q1c(iii)", dy(54), -1 / 3)
check("10B Q2a coefficient", 5 / 48 ** 2, 5 / 2304)
check("10B Q2a coefficient x", 20 / 48, 5 / 12)
R = (5 / 12) / (5 / 2304)
check("10B Q2b(i)", R, 192)
check("10B Q2b(ii)", -5 / 2304 * 96 ** 2 + 5 / 12 * 96, 20)
check("10B Q2b(iii)", degrees(atan(5 / 12)), 22.6, 0.05)
check("10B Q2b(iv) below", round(-degrees(atan(-10 / 2304 * 120 + 5 / 12))), 6)
check("10B Q3a", sqrt(9 + 1), sqrt(10))
yq = lambda x: (3 * x - 5 * x * x) / 9
check("10B Q3c from x=3t,y=t-5t^2 at t=0.7", yq(2.1), 0.7 - 5 * 0.49)
check("10B Q3d(i)", degrees(atan(1 / 3 - 10 * 0.15 / 9)), 9.5, 0.05)
check("10B Q3d(ii) below", -degrees(atan((1 - 10 * 0.15) / 3)), 9.5, 0.05)
check("10B Q4a coefficient", 5 / 25, 1 / 5)
check("10B Q4b", sqrt(20 * 5), 10)
check("10B Q4c below", round(degrees(atan(2 * 10 / 5))), 76)
check("10B Q5a xdot", 24 * cos(radians(30)), 12 * sqrt(3))
check("10B Q5a ydot0", 24 * sin(radians(30)), 12)
check("10B Q5b coefficient", 5 / (12 * sqrt(3)) ** 2, 5 / 432)
D = max(roots(5, -144 * sqrt(3), -2592))
check("10B Q5c D on path y=-6", D / sqrt(3) - 5 / 432 * D * D, -6, 1e-9)
check("10B Q5d", D, 58.7, 0.05)
a = radians(27)
V2 = 5 * 35 ** 2 / (cos(a) ** 2 * (60 - 35 * tan(a)))
check("10B Q6b(i)", sqrt(V2), 13.5, 0.05)
check("10B Q6b(ii) below", round(degrees(atan(tan(a) + 10 * 35 / (V2 * cos(a) ** 2)))), 71)
s = 75 * 10 / 900
check("10B Q7b low", degrees(asin(s)) / 2, 28.2, 0.05)
check("10B Q7b high", 90 - degrees(asin(s)) / 2, 61.8, 0.05)
check("10B Q8b", degrees(asin(sqrt(15 * 20 / 400))), 60)
# Q8a vertex check with V=20, th=50 deg
V, th = 20.0, radians(50)
xv = V * V * sin(2 * th) / (2 * g)
check("10B Q8a vertex slope 0", tan(th) - g * xv / (V * V * cos(th) ** 2), 0, 1e-9)
check("10B Q8a vertex y", xv * tan(th) - g * xv * xv / (2 * V * V * cos(th) ** 2), V * V * sin(th) ** 2 / (2 * g))
T1, T2 = roots(10 * 3000 ** 2, -2 * 3000 * 200 ** 2, 2 * 500 * 200 ** 2 + 10 * 3000 ** 2)
check("10B Q9b root 1", T1, (4 + sqrt(3)) / 3)
check("10B Q9b root 2", T2, (4 - sqrt(3)) / 3)
check_dm("10B Q9b angle 1", degrees(atan(T1)), 62, 22)
check_dm("10B Q9b angle 2", degrees(atan(T2)), 37, 5)
check("10B Q10a coefficient", 10 / (2 * 34 ** 2), 5 / 1156)
for T in (8 / 15, 538 / 75):
    check(f"10B Q10b passes (30,11) T={T:.4f}", 30 * T - 5 * 900 * (1 + T * T) / 1156, 11, 1e-9)
# Q11c: tan th = 1 - 30k = 60k - 1, k = g cos th / V^2  -> k = 1/45, tan = 1/3
k = 2 / 90
check("10B Q11c tan", 1 - 30 * k, 1 / 3)
th = atan(1 / 3)
V2 = g * cos(th) / k
for d, sgn in ((60, -1), (30, 1)):
    X, Y = d * cos(th), sgn * d * sin(th)
    check(f"10B Q11c point {d} m on path", X - g * X * X / V2, Y, 1e-9)
R = max(roots(1, -16, -36))
check("10B Q12c(ii)", R, 18)
r1, r2 = roots(1, -R, 4 * R)
check("10B Q12c points 6 apart", abs(r1 - r2), 6, 1e-9)
check("10B Q12c height 4", r1 * (1 - r1 / R), 4, 1e-9)

# =================== Chapter review ===================
u, w = 60 * cos(radians(40)), 60 * sin(radians(40))
t = 2 * w / g
check("Rev Q1c(i)", t, 7.7, 0.05)
check("Rev Q1c(ii)", u * t, 354.5, 0.05)
check("Rev Q1c(iii)", w * w / (2 * g), 74.4, 0.05)
u, w = 15, 15 * sqrt(3)
check("Rev Q2a", w * w / 20, 33.75)
t = max(roots(-5, w, 40))
check("Rev Q2b", u * t, 96.58, 0.005)
check("Rev Q2c", sqrt(30 ** 2 + 2 * g * 40), 41.23, 0.005)
check("Rev Q3a xdot", 25 * 3 / 5, 15)
check("Rev Q3a ydot0", 25 * 4 / 5, 20)
check("Rev Q3c", sqrt(15 ** 2 + 15 ** 2), 15 * sqrt(2))
check("Rev Q3d speed", sqrt(15 ** 2 + 10 ** 2), 5 * sqrt(13))
check("Rev Q3d angle", 10 / 15, 2 / 3)
check("Rev Q3e", (2 * 15 * 20 / g) / (400 / 20), 3)
y = lambda x: x - x * x / 10
check("Rev Q4a xdot", 10 * cos(radians(45)), 5 * sqrt(2))
check("Rev Q4b range", 10, max(roots(-0.1, 1, 0)))
check("Rev Q4b height", y(5), 2.5)
check("Rev Q4c(i)", y(8), 1.6)
check("Rev Q4c(ii) below", -(1 - 8 / 5), 3 / 5)
check("Rev Q4d(i)", min(roots(1, -10, 21)), 3)
check("Rev Q4d(ii)", 1 - 3 / 5, 2 / 5)
check("Rev Q5c(i)", sqrt(24 ** 2 + 18 ** 2), 30)
check("Rev Q5c(ii) y", 18 * 4 - 5 * 16, -8)
check("Rev Q5c(ii) x", 24 * 4, 96)
check("Rev Q5c(iii) x", 24 * 1.8, 43.2)
check("Rev Q5c(iii) y", 18 * 1.8 - 5 * 1.8 ** 2, 16.2)
ux, uy = 24 * sqrt(5) / 2, (28 + 20) / 2
check("Rev Q6a x", ux, 12 * sqrt(5))
check("Rev Q6a y", uy, 24)
check("Rev Q6b x", 3 * ux, 36 * sqrt(5))
check("Rev Q6b y", 3 * uy - 45, 27)
check("Rev Q6c ydot", uy - 30, -6)
ux, uy = 108 / 3, 3 * g / 2
check("Rev Q7a V", sqrt(ux * ux + uy * uy), 39)
check("Rev Q7a tan", uy / ux, 5 / 12)
check("Rev Q7b", uy * uy / 20, 11.25)
ux, uy = 5 / sqrt(5), 10 / sqrt(5)
check("Rev Q8a x", ux, sqrt(5))
check("Rev Q8a y", uy, 2 * sqrt(5))
check("Rev Q8d", uy * uy / 20, 1)
check("Rev Q8e flight", 2 * uy / g, 2 / 5 * sqrt(5))
check("Rev Q8c flight < 1", 2 * uy / g < 1, True)
check("Rev Q8e distance", ux * 2 * uy / g, 2)
check("Rev Q8f ydot", uy - g * 2 * uy / g, -2 * sqrt(5))
check("Rev Q8f speed", sqrt(ux * ux + uy * uy), 5)
check("Rev Q8g coefficient", 5 / ux ** 2, 1)
a = radians(26)
V = sqrt(5 * 900 / (cos(a) ** 2 * (30 * tan(a) - 12)))
check("Rev Q9", round(V), 46)
# Ch 9 review Q18: ladder 500 cm, dx/dt = 5 cm/s, x = 140 cm
yl = sqrt(500 ** 2 - 140 ** 2)
check("Rev Q10a", -140 / yl * 5, -35 / 24)
check("Rev Q10b", -5 / (500 * (yl / 500)), -1 / 96)

n_ok = sum(results)
print(f"\n{n_ok}/{len(results)} OK, {len(results) - n_ok} MISMATCH")
