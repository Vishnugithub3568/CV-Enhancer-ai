from fastapi.testclient import TestClient

from app.main import app


def _assert_error_code(response, expected_status, expected_code):
    assert response.status_code == expected_status, response.text

    payload = response.json()
    detail = payload.get("detail", {})
    assert isinstance(detail, dict), payload
    assert detail.get("code") == expected_code, payload

    request_id_header = response.headers.get("X-Request-ID")
    request_id_body = payload.get("request_id")
    assert request_id_header, payload
    assert request_id_body, payload
    assert request_id_header == request_id_body, payload


def run():
    client = TestClient(app)

    upload_response = client.post(
        "/upload-resume/",
        files={"file": ("resume.txt", b"invalid content", "text/plain")},
    )
    _assert_error_code(upload_response, 400, "UNSUPPORTED_FORMAT")

    download_response = client.get("/download-resume/?format=txt")
    _assert_error_code(download_response, 400, "INVALID_DOWNLOAD_FORMAT")

    print("PASS: error-code integration checks completed.")


if __name__ == "__main__":
    run()
