from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

def load_survey():
    """Load survey definition from JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "survey.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    """Welcome page with link to survey."""
    return render_template("index.html")

@app.route("/survey", methods=["GET", "POST"])
def survey():
    survey_data = load_survey()
    question = survey_data["questions"][0]  # only one question for now

    if request.method == "POST":
        # Get selected answer
        answer = request.form.get(question["id"])
        # For now we just show a simple thank you page;
        # in a real app you would store this in a database or file.
        return render_template(
            "thank_you.html",
            answer=answer,
            question_text=question["text"]
        )

    return render_template("survey.html", survey=survey_data, question=question)

if __name__ == "__main__":
    # Development server
    app.run(debug=True)