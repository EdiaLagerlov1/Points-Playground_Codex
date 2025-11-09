from dataclasses import dataclass, field
from typing import List, Tuple

Vector2 = Tuple[float, float]


@dataclass
class Point:
    id: str
    position: Vector2
    original_group_id: str
    is_overlap: bool = False


@dataclass
class Group:
    id: str
    color: str
    mean: Vector2
    variance: Vector2
    points: List[Point] = field(default_factory=list)
    center_position: Vector2 = (0.0, 0.0)


@dataclass
class AppState:
    groups: List[Group]
    active_tool: str = "select"
    pending_kmeans: List[Vector2] = field(default_factory=list)
    seed: int | None = None
