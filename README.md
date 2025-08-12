# The Investigation Kit (TIK) — Phase 1

Orwell-style 2-pane desktop app built with **PyQt6**. Phase 1 focuses on local JSON seeds and a thin service layer you can later swap for an HTTP API.

## Features (Phase 1)
- Left: **Profiler** (Subject card + field drop zones) and **Relationship Graph (stub)** via a tab.
- Right: **Reader** (sources, documents, HTML viewer with highlighted datachunks). Listener/Insider are stubbed.
- Drag a highlighted **datachunk** into a matching Profiler field to accept it.
- **Conflict resolver** when an incoming chunk collides by `exclusiveGroup` on the same field.
- **Objectives** modal evaluates simple predicates (AND/OR of “field exists”).
- **Advisor/Log** dock shows periodic events (timer-mock now; WebSocket/API later).
- **Undo/Redo** via `QUndoStack` for accept and resolve.

## Quickstart

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -U pip
pip install -e .
# or: pip install -r requirements.txt

#run demo
python -m tik.app
# or
python scripts/run_demo.py

# run tests
pytest -q

#structure
tik/
  core/…        # models, store, commands, services
  ui/…          # Qt widgets, overlays, web assets
  data/…        # seed case, docs, chunks
scripts/
tests/
