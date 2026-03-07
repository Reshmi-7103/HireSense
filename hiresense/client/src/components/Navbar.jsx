import { NavLink } from "react-router-dom";
import { useState } from "react";
import LoginSidebar from "./LoginSidebar";
import "../styles/DashboardCandidate.css";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <nav className="navbar">
        <div className="logo">HireSense</div>

        <div className="nav-links">
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? "nav-active" : "")}
          >
            Home
          </NavLink>

          <NavLink
            to="/about"
            className={({ isActive }) => (isActive ? "nav-active" : "")}
          >
            About
          </NavLink>

          <NavLink
            to="/contact"
            className={({ isActive }) => (isActive ? "nav-active" : "")}
          >
            Contact
          </NavLink>
        </div>

        <img
          src="/icons/profile-icon.png"
          className="profile-icon"
          onClick={() => setOpen(true)}
        />
      </nav>

      {open && <LoginSidebar close={() => setOpen(false)} />}
    </>
  );
}
