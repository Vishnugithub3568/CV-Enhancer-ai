# CV Enhancer AI

## Overview

CV Enhancer AI is an AI-powered resume enhancement platform designed for college students and fresh graduates.
The system allows users to upload their existing resume, automatically extracts the content, improves the resume content using AI, and generates a professional resume in a predefined template.

## Features

* Upload resume (PDF/DOCX)
* Resume content extraction
* AI-based resume content enhancement
* Professional resume generation
* Download generated resume
* Full-stack application (React + FastAPI)

## Tech Stack

**Frontend**

* React
* Axios
* Vite

**Backend**

* FastAPI (Python)
* PyPDF2
* python-docx
* OpenAI API

## System Architecture

Upload Resume -> Parse Resume -> AI Enhancement -> Resume Generation -> Download Resume

## How to Run the Project

### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8003
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Future Improvements

* Multiple resume templates
* Resume scoring system
* ATS compatibility check
* User login system
* Deployment to cloud
