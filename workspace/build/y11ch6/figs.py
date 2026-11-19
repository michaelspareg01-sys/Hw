import os, sys, re
from math import sin, cos, tan, atan, atan2, pi, sqrt, radians, degrees, acos, asin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from svg_overlap import text_width, check_string

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def _autofix(svg):
    """Nudge labels that are crossed, overlap or are clipped; then widen the frame for any clipping left."""
    texts = list(re.finditer(r'<text x="([-\d.]+)" y="([-\d.]+)"([^>]*)>([^<]*)</text>', svg))
    def probs(sv, lab):
        return [p for p in check_string(sv) if f"'{lab}'" in p]
    for m in texts:
        lab = m.group(4)
        lim = 16 if lab[-1:] in "°′θαβ" else 30
        offs = sorted(((dx, dy) for dx in range(-lim, lim + 1, 2) for dy in range(-lim, lim + 1, 2) if (dx, dy) != (0, 0)),
                      key=lambda o: o[0] ** 2 + o[1] ** 2)
        if not probs(svg, lab) or "/" in lab:
            continue
        x, y = float(m.group(1)), float(m.group(2))
        cur = f'<text x="{m.group(1)}" y="{m.group(2)}"{m.group(3)}>{lab}</text>'
        if cur not in svg: continue
        base = len(probs(svg, lab))
        for dx, dy in offs:
            cand = f'<text x="{x + dx:.1f}" y="{y + dy:.1f}"{m.group(3)}>{lab}</text>'
            t = svg.replace(cur, cand, 1)
            if not probs(t, lab) and len(check_string(t)) < len(check_string(svg)):
                svg = t; break
    return svg


def save(name, g):
    svg = _autofix(g.svg())
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


# ================= 6K =================
def uv(a): return (cos(radians(a)), sin(radians(a)))
def add(p, q, k=1): return (p[0] + k * q[0], p[1] + k * q[1])

tri("k1a", asa(10, 43, 57), slab={(0, 2): "x", (1, 2): "23"}, alab={0: "43°", 1: "57°"})
tri("k1b", [(-9.55, 9.55), (0, 0), (12.22, 12.22)], slab={(0, 1): "13.5", (1, 2): "x"}, alab={0: "52°"}, right=[1])
tri("k1c", sas(11, 62, 13), slab={(0, 1): "13", (0, 2): "11", (1, 2): "x"}, alab={0: "62°"})
tri("k1d", [(0, 0), (24 / tan(radians(41.5)), 0), (0, 24)], slab={(0, 2): "24", (1, 2): "x"}, alab={1: "41°30′"}, right=[0])
tri("k1e", [(-7.4, 0), (0, 0), (9.2 * cos(radians(82)), 9.2 * sin(radians(82)))], slab={(0, 1): "7.4", (1, 2): "9.2", (0, 2): "x"}, alab={1: "98°"})
tri("k1f", asa(10, 49, 77), slab={(0, 2): "x", (1, 2): "18"}, alab={0: "49°", 2: "54°"})
tri("k2a", sss(11, 10, 12), slab={(0, 1): "12", (0, 2): "10", (1, 2): "11"}, alab={0: "θ"})
tri("k2b", asa(8, 67, 58.1), slab={(0, 1): "8", (1, 2): "9"}, alab={0: "67°", 2: "θ"})
t2c = degrees(acos(13 / 17))
tri("k2c", [(0, 0), (17, 0), (13 * cos(radians(t2c)), 13 * sin(radians(t2c)))], slab={(0, 2): "13", (0, 1): "17"}, alab={0: "θ"}, right=[2])
tri("k2d", asa(10, 36.8, 116), slab={(0, 2): "10.8", (1, 2): "7.2"}, alab={0: "θ", 1: "116°"})
tri("k2e", [(0, 6.8), (8.6, 6.8), (8.6, 0)], slab={(0, 1): "8.6", (1, 2): "6.8"}, alab={2: "θ"}, right=[1])
tri("k2f", rot(sss(21, 19, 5), 100), slab={(0, 1): "5", (0, 2): "19", (1, 2): "21"}, alab={0: "θ"}, H=170)
tri("k3a", rot([(0, 0), (25.82, 0), (0, 7.89)], -55), slab={(1, 2): "27 cm", (0, 1): "x"}, alab={2: "73°"}, right=[0], W=200, H=200)
tri("k3b", [(0, 0), (40, 0), (40, 40 * tan(radians(35)))], slab={(0, 1): "40 cm", (1, 2): "x"}, alab={0: "35°"}, right=[1], W=230)
a3c = degrees(acos(11 / 14))
tri("k3c", [(0, 0), (14, 0), (11 * cos(radians(-a3c)), 11 * sin(radians(-a3c)))], slab={(0, 1): "14 cm", (0, 2): "11 cm"}, alab={1: "θ"}, right=[2], W=230)
tri("k3d", rot([(0, 0), (8, 0), (8, -15)], 25), slab={(0, 1): "8 cm", (1, 2): "15 cm", (0, 2): "17 cm"}, alab={0: "θ"}, right=[1], W=230, H=200)
Q4, R4, P4 = asa(40, 53, 55); T4 = (P4[0], 0)
tri("k4", [Q4, R4, P4], vlab={0: "Q", 1: "R", 2: "P"}, slab={(0, 1): "40 m"}, alab={0: "53°", 1: "55°"}, W=210,
    extra=[(P4, T4, None)], labels=[(T4, "T", 0, 13)], rights=[(T4, R4, P4)], soff={(0, 1): 8})
xB5 = 20 * tan(radians(68)) / (tan(radians(68)) - tan(radians(31))); yC5 = xB5 * tan(radians(31)); P5 = (20, 0)
tri("k5", [(0, 0), (xB5, 0), (xB5, yC5)], vlab={0: "A", 1: "B", 2: "C"}, alab={0: "31°"}, right=[1], W=300, H=200,
    extra=[(P5, (xB5, yC5), None)], labels=[(P5, "P", 0, 13), ((10, 0), "20 cm", 0, 26), (P5, "68°", 26, -16)], marks=[(P5, 14, 0, 68)], pad=34)
BD6 = sqrt(6.7 ** 2 + 8.3 ** 2 - 2 * 6.7 * 8.3 * cos(radians(101)))
aADB = degrees(asin(6.7 * sin(radians(101)) / BD6)); aCBD = degrees(asin(9.2 * sin(radians(73)) / BD6)); aBDC = 180 - 73 - aCBD
D6 = (0, 0); C6 = (9.2, 0); B6 = (BD6 * cos(radians(aBDC)), BD6 * sin(radians(aBDC))); A6p = (8.3 * cos(radians(aBDC + aADB)), 8.3 * sin(radians(aBDC + aADB)))
tri("k6", [D6, C6, B6, A6p], vlab={0: "D", 1: "C", 2: "B", 3: "A"}, slab={(2, 3): "6.7 cm", (3, 0): "8.3 cm", (0, 1): "9.2 cm"},
    alab={3: "101°", 1: "73°"}, extra=[(B6, D6, None)], W=200, H=180, pad=44)
a7 = degrees(acos(40 / 56))
tri("k7", [(0, 0), (7, 0), (4 * cos(radians(a7)), 4 * sin(radians(a7)))], vlab={0: "B", 1: "C", 2: "A"}, slab={(0, 1): "7 cm", (0, 2): "4 cm", (1, 2): "5 cm"})
P8 = (25 / tan(radians(72)), 0); X8 = (P8[0], 25); Z8 = (P8[0] + 25 / tan(radians(42)), 0)
tri("k8", [(0, 0), Z8, X8], vlab={0: "Y", 1: "Z", 2: "X"}, alab={0: "72°", 2: "66°"}, aoff={0: 30, 2: 34}, W=240, H=240,
    extra=[(X8, P8, None)], labels=[(P8, "P", 0, 13), ((P8[0], 12.5), "25 cm", 22, 0)], rights=[(P8, Z8, X8)])
Q10 = (53 * sin(radians(26)), 53 * cos(radians(26))); R10 = (Q10[0] + 78, Q10[1])
tri("k10", [(0, 0), Q10, R10], vlab={0: "P", 1: "Q", 2: "R"}, slab={(1, 2): "78 Nm"}, W=210, H=170,
    extra=[((0, 0), (0, 50), "4 3")], labels=[((0, 0), "26°", 14, -62), ((Q10[0] / 2, Q10[1] / 2), "53 Nm", 26, 8)], fill=False)
u11 = (sin(radians(7)), cos(radians(7)))
g1, g2 = 10 * sin(radians(126.02)) / sin(radians(7)), 10 * sin(radians(39.98)) / sin(radians(7))
B11a, B11b = (g1 * u11[0], g1 * u11[1]), (g2 * u11[0], g2 * u11[1])
tri("k11", [(0, 0), (0, 60), B11a], vlab={0: "G", 1: "H", 2: "B"}, slab={(0, 1): "60 m", (1, 2): "10 m"}, W=150, H=230, fill=False, pad=40,
    extra=[((0, 60), B11b, None)], labels=[(B11b, "B", 11, 2), ((0, 0), "7°", 8, -30)])
AB12 = 70 / sin(radians(20)) * sin(radians(15)) / sin(radians(95)); BQ12 = 70 / tan(radians(20))
xJ = AB12 / tan(radians(20))
tri("k12", [(0, 0), (BQ12, 0), (BQ12, 70), (0, AB12)], vlab={0: "B", 1: "Q", 2: "P", 3: "A"}, W=230, H=150, fill=False,
    extra=[((0, AB12), (BQ12, 70), None), ((0, 0), (BQ12, 70), None), ((0, AB12), (BQ12, AB12), "4 3")],
    labels=[((xJ, AB12), "J", -2, 12), ((BQ12, AB12), "K", -9, 11), ((0, 0), "20°", 62, -9), ((0, AB12), "5°", 46, -8), ((BQ12, 35), "70 m", 24, 0)], pad=42)
P13, Q13, B13, T13 = (0, 0), (15, -1), (8, 4), (8, 13)
tri("k13", [P13, Q13, T13], vlab={0: "P", 1: "Q", 2: "T"}, W=260, H=250, fill=False,
    extra=[(P13, B13, None), (Q13, B13, None), (B13, T13, "4 3"), (B13, (12, 8), "4 3")],
    labels=[(B13, "B", -12, -4), ((8, 8.5), "38 m", -18, 0), (P13, "26°", 37, -34), (Q13, "22°", -40, -41), (B13, "100°", 26, 3), ((12, 8), "N", 4, -8)])
A14, B14, D14, C14 = (0, 0), (14, -1), (6, 4), (6, 12)
tri("k14", [A14, B14, C14], vlab={0: "A", 1: "B", 2: "C"}, slab={(0, 1): "300 m"}, W=260, H=240, fill=False,
    extra=[(A14, D14, None), (B14, D14, "4 3"), (D14, C14, "4 3")],
    labels=[(D14, "D", -12, -4), ((6, 8), "h", 9, 0), (A14, "32°", 42, -50), (A14, "59°", 40, -6), (D14, "78°", 4, 15)])
tri("k15", [(0, 0), (8.3 * cos(radians(118.5)), 8.3 * sin(radians(118.5))), (15.2 * cos(radians(61.5)), 15.2 * sin(radians(61.5)))],
    vlab={0: "A", 1: "B", 2: "C"}, slab={(0, 1): "8.3 km", (0, 2): "15.2 km"}, alab={0: "57°"}, H=170)
A16 = (4 * cos(radians(62)), 4 * sin(radians(62))); B16 = (A16[0] + 4, A16[1])
def inter(p1, p2, p3, p4):
    d1 = (p2[0] - p1[0], p2[1] - p1[1]); d2 = (p4[0] - p3[0], p4[1] - p3[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]; t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])
P16 = inter(A16, (7, 0), B16, (0, 0))
tri("k16", [(0, 0), (7, 0), B16, A16], vlab={0: "D", 1: "C", 2: "B", 3: "A"}, slab={(2, 3): "4 cm", (3, 0): "4 cm", (0, 1): "7 cm"},
    W=210, extra=[(A16, (7, 0), None), (B16, (0, 0), None)], labels=[(P16, "P", 0, -12), ((0, 0), "62°", 42, -11)], marks=[((0, 0), 14, 0, 62)])
xb = 9 / (1 - cos(radians(50))); Wr = 2 * xb
f = Fig(230, 130); sc = 170 / Wr; ox, oy = 30, 100
pt = lambda x, y: (ox + x * sc, oy - y * sc)
L17, R17 = pt(0, 0), pt(Wr, 0); TL17 = pt(xb * cos(radians(50)), xb * sin(radians(50))); TR17 = pt(Wr - xb * cos(radians(50)), xb * sin(radians(50)))
f.line(*L17, *TL17, "ink", 2).line(*R17, *TR17, "ink", 2).line(L17[0] - 10, L17[1], R17[0] + 10, R17[1], "faint", 1.2)
f.line(*TL17, *TR17, "faint", 1, "4 3")
f.dim(L17[0], 118, R17[0], 118)
plain(f, (L17[0] + R17[0]) / 2, 126, "river", size=11)
plain(f, (TL17[0] + TR17[0]) / 2, TL17[1] - 9, "18 m", size=11)
plain(f, (L17[0] + TL17[0]) / 2 - 10, (L17[1] + TL17[1]) / 2 - 4, "x", italic=True, size=11.5)
plain(f, (R17[0] + TR17[0]) / 2 + 10, (R17[1] + TR17[1]) / 2 - 4, "x", italic=True, size=11.5)
f.arc(*L17, 16, 0, 50).arc(*R17, 16, 130, 180)
plain(f, L17[0] + 30, L17[1] - 8, "50°", size=11); plain(f, R17[0] - 30, R17[1] - 8, "50°", size=11)
save("k17", f)
A18, B18, C18 = (8, 7), (0, 0), (9, 0); D18 = ((A18[0] + C18[0]) / 2, (A18[1] + C18[1]) / 2)
tri("k18", [B18, C18, A18], vlab={0: "B", 1: "C", 2: "A"}, slab={(0, 1): "a", (0, 2): "c"}, W=200, H=170,
    extra=[(B18, D18, None)], labels=[(D18, "D", 10, 2), (D18, "b", 10, -28), ((4.25, 1.75), "m", 0, -12), (D18, "θ", -14, -2)])
P20, Q20, A20, B20 = (5, 11), (5, 4), (11, 3.5), (0, 0)
tri("k20", [B20, A20, P20], vlab={0: "B", 1: "A", 2: "P"}, W=200, H=200, fill=False,
    extra=[(P20, Q20, "4 3"), (Q20, A20, "4 3"), (Q20, B20, "4 3")],
    labels=[(Q20, "Q", -11, -4), ((5, 7.5), "h", 8, 0), ((8, 3.75), "x", 0, 12), ((2.5, 2), "y", 10, 4), (A20, "α", -28, -6), (B20, "β", 31, -39), (P20, "θ", 12, 24)])


# ================= Chapter 6 review =================
tri("r20a", [(0, 0), (8.53, 0), (7 * cos(radians(-70)), 7 * sin(radians(-70)))], slab={(0, 1): "x", (0, 2): "7"}, alab={1: "47°", 2: "63°"})
tri("r20b", sas(8, 75, 9), slab={(0, 1): "9", (0, 2): "8", (1, 2): "x"}, alab={0: "75°"})
c20 = 15 * sin(radians(40)) / sin(radians(112)); TR20 = (c20, 0); BR20 = add(TR20, uv(292), 15 * sin(radians(28)) / sin(radians(112)))
tri("r20c", [(0, 0), TR20, BR20], slab={(0, 2): "15", (1, 2): "x"}, alab={1: "112°", 2: "40°"})
tri("r20d", rot(sas(9.3, 18.5, 17.2), 200), slab={(0, 2): "9.3", (0, 1): "17.2", (1, 2): "x"}, alab={0: "18°30′"}, aout={0}, pad=48, W=280, H=150)
tri("r21a", sas(8, 42, 10), slab={(0, 1): "10 cm", (0, 2): "8 cm"}, alab={0: "42°"})
tri("r21b", flipy(sas(12.3, 112.6, 9.8)), slab={(0, 1): "9.8 cm", (0, 2): "12.3 cm"}, alab={0: "112°36′"}, aout={0})
tri("r22a", sss(7, 6, 8), slab={(0, 1): "8", (0, 2): "6", (1, 2): "7"}, alab={0: "θ"})
tri("r22b", flipy(asa(13, 54.45, 48.55)), slab={(0, 1): "13", (0, 2): "10"}, alab={2: "77°", 1: "θ"})
tri("r22c", rot(sas(29, 131.317, 16), 200), slab={(0, 1): "16", (0, 2): "29"}, alab={0: "131°19′", 2: "θ"}, aout={0}, W=250, H=190, pad=42)
tri("r22d", rot(sss(23.8, 13.9, 10.7), 120), slab={(0, 1): "10.7", (0, 2): "13.9", (1, 2): "23.8"}, alab={0: "θ"}, aout={0}, H=200, W=220)
xc25 = 600 * tan(radians(13)) / (tan(radians(7)) + tan(radians(13)))
tri("r25", [(0, 0), (600, 0), (xc25, 160)], vlab={0: "A", 1: "B", 2: "H"}, slab={(0, 1): "600 m"}, alab={0: "7°", 1: "13°"},
    W=230, H=130, extra=[((xc25, 160), (xc25, 0), None)], labels=[((xc25, 0), "C", 0, 13)], rights=[((xc25, 0), (600, 0), (xc25, 160))], soff={(0, 1): 8})
tri("r26", [(0, 0), (13, 0), (13, 6)], vlab={0: "P", 1: "B", 2: "T"}, slab={(1, 2): "h"}, alab={0: "15°"}, right=[1], W=230, H=140,
    extra=[((5, 0), (13, 6), None)], labels=[((5, 0), "Q", 0, 13), ((2.5, 0), "50 m", 0, 26), ((5, 0), "25°", 30, -8)])
Q27 = (140 * sin(radians(50)), 140 * cos(radians(50))); R27 = add(Q27, (sin(radians(130)), cos(radians(130))), 260)
tri("r27", [(0, 0), Q27, R27], vlab={0: "P", 1: "Q", 2: "R"}, slab={(1, 2): "260 Nm"}, W=230, H=190, fill=False,
    extra=[((0, 0), (0, 70), "4 3"), (Q27, (Q27[0], Q27[1] + 60), "4 3")],
    labels=[((0, 0), "50°", 13, -40), (Q27, "130°", 22, -16), ((Q27[0] / 2, Q27[1] / 2), "140 Nm", 26, 10)])
BC29 = 8 * tan(radians(40)); BD29 = BC29 * sin(radians(122)) / sin(radians(23))
A29, B29, C29 = (0, 0), (8, 0), (8, BC29); D29 = add(B29, uv(55), BD29)
tri("r29a", [A29, B29, D29, C29], vlab={0: "A", 1: "B", 2: "D", 3: "C"}, slab={(0, 1): "8 m"}, alab={0: "40°"},
    W=240, H=230, extra=[(B29, C29, None)], rights=[(B29, A29, C29)], labels=[(B29, "35°", 10, -44), (C29, "122°", 26, 14)], marks=[(B29, 22, 55, 90), (C29, 14, -90, 32)])
A29b = (0, 0); D29b = (7 * cos(radians(-10)), 7 * sin(radians(-10))); B29b = (6 * cos(radians(75)), 6 * sin(radians(75)))
vBD = (D29b[0] - B29b[0], D29b[1] - B29b[1]); lBD = sqrt(vBD[0] ** 2 + vBD[1] ** 2); uBD = (vBD[0] / lBD, vBD[1] / lBD)
uBC = (uBD[0] * cos(radians(37)) - uBD[1] * sin(radians(37)), uBD[0] * sin(radians(37)) + uBD[1] * cos(radians(37)))
C29b = add(B29b, uBC, lBD * cos(radians(37)))
tri("r29b", [A29b, D29b, C29b, B29b], vlab={0: "A", 1: "D", 2: "C", 3: "B"}, slab={(3, 0): "6 m", (0, 1): "7 m"},
    alab={0: "85°"}, right=[2], W=180, H=170, extra=[(B29b, D29b, None)], labels=[(B29b, "37°", 30, -7)])
uB = uv(210); uA = uv(210 - 86.4248)
A29c = (4 * uA[0], 4 * uA[1]); B29c = (6 * uB[0], 6 * uB[1]); D29c = (-B29c[0], -B29c[1]); PC = 6 * sin(radians(65)) / sin(radians(180 - 86.4248 - 65))
C29c = (-PC * uA[0], -PC * uA[1])
tri("r29c", [A29c, D29c, C29c, B29c], vlab={0: "A", 1: "D", 2: "C", 3: "B"}, slab={(3, 0): "7 m"}, W=180, H=210,
    extra=[(A29c, C29c, None), (B29c, D29c, None)],
    labels=[((0, 0), "P", 0, 14), ((A29c[0] / 2, A29c[1] / 2), "4 m", 14, -6), ((B29c[0] / 2, B29c[1] / 2), "6 m", 4, 12),
            ((D29c[0] / 2, D29c[1] / 2), "6\u00a0m", -2, -12), (D29c, "65°", -10, 26)])
AB30 = 12 * tan(radians(62)) * tan(radians(64)); BQ30 = 12 * tan(radians(62))
tri("r30", [(0, 0), (BQ30, 0), (BQ30, AB30 - 12), (0, AB30 - 12), (0, AB30)], vlab={0: "B", 1: "Q", 2: "P", 3: "K", 4: "A"}, W=170, H=230, fill=False,
    extra=[((0, AB30), (BQ30, AB30 - 12), None), ((0, AB30), (BQ30, 0), None), ((0, AB30), (BQ30, AB30), "4 3")],
    labels=[((0, AB30 - 6), "12 m", -22, 0), ((0, AB30), "28°", 54, 6), ((0, AB30), "64°", 22, -12)],
    rights=[((0, AB30 - 12), (0, AB30), (BQ30, AB30 - 12)), ((0, 0), (0, 10), (10, 0)), ((BQ30, 0), (0, 0), (BQ30, 10))])
tri("r31", [(0, 0), (8.6, 0), (3.4, 6)], vlab={0: "T₁", 1: "T₂", 2: "S"}, W=190, H=150, fill=False,
    extra=[((-1.5, 0), (10, 0), None), ((-1.5, 6), (10, 6), None)])
tri("r32", [(0, 0), (6, 4), (6, -5)], vlab={0: "C", 1: "A", 2: "B"}, W=170, H=190, fill=False,
    extra=[((0, 0), (6, 0), None)], rights=[((6, 0), (0, 0), (6, 4))],
    labels=[((6, 0), "D", 10, 0), ((0, 0), "α", 30, -8), ((0, 0), "β", 30, 9), ((6, -2.5), "x", -9, 0), ((6, 0), "h", 22, 0)])
tri("r33", [(0, 0), (1.618, 0), (0.809, 0.588)], vlab={0: "C", 1: "A", 2: "B"}, slab={(1, 2): "x", (0, 2): "x"}, alab={1: "36°"}, W=220, H=120,
    extra=[((0.809, 0.588), (0.618, 0), None)], labels=[((0.618, 0), "P", 0, 13), ((0.71, 0.29), "y", -10, 0)])
P34, B34, Q34, A34 = (0, 4), (10, 4), (5, 0), (10, 13)
tri("r34", [P34, Q34, A34], vlab={0: "P", 1: "Q", 2: "A"}, slab={(0, 1): "200 m"}, W=210, H=210, fill=False,
    extra=[(P34, B34, "4 3"), (Q34, B34, None), (A34, B34, None)],
    labels=[(B34, "B", 11, 0), ((10, 8.5), "h", 9, 0), (P34, "42°", 30, -14), (Q34, "35°", 22, -24)], rights=[(B34, P34, A34)])
D35, A35, C35, B35 = (2, 4), (2, 11), (9, 5), (5, 0)
tri("r35", [B35, C35, A35], vlab={0: "B", 1: "C", 2: "A"}, W=190, H=210, fill=False,
    extra=[(A35, D35, None), (D35, B35, None), (D35, C35, "4 3")],
    labels=[(D35, "D", -11, 0), ((2, 7.5), "h", -9, 0), (C35, "45°", -26, -16), (C35, "30°", -16, 18), (B35, "30°\u200d", -2, -34), ((7, 2.5), "x", 10, 6)],
    rights=[(D35, A35, C35)], marks=[(B35, 18, degrees(atan2(4, -3)), degrees(atan2(11, -3)))])

tri("k_ex31", [(0, 0), (0, 6), (10 * sin(radians(120)), 10 * cos(radians(120)))], vlab={0: "H", 1: "A", 2: "B"},
    slab={(0, 1): "6 km", (0, 2): "10 km"}, W=170, H=190, fill=False, extra=[((0, 0), (0, -6), "4 3"), ((-3, 0), (4, 0), "4 3")],
    labels=[((0, 0), "120°", 36, -20)], marks=[((0, 0), 14, -30, 90)])
