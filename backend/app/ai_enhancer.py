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

IMMUTABLE_KEYS = {"name", "email", "phone", "links"}
LOW_VALUE_TOKENS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to", "with",
    "developed", "built", "created", "using", "worked", "project", "team", "experience", "skills", "summary",
}


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


def _tokenize(value):
    if not isinstance(value, str):
        return []
    return re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", value.lower())


def _novel_entity_ratio(source_value, candidate_value):
    source_tokens = set(_tokenize(source_value))
    candidate_tokens = [token for token in _tokenize(candidate_value) if token not in LOW_VALUE_TOKENS]
    if not candidate_tokens:
        return 0.0

    novel = [token for token in candidate_tokens if token not in source_tokens]
    return len(novel) / len(candidate_tokens)


def _passes_factual_guardrails(source_data, candidate_data):
    guarded = dict(candidate_data)

    for key in TARGET_KEYS:
        if key in IMMUTABLE_KEYS:
            guarded[key] = source_data.get(key, guarded.get(key))
            continue

        source_value = source_data.get(key, "")
        candidate_value = guarded.get(key, "")
        if not source_value or not candidate_value:
            continue

        # If too many unfamiliar entity-like tokens appear, keep original field.
        if _novel_entity_ratio(source_value, candidate_value) > 0.35:
            guarded[key] = source_value

    return guarded


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
        normalized = _normalize_output(merged)
        guarded = _passes_factual_guardrails(safe_data, normalized)
        return _normalize_output(guarded)

    except Exception:
        # Safe fallback: return cleaned original data without adding new information.
        return safe_data
