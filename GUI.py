import math

from PySide6 import QtWidgets, QtGui, QtCore

from model import GameMap, GameState
import cube_math as cm
from presenter import Presenter
import config as cf


class Window(QtWidgets.QMainWindow):
    def __init__(self, login_data, parent=None):
        super().__init__(parent)
        self.initThreads(login_data)
        self.screen = QtWidgets.QApplication.screenAt(self.pos())
        self.setGeometry(0, 0, self.screen.size().width()//2, self.screen.size().height())
        self.hex_outer_radius = None
        self.initSignals()

    def getMidMap(self):
        mid_x = self.size().width() / 2
        mid_y = self.size().height() / 2.2
        return mid_x, mid_y

    def initThreads(self, login_data):
        self.controllerThread = Presenter(login_data)
        self.controllerThread.start()

    def initSignals(self):
        self.controllerThread.game_state_updated.connect(self.refreshMap)
        self.controllerThread.game_ended.connect(self.showMessage)

    def refreshMap(self, map_: "GameMap", state: "GameState"):
        self.hex_outer_radius = min(self.size().height() / (4 * map_.size), self.size().height() / (4 * map_.size))
        for cell in map_.cells:
            text = ""
            color = cf.HEX_DEFAULT_FILL
            if cell in map_.obstacles:
                color = cf.OBSTACLE_COLOR
            elif cell in state.get_our_tanks_cells():
                color = cf.OUR_TANKS_COLOR
                tank_id = state.get_our_tank_id(cell)
                text = state.our_tanks[tank_id].hp
            elif cell in state.get_enemy_cells():
                color = cf.ENEMY_COLOR
                text = state.enemy_tanks[cell]
            elif cell in map_.base:
                color = cf.BASE_COLOR
            elif cell in map_.spawn_points:
                color = cf.SPAWN_COLOR
            hex_ = Hex(self.hex_outer_radius, color, text)
            hex_.setParent(self)
            x, y = cm.hex_to_pixel(self.hex_outer_radius, cell)
            hex_.move(self.getMidMap()[0] + x, self.getMidMap()[1] + y)
            hex_.show()

    def showMessage(self, text):
        message = QtWidgets.QMessageBox(text=text, parent=self)
        message.show()

class Hex(QtWidgets.QWidget):
    def __init__(self, hex_outer_radius, color, text="", parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.pen = QtGui.QPen(QtGui.QColor(*cf.HEX_BORDER_COLOR))
        self.pen.setWidth(cf.HEX_BORDER_WEIGHT)
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
    login_data_1 = {
        "name": "Sorcerer",
        "password": "123",
        "game": "mygame125",
        "num_turns": 45,
        "num_players": 1,
        "is_observer": False
    }
    app = QtWidgets.QApplication()
    window = Window(login_data_1)
    window.show()
    app.exec()

