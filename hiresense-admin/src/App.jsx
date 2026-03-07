import {BrowserRouter,Routes,Route} from "react-router-dom";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import ContactQuery from "./pages/ContactQuery";
import UserDetails from "./pages/UserDetails";

function App(){
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AdminLogin/>}/>
        <Route path="/dashboard" element={<AdminDashboard/>}/>
        <Route path="/contact-query" element={<ContactQuery/>}/>
        <Route path="/user-details" element={<UserDetails/>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App;