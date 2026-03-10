import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function RegisterForm() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    password_confirm: "",
    date_of_birth: "",
    dietary_preferences: "",
    height: "",
    activity_level: "",
    favorite_stores: "",
  });

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const formatErrors = (errors) => {
    if (!errors) return "Registration failed.";

    if (typeof errors === "string") return errors;

    return Object.entries(errors)
      .map(([field, messages]) => {
        if (Array.isArray(messages)) {
          return `${field}: ${messages.join(", ")}`;
        }
        return `${field}: ${messages}`;
      })
      .join("\n");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...form,
      height: form.height ? Number(form.height) : null,
      activity_level: form.activity_level ? Number(form.activity_level) : null,
      date_of_birth: form.date_of_birth || null,
      dietary_preferences: form.dietary_preferences || null,
      favorite_stores: form.favorite_stores || null,
    };

    console.log("Register payload:", payload);

    try {
      await register(payload);
      navigate("/");
    } catch (err) {
      const backendError = err.response?.data;
      console.error("Registration failed:", backendError || err);
      alert(formatErrors(backendError));
    }
  };

  return (
    <div className="form-card">
      <h1>Create New Account</h1>

      <form onSubmit={handleSubmit}>
        {step === 1 && (
          <>
            <label>Username</label>
            <input name="username" value={form.username} onChange={handleChange} required />

            <label>Email</label>
            <input name="email" value={form.email} onChange={handleChange} />

            <label>First Name</label>
            <input name="first_name" value={form.first_name} onChange={handleChange} />

            <label>Last Name</label>
            <input name="last_name" value={form.last_name} onChange={handleChange} />

            <label>Password</label>
            <input type="password" name="password" value={form.password} onChange={handleChange} required />

            <label>Confirm Password</label>
            <input type="password" name="password_confirm" value={form.password_confirm} onChange={handleChange} required />

            <button type="button" className="primary-btn" onClick={() => setStep(2)}>
              Next
            </button>
          </>
        )}

        {step === 2 && (
          <>
            <label>Date of Birth</label>
            <input type="date" name="date_of_birth" value={form.date_of_birth} onChange={handleChange} />

            <label>Height (inches)</label>
            <input type="number" name="height" value={form.height} onChange={handleChange} />

            <label>Activity Level (1-5)</label>
            <input type="number" name="activity_level" value={form.activity_level} onChange={handleChange} />

            <label>Dietary Preferences</label>
            <input name="dietary_preferences" value={form.dietary_preferences} onChange={handleChange} />

            <label>Favorite Stores</label>
            <input name="favorite_stores" value={form.favorite_stores} onChange={handleChange} />

            <div className="form-actions">
              <button type="button" className="secondary-btn" onClick={() => setStep(1)}>
                Back
              </button>
              <button type="submit" className="primary-btn">
                Sign Up
              </button>
            </div>
          </>
        )}
      </form>
    </div>
  );
}

export default RegisterForm;
