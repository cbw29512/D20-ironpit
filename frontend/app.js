(() => {
  "use strict";

  const state = { catalog: null, heroSlots: [], heroCards: [], heroes: [], monsters: [], monsterCr: "all", monsterChoice: null, fighting: false };
  const el = (id) => document.getElementById(id);
  const view = window.createEncounterView();
  const pickerView = window.createEncounterPickerView();
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;

  function runtimeCard(card, side) {
    return {
      id: card.runnable_template_id, catalog_id: card.id, name: card.name,
      archetype: side === "heroes" ? card.class_name : card.monster_type,
      level: card.level || null, build_name: card.build_name || null,
      challenge_rating: card.challenge_rating || null, coverage_status: card.coverage_status,
    };
  }

  function clearBattleState() {
    for (const card of [...state.heroCards, ...state.monsters]) {
      delete card.combatant_id; delete card.battle_status; delete card.current_hp; delete card.max_hp;
    }
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

  function removeMonster(index) { state.monsters.splice(index, 1); clearBattleState(); render(); }

  function render() {
    const ready = Boolean(window.IRON_PIT_BROWSER_ENGINE && state.catalog && !state.fighting);
    view.renderSelection(state, ready, removeMonster);
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
    state.heroSlots.length = count; syncHeroes(); clearBattleState(); render();
  }

  function updateHeroSlot(index, patch) {
    state.heroSlots[index] = P().normalizedSlot(state.catalog.heroes, state.heroSlots[index], patch);
    syncHeroes(); clearBattleState(); render();
  }

  function addMonster() {
    if (state.monsters.length >= 8 || !state.catalog) return;
    const chosen = state.catalog.monsters.find((item) => item.id === state.monsterChoice);
    if (!chosen || chosen.coverage_status !== "raw_ready" || !chosen.runnable_template_id) return;
    clearBattleState(); state.monsters.push(runtimeCard(chosen, "monsters")); render();
  }

  function bindCards(battle) {
    const bind = (cards, members) => members.forEach((member, index) => {
      const card = cards[index]; if (!card) return;
      card.combatant_id = member.combatant_id; card.max_hp = member.state.template.max_hp;
      card.current_hp = member.state.template.max_hp; card.battle_status = "ALIVE";
    });
    bind(state.heroCards, battle.setup.heroes); bind(state.monsters, battle.setup.monsters); render();
  }

  function replayCardEvent(event) {
    if (event.hp_after == null && !event.is_dead) return;
    const id = event.target_id || event.actor_id;
    const card = [...state.heroCards, ...state.monsters].find((item) => item.combatant_id === id);
    if (!card) return;
    if (event.hp_after != null) card.current_hp = event.hp_after;
    card.battle_status = event.is_dead ? "DEAD" : card.current_hp === 0 ? "DOWN" : "ALIVE";
    view.renderSelection(state, false, removeMonster);
  }

  async function fight() {
    if (state.heroes.length !== state.heroSlots.length) {
      view.setStatus("Every character slot must use a RAW-certified pregen before fighting."); return;
    }
    try {
      state.fighting = true; clearBattleState(); render(); el("result-panel").hidden = true;
      view.setStatus("Rolling initiative. Entering the Pit…");
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
        hero_ids: state.heroes.map((item) => item.id), monster_ids: state.monsters.map((item) => item.id),
        starting_distance_ft: Number(el("distance").value),
      });
      if (!window.playIronPitBattle) throw new Error("Battle replay system did not load.");
      bindCards(battle); await window.playIronPitBattle(battle, replayCardEvent); view.showResult(battle);
    } catch (error) {
      console.error(error); view.setStatus("Fight failed locally. Check the battle log/console for the blocked mechanic.");
    } finally { state.fighting = false; render(); }
  }

  async function boot() {
    if (!window.IRON_PIT_BROWSER_ENGINE || !window.IRON_PIT_BROWSER_CATALOG || !window.IRON_PIT_ENCOUNTER_PICKER) throw new Error("Browser combat engine did not load.");
    state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog();
    state.heroSlots = [defaultHeroSlot()]; syncHeroes();
    view.setStatus("Pit ready · choose 1–6 individual character cards, then add monster cards by CR."); render();
  }

  el("add-monster").addEventListener("click", addMonster);
  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => { console.error(error); view.setStatus("Browser combat engine failed to initialize."); render(); });
})();
