(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let runtime = null, stop = false, running = false, report = null;
  const pause = () => new Promise((resolve) => setTimeout(resolve, 0));
  function issue(row, status, details) {
    const tr = document.createElement("tr");
    for (const value of [row.name, row.edition, row.seed, status, details]) {
      const td = document.createElement("td");
      td.textContent = String(value);
      if (value === status) td.className = status === "PASS" ? "pass" : "fail";
      tr.append(td);
    }
    $("rows").append(tr);
  }

  function showFamilies(tests) {
    const summary = window.IRON_PIT_BETA_GAUNTLET_ASSERTIONS.aggregate(tests);
    const observed = Object.values(summary).filter((entry) => entry.fights > 0).length;
    $("family-summary").textContent = observed + " / " + Object.keys(summary).length +
      " combat behavior categories observed in successful fights.";
    $("family-rows").replaceChildren();
    for (const [name, entry] of Object.entries(summary)) {
      const tr = document.createElement("tr");
      const values = [name, entry.fights, entry.sample
        ? entry.sample.preset + " / " + entry.sample.edition + " / seed " + entry.sample.seed
        : "Not observed"];
      for (const value of values) {
        const td = document.createElement("td"); td.textContent = String(value); tr.append(td);
      }
      $("family-rows").append(tr);
    }
    return summary;
  }

  function showCoverage(recipes, tests) {
    const matrix = window.IRON_PIT_BETA_GAUNTLET_COVERAGE.coverage(recipes, tests);
    const evidenced = matrix.filter((entry) => entry.coverage === "asserted in passing preset").length;
    $("coverage-summary").textContent = evidenced + " / " + matrix.length +
      " capabilities have explicit passing preset evidence. Remaining capabilities require targeted tests.";
    $("coverage-rows").replaceChildren();
    for (const entry of matrix) {
      const tr = document.createElement("tr");
      for (const value of [entry.id, entry.status, entry.coverage]) {
        const td = document.createElement("td");
        td.textContent = value;
        tr.append(td);
      }
      $("coverage-rows").append(tr);
    }
    return matrix;
  }

  async function execute() {
    if (!runtime || running) return;
    running = true; stop = false; $("start").disabled = true; $("stop").disabled = false;
    $("export").disabled = true; $("rows").replaceChildren();
    const count = Number($("count").value), seed = Number($("seed").value);
    if (!Number.isInteger(count) || count < 1 || count > 100 || !Number.isInteger(seed)
      || seed < 0 || seed > 0xffffffff) {
      $("status").textContent = "Enter 1–100 fights per preset and a 32-bit unsigned seed.";
      running = false; $("start").disabled = false; $("stop").disabled = true; return;
    }
    const w = runtime, turbo = w.IRON_PIT_BROWSER_TURBO, presets = w.IRON_PIT_COMBAT_PRESETS;
    const edition = $("edition").value;
    const editions = edition === "both" ? ["2014", "2024"] : [edition];
    const suite = $("suite").value;
    let recipes;
    try {
      recipes = suite === "roster" ? [] : w.IRON_PIT_COMBAT_PRESET_RECIPES.recipes.filter((item) =>
        editions.includes(item.ruleset));
      if (suite !== "presets") recipes.push(...await window.IRON_PIT_BETA_GAUNTLET_CASES.rosterSweep(w, editions));
    } catch (error) {
      $("status").textContent = "Test roster unavailable: " + error.message;
      running = false; $("start").disabled = false; $("stop").disabled = true; return;
    }
    report = { timestamp: new Date().toISOString(), base_seed: seed, edition, fights_per_preset: count,
      tests: [], environment: location.href };
    const catalogs = {};
    let finished = 0, passes = 0, failures = 0;
    $("progress").max = recipes.length * count; $("progress").value = 0;
    try {
      for (const recipe of recipes) {
        if (stop) break;
        let setup, setupError;
        try {
          catalogs[recipe.ruleset] ||= await w.IRON_PIT_BROWSER_CATALOG.buildCatalog(recipe.ruleset);
          setup = recipe.selection || window.IRON_PIT_BETA_GAUNTLET_CASES.selection(recipe, catalogs[recipe.ruleset], presets);
        } catch (error) { setupError = error; }
        for (let index = 0; index < count && !stop; index += 1) {
          const testSeed = index === 0 ? recipe.seed : turbo.deriveSeed(seed ^ recipe.seed, index);
          const row = { name: recipe.id, edition: recipe.ruleset, seed: testSeed, index };
          let replay = null;
          try {
            if (setupError) throw setupError;
            replay = turbo.runSeeded(setup, testSeed);
            row.details = window.IRON_PIT_BETA_GAUNTLET_CASES.validate(replay, recipe, presets, index === 0 && !recipe.selection);
            row.observed = window.IRON_PIT_BETA_GAUNTLET_ASSERTIONS.inspect(replay.battle);
            row.result = "PASS";
            row.diagnostic_id = replay.diagnostic_id;
            row.outcome = replay.battle.outcome; row.rounds = replay.battle.rounds;
            row.events = replay.battle.events;
            if ($("watch").checked) {
              $("status").textContent = "Watching " + recipe.id + " (" + (index + 1) + "/" + count + ")";
              try {
                await window.IRON_PIT_BETA_SPECTATOR.play(replay.battle, recipe, testSeed);
              } catch (playbackError) {
                row.playback_error = playbackError?.message || String(playbackError);
              }
            }
          } catch (error) {
            row.result = "FAIL"; row.details = error?.message || String(error);
            row.stack = error?.stack || null;
            if (replay?.battle?.events) row.events = replay.battle.events;
          }
          if (row.result === "PASS") passes++; else failures++;
          report.tests.push(row); finished++; $("progress").value = finished;
          issue(row, row.result, row.details);
          $("totals").textContent = passes + " passed / " + failures + " failed / " + finished + " run";
          $("status").textContent = "Testing " + recipe.id + " (" + (index + 1) + "/" + count + ")";
          await pause();
        }
      }
      $("status").textContent = stop ? "Stopped; partial report available." : "Completed all requested fights.";
    } catch (error) {
      $("status").textContent = "Runner failure: " + (error?.message || String(error));
      console.error("Fight gauntlet failed", error);
    } finally {
      report.capability_coverage = showCoverage(recipes, report.tests);
      report.observed_behaviors = showFamilies(report.tests);
      report.completed = !stop && finished === recipes.length * count;
      report.passed = passes; report.failed = failures;
      running = false; $("start").disabled = false; $("stop").disabled = true;
      $("export").disabled = report.tests.length === 0;
    }
  }

  $("runtime").addEventListener("load", async () => {
    for (let i = 0; i < 100 && !$("runtime").contentWindow?.IRON_PIT_BROWSER_TURBO; i++) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    try {
      const w = $("runtime").contentWindow;
      if (!w.IRON_PIT_BROWSER_TURBO || !window.IRON_PIT_BETA_SPECTATOR || !w.IRON_PIT_COMBAT_PRESETS ||
        !w.IRON_PIT_COMBAT_PRESET_RECIPES || !w.IRON_PIT_BROWSER_CATALOG) {
        throw Error("Site runtime or test presets did not initialize.");
      }
      runtime = w; $("start").disabled = false; $("start").textContent = "Run all fights";
      $("status").textContent = "Ready — run all fight presets.";
    } catch (error) {
      $("status").textContent = "Runtime unavailable: " + (error?.message || String(error));
    }
  });
  $("start").addEventListener("click", execute);
  $("stop").addEventListener("click", () => { stop = true; $("status").textContent = "Stopping after current fight…"; });
  $("export").addEventListener("click", () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob); link.download = "ironpit-beta-gauntlet.json";
    link.click(); setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  });
})();
