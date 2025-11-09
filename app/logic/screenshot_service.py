from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QWidget


def save_widget_screenshot(widget: QWidget, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    pixmap = widget.grab()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"kmeans_{timestamp}.png"
    pixmap.save(str(path), "PNG")
    return path
