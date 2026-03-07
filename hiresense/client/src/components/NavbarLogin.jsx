import { NavLink, useNavigate } from "react-router-dom";
import "../styles/DashboardCandidate.css";

export default function Navbar() {

  const navigate = useNavigate();

  function handleProfileClick() {
    navigate("/ProfileCandidate");
  }


  return (
    <>
      <nav className="navbar">

        {/* LOGO */}
        <div className="logo">
          HireSense
        </div>


        {/* LINKS */}
        <div className="nav-links">

          <NavLink
            to="/Dashboard"
            className={({ isActive }) => (isActive ? "nav-active" : "")}
          >
            Home
          </NavLink>

          <NavLink
            to="/aboutlogin"
            className={({ isActive }) => (isActive ? "nav-active" : "")}
          >
            About
          </NavLink>

          <NavLink
            to="/contactlogin"
            className={({ isActive }) => (isActive ? "nav-active" : "")}
          >
            Contact
          </NavLink>

        </div>


        {/* PROFILE ICON */}
        <img
          src="/icons/profile-icon.png"
          className="profile-icon"
          onClick={handleProfileClick}
          alt="Profile"
        />

      </nav>
    </>
  );
}
