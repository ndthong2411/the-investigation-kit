from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex, pyqtSignal
from PyQt6.QtWidgets import QListView
from PyQt6.QtCore import QItemSelectionModel

from ....core.models import Document
from ....core.store import Store


class DocumentListModel(QAbstractListModel):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self._items: List[Document] = store.sel.case.documents if store.sel.case else []
        store.selectionChanged.connect(self._reload)

    def _reload(self) -> None:
        self.beginResetModel()
        self._items = self.store.sel.case.documents if self.store.sel.case else []
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._items)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        doc = self._items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return doc.title
        return None

    def document(self, row: int) -> Document:
        return self._items[row]


class DocumentListView(QListView):
    documentSelected = pyqtSignal(object)  # Document | None

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self._sel_model: Optional[QItemSelectionModel] = None

    def setModel(self, model) -> None:  # type: ignore[override]
        if self._sel_model is not None:
            try:
                self._sel_model.selectionChanged.disconnect(self._on_sel)
            except TypeError:
                pass
        super().setModel(model)
        self._sel_model = self.selectionModel()
        if self._sel_model is not None:
            self._sel_model.selectionChanged.connect(self._on_sel)

    def _on_sel(self, *_):
        idxs = self.selectedIndexes()
        if not idxs:
            self.documentSelected.emit(None)
            return
        model: DocumentListModel = self.model()  # type: ignore[assignment]
        self.documentSelected.emit(model.document(idxs[0].row()))
