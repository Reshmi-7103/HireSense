import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function AdminLogin(){

  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");

  const navigate=useNavigate();

  async function handleLogin(){

    const res = await fetch("http://127.0.0.1:5000/api/admin-login",{
      method:"POST",
      headers:{
        "Content-Type":"application/json"
      },
      body:JSON.stringify({email,password})
    });

    const data = await res.json();

    if(data.success){
      localStorage.setItem("admin",JSON.stringify(data.admin));
      navigate("/dashboard");
    }
    else{
      alert(data.error);
    }
  }

  return(
    <div style={{padding:"40px"}}>
      <h1>Admin Login</h1>

      <input
        placeholder="Email"
        onChange={e=>setEmail(e.target.value)}
      />

      <br/><br/>

      <input
        type="password"
        placeholder="Password"
        onChange={e=>setPassword(e.target.value)}
      />

      <br/><br/>

      <button onClick={handleLogin}>Login</button>
    </div>
  );
}