import { useState } from "react";
import { Sun, MapPin, FileText, Image as ImageIcon } from "lucide-react";

export default function HomePage({ onSubmit }) {
  const [activeInput, setActiveInput] = useState(null);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [file, setFile] = useState(null);
  const [image, setImage] = useState(null);

  const handleTextSubmit = () => {
  if (latitude && longitude) {
    onSubmit({ latitude, longitude }, "text");
  }
};

  const handleFileSubmit = () => {
  if (file) {
    onSubmit({ file }, "file");
  }
};


  const handleImageSubmit = () => {
  if (image) {
    onSubmit({ image }, "image");
  }
};


  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Sun className="w-12 h-12 text-violet-600" />
          <h1 className="text-violet-900">Welcome to SunEye Intelligence</h1>
        </div>
        <p className="text-black/70">Choose your input: TEXT, FILE or IMAGE</p>
      </div>

      {/* Input Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
        {/* Text Input Card */}
        <div className="bg-white rounded-2xl shadow-lg border-2 border-violet-200 p-6 hover:shadow-xl transition-shadow">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-violet-100 rounded-lg">
              <MapPin className="w-6 h-6 text-violet-600" />
            </div>
            <h3 className="text-violet-900">Text Input</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block mb-2 text-black/70">Latitude</label>
              <input
                type="text"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="e.g., 34.0522"
                className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-violet-400 transition-colors"
              />
            </div>

            <div>
              <label className="block mb-2 text-black/70">Longitude</label>
              <input
                type="text"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="e.g., -118.2437"
                className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-violet-400 transition-colors"
              />
            </div>

            <button
              onClick={handleTextSubmit}
              disabled={!latitude || !longitude}
              className="w-full bg-violet-600 text-white py-3 rounded-lg hover:bg-violet-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Submit
            </button>
          </div>
        </div>

        {/* File Input Card */}
        <div className="bg-white rounded-2xl shadow-lg border-2 border-blue-200 p-6 hover:shadow-xl transition-shadow">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-blue-900">File Input</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block mb-2 text-black/70">Upload Excel File</label>
              <div className="relative">
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-violet-400 transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              {file && <p className="mt-2 text-green-600">Selected: {file.name}</p>}
            </div>

            <button
              onClick={handleFileSubmit}
              disabled={!file}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors mt-auto"
            >
              Submit
            </button>
          </div>
        </div>

        {/* Image Input Card */}
        <div className="bg-white rounded-2xl shadow-lg border-2 border-violet-200 p-6 hover:shadow-xl transition-shadow">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-violet-100 rounded-lg">
              <ImageIcon className="w-6 h-6 text-violet-600" />
            </div>
            <h3 className="text-violet-900">Image Input</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block mb-2 text-black/70">Upload Image</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setImage(e.target.files?.[0] || null)}
                className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-violet-400 transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
              />

              {image && (
                <div className="mt-4">
                  <img
                    src={URL.createObjectURL(image)}
                    alt="Preview"
                    className="w-full h-32 object-cover rounded-lg border-2 border-blue-200"
                  />
                  <p className="mt-2 text-green-600">Selected: {image.name}</p>
                </div>
              )}
            </div>

            <button
              onClick={handleImageSubmit}
              disabled={!image}
              className="w-full bg-violet-600 text-white py-3 rounded-lg hover:bg-violet-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}