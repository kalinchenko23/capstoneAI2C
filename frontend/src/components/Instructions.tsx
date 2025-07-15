
import Map from "./Map"

export const Instructions = () => {
  return (
    <>
      {/* Full-screen hero */}
      <section className="w-full min-h-screen bg-background flex flex-col justify-center items-center px-6 py-20 space-y-12">
        {/* Title & Logo */}
        <div className="text-center space-y-6" >
          <div className="flex items-center justify-center space-x-4">
            <img src="/src/assets/AI2c_logo.png" alt="Logo" className="h-35 w-35" />
            <h1 className="text-5xl md:text-6xl text-gray-300 font-bold text">
              <span className="text-yellow-500 bg-clip-text">
                PLAID
              </span>{" "}
              analytics asistant.
            </h1>
          </div>

    <div className="max-w-2xl mx-auto p-6 bg-gray-300 rounded-2xl shadow-md text-gray-800">
      <h2 className="text-2xl font-bold mb-4 text-black">
        📍 App Instructions: Search & Export Places
      </h2>

      <ol className="list-decimal list-inside space-y-3">
        <li>
          <strong>Draw Area on the Map:</strong> Use the map interface to draw a shape (rectangle) to define your area of interest. You can adjust or redraw the area as needed.
        </li>

        <li>
          <strong>Enter Search Parameter:</strong> In the search box, type what you're looking for (e.g., "restaurants", "hospitals", "schools") and press <strong>Search</strong>.
        </li>
        <li>
          <strong>Enter VLM Prompt</strong> to let model know what it should focus on while parsing the images.
        </li>
        <li>
          <strong>View Results:</strong> The app will show matching places within your drawn area on the map and in a list below.
        </li>

        <li>
          <strong>Download Results:</strong> Click the <strong>Download</strong> button and select a format:
          <ul className="list-disc list-inside ml-5 mt-2 space-y-1">
            <li>📄 <strong>Excel (.xlsx)</strong></li>
            <li>🌍 <strong>KMZ (Google Earth)</strong></li>
            <li>🧾 <strong>JSON (Raw Data)</strong></li>
          </ul>
          Select which file type would you like to download.
        </li>
      </ol>
    </div>
        
        </div>
      </section>
    </>
  );
};
