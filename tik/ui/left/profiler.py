from __future__ import annotations

from typing import List

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout

from ...core.store import Store
from ...core.models import AcceptedChunk, FieldDef
from ..widgets.drop_zone import FieldDropZone


class ProfilerPanel(QWidget):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self._labels: dict[str, QLabel] = {}
        self._zones: dict[str, FieldDropZone] = {}

        lay = QVBoxLayout(self)
        title = QLabel("Record")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        lay.addWidget(title)

        self.grid = QGridLayout()
        lay.addLayout(self.grid)

        self.btns = QHBoxLayout()
        lay.addLayout(self.btns)

        self.store.acceptedChanged.connect(self._refresh_values)
        self.store.selectionChanged.connect(self._rebuild_fields)
        self._rebuild_fields()

    def _current_fields(self) -> List[FieldDef]:
        case = self.store.sel.case
        if not case or not case.schema:
            # fallback: các field cũ nếu seed chưa có schema
            return [FieldDef(id="name", label="Name"),
                    FieldDef(id="dob", label="DOB"),
                    FieldDef(id="address", label="Address"),
                    FieldDef(id="occupation", label="Occupation")]
        return case.schema

    def _rebuild_fields(self) -> None:
        # clear UI
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        while self.btns.count():
            item = self.btns.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self._labels.clear()
        self._zones.clear()

        row = 0
        for f in self._current_fields():
            lab = QLabel(f.label)
            lab.setObjectName("Chip")
            val = QLabel("—")
            val.setWordWrap(True)

            dz = FieldDropZone(f.id)
            dz.acceptRequested.connect(self._on_accept)

            self._labels[f.id] = val
            self._zones[f.id] = dz

            self.grid.addWidget(lab, row, 0)
            self.grid.addWidget(val, row, 1)
            self.grid.addWidget(dz, row, 2)
            row += 1

        # retract buttons
        for f in self._current_fields():
            b = QPushButton(f"Retract {f.label}")
            b.clicked.connect(lambda _, field_id=f.id: self.store.retract_field(field_id))
            self.btns.addWidget(b)

        self._refresh_values()

    def _on_accept(self, chunk_payload) -> None:
        self.store.request_accept(chunk_payload)

    def _refresh_values(self) -> None:
        person = self.store.sel.person
        if not person:
            return
        for fid, lab in self._labels.items():
            ac: AcceptedChunk | None = person.accepted.get(fid)
            lab.setText(ac.value if ac else "—")
