(() => {
  "use strict";

  const state = { catalog: null, heroes: [], monsters: [] };
  const el = (id) => document.getElementById(id);
  const view = window.createEncounterView();

  function render() {
    const ready = Boolean(window.IRON_PIT_BROWSER_ENGINE && state.catalog);
    view.renderSelection(state, ready, (side, index) => {
      state[side].splice(index, 1);
      render();
    });
  }

  function runtimeCard(card, side) {
    return {
      id: card.runnable_template_id,
      catalog_id: card.id,
      name: card.name,
      archetype: side === "heroes" ? card.class_name : card.monster_type,
      level: card.level || null,
      build_name: card.build_name || null,
      challenge_rating: card.challenge_rating || null,
      coverage_status: card.coverage_status,
    };
  }

  function addSelected(side) {
    if (state[side].length >= 8 || !state.catalog) return;
    const pickerId = side === "heroes" ? "hero-picker" : "monster-picker";
    const source = side === "heroes" ? state.catalog.heroes : state.catalog.monsters;
    const chosen = source.find((item) => item.id === el(pickerId).value);
    if (!chosen) return;
    if (chosen.coverage_status !== "raw_ready" || !chosen.runnable_template_id) {
      view.setStatus(`${chosen.name} is cataloged but not RAW-certified for automated fights yet.`);
      return;
    }
    state[side].push(runtimeCard(chosen, side));
    render();
  }

  async function fight() {
    try {
      el("fight-button").disabled = true;
      el("result-panel").hidden = true;
      view.setStatus("Rolling initiative. Entering the Pit…");
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
        hero_ids: state.heroes.map((item) => item.id),
        monster_ids: state.monsters.map((item) => item.id),
        starting_distance_ft: Number(el("distance").value),
      });
      if (!window.playIronPitBattle) throw new Error("Battle replay system did not load.");
      await window.playIronPitBattle(battle);
      view.showResult(battle);
    } catch (error) {
      console.error(error);
      view.setStatus("Fight failed locally. Check the battle log/console for the blocked mechanic.");
    } finally {
      render();
    }
  }

  function seedReadyCard(side) {
    const source = side === "heroes" ? state.catalog.heroes : state.catalog.monsters;
    const card = source.find((item) => item.coverage_status === "raw_ready" && item.runnable_template_id);
    if (card) state[side].push(runtimeCard(card, side));
  }

  async function boot() {
    if (!window.IRON_PIT_BROWSER_ENGINE || !window.IRON_PIT_BROWSER_CATALOG) throw new Error("Browser combat engine did not load.");
    state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog();
    view.fillPicker("hero-picker", state.catalog.heroes);
    view.fillPicker("monster-picker", state.catalog.monsters);
    seedReadyCard("heroes");
    seedReadyCard("monsters");
    view.setStatus(`Pit ready · ${state.catalog.hero_count} hero builds · ${state.catalog.monster_count} SRD monsters cataloged.`);
    render();
  }

  el("add-hero").addEventListener("click", () => addSelected("heroes"));
  el("add-monster").addEventListener("click", () => addSelected("monsters"));
  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => {
    console.error(error);
    view.setStatus("Browser combat engine failed to initialize.");
    render();
  });
})();
