(() => {
  "use strict";

  const el = (id) => document.getElementById(id);

  function crNumber(value) {
    const text = String(value ?? "0");
    if (!text.includes("/")) return Number(text) || 0;
    const [a, b] = text.split("/").map(Number); return b ? a / b : 0;
  }

  function formatCr(value) {
    if (Number.isInteger(value)) return String(value);
    const quarters = Math.round(value * 4);
    return quarters === 1 ? "1/4" : quarters === 2 ? "1/2" : quarters === 3 ? "3/4" : value.toFixed(2);
  }

  function card(template, side, index, removeMonster) {
    const node = document.createElement("div"); node.className = "combat-card";
    const copy = document.createElement("div"), title = document.createElement("strong"), meta = document.createElement("small");
    title.textContent = template.name;
    if (side === "heroes") {
      const ready = template.coverage_status === "raw_ready" && template.id;
      meta.textContent = `${template.archetype} · Level ${template.level}${template.build_name ? ` · ${template.build_name}` : ""} · ${ready ? "RAW ready" : "not certified yet"}`;
      if (!ready) node.classList.add("blocked-card");
    } else {
      meta.textContent = `${template.archetype} · CR ${template.challenge_rating}`;
      const remove = document.createElement("button");
      remove.className = "remove-card"; remove.type = "button"; remove.textContent = "Remove";
      remove.addEventListener("click", () => removeMonster(index)); node.append(copy, remove);
    }
    copy.append(title, meta); if (side === "heroes") node.append(copy); return node;
  }

  function renderSide(side, list, removeMonster) {
    const root = el(side === "heroes" ? "hero-cards" : "monster-cards"); root.replaceChildren();
    if (!list.length) {
      const empty = document.createElement("div"); empty.className = "empty";
      empty.textContent = side === "heroes" ? "Choose your character slots above." : "Add monsters by CR to build the encounter.";
      root.append(empty); return;
    }
    list.forEach((item, index) => root.append(card(item, side, index, removeMonster)));
  }

  function renderSelection(state, ready, removeMonster) {
    renderSide("heroes", state.heroCards, removeMonster); renderSide("monsters", state.monsters, removeMonster);
    const levels = state.heroCards.reduce((sum, hero) => sum + Number(hero.level || 0), 0);
    const cr = state.monsters.reduce((sum, monster) => sum + crNumber(monster.challenge_rating), 0);
    el("hero-summary").textContent = `${state.heroCards.length} character${state.heroCards.length === 1 ? "" : "s"} · Total Levels ${levels}`;
    el("monster-summary").textContent = `${state.monsters.length} cards · Total CR ${formatCr(cr)}`;
    const partyCertified = state.heroSlots.length > 0 && state.heroes.length === state.heroSlots.length;
    el("fight-button").disabled = !partyCertified || !state.monsters.length || !ready;
  }

  function finalState(member) {
    const state = member.state;
    if (state.is_dead || !state.is_alive) return "DEAD";
    if (state.current_hp > 0) return "ALIVE";
    if (state.is_stable) return "STABLE";
    if (state.is_unconscious) return "UNCONSCIOUS";
    return "DOWN";
  }

  function showResult(battle) {
    const combatants = [...battle.setup.heroes, ...battle.setup.monsters];
    const names = new Map(combatants.map((c) => [c.combatant_id, c.state.template.name]));
    const winner = battle.outcome === "heroes_win" ? "HEROES WIN" : battle.outcome === "monsters_win" ? "MONSTERS WIN" : "DRAW";
    el("result-title").textContent = winner; el("round-count").textContent = `${battle.rounds} round${battle.rounds === 1 ? "" : "s"}`;
    const initiative = el("initiative-list"); initiative.replaceChildren();
    for (const id of battle.initiative.turn_order) { const item = document.createElement("li"); item.textContent = names.get(id) || id; initiative.append(item); }
    const survivors = el("survivors"); survivors.replaceChildren();
    for (const member of combatants) {
      const row = document.createElement("div"), status = finalState(member);
      row.className = `survivor ${status === "ALIVE" ? "alive" : "down"}`;
      row.textContent = `${member.state.template.name} — ${status} · ${member.state.current_hp}/${member.state.template.max_hp} HP`; survivors.append(row);
    }
    const log = el("battle-log"); log.replaceChildren();
    for (const event of battle.events) {
      const item = document.createElement("li"), naturalOne = event.event_type === "attack" && event.attack_roll?.selected_roll === 1;
      item.textContent = `R${event.round_number}: ${event.description}`;
      if (event.critical) item.classList.add("log-critical"); if (naturalOne) item.classList.add("log-fumble"); log.append(item);
    }
    el("result-panel").hidden = false;
    el("status").textContent = `${winner} · Total Levels ${battle.setup.hero_total_levels} vs Total CR ${battle.setup.monster_total_cr}`;
  }

  window.createEncounterView = () => ({ renderSelection, showResult, setStatus: (text) => { el("status").textContent = text; } });
})();
