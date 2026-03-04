import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/")
      .then(response => {
        setMessage("Backend Connected!");
      })
      .catch(error => {
        setMessage("Backend NOT connected");
      });
  }, []);

  return (
    <div style={{ padding: "40px" }}>
      <h1>LettuceSave</h1>
      <h2>{message}</h2>
    </div>
  );
}

export default App;
