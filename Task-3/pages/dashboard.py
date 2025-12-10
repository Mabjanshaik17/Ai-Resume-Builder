import streamlit as st
import sys
import os

# -------------------------------
# Import backend functions
# -------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "../../Task-6/backend"))
sys.path.append(backend_path)

from parser import parse_resume   # Your resume parser


# -----------------------------------
# Dashboard UI
# -----------------------------------
st.title("User Dashboard")

# Get the logged-in user (stored in session_state)
if "user_email" not in st.session_state:
    st.error("You are not logged in. Please go back to Login Page.")
    st.stop()

user_email = st.session_state["user_email"]
user_data = get_user_details(user_email)

st.subheader(f"Welcome, {user_data.get('name', 'User')} 👋")
st.write(f"**Email:** {user_email}")

# -----------------------------------
# Resume Upload Section
# -----------------------------------
st.markdown("---")
st.header("Upload Your Resume")

uploaded_file = st.file_uploader("Upload Resume (PDF / DOCX)", type=["pdf", "docx"])

if uploaded_file:
    with open("temp_resume", "wb") as f:
        f.write(uploaded_file.read())

    st.success("Resume uploaded successfully! Parsing now...")

    # Parse resume
    parsed_text = parse_resume("temp_resume")

    # Store in session for later use
    st.session_state["parsed_resume"] = parsed_text

    st.subheader("📄 Extracted Resume Text")
    st.text_area("Parsed Content", parsed_text, height=400)

    os.remove("temp_resume")  # delete temporary file
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
from parse_utils import extract_text_from_file, parse_basic_info

# Initialize app
app = FastAPI()

# Folder to save uploaded resumes
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Resume Parser Backend Running"}

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    # Create unique filename
    unique_id = uuid.uuid4().hex
    save_name = f"{unique_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, save_name)

    # Save file
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    extracted_text = extract_text_from_file(save_path)

    # Parse details
    parsed_info = parse_basic_info(extracted_text)

    # Send response
    response = {
        "file_saved_as": save_name,
        "parsed_info": parsed_info,
        "extracted_text": extracted_text[:2000]  # send preview
    }

    return JSONResponse(content=response)
