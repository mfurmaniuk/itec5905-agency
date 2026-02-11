from flask import Flask, render_template, request, redirect, url_for
import json
import os
from collections import defaultdict

app = Flask(__name__)

def load_survey():
    """Load survey definition from JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "survey.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_score(survey_data, answers):
    """
    Calculate average numeric scores per agency from survey.json.

    For each question that has an 'agency' and a 'scoring' map, we:
    - look up the user's selected answer
    - add the numeric score to that agency's running total
    - increment the count of questions contributing to that agency

    The result is a dict mapping agency name -> average score.
    """
    agency_sums = defaultdict(int)
    agency_counts = defaultdict(int)

    for question in survey_data["questions"]:
        agency = question.get("agency")
        scoring = question.get("scoring") or {}
        if not agency or not scoring:
            continue

        answer = answers.get(question["id"])
        if answer is None or answer not in scoring:
            continue

        agency_sums[agency] += scoring[answer]
        agency_counts[agency] += 1

    # Compute per-agency averages; only include agencies with at least one scored question
    agency_averages = {}
    for agency, total in agency_sums.items():
        count = agency_counts.get(agency, 0)
        if count > 0:
            agency_averages[agency] = total / count

    return agency_averages

@app.route("/")
def index():
    """Welcome page with link to survey."""
    return render_template("index.html")

@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")

@app.route("/survey", methods=["GET", "POST"])
def survey():
    survey_data = load_survey()
    
    if request.method == "POST":
        # Collect all answers
        answers = {}
        for question in survey_data["questions"]:
            answers[question["id"]] = request.form.get(question["id"])
        
        # Calculate profile
        agency_result = calculate_score(survey_data, answers)
        
        return render_template(
            "thank_you.html",
            answers=answers,
            questions=survey_data["questions"],
            agency_result=agency_result
        )

    # GET request - show the survey with all questions
    return render_template("survey.html", survey=survey_data)

if __name__ == "__main__":
    # Development server
    app.run(debug=True)