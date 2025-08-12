from __future__ import annotations

from PyQt6.QtWidgets import QApplication


TOKENS = {
    "bg": "#0e141b",
    "panel": "#111922",
    "surface": "#16202b",
    "text": "#d7e3f4",
    "muted": "#93a4b8",
    "accent": "#58a6ff",
    "accent2": "#f778ba",
    "danger": "#ff6b6b",
    "ok": "#4cc38a",
    "warn": "#ffcc66",
    "chip": "#1f2a36",
    "chip_border": "#2a3a4a",
}


def stylesheet() -> str:
    t = TOKENS
    return f"""
    * {{
        color: {t['text']};
        font-family: Segoe UI, Inter, Arial;
    }}
    QMainWindow, QWidget {{
        background: {t['bg']};
    }}
    QSplitter::handle {{
        background: {t['panel']};
        width: 6px;
    }}
    QTabBar::tab {{
        background: {t['panel']};
        padding: 6px 10px;
        margin: 2px;
        border-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background: {t['surface']};
        color: {t['accent']};
    }}
    QListView, QTreeView, QTextEdit {{
        background: {t['panel']};
        border: 1px solid {t['chip_border']};
        border-radius: 8px;
    }}
    QToolBar {{
        background: {t['surface']};
        border: none;
    }}
    QPushButton {{
        background: {t['chip']};
        border: 1px solid {t['chip_border']};
        border-radius: 8px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{ border-color: {t['accent']}; }}
    QLabel#Chip {{
        background: {t['chip']};
        border: 1px solid {t['chip_border']};
        border-radius: 8px;
        padding: 2px 6px;
        color: {t['muted']};
    }}
    """


def apply_theme(app: QApplication) -> None:
    app.setStyleSheet(stylesheet())
