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
    """Sum numeric scores per agency from survey.json."""
    agency_totals = defaultdict(int)

    for question in survey_data["questions"]:
        agency = question.get("agency")
        scoring = question.get("scoring") or {}
        if not agency or not scoring:
            continue
        answer = answers.get(question["id"])
        if answer is not None and answer in scoring:
            agency_totals[agency] += scoring[answer]

    return dict(agency_totals)

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