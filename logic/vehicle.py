"""
This Module contents game logic only, it does not store any data.
"""
import random
from typing import Optional, Union

from config import game_balance as gb_cf
from config.config import Actions
from logic.cell import Cell
from logic.model import TankModel, GameState, GameMap


class Vehicle:
    """
    Superclass for all vehicle types implements most
    common vehicle strategy, and vehicle actions
    """

    def __init__(self, t_id: int, spec: TankModel):
        self.t_id = t_id
        self.model = spec
        self.speed = gb_cf.SPEED_POINTS[self.model.vehicle_type]
        self.max_shoot_range = gb_cf.MAX_RANGE[self.model.vehicle_type]
        self.min_range = gb_cf.MIN_RANGE[self.model.vehicle_type]
        self.damage = gb_cf.DAMAGE[self.model.vehicle_type]
        self.priority = None

    def refresh_model(self, state: GameState) -> None:
        """
        Refreshes tank model using game state
        :param state: GameState object
        :return: None
        """
        self.model = state.our_tanks[self.t_id]

    def cells_in_range(self) -> set[Cell]:
        """
        Returns cells in shooting range of tank
        :return: set of Cell
        """
        max_radius = self.max_shoot_range + self.model.shoot_range_bonus
        return self.model.coordinates.in_radius_excl(self.min_range, max_radius)

    def targets_in_range(
        self, state: GameState, map_: GameMap
    ) -> Union[set, set[Cell]]:
        """
        Returns cells with non-neutral player
        tanks that are in range of current tank
        :param state: GameState obj
        :param map_: GameMap obj
        :return: set of cells
        """
        return self.cells_in_range().intersection(state.get_aggressive_cells())

    def shoot(self, target: Cell) -> tuple[Actions, dict]:
        """
        Produces SHOOT action with self t_id and target coordinate
        :param target: cell with enemy tank
        :return: Python obj SHOOT action
        """
        return Actions.SHOOT, {
            "vehicle_id": self.t_id,
            "target": {"x": target.x, "y": target.y, "z": target.z},
        }

    def move(self, cell: Cell) -> tuple[Actions, dict]:
        """
        Produces MOVE action with self t_id and target coordinate
        :param cell: empty Coordinate obj in moving range
        :return: Pyhon obj MOVE action
        """
        return Actions.MOVE, {
            "vehicle_id": self.t_id,
            "target": {"x": cell.x, "y": cell.y, "z": cell.z},
        }

    def choose_target(self, targets: set[Cell], state: GameState) -> Cell:
        """
        Choose target from given set of available
        targets, according to given GameState
        :param targets: set of available targets
        :param state: GameState obj
        :return: target cell
        """
        for target in targets:
            if state.aggressive_tanks[target] <= self.damage:
                return target
        return targets.pop()

    def make_turn(
        self, state: GameState, map_: GameMap
    ) -> Optional[tuple[Actions, dict]]:
        """
        Main method to provide vehicle action, returns
        Python obj with SHOOT or MOVE action | None
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
        return None

    def set_priority(self, state: GameState, map_: GameMap) -> None:
        """
        Method set priority cell to move for current vehicle,
        according to game situation
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
            free_cells = map_.available_cells.difference(state.tank_cells)
            self.priority = random.choice(list(free_cells.difference(map_.base)))

    def move_to_priority(
        self, map_: GameMap, state: GameState
    ) -> Optional[tuple[Actions, dict]]:
        """
        Method finds path to priority, and call move action
        with reachable empty cell on the path to priority,
        according to current game situation
        :param map_: GameMap obj
        :param state: GameState obj
        :return:
        """
        step_cell = None
        path_to_priority = self.model.coordinates.a_star(
            map_.available_cells, self.priority
        )
        speed_points = self.speed
        if speed_points >= len(path_to_priority):
            step_cell = path_to_priority[-1]
        else:
            while speed_points:
                if path_to_priority[speed_points - 1] in state.tank_cells:
                    speed_points -= 1
                else:
                    step_cell = path_to_priority[speed_points - 1]
                    break
        if step_cell and step_cell not in state.tank_cells:
            return self.move(step_cell)
        return None

    @staticmethod
    def build(t_id: int, spec: TankModel) -> "Vehicle":
        """
        fabric method instantiates vehicles of given spec
        :param t_id: tanks id
        :param spec: TankModel obj
        :return: Vehicle of proper type
        """
        vehicle_types = {
            "medium_tank": MediumTank,
            "light_tank": LightTank,
            "heavy_tank": HeavyTank,
            "at_spg": AtSpg,
            "spg": Spg,
        }
        return vehicle_types[spec.vehicle_type](t_id, spec)


class MediumTank(Vehicle):
    """
    Medium tanks class that implements
    specific strategy for medium tanks
    """


class LightTank(Vehicle):
    """
    Light tanks class that implements
    specific strategy for light tanks
    """


class HeavyTank(Vehicle):
    """
    Heavy tanks class that implements
    specific strategy for heavy tanks
    """


class AtSpg(Vehicle):
    """
    AtSpg class that implements
    specific strategy for AtSpg
    """

    def targets_in_range(self, state: GameState, map_: GameMap) -> set[Cell]:
        """
        Overloads shooting mechanic for atSPG, return set of cells on available directions
        that contains aggressive tanks
        :param state: GameState obj
        :param map_: GameMap obj
        :return: set of cells, or empty set
        """
        targets = set()
        for direction in self.range_exclude_walls(map_, self.cells_in_range()):
            if direction.intersection(state.get_aggressive_cells()):
                targets.update(direction)
        return targets

    def choose_target(self, targets: set[Cell], state: GameState) -> Cell:
        """
        Choose direction with maximum number of available targets
        :param targets: list that contains sets of Cell, each set - direction
        :param state: GameState obj
        :return: cell to shoot
        """
        max_enemy_direction = max(
            (targets.intersection(direction) for direction in self.cells_in_range()),
            key=len,
        )
        return max_enemy_direction.intersection(
            self.model.coordinates.neighbours()
        ).pop()

    def range_exclude_walls(
        self, map_: GameMap, directions: list[set[Cell]]
    ) -> list[set[Cell]]:
        """
        Exclude cells that are behind the obstacles from atSPG shoot directions
        :param map_: GameMap obj
        :param directions: list with sets of cells in directions which atSPG can shoot
        :return: list that contains sets of Cell, each set
        - direction which atSPG can shoot, depending on obstacles
        """
        new_directions = []
        for direction in directions:
            if direction.intersection(map_.obstacles):
                list_direction = list(direction)
                list_direction.sort(key=self.model.coordinates.cube_distance)
                current_direction = set()
                for cell in list_direction:
                    if cell in map_.obstacles:
                        break
                    current_direction.add(cell)
                new_directions.append(current_direction)
            else:
                new_directions.append(direction)
        return new_directions

    def cells_in_range(self) -> list[set[Cell]]:
        """
        returns directions which atSPG can shoot,
        does not take into account obstacles
        :return: list with sets of Cell
        """
        radius = self.max_shoot_range + self.model.shoot_range_bonus
        return self.model.coordinates.normal_directions(radius)


class Spg(Vehicle):
    """
    Spg class that implements
    specific strategy for spg
    """
