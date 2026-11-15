"""Generate the expansion homework (questions and answers) from fixed number choices.
Answers are computed with sympy; the check script workspace/checks/expand.py re-derives them from the printed TeX."""
import sympy as sp
x, y, a, b = sp.symbols('x y a b')

TYPES = [
 ("(x+a)(x+b)",   lambda p, q: (x+p)*(x+q),   [(3,4),(9,6)]),
 ("(x+a)(x-b)",   lambda p, q: (x+p)*(x-q),   [(7,3),(5,6)]),
 ("(x-a)(x+b)",   lambda p, q: (x-p)*(x+q),   [(2,6),(9,8)]),
 ("(x-a)(x-b)",   lambda p, q: (x-p)*(x-q),   [(2,3),(7,9)]),
 ("(x+y+a)(x+b)", lambda p, q: (x+y+p)*(x+q), [(2,3),(8,5)]),
 ("(x+a)(x+y+b)", lambda p, q: (x+p)*(x+y+q), [(3,2),(7,6)]),
 ("(x-a)(x+a)",   lambda p, q: (x-p)*(x+p),   [(4,0),(8,0)]),
 ("(x-a)^2",      lambda p, q: (x-p)**2,      [(8,0),(11,0)]),
]
TITLES = ["Two sums", "A sum and a difference", "A difference and a sum", "Two differences",
          "Three terms times two terms", "Two terms times three terms",
          "A difference times a sum of the same numbers", "Squaring a difference"]
ORDER = [x**2, x*y, x, y, sp.Integer(1)]

def bracket(terms):
    """terms: list of (sign, text) for one bracket"""
    s = terms[0][1]
    for sg, t in terms[1:]:
        s += sg + t
    return "(" + s + ")"

def q_tex(kind, p, q):
    if kind == "(x+a)(x+b)":   return f"(x+{p})(x+{q})"
    if kind == "(x+a)(x-b)":   return f"(x+{p})(x-{q})"
    if kind == "(x-a)(x+b)":   return f"(x-{p})(x+{q})"
    if kind == "(x-a)(x-b)":   return f"(x-{p})(x-{q})"
    if kind == "(x+y+a)(x+b)": return f"(x+y+{p})(x+{q})"
    if kind == "(x+a)(x+y+b)": return f"(x+{p})(x+y+{q})"
    if kind == "(x-a)(x+a)":   return f"(x-{p})(x+{p})"
    if kind == "(x-a)^2":      return f"(x-{p})^2"

def letter_tex(kind):
    return {"(x-a)^2": "(x-a)^2"}.get(kind, kind)

def mono_tex(m):
    return {x**2: "x^2", x*y: "xy", x: "x", y: "y", 1: ""}[m]

def poly_tex(expr):
    """Numeric polynomial in standard order x^2, xy, x, y, const."""
    P = sp.Poly(sp.expand(expr), x, y)
    out = ""
    for m in ORDER:
        c = P.coeff_monomial(m)
        if c == 0: continue
        mt = mono_tex(m)
        mag = abs(c)
        body = (str(mag) if (mag != 1 or mt == "") else "") + mt
        if out == "":
            out = ("-" if c < 0 else "") + body
        else:
            out += ("-" if c < 0 else "+") + body
    return out

def foil_terms(kind, p, q):
    """The unsimplified line: every product written out, in bracket order."""
    if kind == "(x-a)^2":
        L, R = [(1, "x"), (-p, "")], [(1, "x"), (-p, "")]
    else:
        s = q_tex(kind, p, q)
        left, right = s[1:].split(")(")
        right = right.rstrip(")")
        def parse(br):
            toks, cur = [], ""
            for ch in br:
                if ch in "+-" and cur: toks.append(cur); cur = ch
                else: cur += ch
            toks.append(cur)
            res = []
            for t in toks:
                sg = -1 if t.startswith("-") else 1
                t = t.lstrip("+-")
                if t.isdigit(): res.append((sg*int(t), ""))
                else: res.append((sg, t))
            return res
        L, R = parse(left), parse(right)
    prods = []
    for c1, v1 in L:
        for c2, v2 in R:
            c = c1*c2
            v = v1 + v2
            v = {"xx": "x^2", "yx": "xy"}.get(v, v)
            prods.append((c, v))
    out = ""
    for c, v in prods:
        mag = abs(c)
        body = (str(mag) if (mag != 1 or v == "") else "") + v
        out += ("-" if c < 0 else ("+" if out else "")) + body
    return out

LETTER_ANS = {
 "(x+a)(x+b)":   ("x^2+bx+ax+ab", "x^2+(a+b)x+ab"),
 "(x+a)(x-b)":   ("x^2-bx+ax-ab", "x^2+(a-b)x-ab"),
 "(x-a)(x+b)":   ("x^2+bx-ax-ab", "x^2+(b-a)x-ab"),
 "(x-a)(x-b)":   ("x^2-bx-ax+ab", "x^2-(a+b)x+ab"),
 "(x+y+a)(x+b)": ("x^2+bx+xy+by+ax+ab", "x^2+xy+(a+b)x+by+ab"),
 "(x+a)(x+y+b)": ("x^2+xy+bx+ax+ay+ab", "x^2+xy+(a+b)x+ay+ab"),
 "(x-a)(x+a)":   ("x^2+ax-ax-a^2", "x^2-a^2"),
 "(x-a)^2":      ("x^2-ax-ax+a^2", "x^2-2ax+a^2"),
}
LETTER_EXPR = {
 "(x+a)(x+b)": (x+a)*(x+b), "(x+a)(x-b)": (x+a)*(x-b), "(x-a)(x+b)": (x-a)*(x+b), "(x-a)(x-b)": (x-a)*(x-b),
 "(x+y+a)(x+b)": (x+y+a)*(x+b), "(x+a)(x+y+b)": (x+a)*(x+y+b), "(x-a)(x+a)": (x-a)*(x+a), "(x-a)^2": (x-a)**2,
}
LETTERS = "abcdefgh"
LETTER_WHERE = {k: ("\\(a\\) is a number" if k in ("(x-a)(x+a)", "(x-a)^2") else "\\(a\\) and \\(b\\) are numbers") for k in LETTER_ANS}
TIMES = [3, 4, 4, 4, 5, 5, 3, 3]

def build():
    q, ans = [], []
    for i, ((kind, f, nums), title) in enumerate(zip(TYPES, TITLES)):
        n = i + 1
        sec = f"Type {n}"
        hgt = 30 if kind in ("(x+y+a)(x+b)", "(x+a)(x+y+b)") else 26
        cells = []
        for j, (p, qq) in enumerate(nums):
            cells.append(f'<div><span class="pl">{LETTERS[j]}</span>\\({q_tex(kind,p,qq)}\\)</div>')
        cells.append(f'<div><span class="pl">c</span>\\({letter_tex(kind)}\\) <span class="lw">({LETTER_WHERE[kind]})</span></div>')
        q.append(f'''<div class="tsec" style="break-inside:avoid">
<div class="thead"><span class="tnum">{n}</span><span class="tform">\\({letter_tex(kind)}\\)</span><span class="ttitle">{title}</span><span class="ttime">about {TIMES[i]} min</span></div>
<div class="q"><span class="q-num">{n}</span><div class="q-body">Expand and simplify.
<div class="ex three" style="--h:{hgt}mm">{"".join(cells)}</div></div></div>
</div>''')
        rows = []
        for j, (p, qq) in enumerate(nums):
            e = f(p, qq)
            rows.append(f'<div><b>{LETTERS[j]}</b> \\({q_tex(kind,p,qq)}={foil_terms(kind,p,qq)}=\\) <span data-k="T{n}{LETTERS[j]}" data-q="{q_tex(kind,p,qq)}">\\({poly_tex(e)}\\)</span></div>')
        l1, l2 = LETTER_ANS[kind]
        ans.append(f'''<div class="asec" style="break-inside:avoid"><div class="ans-sec">Type {n} &nbsp;\\({letter_tex(kind)}\\)</div>
<div class="a"><span class="an">{n}</span><div class="ab"><div class="agrid">{"".join(rows)}<div><b>c</b> \\({letter_tex(kind)}={l1}=\\) <span data-k="T{n}L" data-q="{letter_tex(kind)}">\\({l2}\\)</span></div></div></div></div></div>''')
    return q, ans

STYLE = """<style>
.thead{break-after:avoid;display:flex;align-items:baseline;gap:3mm;border-bottom:1.6px solid var(--line-strong);padding-bottom:1mm;margin:4mm 0 2mm}
.tnum{font-weight:800;color:var(--blue);font-size:13pt}
.tform{font-size:12pt}
.ttitle{font-weight:700;color:var(--ink-soft)}
.ttime{margin-left:auto;font-size:9.3pt;color:var(--ink-faint)}
.ex{display:grid;grid-template-columns:1fr 1fr;gap:0 8mm;margin-top:1.5mm}
.ex.one{grid-template-columns:1fr}
.ex.three{grid-template-columns:1fr 1fr 1fr;gap:0 5mm}
.lw{font-size:9pt;color:var(--ink-soft)}
.ex>div{min-height:var(--h);border-bottom:1px dotted var(--line);padding-top:1mm}
.ex .pl{font-weight:700;margin-right:2mm}
.agrid{display:grid;grid-template-columns:1fr;gap:1mm 0}
.asec{margin-bottom:3mm}
</style>"""

if __name__ == "__main__":
    q, ans = build()
    total = sum(TIMES)
    rows = "".join(f'<tr><td>Type {i+1}</td><td>\\({letter_tex(k)}\\)</td><td class="m">{TIMES[i]} min</td></tr>' for i, (k, _, _) in enumerate(TYPES))
    cover = f"""{STYLE}
<style>
table.tt{{border-collapse:collapse;width:100%;font-size:10.3pt;margin:2mm 0 1mm}}
table.tt td,table.tt th{{border-bottom:1px solid var(--line);padding:1.3mm 2mm;text-align:left;vertical-align:top}}
table.tt th{{color:var(--head);font-size:9.3pt;letter-spacing:.04em;text-transform:uppercase;border-bottom:1.6px solid var(--line-strong)}}
table.tt td.m{{text-align:right;white-space:nowrap;font-family:'JetBrains Mono',monospace;color:var(--blue);font-weight:700}}
</style>
<div class="cover">
  <div class="eyebrow">Mathematics</div>
  <h1>Expanding Brackets</h1>
  <div class="sub">Homework (short version)</div>
  <div class="rule"></div>
  <p style="margin:0 0 3mm">Expand each pair of brackets and simplify by collecting like terms. Every type has two questions with numbers, then one final question with letters, where the letters stand for numbers. Work in the space under each question. Answers, with the working line, are in the separate Answers booklet.</p>
  <table class="tt">
    <tr><th>Type</th><th>Form</th><th style="text-align:right">Time</th></tr>
    {rows}
    <tr><td><b>Total</b></td><td></td><td class="m">about {total} min</td></tr>
  </table>
</div>"""
    open("cover.html", "w").write(cover)
    open("q_all.html", "w").write(STYLE + '\n<div class="lesson">\n' + "\n".join(q) + "\n</div>\n")
    open("a_all.html", "w").write(STYLE + "\n" + "\n".join(ans) + "\n")
    print("written", total, "min")
