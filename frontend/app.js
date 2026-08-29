(() => {
  "use strict";

  const MAX_SLOTS = 6;
  const state = { catalog: null, heroSlots: Array(MAX_SLOTS).fill(null), monsterSlots: Array(MAX_SLOTS).fill(null), fighting: false };
  const el = (id) => document.getElementById(id);
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const picker = () => window.IRON_PIT_BATTLEFIELD_PICKER;

  function clearResult() {
    el("result-panel").hidden = true; el("pit-round").textContent = "";
    el("battle-log").replaceChildren(Object.assign(document.createElement("li"), { textContent: "Cards loaded. Press FIGHT when both sides are ready." }));
  }

  function render() { if (state.catalog) view().render(state, openSlot); }

  function setSlot(side, index, card) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = card; clearResult(); render();
  }

  function removeSlot(side, index) {
    const slots = side === "heroes" ? state.heroSlots : state.monsterSlots;
    slots[index] = null; clearResult(); render();
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

  async function fight() {
    const heroes = selected("heroes"), monsters = selected("monsters");
    const error = validate(heroes.cards, "heroes") || validate(monsters.cards, "monsters");
    if (error) { el("status").textContent = error; return; }
    try {
      state.fighting = true; render(); clearResult(); el("status").textContent = "Rolling initiative…";
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
        hero_ids: heroes.cards.map((card) => card.runnable_template_id),
        monster_ids: monsters.cards.map((card) => card.runnable_template_id),
        starting_distance_ft: Number(el("distance").value),
      });
      await window.playIronPitBattle(battle, { heroes: heroes.indexes, monsters: monsters.indexes });
      view().writeLog(battle); view().showResult(battle);
    } catch (errorCaught) {
      console.error(errorCaught); el("status").textContent = "Fight stopped because a required RAW mechanic is unsupported or the battle engine failed.";
    } finally {
      state.fighting = false; el("fight-button").disabled = false;
    }
  }

  async function boot() {
    const required = [window.IRON_PIT_BROWSER_ENGINE, window.IRON_PIT_BROWSER_CATALOG, window.IRON_PIT_ENCOUNTER_PICKER, view(), picker()];
    if (required.some((item) => !item)) throw new Error("Iron Pit browser modules did not load.");
    state.catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog();
    picker().bind(() => state); render();
    el("status").textContent = "Click an empty slot to add a RAW-certified card.";
  }

  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => { console.error(error); el("status").textContent = "The Iron Pit failed to initialize."; });
})();
