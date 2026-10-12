#!/usr/bin/env python3
"""Sujet « Paper 2 seul » sur B.3 : les questions longues dont l'introduction manquait dans la source.

Usage :
    python3 scripts/build_p2_paper.py
    node scripts/print_pdf.cjs exams/w4ss-b3-paper2.html exams/W4ss_Academy_Physics_B3_Paper2.pdf
    node scripts/print_pdf.cjs exams/w4ss-b3-paper2-markscheme.html exams/W4ss_Academy_Physics_B3_Paper2_Markscheme.pdf

Les introductions sont rédigées dans scripts/written_stems.py, à partir des données du markscheme officiel.
Toutes les parties de chaque question sont gardées.
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_exam import OUT, ROOT, SITE, TITLE, load_js, p2_section, page_markscheme, page_p2  # noqa: E402
from written_stems import STEMS  # noqa: E402

CODE = "W4SS–PHY–B3–P2–01"
QUESTIONS = ["EXE.2.SL.TZ0.10", "EXE.2.SL.TZ0.8", "23M.2.SL.TZ2.2", "22N.2.SL.TZ0.2"]
DURATION_MIN = 50   # même rythme que le Paper 2 HL : 150 min pour 90 points


def main():
    sub = load_js(os.path.join(ROOT, "data", "b3.js"))
    p2_by_id = {q["id"]: q for q in sub["p2"]}
    specs = [(qid, [p["key"] for p in p2_by_id[qid]["parts"]], STEMS[qid]) for qid in QUESTIONS]
    sources = []
    blocks, ms, total = p2_section(specs, p2_by_id, sources)

    today = date.today()
    ctx = dict(code=CODE, number=1, series="Paper 2 practice", title=TITLE, site=SITE,
               date=f"{today.day} {today.strftime('%B %Y')}", year=today.year)
    duration = f"{DURATION_MIN} minutes"
    extra = ("<p>The introductions of these questions are missing from the Questionbank. W4ss Academy wrote them "
             "using only the data of the official markscheme, so that the markscheme still applies.</p>")
    os.makedirs(OUT, exist_ok=True)
    pages = {
        "w4ss-b3-paper2.html": page_p2(ctx, blocks, sources, total, duration, extra),
        "w4ss-b3-paper2-markscheme.html": page_markscheme(ctx, [], ms, instructions=[
            "This markscheme is for teachers and for self-assessment after the test.",
            "Award one mark per ✓. Accept equivalent answers (OWTTE) and error carried forward (ECF) where stated.",
            f"Total: <b>[{total} marks]</b>.",
        ], duration="Paper 2", total=total),
    }
    for name, content in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("exams/" + name)
    print(f"{len(QUESTIONS)} questions, {total} points")


if __name__ == "__main__":
    main()
