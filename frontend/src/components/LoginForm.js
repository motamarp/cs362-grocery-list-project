import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Link, useNavigate } from "react-router-dom";

function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(form);
      navigate("/");
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Login failed. Check username and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card">
      <h1>Sign In</h1>
      <p className="muted-text">
        No account yet? <Link to="/register">Create one</Link>
      </p>

      <form onSubmit={handleSubmit}>
        <label>Username</label>
        <input
          name="username"
          value={form.username}
          onChange={handleChange}
          required
        />

        <label>Password</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          required
        />

        <button type="submit" className="primary-btn" disabled={loading}>
          {loading ? "Signing In..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}

export default LoginForm;
