import json
import os
import re

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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
BULLET_SECTION_KEYS = {"projects", "experience", "certifications", "achievements", "responsibilities", "extracurricular"}
LOW_VALUE_TOKENS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to", "with",
    "developed", "built", "created", "using", "worked", "project", "team", "experience", "skills", "summary",
}


def _clean_text(value):
    if not isinstance(value, str):
        return ""

    text = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized_lines = []
    for raw_line in text.split("\n"):
        line = re.sub(r"[\t ]+", " ", raw_line).strip()
        if not line:
            continue
        line = re.sub(r"^[\-*]\s*", "- ", line)
        normalized_lines.append(line)

    return "\n".join(normalized_lines).strip()


def _split_into_items(value):
    text = _clean_text(value)
    if not text:
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) > 1:
        return [re.sub(r"^[\-*]\s*", "", line).strip() for line in lines if line.strip()]

    sentence_chunks = re.split(r"(?<=[.!?])\s+", text)
    items = [chunk.strip() for chunk in sentence_chunks if chunk.strip()]
    return items if items else [text]


def _ensure_bullet_block(value):
    items = _split_into_items(value)
    if not items:
        return ""
    return "\n".join(f"- {item}" for item in items if item)


def _format_summary(value):
    text = _clean_text(value)
    if not text:
        return ""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) >= 2:
        return "\n".join(sentences[:3])
    return text


def _format_skills(value):
    text = _clean_text(value)
    if not text:
        return ""

    if ":" in text or text.startswith("-"):
        return text

    tokens = [token.strip() for token in re.split(r"[,|/]", text) if token.strip()]
    if len(tokens) >= 4:
        return "\n".join(f"- {token}" for token in tokens)

    return text


def _post_format_enhanced_data(data):
    formatted = dict(data)
    formatted["summary"] = _format_summary(formatted.get("summary", ""))
    formatted["skills"] = _format_skills(formatted.get("skills", ""))

    for key in BULLET_SECTION_KEYS:
        formatted[key] = _ensure_bullet_block(formatted.get(key, ""))

    return formatted


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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return safe_data

    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        You are a professional resume writer.

        Rewrite the following resume content so the final resume is clearly more professional, ATS friendly, concise, and impactful.

        Mandatory quality requirements:
        - Improve professional summary quality in 2-3 lines.
        - Use strong action verbs throughout projects and experience.
        - Improve project descriptions with purpose, technologies, and impact.
        - Improve skills section readability and formatting.
        - Keep formatting consistent across all sections.
        - Keep language professional and recruiter-ready.

        Resume structure intent:
        - Name and Contact Information
        - Professional Summary
        - Education
        - Technical Skills
        - Projects
        - Internship / Work Experience
        - Certifications
        - Achievements / Extracurricular Activities
        - Coding Profiles / Links

        Critical factual rules:
        - Do not add fake information.
        - Do not add new companies, technologies, dates, roles, achievements, links, or qualifications.
        - Do not remove important information.
        - Preserve original facts and intent.
        - If information is missing, keep it empty.

        Formatting rules:
        - Use concise bullet points for projects, experience, certifications, achievements, responsibilities, and extracurricular when content exists.
        - Keep summary plain text in 2-3 lines.
        - Keep skills clearly organized with readable groupings when possible.

        Output format:
        - Return ONLY valid JSON.
        - Use exactly these keys (no extra/missing keys):
        {TARGET_KEYS}
        - Map sections as:
          summary -> Summary
          education -> Education
          skills -> Technical Skills
          projects -> Projects
          experience -> Internship / Work Experience
          certifications -> Certifications
          achievements -> Achievements
          responsibilities -> Positions of Responsibility
          extracurricular -> Extracurricular

        Resume Data:
        {json.dumps(safe_data, indent=2)}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume editor. Produce ATS-friendly, concise, impact-focused rewrites using strong action verbs, and never invent facts.",
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
        formatted = _post_format_enhanced_data(normalized)
        guarded = _passes_factual_guardrails(safe_data, formatted)
        return _normalize_output(guarded)

    except Exception:
        # Safe fallback: return cleaned original data without adding new information.
        return safe_data
