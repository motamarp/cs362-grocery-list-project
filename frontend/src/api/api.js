import axios from "axios";

const BASE_URL = "http://127.0.0.1:8001/";

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const unwrapResults = (response) => {
  const data = response.data;
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

/* Auth */
export const registerUser = (payload) => api.post("api/auth/register/", payload);
export const loginUser = (payload) => api.post("api/auth/login/", payload);
export const logoutUser = () => api.post("api/auth/logout/");
export const getMe = () => api.get("api/auth/me/");

/* Profile */
export const getMyProfile = () => api.get("api/profiles/me/");
export const updateMyProfile = (payload) => api.patch("api/profiles/me/", payload);

/* Recipes */
export const getRecipes = () => api.get("api/recipes/");
export const createRecipe = (payload) => api.post("api/recipes/", payload);
export const updateRecipe = (id, payload) => api.put(`api/recipes/${id}/`, payload);
export const deleteRecipe = (id) => api.delete(`api/recipes/${id}/`);

/* Meal Plans */
export const getMealPlans = () => api.get("api/mealplans/");
export const getMealPlanById = (id) => api.get(`api/mealplans/${id}/`);
export const createMealPlan = (payload) => api.post("api/mealplans/", payload);
export const deleteMealPlan = (id) => api.delete(`api/mealplans/${id}/`);
export const cloneMealPlan = (id, payload) => api.post(`api/mealplans/${id}/clone/`, payload);
export const activateMealPlan = (id) => api.post(`api/mealplans/${id}/activate/`);

export const generateMealPlan = (payload) => api.post("api/mealplans/generate/", payload);
export const generateGroceryList = (mealPlanId) => api.post(`api/mealplans/${mealPlanId}/generate_grocery_list/`);

/* Planned Meals */
export const createPlannedMeal = (payload) => api.post("api/plannedmeals/", payload);
export const deletePlannedMeal = (id) => api.delete(`api/plannedmeals/${id}/`);

/* Grocery Lists */
export const getGroceryLists = () => api.get("api/groceries/");
export const createGroceryListItem = (payload) => api.post("api/grocery-list-items/", payload);
export const patchGroceryListItem = (id, payload) => api.patch(`api/grocery-list-items/${id}/`, payload);
export const deleteGroceryListItem = (id) => api.delete(`api/grocery-list-items/${id}/`);
export const addItemToActivePlan = (payload) =>
  api.post("api/grocery-list-items/add_to_active_plan/", payload);

/* Store Search */
export const searchStoreIngredients = (query) =>
  api.get(`api/store-ingredients/?search=${encodeURIComponent(query)}`);


