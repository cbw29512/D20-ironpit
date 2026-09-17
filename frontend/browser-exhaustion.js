(() => {
  "use strict";

  const level = (state) => state.exhaustion_level || 0;
  const is2014 = (state) => state.template.ruleset === "2014";

  function d20Modifier(state) { return is2014(state) ? 0 : -2 * level(state); }
  function abilityCheckDisadvantage(state) { return Number(is2014(state) && level(state) >= 1); }
  function attackDisadvantage(state) { return Number(is2014(state) && level(state) >= 3); }
  function saveDisadvantage(state) { return Number(is2014(state) && level(state) >= 3); }

  function effectiveSpeed(state, speed) {
    if (is2014(state)) {
      if (level(state) >= 5) return 0;
      return level(state) >= 2 ? Math.floor(speed / 2) : speed;
    }
    return Math.max(0, speed - 5 * level(state));
  }

  function effectiveMaxHp(state, maximum) {
    return is2014(state) && level(state) >= 4 ? Math.floor(maximum / 2) : maximum;
  }

  function gain(state, levels = 1) {
    if (levels < 0) throw new Error("Exhaustion gain cannot be negative.");
    state.exhaustion_level = Math.min(6, level(state) + levels);
    state.current_hp = Math.min(state.current_hp, effectiveMaxHp(state, state.template.max_hp + (state.max_hp_bonus || 0)));
    if (state.exhaustion_level >= 6) {
      state.current_hp = 0; state.is_alive = false; state.is_unconscious = false;
      state.is_stable = false; state.is_dead = true;
    }
    return state.exhaustion_level;
  }

  function reduce(state, levels = 1) {
    if (levels < 0) throw new Error("Exhaustion reduction cannot be negative.");
    state.exhaustion_level = Math.max(0, level(state) - levels);
    return state.exhaustion_level;
  }

  window.IRON_PIT_BROWSER_EXHAUSTION = {
    abilityCheckDisadvantage, attackDisadvantage, d20Modifier,
    effectiveMaxHp, effectiveSpeed, gain, reduce, saveDisadvantage,
  };
})();
