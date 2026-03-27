const { useState } = React;

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      setStatus("Please choose a resume file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setStatus("Uploading...");

      const response = await fetch("http://127.0.0.1:8000/upload-resume/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status ${response.status}`);
      }

      const data = await response.json();
      setStatus(`${data.message} (${data.filename})`);
    } catch (error) {
      setStatus(error.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="card">
      <h1>CV Enhancer AI</h1>
      <p>Upload your resume (PDF/DOCX) to test Day 1 backend integration.</p>

      <form onSubmit={onSubmit}>
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <div>
          <button type="submit" disabled={loading}>
            {loading ? "Uploading..." : "Upload Resume"}
          </button>
        </div>
      </form>

      {status ? <div className="status">{status}</div> : null}
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
