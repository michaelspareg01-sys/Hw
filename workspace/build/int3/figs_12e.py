"""Figures for Lesson 12E (lesson and answers).

Kept in its own file so that parallel lesson tasks do not edit int3/figs.py at the same time.
Run: python3 workspace/build/int3/figs_12e.py  (writes int3/svg/c12e_*.svg and a12e_*.svg)
"""
import os
import sys
from math import cos, radians, sin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import ACC, Fig, save  # noqa: E402


def frame(f, cx, cy, R, ext=18):
    """x and y axes through the centre, with arrowheads and labels."""
    f.line(cx - R - ext, cy, cx + R + ext, cy, width=1.2)
    f.raw(f'<path d="M{cx + R + ext + 6},{cy} l-8,-4 v8 z" fill="{ACC["ink"]}"/>')
    f.line(cx, cy + R + ext, cx, cy - R - ext, width=1.2)
    f.raw(f'<path d="M{cx},{cy - R - ext - 6} l-4,8 h8 z" fill="{ACC["ink"]}"/>')
    f.text(cx + R + ext + 10, cy + 4, "x", anchor="start", italic=True)
    f.text(cx - 7, cy - R - ext - 2, "y", anchor="end", italic=True)


def circle(f, cx, cy, R):
    f.raw(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{ACC["ink"]}" stroke-width="1.3"/>')


def pt(cx, cy, R, deg):
    return cx + R * cos(radians(deg)), cy - R * sin(radians(deg))


def half_segment(name, chord_lab, r_lab, w=196, h=180):
    """Example 21(b): the region under y = sqrt(r^2 - x^2) from x = r/sqrt2 to x = r is half the
    segment cut off by the chord x = r/sqrt2, which subtends 90 degrees (from -45 to 45) at O."""
    cx, cy, R = 84, h / 2, 60
    f = Fig(w, h)
    ax, ay = pt(cx, cy, R, 45)
    f.path(f"M{ax:.1f},{cy:.1f} L{ax:.1f},{ay:.1f} A{R},{R} 0 0 1 {cx + R:.1f},{cy:.1f} Z",
           color="blue", width=0.8, fill="blue", opacity=0.3)
    circle(f, cx, cy, R)
    frame(f, cx, cy, R)
    bx, by = pt(cx, cy, R, -45)
    f.line(ax, ay, bx, by, width=1.3)
    ex, ey = pt(cx, cy, R + 16, 45)
    f.arrow(cx, cy, ex, ey, color="faint", width=1.1, head=6)
    ex2, ey2 = pt(cx, cy, R + 16, -45)
    f.arrow(cx, cy, ex2, ey2, color="faint", width=1.1, head=6)
    f.text(ex + 4, ey - 2, "45°", anchor="start", size=11)
    f.text(ex2 + 4, ey2 + 10, "−45°", anchor="start", size=11)
    f.text(ax - 3, cy + 15, chord_lab, anchor="end", size=11)
    f.text(cx + R + 4, cy + 15, r_lab, anchor="start", size=11)
    save(name, f)


def sector_triangle(name, w=196, h=182):
    """Your turn C2(b): under y = sqrt(36 - x^2) from x = 0 to x = 3 is the triangle O(0,0), (3,0),
    (3, 3sqrt3) plus the sector between the ray at 60 degrees and the y-axis."""
    cx, cy, R = 84, 112, 72
    f = Fig(w, h)
    px, py = pt(cx, cy, R, 60)
    f.poly([(cx, cy), (px, cy), (px, py)], color="blue", opacity=0.3, stroke="ink", width=1.2)
    f.path(f"M{cx:.1f},{cy:.1f} L{px:.1f},{py:.1f} A{R},{R} 0 0 0 {cx:.1f},{cy - R:.1f} Z",
           color="ink", width=1.2, fill="teal", opacity=0.3)
    f.path(f"M{cx + R:.1f},{cy:.1f} A{R},{R} 0 0 0 {cx - R:.1f},{cy:.1f}", color="ink", width=1.3)
    frame(f, cx, cy, R, ext=14)
    f.arc(cx, cy, 16, 60, 90, color="ink", width=1.1)
    f.text(cx + 9, cy - 24, "π/6", anchor="start", size=10)
    f.arc(cx, cy, 12, 0, 60, color="ink", width=1.1)
    f.text(cx + 15, cy - 5, "π/3", anchor="start", size=10)
    f.right(px, cy, -1, -1, 6)
    f.text(px, cy + 15, "3", size=11)
    f.text(cx + R, cy + 15, "6", size=11)
    f.text(px + 5, (py + cy) / 2 + 4, "3√3", anchor="start", size=11)
    f.text(cx - 4, cy + 15, "O", anchor="end", size=11, italic=True)
    save(name, f)


def triangles(name, w=340, h=120):
    """Returning to x: right triangles for x = a sin t (sin t = x/a) and x = a tan t (tan t = x/a)."""
    f = Fig(w, h)
    # triangle 1: angle at (20, 100); right angle at (140, 100); top (140, 30)
    x0, y0, x1, y1 = 22, 100, 140, 34
    f.poly([(x0, y0), (x1, y0), (x1, y1)], color="blue", opacity=0.12, stroke="ink", width=1.5)
    f.right(x1, y0, -1, -1, 7)
    f.arc(x0, y0, 20, 0, 29, color="ink", width=1.1)
    f.text(x0 + 25, y0 - 4, "θ", anchor="start", size=11, italic=True)
    f.text((x0 + x1) / 2, y0 + 15, "√(a² − x²)", size=11)
    f.text(x1 + 6, (y0 + y1) / 2 + 4, "x", anchor="start", size=12, italic=True)
    f.text((x0 + x1) / 2 - 8, (y0 + y1) / 2 - 6, "a", anchor="end", size=12, italic=True)
    f.text((x0 + x1) / 2 + 12, 14, "x = a sin θ", size=11)
    # triangle 2
    x0, x1 = 200, 318
    f.poly([(x0, y0), (x1, y0), (x1, y1)], color="blue", opacity=0.12, stroke="ink", width=1.5)
    f.right(x1, y0, -1, -1, 7)
    f.arc(x0, y0, 20, 0, 29, color="ink", width=1.1)
    f.text(x0 + 25, y0 - 4, "θ", anchor="start", size=11, italic=True)
    f.text((x0 + x1) / 2, y0 + 15, "a", size=12, italic=True)
    f.text(x1 + 6, (y0 + y1) / 2 + 4, "x", anchor="start", size=12, italic=True)
    f.text((x0 + x1) / 2 - 8, (y0 + y1) / 2 - 6, "√(a² + x²)", anchor="end", size=11)
    f.text((x0 + x1) / 2 + 12, 14, "x = a tan θ", size=11)
    save(name, f)


def segment_q12(name, w=190, h=170):
    """Exercise 12E Q12(b): the segment cut off by the chord AB subtending alpha at O."""
    cx, cy, R = 82, 88, 62
    half = 46
    f = Fig(w, h)
    ax, ay = pt(cx, cy, R, half)
    bx, by = pt(cx, cy, R, -half)
    f.path(f"M{ax:.1f},{ay:.1f} A{R},{R} 0 0 1 {bx:.1f},{by:.1f} Z", color="blue", width=1.4,
           fill="blue", opacity=0.3)
    circle(f, cx, cy, R)
    frame(f, cx, cy, R, ext=14)
    f.line(cx, cy, ax, ay, width=1.2).line(cx, cy, bx, by, width=1.2)
    f.text(ax + 2, ay - 6, "A", anchor="start", size=11, italic=True)
    f.text(bx + 2, by + 13, "B", anchor="start", size=11, italic=True)
    f.text(cx - 6, cy + 14, "O", anchor="end", size=11, italic=True)
    f.text(cx + R + 4, cy + 14, "r", anchor="start", size=11, italic=True)
    f.text(cx + 22, cy - 9, "α/2", anchor="start", size=10)
    f.text(cx + 22, cy + 14, "α/2", anchor="start", size=10)
    save(name, f)


if __name__ == "__main__":
    half_segment("c12e_ex21", "3√2", "6")
    half_segment("a12e_c2demo", "2√2", "4")
    sector_triangle("a12e_c2yt")
    triangles("c12e_tri")
    segment_q12("c12e_q12")
