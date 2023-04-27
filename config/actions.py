"""
This module contains actions that used in game logic
and client-server interact
"""
from enum import IntEnum


class Actions(IntEnum):
    """
    Enum class Actions used to store decimal values
    of actions used in game logic and client-server interact
    """
    LOGIN = 1
    LOGOUT = 2
    MAP = 3
    GAME_STATE = 4
    GAME_ACTIONS = 5
    TURN = 6
    CHAT = 100
    MOVE = 101
    SHOOT = 102