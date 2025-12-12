# app/api.py
import io
import math
import os
import datetime
import uuid
import typing
from fastapi import APIRouter, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageOps
import requests
import pandas as pd

from .models.inference import analyze_image
from .utils import config, area, qc
from . import storage

router = APIRouter()


# -------------------------
# helper: fetch OSM tile (no API key)
# -------------------------
def fetch_osm_image(lat: float, lon: float, zoom: int = 18, size=(1024, 1024)) -> Image.Image:
    """
    Fetch a single OSM raster tile that covers the lat/lon (tile-based).
    This is good for dev & small batches; for production prefer a proper imagery provider.
    """
    try:
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - (math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi)) / 2.0 * n)

        tile_url = f"https://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"
        r = requests.get(tile_url, timeout=10)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        if size and img.size != size:
            img = img.resize(size)
        return img
    except Exception as e:
        raise RuntimeError(f"OSM tile fetch failed: {e}")


# -------------------------
# helper: find flexible column
# -------------------------
def find_column(df: pd.DataFrame, candidates: typing.List[str]) -> typing.Optional[str]:
    lc = [c.lower().strip() for c in df.columns]
    for cand in candidates:
        for i, col in enumerate(lc):
            if cand in col:
                return df.columns[i]
    return None


# -------------------------
# endpoint: analyze
# Accepts form-data with:
#   input_type: 'text'|'image'|'file'
#   latitude, longitude (for text)
#   file (csv/xlsx) for file
#   image for image
# -------------------------
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

        # ---------- TEXT input (single sample) ----------
        if input_type == "text":
            if not latitude or not longitude:
                return JSONResponse(status_code=400, content={"error": "latitude & longitude required for text input"})
            lat = float(latitude)
            lon = float(longitude)
            sample_id = f"auto-{uuid.uuid4().hex[:8]}"

            # fetch image and analyze
            img = fetch_osm_image(lat, lon)
            inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)
            used_radius = config.BUFFER_RADIUS_SMALL_SQFT
            if not inf.get("has_solar", False):
                used_radius = config.BUFFER_RADIUS_LARGE_SQFT
                inf2 = analyze_image(img, buffer_radius_sqft=used_radius)
                if inf2.get("confidence", 0.0) > inf.get("confidence", 0.0):
                    inf = inf2

            pv_area = 0.0
            if inf.get("mask") is not None:
                pv_area = area.mask_area_sqm(inf["mask"], meters_per_pixel=meters_per_pixel)

            qc_value = qc.qc_status(img, inf)

            # estimate electricity
            panel_eff = config.PANEL_EFFICIENCY
            perf_ratio = config.PERFORMANCE_RATIO
            hours = config.DEFAULT_PEAK_SUN_HOURS
            daily_kwh = pv_area * 1000 * panel_eff * perf_ratio * hours / 1000.0
            yearly_kwh = daily_kwh * 365

            # save outputs
            output = {
                "sample_id": sample_id,
                "lat": lat,
                "lon": lon,
                "has_solar": bool(inf.get("has_solar", False)),
                "confidence": float(inf.get("confidence", 0.0)),
                "pv_area_sqm_est": float(round(pv_area, 4)),
                "buffer_radius_sqft": used_radius,
                "qc_status": qc_value,
                "bbox_or_mask": "",
                "image_metadata": {"source": "OSM_PUBLIC"}
            }

            # save mask and overlay if exists
            if inf.get("mask") is not None:
                storage.save_mask(sample_id, inf["mask"], name="mask.png")
                # overlay
                overlay = img.copy()
                draw = ImageDraw.Draw(overlay)
                if inf.get("bbox"):
                    x0, y0, x1, y1 = inf["bbox"]
                    draw.rectangle([x0, y0, x1, y1], outline="yellow", width=6)
                try:
                    mask_rgb = inf["mask"].convert("L").resize(img.size).point(lambda p: 255 if p > 128 else 0)
                    mask_colored = ImageOps.colorize(mask_rgb, black="black", white="yellow")
                    overlay = Image.blend(overlay, mask_colored, alpha=0.35)
                except Exception:
                    pass
                storage.save_image(sample_id, overlay, name="overlay.png")
            else:
                storage.save_image(sample_id, img, name="overlay.png")

            storage.save_json(sample_id, output)

            # add energy estimates to output as requested
            output["estimated_kwh_per_day"] = round(daily_kwh, 3)
            output["estimated_kwh_per_year"] = round(yearly_kwh, 2)

            results.append(output)
            return JSONResponse(status_code=200, content={"samples": results})

        # ---------- IMAGE input (single sample, auto id) ----------
        elif input_type == "image":
            if image is None:
                return JSONResponse(status_code=400, content={"error": "image upload required for image input"})
            raw = await image.read()
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            sample_id = f"auto-{uuid.uuid4().hex[:8]}"
            lat = None
            lon = None
            # run inference on upload
            inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)
            used_radius = config.BUFFER_RADIUS_SMALL_SQFT
            if not inf.get("has_solar", False):
                used_radius = config.BUFFER_RADIUS_LARGE_SQFT
                inf2 = analyze_image(img, buffer_radius_sqft=used_radius)
                if inf2.get("confidence", 0.0) > inf.get("confidence", 0.0):
                    inf = inf2

            pv_area = 0.0
            if inf.get("mask") is not None:
                pv_area = area.mask_area_sqm(inf["mask"], meters_per_pixel=meters_per_pixel)

            qc_value = qc.qc_status(img, inf)

            panel_eff = config.PANEL_EFFICIENCY
            perf_ratio = config.PERFORMANCE_RATIO
            hours = config.DEFAULT_PEAK_SUN_HOURS
            daily_kwh = pv_area * 1000 * panel_eff * perf_ratio * hours / 1000.0
            yearly_kwh = daily_kwh * 365

            output = {
                "sample_id": sample_id,
                "lat": lat,
                "lon": lon,
                "has_solar": bool(inf.get("has_solar", False)),
                "confidence": float(inf.get("confidence", 0.0)),
                "pv_area_sqm_est": float(round(pv_area, 4)),
                "buffer_radius_sqft": used_radius,
                "qc_status": qc_value,
                "bbox_or_mask": "",
                "image_metadata": {"source": f"UPLOAD:{image.filename}"}
            }

            if inf.get("mask") is not None:
                storage.save_mask(sample_id, inf["mask"], name="mask.png")
            storage.save_image(sample_id, img, name="overlay.png")
            storage.save_json(sample_id, output)

            output["estimated_kwh_per_day"] = round(daily_kwh, 3)
            output["estimated_kwh_per_year"] = round(yearly_kwh, 2)

            results.append(output)
            return JSONResponse(status_code=200, content={"samples": results})

        # ---------- FILE input (csv or xlsx) ----------
        elif input_type == "file":
            if file is None:
                return JSONResponse(status_code=400, content={"error": "file upload required for file input"})

            raw = await file.read()
            filename = getattr(file, "filename", "") or ""
            # choose parser based on extension or try both
            df = None
            try:
                if filename.lower().endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(raw))
                else:
                    # try xlsx
                    df = pd.read_excel(io.BytesIO(raw), engine="openpyxl")
            except Exception as e:
                # as fallback try csv decode
                try:
                    df = pd.read_csv(io.StringIO(raw.decode("utf-8")))
                except Exception:
                    return JSONResponse(status_code=400, content={"error": "Failed to parse file. Ensure CSV or XLSX."})

            if df is None or df.empty:
                return JSONResponse(status_code=400, content={"error": "Uploaded file is empty or couldn't be parsed."})

            # detect columns flexibly
            cols_lower = {c.lower().strip(): c for c in df.columns}
            sample_col = None
            for cand in ["sample_id", "sampleid", "id", "sid", "sample"]:
                if cand in cols_lower:
                    sample_col = cols_lower[cand]; break
            if sample_col is None:
                # fallback: any column with 'id' or sample
                for k, v in cols_lower.items():
                    if "sample" in k or k.endswith("id"):
                        sample_col = v; break

            lat_col = None
            for k, v in cols_lower.items():
                if "lat" in k:
                    lat_col = v; break
            lon_col = None
            for k, v in cols_lower.items():
                if "lon" in k or "long" in k:
                    lon_col = v; break

            if not lat_col or not lon_col:
                return JSONResponse(status_code=400, content={"error": "Excel/CSV must contain latitude and longitude columns."})

            # iterate rows (up to 100)
            count = 0
            for idx, row in df.iterrows():
                if count >= 100:
                    break
                count += 1

                # sample id from file (string). If missing generate one.
                sample_raw = None
                if sample_col is not None:
                    sample_raw = row[sample_col]
                    if pd.isna(sample_raw):
                        sample_id = f"auto-{uuid.uuid4().hex[:8]}"
                    else:
                        sample_id = str(sample_raw)
                else:
                    sample_id = f"auto-{uuid.uuid4().hex[:8]}"

                try:
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                except Exception as e:
                    # skip row if lat/lon invalid
                    results.append({
                        "sample_id": sample_id,
                        "lat": None,
                        "lon": None,
                        "has_solar": False,
                        "estimated_kwh_per_day": 0,
                        "estimated_kwh_per_year": 0,
                        "error": f"Invalid lat/lon: {e}"
                    })
                    continue

                # fetch image and analyze
                try:
                    img = fetch_osm_image(lat, lon)
                except Exception as e:
                    # can't fetch image, still record row
                    results.append({
                        "sample_id": sample_id,
                        "lat": lat,
                        "lon": lon,
                        "has_solar": False,
                        "estimated_kwh_per_day": 0,
                        "estimated_kwh_per_year": 0,
                        "error": f"Image fetch failed: {e}"
                    })
                    continue

                inf = analyze_image(img, buffer_radius_sqft=config.BUFFER_RADIUS_SMALL_SQFT)
                used_radius = config.BUFFER_RADIUS_SMALL_SQFT
                if not inf.get("has_solar", False):
                    used_radius = config.BUFFER_RADIUS_LARGE_SQFT
                    inf2 = analyze_image(img, buffer_radius_sqft=used_radius)
                    if inf2.get("confidence", 0.0) > inf.get("confidence", 0.0):
                        inf = inf2

                pv_area = 0.0
                if inf.get("mask") is not None:
                    pv_area = area.mask_area_sqm(inf["mask"], meters_per_pixel=meters_per_pixel)

                qc_value = qc.qc_status(img, inf)

                panel_eff = config.PANEL_EFFICIENCY
                perf_ratio = config.PERFORMANCE_RATIO
                hours = config.DEFAULT_PEAK_SUN_HOURS
                daily_kwh = pv_area * 1000 * panel_eff * perf_ratio * hours / 1000.0
                yearly_kwh = daily_kwh * 365

                output = {
                    "sample_id": sample_id,
                    "lat": lat,
                    "lon": lon,
                    "has_solar": bool(inf.get("has_solar", False)),
                    "confidence": float(inf.get("confidence", 0.0)),
                    "pv_area_sqm_est": float(round(pv_area, 4)),
                    "buffer_radius_sqft": used_radius,
                    "qc_status": qc_value,
                    "bbox_or_mask": "",
                    "image_metadata": {"source": "OSM_PUBLIC"}
                }

                # save mask + overlay
                if inf.get("mask") is not None:
                    storage.save_mask(sample_id, inf["mask"], name="mask.png")
                    overlay = img.copy()
                    draw = ImageDraw.Draw(overlay)
                    if inf.get("bbox"):
                        x0, y0, x1, y1 = inf["bbox"]
                        draw.rectangle([x0, y0, x1, y1], outline="yellow", width=6)
                    try:
                        mask_rgb = inf["mask"].convert("L").resize(img.size).point(lambda p: 255 if p > 128 else 0)
                        mask_colored = ImageOps.colorize(mask_rgb, black="black", white="yellow")
                        overlay = Image.blend(overlay, mask_colored, alpha=0.35)
                    except Exception:
                        pass
                    storage.save_image(sample_id, overlay, name="overlay.png")
                    output["bbox_or_mask"] = storage.save_mask(sample_id, inf["mask"], name="mask.png")
                else:
                    storage.save_image(sample_id, img, name="overlay.png")

                storage.save_json(sample_id, output)

                output["estimated_kwh_per_day"] = round(daily_kwh, 3)
                output["estimated_kwh_per_year"] = round(yearly_kwh, 2)

                results.append(output)

            return JSONResponse(status_code=200, content={"samples": results})

        else:
            return JSONResponse(status_code=400, content={"error": "invalid input_type"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# -------------------------
# /api/calculate-electricity
# expects JSON body: { "sample_id": "..." }
# -------------------------
@router.post("/calculate-electricity")
async def calculate_electricity(payload: dict = Body(...)):
    try:
        sample_id = payload.get("sample_id")
        if not sample_id:
            return JSONResponse(status_code=400, content={"error": "sample_id required in body"})

        path = storage.sample_output_path(sample_id)
        json_file = os.path.join(path, f"{sample_id}.json")
        if not os.path.exists(json_file):
            return JSONResponse(status_code=404, content={"error": "sample_id not found"})

        import json
        with open(json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)

        area_m2 = float(payload.get("pv_area_sqm_est", 0.0))
        if area_m2 <= 0:
            return JSONResponse(status_code=400, content={"error": "pv_area_sqm_est is zero or missing"})

        panel_eff = config.PANEL_EFFICIENCY
        perf_ratio = config.PERFORMANCE_RATIO
        hours = config.DEFAULT_PEAK_SUN_HOURS

        daily_kwh = area_m2 * 1000 * panel_eff * perf_ratio * hours / 1000.0
        yearly_kwh = daily_kwh * 365

        resp = {
            "sample_id": sample_id,
            "estimated_kwh_per_day": round(daily_kwh, 3),
            "estimated_kwh_per_year": round(yearly_kwh, 2)
        }
        return JSONResponse(status_code=200, content=resp)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
