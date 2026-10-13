# Questionbank (IB DP — Physics et Maths)

Site statique de révision. La page d'accueil (`index.html`) propose deux matières :

| Bouton | Page | Contenu |
|---|---|---|
| Physics | `physics.html` | DP Physics (première évaluation 2025) : Paper 1A (QCM) et Paper 2, classés par thème et sous-thème (A.1 → E.5, Tools, Inquiry) |
| Maths | `maths.html` | Maths AA SL, Topic 4 Statistics and probability : 89 exercices de Paper 1 et Paper 2 |

Les anciens liens vers la Questionbank de physique (`index.html#p1a?...`) redirigent automatiquement vers `physics.html`.

## Maths AA SL — Topic 4

- Onglets **Tous / Paper 1** (sans calculatrice) **/ Paper 2** (calculatrice)
- Filtres : Section A (questions courtes 1 à 6) ou B (questions longues 7 à 9), session, recherche (texte ou référence)
- Chaque exercice affiche ses textes de contexte au moment où une partie en a besoin. Chaque partie a son markscheme et, quand il existe, le rapport des examinateurs. Une case permet d'afficher tous les markschemes.
- Les questions de l'ancien programme Mathematics SL (préfixe `S_`) sont signalées par une étiquette « ancien programme ». Celles dont l'énoncé commun manque dans la source portent un avertissement.

Le fichier source ne précise pas le sous-thème (4.1, 4.2…) de chaque question : les exercices sont donc classés par paper, section et session, sans deviner de sous-thème. Pour mettre à jour les données :

```bash
python3 scripts/build_maths.py Maths_AA_SL_Topic_4_questions.json   # produit data/maths-t4.js
python3 scripts/stamp_versions.py
```

## Physics — fonctionnalités

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

## Méthodes de résolution des QCM

Pour B.3, chaque QCM a une méthode de résolution rédigée en français, qui s'affiche dans le markscheme sous la réponse, après que l'élève a répondu. Les méthodes se trouvent dans `data/methods/b3.json`, une entrée par QCM. Pour corriger ou ajouter une méthode, modifie ce fichier puis relance `import_subtopic_json.py` : le script vérifie que la référence et la réponse de chaque méthode correspondent au QCM.

## Sujets d'entraînement W4ss Academy (PDF)

Chaque sujet porte sur B.3 Gas laws et fait 20 points : 10 QCM (Paper 1A) et 10 points de questions longues (Paper 2). La mise en page suit celle des sujets de physique du DP. Chaque sujet a son corrigé : réponses et méthodes des QCM, markscheme du Paper 2.

| Sujet | Référence | Fichiers (`exams/`) |
|---|---|---|
| 1 | W4SS–PHY–B3–01 | `W4ss_Academy_Physics_B3_Test.pdf`, `W4ss_Academy_Physics_B3_Markscheme.pdf` |
| 2 | W4SS–PHY–B3–02 | `W4ss_Academy_Physics_B3_Test_2.pdf`, `W4ss_Academy_Physics_B3_Markscheme_2.pdf` |
| 3 | W4SS–PHY–B3–03 | `W4ss_Academy_Physics_B3_Test_3.pdf`, `W4ss_Academy_Physics_B3_Markscheme_3.pdf` |

Aucun QCM ni aucune partie de question longue ne sert dans deux sujets, et le script le vérifie. Avec le sujet 3, les QCM B.3 et les parties de Paper 2 B.3 dont l'énoncé est complet sont presque tous utilisés : il reste 2 QCM. Les questions retenues sont dans `PAPERS`, en haut de `scripts/build_exam.py`. Pour régénérer :

```bash
python3 scripts/build_exam.py B3_Gas_laws_questions.json        # tous les sujets (ou ajouter le numéro : 2)
node scripts/print_pdf.cjs exams/w4ss-b3-test-2.html exams/W4ss_Academy_Physics_B3_Test_2.pdf
node scripts/print_pdf.cjs exams/w4ss-b3-markscheme-2.html exams/W4ss_Academy_Physics_B3_Markscheme_2.pdf
```

## Paper 2 seul : questions dont l'introduction manquait

Les 5 questions longues B.3 dont le texte d'introduction manque dans la source sont complétées et rassemblées dans deux sujets « Paper 2 seul ». Chaque question garde toutes ses parties.

| Sujet | Référence | Questions | Points | Fichiers (`exams/`) |
|---|---|---|---|---|
| 1 (SL/HL) | W4SS–PHY–B3–P2–01 | EXE.2.SL.TZ0.10, EXE.2.SL.TZ0.8, 23M.2.SL.TZ2.2, 22N.2.SL.TZ0.2 | 30 | `W4ss_Academy_Physics_B3_Paper2.pdf` + `_Markscheme` |
| 2 (HL) | W4SS–PHY–B3–P2–02 | EXE.2.HL.TZ0.1 (centrale nucléaire : fission, radioactivité, cycle de Brayton, turbine) | 20 | `W4ss_Academy_Physics_B3_Paper2_2.pdf` + `_Markscheme` |

Les introductions, graphiques et tableaux sont écrits dans `scripts/written_stems.py`. Toutes leurs données viennent du markscheme officiel, pour que la correction reste valable, et les calculs de vérification sont en tête du fichier. Par exemple, le cycle de EXE.2.HL.TZ0.1 (1,0 mol d'hélium, 8,0/1,6 MPa) redonne exactement les travaux 8.23, 9.11, 4.32 et 3.25 kJ, 20.58 kJ reçus et un rendement de 0.47. Pour régénérer :

```bash
python3 scripts/build_p2_paper.py            # ou : python3 scripts/build_p2_paper.py 2
node scripts/print_pdf.cjs exams/w4ss-b3-paper2-2.html exams/W4ss_Academy_Physics_B3_Paper2_2.pdf
node scripts/print_pdf.cjs exams/w4ss-b3-paper2-2-markscheme.html exams/W4ss_Academy_Physics_B3_Paper2_2_Markscheme.pdf
```

## Après chaque modification

Lance `python3 scripts/stamp_versions.py`. Ce script ajoute à chaque fichier JS/CSS un numéro de version (`?v=...`) pour que les navigateurs rechargent les fichiers modifiés. Sans lui, un navigateur peut mélanger un ancien fichier en cache avec un nouveau, et la page ne s'affiche plus (par exemple, les QCM ne se chargent pas).
