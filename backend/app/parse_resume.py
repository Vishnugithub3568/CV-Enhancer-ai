from fastapi import APIRouter, HTTPException

from app.api_errors import ErrorCode, raise_api_error
from app.parser import extract_text, parse_resume_sections
from app.storage import SUPPORTED_UPLOAD_EXTENSIONS, UPLOAD_DIR, cleanup_runtime_files, get_latest_file

router = APIRouter()


@router.get("/parse-resume/")
def parse_resume():
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

        return {
            "raw_text": text,
            "parsed_data": parsed_data,
        }
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise_api_error(
            status_code=500,
            code=ErrorCode.PARSE_FAILED,
            message="Failed to parse the uploaded resume.",
        )
