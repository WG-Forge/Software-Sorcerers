from enum import IntEnum


SERVER = 'wgforge-srv.wargaming.net'
PORT = 443
BUFFER_SIZE = 8192


class StatusCode(IntEnum):
    OKEY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500
