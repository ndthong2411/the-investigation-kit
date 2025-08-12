from __future__ import annotations

from tik.core.models import DataChunk, AcceptedChunk, ObjectiveExpr, ObjectivePredicate, Objective


def test_chunk_roundtrip():
    c = DataChunk(
        id="c1", document_id="d1", source_id="s1",
        field="name", value="Alice", offset_start=10, offset_end=15, exclusive_group="identity"
    )
    ac = AcceptedChunk(
        chunk_id=c.id, field=c.field, value=c.value,
        source_id=c.source_id, document_id=c.document_id, exclusive_group=c.exclusive_group
    )
    assert ac.field == "name" and ac.value == "Alice"

def test_objective_tree():
    obj = Objective(
        id="o1", title="has name", satisfied=False,
        expr=ObjectiveExpr(kind="LEAF", predicate=ObjectivePredicate(op="exists", path="person.name"))
    )
    assert obj.expr.kind == "LEAF"
