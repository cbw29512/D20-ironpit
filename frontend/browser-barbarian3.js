(() => {
  "use strict";

  const FEATURE = "frenzy";
  const RECKLESS_MARKER = "frenzy-reckless";
  const R = () => window.IRON_PIT_BROWSER_RAGE;
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2;

  function markRecklessUse(state, turnKey) {
    if (!turnKey || !state.template.frenzy || !R()?.active(state)) return;
    state.feature_last_turn_keys[RECKLESS_MARKER] = turnKey;
  }

  function bonusDamage(state, attack, turnKey) {
    if (!turnKey || !state.template.frenzy || !R()?.active(state) || !B2()?.active(state)) return null;
    if (attack.attackAbility !== "strength" || state.feature_last_turn_keys[RECKLESS_MARKER] !== turnKey) return null;
    if (state.feature_last_turn_keys[FEATURE] === turnKey) return null;
    const diceCount = state.template.rage_damage_bonus || 0;
    if (!(diceCount > 0)) return null;
    state.feature_last_turn_keys[FEATURE] = turnKey;
    return { source: "Frenzy", diceCount, diceSize: 6, damageType: attack.damageType };
  }

  window.IRON_PIT_BROWSER_BARBARIAN3 = { bonusDamage, markRecklessUse };
})();
