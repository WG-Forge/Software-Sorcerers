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
BUFFER_SIZE = 8192
# <----------- end connection

