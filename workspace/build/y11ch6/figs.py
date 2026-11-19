import os, sys
from math import sin, cos, tan, atan, atan2, pi, sqrt, radians, degrees, acos, asin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from svg_overlap import text_width, check_string

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    svg = g.svg()
    for p in check_string(svg):                 # labels crossed, overlapping or clipped (see the report)
        print(f"{name}: {p}")
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)


class Fig:
    """Plain geometry diagram in pixel coordinates (y downwards)."""

    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def line(self, x1, y1, x2, y2, color="ink", width=1.6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ACC[color]}" stroke-width="{width}"{d} stroke-linecap="round"/>')
        return self

    def arrow(self, x1, y1, x2, y2, color="ink", width=1.6, head=7, dash=None):
        self.line(x1, y1, x2, y2, color, width, dash)
        a = atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head * cos(a - 0.4), y2 - head * sin(a - 0.4))
        p2 = (x2 - head * cos(a + 0.4), y2 - head * sin(a + 0.4))
        self.items.append(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} z" fill="{ACC[color]}"/>')
        return self

    def dim(self, x1, y1, x2, y2, color="faint"):
        """Double-headed dimension arrow."""
        self.arrow(x1, y1, x2, y2, color, 1.1, 6)
        return self.arrow(x2, y2, x1, y1, color, 1.1, 6)

    def poly(self, pts, color="blue", opacity=0.18, stroke="ink", width=1.6, closed=True):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        fill = ACC[color] if color else "none"
        self.items.append(f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" stroke="{ACC[stroke]}" stroke-width="{width}" stroke-linejoin="round"/>')
        return self

    def path(self, d, color="blue", width=2.2, dash=None, fill="none", opacity=1):
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        f = ACC[fill] if fill != "none" else "none"
        self.items.append(f'<path d="{d}" fill="{f}" fill-opacity="{opacity}" stroke="{ACC[color]}" stroke-width="{width}"{ds} stroke-linejoin="round"/>')
        return self

    def arc(self, cx, cy, r, a0, a1, color="faint", width=1.3):
        """Arc from angle a0 to a1 (degrees, anticlockwise from +x on screen, i.e. upwards)."""
        x0, y0 = cx + r * cos(radians(a0)), cy - r * sin(radians(a0))
        x1, y1 = cx + r * cos(radians(a1)), cy - r * sin(radians(a1))
        large = 1 if abs(a1 - a0) > 180 else 0
        sweep = 0 if a1 > a0 else 1
        self.items.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"/>')
        return self

    def right(self, x, y, dx, dy, s=8):
        """Right-angle mark at (x, y) with legs towards (dx, dy) signs."""
        self.items.append(f'<path d="M{x + dx*s:.1f},{y:.1f} L{x + dx*s:.1f},{y + dy*s:.1f} L{x:.1f},{y + dy*s:.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
        return self

    def text(self, x, y, s, anchor="middle", size=12, color="ink", italic=False, weight=500):
        self.items.append(_txt(x, y, s, anchor, size=size, color=ACC[color], italic=italic, weight=weight))
        return self

    def ring(self, cx, cy, r, width=1.5):
        """Open circle drawn as two arcs (int3/place.py does the same), so that svg_overlap tests labels
        against the ring itself rather than against the circle's whole bounding box."""
        self.items.append(f'<path d="M{cx - r:.1f},{cy:.1f} A{r:g},{r:g} 0 1 0 {cx + r:.1f},{cy:.1f} '
                          f'A{r:g},{r:g} 0 1 0 {cx - r:.1f},{cy:.1f} Z" fill="none" stroke="{INK}" stroke-width="{width}"/>')
        return self

    def dot(self, x, y, r=3, color="ink"):
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{ACC[color]}"/>')
        return self

    def raw(self, s):
        self.items.append(s)
        return self

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="Inter, Arial, sans-serif">' + "".join(self.items) + "</svg>")



def plain(f, x, y, s, anchor="middle", size=11.5, italic=False):
    st = ' font-style="italic"' if italic else ''
    f.raw(f'<text x="{x:.1f}" y="{y + size*0.35:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{INK}" font-weight="500"{st}>{s}</text>')


def quad(name, rays, arcs=(), w=190, h=150, r=None):
    """Quadrant diagram. rays: [(angle_deg, label)]; arcs: [(angle_deg, label)] mark the related acute
    angle between the ray and the nearer x-axis."""
    f = Fig(w, h)
    cx, cy = w / 2, h / 2
    r = r or min(w, h) / 2 - 22
    f.line(cx - r - 10, cy, cx + r + 10, cy, "ink", 1.2).line(cx, cy + r + 8, cx, cy - r - 8, "ink", 1.2)
    for a, lab in rays:
        ex, ey = cx + r * cos(radians(a)), cy - r * sin(radians(a))
        f.arrow(cx, cy, ex, ey, "blue", 2)
        if lab:
            c, s = cos(radians(a)), sin(radians(a))
            plain(f, ex + 6 * c + (4 if c >= 0 else -4), ey - 9 * s - (0 if abs(s) > 0.3 else 8), lab,
                  "start" if c >= 0 else "end", size=11)
    for a, lab in arcs:
        ref = 0 if cos(radians(a)) >= 0 else 180
        aa = a % 360
        if ref == 0 and aa > 180: aa -= 360
        lo, hi = sorted([ref if not (ref == 0 and aa < 0) else 0, aa])
        if ref == 180: lo, hi = sorted([180, aa])
        f.arc(cx, cy, 20, lo, hi, "faint", 1.2)
        mid = radians((lo + hi) / 2)
        rr = max(38, (text_width(lab, 11) / 2 + 5) / sin(radians(hi - lo) / 2))
        plain(f, cx + rr * cos(mid), cy - rr * sin(mid), lab, size=11)
    save(name, f)


def tri(name, pts, vlab=None, slab=None, alab=None, right=(), W=188, H=150, pad=30, extra=(), arcs=True,
        aoff=None, soff=None, fill=True, labels=(), rights=(), aout=(), marks=()):
    """Triangle (or polygon) from math coordinates (y up), scaled to fit W x H.
    vlab {i: 'A'}; slab {(i, j): '12'}; alab {i: '30°'}; right [i]; extra [((x1,y1),(x2,y2),dash)]."""
    vlab, slab, alab = vlab or {}, slab or {}, alab or {}
    aoff, soff = aoff or {}, soff or {}
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for e in extra:
        xs += [e[0][0], e[1][0]]; ys += [e[0][1], e[1][1]]
    sx = (W - 2 * pad) / max(1e-9, max(xs) - min(xs)); sy = (H - 2 * pad) / max(1e-9, max(ys) - min(ys))
    k = min(sx, sy)
    w = (max(xs) - min(xs)) * k + 2 * pad; h = (max(ys) - min(ys)) * k + 2 * pad
    P = lambda p: (pad + (p[0] - min(xs)) * k, pad + (max(ys) - p[1]) * k)
    Q = [P(p) for p in pts]
    f = Fig(round(w), round(h))
    n = len(Q)
    gx, gy = sum(q[0] for q in Q) / n, sum(q[1] for q in Q) / n
    f.poly(Q, color="blue" if fill else None, opacity=0.08, stroke="ink", width=1.5)
    for e in extra:
        a, b = P(e[0]), P(e[1])
        f.line(a[0], a[1], b[0], b[1], "ink" if not e[2] else "faint", 1.2 if e[2] else 1.5, e[2] or None)
    for i in right:
        o = Q[i]; a = Q[(i - 1) % n]; b = Q[(i + 1) % n]
        ua = ((a[0] - o[0]), (a[1] - o[1])); la = sqrt(ua[0] ** 2 + ua[1] ** 2); ua = (ua[0] / la, ua[1] / la)
        ub = ((b[0] - o[0]), (b[1] - o[1])); lb = sqrt(ub[0] ** 2 + ub[1] ** 2); ub = (ub[0] / lb, ub[1] / lb)
        s = 8
        f.raw(f'<path d="M{o[0]+ua[0]*s:.1f},{o[1]+ua[1]*s:.1f} L{o[0]+(ua[0]+ub[0])*s:.1f},{o[1]+(ua[1]+ub[1])*s:.1f} L{o[0]+ub[0]*s:.1f},{o[1]+ub[1]*s:.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    for i, lab in vlab.items():
        o = Q[i]; dx, dy = o[0] - gx, o[1] - gy; l = sqrt(dx * dx + dy * dy) or 1
        tw = text_width(lab, 11.5)
        plain(f, o[0] + dx / l * (9 + tw / 2), o[1] + dy / l * 11, lab, italic=True)
    for (i, j), lab in slab.items():
        a, b = Q[i], Q[j]; mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx, ny = -(b[1] - a[1]), b[0] - a[0]; l = sqrt(nx * nx + ny * ny); nx, ny = nx / l, ny / l
        if nx * (mx - gx) + ny * (my - gy) < 0: nx, ny = -nx, -ny
        tw = text_width(lab, 11.5)
        d = soff.get((i, j), 0)
        dd = abs(nx) * tw / 2 + abs(ny) * 5.5 + 5 + d
        plain(f, mx + nx * dd, my + ny * dd, lab, italic=not any(ch.isdigit() for ch in lab))
    for i, lab in alab.items():
        o = Q[i]; a = Q[(i - 1) % n]; b = Q[(i + 1) % n]
        a1 = degrees(atan2(-(a[1] - o[1]), a[0] - o[0])); a2 = degrees(atan2(-(b[1] - o[1]), b[0] - o[0]))
        d = (a2 - a1) % 360
        if d > 180: a1, a2, d = a2, a1, 360 - d
        if arcs: f.arc(o[0], o[1], 13, a1, a1 + d, "faint", 1.2)
        mid = radians(a1 + d / 2)
        tw = text_width(lab, 11)
        rr = aoff.get(i) or max(26 + tw / 4, (tw / 2 + 7) / max(0.2, sin(radians(d / 2))))
        rr = min(rr, 60)
        if i in aout:
            mid += pi; rr = 14 + tw / 2
        plain(f, o[0] + rr * cos(mid), o[1] - rr * sin(mid), lab, size=11, italic=not any(ch.isdigit() for ch in lab))
    for (p, r_, a0, a1) in marks:
        q = P(p)
        f.arc(q[0], q[1], r_, a0, a1, "faint", 1.2)
    for (p, lab, dx, dy) in labels:
        q = P(p)
        plain(f, q[0] + dx, q[1] + dy, lab, size=11, italic=not any(ch.isdigit() for ch in lab) and len(lab) < 3)
    for (o, a, b) in rights:                      # right-angle mark at o between directions to a and b
        o, a, b = P(o), P(a), P(b)
        ua = (a[0] - o[0], a[1] - o[1]); la = sqrt(ua[0]**2 + ua[1]**2); ua = (ua[0]/la, ua[1]/la)
        ub = (b[0] - o[0], b[1] - o[1]); lb = sqrt(ub[0]**2 + ub[1]**2); ub = (ub[0]/lb, ub[1]/lb)
        f.raw(f'<path d="M{o[0]+ua[0]*7:.1f},{o[1]+ua[1]*7:.1f} L{o[0]+(ua[0]+ub[0])*7:.1f},{o[1]+(ua[1]+ub[1])*7:.1f} L{o[0]+ub[0]*7:.1f},{o[1]+ub[1]*7:.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    save(name, f)
    return f


def flipy(p): return [(x, -y) for x, y in p]
def flipx(p): return [(-x, y) for x, y in p]
def rot(p, d):
    c, s_ = cos(radians(d)), sin(radians(d))
    return [(x * c - y * s_, x * s_ + y * c) for x, y in p]


def solve_tri(a=None, b=None, c=None, A=None, B=None, C=None):
    """Coordinates of a triangle from three sides: A at origin, B on +x axis (c = AB), C above."""
    Ax, Bx = (0, 0), (c, 0)
    ang = A
    return [Ax, Bx, (b * cos(radians(ang)), b * sin(radians(ang)))]


def sas(b, A, c):
    """Vertices A, B, C with AB = c along the x-axis and AC = b at angle A."""
    return [(0, 0), (c, 0), (b * cos(radians(A)), b * sin(radians(A)))]


def asa(c, A, B):
    """AB = c, angles A and B: vertices A, B, C."""
    C = 180 - A - B
    b = c * sin(radians(B)) / sin(radians(C))
    return sas(b, A, c)


def sss(a, b, c):
    A = degrees(acos((b * b + c * c - a * a) / (2 * b * c)))
    return sas(b, A, c)


# ================= 6H =================
g = Graph(-60, 800, -1.25, 1.35, w=360, h=170, pad=(26, 30, 18, 26))
g.axes()
g.curve(lambda x: sin(radians(x)), x0=-30, x1=740)
g.hline(-1, x0=0, x1=630)
for v in (270, 630):
    g.vline(v, -1, 0)
g.xticks([(270, ""), (360, ""), (630, ""), (720, "")])
g.yticks([(1, ""), (-1, "")])
g.label(270, 0, "270°", dy=-11)
g.label(630, 0, "630°", dy=-11)
g.label(360, 0, "360°", dx=4, dy=13, anchor="start")
g.label(720, 0, "720°", dx=6, dy=13, anchor="start")
g.label(0, 1, "1", dx=-7, anchor="end")
g.label(0, -1, "−1", dx=-7, anchor="end")
save("h_ex16", g)

quad("h_ex17a", [(-150, "−150°"), (-30, "−30°")], [(-150, "30°"), (-30, "30°")])
quad("h_ex17b", [(108, "108°"), (-72, "288°")], [(108, "72°"), (-72, "72°")])
quad("h_ex19", [(60, "60°, 420°"), (240, "240°, 600°")], [(60, "60°"), (240, "60°")], w=230)
quad("h_ex20", [(120, "−240°"), (60, "60°")], [(120, "60°"), (60, "60°")])


# ================= 6I / 6J revision =================
D = "°"
tri("i1a", asa(10, 60, 50), slab={(0, 1): "10", (2, 0): "x"}, alab={2: "70°", 1: "50°"})
tri("i1c", flipy(asa(4, 85, 40)), slab={(0, 1): "4", (1, 2): "x"}, alab={0: "85°", 2: "55°"})
tri("i1e", asa(1, 71, 46), slab={(2, 0): "7", (1, 2): "x"}, alab={0: "71°", 1: "46°"})
tri("i3b", flipy(asa(10, 42.2, 52.8)), slab={(0, 1): "10", (0, 2): "8"}, alab={2: "85°", 1: "θ"})
tri("i3d", asa(6, 72, 88.4), slab={(0, 1): "6", (1, 2): "17"}, alab={0: "72°", 2: "θ"}, aoff={0: 31}, W=170, H=230)
tri("i3f", asa(16, 53, 84.74), slab={(0, 1): "16", (1, 2): "19"}, alab={0: "53°", 2: "θ"})
tri("i4a", sas(3, 50, 4), slab={(0, 1): "4 cm", (0, 2): "3 cm"}, alab={0: "50°"})
tri("i4b", rot(sas(5, 70, 8), -125), slab={(0, 1): "8 cm", (0, 2): "5 cm"}, alab={0: "70°"})
tri("i4c", flipy(sas(7, 115, 7)), slab={(0, 1): "7 cm", (0, 2): "7 cm"}, alab={0: "115°"})
for nm, ac in (("i7a", 9 * cos(radians(22)) - sqrt(25 - (9 * sin(radians(22))) ** 2)),
               ("i7b", 9 * cos(radians(22)) + sqrt(25 - (9 * sin(radians(22))) ** 2))):
    tri(nm, [(0, 0), (9 * cos(radians(22)), 9 * sin(radians(22))), (ac, 0)],
        slab={(0, 1): "9 cm", (1, 2): "5 cm"}, alab={0: "22°"}, W=190)
tri("i13a", sas(12, 30, 16), slab={(0, 2): "12 m", (0, 1): "x"}, alab={0: "30°"})
tri("i13c", rot(sas(9, 130, 36), -20), slab={(0, 2): "x", (0, 1): "36 m"}, alab={0: "130°"}, W=200, aout={0})
tri("i14a", sas(16, 30, 18), slab={(0, 2): "16 cm", (0, 1): "18 cm"}, alab={0: "θ"})
tri("i14c", rot(sas(12, 70, 10), 180), W=220, slab={(0, 2): "12 cm", (0, 1): "10 cm"}, alab={0: "θ"})
tri("i15a", asa(6 * sin(radians(75)) / sin(radians(45)), 60, 45), slab={(0, 2): "6", (1, 2): "x"}, alab={0: "60°", 1: "45°"})
tri("i15d", asa(6 * sin(radians(105)) / sin(radians(30)), 45, 30), slab={(0, 2): "6", (1, 2): "x"}, alab={0: "45°", 1: "30°"}, W=200)
# 6I Q17: mountain
Qp, X, Y = (150, 60), 260, 300                     # schematic (not to scale), as in the book
tri("i17", [(0, 0), Qp, (X, Y)], vlab={0: "P", 1: "Q", 2: "S"}, W=230, H=240,
    extra=[((0, 0), (X, 0), None), ((X, 0), (X, Y), None), (Qp, (X, Qp[1]), "4 3")],
    marks=[((0, 0), 24, 0, 49), (Qp, 24, 0, 65.4)],
    labels=[((X, 0), "M", 10, 4), ((X, Qp[1]), "R", 10, 0), ((0, 0), "42°", 12, -40), ((0, 0), "18°", 95, -9),
            (Qp, "54°", 34, -22), ((125, 50), "250 m", 0, -24)],
    rights=[((X, 0), (0, 0), (X, Y)), ((X, Qp[1]), Qp, (X, Y))], fill=False)
# 6I Q21
xa, ya = 4.0, 9.0; h = 4.0
tri("i21", [(0, 0), (ya, 0), (ya, h)], vlab={0: "A", 1: "C", 2: "D"}, slab={(1, 2): "h"}, right=[1], W=200,
    extra=[((xa, 0), (ya, h), None)], labels=[((xa, 0), "B", 0, 12), ((0, 0), "β", 34, -7), ((xa, 0), "α", 26, -7),
    ((xa / 2, 0), "x", 0, 12), ((ya / 2, 0), "y", 0, 26)], pad=36)
# 6J
tri("j1b", flipx(sas(5, 50, 6)), slab={(0, 1): "6", (0, 2): "5", (1, 2): "x"}, alab={0: "50°"})
tri("j1d", sas(10, 115, 8), slab={(0, 1): "8", (0, 2): "10", (1, 2): "x"}, alab={0: "115°"})
tri("j1f", rot(sas(13, 131, 14), 160), slab={(0, 1): "14", (0, 2): "13", (1, 2): "x"}, alab={0: "131°"}, aout={0})
tri("j2a", sss(2, 3, 3), slab={(0, 1): "3", (0, 2): "3", (1, 2): "2"}, alab={0: "θ"})
tri("j2c", rot(sss(10, 9, 7), 90), slab={(0, 1): "7", (0, 2): "9", (1, 2): "10"}, alab={0: "θ"})
tri("j2e", rot(sss(12, 6, 8), 200), slab={(0, 1): "8", (0, 2): "6", (1, 2): "12"}, alab={0: "θ"})
tri("j3a", sas(3, 60, 4), slab={(0, 1): "4", (0, 2): "3", (1, 2): "x"}, alab={0: "60°"})
tri("j3b", sas(2, 120, 1), slab={(0, 1): "1", (0, 2): "2", (1, 2): "x"}, alab={0: "120°"}, aout={0})
tri("j4a", flipx(sas(2, degrees(acos(0.25)), 3)), vlab={0: "A", 1: "B", 2: "C"}, slab={(0, 1): "3", (0, 2): "2", (1, 2): "a"})
tri("j5a", sss(7, 5, 6), slab={(0, 1): "6", (0, 2): "5", (1, 2): "7"})
tri("j5c", flipy(sss(5, 4, 4)), slab={(0, 1): "4", (0, 2): "4", (1, 2): "5"}, alab={0: "θ"})
A6 = (120 * cos(radians(18)), 120 * sin(radians(18))); B6 = (180 * cos(radians(-46)), 180 * sin(radians(-46)))
tri("j6", [(0, 0), A6, B6], vlab={0: "L", 1: "A", 2: "B"}, slab={(0, 1): "120 Nm", (0, 2): "180 Nm"}, W=180, H=190,
    extra=[((0, 0), (0, 60), "4 3")], labels=[((0, 60), "N", 0, -9)], fill=False)
Dp, Cp = (0, 0), (9, 0); Ap = (1.5, 3 * sin(radians(60))); Bp = (10.5, Ap[1]); Pp = (3, 0)
tri("j12", [Dp, Cp, Bp, Ap], vlab={0: "D", 1: "C", 2: "B", 3: "A"}, slab={(2, 3): "9 cm", (3, 0): "3 cm"},
    alab={0: "60°"}, aoff={0: 30}, W=250, extra=[(Ap, Pp, None), (Pp, Bp, None)],
    labels=[(Pp, "P", 0, 12), ((1.5, 0), "3 cm", 0, 12), (Pp, "x", 6, -16)])
Pt, Qt, Ft, Tt = (0, 0), (16, 0), (8, 4), (8, 13)
tri("j13", [Pt, Qt, Tt], vlab={0: "P", 1: "Q", 2: "T"}, slab={(0, 1): "63 m"}, W=212, H=210,
    extra=[(Pt, Ft, None), (Qt, Ft, None), (Ft, Tt, "4 3")],
    labels=[(Ft, "F", -12, -10), (Pt, "22°", 41, -36), (Qt, "27°", -41, -36), (Ft, "51°", 0, 16), ((8, 6.5), "x m", 15, 0)], fill=False)
xC = 3 * sqrt(3) + sqrt(7)
tri("j15", [(0, 0), (6, 0), (xC * cos(radians(-30)), xC * sin(radians(-30)))], vlab={0: "A", 1: "B", 2: "C"},
    slab={(0, 1): "6 cm", (1, 2): "4 cm", (0, 2): "x cm"}, alab={0: "30°"})
