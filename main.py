"""
This module is an entry point to the app.
"""
from PySide6 import QtWidgets

from GUI.main_window import Window

login_data = {
    "name": "Sorcerer",
    "password": "42",
    "game": "test_122",
    "num_turns": 45,
    "num_players": 3,
    "is_observer": False,
}

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = Window(login_data)
    window.show()
    app.exec()
