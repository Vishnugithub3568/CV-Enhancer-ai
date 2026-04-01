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
STRONG_ACTION_VERBS = {
    "developed", "designed", "implemented", "built", "created", "integrated",
    "automated", "optimized", "analyzed", "led", "collaborated", "organized", "managed",
}
WEAK_START_PATTERNS = {
    "worked on": "Developed",
    "helped in": "Contributed to",
    "did project": "Implemented",
    "made": "Built",
}

SKILL_CATEGORY_KEYWORDS = {
    "Programming Languages": {"python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", "php", "kotlin", "swift", "sql"},
    "Web Development": {"react", "vite", "html", "css", "javascript", "typescript", "node", "fastapi", "django", "flask", "bootstrap", "tailwind", "rest", "api"},
    "Databases": {"mysql", "postgresql", "postgres", "mongodb", "sqlite", "oracle", "firebase", "redis"},
    "Tools & Platforms": {"git", "github", "docker", "postman", "linux", "jira", "figma", "vercel", "render", "aws", "azure", "gcp"},
    "Machine Learning / Data Science": {"machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "opencv", "matplotlib"},
    "Operating Systems": {"windows", "linux", "ubuntu", "macos"},
    "Soft Skills": {"communication", "teamwork", "leadership", "problem solving", "adaptability", "time management", "collaboration"},
}

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

    strengthened = [_strengthen_action_verb(item) for item in items if item]
    return "\n".join(f"- {item}" for item in strengthened if item)


def _format_summary(value):
    text = _clean_text(value)
    if not text:
        return ""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) >= 2:
        return "\n".join(sentences[:3])
    return text


def _normalize_skill_token(token):
    cleaned = token.strip(" .;:-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _skill_bucket_for(token):
    lower = token.lower()
    for category, keywords in SKILL_CATEGORY_KEYWORDS.items():
        if lower in keywords:
            return category
        if any(k in lower for k in keywords if " " in k):
            return category
    return None


def _extract_skill_tokens(text):
    parts = re.split(r"[,|/]", text)
    tokens = []
    for part in parts:
        token = _normalize_skill_token(part)
        if token:
            tokens.append(token)
    return tokens


def _format_skills(value):
    text = _clean_text(value)
    if not text:
        return ""

    tokens = []
    for line in text.split("\n"):
        line_clean = line.strip()
        if not line_clean:
            continue
        if line_clean.startswith("- "):
            line_clean = line_clean[2:].strip()
        if ":" in line_clean:
            _, rhs = line_clean.split(":", 1)
            tokens.extend(_extract_skill_tokens(rhs))
        else:
            tokens.extend(_extract_skill_tokens(line_clean))

    if not tokens:
        return text

    grouped = {category: [] for category in SKILL_CATEGORY_KEYWORDS}
    uncategorized = []
    seen = set()

    for raw_token in tokens:
        token = _normalize_skill_token(raw_token)
        if not token:
            continue
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)

        bucket = _skill_bucket_for(token)
        if bucket:
            grouped[bucket].append(token)
        else:
            uncategorized.append(token)

    lines = []
    for category in [
        "Programming Languages",
        "Web Development",
        "Databases",
        "Tools & Platforms",
        "Machine Learning / Data Science",
        "Operating Systems",
        "Soft Skills",
    ]:
        if grouped[category]:
            lines.append(f"{category}: {', '.join(grouped[category])}")

    if uncategorized:
        lines.append(f"Additional Skills: {', '.join(uncategorized)}")

    return "\n".join(lines) if lines else text


def _infer_career_interest(skills_text):
    skills = skills_text.lower()
    if any(k in skills for k in ["react", "node", "fastapi", "django", "flask", "web"]):
        return "software development and full stack engineering"
    if any(k in skills for k in ["tensorflow", "pytorch", "machine learning", "opencv", "data"]):
        return "machine learning and data-driven engineering roles"
    return "software development roles"


def _build_fallback_summary(data):
    education = _clean_text(data.get("education", ""))
    skills = _clean_text(data.get("skills", ""))
    projects = _clean_text(data.get("projects", ""))

    education_line = education.split("\n")[0] if education else "Computer Science undergraduate"
    skills_tokens = _extract_skill_tokens(skills.replace("\n", ", "))
    top_skills = ", ".join(skills_tokens[:4]) if skills_tokens else "Python, Java, and web technologies"
    career_interest = _infer_career_interest(skills)

    project_phrase = ""
    if projects:
        project_phrase = " Experienced in building academic and personal projects with practical implementation focus."

    return (
        f"{education_line} with a strong foundation in {top_skills}."
        f"{project_phrase}"
        f" Seeking opportunities in {career_interest} to apply technical and problem-solving skills."
    ).strip()


def _strengthen_action_verb(item):
    text = _clean_text(item)
    if not text:
        return ""

    lower = text.lower()
    for weak_start, replacement in WEAK_START_PATTERNS.items():
        if lower.startswith(weak_start):
            suffix = text[len(weak_start):].strip(" .")
            return f"{replacement} {suffix}".strip()

    first_word_match = re.match(r"([A-Za-z]+)", text)
    if first_word_match and first_word_match.group(1).lower() in STRONG_ACTION_VERBS:
        return text

    return f"Implemented {text[0].lower() + text[1:] if len(text) > 1 else text.lower()}"


def _post_format_enhanced_data(data):
    formatted = dict(data)
    summary_value = _format_summary(formatted.get("summary", ""))
    if not summary_value:
        summary_value = _format_summary(_build_fallback_summary(formatted))
    formatted["summary"] = summary_value
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
        return _normalize_output(_post_format_enhanced_data(safe_data))

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
        - Achievements / Extracurricular Activities
        - Certifications
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
        - Group skills in categories where possible: Programming Languages, Web Development, Databases, Tools & Platforms, Machine Learning / Data Science, Operating Systems, Soft Skills.
        - Prefer strong action verbs: Developed, Designed, Implemented, Built, Created, Integrated, Automated, Optimized, Led, Organized, Collaborated, Managed.
        - Avoid weak starts like: Worked on, Did project, Helped in, Made.

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
