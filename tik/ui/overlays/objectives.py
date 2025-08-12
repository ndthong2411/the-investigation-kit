from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton

from ...core.store import Store
from ...core.models import Objective


class ObjectivesDialog(QDialog):
    def __init__(self, parent, store: Store):
        super().__init__(parent)
        self.setWindowTitle("Objectives")
        self.store = store
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Complete these to progress the case:"))
        self.list = QListWidget()
        lay.addWidget(self.list)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)
        self._refresh()

    def _refresh(self) -> None:
        self.list.clear()
        case = self.store.sel.case
        if not case:
            return
        objectives = getattr(case, "_objectives", [])
        for obj in objectives:
            it = QListWidgetItem(f"{'✔' if obj.satisfied else '○'}  {obj.title}")
            it.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.list.addItem(it)
