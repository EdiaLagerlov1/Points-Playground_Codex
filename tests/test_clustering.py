from app.logic.clustering import run_kmeans
from app.models import Point


def test_kmeans_groups_points_by_proximity():
    points = [
        Point(id="a0", position=(0.1, -0.2), original_group_id="a"),
        Point(id="a1", position=(0.2, 0.3), original_group_id="a"),
        Point(id="b0", position=(10.1, 10.2), original_group_id="b"),
        Point(id="b1", position=(9.8, 10.4), original_group_id="b"),
        Point(id="c0", position=(20.2, 20.1), original_group_id="c"),
        Point(id="c1", position=(20.5, 19.9), original_group_id="c"),
    ]
    centers, assignments, score = run_kmeans(points, [(0.0, 0.0), (10.0, 10.0), (20.0, 20.0)])
    assert len(centers) == 3
    assert score > 0
    groups = {index: [] for index in range(3)}
    for point in points:
        groups[assignments[point.id]].append(point.id[0])
    assert len(groups[0]) >= 2
    assert len(groups[1]) >= 2
    assert len(groups[2]) >= 2
