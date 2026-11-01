#!/usr/bin/env python3
"""Convertit l'export Maths SL 2.1–2.5 (ex. IB_Maths_SL_2_1_to_2_5_questions.json) en data/maths-t2.js.

Usage :
    python3 scripts/build_maths_t2.py IB_Maths_SL_2_1_to_2_5_questions.json

Le format de sortie est celui de data/maths-t4.js (contextes reliés aux parties, une entrée par partie),
pour que maths.html et build_maths_exam.py traitent les deux topics de la même façon.

- Cet export n'a pas de markscheme : les corrigés rédigés par W4ss Academy (scripts/maths_t2_solutions.py)
  sont ajoutés aux parties concernées, avec ms_src = "W4ss Academy".
- Les images données seulement par un lien vers un autre site ne sont jamais chargées : elles sont
  remplacées par la figure redessinée (FIGURES) ou, à défaut, par un avertissement.
- L'export ne donne ni la section ni la date : la section vient du barème (B, questions longues, à partir
  de 12 points), la date et le fuseau de la référence (ex. 22M.1.SL.TZ1.1 : May 2022, TZ1).

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
from maths_t2_solutions import FIGURES, SOLUTIONS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MISSING = '<p class="fig-missing">[The figure of this question is not available in the source.]</p>'
MONTHS = {"M": "May", "N": "November"}


def session_date(code):
    if code == "SPM":
        return "May Specimen paper"
    if code.startswith("EX"):
        return f"{MONTHS[code[2]]} Example questions"
    return f"{MONTHS[code[2]]} 20{code[:2]}"


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    codes = {s["id"]: s["code"].replace("SL ", "") for s in data["subtopics"]}
    exercises = []
    used = set()
    for q in data["questions"]:
        def figures(html):
            for alt, svg in FIGURES.get(q["id"], {}).items():
                html, count = re.subn(rf'<img[^>]*alt="{re.escape(alt)}"[^>]*>', svg, html)
                used.update([(q["id"], alt)] if count else [])
            return re.sub(r'<p>\s*<img[^>]*src="https?://[^"]*"[^>]*>\s*</p>|<img[^>]*src="https?://[^"]*"[^>]*>', MISSING, html)

        contexts, parts, seen = [], [], []
        for i, b in enumerate(q["content_blocks"]):
            html = figures(compact(b["html"]))
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
        for p in parts:
            p["ms"] = SOLUTIONS.get(q["id"], {}).get(p["label"], "")
            p["ms_src"] = "W4ss Academy" if p["ms"] else ""
        legacy = re.search(r"\.([STH]_)\d+$", q["id"])
        session = q["id"].split(".")[0]
        exercises.append(OrderedDict(
            id=q["id"], section="B" if (q["available_marks"] or 0) >= 12 else "A", paper=q["paper"],
            session=session, date=session_date(session), tz=re.search(r"\.(TZ\d)\.", q["id"]).group(1),
            legacy=legacy.group(1) if legacy else "", marks=q["available_marks"],
            subtopics=[codes[s] for s in q["subtopics"]], contexts=contexts, parts=parts, notes=q["source_notes"],
        ))
    missing = {(qid, alt) for qid, figs in FIGURES.items() for alt in figs} - used
    assert not missing, f"figures non placées : {missing}"
    solved = {(e["id"], p["label"]) for e in exercises for p in e["parts"] if p["ms"]}
    unused = {(qid, lab) for qid, sol in SOLUTIONS.items() for lab in sol} - solved
    assert not unused, f"corrigés sans partie : {unused}"
    out = OrderedDict(subject="DP Mathematics: Analysis and Approaches", level="SL",
                      topic=OrderedDict(number=2, title="Functions",
                                        subtopics=[OrderedDict(code=s["code"].replace("SL ", ""), title=s["title"])
                                                   for s in data["subtopics"]]),
                      exercises=exercises)
    target = os.path.join(ROOT, "data", "maths-t2.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("window.QB_MATHS_T2 = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"data/maths-t2.js : {len(exercises)} questions, {sum(len(e['parts']) for e in exercises)} parties, "
          f"{len(solved)} corrigés W4ss, {os.path.getsize(target) / 1e3:.0f} ko")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
