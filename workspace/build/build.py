"""Assemble a chapter's HTML fragments into lesson/answers HTML and print them to PDF.

usage: python build.py <chapter_dir> [lesson|answers|all]
<chapter_dir>/pack.json:
  {"chapter": "Chapter 11 Trigonometric Equations",
   "lesson":  {"parts": [...fragment files...], "out": "....pdf"},
   "answers": {"parts": [...], "out": "....pdf"}}
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

ICONS = {
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.4"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M18 6l-2.5 2.5M8.5 15.5L6 18"/>',
    "key": '<circle cx="8" cy="8" r="4"/><path d="M11 11l8 8M16 16l2-2M18 18l2-2"/>',
    "pencil": '<path d="M14 4l6 6L9 21H3v-6L14 4z"/><path d="M12.5 6.5l5 5"/>',
    "hand": '<path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V11M12 10.5V4.5a1.5 1.5 0 0 1 3 0V11M15 11V6.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-1.5a5 5 0 0 1-3.6-1.6L4 14.5a1.6 1.6 0 0 1 2.4-2L9 15"/>',
    "award": '<circle cx="12" cy="9" r="5"/><path d="M8.5 13.5L7 21l5-2.5L17 21l-1.5-7.5"/>',
    "alert": '<path d="M12 4L2.5 20h19L12 4z"/><path d="M12 10v4.5M12 17.5v.01"/>',
    "check": '<circle cx="12" cy="12" r="8.5"/><path d="M8.5 12.2l2.4 2.4 4.6-5"/>',
    "book": '<path d="M12 5.5C10.5 4.4 8.5 4 4 4.4V18c4.5-.4 6.5 0 8 1.1 1.5-1.1 3.5-1.5 8-1.1V4.4C15.5 4 13.5 4.4 12 5.5z"/><path d="M12 5.5v13.6"/>',
    "loop": '<path d="M4 12a8 8 0 0 1 13.5-5.8L20 8"/><path d="M20 4v4h-4"/><path d="M20 12a8 8 0 0 1-13.5 5.8L4 16"/><path d="M4 20v-4h4"/>',
    "bulb": '<path d="M9 17h6M9.5 20h5"/><path d="M12 3a6 6 0 0 0-3.5 10.8c.6.5 1 1.2 1 2h5c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z"/>',
    "note": '<path d="M5 4h14v11l-5 5H5z"/><path d="M14 20v-5h5"/><path d="M8 9h8M8 13h4"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
}
DIFF = {"F": ("easy", "Foundation"), "D": ("med", "Development"), "E": ("chal", "Enrichment")}


def sec(m):
    accent, icon, title = m.group(1), m.group(2), m.group(3)
    sub = m.group(4)
    svg = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
           'stroke-linecap="round" stroke-linejoin="round">' + ICONS[icon] + '</svg>')
    s = f'<span class="sec-sub">· {sub}</span>' if sub else ''
    return (f'<div class="sec-head ac-{accent}"><span class="sec-chip" style="background:var(--{accent}-tint)">'
            f'{svg}</span><span class="sec-title">{title}</span>{s}<span class="sec-rule"></span></div>')


def escape_math(html):
    """Escape < and > inside \\( \\) and \\[ \\] so the HTML parser never sees a tag."""
    def esc(m):
        return m.group(0).replace("<", "&lt;").replace(">", "&gt;")
    html = re.sub(r"\\\((.+?)\\\)", esc, html, flags=re.S)
    return re.sub(r"\\\[(.+?)\\\]", esc, html, flags=re.S)


def expand(html, chdir, title=""):
    html = escape_math(html)
    html = re.sub(r"\{\{ahead:([^}]+)\}\}", lambda m: f'<div class="ans-head"><div class="ans-title">{title}</div><div class="eyebrow">{m.group(1)}</div><div class="rule"></div></div>', html)
    html = re.sub(r"\{\{sec:(\w+):(\w+):([^:}]+)(?::([^}]+))?\}\}", sec, html)
    html = re.sub(r"\{\{work:(\d+)\}\}", lambda m: f'<div class="writebox" style="height:{m.group(1)}mm"></div>', html)
    html = re.sub(r"\{\{band:([FDE])\}\}", lambda m: f'<div class="band"><span class="diff diff-{DIFF[m.group(1)][0]}">{DIFF[m.group(1)][1]}</span><span class="line"></span></div>', html)
    html = re.sub(r"\{\{([FDE])\}\}", lambda m: f'<span class="diff diff-{DIFF[m.group(1)][0]}">{DIFF[m.group(1)][1]}</span>', html)

    def svg(m):
        path = os.path.join(chdir, "svg", m.group(1) + ".svg")
        with open(path, encoding="utf-8") as f:
            return '<div class="fig">' + f.read() + '</div>'
    html = re.sub(r"\{\{svg:([\w-]+)\}\}", svg, html)
    return html


PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css}">
<script>
window.MathJax = {{
  tex: {{ inlineMath: [["\\\\(", "\\\\)"]], displayMath: [["\\\\[", "\\\\]"]], processEscapes: true, macros: {{ tv: ["\\\\underset{{\\\\sim}}{{#1}}", 1] }} }},
  svg: {{ fontCache: "local", displayAlign: "left" }},
  startup: {{ pageReady: () => MathJax.startup.defaultPageReady().then(() =>
      document.fonts.ready.then(() => {{ window.__ready = true; }})) }}
}};
</script>
<script src="{mj}" async></script></head><body>
{body}
</body></html>"""


def build(chdir, kind):
    with open(os.path.join(chdir, "pack.json"), encoding="utf-8") as f:
        pack = json.load(f)
    spec = pack[kind]
    body = []
    for part in spec["parts"]:
        with open(os.path.join(chdir, part), encoding="utf-8") as f:
            body.append(expand(f.read(), chdir, spec.get("heading", "")))
    html_path = os.path.join(chdir, kind + ".html")
    css = os.path.relpath(os.path.join(HERE, "pack.css"), chdir).replace("\\", "/")
    mj = os.path.relpath(os.path.join(HERE, "vendor", "mathjax-tex-svg.js"), chdir).replace("\\", "/")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(PAGE.format(title=spec.get("title", pack["chapter"]), css=css, mj=mj, body="\n".join(body)))
    out = spec["out"]
    env = dict(os.environ)
    if "header" in pack:                      # optional page-header text (print.mjs reads PACK_HEADER)
        env["PACK_HEADER"] = pack["header"]
    subprocess.run(["node", os.path.join(HERE, "print.mjs"), html_path, out,
                    spec.get("footer", pack["chapter"])], check=True, env=env)
    print("wrote", out)


if __name__ == "__main__":
    chdir = os.path.abspath(sys.argv[1])
    kinds = ["lesson", "answers"] if len(sys.argv) < 3 or sys.argv[2] == "all" else [sys.argv[2]]
    for k in kinds:
        build(chdir, k)
