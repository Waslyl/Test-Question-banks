#!/usr/bin/env python3
"""Construit data/b1-paper2.js : les questions Paper 2 du sous-thème B.1, avec toutes leurs parties.

Usage :
    python3 scripts/build_b1_paper2.py merged.json split.json page_B1.html

- La liste des questions et des parties B.1 vient de la page HTML du sous-thème B.1.
- Le contenu vient des exports JSON, fusionnés partie par partie : le fichier split garde la
  numérotation complète (ex. 2AI -> a(i)) et le markscheme de chaque partie ; le fichier merged
  apporte, pour les anciens sujets, le texte de contexte placé avant certaines parties. Aucune des
  deux sources n'est complète seule.
"""
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import compact, marks_of, norm_text, parse_id, subtopic_code  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6}


def norm(label):
    """'a.i.' / 'a(i)' / 'AI' / 'A.I' -> 'ai'"""
    return re.sub(r"[^a-z]", "", label.lower())


def split_label(key):
    """'ai' -> ('a', 'i') ; 'cii' -> ('c', 'ii') ; '' -> ('', '')"""
    if not key:
        return "", ""
    return key[0], key[1:]


def display(key):
    letter, roman = split_label(key)
    if not letter:
        return ""
    return f"({letter})" + (f"({roman})" if roman else "")


def sort_key(key):
    letter, roman = split_label(key)
    return (letter, ROMAN.get(roman, 0))


def top_blocks(html):
    """Découpe un fragment HTML en blocs <div> de premier niveau : [(classe, html), ...]"""
    blocks, depth, start, cls = [], 0, None, None
    for m in re.finditer(r"<div\b[^>]*>|</div>", html):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append((cls, html[start:m.end()]))
                start = None
        else:
            if depth == 0:
                start = m.start()
                c = re.search(r'class="([^"]*)"', m.group(0))
                cls = c.group(1) if c else ""
            depth += 1
    return blocks


def label_in(block):
    m = re.search(r'question_part_label">([^<]*)<', block) or \
        re.search(r'qn_code_number">\s*\(?(.*?)\)?\s*</div>', block, re.S)
    return norm(m.group(1)) if m else None


def merged_pieces(rec):
    """Parties d'une question du fichier merged (anciens sujets), avec le texte de contexte qui les précède."""
    parts, pre = OrderedDict(), ""
    for cls, block in top_blocks(rec["Question"]):
        if "specification" in cls:
            pre += block
            continue
        key = label_in(block)
        if key is None:
            pre += block
            continue
        parts.setdefault(key, {"pre": compact(pre), "q": compact(block)})
        pre = ""
    for field, name in (("Markscheme", "ms"), ("Examiners report", "er")):
        html = re.sub(r"<br\s*/?>", "", rec.get(field) or "")
        key = None
        for cls, block in top_blocks(html):
            k = label_in(block)
            if "qn_code_number" in cls:      # format « (a.i) » : libellé puis bloc card-body
                key = k
                continue
            if k is None:
                k = key
            if k in parts:
                parts[k][name] = parts[k].get(name, "") + compact(block)
    return parts


def split_pieces(split, parent):
    """Parties d'une question du fichier split, indexées par libellé normalisé (ex. 'aii')."""
    pieces = [r for r in split if re.fullmatch(re.escape(parent) + r"[A-Z.()]*", r["question_id"])]
    parts = OrderedDict()
    # les parties avec suffixe d'abord ; l'entrée sans suffixe sert seulement si sa partie manque
    for r in sorted(pieces, key=lambda r: r["question_id"] == parent):
        key = norm(r["question_id"][len(parent):])
        if r["question_id"] == parent:
            m = re.search(r'qn_code_number">\s*\(([^)]*)\)', r["Question"])
            key = norm(m.group(1)) if m else ""
        if key in parts:
            continue
        q = re.sub(r'<div class="qn_code_number">.*?</div>', "", r["Question"], count=1, flags=re.S)
        parts[key] = {
            "subtopics": sorted({c for c in (subtopic_code(s) for s in r.get("subtopics") or []) if c}),
            "q": compact(q), "ms": compact(r.get("Markscheme")), "er": compact(r.get("Examiners report")),
        }
    return parts


def chunk(html):
    t = norm_text(html)
    return t[len(t) // 4: len(t) // 4 + 40] if len(t) > 50 else t


def find_merged(merged, parent, split_parts):
    """Version merged de la question, vérifiée par son contenu.

    Le fichier merged range parfois une question sous un autre identifiant (ex. la question
    21N.2.SL.TZ0.5 y figure sous 21N.2.HL.TZ0.5, alors que 21N.2.SL.TZ0.5 contient une autre
    question). On garde donc la version dont le texte contient les parties du fichier split.
    """
    info = parse_id(parent)
    candidates = [merged[parent]] if parent in merged else []
    candidates += [r for qid, r in merged.items() if qid != parent
                   and qid.split(".")[0] == info["session"] and qid.split(".")[1] == "2"
                   and qid.split(".")[3] == info["tz"]]
    chunks = [chunk(p["q"]) for p in split_parts.values() if chunk(p["q"])]
    if not chunks:
        return candidates[0] if candidates else None
    for r in candidates:
        text = norm_text(r["Question"])
        if any(c in text for c in chunks):
            return r
    return None


def main(merged_path, split_path, html_path):
    merged = {r["question_id"]: r for r in json.load(open(merged_path, encoding="utf-8"))}
    split = json.load(open(split_path, encoding="utf-8"))
    html = open(html_path, encoding="utf-8", errors="ignore").read()

    # Questions et parties listées dans la page B.1 (identifiants numérotés uniquement)
    wanted = OrderedDict()
    for qid in re.findall(r"<li>\s*((?:\d\d[MN]|SPM|EXE)\.2\.(?:SL|HL)\.TZ\d\.\d+[\w().]*):", html):
        m = re.match(r"(.*\.TZ\d\.)(\d+)(.*)", qid)
        parent = m.group(1) + m.group(2)
        wanted.setdefault(parent, set()).add(norm(m.group(3)))

    out = []
    for parent, b1_parts in wanted.items():
        info = parse_id(parent)
        new_format = info["session"] in ("23M", "SPM", "EXE")
        split_parts = split_pieces(split, parent)
        source = None if new_format else find_merged(merged, parent, split_parts)
        merged_parts = merged_pieces(source) if source else {}
        if merged_parts:
            # le fichier merged fait foi pour les lettres qu'il contient ; le split ne complète
            # que les parties absentes (ex. 21N.2.SL.TZ0.5 : (c) et (d) manquent dans merged)
            letters = {k[:1] for k in merged_parts}
            split_parts = {k: v for k, v in split_parts.items() if k[:1] not in letters}

        parts, seen = [], {}
        keys = sorted(set(split_parts) | set(merged_parts), key=sort_key)
        # une même partie peut figurer deux fois sous deux libellés (ex. « c » et « c(i) ») :
        # on garde le libellé le plus précis
        for key in sorted(keys, key=len, reverse=True):
            text = norm_text((merged_parts.get(key) or split_parts.get(key))["q"])
            seen.setdefault(text, key)
        keys = [k for k in keys if seen[norm_text((merged_parts.get(k) or split_parts.get(k))["q"])] == k]
        for key in keys:
            sp, mp = split_parts.get(key, {}), merged_parts.get(key, {})
            parts.append(OrderedDict(
                label=display(key), key=key, subtopics=sp.get("subtopics", []),
                pre=mp.get("pre", ""), q=mp.get("q") or sp.get("q", ""),
                ms=sp.get("ms") or mp.get("ms", ""), er=sp.get("er") or mp.get("er", ""),
            ))
        out.append(OrderedDict(id=parent, session=info["session"], level=info["level"], tz=info["tz"],
                               num=info["num"], b1=sorted(b1_parts, key=sort_key),
                               marks=sum(marks_of(p["q"]) for p in parts), parts=parts))

    # même question listée sous deux numéros dans le même sujet (ex. 23M.2.SL.TZ2.12 et .17) :
    # on n'en garde qu'une, en indiquant l'autre numéro
    out.sort(key=lambda q: (q["session"], q["tz"], q["level"], q["num"]))
    kept, by_text = [], {}
    for q in out:
        key = (q["session"], q["level"], q["tz"], "".join(norm_text(p["q"]) for p in q["parts"]))
        if key in by_text:
            first = by_text[key]
            first["aliases"].append(q["id"])
            first["b1"] = sorted(set(first["b1"]) | set(q["b1"]), key=sort_key)
            continue
        q["aliases"] = []
        by_text[key] = q
        kept.append(q)
    out = kept
    path = os.path.join(ROOT, "data", "b1-paper2.js")
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.QB_B1_P2 = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"b1-paper2.js : {len(out)} questions, {sum(len(q['parts']) for q in out)} parties")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
