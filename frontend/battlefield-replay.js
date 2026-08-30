(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const nodes = new Map();
  const reduced = () => window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, reduced() ? Math.min(ms, 70) : ms));

  function bindBattle(battle, slotMap) {
    nodes.clear();
    const bindSide = (members, indexes, side) => members.forEach((member, i) => {
      const slot = indexes[i], node = document.querySelector(`.battle-card.${side}[data-slot-index="${slot}"]`);
      if (!node) return; node.dataset.combatantId = member.combatant_id; nodes.set(member.combatant_id, node);
    });
    bindSide(battle.setup.heroes, slotMap.heroes, "heroes");
    bindSide(battle.setup.monsters, slotMap.monsters, "monsters");
    battle.initiative.groups.forEach((group) => group.combatant_ids.forEach((id) => {
      const node = nodes.get(id); if (node) node.querySelector(".initiative-badge").textContent = String(group.initiative_count);
    }));
  }

  function hp(node, value) {
    if (!node || value == null) return;
    const max = Number(node.dataset.maxHp) || 1, safe = Math.max(0, Math.min(Number(value), max));
    node.dataset.currentHp = String(safe); node.querySelector(".hp-text").textContent = `${safe} / ${max} HP`;
    node.querySelector(".card-hp span").style.width = `${(safe / max) * 100}%`;
    node.classList.toggle("battle-down", safe === 0 && !node.classList.contains("battle-dead"));
  }

  function renderConditions(node, set) {
    if (!node) return;
    const rack = node.querySelector(".card-conditions");
    const badges = [...set].sort().map((id) => {
      const badge = document.createElement("span");
      badge.className = `condition-badge condition-${id}`;
      badge.dataset.condition = id;
      badge.textContent = id.replaceAll("_", " ").toUpperCase();
      return badge;
    });
    rack.replaceChildren(...badges);
    node.classList.toggle("has-condition", badges.length > 0);
  }

  function conditions(node, added = [], removed = []) {
    if (!node) return;
    const set = new Set((node.dataset.conditions || "").split(",").filter(Boolean));
    removed.forEach((id) => set.delete(id)); added.forEach((id) => set.add(id));
    node.dataset.conditions = [...set].join(",");
    renderConditions(node, set);
  }

  function dead(node) {
    if (!node) return; node.classList.add("battle-dead"); node.classList.remove("battle-down");
  }

  async function critFx(event) {
    if (!event.critical) return;
    const overlay = el("combat-fx-overlay"); overlay.querySelector("strong").textContent = "CRITICAL HIT!";
    overlay.classList.add("critical-screen"); document.body.classList.add("screen-shake");
    await sleep(300); overlay.classList.remove("critical-screen"); document.body.classList.remove("screen-shake");
  }

  async function fumbleFx(event, actor) {
    if (event.event_type !== "attack" || event.attack_roll?.selected_roll !== 1 || !actor) return;
    actor.classList.add("fumble-blackout"); await sleep(360); actor.classList.remove("fumble-blackout");
  }

  async function eventStep(event) {
    el("pit-round").textContent = `ROUND ${event.round_number}`;
    const actor = nodes.get(event.actor_id), target = nodes.get(event.target_id);
    if (actor) actor.classList.add("turn-active");
    await fumbleFx(event, actor); await critFx(event);
    if (target && event.hp_after != null) hp(target, event.hp_after);
    if (actor && event.event_type === "healing" && event.hp_after != null) hp(actor, event.hp_after);
    if (actor && event.event_type === "death_save" && event.hp_after != null) hp(actor, event.hp_after);
    conditions(target, event.applied_condition_ids || [], event.removed_condition_ids || []);
    if (event.feature_id === "escape-grapple" && event.check_succeeded) conditions(actor, [], ["grappled", "restrained"]);
    if (target && event.is_dead) dead(target); if (actor && event.event_type === "death_save" && event.is_dead) dead(actor);
    await sleep(event.event_type === "initiative" ? 90 : 230);
    if (actor) actor.classList.remove("turn-active");
  }

  function syncFinal(battle) {
    [...battle.setup.heroes, ...battle.setup.monsters].forEach((member) => {
      const node = nodes.get(member.combatant_id), state = member.state; if (!node) return;
      hp(node, state.current_hp); if (state.is_dead || !state.is_alive) dead(node);
      node.classList.toggle("battle-stable", Boolean(state.is_stable && state.current_hp === 0));
      node.dataset.conditions = (state.active_effect_ids || []).join(",");
      renderConditions(node, new Set(state.active_effect_ids || []));
    });
  }

  async function play(battle, slotMap) {
    bindBattle(battle, slotMap);
    for (const event of battle.events || []) await eventStep(event);
    syncFinal(battle); return battle;
  }

  window.playIronPitBattle = play;
})();
