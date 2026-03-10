import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import RecipeList from "./components/RecipeList";
import MealPlan from "./components/MealPlan";
import MealPlanDetail from "./components/MealPlanDetail";
import GroceryList from "./components/GroceryList";
import RegisterForm from "./components/RegisterForm";
import LoginForm from "./components/LoginForm";
import ProtectedRoute from "./components/ProtectedRoute";
import StoreSearch from "./components/StoreSearch";
import "./App.css";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/recipes"
            element={
              <ProtectedRoute>
                <RecipeList />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mealplans"
            element={
              <ProtectedRoute>
                <MealPlan />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mealplans/:id"
            element={
              <ProtectedRoute>
                <MealPlanDetail />
              </ProtectedRoute>
            }
          />

          <Route
            path="/groceries"
            element={
              <ProtectedRoute>
                <GroceryList />
              </ProtectedRoute>
            }
          />

          <Route
            path="/store-search"
            element={
              <ProtectedRoute>
                <StoreSearch />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
