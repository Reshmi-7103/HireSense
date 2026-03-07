// import { useState } from "react";
// import { motion } from "framer-motion";
// import { useNavigate } from "react-router-dom";
// import "../styles/Register.css";

// export default function Register() {
//   const navigate = useNavigate();

//   const [form, setForm] = useState({
//     name: "",
//     email: "",
//     phone: "",
//     college: "",
//     yop: "",
//     dob: "",
//     skills: "",
//     experience: "",
//     password: "",
//   });

//   function update(k, v) {
//     setForm((s) => ({ ...s, [k]: v }));
//   }

//   // ✅ CONNECTED TO FLASK BACKEND
//   async function handleSubmit(e) {
//     e.preventDefault();

//     try {
//       const res = await fetch("http://127.0.0.1:5000/api/register", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(form),
//       });

//       const data = await res.json();

//       if (data.success) {
//         alert("Registration Successful ✅");
//         navigate("/login");
//       } else {
//         alert(data.error);
//       }

//     } catch (err) {
//       alert("Server error ❌");
//     }
//   }

//   return (
//     <div className="register-layout">

//       {/* LEFT SIDE - FORM */}
//       <div className="auth-page">

//         <motion.div
//           initial={{ opacity: 0, y: 40 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ duration: 0.6 }}
//           className="register-box"
//         >
//           <h1>Create Your Profile</h1>

//           <p className="subtitle">
//             Fill your details to build your HireSense profile
//           </p>

//           <form onSubmit={handleSubmit}>

//             <div className="grid">

//               <div className="field">
//                 <label>Full Name</label>
//                 <input
//                   required
//                   onChange={(e) => update("name", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>Email</label>
//                 <input
//                   type="email"
//                   required
//                   onChange={(e) => update("email", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>Phone</label>
//                 <input
//                   onChange={(e) => update("phone", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>Date of Birth</label>
//                 <input
//                   type="date"
//                   onChange={(e) => update("dob", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>College</label>
//                 <input
//                   onChange={(e) => update("college", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>Year of Passing</label>
//                 <input
//                   type="number"
//                   placeholder="2026"
//                   onChange={(e) => update("yop", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>Skills</label>
//                 <input
//                   placeholder="React, Python, ML"
//                   onChange={(e) => update("skills", e.target.value)}
//                 />
//               </div>

//               <div className="field">
//                 <label>Experience</label>
//                 <input
//                   placeholder="Fresher / 2 Years"
//                   onChange={(e) => update("experience", e.target.value)}
//                 />
//               </div>

//               <div className="field full">
//                 <label>Password</label>
//                 <input
//                   type="password"
//                   required
//                   onChange={(e) => update("password", e.target.value)}
//                 />
//               </div>

//             </div>

//             <button type="submit">Create Account</button>

//           </form>

//           <p className="redirect">
//             Already registered?{" "}
//             <span onClick={() => navigate("/login")}>Login</span>
//           </p>

//         </motion.div>

//       </div>


//       {/* RIGHT SIDE - INFO */}
//       <div className="register-info">

//         <h2>Your Career Starts Here 🚀</h2>

//         <p>
//           Create a complete profile to unlock personalized jobs,
//           resume analysis, and interview preparation.
//         </p>

//         <ul>
//           <li>✔ Smart Job Matching</li>
//           <li>✔ Resume Scoring</li>
//           <li>✔ AI Interview Coach</li>
//           <li>✔ Career Dashboard</li>
//         </ul>

//         <div className="quote">
//           “Success is where preparation meets opportunity.”
//         </div>

//       </div>

//     </div>
//   );
// }



// new code Regiter page 
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "../styles/Register.css";

export default function Register() {

  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    college: "",
    yop: "",
    dob: "",
    skills: "",
    experience: "",
    password: "",
  });


  // ✅ If already logged in → redirect
  useEffect(() => {

    const user = localStorage.getItem("user");

    if (user) {
      navigate("/dashboard");
    }

  }, [navigate]);


  function update(k, v) {
    setForm((s) => ({ ...s, [k]: v }));
  }


  // ✅ CONNECTED TO FLASK BACKEND
  async function handleSubmit(e) {

    e.preventDefault();

    setLoading(true);

    try {

      const res = await fetch("http://127.0.0.1:5000/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();


      if (res.ok && data.success) {

        alert("Registration Successful ✅");

        navigate("/login");

      } else {

        alert(data.error || "Registration failed ❌");

      }

    } catch (err) {

      console.log(err);
      alert("Server error ❌");

    } finally {

      setLoading(false);

    }
  }


  return (
    <div className="register-layout">

      {/* LEFT SIDE - FORM */}
      <div className="auth-page">

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="register-box"
        >

          <h1>Create Your Profile</h1>

          <p className="subtitle">
            Fill your details to build your HireSense profile
          </p>


          <form onSubmit={handleSubmit}>

            <div className="grid">


              {/* Name */}
              <div className="field">
                <label>Full Name</label>
                <input
                  required
                  onChange={(e) => update("name", e.target.value)}
                />
              </div>


              {/* Email */}
              <div className="field">
                <label>Email</label>
                <input
                  type="email"
                  required
                  onChange={(e) => update("email", e.target.value)}
                />
              </div>


              {/* Phone */}
              <div className="field">
                <label>Phone</label>
                <input
                  onChange={(e) => update("phone", e.target.value)}
                />
              </div>


              {/* DOB */}
              <div className="field">
                <label>Date of Birth</label>
                <input
                  type="date"
                  onChange={(e) => update("dob", e.target.value)}
                />
              </div>


              {/* College */}
              <div className="field">
                <label>College</label>
                <input
                  onChange={(e) => update("college", e.target.value)}
                />
              </div>


              {/* YOP */}
              <div className="field">
                <label>Year of Passing</label>
                <input
                  type="number"
                  placeholder="2026"
                  onChange={(e) => update("yop", e.target.value)}
                />
              </div>


              {/* Skills */}
              <div className="field">
                <label>Skills</label>
                <input
                  placeholder="React, Python, ML"
                  onChange={(e) => update("skills", e.target.value)}
                />
              </div>


              {/* Experience */}
              <div className="field">
                <label>Experience</label>
                <input
                  placeholder="Fresher / 2 Years"
                  onChange={(e) => update("experience", e.target.value)}
                />
              </div>


              {/* Password */}
              <div className="field full">
                <label>Password</label>
                <input
                  type="password"
                  required
                  onChange={(e) => update("password", e.target.value)}
                />
              </div>


            </div>


            {/* Button */}
            <button type="submit" disabled={loading}>

              {loading ? "Creating Account..." : "Create Account"}

            </button>

          </form>


          {/* Redirect */}
          <p className="redirect">

            Already registered?{" "}

            <span onClick={() => navigate("/login")}>
              Login
            </span>

          </p>

        </motion.div>

      </div>


      {/* RIGHT SIDE - INFO */}
      <div className="register-info">

        <h2>Your Career Starts Here 🚀</h2>

        <p>
          Create a complete profile to unlock personalized jobs,
          resume analysis, and interview preparation.
        </p>

        <ul>
          <li>✔ Smart Job Matching</li>
          <li>✔ Resume Scoring</li>
          <li>✔ AI Interview Coach</li>
          <li>✔ Career Dashboard</li>
        </ul>

        <div className="quote">
          “Success is where preparation meets opportunity.”
        </div>

      </div>

    </div>
  );
}
