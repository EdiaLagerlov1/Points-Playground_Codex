from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

from app.models import Point, Vector2


def run_kmeans(
    points: Sequence[Point],
    initial_centers: Sequence[Vector2] | None = None,
    max_iterations: int = 30,
    epsilon: float = 1.0,
) -> Tuple[List[Vector2], Dict[str, int], float]:
    if len(points) < 3:
        raise ValueError("K-means requires at least three points.")
    centers = list(initial_centers) if initial_centers else _default_centers(points)
    assignments: Dict[str, int] = {}
    for _ in range(max_iterations):
        changed = _assign_points(points, centers, assignments)
        new_centers = _recenter(points, assignments, len(centers))
        shift = _total_shift(centers, new_centers)
        centers = new_centers
        if not changed or shift < epsilon:
            break
    score = _total_within_variance(points, centers, assignments)
    return centers, assignments, score


def _default_centers(points: Sequence[Point]) -> List[Vector2]:
    unique = list({point.id: point for point in points}.values())
    if len(unique) < 3:
        raise ValueError("Insufficient unique points for centers.")
    return [unique[i].position for i in range(3)]


def _assign_points(
    points: Sequence[Point],
    centers: Sequence[Vector2],
    assignments: Dict[str, int],
) -> bool:
    changed = False
    for point in points:
        index = _closest_center(point.position, centers)
        if assignments.get(point.id) != index:
            assignments[point.id] = index
            changed = True
    return changed


def _recenter(
    points: Sequence[Point],
    assignments: Dict[str, int],
    center_count: int,
) -> List[Vector2]:
    totals = [(0.0, 0.0, 0) for _ in range(center_count)]
    for point in points:
        index = assignments.get(point.id, 0)
        total_x, total_y, total_count = totals[index]
        totals[index] = (
            total_x + point.position[0],
            total_y + point.position[1],
            total_count + 1,
        )
    new_centers: List[Vector2] = []
    for total_x, total_y, total_count in totals:
        if total_count == 0:
            new_centers.append((0.0, 0.0))
        else:
            new_centers.append((total_x / total_count, total_y / total_count))
    return new_centers


def _closest_center(point: Vector2, centers: Sequence[Vector2]) -> int:
    distances = [
        (index, _distance_squared(point, center)) for index, center in enumerate(centers)
    ]
    return min(distances, key=lambda item: item[1])[0]


def _distance_squared(a: Vector2, b: Vector2) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _total_shift(previous: Sequence[Vector2], current: Sequence[Vector2]) -> float:
    total = 0.0
    for before, after in zip(previous, current):
        total += math.sqrt(_distance_squared(before, after))
    return total


def _total_within_variance(
    points: Sequence[Point], centers: Sequence[Vector2], assignments: Dict[str, int]
) -> float:
    total = 0.0
    for point in points:
        center = centers[assignments.get(point.id, 0)]
        total += _distance_squared(point.position, center)
    return total
