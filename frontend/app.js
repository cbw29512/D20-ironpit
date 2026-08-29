(() => {
  "use strict";

  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const state = { catalog: null, heroes: [], monsters: [], apiReady: false };
  const el = (id) => document.getElementById(id);
  const view = window.createEncounterView();

  function render() {
    view.renderSelection(state, state.apiReady, (side, index) => {
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

  async function fetchWithTimeout(url, options = {}, timeoutMs = 20000) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await fetch(url, { ...options, signal: controller.signal, cache: "no-store" });
    } finally {
      window.clearTimeout(timer);
    }
  }

  async function requireHealthyApi() {
    if (!apiBase) throw new Error("Production API base is blank.");
    view.setStatus("Waking the production combat engine…");
    const response = await fetchWithTimeout(`${apiBase}/health`, {}, 45000);
    if (!response.ok) throw new Error(`Health API returned ${response.status}`);
    const health = await response.json();
    if (health.status !== "ok") throw new Error("Production API health check failed.");
  }

  async function fight() {
    try {
      state.apiReady = false;
      render();
      view.setStatus("Rolling initiative and resolving the fight…");
      const response = await fetchWithTimeout(`${apiBase}/api/encounters/fight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hero_ids: state.heroes.map((item) => item.id),
          monster_ids: state.monsters.map((item) => item.id),
          starting_distance_ft: Number(el("distance").value),
        }),
      }, 60000);
      if (!response.ok) throw new Error(`Fight API returned ${response.status}`);
      const battle = await response.json();
      view.showResult(battle);
      await window.playIronPitCriticalEffects?.(battle);
      state.apiReady = true;
    } catch (error) {
      console.error(error);
      view.setStatus("Fight failed. Production API is unavailable or still waking up.");
      try {
        await requireHealthyApi();
        state.apiReady = true;
      } catch (healthError) {
        console.error(healthError);
      }
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
    await requireHealthyApi();
    view.setStatus("Production API online. Loading certified cards…");
    const response = await fetchWithTimeout(`${apiBase}/api/catalog`);
    if (!response.ok) throw new Error(`Catalog API returned ${response.status}`);
    state.catalog = await response.json();
    view.fillPicker("hero-picker", state.catalog.heroes);
    view.fillPicker("monster-picker", state.catalog.monsters);
    seedReadyCard("heroes");
    seedReadyCard("monsters");
    state.apiReady = true;
    view.setStatus(`Production ready · ${state.catalog.hero_count} hero builds · ${state.catalog.monster_count} SRD monsters cataloged.`);
    render();
  }

  el("add-hero").addEventListener("click", () => addSelected("heroes"));
  el("add-monster").addEventListener("click", () => addSelected("monsters"));
  el("fight-button").addEventListener("click", fight);
  render();
  boot().catch((error) => {
    console.error(error);
    state.apiReady = false;
    view.setStatus("Production combat engine is offline. FIGHT is disabled until health checks pass.");
    render();
  });
})();
