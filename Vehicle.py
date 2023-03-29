from typing import Optional, Union


import cube_math as cm
from Model import TankModel, GameState, GameMap

MT_MAX_RANGE = 2
MT_MIN_RANGE = 1
MT_SPEED_POINTS = 2


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
    def __init__(self,  spec: tuple[int, "TankModel"], sp: int, max_range: int, min_range: int):
        self.id = spec[0]
        self.model = spec[-1]
        self.sp = sp
        self.max_shoot_range = max_range
        self.min_range = min_range
        self.priority = None

    def refresh_model(self, state: "GameState") -> None:
        self.model = state.our_tanks[self.id]

    def cells_in_range(self) -> set[tuple[int, int, int]]:
        return cm.in_radius_excl(self.model.coordinates, self.min_range, self.max_shoot_range
                                 + self.model.shoot_range_bonus)

    def targets_in_range(self, state: "GameState") -> Union[set, set[tuple[int, int, int]]]:
        return self.cells_in_range().intersection(state.agressive_cells)

    def shoot(self, target: tuple[int, int, int]) -> tuple[str, dict]:
        return "SHOOT", {"vehicle_id": self.id, "target": {"x": target[0], "y": target[1], "z": target[2]}}

    def move(self, cell: tuple[int, int, int]) -> tuple[str, dict]:
        return "MOVE", {"vehicle_id": self.id, "target": {"x": cell[0], "y": cell[1], "z": cell[2]}}

    def choose_target(self, targets: set[tuple[int, int, int]], state: "GameState", map_: "GameMap")\
            -> tuple[int, int, int]:
        return targets.pop()  # TODO here some target choosing logic, targets are already shootable:)

    def make_turn(self, state, map_) -> Optional[tuple[str, dict]]:
        self.refresh_model(state)
        targets = self.targets_in_range(state)
        if targets:
            target = self.choose_target(targets, state, map_)
            return self.shoot(target)
        self.set_priority(state, map_)
        if self.priority():
            return self.move_to_priority(map_, state)

    def set_priority(self, state, map_):
        is_in_base = self.model.coordinates in map_.base_cells
        if is_in_base:
            self.priority = None
        our_tanks_in_base = state.our_tanks_cells.intersect(map_.base_cells)
        empty_base_cells = map_.base_cells.difference(state.tank_cells)
        if empty_base_cells and our_tanks_in_base < 2:
            self.priority = empty_base_cells.pop(0)
            # TODO: all strategy is here, should set priority (one free cell or None), we can overload it for different types of vehicles

    def move_to_priority(self, map_, state):
        step_cell = None
        path_to_priority = cm.a_star(map_.available_calls, self.model.coordinates, self.priority)
        speed_points = self.sp
        if speed_points >= len(path_to_priority):
            step_cell = path_to_priority[-1]
        else:
            while speed_points:
                if not(path_to_priority[speed_points - 1] in state.tank_cells):
                    step_cell = path_to_priority[speed_points - 1]
                    break
                speed_points -= 1
        if step_cell:
            return self.move(step_cell)


class MediumTank(Vehicle):
    def __init__(self, spec: tuple[int, "TankModel"]):
        super().__init__(spec, MT_SPEED_POINTS, MT_MAX_RANGE, MT_MIN_RANGE)

# <------------- End of stage 1


class LightTank(Vehicle):
    pass


class HeavyTank(Vehicle):
    pass


class AtSpg(Vehicle):
    pass


class Spg(Vehicle):
    pass
