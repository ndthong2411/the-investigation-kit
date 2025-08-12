from __future__ import annotations

from PyQt6.QtGui import QUndoCommand

from .models import Person, DataChunk, AcceptedChunk


class AcceptChunkCommand(QUndoCommand):
    def __init__(self, person: Person, chunk: DataChunk):
        super().__init__(f"Accept {chunk.field}")
        self.person = person
        self.chunk = chunk
        self._prev: AcceptedChunk | None = person.accepted.get(chunk.field)

    def redo(self) -> None:
        self.person.accepted[self.chunk.field] = AcceptedChunk(
            chunk_id=self.chunk.id,
            field=self.chunk.field,
            value=self.chunk.value,
            source_id=self.chunk.source_id,
            document_id=self.chunk.document_id,
            exclusive_group=self.chunk.exclusive_group,
        )

    def undo(self) -> None:
        if self._prev is None:
            self.person.accepted.pop(self.chunk.field, None)
        else:
            self.person.accepted[self._prev.field] = self._prev


class ResolveConflictCommand(QUndoCommand):
    """Winner is either the existing accepted or the incoming chunk turned into an AcceptedChunk."""
    def __init__(self, person: Person, current: AcceptedChunk, incoming: DataChunk, winner: AcceptedChunk):
        super().__init__(f"Resolve conflict {incoming.field}")
        self.person = person
        self.current = current
        self.incoming = incoming
        self.winner = winner
        self._before = current

    def redo(self) -> None:
        self.person.accepted[self.winner.field] = self.winner

    def undo(self) -> None:
        self.person.accepted[self._before.field] = self._before


class RetractChunkCommand(QUndoCommand):
    def __init__(self, person: Person, field: str):
        super().__init__(f"Retract {field}")
        self.person = person
        self.field = field
        self._prev = person.accepted.get(field)

    def redo(self) -> None:
        self.person.accepted.pop(self.field, None)

    def undo(self) -> None:
        if self._prev:
            self.person.accepted[self.field] = self._prev
