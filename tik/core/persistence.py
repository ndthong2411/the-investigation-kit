from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .models import Case, Person, AcceptedChunk


def _serialize_person(person: Person) -> Dict[str, dict]:
    """field -> AcceptedChunk dict"""
    return {fid: ac.model_dump() for fid, ac in person.accepted.items()}


def save_record_json(path: Path, case: Case, person: Person) -> None:
    """Write current record (accepted fields) to JSON."""
    data = {
        "version": 1,
        "case_id": case.id,
        "case_title": case.title,
        "person_id": person.id,
        "accepted": _serialize_person(person),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_record_json(path: Path) -> dict:
    """Load record JSON as plain dict (no mutation here)."""
    return json.loads(path.read_text(encoding="utf-8"))
