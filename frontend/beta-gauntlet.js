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

  function selection(recipe, catalog, presets) {
    const cards = presets.resolve(recipe, catalog);
    return {
      ruleset: recipe.ruleset,
      hero_ids: cards.heroes.map((card) => card.runnable_template_id),
      monster_ids: cards.monsters.map((card) => card.runnable_template_id),
    };
  }

  function validate(replay, recipe, presets, expectedAspects) {
    const battle = replay.battle;
    if (!battle || !Array.isArray(battle.events) || battle.events.length < 1) throw Error("No battle events");
    if (!["heroes_win", "monsters_win", "draw"].includes(battle.outcome)) throw Error("Invalid outcome");
    if (!Number.isInteger(battle.rounds) || battle.rounds < 1 || battle.rounds > 100) throw Error("Invalid round count");
    if (battle.outcome === "draw" && battle.rounds >= 100) throw Error("Safety stop at 100 rounds");
    if (expectedAspects) {
      for (const spec of recipe.aspects) {
        if (!presets.aspectFired(battle, spec)) {
          throw Error("Missing expected " + spec.kind + ": " + JSON.stringify(spec.value));
        }
      }
    }
    return battle.rounds + " rounds, " + battle.events.length + " events, " + battle.outcome;
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
    const recipes = w.IRON_PIT_COMBAT_PRESET_RECIPES.recipes.filter((item) =>
      edition === "both" || item.ruleset === edition);
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
          setup = selection(recipe, catalogs[recipe.ruleset], presets);
        } catch (error) { setupError = error; }
        for (let index = 0; index < count && !stop; index += 1) {
          const testSeed = index === 0 ? recipe.seed : turbo.deriveSeed(seed ^ recipe.seed, index);
          const row = { name: recipe.id, edition: recipe.ruleset, seed: testSeed, index };
          try {
            if (setupError) throw setupError;
            const replay = turbo.runSeeded(setup, testSeed);
            row.result = "PASS"; row.details = validate(replay, recipe, presets, index === 0);
            row.diagnostic_id = replay.diagnostic_id;
            row.outcome = replay.battle.outcome; row.rounds = replay.battle.rounds; passes++;
          } catch (error) {
            row.result = "FAIL"; row.details = error?.message || String(error);
            row.stack = error?.stack || null; failures++;
          }
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
      report.completed = !stop && finished === recipes.length * count;
      report.passed = passes; report.failed = failures;
      running = false; $("start").disabled = false; $("stop").disabled = true;
      $("export").disabled = report.tests.length === 0;
    }
  }

  $("runtime").addEventListener("load", () => {
    try {
      const w = $("runtime").contentWindow;
      if (!w.IRON_PIT_BROWSER_TURBO || !w.IRON_PIT_COMBAT_PRESETS ||
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
