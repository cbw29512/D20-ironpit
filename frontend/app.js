(() => {
  "use strict";
  const MAX_SLOTS = 6;
  const state = { ruleset: "2024", catalog: null, heroSlots: Array(MAX_SLOTS).fill(null), monsterSlots: Array(MAX_SLOTS).fill(null), fighting: false, hasRun: false, turboBatch: null, session: null };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;
  const turboView = () => window.IRON_PIT_TURBO_VIEW;
  const actions = () => window.IRON_PIT_BATTLE_ACTIONS;
  let rulesetBundlePromise = null;

  function updateControls() {
    const ready = state.heroSlots.some(Boolean) && state.monsterSlots.some(Boolean);
    const active = Boolean(state.session && !state.session.complete);
    for (const id of ["fight-button", "step-fight-button", "turbo-button"]) el(id).disabled = state.fighting || active || !ready;
    el("rerun-button").disabled = state.fighting || active || !state.hasRun;
    el("quick-test").disabled = state.fighting || active; el("reset-fight").disabled = state.fighting;
    if (el("ruleset-select")) el("ruleset-select").disabled = state.fighting || active;
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
    const label = state.ruleset === "2014" ? (side === "heroes" ? "Team A" : "Team B") : side === "heroes" ? "Hero" : "Monster";
    if (!cards.length) return `${label} side needs at least one card.`;
    const blocked = cards.find((card) => card.coverage_status !== "raw_ready" || !card.runnable_template_id);
    return blocked ? `${blocked.name} is not RAW-certified for automated combat yet.` : null;
  }

  function matchup() {
    const heroes = selected("heroes"), monsters = selected("monsters");
    const error = validate(heroes.cards, "heroes") || validate(monsters.cards, "monsters");
    return {
      heroes,
      monsters,
      error,
      selection: {
        ruleset: state.ruleset,
        hero_ids: heroes.cards.map((card) => card.runnable_template_id),
        monster_ids: monsters.cards.map((card) => card.runnable_template_id),
      },
    };
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
    let heroes, monsters, message;
    if (state.ruleset === "2014") {
      heroes = [cardByTemplate("heroes", "2014-brown-bear"), cardByTemplate("heroes", "2014-bandit")];
      monsters = [cardByTemplate("monsters", "2014-skeleton"), cardByTemplate("monsters", "2014-goblin")];
      message = "2014 sample loaded: Brown Bear + Bandit vs Skeleton + Goblin.";
    } else {
      heroes = [cardByTemplate("heroes", "karnok-stoneward-l1"), cardByTemplate("heroes", "seraphine-dawnshield-l1")];
      monsters = [cardByTemplate("monsters", "srd-goblin-warrior"), cardByTemplate("monsters", "srd-wolf")];
      message = "2024 sample loaded: Karnok + Seraphine vs Goblin Warrior + Wolf.";
    }
    if ([...heroes, ...monsters].some((card) => !card)) { el("status").textContent = "Sample matchup could not find its certified cards."; return; }
    state.heroSlots.fill(null); state.monsterSlots.fill(null);
    heroes.forEach((card, index) => { state.heroSlots[index] = card; }); monsters.forEach((card, index) => { state.monsterSlots[index] = card; });
    invalidateRun(); clearResult(message); render();
    el("status").textContent = "Sample loaded. Choose FIGHT, STEP FIGHT, or TURBO.";
  }

  function ensureRulesetStyles() {
    if (document.querySelector('link[data-iron-pit-ruleset-style="true"]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet"; link.href = "ruleset-switch.css"; link.dataset.ironPitRulesetStyle = "true";
    document.head.append(link);
  }

  function ensure2014Bundle() {
    if (window.IRON_PIT_2014_MVP_READY === true && window.IRON_PIT_BROWSER_MONSTERS_2014) return Promise.resolve();
    if (rulesetBundlePromise) return rulesetBundlePromise;
    rulesetBundlePromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "browser-monsters-2014.js"; script.async = true; script.dataset.ironPitRuleset = "2014";
      script.onload = () => window.IRON_PIT_2014_MVP_READY === true ? resolve() : reject(new Error("2014 browser bundle loaded without its readiness marker."));
      script.onerror = () => reject(new Error("2014 browser bundle could not be loaded."));
      document.head.append(script);
    });
    return rulesetBundlePromise;
  }

  function rulesetSummary() {
    if (!state.catalog) return "";
    if (state.ruleset === "2014") return `${state.catalog.monster_ready_count}/4 certified 2014 monsters · test lane · monster-vs-monster until 2014 pregens are certified.`;
    return `${state.catalog.hero_ready_count}/${state.catalog.hero_count} certified hero levels · ${state.catalog.monster_ready_count}/${state.catalog.monster_count} certified monsters.`;
  }

  function updateRulesetText() {
    const is2014 = state.ruleset === "2014", header = document.querySelector("header.hero");
    const eyebrow = header?.querySelector("p.eyebrow"), introStrong = header?.querySelector("p strong");
    const headerNotes = header?.querySelectorAll("p.rules-note") || [];
    if (eyebrow) eyebrow.textContent = is2014 ? "D&D 5e 2014 · SRD 5.1 TEST LANE" : "D&D 5e 2024 · SRD 5.2.1";
    if (introStrong?.parentElement) introStrong.parentElement.innerHTML = is2014
      ? "<strong>D&D 5e (2014) test combat lane.</strong> Pick certified 2014 monsters for both teams and run them through the shared Iron Pit engine."
      : "<strong>D&D 5e (2024) compatible combat simulation system.</strong> Load the cards, roll initiative, and watch a rules-driven fight play out.";
    if (headerNotes[0]) headerNotes[0].textContent = is2014
      ? "2014 is isolated from 2024. This test lane currently exposes only the four certified MVP monsters."
      : "2024 production lane. Only explicitly certified hero levels and monsters can enter automated combat.";
    const auditNote = document.querySelector(".log-panel .rules-note");
    if (auditNote) auditNote.textContent = is2014 ? "D&D 2014 / SRD 5.1 test lane · expandable rules audit" : "D&D 2024 / SRD 5.2.1 · expandable rules audit";
    const leftLabel = document.querySelector(".hero-field .field-heading span"), rightLabel = document.querySelector(".monster-field .field-heading span");
    if (leftLabel) leftLabel.textContent = is2014 ? "TEAM A MONSTERS" : "HERO CARDS";
    if (rightLabel) rightLabel.textContent = is2014 ? "TEAM B MONSTERS" : "MONSTER CARDS";
    if (el("ruleset-summary")) el("ruleset-summary").textContent = rulesetSummary();
    if (el("ruleset-control")) el("ruleset-control").dataset.ruleset = state.ruleset;
    document.title = is2014 ? "The Iron Pit — D&D 5e 2014 Test Lane" : "The Iron Pit — D&D 5e 2024 Combat Simulator";
  }

  async function changeRuleset(nextRuleset) {
    const selector = el("ruleset-select");
    if (nextRuleset === state.ruleset) return;
    if (state.fighting || (state.session && !state.session.complete)) { if (selector) selector.value = state.ruleset; return; }
    try {
      if (nextRuleset === "2014") await ensure2014Bundle();
      state.ruleset = nextRuleset;
      state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(nextRuleset);
      state.heroSlots.fill(null); state.monsterSlots.fill(null); invalidateRun();
      clearResult(`${nextRuleset} ruleset loaded. Previous matchup cleared to preserve edition isolation.`);
      updateRulesetText(); render();
      el("status").textContent = nextRuleset === "2014"
        ? "2014 test lane ready. Choose certified monsters for Team A and Team B, or load the sample."
        : "2024 production lane ready. Choose cards or load the sample matchup.";
    } catch (error) {
      console.error("Ruleset switch failed", error);
      if (selector) selector.value = state.ruleset;
      el("status").textContent = `Could not load the ${nextRuleset} ruleset.`;
    }
  }

  function installRulesetControl() {
    ensureRulesetStyles();
    const header = document.querySelector("header.hero"), heading = header?.querySelector("h1");
    if (!header || !heading || el("ruleset-control")) return;
    const control = document.createElement("div"); control.id = "ruleset-control"; control.className = "ruleset-control"; control.dataset.ruleset = state.ruleset;
    const label = document.createElement("label"); label.textContent = "Ruleset";
    const select = document.createElement("select"); select.id = "ruleset-select"; select.setAttribute("aria-label", "Iron Pit ruleset");
    for (const [value, text] of [["2024", "2024"], ["2014", "2014"]]) select.append(Object.assign(document.createElement("option"), { value, textContent: text }));
    const summary = document.createElement("small"); summary.id = "ruleset-summary";
    label.append(select); control.append(label, summary); heading.insertAdjacentElement("afterend", control);
    select.addEventListener("change", () => changeRuleset(select.value));
  }

  async function boot() {
    try {
      if (window.IRON_PIT_CANONICAL_MONSTERS_READY !== true) throw new Error("Canonical RAW-certified monster bundle did not load.");
      const required = [window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER, view(), picker(), window.IRON_PIT_EXECUTION, actions()];
      if (required.some((item) => !item)) throw new Error("Iron Pit browser modules did not load.");
      installRulesetControl();
      state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(state.ruleset); picker().bind(() => state);
      actions().install({ state, matchup, render, updateControls, clearResult }); updateRulesetText(); render();
      el("status").textContent = "Iron Pit ready. Choose cards or load the sample matchup.";
    } catch (error) {
      console.error("Iron Pit initialization failed", error); el("status").textContent = "The Iron Pit failed to initialize.";
    }
  }

  el("reset-fight").addEventListener("click", resetFight); el("quick-test").addEventListener("click", loadSample);
  boot();
})();