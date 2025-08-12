from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

from ...core.models import AcceptedChunk, DataChunk


class ConflictsDialog(QDialog):
    def __init__(self, parent, current: AcceptedChunk, incoming: DataChunk):
        super().__init__(parent)
        self.setWindowTitle("Resolve Conflict")
        self._winner: AcceptedChunk | None = None

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"Field: {current.field}"))
        lay.addWidget(QLabel(f"Keep current: {current.value}"))
        lay.addWidget(QLabel(f"Use incoming: {incoming.value}"))

        btns = QHBoxLayout()
        keep = QPushButton("Keep current")
        use = QPushButton("Use incoming")
        cancel = QPushButton("Cancel")

        keep.clicked.connect(lambda: self._choose(current))
        use.clicked.connect(lambda: self._choose(AcceptedChunk(
            chunk_id=incoming.id, field=incoming.field, value=incoming.value,
            source_id=incoming.source_id, document_id=incoming.document_id,
            exclusive_group=incoming.exclusive_group)))
        cancel.clicked.connect(self.reject)

        btns.addWidget(keep); btns.addWidget(use); btns.addWidget(cancel)
        lay.addLayout(btns)

    def _choose(self, winner: AcceptedChunk) -> None:
        self._winner = winner
        self.accept()

    def winner(self) -> AcceptedChunk | None:
        return self._winner
