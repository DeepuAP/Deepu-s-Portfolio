import streamlit as st
import streamlit.components.v1 as components
import base64
import os

from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Loga Deepak | AI Architect", page_icon="⚡")

# Load environment variables
load_dotenv()

# --- HIDE STREAMLIT HEADER/FOOTER ---
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none; }
    .stApp { 
        overflow: hidden; 
        background-color: #ffffff !important; 
    }
    .block-container { 
        padding: 0 !important; 
        max-width: 100% !important; 
        margin: 0 !important;
    }
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 999999 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

def load_frontend():
    """Reads index.html, injects Recruiter Mode, Profile Image, and API Keys."""
    
    base_dir = os.path.dirname(__file__)
    html_path = os.path.join(base_dir, "index.html")
    recruiter_path = os.path.join(base_dir, "recruiter.html")
    image_path = os.path.join(base_dir, "static", "assets", "images", "Deepu.JPG")
    # For file existence check only 
    resume_pdf_path = os.path.join(base_dir, "static", "assets", "PDF", "RESUME_LOGA DEEPAK .pdf")
    
    # 1. Read Main HTML
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        st.error("Error: index.html not found!")
        return None

    # 2. Read Recruiter HTML
    try:
        with open(recruiter_path, "r", encoding="utf-8") as f:
            recruiter_content = f.read()
    except FileNotFoundError:
        recruiter_content = ""
        
    # 3. Inject Recruiter Content
    html_content = html_content.replace('{{RECRUITER_MODE_HTML}}', recruiter_content)

    # 4. Inject Profile Image
    try:
        with open(image_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        html_content = html_content.replace('{{PROFILE_IMG_B64}}', b64_string)
    except FileNotFoundError:
        pass 
    
    # 5. Inject Resume PDF (Base64 Encoded)
    # File is at static/resume.pdf
    resume_pdf_path = os.path.join(base_dir, "static", "assets", "PDF", "RESUME_LOGA DEEPAK.pdf")
    
    if os.path.exists(resume_pdf_path):
        try:
            with open(resume_pdf_path, "rb") as pdf_file:
                resume_b64 = base64.b64encode(pdf_file.read()).decode()
                resume_data_uri = f"data:application/pdf;base64,{resume_b64}"
                html_content = html_content.replace('{{RESUME_PDF}}', resume_data_uri)
                print(f"SUCCESS: Resume injected from {resume_pdf_path}")
        except Exception as e:
            print(f"ERROR reading resume pdf: {e}")
            html_content = html_content.replace('{{RESUME_PDF}}', '#')
    else:
        print(f"⚠️ WARNING: Resume PDF not found at {resume_pdf_path}")
        # Remove the download attribute so it doesn't download the HTML page as a PDF
        html_content = html_content.replace('download="Loga_Deepak_Resume.pdf"', 'onclick="alert(\'Resume file not found on server.\')"', 1)
        html_content = html_content.replace('{{RESUME_PDF}}', '#')
        
    # --- INTELLIGENT KEY LOADING ---
    # 1. Try loading from Streamlit Cloud Secrets (Production)
    try:
        if hasattr(st, "secrets"):
            gemini_key = st.secrets.get("GEMINI_API_KEY", "")
            deepgram_key = st.secrets.get("DEEPGRAM_API_KEY", "")
        else:
            gemini_key = ""
            deepgram_key = ""
    except (StreamlitSecretNotFoundError, FileNotFoundError):
        # Graceful fallback if secrets file is missing or corrupt
        gemini_key = ""
        deepgram_key = ""

    # 2. If not found in Secrets, try local .env (Development)
    if not gemini_key:
        gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not deepgram_key:
        deepgram_key = os.getenv("DEEPGRAM_API_KEY", "")

    # 3. Inject into HTML
    if not gemini_key:
        print("⚠️ WARNING: GEMINI_API_KEY not found!")
    
    html_content = html_content.replace('{{GEMINI_API_KEY}}', gemini_key)
    html_content = html_content.replace('{{DEEPGRAM_API_KEY}}', deepgram_key)
    
    return html_content

# --- MAIN APP LOGIC ---
if __name__ == "__main__":
    frontend_code = load_frontend()
    if frontend_code:
        components.html(frontend_code, height=1000, scrolling=True)
