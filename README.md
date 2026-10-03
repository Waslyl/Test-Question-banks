# Physics Questionbank (DP Physics 2025)

Site statique pour réviser les questions **Paper 1A** (QCM) et **Paper 2** du programme IB DP Physics (première évaluation 2025), classées par thème et sous-thème (A.1 → E.5, Tools, Inquiry).

## Fonctionnalités

- Onglets **Paper 1A** / **Paper 2**
- Classement par thème et sous-thème dans la barre latérale, avec le nombre de questions
- Filtres : niveau SL/HL, session, recherche plein texte, ordre aléatoire
- Paper 1A : on clique sur A/B/C/D pour répondre. La correction et le score sont mémorisés dans le navigateur
- Paper 2 : markscheme et rapport des examinateurs affichables question par question
- Lien partageable : l'URL garde le paper, le thème et les filtres (ex. `#p1a?t=A.3&l=SL`)

## Lancer le site

Le site n'utilise que du HTML, du CSS et du JS, sans dépendance. En local :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

Pour le mettre en ligne, n'importe quel hébergement statique fait l'affaire : GitHub Pages (Settings → Pages → branche), Netlify, etc.

## Mettre à jour les questions

Les données sont générées à partir des deux exports JSON (`merged` et `split`) :

```bash
python3 scripts/build_data.py chemin/Physics_2025_QB_merged.json chemin/Physics_2025_QB_split.json
```

Le script produit `data/paper1a.js` et `data/paper2.js`. Seules les questions des Papers 1A et 2 sont gardées : les Papers 1B et 3 sont exclus.

## Pages dédiées au sous-thème B.1

- `b1-paper1a.html` : les 44 questions Paper 1A de B.1
- `b1-paper2.html` : les questions Paper 2 de B.1, complètes, avec toutes leurs parties. Les parties B.1 sont mises en évidence et chaque partie a son propre markscheme.

Les données de `b1-paper2.html` se régénèrent à partir de la page B.1 de la Questionbank, enregistrée en HTML :

```bash
python3 scripts/build_b1_paper2.py merged.json split.json page_B1.html
```
