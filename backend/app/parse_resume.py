from fastapi import APIRouter

from app.parser import extract_text, parse_resume_sections
from app.storage import SUPPORTED_UPLOAD_EXTENSIONS, UPLOAD_DIR, cleanup_runtime_files, get_latest_file

router = APIRouter()


@router.get("/parse-resume/")
def parse_resume():
    cleanup_runtime_files()
    latest_file = get_latest_file(UPLOAD_DIR, SUPPORTED_UPLOAD_EXTENSIONS)

    if not latest_file:
        return {"message": "No resumes uploaded"}

    text = extract_text(latest_file)
    parsed_data = parse_resume_sections(text)

    return {
        "raw_text": text,
        "parsed_data": parsed_data,
    }
