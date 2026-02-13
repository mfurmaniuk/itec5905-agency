from flask import Flask, render_template, request, redirect, url_for
import json
import os
from collections import defaultdict

app = Flask(__name__)

# National average scores per agency.
NATIONAL_AVERAGES = {
    "Autonomy": 2.6828,
    "Resilience": 1.4845,
    "Vulnerability": 1.0349,
}

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

def compare_to_national(agency_averages, national_averages):
    """Build per-agency comparison vs national averages."""
    comparisons = {}
    for agency, user_avg in agency_averages.items():
        nat_avg = national_averages.get(agency)
        if nat_avg is None:
            continue
        diff = user_avg - nat_avg
        if abs(diff) < 0.05:
            position = "about the same as"
        elif diff > 0:
            position = "above"
        else:
            position = "below"
        
        # Add contextual messages for specific agencies
        message = None
        if agency == "Autonomy":
            if diff > 0:
                message = "This suggests you tend to act independently and feel confident making your own decisions."
            elif diff < 0:
                message = "This may indicate a stronger preference for guidance or external support when making decisions."
        elif agency == "Resilience":
            if diff > 0:
                message = "This suggests you generally recover well from challenges and adapt to stress."
            elif diff < 0:
                message = "This may indicate that stressful situations feel more difficult to bounce back from."
        elif agency == "Vulnerability":
            if diff > 0:
                message = "This suggests you may be more sensitive to stress or emotional challenges."
            elif diff < 0:
                message = "This suggests a lower tendency toward emotional or stress-related vulnerability."
        
        comparisons[agency] = {
            "user_average": user_avg,
            "national_average": nat_avg,
            "difference": diff,
            "position": position,
            "message": message,
        }
    return comparisons

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
        
        # Calculate average scores per agency
        agency_result = calculate_score(survey_data, answers)
        # Build comparison to national averages for each agency
        agency_comparisons = compare_to_national(agency_result, NATIONAL_AVERAGES)

        return render_template(
            "thank_you.html",
            answers=answers,
            questions=survey_data["questions"],
            agency_result=agency_result,
            agency_comparisons=agency_comparisons,
        )

    # GET request - show the survey with all questions
    return render_template("survey.html", survey=survey_data)

if __name__ == "__main__":
    # Development server
    app.run(debug=True)