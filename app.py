import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("Universal Text Summarizer 🧠📄🖼️")
st.write("Upload a file or enter text to get a summary")

# Checkbox
show_response = st.checkbox("Show Full LLM Response")

# Text input
user_text = st.text_area("Or type text manually")

# File upload
uploaded_file = st.file_uploader(
    "Upload a document (PDF, Word, Image, Text)",
    type=["txt", "pdf", "docx", "png", "jpg", "jpeg"]
)

def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")

    elif file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file.type.startswith("image"):
        image = Image.open(file)
        return pytesseract.image_to_string(image)

    return ""

if st.button("Summarize"):
    text = user_text.strip()

    if uploaded_file:
        text = extract_text(uploaded_file)

    if text == "":
        st.warning("Please provide text or upload a file")
    else:
        prompt = f"""
        Summarize the following content clearly and concisely:

        {text}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        summary = response.choices[0].message.content.strip()

        st.success("Summary:")
        st.write(summary)

        # Console output
        print("MODEL OUTPUT:")
        print(summary)

        if show_response:
            st.json(response.model_dump())
