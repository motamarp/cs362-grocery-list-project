import React from "react";
import { Link } from "react-router-dom";

function Dashboard() {
  return (
    <div>
      <section className="hero">
        <div>
          <h1>Plan smarter. Shop faster.</h1>
          <p>
            Build meal plans, organize groceries, and compare items in one place.
          </p>
          <div className="hero-actions">
            <Link to="/mealplans" className="primary-btn">Open Meal Plans</Link>
            <Link to="/groceries" className="secondary-btn">View Grocery List</Link>
          </div>
        </div>
      </section>

      <section className="dashboard-grid">
        <div className="panel">
          <h2>Meal Plan</h2>
          <p>Review weekly meals and make swaps.</p>
          <Link to="/mealplans" className="panel-link">Go to Meal Plans</Link>
        </div>

        <div className="panel">
          <h2>Grocery List</h2>
          <p>Track ingredients, prices, and purchase status.</p>
          <Link to="/groceries" className="panel-link">Go to Grocery List</Link>
        </div>

        <div className="panel">
          <h2>Recipes</h2>
          <p>Browse recipe options for your plan.</p>
          <Link to="/recipes" className="panel-link">Browse Recipes</Link>
        </div>

        <div className="panel">
          <h2>Create Account</h2>
          <p>Set up profile preferences and restrictions.</p>
          <Link to="/register" className="panel-link">Register</Link>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
