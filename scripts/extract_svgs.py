# Regenerate svg/ from the brand guidelines PDF:
#   uvx --with pymupdf python scripts/extract_svgs.py "Comfy Brand guidelines.pdf" svg
import sys, fitz
pdf, out = sys.argv[1], sys.argv[2]
d = fitz.open(pdf)
BLUE, YELLOW = "#172DD7", "#F0FF41"
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")

def path(g, ox, oy):
    s, cur = [], None
    def P(p): return f"{f(p.x-ox)} {f(p.y-oy)}"
    for it in g["items"]:
        k = it[0]
        if k == "re":
            r = it[1]; s.append(f"M{f(r.x0-ox)} {f(r.y0-oy)}H{f(r.x1-ox)}V{f(r.y1-oy)}H{f(r.x0-ox)}Z"); cur=None; continue
        if k == "qu":
            q = it[1]; s.append(f"M{P(q.ul)}L{P(q.ur)}L{P(q.lr)}L{P(q.ll)}Z"); cur=None; continue
        a = it[1]
        if cur is None or abs(cur.x-a.x)>1e-3 or abs(cur.y-a.y)>1e-3:
            if s and not s[-1].endswith("Z"): s.append("Z")
            s.append(f"M{P(a)}")
        if k == "l": s.append(f"L{P(it[2])}"); cur = it[2]
        elif k == "c": s.append(f"C{P(it[2])} {P(it[3])} {P(it[4])}"); cur = it[4]
    if s and not s[-1].endswith("Z"): s.append("Z")
    return "".join(s)

def svg(title, w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w)}" height="{f(h)}">\n'
            f'  <title>{title}</title>\n{body}</svg>\n')

def logo(page, idxs, name):
    gs = [d[page-1].get_drawings()[i] for i in idxs]
    r = gs[0]["rect"]
    for g in gs[1:]: r |= g["rect"]
    for col, cname in ((BLUE,"Blue"),(YELLOW,"Yellow")):
        body = "".join(f'  <path fill="{col}"{" fill-rule=\"evenodd\"" if g.get("even_odd") else ""} d="{path(g, r.x0, r.y0)}"/>\n' for g in gs)
        open(f"{out}/{name} ({cname}).svg","w").write(svg(f"{name} ({cname})", r.width, r.height, body))

logo(6, [10], "Logo - Comfy")
logo(7, [10, 11], "Logo - Comfy UI")
logo(8, [10], "Logo - C")

dr = d[7].get_drawings()
bg, c = dr[12]["rect"], dr[13]
for bgcol, fg, cname in ((BLUE, YELLOW, "Blue"), (YELLOW, BLUE, "Yellow")):
    body = (f'  <rect width="{f(bg.width)}" height="{f(bg.height)}" fill="{bgcol}"/>\n'
            f'  <path fill="{fg}"{" fill-rule=\"evenodd\"" if c.get("even_odd") else ""} d="{path(c, bg.x0, bg.y0)}"/>\n')
    open(f"{out}/App logo - C ({cname}).svg","w").write(svg(f"App logo - C ({cname})", bg.width, bg.height, body))

