"""Textes d'introduction rédigés par W4ss Academy pour les questions B.3 dont l'introduction manque dans la source.

Chaque donnée est tirée du markscheme officiel de la question, pour que la correction reste valable :
    22N.2.SL.TZ0.2   250 kg d'eau, 15 °C -> 30 °C, 680 W m-2, rendement 30 %, albédo 0.20, émissivité 0.97
                     (A = 250 × 4200 × 15 / (0.30 × 680 × 3600) = 21 m2 ; T = (544 / 0.97σ)^1/4 = 315 K = 42 °C)
    23M.2.SL.TZ2.2   graphe pV = 1.50 × (θ + 273) J, donc pV/T = 1.50 J K-1 et intercept à −273 °C ;
                     molécule de 4.7 × 10-26 kg -> masse = (1.50 / 8.31) × 6.02 × 10^23 × 4.7 × 10-26 = 5.1 g
    EXE.2.SL.TZ0.8   p = 1.8 × 10^5 Pa, ρ = 2.0 kg m-3 -> v = √(3p/ρ) = 520 m s-1
    EXE.2.SL.TZ0.10  2.0 mol d'oxygène, 0.36 m3, 260 K -> p = 12 kPa, m = 6.4 × 10-2 kg, v = 450 m s-1

Chaque entrée donne les options attendues par build_exam.p2_section : intro, pre (texte avant une partie), note.
"""

NOTE = "introduction written by W4ss Academy from the markscheme"


def pv_theta_graph():
    """Graphe de pV (J) en fonction de θ (°C) pour 23M.2.SL.TZ2.2 : droite pV = 1.50 (θ + 273)."""
    x0, y0, w, h = 78, 18, 480, 330            # zone de tracé (unités du viewBox)
    tmin, tmax, pmin, pmax = 0, 100, 400, 580

    def X(t):
        return x0 + (t - tmin) * w / (tmax - tmin)

    def Y(p):
        return y0 + h - (p - pmin) * h / (pmax - pmin)

    out = [f'<svg class="graph" viewBox="0 0 600 410" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Liberation Sans, Arial" font-size="13">']
    for t in range(tmin, tmax + 1, 2):        # grille fine : 2 °C et 5 J
        major = t % 10 == 0
        out.append(f'<line x1="{X(t):.1f}" y1="{y0}" x2="{X(t):.1f}" y2="{y0 + h}" stroke="{"#888" if major else "#ccc"}" stroke-width="{0.9 if major else 0.5}"/>')
    for p in range(pmin, pmax + 1, 5):
        major = p % 20 == 0
        out.append(f'<line x1="{x0}" y1="{Y(p):.1f}" x2="{x0 + w}" y2="{Y(p):.1f}" stroke="{"#888" if major else "#ccc"}" stroke-width="{0.9 if major else 0.5}"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="1.2"/>')
    for t in range(tmin, tmax + 1, 20):
        out.append(f'<text x="{X(t):.1f}" y="{y0 + h + 18}" text-anchor="middle">{t}</text>')
    for p in range(pmin, pmax + 1, 20):
        out.append(f'<text x="{x0 - 8}" y="{Y(p) + 4:.1f}" text-anchor="end">{p}</text>')
    out.append(f'<text x="{x0 + w / 2}" y="{y0 + h + 42}" text-anchor="middle"><tspan font-style="italic">θ</tspan> / °C</text>')
    out.append(f'<text x="20" y="{y0 + h / 2}" text-anchor="middle" transform="rotate(-90 20 {y0 + h / 2})">'
               f'<tspan font-style="italic">pV</tspan> / J</text>')
    pv = lambda t: 1.50 * (t + 273)
    out.append(f'<line x1="{X(0):.1f}" y1="{Y(pv(0)):.1f}" x2="{X(100):.1f}" y2="{Y(pv(100)):.1f}" stroke="#111" stroke-width="1.6"/>')
    for t in range(10, 100, 20):              # points de mesure
        cx, cy = X(t), Y(pv(t))
        out.append(f'<path d="M{cx - 5:.1f} {cy - 5:.1f} L{cx + 5:.1f} {cy + 5:.1f} M{cx - 5:.1f} {cy + 5:.1f} L{cx + 5:.1f} {cy - 5:.1f}" stroke="#111" stroke-width="1.4"/>')
    out.append("</svg>")
    return "".join(out)


STEMS = {
    "EXE.2.SL.TZ0.10": dict(
        note=NOTE,
        intro="<p>A container of volume 0.36 m<sup>3</sup> holds 2.0 mol of oxygen gas at a temperature of 260 K. "
              "Assume that the oxygen behaves as an ideal gas.</p>"
              "<p>Molar mass of oxygen = 32 g mol<sup>−1</sup></p>"),
    "EXE.2.SL.TZ0.8": dict(
        note=NOTE,
        intro="<p>A container holds a sample of air at a pressure of 1.8 × 10<sup>5</sup> Pa. The density of the air "
              "in the container is 2.0 kg m<sup>−3</sup>. Assume that the air behaves as an ideal gas.</p>"),
    "23M.2.SL.TZ2.2": dict(
        note=NOTE + " (graph drawn by W4ss Academy)",
        intro="<p>A fixed mass of a gas is kept in a container. The graph shows how the product <em>pV</em> of the "
              "pressure <em>p</em> and the volume <em>V</em> of the gas varies with its temperature <em>θ</em> in °C.</p>"
              + pv_theta_graph(),
        pre={"c": "<p>The mass of one molecule of the gas is 4.7 × 10<sup>−26</sup> kg.</p>"}),
    "22N.2.SL.TZ0.2": dict(
        note=NOTE,
        intro="<p>A solar heating panel on the roof of a house heats the water in a storage tank. The tank contains "
              "250 kg of water at an initial temperature of 15 °C.</p>"
              "<p>The intensity of the solar radiation incident on the panel is 680 W m<sup>−2</sup>. The panel "
              "transfers 30 % of the incident solar energy to the water in the tank.</p>"
              "<p>Specific heat capacity of water = 4200 J kg<sup>−1</sup> K<sup>−1</sup></p>",
        pre={
            "aii": "<p>The roof is covered with tiles that receive the same solar radiation. The albedo of the tiles is "
                   "0.20 and their emissivity is 0.97. Assume that the tiles are in thermal equilibrium and that they "
                   "lose energy only by radiation from their upper surface.</p>",
            "bi": "<p>The tank is not completely full: the space above the water contains air. A small opening at the "
                  "top of the tank keeps this air at atmospheric pressure, and the level of the water in the tank "
                  "remains constant.</p>",
        }),
}
