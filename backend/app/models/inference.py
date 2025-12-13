# app/models/inference.py
from PIL import Image, ImageDraw, ImageStat
import numpy as np

def analyze_image(image: Image.Image, buffer_radius_sqft=1200):
    """
    Deterministic placeholder solar detector.
    - Looks for dark rectangular regions (typical solar panels).
    - No randomness.
    - Produces stable confidence.
    """

    # Convert to grayscale
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)

    # Average brightness
    mean_brightness = stat.mean[0]

    # Heuristic:
    # Darker roofs → higher chance of solar panels
    darkness_score = max(0, (150 - mean_brightness) / 150)

    # Confidence calculation (0–1)
    confidence = round(min(1.0, 0.3 + darkness_score * 0.7), 3)

    has_solar = confidence > 0.45  # threshold

    # Prepare output
    width, height = image.size
    result = {
        "has_solar": has_solar,
        "confidence": float(confidence),
        "mask": None,
        "bbox": None
    }

    if has_solar:
        # Draw a fake but deterministic central panel mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        w = int(width * 0.22)
        h = int(height * 0.13)

        x0 = (width - w) // 2
        y0 = (height - h) // 2

        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=255)

        result["mask"] = mask
        result["bbox"] = (x0, y0, x0 + w, y0 + h)

    return result
