from __future__ import annotations

from tik.core.store import Store
from tik.core.services.fake import FakeCaseService, FakeDocumentService, FakeChunkService, FakeObjectiveService, FakeEventService
from pathlib import Path


def _mk_store():
    data_dir = Path(__file__).resolve().parents[1] / "tik" / "data"
    return Store(
        case_service=FakeCaseService(data_dir),
        document_service=FakeDocumentService(data_dir),
        chunk_service=FakeChunkService(data_dir),
        objective_service=FakeObjectiveService(),
        event_service=FakeEventService()
    )


def test_accept_and_undo(qtbot):
    s = _mk_store()
    s.load_default_case()
    case = s.sel.case
    doc = case.documents[0]
    html, chunks = s.doc_svc.load_document_html_and_chunks(doc.id)  # type: ignore[attr-defined]
    # pick the name chunk
    c = [x for x in chunks if x["field"] == "name"][0]
    s.request_accept(type("Obj", (), {
        "id": c["id"], "document_id": c["document_id"], "source_id": c["source_id"],
        "field": c["field"], "value": c["value"], "offset_start": 0, "offset_end": 0,
        "exclusive_group": c.get("exclusive_group")
    }))
    assert "name" in s.sel.person.accepted
    s.undo_stack.undo()
    assert "name" not in s.sel.person.accepted
