from typing import Optional, OrderedDict


import cube_math as cm


CENTER_POINT = (0, 0, 0)


class GameMap:
    def __init__(self, data: dict):
        self.size = data["size"]
        self.name = data["name"]
        self.cells = cm.in_radius(CENTER_POINT, self.size - 1)
        self.obstacles = self.parse_obstacles(data["content"])
        self.spawn_points = self.parse_spawn_points(data["spawn_points"])
        self.available_cells = self.cells.difference(self.obstacles.union(self.spawn_points))
        self.base = {(base_cell["x"], base_cell["y"], base_cell["z"]) for base_cell in data["content"]["base"]}

# <----------------------- attributes for next stages -------------------
        self.light_repairs = self.parse_light_repairs(data["content"])
        self.hard_repairs = self.parse_hard_repairs(data["content"])
        self.catapults = self.parse_catapults(data["content"])
# <------------------- end of attributes for next stages ----------------

    @staticmethod
    def parse_obstacles(content: dict) -> set[Optional[tuple[int, int, int]]]:
        if not ("obstacle" in content):
            return set()  # Here is not used None to avoid TypeError in self.available_cells
        return {(obs["x"], obs["y"], obs["z"])for obs in content["obstacle"]}

    @staticmethod
    def parse_spawn_points(spawn_points: list) -> set[tuple[int, int, int]]:
        pass  # TODO implement, mb we need to exclude our spawn points from here, to avoid situation when our tank stack between our spawn points

# <----------------------- methods for next stages ---------------------
    @staticmethod
    def parse_catapults(content: dict) -> Optional[set[tuple[int, int, int]]]:
        if not ("catapult" in content):
            return None
        ...

    @staticmethod
    def parse_light_repairs(content: dict) -> Optional[set[tuple[int, int, int]]]:
        if not ("light_repair" in content):
            return None
        ...

    @staticmethod
    def parse_hard_repairs(content: dict) -> Optional[set[tuple[int, int, int]]]:
        if not ("light_repair" in content):
            return None
        ...
# <------------------ end of methods for next stages ---------------------

class GameState:
    def __init__(self, data: dict, idx: int):
        self.is_finished = data["finished"]
        self.current_player_id = data["current_player_idx"]
        self.winner = data["winner"]
        self.our_tanks = self.parse_our_tanks(data["vehicles"], idx) # ordered (left to right) dict{id:TankModel} (update if we move)
        self.tank_cells = self.parse_tank_cells(data["vehicles"]) # set of all tank cells for moving logic  (update if you move)
        self.__agressive_cells = self.parse_agressive_cells(data, idx) # dictioanry cell:hp (update if you shoot enemy vehicle)


    @staticmethod
    def parse_our_tanks(vehicles: dict, idx: int) -> OrderedDict[int: "TankModel"]:
        pass

    @staticmethod
    def parse_tank_cells(vehicles: dict) -> set[tuple[int, int, int]]:
        pass

    @staticmethod
    def parse_agressive_cells(data:dict, idx: int) -> Optional[dict[tuple[int,int,int] : int]]:
        pass

    def update_data(self, data: tuple[str, dict]):
        pass

    @property
    def agressive_cells(self) -> set[int]:
        return {cell for cell in self.__agressive_cells}



class GameActions:
    def __init__(self, data: dict):
        pass

class TankModel:
    def __init__(self, data: ):
        self.hp = #int
        self.vehicle_type = #string
        self.coordinates = #tuple of ints

# <----------------------- attributes for next stages -------------------
        self.shoot_range_bonus = None