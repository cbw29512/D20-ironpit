(() => {
  "use strict";

  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const state = { catalog: null, heroes: [], monsters: [] };
  const el = (id) => document.getElementById(id);
  const view = window.createEncounterView();

  function render() {
    view.renderSelection(state, Boolean(apiBase), (side, index) => {
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
      view.setStatus("Rolling initiative and resolving the fight…");
      const response = await fetch(`${apiBase}/api/encounters/fight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hero_ids: state.heroes.map((item) => item.id),
          monster_ids: state.monsters.map((item) => item.id),
          starting_distance_ft: Number(el("distance").value),
        }),
      });
      if (!response.ok) throw new Error(`Fight API returned ${response.status}`);
      const battle = await response.json();
      view.showResult(battle);
      await window.playIronPitCriticalEffects?.(battle);
    } catch (error) {
      console.error(error);
      view.setStatus("Fight failed. The production API may still be deploying.");
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
    if (!apiBase) {
      view.setStatus("Production API is not configured.");
      render();
      return;
    }
    const response = await fetch(`${apiBase}/api/catalog`);
    if (!response.ok) throw new Error(`Catalog API returned ${response.status}`);
    state.catalog = await response.json();
    view.fillPicker("hero-picker", state.catalog.heroes);
    view.fillPicker("monster-picker", state.catalog.monsters);
    seedReadyCard("heroes");
    seedReadyCard("monsters");
    view.setStatus(`Loaded ${state.catalog.hero_count} hero builds and ${state.catalog.monster_count} SRD monsters.`);
    render();
  }

  el("add-hero").addEventListener("click", () => addSelected("heroes"));
  el("add-monster").addEventListener("click", () => addSelected("monsters"));
  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => {
    console.error(error);
    view.setStatus("Catalog failed to load from production API.");
    render();
  });
})();
