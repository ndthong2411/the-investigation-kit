from __future__ import annotations

from html import escape
from typing import List, Tuple

from .models import DataChunk


def _safe_html(html: str) -> str:
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
            out.append(html[i:j+1] if tag_name in allowed else escape(html[i:j+1]))
            i = j + 1
        else:
            out.append(escape(ch)); i += 1
    return "".join(out)


def _ranges(safe: str, chunks: List[DataChunk]) -> List[Tuple[int, int, DataChunk]]:
    res: List[Tuple[int, int, DataChunk]] = []
    def overlap(a,b,c,d): return max(a,c) < min(b,d)
    for c in chunks:
        st, en = c.offset_start, c.offset_end
        ok = 0 <= st < en <= len(safe) and c.value in safe[st:en]
        if not ok:
            idx = safe.find(c.value)
            if idx != -1:
                st, en = idx, idx + len(c.value)
            else:
                continue
        if any(overlap(st,en,x,y) for x,y,_ in res): continue
        res.append((st,en,c))
    return sorted(res, key=lambda t:t[0])


def wrap_chunks_into_html(html: str, chunks: List[DataChunk]) -> str:
    safe = _safe_html(html)
    ranges = _ranges(safe, chunks)
    out: list[str] = []
    cur = 0
    for st, en, c in ranges:
        if cur < st: out.append(safe[cur:st])
        attrs = (
            f'data-chunk-id="{c.id}" data-field="{c.field}" data-value="{escape(c.value)}" '
            f'data-source-id="{c.source_id}" data-document-id="{c.document_id}" '
            f'data-exclusive-group="{escape(c.exclusive_group or "")}" '
            f'data-quote="{escape(c.quote or c.value)}" '
            f'data-locator="{escape(c.locator or "")}" '
            f'data-confidence="{"" if c.confidence is None else c.confidence}"'
        )
        out.append(f'<span class="chunk" draggable="true" {attrs}>')
        out.append(safe[st:en])
        out.append("</span>")
        cur = en
    if cur < len(safe): out.append(safe[cur:])
    return "".join(out)
