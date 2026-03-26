// Profile code 
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/NavbarLogin";
import "../styles/ProfileCandidate.css";

export default function ProfileCandidate() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({});

  // 🔥 NEW STATE FOR RESUME
  const [resumeFile,setResumeFile]=useState(null);

  // ✅ Load user from localStorage
  useEffect(() => {
    const u = localStorage.getItem("user");

    if (!u) {
      navigate("/login");
    } else {
      const parsed = JSON.parse(u);
      setUser(parsed);
      setForm(parsed);
    }
  }, [navigate]);

  // ✅ Handle input change
  function handleChange(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  }

  // ✅ UPDATE PROFILE
  async function handleUpdate() {

  try {

    const payload = {
      ...form,
      id: user._id
    };

    const res = await fetch("http://127.0.0.1:5000/api/update-profile", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (data.success) {

      localStorage.setItem("user", JSON.stringify(data.user));

      setUser(data.user);
      setForm(data.user);
      setEdit(false);

      alert("Profile Updated ✅");

    } else {
      alert(data.error || "Update failed ❌");
    }

  } catch (err) {
    alert("Server Error ❌");
  }
}

 // 🔥 NEW FUNCTION FOR RESUME UPLOAD
 async function handleResumeUpload(){

  if(!resumeFile){
    alert("Please select resume first ❌");
    return;
  }

  const formData=new FormData();
  formData.append("resume",resumeFile);

  try{

    const res=await fetch(`http://127.0.0.1:5000/api/upload-resume/${user._id}`,{
      method:"POST",
      body:formData
    });

    const data=await res.json();

    if(data.success){

      localStorage.setItem("user",JSON.stringify(data.user));

      setUser(data.user);
      setForm(data.user);

      alert("Resume Uploaded Successfully ✅");

    }
    else{
      alert("Upload Failed ❌");
    }

  }
  catch(err){
    alert("Server Error ❌");
  }
 }

  // ✅ LOGOUT
  function handleLogout() {
    localStorage.removeItem("user");
    navigate("/");
  }

  if (!user) return null;

  return (
    <div className="profile-page">
      <Navbar />

      <div className="profile-wrapper">

        {/* PROFILE CARD */}
        <div className="profile-card">
          <h1>My Profile 👤</h1>

          {!edit && (
            <div className="profile-view">
              <div className="row"><span>Full Name</span><p>{user.name}</p></div>
              <div className="row"><span>Email</span><p>{user.email}</p></div>
              <div className="row"><span>Phone</span><p>{user.phone}</p></div>
              <div className="row"><span>College</span><p>{user.college}</p></div>
              <div className="row"><span>Year of Passing</span><p>{user.yop}</p></div>
              <div className="row"><span>Date of Birth</span><p>{user.dob}</p></div>
              <div className="row"><span>Skills</span><p>{user.skills}</p></div>
              <div className="row"><span>Experience</span><p>{user.experience}</p></div>

              {/* 🔥 RESUME VIEW DOWNLOAD */}
              <div className="row">
                <span>Resume</span>

                {user.resume ? (

                  <div style={{display:"flex",gap:"10px"}}>

                    <a
                      href={`http://127.0.0.1:5000/resumes/${user.resume}`}
                      target="_blank"
                      rel="noreferrer"
                      className="resume-btn"
                    >
                      View 📄
                    </a>

                    <a
                      href={`http://127.0.0.1:5000/resumes/${user.resume}`}
                      download
                      className="resume-btn"
                    >
                      Download ⬇️
                    </a>

                  </div>

                ) : (
                  <p>No Resume Uploaded</p>
                )}
              </div>

              {/* 🔥 RESUME UPLOAD */}
              <div className="resume-upload">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e)=>setResumeFile(e.target.files[0])}
                />
                <button onClick={handleResumeUpload}>
                  Upload / Change Resume
                </button>
              </div>

              <div className="profile-btns">
                <button onClick={() => setEdit(true)}>
                  Update Profile ✏️
                </button>

                <button className="logout-btn" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </div>
          )}

          {edit && (
            <div className="profile-edit">
              <div className="field">
                <label>Full Name</label>
                <input name="name" value={form.name || ""} onChange={handleChange} />
              </div>

              <div className="field">
                <label>Phone</label>
                <input name="phone" value={form.phone || ""} onChange={handleChange} />
              </div>

              <div className="field">
                <label>College</label>
                <input name="college" value={form.college || ""} onChange={handleChange} />
              </div>

              <div className="field">
                <label>Year of Passing</label>
                <input name="yop" value={form.yop || ""} onChange={handleChange} />
              </div>

              <div className="field">
                <label>Date of Birth</label>
                <input type="date" name="dob" value={form.dob || ""} onChange={handleChange} />
              </div>

              <div className="field">
                <label>Skills</label>
                <input name="skills" value={form.skills || ""} onChange={handleChange} />
              </div>

              <div className="field">
                <label>Experience</label>
                <input name="experience" value={form.experience || ""} onChange={handleChange} />
              </div>

              <div className="btn-group">
                <button onClick={handleUpdate}>Save Changes 💾</button>
                <button className="cancel" onClick={() => setEdit(false)}>Cancel</button>
              </div>
            </div>
          )}
        </div>


        {/* RIGHT SIDE FEATURES */}

        <div className="profile-features">

          <div
            className="profile-feature-card"
            onClick={() => navigate("/Interview")}
          >
            <div className="feature-icon">🎯</div>
            <h3>Interview Preparation</h3>
            <p>
              Practice aptitude, coding and HR questions to get ready
              for your dream job interviews.
            </p>
          </div>

          <div
            className="profile-feature-card"
            onClick={() => navigate("/resume-analyzer")}
          >
            <div className="feature-icon">📄</div>
            <h3>Resume Analyzer</h3>
            <p>
              Upload your resume and get AI-based feedback
              to improve your job chances.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}