#!/usr/bin/env python3
"""Convertit l'export Maths SL 2.1–2.5 (ex. IB_Maths_SL_2_1_to_2_5_questions.json) en data/maths-t2.js.

Usage :
    python3 scripts/build_maths_t2.py IB_Maths_SL_2_1_to_2_5_questions.json

Le format de sortie est celui de data/maths-t4.js (contextes reliés aux parties, une entrée par partie),
pour que build_maths_exam.py traite les deux topics de la même façon. Cet export n'a pas de markscheme :
les corrigés sont rédigés à part, dans scripts/maths_t2_solutions.py.

Les blocs de l'export sont dans l'ordre de la page : chaque partie reçoit tous les contextes qui la
précèdent. Une question sans partie (tout l'énoncé dans un contexte) devient une partie sans libellé.
"""
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_maths import compact  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    codes = {s["id"]: s["code"].replace("SL ", "") for s in data["subtopics"]}
    exercises = []
    for q in data["questions"]:
        contexts, parts, seen = [], [], []
        for i, b in enumerate(q["content_blocks"]):
            html = compact(b["html"])
            if b["type"] == "context":
                cid = f"ctx{i}"
                contexts.append(OrderedDict(id=cid, html=html))
                seen.append(cid)
            else:
                parts.append(OrderedDict(label=(b["part"] or "").rstrip("."), type="question", marks=b["marks"],
                                         ctx=list(seen), q=html, ms="", er=""))
        if not parts:   # tout l'énoncé est dans le dernier contexte
            last = contexts.pop()
            parts.append(OrderedDict(label="", type="question", marks=q["available_marks"],
                                     ctx=[c["id"] for c in contexts], q=last["html"], ms="", er=""))
        legacy = re.search(r"\.([STH]_)\d+$", q["id"])
        exercises.append(OrderedDict(
            id=q["id"], paper=q["paper"], session=q["id"].split(".")[0], legacy=legacy.group(1) if legacy else "",
            marks=q["available_marks"], subtopics=[codes[s] for s in q["subtopics"]],
            contexts=contexts, parts=parts, notes=q["source_notes"],
        ))
    out = OrderedDict(subject="DP Mathematics: Analysis and Approaches", level="SL",
                      topic=OrderedDict(number=2, title="Functions", subtopics="2.1–2.5"), exercises=exercises)
    target = os.path.join(ROOT, "data", "maths-t2.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("window.QB_MATHS_T2 = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"data/maths-t2.js : {len(exercises)} questions, {sum(len(e['parts']) for e in exercises)} parties, "
          f"{os.path.getsize(target) / 1e3:.0f} ko")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
