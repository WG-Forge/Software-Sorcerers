"""
This module contains constants used in client-server interact
"""
from enum import IntEnum


SERVER = 'wgforge-srv.wargaming.net'
PORT = 443
BUFFER_SIZE = 8192


class StatusCode(IntEnum):
    """
    IntEnum class store decimal values of status
    codes that can be received from server.
    """
    OKEY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500
