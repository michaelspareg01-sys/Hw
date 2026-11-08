"""Frame fitting for the int1 figures (used by figs.save and figs_4j.save_raw).

fit(svg)      grow the SVG frame (and move the drawing right/down where needed) so that every text
              label lies inside it, by the label extents that workspace/tools/svg_overlap.py estimates.
              A figure that already fits is returned unchanged.
flatten(svg)  apply each <g transform="translate(dx,dy)"> to its contents and drop the group, so that
              composite figures are checked panel by panel in true coordinates.
shift(s, dx, dy) moves every absolute coordinate in an SVG fragment.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from svg_overlap import text_width, text_extent  # noqa: E402

NUM = r"-?\d*\.?\d+(?:e-?\d+)?"


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-9 else str(int(round(v)))


def _shift_path(d, dx, dy):
    toks = re.findall(r"[A-Za-z]|" + NUM, d)
    out, i, cmd = [], 0, None
    arity = {"M": 2, "L": 2, "T": 2, "Q": 4, "S": 4, "C": 6, "A": 7, "H": 1, "V": 1, "Z": 0}
    while i < len(toks):
        t = toks[i]
        if re.fullmatch(r"[A-Za-z]", t):
            cmd = t
            out.append(t)
            i += 1
            if cmd in "Zz":
                continue
            continue
        k = arity[cmd.upper()]
        vals = [float(v) for v in toks[i:i + k]]
        i += k
        if cmd.isupper():
            c = cmd
            if c in "MLTQSC":
                vals = [v + (dx if j % 2 == 0 else dy) for j, v in enumerate(vals)]
            elif c == "A":
                vals[5] += dx
                vals[6] += dy
            elif c == "H":
                vals[0] += dx
            elif c == "V":
                vals[0] += dy
        out.append(" ".join(_f(v) for v in vals))
        if cmd == "M":
            cmd = "L"
        elif cmd == "m":
            cmd = "l"
    s = ""
    for t in out:
        s += t if re.fullmatch(r"[A-Za-z]", t) else t + " "
    return s.strip()


def shift(s, dx, dy):
    """Move every absolute coordinate in the SVG fragment s by (dx, dy)."""
    if not dx and not dy:
        return s
    if "<defs>" in s:                     # pattern tiles keep their own coordinates
        parts = re.split(r"(<defs>.*?</defs>)", s, flags=re.S)
        return "".join(p if p.startswith("<defs>") else shift(p, dx, dy) for p in parts)

    def attr(name, off):
        nonlocal s
        s = re.sub(r'(\s%s=")(%s)(")' % (name, NUM), lambda m: m.group(1) + _f(float(m.group(2)) + off) + m.group(3), s)

    # tspans carry only relative dy shifts, so the x/y of <text> and the other shapes are enough
    for name in ("x", "x1", "x2", "cx"):
        attr(name, dx)
    for name in ("y", "y1", "y2", "cy"):
        attr(name, dy)
    s = re.sub(r'(\spoints=")([^"]*)(")', lambda m: m.group(1) + " ".join(
        f"{_f(float(a) + dx)},{_f(float(b) + dy)}" for a, b in (p.split(",") for p in m.group(2).split())) + m.group(3), s)
    s = re.sub(r'(\sd=")([^"]*)(")', lambda m: m.group(1) + _shift_path(m.group(2), dx, dy) + m.group(3), s)
    return s


def flatten(svg):
    """Replace <g transform="translate(dx,dy)">...</g> (not nested) by its shifted contents."""
    def one(m):
        return shift(m.group(3), float(m.group(1)), float(m.group(2)))
    return re.sub(r'<g transform="translate\((%s),(%s)\)">(.*?)</g>' % (NUM, NUM), one, svg, flags=re.S)


def _boxes(svg):
    for m in re.finditer(r"<text([^>]*)>(.*?)</text>", svg, flags=re.S):
        a, body = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if not body.strip():
            continue
        g = lambda k, d=0.0: float(re.search(r'\s%s="(%s)' % (k, NUM), a).group(1)) if re.search(r'\s%s="(%s)' % (k, NUM), a) else d  # noqa: E731
        size, x, y = g("font-size", 12.0), g("x"), g("y")
        anc = (re.search(r'text-anchor="(\w+)"', a) or [None, "start"])[1]
        w = text_width(body, size)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anc]
        up, down = text_extent(body, size)
        lean = 0.08 * size if 'font-style="italic"' in a else 0.0
        yield (x0 - lean, y - up, x0 + w + lean, y + down)


def fit(svg, margin=1.0):
    """Grow the frame so that every label box lies inside it, with the given margin (px)."""
    head = re.match(r"<svg[^>]*>", svg).group(0)
    vb = [float(v) for v in re.search(r'viewBox="([^"]*)"', head).group(1).split()]
    W, H = vb[2], vb[3]
    bs = list(_boxes(svg))
    if not bs:
        return svg
    minx, miny = min(b[0] for b in bs), min(b[1] for b in bs)
    maxx, maxy = max(b[2] for b in bs), max(b[3] for b in bs)
    if minx >= 0 and miny >= 0 and maxx <= W and maxy <= H:
        return svg                        # nothing clipped: leave the figure exactly as it is
    dx = max(0.0, margin - minx)
    dy = max(0.0, margin - miny)
    dx, dy = float(int(dx + 0.999)), float(int(dy + 0.999))
    W2 = max(W + dx, maxx + dx + margin)
    H2 = max(H + dy, maxy + dy + margin)
    W2, H2 = float(int(W2 + 0.999)), float(int(H2 + 0.999))
    if (dx, dy, W2, H2) == (0.0, 0.0, W, H):
        return svg
    body = svg[len(head):]
    body = shift(body, dx, dy)
    head2 = re.sub(r'viewBox="[^"]*"', f'viewBox="0 0 {_f(W2)} {_f(H2)}"', head)
    head2 = re.sub(r'\swidth="%s"' % NUM, f' width="{_f(W2)}"', head2)
    head2 = re.sub(r'\sheight="%s"' % NUM, f' height="{_f(H2)}"', head2)
    # a fixed style width (mm) keeps its scale: grow it in proportion
    mw = re.search(r"width:(%s)mm" % NUM, head2)
    if mw:
        head2 = head2.replace(mw.group(0), f"width:{float(mw.group(1)) * W2 / W:.1f}mm", 1)
    return head2 + body


def _texts(svg):
    """(start, end, label) of each top-level <text> element, label as svg_overlap names it."""
    out = []
    for m in re.finditer(r"<text[^>]*>(.*?)</text>", svg, flags=re.S):
        out.append((m.start(), m.end(), re.sub(r"<[^>]+>", "", m.group(1))))
    return out


def _move(el, dx, dy):
    el = re.sub(r'(<text[^>]*?\sx=")(%s)(")' % NUM, lambda m: m.group(1) + _f(float(m.group(2)) + dx) + m.group(3), el, count=1)
    return re.sub(r'(<text[^>]*?\sy=")(%s)(")' % NUM, lambda m: m.group(1) + _f(float(m.group(2)) + dy) + m.group(3), el, count=1)


def untangle(svg, rmax=8, log=None):
    """Nudge single labels (not stacked fractions) that svg_overlap flags, by at most rmax px, to the
    nearest position where the figure has fewer problems. Returns the new svg."""
    from math import cos, sin, pi
    from svg_overlap import check_string
    probs = check_string(svg)
    tried = set()
    while probs:
        names = []
        for p in probs:
            n = re.match(r"'(.*?)' (crossed|overlaps|clipped)", p)
            if n and "/" not in n.group(1) and n.group(1) not in tried:
                names.append(n.group(1))
        if not names:
            break
        name = names[0]
        tried.add(name)
        best = None
        for (a, b, lab) in _texts(svg):
            if lab != name:
                continue
            el = svg[a:b]
            for r in range(1, rmax + 1):
                for k in range(16):
                    dx, dy = round(r * cos(2 * pi * k / 16), 1), round(r * sin(2 * pi * k / 16), 1)
                    t = svg[:a] + _move(el, dx, dy) + svg[b:]
                    q = check_string(t)
                    if len(q) < len(probs) and not (set(q) - set(probs)):
                        best = (t, q, r, dx, dy)
                        break
                if best:
                    break
            if best:
                break
        if best:
            svg, probs = best[0], best[1]
            tried.discard(name)
            if log is not None:
                log.append(f"{name!r} moved ({best[3]:+g}, {best[4]:+g})")
    return svg


def separate(svg):
    """Draw order only: a horizontal line (a tick mark or guide) that sits between two labels in the
    source, and is not the bar of a stacked fraction, is moved in front of the first label. This changes
    nothing on the page, but svg_overlap.py would otherwise read label, line, label as one fraction."""
    one_text = r"<text[^>]*>(?:(?!</text>|<text).)*</text>"
    pat = re.compile(r"(%s)(<line[^>]*/>)(%s)" % (one_text, one_text), re.S)

    def num(el, k):
        m = re.search(r'\s%s="(%s)"' % (k, NUM), el)
        return float(m.group(1)) if m else None

    def one(m):
        t1, ln, t2 = m.groups()
        y1, y2 = num(ln, "y1"), num(ln, "y2")
        if y1 is None or abs(y1 - y2) > 0.01:
            return m.group(0)
        mid = (num(ln, "x1") + num(ln, "x2")) / 2
        bar = all('text-anchor="middle"' in t and num(t, "x") is not None and abs(num(t, "x") - mid) < 0.6 for t in (t1, t2))
        return m.group(0) if bar else ln + t1 + t2

    pos = 0
    while True:
        m = pat.search(svg, pos)
        if not m:
            return svg
        new = one(m)
        if new == m.group(0):
            pos = m.start() + 1               # overlapping candidates: the next text may start a triple
        else:
            svg = svg[:m.start()] + new + svg[m.end():]
            pos = 0                           # a moved line can make a new triple further back


def masked(frag, pad=1.5):
    """Put a white background behind a label (an svg fragment of <text> elements, a stacked fraction
    included), so that lines drawn earlier pass behind it. A white rect goes before each text that does
    not directly follow a line (a fraction bar), covering that text and the texts after it."""
    els = re.findall(r"<text[^>]*>(?:(?!</text>|<text).)*</text>|<line[^>]*/>|<rect[^>]*/>", frag, flags=re.S)
    if "".join(els) != frag.replace("\n", ""):
        return frag
    out = []
    for i, el in enumerate(els):
        if el.startswith("<text") and not (i and els[i - 1].startswith("<line")):
            bs = list(_boxes("".join(e for e in els[i:] if e.startswith("<text"))))
            for e in els[i:]:
                if e.startswith("<line"):
                    v = [float(re.search(r'\s%s="(%s)"' % (k, NUM), e).group(1)) for k in ("x1", "y1", "x2", "y2")]
                    bs.append((min(v[0], v[2]), min(v[1], v[3]), max(v[0], v[2]), max(v[1], v[3])))
            x0, y0 = min(b[0] for b in bs) - pad, min(b[1] for b in bs) - pad
            x1, y1 = max(b[2] for b in bs) + pad, max(b[3] for b in bs) + pad
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="#fff"/>')
        out.append(el)
    return "".join(out)
