import { useState } from 'react';
import { ArrowLeft, Download, Calculator } from 'lucide-react';
import ExportModal from './ExportModal';
import ElectricityCalculationModal from './ElectricityCalculationModal';

export default function OutputPage({ data, inputType, onBack }) {
  const [showExportModal, setShowExportModal] = useState(false);
  const [showCalculationModal, setShowCalculationModal] = useState(false);

  return (
    <div className="min-h-screen p-8">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-violet-600 hover:text-violet-800 mb-8 transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </button>

      {/* Output Container */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg border-2 border-violet-200 p-8">
          <h2 className="text-violet-900 mb-6">Analysis Results</h2>

          {/* JSON Output */}
          <div className="bg-black/5 rounded-lg p-6 mb-6 max-h-96 overflow-auto">
            <pre className="text-black/80 whitespace-pre-wrap break-words">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setShowExportModal(true)}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-5 h-5" />
              Export
            </button>

            <button
              onClick={() => setShowCalculationModal(true)}
              className="flex items-center gap-2 bg-violet-600 text-white px-6 py-3 rounded-lg hover:bg-violet-700 transition-colors"
            >
              <Calculator className="w-5 h-5" />
              Electricity Calculation
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showExportModal && (
        <ExportModal
          data={data}
          onClose={() => setShowExportModal(false)}
        />
      )}

      {showCalculationModal && (
        <ElectricityCalculationModal
          onClose={() => setShowCalculationModal(false)}
        />
      )}
    </div>
  );
}