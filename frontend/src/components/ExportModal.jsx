import { Download, X } from "lucide-react";

export default function ExportModal({ data, onClose }) {
  const handleDownload = () => {
    const dataStr = JSON.stringify(data, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    `link.download = solar-analysis-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-violet-900">Export Data</h3>
          <button
            onClick={onClose}
            className="text-black/50 hover:text-black transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <p className="text-black/70 mb-8">
          Download the analysis results as a JSON file to your device.
        </p>

        <div className="flex gap-4">
          <button
            onClick={handleDownload}
            className="flex-1 flex items-center justify-center gap-2 bg-violet-600 text-white px-6 py-3 rounded-lg hover:bg-violet-700 transition-colors"
          >
            <Download className="w-5 h-5" />
            Download
          </button>

          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 text-black px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}