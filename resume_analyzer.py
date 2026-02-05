import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
from docx import Document

# Load env
load_dotenv()

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("📄 AI Resume & ATS Analyzer")
st.write("Upload resume and job description to get ATS score")

# Upload resume
uploaded_file = st.file_uploader(
    "Upload Resume (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"]
)

# Job description
job_description = st.text_area("Paste Job Description")

# Checkbox
show_response = st.checkbox("Show Full LLM Response")

# Text extraction
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")

    elif file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""

# Analyze button
if st.button("Analyze Resume (ATS)"):
    if not uploaded_file or job_description.strip() == "":
        st.warning("Please upload resume and job description")
    else:
        resume_text = extract_text(uploaded_file)

        prompt = f"""
You are an ATS system and professional HR recruiter.

Analyze the resume against the job description.

Tasks:
1. Calculate ATS match score (0–100)
2. Identify keyword match percentage
3. List missing important skills
4. Mention resume strengths
5. Identify ATS formatting issues
6. Give suggestions to improve ATS score

Resume:
{resume_text}

Job Description:
{job_description}

Respond in a structured and clear format.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )

        result = response.choices[0].message.content

        st.success("📊 ATS Resume Analysis")
        st.write(result)

        # Console output
        print("ATS ANALYSIS RESULT:")
        print(result)

        if show_response:
            st.json(response.model_dump())



