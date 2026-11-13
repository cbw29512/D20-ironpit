(() => {
  "use strict";
  // UI-only state. The source recipes, runner and immutable combatants own
  // the actual matchup and battle; no independent combat rules live here.
  const $ = id => document.getElementById(id);
  const OUTCOMES = new Set(["heroes_win", "monsters_win", "draw"]);
  let runningSingle = false;

  function runPrepared(entry, button, resultEl) {
    if (runningSingle) return;
    runningSingle = true;
    button.disabled = true;
    resultEl.textContent = "Running real seeded combat…";
    resultEl.dataset.result = "";
    try {
      const sourceLookup = window.IRON_PIT_TEST_ALL_RUNNER?.sources;
      const seeded = window.IRON_PIT_BROWSER_TURBO?.runSeeded;
      const aspects = window.IRON_PIT_COMBAT_PRESETS?.aspectFired;
      const fingerprint = window.IRON_PIT_BATTLE_LAB?.fingerprint;
      if (!sourceLookup || !seeded || !aspects || !fingerprint)
        throw new Error("Shared combat/certification modules are unavailable.");
      const originals = sourceLookup(entry.selection)
        .map(([id, card]) => [id, JSON.stringify(card)]);
      const replay = seeded(entry.selection, entry.seed);
      const battle = replay?.battle;
      const events = battle?.events || [];
      const problems = [];
      if (!events.length) problems.push("no_combat_events");
      if (!OUTCOMES.has(battle?.outcome)) problems.push("invalid_outcome");
      if (events.some(event => event.event_type === "movement"))
        problems.push("forbidden_tactical_movement");
      if (entry.required_aspects?.some(spec => !aspects(battle, spec)))
        problems.push("required_mechanic_not_observed");
      if (originals.some(([id, snapshot], index) => {
        const current = sourceLookup(entry.selection)[index];
        return current[0] !== id || JSON.stringify(current[1]) !== snapshot;
      })) problems.push("source_card_mutation");
      if (fingerprint(battle) !== fingerprint(seeded(entry.selection, entry.seed).battle))
        problems.push("seed_replay_mismatch");
      const pass = problems.length === 0;
      resultEl.dataset.result = pass ? "pass" : "fail";
      resultEl.textContent = pass
        ? "PASS · " + battle.rounds + " rounds · " + events.length + " events"
        : "FAIL · " + problems.join(", ");
      $("events").textContent = JSON.stringify({
        label: entry.label, edition: entry.selection.ruleset,
        seed: entry.seed, outcome: battle?.outcome, problems, events,
      }, null, 2);
      $("summary").textContent = resultEl.textContent +
        " · Observed mechanics only; untriggered abilities remain unverified.";
      $("events").scrollIntoView({behavior: "smooth", block: "start"});
    } catch (error) {
      console.error("Prepared Iron Pit combat failed", {entry, error});
      resultEl.dataset.result = "fail";
      resultEl.textContent = "FAIL · " + (error?.message || String(error));
    } finally {
      button.disabled = false;
      runningSingle = false;
    }
  }

  async function renderPresets() {
    const host = $("test-preset-cards");
    const status = $("test-preset-cards-status");
    try {
      const plan = await window.IRON_PIT_TEST_ALL_PLAN.create("presets");
      const recipes = window.IRON_PIT_COMBAT_PRESET_RECIPES?.recipes;
      if (!Array.isArray(recipes) || recipes.length !== plan.total)
        throw new Error("Prepared fights do not match the certified matchup plan.");
      const fragment = document.createDocumentFragment();
      recipes.forEach((recipe, index) => {
        const entry = plan.at(index);
        if (recipe.ruleset !== entry.selection.ruleset)
          throw new Error("A prepared card crossed its ruleset boundary.");
        const card = document.createElement("article");
        card.className = "test-recipe-card";
        const edition = document.createElement("span");
        edition.className = "edition";
        edition.textContent = recipe.ruleset + " · LEVEL " + recipe.level;
        const title = document.createElement("h3");
        title.textContent = recipe.title;
        const matchup = document.createElement("p");
        matchup.textContent = recipe.classes.join(" + ") +
          " vs " + recipe.monsters.join(" + ");
        const purpose = document.createElement("p");
        purpose.textContent = "Checks: " + recipe.purpose;
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "Run this fight";
        const outcome = document.createElement("span");
        outcome.className = "case-result";
        outcome.setAttribute("aria-live", "polite");
        outcome.textContent = "Seed " + entry.seed + " · not yet tested";
        button.addEventListener("click", () => runPrepared(entry, button, outcome));
        card.append(edition, title, matchup, purpose, button, outcome);
        fragment.append(card);
      });
      host.replaceChildren(fragment);
      status.textContent = recipes.length +
        " real, source-backed 2014/2024 battles ready; each card runs the existing engine.";
    } catch (error) {
      console.error("Could not render prepared combat cards", error);
      status.textContent = "Could not load prepared fights: " + error.message;
    }
  }

  function startExisting(kind) {
    try {
      if (!$("bag-stop").disabled || !$("sweep-stop").disabled || runningSingle)
        throw new Error("Finish or stop the active test first.");
      const ids = {bag: "bag-run", pairs: "sweep-run", presets: "all-presets"};
      if (!ids[kind]) throw new Error("Unknown workbench test mode.");
      if (kind === "pairs") $("sweep-mode").value = "pairs";
      if (kind === "presets") $("advanced-tests").open = true;
      $(ids[kind]).click();
      const destination = kind === "bag" ? "bag-panel" :
        kind === "pairs" ? "sweep-panel" : "advanced-tests";
      $(destination).scrollIntoView({behavior: "smooth", block: "start"});
    } catch (error) {
      console.error("Could not start selected test suite", {kind, error});
      $("test-dashboard-status").textContent = error.message;
    }
  }

  $("test-bag-all").addEventListener("click", () => startExisting("bag"));
  $("test-pairs-all").addEventListener("click", () => startExisting("pairs"));
  $("test-presets-all").addEventListener("click", () => startExisting("presets"));
  void renderPresets();
  window.IRON_PIT_TEST_WORKBENCH = {renderPresets};
})();
