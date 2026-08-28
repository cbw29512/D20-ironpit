(() => {
  "use strict";

  window.createIronPitRulesView = function createIronPitRulesView() {
    try {
      const summary = document.querySelector("#rules-summary");
      const list = document.querySelector("#rules-list");

      function render(report) {
        try {
          const counts = { implemented: 0, partial: 0, unsupported: 0, arena_assumption: 0 };
          list.innerHTML = "";
          for (const entry of report.entries || []) {
            counts[entry.status] = (counts[entry.status] || 0) + 1;
            const item = document.createElement("li");
            item.dataset.status = entry.status;
            const heading = document.createElement("strong");
            heading.textContent = `${entry.name} · ${entry.status.replaceAll("_", " ")}`;
            const notes = document.createElement("span");
            notes.textContent = entry.notes;
            item.append(heading, notes);
            list.appendChild(item);
          }
          summary.textContent = `${report.ruleset} · ${counts.implemented} implemented · ${counts.partial} partial · ${counts.unsupported} unsupported · ${counts.arena_assumption} assumptions`;
        } catch (error) {
          console.error("Rules coverage render failed", error);
          summary.textContent = "Rules coverage could not be rendered.";
        }
      }

      function setError(message) {
        try { summary.textContent = message; }
        catch (error) { console.error("Rules coverage error render failed", error); }
      }

      return { render, setError };
    } catch (error) {
      console.error("Rules coverage view initialization failed", error);
      throw error;
    }
  };
})();
