#!/usr/bin/env python3
"""Convertit le test « QuestionBank Test » (PDF exporté depuis la Questionbank, 8 questions de statistiques)
en data/maths-qbtest.js, pour en faire un sujet W4ss avec build_maths_exam.py (sujet qb-p1).

Usage :
    python3 scripts/build_qbtest.py QuestionBank_Test.pdf      # test 1 (16 images) -> data/maths-qbtest.js
    python3 scripts/build_qbtest.py QuestionBank_Test_2.pdf    # test 2 (7 images)  -> data/maths-qbtest2.js

Le test 2 reprend deux questions du test 1 (17M.1.SL.TZ2.T_6 et 21N.1.SL.TZ0.9) : elles sont copiées de
data/maths-qbtest.js, qu'il faut donc avoir produit avant.

    python3 scripts/build_qbtest.py --test3 courbe.png grille.png corrige.png   # test 3 -> data/maths-qbtest3.js

Le test 3 a été envoyé en captures d'écran de téléphone : seules les images de 16N.1.SL.TZ0.T_2 (courbe des
fréquences cumulées, grille vierge, boîte à moustaches du corrigé) sont recadrées dans ces captures et
passées en argument ; ses trois autres questions sont reprises des tests 1 et 2.

Le texte des énoncés et des corrigés est recopié du PDF et de son corrigé (QuestionBank_Test_answers.pdf) ;
les images (boîtes à moustaches, tableau) sont extraites du PDF avec pdfimages. La question 20N.1.SL.TZ0.S_8
existe déjà dans data/maths-t4.js : elle en est reprise telle quelle, avec son markscheme.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_exam import load_js  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(text, mark=""):
    return f"<p>{text}" + (f"&nbsp;&nbsp;&nbsp;&nbsp;<em><strong>{mark}</strong></em>" if mark else "") + "</p>"


def note(text):
    return f"<p><strong>Note:</strong> {text}</p>"


def part(label, marks, ctx, q, ms):
    return OrderedDict(label=label, type="question", marks=marks, ctx=ctx, q=q, ms=ms, er="")


def exercise(qid, session, date, tz, legacy, contexts, parts):
    return OrderedDict(id=qid, section="A", paper=1, session=session, date=date, tz=tz, legacy=legacy,
                       marks=sum(x["marks"] for x in parts), contexts=contexts, parts=parts, notes=[])


def images(pdf):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdfimages", "-png", pdf, os.path.join(tmp, "img")], check=True)
        names = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
        return [f'<p><img src="data:image/png;base64,{base64.b64encode(open(os.path.join(tmp, n), "rb").read()).decode()}"></p>'
                for n in names]


def write(name, var, exercises):
    out = OrderedDict(subject="DP Mathematics: Analysis and Approaches", level="SL",
                      topic=OrderedDict(number=4, title="Statistics and probability"), exercises=exercises)
    target = os.path.join(ROOT, "data", name)
    with open(target, "w", encoding="utf-8") as f:
        f.write(f"window.{var} = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"data/{name} : {len(exercises)} questions, {sum(e['marks'] for e in exercises)} points")


def test2(img):
    """Test 2 : 17M.1.SL.TZ2.T_6, 17M.1.SL.TZ2.S_8 (a)(ii) et (b)(i), 21N.1.SL.TZ0.9, EXN.1.SL.TZ0.4."""
    test1 = {e["id"]: e for e in load_js(os.path.join(ROOT, "data", "maths-qbtest.js"))["exercises"]}
    exercises = [
        test1["17M.1.SL.TZ2.T_6"],
        exercise("17M.1.SL.TZ2.S_8", "17M", "May 2017", "TZ2", "S_", [
            OrderedDict(id="c1", html="<p>A city hired 160 employees to work at a festival. The following cumulative "
                                      "frequency curve shows the number of hours employees worked during the festival."
                                      "</p>" + img[1] + "<p>The city paid each of the employees £8 per hour for the "
                                      "first 40 hours worked, and £10 per hour for each hour they worked after the first "
                                      "40 hours.</p>")], [
            part("a.ii", 1, ["c1"], "<p>Write down the number of employees who worked 50 hours or less.</p>",
                 p("130 employees", "A1 N1")),
            part("b.i", 1, ["c1"], "<p>Find the amount of money an employee earned for working 40 hours.</p>",
                 p("£320", "A1 N1"))]),
        exercise("EXN.1.SL.TZ0.4", "EXN", "November Example questions", "TZ0", "", [
            OrderedDict(id="c1", html="<p>A food scientist measures the weights of 760 potatoes taken from a single field "
                                      "and the distribution of the weights is shown by the cumulative frequency curve "
                                      "below.</p>" + img[4]),
            OrderedDict(id="c2", html="<p>The weight of the smallest potato in the sample is 20 grams and the weight of "
                                      "the largest is 400 grams.</p>")], [
            part("a", 2, ["c1"], "<p>Find the number of potatoes in the sample with a weight of more than 200 grams.</p>",
                 p("760 − 420 = 340 (g)", "(M1)A1")),
            part("b.i", 1, ["c1"], "<p>Find the median weight.</p>", p("Median = 190 (g)", "A1")),
            part("b.ii", 1, ["c1"], "<p>Find the lower quartile.</p>", p("Lower quartile = 135 − 140 (g)", "A1")),
            part("b.iii", 1, ["c1"], "<p>Find the upper quartile.</p>", p("Upper quartile = 242 − 247 (g)", "A1")),
            part("c", 2, ["c1", "c2"], "<p>Use the scale shown below to draw a box and whisker diagram showing the "
                                       "distribution of the weights of the potatoes. You may assume there are no "
                                       "outliers.</p>" + img[5],
                 img[6] + p("", "M1A1") + note("The M1 is for a box and whisker plot and the A1 for all 5 statistics "
                                               "in the right places."))]),
        test1["21N.1.SL.TZ0.9"],
    ]
    write("maths-qbtest2.js", "QB_MATHS_QBTEST2", exercises)


def png(path):
    return f'<p><img src="data:image/png;base64,{base64.b64encode(open(path, "rb").read()).decode()}"></p>'


def test3(curve, grid, answer):
    """Test 3 : 17N.1.SL.TZ0.T_1, 16N.1.SL.TZ0.T_2, 17M.1.SL.TZ2.S_8, EXN.1.SL.TZ0.4."""
    test1 = {e["id"]: e for e in load_js(os.path.join(ROOT, "data", "maths-qbtest.js"))["exercises"]}
    test2 = {e["id"]: e for e in load_js(os.path.join(ROOT, "data", "maths-qbtest2.js"))["exercises"]}
    exercises = [
        test1["17N.1.SL.TZ0.T_1"],
        exercise("16N.1.SL.TZ0.T_2", "16N", "November 2016", "TZ0", "T_", [
            OrderedDict(id="c1", html="<p>A sample of 120 oranges was tested for Vitamin C content. The cumulative "
                                      "frequency curve below represents the Vitamin C content, in milligrams, of these "
                                      "oranges.</p>" + png(curve) + "<p>The minimum level of Vitamin C content of an "
                                      "orange in the sample was 30.1 milligrams. The maximum level of Vitamin C content "
                                      "of an orange in the sample was 35.0 milligrams.</p>")], [
            part("", 3, ["c1"], "<p>Draw a box-and-whisker diagram on the grid below to represent the Vitamin C "
                                "content, in milligrams, for this sample.</p>" + png(grid),
                 png(answer) + p("", "(A1)(ft)(A1)(ft)(A1)")
                 + note("Award (A1)(ft) for correct median, (A1)(ft) for correct quartiles and box, (A1) for correct "
                        "end points of whiskers and straight whiskers. Award at most (A1)(A1)(A0) if a horizontal line "
                        "goes right through the box or if the whiskers are not well aligned with the midpoint of the "
                        "box. Follow through from part (a)."))]),
        test2["17M.1.SL.TZ2.S_8"],
        test2["EXN.1.SL.TZ0.4"],
    ]
    write("maths-qbtest3.js", "QB_MATHS_QBTEST3", exercises)


def main(pdf):
    img = images(pdf)
    if len(img) == 7:
        return test2(img)
    assert len(img) == 16, len(img)   # 14 images d'énoncé, 2 de corrigé (courbe et boîte à moustaches)

    x, k = "<i>x</i>", "<i>k</i>"
    exercises = [
        exercise("19M.1.SL.TZ2.T_6", "19M", "May 2019", "TZ2", "T_", [
            OrderedDict(id="c1", html="<p>A health inspector analysed the amount of sugar in 500 different snacks prepared "
                                      "in various school cafeterias. The collected data are shown in the following "
                                      "box-and-whisker diagram.</p>" + img[0]
                                      + '<p class="center">Amount of sugar per snack in grams</p>'
                                      "<p>The health inspector visits two school cafeterias. She inspects the same number "
                                      "of meals at each cafeteria. The data is shown in the following box-and-whisker "
                                      "diagrams.</p>" + img[1]
                                      + "<p>Meals prepared in the school cafeterias are required to have less than 10 grams "
                                      "of sugar.</p>")], [
            part("", 2, ["c1"], "<p>State, giving a reason, which school cafeteria has more meals that do not meet the "
                                "requirement.</p>",
                 p("Cafeteria 2", "(A1)(C1)") + p("75 % &gt; 50 % (do not meet the requirement)", "(R1)(C1)")
                 + "<p><strong>OR</strong></p>" + p("25 % &lt; 50 % (meet the requirement)", "(R1)(C1)")
                 + note("Do not award (A1)(R0). Award the (R1) for a correct comparison of percentages for both "
                        "cafeterias, which may be in words. The percentage values or fractions must be seen. It is "
                        "possible to award (A0)(R1)."))]),
        exercise("18M.1.SL.TZ1.T_6", "18M", "May 2018", "TZ1", "T_", [
            OrderedDict(id="c1", html="<p>In a high school, 160 students completed a questionnaire which asked for the "
                                      "number of people they are following on a social media website. The results were "
                                      "recorded in the following box-and-whisker diagram.</p>" + img[2]
                                      + "<p>The following incomplete table shows the distribution of the responses from "
                                      "these 160 students.</p>" + img[3])], [
            part("", 1, ["c1"], f"<p>Write down the mid-interval value for the 100 &lt; {x} ≤ 150 group.</p>",
                 p("125 (accept 125.5)", "(A1)"))]),
        exercise("19N.1.SL.TZ0.T_15", "19N", "November 2019", "TZ0", "T_", [
            OrderedDict(id="c1", html="<p>Stephen was invited to perform a piano recital. In preparation for the event, "
                                      "Stephen recorded the amount of time, in minutes, that he rehearsed each day for "
                                      "the piano recital.</p><p>Stephen rehearsed for 32 days and data for all these days "
                                      "is displayed in the following box-and-whisker diagram.</p>" + img[4]),
            OrderedDict(id="c2", html="<p>Stephen states that he rehearsed on each of the 32 days.</p>")], [
            part("a", 1, ["c1"], "<p>Write down the median rehearsal time.</p>", p("42 (minutes)", "(A1)(C1)")),
            part("b", 2, ["c1", "c2"], "<p>State whether Stephen is correct. Give a reason for your answer.</p>",
                 p("Stephen is correct.", "(A1)") + p("the minimum rehearsal time is greater than zero", "(R1)")
                 + "<p><strong>OR</strong></p>" + p("he rehearsed at least 20 minutes every day", "(R1)(C2)")
                 + note("Do not award (A1)(R0). Accept equivalent reasoning based on the box-and-whisker diagram.")),
            part("c", 3, ["c1", "c2"], f"<p>On {k} days, Stephen practiced exactly 24 minutes. Find the possible "
                                       f"values of {k}.</p>",
                 p("0, 2, 3, 4, …, 15", "(A1)(A1)(A1)(C3)")
                 + note("Award (A1)(A1) for each correct endpoint of the interval, (A1) for indication of integer "
                        "values, except 1, between their endpoints."))]),
    ]
    a, b, h = "<i>a</i>", "<i>b</i>", "<i>h</i>"
    exercises += [
        exercise("17M.1.SL.TZ2.T_6", "17M", "May 2017", "TZ2", "T_", [
            OrderedDict(id="c1", html="<p>For a study, a researcher collected 200 leaves from oak trees. After measuring "
                                      "the lengths of the leaves, in cm, she produced the following cumulative frequency "
                                      "graph.</p>" + img[7])], [
            part("a", 1, ["c1"], "<p>Write down the median length of these leaves.</p>", p("9 (cm)", "(A1)(C1)")),
            part("b", 1, ["c1"], "<p>Write down the number of leaves with a length less than or equal to 8 cm.</p>",
                 p("40 (leaves)", "(A1)(C1)"))]),
        exercise("19M.1.SL.TZ2.T_12", "19M", "May 2019", "TZ2", "T_", [
            OrderedDict(id="c1", html=f"<p>University students were surveyed and asked how many hours, {h}, they worked "
                                      "each month. The results are shown in the following table.</p>" + img[8]
                                      + "<p>Use the table to find the following values.</p>"
                                      "<p>The first five class intervals, indicated in the table, have been used to draw "
                                      "part of a cumulative frequency curve as shown.</p>" + img[9])], [
            part("a.i", 1, ["c1"], "<p><i>p</i>.</p>",
                 p("<i>p</i> = 10", "(A1)(C1)") + note("Award (A1) for each correct value.")),
            part("a.ii", 1, ["c1"], "<p><i>q</i>.</p>",
                 p("<i>q</i> = 56", "(A1)(C1)") + note("Award (A1) for each correct value.")),
            part("b", 2, ["c1"], "<p>On the same grid, complete the cumulative frequency curve for these data.</p>",
                 img[14] + p("", "(A1)(A1)(C2)")
                 + note("Award (A1)(ft) for their 3 correctly plotted points; award (A1)(ft) for completing diagram "
                        "with a smooth curve through their points. The second (A1)(ft) can follow through from "
                        "incorrect points, provided the gradient of the curve is never negative. Award (C2) for a "
                        "completely correct smooth curve that goes through the correct points.")),
            part("c", 2, ["c1"], "<p>Use the cumulative frequency curve to find an estimate for the number of students "
                                 "who worked at most 35 hours per month.</p>",
                 p("a straight vertical line drawn at 35 (accept 35 ± 1)", "(M1)") + p("26 (students)", "(A1)(C2)")
                 + note("Accept values between 25 and 27 inclusive."))]),
        exercise("17N.1.SL.TZ0.T_1", "17N", "November 2017", "TZ0", "T_", [
            OrderedDict(id="c1", html="<p>A group of 20 students travelled to a gymnastics tournament together. Their "
                                      "ages, in years, are given in the following table.</p>" + img[10]
                                      + "<p>The lower quartile of the ages is 16 and the upper quartile is 18.5.</p>")], [
            part("a.ii", 1, ["c1"], "<p>For the students in this group write down the median age.</p>",
                 p("16.5", "(A1)(C1)")),
            part("b", 3, ["c1"], "<p>Draw a box-and-whisker diagram, for these students’ ages, on the following "
                                 "grid.</p>" + img[11],
                 img[15] + p("", "(A1)(A1)(A1)(ft)(C3)")
                 + note("Award (A1) for correct endpoints, (A1) for correct quartiles, (A1)(ft) for their median. "
                        "Follow through from part (a)(ii), but only if median is between 16 and 18.5. If a horizontal "
                        "line goes through the box, award at most (A1)(A1)(A0). Award at most (A0)(A1)(A1) if a ruler "
                        "has not been used."))]),
    ]
    t4 = {e["id"]: e for e in load_js(os.path.join(ROOT, "data", "maths-t4.js"))["exercises"]}
    exercises.append(t4["20N.1.SL.TZ0.S_8"])
    mean = ('<math><mfrac><mrow><mn>6</mn><mo>×</mo><mn>1</mn><mo>+</mo><mn>13</mn><mo>×</mo><mn>2</mn><mo>+</mo>'
            '<mn>26</mn><mo>×</mo><mn>3</mn><mo>+</mo><mo>(</mo><mn>75</mn><mo>−</mo><mi>b</mi><mo>)</mo><mo>×</mo>'
            '<mn>4</mn><mo>+</mo><mi>b</mi><mo>×</mo><mn>5</mn></mrow><mn>120</mn></mfrac><mo>=</mo><mn>3.65</mn></math>')
    exercises.append(OrderedDict(
        exercise("21N.1.SL.TZ0.9", "21N", "November 2021", "TZ0", "", [
            OrderedDict(id="c1", html="<p>A group of 120 students sat a history exam. The cumulative frequency graph "
                                      "shows the scores obtained by the students.</p>" + img[12]
                                      + "<p>The students were awarded a grade from 1 to 5, depending on the score "
                                      "obtained in the exam. The number of students receiving each grade is shown in the "
                                      "following table.</p>" + img[13] + "<p>The mean grade for these students is 3.65.</p>")], [
            part("a", 1, ["c1"], "<p>Find the median of the scores obtained.</p>", p("75", "A1")),
            part("b", 2, ["c1"], f"<p>Find an expression for {a} in terms of {b}.</p>",
                 p("recognition that all entries add up to 120", "(M1)")
                 + p(f"{a} = 120 − 6 − 13 − 26 − {b}&nbsp; OR &nbsp;{a} = 75 − {b}", "A1")),
            part("c.i", 3, ["c1"], "<p>Find the number of students who obtained a grade 5.</p>",
                 p(mean, "(M1)(A1)")
                 + note("Award (M1) for attempt to substitute into mean formula, LHS expression is sufficient for the "
                        "M mark. Award (A1) for correct substitutions in one variable OR in two variables, followed by "
                        f"evidence of solving simultaneously with {a} + {b} = 75.") + p(f"{b} = 28", "A1")),
            part("c.ii", 2, ["c1"], "<p>Find the minimum score needed to obtain a grade 5.</p>",
                 p("120 − their part (c)(i) seen (e.g. 92 indicated on graph)", "(M1)") + p("84", "A1"))]),
        section="B"))
    write("maths-qbtest.js", "QB_MATHS_QBTEST", exercises)


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--test3":
        test3(*sys.argv[2:])
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.exit(__doc__)
