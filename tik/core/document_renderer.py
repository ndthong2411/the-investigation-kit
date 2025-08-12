from __future__ import annotations

from html import escape
from typing import List, Tuple

from .models import DataChunk


def _safe_html(html: str) -> str:
    """
    Minimal sanitizer: escape all tags except a tiny allowlist we rely on for basic formatting.
    NOTE: Backend should still sanitize before persisting.
    """
    allowed = {"b", "i", "em", "strong", "u", "p", "br", "ul", "ol", "li", "span"}
    out: list[str] = []
    i = 0
    while i < len(html):
        ch = html[i]
        if ch == "<":
            j = html.find(">", i + 1)
            if j == -1:
                out.append(escape(html[i:]))
                break
            tag = html[i + 1 : j].strip().strip("/")
            tag_name = tag.split()[0].lower() if tag else ""
            if tag_name in allowed:
                out.append(html[i : j + 1])
            else:
                out.append(escape(html[i : j + 1]))
            i = j + 1
        else:
            out.append(escape(ch))
            i += 1
    return "".join(out)


def _compute_ranges_with_fallback(safe: str, chunks: List[DataChunk]) -> List[Tuple[int, int, DataChunk]]:
    """
    Build non-overlapping (start, end, chunk) ranges on the sanitized `safe` string.

    Strategy:
      1) Trust offsets if they are within bounds AND the substring contains chunk.value.
      2) Otherwise, fallback to searching `chunk.value` inside `safe` (first non-overlapping match).
         This fixes common offset drift caused by HTML tags vs textContent indexing.
    """
    ranges: List[Tuple[int, int, DataChunk]] = []

    def overlaps(a_start: int, a_end: int) -> bool:
        for s, e, _ in ranges:
            if max(a_start, s) < min(a_end, e):
                return True
        return False

    for c in chunks:
        start, end = c.offset_start, c.offset_end
        ok = isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(safe)
        if ok:
            segment = safe[start:end]
            if c.value not in segment:
                ok = False

        if not ok:
            # Fallback: locate `value` directly in `safe`, avoiding already-reserved ranges
            needle = c.value or ""
            if not needle:
                continue
            search_pos = 0
            found = False
            while True:
                idx = safe.find(needle, search_pos)
                if idx == -1:
                    break
                candidate = (idx, idx + len(needle))
                if not overlaps(*candidate):
                    start, end = candidate
                    found = True
                    break
                search_pos = idx + 1
            if not found:
                # Give up on this chunk if we cannot locate it
                continue

        if not overlaps(start, end):
            ranges.append((start, end, c))

    ranges.sort(key=lambda t: t[0])
    return ranges


def wrap_chunks_into_html(html: str, chunks: List[DataChunk]) -> str:
    """
    Return an HTML fragment with <span class="chunk" draggable="true" ...> inserted
    exactly around chunk values.

    Steps:
      1) Sanitize (keep a few formatting tags).
      2) Compute non-overlapping highlight ranges using offsets OR fallback string search.
      3) Insert chunk spans in order to keep HTML valid (no broken nesting).
    """
    safe = _safe_html(html)
    ranges = _compute_ranges_with_fallback(safe, chunks)

    result: list[str] = []
    cursor = 0
    for start, end, c in ranges:
        if cursor < start:
            result.append(safe[cursor:start])
        data_attrs = (
            f'data-chunk-id="{c.id}" '
            f'data-field="{c.field}" '
            f'data-value="{escape(c.value)}" '
            f'data-source-id="{c.source_id}" '
            f'data-document-id="{c.document_id}" '
            f'data-exclusive-group="{escape(c.exclusive_group or "")}"'
        )
        result.append(f'<span class="chunk" draggable="true" {data_attrs}>')
        result.append(safe[start:end])
        result.append("</span>")
        cursor = end

    if cursor < len(safe):
        result.append(safe[cursor:])

    return "".join(result)
