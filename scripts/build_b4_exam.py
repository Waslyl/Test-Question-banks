#!/usr/bin/env python3
"""Sujets d'entraînement W4ss Academy sur B.4 Thermodynamics : Paper 1A et Paper 2 dans le même sujet, 30 minutes.

Usage :
    python3 scripts/build_b4_exam.py            # tous les sujets (ou ajouter le numéro : 2)
    node scripts/print_pdf.cjs exams/w4ss-b4-test-2.html exams/W4ss_Academy_Physics_B4_Test_2.pdf

Même format que les sujets B.3 (build_exam.py), mais 20 points répartis autrement : l'export B.4 n'a que
10 QCM, partagés entre les trois sujets. Les questions viennent de data/b4.js (import_b4.py) ; les
introductions des questions Paper 2 sont celles rédigées dans b4_content.py. Aucun QCM ni aucune partie
ne sert dans deux sujets.
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b4_content import METHODS, STEMS  # noqa: E402
from build_exam import OUT, ROOT, SITE, clean, load_js, p2_section, page_markscheme, page_test  # noqa: E402

TITLE = "B.4 Thermodynamics"


def stem(qid, **extra):
    return dict(intro=STEMS[qid]["intro"], note=STEMS[qid]["note"], **extra)


PAPERS = {
    1: dict(code="W4SS–PHY–B4–01",
            qcm=["EXE.1A.HL.TZ0.17", "EXE.1A.HL.TZ0.18", "EXE.1A.HL.TZ0.23", "EXE.1A.HL.TZ0.21"],
            p2=[("19M.2.HL.TZ1.7", ["a", "bi", "bii", "biii", "ci", "cii"], stem("19M.2.HL.TZ1.7")),
                ("EXE.2.HL.TZ0.11", ["a", "b"], stem("EXE.2.HL.TZ0.11"))]),
    2: dict(code="W4SS–PHY–B4–02",
            qcm=["EXE.1A.HL.TZ0.22", "SPM.1A.HL.TZ0.11", "EXE.1A.HL.TZ0.19"],
            p2=[("23M.2.SL.TZ1.9", ["a", "b", "c", "d", "e"], stem("23M.2.SL.TZ1.9")),
                ("EXE.2.HL.TZ0.14", ["a", "b", "c"], stem("EXE.2.HL.TZ0.14"))]),
    3: dict(code="W4SS–PHY–B4–03",
            qcm=["EXE.1A.HL.TZ0.20", "EXE.1A.HL.TZ0.24", "SPM.1A.HL.TZ0.12"],
            p2=[("23M.2.HL.TZ2.7", ["a", "b", "c", "d", "e", "f"], stem("23M.2.HL.TZ2.7")),
                # (a) n'est pas reprise : (b), (c), (d) deviennent (a), (b), (c)
                ("EXE.2.HL.TZ0.12", ["b", "c", "d"], stem("EXE.2.HL.TZ0.12", relabel={"b": "a", "c": "b", "d": "c"},
                                                          replace={"d": [("answer in (c)", "answer in (b)")]}))]),
}
INTRO = ("This practice test was put together by W4ss Academy for internal class use. The questions are taken "
         "from the IB DP Physics Questionbank (first assessment 2025), topic B.4 Thermodynamics. The introductions "
         "of the Paper 2 questions are missing from the source: W4ss Academy wrote them using only the data of the "
         "official markscheme, so that the markscheme still applies. The questions remain the property of the "
         "International Baccalaureate Organization and must not be published or sold.")


def build(num, sub):
    paper = PAPERS[num]
    qcm = {q["id"]: q for q in sub["p1a"]}
    p2_by_id = {q["id"]: q for q in sub["p2"]}
    blocks, keys, sources = [], [], []
    for n, qid in enumerate(paper["qcm"], 1):
        q = qcm[qid]
        blocks.append(f'<div class="blk" data-kind="p1a"><div class="qn"><span class="num">{n}.</span>'
                      f'<div class="qbody">{clean(q["q"])}<div class="options"></div></div></div></div>')
        answer, steps = METHODS[qid]
        keys.append((n, {"correct_option": answer}, {"steps": steps}))
        sources.append((f"Paper 1A — question {n}", qid))
    p2_blocks, ms, total = p2_section(paper["p2"], p2_by_id, sources)
    marks = (len(blocks), total)
    assert sum(marks) == 20, marks

    today = date.today()
    ctx = dict(code=paper["code"], number=num, title=TITLE, site=SITE, level="Higher level",
               date=f"{today.day} {today.strftime('%B %Y')}", year=today.year)
    suffix = "" if num == 1 else f"-{num}"
    os.makedirs(OUT, exist_ok=True)
    for name, content in (
            (f"w4ss-b4-test{suffix}.html",
             page_test(ctx, blocks, p2_blocks, sources, marks=marks, intro=INTRO,
                       title="W4ss Academy — Physics B.4 practice test")),
            (f"w4ss-b4-markscheme{suffix}.html",
             page_markscheme(ctx, keys, ms, total=sum(marks), title="W4ss Academy — Physics B.4 markscheme"))):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("exams/" + name)
    print(f"sujet {num} : {marks[0]} QCM + {marks[1]} points de Paper 2")


def check_no_overlap():
    seen = {}
    for num, paper in PAPERS.items():
        for item in paper["qcm"] + [f"{qid} ({k})" for qid, keys, _ in paper["p2"] for k in keys]:
            assert item not in seen, f"{item} est dans les sujets {seen[item]} et {num}"
            seen[item] = num


if __name__ == "__main__":
    check_no_overlap()
    sub = load_js(os.path.join(ROOT, "data", "b4.js"))
    for num in ([int(sys.argv[1])] if len(sys.argv) > 1 else sorted(PAPERS)):
        build(num, sub)
