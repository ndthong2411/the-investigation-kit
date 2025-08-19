from __future__ import annotations
import json
from pathlib import Path
from importlib import resources
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListView, QSplitter
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

from ...core.store import Store
from .widgets.source_list import SourceListModel, SourceListView
from .widgets.document_list import DocumentListModel, DocumentListView


class DebugPage(QWebEnginePage):
    # Print JS console logs to help verify highlight.js is running
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):  # type: ignore[override]
        print(f"[JS:{level.name}] {sourceID}:{lineNumber} — {message}")


class DocumentView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setPage(DebugPage(self))  # enable console log passthrough

    def set_document(self, html_fragment: str) -> None:
        # Build a small HTML page that links our local CSS/JS assets.
        base = resources.files("tik.ui.web")  # requires tik/ui/web/__init__.py
        css_url = QUrl.fromLocalFile(str(base.joinpath("style.css")))
        js_url = QUrl.fromLocalFile(str(base.joinpath("highlight.js")))
        tpl = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="{css_url.toString()}">
</head>
<body>
  <div id="container">{html_fragment}</div>
  <script src="{js_url.toString()}"></script>
</body>
</html>"""
        # Use a file base URL to relax same-origin for local assets.
        self.setHtml(tpl, QUrl.fromLocalFile(str(base)))


class ReaderPanel(QWidget):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store

        lay = QHBoxLayout(self)
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Horizontal)

        self.source_model = SourceListModel(store)
        self.source_view = SourceListView()
        self.source_view.setModel(self.source_model)

        self.doc_model = DocumentListModel(store)
        self.doc_view = DocumentListView()
        self.doc_view.setModel(self.doc_model)

        left = QWidget()
        l = QVBoxLayout(left)
        l.addWidget(QLabel("Sources"))
        l.addWidget(self.source_view)
        l.addWidget(QLabel("Documents"))
        l.addWidget(self.doc_view)

        self.web = DocumentView()
        splitter.addWidget(left)
        splitter.addWidget(self.web)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        lay.addWidget(splitter)

        self._wire()

    def _wire(self) -> None:
        self.source_view.sourceSelected.connect(self.store.select_source)
        self.doc_view.documentSelected.connect(self.store.select_document)
        self.store.documentLoaded.connect(self._on_document_loaded)

    def _on_document_loaded(self, html, _chunks_json_list) -> None:
        self.web.set_document(html)
