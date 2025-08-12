print(r"""
=== TIK Phase 1 — Manual QA Checklist ===

[ ] Launch app (python -m tik.app). Window should show left tabs (Profiler/Graph) and Reader on right.
[ ] In Reader, select "Citizen DB" then "Registry Entry". The document renders highlighted chunks.
[ ] Drag the "Jane Doe" highlight onto Profiler's Name drop zone. Name should populate; a toast appears; Log shows entry.
[ ] Drag the date "1990-01-23" to DOB. Objective "Identify subject's name and date of birth" should now show as complete in Objectives dialog.
[ ] Drag the conflicting name (from Social Feed if present) onto Name. Conflict dialog appears; choose either option and verify Profiler updates accordingly.
[ ] Use Undo, then Redo from toolbar to confirm state transitions.
[ ] Retract a field via its button; verify it clears and can be undone.
[ ] Close and relaunch app (state is in-memory only; values reset), ensuring no crashes on load.

Notes:
- Drag payload is plain text JSON; verify with an external text drop target if debugging.
- If drops don't work, click inside the web view once; some platforms require focus before DnD.
""")
