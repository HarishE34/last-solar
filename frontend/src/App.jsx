import { useState } from 'react';
import HomePage from './components/HomePage.jsx';
import OutputPage from './components/OutputPage.jsx';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [outputData, setOutputData] = useState(null);
  const [inputType, setInputType] = useState('');

  const handleSubmit = async (data, type) => {
  const formData = new FormData();
  formData.append("input_type", type);

  if (type === "text") {
    formData.append("latitude", data.latitude);
    formData.append("longitude", data.longitude);
  }

  if (type === "file") {
    formData.append("file", data.file);
  }

  if (type === "image") {
    formData.append("image", data.image);
  }

  try {
    const res = await fetch("http://localhost:8000/api/analyze", {
      method: "POST",
      body: formData
    });

    const result = await res.json();
    setOutputData(result);
    setInputType(type);
    setCurrentPage("output");

  } catch (err) {
    console.error("Error:", err);
    alert("Backend error — check console.");
  }
};


  const handleBack = () => {
    setCurrentPage('home');
    setOutputData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-blue-50">
      {currentPage === 'home' ? (
        <HomePage onSubmit={handleSubmit} />
      ) : (
        <OutputPage
          data={outputData}
          inputType={inputType}
          onBack={handleBack}
        />
      )}
    </div>
  );
}