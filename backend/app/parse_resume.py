import os

from fastapi import APIRouter

from app.parser import extract_text, parse_resume_sections

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


@router.get("/parse-resume/")
def parse_resume():
    files = os.listdir(UPLOAD_DIR)

    if not files:
        return {"message": "No resumes uploaded"}

    latest_file = os.path.join(UPLOAD_DIR, files[-1])

    text = extract_text(latest_file)
    parsed_data = parse_resume_sections(text)

    return {
        "raw_text": text,
        "parsed_data": parsed_data,
    }
