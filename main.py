"""
This module is an entry point to the app.
"""
from PySide6 import QtWidgets

from GUI.main_window import Window

login_data = {
    "name": "Sorcerer1",
    "password": "my_pass",
    "game": "my_game",
    "num_turns": 45,
    "num_players": 1,
    "is_observer": False,
}

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = Window(login_data)
    window.show()
    app.exec()
