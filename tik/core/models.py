from __future__ import annotations

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


class Person(BaseModel):
    id: str
    name: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    # accepted values indexed by field
    accepted: Dict[str, "AcceptedChunk"] = Field(default_factory=dict)


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
    field: str                 # e.g., "name", "dob"
    value: str
    offset_start: int
    offset_end: int
    exclusive_group: Optional[str] = None  # conflicts within same field


class AcceptedChunk(BaseModel):
    chunk_id: str
    field: str
    value: str
    source_id: str
    document_id: str
    exclusive_group: Optional[str] = None


class Case(BaseModel):
    id: str
    title: str
    people: List[Person]
    sources: List[Source]
    documents: List[Document]


class ObjectivePredicate(BaseModel):
    """Minimal predicate system: op in {'exists'} with a path like 'person.name'."""
    op: Literal["exists"]
    path: str  # "person.<field>"


class ObjectiveExpr(BaseModel):
    """Boolean tree: kind 'AND' or 'OR' with either children or a predicate leaf."""
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
