// import { useState } from "react";
// import { motion } from "framer-motion";
// import { useNavigate } from "react-router-dom";
// import "../styles/Login.css";

// export default function Login() {

//   const navigate = useNavigate();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   // ✅ CONNECTED TO FLASK BACKEND
//   async function handleSubmit(e) {
//     e.preventDefault();

//     try {
//       const res = await fetch("http://127.0.0.1:5000/api/login", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ email, password }),
//       });

//       const data = await res.json();

//       if (data.success) {

//         // Save user in browser
//         localStorage.setItem("user", JSON.stringify(data.user));

//         alert("Login Successful ✅");

//         navigate("/dashboard");

//       } else {
//         alert(data.error);
//       }

//     } catch (err) {
//       alert("Server error ❌");
//     }
//   }

//   return (
//     <div className="login-layout">

//       {/* LEFT - LOGIN FORM */}
//       <div className="auth-page">

//         <motion.div
//           initial={{ opacity: 0, y: 40 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ duration: 0.6 }}
//           className="auth-box"
//         >
//           <h1>Welcome Back 👋</h1>

//           <p className="subtitle">
//             Login to your HireSense account
//           </p>

//           <form onSubmit={handleSubmit}>

//             <div className="field">
//               <label>Email Address</label>

//               <input
//                 type="email"
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//                 required
//               />
//             </div>

//             <div className="field">
//               <label>Password</label>

//               <input
//                 type="password"
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 required
//               />
//             </div>

//             <button type="submit">
//               Login
//             </button>

//           </form>

//           <p className="redirect">
//             Don’t have an account?{" "}
//             <span onClick={() => navigate("/register")}>
//               Register
//             </span>
//           </p>

//         </motion.div>

//       </div>


//       {/* RIGHT - INFO PANEL */}
//       <div className="login-info">

//         <h2>Grow Your Career with AI 🚀</h2>

//         <p>
//           HireSense helps you discover the right jobs, prepare for interviews,
//           and build strong resumes using Artificial Intelligence.
//         </p>

//         <ul>
//           <li>✔ Smart Job Matching</li>
//           <li>✔ Resume Analyzer</li>
//           <li>✔ Interview Preparation</li>
//           <li>✔ Career Dashboard</li>
//         </ul>

//         <div className="quote">
//           “Your future depends on what you do today.”
//         </div>

//       </div>

//     </div>
//   );
// }






// new lOGIN CODE

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css";

export default function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);


  // ✅ If already logged in → go to dashboard
  useEffect(() => {

    const user = localStorage.getItem("user");

    if (user) {
      navigate("/dashboard");
    }

  }, [navigate]);


  // ✅ CONNECTED TO FLASK BACKEND
  async function handleSubmit(e) {
    e.preventDefault();

    setLoading(true);

    try {

      const res = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();


      if (res.ok && data.success) {

        // ✅ Save user in browser
        localStorage.setItem("user", JSON.stringify(data.user));

        alert("Login Successful ✅");

        // ✅ Go to Dashboard
        navigate("/Dashboard");

      } else {

        alert(data.error || "Login failed ❌");

      }

    } catch (err) {

      console.log(err);
      alert("Server error ❌");

    } finally {

      setLoading(false);

    }
  }


  return (
    <div className="login-layout">

      {/* LEFT - LOGIN FORM */}
      <div className="auth-page">

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="auth-box"
        >

          <h1>Welcome Back 👋</h1>

          <p className="subtitle">
            Login to your HireSense account
          </p>


          <form onSubmit={handleSubmit}>

            {/* Email */}
            <div className="field">

              <label>Email Address</label>

              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

            </div>


            {/* Password */}
            <div className="field">

              <label>Password</label>

              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

            </div>


            {/* Button */}
            <button type="submit" disabled={loading}>

              {loading ? "Logging in..." : "Login"}

            </button>

          </form>


          {/* Redirect */}
          <p className="redirect">

            Don’t have an account?{" "}

            <span onClick={() => navigate("/register")}>
              Register
            </span>

          </p>

        </motion.div>

      </div>


      {/* RIGHT - INFO PANEL */}
      <div className="login-info">

        <h2>Grow Your Career with AI 🚀</h2>

        <p>
          HireSense helps you discover the right jobs, prepare for interviews,
          and build strong resumes using Artificial Intelligence.
        </p>

        <ul>
          <li>✔ Smart Job Matching</li>
          <li>✔ Resume Analyzer</li>
          <li>✔ Interview Preparation</li>
          <li>✔ Career Dashboard</li>
        </ul>

        <div className="quote">
          “Your future depends on what you do today.”
        </div>

      </div>

    </div>
  );
}

