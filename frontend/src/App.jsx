import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);

  const API_BASE = "http://127.0.0.1:8003";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadResume = async () => {
    const formData = new FormData();
    formData.append("file", file);

    await axios.post(`${API_BASE}/upload-resume/`, formData);
    alert("Resume Uploaded");
  };

  const generateResume = async () => {
    const res = await axios.get(`${API_BASE}/generate-resume/`);
    alert("Resume Generated: " + res.data.file_path);
  };

  return (
    <div style={{ padding: "50px" }}>
      <h1>CV Enhancer AI</h1>
      <input type="file" onChange={handleFileChange} />
      <br /><br />

      <button onClick={uploadResume}>Upload Resume</button>
      <br /><br />

      <button onClick={generateResume}>Generate Resume</button>
    </div>
  );
}

export default App;
