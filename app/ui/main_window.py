from __future__ import annotations

from pathlib import Path
from typing import Callable

from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from app.logic.screenshot_service import save_widget_screenshot
from app.logic.state_manager import StateManager
from app.models import AppState, Vector2
from app.ui.board_widget import BoardWidget
from app.ui.toolbar import ToolbarWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        manager: StateManager,
        circle_radius: float,
        screenshot_dir: Path,
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.circle_radius = circle_radius
        self.screenshot_dir = screenshot_dir
        self.status_callback = status_callback
        self.board = BoardWidget(
            state_provider=lambda: self.manager.state,
            move_group=self._move_group,
            explode_group=self._explode_group,
            circle_radius=circle_radius,
        )
        self.toolbar = ToolbarWidget(
            on_compute=self._compute_kmeans,
            on_apply=self._apply_kmeans,
            on_seed_change=self._set_seed,
        )
        self._configure_layout()
        self.setWindowTitle("Points Cluster Playground")
        self.resize(960, 640)

    def _configure_layout(self) -> None:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.board, 1)
        layout.addWidget(self.toolbar)
        self.setCentralWidget(container)

    def _move_group(self, group_id: str, delta: Vector2) -> None:
        self.manager.move_group(group_id, delta)

    def _explode_group(self, group_id: str) -> None:
        self.manager.regenerate_group(group_id)
        self._notify(f"Group {group_id} regenerated.")

    def _compute_kmeans(self) -> None:
        _, _, score, percent, v_measure, ari, nmi = self.manager.compute_kmeans()
        self.board.set_score_text(f"V-measure {v_measure:.1f}% | ARI {ari:.1f}% | NMI {nmi:.1f}%")
        save_widget_screenshot(self.board, self.screenshot_dir)
        self.toolbar.show_status(
            f"Score diff: {percent:+.2f}% (total {score:.2f}) | "
            f"V-measure {v_measure:.1f}% | ARI {ari:.1f}% | NMI {nmi:.1f}%"
        )
        self.toolbar.set_apply_enabled(True)
        self._notify(f"K-mean computed. Δ{percent:+.2f}%, score {score:.2f}, V-measure {v_measure:.1f}%.")

    def _apply_kmeans(self) -> None:
        self.manager.apply_kmeans()
        self.board.set_score_text(None)
        self.toolbar.set_apply_enabled(False)
        self.toolbar.show_status("K-mean applied.")
        self._notify("K-mean applied.")

    def _set_seed(self, seed: int) -> None:
        self.manager.set_seed(seed if seed >= 0 else None)
        self._notify(f"Seed set to {seed}.")

    def _notify(self, message: str) -> None:
        if self.status_callback:
            self.status_callback(message)
