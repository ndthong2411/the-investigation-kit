from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lab = QLabel("Relationship Graph (stub)")
        lab.setStyleSheet("font-size: 16px; color: #93a4b8;")
        lay.addWidget(lab)

    # API placeholders for future graph integration
    def set_graph_data(self, data) -> None:
        pass

    def center_on(self, node_id: str) -> None:
        pass
