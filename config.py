# <---------- game balance
DAMAGE = {
    "medium_tank": 1,
    "at_spg": 1,
    "heavy_tank": 1,
    "light_tank": 1,
    "spg": 1
}

MAX_RANGE = {
    "medium_tank": 2,
    "at_spg": 3,
    "heavy_tank": 2,
    "light_tank": 2,
    "spg": 3
}

MIN_RANGE = {
    "medium_tank": 1,
    "at_spg": 0,
    "heavy_tank": 0,
    "light_tank": 1,
    "spg": 2
}

SPEED_POINTS = {
    "medium_tank": 2,
    "at_spg": 1,
    "heavy_tank": 1,
    "light_tank": 3,
    "spg": 1
}
# <---------- end game balance

CENTER_POINT = (0, 0, 0)  # in case we will have other coordinate in central point

# <----------- connection
SERVER = 'wgforge-srv.wargaming.net'
PORT = 443
BUFFER_SIZE = 16384

STATUS_CODE = {
        0: "OKEY",
        1: "BAD_COMMAND",
        2: "ACCESS_DENIED",
        3: "INAPPROPRIATE_GAME_STATE",
        4: "TIMEOUT",
        500: "INTERNAL_SERVER_ERROR"
    }
ACTIONS = {
        "LOGIN": 1,
        "LOGOUT": 2,
        "MAP": 3,
        "GAME_STATE": 4,
        "GAME_ACTIONS": 5,
        "TURN": 6,
        "CHAT": 100,
        "MOVE": 101,
        "SHOOT": 102,
    }
# <----------- GUI colours
HEX_BORDER_COLOR = (0, 0, 0)
HEX_BORDER_WEIGHT = 2
HEX_DEFAULT_FILL = (200, 200, 200)
OBSTACLE_COLOR = (64, 64, 64)
BASE_COLOR = (255, 204, 153)
OUR_TANKS_COLOR = (178, 255, 102)
ENEMY_COLOR = (255, 102, 102)
SPAWN_COLOR = (160, 160, 160)