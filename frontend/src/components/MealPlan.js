import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getMealPlans,
  createMealPlan,
  deleteMealPlan,
  cloneMealPlan,
  activateMealPlan,
  unwrapResults,
} from "../api/api";

function MealPlan() {
  const [plans, setPlans] = useState([]);
  const [weekStartDate, setWeekStartDate] = useState("");
  const [cloneDates, setCloneDates] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const setFlashMessage = (type, text) => {
    setMessage({ type, text });
    window.clearTimeout(window.__lettuceMealPlanFlashTimer);
    window.__lettuceMealPlanFlashTimer = window.setTimeout(() => {
      setMessage(null);
    }, 2500);
  };

  const fetchPlans = async () => {
    try {
      const res = await getMealPlans();
      setPlans(unwrapResults(res));
    } catch (err) {
      console.error("Failed to fetch meal plans:", err);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const activePlan = plans.find((plan) => plan.is_active);
  const archivedPlans = plans.filter((plan) => !plan.is_active);

  const handleCreate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await createMealPlan({
        week_start_date: weekStartDate,
        total_cost_estimate: "0.00",
        is_active: true,
      });
      setWeekStartDate("");
      await fetchPlans();
      setFlashMessage("success", "New meal plan created and activated.");
    } catch (err) {
      console.error("Failed to create meal plan:", err.response?.data || err);
      setFlashMessage("error", "Could not create meal plan.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm("Delete this meal plan?");
    if (!confirmed) return;

    try {
      await deleteMealPlan(id);
      await fetchPlans();
      setFlashMessage("success", "Meal plan deleted.");
    } catch (err) {
      console.error("Failed to delete meal plan:", err);
      setFlashMessage("error", "Could not delete meal plan.");
    }
  };

  const handleClone = async (id) => {
    const chosenDate = cloneDates[id];
    if (!chosenDate) {
      setFlashMessage("error", "Choose a new week start date first.");
      return;
    }

    try {
      await cloneMealPlan(id, { week_start_date: chosenDate });
      await fetchPlans();
      setFlashMessage("success", "Meal plan cloned and activated.");
    } catch (err) {
      console.error("Failed to clone meal plan:", err.response?.data || err);
      setFlashMessage("error", "Could not clone meal plan.");
    }
  };

  const handleActivate = async (id) => {
    try {
      await activateMealPlan(id);
      await fetchPlans();
      setFlashMessage("success", "Meal plan activated.");
    } catch (err) {
      console.error("Failed to activate meal plan:", err.response?.data || err);
      setFlashMessage("error", "Could not activate meal plan.");
    }
  };

  return (
    <div>
      <h1 className="page-title">Meal Plans</h1>

      {message && (
        <div className={`inline-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="panel form-panel">
        <h2>Create Meal Plan</h2>
        <form className="grid-form" onSubmit={handleCreate}>
          <input
            type="date"
            value={weekStartDate}
            onChange={(e) => setWeekStartDate(e.target.value)}
            required
          />

          <div className="form-actions full-span">
            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? "Creating..." : "Create Meal Plan"}
            </button>
          </div>
        </form>
      </div>

      <div className="two-column">
        <div className="panel">
          <h2>Archived History</h2>
          {archivedPlans.length === 0 ? (
            <p>No archived meal plans.</p>
          ) : (
            archivedPlans.map((plan) => (
              <div className="history-item" key={plan.id}>
                <strong>Week:</strong> {plan.week_start_date}
                <br />
                <strong>Active:</strong> No

                <div className="clone-row">
                  <input
                    type="date"
                    value={cloneDates[plan.id] || ""}
                    onChange={(e) =>
                      setCloneDates((prev) => ({
                        ...prev,
                        [plan.id]: e.target.value,
                      }))
                    }
                  />
                  <button className="secondary-btn" onClick={() => handleClone(plan.id)}>
                    Clone Plan
                  </button>
                </div>

                <div className="inline-actions">
                  <button className="secondary-btn" onClick={() => handleActivate(plan.id)}>
                    Activate
                  </button>
                  <Link className="secondary-btn" to={`/mealplans/${plan.id}`}>
                    Open
                  </Link>
                  <button className="danger-btn" onClick={() => handleDelete(plan.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="panel">
          <h2>Current Meal Plan</h2>
          {activePlan ? (
            <>
              <div className="active-plan-summary">
                <strong>Week:</strong> {activePlan.week_start_date}
                <div className="inline-actions">
                  <Link className="secondary-btn" to={`/mealplans/${activePlan.id}`}>
                    Open Active Plan
                  </Link>
                </div>
              </div>

              <div className="weekday-list">
                {["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].map((day) => (
                  <div className="weekday-box" key={day}>
                    {day}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p>No active meal plan yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default MealPlan;
