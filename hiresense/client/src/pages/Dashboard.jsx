import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/NavbarLogin";
import Robot3D from "../components/Robot3D";

import "../styles/DashboardCandidate.css";


const jobs = [
  { title: "Frontend Developer", desc: "React, UI, Performance", img: "/images/job1.png" },
  { title: "Backend Developer", desc: "Node, APIs, Databases", img: "/images/job2.png" },
  { title: "AI Engineer", desc: "ML, NLP, Models", img: "/images/job3.png" },
  { title: "Data Analyst", desc: "Insights & Reports", img: "/images/job1.png" },
  { title: "ML Engineer", desc: "Model Training", img: "/images/job2.png" },
  { title: "DevOps Engineer", desc: "CI/CD & Cloud", img: "/images/job3.png" },
  { title: "UI Designer", desc: "UX & Visuals", img: "/images/job1.png" },
  { title: "Cloud Engineer", desc: "AWS / Azure", img: "/images/job2.png" },
  { title: "Product Engineer", desc: "Build & Scale", img: "/images/job3.png" },
];


export default function Dashboard() {

  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [user, setUser] = useState(null);
  const [resume, setResume] = useState(null);


  // ✅ Check Login
  useEffect(() => {

    const u = localStorage.getItem("user");

    if (!u) {
      navigate("/login");
    } else {
      setUser(JSON.parse(u));
    }

  }, [navigate]);


  return (
    <div className="dashboard">

      <Navbar />


      {/* HERO */}
            <section className="hero">
              {/* carousel-bg hata diya kyunki CSS ::before use ho raha hai */}
      
              {/* ✅ class hero-content CSS ke saath match */}
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


      {/* ================= RESUME UPLOAD ================= */}
      {!resume && (

        <div className="resume-section">

          <h2>Upload Your Resume 📄</h2>

          <p>
            Upload your resume to unlock AI-powered job matching.
          </p>

          <div className="resume-box">

            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setResume(e.target.files[0])}
            />

            <button
              onClick={() => alert("Resume Uploaded ✅ (ML Coming Soon 😄)")}
            >
              Upload Resume
            </button>

          </div>

        </div>

      )}


      {/* ================= SEARCH + JOBS ================= */}
      {resume && (

        <>

          {/* SEARCH */}
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


          {/* JOBS */}
          <section className="jobs">

            <h2>Recommended Jobs</h2>

            <div className="job-grid">

              {jobs
                .filter(j =>
                  j.title.toLowerCase().includes(search.toLowerCase())
                )
                .map((job, i) => (

                  <div className="job-card" key={i}>

                    <img src={job.img} alt={job.title} />

                    <div className="job-overlay">

                      <h3>{job.title}</h3>

                      <p>{job.desc}</p>

                      <button>Apply</button>

                    </div>

                  </div>

                ))}

            </div>

          </section>

        </>
      )}

    </div>
  );
}
