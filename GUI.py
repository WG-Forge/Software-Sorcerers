from functools import cache
import math

from PySide6 import QtWidgets, QtGui, QtCore

from model import GameMap, GameState
from presenter import Presenter
from config import ui as ucf

"""
"""


class Window(QtWidgets.QMainWindow):
    def __init__(self, login_data, parent=None):
        super().__init__(parent)
        self.controllerThread = Presenter(login_data)
        self.controllerThread.start()
        self.screen = QtWidgets.QApplication.screenAt(self.pos())
        self.setGeometry(0, 0, self.screen.size().width()//2, self.screen.size().height()//1.1)
        self.setFixedSize(self.size())
        self.hex_outer_radius = None
        self.init_signals()

    def get_mid_map(self):
        mid_x = self.size().width() / 2
        mid_y = self.size().height() / 2.2
        return mid_x, mid_y

    def init_signals(self):
        self.controllerThread.game_state_updated.connect(self.refresh_map)
        self.controllerThread.game_ended.connect(self.show_message)

    def set_hex_radius(self, map_size):
        self.hex_outer_radius = min(self.size().height() / (4 * map_size), self.size().height() / (4 * map_size))

    @staticmethod
    def hex_to_pixel(size: int, cell: tuple[int, int, int]):
        x = size * (3 / 2 * cell[0])
        y = size * (math.sqrt(3) / 2 * cell[0] + math.sqrt(3) * cell[1])
        return x, y

    def refresh_map(self, map_: "GameMap", state: "GameState"):
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
                text = state.our_tanks[tank_id].hp
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
            x, y = self.hex_to_pixel(self.hex_outer_radius, cell)
            hex_.move(self.get_mid_map()[0] + x, self.get_mid_map()[1] + y)
            hex_.show()

    def show_message(self, text):
        message = QtWidgets.QMessageBox(text=text, parent=self)
        message.show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.controllerThread.exit()


class Hex(QtWidgets.QWidget):
    def __init__(self, hex_outer_radius, color, text="", parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.pen = QtGui.QPen(QtGui.QColor(*ucf.HEX_BORDER_COLOR))
        self.pen.setWidth(ucf.HEX_BORDER_WEIGHT)
        self.brush = QtGui.QBrush(QtGui.QColor(*self.color))
        self.polygon = self.create_hex(hex_outer_radius)

    @cache
    def create_hex(self, radius):
        polygon = QtGui.QPolygonF()
        for point in self.get_hex_points(radius):
            polygon.append(QtCore.QPointF(*point))
        return polygon

    @staticmethod
    def get_hex_points(radius: float):
        width = radius * 2
        height = math.sqrt(3) * radius
        return ((width / 2 + radius * math.cos(math.radians(60 * i)),
                 height / 2 + radius * math.sin(math.radians(60 * i))) for i in range(6))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
        painter.drawText(12, 12, f"{self.text}")
        painter.end()


if __name__ == "__main__":
    login_data_2 = {
        "name": "Sorcerer2",
        "password": "36",
        "game": "my2",
        "num_turns": 45,
        "num_players": 2,
        "is_observer": False
    }
    player2 = Presenter(login_data_2)
    player2.start()
    login_data_1 = {
        "name": "Sorcerer1",
        "password": "36",
        "game": "my2",
        "num_turns": 45,
        "num_players": 2,
        "is_observer": False
    }
    app = QtWidgets.QApplication()
    window = Window(login_data_1)
    window.show()
    app.exec()
