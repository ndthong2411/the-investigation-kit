const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text) n.textContent = text;
  return n;
};

const state = {
  tabs: ["Reader","Listener","Insider","Profiler","Objectives","Log"],
  active: "Reader",
  entity: null,
  sources: [],
  lastDrag: null,
  showObjectives: false,
  advisor: null,
};

async function api(path, opts={}) {
  const res = await fetch(path, {headers:{'Content-Type':'application/json'}, ...opts});
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadInitial() {
  const [entities, sources] = await Promise.all([
    api("/api/entities"), api("/api/sources?kind=reader")
  ]);
  state.entity = entities[0];
  state.sources = sources;
}

function mountTopbar(root) {
  const bar = el("div","topbar");
  const left = el("div",null);
  left.append(el("div",null,"TIK • Investigation Workspace (Minimal)"));
  const tabs = el("div","tabs");
  state.tabs.forEach(t=>{
    const b = el("button","btn",t);
    b.onclick = () => {
      if (t==="Objectives") { state.showObjectives = true; render(); return; }
      state.active = t; render();
    };
    tabs.append(b);
  });
  const right = el("div",null,"09 Aug 2025 • 16:00");
  bar.append(left,tabs,right);
  root.append(bar);
}

function fieldBox(label, fieldKey) {
  const box = el("div","field");
  const lab = el("div","label",label);
  const val = el("div","val");
  const ev = el("div","ev");
  box.append(lab,val,ev);

  // drop
  box.ondragover = (e)=> e.preventDefault();
  box.ondrop = async (e)=>{
    e.preventDefault();
    const payload = e.dataTransfer.getData("application/json");
    if (!payload) return;
    const { field, value, sourceId } = JSON.parse(payload);
    if (field !== fieldKey) return;
    const ent = await api("/api/chunks/commit",{ method:"POST", body: JSON.stringify({
      entityId: state.entity.id, field, value, sourceId
    })});
    state.entity = ent;
    // advisor for key fields
    if (["name","dob"].includes(field)) state.advisor = `Good. You captured ${field.toUpperCase()}. Review Objectives.`;
    render();
  };

  // fill value & evidence & conflict UI
  const cur = state.entity.fields[fieldKey];
  val.textContent = cur || "— drop here —";
  const evidence = state.entity.evidence[fieldKey] || [];
  const uniq = [...new Set(evidence.map(e=>e.value))];
  if (uniq.length > 1) box.classList.add("warn");
  ev.textContent = `Evidence: ${evidence.length}`

  if (uniq.length > 1) {
    const wrap = el("div",null);
    uniq.forEach(v=>{
      const b = el("button","btn",`choose "${v}"`);
      b.style.marginRight = "6px";
      b.onclick = async ()=>{
        const ent = await api("/api/chunks/resolve",{ method:"POST", body: JSON.stringify({
          entityId: state.entity.id, field: fieldKey, chosen: v
        })});
        state.entity = ent; render();
      }
      wrap.append(b);
    });
    box.append(wrap);
  }

  return box;
}

function mountProfile(root) {
  const section = el("div","profile");
  const card = el("div","card");
  const top = el("div",null);
  const avatar = el("img"); avatar.src = state.entity.avatar; avatar.width=48; avatar.style.borderRadius="10px"; avatar.style.marginRight="10px";
  const name = el("span",null, state.entity.fields.name || "(unknown)");
  top.append(avatar, name);
  const fields = el("div","fields");
  const order = ["name","alias","dob","address","occupation","email","phone","account","contact"];
  order.forEach(k=>{
    fields.append(fieldBox(k, k));
  });
  card.append(top, fields);
  section.append(card);
  root.append(section);

  // mini graph stub
  const graph = el("div","graph");
  const title = el("div","label"); title.textContent="Graph (stub)";
  graph.append(title);
  const contacts = (state.entity.evidence["contact"] || []).map(e=>e.value);
  [...new Set(contacts)].slice(0,5).forEach(c=>{
    const n = el("div","node",c);
    graph.append(n);
  });
  root.append(graph);
}

function mountRight(root) {
  const head = el("div","section-h",state.active);
  const contentWrap = el("div","content");
  if (state.active === "Reader") {
    const s = state.sources[0];
    const cont = el("div");
    cont.innerHTML = s.html;
    // make chunks draggable
    cont.querySelectorAll(".chunk").forEach(span=>{
      span.setAttribute("draggable","true");
      span.addEventListener("dragstart",(e)=>{
        const field = span.getAttribute("data-field");
        const value = span.getAttribute("data-value");
        state.lastDrag = {field,value,sourceId: s.id};
        e.dataTransfer.setData("application/json", JSON.stringify(state.lastDrag));
      });
    });
    contentWrap.append(cont);
  } else {
    const stub = el("div",null,"This tab is stubbed in the minimal demo. Use Reader to drag highlighted chunks.");
    contentWrap.append(stub);
  }
  root.append(head, contentWrap);
}

function mountObjectivesModal(root){
  if (!state.showObjectives) return;
  const modal = el("div","modal");
  const backdrop = el("div","backdrop"); backdrop.onclick=()=>{state.showObjectives=false; render();}
  const panel = el("div","panel");
  const title = el("div",null); title.textContent = "Objectives";
  const ul = el("ul");
  const items = [
    { id:"obj1", text:"Xác định họ tên", check: !!state.entity.fields.name },
    { id:"obj2", text:"Ghi nhận DOB", check: !!state.entity.fields.dob },
    { id:"obj3", text:"Xác minh địa chỉ hiện tại", check: !!state.entity.fields.address },
  ];
  items.forEach(o=>{
    const li = el("li",null);
    const badge = el("span","badge", o.check ? "DONE" : "—");
    badge.style.marginRight="8px";
    li.append(badge, document.createTextNode(o.text));
    ul.append(li);
  });
  const actions = el("div",null);
  const close = el("button","btn","Close"); close.onclick=()=>{state.showObjectives=false; render();}
  actions.style.marginTop="10px"; actions.style.textAlign="right"; actions.append(close);
  panel.append(title,ul,actions);
  modal.append(backdrop,panel);
  root.append(modal);
}

function mountAdvisor(root){
  if (!state.advisor) return;
  const modal = el("div","modal");
  const backdrop = el("div","backdrop");
  const panel = el("div","panel");
  const title = el("div",null); title.textContent = "Advisor";
  const msg = el("div",null); msg.textContent = state.advisor;
  const btn = el("button","btn","Acknowledge");
  btn.style.marginTop="10px";
  btn.onclick=()=>{ state.advisor=null; render(); }
  panel.append(title,msg,btn);
  modal.append(backdrop,panel);
  root.append(modal);
}

function render() {
  const root = document.getElementById("app");
  root.innerHTML = "";
  mountTopbar(root);

  const grid = el("div","grid");
  const left = el("div","left");
  left.append(el("div","section-h","Profile / Graph / Timeline"));
  mountProfile(left);

  const right = el("div","right");
  mountRight(right);

  grid.append(left,right);
  root.append(grid);

  const footer = el("div","footer");
  footer.textContent = `Drag last: ${state.lastDrag ? `${state.lastDrag.field} → ${state.lastDrag.value}` : "—"}`;
  root.append(footer);

  mountObjectivesModal(root);
  mountAdvisor(root);
}

(async function bootstrap(){
  await loadInitial();
  render();
})();
