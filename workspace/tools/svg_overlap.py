"""Find text labels in SVG figures that are crossed by a stroke, overlap another label, or are clipped.

usage: python3 -I svg_overlap.py [--pad N] file.svg [file.svg ...]      (globs are expanded by the shell)

For each <text> the script estimates a bounding box from x, y, font-size, text-anchor and the string
(per-character widths for Inter-like fonts; baseline at y; x-height 0.55 em, ascenders and digits
0.73 em, superscripts and radicals 0.8 em, descenders 0.21 em). It then
tests the box, shrunk by --pad px (default -2.0: the box is GROWN by 2 px, so a label needs 2 px of
clearance), against
  * every stroked segment: <line>, <polyline>, <polygon> edges (unless stroke="none"), <path> commands
    M/m L/l H/h V/v Q/q C/c A/a (curves sampled), Z/z;
  * every other text box;
  * every <circle> (as its bounding box);
  * the frame of the SVG (viewBox), for clipping.
A stacked fraction drawn by plots._txt (text, short line, text) is one label: its own bar is ignored and
its numerator and denominator are not tested against each other.
A label drawn on a white background (<rect fill="#fff"/"white"> covering the text box, placed just before
the text) masks everything drawn earlier in document order, so only later strokes count against it.
Exit status 1 if any problem is found. Prints one line per problem: file, label, what it hits.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET

WIDE = {" ": 0.34, "=": 0.66, "+": 0.66, "−": 0.66, "-": 0.66, "√": 0.62, "∛": 0.66, "²": 0.36, "³": 0.36,
        "⁴": 0.36, "⁵": 0.36, "(": 0.34, ")": 0.34, ",": 0.28, ".": 0.28, "1": 0.5, "i": 0.26, "l": 0.26,
        "j": 0.28, "f": 0.34, "t": 0.36, "r": 0.38, "x": 0.52, "y": 0.52, "m": 0.84, "w": 0.76, "/": 0.36}


ASC = set("bdfhklt0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ()/|")
HIGH = set("²³⁴⁵√∛")
DESC = set("gjpqy(),|")


def text_width(s, size):
    return 1.05 * sum(WIDE.get(ch, 0.58) for ch in s) * size        # calibrated on Inter spans in a PDF


def text_extent(s, size):
    """(height above the baseline, depth below it) in px: x-height 0.55 em, ascenders and digits 0.73 em,
    superscripts and radicals 0.8 em; descenders 0.21 em."""
    up = 0.55
    if any(ch in ASC for ch in s):
        up = 0.73
    if any(ch in HIGH for ch in s):
        up = 0.8
    down = 0.21 if any(ch in DESC for ch in s) else 0.02
    return up * size, down * size


def fnum(v, default=0.0):
    try:
        return float(re.sub(r"[a-z%]+$", "", str(v)))
    except (TypeError, ValueError):
        return default


def local(tag):
    return tag.split("}")[-1]


def path_segments(d):
    toks = re.findall(r"[MmLlHhVvQqCcAaZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    segs, i, cmd = [], 0, None
    cx = cy = sx = sy = 0.0

    def nums(k):
        nonlocal i
        out = [float(t) for t in toks[i:i + k]]
        i += k
        return out

    while i < len(toks):
        if re.fullmatch(r"[A-Za-z]", toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                segs.append(((cx, cy), (sx, sy)))
                cx, cy = sx, sy
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            x, y = nums(2)
            cx, cy = (cx + x, cy + y) if rel else (x, y)
            sx, sy = cx, cy
            cmd = "l" if rel else "L"
        elif c == "L":
            x, y = nums(2)
            nx, ny = (cx + x, cy + y) if rel else (x, y)
            segs.append(((cx, cy), (nx, ny)))
            cx, cy = nx, ny
        elif c in "HV":
            (v,) = nums(1)
            nx, ny = cx, cy
            if c == "H":
                nx = cx + v if rel else v
            else:
                ny = cy + v if rel else v
            segs.append(((cx, cy), (nx, ny)))
            cx, cy = nx, ny
        elif c in "QC":
            k = 4 if c == "Q" else 6
            p = nums(k)
            if rel:
                p = [p[j] + (cx if j % 2 == 0 else cy) for j in range(k)]
            pts = [(cx, cy)] + [(p[j], p[j + 1]) for j in range(0, k, 2)]
            prev = (cx, cy)
            for s in range(1, 17):
                t = s / 16
                if c == "Q":
                    (x0, y0), (x1, y1), (x2, y2) = pts
                    q = ((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2,
                         (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2)
                else:
                    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
                    q = ((1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3 * x3,
                         (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3 * y3)
                segs.append((prev, q))
                prev = q
            cx, cy = pts[-1]
        elif c == "A":
            rx, ry, rot, large, sweep, x, y = nums(7)
            nx, ny = (cx + x, cy + y) if rel else (x, y)
            segs += arc_segments(cx, cy, rx, ry, large, sweep, nx, ny)
            cx, cy = nx, ny
        else:
            i += 1
    return segs


def arc_segments(x1, y1, rx, ry, large, sweep, x2, y2, n=16):
    """Circular-arc approximation (rx = ry assumed, no rotation), as drawn by the pack's helpers."""
    r = max(rx, 1e-9)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    if d == 0 or d > 2 * r + 1e-6:
        return [((x1, y1), (x2, y2))]
    h = math.sqrt(max(r * r - d * d / 4, 0))
    ux, uy = -dy / d, dx / d
    sign = 1 if large != sweep else -1
    cx, cy = mx + sign * h * ux, my + sign * h * uy
    a1, a2 = math.atan2(y1 - cy, x1 - cx), math.atan2(y2 - cy, x2 - cx)
    da = a2 - a1
    if sweep and da < 0:
        da += 2 * math.pi
    if not sweep and da > 0:
        da -= 2 * math.pi
    pts = [(cx + r * math.cos(a1 + da * k / n), cy + r * math.sin(a1 + da * k / n)) for k in range(n + 1)]
    return list(zip(pts[:-1], pts[1:]))


def seg_hits_box(p, q, b):
    """Liang-Barsky: does segment pq meet the box (x0, y0, x1, y1)?"""
    x0, y0, x1, y1 = b
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pp == 0:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def boxes_meet(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def check(path, pad=-2.0):
    """Problems in one SVG file (a list of strings)."""
    return check_root(ET.parse(path).getroot(), pad)


def check_string(svg_text, pad=-2.0):
    """Problems in SVG source text (used by figure scripts to place labels)."""
    return check_root(ET.fromstring(svg_text), pad)


def check_root(root, pad=-2.0):
    vb = [fnum(v) for v in root.get("viewBox", "0 0 0 0").split()]
    W, H = (vb[2], vb[3]) if len(vb) == 4 else (fnum(root.get("width")), fnum(root.get("height")))
    els = [e for e in root.iter() if local(e.tag) != "svg"]
    items = []          # (order, kind, data)
    for k, e in enumerate(els):
        tag = local(e.tag)
        stroke = e.get("stroke", "none")
        if tag == "text":
            s = "".join(e.itertext())
            if not s.strip():
                continue
            size = fnum(e.get("font-size"), 12)
            x, y = fnum(e.get("x")), fnum(e.get("y"))
            w = text_width(s, size)
            anc = e.get("text-anchor", "start")
            x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anc]
            up, down = text_extent(s, size)
            lean = 0.08 * size if e.get("font-style") == "italic" else 0.0     # italic overhang
            items.append([k, "text", (x0 - lean, y - up, x0 + w + lean, y + down), s])
        elif tag == "rect" and e.get("fill", "").lower() in ("#fff", "#ffffff", "white"):
            x, y = fnum(e.get("x")), fnum(e.get("y"))
            items.append([k, "mask", (x, y, x + fnum(e.get("width")), y + fnum(e.get("height"))), ""])
        elif tag == "circle":
            cx, cy, r = fnum(e.get("cx")), fnum(e.get("cy")), fnum(e.get("r"))
            items.append([k, "dot", (cx - r, cy - r, cx + r, cy + r), ""])
        elif stroke != "none" and tag in ("line", "polyline", "polygon", "path"):
            if tag == "line":
                segs = [((fnum(e.get("x1")), fnum(e.get("y1"))), (fnum(e.get("x2")), fnum(e.get("y2"))))]
            elif tag in ("polyline", "polygon"):
                pts = [tuple(float(v) for v in p.split(",")) for p in e.get("points", "").split()]
                segs = list(zip(pts[:-1], pts[1:]))
                if tag == "polygon" and len(pts) > 2:
                    segs.append((pts[-1], pts[0]))
            else:
                segs = path_segments(e.get("d", ""))
            items.append([k, "stroke", segs, tag, fnum(e.get("stroke-width"), 1.0)])
        elif tag == "path" and e.get("fill", "none") != "none" and stroke == "none":
            # arrowheads: a filled shape has no stroke, so it needs 1 px less clearance than a line
            items.append([k, "stroke", path_segments(e.get("d", "")), "filled path", -2.0])
    # stacked fractions: text, short line, text (plots._txt) -> merge into one label
    merged, skip = [], set()
    for j, it in enumerate(items):
        if j in skip:
            continue
        if (it[1] == "text" and j + 2 < len(items) and items[j + 1][1] == "stroke" and items[j + 1][3] == "line"
                and items[j + 2][1] == "text"):
            (p, q), = items[j + 1][2][:1]
            b1, b2 = it[2], items[j + 2][2]
            if abs(p[1] - q[1]) < 0.01 and b1[3] <= p[1] + 3 and b2[1] >= p[1] - 3 - (b2[3] - b2[1]):
                box = (min(b1[0], b2[0], p[0]), b1[1], max(b1[2], b2[2], q[0]), b2[3])
                merged.append([it[0], "text", box, it[3] + "/" + items[j + 2][3]])
                skip.update({j + 1, j + 2})
                continue
        merged.append(it)
    items = merged
    # white masks just before a text
    masked_from = {}
    for j, it in enumerate(items):
        if it[1] == "text" and j > 0 and items[j - 1][1] == "mask" and boxes_meet(items[j - 1][2], it[2]):
            masked_from[j] = items[j - 1][0]
    problems = []
    for j, it in enumerate(items):
        if it[1] != "text":
            continue
        b = it[2]
        ib = (b[0] + pad, b[1] + pad, b[2] - pad, b[3] - pad)
        if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H:
            problems.append(f"'{it[3]}' clipped by the frame (box {tuple(round(v) for v in b)}, frame {W:g}x{H:g})")
        for jj, other in enumerate(items):
            if jj == j:
                continue
            if j in masked_from and other[0] < masked_from[j]:
                continue
            if other[1] == "stroke":
                hw = other[4] / 2                      # half the stroke width
                sb = (ib[0] - hw, ib[1] - hw, ib[2] + hw, ib[3] + hw)
                if any(seg_hits_box(p, q, sb) for p, q in other[2]):
                    problems.append(f"'{it[3]}' crossed by a {other[3]}")
            elif other[1] in ("text", "dot") and jj > j or (other[1] == "dot"):
                if other[1] == "text" and jj < j:
                    continue
                ob = other[2]
                ob = (ob[0] + pad, ob[1] + pad, ob[2] - pad, ob[3] - pad)
                if boxes_meet(ib, ob):
                    problems.append(f"'{it[3]}' overlaps " + (f"label '{other[3]}'" if other[1] == "text" else "a dot"))
    return sorted(set(problems))


def main(argv):
    pad = -2.0
    if argv[:1] == ["--pad"]:
        pad, argv = float(argv[1]), argv[2:]
    bad = 0
    for f in argv:
        for p in check(f, pad):
            print(f"{f.split('/')[-1]}: {p}")
            bad += 1
    print(f"{len(argv)} files, {bad} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
