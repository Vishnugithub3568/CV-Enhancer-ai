import os

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

MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(5 * 1024 * 1024)))
ALLOWED_CONTENT_TYPES = {
    ".pdf": {
        "application/pdf",
        "application/x-pdf",
    },
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    },
}

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

    content_type = (file.content_type or "").lower()
    allowed_types = ALLOWED_CONTENT_TYPES.get(extension, set())
    if content_type and content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="File content type does not match the provided extension.",
        )

    file_location = os.path.join(UPLOAD_DIR, safe_name)

    try:
        with open(file_location, "wb") as buffer:
            total_size = 0
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
                    )
                buffer.write(chunk)
    except HTTPException:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.") from exc
    finally:
        file.file.close()

    return {
        "filename": safe_name,
        "message": "Resume uploaded successfully",
    }
