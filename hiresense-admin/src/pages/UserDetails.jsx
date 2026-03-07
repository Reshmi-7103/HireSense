import { useLocation, useNavigate } from "react-router-dom";
import "../styles/UserDetails.css";

export default function UserDetails(){

 const location = useLocation();
 const navigate = useNavigate();

 const user = location.state?.user;

 if(!user) return <h2>No User Data Found</h2>;

 return(

  <div className="details-container">

    <div className="details-card">

      <h1>User Profile</h1>

      <p><b>Name:</b> {user.name}</p>
      <p><b>Email:</b> {user.email}</p>
      <p><b>Phone:</b> {user.phone}</p>
      <p><b>College:</b> {user.college}</p>
      <p><b>Year of Passing:</b> {user.yop}</p>
      <p><b>Date of Birth:</b> {user.dob}</p>
      <p><b>Skills:</b> {user.skills}</p>
      <p><b>Experience:</b> {user.experience}</p>

      <button onClick={()=>navigate(-1)}>
        Back
      </button>

    </div>

  </div>
 )
}