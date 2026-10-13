#!/usr/bin/env python3
"""Convertit l'export Maths (ex. Maths_AA_SL_Topic_4_questions.json) en data/maths-t4.js pour maths.html.

Usage :
    python3 scripts/build_maths.py Maths_AA_SL_Topic_4_questions.json

Chaque exercice garde ses textes de contexte (contexts), reliés aux parties par context_ids, et
chaque partie garde son énoncé, son markscheme et le rapport des examinateurs. Les liens vers les
pages sources ne sont pas repris.
"""
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def compact(html):
    html = re.sub(r"<!--.*?-->", "", html or "", flags=re.S)
    html = re.sub(r"\s+", " ", html)
    return re.sub(r">\s+<", "> <", html).strip()


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    exercises = []
    for section, items in data["sections"].items():
        for e in items:
            parts = []
            for p in e["parts"]:
                parts.append(OrderedDict(
                    label=p["label"], type=p["type"], marks=p["marks"], ctx=p["context_ids"],
                    q=compact(p["statement"]["html"]), ms=compact(p["markscheme"]["html"]),
                    er=compact(p["examiners_report"]["html"]),
                ))
            exercises.append(OrderedDict(
                id=e["reference"], section=section, paper=e["paper"], session=e["session"], date=e["date"],
                tz=e["time_zone"], num=e["question_number"], legacy=e.get("legacy_prefix") or "",
                marks=e["marks_in_topic4"], context_status=e["context_status"],
                contexts=[OrderedDict(id=c["id"], html=compact(c["html"])) for c in e["contexts"]],
                parts=parts,
            ))
    out = OrderedDict(
        subject=data["subject"], level=data["level"],
        topic=OrderedDict(number=data["topic"]["number"], title=data["topic"]["title"]),
        exercises=exercises,
    )
    target = os.path.join(ROOT, "data", "maths-t4.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("window.QB_MATHS = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    n_parts = sum(len(e["parts"]) for e in exercises)
    print(f"data/maths-t4.js : {len(exercises)} exercices, {n_parts} parties, "
          f"{sum(p['marks'] for e in exercises for p in e['parts'])} points, {os.path.getsize(target) / 1e6:.1f} Mo")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
