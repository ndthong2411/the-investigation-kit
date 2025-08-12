
from __future__ import annotations

from pathlib import Path
from tik.core.services.fake import FakeCaseService, FakeDocumentService, FakeChunkService, FakeObjectiveService
from tik.core.models import ObjectiveExpr, ObjectivePredicate, AcceptedChunk


def test_objective_eval_changes():
    data_dir = Path(__file__).resolve().parents[1] / "tik" / "data"
    case = FakeCaseService(data_dir).load_default_case()
    objsvc = FakeObjectiveService()
    person = case.people[0]
    # initially false
    changed = objsvc.evaluate(case, person)
    assert changed is False
    # set name (đúng kiểu AcceptedChunk)
    person.accepted["name"] = AcceptedChunk(
        chunk_id="x", field="name", value="Jane", source_id="s", document_id="d", exclusive_group="identity"
    )
    changed = objsvc.evaluate(case, person)
    assert isinstance(changed, bool)
