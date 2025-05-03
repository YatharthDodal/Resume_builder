import streamlit as st
import markdown2
import pdfkit

import os
#from google import genai
import google.generativeai as genai1

client = genai1.configure(api_key=os.getenv("AIzaSyAEb5Sgx9x7NZqSjgq-iHK4JXvmx924cGo"))
#chat = client.chats.create(model="gemini-2.0-flash")
def generate_resume(role, name, email, mobile, linkedin, github, about, educaion, experience, projects,certificates, links):
    prompt = (
            "Directly start with the resume, also don't add any emojis or special characters.\n"
            "No need to add any headers or titles, just the content.\n"
            "Use H1 for the name and role, H2 for the sections (About, Education, Work Experience, Projects, Certificates, Additional Links), and bullet points for the details.\n"
            "Use ATS-friendly resume format with keywords.\n"
            "I am applying for the role of " + role + ". Here is my information:\n"
                                                      "Name: " + name + "\n"
                                                                        "Email: " + email + "\n"
                                                                                            "Mobile: " + mobile + "\n"
                                                                                                                  "Linkedin: " + linkedin + "\n"
                                                                                                                                            "Github: " + github + "\n"
                                                                                                                                                                  "About me: " + about + "\n"
                                                                                                                                                                                         "Education: " + educaion + "\n"
                                                                                                                                                                                                                    "Work Experience: " + experience + "\n"
                                                                                                                                                                                                                                                       "Projects: " + projects + "\n"
                                                                                                                                                                                                                                                                                 "Certificates: " + certificates + "\n"
                                                                                                                                                                                                                                                                                                                   "Additional Links: " + links + "\n"
                                                                                                                                                                                                                                                                                                                                                  "Please format this resume in markdown, optimised for the role of " + role + "."
    )

    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        response=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.25
    )return response.text"""
    model = genai1.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    return response.text


def get_resume_feedback(role, resume_content):
    prompt = (
            "You are an expert career advisor. Please review the following resume for the role of " + role + " and provide a score out of 100.\n"
                                                                                                             "Include detailed feedback on the following areas:\n"
                                                                                                             "- Relevance of skills and experience for the role.\n"
                                                                                                             "- Areas for improvement.\n"
                                                                                                             "- Missing components that are commonly expected in resumes for this role.\n"
                                                                                                             "Resume content:\n"
            + resume_content
    )

    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        response=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.25
    )
    return response.text"""
    model = genai1.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    return response.text

def convert_markdown_to_pdf(markdown_content, output_filename):
    try:
        html_content = markdown2.markdown(markdown_content)
        custom_css = """
        <style>
            body {
            font-family: Arial, sans-serif;
            }
        </style>
        """
        html_content = f"{custom_css}{html_content}"
        temp_html = "resume.html"
        with open(temp_html, "w") as f:
            f.write(html_content)
        pdfkit.from_file(temp_html, output_filename)
        os.remove(temp_html)
        return True
    except Exception as e:
        st.error(f"Error converting Markdown into PDF: {e}")
        return False

st.title("AI-Powered Resume Generator (Gemini)")

role = st.text_input("Role you're applying for", "Data Engineer")
name = st.text_input("Full Name", "John Doe")
email = st.text_input("Email", "example@email.com")
mobile = st.text_input("Mobile Number", "+1 123 456 7890")
linkedin = st.text_input("LinkedIn Profile URL", "https://linkedin.com/in/johndoe")
github = st.text_input("GitHub Profile URL", "https://github.com/johndoe")
about = st.text_area("Tell us about yourself", "I am a data engineer passionate about...")
education = st.text_area("Education", "B.Sc. in Computer Science, University X")
experience = st.text_area("Work Experience", "Software Engineer at Y Company...")
projects = st.text_area("Projects", "Developed an AI-powered resume generator...")
certificates = st.text_area("Certificates", "AWS Certified Solutions Architect")
links = st.text_area("Additional Links", "https://portfolio.com")

if st.button("Generate Resume"):
    resume_markdown = generate_resume(role, name, email, mobile, linkedin, github, about, education, experience, projects, certificates, links)
    feedback = get_resume_feedback(role, resume_markdown)
    st.subheader("Resume Feedback and Score")
    st.text(feedback)
    if convert_markdown_to_pdf(resume_markdown, "resume_generated.pdf"):
        st.success("Resume PDF generated successfully!")
        with open("resume_generated.pdf", "rb") as f:
            st.download_button("Download Resume PDF", f, file_name="resume_generated.pdf")





