"""Maths AA SL 2.1–2.5 : corrigés rédigés par W4ss Academy et figures redessinées.

L'export (IB_Maths_SL_2_1_to_2_5_questions.json) ne contient aucun markscheme. Les corrigés ci-dessous
suivent les conventions de l'IB (M, A, R, AG, marques entre parenthèses implicites). Ils ont été
vérifiés par calcul : voir les valeurs en tête de chaque question.

Quand l'export ne donne qu'un lien vers une image, la figure est redessinée à partir des données de
l'énoncé (FIGURES, indexées par le texte alt de l'image) : l'image distante n'est jamais téléchargée.
"""
import math

from maths_figures import axes_grid, sample


def p(text, mark=""):
    return f"<p>{text}" + (f"&nbsp;&nbsp;&nbsp;&nbsp;<em><strong>{mark}</strong></em>" if mark else "") + "</p>"


def note(text):
    return f"<p><strong>Note:</strong> {text}</p>"


def method(n):
    return f"<p><strong>METHOD {n}</strong></p>"


def v(name):
    return f"<i>{name}</i>"


x, y, k, f, g, a, c = (v(s) for s in "xykfgac")
FRAC = '<math><mfrac><mrow>{}</mrow><mrow>{}</mrow></mfrac></math>'


# ---------------------------------------------------------------- figures

# 17M.1.SL.TZ1.T_12 : f(x) = ax + b + c/x avec maximum local (−2, −2) et minimum local (2, 6)
# f'(x) = a − c/x² = 0 en x = ±2 ⇒ c = 4a ; b − 4a = −2 et b + 4a = 6 ⇒ a = 1, b = 2, c = 4
def t12(x_):
    return x_ + 2 + 4 / x_


def t12_graph(sx, line=False):
    branches = [sample(t12, -9, -0.25, 800), sample(t12, 0.25, 9, 800)]
    return axes_grid((-9, 9), (-10, 12), sx, sx, 2, 2, 1, 1, curves=branches, hlines=[-6] if line else [], yright=True)


# 17M.2.SL.TZ2.S_6 : grille pour (f ∘ g)(x) = x⁴ − 4x² + 3, 0 ≤ x ≤ 2.25 (valeurs de −1 à 8.38)
def s6(x_):
    return x_ ** 4 - 4 * x_ ** 2 + 3


def s6_grid(sx, sy, curve=False):
    dots = [(0, 3, "(0, 3)", 1.4, -1.2), (1, 0, "1", -2.6, -1.4), (3 ** 0.5, 0, "1.73", 1.2, -1.4),
            (2 ** 0.5, -1, "(1.41, −1)", 1.4, 3.6), (2.25, s6(2.25), "(2.25, 8.38)", -19, 0.5)] if curve else []
    return axes_grid((0, 2.5), (-2, 10), sx, sy, 0.5, 2, 0.1, 0.5,
                     curves=[sample(s6, 0, 2.25)] if curve else [], dots=dots)


# 21N.2.SL.TZ0.2 : f(x) = e^(−x²) − 0.5 ; zéros ±√(ln 2) = ±0.832555 ; f(±2) = −0.481684
def n21(x_):
    return math.exp(-x_ ** 2) - 0.5


N21_SKETCH = axes_grid((-2, 2), (-1, 1), 17, 17, 1, 0.5, 0.1, 0.1, curves=[sample(n21, -2, 2)],
                       dots=[(0, 0.5, "(0, 0.5)", 1.2, -1.4), (-0.8326, 0, "−0.833", -9.5, -1.4),
                             (0.8326, 0, "0.833", 1.2, -1.4), (-2, n21(-2), "(−2, −0.482)", 1, 4),
                             (2, n21(2), "(2, −0.482)", -16, 4)])

FIGURES = {
    "17M.1.SL.TZ1.T_12": {"M17/5/MATSD/SP1/ENG/TZ1/12": t12_graph(5)},
    "17M.2.SL.TZ2.S_6": {"M17/5/MATME/SP2/ENG/TZ2/06.b": s6_grid(40, 8)},
}
REDRAWN = {qid: "figure redrawn by W4ss Academy from the data in the question" for qid in FIGURES}

# ---------------------------------------------------------------- corrigés

SOLUTIONS = {
    # tableau : x = −2, 0, 3, 4 ; f(x) = 8, 4, 0, −3 ; g(x) = −5, −2, 4, 0
    "22M.1.SL.TZ2.1": {
        "a": p(f"{g}(0) = −2", "A1"),
        "b": p(f"attempt to find {f}({g}(0)), e.g. {f}(−2)", "(M1)") + p(f"({f} ∘ {g})(0) = 8", "A1"),
        "c": p(f"recognizing from the table that {f}(3) = 0", "(M1)") + p(f"{x} = 3", "A1"),
    },
    # m(BC) = (12 − 6)/(−14 − 4) = −1/3 ⇒ m(L) = 3 ; L : y = 3x + 26 ; 2 = 3k + 26 ⇒ k = −8
    "22M.1.SL.TZ1.1": {
        "a": p(f"gradient of [BC] = {FRAC.format('<mn>12</mn><mo>−</mo><mn>6</mn>', '<mo>−</mo><mn>14</mn><mo>−</mo><mn>4</mn>')}"
               f" = −{FRAC.format('<mn>1</mn>', '<mn>3</mn>')}", "(A1)")
             + p(f"use of {v('m')}<sub>1</sub>{v('m')}<sub>2</sub> = −1: gradient of {v('L')} = 3", "(M1)")
             + p(f"{y} − 20 = 3({x} + 2)&nbsp; OR &nbsp;{y} = 3{x} + 26", "A1"),
        "b": p(f"substituting ({k}, 2) into their equation: 2 = 3{k} + 26", "(M1)") + p(f"{k} = −8", "A1"),
    },
    # f(x) = x + 2 + 4/x ; f(x) = −6 ⇔ x² + 8x + 4 = 0 ⇔ x = −4 ± √12 (−7.46 et −0.536) : 2 solutions
    "17M.1.SL.TZ1.T_12": {
        "b.i": p(f"horizontal straight line through {y} = −6, drawn across the whole grid", "A1") + t12_graph(3.4, line=True),
        "b.ii": p("2 (solutions)", "A1") + note("the line meets the left branch twice and does not meet the right branch."),
        "c": p(f"−2 &lt; {k} &lt; 6", "A1A1")
             + note(f"A1 for the end values −2 and 6, A1 for the strict inequalities. There is no solution for the "
                    f"values of {k} between the local maximum (−2) and the local minimum (6)."),
    },
    # g(f(x)) = 8(x + 3)/4 + 5 = 2x + 11 ; (g∘f)⁻¹(a) = 4 ⇔ a = (g∘f)(4) = 19
    "SPM.1.SL.TZ0.5": {
        "a": p(f"attempt to substitute {f}({x}) into {g}: 8 × {FRAC.format('<mi>x</mi><mo>+</mo><mn>3</mn>', '<mn>4</mn>')} + 5", "M1")
             + p(f"= 2({x} + 3) + 5", "A1") + p(f"= 2{x} + 11", "AG"),
        "b": method(1) + p(f"{a} = ({g} ∘ {f})(4)", "(M1)") + p("= 2 × 4 + 11", "(A1)") + p(f"{a} = 19", "A1")
             + method(2) + p(f"({g} ∘ {f})<sup>−1</sup>({x}) = {FRAC.format('<mi>x</mi><mo>−</mo><mn>11</mn>', '<mn>2</mn>')}", "(M1)(A1)")
             + p(f"{FRAC.format('<mi>a</mi><mo>−</mo><mn>11</mn>', '<mn>2</mn>')} = 4 ⇒ {a} = 19", "A1"),
    },
    # f(x) = 2x³ + 5 croissante sur [−2, 2] : f(−2) = −11, f(2) = 21
    "17M.1.AHL.TZ2.H_2": {
        "a": p(f"−11 ≤ {f}({x}) ≤ 21", "A1A1") + note("A1 for each correct end value with the correct inequality. Accept [−11, 21]."),
        "b": p(f"{x} = 2{y}<sup>3</sup> + 5 (interchanging {x} and {y})", "M1")
             + p(f"{f}<sup>−1</sup>({x}) = ∛(({x} − 5)/2)&nbsp; OR &nbsp;(({x} − 5)/2)<sup>1/3</sup>", "A1"),
        "c": p(f"domain: −11 ≤ {x} ≤ 21", "A1") + p(f"range: −2 ≤ {f}<sup>−1</sup>({x}) ≤ 2", "A1"),
    },
    "21N.2.SL.TZ0.2": {
        "a": p(f"{x} = −0.833, {x} = 0.833&nbsp; (±0.832554…, i.e. ±√ln 2)", "A1A1"),
        "b": N21_SKETCH
             + p(f"correct shape: symmetrical about the {y}-axis, with a single maximum on the {y}-axis", "A1")
             + p(f"maximum at (0, 0.5) and {x}-intercepts at about ±0.833", "A1")
             + p("end points at about (−2, −0.482) and (2, −0.482)", "A1"),
    },
    # zéro : x = −∛12 = −2.28943 ; minimum local : (∛24, 3∛3) = (2.88450, 4.32675) ;
    # f(x) = 3 − x ⇔ 2x³ − 3x² + 12 = 0 : une seule racine réelle, x = −1.43081
    "20N.1.SL.TZ0.T_4": {
        "a.i": p(f"{x} + {FRAC.format('<mn>12</mn>', '<msup><mi>x</mi><mn>2</mn></msup>')} = 0, or the {x}-intercept of the graph on the GDC", "(M1)")
               + p(f"{x} = −2.29&nbsp; (−2.28942…)", "A1") + note("Accept (−2.29, 0)."),
        "a.ii": p("(2.88, 4.33)&nbsp; ((2.88449…, 4.32674…))", "A1A1")
                + note("A1 for each coordinate. Exact values: (2∛3, 3∛3)."),
        "b": p(f"{x} + {FRAC.format('<mn>12</mn>', '<msup><mi>x</mi><mn>2</mn></msup>')} = 3 − {x}, or the graphs of {f} and {g} on the GDC", "(M1)")
             + p(f"{x} = −1.43&nbsp; (−1.43080…)", "A1"),
    },
    # f(x) = 6(x − 1)² − 5 ; (g∘f)(x) = −f(x) + c ≤ 0 pour tout x ⇔ c ≤ min f = −5
    "21M.2.SL.TZ2.5": {
        "a": p(f"minimum value of {f} is −5 (at {x} = 1), e.g. {f}({x}) = 6({x} − 1)<sup>2</sup> − 5 or from the GDC", "(A1)")
             + p(f"{f}({x}) ≥ −5", "A1"),
        "b": p(f"({g} ∘ {f})({x}) = −(6{x}<sup>2</sup> − 12{x} + 1) + {c} = −6{x}<sup>2</sup> + 12{x} − 1 + {c}", "(A1)")
             + p(f"recognizing that the maximum of {g} ∘ {f} is at {x} = 1 (or that {c} ≤ {f}({x}) for every {x})", "(M1)")
             + p(f"maximum value of ({g} ∘ {f})({x}) = 5 + {c}", "(A1)")
             + p(f"5 + {c} ≤ 0 ⇒ {c} ≤ −5", "A1"),
    },
    # (f∘g)(x) = (x² − 2)² − 1 ; minimum −1 en x = √2 ; (f∘g)(0) = 3 ; (f∘g)(2.25) = 8.37891
    # deux solutions exactement ⇔ −1 < k ≤ 3 (k = 3 : x = 0 et x = 2)
    "17M.2.SL.TZ2.S_6": {
        "a": p(f"({f} ∘ {g})({x}) = {f}({x}<sup>2</sup> − 2) = ({x}<sup>2</sup> − 2)<sup>2</sup> − 1", "A1")
             + p(f"= {x}<sup>4</sup> − 4{x}<sup>2</sup> + 4 − 1", "A1") + p(f"= {x}<sup>4</sup> − 4{x}<sup>2</sup> + 3", "AG"),
        "b": s6_grid(26, 5.2, curve=True)
             + p("correct shape: decreasing to a single minimum, then increasing", "A1")
             + p(f"{y}-intercept (0, 3), {x}-intercepts at 1 and about 1.73, minimum at about (1.41, −1)", "A1")
             + p(f"curve stops at {x} = 2.25, at about (2.25, 8.38)", "A1"),
        "c": p(f"recognizing the minimum value −1 and ({f} ∘ {g})(0) = 3, e.g. horizontal lines on the graph", "(M1)")
             + p(f"−1 &lt; {k} ≤ 3", "A1A1")
             + note(f"A1 for −1 &lt; {k}, A1 for {k} ≤ 3. For {k} = 3 the two solutions are {x} = 0 and {x} = 2."),
    },
}
