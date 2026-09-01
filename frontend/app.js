(() => {
  "use strict";

  const MAX_SLOTS = 6;
  const state = {
    catalog: null,
    heroSlots: Array(MAX_SLOTS).fill(null),
    monsterSlots: Array(MAX_SLOTS).fill(null),
    fighting: false,
    lastScenarioKey: null,
    lastFingerprint: null,
  };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;
  const lab = () => window.IRON_PIT_BATTLE_LAB;
  const secureDice = window.IRON_PIT_DICE;

  function updateLabControls() {
    const rerun = el("rerun-button");
    if (rerun) rerun.disabled = state.fighting || !state.lastScenarioKey;
    for (const id of ["quick-test", "reset-fight", "battle-seed", "instant-mode"]) {
      const node = el(id); if (node) node.disabled = state.fighting;
    }
  }

  function clearResult(message = "Cards loaded. Press FIGHT when both sides are ready.") {
    el("result-panel").hidden = true; el("pit-round").textContent = "";
    el("battle-log").replaceChildren(Object.assign(document.createElement("li"), { textContent: message }));
    if (el("lab-summary")) el("lab-summary").textContent = "Choose a seed to reproduce a fight exactly; leave it blank for secure random dice.";
  }

  function invalidateReplay() {
    state.lastScenarioKey = null; state.lastFingerprint = null; updateLabControls();
  }

  function render() {
    if (state.catalog) view().render(state, openSlot);
    updateLabControls();
  }

  function setSlot(side, index, card) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = card; invalidateReplay(); clearResult(); render();
  }

  function removeSlot(side, index) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = null; invalidateReplay(); clearResult(); render();
  }

  function openSlot(side, index) {
    if (state.fighting || !state.catalog) return;
    picker().open(state, side, index, setSlot, removeSlot);
  }

  function selected(side) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    const cards = [], indexes = [];
    slots.forEach((card, index) => { if (card) { cards.push(card); indexes.push(index); } });
    return { cards, indexes };
  }

  function validate(cards, side) {
    if (!cards.length) return `${side === "heroes" ? "Hero" : "Monster"} side needs at least one card.`;
    const blocked = cards.find((card) => card.coverage_status !== "raw_ready" || !card.runnable_template_id);
    return blocked ? `${blocked.name} is not RAW-certified for automated combat yet.` : null;
  }

  function scenarioKey(heroes, monsters, seed) {
    return JSON.stringify({
      hero_ids: heroes.cards.map((card) => card.runnable_template_id),
      monster_ids: monsters.cards.map((card) => card.runnable_template_id),
      seed,
    });
  }

  function configureDice(seed) {
    window.IRON_PIT_DICE = seed ? lab().createSeededDice(seed) : secureDice;
  }

  async function fight() {
    const heroes = selected("heroes"), monsters = selected("monsters");
    const error = validate(heroes.cards, "heroes") || validate(monsters.cards, "monsters");
    if (error) { el("status").textContent = error; return; }
    const seed = el("battle-seed").value.trim();
    const key = scenarioKey(heroes, monsters, seed);
    const previousFingerprint = seed && state.lastScenarioKey === key ? state.lastFingerprint : null;
    try {
      state.fighting = true; render(); clearResult();
      el("status").textContent = seed ? `Running reproducible seed ${seed}…` : "Rolling initiative…";
      await new Promise((resolve) => requestAnimationFrame(resolve));
      configureDice(seed);
      const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
        hero_ids: heroes.cards.map((card) => card.runnable_template_id),
        monster_ids: monsters.cards.map((card) => card.runnable_template_id),
      });
      const currentFingerprint = lab().fingerprint(battle);
      let replayStatus = "";
      if (previousFingerprint) replayStatus = previousFingerprint === currentFingerprint
        ? "exact replay reproduced" : "REPLAY MISMATCH — investigate engine nondeterminism";
      await window.playIronPitBattle(
        battle,
        { heroes: heroes.indexes, monsters: monsters.indexes },
        { instant: el("instant-mode").checked },
      );
      view().writeLog(battle); view().showResult(battle);
      state.lastScenarioKey = key; state.lastFingerprint = currentFingerprint;
      el("lab-summary").textContent = lab().summary(battle, seed, replayStatus);
      if (replayStatus.startsWith("REPLAY MISMATCH")) el("status").textContent = replayStatus;
    } catch (errorCaught) {
      console.error(errorCaught); el("status").textContent = "Fight stopped because a required RAW mechanic is unsupported or the battle engine failed.";
    } finally {
      window.IRON_PIT_DICE = secureDice;
      state.fighting = false; render();
    }
  }

  function resetFight() {
    if (state.fighting) return;
    clearResult("Battle reset. Cards and test seed are still loaded.");
    render(); el("status").textContent = "Battle reset. Press FIGHT or RUN AGAIN.";
  }

  function cardByTemplate(side, templateId) {
    const rows = side === "heroes" ? state.catalog.heroes : state.catalog.monsters;
    return rows.find((card) => card.runnable_template_id === templateId && card.coverage_status === "raw_ready") || null;
  }

  async function quickTest() {
    if (state.fighting || !state.catalog) return;
    const heroes = [cardByTemplate("heroes", "karnok-stoneward-l1"), cardByTemplate("heroes", "seraphine-dawnshield-l1")];
    const monsters = [cardByTemplate("monsters", "srd-goblin-warrior"), cardByTemplate("monsters", "srd-wolf")];
    if ([...heroes, ...monsters].some((card) => !card)) {
      el("status").textContent = "Quick Test could not find its certified smoke-test cards."; return;
    }
    state.heroSlots.fill(null); state.monsterSlots.fill(null);
    heroes.forEach((card, index) => { state.heroSlots[index] = card; });
    monsters.forEach((card, index) => { state.monsterSlots[index] = card; });
    el("battle-seed").value = "iron-pit-smoke-1";
    el("instant-mode").checked = true;
    invalidateReplay(); clearResult("Quick Test loaded: Karnok + Seraphine vs Goblin Warrior + Wolf."); render();
    await fight();
  }

  async function boot() {
    if (window.IRON_PIT_CANONICAL_MONSTERS_READY !== true) {
      throw new Error("Canonical RAW-certified monster bundle did not load.");
    }
    const required = [
      window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER,
      view(), picker(), lab(), secureDice,
    ];
    if (required.some((item) => !item)) throw new Error("Iron Pit browser modules did not load.");
    state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog();
    picker().bind(() => state); render();
    el("status").textContent = "Battle Lab ready. Choose cards or hit QUICK TEST.";
  }

  el("fight-button").addEventListener("click", fight);
  el("rerun-button").addEventListener("click", fight);
  el("reset-fight").addEventListener("click", resetFight);
  el("quick-test").addEventListener("click", quickTest);
  el("battle-seed").addEventListener("input", invalidateReplay);
  boot().catch((error) => { console.error(error); el("status").textContent = "The Iron Pit failed to initialize."; });
})();
