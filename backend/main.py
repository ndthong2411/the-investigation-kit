from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Any

# ---------------- In-memory store (seed) ----------------
class Entity(BaseModel):
    id: str
    name: str | None = None
    avatar: str
    fields: Dict[str, str | None]
    evidence: Dict[str, List[Dict[str, Any]]]  # field -> [{value, sourceId}]

class Source(BaseModel):
    id: str
    kind: str  # reader|listener|insider
    title: str
    html: str  # already highlighted with <span class="chunk" ...>

class Store(BaseModel):
    entities: Dict[str, Entity]
    sources: Dict[str, Source]

def seed_store() -> Store:
    src = Source(
        id="src-001",
        kind="reader",
        title="City Gazette",
        html=(
            '<h2>City Gazette • Breaking</h2>'
            '<p>Authorities are investigating '
            '<span class="chunk" data-field="name" data-value="Evelyn Hart">Evelyn Hart</span> '
            '(also known as <span class="chunk" data-field="alias" data-value="Eva">Eva</span>), '
            'living at <span class="chunk" data-field="address" data-value="22 Palm Street">22 Palm Street</span>, '
            'previously at <span class="chunk" data-field="address" data-value="14 Cedar Ave">14 Cedar Ave</span>. '
            'Born on <span class="chunk" data-field="dob" data-value="1992-04-12">Apr 12, 1992</span>. '
            'Works at <span class="chunk" data-field="occupation" data-value="Aperture Analytics">Aperture Analytics</span>. '
            'Email <span class="chunk" data-field="email" data-value="evelyn.hart@aperture.ai">evelyn.hart@aperture.ai</span>, '
            'Phone <span class="chunk" data-field="phone" data-value="+1-202-555-0138">+1-202-555-0138</span>. '
            'Contacts: <span class="chunk" data-field="contact" data-value="Jonas Wilder">Jonas Wilder</span>, '
            '<span class="chunk" data-field="contact" data-value="Mira Koh">Mira Koh</span>. '
            'Handle <span class="chunk" data-field="account" data-value="@eva_h">@eva_h</span>.</p>'
        ),
    )
    ent = Entity(
        id="ent-001",
        name=None,
        avatar="https://api.dicebear.com/9.x/shapes/svg?seed=evelyn",
        fields={
            "name": None, "alias": None, "dob": None, "address": None,
            "occupation": None, "email": None, "phone": None, "account": None, "contact": None
        },
        evidence={}
    )
    return Store(entities={ent.id: ent}, sources={src.id: src})

STORE = seed_store()

# ---------------- API models ----------------
class CommitChunkIn(BaseModel):
    entityId: str
    field: str
    value: str
    sourceId: str

class ResolveIn(BaseModel):
    entityId: str
    field: str
    chosen: str

# ---------------- App ----------------
app = FastAPI(title="TIK Minimal API")

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/api/entities", response_model=List[Entity])
def list_entities():
    return list(STORE.entities.values())

@app.get("/api/sources", response_model=List[Source])
def list_sources(kind: str | None = None):
    srcs = list(STORE.sources.values())
    return [s for s in srcs if s.kind == kind] if kind else srcs

@app.post("/api/chunks/commit", response_model=Entity)
def commit_chunk(payload: CommitChunkIn):
    ent = STORE.entities.get(payload.entityId)
    if not ent:
        raise HTTPException(404, "Entity not found")
    ent.evidence.setdefault(payload.field, []).append({"value": payload.value, "sourceId": payload.sourceId})
    # Set field only if empty; conflicts resolved by /resolve
    if ent.fields.get(payload.field) in (None, ""):
        ent.fields[payload.field] = payload.value
    STORE.entities[ent.id] = ent
    return ent

@app.post("/api/chunks/resolve", response_model=Entity)
def resolve_conflict(payload: ResolveIn):
    ent = STORE.entities.get(payload.entityId)
    if not ent:
        raise HTTPException(404, "Entity not found")
    ent.fields[payload.field] = payload.chosen
    STORE.entities[ent.id] = ent
    return ent

# health
@app.get("/api/health", response_class=HTMLResponse)
def health():
    return "ok"
