from __future__ import annotations

import json
from pathlib import Path

from tik.core.models import AcceptedChunk
from tik.core.services.fake import FakeCaseService, FakeDocumentService, FakeChunkService, FakeObjectiveService, FakeEventService
from tik.core.store import Store


def _mk_store():
    data_dir = Path(__file__).resolve().parents[1] / "tik" / "data"
    return Store(
        case_service=FakeCaseService(data_dir),
        document_service=FakeDocumentService(data_dir),
        chunk_service=FakeChunkService(data_dir),
        objective_service=FakeObjectiveService(),
        event_service=FakeEventService(),
    )


def test_save_load_roundtrip(tmp_path):
    s = _mk_store()
    s.load_default_case()
    # seed accepted value
    p = s.sel.person
    p.accepted["name"] = AcceptedChunk(
        chunk_id="cX", field="name", value="Jane Doe", source_id="s-001", document_id="doc_0001", exclusive_group="identity"
    )
    out = tmp_path / "record.json"
    assert s.save_to_path(out) is True
    # clear and reload
    p.accepted.clear()
    assert "name" not in p.accepted
    assert s.load_from_path(out) is True
    assert p.accepted["name"].value == "Jane Doe"
    # sanity: JSON structure
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["case_id"] and data["person_id"] and "accepted" in data
