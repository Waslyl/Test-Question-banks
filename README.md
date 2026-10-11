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

## Pages par sous-thème

| Sous-thème | Paper 1A | Paper 2 |
|---|---|---|
| B.1 Thermal energy transfers | `b1-paper1a.html` (37 QCM vérifiés sur 44 listés) | `b1-paper2.html` (20 questions) |
| B.3 Gas laws | `b3-paper1a.html` (32 QCM) | `b3-paper2.html` (10 questions) |

Dans les pages Paper 2, chaque question est complète, avec toutes ses parties. Les parties du sous-thème sont mises en évidence et chaque partie a son propre markscheme.

Pour ajouter un sous-thème, enregistre sa page de la Questionbank en HTML (ou celle du thème entier), puis lance :

```bash
python3 scripts/build_subtopic.py merged.json split.json page.html B.3
```

Le script produit `data/b3.js`. Ensuite, copie `b3-paper1a.html` et `b3-paper2.html` en remplaçant `b3` et le titre.

**Attention aux identifiants.** Dans les exports généraux (merged et split), un même identifiant IB désigne parfois une autre question que celle du sous-thème. `build_subtopic.py` compare donc chaque question avec le début de texte affiché par la page HTML : il écarte les QCM qui ne correspondent pas, et quand une question Paper 2 en mélange deux, il ne garde que les parties vérifiées.

Quand un export dédié au sous-thème existe (ex. `B3_Gas_laws_questions.json`), c'est la meilleure source :

```bash
python3 scripts/import_subtopic_json.py B3_Gas_laws_questions.json merged.json split.json
```

Les QCM et la liste des parties viennent de l'export dédié. Les fichiers merged et split servent seulement à afficher les autres parties de chaque question et son texte de contexte, et seulement après vérification du texte de chaque partie.
