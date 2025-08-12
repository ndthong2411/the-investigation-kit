from __future__ import annotations

import httpx
from typing import List, Tuple, Optional

from .base import CaseService, DocumentService, ChunkService, ObjectiveService, EventService
from ..models import Case, Document, DataChunk, AdvisorEvent, Person


class ApiCaseService(CaseService):
    def __init__(self, base_url: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=10.0)

    def load_default_case(self) -> Case:
        raise NotImplementedError("HTTP API not implemented in Phase 1")


class ApiDocumentService(DocumentService):
    def __init__(self, base_url: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=10.0)

    def load_document_html_and_chunks(self, document_id: str) -> Tuple[str, list]:
        raise NotImplementedError("HTTP API not implemented in Phase 1")


class ApiChunkService(ChunkService):
    def __init__(self, base_url: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=10.0)

    def list_chunks_for_document(self, document_id: str) -> List[DataChunk]:
        raise NotImplementedError("HTTP API not implemented in Phase 1")


class ApiObjectiveService(ObjectiveService):
    def __init__(self, base_url: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=10.0)

    def evaluate(self, case: Case, person: Person) -> bool:
        raise NotImplementedError("HTTP API not implemented in Phase 1")


class ApiEventService(EventService):
    def __init__(self, base_url: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=10.0)

    def poll(self) -> Optional[AdvisorEvent]:
        raise NotImplementedError("HTTP API not implemented in Phase 1")
