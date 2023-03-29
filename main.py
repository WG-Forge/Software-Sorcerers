from Client import Dialogue
from Model import GameState, GameMap, GameActions
from Vehicle import VehicleFactory

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
        self.game_state = None
        self.game_actions = None
        self.map = None

    def play(self):
        self.init_game()
# <---------------------- main loop ---------------------
        while not self.game_state.is_finished:
            while self.game_state.current_player_id != self.idx:
                self.refresh_game_state()
            for vehicle in self.vehicles_list:
                vehicle_turn = vehicle.make_turn(self.game_state, self.map, self.game_actions)
                if not (vehicle_turn is None):
                    self.game_state.update_data(vehicle_turn)
                    self.dialogue.send(vehicle_turn)
            self.dialogue.send("TURN")
# <-------------------- end of main loop ----------------

        print(f"Game ended, winner: {self.game_state.winner}")
        self.dialogue.send("LOGOUT")

    def refresh_game_state(self):
        self.game_state = GameState(self.dialogue.send("GAME_STATE"), self.idx)

    def refresh_game_actions(self):
        self.game_actions = GameActions(self.dialogue.send("ACTIONS"))

    def init_vehicles(self):
        self.vehicles_list = [VehicleFactory.build(our_vehicle) for our_vehicle in self.game_state.our_tanks.items]
        # TODO Game_state must have ordered (left-to right) dict "our_vehicles" with id: TankModel

    def init_game(self):
        self.dialogue.start_dialogue()
        login_answer = self.dialogue.send("LOGIN", LOGIN_DATA)
        self.idx = login_answer["idx"]
        self.map = GameMap(self.dialogue.send("MAP"))
        self.refresh_game_state()
        #
        self.init_vehicles()
