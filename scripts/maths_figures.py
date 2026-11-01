"""Repères quadrillés en SVG, dans le style des sujets de maths (axes fléchés, graduations sur les axes).

Sert aux figures redessinées par W4ss Academy quand l'export ne donne qu'un lien vers l'image, et aux
courbes des corrigés. Les tailles sont en millimètres.
"""
import math


def frange(lo, hi, step):
    """Multiples de step compris entre lo et hi."""
    k, out = math.ceil(lo / step - 1e-9), []
    while k * step <= hi + 1e-9:
        out.append(round(k * step, 6))
        k += 1
    return out


def sample(f, a, b, n=400):
    return [(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)]


def num(v):
    return f"{v:g}".replace("-", "−")


def axes_grid(xr, yr, sx, sy, xticks, yticks, xminor, yminor, curves=(), hlines=(), dots=(), margin=7, extra=8,
              yright=False):
    """xr, yr = (min, max) ; sx, sy = mm par unité ; xticks, yticks = pas des graduations chiffrées ;
    xminor, yminor = pas du quadrillage ; curves = listes de points (coupées hors du cadre) ;
    hlines = ordonnées de droites horizontales ; dots = (x, y, texte, dx, dy) en mm ;
    yright = graduations négatives de l'axe des y écrites à droite de l'axe (quand la courbe longe l'axe à gauche)."""
    w, h = (xr[1] - xr[0]) * sx, (yr[1] - yr[0]) * sy
    W, H = w + 2 * margin + extra, h + 2 * margin + extra   # extra : place des flèches et des noms d'axes

    def X(x):
        return margin + (x - xr[0]) * sx

    def Y(y):
        return margin + extra + (yr[1] - y) * sy

    # largeur en attribut : le nettoyage des énoncés supprime les attributs style
    out = [f'<svg class="mgraph" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.1f}mm" '
           'xmlns="http://www.w3.org/2000/svg" font-family="Liberation Sans, Arial" font-size="3.3">']
    for x in frange(*xr, xminor):
        major = abs(x / xticks - round(x / xticks)) < 1e-6
        out.append(f'<line x1="{X(x):.2f}" y1="{Y(yr[1]):.2f}" x2="{X(x):.2f}" y2="{Y(yr[0]):.2f}" '
                   f'stroke="{"#9a9a9a" if major else "#d2d2d2"}" stroke-width="{0.22 if major else 0.14}"/>')
    for y in frange(*yr, yminor):
        major = abs(y / yticks - round(y / yticks)) < 1e-6
        out.append(f'<line x1="{X(xr[0]):.2f}" y1="{Y(y):.2f}" x2="{X(xr[1]):.2f}" y2="{Y(y):.2f}" '
                   f'stroke="{"#9a9a9a" if major else "#d2d2d2"}" stroke-width="{0.22 if major else 0.14}"/>')
    ax = 0 if xr[0] <= 0 <= xr[1] else xr[0]       # abscisse de l'axe des y
    ay = 0 if yr[0] <= 0 <= yr[1] else yr[0]       # ordonnée de l'axe des x
    tip = 4
    out.append(f'<line x1="{X(xr[0]) - (2 if xr[0] < 0 else 0):.2f}" y1="{Y(ay):.2f}" x2="{X(xr[1]) + tip:.2f}" y2="{Y(ay):.2f}" stroke="#111" stroke-width="0.35"/>')
    out.append(f'<line x1="{X(ax):.2f}" y1="{Y(yr[0]) + (2 if yr[0] < 0 else 0):.2f}" x2="{X(ax):.2f}" y2="{Y(yr[1]) - tip:.2f}" stroke="#111" stroke-width="0.35"/>')
    out.append(f'<path d="M{X(xr[1]) + tip + 1.6:.2f} {Y(ay):.2f} l-2.6 -1.1 v2.2 z" fill="#111"/>')
    out.append(f'<path d="M{X(ax):.2f} {Y(yr[1]) - tip - 1.6:.2f} l-1.1 2.6 h2.2 z" fill="#111"/>')
    out.append(f'<text x="{X(xr[1]) + tip + 2.6:.2f}" y="{Y(ay) + 1.2:.2f}" font-style="italic" font-size="3.8">x</text>')
    out.append(f'<text x="{X(ax) + 1.6:.2f}" y="{Y(yr[1]) - tip - 0.6:.2f}" font-style="italic" font-size="3.8">y</text>')
    for x in frange(*xr, xticks):
        if abs(x - ax) > 1e-9:
            out.append(f'<line x1="{X(x):.2f}" y1="{Y(ay) - 0.8:.2f}" x2="{X(x):.2f}" y2="{Y(ay) + 0.8:.2f}" stroke="#111" stroke-width="0.3"/>'
                       f'<text x="{X(x):.2f}" y="{Y(ay) + 4.2:.2f}" text-anchor="middle">{num(x)}</text>')
    for y in frange(*yr, yticks):
        if abs(y - ay) > 1e-9:
            right = yright and y < 0
            out.append(f'<line x1="{X(ax) - 0.8:.2f}" y1="{Y(y):.2f}" x2="{X(ax) + 0.8:.2f}" y2="{Y(y):.2f}" stroke="#111" stroke-width="0.3"/>'
                       f'<text x="{X(ax) + (1.6 if right else -1.6):.2f}" y="{Y(y) + (-0.7 if right else 1.2):.2f}" '
                       f'text-anchor="{"start" if right else "end"}">{num(y)}</text>')
    out.append(f'<text x="{X(ax) - 1.6:.2f}" y="{Y(ay) + 4.2:.2f}" text-anchor="end">0</text>')
    for pts in curves:   # tracé coupé là où la courbe sort du cadre
        d, pen = [], False
        for x, y in pts:
            inside = yr[0] <= y <= yr[1] and xr[0] <= x <= xr[1]
            if inside:
                d.append(f"{'L' if pen else 'M'}{X(x):.2f} {Y(y):.2f}")
            pen = inside
        out.append(f'<path d="{" ".join(d)}" fill="none" stroke="#111" stroke-width="0.45"/>')
    for y in hlines:
        out.append(f'<line x1="{X(xr[0]):.2f}" y1="{Y(y):.2f}" x2="{X(xr[1]):.2f}" y2="{Y(y):.2f}" stroke="#111" stroke-width="0.45"/>')
    for x, y, text, dx, dy in dots:
        out.append(f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="0.7" fill="#111"/>'
                   f'<text x="{X(x) + dx:.2f}" y="{Y(y) + dy:.2f}" font-size="3">{text}</text>')
    out.append("</svg>")
    return "".join(out)
