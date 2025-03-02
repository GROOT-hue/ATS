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

    """Extract text from DOCX file"""
    try:
        doc = docx.Document(docx_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except:
        return ""

def preprocess_text(text):
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    return tokens

def extract_keywords(text, top_n=20):
    """Extract most frequent keywords"""
    tokens = preprocess_text(text)
    # Count word frequencies
    word_freq = Counter(tokens)
    # Get most common keywords
    keywords = [word for word, freq in word_freq.most_common(top_n)]
    return keywords

def calculate_match_score(resume_keywords, job_keywords):
    """Calculate match score between resume and job description"""
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    common_keywords = resume_set.intersection(job_set)
    match_score = (len(common_keywords) / len(job_set)) * 100
    return match_score, common_keywords

def main():
    st.title("ATS Resume Analyzer")
    st.write("Upload your resume and job description to analyze compatibility")

    # File upload sections
    resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])
    job_desc_file = st.file_uploader("Upload Job Description (PDF, DOCX, or TXT)", 
                                   type=['pdf', 'docx', 'txt'])
    
    if resume_file and job_desc_file:
        # Extract text from resume
        if resume_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_docx(resume_file)

        # Extract text from job description
        if job_desc_file.type == "application/pdf":
            job_text = extract_text_from_pdf(job_desc_file)
        elif job_desc_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            job_text = extract_text_from_docx(job_desc_file)
        else:
            job_text = job_desc_file.getvalue().decode("utf-8")

        if resume_text and job_text:
            # Extract keywords
            resume_keywords = extract_keywords(resume_text)
            job_keywords = extract_keywords(job_text)

            # Calculate match score
            match_score, common_keywords = calculate_match_score(resume_keywords, job_keywords)

            # Display results
            st.subheader("Analysis Results")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Resume Keywords:")
                st.write(", ".join(resume_keywords))
                
            with col2:
                st.write("Job Description Keywords:")
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
