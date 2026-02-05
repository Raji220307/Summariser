import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Page title
st.title("Sentiment Analysis App 😊😐😡")

st.write("Enter a sentence and find out whether it is Positive, Negative, or Neutral.")

# Text input
user_text = st.text_area("Enter your text here:")

# ✅ Checkbox should be OUTSIDE the button
show_response = st.checkbox("Show/Hide Full LLM Response")

# Button
if st.button("Analyze Sentiment"):
    if user_text.strip() == "":
        st.warning("Please enter some text")
    else:
        prompt = f"""
        Analyze the sentiment of the following text.
        Respond with only one word: Positive, Negative, or Neutral.

        Text:
        {user_text}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )

        # Console output
        print("FULL RESPONSE OBJECT:")
        print(response)
        print("\nMODEL OUTPUT:")
        print(response.choices[0].message.content)

        sentiment = response.choices[0].message.content.strip()

        st.success(f"Sentiment: **{sentiment}**")

        # ✅ Show only if checkbox is checked
        if show_response:
            st.write("Full LLM Response:")
            st.json(response.model_dump())
