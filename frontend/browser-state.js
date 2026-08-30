(() => {
  "use strict";

  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { has: (state, id) => state.active_effect_ids.includes(id), incapacitated: (state) => state.is_unconscious };

  function buildState(template) {
    return {
      template, current_hp: template.max_hp, temporary_hp: 0, is_alive: true,
      is_unconscious: false, is_stable: false, is_dead: false,
      death_save_successes: 0, death_save_failures: 0,
      action_available: true, bonus_action_available: true, reaction_available: true,
      movement_remaining_ft: 0, resources: { ...(template.resources || {}) },
      active_effect_ids: [], grapple_sources: [], timed_effects: [], feature_last_turn_keys: {},
      spell_slot_expended_turn_key: null,
      temporary_damage_resistances: [], rage_expires_round: null, rage_max_round: null,
    };
  }

  function refreshReaction(state) { state.reaction_available = true; }

  function beginTurn(state) {
    const incapacitated = Q().incapacitated(state);
    state.action_available = !incapacitated;
    state.bonus_action_available = !incapacitated;
    refreshReaction(state);
    const speedZero = G()?.speedIsZero(state) || false;
    state.movement_remaining_ft = speedZero ? 0 : state.template.speed_ft;
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "dodge");
    if (state.active_effect_ids.includes("prone") && state.template.speed_ft > 0 && !speedZero) {
      state.movement_remaining_ft = Math.max(0, state.movement_remaining_ft - Math.floor(state.template.speed_ft / 2));
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "prone");
    }
  }

  const distance = (a, b) => Math.abs(a.position_ft - b.position_ft);
  const active = (member) => member.state.is_alive && !member.state.is_dead && !member.state.is_unconscious && member.state.current_hp > 0;
  const downedCharacter = (member) => member.state.template.kind === "character" && member.state.is_alive && !member.state.is_dead && member.state.current_hp === 0;
  const opponents = (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes;

  function targetPriority(member) {
    const state = member.state;
    if (!state.is_alive || state.is_dead) return null;
    if (state.current_hp > 0) return Q().has(state, "petrified") ? 1 : 0;
    if (state.template.kind === "character" && state.current_hp === 0) return 2;
    return null;
  }

  function priorityTargets(member, setup) {
    const eligible = opponents(member, setup).filter((candidate) => targetPriority(candidate) !== null);
    if (!eligible.length) return [];
    const priority = Math.min(...eligible.map(targetPriority));
    return eligible.filter((candidate) => targetPriority(candidate) === priority);
  }

  function nearestTarget(member, setup) {
    const candidates = priorityTargets(member, setup);
    if (!candidates.length) return null;
    const held = candidates.filter((candidate) =>
      candidate.state.grapple_sources.some((source) => source.source_id === member.combatant_id));
    if (held.length) return held.reduce((best, item) => distance(member, item) < distance(member, best) ? item : best);
    const grapplerIds = new Set(member.state.grapple_sources.map((source) => source.source_id));
    const grapplers = candidates.filter((candidate) => grapplerIds.has(candidate.combatant_id));
    const choices = grapplers.length ? grapplers : candidates;
    return choices.reduce((best, item) => distance(member, item) < distance(member, best) ? item : best);
  }

  function hasActiveAlly(member, setup) {
    const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.some((ally) => ally.combatant_id !== member.combatant_id && active(ally));
  }

  const packTactics = (member, setup) => member.state.template.traits?.includes("pack-tactics") && hasActiveAlly(member, setup);
  function moveToward(member, target, desired) {
    const before = distance(member, target);
    const moved = Math.min(Math.max(0, before - desired), member.state.movement_remaining_ft);
    if (!moved) return null;
    member.position_ft += (member.position_ft < target.position_ft ? 1 : -1) * moved;
    member.state.movement_remaining_ft -= moved;
    return { before, after: distance(member, target), moved };
  }

  const sizeAtMost = (member, maxSize) => Boolean(maxSize) && SIZE_RANK[member.state.template.size] <= SIZE_RANK[maxSize];
  const canProne = (target, maxSize) => sizeAtMost(target, maxSize);
  window.IRON_PIT_BROWSER_STATE = {
    active, beginTurn, buildState, canProne, distance, downedCharacter, hasActiveAlly,
    moveToward, nearestTarget, packTactics, refreshReaction, sizeAtMost, targetPriority,
  };
})();
