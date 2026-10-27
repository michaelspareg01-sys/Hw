"""Tiny SVG graph helper for lesson diagrams (grayscale-safe, template tokens).

Labels: plain text; "a/b" is drawn as a stacked fraction; "-" becomes a minus sign.
"""
import math

INK, FAINT, LINE = "#1f2a37", "#8a96a3", "#cdd4dd"
ACC = {"blue": "#2563eb", "teal": "#0d9488", "amber": "#c2790a", "rose": "#e11d48",
       "violet": "#6d44d9", "green": "#15a34a", "ink": INK, "faint": FAINT}


def _txt(x, y, s, anchor="middle", size=12, color=INK, weight=500, italic=False):
    s = s.replace("-", "−")
    st = ' font-style="italic"' if italic else ''
    if "/" in s:
        num, den = s.split("/", 1)
        w = max(len(num), len(den)) * size * 0.55 + 2
        ax = {"middle": x, "start": x + w / 2, "end": x - w / 2}[anchor]
        sign = ""
        if num.startswith("−"):
            sign, num = "−", num[1:]
        out = []
        if sign:
            out.append(f'<text x="{ax - w/2 - 2}" y="{y + size*0.35}" text-anchor="end" font-size="{size}" fill="{color}">{sign}</text>')
        out.append(f'<text x="{ax}" y="{y - 2}" text-anchor="middle" font-size="{size*0.9}" fill="{color}" font-weight="{weight}">{num}</text>')
        out.append(f'<line x1="{ax - w/2}" y1="{y + 1}" x2="{ax + w/2}" y2="{y + 1}" stroke="{color}" stroke-width="1"/>')
        out.append(f'<text x="{ax}" y="{y + size*0.9 + 2}" text-anchor="middle" font-size="{size*0.9}" fill="{color}" font-weight="{weight}">{den}</text>')
        return "".join(out)
    return (f'<text x="{x}" y="{y + size*0.35}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}"{st}>{s}</text>')


class Graph:
    def __init__(self, xmin, xmax, ymin, ymax, w=420, h=220, pad=(30, 34, 22, 40)):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.w, self.h = w, h
        self.pl, self.pr, self.pt, self.pb = pad  # left, right, top, bottom
        self.items = []

    def X(self, x):
        return self.pl + (x - self.xmin) / (self.xmax - self.xmin) * (self.w - self.pl - self.pr)

    def Y(self, y):
        return self.pt + (self.ymax - y) / (self.ymax - self.ymin) * (self.h - self.pt - self.pb)

    def axes(self, xlabel="x", ylabel="y"):
        x0 = self.X(max(self.xmin, min(0, self.xmax)))
        y0 = self.Y(max(self.ymin, min(0, self.ymax)))
        a = []
        a.append(f'<line x1="{self.X(self.xmin)-6}" y1="{y0}" x2="{self.X(self.xmax)+14}" y2="{y0}" stroke="{INK}" stroke-width="1.4"/>')
        a.append(f'<path d="M{self.X(self.xmax)+14},{y0} l-7,-3.5 v7 z" fill="{INK}"/>')
        a.append(f'<line x1="{x0}" y1="{self.Y(self.ymin)+6}" x2="{x0}" y2="{self.Y(self.ymax)-12}" stroke="{INK}" stroke-width="1.4"/>')
        a.append(f'<path d="M{x0},{self.Y(self.ymax)-12} l-3.5,7 h7 z" fill="{INK}"/>')
        a.append(_txt(self.X(self.xmax) + 18, y0 + 12, xlabel, "start", italic=True))
        a.append(_txt(x0 - 6, self.Y(self.ymax) - 12, ylabel, "end", italic=True))
        self.items += a
        self._x0, self._y0 = x0, y0
        return self

    def xticks(self, ticks, below=True):
        for v, lab in ticks:
            x = self.X(v)
            self.items.append(f'<line x1="{x}" y1="{self._y0-3}" x2="{x}" y2="{self._y0+3}" stroke="{INK}" stroke-width="1.2"/>')
            if lab:
                dy = 14 if below else -14
                if "/" in lab:
                    dy = 18 if below else -20
                self.items.append(_txt(x, self._y0 + dy, lab, size=11))
        return self

    def yticks(self, ticks):
        for v, lab in ticks:
            y = self.Y(v)
            self.items.append(f'<line x1="{self._x0-3}" y1="{y}" x2="{self._x0+3}" y2="{y}" stroke="{INK}" stroke-width="1.2"/>')
            if lab:
                self.items.append(_txt(self._x0 - 7, y, lab, "end", size=11))
        return self

    def curve(self, f, color="blue", width=2.2, dash=None, x0=None, x1=None, n=400):
        x0 = self.xmin if x0 is None else x0
        x1 = self.xmax if x1 is None else x1
        pts, segs = [], []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            try:
                y = f(x)
            except (ValueError, ZeroDivisionError):
                y = None
            if y is None or not (self.ymin - 0.05 * (self.ymax - self.ymin) <= y <= self.ymax + 0.05 * (self.ymax - self.ymin)):
                if len(pts) > 1:
                    segs.append(pts)
                pts = []
                continue
            pts.append(f"{self.X(x):.1f},{self.Y(y):.1f}")
        if len(pts) > 1:
            segs.append(pts)
        d = f' stroke-dasharray="{dash}"' if dash else ''
        for s in segs:
            self.items.append(f'<polyline points="{" ".join(s)}" fill="none" stroke="{ACC[color]}" stroke-width="{width}"{d} stroke-linejoin="round"/>')
        return self

    def hline(self, y, color="faint", dash="4 3", x0=None, x1=None, width=1.2):
        x0 = self.xmin if x0 is None else x0
        x1 = self.xmax if x1 is None else x1
        self.items.append(f'<line x1="{self.X(x0)}" y1="{self.Y(y)}" x2="{self.X(x1)}" y2="{self.Y(y)}" stroke="{ACC[color]}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
        return self

    def vline(self, x, y0=None, y1=None, color="faint", dash="4 3", width=1.2):
        y0 = self.ymin if y0 is None else y0
        y1 = self.ymax if y1 is None else y1
        self.items.append(f'<line x1="{self.X(x)}" y1="{self.Y(y0)}" x2="{self.X(x)}" y2="{self.Y(y1)}" stroke="{ACC[color]}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
        return self

    def dot(self, x, y, color="ink", r=3.2, hollow=False):
        fill = "#fff" if hollow else ACC[color]
        self.items.append(f'<circle cx="{self.X(x)}" cy="{self.Y(y)}" r="{r}" fill="{fill}" stroke="{ACC[color]}" stroke-width="1.5"/>')
        return self

    def label(self, x, y, s, dx=0, dy=0, anchor="middle", color="ink", size=11.5, italic=False):
        self.items.append(_txt(self.X(x) + dx, self.Y(y) + dy, s, anchor, size=size, color=ACC[color], italic=italic))
        return self

    def fill(self, top, bottom, a, b, color="blue", n=200, opacity=0.28):
        """Shade the region between two functions of x on [a, b]."""
        up = [(a + (b - a) * i / n) for i in range(n + 1)]
        pts = [f"{self.X(x):.1f},{self.Y(top(x)):.1f}" for x in up]
        pts += [f"{self.X(x):.1f},{self.Y(bottom(x)):.1f}" for x in reversed(up)]
        self.items.insert(0, f'<polygon points="{" ".join(pts)}" fill="{ACC[color]}" fill-opacity="{opacity}" stroke="none"/>')
        return self

    def fill_y(self, right, left, c, d, color="blue", n=200, opacity=0.28):
        """Shade the region between two functions of y (x = right(y), x = left(y)) on [c, d]."""
        ys = [(c + (d - c) * i / n) for i in range(n + 1)]
        pts = [f"{self.X(right(y)):.1f},{self.Y(y):.1f}" for y in ys]
        pts += [f"{self.X(left(y)):.1f},{self.Y(y):.1f}" for y in reversed(ys)]
        self.items.insert(0, f'<polygon points="{" ".join(pts)}" fill="{ACC[color]}" fill-opacity="{opacity}" stroke="none"/>')
        return self

    def field(self, f, xs, ys, length=11, color="ink", width=1.3, skip=None):
        """Slope field: a short line element of gradient f(x, y) centred at each grid point.
        Lengths are in screen pixels; undefined gradients are drawn vertical."""
        sx = (self.w - self.pl - self.pr) / (self.xmax - self.xmin)
        sy = (self.h - self.pt - self.pb) / (self.ymax - self.ymin)
        for x in xs:
            for y in ys:
                if skip and skip(x, y):
                    continue
                try:
                    m = f(x, y)
                except (ZeroDivisionError, ValueError, OverflowError):
                    m = None
                cx, cy = self.X(x), self.Y(y)
                if m is None or abs(m) > 1e6:
                    dx, dy = 0, length / 2
                else:
                    vx, vy = sx, m * sy
                    n = math.hypot(vx, vy)
                    dx, dy = length / 2 * vx / n, length / 2 * vy / n
                self.items.append(f'<line x1="{cx - dx:.1f}" y1="{cy + dy:.1f}" x2="{cx + dx:.1f}" y2="{cy - dy:.1f}" '
                                  f'stroke="{ACC[color]}" stroke-width="{width}" stroke-linecap="round"/>')
        return self

    def shade_x(self, a, b, color="blue"):
        """Thick bar on the x-axis marking a solution interval."""
        self.items.append(f'<line x1="{self.X(a)}" y1="{self._y0}" x2="{self.X(b)}" y2="{self._y0}" stroke="{ACC[color]}" stroke-width="5" stroke-opacity=".55"/>')
        return self

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="Inter, Arial, sans-serif">' + "".join(self.items) + "</svg>")


def quadrant(angle_deg, label="", w=150, h=130, color="blue", arc_label=None):
    """Quadrant diagram: axes with a ray at angle_deg (degrees), for auxiliary angles."""
    cx, cy, r = w / 2, h / 2, min(w, h) / 2 - 14
    a = math.radians(angle_deg)
    ex, ey = cx + r * math.cos(a), cy - r * math.sin(a)
    s = [f'<line x1="{cx-r-6}" y1="{cy}" x2="{cx+r+6}" y2="{cy}" stroke="{INK}" stroke-width="1.2"/>',
         f'<line x1="{cx}" y1="{cy+r+6}" x2="{cx}" y2="{cy-r-6}" stroke="{INK}" stroke-width="1.2"/>',
         f'<line x1="{cx}" y1="{cy}" x2="{ex}" y2="{ey}" stroke="{ACC[color]}" stroke-width="2.2"/>',
         f'<circle cx="{ex}" cy="{ey}" r="3" fill="{ACC[color]}"/>']
    if label:
        s.append(_txt(ex + (10 if math.cos(a) >= 0 else -10), ey + (-8 if math.sin(a) >= 0 else 10), label,
                      "start" if math.cos(a) >= 0 else "end", size=11.5))
    if arc_label:
        # arc for the related (acute) angle to the nearest x-axis
        ref = 0 if math.cos(a) >= 0 else math.pi
        a0, a1 = sorted([ref, a if ref == 0 else a])
        rr = 22
        x0, y0 = cx + rr * math.cos(ref), cy - rr * math.sin(ref)
        x1, y1 = cx + rr * math.cos(a), cy - rr * math.sin(a)
        sweep = 0 if (math.sin(a) >= 0) == (ref == 0) else 1
        s.append(f'<path d="M{x0},{y0} A{rr},{rr} 0 0 {sweep} {x1},{y1}" fill="none" stroke="{FAINT}" stroke-width="1.2"/>')
        mid = (ref + a) / 2
        s.append(_txt(cx + (rr + 16) * math.cos(mid), cy - (rr + 12) * math.sin(mid), arc_label, size=10.5, color=FAINT))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="Inter, Arial, sans-serif">' + "".join(s) + "</svg>")
