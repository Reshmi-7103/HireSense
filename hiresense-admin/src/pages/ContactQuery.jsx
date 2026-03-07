import {useEffect,useState} from "react";
import "../styles/AdminDashboard.css";

export default function ContactQuery(){

 const [data,setData]=useState(null);
 const [tab,setTab]=useState("user");

 // LOAD DATA
 async function loadData(){

  const res = await fetch("http://127.0.0.1:5000/api/admin-data");
  const d = await res.json();

  setData(d);
 }

 useEffect(()=>{
  loadData();
 },[])


 // 🔥 DELETE FUNCTION (FINAL FIX)
 async function deleteQuery(id){

  await fetch("http://127.0.0.1:5000/api/delete-query",{
   method:"DELETE",
   headers:{
    "Content-Type":"application/json"
   },
   body:JSON.stringify({
    id:id
   })
  })

  alert("Query Deleted ❌");

  loadData();   // REFRESH
 }


 if(!data) return <h2>Loading...</h2>

 return(

  <div className="admin-container">

   <h1 className="admin-title">
     Contact Queries 📩
   </h1>

   <div className="tabs">
     <button onClick={()=>setTab("user")}>
       User Queries
     </button>

     <button onClick={()=>setTab("company")}>
       Company Queries
     </button>
   </div>


   {/* USER CONTACT */}

   {tab==="user" && (

   <div className="table">

     {data.contacts.map(c=>(

       <div className="row" key={c._id}>
         <p>{c.name}</p>
         <p>{c.email}</p>
         <p>{c.message}</p>

         {/* 🔥 DELETE BUTTON */}
         <button
           className="delete-btn"
           onClick={()=>deleteQuery(c._id)}
         >
           Delete
         </button>

       </div>

     ))}

   </div>

   )}


   {/* COMPANY CONTACT */}

   {tab==="company" && (

   <div className="table">
     <h3>No Company Queries Yet</h3>
   </div>

   )}

  </div>
 )
}