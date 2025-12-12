# app/utils/area.py
def mask_area_sqm(mask_image, meters_per_pixel: float = None):
    try:
        import numpy as np
    except Exception:
        raise RuntimeError("numpy required for area calculations (pip install numpy)")

    if meters_per_pixel is None:
        meters_per_pixel = 0.3  # fallback

    arr = mask_image.convert("L")
    data = np.array(arr)
    pv_pixels = (data > 128).sum()
    area_sqm = pv_pixels * (meters_per_pixel ** 2)
    return float(area_sqm)
