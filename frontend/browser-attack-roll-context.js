(() => {
  "use strict";

  function create({ baseDisadvantageSources = 0, rangedDisadvantage = false } = {}) {
    if (!Number.isFinite(baseDisadvantageSources) || baseDisadvantageSources < 0) {
      throw new Error("Attack-roll context requires non-negative base Disadvantage sources.");
    }
    return {
      baseDisadvantageSources,
      rangedDisadvantage: Boolean(rangedDisadvantage),
      advantageSources: {},
      descriptionFragments: [],
      aggregateFeatureId: null,
    };
  }

  function requireContext(ctx) {
    const state = ctx?.attackRollContext;
    if (!state || typeof state !== "object" || Array.isArray(state)) {
      throw new Error("Before-attack-roll hook requires a mutable attackRollContext object.");
    }
    if (!Number.isFinite(state.baseDisadvantageSources) || state.baseDisadvantageSources < 0) {
      throw new Error("Attack-roll context base Disadvantage sources are invalid.");
    }
    if (typeof state.rangedDisadvantage !== "boolean") {
      throw new Error("Attack-roll context ranged Disadvantage flag is invalid.");
    }
    if (!state.advantageSources || typeof state.advantageSources !== "object"
        || Array.isArray(state.advantageSources) || !Array.isArray(state.descriptionFragments)) {
      throw new Error("Attack-roll context source/description state is invalid.");
    }
    return state;
  }

  function setAdvantageSource(state, sourceId, value) {
    if (typeof sourceId !== "string" || !sourceId.trim()) throw new Error("Attack-roll Advantage source requires a stable id.");
    if (!Number.isFinite(value) || value < 0) throw new Error(`Attack-roll Advantage source ${sourceId} must be non-negative.`);
    state.advantageSources[sourceId] = value;
  }
  const advantageSource = (state, sourceId) => Number(state.advantageSources[sourceId] || 0);
  function advantageTotal(state) {
    return Object.values(state.advantageSources).reduce((sum, value) => {
      if (!Number.isFinite(value) || value < 0) throw new Error("Attack-roll Advantage source map is invalid.");
      return sum + value;
    }, 0);
  }
  function noEventResult(sequence) {
    if (!Number.isInteger(sequence) || sequence < 0) throw new Error("Before-attack-roll hook requires a valid sequence.");
    return { events: [], sequence, claimed: false };
  }

  window.IRON_PIT_BROWSER_ATTACK_ROLL_CONTEXT = {
    advantageSource, advantageTotal, create, noEventResult, requireContext, setAdvantageSource,
  };
})();