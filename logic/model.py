"""
This module contains classes to parse and store game data
"""
import collections as coll
import dataclasses
from typing import Optional, OrderedDict

from config import game_balance as gb_cf
from config.config import Actions
from logic.cell import Cell

CENTER_POINT = (0, 0, 0)


class GameMap:
    """
    Data class to parse and store static game objects from GAME_MAP response
    """

    def __init__(self, data: dict):
        self.size = data["size"]
        self.name = data["name"]
        self.cells = Cell(*CENTER_POINT).in_radius(self.size - 1)
        self.obstacles = self.parse_content(data["content"], "obstacle")
        self.spawn_points = self.parse_spawn_points(data["spawn_points"])
        self.base = self.parse_content(data["content"], "base")
        self.light_repairs = self.parse_content(data["content"], "light_repair")
        self.hard_repairs = self.parse_content(data["content"], "hard_repair")
        self.catapults = self.parse_content(data["content"], "catapult")

    @staticmethod
    def parse_content(content: dict, content_type: str) -> set[Optional[Cell]]:
        """
        Handles parsing obstacles from content part of GAME_MAP response
        :param content: dict with content part of GAME_MAP response
        :param content_type: name of content type defined by game rules in
        client-server interact protocol
        :return: set of obstacle Cell
        """
        if content_type in content:
            return {Cell(i["x"], i["y"], i["z"]) for i in content[content_type]}
        return set()  # Here is not used None to avoid TypeError in self.available_cells

    @staticmethod
    def parse_spawn_points(spawn_points: list) -> set[Cell]:
        """
        Handles parsing spawn points from spawn points part of GAME_MAP response
        :param spawn_points: dict with spawn points part of GAME_MAP response
        :return: set of spawn points Cell
        """
        spawn_points_set = set()
        for player_vehicles in spawn_points:
            for list_of_spawn_points in player_vehicles.values():
                for point in list_of_spawn_points:
                    spawn_points_set.add(Cell(point["x"], point["y"], point["z"]))
        return spawn_points_set

    def get_content_cells(self) -> set[Cell]:
        """
        :return: set of cells with static content
        """

        return set.union(
            self.base,
            self.catapults,
            self.light_repairs,
            self.hard_repairs,
            self.obstacles,
            self.spawn_points,
        )

    def get_available_cells(self) -> set[Cell]:
        """
        :return: set of cells allowed to vehicle move
        """
        return self.cells.difference(self.obstacles.union(self.spawn_points))


class GameState:
    """
    Data class to parse and store dynamic game data from GAME_STATE response
    In part of game logic handle only neutrality rule. Also updates during
    players turn to avoid move collisions, and shooting
    units destroyed by previous tank
    """

    def __init__(self, data: dict, idx: int):
        self.idx = idx
        self.current_turn = data["current_turn"]
        self.attack_matrix = data["attack_matrix"]

        self.attack_matrix.pop(str(self.idx))

        self.enemy_tanks = self.parse_enemy_tanks(data["vehicles"])
        self.our_tanks = self.parse_tanks_by_id(data["vehicles"], idx)
        self.tank_cells = self.parse_tank_cells(data["vehicles"])
        self.aggressive_tanks = self.parse_aggressive_tanks(data["vehicles"])

    @staticmethod
    def parse_tanks_by_id(vehicles: dict, idx: int) -> dict[int, "TankModel"]:
        """
        Handles parsing of tanks from "vehicles" part of
        GAME_STATE response for player with given id
        :param vehicles: dict with vehicles from response
        :param idx: player id
        :return: dict(tank_id: TankModel)
        """
        tanks_dict = {}
        for tank_id, i in vehicles.items():
            if i["player_id"] == idx:
                tank_id = int(tank_id)
                position = Cell(
                    i["position"]["x"], i["position"]["y"], i["position"]["z"]
                )
                health = i["health"]
                model = i["vehicle_type"]
                shoot_range_bonus = i["shoot_range_bonus"]
                capture_points = i["capture_points"]
                tanks_dict[tank_id] = TankModel(
                    health, model, position, shoot_range_bonus, capture_points
                )
        return tanks_dict

    def get_ordered_tanks(self) -> OrderedDict:
        """
        Creates ordered dict of player tanks, used only once at the beginning
        of the game to instantiate vehicles and define order of their turn
        :return: ordered left-to-right dict (tank_id: TankModel)
        """
        first_tank = list(self.our_tanks.values())[0]
        second_tank = list(self.our_tanks.values())[1]
        if first_tank.coordinates.x == second_tank.coordinates.x:
            sorting_key = 2
        elif first_tank.coordinates.y == second_tank.coordinates.y:
            sorting_key = 0
        else:
            sorting_key = 1
        sorted_items = sorted(
            self.our_tanks.items(),
            key=lambda x: abs(dataclasses.astuple(x[1].coordinates)[sorting_key]),
        )
        ordered_tanks = coll.OrderedDict()
        for key, value in sorted_items:
            ordered_tanks[key] = value
        return ordered_tanks

    @staticmethod
    def parse_tank_cells(vehicles: dict) -> set[Cell]:
        """
        Handle parsing of tank cells from "vehicles" part of GAME_STATE response
        :param vehicles: dict with "vehicles" part of GAME_STATE response
        :return: set of tank Cell
        """
        return {
            Cell(i["position"]["x"], i["position"]["y"], i["position"]["z"])
            for i in vehicles.values()
        }

    def parse_aggressive_tanks(self, vehicles: dict) -> dict[Cell, int]:
        """
        :param vehicles: dict with "vehicles" part of GAME_STATE response
        :return: dict (cell: health) of tanks that we can shoot
        """
        aggressive_tanks = {}
        for i in vehicles.values():
            if i["player_id"] in self.get_non_neutral_players():
                position = (i["position"]["x"], i["position"]["y"], i["position"]["z"])
                health = i["health"]
                aggressive_tanks[Cell(*position)] = health
        return aggressive_tanks

    def parse_enemy_tanks(self, vehicles: dict) -> dict[Cell, int]:
        """
        :param vehicles: dict with "vehicles" part of GAME_STATE response
        :return: dict (cell: health) of enemy tanks
        """
        enemy_tanks = {}
        for i in vehicles.values():
            if i["player_id"] != self.idx:
                position = (i["position"]["x"], i["position"]["y"], i["position"]["z"])
                health = i["health"]
                enemy_tanks[Cell(*position)] = health
        return enemy_tanks

    def get_our_tank_id(self, cell) -> int:
        """
        :param cell: cell with tank
        :return: t_id of our tank in given cell
        """
        for tank_id, model in self.our_tanks.items():
            if model.coordinates == cell:
                return tank_id

    def get_non_neutral_players(self) -> set[int]:
        """
        return players which we may attack using attack matrix
        :return: set of players ids
        """
        non_neutral_set = {int(player) for player in self.attack_matrix}
        for player in list(non_neutral_set):
            for value in self.attack_matrix.values():
                if player in value:
                    non_neutral_set.remove(player)
        for player, attack_list in self.attack_matrix.items():
            if self.idx in attack_list:
                non_neutral_set.add(int(player))
        return non_neutral_set

    def update_data(self, data: tuple[str, dict]) -> None:
        """
        updates tanks state for current turn using action provided by vehicle
        :param data: action provided by vehicle in vehicles turn
        :return: None
        """
        if data:
            action = data[0]
            vehicle_id = data[1]["vehicle_id"]
            vehicle_type = self.our_tanks[vehicle_id].vehicle_type
            if vehicle_type == "at_spg":
                return
            cell = (
                data[1]["target"]["x"],
                data[1]["target"]["y"],
                data[1]["target"]["z"],
            )
            position = Cell(*cell)
            if action == Actions.SHOOT:
                self.aggressive_tanks[position] -= gb_cf.DAMAGE[vehicle_type]
                if self.aggressive_tanks[position] <= 0:
                    self.aggressive_tanks.pop(position)
            else:
                self.tank_cells.remove(self.our_tanks[vehicle_id].coordinates)
                self.tank_cells.add(position)
                self.our_tanks[vehicle_id].coordinates = position

    def get_aggressive_cells(self) -> set[Cell]:
        """
        returns cells with tanks that we may shoot
        :return: set of cells
        """
        if self.aggressive_tanks:
            return set(self.aggressive_tanks)
        return set()

    def get_our_tanks_cells(self) -> set[Cell]:
        """
        return cells with our tanks
        :return: set of cells
        """
        return {vehicle.coordinates for vehicle in self.our_tanks.values()}


class GameActions:
    """
    Data class to parse and store data from GAME_ACTIONS response
    Currently not used
    """

    def __init__(self, data: dict):
        self.data = data


@dataclasses.dataclass
class TankModel:
    """
    Dataclass to store dynamic state of tanks
    """

    health: int
    vehicle_type: str
    coordinates: Cell
    shoot_range_bonus: int
    capture_points: int
