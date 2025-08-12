from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from ..models import Case, Document, DataChunk, Objective, AdvisorEvent, Person


class CaseService(ABC):
    @abstractmethod
    def load_default_case(self) -> Case: ...


class DocumentService(ABC):
    @abstractmethod
    def load_document_html_and_chunks(self, document_id: str) -> Tuple[str, list]: ...


class ChunkService(ABC):
    @abstractmethod
    def list_chunks_for_document(self, document_id: str) -> List[DataChunk]: ...


class ObjectiveService(ABC):
    @abstractmethod
    def evaluate(self, case: Case, person: Person) -> bool:
        """Recompute objective statuses. Return True if any change."""


class EventService(ABC):
    @abstractmethod
    def poll(self) -> Optional[AdvisorEvent]: ...
