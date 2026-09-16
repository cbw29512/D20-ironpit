(() => {
  "use strict";
  const MAX_SLOTS = 6;
  const state = { ruleset: "2024", catalog: null, heroSlots: Array(MAX_SLOTS).fill(null), monsterSlots: Array(MAX_SLOTS).fill(null), fighting: false, hasRun: false, turboBatch: null, session: null };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;
  const turboView = () => window.IRON_PIT_TURBO_VIEW;
  const actions = () => window.IRON_PIT_BATTLE_ACTIONS;
  const rulesetUi = () => window.IRON_PIT_RULESET_UI;

  function loadRulesetUi() {
    if (rulesetUi()) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const script = document.createElement("script"); script.src = "browser-ruleset-ui.js"; script.async = true;
      script.onload = resolve; script.onerror = () => reject(new Error("Ruleset UI module could not be loaded."));
      document.head.append(script);
    });
  }

  function updateControls() {
    const ready = state.heroSlots.some(Boolean) && state.monsterSlots.some(Boolean);
    const active = Boolean(state.session && !state.session.complete);
    for (const id of ["fight-button", "step-fight-button", "turbo-button"]) el(id).disabled = state.fighting || active || !ready;
    el("rerun-button").disabled = state.fighting || active || !state.hasRun;
    el("quick-test").disabled = state.fighting || active; el("reset-fight").disabled = state.fighting;
    rulesetUi()?.syncDisabled(state);
  }

  function clearResult(message = "Cards loaded. Press FIGHT when both sides are ready.") {
    el("result-panel").hidden = true; el("pit-round").textContent = "";
    el("battle-log").replaceChildren(Object.assign(document.createElement("li"), { textContent: message }));
    el("lab-summary").textContent = "Production combat path · secure Web Crypto dice.";
  }

  function invalidateRun() {
    state.hasRun = false; state.turboBatch = null; state.session = null; turboView()?.hide();
    actions()?.syncControls(state); updateControls();
  }
  function render() { if (state.catalog) view().render(state, openSlot); updateControls(); actions()?.syncControls(state); }
  function setSlot(side, index, card) { (side === "heroes" ? state.heroSlots : state.monsterSlots)[index] = card; invalidateRun(); clearResult(); render(); }
  function removeSlot(side, index) { (side === "heroes" ? state.heroSlots : state.monsterSlots)[index] = null; invalidateRun(); clearResult(); render(); }
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
    const label = state.ruleset === "2014" ? (side === "heroes" ? "Team A" : "Team B") : side === "heroes" ? "Hero" : "Monster";
    if (!cards.length) return `${label} side needs at least one card.`;
    const blocked = cards.find((card) => card.coverage_status !== "raw_ready" || !card.runnable_template_id);
    return blocked ? `${blocked.name} is not RAW-certified for automated combat yet.` : null;
  }
  function matchup() {
    const heroes = selected("heroes"), monsters = selected("monsters");
    const error = validate(heroes.cards, "heroes") || validate(monsters.cards, "monsters");
    return { heroes, monsters, error, selection: { ruleset: state.ruleset, hero_ids: heroes.cards.map((card) => card.runnable_template_id), monster_ids: monsters.cards.map((card) => card.runnable_template_id) } };
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
    const is2014 = state.ruleset === "2014";
    const heroes = is2014 ? [cardByTemplate("heroes", "2014-brown-bear"), cardByTemplate("heroes", "2014-bandit")] : [cardByTemplate("heroes", "karnok-stoneward-l1"), cardByTemplate("heroes", "seraphine-dawnshield-l1")];
    const monsters = is2014 ? [cardByTemplate("monsters", "2014-skeleton"), cardByTemplate("monsters", "2014-goblin")] : [cardByTemplate("monsters", "srd-goblin-warrior"), cardByTemplate("monsters", "srd-wolf")];
    if ([...heroes, ...monsters].some((card) => !card)) { el("status").textContent = "Sample matchup could not find its certified cards."; return; }
    state.heroSlots.fill(null); state.monsterSlots.fill(null);
    heroes.forEach((card, index) => { state.heroSlots[index] = card; }); monsters.forEach((card, index) => { state.monsterSlots[index] = card; });
    invalidateRun(); clearResult(is2014 ? "2014 sample loaded: Brown Bear + Bandit vs Skeleton + Goblin." : "2024 sample loaded: Karnok + Seraphine vs Goblin Warrior + Wolf."); render();
    el("status").textContent = "Sample loaded. Choose FIGHT, STEP FIGHT, or TURBO.";
  }

  async function changeRuleset(nextRuleset) {
    const selector = el("ruleset-select");
    if (nextRuleset === state.ruleset) return;
    if (state.fighting || (state.session && !state.session.complete)) { if (selector) selector.value = state.ruleset; return; }
    try {
      await rulesetUi().ensureBundle(nextRuleset);
      state.ruleset = nextRuleset; state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(nextRuleset);
      state.heroSlots.fill(null); state.monsterSlots.fill(null); invalidateRun();
      clearResult(`${nextRuleset} ruleset loaded. Previous matchup cleared to preserve edition isolation.`); rulesetUi().update(state); render();
      el("status").textContent = nextRuleset === "2014" ? "2014 test lane ready. Choose certified monsters for Team A and Team B, or load the sample." : "2024 production lane ready. Choose cards or load the sample matchup.";
    } catch (error) {
      console.error("Ruleset switch failed", error); if (selector) selector.value = state.ruleset;
      el("status").textContent = `Could not load the ${nextRuleset} ruleset.`;
    }
  }

  async function boot() {
    try {
      await loadRulesetUi();
      if (window.IRON_PIT_CANONICAL_MONSTERS_READY !== true) throw new Error("Canonical RAW-certified monster bundle did not load.");
      const required = [window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER, view(), picker(), window.IRON_PIT_EXECUTION, actions(), rulesetUi()];
      if (required.some((item) => !item)) throw new Error("Iron Pit browser modules did not load.");
      rulesetUi().install(state, changeRuleset); state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(state.ruleset); picker().bind(() => state);
      actions().install({ state, matchup, render, updateControls, clearResult }); rulesetUi().update(state); render();
      el("status").textContent = "Iron Pit ready. Choose cards or load the sample matchup.";
    } catch (error) { console.error("Iron Pit initialization failed", error); el("status").textContent = "The Iron Pit failed to initialize."; }
  }

  el("reset-fight").addEventListener("click", resetFight); el("quick-test").addEventListener("click", loadSample); boot();
})();