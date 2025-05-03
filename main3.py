import os
import openai  # Ensure you have this installed via pip (pip install openai)
import streamlit as st
import markdown2
import pdfkit

os.environ["GITHUB_TOKEN"] = "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"

# ===== OpenAI Configuration =====

# Load OpenAI API Key from Environment Variable
token = os.environ.get("GITHUB_TOKEN", None)
if not token:
    st.error("GitHub token not found. Set the environment variable GITHUB_TOKEN.")
    st.stop()

# Use a custom endpoint if required
endpoint = "https://models.github.ai/inference"  # Replace with actual endpoint if necessary
model = "openai/gpt-4.1"  # Replace with the actual model

# Configure OpenAI client
openai.api_base = endpoint
openai.api_key = token


# ===== Function Definitions =====

# Function to generate resume in markdown format via OpenAI API
def generate_resume(role, name, email, mobile, linkedin, github, about, education, experience, projects, certificates,
                    links):
    prompt = f"""
    Directly start with the resume, also don't add any emojis or special characters.
    No need to add any headers or titles, just the content.
    Use H1 for the name and role, H2 for the sections (About, Education, Work Experience, Projects, Certificates, Additional Links), and bullet points for the details.
    Separate sections with --- and use an ATS-friendly format.
    I am applying for the role of {role}. Use the information below to create my resume:

    Name: {name}
    Email: {email}
    Mobile: {mobile}
    LinkedIn: {linkedin}
    GitHub: {github}

    About me: {about}

    Education: {education}

    Work Experience: {experience}

    Projects: {projects}

    Certificates: {certificates}

    Additional Links: {links}
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI-powered assistant for generating resumes."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error generating resume: {e}")
        return None


# Function to provide feedback on resume content
def get_resume_feedback(role, resume_content):
    prompt = f"""
    Please review the following resume for the role of {role} and provide a score out of 100.
    Include detailed feedback on:
    - Relevance of skills and experience for the role.
    - Areas for improvement.
    - Missing components that are commonly expected in resumes for this role.

    Resume:
    {resume_content}
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error providing feedback: {e}")
        return None


# Function to convert Markdown to PDF
def convert_markdown_to_pdf(markdown_content, output_filename):
    try:
        # Convert markdown to HTML
        html_content = markdown2.markdown(markdown_content)

        # Add CSS for PDF formatting
        custom_css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }
            h1, h2 {
                color: #333;
            }
            h1 {
                font-size: 24px;
                font-weight: bold;
            }
            h2 {
                font-size: 18px;
                margin-top: 20px;
            }
            p, li {
                font-size: 14px;
            }
        </style>
        """
        html_content = f"{custom_css}{html_content}"

        # Save HTML content to a temporary file
        temp_html = "temp_resume.html"
        with open(temp_html, 'w') as temp_file:
            temp_file.write(html_content)

        # Convert the HTML file to PDF
        pdfkit.from_file(temp_html, output_filename)
        os.remove(temp_html)  # Clean up temporary HTML file after PDF generation
        return True
    except Exception as e:
        st.error(f"Error converting Markdown to PDF: {e}")
        return False


# ===== Streamlit UI =====

st.title("AI-Powered Resume Generator")

st.sidebar.header("Input Your Details")
role = st.sidebar.text_input("Role you're applying for", "Data Engineer")
name = st.sidebar.text_input("Full Name", "John Doe")
email = st.sidebar.text_input("Email", "johndoe@examplemail.com")
mobile = st.sidebar.text_input("Mobile Number", "+1 123 456 7890")
linkedin = st.sidebar.text_input("LinkedIn Profile URL", "https://linkedin.com/in/johndoe")
github = st.sidebar.text_input("GitHub Profile URL", "https://github.com/johndoe")
about = st.sidebar.text_area("About Me", "I am a data engineer with expertise in ETL, pipelines, and cloud computing.")
education = st.sidebar.text_area("Education", "Master of Computer Science, XYZ University, 2019-2021")
experience = st.sidebar.text_area("Work Experience", "Software Engineer at Company A: Built pipelines...")
projects = st.sidebar.text_area("Projects", "1. Predictive Analytics using Python.")
certificates = st.sidebar.text_area("Certificates", "AWS Solutions Architect (2021)")
links = st.sidebar.text_area("Additional Links", "https://personal-portfolio.com")

# Button to trigger resume generation
if st.sidebar.button("Generate Resume"):
    with st.spinner("Generating your resume..."):
        # Generate resume via GPT
        resume_markdown = generate_resume(
            role, name, email, mobile, linkedin, github, about, education, experience, projects, certificates, links
        )

        if resume_markdown:
            st.success("Resume successfully generated!")
            st.subheader("Generated Markdown Resume")
            st.code(resume_markdown, language="markdown")

            # Offer feedback
            feedback = get_resume_feedback(role, resume_markdown)
            if feedback:
                st.subheader("Resume Feedback")
                st.text(feedback)

            # Convert Markdown to PDF and allow download
            output_pdf_path = "generated_resume.pdf"
            if convert_markdown_to_pdf(resume_markdown, output_pdf_path):
                with open(output_pdf_path, "rb") as pdf_file:
                    st.download_button("Download Your Resume as PDF", pdf_file, file_name="resume.pdf")
