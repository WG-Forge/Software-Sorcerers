from typing import Optional


class VehicleFactory:
    @staticmethod
    def build(spec: tuple[int, tuple[tuple[int, int, int], str]]) -> "Vehicle":
        """
        instantiates vehicles of given spec
        :param spec: tuple(vehicle_id (coordinates, vehicle_type))
        :return: Vehicle of proper type
        """
        match spec[-1][-1]:
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
    def make_turn(self, state, map_, actions) -> Optional[tuple[str, dict]]:
        # must return ("SHOOT", {dict}), ("MOVE", {dict}), or None
        pass


class MediumTank(Vehicle):
    pass

# <------------- End of stage 1


class LightTank(Vehicle):
    pass


class HeavyTank(Vehicle):
    pass


class AtSpg(Vehicle):
    pass


class Spg(Vehicle):
    pass
