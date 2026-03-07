import { useState } from "react";
import Navbar from "../components/Navbar";
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

export default function DashboardCandidate() {
  const [search, setSearch] = useState("");

  return (
    <div className="dashboard">
      <Navbar />

      {/* HERO */}
      <section className="hero">
        {/* carousel-bg hata diya kyunki CSS ::before use ho raha hai */}

        {/* ✅ class hero-content CSS ke saath match */}
        <div className="hero-content">
          <h1 className="hero-title">Welcome to HireSense</h1>
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

      {/* SEARCH */}
      <div className="search-wrapper">
        <div className="search-box">
          {/* ✅ SEARCH FIXED */}
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
    </div>
  );
}
