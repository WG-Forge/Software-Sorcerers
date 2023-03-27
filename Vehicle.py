from typing import Optional
import cube_math as cm


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
    def __init__(self, id: int, coordinates: tuple[int, int, int], hp: int, sp: int, shoot_distance: int,):
        self.id
        self.coordinates = coordinates
        self.hp = hp
        self.sp = sp
        self.shoot_distance = shoot_distance
        #self.capture_points = 0 #maybe needed
        #self.destruction_points = 0 #maybe needed

    def make_turn(self, state, map_, actions) -> Optional[tuple[str, dict]]:
        # must return ("SHOOT", {dict}), ("MOVE", {dict}), or None

        self.refresh_state(state)

        can_shoot, coord = self.can_shoot(state, map_, actions)

        if can_shoot:
            return "SHOOT", {"vehicle_id":id,"target":{"x":coord[0],"y":coord[1],"z":coord[2]}}
        
        can_move, coord = self.can_move(state, map_, actions)

        if can_move:
            return "MOVE", {"vehicle_id":id,"target":{"x":coord[0],"y":coord[1],"z":coord[2]}}

        return None
    
    def refresh_state(self, state):
        #updates vehicle coordinates and hp

        self.coordinates = state.vehicles[self.id]["position"]
        self.hp = state.vehicles[self.id]["health"]

    def can_shoot(self, state, map_, actions) -> tuple[bool, Optional[tuple[int, int, int]]]:
        # must return (True, (x, y, z)) or (False, None)

        for vehicle_id, vehicle in state.vehicles.items():

            #we're not gonna shoot our tanks
            if state.current_player_idx == vehicle["player_id"]:
                continue
            
            if cm.distance(self.coordinates, vehicle["position"]) != self.shoot_distance:
                continue

            #TODO: check if we are able to shoot this tank (rule of neutrality)
            
        #if we didn't find any enemy tanks in range return False, None
        return False, None

    def can_move(self, state, map_, actions) -> tuple[bool, Optional[tuple[int, int, int]]]:
        # must return (True, (x, y, z)) or (False, None)

        #if tank is in base, it shouldn't move
        if self.coordinate in map_.base:
            return False, None
        
        #if tank is not in base, try to move towards the base
        for base_coord in map_.base:
            path = cm.a_star(map_.cells, self.coordinates, base_coord) 
            if path[1] in map_.available_cells:
                return True, path[1]
            elif path[0] in map_.available_cells:
                return True, path[0]
            else:
                return False, None


class MediumTank(Vehicle):
    def __init__(self, spec: tuple[int, tuple[tuple[int, int, int], str]]):
        """
        :param spec: tuple(vehicle_id (coordinates, vehicle_type))
        """
        super().__init__(spec[0], spec[1][0], 2, 2, 2)

# <------------- End of stage 1


class LightTank(Vehicle):
    pass


class HeavyTank(Vehicle):
    pass


class AtSpg(Vehicle):
    pass


class Spg(Vehicle):
    pass
