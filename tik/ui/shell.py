from __future__ import annotations

from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter,
    QTabWidget,
    QToolBar,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtGui import QAction

from ..core.store import Store
from .left.profiler import ProfilerPanel
from .left.graph_stub import GraphPanel
from .right.reader import ReaderPanel
from .overlays.objectives import ObjectivesDialog
from .overlays.conflicts import ConflictsDialog
from .overlays.logdock import LogDock
from .widgets.toast import Toast


class MainWindow(QMainWindow):
    def __init__(self, store: Store):
        super().__init__()
        self.setWindowTitle("The Investigation Kit")
        self.store = store
        self.toast = Toast(self)

        left_tabs = QTabWidget()
        self.profiler = ProfilerPanel(store)
        self.graph = GraphPanel()
        left_tabs.addTab(self.profiler, "Profiler")
        left_tabs.addTab(self.graph, "Graph")

        self.reader = ReaderPanel(store)
        split = QSplitter()
        split.setOrientation(Qt.Orientation.Horizontal)
        split.addWidget(left_tabs)
        split.addWidget(self.reader)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        self.setCentralWidget(split)

        self.logdock = LogDock(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.logdock)

        self._build_toolbar()
        self._wire_signals()

        def resolver(current, incoming):
            dlg = ConflictsDialog(self, current=current, incoming=incoming)
            if dlg.exec():
                return dlg.winner()
            return None

        self.store.set_conflict_resolver(resolver)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main")
        self.addToolBar(tb)

        act_obj = QAction("Objectives", self)
        act_obj.triggered.connect(self._open_objectives)
        tb.addAction(act_obj)

        act_export = QAction("Export Markdown", self)
        act_export.triggered.connect(self._export_markdown)
        tb.addAction(act_export)

        act_save = QAction("Save State", self)
        act_save.triggered.connect(self._save_state)
        tb.addAction(act_save)

        act_load = QAction("Load State", self)
        act_load.triggered.connect(self._load_state)
        tb.addAction(act_load)

        act_undo = self.store.undo_stack.createUndoAction(self, "Undo")
        act_redo = self.store.undo_stack.createRedoAction(self, "Redo")
        tb.addAction(act_undo)
        tb.addAction(act_redo)

    def _wire_signals(self) -> None:
        self.store.advisorEvent.connect(lambda evt: (self.toast.show(evt.text), self.logdock.append(evt)))
        self.store.objectivesChanged.connect(lambda: self.logdock.append_text("Objectives updated"))

    def _open_objectives(self) -> None:
        dlg = ObjectivesDialog(self, self.store)
        dlg.exec()

    # --- Export Markdown of current record ---
    def _export_markdown(self) -> None:
        case = self.store.sel.case
        person = self.store.sel.person
        if not case or not person:
            QMessageBox.warning(self, "Export", "No record loaded.")
            return
        lines = [f"# Research Record — {case.title}", ""]
        lines.append(f"_Exported: {datetime.now().isoformat(timespec='seconds')}_")
        lines.append("")
        for fid, ac in person.accepted.items():
            lines.append(f"## {fid}")
            lines.append(f"- **Value:** {ac.value}")
            if ac.quote:
                lines.append(f"- **Quote:** > {ac.quote}")
            lines.append(f"- **Source:** {ac.source_id}/{ac.document_id}")
            if ac.locator:
                lines.append(f"- **Locator:** {ac.locator}")
            if ac.confidence is not None:
                lines.append(f"- **Confidence:** {ac.confidence:.2f}")
            if ac.tags:
                lines.append(f"- **Tags:** {', '.join(ac.tags)}")
            lines.append("")
        text = "\n".join(lines)
        path, _ = QFileDialog.getSaveFileName(self, "Save Markdown", "record.md", "Markdown (*.md)")
        if not path:
            return
        Path(path).write_text(text, encoding="utf-8")
        QMessageBox.information(self, "Export", f"Saved: {path}")

    # --- NEW: Save/Load JSON state ---
    def _save_state(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Record", "record.json", "JSON (*.json)")
        if not path:
            return
        ok = self.store.save_to_path(Path(path))
        if ok:
            QMessageBox.information(self, "Save", f"Saved: {path}")
        else:
            QMessageBox.warning(self, "Save", "No record loaded.")

    def _load_state(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Record", "", "JSON (*.json)")
        if not path:
            return
        ok = self.store.load_from_path(Path(path))
        if ok:
            QMessageBox.information(self, "Load", f"Loaded: {path}")
        else:
            QMessageBox.warning(self, "Load", "Failed to load.")
