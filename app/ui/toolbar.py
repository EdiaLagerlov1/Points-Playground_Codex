from __future__ import annotations

from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget


class ToolbarWidget(QWidget):
    def __init__(
        self,
        on_compute: Callable[[], None],
        on_apply: Callable[[], None],
        on_seed_change: Callable[[int], None],
    ) -> None:
        super().__init__()
        self._on_compute = on_compute
        self._on_apply = on_apply
        self._on_seed_change = on_seed_change
        self.status_label = QLabel("")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(QLabel("Tools"))
        compute = QPushButton("Calc K-mean")
        compute.clicked.connect(self._on_compute)
        layout.addWidget(compute)
        self.apply_button = QPushButton("Apply K-mean")
        self.apply_button.clicked.connect(self._on_apply)
        self.apply_button.setEnabled(False)
        layout.addWidget(self.apply_button)
        seed_label = QLabel("Seed")
        layout.addWidget(seed_label)
        seed_box = QSpinBox()
        seed_box.setRange(-1, 999999)
        seed_box.setValue(-1)
        seed_box.valueChanged.connect(self._handle_seed_change)
        layout.addWidget(seed_box)
        layout.addStretch(1)
        layout.addWidget(self.status_label)

    def show_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _handle_seed_change(self, value: int) -> None:
        self._on_seed_change(value if value >= 0 else -1)

    def set_apply_enabled(self, enabled: bool) -> None:
        self.apply_button.setEnabled(enabled)
