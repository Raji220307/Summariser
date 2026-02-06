import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

from PyPDF2 import PdfReader
from docx import Document

# ---------------------------------------------------
# Load environment variables
# ---------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Initialize Groq client
# --------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.title("🧠 AI Test Paper Evaluation System")
st.write("Upload a test paper containing **questions and student answers** to get automatic evaluation.")

uploaded_file = st.file_uploader(
    "Upload Test Paper (PDF, Word, Text)",
    type=["pdf", "docx", "txt"]
)

max_marks = st.number_input(
    "Maximum Marks",
    min_value=1,
    max_value=100,
    value=10
)

# --------------------------------------------------
# Text Extraction Function (NO IMAGE / OCR)
# --------------------------------------------------
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")

    elif file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    return ""

# --------------------------------------------------
# Evaluation Logic
# --------------------------------------------------
if st.button("Evaluate Test Paper"):
    if not uploaded_file:
        st.warning("⚠ Please upload a test paper")
    else:
        test_text = extract_text(uploaded_file)

        if test_text.strip() == "":
            st.warning("⚠ Could not extract text from the file")
        else:
            prompt = f"""
You are an experienced exam evaluator.

The following document contains exam questions
along with student answers.

Evaluate the paper using general subject knowledge.

Instructions:
- Understand each question
- Evaluate the student's answers
- Assign marks out of {max_marks}
- Clearly mention:
  1. Total marks obtained
  2. Correct answers / good points
  3. Wrong or missing points
  4. Short feedback for improvement

Test Paper Content:
{test_text}

Provide the evaluation in a clear, structured format.
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700
            )

            evaluation = response.choices[0].message.content.strip()

            # --------------------------------------------------
            # Display Results (Only Evaluation)
            # --------------------------------------------------
            st.success("📊 Evaluation Result")
            st.write(evaluation)

            # Console output (optional for developer)
            print("====== TEST PAPER EVALUATION ======")
            print(evaluation)
