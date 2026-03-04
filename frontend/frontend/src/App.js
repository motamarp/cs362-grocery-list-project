import React, { useState, useEffect } from "react";

const App = () => {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [recipes, setRecipes] = useState([]);
  const [form, setForm] = useState({
    username: "",
    password: "",
    password_confirm: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
    height: "",
    weight: "",
    sex: "",
    activity_level: "",
    dietary_preferences: [],
    meal_preferences: ""
  });
  const [newRecipe, setNewRecipe] = useState("");

  useEffect(() => {
    if (token) fetchRecipes();
  }, [token]);

  const fetchRecipes = async () => {
    const res = await fetch("/api/recipes/", {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      setRecipes(data);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === "checkbox") {
      let newPrefs = [...form.dietary_preferences];
      if (checked) newPrefs.push(value);
      else newPrefs = newPrefs.filter((v) => v !== value);
      setForm({ ...form, dietary_preferences: newPrefs });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleLogin = async () => {
    const res = await fetch("/api/token/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: form.username, password: form.password })
    });
    const data = await res.json();
    if (data.access) {
      setToken(data.access);
      localStorage.setItem("token", data.access);
      fetchRecipes();
    } else {
      alert("Login failed. Check username/password.");
    }
  };

  const handleRegister = async () => {
    const res = await fetch("/api/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });
    const data = await res.json();
    if (res.status === 201) {
      alert("User registered! Log in now.");
    } else {
      let errorMsg = "Registration failed.\n";
      if (data.username) errorMsg += `Username: ${data.username.join(" ")}\n`;
      if (data.password) errorMsg += `Password: ${data.password.join(" ")}\n`;
      if (data.non_field_errors) errorMsg += data.non_field_errors.join(" ");
      alert(errorMsg);
    }
  };

  const handleAddRecipe = async () => {
    if (!newRecipe) return;
    const res = await fetch("/api/recipes/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ name: newRecipe })
    });
    if (res.ok) {
      setNewRecipe("");
      fetchRecipes();
    }
  };

  const handleDeleteRecipe = async (id) => {
    const res = await fetch(`/api/recipes/${id}/`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) fetchRecipes();
  };

  const formStyle = {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    backgroundColor: "#e0f7e9",
    padding: "20px",
    borderRadius: "10px",
    color: "#004d00"
  };

  const inputStyle = {
    padding: "8px",
    borderRadius: "5px",
    border: "1px solid #004d00",
    outline: "none",
    width: "100%"
  };

  const buttonStyle = {
    padding: "10px",
    borderRadius: "5px",
    border: "none",
    backgroundColor: "#4caf50",
    color: "white",
    cursor: "pointer"
  };

  if (!token)
    return (
      <div style={{ padding: 20, fontFamily: "Arial", maxWidth: 600, margin: "auto" }}>
        <h2>LettuceSave Login / Register</h2>
        <div style={formStyle}>
          <h3>Login</h3>
          <input style={inputStyle} name="username" placeholder="Username" onChange={handleInputChange} />
          <input style={inputStyle} name="password" type="password" placeholder="Password" onChange={handleInputChange} />
          <button style={buttonStyle} onClick={handleLogin}>Sign In</button>

          <h3>Register</h3>
          <input style={inputStyle} name="username" placeholder="Username" onChange={handleInputChange} />
          <input style={inputStyle} name="password" type="password" placeholder="Password" onChange={handleInputChange} />
          <input style={inputStyle} name="password_confirm" type="password" placeholder="Confirm Password" onChange={handleInputChange} />
          <input style={inputStyle} name="first_name" placeholder="First Name" onChange={handleInputChange} />
          <input style={inputStyle} name="last_name" placeholder="Last Name" onChange={handleInputChange} />
          <input style={inputStyle} name="date_of_birth" type="date" placeholder="DOB" onChange={handleInputChange} />
          <input style={inputStyle} name="height" placeholder="Height (inches)" onChange={handleInputChange} />
          <input style={inputStyle} name="weight" placeholder="Weight (lbs)" onChange={handleInputChange} />
          <select style={inputStyle} name="sex" onChange={handleInputChange}>
            <option value="">Select Sex</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
          <select style={inputStyle} name="activity_level" onChange={handleInputChange}>
            <option value="">Activity Level</option>
            <option value="0">0 days</option>
            <option value="1-2">1-2x/week</option>
            <option value="3-4">3-4x/week</option>
            <option value="5+">5+ times/week</option>
          </select>
          <label>Dietary Preferences:</label>
          {["N/A", "Vegan", "Lactose Intolerance", "Other"].map((d) => (
            <div key={d}>
              <input
                type="checkbox"
                value={d}
                checked={form.dietary_preferences.includes(d)}
                onChange={handleInputChange}
              /> {d}
            </div>
          ))}
          <textarea
            style={inputStyle}
            name="meal_preferences"
            placeholder="Preferred meals"
            onChange={handleInputChange}
          />
          <button style={buttonStyle} onClick={handleRegister}>Register</button>
        </div>
      </div>
    );

  return (
    <div style={{ padding: 20, fontFamily: "Arial", maxWidth: 600, margin: "auto" }}>
      <h2>Your Recipes</h2>
      <input
        style={{ ...inputStyle, marginBottom: "10px" }}
        placeholder="New Recipe"
        value={newRecipe}
        onChange={(e) => setNewRecipe(e.target.value)}
      />
      <button style={buttonStyle} onClick={handleAddRecipe}>Add Recipe</button>
      <ul>
        {recipes.map((r) => (
          <li key={r.id}>
            {r.name} <button style={{ ...buttonStyle, backgroundColor: "#f44336" }} onClick={() => handleDeleteRecipe(r.id)}>Delete</button>
          </li>
        ))}
      </ul>
      <button style={buttonStyle} onClick={() => { setToken(""); localStorage.removeItem("token"); }}>Log Out</button>
    </div>
  );
};

export default App;
