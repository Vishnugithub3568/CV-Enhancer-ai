from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from app.storage import GENERATED_DIR, cleanup_runtime_files, get_latest_file

router = APIRouter()


@router.get("/download-resume/")
def download_resume(format: str = "pdf"):
    cleanup_runtime_files()

    normalized_format = format.lower().strip()
    if normalized_format not in {"pdf", "docx"}:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'pdf' or 'docx'.")

    latest_file = get_latest_file(GENERATED_DIR, {f".{normalized_format}"})
    if not latest_file:
        return {"message": "No generated resumes found"}

    media_type = "application/pdf" if normalized_format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(
        path=latest_file,
        filename=os.path.basename(latest_file),
        media_type=media_type,
    )
