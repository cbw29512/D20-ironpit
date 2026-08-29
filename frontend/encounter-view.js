(() => {
  "use strict";

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
    return quarters === 1 ? "1/4" : quarters === 2 ? "1/2" : quarters === 3 ? "3/4" : value.toFixed(2);
  }

  function card(template, side, index, removeCard) {
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
    remove.addEventListener("click", () => removeCard(side, index));
    node.append(copy, remove);
    return node;
  }

  function renderSide(side, list, removeCard) {
    const root = el(side === "heroes" ? "hero-cards" : "monster-cards");
    root.replaceChildren();
    if (!list.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = side === "heroes" ? "Add 1–8 Hero Cards" : "Add 1–8 Monster Cards";
      root.append(empty);
      return;
    }
    list.forEach((item, index) => root.append(card(item, side, index, removeCard)));
  }

  function renderSelection(state, apiReady, removeCard) {
    renderSide("heroes", state.heroes, removeCard);
    renderSide("monsters", state.monsters, removeCard);
    const levels = state.heroes.reduce((sum, hero) => sum + Number(hero.level || 0), 0);
    const cr = state.monsters.reduce((sum, monster) => sum + crNumber(monster.challenge_rating), 0);
    el("hero-summary").textContent = `${state.heroes.length} cards · Total Levels ${levels}`;
    el("monster-summary").textContent = `${state.monsters.length} cards · Total CR ${formatCr(cr)}`;
    el("add-hero").disabled = state.heroes.length >= 8;
    el("add-monster").disabled = state.monsters.length >= 8;
    el("fight-button").disabled = !state.heroes.length || !state.monsters.length || !apiReady;
  }

  function fillPicker(id, items) {
    const picker = el(id);
    picker.replaceChildren();
    for (const item of items) {
      const option = document.createElement("option");
      const ready = item.coverage_status === "raw_ready";
      option.value = item.id;
      option.textContent = item.level
        ? `${item.name} — ${item.class_name} ${item.level}${ready ? "" : " — not ready yet"}`
        : `${item.name} — CR ${item.challenge_rating}${ready ? "" : " — not ready yet"}`;
      picker.append(option);
    }
  }

  function showResult(battle) {
    const combatants = [...battle.setup.heroes, ...battle.setup.monsters];
    const names = new Map(combatants.map((c) => [c.combatant_id, c.state.template.name]));
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
    for (const member of combatants) {
      const row = document.createElement("div");
      row.className = `survivor ${member.state.current_hp > 0 ? "alive" : "down"}`;
      row.textContent = `${member.state.template.name} — ${member.state.current_hp}/${member.state.template.max_hp} HP`;
      survivors.append(row);
    }
    const log = el("battle-log");
    log.replaceChildren();
    for (const event of battle.events) {
      const item = document.createElement("li");
      const naturalOne = event.event_type === "attack" && event.attack_roll?.selected_roll === 1;
      item.textContent = `R${event.round_number}: ${event.description}`;
      if (event.critical) item.classList.add("log-critical");
      if (naturalOne) item.classList.add("log-fumble");
      log.append(item);
    }
    el("result-panel").hidden = false;
    el("status").textContent = `${winner} · Total Levels ${battle.setup.hero_total_levels} vs Total CR ${battle.setup.monster_total_cr}`;
  }

  window.createEncounterView = () => ({
    fillPicker,
    renderSelection,
    showResult,
    setStatus: (text) => { el("status").textContent = text; },
  });
})();
