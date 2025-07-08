import React, { useState, useEffect, useRef } from 'react';
import JSZip from 'jszip';

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

  // --- ADD THIS FUNCTION ---
  const handleTierChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setSelectedTiers((prev) =>
      checked ? [...prev, value] : prev.filter((tier) => tier !== value)
    );
  };
  // -------------------------

  useEffect(() => {
    return () => {
      markersRef.current.forEach(marker => marker.setMap(null));
      markersRef.current = [];
    };
  }, []);

  const processKmzForMap = async (kmzBlob: Blob) => {
    if (!map) return;
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];
    
    try {
      const zip = await JSZip.loadAsync(kmzBlob);
      const kmlFile = Object.values(zip.files).find(file => file.name.endsWith('.kml'));
      if (!kmlFile) throw new Error('No .kml file found in the KMZ archive.');

      const kmlText = await kmlFile.async('text');
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(kmlText, 'text/xml');
      const placemarks = xmlDoc.getElementsByTagName('Placemark');
      
      const newMarkers = Array.from(placemarks).map(pm => {
        const name = pm.getElementsByTagName('name')[0]?.textContent || 'No Name';
        const coordinatesStr = pm.getElementsByTagName('coordinates')[0]?.textContent || '';
        const [lng, lat] = coordinatesStr.trim().split(',').map(Number);
        return new google.maps.Marker({ position: { lat, lng }, map, title: name });
      });

      markersRef.current = newMarkers;

      if (newMarkers.length > 0) {
        const bounds = new google.maps.LatLngBounds();
        newMarkers.forEach(marker => bounds.extend(marker.getPosition()!));
        map.fitBounds(bounds);
      }
    } catch (err) {
      console.error("Error processing KMZ file:", err);
      setError("Failed to render KMZ data on map.");
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
      if (!response.ok) throw new Error(`Search request failed: ${response.status}`);
      const searchResults = await response.json();

      if (selectedFormats.includes('kmz')) {
        const bbox = [[formData.lng_sw, formData.lat_sw], [formData.lng_sw, formData.lat_ne], [formData.lng_ne, formData.lat_ne], [formData.lng_ne, formData.lat_sw], [formData.lng_sw, formData.lat_sw]];
        const kmzRequest = { data: searchResults, bbox, search_term: formData.text_query };
        const kmzResp = await fetch('http://127.0.0.1:8000/get_kmz', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(kmzRequest),
        });
        if (!kmzResp.ok) throw new Error(`KMZ generation failed: ${kmzResp.status}`);
        const kmzBlob = await kmzResp.blob();
        await processKmzForMap(kmzBlob);
        const url = window.URL.createObjectURL(kmzBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${formData.text_query.replace(/\s+/g, '_')}.kmz`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
      // Add other format handlers (JSON, Excel) here if needed
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = 'w-full mb-2 p-2 rounded bg-gray-700 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500';
  const checkbox = (name: string, value: string, label: string, onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void) => (
    <label className="inline-flex items-center mr-4 cursor-pointer" key={value}>
      <input type="checkbox" name={name} value={value} onChange={onChange} className="form-checkbox h-4 w-4 text-yellow-500 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500" />
      <span className="ml-2 text-sm text-gray-300">{label}</span>
    </label>
  );

  return (
    <form onSubmit={handleSubmit} className="w-full flex flex-col flex-grow">
      <div className="flex-grow">
        <label className="text-sm font-semibold text-gray-300 block">Query <span className="text-red-500">*</span></label>
        <input type="text" name="query" placeholder="e.g., Restaurants" className={inputStyle} required />

        <label className="text-sm font-semibold text-gray-300 block">Prompt <span className="text-red-500">*</span></label>
        <input type="text" name="llm_prompt" placeholder="e.g., that serve vegan food" className={inputStyle} required />

        <label className="text-sm font-semibold text-gray-300 block">Google API Key <span className="text-red-500">*</span></label>
        <input type="text" name="googleapi" placeholder="Your Google API Key" className={inputStyle} required />

        {selectedTiers.includes('reviews') && (<><label className="text-sm font-semibold text-gray-300 block">LLM Key <span className="text-red-500">*</span></label><input type="text" name="llm" placeholder="LLM key" className={inputStyle} required/></>)}
        {selectedTiers.includes('photos') && (<><label className="text-sm font-semibold text-gray-300 block">VLM Key <span className="text-red-500">*</span></label><input type="text" name="vlm" placeholder="VLM key" className={inputStyle} required/></>)}

        <div className="mb-2"><p className="text-sm font-semibold text-gray-300 mb-2">Data Tiers</p><div className="flex flex-wrap gap-2">{checkbox('tiers', 'reviews', 'Reviews', handleTierChange)}{checkbox('tiers', 'photos', 'Photos', handleTierChange)}</div></div>
        <div className="mb-4"><p className="text-sm font-semibold text-gray-300 mb-2">Output Format <span className="text-red-500">*</span></p><div className="flex flex-wrap gap-2">{checkbox('format', 'excel', 'Excel')}{checkbox('format', 'json', 'JSON')}{checkbox('format', 'kmz', 'KMZ')}</div></div>
      </div>
      <button type="submit" className="w-full mt-auto py-2 px-4 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded disabled:bg-gray-500" disabled={loading}>{loading ? 'Processing...' : 'Submit Query'}</button>
      {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
    </form>
  );
};

export default MyFormComponent;