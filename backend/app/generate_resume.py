from fastapi import APIRouter
import os
from app.parser import extract_text, parse_resume_sections
from app.ai_enhancer import enhance_resume
from app.resume_generator import generate_resume

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.get("/generate-resume/")
def generate_resume_api():
    files = os.listdir(UPLOAD_DIR)

    if not files:
        return {"message": "No resumes uploaded"}

    latest_file = os.path.join(UPLOAD_DIR, files[-1])

    text = extract_text(latest_file)
    parsed_data = parse_resume_sections(text)
    enhanced_data = enhance_resume(parsed_data)

    file_path = generate_resume(enhanced_data)

    return {
        "message": "Resume generated successfully",
        "file_path": file_path
    }
