from __future__ import annotations

import math
from dataclasses import dataclass
from random import Random
from typing import List, Tuple

from app.models import Group, Point, Vector2


@dataclass(frozen=True)
class ParameterBounds:
    mean_min: Vector2
    mean_max: Vector2
    variance_min: Vector2
    variance_max: Vector2


def random_parameters(bounds: ParameterBounds, rng: Random) -> Tuple[Vector2, Vector2]:
    mean = (
        rng.uniform(bounds.mean_min[0], bounds.mean_max[0]),
        rng.uniform(bounds.mean_min[1], bounds.mean_max[1]),
    )
    variance = (
        rng.uniform(bounds.variance_min[0], bounds.variance_max[0]),
        rng.uniform(bounds.variance_min[1], bounds.variance_max[1]),
    )
    return mean, variance


def create_group(
    group_id: str,
    color: str,
    mean: Vector2,
    variance: Vector2,
    rng: Random,
    point_count: int = 10,
) -> Group:
    points = _sample_points(group_id, mean, variance, rng, point_count)
    return Group(
        id=group_id,
        color=color,
        mean=mean,
        variance=variance,
        points=points,
        center_position=mean,
    )


def regenerate_group(group: Group, mean: Vector2, variance: Vector2, rng: Random) -> Group:
    points = _sample_points(group.id, mean, variance, rng, len(group.points))
    return Group(
        id=group.id,
        color=group.color,
        mean=mean,
        variance=variance,
        points=points,
        center_position=mean,
    )


def _sample_points(
    group_id: str, mean: Vector2, variance: Vector2, rng: Random, count: int
) -> List[Point]:
    deviation = (
        math.sqrt(max(variance[0], 1e-6)),
        math.sqrt(max(variance[1], 1e-6)),
    )
    points: List[Point] = []
    for index in range(count):
        x = rng.gauss(mean[0], deviation[0])
        y = rng.gauss(mean[1], deviation[1])
        points.append(
            Point(
                id=f"{group_id}-{index}",
                position=(x, y),
                original_group_id=group_id,
            )
        )
    return points
