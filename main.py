"""
This module is an entry point to the app.
"""
from PySide6 import QtWidgets

from GUI.main_window import Window
from logic.game import Game

login_data_1 = {
        "name": "Sorcerer1",
        "password": "36",
        "game": "my2121",
        "num_turns": 45,
        "num_players": 3,
        "is_observer": False
    }

login_data_2 = {
        "name": "Sorcerer2",
        "password": "36",
        "game": "my2121",
        "num_turns": 45,
        "num_players": 3,
        "is_observer": False
    }

login_data_3 = {
        "name": "Sorcerer3",
        "password": "36",
        "game": "my2121",
        "num_turns": 45,
        "num_players": 3,
        "is_observer": False
    }

if __name__ == "__main__":
    player2 = Game(login_data_2)
    player2.start()
    player3 = Game(login_data_3)
    player3.start()
    app = QtWidgets.QApplication()
    window = Window(login_data_1)
    window.show()
    app.exec()
