#!/usr/bin/env python3
"""Convertit les deux exports JSON (merged + split) en fichiers de données pour le site.

Usage :
    python3 scripts/build_data.py chemin/Physics_2025_QB_merged.json chemin/Physics_2025_QB_split.json

Produit :
    data/paper1a.js  -> window.QB_P1A = [...]   (questions QCM, une entrée par question)
    data/paper2.js   -> window.QB_P2  = [...]   (questions longues, regroupées par question)
"""
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTRA_TOPICS = {"tools": "T", "inquiry": "I", "nature-of-science": "N"}


def topic_code(slug):
    m = re.match(r"^([a-e])-", slug)
    if m:
        return m.group(1).upper()
    return EXTRA_TOPICS.get(slug)


def subtopic_code(slug):
    m = re.match(r"^([a-e])-(\d)-", slug)
    if m:
        return f"{m.group(1).upper()}.{m.group(2)}"
    if slug.startswith("tool-"):
        return "T." + slug.split("-")[1]
    if slug.startswith("inquiry-"):
        return "I." + slug.split("-")[1]
    if slug.startswith("i-"):
        return "I." + slug.split("-")[1]
    return None


def compact(html):
    if not html:
        return ""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r">\s+<", "> <", html)
    return html.strip()


def parse_id(qid):
    parts = qid.split(".")
    session, paper, level, tz = parts[:4]
    rest = ".".join(parts[4:])
    m = re.match(r"(\d+)(.*)", rest)
    num = int(m.group(1)) if m else None
    sub = (m.group(2) if m else rest).strip(".")
    return dict(session=session, paper=paper, level=level, tz=tz, num=num, sub=sub,
                base=".".join(parts[:4]))


def marks_of(html):
    return sum(int(x) for x in re.findall(r"\[(\d+)\]", re.sub(r"<[^>]+>", "", html or "")))


def tags(rec):
    topics = sorted({c for c in (topic_code(t) for t in rec.get("topics") or []) if c})
    subs = sorted({c for c in (subtopic_code(s) for s in rec.get("subtopics") or []) if c})
    return topics, subs


def norm_text(html):
    s = re.sub(r"<!--.*?-->", "", str(html or ""), flags=re.S)
    s = re.sub(r"<img[^>]*>", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[\d+\]", "", s)
    return re.sub(r"\W", "", s)


def main(merged_path, split_path):
    merged = json.load(open(merged_path, encoding="utf-8"))
    split = json.load(open(split_path, encoding="utf-8"))

    # ---------- Paper 1A ----------
    p1a = []
    for r in split:
        info = parse_id(r["question_id"])
        if info["paper"] != "1A":
            continue
        ms_text = re.sub(r"<[^>]+>|\s", "", r.get("Markscheme") or "")
        answer = ms_text if ms_text in ("A", "B", "C", "D") else None
        topics, subs = tags(r)
        p1a.append(OrderedDict(
            id=r["question_id"], session=info["session"], level=info["level"], tz=info["tz"],
            num=info["num"], topics=topics, subtopics=subs, answer=answer,
            q=compact(r["Question"]),
            ms="" if answer else compact(r.get("Markscheme")),
            er=compact(r.get("Examiners report")),
        ))

    # ---------- Paper 2 ----------
    p2 = []
    merged_ids = set()
    merged_text = ""
    for r in merged:
        info = parse_id(r["question_id"])
        if info["paper"] != "2":
            continue
        merged_ids.add(r["question_id"])
        merged_text += norm_text(r["Question"]) + norm_text(r["Markscheme"])
        topics, subs = tags(r)
        p2.append(OrderedDict(
            id=r["question_id"], session=info["session"], level=info["level"], tz=info["tz"],
            num=info["num"], topics=topics, subtopics=subs, marks=marks_of(r["Question"]),
            q=compact(r["Question"]), ms=compact(r.get("Markscheme")),
            er=compact(r.get("Examiners report")), parts=None,
        ))

    # Parties issues du fichier "split" qui ne sont pas déjà couvertes par le fichier "merged"
    groups = OrderedDict()
    for r in split:
        info = parse_id(r["question_id"])
        if info["paper"] != "2":
            continue
        if info["num"] is not None:
            parent = f"{info['base']}.{info['num']}"
            if parent in merged_ids:
                continue
        else:
            t = norm_text(r["Question"])
            chunk = t[len(t) // 4: len(t) // 4 + 50] if len(t) > 60 else t
            if chunk and chunk in merged_text:
                continue
            parent = r["question_id"]
        groups.setdefault(parent, []).append((info, r))

    def part_key(item):
        return item[0]["sub"]

    for parent, items in groups.items():
        items.sort(key=part_key)
        info0 = parse_id(parent)
        topics, subs = set(), set()
        parts = []
        for info, r in items:
            t, s = tags(r)
            topics.update(t)
            subs.update(s)
            parts.append(OrderedDict(
                label=info["sub"] or "", q=compact(r["Question"]), ms=compact(r.get("Markscheme")),
                er=compact(r.get("Examiners report")), subtopics=s,
            ))
        p2.append(OrderedDict(
            id=parent, session=info0["session"], level=info0["level"], tz=info0["tz"],
            num=info0["num"], topics=sorted(topics), subtopics=sorted(subs),
            marks=sum(marks_of(p["q"]) for p in parts), q="", ms="", er="", parts=parts,
        ))

    def sort_key(q):
        return (q["session"], q["tz"], q["level"], q["num"] if q["num"] is not None else 999, q["id"])

    p1a.sort(key=sort_key)
    p2.sort(key=sort_key)

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    for name, var, data in (("paper1a.js", "QB_P1A", p1a), ("paper2.js", "QB_P2", p2)):
        path = os.path.join(ROOT, "data", name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"window.{var} = ")
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write(";\n")
        print(f"{name}: {len(data)} questions, {os.path.getsize(path) / 1e6:.1f} Mo")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
