# SunEye Intelligence - Backend

## Setup
1. Create a Python venv and activate:
   python -m venv venv
   source venv/bin/activate    # unix
   venv\Scripts\activate       # windows

2. Install:
   pip install -r requirements.txt

3. Set environment variables (optional):
   export GOOGLE_STATIC_MAPS_KEY="your_key"
   export ESRI_KEY="your_esri_key"

4. Run dev server:
   python -m app.main

5. API:
   POST /api/analyze
     - form fields:
       input_type: text | file | image
       latitude, longitude (for text)
       file (UploadFile) for file option
       image (UploadFile) for image option
       meters_per_pixel (optional numeric)
