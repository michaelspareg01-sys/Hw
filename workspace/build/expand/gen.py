"""Generate the expansion homework (questions and answers) from fixed number choices.
Answers are computed with sympy; the check script workspace/checks/expand.py re-derives them from the printed TeX."""
import sympy as sp
x, y, a, b = sp.symbols('x y a b')

TYPES = [
 ("(x+a)(x+b)",   lambda p, q: (x+p)*(x+q),   [(2,3),(4,5),(1,7),(6,2),(3,9),(8,5),(10,4),(12,7)]),
 ("(x+a)(x-b)",   lambda p, q: (x+p)*(x-q),   [(5,2),(3,7),(4,3),(6,9),(8,1),(2,10),(9,4),(11,6)]),
 ("(x-a)(x+b)",   lambda p, q: (x-p)*(x+q),   [(3,5),(6,2),(4,5),(7,1),(2,9),(10,3),(5,12),(8,7)]),
 ("(x-a)(x-b)",   lambda p, q: (x-p)*(x-q),   [(1,2),(3,4),(5,2),(6,7),(2,9),(8,3),(10,5),(4,11)]),
 ("(x+y+a)(x+b)", lambda p, q: (x+y+p)*(x+q), [(1,2),(3,4),(2,5),(5,1),(4,6),(7,3),(6,8),(9,2)]),
 ("(x+a)(x+y+b)", lambda p, q: (x+p)*(x+y+q), [(2,1),(3,5),(4,2),(1,6),(5,7),(8,3),(6,4),(10,9)]),
 ("(x-a)(x+a)",   lambda p, q: (x-p)*(x+p),   [(2,0),(5,0),(3,0),(7,0),(1,0),(9,0),(10,0),(12,0)]),
 ("(x-a)^2",      lambda p, q: (x-p)**2,      [(3,0),(1,0),(5,0),(2,0),(6,0),(4,0),(9,0),(7,0)]),
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
TIMES = [9, 10, 10, 10, 13, 13, 7, 9]

def build():
    q, ans = [], []
    for i, ((kind, f, nums), title) in enumerate(zip(TYPES, TITLES)):
        n = i + 1
        sec = f"Type {n}"
        hgt = 24 if kind in ("(x+y+a)(x+b)", "(x+a)(x+y+b)") else 19
        cells = []
        for j, (p, qq) in enumerate(nums):
            cells.append(f'<div><span class="pl">{LETTERS[j]}</span>\\({q_tex(kind,p,qq)}\\)</div>')
        q.append(f'''<div class="tsec">
<div class="thead"><span class="tnum">{n}</span><span class="tform">\\({letter_tex(kind)}\\)</span><span class="ttitle">{title}</span><span class="ttime">about {TIMES[i]} min</span></div>
<div class="q" style="break-inside:avoid"><span class="q-num">{n}.1</span><div class="q-body">Expand and simplify.
<div class="ex" style="--h:{hgt}mm">{"".join(cells)}</div></div></div>
<div class="q" style="break-inside:avoid;break-before:avoid"><span class="q-num">{n}.2</span><div class="q-body">Now use letters. Expand and simplify \\({letter_tex(kind)}\\), where {LETTER_WHERE[kind]}.
<div class="ex one" style="--h:{hgt}mm"><div></div></div></div></div>
</div>''')
        rows = []
        for j, (p, qq) in enumerate(nums):
            e = f(p, qq)
            rows.append(f'<div><b>{LETTERS[j]}</b> \\({q_tex(kind,p,qq)}={foil_terms(kind,p,qq)}=\\) <span data-k="T{n}{LETTERS[j]}" data-q="{q_tex(kind,p,qq)}">\\({poly_tex(e)}\\)</span></div>')
        l1, l2 = LETTER_ANS[kind]
        ans.append(f'''<div class="asec" style="break-inside:avoid"><div class="ans-sec">Type {n} &nbsp;\\({letter_tex(kind)}\\)</div>
<div class="a"><span class="an">{n}.1</span><div class="ab"><div class="agrid">{"".join(rows)}</div></div></div>
<div class="a"><span class="an">{n}.2</span><div class="ab">\\({letter_tex(kind)}={l1}=\\) <span data-k="T{n}L" data-q="{letter_tex(kind)}">\\({l2}\\)</span></div></div></div>''')
    return q, ans

STYLE = """<style>
.thead{break-after:avoid;display:flex;align-items:baseline;gap:3mm;border-bottom:1.6px solid var(--line-strong);padding-bottom:1mm;margin:4mm 0 2mm}
.tnum{font-weight:800;color:var(--blue);font-size:13pt}
.tform{font-size:12pt}
.ttitle{font-weight:700;color:var(--ink-soft)}
.ttime{margin-left:auto;font-size:9.3pt;color:var(--ink-faint)}
.ex{display:grid;grid-template-columns:1fr 1fr;gap:0 8mm;margin-top:1.5mm}
.ex.one{grid-template-columns:1fr}
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
  <div class="sub">Homework</div>
  <div class="rule"></div>
  <p style="margin:0 0 3mm">Expand each pair of brackets and simplify by collecting like terms. Every type has eight questions with numbers, then one final question with letters. Work in the space under each question. Answers, with the working line, are in the separate Answers booklet.</p>
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
