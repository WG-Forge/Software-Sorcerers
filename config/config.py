"""
This module contains constants used in app
"""
from enum import IntEnum


SERVER = "wgforge-srv.wargaming.net"
PORT = 443
BUFFER_SIZE = 2048
RESPONSE_HEADER_SIZE = 8
RESULT_CODE_SIZE = 4
ACTION_ENCODE_SIZE = 4
LENGTH_ENCODE_SIZE = 4


class StatusCode(IntEnum):
    """
    IntEnum class store decimal values of status
    codes that can be received from server.
    Defined in client-server interact protocol.
    Could be extended if there will be any changes.
    """

    OKEY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500


class Actions(IntEnum):
    """
    Enum class Actions used to store decimal values
    of actions used in game logic and client-server interact.
    Values defined by client-server interact protocol,
    could be extended if there will be any changes in
    game rules or client-server interact protocol.
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


DEFAULT_LOGIN = {
    "name": "SorcererBot",
    "password": "42",
    "game": "test_122",
    "num_turns": 45,
    "num_players": 1,
    "is_observer": False,
    "is_full": False,
}
