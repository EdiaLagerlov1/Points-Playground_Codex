from __future__ import annotations

import math

from PyQt6.QtCore import QPointF

from app.models import Vector2


def origin(width: int, height: int) -> QPointF:
    return QPointF(width / 2, height / 2)


def to_world(point: QPointF, origin_point: QPointF) -> Vector2:
    return point.x() - origin_point.x(), origin_point.y() - point.y()


def to_screen(position: Vector2, origin_point: QPointF) -> QPointF:
    return QPointF(origin_point.x() + position[0], origin_point.y() - position[1])


def distance(a: Vector2, b: Vector2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])
