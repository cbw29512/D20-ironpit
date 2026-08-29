(() => {
  "use strict";

  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const state = { roster: null, heroes: [], monsters: [] };
  const el = (id) => document.getElementById(id);

  function crNumber(value) {
    const text = String(value ?? "0");
    if (!text.includes("/")) return Number(text) || 0;
    const [a, b] = text.split("/").map(Number);
    return b ? a / b : 0;
  }

  function formatCr(value) {
    if (Number.isInteger(value)) return String(value);
    const quarters = Math.round(value * 4);
    if (quarters % 4 === 0) return String(quarters / 4);
    if (quarters === 1) return "1/4";
    if (quarters === 2) return "1/2";
    if (quarters === 3) return "3/4";
    return value.toFixed(2);
  }

  function card(template, side, index) {
    const node = document.createElement("div");
    node.className = "combat-card";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const meta = document.createElement("small");
    title.textContent = template.name;
    meta.textContent = side === "heroes"
      ? `${template.archetype} · Level ${template.level}`
      : `${template.archetype} · CR ${template.challenge_rating}`;
    copy.append(title, meta);
    const remove = document.createElement("button");
    remove.className = "remove-card";
    remove.type = "button";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => { state[side].splice(index, 1); render(); });
    node.append(copy, remove);
    return node;
  }

  function renderSide(side) {
    const list = state[side];
    const root = el(side === "heroes" ? "hero-cards" : "monster-cards");
    root.replaceChildren();
    if (!list.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = side === "heroes" ? "Add 1–8 Hero Cards" : "Add 1–8 Monster Cards";
      root.append(empty);
    } else list.forEach((item, index) => root.append(card(item, side, index)));
  }

  function render() {
    renderSide("heroes");
    renderSide("monsters");
    const levels = state.heroes.reduce((sum, hero) => sum + Number(hero.level || 0), 0);
    const cr = state.monsters.reduce((sum, monster) => sum + crNumber(monster.challenge_rating), 0);
    el("hero-summary").textContent = `${state.heroes.length} cards · Total Levels ${levels}`;
    el("monster-summary").textContent = `${state.monsters.length} cards · Total CR ${formatCr(cr)}`;
    el("add-hero").disabled = state.heroes.length >= 8;
    el("add-monster").disabled = state.monsters.length >= 8;
    el("fight-button").disabled = !state.heroes.length || !state.monsters.length || !apiBase;
  }

  function fillPicker(id, items) {
    const picker = el(id);
    picker.replaceChildren();
    for (const item of items) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.level
        ? `${item.name} — ${item.archetype} ${item.level}`
        : `${item.name} — CR ${item.challenge_rating}`;
      picker.append(option);
    }
  }

  function addSelected(side) {
    if (state[side].length >= 8) return;
    const pickerId = side === "heroes" ? "hero-picker" : "monster-picker";
    const source = side === "heroes" ? state.roster.characters : state.roster.monsters;
    const chosen = source.find((item) => item.id === el(pickerId).value);
    if (chosen) state[side].push(chosen);
    render();
  }

  function combatantNameMap(setup) {
    return new Map([...setup.heroes, ...setup.monsters].map((c) => [c.combatant_id, c.state.template.name]));
  }

  function showResult(battle) {
    const names = combatantNameMap(battle.setup);
    const winner = battle.outcome === "heroes_win" ? "HEROES WIN" : battle.outcome === "monsters_win" ? "MONSTERS WIN" : "DRAW";
    el("result-title").textContent = winner;
    el("round-count").textContent = `${battle.rounds} round${battle.rounds === 1 ? "" : "s"}`;
    const initiative = el("initiative-list");
    initiative.replaceChildren();
    for (const id of battle.initiative.turn_order) {
      const item = document.createElement("li");
      item.textContent = names.get(id) || id;
      initiative.append(item);
    }
    const survivors = el("survivors");
    survivors.replaceChildren();
    for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
      const row = document.createElement("div");
      row.className = `survivor ${member.state.current_hp > 0 ? "alive" : "down"}`;
      row.textContent = `${member.state.template.name} — ${member.state.current_hp}/${member.state.template.max_hp} HP`;
      survivors.append(row);
    }
    const log = el("battle-log");
    log.replaceChildren();
    for (const event of battle.events) {
      const item = document.createElement("li");
      item.textContent = `R${event.round_number}: ${event.description}`;
      log.append(item);
    }
    el("result-panel").hidden = false;
    el("status").textContent = `${winner} · Total Levels ${battle.setup.hero_total_levels} vs Total CR ${battle.setup.monster_total_cr}`;
  }

  async function fight() {
    try {
      el("fight-button").disabled = true;
      el("status").textContent = "Rolling initiative and resolving the fight…";
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
      showResult(await response.json());
    } catch (error) {
      console.error(error);
      el("status").textContent = "Fight failed. The production API may still be deploying.";
    } finally { render(); }
  }

  async function boot() {
    if (!apiBase) { el("status").textContent = "Production API is not configured."; render(); return; }
    const response = await fetch(`${apiBase}/api/roster`);
    if (!response.ok) throw new Error(`Roster API returned ${response.status}`);
    state.roster = await response.json();
    fillPicker("hero-picker", state.roster.characters);
    fillPicker("monster-picker", state.roster.monsters);
    if (state.roster.characters[0]) state.heroes.push(state.roster.characters[0]);
    if (state.roster.monsters[0]) state.monsters.push(state.roster.monsters[0]);
    el("status").textContent = "Ready. Build the matchup and hit FIGHT.";
    render();
  }

  el("add-hero").addEventListener("click", () => addSelected("heroes"));
  el("add-monster").addEventListener("click", () => addSelected("monsters"));
  el("fight-button").addEventListener("click", fight);
  boot().catch((error) => { console.error(error); el("status").textContent = "Roster failed to load from production API."; render(); });
})();
