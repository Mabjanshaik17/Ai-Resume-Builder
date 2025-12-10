from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import docx
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import io
import PyPDF2

def extract_text_from_pdf(file_bytes):
    pdf_stream = io.BytesIO(file_bytes)
    reader = PyPDF2.PdfReader(pdf_stream)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text

def parse_details(text):
    name = text.split("\n")[0][:40]

    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\- ]{8,}\d", text)

    skills_keywords = ["python", "java", "c++", "sql", "html", "css",
                       "javascript", "aws", "machine learning",
                       "excel", "communication", "teamwork"]

    skills_found = [s for s in skills_keywords if s.lower() in text.lower()]

    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "skills": skills_found
    }

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    content = file.file.read()

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(content)
    else:
        text = extract_text_from_docx(file.file)

    parsed_info = parse_details(text)

    return {
        "parsed_info": parsed_info,
        "extracted_text": text
    }
