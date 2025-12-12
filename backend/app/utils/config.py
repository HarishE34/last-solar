# app/utils/config.py
import os

# Output directory
OUTPUTS_DIR = os.environ.get("SUNEYE_OUTPUTS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs")))

# Buffer radii (sqft)
BUFFER_RADIUS_SMALL_SQFT = 1200
BUFFER_RADIUS_LARGE_SQFT = 2400

# Electricity defaults
PANEL_EFFICIENCY = 0.18
PERFORMANCE_RATIO = 0.75
DEFAULT_PEAK_SUN_HOURS = 4.0
