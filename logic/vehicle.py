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
        self.damage = gb_cf.DAMAGE[self.model.vehicle_type]
        self.priority: Optional[Cell] = None

    def refresh_model(self, state: GameState) -> None:
        """
        Refreshes tank model using game state
        :param state: GameState object
        :return: None
        """
        self.model = state.our_tanks[self.t_id]

    @staticmethod
    def cells_in_range(model: TankModel) -> set[Cell]:
        """
        Returns cells in shooting range of tank
        :param model: TankModel obj or EnemyTankModel obj
        :return: set of Cell
        """

        max_radius = gb_cf.MAX_RANGE[model.vehicle_type] + model.shoot_range_bonus
        return model.coordinates.in_radius_excl(
            gb_cf.MIN_RANGE[model.vehicle_type], max_radius
        )

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
        return self.cells_in_range(self.model).intersection(
            state.get_aggressive_cells()
        )

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
            if (
                self.can_kill(target, state)
                and state.enemy_tanks[target].capture_points > 0
            ):
                return target
        for target in targets:
            if self.can_kill(target, state):
                return target
        for target in targets:
            if state.enemy_tanks[target].capture_points > 0:
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
        self.set_priority(state, map_)
        targets = self.targets_in_range(state, map_)
        step_cell = None

        if self.priority:
            step_cell = self.move_to_priority(map_, state)

        if targets:
            target = self.choose_target(targets, state)
            return self.shoot(target)
        elif step_cell:
            return self.move(step_cell)
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

        empty_base_cells = map_.base.difference(state.tank_cells)
        if empty_base_cells:
            self.priority = max(
                empty_base_cells, key=self.model.spawn_point.cube_distance
            )
        if self.priority is None or self.priority == self.model.coordinates:
            free_cells = map_.get_available_cells().difference(state.tank_cells)
            self.priority = random.choice(list(free_cells.difference(map_.base)))

    def move_to_priority(self, map_: GameMap, state: GameState) -> Optional[Cell]:
        """
        Method finds path to priority, and return
        reachable empty cell on the path to priority,
        according to current game situation
        :param map_: GameMap obj
        :param state: GameState obj
        :return: Cell
        """
        step_cell = None
        speed_points = self.speed
        if speed_points == 1:
            available_cells = map_.get_available_cells().difference(
                state.tank_cells.intersection(self.model.coordinates.neighbours())
            )
        else:
            available_cells = map_.get_available_cells()
        path_to_priority = self.model.coordinates.a_star(available_cells, self.priority)
        if not path_to_priority:
            return None

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
            return step_cell
        return None

    def is_capturing_base(self, state: GameState, map_: GameMap) -> bool:
        """
        Check if at the end of our turn we can have max capture points
        if vehicles will stay on their places. Returns true only if
        current vehicle located at the base cell.
        Does not check if it is more than two players on base cells
        :param  map_: GameMap obj
        :param state: GameState obj
        :return: bool
        """

        return (
            self.model.coordinates in map_.base
            and len(map_.base.intersection(state.get_our_tanks_cells()))
            >= gb_cf.MAX_CAPTURE_POINTS - state.get_total_cp()
        )

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

    @staticmethod
    def get_hot_spots(state: GameState, map_: GameMap) -> set[Cell]:
        """
        Returns set of Cells which enemies can shoot
        :param state: GameState obj
        :param map_: GameMap obj
        :return: set of Cells
        """
        hot_spots = set()
        for cell, tank in state.enemy_tanks.items():
            if tank.vehicle_type != "at_spg":
                hot_spots.update(Vehicle.cells_in_range(tank))
            else:
                hot_spots.update(
                    *AtSpg.range_exclude_walls(cell, map_, AtSpg.cells_in_range(tank))
                )
        return hot_spots

    def can_kill(self, target: Cell, state: GameState) -> bool:
        """
        Returns true if our tank can kill enemy by its shot
        :param state: GameState obj
        :param target: Cell with enemy tank in it
        :return: bool
        """

        return (
            self.model.vehicle_type == "at_spg"
            or state.aggressive_tanks[target] <= self.damage
        )


class MediumTank(Vehicle):
    """
    Medium tanks class that implements
    specific strategy for medium tanks
    """

    def set_priority(self, state: GameState, map_: GameMap) -> None:
        """
        Set light_repair cell as a priority for medium tank if it has
        less than full HP, it will not leave base if we about to capture it
        :param state:
        :param map_:
        :return:
        """
        if self.model.health == 1 and not self.is_capturing_base(state, map_):
            self.priority = min(
                map_.light_repairs,
                key=self.model.coordinates.cube_distance,
            )
        else:
            super().set_priority(state, map_)


class LightTank(Vehicle):
    """
    Light tanks class that implements
    specific strategy for light tanks
    """

    def set_priority(self, state: GameState, map_: GameMap) -> None:
        """
        Sets active catapult cell as a priority for
        light tank if it has no shoot_range bonus
        :param state: GameState obj
        :param map_: GameMap obj
        :return: None
        """
        active_catapults = map_.catapults.difference(state.inactive_catapults)
        if not self.model.shoot_range_bonus and active_catapults:
            self.priority = min(
                active_catapults, key=self.model.spawn_point.cube_distance
            )

        else:
            super().set_priority(state, map_)

    def move_to_priority(self, map_: GameMap, state: GameState) -> Optional[Cell]:
        """
        Overloads Vehicle move_to priority. Light Tank
        will try to avoid receiving damage
        :param map_: GameMap obj
        :param state: GameState obj
        :return: Cell
        """
        step_cell = super().move_to_priority(map_, state)
        if step_cell in self.get_hot_spots(state, map_):
            self.speed = gb_cf.SPEED_POINTS[self.model.vehicle_type]
            safe_cells = map_.get_available_cells().difference(
                state.tank_cells.union(self.get_hot_spots(state, map_))
            )
            reachable_safe_cells = safe_cells.intersection(
                self.model.coordinates.in_radius(self.speed)
            )
            if reachable_safe_cells:
                self.priority = min(
                    reachable_safe_cells, key=self.priority.cube_distance
                )
                step_cell = super().move_to_priority(map_, state)
            if step_cell in self.get_hot_spots(state, map_):
                available_neighbours = (
                    map_.get_available_cells()
                    .intersection(self.model.coordinates.neighbours())
                    .difference(state.tank_cells)
                )
                safe_neighbours = available_neighbours.difference(
                    self.get_hot_spots(state, map_)
                )
                if safe_neighbours:
                    step_cell = min(safe_neighbours, key=self.priority.cube_distance)
        return step_cell


class HeavyTank(Vehicle):
    """
    Heavy tanks class that implements
    specific strategy for heavy tanks
    """

    def set_priority(self, state: GameState, map_: GameMap) -> None:
        """
        Sets hard_repair cell as a priority for heavy tank
        if it has less than full HP, it will not leave base if we are
        about to capture it.
        :param state: GameState obj
        :param map_: GameMap obj
        :return: None
        """
        if not self.is_capturing_base(state, map_) and self.model.health == 1:
            self.priority = min(
                map_.hard_repairs, key=self.model.coordinates.cube_distance
            )
        else:
            super().set_priority(state, map_)


class AtSpg(Vehicle):
    """
    AtSpg class that implements
    specific strategy for AtSpg
    """

    def targets_in_range(self, state: GameState, map_: GameMap) -> set[Cell]:
        """
        Overloads shooting mechanic for atSPG,
        return set of cells on available directions
        that contains aggressive tanks
        :param state: GameState obj
        :param map_: GameMap obj
        :return: set of cells, or empty set
        """
        targets = set()
        for direction in self.range_exclude_walls(
            self.model.coordinates, map_, self.cells_in_range(self.model)
        ):
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
            (
                targets.intersection(direction)
                for direction in self.cells_in_range(self.model)
            ),
            key=len,
        )
        return max_enemy_direction.intersection(
            self.model.coordinates.neighbours()
        ).pop()

    @staticmethod
    def range_exclude_walls(
        cell: Cell, map_: GameMap, directions: list[set[Cell]]
    ) -> list[set[Cell]]:
        """
        Exclude cells that are behind the obstacles from atSPG shoot directions
        :param cell: tank Cell
        :param map_: GameMap obj
        :param directions: list with sets of cells in directions which atSPG can shoot
        :return: list that contains sets of Cell, each set
        - direction which atSPG can shoot, depending on obstacles
        """
        new_directions = []
        for direction in directions:
            if direction.intersection(map_.obstacles):
                list_direction = list(direction)
                list_direction.sort(key=cell.cube_distance)
                current_direction = set()
                for cell in list_direction:
                    if cell in map_.obstacles:
                        break
                    current_direction.add(cell)
                new_directions.append(current_direction)
            else:
                new_directions.append(direction)
        return new_directions

    @staticmethod
    def cells_in_range(model: TankModel) -> list[set[Cell]]:
        """
        returns directions which atSPG can shoot,
        does not take into account obstacles
        :return: list with sets of Cell
        """
        radius = gb_cf.MAX_RANGE[model.vehicle_type] + model.shoot_range_bonus
        return model.coordinates.normal_directions(radius)

    def set_priority(self, state: GameState, map_: GameMap) -> None:
        """
        Sets hard_repair cell as a priority for at_spg if it has less
        than full HP, it will not leave base if we are about to capture it
        :param state: GameState obj
        :param map_: GameMap obj
        :return: None
        """

        if self.model.health == 1 and not self.is_capturing_base(state, map_):
            self.priority = min(
                map_.hard_repairs, key=self.model.coordinates.cube_distance
            )
        else:
            super().set_priority(state, map_)


class Spg(Vehicle):
    """
    Spg class that implements
    specific strategy for spg
    """

    def move_to_priority(self, map_: GameMap, state: GameState) -> Optional[Cell]:
        """
        Overloads Vehicle move_to_priority to
        avoid dangerous cells if it is possible
        :param map_: GameMap obj
        :param state: GameState obj
        :return: Cell
        """
        step_cell = super().move_to_priority(map_, state)
        if step_cell in self.get_hot_spots(state, map_):
            free_cells = map_.get_available_cells().difference(state.tank_cells)
            free_neighbour_cells = free_cells.intersection(
                self.model.coordinates.neighbours()
            )
            safe_neighbour_cells = free_neighbour_cells.difference(
                self.get_hot_spots(state, map_)
            )
            if safe_neighbour_cells:
                return min(
                    safe_neighbour_cells, key=lambda x: x.cube_distance(self.priority)
                )
        return step_cell
