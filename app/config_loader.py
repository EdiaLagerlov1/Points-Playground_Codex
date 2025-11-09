from __future__ import annotations

import json
from pathlib import Path
from random import Random
from typing import List, Tuple

from app.logic.sampling import ParameterBounds, create_group
from app.models import Group, Vector2


def load_configuration(
    path: Path,
    rng: Random,
) -> Tuple[List[Group], ParameterBounds, float]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    bounds = _parse_bounds(data)
    circle_radius = float(data.get("circle_radius", 120.0))
    groups = [_build_group(entry, rng) for entry in data.get("groups", [])]
    return groups, bounds, circle_radius


def _parse_bounds(data: dict) -> ParameterBounds:
    mean_bounds = data.get("mean_bounds", {})
    variance_bounds = data.get("variance_bounds", {})
    return ParameterBounds(
        mean_min=_parse_vector(mean_bounds.get("min", [-200.0, -200.0])),
        mean_max=_parse_vector(mean_bounds.get("max", [200.0, 200.0])),
        variance_min=_parse_vector(variance_bounds.get("min", [900.0, 900.0])),
        variance_max=_parse_vector(variance_bounds.get("max", [2500.0, 2500.0])),
    )


def _build_group(entry: dict, rng: Random) -> Group:
    group_id = entry["id"]
    color = entry["color"]
    mean = _parse_vector(entry["mean"])
    variance = _parse_vector(entry["variance"])
    return create_group(group_id, color, mean, variance, rng)


def _parse_vector(source) -> Vector2:
    x, y = source
    return float(x), float(y)
