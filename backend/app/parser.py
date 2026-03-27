import os

import PyPDF2
import docx


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


def parse_resume_sections(text):
    data = {
        "name": "",
        "email": "",
        "phone": "",
        "education": "",
        "skills": "",
        "projects": "",
        "experience": "",
    }

    lines = text.split("\n")

    for line in lines:
        if "@" in line and "." in line:
            data["email"] = line
        if any(char.isdigit() for char in line) and len(line) >= 10:
            data["phone"] = line

    text_lower = text.lower()

    if "education" in text_lower:
        data["education"] = "Education section found"

    if "skills" in text_lower:
        data["skills"] = "Skills section found"

    if "project" in text_lower:
        data["projects"] = "Projects section found"

    if "experience" in text_lower:
        data["experience"] = "Experience section found"

    return data
