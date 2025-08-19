(function () {
  function toPayload(span) {
    return JSON.stringify({
      chunkId: span.getAttribute("data-chunk-id"),
      field: span.getAttribute("data-field"),
      value: span.getAttribute("data-value"),
      sourceId: span.getAttribute("data-source-id"),
      documentId: span.getAttribute("data-document-id"),
      exclusiveGroup: span.getAttribute("data-exclusive-group") || null,
      // provenance
      quote: span.getAttribute("data-quote") || null,
      locator: span.getAttribute("data-locator") || null,
      confidence: (function (v) {
        try { return v === "" ? null : parseFloat(v); } catch (e) { return null; }
      })(span.getAttribute("data-confidence"))
    });
  }

  function setup() {
    const spans = document.querySelectorAll("span.chunk");
    console.log("[TIK] highlight.js attached — chunks:", spans.length);
    spans.forEach(function (sp) {
      if (!sp.hasAttribute("draggable")) sp.setAttribute("draggable", "true");
      sp.addEventListener("dragstart", function (ev) {
        const payload = toPayload(sp);
        try { ev.dataTransfer.effectAllowed = "copy"; } catch (e) {}
        try { ev.dataTransfer.dropEffect = "copy"; } catch (e) {}
        // Set BOTH, some Qt/Chromium builds only expose one of them
        ev.dataTransfer.setData("text/plain", payload);
        ev.dataTransfer.setData("application/json", payload);
        console.log("[TIK] dragstart payload:", payload);
      });
      sp.addEventListener("mouseenter", function () { sp.classList.add("hover"); });
      sp.addEventListener("mouseleave", function () { sp.classList.remove("hover"); });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})();
