import React, { useEffect, useState } from "react";
import {
  getRecipes,
  createRecipe,
  updateRecipe,
  deleteRecipe,
  unwrapResults,
} from "../api/api";

const blankForm = {
  name: "",
  description: "",
  meal_type: "dinner",
  prep_time_minutes: "",
  cook_time_minutes: "",
  difficulty: "easy",
  estimated_cost: "",
  instructions: "",
  nutrition: {
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
  },
  dietary_tags: [],
};

function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [form, setForm] = useState(blankForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRecipes = async () => {
    try {
      const res = await getRecipes();
      setRecipes(unwrapResults(res));
    } catch (err) {
      console.error("Failed to fetch recipes:", err);
    }
  };

  useEffect(() => {
    fetchRecipes();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (["calories", "protein", "carbs", "fat"].includes(name)) {
      setForm((prev) => ({
        ...prev,
        nutrition: {
          ...prev.nutrition,
          [name]: Number(value || 0),
        },
      }));
      return;
    }

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const resetForm = () => {
    setForm(blankForm);
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      ...form,
      prep_time_minutes: form.prep_time_minutes ? Number(form.prep_time_minutes) : null,
      cook_time_minutes: form.cook_time_minutes ? Number(form.cook_time_minutes) : null,
      estimated_cost: form.estimated_cost || null,
      dietary_tags: form.dietary_tags.length ? form.dietary_tags : [],
    };

    try {
      if (editingId) {
        await updateRecipe(editingId, payload);
      } else {
        await createRecipe(payload);
      }
      resetForm();
      await fetchRecipes();
    } catch (err) {
      console.error("Failed to save recipe:", err.response?.data || err);
      alert("Could not save recipe. Check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (recipe) => {
    setEditingId(recipe.id);
    setForm({
      name: recipe.name || "",
      description: recipe.description || "",
      meal_type: recipe.meal_type || "dinner",
      prep_time_minutes: recipe.prep_time_minutes || "",
      cook_time_minutes: recipe.cook_time_minutes || "",
      difficulty: recipe.difficulty || "easy",
      estimated_cost: recipe.estimated_cost || "",
      instructions: recipe.instructions || "",
      nutrition: {
        calories: recipe.nutrition?.calories || 0,
        protein: recipe.nutrition?.protein || 0,
        carbs: recipe.nutrition?.carbs || 0,
        fat: recipe.nutrition?.fat || 0,
      },
      dietary_tags: recipe.dietary_tags || [],
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm("Delete this recipe?");
    if (!confirmed) return;

    try {
      await deleteRecipe(id);
      await fetchRecipes();
      if (editingId === id) resetForm();
    } catch (err) {
      console.error("Failed to delete recipe:", err);
      alert("Could not delete recipe.");
    }
  };

  return (
    <div>
      <h1 className="page-title">Recipes</h1>

      <div className="panel form-panel">
        <h2>{editingId ? "Edit Recipe" : "Add Recipe"}</h2>
        <form className="grid-form" onSubmit={handleSubmit}>
          <input name="name" placeholder="Recipe name" value={form.name} onChange={handleChange} required />
          <input
            name="description"
            placeholder="Description"
            value={form.description}
            onChange={handleChange}
          />

          <select name="meal_type" value={form.meal_type} onChange={handleChange}>
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </select>

          <select name="difficulty" value={form.difficulty} onChange={handleChange}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <input
            type="number"
            name="prep_time_minutes"
            placeholder="Prep time"
            value={form.prep_time_minutes}
            onChange={handleChange}
          />
          <input
            type="number"
            name="cook_time_minutes"
            placeholder="Cook time"
            value={form.cook_time_minutes}
            onChange={handleChange}
          />

          <input
            type="number"
            name="estimated_cost"
            placeholder="Estimated cost"
            value={form.estimated_cost}
            onChange={handleChange}
          />
          <input
            name="instructions"
            placeholder="Instructions"
            value={form.instructions}
            onChange={handleChange}
          />

          <input type="number" name="calories" placeholder="Calories" value={form.nutrition.calories} onChange={handleChange} />
          <input type="number" name="protein" placeholder="Protein" value={form.nutrition.protein} onChange={handleChange} />
          <input type="number" name="carbs" placeholder="Carbs" value={form.nutrition.carbs} onChange={handleChange} />
          <input type="number" name="fat" placeholder="Fat" value={form.nutrition.fat} onChange={handleChange} />

          <div className="form-actions full-span">
            {editingId && (
              <button type="button" className="secondary-btn" onClick={resetForm}>
                Cancel
              </button>
            )}
            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? "Saving..." : editingId ? "Update Recipe" : "Create Recipe"}
            </button>
          </div>
        </form>
      </div>

      <div className="card-grid">
        {recipes.length === 0 ? (
          <div className="panel">No recipes found.</div>
        ) : (
          recipes.map((recipe) => (
            <div className="panel" key={recipe.id}>
              <h3>{recipe.name}</h3>
              <p>{recipe.description || "No description provided."}</p>

              <div className="tag-row">
                <span className="tag">{recipe.meal_type}</span>
                <span className="tag">{recipe.difficulty}</span>
                <span className="tag">{recipe.nutrition?.calories || 0} cal</span>
              </div>

              <div className="inline-actions">
                <button className="secondary-btn" onClick={() => handleEdit(recipe)}>
                  Edit
                </button>
                <button className="danger-btn" onClick={() => handleDelete(recipe.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default RecipeList;
