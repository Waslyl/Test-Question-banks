#!/usr/bin/env python3
"""Sujets d'entraînement W4ss Academy de Maths AA SL : Paper 1 et Paper 2 de 30 minutes sur 4.1 à 4.6.

Usage :
    python3 scripts/build_maths_exam.py            # tous les sujets (ou ajouter le nom : p1, p2, p1-2, p2-2)
    node scripts/print_pdf.cjs exams/w4ss-maa-t4-p1.html exams/W4ss_Academy_Maths_AA_T4_Paper1.pdf
    node scripts/print_pdf.cjs exams/w4ss-maa-t4-p1-markscheme.html exams/W4ss_Academy_Maths_AA_T4_Paper1_Markscheme.pdf

Les questions viennent de data/maths-t4.js (produit par build_maths.py). La mise en page reprend
celle des sujets de mathématiques du DP : section A avec cadres de réponse, section B sans cadre
(réponses sur les pages lignées à la fin du sujet). Le gabarit (couverture, pagination) est celui
de build_exam.py.

Le fichier source ne donne pas le sous-thème des questions : il est indiqué à la main dans PAPERS.
Les parties hors de 4.1 à 4.6 sont écartées (ex. droite de régression de x en y, 4.10).
Les sujets du jeu 2 n'ont pas de section B : seulement des questions courtes avec cadres de réponse.
"""
import base64
import html as htmlmod
import math
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_exam import (BRAND, CSS, OUT, PAGINATE, ROOT, SITE, clean, cover, load_js,  # noqa: E402
                        sources_page)

TITLE = "4.1–4.6 Statistics and probability"

# (référence, parties retenues ou None pour toutes, sous-thèmes). Aucune question ne sert dans deux sujets.
# Les sujets du jeu 2 n'ont pas de section B.
PAPERS = {
    "p1": dict(
        paper=1, set=1, code="W4SS–MAA–T4–P1–01", html="w4ss-maa-t4-p1", minutes=30,
        A=[("19N.1.SL.TZ0.S_2", None, "4.6 Venn diagrams"),
           ("21N.1.SL.TZ0.4", None, "4.5, 4.6 tree diagrams, independent events")],
        B=[("21M.1.SL.TZ2.7", None, "4.2 cumulative frequency, percentiles · 4.3 median · 4.1 sampling")],
    ),
    "p2": dict(
        paper=2, set=1, code="W4SS–MAA–T4–P2–01", html="w4ss-maa-t4-p2", minutes=30,
        A=[("EXN.2.SL.TZ0.1", None, "4.3 mean"),
           ("22M.2.SL.TZ1.2", None, "4.3 median and standard deviation of a frequency table"),
           ("21M.2.SL.TZ2.4", None, "4.6 combined events, conditional probability, independence")],
        B=[("EXM.2.SL.TZ0.1", ["a", "b.i", "b.ii", "c", "d.i", "d.ii", "d.iii"],
            "4.1 stratified and systematic sampling · 4.4 correlation coefficient r "
            "— part (e), regression line of t on s (4.10), left out")],
    ),
    "p1-2": dict(
        paper=1, set=2, code="W4SS–MAA–T4–P1–02", html="w4ss-maa-t4-p1-2", minutes=30,
        A=[("19M.1.SL.TZ1.S_1", None, "4.6 Venn diagram, combined events"),
           ("21M.1.SL.TZ1.4", None, "4.2 box and whisker diagram, outliers"),
           ("22N.1.SL.TZ0.6", None, "4.6 independent events, combined events"),
           ("EXM.1.SL.TZ0.2", None, "4.2, 4.3 quartiles, interquartile range, outliers")],
        B=[],
    ),
    "p2-2": dict(
        paper=2, set=2, code="W4SS–MAA–T4–P2–02", html="w4ss-maa-t4-p2-2", minutes=30,
        A=[("19M.2.SL.TZ1.S_1", None, "4.3 mean · 4.2 box-and-whisker plot, interquartile range"),
           ("22M.2.SL.TZ2.5", None, "4.2, 4.3 box and whisker diagrams, outliers, skewness"),
           ("22N.2.SL.TZ0.1", None, "4.4 regression line of y on x, correlation coefficient r"),
           ("22M.2.SL.TZ1.6", ["a"], "4.6 independent events — part (b), P(A′ | B′) with the formal "
                                     "definition of independence (4.11), left out"),
           ("22M.2.SL.TZ2.4", None, "4.6 independent events, combined events")],
        B=[],
    ),
}

SUBJECT = "Mathematics: analysis and approaches"
ADVICE = {
    1: "Full marks are not necessarily awarded for a correct answer with no working. Answers must be supported "
       "by working and/or explanations. Where an answer is incorrect, some marks may be given for a correct "
       "method, provided this is shown by written working. You are therefore advised to show all working.",
    2: "Full marks are not necessarily awarded for a correct answer with no working. Answers must be supported "
       "by working and/or explanations. Solutions found from a graphic display calculator should be supported "
       "by suitable working. For example, if graphs are used to find a solution, you should sketch these as part "
       "of your answer. Where an answer is incorrect, some marks may be given for a correct method, provided this "
       "is shown by written working. You are therefore advised to show all working.",
}
LINES_PER_PAGE = 31
LINE = '<div class="dots"></div>'

MATHS_CSS = """
.maxmark { font-weight: 700; margin: 0 0 3mm; }
.advice { margin: 0 0 7mm; }
.sec-title { font-weight: 700; font-size: 11.5pt; text-align: center; margin: 0 0 4mm; }
.qbody .stem p, .part-context p { margin: 0 0 3mm; }
.part-context img, .qbody img { max-width: 100%; height: auto; display: block; margin: 2mm auto 3mm; }
.qn + .part, .part-context + .part { margin-top: 2mm; }
.blk[data-kind="p2"], .blk[data-kind="secb"] { padding-bottom: 3mm; }
/* cadre de réponse de la section A : une ligne par bloc, pour qu'il puisse continuer sur la page suivante */
.blk.bl { padding: 0; }
.blk.bl.last { padding-bottom: 9mm; }
.bl .bx { border-left: 1px solid #222; border-right: 1px solid #222; padding: 0 9mm; }
.bl .bx .dots { height: 7.4mm; border-bottom: 1.4px dotted #444; }
.bl.first .bx { border-top: 1px solid #222; padding-top: 3mm; }
.bl.last .bx { border-bottom: 1px solid #222; padding-bottom: 4mm; }
/* ombres internes : ne changent ni la hauteur ni le débordement de la page */
.bl.top .bx { box-shadow: inset 0 1px 0 #222; }
.bl.bottom .bx { box-shadow: inset 0 -1.4px 0 #222; }
.bl.top.bottom .bx { box-shadow: inset 0 1px 0 #222, inset 0 -1.4px 0 #222; }
.part { margin: 2mm 0; }
.page .ftr .dnw { position: absolute; left: 0; right: 0; top: 6.5mm; text-align: center; }
.lined h2 { font-size: 11pt; margin: 0 0 4mm; }
.lined .answer-box { border: 0; padding: 0; }
.ms-item h2.next { margin-top: 8mm; }
.ms-item .ms-html img { max-width: 80mm; height: auto; display: block; margin: 1mm 0; }
"""

# pages de la section B : « Do not write solutions on this page. », comme dans les sujets
MATHS_JS = """
<script>
Array.prototype.forEach.call(document.querySelectorAll(".page.secb .ftr"), function (f) {
  f.insertAdjacentHTML("beforeend", '<span class="dnw">Do not write solutions on this page.</span>');
});
// cadre coupé par un changement de page : on le ferme en bas de page et on le rouvre en haut de la suivante
Array.prototype.forEach.call(document.querySelectorAll(".page .body .bl"), function (k) {
  var prev = k.previousElementSibling, next = k.nextElementSibling;
  if (!k.classList.contains("first") && !(prev && prev.classList.contains("bl"))) k.classList.add("top");
  if (!k.classList.contains("last") && !(next && next.classList.contains("bl"))) k.classList.add("bottom");
});
// formule trop large pour sa colonne : on réduit sa taille (elle ne peut pas passer à la ligne)
Array.prototype.forEach.call(document.querySelectorAll(".page math"), function (m) {
  var box = m.parentElement.closest("td, .part-text, .stem, .part-context");
  if (!box) return;
  var right = box.getBoundingClientRect().right - parseFloat(getComputedStyle(box).paddingRight);
  for (var size = 95; m.getBoundingClientRect().right > right + 0.5 && size >= 60; size -= 5) m.style.fontSize = size + "%";
});
</script>
"""


def shell(ctx, title, inner):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{htmlmod.escape(title)}</title><style>{CSS}{MATHS_CSS}</style></head>
<body data-code="{ctx['code']}"><div id="pages"></div><div id="flow">{inner}</div>{PAGINATE}{MATHS_JS}</body></html>"""


def split_label(label):
    """'b.ii' -> ('b', 'ii'), 'a' -> ('a', ''), '' -> ('', '')"""
    letter, _, roman = label.partition(".")
    return letter, roman


def display_label(label):
    letter, roman = split_label(label)
    return (f"({letter})" if letter else "") + (f"({roman})" if roman else "")


def ms_clean(h):
    h = re.sub(r"<p[^>]*>\s*\* This (?:sample question|question is from an exam for a previous syllabus).*?</p>",
               "", h, flags=re.S)
    h = clean(h)
    # « [2 marks] » en fin de partie : déjà dans la colonne des points
    def only_marks(m):
        text = htmlmod.unescape(re.sub(r"<[^>]+>", "", m.group(0)))
        return "" if re.fullmatch(r"\s*\[\s*\d+\s*marks?\s*\]\s*", text) else m.group(0)
    h = re.sub(r"<p>.*?</p>", only_marks, h, flags=re.S)
    return h.strip()


def scale_images(h, factor):
    """Fixe la largeur des images (PNG) à factor × leur taille naturelle (1 px = 0.2646 mm)."""
    def repl(m):
        head = base64.b64decode(m.group(2)[:32])
        width = int.from_bytes(head[16:20], "big") if head[1:4] == b"PNG" else 0
        return f'<img style="width:{width * 0.2646 * factor:.1f}mm" ' if width else m.group(0)
    return re.sub(r'<img (?=src="data:image/(\w+);base64,([^"]{32}))', repl, h)


def question(n, e, labels, kind):
    """Blocs HTML d'une question, lignes du markscheme et total des points.

    Section A (kind « p2 ») : images à 80 % pour garder la question et son cadre ensemble.
    """
    ctx_html = {c["id"]: scale_images(clean(c["html"]), 0.8 if kind == "p2" else 1) for c in e["contexts"]}
    parts = [p for p in e["parts"] if labels is None or p["label"] in labels]
    missing = set(labels or []) - {p["label"] for p in parts}
    assert not missing, f"{e['id']} : parties absentes {missing}"
    total = sum(p["marks"] for p in parts)
    blocks, ms, shown, prev_letter = [], [], set(), None
    single = len(parts) == 1   # une seule partie : pas de libellé (a)
    for i, p in enumerate(parts):
        new_ctx = "".join(ctx_html[c] for c in p["ctx"] if c not in shown and c in ctx_html)
        shown.update(p["ctx"])
        body = re.sub(r"</math>\s+([.,])", r"</math>\1", clean(p["q"]))   # « 14.5 . » -> « 14.5. »
        head = ""
        if i == 0:
            stem = new_ctx + (body if single else "")
            head = (f'<div class="qn"><span class="num">{n}.</span><div class="qbody">'
                    f'<p class="maxmark">[Maximum mark: {total}]</p><div class="stem">{stem}</div></div></div>')
            new_ctx = ""
        context = f'<div class="part-context">{new_ctx}</div>' if new_ctx else ""
        if single:
            blocks.append(f'<div class="blk" data-kind="{kind}" data-q="{n}">{head}</div>')
            ms.append((n, "", p["marks"], ms_clean(p["ms"])))
            continue
        letter, roman = split_label(p["label"])
        if roman and letter == prev_letter:
            label = f'<span class="pl"></span><span class="pr">({roman})</span>'
        elif roman:
            label = f'<span class="pl">({letter})</span><span class="pr">({roman})</span>'
        else:
            label = f'<span class="pl">({letter})</span>'
        prev_letter = letter
        marks = f'<div class="part-marks">[{p["marks"]}]</div>' if p["marks"] else ""
        blocks.append(
            f'<div class="blk" data-kind="{kind}" data-q="{n}">{head}{context}'
            f'<div class="part{" sub" if roman else ""}"><div class="part-label">{label}</div>'
            f'<div class="part-text">{body}</div>{marks}</div></div>')
        if p["marks"]:
            ms.append((n, display_label(p["label"]), p["marks"], ms_clean(p["ms"])))
    if kind == "p2":   # section A : un cadre de réponse après la question (2 lignes par point)
        # des groupes de lignes : au moins 3 lignes en bas de page et 2 en haut de la suivante
        lines = 2 * total
        groups = [3] + [1] * (lines - 5) + [2] if lines >= 5 else [lines]
        for j, count in enumerate(groups):
            cls = "blk bl" + (" first" if j == 0 else "") + (" last" if j == len(groups) - 1 else "")
            blocks.append(f'<div class="{cls}" data-kind="{kind}" data-q="{n}"><div class="bx">{LINE * count}</div></div>')
    return blocks, ms, total


def answer_pages(n, marks):
    """Pages lignées pour une question de la section B."""
    count = max(1, math.ceil(marks / 7))
    pages = []
    for k in range(count):
        title = f"Section B — answers to question {n}" + (" (continued)" if k else "")
        pages.append(
            '<section class="page p2 lined"><div class="hdr"><span class="pn"></span><span class="code"></span></div>'
            f'<div class="body"><h2>{title}</h2><div class="answer-box">{LINE * LINES_PER_PAGE}</div></div>'
            '<div class="ftr"><span class="note"></span><span class="turn"></span></div>'
            '<span class="corner c1"></span><span class="corner c2"></span><span class="corner c3"></span>'
            '<span class="corner c4"></span><span class="stripe"></span></section>')
    return pages


def build(name, by_id):
    paper = PAPERS[name]
    num = paper["paper"]
    sec_blocks, ms_rows, sources, lined = {"A": [], "B": []}, {"A": [], "B": []}, [], []
    total = 0
    n = 0
    for section in ("A", "B"):
        kind = "p2" if section == "A" else "secb"
        for qid, labels, topics in paper[section]:
            n += 1
            e = by_id[qid]
            assert e["paper"] == num, f"{qid} n'est pas une question de Paper {num}"
            blocks, ms, marks = question(n, e, labels, kind)
            sec_blocks[section] += blocks
            ms_rows[section] += ms
            total += marks
            if section == "B":
                lined += answer_pages(n, marks)
            old = " (former Mathematics SL course)" if e["legacy"] else ""
            part_note = ("" if labels is None else f", part {display_label(labels[0])}" if len(labels) == 1
                         else f", parts {display_label(labels[0])} to {display_label(labels[-1])}")
            sources.append((f"Section {section} — question {n}", f"{qid}{old}{part_note} · {topics}"))

    a, b = sec_blocks["A"], sec_blocks["B"]
    a[0] = a[0].replace('data-kind="p2"', 'data-kind="p2" data-newpage', 1).replace(
        '<div class="qn">',
        f'<p class="advice">{ADVICE[num]}</p><div class="sec-title">Section A</div>'
        '<p class="lead">Answer <strong>all</strong> questions. Answers must be written within the answer boxes '
        'provided. Working may be continued below the lines, if necessary.</p><div class="qn">', 1)
    if b:
        b[0] = b[0].replace('data-kind="secb"', 'data-kind="secb" data-newpage', 1).replace(
            '<div class="qn">',
            '<div class="sec-title">Section B</div><p class="lead">Answer <strong>all</strong> questions on the '
            'answer pages at the end of this paper. Please start each question on a new page.</p><div class="qn">', 1)

    today = date.today()
    ctx = dict(code=paper["code"], number=paper["set"], series="practice set", title=TITLE, site=SITE, level="Standard level",
               subject=SUBJECT, brand=BRAND.replace("DP Physics · 2025 syllabus", "DP Mathematics AA · SL"),
               date=f"{today.day} {today.strftime('%B %Y')}", year=today.year)
    calculator = ("You are <b>not</b> permitted access to any calculator for this paper." if num == 1
                  else "A graphic display calculator is required for this paper.")
    instructions = [
        "Write your name in the boxes above.",
        "Do not open this examination paper until instructed to do so.",
        calculator,
        *(["Section A: answer all questions. Answers must be written within the answer boxes provided.",
           "Section B: answer all questions on the answer pages at the end of this paper."] if b else
          ["This paper has a Section A only. Answer all questions. Answers must be written within the answer "
           "boxes provided."]),
        "Unless otherwise stated in the question, all numerical answers should be given exactly or correct to "
        "three significant figures.",
        "A clean copy of the <b>mathematics: analysis and approaches formula booklet</b> is required for this paper.",
        f"The maximum mark for this examination paper is <b>[{total} marks]</b>.",
    ]
    intro = ("This practice paper was put together by W4ss Academy for internal class use. The questions are taken "
             "from the IB DP Mathematics: analysis and approaches Questionbank (standard level, topic 4 Statistics "
             "and probability) and cover subtopics 4.1 to 4.6. They remain the property of the International "
             "Baccalaureate Organization and must not be published or sold.")
    test = (cover(ctx, f"Paper {num}", instructions, f"{paper['minutes']} minutes") + "".join(a) + "".join(b)
            + "".join(lined) + sources_page(sources, intro=intro))

    def table(head, row, first, newpage=False):
        h = f"<tr>{''.join(f'<th>{c}</th>' for c in head)}</tr>" if first else ""
        return f'<div class="blk ms-item" data-kind="ms"{" data-newpage" if newpage else ""}><table>{h}{row}</table></div>'

    ms_blocks = []
    for section in ("A", "B"):
        if not ms_rows[section]:
            continue
        first = section == "A"
        ms_blocks.append(f'<div class="blk ms-item" data-kind="ms"{" data-newpage" if first else ""}>'
                         f'<h2{"" if first else " class=next"}>Section {section}</h2></div>')
        for i, (qn, lab, m, h) in enumerate(ms_rows[section]):
            row = f'<tr><td class="qn-c">{qn}. {lab}</td><td class="c">[{m}]</td><td class="ms-html">{h}</td></tr>'
            ms_blocks.append(table(["Question", "Marks", "Markscheme"], row, i == 0))
    ms_instructions = [
        "This markscheme is for teachers and for self-assessment after the test.",
        "<b>M</b>: method marks. <b>A</b>: answer or accuracy marks, usually after the M mark they depend on. "
        "<b>R</b>: reasoning marks. <b>N</b> (former course): marks for a correct answer with no working.",
        "Marks in brackets, e.g. <b>(M1)</b>, can be implied by correct working that follows. <b>AG</b>: answer given "
        "in the question, no mark for it. <b>FT</b>: follow through from an earlier error.",
        f"Total: <b>[{total} marks]</b>.",
    ]
    markscheme = cover(ctx, f"Paper {num} — markscheme", ms_instructions, f"Paper {num}") + "".join(ms_blocks)

    os.makedirs(OUT, exist_ok=True)
    pages = {f"{paper['html']}.html": shell(ctx, f"W4ss Academy — Maths AA SL Paper {num} (4.1–4.6)", test),
             f"{paper['html']}-markscheme.html": shell(ctx, f"W4ss Academy — Maths AA SL Paper {num} markscheme", markscheme)}
    for fname, content in pages.items():
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(content)
        print("exams/" + fname)
    print(f"{name} : {n} questions, {total} points")


def check_no_overlap():
    seen = {}
    for name, paper in PAPERS.items():
        for qid, _, _ in paper["A"] + paper["B"]:
            if qid in seen:
                sys.exit(f"{qid} est à la fois dans {seen[qid]} et dans {name}")
            seen[qid] = name


if __name__ == "__main__":
    check_no_overlap()
    data = load_js(os.path.join(ROOT, "data", "maths-t4.js"))
    by_id = {e["id"]: e for e in data["exercises"]}
    for name in (sys.argv[1:] or sorted(PAPERS)):
        build(name, by_id)
