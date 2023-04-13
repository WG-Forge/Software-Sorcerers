import math

from PySide6 import QtWidgets, QtGui, QtCore

from Model import GameMap
import cube_math as cm



HEX_BORDER_COLOR = (0, 0, 0)
HEX_BORDER_WEIGHT = 2
HEX_DEFAULT_FILL = (200, 200, 200)



class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

# <--------- for testing ------
        from Client import Dialogue
        dialogue = Dialogue()
        dialogue.start_dialogue()
        dialogue.send("LOGIN", {"name": "Boris"})
        self.map_ = GameMap(dialogue.send("MAP"))
# <--------------end -----------
        self.screen = QtWidgets.QApplication.screenAt(self.pos())
        self.initUi()



    def initUi(self):
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        #self.mapLayout = QtWidgets.QVBoxLayout()
        #self.mapWidget = QtWidgets.QWidget()
        self.hex_outer_radius = self.screen.size().height()/(4*self.map_.size)
        print(self.hex_outer_radius)
        self.initMap(self.map_)
        #self.mapLayout.addWidget(self.mapWidget)
        #elf.setLayout(self.mapLayout)

    def initMap(self, map_: "GameMap"):
        for cell in map_.cells:
            hex_ = Hex(self.hex_outer_radius)
            hex_.setObjectName(f"{cell}")
            hex_.setParent(self)
            mid_x = self.screen.size().width()/2.1
            mid_y = self.screen.size().height()/2.1
            x, y = cm.hex_to_pixel(self.hex_outer_radius, cell)
            hex_.move(mid_x + x, mid_y + y)
            # hex_.label.setText(f"{cell[0]}{cell[1]}")

class Hex(QtWidgets.QWidget):
    def __init__(self, hex_outer_radius, parent=None):
        super().__init__(parent)
        self.pen = QtGui.QPen(QtGui.QColor(*HEX_BORDER_COLOR))
        self.pen.setWidth(HEX_BORDER_WEIGHT)
        self.brush = QtGui.QBrush(QtGui.QColor(*HEX_DEFAULT_FILL))
        self.polygon = self.createHex(hex_outer_radius)
        # self.cellLayout = QtWidgets.QVBoxLayout()
        # self.label = QtWidgets.QLabel(self)

    def createHex(self, r):
        polygon = QtGui.QPolygonF()
        W = 60
        for i in range(6):
            t = W * i
            x = r * math.cos(math.radians(t))
            y = r * math.sin(math.radians(t))
            polygon.append(QtCore.QPointF(self.width() / 2 + x, self.height() / 2 + y))
        return polygon

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
        font = painter.font()
        font.setFamily('Times')
        font.setPointSize(12)
        painter.setFont(font)
        vmin, value = '1', '2'
        painter.drawText(10, 10, "{}{}".format(vmin, value))
        painter.end()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = Window()
    window.show()
    app.exec()