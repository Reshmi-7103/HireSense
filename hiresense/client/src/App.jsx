import { BrowserRouter, Routes, Route } from "react-router-dom";

import DashboardCandidate from "./pages/DashboardCandidate";
import Dashboard from "./pages/Dashboard";

import About from "./pages/About";
import Contact from "./pages/Contact";

import AboutLogin from "./pages/AboutLogin";
import ContactLogin from "./pages/ContactLogin";

import Login from "./pages/Login";
import Register from "./pages/Register";

import ProfileCandidate from "./pages/ProfileCandidate";
import ResumeAnalyzer from "./pages/ResumeAnalyzer";   // 🔥 NEW
import Interview from "./pages/Interview";

function App() {
  return (

    <BrowserRouter>

      <Routes>

        {/* Guest Home */}
        <Route path="/" element={<DashboardCandidate />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Logged-in Dashboard */}
        <Route path="/Dashboard" element={<Dashboard />} />

        {/* Profile */}
        <Route path="/ProfileCandidate" element={<ProfileCandidate />} />

         {/* 🔥 MOCK INTERVIEW */}
        <Route path="/Interview" element={<Interview/>} />

        {/* 🔥 RESUME ANALYZER */}
        <Route path="/resume-analyzer" element={<ResumeAnalyzer />} />

        {/* Static pages */}
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        <Route path="/aboutlogin" element={<AboutLogin />} />
        <Route path="/contactlogin" element={<ContactLogin />} />

      </Routes>

    </BrowserRouter>

  );
}

export default App;