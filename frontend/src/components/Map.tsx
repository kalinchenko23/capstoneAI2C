import React, { useState, useRef } from "react";
import { GoogleMap, useLoadScript } from "@react-google-maps/api";
import MyFormComponent from "./QuerryForm"; // Adjust path if necessary

const mapContainerStyle = {
  width: "100%",
  height: "100%",
};

const defaultCenter = {
  lat: 40.4406,
  lng: -79.9959,
};

function formatEstimatorResult(data: any) {
  if (!data || data.error) {
    return "No valid data available or an error occurred.";
  }
  return (
    <>
      There are a total of{" "}
      <span className="text-yellow-400 font-semibold">{data.places}</span> places found. The reviews will take{" "}
      <span className="text-yellow-400 font-semibold">{data.reviews_time}</span> seconds and cost about{" "}
      <span className="text-yellow-400 font-semibold">${data.reviews_cost}</span>. Photos will take{" "}
      <span className="text-yellow-400 font-semibold">{data.photos_time}</span> seconds and cost about{" "}
      <span className="text-yellow-400 font-semibold">${data.photos_cost}</span>. Total estimates are{" "}
      <span className="text-red-400 font-semibold">{data.time_everything}</span> seconds and{" "}
      <span className="text-red-400 font-semibold">${data.cost_everything}</span>.
    </>
  );
}

const MapWithFormSide = () => {
  const [inputLat, setInputLat] = useState("");
  const [inputLng, setInputLng] = useState("");
  const [search, setSearch] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [boundingBoxPresent, setBoundingBoxPresent] = useState(false);
  const [estimatorResult, setEstimatorResult] = useState<any>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);

  const [bbox, setBbox] = useState<{
    lat_sw: number;
    lng_sw: number;
    lat_ne: number;
    lng_ne: number;
  } | null>(null);

  const rectangleRef = useRef<google.maps.Rectangle | null>(null);
  const historyStack = useRef<google.maps.Rectangle[]>([]);

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: ["drawing", "places"],
  });

  const handleCoordinateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsedLat = parseFloat(inputLat);
    const parsedLng = parseFloat(inputLng);
    if (!isNaN(parsedLat) && !isNaN(parsedLng) && map) {
      map.setCenter({ lat: parsedLat, lng: parsedLng });
      map.setZoom(14);
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
      setEstimatorResult({ error: err.message || "Unknown error" });
    }
  };

  const undoBoundingBox = () => {
    if (rectangleRef.current) {
      rectangleRef.current.setMap(null); // remove current
      rectangleRef.current = null;
    }

    if (historyStack.current.length > 0) {
      const prevRect = historyStack.current.pop()!;
      rectangleRef.current = prevRect;
      prevRect.setMap(map);

      const bounds = prevRect.getBounds();
      if (bounds) {
        setBbox({
          lat_sw: bounds.getSouthWest().lat(),
          lng_sw: bounds.getSouthWest().lng(),
          lat_ne: bounds.getNorthEast().lat(),
          lng_ne: bounds.getNorthEast().lng(),
        });
        setBoundingBoxPresent(true);
      }
    } else {
      setBbox(null);
      setBoundingBoxPresent(false);
    }
  };

  const onLoad = (mapInstance: google.maps.Map) => {
    setMap(mapInstance);

    const drawingManager = new google.maps.drawing.DrawingManager({
      drawingMode: google.maps.drawing.OverlayType.RECTANGLE,
      drawingControl: true,
      drawingControlOptions: {
        position: google.maps.ControlPosition.TOP_CENTER,
        drawingModes: [google.maps.drawing.OverlayType.RECTANGLE],
      },
      rectangleOptions: {
        strokeColor: "#FFC107",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FFC107",
        fillOpacity: 0.35,
        editable: true,
        draggable: true,
      },
    });

    drawingManager.setMap(mapInstance);

    google.maps.event.addListener(drawingManager, 'overlaycomplete', (event: google.maps.drawing.OverlayCompleteEvent) => {
      if (rectangleRef.current) {
        historyStack.current.push(rectangleRef.current);
        rectangleRef.current.setMap(null);
      }

      if (event.type === google.maps.drawing.OverlayType.RECTANGLE) {
        rectangleRef.current = event.overlay as google.maps.Rectangle;
        drawingManager.setDrawingMode(null);

        const updateBounds = () => {
          const bounds = rectangleRef.current!.getBounds();
          if (bounds) {
            setBbox({
              lat_sw: bounds.getSouthWest().lat(),
              lng_sw: bounds.getSouthWest().lng(),
              lat_ne: bounds.getNorthEast().lat(),
              lng_ne: bounds.getNorthEast().lng(),
            });
            setBoundingBoxPresent(true);
          }
        };

        updateBounds();
        rectangleRef.current.addListener("bounds_changed", updateBounds);
      }
    });
  };

  if (loadError) return <div>Error loading maps. Please check your API key and internet connection.</div>;
  if (!isLoaded) return <div>Loading Map...</div>;

  return (
    <div id="map" className="w-full flex flex-col lg:flex-row h-screen bg-gray-900">
      <div className="w-full lg:w-2/3 h-full">
        <GoogleMap mapContainerStyle={mapContainerStyle} center={defaultCenter} zoom={12} onLoad={onLoad} />
      </div>

      <div className="w-full lg:w-1/3 p-6 text-white flex flex-col gap-4 overflow-y-auto">
        <h1 className="text-3xl font-bold text-yellow-400 text-center">Query Interface</h1>

        <form onSubmit={handleCoordinateSubmit} className="flex flex-col gap-2 p-4 bg-gray-800 rounded-lg">
          <h2 className="text-xl font-semibold mb-2 text-gray-300">Find Place</h2>
          <input type="text" value={inputLat} onChange={(e) => setInputLat(e.target.value)} placeholder="Latitude" className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-500" />
          <input type="text" value={inputLng} onChange={(e) => setInputLng(e.target.value)} placeholder="Longitude" className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-500" />
          <button type="submit" className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded">Go to Coordinates</button>
        </form>

        {boundingBoxPresent && (
          <form onSubmit={handleSearchSubmit} className="flex flex-col gap-2 p-4 bg-gray-800 rounded-lg">
            <h2 className="text-xl font-semibold mb-2 text-gray-300">Quick Cost Estimator</h2>
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search Term (e.g., hospitals)" className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-500" />
            <input type="text" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="Google API Key" className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-500" />
            <button type="submit" className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded">Estimate Cost</button>
            <button type="button" onClick={undoBoundingBox} className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white font-semibold rounded mt-2">Undo Last Bounding Box</button>
            {estimatorResult && (
              <div className="p-3 mt-2 bg-gray-700 rounded text-sm"><div className="text-gray-300">{formatEstimatorResult(estimatorResult)}</div></div>
            )}
          </form>
        )}

        <div className="p-4 bg-gray-800 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-300 mb-4">Main Query & Download</h2>
          <MyFormComponent lat_sw={bbox?.lat_sw} lng_sw={bbox?.lng_sw} lat_ne={bbox?.lat_ne} lng_ne={bbox?.lng_ne} map={map} />
        </div>
      </div>
    </div>
  );
};

export default MapWithFormSide;
