from random import Random

from app.logic.overlap_manager import OVERLAP_COUNT, enforce_overlap
from app.models import Group, Point


def build_group(group_id: str) -> Group:
    points = [
        Point(id=f"{group_id}-{index}", position=(index * 10.0, 0.0), original_group_id=group_id)
        for index in range(10)
    ]
    return Group(
        id=group_id,
        color="#000000",
        mean=(0.0, 0.0),
        variance=(1.0, 1.0),
        points=points,
        center_position=(0.0, 0.0),
    )


def test_enforce_overlap_marks_expected_points():
    groups = [build_group("blue"), build_group("green"), build_group("red")]
    enforce_overlap(groups, radius=100.0, rng=Random(42))
    for group in groups:
        overlap_flags = [point.is_overlap for point in group.points[:OVERLAP_COUNT]]
        assert all(overlap_flags)
