import json
import os
import re

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TARGET_KEYS = [
    "name",
    "email",
    "phone",
    "links",
    "summary",
    "education",
    "skills",
    "projects",
    "experience",
    "certifications",
    "achievements",
    "responsibilities",
    "extracurricular",
]


def _clean_text(value):
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _normalize_links(value):
    default = {"linkedin": "", "github": "", "portfolio": "", "other": []}
    if not isinstance(value, dict):
        return default

    links = {
        "linkedin": _clean_text(value.get("linkedin", "")),
        "github": _clean_text(value.get("github", "")),
        "portfolio": _clean_text(value.get("portfolio", "")),
        "other": value.get("other", []),
    }

    if not isinstance(links["other"], list):
        links["other"] = []
    links["other"] = [_clean_text(item) for item in links["other"] if _clean_text(item)]
    return links


def _normalize_output(data):
    normalized = {}
    for key in TARGET_KEYS:
        if key == "links":
            normalized[key] = _normalize_links(data.get("links", {}))
        else:
            normalized[key] = _clean_text(data.get(key, ""))
    return normalized


def _extract_json_from_text(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    return None


def enhance_resume(parsed_data):
    safe_data = _normalize_output(parsed_data)
    if not os.getenv("OPENAI_API_KEY"):
        return safe_data

    try:
        prompt = f"""
        Rewrite the following resume content professionally while preserving original facts.
        Do not add new companies, technologies, dates, roles, achievements, links, or qualifications.
        If information is missing, keep it empty.
        Return ONLY valid JSON with exactly these keys:
        {TARGET_KEYS}

        Resume Data:
        {json.dumps(safe_data, indent=2)}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume editor. Improve wording only and never invent facts.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content or "{}"
        parsed_response = _extract_json_from_text(content)
        if not isinstance(parsed_response, dict):
            return safe_data

        merged = safe_data.copy()
        merged.update(parsed_response)
        return _normalize_output(merged)

    except Exception:
        # Safe fallback: return cleaned original data without adding new information.
        return safe_data
