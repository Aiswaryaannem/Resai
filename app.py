import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the GenAI API
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
else:
    st.error("API key is missing. Please check your environment variables.")

# Function to generate response using Gemini Pro
def get_gemini_pro_response(input_text):
    try:
        response = genai.generate_text(
            model="gemini-pro",
            prompt=input_text
        )
        return response.text
    except Exception as e:
        st.error(f"Failed to generate response: {e}")
        return None

# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += str(page.extract_text())
        return text
    except Exception as e:
        st.error(f"Error processing the PDF file: {e}")
        return None

# Input prompt template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science,
data analyst, and AI engineer. Your task is to evaluate the resume based on 
the given job description. You must consider the job market is very competitive 
and you should provide the best assistance for improving the resumes. Assign 
the percentage Matching based on Job description and the missing keywords with 
high accuracy.
resume: {text}
description: {job_description}

I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS Score")
job_description = st.text_area("Paste the Job Description", help="Enter the job description for which the resume will be evaluated.")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the resume in PDF format.")

# Submit button
submit = st.button("Submit")

if submit:
    # Validate inputs
    if not job_description:
        st.warning("Please paste the job description.")
    elif uploaded_file is None:
        st.warning("Please upload a resume in PDF format.")
    else:
        # Process resume text
        text = input_pdf_text(uploaded_file)
        if text:
            # Generate the prompt
            prompt = input_prompt.format(text=text, job_description=job_description)
            # Get response from Gemini Pro
            response = get_gemini_pro_response(prompt)
            if response:
                st.subheader("ATS Evaluation Result:")
                try:
                    st.json(eval(response))  # Convert response string to JSON and display
                except Exception as e:
                    st.error(f"Error parsing the response: {e}")
