import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import time

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input)
        return response.text
    except Exception as e:
        st.error(f"Error getting Gemini response: {e}")
        return None

def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        num_pages = len(reader.pages)
        progress_bar = st.progress(0)
        for page_num, page in enumerate(reader.pages):
            text += str(page.extract_text())
            progress_bar.progress((page_num + 1) / num_pages)
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
and finally suggest some other roals he/she can apply 
resume:{text}
description:{jd}

for example the repond format should be  like  :
Missing Keywords: 
Statistical packages (e.g. Python, R, SAS, Stata, MATLAB, etc.)
Experience working with multiple teams to bridge qualitative and quantitative insights
Deep interest and aptitude in data, metrics, analysis and trends
Applied knowledge of measurement, statistics and program evaluation
Adept complex analyses into data driven narratives
Profile Summary:
Candidate with B.Tech in Computer Engineering with a basic understanding of programming languages like C, C++, Java, Python, and SQL. Seeking a role where they can contribute to the effectiveness of the organization through creativity, challenges, and learning. Their comprehensive problem-solving abilities, willingness to learn, and team player nature make them a potential asset to any organization.

Suggested Roles: software developer , java developer 
links to apply the job : links to apply 

"""

# Function to process the response and display results
def process_response(response):
    try:
        data = json.loads(response)
        st.success(f"JD Match: {data['JD Match']}%")
        st.subheader("Missing Keywords:")
        for keyword in data['MissingKeywords']:
            st.write("- " + keyword)
        st.subheader("Profile Summary:")
        st.write(data['Profile Summary'])
    except Exception as e:
        st.error(f"Error parsing response: {e}")
        st.write(response) 

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        with st.spinner('Processing PDF...'):
            text = input_pdf_text(uploaded_file)
        if text:
            with st.spinner('Getting Gemini response...'):
                response = get_gemini_response(input_prompt.format(text=text, jd=jd))
            if response:
                with st.spinner('Processing response...'):
                    process_response(response)
