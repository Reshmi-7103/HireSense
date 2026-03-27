import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Robot3D from "../components/Robot3D";
import "../styles/DashboardCandidate.css";
import { useNavigate } from "react-router-dom";

const staticJobs = [
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

export default function DashboardCandidate() {
  const [search, setSearch] = useState("");
  const [jobs, setJobs] = useState(staticJobs);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));

    // ❌ NOT LOGGED IN → STATIC
    if (!user) {
      setJobs(staticJobs);
      return;
    }

    // ✅ LOGGED IN → CALL BACKEND
    fetch(`http://localhost:5000/api/job-recommendations/${user._id}`)
      .then(res => res.json())
      .then(data => {

        // ❌ NO RESUME → REDIRECT
        if (data.no_resume) {
          alert("Please upload resume first!");
          navigate("/profile");
          return;
        }

        // ✅ SHOW ML JOBS
        if (data.success) {
          const formatted = data.jobs.map(j => ({
            title: j.job_title,
            desc: j.company_name + " • " + j.location,
            img: "/images/job1.png",
            url: j.job_url
          }));

          setJobs(formatted);
        }
      })
      .catch(err => {
        console.error(err);
        setJobs(staticJobs);
      });

  }, []);

  return (
    <div className="dashboard">
      <Navbar />

      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Welcome to HireSense</h1>
          <p className="hero-desc">
            HireSense is your AI-powered career partner to discover jobs,
            prepare interviews and analyze resumes .
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
                  <button
                    onClick={() => {
                      if (job.url) {
                        window.open(job.url, "_blank");
                      }
                    }}
                  >
                    Apply
                  </button>
                </div>
              </div>
            ))}
        </div>
      </section>
    </div>
  );
}