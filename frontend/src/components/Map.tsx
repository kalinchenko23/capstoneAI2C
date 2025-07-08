import React, { useState, useRef, useEffect } from "react";
import { GoogleMap, useLoadScript } from "@react-google-maps/api";
import MyFormComponent from "./QuerryForm";

const containerStyle = {
  width: "100%",
  height: "100%",
};

const defaultCenter = {
  lat: 40.4406,
  lng: -79.9959,
};

function formatEstimatorResult(data: any) {
  if (!data || data.error) return "No valid data available.";

  return (
    <>
      There are total of{" "}
      <span className="text-yellow-400 font-semibold">{data.places}</span> places found in your bounding box, the reviews will take{" "}
      <span className="text-yellow-400 font-semibold">{data.reviews_time}</span> seconds and will cost about{" "}
      <span className="text-yellow-400 font-semibold">{data.reviews_cost}</span> dollars. Photos will take{" "}
      <span className="text-yellow-400 font-semibold">{data.photos_time}</span> seconds and will cost about{" "}
      <span className="text-yellow-400 font-semibold">{data.photos_cost}</span> dollars. Total estimates for the query with reviews and photos are{" "}
      <span className="text-red-400 font-semibold">{data.time_everything}</span> seconds and{" "}
      <span className="text-red-400 font-semibold">{data.cost_everything}</span> dollars.
    </>
  );
}

const MapWithFormSide = () => {
  const [lat, setLat] = useState<number | undefined>();
  const [lng, setLng] = useState<number | undefined>();
  const [inputLat, setInputLat] = useState("");
  const [inputLng, setInputLng] = useState("");
  const [search, setSearch] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [boundingBoxPresent, setBoundingBoxPresent] = useState(false);
  const [estimatorResult, setEstimatorResult] = useState<any>(null);

  // New state to store bounding box coordinates reactively
  const [bbox, setBbox] = useState<{
    lat_sw: number;
    lng_sw: number;
    lat_ne: number;
    lng_ne: number;
  } | null>(null);

const { isLoaded } = useLoadScript({
  googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
});


  const mapRef = useRef<google.maps.Map | null>(null);
  const rectangleRef = useRef<google.maps.Rectangle | null>(null);
  const startPoint = useRef<google.maps.LatLngLiteral | null>(null);
  const drawing = useRef(false);

  useEffect(() => {
    if (mapRef.current && lat && lng) {
      mapRef.current.setCenter({ lat, lng });
    }
  }, [lat, lng]);

  const handleCoordinateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsedLat = parseFloat(inputLat);
    const parsedLng = parseFloat(inputLng);
    if (!isNaN(parsedLat) && !isNaN(parsedLng)) {
      setLat(parsedLat);
      setLng(parsedLng);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bbox) return;

    const requestBody = {
      text_query: search,
      lat_sw: bbox.lat_sw,
      lng_sw: bbox.lng_sw,
      lat_ne: bbox.lat_ne,
      lng_ne: bbox.lng_ne,
      google_api_key: apiKey,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/estimator", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();
      setEstimatorResult(data);
    } catch (err: any) {
      console.error("Failed to fetch from /estimator:", err);
      setEstimatorResult({ error: err.message || "Unknown error" });
    }
  };

  const onLoad = (map: google.maps.Map) => {
    mapRef.current = map;

    const handleMouseDown = (e: google.maps.MapMouseEvent) => {
      if (!e.latLng) return;
      drawing.current = true;
      startPoint.current = e.latLng.toJSON();

      if (rectangleRef.current) {
        rectangleRef.current.setMap(null);
        rectangleRef.current = null;
      }

      const rect = new google.maps.Rectangle({
        bounds: new google.maps.LatLngBounds(startPoint.current, startPoint.current),
        map: map,
        strokeColor: "black",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "yellow",
        fillOpacity: 0.35,
        editable: true,
      });

      rectangleRef.current = rect;

      // Initialize bbox state with current bounds
      const bounds = rect.getBounds();
      if (bounds) {
        setBbox({
          lat_sw: bounds.getSouthWest().lat(),
          lng_sw: bounds.getSouthWest().lng(),
          lat_ne: bounds.getNorthEast().lat(),
          lng_ne: bounds.getNorthEast().lng(),
        });
      }

      // Add listener to update bbox when rectangle is resized/moved
      rect.addListener("bounds_changed", () => {
        const b = rect.getBounds();
        if (b) {
          setBbox({
            lat_sw: b.getSouthWest().lat(),
            lng_sw: b.getSouthWest().lng(),
            lat_ne: b.getNorthEast().lat(),
            lng_ne: b.getNorthEast().lng(),
          });
        }
      });

      setBoundingBoxPresent(true);
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!drawing.current || !startPoint.current || !mapRef.current) return;

      const projection = mapRef.current.getProjection();
      if (!projection) return;

      const boundsRect = mapRef.current.getDiv().getBoundingClientRect();
      const point = new google.maps.Point(e.clientX - boundsRect.left, e.clientY - boundsRect.top);
      const moveLatLng = projection.fromContainerPixelToLatLng(point);
      if (!moveLatLng || !rectangleRef.current) return;

      const bounds = new google.maps.LatLngBounds(startPoint.current, moveLatLng.toJSON());
      rectangleRef.current.setBounds(bounds);
    };

    const handleMouseUp = () => {
      if (drawing.current) {
        drawing.current = false;
        startPoint.current = null;
      }
    };

    map.addListener("idle", () => {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    });

    map.addListener("mousedown", handleMouseDown);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  };

  if (!isLoaded) return <div>Loading Map...</div>;

  return (
    <div id="map" className="w-full flex flex-col items-center">
      <div className="w-full flex flex-col lg:flex-row">
        {/* Map Section */}
        <div  className="w-full lg:w-2/3">
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={lat && lng ? { lat, lng } : defaultCenter}
            zoom={13}
            onLoad={onLoad}
          />
        </div>

        {/* Right-Side Forms */}
        <div className="w-full lg:w-1/3 p-6 bg-gray-900 text-white flex flex-col gap-6">
          {/* Find place form */}
          <form onSubmit={handleCoordinateSubmit}>
            <h2 className="text-2xl font-bold mb-4 text-gray-300 text-center">Find place by coordinates (optional)</h2>
            <div className="flex flex-col gap-4">
              <input
                type="text"
                value={inputLat}
                onChange={(e) => setInputLat(e.target.value)}
                placeholder="Latitude"
                className="p-2 rounded bg-gray-800 border border-gray-700"
              />
              <input
                type="text"
                value={inputLng}
                onChange={(e) => setInputLng(e.target.value)}
                placeholder="Longitude"
                className="p-2 rounded bg-gray-800 border border-gray-700"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded"
              >
                Go
              </button>
            </div>
          </form>

          {/* Quick Validation Form */}
          {boundingBoxPresent && (
            <form onSubmit={handleSearchSubmit}>
              <h2 className="text-xl font-bold mb-4 text-gray-300 text-center">Quick Validation (optional)</h2>
              <div className="flex flex-col gap-4 mb-4">
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search (e.g. hospitals)"
                  className="p-2 rounded bg-gray-800 border border-gray-700"
                />
                <input
                  type="text"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Google API Key"
                  className="p-2 rounded bg-gray-800 border border-gray-700"
                />
                <button
                  type="submit"
                  className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded"
                >
                  Look up
                </button>
              </div>

              {estimatorResult && (
                <div className="p-4 bg-gray-800 rounded text-sm">
                  <h3 className="font-semibold mb-2">Look Up Response:</h3>
                  <div className="text-gray-300">{formatEstimatorResult(estimatorResult)}</div>
                </div>
              )}
            </form>
          )}

          {/* MyFormComponent with reactive bounding box */}
          <h2 className="text-xl font-bold text-gray-300 text-center">Custom Query</h2>
          <MyFormComponent
            lat_sw={bbox?.lat_sw}
            lng_sw={bbox?.lng_sw}
            lat_ne={bbox?.lat_ne}
            lng_ne={bbox?.lng_ne}
          />
        </div>
      </div>
    </div>
  );
};

export default MapWithFormSide;
