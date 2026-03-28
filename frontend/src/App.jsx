import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const API_BASE = "http://127.0.0.1:8003";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadResume = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    await axios.post(`${API_BASE}/upload-resume/`, formData);
    setStatus("Resume uploaded successfully");
  };

  const generateResume = async () => {
    setStatus("Generating resume...");
    await axios.get(`${API_BASE}/generate-resume/`);
    setStatus("Resume generated successfully");
  };

  const downloadResume = () => {
    window.open(`${API_BASE}/download-resume/`);
  };

  return (
    <div style={{ padding: "50px", fontFamily: "Arial" }}>
      <h1>CV Enhancer AI</h1>

      <input type="file" onChange={handleFileChange} />
      <br /><br />

      <button onClick={uploadResume}>Upload Resume</button>
      <br /><br />

      <button onClick={generateResume}>Generate Resume</button>
      <br /><br />

      <button onClick={downloadResume}>Download Resume</button>

      <br /><br />
      <h3>{status}</h3>
    </div>
  );
}

export default App;
