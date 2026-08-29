(() => {
  "use strict";

  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const state = { roster: null, heroes: [], monsters: [] };
  const el = (id) => document.getElementById(id);
  const view = window.createEncounterView();

  function render() {
    view.renderSelection(state, Boolean(apiBase), (side, index) => {
      state[side].splice(index, 1);
      render();
    });
  }

  function addSelected(side) {
    if (state[side].length >= 8 || !state.roster) return;
    const pickerId = side === "heroes" ? "hero-picker" : "monster-picker";
    const source = side === "heroes" ? state.roster.characters : state.roster.monsters;
    const chosen = source.find((item) => item.id === el(pickerId).value);
    if (chosen) state[side].push(chosen);
    render();
  }

  async function fight() {
    try {
      el("fight-button").disabled = true;
      view.setStatus("Rolling initiative and resolving the fight…");
      const response = await fetch(`${apiBase}/api/encounters/fight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hero_ids: state.heroes.map((item) => item.id),
          monster_ids: state.monsters.map((item) => item.id),
          starting_distance_ft: Number(el("distance").value),
        }),
      });
      if (!response.ok) throw new Error(`Fight API returned ${response.status}`);
      const battle = await response.json();
      view.showResult(battle);
      await window.playIronPitCriticalEffects?.(battle);
    } catch (error) {
      console.error(error);
      view.setStatus("Fight failed. The production API may still be deploying.");
    } finally {
      render();
    }
  }

  async function boot() {
    if (!apiBase) {
      view.setStatus("Production API is not configured.");
      render();
      return;
    }
    const response = await fetch(`${apiBase}/api/roster`);
    if (!response.ok) throw new Error(`Roster API returned ${response.status}`);
    state.roster = await response.json();
    view.fillPicker("hero-picker", state.roster.characters);
    view.fillPicker("monster-picker", state.roster.monsters);
    if (state.roster.characters[0]) state.heroes.push(state.roster.characters[0]);
    if (state.roster.monsters[0]) state.monsters.push(state.roster.monsters[0]);
    view.setStatus("Ready. Build the matchup and hit FIGHT.");
    render();
  }

  el("add-hero").addEventListener("click", () => addSelected("heroes"));
  el("add-monster").addEventListener("click", () => addSelected("monsters"));
  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => {
    console.error(error);
    view.setStatus("Roster failed to load from production API.");
    render();
  });
})();
