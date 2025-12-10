import re
from PyPDF2 import PdfReader
import docx

# Regex patterns
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\d{10})")

def extract_text_from_file(path):
    """Extract text from PDF or DOCX."""
    if path.lower().endswith(".pdf"):
        try:
            reader = PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except:
            return ""
    elif path.lower().endswith(".docx"):
        try:
            document = docx.Document(path)
            return "\n".join(p.text for p in document.paragraphs)
        except:
            return ""
    return ""

def parse_basic_info(text):
    """Extract name, email, phone, skills from text."""
    emails = EMAIL_RE.findall(text)
    phones = [p[1] for p in PHONE_RE.findall(text)]

    # Extract name (first valid line)
    name = ""
    for line in text.splitlines():
        clean = line.strip()
        if clean and "@" not in clean and not PHONE_RE.search(clean):
            name = clean
            break

    # Skills list (add more if you want)
    SKILLS = [
        "python", "java", "c++", "sql", "excel", "html", "css",
        "machine learning", "data analysis", "django", "flask"
    ]
    lower = text.lower()
    matched_skills = [s for s in SKILLS if s in lower]

    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "skills": matched_skills
    }
