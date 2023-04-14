import math

from PySide6 import QtWidgets, QtGui, QtCore

from Model import GameMap, GameState
import cube_math as cm
from main import Controller

login_data_1 = {
    "name": "Sorcerer",
    "password": "123",
    "game": "mygame125",
    "num_turns": 45,
    "num_players": 1,
    "is_observer": False
}

HEX_BORDER_COLOR = (0, 0, 0)
HEX_BORDER_WEIGHT = 2
HEX_DEFAULT_FILL = (200, 200, 200)
OBSTACLE_COLOR = (64, 64, 64)
BASE_COLOR = (255, 204, 153)
OUR_TANKS_COLOR = (178, 255, 102)
ENEMY_COLOR = (255, 102, 102)

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

# <--------- for testing ------
        self.initThreads()
# <--------------end -----------
        self.screen = QtWidgets.QApplication.screenAt(self.pos())
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.hex_outer_radius = None
        self.initSignals()

    def getMidMap(self):
        mid_x = self.screen.size().width() / 2
        mid_y = self.screen.size().height() / 2.2
        return mid_x, mid_y

    def initThreads(self):
        self.controllerThread = Controller(login_data_1)
        self.controllerThread.start()

    def initSignals(self):
        self.controllerThread.game_state_updated.connect(self.refreshMap)

    def refreshMap(self, map_: "GameMap", state: "GameState"):
        self.hex_outer_radius = self.size().height() / (4 * map_.size)
        for cell in map_.cells:
            text = ""
            color = HEX_DEFAULT_FILL
            if cell in map_.obstacles:
                color = OBSTACLE_COLOR
            elif cell in state.get_our_tanks_cells():
                color = OUR_TANKS_COLOR
                tank_id = state.get_our_tank_id(cell)
                text = state.our_tanks[tank_id].hp
            elif cell in state.get_enemy_cells():
                color = ENEMY_COLOR
                text = state.enemy_tanks[cell]
            elif cell in map_.base:
                color = BASE_COLOR
            hex_ = Hex(self.hex_outer_radius, color, text)
            hex_.setParent(self)
            x, y = cm.hex_to_pixel(self.hex_outer_radius, cell)
            hex_.move(self.getMidMap()[0] + x, self.getMidMap()[1] + y)
            hex_.show()


class Hex(QtWidgets.QWidget):
    def __init__(self, hex_outer_radius, color, text="", parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.pen = QtGui.QPen(QtGui.QColor(*HEX_BORDER_COLOR))
        self.pen.setWidth(HEX_BORDER_WEIGHT)
        self.brush = QtGui.QBrush(QtGui.QColor(*self.color))
        self.width = hex_outer_radius * 2
        self.height = math.sqrt(3) * hex_outer_radius
        self.polygon = self.createHex(hex_outer_radius)


    def createHex(self, r):
        polygon = QtGui.QPolygonF()
        W = 60
        for i in range(6):
            t = W * i
            x = r * math.cos(math.radians(t))
            y = r * math.sin(math.radians(t))
            polygon.append(QtCore.QPointF(self.width / 2 + x, self.height / 2 + y))
        return polygon

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
        painter.drawText(12, 12, f"{self.text}")
        painter.end()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = Window()
    window.show()
    app.exec()

