import streamlit as st
import openai
from docx import Document

# Configure OpenAI API Key
openai.api_key = 'sk-jJEP5FWSHXkU2V3livED4-tqeILbHajtrS6B6EKrGuT3BlbkFJ5GFHFqw_0MtqKzoLOD7gMhG4TTaKfA1ENm3_2KjJsA'

if not openai.api_key:
    st.error("API key is missing. Please check your configuration.")

# Function to extract text from DOCX
def extract_docx_content(docx_file):
    """
    Extracts text from a DOCX file while preserving the original formatting.
    """
    try:
        doc = Document(docx_file)
        sections = [{"text": para.text, "style": para.style} for para in doc.paragraphs]
        return sections
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return None

# Function to enhance resume content
def enhance_resume_content(current_sections, job_description):
    """
    Enhances resume content section by section based on the job description.
    """
    try:
        current_text = "\n".join([section["text"] for section in current_sections if section["text"].strip()])
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional resume writer and ATS optimization expert. "
                        "Rewrite the provided resume to align perfectly with the job description. "
                        "Ensure it includes relevant skills, keywords, and experiences while retaining its original format. "
                        "The resume must be ATS-friendly and free of gaps."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Resume:\n{current_text}\n\nJob Description:\n{job_description}",
                },
            ],
            max_tokens=3000,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error enhancing resume content: {e}")
        return None

# Function to save enhanced content back to the DOCX
def save_docx_content(original_docx_file, updated_content):
    """
    Saves the enhanced resume content back into the original DOCX file while retaining formatting.
    """
    try:
        doc = Document(original_docx_file)
        updated_paragraphs = updated_content.split("\n")

        para_index = 0
        for para in doc.paragraphs:
            if para.text.strip() and para_index < len(updated_paragraphs):
                para.text = updated_paragraphs[para_index]
                para_index += 1

        # Save the enhanced resume
        filename = "Enhanced_Resume_Clean.docx"
        doc.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error saving enhanced resume: {e}")
        return None

# Streamlit app interface
st.title("ATS-Friendly Resume Enhancer")
st.text("Upload your DOCX resume and paste the job description to generate a clean, ATS-optimized resume.")

# Upload DOCX resume file
uploaded_file = st.file_uploader("Upload Your Resume (DOCX)", type=["docx"], help="Upload your Word resume in DOCX format.")

# Input job description
job_description = st.text_area("Paste the Job Description", help="Enter the job description for the role you are applying for.")

# Submit button
if st.button("Enhance Resume"):
    if not uploaded_file:
        st.warning("Please upload your current resume.")
    elif not job_description:
        st.warning("Please paste the job description.")
    else:
        st.info("Extracting content from the uploaded resume...")
        current_sections = extract_docx_content(uploaded_file)

        if current_sections:
            st.success("Resume content extracted successfully.")
            st.info("Enhancing resume content based on the job description...")
            enhanced_content = enhance_resume_content(current_sections, job_description)

            if enhanced_content:
                st.success("Resume enhanced successfully!")
                st.info("Saving enhanced resume...")
                enhanced_docx_file = save_docx_content(uploaded_file, enhanced_content)

                if enhanced_docx_file:
                    st.success("Enhanced resume saved as DOCX.")
                    with open(enhanced_docx_file, "rb") as file:
                        st.download_button(
                            "Download Enhanced Resume (DOCX)",
                            file,
                            file_name="Enhanced_Resume_Clean.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
                else:
                    st.error("Failed to save enhanced resume. Please try again.")
            else:
                st.error("Failed to enhance resume content. Please try again.")
        else:
            st.error("Failed to extract content from the resume. Please ensure the file is a valid DOCX format.")
