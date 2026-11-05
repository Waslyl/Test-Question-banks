#!/usr/bin/env python3
"""Convertit le test « QuestionBank Test » (PDF exporté depuis la Questionbank, 4 questions de statistiques)
en data/maths-qbtest.js, pour en faire un sujet W4ss avec build_maths_exam.py (sujet qb-p1).

Usage :
    python3 scripts/build_qbtest.py QuestionBank_Test.pdf

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


def main(pdf):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdfimages", "-png", pdf, os.path.join(tmp, "img")], check=True)
        names = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
        assert len(names) == 7, names
        img = [f'<p><img src="data:image/png;base64,{base64.b64encode(open(os.path.join(tmp, n), "rb").read()).decode()}"></p>'
               for n in names]

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
    t4 = {e["id"]: e for e in load_js(os.path.join(ROOT, "data", "maths-t4.js"))["exercises"]}
    exercises.append(t4["20N.1.SL.TZ0.S_8"])
    out = OrderedDict(subject="DP Mathematics: Analysis and Approaches", level="SL",
                      topic=OrderedDict(number=4, title="Statistics and probability"), exercises=exercises)
    target = os.path.join(ROOT, "data", "maths-qbtest.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("window.QB_MATHS_QBTEST = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"data/maths-qbtest.js : {len(exercises)} questions, {sum(e['marks'] for e in exercises)} points")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
