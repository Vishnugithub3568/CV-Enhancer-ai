from docx import Document
import os

GENERATED_DIR = "generated_resumes"

if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR)

def generate_resume(enhanced_data, filename="generated_resume.docx"):
    doc = Document()

    doc.add_heading("Professional Resume", level=0)

    doc.add_heading("Education", level=1)
    doc.add_paragraph(enhanced_data.get("education", ""))

    doc.add_heading("Skills", level=1)
    doc.add_paragraph(enhanced_data.get("skills", ""))

    doc.add_heading("Projects", level=1)
    doc.add_paragraph(enhanced_data.get("projects", ""))

    doc.add_heading("Experience", level=1)
    doc.add_paragraph(enhanced_data.get("experience", ""))

    file_path = os.path.join(GENERATED_DIR, filename)
    doc.save(file_path)

    return file_path
