(() => {
  "use strict";

  const state = { catalog: null, heroSlots: [], heroCards: [], heroes: [], monsters: [], monsterCr: "all", monsterChoice: null };
  const el = (id) => document.getElementById(id);
  const view = window.createEncounterView();
  const pickerView = window.createEncounterPickerView();
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;

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

  function syncHeroes() {
    const chosen = state.heroSlots.map((slot) => P().cardForSlot(state.catalog.heroes, slot)).filter(Boolean);
    state.heroCards = chosen.map((card) => runtimeCard(card, "heroes"));
    state.heroes = state.heroCards.filter((card) => card.coverage_status === "raw_ready" && card.id);
  }

  function defaultHeroSlot() {
    const ready = state.catalog.heroes.find((hero) => hero.coverage_status === "raw_ready" && hero.runnable_template_id);
    if (!ready) return P().normalizedSlot(state.catalog.heroes);
    return P().normalizedSlot(state.catalog.heroes, {}, { class_id: ready.class_id, level: ready.level, card_id: ready.id });
  }

  function render() {
    const ready = Boolean(window.IRON_PIT_BROWSER_ENGINE && state.catalog);
    view.renderSelection(state, ready, (index) => {
      state.monsters.splice(index, 1); render();
    });
    if (!state.catalog) return;
    pickerView.renderParty(state, setPartySize, updateHeroSlot);
    state.monsterChoice = pickerView.renderMonsterFilters(
      state,
      (value) => { state.monsterCr = value; state.monsterChoice = null; render(); },
      (value) => { state.monsterChoice = value; },
    );
  }

  function setPartySize(value) {
    const count = Math.max(1, Math.min(6, Number(value) || 1));
    while (state.heroSlots.length < count) state.heroSlots.push(defaultHeroSlot());
    state.heroSlots.length = count;
    syncHeroes(); render();
  }

  function updateHeroSlot(index, patch) {
    state.heroSlots[index] = P().normalizedSlot(state.catalog.heroes, state.heroSlots[index], patch);
    syncHeroes(); render();
  }

  function addMonster() {
    if (state.monsters.length >= 8 || !state.catalog) return;
    const chosen = state.catalog.monsters.find((item) => item.id === state.monsterChoice);
    if (!chosen) return;
    if (chosen.coverage_status !== "raw_ready" || !chosen.runnable_template_id) {
      view.setStatus(`${chosen.name} is cataloged but not RAW-certified for automated fights yet.`); return;
    }
    state.monsters.push(runtimeCard(chosen, "monsters")); render();
  }

  async function fight() {
    if (state.heroes.length !== state.heroSlots.length) {
      view.setStatus("Every character slot must use a RAW-certified class/level build before fighting."); return;
    }
    try {
      el("fight-button").disabled = true; el("result-panel").hidden = true;
      view.setStatus("Rolling initiative. Entering the Pit…");
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
        hero_ids: state.heroes.map((item) => item.id),
        monster_ids: state.monsters.map((item) => item.id),
        starting_distance_ft: Number(el("distance").value),
      });
      if (!window.playIronPitBattle) throw new Error("Battle replay system did not load.");
      await window.playIronPitBattle(battle); view.showResult(battle);
    } catch (error) {
      console.error(error); view.setStatus("Fight failed locally. Check the battle log/console for the blocked mechanic.");
    } finally { render(); }
  }

  async function boot() {
    if (!window.IRON_PIT_BROWSER_ENGINE || !window.IRON_PIT_BROWSER_CATALOG || !window.IRON_PIT_ENCOUNTER_PICKER) {
      throw new Error("Browser combat engine did not load.");
    }
    state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog();
    state.heroSlots = [defaultHeroSlot()]; syncHeroes();
    view.setStatus("Pit ready · choose 1–6 characters, then add RAW-certified monsters by CR."); render();
  }

  el("add-monster").addEventListener("click", addMonster);
  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => {
    console.error(error); view.setStatus("Browser combat engine failed to initialize."); render();
  });
})();
