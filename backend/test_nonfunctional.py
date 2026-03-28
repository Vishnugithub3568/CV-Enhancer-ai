import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8003"
ROUTES = [
    "/parse-resume/",
    "/enhance-resume/",
    "/generate-resume/",
]
ITERATIONS = 5


def call_get(path: str):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=30) as response:
            body = response.read().decode("utf-8", errors="ignore")
            elapsed = (time.perf_counter() - start) * 1000
            return {
                "path": path,
                "status": response.status,
                "elapsed_ms": round(elapsed, 2),
                "body": body,
            }
    except urllib.error.HTTPError as exc:
        elapsed = (time.perf_counter() - start) * 1000
        body = exc.read().decode("utf-8", errors="ignore")
        return {
            "path": path,
            "status": exc.code,
            "elapsed_ms": round(elapsed, 2),
            "body": body,
        }
    except Exception as exc:
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "path": path,
            "status": 0,
            "elapsed_ms": round(elapsed, 2),
            "body": str(exc),
        }


def run_check():
    report = {"iterations": ITERATIONS, "results": []}

    for path in ROUTES:
        latencies = []
        statuses = []

        for _ in range(ITERATIONS):
            result = call_get(path)
            latencies.append(result["elapsed_ms"])
            statuses.append(result["status"])

        report["results"].append(
            {
                "path": path,
                "status_set": sorted(set(statuses)),
                "avg_ms": round(sum(latencies) / len(latencies), 2),
                "min_ms": round(min(latencies), 2),
                "max_ms": round(max(latencies), 2),
            }
        )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run_check()
