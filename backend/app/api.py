# app/api.py
import io
import math
import os
import uuid
import typing
import datetime

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageOps

from .models.inference import analyze_image
from .utils import config, area, qc
from . import storage

router = APIRouter()

# -----------------------------------------------------
# Fetch OSM tile
# -----------------------------------------------------
def fetch_osm_image(lat: float, lon: float, zoom: int = 20, size=(1024, 1024)) -> Image.Image:
    try:
        lat_r = math.radians(lat)
        n = 2 ** zoom
        xtile = int((lon + 180) / 360 * n)
        ytile = int((1 - (math.log(math.tan(lat_r) + (1 / math.cos(lat_r))) / math.pi)) / 2 * n)

        url = f"https://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"
        r = requests.get(url, timeout=12)
        r.raise_for_status()

        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        if size and img.size != size:
            img = img.resize(size)
        return img

    except Exception as e:
        raise RuntimeError(f"Failed fetching OSM image: {e}")

# -----------------------------------------------------
# Safe solar inference wrapper
# -----------------------------------------------------
def run_solar_inference(img: Image.Image, meters_per_pixel: float):
    inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)

    if not inf.get("has_solar", False):
        inf2 = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_LARGE_SQFT)
        if inf2.get("confidence", 0) > inf.get("confidence", 0):
            inf = inf2

    pv_area = 0.0
    if inf.get("mask") is not None:
        pv_area = area.mask_area_sqm(inf["mask"], meters_per_pixel)

    return inf, pv_area

# -----------------------------------------------------
# Build overlay
# -----------------------------------------------------
def build_overlay(img: Image.Image, inf):
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)

    if inf.get("bbox"):
        x0, y0, x1, y1 = inf["bbox"]
        draw.rectangle([x0, y0, x1, y1], outline="yellow", width=5)

    try:
        if inf.get("mask") is not None:
            mask = inf["mask"].convert("L").resize(img.size)
            mask = mask.point(lambda p: 255 if p > 120 else 0)
            colored = ImageOps.colorize(mask, black="black", white="yellow")
            overlay = Image.blend(overlay, colored, alpha=0.35)
    except:
        pass

    return overlay

# -----------------------------------------------------
# Energy estimation
# -----------------------------------------------------
def estimate_energy(area_m2: float):
    eff = config.PANEL_EFFICIENCY
    perf = config.PERFORMANCE_RATIO
    sun = config.DEFAULT_PEAK_SUN_HOURS

    daily = area_m2 * eff * perf * sun
    yearly = daily * 365
    return round(daily, 3), round(yearly, 2)

# -----------------------------------------------------
# MAIN /analyze ENDPOINT
# -----------------------------------------------------
@router.post("/analyze")
async def analyze(
    input_type: str = Form(...),
    latitude: typing.Optional[str] = Form(None),
    longitude: typing.Optional[str] = Form(None),
    file: UploadFile = File(None),
    image: UploadFile = File(None),
    meters_per_pixel: typing.Optional[float] = Form(None),
):
    try:
        results = []

        # ------------------ TEXT MODE ------------------
        if input_type == "text":
            if not latitude or not longitude:
                return JSONResponse(
                    {"error": "latitude and longitude required"},
                    status_code=400
                )

            lat, lon = float(latitude), float(longitude)
            sample_id = f"auto-{uuid.uuid4().hex[:8]}"

            img = fetch_osm_image(lat, lon)
            inf, pv_area = run_solar_inference(img, meters_per_pixel)
            qc_value = qc.qc_status(img, inf)
            overlay = build_overlay(img, inf)

            storage.save_image(sample_id, overlay, "overlay.png")
            if inf.get("mask"):
                storage.save_mask(sample_id, inf["mask"], "mask.png")

            daily, yearly = estimate_energy(pv_area)

            out = {
                "sample_id": sample_id,
                "lat": lat,
                "lon": lon,
                "has_solar": bool(inf.get("has_solar")),
                "confidence": float(inf.get("confidence", 0)),
                "pv_area_sqm_est": float(round(pv_area, 4)),
                "qc_status": qc_value,
                "estimated_kwh_per_day": daily,
                "estimated_kwh_per_year": yearly,
            }

            storage.save_json(sample_id, out)
            return JSONResponse({"samples": [out]}, status_code=200)

        # ------------------ IMAGE MODE ------------------
        if input_type == "image":
            if not image:
                return JSONResponse(
                    {"error": "Image file required"},
                    status_code=400
                )

            raw = await image.read()
            img = Image.open(io.BytesIO(raw)).convert("RGB")

            sample_id = f"auto-{uuid.uuid4().hex[:8]}"
            inf, pv_area = run_solar_inference(img, meters_per_pixel)
            qc_value = qc.qc_status(img, inf)
            overlay = build_overlay(img, inf)

            storage.save_image(sample_id, overlay, "overlay.png")
            if inf.get("mask"):
                storage.save_mask(sample_id, inf["mask"], "mask.png")

            daily, yearly = estimate_energy(pv_area)

            out = {
                "sample_id": sample_id,
                "lat": None,
                "lon": None,
                "has_solar": bool(inf.get("has_solar")),
                "confidence": float(inf.get("confidence", 0)),
                "pv_area_sqm_est": float(round(pv_area, 4)),
                "qc_status": qc_value,
                "estimated_kwh_per_day": daily,
                "estimated_kwh_per_year": yearly,
            }

            storage.save_json(sample_id, out)
            return JSONResponse({"samples": [out]}, status_code=200)

        # ------------------ FILE MODE ------------------
        if input_type == "file":
            if not file:
                return JSONResponse(
                    {"error": "file upload required"},
                    status_code=400
                )

            raw = await file.read()
            filename = file.filename.lower()

            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(raw))
                elif filename.endswith(".xlsx"):
                    df = pd.read_excel(io.BytesIO(raw))
                else:
                    return JSONResponse(
                        {"error": "Invalid file type. Use CSV or XLSX."},
                        status_code=400
                    )
            except ImportError:
                return JSONResponse(
                    {"error": "openpyxl is required for XLSX reading. Install with pip install openpyxl"},
                    status_code=400
                )
            except Exception:
                return JSONResponse(
                    {"error": "Invalid file. Must be CSV or XLSX"},
                    status_code=400
                )

            if df.empty:
                return JSONResponse({"error": "File is empty"}, status_code=400)

            lat_col = next((c for c in df.columns if "lat" in c.lower()), None)
            lon_col = next((c for c in df.columns if "lon" in c.lower()), None)
            id_col = next((c for c in df.columns if "id" in c.lower()), None)

            if not (lat_col and lon_col):
                return JSONResponse({"error": "Latitude & Longitude columns missing"}, status_code=400)

            for _, row in df.iterrows():
                try:
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                except:
                    continue

                sample_id = str(row[id_col]) if id_col else f"auto-{uuid.uuid4().hex[:8]}"
                img = fetch_osm_image(lat, lon)

                inf, pv_area = run_solar_inference(img, meters_per_pixel)
                qc_value = qc.qc_status(img, inf)
                overlay = build_overlay(img, inf)

                storage.save_image(sample_id, overlay, "overlay.png")
                if inf.get("mask"):
                    storage.save_mask(sample_id, inf["mask"], "mask.png")

                daily, yearly = estimate_energy(pv_area)

                out = {
                    "sample_id": sample_id,
                    "lat": lat,
                    "lon": lon,
                    "has_solar": bool(inf.get("has_solar")),
                    "confidence": float(inf.get("confidence", 0)),
                    "pv_area_sqm_est": float(round(pv_area, 4)),
                    "qc_status": qc_value,
                    "estimated_kwh_per_day": daily,
                    "estimated_kwh_per_year": yearly,
                }

                storage.save_json(sample_id, out)
                results.append(out)

            return JSONResponse({"samples": results}, status_code=200)

        return JSONResponse({"error": "Invalid input_type"}, status_code=400)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
