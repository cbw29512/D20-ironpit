(() => {
  "use strict";

  const key = (sourceId, sourceEffectId) => `${sourceId}::${sourceEffectId}`;
  function entries(state) {
    if (!Array.isArray(state.source_effect_immunities)) state.source_effect_immunities = [];
    return state.source_effect_immunities;
  }
  function immune(state, sourceId, sourceEffectId) {
    return entries(state).includes(key(sourceId, sourceEffectId));
  }
  function grant(state, sourceId, sourceEffectId) {
    const value = key(sourceId, sourceEffectId), current = entries(state);
    if (!current.includes(value)) current.push(value);
    return value;
  }

  window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY = { grant, immune, key };
})();
