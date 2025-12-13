# app/utils/config.py
import os

# Output directory
OUTPUTS_DIR = os.environ.get(
    "SUNEYE_OUTPUTS",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))
)

# FIXED BUFFER RADII — real working values
BUFFER_RADIUS_SMALL_SQFT = 5000     # for first pass
BUFFER_RADIUS_LARGE_SQFT = 15000    # fallback pass

# Electricity defaults
PANEL_EFFICIENCY = 0.19             # slight improvement
PERFORMANCE_RATIO = 0.78            # more realistic worldwide
DEFAULT_PEAK_SUN_HOURS = 4.5        # global average
