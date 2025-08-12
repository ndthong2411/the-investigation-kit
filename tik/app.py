from __future__ import annotations

import sys
from pathlib import Path
from loguru import logger

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication

from .theme.qss import apply_theme
from .core.store import Store
from .core.services.fake import FakeCaseService, FakeDocumentService, FakeChunkService, FakeObjectiveService, FakeEventService
from .ui.shell import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("The Investigation Kit")
    app.setOrganizationName("TIK")
    apply_theme(app)

    # Services (can be swapped by API services later)
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    case_svc = FakeCaseService(data_dir)
    doc_svc = FakeDocumentService(data_dir)
    chunk_svc = FakeChunkService(data_dir)
    obj_svc = FakeObjectiveService()
    evt_svc = FakeEventService()

    store = Store(case_service=case_svc, document_service=doc_svc, chunk_service=chunk_svc,
                  objective_service=obj_svc, event_service=evt_svc)

    # Bootstrap default case
    store.load_default_case()

    # UI
    win = MainWindow(store)
    win.resize(1280, 800)
    win.show()

    # Advisor event poller (timer-mock)
    timer = QTimer(win)
    timer.setInterval(3000)  # 3s
    timer.timeout.connect(store.poll_events)
    timer.start()

    logger.info("TIK started")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
