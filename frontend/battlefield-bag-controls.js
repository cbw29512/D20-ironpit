(() => {
  "use strict";
  // UI state: one active runner, optional completed/partial JSON report,
  // and a stop flag checked between real player-facing fights.
  const el = id => document.getElementById(id);
  const control = {running: false, stopRequested: false};
  let result = null;

  function progress(report) {
    try {
      const progressEl = el("bag-all-progress");
      progressEl.max = report.total;
      progressEl.value = report.completed;
      const unobserved = report.cases.reduce((count, row) =>
        count + (row.abilities?.not_observed_count || 0), 0);
      el("bag-all-status").textContent =
        report.completed + " / " + report.total + " pregens · " +
        report.passed + " fights without detected violations · " +
        report.failed + " failures · " + unobserved + " unobserved abilities";
      el("bag-download-button").disabled = !report.completed;
    } catch (error) {
      console.error("Could not show player-facing bag suite progress", error);
      throw error;
    }
  }

  async function start(api) {
    if (control.running) return;
    result = null;
    el("bag-all-button").disabled = true;
    el("bag-stop-button").disabled = false;
    el("bag-download-button").disabled = true;
    el("bag-all-status").textContent =
      "Loading every certified 2014/2024 pregen onto the real battlefield…";
    try {
      result = await window.IRON_PIT_BATTLEFIELD_BAG_RUNNER.run(api, control, progress);
      progress(result);
      el("bag-all-status").textContent += result.stopped
        ? " · Stopped; partial logs ready."
        : " · Completed; full logs ready.";
    } catch (error) {
      console.error("Player-facing Punching Bag test all failed", error);
      el("bag-all-status").textContent =
        "Test All could not complete: " + (error?.message || String(error));
    } finally {
      el("bag-stop-button").disabled = true;
      el("bag-all-button").disabled = false;
    }
  }

  function download() {
    try {
      if (!result?.cases?.length) throw new Error("No completed combat logs exist.");
      const blob = new Blob([JSON.stringify(result, null, 2)],
        {type: "application/json;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "iron-pit-battlefield-bag-pregens-" + result.seed + ".json";
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (error) {
      console.error("Could not download full player-facing combat logs", error);
      el("bag-all-status").textContent =
        "Could not download logs: " + (error?.message || String(error));
    }
  }

  function install(api) {
    try {
      for (const id of ["bag-all-button", "bag-stop-button", "bag-download-button",
        "bag-all-status", "bag-all-progress"]) {
        if (!el(id)) throw new Error("Missing player-facing gauntlet control " + id);
      }
      if (!api?.load || !api?.matchup || !api?.ensureRuleset)
        throw new Error("Real player-facing fight controllers are required.");
      el("bag-all-button").disabled = false;
      el("bag-all-button").addEventListener("click", () => { void start(api); });
      el("bag-stop-button").addEventListener("click", () => {
        if (control.running) control.stopRequested = true;
      });
      el("bag-download-button").addEventListener("click", download);
    } catch (error) {
      console.error("Could not install battlefield Punching Bag controls", error);
      throw error;
    }
  }
  window.IRON_PIT_BATTLEFIELD_BAG_CONTROLS = {install};
})();