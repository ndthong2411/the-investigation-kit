from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from loguru import logger
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QUndoStack

from .commands import AcceptChunkCommand, ResolveConflictCommand, RetractChunkCommand
from .models import (
    AcceptedChunk,
    AdvisorEvent,
    Case,
    DataChunk,
    Document,
    Objective,
    Person,
    Source,
)
from .services.base import CaseService, ChunkService, DocumentService, EventService, ObjectiveService
from .persistence import load_record_json, save_record_json


@dataclass
class Selection:
    case: Optional[Case] = None
    person: Optional[Person] = None
    source: Optional[Source] = None
    document: Optional[Document] = None


class Store(QObject):
    # Signals for UI
    selectionChanged = pyqtSignal()
    documentLoaded = pyqtSignal(str, list)  # (html, chunks_json_str)
    acceptedChanged = pyqtSignal()
    objectivesChanged = pyqtSignal()
    advisorEvent = pyqtSignal(object)  # AdvisorEvent

    def __init__(
        self,
        *,
        case_service: CaseService,
        document_service: DocumentService,
        chunk_service: ChunkService,
        objective_service: ObjectiveService,
        event_service: EventService,
    ):
        super().__init__()
        self.case_svc = case_service
        self.doc_svc = document_service
        self.chunk_svc = chunk_service
        self.obj_svc = objective_service
        self.evt_svc = event_service
        self.sel = Selection()
        self.undo_stack = QUndoStack(self)
        self._conflict_resolver: Optional[Callable[[AcceptedChunk, DataChunk], Optional[AcceptedChunk]]] = None

    # === Bootstrapping & selection ===
    def load_default_case(self) -> None:
        case = self.case_svc.load_default_case()
        self.sel.case = case
        self.sel.person = case.people[0] if case.people else None
        self.selectionChanged.emit()
        logger.info("Loaded case {}", case.title)

    def set_conflict_resolver(self, fn: Callable[[AcceptedChunk, DataChunk], Optional[AcceptedChunk]]) -> None:
        self._conflict_resolver = fn

    def select_source(self, source: Optional[Source]) -> None:
        self.sel.source = source
        self.selectionChanged.emit()

    def select_document(self, doc: Optional[Document]) -> None:
        self.sel.document = doc
        if not doc:
            return
        html, chunks = self.doc_svc.load_document_html_and_chunks(doc.id)
        self.documentLoaded.emit(html, chunks)
        self.selectionChanged.emit()

    # === Accept / retract / conflicts ===
    def request_accept(self, chunk: DataChunk) -> None:
        person = self.sel.person
        if not person:
            return
        current = person.accepted.get(chunk.field)
        if (
            current
            and current.exclusive_group
            and chunk.exclusive_group
            and current.exclusive_group == chunk.exclusive_group
        ):
            # No-op if identical chunk
            if current.chunk_id == chunk.id:
                logger.debug("Accept idempotent for chunk {}", chunk.id)
                return
            logger.debug("Conflict detected on field {} between {} and {}", chunk.field, current.chunk_id, chunk.id)
            winner: Optional[AcceptedChunk] = None
            if self._conflict_resolver:
                winner = self._conflict_resolver(current, chunk)
            if winner is None:
                logger.debug("Conflict unresolved; abort")
                return
            cmd = ResolveConflictCommand(person, current, chunk, winner)
            self.undo_stack.push(cmd)
        else:
            cmd = AcceptChunkCommand(person, chunk)
            self.undo_stack.push(cmd)
        # Objectives re-eval
        self.evaluate_objectives()
        self.acceptedChanged.emit()

    def retract_field(self, field: str) -> None:
        person = self.sel.person
        if not person or field not in person.accepted:
            return
        cmd = RetractChunkCommand(person, field)
        self.undo_stack.push(cmd)
        self.evaluate_objectives()
        self.acceptedChanged.emit()

    # === Objectives & events ===
    def evaluate_objectives(self) -> None:
        case = self.sel.case
        person = self.sel.person
        if not case or not person:
            return
        changed = self.obj_svc.evaluate(case, person)
        if changed:
            self.objectivesChanged.emit()

    def poll_events(self) -> None:
        evt = self.evt_svc.poll()
        if evt:
            self.advisorEvent.emit(evt)
            logger.info("Advisor: {}", evt.text)

    # === Persistence (simple JSON) ===
    def save_to_path(self, path: Path) -> bool:
        if not self.sel.case or not self.sel.person:
            return False
        save_record_json(Path(path), self.sel.case, self.sel.person)
        logger.info("Saved record JSON to {}", path)
        return True

    def load_from_path(self, path: Path) -> bool:
        if not self.sel.case or not self.sel.person:
            return False
        data = load_record_json(Path(path))
        accepted = {}
        for field, obj in (data.get("accepted") or {}).items():
            accepted[field] = AcceptedChunk.model_validate(obj)
        self.sel.person.accepted = accepted
        self.evaluate_objectives()
        self.acceptedChanged.emit()
        logger.info("Loaded record JSON from {}", path)
        return True
