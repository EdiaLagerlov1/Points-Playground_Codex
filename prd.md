# Points Cluster Playground PRD
## Goal
- Deliver a desktop sandbox for exploring Gaussian clusters, regenerating spreads, and comparing k-means realignment quality.

## Target Users
- Data/ML students building intuition for clustering.
- Demo facilitators needing an interactive cluster story.

## Success Metrics
- Dragging a center repositions all 10 points within 0.2s and recomputes their mean/variance.
- Bomb regeneration completes in <0.5s and amplifies variance by 0.3–2×.
- Each k-means run shows preview centroids, enables Apply exactly once, and writes a screenshot 100% of the time.
- Toolbar and board overlay present score delta + clustering metrics (V-measure/ARI/NMI) after compute; metrics reset after apply.

## Functional Scope
- Spawn three color-coded Gaussian groups (blue/green/red) with 10 points each.
- Enforce 1/3 overlap only during initial seeding; later edits behave freely.
- Paint group circles sized to enclose member points with padding.
- Let users drag the bomb icon from the canvas corner; dropping on a center rebuilds that group with new mean/variance.
- Compute k-means on demand, show color-coded preview centers with black outlines, and persist within-cluster sum of squares + Δ%.
- Display clustering quality overlay (V-measure, ARI, NMI) comparing current calc vs. last applied baseline.
- Apply becomes enabled only after a compute; on click it commits assignments, updates radii, disables Apply, and refreshes the ground-truth labels for the next comparison.
- Save every compute as `output/kmeans_YYYYMMDD_HHMMSS.png`.

## Non-Functional Requirements
- PyQt6 desktop app, offline, Python ≥3.11.
- Frame latency under 100ms for drag and bomb moves.
- Deterministic runs when seed is set through toolbar spinner.
- Keep files ≤100 lines and modules single-responsibility.

## Data Model
- `Group`: id, color, mean, variance, points, center_position.
- `Point`: id, position, original_group_id, is_overlap.
- `AppState`: groups, pending_kmeans (preview centers), seed.
- Runtime metrics: `_applied_score` (baseline sum of squares), `_last_score` (preview score), `_ground_truth_labels` (cluster ids at last apply).

## Data Flow
```
config/points.json
        ↓ load_configuration()
    initial Groups ----→ StateManager ----→ BoardWidget (render)
                                   ↑             |
Toolbar actions (drag, compute, apply) ----------+
                                   ↓             |
                             ScreenshotService ←─+
```

## Statistical Outputs
- `score`: total within-cluster variance returned by `run_kmeans`.
- `% diff`: ((baseline − score)/baseline)*100; positive indicates improvement, negative indicates regression.
- `V-measure`, `ARI`, `NMI`: compare clustering versus the last applied ground truth and are shown on the board overlay and toolbar.

## Running Results
- Local run example: `python main.py`.
- After Compute: toolbar prints `Score diff: +12.45% (total 358.12) | V-measure 91.0% | ARI 85.0% | NMI 88.5%` and dashboard shows preview centers.
  ![Compute preview](./output/kmeans_20251106_064654.png)
- After Apply: preview disappears, new radii reflect recomputed spreads.
- Screenshots stored under `/output/`; sample images: `output/kmeans_20251106_064654.png`, `output/kmeans_20251106_115146.png`.
  ![Post bomb example](./output/kmeans_20251106_115146.png)
- חישובי המשך:
  ![2025-11-08 19:12:49](./output/kmeans_20251108_191249.png)
  ![2025-11-08 19:13:15](./output/kmeans_20251108_191315.png)
  ![2025-11-08 19:13:37](./output/kmeans_20251108_191337.png)

## Technical Approach
- Rendering: custom QWidget canvas with manual painting helpers.
- State: `StateManager` exposes movement, regeneration, scoring, k-means application.
- Logic modules: `sampling`, `overlap_manager`, `clustering`, `kmeans_apply`, `screenshot_service`.
- UI modules: `BoardWidget`, `BombOverlay`, `ToolbarWidget`, `MainWindow`.

## Validation
- Pytest suite covering clustering correctness and overlap enforcement.
- Manual QA: drag centers, regenerate each group, run k-means twice, verify toolbar score and screenshot presence.

## Out of Scope
- Network distribution, multi-user sync, persistent storage beyond screenshots, advanced analytics dashboards.
