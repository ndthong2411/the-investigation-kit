from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout

from ...core.store import Store
from ...core.models import AcceptedChunk
from ..widgets.drop_zone import FieldDropZone


FIELDS: List[str] = ["name", "dob", "address", "occupation"]


class ProfilerPanel(QWidget):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self._labels: dict[str, QLabel] = {}
        self._zones: dict[str, FieldDropZone] = {}

        lay = QVBoxLayout(self)
        title = QLabel("Subject")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        lay.addWidget(title)

        grid = QGridLayout()
        row = 0
        for field in FIELDS:
            lab = QLabel(field.capitalize())
            lab.setObjectName("Chip")
            val = QLabel("—")
            val.setWordWrap(True)

            dz = FieldDropZone(field)
            dz.acceptRequested.connect(self._on_accept)

            self._labels[field] = val
            self._zones[field] = dz

            grid.addWidget(lab, row, 0)
            grid.addWidget(val, row, 1)
            grid.addWidget(dz, row, 2)
            row += 1

        lay.addLayout(grid)

        btns = QHBoxLayout()
        for field in FIELDS:
            b = QPushButton(f"Retract {field}")
            b.clicked.connect(lambda _, f=field: self.store.retract_field(f))
            btns.addWidget(b)
        lay.addLayout(btns)

        self.store.acceptedChanged.connect(self._refresh)
        self.store.selectionChanged.connect(self._refresh)
        self._refresh()

    def _on_accept(self, chunk_payload) -> None:
        self.store.request_accept(chunk_payload)

    def _refresh(self) -> None:
        person = self.store.sel.person
        if not person:
            return
        for f in FIELDS:
            ac: AcceptedChunk | None = person.accepted.get(f)
            self._labels[f].setText(ac.value if ac else "—")
