"""
This module contains Game thread class - mediator that contains main game loop
"""
from copy import deepcopy
from typing import Optional

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

    game_state_updated = QtCore.Signal(GameMap, GameState)
    game_ended = QtCore.Signal(str)
    update = QtCore.Signal(str)

    def __init__(self, login_data: dict):
        super().__init__(None)
        self.idx: Optional[int] = None
        self.login_data = login_data
        self.connection = Connection()
        self.vehicles_list: list[Vehicle] = []
        self.game_state: Optional[GameState] = None
        self.game_actions: Optional[GameActions] = None
        self.map: Optional[GameMap] = None
        self.game_statistic = {"Draws": 0, "Your wins": 0}

    def run(self) -> None:
        """
        inherited from QTread method that begins execute when thread started
        executes game initialisation, runs main game loop, emits signals
        used to update main window
        :return: None
        """
        turn = None
        self.init_game()

        # <---------------------- main loop ---------------------
        while True:
            self.refresh_game_state()
            if self.game_state.is_finished:
                self.update_statistic()
                self.update.emit(str(self.game_statistic))
                if not self.game_state.is_last_round():
                    self.connection.send(Actions.TURN)
                    continue
                break
            if self.game_state.current_turn != turn:
                turn = self.game_state.current_turn
                self.game_state_updated.emit(self.map, deepcopy(self.game_state))
            if self.game_state.current_player != self.idx:
                self.connection.send(Actions.TURN)
                continue
            self.make_turn()
            self.connection.send(Actions.TURN)
        # <-------------------- end of main loop ----------------

        self.game_ended.emit(str(self.game_statistic))
        self.connection.send(Actions.LOGOUT)
        self.connection.close_connection()
        self.quit()

    def refresh_game_state(self) -> None:
        """
        Method that creates GameState obj from GAME_STATE dict response,
        and refreshes self.game_state
        :param game_state: GAME_STATE dict response
        :return: None
        """
        self.game_state = GameState(self.connection.send(Actions.GAME_STATE), self.idx)

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
        for t_id, spec in self.game_state.get_ordered_tanks():
            self.vehicles_list.append(Vehicle.build(t_id, spec))

    def make_turn(self) -> None:
        """
        Asks ours vehicle to make turn in order they were instantiated
        in the beginning of the game
        :return: None
        """
        for vehicle in self.vehicles_list:
            vehicle_turn = vehicle.make_turn(self.game_state, self.map)
            if vehicle_turn:
                self.game_state.update_data(vehicle_turn)
                self.connection.send(*vehicle_turn)

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
        self.refresh_game_state()
        self.map = GameMap(self.connection.send(Actions.MAP))
        self.init_vehicles()

    def update_statistic(self) -> None:
        """
        Keeps win statistics up to date. Game statistics
        is emitted by this thread and used in main window.
        Can be expanded with other info, it will require
        modification of slot that is connected to "update"
        signal in main_window.
        :return: None
        """
        winner = self.game_state.winner
        if winner is None:
            self.game_statistic["Draws"] += 1
        elif winner == self.idx:
            self.game_statistic["Your wins"] += 1
        elif winner in self.game_statistic:
            self.game_statistic[winner] += 1
        else:
            self.game_statistic[winner] = 1
