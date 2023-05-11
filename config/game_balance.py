"""
This module contains game balance characteristics defined by rules
"""

DAMAGE = {"medium_tank": 1, "at_spg": 1, "heavy_tank": 1, "light_tank": 1, "spg": 1}

MAX_RANGE = {"medium_tank": 2, "at_spg": 3, "heavy_tank": 2, "light_tank": 2, "spg": 3}

MIN_RANGE = {"medium_tank": 1, "at_spg": 0, "heavy_tank": 0, "light_tank": 1, "spg": 2}

MAX_HP = {"medium_tank": 2, "at_spg": 2, "heavy_tank": 3, "light_tank": 1, "spg": 1}

SPEED_POINTS = {
    "medium_tank": 2,
    "at_spg": 1,
    "heavy_tank": 1,
    "light_tank": 3,
    "spg": 1,
}

TURN_ORDER = {         # If at_spg turn order will be changed
    "medium_tank": 4,  # should be modified update game_state
    "at_spg": 5,       # method due to at_spg shooting mechanics
    "heavy_tank": 3,
    "light_tank": 2,
    "spg": 1,
}
MAX_CATAPULT_USAGE = 3
MAX_CAPTURE_POINTS = 6
