from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

GENERATED_DIR = "generated_resumes"


@router.get("/download-resume/")
def download_resume():
    files = os.listdir(GENERATED_DIR)

    if not files:
        return {"message": "No generated resumes found"}

    latest_file = os.path.join(GENERATED_DIR, files[-1])

    return FileResponse(
        path=latest_file,
        filename=files[-1],
        media_type="application/octet-stream",
    )
