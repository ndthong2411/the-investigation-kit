from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtWidgets import QLabel, QWidget


class Toast(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.setStyleSheet(
            "background:#16202b; border:1px solid #2a3a4a; border-radius:8px; padding:8px 12px;"
        )
        self.hide()
        self._timer = QTimer(self)
        self._timer.setInterval(2200)
        self._timer.timeout.connect(self.hide)

    def show(self, text: str) -> None:  # type: ignore[override]
        super().setText(text)
        p = self.parent().mapToGlobal(QPoint(30, 30))
        super().move(p)
        super().show()
        self._timer.start()
