import os
import openai  # pip install openai
import streamlit as st
import markdown2  # pip install markdown2
import pdfkit  # pip install pdfkit
import pinecone  # pip install pinecone-client
from langchain.embeddings import OpenAIEmbeddings  # pip install langchain
from jinja2 import Template  # pip install jinja2

# ===== Environment & API Keys =====
# OpenAI key (using GITHUB_TOKEN env var in this example)
openai.api_key = os.getenv("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")
if not openai.api_key:
    st.error("OpenAI token not found. Set GITHUB_TOKEN environment variable.")
    st.stop()

# Pinecone configuration\
pinecone_api_key = os.getenv("pcsk_6Ue6nj_Qm5Yu1EXEQDqznQevsGCHpVLpE8dCTMb5bXP52qDJMdqXJN8mdZLscJQN3ipoji")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
if not pinecone_api_key or not pinecone_env:
    st.error("Pinecone API key or environment not set. Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT.")
    st.stop()

pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
pinecone_index_name = "resume-maker"

# Ensure index exists
if pinecone_index_name not in pinecone.list_indexes():
    pinecone.create_index(name=pinecone_index_name, dimension=1536, metric="cosine")
index = pinecone.Index(pinecone_index_name)

# Embedding model
embedding_model = OpenAIEmbeddings()

# ===== Functions =====
def store_uploaded_templates(files):
    """
    Upload multiple .tex templates (from Streamlit uploader) into Pinecone.
    Each file's name is used as the vector ID.
    """
    to_upsert = []
    for file in files:
        raw = file.read().decode("utf-8")
        vec = embedding_model.embed_query(raw)
        to_upsert.append((file.name, vec, {"content": raw}))
    if to_upsert:
        index.upsert(to_upsert)
        return True
    return False


def get_best_template(prompt: str) -> str:
    """
    Query Pinecone for the most relevant LaTeX template given a prompt.
    Returns raw .tex content.
    """
    qv = embedding_model.embed_query(prompt)
    resp = index.query(vector=qv, top_k=1, include_metadata=True)
    return resp['matches'][0]['metadata']['content']


def fill_latex_template(template_tex: str, data: dict) -> str:
    """
    Fill Jinja2-style placeholders in the LaTeX template.
    """
    template = Template(template_tex)
    return template.render(data)


def convert_markdown_to_pdf(markdown_content: str, output_filename: str) -> bool:
    try:
        html = markdown2.markdown(markdown_content)
        css = """
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
            h1 { font-size: 24px; }
            h2 { font-size: 18px; margin-top: 20px; }
        </style>
        """
        html = css + html
        tmp = "temp_resume.html"
        with open(tmp, 'w') as f:
            f.write(html)
        pdfkit.from_file(tmp, output_filename)
        os.remove(tmp)
        return True
    except Exception as e:
        st.error(f"PDF conversion error: {e}")
        return False

# ===== Streamlit UI =====
st.title("AI-Powered Resume Generator with LaTeX Templates")

st.sidebar.header("Upload LaTeX Templates")
uploaded = st.sidebar.file_uploader("Upload .tex files", type="tex", accept_multiple_files=True)
if st.sidebar.button("Upload to Pinecone"):
    if store_uploaded_templates(uploaded):
        st.sidebar.success("Templates uploaded successfully.")
    else:
        st.sidebar.warning("No templates uploaded. Please select .tex files.")

st.sidebar.header("Resume Details")
role = st.sidebar.text_input("Role you're applying for", "Data Engineer")
name = st.sidebar.text_input("Full Name", "John Doe")
email = st.sidebar.text_input("Email", "johndoe@example.com")
mobile = st.sidebar.text_input("Mobile Number", "+1 123 456 7890")
linkedin = st.sidebar.text_input("LinkedIn URL", "https://linkedin.com/in/johndoe")
github = st.sidebar.text_input("GitHub URL", "https://github.com/johndoe")
about = st.sidebar.text_area("About Me", "I am a data engineer with expertise in ETL and cloud.")
education = st.sidebar.text_area("Education", "M.S. Computer Science, XYZ University, 2021")
experience = st.sidebar.text_area("Work Experience", "Software Engineer at Company A: ...")
projects = st.sidebar.text_area("Projects", "1. Predictive Analytics with Python.")
certificates = st.sidebar.text_area("Certificates", "AWS Solutions Architect (2021)")
links = st.sidebar.text_area("Additional Links", "https://portfolio.example.com")

use_latex = st.sidebar.checkbox("Use LaTeX Template from Pinecone")
template_prompt = ""
if use_latex:
    template_prompt = st.sidebar.text_input("Describe desired resume style", "Minimalist professional for software engineer")

if st.sidebar.button("Generate Resume"):
    if use_latex:
        st.info("Generating LaTeX resume...")
        tex_tpl = get_best_template(template_prompt)
        data = {"name": name, "role": role, "email": email, "mobile": mobile,
                "linkedin": linkedin, "github": github, "about": about,
                "education": education, "experience": experience,
                "projects": projects, "certificates": certificates, "links": links}
        filled = fill_latex_template(tex_tpl, data)
        with open("resume.tex", "w") as f:
            f.write(filled)
        st.subheader("Generated LaTeX (.tex)")
        st.code(filled, language="latex")
        st.download_button("Download .tex", filled, file_name="resume.tex")
        # Try local compile
        if os.system("pdflatex resume.tex") == 0:
            with open("resume.pdf", "rb") as pdf:
                st.download_button("Download PDF", pdf, file_name="resume.pdf")
        else:
            st.warning("Local pdflatex compile failed. Upload .tex to Overleaf or compile manually.")
    else:
        st.info("Generating Markdown resume...")
        # Original markdown flow
        prompt = f"""
        Directly start with the resume... (same as your original prompt) """
        response = openai.ChatCompletion.create(
            model="openai/gpt-4.1",
            messages=[{"role": "system", "content": "You are an AI resume assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        md = response.choices[0].message.content
        st.subheader("Markdown Resume")
        st.code(md, language="markdown")
        # Feedback
        fb = openai.ChatCompletion.create(
            model="openai/gpt-4.1",
            messages=[{"role": "system", "content": "You are an expert resume reviewer."},
                      {"role": "user", "content": f"Review resume for {role}:\n{md}"}],
            temperature=0.7
        ).choices[0].message.content
        st.subheader("Feedback")
        st.text(fb)
        # Convert to PDF
        if convert_markdown_to_pdf(md, "resume.pdf"):
            with open("resume.pdf", "rb") as pdf:
                st.download_button("Download PDF", pdf, file_name="resume.pdf")
