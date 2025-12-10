import streamlit as st
import requests
import io
from PyPDF2 import PdfReader
import docx

BACKEND_URL = "http://localhost:8000/upload_resume"  # change when deployed

st.title("Upload Resume")

uploaded = st.file_uploader("Choose a resume (.pdf or .docx)", type=["pdf", "docx"])
MAX_MB = 5

def get_preview(file, ext):
    try:
        if ext == "pdf":
            reader = PdfReader(file)
            page = reader.pages[0]
            return page.extract_text()[:1000]
        else:  # docx
            doc = docx.Document(file)
            text = "\n".join(p.text for p in doc.paragraphs)
            return text[:1000]
    except Exception as e:
        return f"Could not generate preview: {e}"

if uploaded:
    ext = uploaded.name.split(".")[-1].lower()
    size_mb = uploaded.size / (1024*1024)
    if size_mb > MAX_MB:
        st.error(f"File too large ({size_mb:.2f} MB). Max is {MAX_MB} MB.")
    else:
        # corruption check: attempt to read preview
        preview = get_preview(io.BytesIO(uploaded.getvalue()), ext)
        if preview.startswith("Could not generate preview"):
            st.error("File appears corrupted or unsupported.")
        else:
            st.success("File seems ok — preview below:")
            st.text(preview)

            if st.button("Upload to server"):
                files = {"file": (uploaded.name, uploaded.getvalue())}
                with st.spinner("Uploading..."):
                    try:
                        resp = requests.post(BACKEND_URL, files=files, timeout=30)
                        if resp.status_code == 200:
                            st.success("Uploaded and parsed successfully!")
                            st.json(resp.json())
                        else:
                            st.error(f"Server error: {resp.status_code} {resp.text}")
                    except Exception as e:
                        st.error(f"Could not reach backend: {e}")
