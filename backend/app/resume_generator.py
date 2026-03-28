import os
from typing import Optional

from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.storage import GENERATED_DIR, ensure_directories

ensure_directories()


SECTION_ORDER = [
    ("summary", "Professional Summary"),
    ("education", "Education"),
    ("skills", "Technical Skills"),
    ("projects", "Projects"),
    ("experience", "Internship / Work Experience"),
    ("certifications", "Certifications"),
    ("achievements", "Achievements"),
    ("responsibilities", "Positions of Responsibility"),
    ("extracurricular", "Extra-Curricular Activities"),
]


def _safe_text(value) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _build_contact_line(data: dict) -> str:
    parts = []
    for key in ("email", "phone"):
        value = _safe_text(data.get(key, ""))
        if value:
            parts.append(value)

    links = data.get("links", {}) if isinstance(data.get("links"), dict) else {}
    for key in ("linkedin", "github", "portfolio"):
        value = _safe_text(links.get(key, ""))
        if value:
            parts.append(value)

    other_links = links.get("other", []) if isinstance(links.get("other"), list) else []
    for item in other_links:
        value = _safe_text(item)
        if value:
            parts.append(value)

    return " | ".join(parts)


def _create_docx(data: dict, file_path: str) -> None:
    doc = Document()

    name = _safe_text(data.get("name", "")) or "Professional Resume"
    doc.add_heading(name, level=0)

    contact = _build_contact_line(data)
    if contact:
        doc.add_paragraph(contact)

    for key, title in SECTION_ORDER:
        value = _safe_text(data.get(key, ""))
        if not value:
            continue
        doc.add_heading(title, level=1)
        doc.add_paragraph(value)

    doc.save(file_path)


def _create_pdf(data: dict, file_path: str) -> None:
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#123A7A"),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=6,
    )

    doc = SimpleDocTemplate(file_path, pagesize=LETTER, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    name = _safe_text(data.get("name", "")) or "Professional Resume"
    story.append(Paragraph(name, styles["Title"]))

    contact = _build_contact_line(data)
    if contact:
        story.append(Paragraph(contact, body_style))

    story.append(Spacer(1, 8))

    for key, title in SECTION_ORDER:
        value = _safe_text(data.get(key, ""))
        if not value:
            continue
        story.append(Paragraph(title, heading_style))
        for line in value.split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), body_style))

    doc.build(story)


def generate_resume(enhanced_data: dict, base_filename: str = "generated_resume", include_docx: bool = True) -> dict:
    pdf_path = os.path.join(GENERATED_DIR, f"{base_filename}.pdf")
    _create_pdf(enhanced_data, pdf_path)

    docx_path: Optional[str] = None
    if include_docx:
        docx_path = os.path.join(GENERATED_DIR, f"{base_filename}.docx")
        _create_docx(enhanced_data, docx_path)

    return {
        "pdf_path": pdf_path,
        "docx_path": docx_path,
    }
