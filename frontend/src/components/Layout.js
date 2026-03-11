import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  FaHome,
  FaUtensils,
  FaClipboardList,
  FaShoppingBasket,
  FaUserPlus,
  FaSignInAlt,
  FaSignOutAlt,
  FaSearchLocation,
} from "react-icons/fa";
import { useAuth } from "../context/AuthContext";

function Layout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Lettuce Save</div>

        <nav className="nav-links">
          {user ? (
            <>
              <Link className={location.pathname === "/" ? "active-link" : ""} to="/">
                <FaHome /> Dashboard
              </Link>
              <Link className={location.pathname === "/recipes" ? "active-link" : ""} to="/recipes">
                <FaUtensils /> Recipes
              </Link>
              <Link className={location.pathname.startsWith("/mealplans") ? "active-link" : ""} to="/mealplans">
                <FaClipboardList /> Meal Plans
              </Link>
              <Link className={location.pathname === "/groceries" ? "active-link" : ""} to="/groceries">
                <FaShoppingBasket /> Grocery Lists
              </Link>
              <Link className={location.pathname === "/store-search" ? "active-link" : ""} to="/store-search">
                <FaSearchLocation /> Store Search
              </Link>
              <button className="nav-button" onClick={handleLogout}>
                <FaSignOutAlt /> Logout
              </button>
            </>
          ) : (
            <>
              <Link className={location.pathname === "/login" ? "active-link" : ""} to="/login">
                <FaSignInAlt /> Login
              </Link>
              <Link className={location.pathname === "/register" ? "active-link" : ""} to="/register">
                <FaUserPlus /> Register
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="page-content">
        {user && (
          <div className="welcome-bar">
            Signed in as <strong>{user.username}</strong>
          </div>
        )}
        {children}
      </main>
    </div>
  );
}

export default Layout;
