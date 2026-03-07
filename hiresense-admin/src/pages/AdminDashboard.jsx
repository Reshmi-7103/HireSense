import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/AdminDashboard.css";

export default function AdminDashboard() {

  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);

  async function loadAdminData() {
    const res = await fetch("http://127.0.0.1:5000/api/admin-data");
    const d = await res.json();
    setData(d);
  }

  useEffect(() => {
    loadAdminData();
  }, [])

  if (!data) return <h2>Loading...</h2>

  const filteredUsers = data.users.filter(u =>
    u.name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="admin-container">

      <h1 className="admin-title">Admin Dashboard</h1>

      {/* ===== TOP CARDS ===== */}

      <div className="admin-top">

        <div className="admin-card users">
          <span>👤</span>
          <h3>Total Users</h3>
          <p>{data.total_users}</p>
        </div>

        <div className="admin-card company">
          <span>🏢</span>
          <h3>Companies</h3>
          <p>0</p>
        </div>

        {/* 🔥 CONTACT CARD */}
        <div
          className="admin-card contact"
          onClick={() => navigate("/contact-query")}
        >
          <span>📩</span>
          <h3>Contact Queries</h3>
          <p>{data.contacts.length}</p>
        </div>

      </div>


      {/* ===== SEARCH BAR ===== */}

      <input
        className="search-box"
        type="text"
        placeholder="Search user by name..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />


      {/* ===== USER TABLE ===== */}

      <div className="table">

        {filteredUsers.map(u => (

          <div className="row" key={u._id}>
            <p>{u.name}</p>
            <p>{u.email}</p>

            <div style={{ display: "flex", gap: "10px" }}>

              <button
                className="view-btn"
                onClick={() => navigate("/user-details", { state: { user: u } })}
              >
                View Details
              </button>

              {u.resume && (

                <a
                  href={`http://127.0.0.1:5000/resumes/${u.resume}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  <button className="resume-btn">
                    View Resume 📄
                  </button>
                </a>

              )}

            </div>

          </div>

        ))}

      </div>


      {/* ===== POPUP ===== */}

      {selectedUser && (

        <div className="popup">

          <div className="popup-content">

            <h2>User Details</h2>

            <p><b>Name:</b> {selectedUser.name}</p>
            <p><b>Email:</b> {selectedUser.email}</p>
            <p><b>Phone:</b> {selectedUser.phone}</p>
            <p><b>College:</b> {selectedUser.college}</p>
            <p><b>YOP:</b> {selectedUser.yop}</p>
            <p><b>DOB:</b> {selectedUser.dob}</p>
            <p><b>Skills:</b> {selectedUser.skills}</p>
            <p><b>Experience:</b> {selectedUser.experience}</p>

            <button
              className="close-btn"
              onClick={() => setSelectedUser(null)}
            >
              Close
            </button>

          </div>

        </div>

      )}

    </div>
  )
}