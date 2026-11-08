#!/usr/bin/env python3
"""Construit data/b4.js (pages b4-paper1a.html et b4-paper2.html) à partir de l'export B.4.

Usage :
    python3 scripts/import_b4.py IB_Physics_B4_Thermodynamics_questions.json

L'export B.4 donne la liste des questions du sous-thème, mais ni les réponses des QCM, ni les markschemes,
ni l'introduction des questions Paper 2. Ils sont repris de data/paper1a.js et data/paper2.js (exports
généraux), seulement quand le texte de la question de l'export y est retrouvé : dans ces exports, un même
identifiant désigne parfois une autre question (ex. 19M.2.HL.TZ2.10 y est une question sur l'induction).

- QCM : énoncé et réponse de data/paper1a.js ; méthode de résolution de scripts/b4_content.py (METHODS),
  dont la réponse doit être la même.
- Paper 2 : quand l'introduction a été rédigée par W4ss Academy (scripts/b4_content.py, STEMS), la question
  est donnée en entier ; sinon seules les parties B.4 sont données, avec un avertissement.
- EXE.2.HL.TZ0.1 est reprise de data/b3.js, où elle est complète.
"""
import html as htmlmod
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b4_content import METHODS, STEMS  # noqa: E402
from build_data import compact, norm_text  # noqa: E402
from build_exam import load_js  # noqa: E402
from build_subtopic import display, merged_pieces, norm, sort_key  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE, TITLE = "B.4", "Thermodynamics"
ALIASES = {"23M.2.SL.TZ1.7": "23M.2.SL.TZ1.9", "23M.2.HL.TZ2.9": "23M.2.HL.TZ2.7"}   # même question, deux numéros
STEM_NOTE = ('<p class="w4ss-note">Introduction written by W4ss Academy from the data of the markscheme '
             '(the introduction is missing from the source).</p>')
MISSING = ('<p class="w4ss-note">The introduction of this question (data, diagram) is missing from the source: '
           'only the B.4 parts are shown.</p>')


def text(h):
    return norm_text(htmlmod.unescape(h or ""))


def chunk(h):
    t = text(h)
    return t[len(t) // 4: len(t) // 4 + 40] if len(t) > 50 else t


def strip_label(q):
    return compact(re.sub(r'<div class="qn_code_number">.*?</div>', "", q, count=1, flags=re.S))


def pieces(entry):
    """Parties d'une question de data/paper2.js : {clé: {q, ms, er}}."""
    if entry["parts"]:
        return OrderedDict((norm(p["label"]), dict(q=p["q"], ms=p["ms"], er=p["er"])) for p in entry["parts"])
    return merged_pieces({"Question": entry["q"], "Markscheme": entry["ms"], "Examiners report": entry["er"]})


def marks_of(h):
    return sum(int(m) for m in re.findall(r"\[(\d+)\]", re.sub(r"<[^>]+>", "", h)))


def main(path):
    export = json.load(open(path, encoding="utf-8"))
    p1 = {q["id"]: q for q in load_js(os.path.join(ROOT, "data", "paper1a.js"))}
    p2 = load_js(os.path.join(ROOT, "data", "paper2.js"))
    by_id = {q["id"]: q for q in p2}
    b3 = {q["id"]: q for q in load_js(os.path.join(ROOT, "data", "b3.js"))["p2"]}

    # ---------- QCM ----------
    p1a = []
    for q in (x for x in export["questions"] if x["type"] == "qcm"):
        src = p1[q["id"]]
        assert chunk(q["question_html"]) in text(src["q"]), f"{q['id']} : texte différent dans paper1a.js"
        answer, steps = METHODS[q["id"]]
        assert answer == src["answer"], f"{q['id']} : réponse {src['answer']} ≠ méthode {answer}"
        p1a.append(OrderedDict(id=q["id"], key=q["id"], tag=q["subtopic"], session=q["session"],
                               level=q["source_level"], tz=q["time_zone"], num=q["question_number"],
                               topics=["B"], subtopics=[CODE], answer=answer, q=compact(src["q"]), ms="", er="",
                               method="<ol>" + "".join(f"<li>{s}</li>" for s in steps) + "</ol>"))

    # ---------- Paper 2 : parties B.4 regroupées par question ----------
    groups = OrderedDict()
    for q in (x for x in export["questions"] if x["type"] != "qcm"):
        m = re.match(r"(\w+\.2\.\w+\.TZ\d)\.(\d+)(.*)$", q["id"])
        parent = ALIASES.get(f"{m.group(1)}.{m.group(2)}", f"{m.group(1)}.{m.group(2)}")
        groups.setdefault(parent, []).append((norm(m.group(3)), q))

    out = []
    for parent, items in groups.items():
        session, _, level, tz, num = parent.split(".")
        hits = sorted({k for k, _ in items}, key=sort_key)
        aliases = sorted(a for a, c in ALIASES.items() if c == parent)
        if parent in b3:                                     # question complète dans data/b3.js
            q = dict(b3[parent])
            q.update(hits=hits, aliases=aliases)
            out.append(OrderedDict(q))
            continue
        # toutes les parties connues pour cette session, ce paper, ce niveau et ce fuseau
        prefix = parent.rsplit(".", 1)[0]
        own = pieces(by_id[parent]) if parent in by_id else {}
        others = {}
        for e in p2:
            if e["id"].startswith(prefix + ".") and e["id"] != parent:
                for k, v in pieces(e).items():
                    others.setdefault(k, []).append(v)

        def find(key, q):
            for cand in ([own[key]] if key in own else []) + others.get(key, []):
                if chunk(q["question_html"]) in text(cand["q"]):
                    return cand
            return None

        found = {k: find(k, q) for k, q in items}
        if parent in STEMS:
            # question entière : toutes ses parties doivent être celles de l'export
            assert all(found[k] is own.get(k) for k in found), f"{parent} : parties non retrouvées dans la question"
            parts = [OrderedDict(label=display(k), key=k, subtopics=[CODE] if k in hits else [], pre="",
                                 q=strip_label(v["q"]), ms=compact(v.get("ms")), er=compact(v.get("er")))
                     for k, v in own.items()]
            parts[0]["pre"] = STEM_NOTE + STEMS[parent]["intro"]
            complete = True
        else:
            parts = []
            for k, q in sorted(items, key=lambda kv: sort_key(kv[0])):
                v = found[k] or {}
                parts.append(OrderedDict(
                    label=display(k), key=k, subtopics=[CODE], pre="",
                    q=compact(q["question_html"]) + f'<div class="qc_marks_available"><p>[{q["marks"]}]</p></div>',
                    ms=compact(v.get("ms")), er=compact(v.get("er"))))
                if not v:
                    print(f"  {q['id']} : pas de markscheme retrouvé")
            parts[0]["pre"] = MISSING
            complete = False
        out.append(OrderedDict(id=parent, session=session, level=level, tz=tz, num=num, hits=hits,
                               marks=sum(marks_of(p["q"]) for p in parts), parts=parts, aliases=aliases,
                               complete=complete))

    target = os.path.join(ROOT, "data", "b4.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("window.QB_SUB = ")
        json.dump(OrderedDict(code=CODE, title=TITLE, source=os.path.basename(path), p1a=p1a, p2=out),
                  f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"b4.js : {len(p1a)} QCM, {len(out)} questions Paper 2 ({sum(len(q['hits']) for q in out)} parties B.4)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
