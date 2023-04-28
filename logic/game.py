"""
This module contains Game thread class - mediator that contains main game loop
"""
from copy import deepcopy

from PySide6 import QtCore

from config.config import Actions
from connection import Connection
from logic.model import GameState, GameMap, GameActions
from logic.vehicle import Vehicle


class Game(QtCore.QThread):
    """
    Mediator class that contains main game loop,
    runs as a thread called from main window
    """

    game_state_updated = QtCore.Signal(object, object)
    game_ended = QtCore.Signal(str)

    def __init__(self, login_data: dict):
        super().__init__(None)
        self.idx = None
        self.login_data = login_data
        self.connection = Connection()
        self.vehicles_list = []
        self.game_state = None
        self.game_actions = None
        self.map = None

    def run(self) -> None:
        """
        inherited from QTread method that begins execute when thread started
        executes game initialisation, runs main game loop, emits signals
        used to update main window
        :return: None
        """
        turn = None
        winner = None
        self.init_game()
        # <---------------------- main loop ---------------------
        while True:
            current_game_state = self.connection.send(Actions.GAME_STATE)
            if current_game_state["finished"]:
                winner = current_game_state["winner"]
                break
            if current_game_state["current_turn"] != turn:
                turn = current_game_state["current_turn"]
                self.refresh_game_state(current_game_state)
                self.game_state_updated.emit(self.map, deepcopy(self.game_state))
            if current_game_state["current_player_idx"] != self.idx:
                self.connection.send(Actions.TURN)
                continue
            for vehicle in self.vehicles_list:
                vehicle_turn = vehicle.make_turn(self.game_state, self.map)
                if vehicle_turn:
                    self.game_state.update_data(vehicle_turn)
                    self.connection.send(*vehicle_turn)
            self.connection.send(Actions.TURN)
        # <-------------------- end of main loop ----------------

        self.game_ended.emit(f"Game ended, winner: {winner}")
        self.connection.send(Actions.LOGOUT)
        self.quit()

    def refresh_game_state(self, game_state: dict) -> None:
        """
        Method that creates GameState obj from GAME_STATE dict response,
        and refreshes self.game_state
        :param game_state: GAME_STATE dict response
        :return: None
        """
        self.game_state = GameState(game_state, self.idx)

    def refresh_game_actions(self) -> None:
        """
        Method that creates GameActions obj from GAME_ACTIONS dict response,
        and refreshes self.game_actions
        :return: None
        """
        self.game_actions = GameActions(self.connection.send(Actions.GAME_ACTIONS))

    def init_vehicles(self) -> None:
        """
        Instantiates vehicles at the beginning of the game according
        to game_state, add them into list in the order of their turn
        :return: None
        """
        for t_id, spec in self.game_state.get_ordered_tanks().items():
            self.vehicles_list.append(Vehicle.build(t_id, spec))

    def init_game(self) -> None:
        """
        Provides such actions at the beginning of the game: starts connection,
        login, defines player id using login response, calls first refreshing
        of game_state, instantiates GameMap obj using GAME_MAP response,
        call players vehicle instantiation, emit signal for first main window
        update
        :return: None
        """
        self.connection.init_connection()
        login_answer = self.connection.send(Actions.LOGIN, self.login_data)
        self.idx = login_answer["idx"]
        self.refresh_game_state(self.connection.send(Actions.GAME_STATE))
        self.map = GameMap(self.connection.send(Actions.MAP))
        self.init_vehicles()
        self.game_state_updated.emit(self.map, self.game_state)
