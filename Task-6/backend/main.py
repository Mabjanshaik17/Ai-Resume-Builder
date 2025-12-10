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
