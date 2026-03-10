import React, { useEffect, useState } from "react";
import {
  getGroceryLists,
  createGroceryListItem,
  patchGroceryListItem,
  deleteGroceryListItem,
  unwrapResults,
} from "../api/api";

function GroceryList() {
  const [lists, setLists] = useState([]);
  const [selectedListId, setSelectedListId] = useState("");
  const [message, setMessage] = useState(null);
  const [form, setForm] = useState({
    ingredient_name: "",
    quantity: "",
    metric: "",
  });

  const setFlashMessage = (type, text) => {
    setMessage({ type, text });
    window.clearTimeout(window.__lettuceGroceryFlashTimer);
    window.__lettuceGroceryFlashTimer = window.setTimeout(() => {
      setMessage(null);
    }, 2500);
  };

  const fetchLists = async () => {
    try {
      const res = await getGroceryLists();
      const results = unwrapResults(res);
      setLists(results);
      if (!selectedListId && results.length > 0) {
        setSelectedListId(String(results[0].id));
      }
    } catch (err) {
      console.error("Failed to fetch grocery lists:", err);
    }
  };

  useEffect(() => {
    fetchLists();
  }, []);

  const selectedList = lists.find((list) => String(list.id) === String(selectedListId));

  const handleTogglePurchased = async (item) => {
    try {
      await patchGroceryListItem(item.id, {
        is_purchased: !item.is_purchased,
      });
      await fetchLists();
    } catch (err) {
      console.error("Failed to update grocery item:", err);
      setFlashMessage("error", "Could not update grocery item.");
    }
  };

  const handleDeleteItem = async (itemId) => {
    const confirmed = window.confirm("Delete this grocery item?");
    if (!confirmed) return;

    try {
      await deleteGroceryListItem(itemId);
      await fetchLists();
      setFlashMessage("success", "Item deleted.");
    } catch (err) {
      console.error("Failed to delete grocery item:", err);
      setFlashMessage("error", "Could not delete grocery item.");
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!selectedListId) {
      setFlashMessage("error", "Choose a grocery list first.");
      return;
    }

    try {
      await createGroceryListItem({
        grocery_list: Number(selectedListId),
        ingredient_name: form.ingredient_name,
        quantity: Number(form.quantity),
        metric: form.metric,
      });
      setForm({
        ingredient_name: "",
        quantity: "",
        metric: "",
      });
      await fetchLists();
      setFlashMessage("success", "Item added.");
    } catch (err) {
      console.error("Failed to add grocery item:", err.response?.data || err);
      setFlashMessage("error", "Could not add grocery item.");
    }
  };

  return (
    <div>
      <h1 className="page-title">Grocery Lists</h1>

      {message && (
        <div className={`inline-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="panel form-panel">
        <h2>Add Grocery Item</h2>
        <form className="grid-form" onSubmit={handleAddItem}>
          <select value={selectedListId} onChange={(e) => setSelectedListId(e.target.value)}>
            <option value="">Choose grocery list</option>
            {lists.map((list) => (
              <option key={list.id} value={list.id}>
                {list.name}
              </option>
            ))}
          </select>

          <input
            placeholder="Ingredient name"
            value={form.ingredient_name}
            onChange={(e) => setForm((prev) => ({ ...prev, ingredient_name: e.target.value }))}
            required
          />
          <input
            type="number"
            placeholder="Quantity"
            value={form.quantity}
            onChange={(e) => setForm((prev) => ({ ...prev, quantity: e.target.value }))}
            required
          />
          <input
            placeholder="Unit"
            value={form.metric}
            onChange={(e) => setForm((prev) => ({ ...prev, metric: e.target.value }))}
            required
          />

          <div className="form-actions full-span">
            <button type="submit" className="primary-btn">
              Add Item
            </button>
          </div>
        </form>
      </div>

      <div className="two-column">
        <div className="panel">
          <h2>All Grocery Lists</h2>
          {lists.length === 0 ? (
            <p>No grocery lists found.</p>
          ) : (
            lists.map((list) => (
              <div
                key={list.id}
                className={`history-item clickable ${String(selectedListId) === String(list.id) ? "selected-card" : ""}`}
                onClick={() => setSelectedListId(String(list.id))}
              >
                <strong>{list.name}</strong>
                <br />
                Total Cost: ${Number(list.total_cost || 0).toFixed(2)}
              </div>
            ))
          )}
        </div>

        <div className="panel">
          <h2>{selectedList ? selectedList.name : "Choose a Grocery List"}</h2>
          {!selectedList ? (
            <p>No list selected.</p>
          ) : selectedList.items?.length ? (
            selectedList.items.map((item) => (
              <div key={item.id} className="grocery-item-detailed">
                <div className="grocery-item-left">
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={item.is_purchased}
                      onChange={() => handleTogglePurchased(item)}
                    />
                    <span className={item.is_purchased ? "purchased-text" : ""}>
                      <strong>{item.ingredient_name}</strong> — {item.quantity} {item.metric}
                    </span>
                  </label>

                  <div className="grocery-meta">
                    <span><strong>Brand:</strong> {item.brand || "N/A"}</span>
                    <span><strong>Store:</strong> {item.suggested_store_name || "N/A"}</span>
                    <span><strong>Unit Price:</strong> ${item.price_estimate || 0}</span>
                    <span><strong>Total:</strong> ${Number(item.total_price || 0).toFixed(2)}</span>
                  </div>
                </div>

                <button className="danger-btn" onClick={() => handleDeleteItem(item.id)}>
                  Delete
                </button>
              </div>
            ))
          ) : (
            <p>No items in this list yet.</p>
          )}

          {selectedList && (
            <div className="grocery-total-box">
              Total Grocery Cost: ${Number(selectedList.total_cost || 0).toFixed(2)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default GroceryList;
