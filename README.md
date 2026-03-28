# CV Enhancer AI

## Overview

CV Enhancer AI is a full-stack AI-powered resume enhancement platform designed for college students and fresh graduates. The system allows users to upload their existing resume in PDF or DOCX format, automatically extracts the content, enhances the resume content using AI, and generates a clean, professional resume in a predefined template that can be downloaded immediately.

The goal of this project is to simplify resume creation and improvement for students while ensuring their resumes are structured, professional, and recruiter-ready.

---

## Features

* Upload resume (PDF / DOCX)
* Automatic resume content extraction
* Resume section parsing (Education, Skills, Projects, Experience)
* AI-based resume content enhancement
* Professional resume generation using template
* Download generated resume (DOCX)
* Full-stack application (React + FastAPI)
* Modular backend architecture
* Incremental development using Git version control

---

## Tech Stack

### Frontend

* React
* Vite
* Axios
* HTML/CSS

### Backend

* FastAPI (Python)
* PyPDF2 (PDF parsing)
* python-docx (DOCX parsing & generation)
* OpenAI API (AI content enhancement)
* Uvicorn (ASGI server)

### Tools & Technologies

* Git & GitHub
* VS Code
* REST APIs
* JSON data processing

---

## System Architecture

```
React Frontend
	↓
Upload Resume
	↓
FastAPI Backend
	↓
Resume Upload Module
	↓
Resume Parsing Module (PDF/DOCX)
	↓
AI Resume Enhancement Module
	↓
Resume Template Generator
	↓
DOCX Resume Generator
	↓
Download Resume API
	↓
User Downloads Resume
```

---

## Project Workflow

1. User uploads resume (PDF or DOCX)
2. Backend extracts text from resume
3. Resume sections are parsed into structured data
4. AI module improves resume content professionally
5. Enhanced content is inserted into resume template
6. New professional resume is generated
7. User downloads the generated resume

---

## Folder Structure

```
CV Enhancer-ai
│
├── .venv/
│
├── frontend/
│   ├── src/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── upload.py
│   │   ├── parser.py
│   │   ├── parse_resume.py
│   │   ├── ai_enhancer.py
│   │   ├── enhance_resume.py
│   │   ├── resume_generator.py
│   │   ├── generate_resume.py
│   │   └── download_resume.py
│   │
│   ├── uploads/
│   ├── generated_resumes/
│   └── ...
│
├── LICENSE
├── README.md
├── requirements.txt
└── .gitignore
```

---

## How to Run the Project

### Backend Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload --port 8003
```

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

Open browser:

```
http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint         | Description                     |
| ------ | ---------------- | ------------------------------- |
| POST   | /upload-resume   | Upload resume file              |
| GET    | /parse-resume    | Parse resume content            |
| GET    | /enhance-resume  | Enhance resume content using AI |
| GET    | /generate-resume | Generate professional resume    |
| GET    | /download-resume | Download generated resume       |

---

## Development Approach

This project was developed using an incremental development approach with Git version control.
Each module such as upload, parsing, AI enhancement, resume generation, and frontend integration was implemented and committed separately before integrating the complete workflow.

---

## Future Improvements

* Multiple resume templates
* Resume scoring system
* ATS compatibility check
* Cover letter generation
* User login and dashboard
* Resume history and storage
* Deployment to cloud
* LinkedIn profile optimizer
* Job recommendation system

---

## Conclusion

CV Enhancer AI demonstrates a full-stack application integrating document processing, AI content enhancement, backend API development, and frontend user interface. The project showcases modular system design, REST API development, file handling, and AI integration in a real-world application scenario.

---

## Author

**U. Vishnu Vardhan**
GitHub: Vishnugithub3568
