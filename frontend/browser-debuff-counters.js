(() => {
  "use strict";

  function scopeMatches(counter, sourceIsMagical) {
    const scope = counter.source_scope || "any";
    if (scope === "any") return true;
    if (scope === "magical") return Boolean(sourceIsMagical);
    if (scope === "nonmagical") return !sourceIsMagical;
    throw new Error(`Unknown debuff counter source scope: ${scope}.`);
  }

  function matching(state, debuffId, options = {}) {
    try {
      const mode = options.mode || null;
      const sourceIsMagical = Boolean(options.sourceIsMagical);
      return (state.timed_effects || []).flatMap((effect) => effect.owned_debuff_counters || [])
        .filter((counter) => counter.debuff_id === debuffId
          && scopeMatches(counter, sourceIsMagical)
          && (!mode || counter.mode === mode));
    } catch (error) {
      console.error("Failed to resolve browser debuff counters.", {
        combatant: state?.template?.name, debuffId, error,
      });
      throw error;
    }
  }

  const prevented = (state, debuffId, options = {}) =>
    matching(state, debuffId, { ...options, mode: "prevent" }).length > 0;

  function movementCost(state, debuffId, options = {}) {
    const counters = matching(state, debuffId, { ...options, mode: "remove-with-movement" });
    if (!counters.length) return null;
    return Math.min(...counters.map((counter) => counter.movement_cost_ft));
  }

  const difficultTerrainMultiplier = (state, options = {}) =>
    prevented(state, "difficult-terrain", options) ? 1 : 2;

  window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = {
    difficultTerrainMultiplier, matching, movementCost, prevented,
  };
})();
