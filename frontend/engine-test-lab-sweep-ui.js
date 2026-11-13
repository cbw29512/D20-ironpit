(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  let running = null, report = null;
  function progress(result, plan) {
    try {
      $("sweep-progress").max = plan.total;
      $("sweep-progress").value = result.completed;
      $("sweep-status").textContent =
        `${result.completed.toLocaleString()} / ${plan.total.toLocaleString()} matchups · ` +
        `segment starts at #${result.start_case} · ` +
        `${result.passed.toLocaleString()} passed · ${result.failed.toLocaleString()} failed` +
        (result.stopped ? " · stopped" : "");
    } catch (error) {
      console.error("Could not display Test All progress", error);
      throw error;
    }
  }
  function render(result, plan) {
    try {
      progress(result, plan);
      const blocked = Object.entries(plan.unavailable || {})
        .map(([edition, count]) => `${edition}: ${count} blocked/not playable`).join("; ");
      const scope = result.mode === "presets" ? "All predefined fights"
        : result.mode === "pairs" ? "Full 1v1 matrix" : "All-card coverage";
      $("sweep-summary").textContent =
        `${scope}: ` +
        `${result.passed.toLocaleString()} passed, ${result.failed.toLocaleString()} failed, ` +
        `${result.skipped.toLocaleString()} untested after stop, ` +
        `${result.warnings.toLocaleString()} long-draw warnings. ` +
        `${plan.presets_count} source preset patterns included. ${blocked}. ` +
        "Observed runs are not proof that every declared ability activated.";
      const table = document.createElement("table");
      const head = document.createElement("tr");
      for (const title of ["Case", "Edition", "Seed", "Problem"]) {
        const cell = document.createElement("th");
        cell.textContent = title;
        head.append(cell);
      }
      table.append(head);
      for (const failure of result.failures.slice(0, 100)) {
        const row = document.createElement("tr");
        for (const text of [failure.label, failure.selection.ruleset,
          String(failure.seed), failure.problems.join(", ")]) {
          const cell = document.createElement("td");
          cell.textContent = text;
          row.append(cell);
        }
        row.addEventListener("click", () => {
          $("sweep-evidence").textContent = JSON.stringify(failure, null, 2);
        });
        table.append(row);
      }
      $("sweep-failures").replaceChildren(table);
      if (result.failed > result.failures.length) {
        const message = document.createElement("p");
        message.textContent =
          `Showing ${result.failures.length} samples of ${result.failed.toLocaleString()} failures. The JSON contains every failed case number and its error codes.`;
        $("sweep-failures").append(message);
      }
      $("sweep-evidence").textContent = JSON.stringify({
        first_failure: result.failures[0] || null,
        observed_feature_ids: result.observed.feature_ids,
        observed_conditions: result.observed.conditions,
      }, null, 2);
      $("sweep-download").disabled = false;
    } catch (error) {
      console.error("Test All report rendering failed", error);
      throw error;
    }
  }
  async function start() {
    if (running) return;
    const control = {stopRequested: false};
    running = control;
    report = null;
    $("sweep-run").disabled = true;
    $("sweep-stop").disabled = false;
    $("sweep-download").disabled = true;
    $("sweep-failures").replaceChildren();
    $("sweep-summary").textContent = "";
    $("sweep-evidence").textContent = "Collecting actual combat evidence…";
    try {
      const mode = $("sweep-mode").value;
      const seed = Number($("seed").value);
      const plan = await window.IRON_PIT_TEST_ALL_PLAN.create(mode);
      const startCase = Number($("sweep-start").value);
      if (!Number.isInteger(startCase) || startCase < 1 || startCase > plan.total)
        throw new RangeError(`Resume case must be between 1 and ${plan.total}.`);
      control.startIndex = startCase - 1;
      if (!Number.isInteger(seed) || seed < 1 || seed > 0xffffffff)
        throw new RangeError("Select a valid 1–4294967295 seed first.");
      $("sweep-status").textContent =
        `Testing matchups #${startCase.toLocaleString()}–${plan.total.toLocaleString()} across both editions…`;
      report = await window.IRON_PIT_TEST_ALL_RUNNER.run(
        plan, seed, control, interim => {
          report = interim;
          progress(interim, plan);
          $("sweep-download").disabled = false; // live, recoverable checkpoint
        }
      );
      render(report, plan);
      if (report.stopped && report.completed < report.total)
        $("sweep-start").value = String(report.completed + 1);
    } catch (error) {
      console.error("Test All failed before completion", error);
      $("sweep-status").textContent =
        "Test All failed: " + (error?.message || String(error));
    } finally {
      running = null;
      $("sweep-run").disabled = false;
      $("sweep-stop").disabled = true;
    }
  }
  function download() {
    try {
      if (!report) throw new Error("No completed or stopped sweep report.");
      const blob = new Blob([JSON.stringify(report, null, 2)],
        {type: "application/json"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `iron-pit-test-all-${report.mode}-${report.seed}-from-${report.start_case}-through-${report.completed}.json`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (error) {
      console.error("Test All JSON export failed", error);
      $("sweep-status").textContent = "Export failed: " + error.message;
    }
  }
  $("sweep-run").addEventListener("click", () => { void start(); });
  $("sweep-stop").addEventListener("click", () => {
    if (running) running.stopRequested = true;
  });
  $("sweep-download").addEventListener("click", download);
  // Direct navigation from the main Pit is an explicit Test All click.
  // Auto-run only that exact opt-in URL; ordinary visits stay idle.
  try {
    const request = new URLSearchParams(window.location.search);
    if (request.get("run") === "presets") {
      $("sweep-mode").value = "presets";
      void start();
    }
  } catch (error) {
    console.error("Could not read opt-in preset test launch URL", error);
    $("sweep-status").textContent = "Open Test Lab and press Test All Fights.";
  }
})();
