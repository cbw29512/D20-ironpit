(() => {
  "use strict";

  function noteDamageTypes(state, damageTypes = []) {
    if (!state.damage_types_since_last_turn) state.damage_types_since_last_turn = [];
    for (const type of damageTypes) {
      if (!state.damage_types_since_last_turn.includes(type)) state.damage_types_since_last_turn.push(type);
    }
  }

  function defersDeath(state) {
    return Boolean(state.template.regeneration?.diesAtStartTurnIfZeroAndSuppressed);
  }

  function startTurn(state) {
    const rule = state.template.regeneration;
    if (!rule || state.is_dead) {
      state.damage_types_since_last_turn = [];
      return { healed: 0, died: false };
    }
    const history = state.damage_types_since_last_turn || [];
    const suppressed = history.some((type) => (rule.suppressedByDamageTypes || []).includes(type));
    state.damage_types_since_last_turn = [];
    if (suppressed) {
      if (rule.diesAtStartTurnIfZeroAndSuppressed && state.current_hp <= 0) {
        state.is_alive = false; state.is_dead = true; state.is_unconscious = false; state.is_stable = false;
        return { healed: 0, died: true };
      }
      return { healed: 0, died: false };
    }
    const before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp + (state.max_hp_bonus || 0), before + rule.hitPoints);
    if (state.current_hp > 0) { state.is_alive = true; state.is_dead = false; }
    return { healed: state.current_hp - before, died: false };
  }

  window.IRON_PIT_BROWSER_REGENERATION = { defersDeath, noteDamageTypes, startTurn };
})();
