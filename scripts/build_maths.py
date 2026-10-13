#!/usr/bin/env python3
"""Convertit l'export Maths (ex. Maths_AA_SL_Topic_4_questions.json) en data/maths-t4.js pour maths.html.

Usage :
    python3 scripts/build_maths.py Maths_AA_SL_Topic_4_questions.json

Chaque exercice garde ses textes de contexte (contexts), reliés aux parties par context_ids, et
chaque partie garde son énoncé, son markscheme et le rapport des examinateurs. Les liens vers les
pages sources ne sont pas repris.

Le MathML de la source utilise <mfenced> (parenthèses) et <menclose notation="left|right"> (barre de
P(A | B)), que Chrome n'affiche plus : ils sont réécrits avec des <mo> ordinaires.
"""
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_exam import fix_math  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FENCED = re.compile(r"<mfenced([^>]*)>((?:(?!<mfenced\b|</mfenced>).)*)</mfenced>", re.S)
BAR = '<mo lspace="0.1em" rspace="0.1em" stretchy="false">|</mo>'


def children(s):
    """Éléments de premier niveau d'un fragment MathML."""
    kids, depth, start = [], 0, 0
    for t in re.finditer(r"<(/?)([a-zA-Z][\w:-]*)[^>]*?(/?)>", s):
        if t.group(1):
            depth -= 1
            if depth == 0:
                kids.append(s[start:t.end()])
        elif t.group(3):
            if depth == 0:
                kids.append(t.group(0))
        else:
            if depth == 0:
                start = t.start()
            depth += 1
    return kids


def unfence(m):
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    seps = attrs.get("separators", ",").replace(" ", "")
    body = ""
    for i, kid in enumerate(children(m.group(2))):
        if i and seps:
            body += f"<mo>{seps[min(i - 1, len(seps) - 1)]}</mo>"
        body += kid
    fence = lambda c: f"<mo>{c}</mo>" if c else ""  # noqa: E731
    return f'<mrow>{fence(attrs.get("open", "("))}{body}{fence(attrs.get("close", ")"))}</mrow>'


def math_core(html):
    """MathML compatible avec Chrome : mfenced -> mo, menclose (barre de P(A | B)) -> mo « | »."""
    while True:
        new = FENCED.sub(unfence, html)
        if new == html:
            break
        html = new
    html = re.sub(r'<menclose notation="left">(.*?)</menclose>', rf"<mrow>{BAR}\1</mrow>", html, flags=re.S)
    html = re.sub(r'<menclose notation="right">(.*?)</menclose>', rf"<mrow>\1{BAR}</mrow>", html, flags=re.S)
    # « 4 . 3² » : la partie décimale est dans le msup
    html = re.sub(r"<mn>\s*(\d+)\s*</mn>\s*<mo>\s*\.\s*</mo>\s*<msup>\s*<mn>\s*(\d+)\s*</mn>", r"<msup><mn>\1.\2</mn>", html)
    return fix_math(html)


def compact(html):
    html = re.sub(r"<!--.*?-->", "", html or "", flags=re.S)
    html = re.sub(r"\s+", " ", html)
    return math_core(re.sub(r">\s+<", "> <", html).strip())


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
