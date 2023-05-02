"""
This module contains vehicle characteristics defined by rules
"""

DAMAGE = {"medium_tank": 1, "at_spg": 1, "heavy_tank": 1, "light_tank": 1, "spg": 1}

MAX_RANGE = {"medium_tank": 2, "at_spg": 3, "heavy_tank": 2, "light_tank": 2, "spg": 3}

MIN_RANGE = {"medium_tank": 1, "at_spg": 0, "heavy_tank": 0, "light_tank": 1, "spg": 2}

SPEED_POINTS = {
    "medium_tank": 2,
    "at_spg": 1,
    "heavy_tank": 1,
    "light_tank": 3,
    "spg": 1,
}
