# src/ats_analyzer.py
import streamlit as st
from PyPDF2 import PdfReader
import docx
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(docx_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

def preprocess_text(text):
    """Clean and preprocess text"""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    return tokens

def extract_keywords(text, top_n=20):
    """Extract most frequent keywords"""
    tokens = preprocess_text(text)
    word_freq = Counter(tokens)
    keywords = [word for word, freq in word_freq.most_common(top_n)]
    return keywords

def extract_keywords_from_job_name(job_name):
    """Extract keywords from job name"""
    tokens = preprocess_text(job_name)
    return tokens

def calculate_match_score(resume_keywords, job_keywords):
    """Calculate match score between resume and job description"""
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    common_keywords = resume_set.intersection(job_set)
    match_score = (len(common_keywords) / max(len(job_set), 1)) * 100  # Avoid division by zero
    return match_score, common_keywords

def main():
    st.title("ATS Resume Analyzer")
    st.write("Upload your resume and enter a job title to analyze compatibility")

    # File upload and job title input
    resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])
    job_name = st.text_input("Enter Job Title", "")

    # Submit button
    analyze_button = st.button("Analyze")

    # Process when button is clicked
    if analyze_button:
        if resume_file is None:
            st.error("Please upload a resume before analyzing.")
        elif not job_name.strip():
            st.error("Please enter a job title before analyzing.")
        else:
            with st.spinner("Analyzing..."):
                # Extract text from resume
                if resume_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(resume_file)
                else:
                    resume_text = extract_text_from_docx(resume_file)

                if not resume_text:
                    st.error("Could not extract text from resume.")
                else:
                    # Extract keywords
                    resume_keywords = extract_keywords(resume_text)
                    job_keywords = extract_keywords_from_job_name(job_name)

                    # Calculate match score
                    match_score, common_keywords = calculate_match_score(resume_keywords, job_keywords)

                    # Display results
                    st.subheader("Analysis Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("Resume Keywords:")
                        st.write(", ".join(resume_keywords))
                        
                    with col2:
                        st.write("Job Title Keywords:")
                        st.write(", ".join(job_keywords))

                    st.subheader("Match Score")
                    st.progress(int(match_score)/100)
                    st.write(f"Compatibility: {match_score:.2f}%")

                    st.subheader("Matching Keywords")
                    st.write(", ".join(common_keywords))

                    # Provide recommendations
                    st.subheader("Recommendations")
                    missing_keywords = set(job_keywords) - set(resume_keywords)
                    if missing_keywords:
                        st.write("Consider adding these keywords to your resume:")
                        st.write(", ".join(missing_keywords))
                    else:
                        st.write("Great match! Your resume covers all key job requirements.")

if __name__ == "__main__":
    main()
