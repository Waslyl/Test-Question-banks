"""Textes d'introduction rédigés par W4ss Academy pour les questions B.3 dont l'introduction manque dans la source.

Chaque donnée est tirée du markscheme officiel de la question, pour que la correction reste valable :
    22N.2.SL.TZ0.2   250 kg d'eau, 15 °C -> 30 °C, 680 W m-2, rendement 30 %, albédo 0.20, émissivité 0.97
                     (A = 250 × 4200 × 15 / (0.30 × 680 × 3600) = 21 m2 ; T = (544 / 0.97σ)^1/4 = 315 K = 42 °C)
    23M.2.SL.TZ2.2   graphe pV = 1.50 × (θ + 273) J, donc pV/T = 1.50 J K-1 et intercept à −273 °C ;
                     molécule de 4.7 × 10-26 kg -> masse = (1.50 / 8.31) × 6.02 × 10^23 × 4.7 × 10-26 = 5.1 g
    EXE.2.SL.TZ0.8   p = 1.8 × 10^5 Pa, ρ = 2.0 kg m-3 -> v = √(3p/ρ) = 520 m s-1
    EXE.2.SL.TZ0.10  2.0 mol d'oxygène, 0.36 m3, 260 K -> p = 12 kPa, m = 6.4 × 10-2 kg, v = 450 m s-1
    EXE.2.HL.TZ0.1   fission 235U + n -> 132Te + 100Zr + 4n ; ln A = 25 − 2.5 × 10-6 t (A0 = e^25 = 7.2 × 10^10 s-1,
                     T1/2 = 3.2 jours) ; cycle de Brayton de 1,0 mol d'hélium (B : 8.0 MPa, 1.6 × 10-3 m3 -> 1540 K ;
                     W = 8.23, 9.11, −4.32, −3.25 kJ, Q_AB = 20.58 kJ -> rendement 0.47) ;
                     turbine ω = 310, 277, 240, 196, 139, 0 rad s-1 toutes les 20 s (ω² diminue de 19 × 10^3 s-2)

Chaque entrée donne les options attendues par build_exam.p2_section : intro, pre (texte avant une partie), note.
"""

import math

NOTE = "introduction written by W4ss Academy from the markscheme"


def graph(xr, yr, xstep, ystep, xlabel, ylabel, curves=(), crosses=(), labels=(), arrows=(),
          xlabels=None, ylabels=None, fmt="{:g}", yfmt=None):
    """Graphe sur papier millimétré, dans le style des sujets.

    xr, yr = (min, max) ; xstep, ystep = (pas majeur, pas mineur) ; curves = listes de points (x, y) ;
    crosses = points marqués d'une croix ; labels = (x, y, texte, dx, dy) ;
    arrows = (x, y, x2, y2) : flèche placée en (x, y), orientée vers le point (x2, y2) de la courbe.
    """
    x0, y0, w, h = 78, 18, 480, 330

    def X(x):
        return x0 + (x - xr[0]) * w / (xr[1] - xr[0])

    def Y(y):
        return y0 + h - (y - yr[0]) * h / (yr[1] - yr[0])

    def ticks(lo, hi, step):
        k, out = 0, []
        while lo + k * step <= hi + 1e-9:
            out.append(round(lo + k * step, 6))
            k += 1
        return out

    out = ['<svg class="graph" viewBox="0 0 600 410" xmlns="http://www.w3.org/2000/svg" '
           'font-family="Liberation Sans, Arial" font-size="13">']
    for x in ticks(*xr, xstep[1]):
        major = abs(x / xstep[0] - round(x / xstep[0])) < 1e-6
        out.append(f'<line x1="{X(x):.1f}" y1="{y0}" x2="{X(x):.1f}" y2="{y0 + h}" stroke="{"#888" if major else "#ccc"}" stroke-width="{0.9 if major else 0.5}"/>')
    for y in ticks(*yr, ystep[1]):
        major = abs(y / ystep[0] - round(y / ystep[0])) < 1e-6
        out.append(f'<line x1="{x0}" y1="{Y(y):.1f}" x2="{x0 + w}" y2="{Y(y):.1f}" stroke="{"#888" if major else "#ccc"}" stroke-width="{0.9 if major else 0.5}"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="1.2"/>')
    for x in (xlabels or ticks(*xr, xstep[0])):
        out.append(f'<text x="{X(x):.1f}" y="{y0 + h + 18}" text-anchor="middle">{fmt.format(x)}</text>')
    for y in (ylabels or ticks(*yr, ystep[0])):
        out.append(f'<text x="{x0 - 8}" y="{Y(y) + 4:.1f}" text-anchor="end">{(yfmt or fmt).format(y)}</text>')
    out.append(f'<text x="{x0 + w / 2}" y="{y0 + h + 42}" text-anchor="middle">{xlabel}</text>')
    out.append(f'<text x="20" y="{y0 + h / 2}" text-anchor="middle" transform="rotate(-90 20 {y0 + h / 2})">{ylabel}</text>')
    for pts in curves:
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f} {Y(y):.1f}" for i, (x, y) in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="#111" stroke-width="1.6"/>')
    for x, y in crosses:
        cx, cy = X(x), Y(y)
        out.append(f'<path d="M{cx - 5:.1f} {cy - 5:.1f} L{cx + 5:.1f} {cy + 5:.1f} M{cx - 5:.1f} {cy + 5:.1f} L{cx + 5:.1f} {cy - 5:.1f}" stroke="#111" stroke-width="1.4"/>')
    for x, y, x2, y2 in arrows:
        angle = math.degrees(math.atan2(Y(y2) - Y(y), X(x2) - X(x)))
        out.append(f'<path d="M-7 -5 L3 0 L-7 5 Z" fill="#111" transform="translate({X(x):.1f} {Y(y):.1f}) rotate({angle:.1f})"/>')
    for x, y, text, dx, dy in labels:
        out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3" fill="#111"/>'
                   f'<text x="{X(x) + dx:.1f}" y="{Y(y) + dy:.1f}" font-weight="700" font-size="15">{text}</text>')
    out.append("</svg>")
    return "".join(out)


def pv_theta_graph():
    """23M.2.SL.TZ2.2 : droite pV = 1.50 (θ + 273) J."""
    pv = lambda t: 1.50 * (t + 273)
    return graph((0, 100), (400, 580), (10, 2), (20, 5),
                 '<tspan font-style="italic">θ</tspan> / °C', '<tspan font-style="italic">pV</tspan> / J',
                 curves=[[(0, pv(0)), (100, pv(100))]], crosses=[(t, pv(t)) for t in range(10, 100, 20)],
                 xlabels=list(range(0, 101, 20)), ylabels=list(range(400, 581, 20)))


def ln_activity_graph():
    """EXE.2.HL.TZ0.1 (b) : ln(A / s-1) = 25 − 2.5 × 10-6 t, t en 10^5 s."""
    return graph((0, 10), (22, 25.5), (1, 0.2), (0.5, 0.1),
                 '<tspan font-style="italic">t</tspan> / 10<tspan baseline-shift="super" font-size="10">5</tspan> s',
                 'ln (<tspan font-style="italic">A</tspan> / s<tspan baseline-shift="super" font-size="10">−1</tspan>)',
                 curves=[[(0, 25), (10, 22.5)]], crosses=[(t, 25 - 0.25 * t) for t in (1, 3, 5, 7, 9)],
                 ylabels=[22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5], yfmt="{:.1f}")


# Cycle de Brayton de 1,0 mol d'hélium (γ = 5/3) : AB et CD isobares, BC et DA adiabatiques.
# Donne exactement W = 8.23, 9.11, 4.32, 3.25 kJ, Q_AB = 20.58 kJ, rendement 0.47, T_B = 1540 K.
GAMMA, P_HIGH, P_LOW, V_A, V_B = 5 / 3, 8.0, 1.6, 0.571, 1.6        # p en 10^6 Pa, V en 10^-3 m^3
V_C = V_B * (P_HIGH / P_LOW) ** (1 / GAMMA)
V_D = V_A * (P_HIGH / P_LOW) ** (1 / GAMMA)


def pv_cycle_graph():
    def adiabat(p0, v0, v1, steps=40):
        return [(v, p0 * (v0 / v) ** GAMMA) for v in (v0 + (v1 - v0) * k / steps for k in range(steps + 1))]
    vm = (V_C + V_D) / 2
    bc = lambda v: P_HIGH * (V_B / v) ** GAMMA          # adiabatique BC
    da = lambda v: P_LOW * (V_D / v) ** GAMMA           # adiabatique DA
    return graph((0, 4.5), (0, 9), (0.5, 0.1), (1, 0.2),
                 '<tspan font-style="italic">V</tspan> / 10<tspan baseline-shift="super" font-size="10">−3</tspan> m<tspan baseline-shift="super" font-size="10">3</tspan>',
                 '<tspan font-style="italic">p</tspan> / 10<tspan baseline-shift="super" font-size="10">6</tspan> Pa',
                 curves=[[(V_A, P_HIGH), (V_B, P_HIGH)], adiabat(P_HIGH, V_B, V_C),
                         [(V_C, P_LOW), (V_D, P_LOW)], adiabat(P_LOW, V_D, V_A)],
                 arrows=[((V_A + V_B) / 2, P_HIGH, V_B, P_HIGH), (vm, P_LOW, V_D, P_LOW),
                         (2.4, bc(2.4), 2.45, bc(2.45)), (0.9, da(0.9), 0.88, da(0.88))],
                 labels=[(V_A, P_HIGH, "A", -18, -8), (V_B, P_HIGH, "B", 6, -8),
                         (V_C, P_LOW, "C", 8, -6), (V_D, P_LOW, "D", -6, 20)],
                 xlabels=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5], fmt="{:.1f}", yfmt="{:g}")


def nuclide(a, z, symbol):
    return (f'<math><mmultiscripts><mi mathvariant="normal">{symbol}</mi><none/><none/><mprescripts/>'
            f'<mn>{z}</mn><mn>{a}</mn></mmultiscripts></math>')


def table(head, rows):
    h = "".join(f"<th>{c}</th>" for c in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table class="data-table"><tr>{h}</tr>{r}</table>'


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
    "EXE.2.HL.TZ0.1": dict(
        note=NOTE + " (graphs and tables drawn by W4ss Academy; “λ =” restored in (b)(iii))",
        replace={"biii": [("given by − <em> m </em>", "given by <em>λ</em> = −<em>m</em>")]},
        intro="<p>This question is about a nuclear power station.</p>"
              "<p>In the reactor, uranium-235 nuclei undergo fission. One possible fission reaction is</p>"
              f'<p class="center">{nuclide(235, 92, "U")} + {nuclide(1, 0, "n")} → {nuclide(132, 52, "Te")} + '
              f'{nuclide(100, 40, "Zr")} + 4 {nuclide(1, 0, "n")}</p>',
        pre={
            "bi": "<p>Tellurium-132 is one of the products of this reaction. It is radioactive.</p>",
            "bii": "<p>A sample of tellurium-132 is removed from the reactor. The graph shows the variation with "
                   "time <em>t</em> of ln <em>A</em>, where <em>A</em> is the activity of the sample in s<sup>−1</sup>.</p>"
                   + ln_activity_graph(),
            "ci": "<p>In this power station, the reactor is cooled by a liquid coolant. A heat exchanger transfers "
                  "thermal energy from the coolant to helium gas, which drives a turbine.</p>",
            "cii": "<p>1.0 mol of helium, which can be treated as an ideal monatomic gas, is taken through the cycle "
                   "ABCDA shown. AB and CD are isobaric changes. BC and DA are adiabatic changes.</p>"
                   + pv_cycle_graph(),
            "civ": "<p>The table gives the work done by the gas during each change of the cycle. During AB, "
                   "20.58 kJ of thermal energy is transferred to the gas.</p>"
                   + table(["Change", "Work done by the gas / kJ"],
                           [["A → B", "8.23"], ["B → C", "9.11"], ["C → D", "−4.32"], ["D → A", "−3.25"]]),
            "d": "<p>When the power station is shut down, the turbine slows down. The table shows the angular "
                 "speed <em>ω</em> of the turbine at different times <em>t</em> after the shutdown.</p>"
                 + table(["<em>t</em> / s", "0", "20", "40", "60", "80", "100"],
                         [["<em>ω</em> / rad s<sup>−1</sup>", "310", "277", "240", "196", "139", "0"]]),
        }),
}
