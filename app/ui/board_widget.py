from __future__ import annotations
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget
from app.models import AppState, Group, Vector2
from app.ui import coordinates
from app.ui.bomb_overlay import BombOverlay
from app.ui.draw_helpers import draw_groups, draw_pending, radius_for_group
from app.ui.score_overlay import ScoreOverlay


class BoardWidget(QWidget):
    def __init__(
        self,
        state_provider: Callable[[], AppState],
        move_group: Callable[[str, Vector2], None],
        explode_group: Callable[[str], None],
        circle_radius: float,
    ) -> None:
        super().__init__()
        self._state_provider = state_provider; self._move_group = move_group; self._explode_group = explode_group
        self._circle_radius = circle_radius
        self._dragging_id: str | None = None; self._last_world: Vector2 | None = None
        self._bomb = BombOverlay(); self._score = ScoreOverlay()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        origin = coordinates.origin(self.width(), self.height())
        to_screen = lambda pos: coordinates.to_screen(pos, origin)
        groups = self._state_provider().groups; radii = {group.id: radius_for_group(group) for group in groups}
        draw_groups(painter, groups, lambda group: radii[group.id], to_screen)
        draw_pending(painter, self._state_provider().pending_kmeans, groups, radii, to_screen)
        self._bomb.paint(painter); self._score.paint(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._bomb.hit_test(event.position()):
                self._bomb.begin_drag(event.position())
                self.update()
                event.accept()
                return
            world = self._to_world(event.position())
            group = self._hit_group_center(world)
            if group:
                self._dragging_id = group.id
                self._last_world = world
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._bomb.is_dragging():
            self._bomb.update_drag(event.position())
            self.update()
            event.accept()
            return
        if self._dragging_id and event.buttons() & Qt.MouseButton.LeftButton:
            world = self._to_world(event.position())
            if self._last_world:
                delta = (world[0] - self._last_world[0], world[1] - self._last_world[1])
                if delta != (0.0, 0.0):
                    self._move_group(self._dragging_id, delta)
                    self.update()
            self._last_world = world
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._bomb.is_dragging():
                self._handle_bomb_drop(event.position())
                self._bomb.end_drag()
                self.update()
                event.accept()
                return
            self._dragging_id = None; self._last_world = None
        super().mouseReleaseEvent(event)

    def _handle_bomb_drop(self, position) -> None:
        for group in self._state_provider().groups:
            if (self._to_screen(group.center_position) - position).manhattanLength() <= 24:
                self._explode_group(group.id)
                break

    def _hit_group_center(self, world: Vector2) -> Group | None:
        for group in self._state_provider().groups:
            if coordinates.distance(world, group.center_position) <= 18.0:
                return group
        return None

    def _to_world(self, point) -> Vector2:
        return coordinates.to_world(point, coordinates.origin(self.width(), self.height()))

    def _to_screen(self, position: Vector2):
        return coordinates.to_screen(position, coordinates.origin(self.width(), self.height()))

    def set_score_text(self, text: str | None) -> None:
        self._score.set_text(text); self.update()
