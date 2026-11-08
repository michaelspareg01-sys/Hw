"""Move figure labels clear of strokes, other labels and the frame (Int2 assembly sweep).

Each figure script passes its finished SVG text through relabel(). The checks are those of
workspace/tools/svg_overlap.py (same box estimates and 2 px clearance). A "label" here is a run of
consecutive text items drawn side by side (for example "y =", a stacked fraction and "- 1"), so a
composite label moves as one piece. Parts of one composite that touch are first spread apart.
Each label with a problem then moves to the nearest small offset that clears it without making any
other label worse. A label that cannot be cleared within 12 px gets a white background instead.
"""
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import svg_overlap as SO  # noqa: E402

EL = re.compile(r"<defs\b.*?</defs>|<(text|line|polyline|polygon|path|rect|circle)\b[^>]*?(?:/>|>.*?</\1>)", re.S)
NUM = r"-?\d+(?:\.\d+)?"


def _attr(s, a):
    m = re.search(r'\s%s="([^"]*)"' % a, s)
    return m.group(1) if m else None


def _shift(s, dx, dy):
    """Shift one text, line or rect element by (dx, dy)."""
    for a, d in (("x", dx), ("y", dy), ("x1", dx), ("x2", dx), ("y1", dy), ("y2", dy)):
        v = _attr(s, a)
        if v is None or not re.fullmatch(NUM, v):
            continue
        s = re.sub(r'(\s%s=")%s"' % (a, re.escape(v)), lambda m: m.group(1) + f'{float(v) + d:.1f}"', s, count=1)
    return s


class Fig:
    def __init__(self, svg):
        self.head, self.tail = svg[:svg.index(">") + 1], "</svg>"
        body = svg[len(self.head):svg.rindex("</svg>")]
        self.els = [m.group(0) for m in EL.finditer(body)]
        assert "".join(self.els) == body, "unparsed SVG content"
        root = ET.fromstring(svg)
        vb = [float(v) for v in root.get("viewBox").split()]
        self.W, self.H = vb[2], vb[3]

    def text(self):
        return self.head + "".join(self.els) + self.tail

    # ------------------------------------------------------------ items as svg_overlap sees them
    def items(self):
        """List of dicts: kind text/stroke/mask/dot, element indices, box or segments, name."""
        out = []
        for k, e in enumerate(self.els):
            tag = re.match(r"<(\w+)", e).group(1)
            stroke = _attr(e, "stroke") or "none"
            if tag == "text":
                s = re.sub(r"<[^>]+>", "", e)
                s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                if not s.strip():
                    continue
                size = SO.fnum(_attr(e, "font-size"), 12)
                x, y = SO.fnum(_attr(e, "x")), SO.fnum(_attr(e, "y"))
                w = SO.text_width(s, size)
                anc = _attr(e, "text-anchor") or "start"
                x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anc]
                up, down = SO.text_extent(s, size)
                lean = 0.08 * size if _attr(e, "font-style") == "italic" else 0.0
                out.append(dict(kind="text", els=[k], box=(x0 - lean, y - up, x0 + w + lean, y + down), name=s))
            elif tag == "rect" and (_attr(e, "fill") or "").lower() in ("#fff", "#ffffff", "white"):
                x, y = SO.fnum(_attr(e, "x")), SO.fnum(_attr(e, "y"))
                out.append(dict(kind="mask", els=[k], box=(x, y, x + SO.fnum(_attr(e, "width")), y + SO.fnum(_attr(e, "height")))))
            elif tag == "circle":
                cx, cy, r = (SO.fnum(_attr(e, a)) for a in ("cx", "cy", "r"))
                out.append(dict(kind="dot", els=[k], box=(cx - r, cy - r, cx + r, cy + r)))
            elif stroke != "none" and tag in ("line", "polyline", "polygon", "path"):
                if tag == "line":
                    segs = [((SO.fnum(_attr(e, "x1")), SO.fnum(_attr(e, "y1"))), (SO.fnum(_attr(e, "x2")), SO.fnum(_attr(e, "y2"))))]
                elif tag in ("polyline", "polygon"):
                    pts = [tuple(float(v) for v in p.split(",")) for p in (_attr(e, "points") or "").split()]
                    segs = list(zip(pts[:-1], pts[1:]))
                    if tag == "polygon" and len(pts) > 2:
                        segs.append((pts[-1], pts[0]))
                else:
                    segs = SO.path_segments(_attr(e, "d") or "")
                out.append(dict(kind="stroke", els=[k], segs=segs, tag=tag, hw=SO.fnum(_attr(e, "stroke-width"), 1.0) / 2))
            elif tag == "path" and (_attr(e, "fill") or "none") != "none" and stroke == "none":
                out.append(dict(kind="stroke", els=[k], segs=SO.path_segments(_attr(e, "d") or ""), tag="filled path", hw=-1.0))
        merged, j = [], 0
        while j < len(out):
            it = out[j]
            if (it["kind"] == "text" and j + 2 < len(out) and out[j + 1]["kind"] == "stroke" and out[j + 1]["tag"] == "line"
                    and out[j + 2]["kind"] == "text"):
                (p, q), = out[j + 1]["segs"][:1]
                b1, b2 = it["box"], out[j + 2]["box"]
                if abs(p[1] - q[1]) < 0.01 and b1[3] <= p[1] + 3 and b2[1] >= p[1] - 3 - (b2[3] - b2[1]):
                    box = (min(b1[0], b2[0], p[0]), b1[1], max(b1[2], b2[2], q[0]), b2[3])
                    merged.append(dict(kind="text", els=it["els"] + out[j + 1]["els"] + out[j + 2]["els"], box=box,
                                       name=it["name"] + "/" + out[j + 2]["name"]))
                    j += 3
                    continue
            merged.append(it)
            j += 1
        for j, it in enumerate(merged):
            if it["kind"] == "text" and j > 0 and merged[j - 1]["kind"] == "mask" and SO.boxes_meet(merged[j - 1]["box"], it["box"]):
                it["mask_el"] = merged[j - 1]["els"][0]
                it["els"] = merged[j - 1]["els"] + it["els"]
        return merged

    def problems(self, pad=-2.0):
        """List of (item index, message) as svg_overlap reports them."""
        items = self.items()
        probs = []
        for j, it in enumerate(items):
            if it["kind"] != "text":
                continue
            b = it["box"]
            ib = (b[0] + pad, b[1] + pad, b[2] - pad, b[3] - pad)
            if b[0] < 0 or b[1] < 0 or b[2] > self.W or b[3] > self.H:
                probs.append((j, None, "clipped"))
            for jj, o in enumerate(items):
                if jj == j:
                    continue
                if "mask_el" in it and o["els"][-1] < it["mask_el"]:
                    continue
                if o["kind"] == "stroke":
                    sb = (ib[0] - o["hw"], ib[1] - o["hw"], ib[2] + o["hw"], ib[3] + o["hw"])
                    if any(SO.seg_hits_box(p, q, sb) for p, q in o["segs"]):
                        probs.append((j, jj, "stroke"))
                elif o["kind"] in ("text", "dot"):
                    ob = o["box"]
                    ob = (ob[0] + pad, ob[1] + pad, ob[2] - pad, ob[3] - pad)
                    if SO.boxes_meet(ib, ob):
                        probs.append((j, jj, o["kind"]))
        return items, probs


def _units(items):
    """Group consecutive text items drawn side by side into composite labels (lists of item indices)."""
    units, cur = [], []
    for j, it in enumerate(items):
        if it["kind"] != "text" or "mask_el" in it:
            if cur:
                units.append(cur)
                cur = []
            if it["kind"] == "text":
                units.append([j])
            continue
        if cur:
            pb, b = items[cur[-1]]["box"], it["box"]
            vert = min(pb[3], b[3]) - max(pb[1], b[1])
            if 0 <= b[0] - pb[2] + 1 <= 9 and vert > 0.4 * min(pb[3] - pb[1], b[3] - b[1]) and it["els"][0] == items[cur[-1]]["els"][-1] + 1:
                cur.append(j)
                continue
            units.append(cur)
        cur = [j]
    if cur:
        units.append(cur)
    return units


RING = [(0, 0)]
for r in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20):
    for a in range(0, 360, 15 if r > 12 else 30):
        RING.append((round(r * math.cos(math.radians(a))), round(-r * math.sin(math.radians(a)))))
RING = list(dict.fromkeys(RING))
RING.sort(key=lambda p: (p[0] ** 2 + p[1] ** 2, abs(p[0])))


def _untangle(f):
    """A tick mark drawn between two tick labels looks like a fraction bar to svg_overlap: draw it first."""
    for _ in range(len(f.els)):
        done = True
        for k in range(1, len(f.els) - 1):
            a, m, b = f.els[k - 1], f.els[k], f.els[k + 1]
            if not (a.startswith("<text") and m.startswith("<line") and b.startswith("<text")):
                continue
            x1, x2 = SO.fnum(_attr(m, "x1")), SO.fnum(_attr(m, "x2"))
            xa, xb = SO.fnum(_attr(a, "x")), SO.fnum(_attr(b, "x"))
            size = SO.fnum(_attr(a, "font-size"), 12)
            bar = (abs((x1 + x2) / 2 - xa) <= 2 and abs(xa - xb) <= 2 and abs(x2 - x1) < 3 * size
                   and "dasharray" not in m and (_attr(a, "text-anchor") or "start") == "middle")
            if not bar:
                f.els[k - 1], f.els[k] = m, a
                done = False
        if done:
            break


def relabel(svg, log=None, name="", mask=True):
    f = Fig(svg)
    _untangle(f)
    # 1. spread touching parts of a composite label (shift the later parts right)
    for _ in range(6):
        items, probs = f.problems()
        units = _units(items)
        moved = False
        for u in units:
            for a, b in zip(u, u[1:]):
                if any(p[0] == a and p[1] == b or p[0] == b and p[1] == a for p in probs):
                    need = items[a]["box"][2] - items[b]["box"][0] + 4.5
                    rest = [e for jj in u[u.index(b):] for e in items[jj]["els"]]
                    for e in rest:
                        f.els[e] = _shift(f.els[e], need, 0)
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break

    def unit_bad(items, probs, u):
        own = set(u)
        return [p for p in probs if p[0] in own and p[1] not in own]

    # 2. move each label with a problem to the nearest clear offset
    for _ in range(4):
        items, probs = f.problems()
        units = _units(items)
        bad_units = [u for u in units if unit_bad(items, probs, u)]
        if not bad_units:
            break
        for u0 in bad_units:
            items, probs = f.problems()
            units = _units(items)
            first_el = items[u0[0]]["els"][0]
            u = next((v for v in units if items[v[0]]["els"][0] == first_el), None)
            if u is None or not unit_bad(items, probs, u):
                continue
            els = sorted({e for j in u for e in items[j]["els"]})
            base = {e: f.els[e] for e in els}
            total0 = len(probs)
            best = None
            for dx, dy in RING[1:]:
                for e in els:
                    f.els[e] = _shift(base[e], dx, dy)
                it2, pr2 = f.problems()
                un2 = next(v for v in _units(it2) if it2[v[0]]["els"][0] == first_el)
                if not unit_bad(it2, pr2, un2) and len(pr2) < total0:
                    best = (dx, dy)
                    break
            if best is None:
                for e in els:
                    f.els[e] = base[e]
                if mask and not any("mask_el" in items[j] for j in u):
                    # white background behind the label, drawn just before it (and after every stroke)
                    b = [items[j]["box"] for j in u]
                    x0, y0 = min(v[0] for v in b) - 1.5, min(v[1] for v in b) - 1.5
                    x1, y1 = max(v[2] for v in b) + 1.5, max(v[3] for v in b) + 1.5
                    rect = f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="#fff"/>'
                    moved_els = [f.els[e] for e in els]
                    f.els = [e for k, e in enumerate(f.els) if k not in els] + [rect] + moved_els
                    if log is not None:
                        log.append(f"{name}: white background for {[items[j]['name'] for j in u]}")
                elif log is not None:
                    log.append(f"{name}: no clear spot for {[items[j]['name'] for j in u]}")
            elif log is not None:
                log.append(f"{name}: moved {[items[j]['name'] for j in u]} by {best}")
    return f.text()


def check_left(svg):
    return SO.check_string(svg)


if __name__ == "__main__":
    # usage: python3 relabel.py file.svg ...   (dry run: print what would move and what is left)
    for p in sys.argv[1:]:
        s = open(p, encoding="utf-8").read()
        log = []
        t = relabel(s, log, os.path.basename(p))
        print("\n".join(log))
        for q in SO.check_string(t):
            print(f"{os.path.basename(p)}: LEFT {q}")
