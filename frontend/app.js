(() => {
  "use strict";
  const MAX_SLOTS = 6;
  const state = { catalog: null, heroSlots: Array(MAX_SLOTS).fill(null), monsterSlots: Array(MAX_SLOTS).fill(null), fighting: false, hasRun: false, turboBatch: null, session: null };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;
  const turboView = () => window.IRON_PIT_TURBO_VIEW;
  const actions = () => window.IRON_PIT_BATTLE_ACTIONS;

  function updateControls() {
    const ready = state.heroSlots.some(Boolean) && state.monsterSlots.some(Boolean);
    const active = Boolean(state.session && !state.session.complete);
    for (const id of ["fight-button", "step-fight-button", "turbo-button"]) el(id).disabled = state.fighting || active || !ready;
    el("rerun-button").disabled = state.fighting || active || !state.hasRun;
    el("quick-test").disabled = state.fighting || active; el("reset-fight").disabled = state.fighting;
  }

  function clearResult(message = "Cards loaded. Press FIGHT when both sides are ready.") {
    el("result-panel").hidden = true; el("pit-round").textContent = "";
    el("battle-log").replaceChildren(Object.assign(document.createElement("li"), { textContent: message }));
    el("lab-summary").textContent = "2014 playtest combat path · secure Web Crypto dice.";
  }

  function invalidateRun() {
    state.hasRun = false; state.turboBatch = null; state.session = null; turboView()?.hide();
    actions()?.syncControls(state); updateControls();
  }

  function render() { if (state.catalog) view().render(state, openSlot); updateControls(); actions()?.syncControls(state); }

  function setSlot(side, index, card) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = card; invalidateRun(); clearResult(); render();
  }

  function removeSlot(side, index) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = null; invalidateRun(); clearResult(); render();
  }

  function openSlot(side, index) {
    if (state.fighting || (state.session && !state.session.complete) || !state.catalog) return;
    picker().open(state, side, index, setSlot, removeSlot);
  }

  function selected(side) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots, cards = [], indexes = [];
    slots.forEach((card, index) => { if (card) { cards.push(card); indexes.push(index); } });
    return { cards, indexes };
  }

  function validate(cards, side) {
    if (!cards.length) return `${side === "heroes" ? "Test" : "Monster"} side needs at least one card.`;
    const blocked = cards.find((card) => card.coverage_status !== "raw_ready" || !card.runnable_template_id);
    return blocked ? `${blocked.name} is not certified for this 2014 playtest.` : null;
  }

  function matchup() {
    const heroes = selected("heroes"), monsters = selected("monsters");
    const error = validate(heroes.cards, "heroes") || validate(monsters.cards, "monsters");
    return { heroes, monsters, error, selection: { hero_ids: heroes.cards.map((card) => card.runnable_template_id), monster_ids: monsters.cards.map((card) => card.runnable_template_id) } };
  }

  function resetFight() {
    if (state.fighting) return;
    state.session = null; state.turboBatch = null; turboView().hide(); clearResult("Battle reset. Cards are still loaded.");
    render(); el("status").textContent = "Battle reset. Press FIGHT, STEP FIGHT, or TURBO.";
  }

  function cardByTemplate(side, templateId) {
    const rows = side === "heroes" ? state.catalog.heroes : state.catalog.monsters;
    return rows.find((card) => card.runnable_template_id === templateId && card.coverage_status === "raw_ready") || null;
  }

  function loadSample() {
    if (state.fighting || (state.session && !state.session.complete) || !state.catalog) return;
    const heroes = [cardByTemplate("heroes", "2014-veteran"), cardByTemplate("heroes", "2014-acolyte")];
    const monsters = [cardByTemplate("monsters", "2014-goblin"), cardByTemplate("monsters", "2014-wolf")];
    if ([...heroes, ...monsters].some((card) => !card)) { el("status").textContent = "2014 sample matchup could not find its certified cards."; return; }
    state.heroSlots.fill(null); state.monsterSlots.fill(null);
    heroes.forEach((card, index) => { state.heroSlots[index] = card; }); monsters.forEach((card, index) => { state.monsterSlots[index] = card; });
    invalidateRun(); clearResult("2014 sample loaded: Veteran + Acolyte vs Goblin + Wolf."); render();
    el("status").textContent = "2014 sample loaded. Choose FIGHT, STEP FIGHT, or TURBO.";
  }

  async function boot() {
    try {
      if (window.IRON_PIT_CANONICAL_MONSTERS_READY !== true) throw new Error("Certified 2014 monster bundle did not load.");
      if (window.IRON_PIT_RULESET !== "2014" || window.IRON_PIT_HERO_RULESET !== "2014") throw new Error("Pure 2014 playtest data did not load.");
      const required = [window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER, view(), picker(), window.IRON_PIT_EXECUTION, actions()];
      if (required.some((item) => !item)) throw new Error("Iron Pit browser modules did not load.");
      state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(); picker().bind(() => state);
      actions().install({ state, matchup, render, updateControls, clearResult }); render();
      el("status").textContent = "2014 Iron Pit playtest ready. Choose test cards or load the sample matchup.";
    } catch (error) {
      console.error("Iron Pit initialization failed", error); el("status").textContent = "The 2014 Iron Pit playtest failed to initialize.";
    }
  }

  el("reset-fight").addEventListener("click", resetFight); el("quick-test").addEventListener("click", loadSample);
  boot();
})();
