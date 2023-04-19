from typing import Optional, Union
import random

from config import game_balance as gb_cf
from config.actions import Actions
import cube_math as cm
from model import TankModel, GameState, GameMap

"""
This Module contents game logic only, it does not store any data.
"""

class VehicleFactory:
    @staticmethod
    def build(spec: tuple[int, "TankModel"]) -> "Vehicle":
        """
        instantiates vehicles of given spec
        :param spec: tuple(vehicle_id (coordinates, vehicle_type))
        :return: Vehicle of proper type
        """
        match spec[-1].vehicle_type:
            case "medium_tank":
                return MediumTank(spec)
            case "light_tank":
                return LightTank(spec)
            case "heavy_tank":
                return HeavyTank(spec)
            case "at_spg":
                return AtSpg(spec)
            case "spg":
                return Spg(spec)


class Vehicle:
    """
    Superclass for all vehicle types implements most common vehicle strategy, and vehicle actions
    """
    def __init__(self,  spec: tuple[int, "TankModel"]):
        self.id = spec[0]
        self.model = spec[-1]
        self.sp = gb_cf.SPEED_POINTS[self.model.vehicle_type]
        self.max_shoot_range = gb_cf.MAX_RANGE[self.model.vehicle_type]
        self.min_range = gb_cf.MIN_RANGE[self.model.vehicle_type]
        self.damage = gb_cf.DAMAGE[self.model.vehicle_type]
        self.priority = None

    def refresh_model(self, state: "GameState") -> None:
        """
        Refreshes tank model using game state
        :param state: GameState object
        :return: None
        """
        self.model = state.our_tanks[self.id]

    def cells_in_range(self) -> set[tuple[int, int, int]]:
        """
        Returns cells in shooting range of tank
        :return: set of cells
        """
        return cm.in_radius_excl(self.model.coordinates, self.min_range, self.max_shoot_range
                                 + self.model.shoot_range_bonus)

    def targets_in_range(self, state: "GameState", map_:"GameMap") -> Union[set, set[tuple[int, int, int]]]:
        """
        Returns cells with non-neutral player tanks that are in range of current tank
        :param state: GameState obj
        :param map_: GameMap obj
        :return: set of cells
        """
        return self.cells_in_range().intersection(state.get_agressive_cells())

    def shoot(self, target: tuple[int, int, int]) -> tuple["Actions", dict]:
        """
        Produces SHOOT action with self.id and target cell
        :param target: cell with enemy tank
        :return: Python obj SHOOT action
        """
        return Actions.SHOOT, {"vehicle_id": self.id, "target": {"x": target[0], "y": target[1], "z": target[2]}}

    def move(self, cell: tuple[int, int, int]) -> tuple["Actions", dict]:
        """
        Produces MOVE action with self.id and target cell
        :param cell: empty cell in moving range
        :return: Pyhon obj MOVE action
        """
        return Actions.MOVE, {"vehicle_id": self.id, "target": {"x": cell[0], "y": cell[1], "z": cell[2]}}

    def choose_target(self, targets: set[tuple[int, int, int]], state: "GameState") -> tuple[int, int, int]:
        """
        Choose target from given set of available targets, according to given GameState
        :param targets: set of available targets
        :param state: GameState obj
        :param map_: GameMap obj
        :return: target cell
        """
        for target in targets:
            if state.agressive_tanks[target] <= self.damage:
                return target
        return targets.pop()

    def make_turn(self, state: "GameState", map_: "GameMap") -> Optional[tuple["Actions", dict]]:
        """
        Main method to provide vehicle action, returns Python obj with SHOOT or MOVE action | None
        :param state: GameState obj
        :param map_: MapState obj
        :return: Python obj action
        """
        self.refresh_model(state)
        targets = self.targets_in_range(state, map_)
        if targets:
            target = self.choose_target(targets, state)
            return self.shoot(target)
        self.set_priority(state, map_)
        if self.priority:
            return self.move_to_priority(map_, state)

    def set_priority(self, state: "GameState", map_: "GameMap") -> None:
        """
        Method set priority cell to move for current vehicle, according to game situation
        :param state: GameState obj
        :param map_: GameMap obj
        :return: None
        """
        is_in_base = self.model.coordinates in map_.base
        if is_in_base:
            self.priority = None
            return
        our_tanks_in_base = state.get_our_tanks_cells().intersection(map_.base)
        empty_base_cells = map_.base.difference(state.tank_cells)
        if empty_base_cells and len(our_tanks_in_base) < 2:
            self.priority = empty_base_cells.pop()
        if self.priority is None or self.priority == self.model.coordinates:
            self.priority = random.choice(list(map_.available_cells.difference(map_.base).difference(state.tank_cells)))

    def move_to_priority(self, map_: "GameMap", state: "GameState") -> Optional[tuple["Actions", dict]]:
        """
        Method finds path to priority, and call move action with reachable empty cell on the path to priority,
        according to current game situation
        :param map_: GameMap obj
        :param state: GameState obj
        :return:
        """
        step_cell = None
        path_to_priority = cm.a_star(map_.available_cells, self.model.coordinates, self.priority)
        speed_points = self.sp
        if speed_points >= len(path_to_priority):
            step_cell = path_to_priority[-1]
        else:
            while speed_points:
                if not(path_to_priority[speed_points - 1] in state.tank_cells):
                    step_cell = path_to_priority[speed_points - 1]
                    break
                speed_points -= 1
        if step_cell and not(step_cell in state.tank_cells):
            return self.move(step_cell)


class MediumTank(Vehicle):
    def __init__(self, spec: tuple[int, "TankModel"]):
        super().__init__(spec)


class LightTank(Vehicle):
    def __init__(self, spec: tuple[int, "TankModel"]):
        super().__init__(spec)


class HeavyTank(Vehicle):
    def __init__(self, spec: tuple[int, "TankModel"]):
        super().__init__(spec)


class AtSpg(Vehicle):
    def __init__(self, spec: tuple[int, "TankModel"]):
        super().__init__(spec)

    def targets_in_range(self, state: "GameState", map_: "GameMap") -> Union[set, set[tuple[int, int, int]]]:
        """
        Overloads shooting mechanic for atSPG, return set of cells on available directions
        that contains agressive tanks and does not contain neutral or friendly tanks
        :param state: GameState obj
        :param map_: GameMap obj
        :return: set of cells, or empty set
        """
        targets = set()
        neutral_tanks = state.tank_cells.difference(state.get_agressive_cells())
        for direction in self.range_exclude_walls(map_, self.cells_in_range()):
            if not direction.intersection(neutral_tanks) and direction.intersection(state.get_agressive_cells()):
                targets.union(direction)
        return targets

    def choose_target(self, targets: set[tuple[int, int, int]],
                      state: "GameState") -> tuple[int, int, int]:
        """
        Choose direction with maximum number of available targets
        :param targets: list that contains sets of cells, each set - direction
        :param state: GameState obj
        :return: cell to shoot
        """
        return max([targets.intersection(direction) for direction in self.cells_in_range()], key=len).pop()

    def range_exclude_walls(self, map_: "GameMap", directions: list[set[tuple[int, int, int]]]
                            ) -> list[set[tuple[int, int, int]]]:
        """
        Exclude cells that are behind the obstackles from atSPG shoot directions
        :param map_: GameMap obj
        :param directions: list with sets of cells in directions which atSPG can shoot
        :return: list that contains sets of cells, each set - direction which atSPG can shoot, depending on obstacles
        """
        new_directions = []
        for direction in directions:
            if direction.intersection(map_.obstacles):
                list_direction = list(direction)
                list_direction.sort(key=lambda x: cm.cube_distance(self.model.coordinates, x))
                current_direction = set()
                for cell in list_direction:
                    if cell in map_.obstacles:
                        break
                    current_direction.add(cell)
                new_directions.append(current_direction)
            else:
                new_directions.append(direction)
        return new_directions

    def cells_in_range(self) -> list[set[tuple[int, int, int]]]:
        """
        returns directions which atSPG can shoot, does not take into account obstacles
        :return: list with sets of cells
        """
        return cm.normal_directions(self.model.coordinates, self.max_shoot_range + self.model.shoot_range_bonus)


class Spg(Vehicle):
    def __init__(self, spec: tuple[int, "TankModel"]):
        super().__init__(spec)
