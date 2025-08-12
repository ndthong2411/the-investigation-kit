from __future__ import annotations

from PyQt6.QtWidgets import QDockWidget, QTextEdit
from PyQt6.QtCore import Qt

from ...core.models import AdvisorEvent


class LogDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Advisor Log", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self.view = QTextEdit(self)
        self.view.setReadOnly(True)
        self.setWidget(self.view)

    def append(self, evt: AdvisorEvent) -> None:
        self.view.append(f"[{evt.level.upper()}] {evt.text}")

    def append_text(self, text: str) -> None:
        self.view.append(text)
