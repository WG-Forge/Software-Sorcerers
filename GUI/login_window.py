"""
This module contains LoginWindow that
is called on the starting of the app
"""
import random
from copy import deepcopy
from typing import Optional

from PySide6 import QtWidgets

from logic.game import Game
from GUI import ui
from GUI.main_window import Window
from config.config import DEFAULT_LOGIN


class LoginWindow(QtWidgets.QWidget):
    """
    Class that represents login dialogue window
    it contains fields to input login data.
    Default se
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_login = DEFAULT_LOGIN
        self.login_data: Optional[dict] = None
        self.threads: list[Game] = []

        self.init_UI()
        self.init_signals()

    def init_UI(self) -> None:
        """
        UI initialisation, didn't use designer here, because
        it may be harder to maintain
        :return:
        """
        main_layout = QtWidgets.QVBoxLayout()

        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Name:")
        name_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.name_input = QtWidgets.QLineEdit(self.default_login["name"])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)

        password_layout = QtWidgets.QHBoxLayout()
        password_label = QtWidgets.QLabel("Password:")
        password_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.password_input = QtWidgets.QLineEdit(self.default_login["password"])
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        game_layout = QtWidgets.QHBoxLayout()
        game_label = QtWidgets.QLabel("Game:")
        game_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.game_input = QtWidgets.QLineEdit(self.default_login["game"])
        game_layout.addWidget(game_label)
        game_layout.addWidget(self.game_input)

        num_turns_layout = QtWidgets.QHBoxLayout()
        num_turns_label = QtWidgets.QLabel("Number of turns:")
        num_turns_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.num_turns_input = QtWidgets.QSpinBox()
        self.num_turns_input.setValue(self.default_login["num_turns"])
        num_turns_layout.addWidget(num_turns_label)
        num_turns_layout.addWidget(self.num_turns_input)

        num_players_layout = QtWidgets.QHBoxLayout()
        num_players_label = QtWidgets.QLabel("Number of players")
        num_players_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.num_players_input = QtWidgets.QSpinBox()
        self.num_players_input.setRange(1, 3)
        num_players_layout.addWidget(num_players_label)
        num_players_layout.addWidget(self.num_players_input)

        is_full_layout = QtWidgets.QHBoxLayout()
        is_full_label = QtWidgets.QLabel("Full game?")
        is_full_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.is_full_input = QtWidgets.QCheckBox()
        is_full_layout.addWidget(is_full_label)
        is_full_layout.addWidget(self.is_full_input)

        is_test_layout = QtWidgets.QHBoxLayout()
        is_test_label = QtWidgets.QLabel("Run test multiplayer?")
        is_test_label.setFixedWidth(ui.LOGIN_LABEL_WIDTH)
        self.is_test_input = QtWidgets.QCheckBox()
        is_test_layout.addWidget(is_test_label)
        is_test_layout.addWidget(self.is_test_input)

        main_layout.addLayout(name_layout)
        main_layout.addLayout(password_layout)
        main_layout.addLayout(game_layout)
        main_layout.addLayout(num_turns_layout)
        main_layout.addLayout(num_players_layout)
        main_layout.addLayout(is_full_layout)
        main_layout.addLayout(is_test_layout)

        self.start_button = QtWidgets.QPushButton("Start game!")
        main_layout.addWidget(self.start_button)

        self.setLayout(main_layout)

    def init_signals(self) -> None:
        """
        Initiate signals
        :return: None
        """
        self.start_button.clicked.connect(self.start_game)
        self.is_test_input.stateChanged.connect(self.block_input)

    def block_input(self) -> None:
        """
        Signal connected to CheckBox that asks about multiplayer
        test mode, if mode selected - data in blocked fields will be
        generated automatically in init_test_login method
        :return:
        """
        if self.is_test_input.isChecked():
            self.num_players_input.setValue(3)
            self.num_players_input.setEnabled(False)
            self.name_input.setEnabled(False)
            self.game_input.setEnabled(False)
        else:
            self.num_players_input.setEnabled(True)
            self.name_input.setEnabled(True)
            self.game_input.setEnabled(True)

    def init_login_data(self) -> None:
        """
        sets login data according to user input in login form
        :return: None
        """
        self.login_data = {
            "name": self.name_input.text(),
            "password": self.password_input.text(),
            "game": self.game_input.text(),
            "num_turns": self.num_turns_input.value(),
            "num_players": self.num_players_input.value(),
            "is_observer": False,
            "is_full": self.is_full_input.isChecked(),
        }

    def start_game(self) -> None:
        """
        Takes user data using init_login_data, instantiates
        main window with given login_data, if multiplayer test
        mod selected - calls init_test_login to create additional bots
        :return: None
        """
        self.init_login_data()

        if self.is_test_input.isChecked():
            self.init_test_login()

        self.main_window = Window(self.login_data, parent=None)
        self.main_window.closed.connect(self.on_close_main_widget)
        self.main_window.show()
        self.start_button.setEnabled(False)

    def init_test_login(self) -> None:
        """
        Generates random login data if multiplayer test
        mod selected, runs additional bots in threads
        :return: None
        """
        self.login_data["name"] = f"{random.random()}"
        self.login_data["game"] = f"{random.random()}"
        login_data2 = deepcopy(self.login_data)
        login_data3 = deepcopy(self.login_data)
        login_data2["name"] += "1"
        login_data3["name"] += "2"
        self.threads.append(Game(login_data2))
        self.threads.append(Game(login_data3))
        for thread in self.threads:
            thread.start()

    def on_close_main_widget(self) -> None:
        """
        Slot connected to signal emitted by main_window
        when it is closed, it stops all bot_threads if
        they exist, and sets start_button enabled
        :return: None
        """
        for thread in self.threads:
            thread.exit()
        self.threads = []
        self.start_button.setEnabled(True)
