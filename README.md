<h1>🧠 Model Card — SunEye Intelligence (Solar Panel Detection & Energy Estimation)</h1>

<h2>📌 Overview</h2>
<p>
    <strong>SunEye Intelligence</strong> is a geospatial AI system that analyzes satellite imagery to detect 
    solar panels, segment PV areas, and estimate solar energy production. 
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
<p>
    Designed for <strong>hackathons</strong>, <strong>research projects</strong>, and 
    <strong>smart‑city sustainability analytics</strong>.
</p>

<h2>🧰 Model Architecture</h2>
<ol>
    <li>
        <strong>Roof Detection / Feature Extraction</strong><br>
        Lightweight CNN + heuristic masking for roof region identification.
    </li>
    <li>
        <strong>Solar Panel Segmentation</strong><br>
        Segment‑anything / custom mask generator with refinement filters.
    </li>
    <li>
        <strong>Post‑Processing</strong><br>
        Morphological filtering + PV area computation.
    </li>
    <li>
        <strong>Energy Estimation</strong><br>
        <code>energy = area_m2 × panel_efficiency × performance_ratio × sun_hours</code>
    </li>
</ol>

<h2>📡 Data Sources</h2>
<ul>
    <li>OpenStreetMap (OSM) raster tiles</li>
    <li>Uploaded geospatial images (RGB)</li>
    <li>User‑provided CSV/XLSX coordinate files</li>
</ul>
<p>No private or personally identifiable data is stored.</p>

<h2>⚙️ Inputs</h2>
<h3>1️⃣ Text Mode</h3>
<pre>{
  "input_type": "text",
  "latitude": "12.983",
  "longitude": "77.605"
}</pre>

<h3>2️⃣ Image Mode</h3>
<p>Upload an aerial/satellite-style image.</p>

<h3>3️⃣ File Mode</h3>
<p>Bulk processing using CSV/XLSX with lat/lon columns.</p>

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

<p>Additional artifacts stored:</p>
<ul>
    <li><code>overlay.png</code> → PV highlight map</li>
    <li><code>mask.png</code> → segmentation mask</li>
    <li><code>result.json</code> → metadata</li>
</ul>

<h2>📊 Performance</h2>
<p>Optimized for:</p>
<ul>
    <li>Urban & suburban rooftops</li>
    <li>Clear, high‑contrast satellite images</li>
</ul>
<p>Performance may degrade with:</p>
<ul>
    <li>Poor‑quality or low‑resolution tiles</li>
    <li>Dense vegetation</li>
    <li>Shadow‑covered rooftops</li>
</ul>

<h2>🧪 Evaluation</h2>
<ul>
    <li>IoU for segmentation</li>
    <li>Model confidence score</li>
    <li>Manual QC flags</li>
</ul>

<h2>🔒 Limitations</h2>
<ul>
    <li>Not suitable for ground‑mounted solar farms.</li>
    <li>Accuracy depends on regional OSM tile resolution.</li>
    <li>May misinterpret skylights, dark roofs, or shadows.</li>
</ul>

<h2>⚠️ Ethical Considerations</h2>
<ul>
    <li>Uses only publicly available satellite imagery.</li>
    <li>No tracking of individuals or private behavior.</li>
    <li>Detection performed at the building level.</li>
</ul>

<h2>📄 License</h2>
<p>This project is for <strong>educational</strong> and <strong>hackathon</strong> use. Please use responsibly.</p>

<h2>🤝 Contributors</h2>
<ul>
    <li>HARISH</li>
    <li>mr_jagii</li>
    <li>Dhinesh</li>
</ul>
