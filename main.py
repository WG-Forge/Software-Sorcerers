"""
This module is an entry point to the app.
"""
from PySide6 import QtWidgets

from GUI.login_window import LoginWindow


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = LoginWindow()
    window.show()
    app.exec()
