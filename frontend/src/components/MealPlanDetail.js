import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getMealPlanById,
  getRecipes,
  createPlannedMeal,
  deletePlannedMeal,
  unwrapResults,
} from "../api/api";

const DAYS = [
  { label: "Monday", value: 0 },
  { label: "Tuesday", value: 1 },
  { label: "Wednesday", value: 2 },
  { label: "Thursday", value: 3 },
  { label: "Friday", value: 4 },
  { label: "Saturday", value: 5 },
  { label: "Sunday", value: 6 },
];

function MealPlanDetail() {
  const { id } = useParams();
  const [mealPlan, setMealPlan] = useState(null);
  const [recipes, setRecipes] = useState([]);
  const [form, setForm] = useState({
    day_of_week: 0,
    meal_type: "breakfast",
    recipe: "",
    custom_notes: "",
    was_completed: false,
  });

  const fetchMealPlan = async () => {
    try {
      const res = await getMealPlanById(id);
      setMealPlan(res.data);
    } catch (err) {
      console.error("Failed to fetch meal plan:", err);
    }
  };

  const fetchRecipes = async () => {
    try {
      const res = await getRecipes();
      setRecipes(unwrapResults(res));
    } catch (err) {
      console.error("Failed to fetch recipes:", err);
    }
  };

  useEffect(() => {
    fetchMealPlan();
    fetchRecipes();
  }, [id]);

  const groupedMeals = useMemo(() => {
    if (!mealPlan?.meals) return {};
    return mealPlan.meals.reduce((acc, meal) => {
      const key = meal.day_name || DAYS.find((d) => d.value === meal.day_of_week)?.label || "Unknown";
      if (!acc[key]) acc[key] = [];
      acc[key].push(meal);
      return acc;
    }, {});
  }, [mealPlan]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleAddMeal = async (e) => {
    e.preventDefault();

    try {
      await createPlannedMeal({
        meal_plan: Number(id),
        day_of_week: Number(form.day_of_week),
        meal_type: form.meal_type,
        recipe: Number(form.recipe),
        custom_notes: form.custom_notes,
        was_completed: form.was_completed,
      });
      setForm({
        day_of_week: 0,
        meal_type: "breakfast",
        recipe: "",
        custom_notes: "",
        was_completed: false,
      });
      await fetchMealPlan();
    } catch (err) {
      console.error("Failed to add planned meal:", err.response?.data || err);
      alert("Could not add meal. This can also happen if that day/meal slot already exists.");
    }
  };

  const handleDeleteMeal = async (mealId) => {
    const confirmed = window.confirm("Delete this planned meal?");
    if (!confirmed) return;

    try {
      await deletePlannedMeal(mealId);
      await fetchMealPlan();
    } catch (err) {
      console.error("Failed to delete planned meal:", err);
      alert("Could not delete planned meal.");
    }
  };

  return (
    <div>
      <h1 className="page-title">Meal Plan Detail</h1>

      {mealPlan && (
        <div className="panel">
          <h2>Week of {mealPlan.week_start_date}</h2>
          <p>Active: {mealPlan.is_active ? "Yes" : "No"}</p>
          <p>Total Cost Estimate: ${mealPlan.total_cost_estimate || "0.00"}</p>
        </div>
      )}

      <div className="panel form-panel">
        <h2>Add Meal To Plan</h2>
        <form className="grid-form" onSubmit={handleAddMeal}>
          <select name="day_of_week" value={form.day_of_week} onChange={handleChange}>
            {DAYS.map((day) => (
              <option key={day.value} value={day.value}>
                {day.label}
              </option>
            ))}
          </select>

          <select name="meal_type" value={form.meal_type} onChange={handleChange}>
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </select>

          <select name="recipe" value={form.recipe} onChange={handleChange} required>
            <option value="">Select recipe</option>
            {recipes.map((recipe) => (
              <option key={recipe.id} value={recipe.id}>
                {recipe.name}
              </option>
            ))}
          </select>

          <input
            name="custom_notes"
            placeholder="Custom notes"
            value={form.custom_notes}
            onChange={handleChange}
          />

          <label className="checkbox-row full-span">
            <input
              type="checkbox"
              name="was_completed"
              checked={form.was_completed}
              onChange={handleChange}
            />
            Mark completed
          </label>

          <div className="form-actions full-span">
            <button type="submit" className="primary-btn">
              Add Meal
            </button>
          </div>
        </form>
      </div>

      <div className="card-grid">
        {DAYS.map((day) => (
          <div className="panel" key={day.label}>
            <h3>{day.label}</h3>
            {(groupedMeals[day.label] || []).length === 0 ? (
              <p>No meals added.</p>
            ) : (
              groupedMeals[day.label].map((meal) => (
                <div className="meal-entry" key={meal.id}>
                  <strong>{meal.meal_type}</strong>
                  <p>{meal.recipe_details?.name || "No recipe"}</p>
                  <p>{meal.custom_notes || "No notes"}</p>
                  <button className="danger-btn" onClick={() => handleDeleteMeal(meal.id)}>
                    Delete
                  </button>
                </div>
              ))
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default MealPlanDetail;
