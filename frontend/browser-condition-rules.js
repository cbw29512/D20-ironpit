(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  function has(state, id) {
    if (!state.active_effect_ids.includes(id)) return false;
    const timed = (state.timed_effects || []).filter((effect) => effect.effect_id === id);
    if (timed.length) {
      return timed.some((effect) => !I().immune(state, id, null, { sourceIsMagical: Boolean(effect.source_is_magical) }));
    }
    return !I().immune(state, id);
  }

  function incapacitated(state) {
    if (I().immune(state, "incapacitated")) return false;
    return state.is_unconscious || has(state, "incapacitated") || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  }

  const autoFailStrDex = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  const attackAdvantage = (state) => state.is_unconscious || has(state, "blinded") || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  const autoCritical = (state) => state.is_unconscious || has(state, "paralyzed");
  const suppressAttackAdvantage = (state) => Boolean(state.template?.suppress_attack_advantage_while_not_incapacitated) && !incapacitated(state);
  const speedZero = (state) => state.is_unconscious || has(state, "paralyzed") || has(state, "petrified") || has(state, "restrained");

  window.IRON_PIT_BROWSER_CONDITION_RULES = { attackAdvantage, autoCritical, autoFailStrDex, has, incapacitated, speedZero, suppressAttackAdvantage };
})();
