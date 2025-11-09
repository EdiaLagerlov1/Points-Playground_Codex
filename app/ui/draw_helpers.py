from __future__ import annotations

import math
from typing import Callable, Iterable, Mapping, Sequence

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen

from app.models import Group, Point, Vector2


def radius_for_group(
    group: Group, padding: float = 20.0, minimum: float = 40.0
) -> float:
    if not group.points:
        return max(minimum, padding)
    max_distance = max(
        math.hypot(
            point.position[0] - group.center_position[0],
            point.position[1] - group.center_position[1],
        )
        for point in group.points
    )
    return max(max_distance + padding, minimum)


def draw_groups(
    painter: QPainter,
    groups: Sequence[Group],
    radius_provider: Callable[[Group], float],
    to_screen: Callable[[Vector2], QPointF],
) -> None:
    for group in groups:
        radius = radius_provider(group)
        _draw_group(painter, group, radius, to_screen)


def draw_pending(
    painter: QPainter,
    centers: Iterable[Vector2],
    groups: Sequence[Group],
    radii: Mapping[str, float],
    to_screen: Callable[[Vector2], QPointF],
) -> None:
    centers = list(centers)
    if not centers:
        return
    for group, center in zip(groups, centers):
        screen = to_screen(center)
        radius = radii.get(group.id, 60.0)
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(screen, radius, radius)
        painter.setBrush(QColor(group.color))
        painter.setPen(Qt.GlobalColor.black)
        painter.drawEllipse(screen, 9, 9)


def _draw_group(
    painter: QPainter,
    group: Group,
    circle_radius: float,
    to_screen: Callable[[Vector2], QPointF],
) -> None:
    center = to_screen(group.center_position)
    color = QColor(group.color)
    pen = QPen(color)
    pen.setWidth(3)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, circle_radius, circle_radius)
    painter.setBrush(color)
    painter.drawEllipse(center, 12, 12)
    painter.setPen(Qt.GlobalColor.black)
    painter.drawText(center + QPointF(14, 4), group.id.capitalize())
    for point in group.points:
        _draw_point(painter, point, color, to_screen)


def _draw_point(
    painter: QPainter,
    point: Point,
    color: QColor,
    to_screen: Callable[[Vector2], QPointF],
) -> None:
    center = to_screen(point.position)
    radius = 6 if point.is_overlap else 5
    painter.setBrush(color)
    painter.setPen(Qt.GlobalColor.black if point.is_overlap else color)
    painter.drawEllipse(center, radius, radius)
