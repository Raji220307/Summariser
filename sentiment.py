import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import pandas as pd

from PyPDF2 import PdfReader
from docx import Document

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Initialize Groq client
# --------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.title("🧠 Sentiment Analysis App (Text & Documents)")
st.write("Analyze sentiment from **text input or uploaded files** (PDF, DOCX, CSV).")

# User input choice
input_type = st.radio(
    "Choose Input Type",
    ["Text", "PDF", "DOCX", "CSV"]
)

show_response = st.checkbox("Show/Hide Full LLM Response")

# --------------------------------------------------
# Input Section
# --------------------------------------------------
text_data = ""

if input_type == "Text":
    text_data = st.text_area("Enter your text here:")

elif input_type in ["PDF", "DOCX", "CSV"]:
    uploaded_file = st.file_uploader(
        f"Upload {input_type} file",
        type=[input_type.lower()]
    )

    def extract_text(file):
        if file is None:
            return ""

        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join(
                [page.extract_text() or "" for page in reader.pages]
            )

        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs])

        elif file.type == "text/csv":
            df = pd.read_csv(file)
            return " ".join(df.astype(str).values.flatten())

        return ""

    if uploaded_file:
        text_data = extract_text(uploaded_file)

# --------------------------------------------------
# Sentiment Analysis
# --------------------------------------------------
if st.button("Analyze Sentiment"):
    if text_data.strip() == "":
        st.warning("⚠ Please provide some text or upload a file")
    else:
        prompt = f"""
Analyze the sentiment of the following content.

Respond with only ONE word:
Positive, Negative, or Neutral.

Content:
{text_data}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )

        sentiment = response.choices[0].message.content.strip()

        st.success(f"📊 Sentiment: **{sentiment}**")

        if show_response:
            st.subheader("Full LLM Response")
            st.json(response.model_dump())
