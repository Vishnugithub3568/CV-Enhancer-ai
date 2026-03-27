from fastapi import APIRouter
import os
from app.parser import extract_text, parse_resume_sections
from app.ai_enhancer import enhance_resume

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.get("/enhance-resume/")
def enhance_resume_api():
    try:
        files = os.listdir(UPLOAD_DIR)

        if not files:
            return {"message": "No resumes uploaded"}

        latest_file = os.path.join(UPLOAD_DIR, files[-1])

        text = extract_text(latest_file)
        parsed_data = parse_resume_sections(text)

        enhanced_content = enhance_resume(parsed_data)

        return {
            "parsed_data": parsed_data,
            "enhanced_resume": enhanced_content,
        }

    except Exception as e:
        return {"error": str(e)}
