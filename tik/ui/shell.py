from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QTabWidget, QToolBar, QFileDialog, QMessageBox
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

        # Provide conflict resolver to store (UI mediation)
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
