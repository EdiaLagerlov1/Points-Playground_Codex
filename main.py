from __future__ import annotations

import sys
from pathlib import Path
from random import Random

from PyQt6.QtWidgets import QApplication

from app.config_loader import load_configuration
from app.logic.state_manager import StateManager
from app.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    rng = Random()
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config" / "points.json"
    groups, bounds, circle_radius = load_configuration(config_path, rng)
    manager = StateManager(
        groups=groups,
        parameter_bounds=bounds,
        overlap_radius=circle_radius,
        rng=rng,
    )
    window = MainWindow(
        manager=manager,
        circle_radius=circle_radius,
        screenshot_dir=base_dir / "output",
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
