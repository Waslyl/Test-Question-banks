"""B.4 Thermodynamics : introductions rédigées par W4ss Academy et méthodes des QCM.

L'export B.4 (IB_Physics_B4_Thermodynamics_questions.json) ne donne pour le Paper 2 que la consigne de
chaque partie : l'introduction (données, diagramme) de la question manque. Les introductions ci-dessous
sont écrites à partir des données du markscheme officiel, pour que la correction reste valable :

    19M.2.HL.TZ1.7    cycle de Carnot entre 620 K et 340 K, gaz parfait monoatomique ;
                      e = 1 − 340/620 = 0.45 ; Q_out = 0.55 × 540 = 297 J ; V_C/V_B = (620/340)^1.5 = 2.5 ;
                      ΔS_AB = 540/620 = 0.87 J K-1
    23M.2.SL.TZ1.9    0.200 mol (pV/RT = 5.00e5 × 2.00e-3 / (8.31 × 602) = 0.200) ; A : 5.00e5 Pa, 2.00e-3 m3, 602 K ;
                      B : 3.00e4 Pa ; C : 4.60e3 Pa ; V_B = V_C = 3.33e-2 m3 (isotherme ET adiabatique le confirment) ;
                      T_C = 92 K ; Q_BC = 1.5 × 3.33e-2 × (3.00e4 − 4.60e3) = 1270 J ; e_Carnot = 1 − 92/602 = 0.85
    23M.2.HL.TZ2.7    A : 129 kPa, 27 °C ; V_B = 3 V_A ; p_B = 43 kPa ; T_C = 300 × 3^(2/3) = 624 K ;
                      p_C = 43 × 3^(5/3) = 268 kPa ; 53.2 mol : Q_CA = 1.5 × 53.2 × 8.31 × 324 = 2.15e5 J
    EXE.2.HL.TZ0.11   gaz qui occupe d'abord une moitié du récipient (1 seul micro-état), puis tout le récipient
    EXE.2.HL.TZ0.12   6 particules et 6 quanta ; A : une particule a les 6 quanta -> 6 micro-états ;
                      B : 0, 0, 0, 1, 2, 3 quanta -> 6!/3! = 120 micro-états ; ΔS = kB ln(120/6) = 3.0 kB
    EXE.2.HL.TZ0.13   50 molécules dans deux récipients reliés (1 seule façon d'en avoir 50 dans X, 50 d'en avoir 49)
    EXE.2.HL.TZ0.14   10 pièces : C(10, n) micro-états, total 1024 ; 5, 4 et 6 faces : 252 + 210 + 210 = 672 ;
                      tout pile ou tout face : 2 chances sur 1024 ; 7 faces : 120 -> ΔS = kB ln 120 = 4.8 kB

Les méthodes des QCM sont rédigées en français, comme pour B.3 (data/methods/b3.json).
"""
import math

NOTE = "introduction written by W4ss Academy from the markscheme"


def svg_pv(curves, labels, arrows=(), xmax=4.6, ymax=1.15, width=78, note=""):
    """pV schématique (sans graduation) : curves = listes de points (V, p) ; labels = (V, p, texte, dx, dy) ;
    arrows = (V, p, V2, p2) : flèche en (V, p) orientée vers (V2, p2)."""
    W, H, x0, y0 = 100, 70, 10, 62

    def X(v):
        return x0 + v / xmax * (W - x0 - 6)

    def Y(p):
        return y0 - p / ymax * (y0 - 6)

    out = [f'<svg class="mgraph pv" viewBox="0 0 {W} {H}" width="{width}mm" xmlns="http://www.w3.org/2000/svg" '
           'font-family="Liberation Sans, Arial" font-size="4.2">',
           f'<line x1="{x0}" y1="{y0}" x2="{W - 3}" y2="{y0}" stroke="#111" stroke-width="0.4"/>',
           f'<path d="M{W - 1} {y0} l-3 -1.2 v2.4 z" fill="#111"/>',
           f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="4" stroke="#111" stroke-width="0.4"/>',
           f'<path d="M{x0} 2 l-1.2 3 h2.4 z" fill="#111"/>',
           f'<text x="{W - 4}" y="{y0 + 5}" font-style="italic">V</text>',
           f'<text x="{x0 - 6}" y="7" font-style="italic">p</text>',
           f'<text x="{x0 - 4}" y="{y0 + 4}">0</text>']
    for pts in curves:
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(v):.2f} {Y(p):.2f}" for i, (v, p) in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="#111" stroke-width="0.55"/>')
    for v, p, v2, p2 in arrows:
        a = math.degrees(math.atan2(Y(p2) - Y(p), X(v2) - X(v)))
        out.append(f'<path d="M-2 -1.3 L1.5 0 L-2 1.3 Z" fill="#111" transform="translate({X(v):.2f} {Y(p):.2f}) rotate({a:.1f})"/>')
    for v, p, text, dx, dy in labels:
        out.append(f'<circle cx="{X(v):.2f}" cy="{Y(p):.2f}" r="0.8" fill="#111"/>'
                   f'<text x="{X(v) + dx:.2f}" y="{Y(p) + dy:.2f}">{text}</text>')
    if note:
        out.append(f'<text x="{W - 2}" y="9" text-anchor="end" font-size="3.4">{note}</text>')
    out.append("</svg>")
    return "".join(out)


def curve(f, a, b, n=60):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def carnot():
    """Cycle de Carnot schématique : adiabatiques exagérées (p ∝ V^-3) pour que le cycle soit lisible (pas à l'échelle)."""
    g = 3
    va, vb, vc = 0.8, 1.6, 3.0
    hot = lambda v: 1.6 / v                  # noqa: E731
    bc = lambda v: hot(vb) * (vb / v) ** g   # noqa: E731
    da = lambda v: hot(va) * (va / v) ** g   # noqa: E731
    c = bc(vc) * vc                          # isotherme froide passant par C
    cold = lambda v: c / v                   # noqa: E731
    vd = (hot(va) * va ** g / c) ** (1 / (g - 1))
    return svg_pv([curve(hot, va, vb), curve(bc, vb, vc), curve(cold, vd, vc), curve(da, va, vd)],
                  [(va, hot(va), "A", -5, -1.5), (vb, hot(vb), "B", 1.5, -1.5),
                   (vc, cold(vc), "C", 1.5, 4), (vd, cold(vd), "D", -5, 4)],
                  arrows=[((va + vb) / 2, hot((va + vb) / 2), vb, hot(vb)), ((vc + vd) / 2, cold((vc + vd) / 2), vd, cold(vd)),
                          ((vb + vc) / 2, bc((vb + vc) / 2), (vb + vc) / 2 + 0.1, bc((vb + vc) / 2 + 0.1)),
                          ((va + vd) / 2, da((va + vd) / 2), (va + vd) / 2 - 0.1, da((va + vd) / 2 - 0.1))],
                  xmax=3.6, ymax=2.3, note="not to scale")


def cycle_23m_sl():
    """A→B (isotherme, moins pentue), B→C (verticale), C→A (adiabatique, plus pentue) — pas à l'échelle."""
    iso = lambda v: 1 / v                # noqa: E731
    adi = lambda v: v ** (-5 / 3)        # noqa: E731
    return svg_pv([curve(iso, 1, 4), [(4, iso(4)), (4, adi(4))], curve(adi, 1, 4)],
                  [(1, 1, "A", -5, 0), (4, iso(4), "B", 1.5, -1), (4, adi(4), "C", 1.5, 3)],
                  arrows=[(2.2, iso(2.2), 2.3, iso(2.3)), (4, 0.17, 4, 0.12), (2.0, adi(2.0), 1.9, adi(1.9))],
                  xmax=4.6, ymax=1.15, note="not to scale")


def ab_23m_hl():
    """Processus AB tracé sur un quadrillage ; BC et CA sont à tracer par l'élève (partie (b))."""
    from written_stems import graph
    iso = lambda v: 129 / v              # noqa: E731
    return graph((0, 3.5), (0, 300), (0.5, 0.1), (50, 10),
                 '<tspan font-style="italic">V</tspan> / <tspan font-style="italic">V</tspan><tspan baseline-shift="sub" font-size="10">A</tspan>',
                 '<tspan font-style="italic">p</tspan> / kPa',
                 curves=[curve(iso, 1, 3)], arrows=[(2.0, iso(2.0), 2.1, iso(2.1))],
                 labels=[(1, 129, "A", -16, -6), (3, 43, "B", 6, -8)], fmt="{:g}")


def p(text):
    return f"<p>{text}</p>"


STEMS = {
    "19M.2.HL.TZ1.7": dict(note=NOTE, intro=(
        p("An ideal monatomic gas is the working substance of a heat engine. The gas is taken through the Carnot "
          "cycle ABCDA shown on the <em>pV</em> diagram.")
        + carnot()
        + p("A → B: isothermal expansion at 620 K</p><p>B → C: adiabatic expansion</p><p>"
            "C → D: isothermal compression at 340 K</p><p>D → A: adiabatic compression"))),
    "23M.2.SL.TZ1.9": dict(note=NOTE, intro=(
        p("0.200 mol of an ideal monatomic gas is taken around the cycle A → B → C → A shown on the <em>pV</em> "
          "diagram. One of the processes between A and B and between C and A is isothermal, the other is "
          "adiabatic. Process BC takes place at constant volume.")
        + cycle_23m_sl()
        + p("At A the pressure of the gas is 5.00 × 10<sup>5</sup> Pa, its volume is 2.00 × 10<sup>−3</sup> m<sup>3</sup> "
            "and its temperature is 602 K. The pressure at B is 3.00 × 10<sup>4</sup> Pa and the pressure at C is "
            "4.60 × 10<sup>3</sup> Pa."))),
    "23M.2.HL.TZ2.7": dict(note=NOTE, intro=(
        p("A fixed quantity of an ideal monatomic gas is trapped in a cylinder. At A the pressure of the gas is "
          "129 kPa and its temperature is 27 °C. The gas undergoes the following cycle:")
        + p("A → B: isothermal expansion until the volume is three times the volume at A</p><p>"
            "B → C: adiabatic compression back to the volume at A</p><p>"
            "C → A: cooling at constant volume back to A")
        + p("The <em>pV</em> diagram shows the process AB.") + ab_23m_hl())),
    "EXE.2.HL.TZ0.11": dict(note=NOTE, intro=(
        p("An insulated container is divided into two equal halves by a partition. A gas is initially confined to "
          "the left half (configuration A). The partition is removed and the gas expands to fill the whole "
          "container, so that there are molecules in both halves (configuration B).")
        + p("Treat the molecules as distinguishable. A microstate specifies which half of the container each "
            "molecule is in."))),
    "EXE.2.HL.TZ0.12": dict(note=NOTE, intro=(
        p("An isolated system consists of six distinguishable particles that share six quanta of energy. Each "
          "particle can have 0, 1, 2, … quanta.")
        + p("In configuration A, one particle has all six quanta and the other five particles have none.</p><p>"
            "In configuration B, three particles have no energy and the other three particles have 1, 2 and 3 "
            "quanta."))),
    "EXE.2.HL.TZ0.13": dict(note=NOTE, intro=(
        p("Fifty identical gas molecules can move freely between two connected containers, X and Y.")
        + p("Case 1: all 50 molecules are in container X.</p><p>Case 2: 49 molecules are in X and 1 molecule is in Y."))),
    "EXE.2.HL.TZ0.14": dict(note=NOTE, intro=(
        p("Ten identical coins are thrown at the same time. Each coin lands heads or tails with equal probability. "
          "A macrostate is defined by the number of heads; a microstate specifies the result for each individual "
          "coin. The table shows the number of microstates of each macrostate.")
        + '<table class="data-table"><tr><th>Number of heads</th>'
        + "".join(f"<td>{n}</td>" for n in range(11)) + "</tr><tr><th>Number of microstates</th>"
        + "".join(f"<td>{math.comb(10, n)}</td>" for n in range(11)) + "</tr></table>")),
}

# méthodes des QCM (réponse de data/paper1a.js, vérifiée par le calcul)
METHODS = {
    "EXE.1A.HL.TZ0.17": ("C", [
        "Sur un diagramme <em>pV</em>, une adiabatique est plus pentue qu'une isotherme passant par le même point.",
        "Z → X est la courbe la plus pentue : c'est l'adiabatique. X → Y, moins pentue, est l'isotherme.",
        "Y → Z est vertical : le volume ne change pas, c'est l'isovolumétrique (isochore). Réponse C."]),
    "EXE.1A.HL.TZ0.18": ("B", [
        "L'énergie interne d'un gaz parfait ne dépend que de sa température.",
        "La transformation est isotherme, donc Δ<em>U</em> = 0 : les 100 J de travail fournis par le gaz viennent "
        "de 100 J de chaleur reçue (<em>Q</em> = Δ<em>U</em> + <em>W</em>)."]),
    "EXE.1A.HL.TZ0.19": ("A", [
        "<em>S</em> = <em>k</em><sub>B</sub> ln Ω : l'entropie augmente avec le nombre de micro-états Ω.",
        "Dans un système isolé, une transformation irréversible fait augmenter l'entropie : l'état final a "
        "<strong>plus</strong> de micro-états que l'état initial."]),
    "EXE.1A.HL.TZ0.20": ("D", [
        "Le deuxième principe s'applique au système <strong>et</strong> à son environnement : leur entropie totale "
        "ne diminue jamais.",
        "L'entropie d'un système non isolé peut donc diminuer, mais seulement si celle de l'environnement augmente "
        "au moins autant."]),
    "EXE.1A.HL.TZ0.21": ("A", [
        "Transformation isotherme : Δ<em>S</em> = <em>Q</em> / <em>T</em>, avec <em>T</em> en kelvins.",
        "<em>T</em> = 27 + 273 = 300 K, donc Δ<em>S</em> = 200 / 300 = 0.67 J K<sup>−1</sup>."]),
    "EXE.1A.HL.TZ0.22": ("B", [
        "Chaleur reçue pour fondre la glace : <em>Q</em> = <em>mL</em> = 0.050 × 335 = 16.75 kJ.",
        "La fusion se fait à 0 °C = 273 K : Δ<em>S</em> = <em>Q</em> / <em>T</em> = 16.75 / 273 = 0.061 kJ K<sup>−1</sup>."]),
    "EXE.1A.HL.TZ0.23": ("B", [
        "I est vrai : le cycle de Carnot est formé de transformations réversibles.",
        "II est faux : pour un cycle réversible, la variation totale d'entropie est nulle, pas positive.",
        "III est vrai : la chaleur n'est échangée que pendant les deux isothermes (pas pendant les adiabatiques). "
        "Réponse B."]),
    "EXE.1A.HL.TZ0.24": ("D", [
        "Deuxième principe : l'entropie de l'Univers augmente lors d'une transformation irréversible et reste "
        "constante lors d'une transformation réversible.",
        "Elle ne diminue donc jamais. « Augmente toujours » (A) est faux pour une transformation réversible."]),
    "SPM.1A.HL.TZ0.11": ("A", [
        "L'énergie interne est une fonction d'état : elle ne dépend que de l'état du gaz.",
        "Après un cycle, le gaz revient à son état initial, donc Δ<em>U</em> = 0."]),
    "SPM.1A.HL.TZ0.12": ("D", [
        "Le réfrigérateur consomme de l'énergie électrique, finalement dissipée en énergie thermique dans la pièce "
        "fermée.",
        "Ces transformations sont irréversibles : l'entropie de la pièce augmente (le réfrigérateur ne la refroidit "
        "pas, porte ouverte)."]),
}
