(() => {
  "use strict";
  // UI state: one selected source-backed case, one attempt index, and at most
  // ONE full seeded replay in memory. Coverage summaries remain compact.
  const $ = id => document.getElementById(id);
  let selected = null, displayed = null, allCases = [];

  function clear(message = "Select a card and replay an attempt to see its actual turn-by-turn combat.") {
    try {
      displayed = null;
      $("bag-combat-events").textContent = message;
      $("bag-combat-message").textContent = message;
      $("bag-combat-txt").disabled = true;
      $("bag-combat-json").disabled = true;
    } catch (error) {
      console.error("Could not clear selected combat transcript", error);
      throw error;
    }
  }

  function choose(row) {
    try {
      selected = row || null;
      const caseIndex = allCases.indexOf(row);
      if (caseIndex >= 0) $("bag-card-select").value = String(caseIndex);
      $("bag-details").textContent = row ? JSON.stringify(row, null, 2)
        : "No Punching Bag card selected.";
      const selector = $("bag-attempt");
      selector.replaceChildren();
      for (const [index, attempt] of (row?.attempts || []).entries()) {
        const option = document.createElement("option");
        option.value = String(index);
        option.textContent = `Attempt ${attempt.attempt} · seed ${attempt.seed}`
          + (attempt.error ? " · recorded engine error" : "");
        selector.append(option);
      }
      const success = (row?.attempts || []).findIndex(a => !a.error);
      if (success >= 0) selector.value = String(success);
      $("bag-replay").disabled = !(row?.attempts || []).length;
      clear(row
        ? `Selected ${row.card_name} (${row.edition}). Choose a recorded attempt, then Replay selected fight.`
        : undefined);
    } catch (error) {
      console.error("Could not select a Punching Bag fight", error);
      throw error;
    }
  }

  function setCases(cases) {
    try {
      if (!Array.isArray(cases)) throw new TypeError("Combat card list must be an array.");
      allCases = cases;
      const select = $("bag-card-select");
      select.replaceChildren();
      for (const [index, row] of cases.entries()) {
        const option = document.createElement("option");
        option.value = String(index);
        option.textContent = `${row.edition} ${row.kind} · ${row.card_name} (${row.card_id})`;
        select.append(option);
      }
      select.disabled = !cases.length;
      choose(cases[0] || null);
    } catch (error) {
      console.error("Could not list combat card replays", error);
      throw error;
    }
  }

  function replay() {
    try {
      if (!selected) throw new Error("Select a Punching Bag card first.");
      displayed = null;
      clear("Replaying the actual engine from the recorded seed…");
      const index = Number($("bag-attempt").value);
      const record = window.IRON_PIT_TEST_BAG_COMBAT_LOG.replayCase(selected, index);
      displayed = record;
      $("bag-combat-events").textContent = record.narrative;
      $("bag-combat-message").textContent =
        `Real combat events: ${record.metadata.event_count}; round count: ${record.metadata.rounds}. Full transcript and raw event JSON can be downloaded.`;
      $("bag-combat-txt").disabled = false;
      $("bag-combat-json").disabled = false;
    } catch (error) {
      console.error("Selected Punching Bag battle replay failed", error);
      clear("This fight could not be replayed: " + (error?.message || String(error))
        + " The original seed and failure are still in the coverage report.");
    }
  }

  function download(ext) {
    try {
      if (!displayed) throw new Error("Replay a fight before downloading its combat log.");
      if (ext !== "txt" && ext !== "json") throw new Error("Unsupported combat log format.");
      const content = ext === "txt" ? displayed.narrative + "\n"
        : JSON.stringify(displayed.event_json, null, 2) + "\n";
      const meta = displayed.metadata;
      const safeId = String(meta.card_id).replace(/[^a-zA-Z0-9_-]/g, "_");
      const blob = new Blob([content], {type: ext === "txt"
        ? "text/plain;charset=utf-8" : "application/json;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `ironpit-combat-${meta.edition}-${safeId}-${meta.seed}.${ext}`;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (error) {
      console.error("Could not download selected combat log", error);
      $("bag-combat-message").textContent = "Combat download failed: " + (error?.message || String(error));
    }
  }

  function install() {
    try {
      for (const id of ["bag-card-select", "bag-details", "bag-attempt", "bag-replay", "bag-combat-txt",
        "bag-combat-json", "bag-combat-message", "bag-combat-events"]) {
        if (!$(id)) throw new Error("Missing real combat log UI control: " + id);
      }
      $("bag-card-select").addEventListener("change", () => {
        const index = Number($("bag-card-select").value);
        choose(allCases[index] || null);
      });
      $("bag-attempt").addEventListener("change", () => clear());
      $("bag-replay").addEventListener("click", replay);
      $("bag-combat-txt").addEventListener("click", () => download("txt"));
      $("bag-combat-json").addEventListener("click", () => download("json"));
      choose(null);
    } catch (error) {
      console.error("Could not install full combat log controls", error);
      throw error;
    }
  }

  window.IRON_PIT_TEST_BAG_COMBAT_VIEW = {install, choose, setCases, clear};
})();