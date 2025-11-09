from __future__ import annotations

import math
from random import Random
from typing import Iterable, List, Sequence

from app.models import Group, Point, Vector2

OVERLAP_COUNT = 3


def enforce_overlap(groups: Sequence[Group], radius: float, rng: Random) -> None:
    if not groups:
        return
    center = _compute_overlap_center(groups)
    jitter_radius = radius * 0.3
    for group in groups:
        _mark_overlap_points(group.points, center, jitter_radius, rng)


def _mark_overlap_points(
    points: List[Point], center: Vector2, jitter_radius: float, rng: Random
) -> None:
    for index, point in enumerate(points):
        if index < OVERLAP_COUNT:
            angle = rng.uniform(0.0, 2.0 * math.pi)
            distance = rng.uniform(0.0, jitter_radius)
            point.position = (
                center[0] + math.cos(angle) * distance,
                center[1] + math.sin(angle) * distance,
            )
            point.is_overlap = True
        else:
            point.is_overlap = False


def _compute_overlap_center(groups: Iterable[Group]) -> Vector2:
    total_x = 0.0
    total_y = 0.0
    count = 0
    for group in groups:
        total_x += group.center_position[0]
        total_y += group.center_position[1]
        count += 1
    if count == 0:
        return 0.0, 0.0
    return total_x / count, total_y / count
