(function () {
  function toPayload(span) {
    return JSON.stringify({
      chunkId: span.getAttribute("data-chunk-id"),
      field: span.getAttribute("data-field"),
      value: span.getAttribute("data-value"),
      sourceId: span.getAttribute("data-source-id"),
      documentId: span.getAttribute("data-document-id"),
      exclusiveGroup: span.getAttribute("data-exclusive-group") || null
    });
  }

  function setup() {
    document.querySelectorAll("span.chunk").forEach(function (sp) {
      // đảm bảo phần tử có thể kéo
      sp.setAttribute("draggable", "true");

      sp.addEventListener("dragstart", function (ev) {
        const payload = toPayload(sp);
        try { ev.dataTransfer.effectAllowed = "copyMove"; } catch (e) {}
        try { ev.dataTransfer.dropEffect = "copy"; } catch (e) {}
        // Qt thường đọc text/plain; thêm application/json làm dự phòng
        try { ev.dataTransfer.setData("text/plain", payload); } catch (e) {}
        try { ev.dataTransfer.setData("application/json", payload); } catch (e) {}
      });

      sp.addEventListener("mouseenter", function () { sp.classList.add("hover"); });
      sp.addEventListener("mouseleave", function () { sp.classList.remove("hover"); });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
