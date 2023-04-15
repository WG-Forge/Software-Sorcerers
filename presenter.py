import time
from copy import deepcopy

from PySide6 import QtCore

from client import Dialogue
from model import GameState, GameMap, GameActions
from vehicle import VehicleFactory


class Presenter(QtCore.QThread):
    game_state_updated = QtCore.Signal(object, object)
    game_ended = QtCore.Signal(str)

    def __init__(self, login_data: dict):
        super().__init__(None)
        self.idx = None
        self.login_data = login_data
        self.dialogue = Dialogue()
        self.vehicles_list = None
        self.game_state = None
        self.game_actions = None
        self.map = None
        self.turn = None

    def run(self):
        self.init_game()
# <---------------------- main loop ---------------------
        while not self.game_state.is_finished:
            current_game_state = self.dialogue.send("GAME_STATE")
            if current_game_state["finished"]:
                self.refresh_game_state(current_game_state)
                break
            if current_game_state["current_turn"] != self.turn:
                self.refresh_game_state(current_game_state)
                self.game_state_updated.emit(self.map, deepcopy(self.game_state))
                self.turn = self.game_state.current_turn
            if current_game_state["current_player_idx"] != self.idx:
                self.dialogue.send("TURN")
                continue
            for vehicle in self.vehicles_list:
                vehicle_turn = vehicle.make_turn(self.game_state, self.map)
                if not (vehicle_turn is None):
                    self.game_state.update_data(vehicle_turn)
                    self.dialogue.send(*vehicle_turn)
            self.dialogue.send("TURN")
# <-------------------- end of main loop ----------------

        self.game_ended.emit(f"Game ended, winner: {self.game_state.winner}")
        self.dialogue.send("LOGOUT")
        self.quit()

    def refresh_game_state(self, game_state):
        self.game_state = GameState(game_state, self.idx)

    def refresh_game_actions(self):
        self.game_actions = GameActions(self.dialogue.send("ACTIONS"))

    def init_vehicles(self):
        self.vehicles_list = [VehicleFactory.build(our_vehicle) for our_vehicle in self.game_state.our_tanks.items()]

    def init_game(self):
        self.dialogue.start_dialogue()
        login_answer = self.dialogue.send("LOGIN", self.login_data)
        self.idx = login_answer["idx"]
        self.refresh_game_state(self.dialogue.send("GAME_STATE"))
        self.map = GameMap(self.dialogue.send("MAP"))
        self.init_vehicles()
        self.game_state_updated.emit(self.map, self.game_state)


if __name__ == "__main__":
    pass
