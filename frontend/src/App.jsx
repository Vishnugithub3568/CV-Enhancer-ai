import { useState } from "react";
import axios from "axios";
import "./App.css";

const STATUS = {
  IDLE: "idle",
  UPLOADING: "uploading",
  GENERATING: "generating",
  SUCCESS: "success",
  ERROR: "error",
};

const ERROR_MESSAGES = {
  UNSUPPORTED_FORMAT: "Unsupported format. Please upload a PDF or DOCX file.",
};

const ALLOWED_UPLOAD_EXTENSIONS = new Set([".pdf", ".docx"]);
const ALLOWED_UPLOAD_MIME_TYPES = new Set([
  "application/pdf",
  "application/x-pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]);

const isAllowedResumeFile = (candidateFile) => {
  if (!candidateFile?.name) {
    return false;
  }

  const normalizedName = candidateFile.name.toLowerCase();
  const extension = normalizedName.slice(normalizedName.lastIndexOf("."));
  if (!ALLOWED_UPLOAD_EXTENSIONS.has(extension)) {
    return false;
  }

  // Browser MIME detection is inconsistent, so extension is primary and MIME is best-effort.
  const fileType = (candidateFile.type || "").toLowerCase();
  return !fileType || ALLOWED_UPLOAD_MIME_TYPES.has(fileType);
};

const getApiErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (detail && typeof detail === "object") {
    return detail.message || fallback;
  }

  return fallback;
};

function App() {
  const [file, setFile] = useState(null);
  const [statusText, setStatusText] = useState("Select a resume file to begin.");
  const [statusType, setStatusType] = useState(STATUS.IDLE);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [hasUploaded, setHasUploaded] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8003";

  const isBusy = isUploading || isGenerating;
  const hasValidSelection = Boolean(file && isAllowedResumeFile(file));

  let currentStep = 1;
  if (hasGenerated) {
    currentStep = 3;
  } else if (hasUploaded || isGenerating) {
    currentStep = 2;
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0] || null;

    if (selectedFile && !isAllowedResumeFile(selectedFile)) {
      setFile(null);
      setHasUploaded(false);
      setHasGenerated(false);
      setStatusType(STATUS.ERROR);
      setStatusText(ERROR_MESSAGES.UNSUPPORTED_FORMAT);
      e.target.value = "";
      return;
    }

    setFile(selectedFile);
    setHasUploaded(false);
    setHasGenerated(false);

    if (selectedFile) {
      setStatusType(STATUS.IDLE);
      setStatusText(`File selected: ${selectedFile.name}`);
    } else {
      setStatusType(STATUS.IDLE);
      setStatusText("Select a resume file to begin.");
    }
  };

  const uploadResume = async () => {
    if (!file) {
      setStatusType(STATUS.ERROR);
      setStatusText("Please select a PDF or DOCX file before uploading.");
      return;
    }

    if (!isAllowedResumeFile(file)) {
      setFile(null);
      setHasUploaded(false);
      setHasGenerated(false);
      setStatusType(STATUS.ERROR);
      setStatusText(ERROR_MESSAGES.UNSUPPORTED_FORMAT);
      return;
    }

    try {
      setIsUploading(true);
      setStatusType(STATUS.UPLOADING);
      setStatusText("Extracting resume details...");

      const formData = new FormData();
      formData.append("file", file);

      await axios.post(`${API_BASE}/upload-resume/`, formData);
      setHasUploaded(true);
      setHasGenerated(false);

      setStatusType(STATUS.SUCCESS);
      setStatusText("Resume uploaded successfully. You can now generate your resume.");
    } catch (error) {
      setStatusType(STATUS.ERROR);
      setStatusText(getApiErrorMessage(error, "Upload failed. Please try again."));
    } finally {
      setIsUploading(false);
    }
  };

  const generateResume = async () => {
    if (!file) {
      setStatusType(STATUS.ERROR);
      setStatusText("Please upload your resume before generating.");
      return;
    }

    if (!hasUploaded) {
      setStatusType(STATUS.ERROR);
      setStatusText("Please upload your selected resume first.");
      return;
    }

    try {
      setIsGenerating(true);
      setStatusType(STATUS.GENERATING);
      setStatusText("AI is enhancing your resume...");

      await axios.get(`${API_BASE}/generate-resume/`);
      setHasGenerated(true);

      setStatusType(STATUS.SUCCESS);
      setStatusText("Resume generated successfully. Download PDF or DOCX below.");
    } catch (error) {
      setStatusType(STATUS.ERROR);
      setStatusText(getApiErrorMessage(error, "Generation failed. Please try again."));
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadResume = async (format) => {
    if (!hasGenerated) {
      setStatusType(STATUS.ERROR);
      setStatusText("Generate your resume before downloading.");
      return;
    }

    try {
      setStatusType(STATUS.IDLE);
      setStatusText(`Preparing ${format.toUpperCase()} download...`);

      const response = await axios.get(`${API_BASE}/download-resume/?format=${format}`, {
        responseType: "blob",
      });

      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `enhanced_resume.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);

      setStatusType(STATUS.SUCCESS);
      setStatusText(`${format.toUpperCase()} downloaded successfully.`);
    } catch (error) {
      setStatusType(STATUS.ERROR);
      setStatusText(getApiErrorMessage(error, `Could not prepare ${format.toUpperCase()}. Please try again.`));
    }
  };

  const steps = ["Upload", "Generate", "Download"];

  return (
    <div className="resume-page">
      <div className="resume-card">
        <header className="hero-block">
          <span className="brand-pill">AI Resume Builder</span>
          <h1>CV Enhancer AI</h1>
          <p className="helper-text">Transform student resumes into cleaner, recruiter-ready versions without changing your original achievements.</p>
        </header>

        <section className="steps-row" aria-label="workflow progress">
          <ol className="stepper" aria-live="polite">
            {steps.map((label, idx) => {
              const stepNumber = idx + 1;
              const stepState = stepNumber < currentStep ? "completed" : stepNumber === currentStep ? "current" : "upcoming";
              return (
                <li key={label} className={`stepper-item step-${stepState}`}>
                  <span className="step-circle" aria-hidden="true">{stepState === "completed" ? "✓" : stepNumber}</span>
                  <span className="step-label">{label}</span>
                </li>
              );
            })}
          </ol>
        </section>

        <section className="uploader-card">
          <p className="file-label">Choose Resume (PDF / DOCX)</p>
          <label className={`upload-dropzone ${isBusy ? "upload-dropzone-disabled" : ""}`} htmlFor="resumeFile">
            <span className="dropzone-icon" aria-hidden="true">☁</span>
            <span className="dropzone-title">{file ? "Change selected file" : "Click to upload resume"}</span>
            <span className="dropzone-subtitle">PDF or DOCX only</span>
            <span className="selected-file">{file ? file.name : "No file selected"}</span>
          </label>
          <input
            id="resumeFile"
            className="hidden-input"
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleFileChange}
            disabled={isBusy}
          />
          <p className="supported-format">Supported formats: PDF, DOCX</p>
        </section>

        <section className="button-grid">
          <button
            className={`primary-btn ${hasUploaded ? "success-btn" : ""}`}
            onClick={uploadResume}
            disabled={isBusy || !hasValidSelection || hasUploaded}
          >
            {isUploading ? "Uploading..." : hasUploaded ? "✓ Uploaded" : "Upload Resume"}
          </button>

          <button
            className={`primary-btn ${hasUploaded && !hasGenerated ? "active-generate-btn" : "secondary-btn"}`}
            onClick={generateResume}
            disabled={isBusy || !hasUploaded || hasGenerated}
          >
            {isGenerating ? "Generating..." : "Generate Resume"}
          </button>

          {hasGenerated && (
            <>
              <button className="secondary-btn" onClick={() => downloadResume("pdf")} disabled={isBusy}>
                Download PDF
              </button>

              <button className="secondary-btn" onClick={() => downloadResume("docx")} disabled={isBusy}>
                Download DOCX
              </button>
            </>
          )}
        </section>

        <div className={`status-box status-${statusType}`} role="status" aria-live="polite">
          {(statusType === STATUS.UPLOADING || statusType === STATUS.GENERATING) && <span className="spinner" aria-hidden="true" />}
          <span>{statusText}</span>
        </div>
      </div>
    </div>
  );
}

export default App;
