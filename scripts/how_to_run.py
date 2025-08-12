print(r"""
=== TIK Phase 1 — Run Instructions ===

1) Create & activate a virtual environment:
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate

2) Install dependencies:
   pip install -U pip
   pip install -e .
   # or: pip install -r requirements.txt

3) Run the app:
   python -m tik.app
   # or:
   python scripts/run_demo.py

4) Run tests:
   pytest -q

Tips:
- If WebEngine fails to load on Linux, ensure Qt WebEngine runtime packages are installed.
- Use Undo/Redo from the toolbar after drag-and-drop to verify command stack.
""")
