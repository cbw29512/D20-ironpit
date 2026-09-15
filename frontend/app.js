(() => {
  "use strict";
  const MAX_SLOTS = 6;
  const state = { catalog: null, heroSlots: Array(MAX_SLOTS).fill(null), monsterSlots: Array(MAX_SLOTS).fill(null), fighting: false, hasRun: false, turboBatch: null, session: null };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;
  const turboView = () => window.IRON_PIT_TURBO_VIEW;
  const actions = () => window.IRON_PIT_BATTLE_ACTIONS;

  function applyPlaytestShell() {
    document.title = "The Iron Pit — D&D 5e 2014 Combat Engine Beta";
    const hero = document.querySelector(".compact-hero");
    if (hero) {
      const eyebrows = hero.querySelectorAll(".eyebrow");
      if (eyebrows[1]) eyebrows[1].textContent = "D&D 5e 2014 · SRD PLAYTEST";
      const intro = hero.querySelector("p strong");
      if (intro) intro.textContent = "D&D 5e (2014) rules-engine playtest.";
      const notes = hero.querySelectorAll(".rules-note");
      if (notes[0]) notes[0].innerHTML = "<strong>Beta build:</strong> certified 2014 monsters plus four temporary SRD test heroes. Final player pregens come after the 2014 engine is verified.";
      if (notes[1]) notes[1].innerHTML = "<strong>Simulation note:</strong> Iron Pit automates combat consistently using the 2014 rules baseline. Complex edge cases may use documented arena simplifications while the engine is being certified.";
    }
    const heroHeading = document.querySelector(".hero-field .field-heading span");
    if (heroHeading) heroHeading.textContent = "2014 TEST HEROES";
    const monsterHeading = document.querySelector(".monster-field .field-heading span");
    if (monsterHeading) monsterHeading.textContent = "CERTIFIED MONSTERS";
    const kicker = document.querySelector(".lab-kicker");
    if (kicker) kicker.textContent = "2014 BETA";
    const logNote = document.querySelector(".log-panel .rules-note");
    if (logNote) logNote.textContent = "D&D 5e 2014 playtest · expand RULES AUDIT for engine details";
    const firstLog = el("battle-log")?.querySelector("li");
    if (firstLog) firstLog.textContent = "Load the sample fight or click an empty card slot to choose combatants.";
  }

  function installTestGuide() {
    const battlefield = document.querySelector(".battlefield");
    if (!battlefield || document.getElementById("beta-test-guide")) return;
    const guide = document.createElement("section");
    guide.id = "beta-test-guide";
    guide.className = "beta-test-guide";
    guide.innerHTML = "<strong>PLAYTEST LOOP</strong><span><b>1</b> Load Sample or choose cards</span><span><b>2</b> FIGHT for a full battle</span><span><b>3</b> STEP FIGHT to inspect decisions</span><span><b>4</b> Copy the log if something looks wrong</span>";
    battlefield.before(guide);
  }

  async function copyBattleLog() {
    const rows = [...el("battle-log").querySelectorAll("li")].map((node) => node.innerText.trim()).filter(Boolean);
    const text = rows.join("\n\n");
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      el("status").textContent = "Battle log copied. Paste it into ChatGPT with what looked wrong.";
    } catch (error) {
      console.error("Battle log copy failed", error);
      el("status").textContent = "Could not copy automatically. Select the Battle Log text and copy it manually.";
    }
  }

  function installCopyLogButton() {
    const actionsRoot = document.querySelector(".lab-actions");
    if (!actionsRoot || el("copy-battle-log")) return;
    const button = document.createElement("button");
    button.id = "copy-battle-log";
    button.type = "button";
    button.textContent = "COPY LOG";
    button.addEventListener("click", copyBattleLog);
    actionsRoot.append(button);
  }

  function updateControls() {
    const ready = state.heroSlots.some(Boolean) && state.monsterSlots.some(Boolean);
    const active = Boolean(state.session && !state.session.complete);
    for (const id of ["fight-button", "step-fight-button", "turbo-button"]) el(id).disabled = state.fighting || active || !ready;
    el("rerun-button").disabled = state.fighting || active || !state.hasRun;
    el("quick-test").disabled = state.fighting || active; el("reset-fight").disabled = state.fighting;
    if (el("copy-battle-log")) el("copy-battle-log").disabled = !el("battle-log")?.children.length;
  }

  function clearResult(message = "Cards loaded. Press FIGHT when both sides are ready.") {
    el("result-panel").hidden = true; el("pit-round").textContent = "";
    el("battle-log").replaceChildren(Object.assign(document.createElement("li"), { textContent: message }));
    el("lab-summary").textContent = "2014 rules engine · certified roster · secure Web Crypto dice.";
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
    el("status").textContent = "Sample ready. Use FIGHT for the whole battle or STEP FIGHT to inspect it action by action.";
  }

  async function boot() {
    applyPlaytestShell(); installTestGuide(); installCopyLogButton();
    try {
      if (window.IRON_PIT_CANONICAL_MONSTERS_READY !== true) throw new Error("Certified 2014 monster bundle did not load.");
      if (window.IRON_PIT_RULESET !== "2014" || window.IRON_PIT_HERO_RULESET !== "2014") throw new Error("Pure 2014 playtest data did not load.");
      const required = [window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER, view(), picker(), window.IRON_PIT_EXECUTION, actions()];
      if (required.some((item) => !item)) throw new Error("Iron Pit browser modules did not load.");
      state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(); picker().bind(() => state);
      actions().install({ state, matchup, render, updateControls, clearResult }); render();
      el("status").textContent = "2014 beta ready. Load the sample or choose combatants, then start a fight.";
    } catch (error) {
      console.error("Iron Pit initialization failed", error); el("status").textContent = "The 2014 Iron Pit playtest failed to initialize.";
    }
  }

  el("reset-fight").addEventListener("click", resetFight); el("quick-test").addEventListener("click", loadSample);
  boot();
})();