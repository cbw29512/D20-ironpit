(() => {
  "use strict";

  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function buildState(template) {
    return {
      template, current_hp: template.max_hp, temporary_hp: 0, initiative_roll: null, initiative_total: null, is_alive: true,
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
  const active = (member) => member.state.is_alive && !member.state.is_dead
    && member.state.current_hp > 0 && !Q().incapacitated(member.state);
  const downedCharacter = (member) => member.state.template.kind === "character" && member.state.is_alive && !member.state.is_dead && member.state.current_hp === 0;
  const opponents = (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes;

  function targetPriority(member) {
    const state = member.state;
    if (!state.is_alive || state.is_dead) return null;
    if (state.template.kind === "character" && state.current_hp === 0) return state.is_unconscious || state.is_stable ? 1 : null;
    return state.current_hp > 0 && !Q().incapacitated(state) ? 0 : null;
  }

  function nearestTarget(member, setup) {
    const candidates = opponents(member, setup)
      .map((target) => ({ target, priority: targetPriority(target) }))
      .filter((item) => item.priority !== null)
      .sort((a, b) => a.priority - b.priority || distance(member, a.target) - distance(member, b.target));
    return candidates[0]?.target || null;
  }

  function packTactics(member, setup) {
    if (!member.state.template.traits?.includes("pack-tactics") || !active(member)) return false;
    return (member.side === "heroes" ? setup.heroes : setup.monsters)
      .some((ally) => ally.combatant_id !== member.combatant_id && active(ally));
  }

  function canProne(target, maxSize) {
    if (!maxSize) return true;
    return (SIZE_RANK[target.state.template.size] ?? 2) <= (SIZE_RANK[maxSize] ?? 2);
  }

  function moveToward(member, target, desiredDistance = 5) {
    const before = distance(member, target), needed = Math.max(0, before - desiredDistance);
    const moved = Math.min(needed, member.state.movement_remaining_ft);
    if (moved <= 0) return null;
    member.position_ft += member.position_ft < target.position_ft ? moved : -moved;
    member.state.movement_remaining_ft -= moved;
    return { before, after: distance(member, target), moved };
  }

  function refreshStartTurn(state) {
    refreshReaction(state);
  }

  window.IRON_PIT_BROWSER_STATE = {
    buildState, beginTurn, refreshStartTurn, refreshReaction, distance, nearestTarget, packTactics, canProne, moveToward,
  };
})();
