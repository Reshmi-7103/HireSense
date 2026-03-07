import { useNavigate } from "react-router-dom";

export default function LoginSidebar({ close }) {
  const navigate = useNavigate();

  return (
    <div className="auth-sidebar">
      <button className="close-btn" onClick={close}>✖</button>

      <h2>Welcome 👋</h2>
      <p>Login or create account to continue</p>

      <button
        className="primary-btn"
        onClick={() => {
          close();
          navigate("/login");
        }}
      >
        Login
      </button>

      <button
        className="secondary-btn"
        onClick={() => {
          close();
          navigate("/register");
        }}
      >
        Register
      </button>
    </div>
  );
}
