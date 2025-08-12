from __future__ import annotations

import json
import itertools
from pathlib import Path
from typing import List, Tuple, Optional

from pydantic import TypeAdapter

from ..models import (
    Case, Person, Source, Document, DataChunk, Objective, ObjectiveExpr, ObjectivePredicate, AdvisorEvent, AcceptedChunk
)
from ..document_renderer import wrap_chunks_into_html
from .base import CaseService, DocumentService, ChunkService, ObjectiveService, EventService


class FakeCaseService(CaseService):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._case: Optional[Case] = None
        self._objectives: List[Objective] = []

    def load_default_case(self) -> Case:
        seed_path = self.data_dir / "seed_case.json"
        data = json.loads(seed_path.read_text(encoding="utf-8"))
        case = Case.model_validate(data["case"])
        # Load objectives
        self._objectives = TypeAdapter(List[Objective]).validate_python(data.get("objectives", []))
        # Attach objectives back to case via private attr for retrieval by ObjectiveService
        case._objectives = self._objectives  # type: ignore[attr-defined]
        self._case = case
        return case


class FakeDocumentService(DocumentService):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load_document_html_and_chunks(self, document_id: str) -> Tuple[str, list]:
        doc_html_path = self.data_dir / "docs" / f"{document_id}.html"
        chunks_path = self.data_dir / "chunks" / f"{document_id}.json"
        html = doc_html_path.read_text(encoding="utf-8")
        chunks = TypeAdapter(List[DataChunk]).validate_python(json.loads(chunks_path.read_text(encoding="utf-8")))
        wrapped_html = wrap_chunks_into_html(html, chunks)
        # For WebEngine, also pass chunks as JSON list for client-side DnD attrs (redundant but handy to inspect)
        return wrapped_html, [c.model_dump() for c in chunks]


class FakeChunkService(ChunkService):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def list_chunks_for_document(self, document_id: str) -> List[DataChunk]:
        p = self.data_dir / "chunks" / f"{document_id}.json"
        return TypeAdapter(List[DataChunk]).validate_python(json.loads(p.read_text(encoding="utf-8")))


class FakeObjectiveService(ObjectiveService):
    def evaluate(self, case: Case, person: Person) -> bool:
        changed = False
        objectives: List[Objective] = getattr(case, "_objectives", [])
        for obj in objectives:
            was = obj.satisfied
            obj.satisfied = self._eval_expr(obj.expr, person)
            changed = changed or (was != obj.satisfied)
        return changed

    def _eval_expr(self, expr: ObjectiveExpr, person: Person) -> bool:
        if expr.kind == "LEAF" and expr.predicate:
            pred = expr.predicate
            if pred.op == "exists":
                _, field = pred.path.split(".", 1)
                return field in person.accepted and bool(person.accepted[field].value)
            return False
        if expr.kind == "AND":
            return all(self._eval_expr(c, person) for c in expr.children or [])
        if expr.kind == "OR":
            return any(self._eval_expr(c, person) for c in expr.children or [])
        return False


class FakeEventService(EventService):
    _counter = itertools.count(1)

    def poll(self) -> Optional[AdvisorEvent]:
        i = next(self._counter)
        levels = ["info", "warn", "error"]
        return AdvisorEvent(id=str(i), text=f"Background check #{i} completed.", level=levels[i % 3])
