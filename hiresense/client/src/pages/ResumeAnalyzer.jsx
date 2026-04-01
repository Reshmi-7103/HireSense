import { useState } from "react";
import Navbar from "../components/NavbarLogin";
import "../styles/ResumeAnalyzer.css";

export default function ResumeAnalyzer() {

  const user = JSON.parse(localStorage.getItem("user"));
  const [role, setRole] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // ==================== FILE HANDLER ====================
  function handleFileChange(e) {
    const selected = e.target.files[0];
    if (selected && selected.type !== "application/pdf") {
      alert("Only PDF Resume Allowed!");
      return;
    }
    setFile(selected);
  }

  // ==================== MAIN ANALYSIS FUNCTION ====================
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
        console.log("Analysis Result:", data.analysis);
      } else {
        alert("Analysis Failed");
      }
    } catch (err) {
      console.log(err);
      alert("Server Error");
    }

    setLoading(false);
  }

  // ==================== DOWNLOAD REPORT ====================
  function downloadAnalysis() {
    if (!result) return;

    const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Analysis Report - HireSense AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            padding: 40px;
            min-height: 100vh;
        }
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 30px;
            box-shadow: 0 30px 70px rgba(0,0,0,0.4);
            overflow: hidden;
        }
        .report-header {
            background: linear-gradient(135deg, #00c9a7, #00b894);
            color: white;
            padding: 50px;
            text-align: center;
        }
        .report-header h1 { font-size: 2.5rem; margin-bottom: 15px; }
        .report-date { margin-top: 20px; font-size: 0.9rem; opacity: 0.9; }
        .report-content { padding: 40px; }
        .score-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .score-card {
            background: #f8f9fa;
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            border-left: 4px solid #00c9a7;
        }
        .score-value {
            font-size: 3rem;
            font-weight: bold;
            color: #00c9a7;
        }
        .progress-bar-container {
            background: #e0e0e0;
            border-radius: 10px;
            margin-top: 15px;
            height: 8px;
            overflow: hidden;
        }
        .progress-bar-fill {
            background: #00c9a7;
            height: 100%;
            border-radius: 10px;
        }
        .section-title {
            font-size: 1.5rem;
            color: #2c3e50;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #00c9a7;
        }
        .skills-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }
        .skill-badge {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 6px 15px;
            border-radius: 20px;
        }
        .skill-badge.missing {
            background: #ffebee;
            color: #c62828;
        }
        .recommendations-list {
            list-style: none;
            padding: 0;
        }
        .recommendations-list li {
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #00c9a7;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>🤖 AI Resume Analysis Report</h1>
            <p>Powered by HireSense Intelligent Support System</p>
            <div class="report-date">📅 ${new Date().toLocaleString()}</div>
        </div>
        <div class="report-content">
            <div class="score-section">
                <div class="score-card">
                    <h3>ATS Compatibility</h3>
                    <div class="score-value">${result.scores?.ats_compatibility || 0}%</div>
                    <div class="progress-bar-container"><div class="progress-bar-fill" style="width: ${result.scores?.ats_compatibility || 0}%"></div></div>
                </div>
                <div class="score-card">
                    <h3>Job Match Score</h3>
                    <div class="score-value">${result.scores?.job_match_rate || 0}%</div>
                    <div class="progress-bar-container"><div class="progress-bar-fill" style="width: ${result.scores?.job_match_rate || 0}%"></div></div>
                </div>
                <div class="score-card">
                    <h3>Overall Score</h3>
                    <div class="score-value">${result.scores?.ranking_score || 0}%</div>
                    <div class="progress-bar-container"><div class="progress-bar-fill" style="width: ${result.scores?.ranking_score || 0}%"></div></div>
                </div>
                <div class="score-card">
                    <h3>Skills Match</h3>
                    <div class="score-value">${result.skills_analysis?.match_percentage || 0}%</div>
                    <div class="progress-bar-container"><div class="progress-bar-fill" style="width: ${result.skills_analysis?.match_percentage || 0}%"></div></div>
                </div>
            </div>
            
            <h2 class="section-title">🔧 Skills Intelligence</h2>
            <h3>✅ Matched Skills (${result.skills_analysis?.matched_skills?.length || 0})</h3>
            <div class="skills-grid">${result.skills_analysis?.matched_skills?.map(s => `<span class="skill-badge">${s}</span>`).join('') || '<p>No matched skills found</p>'}</div>
            
            <h3>❌ Skills to Develop (${result.skills_analysis?.missing_skills?.length || 0})</h3>
            <div class="skills-grid">${result.skills_analysis?.missing_skills?.map(s => `<span class="skill-badge missing">${s}</span>`).join('') || '<p>No missing skills identified</p>'}</div>
            
            <h2 class="section-title">💡 Recommendations</h2>
            <ul class="recommendations-list">${result.recommendations?.map(rec => `<li>✨ ${rec}</li>`).join('') || '<li>No recommendations available</li>'}</ul>
            
            <h2 class="section-title">📝 Quality Analysis</h2>
            <p><strong>Grammar Errors:</strong> ${result.content_issues?.grammar_errors || 0}</p>
        </div>
        <div class="footer">
            <p>🚀 Generated by HireSense AI - Your Intelligent Career Companion</p>
        </div>
    </div>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_analysis_${new Date().toISOString().slice(0, 19)}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="resume-page">
      <Navbar />
      <div className="resume-container">
        <div className="resume-card">

          {/* Header */}
          <div className="header-section">
            <h1 className="main-title">
              <span className="ai-icon">🤖</span>
              AI Resume Analyzer
            </h1>
            <p className="subtitle">Powered by HireSense • Get instant AI-powered insights</p>
          </div>

          {/* Input Form */}
          <div className="form-section">
            <div className="input-field">
              <label className="field-label">
                <span className="label-icon">🎯</span>
                Target Job Role
              </label>
              <input
                type="text"
                className="role-input"
                placeholder="e.g., Software Engineer, Data Scientist, Full Stack Developer"
                value={role}
                onChange={e => setRole(e.target.value)}
              />
            </div>

            <div className="input-field">
              <label className="field-label">
                <span className="label-icon">📄</span>
                Upload Resume (PDF only)
              </label>
              <div className="file-upload-wrapper">
                <input
                  type="file"
                  id="resume-upload"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="file-input-hidden"
                />
                <label htmlFor="resume-upload" className="file-upload-btn">
                  <span className="upload-icon">📁</span>
                  {file ? file.name : "Choose PDF File"}
                </label>
                {file && (
                  <span className="file-status">✓ Ready to analyze</span>
                )}
              </div>
            </div>

            <button
              className={`analyze-btn ${loading ? 'loading' : ''}`}
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>
                  <span className="btn-icon">🚀</span>
                  Analyze Resume
                </>
              )}
            </button>
          </div>

          {/* Results */}
          {result && (
            <>
              <div className="results-section">

                {/* Score Cards */}
                <div className="scores-grid">
                  <div className="score-item">
                    <div className="score-icon">🎯</div>
                    <div className="score-number">{result.scores?.ats_compatibility || 0}%</div>
                    <div className="score-label">ATS Compatibility</div>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${result.scores?.ats_compatibility || 0}%` }}></div>
                    </div>
                  </div>

                  <div className="score-item">
                    <div className="score-icon">📊</div>
                    <div className="score-number">{result.scores?.job_match_rate || 0}%</div>
                    <div className="score-label">Job Match</div>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${result.scores?.job_match_rate || 0}%` }}></div>
                    </div>
                  </div>

                  <div className="score-item">
                    <div className="score-icon">⭐</div>
                    <div className="score-number">{result.scores?.ranking_score || 0}%</div>
                    <div className="score-label">Overall Score</div>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${result.scores?.ranking_score || 0}%` }}></div>
                    </div>
                  </div>
                </div>

                {/* Skills Analysis */}
                <div className="analysis-card">
                  <h3 className="card-title">
                    <span className="title-icon">🔧</span>
                    Skills Analysis
                    <span className="ai-badge">AI Analyzed</span>
                  </h3>
                  
                  <div className="skills-dual">
                    <div className="skills-box">
                      <h4>✅ Matched Skills <span className="badge">{result.skills_analysis?.matched_skills?.length || 0}</span></h4>
                      <div className="skills-list">
                        {result.skills_analysis?.matched_skills?.map((s, i) => (
                          <span key={i} className="skill-tag matched">{s}</span>
                        ))}
                        {(!result.skills_analysis?.matched_skills?.length) && (
                          <p className="empty-msg">No matched skills found</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="skills-box">
                      <h4>❌ Missing Skills <span className="badge">{result.skills_analysis?.missing_skills?.length || 0}</span></h4>
                      <div className="skills-list">
                        {result.skills_analysis?.missing_skills?.map((s, i) => (
                          <span key={i} className="skill-tag missing">{s}</span>
                        ))}
                        {(!result.skills_analysis?.missing_skills?.length) && (
                          <p className="empty-msg success">Great! No critical skills missing</p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="match-rate">
                    <span>Match Rate: {result.skills_analysis?.match_percentage || 0}%</span>
                    <div className="match-bar">
                      <div className="match-fill" style={{ width: `${result.skills_analysis?.match_percentage || 0}%` }}></div>
                    </div>
                  </div>
                </div>

                {/* Quality Issues */}
                <div className="analysis-card">
                  <h3 className="card-title">
                    <span className="title-icon">📝</span>
                    Quality Check
                  </h3>
                  <div className="quality-metric">
                    <span>Grammar Errors:</span>
                    <strong className={result.content_issues?.grammar_errors > 10 ? 'warning' : 'success'}>
                      {result.content_issues?.grammar_errors || 0}
                    </strong>
                  </div>
                  
                  {result.content_issues?.grammar_details?.length > 0 && (
                    <div className="grammar-list">
                      <h4>Issues Found:</h4>
                      {result.content_issues.grammar_details.slice(0, 3).map((err, i) => (
                        <div key={i} className="grammar-item">
                          <span className="grammar-line">Line {err.line_number || '?'}:</span>
                          <span className="grammar-msg">{err.message}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Formatting Issues */}
                {result.content_issues?.formatting_issues?.length > 0 && (
                  <div className="analysis-card">
                    <h3 className="card-title">
                      <span className="title-icon">⚠️</span>
                      Formatting Issues
                    </h3>
                    <ul className="issues-list">
                      {result.content_issues.formatting_issues.map((issue, i) => (
                        <li key={i}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                <div className="analysis-card highlight">
                  <h3 className="card-title">
                    <span className="title-icon">💡</span>
                    AI Recommendations
                  </h3>
                  <ul className="recommendations-list">
                    {result.recommendations?.map((rec, i) => (
                      <li key={i}>
                        <span className="rec-bullet"> </span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Download Button */}
              <button className="download-btn" onClick={downloadAnalysis}>
                <span className="btn-icon">📥</span>
                Download Full Report
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}