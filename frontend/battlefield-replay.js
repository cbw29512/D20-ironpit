(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const nodes = new Map();
  const SELF_BUFFS = new Set(["rage", "dodge"]);
  const DEBUFF_MODIFIERS = new Set(["attacks-against-advantage"]);
  const reduced = () => window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, reduced() ? Math.min(ms, 70) : ms));
  const cleanLabel = (id) => String(id || "").replace(/^weapon-mastery-/, "").replace(/^tactical-master-/, "").replaceAll("_", " ").replaceAll("-", " ").toUpperCase();
  const conditionLabel = (id) => id === "frightened" ? "😱 FEAR" : cleanLabel(id);
  const concentrationLabel = (id) => id ? `✨ CONCENTRATING · ${cleanLabel(id)}` : "";

  function modifierIsDebuff(modifier) {
    return DEBUFF_MODIFIERS.has(modifier.kind) || Number(modifier.flat_bonus || 0) < 0;
  }

  function classifyStatusLanes(state) {
    const buffs = new Set(state.active_buff_effect_ids || []), debuffs = new Set();
    for (const id of state.active_effect_ids || []) (SELF_BUFFS.has(id) ? buffs : debuffs).add(id);
    for (const effect of state.timed_effects || []) debuffs.add(effect.effect_id);
    for (const modifier of state.active_modifiers || []) {
      const id = modifier.source_effect_id; if (!id) continue;
      (modifierIsDebuff(modifier) ? debuffs : buffs).add(id);
    }
    if (state.concentration?.effect_id) buffs.delete(state.concentration.effect_id);
    for (const id of debuffs) buffs.delete(id);
    return { buffs: [...buffs].sort(), debuffs: [...debuffs].sort() };
  }

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

  function concentration(node, effectId) {
    if (!node) return;
    const badge = node.querySelector(".card-concentration"); if (!badge) return;
    badge.textContent = concentrationLabel(effectId); badge.hidden = !effectId;
    node.dataset.concentration = effectId || "";
  }

  function renderLane(node, selector, ids, kind) {
    const rack = node?.querySelector(selector); if (!rack) return;
    const badges = ids.map((id) => {
      const badge = document.createElement("span");
      badge.className = kind === "buff" ? `buff-badge buff-${id}` : `debuff-badge condition-badge condition-${id}`;
      badge.dataset.effect = id; badge.textContent = kind === "debuff" ? conditionLabel(id) : cleanLabel(id);
      badge.setAttribute("aria-label", `${kind === "buff" ? "Buff" : "Debuff"}: ${cleanLabel(id)}`); return badge;
    });
    rack.replaceChildren(...badges);
  }

  function renderStateLanes(node, state) {
    if (!node) return;
    const lanes = classifyStatusLanes(state); renderLane(node, ".card-buffs", lanes.buffs, "buff");
    renderLane(node, ".card-debuffs", lanes.debuffs, "debuff");
    node.classList.toggle("has-buff", lanes.buffs.length > 0 || Boolean(state.concentration));
    node.classList.toggle("has-debuff", lanes.debuffs.length > 0); node.classList.toggle("has-condition", lanes.debuffs.length > 0);
  }

  function conditions(node, added = [], removed = []) {
    if (!node) return;
    const set = new Set((node.dataset.conditions || "").split(",").filter(Boolean));
    removed.forEach((id) => set.delete(id)); added.forEach((id) => set.add(id));
    node.dataset.conditions = [...set].join(","); renderLane(node, ".card-debuffs", [...set].sort(), "debuff");
    node.classList.toggle("has-debuff", set.size > 0); node.classList.toggle("has-condition", set.size > 0);
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
    if (event.concentration_started_effect_id) concentration(actor, event.concentration_started_effect_id);
    if (event.concentration_ended_effect_id) concentration(target || actor, null);
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
      concentration(node, state.concentration?.effect_id || null); renderStateLanes(node, state);
    });
  }

  async function play(battle, slotMap, options = {}) {
    bindBattle(battle, slotMap);
    if (!options.instant) {
      for (const event of battle.events || []) await eventStep(event);
    } else {
      el("pit-round").textContent = `ROUND ${battle.rounds}`;
    }
    syncFinal(battle); return battle;
  }

  window.IRON_PIT_BATTLEFIELD_REPLAY = { classifyStatusLanes, concentrationLabel, conditionLabel };
  window.playIronPitBattle = play;
})();