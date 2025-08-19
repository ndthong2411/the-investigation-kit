from __future__ import annotations

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


class FieldDef(BaseModel):
    id: str                     # ví dụ: "name", "dob", "definition", ...
    label: str                  # nhãn hiển thị
    type: Literal["text", "date", "number", "url", "note"] = "text"
    exclusive_group: Optional[str] = None  # nhóm độc quyền mặc định cho field (nếu có)


class Person(BaseModel):
    id: str
    name: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    accepted: Dict[str, "AcceptedChunk"] = Field(default_factory=dict)  # field -> AcceptedChunk


class Source(BaseModel):
    id: str
    title: str


class Document(BaseModel):
    id: str
    source_id: str
    title: str
    path: str  # relative package path to HTML file


class DataChunk(BaseModel):
    id: str
    document_id: str
    source_id: str
    field: str
    value: str
    offset_start: int
    offset_end: int
    exclusive_group: Optional[str] = None
    # --- mới cho nghiên cứu ---
    quote: Optional[str] = None       # trích nguyên văn (nếu muốn giữ nguyên dấu câu/chữ hoa)
    locator: Optional[str] = None     # vị trí trong tài liệu (vd: "p.12, para.3")
    confidence: Optional[float] = None  # 0..1: độ tin cậy sơ bộ
    tags: List[str] = Field(default_factory=list)


class AcceptedChunk(BaseModel):
    chunk_id: str
    field: str
    value: str
    source_id: str
    document_id: str
    exclusive_group: Optional[str] = None
    # --- giữ provenance mở rộng ---
    quote: Optional[str] = None
    locator: Optional[str] = None
    confidence: Optional[float] = None
    tags: List[str] = Field(default_factory=list)


class Case(BaseModel):
    id: str
    title: str
    people: List[Person]
    sources: List[Source]
    documents: List[Document]
    # --- schema động cho Profiler ---
    schema: List[FieldDef] = Field(default_factory=list)


class ObjectivePredicate(BaseModel):
    """
    Minimal predicate: op='exists' với path như 'record.name' hoặc 'person.name'.
    Ta chấp nhận cả 2 prefix để dùng cho nghiên cứu (record) lẫn điều tra (person).
    """
    op: Literal["exists"]
    path: str


class ObjectiveExpr(BaseModel):
    kind: Literal["AND", "OR", "LEAF"]
    children: Optional[List["ObjectiveExpr"]] = None
    predicate: Optional[ObjectivePredicate] = None


class Objective(BaseModel):
    id: str
    title: str
    expr: ObjectiveExpr
    satisfied: bool = False


class AdvisorEvent(BaseModel):
    id: str
    text: str
    level: Literal["info", "warn", "error"] = "info"
