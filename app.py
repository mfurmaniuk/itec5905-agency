from flask import Flask, render_template, request, redirect, url_for
import json
import os
from collections import Counter

app = Flask(__name__)

def load_survey():
    """Load survey definition from JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "survey.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_profile(survey_data, answers):
    """Calculate the microaggression vulnerability profile based on answers."""
    profile_scores = Counter()
    
    for question in survey_data["questions"]:
        question_id = question["id"]
        answer = answers.get(question_id)
        
        # Check if this question has profile mappings
        if answer and "profiles" in question and question["profiles"]:
            profile = question["profiles"].get(answer)
            if profile:
                profile_scores[profile] += 1
    
    # Determine the dominant profile (most common)
    if profile_scores:
        dominant_profile = profile_scores.most_common(1)[0][0]
        return {
            "dominant": dominant_profile,
            "scores": dict(profile_scores)
        }
    return None

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
        profile_result = calculate_profile(survey_data, answers)
        
        return render_template(
            "thank_you.html",
            answers=answers,
            questions=survey_data["questions"],
            profile_result=profile_result
        )

    # GET request - show the survey with all questions
    return render_template("survey.html", survey=survey_data)

if __name__ == "__main__":
    # Development server
    app.run(debug=True)