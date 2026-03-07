import { motion } from "framer-motion";
import Navbar from "../components/Navbar";
// import Navbar from "../components/NavbarLogin";
import "../styles/About.css";

export default function About() {
  return (
    <>
      <Navbar />

      <div className="about-page">
        {/* Heading */}
        <motion.h1
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="about-title"
        >
          About HireSense
        </motion.h1>

        {/* Intro */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="about-intro"
        >
          <p>
            HireSense is your all-in-one platform to{" "}
            <span>find jobs</span>, <span>prepare for interviews</span>, and{" "}
            <span>get AI-powered resume insights</span>.  
            Our mission is to empower job seekers with modern tools and intelligent recommendations.
          </p>
        </motion.div>

        {/* Features */}
        <div className="about-features">
          <motion.div
            className="feature-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <img src="/images/search-job.png" alt="Job Search" />
            <h3>Smart Job Search</h3>
            <p>Find job opportunities personalized to your skills and interests.</p>
          </motion.div>

          <motion.div
            className="feature-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <img src="/images/interview.png" alt="Interview Prep" />
            <h3>Interview Preparation</h3>
            <p>AI-assisted mock interviews and preparation tips.</p>
          </motion.div>

          <motion.div
            className="feature-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <img src="/images/resume.png" alt="Resume Analyzer" />
            <h3>Resume Analyzer</h3>
            <p>Optimize your resume with AI feedback.</p>
          </motion.div>
        </div>

        {/* Closing */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="about-closing"
        >
          <p>
            At HireSense, we combine AI technology with a user-friendly interface
            to make job hunting smarter and faster.
          </p>
        </motion.div>
      </div>
    </>
  );
}
