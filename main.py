from Client import Dialogue
from Model import Game_state, Game_map, Game_actions  # TODO Classes to implement
from Vehicle import Vehicle  # TODO Class to implement it shoud be a fabric that instantiates proper type of vehicle

LOGIN_DATA = {
    "name": "Sorcerer",
    "password": "",
    "num_turns": None,
    "num_players": 1,
    "is_observer": False
}


class Controller:
    def __init__(self):
        self.idx = None
        self.dialogue = Dialogue()
        self.vehicles_list = None
        self.game_state = None  # TODO Game_state class to implement
        self.game_actions = None  # TODO Game_actions class to implement
        self.map = None  # TODO  Game_map class to implement

    def play(self):
        self.init_game()

# <---------------------- main loop ---------------------
        while not self.game_state.is_finished:  # TODO Game_state must have bool field is_finished
            while self.game_state.current_player_id != self.idx:
                self.refresh_game_state()
            self.refresh_game_actions()
            for vehicle in self.vehicles_list:
                self.refresh_game_state()
                if vehicle.id in self.game_state.our_vehicles:
                    vehicle_turn = vehicle.make_turn(self.game_state, self.map, self.game_actions)
                    if not (vehicle_turn is None):
                        self.dialogue.send(vehicle_turn)
            self.dialogue.send("TURN")
# <-------------------- end of main loop ----------------

        self.dialogue.send("LOGOUT")

    def refresh_game_state(self):
        self.game_state = Game_state(self.dialogue.send("GAME_STATE"))  # TODO Game_state must parse answer dict

    def refresh_game_actions(self):
        self.game_actions = Game_actions(self.dialogue.send("ACTIONS"))  # TODO Game_actions must parse answer dict

    def init_vehicles(self):
        self.vehicles_list = [Vehicle(our_vehicle) for our_vehicle in self.game_state.our_vehicles.items]
        # TODO Game_state must have ordered dict "our_vehicles" with id: (coordinates, type_of_vehicles)
        # TODO Vehicle class must initialise vehicles of propper type in given coordinates

    def init_game(self):
        self.dialogue.start_dialogue()
        login_answer = self.dialogue.send("LOGIN", LOGIN_DATA)
        self.idx = login_answer["idx"]
        map_answer = self.dialogue.send("MAP")
        self.map = Game_map(map_answer)  # TODO  Game_map must parse answer dict
        self.refresh_game_state()
        self.init_vehicles()
