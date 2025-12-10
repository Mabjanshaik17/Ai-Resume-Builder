from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
import io
import re

import PyPDF2
import docx

# -------------------------------
# App initialization
# -------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Upload folder
# -------------------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------
# Text extraction helpers
# -------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf_stream = io.BytesIO(file_bytes)
    reader = PyPDF2.PdfReader(pdf_stream)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


def extract_text_from_docx(file_obj) -> str:
    doc = docx.Document(file_obj)
    return "\n".join([p.text for p in doc.paragraphs])


# -------------------------------
# Resume parsing logic
# -------------------------------
def parse_basic_info(text: str) -> dict:
    name = text.split("\n")[0][:40]

    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\- ]{8,}\d", text)

    skills_keywords = [
        "python", "java", "c++", "sql", "html", "css",
        "javascript", "aws", "machine learning",
        "excel", "communication", "teamwork"
    ]

    skills_found = [s for s in skills_keywords if s.lower() in text.lower()]

    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "skills": skills_found
    }

# -------------------------------
# Health check
# -------------------------------
@app.get("/")
def home():
    return {"message": "Resume Parser Backend Running"}

# -------------------------------
# Upload + parse endpoint
# -------------------------------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    unique_id = uuid.uuid4().hex
    save_name = f"{unique_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, save_name)

    # Read file bytes
    content = await file.read()

    # Save file to disk
    with open(save_path, "wb") as f:
        f.write(content)

    # Extract text
    if file.filename.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(content)
    elif file.filename.lower().endswith(".docx"):
        extracted_text = extract_text_from_docx(io.BytesIO(content))
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Unsupported file type"}
        )

    # Parse details
    parsed_info = parse_basic_info(extracted_text)

    # Response
    return JSONResponse(content={
        "file_saved_as": save_name,
        "parsed_info": parsed_info,
        "extracted_text": extracted_text[:2000]
    })
