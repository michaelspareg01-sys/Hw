"""Nudge figure labels clear of lines, dots, other labels and the frame (layout only).

declutter(svg_text) -> svg_text.  Every text label (a stacked fraction from plots._txt counts as one label,
together with its minus sign and any white mask drawn just before it) that workspace/tools/svg_overlap.py
would flag is moved by the smallest offset, at most RMAX px, that leaves it with no problem.  A label
that cannot be cleared is left where it is (the overlap tool still reports it).  The measures are the
tool's own (svg_overlap.text_width / text_extent, 2 px clearance).
"""
import math
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import svg_overlap as so  # noqa: E402

SVGNS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVGNS)
RMAX = 8
PAD = 2.0


def _tbox(e):
    s = "".join(e.itertext())
    size = so.fnum(e.get("font-size"), 12)
    x, y = so.fnum(e.get("x")), so.fnum(e.get("y"))
    w = so.text_width(s, size)
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[e.get("text-anchor", "start")]
    up, down = so.text_extent(s, size)
    lean = 0.08 * size if e.get("font-style") == "italic" else 0.0
    return (x0 - lean, y - up, x0 + w + lean, y + down), s


def _items(root):
    out = []
    for k, e in enumerate(x for x in root.iter() if so.local(x.tag) != "svg"):
        tag, stroke = so.local(e.tag), e.get("stroke", "none")
        if tag == "text":
            b, s = _tbox(e)
            if s.strip():
                out.append({"k": k, "kind": "text", "box": b, "s": s, "el": [e]})
        elif tag == "rect" and e.get("fill", "").lower() in ("#fff", "#ffffff", "white"):
            x, y = so.fnum(e.get("x")), so.fnum(e.get("y"))
            out.append({"k": k, "kind": "mask", "box": (x, y, x + so.fnum(e.get("width")), y + so.fnum(e.get("height"))), "el": [e]})
        elif tag == "rect" and stroke != "none":
            x, y = so.fnum(e.get("x")), so.fnum(e.get("y"))
            x1, y1 = x + so.fnum(e.get("width")), y + so.fnum(e.get("height"))
            segs = [((x, y), (x1, y)), ((x1, y), (x1, y1)), ((x1, y1), (x, y1)), ((x, y1), (x, y))]
            out.append({"k": k, "kind": "stroke", "segs": segs, "tag": "rect", "w": so.fnum(e.get("stroke-width"), 1.0), "el": [e]})
        elif tag == "circle":
            cx, cy, r = so.fnum(e.get("cx")), so.fnum(e.get("cy")), so.fnum(e.get("r"))
            out.append({"k": k, "kind": "dot", "box": (cx - r, cy - r, cx + r, cy + r), "el": [e]})
        elif stroke != "none" and tag in ("line", "polyline", "polygon", "path"):
            if tag == "line":
                segs = [((so.fnum(e.get("x1")), so.fnum(e.get("y1"))), (so.fnum(e.get("x2")), so.fnum(e.get("y2"))))]
            elif tag in ("polyline", "polygon"):
                pts = [tuple(float(v) for v in p.split(",")) for p in e.get("points", "").split()]
                segs = list(zip(pts[:-1], pts[1:]))
                if tag == "polygon" and len(pts) > 2:
                    segs.append((pts[-1], pts[0]))
            else:
                segs = so.path_segments(e.get("d", ""))
            out.append({"k": k, "kind": "stroke", "segs": segs, "tag": tag, "w": so.fnum(e.get("stroke-width"), 1.0), "el": [e]})
        elif tag == "path" and e.get("fill", "none") != "none" and stroke == "none":
            out.append({"k": k, "kind": "stroke", "segs": so.path_segments(e.get("d", "")), "tag": "filled", "w": -2.0, "el": [e]})
    return out


def _groups(items):
    """Labels: merge fraction triples (as the tool does), then attach a leading minus sign and a mask."""
    merged, skip = [], set()
    for j, it in enumerate(items):
        if j in skip:
            continue
        if (it["kind"] == "text" and j + 2 < len(items) and items[j + 1]["kind"] == "stroke"
                and items[j + 1]["tag"] == "line" and items[j + 2]["kind"] == "text"):
            (p, q), = items[j + 1]["segs"][:1]
            b1, b2 = it["box"], items[j + 2]["box"]
            if abs(p[1] - q[1]) < 0.01 and b1[3] <= p[1] + 3 and b2[1] >= p[1] - 3 - (b2[3] - b2[1]):
                box = (min(b1[0], b2[0], p[0]), b1[1], max(b1[2], b2[2], q[0]), b2[3])
                merged.append({"k": it["k"], "kind": "label", "boxes": [box],
                               "el": it["el"] + items[j + 1]["el"] + items[j + 2]["el"]})
                skip.update({j + 1, j + 2})
                continue
        if it["kind"] == "text":
            merged.append({"k": it["k"], "kind": "label", "boxes": [it["box"]], "el": it["el"]})
        else:
            merged.append(it)
    out = []
    for it in merged:
        prev = out[-1] if out else None
        if (it["kind"] == "label" and prev is not None and prev["kind"] == "label" and len(prev["el"]) == 1
                and len(it["el"]) == 3 and "".join(prev["el"][0].itertext()) == "−"
                and prev["el"][0].get("text-anchor") == "end" and 0 <= it["boxes"][0][0] - prev["boxes"][0][2] <= 8):
            out[-1] = {"k": prev["k"], "kind": "label", "boxes": prev["boxes"] + it["boxes"], "el": prev["el"] + it["el"]}
            continue
        out.append(it)
    final = []
    for it in out:
        prev = final[-1] if final else None
        if it["kind"] == "label" and prev is not None and prev["kind"] == "mask" and any(so.boxes_meet(prev["box"], b) for b in it["boxes"]):
            final[-1] = dict(it, el=prev["el"] + it["el"], mask=prev["box"], mk=prev["k"])
            continue
        final.append(it)
    return final


def _shift_box(b, dx, dy):
    return (b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy)


def _grow(b, g):
    return (b[0] - g, b[1] - g, b[2] + g, b[3] + g)


def _hits(lab, dx, dy, groups, W, H):
    """What the label (moved by dx, dy) would hit: a list of groups, with "frame" for the frame."""
    out = []
    for b0 in lab["boxes"]:
        b = _shift_box(b0, dx, dy)
        ib = _grow(b, PAD)
        if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H:
            out.append("frame")
        for o in groups:
            if o is lab:
                continue
            if o["kind"] == "stroke":
                if "mk" in lab and o["k"] < lab["mk"]:
                    continue
                sb = _grow(ib, o["w"] / 2)
                if any(so.seg_hits_box(p, q, sb) for p, q in o["segs"]):
                    out.append(o)
            elif o["kind"] == "dot":
                if so.boxes_meet(ib, _grow(o["box"], PAD)):
                    out.append(o)
            elif o["kind"] == "label":
                for ob in o["boxes"]:
                    if so.boxes_meet(ib, _grow(ob, PAD)):
                        out.append(o)
    return out


def _count(lab, dx, dy, groups, W, H):
    return len(_hits(lab, dx, dy, groups, W, H))


def _guide(o):
    """A guide line: dashed, or a light grid line.  A label may sit on a white patch over these."""
    if o == "frame" or o["kind"] != "stroke" or o["tag"] in ("filled", "rect"):
        return False
    e = o["el"][0]
    if o["tag"] != "line":
        return bool(e.get("stroke-dasharray", "").strip())
    return (bool(e.get("stroke-dasharray", "").strip()) or e.get("stroke", "").lower() in ("#cdd4dd", "#c9d1db")
            or so.fnum(e.get("stroke-opacity"), 1.0) < 1 or so.fnum(e.get("stroke-width"), 1.0) <= 0.6)


def _mask(root, lab):
    """White patches behind the label (one per part: the minus sign, the fraction), each drawn just before it."""
    parts = [lab["el"][0]] if len(lab["boxes"]) == 1 else [lab["el"][0], lab["el"][1]]
    for el, b in zip(parts, lab["boxes"]):
        parent = next(p for p in root.iter() if el in list(p))
        r = ET.Element(el.tag[:-len("text")] + "rect", {"x": f"{b[0] - 1:.1f}", "y": f"{b[1] - 1:.1f}",
                                                      "width": f"{b[2] - b[0] + 2:.1f}", "height": f"{b[3] - b[1] + 2:.1f}",
                                                      "fill": "#fff"})
        parent.insert(list(parent).index(el), r)


def _move(lab, dx, dy):
    for e in lab["el"]:
        tag = so.local(e.tag)
        for a, d in (("x", dx), ("y", dy), ("x1", dx), ("x2", dx), ("y1", dy), ("y2", dy)):
            if e.get(a) is not None and (tag != "line" or a not in ("x", "y")):
                e.set(a, f"{so.fnum(e.get(a)) + d:.1f}")
    lab["boxes"] = [_shift_box(b, dx, dy) for b in lab["boxes"]]
    if "mask" in lab:
        lab["mask"] = _shift_box(lab["mask"], dx, dy)


OFFSETS = sorted(((dx, dy) for dx in range(-RMAX, RMAX + 1) for dy in range(-RMAX, RMAX + 1)
                  if 0 < math.hypot(dx, dy) <= RMAX), key=lambda t: (math.hypot(*t), abs(t[1]), t))


def _labels_to_front(root):
    """Draw unmasked labels last (on top), in their order.  This also keeps a tick label, the next tick
    mark and the next tick label from reading as one stacked fraction (text, short line, text)."""
    kids = list(root)
    items = [{"k": i, "kind": "", "el": [e]} for i, e in enumerate(kids)]
    for it in items:
        e = it["el"][0]
        tag = so.local(e.tag)
        if tag == "text" and "".join(e.itertext()).strip():
            it["kind"], it["box"] = "text", _tbox(e)[0]
        elif tag == "line" and e.get("stroke", "none") != "none":
            it.update(kind="stroke", tag="line", segs=[((so.fnum(e.get("x1")), so.fnum(e.get("y1"))),
                                                        (so.fnum(e.get("x2")), so.fnum(e.get("y2"))))])
        elif tag == "rect" and e.get("fill", "").lower() in ("#fff", "#ffffff", "white"):
            it["kind"] = "mask"
    labs, j = [], 0
    while j < len(items):
        it = items[j]
        if it["kind"] == "text":
            grp = [j]
            if (j + 2 < len(items) and items[j + 1]["kind"] == "stroke" and items[j + 2]["kind"] == "text"):
                (p, q), = items[j + 1]["segs"]
                b1, b2 = it["box"], items[j + 2]["box"]
                # a real fraction from plots._txt: numerator and denominator share the bar's centre
                if (abs(p[1] - q[1]) < 0.01 and abs((b1[0] + b1[2]) / 2 - (p[0] + q[0]) / 2) < 1
                        and abs((b2[0] + b2[2]) / 2 - (p[0] + q[0]) / 2) < 1 and b1[3] <= p[1] + 3 and b2[1] >= p[1] - 3 - (b2[3] - b2[1])):
                    grp = [j, j + 1, j + 2]
            masked = j > 0 and items[j - 1]["kind"] == "mask"
            if not masked:
                labs += grp
            j = grp[-1] + 1
        else:
            j += 1
    for i in labs:
        root.remove(kids[i])
    for i in labs:
        root.append(kids[i])


def _circles_to_paths(root):
    """An open circle (a ring, not a dot) becomes the same circle drawn as two arcs, so that the overlap
    tool tests labels against the ring itself rather than against its whole bounding box."""
    found = False
    for e in root.iter():
        if so.local(e.tag) == "circle" and e.get("fill", "") in ("none", "transparent") and so.fnum(e.get("r")) > 8:
            cx, cy, r = so.fnum(e.get("cx")), so.fnum(e.get("cy")), so.fnum(e.get("r"))
            e.tag = e.tag[:-len("circle")] + "path"
            for a in ("cx", "cy", "r"):
                del e.attrib[a]
            e.set("d", f"M{cx - r:.1f},{cy:.1f} A{r:g},{r:g} 0 1 0 {cx + r:.1f},{cy:.1f} A{r:g},{r:g} 0 1 0 {cx - r:.1f},{cy:.1f} Z")
            found = True
    return found


def declutter(svg_text):
    root = ET.fromstring(svg_text)
    rings = _circles_to_paths(root)
    if not so.check_root(root):
        return ET.tostring(root, encoding="unicode") if rings else svg_text
    _labels_to_front(root)
    vb = [so.fnum(v) for v in root.get("viewBox", "0 0 0 0").split()]
    W, H = (vb[2], vb[3]) if len(vb) == 4 else (so.fnum(root.get("width")), so.fnum(root.get("height")))
    groups = _groups(_items(root))
    for lab in groups:
        if lab["kind"] != "label" or _count(lab, 0, 0, groups, W, H) == 0:
            continue
        for dx, dy in OFFSETS:
            if _count(lab, dx, dy, groups, W, H) == 0:
                _move(lab, dx, dy)
                break
        else:
            if "mk" in lab:
                continue
            for dx, dy in [(0, 0)] + OFFSETS:
                hits = _hits(lab, dx, dy, groups, W, H)
                if all(_guide(o) for o in hits):
                    _move(lab, dx, dy)
                    _mask(root, lab)
                    break
    return ET.tostring(root, encoding="unicode")


def _shift_path(d, dx, dy):
    import re
    toks = re.findall(r"[MmLlHhVvQqCcSsTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    out, i, cmd, first = [], 0, None, True
    per = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7, "Z": 0}
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            if cmd in "Zz":
                continue
        n = per[cmd.upper()]
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        absolute = cmd.isupper() or (first and cmd == "m")
        if absolute:
            if cmd.upper() == "H":
                vals[0] += dx
            elif cmd.upper() == "V":
                vals[0] += dy
            elif cmd.upper() == "A":
                vals[5] += dx
                vals[6] += dy
            else:
                for k in range(0, n, 2):
                    vals[k] += dx
                    vals[k + 1] += dy
        if cmd == "m" and first:
            cmd = "l"          # later pairs after an initial m are relative lines
        first = False
        out.append(" ".join(f"{v:.2f}".rstrip("0").rstrip(".") for v in vals))
    return " ".join(out)


def _translate(e, dx, dy):
    tag = so.local(e.tag)
    for a, d in (("x", dx), ("y", dy), ("x1", dx), ("x2", dx), ("y1", dy), ("y2", dy), ("cx", dx), ("cy", dy)):
        if e.get(a) is not None:
            e.set(a, f"{so.fnum(e.get(a)) + d:.1f}")
    if tag in ("polyline", "polygon"):
        pts = [p.split(",") for p in e.get("points", "").split()]
        e.set("points", " ".join(f"{float(x) + dx:.1f},{float(y) + dy:.1f}" for x, y in pts))
    if tag == "path":
        e.set("d", _shift_path(e.get("d", ""), dx, dy))
    for c in e:
        if so.local(c.tag) == "tspan":
            _translate(c, dx, dy)


def flat_panel(svg_text, dx, dy):
    """The children of a 1:1 panel <svg>, moved by (dx, dy), as markup to put straight into a parent svg
    (no nested <svg>: the overlap tool then sees every panel where it is drawn)."""
    root = ET.fromstring(svg_text)
    vb = [so.fnum(v) for v in root.get("viewBox", "0 0 0 0").split()]
    w = so.fnum(root.get("width"), vb[2])
    assert vb[:2] == [0, 0] and abs(w - vb[2]) < 1e-6, "panel must be drawn at 1:1"
    out = []
    for e in list(root):
        _translate(e, dx, dy)
        s = ET.tostring(e, encoding="unicode")
        out.append(s.replace(' xmlns="http://www.w3.org/2000/svg"', ""))
    return "".join(out)
