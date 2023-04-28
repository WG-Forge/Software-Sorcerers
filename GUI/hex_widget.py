"""
This module contains Hex Widget class that is used by
main window to display map cells
"""
import math
from functools import lru_cache
from typing import Generator

from PySide6 import QtWidgets, QtGui, QtCore

import GUI.ui as ui


class Hex(QtWidgets.QWidget):
    """
    Hexagonal Widget class used to display map cells in main window
    """

    def __init__(self, hex_outer_radius, color, text="", parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.pen = QtGui.QPen(QtGui.QColor(*ui.HEX_BORDER_COLOR))
        self.pen.setWidth(ui.HEX_BORDER_WEIGHT)
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
        return (
            (
                width / 2 + radius * math.cos(math.radians(60 * i)),
                height / 2 + radius * math.sin(math.radians(60 * i)),
            )
            for i in range(6)
        )

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
