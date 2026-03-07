// import Navbar from "../components/Navbar";
// import NavbarLogin from "../components/NavbarLogin";
// import "../styles/Contact.css";

// export default function Contact() {
//   return (
//     <>
//       <Navbar />

//       <div className="contact-page">
//         <h1 className="contact-title">Contact Us</h1>

//         <div className="contact-container">
//           {/* LEFT FORM */}
//           <div className="contact-form">
//             <h2>Get in Touch</h2>

//             <form>
//               <input type="text" placeholder="Your Name" />
//               <input type="email" placeholder="Your Email" />
//               <textarea rows="6" placeholder="Your Message"></textarea>
//               <button type="submit">Send Message</button>
//             </form>
//           </div>

//           {/* RIGHT INFO */}
//           <div className="contact-info">
//             <div className="info-card">
//               <h3>Email</h3>
//               <p>support@hiresense.com</p>
//             </div>

//             <div className="info-card">
//               <h3>Phone</h3>
//               <p>+91 98765 43210</p>
//             </div>

//             <div className="info-card">
//               <h3>Address</h3>
//               <p>123 HireSense Street, Mumbai, India</p>
//             </div>
//           </div>
//         </div>

//         <p className="contact-footer">
//           We are always here to help you. Your feedback matters to us!
//         </p>
//       </div>
//     </>
//   );

// }

import { useState } from "react";
import Navbar from "../components/Navbar";
import "../styles/Contact.css";

export default function Contact() {

  const [name,setName]=useState("");
  const [email,setEmail]=useState("");
  const [message,setMessage]=useState("");

  async function handleSubmit(e){

    e.preventDefault();

    const res = await fetch("http://127.0.0.1:5000/api/contact",{
      method:"POST",
      headers:{
        "Content-Type":"application/json"
      },
      body:JSON.stringify({
        name,
        email,
        message
      })
    })

    const data = await res.json();

    if(data.success){
      alert("Message Sent Successfully");
      setName("");
      setEmail("");
      setMessage("");
    }
    else{
      alert("Error sending message");
    }
  }

  return (
    <>
      <Navbar />

      <div className="contact-page">
        <h1 className="contact-title">Contact Us</h1>

        <div className="contact-container">

          {/* LEFT FORM */}
          <div className="contact-form">
            <h2>Get in Touch</h2>

            <form onSubmit={handleSubmit}>

              <input
                type="text"
                placeholder="Your Name"
                value={name}
                onChange={e=>setName(e.target.value)}
              />

              <input
                type="email"
                placeholder="Your Email"
                value={email}
                onChange={e=>setEmail(e.target.value)}
              />

              <textarea
                rows="6"
                placeholder="Your Message"
                value={message}
                onChange={e=>setMessage(e.target.value)}
              ></textarea>

              <button type="submit">Send Message</button>

            </form>
          </div>

          {/* RIGHT INFO */}
          <div className="contact-info">
            <div className="info-card">
              <h3>Email</h3>
              <p>support@hiresense.com</p>
            </div>

            <div className="info-card">
              <h3>Phone</h3>
              <p>+91 98765 43210</p>
            </div>

            <div className="info-card">
              <h3>Address</h3>
              <p>123 HireSense Street, Mumbai, India</p>
            </div>
          </div>

        </div>

        <p className="contact-footer">
          We are always here to help you. Your feedback matters to us!
        </p>
      </div>
    </>
  );
}