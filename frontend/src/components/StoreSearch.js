import React, { useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import {
  searchStoreIngredients,
  unwrapResults,
  addItemToActivePlan,
} from "../api/api";

function toRadians(degrees) {
  return degrees * (Math.PI / 180);
}

function calculateDistanceMiles(lat1, lon1, lat2, lon2) {
  if (
    lat1 == null || lon1 == null ||
    lat2 == null || lon2 == null
  ) {
    return null;
  }

  const earthRadiusMiles = 3958.8;
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return (earthRadiusMiles * c).toFixed(2);
}

function StoreSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedResultId, setSelectedResultId] = useState(null);
  const [quantities, setQuantities] = useState({});
  const [message, setMessage] = useState(null);

  const setFlashMessage = (type, text) => {
    setMessage({ type, text });
    window.clearTimeout(window.__lettuceFlashTimer);
    window.__lettuceFlashTimer = window.setTimeout(() => {
      setMessage(null);
    }, 2500);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);

    try {
      const res = await searchStoreIngredients(query);
      const parsed = unwrapResults(res);
      setResults(parsed);
      setSelectedResultId(parsed.length > 0 ? parsed[0].id : null);

      const initialQuantities = {};
      parsed.forEach((item) => {
        initialQuantities[item.id] = 1;
      });
      setQuantities(initialQuantities);
    } catch (err) {
      console.error("Store search failed:", err.response?.data || err);
      setFlashMessage("error", "Could not search store inventory.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      setFlashMessage("error", "Geolocation is not supported by your browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setFlashMessage("success", "Location updated.");
      },
      () => {
        setFlashMessage("error", "Could not get your location.");
      }
    );
  };

  const handleQuantityChange = (itemId, value) => {
    setQuantities((prev) => ({
      ...prev,
      [itemId]: value,
    }));
  };

  const handleAddItem = async (item) => {
    const qty = Number(quantities[item.id] || 1);

    if (!qty || qty <= 0) {
      setFlashMessage("error", "Please enter a quantity greater than 0.");
      return;
    }

    try {
      await addItemToActivePlan({
        ingredient_name: item.ingredient_name,
        quantity: qty,
        metric: item.price_unit || "each",
        suggested_store: item.store,
        price_estimate: item.price,
        brand: item.brand || "",
      });

      setFlashMessage(
        "success",
        `${item.ingredient_name} added to your active meal plan grocery list.`
      );
    } catch (err) {
      console.error("Add item failed:", err.response?.data || err);
      setFlashMessage(
        "error",
        err.response?.data?.error ||
          "Could not add item to the active meal plan grocery list."
      );
    }
  };

  const uniqueStoreMarkers = useMemo(() => {
    const seen = new Map();

    results.forEach((item) => {
      const key = `${item.store}-${item.store_latitude}-${item.store_longitude}`;
      if (!seen.has(key)) {
        seen.set(key, {
          id: item.id,
          storeId: item.store,
          storeName: item.store_name,
          address: item.store_address,
          lat: item.store_latitude,
          lng: item.store_longitude,
        });
      }
    });

    return Array.from(seen.values());
  }, [results]);

  const mapCenter = useMemo(() => {
    if (selectedResultId) {
      const selected = results.find((r) => r.id === selectedResultId);
      if (selected?.store_latitude && selected?.store_longitude) {
        return [selected.store_latitude, selected.store_longitude];
      }
    }
    return [44.5646, -123.2620];
  }, [results, selectedResultId]);

  return (
    <div>
      <h1 className="page-title">Store Search</h1>

      {message && (
        <div className={`inline-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="panel form-panel">
        <form className="search-row" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search grocery item..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
          <button className="secondary-btn" type="button" onClick={handleGetLocation}>
            Use My Location
          </button>
        </form>
      </div>

      <div className="search-layout">
        <div className="panel">
          <h2>Results</h2>

          {results.length === 0 ? (
            <p>No results yet. Search for an item like milk, eggs, pasta, coffee, or bread.</p>
          ) : (
            results.map((item) => {
              const distance =
                userLocation &&
                calculateDistanceMiles(
                  userLocation.latitude,
                  userLocation.longitude,
                  item.store_latitude,
                  item.store_longitude
                );

              const isSelected = item.id === selectedResultId;

              return (
                <div
                  className={`store-result-card ${isSelected ? "selected-store-card" : ""}`}
                  key={item.id}
                  onClick={() => setSelectedResultId(item.id)}
                >
                  <h3>{item.store_name}</h3>
                  <p><strong>Item:</strong> {item.ingredient_name}</p>
                  <p><strong>Brand:</strong> {item.brand || "N/A"}</p>
                  <p><strong>Price:</strong> ${item.price} / {item.price_unit}</p>
                  <p><strong>In Stock:</strong> {item.in_stock ? "Yes" : "No"}</p>
                  <p><strong>Address:</strong> {item.store_address}</p>
                  <p><strong>Distance:</strong> {distance ? `${distance} miles` : "Click 'Use My Location'"}</p>

                  <div
                    className="result-actions"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <label className="quantity-label">
                      Qty:
                      <input
                        type="number"
                        min="1"
                        value={quantities[item.id] || 1}
                        onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                      />
                    </label>

                    <button
                      type="button"
                      className="add-btn"
                      onClick={() => handleAddItem(item)}
                    >
                      + Add
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="panel">
          <h2>Map Area</h2>
          <div className="map-wrapper">
            <MapContainer
              center={mapCenter}
              zoom={13}
              scrollWheelZoom={true}
              className="leaflet-map"
            >
              <TileLayer
                attribution='&copy; OpenStreetMap contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {uniqueStoreMarkers.map((marker) => {
                const relatedSelectedResult = results.find((r) => r.id === selectedResultId);
                const isHighlighted =
                  relatedSelectedResult &&
                  relatedSelectedResult.store === marker.storeId;

                return (
                  <CircleMarker
                    key={`${marker.storeId}-${marker.lat}-${marker.lng}`}
                    center={[marker.lat, marker.lng]}
                    radius={isHighlighted ? 14 : 9}
                    pathOptions={{
                      color: isHighlighted ? "#ff7f11" : "#2f8fdf",
                      fillColor: isHighlighted ? "#ff7f11" : "#2f8fdf",
                      fillOpacity: 0.8,
                    }}
                    eventHandlers={{
                      click: () => {
                        const firstMatch = results.find((r) => r.store === marker.storeId);
                        if (firstMatch) {
                          setSelectedResultId(firstMatch.id);
                        }
                      },
                    }}
                  >
                    <Popup>
                      <strong>{marker.storeName}</strong>
                      <br />
                      {marker.address}
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StoreSearch;
