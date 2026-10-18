(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let stopping = false, running = false;
  const wait = () => new Promise((resolve) => setTimeout(resolve, 0));
  function runnable(cards) {
    return cards.filter((card) => card.coverage_status === "raw_ready" && card.runnable_template_id);
  }
  async function cases(edition, suite) {
    const out = [], catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(edition);
    if (suite !== "roster") {
      const p = window.IRON_PIT_COMBAT_PRESETS;
      for (const recipe of window.IRON_PIT_COMBAT_PRESET_RECIPES.recipes.filter((x) => x.ruleset === edition)) {
        const cards = p.resolve(recipe, catalog);
        out.push({ label: recipe.title || recipe.id, seed: recipe.seed, recipe,
          selection: { ruleset: edition, hero_ids: cards.heroes.map((x) => x.runnable_template_id),
            monster_ids: cards.monsters.map((x) => x.runnable_template_id) } });
      }
    }
    if (suite !== "presets") {
      const heroes = runnable(catalog.heroes), monsters = runnable(catalog.monsters);
      if (!heroes.length || !monsters.length) throw Error("No runnable " + edition + " cards.");
      for (let i = 0; i < Math.max(heroes.length, monsters.length); i++) {
        out.push({ label: "Roster " + (i + 1), seed: (1701 + i) >>> 0,
          selection: { ruleset: edition,
            hero_ids: [heroes[i % heroes.length].runnable_template_id],
            monster_ids: [monsters[i % monsters.length].runnable_template_id] } });
      }
    }
    return out;
  }
  async function run(presetOnly = false) {
    if (running) return;
    running = true; stopping = false;
    const start = $("beta-run-all"), stop = $("beta-stop-all"), status = $("beta-run-status");
    start.disabled = true; $("beta-run-presets").disabled = true; stop.disabled = false;
    let pass = 0, fail = 0, completed = 0;
    try {
      const edition = presetOnly ? "both" : $("beta-run-edition").value;
      const repeats = Math.min(100, Math.max(1, Number($("beta-repeats").value) || 1));
      const selected = edition === "both"
        ? [...await cases("2014", "presets"), ...await cases("2024", "presets")]
        : await cases(edition, presetOnly ? "presets" : $("beta-suite").value);
      $("beta-run-progress").max = selected.length * repeats;
      for (const test of selected) {
        for (let i = 0; i < repeats && !stopping; i++) {
          const seed = i === 0 ? test.seed :
            window.IRON_PIT_BROWSER_TURBO.deriveSeed(test.seed ^ 1701, i);
          status.textContent = "Fight " + (completed + 1) + "/" +
            (selected.length * repeats) + " · " + test.label;
          let battle = null;
          try {
            battle = window.IRON_PIT_BROWSER_TURBO.runSeeded(test.selection, seed).battle;
            if (!battle?.events?.length) throw Error("No battle events.");
            if (!["heroes_win", "monsters_win", "draw"].includes(battle.outcome)) throw Error("Invalid outcome.");
            if (test.recipe && i === 0) {
              for (const aspect of test.recipe.aspects || []) {
                if (!window.IRON_PIT_COMBAT_PRESETS.aspectFired(battle, aspect)) {
                  throw Error("Expected mechanic absent: " + aspect.kind);
                }
              }
            }
            await window.IRON_PIT_BETA_BRIDGE.showFight(test.selection, battle, seed);
            pass++;
          } catch (error) {
            fail++;
            window.IRON_PIT_BETA_LOG.record(battle, test.selection, seed, error.message);
          }
          completed++;
          $("beta-run-progress").value = completed;
          $("beta-run-counts").textContent = pass + " passed · " + fail + " failed · " +
            completed + " finished";
          await wait();
        }
        if (stopping) break;
      }
      status.textContent = stopping ? "Stopped. Full log retained." : "Complete. Full log retained.";
    } catch (error) {
      status.textContent = "Runner error: " + error.message;
    } finally {
      running = false; start.disabled = false; $("beta-run-presets").disabled = false; stop.disabled = true;
    }
  }
  $("beta-run-all")?.addEventListener("click", () => run(false));
  $("beta-run-presets")?.addEventListener("click", () => run(true));
  $("beta-stop-all")?.addEventListener("click", () => { stopping = true; });
  async function ready() {
    for (let i = 0; i < 200; i++) {
      if (window.IRON_PIT_BETA_BRIDGE?.ready() && window.IRON_PIT_BETA_LOG) {
        $("beta-run-all").disabled = false;
        $("beta-run-presets").disabled = false;
        $("beta-run-status").textContent = "2014 beta runner ready.";
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    $("beta-run-status").textContent = "Beta runner unavailable; reload or check engine startup.";
  }
  ready();
})();
