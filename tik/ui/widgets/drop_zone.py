from __future__ import annotations
import json
from typing import Optional, Any
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData
from PyQt6.QtWidgets import QLabel, QWidget


class FieldDropZone(QLabel):
    """Drop target nhận payload JSON (text/plain hoặc application/json) từ QWebEngineView."""
    acceptRequested = pyqtSignal(object)  # emits DataChunk-like object (dict-like object)

    def __init__(self, field: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.field = field
        self.setText("Drop here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            "border: 1px dashed #2a3a4a; padding: 10px; border-radius: 8px; color: #93a4b8;"
        )

    # ---- helpers ----
    def _parse_mime(self, md: QMimeData) -> Optional[dict[str, Any]]:
        # Prefer application/json if present
        if md.hasFormat("application/json"):
            try:
                raw = md.data("application/json")
                if hasattr(raw, "data"):
                    raw = raw.data()
                s = bytes(raw).decode("utf-8", errors="ignore")
                return json.loads(s)
            except Exception:
                pass
        # Fallback text/plain
        if md.hasText():
            try:
                return json.loads(md.text())
            except Exception:
                pass
        return None

    # ---- DnD events ----
    def dragEnterEvent(self, e):
        data = self._parse_mime(e.mimeData())
        if data and data.get("field") == self.field:
            self.setStyleSheet("border: 2px solid #58a6ff; padding: 9px; border-radius: 8px; color: #d7e3f4;")
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.setStyleSheet("border: 1px dashed #2a3a4a; padding: 10px; border-radius: 8px; color: #93a4b8;")

    def dragMoveEvent(self, e):
        data = self._parse_mime(e.mimeData())
        if data and data.get("field") == self.field:
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.setStyleSheet("border: 1px dashed #2a3a4a; padding: 10px; border-radius: 8px; color: #93a4b8;")
        data = self._parse_mime(e.mimeData())
        if not data or data.get("field") != self.field:
            e.ignore()
            return
        payload = {
            "id": data["chunkId"],
            "document_id": data["documentId"],
            "source_id": data["sourceId"],
            "field": data["field"],
            "value": data["value"],
            "offset_start": data.get("offsetStart", 0),
            "offset_end": data.get("offsetEnd", 0),
            "exclusive_group": data.get("exclusiveGroup") or None,
        }
        self.acceptRequested.emit(type("Obj", (), payload))
        e.acceptProposedAction()
