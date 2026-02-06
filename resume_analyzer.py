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
st.title("📄 ATS Resume & Career Fit Analyzer")
st.write(
    "Upload your resume and paste a job description.\n"
    "You will get ATS score, improvement tips, and suitable job roles."
)

uploaded_file = st.file_uploader(
    "Upload Resume (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"]
)

job_description = st.text_area(
    "Paste Target Job Description",
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
# Analysis
# --------------------------------------------------
if st.button("Analyze Resume & Career Fit"):
    if not uploaded_file or job_description.strip() == "":
        st.warning("⚠ Please upload resume and paste job description")
    else:
        resume_text = extract_text(uploaded_file)

        prompt = f"""
You are:
- An ATS system
- A senior HR recruiter
- A career guidance expert

Analyze the resume and job description.

Respond ONLY in this format:

ATS_SCORE:
<number>/100

CURRENT_JOB_FIT:
<Is the candidate suitable for this job? Yes/Partial/No with reason>

KEYWORD_MATCH:
<percentage>%

MISSING_SKILLS:
- skill 1
- skill 2

ATS_FORMATTING_ISSUES:
- issue 1
- issue 2

SUITABLE_JOB_ROLES:
- Job Role 1 (reason)
- Job Role 2 (reason)
- Job Role 3 (reason)

SKILLS_TO_LEARN:
- Skill + why it matters
- Skill + recommended level

IMPROVEMENT_GUIDE:
- How to rewrite experience points
- Where to add keywords
- Formatting changes for ATS

Resume:
{resume_text}

Job Description:
{job_description}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )

        analysis = response.choices[0].message.content.strip()

        # --------------------------------------------------
        # Display structured output
        # --------------------------------------------------
        st.success("📊 Resume Analysis Result")

        sections = analysis.split("\n\n")

        for section in sections:
            if section.startswith("ATS_SCORE"):
                st.subheader("📌 ATS Score")
                st.write(section.replace("ATS_SCORE:", "").strip())

            elif section.startswith("CURRENT_JOB_FIT"):
                st.subheader("🎯 Current Job Suitability")
                st.write(section.replace("CURRENT_JOB_FIT:", "").strip())

            elif section.startswith("KEYWORD_MATCH"):
                st.subheader("🔑 Keyword Match")
                st.write(section.replace("KEYWORD_MATCH:", "").strip())

            elif section.startswith("MISSING_SKILLS"):
                st.subheader("❌ Missing Skills")
                st.write(section.replace("MISSING_SKILLS:", "").strip())

            elif section.startswith("ATS_FORMATTING_ISSUES"):
                st.subheader("⚠ ATS Formatting Issues")
                st.write(section.replace("ATS_FORMATTING_ISSUES:", "").strip())

            elif section.startswith("SUITABLE_JOB_ROLES"):
                st.subheader("💼 Jobs That Suit You")
                st.write(section.replace("SUITABLE_JOB_ROLES:", "").strip())

            elif section.startswith("SKILLS_TO_LEARN"):
                st.subheader("📚 Skills to Learn Next")
                st.write(section.replace("SKILLS_TO_LEARN:", "").strip())

            elif section.startswith("IMPROVEMENT_GUIDE"):
                st.subheader("🚀 Resume Improvement Guide")
                st.write(section.replace("IMPROVEMENT_GUIDE:", "").strip())
