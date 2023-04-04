from typing import Optional, OrderedDict


import cube_math as cm
import config as cf


class GameMap:
    def __init__(self, data: dict):
        self.size = data["size"]
        self.name = data["name"]
        self.cells = cm.in_radius(cf.CENTER_POINT, self.size - 1)
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
        spawn_points_set = set()
        for player_vehicles in spawn_points:
            for list_of_spawn_points in player_vehicles.values():
                for point in list_of_spawn_points:
                    spawn_points_set.add((point["x"], point["y"], point["z"]))
        return spawn_points_set

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
        self.agressive_cells = self.parse_agressive_cells(data, idx) # dictioanry cell:hp(update if you shoot enemy vehicle)


    @staticmethod
    def parse_our_tanks(vehicles: dict, idx: int) -> OrderedDict[int, "TankModel"]:
        our_tanks = {int(key): TankModel((value["health"],
                                          value["vehicle_type"],
                                          (value["position"]["x"], value["position"]["y"], value["position"]["z"])
                                          ))
                     for key, value in vehicles.items() if value["player_id"] == idx}

        return dict(sorted(our_tanks.items(), key=lambda x: x[1].coordinates[0]))


    @staticmethod
    def parse_tank_cells(vehicles: dict) -> set[tuple[int, int, int]]:
        return {(record["position"]["x"], record["position"]["y"], record["position"]["z"]) for record in vehicles.values()}

    @staticmethod
    def parse_agressive_cells(data:dict, idx: int) -> Optional[dict[tuple[int, int, int], int]]:
        pass

    def update_data(self, data: tuple[str, dict]):
        if data is not None:
            action = data[0]
            vehicle_id = data[1]["vehicle_id"]
            position = (data[1]["target"]["x"], data[1]["target"]["y"], data[1]["target"]["z"])
            if action == "SHOOT":
                self.__agressive_cells[position] -= cf.DAMAGE[our_tanks[vehicle_id].vehicle_type]
                if self.__agressive_cells[position] <= 0:
                    self.__agressive_cells.pop(position)
            else:
                self.tank_cells.discard(self.our_tanks[vehicle_id].coordinates)
                self.tank_cells.add(position)
                self.our_tanks[vehicle_id].coordinates = position


    @property
    def agressive_cells(self) -> set[tuple[int, int, int]]:
        return {cell for cell in self.__agressive_cells}

    def get_our_tanks_cells(self) -> set[tuple[int, int, int]]:
        pass



class GameActions:
    def __init__(self, data: dict):
        pass


class TankModel:
    def __init__(self, data: tuple[int, str, tuple[int, int, int]]):
        self.hp = data[0]
        self.vehicle_type = data[1]
        self.coordinates = data[2]
# <----------------------- attributes for next stages -------------------
        self.shoot_range_bonus = 0

if __name__ == "__main__":
    vehicle_dict = {
        "player_id": 1,
        "vehicle_type": "medium_tank",
        "health": 2,
        "spawn_position": {
            "x": 4,
            "y": -3,
            "z": 10
        },
        "position": {
            "x": 3,
            "y": -3,
            "z": 10
        },
        "capture_points": 0,
        "shoot_range_bonus": 0
    }
    vehicle_dict_1 = {
        "player_id": 1,
        "vehicle_type": "medium_tank",
        "health": 2,
        "spawn_position": {
            "x": -7,
            "y": -3,
            "z": 10
        },
        "position": {
            "x": 4,
            "y": 5,
            "z": 5,
        },
        "capture_points": 0,
        "shoot_range_bonus": 0
    }
    vehicle_dict_2 = {
        "player_id": 5,
        "vehicle_type": "medium_tank",
        "health": 17,
        "spawn_position": {
            "x": -7,
            "y": -3,
            "z": 10
        },
        "position": {
            "x": 3,
            "y": 5,
            "z": 5,
        },
        "capture_points": 0,
        "shoot_range_bonus": 0
    }

    # Create a dictionary for the "vehicles" key that contains the vehicle dictionary
    vehicles_dict = {
        "1": vehicle_dict,
        "2": vehicle_dict_1,
        "3": vehicle_dict_2

    }


    print("Test parse_tank_cells: ")
    print(GameState.parse_tank_cells(vehicles_dict))

    print("Test parse_our_tanks:")
    our_tanks = GameState.parse_our_tanks(vehicles_dict, 1);
    for tank in our_tanks.values():
        print(tank.hp, " ", tank.vehicle_type, " ", tank.coordinates)

    print(GameMap.parse_spawn_points([{'at_spg': [{'x': -3, 'y': -7, 'z': 10}],
                                       'heavy_tank': [{'x': -5, 'y': -5, 'z': 10}],
                                       'light_tank': [{'x': -6, 'y': -4, 'z': 10}],
                                       'medium_tank': [{'x': -4, 'y': -6, 'z': 10}],
                                       'spg': [{'x': -7, 'y': -3, 'z': 10}]},
                                      {'at_spg': [{'x': -7, 'y': 10, 'z': -3}],
                                       'heavy_tank': [{'x': -5, 'y': 10, 'z': -5}],
                                       'light_tank': [{'x': -4, 'y': 10, 'z': -6}],
                                       'medium_tank': [{'x': -6, 'y': 10, 'z': -4}],
                                       'spg': [{'x': -3, 'y': 10, 'z': -7}]},
                                      {'at_spg': [{'x': 10, 'y': -3, 'z': -7}],
                                       'heavy_tank': [{'x': 10, 'y': -5, 'z': -5}],
                                       'light_tank': [{'x': 10, 'y': -6, 'z': -4}],
                                       'medium_tank': [{'x': 10, 'y': -4, 'z': -6}],
                                       'spg': [{'x': 10, 'y': -7, 'z': -3}]}]))
