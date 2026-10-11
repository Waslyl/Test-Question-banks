#!/usr/bin/env python3
"""Construit data/<sous-thème>.js à partir d'un export dédié à un sous-thème (ex. B3_Gas_laws_questions.json).

Usage :
    python3 scripts/import_subtopic_json.py export.json merged.json split.json

L'export dédié fait foi : il a été extrait directement de la liste du sous-thème, alors que les
exports généraux (merged, split) rangent parfois deux questions différentes sous le même
identifiant IB (ex. 19M.1A.SL.TZ2.12). Les fichiers merged et split servent seulement à
compléter une question Paper 2 avec ses autres parties et son texte de contexte, et
seulement si le texte de chaque partie de l'export y est retrouvé.
"""
import html as htmlmod
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import compact, norm_text, parse_id  # noqa: E402
from build_subtopic import build_parts, display, norm, sort_key  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def options_html(q):
    """Les propositions A–D, comme sur la Questionbank : image, tableau ou liste."""
    if q.get("options_image"):
        return f'<p><img src="{q["options_image"]}" alt="Propositions A à D"/></p>'
    if q.get("option_columns"):
        head = "".join(f"<th>{htmlmod.escape(c)}</th>" for c in q["option_columns"])
        rows = "".join(
            f"<tr><td>{o['label']}.</td>" + "".join(f"<td>{htmlmod.escape(v)}</td>" for v in o.get("values", [])) + "</tr>"
            for o in q["options"])
        return f"<table><tr><th></th>{head}</tr>{rows}</table>"
    return "".join(f"<p>{o['label']}. {o.get('html') or htmlmod.escape(o['text'])}</p>" for o in q["options"])


def import_qcm(qcm):
    out, seen = [], Counter(q["reference"] for q in qcm)
    count = Counter()
    for q in qcm:
        ref = q["reference"]
        count[ref] += 1
        tags = []
        if seen[ref] > 1:
            tags.append(f"variante {count[ref]}")
        if len(q["levels"]) > 1:
            tags.append(" + ".join(sorted(q["levels"], reverse=True)))
        ms = q["markscheme"]["html"]
        comment = "" if re.sub(r"<[^>]+>|\s", "", ms) == q["correct_option"] else compact(ms)
        out.append(OrderedDict(
            id=ref, key=q["id"], tag=", ".join(tags), session=q["session"],
            level="SL" if "SL" in q["levels"] else q["levels"][0], tz=q["time_zone"],
            num=q["question_number"], topics=[], subtopics=[], answer=q["correct_option"],
            q=compact(q["statement"]["html"] + options_html(q)) + '<div class="qc_marks_available"><p>[1]</p></div>',
            ms="", er=comment,
        ))
    return out


def add_methods(p1a, code):
    """Ajoute la méthode de résolution rédigée pour chaque QCM (data/methods/<sous-thème>.json)."""
    path = os.path.join(ROOT, "data", "methods", code.lower().replace(".", "") + ".json")
    if not os.path.exists(path):
        return
    methods = json.load(open(path, encoding="utf-8"))
    for q in p1a:
        m = methods.get(q["key"])
        if not m:
            print(f"  pas de méthode pour {q['id']} ({q['key']})")
            continue
        if m["ref"] != q["id"] or m["answer"] != q["answer"]:
            sys.exit(f"Méthode incohérente pour {q['key']} : {m['ref']}/{m['answer']} au lieu de {q['id']}/{q['answer']}")
        q["method"] = "<ol>" + "".join(f"<li>{step}</li>" for step in m["steps"]) + "</ol>"
    unused = set(methods) - {"_info"} - {q["key"] for q in p1a}
    if unused:
        print(f"  méthodes sans QCM correspondant : {sorted(unused)}")


def import_exercise(ex, code, merged, split):
    hits = [norm(p["label"]) for p in ex["parts"]]
    full = build_parts(ex["reference"], merged, split) if merged else []
    by_key = {p["key"]: p for p in full}

    def text(h):
        return norm_text(htmlmod.unescape(h))   # les &nbsp; ne doivent pas compter

    def found(p):
        part = by_key.get(norm(p["label"]))
        t = text(p["statement"]["html"])
        chunk = t[len(t) // 4: len(t) // 4 + 40] if len(t) > 50 else t
        return part is not None and chunk in text(part["q"])

    if full and all(found(p) for p in ex["parts"]):
        parts, complete = full, True
    else:
        # question absente ou différente dans les exports généraux : on garde les seules parties de l'export
        context = "".join(compact(c["html"]) for c in ex["contexts"])
        parts, complete = [], False
        for i, p in enumerate(ex["parts"]):
            k = norm(p["label"])
            parts.append(OrderedDict(
                label=display(k), key=k, subtopics=[code], pre=context if i == 0 else "",
                q=compact(p["statement"]["html"]) + f'<div class="qc_marks_available"><p>[{p["marks"]}]</p></div>',
                ms=compact(p["markscheme"]["html"]), er=""))
    info = parse_id(ex["reference"])
    marks = sum(int(m) for p in parts for m in re.findall(r"\[(\d+)\]", re.sub(r"<[^>]+>", "", p["q"])))
    level = "SL" if "SL" in ex["levels"] else ex["levels"][0]
    return OrderedDict(id=ex["reference"], session=ex["session"], level=level, tz=ex["time_zone"],
                       num=info["num"], hits=sorted(hits, key=sort_key), marks=marks, parts=parts,
                       aliases=[], complete=complete)


def main(export_path, merged_path, split_path):
    data = json.load(open(export_path, encoding="utf-8"))
    merged = {r["question_id"]: r for r in json.load(open(merged_path, encoding="utf-8"))}
    split = json.load(open(split_path, encoding="utf-8"))
    code, title = data["syllabus_section"]["code"], data["syllabus_section"]["title"]

    p1a = import_qcm(data["qcm"])
    add_methods(p1a, code)
    p2 = [import_exercise(ex, code, merged, split) for ex in data["structured_questions"]]
    for q in p2:
        if not q["complete"]:
            print(f"  {q['id']} : question non retrouvée dans merged/split, parties {code} seules")

    slug = code.lower().replace(".", "")
    path = os.path.join(ROOT, "data", slug + ".js")
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.QB_SUB = ")
        json.dump(OrderedDict(code=code, title=title, source=os.path.basename(export_path),
                              p1a=p1a, p2=p2), f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"{slug}.js : {code} {title} — {len(p1a)} QCM, {len(p2)} questions Paper 2 "
          f"({sum(len(q['hits']) for q in p2)} parties {code}, {sum(len(q['parts']) for q in p2)} parties en tout)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
