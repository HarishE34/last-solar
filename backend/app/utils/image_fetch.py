# app/utils/image_fetch.py
import io
import requests
from PIL import Image
from . import config

def fetch_google_static_map(lat, lon, zoom=20, size=(1024, 1024), maptype="satellite"):
    """
    Fetch satellite tile via Google Static Maps API.
    Requires config.GOOGLE_STATIC_MAPS_KEY to be set.
    """
    key = config.GOOGLE_STATIC_MAPS_KEY
    if not key:
        raise RuntimeError("Google Static Maps API key not configured in config.GOOGLE_STATIC_MAPS_KEY")

    width, height = size
    url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={lat},{lon}&zoom={zoom}&size={width}x{height}&maptype={maptype}&key={key}"
    )
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Google Static Maps failed: {r.status_code} {r.text[:200]}")
    try:
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        return img
    except Exception as e:
        raise RuntimeError("Failed to parse image from Google Static Maps: " + str(e))
