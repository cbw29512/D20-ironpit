(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const has = (state, id) => state.active_effect_ids.includes(id) && !I().immune(state, id);

  function incapacitated(state) {
    if (I().immune(state, "incapacitated")) return false;
    return state.is_unconscious || has(state, "incapacitated") || has(state, "paralyzed") || has(state, "stunned");
  }

  const autoFailStrDex = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "stunned");
  const attackAdvantage = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "stunned");
  const autoCritical = (state) => state.is_unconscious || has(state, "paralyzed");
  const speedZero = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "restrained");

  window.IRON_PIT_BROWSER_CONDITION_RULES = { attackAdvantage, autoCritical, autoFailStrDex, has, incapacitated, speedZero };
})();
