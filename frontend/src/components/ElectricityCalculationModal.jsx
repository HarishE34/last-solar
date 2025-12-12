import { useState } from "react";
import { Calculator, X, Zap } from "lucide-react";

export default function ElectricityCalculationModal({ onClose }) {
  const [sampleId, setSampleId] = useState("");
  const [result, setResult] = useState(null);

 const handleCalculate = async () => {
  if (!sampleId) return;

  try {
    const res = await fetch("http://localhost:8000/api/calculate-electricity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample_id: Number(sampleId) })
    });

    const result = await res.json();

    if (res.status === 404 || result.error) {
      setResult("❌ Sample ID not found. Enter a correct ID.");
      return;
    }

    setResult(
      `Sample ID: ${sampleId}\n` +
      `Estimated Daily Energy: ${result.estimated_kwh_per_day} kWh\n` +
      `Estimated Yearly Energy: ${result.estimated_kwh_per_year} kWh`
    );
  } catch (err) {
    console.error(err);
    setResult("Backend error. Check server.");
  }
};


  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-violet-100 rounded-lg">
              <Zap className="w-6 h-6 text-violet-600" />
            </div>
            <h3 className="text-violet-900">Electricity Calculation</h3>
          </div>
          <button
            onClick={onClose}
            className="text-black/50 hover:text-black transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block mb-2 text-black/70">Sample ID</label>
            <input
              type="text"
              value={sampleId}
              onChange={(e) => setSampleId(e.target.value)}
              placeholder="Enter Sample ID"
              className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-violet-400 transition-colors"
            />
          </div>

          {result && (
            <div className="bg-violet-50 border-2 border-violet-200 rounded-lg p-4">
              <h4 className="text-violet-900 mb-2">Calculation Result</h4>
              <pre className="text-black/80 whitespace-pre-wrap">{result}</pre>
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={handleCalculate}
              disabled={!sampleId}
              className="flex-1 flex items-center justify-center gap-2 bg-violet-600 text-white px-6 py-3 rounded-lg hover:bg-violet-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <Calculator className="w-5 h-5" />
              Calculate
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
    </div>
  );
}