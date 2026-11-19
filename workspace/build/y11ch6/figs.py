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


def tri(name, pts, vlab=None, slab=None, alab=None, right=(), W=170, H=120, pad=24, extra=(), arcs=True,
        aoff=None, soff=None, fill=True):
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
        plain(f, mx + nx * (6 + d + abs(nx) * tw / 2), my + ny * (8 + d), lab, italic=not any(ch.isdigit() for ch in lab))
    for i, lab in alab.items():
        o = Q[i]; a = Q[(i - 1) % n]; b = Q[(i + 1) % n]
        a1 = degrees(atan2(-(a[1] - o[1]), a[0] - o[0])); a2 = degrees(atan2(-(b[1] - o[1]), b[0] - o[0]))
        d = (a2 - a1) % 360
        if d > 180: a1, a2, d = a2, a1, 360 - d
        if arcs: f.arc(o[0], o[1], 13, a1, a1 + d, "faint", 1.2)
        mid = radians(a1 + d / 2)
        tw = text_width(lab, 11)
        rr = aoff.get(i) or max(22, (tw / 2 + 5) / max(0.2, sin(radians(d / 2))) )
        rr = min(rr, 60)
        plain(f, o[0] + rr * cos(mid), o[1] - rr * sin(mid), lab, size=11, italic=not any(ch.isdigit() for ch in lab))
    save(name, f)
    return f


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
