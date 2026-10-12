#!/usr/bin/env python3
"""Sujets « Paper 2 seul » sur B.3 : les questions longues dont l'introduction manquait dans la source.

Usage :
    python3 scripts/build_p2_paper.py            # tous les sujets (ou ajouter le numéro : 2)
    node scripts/print_pdf.cjs exams/w4ss-b3-paper2-2.html exams/W4ss_Academy_Physics_B3_Paper2_2.pdf

Les introductions, graphiques et tableaux sont rédigés dans scripts/written_stems.py, à partir des
données du markscheme officiel. Toutes les parties de chaque question sont gardées.
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_exam import OUT, ROOT, SITE, TITLE, load_js, p2_section, page_markscheme, page_p2  # noqa: E402
from written_stems import STEMS  # noqa: E402

PAPERS = {
    1: dict(code="W4SS–PHY–B3–P2–01", html="w4ss-b3-paper2", level="Standard and higher level", minutes=50,
            questions=["EXE.2.SL.TZ0.10", "EXE.2.SL.TZ0.8", "23M.2.SL.TZ2.2", "22N.2.SL.TZ0.2"]),
    2: dict(code="W4SS–PHY–B3–P2–02", html="w4ss-b3-paper2-2", level="Higher level", minutes=35,
            questions=["EXE.2.HL.TZ0.1"]),
}
# durée : même rythme que le Paper 2 HL (150 minutes pour 90 points)


def build(num):
    paper = PAPERS[num]
    sub = load_js(os.path.join(ROOT, "data", "b3.js"))
    p2_by_id = {q["id"]: q for q in sub["p2"]}
    specs = [(qid, [p["key"] for p in p2_by_id[qid]["parts"]], STEMS[qid]) for qid in paper["questions"]]
    sources = []
    blocks, ms, total = p2_section(specs, p2_by_id, sources)

    today = date.today()
    ctx = dict(code=paper["code"], number=num, series="Paper 2 practice", title=TITLE, site=SITE,
               level=paper["level"], date=f"{today.day} {today.strftime('%B %Y')}", year=today.year)
    extra = ("<p>The introductions of these questions are missing from the Questionbank. W4ss Academy wrote them "
             "using only the data of the official markscheme, so that the markscheme still applies.</p>")
    os.makedirs(OUT, exist_ok=True)
    pages = {
        f"{paper['html']}.html": page_p2(ctx, blocks, sources, total, f"{paper['minutes']} minutes", extra),
        f"{paper['html']}-markscheme.html": page_markscheme(ctx, [], ms, instructions=[
            "This markscheme is for teachers and for self-assessment after the test.",
            "Award one mark per ✓. Accept equivalent answers (OWTTE) and error carried forward (ECF) where stated.",
            f"Total: <b>[{total} marks]</b>.",
        ], duration="Paper 2", total=total),
    }
    for name, content in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("exams/" + name)
    print(f"sujet {num} : {len(paper['questions'])} question(s), {total} points")


if __name__ == "__main__":
    for num in ([int(sys.argv[1])] if len(sys.argv) > 1 else sorted(PAPERS)):
        build(num)
