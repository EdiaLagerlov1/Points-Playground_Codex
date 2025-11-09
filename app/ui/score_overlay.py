from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter


class ScoreOverlay:
    def __init__(self) -> None:
        self._text: str | None = None

    def set_text(self, text: str | None) -> None:
        self._text = text

    def paint(self, painter: QPainter) -> None:
        if not self._text:
            return
        painter.save()
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(16, 28, self._text)
        painter.restore()
