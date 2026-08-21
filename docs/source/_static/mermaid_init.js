document.addEventListener("DOMContentLoaded", function () {
  function initMermaid() {
    const mermaidCodeBlocks = document.querySelectorAll(
      ".highlight-mermaid, pre.mermaid, div.mermaid"
    );
    if (!mermaidCodeBlocks || mermaidCodeBlocks.length === 0) return;

    mermaidCodeBlocks.forEach(function (block, idx) {
      let code = "";
      if (block.tagName.toLowerCase() === "div" && block.classList.contains("highlight-mermaid")) {
        const pre = block.querySelector("pre");
        code = pre ? pre.textContent.trim() : block.textContent.trim();
      } else {
        code = block.textContent.trim();
      }

      const container = document.createElement("div");
      container.className = "mermaid-diagram";
      container.style.textAlign = "center";
      container.style.margin = "1.5rem 0";

      const mermaidDiv = document.createElement("div");
      mermaidDiv.className = "mermaid";
      mermaidDiv.textContent = code;

      container.appendChild(mermaidDiv);
      block.parentNode.replaceChild(container, block);
    });

    if (typeof mermaid !== "undefined") {
      mermaid.initialize({
        startOnLoad: true,
        theme: "neutral",
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
          curve: "basis"
        }
      });
      mermaid.run();
    }
  }

  if (typeof mermaid === "undefined") {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
    script.onload = initMermaid;
    document.head.appendChild(script);
  } else {
    initMermaid();
  }
});
