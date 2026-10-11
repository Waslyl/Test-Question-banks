#!/usr/bin/env python3
"""Ajoute à chaque fichier JS/CSS appelé par les pages un numéro de version (?v=...) tiré de son contenu.

Usage (après toute modification d'un fichier de assets/ ou data/) :
    python3 scripts/stamp_versions.py

Sans ce numéro, un navigateur peut garder en cache l'ancienne version d'un fichier et la mélanger
avec la nouvelle version d'un autre : la page plante (ex. les QCM ne se chargent plus).
"""
import glob
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def version(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def stamp(match):
    attr, path = match.group(1), match.group(2)
    if not os.path.exists(os.path.join(ROOT, path)):
        return match.group(0)
    return f'{attr}="{path}?v={version(path)}"'


def main():
    # les données chargées depuis le JS (onglets Paper 1A / Paper 2 du site principal), avant
    # les pages, puisque app.js change alors lui-même de version
    app = os.path.join(ROOT, "assets", "app.js")
    js = open(app, encoding="utf-8").read()
    new = re.sub(r'file: "((?:data)/[^"?]+\.js)(?:\?v=[0-9a-f]+)?"', lambda m: f'file: "{m.group(1)}?v={version(m.group(1))}"', js)
    if new != js:
        open(app, "w", encoding="utf-8").write(new)
        print("mis à jour : assets/app.js")
    for page in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        html = open(page, encoding="utf-8").read()
        new = re.sub(r'(src|href)="((?:assets|data)/[^"?]+\.(?:js|css))(?:\?v=[0-9a-f]+)?"', stamp, html)
        if new != html:
            open(page, "w", encoding="utf-8").write(new)
            print("mis à jour :", os.path.basename(page))


if __name__ == "__main__":
    main()
