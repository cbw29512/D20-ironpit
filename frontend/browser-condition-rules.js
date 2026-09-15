(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { invisibilitySuppressed: () => false };
  const has = (state, id) => {
    const swallowed = state.swallowed && ["blinded", "restrained"].includes(id);
    const present = Boolean(swallowed || state.active_effect_ids.includes(id)) && !I().immune(state, id);
    return id === "invisible" && M().invisibilitySuppressed(state) ? false : present;
  };

  function incapacitated(state) {
    if (I().immune(state, "incapacitated")) return false;
    return state.is_unconscious || has(state, "incapacitated") || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  }

  const autoFailStrDex = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  const attackAdvantage = (state) => state.is_unconscious || has(state, "blinded") || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  const autoCritical = (state) => state.is_unconscious || has(state, "paralyzed");
  const speedZero = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "petrified") || has(state, "restrained");

  window.IRON_PIT_BROWSER_CONDITION_RULES = { attackAdvantage, autoCritical, autoFailStrDex, has, incapacitated, speedZero };
})();
