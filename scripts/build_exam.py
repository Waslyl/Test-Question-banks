#!/usr/bin/env python3
"""Génère un sujet d'entraînement W4ss Academy (Paper 1A + Paper 2) et son markscheme, en HTML.

Usage :
    python3 scripts/build_exam.py export_B3.json
    node scripts/print_pdf.cjs exams/w4ss-b3-test.html exams/W4ss_Academy_Physics_B3_Test.pdf

La mise en page reprend celle des sujets de physique du DP (couverture, numérotation « – n – »,
« Turn over », cadres de réponse en pointillés) avec l'identité W4ss Academy.
"""
import html as htmlmod
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "exams")

CODE = "W4SS–PHY–B3–01"
TITLE = "B.3 Gas laws"
SITE = "waslyl.github.io/Test-Question-banks"

# 10 QCM (clé unique de l'export B.3), dans l'ordre du sujet
QCM = [
    "qcm_8d8b0b07c0fb",  # 20N.1A.SL.TZ0.12  distance entre molécules
    "qcm_cd020f734c07",  # 19N.1A.SL.TZ0.9   gaz réel ≈ gaz parfait
    "qcm_506630153200",  # 20N.1A.SL.TZ0.11  origine de la pression
    "qcm_32d5e7548033",  # 21N.1A.SL.TZ0.12  333 °C
    "qcm_920155f589aa",  # 22N.1A.SL.TZ0.10  constante de Boltzmann
    "qcm_d6f55b33e326",  # 21M.1A.SL.TZ1.10  énergie cinétique et vitesse moyennes
    "qcm_a28992795606",  # 19M.1A.SL.TZ1.13  réservoir, N/4 molécules
    "qcm_3282e5b185de",  # 21M.1A.SL.TZ1.12  80 kPa
    "qcm_f4036d4a0136",  # 19M.1A.SL.TZ2.12  argon / néon
    "qcm_db579e54282b",  # 22M.1A.SL.TZ1.12  graphe P en fonction de 1/V
]
# Paper 2 : (question, parties retenues) — 6 + 4 = 10 points
P2 = [
    ("22M.2.SL.TZ2.2", ["a", "bi", "bii"]),
    ("EXE.2.SL.TZ0.9", ["b"]),
]


def load_js(path):
    s = open(path, encoding="utf-8").read()
    return json.loads(s[s.index("=") + 1:].strip().rstrip(";"))


def clean(h):
    """HTML d'énoncé sans les libellés, barèmes et styles parasites de la source."""
    h = re.sub(r'<div class="(?:marks|question_part_label|qc_marks_available|qn_code_number)">.*?</div>', "", h, flags=re.S)
    h = re.sub(r'\sstyle="[^"]*"', "", h)
    h = re.sub(r'<div class="(?:t_qn_question_content|qc_body[^"]*|question)"[^>]*>', "<div>", h)
    h = re.sub(r"<p>\s*(?:&nbsp;|\s)*</p>", "", h)
    return h.strip()


def marks_of(h):
    return sum(int(m) for m in re.findall(r"\[(\d+)\]", re.sub(r"<[^>]+>", "", h)))


def options_html(q):
    if q.get("option_columns"):
        head = "".join(f"<th>{htmlmod.escape(c)}</th>" for c in q["option_columns"])
        rows = "".join(
            f'<tr><td class="lbl">{o["label"]}.</td>' + "".join(f"<td>{htmlmod.escape(v)}</td>" for v in o["values"]) + "</tr>"
            for o in q["options"])
        return f'<table class="opt-table"><tr><th class="lbl"></th>{head}</tr>{rows}</table>'
    return "".join(f'<div class="opt"><span class="lbl">{o["label"]}.</span><span>{o.get("html") or htmlmod.escape(o["text"])}</span></div>'
                   for o in q["options"])


def roman_label(key):
    """'bi' -> ('b', 'i')"""
    return key[:1], key[1:]


def answer_box(marks):
    return '<div class="answer-box">' + '<div class="dots"></div>' * (2 * marks) + "</div>"


def build(export_path):
    export = json.load(open(export_path, encoding="utf-8"))
    qcm_by_key = {q["id"]: q for q in export["qcm"]}
    methods = json.load(open(os.path.join(ROOT, "data", "methods", "b3.json"), encoding="utf-8"))
    sub = load_js(os.path.join(ROOT, "data", "b3.js"))
    p2_by_id = {q["id"]: q for q in sub["p2"]}

    # ---------- Paper 1A ----------
    p1a_blocks, key_rows, sources = [], [], []
    for n, k in enumerate(QCM, 1):
        q = qcm_by_key[k]
        statement = clean(q["statement"]["html"])
        p1a_blocks.append(
            f'<div class="blk" data-kind="p1a"><div class="qn"><span class="num">{n}.</span>'
            f'<div class="qbody">{statement}<div class="options">{options_html(q)}</div></div></div></div>')
        key_rows.append((n, q, methods[k]))
        sources.append((f"Paper 1A — question {n}", q["reference"]))

    # ---------- Paper 2 ----------
    p2_blocks, ms_p2, total_p2 = [], [], 0
    first = True
    for n, (qid, keys) in enumerate(P2, 1):
        q = p2_by_id[qid]
        parts = [p for p in q["parts"] if p["key"] in keys]
        intro = "".join(clean(p["pre"]) for p in parts if p["pre"])
        lead = '<p class="lead">Answer <strong>all</strong> questions. Answers must be written within the answer boxes provided.</p>' if first else ""
        first = False
        single = len(parts) == 1
        prev_letter = None
        for i, p in enumerate(parts):
            m = marks_of(p["q"])
            total_p2 += m
            letter, roman = roman_label(p["key"])
            body = clean(p["q"])
            if single:
                label = ""
            elif roman and letter == prev_letter:
                label = f'<span class="pl"></span><span class="pr">({roman})</span>'
            elif roman:
                label = f'<span class="pl">({letter})</span><span class="pr">({roman})</span>'
            else:
                label = f'<span class="pl">({letter})</span>'
            prev_letter = letter
            head = ""
            if i == 0 and not single:
                head = f'{lead}<div class="qn p2"><span class="num">{n}.</span><div class="qbody">{intro}</div></div>'
            elif i == 0:
                head = lead
                label = f'<span class="num">{n}.</span>'
            text = (intro + body) if single else body
            p2_blocks.append(
                f'<div class="blk" data-kind="p2" data-q="{n}">{head}'
                f'<div class="part{" single" if single else ""}{" sub" if roman and not single else ""}">'
                f'<div class="part-label">{label}</div><div class="part-text">{text}</div>'
                f'<div class="part-marks">[{m}]</div></div>{answer_box(m)}</div>')
            ms_p2.append((n, display_label(letter, roman) if not single else "", m, p["ms"]))
        sources.append((f"Paper 2 — question {n}", qid + ("" if len(parts) == len(q["parts"]) else
                                                            " (part " + ", ".join(display_label(*roman_label(k)) for k in keys) + ")")))
    assert total_p2 == 10, total_p2

    today = date.today()
    ctx = dict(code=CODE, title=TITLE, site=SITE, date=f"{today.day} {today.strftime('%B %Y')}", year=today.year)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "w4ss-b3-test.html"), "w", encoding="utf-8") as f:
        f.write(page_test(ctx, p1a_blocks, p2_blocks, sources))
    with open(os.path.join(OUT, "w4ss-b3-markscheme.html"), "w", encoding="utf-8") as f:
        f.write(page_markscheme(ctx, key_rows, ms_p2))
    print("exams/w4ss-b3-test.html et exams/w4ss-b3-markscheme.html générés")


def display_label(letter, roman):
    return f"({letter})" + (f"({roman})" if roman else "")


# ---------------------------------------------------------------- gabarits

BRAND = """
<svg class="brand" viewBox="0 0 250 64" xmlns="http://www.w3.org/2000/svg" aria-label="W4ss Academy">
  <path d="M30 2 H236 L248 2 Q236 34 222 62 H30 Z" fill="#555"/>
  <path d="M222 62 Q236 34 248 2 L250 2 Q242 36 230 62 Z" fill="#999"/>
  <circle cx="32" cy="32" r="30" fill="#2b2b2b" stroke="#fff" stroke-width="2"/>
  <text x="32" y="41" text-anchor="middle" font-family="Liberation Sans, Arial" font-weight="700" font-size="25" fill="#fff">W4</text>
  <text x="74" y="22" font-family="Liberation Sans, Arial" font-size="12.5" font-weight="700" fill="#fff">W4ss Academy</text>
  <text x="74" y="38" font-family="Liberation Sans, Arial" font-size="10.5" fill="#fff">DP Physics · 2025 syllabus</text>
  <text x="74" y="53" font-family="Liberation Sans, Arial" font-size="11" fill="#fff">Practice papers</text>
</svg>"""

BAND = """
<svg class="band" viewBox="0 0 400 70" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 70 Q170 10 400 4 V70 Z" fill="#cfcfcf"/>
  <path d="M60 70 Q200 22 400 16 V70 Z" fill="#4a4a4a"/>
  <circle cx="318" cy="46" r="15" fill="#fff"/>
  <text x="318" y="51" text-anchor="middle" font-family="Liberation Sans, Arial" font-weight="700" font-size="13" fill="#2b2b2b">W4</text>
  <text x="338" y="44" font-family="Liberation Sans, Arial" font-size="7.5" font-weight="700" fill="#fff">W4ss Academy</text>
  <text x="338" y="54" font-family="Liberation Sans, Arial" font-size="6.5" fill="#fff">Practice papers</text>
</svg>"""

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Liberation Sans", Arial, Helvetica, sans-serif; font-size: 10.6pt; color: #111; line-height: 1.38; }
#flow { position: absolute; left: -10000px; width: 170mm; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
.page .hdr { position: absolute; top: 12mm; left: 20mm; right: 20mm; height: 6mm; font-size: 10pt; }
.page .hdr .pn { position: absolute; left: 0; right: 0; text-align: center; }
.page .hdr .code { position: absolute; right: 0; font-size: 8.5pt; top: 1px; }
.page .body { position: absolute; top: 22mm; left: 20mm; right: 20mm; bottom: 24mm; }
.page .ftr { position: absolute; left: 20mm; right: 20mm; bottom: 14mm; height: 6mm; font-weight: 700; font-size: 10pt; }
.page .ftr .note { position: absolute; left: 0; }
.page .ftr .turn { position: absolute; right: 0; }
.page.p2 .corner { position: absolute; width: 6mm; height: 6mm; border-color: #222; border-style: solid; border-width: 0; }
.page.p2 .c1 { top: 8mm; left: 8mm; border-top-width: 1px; border-left-width: 1px; }
.page.p2 .c2 { top: 8mm; right: 8mm; border-top-width: 1px; border-right-width: 1px; }
.page.p2 .c3 { bottom: 8mm; left: 8mm; border-bottom-width: 1px; border-left-width: 1px; }
.page.p2 .c4 { bottom: 8mm; right: 8mm; border-bottom-width: 1px; border-right-width: 1px; }
.page.p2 .stripe { position: absolute; top: 0; bottom: 0; width: 4mm; background: repeating-linear-gradient(135deg, #bbb 0 1px, #fff 1px 3px); }
.page.p2.odd .stripe { left: 0; } .page.p2.even .stripe { right: 0; }

/* couverture */
.cover .brand { position: absolute; top: 9mm; right: 18mm; width: 84mm; }
.cover .band { position: absolute; bottom: 0; right: 0; width: 140mm; height: 24mm; }
.cover .inner { position: absolute; top: 36mm; left: 19mm; right: 19mm; }
.cover h1 { font-size: 13.5pt; line-height: 1.32; margin: 0 0 12px; }
.cover .date { font-size: 8.5pt; margin-bottom: 6px; }
.cover .zones { font-size: 8.5pt; margin-bottom: 16px; }
.cover .zones b { font-weight: 700; }
.cover .zones .sep { display: inline-block; border-left: 1px solid #111; height: 9pt; vertical-align: -1px; margin: 0 6px; }
.cover .row { display: flex; align-items: flex-end; justify-content: space-between; border-bottom: 1.6px solid #111; padding-bottom: 6px; }
.cover .duration { font-size: 10.5pt; }
.cover .name-box { text-align: center; font-size: 10.5pt; }
.cover .name-box .boxes { display: flex; border: 1px solid #333; height: 8.5mm; width: 98mm; margin-top: 3px; }
.cover .name-box .boxes span { flex: 1; border-left: 1px solid #333; }
.cover .name-box .boxes span:first-child { border-left: 0; }
.cover h2 { font-size: 10.5pt; margin: 14px 0 8px; }
.cover ul { margin: 0; padding-left: 18px; }
.cover li { margin: 1px 0; }
.cover .foot { position: absolute; bottom: 30mm; left: 28mm; right: 19mm; font-size: 10.5pt; }
.cover .foot .pages { position: absolute; left: 0; bottom: 0; }
.cover .foot .rights { position: absolute; right: 0; bottom: 0; text-align: right; line-height: 1.5; }
.cover .foot .rights .c { font-size: 8.5pt; }
.cover .site { position: absolute; left: 19mm; bottom: 9mm; font-size: 7.5pt; color: #444; }

/* questions */
.blk { padding-bottom: 7mm; }
.qn { display: flex; }
.qn .num { width: 11mm; flex: none; font-weight: 700; }
.qbody { flex: 1; min-width: 0; }
.qbody p { margin: 0 0 3.2mm; }
.qbody img { max-width: 100%; height: auto; display: block; margin: 2mm auto 3mm; }
.qbody table { border-collapse: collapse; }
.options { margin-top: 1mm; }
.opt { display: flex; margin: 0 0 3.6mm; min-height: 5mm; align-items: center; }
.opt .lbl { width: 10mm; flex: none; }
.opt-table { border-collapse: collapse; margin: 1mm 0 2mm -10mm; }
.opt-table th, .opt-table td { border: 1px solid #222; padding: 1.4mm 4mm; text-align: center; min-width: 44mm; font-size: 10pt; }
.opt-table th { font-weight: 700; }
.opt-table .lbl { border: 0; min-width: 10mm; width: 10mm; text-align: left; padding-left: 0; }
math { font-family: "Liberation Sans", Arial, sans-serif; math-style: normal; font-size: 1em; }
math mi { text-transform: none; }
math mfrac { padding: 0 1px; }
.lead { margin: 0 0 6mm; }
.qn.p2 { margin-bottom: 1mm; }
.part { display: flex; align-items: flex-start; margin: 3mm 0 3mm; }
.part .part-label { width: 22mm; flex: none; padding-left: 11mm; display: flex; }
.part.sub .part-label { width: 32mm; }
.part .part-label .pl { width: 10mm; flex: none; }
.part .part-label .pr { width: 10mm; flex: none; }
.part.single .part-label { width: 11mm; padding-left: 0; font-weight: 700; }
.part .part-marks { align-self: flex-end; }
.part .part-text { flex: 1; min-width: 0; }
.part .part-text p { margin: 0 0 2mm; }
.part .part-text p:last-child, .part .part-text > div:last-child > p:last-child { margin-bottom: 0; }
.part .part-marks { width: 12mm; flex: none; text-align: right; }
.answer-box { border: 1px solid #222; padding: 3mm 9mm 4mm; }
.answer-box .dots { height: 7.4mm; border-bottom: 1.4px dotted #444; }
.cont { font-weight: 700; margin-bottom: 4mm; }
.section-title { font-weight: 700; font-size: 11.5pt; margin: 0 0 5mm; }
.end-rule { border-top: 1px solid #222; margin-top: 4mm; }

/* feuille de réponses */
.sheet h2 { font-size: 12pt; margin: 0 0 3mm; }
.sheet .who { display: flex; gap: 10mm; margin: 4mm 0 7mm; }
.sheet .who div { flex: 1; border-bottom: 1px solid #222; padding-bottom: 6mm; font-size: 9.5pt; }
.sheet table { border-collapse: collapse; margin: 0 auto; }
.sheet td { padding: 2.2mm 4mm; text-align: center; }
.sheet td.n { font-weight: 700; text-align: right; width: 12mm; }
.sheet .bubble { display: inline-block; width: 9mm; height: 6.2mm; border: 1.2px solid #222; border-radius: 50%; font-size: 8.5pt; line-height: 6mm; color: #555; }
.sheet .hint { font-size: 9pt; margin: 8mm 0 0; color: #333; }

.blank-note { position: absolute; top: 118mm; left: 50%; transform: translateX(-50%); border: 1px solid #222; padding: 5mm 8mm; text-align: center; width: 84mm; }
.blank-note p { margin: 0 0 4mm; } .blank-note p:last-child { margin: 0; }

/* sources */
.sources h2 { font-size: 11.5pt; margin: 0 0 4mm; }
.sources table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
.sources td { border-bottom: 1px solid #ccc; padding: 1.6mm 2mm; }
.sources p { font-size: 9pt; color: #333; }

/* markscheme */
.ms-item { padding-bottom: 0; }
.ms-item h2 { font-size: 12pt; margin: 0 0 4mm; }
.ms-item table { border-collapse: collapse; width: 100%; table-layout: fixed; }
.ms-item th:nth-child(1), .ms-item td:nth-child(1) { width: 22mm; }
.ms-item th:nth-child(2), .ms-item td:nth-child(2) { width: 18mm; }
.ms-item + .ms-item table { margin-top: -1px; }
.ms-item th, .ms-item td { border: 1px solid #222; padding: 2mm 3mm; vertical-align: top; text-align: left; font-size: 9.6pt; }
.ms-item th { background: #eee; }
.ms-item td.c { text-align: center; font-weight: 700; }
.ms-item td.qn-c { text-align: center; font-weight: 700; }
.ms-item ol { margin: 0; padding-left: 5mm; }
.ms-item li { margin: 0 0 1mm; }
.ms-item .ms-html p { margin: 0 0 1.5mm; }
"""

PAGINATE = """
<script>
// variables d'une lettre en italique, comme dans les sujets (les unités et mots restent droits)
Array.prototype.forEach.call(document.querySelectorAll("math mi"), function (mi) {
  if (mi.textContent.trim().length === 1 && mi.getAttribute("mathvariant") !== "normal") mi.style.fontStyle = "italic";
});
(function () {
  var CODE = document.body.getAttribute("data-code");
  var holder = document.getElementById("pages");
  var flow = document.getElementById("flow");
  var pages = [];
  var cur = null;

  function newPage(kind) {
    var p = document.createElement("section");
    p.className = "page " + kind;
    p.innerHTML = '<div class="hdr"><span class="pn"></span><span class="code"></span></div>' +
      '<div class="body"></div><div class="ftr"><span class="note"></span><span class="turn"></span></div>' +
      (kind === "p2" ? '<span class="corner c1"></span><span class="corner c2"></span><span class="corner c3"></span><span class="corner c4"></span><span class="stripe"></span>' : "");
    holder.appendChild(p);
    pages.push(p);
    cur = { el: p, kind: kind, body: p.querySelector(".body") };
    return cur;
  }

  Array.prototype.slice.call(flow.children).forEach(function (blk) {
    if (blk.classList.contains("page")) {          // page fixe (couverture, feuille de réponses...)
      holder.appendChild(blk); pages.push(blk); cur = null; return;
    }
    var kind = blk.getAttribute("data-kind");
    if (!cur || cur.kind !== kind || blk.hasAttribute("data-newpage")) newPage(kind);
    cur.body.appendChild(blk);
    if (cur.body.scrollHeight > cur.body.clientHeight + 1 && cur.body.children.length > 1) {
      cur.body.removeChild(blk);
      var last = cur.body.lastElementChild;
      var q = blk.getAttribute("data-q");
      var continues = kind === "p2" && q && last && last.getAttribute("data-q") === q;
      if (continues) cur.el.querySelector(".ftr .note").textContent = "(This question continues on the following page)";
      newPage(kind);
      if (continues) {
        var c = document.createElement("div");
        c.className = "cont"; c.textContent = "(Question " + q + " continued)";
        cur.body.appendChild(c);
      }
      cur.body.appendChild(blk);
    }
  });

  // nombre pair de pages, comme un livret d'examen
  if (pages.length % 2) {
    var b = document.createElement("section");
    b.className = "page blank";
    b.innerHTML = '<div class="hdr"><span class="pn"></span><span class="code"></span></div>' +
      '<div class="blank-note"><p>Please <strong>do not</strong> write on this page.</p><p>Answers written on this page<br>will not be marked.</p></div>';
    holder.appendChild(b); pages.push(b);
  }

  var total = pages.length;
  pages.forEach(function (p, i) {
    var n = i + 1;
    p.classList.add(n % 2 ? "odd" : "even");
    var pn = p.querySelector(".hdr .pn"), code = p.querySelector(".hdr .code");
    if (pn && n > 1) pn.textContent = "– " + n + " –";
    if (code && n > 1) code.textContent = CODE;
    var turn = p.querySelector(".ftr .turn");
    if (turn && n % 2 === 1 && n < total && !pages[n].classList.contains("blank")) turn.textContent = "Turn over";
  });
  var tp = document.getElementById("total-pages");
  if (tp) tp.textContent = total + " pages";
  document.body.setAttribute("data-ready", "1");
})();
</script>
"""


def shell(ctx, title, inner):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{htmlmod.escape(title)}</title><style>{CSS}</style></head>
<body data-code="{ctx['code']}"><div id="pages"></div><div id="flow">{inner}</div>{PAGINATE}</body></html>"""


def cover(ctx, kind_label, instructions, duration):
    return f"""<section class="page cover">{BRAND}
<div class="inner">
  <h1>Physics<br>Standard and higher level<br>{kind_label}<br>{ctx['title']}</h1>
  <div class="date">{ctx['date']}</div>
  <div class="zones"><b>W4ss Academy</b> practice test<span class="sep"></span><b>Topic</b> {ctx['title']}<span class="sep"></span><b>Ref.</b> {ctx['code']}</div>
  <div class="row"><div class="duration">{duration}</div>
    <div class="name-box">Student name<div class="boxes">{'<span></span>' * 12}</div></div></div>
  <h2>Instructions to students</h2>
  <ul>{''.join(f'<li>{i}</li>' for i in instructions)}</ul>
</div>
<div class="foot"><span class="pages" id="total-pages"></span>
  <span class="rights">{ctx['code']}<br><span class="c">W4ss Academy {ctx['year']}</span></span></div>
<div class="site">Online revision: {ctx['site']}</div>{BAND}</section>"""


def page_test(ctx, p1a_blocks, p2_blocks, sources):
    instructions = [
        "Write your name in the boxes above.",
        "Do not open this examination paper until instructed to do so.",
        "Answer all questions.",
        "<b>Paper 1A:</b> for each question, choose the answer you consider to be the best and indicate your choice on the answer sheet provided.",
        "<b>Paper 2:</b> answers must be written within the answer boxes provided.",
        "A calculator is required for this paper.",
        "A clean copy of the <b>physics data booklet</b> is required for this paper.",
        "The maximum mark for paper 1A is <b>[10 marks]</b>.",
        "The maximum mark for paper 2 is <b>[10 marks]</b>.",
        "The maximum mark for this examination paper is <b>[20 marks]</b>.",
    ]
    p1a_blocks = list(p1a_blocks)
    p1a_blocks[0] = p1a_blocks[0].replace('data-kind="p1a"', 'data-kind="p1a" data-newpage', 1).replace(
        '<div class="qn">', '<div class="section-title">Paper 1A</div><div class="qn">', 1)
    p1a_blocks[-1] = p1a_blocks[-1].replace("</div></div></div></div>", '</div></div></div><div class="end-rule"></div></div>')
    p2_blocks = list(p2_blocks)
    p2_blocks[0] = p2_blocks[0].replace('data-kind="p2"', 'data-kind="p2" data-newpage', 1).replace(
        '<p class="lead">', '<div class="section-title">Paper 2</div><p class="lead">', 1)
    rows = "".join(
        f'<tr><td class="n">{n}.</td>' + "".join(f'<td><span class="bubble">{l}</span></td>' for l in "ABCD") + "</tr>"
        for n in range(1, len(p1a_blocks) + 1))
    sheet = f"""<section class="page sheet"><div class="hdr"><span class="pn"></span><span class="code"></span></div>
<div class="body"><h2>Paper 1A — answer sheet</h2>
<div class="who"><div>Student name</div><div>Date</div></div>
<table>{rows}</table>
<p class="hint">Shade <b>one</b> circle per question. If you change your answer, cross out the wrong circle clearly.</p>
</div></section>"""
    src_rows = "".join(f"<tr><td>{htmlmod.escape(a)}</td><td>{htmlmod.escape(b)}</td></tr>" for a, b in sources)
    src = f"""<section class="page sources"><div class="hdr"><span class="pn"></span><span class="code"></span></div>
<div class="body"><h2>Sources of the questions</h2>
<p>This practice test was put together by W4ss Academy for internal class use. The questions are taken from the
IB DP Physics Questionbank (first assessment 2025), topic B.3 Gas laws. They remain the property of the
International Baccalaureate Organization and must not be published or sold.</p>
<table>{src_rows}</table></div></section>"""
    inner = cover(ctx, "Paper 1A and Paper 2", instructions, "30 minutes [Paper 1A and Paper 2]") + \
        "".join(p1a_blocks) + sheet + "".join(p2_blocks) + src
    return shell(ctx, "W4ss Academy — Physics B.3 practice test", inner)


def page_markscheme(ctx, key_rows, ms_p2):
    def table(head, row, first, newpage=False):
        h = f"<tr>{''.join(f'<th>{c}</th>' for c in head)}</tr>" if first else ""
        return f'<div class="blk ms-item" data-kind="ms"{" data-newpage" if newpage else ""}><table>{h}{row}</table></div>'

    blocks = ['<div class="blk ms-item" data-kind="ms" data-newpage><h2>Paper 1A — answers and methods</h2></div>']
    for i, (n, q, m) in enumerate(key_rows):
        row = (f'<tr><td class="qn-c">{n}.</td><td class="c">{q["correct_option"]}</td><td><ol>'
               + "".join(f"<li>{s}</li>" for s in m["steps"]) + "</ol></td></tr>")
        blocks.append(table(["Question", "Answer", "Method"], row, i == 0))
    blocks.append('<div class="blk ms-item" data-kind="ms" data-newpage><h2>Paper 2 — markscheme</h2></div>')
    for i, (n, lab, m, h) in enumerate(ms_p2):
        row = f'<tr><td class="qn-c">{n}. {lab}</td><td class="c">[{m}]</td><td class="ms-html">{clean(h)}</td></tr>'
        blocks.append(table(["Question", "Marks", "Answers"], row, i == 0))
    instructions = [
        "This markscheme is for teachers and for self-assessment after the test.",
        "Paper 1A: one mark per correct answer. The method (in French) shows how to find each answer.",
        "Paper 2: award one mark per ✓ in the markscheme. Accept equivalent answers (OWTTE).",
        "Total: <b>[20 marks]</b>.",
    ]
    inner = cover(ctx, "Markscheme", instructions, "Paper 1A and Paper 2") + "".join(blocks)
    return shell(ctx, "W4ss Academy — Physics B.3 markscheme", inner)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(sys.argv[1])
