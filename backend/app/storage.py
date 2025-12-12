# app/storage.py
import os
import json
from pathlib import Path
from .utils import config

OUTPUTS_DIR = Path(config.OUTPUTS_DIR)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def sample_output_path(sample_id):
    p = OUTPUTS_DIR / str(sample_id)
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def save_json(sample_id, payload):
    p = sample_output_path(sample_id)
    fp = os.path.join(p, f"{sample_id}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return fp


def save_image(sample_id, pil_image, name="overlay.png"):
    p = sample_output_path(sample_id)
    path = os.path.join(p, name)
    pil_image.save(path)
    return path


def save_mask(sample_id, mask_image, name="mask.png"):
    p = sample_output_path(sample_id)
    path = os.path.join(p, name)
    mask_image.save(path)
    return path
