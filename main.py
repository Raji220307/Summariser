from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

app = Flask(__name__)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None

    if request.method == "POST":
        paragraph = request.form["paragraph"]

        prompt = f"""
        Read the following paragraph carefully and summarize all its content
        in one concise sentence:

        {paragraph}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        summary = response.choices[0].message.content

    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
