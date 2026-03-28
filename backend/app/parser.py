import re

import docx
import PyPDF2


SECTION_ALIASES = {
    "summary": {"summary", "career objective", "objective", "profile"},
    "education": {"education", "academic background"},
    "skills": {"skills", "technical skills", "core skills"},
    "projects": {"projects", "academic projects", "personal projects"},
    "experience": {"experience", "work experience", "internship", "internships"},
    "certifications": {"certifications", "certificates"},
    "achievements": {"achievements", "awards"},
    "responsibilities": {"positions of responsibility", "leadership", "responsibility"},
    "extracurricular": {"extra-curricular", "extracurricular", "activities"},
}


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format"


def _normalize_heading(line):
    return re.sub(r"[^a-z ]", "", line.lower()).strip()


def _find_section(line):
    normalized = _normalize_heading(line.replace(":", " "))
    if not normalized:
        return None

    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if (
                normalized == alias
                or normalized.startswith(alias + " ")
                or normalized.endswith(" " + alias)
                or f" {alias} " in f" {normalized} "
            ):
                return section
    return None


def _first_non_empty_line(lines):
    for line in lines:
        if line.strip():
            return line.strip()
    return ""


def _extract_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_phone(text):
    matches = re.findall(r"(?:\+?\d[\d\s\-()]{8,}\d)", text)
    if not matches:
        return ""

    cleaned = []
    for raw in matches:
        normalized = re.sub(r"[^\d+\-() ]", "", raw)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        normalized = normalized.lstrip(") ")
        cleaned.append(normalized)
    return cleaned[0]


def _extract_links(text):
    links = re.findall(r"(?:https?://\S+|www\.\S+|(?:linkedin|github)\.com/\S+)", text, flags=re.IGNORECASE)

    link_data = {
        "linkedin": "",
        "github": "",
        "portfolio": "",
        "other": [],
    }

    for link in links:
        cleaned = link.rstrip(",.;)")
        lower = cleaned.lower()
        if "linkedin" in lower and not link_data["linkedin"]:
            link_data["linkedin"] = cleaned
        elif "github" in lower and not link_data["github"]:
            link_data["github"] = cleaned
        elif ("portfolio" in lower or "behance" in lower or "dribbble" in lower) and not link_data["portfolio"]:
            link_data["portfolio"] = cleaned
        elif cleaned not in link_data["other"]:
            link_data["other"].append(cleaned)

    return link_data


def _is_contact_or_link_line(line):
    lower = line.lower()
    return (
        "@" in line
        or "linkedin" in lower
        or "github" in lower
        or "http://" in lower
        or "https://" in lower
        or "www." in lower
    )


def _looks_like_name(line):
    candidate = re.sub(r"[^A-Za-z\s]", "", line).strip()
    if not candidate:
        return False
    words = [w for w in candidate.split() if w]
    if len(words) < 2 or len(words) > 4:
        return False
    if any(w.lower() in {"resume", "curriculum", "vitae", "contact"} for w in words):
        return False
    return all(w[0].isupper() for w in words if w)


def _extract_name(lines):
    for line in lines[:8]:
        if _is_contact_or_link_line(line):
            continue
        if re.search(r"\d", line):
            continue
        if _looks_like_name(line):
            return line.strip()

    fallback = _first_non_empty_line(lines)
    if _is_contact_or_link_line(fallback) or re.search(r"\d", fallback):
        return ""
    return fallback


def _fallback_section_text(lines, keywords):
    collected = []
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            collected.append(line)
    return "\n".join(collected[:5]).strip()


def parse_resume_sections(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = {key: [] for key in SECTION_ALIASES}
    preamble = []
    current_section = None

    for line in lines:
        matched_section = _find_section(line)
        if matched_section:
            current_section = matched_section
            continue

        if current_section:
            sections[current_section].append(line)
        else:
            preamble.append(line)

    name_candidate = _extract_name(lines)

    summary_text = "\n".join(sections["summary"]).strip()
    if not summary_text:
        summary_candidates = []
        for line in preamble:
            if _is_contact_or_link_line(line):
                continue
            if re.search(r"\+?\d", line):
                continue
            if len(line.split()) < 6:
                continue
            summary_candidates.append(line)
        summary_text = " ".join(summary_candidates[:2]).strip()

    education_text = "\n".join(sections["education"]).strip()
    if not education_text:
        education_text = _fallback_section_text(lines, ["bachelor", "master", "university", "college", "cgpa", "gpa"])

    skills_text = "\n".join(sections["skills"]).strip()
    if not skills_text:
        skills_text = _fallback_section_text(lines, ["python", "java", "sql", "react", "fastapi", "skills"])

    projects_text = "\n".join(sections["projects"]).strip()
    if not projects_text:
        projects_text = _fallback_section_text(lines, ["project", "developed", "built", "implemented"])

    experience_text = "\n".join(sections["experience"]).strip()
    if not experience_text:
        experience_text = _fallback_section_text(lines, ["experience", "intern", "worked", "developer", "engineer"])

    data = {
        "name": name_candidate,
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "links": _extract_links(text),
        "summary": summary_text,
        "education": education_text,
        "skills": skills_text,
        "projects": projects_text,
        "experience": experience_text,
        "certifications": "\n".join(sections["certifications"]).strip(),
        "achievements": "\n".join(sections["achievements"]).strip(),
        "responsibilities": "\n".join(sections["responsibilities"]).strip(),
        "extracurricular": "\n".join(sections["extracurricular"]).strip(),
    }

    return data
