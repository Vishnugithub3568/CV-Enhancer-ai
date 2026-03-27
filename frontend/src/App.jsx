import { useState } from 'react'
import axios from 'axios'

function App() {
  const [file, setFile] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    const formData = new FormData()
    formData.append("file", file)

    await axios.post("http://127.0.0.1:8000/upload-resume/", formData)
    alert("Resume Uploaded Successfully")
  }

  return (
    <div style={{ padding: "50px" }}>
      <h1>CV Enhancer AI</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload Resume</button>
    </div>
  )
}

export default App
