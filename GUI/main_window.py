"""
This module contains implementation of main window, using PySide6

"""
import math

from PySide6 import QtWidgets, QtGui

import GUI.ui as ui
from GUI.hex_widget import Hex
from logic.coordinates import Coordinates
from logic.game import Game
from logic.model import GameMap, GameState


class Window(QtWidgets.QMainWindow):
    """
    Main window of user interface
    """

    def __init__(self, login_data, parent=None):
        super().__init__(parent)
        self.presenter_thread = Game(login_data)
        self.presenter_thread.start()
        self.screen = QtWidgets.QApplication.screenAt(self.pos())
        self.setGeometry(0, 0, self.screen.size().width() // ui.SCREEN_TO_WINDOW_WIDTH_RATIO,
                         self.screen.size().height() // ui.SCREEN_TO_WINDOW_HIGH_RATIO)
        self.setFixedSize(self.size())
        self.hex_outer_radius = None
        self.init_signals()

    def get_mid_map(self) -> tuple[int, int]:
        """
        Give point to place central cell widget of map
        :return: pixels x, y
        """
        mid_x = self.size().width() // 2
        mid_y = self.size().height() // 2.2  # Slightly moved to top
        return mid_x, mid_y

    def init_signals(self) -> None:
        """
        Initiates signals from thread
        :return: None
        """
        self.presenter_thread.game_state_updated.connect(self.refresh_map)
        self.presenter_thread.game_ended.connect(self.show_message)

    def set_hex_radius(self, map_size: int) -> None:
        """
        Set radius of Hex Widgets dependent on window size and map size
        :param map_size: game map size (max coordinate value)
        :return: None
        """
        self.hex_outer_radius = \
            min(self.size().height() / (4 * map_size), self.size().height() / (4 * map_size))

    def hex_to_pixel(self, cell: Coordinates) -> tuple[int, int]:
        """
        Calculates axis shift in pixels of each Hex Widget dependent on
        coordinates relative to central Hex Widget
        :param cell: Coordinates obj
        :return: pixels shift (x, y)
        """
        shift_x = self.hex_outer_radius * (3 / 2 * cell.x)
        shift_y = self.hex_outer_radius * (math.sqrt(3) / 2 * cell.x + math.sqrt(3) * cell.y)
        return shift_x, shift_y

    def refresh_map(self, map_: GameMap, state: GameState) -> None:
        """
        Slot connected to presenter signal game_state_updated.
        Updates widgets in main window dependent on current game content.
        Create child Hex Widgets of proper type, move Widgets to correct pixel.
        Every turn sets parent as None for widgets created on previous turn,
        that decrease reference count of each widget to 0
        :param map_: GameMap obj
        :param state: GameState obj
        :return: None
        """
        if self.hex_outer_radius is None:
            self.set_hex_radius(map_.size)
        for cell in map_.cells:
            existing_cell = self.findChild(Hex, f"{cell}")
            if existing_cell:
                existing_cell.setParent(None)
            text = ""
            color = ui.HEX_DEFAULT_FILL
            if cell in map_.obstacles:
                color = ui.OBSTACLE_COLOR
            elif cell in state.get_our_tanks_cells():
                color = ui.OUR_TANKS_COLOR
                tank_id = state.get_our_tank_id(cell)
                text = state.our_tanks[tank_id].health
            elif cell in state.enemy_tanks:
                color = ui.ENEMY_COLOR
                text = state.enemy_tanks[cell]
            elif cell in map_.base:
                color = ui.BASE_COLOR
            elif cell in map_.spawn_points:
                color = ui.SPAWN_COLOR
            hex_ = Hex(self.hex_outer_radius, color, text)
            hex_.setParent(self)
            hex_.setObjectName(f"{cell}")
            shift_x, shift_y = self.hex_to_pixel(cell)
            hex_.move(self.get_mid_map()[0] + shift_x, self.get_mid_map()[1] + shift_y)
            hex_.show()

    def show_message(self, text: str) -> None:
        """
        Create pop-up message window
        :param text: text to display
        :return: None
        """
        message = QtWidgets.QMessageBox(text=text, parent=self)
        message.show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Close event handler
        :param event: system generated event
        :return: None
        """
        self.presenter_thread.exit()
