#!/usr/bin/env python3
"""Test de la classe « Solving first order differential equations » (Maths AA HL) -> data/maths-de.js.

Usage :
    python3 scripts/build_de_test.py QuestionBank_Test.pdf
    python3 scripts/build_maths_exam.py de-mock de-practice

Le PDF (export de la Questionbank, 12 questions et leurs markschemes) perd des parenthèses dans les
formules (ex. « y = x tan ln x − 1 » pour y = x(tan(ln x) − 1)). Les énoncés sont donc récrits ici en
LaTeX (latex_mathml.py), en gardant seulement les parties où l'on résout une équation différentielle
(méthode d'Euler, variables séparables, substitution y = vx, facteur intégrant). Les markschemes sont
des extraits des pages du PDF : chaque extrait va du libellé de la partie au libellé suivant, et le
libellé d'origine est masqué (les parties sont renumérotées).
"""
import base64
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_mathml import texte_math as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPI = 170
TOP, BOTTOM, LEFT, RIGHT = 32, 765, 50, 564   # zone utile d'une page, en points
MS_FIRST_PAGE = 8

D = r"\frac{\mathrm{d}y}{\mathrm{d}x}"

# (référence, session, date, fuseau, ancien programme, [(contexte avant la partie, libellé PDF, libellé, points, énoncé)])
QUESTIONS = [
    ("19N.3.AHL.TZ0.HCA_4", "19N", "November 2019", "TZ0", "HCA_", [
        (rf"Consider the differential equation ${D}=\frac{{4x^{{2}}+y^{{2}}-xy}}{{x^{{2}}}}$, with $y=2$ when $x=1$.",
         "a.", "a", 5, r"Use Euler’s method, with step length $h=0.1$, to find an approximate value of $y$ when $x=1.4$."),
        ("", "c.i.", "b.i", 1, r"Express $m^{2}-2m+4$ in the form $(m-a)^{2}+b$, where $a, b \in \mathbb{Z}$."),
        ("", "c.ii.", "b.ii", 10, r"Solve the differential equation, for $x>0$, giving your answer in the form $y=f(x)$."),
    ]),
    ("21M.2.AHL.TZ1.12", "21M", "May 2021", "TZ1", "", [
        (r"The function $f$ has a derivative given by $f'(x)=\frac{1}{x(k-x)}$, $x \in \mathbb{R}$, $x \ne 0$, "
         r"$x \ne k$, where $k$ is a positive constant.",
         "a.", "a", 3, r"The expression for $f'(x)$ can be written in the form $\frac{a}{x}+\frac{b}{k-x}$, where "
                       r"$a, b \in \mathbb{R}$. Find $a$ and $b$ in terms of $k$."),
        ("", "b.", "b", 3, r"Hence, find an expression for $f(x)$."),
        (r"Consider $P$, the population of a colony of ants, which has an initial value of $1200$.</p><p>The rate of "
         rf"change of the population can be modelled by the differential equation "
         r"$\frac{\mathrm{d}P}{\mathrm{d}t}=\frac{P(k-P)}{5k}$, where $t$ is the time measured in days, $t \ge 0$, "
         r"and $k$ is the upper bound for the population.",
         "c.", "c", 8, r"By solving the differential equation, show that "
                       r"$P=\frac{1200k}{(k-1200)e^{-\frac{t}{5}}+1200}$."),
    ]),
    ("EXN.2.AHL.TZ0.12", "EXN", "November Example questions", "TZ0", "", [
        (rf"Consider the differential equation $${D}=f\left(\frac{{y}}{{x}}\right), \quad x>0.$$"
         rf"The curve $y=f(x)$ for $x>0$ has a gradient function given by "
         rf"$${D}=\frac{{y^{{2}}+3xy+2x^{{2}}}}{{x^{{2}}}}.$$The curve passes through the point $(1, -1)$.",
         "a.", "a", 3, r"Use the substitution $y=vx$ to show that $\int \frac{\mathrm{d}v}{f(v)-v}=\ln x+C$, "
                       r"where $C$ is an arbitrary constant."),
        ("", "b.", "b", 9, r"By using the result from part (a) or otherwise, solve the differential equation and hence "
                           r"show that the curve has equation $y=x\left(\tan(\ln x)-1\right)$."),
    ]),
    ("17N.3.AHL.TZ0.HCA_2", "17N", "November 2017", "TZ0", "HCA_", [
        (rf"Consider the differential equation ${D}+\frac{{x}}{{x^{{2}}+1}}y=x$, where $y=1$ when $x=0$.",
         "a.", "a", 4, r"Show that $\sqrt{x^{2}+1}$ is an integrating factor for this differential equation."),
        ("", "b.", "b", 6, r"Solve the differential equation giving your answer in the form $y=f(x)$."),
    ]),
    ("18M.3.AHL.TZ0.HCA_5", "18M", "May 2018", "TZ0", "HCA_", [
        (rf"Consider the differential equation $x{D}-y=x^{{p}}+1$, where $x \in \mathbb{{R}}$, $x \ne 0$ and $p$ "
         r"is a positive integer, $p>1$.",
         "a.", "", 8, r"Solve the differential equation given that $y=-1$ when $x=1$. Give your answer in the form "
                      r"$y=f(x)$."),
    ]),
    ("18N.3.AHL.TZ0.HCA_4", "18N", "November 2018", "TZ0", "HCA_", [
        (rf"Consider the differential equation ${D}=1+\frac{{y}}{{x}}$, where $x \ne 0$.",
         "a.", "a", 4, r"Given that $y(1)=1$, use Euler’s method with step length $h=0.25$ to find an approximation "
                       r"for $y(2)$. Give your answer to two significant figures."),
        ("", "b.", "b", 6, rf"Solve the equation ${D}=1+\frac{{y}}{{x}}$ for $y(1)=1$."),
    ]),
    ("17M.3.AHL.TZ0.HCA_4", "17M", "May 2017", "TZ0", "HCA_", [
        (rf"Consider the differential equation $${D}=f\left(\frac{{y}}{{x}}\right), \quad x>0.$$",
         "a.", "a", 3, r"Use the substitution $y=vx$ to show that the general solution of this differential equation "
                       r"is $$\int \frac{\mathrm{d}v}{f(v)-v}=\ln x+\text{constant}.$$"),
        ("", "b.", "b", 10, rf"Hence, or otherwise, solve the differential equation "
                            rf"${D}=\frac{{x^{{2}}+3xy+y^{{2}}}}{{x^{{2}}}}$, $x>0$, given that $y=1$ when $x=1$. "
                            r"Give your answer in the form $y=g(x)$."),
    ]),
    ("16N.3.AHL.TZ0.HCA_1", "16N", "November 2016", "TZ0", "HCA_", [
        (rf"Consider the differential equation ${D}+\left(\frac{{2x}}{{1+x^{{2}}}}\right)y=x^{{2}}$, given that "
         r"$y=2$ when $x=0$.",
         "a.", "a", 5, r"Show that $1+x^{2}$ is an integrating factor for this differential equation."),
        ("", "b.", "b", 6, r"Hence solve this differential equation. Give the answer in the form $y=f(x)$."),
    ]),
    ("19M.3.AHL.TZ0.HCA_5", "19M", "May 2019", "TZ0", "HCA_", [
        (rf"Consider the differential equation $2xy{D}=y^{{2}}-x^{{2}}$, where $x>0$.",
         "a.", "", 11, r"Solve the differential equation and show that a general solution is $x^{2}+y^{2}=cx$ where "
                       r"$c$ is a positive constant."),
    ]),
    ("20N.3.AHL.TZ0.HCA_3", "20N", "November 2020", "TZ0", "HCA_", [
        (rf"The curve $y=f(x)$ has a gradient function given by $${D}=x-y.$$The curve passes through the point $(1, 1)$.",
         "b.", "", 8, rf"Find the solution of the differential equation ${D}=x-y$ which passes through the point "
                      r"$(1, 1)$. Give your answer in the form $y=f(x)$."),
    ]),
    ("20N.2.AHL.TZ0.F_9", "20N", "November 2020", "TZ0", "F_", [
        (rf"Consider the differential equation ${D}=\frac{{y-x}}{{y+x}}$, where $x, y>0$.</p><p>It is given that "
         r"$y=2$ when $x=1$.",
         "a.", "", 9, r"Solve the differential equation, giving your answer in the form $f(x, y)=0$."),
    ]),
    ("22M.2.AHL.TZ1.12", "22M", "May 2022", "TZ1", "", [
        (rf"Consider the differential equation $x^{{2}}{D}=y^{{2}}-2x^{{2}}$ for $x>0$ and $y>2x$. It is given that "
         r"$y=3$ when $x=1$.",
         "a.", "a", 4, r"Use Euler’s method, with a step length of $0.1$, to find an approximate value of $y$ when "
                       r"$x=1.5$."),
        ("", "b.", "b", 3, r"Use the substitution $y=vx$ to show that $x\frac{\mathrm{d}v}{\mathrm{d}x}=v^{2}-v-2$."),
        ("", "c.i.", "c", 10, r"By solving the differential equation, show that $y=\frac{8x+x^{4}}{4-x^{3}}$."),
    ]),
]


def markers(pdf):
    """En-têtes de question et libellés de partie des pages de markscheme : [(page, y0, y1, x1, texte)]."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "bbox.html")
        subprocess.run(["pdftotext", "-bbox-layout", pdf, out], check=True)
        s = open(out, encoding="utf-8").read()
    found = []
    for n, page in enumerate(re.split(r"<page ", s)[1:], 1):
        if n < MS_FIRST_PAGE:
            continue
        for line in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)">(.*?)</line>',
                                page, re.S):
            words = re.findall(r'<word xMin="[\d.]+" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)</word>',
                               line.group(4))
            if not words:
                continue
            first = html.unescape(words[0][1])
            x0, y0, y1 = float(line.group(1)), float(line.group(2)), float(line.group(3))
            if re.match(r"^(\d\d[MN]|EXN|SPM)\.\d\.", first):
                found.append((n, y0, y1, 0, "#" + first))
            elif x0 < 80 and re.fullmatch(r"[a-e]\.(i{1,3}v?\.)?", first):
                found.append((n, y0, y1, float(words[0][0]), first))
    return found


def crops(pdf, pages, segments):
    """Images (JPEG en base64) des extraits de markscheme."""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", "-f", str(min(pages)), "-l", str(max(pages)),
                        pdf, os.path.join(tmp, "p")], check=True)
        files = {int(re.search(r"(\d+)\.png$", f).group(1)): os.path.join(tmp, f)
                 for f in os.listdir(tmp) if f.endswith(".png")}
        k = DPI / 72
        for key, pieces in segments.items():
            parts = []
            for i, (page, y0, y1, mask) in enumerate(pieces):
                part = os.path.join(tmp, f"{abs(hash(key))}_{i}.png")
                cmd = ["convert", files[page]]
                if mask:      # masque le libellé d'origine (« c.i. ») : les parties sont renumérotées
                    mx1, my0, my1 = mask
                    cmd += ["-fill", "white", "-draw",
                            f"rectangle {int((LEFT + 4) * k)},{int((my0 - 1) * k)} {int((mx1 + 2) * k)},{int((my1 + 1) * k)}"]
                cmd += ["-crop", f"{int((RIGHT - LEFT) * k)}x{int((y1 - y0) * k)}+{int(LEFT * k)}+{int(y0 * k)}",
                        "+repage", part]
                subprocess.run(cmd, check=True)
                parts.append(part)
            # une image par morceau de page, pour que le markscheme puisse passer d'une page à l'autre ; sans le
            # blanc inutile en haut et en bas (la largeur reste celle de la page, donc la même échelle)
            out[key] = []
            for j, part in enumerate(parts):
                mean = subprocess.run(["convert", part, "-format", "%[fx:mean]", "info:"], check=True,
                                      capture_output=True, text=True).stdout
                if float(mean) > 0.997:      # morceau vide (libellé masqué seul en bas de page)
                    continue
                final = part[:-4] + ".jpg"
                subprocess.run(["convert", part, "-bordercolor", "white", "-border", "0x2", "-trim", "+repage",
                                "-background", "white", "-gravity", "northwest",
                                "-extent", f"{int((RIGHT - LEFT) * k)}x", "-quality", "82", final], check=True)
                out[key].append(base64.b64encode(open(final, "rb").read()).decode())
    return out


def main(pdf):
    marks = markers(pdf)
    wanted = {(q[0], p[1]) for q in QUESTIONS for p in q[5]}
    segments, qid = {}, None
    for i, (page, y0, y1, x1, text) in enumerate(marks):
        if text.startswith("#"):
            qid = text[1:]
            continue
        if (qid, text) not in wanted:
            continue
        npage, ny0 = (marks[i + 1][0], marks[i + 1][1]) if i + 1 < len(marks) else (page, BOTTOM)
        pieces, p, start, mask = [], page, y0 - 3, (x1, y0, y1)
        while p < npage:
            pieces.append((p, start, BOTTOM, mask))
            p, start, mask = p + 1, TOP, None
        if ny0 - 3 > start + 5:
            pieces.append((p, start, ny0 - 3, mask))
        segments[(qid, text)] = pieces
    missing = wanted - set(segments)
    assert not missing, f"libellés non trouvés dans le markscheme : {missing}"
    images = crops(pdf, {p for pieces in segments.values() for p, *_ in pieces}, segments)

    exercises = []
    for qid, session, date, tz, legacy, parts in QUESTIONS:
        contexts, out = [], []
        for i, (ctx, pdf_label, label, mk, q) in enumerate(parts):
            if ctx:
                contexts.append(OrderedDict(id=f"c{i}", html=f"<p>{T(ctx)}</p>"))
            img = images[(qid, pdf_label)]
            out.append(OrderedDict(label=label, type="question", marks=mk, ctx=[c["id"] for c in contexts],
                                   q=f"<p>{T(q)}</p>", er="",
                                   ms="".join(f'<img class="ms-crop" src="data:image/jpeg;base64,{i}" alt="Markscheme">'
                                              for i in img)))
        exercises.append(OrderedDict(id=qid, section="A", paper=2, session=session, date=date, tz=tz, legacy=legacy,
                                     marks=sum(p["marks"] for p in out), contexts=contexts, parts=out, notes=[]))
    data = OrderedDict(subject="DP Mathematics: Analysis and Approaches", level="HL",
                       topic=OrderedDict(number=5, title="First order differential equations"), exercises=exercises)
    target = os.path.join(ROOT, "data", "maths-de.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("window.QB_MATHS_DE = ")
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"data/maths-de.js : {len(exercises)} questions, {sum(e['marks'] for e in exercises)} points, "
          f"{os.path.getsize(target) / 1e6:.1f} Mo")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
