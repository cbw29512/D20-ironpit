(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  function rule(state, damageType) {
    return (state.template.damageAbsorptions || []).find((item) => item.damageType === damageType) || null;
  }
  function matches(state, damageType) {
    return rule(state, damageType) !== null;
  }
  function apply(state, amount, damageType) {
    const profile = rule(state, damageType);
    if (!profile || amount <= 0 || state.is_dead) return 0;
    const before = state.current_hp, maximum = S().effectiveMaxHp(state);
    state.current_hp = Math.min(maximum, before + amount * (profile.healingMultiplier || 1));
    const healed = state.current_hp - before;
    if (healed > 0) {
      state.is_alive = true; state.is_unconscious = false; state.is_stable = false;
      state.death_save_successes = 0; state.death_save_failures = 0;
    }
    return healed;
  }

  window.IRON_PIT_BROWSER_DAMAGE_ABSORPTION = { apply, matches };
})();
