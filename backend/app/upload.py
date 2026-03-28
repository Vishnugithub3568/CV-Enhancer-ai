import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.storage import (
    SUPPORTED_UPLOAD_EXTENSIONS,
    UPLOAD_DIR,
    cleanup_runtime_files,
    ensure_directories,
    sanitize_filename,
)

router = APIRouter()

ensure_directories()

@router.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    cleanup_runtime_files()

    safe_name = sanitize_filename(file.filename)
    extension = os.path.splitext(safe_name)[1].lower()
    if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Please upload a PDF or DOCX file.",
        )

    file_location = os.path.join(UPLOAD_DIR, safe_name)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.") from exc

    return {
        "filename": safe_name,
        "message": "Resume uploaded successfully",
    }
