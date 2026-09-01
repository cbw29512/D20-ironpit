(() => {
  "use strict";
  const MAX_SLOTS = 6;
  const state = { catalog: null, heroSlots: Array(MAX_SLOTS).fill(null), monsterSlots: Array(MAX_SLOTS).fill(null), fighting: false, hasRun: false };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;
  const lab = () => window.IRON_PIT_BATTLE_LAB;
  const dice = () => window.IRON_PIT_DICE;
  function updateControls() {
    el("rerun-button").disabled = state.fighting || !state.hasRun;
    for (const id of ["quick-test", "reset-fight"]) el(id).disabled = state.fighting;
  }
  function clearResult(message = "Cards loaded. Press FIGHT when both sides are ready.") {
    el("result-panel").hidden = true; el("pit-round").textContent = "";
    el("battle-log").replaceChildren(Object.assign(document.createElement("li"), { textContent: message }));
    el("lab-summary").textContent = "Production combat path · secure Web Crypto dice.";
  }
  function invalidateRun() { state.hasRun = false; updateControls(); }
  function render() { if (state.catalog) view().render(state, openSlot); updateControls(); }
  function setSlot(side, index, card) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = card; invalidateRun(); clearResult(); render();
  }
  function removeSlot(side, index) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = null; invalidateRun(); clearResult(); render();
  }
  function openSlot(side, index) {
    if (state.fighting || !state.catalog) return;
    picker().open(state, side, index, setSlot, removeSlot);
  }
  function selected(side) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots, cards = [], indexes = [];
    slots.forEach((card, index) => { if (card) { cards.push(card); indexes.push(index); } });
    return { cards, indexes };
  }
  function validate(cards, side) {
    if (!cards.length) return `${side === "heroes" ? "Hero" : "Monster"} side needs at least one card.`;
    const blocked = cards.find((card) => card.coverage_status !== "raw_ready" || !card.runnable_template_id);
    return blocked ? `${blocked.name} is not RAW-certified for automated combat yet.` : null;
  }
  async function fight() {
    const heroes = selected("heroes"), monsters = selected("monsters");
    const error = validate(heroes.cards, "heroes") || validate(monsters.cards, "monsters");
    if (error) { el("status").textContent = error; return; }
    try {
      state.fighting = true; render(); clearResult(); el("status").textContent = "Rolling initiative…";
      await new Promise((resolve) => requestAnimationFrame(resolve)); dice().clearHistory();
      const heroIds = heroes.cards.map((card) => card.runnable_template_id), monsterIds = monsters.cards.map((card) => card.runnable_template_id);
      const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({ hero_ids: heroIds, monster_ids: monsterIds });
      const rolls = dice().getHistory(), diagnosticId = lab().diagnosticId(heroIds, monsterIds, rolls);
      await window.playIronPitBattle(battle, { heroes: heroes.indexes, monsters: monsters.indexes });
      view().writeLog(battle); view().showResult(battle); state.hasRun = true;
      el("lab-summary").textContent = lab().summary(battle, rolls, diagnosticId);
    } catch (errorCaught) {
      console.error(errorCaught); el("status").textContent = "Fight stopped because a required RAW mechanic is unsupported or the battle engine failed.";
    } finally { state.fighting = false; render(); }
  }
  function resetFight() {
    if (state.fighting) return;
    clearResult("Battle reset. Cards are still loaded."); render();
    el("status").textContent = "Battle reset. Press FIGHT or RUN AGAIN.";
  }
  function cardByTemplate(side, templateId) {
    const rows = side === "heroes" ? state.catalog.heroes : state.catalog.monsters;
    return rows.find((card) => card.runnable_template_id === templateId && card.coverage_status === "raw_ready") || null;
  }
  function loadSample() {
    if (state.fighting || !state.catalog) return;
    const heroes = [cardByTemplate("heroes", "karnok-stoneward-l1"), cardByTemplate("heroes", "seraphine-dawnshield-l1")];
    const monsters = [cardByTemplate("monsters", "srd-goblin-warrior"), cardByTemplate("monsters", "srd-wolf")];
    if ([...heroes, ...monsters].some((card) => !card)) { el("status").textContent = "Sample matchup could not find its certified cards."; return; }
    state.heroSlots.fill(null); state.monsterSlots.fill(null);
    heroes.forEach((card, index) => { state.heroSlots[index] = card; }); monsters.forEach((card, index) => { state.monsterSlots[index] = card; });
    invalidateRun(); clearResult("Sample loaded: Karnok + Seraphine vs Goblin Warrior + Wolf. Press FIGHT to use the normal production combat path.");
    render(); el("status").textContent = "Sample loaded. Press FIGHT.";
  }
  async function boot() {
    if (window.IRON_PIT_CANONICAL_MONSTERS_READY !== true) throw new Error("Canonical RAW-certified monster bundle did not load.");
    const required = [window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER, view(), picker(), lab(), dice()];
    if (required.some((item) => !item) || typeof dice().clearHistory !== "function" || typeof dice().getHistory !== "function") throw new Error("Iron Pit browser modules did not load.");
    state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog();
    picker().bind(() => state); render(); el("status").textContent = "Iron Pit ready. Choose cards or load the sample matchup.";
  }
  el("fight-button").addEventListener("click", fight);
  el("rerun-button").addEventListener("click", fight);
  el("reset-fight").addEventListener("click", resetFight);
  el("quick-test").addEventListener("click", loadSample);
  boot().catch((error) => { console.error(error); el("status").textContent = "The Iron Pit failed to initialize."; });
})();
