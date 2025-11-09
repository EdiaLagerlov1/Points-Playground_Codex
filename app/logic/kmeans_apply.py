from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Sequence

from app.models import Group, Point, Vector2


def apply_assignments(
    groups: Sequence[Group],
    centers: Sequence[Vector2],
    assignments: Dict[str, int],
) -> List[Group]:
    grouped = _group_points(groups, assignments, len(centers))
    updated: List[Group] = []
    for index, group in enumerate(groups):
        points = grouped.get(index, [])
        if points:
            center = centers[index]
            updated.append(
                replace(
                    group,
                    mean=center,
                    variance=_variance(center, points),
                    center_position=center,
                    points=points,
                )
            )
        else:
            updated.append(group)
    return updated


def _group_points(
    groups: Sequence[Group], assignments: Dict[str, int], count: int
) -> Dict[int, List[Point]]:
    grouped: Dict[int, List[Point]] = {index: [] for index in range(count)}
    for group in groups:
        for point in group.points:
            index = assignments.get(point.id, 0)
            grouped[index].append(point)
    return grouped


def _variance(center: Vector2, points: Sequence[Point]) -> Vector2:
    length = float(len(points))
    return (
        sum((point.position[0] - center[0]) ** 2 for point in points) / length,
        sum((point.position[1] - center[1]) ** 2 for point in points) / length,
    )
