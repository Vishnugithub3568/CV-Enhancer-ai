import time

from fastapi import APIRouter, HTTPException

from app.api_errors import ErrorCode, raise_api_error
from app.parser import extract_text, parse_resume_sections
from app.ai_enhancer import enhance_resume
from app.resume_generator import generate_resume
from app.storage import SUPPORTED_UPLOAD_EXTENSIONS, UPLOAD_DIR, cleanup_runtime_files, get_latest_file

router = APIRouter()

@router.get("/generate-resume/")
def generate_resume_api():
    try:
        cleanup_runtime_files()
        latest_file = get_latest_file(UPLOAD_DIR, SUPPORTED_UPLOAD_EXTENSIONS)

        if not latest_file:
            raise_api_error(
                status_code=404,
                code=ErrorCode.NO_UPLOADED_RESUME,
                message="No resumes uploaded.",
            )

        text = extract_text(latest_file)
        parsed_data = parse_resume_sections(text)
        enhanced_data = enhance_resume(parsed_data)

        generated = generate_resume(
            enhanced_data,
            base_filename=f"generated_resume_{int(time.time())}",
            include_docx=True,
        )

        return {
            "message": "Resume generated successfully",
            "primary_file": generated.get("pdf_path"),
            "pdf_path": generated.get("pdf_path"),
            "docx_path": generated.get("docx_path"),
        }
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise_api_error(
            status_code=500,
            code=ErrorCode.GENERATE_FAILED,
            message="Failed to generate resume output files.",
        )
