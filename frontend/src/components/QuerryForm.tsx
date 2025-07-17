import React, { useState, useEffect, useRef } from 'react';

// Define an interface for the place data for better type safety
interface Place {
  name: {
    original_name: string;
  };
  latitude: number;
  longitude: number;
  recommended?: boolean; 
}

interface MyFormComponentProps {
  lat_sw?: number;
  lng_sw?: number;
  lat_ne?: number;
  lng_ne?: number;
  map: google.maps.Map | null;
}

const MyFormComponent: React.FC<MyFormComponentProps> = ({ lat_sw, lng_sw, lat_ne, lng_ne, map }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTiers, setSelectedTiers] = useState<string[]>([]);
  const markersRef = useRef<google.maps.Marker[]>([]);
  
  // Create a ref to hold the InfoWindow instance
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  const handleTierChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setSelectedTiers((prev) =>
      checked ? [...prev, value] : prev.filter((tier) => tier !== value)
    );
  };

  // Effect to clear markers and close InfoWindow when the component unmounts
  useEffect(() => {
    return () => {
      infoWindowRef.current?.close();
      markersRef.current.forEach(marker => marker.setMap(null));
      markersRef.current = [];
    };
  }, []);

  /**
   * Clears existing markers and renders new ones from JSON data.
   * @param {Place[]} places - An array of place objects from the API.
   */
  const processJsonForMap = async (places: Place[]) => {
    if (!map) return;
    
    // Close any open InfoWindow before clearing markers
    infoWindowRef.current?.close();
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];

    // Initialize the InfoWindow if it doesn't exist
    if (!infoWindowRef.current) {
        infoWindowRef.current = new google.maps.InfoWindow();
    }

    try {
      const newMarkers = places.map(place => {
        const name = place.name?.original_name || 'No Name';
        const lat = place.latitude;
        const lng = place.longitude;

        if (typeof lat !== 'number' || typeof lng !== 'number') {
          console.warn('Invalid coordinates for place:', place);
          return null;
        }

        const markerOptions: google.maps.MarkerOptions = {
          position: { lat, lng },
          map,
          title: name,
        };

        if (place.recommended === true) {
          markerOptions.icon = 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png';
        }

        const marker = new google.maps.Marker(markerOptions);

        // Add a click listener to each marker
        marker.addListener('click', () => {
          const infoWindow = infoWindowRef.current;
          if (infoWindow) {
            // Create HTML content for the InfoWindow
            const content = `
              <div style="color: #000;">
                <div style="text-align: center;">
                  <strong style="font-size: 1.1em; text-align: center;">${place.name.original_name}</strong>${place.recommended ? '<p style="font-weight: bold; color: #1E88E5;">Recommended</p>' : ''}
                </div>
                <br>
                <strong style="font-size: 1.1em; text-align: center;">Coordinates:</strong><p>${place.latitude.toFixed(5)}, ${place.longitude.toFixed(5)}</p>
                <br>
                <strong style="font-size: 1.1em;">Summary of the reviews:</strong><p>${place.reviews_summary}</p>
                <br>
                <strong style="font-size: 1.1em;">Summary of the photos:</strong><p>${place.photos_summary}</p>
                <br>
                <strong style="font-size: 1.1em; text-align: center;">Url to all photos:</strong></p>${place.url_to_all_photos}</p>
              </div>
            `;
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
          }
        });

        return marker;
      }).filter((marker): marker is google.maps.Marker => marker !== null);

      markersRef.current = newMarkers;

      if (newMarkers.length > 0) {
        const bounds = new google.maps.LatLngBounds();
        newMarkers.forEach(marker => bounds.extend(marker.getPosition()!));
        map.fitBounds(bounds);
      }
    } catch (err) {
      console.error("Error processing JSON for map:", err);
      setError("Failed to render location data on the map.");
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!lat_sw || !lng_sw || !lat_ne || !lng_ne) {
      setError("Please draw a bounding box on the map first.");
      return;
    }
    setLoading(true);
    setError(null);

    const form = e.currentTarget;
    const selectedFormats = Array.from(form.querySelectorAll('input[name="format"]:checked')).map(input => (input as HTMLInputElement).value);
    
    if (selectedFormats.length === 0) {
      setError("Please select at least one output format.");
      setLoading(false);
      return;
    }
    
    const formData = {
      text_query: form.query.value, prompt_info: form.llm_prompt.value, tiers: selectedTiers,
      format: selectedFormats, google_api_key: form.googleapi.value, llm_key: form.llm?.value || '',
      vlm_key: form.vlm?.value || '', lat_sw, lng_sw, lat_ne, lng_ne,
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/search_nearby', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error(`Search request failed: ${response.status} ${response.statusText}`);
      const searchResults: Place[] = await response.json();

      await processJsonForMap(searchResults);

      // --- Handle file downloads based on selected formats ---

      if (selectedFormats.includes('json')) {
        const jsonBlob = new Blob([JSON.stringify(searchResults, null, 2)], { type: 'application/json' });
        const jsonUrl = window.URL.createObjectURL(jsonBlob);
        const jsonLink = document.createElement('a');
        jsonLink.href = jsonUrl;
        jsonLink.download = `${formData.text_query.replace(/\s+/g, '_')}.json`;
        document.body.appendChild(jsonLink);
        jsonLink.click();
        document.body.removeChild(jsonLink);
        window.URL.revokeObjectURL(jsonUrl);
      }

      if (selectedFormats.includes('excel')) {
        const excelRequest = { places: searchResults };
        const excelResp = await fetch('http://127.0.0.1:8000/get_excel', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(excelRequest),
        });
        if (!excelResp.ok) throw new Error(`Excel generation failed: ${excelResp.status}`);
        const excelBlob = await excelResp.blob();
        const excelUrl = window.URL.createObjectURL(excelBlob);
        const excelAnchor = document.createElement('a');
        excelAnchor.href = excelUrl;
        excelAnchor.download = `${formData.text_query.replace(/\s+/g, '_')}.xlsx`;
        document.body.appendChild(excelAnchor);
        excelAnchor.click();
        document.body.removeChild(excelAnchor);
        window.URL.revokeObjectURL(excelUrl);
      }
      
      if (selectedFormats.includes('kmz')) {
        const bbox = [[formData.lng_sw, formData.lat_sw], [formData.lng_sw, formData.lat_ne], [formData.lng_ne, formData.lat_ne], [formData.lng_ne, formData.lat_sw], [formData.lng_sw, formData.lat_sw]];
        const kmzRequest = { data: searchResults, bbox, search_term: formData.text_query };
        const kmzResp = await fetch('http://127.0.0.1:8000/get_kmz', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(kmzRequest),
        });
        if (!kmzResp.ok) throw new Error(`KMZ generation failed: ${kmzResp.status}`);
        const kmzBlob = await kmzResp.blob();
        const url = window.URL.createObjectURL(kmzBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${formData.text_query.replace(/\s+/g, '_')}.kmz`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- JSX for the form ---
  const inputStyle = 'w-full mb-2 p-2 rounded bg-gray-700 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500';
  const checkbox = (name: string, value: string, label: string, onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void) => (
    <label className="inline-flex items-center mr-4 cursor-pointer" key={value}>
      <input type="checkbox" name={name} value={value} onChange={onChange} className="form-checkbox h-4 w-4 text-yellow-500 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500" />
      <span className="ml-2 text-sm text-gray-300">{label}</span>
    </label>
  );

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="space-y-4">
        <div>
          <label className="text-sm font-semibold text-gray-300 block">
            Query <span className="text-red-500">*</span>
          </label>
          <input type="text" name="query" placeholder="e.g., Restaurants" className={inputStyle} required />
        </div>

        <div>
          <label className="text-sm font-semibold text-gray-300 block">
            Prompt <span className="text-red-500">*</span>
          </label>
          <input type="text" name="llm_prompt" placeholder="e.g., look for outdoor seating" className={inputStyle} required />
        </div>

        <div>
          <label className="text-sm font-semibold text-gray-300 block">
            Google API Key <span className="text-red-500">*</span>
          </label>
          <input type="text" name="googleapi" placeholder="Your Google API Key" className={inputStyle} required />
        </div>

        {selectedTiers.includes('reviews') && (
          <div>
            <label className="text-sm font-semibold text-gray-300 block">
              LLM Key <span className="text-red-500">*</span>
            </label>
            <input type="text" name="llm" placeholder="LLM key" className={inputStyle} required />
          </div>
        )}

        {selectedTiers.includes('photos') && (
          <div>
            <label className="text-sm font-semibold text-gray-300 block">
              VLM Key <span className="text-red-500">*</span>
            </label>
            <input type="text" name="vlm" placeholder="VLM key" className={inputStyle} required />
          </div>
        )}

        <div>
          <p className="text-sm font-semibold text-gray-300 mb-2">Data Tiers</p>
          <div className="flex flex-wrap gap-2">
            {checkbox('tiers', 'reviews', 'Reviews', handleTierChange)}
            {checkbox('tiers', 'photos', 'Photos', handleTierChange)}
          </div>
        </div>

        <div>
          <p className="text-sm font-semibold text-gray-300 mb-2">Output Format <span className="text-red-500">*</span></p>
          <div className="flex flex-wrap gap-2">
            {checkbox('format', 'excel', 'Excel')}
            {checkbox('format', 'json', 'JSON')}
            {checkbox('format', 'kmz', 'KMZ')}
          </div>
        </div>
      </div>

      <button
        type="submit"
        className="w-full mt-6 py-2 px-4 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded disabled:bg-gray-500"
        disabled={loading}
      >
        {loading ? 'Processing...' : 'Submit Query'}
      </button>

      {error ? <p className="mt-4 text-red-500 text-center">{error}</p> : null}
    </form>
  );
};

export default MyFormComponent;