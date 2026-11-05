# Questionbank (IB DP — Physics et Maths)

Site statique de révision. La page d'accueil (`index.html`) propose deux matières :

| Bouton | Page | Contenu |
|---|---|---|
| Physics | `physics.html` | DP Physics (première évaluation 2025) : Paper 1A (QCM) et Paper 2, classés par thème et sous-thème (A.1 → E.5, Tools, Inquiry) |
| Maths | `maths.html` | Maths AA SL, Topic 2 Functions (16 questions, 2.1 à 2.5) et Topic 4 Statistics and probability (89 exercices) : Paper 1 et Paper 2 |

Les anciens liens vers la Questionbank de physique (`index.html#p1a?...`) redirigent automatiquement vers `physics.html`.

## Maths AA SL — Topics 2 et 4

- Filtre par topic : **Tous les topics / Topic 2 Functions / Topic 4 Statistics and probability**. Pour le topic 2, un menu permet aussi de choisir un sous-thème (2.1 à 2.5). Chaque carte porte son topic et, pour le topic 2, ses sous-thèmes.
- Onglets **Tous / Paper 1** (sans calculatrice) **/ Paper 2** (calculatrice)
- Filtres : Section A (questions courtes 1 à 6) ou B (questions longues 7 à 9), session, recherche (texte ou référence)
- Chaque exercice affiche ses textes de contexte au moment où une partie en a besoin. Chaque partie a son markscheme et, quand il existe, le rapport des examinateurs. Une case permet d'afficher tous les markschemes.
- Les questions de l'ancien programme Mathematics SL (préfixe `S_`) sont signalées par une étiquette « ancien programme ». Celles dont l'énoncé commun manque dans la source portent un avertissement.

Le fichier du topic 4 ne précise pas le sous-thème (4.1, 4.2…) de chaque question : ses exercices sont classés par paper, section et session, sans deviner de sous-thème. Pour mettre à jour les données du topic 4 :

```bash
python3 scripts/build_maths.py Maths_AA_SL_Topic_4_questions.json   # produit data/maths-t4.js
python3 scripts/stamp_versions.py
```

Le script réécrit aussi le MathML de la source que Chrome n'affiche plus : `<mfenced>` (les parenthèses de P(A ∩ B) disparaissaient) et `<menclose>` (la barre de P(A | B)). Il recolle les nombres décimaux coupés en morceaux (« 0 . 25 » → « 0.25 »), remet à la bonne taille le prime de A′ et supprime l'espace après un moins unaire (« (−2, −2) »).

### Sujets W4ss Academy de 30 minutes sur 4.1 à 4.6 (PDF)

Sujets au format des papers de Maths AA SL : couverture, section A (questions courtes ; le cadre de réponse suit chaque question et continue sur la page suivante si besoin), section B (question longue, à rédiger sur les pages lignées à la fin du sujet) et page des sources. Les sujets du jeu 2 n'ont pas de section B. Chaque sujet a son markscheme, et aucune question ne sert dans deux sujets.

| Sujet | Référence | Questions | Points | Fichiers (`exams/`) |
|---|---|---|---|---|
| Jeu 1, Paper 1 (sans calculatrice) | W4SS–MAA–T4–P1–01 | 19N.1.SL.TZ0.S_2 (4.6 diagramme de Venn), 21N.1.SL.TZ0.4 (4.5, 4.6 arbre, indépendance), 21M.1.SL.TZ2.7 (4.2 fréquences cumulées, 4.3 médiane, 4.1 échantillonnage) | 25 | `W4ss_Academy_Maths_AA_T4_Paper1.pdf` + `_Markscheme` |
| Jeu 1, Paper 2 (calculatrice) | W4SS–MAA–T4–P2–01 | EXN.2.SL.TZ0.1 (4.3 moyenne), 22M.2.SL.TZ1.2 (4.3 médiane, écart type), 21M.2.SL.TZ2.4 (4.6 probabilités, indépendance), EXM.2.SL.TZ0.1 (a) à (d) (4.1 échantillonnage, 4.4 corrélation) | 27 | `W4ss_Academy_Maths_AA_T4_Paper2.pdf` + `_Markscheme` |
| Jeu 2, Paper 1, section A seule | W4SS–MAA–T4–P1–02 | 19M.1.SL.TZ1.S_1 (4.6 diagramme de Venn), 21M.1.SL.TZ1.4 (4.2 boîte à moustaches, valeurs aberrantes), 22N.1.SL.TZ0.6 (4.6 événements indépendants), EXM.1.SL.TZ0.2 (4.2, 4.3 quartiles, valeurs aberrantes) | 26 | `W4ss_Academy_Maths_AA_T4_Paper1_2.pdf` + `_Markscheme` |
| Jeu 2, Paper 2, section A seule | W4SS–MAA–T4–P2–02 | 19M.2.SL.TZ1.S_1 (4.3 moyenne, 4.2 boîte à moustaches), 22M.2.SL.TZ2.5 (4.2, 4.3 boîtes à moustaches, valeurs aberrantes), 22N.2.SL.TZ0.1 (4.4 régression, r), 22M.2.SL.TZ1.6 (a) (4.6 indépendance), 22M.2.SL.TZ2.4 (4.6 indépendance) | 26 | `W4ss_Academy_Maths_AA_T4_Paper2_2.pdf` + `_Markscheme` |

La durée suit le rythme des vrais sujets (90 minutes pour 80 points). Deux parties sont écartées parce qu'elles sortent de 4.1 à 4.6 : la partie (e) de EXM.2.SL.TZ0.1 demande la droite de régression de t en s, c'est-à-dire de x en y (4.10), et la partie (b) de 22M.2.SL.TZ1.6 demande P(A′ | B′) avec la définition formelle de l'indépendance (4.11). Les questions retenues et leurs sous-thèmes sont dans `PAPERS`, en haut de `scripts/build_maths_exam.py`. Pour régénérer :

```bash
python3 scripts/build_maths_exam.py            # ou un seul sujet : p1, p2, p1-2, p2-2
node scripts/print_pdf.cjs exams/w4ss-maa-t4-p2.html exams/W4ss_Academy_Maths_AA_T4_Paper2.pdf
node scripts/print_pdf.cjs exams/w4ss-maa-t4-p2-markscheme.html exams/W4ss_Academy_Maths_AA_T4_Paper2_Markscheme.pdf
```

### Topic 2 Functions, 2.1 à 2.5 : sujets W4ss Academy (PDF)

L'export `IB_Maths_SL_2_1_to_2_5_questions.json` contient 16 questions classées en 2.1 à 2.5, sans markscheme. Il est converti dans le même format que le topic 4, et `maths.html` charge les deux fichiers. Sur le site, les parties qui ont un corrigé W4ss affichent un bouton « Corrigé W4ss » à la place de « Markscheme ». L'export ne donne ni la section ni la date : la section vient du barème (B à partir de 12 points), la date de la référence.

```bash
python3 scripts/build_maths_t2.py IB_Maths_SL_2_1_to_2_5_questions.json   # produit data/maths-t2.js
```

Deux sujets de 30 minutes, section A seule :

| Sujet | Référence | Questions | Points | Fichiers (`exams/`) |
|---|---|---|---|---|
| Paper 1 (sans calculatrice) | W4SS–MAA–T2–P1–01 | 22M.1.SL.TZ2.1 (2.5 composées, tableau), 22M.1.SL.TZ1.1 (2.1 droites perpendiculaires), 17M.1.SL.TZ1.T_12 (2.2, 2.4 lecture graphique), SPM.1.SL.TZ0.5 (2.5 composée et réciproque), 17M.1.AHL.TZ2.H_2 (2.2, 2.5 ensemble image, réciproque) | 25 | `W4ss_Academy_Maths_AA_T2_Paper1.pdf` + `_Markscheme` |
| Paper 2 (calculatrice) | W4SS–MAA–T2–P2–01 | 21N.2.SL.TZ0.2 (2.3 tracé, 2.4 zéros), 20N.1.SL.TZ0.T_4 (2.4 zéro, minimum, intersection), 21M.2.SL.TZ2.5 (2.2 ensemble image, 2.5 composée), 17M.2.SL.TZ2.S_6 (2.5 composée, 2.3 tracé, 2.4 nombre de solutions) | 25 | `W4ss_Academy_Maths_AA_T2_Paper2.pdf` + `_Markscheme` |

- **Corrigés.** L'export n'en a pas : ils sont rédigés par W4ss Academy dans `scripts/maths_t2_solutions.py`, au format des markschemes de l'IB, avec en commentaire les calculs de vérification. La couverture du markscheme le signale.
- **Figures.** Quand l'export ne donne qu'un lien vers une image, elle n'est pas téléchargée : la figure est redessinée à partir des données de l'énoncé (`FIGURES`, avec le module `scripts/maths_figures.py`), et la page des sources le précise. Par exemple, le graphe de 17M.1.SL.TZ1.T_12 est celui de f(x) = x + 2 + 4/x, la seule fonction de la forme ax + b + c/x qui a un maximum local en (−2, −2) et un minimum local en (2, 6).
- **Anciens programmes.** 17M.1.SL.TZ1.T_12 n'a dans la source que les parties (b) et (c) : elles sont renumérotées (a) et (b). 20N.1.SL.TZ0.T_4 vient d'un Paper 1 de Mathematical studies, où la calculatrice était permise : elle est placée dans le Paper 2.

```bash
python3 scripts/build_maths_exam.py t2-p1 t2-p2
node scripts/print_pdf.cjs exams/w4ss-maa-t2-p1.html exams/W4ss_Academy_Maths_AA_T2_Paper1.pdf
```

### Test de la classe (QuestionBank Test)

Le test exporté de la Questionbank (`QuestionBank_Test.pdf` et son corrigé) est mis en page comme les autres sujets : 3 questions courtes en section A, une question longue en section B, 24 points, Paper 1. Référence W4SS–MAA–QB–P1–01, fichiers `exams/W4ss_Academy_Maths_QuestionBank_Test.pdf` et `_Markscheme.pdf`.

```bash
python3 scripts/build_qbtest.py QuestionBank_Test.pdf     # produit data/maths-qbtest.js
python3 scripts/build_maths_exam.py qb-p1
node scripts/print_pdf.cjs exams/w4ss-maa-qbtest.html exams/W4ss_Academy_Maths_QuestionBank_Test.pdf
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
