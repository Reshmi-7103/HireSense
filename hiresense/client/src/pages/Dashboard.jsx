import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/NavbarLogin";
import Robot3D from "../components/Robot3D";

import "../styles/DashboardCandidate.css";

const BASE_URL = "http://localhost:5000";

// Fallback images cycling for job cards (same as your original)
const CARD_IMAGES = [
  "/images/job1.png",
  "/images/job2.png",
  "/images/job3.png",
];

export default function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser]             = useState(null);
  const [search, setSearch]         = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeName, setResumeName] = useState("");
  const [uploading, setUploading]   = useState(false);
  const [analyzing, setAnalyzing]   = useState(false);
  const [jobs, setJobs]             = useState([]);
  const [error, setError]           = useState("");
  const [uploaded, setUploaded]     = useState(false);

  const fileInputRef = useRef(null);

  // ── Auth guard ──────────────────────────────────────────────────────────────
  useEffect(() => {
    const u = localStorage.getItem("user");
    if (!u) {
      navigate("/login");
    } else {
      const parsed = JSON.parse(u);
      setUser(parsed);
      if (parsed.resume) setUploaded(true);
    }
  }, [navigate]);

  // ── File selected ───────────────────────────────────────────────────────────
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setResumeFile(file);
    setResumeName(file.name);
    setError("");
    setJobs([]);
    setUploaded(false);
  };

  // ── Step 1: Upload resume ───────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!resumeFile) { setError("Please select a resume file first."); return; }

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("resume", resumeFile);

      const res  = await fetch(`${BASE_URL}/api/upload-resume/${user._id}`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!data.success) {
        setError(data.error || "Upload failed. Try again.");
        setUploading(false);
        return;
      }

      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      setUploaded(true);

    } catch (err) {
      console.error("Upload error:", err);
      setError("Network error during upload. Make sure Flask is running on port 5000.");
    }

    setUploading(false);
  };

  // ── Step 2: Get ML recommendations ─────────────────────────────────────────
  const handleGetRecommendations = async () => {
    setAnalyzing(true);
    setError("");
    setJobs([]);

    try {
      const formData = new FormData();

      if (resumeFile) {
        formData.append("resume", resumeFile);
      } else {
        // Fetch existing saved resume from server
        const fileRes = await fetch(`${BASE_URL}/resumes/${user.resume}`);
        const blob    = await fileRes.blob();
        const ext     = user.resume.split(".").pop();
        formData.append("resume", blob, `resume.${ext}`);
      }

      const res  = await fetch(`${BASE_URL}/api/recommend-jobs/${user._id}`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!data.success) {
        setError(data.error || "Could not fetch recommendations.");
        setAnalyzing(false);
        return;
      }

      setJobs(data.jobs || []);

    } catch (err) {
      console.error("Recommendation error:", err);
      setError("Network error while fetching jobs.");
    }

    setAnalyzing(false);
  };

  // ── Filter ML results by search ─────────────────────────────────────────────
  const filteredJobs = jobs.filter((j) =>
    j.job_title.toLowerCase().includes(search.toLowerCase()) ||
    j.company_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="dashboard">

      <Navbar />

      {/* ── HERO ──────────────────────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Welcome {user?.name} to HireSense</h1>
          <p className="hero-desc">
            HireSense is your AI-powered career partner to discover jobs,
            prepare interviews and analyze resumes smartly.
          </p>
          <div className="hero-buttons">
            <button className="primary-btn">Interview Preparation</button>
            <button className="secondary-btn">Resume Analyzer</button>
          </div>
        </div>
        <div className="hero-right">
          <Robot3D />
        </div>
      </section>


      {/* ── RESUME UPLOAD ─────────────────────────────────────────────────── */}
      <div className="resume-section">

        <h2>{uploaded ? "✅ Resume Uploaded" : "Upload Your Resume 📄"}</h2>

        <p>
          {uploaded
            ? "Your resume is saved. Click below to get AI-powered job matches."
            : "Upload your PDF or DOCX resume to unlock AI-powered job matching."}
        </p>

        <div className="resume-box">

          {/* Hidden native file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />

          {/* Choose file button */}
          <button
            className="secondary-btn"
            onClick={() => fileInputRef.current.click()}
          >
            {resumeName ? `📎 ${resumeName}` : "Choose File"}
          </button>

          {/* Upload — only when new file picked */}
          {resumeFile && !uploaded && (
            <button
              className="primary-btn"
              onClick={handleUpload}
              disabled={uploading}
              style={{ marginLeft: "10px" }}
            >
              {uploading ? "Uploading…" : "Upload Resume"}
            </button>
          )}

          {/* Re-upload after already uploaded */}
          {uploaded && (
            <button
              className="secondary-btn"
              style={{ marginLeft: "10px" }}
              onClick={() => {
                setUploaded(false);
                setJobs([]);
                setResumeFile(null);
                setResumeName("");
                setTimeout(() => fileInputRef.current.click(), 100);
              }}
            >
              🔄 Re-upload
            </button>
          )}

        </div>

        {/* Error */}
        {error && (
          <p style={{ color: "#ef4444", marginTop: "10px", fontWeight: 600 }}>
            ⚠️ {error}
          </p>
        )}

        {/* Get Recommendations button */}
        {(uploaded || user?.resume) && (
          <button
            className="primary-btn"
            style={{ marginTop: "20px" }}
            onClick={handleGetRecommendations}
            disabled={analyzing}
          >
            {analyzing ? "🤖 Analysing Resume…" : "🔍 Get Job Recommendations"}
          </button>
        )}

        {analyzing && (
          <p style={{ marginTop: "12px", opacity: 0.65 }}>
            Our ML model is reading your resume and matching jobs — hang tight!
          </p>
        )}

      </div>


      {/* ── SEARCH + JOB CARDS ────────────────────────────────────────────── */}
      {jobs.length > 0 && (
        <>
          {/* Search bar — same as original */}
          <div className="search-wrapper">
            <div className="search-box">
              <input
                placeholder="Search jobs..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button>🔍</button>
            </div>
          </div>

          {/* Jobs section — ORIGINAL card design restored */}
          <section className="jobs">

            <h2>
              Recommended Jobs&nbsp;
              <span style={{ fontSize: "0.85rem", opacity: 0.55 }}>
                ({filteredJobs.length} matches)
              </span>
            </h2>

            <div className="job-grid">

              {filteredJobs.map((job, i) => (

                // ── ORIGINAL card structure exactly as you had ──────────────
                <div className="job-card" key={i}>

                  <img
                    src={CARD_IMAGES[i % CARD_IMAGES.length]}
                    alt={job.job_title}
                  />

                  {/* Match % badge — sits above the overlay */}
                  <div
                    style={{
                      position:     "absolute",
                      top:          "10px",
                      right:        "10px",
                      background:   job.match_score >= 70
                                      ? "#22c55e"
                                      : job.match_score >= 40
                                        ? "#f59e0b"
                                        : "#ef4444",
                      color:        "#fff",
                      fontSize:     "0.72rem",
                      fontWeight:   700,
                      padding:      "3px 8px",
                      borderRadius: "20px",
                      zIndex:       10,
                    }}
                  >
                    {job.match_score ?? "–"}% Match
                  </div>

                  {/* ORIGINAL overlay */}
                  <div className="job-overlay">

                    <h3>{job.job_title}</h3>

                    <p>🏢 {job.company_name}</p>
                    <p>📍 {job.location}</p>

                    {job.job_url ? (
                      <a
                        href={job.job_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          display:         "inline-block",
                          marginTop:       "8px",
                          padding:         "7px 18px",
                          background:      "#fff",
                          color:           "#111",
                          borderRadius:    "6px",
                          fontWeight:      600,
                          textDecoration:  "none",
                          fontSize:        "0.85rem",
                        }}
                      >
                        Apply
                      </a>
                    ) : (
                      <button disabled style={{ marginTop: "8px", opacity: 0.5 }}>
                        No Link
                      </button>
                    )}

                  </div>

                </div>

              ))}

            </div>

          </section>
        </>
      )}

      {/* Empty state */}
      {!analyzing && jobs.length === 0 && (uploaded || user?.resume) && (
        <p style={{ textAlign: "center", marginTop: "30px", opacity: 0.5 }}>
          Click "Get Job Recommendations" to see AI-matched jobs.
        </p>
      )}

    </div>
  );
}