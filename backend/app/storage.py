import os
import re
import time
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
GENERATED_DIR = os.path.join(BASE_DIR, "generated_resumes")

SUPPORTED_UPLOAD_EXTENSIONS = {".pdf", ".docx"}
RETENTION_SECONDS = int(os.getenv("FILE_RETENTION_SECONDS", "3600"))


def ensure_directories() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(GENERATED_DIR, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    name = os.path.basename(filename or "")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or f"resume_{int(time.time())}.docx"


def cleanup_old_files(directory: str, ttl_seconds: Optional[int] = None) -> int:
    if not os.path.isdir(directory):
        return 0

    ttl = RETENTION_SECONDS if ttl_seconds is None else ttl_seconds
    now = time.time()
    removed = 0

    for item in os.listdir(directory):
        if item.startswith(".git"):
            continue

        path = os.path.join(directory, item)
        if not os.path.isfile(path):
            continue

        try:
            if now - os.path.getmtime(path) > ttl:
                os.remove(path)
                removed += 1
        except OSError:
            continue

    return removed


def cleanup_runtime_files() -> int:
    removed_uploads = cleanup_old_files(UPLOAD_DIR)
    removed_generated = cleanup_old_files(GENERATED_DIR)
    return removed_uploads + removed_generated


def get_latest_file(directory: str, extensions: Optional[set[str]] = None) -> Optional[str]:
    if not os.path.isdir(directory):
        return None

    files = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            continue
        if extensions:
            ext = os.path.splitext(name)[1].lower()
            if ext not in extensions:
                continue
        files.append(path)

    if not files:
        return None

    return max(files, key=os.path.getmtime)
