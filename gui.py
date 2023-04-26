"""
This module contains implementation of graphical user interface, using PySide6

"""
from functools import lru_cache
from typing import Generator
import math

from PySide6 import QtWidgets, QtGui, QtCore

from model import GameMap, GameState
from presenter import Presenter
from config import ui as ucf
from coordinates import Coordinates


class Window(QtWidgets.QMainWindow):
    """
    Main window of user interface
    """
    def __init__(self, login_data, parent=None):
        super().__init__(parent)
        self.presenter_thread = Presenter(login_data)
        self.presenter_thread.start()
        self.screen = QtWidgets.QApplication.screenAt(self.pos())
        self.setGeometry(0, 0, self.screen.size().width()//2, self.screen.size().height()//1.1)
        self.setFixedSize(self.size())
        self.hex_outer_radius = None
        self.init_signals()

    def get_mid_map(self) -> tuple[int, int]:
        """
        Give point to place central cell widget of map
        :return: pixels x, y
        """
        mid_x = self.size().width() // 2
        mid_y = self.size().height() // 2.2
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
        self.hex_outer_radius =\
            min(self.size().height() / (4 * map_size), self.size().height() / (4 * map_size))

    def hex_to_pixel(self, cell: Coordinates) -> tuple[int, int]:
        """
        Calculates axis shift in pixels of each Hex Widget dependent on
        coordinates relative to central Hex Widget
        :param cell: Coordinates obj
        :return: pixels shift (x, y)
        """
        shift_x = self.hex_outer_radius * (3 / 2 * cell[0])
        shift_y = self.hex_outer_radius * (math.sqrt(3) / 2 * cell[0] + math.sqrt(3) * cell[1])
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
            color = ucf.HEX_DEFAULT_FILL
            if cell in map_.obstacles:
                color = ucf.OBSTACLE_COLOR
            elif cell in state.get_our_tanks_cells():
                color = ucf.OUR_TANKS_COLOR
                tank_id = state.get_our_tank_id(cell)
                text = state.our_tanks[tank_id].health
            elif cell in state.enemy_tanks:
                color = ucf.ENEMY_COLOR
                text = state.enemy_tanks[cell]
            elif cell in map_.base:
                color = ucf.BASE_COLOR
            elif cell in map_.spawn_points:
                color = ucf.SPAWN_COLOR
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


class Hex(QtWidgets.QWidget):
    """
    Hexagonal Widget class used to display map cells in main window
    """
    def __init__(self, hex_outer_radius, color, text="", parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.pen = QtGui.QPen(QtGui.QColor(*ucf.HEX_BORDER_COLOR))
        self.pen.setWidth(ucf.HEX_BORDER_WEIGHT)
        self.brush = QtGui.QBrush(QtGui.QColor(*self.color))
        self.polygon = self.create_hex(hex_outer_radius)

    @lru_cache(1)
    def create_hex(self, radius: float) -> QtGui.QPolygonF:
        """
        Creates PySide QPolygonF obj of hexagon inscribed in a circle of given radius
        :param radius: circumscribed circle radius
        :return: PySide QPolygonF obj
        """
        polygon = QtGui.QPolygonF()
        for point in self.get_hex_points(radius):
            polygon.append(QtCore.QPointF(*point))
        return polygon

    @staticmethod
    def get_hex_points(radius: float) -> Generator:
        """
        Creates generator of vertex coordinates in pixels relative
        to center of hexagon inscribed in a circle of given radius
        :param radius: circumscribed circle radius
        :return: Generator
        """
        width = radius * 2
        height = math.sqrt(3) * radius
        return ((width / 2 + radius * math.cos(math.radians(60 * i)),
                 height / 2 + radius * math.sin(math.radians(60 * i))) for i in range(6))

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Paint event handler
        :param event: system generated event
        :return: None
        """
        painter = QtGui.QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
        painter.drawText(12, 12, f"{self.text}")
        painter.end()


if __name__ == "__main__":
    login_data_1 = {
        "name": "Sorcerer1",
        "password": "36",
        "game": "my2121",
        "num_turns": 45,
        "num_players": 1,
        "is_observer": False
    }
    app = QtWidgets.QApplication()
    window = Window(login_data_1)
    window.show()
    app.exec()
