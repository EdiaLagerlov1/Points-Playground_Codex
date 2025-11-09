from __future__ import annotations

import math
from random import Random
from typing import Dict, List, Tuple

from app.logic import overlap_manager, sampling
from app.logic.kmeans_apply import apply_assignments
from app.logic.clustering import run_kmeans
from app.models import AppState, Group, Point, Vector2


class StateManager:
    def __init__(
        self,
        groups: List[Group],
        parameter_bounds: sampling.ParameterBounds,
        overlap_radius: float,
        rng: Random,
    ) -> None:
        self.bounds = parameter_bounds
        self.overlap_radius = overlap_radius
        self.rng = rng
        self.state = AppState(groups=list(groups))
        self._pending_assignments: Dict[str, int] | None = None
        self._overlap_enabled = True
        overlap_manager.enforce_overlap(self.state.groups, overlap_radius, rng)
        self._overlap_enabled = False
        self._last_score: float | None = None
        self._applied_score: float | None = self._current_score()
        self._ground_truth_labels = self._current_cluster_labels()

    def set_active_tool(self, tool: str) -> None:
        self.state.active_tool = tool

    def set_seed(self, seed: int | None) -> None:
        self.state.seed = seed
        self.rng = Random(seed) if seed is not None else Random()

    def move_group(self, group_id: str, delta: Vector2) -> None:
        group = self._require_group(group_id)
        dx, dy = delta
        group.center_position = (group.center_position[0] + dx, group.center_position[1] + dy)
        for point in group.points:
            point.position = (point.position[0] + dx, point.position[1] + dy)
        group.mean = group.center_position
        group.variance = self._variance(group.center_position, group.points)
        self._enforce_overlap_if_enabled()

    def regenerate_group(self, group_id: str) -> None:
        group = self._require_group(group_id)
        mean, variance = sampling.random_parameters(self.bounds, self.rng)
        variance = self._amplify_variance(variance)
        updated = sampling.regenerate_group(group, mean, variance, self.rng)
        self._replace_group(updated)
        self._enforce_overlap_if_enabled()

    def compute_kmeans(self) -> Tuple[List[Vector2], Dict[str, int], float, float, float, float, float]:
        points = self._all_points()
        truth_labels = self._ground_truth_labels
        baseline_labels = truth_labels if truth_labels else self._current_cluster_labels()
        initial_centers = [group.center_position for group in self.state.groups]
        centers, assignments, score = run_kmeans(points, initial_centers)
        self.state.pending_kmeans = centers
        self._pending_assignments = assignments
        baseline = self._applied_score if self._applied_score is not None else score
        percent = 0.0 if baseline == 0 else ((baseline - score) / baseline) * 100.0
        predicted_labels = [assignments.get(point.id, 0) for point in points]
        v_measure = self._v_measure(baseline_labels, predicted_labels) * 100.0
        ari = self._adjusted_rand_index(baseline_labels, predicted_labels) * 100.0
        nmi = self._normalized_mutual_info(baseline_labels, predicted_labels) * 100.0
        self._last_score = score
        return centers, assignments, score, percent, v_measure, ari, nmi

    def apply_kmeans(self) -> None:
        if not self._pending_assignments:
            return
        centers = self.state.pending_kmeans
        self.state.groups = apply_assignments(self.state.groups, centers, self._pending_assignments)
        self._enforce_overlap_if_enabled()
        self.state.pending_kmeans = []
        self._pending_assignments = None
        self._applied_score = self._last_score if self._last_score is not None else self._current_score()
        self._ground_truth_labels = self._current_cluster_labels()
        self._last_score = None

    def _all_points(self) -> List[Point]:
        return [point for group in self.state.groups for point in group.points]

    def _replace_group(self, replacement: Group) -> None:
        for index, group in enumerate(self.state.groups):
            if group.id == replacement.id:
                self.state.groups[index] = replacement
                return
        raise KeyError(f"Group {replacement.id} not found.")

    def _require_group(self, group_id: str) -> Group:
        for group in self.state.groups:
            if group.id == group_id:
                return group
        raise KeyError(f"Group {group_id} not found.")

    @staticmethod
    def _variance(center: Vector2, points: List[Point]) -> Vector2:
        if not points:
            return (0.0, 0.0)
        count = float(len(points))
        return (
            sum((point.position[0] - center[0]) ** 2 for point in points) / count,
            sum((point.position[1] - center[1]) ** 2 for point in points) / count,
        )

    def _enforce_overlap_if_enabled(self) -> None:
        if self._overlap_enabled:
            overlap_manager.enforce_overlap(self.state.groups, self.overlap_radius, self.rng)

    def _amplify_variance(self, variance: Vector2) -> Vector2:
        def adjust(value: float, min_val: float, max_val: float) -> float:
            if self.rng.random() < 0.5:
                scale = self.rng.uniform(0.3, 0.6)
            else:
                scale = self.rng.uniform(1.4, 2.0)
            return max(min_val, min(max_val, value * scale))

        return (
            adjust(variance[0], self.bounds.variance_min[0], self.bounds.variance_max[0]),
            adjust(variance[1], self.bounds.variance_min[1], self.bounds.variance_max[1]),
        )

    def _current_score(self) -> float:
        total = 0.0
        for group in self.state.groups:
            mean = group.mean
            for point in group.points:
                total += (point.position[0] - mean[0]) ** 2 + (point.position[1] - mean[1]) ** 2
        return total

    def _current_cluster_labels(self) -> List[int]:
        label_map = {group.id: index for index, group in enumerate(self.state.groups)}
        labels: List[int] = []
        for group in self.state.groups:
            label = label_map[group.id]
            for _ in group.points:
                labels.append(label)
        return labels

    def _v_measure(self, truth: List[int], predicted: List[int]) -> float:
        if not truth:
            return 0.0
        cluster_counts: Dict[int, Dict[int, int]] = {}
        class_counts: Dict[int, int] = {}
        for t, p in zip(truth, predicted):
            class_counts[t] = class_counts.get(t, 0) + 1
            group_counts = cluster_counts.setdefault(p, {})
            group_counts[t] = group_counts.get(t, 0) + 1

        total_points = float(len(truth))
        h_c = self._entropy(class_counts.values(), total_points)
        h_k = self._entropy(
            (sum(group_counts.values()) for group_counts in cluster_counts.values()),
            total_points,
        )
        h_c_given_k = self._conditional_entropy(cluster_counts, total_points)
        h_k_given_c = self._conditional_entropy_by_class(cluster_counts, class_counts, total_points)

        homogeneity = 1.0 if h_c == 0 else 1.0 - h_c_given_k / h_c
        completeness = 1.0 if h_k == 0 else 1.0 - h_k_given_c / h_k
        if homogeneity + completeness == 0:
            return 0.0
        return 2 * homogeneity * completeness / (homogeneity + completeness)

    def _adjusted_rand_index(self, truth: List[int], predicted: List[int]) -> float:
        if not truth:
            return 0.0
        class_counts: Dict[int, int] = {}
        cluster_counts: Dict[int, int] = {}
        contingency: Dict[Tuple[int, int], int] = {}
        for t, p in zip(truth, predicted):
            class_counts[t] = class_counts.get(t, 0) + 1
            cluster_counts[p] = cluster_counts.get(p, 0) + 1
            key = (p, t)
            contingency[key] = contingency.get(key, 0) + 1

        def comb2(value: int) -> float:
            return value * (value - 1) / 2.0

        sum_comb_c = sum(comb2(value) for value in class_counts.values())
        sum_comb_k = sum(comb2(value) for value in cluster_counts.values())
        sum_comb_cont = sum(comb2(value) for value in contingency.values())
        total_pairs = comb2(len(truth))
        if total_pairs == 0:
            return 0.0
        expected_index = (sum_comb_c * sum_comb_k) / total_pairs
        max_index = (sum_comb_c + sum_comb_k) / 2.0
        if max_index == expected_index:
            return 0.0
        return (sum_comb_cont - expected_index) / (max_index - expected_index)

    def _normalized_mutual_info(self, truth: List[int], predicted: List[int]) -> float:
        if not truth:
            return 0.0
        class_counts: Dict[int, int] = {}
        cluster_counts: Dict[int, int] = {}
        contingency: Dict[Tuple[int, int], int] = {}
        for t, p in zip(truth, predicted):
            class_counts[t] = class_counts.get(t, 0) + 1
            cluster_counts[p] = cluster_counts.get(p, 0) + 1
            key = (p, t)
            contingency[key] = contingency.get(key, 0) + 1
        total_points = float(len(truth))
        mutual_info = 0.0
        for (cluster, cls), value in contingency.items():
            if value == 0:
                continue
            mutual_info += (value / total_points) * math.log(
                (value * total_points) / (cluster_counts[cluster] * class_counts[cls])
            )
        h_cluster = self._entropy(cluster_counts.values(), total_points)
        h_class = self._entropy(class_counts.values(), total_points)
        denominator = h_cluster + h_class
        if denominator == 0:
            return 0.0
        return (2 * mutual_info) / denominator

    @staticmethod
    def _entropy(counts, total: float) -> float:
        entropy = 0.0
        for count in counts:
            if count == 0:
                continue
            prob = count / total
            entropy -= prob * math.log(prob)
        return entropy

    @staticmethod
    def _conditional_entropy(cluster_counts: Dict[int, Dict[str, int]], total: float) -> float:
        entropy = 0.0
        for counts in cluster_counts.values():
            cluster_total = sum(counts.values())
            if cluster_total == 0:
                continue
            weight = cluster_total / total
            entropy += weight * StateManager._entropy(counts.values(), cluster_total)
        return entropy

    @staticmethod
    def _conditional_entropy_by_class(
        cluster_counts: Dict[int, Dict[str, int]],
        class_counts: Dict[str, int],
        total: float,
    ) -> float:
        entropy = 0.0
        class_totals = class_counts
        for class_id, class_total in class_totals.items():
            if class_total == 0:
                continue
            weight = class_total / total
            cluster_distribution = []
            for counts in cluster_counts.values():
                cluster_distribution.append(counts.get(class_id, 0))
            entropy += weight * StateManager._entropy(cluster_distribution, class_total)
        return entropy
