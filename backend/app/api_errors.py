from fastapi import HTTPException


class ErrorCode:
    NO_UPLOADED_RESUME = "NO_UPLOADED_RESUME"
    NO_GENERATED_RESUME = "NO_GENERATED_RESUME"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    INVALID_CONTENT_TYPE = "INVALID_CONTENT_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_DOWNLOAD_FORMAT = "INVALID_DOWNLOAD_FORMAT"
    FILE_SAVE_FAILED = "FILE_SAVE_FAILED"
    PARSE_FAILED = "PARSE_FAILED"
    ENHANCE_FAILED = "ENHANCE_FAILED"
    GENERATE_FAILED = "GENERATE_FAILED"


def raise_api_error(status_code: int, code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )
