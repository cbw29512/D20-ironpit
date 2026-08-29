(() => {
  "use strict";

  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };

  function buildState(template) {
    return {
      template,
      current_hp: template.max_hp,
      temporary_hp: 0,
      is_alive: true,
      is_unconscious: false,
      is_stable: false,
      is_dead: false,
      death_save_successes: 0,
      death_save_failures: 0,
      action_available: true,
      bonus_action_available: true,
      movement_remaining_ft: 0,
      resources: { ...(template.resources || {}) },
      active_effect_ids: [],
      feature_last_turn_keys: {},
      temporary_damage_resistances: [],
      rage_expires_round: null,
      rage_max_round: null,
    };
  }

  function beginTurn(state) {
    state.action_available = true;
    state.bonus_action_available = true;
    state.movement_remaining_ft = state.template.speed_ft;
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "dodge");
    if (state.active_effect_ids.includes("prone") && state.template.speed_ft > 0) {
      state.movement_remaining_ft = Math.max(0, state.movement_remaining_ft - Math.floor(state.template.speed_ft / 2));
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "prone");
    }
  }

  const distance = (a, b) => Math.abs(a.position_ft - b.position_ft);
  const active = (member) => member.state.is_alive && !member.state.is_dead && !member.state.is_unconscious && member.state.current_hp > 0;
  const downedCharacter = (member) => member.state.template.kind === "character" && member.state.is_alive && !member.state.is_dead && member.state.current_hp === 0;

  function opponents(member, setup) {
    return member.side === "heroes" ? setup.monsters : setup.heroes;
  }

  function nearestTarget(member, setup) {
    const enemies = opponents(member, setup);
    let candidates = enemies.filter(active);
    if (!candidates.length) candidates = enemies.filter(downedCharacter);
    return candidates.length ? candidates.reduce((best, item) => distance(member, item) < distance(member, best) ? item : best) : null;
  }

  function hasActiveAlly(member, setup) {
    const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.some((ally) => ally.combatant_id !== member.combatant_id && active(ally));
  }

  function packTactics(member, setup) {
    return member.state.template.traits?.includes("pack-tactics") && hasActiveAlly(member, setup);
  }

  function moveToward(member, target, desired) {
    const before = distance(member, target);
    const moved = Math.min(Math.max(0, before - desired), member.state.movement_remaining_ft);
    if (!moved) return null;
    member.position_ft += (member.position_ft < target.position_ft ? 1 : -1) * moved;
    member.state.movement_remaining_ft -= moved;
    return { before, after: distance(member, target), moved };
  }

  function canProne(target, maxSize) {
    return maxSize && SIZE_RANK[target.state.template.size] <= SIZE_RANK[maxSize];
  }

  window.IRON_PIT_BROWSER_STATE = {
    active, beginTurn, buildState, canProne, distance, downedCharacter, hasActiveAlly, moveToward, nearestTarget, packTactics,
  };
})();
