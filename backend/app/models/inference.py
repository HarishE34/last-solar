import requests
from PIL import Image
import io
import numpy as np

ROBOFLOW_API_KEY = "YOUR_KEY"
ROBOFLOW_MODEL = "solar-panel-detection/1"   # example: replace with your model
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL}?api_key={ROBOFLOW_API_KEY}"

def analyze_image(image: Image.Image, buffer_radius_sqft=1200):
    """
    Send image to Roboflow for real solar‑panel detection.
    """

    # Convert PIL → JPEG bytes
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    # Send to Roboflow
    resp = requests.post(
        ROBOFLOW_URL,
        files={"file": ("image.jpg", img_bytes, "image/jpeg")}
    )

    if resp.status_code != 200:
        return {
            "has_solar": False,
            "confidence": 0.0,
            "mask": None,
            "bbox": None
        }

    data = resp.json()

    # No detections
    if "predictions" not in data or len(data["predictions"]) == 0:
        return {
            "has_solar": False,
            "confidence": 0.0,
            "mask": None,
            "bbox": None
        }

    # Highest confidence detection
    pred = max(data["predictions"], key=lambda x: x["confidence"])

    x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]

    # Convert prediction → bbox
    bbox = (
        int(x - w/2),         # xmin
        int(y - h/2),         # ymin
        int(x + w/2),         # xmax
        int(y + h/2)          # ymax
    )

    # Create mask
    mask = Image.new("L", image.size, 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.rectangle(bbox, fill=255)

    return {
        "has_solar": True,
        "confidence": float(pred["confidence"]),
        "mask": mask,
        "bbox": bbox
    }
