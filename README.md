<!DOCTYPE html>
<html lang="en">

<body>

<h1>🌞 SunEye Intelligence</h1>
<div class="center">AI‑Powered Solar Panel Detection & Energy Estimation</div>


<!-- DESCRIPTION -->
<h2>📘 Description</h2>
<p class="highlight">
SunEye Intelligence is an AI‑driven geospatial tool designed to detect rooftop solar panels,
segment photovoltaic regions, and estimate potential solar energy output using satellite imagery.  
It supports image uploads, coordinates-based analysis, and bulk CSV/XLSX processing—
making it ideal for sustainability projects, government energy audits, and hackathon innovation.
</p>


<!-- COMMANDS -->
<h2>⚙️ Project Execution Commands</h2>

<h3>📌 Backend Setup</h3>
<div class="cmd-box">
cd backend<br>
python -m venv venv<br>
venv\Scripts\activate<br>
pip install uvicorn<br>
pip install fastapi<br>
pip install requests<br>
pip install pandas<br>
pip install Pillow<br>
pip install python-multipart<br>
uvicorn app.main:app --reload<br>
</div>

<h3>📌 Frontend Setup</h3>
<div class="cmd-box">
cd frontend<br>
npm install<br>
npm run dev<br>
</div>


<!-- PROBLEM STATEMENT -->
<h2>🚩 Problem Statement</h2>
<p class="highlight">
India is rapidly expanding solar adoption, but identifying suitable rooftops and estimating solar potential  
across large areas is time‑consuming and lacks accurate ground‑level data.  
Manual surveys are expensive, slow, and not scalable for smart‑city development.
</p>

<h2>💡 Our Solution</h2>
<p class="highlight">
SunEye Intelligence automates solar panel detection using satellite imagery and AI-based segmentation.  
It analyzes rooftops, estimates panel area, and predicts energy output—providing an end‑to‑end digital solution  
that helps governments, energy companies, and startups scale solar adoption effortlessly.
</p>


<!-- WORKFLOW -->
<h2>🔄 Project Workflow </h2>
<ul>
    <li>User enters coordinates / uploads an image / uploads a CSV file.</li>
    <li>System fetches OpenStreetMap satellite tiles or reads user-provided images.</li>
    <li>AI model detects roofs, identifies solar panels, and generates segmentation masks.</li>
    <li>Post‑processing refines boundaries and calculates PV area using pixel‑meter ratio.</li>
    <li>Energy estimation generates daily & yearly production metrics.</li>
    <li>Output includes overlay images, masks, and complete metadata.</li>
</ul>


<!-- MODEL CARD -->
<h2>🧠 Model Card</h2>

<h2>📌 Overview</h2>
<p>
    <strong>SunEye Intelligence</strong> is a geospatial AI system that analyzes satellite imagery 
    to detect solar panels, segment PV areas, and estimate solar energy production. 
    The model processes OpenStreetMap tiles, uploaded images, and bulk coordinate files.
</p>

<h2>🎯 Model Purpose</h2>
<p>The model aims to:</p>
<ul>
    <li>Identify the presence of solar panels on rooftops.</li>
    <li>Segment photovoltaic (PV) panel areas.</li>
    <li>Estimate solar panel area in square meters.</li>
    <li>Predict daily & yearly energy production.</li>
    <li>Enable large‑scale solar mapping for sustainability projects.</li>
</ul>
<p>Designed for <strong>hackathons, research projects, and smart‑city sustainability analytics</strong>.</p>

<h2>🧰 Model Architecture</h2>
<ol>
    <li><strong>Roof Detection / Feature Extraction</strong> — Lightweight CNN + heuristic masking.</li>
    <li><strong>Solar Panel Segmentation</strong> — SAM/custom mask refinement.</li>
    <li><strong>Post‑Processing</strong> — Morphological filtering + area calculation.</li>
    <li><strong>Energy Estimation</strong> — <code>area × efficiency × performance × sun_hours</code></li>
</ol>

<h2>📡 Data Sources</h2>
<ul>
    <li>OpenStreetMap Raster Tiles</li>
    <li>User‑uploaded satellite images</li>
    <li>CSV/XLSX coordinate files</li>
</ul>
<p>No personal or identifiable data is collected.</p>

<h2>⚙️ Inputs</h2>

<h3>1️⃣ Text Mode</h3>
<pre>{
  "input_type": "text",
  "latitude": "12.983",
  "longitude": "77.605"
}</pre>

<h3>2️⃣ Image Mode</h3>
<p>Upload any satellite‑style rooftop image.</p>

<h3>3️⃣ File Mode</h3>
<p>Bulk CSV/XLSX with Latitude & Longitude columns.</p>

<h2>🟢 Outputs</h2>
<pre>{
  "sample_id": "auto-23ab91fe",
  "lat": 12.983,
  "lon": 77.605,
  "has_solar": true,
  "confidence": 0.92,
  "pv_area_sqm_est": 34.5,
  "qc_status": "GOOD",
  "estimated_kwh_per_day": 25.1,
  "estimated_kwh_per_year": 9150.3
}</pre>

<ul>
    <li><code>overlay.png</code> → Highlighted solar detection</li>
    <li><code>mask.png</code> → Segmentation mask</li>
    <li><code>result.json</code> → All metadata</li>
</ul>

<h2>📊 Performance</h2>
<p>Optimized for:</p>
<ul>
    <li>Urban & suburban rooftops</li>
    <li>Clear, high‑contrast imagery</li>
</ul>
<p>Performance may drop with:</p>
<ul>
    <li>Low‑resolution images</li>
    <li>Vegetation cover</li>
    <li>Heavy shadows</li>
</ul>

<h2>🧪 Evaluation</h2>
<ul>
    <li>Segmentation IoU</li>
    <li>Model confidence</li>
    <li>QC flags</li>
</ul>

<h2>🔒 Limitations</h2>
<ul>
    <li>Not optimized for ground‑mounted solar farms</li>
    <li>Dependent on satellite resolution</li>
    <li>Possible misclassification of dark roofing materials</li>
</ul>

<h2>⚠️ Ethical Considerations</h2>
<ul>
    <li>Uses only publicly available imagery</li>
    <li>No people, vehicles, or private activity detected</li>
    <li>Focuses solely on rooftops</li>
</ul>

<h2>📄 License</h2>
<p>For educational & hackathon purposes.</p>

<h2>🤝 Contributors</h2>
<ul>
    <li><strong>HARISH E</strong></li>
    <li><strong>DHINESH B</strong></li>
    <li><strong>JAGADISH KG</strong></li>
</ul>

</body>
</html>
