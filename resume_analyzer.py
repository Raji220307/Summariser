import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
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
# UI
# --------------------------------------------------
st.title("📄 ATS Resume Analyzer")
st.write("Upload your resume and paste the job description to get ATS score and improvement tips.")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=200
)

# --------------------------------------------------
# Text extraction
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
        return "\n".join(p.text for p in doc.paragraphs)

    return ""

# --------------------------------------------------
# ATS Analysis
# --------------------------------------------------
if st.button("Analyze Resume (ATS)"):
    if not uploaded_file or job_description.strip() == "":
        st.warning("⚠ Please upload resume and paste job description")
    else:
        resume_text = extract_text(uploaded_file)

        prompt = f"""
You are an Applicant Tracking System (ATS) and senior HR recruiter.

Analyze the resume strictly for ATS compatibility.

Return the response ONLY in the following format:

ATS_SCORE:
<number>/100

KEYWORD_MATCH:
<percentage>%

MISSING_SKILLS:
- skill 1
- skill 2

RESUME_STRENGTHS:
- point 1
- point 2

ATS_FORMATTING_ISSUES:
- issue 1
- issue 2

IMPROVEMENT_SUGGESTIONS:
- Exact changes to make
- Where to add keywords
- How to rewrite bullet points
- Formatting improvements

Resume:
{resume_text}

Job Description:
{job_description}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )

        analysis = response.choices[0].message.content.strip()

        # --------------------------------------------------
        # Display CLEAN output
        # --------------------------------------------------
        st.success("📊 ATS Resume Evaluation")

        sections = analysis.split("\n\n")

        for section in sections:
            if section.startswith("ATS_SCORE"):
                st.subheader("📌 ATS Score")
                st.write(section.replace("ATS_SCORE:", "").strip())

            elif section.startswith("KEYWORD_MATCH"):
                st.subheader("🔑 Keyword Match")
                st.write(section.replace("KEYWORD_MATCH:", "").strip())

            elif section.startswith("MISSING_SKILLS"):
                st.subheader("❌ Missing Skills")
                st.write(section.replace("MISSING_SKILLS:", "").strip())

            elif section.startswith("RESUME_STRENGTHS"):
                st.subheader("✅ Resume Strengths")
                st.write(section.replace("RESUME_STRENGTHS:", "").strip())

            elif section.startswith("ATS_FORMATTING_ISSUES"):
                st.subheader("⚠ ATS Formatting Issues")
                st.write(section.replace("ATS_FORMATTING_ISSUES:", "").strip())

            elif section.startswith("IMPROVEMENT_SUGGESTIONS"):
                st.subheader("🚀 How to Improve Your Resume")
                st.write(section.replace("IMPROVEMENT_SUGGESTIONS:", "").strip())
