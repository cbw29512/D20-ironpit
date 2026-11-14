(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  let control = null, result = null;

  function status(report) {
    try {
      $("bag-progress").max = report.total;
      $("bag-progress").value = report.completed;
      const remaining = report.cases.reduce((sum, row) =>
        sum + row.not_observed.length, 0);
      $("bag-status").textContent = `${report.completed.toLocaleString()} / ` +
        `${report.total.toLocaleString()} cards · ` +
        `${report.fights_executed.toLocaleString()} fights · ` +
        `${report.failed.toLocaleString()} failed · ` +
        `${remaining.toLocaleString()} unobserved abilities` +
        (report.stopped ? " · stopped" : "");
    } catch (error) {
      console.error("Could not render Punching Bag progress", error);
      throw error;
    }
  }

  function render(report) {
    try {
      status(report);
      const missingCards = report.cases.filter(row => row.not_observed.length);
      $("bag-summary").textContent =
        `Completed ${report.completed} / ${report.total} certified cards. ` +
        `${report.failed} fights reported engine/rule violations. ` +
        `${missingCards.length} cards still have unobserved declared abilities. ` +
        "A successful fight does NOT certify untriggered abilities. " +
        "Download the ability coverage JSON for seeds and errors. " +
        "Select a card and replay its seed for real turn-by-turn combat logs.";
      const table = document.createElement("table");
      const head = document.createElement("tr");
      for (const name of ["Card / edition", "Attempts", "Ability evidence", "Result"]) {
        const th = document.createElement("th"); th.textContent = name;
        head.append(th);
      }
      table.append(head);
      const ordered = [...report.cases].sort((a,b) =>
        Number(Boolean(b.problems.length)) - Number(Boolean(a.problems.length)) ||
        b.not_observed.length - a.not_observed.length);
      for (const entry of ordered.slice(0, 150)) {
        const tr = document.createElement("tr");
        const values = [
          `${entry.card_name} (${entry.edition} ${entry.kind})`,
          String(entry.attempts.length),
          `${entry.observed}/${entry.declared} observed; ${entry.not_observed.length} remaining`,
          entry.problems.length ? entry.problems.join(", ") : "Completed (not fully certified)",
        ];
        for (const value of values) {
          const td = document.createElement("td"); td.textContent = value;
          tr.append(td);
        }
        tr.addEventListener("click", () => {
          window.IRON_PIT_TEST_BAG_COMBAT_VIEW.choose(entry);
        });
        table.append(tr);
      }
      $("bag-results").replaceChildren(table);
      window.IRON_PIT_TEST_BAG_COMBAT_VIEW.setCases(ordered);
      $("bag-download").disabled = false;
    } catch (error) {
      console.error("Could not render Punching Bag coverage report", error);
      throw error;
    }
  }

  async function start() {
    if (control) return;
    control = {stopRequested: false};
    result = null;
    $("bag-run").disabled = true;
    $("bag-stop").disabled = false;
    $("bag-download").disabled = true;
    $("bag-results").replaceChildren();
    window.IRON_PIT_TEST_BAG_COMBAT_VIEW.setCases([]);
    $("bag-details").textContent = "Collecting ability coverage and replay seeds…";
    try {
      const seed = Number($("seed").value);
      const attempts = Number($("bag-attempts").value);
      const plan = window.IRON_PIT_TEST_BAG_PLAN.create();
      $("bag-status").textContent =
        `Starting ${plan.total.toLocaleString()} card tests in both editions…`;
      result = await window.IRON_PIT_TEST_BAG_RUNNER.run(
        plan, seed, attempts, control, status);
      render(result);
    } catch (error) {
      console.error("Punching Bag all-cards run aborted", error);
      $("bag-status").textContent =
        "Punching Bag run failed: " + (error?.message || String(error));
    } finally {
      control = null;
      $("bag-run").disabled = false;
      $("bag-stop").disabled = true;
    }
  }

  function download() {
    try {
      if (!result) throw new Error("No completed Punching Bag test report.");
      const blob = new Blob([JSON.stringify(result, null, 2)],
        {type: "application/json"});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ironpit-punching-bag-${result.seed}.json`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (error) {
      console.error("Punching Bag report export failed", error);
      $("bag-status").textContent = "JSON export failed: " + error.message;
    }
  }

  // Validate and activate the independent, one-fight-at-a-time transcript UI.
  if (!window.IRON_PIT_TEST_BAG_COMBAT_VIEW?.install)
    throw new Error("The Punching Bag combat transcript controls are missing.");
  window.IRON_PIT_TEST_BAG_COMBAT_VIEW.install();
  $("bag-run").addEventListener("click", () => { void start(); });
  $("bag-stop").addEventListener("click", () => {
    if (control) control.stopRequested = true;
  });
  $("bag-download").addEventListener("click", download);
  try {
    if (new URLSearchParams(window.location.search).get("run") === "bag")
      void start();
  } catch (error) {
    console.error("Could not read Punching Bag launch URL", error);
  }
})();
