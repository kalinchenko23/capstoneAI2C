import React, { useState } from 'react';

interface MyFormComponentProps {
  lat_sw?: number;
  lng_sw?: number;
  lat_ne?: number;
  lng_ne?: number;
}

const MyFormComponent: React.FC<MyFormComponentProps> = ({
  lat_sw,
  lng_sw,
  lat_ne,
  lng_ne,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTiers, setSelectedTiers] = useState<string[]>([]);

  const handleTierChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setSelectedTiers((prev) =>
      checked ? [...prev, value] : prev.filter((tier) => tier !== value)
    );
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const form = e.currentTarget;

    const selectedFormats = Array.from(
      form.querySelectorAll('input[name="format"]:checked')
    ).map((input) => (input as HTMLInputElement).value);

    if (selectedFormats.length === 0) {
      setError("Please select at least one output format.");
      setLoading(false);
      return;
    }

    const formData = {
      text_query: form.query.value,
      prompt_info: form.llm_prompt.value,
      tiers: selectedTiers,
      format: selectedFormats,
      google_api_key: form.googleapi.value,
      llm_key: form.llm?.value || '',
      vlm_key: form.vlm?.value || '',
      lat_sw,
      lng_sw,
      lat_ne,
      lng_ne,
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/search_nearby', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error(`Request failed: ${response.status}`);
      const searchResults = await response.json();

      if (selectedFormats.includes('kmz')) {
        const bbox = [
          [formData.lng_sw, formData.lat_sw],
          [formData.lng_sw, formData.lat_ne],
          [formData.lng_ne, formData.lat_ne],
          [formData.lng_ne, formData.lat_sw],
          [formData.lng_sw, formData.lat_sw],
        ];

        const kmzRequest = {
          data: searchResults,
          bbox,
          search_term: formData.text_query,
        };

        const kmzResp = await fetch('http://127.0.0.1:8000/get_kmz', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(kmzRequest),
        });

        if (!kmzResp.ok) throw new Error(`KMZ generation failed: ${kmzResp.status}`);

        const kmzBlob = await kmzResp.blob();
        const kmzUrl = window.URL.createObjectURL(kmzBlob);
        const kmzAnchor = document.createElement('a');
        kmzAnchor.href = kmzUrl;
        kmzAnchor.download = `${formData.text_query.replace(/\s+/g, '_')}.kmz`;
        kmzAnchor.click();
        window.URL.revokeObjectURL(kmzUrl);
      }

      if (selectedFormats.includes('json')) {
        const filename = `response.json`;
        const blob = new Blob([JSON.stringify(searchResults, null, 2)], {
          type: 'application/json',
        });
        const url = window.URL.createObjectURL(blob);
        const jsonAnchor = document.createElement('a');
        jsonAnchor.href = url;
        jsonAnchor.download = filename;
        jsonAnchor.click();
        window.URL.revokeObjectURL(url);
      }
      
      if (selectedFormats.includes('excel')){
          const excelRequest = {places: searchResults};
          const excelResp = await fetch('http://127.0.0.1:8000/get_excel', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(excelRequest), // reuse the same payload or change if needed
        });

        if (!excelResp.ok) throw new Error(`Excel generation failed: ${excelResp.status}`);

        const excelBlob = await excelResp.blob();
        const excelUrl = window.URL.createObjectURL(excelBlob);
        const excelAnchor = document.createElement('a');
        excelAnchor.href = excelUrl;
        excelAnchor.download = `${formData.text_query.replace(/\s+/g, '_')}.xlsx`; // or .csv
        excelAnchor.click();
        window.URL.revokeObjectURL(excelUrl);
              }
    } catch (err: any) {
      console.error('Error submitting form:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle =
    'w-full mb-3 p-2 rounded bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500';

  const checkbox = (
    name: string,
    value: string,
    label: string,
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  ) => (
    <label className="inline-flex items-center mr-12 cursor-pointer" key={value}>
      <input
        type="checkbox"
        name={name}
        value={value}
        className="form-checkbox text-yellow-500"
        onChange={onChange}
      />
      <span className="ml-2 text-sm text-gray-300">{label}</span>
    </label>
  );

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full mx-auto bg-gray-900 text-gray-200 rounded-lg shadow-lg"
    >
      {/* Hidden bounding box fields */}
      <input type="hidden" name="lat_sw" value={lat_sw ?? ''} />
      <input type="hidden" name="lng_sw" value={lng_sw ?? ''} />
      <input type="hidden" name="lat_ne" value={lat_ne ?? ''} />
      <input type="hidden" name="lng_ne" value={lng_ne ?? ''} />

      <label className="text-sm font-semibold text-gray-300 mb-1 block">
        Query <span className="text-red-500">*</span>
      </label>
      <input type="text" name="query" placeholder="Search term *" className={inputStyle} required />

      <label className="text-sm font-semibold text-gray-300 mb-1 block">
        Prompt <span className="text-red-500">*</span>
      </label>
      <input type="text" name="llm_prompt" placeholder="LLM prompt *" className={inputStyle} required />

      <label className="text-sm font-semibold text-gray-300 mb-1 block">
        Google API Key <span className="text-red-500">*</span>
      </label>
      <input type="text" name="googleapi" placeholder="Google API Key *" className={inputStyle} required />

      {/* Conditionally rendered inputs */}
      {selectedTiers.includes('reviews') && (
        <>
          <label className="text-sm font-semibold text-gray-300 mb-1 block">
            LLM Key <span className="text-red-500">*</span>
          </label>
          <input type="text" name="llm" placeholder="LLM key" className={inputStyle}required/>
        </>
      )}

      {selectedTiers.includes('photos') && (
        <>
          <label className="text-sm font-semibold text-gray-300 mb-1 block">
            VLM Key <span className="text-red-500">*</span>
          </label>
          <input type="text" name="vlm" placeholder="VLM key" className={inputStyle} required/>
        </>
      )}

      {/* Tiers */}
      <div className="mb-4">
        <p className="text-sm font-semibold text-gray-300 mb-2">Data Tiers</p>
        <div className="text-sm text-gray-400 flex flex-wrap gap-4">
          {checkbox('tiers', 'reviews', 'Reviews', handleTierChange)}
          {checkbox('tiers', 'photos', 'Photos', handleTierChange)}
        </div>
      </div>

      {/* Output format */}
      <div className="mb-6">
        <p className="text-sm font-semibold text-gray-300 mb-2">
          Output Format <span className="text-red-500">*</span>
        </p>
        <div className="text-sm text-gray-400 flex flex-wrap gap-4">
          {checkbox('format', 'excel', 'Excel')}
          {checkbox('format', 'json', 'JSON')}
          {checkbox('format', 'kmz', 'KMZ')}
        </div>
      </div>

      <button
        type="submit"
        className="w-full py-2 px-4 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded"
        disabled={loading}
      >
        {loading ? (
          <div className="flex justify-center items-center">
            <svg
              className="animate-spin h-5 w-5 mr-3 text-black"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              ></path>
            </svg>
            Downloading...
          </div>
        ) : (
          'Submit'
        )}
      </button>

      {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
    </form>
  );
};

export default MyFormComponent;
