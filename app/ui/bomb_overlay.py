from __future__ import annotations

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter


class BombOverlay:
    def __init__(self) -> None:
        self._dragging = False
        self._position: QPointF | None = None

    def home(self) -> QPointF:
        return QPointF(40, 40)

    def is_dragging(self) -> bool:
        return self._dragging

    def current(self) -> QPointF:
        return self._position or self.home()

    def hit_test(self, point: QPointF, radius: float = 24.0) -> bool:
        return (point - self.current()).manhattanLength() <= radius

    def begin_drag(self, point: QPointF) -> None:
        self._dragging = True
        self._position = point

    def update_drag(self, point: QPointF) -> None:
        self._position = point

    def end_drag(self) -> None:
        self._dragging = False
        self._position = None

    def paint(self, painter: QPainter) -> None:
        center = self.current()
        painter.save()
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.black)
        painter.drawEllipse(center, 14, 14)
        fuse = QPointF(center.x() + 10.0, center.y() - 10.0)
        start = QPointF(center.x() + 8.0, center.y() - 8.0)
        painter.drawLine(start, fuse)
        painter.setBrush(Qt.GlobalColor.yellow)
        painter.drawEllipse(fuse, 4, 4)
        painter.restore()
