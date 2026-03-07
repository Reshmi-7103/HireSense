import { useState } from "react";
import Navbar from "../components/NavbarLogin";
import "../styles/ResumeAnalyzer.css";

export default function ResumeAnalyzer() {

  const user = JSON.parse(localStorage.getItem("user"));

  const [role, setRole] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // HANDLE FILE

  function handleFileChange(e) {
    const selected = e.target.files[0];

    if (selected && selected.type !== "application/pdf") {
      alert("Only PDF Resume Allowed!");
      return;
    }

    setFile(selected);
  }

  // ANALYZE

  async function handleAnalyze() {

    if (!user || !user._id) {
      alert("Please Login First");
      return;
    }

    if (!file || !role.trim()) {
      alert("Enter Role & Upload Resume");
      return;
    }

    setLoading(true);
    setResult(null);

    try {

      const formData = new FormData();
      formData.append("resume", file);
      formData.append("role", role);

      const res = await fetch(
        `http://127.0.0.1:5000/api/analyze-resume/${user._id}`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await res.json();

      if (data.success) {
        setResult(data.analysis);
      } else {
        alert("Analysis Failed");
      }

    } catch (err) {
      console.log(err);
      alert("Server Error");
    }

    setLoading(false);
  }

  // UI

  return (

    <div className="resume-page">

      <Navbar />

      <div className="resume-wrapper">

        <div className="resume-card">

          <h1 className="title">Resume Analyzer 🤖</h1>

          <input
            className="role-input"
            placeholder="Enter Target Job Role"
            value={role}
            onChange={e => setRole(e.target.value)}
          />

          <input
            className="file-input"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
          />

          <button
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Resume"}
          </button>

          {result && (

            <div className="result-box">

              <h3>ATS Score</h3>

              <div className="progress">
                <div
                  className="progress-bar"
                  style={{ width: `${result.ats_score}%` }}
                >
                  {result.ats_score}%
                </div>
              </div>

              <p>Grammar Errors: {result.grammar_errors}</p>
              <p>Role Match: {result.role_match}</p>

              <div className="skills">
                {result.skills.map((s, i) => (
                  <span key={i} className="skill-chip">{s}</span>
                ))}
              </div>

              {/* 🔥 RECOMMENDED JOBS */}

              {result.recommended_jobs && result.recommended_jobs.length > 0 && (

                <>
                  <h3 style={{marginTop:"20px"}}>Recommended Jobs</h3>

                  <div className="skills">
                    {result.recommended_jobs.map((j, i) => (
                      <span key={i} className="skill-chip">{j}</span>
                    ))}
                  </div>
                </>

              )}

            </div>

          )}

        </div>

      </div>

    </div>
  )
}