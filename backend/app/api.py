# app/api.py
import io
import math
import os
import uuid
import typing
import requests
import pandas as pd

from fastapi import APIRouter, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse

from PIL import Image, ImageDraw, ImageOps
from .models.inference import analyze_image
from .utils import config, area, qc
from . import storage

router = APIRouter()


# ==============================
# OSM IMAGE FETCHER (STABLE)
# ==============================
def fetch_osm_image(lat: float, lon: float, zoom: int = 18, size=(1024, 1024)) -> Image.Image:
    """Fetch one OSM tile based on lat/lon"""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom

    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1 - (math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)) / 2 * n)

    url = f"https://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        if img.size != size:
            img = img.resize(size)
        return img
    except Exception as e:
        raise RuntimeError(f"Unable to fetch OSM image: {e}")


# ==================================================
# CLEAN RESPONSE FORMATTER
# ==================================================
def safe_response(status: int, content: dict):
    return JSONResponse(status_code=status, content=content)


# ==================================================
# MAIN ANALYZE ENDPOINT
# ==================================================
@router.post("/analyze")
async def analyze(
    input_type: str = Form(...),
    latitude: typing.Optional[str] = Form(None),
    longitude: typing.Optional[str] = Form(None),
    file: UploadFile = File(None),
    image: UploadFile = File(None),
    meters_per_pixel: float = Form(0.1)  # default
):
    try:
        results = []

        # ==============================================================
        # CASE 1: TEXT INPUT (lat/lon only)
        # ==============================================================
        if input_type == "text":
            if not latitude or not longitude:
                return safe_response(400, {"error": "latitude & longitude required"})

            lat = float(latitude)
            lon = float(longitude)
            sample_id = f"auto-{uuid.uuid4().hex[:8]}"

            # Fetch satellite tile
            img = fetch_osm_image(lat, lon)

            # Run inference
            inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)

            # Second pass if no solar detected
            if not inf.get("has_solar", False):
                inf2 = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_LARGE_SQFT)
                if inf2.get("confidence", 0) > inf.get("confidence", 0):
                    inf = inf2

            mask = inf.get("mask")

            pv_area = area.mask_area_sqm(mask, meters_per_pixel) if mask else 0
            qc_status = qc.qc_status(img, inf)

            # ENERGY CALC
            eff = config.PANEL_EFFICIENCY
            pr = config.PERFORMANCE_RATIO
            hours = config.DEFAULT_PEAK_SUN_HOURS

            daily_kwh = pv_area * 1000 * eff * pr * hours / 1000
            yearly_kwh = daily_kwh * 365

            # SAVE OVERLAY
            if mask is not None:
                overlay = img.copy()
                m = mask.convert("L").resize(img.size)
                colored = ImageOps.colorize(m.point(lambda p: 255 if p > 128 else 0), "black", "yellow")
                overlay = Image.blend(overlay, colored, alpha=0.35)
                storage.save_image(sample_id, overlay, "overlay.png")
                storage.save_mask(sample_id, mask, "mask.png")
            else:
                storage.save_image(sample_id, img, "overlay.png")

            output = {
                "sample_id": sample_id,
                "lat": lat,
                "lon": lon,
                "has_solar": bool(inf.get("has_solar")),
                "confidence": float(inf.get("confidence")),
                "pv_area_sqm_est": round(pv_area, 3),
                "qc_status": qc_status,
                "estimated_kwh_per_day": round(daily_kwh, 3),
                "estimated_kwh_per_year": round(yearly_kwh, 2),
                "image_source": "OSM"
            }

            storage.save_json(sample_id, output)
            return safe_response(200, {"samples": [output]})

        # ==============================================================
        # CASE 2: DIRECT IMAGE UPLOAD
        # ==============================================================
        if input_type == "image":
            if image is None:
                return safe_response(400, {"error": "image file required"})

            img = Image.open(io.BytesIO(await image.read())).convert("RGB")
            sample_id = f"auto-{uuid.uuid4().hex[:8]}"

            inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)

            if not inf.get("has_solar"):
                inf2 = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_LARGE_SQFT)
                if inf2.get("confidence", 0) > inf.get("confidence", 0):
                    inf = inf2

            mask = inf.get("mask")
            pv_area = area.mask_area_sqm(mask, meters_per_pixel) if mask else 0
            qc_status = qc.qc_status(img, inf)

            eff = config.PANEL_EFFICIENCY
            pr = config.PERFORMANCE_RATIO
            hours = config.DEFAULT_PEAK_SUN_HOURS

            daily_kwh = pv_area * eff * pr * hours
            yearly_kwh = daily_kwh * 365

            # SAVE
            if mask is not None:
                storage.save_mask(sample_id, mask, "mask.png")

            storage.save_image(sample_id, img, "overlay.png")

            output = {
                "sample_id": sample_id,
                "lat": None,
                "lon": None,
                "has_solar": bool(inf.get("has_solar")),
                "confidence": float(inf.get("confidence")),
                "pv_area_sqm_est": pv_area,
                "qc_status": qc_status,
                "estimated_kwh_per_day": round(daily_kwh, 3),
                "estimated_kwh_per_year": round(yearly_kwh, 2),
                "image_source": "UPLOAD"
            }

            storage.save_json(sample_id, output)
            return safe_response(200, {"samples": [output]})

        # ==============================================================
        # CASE 3: FILE UPLOAD (CSV/XLSX)
        # ==============================================================
        if input_type == "file":
            if file is None:
                return safe_response(400, {"error": "file required"})

            raw = await file.read()

            try:
                if file.filename.lower().endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(raw))
                else:
                    df = pd.read_excel(io.BytesIO(raw))
            except Exception:
                return safe_response(400, {"error": "Invalid CSV/XLSX format"})

            if df.empty:
                return safe_response(400, {"error": "file empty"})

            # Detect columns
            cols = {c.lower().strip(): c for c in df.columns}
            lat_col = next((cols[c] for c in cols if "lat" in c), None)
            lon_col = next((cols[c] for c in cols if "lon" in c), None)
            id_col = next((cols[c] for c in cols if "id" in c), None)

            if not lat_col or not lon_col:
                return safe_response(400, {"error": "File must contain latitude & longitude columns"})

            results = []

            for idx, row in df.head(100).iterrows():
                sample_id = str(row[id_col]) if id_col else f"auto-{uuid.uuid4().hex[:8]}"

                try:
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                except:
                    results.append({"sample_id": sample_id, "error": "Invalid lat/lon"})
                    continue

                try:
                    img = fetch_osm_image(lat, lon)
                except Exception as e:
                    results.append({"sample_id": sample_id, "error": str(e)})
                    continue

                inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)

                if not inf.get("has_solar"):
                    inf2 = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_LARGE_SQFT)
                    if inf2.get("confidence", 0) > inf.get("confidence", 0):
                        inf = inf2

                mask = inf.get("mask")
                pv_area = area.mask_area_sqm(mask, meters_per_pixel) if mask else 0
                qc_status = qc.qc_status(img, inf)

                eff = config.PANEL_EFFICIENCY
                pr = config.PERFORMANCE_RATIO
                hours = config.DEFAULT_PEAK_SUN_HOURS

                daily_kwh = pv_area * eff * pr * hours
                yearly_kwh = daily_kwh * 365

                output = {
                    "sample_id": sample_id,
                    "lat": lat,
                    "lon": lon,
                    "has_solar": bool(inf.get("has_solar")),
                    "confidence": float(inf.get("confidence")),
                    "pv_area_sqm_est": pv_area,
                    "qc_status": qc_status,
                    "estimated_kwh_per_day": round(daily_kwh, 3),
                    "estimated_kwh_per_year": round(yearly_kwh, 2),
                }

                results.append(output)

            return safe_response(200, {"samples": results})

        return safe_response(400, {"error": "Invalid input_type"})

    except Exception as e:
        return safe_response(500, {"error": str(e)})
