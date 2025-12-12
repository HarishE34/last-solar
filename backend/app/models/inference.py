# app/models/inference.py
from PIL import Image, ImageDraw
import random

def analyze_image(image: Image.Image, buffer_radius_sqft=1200):
    width, height = image.size
    has_solar = random.random() < 0.5
    confidence = round(random.uniform(0.4, 0.98), 3)
    result = {
        "has_solar": has_solar,
        "confidence": confidence,
        "mask": None,
        "bbox": None
    }
    if has_solar:
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        w = int(width * 0.2)
        h = int(height * 0.12)
        x0 = (width - w) // 2
        y0 = (height - h) // 2
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=255)
        result["mask"] = mask
        result["bbox"] = (x0, y0, x0 + w, y0 + h)
    return result
